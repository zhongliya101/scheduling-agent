import tempfile
import unittest
from pathlib import Path

from app.data.seed_loader import SeedLoader
from app.data.store import SQLiteStore
from app.engine.scheduling import SchedulingGenerator
from app.models.schemas import GenerateScheduleRequest, ModifyScheduleRequest
from app.services.agent_service import AgentService
from app.services.demand_service import DemandService
from app.services.schedule_service import ScheduleService


ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "backend" / "app" / "seed"


class ScheduleCoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        loader = SeedLoader(SEED)
        store = SQLiteStore(Path(self.tmp.name) / "demo.sqlite", loader)
        demand = DemandService(loader)
        generator = SchedulingGenerator(loader)
        self.service = ScheduleService(store, demand, generator)
        self.agent = AgentService(store, generator)

    def tearDown(self):
        self.tmp.cleanup()

    def test_generate_week_schedule(self):
        response = self.service.generate(
            GenerateScheduleRequest(store_id="fresh_store_001", week_start="2026-07-13")
        )
        self.assertEqual(len(response.demand_results), 490)
        self.assertGreaterEqual(len(response.schedule_items), 140)
        self.assertEqual(response.kpis.professional_coverage_rate, 1.0)
        self.assertEqual(response.kpis.baseline_achievement_rate, 1.0)
        self.assertGreaterEqual(response.kpis.mixed_utilization_rate, 0.8)
        hours_by_employee = {}
        for item in response.schedule_items:
            hours_by_employee[item.employee_id] = hours_by_employee.get(item.employee_id, 0) + item.hours
        for employee_id, hours in hours_by_employee.items():
            limit = self.service.generator.employees[employee_id]["weekly_hours_limit"]
            self.assertLessEqual(hours, limit)

    def test_agent_recommends_temporary_support(self):
        response = self.service.generate(
            GenerateScheduleRequest(store_id="fresh_store_001", week_start="2026-07-13")
        )
        candidates = self.agent.recommend_support(
            response.version_id, "2026-07-17", "18:00-19:00", "produce", "restock"
        )
        self.assertTrue(candidates)
        self.assertIn("employee_name", candidates[0])

    def test_manual_modify_records_intervention(self):
        response = self.service.generate(
            GenerateScheduleRequest(store_id="fresh_store_001", week_start="2026-07-13")
        )
        item = next(row for row in response.schedule_items if row.assignment_type == "temporary")
        result = self.service.modify(
            response.version_id,
            item.id,
            ModifyScheduleRequest(
                after={"area_code": "cashier", "task_code": "cashier"},
                reason_code="manager_experience",
                reason_text="晚高峰收银更需要支援",
                force=True,
            ),
        )
        self.assertIsNotNone(result)
        interventions = self.service.interventions(response.version_id)
        self.assertEqual(len(interventions), 1)


if __name__ == "__main__":
    unittest.main()
