# API.md — FastAPI Endpoint Specification

## POST /api/generate

Runs the full dataset generation pipeline.

Request:

```json
{
  "topic": "Classify mobile app reviews into praise, bug_report, feature_request, usability_issue, and pricing_complaint",
  "rows": 300,
  "max_labels": 6,
  "search_enabled": true,
  "seed": 42
}
```

Response:

```json
{
  "run_id": "uuid",
  "topic": "...",
  "research_report": {},
  "quality_report": {},
  "preview_rows": [],
  "download_urls": {
    "csv": "/api/download/{run_id}/csv",
    "jsonl": "/api/download/{run_id}/jsonl",
    "pdf": "/api/download/{run_id}/pdf"
  }
}
```

## GET /api/download/{run_id}/csv

Returns generated CSV.

## GET /api/download/{run_id}/jsonl

Returns generated JSONL.

## GET /api/download/{run_id}/pdf

Returns PDF Dataset Card.

## GET /api/health

Response:

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## GET /api/config/status

Returns safe config status only.

Never return API key.

Response:

```json
{
  "provider": "openrouter",
  "model": "openrouter/free",
  "api_key_present": true,
  "search_enabled": true
}
```

## Run Storage

For semester scope, store generated run files in local temp/output directory.

No database.

Example:

```text
~/.cache/automl-synth/runs/{run_id}/
```
