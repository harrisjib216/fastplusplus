# CMSIS-NN

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Arm's int8/int16/int4 neural-network kernels for Cortex-M; bit-exact drop-in backend that replaces TensorFlow Lite Micro reference kernels.

| | |
|---|---|
| **Beats** | TensorFlow Lite Micro reference kernels (the portable C kernels that TFLM uses when no OPTIMIZED_KERNEL_DIR is set) |
| **Claimed result** | Third-party issue report: reference kernels 14.05 s and CMSIS-NN 13.13 s with the target Makefile's -fno-builtin (about 1.07x, derived from page data); with -fno-builtin removed, reference 14.01 s versus CMSIS-NN 2.33 s, which the reporter calls 'speeded up by 6x' (about 6.0x, derived from page data). Project README itself gives no numbers, only 'optimized to maximize performance and minimize memory footprint' and 'bit-exact with TensorFlow Lite reference kernels'. |
| **Workload** | TFLM cifar10 example (three convolutional layers; an int8-quantized model is needed for CMSIS-NN to be used) built for the sparkfun_edge target, reference kernels versus TAGS=cmsis-nn, same board, same source tree, timed run in seconds. |
| **Metric** | latency |
| **Hardware** | SparkFun Edge board (Cortex-M4F); the reporter says a Cypress PSoC6 board behaves the same. Clock speed not stated; build host Ubuntu 18.04 under WSL. |
| **Compiler and flags** | Not fully stated. Build commands on the page: make -f tensorflow/lite/micro/tools/make/Makefile TARGET=sparkfun_edge cifar10_bin, with and without TAGS=cmsis-nn; the only flag discussed is -fno-builtin from apollo3evb_makefile.inc (present vs deleted). GCC version and -O level are not given. |
| **Adoption** | 449 stars; the CMSIS-NN backend of TensorFlow Lite Micro (tflite-micro tensorflow/lite/micro/kernels/cmsis_nn) |
| **Last commit** | 2026-10-21 |
| **Links** | [repository](https://github.com/ARM-software/CMSIS-NN) · [benchmark](https://github.com/tensorflow/tensorflow/issues/37361) |

## Verdict

One third-party user (TensorFlow issue #37361, March 2020) timed interpreter-&gt;Invoke() with GPIO toggling on a SparkFun Edge (Cortex-M4F) for the TFLM cifar10 example: reference kernels 14.01 s versus CMSIS-NN 2.33 s (about 6.0x) once -fno-builtin was removed, but 14.05 s versus 13.13 s (about 1.07x) with it; GCC version, -O level, clock and repeat count are not given, and the CMSIS-NN version was the one TFLM vendored in 2020.

## Use it when

- Running int8-quantized TFLite models with TensorFlow Lite Micro on Cortex-M4/M7/M33 (DSP extension) or Cortex-M55/M85 (Helium): switch the TFLM build to the cmsis_nn kernels and keep the same outputs.
- Convolution-heavy models (image classification, Visual Wake Words-style CNNs) where kernel time dominates; a third-party SparkFun Edge (Cortex-M4F) run measured 14.01 s to 2.33 s for a three-conv-layer cifar10 example.
- Bare-metal firmware without an interpreter that needs hand-called quantized layers with a fixed, caller-sized scratch buffer and no heap.
- int4-weight / int8-activation or int16-activation (16x8) models on Cortex-M, which the operator table lists as supported for conv, depthwise conv and fully connected.

## Skip it when

- Arm A-class CPUs (Cortex-A, Neoverse): the README itself says to prefer Arm Compute Library or XNNPACK there.
- Models dominated by interpreter or non-kernel overhead: the TFLM paper (per search snippet, not opened) reports only about 25% gain for the Google Hotword model against more than 4x for Visual Wake Words on Cortex-M4.
- Float models on cores without Helium: the float API is experimental and opt-in, and on DSP-only cores it falls back to scalar C that is not a performance target; the v8.0.0 release notes recommend Arm Compiler 6 and mention known GCC issues for the float extension.
- Projects built with IAR or for a host PC: IAR is untested (open issues #212 and #210 on inline assembly and warnings) and host compilation is not supported out of the box.
- Operators outside the table (e.g. Minimum/Maximum/Pad/Transpose have no int16 or DSP versions), where TFLM falls back to its reference kernels anyway.

## How it is fast

Convolution is done as partial im2col plus GEMM: only a couple of patches are expanded into a scratch buffer at a time, then multiplied, to keep RAM small. On cores with the DSP extension (Cortex-M4, M7, M33) int8 data is widened to int16 and multiplied two lanes at a time with the SMLAD dual multiply-accumulate instruction; on Helium cores (Cortex-M55, M85) the MVE path runs int8 matrix multiplies with vector instructions. A wrapper dispatches shape-specialized kernels (1x1 fast path, 1xN path, generic path), and requantization stays in fixed point, so the bit-exact TFLM result is kept.

## Compared with alternatives

Pick CMSIS-NN for Cortex-M microcontrollers running TFLM int8/int16 models; pick KleidiAI (the other Arm kernel library catalogued) for Cortex-A/Neoverse CPUs and LLM matmuls, and RTNeural for small recurrent audio models on desktop-class CPUs where floating point and Eigen/xsimd are available.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake add_library cmsis-nn STATIC) or source-drop via the CMSIS pack / TFLM's downloaded copy |
| **Dependencies** | CMSIS-Core headers (the TFLM build notes say CMSIS-NN depends on CMSIS-Core); Arm Ethos-U Core Platform toolchain files recommended for CMake builds; pybind11 only for the optional Python buffer-size helpers |
| **Minimum toolchain** | CMake 3.21; tested with Arm Compiler 6 and Arm GNU Toolchain (C standard not stated); IAR untested |
| **Platforms** | Arm Cortex-M: pure C path (M0/M3), DSP-extension path (M4, M7, M33 with DSP), MVE/Helium path (M55, M85); selected from compiler feature flags |
| **Thread safety** | not documented (kernels write only to caller-supplied output and a caller-supplied scratch buffer in cmsis_nn_context) |
| **Drop-in for the baseline** | partial — inside TensorFlow Lite Micro it is a build switch with bit-exact results versus the reference kernels; outside TFLM it is a different C API that needs quantization parameters and a scratch buffer per call |

## Gotchas

- Do not build with -fno-builtin or -ffreestanding: CMSIS-NN leans on inlined memcpy/memset, and in TensorFlow issue #37361 the flag cut its lead over the reference kernels from about 6x to about 7%; TensorFlow PR #37936 ('TFLu: remove -fno-builtin compiler flag', merged 2020-05-22) removed it from the TFLM build, but check your own vendor makefiles.
- The CMake default is -Ofast, and the experimental float kernels do not handle NaN, Inf, denormals or signed zero; inputs must already be finite.
- CMSIS_NN_USE_REQUANTIZE_INLINE_ASSEMBLY is faster on Cortex-M4 but slower on other cores, and an output difference with it enabled is an open issue (#177); options marked as affecting headers must be set identically in TFLM.
- APIs change across major releases (v6.0.0 and v7.0.0 changed arm_convolve_s8, buffer-size and LSTM signatures), and recent fixes include wrong transpose-conv output when pad_h % stride_h != 0 (#230) and missing int16 saturation in LSTM gates (#245), so pin a release and run the unit tests.

## Known shortcomings

- Downgraded B to C by verifier: TF issue #37361 numbers match (14.05/13.13 s with -fno-builtin, 14.01/2.33 s without), but it is one user's report with no GCC version, -O level, clock or timing scope (numbers without methodology, NCCL gloo-issue precedent).
- 1.07x row measures a -fno-builtin build handicap; float kernels ignore NaN, Inf and denormals

## Caveats and trade-offs

Evidence is one March 2020 user issue (opened 2020-03-05, closed 2020-06-11), not a project benchmark: single model, single board, no compiler version or -O level, timing scope (whole run or per inference) not spelled out, and the comparison depends on a TFLM Makefile flag (-fno-builtin) that the TFLM fix PR #37936 later addressed; the CMSIS-NN version then vendored in TFLM is also old. With the flag on, CMSIS-NN was only about 7% faster. The same issue says that from TensorFlow commit 4030aa1 the reference conv and depthwise-conv layers were 'equally fast as the optimized CMSIS-NN kernel or even faster' under that flag, which the reporter traced to -fno-builtin, not to the commit. Other numbers seen only as search-result snippets, pages blocked (EGRESS_BLOCKED) so unverified: the MLSys 2021 TFLM paper (arXiv 2010.08678) reports more than 4x for the Visual Wake Words model on Cortex-M4 and about 25% for the Google Hotword model against reference kernels; an Arm blog reports 3.1x with GCC on a Cortex-M7 (2.26 versus 0.72 inferences/s); the original 2018 CMSIS-NN paper (arXiv 1801.06601) reports 4.6x runtime on CIFAR-10 on a Cortex-M7 at 216 MHz, but against a Caffe-like baseline built on CMSIS-DSP 1D convolution, not TFLM reference kernels. A tflite-micro pull request opened 2026-10-10 (#3823, float32 Conv2D dispatch, page opened) quotes total CONV_2D ticks 235.6M down to 19.1M (about 12.35x) on the Corstone-300 FVP, which it says is not cycle accurate; core, compiler and flags not stated. The CMSIS-NN README and release notes carry no cycle counts or speedups. [retier] Enricher: issue #37361 gives the timing scope (Invoke() timed by a GPIO toggle). Removing -fno-builtin speeds CMSIS-NN 3-6x while the reference kernels stay unchanged, so the 1.07x row measures a build-flag handicap; PR #37936, which removed -fno-builtin, merged 2020-05-22. Gotchas: the CMake default is -Ofast; float kernels ignore NaN, Inf and denormals; open issue #177; fixes #230 and #245.

C library for Cortex-M (DSP extension, Helium/MVE) with int4, int8 and int16 kernels and an experimental float set; bit-exact with TensorFlow Lite reference kernels (TFL and TFLM references may differ, per the README). The README says restrict-keyword and requantize inline-assembly options help some cores (Cortex-M7, Cortex-M4) and not others, and that A-class CPUs are expected to be slower than Arm Compute Library or XNNPACK. IAR is untested.

## Maintenance

Actively maintained by Arm (last commit 2026-10-21, latest release v8.0.0 adding experimental float kernels, about two releases a year) under Apache-2.0, and shipped as the CMSIS-NN backend of TensorFlow Lite Micro, so it is safe to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** tensorflow/tensorflow issue #37361 (opened 2020-03-05 by a third-party Infineon user, closed 2020-06-11) gives exactly 14.05 s / 13.13 s with -fno-builtin and 14.01 s / 2.33 s without it for TFLM reference versus TAGS=cmsis-nn on the SparkFun Edge (Cortex-M4F), with the make commands shown, but it is a single user report with no GCC version, -O level, clock, iteration count or timing scope, so it is independent numbers without methodology (C, as for the NCCL gloo-issue precedent), not a benchmark suite or paper (B).
- **Verifier notes:** All record numbers, dates, commit 4030aa1, PR #37936 and the PSoC6 remark (2020-03-12 comment) match the issue; host is written 'Ubuntu 18.04 in WSH on Win10' on the page. tflite-micro PR #3823 (open, 2026-10-10) quote of 235.6M to 19.1M CONV_2D ticks on Corstone-300 FVP, 'not cycle accurate', also checked. Metadata confirmed: Apache-2.0, 449 stars, last commit 2026-10-21; README has no numbers. The paper/blog figures in caveats stay snippet-only leads for enrichment (MLSys TFLM paper, Arm blog).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-182 (wave 8 book seed pass, 2026-10-24); enrichment (wave 8 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/tensorflow/tensorflow/issues/37361>
  - <https://github.com/ARM-software/CMSIS-NN>
  - <https://github.com/ARM-software/CMSIS-NN/commits>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-NN/HEAD/README.md>
  - <https://github.com/tensorflow/tflite-micro/pull/3823>
- **Sources the enricher read:**
  - <https://github.com/ARM-software/CMSIS-NN>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-NN/HEAD/README.md>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-NN/HEAD/Include/arm_nnfunctions.h>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-NN/HEAD/Source/ConvolutionFunctions/arm_convolve_wrapper_s8.c>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-NN/HEAD/Source/ConvolutionFunctions/arm_convolve_s8.c>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-NN/HEAD/ARM.CMSIS-NN.pdsc>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-NN/HEAD/CMakeLists.txt>
  - <https://github.com/ARM-software/CMSIS-NN/issues?q=is%3Aissue>
  - <https://github.com/ARM-software/CMSIS-NN/releases>
  - <https://github.com/tensorflow/tensorflow/issues/37361>
  - <https://github.com/tensorflow/tensorflow/pull/37936>
  - <https://raw.githubusercontent.com/tensorflow/tflite-micro/main/tensorflow/lite/micro/kernels/cmsis_nn/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/arm-software/cmsis-nn`) · [data/wave8/enrich/raw/github_com_arm_software_cmsis_nn.json](../../../data/wave8/enrich/raw/github_com_arm_software_cmsis_nn.json) (enrichment confidence 0.72)

</details>
