"""Core data types for AutoML-Synth."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class QualityGrade(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    NEEDS_IMPROVEMENT = "Needs Improvement"


class ProviderType(str, Enum):
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    OPENAI_COMPATIBLE = "openai_compatible"


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


@dataclass
class ResearchReport:
    topic: str
    labels: list[str]
    label_descriptions: dict[str, str]
    style_guidelines: dict[str, Any]
    difficulty_levels: list[str] = field(default_factory=lambda: ["easy", "medium", "hard"])
    source_agent: str = "research"


@dataclass
class GeneratedRow:
    id: int
    text: str
    label: str
    topic: str
    source_agent: str
    difficulty: str
    synthetic_quality_score: float


@dataclass
class QualityReport:
    quality_score: float
    quality_grade: str
    total_rows: int
    label_distribution: dict[str, int]
    class_balance_ratio: float
    duplicate_rows: int
    label_leakage_rows: int
    repeated_fragment_groups: int
    missing_text_rows: int
    short_text_rows: int
    unique_vocabulary_ratio: float
    avg_text_length: float
    avg_word_count: float
    meta_language_rows: int
    single_source_agent_rows: int
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    run_id: str
    topic: str
    rows: list[GeneratedRow]
    research_report: ResearchReport
    quality_report: QualityReport
    output_dir: str
    files: dict[str, str] = field(default_factory=dict)
