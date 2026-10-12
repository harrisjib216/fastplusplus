# VkFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Header-only, cross-vendor GPU FFT library; matches cuFFT on smooth lengths and is \~1.5-3x faster on prime/Bluestein lengths.

| | |
|---|---|
| **Beats** | NVIDIA cuFFT (CUDA 11.7) and AMD rocFFT (ROCm 5.2) |
| **Claimed result** | README plot (FP64 batched 1D C2C, A100): radix 2-13 lengths are at parity (\~1250-1280 GB/s for both VkFFT and cuFFT); for Rader primes VkFFT reaches \~400-1250 GB/s vs cuFFT \~250-630 GB/s, and for Bluestein VkFFT beats cuFFT (cuFFT Bluestein drops to \~100-180 GB/s above length 2048), i.e. roughly 1.5-3x on non-smooth lengths (derived from page data). Paper: Bluestein 'faster than either cuFFT and rocFFT'. |
| **Workload** | Batched 1D FFTs of all lengths 2..4096 (500MB-1GB systems), double precision, on Nvidia A100 and AMD MI250; Rader/Bluestein prime sizes; zero-padded multidimensional |
| **Metric** | throughput |
| **Hardware** | Nvidia A100 40GB, AMD MI250 64GB |
| **Adoption** | 1.8k stars; IEEE Access 2023 (10.1109/ACCESS.2023.3242240) |
| **Last commit** | 2026-04-04 |
| **Links** | [repository](https://github.com/DTolm/VkFFT) · [benchmark](https://scispace.com/pdf/vkfft-a-performant-cross-platform-and-open-source-gpu-fft-sr243p64.pdf) |

## Verdict

The author's VkFFT_TestSuite (-vkfft 1001) batched 1D C2C FP64 transforms of every length 2-4096 into 500MB-1GB systems and reported achieved bandwidth on an A100 40GB vs cuFFT (CUDA 11.7) and an MI250 vs rocFFT (ROCm 5.2). Radix 2-13 lengths were at parity with cuFFT; Rader-prime and Bluestein lengths were roughly 1.5-3x faster (derived from page data). These are first-party numbers published in a peer-reviewed IEEE Access 2023 paper, with compiler and flags unstated.

## Use it when

- Batched FP64 or FP32 GPU FFTs whose lengths contain primes above 13 or are not smooth: on A100 cuFFT's Bluestein path falls to \~100-180 GB/s above length 2048 while VkFFT stays far higher
- One FFT dependency for Nvidia, AMD, Intel and Apple GPUs (and Raspberry Pi 4) on Windows, Linux and macOS, or for Vulkan/Metal apps that have no cuFFT
- Vulkan or Metal rendering/compute pipelines that want FFT dispatches appended straight into their own command buffer without extra synchronisation
- FFT-based convolution or cross-correlation and zero-padded open-boundary systems: the last FFT pass, kernel multiply and first iFFT pass are fused, and padded zeros are skipped (README: up to 2x faster than padding the array)
- GPU DCT I-IV, or FP64 transforms that need better-than-cuFFT accuracy (FP128-precomputed twiddles) or double-double precision

## Skip it when

- Power-of-two or 2-13-smooth lengths on Nvidia/AMD datacenter GPUs: the author's own A100 plot shows parity with cuFFT (\~1250-1280 GB/s), so you add a runtime compiler dependency for no speedup
- CPU-side FFTs: GPU only; use FFTW, PocketFFT or pffft
- Programs that create many short-lived plans of different sizes: every initializeVkFFT generates and runtime-compiles kernels unless you cache binaries with saveApplicationToString/loadApplicationFromString (not available on Metal)
- Intel iGPUs via Level Zero, Metal with NSAutoreleasePool, or Y-axis zero-padding on CUDA: open issues report non-deterministic wrong results (#228, v1.2.31-v1.3.4), a double free (#226) and wrong Y-padded results (#206)
- Multi-GPU split transforms: listed only as a future plan

## How it is fast

At plan time it generates GPU source specialised to the exact length, layout and device (shared-memory size, coalescing width, register file), with constants inlined and loops unrolled, then compiles it with the backend's runtime compiler (NVRTC, HIPRTC, glslang, OpenCL, clang+llvm-spirv). The core is a mixed-radix Stockham autosort FFT with radix 2-13 kernels that keeps whole sequences in shared memory, using the register file as extra storage ('register overutilization') so more sizes fit in a single upload; longer sequences use a Four-Step FFT. Primes from 17 up to the shared-memory limit are done in-kernel with Rader's algorithm (direct-multiplication or FFT-convolution variant), other lengths with Bluestein's algorithm using merged convolution and zero-padding to cut memory passes, which is where it beats cuFFT/rocFFT.

## Compared with alternatives

Pick VkFFT over tcFFT and TurboFFT when you need a maintained, general library: non-Nvidia GPUs, double precision, arbitrary or prime lengths, multidimensional, DCT or convolution. tcFFT (half precision on tensor cores) and TurboFFT (small sizes, fault tolerance) are CUDA research codes that can beat cuFFT in their narrow niches; for CPU FFTs use PocketFFT or pffft instead.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | backend runtime plus its runtime compiler: Vulkan + glslang/SPIRV, CUDA driver/runtime + NVRTC, HIP + HIPRTC, OpenCL, Level Zero + clang + llvm-spirv, or Metal + metal-cpp; quadmath for double-double; FFTW/cuFFT/rocFFT only for the benchmark suite |
| **Minimum toolchain** | C99-style C (also compiles as C++); Vulkan 1.0 (1.1 for half precision); ROCm 4.5+ unless VKFFT_OLD_ROCM is defined; CMake 3.11 for the test suite |
| **Platforms** | Nvidia, AMD, Intel, Apple and Raspberry Pi 4 GPUs; Windows, Linux, macOS |
| **Thread safety** | Not documented. Each VkFFTApplication is initialised once from zeroed memory and VkFFTAppend only records or launches kernels into the caller's command buffer, queue or stream (CUDA/HIP streams fixed at plan creation); concurrent use of one application is not addressed |
| **Drop-in for the baseline** | false — different API from cuFFT/rocFFT (one config struct + initializeVkFFT/VkFFTAppend/deleteVkFFT instead of cufftPlanMany/cufftExec\*); interleaved complex data is compatible but axis order is XYZ, the reverse of cuFFT/FFTW |

## Gotchas

- Structs must be zero-initialised (C API); initializeVkFFT on a non-zero app returns VKFFT_ERROR_NONZERO_APP_INITIALIZATION
- Inverse transforms are unnormalised by default (set normalize=1); multidimensional sizes are given fastest axis first (XYZ), opposite to FFTW/cuFFT
- Sequences beyond one shared-memory upload (e.g. \~4096 FP64 with 64KB shared memory, less for strided axes) switch to Four-Step FFT and need a tempBuffer the size of the main buffer; Bluestein needs extra buffers too
- Bug fixes since v1.3.4 (memory leaks #197, 2D zero-padding #201, convolution kernel compile failure #222) exist only on the develop branch; master/releases still carry them

## Known shortcomings

- Baseline cuFFT/rocFFT is a GPU library outside the category list; no gain on lengths that factor into radix 2-13 (level at \~1260 GB/s on A100); gains (\~1.5-3x, derived from plot) only on Rader/Bluestein lengths; author's own numbers; compiler and flags not stated; stale (last commit 2024-02-05).
- Master (v1.3.4) is Feb 2024 but the develop branch has unreleased fixes until 2026-04-04 (leaks #197, 2D zero-padding #201, conv kernel #222). Open correctness bugs: #228 Level Zero non-deterministic wrong results on Intel iGPU (v1.2.31-1.3.4), #206 Y-dim zero-padding wrong (CUDA), #226 Metal double free.

## Caveats and trade-offs

Baseline cuFFT/rocFFT is a GPU incumbent, not in the category list. Speedup applies to non-power-of-2/prime lengths; radix 2-13 lengths are at parity with cuFFT. First-party author measurements (peer-reviewed). Compiler/flags unstated. Last commit Feb 2024 (v1.3.4). Precision: with FP128 twiddles VkFFT is more precise than cuFFT/rocFFT in FP64; with FP32 twiddles slightly less precise in Bluestein/Rader. [retier] Last release v1.3.4 (Feb 2024); develop branch carries unreleased fixes until 2026-04-04.

GPU only (Vulkan/CUDA/HIP/OpenCL/Level Zero/Metal); header-only, runtime kernel compilation; C API usable from C++

## Maintenance

The last release (v1.3.4) and the last master commit are from Feb 2024, but the single author kept pushing bug fixes to the develop branch until 2026-04-04 and issues are still being filed, so it is slow-moving rather than abandoned. MIT-licensed and header-only, so it is easy to vendor; take develop if you hit the zero-padding or memory-leak bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Upgraded C-&gt;B: peer-reviewed paper (Tolmachev, IEEE Access 2023, DOI 10.1109/ACCESS.2023.3242240) reports the A100/CUDA 11.7 and MI250/ROCm 5.2 FP64 comparison vs cuFFT/rocFFT; benchmark harness (VkFFT_TestSuite, -vkfft 1001 / -cufft keys) is public in the repo, but compiler and flags are not stated, so not A.
- **Verifier notes:** Plots read from benchmark_plot/fp64_cuda_a100.png; kept README as benchmark_url. Paper read via scispace PDF mirror (IEEE page https://ieeexplore.ieee.org/document/10036080/ not opened). MIT, 1.8k stars, not fork/archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `last_commit`, `maintenance_status`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/DTolm/VkFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/DTolm/VkFFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/DTolm/VkFFT/master/benchmark_plot/fp64_cuda_a100.png>
  - <https://raw.githubusercontent.com/DTolm/VkFFT/master/benchmark_plot/fp64_hip_mi250.png>
  - <https://github.com/DTolm/VkFFT>
  - <https://github.com/DTolm/VkFFT/commits>
  - <https://scispace.com/pdf/vkfft-a-performant-cross-platform-and-open-source-gpu-fft-sr243p64.pdf>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/DTolm/VkFFT/HEAD/README.md>
  - <https://github.com/DTolm/VkFFT>
  - <https://github.com/DTolm/VkFFT/commits>
  - <https://github.com/DTolm/VkFFT/branches>
  - <https://github.com/DTolm/VkFFT/commits/develop>
  - <https://github.com/DTolm/VkFFT/tree/master/documentation>
  - <https://raw.githubusercontent.com/DTolm/VkFFT/HEAD/documentation/VkFFT_API_guide.tex>
  - <https://raw.githubusercontent.com/DTolm/VkFFT/HEAD/vkFFT/vkFFT.h>
  - <https://raw.githubusercontent.com/DTolm/VkFFT/HEAD/CMakeLists.txt>
  - <https://github.com/DTolm/VkFFT/issues>
  - <https://github.com/DTolm/VkFFT/issues?q=is%3Aissue+wrong+OR+incorrect+OR+bug>
  - <https://github.com/DTolm/VkFFT/issues/228>
  - <https://github.com/DTolm/VkFFT/issues/206>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dtolm/vkfft`) · [data/wave8/enrich/raw/github_com_dtolm_vkfft.json](../../../data/wave8/enrich/raw/github_com_dtolm_vkfft.json) (enrichment confidence 0.8)

</details>
