# DeltaCV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Four hand-written SSE/AVX2 kernels that fuse colour conversion and threshold masking; first-party 3.4-7.6x over OpenCV call chains.

| | |
|---|---|
| **Beats** | OpenCV (cv::cvtColor RGB2GRAY and RGB2HSV on CPU, and OpenCV chains for fused colour-space plus threshold operations) |
| **Claimed result** | CPU, same machine (1024x1280, CPU not stated): inRange 0.29-0.30 vs OpenCV 1.06-1.18 ms (3.5-4.0x); weightedGrayWithSeg 3.39-4.33x; grayBRWithSeg 4.6-4.8x. The fused ycrcbWithSeg row (0.88-0.90 ms vs cvtColor(RGB2YCrCb)+inRange 6.68-6.75 ms, 7.4-7.6x) computes a different, wrong YCrCb (mixed channel order) and should not be cited. GPU vs CPU, a different machine class (480x640, GTX 1070 kernel time vs OpenCV on an i5 7500): RGB2GRAY 0.008-0.010 vs 0.340-0.360 ms (the README cell says '3.4 - 45'; timings imply 34-45x, derived from page data). The README's RGB2HSV row compares different work and should not be cited. |
| **Workload** | CPU: fused colour-space conversion plus threshold segmentation on a 1024x1280 image (ycrcbWithSeg, inRange, weightedGrayWithSeg, grayBRWithSeg), each producing an 8-bit mask, vs the OpenCV call chain (for example cvtColor then inRange). GPU: CUDA kernels on a 480x640 image vs CPU OpenCV. The GPU 'RGB2HSV' kernel (gpu/src/colorSpace.cu) does not output HSV: it masks the RGB input by an HSV range, unlike OpenCV's cvtColor RGB2HSV. |
| **Metric** | latency |
| **Hardware** | GPU table: NVIDIA GTX 1070 8G versus OpenCV on Intel i5 7500; CPU SIMD table: CPU model not stated |
| **Compiler and flags** | CPU part built with -mavx2 -march=haswell (compiler not stated) |
| **Adoption** | 128 stars, 12 forks |
| **Last commit** | 2019-04-27 |
| **Links** | [repository](https://github.com/DasudaRunner/DeltaCV) · [benchmark](https://github.com/DasudaRunner/DeltaCV) |

## Verdict

The README's same-machine CPU table (1024x1280 BGR, unnamed CPU and compiler, OpenCV version not stated, -O3 -mavx2 -march=haswell) reports the fused kernels at 3.4-7.6x OpenCV call chains, e.g. ycrcbWithSeg 0.88-0.90 ms vs cvtColor plus inRange 6.68-6.75 ms. The repo has no timing code to reproduce this, and the ycrcbWithSeg output does not match the OpenCV chain it was timed against. The GPU table (GTX 1070 kernel-only vs OpenCV on an i5-7500 CPU) is not a like-for-like comparison.

## Use it when

- Per-frame colour segmentation (robot vision, coloured-marker or light-bar detection) on x86 CPUs with AVX2, where the only output you need is a binary mask from a fixed BGR, grey-weight or channel-difference threshold.
- Hot loops that today run cv::split plus scaled Mat adds plus cv::threshold (weightedGrayWithSeg) or a channel difference plus threshold (grayBRWithSegStandard). The fused pass avoids several full-image temporaries.
- Plain 3-channel cv::inRange on contiguous 8-bit BGR images whose pixel count is a multiple of 16 (README: 0.29-0.30 ms vs 1.06-1.18 ms on 1024x1280).
- As a reference or starting point for writing your own pshufb + pmaddwd fused kernels; each function is about 150 lines of intrinsics.

## Skip it when

- When the mask must match OpenCV's YCrCb: ycrcbWithSeg's colour math is wrong (see gotchas). Its Cr and Cb channels match neither BGR2YCrCb nor RGB2YCrCb, so thresholds tuned on cv::cvtColor output select different pixels.
- Images whose pixel count is not a multiple of 16 (3-channel inRange, ycrcbWithSeg) or 32 (AVX2 functions): the scalar tail loop starts at a byte offset instead of a pixel index, so the trailing pixels are never written. For 1-channel inRange the tail reads two bytes past the buffer and trips an assert in debug builds.
- Strided or ROI images (cv::Mat with padding or submatrices): there is no row-stride parameter, and every function assumes width\*height\*3 contiguous bytes.
- Non-x86 targets or CPUs without AVX2: there is no scalar fallback, NEON path or runtime dispatch, and the build hard-codes -mavx2 -march=haswell.
- The GPU part: the README's RGB2HSV speed-up compares an RGB mask kernel (it zeroes every non-negative hue) with a real OpenCV HSV conversion. GPU times exclude transfers and are set against a CPU, not OpenCV CUDA or NPP.

## How it is fast

Kernel fusion: the colour transform and the range test run in registers on the same 16 or 32 pixels, so no intermediate YCrCb, grey or split-plane image is written to memory. BGR de-interleaving uses pshufb (_mm_shuffle_epi8) byte shuffles. The weighted sums are Q15 fixed-point dot products via pmaddwd (_mm_madd_epi16), packed back with saturation, and compared with unsigned max/min-plus-cmpeq tricks. ycrcbWithSeg and 3-channel inRange are 128-bit SSSE3/SSE4.1. weightedGrayWithSeg, both grayBR functions and 1-channel inRange use 256-bit AVX2, with the two 128-bit lanes split so the in-lane packus keeps pixel order.

## Compared with alternatives

Pick DeltaCV only when you want a fused threshold mask in one pass and will fix and test the kernels yourself. For colour conversion that matches OpenCV, CompV (RGB to grey, YUV and HSV, 6-7x OpenCV in its own result file) or FlyCV are maintained libraries, and RGB2Y covers plain BGR-to-grey at 2-3x OpenCV.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the SIMD kernels (raw pointers; core.hpp and DataTypes.hpp only include the intrinsics headers). OpenCV for the examples; Boost (system, atomic, interprocess) for shm.hpp and the CMake targets; CUDA plus OpenCV for the GPU part. |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11); compiler not stated; built with -O3 -msse4.1 -mavx2 -march=haswell |
| **Platforms** | x86-64 with SSSE3/SSE4.1 for ycrcbWithSeg and 3-channel inRange and AVX2 for the rest (effectively Haswell or newer); GPU kernels need CUDA (tested on a GTX 1070) |
| **Thread safety** | not documented; the CPU functions keep no global state and only touch caller buffers, so separate calls on separate buffers are independent |
| **Drop-in for the baseline** | partial — inRange mirrors cv::inRange for contiguous 8-bit images (pixel count a multiple of 16 or 32). The other functions fuse several OpenCV calls behind a new pointer-based signature, and ycrcbWithSeg does not reproduce OpenCV's YCrCb. |

