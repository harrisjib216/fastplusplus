# normaldist-benchmark (Ziggurat and AVX/SSE2 Box-Muller)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT (src/ziggurat.cpp is Jochen Voss's GPL-2.0-or-later code)` · 🔴 abandoned

> 2015 benchmark of normal-sample generators; Ziggurat and AVX Box-Muller run 2.8-8x faster than std::normal_distribution with minstd_rand.

| | |
|---|---|
| **Beats** | std::normal_distribution with std::minstd_rand (the 'cpp11random' row) |
| **Claimed result** | Double precision: cpp11random 32.245 ns/sample vs ziggurat 7.086 ns (page lists 4.55x). Single precision: cpp11random 18.642 ns vs ziggurat 6.731 ns and boxmuller_avx 2.253 ns (about 2.8x and 8.3x, derived from page data); boxmuller_sse2 3.752 ns. |
| **Workload** | Filling an array of 1,000,000 standard-normal samples (best of 10 trials) in float and double with Box-Muller, Marsaglia polar, Ziggurat, inverse CDF, CLT, and SSE2/AVX Box-Muller variants. |
| **Metric** | throughput |
| **Hardware** | iMac, Intel Core i5-3330S @ 2.70GHz |
| **Compiler and flags** | clang 6.1 on macOS 64-bit (named in the result file Corei5-3330S@2.70GHz_mac64_clang6.1 linked from the README); build/premake4.lua release config: premake4 'Optimize' flag (-O2) with NDEBUG, plus -mavx -Wall -Wextra -std=c++11 for gmake |
| **Adoption** | 133 stars |
| **Last commit** | 2015-07-10 |
| **Links** | [repository](https://github.com/miloyip/normaldist-benchmark) · [benchmark](https://github.com/miloyip/normaldist-benchmark) |

## Verdict

On an iMac Core i5-3330S (2.7 GHz) with clang 6.1 and libc++, best of 10 runs of 1M samples: double cpp11random (std::normal_distribution + std::minstd_rand) 32.2 ns/sample vs Ziggurat 7.1 ns (4.55x); float 18.6 ns vs Ziggurat 6.7 ns (about 2.8x) and boxmuller_avx 2.25 ns (about 8.3x, derived from page data). Against the same-LCG polar method, Ziggurat's own algorithmic gain is about 1.6-1.8x (derived from page data).

## Use it when

- Choosing a normal-sampling algorithm: the table shows how Box-Muller, polar, inverse CDF, CLT and Ziggurat compare under the same cheap uniform source
- Bulk float fills (Monte Carlo noise, procedural generation) on x86 with AVX where approximate log/sincos accuracy is acceptable: boxmuller_avx reached 2.25 ns/sample
- A scalar Ziggurat for float or double when you can accept GPL-2.0-or-later code or will rewrite it
- As a starting harness to benchmark your own normal sampler against std::normal_distribution

## Skip it when

- Statistically sensitive work: the uniform source is a power-of-two LCG, and the Ziggurat takes its layer index and sign from the LCG's lowest 8 bits, which cycle with period 128/256
- Projects that cannot take copyleft code: src/ziggurat.cpp is GPL-2.0-or-later even though the repo is MIT
- Code that needs a reusable sampler object: each call re-creates the generator at a fixed seed, so every call returns the same sequence and there is no seeding API
- The CLT variants: they fail the repo's own kurtosis check, and clt\*_avx has a buffer-overrun bug (see gotchas)
- Non-x86 targets or modern CPUs without retesting: SIMD paths are SSE2/AVX intrinsics only, and the only published numbers are from a 2012 Core i5 with clang 6.1

## How it is fast

Ziggurat (Marsaglia-Tsang 2000) covers the density with 128 equal-area layers, so about 99% of samples cost one 32-bit draw, a table lookup, a multiply and a compare; log/exp are needed only in the rare wedge and tail cases. The SSE2/AVX Box-Muller variants run 4 or 8 lanes of a 32-bit LCG and use vectorized log and sincos approximations from sse_mathfun/avx_mathfun, producing 8 or 16 floats per loop iteration. Every non-std variant uses a one-multiply LCG (Numerical Recipes constants for 32-bit, a 64-bit LCG for double) as the uniform source, which is far cheaper than minstd_rand plus uniform_real_distribution.

## Compared with alternatives

Use it to compare algorithms or to borrow a minimal Ziggurat or SIMD Box-Muller kernel; for production sampling, Zest (generalized Ziggurat, reported 3.6x over STL normal) or EigenRand (vectorized std-like distributions) give a maintained API with a proper engine. An open issue (#3, 2020) posts a faster single-table Ziggurat (about 4.0 ns vs 7.3-7.8 ns for the repo's version).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for scalar variants; sse_mathfun.h / avx_mathfun.h (zlib license, vendored in src/) for SSE2/AVX variants; premake4 to build the harness |
| **Minimum toolchain** | C++11 (premake gmake build passes -std=c++11 -mavx) |
| **Platforms** | x86/x86-64; the AVX variants need AVX (the 8-lane LCG emulates 256-bit integer multiply with SSE4.1 _mm_mullo_epi32); scalar code is portable |
| **Thread safety** | Each call uses its own stack-local LCG, so concurrent calls are safe but all return the identical sequence; not documented by the author |
| **Drop-in for the baseline** | no |

## Gotchas

- Alignment and size: boxmuller_sse2 needs 16-byte-aligned data and n % 8 == 0; boxmuller_avx needs 32-byte alignment and n % 16 == 0 (the code asserts 16, not 8); scalar boxmuller and polar need even n
- clt_avx steps the index by 4 while storing 8 floats per iteration, so it does twice the work and the last store writes 16 bytes past the end of the buffer; the harness's 32-byte slack may not cover it
- Not like-for-like with std: libc++'s normal_distribution is itself the Marsaglia polar method, and the repo's own polar method with the cheap LCG is already 2.5x faster than cpp11random in double, so most of the headline gap is the uniform source, not the algorithm (derived from page data)
- The SIMD lanes are seeded 1..4 or 1..8 with the same LCG constants, so lanes are linearly related; output is not suitable where independence between samples matters

## Known shortcomings

- src/ziggurat.cpp is GPL-2.0+ inside an MIT repo; the std side pays minstd_rand's cost while the others use a bare LCG.
- clt_avx steps the index by 4 but stores 8 floats: double work plus a 16-byte write past the buffer end on the last iteration. Ziggurat takes layer index and sign from the low 8 bits of a power-of-2 LCG (period 128/256); lanes seeded 1..8, so they are correlated. libc++ normal_distribution is itself the polar method and the repo's polar with a cheap LCG is already 2.5x faster than cpp11random in double, so the ziggurat's algorithmic gain is only 1.6-1.8x (derived from page data). Abandoned 2015.

## Caveats and trade-offs

Not a like-for-like comparison: cpp11random pays for std::minstd_rand plus the library's normal_distribution, while the other implementations use the 'simplest' LCG, so part of the gap is the cheaper, lower-quality uniform source. The README's Speedup column for float is relative to clt16, not to cpp11random; the ratios against std are derived from page data. CLT variants fail the repo's own kurtosis check. src/ziggurat.cpp is GPL-2.0-or-later (Jochen Voss, 2005) inside an MIT repo, so the ziggurat code carries copyleft terms. Single 2012-era CPU and a 2015 toolchain; repo unchanged since 2015-07-10.

Benchmark harness with standalone implementations rather than a packaged library: Ziggurat is Jochen Voss's implementation, Box-Muller SSE2/AVX use sse_mathfun/avx_mathfun approximations and need aligned buffers and n divisible by 2/8; the CLT variants fail the repo's own kurtosis check.

## Maintenance

Abandoned since July 2015 (one open PR and two open issues from 2019-2020); the MIT harness and SIMD kernels are small enough to copy, but the Ziggurat file is GPL-2.0-or-later and needs a better uniform generator before reuse.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README tables (also in result/Corei5-3330S@2.70GHz_mac64_clang6.1.csv) come from public benchmark code (src/\*.cpp, cpp11random = std::normal_distribution with std::minstd_rand); the CPU (Core i5-3330S) is stated, the compiler (clang 6.1, mac64) is named in the linked result file, and build/premake4.lua gives the flags.
- **Verifier notes:** All numbers match the README and the result CSV (float: cpp11random 18.642 ns, boxmuller_avx 2.253, boxmuller_sse2 3.752, ziggurat 6.731; double: cpp11random 32.245, ziggurat 7.086). baseline_stdlib set to libc++ on the inference that Apple clang on macOS links libc++ by default (premake4.lua sets no -stdlib). The README file is readme.md (lowercase).
- **Fields the verifier corrected:** `compiler_and_flags`, `baseline_stdlib`, `license`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/readme.md>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/result/Corei5-3330S@2.70GHz_mac64_clang6.1.csv>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/build/premake4.lua>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/cpp11random.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/boxmuller.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/ziggurat.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/test.h>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/LICENSE>
  - <https://github.com/miloyip/normaldist-benchmark>
  - <https://github.com/miloyip/normaldist-benchmark/commits>
- **Sources the enricher read:**
  - <https://github.com/miloyip/normaldist-benchmark>
  - <https://github.com/miloyip/normaldist-benchmark/issues?q=is%3Aissue>
  - <https://github.com/miloyip/normaldist-benchmark/issues/3>
  - <https://github.com/miloyip/normaldist-benchmark/pulls>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/readme.md>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/build/premake4.lua>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/result/Corei5-3330S@2.70GHz_mac64_clang6.1.csv>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/test.h>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/timer.h>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/lcg.h>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/cpp11random.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/boxmuller.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/boxmuller_sse2.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/boxmuller_avx.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/ziggurat.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/marsagliapolar.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/inverse.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/clt.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/clt_sse2.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/clt_avx.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/null.cpp>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/sse_mathfun.h>
  - <https://raw.githubusercontent.com/miloyip/normaldist-benchmark/HEAD/src/avx_mathfun.h>
  - <https://raw.githubusercontent.com/llvm/llvm-project/HEAD/libcxx/include/__random/normal_distribution.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/miloyip/normaldist-benchmark`) · [data/wave8/enrich/raw/github_com_miloyip_normaldist_benchmark.json](../../../data/wave8/enrich/raw/github_com_miloyip_normaldist_benchmark.json) (enrichment confidence 0.85)

</details>
