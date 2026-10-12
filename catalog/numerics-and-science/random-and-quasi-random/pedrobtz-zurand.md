# zurand

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Stateless key-based R RNG package with C core; xoshiro256++ fills \~2.3x dqrng, \~8x runif(), thread-count-independent output.

| | |
|---|---|
| **Beats** | dqrng (R package) and base R runif()/rnorm() (Mersenne Twister); randompack x256++simd (SIMD xoshiro256++) is the closest competitor |
| **Claimed result** | Uniform, 1 thread, Linux x86_64 (AMD EPYC 7763): zurand xoshiro256pp 864 M/s versus randompack x256++simd 688, dqrng 368, base R runif() 104 (README: 1.26x over randompack; derived from page data: about 2.3x over dqrng and 8.3x over runif()). Apple M1, 1 thread: 2196 versus randompack 1918, dqrng 311, runif() 213. Gaussian, 1 thread: EPYC 366 versus randompack 355, dqrng 143, RcppZiggurat 125, rnorm() 28; M1 739 versus 718, 235, 225, 43. Threaded: EPYC 4 threads 1801 uniform versus randompack 684; M1 8 threads 4984 uniform and 3143 normal versus randompack 1888 and 708. README: single-thread lead over dqrng and RcppZiggurat is 2.3-7x. |
| **Workload** | R-level fills of n = 1e7 doubles (uniform and standard normal), millions of values per second, median of five rounds, every package in the same bench::mark() call, 1 thread and all threads, on a GitHub-hosted Linux x86_64 runner and an Apple M1 laptop. |
| **Metric** | throughput |
| **Hardware** | Linux: AMD EPYC 7763, 4 cores, AVX2, OpenMP, GitHub-hosted runner (2026-09-26). Apple M1 MacBook Air (4 performance plus 4 efficiency cores, 16 GB, NEON, mains power), 2026-09-27. README example output from an Intel Core i5-8500B (macOS, R 4.5.2, one thread). |
| **Compiler and flags** | R CMD INSTALL build at -O2 ('an -O2 build, never devtools::load_all()', vignettes/performance.Rmd); compiler name and version not stated; OpenMP on Linux, R's own libomp on macOS; AVX2 and NEON paths; no fused multiply-add in normal sampling. |
| **Adoption** | 0 stars, 0 forks; version 0.1.0, not yet on CRAN ('from CRAN, once released') |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/pedrobtz/zurand) · [benchmark](https://github.com/pedrobtz/zurand) |

## Verdict

R-level fills of 1e7 doubles, every package in one bench::mark() call, median of five rounds, R CMD INSTALL -O2 build with the compiler not named: on a GitHub-hosted AMD EPYC 7763 (AVX2, THP always) zurand xoshiro256pp gave 864 M/s uniform versus CRAN randompack x256++simd 688 (its scalar fallback on x86_64), dqrng 368 and runif() 104, and 366 M/s normal versus 355, dqrng 143, RcppZiggurat 125 and rnorm() 28; on a local Apple M1 2196 versus 1918 uniform and 739 versus 718 normal. Threaded rows (1801 M/s on 4 EPYC threads, 4984 on 8 M1 threads) compare zurand's OpenMP fills with single-threaded competitors.

## Use it when

- R simulations that must give identical numbers regardless of thread count, worker scheduling or call order (future/parallel maps): hand each task a key from rng_key(seed, n) or rng_fold().
- Bulk fills of 1e6+ uniforms or normals in R on a multi-core machine: it is the only R package in its benchmark that threads at the R level (1801 M/s uniform on 4 EPYC 7763 cores; 4984 M/s uniform and 3143 M/s normal on an 8-core M1).
- Single-threaded R code that currently calls runif()/rnorm() in hot loops and can switch API: about 8x (uniform) and 13x (normal) faster than base R on the EPYC runner.
- R packages with C code that need per-thread random fills or streamed chunks that never hold the full vector in memory (zurand.h fill_\*_at, stream_normal).
- Very long virtual vectors read only in part (lazy vectors: x[1:1e6] of a lazy 1e8 vector took a tenth of the time of generating the 1e8).

## Skip it when

- Code that must reproduce existing set.seed()/runif() streams, or users who expect the global-RNG API: values and interface both differ, and changing engine or normal method changes every value.
- C or C++ projects outside R: there is no standalone library (zurand.h includes Rinternals.h and keys come from R); use Randompack's C library, simdrng or Random123 directly.
- Distributions beyond uniform, normal, bounded integer and raw bits (no exponential, gamma, binomial, sampling); dqrng and randompack cover more.
- Small single-threaded fills: against randompack the lead is 1.01-1.08x on normals and 0.97x for 1e5 uniforms on the M1, and fills under 32,768 values never thread.
- Risk-averse production use: version 0.1.0 created in September 2026, not yet on CRAN, 0 stars, a single author; PractRand depth so far covers only the default engine (1 TB; 512 GB for normals).

## How it is fast

The default engine runs a xoshiro256++ recurrence (about five operations per word) on 512-word sub-chunks, each seeded by one Philox4x64-10 call from (key, sub-chunk index); independent sub-chunks are what let it run four lanes of AVX2 (runtime dispatch through a target("avx2") attribute) or eight NEON lanes plus two scalar streams on arm64, and split across OpenMP threads with bit-identical output. Uniforms are converted in registers by mantissa stuffing ((bits &gt;&gt; 12) | 0x3ff0..., minus 1 - 2^-53) and stored directly; normals use NumPy's ziggurat tables with a sign-folded table, a loop unrolled by four over a stack word buffer, and an out-of-line slow path whose fixed-point wedge brackets avoid most exp() calls. Platform tricks: madvise(MADV_HUGEPAGE) on outputs of 4 MiB or more on madvise-mode Linux kernels, and DC ZVA cache-line zeroing for large uniform fills on Apple Silicon.

## Compared with alternatives

Pick zurand over dqrng or randompack's R package when you need multi-threaded R-level fills or results that are bit-identical across thread counts and platforms with key-based substreams; pick Randompack (C library, R, Python, Julia, Fortran) for many distributions or non-R use, and OpenRAND or Random123 when you want counter-based generators in plain C++.

## Integration

| | |
|---|---|
| **Form** | R package (compiled shared library loaded by R; C API header inst/include/zurand.h for LinkingTo packages) |
| **Dependencies** | R only at run time (no Imports); OpenMP optional (on macOS configure links the libomp that R ships); bundles Random123 (BSD-3), NumPy ziggurat tables (BSD-3) and fdlibm exp/log1p |
| **Minimum toolchain** | Minimum R version not documented (DESCRIPTION has no Depends); a C compiler R can use; AVX2 path needs GCC or Clang (target attribute, __builtin_cpu_supports); macOS OpenMP needs the mac.r-project.org OpenMP headers at build time |
| **Platforms** | Linux (glibc and musl), macOS, Windows; x86_64 with optional AVX2 chosen at run time, aarch64 with NEON (DC ZVA on Apple only), scalar elsewhere; bit-identical output on all of these, 32-bit x87 excluded |
| **Thread safety** | R samplers parallelise internally with OpenMP above 32,768 values (rng_threads() caps it, values unchanged); C API fills call no R API and may run from any thread once zurand_get_api() and key_get() have run on the main thread; each fill uses about 40 KB of stack (about 100 KB for positional fills and streams). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the x86_64 peer comparison: the workflow installs CRAN randompack 0.1.10, whose src/Makevars.in (since commit b8fe640, 2026-04-22) compiles no avx2.o and never defines BUILD_AVX2, so its x256++simd engine on x86_64 runs the fallback of eight interleaved scalar xoshiro256++ streams; the vignette's 'both vectorise the generator (AVX2 on x86_64)' is wrong for that build, and the 1.26x uniform and 1.03x normal leads on the EPYC 7763 are over randompack's non-SIMD path. The Apple M1 rows (NEON on both sides: 1.15x uniform, 1.01-1.03x normal, 0.97x at 1e5) are the like-for-like ones.
- The published numbers use default arguments only: rng_uniform(key, n, min, max) with other bounds and rng_normal(key, n, mean, sd) with mean != 0 or sd != 1 add a second full pass over the output (two-wide, FMA-free by design), which no benchmark row measures.
- On Linux kernels in transparent-huge-page madvise mode (the Ubuntu default) zurand itself requests 2 MiB pages for outputs of 4 MiB or more and the competitors do not; on a Neoverse N2 without the request it is at parity with randompack (268 vs 271 M/s uniform). options(zurand.hugepages = FALSE) turns it off; the EPYC runner used THP 'always', so its rows are page-size fair.
- The default xoshiro256pp engine reaches a scattered position by reseeding and stepping up to 511 times; for random-index reads of lazy vectors key with engine = "philox4x64" (7-11x faster per read). Benchmarking a devtools::load_all() build measures an -O0 build about ten times slower.

## Known shortcomings

- First-party README and vignette numbers against R packages (dqrng, base R, randompack) rather than std::mt19937, xoshiro or PCG directly; compiler never named (EPYC 7763 and M1). On madvise-mode Linux kernels zurand requests 2 MiB pages while the competitors do not; without that request it ties randompack (N2 uniform 268 vs 271 M/s) and its real lead over randompack is 1.01-1.26x; threaded rows are not like for like. 0 stars.
- Enricher: the x86_64 peer baseline was not SIMD. The benchmark workflow installs CRAN randompack 0.1.10 (2026-08-24), whose src/Makevars.in (since commit b8fe640, 2026-04-22) builds no avx2.o and never defines BUILD_AVX2, so its x256++simd generator ran the fallback of 8 interleaved scalar xoshiro256++ streams on the EPYC; the vignette's 'both vectorise (AVX2 on x86_64)' is wrong for that build. The fair peer gap is the M1 rows with NEON on both sides: 1.15x uniform, 1.01-1.03x normal, 0.97x at 1e5. Benchmarks use default min/max and mean/sd only (other values add a second full pass, unmeasured); the default xoshiro engine is slow for scattered reads (philox 7-11x faster per read); PractRand depth covers only the default engine (1 TB; normals 512 GB) with philox and threefry at 256 MB smoke tests.

## Caveats and trade-offs

None of the listed baselines (std::mt19937, xoshiro, PCG) is measured directly: competitors are R packages (dqrng, randompack, RcppZiggurat, sitmo) and base R, so numbers include R vector allocation and page faults (vignette: allocating and zeroing a 1e7 vector alone runs at about 1,250 M/s on the Linux runner; forcing 4 KiB pages cut the uniform fill from 837 to 242 M/s and the normal fill from 338 to 162). On Linux kernels in the default madvise mode zurand itself requests 2 MiB pages for outputs of 4 MiB or more while the competitors do not; the vignette's Neoverse N2 table shows zurand without that request at parity with randompack (268 vs 271 M/s uniform, 214 vs 200 normal) and 532/344 with it, so on such kernels much of the lead is page size, not generation. The EPYC runner used transparent huge pages 'always', so its rows are like-for-like on page size. Base R's runif()/rnorm() default is a Mersenne Twister with inversion, so the large gaps against it (derived from page data: about 8.3x uniform and 13x normal on EPYC, 1 thread) are largely algorithm and implementation choice. The real peer is randompack's SIMD xoshiro256++, where the single-thread lead is 1.26x (uniform, x86_64), 1.15x (M1; 0.97x for 1e5 values), and only 1.01-1.08x for normals. The threaded rows are not like-for-like (the competitors have no threaded R-level entry point, as the workflow itself says). Linux numbers come from a shared CI runner launched on demand (workflow_dispatch); the author notes GitHub's M1 runner moved by a third between runs and that zurand is tuned on Apple Silicon, and the M1 numbers were run locally. Compiler not named, so tier C rather than A despite public workflow code and stated CPU models. Brand-new repository (commits from 2026-09-27, version 0.1.0, not yet on CRAN), 0 stars; first-party numbers only. [retier] First-party benchmark workflow against R packages (dqrng, base R, randompack), not std::mt19937, xoshiro or PCG directly; compiler unnamed (EPYC 7763, M1). The x86_64 randompack baseline (CRAN 0.1.10) is built without AVX2, so the EPYC leads (1.26x uniform, 1.03x normal) are over a scalar fallback; on the M1 with NEON on both sides zurand is 1.15x on uniform and 0.97-1.03x on normals. zurand alone requests 2 MiB pages on madvise-mode kernels; threaded rows not like for like; min/max and mean/sd only; 0 stars.

Stateless, key-based API: every value is a pure function of an immutable key and its position, never touches .Random.seed, output bit-identical across platforms and thread counts (including with OpenMP). Default engine xoshiro256++ reseeded every 512 values from Philox4x64-10 (Random123), PractRand clean to 1 TB; Philox4x64 and Threefry4x64 counter-based engines also available. Samplers: uniform, ziggurat normal (NumPy tables, plus McFarland method), integer, raw bits; ALTREP lazy vectors (full scans 1.6-2.7x slower than a materialised vector); C API header for LinkingTo packages. Changing engine changes every value. R package with C core, not a standalone C++ library.

## Maintenance

Actively developed (183 commits between late September and 2026-10-05, many co-authored with an AI coding assistant per the commit log), MIT, version 0.1.0 installable from GitHub but not yet on CRAN; streams carry a version tag so later fixes will not change existing keys' values; its x86_64 lead over randompack is measured against randompack's non-SIMD CRAN build, so treat the M1 margins (1.01-1.15x) as the honest peer gap.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance tables and vignettes/performance.Rmd show every claimed number (864/688/368/104 uniform and 366/355/143/125/28 normal on EPYC 7763; 2196/1918/311/213 and 739/718/235/225/43 on M1; threaded 1801, 4984, 3143), with public benchmark code (.github/workflows/benchmark.yml, tools/benchmark.R) and CPU models, but the compiler is never named (only 'an -O2 build' via R CMD INSTALL) and the numbers are first-party, so C rather than A.
- **Verifier notes:** All README/vignette numbers match the record; metadata (MIT, 0 stars, 0 forks, last commit 2026-10-05, 183 commits) checked on github.com. Added shortcoming: on madvise-mode Linux kernels zurand requests 2 MiB pages for its own output and is at parity with randompack without that request (N2: 268 vs 271 M/s uniform). The 'no fused multiply-add in normal sampling' item in compiler_and_flags was not confirmed in configure or Makevars.in (no -ffp-contract flag there); left as is.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** same-page-size comparison against xoshiro and PCG; AVX2-enabled randompack build on the same host
- **Pages the verifier opened:**
  - <https://github.com/pedrobtz/zurand>
  - <https://github.com/pedrobtz/zurand/commits/main>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/README.md>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/DESCRIPTION>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/vignettes/performance.Rmd>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/tools/benchmark.R>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/.github/workflows/benchmark.yml>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/src/Makevars.in>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/configure>
- **Sources the enricher read:**
  - <https://github.com/pedrobtz/zurand>
  - <https://github.com/pedrobtz/zurand/tree/main/src>
  - <https://github.com/pedrobtz/zurand/commits/main>
  - <https://github.com/pedrobtz/zurand/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/README.md>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/DESCRIPTION>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/NAMESPACE>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/vignettes/performance.Rmd>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/tools/benchmark.R>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/.github/workflows/benchmark.yml>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/src/Makevars.in>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/src/Makevars.win>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/configure>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/src/zurand.c>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/src/zurand_engine.h>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/src/zurand_lazy.h>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/inst/include/zurand.h>
  - <https://raw.githubusercontent.com/pedrobtz/zurand/HEAD/dev/statistical-audit.md>
  - <https://github.com/jonasson2/randompack>
  - <https://github.com/jonasson2/randompack/tree/main/r-package/src>
  - <https://github.com/jonasson2/randompack/commits/main/r-package/src/Makevars.in>
  - <https://github.com/jonasson2/randompack/commit/b8fe640>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/r-package/src/Makevars.in>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/r-package/configure>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/r-package/DESCRIPTION>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/r-package/src/randompack.c>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/r-package/src/randompack_config.h>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/r-package/src/simd_macros.inc>
  - <https://raw.githubusercontent.com/jonasson2/randompack/HEAD/r-package/src/x256pp_neon_scalar.inc>
  - <https://raw.githubusercontent.com/cran/randompack/HEAD/DESCRIPTION>
  - <https://raw.githubusercontent.com/cran/randompack/HEAD/src/Makevars.in>
  - <https://raw.githubusercontent.com/cran/randompack/HEAD/configure>
  - <https://raw.githubusercontent.com/cran/randompack/HEAD/src/randompack.c>
  - <https://raw.githubusercontent.com/cran/randompack/HEAD/src/x256pp_neon_scalar.inc>
  - https://cran.r-universe.dev/randompack (WebSearch snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/pedrobtz/zurand`) · [data/wave8/enrich/raw/github_com_pedrobtz_zurand.json](../../../data/wave8/enrich/raw/github_com_pedrobtz_zurand.json) (enrichment confidence 0.82)

</details>
