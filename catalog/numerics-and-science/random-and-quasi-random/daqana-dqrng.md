# dqrng (xoshiro256++ / PCG64 generators and fast distributions; C++ header-only, R package)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (R package)` · `AGPL-3.0` · 🟡 stale

> R package with header-only xoshiro, PCG64 and Threefry engines, Ziggurat distributions and fast sampling; beats base R's RNG.

| | |
|---|---|
| **Beats** | R's built-in RNG (Mersenne Twister with R's rnorm and sample.int) |
| **Claimed result** | rnorm(1e4) median 654.7 us vs dqrnorm 85.9 us (7.6x, derived from page data); sample.int(1e7, 1e5, replace=TRUE) 7.07 ms vs dqsample.int 296.86 us (24x, derived); sample.int(1e7, 1e5) without replacement 42.8 ms vs dqsample.int 679.1 us (63x, derived). |
| **Workload** | bench::mark from R: rnorm(1e4) vs dqrnorm(1e4); sample.int(1e7, 1e5) and sample.int(1e10, 1e5) with and without replacement vs dqsample.int. |
| **Metric** | throughput |
| **Adoption** | 50 stars; on CRAN |
| **Last commit** | 2025-06-29 |
| **Links** | [repository](https://github.com/daqana/dqrng) · [benchmark](https://github.com/daqana/dqrng) |

## Verdict

First-party bench::mark medians in the README, with no CPU, compiler or R version stated: rnorm(1e4) 654.7 us vs dqrnorm 85.9 us (7.6x), sample.int(1e7, 1e5, replace=TRUE) 7.07 ms vs 296.86 us (24x), and without replacement 42.8 ms vs 679.1 us (63x), ratios derived from page data. These time whole R-level functions (a different engine plus Ziggurat vs inversion, plus different sampling algorithms), not a generator against std::mt19937.

## Use it when

- R code bottlenecked on rnorm/runif/rexp: README medians are rnorm(1e4) 654.7 us vs dqrnorm 85.9 us.
- Unweighted sampling in R, especially without replacement from large ranges: sample.int(1e7, 1e5) 42.8 ms vs dqsample.int 679.1 us; with replacement 7.07 ms vs 296.86 us.
- Rcpp, RcppParallel or OpenMP code that needs reproducible independent streams (clone(stream), xoshiro jumps, PCG streams, Threefry counter splitting), as shown in the parallel vignette.
- R packages whose C++ code should share one seeded engine with the R session (random_64bit_accessor).
- Pure C++ projects only for the bundled standalone engine headers: xoshiro.h (CC0) and pcg_\* (Apache-2.0 or MIT).

## Skip it when

- Standalone C++ without R: dqrng_types.h, dqrng_generator.h and dqrng_sample.h include Rcpp, and dqrng_distribution.h pulls in dqrng_generator.h, so outside R use upstream xoshiro/pcg-cpp with Boost.Random or a C++ library such as EigenRand.
- Codebases that cannot take AGPL-3 (strong copyleft with a network clause) for dqrng's own code.
- Weighted sampling: the C++ dqsample_int ignores prob, and open issue #52 reports R-level dqsample.int with prob about 10x slower than base sample.int for small probability vectors.
- When you must reproduce base R's random streams or keep streams stable across dqrng versions: the engines differ, rexp and dqrexp differ even after register_methods(), and the default engine (0.4.0) and seeding (0.3.0) have changed before.

## How it is fast

It swaps R's MT19937 and inversion normals for small 64-bit engines and Boost.Random's Ziggurat normal and exponential samplers, with specializations so one 64-bit draw yields both the 53-bit double and the 8-bit Ziggurat layer index (generate_double_8bit_pair). Bounded integers use O'Neill's debiased integer-multiplication method (Lemire's multiply-shift with a rare modulo), and 32-bit requests use both halves of a 64-bit draw. Sampling without replacement picks the algorithm by sampling ratio: a partial Fisher-Yates shuffle above 50%, bitset rejection from 0.1% to 50%, and an open-addressing hash set below that.

## Compared with alternatives

Pick dqrng when you work in R/Rcpp and want faster drop-in-style replacements for runif/rnorm/sample.int plus parallel streams; zigg is a lighter R/C++ Ziggurat-only alternative, while pure C++ code is better served by EigenRand (vectorized distributions) or the simdrng and VMT19937 SIMD engines.

## Integration

| | |
|---|---|
| **Form** | R package (CRAN) shipping header-only C++ in inst/include, used via LinkingTo or Rcpp::depends |
| **Dependencies** | R and Rcpp (the generator, type and sampling headers include Rcpp); BH (Boost.Random) for dqrng_distribution.h; sitmo for Threefry; xoshiro.h and the pcg_\* headers are standalone |
| **Minimum toolchain** | C++11 (per the vignette); R &gt;= 3.5.0, Rcpp &gt;= 0.12.16, BH &gt;= 1.64.0-1, sitmo &gt;= 2.0.0 (DESCRIPTION) |
| **Platforms** | wherever R and Rcpp build; PCG64 is disabled on macOS PowerPC and a fallback for compilers without a 128-bit integer was added in 0.4.1; open issue #76 reports 'Cannot install on Windows because of symlink' |
| **Thread safety** | The global RNG is not thread-safe and must not be stored or used across threads (dqRNGkind invalidates it); the parallel vignette makes a thread-local copy per thread with clone(stream) under OpenMP, or uses PCG streams with RcppParallel. |
| **Drop-in for the baseline** | partial — the R functions mirror runif/rnorm/rexp/sample.int and register_methods() swaps R's generator in place, but the numbers differ from base R; at C++ level the engines satisfy UniformRandomBitGenerator and work with &lt;random&gt; and Boost distributions |

## Gotchas

- The C++ API vignette says operator()(range) returns integers in the closed interval [0, range], but the code (multiply-shift with rejection, returning the high half of x\*range) returns [0, range).
- Selecting stream k on the Xo(ro)shiro engines runs k jump() or long_jump() calls, so the cost grows linearly with the stream number.
- The fast Boost specializations (Ziggurat bucket pair, uniform real) are written for random_64bit_generator and random_64bit_accessor only; passing a derived generator type falls back to Boost's generic paths (open issue #65). The uniform specialization also drops Boost's result &lt; max rejection loop, so rounding can return max.
- Every draw through random_64bit_generator is a virtual call; for the tightest loops use the concrete engine type (for example dqrng::xoroshiro128plusplus) directly.

## Known shortcomings

- Baseline is R's RNG, not a C++ incumbent; own code AGPL-3 (vendored pcg Apache-2.0/MIT, xoshiro CC0).
- C++ headers need Rcpp/R, so they are not usable from standalone C++ (only xoshiro.h and pcg_\* are). Vignette says operator()(range) returns [0, range] but code returns [0, range). Open #65: fast Boost specializations do not apply to derived generator types. Uniform specialization skips Boost's &lt; max check, so rounding can return max. #52: with prob, dqsample.int is \~10x slower than base sample.int.

## Caveats and trade-offs

The baseline is R's built-in RNG and sampling functions, not std::mt19937 or another C++ generator; no C++ benchmark against std:: engines exists in the README or vignettes/dqrng.Rmd. No hardware or compiler is stated. The speedups mix a different engine with different algorithms (Ziggurat normals vs R's inversion; different sampling algorithms), so they are not generator-only gains, and the 63x sampling-without-replacement figure is largely algorithmic. Licensing: dqrng's own code is AGPL-3 (strong copyleft with a network clause), while the vendored generator headers are permissive (inst/include/pcg_\* Apache-2.0 or MIT, inst/include/xoshiro.h CC0) per LICENSE.note; the bundled C++ headers depend on Rcpp/BH/sitmo for the R-facing parts.

The RNG and distribution code is a C++ header-only library usable from C++ (xoshiro.h is CC0, pcg_\* headers are Apache-2.0 or MIT per LICENSE.note), but the package as a whole is AGPL-3.0 strong copyleft. R-centric API (registers as a user-supplied R RNG).

## Maintenance

Stale (last commit 2025-06-29, DESCRIPTION version 0.4.1.1, 16 open issues) but on CRAN with CI and coverage; the package is AGPL-3, while the bundled xoshiro.h (CC0) and pcg_\* (Apache-2.0 or MIT) headers can be copied on their own terms.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README (generated from README.Rmd) shows first-party bench::mark medians against R's rnorm and sample.int with no hardware, compiler or flags; no C++-level comparison against std::mt19937 was found in the README or the dqrng vignette, so C.
- **Verifier notes:** All three README numbers and the derived ratios (7.6x, 24x, 63x) check out. Metadata confirmed: DESCRIPTION License AGPL-3, 50 stars, not archived, last commit 2025-06-29 (stale).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/daqana/dqrng>
  - <https://github.com/daqana/dqrng/commits/main>
  - <https://github.com/daqana/dqrng/tree/main/vignettes>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/README.md>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/DESCRIPTION>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/LICENSE.note>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/vignettes/dqrng.Rmd>
- **Sources the enricher read:**
  - <https://github.com/daqana/dqrng>
  - <https://github.com/daqana/dqrng/issues>
  - <https://github.com/daqana/dqrng/issues/65>
  - <https://github.com/daqana/dqrng/issues/52>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/README.md>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/DESCRIPTION>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/LICENSE.note>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/vignettes/dqrng.Rmd>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/vignettes/cpp-api.Rmd>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/vignettes/sample.Rmd>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/vignettes/parallel.Rmd>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/inst/include/dqrng_distribution.h>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/inst/include/dqrng_generator.h>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/inst/include/dqrng_sample.h>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/inst/include/dqrng_types.h>
  - <https://raw.githubusercontent.com/daqana/dqrng/HEAD/inst/include/xoshiro.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/daqana/dqrng`) · [data/wave8/enrich/raw/github_com_daqana_dqrng.json](../../../data/wave8/enrich/raw/github_com_daqana_dqrng.json) (enrichment confidence 0.8)

</details>
