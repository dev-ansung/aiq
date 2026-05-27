import subprocess
import sys
import httpx
import typer
from aiq.cli import AIQ_URL

app = typer.Typer(invoke_without_command=True)


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        cmd_status()


@app.command("start")
def cmd_start():
    subprocess.Popen(
        [sys.executable, "-m", "aiq.daemon.app"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    typer.echo("aiqd started.")


@app.command("stop")
def cmd_stop():
    try:
        httpx.post(f"{AIQ_URL}/_shutdown", timeout=3)
        typer.echo("aiqd stopped.")
    except Exception:
        typer.echo("aiqd not running.")


@app.command("status")
def cmd_status():
    try:
        r = httpx.get(f"{AIQ_URL}/health", timeout=3)
        typer.echo("aiqd running." if r.status_code == 200 else "aiqd not healthy.")
    except Exception:
        typer.echo("aiqd not running.")
