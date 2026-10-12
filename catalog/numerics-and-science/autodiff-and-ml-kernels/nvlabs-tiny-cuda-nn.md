# tiny-cuda-nn

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++/CUDA` · `BSD-3-Clause` · 🟢 active

> CUDA framework whose fully fused small-MLP kernels train and infer 2x-10x faster than TensorFlow 2.5 XLA (RTX 3090).

| | |
|---|---|
| **Beats** | TensorFlow v2.5.0 with XLA (which uses cuDNN/cuBLAS) |
| **Claimed result** | The README chart (data/readme/fully-fused-vs-tensorflow.png) shows fully fused MLPs ahead of TensorFlow 2.5.0 with XLA at every batch size from 2^14 to 2^21 on an RTX 3090. Read from the chart (approximate, derived from page data), 64-neuron-wide training throughput is about 1.2e8 vs 0.12e8 elements/s at batch 2^14 (\~10x), narrowing to about 2.0e8 vs 1.0e8 at 2^21 (\~2x). 64-wide inference is about 1.08e9 vs 0.14e9 elements/s at 2^21 (\~8x), with a larger gap at small batches. The 128-wide (dashed) gap is about 2x to 6x for training. Separately, the README claims JIT fusion gives 1.5x to 2.5x over tiny-cuda-nn's own earlier path (it can slow down RTX 3000-series or large models), and Instant NGP gets 5x by fusing its NeRF ray marcher into one kernel. |
| **Workload** | Training and inference throughput (elements per second) of fully fused multi-layer perceptrons 64 and 128 neurons wide, batch sizes 2^14 to 2^21. |
| **Metric** | throughput |
| **Hardware** | NVIDIA RTX 3090 |
| **Adoption** | 4.5k stars; used by Instant NGP and NerfStudio |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/NVlabs/tiny-cuda-nn) · [benchmark](https://github.com/NVlabs/tiny-cuda-nn/blob/master/README.md) |

## Verdict

The only external comparison is the author's chart: fully fused MLPs 64 and 128 neurons wide vs TensorFlow 2.5.0 with XLA (whose script also runs the matmuls in FP16) on an RTX 3090, learning an image at batch sizes 2^14-2^21; read approximately, 64-wide training is about 10x faster at 2^14 narrowing to about 2x at 2^21, and inference about 8x at 2^21. CUDA, driver and compiler versions are not stated; the 1.5x-2.5x JIT-fusion and 5x Instant NGP figures are against tiny-cuda-nn's own earlier path, not an external baseline.

## Use it when

- Neural fields, NeRF/neural radiance caching, SDFs and other coordinate networks: millions of points per step through MLPs 16-128 neurons wide, often after a hash-grid or frequency encoding.
- Online training inside a renderer or simulator where both training and inference must run every frame on the GPU.
- Large batches (2^14 and up); the README says PyTorch-binding overhead roughly doubles runtime at 64k batch but is much smaller from 256k.
- Tensor-core NVIDIA GPUs (compute capability above 7.0, e.g. Turing and newer) with enough shared memory; the README names RTX 2080 Ti / RTX 3090 or higher for the default fully fused configuration.

## Skip it when

- Wide or general networks: FullyFusedMLP accepts only 16, 32, 64 or 128 neurons per hidden layer; anything else needs the slower CutlassMLP, and convolutions, attention or recurrent layers are not provided.
- Non-NVIDIA hardware, CPUs, or GPUs at or below compute capability 7.0: the fully fused path is not compiled there and falls back to CutlassMLP; FP32 builds also fall back.
- Lower-end or some data-center GPUs where the default shared-memory footprint does not fit (issue #511 reports the insufficient-shared-memory error on an A100 at 64 neurons, open with no reply).
- Teams without CUDA build expertise: about 240 open issues, dominated by pip/CMake/Windows/new-GPU build failures; there are no tagged releases after 2.0.
- Small batches or per-sample latency work: batch sizes must be multiples of 256 (BATCH_SIZE_GRANULARITY) and the kernels are tuned for throughput.

## How it is fast

The fully fused MLP evaluates every layer of a narrow network in one kernel: each thread block keeps its slice of the batch's activations in shared memory, loads weight tiles into registers and runs the matrix products on tensor cores via WMMA 16x16x16 FP16 fragments, so intermediate activations never go to global memory and there is one launch per pass instead of one per layer. Hidden widths are template parameters (16/32/64/128) and shared-memory rows are skewed by 8 halfs to avoid bank conflicts. Version 2.0 adds JIT fusion: the model is emitted as a CUDA device function and compiled with NVRTC, optionally fused with the caller's own kernel (Instant NGP fuses its whole NeRF ray marcher this way).

## Compared with alternatives

Pick tiny-cuda-nn over ThunderKittens or FlashAttention-3 when the workload is many tiny MLP evaluations (neural fields) rather than large GEMMs or attention, and over RTNeural when you have an NVIDIA GPU and huge batches instead of per-sample CPU inference; for CPU small-GEMM building blocks LIBXSMM is the closer fit.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake add_subdirectory; builds the tiny-cuda-nn STATIC target) or PyTorch extension via pip from bindings/torch |
| **Dependencies** | CUDA toolkit; NVRTC for JIT fusion (TCNN_BUILD_WITH_RTC, on by default); bundled submodules CUTLASS, fmt and nlohmann/json; cuBLAS/cuSolver only for the Shampoo optimizer (off by default); PyTorch for the bindings |
| **Minimum toolchain** | C++17, CMake 3.21+ per README (CMakeLists says 3.18), GCC 8+ or Visual Studio 2019/2022, CUDA 10.2+ on Linux or 11.5+ on Windows |
| **Platforms** | Linux and Windows with an NVIDIA GPU; fully fused MLP needs compute capability &gt; 7.0 and FP16 (TCNN_HALF_PRECISION, default on except sm_61 and &lt;= sm_52); targets up to sm_120 with recent CUDA |
| **Thread safety** | not documented; work is issued on caller-supplied CUDA streams and models hold mutable training state, so treat each model as single-owner |
| **Drop-in for the baseline** | no |

## Gotchas

- The fully fused forward and backward passes throw unless network precision is __half, so outputs and gradients are FP16; mixed-precision accuracy is your problem to check.
- Unsupported widths, too-old GPUs or FP32 builds silently degrade to CutlassMLP (a log warning), which is much slower; check the logged network type.
- JIT fusion is opt-in (set_jit_fusion) and the README warns it can slow training for hash grids over \~20M parameters, MLPs wider than 128, or RTX 3000-series and older GPUs; measure both modes.
- The README benchmark caption still names benchmarks/bench_ours.cu and bench_tensorflow.py, which moved to benchmarks/image/.

## Known shortcomings

- TensorFlow 2.5+XLA comparison is a chart only (read from PNG: about 2x-10x training, 8x+ inference on RTX 3090); README bench paths 404 (real files benchmarks/image/bench_ours.cu and bench_tensorflow.py); no CPU or compiler given.
- FullyFusedMLP accepts only widths 16/32/64/128 in FP16 and silently (log warning only) falls back to the slower CutlassMLP on older GPUs or FP32 builds; open issue #511 reports a shared-memory error on A100 at width 64.

## Caveats and trade-offs

The TensorFlow comparison is a chart with no numbers in the text, against a 2021 TensorFlow 2.5 plus XLA baseline. The README names benchmarks/bench_ours.cu and benchmarks/bench_tensorflow.py, but those paths 404; the files now live at benchmarks/image/bench_ours.cu and benchmarks/image/bench_tensorflow.py (an image-learning workload). CPU model, compiler and CUDA versions are not stated; the CMake defaults are Release and --use_fast_math. The 1.5x-2.5x and 5x figures are against the library's own earlier path or a non-fused application, not an external baseline. The fully fused MLP paper (Mueller et al. 2021, real-time neural radiance caching) could not be opened (tom94.net is blocked here).

Fully fused MLPs work for narrow layers only (up to about 128 neurons; JIT fusion can slow larger models and older GPUs); NVIDIA GPU, CUDA 10.2+ (Linux), C++17, CMake 3.21+; PyTorch bindings add overhead (about 2x slower at batch 64k than native CUDA).

## Maintenance

Active (last commit 2026-09-29, 4.5k stars, used by Instant NGP, Nerfstudio and NerfAcc) and BSD-3-Clause per LICENSE.txt, so copyable, but builds are fragile and the last tagged release is 2.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The only external comparison is a first-party chart (fully fused MLP vs TensorFlow 2.5.0 with XLA, RTX 3090) with no numbers in the text. Benchmark code is public at benchmarks/image/bench_ours.cu and benchmarks/image/bench_tensorflow.py, and CMake defaults to Release with --use_fast_math. CPU model, compiler and CUDA versions are not stated, so it is not A, and no peer-reviewed source could be opened, so it is not B.
- **Verifier notes:** Metadata checked: BSD-3-Clause, 4.5k stars, last commit 2026-09-29, not archived, not a fork. The chart values were read from the PNG and are approximate.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/master/data/readme/fully-fused-vs-tensorflow.png>
  - <https://github.com/NVlabs/tiny-cuda-nn>
  - <https://github.com/NVlabs/tiny-cuda-nn/commits/master>
  - <https://github.com/NVlabs/tiny-cuda-nn/tree/master/benchmarks>
  - <https://github.com/NVlabs/tiny-cuda-nn/tree/master/benchmarks/mlp>
  - <https://github.com/NVlabs/tiny-cuda-nn/tree/master/benchmarks/image>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/master/benchmarks/mlp/bench_mlp_ours.cu>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/master/benchmarks/image/bench_tensorflow.py>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/master/LICENSE.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/HEAD/DOCUMENTATION.md>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/HEAD/src/fully_fused_mlp.cu>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/HEAD/src/network.cu>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/HEAD/include/tiny-cuda-nn/common.h>
  - <https://raw.githubusercontent.com/NVlabs/tiny-cuda-nn/HEAD/benchmarks/image/bench_tensorflow.py>
  - <https://github.com/NVlabs/tiny-cuda-nn>
  - <https://github.com/NVlabs/tiny-cuda-nn/issues>
  - <https://github.com/NVlabs/tiny-cuda-nn/issues/511>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nvlabs/tiny-cuda-nn`) · [data/wave8/enrich/raw/github_com_nvlabs_tiny_cuda_nn.json](../../../data/wave8/enrich/raw/github_com_nvlabs_tiny_cuda_nn.json) (enrichment confidence 0.75)

</details>
