# Fortran (gfortran) in fortran-lang/benchmarks: poisson2d (optimized)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Fortran` · `MIT` · 🔴 abandoned

> gfortran -Ofast Jacobi Poisson solver timed 4-9% faster than a C transliteration; the M=100 'win' came from a Fortran precision bug.

| | |
|---|---|
| **Beats** | C (gcc -Ofast) optimized.c: the same Jacobi-iteration Poisson solver on an MxM double grid, written as a line-by-line transliteration of optimized.f90 |
| **Claimed result** | README timings (seconds, one run per cell, June 2021): optimized Fortran 6.25 / 31.4 against optimized C 6.80 / 32.8 for M=200 / 300, about 1.09x and 1.04x faster (derived from page data). The M=100 column (Fortran 0.18 vs C 0.37 s) is invalid: the timed Fortran's single-precision literals halved its sweep count (enricher replay). |
| **Workload** | Jacobi iteration for a 2D Poisson equation (tolerance 1e-6, grid spacing 0.01, two charged squares) on an MxM double-precision grid for M=100, 200 and 300; whole-run time in seconds. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 3600 @ 3.6 GHz, WSL2 on Windows 10 (README) |
| **Compiler and flags** | gfortran sourcefile.f95 -Ofast and gcc sourcefile.c -Ofast (from the README); compiler versions not stated; no -march, LTO or PGO on either side. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Adoption** | 26 stars, 10 forks |
| **Last commit** | 2022-03-05 |
| **Links** | [repository](https://github.com/fortran-lang/benchmarks) · [benchmark](https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/README.md) |

## Verdict

The poisson2d README (June 2021, AMD Ryzen 5 3600 under WSL2, gfortran and gcc -Ofast of unstated versions, one run per cell) gives optimized Fortran 0.18 / 6.25 / 31.4 s against optimized C 0.37 / 6.80 / 32.8 s for M = 100 / 200 / 300. Divided by sweep counts from a numpy replay of the timed code, Fortran is about 2% slower per sweep at M=100 (it did half the sweeps because of a single-precision literal bug) and about 1.10x and 1.05x faster per sweep at M=200 and 300 (derived from page data).

## Use it when

- As a small example that a 5-point stencil written with Fortran fixed-size arrays and array syntax runs at C speed or slightly better under gfortran -Ofast on x86-64 (31-73 us per sweep on a 200x200 to 300x300 grid, Ryzen 5 3600).
- Teaching Jacobi iteration and language overhead: the same directory has pure Python (276 s at M=100), Cython (229 s at M=300) and naive and optimized C and Fortran.
- As a starting point for a fairer benchmark: open PR #26 (fixed sweep count, allocatable arrays on both sides, grids larger than L3) shows what needs changing.

## Skip it when

- As evidence that Fortran beats C: the naive pair goes the other way (naive C about 1.8x faster per sweep at M=200 and 2.1x at M=300, derived from README times and replayed sweep counts), and the optimized margin is 5-10% from one run per cell.
- For real Poisson solves: Jacobi needs O(M^2) sweeps (about 46,000 at M=100 and 427,000 at M=300 in the replay), so a multigrid, FFT or Krylov solver from a maintained library is the practical choice.
- When the grid size is only known at run time: M is a PARAMETER in Fortran and a #define in C, so every size needs a rebuild.
- When your C already uses restrict, static or stack arrays, or a single fused copy-and-max loop: that C variant was never timed, so the gap against it is unknown.

## How it is fast

The repo does not say. Both optimized programs precompute rho into an array and copy one grid per sweep; the Fortran side keeps fixed-size main-program arrays and uses array syntax that gfortran knows cannot alias, while the C side passes heap buffers to non-restrict helpers (a Discourse reply, seen only as a search snippet, says heap allocation cost C a few seconds). Normalised by sweep count from a numpy replay of the code, the timed Fortran was about 1.10x faster per sweep at M=200 and 1.05x at M=300, and about 2% slower at M=100, where the headline 2x came from doing half the sweeps (see gotchas).

## Compared with alternatives

This is the only stencil or PDE data point among the catalogued Fortran rows, but its comparison is weaker than the plb2 Fortran matmul entry (same work verified, tier A, about 6%) and the JuliaLang Microbenchmarks userfunc_mandelbrot row (1.42x). Cite it only as 'at parity within about 10% per sweep', never for the M=100 2x.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond a Fortran compiler and its runtime (gfortran in the README) |
| **Minimum toolchain** | Fortran 90 (modules, kind(0.d0), array syntax); timed with gfortran -Ofast and gcc -Ofast of unstated versions (a June 2021 comment by the README author in PR #23 mentions gfortran-9.3.0) |
| **Platforms** | Timed only on x86-64 (AMD Ryzen 5 3600, WSL2 on Windows 10); portable source |
| **Thread safety** | Not applicable; single-threaded programs with global fixed-size arrays |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the M=100 column: the timed Fortran used single-precision literals a=0.01 and y&lt;0.8 (fixed by PR #30 on 2022-03-05, after the timings; issue #29 is still open). With a = 0.0099999998 both charge squares grow from 19x19 to 20x20 cells and sit exactly antisymmetric about the grid centre at M=100, so the charge has zero projection on the slowest Jacobi mode (computed). A numpy replay of the code then stops after 22,050 sweeps for the timed Fortran against 46,202 for C and 46,316 for the fixed Fortran. That is the README's unexplained 'C did nearly double the iterations': the 0.18 s against 0.37 s compares half the work, and per sweep C was about 2% faster (8.01 against 8.16 us).
- At M=200 and 300 the replay gives the timed Fortran 201,586 and 428,538 sweeps against C's 199,514 and 426,685 (1.0% and 0.4% more work for Fortran, because its charge squares are 400 cells against 361), so the README's 1.09x and 1.04x become about 1.10x and 1.05x per sweep. After the fix, issue #29 (GCC 11.2.0 on Windows, -Ofast, M=100) got 46,337 Fortran and 46,213 C sweeps and 0.453 s against 0.473 s, about 1.05x per sweep, which matches the replay's counts to within 0.05%.
- Even after the fix, the programs solve slightly different problems: C indexes rho(i\*a) from a 0-based boundary and Fortran from a 1-based one, so the squares sit one cell closer to the grounded edge in Fortran (open PR #26 calls this an indexing error). The stopping test is an absolute 1e-6 on potentials of about 1.0e9 to 1.6e9, only about 4 to 8 units in the last place, so -Ofast reordering shifts sweep counts; PR #23 reported a refactored solver that converged at -O0/-O1 but not at -O2, -O3 or -Ofast with gfortran 9.3.0.
- One run per cell, CPU time via clock() and cpu_time over the whole run including setup, and no compiler versions. The Fortran loops run i outer and j inner over column-major arrays (stride M), so its speed relies on GCC's -floop-interchange (on at -O3 and -Ofast) or the hardware prefetcher; this was not checked in assembly.

## Known shortcomings

- Only a 4-9% margin from one run per cell under WSL2 (naive C beats naive Fortran about 2x); no gcc or gfortran versions; the June 2021 timings predate PR #30 (2022-03-05) fixing single-precision literals in both .f90 files, so the timed Fortran solved a slightly different problem; the C and Fortran charge grids sit one cell apart (0-based vs 1-based rho index) and iteration counts are unreported (M=100 C did about 2x iterations); the C baseline keeps arrays in malloc buffers without restrict, so the gap is likely storage and aliasing, not codegen; last commit 2022-03-05.
- Harness flaw behind the M=100 column: the timed Fortran used single-precision literals (a=0.01, y&lt;0.8; fixed by PR #30 on 2022-03-05 after the timings, issue #29 still open), which at M=100 makes both 20x20 charge squares exactly antisymmetric about the grid centre and zeroes the slowest Jacobi mode. A numpy replay of the code stops after 22,050 sweeps for the timed Fortran against 46,202 for C, so the README's 'C did nearly double the iterations' was the Fortran bug and the 0.18 s vs 0.37 s column compares half the work (per sweep C was about 2% faster there). The M=200 and M=300 replays give 201,586 / 428,538 Fortran sweeps vs 199,514 / 426,685 for C, so per sweep Fortran is about 1.10x and 1.05x faster there; issue #29's compiled counts (46,337 / 46,213) match the replay within 0.05%. The 1e-6 stop test is only 4-8 ulps on potentials of about 1e9, and naive C is about 1.8-2.1x faster per sweep than naive Fortran.

## Caveats and trade-offs

The margin is 4-9% on one machine, with a single run per cell under WSL2, and holds only for the hand-optimized pair (rho precomputed into an array, one copy per iteration). In the naive pair, naive C is about twice as fast as naive Fortran, so there is no consistent language-level win. (1) The timings predate PR #30 (Euler-37, merged 2022-03-05, titled 'change the precision problems in fortran files'). That PR changed a=0.01 to a=0.01_dp and y&lt;0.8 to y&lt;0.8_dp in both naive.f90 and optimized.f90. The timed Fortran therefore used a single-precision grid spacing (about 0.0099999998) and charge bound, and solved a slightly different problem from the C code; nobody re-timed after the fix. (2) The two programs do not solve the same instance even after the fix. C fills rhoa[i][j]=rho(i\*a,j\*a) with 0-based i, while Fortran fills rhoarr(i,j)=rho(i\*a,j\*a) with 1-based i, so the charge squares sit one cell apart relative to the grounded boundary and the iteration counts differ. The README gives no iteration counts, only 'approximately the same' for M=200/300 and 'nearly double' for C at M=100. A Discourse reply seen only as a search snippet reported about 320k Fortran against 304k C iterations on a 250x250 grid in an earlier version. A 4-9% margin is within that spread. (3) The C side keeps phi, phip and rhoa in malloc'd pointer-to-array buffers and passes them to out-of-line mmax/swap helpers without restrict. The Fortran side uses static arrays with whole-array assignment and maxval(abs()). A Discourse reply (snippet only) says the C code ran a few seconds slower with heap-allocated arrays. The gap is therefore at least partly a storage choice that C could also make, not a language property. (4) The Fortran loops run i outer and j inner over phiprime(i,j), which is stride-M access in column-major order. Any Fortran win therefore depends on gfortran interchanging the loops (-floop-interchange is part of -O3/-Ofast in GCC 8+), which was not verified. (5) The gcc and gfortran versions are not stated, the last commit is March 2022, and -Ofast enables -ffast-math on both sides. Timing uses clock() in C and cpu_time in Fortran, over the whole run in both. The linked Discourse thread (fortran-lang.discourse.group/t/performance-c-vs-fortran/1461) does not resolve here (ENOTFOUND); what it says was read from search snippets only. [retier] Enricher: the M=100 column is invalid; the timed Fortran used single-precision literals (a=0.01, y&lt;0.8; fixed by PR #30 on 2022-03-05 after the timings, issue #29 still open), which at M=100 makes both 20x20 charge squares exactly antisymmetric about the grid centre and zeroes the slowest Jacobi mode, so a numpy replay stops after 22,050 Fortran sweeps against 46,202 for C; the README's 'C did nearly double the iterations' was this bug, and per sweep C was about 2% faster there. The M=200 and M=300 replays give 201,586 / 428,538 Fortran sweeps vs 199,514 / 426,685 for C, so per sweep Fortran is about 1.10x and 1.05x faster; issue #29's compiled counts match the replay within 0.05%. The 1e-6 stop test is only 4-8 ulps on potentials of about 1e9.

Toy 300x300 static-array Jacobi solver, not a library. Fortran needs gfortran; the repo also carries pure Python and Cython versions (Cython 229 s at M=300 versus 31-34 s for Fortran and C).

## Maintenance

Abandoned: MIT-licensed, 26 stars, 9 commits, last change 2022-03-05 (the PR #30 precision fix); three PRs that rework poisson2d for fairness and verification (#23, #24, #26) have been open since mid-2021, and the README timings were never re-run after the fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The poisson2d/README.md table matches the record exactly (optimized Fortran 0.18 / 6.25 / 31.4 s against optimized C 0.37 / 6.80 / 32.8 s), and the code (optimized.c, optimized.f90), flags (-Ofast on both sides) and CPU (Ryzen 5 3600 under WSL2) are public. It is not A: neither the gcc nor the gfortran version is stated (the vibrato precedent), and the timed Fortran code was changed afterwards by PR #30 (2022-03-05), which fixed single-precision literals; under the later-fixed-code rule that caps it at C. The suite is the Fortran community's own one-person benchmark with one run per cell, so it is not B.
- **Verifier notes:** Numbers verified on the README and all four sources read. Tier C stands (no compiler versions; the timed Fortran was later fixed for single-precision literals by PR #30), and the record is metadata-accurate (MIT, 26 stars, 10 forks, last commit 2022-03-05, abandoned). Shortcomings to record: 4-9% margin from a single run, inside the iteration-count spread; C and Fortran charge grids are offset by one cell; C baseline uses malloc'd buffers without restrict; Fortran loop order is cache-strided unless interchanged; naive C beats naive Fortran by about 2x; timings predate the PR #30 precision fix. Not a duplicate of the plb2 Fortran matmul entry (a different benchmark and suite).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-90 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/README.md>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/optimized.c>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/optimized.f90>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/naive.c>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/naive.f90>
  - <https://github.com/fortran-lang/benchmarks>
  - <https://github.com/fortran-lang/benchmarks/tree/master/poisson2d>
  - <https://github.com/fortran-lang/benchmarks/commits/main>
  - <https://github.com/fortran-lang/benchmarks/pull/30/files>
- **Sources the enricher read:**
  - <https://github.com/fortran-lang/benchmarks>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/README.md>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/optimized.c>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/optimized.f90>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/naive.c>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/HEAD/poisson2d/naive.f90>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/b76fb4a/poisson2d/optimized.f90>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/b76fb4a/poisson2d/naive.f90>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/b76fb4a/poisson2d/optimized.c>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/b76fb4a/poisson2d/naive.c>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/b76fb4a/poisson2d/README.md>
  - <https://raw.githubusercontent.com/fortran-lang/benchmarks/385cb83/poisson2d/optimized.c>
  - <https://github.com/fortran-lang/benchmarks/commits/main/poisson2d>
  - <https://github.com/fortran-lang/benchmarks/issues>
  - <https://github.com/fortran-lang/benchmarks/issues/29>
  - <https://github.com/fortran-lang/benchmarks/pulls>
  - <https://github.com/fortran-lang/benchmarks/pull/23>
  - <https://github.com/fortran-lang/benchmarks/pull/24>
  - <https://github.com/fortran-lang/benchmarks/pull/26>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-13/gcc/doc/invoke.texi>
  - WebSearch snippets for fortran-lang.discourse.group/t/performance-c-vs-fortran/1461 (thread itself not opened)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:fortran/fortran-lang/benchmarks#poisson2d`) · [data/wave14/enrich/raw/lang_fortran_fortran_lang_benchmarks_poisson2d.json](../../../data/wave14/enrich/raw/lang_fortran_fortran_lang_benchmarks_poisson2d.json) (enrichment confidence 0.75)

</details>
