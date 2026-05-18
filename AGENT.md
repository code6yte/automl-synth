# AGENT.md — Build Instructions for AutoML-Synth Coding Agent

You are a CLI coding agent. Build **AutoML-Synth** exactly as a semester-level installable Python package with a CLI, FastAPI server, and optional React dashboard.

The project is **not** a startup, not a research framework, not an LLM-training project, and not an AutoML model-training platform. Keep scope locked.

## Mission
Build an installable AI dataset generation tool for **text classification datasets**.

User provides a topic such as:

```bash
automl-synth generate --topic "Classify news headlines into politics, sports, technology, entertainment, and business" --rows 300 --out ./output
```

The system must:

1. Research the topic using web search + LLM.
2. Create a label plan.
3. Generate a synthetic labeled text dataset.
4. Clean bad rows.
5. Analyze dataset quality.
6. Export CSV, JSONL, and PDF Dataset Card.
7. Optionally serve a React dashboard through FastAPI.

## Hard Constraints

Do not implement:

- AutoML model training.
- Prediction testing.
- LLM fine-tuning.
- Arbitrary shell command execution by the LLM.
- User accounts.
- Database.
- Cloud deployment platform.
- Kaggle replacement features.
- Production marketplace features.

## Required Stack

- Core engine: Python package.
- CLI: Typer.
- Backend: FastAPI.
- Dashboard: React + Vite, built into static files.
- LLM provider: OpenRouter API by default.
- Optional LLM provider: Ollama/custom local endpoint.
- Search: DuckDuckGo-compatible search package.
- Data: pandas.
- Export: CSV, JSONL, PDF.
- Install: pipx and curl install script.

## Primary Commands

Implement only these public commands:

```bash
automl-synth generate --topic "..." --rows 300 --out ./output
```

```bash
automl-synth serve --host 127.0.0.1 --port 8000
```

```bash
automl-synth doctor
```

## Implementation Priority

1. Build Python package structure.
2. Implement config loading and LLM provider abstraction.
3. Implement Research Agent.
4. Implement Generator Agent.
5. Implement Cleaning Agent.
6. Implement Quality Analysis Agent.
7. Implement CSV/JSONL/PDF exporters.
8. Implement Typer CLI.
9. Implement FastAPI server endpoints.
10. Build React dashboard and serve static files.
11. Add installer and doctor command.
12. Add tests.

## Quality Rule
Generated text must match the topic format.

For news headline topics, generate actual headlines:

```text
Government approves new education policy after cabinet debate
```

Never generate domain-mismatched rows such as:

```text
I ran into economics and it made the experience frustrating
```

## LLM Rule
Use the LLM as a service. The app must not manage OpenRouter or Ollama installation.

The app only needs:

- provider name
- base URL
- API key if required
- model name

## Safety Rule
The LLM must not be allowed to execute arbitrary commands, edit files outside the output directory, install packages, delete files, or control the OS.

Allowed tools are only:

- web search
- LLM completion
- dataset generation
- cleaning
- quality analysis
- export CSV/JSONL/PDF
- write files inside output directory

## Final Definition of Done

A user can run:

```bash
automl-synth doctor
```

then:

```bash
automl-synth generate --topic "Classify mobile app reviews into praise, bug_report, feature_request, usability_issue, and pricing_complaint" --rows 300 --out ./demo-output
```

and receive:

```text
demo-output/dataset.csv
demo-output/dataset.jsonl
demo-output/dataset-card.pdf
demo-output/quality-report.json
```

Then:

```bash
automl-synth serve
```

opens the dashboard at:

```text
http://127.0.0.1:8000
```
