# bilinear_filter_simd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🔴 abandoned

> Demo SSE4, AVX2 and AVX-512 bilinear sampler for packed 24-bit BGR images; 1.2-2.3x over its own scalar loop.

| | |
|---|---|
| **Beats** | plain scalar C++ bilinear filter in the same repo ('No SIMD') |
| **Claimed result** | Readme.md (2020-08-09, Xeon Platinum 8124M, c5.4xlarge EC2): single thread No SIMD 13.3 ms, SSE4 10.7 ms, AVX2 8.14 ms, AVX512 7.33 ms (1.24x, 1.63x, 1.81x, derived from page data); multi-thread No SIMD 1.25 ms vs AVX512 0.822 ms (1.52x, derived). Core i7-8700 (no AVX-512) single thread: No SIMD 7.64 ms, SSE4 5.26 ms, AVX2 4.26 ms (1.79x derived). Benchmarks.md 2020-08-11 run (same 16-thread machine, CPU line not printed): single thread No SIMD 13.3 ms vs AVX512 5.87 ms (2.27x derived), multi-thread 1.23 ms vs 0.743 ms (1.66x derived). |
| **Workload** | 1280x720 output from a 3840x2160 source through a per-pixel coordinate map: a 3x-downscale grid rotated 0.314 rad with cv::warpAffine and its default constant border, so about 27% of output pixels map to coordinate (0,0) and read the same cache-hot source pixel (derived from the transform in src/common.hpp); each timed iteration also allocates the 2.7 MB output cv::Mat3b. |
| **Metric** | latency |
| **Hardware** | Intel Xeon Platinum 8124M @ 3.00 GHz (AWS c5.4xlarge, 16 vCPUs) and Intel Core i7-8700 @ 3.20 GHz (12 threads) |
| **Compiler and flags** | CMakeLists.txt: CMAKE_BUILD_TYPE defaults to Release (CMake's GCC default -O3 -DNDEBUG), -march=native, -Wall -Wextra -Wpedantic, C++17. README lists GCC &gt;= 8 as a dependency; the compiler and version used for the 2020 runs are not stated. The ubuntu:23.04 Dockerfile was added in July 2023, after the benchmarks. |
| **Adoption** | 10 stars |
| **Last commit** | 2023-07-08 |
| **Links** | [repository](https://github.com/jviney/bilinear_filter_simd) · [benchmark](https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/Readme.md) |

## Verdict

The repo's Google Benchmark driver times its own fixed-point scalar loop against SSE4, AVX2 and AVX-512 versions of the same sampler on a rotated 3x-downscale map of a 3840x2160 photo (1280x720 output), Release build with -march=native and an unstated GCC. Readme.md (2020-08-09): Xeon Platinum 8124M on a c5.4xlarge, single thread 13.3 ms scalar vs 7.33 ms AVX-512 (1.81x) and multi-thread 1.25 vs 0.822 ms (1.52x); Core i7-8700, 7.64 vs 4.26 ms AVX2 (1.79x); the later Benchmarks.md run (2020-08-11) reached 5.87 ms (2.27x) and 0.743 ms (1.66x), all ratios derived from page data.

## Use it when

- As a reference for vectorising bilinear sampling of packed 24-bit BGR on x86 with pshufb/pmaddwd (study only: the repo has no licence).
- Arbitrary per-pixel sampling maps (rotation, affine warp, undistortion) on x86-64 with AVX2, with output widths that are multiples of 4 (8 for AVX-512).
- Single-threaded loops, where the SIMD gap over a fixed-point scalar loop is largest (1.8-2.3x on AVX-512, about 1.8-1.9x on AVX2).
- As a starting point for your own benchmark against cv::remap on your real maps before committing to a hand-written kernel.

## Skip it when

- Production code: there is no LICENSE file, so the code cannot be reused as is, and the demo has been inactive since 2023-07-08.
- Maps that touch or leave the image edge: x is never clamped and negative coordinates are not checked, so a sample at x &gt;= cols-1 blends in the first pixel of the next row and the 8-byte loads can run past the buffer.
- Plain image resizing or when OpenCV is already linked: cv::resize and cv::remap (both SIMD and multithreaded) were never timed against these kernels.
- Non-x86 targets (no NEON or scalar-portable SIMD path), RGBA, planar, 16-bit or float images, or output widths that are not a multiple of 4 or 8.
- Multi-threaded pipelines: with threads the SIMD kernels add only 1.25x (i7-8700, AVX2) to 1.5-1.7x (Xeon, AVX-512) because the gather is memory-bound.

## How it is fast

For 4 (AVX2) or 8 (AVX-512) output pixels at once it computes the four bilinear weights in 16-bit fixed point: floor, scale the fractions by 256, convert and pack, multiply x and y weights with mullo/mulhi and patch the 256\*256 overflow case with a blend. Each 2x2 neighbourhood is fetched as two unaligned 8-byte loads (top row and the row below), pshufb spreads the 24-bit pixels into 16-bit lanes, and pmaddwd plus phaddd form the weighted sums before packus narrows back to bytes and one 8+4-byte store writes 4 pixels. Coordinates are read with streaming loads. The gain stays modest because every output pixel still costs two scattered loads from a 24 MB source image; row threading gives about 10x where SIMD gives 1.2-2.3x.

## Compared with alternatives

It is the only bilinear image-sampling kernel among the catalogued SIMD entries, so pick it as worked x86 code for 24-bit BGR gather-and-blend; to write your own portable kernel use a licensed abstraction such as EVE or the Vector Class Library, and for ARM image kernels see ARM NEON Compositor. Pure SIMD shows the same per-pixel pattern with a larger (about 9.4x) gain on compute-bound shading.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Kernels: none beyond &lt;immintrin.h&gt; and &lt;stdint.h&gt;. Demo driver: OpenCV 4 (imread, warpAffine, parallel_for_), google/benchmark (git submodule), CMake 3.16. |
| **Minimum toolchain** | C++17, GCC &gt;= 8 per the README; built with -march=native (the 2023 bounds fix also uses the C++20 [[likely]] attribute inside the C++17 build). Docker image: ubuntu:23.04 build-essential. |
| **Platforms** | x86-64 only: SSE4.1 path, AVX2 required by the README, AVX-512 (F and BW intrinsics) path compiled only when __AVX512F__ is defined. |
| **Thread safety** | Kernels read const input and write disjoint output pixels, so row-partitioned calls are safe (the demo uses cv::parallel_for_); otherwise not documented. |
| **Drop-in for the baseline** | partial — same call shape as the repo's scalar plain::interpolate_multiple&lt;4&gt; and output within 3 levels per channel of it, but not a drop-in for cv::remap or cv::resize (no border modes, no tail handling, BGR8 only). |

## Gotchas

- The validation is not an equality check: mats_equivalent() in src/common.hpp accepts per-channel differences up to 3 (a TODO blames rounding). The SIMD paths round the scaled fractions with cvtps and multiply 16-bit weights, while the scalar baseline truncates float weights, so outputs are not bit-identical.
- The timed workload is a rotated remap, not the downscale the record describes: sampling_coordinates() rotates a 3x-downscale grid with cv::warpAffine and its default constant border, so about 27% of the 1280x720 outputs get coordinate (0,0) and all read the same cache-hot top-left pixel (share derived from the transform in src/common.hpp, not printed by the repo). That flatters every variant against a real full-image warp.
- Harness flaw behind the numbers: all published results (2020) predate commit b333369 (2021, alignas on the AVX2/AVX-512 stack store buffers that could crash) and commit d0f0187 (2023-07-08, 'Fix out of bounds access'), which added a compare-and-branch to ptr_below() in every variant's hot path; no post-fix numbers exist. The fix clamps only the row: its own test coordinate (2159, 3839) still makes the scalar path read pixel[1] 3 bytes past the image buffer and the SIMD 8-byte loads read 5 bytes past it (weight 0, so the output is unaffected, but it is an out-of-bounds read).
- Each timed iteration also allocates the 2.7 MB output cv::Mat3b, the multi-thread rows depend on an unstated OpenCV parallel_for_ backend, and the compiler used for the runs is never named.

## Known shortcomings

- No licence (reference); the baseline is its own scalar path only (no cv::resize timing), gains 1.2-2.3x; compiler unstated; the 2020 numbers predate the 2021 alignment fix and the 2023 out-of-bounds fix.
- The timed workload is not a plain downscale: the sampling map is a 3x-downscale grid rotated 0.314 rad by cv::warpAffine with constant border, so about 27% of outputs sample the cache-hot pixel (0,0) (derived from src/common.hpp). mats_equivalent allows a difference of 3 per channel, not equality. The 2020 numbers predate commit b333369 (alignas crash fix) and d0f0187 (ptr_below branch added to the hot path); no post-fix numbers exist. An out-of-bounds read remains after d0f0187: its own test coordinate (2159, 3839) reads 3 bytes past the image buffer in the scalar path and 5 bytes in the SIMD 8-byte loads. cv::remap is never timed.

## Caveats and trade-offs

No licence file in the repo, so the code is reference only. A demo project; benchmarks are from August 2020 and predate correctness fixes (2021 'Fix potential crash caused by incorrect alignment', 2023 'Fix out of bounds access' and 'Don't assume image data is tightly packed'). The only baseline is the author's own scalar code built with -march=native (auto-vectorisation possible); the repo links OpenCV but never times cv::resize, the obvious incumbent. SIMD gains are modest: 1.2x to 2.3x single-thread and 1.5x to 1.7x multi-threaded, where scalar multi-thread is already 10x faster than scalar single-thread. Outputs are checked for equality against the scalar result before benchmarking. [retier] No licence file in the repo, so the code is reference only. A demo project whose benchmarks (August 2020) predate commit b333369 (2021, alignas on the AVX2/AVX-512 stack buffers that could crash) and commit d0f0187 (2023-07-08, 'Fix out of bounds access', which added a compare-and-branch to ptr_below() in every variant's hot path); no post-fix numbers exist, and an out-of-bounds read remains after the fix (its own test coordinate (2159, 3839) reads 3 bytes past the image buffer in the scalar path and 5 bytes in the SIMD 8-byte loads). The timed workload is a rotated remap, not a plain downscale (about 27% of outputs sample the cache-hot pixel (0,0)), which flatters every variant against a real full-image warp. Validation is not an equality check: mats_equivalent() accepts per-channel differences up to 3 (the SIMD paths round with cvtps and 16-bit weights while the scalar baseline truncates float weights). The only baseline is the author's own scalar code built with -march=native; cv::remap and cv::resize are never timed. SIMD gains are modest: 1.2x to 2.3x single-thread and 1.5x to 1.7x multi-threaded; the multi-thread rows depend on an unstated OpenCV parallel_for_ backend; the compiler used for the runs is never named.

x86-64 only (SSE4, AVX2, AVX-512 paths); needs OpenCV 4 as a dependency of the demo; multithreading helps more than SIMD in the shown results.

## Maintenance

Abandoned demo (last commit 2023-07-08, 10 stars, no issues ever filed) with no licence file, so reference only; every published number comes from August 2020 code that predates the 2021 alignment fix and the 2023 bounds fix, and no OpenCV cv::remap or cv::resize baseline was ever timed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Public Google Benchmark driver (src/main.cpp, which also checks every SIMD output for equality against the scalar 'No SIMD' result) with CMake flags (Release, -march=native) and the CPU model (Xeon Platinum 8124M on a c5.4xlarge, Core i7-8700) printed, but the compiler used for the runs is never stated (README only lists 'GCC &gt;= 8' as a dependency), and the 2020 numbers predate a 2023 'Fix out of bounds access' commit and a 2021 'Fix potential crash caused by incorrect alignment' commit, so the later-fixed-bug rule caps it at C.
- **Verifier notes:** Numbers match Readme.md and Benchmarks.md exactly. Shortcomings: no licence (reference only), demo repo abandoned since 2023-07-08, own-scalar baseline only (no OpenCV cv::resize timing), compiler for the runs unstated, 2020 numbers predate the 2021 alignment fix and the 2023 out-of-bounds fix.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`, `workload`
- **Shortcomings recorded by:** verifier batch-110 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/Benchmarks.md>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/master/src/main.cpp>
  - <https://github.com/jviney/bilinear_filter_simd>
  - <https://github.com/jviney/bilinear_filter_simd/commits>
  - <https://github.com/jviney/bilinear_filter_simd/tree/master/src>
- **Sources the enricher read:**
  - <https://github.com/jviney/bilinear_filter_simd>
  - <https://github.com/jviney/bilinear_filter_simd/commits>
  - <https://github.com/jviney/bilinear_filter_simd/commits/master>
  - <https://github.com/jviney/bilinear_filter_simd/tree/master/src>
  - <https://github.com/jviney/bilinear_filter_simd/tree/master/src/interpolate>
  - <https://github.com/jviney/bilinear_filter_simd/tree/master/src/benchmark>
  - <https://github.com/jviney/bilinear_filter_simd/issues?q=is%3Aissue>
  - <https://github.com/jviney/bilinear_filter_simd/commit/d0f018735917c5fa6bdfe97818f0c27b661439cd>
  - <https://github.com/jviney/bilinear_filter_simd/commit/b333369f1718b972143eea7d9f788c019244f551>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/Benchmarks.md>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/common.hpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/interpolate/types.hpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/interpolate/bilinear_plain.hpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/interpolate/bilinear_sse4.hpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/interpolate/bilinear_avx2.hpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/interpolate/bilinear_avx512.hpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/benchmark/bilinear_plain_single_thread.hpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/benchmark/bilinear_plain_multi_thread.hpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/benchmark/bilinear_sse4_multi_thread.hpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/benchmark/bilinear_avx2_single_thread.hpp>
  - <https://raw.githubusercontent.com/jviney/bilinear_filter_simd/HEAD/src/benchmark/bilinear_avx512_multi_thread.hpp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jviney/bilinear_filter_simd`) · [data/wave13/enrich/raw/github_com_jviney_bilinear_filter_simd.json](../../../data/wave13/enrich/raw/github_com_jviney_bilinear_filter_simd.json) (enrichment confidence 0.8)

</details>
