# optimize-gemm (Avafly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Step-by-step ARM NEON SGEMM tutorial for Raspberry Pi 4 whose final kernel beats OpenBLAS 0.3.28 and Eigen 3.4.0 at one size.

| | |
|---|---|
| **Beats** | OpenBLAS 0.3.28 and Eigen 3.4.0 (BLIS 0.9.0-156 and GSL 2.8 also measured) |
| **Claimed result** | mm_optimize 38.5153 GFLOPS (123.49 ms) versus OpenBLAS 31.4546 GFLOPS (151.21 ms) and Eigen 19.9660 GFLOPS (238.22 ms); BLIS is slightly faster at 39.5670 GFLOPS (120.21 ms); GSL 0.6559 GFLOPS. |
| **Workload** | FP32 row-major GEMM, M=1536, N=1152, K=1344, OpenMP with 4 threads on a Raspberry Pi 4B; hand-written NEON 12x8 kernel with blocking and packing. |
| **Metric** | throughput |
| **Hardware** | Raspberry Pi 4 Model B (4GB RAM), Cortex-A72, 4 cores |
| **Compiler and flags** | CMake: C++11, CMAKE_CXX_FLAGS '-DM_SIZE=1536 -DN_SIZE=1152 -DK_SIZE=1344 -O3', OpenMP; compiler name and version not stated |
| **Adoption** | 17 stars |
| **Last commit** | 2026-08-07 |
| **Links** | [repository](https://github.com/Avafly/optimize-gemm) · [benchmark](https://github.com/Avafly/optimize-gemm) |

## Verdict

On a Raspberry Pi 4 Model B (Cortex-A72, 4 cores, OpenMP 4 threads), one 1536x1152x1344 float32 row-major GEMM took 123.49 ms (38.52 GFLOPS) with mm_optimize versus 151.21 ms (31.45 GFLOPS) for OpenBLAS 0.3.28 cblas_sgemm and 238.22 ms (19.97 GFLOPS) for Eigen 3.4.0; BLIS 0.9.0 was slightly faster at 39.57 GFLOPS. Built with -O3 and an unnamed compiler; first-party, single cold run per library.

## Use it when

- Learning how a NEON SGEMM micro-kernel, packing and cache blocking fit together on an in-order-ish ARMv8 core; each optimization step is a separate file with its own measured GFLOPS.
- As a starting point for a fixed-shape float32 GEMM on Cortex-A72 class boards (Raspberry Pi 4) where you control M, N and K at compile time and they are multiples of the block sizes.
- Comparing your own kernel against OpenBLAS, BLIS, Eigen and GSL on a Pi with ready-made harnesses that print a checksum.

## Skip it when

- General-purpose GEMM: there is no edge handling, so M must be a multiple of 384 (and 12), N of 96 (and 16) and K of 192, and sizes are fixed by -DM_SIZE/-DN_SIZE/-DK_SIZE at build time.
- When BLIS is available: on the author's own table BLIS 0.9.0 is slightly faster (39.57 vs 38.52 GFLOPS).
- x86 or any non-NEON target: the kernel is written only with arm_neon.h intrinsics.
- Double precision, transposed or column-major inputs, alpha/beta scaling, or any other BLAS routine.
- Code that needs reentrancy: pack buffers and matrices are global arrays, so only one GEMM can run at a time.

## How it is fast

Goto/BLIS-style GEMM: a 12x8 register-blocked micro-kernel holding 24 float32x4 accumulators and using vfmaq_laneq_f32 lane-broadcast FMAs, fed by A packed into transposed 12-row panels (NEON 4x4 transposes) and B packed into 8-column panels so both reach the kernel as sequential streams. Each matrix is packed once, outside the loop nest; one OpenMP parallel region with a static schedule gives every thread its own rows of C, so no barriers are needed after packing, and the kernel software-prefetches a few k steps ahead.

## Compared with alternatives

Pick it over salykova's sgemm.c or carlushuang's cpu_gemm_opt when you want the ARM NEON version of the same Goto-style tutorial on a Raspberry Pi; for a usable ARM library with edge handling, use LibShalom (small and irregular shapes on ARMv8) or plain BLIS instead.

## Integration

| | |
|---|---|
| **Form** | source-drop (tutorial program; copy mm_optimize.cpp and utils.hpp) |
| **Dependencies** | OpenMP; OpenBLAS, BLIS, Eigen and GSL only for the comparison programs |
| **Minimum toolchain** | C++11 and CMake 3.10 (CMakeLists.txt); GCC-style __attribute__ and __builtin_prefetch; compiler name and version not documented |
| **Platforms** | AArch64 with NEON (tuned for Cortex-A72 / Raspberry Pi 4B); no other targets |
| **Thread safety** | Not reentrant: uses global A_pack/B_pack buffers; parallel internally with OpenMP |
| **Drop-in for the baseline** | no |

## Gotchas

- The kernel loads C and accumulates (C += A\*B); it relies on C being zero-initialized, so calling matmul twice on the same C doubles the result.
- Benchmarks time a single cold call per program (no warm-up, no repetitions), so thread start-up and first-touch costs land inside the timing for every library.
- CMakeLists.txt sets only -O3 (no -mcpu=cortex-a72), and the OpenBLAS/BLIS/Eigen builds and their thread counts are not described, so the baseline configuration cannot be reproduced exactly.
- Matrices are read from text files in ../data relative to the build directory; the program exits if they are missing.

## Known shortcomings

- Each library timed with one cold call, no warm-up; sizes fixed at compile time and must divide the block sizes, so it is tutorial code, not a general GEMM; compiler not named.
- Kernel adds into C (C += AB) rather than overwriting it; no edge handling.

## Caveats and trade-offs

One size, one machine, one cold run per library: every program times a single gemm call with omp_get_wtime (no warm-up, no repetitions), so first-call buffer allocation and thread start-up of OpenBLAS/BLIS fall inside the timing. The compiler is not named, CMakeLists.txt passes only -O3 (no -mcpu), and the OpenBLAS/BLIS/Eigen builds (target, thread count) are not described, so OpenBLAS 0.3.28 may be running an untuned kernel. mm_optimize.cpp is tutorial code, not a library: M/N/K are compile-time macros, pack buffers are static globals sized at compile time, and sizes must be divisible by the kernel and block dimensions. BLIS is about 1 GFLOPS faster (39.57 vs 38.52 GFLOPS). Matrices are loaded from text files and a checksum is printed for correctness.

ARMv8 NEON-only, single precision, row-major, tile sizes tuned to Cortex-A72; educational step-by-step repo (mm_naive to mm_optimize) rather than a drop-in BLAS (matmul(A,B,C,M,N,K) interface only).

## Maintenance

Small MIT-licensed tutorial (17 stars, 11 commits) that was revived in July-August 2026 with the layout/scheduling step and the BLIS comparison; fine to copy as teaching code, not maintained as a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README table compares mm_optimize.cpp against OpenBLAS 0.3.28 (mm_blas.cpp), Eigen 3.4.0, BLIS and GSL on a named CPU (Raspberry Pi 4B, Cortex-A72) with public code and -O3 in CMakeLists.txt, but the compiler is never named, so not A; first-party single run.
- **Verifier notes:** All README numbers (38.5153 vs OpenBLAS 31.4546, Eigen 19.9660, BLIS 39.5670, GSL 0.6559 GFLOPS) match the record. Shortcoming worth recording: single cold-call timing and fixed compile-time sizes (not a general-purpose GEMM). MIT, 17 stars, last commit 2026-08-07, not a fork.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Avafly/optimize-gemm>
  - <https://github.com/Avafly/optimize-gemm/commits>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/mm_blas.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/mm_blis.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/mm_optimize.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/utils.hpp>
- **Sources the enricher read:**
  - <https://github.com/Avafly/optimize-gemm>
  - <https://github.com/Avafly/optimize-gemm/commits>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/mm_optimize.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/utils.hpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/mm_blas.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/mm_blis.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/mm_eigen.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-gemm/HEAD/LICENSE>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/avafly/optimize-gemm`) · [data/wave8/enrich/raw/github_com_avafly_optimize_gemm.json](../../../data/wave8/enrich/raw/github_com_avafly_optimize_gemm.json) (enrichment confidence 0.8)

</details>
