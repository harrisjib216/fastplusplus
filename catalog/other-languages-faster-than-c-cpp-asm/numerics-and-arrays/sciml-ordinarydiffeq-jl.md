# OrdinaryDiffEq.jl (DifferentialEquations.jl) ODE solvers vs Sundials, ODEPACK and Hairer codes

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Julia ODE solver suite whose Verner Runge-Kutta methods beat Sundials CVODE/ARKODE on small non-stiff work-precision benchmarks.

| | |
|---|---|
| **Beats** | Sundials CVODE_Adams and ARKODE (C) and liblsoda (C port of ODEPACK lsoda), plus Hairer dopri5/dop853/odex (Fortran), called through Julia wrappers with a Julia right-hand side. |
| **Claimed result** | SciMLBenchmarks README summary (no numbers): non-stiff 'OrdinaryDiffEq.jl's methods are the most efficient by a good amount', the Vern methods do best, ARKODE and Hairer dopri5/dop853 are 'far less efficient than the Vern methods', CVODE_Adams and lsoda 'tend to not do very well'; stiff: ARKODE is inconsistent and KenCarp4 is 'much more efficient in most cases'. Rigid Body work-precision plot (RigidBody_wpd_5_1, 3 equations, AMD EPYC 7502): Vern7/Vern8 take about 2e-5 to 1e-4 s while CVODE_Adams and ARKODE (explicit, order 6) take about 1e-4 to 1e-3 s over the same error range, roughly 5-10x at matched error (read off the plot, derived from page data). On the stiff Pollution page (20 equations) FBDF is only modestly ahead of CVODE_BDF in the high-tolerance plot, and the page's own conclusion reads 'Sundials CVODE_BDF the best here'. |
| **Workload** | Work-precision diagrams (wall time versus error at tolerances 1e-6 to 1e-13) for non-stiff ODEs: Lotka-Volterra, Pleiades and Three-Body. |
| **Metric** | other |
| **Hardware** | AMD EPYC 7502 32-Core (128 threads), Linux; Julia 1.11.9, LLVM 16.0.6 (znver2), per the RigidBody and Pollution page appendices |
| **Compiler and flags** | Julia 1.11.9 (LLVM 16.0.6, znver2) for OrdinaryDiffEq; Sundials C library via Sundials.jl v6.7.1 and Sundials_jll v7.5.0+0 (BinaryBuilder build, compiler and flags not stated); ODEInterface_jll v0.0.2 and LSODA_jll v0.1.2 for the secondary baselines |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Pages credit the Verner methods and algorithm-specific interpolants; Julia specialization of the user's ODE function (FullSpecialize, StaticArrays) is implied by the setup but not argued as the cause. |
| **Adoption** | 692 stars (OrdinaryDiffEq.jl); SciMLBenchmarks.jl 346 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/SciML/OrdinaryDiffEq.jl) · [benchmark](https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/NonStiffODE/RigidBody_wpd.md) |

## Verdict

SciMLBenchmarks RigidBody work-precision page (3-equation rigid body, abstol 1e-6 to 1e-13, min of up to 100 runs, AMD EPYC 7502, Julia 1.11.9): Vern7/Vern8 take about 2e-5 to 1e-4 s against about 1e-4 to 1e-3 s for CVODE_Adams and explicit order-6 ARKODE (Sundials_jll 7.5.0 through Sundials.jl 6.7.1, build flags unstated), roughly 5-10x at matched final-time error read off the plot. This is an algorithm comparison measured by the solver's own authors, with the C solvers driven through Julia wrappers and callbacks.

## Use it when

- Small non-stiff systems (a handful to tens of states) solved to tolerances of 1e-6 to 1e-13, where Vern7/Vern8 reach matched error in roughly 5-10x less time than CVODE_Adams or explicit ARKODE in the RigidBody plot.
- Many repeated solves of tiny systems (parameter sweeps, ensembles) where an SVector state and out-of-place RHS avoid allocations entirely.
- Small-to-medium stiff systems at low tolerances, where Rodas4/Rodas5P lie below CVODE_BDF in the Pollution low-tolerance plot.
- Projects already in Julia that want to compare or switch algorithms (CVODE, LSODA, Hairer codes, native methods) without rewriting the model.

## Skip it when

- C or C++ codebases: there is no C API, so using it means embedding Julia; the comparison says nothing about CVODE called natively from C.
- Stiff problems where CVODE_BDF is already well tuned: on POLLU (20 equations) FBDF is roughly tied with CVODE_BDF and the page's prose names CVODE_BDF the best.
- Fixed-step implicit solves (adaptive = false) of linear systems: open issue #2586 measures OrdinaryDiffEq ImplicitEuler 70-100x slower than a hand-written loop at N = 100 because W is rebuilt and refactorized every step.
- Short-lived processes or scripts where Julia start-up, package loading and first-solve compilation dominate the solve time.
- Delay equations with long histories or many interpolation points: open performance issues #3146-#3149 report history memory growing with tspan and allocation-heavy interpolation.

