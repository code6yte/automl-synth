# CLI.md — CLI Specification

Use Typer.

## Command: generate

```bash
automl-synth generate \
  --topic "Classify news headlines into politics, sports, technology, entertainment, and business" \
  --rows 300 \
  --out ./output
```

Options:

```text
--topic TEXT       Required. User topic.
--rows INTEGER    Default 300.
--out PATH        Default ./output.
--labels INTEGER  Max labels, default 6.
--seed INTEGER    Default 42.
--provider TEXT   Optional override: openrouter, ollama, openai_compatible.
--model TEXT      Optional model override.
--no-search       Disable web search.
--format TEXT     csv,jsonl,pdf. Default all.
```

Output files:

```text
output/dataset.csv
output/dataset.jsonl
output/dataset-card.pdf
output/quality-report.json
output/research-report.json
```

Terminal output should show:

```text
✓ Research complete
✓ Dataset generated
✓ Dataset cleaned
✓ Quality analysis complete
✓ Exports written
Quality Score: 86/100 Good
Output: ./output
```

## Command: serve

```bash
automl-synth serve --host 127.0.0.1 --port 8000
```

Options:

```text
--host TEXT
--port INTEGER
--reload BOOLEAN
```

Starts FastAPI and serves dashboard.

## Command: doctor

```bash
automl-synth doctor
```

Checks:

- Python version
- package install
- config
- LLM provider
- web search package
- PDF export
- output write permissions
- dashboard static files

## CLI Exit Codes

```text
0 = success
1 = config error
2 = provider error
3 = generation error
4 = export error
```
