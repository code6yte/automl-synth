"""Tests for cleaning agent."""

from automl_synth.agents.cleaning_agent import clean_dataset
from automl_synth.types import GeneratedRow


def make_row(id, text, label="test"):
    return GeneratedRow(
        id=id, text=text, label=label, topic="topic",
        source_agent="generator", difficulty="medium", synthetic_quality_score=0.8,
    )


def test_removes_empty_rows():
    rows = [make_row(1, ""), make_row(2, "valid text here")]
    cleaned = clean_dataset(rows)
    assert len(cleaned) == 1
    assert cleaned[0].id == 2


def test_removes_short_rows():
    rows = [make_row(1, "short"), make_row(2, "this is a valid longer text")]
    cleaned = clean_dataset(rows)
    assert len(cleaned) == 1


def test_removes_duplicates():
    rows = [make_row(1, "same text that is long enough to pass"), make_row(2, "same text that is long enough to pass")]
    cleaned = clean_dataset(rows)
    assert len(cleaned) == 1


def test_removes_meta_language():
    rows = [make_row(1, "Here is a sample text about something"), make_row(2, "A normal text about things")]
    cleaned = clean_dataset(rows)
    assert len(cleaned) == 1
    assert cleaned[0].id == 2


def test_removes_label_leakage():
    rows = [make_row(1, "This text is classified as positive"), make_row(2, "A normal text")]
    cleaned = clean_dataset(rows)
    assert len(cleaned) == 1
