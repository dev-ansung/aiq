from fastapi import FastAPI
from aiq.daemon.routes import groups, models, agents, tasks


def create_app() -> FastAPI:
    app = FastAPI(title="aiqd")
    app.include_router(groups.router)
    app.include_router(models.router)
    app.include_router(agents.router)
    app.include_router(tasks.router)
    return app


def main():
    import uvicorn
    uvicorn.run("aiq.daemon.app:create_app", host="127.0.0.1", port=7777, factory=True)
