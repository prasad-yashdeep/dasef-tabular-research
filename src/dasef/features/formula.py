from __future__ import annotations

import ast
import logging
import re
from typing import Any

import numpy as np
import pandas as pd

from dasef.schema import FeatureSpec, SchemaSpec

logger = logging.getLogger(__name__)

ALLOWED_NODES = (
    ast.Expression, ast.BoolOp, ast.BinOp, ast.UnaryOp, ast.Compare, ast.Call,
    ast.Name, ast.Load, ast.Constant, ast.Subscript, ast.Attribute, ast.List, ast.Tuple,
    ast.And, ast.Or, ast.BitAnd, ast.BitOr, ast.Invert, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
    ast.USub, ast.UAdd, ast.Not, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.IfExp,  # Python ternary: x if cond else y — safe for tree-style branching
)
ALLOWED_FUNCS = {"log", "log1p", "sqrt", "abs", "minimum", "maximum", "clip", "where", "isnan", "logical_and", "logical_or", "sum", "mean", "std", "exp", "power", "sign", "floor", "ceil", "round", "nan_to_num", "count_nonzero", "float64", "int64", "float32", "array", "ones_like", "zeros_like", "full_like", "percentile", "quantile", "digitize", "searchsorted", "interp", "tanh", "sigmoid", "log2", "log10", "square", "cbrt", "reciprocal", "arctan", "arctan2", "sin", "cos", "tan", "float", "int", "bool"}
# Safe pandas/numpy method names allowed on any expression (e.g. (expr).astype(int))
ALLOWED_METHODS = {"astype", "sum", "mean", "std", "min", "max", "count", "abs", "clip", "round", "fillna", "replace"}
BACKTICK_COLUMN_RE = re.compile(r"`([^`]+)`")
# Allowed names that numpy does not export (numpy dropped the ``np.float``/``np.int``/
# ``np.bool`` aliases in 1.24), bound explicitly so ``.astype(int)`` and ``float(x)``
# behave as written instead of resolving to None.
_NON_NUMPY_FUNCS: dict[str, Any] = {
    "float": float,
    "int": int,
    "bool": bool,
    "sigmoid": lambda x: 1.0 / (1.0 + np.exp(-x)),
}


class UnsafeFormula(ValueError):
    pass


def _safe_column_name(col: str, used: set[str]) -> str:
    base = re.sub(r"\W+", "_", col).strip("_")
    if not base or base[0].isdigit():
        base = f"col_{base}"
    candidate = f"__dasef_col_{base}"
    i = 2
    while candidate in used:
        candidate = f"__dasef_col_{base}_{i}"
        i += 1
    used.add(candidate)
    return candidate


def _sanitize_columns(expr: str, allowed_names: set[str]) -> tuple[str, set[str], dict[str, str]]:
    """Replace formula column names that are not valid Python identifiers.

    LLMs often quote awkward column names as pandas-style backticks, e.g.
    `` `Band_74_W_544_90` ``. Python's AST parser cannot parse those, so
    translate quoted column references into internal safe variables before
    validation and evaluation.
    """
    sanitized_names = set(allowed_names)
    sanitized_expr = expr
    used = set(allowed_names) | set(ALLOWED_FUNCS) | {"np"}
    column_map: dict[str, str] = {}

    def get_safe(col: str) -> str:
        if col not in column_map:
            column_map[col] = _safe_column_name(col, used)
        return column_map[col]

    def replace_backtick(match: re.Match[str]) -> str:
        col = match.group(1)
        if col not in allowed_names:
            raise UnsafeFormula(f"Unknown backtick column in formula: {col}")
        return get_safe(col)

    sanitized_expr = BACKTICK_COLUMN_RE.sub(replace_backtick, sanitized_expr)

    dot_cols = sorted([n for n in allowed_names if "." in n], key=len, reverse=True)
    for col in dot_cols:
        safe = get_safe(col)
        sanitized_expr = sanitized_expr.replace(col, safe)
        sanitized_names.discard(col)
        sanitized_names.add(safe)

    # Columns whose names collide with an allowed function (e.g. a real-estate
    # column literally called ``floor``) must not be shadowed by the numpy
    # function of the same name at eval time. Rewrite bare references to such
    # columns into safe variables while leaving call-position names (``floor(x)``)
    # bound to the function.
    colliding = {n for n in sanitized_names if n in ALLOWED_FUNCS or n == "np"}
    if colliding:
        try:
            tree = ast.parse(sanitized_expr, mode="eval")
        except SyntaxError:
            tree = None  # validate_formula will surface the parse error
        if tree is not None:

            class _RenameCollidingColumns(ast.NodeTransformer):
                def visit_Call(self, node: ast.Call) -> ast.AST:
                    if isinstance(node.func, ast.Name) and node.func.id in colliding:
                        node.args = [self.visit(a) for a in node.args]
                        node.keywords = [self.visit(k) for k in node.keywords]
                        return node
                    return self.generic_visit(node)

                def visit_Name(self, node: ast.Name) -> ast.AST:
                    if node.id in colliding:
                        return ast.copy_location(ast.Name(id=get_safe(node.id), ctx=node.ctx), node)
                    return node

            tree = ast.fix_missing_locations(_RenameCollidingColumns().visit(tree))
            sanitized_expr = ast.unparse(tree)

    for col, safe in column_map.items():
        sanitized_names.discard(col)
        sanitized_names.add(safe)
    return sanitized_expr, sanitized_names, column_map


