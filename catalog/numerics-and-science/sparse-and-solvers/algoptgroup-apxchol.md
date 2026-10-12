# apxchol (parallel approximate-Cholesky PCG for Laplacian and SDDM systems)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++ (optional CUDA)` · `BSD-4-Clause (LICENSE file)` · 🟢 active

> Parallel randomized approximate-Cholesky PCG for graph-Laplacian and SDDM systems; beats hypre BoomerAMG on total solve time.

| | |
|---|---|
| **Beats** | hypre BoomerAMG (CPU and GPU builds); AMGCL, RCHOL and ParAC are also in the comparison |
| **Claimed result** | Derived from benchmarks/daint/results.csv (total time, CPU apxchol 'bg+tree' vs competitor): geometric-mean 5.7x faster than CPU BoomerAMG (median 4.6x, min 1.6x, max 123x, faster on all 26 matrices where both finished); 2.4x geometric mean vs CPU AMGCL (median 1.2x, faster on 21 of 27, slower on 6); 33x vs ParAC; GPU apxchol vs GPU BoomerAMG only 1.04x geometric mean (faster on 14 of 26). |
| **Workload** | Setup plus solve time to 1e-8 true residual of the original system on 27 matrices (grids, interior-point matrices, SuiteSparse/SNAP graphs), one right-hand side, 72 threads on a GH200 node, median-total repetition after a warmup. |
| **Metric** | latency |
| **Hardware** | NVIDIA GH200 node (72-core Grace CPU plus Hopper GPU), 72 threads |
| **Compiler and flags** | Not stated on the benchmark page. The later Daint snapshot (benchmarks/daint/results.csv, not the 2b755997 campaign the headline ratios come from) records Clang 22.1.8 with libomp for CPU apxchol rows, GCC 14.3 for GPU GKS rows and NVCC with GCC 14.3 host for GPU trace rows; competitor rows say only 'clang' or 'julia'. Build is CMake Release with APXCHOL_NATIVE_ARCH on by default (-mcpu=native on ARM, -march=native on x86); exact flags of the measured binaries are not listed. |
| **Adoption** | 8 stars; developed at ETH Zurich |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/AlgOptGroup/apxchol) · [benchmark](https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/daint/results.csv) |

## Verdict

The authors measured setup plus solve to a 1e-8 true relative residual, one right-hand side, 72 threads on a CSCS Daint GH200 node; from the refreshed summary table the CPU build is a geometric-mean 5.7x faster than CPU hypre BoomerAMG (26 of 26 matrices) and 2.4x faster than AMGCL (faster on 18, tied on 3 and slower on 6 of 27, derived from page data), while the labelled historical campaign 2b755997 reports 3.3x over BoomerAMG and 1.7x over AMGCL with AMGCL winning 16 of 26. Compiler versions come from a later CSV snapshot and exact flags of the measured binaries are not listed; all numbers are first-party.

## Use it when

- Large graph Laplacians from social, web or collaboration networks with skewed degrees: in the authors' GH200 table it takes 4.68 s on com-LiveJournal against 149 s for BoomerAMG and 83.7 s for AMGCL, and 0.76 s on as-Skitter against 69.8 s and 6.8 s.
- Interior-point Laplacian/SDDM systems that change every iteration, where AMG setup is expensive: about 0.3 s against 7.6-9.9 s for AMGCL on the iter0020-iter0040 matrices.
- Many right-hand sides on one fixed Laplacian (factor once with cpu_solver, then solve or apply repeatedly), from C++, Python or Octave.
- Multicore CPU servers where you can pin threads across NUMA domains; the solver is memory-bandwidth bound and the README gives placement guidance.

## Skip it when

- General SPD matrices that are not Laplacian or SDDM (for example elasticity or most higher-order FEM systems): only Laplacian and SDDM inputs are supported.
- Regular grids and FEM meshes where AMG already works well: AMGCL matched or beat it on grid_500, grid3d_100, grid_5000, parabolic_fem, kron_g500-logn16 and com-Orkut, and BoomerAMG needs 7-9 PCG iterations where apxchol needs 30-50.
- Projects that need bit-reproducible results across thread counts: the docs state a fixed seed does not give byte-identical parallel factors, so iteration counts can vary between runs.
- Licensing-sensitive or GPL projects: the BSD-4-Clause advertising clause is not OSI-approved and is GPL-incompatible.
- Expecting a GPU win for a single right-hand side: in the historical GH200 campaign the CPU build was faster than its own GPU build (CPU/GPU total-time ratio 0.461, solve-only 0.853).

