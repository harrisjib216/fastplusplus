# VDT (VectoriseD maTh)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `LGPL-3.0-or-later` · 🟡 stale

> Header-only Padé-polynomial libm replacements for exp/log/trig/asin-acos-atan/isqrt, auto-vectorizable, 1.3-13x faster scalar.

| | |
|---|---|
| **Beats** | &lt;cmath&gt; (libm) |
| **Claimed result** | Paper Table 1 (ns/call, glibc 2.12 libm vs VDT v0.3.6), scalar double: Exp 102.0 vs 8.00 (\~12.8x), Log 32.28 vs 11.48 (\~2.8x), Sin 77.77 vs 16.50 (\~4.7x), Cos 77.60 vs 14.41 (\~5.4x), Tan 89.69 vs 10.59 (\~8.5x), Asin 21.25 vs 8.94 (\~2.4x), Atan 15.56 vs 8.41 (\~1.9x), Isqrt 5.66 vs 4.27 (\~1.3x). Vectorised AVX2+fma, e.g. Log 1.47 ns (\~22x). Scalar single-precision Expf, Logf and Isqrtf are slower than libm (8.01 vs 7.52, 11.93 vs 10.90, 1.87 vs 0.63). README table (i7-3930K): Exp 16.7 vs 6.1/3.8/2.9 (scalar/SSE/AVX, \~2.7x/4.4x/5.8x), Log 34.9 vs 12.5/5.7/4.2 (\~2.8x/6.1x/8.3x), Tan 46.6 vs 12.5/6.3/5.6 (\~3.7x/7.4x/8.3x). (derived from page data) |
| **Workload** | Paper: 5 million random inputs over each function's domain (at most [-5000,5000]), timings averaged over 250 repetitions, scalar and array signatures with SSE/AVX/AVX2/AVX2+FMA. README table: double-precision ns/call over [-5000,5000] ((0,5000] for isqrt, [-1,1] for asin/acos). |
| **Metric** | throughput |
| **Hardware** | Paper: Intel Core i7-4770K @ 3.50GHz, Scientific Linux 6, glibc 2.12. README table: Intel Core i7-3930K @ 3.20GHz, Scientific Linux 6 |
| **Compiler and flags** | GCC 4.8.1 (paper; optimization flags not stated). The README table states no compiler. |
| **Adoption** | 59 stars; used in LHC experiment software and the Geant4 simulation toolkit at CERN |
| **Last commit** | 2025-04-03 |
| **Links** | [repository](https://github.com/dpiparo/vdt) · [benchmark](https://iopscience.iop.org/article/10.1088/1742-6596/513/5/052027) |

## Verdict

The refereed CHEP2013 paper (glibc 2.12 libm vs VDT v0.3.6, GCC 4.8.1, Intel Core i7-4770K) reports scalar double-precision speedups from \~1.3x (isqrt) to \~12.8x (exp), with AVX2+FMA-vectorized log reaching \~22x; the README's separate i7-3930K table shows smaller but consistent scalar gains (Exp 2.7x, Log 2.8x, Tan 3.7x) rising to 4-8x with SSE/AVX. Both sources agree that scalar single-precision expf/logf/isqrtf are slower than libm.

## Use it when

- Hot loops calling exp/log/sin/cos/tan/asin/acos/atan/atan2/isqrt millions of times where \~0.1-0.5 ULP error is acceptable, e.g. physics simulation and reconstruction code (VDT originated at CERN and is used in Geant4 and LHC experiment software).
- Code that can call the array (\*_v) signatures or already auto-vectorizes, since SIMD gains (SSE/AVX/AVX2+FMA) are consistently larger than scalar gains in both the README table and the cited paper.
- x86-64 builds where you can pick SSE/AVX/AVX2/FMA at CMake configure time, or ARM builds via the NEON CMake option (though NEON is not exercised in the published benchmarks).
- Projects willing to vendor a small LGPL-3 header-only library and either call vdt:: functions directly or use the PRELOAD build to intercept an existing libm-calling binary without recompiling it.

## Skip it when

- Need bit-identical results to libm/std math (finance, reproducibility-critical or correctness-critical code) — VDT trades \~0.1-0.5 ULP accuracy for speed on every function.
- Building on Windows: issue #1 (open) reports it isn't compatible (__restrict__ vs __restrict, missing _USE_MATH_DEFINES) with no merged fix.
- Building on aarch64: default CMake option SSE=ON still passes -msse and breaks the build (issue #21, filed 2025-04-29, open, unresolved as of the last commit).
- Scalar single-precision expf/logf/isqrtf specifically — the record's own benchmark numbers show these particular scalar variants are slower than glibc libm.
- Teams that need active upstream support: last commit 2025-04-03, several issues open for years (CMake overwrites user CXX flags, clang linking error, Python 3.12 removed the imp module the Python scripts depend on).

## How it is fast

Each function is a Padé/minimax rational-polynomial approximation adapted from the Cephes math library, evaluated with a small fixed number of multiply-adds instead of libm's argument-reduction-and-table-lookup algorithms. The scalar code uses no intrinsics, so it auto-vectorizes under GCC/Clang/ICC into SSE/AVX/AVX2(+FMA) loops; the array (\*_v) signatures make this explicit for the compiler and unlock the larger SIMD gains. Accuracy is deliberately relaxed (\~0.1-0.5 average LSB difference from libm per the README's own table) to keep polynomial degree and branching low.

## Compared with alternatives

Pick VDT over SLEEF or trigno_simd_cpp when you want one small header-only LGPL library covering the whole transcendental family (exp/log/trig/inverse-trig/isqrt) with a production track record in CERN/Geant4 physics code, rather than SLEEF's correctly-rounded (1-ulp) precision or trigno_simd_cpp's narrower sin/cos/tan-only scope; choose SLEEF instead when correct rounding matters more than raw speed.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (optional Vc library integration via USE_VC CMake option) |
| **Minimum toolchain** | GCC &gt;=4.8, AppleClang &gt;=5.0, Clang &gt;=3.3, or ICC &gt;=15.0 (enforced by CMakeLists.txt); C++11 is required only to build the optional DIAG benchmarking/unit-test tools, not to use the headers |
| **Platforms** | x86-64 primarily (SSE on by default, AVX/AVX2/FMA opt-in via CMake flags); NEON is an opt-in CMake option for ARM but the default aarch64 build is currently broken by the SSE flag (issue #21); not Windows-compatible per issue #1 |
| **Thread safety** | not documented; the scalar functions inspected (exp.h, stdwrap.h) are stateless/pure with no shared mutable state, so concurrent calls appear safe, but no explicit guarantee is stated anywhere in the docs |
| **Drop-in for the baseline** | partial — functions are not std:: overloads, callers must explicitly call vdt::fast_\* instead of std::exp/std::sin/etc.; only the optional PRELOAD build mode intercepts existing libm calls at runtime without source changes |

## Gotchas

- fast_expf has a documented undefined-behavior bug (left shift of a negative value) for large negative inputs such as -163.48, caught by UBSan; open since 2019 (issue #10) with a proposed but unmerged fix.
- Default CMake option SSE=ON means a plain `cmake .` still emits -msse even on non-x86 targets, which currently breaks aarch64 builds (issue #21).
- Accuracy varies per function: the README's own table shows isqrt averaging \~0.45 LSB off libm, the largest deviation of any function in the library.
- CMake overwrites user-supplied CMAKE_CXX_FLAGS instead of appending to them (issue #8, open since 2018).

## Caveats and trade-offs

Baseline is an old glibc 2.12 libm; some libm timings (scalar exp 102 ns, sinf/cosf/tanf \~178 ns over [-5000,5000]) are pathological for that version and inflate a few ratios. Optimization flags are unstated in both paper and README. Scalar single-precision expf/logf/isqrtf are slower than libm. Functions are approximate (average \~0.1-0.5 LSB difference vs libm). Hardware is \~2012-2013.

Results are approximate (documented average bit-level difference vs libm per function, e.g. up to \~0.45 ULP for isqrt); functions live in a separate vdt:: namespace with fast_ prefixes rather than being a drop-in for std math calls, though a PRELOAD build mode can intercept libm calls at runtime.

## Maintenance

Maintenance is stale (last commit 2025-04-03; multiple issues from 2016-2025 remain open, including a Windows-incompatibility report and an unfixed UB bug), but it's LGPL-3.0-or-later, header-only, and small enough to vendor; it's still cited in the repo description as used in CERN's Geant4 and LHC experiment software.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C. The project's refereed CHEP2013 paper (J. Phys.: Conf. Ser. 513 052027, open access) has Table 1 timing VDT against glibc 2.12 libm with GCC 4.8.1 on a Core i7-4770K. Benchmark code is public (progs/vdtPerfBenchmark.cpp), but optimization flags are not stated, so not A. The few &gt;50x entries (vectorised Exp, Sinf/Cosf/Tanf) come from very slow glibc 2.12 timings the paper itself discusses; the headline scalar gains are 1.3-13x, so no cap was applied.
- **Verifier notes:** README numbers and the record's derived ratios are all correct. The tier moves to B because of the refereed CHEP2013 paper; the numbers now come from it. License confirmed as LGPL-3.0-or-later: Licence.txt says 'version 3 ... or (at your option) any later version', although GitHub reports NOASSERTION.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dpiparo/vdt>
  - <https://github.com/dpiparo/vdt/blob/master/ReadMe.md>
  - <https://github.com/dpiparo/vdt/blob/master/Licence.txt>
  - <https://github.com/dpiparo/vdt/blob/master/progs/vdtPerfBenchmark.cpp>
  - <https://iopscience.iop.org/article/10.1088/1742-6596/513/5/052027>
  - <https://iopscience.iop.org/article/10.1088/1742-6596/513/5/052027/pdf>
- **Sources the enricher read:**
  - <https://github.com/dpiparo/vdt>
  - <https://github.com/dpiparo/vdt/blob/master/ReadMe.md>
  - <https://github.com/dpiparo/vdt/blob/master/Licence.txt>
  - <https://github.com/dpiparo/vdt/blob/master/include/exp.h>
  - <https://github.com/dpiparo/vdt/blob/master/include/vdtMath.h>
  - <https://github.com/dpiparo/vdt/blob/master/CMakeLists.txt>
  - <https://github.com/dpiparo/vdt/blob/master/include/stdwrap.h>
  - <https://github.com/dpiparo/vdt/issues/1>
  - <https://github.com/dpiparo/vdt/issues/10>
  - <https://github.com/dpiparo/vdt/issues/21>
  - https://github.com/dpiparo/vdt/issues (list of open/closed issues)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/dpiparo/vdt`) · [data/wave1/enrich/raw/github_com_dpiparo_vdt.json](../../../data/wave1/enrich/raw/github_com_dpiparo_vdt.json) (enrichment confidence 0.65)

</details>
