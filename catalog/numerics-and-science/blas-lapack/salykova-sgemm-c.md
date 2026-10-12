# sgemm.c (salykova)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Compact pure-C, OpenMP, AVX2/FMA SGEMM in BLIS style that claims parity with OpenBLAS on two desktop CPUs.

| | |
|---|---|
| **Beats** | OpenBLAS 0.3.26 (sgemm) |
| **Claimed result** | README: 'Performance comparable to modern BLAS libraries'; plots vs OpenBLAS only, no numbers in text. MKL is not compared on the current tutorial page. |
| **Workload** | FP32 GEMM on square sizes, multithreaded and single-threaded, AVX2/FMA3 BLIS-style kernel via OpenMP |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 9700X and Intel Core Ultra 265 @ 90W, DDR5 |
| **Compiler and flags** | GCC 13.3.0; -O3 -march=native -Wall -mno-avx512f -fopenmp (CMakeLists.txt); OpenBLAS 0.3.26 built with make TARGET=ZEN |
| **Adoption** | 377 stars |
| **Last commit** | 2025-04-21 |
| **Links** | [repository](https://github.com/salykova/sgemm.c) · [benchmark](https://salykova.github.io/matmul-cpu) |

## Verdict

The author's plots (GCC 13.3, -O3 -march=native -mno-avx512f, Ryzen 7 9700X and Core Ultra 265 at 90 W, DDR5-7000) show multithreaded FP32 GEMM on square sizes roughly matching OpenBLAS 0.3.26; no numbers appear in the text, and the OpenBLAS harness is not in the repo. A third-party reproduction on a Xeon Silver 4310 found it consistently slower than OpenBLAS.

## Use it when

- Learning or teaching how a Goto/BLIS-style GEMM reaches near-BLAS throughput, with readable C instead of assembly
- Vendoring a small, dependency-free FP32 GEMM into a C/C++ project on AVX2/FMA x86-64 desktops (Zen 5, Arrow Lake class) where you can tune MC/NC/KC and thread count
- Large square FP32 matrices in column-major layout where a \~2-file kernel is preferred over linking OpenBLAS
- Starting point for a custom fused kernel (e.g. adding an epilogue) that a BLAS library will not let you modify

## Skip it when

- When you need speed over OpenBLAS: the README only claims 'comparable', and an independent run (tianyuxbear/matmul-cpu on a Xeon Silver 4310) measured it below OpenBLAS
- On AVX-512 CPUs: AVX-512 is deliberately disabled (-mno-avx512f), and the tutorial says BLAS libraries may be notably faster there
- Many-core servers: the README says its threading strategy and tile sizes are tuned for the Ryzen 7 9700X / Core Ultra 265 and recommends nested parallelism elsewhere, which is not implemented
- Double precision, complex, strided/submatrix operands, transposes or C += alpha\*A\*B: none are supported
- Small matrices: the tutorial notes multithreading pays off only at large sizes; siblings aimed at small GEMM do better there

## How it is fast

It follows the BLIS/Goto loop nest: cache blocking with MC/NC/KC (KC=500; MC and NC scale with the compile-time thread count), packing A into 16-row panels and B into 6-column panels with zero padding, and a 16x6 register-blocked micro-kernel that does rank-1 updates with _mm256_broadcast_ss + _mm256_fmadd_ps into 12 YMM accumulators. Edge tiles use masked loads and stores. OpenMP parallelizes the packing loops and the jr loop around the micro-kernel.

## Compared with alternatives

Pick it over Eigen or BLASFEO only when you want a tiny, readable C kernel to study or modify; for production FP32 GEMM, Eigen or OpenBLAS itself is safer, and the catalogued tianyuxbear/matmul-cpu reports multi-core numbers that slightly exceed OpenBLAS. BLASFEO or LibShalom fit small matrices better.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenMP (libgomp/libomp); CMake for the bundled build |
| **Minimum toolchain** | C compiler with AVX2/FMA intrinsics and OpenMP; tested with GCC 13.3 on Ubuntu 24.04; CMake 3.10+ |
| **Platforms** | x86-64 with AVX2 + FMA3 only; no ARM or scalar fallback |
| **Thread safety** | Not reentrant: the packing buffers blockA_packed/blockB_packed are static globals, so concurrent matmul calls from different threads race; parallelism is internal via OpenMP |
| **Drop-in for the baseline** | false — not a BLAS/CBLAS sgemm signature (no alpha/beta, trans flags or leading dimensions); a wrapper would have to copy submatrices |

## Gotchas

- NTHREADS and OMP_SCHEDULE are compile-time macros (CMake fails without NTHREADS) and MC/NC derive from them, so the binary is tied to one thread count
- matmul overwrites C (the first k-block zero-initialises the accumulators); it does not accumulate into existing C
- Static packing buffers of size MC\*KC and NC\*KC floats live in .bss and grow with NTHREADS
- Built with -march=native, so binaries are not portable across CPUs

## Known shortcomings

- Claims only parity ('comparable') with OpenBLAS, graphs only; repo's benchmark.c times only its own kernel; matmul-cpu README reports it slower than OpenBLAS on a Xeon Silver 4310; stale (2025-04-21).
- Not a BLAS API (no alpha/beta, transposes or leading dims; overwrites C); not reentrant (static global packing buffers); thread count and schedule fixed at compile time; -march=native with AVX-512 disabled.

## Caveats and trade-offs

Claim is 'comparable', not clearly faster; results are graphs only; OpenBLAS comparison harness is not in the repo (benchmark.c times only matmul); threading and tile sizes tuned for Ryzen 7 9700X / Core Ultra 265; an independent reproduction (tianyuxbear/matmul-cpu, Xeon Silver 4310, OpenBLAS forced to Haswell) found it consistently below OpenBLAS; last commit 2025-04-21.

FP32 only, no AVX-512, tile sizes and threading tuned to two specific CPUs; not a full BLAS API.

## Maintenance

Stale (last commit 2025-04-21) but MIT-licensed, about two source files, and easy to vendor or study; treat it as a reference implementation, not a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README and tutorial show only plots vs OpenBLAS 0.3.26 (GCC 13.3, -O3 -march=native -mno-avx512f -fopenmp, Ryzen 7 9700X / Core Ultra 265) with no textual numbers; the repo's benchmark.c times only its own kernel, so the OpenBLAS baseline code is not public and it is not A. First-party, so C.
- **Verifier notes:** Borderline on 'not-faster' (it claims parity, and a third party measured it slower), but kept as a notable (377 stars) reference implementation; orchestrator may want to record the shortcoming 'parity claim only; independent run slower than OpenBLAS'. Last commit 2025-04-21 is &gt;12 months ago, so stale.
- **Fields the verifier corrected:** `claimed_speedup`, `benchmark_url`, `compiler_and_flags`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/salykova/sgemm.c>
  - <https://github.com/salykova/sgemm.c/commits>
  - <https://salykova.github.io/matmul-cpu>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/src/matmul.c>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/src/matmul.h>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/src/kernel.h>
  - <https://raw.githubusercontent.com/salykova/sgemm.c/HEAD/src/kernel.c>
  - <https://salykova.github.io/matmul-cpu>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/salykova/sgemm.c`) · [data/wave8/enrich/raw/github_com_salykova_sgemm_c.json](../../../data/wave8/enrich/raw/github_com_salykova_sgemm_c.json) (enrichment confidence 0.75)

</details>
