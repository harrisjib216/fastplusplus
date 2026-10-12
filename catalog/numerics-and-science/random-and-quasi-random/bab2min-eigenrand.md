# EigenRand

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only SIMD random distributions for Eigen matrices; roughly 1.6-60x faster than std &lt;random&gt; plus NullaryExpr or Eigen::Random.

| | |
|---|---|
| **Beats** | C++ &lt;random&gt; distributions (std::normal_distribution, std::uniform_real_distribution, std::uniform_int_distribution, etc.) and Eigen::DenseBase::Random |
| **Claimed result** | README: '5\~10 times faster than non-vectorized functions'. Charts (speed-up over the std or Eigen reference, read by eye, approximate): Ubuntu GCC 7.5 AVX2 on Xeon Platinum 8370C: uniformReal about 22x, normal(0,1) about 8x, uniformInt(0\~63) about 10x, cauchy about 15x, binomial(20,0.5) about 24x, discrete(fp32) about 32x, several only about 1.6x-1.7x (chiSquared, gamma(10.5,1), fisherF(5,5), uniformInt(0\~100k)). Windows MSVC 19.29 AVX2 on Xeon Platinum 8171M: about 3x-61x (uniformReal about 61x, gamma(5,3) about 33x, randBits about 3x). macOS clang 13.1.6 NEON on Apple M1 Pro: about 1.1x-15x, but binomial(100,0.75) (about 0.6x) and weibull (about 0.75x) are slower than the reference (orange bars). |
| **Workload** | Generation of whole Eigen matrices of random numbers from many univariate distributions with SSE2/AVX2/AVX512/NEON vectorized generators and Vmt19937_64 versus the equivalent non-vectorized std or Eigen calls. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8370C (AVX2, Ubuntu); Intel Xeon Platinum 8171M (AVX2, Windows); Apple M1 Pro (NEON, macOS) |
| **Compiler and flags** | Ubuntu 18.04 GCC 7.5.0 AVX2; Windows MSVC 19.29.30147 AVX2; macOS Monterey Apple clang 13.1.6 NEON; Eigen 3.4.0. CMakeLists.txt Release flags: -DNDEBUG -DRELEASE -O3 plus EIGENRAND_CXX_FLAGS on GCC/Clang, -DNDEBUG -DRELEASE -O2 -Oi -Gy on MSVC; the CI benchmark workflow (.github/workflows/release.yml) passes -mavx2 (Linux) or /arch:AVX2 (Windows) for its AVX2 matrix entries. The workflow at HEAD runs on ubuntu-22.04/24.04 and windows-2022, so the exact 2022-era chart runs are not reproducible from the current file verbatim. |
| **Adoption** | 105 stars; release 0.6.0 (2026-01-31) |
| **Last commit** | 2026-03-17 |
| **Links** | [repository](https://github.com/bab2min/EigenRand) · [benchmark](https://github.com/bab2min/EigenRand) |

## Verdict

The repo's benchmark generates 1000x1000 Eigen arrays 20 times per distribution. It compares EigenRand against std::mt19937_64 plus the matching std distribution through Eigen NullaryExpr, and against Eigen::Random for 'balanced'. The README bar charts (Eigen 3.4.0; GCC 7.5 AVX2 on Xeon Platinum 8370C, MSVC 19.29 AVX2 on Xeon Platinum 8171M, Apple clang 13.1.6 NEON on M1 Pro) show speed-ups of about 1.6x-32x on Ubuntu, 3x-61x on Windows and 0.6x-15x on M1. All values are read by eye from images, and the runs were on shared CI machines.

## Use it when

- You already use Eigen and generate large random matrices or arrays (e.g. 1000x1000 per call) for Monte Carlo, ML initialization or simulation.
- You need non-uniform distributions in bulk (normal, Cauchy, binomial, discrete, uniformReal). The Ubuntu AVX2 chart shows about 8x-32x for these.
- You want reproducible streams across SSE/AVX2/NEON builds (use P8_mt19937_64), or per-element parameters through vectorization over parameters (uniformReal, normal, binomial and others).
- You want to replace Eigen::Random (rand()-based, unseedable) with a seedable, higher-quality generator.

## Skip it when

- You draw a few scalars at a time outside Eigen expressions. The speed-up comes from bulk packet generation, and the library is tied to Eigen 3.3.4-3.4.x or 5.0.x.
- You need bit-identical streams to std::normal_distribution or other std distributions. The algorithms differ, and outputs only match statistically (checked by Earth Mover's Distance).
- chiSquared, gamma with large shape, fisherF, uniformInt over wide ranges (0\~100k): only about 1.6-1.7x on the Ubuntu AVX2 chart. On Apple M1 NEON, binomial(100,0.75) and weibull are slower than std.
- You need integer distributions for types other than int32_t. UniformIntGen and DiscreteGen static_assert on int32_t, and issue #58 requesting other integral types is open.
- You need a library with many maintainers. It is a single-author project (105 stars), and issue #29 (an access violation in uniformReal for a 5x3 matrix on Eigen 3.3.9) is still open.

## How it is fast

Every distribution has an Eigen packetOp, so a whole SSE2/AVX/AVX2/AVX512/NEON register of samples is produced per step and fused into Eigen's expression evaluation. Uniform reals use the mantissa trick: random bits are placed under a [1,2) exponent and 1 is subtracted. Normal uses vectorized Box-Muller with packet log/sincos and caches the second output. Rejection samplers (uniformInt bitmask rejection, gamma, binomial) pack the accepted lanes into a per-generator cache with a SIMD compress-append, so no lane is wasted. Discrete distributions use the alias method. Vmt19937_64 runs 2 (SSE2/NEON) or 4 (AVX2) Mersenne Twister 64 states in parallel lanes.

## Compared with alternatives

Pick EigenRand when your data already lives in Eigen and you need many distributions (including multivariate and vectorization over parameters) behind one API. Zest or normaldist-benchmark's Ziggurat are lighter for scalar normal/gamma sampling without Eigen. Randompack covers C-callable bulk U(0,1)/N(0,1) with paper numbers, and simdrng/VMT19937 are better if you only need a fast vectorized bit engine.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Eigen 3.3.4-3.4.0 or Eigen 5.0.x (googletest only for the tests) |
| **Minimum toolchain** | C++11 (C++14 with Eigen 5.0.x); CMake 3.9+ only for building tests and benchmarks |
| **Platforms** | x86 and x86-64 (SSE2, AVX, AVX2, AVX512), ARM64 NEON; scalar fallback when Eigen vectorization is off (Vmt19937_64 becomes std::mt19937_64) |
| **Thread safety** | Not documented (issue #25 asked). Engines and generator objects hold mutable state (Box-Muller and rejection caches), so use one engine and one generator per thread. |
| **Drop-in for the baseline** | partial: it accepts std engines and has a std-equivalent distribution for most cases, but it is called through Eigen matrix APIs, not as dist(urng), and its output values differ from libstdc++, libc++ and MSVC |

## Gotchas

- The -Like and generator functions return lazy expressions. Rand::balancedLike(mat, urng) alone does nothing until assigned, and each evaluation draws new numbers from the engine held by reference.
- Vmt19937_64 is a different type and stream depending on the compile-time ISA (Packet8i under AVX2, Packet4i under SSE2/NEON, std::mt19937_64 when unvectorized). Use P8_mt19937_64 when results must match across machines.
- Uniform reals are built by the mantissa trick, so float outputs have 2^-23 granularity and never hit tiny nonzero values (to_nzur adds epsilon/8 where log(0) must be avoided).
- Rejection loops have only a debug-mode assert after 100 iterations (EIGENRAND_CHECK_INFINITY_LOOP). Past bugs include a non-terminating normal (#27, fixed in 0.3.5) and out-of-range uniformInt (#42, fixed in 0.4.1), so pin to 0.6.0 or later.

## Known shortcomings

- macOS NEON chart shows binomial(100,0.75) \~0.6x and weibull \~0.75x, slower than std; the \~61x figure is from the MSVC chart.
- Open issue #29: access violation in uniformReal for a 5x3 matrix on Eigen 3.3.9. Integer distributions support only int32_t. On NEON, binomial and weibull are slower than std.

## Caveats and trade-offs

Charts are bar images (values read by eye); the exact numbers are on GitHub Actions run pages that were not opened. The chart machines (Xeon Platinum 8370C/8171M) are shared CI runners, so noise is likely. Speed-ups range from about 0.6x to about 61x depending on distribution and platform; on Apple M1 Pro NEON binomial(100,0.75) and weibull are slower than the std reference. The std reference is std::mt19937_64 plus the std distribution, which is not vectorizable; EigenRand also offers a vectorized engine (Vmt19937_64). Charts use Eigen 3.4.0; current code supports Eigen 5.0.x.

Requires Eigen (3.3.4 to 5.0.x). The speed-up is for bulk matrix generation and vectorization over parameters; results are not bit-identical to std distributions (vectorized math with accuracy checked by Earth Mover's Distance), and P8_mt19937_64 exists for architecture-independent streams.

## Maintenance

Active, with release 0.6.0 (2026-01-31) adding Eigen 5.0.x and AVX512 support and the last commit on 2026-03-17. MIT-licensed and header-only, so it is easy to vendor alongside Eigen.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README charts state OS, compiler version, CPU model, SIMD target and Eigen version per platform; the benchmark code is public (benchmark/benchmark.cpp, std::mt19937_64 plus std distributions as reference) and the build is public: CMakeLists.txt Release flags (-O3 -DNDEBUG for GCC/Clang, -O2 -Oi -Gy for MSVC) plus the target flag passed by .github/workflows/release.yml (-mavx2 or /arch:AVX2 for the AVX2 runs).
- **Verifier notes:** Ubuntu chart values in the record match; added the Windows and macOS charts, which include two NEON regressions. MIT, 105 stars, last commit 2026-03-17, latest release 0.6.0 (2026-01-31). baseline_stdlib (libstdc++, MSVC STL, libc++) matches the three charted toolchains.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/README.md>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/doxygen/images/perf_avx2_ubu.png>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/doxygen/images/perf_avx2_win.png>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/doxygen/images/perf_neon_mac.png>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/.github/workflows/release.yml>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/LICENSE>
  - <https://github.com/bab2min/EigenRand>
  - <https://github.com/bab2min/EigenRand/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/README.md>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/HEAD/LICENSE>
  - <https://github.com/bab2min/EigenRand/tree/main/EigenRand>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/EigenRand>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/Macro.h>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/doc.h>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/PacketRandomEngine.h>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/RandUtils.h>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/MorePacketMath.h>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/PacketFilter.h>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/Dists/Basic.h>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/Dists/NormalExp.h>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/Dists/Discrete.h>
  - <https://raw.githubusercontent.com/bab2min/EigenRand/main/EigenRand/Dists/GammaPoisson.h>
  - <https://github.com/bab2min/EigenRand/issues?q=is%3Aissue>
  - <https://github.com/bab2min/EigenRand/issues/25>
  - <https://github.com/bab2min/EigenRand/issues/29>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/bab2min/eigenrand`) · [data/wave8/enrich/raw/github_com_bab2min_eigenrand.json](../../../data/wave8/enrich/raw/github_com_bab2min_eigenrand.json) (enrichment confidence 0.8)

</details>
