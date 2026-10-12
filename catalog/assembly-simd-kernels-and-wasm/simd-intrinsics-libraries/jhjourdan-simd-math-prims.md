# SIMD-math-prims (vectorizable approximate sin, cos, log, exp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> One MIT header of polynomial sin/cos/exp/log approximations that compilers auto-vectorise; 21-36x over scalar libm floats, about 1e-5 error.

| | |
|---|---|
| **Beats** | libm sinf, cosf, logf, expf (scalar single-precision functions) |
| **Claimed result** | README output: sinf 213.3M/s vs sinapprox 6238.5M/s (about 29x); cosf 226.7M/s vs cosapprox 7380.7M/s (about 33x); logf 115.2M/s vs logapprox 4112.9M/s (about 36x); expf 111.3M/s vs expapprox 2366.8M/s (about 21x) (ratios derived from page data). README text: 'speedups from 20x to 40x' with gcc vectorisation. |
| **Workload** | test_fun.cpp: each function is evaluated over a 1024-element array of floats drawn uniformly from [0, 1) (vals_test), repeated 100,000 times for libm and 1,000,000 times for the approximations, single thread, timed with clock() and reported in million evaluations per second. The intervals [-pi, pi], [1e-10, 10] and [-10, 10] are used only for the separate error statistics (bias, mean/RMS/min/max error against libm), not for the throughput loop. |
| **Metric** | throughput |
| **Compiler and flags** | Makefile: g++ test_fun.cpp -o test_fun -Wall -W -O3 -std=c++11 -march=native (auto-vectorisation); gcc version not stated; README says clang also works |
| **Adoption** | 106 stars |
| **Last commit** | 2020-04-19 |
| **Links** | [repository](https://github.com/jhjourdan/SIMD-math-prims) · [benchmark](https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/README.md) |

## Verdict

README output 'on my computer' (CPU, compiler version and libm not stated; Makefile g++ -O3 -std=c++11 -march=native), 2015 code, float, 1024 inputs in [0, 1) looped 1e5 times for libm and 1e6 times for the approximations, timed with clock(): sinf 213.3 vs sinapprox 6238.5 M evaluations/s (about 29x), cosf 226.7 vs 7380.7 (33x), logf 115.2 vs 4112.9 (36x), expf 111.3 vs 2366.8 (21x), ratios derived from page data. It compares a vectorised approximation against scalar, correctly rounded libm, not against a vector libm.

## Use it when

- Large float arrays of exp/log in simulation or ML inner loops (the author's motivation was a Metropolis-Hastings sampler) where about 1e-5 relative or absolute error is acceptable
- sin/cos of angles you already keep in [-pi, pi] (phases, rotations, oscillators) when you want vectorised code with no intrinsics and no dependency
- Toolchains where you cannot use -ffast-math plus glibc libmvec, SLEEF or SVML, but GCC or Clang auto-vectorisation is available
- As a short, readable starting point for your own Sollya-fitted kernels: the Sollya commands are in the header comments

## Skip it when

- Arguments outside [-pi, pi]: there is no range reduction, so sinapprox(10) returns about 896 and sinapprox(100) about 2.1e12 (float re-evaluation of the current coefficients); reduce the angle yourself first
- Code that needs IEEE special cases or subnormals: logapprox returns -inf for NaN, a finite 88.72 for +inf and about -88.02 for 1e-40 (true -92.10); expapprox returns 0 below about -87.3 and is documented as invalid for NaN
- Results that must be exact at anchor points: logapprox(1.0) is about 1.0e-5, not 0 (the approxmath port documents the same effect, 4.5e-9 for its double log)
- MSVC or other compilers that do not auto-vectorise the union bit tricks (issue #3 reports Visual Studio 2017 did not vectorise exp and log); the double exp/log versions vectorise only with AVX-512DQ according to the header
- Choosing between this and a vector libm: no glibc libmvec (in glibc since 2.22, used with -ffast-math), SLEEF or SVML numbers exist, and glibc 2.27's NEWS lists optimised generic sinf, cosf, expf and logf, a release later than the README's 2015 run, so the scalar baseline is dated as well

## How it is fast

Each function is branch-free arithmetic the auto-vectoriser can map to SIMD lanes: Remez minimax polynomials generated in Sollya (degree 9 odd for sin, degree 8 even for cos, degree 4 for exp's and degree 5 for log's mantissa terms), with exp and log built on IEEE-754 bit manipulation (exp writes the scaled argument into the exponent field, log reads the exponent field and approximates log of the mantissa in [1, 2)). There is no range reduction, table lookup or special-case branching, which is where both the speed and the restricted domains come from.

## Compared with alternatives

Pick it over math_intrinsics, corvus or EVE when you want a 229-line, dependency-free MIT header that the compiler vectorises for any ISA and your inputs already sit in [-pi, pi] or the normal float range; pick those siblings when you need explicit AVX2/NEON code, more functions or full-range arguments, since this header has no range reduction.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (math.h, stdint.h); icsilog.h in the repo is only for the benchmark and is GPL-2.0-or-later |
| **Minimum toolchain** | C++11 per the Makefile (g++ -O3 -std=c++11 -march=native); usable from C via the extern "C" block; vectorisation needs GCC or Clang auto-vectorisation |
| **Platforms** | any IEEE-754 target; float versions vectorise wherever the compiler auto-vectorises (SSE2/AVX2/NEON class); double exp/log need AVX-512DQ to vectorise |
| **Thread safety** | not documented; the functions are pure apart from reading two mutable globals per precision (exp_cst1_f/exp_cst2_f, exp_cst1_d/exp_cst2_d) |
| **Drop-in for the baseline** | partial: same float-in float-out signature as sinf/cosf/expf/logf, but restricted domains, no special-value semantics and about 1e-5 error |

## Gotchas

- Header defines non-const, non-static globals (float exp_cst1_f = 2139095040.f; exp_cst2_f; exp_cst1_d; exp_cst2_d) as a 'workaround' for gcc, so including it from two translation units gives multiple-definition link errors; in C the plain 'inline' functions follow C99 inline rules and can fail to link at -O0. Make them static or const, and static inline, when vendoring.
- Harness flaw in the current test_fun.cpp (does not touch the README numbers, which are float-only): main() fills only vals_test, never vals_test_d, so every double benchmark (sin, cos, log, exp and the _d approximations) runs on 1024 zeros, timing sin(0), cos(0), exp(0) and log(0) = -inf.
- The README output is from the 2015 code: the cos and exp coefficients changed in 2017 (cos(0) = 1, exp(0) = 1 commits) and the benchmark loop gained its __asm__ barrier in 2019 (5c3caea), and nothing was re-measured; the mipac fork's README and older header are an identical 2015 snapshot. A numpy float32 re-evaluation of today's coefficients (no FMA, 2M points) gave max abs error 6.2e-6 for sin and 4.6e-5 for cos in [-pi, pi], 9.1e-6 max relative error for exp in [-10, 10] and 1.3e-5 for log in [1e-10, 10], versus the README's 5.9e-6, 4.0e-5, 8.6e-6 and 9.1e-6.
- Throughput inputs are 1024 floats uniform in [0, 1) for every function, which keeps libm on its easiest small-argument paths and says nothing about the restricted-domain behaviour above.

## Known shortcomings

- CPU and compiler version unstated; compares a vectorised approximation (errors up to 4e-5) with scalar libm and no libmvec or SLEEF baseline; README numbers from 2015 predate the 2019 dead-code fix of the harness; throughput inputs only in [0,1).
- Harness flaw: test_fun.cpp never fills vals_test_d, so all double benches run on 1024 zeros (README rows are float-only and unaffected). README numbers come from 2015 code: cos/exp coefficients changed in 2017 and an asm barrier was added in 2019, never re-measured; the mipac fork is an identical 2015 snapshot. The header defines non-static globals (exp_cst1_f etc.), so a second including translation unit fails to link. No range reduction (sinapprox(10) about 896); logapprox gives -inf for NaN, 88.72 for +inf and wrong subnormals. icsilog.h is GPL-2.0+ (bench only). Baseline is scalar libm from before glibc 2.27; no libmvec or SLEEF comparison.

## Caveats and trade-offs

Output is 'on my computer' with no CPU or compiler version. The README output dates from 2015 (README last changed 2015-10-22), before commit 5c3caea (2019-01-11, 'Prevents dead code optimizations in test_fun.cpp') added an asm barrier to the benchmark loop; the 2015 figures (about 1.5-2 evaluations per cycle) are too low to reflect an elided loop, but they were not re-measured on the fixed harness. The speedup is a vectorised approximation against scalar, correctly rounded libm (gcc does not vectorise sinf/logf calls without -ffast-math and libmvec), so it trades precision for speed: sinapprox max abs error 5.9e-6, cosapprox 4.0e-5, logapprox 9.1e-6, expapprox max relative error 8.6e-6; glibc libmvec or other vector math libraries (SLEEF, SVML) were not compared. Throughput inputs are all in [0, 1), which hits libm's easy small-argument paths. Not intrinsics-based despite the category: plain C written so the compiler auto-vectorises it (closer to wave 1's math-simd-linear-algebra). The mipac fork claim was not checked. [retier] First-party README output from the 2015 code: cos and exp coefficients changed in 2017 and an asm barrier was added in 2019, never re-measured (the mipac fork is an identical 2015 snapshot). Harness flaw: test_fun.cpp never fills vals_test_d, so all double benches run on 1024 zeros; the README rows are float-only and unaffected. Baseline is scalar libm from before glibc 2.27 (no libmvec) with no SLEEF or other vector-math comparison, and the approximations trade accuracy for speed: no range reduction (sinapprox(10) about 896), logapprox gives -inf for NaN, 88.72 for +inf and wrong results for subnormals. The header defines non-static globals (exp_cst1_f etc.), so a second including translation unit fails to link. icsilog.h is GPL-2.0+ (bench only); the library itself is MIT.

Approximate: sin mean absolute error 3.7e-6, cos 2.6e-5, log 5.6e-6 (README output); header-only and portable but relies on compiler auto-vectorisation, so speedups depend on gcc or clang loop vectorisation.

## Maintenance

Abandoned since 2020-04-19 (23 commits, 106 stars, one open question), but MIT-licensed and a single short header that is easy to vendor once the global-variable and inline linkage issues are fixed; a Python/NumPy port exists as approxmath (brendanashworth/approxmath).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README shows first-party output of the repo's own test_fun.cpp against libm sinf/cosf/logf/expf (213.3 vs 6238.5 M/s etc.); the Makefile gives g++ -O3 -std=c++11 -march=native, but no compiler version or CPU model ('on my computer'), so it falls short of A.
- **Verifier notes:** Numbers match the README exactly; ratios 29x/33x/36x/21x are derived from page data. Shortcomings: unspecified CPU and compiler version, accuracy-for-speed trade against scalar libm with no vector-libm baseline, README numbers predate the 2019 dead-code fix of the harness, throughput inputs only in [0, 1), not an intrinsics library. Metadata checked: MIT, 106 stars, last commit 2020-04-19 (abandoned), not a fork.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-112 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/README.md>
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/test_fun.cpp>
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/simd_math_prims.h>
  - <https://github.com/jhjourdan/SIMD-math-prims>
  - <https://github.com/jhjourdan/SIMD-math-prims/commits>
  - <https://github.com/jhjourdan/SIMD-math-prims/commits/master/README.md>
  - <https://github.com/jhjourdan/SIMD-math-prims/commits/master/test_fun.cpp>
  - <https://github.com/jhjourdan/SIMD-math-prims/commit/5c3caea>
- **Sources the enricher read:**
  - <https://github.com/jhjourdan/SIMD-math-prims>
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/README.md>
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/test_fun.cpp>
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/simd_math_prims.h>
  - <https://raw.githubusercontent.com/jhjourdan/SIMD-math-prims/HEAD/icsilog.h>
  - <https://github.com/jhjourdan/SIMD-math-prims/commits/master>
  - <https://github.com/jhjourdan/SIMD-math-prims/commit/5c3caea>
  - <https://github.com/jhjourdan/SIMD-math-prims/issues?q=is%3Aissue>
  - <https://github.com/jhjourdan/SIMD-math-prims/issues/3>
  - <https://github.com/jhjourdan/SIMD-math-prims/issues/5>
  - <https://github.com/jhjourdan/SIMD-math-prims/forks>
  - <https://raw.githubusercontent.com/mipac/SIMD-math-prims/HEAD/README.md>
  - <https://raw.githubusercontent.com/mipac/SIMD-math-prims/HEAD/simd_math_prims.h>
  - <https://raw.githubusercontent.com/bminor/glibc/master/NEWS>
  - <https://pypi.org/pypi/approxmath/json>
  - https://gallium.inria.fr/blog/fast-vectorizable-math-approx/ (unreachable: ENOTFOUND; WebSearch snippet only: logapprox 7.5x faster than icsi_log in tight loops, exp relative error bounded by 1e-5, log absolute error 7e-5 in an earlier version, denormals excluded)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jhjourdan/simd-math-prims`) · [data/wave13/enrich/raw/github_com_jhjourdan_simd_math_prims.json](../../../data/wave13/enrich/raw/github_com_jhjourdan_simd_math_prims.json) (enrichment confidence 0.75)

</details>
