# FastFormat

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Type-safe C++ formatting library (positional fmt and concatenating write) that beats IOStreams and Boost.Format; mixed against printf.

| | |
|---|---|
| **Beats** | C stdio snprintf (printf family), plus C++ IOStreams and Boost.Format |
| **Claimed result** | Times relative to FastFormat.Format (above 1.0 means FastFormat.Format faster), averaged over five platform/compiler rows, scenarios 1-7: 'Streams (snprintf())' 1.49, 0.83, 1.15, 0.66, 1.63, 6.87, 1.64; IOStreams 3.28, 2.16, 5.08, 2.41, 2.82, 9.96, 2.86; Boost.Format 10.29, 5.18, 12.10, 5.57, 8.68, 17.27, 8.94; Loki.SafeFormat 2.28, 1.36, 2.03, 1.35, 2.17, 5.47, 2.16; FastFormat.Write 0.74, 0.84, 0.61, 0.81, 0.70, 0.88, 0.71. Page summary: faster than Streams by 15-580% except scenarios 2 and 4 (17% and 34% slower); faster than IOStreams by \~100-900% in all cases; faster than Boost.Format by \~400-1650%; FastFormat.Write is \~25% faster than FastFormat.Format and faster than all competitors except in scenarios 2 and 4. Headline: 5-17 times faster than Boost.Format, 1.5-5.5 times faster than Loki.SafeFormat. |
| **Workload** | Seven scenarios from the FastFormat 0.2.1 beta 6 test/performance programs, each formatting into a std::string per iteration with functional equivalents for the other libraries: (1) 'My name is {0} {1}; I am {2} years old; call me {0}' (cvu.ex.1); (2) name, int age, float height for five records (name_age_height); (3) one int from INT_MIN to INT_MAX (one_integer); (4) one pointer (one_pointer); (5) three strings with repeats (scenario1); (6) ten strings, including a 1000-char one, formatted twice (ten_strings_twice); (7) three strings and one int (three_strings_one_integer). Run on Ubuntu x86 (GCC 4.2), Ubuntu x64 (GCC 4.1), Windows x86 (Visual C++ 6 and 9) and Windows x64 (Visual C++ 9); timed with the STLSoft platformstl performance_counter. |
| **Metric** | throughput |
| **Compiler and flags** | GCC 4.1, GCC 4.2, Visual C++ 6, Visual C++ 9; optimisation flags not stated |
| **Adoption** | 58 stars |
| **Last commit** | 2026-08-04 |
| **Links** | [repository](https://github.com/synesissoftware/FastFormat) · [benchmark](https://fastformat.sourceforge.net/performance.html) |

## Verdict

The author's 2008-2009 page (FastFormat 0.2.1 beta 6; GCC 4.1/4.2 on Ubuntu x86/x64 and Visual C++ 6/9 on Windows x86/x64; no CPU or flags) times seven std::string-building scenarios at 100,000 iterations each: averaged over the five rows FastFormat.Format is 5-17x faster than Boost.Format, about 2-10x faster than IOStreams, and 0.66-6.87x versus the printf family, losing on the float and pointer scenarios and, per the record's derivation, losing to glibc sprintf in 11 of 14 GCC cells.

## Use it when

- Building strings from many string-like pieces (std::string, C strings, string views, long payloads) where knowing lengths up front and one reservation beat sprintf's strlen-and-copy plus a second copy into std::string (the 6.9x scenario was ten strings including a 1000-char one)
- Replacing Boost.Format or IOStreams string building in hot paths with a type-safe API (5-17x and roughly 2-10x on the author's tables)
- Code already built on STLSoft or Pantheios, where the shim mechanism lets your own types format without extra glue
- I18N-style positional patterns where an argument is referenced several times ({0} reused)

## Skip it when

- Floating-point or pointer formatting: FastFormat calls sprintf("%G") / snprintf("%p") internally, so it cannot beat printf there and lost to it on average in exactly those scenarios (2 and 4)
- New projects that can use {fmt} or C++20 std::format: same positional, type-safe model, maintained, with native fast float formatting
- Builds on Windows with the current repo: the CMake build stops with 'Use of CMake on Windows not currently supported' and the legacy makefiles were removed, although most of the published wins over printf came from Visual C++ rows
- Projects that cannot take STLSoft (and xTests for the tests) as dependencies or that need a packaged, released library (latest is 0.7.4 RC 6 from February 2024)
- Formatting char or bool values without writing your own shim: those conversion shims are marked 'Feature not yet implemented' in fastformat.hpp

## How it is fast

Each argument is turned into a (pointer, length) string slice without a format-specifier interpreter; the sink then sums the slice lengths, reserves once and appends (shims/action/fmt_slices/generic_string.hpp), so a std::string target is grown a single time. Format patterns are parsed once and cached in a process-wide std::map (src/fmt_cache.cpp), so repeated literal patterns skip parsing, unlike Boost.Format which re-parses per call. Integers go through STLSoft's integer_to_string; doubles and pointers are not converted natively but by calling sprintf("%G") and snprintf("%p").

## Compared with alternatives

{fmt} is the catalogued sibling with the same type-safe, positional API and is far faster on doubles (20x over sprintf per its benchmark, where FastFormat just calls sprintf); pick FastFormat only for string-concatenation-heavy code already on STLSoft/Pantheios, and use Ryu, Dragonbox or the to_chars libraries for number conversion.

## Integration

| | |
|---|---|
| **Form** | static lib (src/\*.cpp: api, fmt_cache, memory_pool, replacements, snprintf) plus headers |
| **Dependencies** | STLSoft headers (1.9.121+ per INSTALL.md; CMake looks for STLSoft 0.10.8+ and xTests 0.21.2+ when BUILD_TESTING is on); Boost and Loki only for the comparison benchmarks |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11), CMake 3.20; library built with -Werror -Wall -Wextra -pedantic on GCC/Clang |
| **Platforms** | Unix-like (Linux, macOS) via CMake; Windows only historically (CMake build refuses Windows) |
| **Thread safety** | The pattern cache is a process-wide std::map guarded by a platformstl thread_mutex only when FASTFORMAT_MT is defined (Unix: UNIXSTL_USING_PTHREADS; Windows: _MT/_REENTRANT/__MT__); without it a null_mutex is used and concurrent fmt() calls are unsafe. Sinks are not synchronised (ostream sink locking is on the TODO list). |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark harness: the scenarios FastFormat loses against the printf family (2: float height, 4: pointer) are the ones where FastFormat itself delegates to sprintf("%G") and snprintf("%p"), so those losses are structural, not noise; the 'Streams (snprintf())' column actually times unbounded ::sprintf into a fixed stack buffer plus a std::string copy, and output equality is checked only in debug builds (#ifndef NDEBUG).
- Benchmark harness: the IOStreams column constructs a fresh std::stringstream per call and the Format column always hits its pattern cache with one literal pattern, which flatters the IOStreams and Boost.Format ratios relative to code that reuses a stream or has many distinct patterns.
- Doubles print with %G, not %g: 6 significant digits, uppercase exponent and INF/NAN, so output differs from printf("%g") and is not round-trip safe.
- Every fmt() call takes the pattern-cache mutex in MT builds and the cache grows without bound with each distinct pattern string; use write() or literal patterns in hot or multi-threaded code.

## Known shortcomings

- performance.html numbers from 2008 compilers (GCC 4.1/4.2, VC6/VC9) with no CPU or flags; on Ubuntu/GCC glibc snprintf is faster than FastFormat.Format in 11 of 14 cells (derived from page data), so the printf win comes mostly from the MSVC CRT rows. The 2026-08-04 commit is boilerplate only.
- Enricher: floats go through sprintf("%G") (reals.hpp) and pointers through snprintf("%p") (void_pointers.hpp), exactly the two scenarios (2, 4) FastFormat loses to printf, so the losses are built in; the IOStreams column builds a new stringstream per call; Format always hits its pattern cache (std::map under a mutex); output is checked only in debug builds. Current CMake refuses Windows (FATAL_ERROR) although the MSVC rows carried the printf wins; %G not %g output; char/bool shims are 'not yet implemented'.

## Caveats and trade-offs

Author's own page from the 2008-2009 era (FastFormat 0.2.1 beta 6; GCC 4.1/4.2, Visual C++ 6/9); no CPU, RAM, optimisation flags or date are given. The printf-family win comes from the MSVC CRT rows: on the two Ubuntu/GCC rows glibc snprintf beat FastFormat.Format in 11 of 14 cells (FastFormat.Format won only scenario 6 on both and scenario 3 on x86; derived from page data), and the page itself reports FastFormat.Format 17% and 34% slower than snprintf on average in scenarios 2 and 4. FastFormat.Write beat glibc snprintf in 10 of 14 GCC cells, losing scenarios 2 and 4 (derived from page data). The averages mix platforms and compilers. The current repo's harness (test/performance/\*, updated February 2024) times ::sprintf into a 10001-char stack buffer followed by a std::string construction, while the page labels the column snprintf(). The IOStreams column is the C++ standard library (libstdc++ of GCC 4.1/4.2 and the Visual C++ 6/9 library), so the C++ comparison is direct but on toolchains that are 15+ years old. The ACCU Overload 91 article (June 2009) could not be opened (egress blocked); a web search snippet reports about 3x faster than printf-family, 6x faster than IOStreams and 17x faster than Boost.Format. Requires the header-only STLSoft 1.9.121+ library. The only commit since February 2024 is 'Boilerplate (#4)' (2026-08-04), so 'active' reflects project scaffolding, not new performance work.

Type-safe, no format-string parsing for the Write API; relies on the STLSoft and Pantheios-style support libraries and sink objects; Format (replacement-based, I18N friendly) is slower than Write (concatenation-based). Needs its own inserter functions for user types.

## Maintenance

BSD-3-Clause and still buildable on Unix with CMake (added February 2024), but effectively dormant since 2017 apart from boilerplate commits (last 2026-08-04), never released past 0.7.4 RC 6, and its speed evidence is from 15-year-old compilers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's own performance page reports times relative to FastFormat.Format for seven scenarios against a column labelled 'Streams (snprintf())', IOStreams, Boost.Format and Loki.SafeFormat, with compilers named (GCC 4.1/4.2, Visual C++ 6/9) and public benchmark code (test/performance/ in the repo, 'make test.performance' in the 0.2.1 beta 6 distribution), but no optimisation flags and no CPU model; first-party with partial methodology is C.
- **Verifier notes:** Numbers in the record match the page exactly (the column is labelled 'Streams (snprintf())'); keep at tier C. Shortcomings to record: no CPU or flags, 2008-era compilers, win over snprintf holds mainly against the MSVC CRT (glibc snprintf faster in 11 of 14 GCC cells, derived from page data), slower than snprintf in scenarios 2 and 4. Metadata checked: BSD-3-Clause, 58 stars, not a fork, not archived, last commit 2026-08-04 'Boilerplate (#4)' (prior commit 2024-02-06); corrected baseline_stdlib and compared_against_cpp_std_directly because IOStreams is measured.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `baseline_stdlib`, `compared_against_cpp_std_directly`, `caveats`
- **Shortcomings recorded by:** first-party performance.html (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://fastformat.sourceforge.net/performance.html>
  - <https://fastformat.sourceforge.net/performance_scenario1.html>
  - <https://fastformat.sourceforge.net/performance_scenario2.html>
  - <https://fastformat.sourceforge.net/performance_scenario3.html>
  - <https://fastformat.sourceforge.net/performance_scenario4.html>
  - <https://fastformat.sourceforge.net/performance_scenario5.html>
  - <https://fastformat.sourceforge.net/performance_scenario6.html>
  - <https://fastformat.sourceforge.net/performance_scenario7.html>
  - <https://github.com/synesissoftware/FastFormat>
  - <https://github.com/synesissoftware/FastFormat/tree/master/test>
  - <https://github.com/synesissoftware/FastFormat/tree/master/test/performance>
  - <https://github.com/synesissoftware/FastFormat/commits/master.atom>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/README.md>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/FAQ.md>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/CMakeLists.txt>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/test.performance.ten_strings_twice/test.performance.ten_strings_twice.cpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/test.performance.name_age_height/test.performance.name_age_height.cpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/test.performance.scenario1/test.performance.scenario1.cpp>
- **Sources the enricher read:**
  - <https://github.com/synesissoftware/FastFormat>
  - <https://github.com/synesissoftware/FastFormat/commits/master>
  - <https://github.com/synesissoftware/FastFormat/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/README.md>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/FAQ.md>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/CHANGES.txt>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/HISTORY.txt>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/KNOWN_ISSUES.txt>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/src/fmt_cache.cpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/src/api.cpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/include/fastformat/fastformat.h>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/include/fastformat/fastformat.hpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/include/fastformat/internal/threading.h>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/include/fastformat/shims/conversion/filter_type/reals.hpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/include/fastformat/shims/conversion/filter_type/void_pointers.hpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/include/fastformat/shims/action/fmt_slices/generic_string.hpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/include/fastformat/sinks/ostream.hpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/include/fastformat/sinks/char_buffer.hpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/CMakeLists.txt>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/test.performance.one_integer/test.performance.one_integer.cpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/test.performance.one_pointer/test.performance.one_pointer.cpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/test.performance.name_age_height/test.performance.name_age_height.cpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/test.performance.scenario1/test.performance.scenario1.cpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/test.performance.ten_strings_twice/test.performance.ten_strings_twice.cpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/test.performance.three_strings_one_integer/test.performance.three_strings_one_integer.cpp>
  - <https://raw.githubusercontent.com/synesissoftware/FastFormat/HEAD/test/performance/test.performance.overload.ex.1/test.performance.overload.ex.1.cpp>
  - <https://fastformat.sourceforge.net/performance.html>
  - <https://fastformat.sourceforge.net/performance_scenario2.html>
  - <https://fastformat.sourceforge.net/performance_scenario4.html>
  - <https://fastformat.sourceforge.net/performance_scenario6.html>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/synesissoftware/fastformat`) · [data/wave1/enrich/raw/github_com_synesissoftware_fastformat.json](../../../data/wave1/enrich/raw/github_com_synesissoftware_fastformat.json) (enrichment confidence 0.75)

</details>
