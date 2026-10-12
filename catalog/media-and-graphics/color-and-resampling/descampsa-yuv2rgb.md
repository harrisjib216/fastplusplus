# yuv2rgb (descampsa)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Two-file C99 SSE2 converter between planar YUV420 (also NV12/NV21) and RGB24 that roughly doubles old libswscale's speed.

| | |
|---|---|
| **Beats** | FFmpeg libswscale 3.0.0 (MMX path) |
| **Claimed result** | yuv2rgb, 100 iterations: sse2_aligned 0.607 s and sse2_unaligned 0.704 s vs ffmpeg 1.227 s / 1.221 s (about 2x). rgb2yuv: sse2_aligned 0.641 s and sse2_unaligned 0.677 s vs ffmpeg 3.398 s / 3.386 s (about 5.3x). Plain C std path 2.63 s / 2.59 s. Intel IPP 9.0.1 is slightly faster than the SSE2 code (0.636 s yuv2rgb, 0.579-0.594 s rgb2yuv). |
| **Workload** | YUV420p to RGB24 and RGB24 to YUV420p conversion of a 4K (4096x2160) image, 100 iterations, using the repo's test_yuv_rgb program; SSE2 versions, a plain C version, FFmpeg swscale and Intel IPP are timed side by side. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-5500U |
| **Compiler and flags** | gcc 4.9.2, swscale 3.0.0, IPP 9.0.1; built with cmake -DCMAKE_BUILD_TYPE=Release plus -Werror -Wall -Wextra -pedantic -std=c99 from CMakeLists.txt (no explicit -O or -msse flags in the file) |
| **Adoption** | 191 stars |
| **Last commit** | 2022-02-15 |
| **Links** | [repository](https://github.com/descampsa/yuv2rgb) · [benchmark](https://github.com/descampsa/yuv2rgb) |

## Verdict

Author's run of the public test_yuv_rgb harness (clock() over 100 conversions of one 4096x2160 BT.601 frame, CMake Release build with GCC 4.9.2, Core i7-5500U): yuv2rgb SSE2 0.607 s with streaming stores and 0.704 s with plain stores vs libswscale 3.0.0 about 1.22 s (about 2x) and IPP 9.0.1 0.636 s. rgb2yuv SSE2 0.641/0.677 s vs swscale 3.39 s (about 5.3x, probably swscale's generic filtered-chroma path, not an equivalent converter) and IPP 0.579-0.594 s. Each frame touches about 40 MB (13.3 MB of YUV plus 26.5 MB of RGB, derived from page data), so the loop streams from DRAM rather than running cache-warm, and outputs are never compared across methods.

## Use it when

- You decode or capture planar I420, NV12 or NV21 frames on x86 and need RGB24 output with no FFmpeg or libyuv dependency.
- Large frames (HD to 4K) streamed straight to a file, encoder or GPU upload, where the _sse variant's non-temporal stores avoid read-for-ownership traffic on a destination far larger than the CPU cache.
- RGB24 or RGBA to I420 for an encoder input path when box-filtered chroma (2x2 average) is acceptable.
- Codebases that want a small BSD-3-Clause source drop they can read and modify in an afternoon.

## Skip it when

- ARM/aarch64 or any non-x86 target: yuv_rgb.c includes &lt;emmintrin.h&gt; unconditionally and there is no NEON path, so it does not compile there without editing.
- You need AVX2/AVX-512 speed: the code is SSE2 only, and Intel IPP 9.0.1 already beat it on rgb2yuv (0.579-0.594 s vs 0.641-0.677 s) and matched it on yuv2rgb in the author's own run.
- Quality-sensitive work: chroma is nearest-sample upsampled and box-downsampled, and the fixed-point math truncates instead of rounding, so output is not bit-exact with libswscale or IPP.
- High bit depth, 4:2:2/4:4:4, BGR/ARGB output or scaling: only 8-bit 4:2:0 to or from RGB24 (plus RGBA input) is implemented.
- Images narrower than 32 pixels with the SSE functions (see gotchas), or anything that needs an actively maintained dependency (last commit 2022-02-15).

## How it is fast

The SSE2 kernels process 32 pixels across two rows per step. Chroma is handled once per 2x2 block (nearest-sample replication when decoding, a plain 2x2 sum then &gt;&gt;2 when encoding), and all arithmetic is 16-bit fixed point (_mm_mullo_epi16 with 6-8 fractional bits) instead of swscale's higher-precision filter path. RGB24 is interleaved and de-interleaved with chains of byte unpack/pack shuffles (rgb.txt in the repo explains the scheme). The aligned (_sse) variants write with _mm_stream_si128 non-temporal stores, and the unaligned (_sseu) variants use ordinary _mm_storeu_si128.

## Compared with alternatives

