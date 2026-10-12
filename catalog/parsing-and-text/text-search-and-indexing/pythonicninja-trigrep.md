# trigrep

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · 🟢 active

> Rust CLI that pre-builds a disk-backed trigram index of a repo, then searches only candidate files, beating ripgrep in a first-party benchmark.

| | |
|---|---|
| **Beats** | ripgrep |
| **Claimed result** | \~1.58x faster than ripgrep and \~14.79x faster than grep by mean query time (0.0405s trigrep vs 0.0640s ripgrep vs 0.5990s grep) |
| **Workload** | Search-only benchmark on a clone of git/git (patterns: TODO\|FIXME, ^#include, struct [A-Za-z_][A-Za-z0-9_]\*, parse), 5 timed runs + 1 warmup per pattern per tool, trigram index pre-built before timing (make benchmark). |
| **Metric** | latency |
| **Compiler and flags** | Release build: `make benchmark` depends on `make release` (cargo build --workspace --release), and the script runs target/release/trigrep; no rustc version or RUSTFLAGS stated |
| **Adoption** | 46 stars |
| **Last commit** | 2026-04-30 |
| **Links** | [repository](https://github.com/PythonicNinja/trigrep) · [benchmark](https://github.com/PythonicNinja/trigrep#benchmark) |

## Verdict

First-party README benchmark on a clone of git/git (4 patterns, 5 timed runs + 1 warmup each, index pre-built) reports mean query time 0.0405s for trigrep vs 0.0640s for ripgrep and 0.5990s for grep, i.e. \~1.58x and \~14.79x; medians for trigrep and ripgrep are tied at 0.0500s. Timed with `/usr/bin/time -p` (10ms resolution) over 20 samples; no CPU model or rustc version given, and index build time is excluded.

## Use it when

- Large, mostly-static trees (git.git-scale or bigger) searched repeatedly, so index-build cost amortizes
- AI coding agents or scripted workflows issuing many regex searches per checkout, as the README targets
- Patterns with real literal content (e.g. TODO|FIXME, ^#include) that decompose into selective trigrams
- Need for grep-compatible text output or structured JSON output in the same tool
- Prebuilt-binary install wanted on Linux/macOS (x86_64/aarch64) or Windows (x86_64) without a Rust toolchain

## Skip it when

- One-off or rarely-repeated searches on a tree: index-build time is excluded from the published benchmark and isn't amortized
- Anything requiring code reuse or redistribution rights: no LICENSE file and no license field in either Cargo.toml, so it is reference-only
- Patterns with no extractable literal (bare character classes, anchors, `.`) fall back to a MatchAll node, losing index selectivity
- Decisions resting on the headline 1.58x: trigrep and ripgrep have the same 0.0500s median, so the gap is mean-only and close to the 10ms timer resolution used
- Concurrent or long-lived multi-process use where index staleness/locking matters: thread/process safety around the on-disk index is not documented

## How it is fast

Indexing extracts every overlapping 3-byte trigram per file and writes a sorted, mmap'd lookup table (`lookup.bin`) plus posting lists (`postings.bin`), enabling binary search instead of a byte scan. At query time the regex is parsed into a `regex-syntax` HIR and decomposed into an AND/OR tree of literal trigrams; posting lists are intersected/unioned (smallest-first) to shrink the file set before the real regex engine ever runs. An 8-bit `loc_mask` (byte-offset adjacency) and an 8-bit `next_mask` Bloom filter on the following byte further prune false-positive candidates pre-verification. Indexing itself is parallelized with rayon.

## Compared with alternatives

Pick trigrep over ngi or ugrep-indexer mainly for its Cursor-derived on-disk format (mmap'd trigram lookup + loc/next-mask filtering) rather than for the strength of the evidence: ngi reports 1.7x-5.9x and ugrep-indexer 10x-21x with clearer separation, while trigrep's own numbers show tied medians and only a mean-based 1.58x over ripgrep.

## Integration

| | |
|---|---|
| **Form** | crate (trigrep-index library) + CLI binary (trigrep-cli), plus prebuilt release binaries |
| **Dependencies** | trigrep-cli: clap, regex, regex-syntax, anyhow, colored, rayon, atty. trigrep-index: memmap2, ignore, thiserror, serde, serde_json, rayon, byteorder |
| **Minimum toolchain** | Rust edition 2021 (workspace Cargo.toml), no MSRV stated |
| **Platforms** | x86_64-unknown-linux-gnu, aarch64-unknown-linux-gnu, x86_64-apple-darwin, aarch64-apple-darwin, x86_64-pc-windows-msvc (per release workflow targets) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — default output is grep-compatible and flags mirror grep/ripgrep conventions, but it requires an explicit `trigrep index .` step (or an implicit first-run build) before search, so it is not a binary drop-in replacement |

## Gotchas

- Search auto-builds the index if missing, so a cold first query pays full index-build cost that the published benchmark excludes
- No LICENSE file and no license field in Cargo.toml: code can be read but not legally reused or redistributed
- The next_mask adjacency filter is a Bloom filter (false positives possible, no false negatives); correctness depends on the final real-regex verification pass, not the index alone
- `trigrep status` checks staleness against git HEAD but the index is not auto-refreshed on file edits without rerunning `trigrep index`

## Caveats and trade-offs

No license: there is no LICENSE file and no license field in either Cargo.toml, so usability is reference. CPU model not stated. The script times each run with `/usr/bin/time -p` (10 ms resolution) over 20 samples. trigrep and ripgrep have the same median (0.0500 s), so the \~1.58x gap exists only in the mean. Index build time is excluded (search-only scope).

Requires an explicit `trigrep index .` step before searching; no license file present, so the code can be studied but not legally reused/redistributed.

## Maintenance

Actively maintained (last commit 2026-04-30, 46 stars) but ships with no license, so usability is reference-only rather than reusable/redistributable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmark table on git.git shows mean 0.0405 s (trigrep) vs 0.0640 s (ripgrep) vs 0.5990 s (grep), stated as \~1.58x and \~14.79x. The harness scripts/benchmark.sh is public, but no CPU model or rustc version is stated. These are first-party numbers with partial methodology, so the tier is C.
- **Verifier notes:** The claim matches the README exactly. The win is marginal: the medians are equal, and the timer resolution is close to the measured times. It has 46 stars and its last commit was 2026-04-30.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/PythonicNinja/trigrep>
  - <https://github.com/PythonicNinja/trigrep#benchmark>
  - <https://github.com/PythonicNinja/trigrep/blob/master/scripts/benchmark.sh>
  - <https://github.com/PythonicNinja/trigrep/blob/master/Makefile>
  - <https://github.com/PythonicNinja/trigrep/blob/master/Cargo.toml>
  - <https://github.com/PythonicNinja/trigrep/blob/master/trigrep-cli/Cargo.toml>
  - <https://github.com/PythonicNinja/trigrep/blob/master/trigrep-index/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/PythonicNinja/trigrep>
  - <https://github.com/PythonicNinja/trigrep#benchmark>
  - <https://github.com/PythonicNinja/trigrep/blob/master/Cargo.toml>
  - <https://github.com/PythonicNinja/trigrep/blob/master/trigrep-cli/Cargo.toml>
  - <https://github.com/PythonicNinja/trigrep/blob/master/trigrep-index/Cargo.toml>
  - <https://github.com/PythonicNinja/trigrep/blob/master/algorithm.md>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/pythonicninja/trigrep`) · [data/wave3/enrich/raw/github_com_pythonicninja_trigrep.json](../../../data/wave3/enrich/raw/github_com_pythonicninja_trigrep.json) (enrichment confidence 0.55)

</details>
