# TensorFlow

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Google's ML framework; with XLA plus mixed precision (NVIDIA's 2020 TF 1.15 build) it out-trained NGC PyTorch on ResNet-50 and BERT-base.

| | |
|---|---|
| **Beats** | PyTorch (NGC PyTorch 1.5.0a0+8f84ded, container nvcr.io/nvidia/pytorch:20.03-py3) |
| **Claimed result** | DLPerf ResNet-50 v1.5 AMP: NGC TensorFlow 1.x with XLA 1198.55 vs NGC PyTorch 802.9 img/s on 1 GPU (1.49x) and 8588.45 vs 6154.66 on 8 GPUs (1.40x); with DLPerf's static-loss-scale PyTorch run the lead is 1.45x/1.33x; NVIDIA READMEs: 1099.55 (1217.90 with XLA) vs 856.52 img/s on 1 V100. |
| **Workload** | Training throughput of ResNet-50 v1.5 (images/sec, automatic mixed precision) and BERT-base pretraining (sentences/sec, AMP) on 1 to 32 Tesla V100-SXM2-16GB GPUs (4 nodes x 8) using NVIDIA DeepLearningExamples scripts; the TensorFlow side is NGC TensorFlow 1.15.2 (nvcr.io/nvidia/tensorflow:20.03-tf1-py3) with XLA, and stock TensorFlow 2.3.0 with tensorflow/models scripts. |
| **Metric** | throughput |
| **Hardware** | 4 nodes, each 8x Tesla V100-SXM2-16GB, Intel Xeon Gold 5118 @ 2.30GHz, 384 GB RAM, InfiniBand 100 Gb/s EDR, Ubuntu 16.04.4 |
| **Compiler and flags** | Not stated (prebuilt NVIDIA NGC containers 20.03 for TensorFlow 1.15.2 and PyTorch 1.5.0a0; TensorFlow 2.3.0 and PyTorch 1.6.0 installed separately); CUDA 10.2, driver 440.33.01; XLA and AMP enabled per run as listed in the report. |
| **Adoption** | 200.9k stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/tensorflow/tensorflow) · [benchmark](https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/reports/dlperf_benchmark_test_report_v1.md) |

## Verdict

OneFlow's DLPerf report (October 2020; 4 nodes x 8 Tesla V100-SXM2-16GB, Xeon Gold 5118, CUDA 10.2, InfiniBand EDR; median of 5-6 runs, 100 steps after 20 warmup) measured NGC TensorFlow 1.15.2 with XLA and AMP at 1198.55 vs 802.9 img/s for NGC PyTorch 1.5.0a0 on ResNet-50 v1.5 with one GPU and 29171.69 vs 22551.16 on 32 GPUs (about 1.49x and 1.29x, derived from page data). On BERT-base AMP at batch 96 the figures were 468.10 vs 462.35 and 11650.0 vs 10349.12 sentences/s (about 1.01x and 1.13x); the data pipelines and loss scaling differed between the two frameworks, and container compiler flags are not stated.

## Use it when

- You already train in TensorFlow/Keras on NVIDIA GPUs and can turn on XLA (jit_compile) and mixed precision: in this suite those two switches are what put TensorFlow ahead.
- CNN training of ResNet-50 class models with AMP on V100-class GPUs and a GPU-side input pipeline (DALI or similar), from 1 GPU to 4 nodes x 8 GPUs.
- BERT-base style pretraining with AMP only if XLA is enabled; then TensorFlow led NGC PyTorch by 1-13% at the largest per-GPU batch (96).
- Deployments that need a C++ runtime and a maintained, Apache-2.0 framework with official wheels for Linux x86-64/aarch64, macOS arm64 and Windows.

## Skip it when

- FP32 training: in the same report PyTorch is faster on ResNet-50 at every scale (NGC PyTorch 10917.09 vs NGC TensorFlow 9514.64 img/s on 32 GPUs) and on BERT-base at batch 32.
- Transformer training without XLA: NGC TensorFlow BERT-base AMP was about 2.4x slower than NGC PyTorch on one GPU (183.25 vs 444.51 sentences/s), and stock TensorFlow 2.3.0 BERT AMP was about 2.5x slower on 32 GPUs (4168.79 vs 10349.12).
- Choosing on raw ResNet-50 throughput alone: NGC MXNet (1393.87 vs 1198.55 img/s on one GPU) and OneFlow beat TensorFlow-with-XLA in the same table.
- Expecting the 2020 numbers to carry over: the winning build is TensorFlow 1.15.2 in the NGC 20.03 container; the maintained line is 2.x (2.21.0, March 2026) and stock TF 2.3.0 lost to NGC PyTorch at 16 and 32 GPUs.
- C/C++ embedding from prebuilt binaries: TensorFlow stopped publishing libtensorflow packages in 2.19 (the release notes say to unpack it from the PyPI wheel), otherwise you build with Bazel.

