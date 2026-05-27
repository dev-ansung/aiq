import httpx
import typer
from rich.table import Table
from rich.console import Console
from aiq.cli import AIQ_URL

app = typer.Typer(invoke_without_command=True)
console = Console()


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        cmd_list()


@app.command("list")
def cmd_list():
    try:
        groups = httpx.get(f"{AIQ_URL}/groups").json()
    except Exception:
        typer.echo("aiqd not running — start with 'aiq daemon start'")
        raise typer.Exit(1)
    t = Table("Name", "Parallelism", "Status")
    for g in groups:
        t.add_row(g["id"], str(g["parallelism"]), g["status"])
    console.print(t)


@app.command("add")
def cmd_add(name: str, yes: bool = typer.Option(False, "-y")):
    if not yes:
        typer.confirm(f"Add group '{name}'?", abort=True)
    r = httpx.post(f"{AIQ_URL}/groups", json={"id": name})
    r.raise_for_status()
    typer.echo(f"Group '{name}' added.")


@app.command("remove")
def cmd_remove(name: str, yes: bool = typer.Option(False, "-y")):
    if not yes:
        typer.confirm(f"Remove group '{name}'?", abort=True)
    httpx.delete(f"{AIQ_URL}/groups/{name}").raise_for_status()
    typer.echo(f"Group '{name}' removed.")


@app.command("pause")
def cmd_pause(name: str, yes: bool = typer.Option(False, "-y")):
    if not yes:
        typer.confirm(f"Pause group '{name}'?", abort=True)
    httpx.post(f"{AIQ_URL}/groups/{name}/pause").raise_for_status()
    typer.echo(f"Group '{name}' paused.")


@app.command("resume")
def cmd_resume(name: str, yes: bool = typer.Option(False, "-y")):
    if not yes:
        typer.confirm(f"Resume group '{name}'?", abort=True)
    httpx.post(f"{AIQ_URL}/groups/{name}/resume").raise_for_status()
    typer.echo(f"Group '{name}' resumed.")
