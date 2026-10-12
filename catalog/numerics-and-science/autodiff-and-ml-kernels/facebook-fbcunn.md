# fbfft / fbcunn (FFT-based convolution for Torch7)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Lua/CUDA C++ (Torch7 extension)` · `BSD-3-Clause` · 🔴 abandoned

> Archived Torch7 CUDA module set whose FFT spatial convolution ran about 4x faster than cuDNN R2 on large-kernel layers in 2015.

| | |
|---|---|
| **Beats** | NVIDIA cuDNN R2 (layer-wise table); cuDNN R4 appears in the full-network tables where fbfft is slower |
| **Claimed result** | convnet-benchmarks layer-wise table (last updated April 2015): fbfft SpatialConvolutionCuFFT 256 ms (forward 101, backward 155) vs CuDNN R2 1019 ms (forward 269, backward 750), about 4x (derived from page data). In the full-network tables fbfft also beats CuDNN R2 (AlexNet 104 vs 231 ms, Overfeat-fast 342 vs 810 ms, OxfordNet 1092 vs 1099 ms) but loses to CuDNN R4 fp32 (81, 268, 529 ms). fbcunn README: temporal convolutions '1.5x to 10x faster compared to Torch's cunn implementations'. Paper (arXiv 1412.7580, via WebSearch summary only): faster than cuDNN for many common layers, up to 23.5x for a synthetic kernel configuration, and fbfft over 1.5x faster than cuFFT. |
| **Workload** | Spatial convolution layer forward+backward (fprop, bprop, accGrad) timing from the convnet-benchmarks layer-wise table, last updated April 2015. |
| **Metric** | latency |
| **Hardware** | 6-core Intel Core i7-5930K CPU @ 3.50GHz + NVIDIA Titan X + Ubuntu 14.04 x86_64 (README header; the layer-wise section is marked last updated April 2015 and a legacy table was run on Titan Black) |
| **Adoption** | 1.1k stars, 242 forks; Facebook AI Research; repository moved to facebookarchive/fbcunn and archived 2022-01-13; independent suite convnet-benchmarks has 2.7k stars |
| **Last commit** | 2017-07-21 |
| **Links** | [repository](https://github.com/facebook/fbcunn) · [benchmark](https://github.com/soumith/convnet-benchmarks) |

## Verdict

soumith/convnet-benchmarks (independent; Torch7 harness, 10 timed steps after dry runs with cutorch.synchronize) layer-wise table, last updated April 2015 on a Core i7-5930K + Titan X, gives fbfft 256 ms (101 forward, 155 backward) for five stride-1 layers (kernels 11x11, 9x9, 9x9, 7x7, 3x3, batch 128) vs 1019 ms (269 / 750) for cuDNN R2, about 4x. The same suite's whole-network tables show it ahead of cuDNN R2 but behind cuDNN R4 fp32 by 1.3x to 2.1x; compiler, flags and CUDA/cuDNN builds are not given.

## Use it when

- Reproducing or studying 2015-era FFT convolution results; the code is a readable reference for warp-shuffle FFTs and frequency-domain convolution (BSD-3-Clause)
- Stride-1 convolutions with large kernels (7x7 to 11x11) and many feature maps, which is where it won: in the layer-wise table its backward pass for the 9x9 layer took 45 ms vs 401 ms for cuDNN R2
- Mining the fbfft kernels for a small-size batched GPU FFT (sizes up to 256) in a new project, if you are willing to port them off Torch7 and old CUDA

## Skip it when

- Any current training or inference stack: it is a Torch7/Lua extension pinned to CUDA 7.5, sm_35, Folly, fbthrift, thpp and fblualib, and the repository was archived in 2022
- Modern cuDNN baselines: in the same benchmark suite whole networks were slower than cuDNN R4 fp32 (AlexNet 104 vs 81 ms, Overfeat-fast 342 vs 268 ms, OxfordNet 1092 vs 529 ms) and slower than Nervana neon
- Strided convolutions: both FFT modules assert stride 1 ('fft only supports stride-1 convolutions atm')
- Layers with few input planes or memory-tight GPUs: on the first layer (3 -&gt; 96 planes, 11x11) its forward pass took 57 ms vs 36 ms for cuda-convnet2 and 56 ms for cuDNN R2, and padding every plane to a power of two inflates buffer memory
- fp16 or fp64 models: the module code assumes 4-byte float elements

## How it is fast

Convolution is done in the frequency domain: inputs, weights and gradients are zero-padded to a power-of-two size, transformed with batched FFTs, combined with batched complex matrix products (a transposed cuBLAS GEMM path, fbTransposeMM, is the default strategy) and transformed back, so cost depends little on kernel size. fbfft itself is a hand-written decimation-in-frequency FFT that keeps each transform in registers and exchanges data with warp shuffles, packing several small FFTs into one warp; it supports power-of-two sizes 2 to 256. The FFT path can also pad implicitly inside the transform instead of materialising padded copies, which the cuFFT path cannot.

## Compared with alternatives

Pick it only for historical or reference use: among GPU convolution siblings, Nervana neon beat both fbfft and cuDNN R4 in the same suite, and modern work should start from current cuDNN-backed frameworks; on CPU, NNPACK is the catalogued FFT/Winograd convolution library.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Torch7 (with a patched nn branch), cutorch, cudnn.torch, fbtorch, fbnn, Folly, fbthrift, thpp, fblualib, glog, cuFFT, cuBLAS; fbfft kernels from fbcuda |
| **Minimum toolchain** | CUDA 7.5 (CMake requires it), nvcc -arch=sm_35, C++11, Ubuntu 14.04-era toolchain; installed with luarocks |
| **Platforms** | Linux x86-64 with an NVIDIA GPU of compute capability 3.5 or higher |
| **Thread safety** | not documented; FFT buffers, streams and cuBLAS handles are kept in class-level maps shared by all module instances, and a source comment says the instance counter is not incremented atomically for multi-threaded use |
| **Drop-in for the baseline** | partial: drop-in for nn.SpatialConvolution inside Torch7 when stride is 1 (and, for the cuFFT module, padding is 0); not a cuDNN API replacement |

## Gotchas

- The rows labelled fbfft in convnet-benchmarks link to the SpatialConvolutionCuFFT class, whose current source sets fftImplementation = 'cufft'; which FFT backend produced the April 2015 numbers is not stated on the page
- fbfft returns UnsupportedSize for transform sizes other than powers of two up to 256 (asserts size &lt;= 256), so very large feature maps fall back to cuFFT or fail
- SpatialConvolutionCuFFT rejects implicit padding ('cufft does not support implicit padding!'); pad the input explicitly or use the FBFFT module
- License is BSD-3-Clause plus Facebook's Additional Grant of Patent Rights Version 2, whose patent grant has a termination clause

## Known shortcomings

- Loses to cuDNN R4; repo moved to facebookarchive; BSD plus PATENTS rider; Torch7-era.
- convnet-benchmarks 'fbfft' rows link to SpatialConvolutionCuFFT, whose current source uses cuFFT, so the page does not show whether fbfft kernels produced the 2015 numbers. Stride 1 only, float32 only, fbfft sizes power of 2 up to 256; needs CUDA 7.5/sm_35 plus Folly/fbthrift. Lost first-layer forward to cuda-convnet2 (57 vs 36 ms). Archived.

## Caveats and trade-offs

The win is against cuDNN R2 (2014-2015 era). In the same suite's full-network tables fbfft loses to cuDNN R4: AlexNet 104 ms vs 81 ms, Overfeat-fast 342 ms vs 268 ms, OxfordNet 1092 ms vs 529 ms (fp32). Old hardware (Titan X, Maxwell). cuDNN rows go through Torch bindings. CPU and GPU are named, but compiler, flags and CUDA versions are not, so not tier A. Torch7/Lua extension that no longer builds against current toolchains (last code commit 2017-07-21, archived). BSD-3-Clause plus Facebook's 'Additional Grant of Patent Rights Version 2' (PATENTS file, with a termination clause).

FFT convolution needs extra memory and wins only for some kernel/feature-map sizes; Torch7 (Lua) only, archived, ships with an extra PATENTS grant file.

## Maintenance

Abandoned: last code commit 2017-07-21, moved to facebookarchive/fbcunn and archived 2022-01-13; BSD-3-Clause with a patent grant, usable only as reference code since it does not build against current CUDA, Torch or PyTorch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** soumith/convnet-benchmarks (2.7k stars, independent well-known suite) layer-wise table shows fbfft 256 ms (101 fwd / 155 bwd) vs CuDNN R2 1019 ms (269 / 750), with harness code in its torch7/ directory and the machine named (i7-5930K + Titan X), but no compiler, flags or CUDA/cuDNN build details, so not A. The fbfft paper (arXiv 1412.7580, ICLR 2015) also reports wins over cuDNN (seen only through a WebSearch summary).
- **Verifier notes:** All table numbers verified on the convnet-benchmarks README. The repository URL now redirects to facebookarchive/fbcunn; metadata otherwise matches (BSD-3-Clause + PATENTS, 1.1k stars, archived 2022-01-13, last commit 2017-07-21). The paper (arxiv.org) was not opened; its 23.5x figure comes from a WebSearch summary.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/soumith/convnet-benchmarks>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/HEAD/README.md>
  - <https://github.com/facebook/fbcunn>
  - <https://raw.githubusercontent.com/facebook/fbcunn/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebook/fbcunn/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/facebook/fbcunn/HEAD/PATENTS>
  - <https://github.com/facebook/fbcunn/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/PATENTS>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/CMakeLists.txt>
  - <https://github.com/facebookarchive/fbcunn/tree/master/src/fft>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/src/fft/CuFFTStrategy.h>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/src/fft/SpatialConvolutionCuFFT.cpp>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/src/fft/SpatialConvolutionCuFFTTuner.cpp>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/src/fft/FBFFTHost.cpp>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/src/fft/FBFFTDevice.cu>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/fbcunn/SpatialConvolutionCuFFT.lua>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/fbcunn/SpatialConvolutionFBFFT.lua>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/fbcunn/SpatialConvolutionFFT.lua>
  - https://github.com/facebookarchive/fbcunn/issues?q=is%3Aissue (no issues listed)
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFT.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFT-inl.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFTCommon.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFTParameters.h>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/HEAD/README.md>
  - <https://github.com/soumith/convnet-benchmarks/tree/master/torch7>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/HEAD/torch7/layerwise_benchmarks/benchmark.lua>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/HEAD/torch7/imagenet_winners/benchmark.lua>
  - https://ar5iv.labs.arxiv.org/html/1412.7580 (egress-blocked; paper claims taken from a WebSearch summary only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/facebook/fbcunn`) · [data/wave8/enrich/raw/github_com_facebook_fbcunn.json](../../../data/wave8/enrich/raw/github_com_facebook_fbcunn.json) (enrichment confidence 0.75)

</details>
