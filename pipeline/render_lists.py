#!/usr/bin/env python3
"""Render the catalog from every wave's verified.json, the enrichment records and data/decisions.json.

Writes:
  catalog/README.md                         index of domains
  catalog/<domain>/README.md                one page per domain: its categories and top picks
  catalog/<domain>/<category>/README.md     one page per category: ranked table of entries
  catalog/<domain>/<category>/<entry>.md    one page per entry
  catalog/rejected.md                       candidates whose evidence did not hold up
  catalog/catalog.jsonl, catalog/catalog.csv   machine-readable exports (schema: docs/schema.md)
  README.md                                 only the blocks between <!-- fastpp:NAME --> and <!-- /fastpp:NAME -->

The output is deterministic, so CI re-runs this script and fails when the committed files differ.
"""
import csv
import hashlib
import io
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from catalog_meta import (CATEGORY_ALIASES, CATEGORY_TITLES, CROSS_LANGUAGE_BASELINE, CROSS_LANGUAGE_DOMAIN,
                          DOMAINS, FEATURED)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CATALOG = ROOT / "catalog"
SPEC = ROOT / "pipeline" / "spec.md"
TIER_RANK = {"A": 0, "B": 1, "C": 2, "D": 3}
TIER_TEXT = {"A": "reproducible public benchmark", "B": "independent or peer-reviewed measurement",
             "C": "first-party claim", "D": "directional, no numbers"}
STATUS_RANK = {"active": 0, "finished": 1, "slow": 2, "mixed": 2, "stale": 3, "unknown": 4, "abandoned": 5}
STATUS_ICON = {"active": "🟢", "finished": "🔵", "slow": "🟡", "mixed": "🟡", "stale": "🟡", "unknown": "⚪",
               "abandoned": "🔴"}
DECISIONS = {d["id"]: d for d in json.loads((DATA / "decisions.json").read_text())}
LEGEND = ("<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent "
          "or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. "
          "Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. "
          "*Study only* means no usable open-source license: read the idea, don't copy the code.</sub>")


# ---------------------------------------------------------------- text helpers

def enrich_slug(entry_id):
    """File name of an entry's enrichment record (data/waveN/enrich/raw/<slug>.json)."""
    return re.sub(r"[^a-z0-9]+", "_", entry_id.removeprefix("https://")).strip("_")


def page_slug(entry_id):
    s = entry_id.removeprefix("https://").removeprefix("http://").removeprefix("github.com/")
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    if len(s) > 80:
        s = s[:70].rstrip("-") + "-" + hashlib.sha1(entry_id.encode()).hexdigest()[:8]
    return s


PROSE_ESCAPES = str.maketrans({"<": "&lt;", ">": "&gt;", "*": "\\*", "~": "\\~", "$": "\\$"})


def esc(text):
    """Data prose to Markdown. Outside code spans, escape what GitHub would otherwise act on: unknown HTML tags
    are dropped, single tildes strike through ("~2x ... ~3x"), dollar pairs become math, asterisks emphasis."""
    parts = re.split(r"(`[^`\n]*`)", str(text or "").replace("\r", ""))
    return "".join(p if i % 2 else p.translate(PROSE_ESCAPES) for i, p in enumerate(parts))


def trunc(text, limit=None):
    t = " ".join(str(text or "").split())
    if limit and len(t) > limit:
        t = t[:limit].rsplit(" ", 1)[0].rstrip(",;:.") + "…"
        if t.count("`") % 2:
            t = t.replace("`", "")
    return t


def cell(text, limit=None):
    return esc(trunc(text, limit)).replace("|", "\\|")


def url(u):
    u = (u or "").strip()
    return f"<{u}>" if re.search(r"[\s()<>]", u) else u


def link(label, target):
    return f"[{label}]({url(target)})" if target else label


def bullets(items):
    return "\n".join(f"- {esc(i)}" for i in items or [] if str(i).strip())


def yes_no(v):
    return {True: "yes", False: "no"}.get(v, "not stated")


def group(n):
    return f"{n:,}"


# ---------------------------------------------------------------- entry facts

