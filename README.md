# AutoML-Synth

CLI + Dashboard for generating synthetic text classification datasets using **LLM APIs** or a **local hybrid SVD+ngram model** — no API key required.

## Features

- **Topic-driven** — enter any topic, get a labeled dataset
- **Local generation** — built-in hybrid SVD+ngram model, zero API cost
- **LLM generation** — multi-provider: OpenRouter, Ollama, Groq, Cerebras, DeepInfra, Fireworks, SambaNova, NVIDIA, OpenAI, DeepSeek, Mistral, and more
- **Web research** — DuckDuckGo search provides context for better data
- **Auto-cleaning** — removes duplicates, meta-language, label leakage, short rows
- **Quality scoring** — 0-100 with detailed metrics and warnings
- **Training accumulation** — model learns general dataset generation skill across runs
- **Search caching** — avoid repeated network calls for repeat topics
- **Multiple exports** — CSV, JSONL, PDF dataset card, JSON reports
- **Dashboard** — web UI at http://127.0.0.1:8000

## Quick Start

```bash
# No API key needed for local generation:
automl-synth generate --topic "product reviews" --rows 300 --local

# With LLM (requires API key):
export OPENROUTER_API_KEY="sk-or-..."
automl-synth generate --topic "movie reviews" --rows 300

# Start web dashboard:
automl-synth serve
```

## Local Generation (No API Key)

Uses a hybrid SVD+ngram model that improves with every use:

| Run | Model trained on | Quality |
|-----|-----------------|---------|
| 1st | Current search snippets | Baseline |
| 2nd | ~300 prior rows | Better |
| 10th | ~3000 rows across topics | Significantly better |

- Search results cached per topic — repeat runs skip the network
- Training accumulates in `~/.cache/automl-synth/training_data.jsonl`
- Topic relevance from cached search keywords, not from training data

```bash
# First run (searches web, saves cache):
automl-synth generate --topic "hotel reviews" --rows 300 --local

# Second run on different topic (uses cached training, searches web for new topic):
automl-synth generate --topic "customer feedback" --rows 200 --local

# Third run on same topic (fully offline — no network calls):
automl-synth generate --topic "hotel reviews" --rows 300 --local
```

## CLI Reference

### `generate`

```bash
automl-synth generate --topic "news" --rows 300 [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--topic, -t` | (required) | Topic for dataset generation |
| `--rows, -r` | 300 | Number of rows to generate |
| `--out, -o` | ./output | Output directory |
| `--labels, -l` | auto | Comma-separated labels (max 6) |
| `--seed, -s` | 42 | Random seed |
| `--local, -L` | false | Use local ngram model (no API key) |
| `--model, -m` | auto | LLM model ID (auto-detects provider from prefix) |
| `--interactive, -i` | false | Interactive model selection |
| `--list-models` | false | List available models and exit |
| `--no-search` | false | Skip web search |
| `--format, -f` | csv,jsonl,pdf,json | Output formats |

### `serve`

```bash
automl-synth serve --host 127.0.0.1 --port 8000
```

### `doctor`

```bash
automl-synth doctor
```

Checks Python version, package install, API key, dependencies, cache status, and output folder.

## Multi-Provider LLM Support

Auto-detected from model ID prefix:

```bash
# OpenRouter (default):
automl-synth generate --topic "reviews" --model "openrouter/free"

# Groq:
automl-synth generate --topic "reviews" --model "groq/llama3-70b-8192"

# DeepInfra:
automl-synth generate --topic "reviews" --model "meta-llama/llama-3.3-70b"

# Ollama (local):
automl-synth generate --topic "reviews" --model "llama3" --provider ollama
```

Supported providers: OpenRouter, Ollama, Groq, Cerebras, DeepInfra, Fireworks, SambaNova, NVIDIA, OpenAI, Anthropic, DeepSeek, Mistral, Google, Qwen/DashScope, and any OpenAI-compatible endpoint.

## Configuration

`.env` file or environment variables:

```env
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-...
LLM_MODEL=openrouter/free
```

Config load order: CLI args → env vars → `.env` → `~/.config/automl-synth/.env` → defaults.

## Output

| File | Description |
|------|-------------|
| `dataset.csv` | Full dataset (id, text, label, topic, source_agent, difficulty, quality_score) |
| `dataset.jsonl` | JSON Lines format |
| `dataset-card.pdf` | PDF report with overview, label distribution, quality metrics, sample rows |
| `quality-report.json` | Quality analysis (score, grade, metrics, warnings) |
| `research-report.json` | Research findings and label schema |

### Quality Grading

| Score | Grade |
|-------|-------|
| 90-100 | Excellent |
| 75-89 | Good |
| 60-74 | Fair |
| 0-59 | Needs Improvement |

Penalized for: class imbalance, duplicates, missing/short text, low vocabulary diversity, single-source rows.

## API Endpoints

When serving (`automl-synth serve`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate` | Run generation pipeline |
| `GET` | `/api/download/{run_id}/csv` | Download CSV |
| `GET` | `/api/download/{run_id}/jsonl` | Download JSONL |
| `GET` | `/api/download/{run_id}/pdf` | Download PDF |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/config/status` | Config status |

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
ruff check automl_synth/ tests/
```

## Requirements

- Python 3.11+
- Internet access for web search and LLM API calls (local mode works offline)
- LLM API key for non-local generation

## License

MIT