## How it is fast

The lead comes from the XLA JIT compiler (--use_xla), which fuses graph ops into fewer, larger GPU kernels: inside the same suite XLA alone lifts ResNet-50 AMP from 945.18 to 1198.55 img/s on one V100 (about 1.27x) and BERT-base AMP from 183.25 to 422.53 sentences/s (about 2.3x, both derived from page data). Mixed precision comes from NVIDIA's automatic-mixed-precision graph rewrite (--use_tf_amp) with a static loss scale of 128; multi-GPU scaling uses Horovod over NCCL and InfiniBand, and images are decoded on the GPU by DALI (nvJPEG 'mixed' decoder).

## Compared with alternatives

Choose TensorFlow over PyTorch only when you can run it with XLA plus AMP, since the PyTorch entry's FP32 and non-XLA rows go the other way. For raw ResNet-50 throughput in this same suite, MXNet (NGC build) and OneFlow were faster. CNTK beat TensorFlow 1.2 on LSTMs, and Flashlight beat TensorFlow 2.4, so only reach for TensorFlow on speed when its XLA path applies.

## Integration

| | |
|---|---|
| **Form** | pip wheel (Python) or shared library (libtensorflow / libtensorflow_cc) built from source with Bazel |
| **Dependencies** | Bazel 7.7.0 for source builds; hermetic CUDA 12.5.1 and cuDNN 9.10.0 by default for GPU builds (CUDA 13 config available); Horovod, NCCL and DALI were added separately in the benchmarked NGC setup |
| **Minimum toolchain** | C++17 (.bazelrc sets -std=c++17 on all platforms); Python &gt;= 3.10 for TensorFlow 2.21 |
| **Platforms** | Linux x86-64 and aarch64, macOS arm64, Windows x86-64 (PyPI wheels); NVIDIA GPUs via CUDA; the benchmark ran on Tesla V100-SXM2-16GB |
| **Thread safety** | not documented in the pages read |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the ResNet-50 AMP comparison: TensorFlow reads TFRecords through DALI with GPU nvJPEG decoding and GPU resize (NVIDIA data_utils passes dali_cpu=False), while DLPerf's NGC PyTorch script hard-codes --data-backend dali-cpu, so PyTorch decodes JPEGs and runs RandomResizedCrop on the host Xeon Gold 5118 CPUs (NVIDIA's README does recommend dali-cpu for DGX-1).
- Harness flaw: TensorFlow ran AMP with --use_static_loss_scaling --loss_scale=128, PyTorch with --dynamic-loss-scale; DLPerf's own static-loss-scale PyTorch run is 827.86 and 6446.74 img/s on 1 and 8 GPUs, not the reported 802.9 and 6154.66, which cuts TensorFlow's 1.49x and 1.40x leads to about 1.45x and 1.33x. NVIDIA's own READMEs still put TensorFlow 20.03 ahead (AMP 1099.55 img/s, 1217.90 with XLA, vs PyTorch AMP 856.52 img/s on one V100 16GB), so the ordering holds while the margin is inflated.
- Metric mismatch: TensorFlow ResNet-50 throughput is the arithmetic mean of rank 0's per-step imgs_per_sec (extract_tensorflow_logs.py, 100 steps after a 20-step warmup), while PyTorch's comes from elapsed time over the same window (extract_pytorch_logs_time.py); a mean of rates is never below the time-based figure, and DLPerf says the two methods differ slightly. Batch sizes also differ (TensorFlow 224 after OOM at 256 vs PyTorch 256), which works against TensorFlow.
- XLA and the regular kernels can disagree: the 2.22 release notes fix jit_compile=True silently accepting integer inputs for Reciprocal/Inv and segfaulting in non_max_suppression on empty boxes, so validate numerics when enabling XLA.

## Known shortcomings

