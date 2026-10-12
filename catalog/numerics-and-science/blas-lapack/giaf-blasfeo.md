# BLASFEO

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> C BLAS/LAPACK subset tuned for cache-resident small matrices; 2-3x faster than OpenBLAS/BLIS at sizes in the tens.

| | |
|---|---|
| **Beats** | Intel MKL and OpenBLAS (level-3 BLAS and LAPACK routines on small matrices) |
| **Claimed result** | 2-3x faster than OpenBLAS and BLIS for level-3 BLAS at matrix sizes in the tens on Haswell, \~2x for LAPACK factorizations up to size 100; competitive with MKL on dgemm and faster than MKL on other level-3 and LAPACK routines; \~2x on Cortex A57, larger margin on Cortex A53 |
| **Workload** | Cache-resident small dense matrices (up to \~100-256): gemm_nt and potrf_l in double and single precision |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 4800MQ (Haswell, 3.3 GHz, 52.8 Gflops peak); also Ivy Bridge i3 3520M, Cortex A57/A15 |
| **Compiler and flags** | not stated in paper (libraries single-threaded; MKL with MKL_DIRECT_CALL_SEQ) |
| **Adoption** | 415 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/giaf/blasfeo) · [benchmark](https://arxiv.org/pdf/1704.02457) |

## Verdict

The authors' BLAS API paper (arXiv 1902.08115) times single-threaded BLASFEO against OpenBLAS 0.3.4-dev, BLIS 0.5.0 and MKL 2019.1 on a Haswell Core i7 4810MQ, Cortex-A57 (Tegra TX1) and Cortex-A53: factor 2-3 over OpenBLAS/BLIS for level-3 BLAS at sizes in the tens on Haswell, about 2x for LAPACK factorizations up to \~100, on par with MKL dgemm and faster on other routines; compiler and flags are not stated.

## Use it when

- Single-threaded dense linear algebra on matrices of roughly 10-250 per side that fit in cache (MPC, embedded optimization, Kalman filters, robotics)
- Cholesky/LU/QR on small matrices, where the BLAS API paper shows about 2x over OpenBLAS/BLIS LAPACK up to size \~100
- Low-power ARM (Cortex-A53/A57) boards, where the margin over OpenBLAS and BLIS is largest
- Code you control end to end and can move to the native panel-major API for another 10-15% over BLASFEO's own BLAS API

## Skip it when

- Large matrices or multithreaded throughput: routines are single-threaded and optimized for cache-resident sizes; use OpenBLAS/MKL/BLIS
- Needing full BLAS/LAPACK coverage: only a subset of routines and variants is optimized, others fall back to reference code or need Netlib complementing
- dgemm alone on Intel: the paper finds it only competitive with MKL there, not faster
- Complex-number routines: not listed among optimized routines

## How it is fast

Hand-written assembly kernels per microarchitecture (Haswell AVX2/FMA, Skylake-X AVX-512, Cortex-A53/A57/A76, Apple M1, etc.) with a custom internal calling convention so kernels chain without function-call overhead. The native API stores matrices in panel-major format (fixed-height row panels, column-major inside), which is the layout GEMM kernels want, so no packing is done at all; the BLAS API packs on the fly with strategies tuned for small sizes. LAPACK factorizations are written directly on these kernels instead of the blocked LAPACK reference algorithms.

## Compared with alternatives

Pick BLASFEO over Eigen or a general BLAS (FT-BLAS, BLIS forks) when your matrices are small and you also need fast factorizations (potrf/getrf/geqrf), not just GEMM; LibShalom reports 2x over BLASFEO at M=N=K=8 on Phytium, so for tiny GEMM-only work on ARM servers check LibShalom or IAAT first.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (optional external BLAS/LAPACK for the wrapper backend, fallback or Netlib complement; Python 3.6 + jinja2 only for the test suite) |
| **Minimum toolchain** | C compiler with GNU-style assembler (gcc default); Make or CMake; exact minimum not documented |
| **Platforms** | x86-64 (SSE3/AVX/AVX2+FMA/AVX-512 targets), 32-bit x86, ARMv8-A (A53/A55/A57/A73/A76, Apple M1), ARMv7-A, plus a GENERIC C target; high-performance backend on Linux, Windows x86-64 and macOS |
| **Thread safety** | not documented (routines are single-threaded) |
| **Drop-in for the baseline** | partial — the BLAS API exports standard dgemm_/cblas_ names only when built with FORTRAN_BLAS_API=1 (default names are blasfeo_blas_\*), and only a subset of BLAS/LAPACK routines is provided unless complemented with Netlib |

## Gotchas

- Target is chosen at build time (TARGET=...); a binary built for X64_INTEL_HASWELL will not adapt to other CPUs (CMake has X64_AUTOMATIC detection for the host only)
- Denormals in matrix memory, including padding, can slow routines 10x or more; the docs recommend zeroing memory passed to blasfeo_create_dmat and BLAS-API arrays
- Align memory to 64-byte cache lines and use leading dimensions that are multiples of the kernel size (typically 4 in double) for best speed
- Stack buffers sized by K_MAX_STACK (default 300) can exceed small thread stacks; lower it if the stack overflows

## Known shortcomings

- Paper: 2-3x faster than OpenBLAS/BLIS at sizes in the tens (not '1.5-3x up to 100'); level with MKL on dgemm; no compiler or flags given.
- arXiv abstract (TOMS paper 1704.02457) gives 20-30% over comparable libraries up to \~100, 2-3x only vs LAPACK; not a default drop-in (dgemm_/cblas_ exported only with FORTRAN_BLAS_API=1, only some routines optimized); single-threaded only; denormals in matrix memory or padding can slow it 10x+.

## Caveats and trade-offs

Paper numbers from 2019-2020 (OpenBLAS 0.3.4-dev, BLIS 0.5.0, MKL 2019.1); single-threaded only; win is for small cache-resident matrices, not large ones; compiler/flags not stated

Panel-major storage in native API (BLAS API wrapper also available); optimized for small cache-resident matrices, not large.

## Maintenance

Actively developed (commits through Sept 2026), BSD-2-Clause, and used as the linear algebra layer of embedded optimization toolchains, so it is safe to build from source or vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed paper (The BLAS API of BLASFEO, arXiv 1902.08115) benchmarks single-threaded BLASFEO vs OpenBLAS 0.3.4-dev, BLIS 0.5.0 and MKL 2019.1 on named CPUs; compiler and flags are not stated, so not A.
- **Verifier notes:** Paper gives 'factor 2 or 3' for sizes in the tens, not 1.5-3x up to 100; corrected. Metadata (BSD-2-Clause, 415 stars, last commit 2026-09-29) checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/1902.08115>
  - <https://arxiv.org/pdf/1902.08115>
  - <https://github.com/giaf/blasfeo>
  - <https://github.com/giaf/blasfeo/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/giaf/blasfeo/HEAD/README.md>
  - <https://raw.githubusercontent.com/giaf/blasfeo/HEAD/Makefile.rule>
  - <https://raw.githubusercontent.com/giaf/blasfeo/HEAD/guidelines.md>
  - <https://arxiv.org/abs/1902.08115>
  - <https://arxiv.org/abs/1704.02457>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/giaf/blasfeo`) · [data/wave8/enrich/raw/github_com_giaf_blasfeo.json](../../../data/wave8/enrich/raw/github_com_giaf_blasfeo.json) (enrichment confidence 0.75)

</details>
