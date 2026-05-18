"""JSONL exporter."""

from __future__ import annotations

import json

from automl_synth.types import GeneratedRow


def export_jsonl(rows: list[GeneratedRow], output_path: str) -> str:
    """Export dataset rows to JSONL."""
    with open(output_path, "w", encoding="utf-8") as f:
        for row in rows:
            record = {
                "id": row.id,
                "text": row.text,
                "label": row.label,
                "topic": row.topic,
                "source_agent": row.source_agent,
                "difficulty": row.difficulty,
                "synthetic_quality_score": row.synthetic_quality_score,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return output_path
