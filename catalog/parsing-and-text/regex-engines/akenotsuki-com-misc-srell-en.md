# SRELL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Header-only ECMAScript regex engine with the std::regex class design; a 2023 competitor shootout timed it far ahead of std::regex.

| | |
|---|---|
| **Beats** | std::regex |
| **Claimed result** | Snippet figures from the author's results sheet, -O3: SRELL 0.0174093 vs std::regex 0.724126 (about 41x, derived from page data; unit not visible, probably seconds); SRELL 'minimized' build 0.018889; Boost 0.084939; CTRE 0.061135; Matcheroni 0.057985. A second snippet of what looks like per-pattern msec values showed SRELL Email 0.018666 vs std::regex 0.001538 (SRELL slower), URL 0.000253 vs 0.000294, IP4 0.000336 vs 0.000362. The Matcheroni README of mid-2023 says 'SRELL is the performance champion' and 'std::regex is terrible by all metrics'. |
| **Workload** | Matcheroni author's regex shootout (examples/regex/regex_benchmark.cpp, formerly matcheroni/benchmark.cpp): count matches of the Email, URI and IPv4 patterns from mariomka/regex-benchmark over its input-text.txt (a concatenation of the Learn X in Y minutes docs), also recording build time and binary size. |
| **Metric** | throughput |
| **Compiler and flags** | -O3 (a search summary said GCC 14; not confirmed from an opened page) |
| **Adoption** | Packaged in FreeBSD ports (devel/srell, DISTVERSION 2026.05, LICENSE=BSD2CLAUSE); other distribution packaging not verified; no GitHub repository |
| **Links** | [repository](https://www.akenotsuki.com/misc/srell/en/) · [benchmark](https://docs.google.com/spreadsheets/d/17AjRa8XYFfhlluFPoLMWJUpjH6aI_gf-psUpRgDJIUA/edit?usp=sharing) |

## Verdict

The only numbers are search-snippet figures from Matcheroni's 2023 results sheet (aappleby's own shootout of the mariomka/regex-benchmark Email, URI and IPv4 patterns, -O3, compiler reportedly GCC 14, CPU, std::regex implementation and SRELL version unstated): SRELL about 0.0174 vs std::regex 0.724 (about 41x, derived from page data, unit not visible), with Boost, CTRE and Matcheroni in between. A second snippet of per-pattern values shows SRELL slower than std::regex on Email, but its sub-millisecond whole-file times do not fit the first set and probably come from another run or harness, so the ranking is unconfirmed.

## Use it when

- C++ code already written against std::regex where matching is slow and you want a header-only replacement with the same class and function names.
- Patterns that need JavaScript semantics or features std::regex lacks: lookbehind, named groups, \p{Script=...} properties, case folding across all of Unicode.
- Matching UTF-8, UTF-16 or UTF-32 text by code point (u8cregex, u16regex, u32regex) without converting to wide strings first.
- Projects that must vendor a dependency-free, BSD-2-Clause header and can build with old compilers (pre-C++11 is still considered in the change history).
- Search-heavy loops on x86-64 where a literal or small character class starts the pattern, so the BMH or SIMD start-position scan does most of the work.

## Skip it when

- Untrusted patterns or inputs: it is a backtracking engine, so catastrophic patterns hit the backtrack limit (2^21 failures by default) and throw regex_error(error_complexity) instead of running in linear time; prefer an RE2-family engine there.
- Multi-pattern or bulk stream scanning (IDS signatures, log grepping at GB/s): Hyperscan or Vectorscan compile many patterns into one automaton and are in a different throughput class.
- Builds where compile time or binary size matter: the Matcheroni author's sheet notes it adds a lot to build time and binary size by default, and the 'minimized' mode (SRELL_NO_UNICODE_DATA and other SRELL_NO_\* macros) is still slow to build.
- Code that relies on std::regex basic, extended, awk, grep or egrep grammars: those flags are defined as 0 in srell.hpp and silently fall back to ECMAScript.
- Teams that need a public bug tracker or vetted releases: bugs go to the author by email, and the change history lists a steady stream of optimiser bugs that returned wrong matches or crashed.

## How it is fast

The compiled pattern is a backtracking NFA that the author tunes with first-character analysis: an 'entry state selector' (since 4.019) picks where matching can start, literal patterns go through a Boyer-Moore-Horspool search, and the candidate start positions are found with memchr or an SSE4.2 _mm_cmpestri range scan (since 4.061, chosen at run time via cpuid/__builtin_cpu_supports; memchr preferred when AVX2 is present since 2026.03). Many pattern-specific rewrites (single-character-class runs A\*B, C{n,m}, shared-prefix alternatives) cut backtracking, and a unified pointer-based backtrack stack is used for contiguous iterators. There is no DFA or Thompson-NFA path, so worst-case time is still exponential.

