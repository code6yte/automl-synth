"""Generator agent - generates synthetic dataset rows."""

from __future__ import annotations

import random

from automl_synth.models.ngram import HybridTextModel, train_from_snippets
from automl_synth.models.training_cache import load_training_texts
from automl_synth.providers.base import LLMProvider
from automl_synth.search.search_cache import get_seed_keywords, save_search_cache
from automl_synth.search import search_web
from automl_synth.types import GeneratedRow, ResearchReport


async def generate_dataset(
    provider: LLMProvider,
    research: ResearchReport,
    num_rows: int = 300,
    seed: int = 42,
) -> list[GeneratedRow]:
    """Generate synthetic text classification dataset rows."""
    random.seed(seed)
    rows: list[GeneratedRow] = []
    labels = research.labels
    difficulties = research.difficulty_levels
    label_desc = research.label_descriptions
    style = research.style_guidelines

    rows_per_label = num_rows // len(labels)
    remainder = num_rows - (rows_per_label * len(labels))

    label_counts = {label: rows_per_label for label in labels}
    for i in range(remainder):
        label_counts[labels[i % len(labels)]] += 1

    row_id = 1
    for label, count in label_counts.items():
        desc = label_desc.get(label, f"Content about {label}")
        batches = (count + 19) // 20

        for batch_idx in range(batches):
            batch_size = min(20, count - (batch_idx * 20))
            if batch_size <= 0:
                break

            difficulty = difficulties[batch_idx % len(difficulties)]
            prompt = _build_generation_prompt(
                topic=research.topic,
                label=label,
                label_desc=desc,
                batch_size=batch_size,
                difficulty=difficulty,
                style=style,
            )

            try:
                result = await provider.complete_json(prompt, temperature=0.7)
                samples = result.get("samples", [])
                for sample in samples:
                    text = sample.get("text", "").strip()
                    if text:
                        score = _compute_row_score(text, difficulty)
                        rows.append(
                            GeneratedRow(
                                id=row_id,
                                text=text,
                                label=label,
                                topic=research.topic,
                                source_agent="generator",
                                difficulty=difficulty,
                                synthetic_quality_score=score,
                            )
                        )
                        row_id += 1
            except Exception:
                for _ in range(batch_size):
                    text = _fallback_text(research.topic, label, difficulty)
                    score = _compute_row_score(text, difficulty)
                    rows.append(
                        GeneratedRow(
                            id=row_id,
                            text=text,
                            label=label,
                            topic=research.topic,
                            source_agent="generator",
                            difficulty=difficulty,
                            synthetic_quality_score=score,
                        )
                    )
                    row_id += 1

    while len(rows) < num_rows:
        label = random.choice(labels)
        difficulty = random.choice(difficulties)
        text = _fallback_text(research.topic, label, difficulty)
        rows.append(
            GeneratedRow(
                id=row_id,
                text=text,
                label=label,
                topic=research.topic,
                source_agent="generator",
                difficulty=difficulty,
                synthetic_quality_score=_compute_row_score(text, difficulty),
            )
        )
        row_id += 1

    random.shuffle(rows)
    for i, row in enumerate(rows):
        row.id = i + 1

    return rows[:num_rows]


def _build_generation_prompt(
    topic: str,
    label: str,
    label_desc: str,
    batch_size: int,
    difficulty: str,
    style: dict,
) -> list[dict[str, str]]:
    style_notes = ""
    if style:
        parts = []
        if "tone" in style:
            parts.append(f"Tone: {style['tone']}")
        if "avg_length" in style:
            parts.append(f"Average length: {style['avg_length']}")
        if "format_notes" in style:
            parts.append(f"Format: {style['format_notes']}")
        style_notes = "\n".join(parts)

    return [
        {
            "role": "system",
            "content": "You are a synthetic data generator. Return ONLY valid JSON with no extra text.",
        },
        {
            "role": "user",
            "content": f"""Generate {batch_size} synthetic text samples for topic "{topic}" classified as "{label}".
Label description: {label_desc}
Difficulty: {difficulty}
{style_notes}

Rules:
- Each text must be natural and realistic for the topic
- Texts should vary in length and style
- Do NOT include meta-language like "Here is a sample" or "This text is about"
- Do NOT mention the label or classification in the text
- Return ONLY valid JSON

Format:
{{"samples": [{{"text": "actual text content here"}}, ...]}}""",
        },
    ]


def _compute_row_score(text: str, difficulty: str) -> float:
    score = 0.7
    length = len(text)
    if 50 <= length <= 500:
        score += 0.2
    elif length > 500:
        score += 0.1
    words = len(text.split())
    if words >= 10:
        score += 0.1
    difficulty_bonus = {"easy": 0.0, "medium": 0.0, "hard": 0.0}
    score += difficulty_bonus.get(difficulty, 0.0)
    return round(min(score, 1.0), 2)


def _fallback_text(topic: str, label: str, difficulty: str) -> str:
    templates = [
        f"This is a sample text about {topic} that falls under the {label} category.",
        f"Regarding {topic}, this example demonstrates characteristics of {label}.",
        f"An example related to {topic} with {label} classification.",
    ]
    return random.choice(templates)


def generate_dataset_local(
    research: ResearchReport,
    num_rows: int = 300,
    seed: int = 42,
    max_search_results: int = 10,
    cache_dir: str | None = None,
) -> list[GeneratedRow]:
    """Generate dataset using local model trained on accumulated dataset rows.

    - First run: trains on search snippets (fallback), saves results
    - Subsequent runs: trains on ALL previously generated rows from any topic
    - Topic relevance comes from seed keywords extracted from cached search results
    """
    rng = random.Random(seed)

    results = search_web(research.topic, max_results=max_search_results)
    snippets = [r.snippet for r in results if r.snippet]

    if cache_dir:
        save_search_cache(research.topic, results, cache_dir)

    if not snippets:
        snippets = [f"Information about {research.topic}"]

    prior_texts = load_training_texts(cache_dir) if cache_dir else []

    if prior_texts:
        model = HybridTextModel(n=3, n_components=50, seed=seed)
        model.train(prior_texts)
    else:
        model = train_from_snippets(snippets, seed=seed)

    rows: list[GeneratedRow] = []
    labels = research.labels
    difficulties = research.difficulty_levels

    rows_per_label = num_rows // len(labels)
    remainder = num_rows - (rows_per_label * len(labels))

    label_counts = {label: rows_per_label for label in labels}
    for i in range(remainder):
        label_counts[labels[i % len(labels)]] += 1

    seed_keywords = (
        get_seed_keywords(research.topic, cache_dir, top_k=10)
        if cache_dir
        else [research.topic.lower()]
    )

    row_id = 1
    for label, count in label_counts.items():
        for _ in range(count):
            difficulty = rng.choice(difficulties)

            temp_map = {"easy": 0.5, "medium": 0.8, "hard": 1.2}
            temperature = temp_map.get(difficulty, 0.8)

            seed_list = [label.lower()] + seed_keywords[:3]

            text = model.generate(
                min_words=10,
                max_words=40,
                seed_words=seed_list,
                temperature=temperature,
            )

            if not text or len(text.split()) < 5:
                text = _fallback_text(research.topic, label, difficulty)

            score = _compute_row_score(text, difficulty)
            rows.append(
                GeneratedRow(
                    id=row_id,
                    text=text,
                    label=label,
                    topic=research.topic,
                    source_agent="generator_local",
                    difficulty=difficulty,
                    synthetic_quality_score=score,
                )
            )
            row_id += 1

    rng.shuffle(rows)
    for i, row in enumerate(rows):
        row.id = i + 1

    return rows[:num_rows]
