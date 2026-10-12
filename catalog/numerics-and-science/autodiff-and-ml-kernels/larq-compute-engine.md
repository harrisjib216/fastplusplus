# Larq Compute Engine

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (hand-written kernels with inline assembly and intrinsics) with Python converter` · `Apache-2.0` · 🟢 active

> TensorFlow Lite custom ops for binarized neural networks on 64-bit ARM; reports lower Bi-RealNet latency than dabnn on a Pixel 1.

| | |
|---|---|
| **Beats** | dabnn (its own published Bi-RealNet time on Pixel 1, cross-report, not a same-run measurement); the MLSys 2021 LCE paper (not opened) reportedly compares binary convolutions against full-precision TensorFlow Lite convolutions |
| **Claimed result** | README: dabnn 'reports an inference time of 61.3 ms for Bi-RealNet (56.4% accuracy) on the Pixel 1 phone, while LCE achieves an inference time of 41.6 ms for Bi-RealNet on the same device' (1.47x, derived from page data); BiRealNet-Stem 43.2 ms at the same accuracy. QuickNet tables (single-thread / 4 threads, no baseline): QuickNet 45.0/20.8 ms on RPi 4B, 25.5/12.6 ms on Pixel 1, 5.8/2.5 ms on Mac Mini M1. MLSys 2021 paper abstract (per WebSearch snippet, PDF not opened): binary convolutions 8.5x to 18.5x faster than their full-precision counterparts on Pixel 1. |
| **Workload** | Bi-RealNet inference on a Pixel 1 phone, and QuickNet models on Raspberry Pi 4B, Pixel 1 and Mac Mini M1 (TensorFlow Lite benchmark tool with XNNPack enabled). |
| **Metric** | latency |
| **Hardware** | Pixel 1 phone (2016) for the dabnn comparison; Raspberry Pi 4B 1.5GHz and Mac Mini M1 for QuickNet tables |
| **Adoption** | 258 stars |
| **Last commit** | 2026-07-30 |
| **Links** | [repository](https://github.com/larq/compute-engine) · [benchmark](https://github.com/larq/compute-engine) |

## Verdict

The README reports first-party latencies from its TFLite benchmark tool with XNNPACK enabled and random inputs: Bi-RealNet runs in 41.6 ms on a Pixel 1, versus the 61.3 ms that dabnn published for the same model (about 1.47x, a cross-report comparison, not a same-run measurement); QuickNet runs in 25.5 ms single-threaded on a Pixel 1 and 45.0 ms on a Raspberry Pi 4B. The MLSys 2021 paper's 8.5-18.5x figure (known only from search snippets) compares binary convolutions with full-precision ones, which is not equal work; no compiler flags are stated.

## Use it when

- You are deploying a BNN (QuickNet, Bi-RealNet or your own Larq model) to an AArch64 phone or board such as Android or Raspberry Pi 4 in 64-bit mode.
- Your binary layers are standard 2D convolutions (grouped convolutions are supported since v0.5/v0.6) and the rest of the model can stay on built-in TFLite ops.
- You already train with Larq/Keras and want a converter path that keeps the training graph and the deployed graph consistent.
- You want per-layer latency numbers on device: the repo ships a TFLite benchmark tool with the LCE ops registered.

## Skip it when

- Full-precision or int8 models: LCE adds nothing; it only speeds up layers that are truly binarized, and binarization costs accuracy (QuickNet tops out at 66.9% ImageNet top-1).
- x86 or other non-AArch64 targets as an inference engine: the hand-written kernels are AArch64-only, and elsewhere the code falls back to portable C++ (Ruy kStandardCpp path, std::bitset popcount).
- GPUs, NPUs or LLM workloads: CPU only, convnet-oriented ops.
- Projects that cannot take a Bazel build pinned to a specific TensorFlow source tree (TF 2.16.1 in WORKSPACE, Bazel 6.5.0).
- Teams wanting fast upstream movement: the last tagged release is v0.16.0 (2024-06-21) and recent commits are mostly dependency bumps.

## How it is fast

Binary convolution becomes a binary GEMM: activations and weights are bit-packed into 32-bit words, and each multiply-accumulate is an XOR followed by a popcount. On AArch64 the indirect-BGEMM kernels (8x4x1, 8x4x2 and 8x4x4, picked at runtime from the packed input depth) do this in inline NEON assembly (eor, cnt, addp) with 16-bit accumulators, and the im2col path plugs custom kernels into Google's Ruy GEMM framework. The kernels apply a per-channel output transform (multiplier, bias, clamp) in the same pass, and since v0.7.0 the converter keeps activations bit-packed between binary layers by default.

## Compared with alternatives

Pick LCE over MNN, OpenVINO or FeatherCNN only when your network is binarized end to end, since those engines target float/int8 models; pick BitNet (bitnet.cpp) or T-MAC instead for low-bit LLM inference, which is where LCE has no kernels.

## Integration

| | |
|---|---|
| **Form** | static lib (TFLite custom-op library built with Bazel against a pinned TensorFlow source tree) plus a Python converter wheel |
| **Dependencies** | TensorFlow Lite (TensorFlow 2.16.1 sources), Ruy, flatbuffers; the converter needs Python 3.10-3.12 and TensorFlow &gt;= 2.8; Bazel 6.5.0 to build |
| **Minimum toolchain** | Bazel 6.5.0; aarch64 builds use -march=armv8-a; Android NDK for Android; exact minimum compiler not documented |
| **Platforms** | Optimized kernels: AArch64 (Android, 64-bit Raspberry Pi and other ARM boards, Apple M1 per the README benchmarks). Portable C++ fallback elsewhere. Converter wheels: Linux x86-64, macOS x86-64 and arm64, Windows x86-64. |
| **Thread safety** | Not documented beyond TFLite interpreter rules (one interpreter per thread; intra-op threads via TFLite's thread count). Issue #730 (2022) reported the aarch64 benchmark tool crashing with --num_threads=2 on Raspberry Pi and Jetson; closed a day later, resolution not visible on the page. |
| **Drop-in for the baseline** | partial — the model must be trained with Larq and converted with the LCE converter; the TFLite interpreter API is unchanged, you only register the extra custom ops |

## Gotchas

- Kernels may read (never write) up to 16 bytes past the end of an array (LCE_EXTRA_BYTES in core/types.h); custom tensor allocations need that padding.
- The AArch64 assembly kernels use 16-bit accumulators and are chosen only if the maximum accumulator value fits in uint16; otherwise the code falls back to the portable 4x2 C++ kernel, and bit-packed output is also portable-only.
- The benchmark tool defaults to use_indirect_bgemm=false (Ruy-based BGEMM); pass the flag to measure the indirect kernels.
- Open bug #421 (since 2020): int8 default ranges break when a binary conv is followed by a normal conv.

## Known shortcomings

- dabnn number taken from dabnn's own report, not the same run; MLSys 2021 paper unreadable here (possible B on retier).
- Optimized kernels are AArch64-only; x86 falls back to portable C++ (std::bitset popcount). Bug #421 (int8 ranges) open since 2020. Kernels over-read 16 bytes. Last release v0.16.0 (2024-06), pinned to TF 2.16.1. dabnn comparison is cross-report, not one harness.

## Caveats and trade-offs

The dabnn figure is dabnn's own reported number, not a same-run measurement, so this is a cross-report comparison. Benchmarks are dated 2021-06-11 (Pixel 1), 2021-06-13 (M1) and 2022-04-20 (RPi 4B) and use the LCE TFLite benchmark tool with XNNPack enabled and randomized inputs; no compiler or build flags stated. The README gives no XNNPACK or oneDNN comparison; the paper's 8.5x to 18.5x figure compares 1-bit binary convolutions against full-precision ones (different precision and accuracy), not equal work. Recent commits are mostly dependabot bumps; the last human commit seen is 2026-06-19 (RISC-V build path).

Only helps binarized or extremely quantized networks; runs as custom TensorFlow Lite operators. Non-binarized layers use the regular TensorFlow Lite operators.

## Maintenance

Apache-2.0 and still receiving commits (mostly dependency bumps, plus a RISC-V build path in 2026), but the last PyPI release is v0.16.0 from June 2024 and the build is tied to TensorFlow 2.16.1, so expect to do your own porting.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README gives first-party Pixel 1 / RPi 4B / M1 latencies measured with the public LCE TFLite benchmark tool (larq_compute_engine/tflite/benchmark/lce_benchmark_main.cc), but the only baseline is dabnn's own published Bi-RealNet time, and compiler/flags are not stated, so C. The peer-reviewed MLSys 2021 paper could not be opened (proceedings.mlsys.org blocked), so B is not confirmed.
- **Verifier notes:** Metadata confirmed via github.com: Apache-2.0, 258 stars, 35 forks, 636 commits, not archived/fork, last commit 2026-07-30 (dependabot). Retier candidate: MLSys 2021 paper 'Larq Compute Engine: Design, Benchmark, and Deploy State-of-the-Art Binarized Neural Networks' (Bannink et al.) is peer-reviewed; if its PDF can be opened elsewhere, B is likely.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/larq/compute-engine>
  - <https://github.com/larq/compute-engine/commits>
  - <https://github.com/larq/compute-engine/tree/main/larq_compute_engine/tflite/benchmark>
  - <https://github.com/larq/compute-engine/tree/main/docs>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/README.md>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/larq/compute-engine>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/README.md>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/docs/README.md>
  - <https://github.com/larq/compute-engine/tree/main/docs>
  - <https://github.com/larq/compute-engine/tree/main/larq_compute_engine/core>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/.bazelrc>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/.bazelversion>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/WORKSPACE>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/setup.py>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/configure.py>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/larq_compute_engine/core/types.h>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/larq_compute_engine/core/bgemm/bgemm.h>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/larq_compute_engine/core/bgemm/kernels_aarch64.h>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/larq_compute_engine/core/indirect_bgemm/select_kernel.h>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/larq_compute_engine/core/indirect_bgemm/kernel_8x4x1_aarch64.h>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/larq_compute_engine/core/indirect_bgemm/kernel_4x2_portable.h>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/larq_compute_engine/tflite/kernels/BUILD>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/larq_compute_engine/tflite/benchmark/lce_benchmark_main.cc>
  - <https://raw.githubusercontent.com/larq/compute-engine/HEAD/larq_compute_engine/tflite/benchmark/lce_benchmark_tflite_model.cc>
  - <https://github.com/larq/compute-engine/issues?q=is%3Aissue+bug>
  - <https://github.com/larq/compute-engine/issues/730>
  - <https://github.com/larq/compute-engine/releases>
  - <https://pypi.org/pypi/larq-compute-engine/json>
  - https://arxiv.org/html/2011.09398v2 (EGRESS_BLOCKED; paper claims taken from WebSearch snippets)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/larq/compute-engine`) · [data/wave8/enrich/raw/github_com_larq_compute_engine.json](../../../data/wave8/enrich/raw/github_com_larq_compute_engine.json) (enrichment confidence 0.75)

</details>
