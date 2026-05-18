"""CSV exporter."""

from __future__ import annotations

import csv

from automl_synth.types import GeneratedRow


def export_csv(rows: list[GeneratedRow], output_path: str) -> str:
    """Export dataset rows to CSV."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "text", "label", "topic", "source_agent", "difficulty", "synthetic_quality_score"])
        for row in rows:
            writer.writerow([
                row.id,
                row.text,
                row.label,
                row.topic,
                row.source_agent,
                row.difficulty,
                row.synthetic_quality_score,
            ])
    return output_path
