"""Web search module using DuckDuckGo."""

from __future__ import annotations

from automl_synth.types import SearchResult


def search_web(query: str, max_results: int = 10) -> list[SearchResult]:
    """Search the web using DuckDuckGo and return results."""
    try:
        from ddgs import DDGS

        results: list[SearchResult] = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    SearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                    )
                )
        return results
    except ImportError:
        return []
    except Exception:
        return []
