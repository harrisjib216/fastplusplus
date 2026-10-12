# COSMA

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Communication-optimal distributed (MPI) matrix multiply with a ScaLAPACK p?gemm drop-in; beats MKL ScaLAPACK and Cray LibSci pdgemm.

| | |
|---|---|
| **Beats** | Intel MKL ScaLAPACK pdgemm (also Cray LibSci, Cray LibSci_acc, CARMA, CTF) |
| **Claimed result** | README text: 'speedups by factor of up to 8.3x over the second-fastest algorithm' (no supporting table on the README). CP2K RPA 128-H2O on 1024 Piz Daint GPU nodes: the 46 pdgemm calls took 75.26 s with COSMA-GPU vs 139.82 s with Cray LibSci_acc 19.10.1 (README 'approximately 2x faster'; 1.86x derived from page data). On 128 nodes: CPU-only COSMA 1723.62 s vs Intel MKL 19.0.1.144 ScaLAPACK 1836.85 s vs Cray LibSci 5896.45 s for the pdgemm calls (1.07x over MKL derived from page data; table annotation '\~10% faster'; whole CP2K run 2238.94 s vs 2305.41 s), COSMA-GPU 257.99 s vs LibSci_acc 338.47 s (1.31x derived from page data; README '25-27% faster than the second best'). Square matrices on 128 nodes vs MKL ScaLAPACK: plot annotated '\~2x faster on CPU' (about 300 vs 150 GFlop/s at n=20000, narrowing to about 740 vs 565 at n=120000, read from plot) and '\~3x faster on GPU' (GPU COSMA vs CPU-only MKL). |
| **Workload** | Distributed matrix-matrix multiplication (communication-optimal, with a ScaLAPACK pxgemm wrapper): CP2K RPA benchmark of 128 water molecules (46 tall-and-skinny pdgemm calls) and square matrices, on Piz Daint. |
| **Metric** | throughput |
| **Hardware** | Piz Daint: CP2K runs on Cray XC50 GPU-partition nodes (Intel Xeon E5-2690 v3 @ 2.60GHz 12 cores, NVIDIA Tesla P100 16GB), 128 and 1024 nodes; square-matrix runs on 128 XC50 (GPU) and XC40 (CPU-only) nodes |
| **Adoption** | 219 stars; integrated in CP2K |
| **Last commit** | 2026-07-29 |
| **Links** | [repository](https://github.com/eth-cscs/COSMA) · [benchmark](https://github.com/eth-cscs/COSMA) |

## Verdict

On Piz Daint (Cray XC50 nodes with Xeon E5-2690 v3 and Tesla P100, 2019), CP2K's 128-water RPA benchmark spent 75.3 s in pdgemm with GPU COSMA vs 139.8 s with Cray LibSci_acc 19.10.1 on 1024 nodes; on 128 nodes CPU COSMA took 1723.6 s vs 1836.9 s for MKL 19.0.1.144 ScaLAPACK and 5896.5 s for Cray LibSci. The SC19 paper (abstract via search snippet) reports up to 12.8x and 2.2x average over ScaLAPACK, CARMA and CTF; compiler and flags are not stated.

## Use it when

- Distributed dense GEMM on clusters, especially tall-and-skinny or otherwise non-square shapes where 2D ScaLAPACK grids waste communication (CP2K RPA: 46 tall-and-skinny pdgemm calls)
- Fortran or C codes already calling ScaLAPACK pdgemm that want a speedup by relinking only
- GPU-accelerated nodes where matrices start in host memory: GPU COSMA was about 1.86x Cray LibSci_acc on 1024 Piz Daint nodes and 1.31x on 128
- Square multiplications at moderate node counts on CPU, where the README plot shows about 2x over MKL ScaLAPACK at n=20000 narrowing to about 1.3x at n=120000

## Skip it when

- Single-node or shared-memory GEMM: it is an MPI algorithm that calls a local BLAS (MKL, OpenBLAS, BLIS, cuBLAS, rocBLAS) for the actual work
- Memory-tight runs: open issue #118 reports CP2K gradient pdgemm calls (m=n=17,408, k=3,473,408) running out of CPU/GPU memory where ScaLAPACK fit, needing about 3x the nodes
- Anything beyond GEMM: no factorizations or other PBLAS/ScaLAPACK routines are provided
- Expecting large wins over Intel MKL ScaLAPACK in production on CPU: the CP2K 128-node pdgemm time improved only about 7% (1723.6 s vs 1836.9 s)
- Build environments with AMD or other non-MKL/OpenBLAS BLAS and COSMA_BLAS=auto: open issue #171 reports the CMake search stopping early

## How it is fast

It derives a near-optimal sequential schedule from a red-blue pebble game I/O lower bound and then parallelizes it, choosing the processor decomposition from m, n, k, p and memory instead of fixing a 2D (SUMMA) or 2.5D grid upfront; it may idle some ranks to get a better grid. The paper reports up to sqrt(3) less communication than 2D/3D algorithms, which matters most for tall-and-skinny shapes. Buffers are preallocated and reused, local reshuffling is minimized via the COSTA layout-transform library, communication can overlap computation, and GPU runs pipeline tiles through Tiled-MM (cuBLAS/rocBLAS) with optional NCCL/RCCL or GPU-aware MPI.

## Compared with alternatives

Pick COSMA over SPLA (also eth-cscs, pdgemm-compatible) when you want the more general, peer-reviewed algorithm with native-layout and multi-GPU (NCCL/RCCL) options; SPLA's own README claims parity with COSMA on CPU and a lead on GPU, so benchmark both on GPU nodes. Tiled-MM is the single-node GPU engine COSMA itself uses, and node-local BLAS siblings (Eigen, BLASFEO, OpenBLAS forks) solve a different problem.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | MPI 3, a BLAS backend (MKL, OpenBLAS, BLIS, ATLAS, Cray LibSci, NVPL, custom, or CUDA/ROCm), optional ScaLAPACK (MKL, Cray LibSci, NVPL, custom) for the p?gemm wrappers, optional NCCL/RCCL; bundled submodules COSTA, Tiled-MM, semiprof, gtest_mpi |
| **Minimum toolchain** | C++14 (cxx_std_14), CMake 3.24 per CMakeLists.txt (the README still says 3.17) |
| **Platforms** | Linux clusters with MPI; CPU any architecture with a BLAS, NVIDIA GPUs via CUDA, AMD GPUs via ROCm; Spack and Docker recipes provided |
| **Thread safety** | not documented (each MPI rank uses OpenMP/BLAS threads set via OMP_NUM_THREADS and MKL_NUM_THREADS) |
| **Drop-in for the baseline** | partial — the pxgemm wrapper library matches ScaLAPACK p?gemm signatures exactly and is selected by link order, but only the gemm routines are replaced, the layout transform costs some throughput versus the native layout, and ScaLAPACK is still needed for everything else |

## Gotchas

- Link order matters: libcosma_pxgemm must come before any other library providing p?gemm, otherwise the ScaLAPACK version is silently used
- Releases before v2.8.3 (April 2024) read the user's C matrix even when beta=0, so uninitialized or NaN-filled C could corrupt results; the fix shipped in COSTA 2.3.1, so use COSMA 2.8.4 or later
- COSMA_CPU_MAX_MEMORY caps per-rank memory but throws runtime_error if the multiplication cannot fit, and the README marks it as still in testing
- Clone with --recursive: COSTA and Tiled-MM are submodules, and COSMA_BLAS must be set explicitly (the CMake default OFF is a fatal error, despite the README calling MKL the default)

## Known shortcomings

- Against MKL in CP2K small the win is about 7% (pdgemm 1723.62 vs 1836.85 s); the 2x is vs LibSci_acc; paper unread here (arXiv blocked).
- Correctness bug fixed in v2.8.3 (COSTA 2.3.1): pdgemm read C even when beta=0; open issue #118 memory blow-up (CP2K needed about 3x the nodes ScaLAPACK did); open issue #171 CMake BLAS auto-detect broken; README says CMake 3.17 but CMakeLists needs 3.24.

## Caveats and trade-offs

Peer-reviewed (SC19 Best Student Paper; ACM DL and arXiv:1908.09606 linked from README) but the paper could not be opened in this run (arxiv.org and mirrors blocked); its abstract, seen only as a web-search snippet, reports up to 12.8x (2.2x on average) over ScaLAPACK, CARMA and CTF, while the README says up to 8.3x over the second-fastest algorithm. Against MKL ScaLAPACK in the CP2K workload the CPU win is small (about 7% on pdgemm time, 3% on total run time); the 2x and 3x figures are against Cray LibSci_acc or compare GPU COSMA with CPU-only MKL. README result tables are SVG/plot images. Compiler and flags not stated; results are from 2019 with MKL 19.0.1.144, Cray LibSci 19.06.1 and LibSci_acc 19.10.1.

MPI-based, needs a local BLAS (MKL, LibSci, OpenBLAS, BLIS, cuBLAS, rocBLAS) and optionally ScaLAPACK for the wrapper; distributed-memory only; speedups depend on matrix shape and node count; the ScaLAPACK-layout wrapper costs some throughput versus the native layout.

## Maintenance

Maintained by ETH Zurich/CSCS (last commit 2026-07-29, latest release v2.8.4 from April 2024, 219 stars, used in CP2K), BSD-3-Clause, with 7 open issues including memory blow-up and CMake BLAS-detection bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SC19 paper (ACM DOI 10.1145/3295500.3356181, Best Student Paper, linked from the README) plus README result tables naming CPU/GPU models (Xeon E5-2690 v3, Tesla P100) and baseline versions (MKL 19.0.1.144, LibSci 19.06.1, LibSci_acc 19.10.1); miniapps (miniapp/cosma_miniapp, pxgemm_miniapp) are public but compiler and flags are not stated, so not A.
- **Verifier notes:** README tables (rendered from docs/\*.svg) confirm the 2x and 25-27% claims; the record's numbers were correct but the MKL margin in the production workload is only about 7%. Metadata verified: BSD-3-Clause, 219 stars, not archived, last commit 2026-07-29.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/eth-cscs/COSMA>
  - <https://github.com/eth-cscs/COSMA/commits>
  - <https://raw.githubusercontent.com/eth-cscs/COSMA/HEAD/README.md>
  - <https://raw.githubusercontent.com/eth-cscs/COSMA/HEAD/docs/square-results.svg>
  - <https://raw.githubusercontent.com/eth-cscs/COSMA/HEAD/docs/cp2k-results-128.svg>
  - <https://raw.githubusercontent.com/eth-cscs/COSMA/HEAD/docs/cp2k-results-1024.svg>
- **Sources the enricher read:**
  - <https://github.com/eth-cscs/COSMA>
  - <https://github.com/eth-cscs/COSMA/issues>
  - <https://github.com/eth-cscs/COSMA/issues/118>
  - <https://github.com/eth-cscs/COSMA/issues/171>
  - <https://github.com/eth-cscs/COSMA/releases>
  - <https://raw.githubusercontent.com/eth-cscs/COSMA/HEAD/README.md>
  - <https://raw.githubusercontent.com/eth-cscs/COSMA/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/eth-cscs/COSMA/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/COSMA/HEAD/src/cosma/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/COSMA/HEAD/LICENSE>
  - WebSearch snippet for arXiv 1908.09606 abstract (arxiv.org egress-blocked)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/eth-cscs/cosma`) · [data/wave8/enrich/raw/github_com_eth_cscs_cosma.json](../../../data/wave8/enrich/raw/github_com_eth_cscs_cosma.json) (enrichment confidence 0.75)

</details>
