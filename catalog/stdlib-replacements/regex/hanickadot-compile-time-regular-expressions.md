# CTRE (compile-time regular expressions)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Regex](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C++ template-metaprogramming regex engine for compile-time-known patterns, with large wall-clock wins over std::regex.

| | |
|---|---|
| **Beats** | std::regex |
| **Claimed result** | clang-bench.txt: CTRE 10.093s vs std::regex 21m9.309s (\~125x, derived from page data) on 'ABCD\|DEFGH\|EFGHI\|A{4,}'; CTRE 14.197s vs std::regex 2m34.505s (\~10.9x, derived from page data) on '[0-9a-fA-F]{8,16}'; CTRE 7.596s vs std::regex 7m54.793s (\~62.5x, derived from page data) on '^([0-9]{4,16})?[aA]'; CTRE 59.864s vs std::regex 27m35.004s (\~27.6x, derived from page data) on the alternation pattern. gcc-bench.txt shows smaller gaps, e.g. CTRE 3.982s vs std::regex 0m55.058s (\~13.8x, derived from page data) on the first pattern. |
| **Workload** | Raw `time`-command wall-clock comparison of egrep, CTRE, PCRE, and std::regex matching four regex patterns (e.g. 'ABCD\|DEFGH\|EFGHI\|A{4,}', '[0-9a-fA-F]{8,16}', '^([0-9]{4,16})?[aA]', '([aAbB]{4,}\|[xXyY]{4,}\|[1234]{4,})0'), captured once with clang (clang-bench.txt) and once with gcc (gcc-bench.txt). No description of input size, test harness, or what program was actually timed. |
| **Metric** | other |
| **Compiler and flags** | clang (version unstated) for clang-bench.txt, gcc (version unstated) for gcc-bench.txt; no optimization flags stated. |
| **Adoption** | 3.9k stars; used as a reference implementation for a C++ standards proposal (P1433) for compile-time regex |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/hanickadot/compile-time-regular-expressions) · [benchmark](https://github.com/hanickadot/compile-time-regular-expressions/blob/main/clang-bench.txt) |

## Verdict

First-party `time`-command runs (clang-bench.txt and gcc-bench.txt, committed 2018-10-23) show CTRE beating std::regex by roughly 11x-125x wall-clock across four patterns under clang (e.g. 10.093s vs 21m9.309s on 'ABCD|DEFGH|EFGHI|A{4,}') and roughly 14x-24x under gcc (e.g. 3.982s vs 0m55.058s on the same pattern), with no compiler version, optimization flags, CPU, or input size recorded. A separate WG21 P1433R0 table gives CTRE 3.172s vs std::regex/libstdc++ 33.585s on Linux/gcc and CTRE 11.11s vs std::regex/libc++ 1655s on macOS/clang, and that macOS figure duplicates a clang-bench.txt number exactly, so the two sources' data provenance is unclear.

## Use it when

- Pattern is a compile-time literal or constexpr reused across many match calls (parsers, lexers, validators), not built from runtime user input.
- Hot-path matching/parsing where std::regex's per-invocation compile step dominates runtime.
- Want structured-binding capture access (e.g. `auto [whole, year, month] = ...`) instead of std::smatch/std::ssub_match.
- Project can require clang 14+, gcc 9+, or MSVC 16.11+ and build with C++17/20.
- Header-only vendoring is acceptable — a single-header variant exists for easy drop-in as a source file.

## Skip it when

- Pattern arrives at runtime (user-supplied, config-loaded) — CTRE patterns must be compile-time-known, so it can't replace std::regex there.
- Need PCRE features CTRE excludes: callouts, comments, conditional patterns, \cX control-char escapes, \K match-point reset, named characters, octal numbers, subroutines, \X grapheme clusters.
- Toolchain predates clang 14 / gcc 9 / MSVC 16.11 (VS 2019 16.11).
- Taking the README's or bench files' &gt;50x numbers at face value: they are tier-C, dated 2018-10-23, with no CPU, compiler version, flags, or input size stated.
- Correctness on edge cases matters as much as speed: open bugs include incorrect matches with repeated capture groups (#300) and lookahead failing to compile with UTF-8 input (#338).

## How it is fast

Regex parsing and construction of the matching logic both happen at compile time via constexpr functions and template metaprogramming (the bundled ctll parser), so the compiler emits specialized branch/comparison code for one exact pattern instead of interpreting a generic runtime NFA the way std::regex does. This removes std::regex's per-call pattern-compilation cost entirely and lets ordinary compiler optimizations (inlining, constant folding) act directly on the matcher. The tradeoff is longer compile times and larger generated code in exchange for eliminated runtime interpretation overhead.

## Compared with alternatives

Pick CTRE over RE2 when the pattern set is fixed at compile time and you want zero runtime regex-compile overhead with PCRE-like syntax and structured-binding captures; pick RE2 instead when patterns are supplied at runtime or you need its linear-time worst-case guarantee against untrusted/adversarial input.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (bundles its own ctll template-parser headers) |
| **Minimum toolchain** | C++17 (C++20 for the `<pattern>` NTTP syntax); clang 14+, gcc 9+, MSVC 16.11+ (VS 2019 16.11) |
| **Platforms** | any (portable standard C++, no architecture-specific code) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same match/search/capture concepts as std::regex, but the pattern must be a compile-time template argument (not a runtime std::string) and results are a regex_results/structured-binding type rather than std::smatch, so call sites need rewriting |

## Gotchas

- Pattern must be compile-time-known: a template argument or constexpr ctll::fixed_string, never something assembled at runtime.
- The N3599 UDL syntax (`"regex"_ctre`) on GCC 9.1+ requires defining CTRE_ENABLE_LITERALS and building without -pedantic.
- Unicode support is opt-in via separate `<ctre-unicode.hpp>` + `<unicode-db.hpp>` includes; omitting them gives missing-symbol link errors, not silent fallback.
- Open bugs: incorrect match with repeated capture groups (#300, 2025), lookahead fails to compile with UTF-8 strings (#338, 2025), MSVC internal compiler error on some inputs (#255, 2022).

## Caveats and trade-offs

The README has no benchmark numbers, and compile-time.re/graph/ is JS-rendered. clang-bench.txt/gcc-bench.txt date from 2018-10-23 and give no compiler version, flags, CPU or input size, so they predate current v3. Benchmark sources exist in tests/benchmark-exec (ctre.cpp, std.cpp, pcre.cpp, re2.cpp, ...), and the current Makefile builds with -O3, but the txt files cannot be tied to them. WG21 P1433R0 (same author) has another first-party table on a \~1.3 GB CSV with pattern ([0-9]{4,16})?[aA]: CTRE 3.172 s vs std::regex (libstdc++) 33.585 s on GNU/gcc, and CTRE 11.11 s vs std::regex (libc++) 1655 s on macOS/clang. That 1655 s figure equals clang-bench.txt's 4th-pattern std::regex time, so data provenance is unclear. Several ratios exceed 50x with flags unstated.

Regex pattern must be a compile-time-known string (template/NTTP); needs recent compilers (clang 14+, gcc 9+, MSVC 16.11+); does not support callouts, comments, conditional patterns, control-char escapes, named characters, octal numbers, subroutines, or Unicode grapheme-cluster \X (per README's PCRE-syntax exception list).

## Maintenance

Actively maintained (last commit 2026-09-11, CMakeLists reports v3.11.0) with 3.9k stars and used as the reference implementation for WG21 proposal P1433; Apache-2.0 licensed and header-only, so cheap to vendor even though its headline benchmark numbers are old (2018) and thinly documented.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** clang-bench.txt/gcc-bench.txt (committed 2018-10-23) are first-party raw `time` outputs with CTRE vs std::regex. They give no compiler version, flags, CPU or input, and ratios exceed 50x, so C. The WG21 paper P1433R0 adds stdlib names and input size but still no CPU/flags, so it stays C.
- **Verifier notes:** All numbers verified in both txt files. Ratios were unmarked, so I added '(derived from page data)'. baseline_stdlib is left [] because the benchmark_url files don't name a stdlib, but P1433R0 names libstdc++ and libc++. Metadata checks out: Apache-2.0, 3,855 stars, last commit 2026-09-11. P1433 does cite CTRE as its implementation.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/hanickadot/compile-time-regular-expressions/blob/main/clang-bench.txt>
  - <https://github.com/hanickadot/compile-time-regular-expressions/blob/main/gcc-bench.txt>
  - <https://github.com/hanickadot/compile-time-regular-expressions>
  - <https://github.com/hanickadot/compile-time-regular-expressions/blob/main/README.md>
  - <https://github.com/hanickadot/compile-time-regular-expressions/blob/main/Makefile>
  - <https://github.com/hanickadot/compile-time-regular-expressions/tree/main/tests/benchmark-exec>
  - <https://compile-time.re/>
  - <https://compile-time.re/graph/>
  - <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1433r0.pdf>
- **Sources the enricher read:**
  - <https://github.com/hanickadot/compile-time-regular-expressions>
  - <https://github.com/hanickadot/compile-time-regular-expressions/blob/main/README.md>
  - <https://github.com/hanickadot/compile-time-regular-expressions/blob/main/CMakeLists.txt>
  - <https://github.com/hanickadot/compile-time-regular-expressions/blob/main/clang-bench.txt>
  - <https://github.com/hanickadot/compile-time-regular-expressions/blob/main/gcc-bench.txt>
  - <https://github.com/hanickadot/compile-time-regular-expressions/issues>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/hanickadot/compile-time-regular-expressions`) · [data/wave0-seed/enrich/raw/github_com_hanickadot_compile_time_regular_expressions.json](../../../data/wave0-seed/enrich/raw/github_com_hanickadot_compile_time_regular_expressions.json) (enrichment confidence 0.45)

</details>
