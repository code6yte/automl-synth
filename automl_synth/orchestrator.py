"""Orchestrator - runs the full generation pipeline."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from automl_synth.agents.cleaning_agent import clean_dataset
from automl_synth.agents.generator_agent import generate_dataset, generate_dataset_local
from automl_synth.agents.quality_agent import analyze_quality
from automl_synth.agents.research_agent import research_topic, research_topic_local
from automl_synth.exporters.csv_exporter import export_csv
from automl_synth.exporters.jsonl_exporter import export_jsonl
from automl_synth.exporters.pdf_exporter import export_pdf
from automl_synth.models.training_cache import append_rows
from automl_synth.providers.base import LLMProvider
from automl_synth.types import GenerationResult


async def run_pipeline(
    provider: LLMProvider,
    topic: str,
    num_rows: int = 300,
    labels: list[str] | None = None,
    seed: int = 42,
    output_dir: str = "./output",
    search_enabled: bool = True,
    max_search_results: int = 10,
    formats: list[str] | None = None,
) -> GenerationResult:
    """Run the full dataset generation pipeline."""
    run_id = str(uuid.uuid4())[:8]
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    files: dict[str, str] = {}

    research = await research_topic(
        provider=provider,
        topic=topic,
        labels=labels,
        max_search_results=max_search_results,
        search_enabled=search_enabled,
    )

    raw_rows = await generate_dataset(
        provider=provider,
        research=research,
        num_rows=num_rows,
        seed=seed,
    )

    cleaned_rows = clean_dataset(raw_rows)

    quality = analyze_quality(cleaned_rows)

    if formats is None:
        formats = ["csv", "jsonl", "pdf", "json"]

    base_name = out_path / "dataset"

    if "csv" in formats:
        csv_path = export_csv(cleaned_rows, str(base_name.with_suffix(".csv")))
        files["csv"] = csv_path

    if "jsonl" in formats:
        jsonl_path = export_jsonl(cleaned_rows, str(base_name.with_suffix(".jsonl")))
        files["jsonl"] = jsonl_path

    if "pdf" in formats:
        pdf_path = export_pdf(cleaned_rows, research, quality, str(out_path / "dataset-card.pdf"))
        files["pdf"] = pdf_path

    if "json" in formats:
        quality_path = str(out_path / "quality-report.json")
        with open(quality_path, "w") as f:
            json.dump(
                {
                    "quality_score": quality.quality_score,
                    "quality_grade": quality.quality_grade,
                    "total_rows": quality.total_rows,
                    "label_distribution": quality.label_distribution,
                    "class_balance_ratio": quality.class_balance_ratio,
                    "duplicate_rows": quality.duplicate_rows,
                    "label_leakage_rows": quality.label_leakage_rows,
                    "repeated_fragment_groups": quality.repeated_fragment_groups,
                    "warnings": quality.warnings,
                    "metrics": quality.metrics,
                },
                f,
                indent=2,
            )
        files["quality_report"] = quality_path

        research_path = str(out_path / "research-report.json")
        with open(research_path, "w") as f:
            json.dump(
                {
                    "topic": research.topic,
                    "labels": research.labels,
                    "label_descriptions": research.label_descriptions,
                    "style_guidelines": research.style_guidelines,
                    "difficulty_levels": research.difficulty_levels,
                },
                f,
                indent=2,
            )
        files["research_report"] = research_path

    return GenerationResult(
        run_id=run_id,
        topic=topic,
        rows=cleaned_rows,
        research_report=research,
        quality_report=quality,
        output_dir=str(out_path),
        files=files,
    )


def run_pipeline_local(
    topic: str,
    num_rows: int = 300,
    labels: list[str] | None = None,
    seed: int = 42,
    output_dir: str = "./output",
    max_search_results: int = 10,
    formats: list[str] | None = None,
    cache_dir: str | None = None,
) -> GenerationResult:
    """Run the full dataset generation pipeline using local ngram model (no LLM)."""
    run_id = str(uuid.uuid4())[:8]
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    files: dict[str, str] = {}

    research = research_topic_local(
        topic=topic,
        max_search_results=max_search_results,
    )

    if labels:
        research.labels = labels
        research.label_descriptions = {
            lbl: f"Content related to {lbl.lower()} aspects of {topic}"
            for lbl in labels
        }

    raw_rows = generate_dataset_local(
        research=research,
        num_rows=num_rows,
        seed=seed,
        max_search_results=max_search_results,
        cache_dir=cache_dir,
    )

    cleaned_rows = clean_dataset(raw_rows)

    if cache_dir:
        append_rows(cleaned_rows, cache_dir)

    quality = analyze_quality(cleaned_rows)

    if formats is None:
        formats = ["csv", "jsonl", "pdf", "json"]

    base_name = out_path / "dataset"

    if "csv" in formats:
        csv_path = export_csv(cleaned_rows, str(base_name.with_suffix(".csv")))
        files["csv"] = csv_path

    if "jsonl" in formats:
        jsonl_path = export_jsonl(cleaned_rows, str(base_name.with_suffix(".jsonl")))
        files["jsonl"] = jsonl_path

    if "pdf" in formats:
        pdf_path = export_pdf(cleaned_rows, research, quality, str(out_path / "dataset-card.pdf"))
        files["pdf"] = pdf_path

    if "json" in formats:
        quality_path = str(out_path / "quality-report.json")
        with open(quality_path, "w") as f:
            json.dump(
                {
                    "quality_score": quality.quality_score,
                    "quality_grade": quality.quality_grade,
                    "total_rows": quality.total_rows,
                    "label_distribution": quality.label_distribution,
                    "class_balance_ratio": quality.class_balance_ratio,
                    "duplicate_rows": quality.duplicate_rows,
                    "label_leakage_rows": quality.label_leakage_rows,
                    "repeated_fragment_groups": quality.repeated_fragment_groups,
                    "warnings": quality.warnings,
                    "metrics": quality.metrics,
                },
                f,
                indent=2,
            )
        files["quality_report"] = quality_path

        research_path = str(out_path / "research-report.json")
        with open(research_path, "w") as f:
            json.dump(
                {
                    "topic": research.topic,
                    "labels": research.labels,
                    "label_descriptions": research.label_descriptions,
                    "style_guidelines": research.style_guidelines,
                    "difficulty_levels": research.difficulty_levels,
                },
                f,
                indent=2,
            )
        files["research_report"] = research_path

    return GenerationResult(
        run_id=run_id,
        topic=topic,
        rows=cleaned_rows,
        research_report=research,
        quality_report=quality,
        output_dir=str(out_path),
        files=files,
    )
