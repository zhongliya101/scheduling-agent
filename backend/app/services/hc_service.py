from __future__ import annotations

from app.data.store import SQLiteStore
from app.engine.scheduling import SchedulingGenerator


class HcService:
    def __init__(self, store: SQLiteStore | None = None, generator: SchedulingGenerator | None = None) -> None:
        self.store = store or SQLiteStore()
        self.generator = generator or SchedulingGenerator()

    def optimize(self, version_id: str) -> list[dict[str, str]]:
        version = self.store.get_version(version_id)
        if not version:
            return []
        gap_by_area: dict[str, int] = {}
        for risk in version["risks"]:
            if risk["type"] != "peak_gap":
                continue
            for area_code, area in self.generator.areas.items():
                if area["name"] in risk["description"]:
                    gap_by_area[area_code] = gap_by_area.get(area_code, 0) + 1
        suggestions = []
        for index, (area_code, count) in enumerate(sorted(gap_by_area.items(), key=lambda item: item[1], reverse=True), 1):
            area = self.generator.areas[area_code]
            suggestions.append(
                {
                    "id": f"hc_{index:04d}",
                    "area_code": area_code,
                    "area_name": area["name"],
                    "suggestion_type": "temporary_pool_adjustment",
                    "title": f"{area['name']}高峰临时工池增加1人",
                    "description": f"本周{area['name']}出现{count}个高峰缺口，建议增加具备通用任务技能的临时工或提高该区域临时工优先级。",
                    "expected_impact": "预计降低高峰缺口并减少店长临时调班。",
                    "status": "pending",
                }
            )
        if not suggestions:
            suggestions.append(
                {
                    "id": "hc_0001",
                    "area_code": "produce",
                    "area_name": "果蔬区",
                    "suggestion_type": "skill_cross_training",
                    "title": "保留现有编制，增强果蔬/收银交叉训练",
                    "description": "当前缺口风险较低，优先通过临时工技能复训提升补位弹性。",
                    "expected_impact": "维持成本稳定，提高跨区补位成功率。",
                    "status": "pending",
                }
            )
        self._save(suggestions)
        return suggestions

    def suggestions(self) -> list[dict[str, str]]:
        return self.store.fetch_all("hc_suggestions", "id")

    def confirm(self, suggestion_id: str, status: str) -> dict[str, str] | None:
        with self.store.connect() as conn:
            row = conn.execute("SELECT * FROM hc_suggestions WHERE id = ?", (suggestion_id,)).fetchone()
            if not row:
                return None
            conn.execute("UPDATE hc_suggestions SET status = ? WHERE id = ?", (status, suggestion_id))
            updated = dict(row)
            updated["status"] = status
            return updated

    def _save(self, suggestions: list[dict[str, str]]) -> None:
        with self.store.connect() as conn:
            conn.execute("DELETE FROM hc_suggestions")
            for row in suggestions:
                conn.execute(
                    """
                    INSERT INTO hc_suggestions
                    (id, area_code, area_name, suggestion_type, title, description, expected_impact, status)
                    VALUES (:id, :area_code, :area_name, :suggestion_type, :title, :description, :expected_impact, :status)
                    """,
                    row,
                )

