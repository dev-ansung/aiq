import httpx
import typer
from rich.table import Table
from rich.console import Console

app = typer.Typer(invoke_without_command=True)
AIQ_URL = "http://127.0.0.1:7777"
console = Console()


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        cmd_list()


@app.command("list")
def cmd_list():
    agents = httpx.get(f"{AIQ_URL}/agents").json()
    t = Table("Id", "Model", "System Prompt")
    for a in agents:
        t.add_row(a["id"], a["model"], a["system_prompt"][:60])
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
