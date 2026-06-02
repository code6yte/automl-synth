"""Training cache - accumulates dataset rows across runs for model training."""

from __future__ import annotations

import json
from pathlib import Path

from automl_synth.types import GeneratedRow


TRAINING_FILE = "training_data.jsonl"


def _training_path(cache_dir: str) -> Path:
    return Path(cache_dir) / TRAINING_FILE


def load_training_texts(cache_dir: str) -> list[str]:
    """Load text from all previously generated dataset rows."""
    path = _training_path(cache_dir)
    if not path.exists():
        return []
    texts: list[str] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                text = data.get("text", "")
                if text and len(text) >= 20:
                    texts.append(text)
            except json.JSONDecodeError:
                continue
    return texts


def load_training_count(cache_dir: str) -> int:
    """Count accumulated training rows."""
    return len(load_training_texts(cache_dir))


def append_rows(rows: list[GeneratedRow], cache_dir: str) -> None:
    """Append this run's cleaned rows to the growing training pool."""
    path = _training_path(cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        for row in rows:
            record = {
                "text": row.text,
                "label": row.label,
                "topic": row.topic,
                "difficulty": row.difficulty,
                "source_agent": row.source_agent,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
