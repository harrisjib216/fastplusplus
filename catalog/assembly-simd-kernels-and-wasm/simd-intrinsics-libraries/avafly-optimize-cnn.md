# optimize-cnn (hand-written NEON tiny CNN inference)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Hand-written NEON inference for one tiny Fashion-MNIST CNN on a Raspberry Pi 4B; 2.1-3.1x faster than tuned TFLite, ncnn and ONNX Runtime.

| | |
|---|---|
| **Beats** | ONNX Runtime 1.27.1, ncnn 20260526 and TensorFlow Lite 2.20.0 (tuned by the author) |
| **Claimed result** | README table: cnn_fuse 783 ms and cnn_neon 1045 ms vs cnn_ort 2440 ms, cnn_ncnn 2302 ms, cnn_tflite 1621 ms (cnn_fuse about 3.1x vs ORT, 2.9x vs ncnn, 2.1x vs TFLite, derived from page data). |
| **Workload** | Inference of a tiny fixed Fashion-MNIST CNN (conv 8 ch, conv 16 ch, FC) over 70,000 28x28 images, processed in blocks of 32; ncnn, TFLite and the hand-written variants run one image per OpenMP thread (single-threaded ncnn net and per-thread TFLite interpreters), ORT uses intra-op threads with sub-batches of 8; one warmup, then the best of --runs timed runs (N not stated) of steady_clock wall time; README text gives 4 threads for the framework rows. |
| **Metric** | throughput |
| **Hardware** | Raspberry Pi 4B (4x Cortex-A72 at 1.8 GHz, 4 GB RAM) |
| **Compiler and flags** | CMake Release build (default), C++17, -Wall -Wextra -Wpedantic, OpenMP; the hand-written variants (cnn_struct, cnn_const, cnn_neon, cnn_fuse) add -funsafe-math-optimizations -mcpu=native; ONNX Runtime 1.27.1, ncnn 20260526, TFLite 2.20.0 and OpenBLAS are linked as prebuilt libraries from \~/Documents/libs with unstated build options; compiler name and version not stated |
| **Adoption** | 10 stars |
| **Last commit** | 2026-08-29 |
| **Links** | [repository](https://github.com/Avafly/optimize-cnn) · [benchmark](https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/README.md) |

## Verdict

On a Raspberry Pi 4B (4x Cortex-A72 at 1.8 GHz), classifying 70,000 Fashion-MNIST images in blocks of 32 with best-of-N wall time, cnn_fuse took 783 ms and cnn_neon 1045 ms against TFLite 2.20.0 at 1621 ms, ncnn 20260526 at 2302 ms and ONNX Runtime 1.27.1 at 2440 ms (about 2.1x, 2.9x and 3.1x for cnn_fuse, derived from page data), with each framework tuned by the author; compiler unstated. By the README's own one-FMLA-per-cycle ceiling (137 + 403 + 14 ms for conv1, conv2 and FC at 4 threads), cnn_fuse runs at roughly 70% of peak (derived from page data).

## Use it when

- You ship a fixed, tiny CNN (a few thousand parameters, few channels) to a known ARMv8 board and per-image latency or throughput matters more than flexibility.
- You want a short, readable template for a fused conv + pool + activation NEON kernel to adapt to your own small model.
- You profile a small model under ONNX Runtime, ncnn or TFLite and find im2col and framework overhead dominate; this repo shows the per-layer measurement-versus-MAC-ceiling method for deciding what to hand-write.
- Teaching or self-study of step-by-step inference optimization (struct, then constants, then NEON, then fusion), each step with a measured time.

## Skip it when

- Any model other than this exact architecture: kernel shapes, offsets into model.bin and buffer sizes are hard-coded, so a new model means rewriting the kernels.
- x86 or 32-bit ARM targets: the kernels use AArch64-only NEON intrinsics (vfmaq_laneq_f32, vaddvq_f32, vpmaxq_f32) and there is no scalar fallback.
- Medium or large models where im2col cost is small next to GEMM; the README itself says frameworks do well there.
- When you need quantized (int8) or fp16 inference, dynamic shapes, batching APIs or model-format import; none exist here.
- Production use that needs tests beyond the one logit-tolerance check, versioned releases or support: 10 stars, 18 commits written in one week of August 2026.

## How it is fast

cnn_neon replaces im2col + OpenBLAS sgemm with a direct convolution: weights are repacked so four output channels sit in one NEON register, and each 3x3 tap does vfmaq_laneq_f32 on four output pixels for four channels at once (4x4 register blocking), with a zero-bordered input copy to drop boundary checks; the FC layer uses pre-interleaved weights and ten NEON accumulators. cnn_fuse then fuses conv, 2x2 max pool and leaky ReLU into one kernel: it computes two conv rows in registers, pools them with vpmaxq_f32/vmax_f32, applies the activation after pooling (valid because leaky ReLU is monotonic, so it runs on 4x fewer values) and never writes the conv output to memory. Shapes are compile-time constants, and parallelism is one image per OpenMP thread.

## Compared with alternatives

None of the siblings is an inference engine; pick this over IntrinsicML (generic SIMD ML microkernels, mostly x86) when you need a complete fused NEON forward pass for a tiny CNN on Cortex-A72, and over ARM NEON Compositor when your NEON workload is convolution rather than image blending.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenMP and fmt (vendored header-only in src/3rdparty) for cnn_neon and cnn_fuse; OpenBLAS for cnn_struct and cnn_const; ONNX Runtime 1.27.1, ncnn 20260526 and TFLite 2.20.0 for the comparison programs; Python 3.11 with torch 2.13.0 to train and export the model |
| **Minimum toolchain** | C++17, CMake 3.20, a GCC or Clang with AArch64 arm_neon.h and OpenMP (compiler version not documented) |
| **Platforms** | AArch64 with NEON only (tested on Raspberry Pi 4B, Cortex-A72, 64-bit OS implied by the A64 intrinsics) |
| **Thread safety** | not documented; each program uses file-scope static buffers with per-OpenMP-thread scratch slots indexed by omp_get_thread_num() and capped at 8 threads, so run() is safe only inside its own OpenMP loop |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry: the ONNX Runtime row runs Session::Run sequentially on sub-batches of 8 images with intra-op threads, while every other row runs one image per OpenMP thread (ncnn with a single-threaded net, TFLite with one interpreter per thread); an image-per-thread ORT configuration (concurrent Run calls, one intra-op thread each) was not measured, so part of the 3.1x versus ORT may reflect threading strategy rather than kernels.
- The hand-written builds get -mcpu=native and -funsafe-math-optimizations while ORT, ncnn, TFLite and OpenBLAS are prebuilt libraries from \~/Documents/libs with unstated build options; the compiler and version, and the --threads and --runs values used for the README table, are not stated (the program default is 1 thread; the README text mentions 4 threads for the frameworks).
- The README says cnn_neon uses a hand-written GEMM from optimize-gemm; the code is a self-contained direct convolution (4x4 register-blocked lane FMAs), and no optimize-gemm code is included. Correctness is checked: the hand-written programs compare all 70,000 x 10 logits against PyTorch reference logits with a 1e-4 max-abs tolerance, while the framework programs only report argmax agreement (tolerance disabled).
- CMakeLists.txt makes ncnn, ONNX Runtime and OpenBLAS REQUIRED for the whole project, so building only cnn_fuse needs an edited CMakeLists or a manual compile; the images, reference logits and model files come from the 'data' release (data_20260829.tar.gz, 46 MB) or from rerunning python/train.py.

## Known shortcomings

- A toy fixed model, not a library; compiler unstated; the frameworks are prebuilt with unknown flags against a -mcpu=native -funsafe-math-optimizations build; loose category fit.
- Enricher: harness asymmetry: the ONNX Runtime row runs sequential Session::Run on 8-image sub-batches with intra-op threads while every other row runs one image per OpenMP thread; thread and run counts for the table unstated; frameworks prebuilt with unknown flags; the README says cnn_neon uses the optimize-gemm GEMM but the code is a self-contained direct convolution (4x4 register-blocked lane FMAs); AArch64-only intrinsics; CMake hard-requires ncnn and ORT; hand-written outputs match the reference logits at 1e-4.

## Caveats and trade-offs

A single fixed tiny model hand-coded in about 200 lines per variant, not a reusable library or a general SIMD library; the category simd-intrinsics-libraries is a loose fit (NEON intrinsics in an ML inference demo). The hand-written builds get -mcpu=native and -funsafe-math-optimizations while the frameworks are prebuilt binaries with unknown build flags, and the author tuned each framework (per-thread ncnn allocators with fp16 and packing disabled, per-thread TFLite interpreters, ORT batch shape); compiler and version are not stated and the per-row thread count and run count of the table are not stated. The hand-written outputs are checked against reference logits with a 1e-4 tolerance (frameworks with argmax agreement only), so the fast path computes the same model. Uses the author's hand-written GEMM from optimize-gemm (already catalogued in wave 8, blas-lapack). 10 stars, 18 commits, all from August 2026.

Hard-coded model architecture and fixed hardware (Cortex-A72 NEON, fused conv-pool-activation kernels); not a general inference framework.

## Maintenance

Active only in a burst (18 commits, 22-29 August 2026, none since) and MIT-licensed; useful as a copyable template for small fixed models on AArch64, not as a maintained dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table (cnn_fuse 783 ms, cnn_neon 1045 ms vs cnn_ort 2440, cnn_ncnn 2302, cnn_tflite 1621 ms) with public harness code (src/cnn_\*.cpp, src/common.h run_timed and verify) and the CPU (Raspberry Pi 4B, Cortex-A72) stated, but no compiler name or version and the framework libraries are unstated prebuilt binaries, so not A.
- **Verifier notes:** Numbers on the README match the record exactly and the harness compares like with like (same 70,000 images, same block-of-32 pattern, correctness check against exported reference logits). Main shortcomings: one fixed toy model, compiler unstated, frameworks built with unknown flags while the hand-written code gets -mcpu=native -funsafe-math-optimizations, and the category is a loose fit (ML inference demo rather than a SIMD library). Related to avafly/optimize-gemm (wave 8) but a distinct project, not a duplicate.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-111 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/README.md>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_fuse.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_neon.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_ort.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_ncnn.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_tflite.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/common.h>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/LICENSE>
  - <https://github.com/Avafly/optimize-cnn>
  - <https://github.com/Avafly/optimize-cnn/commits>
- **Sources the enricher read:**
  - <https://github.com/Avafly/optimize-cnn>
  - <https://github.com/Avafly/optimize-cnn/commits>
  - <https://github.com/Avafly/optimize-cnn/issues?q=is%3Aissue>
  - <https://github.com/Avafly/optimize-cnn/releases>
  - <https://github.com/Avafly/optimize-cnn/releases/expanded_assets/data>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/README.md>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/common.h>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_fuse.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_neon.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_struct.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_const.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/layers.h>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_ort.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_ncnn.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/src/cnn_tflite.cpp>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/python/train.py>
  - <https://raw.githubusercontent.com/Avafly/optimize-cnn/HEAD/python/requirements.txt>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/avafly/optimize-cnn`) · [data/wave13/enrich/raw/github_com_avafly_optimize_cnn.json](../../../data/wave13/enrich/raw/github_com_avafly_optimize_cnn.json) (enrichment confidence 0.7)

</details>
