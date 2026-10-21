from __future__ import annotations

import pandas as pd

from dasef.judgment_audit import audit_judgment_features, audits_to_frame
from dasef.schema import FeatureSpec, FeatureType, SchemaSpec


def _schema() -> SchemaSpec:
    return SchemaSpec(
        dataset_name="toy",
        model_family="distance_knn",
        schema_generator="unit-test",
        features=[
            FeatureSpec(
                name="stable_risk",
                type=FeatureType.judgment,
                description="Nearly collapsed score.",
                value_range=(0.0, 1.0),
                feature_family="semantic",
                expected_model_benefit="Adds a semantic axis.",
                leakage_risk="low",
            ),
            FeatureSpec(
                name="missing_risk",
                type=FeatureType.judgment,
                description="Contains missing values.",
                value_range=(0.0, 10.0),
                feature_family="semantic",
                expected_model_benefit="Adds a semantic axis.",
                leakage_risk="low",
            ),
        ],
    )


def test_audit_judgment_features_flags_missing_and_collapse() -> None:
    judgment_df = pd.DataFrame(
        {
            "stable_risk": [0.5] * 10,
            "missing_risk": [1.0, 2.0, None, 4.0, 5.0, None, 7.0, 8.0, 9.0, 10.0],
        }
    )

    audit = audit_judgment_features(judgment_df, _schema())
    frame = audits_to_frame([audit])

    stable = frame.loc[frame["feature_name"] == "stable_risk"].iloc[0]
    missing = frame.loc[frame["feature_name"] == "missing_risk"].iloc[0]
    assert "dominant_value_collapse" in stable["warnings"]
    assert "near_midpoint_collapse" in stable["warnings"]
    assert "missing_or_parse_failed_values" in missing["warnings"]
    assert missing["missing_count"] == 2
