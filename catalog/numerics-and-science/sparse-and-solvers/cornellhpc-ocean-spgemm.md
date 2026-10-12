# Ocean SpGEMM (CornellHPC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `CUDA/C++` · `no license` · 🟢 active

> GPU SpGEMM (C = A\*B, FP64 CSR) that sizes output rows with HyperLogLog estimates; reported 1.4x over spECK on A100.

| | |
|---|---|
| **Beats** | spECK (primary) and OpSparse; also TileSpGEMM and HSMU-SpGEMM |
| **Claimed result** | From WebSearch snippets of the arXiv 2604.19004 abstract and body (paper not opened): on A100 over 337 square SuiteSparse matrices Ocean achieves 1.4x, 2.6x, 3.5x and 2.0x over spECK, opSparse, TileSpGEMM and HSMU-SpGEMM; overall 1.4x-2.8x on A100 and H100. A snippet also reports, for H100 rectangular matrices, 60.7 GFLOPS for Ocean against 42.6 for spECK and 17.1 for opSparse (about 1.42x and 3.55x, derived from snippet data). |
| **Workload** | GPU SpGEMM (C = A\*B) on 337 square SuiteSparse matrices on A100, plus H100 and 64 rectangular matrices; replaces the symbolic pass with HyperLogLog estimation. |
| **Metric** | throughput |
| **Hardware** | NVIDIA A100 and H100 (tested only on these) |
| **Compiler and flags** | CUDA Toolkit 12.4 or later. The Makefile builds with nvcc -std=c++14 -O3 -gencode=arch=compute_61,code=sm_80 (Compute_Capability set by hand) -Xptxas=-v -Xcompiler -Wall --expt-extended-lambda -use_fast_math --expt-relaxed-constexpr; NUM_SM and SHARED_MEMORY_KB are set by hand in include/Common.h. The paper's flags were not checked because the paper is blocked. |
| **Adoption** | 7 stars |
| **Last commit** | 2026-04-21 |
| **Links** | [repository](https://github.com/CornellHPC/Ocean-SpGEMM) · [benchmark](https://arxiv.org/abs/2604.19004) |

## Verdict

Per WebSearch snippets of the ICS '26 paper (arXiv 2604.19004, not opened because arXiv, alphaxiv and doi.org are egress-blocked), Ocean averages 1.4x, 2.6x, 3.5x and 2.0x over spECK, OpSparse, TileSpGEMM and HSMU-SpGEMM on 337 square SuiteSparse matrices on an A100, with 1.4x to 2.8x across A100, H100 and rectangular matrices. Whether these are geometric or arithmetic means, the host CPU, and whether cuSPARSE was compared could not be checked.

## Use it when

- Repeated FP64 SpGEMM (A\*A, A\*B, AMG Galerkin products, graph contraction) on A100 or H100 where spECK or OpSparse is the current tool.
- Workloads where the symbolic pass dominates; the paper's abstract says it is about 28% of spECK's runtime.
- Benchmarking or research on estimation-based SpGEMM, since the repo ships the 337-square and 64-rectangular SuiteSparse matrix lists and a download script.

## Skip it when

- Anything you need to ship: the repository has no license, so it can be read but not legally copied or redistributed.
- GPUs other than A100/H100 or older than compute capability 8.0; the README warns that untested hardware will likely hit compile, configuration or runtime errors.
- FP32, complex or integer values, or matrices you cannot convert to its custom CSR file format without writing glue code (data_t is hard-coded to double).
- Pipelines that cannot tolerate a hard failure: if HLL underestimates output size beyond the spare buffer, run() throws std::runtime_error and asks you to raise hll_numeric_malloc_expansion_coe.
- Memory-tight runs: estimation over-allocates the output (default factor 1.3) and the memory pool is set never to release memory.

## How it is fast

Most GPU SpGEMM codes (spECK, OpSparse, nsparse) run an exact symbolic pass to count each output row's nonzeros before the numeric pass; Ocean replaces it, where profitable, with per-row HyperLogLog cardinality estimates (HLL sketches of B's rows built with MurmurHash3, merged per row of A) and over-allocates by a configurable factor. An analysis stage uses input statistics and sampling to pick among an ultra-sparse path, an estimation path, an exact symbolic path and a 'fat' path, and the numeric phase uses hybrid dense, hash and ESC accumulators binned by row size, with rows that overflow their estimate recomputed by a dense fallback kernel. Code is compiled for compute_61 PTX on purpose to avoid Independent Thread Scheduling, which the Makefile says slows some kernels.

## Compared with alternatives

Pick Ocean over spECK or OpSparse when you are on A100/H100 and only need to study or benchmark (no license); for code you will ship, use spECK, OpSparse or TileSpGEMM, or Kokkos Kernels SpGEMM where portability and a maintained API matter more than the reported 1.4x to 3.5x.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA Toolkit 12.4+ (cudart, CUB); vendored nlohmann/json and a MurmurHash3 port; parts adapted from spECK |
| **Minimum toolchain** | CUDA 12.4, C++14 (nvcc -std=c++14), Linux |
| **Platforms** | NVIDIA GPUs with compute capability 8.0+, tested only on A100 and H100; NUM_SM and SHARED_MEMORY_KB must be edited in include/Common.h and Compute_Capability in the Makefile |
| **Thread safety** | not documented; run() configures the device-0 default memory pool, which affects the whole process |
| **Drop-in for the baseline** | no |

