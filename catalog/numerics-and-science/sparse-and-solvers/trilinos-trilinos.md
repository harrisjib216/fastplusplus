# Basker (ShyLU threaded sparse LU, in Trilinos)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Threaded sparse LU (Trilinos ShyLU-Basker) for low-fill circuit matrices; paper reports 5.9x geomean over sequential KLU on 16 cores.

| | |
|---|---|
| **Beats** | KLU (SuiteSparse) and Intel MKL PARDISO |
| **Claimed result** | Geometric-mean speedup of 5.91x on CPU (16 cores) and 7.4x on Xeon Phi (32 cores) relative to KLU; up to 53x on CPU (16 cores) and 13.3x on Xeon Phi (32 cores) over Intel MKL PARDISO for low fill-in circuit matrices (paper abstract as quoted in search results; paper not opened). |
| **Workload** | Threaded sparse LU factorization of low-fill circuit-type matrices on a 16-core CPU and a 32-core Xeon Phi, versus KLU and MKL PARDISO. |
| **Metric** | latency |
| **Hardware** | Basker README lists tested platforms Intel Sandy/Phi and IBM Power8; exact CPU models not read |
| **Adoption** | Trilinos repo 1.4k stars; Basker lives in packages/shylu/shylu_node/basker |
| **Last commit** | 2026-08-06 |
| **Links** | [repository](https://github.com/trilinos/Trilinos) · [benchmark](https://arxiv.org/abs/1601.05725) |

## Verdict

The Basker paper (Booth, Rajamanickam, Thornquist; ASHES/IPDPS 2016 workshop, arXiv 1601.05725; journal version Parallel Computing 2017) reports, per its abstract seen only in search results, a geometric-mean 5.91x speedup on a 16-core CPU and 7.4x on a 32-core Xeon Phi over sequential KLU on circuit-type matrices, and up to 53x / 13.3x over MKL PARDISO on low-fill matrices. CPU models, compiler and flags, and the matrix list were not visible (the paper hosts are blocked), and the repo carries no benchmark code.

## Use it when

- SPICE-style circuit simulation: low-fill, BTF-reducible Jacobians that are refactored many times with the same pattern on one 8-32 core node.
- You already build on Trilinos (Tpetra/Amesos2) and want a threaded replacement for KLU2 without leaving the stack.
- You need an open-source, BSD-3-licensed threaded KLU-class solver; the circuit-LU siblings NICSLU and CKTSO need license files.
- Real or complex scalars (the Entry template parameter; complex-build fixes landed in March 2025).

## Skip it when

- High-fill matrices from 3D PDE/FEM discretizations: the code is designed for low fill-in, and the large PARDISO margins in the paper apply only to low-fill circuit matrices where supernodal PARDISO is a weak fit; use a supernodal or multifrontal solver there.
- You want to run on a GPU: factorization runs in the Kokkos host execution space; GPU builds since August 2025 only let it coexist with CUDA-enabled Kokkos.
- Distributed memory: through Amesos2 the matrix is gathered to the root MPI rank and factored there, so it does not scale across nodes.
- You need a standalone library: it builds only as a Trilinos subpackage (TriBITS, Kokkos, Teuchos, TrilinosSS); Trilinos 17 requires CMake 3.27 and a C++20 compiler.
- You need reproducible, current numbers: the only speedups are 2016-17 paper figures; the repo has no benchmark harness ('Compiler Option Flags: NA').

## How it is fast

It parallelizes the left-looking Gilbert-Peierls LU kernel that KLU runs serially. A block triangular form (BTF) permutation splits the matrix into many small diagonal blocks, which are factored independently, and one large block. The large block is reordered by nested dissection (METIS or Scotch) into a hierarchical 2D block layout, so threads factor separate subtrees with no communication and then cooperate on separators using point-to-point synchronization instead of global barriers (the paper's 'hierarchical parallelism and data layouts'). Diagonal blocks get AMD ordering and optional max-weight matching.

## Compared with alternatives

Pick Basker over NICSLU and CKTSO, which target the same circuit-matrix niche and claim larger speedups, when you need source code under BSD-3 inside Trilinos; NICSLU is unmaintained and needs a nicslu.lic file. Pick it over GLU or CKTSO-GPU when there is no NVIDIA GPU, or the matrices are too sparse for a GPU to pay off.

## Integration

| | |
|---|---|
| **Form** | static or shared lib (Trilinos subpackage ShyLU_NodeBasker: template headers plus shylubasker.cpp, library shylu_nodebasker) |
| **Dependencies** | Kokkos (OpenMP backend for threads), Teuchos, TrilinosSS (bundled SuiteSparse AMD/BTF/COLAMD); optional METIS or Scotch for nested dissection, MKL, VTune; Amesos2 and Tpetra for the high-level interface |
| **Minimum toolchain** | Trilinos 17.x: C++20 compiler and CMake 3.27+ (release notes); the original 2015 README said C++11 |
| **Platforms** | shared-memory CPUs through Kokkos OpenMP; README lists Intel Sandy Bridge, Xeon Phi and IBM Power8 as tested |
| **Thread safety** | not documented; each Basker object drives its own Kokkos OpenMP thread team, and Kokkos must be initialized with at least the requested number of threads |
| **Drop-in for the baseline** | partial: not API-compatible with KLU's C interface, but the Symbolic/Factor/Solve flow on CSC arrays mirrors it, and inside Amesos2 it swaps with KLU2 behind the same solver interface |

## Gotchas

- SetThreads rounds the thread count down to a power of two and caps it at Kokkos OpenMP concurrency. Inside Amesos2 the default is every hardware thread when OpenMP is enabled.
- The Amesos2 adapter defaults replace_zero_pivot to true, so a zero pivot is silently replaced rather than reported as singular; check residuals. The parameter 'pivot' defaults to false in the valid-parameter list, and passing that list through disables pivoting.
- Symbolic cannot be rerun on the same object ('YOU CANNOT RERUN SYMBOLIC'), so a new sparsity pattern needs a new instance. Factor returns an error when BTF yields no blocks ('Case for btf_nbkls = 0 is not implemented'), so keep btf=true.
- Building with CUDA-enabled Kokkos plus Basker failed with an extended-lambda error (issue #14227, closed December 2025); use a recent Trilinos if you mix backends.

## Known shortcomings

- Only the ShyLU Basker component of Trilinos. Evidence is the Parallel Computing 2017 paper abstract (5.91x geomean vs KLU, up to 53x vs PARDISO); no numbers in the repo.
- Basker's speedups come only from the 2016-17 paper abstract (search snippet); the repo has no harness. It builds only inside Trilinos (17.x needs C++20 and CMake 3.27). The thread count is rounded down to a power of 2; the Amesos2 adapter defaults replace_zero_pivot=true, so zero pivots are silently replaced; under MPI it factors on the root rank only; factorization errors when btf_nblks == 0. Sibling GPU solver Tacho (ShyLU) is not catalogued.

## Caveats and trade-offs

Numbers come from the abstract of the Basker paper (arXiv 1601.05725; journal version Parallel Computing 2017, doi 10.1016/j.parco.2017.06.003) as quoted in WebSearch results; the paper itself could not be opened (arxiv, sciencedirect, osti.gov, adsabs are egress-blocked), so flags, CPU models and the matrix set are unseen. The 5.91x/7.4x KLU figures are geometric means; the 53x/13.3x PARDISO figures are maxima on low-fill circuit matrices, where supernodal PARDISO is a weak fit. Basker's README.txt in the repo lists tested systems (Intel Sandy, Intel Phi, IBM Power8) and has no benchmark numbers or harness ('Compiler Option Flags: NA'). License: the Basker sources and packages/shylu/LICENSE carry 'SPDX-License-Identifier: BSD-3-Clause'. Numbers date from 2016 hardware and the 2016-17 code; the canonical URL is the Trilinos monorepo (Basker lives in packages/shylu/shylu_node/basker).

Built as part of Trilinos (ShyLU) with Kokkos and C++11; depends on SuiteSparse (AMD/BTF/COLAMD) and optionally Scotch 6.0; designed for matrices with low fill-in such as circuit matrices, not a general-purpose replacement for supernodal solvers.

## Maintenance

Actively maintained inside Trilinos (Basker commits through 2026-08-06, adding threaded solve, worker threads and partial factorization in 2025-26) and BSD-3-Clause, but usable only as part of a Trilinos build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: a WebSearch result set shows Basker is peer reviewed (Parallel Computing 2017, 'Basker: Parallel sparse LU factorization utilizing hierarchical parallelism and data layouts', doi 10.1016/j.parco.2017.06.003; earlier version presented at the ASHES/IPDPS 2016 workshop, arXiv 1601.05725), and the quoted abstract gives a geometric-mean 5.91x (16-core CPU) and 7.4x (32-core Xeon Phi) over KLU and up to 53x / 13.3x over MKL PARDISO on low-fill circuit matrices. B rests on venue plus abstract per earlier precedents; the paper itself (arxiv, sciencedirect, osti.gov, adsabs) is blocked and the repo has no benchmark numbers or harness, so not A.
- **Verifier notes:** benchmark_url set to the arXiv preprint whose abstract carries the numbers (search results; not opened, arxiv is blocked); journal version is Parallel Computing 2017 (doi 10.1016/j.parco.2017.06.003). No benchmark_url exists in the repo; the numbers rest on the abstract only. Metadata checked: Trilinos 1.4k stars, 634 forks; Basker directory last commit 2026-08-06 ('fix long/UF_long mismatch in SuiteSparse AMD/BTF/COLAMD calls'), master last commit 2026-09-27; BSD-3-Clause confirmed in shylubasker_def.hpp and packages/shylu/LICENSE.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/trilinos/Trilinos>
  - <https://github.com/trilinos/Trilinos/commits/master>
  - <https://github.com/trilinos/Trilinos/commits/master/packages/shylu/shylu_node/basker>
  - <https://github.com/trilinos/Trilinos/tree/master/packages/shylu/shylu_node/basker>
  - <https://github.com/trilinos/Trilinos/tree/master/packages/shylu/shylu_node/basker/doc>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/shylu/shylu_node/basker/README.txt>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/shylu/shylu_node/basker/src/shylubasker_def.hpp>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/shylu/LICENSE>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/shylu/shylu_node/basker/README.txt>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/shylu/shylu_node/basker/src/shylubasker_def.hpp>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/shylu/shylu_node/basker/src/shylubasker_types.hpp>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/shylu/shylu_node/basker/CMakeLists.txt>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/shylu/shylu_node/basker/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/shylu/shylu_node/basker/cmake/Dependencies.cmake>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/shylu/shylu_node/basker/test/basker_test.cpp>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/packages/amesos2/src/Amesos2_ShyLUBasker_def.hpp>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/RELEASE_NOTES>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/README.md>
  - <https://raw.githubusercontent.com/trilinos/Trilinos/HEAD/INSTALL.rst>
  - <https://github.com/trilinos/Trilinos/commits/master/packages/shylu/shylu_node/basker>
  - <https://github.com/trilinos/Trilinos/tree/master/packages/shylu/shylu_node/basker/test>
  - <https://github.com/trilinos/Trilinos/issues?q=is%3Aissue+basker>
  - <https://github.com/trilinos/Trilinos/issues/14227>
  - <https://github.com/trilinos/Trilinos/pull/14065>
  - <https://github.com/chenxm1986/nicslu>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/trilinos/trilinos`) · [data/wave8/enrich/raw/github_com_trilinos_trilinos.json](../../../data/wave8/enrich/raw/github_com_trilinos_trilinos.json) (enrichment confidence 0.7)

</details>
