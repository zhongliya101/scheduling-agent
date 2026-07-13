from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_hc_service
from app.models.schemas import ConfirmHcSuggestionRequest
from app.services.hc_service import HcService

router = APIRouter(prefix="/hc", tags=["hc"])


@router.post("/optimize")
def optimize(payload: dict[str, str], service: HcService = Depends(get_hc_service)):
    version_id = payload.get("version_id", "")
    suggestions = service.optimize(version_id)
    if not suggestions:
        raise HTTPException(status_code=404, detail={"error_code": "VERSION_NOT_FOUND"})
    return {"suggestions": suggestions}


@router.get("/suggestions")
def suggestions(service: HcService = Depends(get_hc_service)):
    return service.suggestions()


@router.post("/suggestions/confirm")
def confirm(request: ConfirmHcSuggestionRequest, service: HcService = Depends(get_hc_service)):
    row = service.confirm(request.suggestion_id, request.status)
    if not row:
        raise HTTPException(status_code=404, detail={"error_code": "SUGGESTION_NOT_FOUND"})
    return row

