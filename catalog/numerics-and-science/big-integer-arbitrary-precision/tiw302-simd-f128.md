# simd-f128

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Header-only C11/C++11 double-double (about 106-bit, 31-digit) type, claimed 1.5-3.4x lower latency than GCC __float128.

| | |
|---|---|
| **Beats** | GCC __float128 (libquadmath) |
| **Claimed result** | The README has two inconsistent tables for the same 10M-iteration latency test against __float128 (GCC). The summary table gives __float128 add 152.31 ms, mul 189.81 ms, div 276.00 ms, and simd-f128 73.60, 56.15 and 159.70 ms; it claims '3.38x faster than GCC' on multiply and '1.7x to 3.3x faster' overall. The 'Comparative Speed' section with raw bench_compare console output gives __float128 153.37 / 193.23 / 325.37 ms and simd-f128 (AVX2) 99.44 / 74.46 / 207.98 ms, which it states as 'multiplication is 2.59x faster, addition is 1.54x faster, and division is 1.56x faster'. |
| **Workload** | 10,000,000 iterations in latency mode of add, mul and div on a 128-bit double-double (about 31 digits) type with AVX2/NEON/WASM-SIMD backends versus GCC __float128. |
| **Metric** | latency |
| **Compiler and flags** | Not stated for the published runs. CMakeLists.txt sets -Wall -Wextra -O3 for GCC/Clang, plus -mavx2 -mfma when SIMD_F128_AVX2 is on (inferred from the build files, not from the benchmark write-up). |
| **Adoption** | 2 stars; published on PyPI (simd-f128 1.6.2), npm and crates.io |
| **Last commit** | 2026-08-17 |
| **Links** | [repository](https://github.com/tiw302/simd-f128) · [benchmark](https://github.com/tiw302/simd-f128) |

## Verdict

First-party only. The project's bench_compare.c runs loop-carried add, mul and div 10M times each against GCC __float128 on an unnamed 12-thread, 3.27 GHz machine with no compiler version stated. The current console output reads __float128 153.37/193.23/325.37 ms vs simd-f128 (AVX2) 99.44/74.46/207.98 ms (1.54x, 2.59x, 1.56x). A second README table from a different run claims up to 3.38x on multiplication.

## Use it when

- Deep-zoom fractal rendering (the author's mandelbrot-c reaches 1e-28 coordinates) and other inner loops that need about 31 digits without heap allocation.
- Long-horizon integrators (RK4, n-body, orbital mechanics) where double rounding error accumulates and the range of double (about 1e308) is enough.
- Projects that must build on MSVC, ARM, RISC-V or WebAssembly where __float128 is unavailable or emulated slowly.
- Batch element-wise work on x86 with AVX2 and FMA, using simd_f128x4 or the SoA array helpers.
- Eigen or std::complex code that needs a higher-precision scalar through the provided traits.

## Skip it when

- You need IEEE binary128 semantics: correct rounding, the 15-bit exponent range, or bit-exact results matching other quad implementations. Use __float128 or TLFloat.
- Your code subtracts nearly equal values: the README warns of catastrophic cancellation, and the sloppy add has no small relative-error bound in that case.
- sin and cos of large arguments: math_theory.md says range reduction is simplified and Payne-Hanek reduction must be applied externally for |x| much larger than 2\*pi.
- You need more than about 31 digits or arbitrary precision: use MPFR, or a triple/quad-double library such as MultiFloats.jl or QD.
- Mature production use: first commit 2026-08, one author, 2 stars, a small test suite (two ctest targets in the README run) and no external users besides the author's own projects.

## How it is fast

Values are unevaluated sums of two hardware doubles, so each operation is a dozen or so native double operations instead of software-emulated 113-bit binary128. Addition is Knuth TwoSum on the high parts plus plain addition of the low parts (QD's 'sloppy' add); multiplication uses hardware FMA for the exact product error when FP_FAST_FMA is defined, otherwise the Dekker/Veltkamp split; division and sqrt take one hardware estimate plus one Newton-Raphson-style correction. The scalar API keeps the pair in a SIMD register but computes lane by lane, so the speedup over __float128 comes from hardware double arithmetic and FMA, not lane parallelism; only simd_f128x4 (AVX2) processes four values at once.

## Compared with alternatives

Pick it over TLFloat when you are in C or C++, can accept double-double semantics, and want the cheapest roughly 31-digit type on MSVC, ARM or WebAssembly; pick TLFloat when you need IEEE binary128. Pick it over MultiFloats.jl and DoubleFloats.jl only because those are Julia-only; they offer triple and quad-double, normalized algorithms and a longer track record.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (libm on Linux/UNIX for fma); optional Google Benchmark for benchmarks; pybind11, Emscripten or cc/bindgen for the bindings |
| **Minimum toolchain** | C11 (C99 for the scalar path) or C++11; README lists GCC 4.9+, Clang 3.5+, MSVC 2019+, Emscripten 3.0+, with CI on GCC 11+, Clang 14+ and MSVC 2022 |
| **Platforms** | x86-64 (scalar, SSE2, AVX2), AArch64 NEON, ARMv7 (scalar, VFPv4 for FMA), RISC-V64 scalar, WebAssembly SIMD128 and scalar; backend chosen at compile time from compiler macros |
| **Thread safety** | not documented; values are plain registers or structs and the arithmetic has no shared state, apart from the PRNG header, which is stateful |
| **Drop-in for the baseline** | partial: f128::float128 offers operators and common math functions like __float128, but it is a different type with double's exponent range, no correct rounding and different results, and C code must call simd_f128_add-style functions |

## Gotchas

- Every function body is static inline but sits behind #ifdef SIMD_F128_IMPLEMENTATION. Contrary to the README's 'exactly one translation unit' instruction, any translation unit that calls the arithmetic must define the macro, or it sees only declarations (inferred from simd_f128.h).
- Speed depends on build flags: the default CMake build is the scalar backend, and exact products use FMA only when FP_FAST_FMA (or __FMA__ for the x4 path) is defined. Build with -mavx2 -mfma (SIMD_F128_AVX2=ON) or an AArch64 target, or multiplication falls back to the slower Dekker split.
- std::numeric_limits&lt;f128::float128&gt;::is_iec559 is set to true although the type is double-double and not IEEE binary128. Generic code that trusts this trait will assume IEEE behaviour.
- The README's Google Benchmark table mixes metrics: Add and Mul (11.7 and 10.1 ns) are loop-carried latency, while Div and Sqrt (2.87 and 6.05 ns) time independent operations (bench_math.cpp). In the Mul loop the value roughly doubles every iteration and soon overflows to infinity, hitting the early-return path.

## Known shortcomings

- README has two inconsistent tables (mul 3.38x vs 2.59x; div 1.73x vs 1.56x) and the '1.7x-3.3x' headline uses the more favourable run; baseline is __float128 only (no GMP/MPFR numbers); double-double is not IEEE binary128; the Google Benchmark mul loop overflows to inf; no CPU or compiler version (flags inferred from CMakeLists); extended-precision float rather than big integers, an edge case for this category.
- numeric_limits is_iec559=true on a non-IEEE type; add is the QD 'sloppy' add; the Google Benchmark table mixes latency (add/mul) and independent-op (div/sqrt) timings; bodies are static inline behind SIMD_F128_IMPLEMENTATION, so the README's one-TU rule breaks multi-TU builds (inferred); default CMake build is scalar without FMA.

## Caveats and trade-offs

Weak evidence. No CPU model or compiler version is given (the Google Benchmark output shows only 12 x 3266.69 MHz with a 16 MiB L3). The README's two benchmark tables disagree (multiply 3.38x vs 2.59x; division 1.73x vs 1.56x, derived from page data), so the headline '1.7x to 3.3x' comes from the more favourable run. The comparison is against __float128, not GMP or MPFR (the README only calls GMP/MPFR 'Very Slow', with no numbers). Double-double (\~106-bit mantissa) is not IEEE binary128: it has a smaller exponent range and no correct rounding, and the README warns of catastrophic cancellation and says to use __float128 when binary128 compliance is needed. In the Google Benchmark mul loop (bench_arithmetic.cpp) the value is multiplied by about 2 every iteration, so it overflows to infinity quickly. The project is very new (first commits 2026-08-09) and has 2 stars.

Header-only C11/C++11 double-double arithmetic: about 31 digits, zero allocation, no dependencies, AVX2/SSE2/NEON/WASM-SIMD or scalar fallback. Not IEEE binary128 compliant and susceptible to catastrophic cancellation; no arbitrary precision.

## Maintenance

Brand-new (2026-08) single-author MIT project with 2 stars, active through 2026-08-17 (v1.6.0, PyPI 1.6.2), small enough to vendor but not yet proven in outside use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** These are first-party numbers from the project's own benchmarks/bench_compare.c, which uses loop-carried add/mul/div over 10M iterations against GCC __float128. No CPU model or compiler version is given for the published runs; the Google Benchmark output shows only '12 X 3266.69 MHz'. The flags can be inferred only from CMakeLists.txt, so this is C.
- **Verifier notes:** Metadata confirmed: MIT, not archived or a fork, 2 stars, last commit 2026-08-17 ('release version 1.6.0'), PyPI simd-f128 latest 1.6.2 uploaded 2026-08-17. The category is a poor fit: this is extended-precision floating point (double-double), not big-integer/arbitrary precision; the orchestrator may want to move it to a floating-point or numerics category.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tiw302/simd-f128>
  - <https://github.com/tiw302/simd-f128/commits>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/README.md>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/benchmarks/bench_compare.c>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/benchmarks/bench_arithmetic.cpp>
  - <https://pypi.org/pypi/simd-f128/json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/README.md>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/include/simd_f128.h>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/include/simd_f128_vector.h>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/include/simd_f128.hpp>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/benchmarks/bench_arithmetic.cpp>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/benchmarks/bench_math.cpp>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/benchmarks/bench_compare.c>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/docs/math_theory.md>
  - <https://raw.githubusercontent.com/tiw302/simd-f128/HEAD/CMakeLists.txt>
  - <https://github.com/tiw302/simd-f128/issues?q=is%3Aissue>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tiw302/simd-f128`) · [data/wave8/enrich/raw/github_com_tiw302_simd_f128.json](../../../data/wave8/enrich/raw/github_com_tiw302_simd_f128.json) (enrichment confidence 0.75)

</details>
