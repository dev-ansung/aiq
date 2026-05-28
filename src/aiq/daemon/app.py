from contextlib import asynccontextmanager
import asyncio
import uvicorn
from fastapi import FastAPI
from aiq.daemon.routes import groups, models, agents, tasks
from aiq.daemon.scheduler import run_scheduler_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    from aiq.state.store import Store
    store = Store()
    state = store.load_state()
    if "default" not in state["groups"]:
        state["groups"]["default"] = {"id": "default", "parallelism": 1, "status": "running"}
        store.save_state(state)
    asyncio.create_task(run_scheduler_loop())
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="aiqd", lifespan=lifespan)
    app.include_router(groups.router)
    app.include_router(models.router)
    app.include_router(agents.router)
    app.include_router(tasks.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/_shutdown")
    def shutdown():
        import os, signal
        os.kill(os.getpid(), signal.SIGTERM)
        return {"status": "shutting down"}

    return app


def main():
    uvicorn.run("aiq.daemon.app:create_app", host="127.0.0.1", port=7777, factory=True)


if __name__ == "__main__":
    main()
