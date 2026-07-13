from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_agent_service
from app.models.schemas import AgentChatRequest, ExplainDemandRequest, RecommendSupportRequest
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat")
def chat(request: AgentChatRequest, service: AgentService = Depends(get_agent_service)):
    return service.chat(request.message, request.version_id, request.context)


@router.post("/recommend-support")
def recommend_support(request: RecommendSupportRequest, service: AgentService = Depends(get_agent_service)):
    candidates = service.recommend_support(
        request.version_id,
        request.date,
        request.slot,
        request.area_code,
        request.task_code,
    )
    if not candidates:
        return {"candidates": [], "message": "未找到可用候选人，建议放宽时段或检查临时工技能。"}
    return {"candidates": candidates}


@router.post("/explain-demand")
def explain_demand(request: ExplainDemandRequest, service: AgentService = Depends(get_agent_service)):
    response = service.explain_demand(request.version_id, request.date, request.slot, request.area_code)
    if response["message"].startswith("暂未找到"):
        raise HTTPException(status_code=404, detail={"error_code": "DEMAND_NOT_FOUND", "message": response["message"]})
    return response

