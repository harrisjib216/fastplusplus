# NNPACK (Winograd/FFT convolution)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🔴 abandoned

> C99 CPU convolution primitives using Winograd and FFT tiles for stride-1 layers; fp32, AVX2/FMA3 or NEON.

| | |
|---|---|
| **Beats** | XNNPACK (convolution_bench, 2020 version) |
| **Claimed result** | Issue output: NNPACK (benchmark_conv, WT8x8 Winograd, 1 thread, 3 iterations) 31.948 ms and 76.170 ms (block multiplication 91.4 and 89.3 GFLOPS) vs XNNPACK convolution_bench 1345.8 ms and 3060.0 ms (7.07 and 7.05 GFLOPS, 1 iteration) for 256-to-128 channels at 128x128 and 192-to-96 channels at 256x256 with 3x3 kernels: about 42x and 40x (derived from page data). The XNNPACK run was most likely an unoptimized Bazel fastbuild (no '-c opt'), so the ratio overstates the gap; the reporter's own estimate on real networks is that XNNPACK was 3-5x slower on arm64 and x86, with no numbers given. |
| **Workload** | Two large 3x3 convolutions (256 input / 128 output channels at 128x128; 192 input / 96 output channels at 256x256) on a 6-core 4.3 GHz x86 CPU, XNNPACK convolution_bench vs NNPACK benchmark_conv with the 8x8 Winograd algorithm. |
| **Metric** | throughput |
| **Hardware** | 6-core CPU at 4300 MHz, caches L1/L2/L3 32 KiB/256 KiB/9216 KiB (model not named), Ubuntu, single thread |
| **Adoption** | 1.7k stars; backend in PyTorch mobile, Caffe2, MXNet, TVM |
| **Last commit** | 2023-02-01 |
| **Links** | [repository](https://github.com/Maratyszcza/NNPACK) · [benchmark](https://github.com/google/XNNPACK/issues/689) |

## Verdict

The only numbers are from one user's June 2020 XNNPACK issue (#689): on an unnamed 6-core 4.3 GHz x86 CPU, single-threaded, NNPACK's 8x8 Winograd took 31.9 ms and 76.2 ms on two large 3x3 layers (256 to 128 channels at 128x128, 192 to 96 at 256x256) against 1345.8 ms and 3060.0 ms for XNNPACK's convolution_bench, about 42x and 40x (derived from page data). XNNPACK was most likely built without -c opt (Bazel's unoptimised default), and Winograd's effective GFLOPS are not comparable with direct convolution, so the ratio overstates the gap; the reporter's own estimate for real networks was 3-5x, with no numbers.

## Use it when

- fp32 inference or training of stride-1 3x3 convolutions with many channels (VGG/ResNet-style layers) on AVX2+FMA3 x86-64 or NEON ARM CPUs, where Winograd F(6x6,3x3) does far fewer multiplies than direct convolution.
- Stride-1 convolutions with larger kernels (4x4 up to 16x16), which select the FFT 8x8 or 16x16 path.
- CPU training loops that need convolution backward passes (input and kernel gradients), not only inference.
- Repeated inference with fixed weights, using transform_strategy precompute/reuse to skip kernel transforms on every call.
- Maintaining an existing Caffe2, MXNet, TVM, tiny-dnn or darknet-nnpack deployment that already links it.

## Skip it when