def validate_formula(expr: str, allowed_names: set[str]) -> None:
    expr, allowed_names, _ = _sanitize_columns(expr, allowed_names)
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_NODES):
            raise UnsafeFormula(f"Disallowed AST node: {type(node).__name__}")
        if isinstance(node, ast.Name):
            if node.id not in allowed_names and node.id not in {"np"} and node.id not in ALLOWED_FUNCS:
                raise UnsafeFormula(f"Unknown name in formula: {node.id}")
        if isinstance(node, ast.Attribute):
            # Allow np.func access
            if isinstance(node.value, ast.Name) and node.value.id == "np" and node.attr in ALLOWED_FUNCS:
                continue
            # Allow safe method calls on any expression: (expr).astype(), col.sum(), etc.
            if node.attr in ALLOWED_METHODS:
                continue
            # Allow np.func access on nested np calls
            if isinstance(node.value, ast.Name) and node.value.id == "np":
                if node.attr not in ALLOWED_FUNCS:
                    raise UnsafeFormula(f"Disallowed attribute access: {ast.unparse(node)}")
            elif isinstance(node.value, ast.Name) and node.value.id in allowed_names:
                # Column attribute access — allow known safe methods
                if node.attr not in ALLOWED_METHODS and node.attr not in ALLOWED_FUNCS:
                    raise UnsafeFormula(f"Disallowed attribute access: {ast.unparse(node)}")
            # For other expressions (Compare, BinOp, etc.) with safe method, already handled above
            # Only reject if attr is not in any allow list
            elif node.attr not in ALLOWED_FUNCS and node.attr not in ALLOWED_METHODS:
                raise UnsafeFormula(f"Disallowed attribute access: {ast.unparse(node)}")
        if isinstance(node, ast.Call):
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "np":
                func_name = node.func.attr
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id in allowed_names:
                # Method call on a column variable (e.g. col.sum()) — allow safe methods
                func_name = node.func.attr if node.func.attr in ALLOWED_FUNCS else node.func.attr
                # Allow pandas-style aggregation methods on columns
                if node.func.attr in {"sum", "mean", "std", "min", "max", "count", "abs", "clip", "round", "astype"}:
                    continue
            if func_name is None:
                # Could not resolve function — skip if it looks like a method on known data
                if isinstance(node.func, ast.Attribute):
                    continue  # Attribute calls are caught by the Attribute check above
            elif func_name not in ALLOWED_FUNCS:
                raise UnsafeFormula(f"Disallowed function call: {func_name}")


def _looks_numeric(values) -> bool:
    """True if every non-null value parses as a float (int-valued category codes stored
    as strings, e.g. OpenML categories ``['-1', '1']`` or ``['117879', '117885', ...]``,
    count as numeric even though pandas stores the category labels as strings)."""
    try:
        for v in values:
            if v is None or (isinstance(v, float) and pd.isna(v)):
                continue
            float(v)
        return True
    except (TypeError, ValueError):
        return False


def _formula_column(series: pd.Series) -> pd.Series:
    """Expose a dataframe column to formula evaluation with its natural semantics.

    Numeric columns are coerced to numbers. Truly textual columns, whether stored as
    ``object``, pandas string dtype, or ``category`` with non-numeric categories, are
    exposed as plain strings so that comparisons such as ``checking_status == 'no
    checking'`` work. ``category`` columns whose category labels are numeric (either
    ``category.dtype.categories`` numeric, or string labels that all parse as numbers,
    e.g. OpenML's ``['-1', '1']`` or ``['117879', ...]`` role/resource ids) are exposed
    as numbers so that arithmetic (``+``, ``/``, comparisons to numeric literals) works;
    treating them as strings previously made every arithmetic formula on such a column
    silently evaluate to NaN or a spurious constant instead of raising. Narrow integer
    columns are widened to int64 so that sums, products and differences cannot wrap.
    """
    dtype = series.dtype
    if isinstance(dtype, pd.CategoricalDtype):
        if pd.api.types.is_numeric_dtype(dtype.categories) or _looks_numeric(dtype.categories):
            return pd.to_numeric(series.astype(object), errors="coerce")
        return series.astype(object)
    if dtype == object or pd.api.types.is_string_dtype(dtype):
        return series
    if pd.api.types.is_bool_dtype(dtype):
        return series
    if pd.api.types.is_integer_dtype(dtype) and getattr(dtype, "itemsize", 8) < 8:
        # Narrow integer columns (OpenML count columns and cached category codes arrive as
        # int8/uint8/int16) must not keep their width inside formulas: numpy arithmetic on
        # uint8 wraps modulo 256, so ``f5 + f6 + f7`` or ``V2 * V4`` silently overflowed
        # (and ``V1 - V4`` wrapped to ~255) before the declared-range clip.
        try:
            return series.astype("int64")
        except (TypeError, ValueError):
            return series.astype("float64")
    return pd.to_numeric(series, errors="coerce")


