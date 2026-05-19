"""CLI entry point for AutoML-Synth."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from automl_synth.config import load_config, validate_config
from automl_synth.providers.factory import create_provider

console = Console()
app = typer.Typer(
    name="automl-synth",
    help="CLI + Dashboard for Synthetic Text Classification Dataset Generation",
    add_completion=False,
)


@app.command()
def models(
    provider: str = typer.Option(None, "--provider", "-p", help="LLM provider"),
):
    """List available models from the configured provider."""
    cfg = load_config(provider=provider)
    provider_instance = create_provider(
        provider_type=cfg["provider"],
        api_key=cfg["api_key"],
        model=cfg["model"],
        base_url=cfg["base_url"],
    )

    console.print(f"[bold]Fetching models from {cfg['provider']}...[/bold]")

    async def _fetch():
        return await provider_instance.list_models()

    try:
        model_list = asyncio.run(_fetch())
    except Exception as e:
        console.print(f"[red]Failed to fetch models:[/red] {e}")
        raise typer.Exit(code=2)

    if not model_list:
        console.print("[yellow]No models found or provider does not support listing.[/yellow]")
        raise typer.Exit(code=0)

    table = Table(title=f"Available Models ({cfg['provider']})")
    table.add_column("#", style="dim")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Context", style="dim")

    for i, m in enumerate(model_list, 1):
        table.add_row(
            str(i),
            m["id"],
            m["name"],
            str(m.get("context_length", "N/A")),
        )

    console.print(table)
    console.print("\n[dim]Use --model <id> to select a model[/dim]")


@app.command()
def generate(
    topic: str = typer.Option(..., "--topic", "-t", help="Topic for dataset generation"),
    rows: int = typer.Option(300, "--rows", "-r", help="Number of rows to generate"),
    out: str = typer.Option("./output", "--out", "-o", help="Output directory"),
    labels: str = typer.Option(None, "--labels", "-l", help="Comma-separated labels (max 6)"),
    seed: int = typer.Option(42, "--seed", "-s", help="Random seed"),
    provider: str = typer.Option(None, "--provider", "-p", help="LLM provider"),
    model: str = typer.Option(None, "--model", "-m", help="LLM model"),
    list_models: bool = typer.Option(False, "--list-models", help="List available models and exit"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive model selection"),
    no_search: bool = typer.Option(False, "--no-search", help="Disable web search"),
    format: str = typer.Option("csv,jsonl,pdf,json", "--format", "-f", help="Output formats"),
):
    """Generate a synthetic text classification dataset."""
    cfg = load_config(provider=provider, model=model)

    errors = validate_config(cfg)
    if errors:
        for e in errors:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)

    provider_instance = create_provider(
        provider_type=cfg["provider"],
        api_key=cfg["api_key"],
        model=cfg["model"],
        base_url=cfg["base_url"],
    )

    if list_models:
        console.print(f"[bold]Fetching models from {cfg['provider']}...[/bold]")

        async def _fetch():
            return await provider_instance.list_models()

        try:
            model_list = asyncio.run(_fetch())
        except Exception as e:
            console.print(f"[red]Failed to fetch models:[/red] {e}")
            raise typer.Exit(code=2)

        if not model_list:
            console.print("[yellow]No models found.[/yellow]")
            raise typer.Exit(code=0)

        table = Table(title=f"Available Models ({cfg['provider']})")
        table.add_column("#", style="dim")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Context", style="dim")

        for i, m in enumerate(model_list, 1):
            table.add_row(
                str(i),
                m["id"],
                m["name"],
                str(m.get("context_length", "N/A")),
            )

        console.print(table)
        raise typer.Exit(code=0)

    if interactive:
        console.print(f"[bold]Fetching available models from {cfg['provider']}...[/bold]")

        async def _fetch():
            return await provider_instance.list_models()

        try:
            model_list = asyncio.run(_fetch())
        except Exception as e:
            console.print(f"[red]Failed to fetch models:[/red] {e}")
            raise typer.Exit(code=2)

        if model_list:
            table = Table(title="Select a model")
            table.add_column("#", style="dim")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")

            for i, m in enumerate(model_list, 1):
                table.add_row(str(i), m["id"], m["name"])

            console.print(table)

            choice = console.input(f"\nSelect model (1-{len(model_list)}, or press Enter for default): ").strip()
            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(model_list):
                    cfg["model"] = model_list[idx]["id"]
                    provider_instance = create_provider(
                        provider_type=cfg["provider"],
                        api_key=cfg["api_key"],
                        model=cfg["model"],
                        base_url=cfg["base_url"],
                    )
                    console.print(f"[green]Selected: {model_list[idx]['id']}[/green]\n")

    label_list = [lbl.strip() for lbl in labels.split(",")] if labels else None
    if label_list and len(label_list) > 6:
        console.print("[red]Error:[/red] Maximum 6 labels allowed")
        raise typer.Exit(code=1)

    formats = [f.strip() for f in format.split(",")]

    async def _run():
        from automl_synth.orchestrator import run_pipeline

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Starting generation...", total=None)
            result = await run_pipeline(
                provider=provider_instance,
                topic=topic,
                num_rows=rows,
                labels=label_list,
                seed=seed,
                output_dir=out,
                search_enabled=not no_search,
                max_search_results=cfg["max_search_results"],
                formats=formats,
            )
            return result

    try:
        result = asyncio.run(_run())
    except Exception as e:
        console.print(f"[red]Generation failed:[/red] {e}")
        raise typer.Exit(code=3)

    console.print(Panel(
        f"[green]Dataset generated successfully![/green]\n\n"
        f"Topic: {result.topic}\n"
        f"Model: {cfg['model']}\n"
        f"Rows: {result.quality_report.total_rows}\n"
        f"Quality: {result.quality_report.quality_score}/100 ({result.quality_report.quality_grade})\n"
        f"Output: {result.output_dir}\n\n"
        f"Files:\n" + "\n".join(f"  - {k}: {v}" for k, v in result.files.items()),
        title="AutoML-Synth",
    ))


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload"),
):
    """Start the FastAPI dashboard server."""
    import uvicorn

    console.print(f"[green]Starting dashboard at http://{host}:{port}[/green]")
    uvicorn.run(
        "automl_synth.api.server:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command()
def doctor():
    """Check system configuration and dependencies."""
    console.print(Panel("AutoML-Synth Doctor", style="bold blue"))
    issues = 0

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    ok = sys.version_info >= (3, 11)
    console.print(f"  Python {python_version} {'[green]OK[/green]' if ok else '[red]FAIL (need 3.11+)[/red]'}")
    if not ok:
        issues += 1

    try:
        import automl_synth
        console.print(f"  Package installed [green]OK[/green] (v{automl_synth.__version__})")
    except ImportError:
        console.print("  Package installed [red]FAIL[/red]")
        issues += 1

    cfg = load_config()
    provider_ok = bool(cfg["api_key"]) or cfg["provider"] == "ollama"
    console.print(f"  LLM config ({cfg['provider']}) {'[green]OK[/green]' if provider_ok else '[yellow]No API key set[/yellow]'}")

    try:
        import ddgs  # noqa: F401
        console.print("  Web search (ddgs) [green]OK[/green]")
    except ImportError:
        console.print("  Web search (ddgs) [yellow]Not installed[/yellow]")

    try:
        import reportlab  # noqa: F401
        console.print("  PDF export (reportlab) [green]OK[/green]")
    except ImportError:
        console.print("  PDF export (reportlab) [red]FAIL[/red]")
        issues += 1

    out_path = Path("./output")
    try:
        out_path.mkdir(parents=True, exist_ok=True)
        console.print("  Output folder [green]OK[/green]")
    except PermissionError:
        console.print("  Output folder [red]Permission denied[/red]")
        issues += 1

    dashboard_path = Path(__file__).parent / "dashboard" / "dist" / "index.html"
    if dashboard_path.exists():
        console.print("  Dashboard files [green]OK[/green]")
    else:
        console.print("  Dashboard files [yellow]Not built (optional)[/yellow]")

    if issues == 0:
        console.print("\n[green]All checks passed![/green]")
    else:
        console.print(f"\n[yellow]{issues} issue(s) found[/yellow]")

    raise typer.Exit(code=0)


def main():
    app()


if __name__ == "__main__":
    main()
