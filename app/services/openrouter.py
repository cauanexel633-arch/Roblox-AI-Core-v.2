import json
import logging
from typing import TypeVar, Type
import httpx
from pydantic import BaseModel, ValidationError
from app.core.config import settings
from app.core.errors import AIProviderError

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class OpenRouterClient:
    def __init__(self) -> None:
        self.base_url = settings.openrouter_base_url.rstrip("/")

    async def generate_structured(self, *, system_prompt: str, user_prompt: str, schema_model: Type[T], schema_name: str) -> tuple[T, str]:
        if not settings.openrouter_api_key:
            raise AIProviderError("OPENROUTER_API_KEY is not configured")
        models = [settings.openrouter_model, *settings.fallback_models]
        last_error: Exception | None = None
        for model in models:
            try:
                result = await self._request_model(model, system_prompt, user_prompt, schema_model, schema_name)
                return result, model
            except Exception as exc:
                last_error = exc
                logger.warning("OpenRouter model %s failed: %s", model, str(exc)[:200])
        raise AIProviderError(str(last_error or "No model could generate the requested content"))

    async def _request_model(self, model: str, system_prompt: str, user_prompt: str, schema_model: Type[T], schema_name: str) -> T:
        schema = schema_model.model_json_schema()
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        }
        base_payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1800,
        }
        # Try strict structured output first. Some free models/providers do not support it.
        payload = {**base_payload, "response_format": {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        }}
        timeout = httpx.Timeout(settings.request_timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            if response.status_code in (400, 404, 422):
                # Compatibility fallback: request JSON mode, then validate locally.
                payload = {**base_payload, "response_format": {"type": "json_object"}}
                response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            if response.status_code >= 400:
                raise AIProviderError(f"OpenRouter HTTP {response.status_code}: {response.text[:500]}")
            try:
                body = response.json()
                content = body["choices"][0]["message"]["content"]
                if isinstance(content, list):
                    content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
                parsed = json.loads(content)
                return schema_model.model_validate(parsed)
            except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValidationError) as exc:
                raise AIProviderError(f"Invalid structured response: {exc}") from exc

openrouter_client = OpenRouterClient()
