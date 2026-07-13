from __future__ import annotations

from typing import Any

from app.data.store import SQLiteStore
from app.engine.scheduling import SchedulingGenerator


class AgentService:
    def __init__(self, store: SQLiteStore | None = None, generator: SchedulingGenerator | None = None) -> None:
        self.store = store or SQLiteStore()
        self.generator = generator or SchedulingGenerator()

    def chat(self, message: str, version_id: str | None = None, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        version = self.store.get_version(version_id) if version_id else None
        text = message.lower()
        if "老张" in message and ("收银" in message or "调" in message):
            return {
                "intent": "explain_unavailable_transfer",
                "is_fallback": True,
                "message": "不建议把老张调去收银。当前规则下专业师傅在保护时段要优先留在原区域，尤其是切肉/分割这类S/A级专业岗；抽走会造成肉类区专业岗和区域保底双重风险。可改用临时工池补收银或果蔬晚高峰缺口。",
                "candidates": [],
            }
        if "谁能" in message or "支援" in message or "候选" in message:
            area_code = context.get("area_code") or self._guess_area(message)
            slot = context.get("slot", "18:00-21:00")
            date = context.get("date") or self._first_friday(version)
            candidates = (
                self.generator.recommend_support(version, date, slot, area_code, context.get("task_code"))
                if version and date
                else []
            )
            names = "、".join(row["employee_name"] for row in candidates[:3]) or "暂无可用临时工"
            return {
                "intent": "recommend_support",
                "is_fallback": True,
                "message": f"建议优先看{names}。推荐依据是临时工跨区能力、对应任务技能等级、区域熟悉度和本周剩余工时；专业固定岗不会被抽调用来补通用缺口。",
                "candidates": candidates,
            }
        if "为什么" in message or "解释" in message or "需求" in message:
            return self.explain_demand(
                version_id or "",
                context.get("date") or self._first_friday(version),
                context.get("slot", "18:00-19:00"),
                context.get("area_code") or self._guess_area(message),
            )
        return {
            "intent": "general_schedule_summary",
            "is_fallback": True,
            "message": "当前班表采用半混班策略：正式工固定在所属区域并覆盖专业岗，临时工进入全店混排池补晚高峰和周末通用任务缺口。你可以问我某个时段为什么缺人、谁能支援，或为什么某位师傅不能被调走。",
            "candidates": [],
        }

    def recommend_support(
        self, version_id: str, date: str, slot: str, area_code: str, task_code: str | None = None
    ) -> list[dict[str, Any]]:
        version = self.store.get_version(version_id)
        if not version:
            return []
        return self.generator.recommend_support(version, date, slot, area_code, task_code)

    def explain_demand(self, version_id: str, date: str | None, slot: str, area_code: str) -> dict[str, Any]:
        version = self.store.get_version(version_id) if version_id else None
        row = None
        if version and date:
            row = next(
                (
                    item
                    for item in version["demand_results"]
                    if item["date"] == date and item["slot"] == slot and item["area_code"] == area_code
                ),
                None,
            )
        if not row:
            return {
                "intent": "explain_demand",
                "is_fallback": True,
                "message": "暂未找到这个时段的需求记录。请先生成班表，或指定日期、时段和区域。",
                "candidates": [],
            }
        factors = "、".join(row["demand_factors"])
        return {
            "intent": "explain_demand",
            "is_fallback": True,
            "message": f"{row['date']} {row['slot']} {row['area_name']}需要{row['required_count']}人，需求分{row['demand_score']}。主要依据是{factors}；系统因此把该时段标记为{row['priority']}优先级，并用于后续正式工保底和临时工补位。",
            "candidates": [],
        }

    def _guess_area(self, message: str) -> str:
        if "水产" in message:
            return "aquatic"
        if "肉" in message:
            return "meat"
        if "收银" in message:
            return "cashier"
        if "补货" in message:
            return "replenishment"
        return "produce"

    def _first_friday(self, version: dict[str, Any] | None) -> str | None:
        if not version:
            return None
        for row in version["demand_results"]:
            if row["weekday"] == "Friday":
                return row["date"]
        return version["week_start"]