## Gotchas

- Correctness bug behind the headline 7.4-7.6x row: ycrcbWithSeg mixes channel orders. The Y row treats channel 0 as blue (0.114, 0.587, 0.299). The Cr row (0.499, -0.419, -0.081) is RGB-order Cr, so channel 0 is treated as red. The Cb row (0.395, -0.331, -0.064) equals 0.564\*(ch0 - Y_rgb), which is not Cb in either order. For a skin-tone BGR pixel (120,150,220) it yields (Y,Cr,Cb) = (168,107,112), where cv::cvtColor BGR2YCrCb gives (168,165,101) (derived by evaluating both formulas). The timed example also runs cv::COLOR_RGB2YCrCb on an imread (BGR) image, so neither side is the conversion the header documents.
- grayBRWithSeg's color_mode is swapped against its header comment ('0 -&gt; red, 1 -&gt; blue'): mode 0 computes B-G and mode 1 computes R-G. The header and example suggest gray weights scalar_d(0.144,0.587,0.299), a typo for 0.114 that brightens grey by 3% and no longer matches the cv::COLOR_BGR2GRAY output it is compared with.
- The SIMD and scalar-tail paths disagree. The SIMD path uses saturating unsigned subtraction and truncating Q15 shifts; the tail uses signed differences. Grey and weighted-grey values are truncated, not rounded, so they can be 1 below OpenCV's. ycrcbWithSeg is declared bool but returns nothing, which is undefined behaviour if the result is used.
- There are no tests and no timing harness. Every example compares outputs by imshow; ycrcbWithSeg.cpp and grayBRWithSegStandard.cpp declare timers that are never used, and the former references an undeclared loop variable i, so it does not compile.

## Known shortcomings

- Claim overstated and abandoned (2019): the headline rows are GPU (GTX 1070, kernel-only) against CPU OpenCV on an i5-7500, a different machine class; the GPU RGB2HSV does different work (masks RGB) and is buggy ('_h = (_h&lt;0)\*(_h + 360)' zeroes the hue), and the example timing code is missing or does not compile. The valid part is the same-machine CPU SIMD rows at 3.4-7.6x, CPU model unstated.
- Correctness bug behind the headline ycrcbWithSeg row (7.4-7.6x): channel order is mixed (Y treats channel 0 as B, Cr treats it as R, Cb is 0.564\*(ch0 - Y_rgb), Cb in neither order), so BGR(120,150,220) gives (168,107,112) against OpenCV's (168,165,101), and the timed example calls COLOR_RGB2YCrCb on BGR data; the mask is not OpenCV-equivalent (retier-07 drops the row). grayBRWithSeg has color_mode swapped against the header, a 0.144 grey-weight typo, tail loops that skip trailing pixels, a 1-channel inRange tail that reads 2 bytes past the buffer (asserts in debug), no row stride, and the weightedGray baseline is a naive split plus MatExpr chain. CPU model unknown (the author's blog on zhihu is blocked here).

