# REAL (real-regex)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Regex](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 linear-time regex engine with lookaround support, beating std::regex 8x-152x and RE2 on every supported pattern.

| | |
|---|---|
| **Beats** | std::regex |
| **Claimed result** | 8.20x-41.97x faster than std::regex (libstdc++) on x86-64 (g++ 13.3.0); 15.31x-151.97x faster than std::regex (libc++) on arm64 (Apple clang 16). Also faster than RE2 in every case it supports (2.90x-16.34x on x86-64, 2.41x-11.53x on arm64) and beats PCRE2-JIT on 7 of 12 patterns on both ISAs. |
| **Workload** | 12 general-purpose regex patterns (word/digit/field extraction, single-char class, bounded repeats, possessive quantifiers, alternation, date/hex matching, literal, anchored, lookahead) scanning the same corpus and counting non-overlapping matches, in nanoseconds per corpus byte; median of 30 paired batches x 3 runs (minimum taken per cell), match counts verified equal across engines on the same commit. |
| **Metric** | throughput |
| **Hardware** | x86-64 host (exact CPU model not named in the doc) and arm64 Apple Silicon (measured on AC power, per the project's own measurement-methodology notes) |
| **Compiler and flags** | c++ -std=c++20 -O2 (per benchmarks/Makefile 'bench-engines' target); g++ 13.3.0 on x86-64, Apple clang 16 on arm64 |
| **Adoption** | 4 stars; very new project (repo created June 2026) |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/RECHE23/real-regex) · [benchmark](https://github.com/RECHE23/real-regex/blob/main/docs/BENCHMARKS.md) |

## Verdict

REAL's own in-repo benchmark (benchmarks/bench_engines.cpp via make bench-engines, c++ -std=c++20 -O2; g++ 13.3.0 on an unnamed x86-64 host, Apple Clang 16 on arm64 Apple Silicon) counted non-overlapping matches for 12 general-purpose patterns and measured REAL 8.20x-41.97x faster than std::regex (libstdc++) on x86-64 and 15.31x-151.97x faster than std::regex (libc++) on arm64, 2.90x-16.34x/2.41x-11.53x faster than RE2 where RE2 supports the pattern, and ahead of PCRE2-JIT on 7 of 12 rows on both ISAs - all figures matched exactly what is published in docs/BENCHMARKS.md this session.

## Use it when

- C++20 codebase needing linear-time, ReDoS-safe matching AND lookaround in the same engine (RE2/Rust regex lack lookaround, PCRE2/std::regex backtrack)
- Single-pattern throughput workloads - word/digit/field extraction, hex/date matching, alternation - where the project's own benchmark shows 8.20x-41.97x (x86-64) / 15.31x-151.97x (arm64) over std::regex and wins over RE2 in every case RE2 supports
- Untrusted or adversarial regex patterns/subject text where catastrophic backtracking (e.g. (a+)+b) is a real operational risk
- Need the same engine exposed from Python, Rust, Go and C via the project's own bindings, not just C++
- Willing to pay a header-only compile-time cost (measured 4.3s / 213KiB __text for one TU vs 1.1s / 47KiB for &lt;regex&gt;, arm64 clang -O2) in exchange for the runtime win

## Skip it when

- Pattern needs backreferences or conditional groups - REAL rejects these outright by design (real::regex_error, no silent fallback in its native API)
- Matching many patterns against one text at once (regex_set) with N much above \~56 - REAL's pure N-walk mode degrades hard (\~559 MB/s at N=16 down to \~39 MB/s at N=128 on the project's own bench) and loses to RE2::Set/Hyperscan at scale
- Lookahead-heavy or fixed-width date/hex workloads specifically - PCRE2-JIT still wins those rows outright (0.71x-0.92x, i.e. PCRE2 faster) in REAL's own tables
- Toolchain stuck below C++20 - this is a hard minimum, asserted in every header, versus std::regex's C++11 floor
- Risk-averse teams: this is an extremely new project (4 stars, repo created 2026-06-13) with benchmarks that are self-published and not yet independently reproduced

## How it is fast

Routes each compiled pattern to the cheapest execution tier that can handle it - exact-literal/fixed-shape fast paths, a one-pass DFA, a lazy DFA with a bounded state cache, or the general Pike VM (Thompson-NFA simulation) as fallback - instead of always running one general matcher. Character-class steps use SIMD probing (engine/simd.hpp), and a required-literal prefilter rejects non-matching input (e.g. classic ReDoS patterns) in microseconds without entering the NFA at all. Constexpr-friendly parsing/compilation lets patterns known at compile time be parsed, compiled and matched at compile time.

## Compared with alternatives

