# cvGPUSpeedup (OpenCV-style wrapper on the Fused Kernel Library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (CUDA)` · `Apache-2.0` · 🟢 active

> Header-only CUDA C++20 wrapper that fuses chains of OpenCV-CUDA-style preprocessing calls into one kernel; first-party 38x over OpenCV-CUDA.

| | |
|---|---|
| **Beats** | OpenCV-CUDA calls launched as separate kernels on one stream (per crop cv::cuda::GpuMat::convertTo and cv::cuda::resize INTER_LINEAR, then cv::cuda::multiply, cvtColor RGB2BGR, subtract, divide and split), against one fused cvGS::executeOperations kernel |
| **Claimed result** | '38x times faster' kernel execution for 50 crops of an image on an RTX A2000 12GB; '1/167th of the time' for variable-size crop, resize and normalize in the NSight Systems timelines; unit tests used as benchmarks 'show always positive speedups ranging from 2x to 10000x (in an RTX A2000)', larger the more small kernels are fused. |
| **Workload** | GPU pre-processing before a neural network: crop N detections (60x120 crops, batch 10 to 300 in the batchresize test; 50 in the README example) from a 3840x2160 8UC3 image, resize to 64x128 with INTER_LINEAR, convert to 32F, multiply, swap channels, subtract, divide and split into planar channels; OpenCV-CUDA runs a chain of separate kernels, cvGPUSpeedup one fused kernel. Timed with cudaEvents on the same stream over 100 iterations, inputs already on the GPU, no host transfers timed; outputs compared against OpenCV-CUDA. |
| **Metric** | latency |
| **Hardware** | NVIDIA RTX A2000 12GB GPU; host CPU not stated |
| **Compiler and flags** | README: nvcc -std=c++20; CMake build with -DENABLE_BENCHMARK=ON adds host -march=native -mtune=native on Linux (/arch:AVX2 with MSVC); tested with CUDA 11.8/12.1/12.3/12.8, VS 2022 v14.39-14.43 and OpenCV 4.8/4.9/4.11; which toolchain, OpenCV version and build type produced the quoted numbers is not stated |
| **Adoption** | 56 stars |
| **Last commit** | 2026-08-27 |
| **Links** | [repository](https://github.com/morousg/cvGPUSpeedup) · [benchmark](https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV) |

## Verdict

First-party only: the README states 38x kernel execution for 50 crops on an RTX A2000 12GB, 1/167th of the time in a user's Nsight timeline, and 2x to 10000x from unit tests run as benchmarks; no result files are committed, and the host CPU, OS/driver model, OpenCV build and build type are unstated. The public harness (tests/batchresize/test_batchresize_x_split3D.cu) times OpenCV-CUDA's per-crop chain (seven launches per crop, or a partly batched variant) against one fused kernel with cudaEvents on the same stream over 100 iterations, BATCH 10 to 300, with inputs already on the GPU. Because the OpenCV side is dominated by host launch rate, the ratio depends heavily on the unstated CPU and driver, and the CSV's first block is corrupted by the warm-up rows described above. The README's OpenCV and cvGS snippets are illustrative and not identical (different divide values; alpha folded into convertTo on one side and a separate multiply on the other).

## Use it when

- Images already live in cv::cuda::GpuMat on an NVIDIA GPU and an Nsight Systems trace shows long chains of tiny OpenCV-CUDA kernels (convertTo, resize, arithmetic, cvtColor, split) before a neural network.
- Crop-and-resize of many small detections per frame (tens to hundreds of crops of about 60x120 into 64x128, as in the batchresize test) followed by normalisation and channel split into a planar float tensor.
- Latency-bound real-time video pipelines where launch overhead and intermediate GpuMat allocations dominate preprocessing, including updating a temporal tensor of recent frames in one kernel.
- Projects already compiling .cu files with nvcc in C++20 that can accept template-heavy headers.

## Skip it when

- One large, bandwidth-bound operation (a single 4K resize or colour conversion): there is little launch overhead to remove, and the README itself says the speedup grows with the number and smallness of fused kernels.
- Interpolations other than bilinear or colour conversions beyond channel reorders and to-gray: cvGS restricts resize to cv::INTER_LINEAR and cvtColor to RGB/BGR/RGBA/BGRA swaps and \*2GRAY at compile time (no cubic, area, Lanczos, YUV or HSV in the wrapper).
- CPU-only, AMD, Intel or Apple GPUs: it is CUDA-only.
- Toolchains on CUDA 12.4 to 12.6, which the README says cannot compile it (an nvcc template-deduction bug), or codebases limited to C++17.
- Teams that need documentation or a stable API: the README says there is no documentation (read the tests) and that FKL is 'less than 1% complete'; the API is still changing (e.g. resize and warp overloads without an input GpuMat added in August 2026).

## How it is fast

Vertical kernel fusion: the whole operation list becomes one templated CUDA kernel, so intermediates stay in registers, the input is read once and the output written once, and there is one launch instead of one per operation and per crop. Horizontal fusion batches all crops of a std::array&lt;GpuMat, BATCH&gt; into the same grid (batch resize with a usedPlanes count), and executeOperations enables 'thread fusion' by default, where each thread processes several elements. The gain therefore comes mostly from removing launch overhead, idle GPU gaps and global-memory round trips between many tiny OpenCV-CUDA kernels, not from a faster resize algorithm.

## Compared with alternatives

The other color-and-resampling entries are mostly CPU libraries (fast_image_resize, libvips, CompV, kornia-rs, stb-image-resize-opt) or a stand-alone GPU kernel (CUDARGB2Y). Pick cvGPUSpeedup when your frames are already on an NVIDIA GPU in OpenCV-CUDA and the cost is a chain of small calls. Pick those CPU libraries when there is no NVIDIA GPU or the job is one large resize, where cvGPUSpeedup's fusion has little to remove.

## Integration

| | |
|---|---|
| **Form** | header-only (include/\*.cuh plus the FKL headers in the fkl submodule), compiled into your own .cu translation units by nvcc |
| **Dependencies** | CUDA toolkit; OpenCV 4.x built with the CUDA modules (the tests link core, cudaarithm, imgproc, cudafilters, cudaimgproc, cudawarping, imgcodecs); Fused Kernel Library submodule (header-only; the repo's CMake asks find_package(FKL 0.1.8)) |
| **Minimum toolchain** | C++20 with nvcc from CUDA 11.8, 12.1, 12.3 or 12.8 (12.4 to 12.6 unsupported); MSVC v14.39 to v14.43 on Windows; CMake 3.24 for the repo's tests and benchmarks; OpenCV 4.8, 4.9 or 4.11 tested (CI moved to OpenCV 4.14.0 in 2026) |
| **Platforms** | NVIDIA GPUs (tested on compute capability 7.5, 8.6 and 8.9) on x86-64 and ARM64 (Jetson Orin), Windows 11 and Ubuntu 22.04/24.04 including WSL2 |
| **Thread safety** | Not documented. Operation descriptors are plain value structs and executeOperations launches on the cv::cuda::Stream you pass; no global state was seen in the cvGS headers, so separate streams per thread should be safe, but this is not stated. |
| **Drop-in for the baseline** | partial: function names and argument types follow OpenCV-CUDA, but each call returns a descriptor that must be chained inside one cvGS::executeOperations call, BATCH and cv types are template parameters, outputs are written to a caller-provided tensor GpuMat, and only a subset of OpenCV-CUDA functionality exists |

## Gotchas

- Benchmark CSV flaw: in ENABLE_BENCHMARK builds the warm-up pass (warmup = true, loop breaks after one iteration) still calls processExecution, so each CSV starts with rows whose means are one cold iteration divided by 100 and whose variance and 'Mean Speedup' are averaged over 99 uninitialised std::array slots. Only the second block of rows (the real 100-iteration run) is meaningful; discard the first when reading your own results.
- The batch-resize tests that double as benchmarks fill the 3840x2160 input with a constant value, so the check against OpenCV-CUDA (absolute tolerance 1e-4 for float) validates the arithmetic chain but cannot catch wrong resize sampling coordinates; validate on your own images.
- Variable batch sizes were broken until PR #184 (merged 2025-11-11): cvGS::resize on a std::array of GpuMats did not forward usedPlanes and backgroundValue to fk::Resize, so code like the README's activeDetections example needs a version from after that fix.
- Batch size, OpenCV types and interpolation are compile-time template arguments, and thread fusion is on by default (executeOperations&lt;true&gt;); every new combination instantiates a new kernel, so expect long nvcc compile times and code growth.

## Known shortcomings

- Same-GPU comparison (RTX A2000) of an OpenCV-CUDA kernel chain against one fused kernel using cudaEvent stream time with transfers excluded (harness tests/batchresize/test_batchresize_x_split3D.cu); no result CSVs back the 38x, 167x or 2x-10000x figures and the host CPU is unstated; the arXiv 2508.07071 20931x is snippet-only. The repo moved to Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV.
- Enricher (e115, 2026-10-05): C stands. Measurement flaw in tests/testsCommon.cuh: the warmup pass still calls processExecution, so each benchmark CSV starts with rows whose mean is one cold iteration divided by 100 and whose variance and 'Mean Speedup' average 99 uninitialised slots; whether the README's 2x-10000x used them is unknown since no CSV is committed. The batchresize input is constant-filled, so the OpenCV check cannot catch resize-coordinate errors; variable-batch resize was broken until PR #184 (2025-11-11); the wrapper covers only INTER_LINEAR resize plus channel-swap/grey cvtColor; the OpenCV side is launch-bound; host CPU and OS unstated.

## Caveats and trade-offs

First-party numbers only. GPU against GPU on the same card (RTX A2000 12GB), so same hardware, but the gain comes from removing launch overhead and global-memory round trips of many tiny OpenCV-CUDA kernels; it is largest for long chains of small kernels and says nothing against a CPU resizer. The 38x figure is a README example and the 167x figure an NSight screenshot of a user's pipeline; neither has a committed result file, and the 2x to 10000x range comes from running unit tests with ENABLE_BENCHMARK whose CSV outputs are not in the repo. benchmarks/benchmark_CPU_OpenCV_vs_cvGS.cu measures host-side launch time (steady_clock without stream sync), not GPU execution, and benchmarks/benchmark_CPUandGPU_cvGS_vs_fk.cu compares cvGS with its own FKL core, not OpenCV. The authors' arXiv preprint 2508.07071 (The Fused Kernel Library) reports up to 20931x on an RTX 4090 against OpenCV-CUDA in synthetic vertical plus horizontal fusion and about 200x in production (search snippet only; arXiv blocked here). Host CPU unstated. The repository was transferred and renamed to Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV; the old morousg/cvGPUSpeedup URL redirects. It wraps the Fused Kernel Library (Libraries-Openly-Fused/FusedKernelLibrary) as a mandatory submodule.

NVIDIA GPU and nvcc only; C++20; the OpenCV-facing wrapper needs OpenCV built with the CUDA modules and mandatory Fused Kernel Library submodule (github.com/morousg/FusedKernelLibrary, header-only C++20); code must be restructured into one fused operation list executed with cvGS::executeOperations on a CUDA stream.

## Maintenance

Active (last commit 2026-08-27; CI moving to CUDA 13.4, CMake 4.4 and OpenCV 4.14), Apache-2.0 and header-only, so it is copyable. It is undocumented, its authors call it a demonstration platform, and the repo moved to Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV (the old morousg URL redirects).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states 38x for 50 crops on an RTX A2000 12GB, 1/167th of the time in an NSight timeline, and 2x to 10000x from unit tests run as benchmarks; the harness is public (tests/batchresize/test_batchresize_x_split3D.cu with cudaEvent timing macros in tests/testsCommon.cuh, which verify results against OpenCV-CUDA and write CSVs), but no result files are committed, the host CPU is unstated and the build optimisation level for the quoted runs is unstated, so first-party C.
- **Verifier notes:** Repo moved to https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV (old URL redirects); repo_url is not a correctable field, so consider updating it. The Fused Kernel Library core (Libraries-Openly-Fused/FusedKernelLibrary) is not filed separately in wave 10 merged.json, so this is not a duplicate. Metadata on github.com: Apache-2.0, 56 stars, 8 forks, 858 commits, last commit 2026-08-27, active.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party CSV harness
- **Pages the verifier opened:**
  - <https://github.com/morousg/cvGPUSpeedup>
  - <https://github.com/morousg/cvGPUSpeedup/commits>
  - <https://github.com/morousg/cvGPUSpeedup/tree/main/benchmarks>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/tree/main/tests>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/tree/main/tests/batchresize>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/README.md>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/benchmarks/benchmark_CPU_OpenCV_vs_cvGS.cu>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/benchmarks/benchmark_CPUandGPU_cvGS_vs_fk.cu>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/benchmarks/benchmark_image_resolution_MAD_loop.cu>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/benchmarks/cmake/benchmark.cmake>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/tests/main.h>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/tests/testsCommon.cuh>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/cmake/archflags.cmake>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/cmake/cuda_init.cmake>
  - <https://raw.githubusercontent.com/morousg/cvGPUSpeedup/HEAD/cmake/cmake_init.cmake>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/tests/batchresize/test_batchresize_x_split3D.cu>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/README.md>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/tests/main.h>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/tests/main.cpp>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/tests/testsCommon.cuh>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/tests/batchresize/test_batchresize_x_split3D.cu>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/benchmarks/verticalfusion/vertical_fusion_static_loop.cuh>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/cmake/discover_tests.cmake>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/cmake/archflags.cmake>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/cmake/cuda_init.cmake>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/cmake/libs/fkl.cmake>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/cmake/libs/opencv.cmake>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/include/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/include/cvGPUSpeedup.cuh>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/include/cvGPUSpeedupHelpers.cuh>
  - <https://raw.githubusercontent.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/HEAD/include/cv2cuda_types.cuh>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/tree/main/include>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/tree/main/benchmarks/verticalfusion>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/issues?q=is%3Aissue>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/issues/183>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/issues/169>
  - <https://github.com/Libraries-Openly-Fused/cvGPUSpeedup-FastOpenCV/pull/184>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/morousg/cvgpuspeedup`) · [data/wave10/enrich/raw/github_com_morousg_cvgpuspeedup.json](../../../data/wave10/enrich/raw/github_com_morousg_cvgpuspeedup.json) (enrichment confidence 0.75)

</details>