## How it is fast

On non-stiff problems the win is algorithmic: Verner's high-order RK pairs (Vern7/Vern8) and Tsit5 need fewer function evaluations per unit of accuracy than Adams multistep (CVODE_Adams, lsoda) or order-6 explicit ARKODE at tight tolerances. Julia compiles the solver specialised on the user's RHS type (FullSpecialize in the benchmark), and the out-of-place StaticArrays path keeps a 3-element state in registers with no heap allocation. On stiff problems the Rosenbrock methods (Rodas4, Rodas5P) with an analytic or AD Jacobian are the strongest entries.

## Compared with alternatives

Pick it for CPU solves of small ODE systems; DiffEqGPU.jl is the sibling for large GPU ensembles, benchmarked against the CUDA C++ MPGOS library. Other numerics siblings (Bessels.jl, FFTA.jl, TriangularSolve.jl) beat C wrappers on different kernels and do not overlap.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Julia packages: SciMLBase, DiffEqBase, OrdinaryDiffEqCore plus per-family sublibraries (OrdinaryDiffEqVerner, OrdinaryDiffEqTsit5, OrdinaryDiffEqBDF, OrdinaryDiffEqRosenbrock, ...), ADTypes, SciMLLogging |
| **Minimum toolchain** | Julia 1.10 (Project.toml compat); benchmark run on Julia 1.11.9 |
| **Platforms** | any platform Julia supports; benchmark numbers from x86-64 (AMD EPYC 7502, LLVM znver2) |
| **Thread safety** | not documented in the pages read; each solve call builds its own integrator and cache |
| **Drop-in for the baseline** | partial: inside Julia's SciML solve interface, replacing CVODE_Adams() with Vern7() is a one-argument change; from C/C++ there is no drop-in replacement for CVODE |

## Gotchas

- Harness asymmetry in DiffEqDevTools (lib/DiffEqDevTools/src/benchmark.jl): every timed run calls solve(prob, alg, sol.u, sol.t, sol.k) with the previous solve's output arrays; OrdinaryDiffEqCore reuses them (convert plus copyat_or_push!), while Sundials.jl's __init ignores them and also creates a new SUNContext, CVodeCreate/CVodeInit, NVector wrappers and Julia callbacks on every timed run, then drives CVODE in CV_ONE_STEP mode, returning to Julia after each internal step. For 20 us to 1 ms solves this per-solve and per-step wrapper cost is inside the C solvers' times, so the 5-10x gap overstates what native C CVODE would lose.
- OrdinaryDiffEq v7 changed ODEFunction's default to AutoSpecialize; the benchmark explicitly uses ODEProblem{true, SciMLBase.FullSpecialize}, and NEWS.md says to opt into FullSpecialize to get maximum inlining, so default user code may not reproduce the plotted times.
- The RigidBody_wpd_5_1 legend repeats the names Vern7 and Vern8: the lower two curves are the StaticArrays out-of-place runs (prob_choice 2), a path the C solvers cannot use.
- The record's 'ODEPACK lsoda (Fortran)' baseline is actually liblsoda, Simon Frost's C translation of LSODA, via LSODA.jl; and the Pollution page's prose conclusion ('Sundials CVODE_BDF the best here') disagrees with its own low-tolerance plot Pollution_16_1, where Rodas5P runs roughly 2-3x faster than CVODE_BDF at about 1e-9 error and FBDF roughly ties it, so that prose is probably stale.

## Known shortcomings

- Found by the num papers, num gh-cpp and jitaot papers searches; the numerics-and-arrays category is kept by override (ODE solver work-precision results against Sundials and Fortran, plots only).
- An algorithm win, not a language win: Sundials is driven through Julia callbacks with wrapper setup inside the timing; numbers exist only in plots (Rigid Body roughly 5-10x read off the SciMLBenchmarksOutput page, AMD EPYC 7502); the Pollution page names CVODE_BDF best.
- Harness asymmetry: DiffEqDevTools times solve(prob, alg, sol.u, sol.t, sol.k), which OrdinaryDiffEqCore reuses, while Sundials.jl ignores those arrays, rebuilds the SUNContext, CVodeCreate and NVector on every timed run and drives CVODE in CV_ONE_STEP mode, so the 5-10x figures overstate the native C solvers' loss. v7 defaults to AutoSpecialize while the benchmark forces FullSpecialize; the record's 'ODEPACK lsoda (Fortran)' is the liblsoda C port; the Pollution prose says CVODE_BDF is best while its plot 16_1 shows Rodas5P about 2-3x faster; issue #2586 reports fixed-step implicit methods 70-100x slow.

## Caveats and trade-offs

