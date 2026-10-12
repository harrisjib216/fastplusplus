# Ginkgo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> C++17 sparse linear algebra library with portable CUDA/HIP/SYCL/OpenMP kernels; beat AmgX AMG and MAGMA batched solves in DOE apps.

| | |
|---|---|
| **Beats** | NVIDIA AmgX; MAGMA batched dense; MA57; LAPACK dgbsv |
| **Claimed result** | Mixed-precision AMG \~1.5x faster than AmgX on one MFEM case (20-40% faster preconditioner application per iteration); BatchBicgstab \~2x over MAGMA batched dense; \~90% less solver time than LAPACK dgbsv in XGC; 1.8-2.4x faster ACOPF on MI250X vs MA57 CPU baseline |
| **Workload** | GPU mixed-precision AMG, batched iterative solvers, sparse solves in AC-OPF |
| **Metric** | throughput |
| **Hardware** | AMD MI250X, NVIDIA V100, Perlmutter, Crusher |
| **Adoption** | 612 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/ginkgo-project/ginkgo) · [benchmark](https://journals.sagepub.com/doi/10.1177/10943420241268323) |

## Verdict

The IJHPCA 2024 ECP paper reports: Ginkgo AMG with 20-40% faster per-iteration preconditioner application than NVIDIA AmgX on a V100 (MFEM), and mixed-precision AMG 1.5x faster on one L-shape case; batched BiCGStab about 2x over MAGMA's batched dense direct solve in PeleLM (MI250X, Frontier); about 90% less linear-solver time than LAPACK dgbsv in XGC (Perlmutter A100, Crusher MI250X); and 1.8-2.4x end-to-end over a CPU MA57 baseline on MI250X for ACOPF (1.05-1.3x on V100). That last result compares GPU against CPU. Compiler flags are not stated.

## Use it when

- Iterative solves of large sparse systems on NVIDIA, AMD or Intel GPUs where you want one codebase across vendors
- Many small independent sparse systems per step (chemistry or combustion kinetics, per-cell plasma solves) through the batched BiCGStab/GMRES solvers
- Replacing NVIDIA AmgX with a vendor-neutral AMG preconditioner, especially in mixed precision
- Moving a CPU sparse direct solve (MA57- or LAPACK-banded-style) onto GPUs to remove host-device round trips
- Distributed solves via the MPI module (GPU-aware MPI recommended)

## Skip it when

- Small or one-off CPU-only sparse solves: Eigen/SuiteSparse are simpler, and no CPU-vs-SuiteSparse benchmark is cited
- Sparse direct factorization of hard 3D problems: the IJHPCA paper says the direct solvers lack supernodal techniques, so CHOLMOD/MUMPS-class solvers are likely stronger
- AMG needing aggressive or alternative coarsening: only parallel graph-matching coarsening is supported per the paper
- Strong scaling on many nodes: the paper names communication as the bottleneck
- Builds with limited compile time or memory: full GPU builds are heavy (INSTALL.md warns of &gt;20 min and high memory for the Jacobi kernels with full optimizations)

## How it is fast

Each backend gets hand-written kernels for its hardware (CUDA, HIP, SYCL), so nothing goes through a generic translation layer. The speedups in the measured cases come from mixed-precision AMG (coarse levels in lower precision, fine level in full precision, parallel graph-matching coarsening), batched iterative solvers that solve many small independent sparse systems inside one GPU kernel, and GPU-resident sparse direct factorization and triangular solves. Half and bfloat16 value types, plus adaptive-precision block-Jacobi, cut memory traffic in these memory-bound kernels.

## Compared with alternatives

Choose Ginkgo over AMGCL when you need full solver stacks on AMD or Intel GPUs, batched small-system solvers, or mixed-precision AMG. Choose it over CSR5, merge-spmv or ISpMV when you need complete solvers and preconditioners rather than one SpMV kernel, and over BaSpaCho or Sympiler when an iterative or batched method fits better than a supernodal Cholesky.

## Integration

| | |
|---|---|
| **Form** | shared lib (static optional via BUILD_SHARED_LIBS=OFF); CMake find_package(Ginkgo), target Ginkgo::ginkgo |
| **Dependencies** | none for the core/reference build; optional CUDA 11+, ROCm 6.2+ (hipBLAS, hipSPARSE, rocRAND, rocThrust), oneAPI 2024.1+ (oneMKL, oneDPL), OpenMP, MPI 3.1+, METIS, PAPI |
| **Minimum toolchain** | C++17; CMake 3.16+; GCC 7+, Clang 5+, Intel 2019+, MSVC 2019+, NVHPC 22.7+ |
| **Platforms** | Linux, macOS, Windows; x86-64/aarch64 CPUs (OpenMP); NVIDIA (CUDA), AMD (HIP), Intel (SYCL) GPUs |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Half precision needs CUDA compute capability 5.3+ and bfloat16 needs 8.0+ unless built with CUDA 12.2+
- GINKGO_JACOBI_FULL_OPTIMIZATIONS gives the best adaptive block-Jacobi but greatly increases compile time and memory
- Windows builds can hit 'export ordinal too large' (needs -O1) and cc1plus out-of-memory errors
- The headline numbers come from application integrations (MFEM, PeleLM, XGC, ExaSGD), not from a standalone kernel shootout

## Known shortcomings

- 1.8-2.4x over MA57 compares a GPU against a CPU; no flags given.
- Paper says sparse direct solvers lack supernodal acceleration, AMG only graph-matching coarsening, communication limits strong scaling; headline numbers from application integrations (MFEM, PeleLM, XGC, ExaSGD), not a kernel shootout; no CPU comparison against SuiteSparse.

## Caveats and trade-offs

Peer-reviewed (IJHPCA 2024) but baselines are not the listed SuiteSparse/Eigen/PETSc; paper itself has no direct PETSc or cuSPARSE comparison. Flags not stated.

Many-core GPU focus (CUDA/HIP/SYCL); C++17

## Maintenance

Actively developed (612 stars, commits through 2026-09) under BSD-3-Clause with an OpenSSF best-practices badge and CI on GitLab, so it is safe to adopt as a dependency, but it is too large to vendor as source.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed IJHPCA 2024 paper reports Ginkgo mixed-precision AMG \~1.5x faster than AmgX (20-40% per-iteration), BatchBicgstab \~2x over MAGMA batched, and 1.8-2.4x ACOPF vs MA57 CPU baseline; no compiler flags, so not A.
- **Verifier notes:** Numbers confirmed on the SAGE page; the MA57 comparison is GPU vs CPU (hardware-confounded). Repo BSD-3-Clause, 612 stars, last commit 2026-09-30, active.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** first-party OpenFOAM integration (hpsim/OGL, OGL_DATA boxTurb16 v0.1-108): OpenFOAM native CG on one Xeon Gold 6230 process 36.04 s vs Ginkgo CUDA on a V100 21.93 s at resolution 64 (about 1.64x, derived from page data), BiCGStab 2.0x, GPU slower at resolution 32; Meccanica paper claims up to 8x / about 15x (snippet only)
- **Pages the verifier opened:**
  - <https://journals.sagepub.com/doi/10.1177/10943420241268323>
  - <https://github.com/ginkgo-project/ginkgo>
  - <https://github.com/ginkgo-project/ginkgo/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ginkgo-project/ginkgo/HEAD/README.md>
  - <https://raw.githubusercontent.com/ginkgo-project/ginkgo/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ginkgo-project/ginkgo/HEAD/BENCHMARKING.md>
  - <https://raw.githubusercontent.com/ginkgo-project/ginkgo/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/ginkgo-project/ginkgo/HEAD/ABOUT-LICENSING.md>
  - <https://raw.githubusercontent.com/ginkgo-project/ginkgo/HEAD/include/ginkgo/core/base/executor.hpp>
  - <https://journals.sagepub.com/doi/10.1177/10943420241268323>
  - <https://github.com/ginkgo-project/ginkgo>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ginkgo-project/ginkgo`) · [data/wave8/enrich/raw/github_com_ginkgo_project_ginkgo.json](../../../data/wave8/enrich/raw/github_com_ginkgo_project_ginkgo.json) (enrichment confidence 0.75)

</details>
