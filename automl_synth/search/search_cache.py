"""Search result cache - saves/loads search results per topic."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from automl_synth.types import SearchResult


def _topic_hash(topic: str) -> str:
    return hashlib.sha256(topic.lower().strip().encode()).hexdigest()[:16]


def _cache_path(topic: str, cache_dir: str) -> Path:
    return Path(cache_dir) / "search_cache" / f"{_topic_hash(topic)}.json"


def save_search_cache(topic: str, results: list[SearchResult], cache_dir: str) -> None:
    """Save search results to cache for reuse."""
    path = _cache_path(topic, cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "topic": topic,
        "results": [
            {"title": r.title, "url": r.url, "snippet": r.snippet}
            for r in results
        ],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_search_cache(topic: str, cache_dir: str) -> list[SearchResult] | None:
    """Load cached search results. Returns None if no cache exists."""
    path = _cache_path(topic, cache_dir)
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    return [
        SearchResult(title=r["title"], url=r["url"], snippet=r["snippet"])
        for r in data.get("results", [])
    ]


def get_snippets(topic: str, cache_dir: str) -> list[str]:
    """Get snippets from cache (title + snippet for keyword extraction)."""
    cached = load_search_cache(topic, cache_dir)
    if not cached:
        return []
    return [f"{r.title} {r.snippet}" for r in cached if r.snippet]


def get_seed_keywords(topic: str, cache_dir: str, top_k: int = 10) -> list[str]:
    """Extract meaningful topic keywords from cached search results."""
    from automl_synth.agents.research_agent import _extract_keywords

    snippets = get_snippets(topic, cache_dir)
    if not snippets:
        return [topic.lower()]
    return _extract_keywords(snippets, top_k=top_k)
