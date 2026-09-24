#!/usr/bin/env python3
"""Render Part 5 cleanup/enrichment prompts: one per verified entry."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "faster-than-std-agent-prompt.md"
INTERNAL_FIELDS = {"assignment_ids", "corrected_fields", "found_via"}

HARNESS = """
=====================================================================
ORCHESTRATOR HARNESS NOTES (environment-specific; these override only
the output-delivery rule above)
=====================================================================
- Tools: WebSearch and WebFetch (if they are not loaded yet, load them
  with ToolSearch query "select:WebSearch,WebFetch"). The `gh` CLI is
  authenticated; for GitHub repos prefer it over WebFetch:
    gh api repos/OWNER/REPO/readme -H "Accept: application/vnd.github.raw"
    gh api repos/OWNER/REPO/contents/PATH -H "Accept: application/vnd.github.raw"
    gh api "repos/OWNER/REPO/git/trees/HEAD?recursive=1" --jq '.tree[].path'
    gh search issues --repo OWNER/REPO "<terms>" --limit 20
  Fetching content through gh counts as opening the github.com URL.
- Do not clone repositories or build anything.
- The record's `verification` block holds the verifier's notes; treat its
  corrections as authoritative over older claims.
- Budget: about 15 tool calls.
- Deliver your output by writing the JSON object, and nothing else, to:
    {output_path}
  Then check it parses:
    python3 -c "import json,sys; json.load(open(sys.argv[1]))" {output_path}
- Your final reply to the orchestrator is one line: the entry name and your confidence.
"""


def load_template():
    text = SPEC.read_text()
    part5 = text.index("## Part 5")
    start = text.index("```\n", part5) + 4
    end = text.index("\n```", start)
    return text[start:end]


def slug(entry_id):
    return re.sub(r"[^a-z0-9]+", "_", entry_id.removeprefix("https://")).strip("_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wave_dir", type=Path)
    args = ap.parse_args()

    today = json.loads((args.wave_dir / "assignments.json").read_text())["today"]
    entries = json.loads((args.wave_dir / "verified.json").read_text())
    template = load_template()
    prompts_dir, raw_dir = args.wave_dir / "enrich" / "prompts", args.wave_dir / "enrich" / "raw"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    for e in entries:
        siblings = [s for s in entries if s["category"] == e["category"] and s["id"] != e["id"]]
        sibling_text = "\n".join(
            f"- {s['name']} ({s['repo_url']}): beats {s['baseline']}; {(s.get('claimed_speedup') or 'no numbers')[:160]}"
            for s in siblings
        ) or "none catalogued yet"
        record = {k: v for k, v in e.items() if k not in INTERNAL_FIELDS}
        out = (raw_dir / f"{slug(e['id'])}.json").resolve()
        prompt = (template.replace("{TODAY}", today)
                  .replace("{ENTRY_JSON}", json.dumps(record, indent=2)
                           + "\n\nSIBLING ENTRIES (same category, already catalogued):\n" + sibling_text)
                  .replace("{SIBLING_ENTRIES}", "the SIBLING ENTRIES listed under the input record"))
        leftover = set(re.findall(r"\{([A-Z_]+)\}", prompt))
        if leftover:
            raise SystemExit(f"{e['id']}: unfilled variables {sorted(leftover)}")
        prompt += "\n" + HARNESS.format(output_path=out)
        (prompts_dir / f"{slug(e['id'])}.txt").write_text(prompt)
        print(f"{slug(e['id'])}\t{e['name']}")


if __name__ == "__main__":
    main()
