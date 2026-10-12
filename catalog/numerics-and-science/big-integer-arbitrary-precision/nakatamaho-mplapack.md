# MPLAPACK (multiple-precision BLAS/LAPACK with double-double, quad-double and CUDA backends)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Full BLAS/LAPACK in C++ at binary80/128, double-double, quad-double, GMP and MPFR; the dd/qd backends far outrun its 512-bit GMP/MPFR backends.

| | |
|---|---|
| **Beats** | GMP (mpf) and MPFR backends of the same library, at their default 512-bit precision |
| **Claimed result** | Manual section 9 peaks for Rgemm: reference GMP 19 MFlops and 693 MFlops OpenMP; reference MPFR 11 MFlops and 390 MFlops OpenMP; reference quad-double 33 MFlops and 1.3 GFlops OpenMP; reference double-double about 365 MFlops and 11.2 GFlops OpenMP. Derived from page data: double-double OpenMP is about 29x MPFR and 16x GMP, quad-double OpenMP about 3.3x MPFR and 1.9x GMP. README: CUDA double-double Rgemm and Rsyrk reach about 450 GFlops on a V100. Benchmark logs in the repo show the A100-box CUDA double-double kernel at 486,829 MFLOPS (n = 562). |
| **Workload** | Rgemm (multiple-precision matrix-matrix multiply) with square matrices on a Ryzen Threadripper 3970X, double-double and quad-double backends (with and without OpenMP) versus the GMP and MPFR backends, plus a CUDA double-double Rgemm on A100/V100 GPUs. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper 3970X, 256 GB DDR4-3200; GPU runs on Tesla V100 / A100 (benchmark/results/2022 folders) |
| **Compiler and flags** | GCC 9.3.0 inside Docker (manual); example builds use g++ -O2, benchmark flags not stated |
| **Adoption** | 108 stars, 15 forks, 3,808 commits; latest release v3.0.1 (2026-09-15) |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/nakatamaho/mplapack) · [benchmark](https://raw.githubusercontent.com/nakatamaho/mplapack/master/doc/manual/manual.pdf) |

## Verdict

First-party manual figures on an AMD Ryzen Threadripper 3970X (GCC 9.3.0 in Docker, optimization flags not stated, square matrices up to about n = 1000): Rgemm with OpenMP peaked at 11.2 GFlops for double-double and 1.3 GFlops for quad-double versus 693 MFlops for 512-bit GMP and 390 MFlops for 512-bit MPFR, about 16x and 29x for dd (derived from page data). The 2022 logs on the A100 box show OpenMP dd 8.16 GFlops versus GMP 667 and MPFR 403 MFlops, and the CUDA dd Rgemm at 487 GFlops kernel-only or 382 GFlops with transfers (derived from page data).

## Use it when

- You need LAPACK-level algorithms (LU/Cholesky solves, eigenvalues, SVD, least squares) beyond binary64 in C/C++, for ill-conditioned systems or interior-point SDP solvers (it began as the backend of SDPA-GMP).
- About 32 digits is enough: the dd backend with OpenMP reached 11.2 GFlops Rgemm on a 32-core Threadripper 3970X versus 0.69 GFlops for 512-bit GMP and 0.39 GFlops for 512-bit MPFR.
- An NVIDIA GPU is available and dd precision suffices: the CUDA dd Rgemm logged about 380 GFlops including transfers (487 GFlops kernel-only) on an A100.
- You need precision chosen at run time (MPFR, e.g. 65,536 bits via MPLAPACK_MPFR_PRECISION) while keeping one LAPACK-style code path across backends.
- You want a heavily tested multiprecision LAPACK: 3.0.0 release QA ran over 126 million lin tests and 116 million eig tests across 11 platform/compiler triplets.

## Skip it when

- binary64 or fast high-precision BLAS: the manual says its double results 'are not competitive to OpenBLAS or Intel MKL' (15 GFlops OpenMP versus 1.46 TFlops OpenBLAS DGEMM on the same CPU); the multiprecision kernels have no blocking or vectorization ('Rgemm acceleration' issue #59 open since 2022).
- You need more than about 64 digits and high throughput: the GMP/MPFR paths ran at 0.4-0.7 GFlops at 512 bits on 32 cores.
- You need certified error bounds: results are rounded floating-point values, not interval or ball enclosures.
- GMP backend for CSD or transcendental-heavy paths: GMP's mpf lacks atan2, so Rorbdb/Cunbdb fail at entry, and the manual says GMP support will be dropped in favor of MPFR.
- Clang-only toolchains needing binary128 (unsupported), or users who need bit-identical results across platforms (the project warns last-digit differences are the default).

## How it is fast

The speedup comes from the format, not from kernel tuning: double-double (about 32 digits) and quad-double (about 64 digits) are unevaluated sums of 2 or 4 hardware doubles using Dekker/Knuth error-free transformations (QD library), avoiding GMP/MPFR's heap-allocated limb arithmetic. The optimized CPU Rgemm is the reference triple loop with one '#pragma omp parallel for' over output columns (no blocking or SIMD). The CUDA double-double Rgemm/Rsyrk kernels (2010-2011 Fermi/Tesla code) use FMA-based dd multiply and add on the GPU.

## Compared with alternatives

Pick MPLAPACK over FLINT or APFP when you need complete LAPACK factorizations, eigen and SVD solvers rather than only fast big-number or matrix-multiply kernels, and over DoubleFloats.jl or MultiFloats.jl when you are in C++ rather than Julia and want one API spanning double-double to arbitrary MPFR precision.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Bundled and built by the autotools build: GMP, MPFR, MPC, QD (libQD3), gmpfrxx_mkII wrappers, OpenBLAS (benchmarks only); CUDA for the dd GPU flavor; the experimental CMake build uses system GMP/MPFR/MPC/QD instead |
| **Minimum toolchain** | C++17 (C++17/20/23/26 selectable); GCC with gfortran for the autotools build, GCC 15 supported since 2.1.1; Intel oneAPI icx/icpx supported; Clang lacks binary128 |
| **Platforms** | Tier 1: Linux and macOS on amd64 and arm64, Windows via MinGW-w64, Debian i386; binary80 x86 only; CUDA dd kernels on NVIDIA GPUs (V100, A100 and RTX 3080 results published) |
| **Thread safety** | not documented; the optimized flavors run OpenMP threads inside Rgemm, Raxpy and similar routines |
| **Drop-in for the baseline** | partial — the same Rgemm/LAPACK-style calls exist for every backend, so moving from the GMP/MPFR backend to dd/qd is a type change and relink, but precision drops from 512 bits to 106 or 212 bits |

## Gotchas

- The headline speedups compare unequal precision: dd (106 bits) and qd (212 bits) against 512-bit GMP/MPFR; at equal precision there is no speedup claim, and benchmarks are from 2022 (v2.0, GCC 9.3.0, flags not stated), before the 3.0.0 move to expression-template MPFR/GMP wrappers.
- 3.0.0 broke the ABI and API: mpreal and mpcomplex became mpfr_class and mpc_class, the GMP complex type became mpfc_class, and since 2.3.0 the separate libmpblas_\* libraries are gone, so the v2.0.1 manual's examples and link lines are out of date.
- GMP backend hazards documented by the project: exact division by zero aborts with SIGFPE instead of producing Inf, and any helper reached through mpf_class's implicit operator double() silently truncates to 53 bits.
- DD needs -ffp-contract=off (a DD miscompilation was fixed in 2.1.1 by forcing it); dd/qd do not implement full IEEE Inf/NaN/signed-zero semantics; the CUDA dd kernels compile with QD's SLOPPY_MUL and CRAY_ADD variants, and the 487 GFlops A100 figure excludes host-device transfers.

## Known shortcomings

- Compares its own double-double/quad-double backends with 512-bit GMP/MPFR (unequal precision); A100 486,829 MFLOPS is kernel-only (381,882 with transfers).
- The 'optimized' CPU Rgemm is the reference triple loop with one OpenMP pragma; CUDA kernels use QD's less accurate fast-multiply/fast-add; 2022 benchmarks predate the 3.0.0 rewrite of the GMP/MPFR wrappers (ABI/API break); the GMP backend aborts with SIGFPE on division by exact zero and some helpers silently drop to 53-bit precision.

## Caveats and trade-offs

Not an equal-precision comparison: the GMP/MPFR columns are 512-bit, the dd and qd columns are 106 and 212 bits, so the speedups mostly reflect hardware double arithmetic versus software bignum. The manual itself says the double results 'are not competitive to OpenBLAS or Intel MKL' (OpenBLAS DGEMM reached 1.46 TFlops on the same CPU). The author notes MPFR is about twice as slow as GMP, possibly because of copies in the MPFR C++ binding. First-party numbers from the arXiv user manual (version 2.0, 2022); the 2023-2026 releases (2.1.0 through 3.0.1, including a GMP/MPFR wrapper migration to gmpfrxx_mkII in 3.0.0) were not re-benchmarked in what was read. The 486,829 MFLOPS A100 figure is the kernel-only log (log.Rgemm.dd_cuda_kernel); the matching log including transfers (log.Rgemm.dd_cuda_total) peaks at 381,882 MFLOPS at n = 2296 (derived from page data). Benchmark optimization flags are not stated (manual examples use g++ -O2). last_commit is from the master commits page (2026-09-19, 'Fix commit-based QA source checkout').

Faster only by giving up precision: double-double is about 32 digits (106 bits) and quad-double about 64 digits (212 bits), while the GMP and MPFR runs use 512 bits. Needs the dd/qd formats' accuracy to be enough; the library keeps one API across binary64, binary128, FP80, dd, qd, GMP and MPFR backends.

## Maintenance

Actively maintained (v3.0.1 released 2026-09-15, latest master commit 2026-09-19, 3,808 commits, 24 open issues), BSD-2-Clause, with a large tiered release test matrix; the performance data has not been refreshed since 2022.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Manual section 9 gives first-party Rgemm/Raxpy peaks on a Ryzen Threadripper 3970X with GCC 9.3.0 in Docker, and the scripts are public (benchmark/mpblas/go.Rgemm.sh), but benchmark optimization flags are not stated and the comparison is the library's own backends at unequal precision (dd/qd vs 512-bit GMP/MPFR), with no peer review, so C.
- **Verifier notes:** All manual figures (19/693, 11/390, 33/1300, 365/11200 MFlops) and the derived ratios check out; the A100 kernel log shows 486829.770 MFLOPS at n = 562. last_commit corrected from the topics-page 'updated' date (2026-09-30) to the latest master commit seen (2026-09-19).
- **Fields the verifier corrected:** `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/doc/manual/manual.pdf>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/HEAD/README.md>
  - <https://github.com/nakatamaho/mplapack>
  - <https://github.com/nakatamaho/mplapack/commits/master>
  - <https://github.com/nakatamaho/mplapack/tree/master/benchmark/results/2022>
  - <https://github.com/nakatamaho/mplapack/tree/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100>
  - <https://github.com/nakatamaho/mplapack/tree/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100/logs>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100/logs/log.Rgemm.dd_cuda_kernel>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100/logs/log.Rgemm.dd_cuda_total>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100/logs/log.Rgemm.gmp_opt>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100/logs/log.Rgemm.mpfr_opt>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100/logs/log.Rgemm.dd_opt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/HEAD/README.md>
  - <https://github.com/nakatamaho/mplapack>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/doc/manual/manual.pdf>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/HEAD/MULTIPRECISION_FAILURE_MODES_2.2.0.md>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/HEAD/CHANGES.3.0.0.md>
  - <https://github.com/nakatamaho/mplapack/tree/master/mpblas/optimized>
  - <https://github.com/nakatamaho/mplapack/tree/master/mpblas/optimized/dd>
  - <https://github.com/nakatamaho/mplapack/tree/master/mpblas/optimized/dd/openmp>
  - <https://github.com/nakatamaho/mplapack/tree/master/mpblas/optimized/dd/cuda>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/mpblas/optimized/dd/Rgemm.cpp>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/mpblas/optimized/dd/openmp/Rgemm_NN_omp.cpp>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/mpblas/optimized/dd/cuda/Rgemm.cu>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/mpblas/optimized/dd/cuda/Rgemm_cuda.cu>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/mpblas/optimized/dd/cuda/dd_real_cuda.h>
  - <https://github.com/nakatamaho/mplapack/issues>
  - <https://github.com/nakatamaho/mplapack/issues/59>
  - <https://github.com/nakatamaho/mplapack/tree/master/benchmark/results>
  - <https://github.com/nakatamaho/mplapack/tree/master/benchmark/results/2022>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100/logs/log.Rgemm.dd_opt>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100/logs/log.Rgemm.gmp_opt>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100/logs/log.Rgemm.mpfr_opt>
  - <https://raw.githubusercontent.com/nakatamaho/mplapack/master/benchmark/results/2022/x86_64-pc-linux-gnu-Ryzen-Threadripper-3970X-TeslaA100/logs/log.Rgemm.dd_cuda_total>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nakatamaho/mplapack`) · [data/wave8/enrich/raw/github_com_nakatamaho_mplapack.json](../../../data/wave8/enrich/raw/github_com_nakatamaho_mplapack.json) (enrichment confidence 0.8)

</details>
