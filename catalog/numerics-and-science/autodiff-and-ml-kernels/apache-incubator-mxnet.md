# MXNet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Apache MXNet: archived C++ deep learning framework; 2020 ResNet-50 runs on V100 had it slightly ahead of PyTorch and TensorFlow.

| | |
|---|---|
| **Beats** | TensorFlow and PyTorch (TensorFlow 2.3 and PyTorch 1.6.0 from framework examples; NGC TensorFlow 1.15.2 and NGC PyTorch 1.5.0a0 containers) |
| **Claimed result** | ResNet-50 v1.5 FP32 bsz 128, 1 GPU: upstream MXNet 1.6.0 (gluon-cv) 384.19 img/s vs PyTorch 1.6.0 348.62 and TensorFlow 2.3 321.80 (1.10x and 1.19x, derived from page data); NVIDIA NGC MXNet 392.24 vs NGC PyTorch 367.29 and NGC TensorFlow 1.15 362.44. 32 GPUs FP32: NGC MXNet 11331.93 vs NGC PyTorch 10917.09 (1.04x) and NGC TensorFlow 1.x 9514.64 (1.19x), derived from page data; upstream MXNet 9579.74 is behind PyTorch 10021.29 and only 1.02x over TensorFlow 2.3 9418.44. AMP bsz 256, 32 GPUs: NGC MXNet 30713.68 vs NGC TensorFlow 1.x with XLA 29171.69 and NGC PyTorch 22551.16, but upstream MXNet 10565.55 is far behind TensorFlow 2.3 19314.31. BERT-base FP32 bsz max, 32 GPUs: MXNet without clip_by_global_norm (bsz 64) 4340.89 sentences/s vs NGC TensorFlow 1.x 3089.74 and NGC PyTorch 3039.3 (both bsz 48, with gradient clipping); the TensorFlow 2.3 figure 2244.38 (bsz 64) is in the DLPerf README summary table, not in the report. |
| **Workload** | OneFlow DLPerf report v1.0 (Oct 2020): ResNet-50 v1.5 training throughput in images/s, FP32 batch size 128 per GPU, 1 to 32 Tesla V100 GPUs; also BERT-base pretraining sentences/s. |
| **Metric** | throughput |
| **Hardware** | 4 nodes, each 8x Tesla V100-SXM2-16GB, Intel Xeon Gold 5118 @ 2.30GHz, 384 GB RAM, InfiniBand 100 Gb/s, Ubuntu 16.04.4 |
| **Compiler and flags** | Prebuilt framework builds, no compile flags stated: NGC 20.03 containers (nvcr.io/nvidia/mxnet:20.03-py3 with MXNet 1.6.0, DALI and Horovod; tensorflow:20.03-tf1-py3 with 1.15.2; pytorch:20.03-py3 with 1.5.0a0), CUDA 10.2 and driver 440.33.01; upstream rows use MXNet 1.6.0 with gluon-cv, TensorFlow 2.3.0 and PyTorch 1.6.0 examples. |
| **Adoption** | 20.8k stars |
| **Last commit** | 2023-01-26 |
| **Links** | [repository](https://github.com/apache/mxnet) · [benchmark](https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/reports/dlperf_benchmark_test_report_v1.md) |

## Verdict

OneFlow's DLPerf v1.0 (Oct 2020) measured ResNet-50 training throughput on 4 nodes of 8x V100-SXM2-16GB (Xeon Gold 5118, CUDA 10.2, cuDNN 7.6.5). The median of 5 to 7 runs, iterations 21-120, was used. Upstream MXNet 1.6.0 with gluon-cv and Horovod did 384.19 img/s on 1 GPU at FP32 bsz 128, against PyTorch 1.6.0 348.62 and TensorFlow 2.3 321.80. Upstream MXNet trailed PyTorch at 8 and 32 GPUs. NVIDIA's NGC MXNet 20.03 container led NGC PyTorch and TensorFlow 1.x at every GPU count in FP32 and fp16. All frameworks use the same cuDNN and cuBLAS kernels, so the gaps measure framework overhead, input pipeline and communication.

## Use it when

- Maintaining or reproducing existing MXNet/Gluon code (GluonCV, GluonNLP, 2017-2022 papers, older AWS pipelines) when a port to another framework is not worth it.
- Data-parallel CNN training on V100-era GPUs with the NGC MXNet container, DALI and Horovod. DLPerf measured NGC MXNet at 11331.93 img/s FP32 and 30713.68 img/s fp16 on 32 V100s, ahead of NGC PyTorch and NGC TensorFlow 1.x.
- Single-GPU FP32 ResNet-50 training on V100 with upstream 1.6.0 and gluon-cv: 384.19 img/s against 348.62 for PyTorch 1.6.0 and 321.80 for TensorFlow 2.3.
- Serving an existing MXNet model from a non-Python language binding (Scala, Clojure, Perl, R, Julia, C API) on CPU (x86-64 or aarch64 wheels) or on CUDA 11.x GPUs.

## Skip it when

- Any new project. The repository was archived (read-only) on 2023-11-17, the project was retired to the Apache Attic, the last release is 1.9.1 (May 2022), and fixes are no longer made.
- Current GPUs and toolchains. The newest prebuilt GPU wheel is mxnet-cu117 1.9.1 (CUDA 11.7, x86-64 only). There are no CUDA 12 wheels, and the 1.9.1 wheel pins numpy&lt;2.0.
- Mixed-precision training on the upstream gluon-cv path. On 32 V100s DLPerf measured 10565.55 img/s, against 19314.31 for TensorFlow 2.3 and 22551.16 for NGC PyTorch. At 8 GPUs it scaled only 3.49x over 1 GPU.
- Multi-threaded inference through Gluon. CachedOp and the graph executor are documented as not thread safe. The thread-safe CachedOp C API supports only a tested model list, one model per process, dense storage and no dynamic shapes.
- Large-scale BERT or transformer work. DLPerf's MXNet BERT rows ran without gradient clipping and still trailed OneFlow run the same way. Modern attention kernels (FlashAttention-class) and compiler stacks are not integrated.

## How it is fast

Every operator is pushed to an asynchronous dependency engine (ThreadedEnginePerDevice by default). The engine orders work by read/write dependencies on variables, so compute, host-device copies and gradient communication overlap. Hybridized graphs get memory planning, bulk execution of up to MXNET_EXEC_BULK_EXEC_MAX_NODE_TRAIN nodes per engine op to close kernel-launch gaps, and runtime-compiled pointwise fusion (MXNET_USE_FUSION, Gluon only with static_alloc=True). Optimizer updates can be aggregated across many weights per call (MXNET_OPTIMIZER_AGGREGATION_SIZE). Convolutions and GEMMs come from cuDNN (autotuned by default) and cuBLAS, or from oneDNN on CPU. The fastest DLPerf rows ran NVIDIA's NGC build and DeepLearningExamples script, which added DALI GPU decoding, Horovod with a 64 MB fusion buffer and tuned engine variables. Its fp16 runs also used NHWC layouts with fused BatchNorm-ReLU and BatchNorm-add-ReLU kernels.

## Compared with alternatives

Pick MXNet over PyTorch only when the code or model already exists in MXNet, or for V100-era CNN training in NVIDIA's NGC MXNet container. Upstream PyTorch matched or beat upstream MXNet from 8 GPUs up in DLPerf, and PyTorch is maintained. For a C++-first training framework, look at Flashlight. For C++ inference of an exported model, OpenVINO or CTranslate2 are maintained alternatives.

## Integration

| | |
|---|---|
| **Form** | shared lib (libmxnet.so) behind a C API, shipped as pip wheels (mxnet, mxnet-cuXX); optional C++ package (USE_CPP_PACKAGE, off by default) |
| **Dependencies** | GPU builds: CUDA, cuDNN, optionally NCCL and cuTENSOR. CPU: a BLAS (OpenBLAS or MKL), oneDNN, OpenMP, optionally OpenCV. Python wheel 1.9.1: numpy (&gt;1.16.0,&lt;2.0.0), requests, graphviz (&lt;0.9.0). Horovod or BytePS for multi-node training. |
| **Minimum toolchain** | v1.x branch (1.9.1 releases): CMake 3.13 and C++11 (C++14 in some configurations). master branch (unreleased 2.0): C++17, GCC 7 or newer, CMake 3.13, CUDA C++14. |
| **Platforms** | PyPI wheels: Linux x86-64 and aarch64 (1.9.x), macOS x86-64 CPU, Windows x86-64 up to 1.7.0.post2. GPU wheels are NVIDIA CUDA only, up to CUDA 11.7, x86-64. |
| **Thread safety** | The dependency engine is thread safe (except WaitToRead in a spawned thread). The graph executor and Gluon CachedOp are not. A thread-safe CachedOp (MXCreateCachedOp with thread_safe=true) exists for inference with the documented limitations. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the exact script behind the upstream MXNet ResNet-50 rows is not published. At the pinned gluon-cv commit f9a8a284b8, train_horovod.py has its per-batch 'Speed: ... samples/sec' log line commented out and logs 'Epoch[0] Batch[N] Loss[...]' lines instead. DLPerf's extract_mxnet_logs.py looks for 'Speed:' on every 'Epoch[0] Batch[' line (IndexError on the Loss line) and needs exactly 120 such lines. DLPerf's runner.sh, however, runs a full epoch with no 120-iteration stop, so OneFlow used a locally modified script that is not in Oneflow-Inc/DLPerf.
- The upstream rows labelled AMP are pure fp16, not AMP: gluon-cv casts the whole net with net.cast('float16') and uses multi-precision NAG. The data path is a CPU gluon DataLoader with Python augmentation (8 decode workers per GPU process on a 2x12-core Xeon Gold 5118 node). The 3.49x 8-GPU scaling points to an input-bound script rather than slow framework code, but DLPerf did not measure the cause.
- Upstream and NGC MXNet are not the same configuration. gluon-cv calls hybridize() without static_alloc, so Gluon pointwise fusion is off. The NGC run sets tuned engine and Horovod variables, uses DALI GPU decoding (DLPerf patched dali.py to run it in the 20.03 container), and for fp16 uses NHWC with fused BatchNorm kernels. Treat 'MXNet beats PyTorch at 32 GPUs' as an NVIDIA-container result.
- The default branch (master) is the never-released 2.0 line (2.0.0b1 on PyPI, March 2022), with NumPy-style mx.np semantics. Stable 1.x releases come from the v1.x branch, and open issue #20675 reports MXNet 2.0 up to 10x slower than 1.x on Windows.

## Known shortcomings

- DLPerf is run by OneFlow, a competitor; MXNet wins only upstream at 1 GPU or inside the NVIDIA NGC container, and upstream AMP runs at about half the speed of TF 2.3 and NGC PyTorch (10565.55 vs 19314.31/22551.16 img/s). The BERT row is unfair (no clip_by_global_norm, batch 64 vs 48). All frameworks run cuDNN underneath. Archived 2023-11-17; repo renamed apache/mxnet. Filed under numerics-and-science/autodiff-and-ml-kernels.
- Enricher: the script behind the upstream MXNet rows is unpublished (gluon-cv f9a8a284b8 train_horovod.py has the per-batch Speed log commented out and DLPerf's extract_mxnet_logs.py would fail on its output, so OneFlow used a modified script); the upstream 'AMP' rows are pure fp16 net.cast with a CPU DataLoader and 3.49x 8-GPU scaling, likely input-bound; the wins come only via the NVIDIA NGC container (DALI, NHWC, fused BN). Newest wheel mxnet-cu117 1.9.1 with a numpy&lt;2 pin.

## Caveats and trade-offs

The benchmark is run by OneFlow, a competing framework, from public scripts in Oneflow-Inc/DLPerf; OneFlow beats MXNet in every row quoted. All frameworks call cuDNN and cuBLAS for the convolutions and GEMMs, so the gaps measure framework overhead, input pipelines (NGC rows use DALI) and distributed communication, not kernels. The MXNet margin is small and not consistent: upstream MXNet 1.6.0 gluon-cv is slower than PyTorch 1.6.0 on 8 GPUs (2556.03 vs 2632.93 img/s) and on 32 GPUs (9579.74 vs 10021.29), and beats TensorFlow 2.3 by only 1.02x there (9418.44). With AMP, upstream MXNet is roughly half the speed of TensorFlow 2.3 and NGC PyTorch (10565.55 vs 19314.31 and 22551.16 img/s on 32 GPUs; 2908.88 vs 6898.00 on 8 GPUs). The large NGC MXNet figures come from NVIDIA's tuned DeepLearningExamples container with DALI and Horovod, not upstream MXNet. The BERT rows are not like-for-like: MXNet's gluon-nlp script has no clip_by_global_norm, which the report says raises throughput and may lower accuracy, and it ran at bsz 64 against bsz 48 for the NGC baselines; OneFlow run the same way (W/O clip) is faster than MXNet. The DLPerf README summary shows NGC MXNet 32-GPU FP32 as 11233.92 while the report shows 11331.93. Versions are from 2020 (TensorFlow 2.3, PyTorch 1.6), so current TensorFlow and PyTorch 2.x numbers have moved. An older NeurIPS 2019 PyTorch paper table (MXNet 218, PyTorch 212, TensorFlow 200 img/s, seen only as a search snippet; arXiv and NeurIPS blocked) points the same way. The repository was renamed apache/mxnet and archived (read-only) on 2023-11-17; Apache MXNet was retired to the Attic.

Archived on GitHub 2023-11-17 (read-only); bindings for Python, R, Julia, Scala, Go, JavaScript and more; hybridization between imperative and symbolic execution. Benefits shown depend on NVIDIA's tuned NGC container (DALI, Horovod).

## Maintenance

Abandoned: last commit 2023-01-26, last release 1.9.1 (May 2022), repository archived 2023-11-17 and project retired to the Apache Attic (retired September 2023, move completed February 2024 according to a search snippet of attic.apache.org). Apache-2.0 and usable for legacy code, but with no CUDA 12 or NumPy 2 support and no further fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party measurement: OneFlow's DLPerf report v1.0 runs MXNet, TensorFlow and PyTorch from public per-framework scripts (Oneflow-Inc/DLPerf MxNet/, TensorFlow/, PyTorch/, NVIDIADeepLearningExamples/) on stated hardware (Xeon Gold 5118, 4x8 V100-SXM2-16GB); prebuilt containers and wheels with no compiler or flags, so not A.
- **Verifier notes:** Numbers verified on the report; last commit 2023-01-26 confirmed from the master commit feed, 20.8k stars, Apache-2.0; TensorFlow 2.x BERT 2244.38 exists only in the DLPerf README, and the BERT comparison mixes an unclipped optimizer and larger batch for MXNet. Shortcomings for the orchestrator: framework-level benchmark run by a competitor, cuDNN under every framework, MXNet wins only at 1 GPU upstream or with NVIDIA's NGC container, upstream MXNet loses badly with AMP, project archived. repo_url apache/incubator-mxnet redirects to apache/mxnet (consider a repo_url override); TensorFlow and PyTorch are not in the autodiff-and-ml-kernels baseline list, so baseline_in_list is false.
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** OneFlow DLPerf (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/reports/dlperf_benchmark_test_report_v1.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/README.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/TensorFlow/bert/README.md>
  - <https://github.com/apache/incubator-mxnet>
  - <https://github.com/apache/mxnet/commits/master.atom>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/reports/dlperf_benchmark_test_report_v1.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/README.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/MxNet/Classification/RN50v1b/README.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/MxNet/Classification/RN50v1b/run_test.sh>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/MxNet/Classification/RN50v1b/runner.sh>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/MxNet/Classification/RN50v1b/extract_mxnet_logs.py>
  - <https://github.com/Oneflow-Inc/DLPerf/tree/master/MxNet/Classification/RN50v1b>
  - <https://github.com/Oneflow-Inc/DLPerf/commits/master/MxNet/Classification/RN50v1b>
  - <https://raw.githubusercontent.com/dmlc/gluon-cv/f9a8a284b8222794bc842453e2bebe5746516048/scripts/classification/imagenet/train_horovod.py>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/NVIDIADeepLearningExamples/MxNet/Classification/RN50v1.5/README.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/HEAD/NVIDIADeepLearningExamples/MxNet/Classification/RN50v1.5/runner.sh>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/e470c2150abf4179f873cabad23945bbc920cc5f/MxNet/Classification/RN50v1.5/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/e470c2150abf4179f873cabad23945bbc920cc5f/MxNet/Classification/RN50v1.5/fit.py>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/e470c2150abf4179f873cabad23945bbc920cc5f/MxNet/Classification/RN50v1.5/dali.py>
  - <https://github.com/apache/mxnet>
  - <https://raw.githubusercontent.com/apache/mxnet/HEAD/README.md>
  - <https://raw.githubusercontent.com/apache/mxnet/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/apache/mxnet/v1.x/CMakeLists.txt>
  - <https://raw.githubusercontent.com/apache/mxnet/HEAD/docs/static_site/src/pages/api/faq/env_var.md>
  - <https://raw.githubusercontent.com/apache/mxnet/HEAD/docs/static_site/src/pages/api/cpp/docs/tutorials/multi_threaded_inference.md>
  - <https://github.com/apache/mxnet/issues?q=is%3Aissue+is%3Aopen+label%3ABug+sort%3Acomments-desc>
  - <https://pypi.org/pypi/mxnet/json>
  - <https://pypi.org/pypi/mxnet-cu112/json>
  - <https://pypi.org/pypi/mxnet-cu117/json>
  - WebSearch: Apache MXNet Attic retirement (snippets of attic.apache.org/projects/mxnet.html and en.wikipedia.org/wiki/Apache_MXNet; pages not opened)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/apache/incubator-mxnet`) · [data/wave12/enrich/raw/github_com_apache_incubator_mxnet.json](../../../data/wave12/enrich/raw/github_com_apache_incubator_mxnet.json) (enrichment confidence 0.72)

</details>