## Gotchas

- Hardware constants are compile-time: a wrong NUM_SM (108 for A100, 114 or 132 for H100) or SHARED_MEMORY_KB (must be 128, 96 or 80) silently changes scheduling or breaks launches.
- index_t defaults to uint32_t, so row offsets and the output's nonzero count must stay below about 4.29 billion unless you rebuild with uint64_t.
- The README says correctness checks against spECK output 'may fail' on some matrices from floating-point differences (relative tolerance 1e-6, auto-fail 1e-4); builds also use -use_fast_math.
- Timed iterations include allocation through cudaMallocAsync from a pool whose release threshold is set to UINT64_MAX, so warm runs reuse memory and cold first-call cost is excluded by the default 10 warmup iterations.

## Known shortcomings

- Downgraded B to C: the ICS 2026 paper (arXiv 2604.19004) could not be opened, so the 1.4x over spECK and 2.6x over OpSparse figures are snippet-only; no LICENSE file, so usability reference. Retier to B when the paper is reachable.
- run() throws std::runtime_error when the HyperLogLog estimate undershoots the output size beyond the spare buffer (hll_numeric_malloc_expansion_coe 1.3); NUM_SM and SHARED_MEMORY_KB are compile-time hand edits; index_t is uint32 by default; built with -use_fast_math. Whether the snippet speedups are geometric or arithmetic means, and any cuSPARSE comparison, are unknown.

## Caveats and trade-offs

No LICENSE file (LICENSE, LICENSE.md, LICENSE.txt and COPYING all return 404) and no license on the repo page, so usability is reference. Parts of the code are adapted from spECK, plus MurmurHash3 from PeterScott/murmur3 and nlohmann/json, which adds licensing ambiguity. The paper (ICS 2026) is peer-reviewed, but arXiv, doi.org and dl.acm.org were egress-blocked, so the speedups come from WebSearch snippets only, and the cuSPARSE comparison, per-matrix numbers, host CPU and flags could not be checked. The '7.35x/1.43x/1.52x' figures in the lead are OpSparse's own results (arXiv 2206.07244), not Ocean's. The baselines are research codes (spECK, opSparse, TileSpGEMM, HSMU-SpGEMM); whether cuSPARSE SpGEMM was compared is unconfirmed. The README recommends spECK output as ground truth and warns numerical comparison may fail on some matrices due to floating-point error. Tested only on A100 and H100. No CPU baseline (SuiteSparse, Eigen, PETSc).

Requires compute capability 8.0+ and CUDA 12.4+, manual hardware constants in include/Common.h, matrices must be converted to a custom .csr format with the bundled convert tool; README warns of likely compile or runtime errors on untested hardware. Part of the code is adapted from spECK; uses nlohmann/json and murmur3.

## Maintenance

Recently published (10 commits, last 2026-04-21, 7 stars, no issues) and buildable with CUDA 12.4+, but with no license it is reference-only; read it for the HyperLogLog-estimation idea rather than vendoring it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README confirms a peer-reviewed ICS '26 paper (doi 10.1145/3797905.3807868), but arXiv (CONNECT 403), doi.org and dl.acm.org are egress-blocked, so the speedups come only from WebSearch snippets of the abstract and I opened no numbers page. Following the fbcuda and PFT precedents, I put it at C until someone opens the paper. Opening it could support B.
- **Verifier notes:** I found the benchmark_url (arXiv 2604.19004) through WebSearch results but could not open it (CONNECT 403). If the paper becomes reachable, a retier to B is likely. The metadata matches: no license, 7 stars, not a fork, last commit 2026-04-21 (README citation), active.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/CornellHPC/Ocean-SpGEMM>
  - <https://github.com/CornellHPC/Ocean-SpGEMM/commits>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/readme.md>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/CornellHPC/Ocean-SpGEMM>
  - <https://github.com/CornellHPC/Ocean-SpGEMM/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/readme.md>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/Makefile>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/include/Common.h>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/include/CSR.h>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/src/main.cu>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/kernels/HLL.cuh>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/kernels/SpGEMM.cuh>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/kernels/Wrappers.cuh>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/kernels/Analysis.cuh>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/config/bench.json>
  - <https://raw.githubusercontent.com/CornellHPC/Ocean-SpGEMM/HEAD/config/analysis.json>
  - https://arxiv.org/abs/2604.19004 (EGRESS_BLOCKED; abstract read from WebSearch snippets only)
  - https://www.alphaxiv.org/abs/2604.19004 (EGRESS_BLOCKED)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/cornellhpc/ocean-spgemm`) · [data/wave8/enrich/raw/github_com_cornellhpc_ocean_spgemm.json](../../../data/wave8/enrich/raw/github_com_cornellhpc_ocean_spgemm.json) (enrichment confidence 0.65)

</details>
