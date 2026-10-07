#!/usr/bin/env python3
"""Seed-list mining (QUEUE.md section F): split a curated list's README into sections and render one
mining prompt per section to data/seeds/prompts/<source>__<slug>.txt. The agent writes its JSON array to
data/seeds/raw/<source>__<slug>.json. Sections named in EXCLUDE (GUI, games, books, tutorials, tooling) are skipped."""
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEEDS = ROOT / "data" / "seeds"
EXCLUDE = re.compile(r"gui|game|book|tutorial|article|podcast|talk|^videos$|website|weblog|blog|coding (style|standard)|"
                     r"api design|other awesome|online compiler|debugger|integrated development|ide$|build system|"
                     r"static code|documentation|data visuali|robotics|editor|^learning|job|conference|news|"
                     r"community|contribut|license$|package manager|version control|unit testing|testing$|"
                     r"text editor|user interface|operating system|windows|mobile|platform", re.I)

PROMPT = """You are mining a curated list to produce SEED CANDIDATES for a catalog of
implementations that are faster than a default/incumbent tool. You are NOT
evaluating evidence and NOT deciding whether anything is actually fast. You
are extracting every entry that might plausibly qualify, with enough
metadata that a later agent can go look for proof.

Today's date: {today}
Source URL:   {source_url}
Section:      {section}
Skip list:    /home/user/fastpp/data/known_list.txt (canonical lowercase repo URLs already
              catalogued or seeded; grep it before including an entry; the orchestrator dedups
              again downstream, so when unsure include)

The section text is reproduced below, so you do not need to fetch anything.

=====================================================================
PROCESS
=====================================================================
1. Read the section text below (one list entry per line, markdown links).
2. For EVERY entry in the section, decide: could this plausibly be
   catalogued as faster than some baseline? Include it if ANY of these:
   - the description contains a performance claim (fast, fastest,
     high-performance, outperforms, faster than, low-latency,
     zero-copy, SIMD, lock-free, drop-in replacement, optimized, lightning)
   - the category itself is performance-sensitive (containers, hash
     maps, sorting, JSON, compression, regex, allocators, networking,
     parsing, math/linear algebra, crypto/hashing, image codecs, logging)
   - it is a whole-stdlib or whole-libc replacement (EASTL-like)
   - it is a hand-written asm/SIMD kernel or a WASM port of a native lib
   Exclude only entries that are clearly out of scope: GUI toolkits,
   game engines, IDEs, books, tutorials, blogs, job boards, and anything
   whose job has no performance dimension (e.g. a coding-style guide).
   When in doubt, include; a bad seed costs one cheap search-agent run.
3. For each included entry, map it to a wave and category from the
   catalog taxonomy below and guess the baseline it would be compared
   against. These are guesses; mark confidence accordingly.
4. Extract the license tag if the list provides one inline ("[MIT]",
   "[Boost]", etc.). Do not open the repo to look for one.
5. Skip anything whose canonical URL is in the skip list.

=====================================================================
CATALOG TAXONOMY (wave: categories)
=====================================================================
{taxonomy}

=====================================================================
HARD RULES
=====================================================================
- Do not open the individual repos. Mine only the section text. Volume
  and coverage matter here; verification happens downstream.
- Copy URLs exactly as they appear. Do not fix, guess, or canonicalize
  beyond stripping tracking parameters.
- Do not assign an evidence tier. That field does not exist at this
  stage.
- Never send the user's email, name or other personal identifiers to any
  outside service. Write nothing in the repository except the output file.
- Write ONLY the JSON array to:
    {output_path}
  then check it parses: python3 -c "import json,sys; json.load(open(sys.argv[1]))" {output_path}

=====================================================================
OUTPUT SCHEMA
=====================================================================
[
  {{
    "name": "string",
    "repo_url": "string",
    "listed_description": "the list's own one-line description, verbatim",
    "listed_license": "SPDX-ish tag from the list, or null",
    "performance_claim_in_description": true | false,
    "claim_text": "the specific words that signal a claim, or null",
    "guessed_wave": "e.g. stdlib-replacements",
    "guessed_category": "e.g. hash-maps-sets",
    "guessed_baseline": "e.g. std::unordered_map, or null",
    "found_in": "{source_url}#{section}",
    "confidence": 0.0-1.0
  }}
]

=====================================================================
SECTION TEXT
=====================================================================
{text}
"""


def taxonomy():
    out = []
    for f in sorted((ROOT / "data").glob("wave*/assignments.json")):
        a = json.loads(f.read_text())
        cats = sorted({x["category"] for x in a["assignments"] if "category" in x})
        if cats:
            out.append(f"- {a['domain']}: {', '.join(cats)}")
    return "\n".join(out)


def split_sections(md):
    """Return [(title, text)] for every '## ' or '### ' heading with at least one list entry."""
    sections, cur, buf = [], None, []
    for line in md.splitlines():
        m = re.match(r"^(##|###)\s+(.*)", line)
        if m:
            if cur and any(l.lstrip().startswith(("*", "-")) for l in buf):
                sections.append((cur, "\n".join(buf).strip()))
            cur, buf = m.group(2).strip().strip("#").strip(), []
        elif cur is not None:
            buf.append(line)
    if cur and any(l.lstrip().startswith(("*", "-")) for l in buf):
        sections.append((cur, "\n".join(buf).strip()))
    return sections


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="short source name, e.g. awesome-cpp")
    ap.add_argument("readme", type=Path, help="local copy of the list's README.md")
    ap.add_argument("--url", required=True, help="source URL for found_in")
    ap.add_argument("--today", required=True)
    args = ap.parse_args()
    (SEEDS / "prompts").mkdir(parents=True, exist_ok=True)
    (SEEDS / "raw").mkdir(parents=True, exist_ok=True)
    tax = taxonomy()
    kept, skipped = [], []
    for title, text in split_sections(args.readme.read_text()):
        if EXCLUDE.search(title):
            skipped.append(title)
            continue
        out = (SEEDS / "raw" / f"{args.source}__{slug(title)}.json").resolve()
        p = SEEDS / "prompts" / f"{args.source}__{slug(title)}.txt"
        p.write_text(PROMPT.format(today=args.today, source_url=args.url, section=title, taxonomy=tax,
                                   output_path=out, text=text))
        kept.append((title, len(text), str(p)))
    for t, n, p in kept:
        print(f"{n:6d}  {t}  -> {p}")
    print(f"\nkept {len(kept)} sections, skipped {len(skipped)}: {skipped}")


if __name__ == "__main__":
    main()
