from __future__ import annotations

from typing import Type

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.settings import settings


class LLMClient:
    def __init__(self) -> None:
        api_key = settings.OPENAI_API_KEY
        self._client = AsyncOpenAI(api_key=api_key) if api_key else None

    async def generate_structured(
        self,
        *,
        model: str,
        schema: Type[BaseModel],
        prompt: str,
    ) -> BaseModel:
        if not self._client:
            raise RuntimeError("OPENAI_API_KEY is not set")

        # OpenAI Chat Completions API с Structured Outputs (JSON Schema)
        resp = await self._client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "schema": schema.model_json_schema(),
                    "strict": True,
                },
            },
        )

        # Достаём JSON текст из первого ответного сообщения
        try:
            json_text = resp.choices[0].message.content
            if json_text is None:
                raise RuntimeError("OpenAI response content is None")
        except (IndexError, AttributeError) as e:
            raise RuntimeError(f"Unexpected OpenAI response shape: {e}")

        return schema.model_validate_json(json_text)