def status(e):
    word = re.split(r"[\s:;,(]", (e.get("maintenance_status") or "unknown").strip().lower(), maxsplit=1)[0]
    return word if word in STATUS_RANK else "unknown"


def stars(e):
    m = re.search(r"(\d[\d,.]*)\s*([kKmM])?\+?\s*(?:GitHub\s+)?stars", e.get("stars_or_usage") or "")
    if not m:
        return 0
    n = float(m.group(1).replace(",", ""))
    return int(n * {"k": 1e3, "m": 1e6}.get((m.group(2) or "").lower(), 1))


def lang_short(e):
    lang = re.split(r"\s*\(|;|, | with | plus ", (e.get("language") or "?").strip(), maxsplit=1)[0].strip()
    return lang[:24] or "?"


def copyable(e):
    return e.get("usability") == "copyable"


def license_cell(e):
    lic = cell(e.get("license") or "no license", 28)
    return lic if copyable(e) else f"{lic} (study only)"


def rank_key(e):
    return (TIER_RANK[e["evidence_tier"]], not copyable(e), STATUS_RANK[status(e)], -stars(e), e["name"].lower())


# ---------------------------------------------------------------- loading

def load_entries():
    entries, missing, dropped = [], [], []
    seen = {}
    for vf in sorted(DATA.glob("wave*/verified.json"), key=lambda p: p.parent.name):
        for e in json.loads(vf.read_text()):
            xf = vf.parent / "enrich" / "raw" / f"{enrich_slug(e['id'])}.json"
            if not xf.exists():
                missing.append(e["name"])
                continue
            e = dict(e, _x=json.loads(xf.read_text()), _record=vf.relative_to(ROOT).as_posix(),
                     _enrichment=xf.relative_to(ROOT).as_posix())
            e["category"] = CATEGORY_ALIASES.get(e["category"], e["category"])
            if e["domain"] not in DOMAINS or e["category"] not in CATEGORY_TITLES:
                raise SystemExit(f"no display title for {e['domain']}/{e['category']} ({e['id']}): "
                                 "add it to pipeline/catalog_meta.py")
            if e["id"] in seen:  # one id verified in two waves: keep the earlier verification
                keep = min(seen[e["id"]], e, key=lambda r: (r["verification"].get("date", ""), r["_record"]))
                dropped.append(f"{e['id']} ({seen[e['id']]['_record']} / {e['_record']})")
                entries[entries.index(seen[e["id"]])] = keep
                seen[e["id"]] = keep
                continue
            seen[e["id"]] = e
            entries.append(e)
    used = defaultdict(set)
    for e in sorted(entries, key=lambda e: e["id"]):
        base = s = page_slug(e["id"])
        n = 2
        while s in used[(e["domain"], e["category"])] or s == "readme":
            s, n = f"{base}-{n}", n + 1
        used[(e["domain"], e["category"])].add(s)
        e["_page"] = f"catalog/{e['domain']}/{e['category']}/{s}.md"
    return entries, missing, dropped


def spec_baselines():
    """Category -> (baselines, languages, where they win) from the spec's Part 3 and Part 4 tables."""
    out = {}
    for line in SPEC.read_text().splitlines():
        cols = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("| ") else []
        if len(cols) >= 2 and re.fullmatch(r"[a-z0-9-]+", cols[0]):
            out[cols[0]] = cols[1:]
    return out


def what_they_beat(domain, category, members, spec):
    if domain == CROSS_LANGUAGE_DOMAIN:
        return CROSS_LANGUAGE_BASELINE
    row = spec.get(category)
    if row and not row[0].startswith("("):
        return row[0]
    common = Counter(trunc(e.get("baseline"), 60) for e in members).most_common(3)
    return "; ".join(b for b, _ in common)


# ---------------------------------------------------------------- pages

def rel(from_page, to_path):
    """Relative link from one repo file to another."""
    a, b = Path(from_page).parent.parts, Path(to_path).parts
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    return "/".join([".."] * (len(a) - i) + list(b[i:])) or "."


def crumbs(page, *trail):
    """trail: (label, repo path) pairs ending at the parent of `page`."""
    return "<sub>" + " › ".join(link(label, rel(page, path)) for label, path in trail) + "</sub>"


