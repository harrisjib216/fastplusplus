# mpFFT (multiprecision FFT on MPFR)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> Research-grade MPFR-based split-radix FFT in C that runs faster than Mathematica and MATLAB/Advanpix multiprecision FFTs.

| | |
|---|---|
| **Beats** | Mathematica 11.1 FFT with SetPrecision, and MATLAB 2019a with the Advanpix Multiprecision Toolbox (mp.Digits) |
| **Claimed result** | README: 'a more than 2x speed-up to Mathematica and a 10x speed-up to MATLAB' (Advanpix toolbox) in serial computation with precision up to 1 million digits, and 'a 10x speed-up to MATLAB' with 4 CPU cores at high precision; no Mathematica multicore comparison. Approximate values read from the log-scale plots (derived from page data): serial at 1,048,576 digits mpFFT about 110 s versus Mathematica about 250 s and MATLAB about 1,300 s per FFT; at 16 digits mpFFT about 0.00085 s versus MATLAB about 0.0016 s and Mathematica about 0.011 s, so the MATLAB gap is only about 2x at low precision; 4 cores at 1,048,576 digits mpFFT about 36 s versus MATLAB about 380 s. |
| **Workload** | Serial 1D complex FFT of length 1024 (random input) at 16 up to 1,048,576 decimal digits on one CPU core, and the same on 4 cores, measured as average seconds per FFT. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-6500 at 3.20 GHz (read from the benchmark plot title) |
| **Compiler and flags** | gcc 9.3.0 with -O3, statically linked MPFR 4.1.0, GMP 6.2.1, -pthread -fopenmp for parallel runs |
| **Adoption** | 3 stars, 1 fork, a single commit |
| **Last commit** | 2021-10-10 |
| **Links** | [repository](https://github.com/mfrewer/mpFFT) · [benchmark](https://github.com/mfrewer/mpFFT) |

## Verdict

First-party plots on one Intel Core i5-6500 inside an Ubuntu 20.04 VMware Workstation VM (gcc 9.3.0 -O3, static MPFR 4.1.0 / GMP 6.2.1) time the kernel alone for a length-1024 random complex FFT: serially at 1,048,576 digits about 110 s versus about 250 s for Mathematica 11.1 and about 1,300 s for MATLAB 2019a with Advanpix, narrowing to about 2x over MATLAB at 16 digits; at fixed 1024 digits it is about 3x faster than both across lengths 16 to 1,048,576, and on 4 cores about 2-3x faster than MATLAB/Advanpix (all values read from log-scale plots, derived from page data). Baseline scripts are not in the repository, so the comparison cannot be rerun from it.

## Use it when

- You need a forward complex FFT at hundreds to about a million decimal digits in C and currently call Mathematica or MATLAB with the Advanpix toolbox for it.
- Power-of-two lengths from 16 to about 1M points at fixed high precision (the dP = 1024 plots show it about 3x ahead of both baselines across that whole range).
- You already hold data as mpfr_t and want a small, readable split-radix kernel to vendor and adapt (Apache-2.0).
- Studying multiprecision FFT design trade-offs: the lab/ tree keeps several kernel variants, complexity counters and an inverse-FFT error test.

## Skip it when

- You need a library API: there is no init/plan/execute interface, N and P are #defines, and state is global, so each size/precision is a recompile.
- Non-power-of-two lengths, real-input, inverse or multidimensional transforms: none are implemented (the README only describes how they could be derived).
- You need rigorous error bounds or arbitrary lengths: FLINT's acb_dft does ball arithmetic and supports any length (naive, CRT, cyclic, radix-2, Bluestein).
- Precision near double-double or quad-double (about 32-64 digits): at 16 digits mpFFT is only about 2x ahead of MATLAB/Advanpix in its own plot, and hardware-double-based formats are a better fit there.
- Production use: single 2021 commit, self-described as 'still in development and far from complete', no tests or CI, no open issues or releases.

## How it is fast

It cuts the number of multiprecision multiplications, which dominate cost at high precision: a recursive decimation-in-time conjugate-pair split-radix-2/4 FFT (Yavne / Duhamel-Hollmann family) with the 3-multiply/3-add complex product (3m3a) using precomputed cos, cos+sin and cos-sin twiddle tables, hard-coded n = 1, 2, 4 base cases and a special butterfly at k = n/8; at P = 1024 bits, N = 1024 the 3m3a scheme drops multiplications from 9,336 to 7,172 and time from 3.32 ms to 3.02 ms (lab OPTIONS.md). The recursive depth-first order removes the bit-reversal pass and keeps the working set local. The parallel version only splits the inner butterfly loop of each recursion level (n &gt;= 16) across 4 OpenMP threads; all arithmetic is plain MPFR calls, so per-operation speed is MPFR's.

## Compared with alternatives

Pick it over FLINT's acb_dft when you only need a plain power-of-two forward FFT on mpfr_t values and want MPFR semantics rather than ball arithmetic, accepting that no head-to-head with FLINT exists. Unlike MPLAPACK or APFP, which speed up multiprecision linear algebra, it is the only catalogued entry aimed at the FFT itself.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | MPFR (4.1.0 used; mpfr_get_str_ndigits needs 4.1+), GMP (6.2.1 used), libm; OpenMP and pthread for the parallel kernel; MPFR must be built with --enable-thread-safe for parallel runs |
| **Minimum toolchain** | C with GCC; only gcc 9.3.0 -O3 is documented |
| **Platforms** | POSIX (uses clock_gettime(CLOCK_MONOTONIC)); tested only on an Intel Core i5-6500; others not documented |
| **Thread safety** | Not reentrant: twiddle tables, input/output arrays and the serial kernel's temporaries are file-scope statics, so only one transform can run per process; the parallel kernel uses per-thread temporaries inside its own OpenMP regions. |
| **Drop-in for the baseline** | no |

## Gotchas

- The shipped mpFFT.c defaults are not the benchmark configuration: CC = 1 turns on operation counters (inside '#pragma omp critical' in the parallel kernel), CH = 1 runs an O(N^2) double-precision DFT check, IN = 2 uses a fixed input rather than the random input in the plots, and M = 1; set CC 0 and CH 0 before timing.
- Benchmarks time the FFT kernel only; building the twiddle table (N/4 mpfr_cos and mpfr_sin calls at full precision) and allocation are excluded and can dominate a one-off transform at high precision.
- The parallel kernel hard-codes num_threads(4) and opens a new OpenMP region (with fresh mpfr_inits2 temporaries) at every recursion level with n &gt;= 16; the author notes at best about 3x on 4 cores because only the inner loop is parallel.
- Conjugate-pair recursion indexes the input through negative offsets (inr - s, wrapped by s0 = N), so the input arrays must follow the exact layout the kernel expects.

## Known shortcomings

- MATLAB gap only about 2x at low precision, 10x at high (read from plots); no Mathematica/MATLAB scripts in the repo.
- Benchmarks ran inside a VMware VM; the shipped mpFFT.c is not configured as benchmarked (operation counters on, O(N^2) DFT check on, fixed input); a program, not a library (compile-time length/precision, global state, not thread-safe); timings exclude twiddle-table construction.

## Caveats and trade-offs

Baselines are proprietary systems (Mathematica 11.1, MATLAB 2019a with Advanpix) and the repository holds no scripts for them (bench/ contains only PNG plots), so the comparison cannot be reproduced from the repo; the speedups are first-party and read from plots. The 10x over MATLAB holds at high precision; at 16-128 digits the gap is roughly 2x. Single i5-6500 machine, 2021 versions. Source code is Apache-2.0; the README states the project content (documentation) is CC BY 4.0. Self-described as 'still in development and far from complete'; the repository has a single commit (2021-10-10). Overlaps the FFT category; kept here because it is a multiprecision (MPFR-based) FFT.

1D complex-to-complex, forward-only, power-of-two lengths, DIT split-radix, recursive, out-of-place, scalar code; all arithmetic comes from MPFR, so it does not beat MPFR, it beats Mathematica and Advanpix at the FFT level; the author calls the project 'still in development and far from complete'.

## Maintenance

Abandoned after a single commit on 2021-10-10, but the code is Apache-2.0 (docs CC BY 4.0) and the kernel is small enough to vendor and adapt.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party plots (bench/serial_mp_N1024_time.png, bench/parallel_mp_C4_N1024_time.png) with gcc 9.3.0 -O3, MPFR 4.1.0/GMP 6.2.1 and an i5-6500 stated, but the Mathematica and MATLAB/Advanpix baseline scripts are not in the repository (bench/ holds only PNG plots) and there is no peer review, so C.
- **Verifier notes:** README and plots match the record; last_commit 2021-10-10 is confirmed by the commits page (single 'initial commit'). Plot readings are approximate and labelled as derived.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/README.md>
  - <https://github.com/mfrewer/mpFFT>
  - <https://github.com/mfrewer/mpFFT/commits/main>
  - <https://github.com/mfrewer/mpFFT/tree/main/bench>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/bench/serial_mp_N1024_time.png>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/bench/parallel_mp_C4_N1024_time.png>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/README.md>
  - <https://github.com/mfrewer/mpFFT>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/mpFFT.c>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/mpFFT.h>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/lab/serial/mp/serial_mp_fft3.c>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/lab/parallel/mp/parallel_mp_fft2.c>
  - <https://github.com/mfrewer/mpFFT/tree/main/lab/serial/mp>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/lab/serial/mp/README.md>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/lab/serial/mp/OPTIONS.md>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/lab/parallel/mp/README.md>
  - <https://github.com/mfrewer/mpFFT/tree/main/docs>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/bench/serial_mp_dP1024_time.png>
  - <https://raw.githubusercontent.com/mfrewer/mpFFT/HEAD/bench/parallel_mp_C4_dP1024_time.png>
  - <https://raw.githubusercontent.com/flintlib/flint/HEAD/doc/source/acb_dft.rst>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mfrewer/mpfft`) · [data/wave8/enrich/raw/github_com_mfrewer_mpfft.json](../../../data/wave8/enrich/raw/github_com_mfrewer_mpfft.json) (enrichment confidence 0.75)

</details>
