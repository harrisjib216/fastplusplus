#!/usr/bin/env python3
"""Render COPYABLE.md and REFERENCE.md from every wave's verified.json + enrichment records."""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TIER_RANK = {"A": 0, "B": 1, "C": 2, "D": 3}
COPYLEFT = re.compile(r"\b(A?GPL|LGPL|MPL|EPL|CDDL|EUPL|OSL)", re.I)


def slug(entry_id):
    return re.sub(r"[^a-z0-9]+", "_", entry_id.removeprefix("https://")).strip("_")


def license_family(spdx):
    options = re.split(r"\s+OR\s+|/", spdx or "")
    return "Permissive" if any(o and not COPYLEFT.search(o) for o in options) else "Copyleft"


def bullets(items):
    return "\n".join(f"- {i}" for i in items)


def render_entry(e, x, with_integration):
    lines = [
        f"##### {e['name']}  `{e['language']}`  `{e['license'] or 'no license'}`  `{e['maintenance_status']}`  `Tier {e['evidence_tier']}`",
        x["one_liner"],
        f"**Beats:** {e['baseline']} — {x['verified_claims_summary']}",
        f"**How:** {x['how_it_is_fast']}",
        f"**Use it when:**\n{bullets(x['when_to_use'])}",
        f"**Skip it when:**\n{bullets(x['when_not_to_use'])}",
    ]
    if with_integration:
        i = x["integration"]
        lines.append(f"**Integration:** {i['form']} · {i['dependencies']} · {i['min_toolchain']} · {i['platforms']}")
    lines.append(f"**Vs siblings:** {x['pick_this_over_siblings_when']}")
    if x.get("gotchas"):
        lines.append(f"**Gotchas:**\n{bullets(x['gotchas'])}")
    lines.append(f"**Status:** {x['status_note']}")
    links = [f"[repo]({e['repo_url']})" if e.get("repo_url") else None,
             f"[benchmark]({e['benchmark_url']})" if e.get("benchmark_url") else None]
    lines.append(" · ".join(l for l in links if l))
    return "\n\n".join(lines)


def section(title, entries, enrich, with_integration):
    out = [f"## {title}"]
    grouped = defaultdict(lambda: defaultdict(list))
    for e in entries:
        grouped[e["domain"]][e["category"]].append(e)
    for domain in sorted(grouped):
        out.append(f"### {domain}")
        for cat in sorted(grouped[domain]):
            out.append(f"#### {cat}")
            for e in sorted(grouped[domain][cat], key=lambda e: (TIER_RANK[e["evidence_tier"]], e["name"].lower())):
                out.append(render_entry(e, enrich[e["id"]], with_integration))
    return out


def main():
    entries, enrich, missing = [], {}, []
    for vf in sorted(DATA.glob("wave*/verified.json")):
        for e in json.loads(vf.read_text()):
            xf = vf.parent / "enrich" / "raw" / f"{slug(e['id'])}.json"
            if not xf.exists():
                missing.append(e["name"])
                continue
            enrich[e["id"]] = json.loads(xf.read_text())
            entries.append(e)

    copyable = [e for e in entries if e["usability"] == "copyable"]
    reference = [e for e in entries if e["usability"] != "copyable"]
    verified = lambda es: [e for e in es if e["evidence_tier"] in ("A", "B")]
    unverified = lambda es: [e for e in es if e["evidence_tier"] not in ("A", "B")]

    doc = ["# Copyable",
           "Entries with a confirmed OSI license or a CC0/public-domain dedication: code can be vendored, wrapped, "
           "or forked. Grouped by license family, then domain and category; tier A/B first, tier C/D under "
           "*Unverified claims*."]
    for fam in ("Permissive", "Copyleft"):
        fam_entries = [e for e in copyable if license_family(e["license"]) == fam]
        if verified(fam_entries):
            doc += section(fam, verified(fam_entries), enrich, True)
        if unverified(fam_entries):
            doc += section(f"{fam} — Unverified claims (tier C/D)", unverified(fam_entries), enrich, True)
    (ROOT / "COPYABLE.md").write_text("\n\n".join(doc) + "\n")

    doc = ["# Reference",
           "No license, unclear/non-OSI license, mixed licensing, or paper-only. Study the idea and reimplement "
           "clean-room; do not copy the code."]
    if verified(reference):
        doc += section("Verified", verified(reference), enrich, False)
    if unverified(reference):
        doc += section("Unverified claims (tier C/D)", unverified(reference), enrich, False)
    (ROOT / "REFERENCE.md").write_text("\n\n".join(doc) + "\n")

    rejected = [e for f in sorted(DATA.glob("wave*/rejected.json")) for e in json.loads(f.read_text())]
    (ROOT / "REJECTED.md").write_text(render_rejected(rejected))
    (ROOT / "README.md").write_text(render_readme(entries, copyable, reference, rejected))

    print(f"COPYABLE.md: {len(copyable)}  REFERENCE.md: {len(reference)}  REJECTED.md: {len(rejected)}  "
          f"missing enrichment: {missing}")


