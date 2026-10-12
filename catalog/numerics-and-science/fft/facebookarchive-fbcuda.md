# fbcuda / fbfft (archived)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA C++` · `BSD-3-Clause` · 🔴 abandoned

> Archived Facebook CUDA headers whose fbfft kernels batch tiny power-of-two FFTs; authors claim \~1.5x over cuFFT at CNN sizes.

| | |
|---|---|
| **Beats** | cuFFT (NVIDIA GPU FFT library) |
| **Claimed result** | Per the authors' paper (arXiv 1412.7580; text seen only as a search snippet, not on any opened page): fbfft gives over 1.5x speedup over cuFFT for the FFT sizes of interest in whole CNNs (reported mean 1.51x, sd 0.21, geometric mean 1.49x). Related opened data against a different baseline: soumith/convnet-benchmarks README layer-wise summary (last updated April 2015) lists fbfft SpatialConvolutionCuFFT at 256 ms total (101 fwd, 155 bwd) vs CuDNN R2 at 1019 ms; its later AlexNet table on Titan X lists fbfft 104 ms vs CuDNN R4 fp32 81 ms (fbfft slower). |
| **Workload** | Batched small power-of-two 1D and 2D FFTs on GPU as used for FFT-based convolution layers of CNNs (paper: Vasilache et al., 'Fast Convolutional Nets With fbfft: A GPU Performance Evaluation', ICLR 2015, arXiv 1412.7580), versus cuFFT. |
| **Metric** | throughput |
| **Adoption** | 284 stars, 57 forks; repository archived by Facebook on 2020-03-03 (read-only) |
| **Last commit** | 2018-05-29 |
| **Links** | [repository](https://github.com/facebookarchive/fbcuda) · [benchmark](https://arxiv.org/abs/1412.7580) |

## Verdict

The only fbfft-vs-cuFFT numbers come from the authors' ICLR 2015 paper (arXiv 1412.7580), seen here only as search snippets: over 1.5x faster than cuFFT (mean 1.51x, geometric mean 1.49x) for the batched FFT sizes used in CNNs, with the convolution experiments on an NVIDIA K40m; the cuFFT version, compiler flags and per-size tables were not seen and the repo has no benchmark. The co-author-maintained convnet-benchmarks compares convolutions with cuDNN, not FFTs with cuFFT: fbfft beat cuDNN R2 in April 2015 (256 vs 1019 ms layer-wise) and lost to cuDNN R4 fp32 on Titan X.

## Use it when

- Studying or porting warp-register FFT designs for very many tiny (2 to 256 point) single-precision transforms, e.g. tile-based FFT convolution.
- Keeping legacy Torch-7 fbcunn FFT convolutions running on Kepler, Maxwell or Pascal GPUs (compute capability 3.5 to 6.x) with an old CUDA toolkit.
- Batched R2C/C2R 1-D sizes 2 to 256, or 2-D up to 32x32, where the batch count is a multiple of the per-warp packing factor.
- As a reference design when benchmarking modern small-size GPU FFT kernels (VkFFT, TurboFFT, tcFFT) against an older warp-shuffle approach.

## Skip it when

- Any GPU newer than Volta: ComputeCapabilities.cuh stops with '#error Unknown __CUDA_ARCH__' above 700, and the code uses the non-_sync __shfl/__shfl_xor intrinsics, which NVIDIA deprecated in CUDA 9.0 and removed for compute capability 7.x targets.
- 1-D sizes above 256, 2-D sizes above 128, non-power-of-two lengths, double or half precision, complex 1-D input, or 3-D transforms: these assert or return UnsupportedSize, and the 2-D code itself says larger sizes 'are often slower than cufft'.
- Getting fast convolutions today: soumith/convnet-benchmarks (Titan X) shows fbfft convolutions slower than cuDNN R4 fp32 (AlexNet 104 vs 81 ms, OverFeat 342 vs 268 ms, VGG-A 1092 vs 529 ms).
- Production code that needs plans, a C ABI, tests or support: the repo is archived, ships no build files or fbfft tests (issue #2 asking for test files has been open since 2017), and the FFTIteratedConvolution.cuh prototypes are self-described as having 'bad performance'.
- Projects that cannot accept Facebook's 'Additional Grant of Patent Rights Version 2', which terminates on patent assertions against Facebook.

## How it is fast

Each transform lives in the registers of one warp: sizes up to 32 run a radix-2 decimation-in-frequency butterfly through warp shuffles (__shfl_xor), with 2 to 16 tiny FFTs packed into a single warp; sizes 64 to 256 keep several values per thread and do the butterflies across registers without shuffles, using shared memory only for bit reversal. The FFT size is a template parameter so every loop fully unrolls, twiddles come from a 128-entry precomputed single-precision table read through __ldg, and two real FFTs are packed into one complex FFT for R2C. The 2-D 32x32 path mixes Volkov-Kazian (2008) style hand-unrolled vertical FFTs with shuffle-based horizontal FFTs.

## Compared with alternatives

VkFFT (cuFFT parity on radix 2-13 lengths), TurboFFT and tcFFT (half precision) run on current GPUs and are the practical choices; pick fbfft only to study its warp-register design for tiny fp32 batches or to keep legacy fbcunn code alive, and use FlashFFTConv for FFT convolution on modern hardware.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | CUDA toolkit, glog (glog/logging.h), fbcuda's own DeviceTensor/Complex/CudaUtils headers under a cuda/ include prefix; the fbcunn consumer also needs Torch-7, Folly, fbthrift, thpp and fblualib |
| **Minimum toolchain** | nvcc with C++11 (constexpr used); fbcunn's INSTALL targets CUDA 7.5 on Ubuntu 14.04; GPU compute capability 3.5 or above (__ldg) |
| **Platforms** | NVIDIA GPUs sm_35 to sm_6x as written (sm_70 passes the arch check but loses the non-sync shuffles under CUDA 9+); Linux |
| **Thread safety** | not documented; kernels take a cudaStream_t, but initTwiddles() uses an unsynchronized function-static flag and copies the twiddle table only to the device current at the first call, so concurrent first calls or multi-GPU use look unsafe from the code |
| **Drop-in for the baseline** | no |

## Gotchas

- A batch count that is not a multiple of the per-warp packing factor drops to one FFT per warp (a TODO in FBFFT-inl.cuh), and the 2-D warp kernels assert that the batch divides evenly.
- Padding is only on the left/top; the caller must choose a 2^(k+1) transform when the padded input no longer fits in 2^k.
- Size limits are enforced partly with assert(), which compiles out under NDEBUG; always check the returned ErrorCode.
- The twiddle table has 128 complex entries, so 256 is a hard ceiling for 1-D without regenerating Twiddles.cuh.

## Known shortcomings

- Downgraded B to C: the fbfft paper (arXiv 1412.7580) could not be opened, so the ICLR venue and the 1.5x over cuFFT are snippet only; the repo has no cuFFT benchmark. The co-author's convnet-benchmarks compare fbfft convolution with cuDNN (not cuFFT): faster than cuDNN R2 (256 vs 1019 ms) but slower than cuDNN R4 on Titan X (104 vs 81 ms). Archived; Facebook PATENTS v2 grant attached.
- Will not compile for sm_75 or newer: ComputeCapabilities.cuh has '#error Unknown __CUDA_ARCH__' above 700 and the code uses the non-_sync __shfl/__shfl_xor that NVIDIA removed for 7.x targets. Sizes are capped at 256 (1-D) and 128 (2-D), and the 2-D code says larger sizes are often slower than cuFFT. initTwiddles() has an unsynchronized static flag and copies twiddles only to the first current device. No tests (issue #2 open since 2017). On convnet-benchmarks' Titan X, fbfft is slower than cuDNN R4 fp32 (AlexNet 104 vs 81 ms, VGG-A 1092 vs 529 ms). Paper 1412.7580 not opened (ar5iv, mlanthology blocked); tier stays C.

## Caveats and trade-offs

(1) Snippet only: the paper (arXiv 1412.7580, 'Fast Convolutional Nets With fbfft: A GPU Performance Evaluation') could not be opened here (arXiv, iclr.cc, ACM, IEEE egress-blocked), so the GPU model, cuFFT version, and whether the 1.51x mean is for FFT kernels alone are unverified; the ICLR 2015 venue is stated by the search record but not by any opened page (the fbcunn README links only arXiv). Retier to B if a session with arXiv access confirms the peer-reviewed venue and tables. (2) fbcuda holds only the kernels (fbfft/FBFFT.cuh, FBFFTCommon.cuh, FBFFTParameters.h and the 2D/inverse headers) with no cuFFT comparison or driver; the convolution modules and test/benchmark_fft.lua (a size sweep over SpatialConvolutionCuFFT with no published results) live in facebookarchive/fbcunn, archived 2022-01-13. (3) soumith/convnet-benchmarks (maintained by fbfft co-author Soumith Chintala, so not independent) shows fbfft convolutions beating CuDNN R2 in April 2015 (256 ms vs 1019 ms layer-wise total) but losing to CuDNN R4 fp32 on Titan X for AlexNet (104 ms vs 81 ms); that is convolution vs cuDNN, not FFT vs cuFFT. (4) 2014-2015 GPUs and cuFFT versions; modern cuFFT and cuDNN FFT/Winograd paths may have closed the gap. (5) cuFFT is not one of the assignment's baselines (FFTW, MKL FFT, KissFFT). (6) License is BSD-3-Clause plus Facebook's 'Additional Grant of Patent Rights Version 2' (PATENTS file, with a termination clause). (7) Repository archived 2020-03-03; last commit 2018-05-29 ('Upgrade - fbcode'), read from the github.com commits page.

Single-precision float only; power-of-two sizes only (fbfft1D asserts size &lt;= 256, fbfft2D works with a 2^k basis where right and bottom padding fills up to 2^k); real-input batched transforms with fixed templated kernels, so it targets small FFTs (the 'sizes of interest' for convnets), not large single transforms; headers only (.cuh) built with CUDA and Facebook's DeviceTensor utilities; no Python or C ABI. BSD plus an 'Additional Grant of Patent Rights Version 2' (PATENTS file) with a termination clause on patent assertions against Facebook; that grant is non-standard and not OSI-approved, so legal review is advised before copying.

## Maintenance

Archived read-only since 2020-03-03 (last commit 2018-05-29); BSD-3-Clause plus a non-OSI patent grant, header-only and small enough to vendor, but it needs patches (sync shuffles, the __CUDA_ARCH__ check) before it compiles for any GPU from Turing onward.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The fbfft-vs-cuFFT numbers (over 1.5x; mean 1.51x, geomean 1.49x) come only from a search snippet of the authors' own paper (arXiv 1412.7580, linked from the fbcunn README), which I could not open (arXiv and iclr.cc are egress-blocked), and no opened page states the paper's venue, so the B rests on neither an opened paper nor a confirmed peer-reviewed abstract; first-party snippet-only numbers are C. Neither fbcuda nor fbcunn publishes a cuFFT comparison (fbcunn test/benchmark_fft.lua only explores SpatialConvolutionCuFFT sizes), so A is unavailable.
- **Verifier notes:** Downgraded B to C per the snippet-only rule: I could not open the paper and no opened page confirms the venue or the 1.5x numbers. Metadata (284 stars, 57 forks, archived 2020-03-03, last commit 2018-05-29, BSD + patent grant) confirmed on github.com pages; convnet-benchmarks adds opened fbfft-vs-cuDNN numbers that cut both ways.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/facebookarchive/fbcuda>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/PATENTS>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFT.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFTCommon.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFTParameters.h>
  - <https://github.com/facebookarchive/fbcuda/commits/master>
  - <https://github.com/facebookarchive/fbcunn>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/README.md>
  - <https://github.com/facebookarchive/fbcunn/tree/master/test>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/master/test/benchmark_fft.lua>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/facebookarchive/fbcuda>
  - <https://github.com/facebookarchive/fbcuda/tree/master/fbfft>
  - <https://github.com/facebookarchive/fbcuda/issues>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/PATENTS>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFT.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFT-inl.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFT2D-inl.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFTCommon.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FBFFTParameters.h>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FFT2D32.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/FFTIteratedConvolution.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/fbfft/Twiddles.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/ComputeCapabilities.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/ShuffleTypes.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcuda/HEAD/CudaUtils.cuh>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/README.md>
  - <https://raw.githubusercontent.com/facebookarchive/fbcunn/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/HEAD/README.md>
  - <https://github.com/BVLC/caffe/issues/1989>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/facebookarchive/fbcuda`) · [data/wave8/enrich/raw/github_com_facebookarchive_fbcuda.json](../../../data/wave8/enrich/raw/github_com_facebookarchive_fbcuda.json) (enrichment confidence 0.7)

</details>
