from fastapi import APIRouter, HTTPException
from aiq.models.schema import Model
from aiq.state.store import Store

router = APIRouter()


def _store() -> Store:
    return Store()


@router.get("/models")
def list_models():
    config = _store().load_config()
    return list(config["models"].values())


@router.post("/models")
def add_model(model: Model):
    store = _store()
    config = store.load_config()
    config["models"][model.id] = model.model_dump()
    store.save_config(config)
    return model


@router.delete("/models/{model_id}")
def remove_model(model_id: str):
    store = _store()
    config = store.load_config()
    if model_id not in config["models"]:
        raise HTTPException(status_code=404, detail="Model not found")
    del config["models"][model_id]
    store.save_config(config)
    return {"ok": True}
