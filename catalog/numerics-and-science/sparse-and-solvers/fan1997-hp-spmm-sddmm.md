# HP-SpMM-SDDMM (fast GPU SpMM for GNN graphs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `Apache-2.0 via per-file headers on the HP-SpMM sources (spmm/mm/spmm_kernel.cu, spmm/mm/spmm_common.cpp, include/spmm/mm/\*, test/\*.cpp). The repo has no LICENSE file. The bundled starml framework headers (e.g. include/starml/basic/matrix.h, allocator.h) and include/spmm/utils/timer_cuda.h carry no license. The integrated GE-SpMM baseline code is MIT upstream.` · 🟡 stale

> FP32 GPU SpMM kernel for GNN graphs (IPDPS'23 HP-SpMM); tops cuSPARSE 12.2 and GE-SpMM on 17 graphs on an H800.

| | |
|---|---|
| **Beats** | cuSPARSE 12.2 SpMM (CSR ALG2, CSR ALG3, CSR default, COO) and GE-SpMM |
| **Claimed result** | README bar chart (GFLOPS averaged over K = 32, 64, 128 on an H800; values read off the chart, so approximate): HP-SpMM is the highest bar on all 17 datasets, e.g. about 1730 vs about 1050 for the best cuSPARSE variant on Yelp, about 1870 vs 1130 on arxiv, about 3000 vs 1920 on reddit; about equal on ddi (about 2400 vs 2370) and only slightly above GE-SpMM on protein (about 2950 vs 2850; best cuSPARSE about 2150). No exact numbers are printed. |
| **Workload** | FP32 sparse-dense matrix multiplication (SpMM) in GFLOPS, averaged over K = 32, 64 and 128 dense columns, on 17 GNN datasets (Yelp, Flickr, AIFB, BGS, AM, MUTAG, AmazonCoBuyComputer, arxiv, collab, ddi, ppa, products, protein, reddit, ...) on an NVIDIA H800. |
| **Metric** | throughput |
| **Hardware** | NVIDIA H800 for the README figure (host CPU not stated); code requires Ampere (A100, A800) or Hopper (H100, H800) GPUs |
| **Compiler and flags** | NVCC &gt;= 11.8 (stated as a minimum; the toolkit actually used is not given beyond 'cuSPARSE-12.2') via CMake. CMakeLists.txt builds Release with host -O3. cmake/public/CUDA.cmake adds -gencode arch=compute_80,code=sm_80, -gencode arch=compute_90,code=sm_90, -std=c++11 and --expt-extended-lambda. |
| **Adoption** | 8 stars, 0 forks (an identical copy at https://github.com/HPMLL/HP-SpMM has 5 stars, 1 fork) |
| **Last commit** | 2023-12-31 |
| **Links** | [repository](https://github.com/fan1997/HP-SpMM-SDDMM) · [benchmark](https://github.com/fan1997/HP-SpMM-SDDMM) |

## Verdict

First-party README chart on an NVIDIA H800 (host CPU and exact CUDA version not stated beyond cuSPARSE 12.2, NVCC 11.8+, -O3, sm_80/sm_90): FP32 SpMM GFLOPS averaged over K = 32, 64 and 128 on 17 GNN graphs, with HP-SpMM above every cuSPARSE variant and GE-SpMM on all of them, for example about 1730 vs 1050 GFLOPS on Yelp and 3000 vs 1920 on reddit (values read off the chart). HP-SpMM alone runs on the precomputed clustering reorder, whose cost is not counted.

## Use it when

- Full-graph GNN aggregation (GCN-style A\*X) in FP32 on A100/A800/H100/H800 with feature widths K = 32, 64 or 128
- Power-law graphs with skewed degrees (Reddit, ogbn-products, Yelp) where row-per-warp CSR kernels suffer load imbalance; the README chart shows roughly 1.5-1.7x over the best cuSPARSE variant on Yelp, arxiv and reddit
- The graph is static across many epochs, so a one-off clustering reorder and COO conversion are amortized
- As a reference implementation of edge-balanced, vectorized SpMM to port into your own GNN framework

## Skip it when

- K not a multiple of 32: the kernels have no column bounds check (cid &lt; k) and read B and write C past the end
- FP16/BF16, FP64 or weighted SpMM with non-default semirings: FP32 only, and the benchmark uses all-ones values
- Pre-Ampere GPUs: the build targets sm_80/sm_90 and the large-graph path uses cp.async
- If you need SDDMM, a maintained library or a PyTorch/DGL binding: none is provided, and there are 6 commits with the last in December 2023
- Graphs that change every step (sampled mini-batches): you cannot reproduce the reorder step from this repo, and without it the speedup is not documented

## How it is fast

Edge-parallel, load-balanced COO SpMM: each warp takes a fixed slice of 32 (or 128 for dense, large graphs) nonzeros, so skewed degree distributions do not leave idle warps, and partial row sums are flushed to C with atomicAdd when the row changes. The paper calls this a hybrid node/edge-parallel strategy with Dynamic Task Partition and Hierarchical Vectorized Memory Access: the 128-nonzero path loads indices and values with float4/int4 cp.async into double-buffered shared memory (Ampere+). A graph-clustering row reordering (precomputed .cugraph_reorder files) groups rows with similar neighbourhoods so the rows of B they read stay in cache.

## Compared with alternatives

Pick it over Sputnik when the workload is GNN-style A\*X on power-law graphs on Ampere/Hopper and FP32 is enough; Sputnik is the more general deep-learning SpMM/SDDMM library and includes SDDMM. merge-spmv and CSR5 balance load in the same spirit but only for SpMV (one dense column).

## Integration

| | |
|---|---|
| **Form** | shared lib (CMake builds libspmm from spmm/\*.cu and \*.cpp); realistically a source-drop of spmm_kernel.cu |
| **Dependencies** | CUDA toolkit with cuSPARSE (baselines) and Thrust; bundled starml tensor framework (unlicensed); precomputed .smtx and .cugraph_reorder dataset files from a SharePoint download |
| **Minimum toolchain** | NVCC 11.8+, CMake 3.14+, C++11 |
| **Platforms** | NVIDIA Ampere and Hopper only (A100, A800, H100, H800; sm_80/sm_90 gencode) |
| **Thread safety** | not documented; kernels accumulate into C with atomicAdd, so C must be zeroed before each call and concurrent calls must not share C |
| **Drop-in for the baseline** | no |

## Gotchas

- Output is accumulated with atomicAdd: LBSpMM does not zero C, and the timed loop runs 200 launches into the same buffer, so after benchmarking C holds 200x the product (the disabled CHECK_RES compares with a 'div' mode); FP32 atomics also make results non-deterministic in summation order
- Only HP-SpMM gets the clustering reorder; cuSPARSE and GE-SpMM run on the original order, and the reorder cost and C zeroing are excluded from its time. Neither HP-SpMM nor GE-SpMM gets the 20 warm-up runs the cuSPARSE paths get
- Index arithmetic is 32-bit int (colind\*k, row\*k), so rows\*K and cols\*K must stay below 2^31; nonzero arrays must be padded to a multiple of 32 as the loader does
- Input is a custom .smtx text format (header line 'rows,cols,nnz', then row offsets and column indices), not Matrix Market

## Known shortcomings

- Not like-for-like: only HP-SpMM gets a precomputed cuGraph row reorder (untimed, no generator script); CHECK_RES off by default; kernel sources carry Apache-2.0 headers but bundled starml is unlicensed and there is no LICENSE file (mixed); HPMLL/HP-SpMM is an identical copy.
- Kernels have no column bounds check, so K not a multiple of 32 reads and writes out of bounds. No SDDMM code despite the name. Only HP-SpMM gets the clustering reorder, and that cost and output zeroing are excluded from its timing; HP-SpMM and GE-SpMM get no warm-up while cuSPARSE gets 20 runs. 32-bit index maths (rows\*K and cols\*K &lt; 2^31); atomicAdd output makes results non-deterministic. HPMLL/HP-SpMM is an identical copy.

## Caveats and trade-offs

Results are only a chart image, and the README calls the code an updated version of the IPDPS 2023 method; the paper (DOI 10.1109/IPDPS54959.2023.00057) was not opened. Not like-for-like input: HP-SpMM (LBSpMM in spmm/mm/spmm_kernel.cu) runs on a COO matrix whose rows are permuted by a precomputed '.cugraph_reorder' file, while cuSPARSE and GE-SpMM get the original order. The reorder cost is excluded, and the reorder files exist only as downloads from a personal SharePoint (dataset/download.sh); no generator script is in the repo. The correctness check (CHECK_RES) is commented out in test/test_all.cpp by default. Values are unweighted (all 1.0). No LICENSE file: the kernel sources carry Apache-2.0 headers but the bundled starml framework does not. cuSPARSE is a vendor library, not one of the listed incumbents. CUDA_ARCHITECTURES is set to 80 on the target while CUDA.cmake also adds sm_90 gencode.

FP32 only, Ampere and Hopper GPUs only, CUDA 11.8+. Targets the sparsity patterns of GNN training graphs rather than scientific matrices. Companion code to 'Fast Sparse GPU Kernels for Accelerated Training of Graph Neural Networks' (IPDPS 2023); this repo is described as the updated version.

## Maintenance

Stale research code (last commit December 2023, also mirrored at HPMLL/HP-SpMM); kernel files carry Apache-2.0 headers but there is no LICENSE file and the starml framework is unlicensed, so copy the kernel rather than depend on the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README chart (result_h800-1704017465770.png) against cuSPARSE 12.2 (CSR ALG2/ALG3/default, COO) and GE-SpMM on an H800. The harness is public (test/test_all.cpp run by run.sh: 20 warm-up and 200 timed runs with CUDA events) and the flags are in CMakeLists.txt and cmake/public/CUDA.cmake, but the toolchain actually used is given only as 'NVCC &gt;= 11.8', no host CPU is named, and the reorder files come from an unpublished step. The IPDPS 2023 paper could make it B, but it covers the earlier version and could not be opened (cse.ust.hk blocked by egress). So C.
- **Verifier notes:** Chart values in the record match the image within reading error, and HP-SpMM does top every dataset. The license is better than the record said: Apache-2.0 headers on the core sources, so it is 'mixed' rather than 'reference'. Main shortcoming to record: the row reordering (precomputed, untimed, supplied only to HP-SpMM) is not given to the cuSPARSE baselines. github.com/HPMLL/HP-SpMM is an identical copy (same README, 6 commits); treat it as the same project.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `license`, `usability`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/fan1997/HP-SpMM-SDDMM>
  - <https://github.com/fan1997/HP-SpMM-SDDMM/commits>
  - <https://github.com/fan1997/HP-SpMM-SDDMM/tree/main/test>
  - <https://github.com/fan1997/HP-SpMM-SDDMM/tree/main/spmm>
  - <https://github.com/fan1997/HP-SpMM-SDDMM/tree/main/spmm/mm>
  - <https://github.com/fan1997/HP-SpMM-SDDMM/tree/main/spmm/starml>
  - <https://github.com/fan1997/HP-SpMM-SDDMM/tree/main/include>
  - <https://github.com/fan1997/HP-SpMM-SDDMM/tree/main/include/starml/basic>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/README.md>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/result_h800-1704017465770.png>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/cmake/public/CUDA.cmake>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/run.sh>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/test/test_all.cpp>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/spmm/mm/spmm_kernel.cu>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/spmm/mm/spmm_common.cpp>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/include/spmm/utils/timer_cuda.h>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/include/starml/basic/matrix.h>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/dataset/download.sh>
  - <https://github.com/HPMLL/HP-SpMM>
  - <https://raw.githubusercontent.com/HPMLL/HP-SpMM/HEAD/README.md>
  - <https://github.com/hgyhungry/ge-spmm>
- **Sources the enricher read:**
  - <https://github.com/fan1997/HP-SpMM-SDDMM>
  - <https://github.com/fan1997/HP-SpMM-SDDMM/issues>
  - <https://github.com/fan1997/HP-SpMM-SDDMM/tree/main/spmm/mm>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/README.md>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/cmake/public/CUDA.cmake>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/run.sh>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/test/test_all.cpp>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/spmm/mm/spmm_kernel.cu>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/spmm/mm/spmm_common.cpp>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/include/spmm/mm/spmm_kernel.h>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/include/spmm/utils/timer_cuda.h>
  - <https://raw.githubusercontent.com/fan1997/HP-SpMM-SDDMM/HEAD/dataset/download.sh>
  - WebSearch: IPDPS 2023 paper abstract via search snippets (cse.ust.hk PDF not opened)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/fan1997/hp-spmm-sddmm`) · [data/wave8/enrich/raw/github_com_fan1997_hp_spmm_sddmm.json](../../../data/wave8/enrich/raw/github_com_fan1997_hp_spmm_sddmm.json) (enrichment confidence 0.75)

</details>
