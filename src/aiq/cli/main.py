import typer
from aiq.cli import daemon, group, model, agent, task

app = typer.Typer(invoke_without_command=True)
app.add_typer(daemon.app, name="daemon")
app.add_typer(group.app, name="group")
app.add_typer(model.app, name="model")
app.add_typer(agent.app, name="agent")
app.add_typer(task.app, name="task")


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        task.cmd_status()
