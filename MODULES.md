# MODULES.md — Module Contracts

## automl_synth/config.py

Responsibilities:

- Load `.env` and environment variables.
- Validate provider config.
- Expose settings object.

Expected settings:

```python
class Settings:
    llm_provider: str
    llm_base_url: str
    llm_api_key: str | None
    llm_model: str
    search_enabled: bool
    default_rows: int
```

## automl_synth/providers/base.py

Define provider interface:

```python
class LLMProvider:
    def complete_text(self, prompt: str, temperature: float = 0.2) -> str: ...
    def complete_json(self, prompt: str, temperature: float = 0.2) -> dict: ...
```

## automl_synth/providers/openrouter.py

Responsibilities:

- Call OpenRouter chat completions endpoint.
- Send bearer token.
- Parse response.
- Return text or JSON.

Never expose API key to frontend.

## automl_synth/providers/ollama.py

Responsibilities:

- Call local/custom Ollama-compatible endpoint.
- No API key required by default.
- Fail gracefully if unavailable.

## automl_synth/search/web_search.py

Function:

```python
def search_web(query: str, max_results: int = 3) -> list[SearchResult]:
    ...
```

Return:

```python
class SearchResult:
    title: str
    url: str
    snippet: str
```

Search must not block the entire run. If it fails, return empty list.

## automl_synth/agents/research_agent.py

Input:

```python
ResearchInput(topic: str, max_labels: int)
```

Output:

```python
ResearchReport(
    topic: str,
    task_type: str,
    labels: list[str],
    label_profiles: dict[str, LabelProfile],
    web_sources: list[SearchResult],
    research_mode: str,
)
```

Rules:

- Use web search when enabled.
- Use LLM to infer labels and examples.
- Do not default to sentiment unless topic is sentiment.
- Require at least two labels.
- If LLM fails, use topic-parsing fallback.

## automl_synth/agents/generator_agent.py

Input:

```python
GenerateInput(research_report, rows, seed)
```

Output:

```python
pd.DataFrame
```

Required columns:

```text
id
text
label
topic
source_agent
difficulty
synthetic_quality_score
```

Rules:

- Use LLM-generated examples when available.
- Use domain-aware fallback only when needed.
- News topics must generate headlines.
- Review topics must generate reviews.
- Comments topics must generate comments.
- Support topics must generate support tickets.
- Do not leak label names.
- Cap repeated fragments.
- Avoid meta-language.

## automl_synth/agents/cleaning_agent.py

Input: dataframe.

Output: cleaned dataframe.

Remove:

- null text/label
- short rows
- duplicates
- meta-language rows
- label leakage rows if severe
- repeated fragments over threshold

## automl_synth/agents/quality_agent.py

Input: cleaned dataframe.

Output:

```python
QualityReport(
    quality_score: int,
    quality_grade: str,
    warnings: list[str],
    metrics: dict,
)
```

Metrics:

- total rows
- number of labels
- label distribution
- class balance ratio
- duplicate rows
- missing values
- average word count
- unique text ratio
- meta-language rows
- label leakage rows
- repeated fragment groups
- max fragment reuse
- source-agent distribution
- difficulty distribution

## automl_synth/exporters/csv_exporter.py

Write dataframe to:

```text
dataset.csv
```

## automl_synth/exporters/jsonl_exporter.py

Write each row as:

```json
{"text": "...", "label": "..."}
```

## automl_synth/exporters/pdf_exporter.py

Create Dataset Card PDF:

- title
- topic
- task type
- label summary
- dataset stats
- quality score
- warnings
- sample rows by label
- limitations
- recommended use

## automl_synth/orchestrator.py

Single pipeline entry point:

```python
def run_pipeline(topic: str, rows: int, output_dir: Path, settings: Settings) -> PipelineResult:
    ...
```

Pipeline:

```text
research → generate → clean → quality → export
```

## automl_synth/api/server.py

FastAPI app.

Endpoints:

- `POST /api/generate`
- `GET /api/download/{run_id}/csv`
- `GET /api/download/{run_id}/jsonl`
- `GET /api/download/{run_id}/pdf`
- `GET /api/health`

Serve dashboard static files from bundled React build.

## automl_synth/cli.py

Typer app commands:

- `generate`
- `serve`
- `doctor`
