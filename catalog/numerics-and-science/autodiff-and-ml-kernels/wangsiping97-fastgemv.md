# FastGEMV (fp16/int8/int4 GEMV CUDA kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++ (CUDA)` · `MIT` · 🔴 abandoned

> Three small CUDA GEMV kernels (fp16, int8, int4 weights x fp16 vector) beating 2023 PyTorch fp16 matmul by 1.1-2.7x.

| | |
|---|---|
| **Beats** | PyTorch fp16 matrix-vector product (torch.matmul on a size x size fp16 matrix and size x 1 vector, baseline.py, kernel time via Nsight Systems) |
| **Claimed result** | README: max 2.7x speedup vs PyTorch on P100 and 1.4x on 3090 Ti. method_and_result.md, P100 fp16: 1.441x (n=512), 1.627x (1024), 1.551x (2048), 1.599x (4096), 2.695x (8192), 1.781x (16384); estimated bandwidth 602.0 GB/s vs PyTorch 320.8 GB/s at n=16384 (peak 732 GB/s). RTX 3090 fp16 kernel: 4372.4 ns vs PyTorch 6106.2 ns at n=1024 (about 1.40x, derived from page data); 609235 ns vs 691660.6 ns at n=16384 (about 1.14x, derived from page data). |
| **Workload** | GEMV of an n x n fp16 matrix with an n x 1 fp16 vector for n=512..16384, plus int8 and int4 quantized-matrix variants that PyTorch cannot run directly; kernel runtime and estimated memory bandwidth. |
| **Metric** | latency |
| **Hardware** | NVIDIA P100 and RTX 3090 (README says 3090 Ti, results doc says 3090); host CPU not stated |
| **Compiler and flags** | nvcc -O3 -m64 -std=c++17 with -gencode sm_60/sm_70/sm_75/sm_86 (Makefile); README requirements list CUDA 11.7 and Nsight Systems 2023.1.2; PyTorch version not stated |
| **Adoption** | 130 stars |
| **Last commit** | 2023-06-06 |
| **Links** | [repository](https://github.com/wangsiping97/FastGEMV) · [benchmark](https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/method_and_result.md) |

## Verdict

Nsight Systems kernel-time averages (10,000 iterations) for an n x n fp16 matrix times an n x 1 fp16 vector, against torch.matmul of mid-2023 (PyTorch version not stated; nvcc -O3, CUDA 11.7): 1.44-2.70x faster on a P100 (peak at n=8192, where PyTorch dropped to 202 GB/s) and 1.02-1.40x faster on an RTX 3090 (4372.4 vs 6106.2 ns at n=1024, 609235 vs 691660.6 ns at n=16384). One independent user report (issue #3, A30, CUDA 12.2, PyTorch 2.1) found the fp16 kernel slower than PyTorch at n=16384.

## Use it when

- Batch-1 matrix-vector products on fp16 weights (LLM-decode-style GEMV) on Pascal or consumer Ampere GPUs, where you can hand-pick blockDim per matrix size.
- Weight-only int8 or int4 GEMV with a single per-tensor scale/zero point, when you want the bandwidth saving of quantized weights in a kernel small enough to read in a few minutes.
- Power-of-two sizes from 512 to 16384, the only range the authors measured.
- As a teaching example of vectorized loads plus warp-shuffle reduction for memory-bound kernels.

## Skip it when

- Modern data-center GPUs without re-measuring: issue #3 (open) reports the fp16 kernel slower than PyTorch on an A30 (8550.95 ms vs 6031.96 ms for 10,000 iterations at n=16384, about 0.71x, derived from page data).
- Real quantized LLM weights: only one per-tensor scale and zero point is supported (no per-channel or group-wise scales), and int4 values are unsigned 0..15.
- Batch sizes above 1 (GEMM), non-power-of-two or non-square shapes: the README and harness assume square power-of-two sizes, and issue #6 asking about rectangular matrices has no answer.
- Small fp16 matrices on newer cards when the gain matters: on the 3090 the fp16 speedup is 1.02x at n=8192 and 1.13x at n=2048 (derived from page data).
- Long-lived production use: no commits since 2023-06-06 and no releases.

## How it is fast

GEMV is memory-bound, so the kernels aim at DRAM bandwidth: p = blockDim.x threads share one row, each loading 16 bytes at a time (float4 holding 8 halves; half4 holding 8 int8 values; two 4-byte packs of 8 int4 values each), and multiply in fp32 registers. Partial sums are combined with a __shfl_down_sync warp reduction (CUTLASS-style), plus one shared-memory pass when a row uses more than 32 threads. Block shape is hand-tuned per size and GPU; on the 3090 at n=16384 the fp16 kernel reaches an estimated 881.8 GB/s of 936 GB/s versus 776.3 GB/s for PyTorch.

## Compared with alternatives

Pick FastGEMV over Marlin or BitBLAS when you want a tiny fp16 or per-tensor int8/int4 GEMV you can read and adapt; Marlin and BitBLAS support group-wise quantization, batch sizes above 1 and newer GPUs, and are measured against current baselines. fast.cu and bare-metal target compute-bound GEMM, not matrix-vector work.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA runtime and cuda_fp16; curand only for the test data generator; PyTorch only for baseline.py; Nsight Systems for the published timings |
| **Minimum toolchain** | C++17 nvcc; README lists CUDA 11.7 and Nsight Systems 2023.1.2; Makefile builds SASS for sm_60, sm_70, sm_75 and sm_86 only |
| **Platforms** | NVIDIA GPUs; measured on P100 and RTX 3090 (README says 3090 Ti); other architectures such as sm_80/sm_89/sm_90 need a Makefile -gencode edit because no PTX fallback is emitted |
| **Thread safety** | not documented (stateless kernels; launches are the caller's responsibility) |
| **Drop-in for the baseline** | false - raw __global__ kernels with caller-chosen launch geometry, not a torch.matmul or cublasGemv replacement |

## Gotchas

- Launch geometry is the caller's job and is not bounds-checked: rows are not guarded, so n must be divisible by blockDim.y; n / blockDim.x must be at least 8 (fp16/int8) or 16 (int4); blockDim.y must be at most 64 (shared-memory array size); and n must be a multiple of 8 for the 16-byte loads.
- Best blockDim differs by size and GPU (for example n=4096 uses 128x8 on the P100 but 256x1 on the 3090), so the published speedups need the same per-size tuning.
- The harness's correctness kernels only print mismatches and never fail the run; the fp16 tolerance is an absolute 0.125 \* n / 512 (4.0 at n=16384).
- The int8/int4 timings move 2x/4x fewer matrix bytes than the fp16 PyTorch baseline, so their 'speedups' are not like-for-like; PyTorch had no direct quantized GEMV to compare against.

## Known shortcomings

- On RTX 3090 the gain is only 1.02x at n=8192; PyTorch version not stated; abandoned since 2023-06-06.
- Open issue #3: an A30 run (CUDA 12.2, PyTorch 2.1, n=16384) had the fp16 kernel slower than PyTorch (8550.95 vs 6031.96 ms for 10k iterations, \~0.71x, derived). Makefile emits SASS only for sm_60/70/75/86, no PTX. The harness correctness check only prints mismatches and never fails the run.

## Caveats and trade-offs

Benchmarks date from May-June 2023 against the PyTorch (and the cuBLAS it dispatches to) of that time; the PyTorch version is not stated and newer releases may have closed the gap. The 2.7x peak is a single size (n=8192 on a P100), where the PyTorch baseline dips to 202 GB/s against 333 GB/s at n=4096. On the 3090 the fp16 gain is 1.02x at n=8192 (156448.3 vs 159163.1 ns) and 1.13x at n=2048 (12395.4 vs 13971.8 ns), both derived from page data, peaking at 1.40x at n=1024. Launch configurations are hand-tuned per size and per GPU. The int8/int4 columns move far fewer bytes than the fp16 PyTorch baseline, so they are not like-for-like. The README names a 3090 Ti while the results document says 3090. Timings are Nsight Systems kernel averages, not end-to-end wall clock. Host CPU not stated.

Square power-of-two sizes only (512..16384); per-tensor scale and zero point for int8/int4; blockDim must be tuned per size and GPU; no batching; tested on Pascal and Ampere only.

## Maintenance

Abandoned since 2023-06-06 (130 stars, MIT, four open issues without maintainer replies), but the kernels are a few hundred lines and easy to vendor and retune.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** method_and_result.md gives per-size kernel times for the project and PyTorch fp16 matmul on P100 and RTX 3090. Both sides are public: baseline.py (torch a.matmul(b), 10,000 iterations under nsys) and test_gemv.cu/fast_gemv.cu with a correctness check. The Makefile states the nvcc flags (-O3 -m64 -std=c++17, sm_60/70/75/86), the README pins CUDA 11.7 and Nsight Systems 2023.1.2, and both GPUs and their launch configurations are named. That meets A under the wave's GPU-kernel precedent; the PyTorch version and host CPU are missing.
- **Verifier notes:** All claimed P100 and 3090 numbers match method_and_result.md exactly. Metadata on github.com: MIT, 130 stars, 8 forks, not a fork, 52 commits, last commit 2023-06-06 (abandoned is right).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/method_and_result.md>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/README.md>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/Makefile>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/baseline.py>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/test_gemv.cu>
  - <https://github.com/wangsiping97/FastGEMV>
  - <https://github.com/wangsiping97/FastGEMV/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/README.md>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/method_and_result.md>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/Makefile>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/baseline.py>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/fast_gemv.cuh>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/fast_gemv.cu>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/test_gemv.cu>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/simple_tensor.h>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/utility.cuh>
  - <https://raw.githubusercontent.com/wangsiping97/FastGEMV/HEAD/utility.cu>
  - <https://github.com/wangsiping97/FastGEMV/issues?q=is%3Aissue>
  - <https://github.com/wangsiping97/FastGEMV/issues/3>
  - <https://github.com/wangsiping97/FastGEMV/issues/4>
  - <https://github.com/wangsiping97/FastGEMV/issues/6>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/wangsiping97/fastgemv`) · [data/wave8/enrich/raw/github_com_wangsiping97_fastgemv.json](../../../data/wave8/enrich/raw/github_com_wangsiping97_fastgemv.json) (enrichment confidence 0.8)

</details>