def _numeric_exposed_categoricals(df: pd.DataFrame, column_map: dict[str, str]) -> set[str]:
    """Formula variable names of ``category`` columns that :func:`_formula_column` exposes
    as numbers (numeric category dtype, or string labels that all parse as numbers)."""
    keys: set[str] = set()
    for col in df.columns:
        dtype = df[col].dtype
        if isinstance(dtype, pd.CategoricalDtype) and (
            pd.api.types.is_numeric_dtype(dtype.categories) or _looks_numeric(dtype.categories)
        ):
            keys.add(column_map.get(col, col.replace(".", "_") if "." in col else col))
    return keys


class _NumericLiteralComparisons(ast.NodeTransformer):
    """Rewrite ``col == '1'`` to ``col == 1.0`` when ``col`` is a category column whose
    numeric-looking string labels are exposed to the formula as numbers.

    Generators write both ``attribute_1 == '1'`` (matching pandas' string labels) and
    ``attribute_1 + 1`` (treating the code as a number) for the same OpenML column.
    Exposing the column as a number makes the arithmetic correct but, without this
    rewrite, silently turns every comparison against a string literal into a constant
    ``False``; rewriting numeric-looking string literals in comparisons that touch such a
    column makes both idioms evaluate as the generator intended. Comparisons that do not
    involve a numeric-exposed category column, and string literals that do not parse as
    numbers, are left untouched.
    """

    def __init__(self, numeric_vars: set[str]) -> None:
        self.numeric_vars = numeric_vars

    @staticmethod
    def _to_number(node: ast.expr) -> ast.expr:
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and _looks_numeric([node.value]):
            return ast.copy_location(ast.Constant(value=float(node.value)), node)
        return node

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        self.generic_visit(node)
        operands = [node.left, *node.comparators]
        touches = any(
            isinstance(n, ast.Name) and n.id in self.numeric_vars for op in operands for n in ast.walk(op)
        )
        if not touches:
            return node
        node.left = self._to_number(node.left)
        node.comparators = [self._to_number(c) for c in node.comparators]
        return node


def compute_formula_feature(df: pd.DataFrame, feature: FeatureSpec) -> pd.Series:
    if not feature.formula:
        raise ValueError(f"Formula missing for {feature.name}")
    allowed = set(df.columns)
    validate_formula(feature.formula, allowed)
    sanitized_formula, _, column_map = _sanitize_columns(feature.formula, allowed)
    env: dict[str, Any] = {}
    for col in df.columns:
        safe_key = column_map.get(col, col.replace(".", "_") if "." in col else col)
        env[safe_key] = _formula_column(df[col])
    env["np"] = np
    for fn in ALLOWED_FUNCS:
        env[fn] = getattr(np, fn) if hasattr(np, fn) else _NON_NUMPY_FUNCS.get(fn)
    tree = ast.parse(sanitized_formula, mode="eval")
    numeric_vars = _numeric_exposed_categoricals(df, column_map)
    if numeric_vars:
        tree = ast.fix_missing_locations(_NumericLiteralComparisons(numeric_vars).visit(tree))
    result = eval(compile(tree, "<dasef_formula>", "eval"), {"__builtins__": {}}, env)  # noqa: S307 - AST validated, no builtins
    if np.isscalar(result):
        result = pd.Series([result] * len(df), index=df.index)
    result = pd.Series(result, index=df.index, name=feature.name)
    lo, hi = feature.value_range
    return pd.to_numeric(result, errors="coerce").clip(lower=lo, upper=hi)


def materialize_formula_features(df: pd.DataFrame, schema: SchemaSpec) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for feature in schema.formula_features:
        try:
            out[feature.name] = compute_formula_feature(df, feature)
        except Exception:
            logger.exception("Failed formula feature=%s dataset=%s", feature.name, schema.dataset_name)
            out[feature.name] = np.nan
    return out