def tier_counts(es):
    c = Counter(e["evidence_tier"] for e in es)
    return {t: c.get(t, 0) for t in "ABCD"}


def entry_table(page, es, with_category=False):
    head = "| # | Project | What it is | " + ("Category | " if with_category else "") + \
           "Tier | Language | License | Status |"
    rows = [head, "|--:|---|---|" + ("---|" if with_category else "") + ":-:|---|---|---|"]
    for i, e in enumerate(es, 1):
        cat = f" {link(cell(CATEGORY_TITLES[e['category']]), rel(page, Path(e['_page']).parent.as_posix() + '/README.md'))} |" \
            if with_category else ""
        rows.append(f"| {i} | {link('**' + cell(e['name'], 60) + '**', rel(page, e['_page']))} | "
                    f"{cell(e['_x'].get('one_liner'), 170)} |{cat} **{e['evidence_tier']}** | {cell(lang_short(e))} | "
                    f"{license_cell(e)} | {STATUS_ICON[status(e)]} {status(e)} |")
    return "\n".join(rows)


def render_entry(e):
    x, page = e["_x"], e["_page"]
    d, c = e["domain"], e["category"]
    v = e.get("verification") or {}
    dec = DECISIONS.get(e["id"], {})
    out = [f"# {esc(e['name'])}",
           crumbs(page, ("fastpp", "README.md"), ("Catalog", "catalog/README.md"),
                  (DOMAINS[d][0], f"catalog/{d}/README.md"), (CATEGORY_TITLES[c], f"catalog/{d}/{c}/README.md")),
           f"**Tier {e['evidence_tier']}** ({TIER_TEXT[e['evidence_tier']]}) · "
           f"{'Copyable' if copyable(e) else 'Study only'} · `{esc(e.get('language') or '?')}` · "
           f"`{esc(e.get('license') or 'no license')}` · {STATUS_ICON[status(e)]} {status(e)}",
           f"> {esc(x.get('one_liner'))}"]
    facts = [("Beats", e.get("baseline")), ("Claimed result", e.get("claimed_speedup")),
             ("Workload", e.get("workload")), ("Metric", e.get("metric")), ("Hardware", e.get("hardware")),
             ("Compiler and flags", e.get("compiler_and_flags"))]
    if d == CROSS_LANGUAGE_DOMAIN:
        facts += [("Kind", "language-level claim" if e.get("language_level_claim") else "library or program"),
                  ("Same algorithm as the baseline", yes_no(e.get("same_algorithm"))),
                  ("Same optimization level", yes_no(e.get("same_opt_level"))),
                  ("Why it wins", e.get("why_faster"))]
    facts += [("Adoption", e.get("stars_or_usage")), ("Last commit", e.get("last_commit")),
              ("Links", " · ".join(filter(None, [link("repository", e.get("repo_url")) if e.get("repo_url") else "",
                                                 link("benchmark", e.get("benchmark_url"))
                                                 if e.get("benchmark_url") else ""])) or "paper only")]
    out.append("| | |\n|---|---|\n" + "\n".join(f"| **{k}** | {val if k == 'Links' else cell(val)} |"
                                                for k, val in facts if val not in (None, "")))
    sections = [("Verdict", esc(x.get("verified_claims_summary"))),
                ("Use it when", bullets(x.get("when_to_use"))),
                ("Skip it when", bullets(x.get("when_not_to_use"))),
                ("How it is fast", esc(x.get("how_it_is_fast"))),
                ("Compared with alternatives", esc(x.get("pick_this_over_siblings_when")))]
    integ = x.get("integration") or {}
    if integ:
        labels = [("form", "Form"), ("dependencies", "Dependencies"), ("min_toolchain", "Minimum toolchain"),
                  ("platforms", "Platforms"), ("thread_safety", "Thread safety"),
                  ("drop_in_for_baseline", "Drop-in for the baseline")]
        sections.append(("Integration", "| | |\n|---|---|\n" + "\n".join(
            f"| **{label}** | {cell(integ[k] if not isinstance(integ[k], bool) else yes_no(integ[k]))} |"
            for k, label in labels if integ.get(k) not in (None, ""))))
    sections += [("Gotchas", bullets(x.get("gotchas"))),
                 ("Known shortcomings", bullets(dec.get("shortcomings"))),
                 ("Caveats and trade-offs", "\n\n".join(esc(t) for t in (e.get("caveats"), e.get("tradeoffs")) if t)),
                 ("Maintenance", esc(x.get("status_note")))]
    for title, body in sections:
        if body and body.strip():
            out.append(f"## {title}\n\n{body}")
    audit = [f"- **Verification** ({v.get('date', 'undated')}): {esc(v.get('verdict', 'n/a'))}; tier before "
             f"verification {v.get('tier_before', '?')}, tier now {e['evidence_tier']}."]
    if v.get("tier_reason"):
        audit.append(f"- **Tier reason:** {esc(v['tier_reason'])}")
    if v.get("retier"):
        r = v["retier"]
        audit.append(f"- **Retiered** {r.get('from', '?')} to {r.get('to', '?')}: {esc(r.get('reason'))}")
    if v.get("notes"):
        audit.append(f"- **Verifier notes:** {esc(v['notes'])}")
    if e.get("corrected_fields"):
        audit.append("- **Fields the verifier corrected:** " + ", ".join(f"`{k}`" for k in e["corrected_fields"]))
    if dec.get("measurements"):
        audit.append("- **Shortcomings recorded by:** " + esc("; ".join(dec["measurements"])))
    for label, urls in (("Pages the verifier opened", v.get("urls_opened")),
                        ("Sources the enricher read", x.get("sources_read"))):
        if urls:
            audit.append(f"- **{label}:**\n" + "\n".join(
                f"  - <{u}>" if re.fullmatch(r"https?://[^\s<>()]+", u) else f"  - {cell(u)}" for u in urls))
    audit.append(f"- **Raw records:** [{e['_record']}]({rel(page, e['_record'])}) (id `{e['id']}`) · "
                 f"[{e['_enrichment']}]({rel(page, e['_enrichment'])}) (enrichment confidence "
                 f"{x.get('confidence', 'n/a')})")
    out.append("<details>\n<summary><b>Audit trail</b></summary>\n\n" + "\n".join(audit) + "\n\n</details>")
    return "\n\n".join(out) + "\n"


