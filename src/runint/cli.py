import typer
import json
import os
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from runint.benchmarks.registry import list_benchmarks, get_benchmark_class
from runint.runtime.manager import RuntimeManager
from runint.schemas.config import RunConfig

# Initialize Typer app and Rich console
app = typer.Typer(help="RunInt: AI Runtime & Benchmark Intelligence CLI")
console = Console()

@app.command()
def info():
    """
    Displays information about available benchmarks and capabilities.
    """
    console.print(Panel.fit("[bold cyan]RunInt Library v0.1.0[/bold cyan]", border_style="cyan"))
    
    # List Benchmarks
    benchmarks = list_benchmarks()
    if benchmarks:
        table = Table(title="Available Benchmarks")
        table.add_column("Name", style="green")
        table.add_column("Type", style="magenta")
        table.add_column("Description")
        
        for name, meta in benchmarks.items():
            table.add_row(name, meta.get("task_type", "N/A"), meta.get("description", ""))
        
        console.print(table)
    else:
        console.print("[yellow]No benchmarks registered. (Check your imports)[/yellow]")

@app.command()
def deploy(
    config_path: str = typer.Option(..., "--config", "-c", help="Path to the JSON run configuration file"),
    dry_run: bool = typer.Option(False, help="Generate deployment files without starting them")
):
    """
    [Run Intelligence] Deploys an AI environment based on a configuration file.
    """
    if not os.path.exists(config_path):
        console.print(f"[bold red]Error:[/bold red] Config file '{config_path}' not found.")
        raise typer.Exit(code=1)

    console.print(f"[bold blue]Loading configuration from {config_path}...[/bold blue]")
    
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
            # Parse into Pydantic model for validation
            run_config = RunConfig(**data)
            
        manager = RuntimeManager(run_config)
        
        # 1. Generate Infrastructure (e.g., Docker Compose)
        output_file = "docker-compose.yml"
        manager.generate_deployment(output_path=output_file)
        console.print(f"[green]✔ Deployment file generated at: {output_file}[/green]")
        
        # 2. Execute (unless dry run)
        if not dry_run:
            console.print("[yellow]Starting environment...[/yellow]")
            # In a real scenario, this might call 'docker-compose up -d'
            manager.start_environment()
            console.print("[bold green]✔ Environment is up and running![/bold green]")
            
    except Exception as e:
        console.print(f"[bold red]Deployment failed:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def benchmark(
    task: str = typer.Option(..., help="Name of