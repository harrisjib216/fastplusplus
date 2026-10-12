# matmul-cpu (core_v5 GEMM kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Learning-project AVX-512 FP32 GEMM (row-major C += A\*B^T) that edges past OpenBLAS at 4096^3 on 24 threads only.

| | |
|---|---|
| **Beats** | OpenBLAS (sgemm, C=A\*B^T+C) |
| **Claimed result** | Multi-core peak 2010.61 vs OpenBLAS 1914.91 GFLOPS (\~106% of OpenBLAS); single-core 110.74 vs 132.88 GFLOPS (82.4%, slower) |
| **Workload** | Single-precision GEMM M=N=K=4096, 24 threads, AVX-512 14x32 micro-kernel, 10 timed rounds after 2 warmups |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Silver 4310 @ 2.10GHz, 24 cores, 2 sockets, AVX-512 |
| **Compiler and flags** | compiler unstated (xmake default toolchain); -O3 -march=native -fopenmp, C++17 (xmake.lua) |
| **Adoption** | 0 stars |
| **Last commit** | 2025-12-28 |
| **Links** | [repository](https://github.com/tianyuxbear/matmul-cpu) · [benchmark](https://github.com/tianyuxbear/matmul-cpu) |

## Verdict

On a 2-socket Intel Xeon Silver 4310 (24 cores, AVX-512) with -O3 -march=native -fopenmp and an unnamed compiler, the author's README reports core_v5 at 2010.61 peak / 1909.40 average GFLOPS against OpenBLAS's 1914.91 / 1796.69 for 4096^3 FP32 C += A\*B^T with 24 threads (about 106%), and core_v4 at 82.4% of single-threaded OpenBLAS. The author's own 256-8960 scaling plots show a clear multi-threaded win only in roughly the 2560-4352 range; elsewhere OpenBLAS is ahead or tied, and the OpenBLAS version is not stated.

## Use it when

- Studying how an AVX-512 Goto-style SGEMM is built, from naive SIMD through cache blocking to a parallel micro-kernel, with timings for each step
- Large square FP32 GEMMs (about 2560-4352 per side) on a 24-core AVX-512 Xeon similar to the Silver 4310, where the author's own plots show it ahead of OpenBLAS; above about 4600 OpenBLAS's best runs are higher at most sizes
- Prototyping an inference-engine GEMM kernel where B is stored as N x K (weights transposed) and you want to avoid pulling OpenBLAS and its thread pool into the binary, if you can obtain a license from the author

## Skip it when

- Any reuse in shipped code: the repository has no LICENSE file, so you have no right to copy it
- Small and medium matrices: in the author's scaling plots core_v5 averages roughly 10 and 40 GFLOPS at 256 and 512 per side (OpenBLAS about 320 and 420) even though its best runs there are comparable, so it is erratic from run to run; OpenBLAS also leads from 768 to about 2300
- Single-threaded use: core_v4 reaches 82.4% of OpenBLAS (110.74 vs 132.88 GFLOPS peak at 4096)
- CPUs without AVX-512, machines that do not have 24 cores, or code that calls GEMM concurrently from several threads
- Anything beyond row-major FP32 C += A\*B^T: there is no FP64, no general transposes, strides, alpha or beta

## How it is fast

It applies the Goto/BLIS loop nest: NC/KC/MC cache blocking, packing A into 14-row and B into 32-column zero-padded panels, and a 14x32 register-blocked micro-kernel that broadcasts one A element (_mm512_set1_ps) and issues two _mm512_fmadd_ps per row into 28 ZMM accumulators. Partial tiles use AVX-512 mask loads and stores. The parallel version (v5) uses OpenMP to split packing and the jr loop over micro-panels across a fixed 24 threads, with MC and NC scaled by that thread count.

## Compared with alternatives

Over salykova's sgemm.c, which it is derived from, pick it when you want an AVX-512, row-major, B-transposed (weights-style) layout to study; sgemm.c is MIT-licensed, while this repo has no license. For production FP32 GEMM, OpenBLAS itself, Eigen or FT-BLAS are safer choices, and BLASFEO or LibShalom fit small matrices better.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenMP; OpenBLAS (via xmake add_requires) only for the benchmark wrappers; xmake for the bundled build |
| **Minimum toolchain** | C++17 with AVX-512F intrinsics and OpenMP; uses __builtin_expect, so GCC or Clang; compiler and version not documented (xmake default toolchain, -O3 -march=native -fopenmp) |
| **Platforms** | x86-64 with AVX-512F only; tuned for one Intel Xeon Silver 4310 (2 sockets, 24 cores); no AVX2-only or ARM path for the core_v4/v5 kernels |
| **Thread safety** | Not thread-safe: v4 and v5 keep packing buffers in static globals, and the v5 source comment warns that concurrent calls are unsafe |
| **Drop-in for the baseline** | false — not a BLAS/CBLAS sgemm signature; only C += A\*B^T with fixed row-major, contiguous operands |

## Gotchas

- core_v5 hard-codes NTHREADS = 24 in an omp parallel for num_threads(24) pragma, and its MC/NC blocks scale with it, so it oversubscribes smaller machines and ignores OMP_NUM_THREADS
- core_v5's static packing buffers are about 48 MB (NC\*KC = 23040\*512 floats for B plus 1680\*512 for A), all in .bss, even for tiny matrices
- It accumulates into C (C += A\*B^T); callers expecting C = A\*B overwrite semantics must zero C first
- The benchmark driver checks correctness only with -v, which the README's benchmark commands do not pass; for partial row tiles the micro-kernel also runs FMAs on accumulator rows it never loaded (results are discarded, but the values are uninitialized)

## Known shortcomings

- Compiler never named (flags in xmake.lua); no LICENSE file (reference only); single core reaches 82.4% of OpenBLAS, wins only multi-threaded (2010.61 vs 1914.91 GFLOPS, 24 threads).
- The 106%-of-OpenBLAS headline is a favourable point: the author's own plots show it ahead only at about 2560-4352; at 256 and 512 it averages about 10 and 40 GFLOPS vs about 320 and 420 for OpenBLAS; above 4600 OpenBLAS's best runs are mostly higher.
- NTHREADS=24 hard-coded; about 48 MB of static buffers; not thread-safe; benchmark checks correctness only with -v (not in README commands); no license; last commit 2025-12-28, so 'active' is doubtful.

## Caveats and trade-offs

Compiler not named (flags only, in xmake.lua); no LICENSE file in repo; wins only multithreaded at 4096 (avg 1909.40 vs 1796.69 GFLOPS) and loses single-core to OpenBLAS (82.4%); computes C=A\*B^T+C row-major only; first-party numbers.

Only C=A\*B^T+C row-major sgemm; not a full BLAS; tile sizes tuned to one CPU.

## Maintenance

Personal learning project (0 stars, 22 commits, last commit 2025-12-28) with no license, so it is reference-only: read it to learn the technique, but do not copy it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README tables compare core_v5_parallel vs OpenBLAS (2010.61 vs 1914.91 peak GFLOPS, 24 threads) on a stated Xeon Silver 4310, with benchmark code in src/ and flags (-O3 -march=native -fopenmp) in xmake.lua, but the compiler is never named, so not A; first-party, so C.
- **Verifier notes:** Numbers match the README exactly. No license file found (LICENSE/LICENSE.md/LICENSE.txt all 404), so usability reference stands. Last commit 2025-12-28 confirmed on commits page.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tianyuxbear/matmul-cpu>
  - <https://github.com/tianyuxbear/matmul-cpu/commits>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/HEAD/README.md>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/HEAD/xmake.lua>
- **Sources the enricher read:**
  - <https://github.com/tianyuxbear/matmul-cpu>
  - <https://github.com/tianyuxbear/matmul-cpu/commits/master>
  - <https://github.com/tianyuxbear/matmul-cpu/tree/master/src>
  - <https://github.com/tianyuxbear/matmul-cpu/tree/master/src/core>
  - <https://github.com/tianyuxbear/matmul-cpu/tree/master/include>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/HEAD/README.md>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/HEAD/xmake.lua>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/master/include/matmul.hpp>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/master/include/utils.hpp>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/master/src/main.cpp>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/master/src/openblas.cpp>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/master/src/utils.cpp>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/master/src/core/matmul_v4_cache_opt.cpp>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/master/src/core/matmul_v5_parallel.cpp>
  - <https://raw.githubusercontent.com/tianyuxbear/matmul-cpu/master/benchmark.sh>
  - <https://raw.githubusercontent.com/tianyuxbear/images/HEAD/blog/core_blas_comparison_avg.png>
  - <https://raw.githubusercontent.com/tianyuxbear/images/HEAD/blog/core_blas_comparison_peak.png>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tianyuxbear/matmul-cpu`) · [data/wave8/enrich/raw/github_com_tianyuxbear_matmul_cpu.json](../../../data/wave8/enrich/raw/github_com_tianyuxbear_matmul_cpu.json) (enrichment confidence 0.8)

</details>
