"""Cleaning agent - removes problematic rows from dataset."""

from __future__ import annotations

import re

from automl_synth.types import GeneratedRow

META_PATTERNS = [
    r"(?i)here is a sample",
    r"(?i)this text is about",
    r"(?i)this is a (synthetic|generated|sample|fake)",
    r"(?i)the following (text|example|sample)",
    r"(?i)as an? (ai|language model|assistant)",
    r"(?i)i (cannot|can't|will not|won't)",
    r"(?i)note: this is",
    r"(?i)example (text|of|for)",
]

LEAKAGE_PATTERNS = [
    r"(?i)(label|class|category)\s*[:=]\s*\w+",
    r"(?i)classified?\s+as\s+",
    r"(?i)(sentiment|classification)\s*[:=]",
    r"(?i)this (is|falls under|belongs to) (the\s+)?\w+\s+(category|class|label)",
]


def clean_dataset(rows: list[GeneratedRow]) -> list[GeneratedRow]:
    """Remove null, short, duplicate, meta-language, and leakage rows."""
    cleaned: list[GeneratedRow] = []
    seen_texts: set[str] = set()

    for row in rows:
        text = row.text.strip()

        if not text:
            continue

        if len(text) < 10:
            continue

        if _has_meta_language(text):
            continue

        if _has_label_leakage(text):
            continue

        normalized = text.lower().strip()
        if normalized in seen_texts:
            continue
        seen_texts.add(normalized)

        cleaned.append(row)

    return cleaned


def _has_meta_language(text: str) -> bool:
    for pattern in META_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def _has_label_leakage(text: str) -> bool:
    for pattern in LEAKAGE_PATTERNS:
        if re.search(pattern, text):
            return True
    return False