- Depthwise, grouped or strided convolutions: these fall back to implicit GEMM, and mobile depthwise-separable networks are better served by XNNPACK (a 2019 PyTorch issue, #30622, proposed replacing NNPACK with XNNPACK on Android for this reason, without numbers).
- Quantised (int8) or fp16/bf16-activation inference: NNPACK is fp32, apart from an fp16 Winograd path on ARM with NEON-HP and fp16-weight fully-connected inference.
- x86 CPUs without AVX2/FMA3, or VMs and containers where cpuinfo cannot see a 3-level cache: nnp_initialize returns unsupported hardware (issues #221 on a Ryzen 9 7950X under Proxmox, #207 on a VM).
- Accuracy-sensitive layers: Winograd F(6x6,3x3) is less numerically stable than direct convolution; issue #8 proposes transforms said to be 100x more stable, and their adoption is not documented.
- New projects that need maintenance, Windows/MSVC or AVX-512 kernels: no commits since 2023-02-01, only an unofficial Windows port, and the x86-64 kernels are AVX2/FMA3 only.

## How it is fast

Fast-convolution algorithms cut the multiply count: 3x3 stride-1 layers use tiled Winograd F(6x6,3x3) on 8x8 tiles, kernels up to 16x16 use 2D FFT on 8x8 or 16x16 tiles, 1x1 uses a direct GEMM, and everything else falls back to implicit GEMM. The transformed tiles are multiplied with register-blocked GEMM microkernels (s8gemm, c8gemm, s4c6gemm), generated on x86-64 as AVX2/FMA3 assembly through PeachPy, with L1/L2/L3 blocking sizes computed at init from cpuinfo's cache detection. Kernel transforms can be precomputed once and reused across inference calls.

## Compared with alternatives

Pick NNPACK over FeatherCNN or MNN when you want standalone fp32 convolution primitives, including backward passes, for large stride-1 3x3 or bigger-kernel layers rather than a full inference engine; FeatherCNN reports beating Caffe2+NNPACK on ARM servers, and LIBXSMM is the better choice on AVX-512/AMX x86 for small-GEMM-based convolution.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (CMake; also a vcpkg port) |
| **Dependencies** | pthreadpool, cpuinfo, FXdiv, FP16 and psimd (downloaded by CMake at configure time unless \*_SOURCE_DIR is set); x86-64 backend also needs Python with PeachPy, opcodes and six to generate assembly; googletest for tests |
| **Minimum toolchain** | C99 (C++11 for tests), CMake 2.8.12+, Python for PeachPy on x86-64; clang required for Android arm64-v8a |
| **Platforms** | x86-64 Linux/macOS (AVX2+FMA3 and a 3-level cache), ARM NEON and ARM64 on Linux/Android/iOS, Android x86/x86-64 (generic SSE2 PSIMD kernels), Emscripten asm.js/WebAssembly, scalar fallback; no mips, no official Windows |
| **Thread safety** | nnp_initialize is guarded by pthread_once; each call parallelises over a caller-supplied pthreadpool (NULL runs on the calling thread); concurrent calls sharing one workspace buffer are not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- On x86-64, if CMake cannot find a Python interpreter it silently falls back to the generic PSIMD backend instead of the AVX2 assembly kernels; Android x86-64 builds always use SSE2 PSIMD kernels.
- Cache-blocking sizes come from detected cache sizes: issue #218 reports a SIGFPE (input_channels_block_max rounding to 0, then a division) in convolution-inference.c on an AMD EPYC 7552 booted with nosmt, where cache sizes were misdetected.
- Workspace buffers must be 64-byte aligned; passing workspace_buffer NULL with a size pointer returns the required size and does not compute, and passing both NULL makes NNPACK allocate on every call.
- The CMake build downloads dependencies and PeachPy from the network at configure time; issues report a failed cpuinfo tag checkout (#213), a missing fp16/psimd.h (#222) and non-reproducible builds (#206).

## Known shortcomings

- 42x claim overstated: XNNPACK was run without '-c opt' (likely an unoptimized Bazel fastbuild).
- nnp_initialize rejects VMs that hide L3 cache (#221, #207); SIGFPE divide-by-zero from misdetected cache sizes under nosmt (#218); silent PSIMD fallback when Python/PeachPy is missing at configure time; Winograd F(6x6,3x3) accuracy concern (#8).

## Caveats and trade-offs

The only evidence is one user's June 2020 GitHub issue (Kepnu4), closed with no maintainer explanation visible; CPU model (6 cores at 4300 MHz, 9 MiB L3), compiler and flags are not stated. XNNPACK was run with 'bazel run //:convolution_bench' without '-c opt', i.e. Bazel's unoptimized fastbuild default (XNNPACK's README uses '-c opt'), which fits its 7 GFLOPS on a 4.2 GHz core. The second XNNPACK run reports Freq=1.18G under a CPU-scaling warning, and each XNNPACK case ran 1 iteration. NNPACK uses Winograd F(6x6,3x3) and XNNPACK direct convolution, so effective GFLOPS compare different algorithms. No commits since February 2023.

Convolution-focused (Winograd for 3x3 stride-1, FFT up to 16x16, implicit GEMM), floating point only; GFLOPS are 'effective' because Winograd does fewer multiplies than direct convolution.

## Maintenance

Abandoned (last commit 2023-02-01, many open build and hardware-detection issues) but BSD-2-Clause and still an optional backend in PyTorch and TVM builds; vendor it only for fp32 stride-1 convolution on AVX2 or NEON CPUs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** A single user's GitHub issue with raw benchmark output but no CPU model, compiler or flags; the XNNPACK baseline was run as 'bazel run //:convolution_bench' without '-c opt' (Bazel's default fastbuild, unoptimized), while XNNPACK's README builds its benchmarks with 'bazel build -c opt'. The rule for debug/-O0 baselines caps this at C, and the 40x-42x ratio is not a fair comparison.
- **Verifier notes:** Downgraded for an overstated claim (tier stays C): the 40x-42x gap almost certainly reflects an unoptimized XNNPACK build. Metadata confirmed on the GitHub page: BSD-2-Clause (LICENSE file: Facebook / Georgia Tech), 1.7k stars, 321 forks, 374 commits, last commit 2023-02-01, not archived; abandoned is correct. Shortcoming to record: the baseline was likely unoptimized and there is no fair numeric evidence; a better numbers page would help (none found in the README).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `hardware`
- **Pages the verifier opened:**
  - <https://github.com/google/XNNPACK/issues/689>
  - <https://github.com/Maratyszcza/NNPACK>
  - <https://github.com/Maratyszcza/NNPACK/commits>
  - <https://raw.githubusercontent.com/Maratyszcza/NNPACK/HEAD/README.md>
  - <https://raw.githubusercontent.com/Maratyszcza/NNPACK/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/google/XNNPACK/HEAD/.bazelrc>
  - <https://raw.githubusercontent.com/google/XNNPACK/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Maratyszcza/NNPACK/HEAD/README.md>
  - <https://raw.githubusercontent.com/Maratyszcza/NNPACK/HEAD/include/nnpack.h>
  - <https://raw.githubusercontent.com/Maratyszcza/NNPACK/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Maratyszcza/NNPACK/HEAD/configure.py>
  - <https://raw.githubusercontent.com/Maratyszcza/NNPACK/HEAD/src/init.c>
  - <https://raw.githubusercontent.com/Maratyszcza/NNPACK/HEAD/src/convolution-inference.c>
  - <https://github.com/Maratyszcza/NNPACK/issues?q=is%3Aissue>
  - <https://github.com/Maratyszcza/NNPACK/issues/218>
  - <https://github.com/Maratyszcza/NNPACK/issues/221>
  - <https://github.com/Maratyszcza/NNPACK/issues/8>
  - <https://github.com/Maratyszcza/NNPACK/issues/168>
  - <https://github.com/pytorch/pytorch/issues/30622>
  - WebSearch snippets: NNPACK vs XNNPACK and PyTorch backend discussions
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/maratyszcza/nnpack`) · [data/wave8/enrich/raw/github_com_maratyszcza_nnpack.json](../../../data/wave8/enrich/raw/github_com_maratyszcza_nnpack.json) (enrichment confidence 0.75)

</details>