def cell(text):
    return (text or "").replace("|", "\\|").replace("\n", " ")


def render_rejected(rejected):
    rows = ["# Rejected",
            "Candidates that failed verification. They stay on `data/known_list.txt` so later search waves "
            "skip them instead of rediscovering them.",
            "| Name | Repo | Domain / category | Reason | Verifier notes |",
            "|---|---|---|---|---|"]
    for e in sorted(rejected, key=lambda e: (e["domain"], e["category"], e["name"].lower())):
        v = e.get("verification", {})
        link = f"[repo]({e['repo_url']})" if e.get("repo_url") else "paper"
        rows.append(f"| {cell(e['name'])} | {link} | {e['domain']} / {e['category']} | "
                    f"{cell(v.get('reject_reason'))} | {cell(v.get('notes'))} |")
    return "\n\n".join(rows[:2]) + "\n\n" + "\n".join(rows[2:]) + "\n"


def render_readme(entries, copyable, reference, rejected):
    counts = defaultdict(lambda: defaultdict(int))
    for e in entries:
        key = (e["domain"], e["category"])
        counts[key][e["evidence_tier"]] += 1
        counts[key]["n"] += 1
    table = ["| Domain | Category | Entries | A | B | C | D |", "|---|---|---|---|---|---|---|"]
    for (domain, cat) in sorted(counts):
        c = counts[(domain, cat)]
        table.append(f"| {domain} | {cat} | {c['n']} | {c['A']} | {c['B']} | {c['C']} | {c['D']} |")
    tiers = defaultdict(int)
    for e in entries:
        tiers[e["evidence_tier"]] += 1
    return f"""# fastpp: faster than the default

A catalog of libraries and tools that are measurably faster than the incumbent developers reach for by
default: the C++ standard library, GCC/Clang/ld, zlib, OpenSSL and so on. Every entry names the baseline it
beats, quotes the speedup from its source, and carries an evidence tier. A separate verifier re-checked each
claim against the cited page before it was written up.

## Lists

- [COPYABLE.md](COPYABLE.md): {len(copyable)} entries under an OSI license or CC0. Code can be vendored or forked.
- [REFERENCE.md](REFERENCE.md): {len(reference)} entries with no, unclear, or non-OSI license. Study the idea; don't copy the code.
- [REJECTED.md](REJECTED.md): {len(rejected)} candidates that failed verification.

Tiers across both lists: A {tiers['A']}, B {tiers['B']}, C {tiers['C']}, D {tiers['D']}.

## Evidence tiers

- **A**: public benchmark code, run against the named baseline, with compiler, flags and CPU model all stated
  (whoever ran it).
- **B**: peer-reviewed paper or well-known independent benchmark suite that falls short of A.
- **C**: numbers from the project itself without full methodology, or numbers without methodology. Listed under
  *Unverified claims*.
- **D**: no numbers; kept only for notable projects.

Ratios marked "(derived from page data)" were computed from numbers on the cited page, not quoted.

## Coverage

{chr(10).join(table)}

## How entries are made

Search agents look for candidates per domain × category × source; a merge step dedups them; an Opus
verifier opens each cited benchmark and re-derives the tier; a Sonnet enrichment agent reads the repo and
writes the entry. Prompts and rules: [faster-than-std-agent-prompt.md](faster-than-std-agent-prompt.md);
scripts: [pipeline/](pipeline/); raw records: [data/](data/).

Speedups are the authors' or third parties' published numbers. None has been re-run on our own hardware yet
(that is the planned code-audit stage).

Regenerate the lists with `python3 pipeline/render_lists.py`.
"""


if __name__ == "__main__":
    main()
