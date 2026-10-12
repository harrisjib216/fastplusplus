# DASP (dense-tensor-core SpMV)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (CUDA)` · `AGPL-3.0` · 🟡 stale

> CUDA SpMV that repacks CSR rows into 8x4 tiles for FP64/FP16 tensor-core MMA; beats cuSPARSE CSR SpMV on A100.

| | |
|---|---|
| **Beats** | cuSPARSE CSR SpMV (CUSPARSE_SPMV_ALG_DEFAULT); also CSR5, TileSpMV, LSRB-CSR and cuSPARSE BSR in the paper |
| **Claimed result** | Paper (SC'23) FP64 on A100: DASP outperforms CSR5, TileSpMV, LSRB-CSR, cuSPARSE BSR and cuSPARSE CSR by a factor of on average 1.46x, 2.09x, 3.29x, 2.08x and 1.52x (up to 12.64x, 17.48x, 90.59x, 283.92x and 6.94x), respectively. FP16 versus cuSPARSE: on average 1.70x and 1.75x (up to 26.47x and 65.94x) on A100 and H800. (Numbers taken from the WebSearch result text for the paper; see caveats.) |
| **Workload** | General sparse matrix-vector multiplication (y = Ax) on SuiteSparse matrices in FP64 and FP16 on NVIDIA A100 and H800 GPUs, using tensor-core MMA units; the repo's harness times cuSPARSE and DASP for 1000 iterations after 100 warm-ups for a given .mtx file. |
| **Metric** | throughput |
| **Hardware** | NVIDIA A100 and H800 GPUs (per the paper text returned by search); the repo recommends a GPU with compute capability 8.0. Host CPU model not verified. |
| **Compiler and flags** | From the repo Makefile: nvcc from CUDA 12.0 with host gcc 12.2, -O3 -m64 -gencode arch=compute_80,code=sm_80, -Xcompiler -fopenmp-simd, linked with -lcusparse -lcublas |
| **Adoption** | 29 stars |
| **Last commit** | 2024-06-18 |
| **Links** | [repository](https://github.com/SuperScientificSoftwareLaboratory/DASP) · [benchmark](https://dl.acm.org/doi/pdf/10.1145/3581784.3607051) |

## Verdict

A search snippet of the SC '23 abstract (paper not opened; dl.acm.org is blocked) reports, for FP64 on A100, average speedups of 1.52x over cuSPARSE CSR (max 6.94x), 1.46x over CSR5, 2.09x over TileSpMV, 3.29x over LSRB-CSR and 2.08x over cuSPARSE BSR; for FP16 it reports 1.70x (A100) and 1.75x (H800) over cuSPARSE. The repo harness (nvcc 12.0, gcc 12.2, -O3, sm_80) times cuSPARSE ALG_DEFAULT and DASP for 1000 iterations each after 100 warm-ups, on all-ones values, excluding DASP preprocessing and without checking results. Independently, the CB-SpMV ICS '25 paper (FP64, 2,843 SuiteSparse matrices, cuSPARSE 12.4) ran DASP as a baseline and beat it by 1.21x on average on A100 and 2.76x on RTX 4090.

## Use it when

- Iterative solvers on A100/H100-class GPUs with strong FP64 tensor cores, where one matrix is multiplied thousands of times and the CPU-side reordering is amortised.
- Matrices whose medium-length rows sort into dense 8x4 tiles (many rows of similar length); these are the cases the MMA path is built for.
- Matrices that are mostly L2-resident: an independent study (search snippet) found DASP's advantage over cuSPARSE holds for cache-resident data.
- FP16 SpMV where half-precision accumulation is acceptable.

## Skip it when

- One-off or few SpMVs: the row classification, sorting and zero-padding run single-threaded on the host and are excluded from the timed loop.
- Matrices much larger than L2: the 'Can Tensor Cores Benefit Memory-Bound Kernels? (No!)' study (snippet only) reports cuSPARSE faster than DASP on average there, and GitHub issue #4 reports DASP slower than cuSPARSE on many matrices on an A100, including bibd_20_10.
- GPUs with weak FP64 tensor cores such as the RTX 4090: CB-SpMV (ICS '25) measured a CUDA-core block format 2.76x faster than DASP on average there, versus 1.21x on A100.
- Code that needs y in original row order with no extra pass, or a maintained, validated kernel: open issues #1 (wrong results when run for only one iteration) and #3 (wrong result on mip1) have no maintainer reply.
- Proprietary or hosted software that cannot accept AGPL-3.0 copyleft.

## How it is fast

On the host, rows are bucketed by length: long rows (256 or more nonzeros), medium 'row-block' rows (5 to 255), and short rows (1 to 4). Medium rows are sorted and grouped into 8-row blocks, then cut into 4-column chunks. A chunk that is at least 75% full goes to a dense part computed with FP64 mma.sync m8n8k4 (x gathered into the B fragment); the remainder goes to a CSR part handled on CUDA cores. Long rows are split into 64-nonzero pieces, one warp each (two MMAs), followed by a separate warp-reduction kernel. Short rows are packed in pairs (1+3, 2+2) or alone (4) so they fill MMA tiles. A single fused kernel covers all parts. It uses streaming cache hints (ld.global.cs), sets the shared-memory carveout to 0 to maximise L1, and processes 1, 2 or 4 row-blocks per warp depending on the row-block count.

## Compared with alternatives

Use DASP over merge-spmv or CSR5 only on A100/H100 when matrices tile densely, fit in L2 and are reused many times. Merge-spmv and CSR5 are more predictable CUDA-core kernels with no reordering. ISpMV is the more recent catalogued option that beats cuSPARSE in FP64 on H100 against CUDA 13 cuSPARSE, and TileSpMV is the same lab's older format that DASP reports beating by 2.09x.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit (cuSPARSE and cuBLAS are linked for the baseline); host compiler with -fopenmp-simd |
| **Minimum toolchain** | Makefile pins nvcc from CUDA 12.0 with host gcc 12.2 (absolute /usr/local paths); FP64 mma.sync m8n8k4 needs compute capability 8.0+ |
| **Platforms** | Linux, NVIDIA GPUs; the Makefile builds only sm_80 (A100). The paper also reports H800, and CB-SpMV ran it on an RTX 4090. |
| **Thread safety** | not documented; spmv_all is a monolithic host routine that allocates, converts, times and frees on every call |
| **Drop-in for the baseline** | no |

## Gotchas

- The output vector is permuted: y comes out ordered as long rows, then row-block rows, then short-row groups, and order_rid maps it back. The verify_new() check against cuSPARSE exists, but its call is commented out in both main_f64.cu and main_f16.cu, so the harness never validates results. This corrects the verifier's note that it checks DASP against cuSPARSE. Because initVec sets every matrix value and x entry to 1.0, any check you re-enable runs on all-ones data.
- The FP16 comparison is not like for like. The cuSPARSE baseline stores FP16 but computes in FP32 (CUDA_R_32F compute type). DASP's FP16 kernels use mma m8n8k4 with .f16 accumulators, so DASP accumulates in half precision; with the all-ones inputs, any row with more than 2048 nonzeros already exceeds FP16's exact-integer range.
- Issue #1 (June 2024): with 0 warm-ups and 1 timed iteration the results are wrong but become correct with more iterations; y is cudaMemset only once before the loops. Issue #3 (Sept 2025): wrong result on mip1. Neither has a reply.
- Tuning is hard-coded: long-row cut 256, tile fill threshold 0.75, rows per warp switched at 59,990 and 400,000 row-blocks. The harness writes relative data/\*.csv files, and make clean deletes data/\*.csv.

## Known shortcomings

- Tier B rests on the SC '23 paper (DOI 10.1145/3581784.3607051), blocked here; the numbers are from a search snippet and unverified by the verifier. The GPU and host model appear only in the paper. Last commit 2024-06-18, stale.
- Downgraded B to C (retier-10): the harness's verify_new call is commented out in both mains so results are never checked; every matrix value and x are 1.0; y comes back in permuted row order; the FP16 rows accumulate in f16 against an FP32 cuSPARSE baseline. Open issues #1 and #3 report wrong results and #4 asks whether the speedups are fake (an A100 user finds DASP slower than cuSPARSE on many matrices including bibd_20_10). arXiv 2502.16851 (snippet) finds cuSPARSE beats DASP on average for matrices larger than L2.

## Caveats and trade-offs

The paper could not be opened here (dl.acm.org and other publishers are egress-blocked); the speedups come from a WebSearch snippet of the SC '23 abstract (ACM DL record of DOI 10.1145/3581784.3607051, the DOI the repo README cites), including the A100-only list of FP64 averages. The repo holds no result tables. Its harness (src/main_f64.cu) times cuSPARSE CSR SpMV (CUSPARSE_SPMV_ALG_DEFAULT) and DASP over 1000 iterations after 100 warm-ups, times cuSPARSE setup separately, and checks the DASP result against cuSPARSE; the DASP row reordering/format conversion is not in the timed loop, so gains pay off only when one matrix is multiplied many times. The repo has no scripts for the CSR5, TileSpMV, LSRB-CSR or BSR baselines, so only the cuSPARSE comparison is reproducible from it. cuSPARSE version used in the paper and host CPU not verified. Large 'up to' ratios (283.92x vs cuSPARSE BSR) are outliers; averages are the meaningful figures. [retier] Harness has no result check (verify_new commented out in both mains); all matrix values and x are 1.0; y is returned in permuted row order; FP16 rows accumulate in f16 against an FP32 cuSPARSE baseline. Open issues #1 (wrong result with 1 iteration), #3 (wrong result on mip1), #4 ('Speedup are mostly fake data?', A100 user slower than cuSPARSE on many matrices including bibd_20_10). Independent: CB-SpMV (ICS '25, FP64, 2,843 matrices) is 1.21x faster than DASP on A100 and 2.76x on RTX 4090; arXiv 2502.16851 (snippet) finds cuSPARSE beats DASP on average for matrices larger than L2. SC '23 paper numbers remain snippet-only.

Needs NVIDIA GPUs with MMA tensor-core support (compute capability 8.0 or newer; FP64 and FP16 variants built from separate mains: make double, make half). Research code driven by Matrix Market files, not a library API. Rows are grouped into long, medium and short categories and repacked into MMA-sized blocks, which adds preprocessing and padding (fill-zero) data. AGPL-3.0 network copyleft applies to anything built on the code.

## Maintenance

Stale research code (19 commits, last 2024-06-18, 29 stars) with four open, unanswered issues, including two wrong-result reports and a challenge to the speedups (#4). It is AGPL-3.0, so copying it into non-AGPL software is not an option.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now C.
- **Tier reason:** Peer-reviewed SC '23 paper: the benchmark_url is the ACM DL PDF of DOI 10.1145/3581784.3607051, which the repo README cites as the SC '23 paper (Article 73), so the snippet numbers come from that venue's abstract; I could not open it (dl.acm.org egress-blocked). The repo's harness (src/main_f64.cu, Makefile with nvcc 12.0, gcc 12.2, -O3 sm_80) reproduces the cuSPARSE comparison, but the GPU/host model is only in the unopened paper, so not A.
- **Retiered** B to C: Downgraded B to C on the enricher's reading of the public harness and issues: the verify_new call is commented out in both mains so nothing checks results, every matrix value and x are set to 1.0, the FP16 rows accumulate in f16 while the cuSPARSE baseline computes FP32 (not like for like), and open issues #1 and #3 report wrong results with #4 asking whether the speedups are fake (an A100 user finds DASP slower than cuSPARSE on many matrices). The SC '23 paper remains unopened, and the independent CB-SpMV paper (ICS '25) measures 1.21x over DASP on A100 and 2.76x on RTX 4090 in FP64.
- **Verifier notes:** Could not open the paper (EGRESS_BLOCKED on dl.acm.org); B kept because the snippet's source is the SC '23 proceedings record whose DOI matches the repo README. Metadata confirmed: AGPL-3.0 LICENSE, 29 stars, 19 commits, last commit 2024-06-18 (stale), not fork/archived; Makefile flags match the record.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; independent: CB-SpMV (ICS '25, doi 10.1145/3721145.3725746, PDF via raw.githubusercontent.com hpcrl/ICS2025-webpage) FP64 over 2,843 matrices is 1.21x faster than DASP on A100 and 2.76x on RTX 4090
- **Pages the verifier opened:**
  - <https://github.com/SuperScientificSoftwareLaboratory/DASP>
  - <https://github.com/SuperScientificSoftwareLaboratory/DASP/commits/main>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/README.md>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/Makefile>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/src/main_f64.cu>
- **Sources the enricher read:**
  - <https://github.com/SuperScientificSoftwareLaboratory/DASP>
  - <https://github.com/SuperScientificSoftwareLaboratory/DASP/tree/main/src>
  - <https://github.com/SuperScientificSoftwareLaboratory/DASP/issues?q=is%3Aissue>
  - <https://github.com/SuperScientificSoftwareLaboratory/DASP/issues/1>
  - <https://github.com/SuperScientificSoftwareLaboratory/DASP/issues/2>
  - <https://github.com/SuperScientificSoftwareLaboratory/DASP/issues/3>
  - <https://github.com/SuperScientificSoftwareLaboratory/DASP/issues/4>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/README.md>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/Makefile>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/src/main_f64.cu>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/src/dasp_f64.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/src/main_f16.cu>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/src/dasp_f16.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/src/common.h>
  - <https://raw.githubusercontent.com/SuperScientificSoftwareLaboratory/DASP/HEAD/src/utils.h>
  - <https://raw.githubusercontent.com/hpcrl/ICS2025-webpage/main/program/Proceedings_ICS25/ics25-7.pdf>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/superscientificsoftwarelaboratory/dasp`) · [data/wave8/enrich/raw/github_com_superscientificsoftwarelaboratory_dasp.json](../../../data/wave8/enrich/raw/github_com_superscientificsoftwarelaboratory_dasp.json) (enrichment confidence 0.7)

</details>
