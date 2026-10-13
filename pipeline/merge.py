#!/usr/bin/env python3
"""Merge + dedup a wave's raw search-agent outputs, then regenerate data/known_list.txt."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
KNOWN_SEED = DATA / "known_seed.txt"
KNOWN_LIST = DATA / "known_list.txt"

EXPECTED_KEYS = {
    "name", "repo_url", "language", "domain", "category", "baseline", "baseline_in_list",
    "metric", "workload", "claimed_speedup", "evidence_tier", "benchmark_url", "baseline_stdlib",
    "compiler_and_flags", "hardware", "compared_against_cpp_std_directly", "license", "usability",
    "last_commit", "maintenance_status", "is_fork_of", "stars_or_usage", "has_code", "tradeoffs",
    "caveats", "found_via", "is_evidence_for_known", "confidence",
}
ENUMS = {
    "evidence_tier": {"A", "B", "C", "D"},
    "usability": {"copyable", "reference", "mixed"},
    "maintenance_status": {"active", "stale", "abandoned", "finished", "unknown"},
    "metric": {"throughput", "latency", "compile-time", "build-time", "startup", "memory", "other"},
}
TIER_RANK = {"A": 0, "B": 1, "C": 2, "D": 3}
FORGES = {"github.com", "codeberg.org", "bitbucket.org"}


def canonical(url):
    if not url:
        return None
    if url.startswith("private:"):  # a repository that is not public yet (the private developer source repo)
        return url.strip().lower()
    u = urlparse(url.strip().lower() if "://" in url else "https://" + url.strip().lower())
    host = u.netloc.removeprefix("www.")
    path = u.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = [p for p in path.split("/") if p]
    if host in FORGES:
        parts = parts[:2]
    elif host == "gitlab.com" and "-" in parts:
        parts = parts[: parts.index("-")]
    return "https://" + host + ("/" + "/".join(parts) if parts else "")


def short_name(name):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\(.*?\)", "", name.lower()))


def entry_key(e):
    # an explicit paper: id keeps separate algorithms that share one repo (e.g. SIEVE and S3-FIFO in libCacheSim)
    if str(e.get("id", "")).startswith(("paper:", "lang:", "private:")):
        return e["id"]
    return canonical(e.get("repo_url")) or "paper:" + re.sub(r"[^a-z0-9]+", "-", e["name"].lower()).strip("-")


def read_url_list(path):
    if not path.exists():
        return []
    return [l.strip() for l in path.read_text().splitlines() if l.strip() and not l.startswith("#")]


OPTIONAL_KEYS = {"language_level_claim", "same_algorithm", "same_opt_level", "why_faster"}  # wave 14 cross-language keys (docs/QUEUE.md section C)


def validate(e):
    problems = []
    keys = set(e)
    if keys - EXPECTED_KEYS - OPTIONAL_KEYS:
        problems.append(f"extra keys {sorted(keys - EXPECTED_KEYS - OPTIONAL_KEYS)}")
    if EXPECTED_KEYS - keys:
        problems.append(f"missing keys {sorted(EXPECTED_KEYS - keys)}")
    for field, allowed in ENUMS.items():
        if field in e and e[field] not in allowed:
            problems.append(f"{field}={e[field]!r}")
    return problems


def known_urls(exclude_wave_dir=None):
    urls = {canonical(u) for u in read_url_list(KNOWN_SEED)}
    for f in list(DATA.glob("wave*/merged.json")) + list(DATA.glob("wave*/rejected.json")):
        if exclude_wave_dir and f.parent.resolve() == exclude_wave_dir.resolve():
            continue
        urls |= {e["id"].split("#")[0] for e in json.loads(f.read_text()) if not e["id"].startswith(("paper:", "lang:", "private:"))}
    return urls


def merge(wave_dir, allow_seed=False):
    known = known_urls(exclude_wave_dir=wave_dir)
    if allow_seed:
        known -= {canonical(u) for u in read_url_list(KNOWN_SEED)}
    merged, evidence_for_known, report = {}, [], []

    for raw in sorted((wave_dir / "raw").glob("*.json")):
        try:
            entries = json.loads(raw.read_text())
        except json.JSONDecodeError as err:
            report.append(f"{raw.name}: INVALID JSON ({err})")
            continue
        report.append(f"{raw.name}: {len(entries)} entries")
        for e in entries:
            for p in validate(e):
                report.append(f"  schema {e.get('name')}: {p}")
            key = entry_key(e)
            e["found_via"] = [e["found_via"]] if isinstance(e.get("found_via"), str) else list(e.get("found_via") or [])
            e["assignment_ids"] = [raw.stem]
            if e.get("is_evidence_for_known"):
                evidence_for_known.append(e)
                continue
            if key in known:
                report.append(f"  KNOWN-LIST VIOLATION {e['name']} ({key})")
                continue
            if (key in merged and merged[key]["category"] != e["category"]
                    and short_name(merged[key]["name"]) != short_name(e["name"])):
                # one repo hosting separate libraries in different categories (e.g. UTL)
                key = f"{key}#{e['category']}"
            e["id"] = key
            prev = merged.get(key)
            if prev is None:
                merged[key] = e
                continue
            if short_name(prev["name"]) != short_name(e["name"]):
                report.append(f"  name conflict on {key}: {prev['name']!r} vs {e['name']!r}")
            better, worse = (e, prev) if (TIER_RANK.get(e["evidence_tier"], 9), -e.get("confidence", 0)) < (
                TIER_RANK.get(prev["evidence_tier"], 9), -prev.get("confidence", 0)) else (prev, e)
            better["found_via"] = sorted(set(better["found_via"]) | set(worse["found_via"]))
            better["assignment_ids"] = sorted(set(better["assignment_ids"]) | set(worse["assignment_ids"]))
            merged[key] = better
            report.append(f"  dedup {key} (kept tier {better['evidence_tier']})")

    out = sorted(merged.values(), key=lambda e: (e["category"], TIER_RANK.get(e["evidence_tier"], 9), e["name"].lower()))
    (wave_dir / "merged.json").write_text(json.dumps(out, indent=2) + "\n")
    (wave_dir / "evidence_for_known.json").write_text(json.dumps(evidence_for_known, indent=2) + "\n")
    return out, evidence_for_known, report


def regenerate_known_list():
    urls = known_urls()
    KNOWN_LIST.write_text("# GENERATED by pipeline/merge.py: seed + every merged/rejected entry. Do not edit.\n"
                          + "\n".join(sorted(urls)) + "\n")
    return len(urls)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wave_dir", type=Path)
    ap.add_argument("--allow-seed", action="store_true", help="seed-record pass: keep entries on the seed list")
    args = ap.parse_args()
    out, efk, report = merge(args.wave_dir, args.allow_seed)
    print("\n".join(report))
    by_tier = {}
    for e in out:
        by_tier[e["evidence_tier"]] = by_tier.get(e["evidence_tier"], 0) + 1
    print(f"\nmerged: {len(out)} unique  tiers={dict(sorted(by_tier.items()))}  evidence_for_known: {len(efk)}")
    print(f"known_list.txt: {regenerate_known_list()} urls")


if __name__ == "__main__":
    main()