## How it is fast

It implements Kyng-Sachdeva style approximate Gaussian elimination: when a vertex is eliminated, the dense clique it would create is replaced by a few sampled edges (Gao-Kyng-Spielman 'GKS' sampler by default, a 'trace_cycle' sampler as an option), so the factor stays about as sparse as the graph. Elimination is parallelized with OpenMP by eliminating independent sets of low-degree vertices per round (block-greedy selection capped at the lowest 20% by current degree), then Baumann-Kyng style rounds on the dense residual and a short serial peel. Factor and triangular-solve arrays are stored in FP32 (optionally scaled FP16) while PCG vectors stay FP64; the CUDA build adds a synchronization-free dataflow triangular solve and a GPU-resident PCG.

## Compared with alternatives

Pick apxchol over AMGCL when the systems are graph Laplacians of skewed-degree networks or interior-point SDDM matrices, where it wins by up to 31x in the authors' tables; keep AMGCL for general SPD problems and for grids and FEM meshes, where it ties or wins. Against LAMG+, which also targets graph Laplacians, apxchol offers a C++ library with OpenMP and CUDA builds and Python bindings, but no head-to-head between the two was found.

## Integration

| | |
|---|---|
| **Form** | static lib built from source with CMake (no install rules in the root CMakeLists), plus a CPU-only PyPI wheel |
| **Dependencies** | Eigen 3.3+ (fetched if absent) for the core; optional OpenMP (may need libatomic for long-double reductions) and CUDA (cudart only); CLI11, spdlog and fast_matrix_market are fetched for the CLI; GoogleTest for tests |
| **Minimum toolchain** | C++23 compiler, CMake 3.16+; CUDA device code compiled as C++20 (nvcc 13.x noted); measured builds used Clang 22 with libomp and GCC 14.3 |
| **Platforms** | x86-64 and aarch64 (measured on GH200 Grace and EPYC 7742); NVIDIA GPUs optional; -march=native / -mcpu=native is on by default; CPU FP16 factor storage needs F16C; PyPI 0.2.2 wheels are Linux x86-64 only (CPython 3.10-3.14) |
| **Thread safety** | cpu_solver solve/apply calls are not safe concurrently on the same object (shared reused PCG workspace, per solve.h); separate solver objects are independent. Internal parallelism is OpenMP and the library never changes thread affinity. |
| **Drop-in for the baseline** | partial — the apx_cholesky preconditioner fits Eigen's iterative-solver interface, but replacing hypre BoomerAMG means a different API and only Laplacian/SDDM inputs |

## Gotchas

- The library's default build uses -march=native, so binaries are not portable to older CPUs; turn off APXCHOL_NATIVE_ARCH for redistributable builds.
- Thread placement matters more than thread count: on an EPYC 7742 socket, 32 threads spread over 4 NUMA domains took 0.77 of the 16-threads-on-one-domain time, and all 64 cores were slower than 32; pin threads explicitly with OMP_PLACES.
- For a singular (connected) Laplacian the returned x is the minimum-norm solution with mean zero, whatever constant component the warm start had; a wrong-length x0 throws std::invalid_argument.
- APXCHOL_POOL_FP32=OFF does not make it an all-FP64 solver: the assembled factor stays FP32 and GPU triangular solves default to scaled FP16.

## Known shortcomings

- BSD-4-Clause (not OSI-approved, advertising clause), so usability is reference; compiler versions come from a later snapshot's results.csv, not the headline campaign 2b755997; no flags; AMGCL beats apxchol on 16 of 26 CPU matrices.
- Record corrected: vs CPU AMGCL it is faster on 18 of 27 matrices, tied on 3 and slower on 6 (recomputed from summary.md), not 21 of 27. Results differ between runs because factors are not repeatable across thread counts (docs/precision.md). Its CPU build beats its own GPU build for one right-hand side (CPU/GPU ratio 0.461). Default build is -march=native.

## Caveats and trade-offs

