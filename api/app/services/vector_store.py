from __future__ import annotations

from typing import Any


async def retrieve_context(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Wave 2 placeholder retrieval that extracts simple topical hints."""
    topics = []
    lowered = query.lower()
    for keyword in ["billing", "security", "deployment", "database", "frontend", "api"]:
        if keyword in lowered:
            topics.append(
                {
                    "source": "keyword-index",
                    "title": f"Context for {keyword}",
                    "snippet": f"Retrieved supporting context for topic '{keyword}'.",
                }
            )
    return topics[:top_k]
