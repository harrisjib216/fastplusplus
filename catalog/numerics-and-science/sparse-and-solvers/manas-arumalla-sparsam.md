# sparsam

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> From-scratch C++20 SLAM/pose-graph backend whose own block-sparse Cholesky beats GTSAM 4.2 on M3500, not Ceres on BA.

| | |
|---|---|
| **Beats** | GTSAM 4.2.1 (PyPI wheel driven through its Python bindings) on 2D pose graphs; Ceres 2.2 on BAL bundle adjustment |
| **Claimed result** | docs/benchmarks/m5.md: on M3500 (3500 poses) with both stacks converging to final chi-squared within 0.009%, sparsam GN (7 iterations) takes 0.078 s vs GTSAM GN (8 iterations) 0.133 s as in-sweep medians of 5, and 0.066 s vs 0.141 s standalone after cooldown; the author states the defensible claim as 1.7-2.1x faster end to end. Against Ceres 2.2 on BAL Ladybug (README), sparsam is slower in wall clock (1.74 s vs 0.67 s on ladybug-49, 1.57 vs 0.48 s on ladybug-73, 9.9 vs 4.9 s on ladybug-138, 26.5 vs 24.0 s on ladybug-318) but 552 vs 1091 ms per iteration on ladybug-318. |
| **Workload** | End-to-end Gauss-Newton/LM optimization of the 2D M3500 pose graph using sparsam's own block-sparse Cholesky with AMD ordering, versus GTSAM 4.2; bundle adjustment on BAL Ladybug versus Ceres 2.2. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 8940HX |
| **Compiler and flags** | GCC 13.3 -O3, single-threaded, Eigen 3.4.0 dense fixed-size kernels (docs/benchmarks/m4.md, m5.md); GTSAM side is the prebuilt gtsam==4.2.1 PyPI wheel (numpy&lt;2), build flags not stated |
| **Adoption** | 1 star; repository created July 2026 |
| **Last commit** | 2026-08-08 |
| **Links** | [repository](https://github.com/Manas-arumalla/sparsam) · [benchmark](https://github.com/Manas-arumalla/sparsam/blob/main/docs/benchmarks/m5.md) |

## Verdict

Author-run on an AMD Ryzen 9 8940HX laptop, single-threaded, GCC 13.3 -O3, median of 5: on M3500 both stacks converge to chi2 137.9 and sparsam's GN takes 0.078 s in-sweep (0.066 s standalone) against 0.133 s (0.141 s) for GTSAM 4.2.1's GN called through its prebuilt PyPI wheel, about 1.7-2.1x end to end with matched stopping criteria and a fresh backend per rep. Against Ceres 2.2 on BAL Ladybug it reaches the same final cost but is slower in wall clock on all four problems, though faster per iteration on ladybug-318 (552 vs 1091 ms).

## Use it when

- 2D pose-graph SLAM on Manhattan-style datasets (M3500-like, thousands of poses) where a single-threaded GN solve under 0.1 s matters and you can avoid GTSAM.
- You want a dependency-light estimation backend (C++20 + Eigen 3.4 only, no SuiteSparse, no Boost) to vendor and read.
- Teaching, auditing or extending a SLAM backend: each component has a committed derivation doc and analytic-vs-numeric Jacobian tests.
- Large 2D TORO graphs (M10000) from odometry initialization, where its GN reached chi2/dof about 1.2 in about 1 s and GTSAM 4.2's LM stalled in the author's runs.

## Skip it when

- Bundle adjustment where wall clock matters: Ceres 2.2 was 1.1-3.3x faster on BAL Ladybug (e.g. 1.74 s vs 0.67 s on ladybug-49), because its trust-region damping needs 2.2-3.5x fewer iterations.
- Fill-heavy 3D pose graphs: the README says GTSAM's per-iteration linear algebra is about 3-5x faster there; there are no supernodes yet.
- Problems where you rely on LM: its LM plateaus on M3500 (2.8e3 after 60 iterations, where GN and GTSAM's LM reach 137.9) and hits the 200-iteration cap on several hard sets.
- Multi-core or GPU solving: everything is single-threaded; use BaSpaCho, CHOLMOD or GTSAM with TBB instead.
- Production use: project created July 2026, version 0.1.0, 1 star, one author; the README architecture lists batch GN/LM/GNC only, with no incremental smoothing (iSAM2-style).

## How it is fast

The normal equations H = J^T Sigma^-1 J are assembled into its own CSR-of-blocks storage and factored by a left-looking simplicial block Cholesky with dense per-block kernels; symbolic analysis, ordering and all storage are built once per problem and reused across iterations and LM retries with no reallocation (lambda is folded into the numeric pass). The fill-reducing ordering is a self-written quotient-graph approximate minimum degree (AMD, Amestoy-Davis-Duff degree bound), which takes M3500 factor+solve from 1623 ms (natural order) to 4.45 ms. The M3500 end-to-end win also comes from needing 7 GN iterations to GTSAM's 8.

## Compared with alternatives

Pick sparsam over BaSpaCho or Sympiler only when you want the whole nonlinear SLAM loop (factors, Lie groups, GN/LM/GNC) in one small dependency-free C++20 codebase for 2D pose graphs; for raw sparse Cholesky speed on large or fill-heavy systems, BaSpaCho's supernodal CPU/GPU factorization (benchmarked against CHOLMOD) is the stronger choice.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target sparsam; the code lives in headers under src/sparsam and the library compiles only version.cpp) |
| **Dependencies** | Eigen 3.4 (dense types only); GoogleTest fetched for tests; Ceres and GTSAM (Python wheel) only for the off-by-default SPARSAM_BUILD_BENCH oracles |
| **Minimum toolchain** | C++20, CMake 3.22; benchmarks built with GCC 13.3 |
| **Platforms** | Linux x86-64 is the only platform the benchmarks name; no SIMD intrinsics in the linear-algebra headers read, other platforms not documented |
| **Thread safety** | not documented; the code is single-threaded and backend/factorization objects hold mutable workspaces, so share none across threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Fail-closed I/O and numerics: unknown g2o/TORO tags, non-PSD information matrices and gapped key sets throw instead of being skipped, so some datasets other tools ingest are rejected.
- Its Pose2 error uses the true SE(2) log, while GTSAM's default Pose2 local chart is first-order; chi2 values differ by 2.6% (M3500) up to 27-61% on rotation-heavy sets before convergence, so unconverged chi2 is not comparable across the two.
- BlockCholesky keeps a pointer to its BlockPattern (the rvalue constructor is deleted); the pattern must outlive the factorization, and one SparseBackend instance serves one fixed graph structure (adding factors after the first linearize throws).
- Each block is a separately allocated Eigen::MatrixXd, so very small blocks pay allocation and indirection costs that a supernodal solver avoids.

## Known shortcomings

- Baseline GTSAM was the 4.2.1 pip wheel; SLAM/pose-graph solver, a loose fit for sparse-and-solvers.
- Wins on 2D pose graphs only (1.7-2.1x vs GTSAM on M3500, partly from 7 vs 8 iterations). Ceres is faster on bundle adjustment and GTSAM is 3-5x faster per iteration on 3D graphs. Single-threaded, v0.1.0.

## Caveats and trade-offs

Mixed result that the README itself states: Ceres wins wall clock on bundle adjustment (1.1-3.3x, mostly from fewer iterations), and on fill-heavy 3D pose graphs GTSAM's per-iteration linear algebra is about 3-5x faster than sparsam's simplicial block Cholesky. The M3500 speedup is end to end GN (7 vs 8 iterations), not a like-for-like factorization time, and the author notes laptop boost-clock state moves both numbers by about 15%. GTSAM was timed through its Python wheel (optimize() call only, median of 5) with wheel build flags unknown. sparsam's own LM plateaus on M3500 where GTSAM's LM converges. Author-run on one laptop; project created July 2026 with 1 star. Category fit is loose: a nonlinear least-squares/SLAM backend whose core is a from-scratch block-sparse Cholesky; baselines are GTSAM and Ceres, not SuiteSparse, Eigen sparse or PETSc.

SLAM and estimation backend written from scratch in C++20 using only the standard library and Eigen dense fixed-size types; own CSR-of-blocks storage, AMD/RCM ordering and simplicial block Cholesky. Not a general sparse solver API. Benchmarks need GTSAM and Ceres built behind an off-by-default CMake flag.

## Maintenance

Active one-author project (latest commit 2026-08-08, created July 2026) under MIT with careful, reproducible benchmark records; copyable, but young and SLAM-specific rather than a general sparse solver.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmarks/m5.md gives the M3500 GN timings against GTSAM 4.2.1 (0.078 s vs 0.133 s in-sweep median of 5, 0.066 s vs 0.141 s standalone) with GCC 13.3 -O3, AMD Ryzen 9 8940HX, single-threaded, and the regeneration commands; the harness is public (bench/pgo2d_bench.cpp for sparsam, python/bench_m5_gtsam.py timing gtsam.GaussNewtonOptimizer.optimize() median-of-5) with raw CSVs committed.
- **Verifier notes:** Numbers in the record match the README and m5.md; benchmark_url pointed at the repo root, corrected to m5.md. Repo page: MIT, 1 star, 0 forks, not archived; latest commit 2026-08-08, oldest visible 2026-07-18.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/README.md>
  - <https://github.com/Manas-arumalla/sparsam>
  - <https://github.com/Manas-arumalla/sparsam/commits>
  - <https://github.com/Manas-arumalla/sparsam/tree/main/docs/benchmarks>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/docs/benchmarks/m4.md>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/docs/benchmarks/m5.md>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/python/bench_m5_gtsam.py>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/bench/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/README.md>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/docs/benchmarks/m5.md>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/docs/benchmarks/m4.md>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/python/bench_m5_gtsam.py>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/src/sparsam/linear/block_cholesky.hpp>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/src/sparsam/linear/sparse_backend.hpp>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/src/sparsam/linear/ordering.hpp>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/bench/pgo2d_bench.cpp>
  - <https://raw.githubusercontent.com/Manas-arumalla/sparsam/HEAD/bench/bench_util.hpp>
  - <https://github.com/Manas-arumalla/sparsam/tree/main/src/sparsam/linear>
  - <https://github.com/Manas-arumalla/sparsam/issues>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/manas-arumalla/sparsam`) · [data/wave8/enrich/raw/github_com_manas_arumalla_sparsam.json](../../../data/wave8/enrich/raw/github_com_manas_arumalla_sparsam.json) (enrichment confidence 0.8)

</details>
