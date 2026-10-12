# FlyCV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> ARM NEON-tuned C++ image library (colour conversion, resize, warps) with an OpenCV-like API; first-party phone demos beat OpenCV 1.16-2.19x.

| | |
|---|---|
| **Beats** | OpenCV (per-operator average speedup; operator list is in image charts, not text) |
| **Claimed result** | README_CN and README_EN say FlyCV is clearly faster than OpenCV with essentially the same output ('在执行效果基本一致的情况下，FlyCV的速度明显快于OpenCV'). The per-operator average-speedup charts for 6 phones are images on user-images.githubusercontent.com and were not read. Numbers are readable in the final frames of the repo's own demo GIFs (docs/assets; '平均速度' is the average time per frame in the same Android demo app, device not named). NV12 to BGR, 1920x1080: FlyCV 6.49 ms vs OpenCV 7.55 ms, 1.16x (derived from page data). BGR2RGBA with mask, 1920x1080: 9.69 ms vs 14.87 ms, 1.53x (derived from page data). 1080P cvt_color + warp_affine + resize pipeline: 29.6 ms vs 64.91 ms, 2.19x (derived from page data). |
| **Workload** | Android demo-app timings at 1920x1080 for NV12 to BGR, BGR2RGBA with mask, and a cvt_color + warp_affine + resize pipeline, plus README charts of per-operator average speedup over several resolutions on 6 high-, mid- and low-end phones (charts not read). |
| **Metric** | throughput |
| **Hardware** | Android phone(s), models not named; the README charts cover 6 phones of high, mid and low tier, also unnamed |
| **Adoption** | 595 stars |
| **Last commit** | 2023-06-02 |
| **Links** | [repository](https://github.com/PaddlePaddle/FlyCV) · [benchmark](https://github.com/PaddlePaddle/FlyCV/tree/develop/docs/assets) |

## Verdict

The only readable comparisons are first-party screen recordings of an Android demo app at 1920x1080: NV12 to BGR 6.49 vs 7.55 ms (1.16x), BGR to RGBA with mask 9.69 vs 14.87 ms (1.53x) and a cvt_color + warp_affine + resize pipeline 29.6 vs 64.91 ms (2.19x), with OpenCV version, build, thread counts and compiler flags unstated; Paddle's launch post (search snippet only) puts the pipeline run on a Snapdragon 636 and quotes average speedups of 1.36x (Snapdragon 888), 1.77x (835) and 4.38x (625). The public Android sample links only flycv_static and the benchmark/ code times FlyCV alone, so the OpenCV side cannot be reproduced from the repo.

## Use it when

- Android, iOS or ARM Linux camera pipelines that turn NV12/NV21 frames into BGR/RGB, resize and warp them before a neural-network runtime, especially on mid- and low-end SoCs where the first-party averages show the largest gains.
- Apps where OpenCV's binary size is the problem: per-operator CMake switches (WITH_FCV_RESIZE, WITH_FCV_COLOR_CONVERT, ...) build only what you use, and Paddle's launch post claims 1.3 MB versus 15.9 MB for OpenCV for common operators (search snippet only).
- Projects that already vendor another image library and need a custom namespace (-DFLYCV_NAMESPACE=...) to avoid symbol clashes.
- Preprocessing chains that match one of the fusion_api functions (BGR plus mask to RGBA, NV12 resize to BGR, normalize plus mean-subtract plus HWC-to-CHW reorder).

## Skip it when

- x86 servers and desktops: the Linux x86 build is plain C unless you pass -DENABLE_AVX=ON (which then adds -march=native), SIMD selection is compile-time with no runtime CPU detection, and no x86 comparison with OpenCV is published.
- When output must match OpenCV bit for bit: the README only promises essentially the same result, and kernels such as NV12 to BGR use 6-bit fixed-point coefficients with truncation.
- Workloads needing operators FlyCV lacks: no smoothing filters (issue #208), no drawContour (#213), limited copy_make_border modes (#207), no video I/O (#177); resize rejects INTER_NEAREST although the enum defines it.
- Several application threads calling FlyCV at once: issue #190 reports reproducible crashes inside the thread pool when multiple inference threads call it without a lock (closed without a visible fix).
- Long-lived products needing support: last commit 2023-06-02, recent issues unanswered, and release download links reported broken (#214, #216).

## How it is fast

The hot kernels are hand-written NEON inline assembly for aarch64 and armv7: NV12 to BGR, for example, converts 16 pixels on two rows per loop iteration with ld2/st3 (de)interleaving and 6-bit fixed-point BT.601 coefficients (Y 74.5, V 102, 52, U 25, 129, truncating shift by 6), trading some precision for fewer instructions. Resize has dedicated exact 2x and 4x downscale kernels and separable fixed-point horizontal/vertical passes. Rows are split across a built-in spin-then-block thread pool (default 2 threads on multi-core CPUs, changeable with set_thread_num), and fused APIs remove intermediate buffers and passes; Android builds use -Ofast -ffast-math.

## Compared with alternatives

Pick FlyCV over CompV or DeltaCV when the target is an ARM phone and you need a broad OpenCV-style preprocessing set (YUV conversion, resize, warps, normalize) in a small binary; for YUV conversion alone, sparkyuv or xxYUV have reproducible numbers against libyuv, and on x86 OpenCV itself or fast_image_resize are safer choices.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake, BUILD_SHARED_LIBS); prebuilt release packages exist but their links are reported broken |
| **Dependencies** | none for core and img_transform; libjpeg-turbo, libpng and zlib for the media_io imgcodecs module (on by default, can be switched off); googletest, Google Benchmark and gflags are downloaded only for tests, benchmarks and samples |
| **Minimum toolchain** | C++11; CMake 3.10 (3.12 with Xcode); Android NDK for Android builds |
| **Platforms** | Android armeabi-v7a/arm64-v8a and ARM Linux (NEON, optional SVE2 path), iOS, macOS (NEON on arm64, SSE/AVX on x86_64), Windows (SSE through AVX enabled by default), x86 Linux (scalar unless ENABLE_AVX), Emscripten/JS; Rockchip RV1109 code paths |
| **Thread safety** | All calls share a process-wide singleton thread pool with one job slot (set_thread_num is global); a call made while another job runs falls back to serial execution in the caller, and issue #190 reports crashes under concurrent use from several threads. |
| **Drop-in for the baseline** | partial — OpenCV-like function names (cvt_color, resize, warp_affine) but its own Mat type, image-type and enum codes, different argument conventions (issue #170 on warp_affine) and int return codes, so call sites must be ported |

## Gotchas

- Silent failures: cvt_color_neon logs and still returns 0 for unsupported conversion codes and for odd NV12 sizes (CHECK_CVT_SIZE returns from a void helper), and resize_cubic_neon leaves 4-channel RGBA/BGRA images untouched (the call is commented out) while returning 0, so INTER_CUBIC on RGBA on ARM yields an unwritten dst.
- Code reading (not tested): the NEON YUV-to-RGB assembly loops (NV12/NV21/I420 to BGR/RGB/BGRA/RGBA) decrement the 16-pixel block count only after running the loop body and have no nn &gt; 0 guard, unlike the BGR-to-YUV kernels; for widths under 16 the 32-bit count wraps and the loop runs far out of bounds.
- Colour order lives in the Mat type, so in-place swaps such as cvt_color(src, src, CVT_PA_BGR2PA_RGB) fail the destination type check (issue #205 reported no effect); Mat is constructed as (width, height), the reverse of OpenCV's (rows, cols).
- The Android toolchain file compiles the whole library with -Ofast -ffast-math, which can change float results (normalize, warp) and NaN handling.

## Known shortcomings

- Upgraded D to C on on-screen millisecond labels in the repo's docs/assets GIFs: NV12 to BGR 6.49 vs 7.55 ms (1.16x), BGR2RGBA with mask 9.69 vs 14.87 (1.53x), cvt_color plus warp_affine plus resize 29.6 vs 64.91 (2.19x), all derived; phone model, OpenCV build and flags unstated, and benchmark/ times FlyCV only. Six-phone charts on user-images.githubusercontent.com are unread (blocked).
- The OpenCV side is not reproducible: the public Android sample links only flycv_static and benchmark/ times FlyCV alone; the Paddle blog snippet names a Snapdragon 636 for the 29.6 versus 64.91 ms pipeline and averages of 1.36x, 1.77x and 4.38x on Snapdragon 888, 835 and 625. NV12-to-BGR NEON uses 6-bit fixed-point coefficients (not bit-exact with OpenCV); default 2-thread global pool; built -Ofast -ffast-math. Correctness bugs by code reading (not behind the numbers): the NEON YUV-to-RGB assembly loops lack an nn &gt; 0 guard so widths under 16 wrap the count (out of bounds); resize_cubic_neon skips RGBA/BGRA (call commented out) yet returns 0; cvt_color_neon returns 0 on unsupported codes and odd NV12 sizes; issue #190 (thread-pool crash with concurrent callers) closed with no visible fix.

## Caveats and trade-offs

The readable numbers come from screen recordings of the project's demo app (docs/assets/nv12_to_bgr.gif, bgr2rgba_with_mask.gif, Demo.gif). The FlyCV and OpenCV runs were recorded separately (on-screen clocks 20:05 and 20:03). The phone model, OpenCV version and build (NEON or carotene HAL, thread count), FlyCV thread count and compiler flags are not stated. The repo's benchmark/ code (Google Benchmark, e.g. benchmark/modules/img_transform/resize_bench.cpp) times FlyCV only and does not link OpenCV, so the comparison cannot be reproduced from public code. The 6-phone per-operator charts in the READMEs are hosted on user-images.githubusercontent.com and were not read; a reader with access could add per-operator ratios. The win for a single colour conversion is modest (1.16x for NV12 to BGR). Results measured on ARM phones may not carry over to x86. The last commit was 2023-06-02.

Optimised mainly for ARM (NEON); x86, RISC-V, GPU and DSP work is described as in progress. OpenCV-like API for migration, C, C++ and JavaScript interfaces, fine-grained build options for small binary size, custom-namespace build option to avoid symbol clashes. Targets Android, ARM Linux, macOS, Windows, iOS.

## Maintenance

Abandoned since 2023-06-02 with unanswered issues, but Apache-2.0 and modular enough to vendor selected operators; audit the NEON kernels for small-width and unsupported-type paths before shipping.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now C.
- **Tier reason:** Tier upgraded from D to C. The repo's own demo GIFs in docs/assets show on-screen average timings for FlyCV against OpenCV (1920x1080, phone not named). These are first-party numbers with no CPU model, compiler, flags or OpenCV build, and the public benchmark/ code times FlyCV only.
- **Verifier notes:** Tier upgraded from D to C. The GIFs on raw.githubusercontent.com hold readable average times (1.16x, 1.53x and 2.19x derived), so the 595-star notability question for tier D no longer applies. The 6-phone charts are still unread because of the image-host block.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/PaddlePaddle/FlyCV>
  - <https://github.com/PaddlePaddle/FlyCV/commits/develop>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/README_CN.md>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/README_EN.md>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/README.md>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/docs/assets>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/docs/assets/nv12_to_bgr.gif>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/docs/assets/bgr2rgba_with_mask.gif>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/docs/assets/Demo.gif>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/benchmark>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/benchmark/modules/img_transform>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/benchmark/modules/img_transform/resize_bench.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/benchmark/modules/img_transform/color_convert_bench.cpp>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/samples>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/README_EN.md>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/README.md>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/cmake/FCVPlatforms.cmake>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/cmake/FCVBuildList.cmake>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/cmake/FCVFindDependencies.cmake>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/cmake/FCVUtils.cmake>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/cmake/platform/android/android_arm.cmake>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/cmake/platform/linux/linux.cmake>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/cmake/platform/armlinux/armlinux.cmake>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/cmake/platform/macos/macos.cmake>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/cmake/platform/windows/windows.cmake>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/modules/img_transform/color_convert>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/modules/img_transform/color_convert/src>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/modules/img_transform/resize/src>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/modules/core/parallel>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/modules/core/parallel/src>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/color_convert/src/color_convert.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/color_convert/src/color_convert_arm.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/color_convert/src/color_convert_c.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/color_convert/src/color_convert_sse.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/color_convert/src/color_convert_avx.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/color_convert/interface/color_convert.h>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/color_convert/include/color_convert_common.h>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/resize/src/resize.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/resize/src/resize_arm.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/resize/src/resize_c.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/resize/src/resize_avx.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/resize/src/resize_sse.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/img_transform/resize/interface/resize.h>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/core/parallel/interface/parallel.h>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/core/parallel/src/parallel.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/core/parallel/src/parallel_manager.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/core/parallel/src/parallel_handler_thread.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/core/parallel/src/thread_pool.cpp>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/core/parallel/include/thread_pool.h>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/fusion_api/bgr_to_rgba_with_mask/interface/bgr_to_rgba_with_mask.h>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/core/mat/interface/mat.h>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/modules/core/base/interface/basic_types.h>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/samples>
  - <https://github.com/PaddlePaddle/FlyCV/tree/develop/samples/android/image-transform>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/samples/android/image-transform/app/build.gradle>
  - <https://raw.githubusercontent.com/PaddlePaddle/FlyCV/develop/samples/android/image-transform/app/CMakeLists.txt>
  - <https://github.com/PaddlePaddle/FlyCV/issues?q=is%3Aissue>
  - <https://github.com/PaddlePaddle/FlyCV/issues/190>
  - <https://github.com/PaddlePaddle/FlyCV/issues/205>
  - <https://github.com/PaddlePaddle/FlyCV/issues/215>
  - <https://github.com/PaddlePaddle/FlyCV/commits/develop>
  - WebSearch snippet: 'FlyCV OpenCV 加速比 resize cvtColor 手机 benchmark' (blog.csdn.net/PaddlePaddle/article/details/128710783, zhuanlan.zhihu.com/p/599840710; pages not opened, blogs blocked)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/paddlepaddle/flycv`) · [data/wave10/enrich/raw/github_com_paddlepaddle_flycv.json](../../../data/wave10/enrich/raw/github_com_paddlepaddle_flycv.json) (enrichment confidence 0.7)

</details>
