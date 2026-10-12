# RA-SpMM (regime-aware GPU SpMM router for GNN workloads)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Rule-based GPU SpMM dispatcher (five CSR/tensor-core kernels) for GNN graphs, 1.70x warm geomean over FP32 cuSPARSE.

| | |
|---|---|
| **Beats** | cuSPARSE SpMM (FP32, cusparseSpMM) |
| **Claimed result** | 1.702x warm geomean speedup over FP32 cuSPARSE (oracle 1.706x, 173/192 oracle hits); precision-matched speedup 1.222x; cold first-call 2.269x; GNN training step vs cuSPARSE backend 1.37x/1.26x/1.26x warm geomean (GCN/SAGE/GIN), up to 3.24x on Reddit; RTX 4090 transfer 1.515x warm. |
| **Workload** | Sparse-dense matrix multiplication (SpMM) with CSR sparse matrix and feature width N in {64,128,256,512} over 51 graphs (26 real, 25 synthetic) = 192 configurations on an RTX 3090; a seven-rule decision tree dispatches each call to one of five CSR or tensor-core tile kernels; warm protocol is 50 warmup + 200 timed CUDA-event iterations on both sides. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 3090 (primary) and RTX 4090 (cross-architecture); host CPU model not stated |
| **Compiler and flags** | nvcc -O3 with -arch=sm_86 (setup.py, RA_SM_ARCH env var), CUDA 11.8 and matching PyTorch; CUDA 12.1 for the RTX 4090 sweep |
| **Adoption** | 1 star, 7 commits |
| **Last commit** | 2026-07-31 |
| **Links** | [repository](https://github.com/tariqaf/RA-SpMM) · [benchmark](https://github.com/tariqaf/RA-SpMM) |

## Verdict

On an RTX 3090 with CUDA 11.8 (nvcc -O3 --use_fast_math -arch=sm_86), over 51 graphs x N in {64,128,256,512}, routed kernels ran 1.702x faster (warm geomean, 50 warmup + 200 timed CUDA-event iterations, preprocessing outside the timed region) than FP32 cusparseSpMM with CUSPARSE_SPMM_CSR_ALG2; the figure recomputes from the released CSV, but compares FP16/TF32 tensor-core paths against FP32 cuSPARSE, so the precision-matched figure is 1.222x (1.053x on an RTX 4090).

## Use it when

- GNN training or inference in PyTorch on Ampere/Ada GPUs (sm_86 RTX 3090, sm_89 RTX 4090 tested) where the same graph is multiplied many times, so the one-time tile build amortizes (median break-even 388 calls per RESULTS.md).
- Feature widths N of 64 to 512 on graphs resembling its 51-graph suite (citation, social, web, Reddit/ogbn-proteins-style dense rows, synthetic power-law and community graphs).
- Cold first-call SpMM where you cannot amortize setup: the cold path dispatches a zero-conversion CSR kernel (2.269x over cuSPARSE descriptor+workspace+first call on the 3090).
- When FP16/TF32 accumulation error (max deviation 0.125 observed under its tolerance gate) is acceptable for your model.

## Skip it when

- You need FP32 or bit-identical results to cuSPARSE: tile paths use FP16 or TF32 inputs and the build uses --use_fast_math; restricted to precision-matched comparison the gain drops to 1.222x on the 3090 and 1.053x on the 4090.
- Graphs unlike the tuning suite: rule thresholds are named after specific benchmark graphs (com-youtube, Reddit, amazon-photo, web-Google), and the frozen router on 9 unseen graphs reached only 1.197x with 11/34 oracle hits; wiki-Talk and cit-Patents at N=512 exhausted memory on every deployed kernel.
- If FlashSparse or MP-SpMM is an option: per RESULTS.md FlashSparse is 1.28x faster than the router over 190 configs on the 4090, and MP-SpMM beats it on aggregate at N=128 (router 0.84x; router wins only on real graphs, 1.15x).
- Non-NVIDIA hardware, CPU, int64 indices, double precision, or code outside PyTorch: none are supported.
- Production use: a research artifact for a paper under review, 1 star, 7 commits on one day; the model-based runtime router (ra_runtime_router.py) loads results/router/runtime_cost_model.json, which is not in the repository.

## How it is fast

A single O(M) pass over the row-pointer array computes row count, mean degree and degree coefficient of variation; with feature width N, a seven-rule decision tree picks one of five kernels: subwarp-per-row CSR (CSR_DIRECT), degree-binned CSR (ZERO_OVERHEAD_CSR), and three tensor-core kernels on an 8x1 vector-block layout using mma.m16n8k8 (TC_DIRECT, COMMUNITY_TC with a leading-neighbour locality sort, SEGMENT_HYBRID with balanced window splits). Tile kernels run FP16 or TF32 inputs chosen by a precision rule, and a cuSPARSE guardrail covers the case where no specialist wins; most of the headline gain comes from tensor-core reduced precision (precision-matched speedup is 1.222x).

## Compared with alternatives

Pick it over HP-SpMM-SDDMM or Sputnik when your graphs vary in structure and you want one call that picks a CSR or tensor-core kernel per graph and accept FP16/TF32 precision; HP-SpMM-SDDMM is a single FP32 kernel tuned on an H800 and Sputnik targets deep-learning sparsity patterns rather than graph adjacency.

## Integration

| | |
|---|---|
| **Form** | module (PyTorch CUDA extension built with python setup.py install; C++/CUDA sources compiled by nvcc) |
| **Dependencies** | CUDA 11.8+ toolkit, cuSPARSE, matching PyTorch (torch.utils.cpp_extension), OpenMP for host-side plan construction; numpy/scipy/scikit-learn only for the evaluation scripts |
| **Minimum toolchain** | C++17 host code, nvcc from CUDA 11.8+; target arch set by RA_SM_ARCH (default 86) |
| **Platforms** | NVIDIA GPUs with tensor cores; tested only on sm_86 (RTX 3090, CUDA 11.8) and sm_89 (RTX 4090, CUDA 12.1); Linux implied |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial: same CSR SpMM operation as cusparseSpMM, but a different PyTorch tensor API with a plan/run split, int32/float32 only, and reduced-precision tile paths |

## Gotchas

- The one-shot run_router_plan helper rebuilds the plan and host-copies the CSR on every call; the binding's own docstring says to cache make_&lt;kernel&gt;_plan/run_&lt;kernel&gt;_plan pairs for real use.
- Tile kernels need a format build (1 ms to 36 ms geomean per kernel, worst 1.5 s) and are withheld when the estimated build (about 20 ms per 1e6 nnz) exceeds 20 s or N &lt; 16; 9 configurations never amortize the tile build at all.
- Plan building copies rowptr/colind/vals to the host, so the cold path includes a device-to-host transfer.
- CUDA errors are thrown as std::runtime_error (surfacing as Python exceptions); setup.py compiles every ablation kernel too, so build time is long.

## Known shortcomings

- Numbers recomputed exactly from the released CSV (1.702x, 173 hits, 0.868), but the paper is still under review.

## Caveats and trade-offs

Paper is under review at Future Generation Computer Systems (README), so not peer reviewed yet: tier C although code, flags, per-table CSVs (CC-BY-4.0) and a reproduce script are public; host CPU model is missing. The headline 1.702x compares FP16/TF32 tensor-core kernels against FP32 cuSPARSE; precision-matched speedup is 1.222x (RESULTS.md: 1.053x on the RTX 4090). RESULTS.md also reports frozen-router validation on 9 unseen graphs at only 1.197x, FlashSparse being faster than the RA-SpMM router (1.28x geomean over 190 configs; FlashSparse faster on 134, router on 56), and a worst-case router/oracle ratio of 0.868x. Self-selected benchmark suite of GNN-style graphs; baseline cuSPARSE is not one of SuiteSparse/Eigen sparse/PETSc.

CUDA GPU only with PyTorch bindings; tile kernels need a one-time format build (1 ms to 36 ms geomean, worst 1.5 s per RESULTS.md) and tensor-core FP16/TF32 paths, so results are not bit-identical to FP32 cuSPARSE; a cuSPARSE guardrail covers inputs no specialist improves.

## Maintenance

Code dump from 2026-07-31 accompanying a paper under review at FGCS; MIT code with CC-BY-4.0 data and a full reproduce script, but no issues, releases or users yet, so treat it as a research artifact to study or vendor rather than a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party artifact for a paper still under review at FGCS: README and RESULTS.md give the cuSPARSE comparison with public drivers (ra_real_graph_eval.py, ra_router_eval.py), CSVs and nvcc -O3 -arch=sm_86 flags (setup.py), and the 1.702x / 1.706x / 173 hits / 0.868 worst case recompute exactly from fgcs_results/revision/tf32/router_quality_v8.csv. Host CPU model is not stated and the paper is not yet peer reviewed, so C.
- **Verifier notes:** Record matches README and RESULTS.md (precision-matched 1.222x on 3090 and 1.053x on 4090, frozen-router 1.197x on 9 unseen graphs, FlashSparse 1.28x faster over 190 configs). cuSPARSE runs CUSPARSE_SPMM_CSR_ALG2 as a fixed choice. Metadata: MIT code plus CC-BY-4.0 data, 1 star, 0 forks, 7 commits all dated 2026-07-31.
- **Shortcomings recorded by:** verifier
- **Pages the verifier opened:**
  - <https://github.com/tariqaf/RA-SpMM>
  - <https://github.com/tariqaf/RA-SpMM/commits>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/README.md>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/setup.py>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/fgcs_results/revision/tf32/router_quality_v8.csv>
- **Sources the enricher read:**
  - <https://github.com/tariqaf/RA-SpMM>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/README.md>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/setup.py>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/router/router_dispatch.cpp>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/bindings/ra_bindings.cpp>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/ra_common.h>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/ra_runtime_router.py>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/requirements-revision.txt>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/DATASETS.md>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/fgcs_results/revision/tf32/baseline_audit/mp_regime.csv>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/fgcs_results/revision/tf32/baseline_audit/hc_regime.csv>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/fgcs_results/revision/tf32/baseline_audit/baseline_regime_matrix.csv>
  - <https://raw.githubusercontent.com/tariqaf/RA-SpMM/HEAD/results/router/runtime_cost_model.json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tariqaf/ra-spmm`) · [data/wave8/enrich/raw/github_com_tariqaf_ra_spmm.json](../../../data/wave8/enrich/raw/github_com_tariqaf_ra_spmm.json) (enrichment confidence 0.8)

</details>