## Caveats and trade-offs

1. GPU numbers compare a GTX 1070 against CPU OpenCV on an i5 7500, a different machine class; there is no OpenCV CUDA or NPP baseline. 2. GPU timings exclude host-device transfers: the leftover, commented-out timer in gpu/main.cpp starts after the cudaMemcpy upload and stops at cudaDeviceSynchronize. 3. The GPU RGB2HSV kernel does different work from OpenCV (an RGB mask, not an HSV image) and is buggy. The line '_h = (_h&lt;0)\*(_h + 360)' zeroes every non-negative hue. The +360 offset on the red branch forces hue positive. The V test uses the channel minimum instead of the maximum. Grey pixels divide by zero. 4. GPU RGB2GRAY uses low-precision 8-bit coefficients (76,150,30)&gt;&gt;8, and its own source comment gives 0.12 ms, not the README's 0.008-0.010 ms. 5. The CPU 'AVX2' functions use 128-bit SSE intrinsics. 6. ycrcbWithSeg returns bool without a return statement, and its tail loop compares a byte offset with a pixel count, so trailing pixels are never processed when the pixel count is not a multiple of 16 (the 1024x1280 benchmark size is unaffected). 7. The example programs carry no usable timing code; outputs are compared only by imshow. 8. The OpenCV version is not stated (a source comment cites opencv-4.0.1 coefficients). 9. Flags -O3 -mavx2 -march=haswell come from cpu/CMakeLists.txt; the compiler is not stated. 10. The SIMD table names no CPU model. 11. Last commit 2019-04-27.

Small collection of hand-written kernels rather than a full library; CPU kernels are fused operations (colour conversion plus segmentation) so they are not drop-in replacements for single OpenCV calls; GPU path needs CUDA and the transfer cost is not stated.

## Maintenance

Abandoned since 2019-04-27 (58 commits, one open issue from 2018 that says the interface is awkward to use). MIT-licensed and small enough to vendor, but treat it as unreviewed sample code: fix the YCrCb coefficients and the tail loops before shipping it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README tables only. The CPU examples carry no working timing code (cpu/examples/ycrcbWithSeg.cpp uses an undeclared loop variable and uninitialised timers; inRange.cpp has no timing at all), and the SIMD table names no CPU or compiler. The GPU table pits a GTX 1070, timing the kernel only, against OpenCV on an i5-7500 CPU.
- **Verifier notes:** Downgraded the claim, not the tier (stays C). The README's GPU RGB2HSV speed-up is invalid: the kernel masks RGB pixels instead of converting to HSV and zeroes the hue. GPU RGB2GRAY is kernel-only against a CPU OpenCV. The usable evidence is the same-machine CPU SIMD rows (3.4-7.6x for fused colour-space plus segmentation), which are first-party with no runnable timing code. Metadata (MIT, 128 stars, 12 forks, abandoned) checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/DasudaRunner/DeltaCV>
  - <https://github.com/DasudaRunner/DeltaCV/commits>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/README.md>
  - <https://github.com/DasudaRunner/DeltaCV/tree/master/cpu/examples>
  - <https://github.com/DasudaRunner/DeltaCV/tree/master/cpu/src/SIMD>
  - <https://github.com/DasudaRunner/DeltaCV/tree/master/gpu>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/examples/ycrcbWithSeg.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/examples/inRange.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/src/SIMD/YCrCbWithSeg.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/gpu/main.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/gpu/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/gpu/src/colorSpace.cu>
- **Sources the enricher read:**
  - <https://github.com/DasudaRunner/DeltaCV>
  - <https://github.com/DasudaRunner/DeltaCV/tree/master/cpu>
  - <https://github.com/DasudaRunner/DeltaCV/tree/master/cpu/src/SIMD>
  - <https://github.com/DasudaRunner/DeltaCV/tree/master/gpu>
  - <https://github.com/DasudaRunner/DeltaCV/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/README.md>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/main.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/include/deltaCV/SIMD/core.hpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/include/deltaCV/SIMD/DataTypes.hpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/include/deltaCV/shm.hpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/src/SIMD/YCrCbWithSeg.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/src/SIMD/inRange.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/src/SIMD/WeightedGrayWithSeg.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/src/SIMD/GrayBRWithSeg.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/examples/ycrcbWithSeg.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/examples/inRange.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/examples/weightedGrayWithSeg.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/examples/grayBRWithSeg.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/cpu/examples/grayBRWithSegStandard.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/gpu/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/gpu/main.cpp>
  - <https://raw.githubusercontent.com/DasudaRunner/DeltaCV/HEAD/gpu/src/colorSpace.cu>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/dasudarunner/deltacv`) · [data/wave10/enrich/raw/github_com_dasudarunner_deltacv.json](../../../data/wave10/enrich/raw/github_com_dasudarunner_deltacv.json) (enrichment confidence 0.8)

</details>
