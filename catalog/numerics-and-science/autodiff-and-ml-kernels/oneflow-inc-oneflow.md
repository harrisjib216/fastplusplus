# OneFlow

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Distributed deep learning training framework (C++/CUDA core, PyTorch-like Python API); vendor DLPerf shows 1.1-1.5x NGC PyTorch/MXNet on 32 V100s.

| | |
|---|---|
| **Beats** | NVIDIA NGC 20.03 containers (MXNet 1.6.0, TensorFlow 1.15.2, PyTorch 1.5.0a0) running NVIDIA DeepLearningExamples, plus stock PyTorch 1.6.0, TensorFlow 2.3.0, MXNet 1.6.0 (gluon-cv/gluon-nlp), PaddlePaddle 1.8.3 and MindSpore official model scripts |
| **Claimed result** | DLPerf README summary (4 nodes x 8 V100-SXM2-16GB; report published Oct 2020). ResNet-50 v1.5 FP32 bsz=128: OneFlow 12411.97 img/s vs NGC MXNet 11233.92, NGC PyTorch 10917.09, PyTorch 10021.29, NGC TensorFlow 1.x 9514.64, TensorFlow 2.x 9418.44 (about 1.14x vs NGC PyTorch and 1.10x vs NGC MXNet, derived from page data). AMP bsz=256: OneFlow 33141.02 vs NGC MXNet 30713.68, NGC TensorFlow 1.x with XLA 29171.69 (bsz=224), NGC PyTorch 22551.16 (about 1.47x vs NGC PyTorch and 1.08x vs NGC MXNet, derived). BERT-base AMP bsz=max: OneFlow 15724.70 (bsz=160) vs NGC TensorFlow 1.x with XLA 11650.0 (bsz=96) and NGC PyTorch 10349.12 (bsz=96), about 1.35x and 1.52x (derived); without gradient clipping OneFlow 17210.63 vs MXNet 14822.31 (about 1.16x, derived). |
| **Workload** | DLPerf training throughput on 4 nodes with 8 Tesla V100-SXM2-16GB each: ResNet-50 v1.5 (images/s) and BERT-base pretraining (sentences/s), FP32 and automatic mixed precision. |
| **Metric** | throughput |
| **Hardware** | 4 nodes x 8 Tesla V100-SXM2-16GB; Intel Xeon Gold 5118 @ 2.30GHz, 384 GB RAM, InfiniBand 100 Gb/s EDR (Mellanox MT27700) per node; Ubuntu 16.04.4, CUDA 10.2, driver 440.33.01 (DLPerf report v1) |
| **Adoption** | 9.4k stars; on PyPI as oneflow 0.9.0 (2023-01-07) |
| **Last commit** | 2025-08-20 |
| **Links** | [repository](https://github.com/Oneflow-Inc/oneflow) · [benchmark](https://github.com/Oneflow-Inc/DLPerf/blob/master/README.md) |

## Verdict

OneFlow's own DLPerf report (Oct 2020) trains ResNet-50 v1.5 and BERT-base on 4 nodes x 8 V100-SXM2-16GB (Xeon Gold 5118 hosts, 100 Gb/s InfiniBand, CUDA 10.2) with each framework's official or NVIDIA DeepLearningExamples scripts, taking the median of repeated 100-step runs. OneFlow 0.2.0 reached 12411.97 img/s FP32 and 33141.02 img/s AMP on ResNet-50 vs 10917.09 and 22551.16 for NGC PyTorch 20.03 (about 1.14x and 1.47x) and 11331.93 and 30713.68 for NGC MXNet (about 1.10x and 1.08x), and 15724.70 vs 10349.12 sentences/s (about 1.52x) on BERT AMP against NGC PyTorch; ratios derived from page data, no compiler flags given for any framework.

## Use it when

- Multi-node, multi-GPU training on NVIDIA clusters where you want data, tensor (model) and pipeline parallelism expressed through placement/SBP annotations instead of hand-written NCCL calls.
- Large embedding or recommendation (Wide&Deep-style) training: DLPerf shows OneFlow 0.2.0 holding about 22.4 ms per iteration up to 819.2M-row vocabularies, while HugeCTR 2.2 ran out of memory above 25.6M rows.
- Teams that already write PyTorch-style code and want a static-graph compile step (nn.Graph) with ZeRO, gradient accumulation and activation checkpointing built in.
- Chinese accelerator targets: recent commits add Ascend NPU, Cambricon MLU and KunLunXin XPU device support.

## Skip it when

- As a kernel library to drop into an existing C++ or PyTorch codebase: it is a whole framework, and the C++ API is beta and off by default.
- Single-GPU training: the vendor's own numbers show near parity with NGC MXNet on one V100 (about 1.4% FP32), so the claimed gains appear only at multi-node scale.
- Projects that need current releases and fast bug turnaround: PyPI stops at 0.9.0 (2023-01-07), v1.0.0 exists only as a GitHub release, the last commit was 2025-08-20, and performance issues such as #10437 (slow elementwise template on RTX 3090) have no visible maintainer reply.
- Comparisons on modern hardware: every published framework-vs-framework number is from 2020 (OneFlow 0.2.0, V100, CUDA 10.2) against 2020 NGC containers; nothing shows the gap still holds against current PyTorch.
- Windows or macOS hosts: the README lists Linux only, with Python 3.7 to 3.11, and the PyPI wheels are x86-64 manylinux only.

## How it is fast

Per the OneFlow paper (arXiv 2110.15032; abstract read via WebSearch, PDF not opened), the speed comes from two ideas: the SBP abstraction, which lets the compiler insert the needed collective ('boxing') operations automatically, and an actor-model runtime where each op is an actor that runs when its inputs and its output buffers are ready, so compute, data movement and communication overlap without a central scheduler. The DLPerf numbers point to scaling rather than per-kernel speed: on one V100, ResNet-50 FP32 is 397.64 vs 392.24 img/s for NGC MXNet (about 1.4%, derived from page data), widening to 12411.97 vs 11331.93 at 32 GPUs. The build also enables fused/fast-math softmax and layer-norm kernels by default (OF_SOFTMAX_USE_FAST_MATH, OF_LAYER_NORM_USE_FAST_MATH).

## Compared with alternatives

The catalogued siblings (LightSeq, ByteTransformer, FasterTransformer, oneDNN Graph Compiler) are kernel or inference libraries that plug into an existing framework; pick OneFlow only when you want to replace the training framework itself to get SBP-based multi-node parallelism. If you just need faster transformer layers inside PyTorch training, LightSeq is the smaller change.

## Integration

| | |
|---|---|
| **Form** | module (Python package with a C++/CUDA shared-library core; pip wheels or CMake source build) |
| **Dependencies** | CUDA Toolkit 10.0+ and cuDNN for GPU builds, NCCL, oneDNN (WITH_ONEDNN on by default), OpenBLAS, nasm, protobuf/gRPC-era third-party libraries built by the CMake THIRD_PARTY step; optional MLIR, RDMA |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17), CMake 3.18+, CUDA 10.0+ with driver 440.33+, Python 3.7-3.11 |
| **Platforms** | Linux x86-64; NVIDIA GPUs with compute capability 6.0+ (Pascal and newer); CPU-only builds; Ascend NPU, Cambricon MLU and KunLunXin XPU backends in recent commits |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — the API mirrors PyTorch (oneflow.mock_torch can redirect `torch` imports), but it is a separate framework with its own runtime, kernels and model files, not a replacement for PyTorch, TensorFlow or MXNet internals |

