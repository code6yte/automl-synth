"""Research agent - researches topic and produces label schema."""

from __future__ import annotations

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
    """Research a topic and produce a structured research report."""
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
