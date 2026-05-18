# CONFIG.md — Configuration Specification

## Config Sources

Load config in this order:

1. CLI arguments.
2. Environment variables.
3. Project `.env` file.
4. User config file at `~/.config/automl-synth/.env`.
5. Defaults.

## Required Environment Variables

For OpenRouter:

```env
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=your_openrouter_key
LLM_MODEL=openrouter/free
```

For Ollama/custom local provider:

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://127.0.0.1:11434
LLM_API_KEY=
LLM_MODEL=llama3.2:1b
```

For any OpenAI-compatible provider:

```env
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://your-provider.example/v1
LLM_API_KEY=your_key
LLM_MODEL=provider_model_name
```

## Other Config

```env
AUTOML_SYNTH_DEFAULT_ROWS=300
AUTOML_SYNTH_SEARCH_ENABLED=true
AUTOML_SYNTH_MAX_SEARCH_RESULTS=3
AUTOML_SYNTH_OUTPUT_DIR=./output
AUTOML_SYNTH_LOG_LEVEL=info
```

## Provider Behavior

### OpenRouter
Call:

```text
{LLM_BASE_URL}/chat/completions
```

Headers:

```text
Authorization: Bearer <LLM_API_KEY>
Content-Type: application/json
```

### Ollama
Call:

```text
{LLM_BASE_URL}/api/generate
```

No API key required unless custom deployment requires it.

## Frontend Config

Frontend must not store provider API keys.

Dashboard sends requests only to FastAPI:

```text
POST /api/generate
```

FastAPI reads `.env` and calls LLM provider.

## Config Validation

`doctor` should show:

```text
Provider: openrouter
Base URL: configured
API Key: found / missing
Model: configured
LLM Reachable: yes / no
Search Package: yes / no
PDF Export: yes / no
```
