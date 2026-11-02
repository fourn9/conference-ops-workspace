import json
from pathlib import Path
import unittest

from demo.workspace import build


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((Path(__file__).parents[1] / "demo/fixture.json").read_text())

    def test_confirmed_label_needs_a_decision_record(self):
        report = build(self.fixture)
        self.assertEqual([e["id"] for e in report["decisions"]["confirmed"]], ["decision-01"])
        self.assertEqual([e["id"] for e in report["decisions"]["open"]], ["decision-02", "decision-03"])
        self.assertEqual(report["external_actions_performed"], 0)

    def test_unapproved_decision_blocks_dependent_task(self):
        tasks = {t["id"]: t for t in build(self.fixture)["tasks"]}
        self.assertFalse(tasks["task-01"]["blocked"])
        self.assertTrue(tasks["task-02"]["blocked"])
        self.assertTrue(tasks["task-03"]["blocked"])
        self.assertNotIn("task-04", tasks)
        self.assertEqual(tasks["task-02"]["timing"], "overdue")

    def test_missing_future_and_invalid_approval_records_stay_open(self):
        approval = self.fixture["journal"][0]["approval"]
        cases = (("explicit", "true"), ("by", ""), ("reference", ""),
                 ("date", "2031-01-01"), ("date", "invalid"))
        for key, value in cases:
            with self.subTest(key=key, value=value):
                previous = approval[key]
                approval[key] = value
                self.assertEqual(build(self.fixture)["decisions"]["confirmed"], [])
                approval[key] = previous

    def test_rejection_also_requires_a_human_record(self):
        self.fixture["journal"][3].pop("approval")
        self.assertEqual(build(self.fixture)["decisions"]["rejected"], [])

    def test_duplicates_are_rejected(self):
        self.fixture["journal"].append(self.fixture["journal"][0])
        with self.assertRaises(ValueError):
            build(self.fixture)

    def test_unknown_decision_reference_blocks(self):
        self.fixture["tasks"][0]["decision_refs"] = ["missing"]
        task = next(t for t in build(self.fixture)["tasks"] if t["id"] == "task-01")
        self.assertTrue(task["blocked"])

    def test_unexpected_task_status_is_not_silently_dropped(self):
        self.fixture["tasks"][0]["status"] = "in_progress"
        with self.assertRaises(ValueError):
            build(self.fixture)

    def test_invalid_fixtures(self):
        for value in ({}, [], {"synthetic": False}, {"synthetic": True}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                build(value)


if __name__ == "__main__":
    unittest.main()
