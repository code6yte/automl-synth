"""FastAPI server with API endpoints and dashboard."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from automl_synth import __version__
from automl_synth.config import load_config, validate_config
from automl_synth.providers.factory import create_provider

app = FastAPI(title="AutoML-Synth", version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_runs: dict[str, dict] = {}


class GenerateRequest(BaseModel):
    topic: str
    rows: int = 300
    labels: list[str] | None = None
    seed: int = 42
    provider: str | None = None
    model: str | None = None
    no_search: bool = False


@app.post("/api/generate")
async def api_generate(req: GenerateRequest):
    cfg = load_config(provider=req.provider, model=req.model)
    errors = validate_config(cfg)
    if errors:
        raise HTTPException(status_code=400, detail=errors)

    provider = create_provider(
        provider_type=cfg["provider"],
        api_key=cfg["api_key"],
        model=cfg["model"],
        base_url=cfg["base_url"],
    )

    from automl_synth.orchestrator import run_pipeline

    result = await run_pipeline(
        provider=provider,
        topic=req.topic,
        num_rows=req.rows,
        labels=req.labels,
        seed=req.seed,
        output_dir=f"./output/{req.topic.replace(' ', '_')}",
        search_enabled=not req.no_search,
        max_search_results=cfg["max_search_results"],
    )

    _runs[result.run_id] = {
        "topic": result.topic,
        "rows": result.quality_report.total_rows,
        "quality_score": result.quality_report.quality_score,
        "quality_grade": result.quality_report.quality_grade,
        "files": result.files,
        "output_dir": result.output_dir,
    }

    return {
        "run_id": result.run_id,
        "topic": result.topic,
        "rows": result.quality_report.total_rows,
        "quality_score": result.quality_report.quality_score,
        "quality_grade": result.quality_report.quality_grade,
        "files": result.files,
    }


@app.get("/api/download/{run_id}/csv")
async def download_csv(run_id: str):
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    csv_path = run["files"].get("csv")
    if not csv_path or not Path(csv_path).exists():
        raise HTTPException(status_code=404, detail="CSV file not found")
    return FileResponse(csv_path, media_type="text/csv", filename="dataset.csv")


@app.get("/api/download/{run_id}/jsonl")
async def download_jsonl(run_id: str):
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    jsonl_path = run["files"].get("jsonl")
    if not jsonl_path or not Path(jsonl_path).exists():
        raise HTTPException(status_code=404, detail="JSONL file not found")
    return FileResponse(jsonl_path, media_type="application/x-ndjson", filename="dataset.jsonl")


@app.get("/api/download/{run_id}/pdf")
async def download_pdf(run_id: str):
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    pdf_path = run["files"].get("pdf")
    if not pdf_path or not Path(pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="dataset-card.pdf")


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": __version__}


@app.get("/api/config/status")
async def config_status():
    cfg = load_config()
    return {
        "provider": cfg["provider"],
        "model": cfg["model"],
        "base_url": cfg["base_url"],
        "has_api_key": bool(cfg["api_key"]),
        "search_enabled": cfg["search_enabled"],
    }


_dashboard_dir = Path(__file__).parent.parent / "dashboard" / "dist"
if _dashboard_dir.exists() and (_dashboard_dir / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(_dashboard_dir), html=True), name="dashboard")
else:
    @app.get("/")
    async def root():
        return {
            "message": "AutoML-Synth API",
            "version": __version__,
            "docs": "/docs",
            "health": "/api/health",
        }
