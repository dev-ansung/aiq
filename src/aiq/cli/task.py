import typer

app = typer.Typer(invoke_without_command=True)


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        cmd_status()


def cmd_status():
    typer.echo("Run 'aiq daemon start' first, then 'aiq task' to see task status.")
