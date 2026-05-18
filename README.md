# AutoML-Synth

CLI + Dashboard for generating synthetic text classification datasets using LLMs.

## Features

- **Topic-driven generation** - Enter any topic and get a labeled dataset
- **Web-assisted research** - DuckDuckGo search provides context for better synthetic data
- **Multi-provider LLM support** - OpenRouter (default), Ollama (local), or any OpenAI-compatible API
- **Automatic cleaning** - Removes duplicates, meta-language, label leakage, and short rows
- **Quality analysis** - Scored 0-100 with letter grades, balance metrics, and warnings
- **Multiple export formats** - CSV, JSONL, PDF dataset card, JSON reports
- **Dashboard** - Web UI for generation, preview, and downloads

## Quick Start

```bash
# Install
pipx install .

# Set up your API key
cp .env.example ~/.config/automl-synth/.env
# Edit with your LLM_API_KEY

# Generate a dataset
automl-synth generate --topic "movie reviews" --rows 300

# Start the dashboard
automl-synth serve
# Open http://127.0.0.1:8000
```

## CLI Commands

### Generate

```bash
automl-synth generate \
  --topic "news headlines" \
  --rows 300 \
  --out ./output \
  --labels "politics,sports,technology,entertainment" \
  --seed 42 \
  --provider openrouter \
  --model "openrouter/free" \
  --format csv,jsonl,pdf,json
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--topic, -t` | (required) | Topic for dataset generation |
| `--rows, -r` | 300 | Number of rows to generate |
| `--out, -o` | ./output | Output directory |
| `--labels, -l` | auto | Comma-separated labels (max 6) |
| `--seed, -s` | 42 | Random seed |
| `--provider, -p` | openrouter | LLM provider (openrouter, ollama, openai_compatible) |
| `--model, -m` | openrouter/free | LLM model name |
| `--no-search` | false | Disable web search |
| `--format, -f` | csv,jsonl,pdf,json | Output formats |

### Serve

```bash
automl-synth serve --host 127.0.0.1 --port 8000
```

### Doctor

```bash
automl-synth doctor
```

Checks Python version, package install, LLM config, search import, PDF export, output folder permissions, and dashboard files.

## Configuration

Create a `.env` file or set environment variables:

```env
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your-key-here
LLM_MODEL=openrouter/free
```

**Config load order:** CLI args -> env vars -> project `.env` -> `~/.config/automl-synth/.env` -> defaults

### Provider Examples

**OpenRouter (default):**
```env
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-...
LLM_MODEL=openrouter/free
```

**Ollama (local, no API key needed):**
```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3
```

**OpenAI-compatible:**
```env
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

## Output Files

| File | Description |
|------|-------------|
| `dataset.csv` | Full dataset with all columns |
| `dataset.jsonl` | JSON Lines format |
| `dataset-card.pdf` | PDF report with overview, label distribution, quality metrics, and samples |
| `quality-report.json` | Detailed quality analysis |
| `research-report.json` | Research findings and label schema |

### Dataset Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Row identifier |
| `text` | str | Generated text content |
| `label` | str | Classification label |
| `topic` | str | Original topic |
| `source_agent` | str | Which agent generated the row |
| `difficulty` | str | easy, medium, or hard |
| `synthetic_quality_score` | float | Per-row quality estimate (0-1) |

## Quality Scores

Scores start at 100 and are penalized for:

| Issue | Penalty |
|-------|---------|
| Class imbalance (ratio < 0.5) | -15 |
| Duplicate rows | up to -20 |
| Missing text | -15 |
| Short text (< 20 chars) | -10 |
| Low vocabulary diversity | -10 |
| Meta-language detected | -20 |
| Label leakage detected | -20 |
| Single source agent | -8 |

**Grades:** 90-100 Excellent, 75-89 Good, 60-74 Fair, 0-59 Needs Improvement

## API

When running `automl-synth serve`, the following endpoints are available:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/generate` | Run generation pipeline |
| `GET` | `/api/download/{run_id}/csv` | Download CSV |
| `GET` | `/api/download/{run_id}/jsonl` | Download JSONL |
| `GET` | `/api/download/{run_id}/pdf` | Download PDF |
| `GET` | `/api/health` | Server status |
| `GET` | `/api/config/status` | Config status (no API keys) |

## Development

```bash
# Create venv
python3 -m venv .venv && source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check automl_synth/ tests/
```

## Requirements

- Python 3.11+
- Internet access (for LLM API and web search)
- LLM API key (OpenRouter, or Ollama for local)

## License

MIT
