# Simd (ermig1979)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> MIT C/C++ library of hand-vectorized image kernels (conversion, resize, filters) for x86 and Arm; no published win over OpenCV or libyuv.

| | |
|---|---|
| **Beats** | OpenCV (cv::resize and colour conversion) and libyuv; no published comparison found |
| **Claimed result** | No numbers. README: 'many useful high performance algorithms for image processing' optimized with SSE, AVX, AVX-512, AMX (x86) and NEON, SVE, SVE2 (Arm). Release notes (docs/2025.html) mention 'Special tests to compare Simd and OpenCV resize' and a SimdResizeMethodBilinearOpenCv mode with AVX2 and AVX-512BW optimizations, with no timings. |
| **Workload** | No published OpenCV or libyuv comparison. The repo has a test mode that times each Simd function's scalar and SIMD implementations against each other, and an optional SIMD_OPENCV build in which ResizeOpenCvSpecialTest times Simd resize against cv::resize on a BGR24 480x640 to 333x444 image, but no numbers are published. |
| **Metric** | throughput |
| **Adoption** | 2.3k stars, 456 forks; vcpkg port; proposed as an OpenCV replacement in wpilibsuite/allwpilib issue 7108 (no numbers) |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/ermig1979/Simd) · [benchmark](https://github.com/ermig1979/Simd) |

## Verdict

No first-party numbers against OpenCV or libyuv exist; the repo's test mode only times Simd's scalar versus SIMD implementations. The only third-party figures found point the other way for resize and BgrToGray (issues #149 and #212, OpenCV 4.5.x 2.65x to 4-6x faster, thread counts unstated), while fwessels/go-cv-simd, a c2goasm Go port of Simd's SSE2 code, reports 3x3 Gaussian, mean and median filters 61-85% faster than OpenCV 2.x cvSmooth via go-opencv (filters only, OpenCV 2.x legacy C API, uninitialised images, hardware and image size not stated in the README).

## Use it when

- You need many pixel-level kernels (colour conversion, YUV planar conversions, reduce/stretch, statistics, motion-detection primitives) behind one MIT C API with runtime ISA dispatch, and do not want OpenCV's footprint.
- Single-threaded per-frame processing on known x86 (AVX2/AVX-512) or Arm NEON hardware where you will benchmark against your current OpenCV build yourself.
- You need bilinear resize that matches OpenCV output (SimdResizeMethodBilinearOpenCv) or PyTorch/Caffe coordinate mappings for neural-network preprocessing.
- Embedded or plugin builds that need a static library with no external dependencies.

## Skip it when

- As a proven speedup over OpenCV: two user reports (issue #149: upscale 3328x1032 to 3752x1080, Simd 9.789 ms vs OpenCV 4.5.1 3.689 ms on an i7-10700; issue #212: Simd::Resize and Simd::BgrToGray '4-6 times slower than OpenCV4.5.5' on an i7-10750H) went unanswered and no counter-benchmark is published.
- Multi-core throughput on large images: SimdGetThreadNumber defaults to 1 and only some functions (GEMM, Synet layers, ResizerNearest since 2025) are parallelized, while OpenCV and libyuv callers usually get threading or IPP for free.
- High-quality resampling: there is no Lanczos or other windowed-sinc filter; use fast_image_resize or Pillow-SIMD class libraries for that.
- Projects that need a stable API: release 8.0.166 (2026-10-01) removed SimdFill, SimdFillBgr, SimdFillBgra, SimdCopyFrame, the HOG, Neural, HAAR/LBP Detection and 8-bit Synet functions and dropped RISC-V and Hexagon HVX support; major versions moved 6 to 7 to 8 within 2026.
- macOS or other non-Windows/Linux targets: the README lists only 32/64-bit Windows and Linux.

## How it is fast

Each function has a scalar Base version plus hand-written intrinsics versions for SSE4.1, AVX2, AVX-512BW, AVX-512VNNI and AMX-BF16 on x86 and NEON and SVE2 on Arm, each compiled in its own translation unit with matching -m flags, and SimdLib.cpp picks the best one at runtime from CPUID. Byte resizers use fixed-point interpolation, and the BilinearOpenCv mode reproduces OpenCV's integer arithmetic so output matches cv::resize within 1 level.

## Compared with alternatives

Pick Simd over CompV, DeltaCV or KLERP when you need one maintained MIT library spanning conversion, resize and filters with AVX-512/AMX and SVE2 dispatch; for YUV conversion prefer libyuv or the measured sparkyuv/xxYUV, and for quality resampling prefer fast_image_resize or Pillow-SIMD, all of which publish numbers Simd lacks.

## Integration

| | |
|---|---|
| **Form** | static lib (default with CMake; DLL by default in the MSVS 2022 project; SIMD_SHARED for a shared lib) |
| **Dependencies** | none (OpenCV optional, test framework only); vcpkg port 'simd' |
| **Minimum toolchain** | C++11 (-std=c++11), CMake 3.10, GCC/Clang or MSVS 2022; AVX-512BW TUs need GCC 5.5+, VNNI GCC 8+, AMX GCC 11+ with binutils 2.34+ |
| **Platforms** | x86 and x86-64 (scalar, SSE4.1, AVX2, AVX-512BW, AVX-512VNNI, AMX-BF16 runtime-dispatched), ARM32/aarch64 NEON, SVE/SVE2 (off by default); Windows and Linux |
| **Thread safety** | not documented; resizer and filter contexts are const at run time and reusable for same-geometry images; SimdSetThreadNumber is a global setting |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: the only OpenCV comparison in the repo, ResizeOpenCvSpecialTest in src/Test/TestResize.cpp, is fair in shape (cv::setNumThreads matched to SimdGetThreadNumber, random BGR24 480x640 to 333x444, both sides rebuild their tables per call since Simd::Resize does Init/Run/Release each time) but runs only with -DSIMD_OPENCV=ON and -m=s and no output is committed; the default -m=a mode only compares Simd's own scalar and SIMD versions.
- The CMake build compiles the dispatcher SimdLib.cpp with -mavx2 -mfma (plus -mavx512bw on Unix when SIMD_AVX512 is ON), and the test app built with SIMD_TARGET set uses the same flags; illegal-instruction reports on older CPUs recur (#71 and #125 closed, #274 open on an Atom Z3735F).
- Memory-safety bugs in SIMD paths are still being found: #299 (STITCH fuzzer with AddressSanitizer) was a 16-byte heap-buffer-overflow write in Avx512bw::TransformImageTranspose_4x4x16 for a 32x4 BGRA image rotated 270 degrees, and #333 (2026-04-09, open) reports a crash in Avx2::AbsDifferenceSums3x3AutoTest.
- Not every method supports every channel type: OpenCV-bilinear, bicubic and area resizers are byte-only, Caffe/PyTorch bilinear are float/BF16-only, and SimdResizerInit returns NULL for unsupported combinations (the C++ Simd::Resize then hits assert(0), which is a no-op in release builds).

## Known shortcomings

- No published OpenCV or libyuv numbers: ResizeOpenCvSpecialTest in src/Test/TestResize.cpp has no committed output, the blocked github.io site is the repo's docs/ folder, and the simd.sourceforge.net mirror has no benchmarks. Kept at D under the keep-and-document rule; 2.3k stars, MIT, active.
- Enricher: the only third-party numbers run against it: issue #149 has Simd 9.789 ms vs OpenCV 4.5.1 3.689 ms upscaling 3328x1032 to 3752x1080 on an i7-10700, and issue #212 reports Resize and BgrToGray '4-6 times slower than OpenCV 4.5.5' on an i7-10750H, both unanswered with thread counts unstated (SimdGetThreadNumber defaults to 1 and most resizers are not parallelised). 8.0.166 (2026-10-01) removed public APIs (Fill\*, CopyFrame, HOG, Neural, HAAR/LBP detection, 8-bit Synet) and dropped RISC-V and HVX; the SimdLib.cpp dispatcher is compiled -mavx2 -mfma with illegal-instruction reports (#71, #125 closed, #274 open); #299 fuzzer/ASan heap-buffer-overflow write in Avx512bw::TransformImageTranspose_4x4x16; #333 crash open. fwessels/go-cv-simd is a Go wrapper of its SSE2 code (duplicate if found).

## Caveats and trade-offs

Claim-only: no Simd versus OpenCV or libyuv numbers are published anywhere reachable. The project site ermig1979.github.io/Simd is EGRESS_BLOCKED here, but it is served from the repo's docs/ folder (index.html, download.html, yearly release notes 2013.html-2026.html, help/), and its simd.sourceforge.net mirror, which was reachable, links no benchmark or comparison report, so the blocked pages do not hide numbers. The OpenCV resize special test (built only with SIMD_OPENCV, matching OpenCV's thread count to Simd's) exists in src/Test/TestResize.cpp but its results are not published; ResizeOpenCv always calls cv::resize with the default interpolation regardless of the Simd method under test. Web searches found no third-party Simd versus OpenCV or libyuv benchmark (a search snippet from a stereo-vision course repo on git.tdem.in reports SIMD 3.54x faster than OpenCV, snippet only and not opened; it does not name this library). [retier] No published Simd vs OpenCV or libyuv numbers (ResizeOpenCvSpecialTest has no committed output; docs site blocked). The only third-party figures are unanswered issues where Simd loses: #149 upscale 9.789 ms vs OpenCV 4.5.1 3.689 ms (i7-10700), #212 Resize and BgrToGray 4-6x slower than OpenCV 4.5.5 (i7-10750H), thread counts unstated (Simd defaults to 1 thread, most resizers unparallelised). 8.0.166 removed several public APIs; open #299 ASan heap-buffer-overflow in an AVX-512 transpose and #274 illegal-instruction report. 2.3k stars, MIT, active.

C API with C++ and Python wrappers; broad coverage of pixel format conversion, resize and filtering, statistics, motion and object detection, and neural-network inference (Synet); x86 SSE to AMX and Arm NEON, SVE, SVE2; dynamic or static link, CMake and MSVS; Windows and Linux, 32 and 64 bit.

## Maintenance

Very active (monthly releases, 8.0.166 on 2026-10-01, about 5,950 commits, 2.3k stars, vcpkg port) and MIT-licensed, but the public API is pruned between major versions and the speed advantage over OpenCV is unmeasured, so treat it as tier D and benchmark against your own OpenCV build before switching.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** No published numbers against OpenCV or libyuv: the README describes only a self-comparison test mode (scalar vs SIMD), src/Test/TestResize.cpp holds an optional SIMD_OPENCV ResizeOpenCvSpecialTest that times cv::resize against Simd::Resize on a BGR24 480x640 to 333x444 image but no output is committed, and the docs (release notes 2013-2026, Doxygen help) carry no timing tables.
- **Verifier notes:** Notable (2.3k stars, vcpkg) but no numbers against any baseline; keep at D and record 'no published baseline comparison'. The earlier caveat about blocked pages is resolved: the pages are the repo's docs/ folder, mirrored on simd.sourceforge.net, with no benchmarks.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** published OpenCV comparison from its own test harness; committed output of its own OpenCV special test
- **Pages the verifier opened:**
  - <https://github.com/ermig1979/Simd>
  - <https://github.com/ermig1979/Simd/commits>
  - <https://github.com/ermig1979/Simd/tree/master/docs>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/src/Test/TestResize.cpp>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/docs/2025.html>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/docs/2026.html>
  - <https://simd.sourceforge.net/>
- **Sources the enricher read:**
  - <https://github.com/ermig1979/Simd>
  - <https://github.com/ermig1979/Simd/commits>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/prj/cmake/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/prj/cmake/x86.cmake>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/prj/cmake/arm.cmake>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/src/Simd/SimdConfig.h>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/src/Simd/SimdLib.h>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/src/Simd/SimdLib.hpp>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/src/Test/TestResize.cpp>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/docs/2025.html>
  - <https://raw.githubusercontent.com/ermig1979/Simd/HEAD/docs/2026.html>
  - <https://github.com/ermig1979/Simd/issues?q=is%3Aissue+illegal+instruction>
  - <https://github.com/ermig1979/Simd/issues?q=is%3Aissue+opencv>
  - <https://github.com/ermig1979/Simd/issues/274>
  - <https://github.com/ermig1979/Simd/issues/212>
  - <https://github.com/ermig1979/Simd/issues/149>
  - <https://github.com/ermig1979/Simd/issues/215>
  - <https://github.com/ermig1979/Simd/issues/299>
  - <https://github.com/fwessels/go-cv-simd>
  - <https://github.com/fwessels/go-cv-simd/tree/master/sse2>
  - <https://raw.githubusercontent.com/fwessels/go-cv-simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/fwessels/go-cv-simd/HEAD/sse2/benchmarks_opencv_test.go>
  - <https://raw.githubusercontent.com/fwessels/go-cv-simd/HEAD/sse2/benchmarks_test.go>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/ermig1979/simd`) · [data/wave10/enrich/raw/github_com_ermig1979_simd.json](../../../data/wave10/enrich/raw/github_com_ermig1979_simd.json) (enrichment confidence 0.65)

</details>