Pick it over libyuv, xxYUV or sparkyuv only when a two-file SSE2 C source drop matters more than speed or coverage, since those carry AVX2/NEON paths and many more formats. Against FFmpeg's libswscale it wins on same-size I420&lt;-&gt;RGB24 on old x86 at the cost of precision and features.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (SSE2 intrinsics; the test program optionally links libswscale and Intel IPP) |
| **Minimum toolchain** | C99 compiler with SSE2 intrinsics (GCC, Clang; MSVC since the Feb 2022 commit); the README numbers used GCC 4.9.2 |
| **Platforms** | x86 and x86-64 with SSE2; the _std functions are portable C, but the unconditional &lt;emmintrin.h&gt; include must be removed for other architectures |
| **Thread safety** | not documented; the functions keep no mutable global state (read-only coefficient tables), so concurrent calls on separate buffers are safe by inspection |
| **Drop-in for the baseline** | partial: it replaces a same-size sws_scale YUV420P&lt;-&gt;RGB24 call, but with a different C API, fixed BT.601/709/JPEG matrices and no scaling or dithering options |

## Gotchas

- The SSE functions leave the last width%32 columns unconverted and the C and SSE functions leave the last row and column untouched for odd sizes (documented in yuv_rgb.h; open issue #13); the caller must convert the tail itself. The SSE loops use uint32_t `x < width-31`, which wraps for widths below 31 and runs past the buffers.
- The _sse variants use non-temporal stores and never issue _mm_sfence: hand the buffer to another thread only after a fence, and expect a cold cache when you read the RGB right after converting. Much of the README's aligned vs unaligned gap (0.607 vs 0.704 s) comes from these stores, not from alignment. At 4096 width the harness's malloc'd 'unaligned' buffers are 16-byte aligned too, and swscale and IPP time the same on both buffer sets.
- Bugs: the SSE2 yuv2rgb code timed in the README (commit 1fc2be8, Sept 2017; the timings have not changed since) overflowed 16 bits for BT.601/709 input with Y &gt;= 236, so those pixels came out black (issue #12). It was fixed on 2022-02-09 (e805bf2: srai to srli and sub_epi8 to subs_epu8). rgb32_yuv420_std still scales V with cb_factor at HEAD, the same bug issue #15 fixed only in the RGB24 path, so RGBA-input chroma from the C path is desaturated.
- yuv_rgb.c defines a global non-static `uint8_t clamp(int16_t)`, which can collide with other `clamp` symbols at link time. CMakeLists.txt adds -Werror globally and builds only the test program, so vendor yuv_rgb.c/.h rather than add_subdirectory.

## Known shortcomings

- Tier A on the repo's own test_yuv_rgb.c (gcc 4.9.2, i7-5500U, CMake Release -O3 -DNDEBUG, 2015-era). The 5.3x rgb2yuv figure is likely against swscale's generic RGB24 path (filtered chroma, no unscaled fast path), not like-for-like; the yuv2rgb 2x is the fairer number. Outputs were never compared against swscale's.
- Retiered A to C (retier-08): README timings are from 2017 code whose SSE2 yuv2rgb path overflowed int16 for luma 236 and above (pixels decoded black, issue #12, fixed 2022-02-09 with a same-cost instruction swap) and were never re-run. The 'aligned' path's edge is _mm_stream_si128 non-temporal stores without an sfence, not alignment; the plain-store SSE2 path is slower than IPP 9.0.1; the test streams about 40 MB per frame from DRAM. Width below 31 wraps the uint32 loop (out-of-bounds); rgb32_yuv420_std still uses cb_factor for V at HEAD (issue #15 fix missed the RGBA path); unconditional emmintrin.h so no ARM build; swscale 3.0.0 is likely Libav 11 (Debian 8).

## Caveats and trade-offs

Author's own run on one laptop CPU (i7-5500U) with an old swscale 3.0.0 whose YUV420P to RGB24 path is MMX code; modern swscale has newer SIMD paths and would narrow the gap. Intel IPP 9.0.1 beat the SSE2 code on rgb2yuv (0.579-0.594 s vs 0.641-0.677 s) and was within 5% on yuv2rgb. The swscale contexts are created with flags 0 (default scaler) and the outputs of each method are written to separate files but never compared, so equivalence is not checked. The rgb2yuv gap (about 5.3x) is likely partly different work: swscale has no unscaled fast path for RGB24 input (its special case is BGR24), so the ffmpeg row probably ran the generic scaler with filtered chroma and higher-precision intermediates, while yuv2rgb uses 8-bit fixed-point coefficients and a plain 2x2 box average for chroma. The yuv2rgb direction (about 2x) is closer to like-for-like (both use one chroma sample per 2x2 block). Flags are the CMake Release preset (-O3 -DNDEBUG) plus -Wall -Wextra -pedantic -std=c99 from CMakeLists.txt; SSE2 is the x86-64 baseline so no -msse flag is needed. Single 4K image run 100 times (cache-warm). README numbers predate the Feb 2022 commits, which include a fix to the plain C (std) rgb2yuv path, not the SSE2 path. [retier] README timings date from 2017 code whose SSE2 yuv2rgb path had an int16 overflow (luma 236 and above decoded black, issue #12, fixed 2022-02-09); never re-run after the fix. Author's own run on one laptop CPU (i7-5500U) with an old swscale 3.0.0 (likely Libav 11 on Debian 8) whose YUV420P to RGB24 path is MMX code; modern swscale has newer SIMD paths. Intel IPP 9.0.1 beat the SSE2 code on rgb2yuv and the plain-store SSE2 yuv2rgb path (0.704 s versus 0.636 s); the 'aligned' variant's edge is _mm_stream_si128 non-temporal stores without an sfence. The swscale contexts use flags 0 and outputs are never compared, so equivalence is unchecked; the rgb2yuv gap is partly different work (swscale has no unscaled fast path for RGB24 input). Width below 31 wraps the uint32 loop (out-of-bounds); rgb32_yuv420_std still uses cb_factor for V at HEAD (issue #15 fix missed the RGBA path); unconditional emmintrin.h, so no ARM build.

Small C99 library: only YUV420p &lt;-&gt; RGB24 (plus a few color-space matrices); aligned and unaligned SSE2 variants; no AVX2 or NEON. Author calls it an exercise in learning SSE intrinsics.

## Maintenance

Abandoned since 2022-02-15 (191 stars, 62 forks, not archived) but BSD-3-Clause and about 1,300 lines of C, so easy to vendor and patch. The README's libswscale 3.0.0 is a 2014-era build (version number consistent with the Libav 11 packages in Debian 8, and the README uses avconv), and modern swscale has newer SIMD paths that would narrow the gap.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now C.
- **Tier reason:** The README prints the full test_yuv_rgb output (std 2.630193 s, sse2_unaligned 0.704394 s, ffmpeg 1.221432/1.227100 s, ipp 0.636 s, sse2_aligned 0.606648 s; rgb2yuv sse2 0.640630/0.676625 s vs ffmpeg 3.385816/3.397952 s) with gcc 4.9.2, swscale 3.0.0, IPP 9.0.1 and an Intel i7-5500U; the timing harness is public (test_yuv_rgb.c, clock() over 100 iterations, sws_scale and ippiYCbCr420ToRGB_8u_P3C3R baselines) and the flags follow from the public CMakeLists.txt plus the documented Release build (CMake's GCC Release preset is -O3 -DNDEBUG).
- **Retiered** A to C: Lowered A to C under the rule that numbers measured on code later fixed for a correctness bug go to C: the README timings are unchanged since commit 1fc2be8 (2017-09-18), and the SSE2 yuv2rgb path timed there used srai plus sub_epi8, so (Y-16)\*149 overflowed int16 for BT.601/709 luma of 236 and above and those pixels came out black (issue #12); the fix e805bf2 (2022-02-09, srli plus subs_epu8) is a same-cost swap, so the timing is probably unaffected, but it was never re-run. The harness, compiler, flags and CPU remain public. Also from the enricher: the 'aligned' SSE2 path uses _mm_stream_si128 non-temporal stores (no sfence), so the 0.607 s versus 0.704 s gap is store type rather than alignment, and the plain-store SSE2 path (0.704 s) is slower than IPP (0.636 s); the test streams about 40 MB per frame from DRAM.
- **Verifier notes:** Numbers match the README exactly and the harness code is public, so tier A stands. The rgb2yuv 5.3x likely compares against swscale's generic (filtered-chroma) path rather than an equivalent converter; the 2x yuv2rgb figure is the more like-for-like headline. Last commit 2022-02-15, 191 stars, BSD-3-Clause, not archived.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/descampsa/yuv2rgb>
  - <https://github.com/descampsa/yuv2rgb/commits>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/README.md>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/test_yuv_rgb.c>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/yuv_rgb.c>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/descampsa/yuv2rgb>
  - <https://github.com/descampsa/yuv2rgb/commits>
  - <https://github.com/descampsa/yuv2rgb/commits/master>
  - <https://github.com/descampsa/yuv2rgb/issues?q=is%3Aissue>
  - <https://github.com/descampsa/yuv2rgb/issues/12>
  - <https://github.com/descampsa/yuv2rgb/issues/13>
  - <https://github.com/descampsa/yuv2rgb/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/README.md>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/test_yuv_rgb.c>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/yuv_rgb.c>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/yuv_rgb.h>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/1fc2be8f22a961e757bbe2dff608dc073e914d03/yuv_rgb.c>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/1fc2be8f22a961e757bbe2dff608dc073e914d03/README.md>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/1fc2be8f22a961e757bbe2dff608dc073e914d03/test_yuv_rgb.c>
  - <https://raw.githubusercontent.com/descampsa/yuv2rgb/434fed1bcea70a1eb1ab8ded3f5a7303e04d4721/yuv_rgb.c>
  - https://packages.debian.org/ja/jessie/libav-tools (WebSearch snippet only)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/descampsa/yuv2rgb`) · [data/wave10/enrich/raw/github_com_descampsa_yuv2rgb.json](../../../data/wave10/enrich/raw/github_com_descampsa_yuv2rgb.json) (enrichment confidence 0.8)

</details>
