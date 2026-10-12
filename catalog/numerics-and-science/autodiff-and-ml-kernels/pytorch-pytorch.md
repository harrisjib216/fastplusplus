# PyTorch

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> PyTorch: eager-mode C++/CUDA tensor and autograd framework; old community benchmarks show faster CNN forward+backward than TensorFlow 1.x.

| | |
|---|---|
| **Beats** | TensorFlow |
| **Claimed result** | Titan V FP32, PyTorch 0.3.0 vs TensorFlow 1.4.0: vgg16 train 108.8 ms vs 157.2 ms (1.44x), resnet152 train 180.2 ms vs 269.8 ms (1.50x). RTX 2080 Ti FP32, PyTorch 1.0.0 vs TensorFlow 1.12.0: resnet152 train 142.5 ms vs 191.0 ms (1.34x), resnet152 eval 41.8 ms vs 43.6 ms; ratios derived from page data. TensorFlow 1.12.0 is faster on vgg16 train (90.8 ms vs 95.5 ms). |
| **Workload** | u39kun/deep-learning-benchmark: forward-pass (eval) and forward+backward (train) time per batch for VGG16, ResNet152 and DenseNet161, 224x224x3 images, batch size 16, FP32 and FP16, on several NVIDIA GPUs using NGC containers. |
| **Metric** | latency |
| **Hardware** | NVIDIA Titan V, GTX 1080 Ti, Tesla V100 (AWS p3) and RTX 2080 Ti; host CPU not stated |
| **Compiler and flags** | Prebuilt NGC docker images, no build flags: nvcr.io/nvidia/pytorch:17.12 (0.3.0) and :19.01-py3 (1.0.0), nvcr.io/nvidia/tensorflow:17.12 (1.4.0) and :19.01-py3 (1.12.0); CUDA 9.0.176, cuDNN 7.0.0.5, driver 387.34, or CUDA 10.0.130 with cuDNN 7.4.2.24 for the 2080 Ti rows. |
| **Adoption** | 103.8k stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/pytorch/pytorch) · [benchmark](https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/README.md) |

## Verdict

In u39kun/deep-learning-benchmark, a community harness, the mean of 20 timed iterations after 20 warm-ups was measured with batch 16 and synthetic 224x224 input, forward+backward without an optimizer step, in NVIDIA NGC containers. With PyTorch 0.3.0 against TensorFlow 1.4.0 (CUDA 9.0.176, cuDNN 7.0) on a Titan V at FP32, ResNet-152 train took 180.2 against 269.8 ms and VGG16 train 108.8 against 157.2 ms. With PyTorch 1.0.0 against TensorFlow 1.12.0 (CUDA 10.0, cuDNN 7.4.2) on an RTX 2080 Ti, ResNet-152 train took 142.5 against 191.0 ms, while TensorFlow won VGG16 train. OneFlow's DLPerf v1.0 (Oct 2020, up to 32 V100-SXM2-16GB) adds PyTorch 1.6.0 at 10021.29 against TensorFlow 2.3 at 9418.44 img/s for FP32 ResNet-50; upstream PyTorch was not run with AMP there.

## Use it when

- Default choice for GPU training and research in Python: active project (release 2.14.1 on 2026-09-30), CUDA 13, ROCm and Intel GPU backends, the largest model ecosystem.
- Dynamic models with data-dependent control flow, where eager define-by-run autograd avoids static-graph workarounds.
- CNN training on a single NVIDIA GPU where per-step framework overhead matters. ResNet-152 forward+backward at batch 16 took 142.5 ms against 191.0 ms for TensorFlow 1.12 on an RTX 2080 Ti, and 180.2 ms against 269.8 ms for TensorFlow 1.4 on a Titan V (old versions).
- Data-parallel ResNet-50 training at FP32. Upstream PyTorch 1.6.0 led upstream TensorFlow 2.3 and upstream MXNet 1.6.0 at 8, 16 and 32 V100s in OneFlow's DLPerf (10021.29 img/s at 32 GPUs).
- C++ applications that need autograd or a trained model without Python: LibTorch ships the same C++ core.

## Skip it when

