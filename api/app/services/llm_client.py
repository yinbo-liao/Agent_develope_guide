from __future__ import annotations

from typing import Any

from app.services.model_router import model_router


class LLMClient:
    """Simulated generation client with model-aware cost estimation."""

    @staticmethod
    async def generate(
        prompt: str,
        context: list[dict[str, Any]] | None = None,
        max_tokens: int = 2000,
        temperature: float = 0.3,
        model: str = "claude-sonnet-4-6",
    ) -> dict[str, Any]:
        context = context or []
        supporting_lines = "\n".join(f"- {item['snippet']}" for item in context[:3])
        content = (
            "Generated response\n\n"
            f"Request: {prompt}\n\n"
            "Summary:\n"
            f"{supporting_lines if supporting_lines else '- No additional context retrieved.'}\n\n"
            f"Execution profile: model={model}, max_tokens={max_tokens}, temperature={temperature}."
        )
        # ~1.3 tokens per word for English text (industry standard)
        tokens = min(max_tokens, max(1, int(len(content.split()) * 1.3)))
        estimated_cost = model_router.estimate_cost(model, tokens)
        return {
            "content": content,
            "tokens_used": tokens,
            "cost_usd": estimated_cost,
            "model": model,
        }
