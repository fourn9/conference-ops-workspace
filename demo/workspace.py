#!/usr/bin/env python3
"""Render a synthetic operations handoff with explicit decision provenance."""

import argparse
from datetime import date
import json
from pathlib import Path
import sys


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def build(data):
    if not isinstance(data, dict) or data.get("synthetic") is not True:
        raise ValueError("This public demo accepts explicitly synthetic fixtures only")
    try:
        today = date.fromisoformat(data["as_of"])
        event = data["event"]
        if not nonempty(event):
            raise ValueError("event must be a non-empty string")
        entries, tasks = data["journal"], data["tasks"]
        if not isinstance(entries, list) or not isinstance(tasks, list):
            raise ValueError("journal and tasks must be arrays")
        seen = set()
        decisions = {"confirmed": [], "open": [], "rejected": []}
        for entry in entries:
            entry_id = entry["id"]
            if not nonempty(entry_id) or entry_id in seen:
                raise ValueError("Journal IDs must be non-empty and unique")
            seen.add(entry_id)
            if not nonempty(entry["text"]):
                raise ValueError("Journal entries need text")
            requested = entry.get("status", "open")
            if requested not in ("confirmed", "open", "rejected"):
                raise ValueError("Unknown journal status")
            approval = entry.get("approval") or {}
            if not isinstance(approval, dict):
                raise ValueError("approval must be an object")
            try:
                approval_date = date.fromisoformat(approval.get("date", ""))
                dated = approval_date <= today
            except (TypeError, ValueError):
                dated = False
            has_approval = (approval.get("explicit") is True
                            and nonempty(approval.get("by"))
                            and nonempty(approval.get("reference")) and dated)
            # An agent-written 'confirmed' label alone never becomes a decision.
            status = requested if requested == "open" or has_approval else "open"
            record = dict(entry, effective_status=status)
            if requested != status:
                record["review_note"] = "Missing explicit, dated human decision record"
            decisions[status].append(record)

        confirmed_ids = {entry["id"] for entry in decisions["confirmed"]}
        queue = []
        task_ids = set()
        for task in tasks:
            if not nonempty(task["id"]) or task["id"] in task_ids:
                raise ValueError("Task IDs must be non-empty and unique")
            task_ids.add(task["id"])
            if not nonempty(task["title"]) or not nonempty(task["owner"]):
                raise ValueError("Tasks need a title and an owner")
            if task["status"] not in ("open", "done"):
                raise ValueError("Unknown task status")
            if task["status"] == "done":
                continue
            due = date.fromisoformat(task["due"])
            blockers = task.get("blocked_by", [])
            refs = task.get("decision_refs", [])
            if not isinstance(blockers, list) or not isinstance(refs, list):
                raise ValueError("blocked_by and decision_refs must be arrays")
            if not all(nonempty(value) for value in blockers + refs):
                raise ValueError("Task references must be non-empty strings")
            missing = [ref for ref in refs if ref not in confirmed_ids]
            reasons = list(blockers) + ["decision not confirmed: " + ref for ref in missing]
            timing = "overdue" if due < today else "today" if due == today else "upcoming"
            queue.append(dict(task, timing=timing, blocked=bool(reasons), reasons=reasons))
        queue.sort(key=lambda task: (task["due"], task["id"]))
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("Malformed workspace fixture") from error
    return {"synthetic": True, "event": event, "as_of": data["as_of"],
            "decisions": decisions, "tasks": queue, "external_actions_performed": 0}


def markdown(report):
    lines = ["# {} — operations handoff".format(report["event"]), "",
             "Synthetic example, as of {}. No messages are sent.".format(report["as_of"]), "",
             "## Decisions"]
    for status, entries in report["decisions"].items():
        lines += ["", "### {} ({})".format(status.capitalize(), len(entries)), ""]
        for entry in entries:
            lines.append("- **{}**: {}".format(entry["id"], entry["text"]))
            if entry.get("review_note"):
                lines.append("  - Review: " + entry["review_note"])
            if status != "open":
                approval = entry["approval"]
                lines.append("  - Decision record: {} / {} / {}".format(
                    approval["by"], approval["date"], approval["reference"]))
    lines += ["", "## Work queue", ""]
    for task in report["tasks"]:
        state = "blocked" if task["blocked"] else "ready for owner"
        lines.append("- **{}** · {} · {} · {}: {}".format(
            task["id"], task["timing"], state, task["owner"], task["title"]))
        lines += ["  - " + reason for reason in task["reasons"]]
    lines += ["", "## Handoff", "",
              "Resolve open decisions and blockers before acting on dependent tasks.",
              "Approval fields are fixture data, not authentication or authorization.",
              "External actions performed: 0.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", nargs="?", type=Path,
                        default=Path(__file__).parent / "fixture.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = build(json.loads(args.fixture.read_text(encoding="utf-8")))
    except (OSError, ValueError) as error:
        parser.exit(2, "Error: {}\n".format(error))
    sys.stdout.write(json.dumps(report, indent=2) + "\n" if args.json else markdown(report))


if __name__ == "__main__":
    main()
