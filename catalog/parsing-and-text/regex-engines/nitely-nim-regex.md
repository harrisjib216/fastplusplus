# nim-regex (nitely/regex)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Nim` · `MIT` · 🟢 active

> Pure-Nim linear-time regex engine (PCRE-like syntax, no backtracking) beating PCRE2 on find-all throughput.

| | |
|---|---|
| **Beats** | PCRE2 |
| **Claimed result** | Default-settings run: nim-regex 36.09 ms total vs C PCRE2 251.37 ms (\~7.0x faster) and C++ STL std::regex 1023.49 ms (\~28x faster); also \~1.6x faster than default Rust regex (57.63 ms). Optimized run: nim-regex 34.15 ms vs optimized PCRE2 87.87 ms (\~2.6x) and C++ STL 1021.10 ms (\~30x), but optimized Rust regex (27.94 ms) beats nim-regex by \~1.2x. All ratios derived from page data. |
| **Workload** | Find-all of email/URI/IPv4 regex patterns over a concatenated text corpus (learnxinyminutes-docs), measured on a MacBook Pro 16-inch 2019 (2.4GHz i9); benchmark also includes C PCRE2, Rust regex crate, and C++ STL std::regex in the same harness |
| **Metric** | throughput |
| **Hardware** | MacBook Pro 16-inch 2019, 2.4 GHz Intel Core i9, 32 GB 2667 MHz DDR4, macOS Big Sur 11.2.3 |
| **Compiler and flags** | Nim 1.4.4, 'nim c -d:release --opt:speed' (nimble package 'regex', unpinned); C: gcc 7.5.0 -O3 -DNDEBUG with PCRE2 10.36-2; C++ STL: g++ 7.5.0 -std=c++11 -O3; Rust: rustc 1.51.0, regex 1.4.5, cargo build --release; run via Docker image mariomka/regex-benchmark:1.6 |
| **Adoption** | 244 stars |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/nitely/nim-regex) · [benchmark](https://github.com/mariomka/regex-benchmark/blob/master/README.md) |

## Verdict

In mariomka/regex-benchmark's third-party cross-language shootout (find-all of email/URI/IPv4 patterns over a concatenated learnxinyminutes-docs corpus, on a 2019 MacBook Pro 16" i9, run in Docker), nim-regex (Nim 1.4.4, -d:release --opt:speed) totaled 36.09 ms versus C PCRE2 10.36-2's 251.37 ms (gcc -O3) and libstdc++ std::regex's 1023.49 ms (g++ -O3) in the default-settings table; with PCRE2 and Rust's regex crate both given their optimized/JIT builds, the PCRE2 gap narrows to \~2.6x (34.15 ms vs 87.87 ms) and optimized Rust regex (27.94 ms) comes out ahead of nim-regex.

## Use it when

- Nim codebases that need to run regexes over untrusted input and want a hard linear-time guarantee instead of PCRE2's backtracking risk
- Patterns with distinctive literal prefixes/substrings (email-, URL-, tag-style patterns) where the litopt prefilter gives large wins
- Compile-time regex validation/compilation is wanted (re2"..." as a const catches syntax errors at compile time and avoids runtime compile cost)
- Need PCRE-like syntax (character classes, named groups, lookaround) in Nim without adding a C PCRE2 dependency or FFI binding
- Running inside Nim's compile-time VM, where linking a C library like PCRE2 isn't an option

## Skip it when

- Need to call the engine from C/C++/other languages without writing an FFI wrapper — PCRE2 is natively embeddable there, nim-regex is not
- Pattern relies on backreferences or other non-regular PCRE features — explicitly unsupported to preserve the linear-time guarantee
- Character-class-heavy patterns without literal anchors (e.g. pure IPv4-style patterns): in the optimized-PCRE2 run, PCRE2 beat nim-regex on the IPv4 pattern (4.73 ms vs 7.27 ms), and optimized Rust regex beat it overall
- Need Unicode level 2/3 support (locale-aware casing, full normalization) — only Unicode level-1 is implemented
- Feeding invalid/untrusted UTF-8 bytes in a release/danger build: UTF-8 validation is only performed in debug builds, so malformed input is undefined behavior (can hit an AssertionDefect) unless you pre-validate

## How it is fast

Matching runs as a Thompson-style NFA simulation over parallel states (Pike's-VM approach, files nfamatch.nim/nfamatch2.nim use a `Pstates`/`Capts3` structure) rather than backtracking, giving match time linear in text and regex length. A literal-substring prefilter (litopt.nim, added in v0.22.0) skips ahead using known literal prefixes/substrings of the pattern, which is why the email-pattern benchmark result (1.32 ms vs PCRE2's 126.10 ms) dominates the aggregate speedup. Captures use a block-based capture array (space O(regex_len \* groups_count)) instead of per-thread heap allocation.

## Compared with alternatives

The other catalogued regex-engine entries (rejit, SafeRE, BLARE, RE#, coregex, nanoregex, re2jit) target C++/Rejit, Java, C++, .NET, Go/Rust-bench, or Python ecosystems; nim-regex is the only Nim-native option, so pick it when you're already in Nim and want PCRE2-beating throughput plus a no-backtracking safety guarantee without FFI, not when raw cross-language speedup magnitude is what matters.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (pure Nim, stdlib only: std/unicode, std/tables, std/sets, std/algorithm, std/math, std/bitops) |
| **Minimum toolchain** | Nim 1.6.0+ |
| **Platforms** | any platform Nim compiles to (pure Nim source, no SIMD/architecture-specific code observed) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: same problem domain and PCRE-like syntax as PCRE2, but a distinct Nim-only API (re2/Regex2), not an ABI-compatible or FFI drop-in; the v0.21.0 release also broke nim-regex's own older API (re""/Regex -&gt; re2""/Regex2) |

## Gotchas

- v0.21.0 deprecated the old re""/Regex/RegexMatch API in favor of re2""/Regex2/RegexMatch2 — check which API a given nimble version exposes
- Only the last repetition of a repeated capture group is retained (same limitation as most regex engines), not all repetitions
- Lookarounds that themselves contain repetition (\*, +, {n,}) can run in polynomial time, breaking the library's headline linear-time guarantee
- UTF-8 input validation is skipped in release/danger builds for performance; malformed UTF-8 is undefined behavior there, so untrusted text must be pre-validated (e.g. with validateUtf8 or nim-unicodeplus)

## Caveats and trade-offs

Third-party cross-language shootout (mariomka/regex-benchmark), not nim-regex's own. Results date from 2021 (Nim 1.4.4, rustc 1.51), and the nim-regex version was whatever nimble installed then. Run in Docker on macOS. The total is dominated by the Email pattern (1.32 ms vs PCRE2's 126.10 ms). In the optimized run PCRE2 beats nim-regex on IPv4 (4.73 vs 7.27 ms) and Rust beats it on URI and IPv4. The lead over PCRE2 shrinks from \~7x to \~2.6x once PCRE2 is optimized, and the Rust win only holds in the default table. The std::regex comparison is libstdc++ (g++ 7.5.0) only.

Nim-only (not usable from C/C++ without FFI wrapping); guarantees linear-time matching (no catastrophic backtracking) via a DFA/NFA hybrid, PCRE-like syntax but with Unicode level-1 support only; benchmark corpus (concatenated tutorial docs) may not represent all real workloads.

## Maintenance

Actively maintained — latest release v0.26.2 with recent "performance improvements" commits and last commit 2026-08-25; MIT-licensed pure-Nim source, small enough to vendor directly into a project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Well-known third-party suite with public code: mariomka/regex-benchmark, nim/benchmark_regex.nim, c/benchmark.c and cpp/benchmark.cpp, driven by run-benchmarks.php. Compiler versions are in the README; flags are in run-benchmarks.php (gcc -O3 -DNDEBUG, g++ -std=c++11 -O3, nim c -d:release --opt:speed, cargo --release). Hardware: MacBook Pro 16-inch 2019 with a 2.4 GHz Core i9, no SKU number printed.
- **Verifier notes:** Every number matches the README rows for Nim Regex, C PCRE2, Rust and C++ STL. I confirmed the 'Nim Regex' row is nitely's package: Dockerfile runs 'nimble install regex'. Compiler flags come from run-benchmarks.php, not the README.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/mariomka/regex-benchmark/blob/master/README.md>
  - <https://github.com/mariomka/regex-benchmark/blob/master/run-benchmarks.php>
  - <https://github.com/mariomka/regex-benchmark/blob/master/Dockerfile>
  - <https://github.com/mariomka/regex-benchmark/tree/master/nim>
  - <https://github.com/nitely/nim-regex>
- **Sources the enricher read:**
  - <https://github.com/nitely/nim-regex>
  - <https://github.com/nitely/nim-regex/blob/master/README.md>
  - <https://github.com/nitely/nim-regex/blob/master/src/regex.nim>
  - <https://github.com/nitely/nim-regex/blob/master/CHANGELOG.md>
  - <https://github.com/nitely/nim-regex/blob/master/src/regex/nfamatch2.nim>
  - <https://github.com/nitely/nim-regex/blob/master/src/regex/nfatype.nim>
  - <https://github.com/nitely/nim-regex/tree/master/src/regex>
  - <https://github.com/mariomka/regex-benchmark/blob/master/README.md>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/nitely/nim-regex`) · [data/wave3/enrich/raw/github_com_nitely_nim_regex.json](../../../data/wave3/enrich/raw/github_com_nitely_nim_regex.json) (enrichment confidence 0.78)

</details>
