from __future__ import annotations

import logging
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from dasef.settings import get_project_secret
from .base import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class MissingAPIKey(RuntimeError):
    pass


class HTTPProviderClient:
    provider: str
    env_key: str
    base_url: str

    def __init__(self, provider: str, env_key: str, base_url: str):
        self.provider = provider
        self.env_key = env_key
        self.base_url = base_url.rstrip("/")

    @property
    def api_key(self) -> str:
        key = get_project_secret(self.env_key)
        if not key:
            raise MissingAPIKey(f"Missing {self.env_key}; add it to project-local .env")
        return key

    def complete(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError

    @retry(wait=wait_exponential(multiplier=1, min=1, max=20), stop=stop_after_attempt(3))
    def _post(self, path: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
        logger.info("LLM request provider=%s model=%s", self.provider, payload.get("model", "unknown"))
        resp = requests.post(f"{self.base_url}{path}", headers=headers, json=payload, timeout=360)
        if resp.status_code >= 400:
            logger.warning("LLM HTTP error provider=%s status=%s body=%s", self.provider, resp.status_code, resp.text[:500])
        resp.raise_for_status()
        return resp.json()


class OpenAIClient(HTTPProviderClient):
    def __init__(self):
        super().__init__("openai", "OPENAI_API_KEY", get_project_secret("OPENAI_BASE_URL") or "https://api.openai.com")

    def complete(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": request.model,
            "input": request.prompt,
            "max_output_tokens": request.max_output_tokens,
        }
        if not request.model.startswith("gpt-5"):
            payload["temperature"] = request.temperature
        if request.response_format == "json" and "json" in request.prompt.lower():
            payload["text"] = {"format": {"type": "json_object"}}
        # For reasoning models, set reasoning effort
        if request.model.startswith("gpt-5") and request.reasoning:
            effort = "medium" if request.reasoning == "max_available" else request.reasoning
            payload["reasoning"] = {"effort": effort}
        raw = self._post("/v1/responses", {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, payload)
        text = raw.get("output_text") or ""
        if not text and raw.get("output"):
            parts = []
            for item in raw["output"]:
                for c in item.get("content", []):
                    if "text" in c:
                        parts.append(c["text"])
            text = "\n".join(parts)
        usage = raw.get("usage") or {}
        return LLMResponse(text=text, provider=self.provider, model=request.model, input_tokens=usage.get("input_tokens"), output_tokens=usage.get("output_tokens"), raw=raw)


class DeepSeekClient(HTTPProviderClient):
    def __init__(self):
        super().__init__("deepseek", "DEEPSEEK_API_KEY", get_project_secret("DEEPSEEK_BASE_URL") or "https://api.deepseek.com")

    def complete(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": request.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
            "response_format": {"type": "json_object"} if request.response_format == "json" else None,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        raw = self._post("/chat/completions", {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, payload)
        message = raw["choices"][0]["message"]
        text = message.get("content", "") or ""
        # Reasoning models (R1, V4 Pro) may put output in reasoning_content
        if not text.strip() and message.get("reasoning_content"):
            text = message["reasoning_content"]
        usage = raw.get("usage") or {}
        return LLMResponse(text=text, provider=self.provider, model=request.model, input_tokens=usage.get("prompt_tokens"), output_tokens=usage.get("completion_tokens"), raw=raw)


class AnthropicClient(HTTPProviderClient):
    def __init__(self):
        super().__init__("anthropic", "ANTHROPIC_API_KEY", "https://api.anthropic.com")

    def complete(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": request.model,
            "max_tokens": request.max_output_tokens,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        # Opus 4.7+ reasoning models don't accept temperature
        if "opus" not in request.model:
            payload["temperature"] = request.temperature
        raw = self._post("/v1/messages", {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}, payload)
        text = "\n".join(block.get("text", "") for block in raw.get("content", []) if block.get("type") == "text")
        usage = raw.get("usage") or {}
        return LLMResponse(text=text, provider=self.provider, model=request.model, input_tokens=usage.get("input_tokens"), output_tokens=usage.get("output_tokens"), raw=raw)


class GeminiClient(HTTPProviderClient):
    def __init__(self):
        super().__init__("gemini", "GEMINI_API_KEY", get_project_secret("GEMINI_BASE_URL") or "https://generativelanguage.googleapis.com")

    def complete(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "contents": [{"parts": [{"text": request.prompt}]}],
            "generationConfig": {"temperature": request.temperature, "maxOutputTokens": request.max_output_tokens, "responseMimeType": "application/json" if request.response_format == "json" else "text/plain"},
        }
        raw = self._post(f"/v1beta/models/{request.model}:generateContent?key={self.api_key}", {"Content-Type": "application/json"}, payload)
        text = ""
        for cand in raw.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                text += part.get("text", "")
        usage = raw.get("usageMetadata") or {}
        return LLMResponse(text=text, provider=self.provider, model=request.model, input_tokens=usage.get("promptTokenCount"), output_tokens=usage.get("candidatesTokenCount"), raw=raw)


def client_for_provider(provider: str):
    if provider == "openai":
        return OpenAIClient()
    if provider == "deepseek":
        return DeepSeekClient()
    if provider == "anthropic":
        return AnthropicClient()
    if provider == "gemini":
        return GeminiClient()
    raise ValueError(f"Unsupported provider: {provider}")