def render_category(d, c, es, spec):
    page = f"catalog/{d}/{c}/README.md"
    t = tier_counts(es)
    n_copy = sum(copyable(e) for e in es)
    lines = [f"# {CATEGORY_TITLES[c]}",
             crumbs(page, ("fastpp", "README.md"), ("Catalog", "catalog/README.md"),
                    (DOMAINS[d][0], f"catalog/{d}/README.md")),
             f"**What these beat:** {cell(what_they_beat(d, c, es, spec))}  \n"
             f"**{len(es)} {'entry' if len(es) == 1 else 'entries'}:** " +
             " · ".join(f"{t[k]} tier {k}" for k in "ABCD") +
             f" · {n_copy} copyable, {len(es) - n_copy} study only"]
    row = spec.get(c)
    if d == CROSS_LANGUAGE_DOMAIN and row and len(row) >= 2:
        lines.append(f"**Languages swept:** {cell(row[0])}  \n**Where they tend to win:** {cell(row[1])}")
    lines += [entry_table(page, es), LEGEND]
    return "\n\n".join(lines) + "\n"


def render_domain(d, by_cat, spec):
    page = f"catalog/{d}/README.md"
    es = [e for c in by_cat for e in by_cat[c]]
    t = tier_counts(es)
    rows = ["| Category | Entries | A | B | C | D | What they beat |", "|---|--:|--:|--:|--:|--:|---|"]
    for c in sorted(by_cat, key=lambda c: CATEGORY_TITLES[c].lower()):
        ct = tier_counts(by_cat[c])
        rows.append(f"| {link(CATEGORY_TITLES[c], f'{c}/README.md')} | {len(by_cat[c])} | " +
                    " | ".join(str(ct[k]) for k in "ABCD") +
                    f" | {cell(what_they_beat(d, c, by_cat[c], spec), 90)} |")
    picks = sorted((e for e in es if e["evidence_tier"] == "A" and copyable(e) and status(e) == "active"),
                   key=lambda e: (-stars(e), e["name"].lower()))[:10]
    lines = [f"# {DOMAINS[d][0]}",
             crumbs(page, ("fastpp", "README.md"), ("Catalog", "catalog/README.md")),
             DOMAINS[d][1],
             f"**{len(es)} entries in {len(by_cat)} categories:** " + " · ".join(f"{t[k]} tier {k}" for k in "ABCD"),
             "\n".join(rows)]
    if picks:
        lines += ["## Most-adopted tier A picks",
                  "Tier A, copyable and actively maintained, ordered by GitHub stars.",
                  entry_table(page, picks, with_category=True)]
    lines.append(LEGEND)
    return "\n\n".join(lines) + "\n"


