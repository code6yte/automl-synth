# PROJECT.md — AutoML-Synth Project Scope

## Project Title
**AutoML-Synth: CLI + Dashboard for Synthetic Text Classification Dataset Generation**

## One-Line Description
AutoML-Synth is an installable AI tool that generates clean, labeled synthetic datasets for text classification topics and produces dataset quality reports.

## Problem
Creating labeled datasets for text classification is time-consuming. Students and developers often need starter datasets for experiments, demos, prototypes, and coursework, but collecting and labeling hundreds of examples manually is slow.

## Solution
AutoML-Synth accepts a topic, researches it using web search and an LLM provider, generates labeled synthetic text rows, cleans the dataset, analyzes dataset quality, and exports CSV/JSONL/PDF outputs.

## Intended Users

- Students building ML/NLP projects.
- Developers prototyping text classification ideas.
- Educators demonstrating dataset creation.
- Beginners who need clean starter datasets.

## Non-Goals

AutoML-Synth is not:

- a Kaggle replacement
- a production dataset marketplace
- an LLM fine-tuning system
- an AutoML model training system
- a factual verification engine
- a safety-critical dataset creator

## Core User Flow

```text
User topic
  ↓
Research Agent
  ↓
Label Plan
  ↓
Dataset Generator Agent
  ↓
Cleaning Agent
  ↓
Quality Analysis Agent
  ↓
CSV / JSONL / PDF Dataset Card
```

## Required Outputs

For every generation run, create:

```text
output/
├── dataset.csv
├── dataset.jsonl
├── dataset-card.pdf
├── quality-report.json
└── research-report.json
```

## Accepted Dataset Schema

Minimum columns:

```text
id
text
label
topic
source_agent
difficulty
synthetic_quality_score
```

Optional columns:

```text
search_topic
base_fragment_key
llm_provider
research_mode
```

## Locked Scope

The project includes:

- CLI generation
- Dashboard generation
- web-assisted research
- LLM provider abstraction
- dataset generation
- cleaning
- quality analysis
- CSV export
- JSONL export
- PDF Dataset Card export

The project excludes:

- AutoML training
- prediction testing
- model leaderboard
- model download
- authentication
- database
- arbitrary tool execution
