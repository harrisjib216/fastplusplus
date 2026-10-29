# AGENTS.md: using fastpp from a coding agent

fastpp is a catalog of 3,000+ open-source libraries and tools that published measurements showing them faster
than a common default (the C++ standard library, zlib, OpenSSL, malloc, nginx, CPython and so on). Use it when a
user asks for a faster alternative, when profiling points at a standard component, or before recommending a
dependency for speed.

## Where things are

| Path | What it holds |
|---|---|
| `catalog/catalog.jsonl` | Every entry, one JSON object per line. The best source for queries. Schema: `docs/schema.md`. |
| `catalog/catalog.csv` | Summary columns only (name, tier, license, status, baseline, one-liner, page). |
| `catalog/<domain>/<category>/README.md` | Ranked table for one category. |
| `catalog/<domain>/<category>/<entry>.md` | Full write-up for one entry. Link this page when you cite an entry. |
| `catalog/rejected.md` | Claims rejected for invalid evidence. Do not recommend these on the strength of their numbers. |
| `data/` | Raw pipeline records. You rarely need them; the exports already merge them. |

Domains (the `domain` field): `stdlib-replacements`, `toolchain-and-build`, `parsing-and-text`,
`serialization-and-formats`, `networking-and-servers`, `storage-and-data`, `crypto-and-hashing`,
`numerics-and-science`, `compression-and-encoding`, `media-and-graphics`, `runtime-and-systems`,
`interpreters-and-vms`, `assembly-simd-kernels-and-wasm`, `other-languages-faster-than-c-cpp-asm`.
List the categories with `jq -r '"\(.domain)/\(.category)"' catalog/catalog.jsonl | sort -u`.

## How to query

```sh
# Candidates for one category, best evidence first
jq -r 'select(.category == "hash-maps-sets") | [.evidence_tier, .usability, .name, .one_liner] | @tsv' \
   catalog/catalog.jsonl | sort

# Search by the baseline you want to replace
jq -c 'select(.baseline | test("zlib"; "i")) | {name, evidence_tier, category, page}' catalog/catalog.jsonl

# Search by keyword in the name or one-liner
jq -c 'select((.name + " " + .one_liner) | test("utf-?8"; "i")) | {name, evidence_tier, page}' catalog/catalog.jsonl

# Everything you need before recommending one entry
jq 'select(.id == "https://github.com/martinus/unordered_dense")
    | {name, evidence_tier, license, usability, baseline, claimed_speedup, hardware, compiler_and_flags,
       when_to_use, when_not_to_use, gotchas, shortcomings, page}' catalog/catalog.jsonl
```

Without `jq`, `grep '"category": "json"' catalog/catalog.jsonl` works because each entry is one line.

## How to read an entry

1. **Tier first.** A: public benchmark code with compiler, flags and CPU stated (reproducible). B: independent or
   peer-reviewed. C: first-party claim. D: no numbers. Present C and D numbers as the project's claims, not as
   facts. Prefer A and B when several entries fit.
2. **The baseline and the workload decide relevance.** A 5x win on 1 KB messages says little about 1 GB files.
   Check `workload`, `metric` and `hardware` against the user's case.
3. **Shortcomings are part of the answer, not footnotes.** Read `shortcomings`, `caveats`, `when_not_to_use` and
   `gotchas` before recommending anything, and pass the relevant ones on to the user. Many entries are kept on
   purpose despite a serious flaw (not faster in some cases, unsafe for untrusted input, unmaintained).
4. **License.** `usability: copyable` means an OSI license or CC0, so code can be vendored or linked under that
   license. `reference` or `mixed` means study the idea only; do not copy the code.
5. **Maintenance.** `maintenance_status` and `last_commit` were true when the entry was verified; check the
   repository for the current state before adding a dependency.
6. **Derived ratios.** Text marked "(derived from page data)" is a ratio the verifier computed from the source's
   numbers, not one the source stated.

## Answering a user

- Name two or three candidates with tier, the published number, the baseline and the workload, then the main
  reason not to use each.
- Link the entry page (`page` field, for example
  `catalog/stdlib-replacements/hash-maps-sets/martinus-unordered-dense.md`) and the original `benchmark_url`.
- Say plainly that the numbers are published measurements that fastpp has not re-run, and suggest measuring on
  the user's own workload before switching.
- If nothing in the catalog fits, say so rather than stretching an entry from another workload.

## Changing the catalog

Never hand-edit files under `catalog/` or the generated blocks of `README.md`; they are rebuilt by
`build/fastpp render` (build it once with `cmake -B build && cmake --build build`). Changes go into the records under
`data/` (see `CONTRIBUTING.md` and the wave loop in `CLAUDE.md`), and `build/fastpp check-pii` must pass before a
commit.
