# SpLLT (task-based sparse Cholesky)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Fortran` · `BSD-3-Clause` · 🔴 abandoned

> Task-based supernodal sparse Cholesky (Fortran) on OpenMP, StarPU or PaRSEC; papers report parity with HSL_MA87, not a speedup.

| | |
|---|---|
| **Beats** | HSL_MA87 (HSL parallel sparse Cholesky) |
| **Claimed result** | None on opened pages (README and Sphinx docs have no performance data). WebSearch snippets of the authors' papers (pages blocked, not opened; snippet only) say the OpenMP and StarPU implementations show 'comparable performance' to HSL_MA87 on a multicore architecture, which is parity rather than a speedup. |
| **Workload** | Parallel supernodal sparse Cholesky factorization of symmetric positive definite matrices on multicore, with OpenMP, StarPU and PaRSEC task backends, compared by the authors' papers with HSL_MA87; no numbers on any opened page. |
| **Metric** | throughput |
| **Adoption** | 6 stars, 1 fork; NLAFET project code from STFC Rutherford Appleton Laboratory (BSD-3-Clause, copyright 2018 STFC) |
| **Last commit** | 2019-08-23 |
| **Links** | [repository](https://github.com/NLAFET/SpLLT) |

## Verdict

No numbers exist in the repo or on any reachable page. The authors' papers (Duff, Hogg and Lopez, NACO 2018, doi 10.3934/naco.2018014; a PaRSEC/PTG paper in IJHPCA, doi 10.1177/1094342019888567), seen only as search snippets because epubs.stfc.ac.uk and aimsciences.org are blocked, say the OpenMP, StarPU and PaRSEC versions perform comparably to HSL_MA87 on a multicore machine, which is parity; compiler, BLAS and hardware are unknown. The comparison drivers in the repo (drivers/run_ma87.f90 with metis_order, drivers/spllt_test.F90 via spllt_analyse, which forces ssids_opt%ordering = 1) both use METIS ordering, so open issue #2's ordering concern does not apply to them.

## Use it when

- Research on runtime systems for sparse direct solvers: the same Cholesky algorithm implemented on OpenMP, StarPU and PaRSEC, which you can compare side by side.
- Multicore SPD factorization where HSL_MA87's licence is a problem and a BSD-3-Clause code with roughly MA87-level speed (per the authors' papers, snippet only) is acceptable.
- Fortran codes that already depend on SPRAL and want a Cholesky-only path whose tasks can be handed to StarPU or PaRSEC; CMake also has USE_GPU (MAGMA, CUDA) and USE_MPI options, status not documented.

## Skip it when

