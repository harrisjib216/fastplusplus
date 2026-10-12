# AMGCL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++ algebraic multigrid solver library; sets up AMG preconditioners faster than Trilinos ML and PETSc GAMG on shared memory.

| | |
|---|---|
| **Beats** | PETSc (GAMG); Trilinos ML; CUSP |
| **Claimed result** | docs/benchmarks.rst (first-party), shared-memory 3D Poisson with 150^3 = 3,375,000 unknowns on dual Xeon E5-2640 v3, CG with smoothed-aggregation AMG: AMGCL sets up the solver about 20-100% faster than Trilinos ML and 4-7x faster than PETSc, and overall CPU performance is on par with Trilinos. Medians computed from the published raw data in docs/smem_data/poisson/{amgcl,trilinos,petsc}.txt (derived from page data): setup on 1 core 3.97 s, against 6.81 s for Trilinos (1.7x) and 27.87 s for PETSc (7.0x); on 16 cores 0.92 s against 1.00 s (1.09x) and 3.57 s (3.9x). Total setup+solve on 1 core 11.58 s against 15.28 s (1.32x) and 49.72 s (4.3x); on 16 cores 2.33 s against 2.48 s (1.06x) and 5.87 s (2.5x). GPU (Tesla K80): AMGCL/CUDA is slightly better than CUSP, and its total time is only about 30% better than CPU AMGCL or Trilinos. Distributed memory: about 3x slower than Trilinos AMG in MareNostrum 4 weak scaling (2.5x faster than Trilinos DD-ML), and 2.5x slower than Trilinos/AMG at 384 cores on SuperMUC. |
| **Workload** | 3D Poisson problem on shared memory, AMG setup and solve times |
| **Metric** | other |
| **Hardware** | Dual Intel Xeon E5-2640 v3; Tesla K80; MareNostrum 4, PizDaint, SuperMUC for distributed |
| **Compiler and flags** | Not stated. The public harness (ddemidov/amgcl_benchmarks, top-level CMakeLists.txt) sets only C++11 plus the OpenMP and MPI compile flags. For CUDA it sets nvcc arch 'Kepler Maxwell Pascal' with -Xcompiler -fopenmp -fPIC. No CMAKE_BUILD_TYPE or -O level, compiler name or version, or PETSc, Trilinos or CUDA version is recorded in the repo or in docs/benchmarks.rst. |
| **Adoption** | 871 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/ddemidov/amgcl) · [benchmark](https://amgcl.readthedocs.io/en/latest/benchmarks.html) |

## Verdict

On a dual Xeon E5-2640 v3 node, solving a 3D Poisson finite-difference system (3,375,000 unknowns, 23.5M nonzeros) with AMG-preconditioned CG, the author's docs report AMGCL (OpenMP) setup about 20-100% faster than Trilinos ML and 4-7x faster than PETSc (both via MPI), with overall CPU time on par with Trilinos; a Tesla K80 CUDA run cut solve time 3-4x but total time only about 30%. Compiler and flags are not stated.

## Use it when

- Single-node solves of large elliptic/PDE systems (millions of unknowns) where you rebuild the preconditioner often and setup time matters.
- C++ codes that want an AMG preconditioner without adopting PETSc or Trilinos data structures or build systems.
- Solve-heavy workloads on a GPU (CUDA, OpenCL, HIP) where solution phase alone was 3-4x faster than CPU on the docs' Poisson test.
- Block-structured systems (elasticity, Navier-Stokes) using static block value types or field-split Schur pressure correction.
- Mixed precision or custom value types via template specialization.

## Skip it when

- Large distributed-memory runs: the project's own weak-scaling test shows AMGCL about 3x slower than Trilinos AMG, and PETSc scales better than both on shared memory.
- You need a direct solver or robust black-box behaviour on hard indefinite or highly anisotropic problems; open issues report convergence trouble on a 3D structural problem (#300).
- Total time-to-solution on GPU for one-shot solves: setup always runs on the CPU, so CUDA total time was only about 30% better than OpenMP AMGCL.
- 32-bit targets (open i386 build failure, #312) or very large CUDA problems (int overflow, #287).
- Strict bitwise reproducibility across thread counts unless you define AMGCL_DETERMINISTIC_REDUCTIONS (may be slower on many cores).

## How it is fast

The AMG hierarchy (e.g. smoothed aggregation coarsening) is built on the CPU with OpenMP using shared-memory data structures, avoiding the distributed-memory bookkeeping that the docs blame for PETSc's and Trilinos' slower setup. After setup the hierarchy is moved to a backend (builtin OpenMP, CUDA/cuSPARSE, VexCL/OpenCL, ViennaCL, HIP), so the solve phase runs on GPUs transparently. Cheap default smoothers (SPAI0) and static block value types (e.g. 4x4 blocks) cut setup cost and memory traffic; Schur pressure-correction field-split preconditioners handle coupled systems like Navier-Stokes.

## Compared with alternatives

Pick AMGCL over Ginkgo when you want a small header-only AMG with fast CPU setup and runtime-configurable solvers; pick Ginkgo for GPU-first sparse work where its AMG beat NVIDIA AmgX. Unlike BaSpaCho or Sympiler (direct Cholesky), AMGCL is iterative and suits very large PDE systems where factorization fill-in is too costly.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | OpenMP (recommended); Boost.property_tree only for the runtime interface (removable with AMGCL_NO_BOOST); per-backend extras: CUDA/cuSPARSE/Thrust, VexCL (Boost + OpenCL/CUDA), ViennaCL, ROCm hipSPARSE/rocSPARSE; MPI 3.0 for distributed solvers; optional Eigen, METIS/Scotch, PaStiX |
| **Minimum toolchain** | C++ standard not documented for the core; CMake 3.10+ for the bundled build; HIP backend requires C++17 |
| **Platforms** | any with a C++ compiler (GCC, Clang, Intel, MSVC configured in CMake); GPUs via CUDA, OpenCL or HIP; i386 build currently broken per open issue |
| **Thread safety** | not documented (setup and builtin backend are internally OpenMP-parallel) |
| **Drop-in for the baseline** | partial — replaces PETSc/Trilinos ML AMG preconditioning with a different C++ template API; adapters accept CRS arrays, Eigen and Epetra matrices, but solver options and defaults differ |

## Gotchas

- Benchmarks compare each library on its default smoother (AMGCL SPAI0, Trilinos symmetric Gauss-Seidel, PETSc damped Jacobi), so iteration counts and solve time are not like-for-like.
- OpenMP reductions give last-bit differences with different thread counts by default; define AMGCL_DETERMINISTIC_REDUCTIONS to fix.
- Heavy template composition means long compile times and large binaries (MSVC needs /bigobj, set by the CMake target).
- Open issue #291 reports growing memory when called repeatedly from a pybind11 module.

## Known shortcomings

- Win is mostly solver setup time (metric 'build-time' means setup); overall CPU speed on par with Trilinos; distributed runs 2.5-3x worse than Trilinos.
- Each library ran its default smoother; open issues: i386 build failure (#312), int overflow in CUDA backend (#287), memory growth when called repeatedly from pybind11 (#291).

## Caveats and trade-offs

First-party docs page; compiler flags not stated; hardware is old (Xeon E5-2640 v3, Tesla K80). The win is mainly in setup time; overall CPU performance is on par with Trilinos, and PETSc scales better. Smoothers differ between libraries (AMGCL SPAI0; Trilinos symmetric Gauss-Seidel; PETSc damped Jacobi, both on defaults). Distributed-memory runs on the same page show AMGCL about 3x worse than Trilinos AMG in one weak-scaling test and 2.5x slower at 384 cores in another. GPU speedup is over CPU AMGCL, not over a baseline library. [retier] First-party comparison by AMGCL's author. The harness (ddemidov/amgcl_benchmarks) and the raw timing files (docs/smem_data, docs/dmem_data) are public, but compiler, flags, build type and library versions are not recorded anywhere. The hardware is old (Xeon E5-2640 v3, Tesla K80), and the results predate current AMGCL, PETSc and Trilinos releases. The CPU win is mainly in setup time: at 16 cores AMGCL's total is within 6% of Trilinos ML. Each library ran its default smoother (AMGCL SPAI0; Trilinos symmetric Gauss-Seidel; PETSc damped Jacobi), and iteration counts differ widely (AMGCL 24, Trilinos 11, PETSc 7 at 1 core), so this is a defaults-vs-defaults comparison. PETSc scales better than both. In distributed runs AMGCL is about 3x slower than Trilinos AMG in one weak-scaling test and 2.5x slower at 384 cores in another. The GPU speedup is measured against CPU AMGCL, not against a baseline library. The readthedocs page is egress-blocked here; its source docs/benchmarks.rst on GitHub was read instead.

Header-only; OpenMP/OpenCL/CUDA backends; solver setup speed, not necessarily solve time

## Maintenance

Actively maintained (release 1.4.9 in June 2026, 871 stars, 59 open issues), MIT-licensed and header-only, so easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party docs page compares AMGCL with PETSc and Trilinos ML on a 3D Poisson problem (3,375,000 unknowns) on dual Xeon E5-2640 v3 and states the 20-100% / 4-7x setup claims verbatim; compiler and flags are not given, so not A, and it is not peer-reviewed or independent.
- **Verifier notes:** Numbers verified on the page (docs/benchmarks.rst). The record's metric 'build-time' really means AMG solver setup time; the orchestrator may want to relabel it (metric is not a correctable field). The arXiv paper 1811.05704 only says performance is 'on par with alternative implementations', so no B upgrade.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://amgcl.readthedocs.io/en/latest/benchmarks.html>
  - <https://raw.githubusercontent.com/ddemidov/amgcl/HEAD/docs/benchmarks.rst>
  - <https://github.com/ddemidov/amgcl>
  - <https://github.com/ddemidov/amgcl/commits>
  - <https://arxiv.org/abs/1811.05704>
- **Sources the enricher read:**
  - <https://github.com/ddemidov/amgcl>
  - <https://github.com/ddemidov/amgcl/issues>
  - <https://raw.githubusercontent.com/ddemidov/amgcl/HEAD/README.md>
  - <https://raw.githubusercontent.com/ddemidov/amgcl/HEAD/docs/benchmarks.rst>
  - <https://raw.githubusercontent.com/ddemidov/amgcl/HEAD/docs/index.rst>
  - <https://raw.githubusercontent.com/ddemidov/amgcl/HEAD/docs/design.rst>
  - <https://raw.githubusercontent.com/ddemidov/amgcl/HEAD/docs/compiling.rst>
  - <https://raw.githubusercontent.com/ddemidov/amgcl/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ddemidov/amgcl`) · [data/wave8/enrich/raw/github_com_ddemidov_amgcl.json](../../../data/wave8/enrich/raw/github_com_ddemidov_amgcl.json) (enrichment confidence 0.8)

</details>
