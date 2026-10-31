# Catalog schema

<sub>[fastpp](../README.md) › Docs</sub>

The catalog is generated from the records in [`data/`](../data/README.md) by
[`fastpp render`](../src/render.cpp). Two exports carry every entry:

- [`catalog/catalog.jsonl`](../catalog/catalog.jsonl): one JSON object per line, sorted by `id`, all fields below.
- [`catalog/catalog.csv`](../catalog/catalog.csv): one row per entry with the summary columns listed at the end.

Ids are stable across renders. Free-text fields are prose written or corrected by the verifier and enrichment
agents; numbers inside them are quoted from the cited source unless marked "(derived from page data)".

## catalog.jsonl

### Identity and classification

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable id: the canonical repository URL (lowercase), `paper:<slug>` for papers or second claims on a listed repository, `lang:<language>/<owner>/<repo>#<benchmark>` for cross-language benchmark rows, or `private:<name>#<category>` for a repository that is not public yet. |
| `name` | string | Display name, often with the component that was measured. |
| `domain` | string | One of the 14 domains, for example `stdlib-replacements`. |
| `category` | string | Category slug within the domain, for example `hash-maps-sets`. |
| `page` | string | Path of the entry's page under `catalog/`. |
| `record` | string | The `verified.json` file the entry comes from. |
| `enrichment` | string | The enrichment record the prose sections come from. |

### Evidence

| Field | Type | Meaning |
|---|---|---|
| `evidence_tier` | `A` \| `B` \| `C` \| `D` | A: public benchmark code with compiler, flags and CPU stated. B: independent or peer-reviewed. C: first-party. D: directional, no numbers. |
| `baseline` | string | The default the entry claims to beat. |
| `claimed_speedup` | string | The published numbers, as corrected by the verifier. |
| `workload` | string | What was measured. |
| `metric` | string | Throughput, latency, memory and so on. |
| `hardware` | string | CPU or GPU model, when stated. |
| `compiler_and_flags` | string | Toolchain and flags, when stated. |
| `caveats` | string | Problems with the evidence the verifier recorded. |
| `tradeoffs` | string | What the speed costs (features, memory, portability). |
| `shortcomings` | string[] | Known shortcomings recorded in `data/decisions.json` (verifier and enricher findings). |
| `verification` | object | `date`, `verdict` (confirm, downgrade), `tier_before`, `tier_reason`, `notes`, and `retier` (`from`, `to`, `reason`) when a later check moved the tier. |

### Project facts

| Field | Type | Meaning |
|---|---|---|
| `usability` | `copyable` \| `reference` \| `mixed` | `copyable`: an OSI license or a CC0/public-domain dedication, so code can be vendored. Otherwise study the idea only. |
| `license` | string or null | SPDX-style license as found in the repository. |
| `language` | string | Implementation language, sometimes with detail. |
| `maintenance_status` | string | `active`, `stale`, `abandoned`, `finished` or `unknown`, sometimes with a note. |
| `repo_url` | string or null | Repository; null for paper-only entries, `private:<name>` for a repository that is not public yet. |
| `benchmark_url` | string or null | The page the numbers come from. |
| `stars_or_usage` | string | Stars and notable users, as text. |
| `last_commit` | string | Date of the last commit seen (YYYY-MM-DD). |
| `has_code` | boolean | Present and false for paper-only entries. |

### Write-up (from the enrichment record)

| Field | Type | Meaning |
|---|---|---|
| `one_liner` | string | One sentence: what it is and what it beats. |
| `what_it_does` | string | A short description. |
| `verified_claims_summary` | string | The verdict on the evidence, in prose. |
| `how_it_is_fast` | string | The mechanism. |
| `when_to_use` | string[] | Situations where the win holds. |
| `when_not_to_use` | string[] | Situations where it does not, or where it is unsafe. |
| `pick_this_over_siblings_when` | string | How it compares with the alternatives in its category. |
| `integration` | object | `form`, `dependencies`, `min_toolchain`, `platforms`, `thread_safety`, `drop_in_for_baseline`. |
| `gotchas` | string[] | Build, API and correctness traps. |
| `status_note` | string | Maintenance and adoption, in prose. |
| `confidence` | number | The enrichment agent's confidence in its write-up, 0 to 1. |

### Cross-language entries only

Entries in `other-languages-faster-than-c-cpp-asm` compare a language against the same task in C or C++.

| Field | Type | Meaning |
|---|---|---|
| `language_level_claim` | boolean | True when the claim is about the language's compiler or runtime rather than one library. |
| `same_algorithm` | boolean or null | Whether both sides implement the same algorithm. |
| `same_opt_level` | boolean or null | Whether both sides were built at a comparable optimization level. |
| `why_faster` | string or null | The mechanism behind the win. |

## catalog.csv

`id, name, domain, category, evidence_tier, usability, license, language, status, stars, last_commit, repo_url,
benchmark_url, baseline, one_liner, page`

`status` is the first word of `maintenance_status`; `stars` is parsed from `stars_or_usage` and empty when no star
count is given.

## Examples

```sh
# Tier A or B, copyable JSON parsers
jq -c 'select(.category == "json" and (.evidence_tier == "A" or .evidence_tier == "B") and .usability == "copyable")
       | {name, evidence_tier, one_liner, page}' catalog/catalog.jsonl

# Everything that claims to beat std::sort, with its shortcomings
jq -r 'select(.baseline | test("std::sort")) | "\(.evidence_tier) \(.name)\n  " + (.shortcomings | join("\n  "))' \
   catalog/catalog.jsonl

# Count entries per tier
jq -r .evidence_tier catalog/catalog.jsonl | sort | uniq -c
```
