from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMRequest:
    model: str
    prompt: str
    temperature: float = 0.0
    max_output_tokens: int = 4096
    reasoning: str | None = None
    response_format: str = "json"


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    raw: dict | None = None


class LLMClient(Protocol):
    provider: str

    def complete(self, request: LLMRequest) -> LLMResponse: ...
