# regex (Rust regex crate)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust's linear-time finite-automata regex engine; faster than PCRE2 JIT and RE2 on most search benchmarks, slower to compile.

| | |
|---|---|
| **Beats** | PCRE2 (interpreter and JIT) and RE2 (C/C++ regex engines); Hyperscan also measured |
| **Claimed result** | rebar README summary of search-time benchmarks (geometric mean of per-benchmark speed ratios to the best engine, lower is better): hyperscan 2.37 (28 benchmarks), rust/regex 1.12.2 3.08 (38), pcre2/jit 10.47 6.00 (34), re2 10.39 (31), pcre2 interpreter 114.75 (33). The compile-time summary goes the other way: pcre2 1.41, pcre2/jit 6.20, rust/regex 11.85, re2 12.28. Intersection derived from the repo's recorded CSVs record/curated/2025-12-19/\*.csv (median search times; derived from page data, re-computed by the verifier): vs PCRE2 JIT rust/regex is faster in 21 of 34 benchmarks, geometric-mean time ratio 2.13x; vs RE2 faster in 27 of 31, 4.3x; vs the PCRE2 interpreter faster in 32 of 33, 44x; vs Hyperscan faster in only 12 of 28 (Hyperscan about 1.45x faster overall). LangArena results 2026-10-05, Etc::LogParser (13 patterns, count all matches): Rust 0.302 s vs C with PCRE2 JIT 0.485 s (clang -O2), 0.488 s (gcc -O2) and 0.486 s (gcc -O3 -march=native 'Fast' build), about 1.6x; vs the C++ version, which uses RE2, 0.993-0.998 s (about 3.3x). In the same file, Template::Regex ({{(.\*?)}} replacement): Rust 3.699 s vs C with PCRE2 JIT 1.155-1.173 s, so PCRE2 JIT is about 3.2x faster there; vs C++ RE2 4.84-4.90 s, Rust is about 1.3x faster. |
| **Workload** | rebar curated barometer: about 38 regex search benchmarks (literals, alternations, dates, Unicode classes, bounded repeats, dictionaries, ReDoS-style patterns, noseyparker rules) across many engines; corroborated by the LangArena Etc::LogParser task (13 log-grep patterns over generated web-server log lines). |
| **Metric** | throughput |
| **Hardware** | rebar does not state the machine. LangArena results file: AMD Ryzen 7 3800X 8-Core Processor, 78 GB, x86_64 Linux. |
| **Compiler and flags** | rebar: engine versions only (rust/regex 1.12.2, pcre2 10.47, re2 2025-11-05). PCRE2 (with SUPPORT_JIT) and RE2 are compiled from vendored source by the cc crate inside each engine's Cargo release profile (lto = fat, codegen-units = 1, default opt-level 3, so -O3 by the cc crate's default). This is derived from engines/pcre2/build.rs, engines/re2/build.rs and their Cargo.toml files; no compiler version is stated. LangArena: rustc 1.99.0, 'cargo build --release' with regex 1.12. C: clang 22.1.8 and gcc 16.0.1, prod flags -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, Fast flags -O3 -march=native -mtune=native -funroll-loops with -flto=thin, linked against the system libpcre2-8. C++ is linked against the system libre2. The system PCRE2 and RE2 versions and build flags are not recorded in the results file. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | rebar analysis: finite-automata engines (lazy DFA, one-pass DFA) with SIMD literal prefilters (memchr, Teddy) avoid backtracking and give DFA-speed matching on most patterns; PCRE2 JIT stays faster where JIT-compiled backtracking is cheap (small anchored patterns, capture-heavy cases). |
| **Adoption** | 4.0k stars; the regex engine behind ripgrep and much of the Rust ecosystem |
| **Last commit** | 2026-08-10 |
| **Links** | [repository](https://github.com/rust-lang/regex) · [benchmark](https://github.com/BurntSushi/rebar) |

## Verdict

rebar (by the crate's author, regex 1.12.2 vs PCRE2 10.47 and RE2 2025-11-05 built from source by the cc crate, CPU not stated) shows regex faster than PCRE2 JIT on 21 of 34 shared search benchmarks (2.13x geometric mean) and faster than RE2 on 27 of 31 (4.3x), but slower than Hyperscan. LangArena (independent, regex 1.13.1 per its Cargo.lock, rustc 1.99.0 on an AMD Ryzen 7 3800X) counts 13 log-grep patterns in 0.302 s vs 0.485 to 0.501 s for every C build using Ubuntu 26.04's libpcre2 with JIT and 0.99 s for C++ with libre2.

## Use it when

- Scanning large haystacks (logs, source trees, documents) with literal-anchored patterns: LangArena's 13 log-grep patterns ran 1.6x faster than C with PCRE2 JIT and 3.3x faster than C++ with RE2.
- Untrusted haystacks or user-supplied patterns where ReDoS matters: the per-search O(m\*n) bound plus RegexBuilder::size_limit cap both time and memory.
- Matching many patterns at once with RegexSet, or Unicode-aware classes (\w, \d, \p{Greek}, case folding) without extra flags.
- Any Rust project as the default regex choice (1.25 billion crates.io downloads; the engine behind ripgrep); from C or C++ only if you can build a Rust static library.

## Skip it when

- Patterns that need backreferences, look-around or recursion: use PCRE2.
- Capture-heavy replacement of many small matches: LangArena Template::Regex (replace_all on {{(.\*?)}} with a captures closure) ran 3.2x slower than C with PCRE2 JIT (3.699 s vs 1.155 s).
- Workloads dominated by compiling many patterns at run time: rebar's compile-time geometric mean is 11.85 for regex vs 1.41 for the PCRE2 interpreter and 6.20 for PCRE2 JIT; one dictionary pattern takes 1.29 ms to compile vs 120 us for PCRE2.
- Maximum throughput on x86 multi-literal scans: Hyperscan beats regex on 16 of the 28 shared rebar benchmarks, about 1.45x overall.
- Pure C/C++ builds that cannot add a Rust toolchain; the rure C API also lacks replace and split.

## How it is fast

The crate is a thin wrapper over regex-automata's meta::Regex, which picks an engine per pattern and per call: a lazy (hybrid) DFA built on demand, a one-pass DFA and a bounded backtracker for capture groups, and a PikeVM as the fallback. Literal extraction feeds SIMD prefilters from memchr and aho-corasick (Teddy) that skip to candidate positions, including prefix, reverse-suffix and reverse-inner literal optimizations. No backtracking means no catastrophic cases, and the DFA runs at near memory speed on literal-heavy patterns.

## Compared with alternatives

Pick regex when you need a general-purpose embeddable engine with a linear-time guarantee. Ferroni (Rust port of Oniguruma) fits when you need Oniguruma syntax such as look-around or backreferences; YARA-X is a malware-rule scanner and fastgrep a grep CLI, not general regex libraries.

## Integration

| | |
|---|---|
| **Form** | crate (regex on crates.io); C API via regex-capi (librure), built from the repo with cargo |
| **Dependencies** | regex-automata and regex-syntax; memchr and aho-corasick through the default perf-literal feature (can be disabled) |
| **Minimum toolchain** | Rust 1.65 (MSRV may rise in minor releases); edition 2021 |
| **Platforms** | any Rust target; LangArena also ran it as wasm32-wasip1 (1.16 to 1.24 s on LogParser vs 0.30 s native) |
| **Thread safety** | Regex is safe to share across threads; each search borrows mutable scratch space from an internal pool, which can contend on short haystacks; the docs advise cloning the Regex per thread (the compiled part is reference counted). |
| **Drop-in for the baseline** | partial: the syntax subset is close to PCRE/RE2 minus backreferences and look-around, but the API is Rust (or the rure C API), not pcre2_\* or RE2:: |

## Gotchas

- regex 1.13.1 (2026-07-15, PR #1364 for issue #1354) fixed reverse-suffix and reverse-inner optimizations that could report a wrong leftmost-first match span. The fix cost speed: the PR's own rebar diff shows curated/06-cloud-flare-redos 1.80x and 1.97x slower and non-curated benchmarks up to 61x slower (bounded-strings-ending-z, reallyhard0-32k, word-ending-nn). rebar's curated numbers (regex 1.12.2, 2025-12-19) predate the fix; adjusting the two curated rows gives about 2.05x vs PCRE2 JIT (was 2.13x) and 26 of 31 wins vs RE2 at about 4.1x (was 27 at 4.3x), derived from page data.
- find_iter and captures_iter are worst case O(m\*n^2), not O(m\*n): each match restarts a search (crate docs example `.*[^A-Z]|[A-Z]`). Use regex-automata's earliest mode if both pattern and haystack are untrusted.
- Compiling is expensive (microseconds to milliseconds); compiling inside a loop is the common performance bug. Use the regex! macro (new in 1.13.0) or a LazyLock static.
- Unicode is on by default: \w, \d and \s are Unicode classes, and . matches a UTF-8 code point. Large Unicode classes with counted repetition can be slow or hit the size limit; use (?-u) or regex::bytes for byte-oriented matching.

## Known shortcomings

- Tier A rests on LangArena (public code, Ryzen 7 3800X, clang 22.1.8, gcc 16.0.1, rustc 1.99.0); rebar alone is the author's own suite with no CPU (2.13x vs PCRE2 JIT on 21 of 34, 4.3x vs RE2 from the CSVs); Hyperscan is 1.45x faster overall and PCRE2 JIT 3.2x faster on Template::Regex; system PCRE2/RE2 versions and flags unrecorded; the LangArena C++ rows are RE2, not PCRE2.
- mariomka/regex-benchmark (verifier batch-67, wave 14): public flags (gcc -O3 -DNDEBUG, g++ -O3, cargo --release) on a 2019 MacBook Pro i9; the PCRE2 'Original' row runs without JIT by suite rule, and in the JIT rows the regex crate leads 3.14x overall but loses on the IP pattern; 2021 toolchains, repo archived.
- The rebar numbers (regex 1.12.2, 2025-12-19) predate the 1.13.1 correctness fix (#1354, PR #1364, 2026-07-15: wrong match spans from the reverse-suffix and inner optimisations); the PR's own rebar diff shows curated cloud-flare-redos 1.80x/1.97x slower and non-curated rows up to 61x slower, and recomputing with those two rows moves the PCRE2 JIT comparison from 2.13x to about 2.05x and RE2 from 27 of 31 at 4.3x to 26 of 31 at about 4.1x (derived). Tier A holds because LangArena's Cargo.lock pins the post-fix 1.13.1 and its LogParser harness has no flaw inflating Rust (fixed checksum 2439432; all 17 C builds 0.485-0.501 s since the time is inside Ubuntu 26.04 libpcre2). PCRE2 JIT is 3.2x faster on Template::Regex captures; compile is slower; Hyperscan is faster overall.

## Caveats and trade-offs

rebar's summary geometric means cover different benchmark subsets per engine (28 to 38), so only the intersection numbers compare like for like; the verifier re-computed them from the repo's recorded CSVs and they match. rebar is written by the regex crate's author, and its README says the analysis is biased towards that crate (BIAS.md). rebar states no CPU or compiler version. Hyperscan beats regex overall, and PCRE2 JIT wins 13 of the 34 shared benchmarks. LangArena is independent, with public code, compilers, flags and CPU. Its C LogParser time is the same at -O2 and at -O3 -march=native (0.486 s), so the opt level does not explain the gap. The PCRE2 and RE2 it measures are system libraries whose versions and build flags are not recorded. The C++ LangArena rows use RE2, not PCRE2. LangArena's Template::Regex task shows a 3.2x loss to PCRE2 JIT. The win is a library and engine-design effect (lazy DFA plus SIMD literal prefilters), not a language effect. [retier] The rebar numbers (regex 1.12.2, 2025-12-19) predate the 1.13.1 correctness fix (#1354, PR #1364, 2026-07-15: wrong match spans from the reverse-suffix and inner optimisations); the PR's rebar diff shows curated cloud-flare-redos 1.80x/1.97x slower, and recomputing with those rows moves the PCRE2 JIT comparison from 2.13x to about 2.05x and RE2 from 27 of 31 at 4.3x to 26 of 31 at about 4.1x. LangArena's LogParser harness has no flaw inflating Rust (fixed checksum; all 17 C builds 0.485-0.501 s). PCRE2 JIT is 3.2x faster on Template::Regex captures; compile is slower; Hyperscan is faster overall.

No backreferences or look-around (linear-time guarantee in exchange). Pattern compilation is slower than PCRE2 and RE2. Unicode tables add binary size. Rust API; C++ needs the rure C binding or FFI.

## Maintenance

Actively maintained by Andrew Gallant under rust-lang (1.13.1 released 2026-07-15, last commit 2026-08-10, 2 open bug issues, one published advisory, GHSA-m5pq-gvj9-9vr8 of March 2022, high severity, slow parsing of large repetitions of empty sub-expressions); MIT OR Apache-2.0 and copyable. LangArena harness checked: no flaw inflates Rust's result (fixed checksum 2439432 across languages; all 17 C builds land at 0.485 to 0.501 s because the time is spent inside the distro libpcre2, so the C compiler flags do not matter; the C side runs PCRE2 in UTF mode without UCP while Rust uses Unicode classes, a small handicap to Rust on ASCII logs if anything).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Tier A rests on the independent LangArena suite: its benchmark code is public (c/src/log_parser.c with pcre2_jit_match, rust/src/benchmarks/log_parser.rs with regex::Regex::find_iter, the same 13 patterns and count-all-matches work). Its results file results/2026-10-05-kostya-ms7c37.js states the CPU (AMD Ryzen 7 3800X), clang 22.1.8, gcc 16.0.1 and rustc 1.99.0, and the C flags are in c/Makefile. rebar alone would be tier C: it is written by the regex crate's author, it lists engine versions but no CPU or compiler version, and its flags are only derivable from Cargo profiles.
- **Verifier notes:** Every number checked: the rebar README summary tables, the intersection ratios re-computed from the 2025-12-19 CSVs (21/34 at 2.13x vs PCRE2 JIT, 27/31 at 4.3x vs RE2, 32/33 at 44x vs the PCRE2 interpreter, 12/28 at 0.69x vs Hyperscan) and the LangArena runtimes all match. Shortcomings: rebar is first-party and states no CPU; regex loses to Hyperscan overall, loses to PCRE2 JIT on about a third of rebar's benchmarks and on LangArena Template::Regex (3.2x); LangArena's baselines are system-packaged PCRE2 and RE2 with unrecorded versions and flags. Metadata confirmed: MIT OR Apache-2.0, 4.0k stars, last commit 2026-08-10. Not a duplicate: ripgrep (wave 11) is listed separately and uses this crate.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-11 (wave 14); verifier batch-67 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/README.md>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/rust-regex.csv>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/pcre2-jit.csv>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/pcre2.csv>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/re2.csv>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/hyperscan.csv>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/README.md>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/engines/pcre2/build.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/engines/pcre2/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/engines/re2/build.rs>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/engines/re2/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/Cargo.toml>
  - <https://github.com/kostya/LangArena/tree/master/c/src>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/log_parser.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/log_parser.rs>
  - <https://github.com/rust-lang/regex>
  - <https://github.com/rust-lang/regex/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rust-lang/regex/HEAD/README.md>
  - <https://raw.githubusercontent.com/rust-lang/regex/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-lang/regex/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/rust-lang/regex/HEAD/UNICODE.md>
  - <https://raw.githubusercontent.com/rust-lang/regex/HEAD/regex-capi/README.md>
  - <https://raw.githubusercontent.com/rust-lang/regex/HEAD/src/lib.rs>
  - <https://github.com/rust-lang/regex/pull/1364>
  - <https://github.com/rust-lang/regex/security>
  - <https://github.com/rust-lang/regex/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/rust-lang/regex/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance>
  - <https://crates.io/api/v1/crates/regex>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/README.md>
  - <https://github.com/BurntSushi/rebar/tree/master/record/curated>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/rust-regex.csv>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/pcre2-jit.csv>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/pcre2.csv>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/re2.csv>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/record/curated/2025-12-19/hyperscan.csv>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/tree/master/rust/src/benchmarks>
  - <https://github.com/kostya/LangArena/commits/master/rust/Cargo.lock>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/Cargo.lock>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/log_parser.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/template.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/log_parser.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/log_parser.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/test.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker-compose.yaml>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/docker/base>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/rust-lang/regex`) · [data/wave14/enrich/raw/github_com_rust_lang_regex.json](../../../data/wave14/enrich/raw/github_com_rust_lang_regex.json) (enrichment confidence 0.85)

</details>