First-party benchmark by the library authors; the headline page is a labelled historical snapshot (campaign 2b755997) and not a measurement of current main, and its numbers differ from the refreshed benchmarks/daint/summary.md tables. The page does not say how per-matrix competitor/apxchol ratios are averaged. AMGCL beats apxchol on 16 of 26 CPU matrices in that campaign; the 1.735x CPU ratio over AMGCL comes mostly from interior-point and social-graph systems (in summary.md AMGCL takes 7.56-9.92 s on iter0020-iter0040 vs about 0.32 s, and 83.74 s vs 4.68 s on com-LiveJournal), while AMGCL is as fast or faster on grids, parabolic_fem, kron_g500-logn16 and com-Orkut. Pairs where a solver timed out, failed or did not converge are excluded from the ratios (hypre timed out on as-Skitter, com-LiveJournal, com-Orkut and com-Youtube on CPU). 'SuiteSparse' in the tables means matrices from the SuiteSparse Matrix Collection, not the SuiteSparse library; the baselines (hypre, AMGCL) are not SuiteSparse, Eigen sparse or PETSc. Licensed BSD-4-Clause (advertising clause), which is not OSI-approved, so usability is reference rather than copyable. Young repo (benchmark docs dated 2026-09). [retier] Recount from summary.md: versus CPU AMGCL apxchol is faster on 18 of 27 matrices, tied on 3 and slower on 6 (the earlier '21 of 27' overstated it). Factors are not repeatable across thread counts.

Graph-Laplacian and SDDM systems only, not general SPD; approximate factor used as a PCG preconditioner; needs a C++23 compiler and Eigen (fetched if absent); CPU solve is memory-bound, so thread placement across NUMA domains matters (0.77 relative time at 32 threads over 4 domains vs 1.00 at 16 threads on one domain).

## Maintenance

Active ETH Zurich research code (354 commits, last commit 2026-09-30, PyPI 0.2.2 from 2026-07-27, 8 stars, no issues filed); usable from source or pip, but the BSD-4-Clause advertising clause limits it to reference use in this catalog.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Daint GH200 campaign (benchmarks/daint/fair_t72_summary.md, campaign 2b755997) with public drivers (benchmarks/sweep_fair.py, benchmarks/CMakeLists.txt) and every claimed ratio and win count present; but the page states no compiler or flags, and the toolchain column in benchmarks/daint/results.csv belongs to a later snapshot that does not include campaign 2b755997, so not A.
- **Verifier notes:** All claimed numbers (3.267x/23 of 23, 3.555x/25 of 25, 1.735x with 10 wins/16 losses vs AMGCL, GPU 2.028x/25 of 26 and 1.835x/22 of 26) are on fair_t72_summary.md. Fixed usability (BSD-4-Clause is not OSI-approved) and clarified that the compiler versions come from a later snapshot's CSV. Stars 8, 3 forks, not a fork, not archived, last commit 2026-09-30 all confirmed.
- **Fields the verifier corrected:** `usability`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/daint/fair_t72_summary.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/daint/summary.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/daint/README.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/daint/PLATFORM.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/daint/results.csv>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/README.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/LICENSE>
  - <https://github.com/AlgOptGroup/apxchol>
  - <https://github.com/AlgOptGroup/apxchol/commits>
- **Sources the enricher read:**
  - <https://github.com/AlgOptGroup/apxchol>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/README.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/CPU-RESIDUAL-BLOCKED.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/docs/precision.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/include/apxchol.h>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/include/apxchol/solver/factor_options.h>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/include/apxchol/solver/solve.h>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/include/apxchol/solver/preconditioner.h>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/daint/fair_t72_summary.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/daint/summary.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/daint/PLATFORM.md>
  - <https://raw.githubusercontent.com/AlgOptGroup/apxchol/HEAD/benchmarks/daint/results.csv>
  - <https://github.com/AlgOptGroup/apxchol/issues?q=is%3Aissue>
  - <https://pypi.org/pypi/apxchol/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/algoptgroup/apxchol`) · [data/wave8/enrich/raw/github_com_algoptgroup_apxchol.json](../../../data/wave8/enrich/raw/github_com_algoptgroup_apxchol.json) (enrichment confidence 0.8)

</details>
