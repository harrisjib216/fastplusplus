# yy_itoa (itoa_yy.c in ibireme/c_numconv_benchmark)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> yy_itoa: a 200-byte-table ANSI C integer-to-decimal routine (yyjson's) that formats u32/u64/i32/i64 about 1.7-2.5x faster than fmt's compiled format_to.

| | |
|---|---|
| **Beats** | fmt::format_to(buf, FMT_COMPILE("{}"), val) from fmtlib (the baseline the repo's own itoa report uses); the repo does not time std::to_chars, fmt::format_int or sprintf |
| **Claimed result** | Random-length itoa, average CPU cycles per call, GCC 13.2.0 on Intel i5-13600KF: yy 20.69 vs fmtlib 40.37 for u32 (1.95x, derived from page data), 33.55 vs 56.88 for u64 (1.70x, derived from page data), 21.33 vs 53.62 for i32 (2.51x, derived from page data), 33.47 vs 65.65 for i64 (1.96x, derived from page data). Same direction on Clang 18.1.3 (u64 34.10 vs 53.93), MSVC 1940 (u64 42.50 vs 71.73) and Apple M1 Pro with Apple Clang 15.0.0 (u64 26.88 vs 43.44); the null no-op group is about 4 cycles (5.66 in the GCC u32 chart, 3.0 on the M1). |
| **Workload** | Integer to decimal string for u32, u64, i32 and i64 into a caller buffer: 10000 samples per measurement, minimum of 32 repeats, reported as average CPU cycles per call; 'random length' mixes digit counts uniformly (1-10 digits for 32-bit, 1-20 for u64, 1-19 for i64), plus fixed-length sweeps over every digit count; a no-op 'null' group measures loop overhead. |
| **Metric** | throughput |
| **Hardware** | 13th Gen Intel Core i5-13600KF, 5090 MHz reported, Linux 64-bit (GCC and Clang) and Windows 64-bit (MSVC); Apple M1 Pro 3228 MHz, macOS 14.4.1 |
| **Compiler and flags** | GCC 13.2.0 (other reports: Clang 18.1.3, MSVC 1940, Apple Clang 15.0.0); CMake Release build (CMAKE_BUILD_TYPE defaults to Release in CMakeLists.txt, so CMake's default -O3 -DNDEBUG for GCC and Clang and /O2 for MSVC; C11 and C++17), GCC gets -falign-functions=64 and Clang -mllvm -align-all-functions=7; the ARCH_NATIVE option (-march=native) defaults to OFF and the report does not say whether it was used |
| **Adoption** | 75 stars on c_numconv_benchmark; the README says the yy functions are used in the yyjson library |
| **Last commit** | 2025-12-05 |
| **Links** | [repository](https://github.com/ibireme/c_numconv_benchmark) · [benchmark](https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/docs/reports/gcc_intel_i5_13600/itoa.html) |

## Verdict

The author's own harness (10000 samples, best of 32 runs, average CPU cycles per call through a function pointer) on a Core i5-13600KF with GCC 13.2 Release builds measured random-length conversion at 20.69 vs 40.37 cycles (u32), 33.55 vs 56.88 (u64), 21.33 vs 53.62 (i32) and 33.47 vs 65.65 (i64) against fmt::format_to with FMT_COMPILE("{}") from a vendored fmt commit; Clang 18.1, MSVC 1940 and Apple M1 runs show the same direction. std::to_chars is not in the repo; a rival project's third-party run on a Xeon 8481C (compiler unstated) put itoa_i64_yy at 2.18x std::to_chars and 1.64x fmt::format_int by geometric mean.

## Use it when

- Serializers (JSON, CSV, logs, metrics) that emit many integers into a buffer they already size, where an 8-20 byte write without bounds checks is acceptable.
- Mixed-magnitude or full-range 32-bit and 64-bit values: on the GCC 13.2 / i5-13600KF random-length chart it took 20.7 cycles (u32) and 33.5 cycles (u64) per call against fmt's 40.4 and 56.9.
- Signed integers in particular: i32 random length 21.3 vs 53.6 cycles for fmt, second only to the 50 KB-table yy_largelut variant in that chart.
- C codebases or freestanding builds that cannot pull in {fmt} or C++17 &lt;charconv&gt;; the code is plain ANSI C with stdint.h, stddef.h and string.h only.
- Code that must stay small in cache: one 200-byte table, no SIMD and no 128-bit integers.

## Skip it when

- When you need the fastest possible routine on these charts: yy_largelut (50 KB tables), an and jeaiii beat yy in several random-length columns (GCC u64: yy_largelut 22.0, an 29.4, jeaiii 33.3, yy 33.5 cycles; GCC u32: an 20.6 vs yy 20.7).
- Mostly 1-4 digit values: in a third-party run (simditoa/benchmarks) fmt::format_int beat itoa_i64_yy on 1-digit (983.9M vs 522.4M ints/s) and 4-digit (454.1M vs 399.0M ints/s) numbers.
- When you need bounds checking, an error code, other bases, padding or locale handling; it is decimal only and trusts the buffer size.
- When you want a maintained, packaged API: it lives as a benchmark contestant file with no header, versioning or tests beyond the harness's spot checks.
- 32-bit targets: the u64 path divides 64-bit values by 1e8, and no 32-bit run is published.

## How it is fast

It branches once on value magnitude (1-2, 3-4, 5-6, 7-8, 9-10 digits for 32-bit; 1-8, 9-16, 17-20 for 64-bit, splitting into 8-digit chunks) so the digit count is known before writing, then emits two digits at a time from a 200-byte 00-99 lookup table with 2-byte memcpy stores. Division by 100 and 10000 is replaced by hand-picked reciprocal multiply-and-shift constants (val\*5243&gt;&gt;19, val\*429497&gt;&gt;32, val\*109951163&gt;&gt;40, val\*3518437209&gt;&gt;45), which let several digit pairs be computed in parallel instead of in a serial divide-by-10 chain. An odd leading digit is handled branchlessly by copying from table offset +1 and moving the output pointer back one byte.

## Compared with alternatives

Pick yy over jeaiii/itoa when you need plain C rather than C++ templates (the two are within 1 percent on GCC u64 random length), and over {fmt} or Boost.Charconv when you want a dependency-free 100-line function; pick simditoa if you can use SIMD and want the largest margin over std::to_chars, and fmt::format_int if your integers are mostly 1-4 digits.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (stdint.h, stddef.h, string.h) |
| **Minimum toolchain** | ANSI C / C99 (repo builds as C11 and C++17 with CMake 3.14+); force_inline and table_align macros cover GCC, Clang and MSVC |
| **Platforms** | any; published runs on x86-64 Linux (GCC 13.2, Clang 18.1), x86-64 Windows (MSVC 1940) and Apple M1 (Apple Clang 15) |
| **Thread safety** | reentrant pure functions (read-only static table, no global state), from reading the source; not documented |
| **Drop-in for the baseline** | partial — same job as fmt::format_to(buf, FMT_COMPILE("{}"), v) or std::to_chars(first, last, v) with a pointer-returning signature, but no last pointer, no error code and no NUL terminator; callers must reserve 10 (u32), 11 (i32) or 20 (u64, i64) bytes |

## Gotchas

- Output is not NUL-terminated, and the function writes scratch bytes outside the returned string: a 1-digit result still stores two bytes (the byte after the returned end is clobbered), and the signed variants always store '-' at buf[0] before writing digits. Never pass a buffer that ends exactly at the digits.
- Harness flaw (does not affect the headline random-length numbers): fill_rand_i32_len and fill_rand_i64_len in src/itoa/benchmark.c fill the negative half of each fixed-length signed sweep with min + i\*step for i from count/2 to count, which runs past max, so those samples have one more digit than the chart's x-axis label; at the top length (10-digit i32, 19-digit i64) the out-of-range double-to-integer cast is undefined behaviour and on x86-64 collapses about half the samples to the single value INT32_MIN or INT64_MIN. The fixed-length i32 and i64 charts therefore mix two digit counts per point.
- The harness checks each contestant against sprintf only on boundary values and powers of 2-10, not on random samples; the reciprocal constants themselves hold over their documented ranges (each satisfies m\*d - 2^k below 2^(k - input bits), checked by hand this session).
- Cycle counts are tick counts scaled by a frequency measured at startup and include call-through-pointer loop overhead (null group 5.66 cycles on GCC u32, about 4.0 elsewhere); subtracting it widens the gap (GCC random length, derived from page data: u32 2.31x, u64 1.79x, i32 2.86x, i64 2.09x). The run apparently had turbo on (5090 MHz) although the README says to disable it.

## Known shortcomings

- First-party report; the baseline is fmt's FMT_COMPILE format_to, not std::to_chars or sprintf, and yy_itoa is beaten by yy_largelut, an and jeaiii in some columns; turbo apparently on. Third-party corroboration (simditoa/benchmarks mean rows): yy 136.1M vs std::to_chars 62.4M and fmt::format_int 83.2M ints/s, but yy loses to format_int on 1-4 digit values, and that repo's summary table contradicts its raw rows.
- Enricher: harness flaw in src/itoa/benchmark.c: fill_rand_i32_len and fill_rand_i64_len push the negative half past the type's maximum, so those samples carry one extra digit, and at 10-digit i32 and 19-digit i64 the out-of-range double-to-int cast is undefined behaviour that collapses about half the samples to INT32_MIN or INT64_MIN; this affects only the fixed-length signed charts, not the random-length headline. The 1-digit result writes 2 bytes, signed variants always write '-' at buf[0], and the verify step covers only boundary values and powers. Net-of-null ratios on GCC (derived from page data): u32 2.31x, u64 1.79x, i32 2.86x, i64 2.09x.

## Caveats and trade-offs

(1) The repo times fmt's compile-time format_to path (src/itoa/itoa_fmtlib.cpp; vendor/fmt submodule pinned at commit 0379bf3, version not checked), not std::to_chars, fmt::format_int or sprintf; sprintf is registered only as the correctness oracle. (2) The benchmark and the yy function have the same author, but the code, compiler versions and CPU model are public. (3) Cycle counts include loop overhead (null group about 4 cycles, 5.66 in the GCC u32 chart); the reported CPU frequency (5090 MHz) suggests turbo boost was on although the README advises turning it off. (4) The interactive reports are served from github.io, which is not reachable here, so the numbers were read from the report HTML committed under docs/reports. (5) yy is not the fastest in the report: yy_largelut, an and jeaiii beat it in several columns (u64 random on GCC: yy_largelut 22.02, an 29.40, jeaiii 33.32, yy 33.55 cycles). (6) Independent corroboration against the listed baselines, from the raw google/benchmark rows of https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/RESULTS.md (repo https://github.com/simditoa/benchmarks, 0 stars, written by a rival integer-formatting project; benchmarks/yy_itoa.cpp calls itoa_i64_yy and benchmarks/fmtlib_fmt.cpp calls fmt::format_int; Intel Xeon Platinum 8481C c3-standard-8 VM, CMake Release with -mavx512\* flags, compiler version and C++ standard library not printed): geometric mean of the _mean ints/s rows over {UNIFORM_POS, LOG_HEAVY, FIXED 12, 16, 19} is 136.1M for itoa_i64_yy, 62.4M for std::to_chars (2.18x, derived from page data) and 83.2M for fmt::format_int (1.64x, derived from page data); the _max rows give 136.3M, 62.5M and 83.4M. yy beats std::to_chars in every measured shape (1.25x at 4 digits up to 2.97x on uniform signed 64-bit values) but loses to fmt::format_int on short numbers (1 digit: 522.4M vs 983.9M ints/s; 4 digits: 399.0M vs 454.1M, mean rows). That file's LLM-written summary scoreboard lists yy_itoa at 103M against std_to_chars 105M and puts the FIXED:1 values in its UNIFORM_POS column, which contradicts its own raw rows, so only the raw rows were used. Because of the unstated compiler that corroboration is tier C by itself. [retier] Enricher: fill_rand_i32_len and fill_rand_i64_len put the negative half one digit past the maximum, and at 10-digit i32 and 19-digit i64 an out-of-range double-to-int cast (undefined behaviour) collapses about half the samples to INT32_MIN or INT64_MIN, so the fixed-length signed charts are unreliable; the verify step covers only boundary values and powers. Net-of-null GCC ratios: u32 2.31x, u64 1.79x, i32 2.86x, i64 2.09x (derived from page data).

Portable ANSI C with one 200-byte two-digit lookup table and branches on value magnitude; no SIMD and no 128-bit integers. Output is not NUL-terminated and the caller buffer must hold 10 (u32), 11 (i32) or 20 (u64, i64) bytes; the function returns a pointer to the end. The same report also lists a yy_largelut variant that is faster still (u64 random 22.02 cycles on GCC), which per its source header uses 50 KB of lookup tables (the author notes large LUTs are unacceptable in many cases) and is a separate function from the 200-byte-table yy.

## Maintenance

Active benchmark repo (last commit 2025-12-05, MIT, 75 stars) whose yy routine is used inside yyjson; small enough to vendor, but it is a benchmark file rather than a packaged library, so you own the copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/reports/gcc_intel_i5_13600/itoa.html carries the yy and fmtlib rows exactly as claimed (random length average cycles: u32 20.69 vs 40.37, u64 33.55 vs 56.88, i32 21.33 vs 53.62, i64 33.47 vs 65.65) with compiler GCC 13.2.0 and CPU i5-13600KF stated; the benchmark code (src/itoa/itoa_fmtlib.cpp calling fmt::format_to(buf, FMT_COMPILE("{}"), val), the yy implementation and run_itoa) and the build flags (CMakeLists.txt defaults to Release, adds -falign-functions=64 for GCC) are public, so it is reproducible.
- **Verifier notes:** Record checks out against all four committed reports, the fmtlib wrapper source, the vendor/fmt pin and the repo metadata (MIT, 75 stars, not a fork, last commit 2025-12-05, active). Small fixes: the simditoa corroboration figures were taken from the _max aggregate rows (mean rows differ by under 0.3 percent, ratios unchanged), and the null group is up to 5.66 cycles. Shortcomings to record: baseline is fmt's FMT_COMPILE format_to rather than std::to_chars (std::to_chars only in a rival's third-party run with unstated toolchain), first-party benchmark, turbo apparently on, yy beaten by yy_largelut, an and jeaiii in several columns and by fmt::format_int on 1-4 digit numbers.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-75 (wave 1 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/docs/reports/gcc_intel_i5_13600/itoa.html>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/docs/reports/clang_intel_i5_13600/itoa.html>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/docs/reports/msvc_intel_i5_13600/itoa.html>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/docs/reports/clang_apple_m1/itoa.html>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/src/itoa/itoa_fmtlib.cpp>
  - <https://github.com/ibireme/c_numconv_benchmark>
  - <https://github.com/ibireme/c_numconv_benchmark/commits>
  - <https://github.com/ibireme/c_numconv_benchmark/tree/master/vendor>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/RESULTS.md>
  - <https://github.com/simditoa/benchmarks>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/fmtlib_fmt.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/benchmarks/yy_itoa.cpp>
  - <https://raw.githubusercontent.com/simditoa/benchmarks/HEAD/common/bench_data.hpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/src/itoa/itoa_yy.c>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/src/itoa/itoa_fmtlib.cpp>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/src/itoa/benchmark.c>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ibireme/c_numconv_benchmark/HEAD/docs/reports/gcc_intel_i5_13600/itoa.html>
  - <https://github.com/ibireme/c_numconv_benchmark/tree/master/src/itoa>
  - <https://github.com/ibireme/c_numconv_benchmark/issues>
  - <https://github.com/fmtlib/fmt/commit/0379bf3>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ibireme/c_numconv_benchmark`) · [data/wave1/enrich/raw/github_com_ibireme_c_numconv_benchmark.json](../../../data/wave1/enrich/raw/github_com_ibireme_c_numconv_benchmark.json) (enrichment confidence 0.8)

</details>
