# math_intrinsics

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🟢 active

> Single C header of branchless AVX2 (8-lane) and NEON (4-lane) float32 sin, cos, exp, log, pow and more; libm comparison is not like-for-like.

| | |
|---|---|
| **Beats** | C standard library scalar float math functions (acosf, asinf, atanf, cbrtf, cosf, sinf, expf, exp2f, logf, log2f); libc and compiler not stated |
| **Claimed result** | AVX2 vs C std: acos 723.7 ms vs 5408.2 ms (7.47x), asin 7.83x, atan 5.13x, cbrt 12.84x, cos 17.62x, sin 18.14x, exp 5.30x, exp2 2.06x, log 16.51x, log2 7.50x. The __MATH_INTRINSINCS_FAST__ mode adds roughly 1.4x to 1.9x for sin, cos, acos, asin, exp2 and pow. |
| **Workload** | tests/benchmark.c (README run matches commit a9e8fe5, NUM_ITERATIONS 1,000,000,000; current code uses 200,000,000): the AVX2 loop evaluates 8 independent lanes starting at 0..0.875 and stepping by FLT_EPSILON (inputs stay in about [0, 2]); the C std loop calls acosf/asinf/atanf/cbrtf/cosf/sinf/expf/exp2f/logf/log2f through a function pointer in a serial dependency chain total += f(total), seeded with the SIMD time in ms. |
| **Metric** | throughput |
| **Hardware** | old Intel Core i7 from 2018 (model not stated) |
| **Compiler and flags** | -O3 -mavx2 -mfma for the benchmark targets (tests/CMakeLists.txt, non-MSVC); compiler of the README run not stated (CI builds with clang on ubuntu-latest and the default compiler on macos-latest) |
| **Adoption** | 38 stars |
| **Last commit** | 2025-11-23 |
| **Links** | [repository](https://github.com/Geolm/math_intrinsics) · [benchmark](https://github.com/Geolm/math_intrinsics) |

## Verdict

The README's 2.06x (exp2) to 18.14x (sin) speedups are real output of tests/benchmark.c at commit a9e8fe5 (1e9 elements, -O3 -mavx2 -mfma, 'old Intel Core i7 from 2018', compiler and libm unstated). They compare 8-lane AVX2 throughput on inputs stuck at 2.0 with a serial libm chain that runs on NaN, infinity or arguments near 880, so they show only that the code is SIMD and branchless, not how much faster it is than libm (tier D).

## Use it when

- Game, graphics, audio or DSP code that already works on __m256 or float32x4_t and needs sin/cos/exp/log on moderate arguments (unit tests cover sin and cos on [-10, 10], exp on [-87, 87]) at about 1e-7 absolute or relative error.
- x86-64 builds compiled with -mavx2 (-mfma optional) where adding a large dependency such as SLEEF is not wanted; one MIT header with no dependencies.
- Code that needs sine and cosine together: mm256_sincos_ps returns both for the cost of one evaluation.
- Apple Silicon (macOS/iOS) NEON builds that want the same API shape as the AVX2 version.
- Visual or audio work that can accept the fast mode's larger errors (up to 6.5e-5 for asin/acos, 8.9e-6 for pow) for a self-reported 1.4-1.9x more speed.

## Skip it when

- Linux or Windows on ARM64: the header picks the NEON branch only when both __ARM_NEON and __ARM_NEON__ are defined. clang 18 defines __ARM_NEON__ for arm64-apple-macos but not for aarch64-linux-gnu or aarch64-pc-windows-msvc, so those targets fall into the AVX branch and stop at immintrin.h's '#error ... only meant to be used on x86' (checked with clang -fsyntax-only in this session).
- Large or arbitrary arguments: sin/cos use float Cody-Waite reduction with an int32 conversion (the fast mode uses x - round(x/2pi)\*2pi), with no Payne-Hanek path and tests only on [-10, 10]; log/log2 clamp denormal inputs to FLT_MIN before taking the logarithm.
- pow on general inputs: it is exp(y\*log(x)), so a negative base with an integer exponent returns NaN (log of a negative number) and a zero base with a negative exponent returns 0 instead of +inf. The README says pow and atan2 are not special-case compliant, and the tests use only exponents y = sin(x) in [-1, 1].
- Double precision, AVX-512, SSE-only or runtime CPU dispatch: none exist; the whole translation unit must be compiled with -mavx2.
- If you need a measured speedup over libm: the only published numbers come from the flawed harness described in gotchas, and the author says 'Performance is not the focus.'

## How it is fast

Every call evaluates 8 (AVX2) or 4 (NEON) lanes with no branches: domain errors, infinities and zero are handled with compare masks and blends instead of if statements. The kernels are Cephes single-precision polynomials evaluated with FMA (Horner form), with Julien Pommier's sse_mathfun code for log/exp/sincos (three-constant Cody-Waite reduction by pi/4), integer exponent/mantissa bit manipulation for log, exp2 and cbrt (plus one Newton step for cbrt), and pow computed as exp(y\*log(x)). The __MATH_INTRINSINCS_FAST__ mode swaps in shorter lolremez polynomials, a single-step 2\*pi reduction from hlslpp, and NVIDIA Cg's asin approximation.

## Compared with alternatives

Pick it over corvus when you want a dependency-free MIT C header that offers the same float32 function set for both AVX2 and Apple NEON and you will measure speed yourself. corvus publishes per-element measurements against vendor libm (about 5.5x for cos/sin on Zen 4), while this library has no valid libm comparison. LitMath is the .NET option and recip_rsqrt_benchmark only covers reciprocal and rsqrt.

## Integration

| | |
|---|---|
| **Form** | header-only (stb-style; implementation enabled by a macro in one translation unit) |
| **Dependencies** | none (immintrin.h or arm_neon.h) |
| **Minimum toolchain** | C99 compiler with AVX2 intrinsics (-mavx2, optionally -mfma) or Apple clang for NEON; the implementation part does not compile as C++ under g++ (6 'taking address of temporary array' errors from (float[]){...} compound literals; clang++ accepts them with a -Wc99-extensions warning), so define the implementation macro in a .c file; declarations are wrapped in extern "C" |
| **Platforms** | x86-64 with AVX2 (FMA used when __FMA__ is defined); AArch64 NEON only where __ARM_NEON__ is also defined (Apple clang); not Linux or Windows ARM64 as written |
| **Thread safety** | not documented; pure functions with no global state |
| **Drop-in for the baseline** | partial: the same function set as the libm float calls, but on 8-wide (AVX2) or 4-wide (NEON) vectors, so the calling loop must be vectorized by hand |

## Gotchas

- Benchmark harness flaw (tests/benchmark.c, README run at commit a9e8fe5): the SIMD side measures throughput on independent lanes, while libm runs a serial latency chain total += f(total) seeded with the SIMD time in ms. In that chain acosf/asinf get |x| &gt; 1 and return NaN from then on, expf/exp2f overflow to +inf after one call, and sinf/cosf run on arguments near 880. On top of that, the SIMD inputs start in [0, 0.875] and step by FLT_EPSILON, and round-to-even stalls them at exactly 2.0 after 16,777,216 of the 125,000,000 vector iterations (float32 simulation in this session). So the SIMD side mostly evaluates one constant vector, which is out of domain (NaN) for acos and asin. The 2.06x-18.14x ratios are not a measure of speed against libm.
- The fast-mode macro is spelled __MATH_INTRINSINCS_FAST__ (note INTRINSINCS); a correctly spelled name silently does nothing.
- Gaps in the unit tests behind the README's max-error figures: relative error is |approx - ref| / ref with a signed ref, so negative results (cbrt on [-1000, 0), log/log2 below 1) always pass. The log/log2 grid runs from FLT_EPSILON to 1e20 in 32768 steps of about 3e15, so ordinary arguments between 1e-7 and 3e15 are never sampled. Only 1024 points are used for sin, cos, acos, asin and atan.
- The README says NEON is tested only by hand on an M1 Pro. tests/CMakeLists.txt builds universal arm64;x86_64 binaries on macOS and passes -mavx2 -mfma to both slices; whether the macOS CI job actually runs the NEON slice was not checked.

## Known shortcomings

- Downgraded C to D: the README numbers come from tests/benchmark.c at a9e8fe5, which times 8-lane AVX2 throughput on inputs in [0,2] against a serial libm chain total += f(total) seeded with milliseconds (723.73), so acosf/asinf ran on NaN, expf/exp2f on +inf and sinf/cosf near 880; compiler and CPU unstated. Crippled baseline, not fabricated.
- Enricher: the SIMD inputs step by FLT_EPSILON and stall at exactly 2.0 after 16,777,216 of 125M iterations (round-to-even), so the SIMD side mostly evaluates one constant vector (NaN for acos/asin); the unit tests divide relative error by the signed reference so negative results always pass and the log grid step (about 3e15) never samples ordinary arguments; pow(negative base, integer exponent) returns NaN and pow(0, negative) returns 0; the NEON branch needs __ARM_NEON__ so Linux/Windows ARM64 hit the immintrin.h #error; the implementation fails under g++.

## Caveats and trade-offs

Baseline harness is not like-for-like: the SIMD side is a throughput loop over 8 independent lanes with inputs in about [0, 2], while the libm side is a latency-bound serial chain total += f(total) seeded with the SIMD time in milliseconds (README run, commit a9e8fe5), so acosf/asinf received |x|&gt;1 and then NaN for the whole run, expf/exp2f overflowed to +inf after the first call and sinf/cosf ran on arguments near 880 (current code seeds with seconds, but log2f still drops to NaN and acosf/asinf still leave the domain after one or two calls). The 2.06x-18.14x ratios are therefore not a valid measure of speed against libm. Compiler, libm (glibc or Apple) and CPU model of the README run are not stated ('old Intel Core i7 from 2018'). The author writes 'Performance is not the focus.' The benchmark source is tests/benchmark.c (not visible in the repo root). Fast-mode gains (\~1.4x-1.9x for sin, cos, acos, asin, exp2, pow) are against the library's own precise mode. No comparison with SLEEF or xsimd math (both catalogued).

Single header; AVX2 (x86) and NEON (checked manually on an M1 Pro, not in CI); float only; max errors around 1e-7 for most functions, up to 6.5e-5 for acos/asin in fast mode. Author states performance is not the focus.

## Maintenance

No code changes since 2024-02-05 (later commits touch only the README and LICENSE), no issues filed, 38 stars, 0 forks; MIT and a single header, so easy to vendor for x86 AVX2 and Apple NEON float32 work after checking the ranges you need.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The README numbers match the output of tests/benchmark.c at commit a9e8fe5 (1e9 iterations, 10 functions), but that harness times 8 independent AVX2 lanes on inputs in about [0, 2] against a serial libm chain total += f(total) seeded with the SIMD time in milliseconds (e.g. 723.73), so acosf/asinf run on |x|&gt;1 and then NaN, expf/exp2f overflow to +inf after one call, and sinf/cosf get arguments near 880. The ratios therefore compare throughput on easy inputs with latency on degenerate inputs; with compiler and CPU model also unstated they are directional only.
- **Verifier notes:** Numbers on the README are real program output, but the benchmark compares 8-lane SIMD throughput on in-range inputs with a serial libm chain that runs on NaN/inf or large arguments, so ratios are confounded (crippled-baseline precedent, like AssemblyScript and dp::thread_pool, rather than a reject). Metadata confirmed: MIT (LICENSE 2025), 38 stars, last commit 2025-11-23 ('updated license'), active. Directionally plausible as an AVX2/NEON transcendental header, but should be shown only as D.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-26 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/README.md>
  - <https://github.com/Geolm/math_intrinsics>
  - <https://github.com/Geolm/math_intrinsics/commits>
  - <https://github.com/Geolm/math_intrinsics/tree/main/tests>
  - <https://github.com/Geolm/math_intrinsics/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/tests/benchmark.c>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/.github/workflows/cmake-multi-platform.yml>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/LICENSE>
  - <https://github.com/Geolm/math_intrinsics/commits/main/tests/benchmark.c>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/a9e8fe5bd50656021bd52beb83b85c2f7cc95100/tests/benchmark.c>
- **Sources the enricher read:**
  - <https://github.com/Geolm/math_intrinsics>
  - <https://github.com/Geolm/math_intrinsics/commits/main>
  - <https://github.com/Geolm/math_intrinsics/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/README.md>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/math_intrinsics.h>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/tests/benchmark.c>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/a9e8fe5bd50656021bd52beb83b85c2f7cc95100/tests/benchmark.c>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/tests/test.c>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/.github/workflows/cmake-multi-platform.yml>
  - <https://raw.githubusercontent.com/Geolm/math_intrinsics/HEAD/LICENSE>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/geolm/math_intrinsics`) · [data/wave13/enrich/raw/github_com_geolm_math_intrinsics.json](../../../data/wave13/enrich/raw/github_com_geolm_math_intrinsics.json) (enrichment confidence 0.8)

</details>
