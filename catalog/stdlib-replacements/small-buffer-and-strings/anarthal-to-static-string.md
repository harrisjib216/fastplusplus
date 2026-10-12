# to_static_string

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟡 stale

> Header-only C++17 wrapper over std::to_chars that returns a stack-based string, replacing allocating, locale-dependent std::to_string.

| | |
|---|---|
| **Beats** | std::to_string |
| **Claimed result** | std::to_string(long) 45.3ns vs to_static_string(long) 27.7ns vs std::to_chars(long) 27.4ns; std::to_string(double) 1245ns vs to_static_string(double) 95.6ns vs std::to_chars(double) 98.4ns (numbers verbatim from README table; \~1.6x and \~13x ratios are derived from page data) |
| **Workload** | Converting long integers and doubles to strings via Google Benchmark, comparing std::to_string, to_static_string, and std::to_chars. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-10510U @ 1.80GHz |
| **Compiler and flags** | clang-18, CMake Release build (CMakeLists.txt sets no extra optimization flags), C++20, libstdc++ on Ubuntu 22.04 |
| **Adoption** | 1 star |
| **Last commit** | 2024-01-13 |
| **Links** | [repository](https://github.com/anarthal/to-static-string) · [benchmark](https://github.com/anarthal/to-static-string) |

## Verdict

On an i7-10510U @ 1.80GHz with clang-18, CMake Release, C++20, libstdc++ (Ubuntu 22.04), via Google Benchmark: std::to_string(long) 45.3ns vs to_static_string(long) 27.7ns (\~1.6x), and std::to_string(double) 1245ns vs to_static_string(double) 95.6ns (\~13x). In both cases to_static_string tracks raw std::to_chars almost exactly (27.7 vs 27.4ns; 95.6 vs 98.4ns), so the measured win is really std::to_chars' win over std::to_string, delivered through a safer wrapper.

## Use it when

- Hot-path numeric-to-string conversion (logging, serialization, protocol encoding) where allocation matters
- Formatting doubles specifically, where the gap over std::to_string is largest (\~13x in this benchmark)
- Code that wants a safe wrapper over std::to_chars without manually sizing and managing the output buffer
- C++17 codebases that want to_chars-level speed without hand-rolling buffer math
- Cases that need locale-independent, non-throwing numeric formatting

## Skip it when

- You need an owning std::string (e.g. stored beyond the current stack frame or in a container) — get() returns a string_view into a local buffer, so you must copy it into a std::string yourself
- You need custom formatting like thousands separators or printf-style width/padding — this only exposes what std::to_chars supports
- char8_t or other 'extension' integer types — README/tests mark these as untested TODOs
- You need release-build safety against conversion failure: errors from std::to_chars are only caught via assert(), which is compiled out under NDEBUG
- You need active maintenance or a track record — single author, 1 star, 0 forks, no commits since 2024-01-13

## How it is fast

It is a thin, noexcept wrapper around std::to_chars: no heap allocation, no locale lookups, no exceptions. All work happens in a fixed-size stack buffer sized per type at compile time. The large win over std::to_string(double) comes from libstdc++'s locale-aware, snprintf-based double formatting being far slower than to_chars' direct digit-generation algorithm; the integer case gains less because libstdc++'s std::to_string(long) is already close to to_chars speed.

## Compared with alternatives

Pick this over Str (MengRao/str) — the only sibling that also targets std::to_string/stoi — when you want a minimal, single-purpose std::to_chars wrapper rather than a broader string/parsing utility library; Str claims larger speedups but bundles more surface area than just numeric formatting.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself; Catch2 and Google Benchmark are only needed to build the tests/benchmarks |
| **Minimum toolchain** | C++17 (CMakeLists.txt sets target_compile_features(... cxx_std_17)); a TO_STATIC_STRING_CXX23_CONSTEXPR macro hints at future full-constexpr support once __cpp_lib_constexpr_charconv is available |
| **Platforms** | any platform with a std::to_chars implementation for the types used; only actually benchmarked on x86-64 Ubuntu 22.04 with clang-18/libstdc++ |
| **Thread safety** | not documented; the implementation holds no global or static state and each call operates on its own stack-local buffer, so concurrent calls appear independent, but this is not stated or tested by the project |
| **Drop-in for the baseline** | partial — same single-argument call shape as std::to_string and exposes a string_view via .get()/implicit conversion, but returns cstatic_string&lt;N&gt; (stack-based, tied to the call's scope), not std::string, so call sites needing an owning, heap-backed string must convert explicitly |

## Gotchas

- Buffer size N is fixed per type at compile time (rounded to 8/16/32 bytes for integers, or computed from max_digits10 for floats) — it is not user-configurable
- std::to_chars errors are only checked via assert(result.ec == std::errc()); in a release (NDEBUG) build a conversion failure is silently ignored rather than surfaced
- get() returns a std::string_view referencing the returned object's internal buffer — do not outlive the cstatic_string instance
- char8_t and other extension integer types are explicitly untested (marked '// TODO' in test/test.cpp)

## Caveats and trade-offs

Single-author project with only 1 star and a single benchmark machine (a laptop-class CPU); README itself says 'testing is still an ongoing effort'; no independent reproduction found.

Header-only and narrowly scoped to numeric-to-string conversion (not a general string/container replacement); non-allocating and non-throwing by design but feature surface is much smaller than std::string; very low adoption so far.

## Maintenance

Stale: single-author project, last commit 2024-01-13, 1 star, 0 forks, 0 open issues/PRs (low-traffic rather than actively triaged). BSL-1.0 licensed, header-only, and small enough (\~150 lines) to read in full and vendor despite the inactivity; note vcpkg.json's manifest license field says 'MIT', which conflicts with the repository's actual BSL-1.0 license (LICENSE_1_0.txt and file headers) — treat BSL-1.0 as authoritative.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README table numbers match exactly. The benchmark code is public (bench/bench.cpp, Google Benchmark, directly calling std::to_string and std::to_chars), and the README states the CPU (i7-10510U), compiler (clang-18), build (CMake Release, C++20; CMakeLists.txt adds no extra flags) and stdlib (libstdc++, Ubuntu 22.04).
- **Verifier notes:** to_static_string wraps std::to_chars and runs at parity with it (27.7 vs 27.4 ns; 95.6 vs 98.4 ns), so the real win is only over std::to_string. The baseline was narrowed to std::to_string for that reason. Metadata checks out: BSL-1.0, 1 star, last commit 2024-01-13, stale.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://github.com/anarthal/to-static-string>
  - <https://github.com/anarthal/to-static-string/blob/master/bench/bench.cpp>
  - <https://github.com/anarthal/to-static-string/blob/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/anarthal/to-static-string>
  - <https://github.com/anarthal/to-static-string/blob/master/README.md>
  - <https://github.com/anarthal/to-static-string/blob/master/include/tostr/to_static_string.h>
  - <https://github.com/anarthal/to-static-string/blob/master/CMakeLists.txt>
  - <https://github.com/anarthal/to-static-string/blob/master/vcpkg.json>
  - <https://github.com/anarthal/to-static-string/blob/master/bench/bench.cpp>
  - <https://github.com/anarthal/to-static-string/blob/master/test/test.cpp>
  - <https://github.com/anarthal/to-static-string/issues>
  - <https://github.com/anarthal/to-static-string/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/anarthal/to-static-string`) · [data/wave1/enrich/raw/github_com_anarthal_to_static_string.json](../../../data/wave1/enrich/raw/github_com_anarthal_to_static_string.json) (enrichment confidence 0.85)

</details>
