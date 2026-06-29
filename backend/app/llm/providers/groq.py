from __future__ import annotations

from groq import Groq

from app.core.exceptions import LLMError
from app.llm.base import LLMMessage, LLMResponse


class GroqLLMProvider:
    """Groq chat completion provider behind the project LLM interface."""

    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        temperature: float = 0.2,
        max_tokens: int = 900,
    ) -> None:
        if not api_key:
            raise LLMError("GROQ_API_KEY is required for GroqLLMProvider")
        self.model_name = model_name
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._client = Groq(api_key=api_key)

    def generate(self, messages: list[LLMMessage]) -> LLMResponse:
        try:
            completion = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": message.role, "content": message.content}
                    for message in messages
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            content = completion.choices[0].message.content or ""
            return LLMResponse(content=content.strip(), model=self.model_name)
        except Exception as exc:
            raise LLMError("Groq generation failed") from exc
