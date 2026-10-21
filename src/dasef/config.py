from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from .paths import CONFIG_DIR


class DatasetConfig(BaseModel):
    name: str
    openml_id: int | None = None
    task_type: str = "classification"
    tier: str = "unknown"
    judgment_cap_rows: int | None = None


class DatasetRegistry(BaseModel):
    datasets: list[DatasetConfig]

    def get(self, name: str) -> DatasetConfig:
        for dataset in self.datasets:
            if dataset.name == name:
                return dataset
        raise KeyError(f"Unknown dataset: {name}")


class LLMModelConfig(BaseModel):
    id: str
    provider: str
    env_key: str
    provider_model: str | None = None
    reasoning: str | None = None
    role: str | None = None


class LLMRegistry(BaseModel):
    schema_generators: list[LLMModelConfig] = Field(default_factory=list)
    judgment_fillers: list[LLMModelConfig] = Field(default_factory=list)


class ModelFamilyConfig(BaseModel):
    downstream_models: list[str]
    schema_priorities: list[str]


class ModelFamilyRegistry(BaseModel):
    model_families: dict[str, ModelFamilyConfig]


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_datasets(path: str | Path = CONFIG_DIR / "datasets.yaml") -> DatasetRegistry:
    return DatasetRegistry.model_validate(load_yaml(path))


def load_llm_models(path: str | Path = CONFIG_DIR / "llm_models.yaml") -> LLMRegistry:
    return LLMRegistry.model_validate(load_yaml(path))


def load_model_families(path: str | Path = CONFIG_DIR / "model_families.yaml") -> ModelFamilyRegistry:
    return ModelFamilyRegistry.model_validate(load_yaml(path))
