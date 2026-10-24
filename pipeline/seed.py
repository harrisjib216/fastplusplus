#!/usr/bin/env python3
"""Render seed-record prompts: records for named known-list projects, reusing Part 2's rules and schema."""
import argparse
import json
import re
from pathlib import Path

from render import load_template

KEEP_SECTIONS = ("WHAT COUNTS", "EVIDENCE TIERS", "DO NOT EXCLUDE", "HARD RULES", "OUTPUT SCHEMA")

INTRO = """You are producing catalog records for well-known projects that are
already on the catalog's known list. Unlike the search agents, you are told
exactly which projects to document. For EACH project below, find its best
evidence of beating one of the listed baselines and fill one record in the
schema further down. Accuracy matters far more than coverage.

Today's date: {today}

=====================================================================
PROJECTS TO DOCUMENT (one record each, in this order)
=====================================================================
{projects}

- If a project is a collection (abseil, folly, highway, ...), document the
  single component with the strongest documented comparison against the
  listed baselines and name it, e.g. "folly F14 (F14FastMap)". You may use
  a different category than suggested if that component clearly belongs
  elsewhere; set domain/category accordingly.
- If a project has no numeric comparison against any recognizable baseline,
  still return its record at tier D and explain in caveats.
- The KNOWN_LIST rules below do not apply to this task: every project here
  is on the known list by design. Set is_evidence_for_known=false.
- Where the schema says {{DOMAIN}}/{{CATEGORY}}, use the project's own domain
  and category. found_via = "seed-record pass" plus the page you started from.
"""

HARNESS = """
=====================================================================
ORCHESTRATOR HARNESS NOTES
=====================================================================
- Tools: WebFetch; the authenticated `gh` CLI (`gh api repos/OWNER/REPO`,
  `gh api "repos/OWNER/REPO/commits?per_page=1"`, `gh api repos/OWNER/REPO/readme
  -H "Accept: application/vnd.github.raw"`, `gh api repos/OWNER/REPO/contents/PATH
  -H "Accept: application/vnd.github.raw"`). Fetching through gh counts as
  opening the github.com URL. WebSearch has a per-session budget shared by all
  agents; prefer direct URLs, and for papers use
  http://export.arxiv.org/api/query?search_query=all:<terms> via WebFetch.
- Do not clone or build anything. Budget: about 40 tool calls per project;
  token cost is not a concern, so read the benchmark sources, not just READMEs.
- Never send the user's email address, name or any other personal identifier to an
  outside service (URLs, headers, payloads). For APIs that want a User-Agent, such as
  crates.io, use exactly: User-Agent: fastpp-research-bot/1.0
- Write the JSON array (one object per project, nothing else) to:
    {output_path}
  Then check it parses:
    python3 -c "import json,sys; json.load(open(sys.argv[1]))" {output_path}
- Final reply to the orchestrator: one line per project, "name: tier".
  Style: caveman ultra in all your own text and this reply (fragments, no articles, no filler, no arrows, no invented abbreviations; names, numbers and errors exact); the JSON output stays normal prose.
"""


def sections(template):
    parts = re.split(r"\n=+\n([^\n]+)\n=+\n", "\n" + template)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wave_dir", type=Path)
    ap.add_argument("--batch", help="only render assignments in this batch")
    args = ap.parse_args()
    manifest = json.loads((args.wave_dir / "assignments.json").read_text())
    secs = sections(load_template())
    kept = []
    for title, body in secs.items():
        if title.startswith(KEEP_SECTIONS):
            kept.append("=" * 69 + f"\n{title}\n" + "=" * 69 + "\n" + body.strip() + "\n")
    rules = "\n".join(kept)
    rules = (rules.replace("{DOMAIN}", "<project's domain>").replace("{CATEGORY}", "<project's category>")
             .replace("{SOURCE}", "seed-record pass").replace("{BASELINES}", "the baselines listed for that project"))
    leftover = set(re.findall(r"\{([A-Z_]+)\}", rules))
    if leftover:
        raise SystemExit(f"unfilled variables {sorted(leftover)}")

    prompts_dir, raw_dir = args.wave_dir / "prompts", args.wave_dir / "raw"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    for a in manifest["assignments"]:
        if (args.batch and a["batch"] != args.batch) or "projects" not in a:
            continue
        projects = "\n".join(
            f"- {p['name']} | {p['repo_url']} | domain: {p['domain']} | category: {p['category']} | "
            f"baselines: {p['baselines']}" + (f" | lead: {p['lead']}" if p.get("lead") else "")
            for p in a["projects"])
        out = (raw_dir / f"{a['id']}.json").resolve()
        prompt = INTRO.format(today=manifest["today"], projects=projects) + "\n" + rules + HARNESS.format(output_path=out)
        (prompts_dir / f"{a['id']}.txt").write_text(prompt)
        print(prompts_dir / f"{a['id']}.txt", f"({len(a['projects'])} projects)")


if __name__ == "__main__":
    main()
