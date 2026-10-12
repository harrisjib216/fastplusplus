# CompV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> GPL C++ computer-vision library with hand-written x86/ARM assembly; first-party numbers show 3-11x over OpenCV colour conversion and bilinear resize.

| | |
|---|---|
| **Beats** | OpenCV (cv::resize bilinear; cvtColor CV_RGB2GRAY, CV_YUV2RGB_I420, CV_RGB2HSV) |
| **Claimed result** | From the result file (10k iterations, 1282x720): RGB24 to Gray 449 ms vs OpenCV 3086 ms ('680%, almost 7 times'); YUV420P to RGB24 968 vs 5919 ms ('611%, 6 times'); RGB24 to HSV 2137 vs 15709 ms ('735%, 7 times'); YUV420P to HSV 3045 vs 32920 ms ('almost 11 times'; OpenCV needs two calls). Bilinear scaling 1282x720 to 1064x597: 1474 ms (mt, avx2) vs OpenCV 4148 ms ('281%, almost 3 times'). CompV's mt plain C++ (2645 ms) also beats OpenCV, but its single-thread AVX2 (5435 ms) does not. |
| **Workload** | 10,000 iterations on a 1282x720 image: RGB24 to grayscale, YUV420P to RGB24, RGB24 to HSV (CV_RGB2GRAY, CV_YUV2RGB_I420, CV_RGB2HSV on the OpenCV side), and bilinear down-scaling to 1064x597. Per tests/image/scale.cxx (factor 0.83, COMPV_SUBTYPE_PIXELS_Y), scaling runs on an 8-bit grayscale image. CompV uses hand-written assembly, SSE/AVX and its own thread pool (8 threads on this machine). |
| **Metric** | latency |
| **Hardware** | Intel Core i7-4790K @ 4.00GHz (8 CPUs), Apple iMac15,1 running Windows 8 Pro 64-bit |
| **Adoption** | 212 stars, 46 forks; code used in the vendor's commercial SDKs |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/DoubangoTelecom/compv) · [benchmark](<https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/speed_compare%20(core%20i7%20quad%404ghz).txt>) |

## Verdict

One first-party result file (last edited 2019) on an Intel Core i7-4790K iMac running Windows 8 reports 10,000 iterations at 1282x720: RGB24 to gray 449 vs 3086 ms (6.9x), YUV420P to RGB24 968 vs 5919 ms (6.1x), RGB24 to HSV 2137 vs 15709 ms (7.4x), YUV420P to HSV 3045 vs 32920 ms (10.8x), and 8-bit grayscale bilinear 1282x720 to 1064x597 1474 ms (8 threads, AVX2) vs 4148 ms (2.8x), all ratios derived from page data. OpenCV's version, build, harness and compiler flags are unpublished, and the CompV side computes lower-precision, differently defined outputs (7-bit limited-range gray, 5-bit YUV coefficients, 0-255 hue, 8-bit bilinear with acknowledged drift), so the rows are not like-for-like in output.

## Use it when

- A GPL-3.0 (or commercially licensed from Doubango) pipeline on 8-bit grayscale frames where CompV's own resize, threshold, Canny, FAST, CCL or MSER chain replaces several OpenCV calls.
- Studio-range BT.601 luma is acceptable or wanted: CompV's 'grayscale' from RGB is limited-range Y (16-235), the same as the Y plane of a YUV conversion, not OpenCV's full-range 0.299R+0.587G+0.114B.
- Real-time HD camera pipelines on x86 AVX2 or ARM NEON (Android, iOS, Raspberry Pi, Jetson) where a few levels of rounding error per pixel do not matter and multithreading across rows is available.
- Building pyramids or downscaled detection inputs, where the 8-bit fixed-point bilinear scaler's small geometric drift and slight darkening are tolerable.

## Skip it when

- When output must match OpenCV: CompV's RGB-to-gray is limited-range Y with truncation (white maps to 237, not 255), YUV-to-RGB uses 5-bit coefficients (1.156 instead of 1.164 for Y), HSV hue spans 0-255 (OpenCV CV_RGB2HSV uses 0-180), and bilinear resize is neither centre-aligned nor bit-exact.
- Quality-sensitive resizing: the bilinear scaler uses 8-bit fractional steps, which the maintainer's open issue #176 says 'produces drift'. For 1282x720 to 1064x597 the step is quantized to 1.203125 instead of 1.2049, so the last column samples source x 1278.9 instead of OpenCV's 1280.9 (derived from the code). Weights sum to 255/256, so a flat white image comes out at 253.
- Colour (RGB) resizing: CompVImageScaleBilinear::process returns NOT_IMPLEMENTED unless the input is 8u with one plane.
- Single-threaded use: the result file's own single-thread AVX2 bilinear time (5435 ms) is slower than OpenCV's 4148 ms; bicubic scaling and rotation have no result ('Shame!!'), and issue #167 says bicubic is slower than OpenCV.
- Proprietary products without a Doubango licence (GPL-3.0), or teams that need documentation and support: the README calls it an undocumented R&D project with 143 open issues and no releases.

