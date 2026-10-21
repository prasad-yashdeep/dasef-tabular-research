from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.stats import wilcoxon

from dasef.io_utils import read_json


DEFAULT_METRIC = "roc_auc_ovr"
DEFAULT_MATRIX_PAIRS = (
    ("raw", "raw_plus_random_formula"),
    ("raw", "raw_plus_formula"),
    ("raw_plus_random_formula", "raw_plus_formula"),
    ("raw", "raw_plus_random_all"),
    ("raw", "raw_plus_formula_plus_judgment"),
    ("raw_plus_random_all", "raw_plus_formula_plus_judgment"),
    ("raw_plus_formula", "raw_plus_formula_plus_judgment"),
    ("raw", "raw_plus_direct_risk"),
    ("raw_plus_direct_risk", "raw_plus_formula"),
    ("raw_plus_direct_risk", "raw_plus_formula_plus_judgment"),
)


@dataclass(frozen=True)
class PairedDeltaStats:
    baseline_mean: float
    candidate_mean: float
    delta_mean: float
    delta_std: float
    ci_low: float
    ci_high: float
    p_value: float | None
    n: int

    @property
    def ci_excludes_zero(self) -> bool:
        return self.ci_low > 0 or self.ci_high < 0


@dataclass(frozen=True)
class MatrixComparison:
    result_path: str
    dataset: str
    schema_path: str | None
    schema_model: str | None
    model_family: str | None
    downstream_model: str
    metric: str
    baseline_matrix: str
    candidate_matrix: str
    baseline_mean: float
    candidate_mean: float
    delta_mean: float
    delta_std: float
    ci_low: float
    ci_high: float
    p_value: float | None
    n: int
    ci_excludes_zero: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def paired_delta_stats(
    baseline_scores: Iterable[float],
    candidate_scores: Iterable[float],
    *,
    n_bootstrap: int = 10_000,
    ci: float = 0.95,
    seed: int = 42,
) -> PairedDeltaStats:
    """Summarize paired fold-level deltas.

    This treats the paired fold deltas as descriptive evidence, not as the final
    publication-level independent unit. The paper should still aggregate primary
    claims across datasets once enough datasets exist.
    """
    baseline = np.asarray(list(baseline_scores), dtype=float)
    candidate = np.asarray(list(candidate_scores), dtype=float)
    if baseline.shape != candidate.shape:
        raise ValueError(f"Paired scores must have same shape: {baseline.shape} != {candidate.shape}")

    finite = np.isfinite(baseline) & np.isfinite(candidate)
    baseline = baseline[finite]
    candidate = candidate[finite]
    if len(baseline) == 0:
        return PairedDeltaStats(
            baseline_mean=math.nan,
            candidate_mean=math.nan,
            delta_mean=math.nan,
            delta_std=math.nan,
            ci_low=math.nan,
            ci_high=math.nan,
            p_value=None,
            n=0,
        )

    deltas = candidate - baseline
    rng = np.random.default_rng(seed)
    alpha = 1.0 - ci
    if len(deltas) == 1:
        ci_low = ci_high = float(deltas[0])
        p_value = None
    else:
        boot_means = rng.choice(deltas, size=(n_bootstrap, len(deltas)), replace=True).mean(axis=1)
        ci_low, ci_high = np.quantile(boot_means, [alpha / 2.0, 1.0 - alpha / 2.0])
        if np.allclose(deltas, 0):
            p_value = 1.0
        else:
            try:
                p_value = float(wilcoxon(deltas, zero_method="wilcox").pvalue)
            except ValueError:
                p_value = None

    return PairedDeltaStats(
        baseline_mean=float(np.mean(baseline)),
        candidate_mean=float(np.mean(candidate)),
        delta_mean=float(np.mean(deltas)),
        delta_std=float(np.std(deltas, ddof=1)) if len(deltas) > 1 else 0.0,
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        p_value=p_value,
        n=int(len(deltas)),
    )


def schema_metadata_from_path(schema_path: str | None) -> tuple[str | None, str | None]:
    if not schema_path:
        return None, None
    parts = Path(schema_path).parts
    if "schemas" not in parts:
        return None, None
    idx = parts.index("schemas")
    try:
        return parts[idx + 2], parts[idx + 3]
    except IndexError:
        return None, None


def normalize_schema_path(schema_path: str | None) -> str | None:
    if not schema_path:
        return None
    parts = Path(schema_path).parts
    if "schemas" not in parts:
        return schema_path
    idx = parts.index("schemas")
    return str(Path("cache", *parts[idx:]))


def _evaluations_by_name(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {evaluation["matrix_name"]: evaluation for evaluation in result.get("evaluations", [])}


def _models_for_pair(
    baseline_eval: dict[str, Any],
    candidate_eval: dict[str, Any],
    metric: str,
) -> set[str]:
    baseline_models = {
        model
        for model, scores in baseline_eval.get("raw_scores", {}).items()
        if metric in scores
    }
    candidate_models = {
        model
        for model, scores in candidate_eval.get("raw_scores", {}).items()
        if metric in scores
    }
    return baseline_models & candidate_models


def comparisons_for_result(
    result_path: str | Path,
    *,
    metric: str = DEFAULT_METRIC,
    matrix_pairs: Iterable[tuple[str, str]] = DEFAULT_MATRIX_PAIRS,
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> list[MatrixComparison]:
    result_path = Path(result_path)
    result = read_json(result_path)
    evaluations = _evaluations_by_name(result)
    schema_path = normalize_schema_path(result.get("artifacts", {}).get("schema"))
    model_family, schema_model = schema_metadata_from_path(schema_path)
    out: list[MatrixComparison] = []

    for baseline_matrix, candidate_matrix in matrix_pairs:
        if baseline_matrix not in evaluations or candidate_matrix not in evaluations:
            continue
        baseline_eval = evaluations[baseline_matrix]
        candidate_eval = evaluations[candidate_matrix]
        for downstream_model in sorted(_models_for_pair(baseline_eval, candidate_eval, metric)):
            stats = paired_delta_stats(
                baseline_eval["raw_scores"][downstream_model][metric],
                candidate_eval["raw_scores"][downstream_model][metric],
                n_bootstrap=n_bootstrap,
                seed=seed,
            )
            out.append(
                MatrixComparison(
                    result_path=str(result_path),
                    dataset=result.get("dataset", ""),
                    schema_path=schema_path,
                    schema_model=schema_model,
                    model_family=model_family,
                    downstream_model=downstream_model,
                    metric=metric,
                    baseline_matrix=baseline_matrix,
                    candidate_matrix=candidate_matrix,
                    baseline_mean=stats.baseline_mean,
                    candidate_mean=stats.candidate_mean,
                    delta_mean=stats.delta_mean,
                    delta_std=stats.delta_std,
                    ci_low=stats.ci_low,
                    ci_high=stats.ci_high,
                    p_value=stats.p_value,
                    n=stats.n,
                    ci_excludes_zero=stats.ci_excludes_zero,
                )
            )
    return out


def comparisons_for_paths(
    result_paths: Iterable[str | Path],
    *,
    metric: str = DEFAULT_METRIC,
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> list[MatrixComparison]:
    comparisons: list[MatrixComparison] = []
    for result_path in result_paths:
        comparisons.extend(
            comparisons_for_result(
                result_path,
                metric=metric,
                n_bootstrap=n_bootstrap,
                seed=seed,
            )
        )
    return comparisons
