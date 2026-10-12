# bare-metal (hand-optimized SASS/CUDA ML kernels for RTX 3070 Ti Laptop)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (CUDA/SASS, with R tooling)` · `MIT` · 🟢 active

> Hand-tuned sm_86 CUDA/SASS ML kernels; FP16 HGEMM roughly ties cuBLAS on one laptop GPU, other kernels trail vendor libraries.

| | |
|---|---|
| **Beats** | cuBLAS (local reference harness; cuDNN and cuSPARSELt rows also measured and lost) |
| **Claimed result** | docs/comparison_to_sota.md: HGEMM 16-warp 2048^3 31,875 GFLOPS vs cuBLAS 28,631 GFLOPS (111.3%); 4096^3 31,765 vs 29,708 GFLOPS (106.9%). Losing rows on the same page: IGEMM pipelined cp.async 4096^3 20.23 vs 29.44 TOPS cuBLAS (68.7%); sparse IGEMM tiled 31.59 vs 124.28 TOPS (25.4%) at 2048^3 and 30.89 vs 170.11 TOPS (18.2%) at 4096^3 vs cuSPARSELt; conv2d implicit GEMM 7,150 vs 16,910 GFLOPS cuDNN (42.3%). The project's current data/baselines.json replaces the HGEMM 'Ours' readings with clock-locked (1605 MHz) medians of 29,174 GFLOPS at 2048^3 and 30,401 at 4096^3, about 1.02x the cuBLAS reference (derived from page data). Its notes record native-boost re-measurements of 28,090 and 27,307 GFLOPS, about 0.98x and 0.92x of cuBLAS (derived from page data). |
| **Workload** | FP16 tensor-core HGEMM (16-warp kernel) on square 2048^3 and 4096^3 problems, against cuBLAS measured on the same RTX 3070 Ti Laptop GPU under a no-throttle fair-run policy (median of 11 runs after 5 warmups). |
| **Metric** | throughput |
| **Hardware** | NVIDIA GeForce RTX 3070 Ti Laptop GPU (GA104, sm_86, 46 SMs) under a 150 W VBIOS cap, WSL2 on a Windows host; current project HGEMM baselines were measured under a host-side 1605 MHz SM clock lock (nvidia-smi -lgc), while the cuBLAS reference (recorded 2026-05-18) carries no clock-lock note; host CPU not stated |
| **Compiler and flags** | nvcc -arch=sm_86 -O2 (kernels via --cubin, bench harnesses use the CUDA Driver API; reference benches add -std=c++17 and link cublas, cublasLt, cudnn, cusparseLt); CUDA 13.2 (nvcc V13.2.78) per AGENTS.md |
| **Adoption** | 2 stars |
| **Last commit** | 2026-08-17 |
| **Links** | [repository](https://github.com/pjt222/bare-metal) · [benchmark](https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/docs/comparison_to_sota.md) |

## Verdict

On an RTX 3070 Ti Laptop GPU (150 W cap, WSL2, CUDA 13.2, nvcc -O2 sm_86), the 16-warp FP16 HGEMM at 2048^3 and 4096^3 was compared with a local cublasGemmEx harness (FP16 in, FP32 out, CUBLAS_COMPUTE_32F_FAST_16F, median of 11 after 5 warmups). The current clock-locked project baselines (29,174 and 30,401 GFLOPS) sit about 2% above the cuBLAS readings (28,631 and 29,708), a margin smaller than the project's own 4.9% session-to-session spread; the 107-111% figures on the comparison page are older native-boost readings.

## Use it when

- Learning how an Ampere tensor-core GEMM is built from WMMA, cp.async double buffering and occupancy tuning, with a documented phase-by-phase progression (naive SGEMM 1.0x to HGEMM 16-warp 69.2x to sparse 2:4 90.5x in docs/inventory.md).
- Studying SASS-level editing on sm_86: the cuasmR workflow (cubin to nvdisasm to byte patch) and the tutorial chapters are the distinctive part of the repo.
- Square FP16-in/FP32-out GEMMs at 2048^3 to 4096^3 on a GA104 (RTX 3070 Ti class) card where you want a small, readable kernel that lands within a few percent of cuBLAS.
- Reusing its benchmark discipline: the clock-lock, throttle-rejection and baseline-provenance rules in data/baselines.json and AGENTS.md are a useful template for noisy laptop GPUs.

## Skip it when

- Production GEMM on any GPU other than sm_86: kernels, constants and tuning target GA104 only, and the repo has no CI that runs on a GPU.
- When you need a measurable win over cuBLAS: under the project's own clock-locked baselines HGEMM is about 1.02x cuBLAS, and at native boost it measured 28,090 and 27,307 GFLOPS, below the recorded cuBLAS reference (28,631 and 29,708).
- INT8, sparse INT8 and convolution: the project's own table shows IGEMM at 68.7% of cuBLAS, sparse IGEMM at 25.4% and 18.2% of cuSPARSELt, and conv2d at 42.3% of cuDNN.
- General shapes or layouts: the HGEMM kernel has no transpose, alpha/beta or batched variants and skips any 16x16 output tile that crosses the M/N boundary.
- Teams without R and the Windows/WSL2 setup: make reproduce needs CUDA 13.2, R 4.6.0 with renv and the local cuasmR package.

## How it is fast

hgemm_16warp uses a 128x128 block tile with 16 warps in a 4x4 grid, each warp owning a 2x2 set of 16x16 WMMA tiles, so accumulators drop to 32 registers and __launch_bounds__(512, 2) fits two blocks (32 warps) per SM. A and B tiles are double-buffered in shared memory with cp.async (LDGSTS, 16-byte copies), padded by 8 halves per row to avoid bank conflicts, and kept under the 50 KB per-block shared-memory cliff that the project measured as a 2x cliff on GA104. The docs frame the work as 'four laws of GA104': feed the Tensor Cores, read each DRAM byte once, fill the warp schedulers, stay under 50 KB of shared memory.

## Compared with alternatives

Pick it over fast.cu when your hardware is a consumer Ampere card (sm_86) rather than an H100, or when the goal is learning SASS-level tuning; fast.cu shows a larger and better-documented margin over cuBLAS (about 1.07x at N=4096 on H100). FastGEMV covers matrix-vector (memory-bound) work, not GEMM, so the two do not overlap.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA toolkit (CUDA 13.2 documented) and the CUDA Driver API for benches; R 4.6.0 with renv packages and the local cuasmR package for the build/bench/SASS-patch tooling; cuBLAS, cuBLASLt, cuDNN and cuSPARSELt only for the reference benches |
| **Minimum toolchain** | nvcc -arch=sm_86 -O2 (Makefile); documented toolchain CUDA 13.2 (nvcc V13.2.78), R 4.6.0; older CUDA versions not documented |
| **Platforms** | NVIDIA sm_86 (GA104, RTX 3070 Ti Laptop) only; developed under WSL2 on a Windows host |
| **Thread safety** | not documented (plain kernels with no global state; launch and stream handling is up to the caller) |
| **Drop-in for the baseline** | false - kernels are raw extern "C" cubin entry points with fixed row-major FP16 x FP16 -&gt; FP32 semantics, not a cublasGemmEx-compatible API |

## Gotchas

- hgemm_16warp silently skips writing any 16x16 output tile that would cross the M or N edge, and its 16-byte cp.async loads assume rows aligned to 8 halves; use M and N that are multiples of 16 and K, N multiples of 8 (read from the kernel source, not documented as a contract).
- Benchmark numbers depend on clock regime: issue #158 (open) records hgemm_16warp running about 10% slower at native boost than under a 1605 MHz lock, and #159 (open) records two locked sessions disagreeing by 4.9% on the 4096^3 figure.
- The 31,875/31,765 GFLOPS rows in docs/comparison_to_sota.md and the 31,910 headline in docs/inventory.md are native-boost readings the project itself footnotes as disputed (#167, closed by PR #206); the cuBLAS reference was recorded on 2026-05-18 without a clock lock, so the comparison mixes dates and regimes.
- Bench executables load cubins by relative filename and must be run from their own directory (AGENTS.md).

## Known shortcomings

- Claim not reproducible: the HGEMM win over cuBLAS is disputed by the repo itself (inventory.md footnote, issue #167); current locked baselines (29,174/30,401 GFLOPS) give about 1.02x cuBLAS and at native boost 0.98x/0.92x. Single laptop GPU (RTX 3070 Ti Laptop).
- Issues #158 and #159 (bug/performance) still open. hgemm_16warp silently skips writing edge tiles when M or N is not a multiple of 16.

## Caveats and trade-offs

The win over cuBLAS is not settled. The two HGEMM rows that beat cuBLAS use native-boost readings that the repo itself disputes: the docs/inventory.md footnote says 'Do not quote it as a settled result', and issue #167 is titled 'hgemm_16warp has two canonical numbers'. Issue #158 records the kernel running slower at native boost than under a clock lock, and #159 records a 4.9% swing between two locked sessions. With the current locked baselines the margin is about 2%, inside that spread. At native boost the kernel measures below the cuBLAS reference. Project and cuBLAS numbers were taken on different dates and under different clock regimes. Every other row on the page loses: dense INT8 68.7% of cuBLAS, sparse INT8 25.4% and 18.2% of cuSPARSELt, conv2d 42.3% of cuDNN. This is a single laptop GPU with a power cap, the README says several results are n=1, and host CPU is not stated. Flash Attention and GroupNorm have no local reference ('not measured locally'). The like-for-like part holds: both sides take FP16 inputs and accumulate and write FP32.

sm_86 (Ampere GA104) only; kernels are compiled to cubin and some are hand-edited at SASS level through the project's R package cuasmR, so they are not portable C++ source; reproduction needs CUDA, Nsight and R (make reproduce).

## Maintenance

Active (last commit 2026-08-17, 2 stars, MIT), with unusually candid self-auditing in its issue tracker; usable as copyable reference code for sm_86, not as a maintained GEMM library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The mechanics meet A: the harness is public (kernels/reference/cublas_hgemm/bench.cu runs cublasGemmEx, FP16 in, FP32 out, CUBLAS_COMPUTE_32F_FAST_16F; kernels/gemm/hgemm/bench for the project kernel). Makefile flags are -arch=sm_86 -O2, the toolchain is CUDA 13.2 and the GPU is named. But the only winning rows pair stale native-boost project readings (31,875 / 31,765 GFLOPS) with a cuBLAS reading taken on another date. The repo's own docs/inventory.md footnote and issue #167 say that HGEMM figure is disputed and not reproducible, and the current data/baselines.json puts the kernel at about 1.02x cuBLAS under a 1605 MHz clock lock and below cuBLAS at native boost. So the faster-than-cuBLAS claim is first-party and unsettled: C.
- **Verifier notes:** Numbers in claimed_speedup match comparison_to_sota.md exactly, but the repo's own data/baselines.json, the docs/inventory.md footnote and issue #167 (closed by PR #206, opened on github.com) contradict the headline. Recordable shortcoming: claim not reproducible per the project's own tracker; margin at most about 2% under a clock lock and negative at native boost. Metadata on github.com: MIT, 2 stars, 2 forks, not a fork, 320 commits, last commit 2026-08-17 (active), 29 open issues.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/docs/comparison_to_sota.md>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/README.md>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/Makefile>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/data/reference_baselines.json>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/data/baselines.json>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/kernels/reference/cublas_hgemm/bench.cu>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/kernels/gemm/hgemm/hgemm_16warp.cu>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/docs/inventory.md>
  - <https://github.com/pjt222/bare-metal>
  - <https://github.com/pjt222/bare-metal/commits>
  - <https://github.com/pjt222/bare-metal/issues/167>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/README.md>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/docs/comparison_to_sota.md>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/docs/inventory.md>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/Makefile>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/data/baselines.json>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/data/reference_baselines.json>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/kernels/gemm/hgemm/hgemm_16warp.cu>
  - <https://raw.githubusercontent.com/pjt222/bare-metal/HEAD/kernels/reference/cublas_hgemm/bench.cu>
  - <https://github.com/pjt222/bare-metal/issues?q=is%3Aissue+hgemm>
  - <https://github.com/pjt222/bare-metal/issues/167>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/pjt222/bare-metal`) · [data/wave8/enrich/raw/github_com_pjt222_bare_metal.json](../../../data/wave8/enrich/raw/github_com_pjt222_bare_metal.json) (enrichment confidence 0.8)

</details>