## How it is fast

Each kernel has a scalar C++ reference plus SSE2/SSSE3/SSE4.1/AVX2 intrinsics, YASM x86/x64 assembly and NEON32/NEON64 assembly, chosen at run time by CPU flags and buffer alignment, and rows are split across a custom thread dispatcher (8 threads in the published run). Much of the speed comes from low-precision fixed point: grayscale uses 7-bit coefficients (Y = ((33R+65G+13B)&gt;&gt;7)+16), YUV to RGB uses 5-bit coefficients (R = (37Y'+51V')&gt;&gt;5), bilinear scaling uses 8-bit fractional coordinates and weights so every product fits in 16-bit lanes (mullo/mulhi_epu16), and HSV uses lookup tables of reciprocals, with an optional approximate SSSE3 reciprocal. Results quoted in the comparison file were taken with assembler code and TBBMalloc or TCMalloc.

## Compared with alternatives

Pick CompV over RGB2Y, DeltaCV or KLERP only when you want a whole GPL vision stack (scaling, thresholding, features, CCL) with ARM and x86 assembly from one vendor. For standalone conversions that must match OpenCV or a standard, KLERP (bilinear, matches OpenCV output) and libyuv, sparkyuv or yuvutils-rs (YUV) are permissive, documented and verifiable.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake; also Visual Studio .sln and Xcode project) |
| **Dependencies** | YASM for x86/x64 assembly (CMake fails without it); bundled tbbmalloc sources and thirdparties headers; pthread/dl on Unix, Shlwapi/Winmm on Windows; optional Intel IPP (COMPV_HAVE_INTEL_IPP), CUDA, OpenCL, OpenGL and other GPU back ends in separate modules |
| **Minimum toolchain** | C++11, CMake 3.10+, YASM; MSVC, GCC or Clang (Release builds use -O3) |
| **Platforms** | x86 and x86-64 (SSE2 to AVX2/FMA, run-time dispatch) on Windows, Linux and macOS; ARM32/ARM64 NEON on Android, iOS, Raspberry Pi and Jetson |
| **Thread safety** | not documented; functions split work over a global thread dispatcher (CompVParallel) and avoid nested dispatch when called from a pool thread |
| **Drop-in for the baseline** | partial — covers cvtColor-style conversions and resize, but through its own CompVMatPtr API and with different output definitions (limited-range gray, 0-255 hue, non-centre-aligned 8-bit bilinear), so results will not match OpenCV |

## Gotchas

- SIMD and assembly paths are selected only when output pointers and strides are 16- or 32-byte aligned; unaligned buffers silently fall back to slower intrinsics or the scalar C++ path.
- The bilinear SIMD kernels are hard-coded for 8-bit fixed point; the source comment says a shift of 11 is correct but no SIMD code exists for it, so the drift in issue #176 (open since 2022-11-30) applies to the AVX2 path behind the published numbers.
- Builds with COMPV_HAVE_INTEL_IPP switch RGB24-to-gray to ippiRGBToGray (full range), which gives different output from the default build's limited-range formula.
- HSV conversion can use an approximate SSSE3 reciprocal, and its expected MD5 differs between x86 and ARM, so HSV output is not bit-identical across platforms.

## Known shortcomings

- GPL-3.0. Result-file numbers (i7-4790K, 2017-2019) match and the CompV drivers are public (tests/image/chroma_conv.cxx, scale.cxx), but the OpenCV harness, version, IPP and thread settings are unpublished and outputs were never matched against OpenCV; scaling was measured on grayscale, HSV uses an approximate reciprocal, and the '50x' appears only in the repo description.
- Compared outputs are not like-for-like with OpenCV: RGB24 to grey computes limited-range BT.601 luma ((33R+65G+13B)&gt;&gt;7)+16, so white gives 237 where OpenCV RGB2GRAY is full-range; YUV to RGB uses 5-bit coefficients (37/32); HSV hue spans 0-255 (OpenCV CV_RGB2HSV uses 0-180); the bilinear AVX2 path is hard-coded 8-bit fixed point and the maintainer's open issue #176 says shift 8 drifts (derived: the last column samples x 1278.9 instead of 1280.9, weights sum to 255/256 so white gives 253). The IPP build swaps the grey formula; 143 open issues.

