# BaSpaCho

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Supernodal sparse Cholesky for block-structured SPD systems with CPU and batched-CUDA backends; factors faster than CHOLMOD on its synthetic tests.

| | |
|---|---|
| **Beats** | CHOLMOD (SuiteSparse) |
| **Claimed result** | Sparse Cholesky factor vs CHOLMOD on synthetic problems: CPU BLAS (OpenBLAS, 16 threads) roughly 4-74% less time across 11 problem types (e.g. -71% FLAT+SCHUR, -69..-74% GRID 200x200); with Intel MKL it ranges from about 20% slower to 88% faster; CUDA backend about 85-90% less time than CPU CHOLMOD on FLAT problems |
| **Workload** | Batched supernodal sparse Cholesky for SPD matrices (bundle adjustment style, synthetic and BAL problems) |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Silver 4214 @ 2.20GHz, 128GB RAM, Quadro RTX 5000 (ThinkStation P720) |
| **Adoption** | 112 stars |
| **Last commit** | 2025-10-08 |
| **Links** | [repository](https://github.com/facebookresearch/baspacho) · [benchmark](https://github.com/facebookresearch/baspacho/blob/main/BENCHMARK_RESULTS.md) |

## Verdict

The repo's bench tool timed factorization against CHOLMOD on synthetic FLAT, FLAT+SCHUR, GRID and MERI block graphs (5 random instances each) on a Xeon Silver 4214 with a Quadro RTX 5000. With OpenBLAS and 16 threads, CPU factor time was 4-17% lower on FLAT problems and 44-74% lower on Schur-heavy and larger grid problems. With MKL the result ran from about 20% slower to 88% faster. The CUDA backend was 77-95% faster than CPU CHOLMOD. Compiler and flags are not stated.

## Use it when

- Bundle adjustment or SLAM normal equations with many small (1-12) parameter blocks and a large set of independently eliminable points (point/landmark Schur structure)
- Repeated factorizations of a fixed sparsity pattern in an LM/Gauss-Newton loop, where the analysis cost is paid once
- Batched solves of same-structure systems on an NVIDIA GPU, e.g. differentiable optimization in PyTorch/Theseus
- Moderately to strongly interconnected graphs (2D grids, mesh-like graphs) where supernodes are large enough for BLAS to pay off
- When you need partial factorization or marginal covariances, or a direct/PCG hybrid

## Skip it when

- Banded or very sparse matrices where simplicial Cholesky wins; the README says to use CHOLMOD or Eigen there
- Matrices that need update/downdate of the factor, or non-SPD/indefinite systems (no LDL^T or LU, and singularity reporting is listed as future work)
- Single-RHS CPU solves dominate your runtime: in the repo's own runs, CPU solve-1 was about 2.1-2.5x slower than CHOLMOD on FLAT 1000
- One-shot factorizations of very sparse FLAT problems: symbolic analysis was about 3.5-4x slower than CHOLMOD on FLAT size=4000 fill=0.01
- If you link Intel MKL: with MKL, BaSpaCho's CPU factor was 15-23% slower than CHOLMOD on two FLAT problem types

## How it is fast

Supernodal Cholesky groups columns into dense blocks so most of the work runs through BLAS/LAPACK potrf/trsm/syrk/gemm. A fitted computation model of BLAS timings chooses which supernodes to merge. Independent small diagonal blocks (the 'Schur-complement trick' from Ceres-style BA) go through a parallel 'sparse elimination' stage before the supernodal part, which gives the large wins on FLAT+SCHUR problems. On GPU it runs entirely in CUDA/cuBLAS and can batch several matrices that share a sparsity pattern.

## Compared with alternatives

Pick BaSpaCho over Sympiler when you need a GPU or batched backend and BA-style Schur elimination built in, rather than code generation specialised to one sparsity pattern on the CPU. Ginkgo and AMGCL are iterative solvers (Krylov/AMG); choose BaSpaCho when you want an exact direct factorization of a block SPD system and the fill is manageable.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake build) |
| **Dependencies** | BLAS/LAPACK (OpenBLAS, ATLAS or MKL); Eigen 3.4, dispenso 1.4 (threads), gtest and Sophus are fetched by CMake; optional CUDA toolkit + cuBLAS/cuSPARSE, SuiteSparse AMD, and CHOLMOD (benchmarks only) |
| **Minimum toolchain** | C++17, CMake 3.28+; CUDA tested with 10.2/11.7, compute capability &gt;= 6.0 for double atomicAdd (else a workaround define) |
| **Platforms** | x86-64 Linux documented (CPU via BLAS); NVIDIA GPUs via CUDA; other platforms not documented |
| **Thread safety** | not documented; Solver methods are const and operate on caller-owned buffers, and the CPU backend uses its own dispenso thread pool (numThreads setting, default 16) |
| **Drop-in for the baseline** | partial — same problem (sparse SPD Cholesky) but a different block-structured API, internal permuted ordering, and supernodal only; no cholmod_\* compatible interface |

