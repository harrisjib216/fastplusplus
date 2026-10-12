# GraphBLAST (GraphBLAS on the GPU)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++ (CUDA)` · `Apache-2.0` · 🔴 abandoned

> CUDA implementation of the GraphBLAS API for graph algorithms; paper reports 43.51x geomean over multi-threaded SuiteSparse:GraphBLAS.

| | |
|---|---|
| **Beats** | SuiteSparse:GraphBLAS through LAGraph (CPU) |
| **Claimed result** | Peer-reviewed ACM TOMS paper (Yang, Buluc, Owens, 'GraphBLAST: A High-Performance Linear Algebra-based Graph Framework on the GPU', doi 10.1145/3466795), per its abstract as quoted in search results: 43.51x geometric mean and 1268x peak speedup over SuiteSparse GraphBLAS on multi-threaded CPUs, and on average at least an order of magnitude over SuiteSparse and GBTL. Third-party check in the spla README chart (docs/stats/rq1_rel.png, log scale, GTX 1070 against LAGraph on a 4-core i7-6700, read by eye): PageRank roughly 13x to 75x, triangle counting roughly 5x to 13x, BFS roughly 0.4x to 4.5x and SSSP roughly 0.2x to 2.6x (slower than LAGraph on some graphs). |
| **Workload** | BFS, SSSP, PageRank and triangle counting on graph adjacency matrices; GraphBLAST on one NVIDIA GPU against SuiteSparse:GraphBLAS (directly in the paper; through LAGraph in the spla chart) on a multi-core CPU. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-6700 3.40 GHz 4-core, 64 GB DDR4, NVIDIA GeForce GTX 1070 8 GB, Ubuntu 20.04 |
| **Adoption** | 238 stars |
| **Last commit** | 2021-06-18 |
| **Links** | [repository](https://github.com/gunrock/graphblast) · [benchmark](https://dl.acm.org/doi/10.1145/3466795) |

## Verdict

The TOMS paper (Yang, Buluc, Owens, doi 10.1145/3466795), known here only from its abstract as quoted in search results, reports a 43.51x geometric-mean and 1268x peak speedup of one NVIDIA GPU over multi-threaded CPU SuiteSparse:GraphBLAS (and 31.83x over GBTL) across its algorithm and graph mix, with the GPU, CPU and versions unverified. The independent spla README chart (GTX 1070 vs LAGraph on a 4-core i7-6700, read by eye) shows big wins for PageRank and triangle counting but mixed BFS and SSSP results, including losses; neither source compares like-for-like hardware.

## Use it when

- Traversal-style or iterative graph analytics (BFS, SSSP, PageRank, triangle counting) on a single NVIDIA GPU where the whole graph, in both CSR and CSC unless symmetric, fits in device memory.
- Large power-law or social graphs where PageRank and triangle counting are compute-heavy: the third-party spla chart puts GraphBLAST roughly 13-75x ahead of LAGraph for PageRank and 5-13x for triangle counting on a GTX 1070 against a 4-core i7.
- Research or prototyping where you want algorithms expressed as semiring linear algebra and are willing to work in C++ templates against an older CUDA toolchain.
- Older Pascal-generation (sm_6x) or earlier NVIDIA GPUs, which match the toolchain the README lists (CUDA 9.1/9.2, g++ 4.9.3/5.4.0).

## Skip it when

- Volta, Turing, Ampere or Hopper GPUs (sm_70+) without testing: open issue #9 reports hangs in BFS on medium matrices after patching the bundled moderngpu for SM &gt;= 70, and the build defaults to compute_35 PTX (common.mk, CMake -arch=sm_35).
- Current CUDA toolkits: issue #28 reports a CUB namespace compile error with CUDA 11.5, and unmasked mxm calls cuSPARSE csrgemm/csrgemm2, which search results say NVIDIA removed in cuSPARSE 12.0; expect porting work.
- Code that relies on non-arithmetic semirings in unmasked mxm: it routes float SpGEMM to cuSPARSE csrgemm2, which only multiplies and adds, so MinimumPlus returns the PlusMultiplies result (open issue #20); the fix (draft PR #26, GALATIC) was never merged.
- Workloads needing the full GraphBLAS feature set: many paths print 'not implemented yet' and return GrB_NOT_IMPLEMENTED (sparse-sparse eWiseAdd per issue #5, unmasked non-float SpGEMM, SpMM/GEMM, masked reduce, several assign/extract variants), and the shipped BFS ('use float for now for both v and A') and README SSSP work in float.
- BFS or SSSP on road-like or small graphs, or graphs larger than GPU memory: the spla chart shows GraphBLAST slower than CPU LAGraph on several BFS/SSSP inputs and missing results on its larger graphs; indices are 32-bit int.

## How it is fast

Direction optimisation (push-pull) borrowed from Ligra and Gunrock: vxm/mxv switches between a push SpMSpV over CSC when the frontier is sparse and a pull masked SpMV over CSR when it is dense, keeping both formats on the GPU. Masked pull SpMV fuses the mask and can exit early per row for the Boolean semiring (spmvDenseMaskedOrKernel), and descriptor flags add structure-only mode (ignore edge values) and operand reuse. Load balancing for the general SpMV comes from moderngpu's merge-based SpmvCsrBinary, and sparse vectors are compacted with prefix scans.

## Compared with alternatives

Pick GraphBLAST over spla when you are on NVIDIA hardware and want direction-optimised BFS/SSSP and the fastest PageRank in the spla comparison; pick spla for AMD or Intel GPUs through OpenCL, cuBool when only Boolean semiring operations are needed and you want a maintained CUDA library, and ALP/GraphBLAS for a CPU GraphBLAS that beats SuiteSparse without a GPU.

## Integration

| | |
|---|---|
| **Form** | header-only templates (copy graphblas/ into the include path) plus two moderngpu sources to compile with your program (ext/moderngpu/src/mgpucontext.cu, mgpuutil.cpp); Makefile and CMake builds for the examples |
| **Dependencies** | CUDA with cuSPARSE, cuBLAS and cuRAND; Boost program_options (the Descriptor parses command-line options); git submodules ctcyang/moderngpu (a fork) and a standalone NVlabs CUB |
| **Minimum toolchain** | Tested on CUDA 9.1/9.2, Boost 1.58, g++ 4.9.3/5.4.0, CMake 3.11.1 optional; compiled as -std=c++11 with -O3 -use_fast_math |
| **Platforms** | NVIDIA GPUs only; build targets compute_35 by default; Linux toolchain paths in common.mk (Boost path hard-coded to the author's machine) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Edit common.mk before building: BOOST_DIR and BOOST_DEPS point to /data/ctcyang/boost_1_58_0, and CUDA_ARCH is 35; the CMake build hard-codes -arch=sm_35.
- Builds use -use_fast_math, which relaxes float accuracy for PageRank-style numeric kernels; BFS and the README SSSP example use float for both vectors and matrix values.
- The benchmark scripts time only GPU kernels with a GpuTimer (not graph loading or host-device transfer) and run PageRank with --max_niter 10, so match iteration counts and what is timed before comparing with a CPU library.
- Directed graphs keep both CSR and CSC copies in device memory for push-pull; only symmetric structure lets it free the CSC index arrays.

## Known shortcomings

- GPU vs CPU comparison (43.51x geomean over SuiteSparse GraphBLAS per the ACM TOMS abstract, doi 10.1145/3466795); paper unreadable here.
- Correctness bug: unmasked float mxm goes to cuSPARSE csrgemm2 and ignores the semiring, so MinPlus returns the PlusTimes result (open #20; fix PR #26 never merged). #9 hangs on sm_70+; #28 CUB build error on CUDA 11.5; csrgemm2 was removed in CUDA 12. Many ops print 'not implemented yet'.

## Caveats and trade-offs

GPU against CPU in both sources, so not like for like; the paper's numbers were seen only as an abstract quote in search results (paper blocked), so its GPU, CPU, SuiteSparse version, compiler and flags are unverified, and the 43.51x geometric mean is an aggregate over its own algorithm and graph mix. In the spla chart (made by a competing project, no flags or harness for GraphBLAST in the repo) GraphBLAST has no bar for comOrkut and i2004 in BFS/SSSP and none for comOrkut, socLvJr, rggn223s0 and rdcent in PageRank, which suggests it failed or was not run on those larger graphs on the 8 GB GPU; it is slower than LAGraph on several BFS and SSSP graphs. Last commit 2021-06-18; CUDA build era of 2019-2021.

NVIDIA CUDA only, Boost dependency, tested on CUDA 9.1/9.2 with g++ 4.9.3/5.4.0 per the README, so it may need porting to build on current toolchains.

## Maintenance

Abandoned since 2021-06-18 (10 open issues, including a correctness bug and Volta+ hangs, without maintainer replies); Apache-2.0 and readable as a reference design, but treat it as research code that needs porting to current CUDA and GPUs before use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C. GraphBLAST's own paper is peer-reviewed in ACM Transactions on Mathematical Software (doi 10.1145/3466795, per several search results; the README cites the arXiv preprint 1908.01407), and its abstract as quoted in search results gives 43.51x geometric-mean and 1268x peak speedup over multi-threaded SuiteSparse GraphBLAS. The paper could not be opened (dl.acm.org, arxiv.org and par.nsf.gov are blocked), so B rests on the venue plus the abstract, per earlier precedents; the spla README chart is third-party secondary evidence without flags.
- **Verifier notes:** The record's ranges match my reading of rq1_rel.png (PageRank top is GraphBLAST's citPat bar, around 75x; the axis has only one labelled tick, so it is approximate). The record called the paper 'TOPC'; search results place it in ACM TOMS. Repo page: Apache-2.0, 238 stars, 28 forks, not archived, 532 commits; latest commit 2021-06-18.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/README.md>
  - <https://github.com/gunrock/graphblast>
  - <https://github.com/gunrock/graphblast/commits>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/README.md>
  - <https://raw.githubusercontent.com/SparseLinearAlgebra/spla/HEAD/docs/stats/rq1_rel.png>
- **Sources the enricher read:**
  - <https://github.com/gunrock/graphblast>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/README.md>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/Makefile>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/common.mk>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/run_bfs.sh>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/run_pr.sh>
  - <https://github.com/gunrock/graphblast/tree/master/graphblas/algorithm>
  - <https://github.com/gunrock/graphblast/tree/master/graphblas/backend/cuda>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/graphblas/graphblas.hpp>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/graphblas/types.hpp>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/graphblas/algorithm/bfs.hpp>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/graphblas/backend/cuda/descriptor.hpp>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/graphblas/backend/cuda/spmv.hpp>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/graphblas/backend/cuda/spmspv.hpp>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/graphblas/backend/cuda/spgemm.hpp>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/graphblas/backend/cuda/operations.hpp>
  - <https://raw.githubusercontent.com/gunrock/graphblast/HEAD/graphblas/backend/cuda/sparse_matrix.hpp>
  - <https://github.com/gunrock/graphblast/issues>
  - <https://github.com/gunrock/graphblast/issues/5>
  - <https://github.com/gunrock/graphblast/issues/9>
  - <https://github.com/gunrock/graphblast/issues/20>
  - <https://github.com/gunrock/graphblast/issues/28>
  - <https://github.com/gunrock/graphblast/pull/26>
  - https://escholarship.org/uc/item/292901ks (EGRESS_BLOCKED)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/gunrock/graphblast`) · [data/wave8/enrich/raw/github_com_gunrock_graphblast.json](../../../data/wave8/enrich/raw/github_com_gunrock_graphblast.json) (enrichment confidence 0.75)

</details>