## Caveats and trade-offs

1. Only evidence: a first-party result file, last edited April 2019, from an i7-4790K iMac running Windows 8. The OpenCV version, its build (IPP on or off, TBB, thread count) and the compilers and flags for both sides are not stated. The file only says 'full optiz' and notes OpenCV uses SSE2 and multithreading for scaling. 2. The CompV-side drivers are public (tests/image/chroma_conv.cxx, tests/image/scale.cxx; loop counts are set to 1 at HEAD) and check CompV's own MD5s; the OpenCV-side code is not in the repo. 3. No output comparison against OpenCV is published. 4. The HSV path uses an approximate SSSE3 reciprocal with its own MD5 set (dstMD5_rcp), so CompV HSV output can differ from an exact conversion. 5. CompV results use assembler plus TBBMalloc/TCMalloc. 6. Single-thread AVX2 bilinear (5435 ms) is slower than OpenCV's 4148 ms. Bicubic scaling and bicubic rotation rows are marked 'Shame!!' (no CompV result). 7. The 'Up to #50 times faster than OpenCV' claim is in the GitHub repo description, not the README. No row of the result file matches it: the largest ratio is about 28x (BruteForce matcher, 2840%), and the colour and scaling rows are about 3-11x. 8. The README says the project is undocumented and 'not intended to be used by other companies'; GPL-3.0.

GPL-3.0 (copyleft, commercial use needs the vendor's licence); README says it is an R&D project with no documentation and is not intended for use by other companies; hand-written assembler and TBBMalloc/TCMalloc are part of the quoted results; large library with GPU back ends.

## Maintenance

Code is still committed to (last commit 2026-09-20 per the verifier) and used in Doubango's commercial SDKs, but it is GPL-3.0, undocumented, has no releases and 143 open issues, so it is copyable mainly for GPL projects willing to vendor a large codebase.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party result file only (speed_compare (core i7 quad@4ghz).txt, edited 2017-12 to 2019-04) on an i7-4790K under Windows 8. The CompV-side timing drivers are public (tests/image/chroma_conv.cxx, tests/image/scale.cxx), but the OpenCV side of the comparison, the OpenCV version and build (IPP, TBB, threads) and the compiler flags are not published.
- **Verifier notes:** Numbers match the result file exactly; C stands. I found the CompV-side benchmark drivers (tests/image/chroma_conv.cxx, scale.cxx), but the OpenCV harness, version and build are unpublished. Bilinear scaling ran on grayscale, not RGB. Metadata (GPL-3.0, 212 stars, 46 forks, last commit 2026-09-20) checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/DoubangoTelecom/compv>
  - <https://github.com/DoubangoTelecom/compv/commits>
  - https://github.com/DoubangoTelecom/compv/commits/master/speed_compare%20(core%20i7%20quad%404ghz).txt
  - https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/speed_compare%20(core%20i7%20quad%404ghz).txt
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/README.md>
  - <https://github.com/DoubangoTelecom/compv/tree/master/tests>
  - <https://github.com/DoubangoTelecom/compv/tree/master/tests/image>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/tests/image/chroma_conv.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/tests/image/scale.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/tests/image/main.cxx>
  - <https://github.com/DoubangoTelecom/compv/issues/118>
- **Sources the enricher read:**
  - <https://github.com/DoubangoTelecom/compv>
  - <https://github.com/DoubangoTelecom/compv/issues>
  - <https://github.com/DoubangoTelecom/compv/issues/176>
  - <https://github.com/DoubangoTelecom/compv/tree/master/base/image>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/README.md>
  - https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/speed_compare%20(core%20i7%20quad%404ghz).txt
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/tests/image/chroma_conv.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/tests/image/scale.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/tests/image/main.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/base/image/compv_image_scale_bilinear.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/base/image/intrin/x86/compv_image_scale_bilinear_intrin_avx2.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/base/image/compv_image_conv_common.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/base/image/compv_image_conv_rgbfamily.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/base/image/compv_image_conv_to_grayscale.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/base/image/compv_image_conv_to_rgbx.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/base/image/compv_image_conv_hsv.cxx>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/base/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DoubangoTelecom/compv/HEAD/common.cmake>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/doubangotelecom/compv`) · [data/wave10/enrich/raw/github_com_doubangotelecom_compv.json](../../../data/wave10/enrich/raw/github_com_doubangotelecom_compv.json) (enrichment confidence 0.75)

</details>
