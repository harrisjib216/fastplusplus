#!/usr/bin/env python3
"""Append shortcomings, measurements and overrides to data/decisions.json from JSON lines on stdin.

Each input line is one object:
  {"id": <entry id>, "s": <shortcoming>, "m": <measurement>,
   "decision": "keep|duplicate|reject", "reason": ...,
   "name"|"category"|"domain"|"repo_url"|"has_code"|"language": <override>}
Only "id" is required. A new id gets decision "keep" with the standing keep-and-document reason.
Repeated shortcomings/measurements are not added twice. Prints "ok N" (total entries).
"""
import json
import sys
from pathlib import Path

DECISIONS = Path(__file__).resolve().parent.parent / "data" / "decisions.json"
DEFAULT_REASON = "user decision 2026-09-25: keep flagged entries and document shortcomings"
OVERRIDES = ("decision", "reason", "name", "category", "domain", "repo_url", "has_code", "language")


def main():
    decisions = json.loads(DECISIONS.read_text()) if DECISIONS.exists() else []
    by_id = {d["id"]: d for d in decisions}
    for line in sys.stdin:
        if not line.strip():
            continue
        item = json.loads(line)
        entry = by_id.get(item["id"])
        if entry is None:
            entry = {"id": item["id"], "decision": "keep", "reason": DEFAULT_REASON}
            decisions.append(entry)
            by_id[item["id"]] = entry
        for field in OVERRIDES:
            if field in item:
                entry[field] = item[field]
        for key, field in (("s", "shortcomings"), ("m", "measurements")):
            if item.get(key) and item[key] not in entry.setdefault(field, []):
                entry[field].append(item[key])
        if not entry.get("measurements"):
            entry.pop("measurements", None)
    DECISIONS.write_text(json.dumps(decisions, indent=2) + "\n")
    print(f"ok {len(decisions)}")


if __name__ == "__main__":
    main()