def render_index(tree, entries, rejected_n, seeds_n):
    page = "catalog/README.md"
    t = tier_counts(entries)
    rows = ["| Domain | Entries | A | B | C | D | Categories |", "|---|--:|--:|--:|--:|--:|---|"]
    for d in DOMAINS:
        if d not in tree:
            continue
        es = [e for c in tree[d] for e in tree[d][c]]
        dt = tier_counts(es)
        cats = " · ".join(link(CATEGORY_TITLES[c], f"{d}/{c}/README.md")
                          for c in sorted(tree[d], key=lambda c: CATEGORY_TITLES[c].lower()))
        rows.append(f"| {link('**' + DOMAINS[d][0] + '**', f'{d}/README.md')} | {len(es)} | " +
                    " | ".join(str(dt[k]) for k in "ABCD") + f" | {cats} |")
    lines = ["# Catalog",
             crumbs(page, ("fastpp", "README.md")),
             f"**{group(len(entries))} verified entries** in {sum(len(tree[d]) for d in tree)} categories across "
             f"{len(tree)} domains: " + " · ".join(f"{group(t[k])} tier {k}" for k in "ABCD") + ".",
             "Every entry names the default it beats, quotes the published numbers, and records what is wrong with "
             "them. Start from a domain or jump straight to a category.",
             "\n".join(rows),
             "## Also here",
             f"- [Rejected claims](rejected.md): {rejected_n} candidates whose evidence did not hold up, with the "
             "reason for each.\n"
             f"- [Seeds without evidence](seeds-no-evidence.md): {seeds_n} projects from curated lists that never "
             "published a comparison against a baseline.\n"
             "- [catalog.jsonl](catalog.jsonl) and [catalog.csv](catalog.csv): every entry in machine-readable form "
             "([schema](../docs/schema.md)).",
             LEGEND]
    return "\n\n".join(lines) + "\n"


def render_rejected(rejected):
    page = "catalog/rejected.md"
    rows = ["| Project | Domain / category | Why it was rejected |", "|---|---|---|"]
    for e in sorted(rejected, key=lambda e: (e["domain"], e["category"], e["name"].lower())):
        v = e.get("verification") or {}
        why = v.get("reject_reason") or v.get("notes") or DECISIONS.get(e["id"], {}).get("reason")
        rows.append(f"| {link('**' + cell(e['name'], 60) + '**', e.get('repo_url'))} | "
                    f"{cell(e['domain'])} / {cell(e['category'])} | {cell(why, 600)} |")
    lines = ["# Rejected claims",
             crumbs(page, ("fastpp", "README.md"), ("Catalog", "catalog/README.md")),
             f"{len(rejected)} candidates failed verification because the evidence itself was invalid: a benchmark "
             "that timed a no-op or a `sleep`, a hard-coded baseline column, a fast path that computed a different "
             "answer, numbers copied from design targets. Weak or first-party evidence is not a reason to reject; "
             "those entries stay in the catalog at a lower tier with their shortcomings written down.",
             "Rejected candidates stay on `data/known_list.txt` so later searches skip them.",
             "\n".join(rows)]
    return "\n\n".join(lines) + "\n"


# ---------------------------------------------------------------- exports

EXPORT_FIELDS = ["id", "name", "domain", "category", "evidence_tier", "usability", "license", "language",
                 "maintenance_status", "repo_url", "benchmark_url", "baseline", "claimed_speedup", "workload",
                 "metric", "hardware", "compiler_and_flags", "caveats", "tradeoffs", "stars_or_usage", "last_commit",
                 "has_code", "language_level_claim", "same_algorithm", "same_opt_level", "why_faster"]
