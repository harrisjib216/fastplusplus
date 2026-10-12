# MNN

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Alibaba's on-device inference/training engine with hand-written ARM/x86 assembly and GPU backends; beat TF-Lite, NCNN, MACE on 2020 phones.

| | |
|---|---|
| **Beats** | TensorFlow Lite, NCNN, MACE, CoreML (MLSys 2020 paper) |
| **Claimed result** | MLSys 2020 paper: 'MNN outperforms other inference engines under almost all settings by about 20%\~40%' (about 30% faster CPU inference on iOS, 34% on Android) on MobileNet-v1, SqueezeNet-v1.1, ResNet-18; README separately claims 'Twice speed increase' for ARM v8.2 FP16 and '2.5 faster to use sdot for ARM v8.2 and VNNI' (vs its own FP32/non-sdot paths) |
| **Workload** | Mobile CNN inference latency (MobileNet-v1, SqueezeNet-v1.1, ResNet-18, 224x224) on phone CPUs and GPUs (OpenCL/Vulkan/OpenGL/Metal). |
| **Metric** | latency |
| **Hardware** | iPhone 8 / iPhone X (Apple A11), Xiaomi MI6 (Snapdragon 835), Huawei Mate 20 (Kirin 980) |
| **Adoption** | 16.0k stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/alibaba/MNN) · [benchmark](https://arxiv.org/abs/2002.12418) |

## Verdict

The MLSys 2020 paper (by the MNN team) ran MobileNet-v1, SqueezeNet-v1.1 and ResNet-18 at 224x224, batch 1, averaged over 10 runs, on iPhone 8/X, Xiaomi MI6 and Huawei Mate 20, and reports MNN about 20-40% faster than CoreML, TF-Lite, NCNN and MACE in almost all settings (4-thread CPU: \~30% on iOS, \~34% on Mate 20); on Metal it is comparable to CoreML. No compiler flags or benchmark harness are given in the paper.

## Use it when

- Shipping CNN or transformer inference inside an Android/iOS app where binary size matters (paper: 400-600 KB added; README: \~800 KB core .so on armv7a)
- Batch-1 mobile CNNs (MobileNet, SqueezeNet, ResNet-class) on ARM CPUs, especially ARMv8.2+ with FP16 or int8 SDOT
- One codebase that must target CPU plus Metal/OpenCL/Vulkan GPUs across a fragmented Android fleet
- Running quantized LLMs or diffusion models on-device through MNN-LLM / MNN-Diffusion
- x86 AVX2/AVX512 servers or desktops that need a light, dependency-free C++ runtime

## Skip it when

- You need an independently benchmarked winner today: the published comparison is first-party, 2020-era phones and engine versions, and omits XNNPACK-backed TFLite, ONNX Runtime and LiteRT
- Your model uses ops outside the converter's coverage (178 TF, 158 ONNX, 163 TorchScript ops listed); unsupported ops mean custom op work
- Datacenter GPU serving at scale: CUDA backend is rated 'A' (works, not deeply optimized) for FP32 and int8; TensorRT or vendor stacks fit better
- Backends rated 'B' in the README table (native CPU without SIMD, NNAPI, QNN FP16) are documented as buggy or unoptimized
- Teams that need English-first support: the README says community discussion is mostly in Chinese (DingTalk groups)

## How it is fast

A 'pre-inference' pass, run once per input shape, scores candidate algorithms and backends (C_total = C_algorithm + C_backend) and picks, for example, sliding-window vs Winograd convolution per layer, then preallocates memory. Kernels are hand-optimized SIMD/assembly on an NC4HW4 blocked layout, with a generic Winograd generator for any kernel size and Strassen matrix multiply for large 1x1 convolutions (7.5-13.5% gain per the paper). On ARMv8.2 it uses FP16 arithmetic and SDOT int8 dot products, and on x86 AVX2/AVX512/VNNI paths.

## Compared with alternatives

Pick MNN when you need a whole deployable runtime for mobile CNNs or LLMs across CPU and mobile GPUs; llamafile tinyBLAS and T-MAC are matmul/low-bit kernels for llama.cpp-style LLM inference on desktop CPUs, and nanoinfer is an educational engine that does not beat ONNX Runtime.

## Integration

| | |
|---|---|
| **Form** | shared lib (default MNN_BUILD_SHARED_LIBS=ON) or static lib; Python wheel |
| **Dependencies** | none at runtime for the core ('no dependencies' per README); converters need protobuf/flatbuffers; GPU backends need the platform's Metal/OpenCL/Vulkan/CUDA |
| **Minimum toolchain** | CMake 3.6+; C++11 by default (C++17/20 for some options such as CUDA transformer fuse) |
| **Platforms** | iOS 8.0+, Android 4.3+, Linux/macOS/Windows, POSIX embedded; ARMv7a/ARMv8 (FP16/SDOT on v8.2, BF16 on v8.6), x86-64 SSE4.1/AVX2/AVX512 |
| **Thread safety** | Global Executor is not thread-safe; create one Module instance per thread and bind an Executor in each thread with ExecutorScope (per mnn-docs Module page) |
| **Drop-in for the baseline** | no |

## Gotchas

- The first run per input shape triggers pre-inference (algorithm selection and memory planning); resizing inputs repeats it, so dynamic shapes cost latency
- Interpreter/Session APIs are marked deprecated in the Python docs; new code should use the Module API
- Security policy supports only the 3.4.x line and lists model-file parsing and converters as in scope; treat untrusted .mnn files as an attack surface
- README speedups for FP16 ('twice') and SDOT/VNNI ('2.5x') compare MNN's own paths, not competitors

## Known shortcomings

- Paper written by MNN's own team; 2020-era phones; never compared against XNNPACK or oneDNN.
- Leaves out XNNPACK-backed TFLite, ONNX Runtime and LiteRT; only 3.4.x gets security support (model-file parsing in scope); global Executor not thread-safe, one Module per thread.

## Caveats and trade-offs

Peer-reviewed but authored by the MNN team (Alibaba); results from 2020-era phones and engine versions. No XNNPACK/oneDNN comparison. README FP16/sdot speedups are vs MNN's own other paths, not vs a competitor.

Full inference framework with its own model format and converters; many backends (Metal/OpenCL/Vulkan/CUDA/Hexagon).

## Maintenance

Very active (3.6.1 released 2026-07-22, commits in late September 2026), Apache-2.0, 16k stars and used in 30+ Alibaba apps; safe to adopt, but the speed claims date from 2020.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded: peer-reviewed MLSys 2020 paper benchmarks MNN against CoreML, TF-Lite, NCNN and MACE on named phones (A11, Snapdragon 835, Kirin 980) and reports \~20-40% wins; no compiler flags/benchmark-code link in the paper, so B not A.
- **Verifier notes:** Tier raised C-&gt;B on the MLSys 2020 paper (read via ar5iv). Metadata confirmed: Apache-2.0, 16.0k stars, last commit 2026-09-30.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/alibaba/MNN>
  - <https://github.com/alibaba/MNN/commits>
  - <https://arxiv.org/abs/2002.12418>
  - <https://arxiv.org/pdf/2002.12418>
  - <https://ar5iv.labs.arxiv.org/html/2002.12418>
- **Sources the enricher read:**
  - <https://github.com/alibaba/MNN>
  - <https://raw.githubusercontent.com/alibaba/MNN/HEAD/README.md>
  - <https://raw.githubusercontent.com/alibaba/MNN/HEAD/CMakeLists.txt>
  - <https://arxiv.org/abs/2002.12418>
  - <https://ar5iv.labs.arxiv.org/html/2002.12418>
  - <https://github.com/alibaba/MNN/security>
  - <https://mnn-docs.readthedocs.io/en/latest/inference/module.html>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/alibaba/mnn`) · [data/wave8/enrich/raw/github_com_alibaba_mnn.json](../../../data/wave8/enrich/raw/github_com_alibaba_mnn.json) (enrichment confidence 0.75)

</details>
