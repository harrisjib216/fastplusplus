#!/usr/bin/env python3
"""Verifier stage: `render` batches merged.json into verifier prompts; `apply` folds verdicts into verified/rejected."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "pipeline" / "verifier_prompt.txt"
CORRECTABLE = {
    "benchmark_url", "claimed_speedup", "baseline", "baseline_in_list", "baseline_stdlib", "compiler_and_flags", "hardware",
    "compared_against_cpp_std_directly", "license", "usability", "last_commit", "maintenance_status",
    "is_fork_of", "stars_or_usage", "has_code", "caveats", "workload",
}
PUBLIC_DOMAIN = re.compile(r"\bCC0\b|public[ -]domain", re.I)
STRIP_FOR_VERIFIER = {"tradeoffs", "found_via", "assignment_ids", "domain", "is_evidence_for_known"}


def render(wave_dir, batch_size, today):
    prompts_dir, raw_dir = wave_dir / "verify" / "prompts", wave_dir / "verify" / "raw"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    done = {v["id"] for f in raw_dir.glob("batch-*.json") for v in json.loads(f.read_text())}
    done |= {i for f in prompts_dir.glob("batch-*.ids.json") for i in json.loads(f.read_text())}
    entries = [e for e in json.loads((wave_dir / "merged.json").read_text()) if e["id"] not in done]
    first = 1 + max((int(p.stem.split("-")[1]) for p in prompts_dir.glob("batch-*.txt")), default=0)
    template = TEMPLATE.read_text()
    for n, i in enumerate(range(0, len(entries), batch_size), first):
        batch = [{k: v for k, v in e.items() if k not in STRIP_FOR_VERIFIER} for e in entries[i:i + batch_size]]
        out = (raw_dir / f"batch-{n:02d}.json").resolve()
        prompt = (template.replace("{TODAY}", today)
                  .replace("{ENTRIES_JSON}", json.dumps(batch, indent=2))
                  .replace("{OUTPUT_PATH}", str(out)))
        (prompts_dir / f"batch-{n:02d}.txt").write_text(prompt)
        (prompts_dir / f"batch-{n:02d}.ids.json").write_text(json.dumps([e["id"] for e in batch]))
        print(f"{prompts_dir / f'batch-{n:02d}.txt'}  ({len(batch)} records: {', '.join(e['name'] for e in batch)})")


def apply(wave_dir, today):
    entries = {e["id"]: e for e in json.loads((wave_dir / "merged.json").read_text())}
    verdicts, retiers = {}, {}
    for f in sorted((wave_dir / "verify" / "raw").glob("batch-*.json")):
        for v in json.loads(f.read_text()):
            verdicts[v["id"]] = v
    for f in sorted((wave_dir / "verify" / "raw").glob("retier-*.json")):
        for v in json.loads(f.read_text()):
            retiers[v["id"]] = v

    verified, rejected, unverified = [], [], []
    tier_moves, fixed_fields, verdict_counts = Counter(), Counter(), Counter()
    for eid, e in entries.items():
        v = verdicts.get(eid)
        if v is None:
            unverified.append(eid)
            continue
        verdict_counts[v["verdict"]] += 1
        e["verification"] = {
            "date": today, "verdict": v["verdict"], "tier_before": e["evidence_tier"],
            "tier_reason": v.get("tier_reason"), "notes": v.get("notes"), "urls_opened": v.get("urls_opened", []),
            "page_compares_against_baseline": v.get("page_compares_against_baseline"),
            "numbers_found_on_page": v.get("numbers_found_on_page"),
        }
        if v["verdict"] == "reject":
            e["verification"]["reject_reason"] = v.get("reject_reason")
            rejected.append(e)
            continue
        for field, value in (v.get("corrections") or {}).items():
            if field in CORRECTABLE and e.get(field) != value:
                e.setdefault("corrected_fields", {})[field] = e.get(field)
                e[field] = value
                fixed_fields[field] += 1
        tier = v["evidence_tier_final"]
        r = retiers.get(eid)
        for field, value in ((r or {}).get("corrections") or {}).items():
            if field in CORRECTABLE and e.get(field) != value:
                e.setdefault("corrected_fields", {}).setdefault(field, e.get(field))
                # retier caveats add to the verifier's caveats rather than replacing them
                e[field] = f"{e.get(field) or ''} [retier] {value}".strip() if field == "caveats" else value
                fixed_fields[field] += 1
        if r and r["evidence_tier_final"] != tier:
            e["verification"]["retier"] = {"from": tier, "to": r["evidence_tier_final"], "reason": r.get("tier_reason"),
                                           "urls_opened": r.get("urls_opened", [])}
            tier = r["evidence_tier_final"]
        if e["usability"] == "reference" and PUBLIC_DOMAIN.search(e.get("license") or ""):
            e.setdefault("corrected_fields", {}).setdefault("usability", "reference")
            e["usability"] = "copyable"
            e["caveats"] = f"{e.get('caveats') or ''} [policy] CC0/public-domain dedication: copyable, but no patent grant.".strip()
        tier_moves[f"{e['evidence_tier']}->{tier}"] += 1
        e["evidence_tier"] = tier
        verified.append(e)

    (wave_dir / "verified.json").write_text(json.dumps(verified, indent=2) + "\n")
    (wave_dir / "rejected.json").write_text(json.dumps(rejected, indent=2) + "\n")
    print(f"verdicts: {dict(verdict_counts)}   unverified (no verdict): {unverified}")
    print(f"tier moves: {dict(sorted(tier_moves.items()))}")
    print(f"corrected fields: {dict(fixed_fields.most_common())}")
    print(f"verified by tier: {dict(sorted(Counter(e['evidence_tier'] for e in verified).items()))}")
    print(f"verified by usability: {dict(Counter(e['usability'] for e in verified))}")
    for e in rejected:
        print(f"  REJECTED {e['name']}: {e['verification']['reject_reason']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["render", "apply"])
    ap.add_argument("wave_dir", type=Path)
    ap.add_argument("--batch-size", type=int, default=5)
    args = ap.parse_args()
    today = json.loads((args.wave_dir / "assignments.json").read_text())["today"]
    if args.command == "render":
        render(args.wave_dir, args.batch_size, today)
    else:
        apply(args.wave_dir, today)


if __name__ == "__main__":
    main()
