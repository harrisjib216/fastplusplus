# zigg (lightweight Ziggurat normal, exponential and uniform generators with a C/C++ interface)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (R package with C/C++-callable header)` · `GPL-2.0-or-later` · 🟢 active

> Small GPL C++ header (KISS + Marsaglia-Tsang Ziggurat) for standard normal, exponential, uniform draws; 4.7-7.4x faster than base R.

| | |
|---|---|
| **Beats** | R's built-in RNG (rnorm, rexp, runif; base R default Mersenne Twister with inversion for normals) |
| **Claimed result** | README: speed gains of zigg relative to base R 'on the order of 7.4, 5.2, and 4.7 for the normal, exponential, and uniform' generators (for the author's example, on his machine). |
| **Workload** | inst/example/timings.R uses microbenchmark to time zrnorm(N), zrexp(N) and zrunif(N) against base R rnorm(N), rexp(N) and runif(N) with N = 1e6 draws per call, and plots the timing distributions; the README chart comes from this script. |
| **Metric** | throughput |
| **Adoption** | 8 stars; on CRAN |
| **Last commit** | 2026-03-25 |
| **Links** | [repository](https://github.com/eddelbuettel/zigg) · [benchmark](https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/README.md) |

## Verdict

inst/example/timings.R uses microbenchmark to time zrnorm/zrexp/zrunif against base R rnorm/rexp/runif at N = 1e6 draws per call. The README and DESCRIPTION report 7.4x, 5.2x and 4.7x 'on our machine', with no CPU, compiler, flags or R version. The baseline is R's built-in generators, not std:: &lt;random&gt;.

## Use it when

- R code where drawing millions of standard normals dominates run time: the author measured 7.4x over rnorm at 1e6 draws per call.
- Native code in another R package that needs a fast N(0,1) generator without Rcpp, through R_GetCCallable or the header (four demo packages show the patterns).
- Standalone C++11 code that wants a tiny, dependency-free Ziggurat normal generator and can accept GPL (&gt;= 2) and a 32-bit KISS core.
- Exploratory simulations with modest statistical demands, which is how the author frames it.

## Skip it when

- Exponential variates, unless you patch the table bug described under gotchas: as shipped, zrexp()/rexp() put about 8.7x too much mass beyond x = 7.697.
- Results that must survive statistical scrutiny or match R's RNG streams: DESCRIPTION warns of 'potentially lesser quality and shorter period', the README recommends staying with base R when in doubt, and set.seed() does not control it (it has its own zsetseed()).
- Proprietary or permissively licensed code: the header is GPL (&gt;= 2).
- Concurrent use: the R entry points share one static zigg::Ziggurat, and the object keeps scratch state (hz, iz, jz) in members.
- Non-standard parameters or other distributions: there are no mean/sd/rate/min/max arguments, so you scale the output yourself; use Zest or dqrng for more distributions.

## How it is fast

It implements Marsaglia and Tsang's Ziggurat with the Leong et al. (2005) correction: a 128-strip table for the normal and a 256-strip table for the exponential, built once in the constructor. One 32-bit KISS draw (MWC xor CONG, plus SHR3) supplies both the strip index (low bits) and the candidate, so most draws cost one integer compare and one multiply; only strip edges and the tail call exp or log. Base R instead runs the Mersenne Twister and, for normals, inversion per draw, and runi() is a single scaled 32-bit integer.

## Compared with alternatives

In R, dqrng reports a similar 7.6x on rnorm with xoshiro256++/PCG64 generators. Pick zigg only for its tiny zero-dependency C-callable interface. In C++, Zest (more distributions, any 32/64-bit URBG) or cxx-ziggurat and normaldist-benchmark pair the Ziggurat with a modern URBG; pick zigg only for a self-contained KISS + Ziggurat normal generator.

## Integration

| | |
|---|---|
| **Form** | header-only (inst/include/zigg/header) or R package (CRAN) |
| **Dependencies** | none for the header (C++ standard library only); R for the package |
| **Minimum toolchain** | C++11 (&lt;chrono&gt;, &lt;cstdint&gt;, brace-initialized std::vector) |
| **Platforms** | any; portable 32-bit integer arithmetic, no SIMD |
| **Thread safety** | Not documented. Generator state and per-call scratch (hz, iz, jz) live in the object and the R functions share one static instance, so use one object per thread from C++ and do not call the R functions concurrently. |
| **Drop-in for the baseline** | partial — zrnorm(n)/zrexp(n)/zrunif(n) replace rnorm(n)/rexp(n)/runif(n) only at default parameters, are seeded by zsetseed() rather than set.seed(), and produce a different stream |

## Gotchas

- Correctness bug in the exponential table setup: 'ke[0] = (uint32_t) (de/q)\*m2;' casts 0.885 to 0 before multiplying, so ke[0] = 0 instead of about 3.80e9 and every base-strip draw (1 in 256) goes to the tail sampler. A Python port of the header (1e6 draws) gave P(X &gt; 7.697) = 0.00394 and mean 1.019, against 0.00045 and 1 for exact Exp(1); with the cast fixed it gave 0.00041 and 1.001. The same line is in RcppZiggurat's Ziggurat.h.
- The constructor ignores its seed argument: unless ZIGG_USE_ORIGINAL_FIXED_INITIALIZATION is defined, it overwrites the seed with the current time in milliseconds, so call setSeed() after construction for reproducible runs. setSeed() only XORs the seed into the SHR3 word and resets the other three words to constants, which allows at most 2^32 seeded streams.
- Draws have 32-bit resolution: runi() is 0.5 + int32(KISS) \* 0.2328306e-09, and rnorm() uses one 32-bit draw for both the 7-bit strip index and the value.
- The header #defines znew, wnew, MWC, SHR3 and CONG and #undefs them at the end, which clobbers any same-named macros in the including code.

## Known shortcomings

- Author warns the generators have lower quality and a shorter period than base R's; baseline is R; script path is inst/example/timings.R.
- Correctness bug in the exponential generator: 'ke[0] = (uint32_t) (de/q)\*m2;' casts 0.885 to 0 before multiplying, so ke[0]=0 and every base-strip draw goes to the tail; an independent port with 1e6 draws gave P(X&gt;7.697)=0.00394 vs exact 0.00045, mean 1.019. The same line is in RcppZiggurat's Ziggurat.h. The 5.2x exponential figure was therefore timed on a wrong distribution (normal and uniform unaffected). Constructor ignores its seed argument (uses the clock unless a macro is set), so call setSeed(). Header has no R dependency, usable from plain C++11.

## Caveats and trade-offs

The numbers sit in a chart image (hosted on eddelbuettel.github.io, not opened) generated by inst/example/timings.R; only the three ratios are given as text, in the README and the DESCRIPTION ('on our machine'), with no CPU, compiler, flags or R version stated. Draws are bulk (1e6 per call). DESCRIPTION warns the generators are 'of potentially lesser quality and shorter period' than base R's, and the README recommends sticking with R's default generators when in doubt, since RNG time is usually a small share of total run time. Baseline is R's RNG, not std::mt19937. The C/C++ interface is meant for use from other R packages' native code (four demo packages: directC, directCpp, headerCpp, headerRcpp), not as a standalone C++ library. The older sibling RcppZiggurat (GPL-2.0-or-later) has a vignette with a speed table that was not opened. [retier] The exponential generator has a cast bug (ke[0]=0) that sends every base-strip draw to the tail, so its 5.2x figure was timed on a wrong distribution; the normal (7.4x) and uniform (4.7x) figures are unaffected. RcppZiggurat carries the same line.

GPL (&gt;= 2); C(++)-callable header-only interface demonstrated by four client packages; older, simpler Ziggurat generator with a shorter period than R's default, which the README itself says may suit only some studies.

## Maintenance

Recent commits only touch CI; the last package change is release 0.0.2 (2025-02-07, on CRAN, GPL &gt;= 2). The header is small enough to vendor into GPL-compatible code, after fixing the ke[0] line.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README ratios (7.4, 5.2, 4.7 vs base R) from a public script (inst/example/timings.R, microbenchmark over 1e6-draw calls), with no CPU, compiler, flags or R version stated, so C.
- **Verifier notes:** The ratios match the README and DESCRIPTION. The record's script path 'example/timings.R' is really inst/example/timings.R. Metadata checked: GPL (&gt;= 2) in DESCRIPTION, 8 stars, last commit 2026-03-25 (active), DESCRIPTION version 0.0.2 dated 2025-02-07.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/README.md>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/master/inst/example/timings.R>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/master/DESCRIPTION>
  - <https://github.com/eddelbuettel/zigg>
  - <https://github.com/eddelbuettel/zigg/commits>
- **Sources the enricher read:**
  - <https://github.com/eddelbuettel/zigg>
  - <https://github.com/eddelbuettel/zigg/tree/master/src>
  - <https://github.com/eddelbuettel/zigg/tree/master/inst/include>
  - <https://github.com/eddelbuettel/zigg/tree/master/tests>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/README.md>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/DESCRIPTION>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/NAMESPACE>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/inst/example/timings.R>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/inst/include/zigg/header>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/src/ziggurat.cpp>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/src/init.c>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/src/Makevars>
  - <https://raw.githubusercontent.com/eddelbuettel/zigg/HEAD/tests/zigg.R>
  - <https://github.com/eddelbuettel/rcppziggurat/tree/master/inst/include>
  - <https://raw.githubusercontent.com/eddelbuettel/rcppziggurat/HEAD/inst/include/Ziggurat.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/eddelbuettel/zigg`) · [data/wave8/enrich/raw/github_com_eddelbuettel_zigg.json](../../../data/wave8/enrich/raw/github_com_eddelbuettel_zigg.json) (enrichment confidence 0.75)

</details>
