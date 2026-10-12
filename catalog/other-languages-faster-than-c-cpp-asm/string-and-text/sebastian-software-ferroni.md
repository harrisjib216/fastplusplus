# Ferroni (Rust port of the Oniguruma regex engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `BSD-2-Clause` · 🟢 active

> Pure-Rust port of the Oniguruma regex engine and the vscode-oniguruma scanner; about 2.2x faster than C Oniguruma on everyday searches and 12x on TextMate highlighting replays.

| | |
|---|---|
| **Beats** | Oniguruma (C); also PCRE2 interpreter, PCRE2 JIT, Onigmo, Rust regex and fancy-regex measured |
| **Claimed result** | README table (geometric means over both hosts, measured 2026-10-09): versus Oniguruma (C) 2.2x faster on 32 everyday-pattern tasks, 1.4x faster on 17 advanced-pattern tasks, 12x faster on 3 syntax-highlighting documents (C, Java, PHP scanner replays). Raw per-host summaries: everyday 2.12x on AMD EPYC and 2.39x on Apple M4 Pro, advanced 1.28x and 1.45x, highlighting documents 9.96x to 17.58x (EPYC) and 8.54x to 14.52x (M4 Pro) (derived from page data). C Oniguruma still wins some tasks on EPYC: regex_tasks rfc5322_emails 0.67, ipv6_addresses 0.64, csv_last_column_backtracking 0.89, email_validation 0.96, html_attribute_values 0.92, markdown_emphasis 0.90, password_rules 0.91, absent_comments 0.78, and C compiles several patterns 2x to 4x faster (compilation__lookbehind 0.27, ts_279_compile 0.48). Versus PCRE2 interpreter 1.7x / 1.4x / 28x faster (only tasks it can run), versus PCRE2 JIT 2.1x slower / 3.5x slower / 9.7x faster, versus Rust regex 1.5x slower on everyday patterns, versus Onigmo 2.6x / 1.5x / 34x faster. |
| **Workload** | Geometric mean over 32 'everyday pattern' tasks (search and extraction in HTML, logs, chat, Markdown, JSON, CSV, source code), 17 'advanced pattern' tasks (look-around, backreferences, possessive groups, subexpression calls, absent expressions, grapheme clusters) and 3 TextMate syntax-highlighting documents (C, Java, PHP), on two machines; each engine must first reproduce Oniguruma's results. |
| **Metric** | throughput |
| **Hardware** | Blacksmith CI runners: blacksmith-6vcpu-macos-26 (Apple M4 Pro, virtual, 6 vCPUs, 24 GB, macOS 26.3) and blacksmith-4vcpu-ubuntu-2404 (AMD EPYC with AVX-512, exact model not given, 4 vCPUs, 16 GB, Ubuntu 24.04.4, kernel 6.6.141); Criterion 3 s measurement, 0.5 s warm-up, 30 samples; workflow runs 37989957431 and 37999607702 on 2026-10-09. |
| **Compiler and flags** | rustc 1.99.0 (LLVM 23.1.1), cargo bench --locked --features onigmo (bench profile: default opt-level 3, lto = "thin"); C Oniguruma at pinned commit f95747b462de672b6f8dbdeb478245ddf061ca53 compiled by build.rs through the cc crate with opt_level(3) (-O3), hand-written config.h, by cc (Ubuntu 13.3.0-6ubuntu2\~24.04.1) 13.3.0 on Linux and Apple clang 21.0.0 on macOS; PCRE2 linked statically (PCRE2_SYS_STATIC=1). Receipts in benches/results/blacksmith-2026-10-09-37989957431/\*/measurements.json. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 8 stars, 3 forks; crates.io 6,325 downloads (ferroni 2.1.0, published 2026-10-10) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/sebastian-software/ferroni) · [benchmark](https://github.com/sebastian-software/ferroni/tree/main/benches/results/blacksmith-2026-10-09-37989957431) |

## Verdict

Author-run Criterion means (30 samples) on Blacksmith CI runners on 2026-10-09: an Apple M4 Pro (virtual, macOS 26.3) and an unnamed AMD EPYC with AVX-512 (Ubuntu 24.04). Ferroni was built with rustc 1.99.0 and thin LTO; C Oniguruma (pinned commit f95747b) was built at -O3 by GCC 13.3.0 or Apple clang 21.0.0, and the vscode-oniguruma C scanner was used for the replays. Every engine was validated against C's matches before timing. Geomean over both hosts: 2.2x faster than C on 32 everyday tasks (2.12x EPYC, 2.39x M4 Pro), 1.4x on 17 advanced tasks, and about 12x on the C, Java and PHP Shiki replays (8.5-17.6x per document).

## Use it when

- TextMate-grammar syntax highlighting or tokenizing in Rust (a Shiki or vscode-textmate equivalent): the scanner replays of real Shiki calls for the C, Java and PHP grammars ran 8.5-17.6x faster than the vscode-oniguruma C scanner.
- Replacing a C Oniguruma dependency (via the onig crate or FFI) to drop the C toolchain and C memory-safety exposure, when your subjects are UTF-8 or ASCII.
- Patterns the regex crate cannot express (look-behind, backreferences, possessive and atomic groups, \G, recursion, absent operator) on search and extraction work over kilobyte-to-megabyte documents.
- Untrusted or hostile patterns and input, where per-search time, retry and stack limits plus the compile-time catastrophic-backtracking check matter.

## Skip it when

- Patterns that fit the regex crate: regex was 1.5x faster on the everyday set and guarantees linear time; PCRE2 JIT was 2.1x faster on everyday and 3.5x faster on advanced patterns among the tasks it could run.
- Workloads dominated by compiling patterns, such as one-shot highlighting of a short snippet: C Oniguruma compiled some grammars 2-3x faster (ts_279_compile 0.53, rust_81_compile 0.35 on EPYC), and some single tasks still favour C (rfc5322_emails 0.67, ipv6_addresses 0.64 on EPYC).
- Non-UTF-8 encodings (27 of Oniguruma's 29 are not ported, e.g. PHP mbregex with EUC-JP or Shift_JIS) or code that needs the POSIX/GNU regcomp/regexec APIs.
- Exact error parity on runaway patterns: where a Rust-only filter leaves out an attempt that would have exhausted the retry limit, C reports ONIGERR_RETRY_LIMIT_IN_MATCH_OVER and Ferroni returns the next match or no match (ADR-008). Ferroni also accepts \x{140000}-\x{1FFFFF}, which C rejects.
- Conservative production use: 9 stars and very fast churn (2.0.0 with breaking changes on 2026-10-09, 2.1.0 and 2.1.1 within two days). It also had recent parity bugs on malformed UTF-8 (#257, #259, #261) and a stack overflow on deeply nested patterns (#285), all fixed by 2026-10-08.

## How it is fast

The structure of C Oniguruma is kept, and Rust-only search additions are layered on top (ADR-007, ADR-008). Literal prefix scans use memchr, memchr2, memchr3 and a memmem Finder. Alternations of plain literals become literal tries, and RegSet fallback entries are filtered by required literals (Aho-Corasick for several of them). Leading class runs are skipped, which the project credits with 22-31x on email-like scans, and leading checks let the search jump ahead. Unicode classes use a binary range lookup and adjacent ASCII class runs are batched. Scanner searches use a first-byte dispatch table, rejects on the first instruction, and a lazy-DFA pre-filter built on regex-automata (the default 'dfa-prefilter' feature) plus result and pattern caches. The large highlighting margin comes mostly from these RegSet additions measured against vscode-oniguruma's onig_regset_search(ONIG_REGSET_POSITION_LEAD), not from Rust codegen.

## Compared with alternatives

Pick Ferroni over the regex crate only when you need Oniguruma syntax (look-around, backreferences, TextMate grammars) or the vscode-oniguruma scanner; for plain search, regex is faster and linear-time. mojo-regex targets Python re and Rust regex syntax in Mojo, not Oniguruma.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | aho-corasick, bitflags, memchr, smallvec; with the default 'dfa-prefilter' feature also regex-automata and regex-syntax. A C compiler is needed only for the 'ffi'/'onigmo' benchmark features. |
| **Minimum toolchain** | Rust 1.94 (MSRV), edition 2024 |
| **Platforms** | any Rust target; memchr's SIMD paths are used where available (SSE2/AVX2 on x86-64, NEON on aarch64); measured on Linux x86-64 and macOS arm64 |
| **Thread safety** | Regex is Send + Sync and cheap to Clone (clones share one compiled program); Scanner is Send + Sync but its search takes &mut self, so each thread needs its own scanner. Limits can be set process-wide or per search. |
| **Drop-in for the baseline** | partial: it keeps the Oniguruma C API names and semantics (all 2,974 upstream UTF-8 test cases pass) and a vscode-oniguruma-shaped Scanner, but only as a Rust crate (no C ABI), for UTF-8 and ASCII only, without the POSIX/GNU APIs, and with small documented differences in retry-limit errors. |

## Gotchas

- The speed-up does not come from Rust codegen. The everyday and advanced figures depend on Rust-only search filters, and the 12x highlighting figure depends on the RegSet dispatch, required-literal and DFA pre-filter additions against the vscode-oniguruma C scanner's ONIG_REGSET_POSITION_LEAD search. Disabling the default 'dfa-prefilter' feature gives up part of the scanner gain.
- The harness is symmetric where it matters. Ferroni and C both go through onig_search with a reused region (benches/general_regex.rs, regex_tasks.rs). In the replays both get fresh string-cache identities every iteration (corpus.strings() vs CReplay::fresh_ids()), and the C side converts UTF-16 starts to byte offsets outside the timing. One residual asymmetry: each side's scanners persist across Criterion iterations, so Ferroni's lazy DFA pre-filter is always warm, and its build cost is not in the replay timing.
- The pre-filter can backfire. In the earlier run 37989957431 the flat CSS scanner regressed to 11-16 ms (C 4.8x faster) until PR #324 retired the pre-filter on sets whose DFA cache thrashes. Issue #327 (warm JSON and Astro regressions in Ferriki under 2.0.0) was fixed in 2.1.0 by building the pre-filter only after a warm-up. The published textmate set covers only the C, C++, Java, PHP and SCSS replays and the three battle_bench grammars (TypeScript, CSS, Rust); the JSON and Astro replays that regressed are not in it.
- The default nesting limit dropped to 256 units (128 groups) in 2.0.0, so deeply nested patterns now fail with ParseDepthLimitOver unless onig_set_parse_depth_limit and onig_set_ast_node_limit are both raised.

## Known shortcomings

- Rust reimplementation of Oniguruma (listed, wave 1) kept as its own entry because it beats its C origin with different algorithms: the win comes from Rust-only algorithms (memchr SIMD, tries, Aho-Corasick, run skips, regex-automata DFA pre-filter, ADR-007/008), not Rust codegen; C Oniguruma still wins some tasks and compiles faster; raw data in benches/results/blacksmith-2026-10-09-\* (rustc 1.99.0, GCC 13.3.0 / Apple clang 21, C at opt level 3, Apple M4 Pro) on shared virtual CI runners.
- Harness symmetric; no flaw behind the numbers (both engines use onig_search with a reused region; replays give fresh string-cache ids per iteration on both sides). The speed-up comes from Rust-only filters plus a regex-automata DFA prefilter, not codegen; the prefilter is always warm and its build cost untimed; C compiles some grammars 2-3x faster; the regex crate and PCRE2 JIT are faster on text tasks; churn (2.0.0 to 2.1.1 in 2 days); parity bugs #257/#259/#261 and stack overflow #285 fixed 2026-10-08.

## Caveats and trade-offs

The speedup is not a Rust-over-C codegen win: ADR-007 and ADR-008 (docs/app/routes/adr/) document Rust-only algorithmic additions layered on the line-by-line port, among them SIMD memchr/memmem literal search, literal tries for alternations, Aho-Corasick required-literal filters, leading-class-run skips (credited with 22-31x on email-like scans, matching the 32.7x email_addresses row), leading-check jumps, Unicode range lookup changes, ASCII class runs, and for highlighting a DFA pre-filter built on the regex-automata crate plus scanner and pattern caches. Measured on shared virtual CI runners (EPYC model unnamed); author-run. C Oniguruma is built from a hand-written config.h rather than its CMake configure. Rust regex and PCRE2 JIT are faster on most text tasks they can run, C Oniguruma wins several individual tasks and compiles some patterns 2x to 4x faster. The highlighting set measured one commit earlier showed a 13 ms regression (C 4.8x faster) on the flat CSS scanner before PR #324 retired the pre-filter there. Upstream Oniguruma ended in April 2025. Supports only ASCII and UTF-8 encodings and not the POSIX/GNU APIs. 8 stars. [retier] The speed-up comes from Rust-only filters plus a regex-automata DFA prefilter, not codegen; the prefilter is always warm and its build cost untimed; C compiles some grammars 2-3x faster; the regex crate and PCRE2 JIT are faster on text tasks; parity bugs #257/#259/#261 and stack overflow #285 were fixed 2026-10-08.

Only ASCII and UTF-8 of Oniguruma's 29 encodings; backtracking engine (no linear-time guarantee unless the compile-time check or limits are used); unsafe confined to parse-tree links.

## Maintenance

Active (2.1.1 released 2026-10-11, about 6.5k crates.io downloads), BSD-2-Clause like upstream, and declared feature-complete with maintenance-only plans now that C Oniguruma ended in April 2025. The benchmark evidence is unusually complete (raw measurements.json, SHA256SUMS, ADRs), but the project is young, single-vendor and has 9 stars.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the repo carries the full raw data behind the README table (benches/results/blacksmith-2026-10-09-37989957431 and -37999607702: measurements.json with host, rustc 1.99.0/LLVM 23.1.1, cc GCC 13.3.0 and Apple clang 21.0.0 receipts, Criterion means per case), the benchmark code is public (benches/battle_bench.rs, benches/regex_tasks.rs, benches/general_regex.rs, scripts/compare-engines.py), C Oniguruma is compiled by build.rs with cc opt_level(3) (-O3) and the Rust side with the bench profile (opt-level 3, thin LTO), and one host's CPU model is named (Apple M4 Pro, virtual). The per-host geomeans in the raw summaries reproduce the README figures (derived from page data).
- **Verifier notes:** Real, well-instrumented comparison against C Oniguruma at -O3 with a symmetric harness (both sides go through onig_search with a reused region in benches/general_regex.rs) and every engine validated against Oniguruma's matches; upgraded C to A from in-repo raw data. For wave 14 record same_algorithm false: the 2.2x/1.4x/12x come from Rust-only algorithmic additions (SIMD literal search, tries, Aho-Corasick, run skips, DFA pre-filter from regex-automata), not from Rust codegen, so the entry does not support a language-level claim. Shortcomings: shared virtual CI runners, C wins several tasks and compiles faster, PCRE2 JIT and Rust regex faster on most text tasks.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/sebastian-software/ferroni>
  - <https://github.com/sebastian-software/ferroni/commits/main>
  - <https://github.com/sebastian-software/ferroni/tree/main/benches>
  - <https://github.com/sebastian-software/ferroni/tree/main/benches/results>
  - <https://github.com/sebastian-software/ferroni/tree/main/benches/results/blacksmith-2026-10-09-37989957431>
  - <https://github.com/sebastian-software/ferroni/tree/main/benches/results/blacksmith-2026-10-09-37999607702>
  - <https://github.com/sebastian-software/ferroni/tree/main/docs/app/routes/adr>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/build.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/scripts/prepare-oniguruma-sources.sh>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/battle_inputs.toml>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/battle_bench.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/engines.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/regex_tasks.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/general_regex.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/results/blacksmith-2026-10-09-37989957431/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/results/blacksmith-2026-10-09-37989957431/summary.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/results/blacksmith-2026-10-09-37989957431/SHA256SUMS>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/results/blacksmith-2026-10-09-37989957431/linux-x86-64-shared/measurements.json>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/results/blacksmith-2026-10-09-37989957431/macos-arm64-shared/measurements.json>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/results/blacksmith-2026-10-09-37999607702/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/results/blacksmith-2026-10-09-37999607702/summary.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/docs/app/routes/adr/007-simd-accelerated-search.mdx>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/docs/app/routes/adr/008-rust-only-optimizations.mdx>
  - <https://crates.io/api/v1/crates/ferroni>
- **Sources the enricher read:**
  - <https://github.com/sebastian-software/ferroni>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/build.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/src/ffi.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/battle_bench.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/general_regex.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/regex_tasks.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/engines.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/shiki_scanner_bench.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/java_scanner_bench.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/cpp_scanner/mod.rs>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/vscode_scanner_native.c>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/scripts/compare-engines.py>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/results/blacksmith-2026-10-09-37989957431/README.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/results/blacksmith-2026-10-09-37989957431/summary.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/benches/results/blacksmith-2026-10-09-37999607702/summary.md>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/docs/app/routes/adr/007-simd-accelerated-search.mdx>
  - <https://raw.githubusercontent.com/sebastian-software/ferroni/HEAD/docs/app/routes/adr/008-rust-only-optimizations.mdx>
  - <https://github.com/sebastian-software/ferroni/issues?q=is%3Aissue>
  - <https://crates.io/api/v1/crates/ferroni>
  - <https://raw.githubusercontent.com/sebastian-software/ferromark/HEAD/README.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/sebastian-software/ferroni`) · [data/wave14/enrich/raw/github_com_sebastian_software_ferroni.json](../../../data/wave14/enrich/raw/github_com_sebastian_software_ferroni.json) (enrichment confidence 0.8)

</details>
