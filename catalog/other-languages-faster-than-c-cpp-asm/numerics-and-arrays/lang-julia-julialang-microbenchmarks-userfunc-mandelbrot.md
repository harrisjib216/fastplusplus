# Julia in JuliaLang/Microbenchmarks: userfunc_mandelbrot

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Julia` · `MIT` · 🟢 active

> Julia's scalar Complex{Float64} Mandelbrot loop in the official Julia microbenchmarks; 1.46x faster than C in 2018 data, a tie today.

| | |
|---|---|
| **Beats** | C version of userfunc_mandelbrot in the same suite (perf.c at the repo root at commit a963d28, now c/perf.c; C99 double complex). Built with gcc 7.3.1 -std=c99 -O\$N for N = 0..3; bin/collect.jl keeps the minimum over all four builds and 5 runs each. |
| **Claimed result** | benchmarks.csv (Julia v1.0.0 era data): userfunc_mandelbrot C 0.076702 ms, Julia 0.052706 ms (1.46x faster than C, derived from page data). Historical only: the project's current results (2026-04-21, gcc 13.3.0 -O2, Julia 1.12.6) give C 0.045061 ms vs Julia 0.045765 ms, parity (derived from page data). |
| **Workload** | JuliaLang Microbenchmarks userfunc_mandelbrot: escape-time iteration (maxiter 80, z = z\*z + c) over a 21 x 26 grid of complex points, identical algorithm in every language, serial single core, best-of timing in ms, result checked against a sum of 14791. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-3960X 3.30 GHz, 64 GB DDR3-1600, openSUSE LEAP 15.0, single core (from the julialang.org benchmarks page, seen only as a search snippet because the host did not resolve here) |
| **Compiler and flags** | C: gcc 7.3.1 -std=c99 -O\$N for N = 0..3 plus Julia's Make.inc CFLAGS, linked with OpenBLAS and openlibm; bin/collect.jl takes the best time over all levels and runs. No -march=native, no -ffast-math or -fcx-limited-range. Julia v1.0.0 default optimisation (-O2, JIT for the host CPU), compile time excluded. Compiler and Julia versions are from julialang.org/benchmarks (search snippet only). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 91 stars (Microbenchmarks); suite behind the julialang.org benchmark page |
| **Last commit** | 2026-04-21 |
| **Links** | [repository](https://github.com/JuliaLang/Microbenchmarks) · [benchmark](https://github.com/JuliaLang/Microbenchmarks/blob/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin/benchmarks.csv) |

## Verdict

In the Julia 1.0-era bin/benchmarks.csv, userfunc_mandelbrot took 0.076702 ms in C (gcc 7.3.1 -std=c99, best of -O0..-O3, 100-call averages) and 0.052706 ms in Julia (minimum single call), about 1.46x faster, on an i7-3960X per julialang.org. The project's current GitHub Actions run (gcc 13.3.0 -O2, Julia 1.12.6, one call per sample for all languages) shows a tie: C 0.045061 ms, Julia 0.045765 ms.

## Use it when

- As evidence that scalar complex-number loops written naturally in Julia (Complex{Float64}, z^2 + c, array comprehension) run at C speed, so such kernels need not be rewritten in C.
- When prototyping small numeric kernels (iteration counts, escape-time fractals, per-point complex maps) where JIT warm-up is paid once and the kernel runs many times.
- As a ready harness (Makefile plus GitHub Actions workflow) to compare Julia against C, Fortran, Rust, Go, Swift and others on your own machine, with the identical algorithm in every language.

## Skip it when

- As proof that Julia is 1.46x faster than C: the project's current CI page (generated 2026-04-21, GitHub Actions ubuntu-latest, gcc 13.3.0 -O2, Julia 1.12.6) has C 0.045061 ms vs Julia 0.045765 ms (Julia 1.016x of C time), and a 2022 CI run posted in issue #48 had C 0.08167 vs Julia 0.0796.
- As evidence across the suite: in the current data Julia is behind C on all eight benchmarks (from 1.016x on mandelbrot and 1.03x on BLAS matmul to 3.1x on recursive fibonacci, derived from page data).
- When you need a faster Mandelbrot than scalar C: neither side vectorizes across points, so explicit SIMD or GPU code is the lever, not the language.
- For one-shot or start-up-sensitive runs: the timings exclude Julia start-up and the JIT compilation of mandel and the comprehension.
- With -ffast-math expectations: neither the C build (no -ffast-math, -fcx-limited-range or -march) nor Julia uses relaxed floating point, so this row says nothing about fast-math code.

## How it is fast

No special technique: Julia type-infers the loop to Complex{Float64}, inlines z^2 into a plain (ac - bd, ad + bc) multiply, and LLVM emits a scalar loop for the host CPU after JIT compilation (excluded from timing). The source gives no reason for the 2018 gap. In the 2018 table C was slower than every compiled language on this row (Julia 0.687, Fortran 0.702, Rust 0.751, Go 0.778 of C time, derived), which fits the verifier's reading that gcc 7.3.1's C99 Annex G complex multiply (NaN check with a __muldc3 fallback) cost C time. The same C source ties Julia when built with gcc 13.3.0, so that cost was specific to the old toolchain or CPU.

## Compared with alternatives

Its Fortran twin (same suite, 1.42x in the same 2018 table) shares every caveat here, and the Mojo SIMD Mandelbrot sibling is an explicit vectorization win against scalar C rather than a like-for-like comparison. Cite this entry only for 'Julia's scalar complex loop matches C'; for a measured win, look elsewhere in the catalog.

## Integration

| | |
|---|---|
| **Form** | source-drop (benchmark script julia/perf.jl; the mandelbrot part is about 20 lines) |
| **Dependencies** | none for the mandelbrot kernel (Base Julia); the full suite needs OpenBLAS, dSFMT 2.2.4 for C, and Test, Printf, Random, Statistics, LinearAlgebra stdlibs |
| **Minimum toolchain** | Julia 1.0 for the 2018 data (perf.jl then used Compat); current perf.jl runs on Julia 1.x ('v1' in CI, 1.12.6 in the 2026-04-21 run); C side gcc -std=c99 |
| **Platforms** | any Julia platform; published numbers are x86-64 only (i7-3960X for 2018 per julialang.org snippet, GitHub Actions runners now) |
| **Thread safety** | not applicable (serial single-core benchmark; CI sets JULIA_NUM_THREADS=1) |
| **Drop-in for the baseline** | no |

## Gotchas

- The 2018 harness was not symmetric: C timed 100 back-to-back mandelperf() calls per sample and divided by 100, kept the best over -O0..-O3 builds and 5 runs each, while Julia's old perfutil.jl @timeit timed single calls in a loop until at least 5 trials and 2000 ms had accumulated and reported the minimum single call. Issue #10 (2018-05-21) flagged the differing repetition counts and sum/assert inclusion; PR #100 (2026-03-02) standardized every language to one call per timed sample.
- The 1.46x does not reproduce in the project's own current data (C 0.045061 vs Julia 0.045765 ms on 2026-04-21), so the win is a property of the 2018 toolchain, CPU or harness, not of Julia codegen.
- The verifier's tie-breaker (gfortran on the same gcc matched Julia in 2018) does not hold today: gfortran 13.3.0 is 1.18x slower than C on this row in the 2026 data (0.05296 ms), and the Fortran mandelperf does less work (it sums into a volatile scalar instead of filling an array).
- bin/benchmarks.csv (Julia 1.0-era data, added in 2022 by #65) carries no versions or hardware; gcc 7.3.1, Julia 1.0.0 and the i7-3960X come only from the julialang.org/benchmarks page. Julia's Make.inc v1.0.0 defines JCFLAGS, not CFLAGS, and adds -march only when MARCH is set, so the C build most likely had no -march.

## Known shortcomings

- Hardware and gcc 7.3.1 seen in a search snippet only (julialang.org unreachable); the win is likely the C99 complex-multiply NaN check since gfortran on the same GCC (0.053836 ms) ties Julia (0.052706 vs C 0.076702 ms), so not a codegen win; matrix_multiply and quicksort are marginal ties.
- Harness asymmetry and no reproduction: the 2018 C harness timed 100 back-to-back calls per sample and kept the best over -O0..-O3 builds while Julia's old perfutil reported the minimum single call over a loop of at least 2000 ms (issue #10; PR #100 of 2026-03-02 standardised every language to one call per sample). The project's own current results (gh-pages dev/benchmarks.csv, 2026-04-21, gcc 13.3.0 -O2, Julia 1.12.6) give C 0.045061 ms vs Julia 0.045765 ms, a tie (Julia 1.016x the C time), and the 2022 CI in issue #48 gave C 0.08167 vs Julia 0.0796. The verifier's gfortran tie-breaker no longer holds either: gfortran 13.3.0 takes 0.05296 ms, 1.18x slower than C. Retiered to D as a historical 2018 result that now reads as parity.

## Caveats and trade-offs

The only clear Julia win of the eight benchmarks: Julia is also nominally ahead on matrix_multiply (0.975 of C time, both call OpenBLAS) and recursion_quicksort (0.997), but those are ties (derived from page data). The data is from the Julia 1.0.0 era (gcc 7.3.1, 2012 CPU) and was added to the repo as 'add original benchmarks.csv data (#65)' in 2022. Current CI results sit on julialang.github.io (blocked here). The source gives no mechanism. Reading the code, the C version multiplies C99 double complex values (z\*z+c) without -ffast-math or -fcx-limited-range. GCC then adds a NaN check after each complex multiply, with a __muldc3 recovery call on the slow path, as C99 Annex G requires. Julia's z^2 and Fortran's complex multiply use the plain formula without that check (GCC applies Fortran rules to gfortran). gfortran, which uses the same gcc 7.3.1 backend and the same algorithm, runs in 0.053836 ms, matching Julia's 0.052706 ms (derived from page data). That points to C's complex-arithmetic semantics rather than better Julia codegen. The C build has no -march=native, while Julia JITs for the host CPU; this probably does not matter here because the i7-3960X has no FMA. Both sides allocate the 21x26 result array on each call (C malloc/free, Julia comprehension). The Rust (0.75 of C time) and Go (0.78) rows of the same benchmark also beat C and are not recorded here. [retier] Enricher: the 2018 harness was not symmetric (C timed 100 back-to-back mandelperf() calls per sample and kept the best over -O0..-O3 builds and 5 runs, Julia's old perfutil reported the minimum single call over a loop of at least 2000 ms; issue #10, fixed suite-wide by PR #100 on 2026-03-02). The 1.46x does not reproduce in the project's own current data: gh-pages dev/benchmarks.csv (2026-04-21, gcc 13.3.0 -O2, Julia 1.12.6) gives C 0.045061 vs Julia 0.045765 ms, a tie (Julia 1.016x the C time), and the 2022 CI in issue #48 gave C 0.08167 vs Julia 0.0796; gfortran 13.3.0 takes 0.05296 ms, 1.18x slower than C.

Julia is JIT compiled; the timings exclude compile time and Julia start-up. Only a micro benchmark of 546 grid points.

## Maintenance

Actively maintained by the Julia project (MIT; CI restructured in March 2026, results page rebuilt 2026-04-21), but its own current data shows parity with C on this row, so the catalogued 1.46x is a historical 2018 result that should be read as at best a tie.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** bin/benchmarks.csv at a963d28 has c,userfunc_mandelbrot 0.076702 and julia 0.052706 ms, and the code (perf.c, perf.jl, Makefile, bin/collect.jl) is public. The suite is the Julia project's own (first-party). The CSV carries no compiler or hardware metadata (versions.csv is absent at that commit), and gcc 7.3.1, Julia 1.0.0 and the i7-3960X come from julialang.org/benchmarks, which did not resolve here and was read only as a search snippet. The win most likely comes from C99 complex-multiply semantics, so it stays at C.
- **Retiered** C to D: Downgraded from C to D: the 2018 harness was asymmetric (C timed 100-call means and kept the best of -O0..-O3 builds, Julia reported the minimum single call; issue #10, standardised only by PR #100 on 2026-03-02) and the project's own current results show parity (C 0.045061 vs Julia 0.045765 ms on 2026-04-21 with gcc 13.3.0 -O2 and Julia 1.12.6; 2022 CI C 0.08167 vs Julia 0.0796), while the verifier's gfortran tie-breaker now runs 1.18x slower than C (0.05296 ms). Same ruling as the Fortran sibling row: a historical result that no longer reproduces.
- **Verifier notes:** Numbers verified on the pinned benchmarks.csv; tier C kept. Shortcomings for the decision record: first-party suite with data from 2018; hardware and compiler details seen only in a search snippet; the 1.46x win tracks C99 complex-multiply semantics (gfortran on the same GCC ties Julia), so it is not a language codegen win; it is one benchmark of eight.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-61 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/JuliaLang/Microbenchmarks>
  - <https://github.com/JuliaLang/Microbenchmarks/commits/master>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin/benchmarks.csv>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perf.c>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perf.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perf.f90>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/Makefile>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/README.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin/collect.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin/benchmarks.ipynb>
  - <https://github.com/JuliaLang/Microbenchmarks/tree/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin>
  - <https://github.com/JuliaLang/Microbenchmarks/commits/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin/benchmarks.csv>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/c/perf.c>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/Makefile>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/LICENSE.md>
- **Sources the enricher read:**
  - <https://github.com/JuliaLang/Microbenchmarks>
  - <https://github.com/JuliaLang/Microbenchmarks/commits/master/c/perf.c>
  - <https://github.com/JuliaLang/Microbenchmarks/issues?q=mandelbrot>
  - <https://github.com/JuliaLang/Microbenchmarks/issues/10>
  - <https://github.com/JuliaLang/Microbenchmarks/issues/48>
  - <https://github.com/JuliaLang/Microbenchmarks/issues/79>
  - <https://github.com/JuliaLang/Microbenchmarks/pull/100>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/README.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/Makefile>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perf.c>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perf.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perf.f90>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perfutil.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin/collect.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin/benchmarks.csv>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/Makefile>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/c/perf.c>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/julia/perf.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/fortran/perf.f90>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/rust/src/main.rs>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/go/perf.go>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/bin/collect.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/bin/benchmarks.csv>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/bin/versions.sh>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/bin/table.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/docs/make.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/docs/src/index.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/HEAD/docs/src/notes.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/benchmarks.csv>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/benchmarks/index.html>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/index.html>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/versions.js>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.0.0/Make.inc>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:julia/julialang/microbenchmarks#userfunc_mandelbrot`) · [data/wave14/enrich/raw/lang_julia_julialang_microbenchmarks_userfunc_mandelbrot.json](../../../data/wave14/enrich/raw/lang_julia_julialang_microbenchmarks_userfunc_mandelbrot.json) (enrichment confidence 0.75)

</details>
