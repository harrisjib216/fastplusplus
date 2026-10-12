# FastTanhSinhQuadrature.jl (Julia tanh-sinh quadrature)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `GPL-3.0` · 🟢 active

> Julia tanh-sinh (double-exponential) quadrature for 1D-3D boxes; beats Cubature/Cuba C wrappers on endpoint-singular and low-order integrands.

| | |
|---|---|
| **Beats** | Cubature.jl (wrapper of the C cubature library, h- and p-adaptive) and Cuba.jl (wrapper of the C Cuba library: Vegas, Divonne, Cuhre) for 2D and 3D integrals; QuadGK.jl and FastGaussQuadrature.jl (Julia) for 1D |
| **Claimed result** | README table, ns per call (ratios derived from page data): 2D x^2+y^2: FTS quad 2153 vs Cubature h 5980 (2.8x) and Cubature p 9098 (4.2x), Cuhre 6.858e4. 2D exp(x+y): FTS avx 5720 vs Cubature p 3.861e4 (6.7x) and Cuhre 6.697e4; the adaptive FTS quad is 2.438e4, only 1.6x faster than Cubature p. 3D x^2\*y^2\*z^2: FTS avx 2.207e4 vs Cubature p 2.441e4 (1.1x); FTS quad 7.634e4 is slower than Cubature p. Endpoint-singular 2D 1/sqrt((1-x^2)(1-y^2)): FTS avx 1865 and quad 3660 vs Cubature h 2.832e7, the only C baseline that met tolerance; Cubature p (2433) and all Cuba methods missed it. Not a win: 3D exp(x+y+z): FTS quad 1.069e6 and avx 3.401e5 vs Cuhre 1.795e5 and Cubature h 3.17e5. The checked-in benchmark/results/timings_full.md comes from a different run with different numbers (e.g. 2D x^2+y^2: FTS quad 1576 vs Cubature h 2720, 1.7x). |
| **Workload** | Adaptive numerical integration at rtol=1e-6, atol=1e-8 of 1D, 2D and 3D test integrands on [-1,1]^d (endpoint singularities, smooth, oscillatory), @belapsed timings with caches prebuilt. |
| **Metric** | latency |
| **Hardware** | Intel Core Ultra 7 155U |
| **Compiler and flags** | Julia (JIT, no flags). The README table does not name the Julia version; REPRODUCIBILITY.md names 1.11/1.12 for tests and 1.13 for figures, and benchmark/Manifest.toml is not in the repo (404). The C baselines are Cubature.jl and Cuba.jl wrappers over prebuilt JLL binaries; their compiler and flags are not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Double-exponential (tanh-sinh) node clustering with prebuilt adaptive caches and an AVX interface (README); no mechanism analysis against the C libraries. |
| **Adoption** | 16 stars; JOSS paper draft in the repo |
| **Last commit** | 2026-04-16 |
| **Links** | [repository](https://github.com/svretina/FastTanhSinhQuadrature.jl) · [benchmark](https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/README.md) |

## Verdict

These are author-run @belapsed timings on an Intel Core Ultra 7 155U at rtol 1e-6 / atol 1e-8, with the Julia version unstated. They compare FTS against Cubature.jl (h and p) and Cuba.jl, Julia wrappers over prebuilt C JLL binaries whose build flags are unstated. The robust result is the endpoint-singular 2D case: FTS takes 1.9-3.7 us, Cubature h 28 ms, and every other C method misses tolerance. Smooth-case wins of 1.1-6.7x are within the harness's run-to-run noise or depend on the oracle-N avx rows, and Cuhre wins on 3D exp.

## Use it when

- 1D integrals dominated by endpoint singularities (1/sqrt(1-x^2), log(1-x)): README run shows quad 528-592 ns against QuadGK 5.2-11.5 us and Cubature h 74-239 us at rtol 1e-6
- 2D or 3D box integrals with singularities on the faces, where h-adaptive cubature (Cubature h, HCubature) needs 28-52 ms and Cubature p and Cuba miss tolerance; FTS takes 2-4 us in 2D
- Repeated integrals over the same box, where a prebuilt adaptive cache or a precomputed (x, w, h) rule can be reused across thousands of calls
- Extended-precision quadrature (Double64, BigFloat, MultiFloats) with the same API as Float64

## Skip it when

- Oscillatory or locally peaked 1D integrands: sin^2(1000x) takes 254 us with quad against 11.4 us with QuadGK (README), and the maintainer measured 26x slower in issue #25; use QuadGK
- Smooth 3D integrands such as exp(x+y+z): Cuba Cuhre (180 us) and Cubature h (317 us) beat adaptive FTS (1.07 ms) in the README run
- More than three dimensions, vector-valued integrands, or interior singularities at unknown locations (quad_split needs the point)
- Projects that cannot take a GPL-3.0 dependency
- Code that must run its _avx paths on Julia 1.13 or later: the test suite marks AVX failures there as allowed (LoopVectorization compatibility), and Project.toml compat stops at 1.12

## How it is fast

The double-exponential substitution x = tanh(pi/2 sinh t) clusters nodes at the endpoints, so integrands with algebraic or log endpoint singularities converge in a few dozen nodes per axis, where h-adaptive Genz-Malik cubature subdivides tens of thousands of times. The adaptive routine halves the step each level and evaluates only the new odd-index nodes, using the 2- and 4-way symmetry of the box. Node and weight tables (the tanh/sinh/cosh work) are memoized in global per-type caches, so later calls do no transcendental setup. The _avx variants run the same sums through LoopVectorization @turbo.

## Compared with alternatives

No other quadrature library is catalogued yet; the closest siblings are Julia numerics packages beating C (Bessels.jl, FFTA.jl, TriangularSolve.jl), each for a different kernel. Pick this one when the job is integrating a callable with endpoint singularities over a 1D-3D box, the one case where its win over the C cubature libraries is large and algorithmic rather than overhead.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | StaticArrays, LambertW, LoopVectorization 0.12 |
| **Minimum toolchain** | Julia 1.9 (compat 1.9-1.12) |
| **Platforms** | any Julia platform; _avx variants need a LoopVectorization-compatible Julia (AVX checks allowed to fail on 1.13+) |
| **Thread safety** | Global node/weight caches are built under a ReentrantLock, so concurrent calls are safe; otherwise not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (probable, not run here): benchmark/benchmarks.jl assigns f, low and up in each branch of an if/elseif/else, and Julia boxes captured variables that are assigned in more than one place (manual: Performance of captured variable). The per-evaluation wrappers given to Cubature, HCubature and Cuba (v -&gt; f(v[1], v[2]) and cuba_f) then pay a runtime dispatch on every integrand call, while the FTS, QuadGK and FastGauss closures pay one dispatch per integral and then run specialised loops. The C-library rows may therefore include Julia callback overhead (Cuba Vegas, which misses tolerance and so presumably runs to the 200000-evaluation cap, works out to about 425 ns per evaluation). HCubature also gets Vector rather than SVector bounds.
- Measurement noise exceeds several claimed ratios. The run uses samples=3 and evals=1, and the two runs checked in on 2026-04-04 disagree by up to 3.5x (QuadGK on 1/(1+25x^2): 1612 vs 458 ns; Cubature h on 2D x^2+y^2: 5980 vs 2720 ns). The quad wrapper is often timed faster than adaptive_integrate_\*, the function it calls (1D x^6: 652 vs 1560 ns). Neither run includes the v2.1.0 hot-path and adaptive-AVX changes of 2026-04-05/06.
- The 'FTS avx' rows are fixed rules at the N found by a prior adaptive run, with no error estimate. In 2D and 3D they also use the 1D truncation window (tanhsinh default D=1) where the adaptive caches use tmax(T, D). They show the speed of a precomputed rule, not of adaptive integration.
- Nodes are clamped to prevfloat(1), so 1-x computed inside the integrand loses relative precision near the endpoints; use quad_cmpl for forms such as log(1-x) or 1/sqrt((1-x)(1+x)). Before PR #31 (2026-04-03) the stopping rule was unreliable (error 0.084 on sin^2(1000x), issue #25). The first call for a new (type, max_levels) pair builds the global cache and is slower.

## Known shortcomings

- C-library (Cubature/Cuba JLL) flags and Julia version unstated; algorithm win, not language; the avx rows use an oracle N against adaptive solvers and many baseline cells miss the tolerance; the README table differs from the checked-in timings_full.md.
- Probable harness flaw (not run, no Julia here): benchmarks.jl assigns f, low and up in all three if/elseif/else branches, so Julia likely boxes them, after which the Cubature, HCubature and Cuba wrappers dispatch at runtime on every integrand call while FTS, QuadGK and FastGauss dispatch once per integral. Run noise reaches 3.5x: two runs checked in on 2026-04-04 disagree (QuadGK 1612 vs 458 ns) and the quad wrapper is timed faster than the function it calls (652 vs 1560 ns), which exceeds the 1.1-1.6x smooth-case claims. Published numbers predate the v2.1.0 kernels; the 2D/3D avx rows use the 1D truncation window; AVX tests may fail on Julia 1.13+. The endpoint-singular win stands. JOSS published 2026-04-16 (DOI 10.21105/joss.10076); issue #25: 26x slower than QuadGK on oscillatory integrals.

## Caveats and trade-offs

This is an algorithmic comparison (tanh-sinh against h/p-adaptive cubature and Monte Carlo), not a language one. Baselines are Julia wrappers around C libraries that call back into the Julia integrand once per evaluation, so the comparison mixes algorithm with wrapper and callback overhead. The 'FTS avx' rows are not adaptive: they rerun a precomputed rule at the N the adaptive FTS run had already found (benchmark/benchmarks.jl: 'FTS avx is run at the N inferred from adaptive FTS convergence'), which is an oracle grid timed against adaptive solvers; the largest smooth-case win (6.7x on 2D exp) comes from it. Several baseline cells carry '\*' (tolerance not met: Cuba Vegas and Divonne on 2D and 3D, Cubature p on the singular cases), so their times are meaningless for those cases. The run is author-run on one laptop CPU with samples=3, evals=1. Cuhre and Cubature h are faster on 3D exp(x+y+z). The README table and the checked-in results/timings_full.md disagree (different runs). The headline plot (JOSS_paper/benchmark_summary.svg) compares against the fastest accurate method per case, which for 1D is a Julia package (QuadGK or FastGaussQuadrature), not a C baseline. The JOSS review badge is present, but publication status could not be checked because joss.theoj.org did not resolve; JOSS reviews software, not benchmark claims. [retier] benchmarks.jl assigns f, low and up in all three if/elseif/else branches, so Julia likely boxes them, after which the Cubature, HCubature and Cuba wrappers dispatch at runtime on every integrand call while FTS, QuadGK and FastGauss dispatch once per integral (not run). Run noise reaches 3.5x (two 2026-04-04 runs give QuadGK 1612 vs 458 ns; the quad wrapper is timed faster than the function it calls), exceeding the 1.1-1.6x smooth-case claims. Published numbers predate the v2.1.0 kernels; the 2D/3D avx rows use the 1D truncation window. Issue #25: 26x slower than QuadGK on oscillatory integrals.

Tanh-sinh double-exponential rules: best for endpoint-dominated integrands on boxes; AVX interface; GPL-3.0 licence; Julia only.

## Maintenance

Active: v2.1.0, last commit 2026-04-16, JOSS paper accepted and published 2026-04-16 (DOI 10.21105/joss.10076, review openjournals/joss-reviews#10076), all 15 issues closed. It is copyable under GPL-3.0, but the benchmark numbers predate the v2.1.0 kernels and benchmark/Manifest.toml is not in the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The README table matches the claimed numbers and the benchmark code is public (benchmark/benchmarks.jl), with the CPU named (Core Ultra 7 155U). It falls short of A: the README run does not name its Julia version, and the C baselines (Cubature, Cuba) are prebuilt JLL binaries whose compiler and flags are stated nowhere. Numbers are first-party from one laptop, so the tier is C.
- **Verifier notes:** Downgrade A to C. Shortcomings: C-library build flags and the Julia version of the README run are unstated, the comparison is of algorithms rather than languages, the avx rows use an oracle N against adaptive solvers, several baseline cells miss tolerance, and the run is first-party on a laptop. Metadata checked: GPL-3.0, 16 stars, last commit 2026-04-16, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-79 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/README.md>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/REPRODUCIBILITY.md>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/benchmark/benchmarks.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/benchmark/results/timings_full.md>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/benchmark/results/timings.csv>
  - <https://github.com/svretina/FastTanhSinhQuadrature.jl>
  - <https://github.com/svretina/FastTanhSinhQuadrature.jl/commits/master>
- **Sources the enricher read:**
  - <https://github.com/svretina/FastTanhSinhQuadrature.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/README.md>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/REPRODUCIBILITY.md>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/Project.toml>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/benchmark/Project.toml>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/benchmark/benchmarks.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/benchmark/results/timings_full.md>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/benchmark/results/timings.csv>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/src/FastTanhSinhQuadrature.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/src/core.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/src/caches.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/src/integrate1D.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/src/integrate2D.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/src/integrate3D.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/src/adaptive.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/src/quad.jl>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/.github/workflows/CI.yml>
  - <https://raw.githubusercontent.com/svretina/FastTanhSinhQuadrature.jl/master/test/runtests.jl>
  - <https://github.com/svretina/FastTanhSinhQuadrature.jl/issues?q=is%3Aissue>
  - <https://github.com/svretina/FastTanhSinhQuadrature.jl/issues/25>
  - <https://github.com/svretina/FastTanhSinhQuadrature.jl/commits/master>
  - <https://github.com/svretina/FastTanhSinhQuadrature.jl/commits/master/benchmark/results/timings_full.md>
  - <https://github.com/svretina/FastTanhSinhQuadrature.jl/commits/master/README.md>
  - <https://github.com/openjournals/joss-reviews/issues/10076>
  - <https://raw.githubusercontent.com/JuliaSIMD/LoopVectorization.jl/main/README.md>
  - <https://raw.githubusercontent.com/giordano/Cuba.jl/master/README.md>
  - <https://raw.githubusercontent.com/giordano/Cuba.jl/master/src/Cuba.jl>
  - <https://raw.githubusercontent.com/JuliaLang/julia/master/doc/src/manual/performance-tips.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/svretina/fasttanhsinhquadrature.jl`) · [data/wave14/enrich/raw/github_com_svretina_fasttanhsinhquadrature_jl.json](../../../data/wave14/enrich/raw/github_com_svretina_fasttanhsinhquadrature_jl.json) (enrichment confidence 0.65)

</details>
