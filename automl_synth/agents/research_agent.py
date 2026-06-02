"""Research agent - researches topic and produces label schema."""

from __future__ import annotations

from collections import Counter
import re

from automl_synth.providers.base import LLMProvider
from automl_synth.search import search_web
from automl_synth.types import ResearchReport


async def research_topic(
    provider: LLMProvider,
    topic: str,
    labels: list[str] | None = None,
    max_search_results: int = 10,
    search_enabled: bool = True,
) -> ResearchReport:
    """Research a topic and produce a structured research report using LLM."""
    search_context = ""
    if search_enabled:
        results = search_web(topic, max_results=max_search_results)
        if results:
            snippets = "\n".join(f"- {r.title}: {r.snippet}" for r in results)
            search_context = f"\nWeb search context:\n{snippets}\n"

    if labels:
        label_list = ", ".join(labels)
    else:
        label_prompt = [
            {
                "role": "system",
                "content": "You are a dataset research assistant. Return ONLY valid JSON.",
            },
            {
                "role": "user",
                "content": f"""Research the topic "{topic}" and suggest 3-6 appropriate classification labels.
Return JSON in this exact format:
{{"labels": ["label1", "label2", ...]}}
{search_context}""",
            },
        ]
        label_resp = await provider.complete_json(label_prompt, temperature=0.3)
        labels = label_resp.get("labels", ["positive", "negative", "neutral"])
        label_list = ", ".join(labels)

    prompt = [
        {
            "role": "system",
            "content": "You are a dataset research assistant. Return ONLY valid JSON.",
        },
        {
            "role": "user",
            "content": f"""For the topic "{topic}" with classification labels: {label_list}
Provide:
1. A brief description for each label
2. Style guidelines for generating synthetic text (tone, length, format)
3. Difficulty levels to use

Return JSON in this exact format:
{{
  "label_descriptions": {{"label1": "description", ...}},
  "style_guidelines": {{"tone": "...", "avg_length": "...", "format_notes": "..."}},
  "difficulty_levels": ["easy", "medium", "hard"]
}}
{search_context}""",
        },
    ]

    result = await provider.complete_json(prompt, temperature=0.3)

    return ResearchReport(
        topic=topic,
        labels=labels if isinstance(labels, list) else result.get("labels", labels),
        label_descriptions=result.get("label_descriptions", {lbl: f"Content about {lbl}" for lbl in labels}),
        style_guidelines=result.get("style_guidelines", {}),
        difficulty_levels=result.get("difficulty_levels", ["easy", "medium", "hard"]),
        source_agent="research",
    )


def _extract_keywords(texts: list[str], top_k: int = 20) -> list[str]:
    """Extract most common meaningful words from texts."""
    words: list[str] = []
    stop_words = {
        "the", "a", "an", "is", "was", "are", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "out", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where", "why",
        "how", "all", "each", "every", "both", "few", "more", "most",
        "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "just", "because", "but", "and", "or",
        "if", "while", "about", "up", "it", "its", "that", "this", "these",
        "those", "which", "who", "whom", "what", "i", "me", "my", "we",
        "our", "you", "your", "he", "him", "his", "she", "her", "they",
        "them", "their", "one", "two", "also", "new", "like", "get",
    }
    for text in texts:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        for word in text.split():
            word = word.strip()
            if word and word not in stop_words and len(word) > 3:
                words.append(word)

    counts = Counter(words)
    return [word for word, _ in counts.most_common(top_k)]


def research_topic_local(
    topic: str,
    max_search_results: int = 10,
) -> ResearchReport:
    """Research a topic using only web search, no LLM."""
    results = search_web(topic, max_results=max_search_results)
    snippets = [r.snippet for r in results if r.snippet]

    keywords = _extract_keywords(snippets)

    if len(keywords) >= 6:
        labels = [k.replace("_", " ").title() for k in keywords[:6]]
    elif len(keywords) >= 3:
        labels = [k.replace("_", " ").title() for k in keywords[:4]]
    else:
        labels = ["Positive", "Negative", "Neutral"]

    label_descriptions = {
        lbl: f"Content related to {lbl.lower()} aspects of {topic}"
        for lbl in labels
    }

    return ResearchReport(
        topic=topic,
        labels=labels,
        label_descriptions=label_descriptions,
        style_guidelines={
            "tone": "informative",
            "avg_length": "medium",
            "format_notes": "Natural sentences about the topic",
        },
        difficulty_levels=["easy", "medium", "hard"],
        source_agent="research_local",
    )
