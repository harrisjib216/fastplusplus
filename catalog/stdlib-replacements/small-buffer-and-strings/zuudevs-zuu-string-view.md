# zuu_string_view

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Small-buffer containers and strings](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Header-only C++11 SWAR-accelerated string_view alternative; faster find/rfind/find_first_of than std::string_view, slower on not_of scans.

| | |
|---|---|
| **Beats** | std::string_view |
| **Claimed result** | find_first_of: zuu 6.11 ns vs std::string_view 15.7 ns (\~2.5x); find (substring): 11.1 vs 14.1 ns (\~1.3x); rfind (substring): 11.4 vs 16.7 ns (\~1.4x); find (char): 1.56 vs 2.24 ns (\~1.4x); find_last_of: 11.0 vs 14.7 ns (\~1.3x); rfind (char): 2.39 vs 2.50 ns (tie). zuu is SLOWER on find_first_not_of (6.22 vs 5.01 ns, \~20% slower) and find_last_not_of (6.82 vs 5.00 ns, \~26% slower). (ns values and approximate ratios are verbatim from the README table.) |
| **Workload** | find_first_of, find (substring), rfind (substring), and find (char) operations over string_view-like objects, measured with Google Benchmark. |
| **Metric** | latency |
| **Hardware** | Reported only as "12 x 2096 MHz CPU" (Google Benchmark auto-detected core count/clock) — no explicit CPU model name given |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-12 |
| **Links** | [repository](https://github.com/zuudevs/zuu_string_view) · [benchmark](https://github.com/zuudevs/zuu_string_view) |

## Verdict

README's first-party Google Benchmark table (one \~95-char haystack, compiler/flags/stdlib unstated, hardware reported only as '12x 2096 MHz CPU') shows zuu::string_view beating std::string_view on find_first_of (6.11 vs 15.7 ns, \~2.5x), find/substring (11.1 vs 14.1 ns), rfind/substring (11.4 vs 16.7 ns), find_last_of (11.0 vs 14.7 ns), and find/char (1.56 vs 2.24 ns), while std::string_view wins on find_first_not_of (5.01 vs 6.22 ns) and find_last_not_of (5.00 vs 6.82 ns).

## Use it when

- Hot-path find/rfind/find_first_of/find_last_of/find(char) calls over ASCII/byte strings (README's own test string is \~95 chars) where a few nanoseconds per call matters
- C++11-only codebases that want string_view-style ergonomics without raising the language standard
- Header-only vendoring is acceptable: just include/zuu/string_view.hpp + include/zuu/char_class.hpp, no build step
- Single-threaded or read-only-shared usage (it's a raw pointer+length pair with no internal synchronization)
- Data provably under \~4 billion characters, since length is stored as a 32-bit unsigned int

## Skip it when

- find_first_not_of / find_last_not_of-heavy code: the README's own numbers show zuu 20-26% slower than std::string_view there
- Buffers that could exceed \~4B characters, or code that assumes std::string_view's std::size_t-typed npos/return values
- wchar_t/char16_t/char32_t workloads or constexpr contexts: the SWAR path is disabled there (sizeof(CharT)==1 and non-constexpr only), so performance likely reduces to the scalar fallback, which is unbenchmarked
- Projects that need a licensed dependency to ship: no LICENSE file and no license field in vcpkg.json
- Teams wanting proven maturity: repo created 2026-09-11, all 30 commits land within about a day, 0 stars, 0 issues, no third-party validation

## How it is fast

The positive-search functions (find, rfind, find_first_of, find_last_of) use SWAR (SIMD-within-a-register): they memcpy 8 bytes at a time into a uint64_t 'tape', broadcast the needle byte(s) across all 8 lanes, XOR against the tape, and apply the classic branchless haszero/hasless byte-detection trick (0x7F7F...7F and 0x8080...80 masks) plus count_trailing_zeros/count_leading_zeros to locate the matching byte in one shot instead of a per-byte loop. Multi-char searches (find_first_of family) extend this with a 256-bit bitmap built from 4 uint64_t lookup words. This path only triggers for sizeof(CharT)==1 outside constexpr evaluation; everything else falls back to a scalar loop.

## Compared with alternatives

It's the only catalogued entry benchmarked against std::string_view itself (the other siblings target std::string/std::to_string), so pick it specifically when your bottleneck is string_view::find-family calls on a C++11 toolchain; for std::string construction/formatting/conversion speedups, use FastString, to_static_string, or Str instead.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself (Google Benchmark and GoogleTest are dev-only, pulled via vcpkg for building the tests/benchmarks) |
| **Minimum toolchain** | C++11 (CI builds it under GCC, Clang, MSVC, and Apple Clang with -DCMAKE_CXX_STANDARD=11); CMake 3.20+ if using the provided build |
| **Platforms** | CI covers Ubuntu 24.04 (GCC/Clang), Windows 2022 (MSVC), macOS 15 (Apple Clang); no vector intrinsics used (SWAR is plain uint64_t arithmetic), so it should build anywhere a 64-bit integer type exists |
| **Thread safety** | not documented; the view holds only an immutable pointer+length with no internal mutable state, so concurrent reads of the same view look safe by inspection, but the project does not state this |
| **Drop-in for the baseline** | partial — explain: API names and shape closely mirror std::string_view and it implicitly converts to/from std::string and std::string_view, but size_type/npos is `unsigned int` rather than std::size_t, so code comparing against std::string_view::npos or relying on 64-bit indices needs changes |

## Gotchas

- size_type and npos are `unsigned int` (32-bit), not std::size_t like std::string_view — a real interop gap, not just a naming difference
- The SWAR fast path only activates when sizeof(CharT)==1 and outside constexpr evaluation; wide-char types and constexpr calls silently use the scalar loop instead
- find_first_not_of and find_last_not_of are slower than std::string_view (20-26% per the README), the opposite of the library's headline claim
- No LICENSE file and no license field in vcpkg.json, so legal usability is unresolved even though the source is public

## Caveats and trade-offs

No LICENSE file and no license field in vcpkg.json (usability 'reference'); 0 stars, very early-stage project. The README does not state the compiler, flags, or stdlib for the benchmark run (CMakePresets.json defaults to clang++ with C++23, but the run is not tied to a preset). Hardware is given only as '12x 2096 MHz CPU'. Every benchmark uses one short (\~95-char) haystack. zuu is 20-26% slower than std::string_view on find_first_not_of and find_last_not_of.

Still a non-owning view like std::string_view, so offers no lifetime-safety improvement; C++11-compatible target may limit some modern-compiler optimizations available to libc++/libstdc++; extremely small/early codebase (31 commits) with minimal external validation.

## Maintenance

Actively developed as of the last commit (2026-09-12) but very early: v0.4.0, all 30 commits landed within about a day of creation (2026-09-11), 0 stars, and no LICENSE file, so treat it as unlicensed and unproven rather than production-ready.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table has first-party Google Benchmark numbers against std::string_view. Benchmark code is public (benchmarks/api/string_view_find.cpp, string_view_search_scenarios.cpp), but the README gives no CPU model (only '12x 2096 MHz'), no compiler, no flags, and no stdlib, so the tier is C.
- **Verifier notes:** The README numbers match the record exactly. I added the find_last_of win and the two not_of losses that the record left out. Which stdlib was the baseline (libstdc++, libc++, or MSVC STL) is unknown, so baseline_stdlib stays [].
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/zuudevs/zuu_string_view>
- **Sources the enricher read:**
  - <https://github.com/zuudevs/zuu_string_view>
  - <https://github.com/zuudevs/zuu_string_view/blob/main/README.md>
  - <https://github.com/zuudevs/zuu_string_view/blob/main/include/zuu/string_view.hpp>
  - <https://github.com/zuudevs/zuu_string_view/blob/main/include/zuu/char_class.hpp>
  - <https://github.com/zuudevs/zuu_string_view/blob/main/vcpkg.json>
  - <https://github.com/zuudevs/zuu_string_view/blob/main/CMakePresets.json>
  - <https://github.com/zuudevs/zuu_string_view/blob/main/CMakeLists.txt>
  - <https://github.com/zuudevs/zuu_string_view/blob/main/benchmarks/api/string_view_find.cpp>
  - <https://github.com/zuudevs/zuu_string_view/blob/main/.github/workflows/ci.yml>
  - <https://github.com/zuudevs/zuu_string_view/issues>
  - <https://github.com/zuudevs/zuu_string_view/commits/main>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/zuudevs/zuu_string_view`) · [data/wave1/enrich/raw/github_com_zuudevs_zuu_string_view.json](../../../data/wave1/enrich/raw/github_com_zuudevs_zuu_string_view.json) (enrichment confidence 0.45)

</details>
