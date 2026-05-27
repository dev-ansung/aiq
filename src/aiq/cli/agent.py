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
        agents = httpx.get(f"{AIQ_URL}/agents").json()
    except Exception:
        typer.echo("aiqd not running — start with 'aiq daemon start'")
        raise typer.Exit(1)
    t = Table("Id", "Model", "System Prompt")
    for a in agents:
        sp = a["system_prompt"]
        t.add_row(a["id"], a["model"], sp[:57] + "…" if len(sp) > 60 else sp)
    console.print(t)


@app.command("add")
def cmd_add(
    id: str,
    model: str = typer.Option(..., "--model"),
    system_prompt: str = typer.Option(..., "--system-prompt"),
    yes: bool = typer.Option(False, "-y"),
):
    if not yes:
        typer.confirm(f"Add agent '{id}'?", abort=True)
    r = httpx.post(f"{AIQ_URL}/agents", json={"id": id, "model": model, "system_prompt": system_prompt})
    r.raise_for_status()
    typer.echo(f"Agent '{id}' added.")


@app.command("remove")
def cmd_remove(id: str, yes: bool = typer.Option(False, "-y")):
    if not yes:
        typer.confirm(f"Remove agent '{id}'?", abort=True)
    httpx.delete(f"{AIQ_URL}/agents/{id}").raise_for_status()
    typer.echo(f"Agent '{id}' removed.")
