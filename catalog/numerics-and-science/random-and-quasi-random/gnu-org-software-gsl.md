# GSL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0-or-later` · ⚪ unknown

> GNU's C numerics library; its Marsaglia-Tsang gamma sampler outran Boost.Random's Knuth-method gamma_distribution about 4x.

| | |
|---|---|
| **Beats** | Boost.Random gamma_distribution |
| **Claimed result** | Boost trac ticket #6135 (Boost.Random patch proposal by Jan Drugowitsch, November 2011; snippet only): generating 100 million gamma variates, GSL about 22.3 million samples/s against Boost.Random gamma_distribution about 5.4 million (Boost using Knuth's method, GSL Marsaglia and Tsang 2000), about 4.1x (derived from page data); with the ticket's patch Boost reached about 14.5 million samples/s against GSL about 22.7 million in the same run, about 1.6x (derived from page data), the remaining gap attributed to GSL's Ziggurat normals versus Box-Muller. |
| **Workload** | Gamma-variate generation in samples per second, GSL against Boost.Random's gamma_distribution, reported in Boost trac ticket 6135 before and after a patch to Boost's algorithm. |
| **Metric** | throughput |
| **Adoption** | GNU package; 639 stars on github.com/ampl/gsl, a CMake/AMPL-bindings copy of the latest stable release |
| **Links** | [repository](https://www.gnu.org/software/gsl/) · [benchmark](https://trac.cpp.al/trac10/ticket/6135) |

## Verdict

A 2011 Boost trac ticket (#6135, search snippets only) timed 100 million gamma draws: GSL about 22.3 million/s against Boost.Random gamma_distribution's 5.4 million/s (about 4.1x), and about 1.6x after the reporter's Marsaglia-Tsang patch. The compiler, flags, CPU, Boost version, generator and shape parameter are unknown. The source confirms the algorithms: Boost develop still uses Knuth's method while GSL uses Marsaglia-Tsang with ziggurat normals.

## Use it when

- C or C++ code that samples many gamma (or chi-squared, beta, Dirichlet) variates and currently uses Boost.Random's gamma_distribution, which still uses Knuth's tan()-based rejection on Boost develop.
- You want one stable C API covering many distributions and the rest of a numerics stack (special functions, CDFs and inverse CDFs, integration), and GPL-3.0 linking is acceptable.
- You need reproducible, named generators (mt19937, taus, ranlxd1/2) selectable at run time through GSL_RNG_TYPE and GSL_RNG_SEED.
- Multi-threaded Monte Carlo with one gsl_rng per thread: the docs say functions keep no static state.

## Skip it when

- You already use libstdc++'s std::gamma_distribution: it also uses Marsaglia-Tsang (with polar-method normals), so GSL's only possible edge there is ziggurat normals, and no measurement of that was found.
- Bulk throughput matters: every draw goes through a function pointer (gsl_rng_get calls r-&gt;type-&gt;get) and nothing is vectorized; SIMD samplers such as EigenRand or Zest's ziggurat are built for speed.
- Proprietary or permissively licensed code: GPL-3.0-or-later, so linking makes the combined work GPL.
- Tiny shapes (a well below 1): the u^(1/a) boost underflows to exactly 0.0 for a large share of draws (with a = 0.001, any u below about 0.47), outside the distribution's support; this is derived from the code, not measured.
- You need modern evidence: the only speed number is a 2011 Boost bug-ticket timing seen through search snippets.

## How it is fast

gsl_ran_gamma uses the Marsaglia-Tsang (2000) squeeze-and-reject method: one normal and one uniform per attempt, a cheap polynomial squeeze that usually avoids the log, and shape a &lt; 1 handled by boosting to a+1 and multiplying by u^(1/a). Its normals come from gsl_ran_gaussian_ziggurat, a 128-strip ziggurat that takes the strip index, sign and a 24-bit position from a single 32-bit draw for full-range generators. Boost.Random's gamma_distribution instead uses Knuth's Cauchy-proposal rejection for a &gt; 1, which costs tan, exp, log and two square roots per attempt.

## Compared with alternatives

Pick GSL over Zest or EigenRand when you want a plain-C, GPL-compatible library that covers dozens of distributions plus CDFs and inverse CDFs and you can live with scalar speed. Zest (ziggurat gamma, about 2.5x over the STL) and EigenRand (SIMD) target raw sampling throughput, and Randompack reports about 15x over C++ std &lt;random&gt; on uniform draws.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (autotools; ampl/gsl adds a CMake build) |
| **Dependencies** | none; ships its own reference CBLAS (libgslcblas), which can be swapped for an optimized CBLAS at link time; ampl/gsl's default CMake build also wants the AMPL ASL submodule unless -DNO_AMPL_BINDINGS=1 |
| **Minimum toolchain** | C compiler (autotools); ampl/gsl CMake needs CMake 3.11+ |
| **Platforms** | any (portable C) |
| **Thread safety** | Functions keep no static variables; use one gsl_rng (and workspace) per thread. A few globals (error handler, range checking, gsl_rng_default) must be set once at startup (doc/usage.rst). |
| **Drop-in for the baseline** | no |

## Gotchas

- The default error handler prints the message and calls abort() (err/error.c); call gsl_set_error_handler_off() or install your own handler in library code.
- gsl_ran_gamma does no parameter checking (source comment 'assume a &gt; 0'): a &lt;= 0 returns garbage or 0 with no error.
- Gaussian draws from gsl_ran_gaussian_ziggurat carry only 24 bits of position within a strip, and speed depends on the generator's range: below 2^32 it takes two draws, below 2^24 it calls gsl_rng_uniform_int twice.
- gsl_ran_gamma_knuth (the old default before GSL 1.9) is still in the library; make sure you call gsl_ran_gamma (alias gsl_ran_gamma_mt) to get the fast method.

## Known shortcomings

- Numbers known only from a search summary of Boost trac ticket #6135 (2011; trac.cpp.al, svn.boost.org, lists.boost.org ENOTFOUND): gamma sampling 22.3 vs 5.4 Msamples/s, 22.7 vs 14.5 after the patch. Boost develop still uses Knuth's gamma method (record wrongly said fixed); libstdc++ std::gamma_distribution already uses Marsaglia-Tsang, so the win is over Boost only. GPL-3.0-or-later; upstream last commit unknown (gnu.org blocked).
- Enricher: Boost develop's gamma sampler is still Knuth's tan() rejection while GSL uses Marsaglia-Tsang with ziggurat normals, but the ticket's explanation of the remaining gap is obsolete (Boost normal_distribution is now ziggurat); shape, generator, compiler and CPU of the 2011 run are unknown and Boost takes a different path for a&lt;1, so the 4.1x may hold for a&gt;1 only; libstdc++ std::gamma_distribution is already Marsaglia-Tsang, so no edge over std was measured. Default error handler aborts; gsl_ran_gamma has no parameter check; for small a, u^(1/a) underflows to 0.0 on a large share of draws (about u&lt;0.47 at a=0.001, code-derived); ziggurat has only a 24-bit position within a strip; function-pointer dispatch per draw.

## Caveats and trade-offs

SNIPPET ONLY: the figures come from a WebSearch summary of Boost trac ticket #6135; trac.cpp.al, svn.boost.org and both Boost mailing-list archives fail with getaddrinfo ENOTFOUND here, so the ticket text, compiler, flags, hardware and Boost version were not seen (the ticket is from November 2011). The patch was apparently never merged: Boost.Random's current gamma_distribution.hpp (develop branch) still says 'The algorithm is taken from Knuth' and uses tan()-based rejection for alpha &gt; 1, so the 2011 gap may still apply to current Boost, but no current measurement was found. GSL's randist/gamma.c uses Marsaglia-Tsang with gsl_ran_gaussian_ziggurat. libstdc++'s std::gamma_distribution already uses Marsaglia-Tsang (bits/random.tcc) with polar-method normals, so GSL's edge over the C++ standard library is unmeasured and would come only from Ziggurat versus polar normals. Other snippets do not show GSL winning: a 2012 Rcpp Gallery post timed GSL's Mersenne Twister Gaussian draws slower than R's rnorm and Armadillo; S. Gerlach's PRNG slides reportedly rate GSL fastest for Gaussian sampling but no numbers were visible. No evidence was found for GSL beating a BLAS/LAPACK or FFT incumbent (the lead's guessed category fft is wrong). GSL is GPL-3.0-or-later (copyleft; linking GSL makes the combined work GPL). repo_url is the gnu.org project page (www.gnu.org ENOTFOUND here); the GitHub copy github.com/ampl/gsl (GPL-3.0, 639 stars, 288 commits, CMake build and AMPL bindings) carries the GSL 2.8 NEWS and was last committed 2026-05-19, which reflects AMPL's packaging, not upstream GSL.

Plain C library with dozens of generators (gsl_rng) and distributions; global error-handler and abort-on-error defaults; GPL (not LGPL), which restricts use in proprietary code; not a performance-tuned library in its linear algebra (reference-style CBLAS).

## Maintenance

GPL-3.0-or-later, GSL 2.8 (configure.ac AC_INIT 2.8) is the current release mirrored by ampl/gsl (639 stars, CMake and AMPL bindings, actively repackaged); upstream savannah git and gnu.org were unreachable, so the upstream commit date is unknown. The 2011 ticket's explanation of the remaining gap (Boost's Box-Muller normals) is obsolete, because Boost's normal_distribution now uses a ziggurat; the 4.1x figure for unpatched Boost still matches the current code path for a &gt; 1.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Numbers known only from a search summary of Boost trac ticket #6135 (trac.cpp.al, svn.boost.org, lists.boost.org and listarchives.boost.org all failed with ENOTFOUND); a user's bug-report timing with no compiler, flags or CPU is at best C, and snippet-only evidence stays at C.
- **Verifier notes:** Snippet confirms the ticket numbers (GSL 22.3 vs Boost 5.4 Msamples/s; after patch GSL 22.7 vs Boost 14.5), so C stays, but nothing was opened first-hand and there is no compiler, flags, CPU or Boost version. The record's caveat that Boost's gamma sampler was 'since fixed' is wrong: Boost develop still uses Knuth's method, while libstdc++'s std::gamma_distribution already uses Marsaglia-Tsang, so GSL's win is over Boost only. Shortcomings: snippet-only 2011 evidence, single distribution, GPL copyleft, upstream last_commit unknown.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-175 (wave 8); enricher w8 pair-044
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/boostorg/random/develop/include/boost/random/gamma_distribution.hpp>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/randist/gamma.c>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/COPYING>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/NEWS>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/random.tcc>
  - <https://github.com/ampl/gsl>
  - <https://github.com/ampl/gsl/commits>
- **Sources the enricher read:**
  - <https://github.com/ampl/gsl>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/README>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/NEWS>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/randist/gamma.c>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/randist/gausszig.c>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/randist/gauss.c>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/rng/gsl_rng.h>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/err/error.c>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/doc/usage.rst>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/doc/rng.rst>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/doc/randist.rst>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ampl/gsl/HEAD/BUGS>
  - <https://raw.githubusercontent.com/boostorg/random/develop/include/boost/random/gamma_distribution.hpp>
  - <https://raw.githubusercontent.com/boostorg/random/develop/include/boost/random/normal_distribution.hpp>
  - <https://raw.githubusercontent.com/boostorg/random/develop/include/boost/random/exponential_distribution.hpp>
  - <https://github.com/boostorg/random/issues?q=gamma>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/random.tcc>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://gnu.org/software/gsl`) · [data/wave8/enrich/raw/gnu_org_software_gsl.json](../../../data/wave8/enrich/raw/gnu_org_software_gsl.json) (enrichment confidence 0.35)

</details>
