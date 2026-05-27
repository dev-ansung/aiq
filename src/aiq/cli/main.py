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


@app.command("status")
def cmd_status_alias():
    task.cmd_status()


@app.command("list")
def cmd_list_alias():
    task.cmd_status()


# Expose task commands at top level for convenience
app.command("add")(task.cmd_add)
app.command("remove")(task.cmd_remove)
app.command("cancel")(task.cmd_cancel)
app.command("restart")(task.cmd_restart)
app.command("log")(task.cmd_log)
app.command("follow")(task.cmd_follow)
app.command("script")(task.cmd_script)
