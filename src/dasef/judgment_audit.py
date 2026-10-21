from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from dasef.schema import SchemaSpec


@dataclass(frozen=True)
class JudgmentFeatureAudit:
    feature_name: str
    range_low: float
    range_high: float
    rows: int
    missing_count: int
    missing_rate: float
    finite_count: int
    mean: float | None
    std: float | None
    min: float | None
    max: float | None
    n_unique: int
    dominant_value_rate: float | None
    near_midpoint_rate: float | None
    at_lower_bound_count: int
    at_upper_bound_count: int
    out_of_range_count: int
    abs_target_correlation: float | None
    warnings: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _float_or_none(value: float) -> float | None:
    return None if not np.isfinite(value) else float(value)


def _encoded_target(y: pd.Series | None, n_rows: int) -> np.ndarray | None:
    if y is None or len(y) != n_rows:
        return None
    encoded = pd.factorize(y.astype(str), sort=True)[0].astype(float)
    return encoded if np.nanstd(encoded) > 0 else None


def audit_judgment_features(
    judgment_df: pd.DataFrame,
    schema: SchemaSpec,
    *,
    y: pd.Series | None = None,
    midpoint_tolerance_fraction: float = 0.05,
    collapse_dominant_threshold: float = 0.80,
    target_corr_warning_threshold: float = 0.95,
) -> dict[str, Any]:
    """Audit judgment feature quality before imputation can hide failures."""
    target = _encoded_target(y, len(judgment_df))
    audits: list[JudgmentFeatureAudit] = []
    for feature in schema.judgment_features:
        warnings: list[str] = []
        lo, hi = feature.value_range
        series = pd.to_numeric(
            judgment_df[feature.name] if feature.name in judgment_df else pd.Series(np.nan, index=judgment_df.index),
            errors="coerce",
        )
        finite = series[np.isfinite(series)]
        missing_count = int(series.isna().sum())
        finite_count = int(finite.shape[0])
        width = hi - lo

        if missing_count:
            warnings.append("missing_or_parse_failed_values")

        if finite_count:
            mean = float(finite.mean())
            std = float(finite.std(ddof=1)) if finite_count > 1 else 0.0
            min_value = float(finite.min())
            max_value = float(finite.max())
            n_unique = int(finite.nunique(dropna=True))
            dominant_value_rate = float(finite.value_counts(normalize=True, dropna=True).iloc[0])
            midpoint = lo + width / 2.0
            tolerance = abs(width) * midpoint_tolerance_fraction
            near_midpoint_rate = float(((finite - midpoint).abs() <= tolerance).mean())
            at_lower_bound_count = int(np.isclose(finite, lo).sum())
            at_upper_bound_count = int(np.isclose(finite, hi).sum())
            out_of_range_count = int(((finite < lo) | (finite > hi)).sum())
        else:
            mean = std = min_value = max_value = None
            n_unique = 0
            dominant_value_rate = None
            near_midpoint_rate = None
            at_lower_bound_count = at_upper_bound_count = out_of_range_count = 0

        if finite_count == 0:
            warnings.append("all_values_missing")
        if out_of_range_count:
            warnings.append("values_outside_declared_range")
        if dominant_value_rate is not None and dominant_value_rate >= collapse_dominant_threshold:
            warnings.append("dominant_value_collapse")
        if near_midpoint_rate is not None and near_midpoint_rate >= collapse_dominant_threshold:
            warnings.append("near_midpoint_collapse")
        if n_unique <= 2 and finite_count >= 10:
            warnings.append("low_cardinality_judgment")
        if at_lower_bound_count or at_upper_bound_count:
            warnings.append("boundary_values_possible_clipping")

        abs_corr: float | None = None
        if target is not None and finite_count >= 3:
            mask = np.isfinite(series.to_numpy(dtype=float)) & np.isfinite(target)
            if mask.sum() >= 3 and np.nanstd(series.to_numpy(dtype=float)[mask]) > 0:
                corr = np.corrcoef(series.to_numpy(dtype=float)[mask], target[mask])[0, 1]
                abs_corr = _float_or_none(abs(corr))
                if abs_corr is not None and abs_corr >= target_corr_warning_threshold:
                    warnings.append("very_high_target_correlation_review_for_leakage")

        audits.append(
            JudgmentFeatureAudit(
                feature_name=feature.name,
                range_low=float(lo),
                range_high=float(hi),
                rows=int(len(judgment_df)),
                missing_count=missing_count,
                missing_rate=float(missing_count / len(judgment_df)) if len(judgment_df) else 0.0,
                finite_count=finite_count,
                mean=mean,
                std=std,
                min=min_value,
                max=max_value,
                n_unique=n_unique,
                dominant_value_rate=dominant_value_rate,
                near_midpoint_rate=near_midpoint_rate,
                at_lower_bound_count=at_lower_bound_count,
                at_upper_bound_count=at_upper_bound_count,
                out_of_range_count=out_of_range_count,
                abs_target_correlation=abs_corr,
                warnings=warnings,
            )
        )

    return {
        "dataset": schema.dataset_name,
        "model_family": schema.model_family,
        "schema_generator": schema.schema_generator,
        "rows": int(len(judgment_df)),
        "features": [audit.as_dict() for audit in audits],
        "summary": {
            "feature_count": len(audits),
            "features_with_missing_values": sum(bool(a.missing_count) for a in audits),
            "features_with_distribution_warnings": sum(
                any(
                    warning
                    in {
                        "dominant_value_collapse",
                        "near_midpoint_collapse",
                        "low_cardinality_judgment",
                        "boundary_values_possible_clipping",
                    }
                    for warning in a.warnings
                )
                for a in audits
            ),
            "features_with_target_corr_warnings": sum(
                "very_high_target_correlation_review_for_leakage" in a.warnings for a in audits
            ),
        },
    }


