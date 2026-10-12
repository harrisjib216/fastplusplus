# miranda (coolbutuseless/miranda, R package with C PRNGs: romu trio, xoshiro256+, lehmer64, splitmix64)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `R` · `MIT` · 🔴 abandoned

> Tiny R package exposing RomuTrio, xoshiro256+, lehmer64 and SplitMix64 as runif-style functions, about 20x faster than R's runif().

| | |
|---|---|
| **Beats** | R base runif() |
| **Claimed result** | README text: up to 20x faster than R's built-in PRNGs; 'At their best, these PRNGs are about 20x faster than runif()'. Chart (log-scale beeswarm, values read approximately from the image): runif(N) about 30 ms for 1e6 doubles vs about 1.5 ms romutrio, 1.7 ms xoshiro256p, 1.8 ms lehmer64 and 2.5 ms splitmix64 (roughly 12x-20x, derived from page data). |
| **Workload** | bench::mark of generating 1 million uniform random numbers with each package function versus runif(N). |
| **Metric** | throughput |
| **Adoption** | 22 stars |
| **Last commit** | 2022-05-10 |
| **Links** | [repository](https://github.com/coolbutuseless/miranda) · [benchmark](https://github.com/coolbutuseless/miranda) |

## Verdict

README bench::mark of 1e6 uniform doubles: R's runif(N) (default Mersenne-Twister) sits at about 30 ms, while non-GC iterations of runif_romutrio and runif_xoshiro256p cluster near 1.5 ms, lehmer64 near 1.7 ms and splitmix64 near 2.5 ms (about 12x-20x, values read off a log-axis beeswarm, derived from page data); iterations that triggered garbage collection took 5-13 ms. No CPU, R version, compiler or flags are given, and the gap measures R's runif call path against an inlined C loop, not generator against generator in C++.

## Use it when

- R code that draws millions of plain U(min, max) doubles in a hot loop and does not need set.seed() reproducibility through R's own RNG machinery.
- You need to save and restore generator state exactly (get_state_\*/set_state_\* as raw vectors) or skip ahead 2^128/2^192 steps with jump_xoshiro256p/long_jump_xoshiro256p.
- You want a readable reference of how to bind a small C PRNG to R's .Call interface with state save/restore.
- Linux or macOS 64-bit R builds, where all four generators compile (lehmer64 needs unsigned __int128).

## Skip it when

- C++ projects: the files add only R glue (R.h/Rinternals.h, SEXP returns, global state); take the generators from their reference sources or a catalogued C++ library instead.
- You need normals, integers, sampling or other distributions: only uniform doubles are provided (dqrng covers rnorm and sample.int).
- Windows R builds that need lehmer64: it is compiled out under _WIN32 and runif_lehmer64 prints a message and returns a single 0 instead of n values.
- Production or packaged work: lifecycle badge says experimental, 11 commits, last code change September 2020, install is from GitHub only per the README, and issue #1 (Windows i386 build failure) has no maintainer reply.
- Parallel or multi-stream use: each generator has exactly one global stream per process, with no per-object state.

## How it is fast

Each runif_\* call runs one tight C loop that steps the generator inline and converts the top 53 bits to a double with (x &gt;&gt; 11) \* 0x1.0p-53, writing straight into a freshly allocated REALSXP. The generators themselves are cheap: RomuTrio is a multiply plus two subtract-rotates, xoshiro256+ is xor/shift/rotate, lehmer64 is one 128-bit multiply (unsigned __int128), SplitMix64 is an add plus two xorshift-multiplies. The speedup is mostly avoided per-value overhead in R's runif path rather than a novel generator technique.

## Compared with alternatives

Pick dqrng over this for almost any R use: it is a header-only C++ library and R package with xoshiro256++/PCG64, fast rnorm and sample.int, and active maintenance. miranda is only the better pick if you specifically want RomuTrio or lehmer64 behind a runif-like call; for C++ code use the reference generators directly (Romu, testingRNG's lehmer64) or a SIMD sibling such as simdrng.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | R (built via R CMD INSTALL / remotes::install_github); testthat suggested for tests |
| **Minimum toolchain** | C compiler accepted by R's build tools; lehmer64 needs unsigned __int128 (64-bit GCC or Clang). R version minimum not documented. |
| **Platforms** | Any 64-bit R build for xoshiro256+, RomuTrio and SplitMix64; lehmer64 disabled on Windows |
| **Thread safety** | Not thread-safe: each generator keeps its state in a file-scope static (or global) variable shared by every caller in the process. |
| **Drop-in for the baseline** | partial — runif_\*(n, min, max) mirrors runif's signature, but min/max are read as scalars (only the first element is used, unlike runif's recycling), seeding goes through set_seed_\* rather than set.seed(), and the streams differ from Mersenne-Twister. |

## Gotchas

- Licensing is mixed despite the package's MIT label: romutrio.c carries Mark Overton's Apache-2.0 header and xoshiro256p.c/splitmix64.c carry Blackman/Vigna CC0 headers; vendoring romutrio.c brings Apache-2.0 obligations.
- Generators are seeded once in .onLoad from stats::runif, so results are reproducible only if you call the package's set_seed_\* (or set.seed() before the package loads); forked workers such as parallel::mclapply would start from copies of the same state unless reseeded or jumped (inferred from the global state in the C code).
- The double conversion maps 53 bits to [0, 1), so an exact 0 (or min) is a possible output.
- romutrio.c does arithmetic on void\* when copying state (pbytes + 8), a GNU extension; porting it to strict C or C++ needs a cast to unsigned char\*.

## Known shortcomings

- Tier C: a README chart only (runif about 30 ms vs romutrio about 1.5 ms, roughly 20x, read by eye), no CPU or flags. Last commit 2022-05-10, abandoned.
- R glue only, with no value over the upstream generator sources for C++. romutrio.c carries an Apache-2.0 header, not MIT. lehmer64 is compiled out on Windows (runif_lehmer64 returns a single 0 there); one global state per generator, not thread-safe; issue #1 (Windows build failure) has no reply. On a chart re-read, GC iterations take 5-13 ms, so the 20x holds only on non-GC runs.

## Caveats and trade-offs

R package, usable from C++ only by reusing its small C sources (MIT). No CPU, R version, compiler or flags stated; the chart is an image and the millisecond values above are approximate readings off a log axis. Both sides are vectorized R calls that allocate a 1e6-double result, so the gap reflects R's runif path (Mersenne-Twister through R's RNG dispatch) versus inlined small-state generators, not raw generator speed against std::mt19937 or PCG. Lifecycle badge: experimental.

