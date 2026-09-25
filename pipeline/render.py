#!/usr/bin/env python3
"""Render search-agent prompts (Part 2 template) for every assignment in a wave manifest."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "faster-than-std-agent-prompt.md"
KNOWN_LIST = ROOT / "data" / "known_list.txt"
KNOWN_SEED = ROOT / "data" / "known_seed.txt"

HARNESS = """
=====================================================================
ORCHESTRATOR HARNESS NOTES (environment-specific; these override only
the output-delivery rule above)
=====================================================================
- Tools: WebSearch and WebFetch (if they are not loaded yet, load them
  with ToolSearch query "select:WebSearch,WebFetch"). The `gh` CLI is
  authenticated; use it for GitHub metadata and content:
    gh search repos "<query>" --sort stars --limit 30
    gh search repos "<query>" --sort updated --limit 30
    gh api repos/OWNER/REPO          (license.spdx_id, stargazers_count,
                                      archived, fork, parent.html_url)
    gh api "repos/OWNER/REPO/commits?per_page=1"   (last commit date)
    gh api repos/OWNER/REPO/readme -H "Accept: application/vnd.github.raw"
    gh api repos/OWNER/REPO/contents/PATH -H "Accept: application/vnd.github.raw"
  Fetching a page's content through gh counts as opening its github.com URL.
  `gh search` shares a 30-requests/minute limit with other agents running in
  parallel. If it reports a rate limit, do not retry in a loop: switch to
  WebSearch for discovery and keep using `gh api repos/...` (5000/hour).
- WebSearch has a per-session budget shared by all agents. If it fails as
  exhausted, do not retry; use WebFetch on public search endpoints instead:
    http://export.arxiv.org/api/query?search_query=all:<terms>&max_results=20
    https://api.semanticscholar.org/graph/v1/paper/search?query=<terms>&fields=title,url,year,externalIds&limit=20
    https://hn.algolia.com/api/v1/search?query=<terms>&tags=story
  (Reddit and Lobsters block automated fetches.)
- Do not clone repositories or build anything; this is a search task.
- Never send the user's email address, name or any other personal identifier to an
  outside service (URLs, headers, payloads). For APIs that want a User-Agent, such as
  crates.io, use exactly: User-Agent: fastpp-research-bot/1.0
- For papers and Hacker News, prefer the arXiv / Semantic Scholar / HN Algolia
  endpoints above over WebSearch; save WebSearch for blogs, talks and pages
  those APIs don't index.
- Budget: about 150 tool calls. Token cost is not a concern; stop when queries
  stop surfacing new items, not to save calls.
- Deliver your output by writing the JSON array, and nothing else, to:
    {output_path}
  Then check it parses:
    python3 -c "import json,sys; json.load(open(sys.argv[1]))" {output_path}
- Your final reply to the orchestrator is one line: entry count and names.
"""


def load_template():
    text = SPEC.read_text()
    part2 = text.index("## Part 2")
    start = text.index("```\n", part2) + 4
    end = text.index("\n```", start)
    return text[start:end]


def load_known():
    path = KNOWN_LIST if KNOWN_LIST.exists() else KNOWN_SEED
    return [l.strip() for l in path.read_text().splitlines() if l.strip() and not l.startswith("#")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wave_dir", type=Path)
    ap.add_argument("--ids", nargs="*", help="only render these assignment ids")
    ap.add_argument("--batch", help="only render assignments in this batch")
    args = ap.parse_args()

    manifest = json.loads((args.wave_dir / "assignments.json").read_text())
    template = load_template()
    known = "\n".join(load_known())
    prompts_dir = args.wave_dir / "prompts"
    raw_dir = args.wave_dir / "raw"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    for a in manifest["assignments"]:
        if (args.ids and a["id"] not in args.ids) or (args.batch and a["batch"] != args.batch):
            continue
        values = {
            "TODAY": manifest["today"],
            "DOMAIN": manifest["domain"],
            "CATEGORY": a["category"],
            "BASELINES": a["baselines"],
            "SOURCE": a["source"],
            "LANGUAGE_FILTER": a["language_filter"],
            "SEED_QUERY": a["seed_query"],
            "KNOWN_LIST": known,
            "MAX_ENTRIES": str(a.get("max_entries", manifest["max_entries"])),
        }
        prompt = re.sub(r"\{([A-Z_]+)\}", lambda m: values.get(m.group(1), m.group(0)), template)
        leftover = set(re.findall(r"\{([A-Z_]+)\}", prompt))
        if leftover:
            raise SystemExit(f"{a['id']}: unfilled variables {sorted(leftover)}")
        output_path = (raw_dir / f"{a['id']}.json").resolve()
        prompt += "\n" + HARNESS.format(output_path=output_path)
        (prompts_dir / f"{a['id']}.txt").write_text(prompt)
        print(prompts_dir / f"{a['id']}.txt")


if __name__ == "__main__":
    main()
