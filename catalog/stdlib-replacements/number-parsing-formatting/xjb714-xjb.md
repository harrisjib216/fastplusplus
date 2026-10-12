# xjb

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Schubfach-derived shortest double/float-to-string converter, about 2.4x faster than Ryu (the algorithm behind std::to_chars) on random doubles.

| | |
|---|---|
| **Beats** | Ryu (ulfjack/ryu, the double-to-shortest-string algorithm that std::to_chars uses in libstdc++, libc++ and MSVC STL; std::to_chars itself is not in the benchmark); also benchmarked against Dragonbox, Schubfach and fmt 12.1.0 |
| **Claimed result** | Result file for GCC 13.3.0 on AMD Ryzen 7 7840H, random doubles, cycles per conversion: xjb64 60.5, ryu 142.5, dragonbox_full 105.8, dragonbox_comp 116.2, fmt_full 132.2, schubfach 127.7, zmij 93.9, yy_double 89.9, i.e. about 2.4x faster than Ryu, 1.75x faster than Dragonbox, 2.2x faster than fmt (derived from page data). On Apple M1 with Apple clang 17.0.0 the same chart reads xjb64 31.4, ryu 98.7, fmt_full 98.3, dragonbox_comp 100.4, about 3.1x faster than Ryu (derived from page data). 'random length' dataset, GCC 13.3.0: xjb64 62.9 vs ryu 199.4. |
| **Workload** | Converting 16M random IEEE-754 doubles (random bit patterns over the whole binary range, NaN and Inf filtered) to shortest round-trip decimal strings; further datasets cover random digit counts, fixed digit counts, [0,1) doubles, integers, subnormals and floats. |
| **Metric** | throughput (CPU cycles per double-to-string conversion) |
| **Hardware** | AMD Ryzen 7 7840H w/ Radeon 780M Graphics, 5115 MHz reported, Linux x86-64 (also Apple M1, Apple clang 17.0.0) |
| **Compiler and flags** | GCC 13.3.0 (result file, last touched by commit 933930c on 2025-12-20). At that commit, bench/makefile builds with g++ -O3 -std=c++20 -march=native main.cpp util/yybench/src/yybench.cpp, without -DNDEBUG. The HEAD makefile uses -O3 -std=c++20 -march=native -DNDEBUG for g++, icpx -no-ftz and clang++. |
| **Adoption** | 46 stars; used by ssrJSON and jsoniter-scala per README |
| **Last commit** | 2026-08-10 |
| **Links** | [repository](https://github.com/xjb714/xjb) · [benchmark](https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/result/bench_double_AMD_Ryzen_7_7840H_w__Radeon_780M_Graphics_GCC_13_3_0.html) |

## Verdict

In the author's yybench run (GCC 13.3.0 -O3 -march=native, AMD Ryzen 7 7840H at about 5.1 GHz, Linux), converting full-range random doubles took 60.5 cycles each for xjb64 vs 142.5 for ulfjack's Ryu d2s, 105.8 for Dragonbox and 132.2 for fmt 12.1.0, about 2.4x faster than Ryu; on Apple M1 with Apple clang 17 it was 31.4 vs 98.7 (3.1x). std::to_chars itself was not timed: Ryu stands in for the algorithm that libstdc++, libc++ and MSVC STL use, and Ryu writes a different exponent format.

## Use it when

- JSON or CSV serializers that print many doubles (ssrJSON and jsoniter-scala use it): random full-range doubles measured 60.5 cycles vs 142.5 for Ryu and 105.8 for Dragonbox on a Zen 4 laptop with GCC 13.3.0.
- Workloads dominated by long values (scientific data, 15-17 significant digits) or arbitrary bit patterns, where xjb's cost stays at about 56-64 cycles while Ryu takes 127-192.
- x86-64 builds with SSE4.1 or AVX-512 IFMA, or AArch64/Apple Silicon with NEON; the README's April 2026 charts put xjb64 at about 43 cycles on the 7840H (icpx) and about 21 on M1 (derived from the SVG bar geometry).
- Code that can take the output format as-is, or that wants the JSON-specific variant.

## Skip it when

- You need std::to_chars or printf semantics: precision, fixed or scientific modes, std::chars_format, error codes, or identical text (std::to_chars prints 1000 as '1000' and 1.2e23 as '1.2e+23'; xjb prints '1000.0' and '1.2e23').
- Inputs are mostly short decimals or small integers: in the same GCC 13.3.0 run, dragonbox_full (45.8-67.9 cycles) and jnum beat xjb64 (about 75) for doubles in [0,1) with 1-11 significant digits, yyjson wins for 1-2 digit integers, and jnum wins for 9-17 digit integers, because xjb's cost is nearly constant regardless of digit count.
- Big-endian targets (on the roadmap, not supported) or toolchains without C++20-era features; no MSVC result is published although MSVC intrinsic paths exist.
- Projects needing settled licensing: the README says MIT while LICENSE and every source header say Apache-2.0 (open issue #25, 2026-10-06), and the README credits parts of the code to zmij.
- Risk-averse code bases: a single-maintainer project with 46 stars whose src/ftoa.cpp had a one-byte buffer overrun fixed in July 2026 (PR #22); pin a commit at or after that fix.

## How it is fast

It is a reworked Schubfach: one 64x128-bit multiplication by a cached power of ten yields the candidate digits, and the shortest-digit and rounding decision is a handful of comparisons written to avoid mispredicted branches (README algorithm listing), instead of Ryu's digit-removal loop. Digit generation writes all 16-17 digits at once with SIMD (SSE2/SSSE3/SSE4.1, an AVX-512 IFMA/VBMI path credited to Daniel Lemire, a NEON path by Dougall Johnson), then fixes the decimal-point position with a shuffle or memmove. Exponent-dependent layout data comes from about 15-18 KB of tables built at compile time (a 368-byte compressed-table variant exists in bench/), so the hot path has few data-dependent branches.

## Compared with alternatives

Pick xjb over Dragonbox, Ryu or {fmt} when bulk shortest-format output dominates and you control the text format: in the author's harness it is 1.75x faster than Dragonbox's full-table build and 2.2x faster than fmt 12.1.0 on random doubles. Pick Dragonbox, {fmt} or Boost.Charconv when you need std-compatible formatting, a mature multi-maintainer library or mostly short decimals; fast_float and fast_double_parser cover the parsing direction.

## Integration

| | |
|---|---|
| **Form** | source-drop (src/ftoa.cpp + src/ftoa.h; src/ftoa_json.cpp for JSON output) |
| **Dependencies** | none (standard C headers; optional compiler intrinsics for SSE2/SSSE3/SSE4.1/AVX-512 IFMA+VBMI or NEON, picked from -march flags) |
| **Minimum toolchain** | Not documented; the code uses C++20 features (designated initializers, [[unlikely]], constexpr-built tables) and the bench builds with -std=c++20 on GCC, Clang, Apple clang and icpx (icpx needs -no-ftz). |
| **Platforms** | x86-64 and AArch64 with SIMD paths, scalar fallback elsewhere; little-endian only |
| **Thread safety** | Not documented; the function is stateless and reads only constant tables (derived from source), so concurrent calls are safe. |
| **Drop-in for the baseline** | partial — same shortest round-trip digits as Ryu/Schubfach, but a C-style char\* API with its own output format ('1000.0', '1.2e23', '-nan', '-0.0') instead of std::to_chars's range, error code and standard formatting |

## Gotchas

- The output buffer must be at least 34 bytes for double and 21 for float even though the longest double string is 24 characters: the SIMD path stores whole 16-byte chunks. PR #22 raised the double requirement from 33 to 34 after a one-byte overrun for negative doubles with 16 integer digits, so callers sized to the old figure must update.
- Harness details behind the cited numbers: the HTML result comes from the yybench harness in bench/util/benchmark.cpp, which at commit 933930c (the last commit touching the GCC 13.3.0 file) timed 100,000 values per dataset in a single pass (meansure_count = 1), through a function pointer, without -DNDEBUG. It is not the 16M-double loop in bench/main.cpp, which only prints to stdout, and not best-of-several runs. Single-pass noise shows in individual points: Ryu's [0,1) fixed-length curve jumps from 156.7 to 236.7 to 160.8 cycles at 3, 4 and 5 digits.
- The benchmarked code is a separate copy (bench/xjb/float_to_string/ftoa.cpp at HEAD, bench/xjb/dtoa_xjb64_xjb32.cpp at 933930c), not src/ftoa.cpp, so fixes and tuning do not automatically flow between the shipped file and the measured one. In newer result files the xjb64_comp and yyjson rows are compile-time stubs that do no work.
- src/ftoa.cpp also exports f16, f80, f128 and f256 overloads (taking raw bit patterns as integers) that ftoa.h does not declare and the README roadmap still lists f80/f128 as unsupported; treat them as experimental. Double verification in the harness checks round-trip and shortest length, but float verification is marked 'To be completed' (the README says 'make check' in bench/ confirms output identical to Schubfach).

## Known shortcomings

- First-party: std::to_chars is never run (Ryu stands in with a different output format); the run (commit 933930c, 2025-12-20) used -O3 -std=c++20 -march=native without -DNDEBUG; README says MIT but LICENSE is Apache-2.0; PR #22 fixed a 1-byte buffer overrun in src/ (buffer requirement now 34 bytes), the bench copy was untouched. In newer result files xjb64_comp and yyjson compile to return-buf stubs, so their near-zero rows are meaningless.
- Enricher: the cited HTML is yybench with 100,000 values per dataset and a single timed pass (meansure_count = 1) at commit 933930c, not 16M doubles or best-of-N (single-pass noise: Ryu 156.7/236.7/160.8 cycles at 3/4/5 digits); xjb64 is not fastest everywhere (dragonbox_full and jnum win on short [0,1) decimals, yyjson and jnum on some integer lengths); the benchmarked file is a separate copy, not src/ftoa.cpp; licence issue #25 open. README v1.5.0 SVG: xjb64 about 43 vs zmij about 49 vs Ryu about 142 cycles on the 7840H. Leads: zmij, teju_jagua, fpfmt.

## Caveats and trade-offs

First-party benchmark run by the author; no peer review. The README's license line says MIT, but the LICENSE file, the GitHub sidebar and the src/ftoa.cpp header are Apache-2.0, so the license is recorded as Apache-2.0. The bench/ directory vendors third-party code (schubfach, ryu, dragonbox, fmt, yy, zmij, teju, uscale, jnum) under their own licenses; the library sources do not need it. std::to_chars is not benchmarked. Ryu (ulfjack d2s_buffered_n) stands in for it and prints its own exponent format (1.1E-6), so output formats differ across rows; the harness comment in bench/util/benchmark.cpp itself calls the comparison 'somewhat unfair' for this reason. Cycles are yybench tick counts scaled by cycles per tick, best of several runs, with each converter called through a function-pointer table, so only ratios are meaningful. In the newer result files (GCC 15.2.0 and Clang 21.1.6 on the 7840H, Apple clang 17 on M1), the xjb64_comp, yyjson and jnum rows sit at the null-function level in every dataset (about 8 cycles on x86, 3.0 on M1). bench/xjb/xjb_i.hpp and bench/yy/yy_i.hpp compile xjb64_comp and yyjson to a 'return buf' stub when USE_xjb_comp or use_yyjson is 0 (the yy header says it is set to 0 to cut compile time), so those rows did no work in those runs. jnum has no such stub, and its near-null value is unexplained. The cited xjb64 and ryu rows are unaffected, and the GCC 13.3.0 file (last updated 2025-12-20) has real values in every row. Results differ by compiler. With Clang 21.1.6 on the same CPU, xjb64 is 71.1 vs ryu 132.5 cycles (about 1.9x); with GCC 15.2.0 it is 55.7 vs 144.4 (about 2.6x) (derived from page data). The HTML result files predate later algorithm updates. The README's current charts (v1.5.0, 2026-04-13; icpx 2025.0.4 on the 7840H, Apple clang 21 on M1/M5) are SVGs only. PR #22 (2026-07-25, 'Fix buffer overflow') raised src/ftoa.cpp's documented output-buffer requirement from 33 to 34 bytes after a one-byte overrun for negative doubles with 16 integer digits in XJB_NO_MEMMOVE mode. Per the PR's file view, it also added a missing NEON store in to_ascii16 and debug-only bounds checks. Callers that sized buffers to the old 33-byte figure must update. The fix touched src/, not the bench copy that produced the cited numbers, and per the PR file view it does not change the release x86 conversion work, so the numbers are not treated as measured on code later fixed for a hot-path bug.

Single-file implementation with lookup tables (full: 15336 bytes double, 1352 bytes float; compressed: 368 and 64 bytes). Derived from Schubfach and produces identical digits to Schubfach (make check in bench). Uses SIMD (NEON, AVX512IFMA paths credited to dougallj and lemire). Output format is its own (for example 1000 prints as '1000.0', 0 as '0.0', NaN as 'nan'), with a separate JSON variant, so it is not a drop-in for std::to_chars. Big-endian is not supported yet; f80, f128 not supported.

## Maintenance

Active (last commit 2026-08-10, v1.5.0 charts from April 2026) but a single-maintainer project; Apache-2.0 per LICENSE and source headers despite the README's MIT line, so vendor src/ftoa.cpp and ftoa.h at a pinned commit after the PR #22 buffer fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The benchmark code is public (bench/main.cpp with the yybench harness in bench/util/benchmark.cpp). The result page names GCC 13.3.0 and the AMD Ryzen 7 7840H, and bench/makefile at commit 933930c (the last commit touching that result file, 2025-12-20) gives g++ -O3 -std=c++20 -march=native. The page times xjb64 against ulfjack's Ryu, the algorithm behind std::to_chars, so tier A holds.
- **Verifier notes:** Every cited number matches the GCC 13.3.0 and Apple M1 result pages (xjb64 60.47 vs ryu 142.53, dragonbox_full 105.79, fmt_full 132.20; random length 62.91 vs 199.36; M1 31.4 vs ryu 98.7), and the metadata checks out (Apache-2.0, 46 stars, last commit 2026-08-10, not archived). Two caveat fixes: the run predates -DNDEBUG in the makefile, and the near-null rows in newer files are compile-time stubs of other libraries, not optimized-away work. Shortcomings to record: std::to_chars not run directly (Ryu stands in, with a different output format); first-party; README says MIT while LICENSE is Apache-2.0; PR #22 raised the documented buffer requirement to 34 bytes after a one-byte overrun.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party public harness (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/result/bench_double_AMD_Ryzen_7_7840H_w__Radeon_780M_Graphics_GCC_13_3_0.html>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/result/bench_double_AMD_Ryzen_7_7840H_w__Radeon_780M_Graphics_GCC_15_2_0.html>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/result/bench_double_AMD_Ryzen_7_7840H_w__Radeon_780M_Graphics_Clang_21_1_6.html>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/result/bench_double_Apple_M1_Clang_17_0_0__Apple_version_.html>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/README.md>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/src/ftoa.cpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/makefile>
  - <https://raw.githubusercontent.com/xjb714/xjb/933930c/bench/makefile>
  - <https://raw.githubusercontent.com/xjb714/xjb/3b6b8ba/bench/makefile>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/main.cpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/util/benchmark.cpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/xjb/xjb_i.hpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/yy/yy_i.hpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/jnum/jnum_i.hpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/ryu/ryu_i.hpp>
  - <https://github.com/xjb714/xjb>
  - <https://github.com/xjb714/xjb/commits>
  - <https://github.com/xjb714/xjb/tree/main/bench/result>
  - <https://github.com/xjb714/xjb/commits/main/bench/result/bench_double_AMD_Ryzen_7_7840H_w__Radeon_780M_Graphics_GCC_13_3_0.html>
  - <https://github.com/xjb714/xjb/commits/main/bench/makefile>
  - <https://github.com/xjb714/xjb/pull/22>
  - <https://github.com/xjb714/xjb/pull/22/files>
- **Sources the enricher read:**
  - <https://github.com/xjb714/xjb>
  - <https://github.com/xjb714/xjb/issues?q=is%3Aissue>
  - <https://github.com/xjb714/xjb/issues/25>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/README.md>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/src/ftoa.cpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/src/ftoa.h>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/src/ftoa_json.cpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/makefile>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/main.cpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/util/benchmark.cpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/933930c/bench/util/benchmark.cpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/xjb/xjb_i.hpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/933930c/bench/xjb/xjb_i.hpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/ryu/ryu_i.hpp>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench/result/bench_double_AMD_Ryzen_7_7840H_w__Radeon_780M_Graphics_GCC_13_3_0.html>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench_result/random_double_7840h.svg>
  - <https://raw.githubusercontent.com/xjb714/xjb/HEAD/bench_result/random_double_m1.svg>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/xjb714/xjb`) · [data/wave1/enrich/raw/github_com_xjb714_xjb.json](../../../data/wave1/enrich/raw/github_com_xjb714_xjb.json) (enrichment confidence 0.8)

</details>
