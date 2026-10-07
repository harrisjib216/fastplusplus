#!/usr/bin/env python3
"""Merge seed-mining outputs (data/seeds/raw/*.json) into data/seeds/seeds.json: validate the schema,
canonicalise repo URLs, drop seeds already on the known list, dedup across sections (first hit wins,
other sections appended to found_in), and report counts per guessed wave and claim flag."""
import json, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge import canonical, read_url_list, KNOWN_LIST  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SEEDS = ROOT / "data" / "seeds"
KEYS = {"name", "repo_url", "listed_description", "listed_license", "performance_claim_in_description", "claim_text",
        "guessed_wave", "guessed_category", "guessed_baseline", "found_in", "confidence"}


def main():
    known = {canonical(u) for u in read_url_list(KNOWN_LIST)}
    seeds, report = {}, []
    dropped_known = dropped_bad = 0
    for raw in sorted((SEEDS / "raw").glob("*.json")):
        try:
            entries = json.loads(raw.read_text())
        except json.JSONDecodeError as err:
            report.append(f"{raw.name}: INVALID JSON ({err})"); continue
        if not isinstance(entries, list):
            report.append(f"{raw.name}: not a list"); continue
        n_new = 0
        for e in entries:
            if not isinstance(e, dict) or not e.get("repo_url"):
                dropped_bad += 1; continue
            missing = KEYS - set(e)
            for k in missing:
                e[k] = None if k != "performance_claim_in_description" else False
            key = canonical(e["repo_url"])
            if not key or key in known:
                dropped_known += 1; continue
            e["id"] = key
            e["source_file"] = raw.stem
            if key in seeds:
                prev = seeds[key]
                prev["found_in"] = sorted(set(str(prev["found_in"]).split(" | ")) | {str(e["found_in"])})
                prev["found_in"] = " | ".join(prev["found_in"])
                prev["performance_claim_in_description"] = bool(prev["performance_claim_in_description"] or e["performance_claim_in_description"])
                continue
            seeds[key] = e; n_new += 1
        report.append(f"{raw.name}: {len(entries)} entries, {n_new} new")
    out = sorted(seeds.values(), key=lambda e: (str(e["guessed_wave"]), not e["performance_claim_in_description"], str(e["name"]).lower()))
    (SEEDS / "seeds.json").write_text(json.dumps(out, indent=2) + "\n")
    print("\n".join(report))
    print(f"\nseeds: {len(out)} unique ({sum(1 for e in out if e['performance_claim_in_description'])} with a claim); "
          f"dropped {dropped_known} known, {dropped_bad} malformed")
    for w, n in sorted(Counter(str(e["guessed_wave"]) for e in out).items()):
        c = sum(1 for e in out if str(e["guessed_wave"]) == w and e["performance_claim_in_description"])
        print(f"  {w}: {n} ({c} with claim)")


if __name__ == "__main__":
    main()
