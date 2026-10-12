# CUDARGB2Y

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (CUDA)` · `MIT` · 🔴 abandoned

> 20-line CUDA kernel converting packed BGR8 already on the GPU to 8-bit gray; claims 5-30x over OpenCV's CPU cvtColor.

| | |
|---|---|
| **Beats** | OpenCV cv::cvtColor(image, out, CV_BGR2GRAY) on a host cv::Mat (CPU), as called in main.cpp; OpenCV version and build (SIMD, threading backend) unstated, though the CV_BGR2GRAY and CV_WINDOW_NORMAL C-API constants point to OpenCV 2.x/3.x |
| **Claimed result** | 'Roughly 5x to 30x faster than OpenCV's implementation, depending on your card.' (README and main.cpp header; no per-card numbers given) |
| **Workload** | RGB to 8-bit grayscale of the repo's test.jpg. GPU side: host high_resolution_clock wall time per call averaged over 2000 calls after 100 warm-ups, where each call is a kernel launch plus cudaDeviceSynchronize (so launch and sync overhead are included), with the input already uploaded to the GPU as a linear texture object and the result left on the device (host-to-device and device-to-host copies are outside the timed loop). CPU side: cv::cvtColor over 2000 calls after 100 warm-ups. The harness then checks every pixel agrees with OpenCV within 1. |
| **Metric** | latency |
| **Hardware** | not stated (no GPU or CPU model, no OpenCV version) |
| **Compiler and flags** | Makefile: .cu built with nvcc --use_fast_math -arch=sm_30 -O3 -std=c++11 -Xcompiler "-Ofast -march=native -funroll-all-loops ..."; main.cpp built with g++ -Ofast -std=gnu++17 -march=native -flto -funroll-all-loops; OpenCV linked as a prebuilt library, so these flags do not apply to the baseline |
| **Adoption** | 16 stars |
| **Last commit** | 2021-03-23 |
| **Links** | [repository](https://github.com/komrad36/CUDARGB2Y) · [benchmark](https://github.com/komrad36/CUDARGB2Y) |

## Verdict

The only performance figure is the README and source-header sentence 'Roughly 5x to 30x faster than OpenCV's implementation, depending on your card'; no run output, GPU, CPU or OpenCV version is recorded. main.cpp times the kernel launch plus cudaDeviceSynchronize with a host clock, averaging 2000 calls after 100 warm-ups, on the repo's test.jpg (1920x1080, decoded in this session), with the input already resident as a texture and the output left on the device. It compares this with cv::cvtColor(CV_BGR2GRAY) on the CPU over the same number of calls; OpenCV's own CUDA path (cv::cuda::cvtColor) is never measured, so the ratio is GPU against CPU without transfers. The harness then requires every pixel to be within 1 of OpenCV. An enricher brute force over all 16.7 million BGR colours shows the kernel's 6-bit weights (7, 38, 19 over 64, truncated) differ from OpenCV 4.x's 15-bit rounded coefficients (3735, 19235, 9798 over 32768) by up to 3: 49.9% of colours by 1, 7.5% by 2 and 1,438 by 3. On test.jpg the maximum difference is 1 (44% of pixels off by one), so the harness passes on its own image. Its claim that the default weights 'match OpenCV's default' holds only to about 1/64 precision.

## Use it when

- BGR8 frames that already sit in contiguous (unpitched) CUDA device memory and must stay there, where you need 8-bit luma as one step of a GPU pipeline.
- Batch or video workloads that already pay the host-to-device copy for other GPU stages, so the conversion adds only a sub-millisecond kernel per 1080p frame (no measured figure is recorded).
- Applications that tolerate small luma differences from OpenCV (display, thresholding, feature detection) rather than needing bit-exact cvtColor output.
- As a minimal, MIT-licensed template for a per-pixel CUDA kernel driven by texture objects, small enough to paste and adapt.

## Skip it when

- Images that live in host memory: the harness times the kernel with the input already uploaded and the result left on the device. A host caller also pays the copy of 3 bytes per pixel up (6.2 MB for the repo's 1920x1080 test.jpg) and 1 byte per pixel down, which is likely to cost more than OpenCV's whole CPU conversion; this end-to-end case is not measured.
- Pipelines that need OpenCV-identical gray values. The 6-bit truncated weights differ from OpenCV's 15-bit rounded coefficients by up to 3 levels: 7.5% of all 24-bit colours differ by 2 or more (enricher brute force), e.g. BGR (218, 0, 243) gives 95 against OpenCV's 98.
- Pitched GPU buffers (cudaMallocPitch, cv::cuda::GpuMat with row padding), RGB-ordered data or 4-channel BGRA input: it assumes tightly packed BGR rows, and RGB input swaps the R and B weights.
- Multi-stream or latency-sensitive GPU code: every call launches on the default stream and then runs cudaDeviceSynchronize, which waits for all device work, not just this kernel, and no CUDA error is checked or returned.
- Current toolchains without edits: the Makefile targets sm_30, which current CUDA toolkits cannot build for (per the verification record), and main.cpp uses OpenCV 2.x/3.x C-API constants (CV_BGR2GRAY, CV_WINDOW_NORMAL). The code has not changed since October 2016.

## How it is fast

There is no algorithmic trick; the gain is GPU memory bandwidth against a CPU. One thread handles one pixel (256-thread blocks). It reads its three bytes with three tex1Dfetch calls through the texture cache, computes a 6-bit fixed-point sum ((7\*B + 38\*G + 19\*R) &gt;&gt; 6, clamped to 255) and writes one byte. The kernel is memory-bound, moving 3 bytes in and 1 byte out per pixel, so newer cards with more bandwidth give the larger end of the claimed range.

## Compared with alternatives

Pick it only when the BGR frame is already on an NVIDIA GPU and you want a tiny standalone kernel to paste. If the image is on the CPU, the author's own RGB2Y (AVX2), CompV (about 7x over OpenCV for RGB24 to gray in its result file) or OpenCV itself avoid the PCIe round trip. If you chain OpenCV-CUDA operations, fusing the conversion into neighbouring steps, as cvGPUSpeedup does, saves more than a faster standalone kernel.

## Integration

| | |
|---|---|
| **Form** | source-drop (CUDARGB2Y.h plus CUDARGB2Y.cu; main.cpp is only the demo and harness) |
| **Dependencies** | CUDA runtime (texture objects). OpenCV (core, imgproc, imgcodecs, highgui, features2d) only for the demo harness. |
| **Minimum toolchain** | nvcc with -std=c++11 for the .cu file; the Makefile's ARCH=sm_30 must be raised for current CUDA. The harness needs a C++17 host compiler (-std=gnu++17) and OpenCV 2.x/3.x-era constants. |
| **Platforms** | NVIDIA GPUs only (CUDA texture objects, so compute capability 3.0 or newer). |
| **Thread safety** | not documented. The kernel itself is stateless, but each call ends in cudaDeviceSynchronize, which blocks the calling host thread until all outstanding work on the device has finished. |
| **Drop-in for the baseline** | no |

## Gotchas

- The README says custom weights are set in CUDARGB2Y.h, but the B_WEIGHT/G_WEIGHT/R_WEIGHT constants live in CUDARGB2Y.cu. Any weight is rounded to a multiple of 1/64 (0.114 becomes 7/64 = 0.109) and the sum is truncated, not rounded.
- The input must be bound as a single linear 1D texture, so it is bounded by the device's maxTexture1DLinear limit. main.cpp never checks cudaCreateTextureObject, cudaMalloc or the kernel launch, so a failed setup would time an empty synchronize loop, and only the later pixel check would notice.
- The harness's pixel check only prints an error and breaks out of the comparison loop. It still prints both timings, so a run with wrong output can still report a speedup.
- main.cpp sets display_image = true and blocks on cv::waitKey(0) after opening HighGUI windows, so it hangs or fails on a headless machine unless that flag is changed.

## Known shortcomings

- GPU against CPU: main.cpp times kernel launch plus cudaDeviceSynchronize against CPU cv::cvtColor with uploads and downloads untimed; no recorded output, GPU or CPU model, or OpenCV version (2.x/3.x constants); built for sm_30.
- Enricher (e111, 2026-10-05): the 6-bit truncated weights differ from OpenCV's conversion by up to 3 grey levels (7.5% of 24-bit colours off by 2 or more, e.g. BGR 218,0,243 gives 95 vs 98); the README's 'match OpenCV' holds only to 1/64 precision, and the 1920x1080 test.jpg has a max difference of 1 so the harness passes. Timing excludes the 6.2 MB upload and 2.1 MB download; there is no cv::cuda::cvtColor baseline; no CUDA error checks, and a check failure still prints timings. Tier C stays.

## Caveats and trade-offs

GPU against CPU: the kernel runs on an unnamed GPU with input already resident on the device, against OpenCV's CPU cvtColor on an unnamed CPU, so the ratio compares different hardware and excludes the upload/download a CPU caller would pay; it is not an end-to-end comparison. The 5x to 30x range is a README sentence with no recorded per-card output; GPU, CPU and OpenCV version are not stated, and whether OpenCV ran its SIMD and threaded cvtColor path depends on that unstated build. Timed GPU calls include launch plus cudaDeviceSynchronize, measured with a host clock. The kernel uses 6-bit fixed-point weights (scale 64, truncating shift) instead of OpenCV's higher-precision rounding, accepted by the harness's tolerance of 1. sm_30 build target is obsolete (removed from current CUDA toolkits). Code dates from Oct 2016; the only later commit (2021-03-23) added the MIT LICENSE. Sibling komrad36 RGB2Y (CPU) is at D after its README figure proved stale; this CUDA claim at least has a harness.

NVIDIA GPU only; two-file (CUDARGB2Y.h and .cu) drop-in; default weights match OpenCV, equal weighting optional; useful only when data already lives on the GPU.

## Maintenance

Abandoned: three commits, code last changed 2016-10-30 and an MIT LICENSE added 2021-03-23, 16 stars and 6 forks. Small enough to vendor, but it needs the sm_30 target and the OpenCV 2.x/3.x constants in the demo updated.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README and main.cpp header state 'Roughly 5x to 30x faster than OpenCV's implementation, depending on your card', and main.cpp is a real harness that times CUDARGB2Y and cv::cvtColor(CV_BGR2GRAY) over 2000 runs and checks pixels agree within 1; but no run output, GPU model, CPU model or OpenCV version is recorded, so this is first-party evidence with partial methodology (C).
- **Verifier notes:** Harness exists (main.cpp) and verifies output against OpenCV, so the claim is not unsupported, but there are no recorded results or hardware, so C stays. Metadata checked on github.com: MIT, 16 stars, 6 forks, 3 commits (2016-10-30 x2, 2021-03-23), not archived, not a fork.
- **Fields the verifier corrected:** `baseline`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party timing
- **Pages the verifier opened:**
  - <https://github.com/komrad36/CUDARGB2Y>
  - <https://github.com/komrad36/CUDARGB2Y/commits>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/Makefile>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/CUDARGB2Y.cu>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/CUDARGB2Y.h>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/komrad36/CUDARGB2Y>
  - <https://github.com/komrad36/CUDARGB2Y/commits>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/Makefile>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/CUDARGB2Y.cu>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/CUDARGB2Y.h>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/komrad36/CUDARGB2Y/HEAD/test.jpg>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/color_rgb.simd.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/color.simd_helpers.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/3.4/modules/imgproc/src/color.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/color.hpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/komrad36/cudargb2y`) · [data/wave10/enrich/raw/github_com_komrad36_cudargb2y.json](../../../data/wave10/enrich/raw/github_com_komrad36_cudargb2y.json) (enrichment confidence 0.8)

</details>