ENRICH_FIELDS = ["one_liner", "what_it_does", "verified_claims_summary", "how_it_is_fast", "when_to_use",
                 "when_not_to_use", "pick_this_over_siblings_when", "integration", "gotchas", "status_note",
                 "confidence"]
CSV_FIELDS = ["id", "name", "domain", "category", "evidence_tier", "usability", "license", "language", "status",
              "stars", "last_commit", "repo_url", "benchmark_url", "baseline", "one_liner", "page"]


def export_record(e):
    rec = {k: e.get(k) for k in EXPORT_FIELDS if k in e}
    rec.update({k: e["_x"].get(k) for k in ENRICH_FIELDS if k in e["_x"]})
    v = e.get("verification") or {}
    rec["shortcomings"] = DECISIONS.get(e["id"], {}).get("shortcomings", [])
    rec["verification"] = {k: v.get(k) for k in ("date", "verdict", "tier_before", "tier_reason", "retier", "notes")
                           if v.get(k) is not None}
    rec["page"] = e["_page"]
    rec["record"] = e["_record"]
    rec["enrichment"] = e["_enrichment"]
    return rec


def write_exports(entries):
    ordered = sorted(entries, key=lambda e: e["id"])
    (CATALOG / "catalog.jsonl").write_text(
        "".join(json.dumps(export_record(e), ensure_ascii=False) + "\n" for e in ordered))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(CSV_FIELDS)
    for e in ordered:
        w.writerow([e["id"], e["name"], e["domain"], e["category"], e["evidence_tier"], e.get("usability"),
                    e.get("license") or "", e.get("language") or "", status(e), stars(e) or "",
                    e.get("last_commit") or "", e.get("repo_url") or "", e.get("benchmark_url") or "",
                    " ".join((e.get("baseline") or "").split()), e["_x"].get("one_liner") or "", e["_page"]])
    (CATALOG / "catalog.csv").write_text(buf.getvalue())


# ---------------------------------------------------------------- README blocks

def readme_blocks(tree, entries, rejected):
    t = tier_counts(entries)
    n_cats = sum(len(tree[d]) for d in tree)
    badge = lambda label, msg, color: (f"<img alt=\"{label}: {msg}\" src=\"https://img.shields.io/badge/"
                                       f"{label.replace(' ', '_')}-{str(msg).replace('-', '--').replace(' ', '_').replace(',', '%2C')}"
                                       f"-{color}\">")
    blocks = {"badges": "<p align=\"center\">\n  " + "\n  ".join([
        badge("verified entries", group(len(entries)), "2ea44f"),
        badge("tier A", group(t["A"]), "1f6feb"),
        badge("categories", n_cats, "8250df"),
        badge("claims rejected", len(rejected), "cf222e"),
        badge("license", "MIT", "blue"),
        f"<a href=\"docs/how-it-was-built.md\">{badge('built with', 'Claude Code', 'd97757')}</a>"]) + "\n</p>"}

    blocks["stats"] = (f"**{group(len(entries))} entries** across **{n_cats} categories** in **{len(tree)} domains** · "
                       f"{group(t['A'])} tier A · {group(t['B'])} tier B · {group(t['C'])} tier C · "
                       f"{group(t['D'])} tier D · {len(rejected)} claims rejected")

    rows = ["| Domain | Entries | Jump to a category |", "|---|--:|---|"]
    for d in DOMAINS:
        if d not in tree:
            continue
        n = sum(len(v) for v in tree[d].values())
        cats = " · ".join(f"{link(CATEGORY_TITLES[c], f'catalog/{d}/{c}/README.md')} {len(tree[d][c])}"
                          for c in sorted(tree[d], key=lambda c: -len(tree[d][c]))[:8])
        more = len(tree[d]) - 8
        if more > 0:
            cats += f" · {link(f'+{more} more', f'catalog/{d}/README.md')}"
        rows.append(f"| {link('**' + DOMAINS[d][0] + '**', f'catalog/{d}/README.md')} | {n} | {cats} |")
    blocks["index"] = "\n".join(rows)

    rows = ["| Need faster… | Pick | What it is | Tier |", "|---|---|---|:-:|"]
    by_id = {e["id"]: e for e in entries}
    for e in (by_id[i] for i in FEATURED if i in by_id):
        rows.append(f"| {link(CATEGORY_TITLES[e['category']], Path(e['_page']).parent.as_posix() + '/README.md')} | "
                    f"{link('**' + cell(e['name'], 50) + '**', e['_page'])} | {cell(e['_x'].get('one_liner'), 160)} | "
                    f"**{e['evidence_tier']}** |")
    blocks["featured"] = "\n".join(rows)

    counts = {
        "search": len(list(DATA.glob("wave*/raw/*.json"))) + len(list(DATA.glob("seeds/raw/*.json"))),
        "verify": len(list(DATA.glob("wave*/verify/raw/batch-*.json"))),
        "retier": len(list(DATA.glob("wave*/verify/raw/retier-*.json"))),
        "enrich": len(list(DATA.glob("wave*/enrich/raw/*.json"))),
        "decisions": len(DECISIONS),
    }
    blocks["pipeline"] = "\n".join([
        "```mermaid",
        "flowchart LR",
        f"  S[\"Search agents<br/>{group(counts['search'])} reports\"] --> M[\"Merge and dedup\"]",
        f"  M --> V[\"Verifier agents<br/>{group(counts['verify'])} batches\"]",
        f"  V --> E[\"Enrichment agents<br/>{group(counts['enrich'])} write-ups\"]",
        f"  E --> R[\"Retier checks and decisions<br/>{counts['retier']} retier files, "
        f"{group(counts['decisions'])} decisions\"]",
        f"  R --> C[\"Catalog<br/>{group(len(entries))} entries\"]",
        f"  V -. invalid evidence .-> X[\"Rejected<br/>{len(rejected)} claims\"]",
        "```"])
    return blocks


