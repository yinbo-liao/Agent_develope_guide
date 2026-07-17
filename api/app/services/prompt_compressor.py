from __future__ import annotations

from typing import Any

# Maximum characters per retrieval snippet before truncation
MAX_SNIPPET_CHARS = 200
# Maximum number of context snippets to pass to the LLM
MAX_CONTEXT_ITEMS = 3


def compress_context(
    retrieval_results: list[dict[str, Any]] | None,
    max_items: int = MAX_CONTEXT_ITEMS,
    max_chars: int = MAX_SNIPPET_CHARS,
) -> list[dict[str, Any]]:
    """Compress retrieval context: keep top-N items, truncate long snippets."""
    if not retrieval_results:
        return []

    # Keep only the top N items
    limited = retrieval_results[:max_items]

    # Truncate long snippets
    compressed: list[dict[str, Any]] = []
    for item in limited:
        snippet = str(item.get("snippet", ""))
        if len(snippet) > max_chars:
            snippet = snippet[: max_chars - 3] + "..."
        compressed.append({**item, "snippet": snippet})

    return compressed


def compress_prompt(query: str, max_query_chars: int = 2000) -> str:
    """Compress a verbose user query by truncation if needed."""
    if len(query) <= max_query_chars:
        return query
    return query[: max_query_chars - 3] + "..."


def estimate_prompt_tokens(prompt: str, context: list[dict[str, Any]]) -> int:
    """Estimate total prompt tokens (input only) using ~1.3 tokens/word."""
    total_text = prompt + " " + " ".join(
        str(item.get("snippet", "")) for item in context
    )
    word_count = len(total_text.split())
    return max(1, int(word_count * 1.3))