## Compared with alternatives

Pick SRELL over Hyperscan, Vectorscan or rejit when you need captures, backreferences, lookaround and Unicode properties behind the std::regex API in a single header; pick re2jit or another RE2-family engine when patterns or inputs are untrusted and linear-time matching matters more than ECMAScript features.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none; srell.hpp plus srell_ucfdata2.h (case folding) and srell_updata3.h (Unicode properties), or the merged single-header version |
| **Minimum toolchain** | Change history (4.100) still fixes pre-C++11 builds; FreeBSD port declares c++11-lang; char16_t/char32_t typedefs need C++11 and u8regex needs C++20 char8_t; int and size_t must be at least 32 bits since 4.100 |
| **Platforms** | any; x86/x64 gets an SSE4.2 (and AVX2-aware) start-position scan with a run-time CPU check, disabled by defining SRELL_NO_SIMD |
| **Thread safety** | Not documented. search() is a const member of basic_regex and keeps backtracking state in a per-call search-state object, so sharing one compiled regex read-only across threads appears safe (inferred from srell.hpp, not stated by the author). |
| **Drop-in for the baseline** | partial — same class and function names in namespace srell and the default grammar is ECMAScript in both, but SRELL follows current ECMAScript semantics, ignores the non-ECMAScript grammar flags, can throw error_complexity on heavy backtracking, and adds SRELL-specific flags and char8_t/char16_t/char32_t support |

## Gotchas

- Backtracking is capped: each search attempt fails with error_complexity after 1 &lt;&lt; 21 backtrack failures (lowered from 1 &lt;&lt; 24 in 4.055), which throws regex_error unless the quiet flag or SRELL_NO_THROW is used; define SRELL_NO_LIMIT_COUNTER to remove the cap (and accept hangs).
- srell::regex on char works on bytes; use u8cregex (or u8regex with char8_t) to match UTF-8 by code point, otherwise \w, '.' and \p{} see code units.
- The optimiser has a history of correctness bugs found after release: wrong leftmost matches from the 4.019 entry-state selector (fixed 4.026/4.027, August 2023), /(?:a|ab|abc)\$/ matching 'ac' (4.021 to 4.037), a 64-bit crash on /ab|ac|ad/ (4.020 to 4.033), memory corruption in u32regex with SIMD (fixed 4.064), crashes on /(?:|)a/ (fixed 2026.00) and wrong results for /(|\w\*)+/ (fixed 2026.05); pin a recent version.
- Bug reports go to the author by email; the only GitHub presence is the data-man/SRELL mirror, which asks not to file issues there.

## Known shortcomings

- Tier C, snippet only: the Matcheroni author's Google sheet (0.0174093 vs std::regex 0.724126) and akenotsuki.com are blocked, one snippet shows SRELL about 12x slower than std::regex on Email, and in Matcheroni's harness the SRELL case is commented out and would not build as-is; no CPU stated. BSD-2-Clause confirmed from the FreeBSD port Makefile (2026.05).
- Enricher (orphaned file): in the competitor's one-shot harness the timer starts after each regex iterator is constructed (first search untimed for std::regex, Boost and SRELL but not for Matcheroni or CTRE), each pattern runs once, match counts are never cross-checked, and the SRELL case is commented out and no longer compiles. Backtracking is capped at 1 &lt;&lt; 21 failures per search (error_complexity, throws unless quiet or SRELL_NO_THROW; SRELL_NO_LIMIT_COUNTER removes the cap); char regexes work on bytes (use u8cregex for code points). The optimiser has a history of post-release correctness bugs (wrong leftmost matches 4.019-4.027, /(?:a|ab|abc)\$/ matching 'ac' 4.021-4.037, a 64-bit crash on /ab|ac|ad/ 4.020-4.033, u32regex SIMD memory corruption fixed 4.064, crashes on /(?:|)a/ fixed 2026.00, wrong results for /(|\w\*)+/ fixed 2026.05), so pin a recent version; bug reports go by email, the data-man/SRELL mirror refuses issues. Version 2026.07 (2026-09-17), BSD-2-Clause, header-only.

## Caveats and trade-offs

SNIPPET ONLY: akenotsuki.com, docs.google.com, linux.org.ru, lists.libreplanet.org and freshports.org were egress-blocked, so the results sheet was never opened; the 0.0174093 (SRELL) vs 0.724126 (std::regex) figures come from WebSearch summaries with no visible unit. A separate snippet attributed to a linux.org.ru SRELL 4.056 announcement gives per-pattern ms values in which SRELL is about 12x slower than std::regex on Email (0.018666 vs 0.001538) and roughly equal on URL (0.000253 vs 0.000294) and IP4 (0.000336 vs 0.000362), with Boost fastest on all three, so the speed ranking is contested and depends on the run. The numbers come from a competitor's (Matcheroni) shootout of the mariomka/regex-benchmark patterns; the current harness examples/regex/regex_benchmark.cpp has the SRELL case commented out (#define REGEX_BENCHMARK_SRELL disabled) and its SRELL block calls unqualified read()/timestamp_ms() where the other engines use utils::, so it no longer builds as-is and the sheet reflects an older harness (matcheroni/benchmark.cpp in the mid-2023 README). Every engine's timer starts after the regex iterator is constructed, so the first search is excluded from all timings. No CPU model, no confirmed compiler (GCC 14 only from a search summary), and the std::regex implementation (libstdc++ vs libc++) is unstated. License confirmed from the FreeBSD port Makefile (BSD2CLAUSE); activity inferred from the 2026.05 port version.

