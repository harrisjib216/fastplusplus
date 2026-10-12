# gif_load

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (ANSI C single header)` · `Unlicense` · 🟢 active

> Public-domain single-header C animated-GIF decoder; with the file cached it decodes 1.3-1.7x faster than giflib 5.2.2.

| | |
|---|---|
| **Beats** | giflib 5.2.2 (also stb_image) |
| **Claimed result** | README tables (best of two runs, wall time in ms): warm cache, gif_load read() beats giflib 5.2.2 stream by 1.28x-1.72x and mmap() by 1.42x-1.78x (derived from page data; README says 1.3x-1.7x), and beats stb_image by 1.4x-2.5x per the README (derived from page data: 1.39x-2.42x for the +RGBA rows, which composite like stb_image), e.g. 1080p shapes 668 ms (read) vs giflib stream 1149 ms vs stb_image 1829 ms. Cold cache vs giflib stream: 1.3x-1.5x faster on the 3 shape GIFs (derived from page data: 1.42x-1.51x with read()) but slower on the 3 noise GIFs; the README states 0.83x-0.85x, while its own table gives 0.89x-0.91x with read() and 0.75x-0.79x with mmap() (derived from page data). Author says the 1.3x-1.5x cold claim also holds on real giphy GIFs (no numbers). Peak memory: one frame plus a 16 KB code table; at 1080p giflib slurp holds 296 MB and stb_image 1254-1611 MB, while giflib stream holds a single row and is lower than gif_load. |
| **Workload** | Wall-time decode of every frame of 6 synthetic animated GIFs (320x240 x100, 640x480 x200, 1920x1080 x150; flat shapes and incompressible noise), file read into RAM with read() or mmap(), cold and warm page cache. |
| **Metric** | throughput |
| **Hardware** | CPU model not stated (RAM latency 128 ns, 8 GB/s sequential read, EXT4 cold disk read 342 MB/s) |
| **Compiler and flags** | GCC 11.5 -O2, Linux 6.4 |
| **Adoption** | 85 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/hidefromkgb/gif_load) · [benchmark](https://github.com/hidefromkgb/gif_load) |

## Verdict

First-party README only: on an unnamed Linux 6.4 machine (GCC 11.5 -O2), wall time including reading the file, best of two runs, to decode all frames of six synthetic non-interlaced GIFs (320x240 x100, 640x480 x200, 1920x1080 x150; flat shapes and noise). With a warm cache gif_load beat giflib 5.2.2 by 1.28x-1.72x and stb_image by 1.39x-2.42x on the compositing +RGBA rows. Cold, it won 1.42x-1.51x on shapes but lost on noise; the prose figure of 0.83x-0.85x matches neither the read() row (0.89x-0.91x) nor the mmap() row (0.75x-0.79x) but roughly their average (about 0.83x-0.84x, derived from page data). The timed code (commit 5a961ff) differs from HEAD only by the 2026-10-01 one-byte bounds check, but the harness and CPU are not published, and stb_image's figure includes its known O(N^2) realloc-and-copy of the whole animation buffer (open stb issue #1883), so the stb gap partly measures that rather than LZW speed.

## Use it when

- Animated GIFs already in memory (asset packs, network buffers, mmap'd files) where you want per-frame palette indices and do your own compositing or GPU palette lookup: warm-cache wall time was 1.28x-1.72x better than giflib's line-by-line API on the author's six test GIFs.
- Long or high-resolution animations where stb_image's whole-animation RGBA buffer is too big: at 1080p x150 frames stb_image peaked at 1254 MB (shapes) and 1611 MB (noise) versus 52-60 MB and 409-418 MB for gif_load, most of which is the GIF file itself.
- Embedded, freestanding or no-libc builds: under 300 lines of C89 plus stdint.h, the only external call is realloc (replaceable with GIF_MGET), and a call makes exactly one allocation (largest frame + 16 KB + 2 bytes).
- Projects that need to vendor a decoder with no licence obligations: Unlicense public-domain dedication in the header.
- Progressive display of a GIF still downloading, at whole-frame granularity, by calling again with skip set to the frames already shown.

## Skip it when

- Cold reads of large or poorly compressible GIFs from disk: the whole file must be in memory before the first pixel, so giflib, which overlaps reading with decoding, won on the three noise GIFs (gif_load at 0.89x-0.91x with read() and 0.75x-0.79x with mmap(), derived from page data).
- Minimal-memory streaming: giflib's line API holds a single row, while gif_load holds the whole file (twice with read(): page cache plus copy) and a full-frame buffer.
- When you want ready-to-use RGBA frames: deinterlacing, disposal modes, transparency and frames that extend past the logical screen are all the caller's job (the README's own C example carries a TODO for out-of-bounds frames).
- Lenient decoding of oddly encoded files: a frame whose LZW data does not begin with a clear code is rejected (gif_load.h line 104 returns -2, though GIF89a only says encoders 'should' emit one), and a frame with another sub-block after the end-of-information code is refused (tests/extradata.gif returns 0); either one stops loading at that frame. Found by code reading; the first case has no test.
- Old vendored copies (the 2019 header, before 2026-09-27): issue #14 integer overflow of the frame-buffer size where long is 32 bits (all Windows, all 32-bit targets) giving an undersized buffer and heap out-of-bounds access, NULL dereference on failed allocation, uninitialised pixels on short streams and rejected palette-less GIFs; issue #15 (1-byte over-read at a trailing 0x21) was fixed on 2026-10-01.

## How it is fast

Each LZW code-table entry is packed into one uint32_t (prefix code in bits 0-11, string length in bits 12-23, last byte in bits 24-31). Because the string length is known up front, the decoder writes each string straight into the frame buffer back to front by following prefix links, with no temporary stack and no per-row copy. Codes are pulled from the sub-blocks 16 bits at a time into a bit accumulator. A first pass only skips sub-blocks to count frames and find the largest one; then one allocation holds the 16 KB code table directly in front of a frame buffer that is reused for every frame. Output stays as palette indices, and there is no I/O layer in the decode loop because the whole GIF is one in-memory buffer.

## Compared with alternatives

Among the catalogued GIF entries, giflib-turbo patches giflib's own LZW decoder, so it keeps the giflib API, but its 2.5x-30x claim comes with no harness, machine or images; pick gif_load when you can hold the file in memory and want a dependency-free public-domain header with published, if unreproducible, timings. msf_gif is an encoder and does not compete here.

## Integration

| | |
|---|---|
| **Form** | header-only (gif_load.h; can also be built as a shared library with GIF_EXTR) |
| **Dependencies** | none beyond stdint.h; realloc from stdlib.h by default, replaceable through the GIF_MGET macro |
| **Minimum toolchain** | ANSI C / C89 plus stdint.h (the test suite builds it with -std=c89 -pedantic -Wall -Wextra -Wno-long-long without warnings); usable from C++ via extern "C"; MSVC build line given in the README |
| **Platforms** | any; little-endian by default, big-endian targets must define GIF_BIGE=1; relies on unaligned 16-bit loads |
| **Thread safety** | Not documented; GIF_Load has no global or static mutable state and works only on its own allocation and the caller's context pointer, so concurrent calls on different buffers are safe (inferred from the source). |
| **Drop-in for the baseline** | false: one call with per-frame callbacks instead of giflib's DGifOpen/DGifSlurp/DGifGetLine; input must be in memory, and the caller does deinterlacing, compositing and disposal that DGifSlurp or stb_image do for you |

## Gotchas

- A positive return value is documented as the total frame count of a properly terminated GIF, but if a frame fails to decode in such a file, loading stops and the return value is the number of frames delivered so far, still positive; compare it with whdr-&gt;nfrm from the callback to detect truncation (traced in GIF_Load, lines 260-264 and 292).
- LZW codes are read as \*(uint16_t\*) at arbitrary byte offsets (lines 104 and 112): unaligned, type-punned loads that work on x86 and ARM but are undefined behaviour in C and trip -fsanitize=alignment or strict-alignment CPUs.
- whdr-&gt;bptr is one buffer reused for every frame, and cpal is NULL with clrs 0 when the file has no palette; copy what you need inside the callback.
- The default GIF_MGET frees with realloc(m, 0), which the header itself warns does not free on some systems; define GIF_MGET with malloc/free there, as the README shows.

## Known shortcomings

- Numbers only in the README Performance section (commit 2026-09-27; GCC 11.5 -O2, Linux 6.4, no CPU model) with the harness unpublished (tests/ checks accuracy only). README prose (cold-noise 0.83x-0.85x) contradicts its own table (0.89x-0.91x read, 0.75x-0.79x mmap). A 1-byte out-of-bounds read was fixed on 2026-10-01, after the numbers.
- The prose cold-noise figure of 0.83-0.85x is roughly the average of the read and mmap rows, and part of the stb_image gap is stb's O(N^2) realloc of the whole animation (stb issue #1883). From code reading: a frame without a leading clear code is rejected (line 104, return -2), an extra sub-block after EOI is refused, a mid-animation decode failure returns a positive smaller count despite the README, uint16_t loads are unaligned type-punned, and the 2019 vendored copies carry the issue #14 overflow and NULL bugs.

## Caveats and trade-offs

The README says 'take everything below with a grain of salt' and that the harness is not published, so the numbers are not reproducible from the repo; no CPU model is given (only RAM latency 128 ns, 8 GB/s sequential read, EXT4 cold read 342 MB/s); synthetic GIFs only; best of two runs; timing includes file acquisition. The README's cold-cache noise ratio (0.83x-0.85x) does not match its own table. Work is comparable only because the test GIFs are not interlaced: gif_load leaves deinterlacing to the caller while giflib DGifSlurp does it; the plain rows return palette indices, so only the +RGBA rows match stb_image's composited output. giflib stream uses less memory than gif_load. Recent fixes landed around the measurement: int32 overflow and null-palette fix (2026-09-27) and a 1-byte out-of-bounds read at GIF_EHDM (2026-10-01, after the numbers were published). Public-domain dedication (Unlicense text in gif_load.h): no patent grant.

Whole file must be in memory before decoding (cannot overlap I/O with decode, which is why cold noise cases lose to giflib). Callback API, header-only, under 300 lines, no libc dependency apart from realloc. Interlaced GIFs are the caller's job to unwind (giflib's DGifSlurp does it). Public-domain dedication (no patent grant).

## Maintenance

Revived after seven idle years by a hardening burst (2026-09-27 to 2026-10-01: overflow, NULL and over-read fixes plus a valgrind-checked accuracy suite); Unlicense and under 300 lines, so vendor the current header rather than any 2019 copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The numbers live only in the README 'Performance' section (added in commit 'Add performance stats', 2026-09-27): first-party wall times vs giflib 5.2.2 and stb_image, GCC 11.5 -O2 on Linux 6.4, but no CPU model and, as the author states, the harness is not published (tests/ holds only accuracy tests: run.sh, gif_test.c). Number without harness or CPU model is C.
- **Verifier notes:** Numbers match the README tables; the warm-cache headline ratios check out, but the cold noise ratio in the prose (0.83x-0.85x) disagrees with the table (0.89x-0.91x read, 0.75x-0.79x mmap). giflib is a recognisable GIF incumbent, not in the category's listed baselines (libjpeg-turbo, libpng, libwebp, libavif), so baseline_in_list false is right. Metadata (Unlicense, 85 stars, last commit 2026-10-01, active) checked.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/hidefromkgb/gif_load>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/HEAD/README.md>
  - <https://github.com/hidefromkgb/gif_load/commits/master>
  - <https://github.com/hidefromkgb/gif_load/tree/master/tests>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/HEAD/gif_load.h>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/HEAD/tests/run.sh>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/HEAD/tests/gif_test.c>
- **Sources the enricher read:**
  - <https://github.com/hidefromkgb/gif_load>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/HEAD/README.md>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/HEAD/gif_load.h>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/5a961ff/gif_load.h>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/74b674d/gif_load.h>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/HEAD/tests/run.sh>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/HEAD/tests/gif_test.c>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/HEAD/tests/README.md>
  - <https://raw.githubusercontent.com/hidefromkgb/gif_load/HEAD/tests/expected-synthetic.txt>
  - <https://github.com/hidefromkgb/gif_load/commits/master>
  - <https://github.com/hidefromkgb/gif_load/commit/5b22e9c>
  - <https://github.com/hidefromkgb/gif_load/issues?q=is%3Aissue>
  - <https://github.com/hidefromkgb/gif_load/issues/11>
  - <https://github.com/hidefromkgb/gif_load/issues/14>
  - <https://github.com/nothings/stb/issues/1883>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/hidefromkgb/gif_load`) · [data/wave10/enrich/raw/github_com_hidefromkgb_gif_load.json](../../../data/wave10/enrich/raw/github_com_hidefromkgb_gif_load.json) (enrichment confidence 0.8)

</details>
