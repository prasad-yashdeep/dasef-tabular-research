from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class FeatureType(str, Enum):
    formula = "formula"
    judgment = "judgment"


class FeatureSpec(BaseModel):
    name: str = Field(pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    type: FeatureType
    description: str
    value_range: tuple[float, float]
    feature_family: str
    expected_model_benefit: str
    leakage_risk: Literal["low", "medium", "high"] = "medium"
    formula: str | None = None
    computation_method: str | None = None
    uses_only_row_values: bool = True

    @field_validator("value_range")
    @classmethod
    def validate_range(cls, value: tuple[float, float]) -> tuple[float, float]:
        lo, hi = value
        if lo >= hi:
            raise ValueError("value_range lower bound must be < upper bound")
        return value

    @model_validator(mode="after")
    def formula_required_for_formula_feature(self) -> "FeatureSpec":
        if self.type == FeatureType.formula and not self.formula:
            raise ValueError(f"Formula feature {self.name} requires formula")
        if self.type == FeatureType.judgment and self.formula:
            raise ValueError(f"Judgment feature {self.name} should not include formula")
        return self


class SchemaSpec(BaseModel):
    dataset_name: str
    model_family: str
    schema_generator: str
    schema_version: str = "v1"
    features: list[FeatureSpec]
    prompt_hash: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def unique_feature_names(self) -> "SchemaSpec":
        names = [f.name for f in self.features]
        if len(names) != len(set(names)):
            raise ValueError("Feature names must be unique")
        return self

    @property
    def formula_features(self) -> list[FeatureSpec]:
        return [f for f in self.features if f.type == FeatureType.formula]

    @property
    def judgment_features(self) -> list[FeatureSpec]:
        return [f for f in self.features if f.type == FeatureType.judgment]


def schema_json_instruction() -> str:
    return """Return a JSON object with keys: dataset_name, model_family, schema_generator, schema_version, features. Each feature must include name, type ('formula' or 'judgment'), description, value_range [min,max], feature_family, expected_model_benefit, leakage_risk ('low','medium','high'), uses_only_row_values, and formula only for formula features."""