## Gotchas

- Softmax and layer-norm kernels are compiled with fast-math variants by default (OF_SOFTMAX_USE_FAST_MATH and OF_LAYER_NORM_USE_FAST_MATH are ON), which can change low-order bits compared with PyTorch.
- The headline BERT comparison against MXNet is run without gradient clipping (gluon-nlp lacks clip_by_global_norm); at AMP batch 64 on 32 GPUs, MXNet without clipping (11269.14) is slightly ahead of OneFlow without clipping (11195.72).
- Sources in the DLPerf table disagree: the README summary lists NGC MXNet ResNet-50 FP32 at 11233.92 img/s, while the report's 4x8 row gives 11331.93.
- The CUDA build cache defaults to RelWithDebInfo and shared libraries; the README's source build expects CUDA_TOOLKIT_ROOT_DIR and CUDNN_ROOT_DIR to be set, and NCCL may fail under make -j\$(nproc) (troubleshooting doc).

## Known shortcomings

- Vendor-run (Oct 2020) with 2020-era baselines; only 1.10x FP32 / 1.08x AMP over NGC MXNet; README NGC MXNet 11233.92 vs report 11331.93 inconsistency; stale.
- Speedup comes from multi-node scaling: on 1 V100 only \~1.4% over NGC MXNet (397.64 vs 392.24); on BERT AMP bsz64 at 32 GPUs MXNet without clip beats OneFlow without clip (11269.14 vs 11195.72); newest PyPI is 0.9.0 (2023) and v1.0.0 is a GitHub release only; softmax/layernorm fast-math on by default.