Header-only template library with the std::regex class design but an ECMAScript-compatible engine with native Unicode (char8_t/char16_t/char32_t). By default it adds a lot to build time and binary size (the same README says so); a 'minimized' mode shrinks the binary but is still slow to build. ECMAScript semantics, not the std::regex default grammar, so patterns can differ.

## Maintenance

Actively maintained by a single author (version 2026.07 of 2026-09-17 adds Unicode 18.0.0, eight releases between March and September 2026), BSD-2-Clause and header-only, so it is easy to vendor; the cited speed rests on a competitor's one-shot harness in which the timer starts after each regex iterator is constructed (so the first search is untimed for std::regex, Boost and SRELL but not for Matcheroni or CTRE), each pattern runs once with no repetition, match counts are never cross-checked, and the SRELL case is now commented out and no longer compiles (unqualified read()/timestamp_ms()); the measured SRELL build (mid-2023, about 4.019-4.022) predates several match-correctness fixes and the SIMD prefilter, so the numbers are neither current nor reproducible.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The results sheet (docs.google.com) and the SRELL site are egress-blocked, so the numbers rest on search snippets only; the opened Matcheroni README at commit 53d152f links the sheet and ranks SRELL 'the performance champion' and std::regex 'terrible by all metrics' without numbers, and the public harness names no CPU model, so C at most.
- **Verifier notes:** Keep at C with snippet-only numbers and a contested ranking (one snippet shows SRELL slower than std::regex on the Email pattern); the competitor harness is public but its SRELL case is disabled and stale. License BSD-2-Clause confirmed via the FreeBSD ports Makefile mirror on GitHub; SRELL has no GitHub repo and the site could not be opened.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-20 (wave 3); enricher (wave 3)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/aappleby/Matcheroni/HEAD/README.md>
  - <https://raw.githubusercontent.com/aappleby/Matcheroni/53d152f/README.md>
  - <https://github.com/aappleby/Matcheroni/tree/main/examples/regex>
  - <https://github.com/aappleby/Matcheroni/tree/53d152f>
  - <https://raw.githubusercontent.com/aappleby/Matcheroni/HEAD/examples/regex/regex_benchmark.cpp>
  - <https://raw.githubusercontent.com/freebsd/freebsd-ports/main/devel/srell/Makefile>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/benchmarks/engines.toml>
- **Sources the enricher read:**
  - https://www.akenotsuki.com/misc/srell/en/ (EGRESS_BLOCKED)
  - <https://github.com/data-man/SRELL>
  - <https://raw.githubusercontent.com/data-man/SRELL/trunk/README.md>
  - <https://raw.githubusercontent.com/data-man/SRELL/trunk/readme_en.txt>
  - <https://raw.githubusercontent.com/data-man/SRELL/trunk/history_en.txt>
  - <https://raw.githubusercontent.com/data-man/SRELL/trunk/license.txt>
  - <https://raw.githubusercontent.com/data-man/SRELL/trunk/srell.hpp>
  - <https://raw.githubusercontent.com/aappleby/Matcheroni/HEAD/README.md>
  - <https://raw.githubusercontent.com/aappleby/Matcheroni/53d152f/README.md>
  - <https://raw.githubusercontent.com/aappleby/Matcheroni/HEAD/examples/regex/regex_benchmark.cpp>
  - <https://github.com/aappleby/Matcheroni/tree/53d152f/matcheroni>
  - <https://github.com/aappleby/Matcheroni/commits/main/matcheroni/benchmark.cpp>
  - <https://raw.githubusercontent.com/aappleby/Matcheroni/7ab1506/matcheroni/benchmark.cpp>
  - <https://raw.githubusercontent.com/freebsd/freebsd-ports/main/devel/srell/Makefile>
  - <https://raw.githubusercontent.com/BurntSushi/rebar/HEAD/benchmarks/engines.toml>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://akenotsuki.com/misc/srell/en`) · [data/wave3/enrich/raw/akenotsuki_com_misc_srell_en.json](../../../data/wave3/enrich/raw/akenotsuki_com_misc_srell_en.json) (enrichment confidence 0.6)

</details>