- Indefinite or unsymmetric matrices: Cholesky only, no pivoting.
- When you need evidence of a speedup: the repo has no numbers, the papers claim parity with HSL_MA87, and no comparison with CHOLMOD, PARDISO or PaStiX was found.
- Current toolchains without patching: gfortran 10+ stops on a rank mismatch in spllt_kernels_mod.F90 unless -fallow-argument-mismatch is added (issue #4); CI only ever ran gcc-6 on Travis, and the code has been unmaintained since 2019.
- C or C++ projects wanting a small dependency: you need a Fortran compiler, SPRAL, METIS 5.1, hwloc, BLAS/LAPACK and a runtime, and the CMake build has no install target (install(TARGETS spllt) is commented out).

## How it is fast

Each supernode is cut into nb x nb tiles and the factorization becomes a DAG of tile tasks (factorize diagonal block, triangular solve, intra-node update, inter-node update_between), the same DAG-based scheme as HSL_MA87. A runtime system schedules the tasks as their dependencies resolve: OpenMP 4 tasks with depend clauses, StarPU in sequential-task-flow style, or PaRSEC with a parameterized task graph. Tree pruning (prune_tree, on by default) folds small subtrees into single coarse tasks to limit scheduling overhead, and the solve phase also runs as a DAG of forward and backward substitution tasks. The goal is to match MA87 performance while staying portable across runtimes, not to beat it.

## Compared with alternatives

Pick SpLLT only to study or reuse one Cholesky algorithm across OpenMP, StarPU and PaRSEC. For production SPD factorization, BaSpaCho (measured gains over CHOLMOD) or SPRAL SSIDS (maintained, also handles indefinite systems) are better-supported choices, and SyLVER, from the same NLAFET project, is a related DAG-based symmetric solver.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | SPRAL (SSIDS analyse), METIS 5.1, BLAS/LAPACK (MKL in the README examples), hwloc, and one of StarPU, PaRSEC or an OpenMP 4.0 compiler; optional CUDA and MAGMA for USE_GPU |
| **Minimum toolchain** | Fortran 2003 compiler with iso_c_binding plus C compiler, CMake 2.6+; gfortran 6 in CI, gfortran 10+ needs -fallow-argument-mismatch; GNU or Intel compilers for the OpenMP build |
| **Platforms** | Linux multicore x86-64 (KNL build option); other platforms not documented |
| **Thread safety** | not documented; parallelism is internal to spllt_factor and spllt_solve through the chosen runtime |
| **Drop-in for the baseline** | partial — same analyse/factor/solve structure as HSL_MA87, but different derived types and option names, so call sites must be rewritten |

## Gotchas

- The default CMake build type is RelWithDebInfo, which appends -fcheck=all -Wall to the Fortran flags, so an unconfigured build runs with array-bounds and runtime checks on; use -DCMAKE_BUILD_TYPE=Release before timing. The default RUNTIME is STF (sequential), options ncpu defaults to 1 and nb to 16, so parallel speed needs -DRUNTIME=OMP|StarPU|Parsec plus explicit ncpu and a larger tile size.
- The OpenMP build adds -fopenmp or -qopenmp only when the C++ compiler is GNU or Intel; with any other compiler (Clang) CMake just sets an ERROR variable and continues, producing a build without OpenMP.
- The OpenMP benchmark driver drivers/spllt_omp_bench.F90 does not compile against the current API (wrong spllt_solve and spllt_compute_solve_dep signatures, issue #1), and after the reporter's fix the run hit an out-of-bounds access on fkeep%sbc; issues #1-#4 from 2022 have no maintainer reply.
- The C binding's spllt_inform_t returns num_flops and num_factor as 32-bit C int while the Fortran fields are 64-bit, so they overflow on any sizeable factorization; it also expects 1-based CSC (nnz is read as ptr(n+1)-1 and the array_base option is commented out).

## Known shortcomings

- No numbers anywhere in the repo; paper snippets say only 'comparable performance' to HSL_MA87, so parity rather than faster. Fortran, abandoned since 2019-08-23, 6 stars. Kept at D under the keep-and-document rule.
- Enricher: the default RelWithDebInfo build adds -fcheck=all; defaults are the sequential STF scheduler with ncpu 1 and nb 16; a clang OpenMP build silently gets no -fopenmp; drivers/spllt_omp_bench.F90 does not compile (issue #1) and after a fix reads fkeep%sbc out of bounds; gfortran 10+ needs -fallow-argument-mismatch (issue #4); the C binding passes num_flops and num_factor as 32-bit C int against 64-bit Fortran (overflow); no install target. spllt_analyse forces METIS like run_ma87.f90, so the issue #2 ordering concern is moot.

## Caveats and trade-offs

No numeric comparison on any page opened, so tier D; claims come only from search snippets (snippet only) of the authors' papers (Duff, Hogg and Lopez, NACO 2018, doi 10.3934/naco.2018014; Duff and Lopez on PaRSEC; an IJHPCA paper, doi 10.1177/1094342019888567) saying the OpenMP, StarPU and PaRSEC versions show 'comparable performance' to HSL_MA87 on a multicore architecture, i.e. parity, not a speedup. HSL_MA87 is itself a licensed HSL code. Comparisons against CHOLMOD or PaStiX were not found. Papers on epubs.stfc.ac.uk and aimsciences.org were EGRESS_BLOCKED. The repo has bench_kernels/ and scripts/ but no published results. Last commit 2019-08-23 (abandoned), Travis CI badge only. Fortran rather than C++; callable from C++ through its C interface (interfaces/). Low notability (6 stars). Kept as a seed record for the catalogue; a paper-access retier could add the tables.

Fortran (with a C interface in interfaces/C and a C example) plus C++ kernel benchmarks (bench_kernels: gemm, potrf, syrk, trsm). Symmetric positive definite systems only. Needs SPRAL for the analysis phase, Metis 5.1, BLAS/LAPACK (MKL in the README examples), hwloc, CMake, and one runtime: StarPU, PaRSEC or OpenMP 4.0+. Sequential build by default.

## Maintenance

Abandoned since 2019-08-23 (710 commits, 6 stars, four 2022 issues unanswered, Travis CI on gcc-6 only); BSD-3-Clause and usable as a research reference, but expect to patch the build for gfortran 10+ and to supply SPRAL, METIS 5.1, hwloc and a runtime yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null; the README, doc/ (Sphinx sources only) and scripts/ hold no performance data, and the papers comparing SpLLT with HSL_MA87 are on blocked hosts (epubs.stfc.ac.uk EGRESS_BLOCKED); search snippets only say 'comparable performance', so no numbers and tier D.
- **Verifier notes:** Metadata checked on github.com: BSD-3-Clause (LICENSE, 2018 STFC), 6 stars, 1 fork, 710 commits, last commit 2019-08-23 'minor bugfix'. Shortcomings: not claimed faster than HSL_MA87 (parity per paper snippets), no numbers reachable, abandoned, low notability; would be a not-notable-tier-d reject under the prompt's rules, kept as confirm D per the keep-and-document policy.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** paper access (epubs.stfc.ac.uk blocked); paper access (parity with MA87 only)
- **Pages the verifier opened:**
  - <https://github.com/NLAFET/SpLLT>
  - <https://github.com/NLAFET/SpLLT/commits/master>
  - <https://github.com/NLAFET/SpLLT/tree/master>
  - <https://github.com/NLAFET/SpLLT/tree/master/doc>
  - <https://github.com/NLAFET/SpLLT/tree/master/scripts>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/README.md>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/NLAFET/SpLLT>
  - <https://github.com/NLAFET/SpLLT/issues>
  - <https://github.com/NLAFET/SpLLT/issues/1>
  - <https://github.com/NLAFET/SpLLT/issues/2>
  - <https://github.com/NLAFET/SpLLT/issues/4>
  - <https://github.com/NLAFET/SpLLT/tree/master/src>
  - <https://github.com/NLAFET/SpLLT/tree/master/drivers>
  - <https://github.com/NLAFET/SpLLT/tree/master/scripts>
  - <https://github.com/NLAFET/SpLLT/tree/master/bench_kernels>
  - <https://github.com/NLAFET/SpLLT/tree/master/interfaces>
  - <https://github.com/NLAFET/SpLLT/tree/master/interfaces/C>
  - <https://github.com/NLAFET/SpLLT/tree/master/example>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/README.md>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/src/spllt_analyse_mod.F90>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/src/spllt_mod.F90>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/src/spllt_c_interface.F90>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/src/spllt_data_mod.F90>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/src/spllt_factorization_task_mod.F90>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/src/task_manager_omp.F90>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/interfaces/C/spllt_data_ciface.F90>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/drivers/run_ma87.f90>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/drivers/spllt_test.F90>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/spllt_test.F90>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/scripts/stress_test.sh>
  - <https://raw.githubusercontent.com/NLAFET/SpLLT/HEAD/scripts/generator_case_omp.sh>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nlafet/spllt`) · [data/wave8/enrich/raw/github_com_nlafet_spllt.json](../../../data/wave8/enrich/raw/github_com_nlafet_spllt.json) (enrichment confidence 0.6)

</details>
