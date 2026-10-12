# frg (fastripgrep)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust CLI that indexes a codebase with sparse n-grams to search faster than ripgrep on every tested pattern.

| | |
|---|---|
| **Beats** | ripgrep |
| **Claimed result** | 5.3x faster than ripgrep on a selective literal search (renderUsage: 10ms vs 53ms); faster than ripgrep on all 8 tested pattern types (1.06x-5.3x); grep took 1,553ms vs frg 10ms on the same literal (\~155x, derived from page data); README claims 100% match-count parity with ripgrep. frg timings exclude a one-time index build (\~20-23 s for 9K files). |
| **Workload** | 8 regex/literal/alternation/wildcard patterns searched over the openclaw codebase (9,000 files), case-sensitive, warm cache, output to /dev/null, comparing frg's sparse n-gram index against ripgrep and grep. |
| **Metric** | latency |
| **Compiler and flags** | cargo build --release; no rustc version or CPU-specific flags stated |
| **Adoption** | 16 stars |
| **Last commit** | 2026-03-24 |
| **Links** | [repository](https://github.com/qhkm/fastripgrep) · [benchmark](https://github.com/qhkm/fastripgrep#benchmarks) |

## Verdict

First-party README table on the openclaw codebase (9,000 files, case-sensitive, warm cache, output to /dev/null), built with `cargo build --release` (no rustc version or CPU model stated): frg beat ripgrep on all 8 tested patterns (1.06x-5.3x, e.g. 10ms vs ripgrep's 53ms on a selective literal) and beat grep by roughly 155x on that same literal (1,553ms), excluding the one-time \~20-23s index build. benches/bench.rs only times frg against itself on synthetic 1K/5K-file repos and never runs ripgrep, so the comparison table has no independent, reproducible harness.

## Use it when

- Large, mostly-static codebase (thousands of files) searched repeatedly, where the one-time \~20-23s index build amortizes
- Interactive or AI-agent-driven code search (frg ships Claude Code/Cursor/Codex integration) where sub-100ms per-query latency matters more than a one-off build cost
- Selective literal or alternation queries (function/variable names, `useState|useEffect`) — this is where the README shows the biggest indexed wins (1.7x-5.3x vs ripgrep)
- Environments where the index can be kept current via `frg watch`/`frg update` (\~70ms incremental) rather than rebuilt from scratch each time

## Skip it when

- One-off search of a directory with no existing index — the \~20-23s build cost dominates a single query
- High-churn repos or CI checkouts that are scanned once and discarded, where index upkeep or build time outweighs any per-search gain
- Wildcard/single-byte patterns with no extractable literals — the index can't help there and speedup drops to 1.06x-2.7x, close to ripgrep
- Anywhere an independently reproducible benchmark is required — the ripgrep comparison is a first-party README table only; benches/bench.rs never invokes ripgrep
- Teams unwilling to add a `.frg/` state directory to the repo tree or manage index sync

## How it is fast

It extracts 'sparse n-grams' (variable-length byte substrings selected by a 256x256 byte-pair weight table so a substring's edge pair-weights exceed all interior pair-weights) into an inverted index of xxh3-hashed n-gram to file-ID posting lists, stored as delta-varint-encoded, mmap-friendly binary. A query's mandatory literals are covered by a minimum set of these n-grams, whose posting lists are intersected/unioned to shrink 9,000 files to about 5 candidates before full regex verification. Patterns with no extractable literals (`.*`, single-byte) skip the index and instead use parallel rayon file scanning with SIMD memchr byte search and zero-copy output.

## Compared with alternatives

Same category as ngi and trigrep (both also pair an index with regex search to beat ripgrep); frg's own benchmark covers more pattern types (8, including alternation and wildcard) and ships a maintained replace subcommand plus AI-agent skill integration, but ngi reports larger peak speedups on the Linux kernel (up to 5.9x) and ugrep is the more mature, feature-complete indexed-grep option if proven adoption matters more than novelty.

## Integration

| | |
|---|---|
| **Form** | crate (binary via cargo install / Homebrew tap / source build) |
| **Dependencies** | regex, regex-syntax, rayon, memmap2, memchr, ignore, xxhash-rust, clap, clap_complete, clap_mangen, notify, serde, serde_json, anyhow, fs4, indicatif, is-terminal, glob |
| **Minimum toolchain** | Rust stable, edition 2021; no minimum rustc version pinned in Cargo.toml or CI |
| **Platforms** | CI (GitHub Actions) tests ubuntu-latest and macos-latest only; no Windows CI; no CPU-specific build flags in Cargo.toml |
| **Thread safety** | not documented explicitly; indexing and search are parallelized with rayon and the on-disk index is read via memmap2 |
| **Drop-in for the baseline** | partial — explain: CLI flags mirror a ripgrep subset (-i, -S, -F, -l, -c, -C, --glob, --type, --json) but requires an explicit `frg index` step and adds a .frg/ directory; not a binary swap for rg |

## Gotchas

- Index must exist and be current before indexed search helps; `frg update`/`frg watch` keep it in sync after file changes (README claims \~70ms incremental via overlay/tombstone)
- Adds a `.frg/` directory (generations/&lt;id&gt;/meta.json, postings.bin, lookup.bin, files.bin) to the project tree
- Patterns with no extractable literals bypass the index entirely and fall back to parallel brute-force scanning
- `frg replace` writes only with an explicit `--write` flag (dry-run/diff-preview by default)

## Caveats and trade-offs

First-party README benchmark only; no CPU model, rustc version, or repeat count. benches/bench.rs benchmarks frg indexed vs brute-force search on synthetic 1K/5K-file repos and does not invoke ripgrep, so the ripgrep comparison is not reproducible from the repo. Indexed search vs ripgrep's index-free scan is not like-for-like: frg needs a one-time index build (\~20-23 s for 9K files) and index updates after file changes.

Requires an upfront index build (\~20-23s for 9K files; incremental updates \~70ms via overlay/tombstone); index must be kept in sync (frg update/watch); adds a .frg/ directory to the repo tree; falls back to brute-force scan for patterns with no extractable literals.

## Maintenance

Active as of last commit 2026-03-24 (single maintainer, 16 stars), MIT-licensed, v0.3.0, distributed via crates.io/Homebrew/source — small and copyable to vendor, but young with no third-party benchmark verification yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table vs ripgrep and grep (openclaw, 9K files, warm cache) with no CPU, rustc version, or repeat count; benches/bench.rs is a Criterion suite on synthetic repos that times frg only and never runs ripgrep, so the table has no public harness.
- **Verifier notes:** README numbers match the record; the \~150x vs grep is a ratio, now marked derived. Last commit is 2026-03-24 (record had 2026-09-24), still 'active'; MIT, 16 stars, not fork/archived.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/qhkm/fastripgrep>
  - <https://github.com/qhkm/fastripgrep#benchmarks>
  - <https://github.com/qhkm/fastripgrep/blob/main/benches/bench.rs>
- **Sources the enricher read:**
  - <https://github.com/qhkm/fastripgrep>
  - <https://github.com/qhkm/fastripgrep#benchmarks>
  - <https://github.com/qhkm/fastripgrep/blob/main/Cargo.toml>
  - <https://github.com/qhkm/fastripgrep/blob/main/.github/workflows/ci.yml>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/qhkm/fastripgrep`) · [data/wave3/enrich/raw/github_com_qhkm_fastripgrep.json](../../../data/wave3/enrich/raw/github_com_qhkm_fastripgrep.json) (enrichment confidence 0.6)

</details>
