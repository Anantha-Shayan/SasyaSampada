# `app/llm/providers`

Pluggable LLM backends behind a common `LLMProvider` protocol.

**Default:** Groq API via `langchain-groq` or direct `groq` SDK.

**Swappable:** OpenRouter (current chatbot), OpenAI, local models.

Existing `app/services/chatbot.py` will migrate here in Phase 12.