def fill_readme(blocks):
    path = ROOT / "README.md"
    text = path.read_text()
    for name, body in blocks.items():
        pattern = re.compile(rf"(<!-- fastpp:{name} -->\n)(?:.*?\n)?(<!-- /fastpp:{name} -->)", re.S)
        if not pattern.search(text):
            raise SystemExit(f"README.md has no <!-- fastpp:{name} --> block")
        text = pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text)
    path.write_text(text)


# ---------------------------------------------------------------- main

def main():
    entries, missing, dropped = load_entries()
    spec = spec_baselines()
    tree = defaultdict(lambda: defaultdict(list))
    for e in sorted(entries, key=rank_key):
        tree[e["domain"]][e["category"]].append(e)

    for sub in [p for p in CATALOG.iterdir() if p.is_dir()] if CATALOG.exists() else []:
        shutil.rmtree(sub)  # every subdirectory is generated; stale entry pages go with it
    CATALOG.mkdir(exist_ok=True)
    for d in tree:
        (CATALOG / d).mkdir()
        (CATALOG / d / "README.md").write_text(render_domain(d, tree[d], spec))
        for c, es in tree[d].items():
            (CATALOG / d / c).mkdir()
            (CATALOG / d / c / "README.md").write_text(render_category(d, c, es, spec))
            for e in es:
                (ROOT / e["_page"]).write_text(render_entry(e))

    rejected = [e for f in sorted(DATA.glob("wave*/rejected.json")) for e in json.loads(f.read_text())]
    seeds = CATALOG / "seeds-no-evidence.md"
    seeds_n = int(m.group(1)) if seeds.exists() and (m := re.search(r"^(\d+) projects", seeds.read_text(), re.M)) else 0
    (CATALOG / "README.md").write_text(render_index(tree, entries, len(rejected), seeds_n))
    (CATALOG / "rejected.md").write_text(render_rejected(rejected))
    write_exports(entries)
    fill_readme(readme_blocks(tree, entries, rejected))

    print(f"catalog: {len(entries)} entries, {sum(len(v) for v in tree.values())} categories, "
          f"{len(rejected)} rejected; missing enrichment: {missing}; duplicate ids kept once: {dropped}")


if __name__ == "__main__":
    main()
