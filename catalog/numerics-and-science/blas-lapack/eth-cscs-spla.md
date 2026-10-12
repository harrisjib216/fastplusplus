# SPLA

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> MPI(+CUDA/ROCm) library for tall-and-skinny distributed GEMM with stripe layouts; outscales MKL ScaLAPACK pzgemm and Cray LibSci_acc.

| | |
|---|---|
| **Beats** | Intel MKL ScaLAPACK pdgemm (also COSMA and Cray LibSci_acc) |
| **Claimed result** | README text: on CPU 'performance is much better compared to Intel MKL and similar to COSMA'; on GPU 'SPLA significantly outperforms COSMA and LIBSCI_ACC'. Plots (complex double PZGEMM-equivalent, M=N=10k, K=1M, block size 500), read from plot: CPU at 36 sockets SPLA about 0.305 vs MKL ScaLAPACK about 0.304 TFLOPS/socket (parity) and COSMA about 0.31; at 484 sockets SPLA about 0.26 vs MKL about 0.163 (about 1.6x) and COSMA about 0.235. GPU (host memory input) at 36 nodes SPLA about 4.0 vs COSMA about 2.6 vs LibSci_acc about 1.73 TFLOPS/node (about 2.3x over LibSci_acc); at 484 nodes about 1.65 vs 1.0 vs 0.27 (about 6x over LibSci_acc). |
| **Workload** | Distributed tall-and-skinny complex matrix multiplication (pgemm_ssb stripe-stripe-block, expressed as an equivalent pzgemm call), M=N=10k, K=1M, block size 500, 36-484 sockets/nodes on Piz Daint: CPU nodes 2x18-core Xeon E5-2695 v4 (two ranks per node), GPU nodes Xeon E5-2690 v3 + Tesla P100 (one rank per node). |
| **Metric** | throughput |
| **Hardware** | Piz Daint multi-core: 2 x Intel Xeon E5-2695 v4 @ 2.10GHz (2 x 18 cores); Piz Daint GPU: Xeon E5-2690 v3 + NVIDIA Tesla P100 16GB |
| **Adoption** | 33 stars |
| **Last commit** | 2024-06-25 |
| **Links** | [repository](https://github.com/eth-cscs/spla) · [benchmark](https://github.com/eth-cscs/spla) |

## Verdict

First-party README plots from Piz Daint (CPU: 2x18-core Xeon E5-2695 v4, two ranks per node; GPU: Xeon E5-2690 v3 + Tesla P100, one rank per node) for complex double M=N=10k, K=1M, block size 500: on CPU SPLA reaches parity with MKL ScaLAPACK at 36 sockets and about 1.6x at 484, and on GPU about 2.3x to 6x over LibSci_acc (values read from plots). Benchmark code exists in tests/programs/benchmark_scalapack.cpp, which times spla::pgemm_ssb and pzgemm/pdgemm on the same 1-D grid (100 repeats by default), but compiler, flags and library versions are not stated.

## Use it when

- Plane-wave / electronic-structure style products of two very tall stripe-distributed matrices (k in the millions, m and n in the thousands), e.g. wavefunction overlap A^H\*B, where the README case is M=N=10k, K=1M complex double.
- Runs at higher node counts where communication dominates: the README CPU plot shows parity with MKL ScaLAPACK at 36 sockets but about 1.6x per socket at 484 sockets (values read from plot).
- GPU clusters with CUDA or ROCm, especially when A, B and C already live in device memory; the README GPU plot shows SPLA ahead of COSMA and Cray LibSci_acc at every node count from 36 to 484.
- Codes already using SIRIUS (its CMakeLists requires SPLA 1.4.0+) or needing a cuBLASXt-like local gemm that mixes host and device pointers.

## Skip it when

- General square or block-cyclic-by-block-cyclic distributed GEMM: SPLA only covers the stripe-stripe-block and stripe-block-stripe patterns; use ScaLAPACK p?gemm or COSMA.
- Small CPU runs: at low rank counts COSMA is faster because SPLA must assign at least one block per rank for the ring (README), and SPLA only matches MKL at 36 sockets.
- GPU runs with host-memory inputs at large node counts: blocks shrink, data is re-copied to the GPU more often and host-GPU bandwidth becomes the limit (README).
- Projects needing active maintenance: last commit 2024-06-25 (v1.6.1, a HIP 6.0 fix), with open build issues (#35 SPLA_BUILD_EXAMPLES configuration failure, #24 tests fail to link, #17/#18 CMake package config).
- Single-node or non-MPI applications: MPI is a hard requirement even for the library build.

## How it is fast

pgemm_ssb is a distributed reduction (every rank contributes to every C element), and SPLA does it with a ring pattern after Del Ben et al.'s GW work (SC20): each rank computes a different block, passes the partial sum to its neighbour while computing the next one, and several block groups are interleaved so communication overlaps local zgemm calls. Internal block sizes are chosen independently of the output layout (with a final redistribution), and on GPUs each block runs on its own CUDA/HIP stream synchronized individually for MPI, which gives finer overlap than COSMA's grouped streams. Data can stay in device memory, avoiding host-to-GPU copies that otherwise limit scaling.

## Compared with alternatives

Pick SPLA over COSMA when the operands are tall-skinny stripes with C block-cyclic, particularly on GPUs or with device-resident data, where SPLA's plot shows it ahead at every node count; COSMA is the better choice for general shapes and for CPU runs below about 196 sockets. Tiled-MM (same group) covers only single-node GPU GEMM against cublasXt, not distributed products.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | MPI (required), BLAS chosen via CMake BLA_VENDOR (MKL, OpenBLAS, BLIS, ArmPL, Cray LibSci), optional OpenMP, optional CUDA (cudart + cuBLAS) or ROCm (HIP + rocBLAS); tests download googletest and CLI11 |
| **Minimum toolchain** | C++17 compiler, CMake 3.18+, CUDA 11.0+ for the CUDA backend (v1.6.0 release notes); Fortran compiler only for SPLA_FORTRAN=ON |
| **Platforms** | Linux HPC clusters; x86-64 and aarch64 hosts (ArmPL support since 1.5.3), NVIDIA GPUs via CUDA, AMD GPUs via ROCm |
| **Thread safety** | not documented; the library throws MPIThreadSupportError ('MPI multi-threading support not sufficient') when the MPI thread level is too low, and the Context owns mutable buffers, so sharing one Context across threads is not documented as safe |
| **Drop-in for the baseline** | partial — the benchmark expresses pgemm_ssb as an equivalent pzgemm('C','N') on a 1-D process grid, but the API is SPLA's own (Context, MatrixDistribution, local leading dimensions), not a ScaLAPACK descriptor interface |

## Gotchas

- The Context must be destroyed before MPI_Finalize (README example comment), and it holds memory pools whose size can grow with use (allocated_memory_\* accessors); custom allocators can be installed per host, pinned and GPU memory.
- Below a 2mnk operation threshold (op_threshold_gpu) a GPU context may compute on the host instead; tile sizes and the number of tiles are tunable and the README notes a performance jump at 256 nodes when MPI messages cross Piz Daint's protocol threshold, so fixed block sizes may need manual tuning per system.
- Errors are reported as C++ exceptions (GenericError hierarchy) in the C++ API and as SplaError codes in the C API.
- Past bugs: a hang on a 6x6 MPI grid (issue #22, closed) and a deadlock when GPU input memory locations differed across ranks (fixed in 1.5.4); 1.6.0 did not compile with rocBLAS 6.0.2 until 1.6.1.

## Known shortcomings

- Read from plots: 1.6x vs MKL only at 484 sockets, parity at 36; COSMA is ahead up to 196 sockets.
- Correction: benchmark code exists (tests/programs/benchmark_scalapack.cpp times pgemm_ssb vs pzgemm/pdgemm on the same 1-D grid, 100 repeats) but compiler/flags are missing; open build issues #35 #24 #17 #18; past 6x6-grid hang (#22) and a GPU deadlock fixed in 1.5.4.

## Caveats and trade-offs

Plots only, no numeric speedups in the text (figures here are read from plots); compiler, flags and library versions not stated; no benchmark program found in examples/ (tests/ not inspected); one problem size; on CPU the MKL win appears only at higher socket counts (parity at 36 sockets) and COSMA is ahead of SPLA up to about 196 sockets; the GPU comparison does not include MKL; data from about 2020 on Piz Daint hardware.

MPI plus optional CUDA/ROCm; specific matrix distributions (stripe/block) rather than a general ScaLAPACK pdgemm; C++ and C interfaces; can take device-memory input.

## Maintenance

Stale since v1.6.1 (June 2024) but BSD-3-Clause, CMake-installable and used by SIRIUS; expect to fix CMake packaging issues yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README plots (docs/images/spla_cosma_mkl.png, spla_cosma_libsci.png) with named CPUs/GPUs and a stated problem size, but no compiler, flags or benchmark program (examples/ holds only usage examples), so C.
- **Verifier notes:** Numbers read from the two README plots; claims match. Metadata verified: BSD-3-Clause, 33 stars, last commit 2024-06-25 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/eth-cscs/spla>
  - <https://github.com/eth-cscs/spla/commits/master>
  - <https://github.com/eth-cscs/spla/tree/master>
  - <https://github.com/eth-cscs/spla/tree/master/examples>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/README.md>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/docs/images/spla_cosma_mkl.png>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/docs/images/spla_cosma_libsci.png>
- **Sources the enricher read:**
  - <https://github.com/eth-cscs/spla>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/README.md>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/include/spla/spla.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/include/spla/context.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/include/spla/pgemm_ssb.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/include/spla/pgemm_sbs.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/include/spla/gemm.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/include/spla/matrix_distribution.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/include/spla/types.h>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/include/spla/exceptions.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/docs/source/index.rst>
  - <https://github.com/eth-cscs/spla/tree/master/tests>
  - <https://github.com/eth-cscs/spla/tree/master/tests/programs>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/tests/programs/benchmark.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/spla/HEAD/tests/programs/benchmark_scalapack.cpp>
  - <https://github.com/eth-cscs/spla/issues?q=is%3Aissue>
  - <https://github.com/eth-cscs/spla/issues/22>
  - <https://github.com/eth-cscs/spla/releases>
  - <https://raw.githubusercontent.com/electronic-structure/SIRIUS/develop/CMakeLists.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/eth-cscs/spla`) · [data/wave8/enrich/raw/github_com_eth_cscs_spla.json](../../../data/wave8/enrich/raw/github_com_eth_cscs_spla.json) (enrichment confidence 0.8)

</details>
