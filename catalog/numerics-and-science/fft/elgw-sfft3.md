# SFFT3 (3-D FFT built from FFTW 1-D transforms)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `GPL-3.0` · 🟡 stale

> 500-line OpenMP 3-D real FFT over FFTW 1-D plans; 1.2-1.3x faster than FFTW 3-D plans on large float volumes.

| | |
|---|---|
| **Beats** | FFTW3 own 3-D routines (FFTW_PATIENT on the Ryzen table, FFTW_MEASURE on the i7 table) |
| **Claimed result** | 8-core Ryzen 3700X, both FFTW_PATIENT: 512^3 8.428e-2 s vs FFTW3-P 1.009e-1 s (1.20x, derived from page data); 1024^3 7.733e-1 vs 1.011 s (1.31x, derived); 1024x1024x256 1.825e-1 vs 2.022e-1 s; 256^3 1.112e-2 vs 1.213e-2 s; slower at 64^3 (1.821e-4 vs 1.185e-4 s) and 128^3 (1.060e-3 vs 7.054e-4 s). 4-core i7-6700K, both FFTW_MEASURE: 512^3 0.182 vs 0.196 s (1.08x, derived), 1024^3 1.640 vs 1.705 s (1.04x, derived), 2048x2048x1024 7.360 vs 8.092 s (run separately with --nofftw/--nosfft); slower at 128^3, 256^3, 512x256x128 and 2100x2100x121. |
| **Workload** | Average time of a forward plus reverse in-place 3-D real FFT in single precision (float, fftw3f), from 64^3 to 2100x2100x121 (and 2048x2048x1024), one OpenMP thread per physical core, padding and planning time excluded; SFFT3 uses FFTW's 1-D routines with cache-blocked transposes and a per-thread workspace. |
| **Metric** | latency |
| **Hardware** | 8-core AMD Ryzen 7 3700X (Ubuntu 24.04.2); 4-core Intel i7-6700K (Ubuntu 22.04.5) |
| **Compiler and flags** | gcc (version not stated), makefile: -O3 -march=native -mtune=native -DNDEBUG -fopenmp -std=gnu11 -fno-schedule-insns, linked with -flto=auto against pkg-config fftw3f and -lfftw3f_omp; i7 run adds CFLAGS=-DSFFT3_L2=256000. FFTW version not stated (Ubuntu system package via pkg-config). |
| **Adoption** | 0 stars |
| **Last commit** | 2025-08-29 |
| **Links** | [repository](https://github.com/elgw/sfft3) · [benchmark](https://raw.githubusercontent.com/elgw/sfft3/HEAD/README.md) |

## Verdict

The author's test_sfft3.c times SFFT3 against fftwf_plan_dft_r2c_3d/c2r_3d in one binary, single precision, one OpenMP thread per physical core, planning and padding excluded. Build: gcc -O3 -march=native -fopenmp -flto=auto; gcc and FFTW versions not stated. It won by 1.20x at 512^3 and 1.31x at 1024^3 on a Ryzen 7 3700X (both PATIENT) and by 1.01-1.10x at its winning sizes on an i7-6700K (both MEASURE), and lost at small sizes. The printed figure is the mean of one forward and one inverse transform, not the pair sum. The harness never renormalizes between round trips, so the timed data overflow to inf/NaN for both libraries alike.

## Use it when

- Large float 3-D real FFTs (about 256^3 and up) on multi-core x86 where FFTW's own 3-D plan is the bottleneck: 8-core Ryzen 3700X, both FFTW_PATIENT, 512^3 1.20x and 1024^3 1.31x (derived from README data)
- Codes already built around FFTW's padded in-place r2c/c2r layout that only need forward/inverse 3-D transforms, e.g. FFT convolution of large volumes
- As a starting point for your own 3-D driver: the author says switching the 1-D backend from FFTW needs relatively small changes
- GPL-compatible projects that already link FFTW

## Skip it when

- Small volumes: 64^3 and 128^3 were 1.54x and 1.50x slower than FFTW_PATIENT on the Ryzen, and 128^3 was 1.79x slower on the i7-6700K (derived from README data)
- Hardware you have not measured yourself: on the 4-core i7-6700K with FFTW_MEASURE it lost at 4 of 9 sizes (including 2100x2100x121) and won by only 1-10% elsewhere; the author does not expect the results to generalize
- Double precision, complex input, 1-D/2-D, out-of-place or batched transforms: only in-place float 3-D r2c/c2r exists
- Memory-tight or overcommit-disabled systems: it uses more workspace than FFTW's 3-D plans and, through a sizing bug, requests far more than it uses
- Production code: the author calls it an untested proof of concept with nothing more planned, and FFTW plus GPL-3.0 rule out closed-source use

## How it is fast

Row-column decomposition with cache-blocked transposes. For each XY plane it runs r2c along the contiguous X lines. It then copies a group of Y lines, sized to fit in L2, into a per-thread workspace through a 32x32 stack tile sized for L1. There it runs contiguous unit-stride FFTW 1-D c2c transforms and transposes the result back; the Z axis is done the same way over XZ planes. OpenMP parallelizes over planes with single-threaded FFTW plans, so every 1-D FFT runs on contiguous cache-resident data rather than strided memory.

## Compared with alternatives

Pick it over FFTW's own 3-D plans only for large float r2c volumes on multi-core x86, after measuring on your machine, and only if you can spare a per-thread plane buffer. Admiral reports a larger N-D margin over FFTW_MEASURE and PocketFFT avoids FFTW's GPL, so look at those first if you are not tied to FFTW.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | FFTW3 single precision (fftw3f via pkg-config; the makefile also links -lfftw3f_omp) and OpenMP |
| **Minimum toolchain** | C11 with GNU extensions (makefile uses -std=gnu11; code uses VLAs and __attribute__((aligned))) plus OpenMP; built with gcc, and the README says clang also works |
| **Platforms** | Any platform with FFTW3 and OpenMP. Its own code has no explicit SIMD; measured only on x86-64 Linux (Ryzen 7 3700X, i7-6700K). |
| **Thread safety** | Not documented. A plan owns one shared workspace, so concurrent execute calls on the same plan race. sfft3_create_plan runs the FFTW planner and calls fftwf_plan_with_nthreads(1), a process-wide FFTW setting. |
| **Drop-in for the baseline** | partial — same padded in-place data layout as fftwf_plan_dft_r2c_3d/c2r_3d, but its own plan/execute API, float only, with dimensions given contiguous-first (sfft3_create_plan(M,N,P) matches fftwf_plan_dft_r2c_3d(P,N,M)) |

## Gotchas

- Do not set plan-&gt;scale = 1: the normalization loop in sfft3_execute_dft_c2r treats the padded array as dense M\*N\*P floats. It scales padding slots and leaves the tail of the array unscaled. Keep the default (0) and normalize the real elements yourself.
- sfft3_create_plan calloc()s threads^2 x max(M\*N\*4, M\*P\*8) x 8 bytes (4 GiB of virtual memory for 1024^3 with 8 threads), while execution touches only about (M/2+1) x max(N,P) x 8 bytes per thread. This works only with lazy zero-page allocation.
- Release builds use -DNDEBUG, which removes the assert() checks on plan and workspace allocation, so an allocation failure crashes instead of reporting an error
- L1/L2 block sizes are compile-time macros (SFFT3_L1=64000, SFFT3_L2=512000 bytes) with no autotuning; the i7 results needed -DSFFT3_L2=256000

## Known shortcomings

- Single precision only; larger workspace than FFTW; slower at 4 of 9 i7 sizes.
- Correctness bug: with plan-&gt;scale=1, sfft3_execute_dft_c2r treats the padded array as dense M\*N\*P floats, scaling padding and leaving the tail unscaled. sfft3_create_plan calloc()s threads^2 x max(M\*N\*4, M\*P\*8) x 8 bytes (4 GiB virtual for 1024^3 on 8 threads). Harness flaws: the timed loop never renormalizes, so data overflow to inf/NaN for both libraries; warmup passes the r2c plan to fftwf_execute_dft_c2r. Reported time is the mean of one forward and one inverse; ratios still hold.

## Caveats and trade-offs

The author calls it an untested proof of concept, run on two similar machines, and does not expect the results to generalize. Wins are 4-31% on large cubes, with losses at small sizes (and at four of nine sizes on the i7). SFFT3 uses a larger workspace than FFTW's 3-D routines, which the author says makes the timings not directly comparable. Single precision only. The gcc and FFTW versions are not stated. The README says it linked -lfftw3d_omp, but the makefile links -lfftw3f_omp.

Not an independent FFT: it calls FFTW3 for every 1-D transform (GPL). Uses a larger workspace than FFTW's 3-D plans (author says timings are not directly comparable). No explicit vectorization, no auto-tuning; L1/L2 sizes are compile-time constants.

## Maintenance

Stale proof of concept (18 commits, last 2025-08-29, 0 stars, no issues; the author says nothing more is planned). GPL-3.0 and about 660 lines over FFTW, so easy to vendor into GPL code and fix yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The README tables come from the public test_sfft3.c, which times SFFT3 against FFTW's own fftwf_plan_dft_r2c_3d/c2r_3d in one binary, with the exact command lines shown. The makefile gives the compiler and flags (gcc -O3 -march=native -mtune=native -fopenmp -flto=auto -fno-schedule-insns), and both CPUs are named (Ryzen 7 3700X, i7-6700K). The gcc and FFTW versions are not stated.
- **Verifier notes:** Numbers verified. GPL-3.0, 0 stars, last commit 2025-08-29, stale, all confirmed. Upgraded to A on the makefile-plus-named-CPU precedent; single precision added to workload.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/elgw/sfft3/HEAD/README.md>
  - <https://raw.githubusercontent.com/elgw/sfft3/HEAD/makefile>
  - <https://raw.githubusercontent.com/elgw/sfft3/HEAD/test_sfft3.c>
  - <https://github.com/elgw/sfft3>
  - <https://github.com/elgw/sfft3/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/elgw/sfft3/HEAD/README.md>
  - <https://raw.githubusercontent.com/elgw/sfft3/HEAD/makefile>
  - <https://raw.githubusercontent.com/elgw/sfft3/HEAD/sfft3.h>
  - <https://raw.githubusercontent.com/elgw/sfft3/HEAD/sfft3.c>
  - <https://raw.githubusercontent.com/elgw/sfft3/HEAD/test_sfft3.c>
  - <https://github.com/elgw/sfft3>
  - <https://github.com/elgw/sfft3/issues?q=is%3Aissue>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/elgw/sfft3`) · [data/wave8/enrich/raw/github_com_elgw_sfft3.json](../../../data/wave8/enrich/raw/github_com_elgw_sfft3.json) (enrichment confidence 0.75)

</details>
