# Boost.Regex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Regex](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only successor to std::regex: same backtracking engine, hand-tuned matcher and pooled allocation for real throughput gains.

| | |
|---|---|
| **Beats** | std::regex |
| **Claimed result** | mariomka/regex-benchmark: C++ Boost 104.23 ms vs C++ STL (std::regex) 1023.49 ms total, \~9.8x (Email 44.97 vs 433.09 \~9.6x; URI 44.13 vs 344.74 \~7.8x; IPv4 15.13 vs 245.66 \~16.2x); the 'optimized' table shows 104.28 vs 1021.10. Supporting evidence from the rust-leipzig/regex-performance chart (results_20221012.png, ms): Boost was faster on 13 of the 14 patterns both engines ran, from \~1.0x ('[a-z]shing' 323.5 vs 326.1) up to \~48.5x ('Tom\|Sawyer\|Huckleberry\|Finn' 12.2 vs 591.3; 'Twain' 8.7 vs 223 \~26x; '\u221E\|\u2713' 7.3 vs 340.7 \~47x). It was slower on '([A-Za-z]awyer\|[A-Za-z]inn)\s' (800.8 vs 595). On '(.\*?,){13}z' std::regex took 17989.3 while Boost was n/a. |
| **Workload** | mariomka/regex-benchmark: find and count non-overlapping matches of 3 patterns (Email, URI, IPv4) over a concatenation of the Learn-X-in-Y-minutes docs. The timing includes pattern compilation. Supporting: rust-leipzig regex_perf runs 18 patterns (literal, alternation, character classes, bounded repeats, case-insensitive variants, one catastrophic-backtracking pattern) over 3200.txt (\~16 MB). The README says 'best of 5', but src/boost.cpp and src/cppstd.cpp actually record the mean of 5 runs, in ms. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (16-inch, 2019), 2.4 GHz Intel Core i9, 32 GB 2667 MHz DDR4, macOS Big Sur 11.2.3, running a Docker ubuntu:bionic image (mariomka). The supporting rust-leipzig run used an AMD Threadripper 3960X (Zen2) at 3.8 GHz on Ubuntu 20.04.5 LTS. |
| **Compiler and flags** | g++ 7.5.0, -std=c++11 -O3, Boost 1.65.1 (mariomka run-benchmarks.php / cpp/README.md). The supporting rust-leipzig run used CMake Release -O3 -march=native with CMAKE_CXX_FLAGS -std=c++11; its compiler and version are not stated. |
| **Adoption** | 119 stars on this GitHub submodule mirror (boostorg/regex); Boost overall is one of the most widely deployed C++ library collections |
| **Last commit** | 2026-05-22 |
| **Links** | [repository](https://github.com/boostorg/regex) · [benchmark](https://github.com/mariomka/regex-benchmark) |

## Verdict

On mariomka/regex-benchmark (g++ 7.5.0, -std=c++11 -O3, Boost 1.65.1 linked via -lboost_regex, Docker ubuntu:bionic on a 2019 MacBook Pro i9), Boost.Regex compiled and matched 3 patterns (Email/URI/IPv4) over the Learn-X-in-Y-minutes corpus in 104ms total versus 1023ms for libstdc++'s std::regex (\~9.8x, including compilation time). The independent rust-leipzig regex-performance suite (18 patterns over a \~16MB text file, AMD Threadripper 3960X, compiler unstated) confirmed the same direction on 13 of 14 shared patterns, from \~1.0x up to \~47x, losing on one alternation-heavy pattern ('([A-Za-z]awyer|[A-Za-z]inn)\s').

## Use it when

- Need std::regex-shaped semantics (ECMAScript/Perl/POSIX syntax, smatch-like results) but higher matching throughput on typical (non-adversarial) patterns.
- Pattern set is compiled once and reused across many inputs, so per-call matching cost dominates over one-time compilation.
- Need the POSIX regcomp/regexec API, MFC string support, or ICU/Unicode string iteration that std::regex does not provide.
- Already on or willing to add Boost (or the standalone header mode) and accept BSL-1.0, for a well-documented \~9.8x total / up to \~47x per-pattern win over libstdc++ std::regex on text-scanning workloads like log or URI/email extraction.
- Building against Boost 1.77+ where the library is header-only, so no extra link step is needed for the core C++ API.

## Skip it when

- Patterns come from untrusted input (user-supplied regex or unbounded nested quantifiers/alternation): this is the same backtracking/ReDoS risk class as std::regex, not a safer engine (see GH issue #178, 'Subroutine call backtracking bug').
- Need a hard guarantee of linear-time matching regardless of pattern shape -- pick a DFA/Thompson-NFA engine like RE2 instead of any backtracking engine, including this one.
- Targeting Boost older than 1.77 (before Boost.Regex 6.0.0, 2021) where the library still requires linking a compiled boost_regex lib, as the mariomka benchmark used (Boost 1.65.1, built with -lboost_regex).
- Want a truly zero-dependency drop-in: even in standalone mode you still add a distinct type hierarchy (boost::regex != std::regex); non-standalone mode also pulls in Boost.Config/Assert/Predef/ThrowException.
- Small, one-off, latency-sensitive regex use where std::regex's ubiquity and zero extra header outweigh a \~2x-ish smaller, but still real, integration cost.

## How it is fast

Same backtracking-NFA design as std::regex: basic_regex_creator compiles the pattern into a graph of states, then perl_matcher walks it. The implementation is heavily hand-tuned around that: a non-recursive matcher (perl_matcher_non_recursive.hpp) that uses an explicit stack instead of C++ call recursion, a pooled memory-block allocator (mem_block_cache.hpp) that reuses backtracking-stack memory across matches instead of hitting the heap, precompiled character-class bitmaps, and a leading-literal fast-skip so scanning for a required prefix doesn't reevaluate the whole state machine at every position. There is no SIMD and no asymptotic change over backtracking matching -- the win is fewer allocations and tighter C++, and it can still hit catastrophic backtracking on adversarial patterns just like std::regex.

## Compared with alternatives

Pick Boost.Regex over RE/flex or REAL when you want an API and feature set (POSIX/ICU/MFC support, Perl/ECMAScript syntax) almost identical to std::regex for an easy migration, rather than adopting a scanner-generator workflow (RE/flex) or a from-scratch header-only engine (REAL/real-regex) for their larger reported multipliers. Unformat is not comparable here -- it only handles fixed-shape format strings at compile time, not general regex.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none in standalone mode (BOOST_REGEX_STANDALONE, or auto-detected under C++17 with __has_include when &lt;boost/version.hpp&gt; is absent); otherwise Boost.Config, Boost.Assert, Boost.Predef, Boost.ThrowException. Optional ICU for Unicode string integration. The POSIX C API (src/posix_api.cpp, src/wide_posix_api.cpp) is still compiled/linked separately if used. |
| **Minimum toolchain** | C++11 minimum; C++03 support was formally deprecated in 6.0.0/Boost 1.77 (doc/history.qbk). C++17 is only needed for automatic standalone-mode detection via __has_include, not as a hard floor. |
| **Platforms** | any (portable C++; no SIMD/ISA requirement found in headers or docs) |
| **Thread safety** | Documented (doc/html/.../thread_safety.html): basic_regex/regex/wregex are safe to compile once and share read-only across threads; regex_match/regex_search/regex_replace and the POSIX functions are reentrant; match_results can be copied between threads but needs a separate instance per thread if used concurrently; calling set_locale from one thread while another thread is matching is unsafe; requires only one thread running before main() starts. |
| **Drop-in for the baseline** | partial -- explain: API shape (regex_match/regex_search/regex_replace, smatch/cmatch) mirrors std::regex almost 1:1, but boost::regex is a distinct type from std::regex, so switching means editing type names and includes, not just relinking. |

## Gotchas

- Header-only status is recent (Boost.Regex 6.0.0 / Boost 1.77, 2021, confirmed via CMakeLists.txt's `add_library(boost_regex INTERFACE)`); the benchmark numbers in this record used Boost 1.65.1, compiled with `-lboost_regex`, from before that change.
- Same backtracking design as std::regex: pathological patterns can still blow up, with no linear-time guarantee (GH #178).
- Standalone mode drops Boost.Config's compiler-defect workarounds; if you disable exceptions in standalone mode you must define BOOST_NO_EXCEPTIONS yourself.
- Changing the global C locale from one thread while another thread is mid-match is explicitly called out as unsafe in the docs.

## Caveats and trade-offs

The mariomka numbers are from 2021 (last commit 2021-10-18) with Boost 1.65.1 and libstdc++ from g++ 7.5.0, and its timings include regex compilation. The rust-leipzig chart is PNG-only, does not state the compiler, and its README misdescribes aggregation (says best-of-5, code computes the mean). A third source, c0rp3n/regex-bench (archived, 2 stars, Ryzen 2700X), shows std::regex 44662340 ns vs boost::regex 4875681 ns (\~9.2x), with compiler and flags not stated. GitHub reports a null license for boostorg/regex, but the headers carry the Boost Software License 1.0.

Same backtracking-NFA design as std::regex (shares its ReDoS risk class); not header-only, requires linking the compiled Boost.Regex library; larger dependency footprint than std::regex.

## Maintenance

Actively maintained (last commit 2026-05-22 on the default branch) and BSL-1.0 licensed, so freely copyable/vendorable; GitHub reports a null license for the repo, but the header comments carry the Boost Software License 1.0 text directly.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The original benchmark_url (rust-leipzig/regex-performance chart) states flags (CMake Release -O3 -march=native) and hardware but not the compiler, so on its own it would be B (independent third-party suite). The independent mariomka/regex-benchmark meets A in full: in-repo code cpp/benchmark.cpp built by run-benchmarks.php as 'g++ -std=c++11 -O3' (with and without -DUSE_BOOST), g++ 7.5.0 / Boost 1.65.1 stated, and the hardware stated. benchmark_url was switched to that source.
- **Verifier notes:** The direction (Boost.Regex much faster than libstdc++ std::regex) is confirmed by three independent suites. The original chart numbers check out; the only error was the pattern '\u221e|\u221a', which is actually '\u221E|\u2713' in src/main.c. last_commit on the default branch (develop) is 2026-05-22; 2026-08-13 is the repo's pushed_at, likely from a non-default branch. Still active.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rust-leipzig/regex-performance/blob/master/results_20221012.png>
  - <https://github.com/rust-leipzig/regex-performance>
  - <https://github.com/boostorg/regex>
  - <https://github.com/mariomka/regex-benchmark>
  - <https://github.com/c0rp3n/regex-bench>
- **Sources the enricher read:**
  - <https://github.com/boostorg/regex>
  - <https://github.com/boostorg/regex/blob/develop/README.md>
  - <https://github.com/boostorg/regex/blob/develop/include/boost/regex/config.hpp>
  - <https://github.com/boostorg/regex/blob/develop/doc/html/boost_regex/background/thread_safety.html>
  - <https://github.com/boostorg/regex/blob/develop/doc/html/boost_regex/configuration/standalone.html>
  - <https://github.com/boostorg/regex/blob/develop/CMakeLists.txt>
  - <https://github.com/boostorg/regex/blob/develop/doc/history.qbk>
  - <https://github.com/boostorg/regex/blob/develop/doc/standards.qbk>
  - <https://github.com/boostorg/regex/blob/develop/doc/performance.qbk>
  - <https://github.com/boostorg/regex/issues>
  - <https://github.com/mariomka/regex-benchmark/blob/master/cpp/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/boostorg/regex`) · [data/wave1/enrich/raw/github_com_boostorg_regex.json](../../../data/wave1/enrich/raw/github_com_boostorg_regex.json) (enrichment confidence 0.82)

</details>
