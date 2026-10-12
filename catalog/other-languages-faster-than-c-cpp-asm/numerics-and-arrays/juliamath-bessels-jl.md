# Bessels.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Pure-Julia Bessel, Hankel and Airy functions for real arguments; README claims 2.3-10x over SpecialFunctions.jl (openlibm/AMOS).

| | |
|---|---|
| **Beats** | SpecialFunctions.jl wrappers: openlibm (C, FreeBSD msun) j0/y0/j1/y1/jn/yn for integer-order and order-0 and 1 calls, AMOS zbes\* routines (Fortran, via openspecfun) for non-integer order, so only the order-0 and order-1 rows have a C baseline |
| **Claimed result** | README Benchmarks (relative speed increase over SpecialFunctions.jl): besselj0 2.5x, bessely0 2.3x (the two rows whose baseline is openlibm C), besselj(nu,x) 6x, bessely(nu,x) 5x, besseli0 10x, besseli(nu,x) 7x, besselk0 10x, besselk(nu,x) 4x, Bessels.gamma 5x. README prose: 'in general 5-10x faster'. |
| **Workload** | Float64 evaluation of Bessel J, Y, I, K functions and gamma for random x and order nu between 0 and 100. |
| **Metric** | throughput |
| **Hardware** | Apple M1 run under Rosetta (x86 emulation) |
| **Compiler and flags** | Julia 1.7.2 (no C/Fortran flags: baselines are prebuilt binary libraries) |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Different algorithms: piecewise polynomial/rational approximations per domain written in pure Julia that inline and vectorize, versus AMOS general-order series/recurrences and libm's older rational approximations. |
| **Adoption** | 91 stars |
| **Last commit** | 2026-06-30 |
| **Links** | [repository](https://github.com/JuliaMath/Bessels.jl) · [benchmark](https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/README.md) |

## Verdict

The README reports first-party speed ratios against SpecialFunctions.jl for random x and nu in (0, 100) on Julia 1.7.2 on an Apple M1 under Rosetta, with no absolute times and no published harness: 2.5x and 2.3x for besselj0 and bessely0 (the only rows whose baseline is C, openlibm's msun j0/y0 through ccall), and 4-10x for the other rows, whose baseline is mostly AMOS Fortran via openspecfun. A commenter on a fortran-lang Discourse thread reproduced roughly 10x for besselk0 with a simple @benchmark (known from a search snippet; the thread itself was unreachable).

## Use it when

- Julia code that evaluates many scalar Bessel J/Y/I/K values for real Float64 or Float32 arguments inside a hot loop, where a ccall into openlibm or AMOS per value dominates.
- Order-0 and order-1 calls (besselj0, bessely0, besseli0, besselk0 and their order-1 versions) where fixed polynomial approximations replace the libm or AMOS path.
- Many consecutive integer orders at one argument: besselj(0:100, x) uses recurrence (README: 398 ns for 101 orders), and besselj!(out, nu, x) avoids the allocation.
- Code that needs Bessel functions differentiable with Enzyme (master ships an EnzymeCore extension) or wants native Float32 code paths for the order-0/1 functions (Float16 inputs are computed in Float32).

## Skip it when

- Complex arguments or complex orders beyond Airy and order-0/1 J and I: use SpecialFunctions.jl (AMOS).
- Tiny arguments with integer orders: issue #58 measured besselj(10, x) for x around 1e-10 at about 30.9 ns against 8.5 ns in SpecialFunctions, because the power series calls gamma instead of a factorial and has no integer-order shortcut.
- When the last ulp matters near zeros: the README's own ArbNumerics comparison gives maximum relative errors up to 2e-11 (besselj(5.0, x)) and 7e-13 (besselj1), and says accuracy is sometimes a digit or two worse than SpecialFunctions.
- Hankel and spherical functions at awkward inputs: open bugs give NaN for hankelh1(7, sqrt(224)) (#111), sphericalbesselj with large l and small x (#121) and besselj for negative x with large negative integer order (#113).
- Higher precision (BigFloat, Double64) is not supported yet (#98); Float128 files exist in the source but the README lists higher precision as a plan.

## How it is fast

Each function splits the (nu, x) plane into regions and uses a cheap closed form in each: fixed minimax polynomials (for Float64 besselj0, 16 degree-13 polynomials centred on roots and extrema after Harrison's 2009 'Fast and accurate Bessel function computation', then a modified Hankel asymptotic expansion above x = 26), Debye uniform asymptotic expansions for large orders, large-argument expansions, power series for small x, and a Levin sequence transformation for besselk. Everything is generic Julia that inlines into the caller and uses evalpoly and SIMDMath vector Horner/Levin kernels, whereas the baseline goes through ccall into openlibm (FreeBSD msun j0/y0) or AMOS's complex-argument Fortran routines. The maintainer attributes most of the gap to faster-converging asymptotic series and to avoiding continued fractions (search snippet of a fortran-lang Discourse thread, page itself unreachable).

## Compared with alternatives

No catalogued sibling covers special functions: FFTA.jl, Gaius.jl and TriangularSolve.jl are other pure-Julia replacements for C libraries in different domains. Pick Bessels.jl over the baseline SpecialFunctions.jl for real-argument Bessel evaluations in Julia hot loops; keep SpecialFunctions for complex arguments, tiny-argument integer orders, and, on master, small-order besseli.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Registered v0.2.8: none. Master (0.3.0-DEV): Gamma.jl and SIMDMath.jl, with EnzymeCore as an optional extension. |
| **Minimum toolchain** | Julia 1.10 on master; Julia 1.6 for registered v0.2.8 |
| **Platforms** | any platform Julia runs on (pure Julia, no binary artifacts) |
| **Thread safety** | not documented; the scalar functions keep no shared mutable state in the source read, and the ! variants write only to the caller's buffer |
| **Drop-in for the baseline** | partial — same function names as SpecialFunctions.jl for real arguments, but complex support is limited, negative arguments with complex results throw DomainError, and both packages export the same names, so calls must be qualified if both are loaded |

## Gotchas

- Hot-path performance bug on master (open issue #115 since June 2024): besseli_power_series in src/BesselFunctions/besseli.jl calls Math.check_convergence(t, s), but the helper is defined as check_convergence(ser, term) = abs(term) &lt;= eps(T)\*ser, so for positive x the test abs(s) &lt;= eps\*t never fires and the loop always runs all 3001 iterations. Results stay correct because the terms underflow to zero, but besseli and besselix with nu &lt;= 25 and x &lt;= 35 (outside the large-argument branch) cost thousands of loop iterations instead of tens. Registered v0.2.8 has the correct test (abs(a) &lt; eps(T) \* abs(out)); the maintainer called it an oversight from the Enzyme refactor. The README's 'besseli(nu, x) 7x' row cannot hold in that region on the master branch that the README's quick start installs.
- The README benchmark table was written between January and October 2022 on Julia 1.7.2 under Rosetta, before the besselj0 rewrite to Harrison's root-centred polynomials, the SIMDMath and Enzyme refactors, and the May 2026 move of gamma into Gamma.jl, so the ratios describe older code; no comparison harness is in the repo, and benchmark/benchmark.jl's 'bessely' group actually times besselj0 and besselj1.
- The README still says the package is 'self contained without any external dependencies'; master now depends on Gamma.jl and SIMDMath.jl. Bessels.gamma is a re-export of Gamma.jl, so the README's 5x gamma row is no longer Bessels' own code.
- `pkg> add Bessels` gives v0.2.8 (the last registered version, early 2023), while the README quick start adds the git URL and gets the unregistered 0.3.0-DEV master, which has the Enzyme support and also the besseli slowdown above.

## Known shortcomings

- First-party ratios measured under Rosetta; benchmark/benchmark.jl times only Bessels and its bessely group is mislabelled; the baseline is mostly Fortran AMOS, only the j0/y0 rows are against openlibm C (-O3); a different algorithm.
- Harness flaw on master: besseli_power_series (src/BesselFunctions/besseli.jl:626) calls Math.check_convergence(t, s) with its arguments reversed, so the loop never exits early and always runs 3001 iterations for besseli/besselix with nu &lt;= 25, x &lt;= 35 (results stay correct, but the README's 'besseli(nu,x) 7x' cannot hold there; issue #115 open since 2024-06; registered v0.2.8 has the correct check while the README quick start installs master). The README table is from 2022 (Julia 1.7.2, Rosetta) and predates the besselj0 rewrite to Harrison 2009 root-centred polynomials (not Cephes for Float64). Open NaN bugs #111, #113, #121; besselj(10,x) at tiny x 30.9 vs 8.5 ns (#58); 'no dependencies' is stale (Gamma.jl, SIMDMath.jl).

## Caveats and trade-offs

First-party, run under Rosetta emulation, no compiler flags or CPU model beyond 'Apple M1', and speedups are ratios with no absolute times. The comparison harness is not in the repo: benchmark/benchmark.jl times only Bessels functions (no SpecialFunctions.jl calls), and its 'bessely' group actually times besselj0/besselj1. Most of the baseline is Fortran AMOS reached through SpecialFunctions' complex-argument path (besseli, besselk and non-integer besselj/bessely all call zbes\* via openspecfun), and a Fortran-vs-Julia comparison is outside this catalogue's scope; only besselj0/bessely0 (2.5x, 2.3x) are measured against C code (openlibm j0/y0, which openlibm's Make.inc builds at -O3 by default), and that baseline goes through non-inlinable Julia ccall wrappers. Algorithm differs (Bessels' besselj0 cites the Cephes rational approximations, openlibm uses FreeBSD msun's), so this is a library win, not a language win. The Bessels.gamma row is a re-export of Gamma.jl per the README, not Bessels' own code. [retier] On master besseli_power_series calls Math.check_convergence(t, s) with reversed arguments, so the loop always runs 3001 iterations for besseli/besselix with nu &lt;= 25, x &lt;= 35 (results correct, but the 'besseli(nu,x) 7x' cannot hold there; issue #115 open since 2024-06; registered v0.2.8 is correct while the README quick start installs master). The README table is from 2022 (Julia 1.7.2, Rosetta) and predates the besselj0 rewrite to Harrison 2009 root-centred polynomials (not Cephes for Float64). Open NaN bugs #111, #113, #121; besselj(10,x) at tiny x 30.9 vs 8.5 ns (#58).

README admits accuracy is sometimes 'within a digit or two' of the baselines rather than better (its own error table vs ArbNumerics gives mean/max relative errors such as besselj0 3e-16/6e-14 and besselj(5.0,x) 3e-14/2e-11); positive real arguments mainly, limited complex support; Float64 focus.

## Maintenance

Active only in maintenance mode: 2026 commits are dependency bumps, Enzyme fixes and the Gamma.jl split by one maintainer, the last registered release is v0.2.8 from early 2023, and several NaN bugs plus the besseli convergence bug (#115) stay open; MIT and pure Julia, so it is easy to vendor or pin to v0.2.8.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks table gives first-party ratios against SpecialFunctions.jl (Julia 1.7.2, Apple M1 under Rosetta) with no absolute times; the repo's benchmark/benchmark.jl times Bessels alone, so the comparison harness is not public. First-party with partial methodology is C.
- **Verifier notes:** Numbers match the README table exactly; baseline description verified against SpecialFunctions.jl src/bessel.jl (openlibm j0/y0/j1/y1/jn/yn; AMOS zbesi/zbesj/zbesk/zbesy). Shortcomings: first-party ratios without absolute times, Rosetta emulation, comparison harness not public (benchmark.jl times Bessels only and mislabels the bessely group), mostly Fortran baseline, different algorithms, ccall overhead on the C rows. Metadata checked: MIT, 91 stars, last commit 2026-06-30, active.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-03 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/JuliaMath/Bessels.jl>
  - <https://github.com/JuliaMath/Bessels.jl/commits>
  - <https://github.com/JuliaMath/Bessels.jl/tree/master/benchmark>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/master/benchmark/benchmark.jl>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/master/src/BesselFunctions/besselj.jl>
  - <https://raw.githubusercontent.com/JuliaMath/SpecialFunctions.jl/master/src/bessel.jl>
  - <https://raw.githubusercontent.com/JuliaMath/openlibm/master/Make.inc>
- **Sources the enricher read:**
  - <https://github.com/JuliaMath/Bessels.jl>
  - <https://github.com/JuliaMath/Bessels.jl/commits/master>
  - <https://github.com/JuliaMath/Bessels.jl/commits/master/README.md>
  - <https://github.com/JuliaMath/Bessels.jl/issues?q=is%3Aissue>
  - <https://github.com/JuliaMath/Bessels.jl/issues/115>
  - <https://github.com/JuliaMath/Bessels.jl/issues/58>
  - <https://github.com/JuliaMath/Bessels.jl/issues/111>
  - <https://github.com/JuliaMath/Bessels.jl/tree/master/src/BesselFunctions>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/benchmark/benchmark.jl>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/src/Bessels.jl>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/src/precompile.jl>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/src/Math/Math.jl>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/src/BesselFunctions/BesselFunctions.jl>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/src/BesselFunctions/besseli.jl>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/src/BesselFunctions/besselj.jl>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/src/BesselFunctions/besselk.jl>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/HEAD/src/BesselFunctions/U_polynomials.jl>
  - <https://raw.githubusercontent.com/JuliaMath/Bessels.jl/v0.2.8/src/besseli.jl>
  - <https://raw.githubusercontent.com/JuliaRegistries/General/master/B/Bessels/Versions.toml>
  - <https://raw.githubusercontent.com/JuliaRegistries/General/master/B/Bessels/Compat.toml>
  - <https://raw.githubusercontent.com/JuliaRegistries/General/master/B/Bessels/Deps.toml>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/juliamath/bessels.jl`) · [data/wave14/enrich/raw/github_com_juliamath_bessels_jl.json](../../../data/wave14/enrich/raw/github_com_juliamath_bessels_jl.json) (enrichment confidence 0.75)

</details>
