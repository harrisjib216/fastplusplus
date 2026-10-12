# RTNeural

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Real-time-safe C++ inference for small Dense/GRU/LSTM/Conv nets; per-sample calls run 2x-190x faster than ONNX Runtime/libtorch/TFLite.

| | |
|---|---|
| **Beats** | libtorch, ONNX Runtime 1.15.1, TensorFlow Lite 2.14.0 |
| **Claimed result** | Exact values from RTNeural-compare results/bench_\*.txt (real-time factor at 48 kHz, one sample per call, higher is better). LSTM size 4: RTNeural Eigen static 268.3x real time vs ONNX Runtime 1.42x and libtorch 0.375x (about 189x vs ONNX Runtime, derived from page data); size 64: Eigen static 6.46x vs ONNX Runtime 1.13x and libtorch 0.262x (about 5.7x, derived). GRU size 4: xsimd static 338.2x vs ONNX Runtime 1.46x and libtorch 0.370x; size 64: Eigen static 8.67x vs 1.23x and 0.273x. Dense size 4: xsimd static 6164x (STL static 5969x) vs TensorFlow Lite 151.5x, ONNX Runtime 7.51x, libtorch 2.33x (about 41x vs TensorFlow Lite, derived); size 64: Eigen static 76.8x (xsimd static 67.9x) vs TensorFlow Lite 40.7x (about 1.9x, derived), ONNX Runtime 6.84x, libtorch 1.75x. The STL backend at size 64 reaches only 1.01x (LSTM) and 1.37x (GRU) against ONNX Runtime's 1.13x and 1.23x, and 8.69x vs TensorFlow Lite's 40.7x on Dense, so it is slower there. |
| **Workload** | Single-sample real-time-factor (48 kHz audio) of Dense, Conv1D, GRU, LSTM layers and activations at layer sizes 4 to 64, RTNeural compile-time and run-time APIs with Eigen, xsimd and STL backends vs libtorch, ONNX Runtime and TensorFlow Lite. |
| **Metric** | throughput |
| **Hardware** | 2018 Mac Mini, Intel Core i7-8700B @ 3.20 GHz |
| **Compiler and flags** | CMake Release build (run_bench.sh: -DCMAKE_BUILD_TYPE=Release), C++17; compiler and version not stated. Baselines: prebuilt onnxruntime-osx-x86_64 1.15.1 and tensorflowlite_c 2.14.0; libtorch version not stated. |
| **Adoption** | 848 stars; used in many audio plugins (BYOD, Chow Centaur, NeuralNote) |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/jatinchowdhury18/RTNeural) · [benchmark](https://github.com/jatinchowdhury18/RTNeural-compare/blob/main/README.md) |

## Verdict

In the author's RTNeural-compare harness on a 2018 Mac Mini (Intel Core i7-8700B), single layers process 10 s of 48 kHz signal one sample per call: LSTM size 4 runs at 268x real time (Eigen, compile-time API) vs 1.42x for ONNX Runtime 1.15.1 and 0.375x for libtorch, narrowing to 6.46x vs 1.13x and 0.262x at size 64; Dense size 64 is 76.8x vs TensorFlow Lite 2.14 at 40.7x. Release CMake build, compiler unstated; the libtorch loop runs without NoGradGuard/InferenceMode at default threads (ONNX Runtime is pinned to 1 thread), and baselines were timed only in the STL-backend run.

## Use it when

- Neural audio effects and amp/pedal models (GuitarML, AIDA-X, BYOD, NeuralNote-style plugins) that must process one sample or a short block per callback with no allocation.
- Small recurrent or dense networks, roughly 4-64 hidden units, where per-call overhead of a general runtime dominates; the author's logs show 6x-268x real time for LSTM at 48 kHz on one i7-8700B core.
- Architectures known at compile time: use ModelT with the Eigen or xsimd backend for the fastest path.
- Embedded or plugin targets (x86, ARM incl. armv7 and Raspberry Pi per downstream users) where you want a header-style dependency with BSD-3 licensing and no runtime library.

## Skip it when

- Batched or large-model inference: the benchmark gap shrinks fast with layer size (Dense 64: Eigen 76.8x vs TFLite 40.7x real time), and a reported crash with two 512-unit GRUs in the compile-time API (issue #157, open, no reply) suggests large static models are untested.
- Layers outside Dense, Conv1D/Conv2D, GRU, LSTM, BatchNorm1D/2D and the tanh/ReLU/sigmoid/softmax/ELU/PReLU activations: MaxPooling, vanilla RNN, attention/transformers and TCN-style blocks are open requests (#102, #147, #120).
- Training, GPU execution or importing ONNX/TorchScript graphs: inference only, CPU only, JSON weights only.
- The STL backend on anything but tiny layers: at size 64 it falls to 1.01x (LSTM) and 8.69x (Dense) real time, below ONNX Runtime and TFLite in the author's own logs.

## How it is fast

It removes framework overhead rather than out-computing the frameworks: no tensor objects, graph dispatch, threading or allocation per call, just a matrix-vector product per layer on preallocated, aligned buffers. The compile-time API fixes every dimension at compile time (Eigen fixed-size matrices or xsimd arrays), so loops unroll and vectorize. The LSTM, for example, stacks W, U and bias into one [4\*out x (in+out+1)] matrix and does a single GEMV per step, then applies sigmoid/tanh to the gate segments. Backends: Eigen (default, better for larger layers), xsimd (better for very small layers) or plain STL; an optional RTNEURAL_USE_AVX build adds -mavx2 -mfma with 32-byte alignment.

## Compared with alternatives

Pick RTNeural over OpenVINO, MNN or ONNX-class runtimes when the network is tiny and called per audio sample under a hard real-time deadline; pick tiny-cuda-nn for small MLPs only when you are on an NVIDIA GPU with large batches, and LIBXSMM when you are writing your own CPU kernels rather than loading a trained model.

## Integration

| | |
|---|---|
| **Form** | header-style library; CMake add_subdirectory builds a small STATIC target, or include headers directly without CMake |
| **Dependencies** | nlohmann/json (bundled in modules/json) for model loading; Eigen or xsimd (bundled submodules) depending on backend; none for the STL backend |
| **Minimum toolchain** | C++14 (CMake errors below 14; C++17 enables if constexpr); CMake 3.11+ |
| **Platforms** | any C++14 target; armv7 uses 8-byte alignment; optional AVX2+FMA on x86 via RTNEURAL_USE_AVX |
| **Thread safety** | not documented; models hold mutable recurrent state and scratch buffers, so use one model instance per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Without CMake you must define RTNEURAL_DEFAULT_ALIGNMENT (16 or 32) and a backend macro yourself; a missing alignment define only warns and falls back to 16, which mismatches an AVX build.
- Recurrent layers are stateful by default; call reset() before the first forward() and between independent sequences (issue #167 reports pops/clicks when reset() is called mid-stream).
- JSON parsing and model construction allocate and use iostreams: do them off the audio thread; only forward()/reset() are marked RTNEURAL_REALTIME (checked with RealtimeSanitizer in CI).
- Default sigmoid/tanh are exact Eigen/STL math; faster approximations require supplying your own MathsProvider template argument.

## Known shortcomings

- STL backend slower than ONNX Runtime (LSTM 64) and TFLite (Dense 64); baselines timed only in the STL run; compiler unstated.
- Biased baseline: RTNeural-compare's libtorch loop runs without NoGradGuard/InferenceMode at the default thread count while ONNX Runtime is pinned to 1 thread; open issue #157 reports a segfault with two 512-unit GRUs in the compile-time API (no reply).

## Caveats and trade-offs

Benchmark by the RTNeural author on one x86 Mac (i7-8700B), one sample per call, so per-call framework overhead dominates the libtorch, ONNX Runtime and TensorFlow Lite figures; the advantage shrinks as layer size grows, and the STL backend falls below ONNX Runtime (LSTM size 64) and well below TensorFlow Lite (Dense size 64). Baselines were timed only in the STL-backend run; the Eigen and xsimd runs were RTNEURAL_ONLY builds, so those ratios compare separate runs. Compiler not stated, libtorch version not stated. The reference paper (arXiv:2106.03037) is a preprint.

Small fixed set of layer types (Dense, Conv1D/2D, GRU, LSTM, pooling, batch norm, common activations) and inference only; models are exported to JSON; header library with Eigen, xsimd or STL backends (Eigen best for larger networks, xsimd for small ones); designed for real-time audio, single-sample processing.

## Maintenance

Actively maintained (last commit 2026-08-20, 848 stars, used by more than a dozen shipping audio plugins) and BSD-3-Clause, so safe to vendor; note the reference paper (arXiv 2106.03037) is a preprint.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark by the RTNeural author with public code (RTNeural-compare src/benchmark.cpp, run_bench.sh, raw logs in results/bench_{stl,eigen,xsimd}.txt) and a named CPU (Intel Core i7-8700B), built as CMake Release, but the compiler and its version are not stated, so not A. The arXiv paper 2106.03037 appears to be a preprint only (no venue seen), so not B.
- **Verifier notes:** Replaced plot readings with exact values from the raw result logs; the record's approximations were right except Dense size 64, where the about-75x figure belongs to the Eigen backend (xsimd static is 67.9x). Metadata confirmed: BSD-3-Clause, 848 stars, last commit 2026-08-20 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/README.md>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/run_bench.sh>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/results/bench_stl.txt>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/results/bench_eigen.txt>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/results/bench_xsimd.txt>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/plots/lstm.png>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/plots/dense.png>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/plots/gru.png>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/README.md>
  - <https://github.com/jatinchowdhury18/RTNeural>
  - <https://github.com/jatinchowdhury18/RTNeural/commits>
  - <https://github.com/jatinchowdhury18/RTNeural-compare>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/README.md>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/cmake/CXXStandard.cmake>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/cmake/SIMDExtensions.cmake>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/cmake/ChooseBackend.cmake>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/RTNeural/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/RTNeural/RTNeural.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/RTNeural/config.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/RTNeural/common.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/RTNeural/Layer.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/RTNeural/lstm/lstm_eigen.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/RTNeural/maths/maths_eigen.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural/HEAD/RTNeural/model_loader.h>
  - <https://github.com/jatinchowdhury18/RTNeural>
  - <https://github.com/jatinchowdhury18/RTNeural/issues>
  - <https://github.com/jatinchowdhury18/RTNeural/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/jatinchowdhury18/RTNeural/issues/157>
  - <https://github.com/jatinchowdhury18/RTNeural/issues/161>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/README.md>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/src/torch_layer.hpp>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/src/onnx_layer.hpp>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/run_bench.sh>
  - <https://raw.githubusercontent.com/jatinchowdhury18/RTNeural-compare/HEAD/results/bench_eigen.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jatinchowdhury18/rtneural`) · [data/wave8/enrich/raw/github_com_jatinchowdhury18_rtneural.json](../../../data/wave8/enrich/raw/github_com_jatinchowdhury18_rtneural.json) (enrichment confidence 0.8)

</details>
