# H264Sharp (native SIMD color converter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> AVX2/SSE4.1/NEON RGB&lt;-&gt;I420 converters inside a .NET OpenH264 wrapper; about 2.4x OpenCV cvtColor single-threaded, 3x multithreaded.

| | |
|---|---|
| **Beats** | OpenCV cv::cvtColor (RGB &lt;-&gt; YUV) |
| **Claimed result** | Ryzen 7 3700X: 1 thread 11919 ms (OpenCV) vs 4899 ms; 4 threads 3807 vs 1303 ms; 8 threads 2543 vs 822 ms; 16 threads 2462 vs 824 ms. Intel i7 10600U: 1 thread 11719 vs 6010 ms; 8 threads 3560 vs 1839 ms. README headline: up to 2.9x faster than OpenCV (the 8-thread Ryzen row works out to about 3.1x, derived from page data). |
| **Workload** | 1080p RGB -&gt; YUV and YUV -&gt; RGB conversion, 5000 iterations, with a custom thread pool, at 1 to 16 threads, H264Sharp native converter vs OpenCV. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3700X desktop and Intel i7 10600U laptop (as written in the README) |
| **Adoption** | 37 stars |
| **Last commit** | 2025-03-14 |
| **Links** | [repository](https://github.com/ReferenceType/H264Sharp) · [benchmark](https://github.com/ReferenceType/H264Sharp) |

## Verdict

README tables, measured on 1080p with 5000 iterations; each iteration is one YUV420-to-RGB plus one RGB-to-YUV420 call from C#, with matched thread counts. The OpenCV side is 4.10 through the OpenCvSharp4 4.10.0.20241108 Windows runtime; the H264Sharp side is a prebuilt native DLL whose compiler and flags are not stated. Ryzen 7 3700X: 4899 vs 11919 ms on one thread (2.43x) and 822 vs 2543 ms on 8 threads (3.09x). i7-10600U: 6010 vs 11719 ms (1.95x). Both libraries point-sample chroma, so they do the same work. H264Sharp computes in truncating 16-bit lanes where OpenCV uses rounded 32-bit lanes (outputs within 1-2 code values, derived from the source formulas), and its 16-thread row used at most 8 workers.

## Use it when

- .NET apps (WPF, Unity, MAUI) that already use H264Sharp and OpenH264 and convert camera or screen frames between RGB and I420 every frame.
- Real-time 720p/1080p capture-and-encode pipelines on x86-64 with AVX2, where frame widths are multiples of 32 (16 for the SSE and NEON paths) and heights are even.
- C++ projects that want a small MIT-licensed BT.601 RGB&lt;-&gt;I420 kernel to vendor: Rgb2YuvAVX2.cpp, Yuv2RgbAVX2.cpp and AVX2Common.h (plus the SSE/NEON variants and ThreadPool.h), built with Clang.
- Video-encoder input or preview display, where values that differ from OpenCV by 1-2 code values do not matter.

## Skip it when

- BT.709/BT.2020 matrices, full-range (JPEG) YUV, 10-bit, or 4:2:2/4:4:4 layouts: only 8-bit BT.601 limited-range 4:2:0 (plus NV12 input) is implemented.
- Bit-exact parity with OpenCV or libyuv, or best chroma quality. The arithmetic truncates instead of rounding, so computed from the source formulas, RGB to YUV lands 1 code value below OpenCV for about half of all inputs (mean bias about -0.5) and YUV to RGB is within +/-2. Chroma is point-sampled rather than averaged, so thin coloured edges alias.
- MSVC-only or GCC-only builds without changes: the code uses Clang/GCC extensions (__attribute__((target("avx2"))), a variable-length array in ThreadPool::ForRange, #pragma clang loop), and the CMake files hard-code clang/clang++ paths.
- Projects that need a maintained dependency: last commit 2025-03-14, 37 stars, open decoder-offset bugs (#20, #21), a reported AVX2 YUV-to-RGB crash on a QEMU Debian guest (#19, closed with no fix visible), and no macOS/iOS binaries (#17).

## How it is fast

It does BT.601 limited-range conversion in 16-bit fixed point with 8-bit coefficients: 66/129/25 &gt;&gt; 8 for Y, the halved chroma weights 56/47/9 and 19/37/56 &gt;&gt; 7, and 149/128 plus x/64 terms for the inverse. One 256-bit AVX2 register therefore holds 16 pixels, while OpenCV 4.10's universal-intrinsics path widens to 32-bit lanes with 20-bit coefficients and rounding. Interleaved pixels are split with byte shuffles and blends, two rows are processed per iteration, and chroma is point-sampled from the top-left pixel of each 2x2 block (as OpenCV does) using wrap-around 16-bit arithmetic and an unsaturated pack. YUV to RGB duplicates each chroma sample with one byte shuffle and packs with saturation. Row bands go to a custom spin-wait thread pool (or PPL on Windows), with runtime dispatch on x86 (AVX2, then SSE4.1, then scalar) and NEON on arm64.

## Compared with alternatives

Pick it when you are already in .NET with OpenH264 and want RGB&lt;-&gt;I420 at about 2.4-3x OpenCV with matched threads. For C++ code, libyuv (the incumbent, with many more formats and matrices) or the smaller xxYUV and descampsa/yuv2rgb are easier to adopt, and sparkyuv or yuvutils-rs cover more matrices and bit depths.

## Integration

| | |
|---|---|
| **Form** | shared lib (H264SharpNative DLL/.so with an extern "C" API, called from C# by P/Invoke; NuGet package H264Sharp); source-drop for C++ use of the converters |
| **Dependencies** | Cisco OpenH264 shared library for the codec part (loaded by name at runtime); the converter files need only the repo's ThreadPool.h, Logger and pch headers; the Windows build links 'synchronization' and can use PPL (concurrency::parallel_for) |
| **Minimum toolchain** | C++17 with Clang (CMakeLists hard-codes clang/clang++, CMakePresets uses LLVM clang++ on Windows, the vcxproj uses ClangCL); the C# wrapper targets .NET Standard and the benchmark targets net6.0 |
| **Platforms** | x86/x86-64 (runtime dispatch: AVX2, SSE4.1, scalar), arm64 NEON, other ARM scalar; prebuilt binaries for Windows, Linux and Android, none for macOS/iOS |
| **Thread safety** | not documented; the converter settings are one process-wide static (Converter::Config, changed by SetConfig) and multithreaded conversions share one static thread pool, so set the config once before converting from several threads |
| **Drop-in for the baseline** | no |

## Gotchas

- RGBX2YUV420 writes one contiguous I420 buffer starting at to-&gt;Y, with Y stride equal to the width and U then V directly after it; it ignores the U/V pointers and strides in YuvNative. YUV420ToRGB does honour strides.
- Width decides the path without telling you: AVX2 needs width % 32 == 0 and SSE/NEON need % 16, otherwise the scalar code runs. Images under 640x480 always run on one thread. With the custom pool, each worker needs at least 245,760 pixels (128 rows at 1080p), so 1080p uses at most 8 workers however many threads you request.
- The SIMD loops step two rows at a time and always touch row y+1, with no tail handling, so an odd height reads and writes one row past the planes (found in the source, not reported in any issue).
- Rgb2Yuv.cpp contains a 2x2-averaging chroma routine, but nothing calls it: the scalar, SSE, AVX2 and NEON paths all point-sample chroma. Release v1.6.0 notes a 'YUV luminance overflow' fix, and the README does not say which version produced its benchmark tables.

## Known shortcomings

- Benchmark is a C# harness (Examples/H264SharpBenchmark/Program.cs, OpenCvSharp4 4.10, matched Cv2.SetNumThreads) timing a prebuilt native DLL whose compiler and flags are not stated. 8-bit fixed-point coefficients, so output is not bit-identical to OpenCV cvtColor.
- Chroma is point-sampled in every path (the 2x2 averaging routine is unused), which matches OpenCV 4.10's RGB2YUV_I420, so the comparison is like-for-like (verifier note corrected); exhaustive formula check: RGB to YUV at most 1 code lower (about 50% of inputs, bias -0.5), YUV to RGB within 2. The custom pool caps 1080p at 8 workers (minimum chunk 245,760 px), so the 16-thread row is 8 against 16 threads. Odd heights make the SIMD loops touch row y+1 (out-of-bounds read and write); RGBX2YUV420 ignores the U and V pointers and strides; needs Clang (VLAs, target attributes); LICENSE.txt is an unfilled MIT template; v1.6.0 fixed a YUV luminance overflow and the README does not name the measured version.

## Caveats and trade-offs

Benchmark code is in the repo (Examples/H264SharpBenchmark/Program.cs): each iteration times a YUV420 to RGB plus RGB to YUV420 round trip on a 1080p image for both libraries, called from C# (OpenCvSharp4 4.10.0.20241108, i.e. OpenCV 4.10, Windows runtime), with Cv2.SetNumThreads set to the same thread count as the converter's custom thread pool, so threading is matched. The committed config.json uses 1000 iterations and 1 thread, not the README's 5000, and the README does not say which build of the native DLL (prebuilt H264SharpNative-win64.dll in the benchmark folder) or which compiler and flags were used. Outputs are not compared: the converter uses 8-bit fixed-point BT.601 coefficients (Rgb2Yuv.cpp) and averages each 2x2 block for chroma, while OpenCV's cvtColor uses higher-precision fixed point, so results are not bit-identical. The 'up to 2.9x' headline matches the 4-thread Ryzen row (2.92x); the 8-thread row is about 3.1x, the 16-thread row 3.0x, the 1-thread row 2.4x and the Intel laptop rows 1.5-2.1x (derived from page data). Primary language is C#; the C++ converter (H264SharpNative/Rgb2Yuv\*.cpp, Yuv2Rgb\*.cpp with SSE, AVX2 and NEON variants) is one component of an OpenH264 wrapper. Last commit 2025-03-14.

The repo is a .NET wrapper around Cisco OpenH264 whose native C++ folder H264SharpNative contains the RGB/YUV converters (Rgb2YuvAVX2.cpp, Yuv2RgbAVX2.cpp, SSE and NEON variants, thread pool); extracting just the converter for C++ use means taking those files. Formats are YUV &lt;-&gt; RGB/BGR/RGBA/BGRA only.

## Maintenance

Stale (last commit 2025-03-14, 37 stars) but MIT: LICENSE.txt is the MIT template with '[year] [fullname]' left unfilled, and the repo page reports MIT. The converter is about ten C++ files that can be vendored if you build with Clang.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README tables match the claim (Ryzen 7 3700X: 11919 vs 4899 ms at 1 thread, 2543 vs 822 ms at 8 threads; i7 10600U: 11719 vs 6010 ms at 1 thread). The benchmark code is public (Examples/H264SharpBenchmark/Program.cs, ConverterVersusOpenCV, against OpenCvSharp4 4.10.0.20241108), but the compiler and flags behind the measured native DLL are not stated (the benchmark folder ships a prebuilt H264SharpNative-win64.dll; repo build files offer ClangCL with AVX2 and a CMake -O3 -msse4.2 build), so first-party with partial methodology: C.
- **Verifier notes:** Numbers match the README; the record's caveat that benchmark code is absent was wrong (Examples/H264SharpBenchmark/Program.cs runs the OpenCV comparison with matched thread counts). Tier stays C because compiler/flags of the measured build are not stated. 37 stars, MIT per the repo page (LICENSE file path not found at /LICENSE), stale.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ReferenceType/H264Sharp>
  - <https://github.com/ReferenceType/H264Sharp/commits>
  - <https://github.com/ReferenceType/H264Sharp/tree/master/Examples>
  - <https://github.com/ReferenceType/H264Sharp/tree/master/Examples/H264SharpBenchmark>
  - <https://github.com/ReferenceType/H264Sharp/tree/master/H264SharpNative>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/HEAD/README.md>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/Examples/H264SharpBenchmark/Program.cs>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/Examples/H264SharpBenchmark/H264SharpBenchmark.csproj>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/Examples/H264SharpBenchmark/config.json>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/H264SharpNative.vcxproj>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Rgb2Yuv.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/CMakePresets.json>
- **Sources the enricher read:**
  - <https://github.com/ReferenceType/H264Sharp>
  - <https://github.com/ReferenceType/H264Sharp/commits/master>
  - <https://github.com/ReferenceType/H264Sharp/releases>
  - <https://github.com/ReferenceType/H264Sharp/issues?q=is%3Aissue>
  - <https://github.com/ReferenceType/H264Sharp/issues/19>
  - <https://github.com/ReferenceType/H264Sharp/issues/3>
  - <https://github.com/ReferenceType/H264Sharp/tree/master/H264SharpNative>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/README.md>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/LICENSE.txt>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/CMakePresets.json>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/Examples/H264SharpBenchmark/Program.cs>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/Examples/H264SharpBenchmark/config.json>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/Examples/H264SharpBenchmark/H264SharpBenchmark.csproj>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Converter.h>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Converter.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Exports.h>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/ImageTypes.h>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Rgb2Yuv.h>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Rgb2Yuv.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Rgb2YuvAVX2.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Rgb2YuvSSE.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Rgb2YuvNEON.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Yuv2Rgb.h>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Yuv2Rgb.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Yuv2RgbAVX2.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Yuv2RgbSSE2.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Yuv2RgbNEON.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/AVX2Common.h>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/ThreadPool.h>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/ThreadPool.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/Downscale.h>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/YuvNV12toYV12.cpp>
  - <https://raw.githubusercontent.com/ReferenceType/H264Sharp/master/H264SharpNative/dllmain.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.10.0/modules/imgproc/src/color_yuv.simd.hpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/referencetype/h264sharp`) · [data/wave10/enrich/raw/github_com_referencetype_h264sharp.json](../../../data/wave10/enrich/raw/github_com_referencetype_h264sharp.json) (enrichment confidence 0.75)

</details>
