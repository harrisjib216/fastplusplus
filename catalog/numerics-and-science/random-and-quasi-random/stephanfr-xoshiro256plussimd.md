# Xoshiro256PlusSIMD

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++17 xoshiro256+ with an AVX2 four-stream next4() that roughly doubles throughput over the scalar reference.

| | |
|---|---|
| **Beats** | scalar xoshiro256+ (Blackman/Vigna reference) |
| **Claimed result** | Reference C xoshiro256+ 1.09 ms per 1M values vs AVX2 next4() 526 us (about 2.07x, derived from page data); serial next4() 1.93 ms vs AVX2 next4() 526 us (about 3.7x, derived from page data) |
| **Workload** | Generating 64-bit values four-wide with AVX2 vs serial |
| **Metric** | throughput |
| **Hardware** | Ryzen 7 1700 in a 2-core Ubuntu 20.04 VM |
| **Adoption** | 14 stars |
| **Last commit** | 2021-08-21 |
| **Links** | [repository](https://github.com/stephanfr/Xoshiro256PlusSIMD) · [benchmark](https://github.com/stephanfr/Xoshiro256PlusSIMD) |

## Verdict

Catch2 benchmarks in the author's README, run in a 2-core Ubuntu 20.04 VM on a Ryzen 7 1700 (compiler and flags not stated): generating 1M uint64 values took 1.09 ms with the Blackman/Vigna C reference, 1.08 ms with the class's serial next(), and 526 us with AVX2 next4() discarding results. That is about 2.07x over the reference (derived from page data), falling to about 1.27x when the four lanes are summed into a uint64_t (860 us).

## Use it when

- Monte Carlo or simulation kernels already written with AVX2 that can use a __m256i or __m256d of four randoms directly
- Filling large buffers of uint64 or double randoms on x86-64 with AVX2, where 4-wide generation measured about 2x the scalar reference (526 us vs 1.09 ms per 1M values)
- When you want xoshiro256+ quality for floating-point output (Vigna's recommended use) with jump-separated streams per instance

## Skip it when

- Single-value draws: the author says AVX2 brings no gain there, and extracting the four lanes one at a time loses the speedup
- Non-x86 targets: the header includes &lt;immintrin.h&gt; and uses __m256i types unconditionally, even in the serial build
- MSVC: issue #1 (Jan 2023, open) reports build errors with Visual Studio 2022
- Integer outputs where low-bit quality matters: xoshiro256+ has weak lowest 3 bits, and the bounded functions use the low 32 bits of the output
- Bounded integers wider than 32 bits: bounds are uint32_t only

## How it is fast

next4() runs four independent xoshiro256+ states in the four 64-bit lanes of AVX2 registers, coded with explicit intrinsics rather than relying on auto-vectorization. The four lane states are seeded 2^192 apart with xoshiro long_jump. Bounded integers use a 32x32 multiply-shift reduction (Lemire-style), not a modulus, and doubles are built by OR-ing the top 52 bits into the 1.0 exponent and subtracting 1.0.

## Compared with alternatives

Pick it over SIMDxorshift or simdpcg when you want a C++17 header with xoshiro256+ quality, bounded-int and double helpers, and serial and SIMD outputs that match. The 8-way xoshiro256++ gist or SHISHUA give more bulk throughput, and Sirius64 or wyrand are better for scalar one-at-a-time draws.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Catch2 only for the unit tests and benchmarks) |
| **Minimum toolchain** | C++17 (if constexpr); GCC on Linux is the only documented toolchain. Compile with -mavx2 and define __AVX2_AVAILABLE__ for the AVX2 variant. |
| **Platforms** | x86-64 only; AVX2 required for the fast path |
| **Thread safety** | Not documented; instances hold mutable state, so use one per thread (the jump-on-copy constructor gives each copy a separate stream) |
| **Drop-in for the baseline** | partial: same xoshiro256+ algorithm and output as the Blackman/Vigna reference for next(), but a C++ class API, not the C next()/jump() functions, and not a std UniformRandomBitGenerator |

## Gotchas

- The AVX2 template instance cannot be created unless the __AVX2_AVAILABLE__ macro is defined before the include (static_assert).
- dnext() and dnext4() type-pun through a union, which is undefined behavior in ISO C++; it works on GCC and Clang.
- Serial next4() is 1.8x slower than four serial next() calls (1.93 ms vs 1.08 ms per 1M values); use next4() only with the AVX2 instance.
- Without -mavx2, serial dnext4() became much slower (6.39 ms vs 2.26 ms per 1M values) in the author's no-AVX benchmark.

## Known shortcomings

- Compiler and flags not stated; measured in a 2-core VM; gain disappears if the four values are consumed one by one; abandoned (last commit 2021-08-21).
- x86-only (includes immintrin.h even in scalar build); issue #1 (Jan 2023): does not build on MSVC 2022; double conversion type-puns through a union (UB in C++); bounded output uses weak low bits; 2.07x drops to \~1.27x when lanes are summed.

## Caveats and trade-offs

Rounded numbers; compiler and flags unstated; measured in a 2-core VM. The author says the gain disappears if the four-wide values are extracted and used one by one. Compared only against the scalar reference, not std::mt19937. Last commit 2021-08-21 (over 3 years ago).

Header-only; AVX2 gain only when four values are consumed together; four streams separated by 2^192 long jumps.

## Maintenance

Abandoned since 2021-08-21, with an unanswered MSVC build issue. It is MIT-licensed (built on CC0 xoshiro code) and about 580 lines, so it is easy to vendor on GCC and Clang x86-64.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README shows Catch2 benchmark output (UnitTest/Benchmark.cpp) for 1M values. The Blackman/Vigna C reference took 1.09 ms and AVX next4() with no sum took 526 us. The hardware is a Ryzen 7 1700 VM, but the compiler and flags are not stated, so the tier is C.
- **Verifier notes:** The last commit was on 2021-08-21, more than 5 years ago, so maintenance_status was corrected to abandoned. It has 14 stars and an MIT license, both confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/stephanfr/Xoshiro256PlusSIMD>
  - <https://raw.githubusercontent.com/stephanfr/Xoshiro256PlusSIMD/HEAD/README.md>
  - <https://raw.githubusercontent.com/stephanfr/Xoshiro256PlusSIMD/main/LICENSE>
  - <https://raw.githubusercontent.com/stephanfr/Xoshiro256PlusSIMD/main/CMakeLists.txt>
  - <https://github.com/stephanfr/Xoshiro256PlusSIMD/commits>
- **Sources the enricher read:**
  - <https://github.com/stephanfr/Xoshiro256PlusSIMD>
  - <https://raw.githubusercontent.com/stephanfr/Xoshiro256PlusSIMD/HEAD/README.md>
  - <https://raw.githubusercontent.com/stephanfr/Xoshiro256PlusSIMD/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/stephanfr/Xoshiro256PlusSIMD/HEAD/include/Xoshiro256Plus.h>
  - <https://github.com/stephanfr/Xoshiro256PlusSIMD/issues>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/stephanfr/xoshiro256plussimd`) · [data/wave8/enrich/raw/github_com_stephanfr_xoshiro256plussimd.json](../../../data/wave8/enrich/raw/github_com_stephanfr_xoshiro256plussimd.json) (enrichment confidence 0.8)

</details>
