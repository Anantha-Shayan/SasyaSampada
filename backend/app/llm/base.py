from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMMessage:
    role: str
    content: str


@dataclass(frozen=True)
class LLMResponse:
    content: str
    model: str


class LLMProvider(Protocol):
    model_name: str

    def generate(self, messages: list[LLMMessage]) -> LLMResponse:
        """Generate a response from chat-style messages."""