R package with C source in src/, lifecycle marked experimental; includes jump-ahead for xoshiro256+; romu trio has a probabilistic period and xoshiro256+ has weak low bits; all four generators are listed as passing or having no systematic failures in BigCrush.

## Maintenance

Abandoned since 2022 (last code change September 2020, then a README typo fix); MIT package licence with Apache-2.0 and CC0 file headers, and the C cores are small enough to vendor, but they offer nothing over the upstream reference sources for C++ users.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README benchmarks the package generators against R's runif(N) with bench::mark code shown in the README and a beeswarm timing chart (README-bench-1.png); the text says 'about 20x faster' at best. No CPU, compiler, flags or R version, so first-party C.
- **Verifier notes:** Stars 22, forks 1, 11 commits, last commit 2022-05-10 ('fix typo'), abandoned; MIT confirmed (DESCRIPTION 'MIT + file LICENSE', GitHub sidebar MIT). Chart image read directly; it supports the 20x text claim for romutrio.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/coolbutuseless/miranda>
  - <https://github.com/coolbutuseless/miranda/commits>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/README.md>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/README.Rmd>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/man/figures/README-bench-1.png>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/DESCRIPTION>
- **Sources the enricher read:**
  - <https://github.com/coolbutuseless/miranda>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/README.md>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/DESCRIPTION>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/NAMESPACE>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/LICENSE>
  - <https://github.com/coolbutuseless/miranda/tree/master/src>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/src/init.c>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/src/lehmer64.c>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/src/romutrio.c>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/src/splitmix64.c>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/src/splitmix64.h>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/src/xoshiro256p.c>
  - <https://github.com/coolbutuseless/miranda/tree/master/R>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/R/rand-xoshiro256p.R>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/R/rand-lehmer64.R>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/R/zzz.R>
  - <https://raw.githubusercontent.com/coolbutuseless/miranda/HEAD/man/figures/README-bench-1.png>
  - <https://github.com/coolbutuseless/miranda/issues>
  - <https://github.com/coolbutuseless/miranda/issues/1>
  - <https://github.com/coolbutuseless/miranda/commits/master>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/coolbutuseless/miranda`) · [data/wave8/enrich/raw/github_com_coolbutuseless_miranda.json](../../../data/wave8/enrich/raw/github_com_coolbutuseless_miranda.json) (enrichment confidence 0.8)

</details>
