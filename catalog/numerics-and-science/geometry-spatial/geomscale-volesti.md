# volesti

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `LGPL-3.0-or-later` · 🟢 active

> Randomised C++ volume estimation and sampling for high-dimensional convex polytopes; orders of magnitude faster than exact VINCI above about 10 dimensions.

| | |
|---|---|
| **Beats** | VINCI 1.0.5 (exact polytope volume; package birkhoff for the Birkhoff polytopes) and Cousins and Vempala's Matlab volume implementation (reference [13] in the text; the Table 7 caption labels it [12], their SODA 2014 Gaussian-volume paper) |
| **Claimed result** | Abstract: 'Our publicly available code is significantly faster than exact computation and more accurate than existing approximation methods.' Table 1, VolEsti vs exact seconds: cross-10 1.58 vs 388.50 (about 250x), cross-11 5.19 vs 6141.40 (about 1180x), rv-8-12 0.59 vs 261.37, rv-10-13 1.24 vs 59.50, B8 192.97 vs 1920.00, cube-20 4.62 vs swap (exact ran out of memory); B9 exact 8 days vs 499.56 s; exact methods cannot handle d above 15. Table 7 vs Cousins-Vempala Matlab (seconds): cube-20 4.62 vs 21.48, cube-30 17.96 vs 49.24, cube-40 50.72 vs 88.09 (ratios derived from page data: 4.6x, 2.7x, 1.7x), with 4 to 100 times smaller error on cube-d for d above 70. |
| **Workload** | Wall-clock time (mean of 100 runs) to approximate H-polytope volume with error about 1% (eps = 1) for cubes, cross polytopes, random polytopes, simplices and Birkhoff polytopes B8 to B15, against exact VINCI/birkhoff computation and against the Cousins-Vempala Matlab code (10 runs). |
| **Metric** | latency |
| **Hardware** | Intel Core i5-2400 3.1GHz, 6MB L2 cache, 8GB RAM, 64-bit Debian GNU/Linux |
| **Compiler and flags** | Not stated (C++ about 2.5K lines on CGAL's d-dimensional kernel, CGAL LP solver with GMP, CGAL approximate minimum ellipsoid, Eigen, Boost mt19937) |
| **Adoption** | 189 stars; CRAN package volesti |
| **Last commit** | 2026-06-29 |
| **Links** | [repository](https://github.com/GeomScale/volesti) · [benchmark](https://raw.githubusercontent.com/vissarion/vissarion.github.io/master/publications/EF_socg14.pdf) |

## Verdict

In the SoCG 2014 paper (Emiris and Fisikopoulos) the precursor C++ code (sourceforge randgeom, CGAL d-dimensional kernel with a GMP LP solver, Eigen, Boost mt19937; compiler and flags not stated) on an Intel Core i5-2400 took, at eps = 1 and about 1% error, 1.58 s vs 388.50 s for exact VINCI on cross-10 and 5.19 s vs 6141.40 s on cross-11, handled cube-20 to cube-100 where VINCI ran out of memory, and beat the Cousins-Vempala Matlab code up to cube-70 (cube-20 4.62 s vs 21.48 s) while losing from cube-80 up. These are algorithmic speedups of an approximate estimator over exact computation, measured on code that predates today's Eigen and lp_solve rewrite.

## Use it when

- You need the volume of an H-polytope in roughly 12 to 100 dimensions, where exact codes (VINCI, qhull, birkhoff) run out of memory or take days.
- About 1% relative error is acceptable, e.g. probability estimates, portfolio or financial-crisis indicators, metabolic flux-space analysis.
- You need uniform or Gaussian samples from a convex polytope as well as its volume (same random-walk machinery).
- You already work in R (CRAN volesti/Rvolesti) or can use Eigen and Boost in a C++17 build.

## Skip it when

- Low dimensions (up to about 10) or simplices: exact VINCI answered in 0.01 to 0.40 s where VolEsti took 0.4 to 1.4 s on cubes, and simplices took VolEsti up to 919 s vs 0.02 s exact in the paper.
- You need an exact or certified volume, or bit-reproducible output: the estimator is randomised and the default RNG is seeded from the system clock.
- Very high dimensions at tight error with the sequence-of-balls method: in the paper the Cousins-Vempala Gaussian-cooling Matlab code was already faster from cube-80 up (cube-100 884 s vs 1285 s); use volesti's own cooling_gaussians or cooling_balls instead.
- Degenerate or lower-dimensional polytopes: open issues #463 (max_inscribed_ball instability), #394 and #396 (ball walks can silently stagnate) and #325 (inscribed-ellipsoid segfault on a 2-D polytope).
- LGPL-3.0 is a problem for your distribution, or you need a macOS/ARM clang build (issue #295, compile errors, open since 2024).

## How it is fast

Multiphase Monte Carlo: the 'sequence of balls' method samples the polytope intersected with concentric balls between the Chebyshev ball and an enclosing ball, and multiplies the estimated volume ratios, using about 400 eps^-2 d log d points per phase. Points come from Coordinate-Directions Hit-and-Run, whose boundary oracle is updated incrementally to O(m) amortised work per step instead of O(md), and the 2014 algorithm added iterative rounding by a minimum enclosing ellipsoid. Later releases add annealing schedules (Cousins-Vempala Gaussian cooling and the cooling-balls schedule from the ICMS 2020 paper) and billiard and Hamiltonian walks. The gains over exact tools come from replacing exact decomposition (exponential in dimension) with a polynomial-time randomised estimator.

## Compared with alternatives

None of the catalogued geometry-spatial siblings (geogram, CGAL-based Manifold or kigumi, Boost.Geometry alternatives, nanoflann) estimates d-dimensional polytope volume or samples convex bodies; pick volesti for that job in moderate to high dimension, and keep exact CGAL/qhull-style tools for low-dimensional exact answers.

## Integration

| | |
|---|---|
| **Form** | header-only templates (include/) plus the lp_solve C library, which the CMake helper downloads and builds as a static library |
| **Dependencies** | Eigen, Boost (random), lp_solve 5.5.2.11; optional Intel MKL, autodiff, Spectra and QD; ifopt, GMP, MPSolve and FFTW3 only when the non-linear oracles are enabled (off by default) |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17, 'needed by autodiff'), CMake 3.11; CI builds with g++ 9-12 and clang++ 11-14 on Ubuntu 22.04 |
| **Platforms** | Linux x86-64 tested in CI; R package checked on Ubuntu, macOS and Windows; macOS/ARM clang compile errors reported (issue #295) |
| **Thread safety** | Not documented. Functions take the polytope by non-const reference (the interior_point overloads mutate it) and each call owns its RNG, so separate polytope copies and RNGs per thread should be used; the n_threads argument does not spawn threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- volume_sequence_of_balls(..., n_threads) is not parallel and does not average: the loop over n_threads runs sequentially, divides the sample count by n_threads, and each pass resets vol to the first ball's volume, so the function returns only the last pass's estimate built from 1/n_threads of the points (the comment says 'take the average'). Leave n_threads at 1.
- The convenience overloads default to walk_length = 1 (the SoCG 2014 runs used W = floor(10 + d/10)), and the argument order differs between overloads: (P, error, walk_length) versus (P, interior_point, walk_length, error).
- The current volume_sequence_of_balls does no rounding, unlike the 2014 algorithm: round skinny polytopes first with the preprocess functions (inscribed_ellipsoid_rounding, min_sampling_covering_ellipsoid_rounding, svd_rounding).
- is_in() returns -1 for inside and 0 for outside; issue #391 ('Unintuitive is_in() semantics') is open and earlier reports (#385, #387, #389) found walks that misread it, so custom bodies and walks must follow that convention.

## Known shortcomings

- SoCG 2014 paper (Table 1 and Table 7, read from the author's github.io repo) measures the 2014 precursor code with flags unstated: cross-10 1.58 s vs VINCI 388.5 s, 4.6x vs the Cousins-Vempala Matlab code on cube-20 but slower from cube-80 up (simplex max 919.01 s); Birkhoff exact times are literature figures, not re-run.
- Enricher: the paper numbers measure the 2014 sourceforge precursor (CGAL+GMP LP), not today's Eigen+lp_solve code. Code bug in volume_sequence_of_balls: the n_threads loop runs sequentially, divides rnum by n_threads, resets vol each pass and returns only the last pass's estimate from 1/n_threads of the points although the comment says 'take the average'; default walk_length=1 vs the paper's W=10+d/10; no rounding in current SOB; clock-seeded RNG; open #463, #391, #295 (macOS/ARM). Not behind the measured numbers.

## Caveats and trade-offs

Peer-reviewed (SoCG 2014, Emiris and Fisikopoulos 'Efficient random-walk methods for approximating polytope volume'; volesti lists it in docs/misc/publications.md) but measures the 2014 precursor code (then on sourceforge randgeom), not today's volesti; PDF read from the author's GitHub pages repo; compiler and flags missing, so B and not A. Approximate versus exact answers are not the same task. Exact VINCI is faster on many low-dimensional inputs: cube-10 0.01 s vs 0.42 s, cube-15 0.40 s vs 1.44 s, simplices 0.01 to 0.02 s vs 0.56 to 919.01 s, rv-8-10 0.01 s vs 0.37 s, rv-10-12 0.01 s vs 1.00 s, cc-8-10 0.05 s vs 1.95 s, Fm-5 0.02 s vs 0.69 s. The Birkhoff exact times (B8 1920 s, B9 8 days, B10 6160 days) come from the birkhoff package's published computations (the paper equates B10 to a single 1 GHz processor running for almost 17 years), not from runs on the test machine. Against the Cousins-Vempala Matlab code (C++ vs Matlab, 10 runs) VolEsti is faster only for d &lt; 80 per the paper: cube-80 582.19 s vs 531.46 s, cube-90 875.69 vs 701.54, cube-100 1285.08 vs 884.43, B9 499.56 vs 420.07, B10 1034.74 vs 691.97 are slower; that code ran with eps = 0.1 against eps = 1 for VolEsti, and VolEsti does about 100 times more hit-and-run steps while returning 4 to 100 times smaller error on cube-d for d &gt; 70 and 5 to 80 times on Birkhoff polytopes. The repo README and docs carry no benchmark numbers.

Randomised approximation (hit-and-run random walks with iterative rounding and boundary oracles), not exact volume; relative error about 1% at eps = 1 and runtime grows steeply with dimension (cube-100 takes 1285 s). Source is LGPL-3.0, so linking is allowed but modifications to the library must be shared.

## Maintenance

Actively maintained (last commit 2026-06-29, GSoC contributions, CRAN package and JOSS paper); LGPL-3.0-or-later header-only code is copyable as a dependency, but the published speed numbers describe the 2014 precursor, not the current algorithms or defaults.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SoCG 2014 paper (Emiris and Fisikopoulos), listed in volesti's docs/misc/publications.md, with Table 1 (vs VINCI exact) and Table 7 (vs the Cousins-Vempala Matlab code) on an Intel Core i5-2400; compiler and flags are not stated and the 2014 code was on sourceforge randgeom, so B and not A. The 250x to 1180x gains are algorithmic (approximate vs exact volume), not implausible codegen gains.
- **Verifier notes:** All quoted Table 1 and Table 7 numbers, the hardware and the abstract sentence are on the PDF. Corrections: the record's caveat 'cube-60 and above slower' is wrong (cube-60 222.10 s vs 229.33 s and cube-70 358.93 vs 427.82 are VolEsti wins; slower from cube-80), simplex max time is 919.01 s, the Matlab code is reference [13] in the text, and Birkhoff exact times are literature figures. Metadata checked: LGPL-3.0-or-later, 189 stars, last commit 2026-06-29 (active).
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-178 (wave 8); enricher w8 pair-030
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vissarion/vissarion.github.io/master/publications/EF_socg14.pdf>
  - <https://github.com/GeomScale/volesti>
  - <https://github.com/GeomScale/volesti/commits>
  - <https://raw.githubusercontent.com/GeomScale/volesti/HEAD/README.md>
  - <https://raw.githubusercontent.com/GeomScale/volesti/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GeomScale/volesti/HEAD/docs/misc/publications.md>
  - <https://raw.githubusercontent.com/GeomScale/volesti/HEAD/docs/misc/credits.md>
- **Sources the enricher read:**
  - <https://github.com/GeomScale/volesti>
  - <https://github.com/GeomScale/volesti/tree/develop/include>
  - <https://github.com/GeomScale/volesti/tree/develop/include/preprocess>
  - <https://github.com/GeomScale/volesti/commits/develop>
  - <https://github.com/GeomScale/volesti/issues?q=is%3Aissue+volume+wrong+OR+bug+OR+crash>
  - <https://github.com/GeomScale/volesti/issues/387>
  - <https://github.com/GeomScale/volesti/issues/391>
  - <https://raw.githubusercontent.com/GeomScale/volesti/HEAD/README.md>
  - <https://raw.githubusercontent.com/GeomScale/volesti/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/GeomScale/volesti/HEAD/docs/misc/publications.md>
  - <https://raw.githubusercontent.com/GeomScale/volesti/HEAD/docs/getting_started/install.md>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/test/benchmarks_sob.cpp>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/test/benchmarks_cg.cpp>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/include/volume/volume_sequence_of_balls.hpp>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/include/volume/volume_cooling_balls.hpp>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/include/volume/volume_cooling_gaussians.hpp>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/include/generators/boost_random_number_generator.hpp>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/include/random_walks/uniform_ball_walk.hpp>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/include/convex_bodies/hpolytope.h>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/include/convex_bodies/ball.h>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/external/cmake-files/LPSolve.cmake>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/external/cmake-files/Eigen.cmake>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/external/cmake-files/Boost.cmake>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/.github/workflows/cmake-gcc.yml>
  - <https://raw.githubusercontent.com/GeomScale/volesti/develop/.github/workflows/cmake-clang.yml>
  - <https://raw.githubusercontent.com/vissarion/vissarion.github.io/master/publications/EF_socg14.pdf>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/geomscale/volesti`) · [data/wave8/enrich/raw/github_com_geomscale_volesti.json](../../../data/wave8/enrich/raw/github_com_geomscale_volesti.json) (enrichment confidence 0.75)

</details>
