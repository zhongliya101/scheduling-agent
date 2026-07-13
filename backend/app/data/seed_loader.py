from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from app.core.config import get_settings


class SeedLoader:
    def __init__(self, seed_dir: Path | None = None) -> None:
        self.seed_dir = seed_dir or get_settings().seed_dir

    def json(self, name: str) -> list[dict[str, Any]]:
        with (self.seed_dir / name).open(encoding="utf-8") as fh:
            return json.load(fh)

    def csv(self, name: str) -> list[dict[str, str]]:
        with (self.seed_dir / name).open(encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    def all(self) -> dict[str, list[dict[str, Any]]]:
        return {
            "areas": self.json("areas.json"),
            "area_tasks": self.json("area_tasks.json"),
            "skill_definitions": self.json("skill_definitions.json"),
            "employees": self.json("employees.json"),
            "employee_skills": self.json("employee_skills.json"),
            "employee_weekly_preferences": self.json("employee_weekly_preferences.json"),
            "employee_weekly_leave": self.json("employee_weekly_leave.json"),
            "modified_reasons": self.json("modified_reasons.json"),
            "historical_sales": self.csv("historical_sales.csv"),
            "historical_traffic": self.csv("historical_traffic.csv"),
            "online_orders": self.csv("online_orders.csv"),
            "weather": self.csv("weather.csv"),
            "holidays": self.csv("holidays.csv"),
            "promotions": self.csv("promotions.csv"),
        }

