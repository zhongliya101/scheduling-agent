from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.config import get_settings
from app.data.store import SQLiteStore
from app.engine.scheduling import SchedulingGenerator
from app.models.schemas import (
    GenerateScheduleRequest,
    ModifyScheduleRequest,
    ModifyScheduleResponse,
    ScheduleResponse,
)
from app.services.demand_service import DemandService


class ScheduleService:
    def __init__(
        self,
        store: SQLiteStore | None = None,
        demand_service: DemandService | None = None,
        generator: SchedulingGenerator | None = None,
    ) -> None:
        self.settings = get_settings()
        self.store = store or SQLiteStore()
        self.demand_service = demand_service or DemandService()
        self.generator = generator or SchedulingGenerator()

    def generate(self, request: GenerateScheduleRequest) -> ScheduleResponse:
        self._validate_generation_request(request)
        demand_results, insights = self.demand_service.calculate_week(request.week_start)
        payload = self.generator.generate(request.week_start, demand_results)
        payload["demand_insights"] = insights
        self.store.save_version(payload)
        return ScheduleResponse(**payload)

    def get(self, version_id: str) -> ScheduleResponse | None:
        version = self.store.get_version(version_id)
        if not version:
            return None
        kpis = self.generator.calculate_kpis(
            version["demand_results"],
            version["schedule_items"],
            version["risks"],
            version["intervention_count"],
        ).model_dump()
        insights = sorted(
            [
                {key: row[key] for key in [
                    "date",
                    "weekday",
                    "slot",
                    "area_code",
                    "area_name",
                    "required_count",
                    "demand_score",
                    "demand_factors",
                    "priority",
                    "confidence",
                ]}
                for row in version["demand_results"]
                if row["priority"] == "high"
            ],
            key=lambda row: row["demand_score"],
            reverse=True,
        )[:12]
        return ScheduleResponse(
            version_id=version["version_id"],
            store_id=version["store_id"],
            store_name=self.settings.store_name,
            week_start=version["week_start"],
            generated_at=version["generated_at"],
            agent_summary=version["agent_summary"],
            agent_fallback=version["agent_fallback"],
            demand_insights=insights,
            demand_results=version["demand_results"],
            schedule_items=version["schedule_items"],
            kpis=kpis,
            risks=version["risks"],
        )

    def modify(self, version_id: str, item_id: str, request: ModifyScheduleRequest) -> ModifyScheduleResponse | None:
        version = self.store.get_version(version_id)
        if not version:
            return None
        item = next((row for row in version["schedule_items"] if row["id"] == item_id), None)
        if not item:
            return None
        before = dict(item)
        after = {**item, **request.after, "source": "manual", "explanation": request.reason_text or "店长手动调整"}
        employee = self.generator.employees.get(after["employee_id"])
        if employee:
            after["employee_name"] = employee["name"]
            after["employee_type"] = employee["employee_type"]
            after["assignment_type"] = "temporary" if employee["employee_type"] == "temporary" else "regular"
        area = self.generator.areas.get(after["area_code"])
        if area:
            after["area_name"] = area["name"]
        task = self.generator.tasks.get((after["area_code"], after["task_code"]))
        if task:
            after["task_name"] = task["task_name"]
            after["is_protected"] = int(task["is_professional"] and after["employee_type"] == "regular")

        updated_items = [after if row["id"] == item_id else row for row in version["schedule_items"]]
        risks = self.generator.detect_risks(version_id, version["demand_results"], updated_items)
        severe = [risk for risk in risks if risk["level"] == "critical"]
        if severe and not request.force:
            record = self._record(version_id, item_id, before, after, request)
            return ModifyScheduleResponse(
                item=after,
                risks=severe,
                kpis=self.generator.calculate_kpis(version["demand_results"], version["schedule_items"], version["risks"], version["intervention_count"]),
                intervention_record=record,
                requires_confirmation=True,
            )

        record = self._record(version_id, item_id, before, after, request)
        self.store.update_schedule_item(version_id, item_id, after)
        self.store.add_intervention({**record.model_dump(), "version_id": version_id})
        new_intervention_count = version["intervention_count"] + 1
        kpis = self.generator.calculate_kpis(version["demand_results"], updated_items, risks, new_intervention_count)
        return ModifyScheduleResponse(
            item=after,
            risks=risks,
            kpis=kpis,
            intervention_record=record,
            requires_confirmation=False,
        )

    def preferences(self, version_id: str, employee_id: str | None = None) -> list[dict[str, Any]] | None:
        version = self.store.get_version(version_id)
        if not version:
            return None
        rows = [
            {
                **row,
                "employee_name": self.generator.employees[row["employee_id"]]["name"],
                "default_shift_type": self.generator.employees[row["employee_id"]].get("regular_shift_type"),
            }
            for row in self.generator.seed["employee_weekly_preferences"]
            if row["week_start"] == version["week_start"] and (employee_id is None or row["employee_id"] == employee_id)
        ]
        return rows

    def leave_preferences(self, version_id: str, employee_id: str | None = None) -> list[dict[str, Any]] | None:
        version = self.store.get_version(version_id)
        if not version:
            return None
        return [
            {**row, "employee_name": self.generator.employees[row["employee_id"]]["name"]}
            for row in self.generator.seed["employee_weekly_leave"]
            if row["week_start"] == version["week_start"] and (employee_id is None or row["employee_id"] == employee_id)
        ]

    def leave_resolution(self, version_id: str) -> list[dict[str, Any]] | None:
        version = self.store.get_version(version_id)
        if not version:
            return None
        return self.generator._leave_payload(version["week_start"], self.generator.resolve_leave(version["week_start"]))

    def kpis(self, version_id: str) -> dict[str, Any] | None:
        version = self.store.get_version(version_id)
        if not version:
            return None
        return self.generator.calculate_kpis(
            version["demand_results"],
            version["schedule_items"],
            version["risks"],
            version["intervention_count"],
        ).model_dump()

    def risks(self, version_id: str) -> list[dict[str, Any]] | None:
        version = self.store.get_version(version_id)
        if not version:
            return None
        return version["risks"]

    def interventions(self, version_id: str) -> list[dict[str, Any]] | None:
        if not self.store.get_version(version_id):
            return None
        return self.store.interventions(version_id)

    def _validate_generation_request(self, request: GenerateScheduleRequest) -> None:
        if request.store_id != self.settings.store_id:
            raise ValueError("STORE_NOT_FOUND")
        start = datetime.strptime(request.week_start, "%Y-%m-%d").date()
        if start.weekday() != 0:
            raise ValueError("INVALID_WEEK_START")

    def _record(
        self,
        version_id: str,
        item_id: str,
        before: dict[str, Any],
        after: dict[str, Any],
        request: ModifyScheduleRequest,
    ):
        from app.models.schemas import InterventionRecord

        return InterventionRecord(
            id=f"ir_{uuid4().hex[:8]}",
            schedule_item_id=item_id,
            before=before,
            after=after,
            reason_code=request.reason_code,
            reason_text=request.reason_text,
            created_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )
