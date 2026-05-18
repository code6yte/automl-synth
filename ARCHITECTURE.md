# ARCHITECTURE.md — System Architecture

## Architecture Style
AutoML-Synth is a **Python core engine** with two interfaces:

1. CLI interface through Typer.
2. Web dashboard through FastAPI + bundled React static files.

The CLI and dashboard must call the same orchestrator pipeline.

## High-Level Diagram

```text
CLI / Dashboard
      ↓
FastAPI API / Typer Command
      ↓
Orchestrator
      ↓
Research Agent
      ↓
LLM Provider Adapter + Web Search
      ↓
Generator Agent
      ↓
Cleaning Agent
      ↓
Quality Analysis Agent
      ↓
Exporters
      ↓
CSV / JSONL / PDF / JSON reports
```

## Core Design Principles

1. **Core engine first**: Business logic lives in Python modules, not React.
2. **Provider agnostic**: Agents call one LLM interface, not provider-specific code.
3. **Dashboard optional**: CLI must work without the dashboard.
4. **No arbitrary execution**: LLM cannot execute shell commands.
5. **Deterministic outputs when seeded**: Generation should accept a seed.
6. **Quality before volume**: Bad rows should be removed even if row count decreases.

## Main Package Structure

```text
automl_synth/
├── cli.py
├── config.py
├── orchestrator.py
├── types.py
│
├── agents/
│   ├── research_agent.py
│   ├── generator_agent.py
│   ├── cleaning_agent.py
│   ├── quality_agent.py
│   └── report_agent.py
│
├── providers/
│   ├── base.py
│   ├── openrouter.py
│   ├── ollama.py
│   └── openai_compatible.py
│
├── exporters/
│   ├── csv_exporter.py
│   ├── jsonl_exporter.py
│   └── pdf_exporter.py
│
├── search/
│   └── web_search.py
│
├── api/
│   └── server.py
│
└── dashboard/
    └── dist/
```

## Interface Responsibilities

### CLI
Responsible for:

- accepting topic/rows/output path/provider settings
- running orchestrator
- writing outputs
- printing status and quality summary

### FastAPI
Responsible for:

- exposing generate endpoint
- serving dashboard static files
- returning generated dataset preview and report metadata
- exposing download endpoints

### React Dashboard
Responsible for:

- polished topic input
- agent progress timeline
- dataset preview
- quality dashboard
- download buttons

React must not contain API keys or LLM calls.

## LLM Provider Layer

All agents must call:

```python
provider.complete_json(messages, schema_hint=None)
```

Provider implementations:

```text
OpenRouterProvider
OllamaProvider
OpenAICompatibleProvider
```

OpenRouter is default. Ollama/custom URL is optional.

## Data Flow

### Step 1 — Research
Input:

```json
{"topic": "Classify news headlines into politics, sports, technology, entertainment, and business"}
```

Output:

```json
{
  "topic": "...",
  "task_type": "news_headline_classification",
  "labels": ["politics", "sports", "technology", "entertainment", "business"],
  "label_profiles": {
    "politics": {
      "description": "...",
      "patterns": ["government", "election", "policy"],
      "seed_examples": ["Government announces new policy after debate"]
    }
  }
}
```

### Step 2 — Generate
Input: research report + rows.

Output: raw dataframe.

### Step 3 — Clean
Input: raw dataframe.

Output: clean dataframe.

### Step 4 — Analyze Quality
Input: clean dataframe.

Output: quality report.

### Step 5 — Export
Input: clean dataframe + reports.

Output: CSV, JSONL, PDF, JSON metadata.

## Serving Dashboard
The React dashboard should be built into `automl_synth/dashboard/dist` and served by FastAPI using static file support. FastAPI supports mounting static files from a directory.

## No Model Training
Do not add scikit-learn training, prediction testing, model leaderboard, or F1/accuracy metrics. This project is only dataset generation and quality analysis.