## Gotchas

- Numeric data and vectors live in the solver's internal reordered layout; use the accessor/paramToSpan permutation to load values and map results back
- The CUDA path is not deterministic when sparse-elimination ranges exist (atomic adds in factor and solve); the CPU path is deterministic given deterministic BLAS
- Default Settings use 16 threads and an untuned computation model; the README advises re-fitting the model (bench -Z plus opt_comp_model) per CPU/BLAS/GPU
- Every entry is a block; matrices with no block structure become 1x1 blocks and run slightly slower, and very large parameter blocks fit the thread/kernel design poorly

## Known shortcomings

- Compiler and flags not stated; with MKL it is 15-23% slower than CHOLMOD on some problem types; CUDA numbers compare GPU build against CPU CHOLMOD.
- With OpenBLAS only 4-17% faster than CHOLMOD on FLAT; CPU single-RHS solve \~2.1-2.5x slower than CHOLMOD on FLAT 1000; symbolic analysis \~3.5-4x slower on sparse FLAT; no comparison with CHOLMOD's GPU path; supernodal only, no update/downdate or LDL^T; CUDA path nondeterministic with sparse-elimination ranges; issues page not reviewed.

## Caveats and trade-offs

First-party synthetic benchmarks; compiler/flags not stated. With Intel MKL BaSpaCho is slower than CHOLMOD on some problem types (+15..+23%). CUDA numbers compare GPU BaSpaCho to CPU CHOLMOD. 112 stars; built for Theseus differentiable optimization.

Supernodal only; README says simplicial/banded matrices better served by CHOLMOD or Eigen; GPU path needs CUDA

## Maintenance

Maintained at low volume by Meta research (76 commits, last commit 2025-10-08, 112 stars) and MIT-licensed, so copyable, but the CMake/BLAS/CUDA build is not trivial to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded D-&gt;C: repo's BENCHMARK_RESULTS.md has first-party timings vs CHOLMOD from benchmarking/bench on a Xeon Silver 4214 + Quadro RTX 5000, but compiler and flags are not stated, so not A.
- **Verifier notes:** MIT, 112 stars, not archived, last commit 2025-10-08 (active). Shortcoming to record: CPU wins are modest and not uniform; MKL runs show regressions vs CHOLMOD on several problem types.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/facebookresearch/baspacho>
  - <https://github.com/facebookresearch/baspacho/commits>
  - <https://raw.githubusercontent.com/facebookresearch/baspacho/HEAD/BENCHMARK_RESULTS.md>
  - <https://raw.githubusercontent.com/facebookresearch/baspacho/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/facebookresearch/baspacho>
  - <https://raw.githubusercontent.com/facebookresearch/baspacho/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebookresearch/baspacho/HEAD/BENCHMARK_RESULTS.md>
  - <https://raw.githubusercontent.com/facebookresearch/baspacho/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebookresearch/baspacho/HEAD/baspacho/baspacho/Solver.h>
  - <https://raw.githubusercontent.com/facebookresearch/baspacho/HEAD/baspacho/baspacho/Accessor.h>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/facebookresearch/baspacho`) · [data/wave8/enrich/raw/github_com_facebookresearch_baspacho.json](../../../data/wave8/enrich/raw/github_com_facebookresearch_baspacho.json) (enrichment confidence 0.8)

</details>
