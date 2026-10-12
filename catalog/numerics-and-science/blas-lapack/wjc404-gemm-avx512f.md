# GEMM_AVX512F (wjc404; AVX-512F SGEMM/DGEMM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0` · 🔴 abandoned

> Hand-written AVX-512F SGEMM/DGEMM with a Fortran-ABI entry point; claims 99% of one-thread MKL, which is parity, not a win.

| | |
|---|---|
| **Beats** | Intel MKL single-thread SGEMM/DGEMM |
| **Claimed result** | README: 'able to reach 99% MKL 1-thread performance after tuning', i.e. about 0.99x of MKL, which is parity and not a win. No GFLOPS, sizes or multi-thread numbers anywhere in the repo. |
| **Workload** | Single-thread SGEMM and DGEMM; matrix sizes, MKL version and the machine are not stated. |
| **Metric** | throughput |
| **Hardware** | dgemm_tune.h and sgemm_tune.h say 'parameters tuned on Xeon Platinum 8269CY'; the README does not say the 99% figure was measured on it. |
| **Compiler and flags** | Makefile: gcc -fopenmp --shared -fPIC -mavx512f -O2 (hand-written assembly kernel src/kernel/gemm_kernel.S plus C driver); the build used for the 99% claim is not stated. |
| **Adoption** | 15 stars, 1 fork; sibling of the already-listed wjc404 GEMM_AVX2_FMA3 |
| **Last commit** | 2022-05-22 |
| **Links** | [repository](https://github.com/wjc404/GEMM_AVX512F) · [benchmark](https://github.com/wjc404/GEMM_AVX512F) |

## Verdict

The only performance statement is the README line 'able to reach 99% MKL 1-thread performance after tuning'. It gives no GFLOPS, matrix sizes, MKL version, compiler or CPU, and the repo contains no GEMM benchmark (AVX512_CPUTEST.c only measures peak FMA throughput and latency); the tune headers say the parameters were tuned on a Xeon Platinum 8269CY. Read literally, it is a 1% deficit against single-threaded MKL: parity, not a win.

## Use it when

- Reading a complete, small AVX-512 GEMM (assembly micro-kernel, packing, prefetch-distance arithmetic, OpenMP driver) in under 2,000 lines.
- Experimenting with register-tile and cache-block parameters on an AVX-512 Xeon: change the tune headers, rebuild, and compare against your own MKL or OpenBLAS runs.
- A GPL-3.0-compatible project that wants a self-contained sgemm_/dgemm_ without a full BLAS and accepts roughly MKL single-thread speed as the best case.
- Tracing where OpenBLAS's SkylakeX DGEMM and STRMM kernels came from (the author committed them upstream in 2020).

## Skip it when

- If you want to beat MKL or OpenBLAS: the only claim is 99% of one-thread MKL, with no numbers, sizes, CPU or MKL version, and the repo has no GEMM benchmark program.
- Code that cannot be GPL-3.0.
- CPUs without AVX-512F, or non-ELF platforms: the kernels are System V AMD64 assembly (.type @function, stack red zone), so Windows and macOS builds are not supported as written.
- Multi-threaded production use: thread 0 packs A alone while the others spin, and the one issue (#1, 2020) reports that the OpenMP .so is less efficient than the serial sgemm.c. Plain OpenBLAS already contains the author's upstreamed kernels and is maintained.
- Anything that needs maintenance or other BLAS routines: last commit 2022-05-22, GEMM only, no tests and no argument checking.

## How it is fast

It uses Goto-style blocking. Each thread packs its own B block, with alpha folded into the packed copy. A is packed once per K block into a buffer that all threads share. A GNU-assembler micro-kernel (src/kernel/gemm_kernel.S) keeps GEMM_UNROLL_M_VEC x GEMM_UNROLL_N zmm accumulators live, by default 3x8 = 24 registers (a 48x8 tile for SGEMM, 24x8 for DGEMM), and updates them with vbroadcastss/sd plus vfmadd231ps/pd. The software-prefetch distances (prefetcht0/t1) into packed A and B come from the L2/L3 latency and FMA-unit parameters in sgemm_tune.h and dgemm_tune.h, and AVX512_CPUTEST.c measures FMA throughput and latency to help set them. Threads split N into equal column chunks and meet at a spin barrier around each shared A pack.

## Compared with alternatives

Pick it only to study or retune an AVX-512 GEMM kernel. The same author's GEMM_AVX2_FMA3 at least publishes numbers against MKL 2019 (2-3% faster at 20000^3 on 8 threads), FT-BLAS claims up to 3.5% over MKL, and stock OpenBLAS already ships this author's SkylakeX DGEMM and STRMM kernels.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | OpenMP (gcc -fopenmp); nothing else |
| **Minimum toolchain** | GCC with -mavx512f and the GNU assembler (AT&T-syntax .S); C11 aligned_alloc; exact GCC version not documented |
| **Platforms** | x86-64 with AVX-512F, ELF / System V ABI (Linux); default parameters tuned on a Xeon Platinum 8269CY |
| **Thread safety** | Each call allocates its own buffers, so separate calls share no state. However, each call opens an OpenMP team sized by omp_get_max_threads() and spin-waits until every thread arrives, so a call from inside another OpenMP parallel region, or with OMP_DYNAMIC or a thread limit, can hang (inferred from src/gemm_driver.c, not tested). |
| **Drop-in for the baseline** | partial: it exports Fortran-ABI sgemm_/dgemm_ with 32-bit integers and can therefore replace the GEMM symbol of an LP64 MKL or OpenBLAS, but it has no cblas_sgemm, no ILP64 and no other routines, and beta=0 does not overwrite C the way the BLAS spec allows. |

## Gotchas

- beta=0 multiplies C by zero (C_MULT_BETA) instead of overwriting it, so NaN or Inf already in C survive; reference BLAS lets callers pass an unset C when beta is zero.
- The thread count comes from omp_get_max_threads(). For the single-thread setting the 99% claim refers to, set OMP_NUM_THREADS=1.
- Tuning is compile-time only, by editing sgemm_tune.h and dgemm_tune.h; gemm_set_parameters.h silently clamps out-of-range values (for example GEMM_UNROLL_N is capped at 24/GEMM_UNROLL_M_VEC).
- aligned_alloc and malloc results are not checked, nothing returns early when m, n or k is 0, and the assembly defines a global symbol with the generic name timedelay (used by the spin barrier).

## Known shortcomings

- Not faster: the only claim is '99% of MKL 1-thread after tuning', with no benchmark code, sizes, MKL version or CPU. Historical value: the author upstreamed dgemm_kernel_16x2_skylakex.c into OpenBLAS (2020-02-03). Last commit 2022-05-22, abandoned.
- beta=0 multiplies C by zero instead of overwriting, so NaN in C survives. The thread count comes from omp_get_max_threads() with a spin barrier, so nesting or OMP_DYNAMIC can hang (inferred from code, not tested). ELF/System V assembly only. Upstream confirmed: wjc404's OpenBLAS commits 'AVX512 16x2 DGEMM kernel' (2020-02-03) and 'AVX512 STRMM kernel' (2020-02-16) match changelog 0.3.8/0.3.9.

## Caveats and trade-offs

The only claim is parity (99% of MKL one-thread after tuning), written by the author with no numbers, sizes, MKL version or CPU. No benchmark program or result file exists: the repo root, src/ and OpenBLAS-like_implementation/ listings show none, and AVX512_CPUTEST.c only measures peak per-core FMA throughput, not GEMM. There is no OpenBLAS comparison in this repo. The author upstreamed this line of work into OpenBLAS itself: OpenBLAS kernel/x86_64/dgemm_kernel_16x2_skylakex.c was created by wjc404 on 2020-02-03 ('AVX512 16x2 DGEMM kernel') and later tuned by others (2021-04-28), and OpenBLAS-like_implementation/ here holds OpenBLAS-format SkylakeX kernels (dgemm_kernel_16x2_skylakex.c, dgemm_kernel_4x8_skylakex_2.c, cgemm3m/zgemm3m skylakex kernels, sgemm.c, dgemm.c, dtrsm_16x4/), so the code largely lives on inside the OpenBLAS baseline. Last commit 2022-05-22 (default branch develop). Not faster than the named baseline.

Needs AVX-512F (Skylake-X / Cascade Lake class and newer Intel, some AMD). Built as DGEMM.so and SGEMM.so shared objects with an OpenMP driver whose blocking constants are hand-tuned in sgemm_tune.h and dgemm_tune.h (README: 'Please edit'). The OpenBLAS-like_implementation/ directory holds OpenBLAS-style Skylake-X kernels (dgemm 16x2 and 4x8, cgemm3m, zgemm3m, a dtrsm 16x4 solver). GPL-3.0 copyleft.

## Maintenance

Abandoned since 2022-05-22 (82 commits, 15 stars, one open 2020 issue) and GPL-3.0, so vendoring it brings copyleft. Its lasting value is upstream: the author's OpenBLAS commits include 'AVX512 16x2 DGEMM kernel' (2020-02-03) and 'AVX512 STRMM kernel' (2020-02-16), matching the AVX512 DGEMM kernel added in OpenBLAS 0.3.8 and the SkylakeX STRMM kernel in 0.3.9.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification C, tier now C.
- **Tier reason:** The README's single sentence 'able to reach 99% MKL 1-thread performance after tuning' is a first-party figure with no sizes, GFLOPS, MKL version, CPU or benchmark code; the repo root, src/ and OpenBLAS-like_implementation/ hold no benchmark program or results. That is a number without methodology (C), and it claims parity-minus-1%, not a win.
- **Verifier notes:** Metadata confirmed (GPL-3.0, 15 stars, 1 fork, 82 commits, last commit 2022-05-22, not archived). Reject as not-faster (99% of MKL); evidence is genuine, so under keep-and-document record shortcoming 'parity claim only, no benchmark; kernels upstreamed into OpenBLAS (dgemm_kernel_16x2_skylakex.c)' or fold as related to the listed OpenBLAS.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/wjc404/GEMM_AVX512F>
  - <https://github.com/wjc404/GEMM_AVX512F/commits/develop>
  - <https://github.com/wjc404/GEMM_AVX512F/tree/develop/src>
  - <https://github.com/wjc404/GEMM_AVX512F/tree/develop/OpenBLAS-like_implementation>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/README.md>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/Makefile>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/dgemm_tune.h>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/sgemm_tune.h>
  - <https://github.com/OpenMathLib/OpenBLAS/commits/develop/kernel/x86_64/dgemm_kernel_16x2_skylakex.c>
- **Sources the enricher read:**
  - <https://github.com/wjc404/GEMM_AVX512F>
  - <https://github.com/wjc404/GEMM_AVX512F/tree/develop/src>
  - <https://github.com/wjc404/GEMM_AVX512F/tree/develop/OpenBLAS-like_implementation>
  - <https://github.com/wjc404/GEMM_AVX512F/commits/develop>
  - <https://github.com/wjc404/GEMM_AVX512F/issues?q=is%3Aissue>
  - <https://github.com/wjc404/GEMM_AVX512F/issues/1>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/README.md>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/Makefile>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/dgemm_tune.h>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/sgemm_tune.h>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/AVX512_CPUTEST.c>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/src/gemm_driver.c>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/src/gemm_set_parameters.h>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/src/gemm_copy.c>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/src/kernel/gemm_kernel.S>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/src/kernel/gemm_kernel_wrapper.c>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/OpenBLAS-like_implementation/sgemm.c>
  - <https://raw.githubusercontent.com/wjc404/GEMM_AVX512F/HEAD/OpenBLAS-like_implementation/dgemm_kernel_16x2_skylakex.c>
  - <https://github.com/OpenMathLib/OpenBLAS/commits/develop/?author=wjc404>
  - <https://raw.githubusercontent.com/OpenMathLib/OpenBLAS/develop/Changelog.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/wjc404/gemm_avx512f`) · [data/wave8/enrich/raw/github_com_wjc404_gemm_avx512f.json](../../../data/wave8/enrich/raw/github_com_wjc404_gemm_avx512f.json) (enrichment confidence 0.75)

</details>
