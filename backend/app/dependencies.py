from functools import lru_cache

from app.data.store import SQLiteStore
from app.services.agent_service import AgentService
from app.services.demand_service import DemandService
from app.services.hc_service import HcService
from app.services.schedule_service import ScheduleService


@lru_cache
def get_store() -> SQLiteStore:
    return SQLiteStore()


@lru_cache
def get_demand_service() -> DemandService:
    return DemandService()


@lru_cache
def get_schedule_service() -> ScheduleService:
    return ScheduleService(store=get_store(), demand_service=get_demand_service())


@lru_cache
def get_agent_service() -> AgentService:
    return AgentService(store=get_store())


@lru_cache
def get_hc_service() -> HcService:
    return HcService(store=get_store())

