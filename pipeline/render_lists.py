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
           "Entries with a confirmed OSI license: code can be vendored, wrapped, or forked. "
           "Grouped by license family, then category; tier A/B first, tier C/D under *Unverified claims*."]
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

    print(f"COPYABLE.md: {len(copyable)}  REFERENCE.md: {len(reference)}  missing enrichment: {missing}")


if __name__ == "__main__":
    main()
