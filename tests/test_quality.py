"""Tests for quality agent."""

from automl_synth.agents.quality_agent import analyze_quality
from automl_synth.types import GeneratedRow, QualityGrade


def make_row(id, text, label="positive"):
    return GeneratedRow(
        id=id, text=text, label=label, topic="topic",
        source_agent="generator", difficulty="medium", synthetic_quality_score=0.8,
    )


def test_empty_dataset():
    report = analyze_quality([])
    assert report.quality_score == 0.0
    assert report.total_rows == 0


def test_balanced_dataset():
    rows = [
        make_row(1, "This is a great product and I love it very much", "positive"),
        make_row(2, "This is a terrible product and I hate it very much", "negative"),
        make_row(3, "Another positive review about the product quality", "positive"),
        make_row(4, "Another negative review about the bad experience", "negative"),
    ]
    report = analyze_quality(rows)
    assert report.total_rows == 4
    assert report.class_balance_ratio == 1.0
    assert report.quality_score >= 80


def test_imbalanced_dataset():
    rows = [
        make_row(1, "Great product love it", "positive"),
        make_row(2, "Amazing quality excellent", "positive"),
        make_row(3, "Another good thing here", "positive"),
        make_row(4, "Another positive example", "positive"),
        make_row(5, "Bad product", "negative"),
    ]
    report = analyze_quality(rows)
    assert report.class_balance_ratio < 0.5
    assert any("imbalance" in w.lower() for w in report.warnings)


def test_quality_grade():
    rows = [
        make_row(1, "This is a great product and I love it very much", "positive"),
        make_row(2, "This is a terrible product and I hate it very much", "negative"),
    ]
    report = analyze_quality(rows)
    assert report.quality_grade in [g.value for g in QualityGrade]
