from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPrice:
    input_per_million: float
    output_per_million: float


PRICES = {
    "claude-sonnet-4.6": TokenPrice(3.0, 15.0),
    "gpt-5.5": TokenPrice(5.0, 30.0),
    "deepseek-r1": TokenPrice(0.55, 2.19),
    "gemini-3-pro-latest": TokenPrice(2.0, 12.0),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price = PRICES[model]
    return (input_tokens / 1_000_000) * price.input_per_million + (output_tokens / 1_000_000) * price.output_per_million
