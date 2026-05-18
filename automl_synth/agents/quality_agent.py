"""Quality analysis agent."""

from __future__ import annotations

from collections import Counter

from automl_synth.types import GeneratedRow, QualityReport, QualityGrade


def analyze_quality(rows: list[GeneratedRow]) -> QualityReport:
    """Analyze dataset quality and produce a quality report."""
    total = len(rows)
    if total == 0:
        return QualityReport(
            quality_score=0.0,
            quality_grade=QualityGrade.NEEDS_IMPROVEMENT.value,
            total_rows=0,
            label_distribution={},
            class_balance_ratio=0.0,
            duplicate_rows=0,
            label_leakage_rows=0,
            repeated_fragment_groups=0,
            missing_text_rows=0,
            short_text_rows=0,
            unique_vocabulary_ratio=0.0,
            avg_text_length=0.0,
            avg_word_count=0.0,
            meta_language_rows=0,
            single_source_agent_rows=0,
            warnings=["Dataset is empty"],
        )

    label_counts = Counter(r.label for r in rows)
    max_count = max(label_counts.values())
    min_count = min(label_counts.values())
    balance_ratio = min_count / max_count if max_count > 0 else 0.0

    texts = [r.text for r in rows]
    text_lengths = [len(r.text) for r in rows]
    word_counts = [len(r.text.split()) for r in rows]

    all_words = set()
    for t in texts:
        all_words.update(t.lower().split())
    unique_vocab_ratio = len(all_words) / max(sum(word_counts), 1)

    missing = sum(1 for t in texts if not t.strip())
    short = sum(1 for t in texts if len(t.strip()) < 20)
    duplicates = total - len(set(t.lower().strip() for t in texts))

    source_agents = Counter(r.source_agent for r in rows)
    single_source = 1 if len(source_agents) == 1 else 0

    score = 100.0
    warnings: list[str] = []

    if balance_ratio < 0.5:
        score -= 15
        warnings.append(f"Class imbalance detected (ratio: {balance_ratio:.2f})")

    if duplicates > 0:
        dup_pct = duplicates / total
        score -= min(20, dup_pct * 100)
        warnings.append(f"{duplicates} duplicate rows found")

    if missing > 0:
        score -= 15
        warnings.append(f"{missing} rows with missing text")

    if short > 0:
        score -= 10
        warnings.append(f"{short} rows with very short text")

    if unique_vocab_ratio < 0.1:
        score -= 10
        warnings.append(f"Low vocabulary diversity ({unique_vocab_ratio:.2%})")

    if single_source:
        score -= 8
        warnings.append("All rows from a single source agent")

    if balance_ratio < 0.7:
        warnings.append("Consider balancing class distribution")

    score = max(0.0, min(100.0, score))

    if score >= 90:
        grade = QualityGrade.EXCELLENT.value
    elif score >= 75:
        grade = QualityGrade.GOOD.value
    elif score >= 60:
        grade = QualityGrade.FAIR.value
    else:
        grade = QualityGrade.NEEDS_IMPROVEMENT.value

    return QualityReport(
        quality_score=round(score, 1),
        quality_grade=grade,
        total_rows=total,
        label_distribution=dict(label_counts),
        class_balance_ratio=round(balance_ratio, 3),
        duplicate_rows=duplicates,
        label_leakage_rows=0,
        repeated_fragment_groups=0,
        missing_text_rows=missing,
        short_text_rows=short,
        unique_vocabulary_ratio=round(unique_vocab_ratio, 3),
        avg_text_length=round(sum(text_lengths) / total, 1),
        avg_word_count=round(sum(word_counts) / total, 1),
        meta_language_rows=0,
        single_source_agent_rows=single_source,
        warnings=warnings,
        metrics={
            "total_rows": total,
            "num_labels": len(label_counts),
            "labels": list(label_counts.keys()),
        },
    )