def audits_to_frame(audits: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for audit in audits:
        for feature in audit.get("features", []):
            rows.append(
                {
                    "dataset": audit.get("dataset"),
                    "model_family": audit.get("model_family"),
                    "schema_generator": audit.get("schema_generator"),
                    **feature,
                    "warnings": ",".join(feature.get("warnings", [])),
                }
            )
    return pd.DataFrame(rows)


def write_judgment_audit_markdown(df: pd.DataFrame, out_path: str | Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        out_path.write_text("# DASEF Judgment Feature Audit\n\nNo judgment matrices found.\n", encoding="utf-8")
        return

    warning_rows = df[df["warnings"].astype(str).str.len() > 0].copy()
    lines = [
        "# DASEF Judgment Feature Audit",
        "",
        "Generated from stored judgment matrices; no external API calls were made.",
        "",
        "## Scope",
        "",
        f"- Judgment features audited: {len(df)}",
        f"- Features with any warning: {len(warning_rows)}",
        f"- Features with missing values: {int((df['missing_count'] > 0).sum())}",
        f"- Features with possible distribution collapse: {int(df['warnings'].astype(str).str.contains('collapse|low_cardinality').sum())}",
        f"- Features with very high target-correlation warning: {int(df['warnings'].astype(str).str.contains('very_high_target').sum())}",
        "",
        "## Warning Rows",
        "",
    ]
    if warning_rows.empty:
        lines.append("_None._")
    else:
        compact_cols = [
            "dataset",
            "model_family",
            "schema_generator",
            "feature_name",
            "missing_rate",
            "std",
            "n_unique",
            "dominant_value_rate",
            "near_midpoint_rate",
            "abs_target_correlation",
            "warnings",
        ]
        lines.append(warning_rows[compact_cols].to_markdown(index=False))
    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- Boundary values are not automatically bad, but they may indicate clipping or overly coarse prompts.",
            "- Target correlation is an audit signal only; high correlation can mean either useful signal or leakage.",
            "- Missing values must be reported before downstream imputers can hide invalid LLM outputs.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")
