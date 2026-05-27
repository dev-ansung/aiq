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
    models = httpx.get(f"{AIQ_URL}/models").json()
    t = Table("Id", "Endpoint", "Model Id")
    for m in models:
        t.add_row(m["id"], m["endpoint_url"], m["model_id"])
    console.print(t)


@app.command("add")
def cmd_add(
    id: str,
    endpoint: str = typer.Option(..., "--endpoint"),
    api_key: str = typer.Option(..., "--api-key"),
    model_id: str = typer.Option(..., "--model-id"),
    yes: bool = typer.Option(False, "-y"),
):
    if not yes:
        typer.confirm(f"Add model '{id}'?", abort=True)
    r = httpx.post(f"{AIQ_URL}/models", json={"id": id, "endpoint_url": endpoint, "api_key": api_key, "model_id": model_id})
    r.raise_for_status()
    typer.echo(f"Model '{id}' added.")


@app.command("remove")
def cmd_remove(id: str, yes: bool = typer.Option(False, "-y")):
    if not yes:
        typer.confirm(f"Remove model '{id}'?", abort=True)
    httpx.delete(f"{AIQ_URL}/models/{id}").raise_for_status()
    typer.echo(f"Model '{id}' removed.")
