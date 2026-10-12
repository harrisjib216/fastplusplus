# TLFloat

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Constexpr C++20 template library for IEEE half to octuple floats; inlined Quad beats libquadmath on add/mul/fma/sqrt/casts, loses on div/exp/log/pow.

| | |
|---|---|
| **Beats** | GNU libquadmath (GCC __float128) |
| **Claimed result** | TLFloat Quad vs GNU libquadmath, Mops/s: add 124.25 vs 87.72, mul 102.486 vs 78.2958, FMA 68.4656 vs 1.93365, sqrt 15.9095 vs 9.50421, cast to/from double 168.078 vs 63.7482, rint 191.323 vs 37.6146, compare 299.502 vs 222.788, sin 2.13261 vs 1.77002. Slower than libquadmath on div 50.7983 vs 72.6179, atan 1.30394 vs 3.02089, exp 1.49075 vs 1.78973, log 1.58123 vs 1.8479, pow 0.88467 vs 1.29873. |
| **Workload** | IEEE 754 binary128 (quadruple precision) operations in millions of operations per second: add, mul, div, fma, sqrt, casts to and from double, compare, rint, sin, atan, exp, log, pow. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X at 4.5 GHz |
| **Compiler and flags** | gcc 12.3.0 (Ubuntu 12.3.0-17ubuntu1); CMakeLists.txt defaults to the Release build type and adds -fno-math-errno, and the bench targets build TLFloat inlined (TLFLOAT_ENABLE_INLINING=1); the flags actually used for the published run (e.g. -march=native, which CMakeLists.txt mentions as an option) are not stated |
| **Adoption** | 38 stars, 7 forks, 223 commits; same GitHub owner (shibatch) as SLEEF |
| **Last commit** | 2026-08-17 |
| **Links** | [repository](https://github.com/shibatch/tlfloat) · [benchmark](https://github.com/shibatch/tlfloat) |

## Verdict

The project's own bench tool (src/util/bench.cpp, -DBUILD_BENCH=True) times 256-element loops of each operation for 10 s on an AMD Ryzen 9 7950X at 4.5 GHz with gcc 12.3.0: TLFloat 1.11.0 Quad (inlined) beat GNU libquadmath / GCC __float128 on add (124 vs 88 Mops/s), mul (102 vs 78), compare, casts to/from double (168 vs 64), sqrt (15.9 vs 9.5), rint (191 vs 38), fma (68.5 vs 1.9) and sin (2.13 vs 1.77), and lost on div, atan, exp, log and pow. First-party, single machine, flags beyond the CMake defaults not stated.

## Use it when

- You need IEEE binary128 arithmetic on clang or MSVC, where GCC's __float128/libquadmath is unavailable, and want bit-identical results across Linux, Windows, wasm and CUDA device code.
- Inner loops heavy on quad add/mul/compare/rint/casts or fma: the README run shows 1.3-1.4x on add/mul, about 5x on rint and about 35x on fma versus libquadmath on a Ryzen 9 7950X.
- Compile-time evaluation of high-precision constants or tables (all C++20 functions are constexpr), or freestanding/microcontroller targets with no malloc.
- You need octuple (binary256) precision with correctly rounded basic operations and 1-ulp elementary functions, where no hardware or compiler type exists.

## Skip it when

- Division- or transcendental-heavy quad code on GCC/x86-64: libquadmath was faster on div (72.6 vs 50.8 Mops/s), atan (3.02 vs 1.30), exp, log and pow in the same run.
- Arbitrary or run-time-selected precision: widths are fixed by template parameters (BigUInt sizes are powers of two), so it does not replace MPFR/GMP.
- Code that relies on non-default rounding modes or floating-point exception flags: neither is documented for TLFloat.
- Throughput-oriented SIMD work: the project's wiki says it prioritizes accuracy and portability over throughput, unlike its sibling SLEEF.
- Projects that cannot use C++20 for the header API (the C++11 API is non-constexpr and requires linking the built library).

## How it is fast

Each float is unpacked into sign, exponent and an integer mantissa held in a recursive BigUInt&lt;N&gt; template (two 2^(N-1)-bit halves), and arithmetic is done as fixed-width integer operations that use x86 intrinsics (_addcarry_u64, _umul128, inline-asm divq, __builtin_clzll) or __int128 when available, with Karatsuba only at 1024+ bits and Newton-style reciprocal approximations for division and sqrt. With TLFLOAT_ENABLE_INLINING every operation is marked always_inline, so the compiler can inline the whole soft-float path into the caller's loop instead of calling an out-of-line routine; the benchmark builds TLFloat this way (--inline-limit=1000000) while libquadmath functions remain shared-library calls.

## Compared with alternatives

Pick TLFloat over simd-f128 (whose README tables against __float128 disagree with each other) when you want a full IEEE binary128/binary256 math library with correctly rounded basic operations and portability to MSVC/CUDA; pick DoubleFloats.jl or MultiFloats.jl instead for faster \~106-bit double-double arithmetic in Julia when non-IEEE semantics are acceptable, and MPFR-based entries (LibBF, FLINT) when precision must exceed 237 bits or vary at run time.

## Integration

| | |
|---|---|
| **Form** | header-only (C++20 API) or static/shared lib (C and C++11 API, -ltlfloat) |
| **Dependencies** | none for the library; MPFR optionally for testers and table generation; libquadmath only for the comparison benchmark |
| **Minimum toolchain** | C++20 for tlmath.hpp/tlfloat.hpp (README example uses g++ -std=c++20); C++11 or C for tlfloat.h; CMake 3.16+ to build; CUDA 12+ for device use with --expt-relaxed-constexpr |
| **Platforms** | Linux, Windows (MSVC, clang-cl), microcontrollers, wasm and CUDA per README; x86-64 intrinsics and __int128 paths used where available, portable C++ otherwise; big-endian supported since v1.8.0; a ppc64el build failure (issue #4) was closed in Feb 2026 |
| **Thread safety** | README: 'All functions are thread-safe and reentrant' |
| **Drop-in for the baseline** | partial: with TLFLOAT_LIBQUADMATH_EMULATION and tlfloat.h most libquadmath functions (sinq, powq, strtoflt128, quadmath_snprintf) map onto TLFloat, but that path goes through the out-of-line C library; the benchmarked speed comes from the C++20 tlfloat::Quad type, a different interface |

## Gotchas

- The published speedups come from the header-only C++ Quad built with forced inlining; the C/libquadmath-emulation API calls into libtlfloat and was not benchmarked against libquadmath in the README (the C-API bench target is only built when the compiler lacks __float128).
- In bench.cpp the 'libquadmath' add, mul, div, compare and cast rows apply plain operators to GCC __float128, so they time GCC's compiler-provided soft-float routines rather than libquadmath functions; only fma, sqrt, rint, sin, atan, exp, log and pow call libquadmath.
- The README numbers are from TLFloat 1.11.0, while the current CMakeLists.txt declares 1.17.1, and the optimization flags of the published run (e.g. -march=native) are not stated.
- Building the library or tests sets very high constexpr step limits (-fconstexpr-ops-limit=1000000000 on GCC, /constexpr:steps1000000000 on MSVC); heavy constexpr use in your own code may need the same flags.

## Known shortcomings

- Loses to libquadmath on div/atan/exp/log/pow; run flags not stated; baseline libquadmath is not a category incumbent.
- bench.cpp's 'libquadmath' add/mul/div/cmp/cast rows use GCC __float128 operators, not libquadmath calls (baseline mislabel); README numbers from v1.11.0 while the source is 1.17.1.

## Caveats and trade-offs

Mixed result, not a blanket win: slower than libquadmath on division, atan, exp, log and pow. Baseline is libquadmath, not GMP/MPFR (MPFR was not benchmarked). Numbers are first-party from TLFloat 1.11.0 (the README table predates later releases; latest release v1.15.0, 2025-03-26); the exact optimization flags of the run are not stated. TLFloat is benchmarked as an inlined header build while libquadmath is a shared-library call. last_commit 2026-08-17 ('Add bug workaround for gcc') confirmed on the main commits page.

C++ template library (half, single, double, quad, octuple precision) with constexpr support and its own arbitrary-width integer classes. Fixed-width binary128/binary256 floats, not arbitrary precision, and no GMP or MPFR comparison.

## Maintenance

Actively maintained (last commit 2026-08-17, 223 commits, no open issues) by the author of SLEEF under BSL-1.0, with a README request that companies earning over US\$1M from it fund maintenance; small but niche (38 stars), with releases on GitHub up to v1.15.0 and a source tree now at 1.17.1.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README.adoc 'Benchmark results' gives first-party Mops/s for TLFloat Quad and GNU libquadmath from the public bench tool (src/util/bench.cpp, -DBUILD_BENCH=True) with CPU (Ryzen 9 7950X at 4.5 GHz) and compiler (gcc 12.3.0) stated, but the optimization flags used for the run (e.g. whether -march=native was set) are not stated, so not A; not peer reviewed, so C.
- **Verifier notes:** Every number in claimed_speedup matches README.adoc, including the losses; README is README.adoc (README.md does not exist). Metadata confirmed: BSL-1.0 (LICENSE.txt), 38 stars, last commit 2026-08-17.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/README.adoc>
  - <https://github.com/shibatch/tlfloat>
  - <https://github.com/shibatch/tlfloat/commits/main>
  - <https://github.com/shibatch/tlfloat/releases>
  - <https://github.com/shibatch/tlfloat/tree/main/src>
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/LICENSE.txt>
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/src/util/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/README.adoc>
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/src/util/CMakeLists.txt>
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/src/util/bench.cpp>
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/src/include/tlfloat/bigint.hpp>
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/src/include/tlfloat/tlfloat.hpp>
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/src/include/tlfloat/tlmath.hpp>
  - <https://raw.githubusercontent.com/shibatch/tlfloat/main/src/include/tlfloat/tlfloat.h>
  - <https://github.com/shibatch/tlfloat>
  - <https://github.com/shibatch/tlfloat/tree/main/src/include/tlfloat>
  - <https://github.com/shibatch/tlfloat/issues>
  - <https://github.com/shibatch/tlfloat/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/shibatch/tlfloat/releases>
  - <https://github.com/shibatch/tlfloat/wiki>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/shibatch/tlfloat`) · [data/wave8/enrich/raw/github_com_shibatch_tlfloat.json](../../../data/wave8/enrich/raw/github_com_shibatch_tlfloat.json) (enrichment confidence 0.8)

</details>
