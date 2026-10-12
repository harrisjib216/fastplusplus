# juFFTe

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Fortran` · `Apache-2.0` · 🟢 active

> Fortran FFTE rewrite with Spiral-generated RISC-V Vector kernels; its authors report beating FFTW3 on RVV 1.0 chips, but the FFTW comparison is weak.

| | |
|---|---|
| **Beats** | FFTW3 |
| **Claimed result** | Repo README and benchmark README contain no numbers. Preprint arXiv 2608.28076 (seen only through search-result summaries; arxiv.org and pith.science blocked): 'average performance improvements of up to a factor of three depending on hardware' over FFTW3; average multi-core speedups of 1.09x on SiFive X280, 1.91x on SpacemiT K3 (X100 core) and 3.03x on Sophon SG2044 (C920v2, 64 cores). A search summary also says FFTW used FFTW_MEASURE by default but the multi-core K3 and SG2044 comparisons ran FFTW with FFTW_ESTIMATE, disclosed by the authors (not verified against the paper text). |
| **Workload** | 1-D/2-D/3-D complex and real FFTs (double precision in the benchmark) on RISC-V RVV 1.0 CPUs; repo fftbench prints time and MFLOPS and, with WITHFFTW=1, FFTW time. |
| **Metric** | throughput |
| **Hardware** | Not stated in the repo. Per the preprint snippet: SiFive X280, SpacemiT K3 (X100 core), Sophon SG2044 (C920v2 core). |
| **Compiler and flags** | Repo defaults in benchmark/Makefile: gfortran -g -O3 -fopenmp; ifx/ifort -g -O3 -qopt-zmm-usage=high -qopenmp; flang -g -O3 plus -ffast-math -mepi; nvfortran -g -O3. Flags used for the paper runs not seen. |
| **Adoption** | 3 stars, 19 commits; Julich Supercomputing Centre |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/FZJ-JSC/juFFTe) · [benchmark](https://github.com/FZJ-JSC/juFFTe/tree/main/benchmark) |

## Verdict

The numbers are first-party only, from preprint arXiv 2608.28076 (accepted per search snippets to the RISC-V for HPC workshop at ISC26), seen only through search summaries. Against FFTW3, average multi-core speedups are 1.09x on SiFive X280, 1.91x on SpacemiT K3 and 3.03x on Sophon SG2044; single core, juFFTe is 1.53x faster on the X280 but slower on the K3's X100 and the SG2044. The K3 and SG2044 multi-core runs used FFTW_ESTIMATE, as does the repo's benchmark/fftw_m.F90, so the headline gains are against untuned FFTW plans. FFTW version, compilers, flags and sizes were not seen.

## Use it when

- Double-precision 1-D/2-D/3-D FFTs on RVV 1.0 hardware (SiFive X280, SpacemiT K3/X100, Sophon SG2044/C920v2), where FFTW has no vector kernels; per the preprint, juFFTe wins multi-core on all three and single-core on the X280
- Fortran HPC codes that already use FFTE's zfft1d/zfft2d/zfft3d calling convention and want a maintained, Apache-2.0 successor
- Single-plan workloads: one transform size per precision and module, initialized once and executed many times from one thread (with OpenMP inside)
- RISC-V porting and benchmarking work at HPC centers, where you can check correctness at your own sizes before relying on it

## Skip it when

- Any program that needs more than one live plan (e.g. a forward and an inverse plan at different sizes, or several sizes): the work and twiddle arrays are module-level statics, so a second init aborts with 'Attempting to allocate already allocated variable b' or silently reuses stale tables (open issue #7)
- 2-D transforms whose ny has a factor of 3 or 5 (e.g. 64x96, 96x96, 100x100, 120x120): they silently return wrong results (open issue #9, 2026-09-23); whether 3-D and r2c/c2r share the bug is unchecked, and CI only tests size 2 (issue #10)
- As an FFTW drop-in: the C shim is defined in the header (multiple-definition link errors with more than one TU), the backward transform is normalized by 1/n where FFTW's is not, fftw_destroy_plan and fftw_plan_with_nthreads are missing from C, and a second plan breaks the first (open issue #8)
- x86-64 or Arm: no SVE or AVX kernels exist (-DWITHSVE stops at configure time), and no x86 or Arm results are published, so there is no evidence it beats FFTW, MKL or KFR there
- Lengths that are not 2^p 3^q 5^r: factor() just stops at the first other prime and nothing checks this, so these sizes are not rejected (read from the source)

## How it is fast

The kernels follow FFTE: Stockham autosort passes with radix-8/5/4/3/2 butterflies (fft235). Long 1-D transforms (n &gt; 174,762, i.e. L2SIZE/48) switch to a six-step decomposition n = nx\*ny, with NBLK=16 cache-blocked transposes, a twiddle multiply and padding (NP=8) to avoid cache conflicts. The OpenMP loops run over those blocks. With -DWITHRVV=ON the butterflies are swapped for Spiral-generated C kernels using RVV 1.0 intrinsics (src/spiral/rvv: dft2 to dft16, double and single precision), and factor2() chooses radices from {3,4,5,6,8,9,10,12,15,16}. The claimed win comes from explicit RVV vectorization, which upstream FFTW lacks (per the verifier, only an open RVV pull request exists); on x86 and Arm the generic Fortran path relies on compiler autovectorization.

## Compared with alternatives

Pick juFFTe only on RVV 1.0 RISC-V machines, where FFTW lacks vector kernels and none of the catalogued siblings publish RVV results; on x86 or Arm, KFR, PocketFFT or (on AMD) AOCL-FFTW have evidence and none of juFFTe's single-plan or correctness limits.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Fortran runtime (libgfortran or the vendor equivalent) and OpenMP; a C99 compiler for the Spiral/RVV kernels; FFTW3 only for the optional benchmark comparison |
| **Minimum toolchain** | Fortran 2003 compiler (tested with gfortran, nvfortran, Flang and Intel ifx/ifort); CMake 3.15+ or the plain Makefile; a riscv64 cross toolchain with RVV 1.0 support for the vector kernels |
| **Platforms** | Any target with a Fortran compiler (generic kernels); RISC-V RVV 1.0 for the Spiral vector kernels, which are the only accelerated backend |
| **Thread safety** | Not thread-safe across concurrent calls: the 1-D work array and twiddle table (b) and the saved wx/wy tables are module-level and shared, so only one call per module may run at a time (issue #7). Each call parallelizes internally with OpenMP. |
| **Drop-in for the baseline** | partial: the README lists an FFTW-style API, but by issue #8 it has the wrong backward normalization, supports a single plan only, lacks fftw_destroy_plan in C and breaks multi-TU builds, so FFTW code will not work unchanged |

## Gotchas

- In C++, src/juffte.h does not compile at HEAD: it opens one extern "C" { block but closes two braces under __cplusplus, includes &lt;complex.h&gt; inside the extern "C" block and uses double _Complex. It also defines non-static globals (int juffte_init = 0, and FFTW_FORWARD etc. as ints, not macros) in the header (read from the header)
- Each OpenMP thread gets private copies of two fixed-size automatic arrays, about 16.8 MB for c((NDA2+NP)\*NBLK) complex(real64) plus 1 MB for d, in the six-step path; this matches the README's known issue of segfaults unless OMP_STACKSIZE and ulimit -s are raised (size worked out from the source)
- Hard size caps from src/param.F90: 2-D transform length up to 65536 per dimension and 3-D up to 4096 per dimension
- The backward transform scales by 1/n (FFTE convention). Commit 1d91fc8 (2026-09-23) fixed inverted FFT sign constants in the C API and a thread-privacy race in the 2-D work arrays, so the preprint's numbers predate these fixes

## Known shortcomings

- Repo FFTW harness uses FFTW_ESTIMATE, and per the paper snippet the headline K3/SG2044 runs (1.09x/1.91x/3.03x) also use ESTIMATE plans, a weak baseline. Fixes landed after the preprint (2-D work-array thread-privacy race, C sign constants), so the numbers predate correctness fixes.
- Four open issues filed 2026-09-23: #9 2-D results silently wrong when ny has a factor of 3 or 5 (64x96, 96x96, 100x100); #7 only one live plan per module (a second init aborts or reuses stale twiddle tables); #8 FFTW shim broken (backward scaled by 1/n, multiple-definition link errors, missing functions); #10 CI tests only size 2. Not thread-safe. src/juffte.h does not compile as C++ (two closing braces for one extern "C"). Preprint reportedly accepted at the ISC26 RISC-V for HPC workshop, but its numbers use FFTW_ESTIMATE and predate correctness fixes, so the tier stays C.

## Caveats and trade-offs

No result tables in the repo; benchmark/sc.sh listed in benchmark/README.md returns 404. The repo's own FFTW comparison (benchmark/fftw_m.F90) plans every FFTW transform with FFTW_ESTIMATE, FFTW's weakest planner, and a search summary of the preprint says the K3 and SG2044 multi-core runs (the 1.91x and 3.03x headline) also used FFTW_ESTIMATE, so the biggest gains are against untuned FFTW plans. Upstream FFTW has no merged RVV kernels (search shows only an open RVV pull request), so the win may be vectorized code against scalar FFTW. The 3x figure is from a first-party preprint (no peer review confirmed) that could not be opened; compiler and flags for the paper runs are unverified. Commits on 2026-09-23 (after the August 2026 preprint) fixed FFT sign constants in the C API, thread-private allocation of work arrays in 2-D transforms (a likely data race) and an undefined reference in the FFTW benchmark, so the published numbers predate correctness fixes. benchmark/README.md lists segmentation faults in some environments (raise system and OpenMP stack size). Fortran library with a C header (src/juffte.h) and an FFTW-compatible C API, so callable from C/C++ with -lgfortran. Young repo: 19 commits, 3 stars.

Modern Fortran (2003) library with an FFTW-compatible C/Fortran API (fftw_plan_dft_1d, fftw_execute_dft, fftw_malloc), a C header (src/juffte.h) and OpenMP; link needs the Fortran runtime (-lgfortran) from C/C++. Only RVV kernels are generated so far (Spiral backend; the SVE and plain Spiral options stop at configure time). Inspired by FFTE; FFTE's own license terms were not checked.

## Maintenance

Active (initial release 2026-06-25, last commit 2026-09-24, Julich Supercomputing Centre, 3 stars). It is Apache-2.0 and copyable, but four open issues opened on 2026-09-23 (#7 single plan, #8 broken FFTW shim, #9 wrong 2-D results, #10 test suite) make it pre-production.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo has a public FFTW comparison harness (benchmark/fftbench.F90 with fftw_m.F90, built with WITHFFTW=1) but publishes no results; the numbers are in a first-party arXiv preprint (2608.28076) seen only via search summaries, with no confirmed peer review and unverified compiler/flags, so C.
- **Verifier notes:** Metadata confirmed from the repo and commits pages (Apache-2.0, 3 stars, 19 commits, last commit 2026-09-24). Shortcomings worth recording: FFTW baseline planned with FFTW_ESTIMATE in the repo harness (and reportedly for the headline multi-core runs), and post-paper correctness fixes (2-D work-array thread privacy, C sign constants).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/FZJ-JSC/juFFTe>
  - <https://github.com/FZJ-JSC/juFFTe/commits>
  - <https://github.com/FZJ-JSC/juFFTe/tree/main/benchmark>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/README.md>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/benchmark/Makefile>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/benchmark/fftbench.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/benchmark/fftw_m.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/LICENSES/Apache-2.0.txt>
- **Sources the enricher read:**
  - <https://github.com/FZJ-JSC/juFFTe>
  - <https://github.com/FZJ-JSC/juFFTe/commits>
  - <https://github.com/FZJ-JSC/juFFTe/tree/main/src>
  - <https://github.com/FZJ-JSC/juFFTe/tree/main/src/spiral/rvv>
  - <https://github.com/FZJ-JSC/juFFTe/issues?q=is%3Aissue>
  - <https://github.com/FZJ-JSC/juFFTe/issues/7>
  - <https://github.com/FZJ-JSC/juFFTe/issues/8>
  - <https://github.com/FZJ-JSC/juFFTe/issues/9>
  - <https://github.com/FZJ-JSC/juFFTe/issues/10>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/README.md>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/Makefile>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/src/juffte.h>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/src/juffte.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/src/param.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/src/factor_m.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/src/zfft1d_m.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/src/zfft2d_m.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/src/fft235_m.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/src/kernel_m.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/src/utils_m.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/benchmark/README.md>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/benchmark/Makefile>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/benchmark/fftbench.F90>
  - <https://raw.githubusercontent.com/FZJ-JSC/juFFTe/HEAD/benchmark/fftw_m.F90>
  - https://arxiv.org/abs/2608.28076 (not opened; WebSearch snippets only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/fzj-jsc/juffte`) · [data/wave8/enrich/raw/github_com_fzj_jsc_juffte.json](../../../data/wave8/enrich/raw/github_com_fzj_jsc_juffte.json) (enrichment confidence 0.7)

</details>