First-party suite run by the SciML project on its own solvers. Algorithm versus algorithm: Vern7/8/9 and Tsit5 against Dormand-Prince, Adams and ARKODE methods, so the win is not the language's (same_algorithm false). In this harness the Sundials C solvers are driven through Sundials.jl wrappers with a Julia right-hand side called back across the C boundary on every function evaluation, and each timed solve includes wrapper setup; on 3-equation problems solved in 20 microseconds to 1 ms this fixed overhead weighs heavily, and the Julia methods also get a StaticArrays out-of-place variant (prob_choice 2) that the C library cannot use. Numbers exist only as plots; the RigidBody page notes that some of the gap depends on each library's error norm. The win is not universal: on the stiff Pollution problem the page's conclusion names Sundials CVODE_BDF the best, and FBDF is only modestly ahead in its high-tolerance plot. Fortran baselines (dopri5, dop853, radau, ODEInterface) are out of scope for a C/C++ baseline. [retier] DiffEqDevTools times solve(prob, alg, sol.u, sol.t, sol.k), which OrdinaryDiffEqCore reuses, while Sundials.jl ignores those arrays, rebuilds the SUNContext, CVodeCreate and NVector on every timed run and drives CVODE in CV_ONE_STEP mode, so the 5-10x figures overstate the C solvers' loss. v7 defaults to AutoSpecialize while the benchmark forces FullSpecialize; the Pollution prose says CVODE_BDF is best while its plot 16_1 shows Rodas5P about 2-3x faster; issue #2586 reports fixed-step implicit methods 70-100x slow.

Julia JIT start-up and package precompilation; wins depend on the Verner high-order Runge-Kutta methods and algorithm-specific interpolation that the C and Fortran codes do not provide.

## Maintenance

Very active (v7.8.1, commits on 2026-10-11, 692 stars, 435 open issues), MIT-licensed and installable with Pkg.add, but useful only from Julia; the v7 release broke keyword APIs (typed autodiff/verbose/alias objects) and DifferentialEquations.jl v8 no longer re-exports Sundials.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README at benchmark_url holds only qualitative summary text, but the linked SciMLBenchmarksOutput pages carry work-precision plots from public jmd code with Julia 1.11.9, package versions (Sundials.jl v6.7.1, Sundials_jll v7.5.0+0) and the CPU (AMD EPYC 7502) in each appendix. The C solvers are BinaryBuilder Sundials_jll builds with no compiler or flags stated and the suite is run by the SciML project on its own solvers, so first-party C, not A or B.
- **Verifier notes:** Keep at C as an algorithm win, not a language win (same_algorithm false, language_level_claim false); benchmark_url moved to the RigidBody output page, which has the plots and the hardware appendix. Shortcomings: first-party, numbers only in plots, C solvers driven through Julia callbacks with wrapper setup inside the timing, Sundials_jll build flags unstated, and the Pollution page names CVODE_BDF the best.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`, `baseline`
- **Shortcomings recorded by:** orchestrator (wave 14 merge); verifier batch-04 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarks.jl/HEAD/README.md>
  - <https://github.com/SciML/OrdinaryDiffEq.jl>
  - <https://github.com/SciML/OrdinaryDiffEq.jl/commits/master>
  - <https://raw.githubusercontent.com/SciML/OrdinaryDiffEq.jl/master/LICENSE.md>
  - <https://github.com/SciML/SciMLBenchmarksOutput/tree/main/markdown/NonStiffODE>
  - <https://github.com/SciML/SciMLBenchmarksOutput/tree/main/markdown/StiffODE>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/NonStiffODE/RigidBody_wpd.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/NonStiffODE/figures/RigidBody_wpd_5_1.png>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/StiffODE/Pollution.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/StiffODE/figures/Pollution_7_1.png>
- **Sources the enricher read:**
  - <https://github.com/SciML/OrdinaryDiffEq.jl>
  - <https://raw.githubusercontent.com/SciML/OrdinaryDiffEq.jl/master/README.md>
  - <https://raw.githubusercontent.com/SciML/OrdinaryDiffEq.jl/master/Project.toml>
  - <https://raw.githubusercontent.com/SciML/OrdinaryDiffEq.jl/master/NEWS.md>
  - <https://raw.githubusercontent.com/SciML/OrdinaryDiffEq.jl/master/lib/DiffEqDevTools/src/benchmark.jl>
  - <https://raw.githubusercontent.com/SciML/OrdinaryDiffEq.jl/master/lib/OrdinaryDiffEqCore/src/solve.jl>
  - <https://raw.githubusercontent.com/SciML/Sundials.jl/master/src/common_interface/solve.jl>
  - <https://raw.githubusercontent.com/rveltz/LSODA.jl/master/README.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarks.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/NonStiffODE/RigidBody_wpd.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/NonStiffODE/figures/RigidBody_wpd_5_1.png>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/StiffODE/Pollution.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/StiffODE/figures/Pollution_16_1.png>
  - <https://github.com/SciML/OrdinaryDiffEq.jl/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance>
  - <https://github.com/SciML/OrdinaryDiffEq.jl/issues/2586>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/sciml/ordinarydiffeq.jl`) · [data/wave14/enrich/raw/github_com_sciml_ordinarydiffeq_jl.json](../../../data/wave14/enrich/raw/github_com_sciml_ordinarydiffeq_jl.json) (enrichment confidence 0.65)

</details>