- As evidence that PyTorch 2.x beats TensorFlow 2.x with XLA or JAX today: the measured versions are 0.3.0, 1.0.0 and 1.6.0 against TensorFlow 1.4-1.12 and 2.3.
- Mixed-precision multi-GPU throughput with 2020 containers. In DLPerf, NGC PyTorch reached 22551.16 img/s on 32 V100s at fp16, against 29171.69 for NGC TensorFlow 1.x with XLA, 24734.22 without XLA, and 30713.68 for NGC MXNet.
- Loading untrusted checkpoints with torch.load. It is pickle-based, and CVE-2025-32434 (CVSS 9.3, from search snippets) allowed code execution even with weights_only=True up to 2.5.1, fixed in 2.6.0. Prefer safetensors or a current release.
- Old Python or minimal deployments: wheels need Python 3.10+, and the Linux wheel pulls in the CUDA 13 toolkit, cuDNN 9, NCCL, NVSHMEM, cuSPARSELt and Triton as dependencies.
- VGG-style models dominated by large convolutions and dense layers on Volta and Turing cards, where TensorFlow matched or beat it in the same harness: V100 vgg16 train 71.7 ms (TensorFlow 1.5) against 83.5 ms, 2080 Ti 90.8 ms (TensorFlow 1.12) against 95.5 ms.

## How it is fast

Each Python op dispatches with little overhead into C++ ATen kernels, which launch asynchronously on CUDA streams, so the host stays ahead of the GPU. Convolutions and GEMMs go to cuDNN and cuBLAS. With torch.backends.cudnn.benchmark=True, which the measured harness sets, cuDNN autotunes the fastest algorithm per layer shape. A CUDA caching allocator reuses device memory, avoiding cudaMalloc/cudaFree and the syncs they imply. The autograd engine runs the backward graph in C++. Newer releases add torch.compile (TorchInductor generating Triton kernels) and CUDA graphs, but the measured 0.3.0 and 1.0.0 versions predate them.

## Compared with alternatives

Pick PyTorch over MXNet for anything new: MXNet is archived, and upstream PyTorch matched or beat upstream MXNet from 8 GPUs up in DLPerf. Flashlight is the C++-native framework that reported lower overhead than PyTorch 1.8 in its own paper. For transformer inference only, CTranslate2, FasterTransformer or ByteTransformer beat PyTorch baselines (eager or TorchScript) in their catalogued benchmarks.

## Integration

| | |
|---|---|
| **Form** | Python package with C++/CUDA shared libraries (pip wheels, docker images); LibTorch shared-library distribution for C++ |
| **Dependencies** | Linux wheel 2.14.1: CUDA 13.0.3 toolkit components (cuBLAS, cudart, cuFFT, cuFile, CUPTI, cuRAND, cuSOLVER, cuSPARSE, nvJitLink, NVRTC, NVTX), cuDNN 9.24, cuSPARSELt, NCCL 2.30.7, NVSHMEM, Triton 3.8. Also sympy, networkx, jinja2, fsspec, filelock, typing-extensions and setuptools. Source builds use MKL or oneDNN on CPU and need cuDNN 9.0+ for CUDA. |
| **Minimum toolchain** | Python 3.10+. Source build: a compiler with full C++20 support (GCC 11.3.0+ on Linux) and Visual Studio on Windows. ROCm 4.0+ for AMD builds. |
| **Platforms** | Wheels for CPython 3.10-3.14 (including free-threaded 3.14t) on Linux x86-64 and aarch64 (manylinux_2_28), macOS 14+ arm64 and Windows x86-64. GPU backends: NVIDIA CUDA, AMD ROCm (Linux only), Intel GPU (Linux and Windows). |
| **Thread safety** | Since 1.6, concurrent backward() calls from several threads run in parallel on CPU. With shared parameters, .grad accumulation races and results are non-deterministic (documented). Use torch.autograd.grad to avoid this. GPU work is asynchronous per stream. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the measured training rows: u39kun's 'train' is forward plus backward of a bogus sum loss with no optimizer step, and the two sides are not symmetric. TensorFlow fetches every gradient tensor to the host each step (sess.run(self.grad)). It also builds the graph with phase_train=False, so BatchNorm uses moving statistics and dropout is off, and it uses tf_cnn_benchmarks' ResNet v1 (stride in the 1x1 conv). PyTorch runs torchvision's ResNet with the stride in the 3x3 conv (the v1.5 layout, which NVIDIA puts at about 5% slower) and BatchNorm in training mode. It also computes an input gradient that flows back through .cuda() to a CPU tensor. The effects cut both ways and none was measured, so the 1.34x-1.50x training ratios are not a clean framework comparison.
- Harness flaw in the PyTorch 1.0.0 eval rows: the harness wraps the input in Variable(x, volatile=True). In 1.0.0 that flag only warns 'volatile was removed and now has no effect' (python_legacy_variable.cpp). With no torch.no_grad(), the 2080 Ti eval passes recorded autograd graphs for the parameters. This handicaps PyTorch, so its 41.8 ms against 43.6 ms ResNet-152 eval win is conservative.
- On Ampere and later GPUs, torch.backends.cudnn.allow_tf32 defaults to True, so 'FP32' convolutions run in TF32 unless disabled. Matmul TF32 has defaulted to False since 1.12, with finer fp32_precision controls after 2.9. Match these settings before comparing against another framework.
- GPU ops are asynchronous: timing without torch.cuda.synchronize() measures kernel launch only (the u39kun harness does synchronize). The caching allocator keeps freed memory reserved, so nvidia-smi over-reports usage. Allocation sizes that change every step (for example a varying batch) can fragment memory; expandable_segments, still experimental, addresses this.

