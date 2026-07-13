from fastapi import APIRouter, Depends

from app.dependencies import get_demand_service, get_store
from app.services.demand_service import DemandService
from app.data.store import SQLiteStore

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/reset")
def reset_demo(store: SQLiteStore = Depends(get_store)):
    store.reset()
    return {"ok": True, "message": "Demo 数据已重置"}


@router.get("/source-data")
def source_data(service: DemandService = Depends(get_demand_service)):
    return service.source_summary()

