# fast_prng (cd-mcfarland modified ziggurat)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Header-only C modified-ziggurat normal and exponential samplers; reference code for the McFarland 2016 algorithm, faster than classic ziggurats.

| | |
|---|---|
| **Beats** | Doornik ziggurat normal and Marsaglia-Tsang ziggurat exponential (other ziggurat generators profiled in the repo); not std::normal_distribution or Boost |
| **Claimed result** | README example output: 'Mean execution time (per PRN): 7.987 (ns)' for 1e9 standard normal draws. The README page gives no baseline timing; benchmarks/ holds profile.c variants for Doornik normal and Marsaglia-Tsang/double Marsaglia exponential but no committed results file was found. |
| **Workload** | Mean time per generated standard normal (and exponential) variate over 1e9 draws, uniform source is SFMT-based MT19937.h. |
| **Metric** | throughput |
| **Hardware** | README run: not stated. benchmarks/profile_all.py default CPU string: Intel Core i7-3770K @ 3.50GHz (other CPUs commented out). |
| **Compiler and flags** | README: gcc -O2 -DNORMAL profile.c -lm. benchmarks/profile_all.py default config: gcc-4.8 -O2, 5 trials, median. |
| **Adoption** | 13 stars, 5 forks; algorithm ported to Apache Commons RNG (ZigguratSampler, whose JMH ZigguratSamplerPerformance benchmark compares it with the older Marsaglia-Tsang ZigguratNormalizedGaussianSampler), chosen per WebSearch snippets as the default for JDK 17 RandomGenerator nextGaussian/nextExponential, USGS BiF Fortran port, PyPI fast_prng |
| **Last commit** | 2025-05-21 |
| **Links** | [repository](https://github.com/cd-mcfarland/fast_prng) · [benchmark](https://github.com/cd-mcfarland/fast_prng) |

## Verdict

The only number in the repo is a README sample run: 7.987 ns per standard normal over 1e9 draws with gcc -O2, clock()-timed, CPU not stated and no baseline row; profile_all.py names gcc-4.8 -O2 on an i7-3770K, but its timings.csv is missing. Outside the repo, the paper's snippet reports median runtimes cut to 53% (normal) and 58% (exponential) of other ziggurats on pre-fix code, and an independent C port in pedrobtz/zurand PR #45 (merged 2026-09-27) measured its McFarland method at 1.08-1.25x the speed of its NumPy-table ziggurat on EPYC 7763/9V74, about 1.04-1.10x on Neoverse N2 and 1.02-1.08x on Apple M1.

## Use it when

- Monte Carlo or simulation code in C that needs very large numbers of N(0,1) or Exp(1) doubles from a single thread and can live with a process-global generator.
- As a reference to port: the algorithm already powers Apache Commons RNG ZigguratSampler, and the pedrobtz/zurand R package re-derived its tables, so the C here is the canonical starting point for a new port.
- When a classic ziggurat (Marsaglia-Tsang, Doornik) is your hot spot and you want the same exactness with a shorter fast path.
- x86-64 Linux/macOS builds with SSE2 where you control the compile flags.

## Skip it when

- Multithreaded code: the generator state (sfmt array, iRandS buffer, global Rand pointer) is process-global with no locking or per-thread instances.
- Reproducible experiments: mt_init() seeds only from getpid(), time(NULL) and getppid() and ignores repeat calls, and there is no public seed function.
- Non-x86 targets or MSVC: MT19937.h uses __m128i/_mm_set_epi64 (MMX __m64) unconditionally and stores 64-bit values in 'signed long', which is 32-bit on Windows; unistd.h is required.
- Code that needs other distributions, float output, or a generic C++ engine/distribution interface; Zest or EigenRand fit better there.
- The PyPI package: fast_prng 1.1.2 dates from 2015-06-10, before the 2021 correctness fixes, so pip installs the biased sampler.

## How it is fast

McFarland's modified ziggurat (J. Stat. Comput. Simul. 86(7), 2016): 252/253 layers are built entirely under the density, so about 98.8% of draws exit after one 64-bit uniform, one table lookup and one multiply, with no rejection test. The low 8 bits of that same uniform, which the float multiply discards anyway, pick the layer. Draws that miss go to Walker alias sampling over the overhang/tail areas, and precomputed triangle bounds (min_iE/max_iE) accept or reject most overhang points without calling exp(). The uniform source is a pointer into a pre-filled SFMT block buffer, so the fast path is a pointer increment.

## Compared with alternatives

Pick it over the miloyip/normaldist-benchmark and cauldron ziggurats when you want the McFarland layout (fewer rejection tests, exp() avoided on most overhang draws) as a C reference to port; pick Zest or EigenRand instead when you need a C++ distribution interface, more distributions, thread-local engines or SIMD batch output, and Randompack when you also need fast uniforms across languages.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond libm and POSIX unistd.h; bundled SFMT-derived MT19937.h (BSD) is required |
| **Minimum toolchain** | C99 compiler with SSE2 intrinsics (README builds with gcc -O2 ... -lm; profile_all.py targets gcc-4.8) |
| **Platforms** | x86-64 with SSE2, POSIX (Linux, macOS); Windows path partially stubbed but not workable as written |
| **Thread safety** | Not thread-safe: single global uniform buffer and Rand pointer shared by normal(), exponential() and the uniform helpers. |
| **Drop-in for the baseline** | partial — same output distribution as a ziggurat normal/exponential sampler, but a C free-function API on a fixed internal SFMT engine, not a replacement for the Doornik/Marsaglia code's engine hooks or for std::normal_distribution |

## Gotchas

- Two correctness bugs found by Alex Herbert were fixed only in Aug-Sep 2021 (PR #1: convex-overhang resampling reused X and flattened the bell curve within +/-0.25; PR #2: off-by-one inflection index in both samplers; a follow-up commit fixed '\~4% of sampled values in the 1st overhang'). The README says neither showed up in the first six moments, so the 2016 paper's timings ran on pre-fix code.
- The headers define non-static symbols (normal_setup, exponential_setup, global 'rand64_t \*Rand'), so including them in more than one translation unit causes duplicate-symbol link errors; keep them in one .c file and wrap them.
- Rand is a raw cursor into the uniform buffer: if you mix in the helper uniforms (rand_long, wide_uniform) you must follow the README rule to call MT_FLUSH() at least every two increments, or you read past the buffer.
- benchmarks/profile.c has '#pragma omp parallel for' around the timing loop; compiled with -fopenmp it races on the global state, so time only single-threaded builds.

## Known shortcomings

- Tier C: README 7.987 ns per normal with no baseline timing in the repo (timings.csv 404); the paper's 58%/53% runtime vs other ziggurats is snippet-only, and the paper timed code later fixed for two bugs (Alex Herbert). Notable through its Commons RNG port and JDK 17's nextGaussian. Last commit 2025-05-21, stale.
- PyPI fast_prng 1.1.2 (2015-06-10) predates the 2021 Herbert fixes (PR #1 convex-overhang bug that flattened the bell curve within +/-0.25, PR #2 off-by-one, a follow-up for about 4% of first-overhang values), so pip installs the biased sampler and the paper timings ran on pre-fix code. Global state, not thread-safe, x86 SSE2 only, seed only from pid/time/ppid; headers define non-static symbols (duplicate-symbol link errors across files); profile.c's omp pragma races on global state under -fopenmp.

## Caveats and trade-offs

The listed baselines (std::mt19937, PCG, xoshiro) are uniform generators, not normal samplers; the real comparison is against other ziggurat implementations (Doornik, Marsaglia-Tsang). No head-to-head against std::normal_distribution or Boost found. Paper abstract (J. Stat. Comput. Simul. 86(7), 2016; arXiv 1403.6870) says median runtimes for exponential and normal variates are reduced to 58% and 53% (range 41-93%); seen only in a WebSearch snippet (snippet only). README states Alex Herbert later fixed two bugs (fast rejection in the normal sampler, off-by-one overhang derivative indexing), so the paper's timings were measured on code later fixed for correctness bugs. Commons RNG reports its Java port beats its older ziggurat on JDK 8 and is no worse on later JDKs (WebSearch snippet; Java port, not this C code). The last commit (2025-05-21) only added a LICENSE file. timings.csv referenced by benchmarks/profile_all.py returns 404 at HEAD.

Header-only C (normal.h, exponential.h, shared.h) with its own SFMT-derived MT19937.h as the uniform source; also Python (pip fast_prng), MATLAB/Octave bindings. Table-based ziggurat with global generator state; the README describes bug fixes by a contributor (rejection sampling and overhang indexing off by one) that moment tests did not detect.

## Maintenance

Stale: the last code change was the Sept 2021 bug fixes and the 2025-05-21 commit only added an MIT LICENSE; the repo has 2 issues (both closed) and is small enough to vendor, but the 2015 PyPI release predates the fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README shows a single first-party run ('Mean execution time (per PRN): 7.987 (ns)' for 1e9 normals, gcc -O2, no CPU) with no baseline timing; benchmarks/profile_all.py names gcc-4.8 -O2 and an i7-3770K but reads a timings.csv that is missing (404), so no reproducible head-to-head is published. The peer-reviewed J. Stat. Comput. Simul. paper comparing against other ziggurats could not be opened (tandfonline/arXiv blocked), so not B.
- **Verifier notes:** README number confirmed verbatim; no baseline numbers in repo. Last commit 2025-05-21 is about 16 months old, so stale (record already said stale). Notable beyond its 13 stars through the Commons RNG and JDK 17 adoption.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; algorithm only, not this code: pedrobtz/zurand PR #45 (merged 2026-09-27) ports the McFarland method and measures 1.08-1.25x over its NumPy-table ziggurat on EPYC 7763/9V74, 1.04-1.10x on Neoverse N2, 1.02-1.08x on M1
- **Pages the verifier opened:**
  - <https://github.com/cd-mcfarland/fast_prng>
  - <https://github.com/cd-mcfarland/fast_prng/commits>
  - <https://raw.githubusercontent.com/cd-mcfarland/fast_prng/HEAD/README.md>
  - <https://raw.githubusercontent.com/cd-mcfarland/fast_prng/HEAD/benchmarks/profile_all.py>
  - <https://raw.githubusercontent.com/cd-mcfarland/fast_prng/HEAD/benchmarks/timings.csv>
  - <https://raw.githubusercontent.com/cd-mcfarland/fast_prng/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/cd-mcfarland/fast_prng>
  - <https://raw.githubusercontent.com/cd-mcfarland/fast_prng/HEAD/README.md>
  - <https://raw.githubusercontent.com/cd-mcfarland/fast_prng/HEAD/normal.h>
  - <https://raw.githubusercontent.com/cd-mcfarland/fast_prng/HEAD/exponential.h>
  - <https://raw.githubusercontent.com/cd-mcfarland/fast_prng/HEAD/shared.h>
  - <https://raw.githubusercontent.com/cd-mcfarland/fast_prng/HEAD/MT19937.h>
  - <https://raw.githubusercontent.com/cd-mcfarland/fast_prng/HEAD/benchmarks/profile.c>
  - <https://github.com/cd-mcfarland/fast_prng/tree/master/benchmarks>
  - <https://github.com/cd-mcfarland/fast_prng/commits>
  - <https://github.com/cd-mcfarland/fast_prng/issues?q=is%3Aissue>
  - <https://github.com/cd-mcfarland/fast_prng/pull/1>
  - <https://github.com/cd-mcfarland/fast_prng/pull/2>
  - <https://pypi.org/pypi/fast_prng/json>
  - <https://github.com/pedrobtz/zurand>
  - <https://github.com/pedrobtz/zurand/pull/45>
  - <https://github.com/pedrobtz/zurand/issues/46>
  - WebSearch snippet: Apache Commons RNG ZigguratSampler docs (commons.apache.org not opened)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/cd-mcfarland/fast_prng`) · [data/wave8/enrich/raw/github_com_cd_mcfarland_fast_prng.json](../../../data/wave8/enrich/raw/github_com_cd_mcfarland_fast_prng.json) (enrichment confidence 0.75)

</details>