## Known shortcomings

- u39kun/deep-learning-benchmark harness is asymmetric (the TensorFlow training path fetches gradients to the host, phase_train=False) and dates from 2017-2019 versions; results are mixed: TensorFlow wins vgg16 training on 2080 Ti and V100 and the NGC AMP ResNet-50 row. All frameworks run cuDNN underneath. Filed under numerics-and-science/autodiff-and-ml-kernels.
- Enricher: in u39kun 'train' is forward plus backward of a sum loss with no optimizer step; the TensorFlow side fetches all gradients to the host with BN in inference mode, dropout off and ResNet v1, while PyTorch runs torchvision's v1.5 ResNet (stride on the 3x3) plus an input-gradient copy to CPU, so the 1.34-1.50x train ratios are not a clean comparison; the 1.0.0 eval rows ran with autograd on (volatile=True was a no-op), which handicaps PyTorch and makes the eval win conservative. cuDNN TF32 is on by default on Ampere+; CVE-2025-32434 torch.load RCE up to 2.5.1.

## Caveats and trade-offs

The benchmark is a small community repo (u39kun, not project-authored) with 2017-2019 framework versions (PyTorch 0.3.0 and 1.0.0 against TensorFlow 1.4 to 1.12 graph mode), so it says little about TensorFlow 2.x with XLA or PyTorch 2.x. Both frameworks call cuDNN for the convolutions, so the gaps measure framework overhead and kernel selection, not new kernels. The harness is not symmetric: the TensorFlow training step fetches every gradient tensor back to the host through sess.run(self.grad) (a device-to-host copy the PyTorch loop does not do) and builds the graph with phase_train=False, while the PyTorch loop also computes a gradient for the input image (requires_grad=True) and enables cudnn.benchmark autotuning; the size of these effects was not measured. The win is mixed: TensorFlow 1.12 is faster on vgg16 training on the 2080 Ti (90.8 vs 95.5 ms FP32, 58.6 vs 68.1 ms FP16); on the V100, TensorFlow 1.5.0 beats PyTorch 0.3.0 on vgg16 (eval 24.0 vs 26.2 ms, train 71.7 vs 83.5 ms) while PyTorch wins resnet152 train (136.5 vs 199.8 ms); on the 1080 Ti vgg16 train is 131.3 (TensorFlow) vs 131.9 ms; eval times are mostly within about 4% (Titan V FP32 vgg16 eval 31.3 vs 31.8 ms). Results are batch size 16 only, synthetic inputs, 20 timed iterations after 20 warm-ups. A second independent source, Oneflow-Inc/DLPerf report v1.0 (Oct 2020, 4x8 V100 GPUs, ResNet-50 v1.5 FP32, bsz 128), has PyTorch 1.6.0 10021.29 img/s vs TensorFlow 2.3 9418.44 (1.06x, derived from page data) and NGC PyTorch 10917.09 vs NGC TensorFlow 1.x 9514.64, but with AMP NGC PyTorch 22551.16 loses to NGC TensorFlow 1.x both with XLA (29171.69) and without (24734.22), and on BERT-base NGC TensorFlow wins the FP32 bsz-max row (3089.74 vs 3039.3) and the AMP bsz-64 row with XLA (9409.2 vs 9331.72); that report was read at https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/reports/dlperf_benchmark_test_report_v1.md. The PyTorch NeurIPS 2019 paper table (MXNet 218, PyTorch 212, TensorFlow 200 img/s ResNet-50, seen only as a search snippet) was not readable because arXiv and NeurIPS are blocked.

