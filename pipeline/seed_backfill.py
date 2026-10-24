#!/usr/bin/env python3
"""Backfill seed-record passes from data/seeds/seeds.json (docs/QUEUE.md section F, steps 2-4).
Groups seeds by guessed wave, registers `mine` assignments (w{N}-mine-{k}) in the wave's
assignments.json and renders one prompt per group to data/wave{N}/prompts/<id>.txt. Unlike seed.py,
a project with no numeric comparison against a recognisable baseline gets NO record: the agent
lists it in data/seeds/no_evidence/<id>.json instead (SEEDS_NO_EVIDENCE.md is compiled from those)."""
import argparse, json, string
from pathlib import Path

import seed  # noqa: E402  (same directory)
from seeds_merge import has_numbers  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def book_techniques(s, limit=12):
    """Lead text for a book companion repo: the book's benchmarked techniques, measured ones first."""
    ts = sorted(s.get("techniques") or [], key=lambda t: (not has_numbers(t), not t["claim_text"]))
    if not ts:
        return ""
    items = [f"{t['name']}: {t['claim_text'] or 'no numbers'}"
             + (f" [measured: {t['book_benchmark']}]" if has_numbers(t) and t["book_benchmark"] else "")
             + f" ({t['found_in']})"
             for t in ts[:limit]]
    more = f"; {len(ts) - limit} more in data/seeds/seeds.json" if len(ts) > limit else ""
    return " Book techniques, one candidate record each if the repo carries the code: " + "; ".join(items) + more
SEEDS = ROOT / "data" / "seeds"
WAVE_DIR = {"stdlib-replacements": "wave1", "toolchain-and-build": "wave2", "parsing-and-text": "wave3",
            "serialization-and-formats": "wave4", "networking-and-servers": "wave5", "storage-and-data": "wave6",
            "crypto-and-hashing": "wave7", "numerics-and-science": "wave8", "compression-and-encoding": "wave9",
            "media-and-graphics": "wave10", "runtime-and-systems": "wave11", "interpreters-and-vms": "wave12",
            "assembly-simd-kernels-and-wasm": "wave13", "other-languages-faster-than-c-cpp-asm": "wave14"}

NO_EVIDENCE_RULE = """
- BACKFILL RULE (replaces the tier-D fallback above): these projects come from a curated list,
  not from the known list. If a project has NO numeric comparison against any recognizable
  baseline anywhere you can reach (README, docs, wiki, issues, linked benchmark repo, a shootout
  that includes it), do NOT write a record for it. Instead append an object
  {{"name", "repo_url", "listed_description", "reason"}} to the JSON array at:
    {no_evidence_path}
  (create the file as [] first). A project with a directional claim but no numbers also goes
  there. Only projects with at least one number against a named baseline get a record.
- The "guessed" wave, category and baseline in each line are a Haiku agent's guess from the
  list's one-line description; correct them from what the repo actually is.
"""

BOOK_RULE = """
- BOOK TECHNIQUES: a project named "(book techniques)" is a C++ book's companion code; its lead lists
  the techniques the book benchmarks or cites. Write one record per technique whose code the repo
  actually carries (check the chapter folders), each with its own explicit id
  "paper:book-<repo name>-<technique slug>" (lowercase, hyphens) and repo_url set to that repo,
  so the records stay separate. Do not copy book text: the lead already paraphrases the book's
  numbers; a book's own measurement is first-party unless its repo carries the benchmark code
  with compiler, flags and CPU. A technique with no code in the repo goes to the no-evidence file.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", required=True)
    ap.add_argument("--claims-only", action="store_true", help="only seeds whose list description carries a claim")
    ap.add_argument("--group", type=int, default=7)
    ap.add_argument("--waves", nargs="*", help="limit to these domains")
    ap.add_argument("--skip-assigned", action="store_true", help="skip seeds already in a mine assignment")
    args = ap.parse_args()
    seeds = json.loads((SEEDS / "seeds.json").read_text())
    (SEEDS / "no_evidence").mkdir(parents=True, exist_ok=True)
    secs = seed.sections(seed.load_template())
    kept = []
    for title, body in secs.items():
        if title.startswith(seed.KEEP_SECTIONS):
            kept.append("=" * 69 + f"\n{title}\n" + "=" * 69 + "\n" + body.strip() + "\n")
    rules = "\n".join(kept)
    rules = (rules.replace("{DOMAIN}", "<project's domain>").replace("{CATEGORY}", "<project's category>")
             .replace("{SOURCE}", "seed-list mining backfill").replace("{BASELINES}", "the baselines guessed for that project, or better ones"))
    by_wave = {}
    for s in seeds:
        w = s.get("guessed_wave")
        if w not in WAVE_DIR or (args.claims_only and not s["performance_claim_in_description"]):
            continue
        if args.waves and w not in args.waves:
            continue
        by_wave.setdefault(w, []).append(s)
    total = 0
    for w, items in sorted(by_wave.items()):
        wdir = ROOT / "data" / WAVE_DIR[w]
        manifest = json.loads((wdir / "assignments.json").read_text())
        existing = {a["id"] for a in manifest["assignments"]}
        assigned = {p["repo_url"].lower() for a in manifest["assignments"] if a.get("batch") == "mine" for p in a["projects"]}
        if args.skip_assigned:
            items = [s for s in items if s["repo_url"].lower() not in assigned]
        letters = iter([c for c in string.ascii_lowercase] + [a + b for a in string.ascii_lowercase for b in string.ascii_lowercase])
        prompts_dir, raw_dir = wdir / "prompts", wdir / "raw"
        prompts_dir.mkdir(exist_ok=True); raw_dir.mkdir(exist_ok=True)
        for i in range(0, len(items), args.group):
            group = items[i:i + args.group]
            while True:
                aid = f"w{WAVE_DIR[w][4:]}-mine-{next(letters)}"
                if aid not in existing:
                    break
            projects = [{"name": s["name"], "repo_url": s["repo_url"], "domain": w,
                         "category": s.get("guessed_category") or "<pick from the wave's categories>",
                         "baselines": s.get("guessed_baseline") or "<guess from the project's role>",
                         "lead": f"Listed as: {s.get('listed_description') or ''} (claim words: {s.get('claim_text')}; licence tag: {s.get('listed_license')}; {s.get('found_in')})"
                                 + (f" Book benchmark: {s['book_benchmark']}" if s.get("book_benchmark") else "")
                                 + book_techniques(s)}
                        for s in group]
            manifest["assignments"].append({"id": aid, "batch": "mine", "projects": projects})
            existing.add(aid)
            plines = "\n".join(
                f"- {p['name']} | {p['repo_url']} | domain: {p['domain']} | category: {p['category']} | baselines: {p['baselines']} | lead: {p['lead']}"
                for p in projects)
            out = (raw_dir / f"{aid}.json").resolve()
            noev = (SEEDS / "no_evidence" / f"{aid}.json").resolve()
            prompt = (seed.INTRO.format(today=args.today, projects=plines) + NO_EVIDENCE_RULE.format(no_evidence_path=noev)
                      + (BOOK_RULE if any(s.get("techniques") for s in group) else "")
                      + "\n" + rules + seed.HARNESS.format(output_path=out))
            (prompts_dir / f"{aid}.txt").write_text(prompt)
            print(f"{aid}: {len(group)} projects -> {prompts_dir / (aid + '.txt')}")
            total += 1
        (wdir / "assignments.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{total} backfill assignments rendered")


if __name__ == "__main__":
    main()
