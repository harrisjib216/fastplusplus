# ngi (N-gram Indexed Regex Search)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> CLI that builds a trigram index of a codebase to pre-filter files before ripgrep does the actual regex match.

| | |
|---|---|
| **Beats** | ripgrep |
| **Claimed result** | 1.7x-5.9x faster than ripgrep and 13x-69x faster than grep across the 5 tested patterns on the Linux kernel (e.g. 27ms vs rg's 161ms vs grep's 1866ms for `__attribute__.*section`); 100% match parity with ripgrep (13/13 test queries) |
| **Workload** | 5 regex patterns (attribute macros, function calls, struct names, exported symbols, mutex usage) searched across the Linux kernel source tree (92,916 files) using ngi's trigram index + ripgrep verification, compared against plain ripgrep and grep -r. |
| **Metric** | latency |
| **Compiler and flags** | Not stated for the benchmark; README install instructions use `cargo build --release`; no rustc or ripgrep version stated |
| **Adoption** | 21 stars |
| **Last commit** | 2026-03-24 |
| **Links** | [repository](https://github.com/erogol/ngi) · [benchmark](https://github.com/erogol/ngi#benchmarks) |

## Verdict

First-party README benchmark on the Linux kernel source tree (92,916 files): ngi beat ripgrep by 1.7x-5.9x and grep -r by 13x-69x across 5 regex patterns (e.g. 27ms vs rg's 161ms vs grep's 1866ms for `__attribute__.*section`), with 100% result parity vs ripgrep (13/13 queries). No CPU/hardware, rustc or ripgrep version, or run count is given, and the 16s/146MB one-time index build for the kernel tree is excluded from the reported timings.

## Use it when

- Large trees (tens of thousands of files, Linux-kernel scale) searched repeatedly with the same working copy
- Queries with extractable literal substrings (identifiers, macro/symbol names) rather than pure wildcards or anchors
- ripgrep is already installed and on PATH -- ngi is a pre-filter in front of it, not a replacement matcher
- Selective queries expected to touch well under 10% of files, where the index actually narrows the candidate set
- Agentic/tooling workflows that want JSONL (`--json`) output alongside the speedup

## Skip it when

- Broad/unselective patterns (&gt;10% of files match) -- ngi's own fallback logic hands the whole scan to rg, so no speedup applies
- One-off searches on a tree you won't query again -- index build (16s / 146MB for the Linux kernel) isn't worth it for a single search
- Rapidly-changing or ephemeral checkouts (CI runners, throwaway containers) where keeping `.ngi/` current adds overhead each run
- Patterns with no extractable literals (e.g. `.*`, bare character classes) -- no trigram filtering is possible
- Anything production-critical: v0.1.0, 21 stars, single first-party benchmark, no third-party validation or issue history yet

## How it is fast

Every file is decomposed into 3-byte substrings (trigrams) and stored as an inverted index (trigram -&gt; posting list of files), mmap'd and binary-searched at query time -- the classic trigram-index scheme (Russ Cox / Google Code Search). regex-syntax parses the pattern to extract required literal substrings, whose trigrams are intersected to shrink the candidate set before rg runs at all. If the surviving candidates exceed \~10% of files, ngi skips the index and lets rg's own file walker do a full scan instead. Note: DESIGN.md describes a fancier 'sparse n-gram' weighted/monotonic-stack extraction scheme (inspired by Cursor's blog post), but src/ngram.rs shows the shipped v0.1.0 index is plain fixed-length trigrams hashed with FNV-1a -- the sparse-gram design in the doc isn't what's actually implemented.

## Compared with alternatives

Pick ngi specifically when you already run ripgrep and just want a pre-filtering index layer in front of it (it literally shells out to rg for the match step) with an explicit &gt;10%-match fallback rule; trigrep and frg make similar 'faster than ripgrep' claims without that documented fallback threshold, and none of the three ripgrep-adjacent siblings has more than a first-party README benchmark backing it.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | anyhow, clap, crc32fast, ignore, memmap2, rayon, regex, regex-syntax (Rust, build-time); ripgrep recommended on PATH at runtime, falls back to the built-in regex crate if absent |
| **Minimum toolchain** | Rust edition 2024 (rustc 1.85+); CI builds against Rust stable |
| **Platforms** | CI covers Linux (ubuntu-latest) and macOS (macos-latest) only; Windows is untested and undocumented |
| **Thread safety** | not documented; index build parallelizes file walking/hashing via rayon, and search reads a read-only mmap'd index, but there are no stated guarantees for concurrent writers to the same .ngi/ index |
| **Drop-in for the baseline** | partial — explain: mirrors common ripgrep flags (-i, -l, -f, -C/-A/-B, -m, --json) under `ngi search`, but it is a separate binary/subcommand CLI with its own index directory, not an `rg` alias or wrapper script |

## Gotchas

- DESIGN.md documents a weighted 'sparse n-gram' extraction algorithm that the shipped code does not implement -- src/ngram.rs is plain fixed-length trigrams; don't take the design doc as current behavior
- `.ngi/` must be added to .gitignore manually per the README -- a stale or accidentally-committed index is a footgun
- Falls back to a full rg scan silently whenever a query matches &gt;10% of files; `ngi search --explain` is the only way to see which mode (indexed/rg-fullscan/full-scan/no-index) actually ran
- The FNV-1a trigram hash is pinned by unit tests as part of the on-disk index format, implying a future hash change would need an index rebuild/migration

## Caveats and trade-offs

First-party README benchmark on a named corpus (Linux kernel). The repo has no benchmark harness, and no hardware, rustc/ripgrep version, run count or warm/cold cache state is given. Timings exclude the one-time index build (16 s, 146 MB index for the Linux kernel per README). ngi delegates the regex matching itself to ripgrep; the win comes from trigram pre-filtering of candidate files, and the README says it only helps on selective queries (under 10% of files matching).

Falls back to a full ripgrep scan when more than \~10% of files match a query (index only helps selective queries); index build takes \~16s for the Linux kernel and produces a 146MB index that must be kept current; depends on ripgrep being on PATH for best performance (falls back to a built-in Rust regex engine otherwise).

## Maintenance

Active as of the last commit (2026-03-24) but very early: v0.1.0, 21 stars, MIT-licensed, no third-party benchmark or issue history yet; the codebase is a small single crate (8 source files under src/) so it's easy to vendor or fork if development stalls.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks table (Linux kernel, 92,916 files) shows ngi vs rg vs grep for 5 patterns: 27/42/71/90/95 ms vs rg 160-174 ms, which is 1.7x-5.9x vs rg and 13x-69x vs grep, plus 13/13 match parity. These are first-party numbers. The repo has no benchmark script (only src/ and tests/), and no CPU, rustc/rg version, run count or cache state is given, so the tier is C.
- **Verifier notes:** The numbers match the README exactly. ngi wraps ripgrep (it pre-filters candidates, then rg does the matching), so it is an indexed front-end, not a faster regex engine. It has 21 stars, an MIT license, and its last commit was 2026-03-24.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/erogol/ngi>
  - <https://github.com/erogol/ngi#benchmarks>
- **Sources the enricher read:**
  - <https://github.com/erogol/ngi>
  - <https://github.com/erogol/ngi#benchmarks>
  - <https://github.com/erogol/ngi/blob/main/README.md>
  - <https://github.com/erogol/ngi/blob/main/DESIGN.md>
  - <https://github.com/erogol/ngi/blob/main/CHANGELOG.md>
  - <https://github.com/erogol/ngi/blob/main/Cargo.toml>
  - <https://github.com/erogol/ngi/blob/main/src/lib.rs>
  - <https://github.com/erogol/ngi/blob/main/src/ngram.rs>
  - <https://github.com/erogol/ngi/blob/main/.github/workflows/ci.yml>
  - <https://github.com/erogol/ngi/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/erogol/ngi`) · [data/wave3/enrich/raw/github_com_erogol_ngi.json](../../../data/wave3/enrich/raw/github_com_erogol_ngi.json) (enrichment confidence 0.6)

</details>
