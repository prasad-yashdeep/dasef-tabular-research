from __future__ import annotations

from dasef.statistics import normalize_schema_path, paired_delta_stats, schema_metadata_from_path


def test_paired_delta_stats_detects_clear_positive_shift() -> None:
    stats = paired_delta_stats(
        [0.70, 0.71, 0.72, 0.73, 0.74],
        [0.75, 0.76, 0.77, 0.78, 0.79],
        n_bootstrap=500,
        seed=0,
    )

    assert stats.n == 5
    assert round(stats.delta_mean, 3) == 0.05
    assert stats.ci_low > 0
    assert stats.ci_excludes_zero


def test_paired_delta_stats_drops_nan_pairs() -> None:
    stats = paired_delta_stats(
        [0.70, float("nan"), 0.72],
        [0.71, 0.75, 0.73],
        n_bootstrap=100,
        seed=0,
    )

    assert stats.n == 2
    assert round(stats.delta_mean, 3) == 0.01


def test_schema_metadata_from_path_reads_family_and_model() -> None:
    model_family, schema_model = schema_metadata_from_path(
        "cache/schemas/pima_diabetes/distance_knn/claude-sonnet-4.6/schema_abc.json"
    )

    assert model_family == "distance_knn"
    assert schema_model == "claude-sonnet-4.6"


def test_normalize_schema_path_strips_absolute_prefix() -> None:
    assert normalize_schema_path(
        "/tmp/project/cache/schemas/pima_diabetes/tree/model/schema_abc.json"
    ) == "cache/schemas/pima_diabetes/tree/model/schema_abc.json"
