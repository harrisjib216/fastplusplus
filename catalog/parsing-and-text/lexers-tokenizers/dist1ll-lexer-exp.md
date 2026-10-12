# lexer-exp (SIMD NEON lexer experiments, dist1ll)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Lexers and tokenizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MPL-2.0` · 🟡 stale

> Hand-rolled NEON SIMD lexer for a toy language; beats the Rust logos crate 20-35% on Apple M1.

| | |
|---|---|
| **Beats** | logos (Rust lexer-generator crate, v0.13) |
| **Claimed result** | Apple M1, 100KB synthetic pseudocode: author reports 'a consistent speedup of 35% over logos' for the final NEON lexer (page shows 118,476 ns/iter, printed under a 'logos:' label that appears to be a typo, vs logos 174,476 ns/iter); on more realistic Hubris kernel snippets lnpl 89,151 ns/iter vs logos 108,257 ns/iter (\~1.21x, derived from page data); author reports a 20%-30% speedup over logos across 5KB-1MB files. The 312,837 vs 174,476 ns/iter pair is the author's original naive lexer vs logos, i.e. logos was \~1.8x faster than that naive version |
| **Workload** | Tokenizing \~100KB of synthetic pseudocode (\~8k lines) and, in a follow-up, real-world source snippets from Oxide's Hubris kernel (5KB-1MB files), using a hand-rolled SIMD lexer built with ARMv8 NEON intrinsics and perfect-hash keyword matching |
| **Metric** | throughput |
| **Hardware** | Apple M1 for all SIMD/NEON lexer results (the lexer is aarch64-only); an early naive-vs-logos run also used unspecified x86_64 hardware |
| **Compiler and flags** | Rust nightly (version not stated; .cargo/config.toml sets rustflags = -Zpolonius), cargo bench / --release |
| **Adoption** | 24 stars |
| **Last commit** | 2024-04-01 |
| **Links** | [repository](https://github.com/dist1ll/lexer-exp) · [benchmark](https://alic.dev/blog/fast-lexing) |

## Verdict

First-party `cargo bench` results (unpinned Rust nightly, single Apple M1 machine) show lnpl's NEON lexer at 118,476 ns/iter vs logos 0.13 at 174,476 ns/iter tokenizing a 100KB synthetic pseudocode file (\~35% faster), and 89,151 ns/iter vs logos's 108,257 ns/iter (\~1.21x) on real Hubris-kernel source snippets (5KB-1MB); the author separately reports 20-30% gains across that Hubris file-size range.

## Use it when

- You're targeting aarch64 (Apple Silicon or ARM servers) specifically -- there is no x86_64 SIMD path
- You want a worked example of NEON-based ASCII token classification plus perfect-hash keyword matching to adapt into your own lexer
- Your token stream is dominated by short, repetitive keyword/identifier patterns, where the gain over logos is largest (\~35% on the synthetic benchmark)
- You can build with an unpinned Rust nightly and are comfortable vendoring unsafe/asm source rather than depending on a published crate
- Throughput on medium files (5KB-1MB) matters more than lexer generality or ergonomics

## Skip it when

- x86_64 targets: the author's own numbers show the naive scalar lexer beating logos there, and no NEON-equivalent path exists
- You need a drop-in replacement for logos's `#[derive(Logos)]` API -- lnpl's token types are hardcoded to the author's toy language
- You need stable Rust: the crate uses `#![feature(core_intrinsics)]` and `#![feature(stdsimd)]`, unstable nightly-only features
- You need a maintained dependency: no crates.io release found, last commit April 2024, no README, and it's explicitly experimental research code
- Your workload looks like realistic, non-repetitive source rather than synthetic pseudocode -- the measured gain shrinks from \~35% to \~20% on the real Hubris kernel snippets

## How it is fast

The aarch64 path loads input in 512-byte chunks into an aligned SIMD buffer and uses NEON 128-bit vector loads to classify 16 ASCII bytes at once (ident/whitespace/number/etc. character classes), with hand-written NEON assembly (aarch64.s) pulled in via global_asm!. Keyword matching uses a perfect hash that packs each keyword into a 64-bit word for single-instruction comparison instead of a DFA/trie walk. The author also reports a 5-10% gain from replacing a computed classification mask with a precomputed lookup table.

## Compared with alternatives

None of the catalogued siblings target Rust + logos on aarch64, so this is the only entry showing that specific pairing; pick it only as a technique reference for NEON ASCII classification + perfect-hash keywords, not as an installable lexer -- for an actual drop-in tokenizer, Accelerated-Zig-Parser or simd-lexing are more complete SIMD lexers, and logos itself (already catalogued) remains the safer general-purpose choice off aarch64.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | logos 0.13 (used only for parity testing / bench comparison, not by the aarch64 lexer itself) |
| **Minimum toolchain** | Rust nightly (unpinned; requires core_intrinsics + stdsimd unstable features; .cargo/config.toml sets rustflags = -Zpolonius) |
| **Platforms** | aarch64 (NEON) for the benchmarked/optimized path; a generic fallback exists for other architectures but is not benchmarked or discussed |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial -- different Token/TokenKind API from logos's derive-macro model; you'd port token definitions, not swap a dependency |

## Gotchas

- Contains raw NEON assembly (aarch64.s) loaded via global_asm! plus unsafe SIMD intrinsics -- review before vendoring
- Uses a fixed 512-byte, 128-byte-aligned SIMD input buffer (SimdBuffer); behavior at buffer boundaries wasn't verified in this review
- Depends on nightly-only, unstable compiler features (core_intrinsics, stdsimd) with no pinned rustc version
- The published benchmark numbers on the blog labeled the lnpl result 'logos:' (apparent typo) -- read the repo's bench source (benches/lexer.rs), not just the blog table, to confirm which number is which

## Caveats and trade-offs

Experimental aarch64/NEON-only research crate ('lnpl'), not a packaged library; paired numbers are first-party cargo bench results on one machine; rustc version not stated; the headline 118,476 ns/iter line is labeled 'logos:' on the page (apparently a typo for lnpl); the gain over logos shrinks from \~35% on synthetic pseudocode to \~20% on realistic Hubris source

ARM NEON-specific code path (author notes x86_64 needs separate treatment); result is workload-dependent, sometimes losing to logos on realistic (non-repetitive) source; experimental research code from a personal compiler project, not a packaged library

## Maintenance

Stale since April 2024 with zero open issues and no crates.io listing found; MPL-2.0 licensed research code from a personal toy-compiler project, small enough to vendor the lexer module but not maintained or packaged as a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** The blog gives paired cargo-bench ns/iter numbers against logos on an Apple M1, and the benchmark code is public (benches/lexer.rs, reproduction commit 94499e0). The rustc version is not stated (an unpinned nightly, since -Zpolonius is set in .cargo/config.toml), so this is first-party C, not A.
- **Verifier notes:** The record misread the page. 174,476 vs 312,837 ns/iter is logos vs the author's naive lexer, not the SIMD lexer vs naive. On Hubris data lnpl (89,151 ns) is faster than logos (108,257 ns), not 18% slower. The author concludes the lexer beats logos by at least 20%. The entry is real, but the claim and caveats needed rewriting.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://alic.dev/blog/fast-lexing>
  - <https://github.com/dist1ll/lexer-exp>
  - <https://github.com/dist1ll/lexer-exp/blob/main/Cargo.toml>
  - <https://github.com/dist1ll/lexer-exp/blob/main/.cargo/config.toml>
  - <https://github.com/dist1ll/lexer-exp/tree/main/benches>
- **Sources the enricher read:**
  - <https://github.com/dist1ll/lexer-exp>
  - <https://alic.dev/blog/fast-lexing>
  - <https://github.com/dist1ll/lexer-exp/blob/main/Cargo.toml>
  - <https://github.com/dist1ll/lexer-exp/blob/main/.cargo/config.toml>
  - <https://github.com/dist1ll/lexer-exp/blob/main/src/lib.rs>
  - <https://github.com/dist1ll/lexer-exp/blob/main/src/lexer/mod.rs>
  - <https://github.com/dist1ll/lexer-exp/blob/main/src/lexer/aarch64.rs>
  - <https://github.com/dist1ll/lexer-exp/blob/main/benches/lexer.rs>
  - https://github.com/dist1ll/lexer-exp/tree/main (file tree)
  - <https://github.com/dist1ll/lexer-exp/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/dist1ll/lexer-exp`) · [data/wave3/enrich/raw/github_com_dist1ll_lexer_exp.json](../../../data/wave3/enrich/raw/github_com_dist1ll_lexer_exp.json) (enrichment confidence 0.65)

</details>
