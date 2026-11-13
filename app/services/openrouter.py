
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

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_model: Type[T],
        schema_name: str,
    ) -> tuple[T, str]:

        if not settings.openrouter_api_key:
            raise AIProviderError(
                "OPENROUTER_API_KEY is not configured"
            )

        models = [
            settings.openrouter_model,
            *settings.fallback_models
        ]

        last_error = None

        for model in models:
            try:
                result = await self._request_model(
                    model,
                    system_prompt,
                    user_prompt,
                    schema_model,
                    schema_name,
                )

                return result, model

            except Exception as exc:
                last_error = exc

                logger.warning(
                    "OpenRouter model %s failed: %s",
                    model,
                    str(exc)[:200],
                )

        raise AIProviderError(
            str(last_error or "No model could generate valid content")
        )

    async def _request_model(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        schema_model: Type[T],
        schema_name: str,
    ) -> T:

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
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": 0.2,
            "max_tokens": 2400,
        }

        schema_payload = {
            **base_payload,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                },
            },
        }

        json_payload = {
            **base_payload,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        system_prompt
                        + "\nReturn exactly one valid JSON object. "
                        + "Do not use Markdown, code fences or explanations. "
                        + "Use double quotes for all JSON keys and strings."
                    ),
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "response_format": {
                "type": "json_object"
            },
        }

        timeout = httpx.Timeout(settings.request_timeout)

        async with httpx.AsyncClient(timeout=timeout) as client:

            # First attempt: strict JSON Schema.
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=schema_payload,
            )

            # Some models/providers do not support JSON Schema.
            if response.status_code in (400, 404, 422):
                logger.warning(
                    "Model %s does not support JSON Schema. "
                    "Trying JSON Mode.",
                    model,
                )

            elif response.status_code >= 400:
                raise AIProviderError(
                    f"OpenRouter HTTP {response.status_code}: "
                    f"{response.text[:500]}"
                )

            else:
                # Schema request was accepted. Validate its response.
                try:
                    return self._parse_response(
                        response,
                        schema_model,
                    )

                except AIProviderError as exc:
                    logger.warning(
                        "Model %s returned invalid structured JSON. "
                        "Retrying with JSON Mode: %s",
                        model,
                        str(exc)[:200],
                    )

            # Second attempt: JSON Mode.
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=json_payload,
            )

            if response.status_code >= 400:
                raise AIProviderError(
                    f"OpenRouter JSON Mode HTTP "
                    f"{response.status_code}: {response.text[:500]}"
                )

            try:
                return self._parse_response(
                    response,
                    schema_model,
                )

            except AIProviderError as exc:
                raise AIProviderError(
                    "Invalid structured response after JSON Mode retry: "
                    + str(exc)
                ) from exc

    @staticmethod
    def _parse_response(
        response: httpx.Response,
        schema_model: Type[T],
    ) -> T:

        try:
            body = response.json()

            choices = body.get("choices", [])

            if not choices:
                raise ValueError("OpenRouter returned no choices")

            message = choices[0].get("message", {})
            content = message.get("content")

            if isinstance(content, list):
                content = "".join(
                    part.get("text", "")
                    for part in content
                    if isinstance(part, dict)
                )

            if not isinstance(content, str) or not content.strip():
                raise ValueError(
                    "Model returned empty or unsupported content"
                )

            parsed = json.loads(content)

            return schema_model.model_validate(parsed)

        except (
            KeyError,
            IndexError,
            TypeError,
            ValueError,
            ValidationError,
            json.JSONDecodeError,
        ) as exc:

            raise AIProviderError(
                f"Invalid structured response: {str(exc)[:250]}"
            ) from exc


openrouter_client = OpenRouterClient()
