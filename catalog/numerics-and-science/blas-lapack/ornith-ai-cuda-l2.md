# CUDA-L2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> 1,000 per-shape fp16 GEMM CUDA kernels found by LLM-guided reinforcement learning; on average 7-12% faster than autotuned cuBLASLt on A100/3090/H100 (offline mode).

| | |
|---|---|
| **Beats** | NVIDIA cuBLAS (also cuBLASLt heuristic, cuBLASLt AutoTuning, torch.matmul) |
| **Claimed result** | README, average gains over 1,000 (M,N,K) shapes, vs torch.matmul / cuBLAS / cuBLASLt-heuristic / cuBLASLt-AutoTuning. A100 F32F16F16F32: offline +22.5% / +20.4% / +16.9% / +12.2%, server +25.1% / +21.5% / +19.9% / +12.7%. H100 F32F16F16F32: offline +19.8% / +17.5% / +28.8% / +7.0%, server +41.7% / +40.5% / +42.1% / +22.1%. RTX 3090 F32F16F16F32: offline +21.3% / +24.2% / +21.1% / +12.7%, server +28.7% / +35.3% / +28.1% / +19.8%. A100 F16F16F16F16: offline +22.0% / +19.2% / +16.8% / +11.4%, server +28.7% / +26.0% / +22.4% / +15.9%. From the per-shape offline CSVs (derived from page data): the README figures are arithmetic means of per-shape speedups; the geometric mean vs cuBLASLt-AutoTuning is 1.11x on A100 and 1.056x on H100. |
| **Workload** | Half-precision HGEMM kernels (16-bit accumulate and 32-bit accumulate) tuned per (M,N,K) configuration across about 1,000 shapes, measured in offline and server modes on A100, RTX 3090 and H100. |
| **Metric** | throughput |
| **Hardware** | NVIDIA A100, RTX 3090, H100 (host CPU not stated) |
| **Compiler and flags** | nvcc through torch.utils.cpp_extension.load with -O3 -std=c++17 --use_fast_math --expt-relaxed-constexpr --expt-extended-lambda (tools/utils.py get_build_cuda_cflags); TORCH_CUDA_ARCH_LIST 8.0 for A100/RTX 3090 and 9.0a for H100; CUTLASS v4.2.1 and PyTorch &gt;= 2.6.0. The CUDA toolkit/nvcc version is not stated. |
| **Adoption** | 482 stars |
| **Last commit** | 2026-03-30 |
| **Links** | [repository](https://github.com/ornith-ai/CUDA-L2) · [benchmark](https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/README.md) |

## Verdict

First-party harness on an A100, an RTX 3090 and an H100 (host and CUDA version not stated), with kernels built with nvcc -O3 --use_fast_math against CUTLASS 4.2.1. Each call is timed by host wall clock around one synchronized launch, with the cuBLAS layout (TN or NN) that is faster for each shape. Averaged over 1,000 shapes (64 to 16384 per dimension), the offline gain over autotuned cuBLASLt (20 GB workspace) is +12.2% on A100, +12.7% on RTX 3090 and +7.0% on H100 for fp32 accumulate. These are arithmetic means of per-shape ratios; geometric means are 1.11x (A100) and 1.056x (H100), and 300 and 338 shapes respectively are slower than cuBLASLt (derived from page data).

## Use it when

- Fixed, known fp16 GEMM shapes in an inference service (projection layers at a few batch sizes) on exactly an A100, RTX 3090 or H100, where the shape (or a slightly larger padded one) is in the released set
- Small and skinny problems: from the per-shape CSVs (derived from page data), for 2MNK below 1e9 the geomean over cuBLASLt-AutoTuning is 1.24x on A100 and 1.13x on H100
- Latency-sensitive serving with idle gaps between calls: the 'server' mode, with Poisson-spaced calls, shows larger gains (+12.7% A100, +22.1% H100 over cuBLASLt-AutoTuning) than back-to-back offline runs
- As a reference for what per-shape CuTe/mma.sync tuning can recover over cuBLAS heuristics on Ampere

## Skip it when

- Large GEMMs: for 2MNK of 1e11 or more the per-shape CSVs give a geomean of about 0.98x (A100) and 0.91-0.94x (H100) against cuBLASLt-AutoTuning, and the worst shapes run at 0.545x (A100) and 0.209x (H100) (derived from page data)
- Arbitrary or dynamic shapes: no runtime dispatch, and padding to a larger released shape spends extra flops
- Other GPUs, or the same GPU family with different SM counts or clocks: the FAQ says A100 kernels are only expected to win on A100
- FP32, BF16, FP8, batched or strided GEMM, or epilogues with alpha/beta/bias: only plain fp16 C = A\*B with fp16 output
- Projects that cannot take a PyTorch build-time dependency or need a C++ API without torch::Tensor

## How it is fast

An LLM proposes kernel code and an RL loop rewards measured speed, so each shape gets its own tile sizes, pipeline depth and variant choice. The kernels inspected use standard Ampere-style tensor-core techniques: CuTe tiled mma.sync (SM80 16x8x16) with cp.async multi-stage shared-memory pipelines, swizzled shared-memory layouts and ldmatrix loads (e.g. the A100 64x4096x64 kernel: BM=64, BN=128, BK=32, 3 stages). The H100 64x4096x64 file uses hand-written PTX mma.sync, not Hopper wgmma/TMA, and times three variants on its first call to pick one. The win comes from per-shape specialization on small and skinny problems where cuBLAS heuristics pick poor configurations.

## Compared with alternatives

Pick CUDA-L2 for fixed small or skinny fp16 shapes on A100, RTX 3090 or H100. Pick blackwell-tensorcore-kernels for large square fp16 GEMM on sm_120, and gpu-compute for true-FP32 tiny GEMMs on Blackwell. Unlike CUDA-L2, those two are general kernels rather than a per-shape lookup.

## Integration

| | |
|---|---|
| **Form** | source-drop (one .cu per shape, built as a PyTorch C++/CUDA extension via torch.utils.cpp_extension.load) |
| **Dependencies** | PyTorch &gt;= 2.6.0, NVIDIA CUTLASS/CuTe v4.2.1 headers, CUDA toolkit (cuBLAS/cuBLASLt only for the baselines) |
| **Minimum toolchain** | nvcc with -std=c++17 (CUDA toolkit version not documented); TORCH_CUDA_ARCH_LIST 8.0 or 9.0a |
| **Platforms** | NVIDIA sm_80 (A100, RTX 3090 kernels) and sm_90a (H100 kernels) only |
| **Thread safety** | not documented; the inspected H100 kernel keeps first-call autotuning state in unsynchronized static globals |
| **Drop-in for the baseline** | no |

## Gotchas

- Callers must replicate the harness's input preparation: A, B and a pre-transposed B copy zero-padded to the kernel's BM/BN/BK multiples (the A100 kernel loops k/BK with no tail handling), and C allocated at the padded size and sliced afterwards.
- Kernels launch with &lt;&lt;&lt;grid, block&gt;&gt;&gt; on the legacy default stream, not PyTorch's current stream, so they can serialize with or race against other streams' work.
- Some H100 files time three variants with cudaEvents on the first call and cache the choice in a static, so the first call is slow and the choice is made once for the whole process.
- Built with --use_fast_math. The harness's correctness gate tests only 0/1-valued inputs against a CPU FP32 reference (exact match required), so it is a weak check for general rounding behaviour. Issue #6 (open) reports eval_one_file.sh bugs, such as a wrong unknown-option message and rm failing on a fresh directory.

## Known shortcomings

- README gains are arithmetic means; per its CSVs it is slower than cuBLASLt-AutoTuning on 300/1000 shapes on A100 and 338/1000 on H100 (worst 0.21x); for M, N, K all &gt;= 4096 it is 0.986x on A100 and 0.928x on H100; builds with --use_fast_math; GEMM, so moved to blas-lapack; first published as deepreinforce-ai/CUDA-L2.
- Kernels need inputs zero-padded to tile multiples (no K tail); launch on the legacy default stream; the H100 64x4096x64 file autotunes on first call into unsynchronized statics and uses SM80 mma.sync, not wgmma; correctness gate tests 0/1 inputs only; geomean vs cuBLASLt-AutoTuning 1.24x A100 / 1.13x H100 below 1e9 flops but 0.98x / 0.91-0.94x at 1e11+ (derived); harness bugs (#6) open.

## Caveats and trade-offs

Plain HGEMM against cuBLAS, so it belongs closer to blas-lapack than to DL-layer kernels; baseline_in_list is false because cuDNN, oneDNN, XNNPACK and Eigen are not the comparison. Gains are per-shape averages for the 1,000 released shapes only (other shapes need zero-padding to the nearest released one), and the kernels are tuned per GPU. Per-shape offline CSVs in eval_results/ (derived from page data): CUDA-L2 is slower than cuBLASLt-AutoTuning on 300 of 1,000 shapes on A100 (worst 0.545x) and 338 of 1,000 on H100 (worst 0.209x); for the 64 shapes with M, N and K all &gt;= 4096 the mean is 0.986x (A100) and 0.928x (H100), so the win concentrates on small and skinny shapes. The kernels build with --use_fast_math. The CUDA toolkit version is not stated, and the paper (arXiv 2512.02551) could not be opened (arxiv.org blocked). The repo was first published as deepreinforce-ai/CUDA-L2 (LICENSE copyright deepreinforce.ai).

GPU-only, fp16 GEMM only, with kernels specialized per (M,N,K) tuple found by an LLM+reinforcement-learning search; shapes not in the released set need zero-padding to a neighbouring configuration or a request in GitHub issues. Requires PyTorch and CUTLASS; kernels trained on one GPU may not carry over to another.

## Maintenance

Research artifact from DeepReinforce (MIT, 482 stars, 21 commits; H100 kernels added 2026-03-30, the last commit) with open harness bugs. It is copyable kernel by kernel, but it is a per-shape snapshot rather than a maintained library, and no independent reproduction turned up in one web search.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables of average percent gains over torch.matmul, cuBLAS and cuBLASLt, backed by public per-shape CSVs in eval_results/ and the harness (eval_one_file.sh, benchmarking_offline.py, benchmarking_server.py, tools/utils.py, which sets the nvcc flags). The CUDA toolkit/nvcc version is not stated in the repo, and the arXiv preprint (not peer-reviewed as far as seen) could not be opened, so A and B are both out of reach.
- **Verifier notes:** README numbers match the record, and the A100 F32 offline means re-derive exactly from eval_results/cuda_l2_a100_F32F16F16F32_speedup_offline.csv (1.2248, 1.2042, 1.1694, 1.1216). Metadata from github.com: MIT, 482 stars, 32 forks, not a fork or archived, last commit 2026-03-30. Consider moving it to blas-lapack; it is slower than tuned cuBLASLt on large square GEMMs.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ornith-ai/CUDA-L2>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/README.md>
  - <https://github.com/ornith-ai/CUDA-L2/commits>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/compile.py>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/eval_one_file.sh>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/benchmarking_utils.py>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/tools/utils.py>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/LICENSE.txt>
  - <https://github.com/ornith-ai/CUDA-L2/tree/main/eval_results>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/eval_results/cuda_l2_a100_F32F16F16F32_speedup_offline.csv>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/eval_results/cuda_l2_h100_F32F16F16F32_speedup_offline.csv>
- **Sources the enricher read:**
  - <https://github.com/ornith-ai/CUDA-L2>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/README.md>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/tools/utils.py>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/compile.py>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/eval_one_file.sh>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/benchmarking_utils.py>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/benchmarking_offline.py>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/benchmarking_server.py>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/zero_one_correctness_check.py>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/summarize_result.py>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/pybind/hgemm_a100_fp32.cc>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/pybind/hgemm_h100_fp32.cc>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/kernels/a100_F32F16F16F32/64_4096_64.cu>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/kernels/h100_F32F16F16F32/64_4096_64.cu>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/cublas/fp32/hgemm_cublas.cu>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/cublas/fp32/hgemm_cublaslt_auto_tuning.cu>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/eval_results/cuda_l2_a100_F32F16F16F32_speedup_offline.csv>
  - <https://raw.githubusercontent.com/ornith-ai/CUDA-L2/HEAD/eval_results/cuda_l2_h100_F32F16F16F32_speedup_offline.csv>
  - <https://github.com/ornith-ai/CUDA-L2/tree/main/kernels>
  - <https://github.com/ornith-ai/CUDA-L2/issues?q=is%3Aissue>
  - <https://github.com/ornith-ai/CUDA-L2/issues/6>
  - WebSearch: CUDA-L2 HGEMM cuBLAS reinforcement learning kernels independent benchmark criticism
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ornith-ai/cuda-l2`) · [data/wave8/enrich/raw/github_com_ornith_ai_cuda_l2.json](../../../data/wave8/enrich/raw/github_com_ornith_ai_cuda_l2.json) (enrichment confidence 0.75)

</details>
