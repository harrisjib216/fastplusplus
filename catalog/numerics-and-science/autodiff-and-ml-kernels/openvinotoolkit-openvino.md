# OpenVINO (CPU inference runtime)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Intel's open-source inference runtime; on x86 CPUs it ran ResNet-50 about 2x faster than TFLite+XNNPACK, but did not win on MobileNet V2.

| | |
|---|---|
| **Beats** | TensorFlow Lite with the XNNPACK delegate (XNNPACK) |
| **Claimed result** | Single thread (the first table; the scripts pass --nthreads 1 / --num_threads=1): ResNet 50 OpenVINO latency-optimized 62.55 ms vs TFLite+XNNPACK 118.3 ms (about 1.9x, derived from page data); MobileNet V2 11.14 vs 11.48 ms (tie). 8 threads: ResNet 50 16.70 vs 32.8 ms (about 2.0x, derived from page data); MobileNet V2 3.56 vs 3.16 ms (XNNPACK faster). OpenVINO throughput-optimized mode: MobileNet V2 382.44 FPS (at 10.40 ms latency) vs 316.46 FPS for XNNPACK; ResNet 50 67.73 vs 30.49 FPS. |
| **Workload** | MobileNet V2 and ResNet 50 single-image inference latency/throughput on an 8-vCPU Google Cloud Ubuntu 16.04 VM, TFLite+XNNPACK vs OpenVINO. |
| **Metric** | latency |
| **Hardware** | Google Cloud VM, 8 vCPUs (CPU model not stated), Ubuntu 16.04 LTS |
| **Compiler and flags** | TFLite benchmark_model built from TensorFlow master with 'bazel build -c opt' (Bazel 3.0.0; compiler not stated); OpenVINO 2020.3.194 prebuilt apt runtime with benchmark_app built by build_samples.sh; no compiler versions or flags stated |
| **Adoption** | 10.9k stars; Intel's mainstream inference toolkit |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/openvinotoolkit/openvino) · [benchmark](https://github.com/yaysummeriscoming/xnnpack_benchmarks) |

## Verdict

A small third-party harness (yaysummeriscoming/xnnpack_benchmarks; 8-vCPU Google Cloud VM, CPU model not stated, Ubuntu 16.04, OpenVINO 2020.3.194 apt packages vs TFLite built from TensorFlow master with Bazel 3.0.0) measured batch-1 ResNet-50 at 62.55 ms vs 118.3 ms single-threaded and 16.70 vs 32.8 ms with 8 threads (about 1.9x and 2.0x, derived from page data). MobileNet V2 tied at 1 thread and lost at 8 threads; throughput mode reached 382.44 vs 316.46 FPS (MobileNet V2) and 67.73 vs 30.49 FPS (ResNet-50). No compiler flags or CPU model were stated, and the source is first-party-level evidence (tier C).

## Use it when

- Batch-1 latency for mid-size CNNs such as ResNet-50 on Intel x86 CPUs, where the benchmark shows about 1.9x (1 thread) and 2.0x (8 threads) lower latency than TFLite+XNNPACK.
- Throughput serving of many independent requests on multi-core Xeons with the THROUGHPUT hint or ov::num_streams, letting the plugin pin streams to cores and NUMA nodes.
- INT8-quantized or bf16 models on recent Xeons (AMX) where the plugin's FakeQuantize fusion and automatic half precision apply.
- Teams that want one C++/Python runtime across Intel CPU, integrated or discrete Intel GPU and NPU, fed by models from several training frameworks.
- Hybrid Intel client CPUs (P-cores plus E-cores), where the plugin decides which core types each hint uses.

## Skip it when

- Small mobile-style networks such as MobileNet V2: TFLite+XNNPACK was faster at 8 threads (3.16 vs 3.56 ms) and tied single-threaded (11.48 vs 11.14 ms).
- x86 CPUs without AVX2: the 2026 release notes state the CPU plugin now requires AVX2 and SSE-only CPUs are no longer supported, although the repo's system-requirements page still lists SSE4.2 Atom parts.
- Arm deployments of quantized models: the docs say Arm executes them in simulation mode, entirely in floating point; CPU inference on Windows ARM64 is not supported.
- Size-constrained embedded builds: the source tree pulls in dozens of submodules (frontends, protobuf, ONNX, OpenCL, level-zero), so expect to use the selective-build option to trim it.
- Workloads that need bit-identical f32 results on AMX or Arm fp16 hardware unless you pin ov::hint::inference_precision to f32.

