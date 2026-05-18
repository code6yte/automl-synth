# TASKS.md — Build Checklist for Coding Agent

## Phase 1 — Package Skeleton

- [ ] Create `pyproject.toml`.
- [ ] Create `automl_synth/` package.
- [ ] Add `cli.py` with Typer app.
- [ ] Add `config.py`.
- [ ] Add `types.py`.
- [ ] Add `README.md`.
- [ ] Add `.env.example`.

## Phase 2 — Provider Layer

- [ ] Implement `providers/base.py`.
- [ ] Implement `providers/openrouter.py`.
- [ ] Implement `providers/ollama.py`.
- [ ] Implement `providers/openai_compatible.py`.
- [ ] Add provider factory.
- [ ] Add provider reachability check for doctor.

## Phase 3 — Search

- [ ] Implement `search/web_search.py`.
- [ ] Use ddgs or DuckDuckGo-compatible package.
- [ ] Fail gracefully if search fails.

## Phase 4 — Agents

- [ ] Implement Research Agent.
- [ ] Implement Generator Agent.
- [ ] Implement Cleaning Agent.
- [ ] Implement Quality Agent.
- [ ] Implement Report Agent.
- [ ] Implement Orchestrator.

## Phase 5 — Exporters

- [ ] CSV exporter.
- [ ] JSONL exporter.
- [ ] PDF Dataset Card exporter.
- [ ] JSON research/quality report export.

## Phase 6 — CLI

- [ ] `automl-synth generate`.
- [ ] `automl-synth serve`.
- [ ] `automl-synth doctor`.

## Phase 7 — API

- [ ] FastAPI app.
- [ ] `POST /api/generate`.
- [ ] download endpoints.
- [ ] health endpoint.
- [ ] static dashboard mount.

## Phase 8 — Dashboard

- [ ] React + Vite app.
- [ ] Topic input page.
- [ ] Agent progress timeline.
- [ ] Label summary.
- [ ] Dataset preview.
- [ ] Quality dashboard.
- [ ] Download panel.
- [ ] Build to static dist.

## Phase 9 — Installer

- [ ] Add `install.sh`.
- [ ] Add pipx install instructions.
- [ ] Ensure runtime dependencies install.
- [ ] Ensure `doctor` verifies setup.

## Phase 10 — Final Testing

Test topics:

- [ ] news headline classification
- [ ] mobile app review classification
- [ ] customer support ticket classification
- [ ] restaurant delivery complaint classification
- [ ] toxic YouTube comment classification

Acceptance:

- [ ] Generated rows match topic format.
- [ ] CSV exports correctly.
- [ ] JSONL exports correctly.
- [ ] PDF exports correctly.
- [ ] Quality report shows useful metrics.
- [ ] Dashboard loads.
- [ ] CLI works without dashboard.
