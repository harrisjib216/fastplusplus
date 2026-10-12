# logos

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Lexers and tokenizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust proc-macro lexer generator: compiles token/regex rules into one DFA with jump tables, aiming to beat hand-written lexers.

| | |
|---|---|
| **Beats** | hand-written lexer |
| **Claimed result** | No paired number from the project: README 'How fast?' lists only logos's own throughput (identifiers 1204 MB/s at 647 ns/iter; keywords/operators/punctuators 1037 MB/s at 2,054 ns/iter; strings 1575 MB/s at 553 ns/iter) and states the goal 'to make the generated Lexer faster than anything you'd write by hand'. Third-party (alic.dev): on Apple M1 over 100KB pseudocode logos 174,476 ns/iter vs the blogger's naive hand-written lexer 312,837 ns/iter (\~1.8x, derived from page data); on x86_64 logos was slower (221,110 vs 201,148 ns/iter); the blogger's optimized hand-written NEON lexer later beat logos by 20-35% |
| **Workload** | Criterion micro-benchmarks tokenizing identifiers, keywords/operators/punctuators, and quoted strings; throughput reported in MB/s |
| **Metric** | throughput |
| **Hardware** | Apple M1 for the third-party comparison (x86_64 CPU unspecified); README throughput numbers give no hardware |
| **Adoption** | 3.6k stars |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/maciejhirsz/logos) · [benchmark](https://alic.dev/blog/fast-lexing) |

## Verdict

Logos's README reports only its own Criterion throughput (identifiers 1204 MB/s, strings 1575 MB/s, keywords/operators/punctuators 1037 MB/s) with no baseline lexer measured in the same run and no hardware or rustc version given. The one paired comparison found, a third-party blog (alic.dev) on an Apple M1 tokenizing a 100KB pseudocode file, showed logos beating a naive hand-written lexer \~1.8x (174,476 vs 312,837 ns/iter) but running about 10% slower than that same hand lexer on an unspecified x86_64 CPU (221,110 vs 201,148 ns/iter); the author's later SIMD-optimized (NEON) hand-written lexer beat logos by 20-35%.

## Use it when

- Building a lexer for a DSL, config format, or query language in Rust and you want a declarative token spec instead of a hand-rolled state machine
- Token set is a regular language expressible as literal tokens and regexes (identifiers, keywords, operators, punctuation, quoted strings)
- Targeting no_std/embedded Rust (logos ships a no_std CI workflow) but still want compile-time generated matching
- Want Criterion-verified throughput (README claims 1000+ MB/s on identifiers/strings) without hand-tuning SIMD yourself
- Fine with proc-macro compile-time cost in exchange for a maintained, widely-used (3.6k-star) crate

## Skip it when

- Grammar needs backtracking, lookahead, or context-sensitive tokenization — logos explicitly forbids backtracking inside token definitions
- Non-Rust project — this is a Rust crate/proc-macro, not usable from C/C++ or other toolchains
- You need proof it beats a specific hand-written lexer: the project publishes no paired benchmark, and the only third-party paired test (alic.dev) shows logos losing \~10% to a naive hand lexer on x86_64 and 20-35% to an optimized SIMD hand lexer
- You want to avoid unsafe code by default — logos uses unsafe internally unless you opt into the `forbid_unsafe` feature, which the README notes may cost performance
- You want a single dependency-free source file to vendor — logos is a workspace of crates (logos, logos-derive, logos-codegen) driven by a proc-macro, not a drop-in header/source file

## How it is fast

All token/regex rules are merged into a single deterministic finite automaton instead of being matched one-by-one, and branches in that DFA are compiled into lookup or jump tables. The codegen unrolls loops and batches byte reads to cut bounds checks, and disallows backtracking inside token definitions (avoiding ReDoS-style regex backtracking cost). All of this happens as proc-macro codegen at compile time, so the generated lexer has no runtime interpretation overhead.

## Compared with alternatives

Pick logos when you want a general-purpose, actively maintained Rust lexer generator with an ergonomic derive-macro API and broad adoption (3.6k stars) rather than a domain-specific tool like CrossDB (SQL only) or Accelerated-Zig-Parser (Zig compiler internals); pick a hand-written or SIMD-tuned lexer instead (e.g. dist1ll's lexer-exp, which reports beating logos by \~35% on Apple M1) when raw throughput against a tuned baseline matters more than developer ergonomics.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | logos-derive (proc-macro, enabled via default `export_derive` feature); no required runtime deps beyond std (std feature can be disabled for no_std) |
| **Minimum toolchain** | Rust 1.80.0 (rust-version in Cargo.toml), edition 2021 |
| **Platforms** | any (no_std supported per CI workflow and crate keywords); no architecture-specific SIMD requirement documented |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — replaces hand-written lexer logic but requires rewriting token definitions as a derive-macro enum, not a source-level drop-in |

## Gotchas

- Default build relies on unsafe code internally; the `forbid_unsafe` Cargo feature swaps in safe alternatives but the README/Cargo.toml note this may reduce performance
- Backtracking inside token definitions is disallowed by design, so overlapping/ambiguous patterns need manual priority handling (see the book's token-disambiguation page)
- A `state_machine_codegen` feature switches between two different codegen backends (tailcall vs. state-machine); behavior and performance can differ between them
- The repo's own bench suite (tests/benches/bench.rs, run via CodSpeed CI) only benchmarks logos itself — no hand-written baseline is run in the same harness, so the README's 'ridiculously fast' framing is not a paired comparison

## Known shortcomings

- Its own README publishes only logos's throughput with no paired baseline; the one head-to-head comparison found (the alic.dev blog) shows mixed results against a hand-written lexer.

## Caveats and trade-offs

'Faster than hand-written' is a design goal; the project publishes no paired benchmark. The only paired evidence found (third-party alic.dev blog) is mixed: logos beat a naive hand-written lexer \~1.8x on Apple M1 but was \~10% slower on x86_64, and lost 20-35% to an optimized hand-written SIMD lexer; no rustc version or CPU model for the README numbers

Requires derive-macro codegen at compile time; combines all tokens into one DFA with lookup/jump tables and unrolled loops; Rust only, less flexible for irregular/ambiguous grammars than a bespoke hand lexer

## Maintenance

Actively maintained (last commit 2026-09-11, v0.16.1 on crates.io, 3,566 stars) and dual MIT/Apache-2.0 licensed, so it's low-risk to depend on directly; it is an ordinary Cargo dependency rather than a header-only file, so 'copyable' here means small enough to vendor, not a single-file drop-in.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README 'How fast?' section lists only logos's own Criterion throughput with no paired baseline, and the repo bench (tests/benches/bench.rs, CodSpeed CI) measures only logos. The only paired comparison found is a third-party blog (alic.dev) with public code, an Apple M1 and no rustc version, and its results are mixed, so C.
- **Verifier notes:** Notable (3,566 stars, widely used crate), but the project's own claim is only a design goal. I pointed benchmark_url at the one page with paired numbers against a hand-written lexer. That evidence is mixed, so the orchestrator may prefer to reject as no-baseline-comparison or not-faster. License: GitHub reports Apache-2.0, but the repo ships LICENSE-MIT and LICENSE-APACHE and the README says dual-licensed, so 'MIT OR Apache-2.0' stands.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/maciejhirsz/logos#how-fast>
  - <https://github.com/maciejhirsz/logos>
  - <https://github.com/maciejhirsz/logos/blob/master/tests/benches/bench.rs>
  - <https://github.com/maciejhirsz/logos/blob/master/.github/workflows/rustbench.yml>
  - <https://github.com/maciejhirsz/logos/blob/master/book/src/intro.md>
  - <https://alic.dev/blog/fast-lexing>
- **Sources the enricher read:**
  - <https://github.com/maciejhirsz/logos>
  - <https://github.com/maciejhirsz/logos#how-fast>
  - <https://github.com/maciejhirsz/logos/blob/master/Cargo.toml>
  - <https://github.com/maciejhirsz/logos/blob/master/tests/benches/bench.rs>
  - <https://alic.dev/blog/fast-lexing>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/maciejhirsz/logos`) · [data/wave3/enrich/raw/github_com_maciejhirsz_logos.json](../../../data/wave3/enrich/raw/github_com_maciejhirsz_logos.json) (enrichment confidence 0.5)

</details>