## How it is fast

The CPU plugin lowers the graph onto its own fork of oneDNN, whose kernels are JIT-generated with Xbyak for the host ISA (AVX2, AVX-512, AMX), and also vendors MLAS and LIBXSMM, plus Arm Compute Library and KleidiAI for Arm. Graph passes fuse convolution with activations, ScaleShift/PReLU and FakeQuantize, FullyConnected with activations, and convolution with a following depthwise convolution, which cuts memory round-trips. On hardware with native bf16/f16 it switches inference precision to half automatically (AMX on Xeon, armv8.2-a+fp16 on Arm). Throughput mode runs several 'streams', each with its own host thread pinned to a NUMA-aligned group of cores, so independent requests run in parallel.

## Compared with alternatives

Pick OpenVINO over MNN for whole-model inference on Intel x86 servers and desktops (AMX, INT8, multi-stream throughput, Intel GPU/NPU offload); MNN's own paper targets mobile CPUs, where it beats TFLite and NCNN. Over LIBXSMM or the oneDNN Graph Compiler, pick it when you want a complete runtime rather than kernels; OpenVINO's CPU plugin already vendors LIBXSMM and a oneDNN fork.

## Integration

| | |
|---|---|
| **Form** | shared lib (OpenVINO Runtime core plus per-device plugin libraries); also pip, conda-forge, Homebrew and npm packages |
| **Dependencies** | bundled as git submodules: openvinotoolkit/oneDNN fork, Xbyak, MLAS, LIBXSMM, Arm Compute Library, KleidiAI, pugixml, zlib, protobuf, ONNX, flatbuffers, snappy, OpenCL and level-zero (for GPU/NPU), telemetry |
| **Minimum toolchain** | C++17, CMake 3.26+, GCC 7.5+ on Linux (build docs); Python 3.9-3.12 for the Python API |
| **Platforms** | x86-64 (AVX2 minimum for the CPU plugin in 2026 releases), Arm armv7a and arm64-v8a, Apple silicon; Windows 10/11, Ubuntu 22.04-26.04, RHEL 8/9, macOS 12.6+; Intel GPU and NPU via separate plugins |
| **Thread safety** | Partly documented: concurrency comes from multiple infer requests mapped onto streams, each with its own host thread, and the async wait methods are documented as thread-safe; thread safety of other calls is not covered in the pages read |
| **Drop-in for the baseline** | partial — OpenVINO reads .tflite models directly but is not a TFLite delegate; you switch to the OpenVINO API (or ONNX Runtime's OpenVINO Execution Provider) instead of keeping TFLite+XNNPACK |

## Gotchas

- On CPUs with native bf16/f16 the plugin silently uses half precision instead of f32; the docs warn accuracy can differ (notably for LLMs) and say to set ov::hint::inference_precision to f32 or use the accuracy execution mode.
- The README says OpenVINO collects performance and usage telemetry, partly via Google Analytics 4; opt out with `opt_in_out --opt_out`.
- The benchmark's 'throughput optimized' rows come from benchmark_app -api async (several streams) and trade per-image latency for FPS (MobileNet V2: 10.40 ms latency at 382 FPS), while the TFLite rows ran one inference at a time, so compare like-for-like modes.
- The benchmark used OpenVINO 2020.3 with Caffe models converted to FP32 IR, while TFLite+XNNPACK ran Keras-built models with padding layers and the global-average-pool mean removed, so the two engines did not run identical graphs.

## Known shortcomings

- Source is a 1-star personal harness; engines ran different models (Caffe OMZ vs modified Keras with random weights); CPU model and flags unstated; first table is single-thread; loses MobileNet V2 at 8 threads.
- Evidence is from 2020.3 with mismatched model graphs; 'throughput' rows are multi-stream async vs single-stream TFLite; automatic bf16/f16 on AMX/Arm changes f32 results; telemetry on by default (GA4); 2026 releases require AVX2.

## Caveats and trade-offs

The benchmark is a small personal repository (1 star, 4 commits, GPL-3.0, undated; OpenVINO 2020.3.194 and TensorFlow master built with Bazel 3.0.0, i.e. about 2020) with an unstated CPU model, so it falls short of tier A and is not an established suite. The engines did not run the same model files: OpenVINO used Open Model Zoo Caffe MobileNet V2 / ResNet-50 converted to FP32 IR, while TFLite+XNNPACK used Keras-built models modified for XNNPACK (explicit padding layers and the global-average-pool mean op removed, weights=None). OpenVINO wins on ResNet 50 but ties at 1 thread and loses at 8 threads on MobileNet V2 latency. A separate user report (XNNPACK issue 1803, Aug 2021, EC2 T2.Large, MobileNet V1 and AlexNet) says OpenVINO took 50% of XNNPACK's latency, but it got no maintainer reply and is anecdotal.

Large toolkit (model converters, plugins for CPU/GPU/NPU) rather than a small kernel library; not a drop-in replacement for XNNPACK kernels inside TFLite.

## Maintenance

Actively maintained (last commit 2026-10-01, release 2026.3 on 4 August 2026, about 10.9k stars, Apache-2.0); the comparison is from the 2020.3 release, so current OpenVINO and XNNPACK may differ in either direction.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The only numbers come from yaysummeriscoming/xnnpack_benchmarks, a 1-star, 4-commit personal harness (not a well-known independent suite, no paper); its scripts are public but the CPU model, compiler and flags are not stated and the two engines ran different model files, so it falls short of A and does not qualify for B (precedent: small personal suites tiered C).
- **Verifier notes:** All numbers match the benchmark README; the 'thread count not labelled' first table is single-threaded per run_benchmarks_openvino.sh and run_benchmarks_xnnpack.sh. Downgraded B to C because the source is a 1-star personal harness with mismatched model inputs. Metadata checked: Apache-2.0, 10.9k stars, last commit 2026-10-01.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/yaysummeriscoming/xnnpack_benchmarks/HEAD/README.md>
  - <https://github.com/yaysummeriscoming/xnnpack_benchmarks>
  - <https://raw.githubusercontent.com/yaysummeriscoming/xnnpack_benchmarks/HEAD/run_benchmarks_openvino.sh>
  - <https://raw.githubusercontent.com/yaysummeriscoming/xnnpack_benchmarks/HEAD/run_benchmarks_xnnpack.sh>
  - <https://raw.githubusercontent.com/yaysummeriscoming/xnnpack_benchmarks/HEAD/main.py>
  - <https://github.com/google/XNNPACK/issues/1803>
  - <https://github.com/openvinotoolkit/openvino>
  - <https://github.com/openvinotoolkit/openvino/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/README.md>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/docs/dev/build.md>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/docs/dev/build_linux.md>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/cmake/developer_package/compile_flags/os_flags.cmake>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/src/plugins/intel_cpu/README.md>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/src/plugins/intel_cpu/CMakeLists.txt>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/src/plugins/intel_cpu/docs/internal_cpu_plugin_optimization.md>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/src/plugins/intel_cpu/docs/fake_quantize.md>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/docs/articles_en/about-openvino/release-notes-openvino/system-requirements.rst>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/docs/articles_en/about-openvino/release-notes-openvino.rst>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/docs/articles_en/openvino-workflow/running-inference/inference-devices-and-modes/cpu-device.rst>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/docs/articles_en/openvino-workflow/running-inference/inference-devices-and-modes/cpu-device/performance-hint-and-thread-scheduling.rst>
  - <https://raw.githubusercontent.com/openvinotoolkit/openvino/HEAD/docs/articles_en/openvino-workflow/running-inference/inference-request.rst>
  - <https://github.com/openvinotoolkit/openvino>
  - <https://github.com/openvinotoolkit/openvino/security>
  - <https://github.com/openvinotoolkit/openvino/issues?q=is%3Aissue+is%3Aopen+label%3A%22category%3A+CPU%22+label%3Abug+performance>
  - <https://raw.githubusercontent.com/yaysummeriscoming/xnnpack_benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/yaysummeriscoming/xnnpack_benchmarks/HEAD/run_benchmarks_openvino.sh>
  - <https://raw.githubusercontent.com/yaysummeriscoming/xnnpack_benchmarks/HEAD/run_benchmarks_xnnpack.sh>
  - <https://raw.githubusercontent.com/yaysummeriscoming/xnnpack_benchmarks/HEAD/main.py>
  - WebSearch: OpenVINO CPU plugin system requirements SSE4.2 AVX2 ARM64 performance hint (snippets; docs.openvino.ai egress-blocked)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/openvinotoolkit/openvino`) · [data/wave8/enrich/raw/github_com_openvinotoolkit_openvino.json](../../../data/wave8/enrich/raw/github_com_openvinotoolkit_openvino.json) (enrichment confidence 0.8)

</details>