- Wins only with the NVIDIA NGC build plus XLA and AMP in OneFlow's 2020 suite (ResNet-50 v1.5 AMP 1198.55 vs 802.9 img/s on 1 GPU); PyTorch is faster in FP32, BERT AMP bsz=64 is mixed, and the no-XLA and stock 2.3.0 BERT runs are 1.8-2.5x slower. Opposite claim to the already-listed pytorch/pytorch entry.
- Enricher: in the DLPerf ResNet-50 AMP comparison TensorFlow decodes JPEGs on the GPU (DALI nvJPEG, dali_cpu=False) while the NGC PyTorch script hard-codes --data-backend dali-cpu (CPU decode on a Xeon Gold 5118); loss scaling differs (TF static 128 vs PyTorch dynamic; DLPerf's own static PyTorch run at 827.86/6446.74 img/s cuts the lead from 1.49x/1.40x to 1.45x/1.33x); TF throughput is a mean of per-step rates while PyTorch's is time-based. NVIDIA's own READMEs still show TF ahead (1099.55, 1217.90 with XLA vs 856.52 img/s on 1 V100), so the ordering holds with an inflated margin.
- Domain set to numerics-and-science to match its autodiff-and-ml-kernels category.

## Caveats and trade-offs

Mixed evidence, not a clean win. The suite is run by OneFlow (a competing framework that tops every table) and published in October 2020, so the numbers are six years old. The wins come from NVIDIA's NGC build of TensorFlow 1.15.2 with XLA plus AMP, not the stock tensorflow/tensorflow v2.3.0 tree, and are against NVIDIA's NGC PyTorch examples; XLA itself now lives in openxla/xla. Without XLA, NGC TensorFlow BERT AMP is far slower than NGC PyTorch (183.25 vs 444.51 sentences/s on 1 GPU, 5189.07 vs 9331.72 on 32 GPUs at bsz=64; about 2.4x and 1.8x, derived from page data). Stock TensorFlow 2.3.0 BERT is slower than NGC PyTorch in both precisions (DLPerf README: FP32 2244.38 at bsz=64 vs 3039.3 at bsz=48; AMP 4168.79 at bsz=96 vs 10349.12 at bsz=96 on 32 GPUs, about 2.5x, derived from page data). In FP32 PyTorch is faster almost everywhere: ResNet-50 bsz=128 NGC TensorFlow 362.44/2721.98/5099.42/9514.64 vs NGC PyTorch 367.29/2887.65/5716.79/10917.09 img/s, TensorFlow 2.3.0 9418.44 vs PyTorch 1.6.0 10021.29 on 32 GPUs; BERT FP32 bsz=32 NGC PyTorch leads at every scale, and at bsz=max TensorFlow leads only on 32 GPUs (3089.74 vs 3039.30). The stock PyTorch examples were not run with AMP. The ResNet AMP comparison pits TensorFlow at bsz=224 (OOM at 256) against PyTorch at 256. XLA vs no-XLA gains inside TensorFlow are TensorFlow-vs-TensorFlow and are not counted as a win over PyTorch. PyTorch is also listed (wave 12) with older numbers showing it 1.3-1.5x faster than TensorFlow 1.4-1.12 on other workloads, so the two entries carry opposite claims. Tier B, not A, because compiler and build flags of the containers are not stated and batch sizes differ between some compared rows. Google's own XLA blog post was not opened. [retier] GPU JPEG decode (DALI nvJPEG) for TF vs CPU decode for PyTorch; static vs dynamic loss scaling; different throughput definitions; wins only with the NGC build plus XLA and AMP; PyTorch faster in FP32; 2020 numbers; opposite claim to the pytorch/pytorch entry.

XLA and AMP need extra configuration, and the TensorFlow 1.x XLA run used a smaller per-GPU batch (224) than PyTorch (256) to avoid out-of-memory; TensorFlow 1.x is end-of-life, TensorFlow 2.x is the maintained line.

## Maintenance

Actively maintained under Apache-2.0 (200.9k stars, 2.21.0 released 2026-03-06, 2.22.0rc0 on 2026-09-22), but the benchmarked winner is a 2020 NVIDIA build of TensorFlow 1.15. XLA is developed as OpenXLA and copied into third_party/xla, and tf.lite is moving out to LiteRT.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now C.
- **Tier reason:** Third-party suite (Oneflow-Inc/DLPerf, scripts per framework in the repo, NVIDIA DeepLearningExamples commits pinned, CPU Xeon Gold 5118 and 4x8 V100 stated) lists NGC TensorFlow 1.15.2 and stock TensorFlow 2.3.0 against NGC PyTorch and PyTorch 1.6.0; every quoted figure is in the report tables. Not A because the prebuilt containers' compiler and build flags are not stated and the compared ResNet AMP rows use different batch sizes (TensorFlow 224 after OOM at 256).
- **Retiered** B to C: Lowered B to C: the independent DLPerf numbers come from an asymmetric harness (TensorFlow decodes JPEGs on the GPU through DALI while the PyTorch script is hard-coded to CPU decode; static vs dynamic loss scaling; per-step mean vs time-based throughput), so the margin is not like for like even though NVIDIA's own READMEs keep the ordering.
- **Verifier notes:** All quoted figures are in reports/dlperf_benchmark_test_report_v1.md; corrections add the 16-GPU rows, the mixed BERT AMP bsz=64 table and the much slower no-XLA and stock-2.3.0 BERT rows. Shortcomings to record: win needs NVIDIA NGC build plus XLA plus AMP, PyTorch faster in FP32 and in stock TF 2.3.0 BERT, 2020 numbers from a competing framework's suite, container build flags unstated. Category autodiff-and-ml-kernels is a wave 8 category filed here by the seed backfill.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-99 (wave 12); enricher w12 pair-010; orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/reports/dlperf_benchmark_test_report_v1.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/README.md>
  - <https://github.com/tensorflow/tensorflow>
  - <https://github.com/tensorflow/tensorflow/commits/master>
- **Sources the enricher read:**
  - <https://github.com/tensorflow/tensorflow>
  - <https://github.com/tensorflow/tensorflow/tree/master/third_party/xla>
  - <https://raw.githubusercontent.com/tensorflow/tensorflow/master/README.md>
  - <https://raw.githubusercontent.com/tensorflow/tensorflow/master/RELEASE.md>
  - <https://raw.githubusercontent.com/tensorflow/tensorflow/master/.bazelversion>
  - <https://raw.githubusercontent.com/tensorflow/tensorflow/master/.bazelrc>
  - <https://pypi.org/pypi/tensorflow/json>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/reports/dlperf_benchmark_test_report_v1.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/README.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/NVIDIADeepLearningExamples/TensorFlow/Classification/ConvNets/resnet50v1.5/README.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/NVIDIADeepLearningExamples/TensorFlow/Classification/ConvNets/resnet50v1.5/scripts/single_node_train.sh>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/NVIDIADeepLearningExamples/TensorFlow/Classification/ConvNets/resnet50v1.5/scripts/run_single_node.sh>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/NVIDIADeepLearningExamples/TensorFlow/Classification/ConvNets/resnet50v1.5/extract_tensorflow_logs.py>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/NVIDIADeepLearningExamples/PyTorch/resnet50v1.5/README.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/NVIDIADeepLearningExamples/PyTorch/resnet50v1.5/scripts/single_node_train.sh>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/NVIDIADeepLearningExamples/PyTorch/resnet50v1.5/scripts/run_single_node.sh>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/NVIDIADeepLearningExamples/TensorFlow/LanguageModeling/BERT/README.md>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/NVIDIADeepLearningExamples/TensorFlow/LanguageModeling/BERT/scripts/run_pretraining_adam.sh>
  - <https://raw.githubusercontent.com/Oneflow-Inc/DLPerf/master/NVIDIADeepLearningExamples/PyTorch/BERT/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/fed7ba99cde958fda12c9e81d12b3d7e738e0590/TensorFlow/Classification/ConvNets/utils/hooks/training_hooks.py>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/fed7ba99cde958fda12c9e81d12b3d7e738e0590/TensorFlow/Classification/ConvNets/utils/dali_utils.py>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/fed7ba99cde958fda12c9e81d12b3d7e738e0590/TensorFlow/Classification/ConvNets/utils/data_utils.py>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/fed7ba99cde958fda12c9e81d12b3d7e738e0590/TensorFlow/Classification/ConvNets/utils/cmdline_helper.py>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/fed7ba99cde958fda12c9e81d12b3d7e738e0590/TensorFlow/Classification/ConvNets/runtime/runner.py>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/fed7ba99cde958fda12c9e81d12b3d7e738e0590/TensorFlow/Classification/ConvNets/resnet50v1.5/README.md>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/5cc03caa153faab7a2c3b1b5b5d63663f06ce1b4/PyTorch/Classification/ConvNets/image_classification/dataloaders.py>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/46ff3707e04683e41b79af0f94a74e45f8016786/PyTorch/Classification/ConvNets/image_classification/dataloaders.py>
  - <https://raw.githubusercontent.com/NVIDIA/DeepLearningExamples/5cc03caa153faab7a2c3b1b5b5d63663f06ce1b4/PyTorch/Classification/ConvNets/resnet50v1.5/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/tensorflow/tensorflow`) · [data/wave12/enrich/raw/github_com_tensorflow_tensorflow.json](../../../data/wave12/enrich/raw/github_com_tensorflow_tensorflow.json) (enrichment confidence 0.6)

</details>
