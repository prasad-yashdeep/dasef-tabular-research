from dasef.config import load_datasets, load_llm_models, load_model_families


def test_configs_load():
    datasets = {d.name for d in load_datasets().datasets}
    # The 10 main Paper-1 benchmark datasets must always be present; the registry
    # may also include additional (e.g. Paper-2 expansion) datasets, so assert a
    # superset rather than a brittle exact count.
    paper1 = {
        "adult_income", "bank_marketing", "blood_transfusion", "car_evaluation",
        "credit_g", "electricity", "phoneme", "pima_diabetes",
        "qsar_biodegradation", "spambase",
    }
    assert paper1 <= datasets
    assert len(datasets) >= len(paper1)
    assert len(load_llm_models().schema_generators) == 4
    assert "tree" in load_model_families().model_families