Eager-mode Python front end over a C++/CUDA core (ATen, autograd); needs GPU memory and a CUDA or ROCm stack for the GPU speedups.

## Maintenance

Very active (last commit 2026-10-07, release 2.14.1 on 2026-09-30, 103.8k stars, 5k+ open issues). The repo carries a BSD-style license, and the PyPI wheel lists a composite licence for bundled code. It is the safe default, but the catalogued speed evidence is 2017-2020 era and asymmetric.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent community measurement with public harness code (u39kun/deep-learning-benchmark benchmark.py, frameworks/pytorch/models.py, frameworks/tensorflow/models.py) and stated GPUs, CUDA and cuDNN versions; prebuilt NGC images, no host CPU model and no build flags, so not A. Corroborated by the independent DLPerf v1.0 report.
- **Verifier notes:** All claimed numbers match the u39kun README. Metadata checked: BSD-3-Clause, 103.8k stars, last commit 2026-10-07; the u39kun repo has 427 stars and no license. Shortcomings for the orchestrator: old framework versions, mixed results (TensorFlow wins vgg16 train on 2080 Ti and V100, and AMP ResNet-50 in DLPerf), asymmetric harness (TensorFlow train fetches gradients to host, BN in inference mode), cuDNN under both frameworks. TensorFlow is not in the autodiff-and-ml-kernels baseline list, so baseline_in_list is false.
- **Fields the verifier corrected:** `baseline_in_list`, `caveats`
- **Shortcomings recorded by:** u39kun deep-learning-benchmark (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/benchmark.py>
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/frameworks/tensorflow/models.py>
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/frameworks/pytorch/models.py>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/reports/dlperf_benchmark_test_report_v1.md>
  - <https://github.com/pytorch/pytorch>
  - <https://github.com/pytorch/pytorch/commits/main.atom>
  - <https://github.com/u39kun/deep-learning-benchmark>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/benchmark.py>
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/frameworks/pytorch/models.py>
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/frameworks/tensorflow/models.py>
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/frameworks/tensorflow/tf_models/resnet_model.py>
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/frameworks/tensorflow/tf_models/convnet_builder.py>
  - <https://raw.githubusercontent.com/u39kun/deep-learning-benchmark/HEAD/frameworks/tensorflow/tf_models/vgg_model.py>
  - <https://raw.githubusercontent.com/pytorch/vision/v0.2.0/torchvision/models/resnet.py>
  - <https://raw.githubusercontent.com/pytorch/pytorch/v1.0.0/torch/csrc/autograd/python_legacy_variable.cpp>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/reports/dlperf_benchmark_test_report_v1.md>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/e470c2150abf4179f873cabad23945bbc920cc5f/MxNet/Classification/RN50v1.5/README.md>
  - <https://github.com/pytorch/pytorch>
  - <https://raw.githubusercontent.com/pytorch/pytorch/HEAD/README.md>
  - <https://raw.githubusercontent.com/pytorch/pytorch/HEAD/docs/source/notes/autograd.md>
  - <https://raw.githubusercontent.com/pytorch/pytorch/HEAD/docs/source/notes/cuda.md>
  - <https://pypi.org/pypi/torch/json>
  - WebSearch: CVE-2025-32434 torch.load weights_only (snippets of wiz.io, sentinelone.com, osv.dev and cvelogic.com; pages not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/pytorch/pytorch`) · [data/wave12/enrich/raw/github_com_pytorch_pytorch.json](../../../data/wave12/enrich/raw/github_com_pytorch_pytorch.json) (enrichment confidence 0.75)

</details>