## Caveats and trade-offs

Benchmark run and published by the OneFlow vendor (Oneflow-Inc/DLPerf) in Oct 2020 with OneFlow 0.2.0 against 2020-era framework versions; none has been re-run on current releases. Compiler and build flags are not stated for any framework. OneFlow's margin over the strongest baseline (NGC MXNet) is small: about 1.10x FP32 and 1.08x AMP on ResNet-50. Baseline caveats: TensorFlow 1.x AMP used bsz=224 (OOM at 256), PyTorch (non-NGC) AMP is missing, MXNet BERT lacks gradient clipping. The README summary lists NGC MXNet FP32 at 11233.92 img/s while the report's 4x32 row gives 11331.93, an internal inconsistency. Last commit 2025-08-20, so stale.

Full deep learning framework (PyTorch-like API, global tensors, graph compiler); the speed claim is an end-to-end training result that mixes kernels, scheduling and communication, not a kernel library result.

## Maintenance

Stale: last commit 2025-08-20 (NPU multinomial support), with the newest PyPI wheel 0.9.0 from 2023-01-07, though the repo is not archived, is Apache-2.0 and has about 9.4k stars; treat it as a framework to evaluate, not a library to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Vendor-run DLPerf benchmark (Oneflow-Inc) with public scripts per framework and a report that names the host CPU (Xeon Gold 5118), V100 GPUs, CUDA 10.2 and driver, but no compiler or build flags for any framework, so it falls short of A; first-party, so C.
- **Verifier notes:** README numbers match the record; the v1 report adds host CPU, CUDA and container versions. Corrected hardware and baseline versions; status stays stale (last commit 2025-08-20, about 13 months ago).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/README.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/reports/dlperf_benchmark_test_report_v1.md>
  - <https://github.com/Oneflow-Inc/oneflow>
  - <https://github.com/Oneflow-Inc/oneflow/commits>
  - <https://pypi.org/pypi/oneflow/json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Oneflow-Inc/oneflow/HEAD/README.md>
  - <https://github.com/Oneflow-Inc/oneflow>
  - <https://github.com/Oneflow-Inc/oneflow/releases>
  - <https://github.com/Oneflow-Inc/oneflow/commits>
  - <https://github.com/Oneflow-Inc/oneflow/tree/master/oneflow/core>
  - <https://raw.githubusercontent.com/Oneflow-Inc/oneflow/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Oneflow-Inc/oneflow/HEAD/cmake/caches/international/cuda.cmake>
  - <https://raw.githubusercontent.com/Oneflow-Inc/oneflow/HEAD/docs/source/troubleshooting.md>
  - <https://github.com/Oneflow-Inc/oneflow/issues?q=is%3Aissue+is%3Aopen+performance>
  - <https://github.com/Oneflow-Inc/oneflow/issues/10437>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/README.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/reports/dlperf_benchmark_test_report_v1.md>
  - <https://pypi.org/pypi/oneflow/json>
  - WebSearch: OneFlow paper abstract (arXiv 2110.15032, SBP and actor model)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/oneflow-inc/oneflow`) · [data/wave8/enrich/raw/github_com_oneflow_inc_oneflow.json](../../../data/wave8/enrich/raw/github_com_oneflow_inc_oneflow.json) (enrichment confidence 0.7)

</details>