Pick REAL over Boost.Regex when you need a linear-time ReDoS-safe guarantee with lookaround - Boost.Regex is a backtracking engine like std::regex and doesn't offer that guarantee. Pick it over RE/flex when you need general runtime regex matching rather than an offline lexer-generator workflow, and over Unformat when the task is general pattern matching rather than std::format-style structured parsing.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (zero runtime deps; the SciForge harness is only needed to build the test suite/CI, never the library itself) |
| **Minimum toolchain** | C++20 (hard requirement, enforced via a static_assert in every header); tested in CI with g++ 13.3.0, Apple Clang 16, and MSVC on Windows |
| **Platforms** | Linux x86-64 and AArch64, macOS arm64, Windows (MSVC) per CI matrix; no specific SIMD ISA extension (e.g. AVX2) documented as mandatory |
| **Thread safety** | A compiled real::regex is immutable and can be used from many threads simultaneously; a match iterator is not shared across threads (docs/site/reference/basic_regex.rst) |
| **Drop-in for the baseline** | partial - explain: native API (real::regex) is a different interface from std::regex; the separate real::compat::std header runs a pattern on REAL when provably equivalent to std::regex/ECMAScript (incl. all five POSIX grammars) and falls back to std::regex otherwise, reporting which backend ran via uses_real() |

## Gotchas

- Possessive quantifiers/atomic groups are only linear-time (Tier 1) for a single atom or one atom wrapped in one capturing group ([^x]\*+, \d++, (?&gt;\w+)); a compound body inside them is rejected outright, never silently mismatched
- Nullable patterns (a\*, (x)?) keep REAL's ReDoS-safe search/match, but regex_replace and iteration on them are delegated to std::regex per-operation - the linear-time guarantee doesn't cover every operation on every pattern
- find_iter (and Python finditer) do not get the trailing-lookahead fast path that count_matches/search/match/replace get - benchmarks that compare via len(findall(...)) rather than count_matches are not comparable to this project's own numbers
- Backreferences, recursion, subroutine calls and callouts are excluded by design (raise real::regex_error) - not a roadmap gap but a permanent rejection to preserve the linear-time guarantee

## Caveats and trade-offs

This is an extremely new, very small project (4 stars, created 2026-06-13) with no external validation beyond its own suite. The CPU models for both benchmark hosts are not disclosed: the x86-64 leg ran in a container with documented 'episodic interference'. std::regex is 'unsupported' for the anchored row on both ISAs and for the possessive row on arm64, so the std::regex ranges cover 11 (x86-64) and 10 (arm64) of the 12 patterns. BENCHMARKS.md is unusually self-critical: it documents past drift between the summary bullets and the measured tables, and warns that before/after deltas are layout-noise-sensitive.

Requires C++20 (std::regex only needs C++11); rejects backreferences and conditional groups by design to keep linear-time guarantees, so it is not a full drop-in for all std::regex/PCRE patterns; PCRE2-JIT still wins on lookahead-heavy and some fixed-width date/hex patterns via backtracking; the multi-pattern (regex_set) N-walk mode degrades hard as pattern count N grows and loses to RE2::Set/Hyperscan at scale, per the project's own docs.

## Maintenance

Actively maintained - near-daily CalVer releases (release notes run through v2026.9.7, last commit 2026-09-24) - and MIT-licensed, header-only, so trivially vendorable, but still a very new, small project (4 stars, repo created 2026-06-13) with no external validation of its benchmarks beyond its own suite.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** There is reproducible in-repo code (benchmarks/bench_engines.cpp via 'make bench-engines', c++ -std=c++20 -O2) with compilers stated (g++ 13.3.0, Apple clang 16). But hardware is given only as ISA ('x86-64' container, 'arm64' Apple on AC power) with no CPU model, so it fails A. It is a self-published benchmark with no peer review or third-party suite, so not B; C by elimination.
- **Verifier notes:** Every number in claimed_speedup matches the §A tables and bullets exactly (8.20-41.97x x86-64, 15.31-151.97x arm64, RE2 2.90-16.34x / 2.41-11.53x, PCRE2-JIT beaten on 7 of 12 on both ISAs). The downgrade is only because the hardware is undisclosed. It would qualify for A if the CPU models were stated. Metadata verified: MIT, 4 stars, last commit 2026-09-24T02:27Z (UTC).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/RECHE23/real-regex/blob/main/docs/BENCHMARKS.md>
  - <https://github.com/RECHE23/real-regex>
  - <https://github.com/RECHE23/real-regex/blob/main/benchmarks/Makefile>
  - <https://github.com/RECHE23/real-regex/blob/main/docs/MEASUREMENT.md>
- **Sources the enricher read:**
  - <https://github.com/RECHE23/real-regex>
  - <https://github.com/RECHE23/real-regex/blob/main/README.md>
  - <https://github.com/RECHE23/real-regex/blob/main/docs/BENCHMARKS.md>
  - <https://github.com/RECHE23/real-regex/blob/main/docs/COMPATIBILITY.md>
  - <https://github.com/RECHE23/real-regex/blob/main/SECURITY.md>
  - <https://github.com/RECHE23/real-regex/blob/main/docs/site/reference/basic_regex.rst>
  - <https://github.com/RECHE23/real-regex/issues?q=bug>
  - <https://github.com/RECHE23/real-regex/issues?q=performance>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/reche23/real-regex`) · [data/wave1/enrich/raw/github_com_reche23_real_regex.json](../../../data/wave1/enrich/raw/github_com_reche23_real_regex.json) (enrichment confidence 0.72)

</details>
