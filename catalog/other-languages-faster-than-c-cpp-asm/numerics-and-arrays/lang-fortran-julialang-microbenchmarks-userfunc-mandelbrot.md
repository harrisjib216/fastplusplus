# Fortran (gfortran) in JuliaLang/Microbenchmarks: userfunc_mandelbrot

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Fortran` · `MIT` · 🟢 active

> gfortran complex(dp) Mandelbrot kernel, 1.42x faster than gcc C99 double complex in Julia's 2018 microbenchmarks; reversed in 2026 CI.

| | |
|---|---|
| **Beats** | C version of userfunc_mandelbrot in the same suite (c/perf.c, double complex, gcc 7.3.1 -std=c99, best timing over -O0 through -O3) |
| **Claimed result** | benchmarks.csv at a963d28 (2018, gcc/gfortran 7.3.1): userfunc_mandelbrot C 0.076702 ms, Fortran 0.053836 ms, so Fortran is 1.42x faster than C (derived from page data). The suite's current results (gh-pages dev/benchmarks.csv, generated 2026-04-21, gcc 13.3.0, both at -O2, separate GitHub Actions runners) reverse this: C 0.045061 ms, Fortran 0.05296 ms, so Fortran is 1.18x slower than C. In 2018 Fortran was slower than C on most other benchmarks (derived): matrix_multiply 1.16, matrix_statistics 1.54, recursion_quicksort 1.19, parse_integers 6.88, print_to_file 5.97; iteration_pi_sum 1.00 and recursion_fibonacci 0.99. |
| **Workload** | JuliaLang Microbenchmarks userfunc_mandelbrot: escape-time iteration (maxiter 80, z = z\*z + c) over a 21 x 26 grid of complex points, identical algorithm in every language, serial single core, best-of timing in ms, result checked against a sum of 14791. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-3960X 3.30 GHz, 64 GB DDR3-1600, openSUSE LEAP 15.0, single core (from the Julia benchmarks page) |
| **Compiler and flags** | 2018 run: C with gcc 7.3.1 '\$(CC) -std=c99 -O\$\* perf.c ... -lopenblas \$(LIBM) \$(CFLAGS)' and Fortran with gfortran 7.3.1 '\$(FC) -fexternal-blas -static-libgfortran -O\$\* perf.f90 ... -lopenblas' (Makefile at a963d28). Each language reports the best timing over -O0..-O3, per the julialang.org benchmarks page. Which level won is not published, and CFLAGS inherited from Julia's Make.inc are not visible. Current CI: gcc 13.3.0, both at -O2 (benchmarks/c2.csv and fortran2.csv), in separate ubuntu-latest jobs. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Adoption** | 91 stars (Microbenchmarks); suite behind the julialang.org benchmark page |
| **Last commit** | 2026-04-21 |
| **Links** | [repository](https://github.com/JuliaLang/Microbenchmarks) · [benchmark](https://github.com/JuliaLang/Microbenchmarks/blob/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin/benchmarks.csv) |

## Verdict

The 2018 julialang.org run (Intel i7-3960X, openSUSE LEAP 15.0, gcc/gfortran 7.3.1, best of -O0..-O3 per language, single core) timed the gfortran Mandelbrot grid at 0.0538 ms against 0.0767 ms for the C99 double complex version, 1.42x (derived from page data). The suite's 2026-04-21 GitHub Actions run (gcc/gfortran 13.3.0, -O2, one call per trial) has Fortran 0.0530 ms against C 0.0451 ms, 1.18x slower.

## Use it when

- You already keep scalar complex(dp) kernels in Fortran and want evidence that gfortran's complex arithmetic is not inherently slower than C99 double complex; on gcc/gfortran 7.3.1 it was faster.
- Auditing a C codebase that does tight z\*z + c complex recurrences under -std=c99 without -fcx-limited-range: this row is a hint to time a variant with manual re/im arithmetic or relaxed complex rules (inference; not measured by the suite).
- You need a tiny reproducible cross-language reference kernel (about 40 lines, MIT, with a built-in checksum of 14791) for compiler or language comparisons.
- You are reproducing or citing the dated julialang.org benchmark table and need its exact provenance (CSV at commit a963d28).

## Skip it when

- Picking Fortran over C for speed today: the suite's current run (2026-04-21, gcc and gfortran 13.3.0, both -O2) has Fortran at 0.05296 ms against C at 0.045061 ms, 1.18x slower.
- Inside a C++ project: adopting it means switching language for a 40-line kernel. The C++-side alternatives, std::complex&lt;double&gt; or hand-written re/im arithmetic, were never measured here.
- As evidence that Fortran is generally faster: in the same 2018 run Fortran was slower than C on most other rows (matrix_statistics 1.54x, recursion_quicksort 1.19x, parse_integers 6.88x, print_to_file 5.97x; derived from page data).
- Judging differences of a few microseconds: since March 2026 each trial times one call of about 50 us (5 trials x 3 processes), and the C and Fortran jobs run on separate GitHub Actions VMs.

## How it is fast

The suite gives no mechanism, and none is established. One candidate is complex-multiply semantics. In C99 mode gcc keeps the Annex G rescue for products that come out NaN + I\*NaN (the libgcc __muldc3 path), while gfortran's Fortran rules skip that check. This rests on the GCC option text for -fcx-fortran-rules, quoted in a 2018 gcc-bugs message and seen as a search snippet only. In 2018, C (0.0767 ms) was the outlier: Julia 0.0527, Fortran 0.0538, Rust 0.0576 and Go 0.0597 ms were all faster. In the 2026 CI run, the same C source compiled with gcc 13.3.0 -std=c99 -O2 matches Julia, Go and Swift (about 0.045 ms), and Fortran is the slow one (0.0530 ms). So the rescue check does not explain the gap on current toolchains.

## Compared with alternatives

Against the Julia row of the same suite and run (0.052706 ms, 1.46x over C in 2018, 1.02x behind C in 2026), Fortran and Julia are a statistical tie, so pick whichever language your code already lives in. The Mojo explicit-SIMD Mandelbrot in mojo-analyze (1.6x over scalar C) and the plb2 Fortran matmul rest on code-shape or SIMD differences you can reason about, while this row's gap is a toolchain-era artifact.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the kernel; the full perf.f90 links OpenBLAS (-fexternal-blas -lopenblas) for the matrix rows |
| **Minimum toolchain** | Fortran 2003 (perf.f90 uses the volatile attribute); measured with gfortran 7.3.1 (2018) and gfortran 13.3.0 (2026) |
| **Platforms** | Measured only on x86-64 Linux (Intel i7-3960X in 2018, GitHub ubuntu-latest runners in 2026); the source is portable standard Fortran |
| **Thread safety** | Not documented. The kernel is pure scalar code with no shared state, and the suite runs it serially with OMP/OPENBLAS threads set to 1. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry behind the 2018 number. C timed 100 calls per trial, each mallocing, filling and freeing a 546-int array, plus a sum and assert on the first call. Fortran timed 1000 calls, each adding into a volatile integer. Issue #10 (May 2018) flagged the inconsistency; it was only fixed by PR #100 (March 2026), which moved every language to one call per trial with the C sum and assert outside the timer.
- The Fortran harness gave no protection against hoisting. Issue #58 (March 2022) reported Fortran mandelbrot at 0.000066 ms against C 0.068 with a newer gfortran, which is about one call amortised over the 1000-call loop (0.053 / 1000). The 2018 figure (0.053836 ms, close to Julia's 0.052706) does not look like that artifact, but the constant-input loop could not rule it out (inference). PR #99 later added volatile guards against such elimination.
- The 2026 reversal is also a small-sample result. C times a single \~45 us interval with gettimeofday converted to absolute double seconds, so its 0.045061 ms is exactly 189 x 2^-22 s, i.e. quantised to about 0.24 us on a 1 us clock (derived). Both sides take the minimum of only 15 single-call trials, on different runner VMs.
- The 2018 build flags are only partly known. Each language kept its best of -O0..-O3, and the winning level is not published. Julia v1.0.0's Make.inc sets no CFLAGS and adds -march only when MARCH is set (cross builds), so both binaries were most likely baseline x86-64 SSE2 code (inference; a Make.user override would not be visible). C also linked Julia's static openlibm, which the mandel kernel does not call (cabs2 is hand-written).

## Known shortcomings

- Stale 2018 numbers (gcc 7.3.1, i7-3960X): the suite's current run (gcc 13.3.0, -O2, 2026-04-21) reverses the result with Fortran 1.18x slower than C; the C99-complex inference is no longer supported.
- Harness flaw: the 2018 harness timed different work per language, C running 100 calls with a malloc and free each while Fortran ran 1000 calls into a volatile sum (issue #10 flagged it in 2018; PR #100 fixed it in March 2026). The Fortran loop could be hoisted (issue #58 from 2022 shows newer gfortran at 0.000066 ms); the 2018 number is not that artefact, but the loop is unprotected. The 2026 reversal is also weak: a single about 45 us call per trial, with C's 0.045061 ms exactly 189 x 2^-22 s (gettimeofday quantisation), on separate runner VMs; the mechanism is still unknown.

## Caveats and trade-offs

The 2018 result does not survive the suite's current run. With gcc 13.3.0, both at -O2, the same double-complex C code is faster than Fortran (Fortran 1.18x slower), though C and Fortran now run in separate GitHub Actions jobs on different runner VMs (bench-c, bench-fortran in .github/workflows/benchmarks.yml). In 2018, C was the outlier on this benchmark: Julia 0.052706, Rust 0.057636 and Go 0.059685 ms were also faster than C's 0.076702 ms. The harnesses differ slightly. C runs 5 trials of 100 calls, and each call mallocs, fills and frees a 546-int result array; it sums only the first call. Fortran runs 5 trials of 1000 calls and adds each result to a volatile integer. Both report the minimum per call. The inner escape-time loop is the same (maxiter 80, 21x26 grid, sum 14791). C uses C99 double complex for z\*z+c, while Fortran uses complex(dp) with z\*\*2. The source gives no mechanism. The earlier inference (C99 Annex G complex-multiply checks) is not supported by the 2026 run, where the same C code wins. The data are from the Julia v1.0.0 / gcc 7.3.1 era (2018), and julialang.org itself calls them 'a bit dated'. The win is on one benchmark of eight. [retier] The 2018 harness timed different work per language: C ran 100 calls with a malloc and free each while Fortran ran 1000 calls into a volatile sum (issue #10 flagged it in 2018; PR #100 fixed it in March 2026). The 2026 reversal is also weak: a single about 45 us call per trial with C's 0.045061 ms exactly 189 x 2^-22 s (gettimeofday quantisation), on separate runner VMs. The Fortran loop is unprotected against hoisting (issue #58).

gfortran source uses complex(dp) with z\*\*2 and a hand-written abs2; Fortran I/O and string parsing rows are far slower than C in the same suite.

## Maintenance

The suite is active (last commit 2026-04-21; methodology standardised in PRs #99, #100 and #112 in March 2026) and MIT-licensed, but the 2018 Fortran-over-C result is stale and toolchain-specific, its harness timed different side work per language, and there is nothing to adopt beyond a 40-line kernel.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The CSV at a963d28 shows C 0.076702 ms and Fortran 0.053836 ms. Code (perf.c, perf.f90 at that commit), compiler (gcc/gfortran 7.3.1), flags (Makefile -O\$\*, best of -O0..-O3) and CPU (i7-3960X, per the julialang.org benchmarks page source) are all public, so the 2018 run itself meets A. It is held at C because the suite's own current run (gcc 13.3.0, both at -O2, 2026-04-21) reverses the result: C 0.045061 ms, Fortran 0.05296 ms, Fortran 1.18x slower. The 2018 win is specific to that toolchain, the winning -O level per side is not recorded, and the two harnesses do different side work.
- **Retiered** C to D: Enricher: the 2018 harness timed 100 malloc-and-free C calls against 1000 Fortran calls into a volatile sum (issue #10, fixed by PR #100 in 2026), and the 2026 re-run that reverses the result is a single quantised call per trial on separate VMs; neither measurement is like-for-like: C to D.
- **Verifier notes:** Confirmed at C with a new rationale. The 2018 numbers match and their methodology is fully public, but the suite's current run (gcc 13.3.0, -O2) shows Fortran 1.18x slower than C on the same code, so the claim is stale and toolchain-specific. Recorded the harness differences and dropped support for the C99-complex inference. MIT (LICENSE.md), 91 stars, last commit 2026-04-21, active.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-60 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin/benchmarks.csv>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/Makefile>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perf.c>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perf.f90>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/README.md>
  - <https://raw.githubusercontent.com/JuliaLang/www.julialang.org/main/benchmarks.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/benchmarks/index.html>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/benchmarks.csv>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/c/perf.c>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/fortran/perf.f90>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/Makefile>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/LICENSE.md>
  - <https://github.com/JuliaLang/Microbenchmarks>
  - <https://github.com/JuliaLang/Microbenchmarks/commits>
- **Sources the enricher read:**
  - <https://github.com/JuliaLang/Microbenchmarks/commits/master>
  - <https://github.com/JuliaLang/Microbenchmarks/issues?q=is%3Aissue+mandelbrot>
  - <https://github.com/JuliaLang/Microbenchmarks/issues/10>
  - <https://github.com/JuliaLang/Microbenchmarks/issues/58>
  - <https://github.com/JuliaLang/Microbenchmarks/pull/99>
  - <https://github.com/JuliaLang/Microbenchmarks/pull/100>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/bin/benchmarks.csv>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/Makefile>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perf.c>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/perf.f90>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/a963d284b09d04b3e0374f6dd46ec4b039ed5569/README.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/c/perf.c>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/fortran/perf.f90>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/Makefile>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/README.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/LICENSE.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/benchmarks.csv>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/benchmarks/index.html>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/notes/index.html>
  - <https://raw.githubusercontent.com/JuliaLang/www.julialang.org/main/benchmarks.md>
  - <https://raw.githubusercontent.com/JuliaLang/julia/v1.0.0/Make.inc>
  - https://gcc.gnu.org/pipermail/gcc-bugs/2018-March/618414.html (WebSearch snippet only; gcc.gnu.org did not resolve)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:fortran/julialang/microbenchmarks#userfunc_mandelbrot`) · [data/wave14/enrich/raw/lang_fortran_julialang_microbenchmarks_userfunc_mandelbrot.json](../../../data/wave14/enrich/raw/lang_fortran_julialang_microbenchmarks_userfunc_mandelbrot.json) (enrichment confidence 0.6)

</details>
