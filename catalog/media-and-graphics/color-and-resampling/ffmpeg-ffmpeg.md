# FFmpeg (libswscale and filters)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1-or-later (optional parts make the build GPL-2.0-or-later when configured with --enable-gpl, per LICENSE.md); libswscale and vf_convolution.c are LGPL` · 🟢 active

> FFmpeg's libswscale and libavfilter (scale, crop, convolution) run the vips-bench crop/resize/sharpen job about 2.1x faster than ImageMagick 7.

| | |
|---|---|
| **Beats** | ImageMagick 7.1.1 (magick, convert) |
| **Claimed result** | libvips wiki table (AMD Ryzen Threadripper PRO 3955WX, Ubuntu 25.04, run 12 Aug 2025): ffmpeg 7.1.1 2.06 s and 1338.36 MB peak vs magick 7.1.1 4.41 s / 1500.52 MB and convert 7.1.1 4.44 s / 1499.29 MB, 2.1x faster (derived from page data); the page's 'times slower than libvips' column reads ffmpeg 3.61 vs magick 7.74. |
| **Workload** | libvips vips-bench (ffmpeg.sh vs im7.sh/im.sh, driver benchmark.sh): the ffmpeg 7.1.1 CLI reads the 10000x10000 8-bit RGB image as a strip TIFF (x-strip.tif; benchmark.sh notes ffmpeg does not support tiled TIFF), crops 100 px per edge (crop filter), scales to 90 percent with the scale filter at libswscale's default SWS_BICUBIC (ffmpeg.sh passes no flags), runs a 3x3 sharpen (kernel sum 8, divided by 8) through the convolution filter, which accepts planar formats only, and writes a TIFF. ImageMagick 7.1.1 reads the tiled TIFF with crop-on-load, resizes 90 percent with -filter triangle and convolves the same 3x3 kernel; its script also runs vipsheader twice inside the timed command. Quickest real time of five runs, OMP_NUM_THREADS=16. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3955WX 16-core, Ubuntu 25.04 (run 12 Aug 2025 by the libvips maintainers) |
| **Compiler and flags** | Not stated (Ubuntu packages). |
| **Adoption** | 64.7k stars (GitHub mirror); ubiquitous media framework |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/FFmpeg/FFmpeg) · [benchmark](https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md) |

## Verdict

The libvips maintainers' Speed-and-memory-use table (AMD Ryzen Threadripper PRO 3955WX, Ubuntu 25.04 packages, quickest real time of five runs, whole process including TIFF I/O) lists ffmpeg 7.1.1 at 2.06 s and 1338.36 MB peak against magick 7.1.1 at 4.41 s / 1500.52 MB and convert 4.44 s / 1499.29 MB, about 2.1x faster (derived from page data). Per the 7.1 code, the timed ffmpeg run is strip-TIFF decode, crop, swscale bicubic resize with RGB24 to YUV444P conversion, SSE4 3x3 sharpen on Y/Cb/Cr, and a PackBits YCbCr TIFF write, so it is not the same pixel pipeline as ImageMagick's RGB one.

## Use it when

- Frames are already in an FFmpeg pipeline (decode, filter, encode) and you need resize, crop or format conversion without leaving libav\*: libswscale is the standard choice there.
- Batch command-line jobs on many-core x86-64 boxes where ImageMagick 7 is the current tool and the format is something FFmpeg reads (strip TIFF, PNG, JPEG, video frames). In the libvips table, ffmpeg 7.1.1 took 2.06 s versus 4.41 s for magick on a 16-core Threadripper PRO 3955WX, with about 160 MB less peak memory (1338 MB versus 1500 MB).
- Pixel-format conversion between YUV and RGB families with many supported layouts (8-16 bit, planar and packed, alpha), where breadth matters more than the last factor of speed.
- Simple fixed-kernel sharpen or blur on 8-bit planar data: the convolution filter's SSE4 3x3 path plus slice threading is cheap to use from a filter string.

## Skip it when

- Still-image batch processing where speed and memory matter most. In the same table libvips (vips-c 8.18) took 0.57 s and 94 MB against ffmpeg's 2.06 s and 1338 MB, and GraphicsMagick 1.4 matched ffmpeg (2.05 s).
- High-quality resizing in a video pipeline: zimg's README reports a Lanczos FHD-to-UHD resize in 7.7 ms versus 15.2 ms for swscale 4.0.2 (i7-8565U), and libyuv-style converters beat swscale on YUV/RGB conversion.
- RGB-exact or colour-managed image work. Filters that accept only planar formats force hidden conversions, and with the vips-bench filter string the RGB image is converted to limited-range YUV 4:4:4 before the sharpen (see gotchas).
- Tiled TIFF input: the benchmark had to feed ffmpeg a strip TIFF because its TIFF decoder does not read tiled TIFF (benchmark.sh comment).
- Projects that cannot accept LGPL obligations, or builds configured with --enable-gpl (then GPL-2.0-or-later).

## How it is fast

libswscale (the 7.1 'legacy' backend) is a separable two-pass scaler. Each input line is converted to a planar intermediate (hand-written SIMD for packed RGB24 to Y/UV in x86 input.asm), filtered horizontally with precomputed per-pixel taps into 15-bit samples (hscale8to15 kernels specialised by filter size, AVX2 versions in scale_avx2.asm), then combined vertically from a ring buffer of lines (yuv2planeX, AVX2 yuv2yuvX). The scale filter hands swscale the filter graph's thread count, so it runs slice-threaded. The convolution filter is slice-threaded too, and for 8-bit 3x3 kernels on x86-64 it uses the ff_filter_3x3_sse4 assembly kernel. Master adds a new graph-based swscale with chained 'ops' SIMD kernels, a JIT and a Vulkan SPIR-V backend, but swscale.h says these backends are auto-selected only with SWS_UNSTABLE.

## Compared with alternatives

Pick FFmpeg when the data already lives in an FFmpeg decode/encode pipeline or you need its breadth of pixel formats. Pick libvips for still-image batch work (3.6x faster than ffmpeg in the same table with about a fourteenth of the peak memory, derived from page data). Pick zimg for higher-quality, faster resampling of video frames, and libyuv or yuv2rgb for raw YUV/RGB conversion.

## Integration

| | |
|---|---|
| **Form** | shared or static libraries (libswscale, libavfilter, libavutil, plus libavcodec/libavformat for file I/O) built with FFmpeg's configure/make, or the ffmpeg CLI |
| **Dependencies** | libswscale needs only libavutil. libavfilter's scale filter needs libswscale. Reading and writing TIFF needs libavcodec and libavformat. The x86 SIMD sources are NASM-syntax .asm files, so an assembler is needed at build time to get the fast paths. |
| **Minimum toolchain** | Not documented in the files read this session (FFmpeg's configure script sets the requirements). |
| **Platforms** | Any OS FFmpeg builds on. libswscale has SIMD directories for x86, aarch64, arm, loongarch, ppc and riscv, and master adds a Vulkan backend. On x86 the AVX2 horizontal scaler is skipped on CPUs flagged SLOW_GATHER (AMD family 0x19 and earlier, Intel Haswell-class), so the 3955WX in the benchmark ran the SSE-class hscale kernels. |
| **Thread safety** | SwsContext has a threads field (0 = automatic) for internal slice threading. In libavfilter, slice threading follows the filter graph's thread count. Concurrent use of one SwsContext from several threads is not documented in the headers read. |
| **Drop-in for the baseline** | no |

## Gotchas

- Hidden format conversion: in release/7.1, convolution accepts only planar formats (no packed RGB24), and the TIFF encoder accepts RGB24, RGBA, gray, PAL8 and planar YUV but not GBRP. Format negotiation therefore picks YUV444P as the closest common format to the RGB24 input (pick_format with av_find_best_pix_fmt_of_2), and the encoder declares limited-range YUV. The vips-bench command sharpens Y, Cb and Cr planes and writes a YCbCr TIFF, not an RGB one. Insert format=gbrp before convolution and convert back to rgb24 explicitly if you need RGB output, and check the choice with -loglevel debug ('picking ... out of').
- Defaults differ from ImageMagick: the scale filter passes no flags, so libswscale uses its SWS_BICUBIC default. ffmpeg's TIFF encoder compresses with PackBits by default (compression_algo), while ImageMagick writes uncompressed TIFF here. Both add work on ffmpeg's side, so they do not inflate its result, but outputs are not byte-comparable.
- Speed depends on CPU generation and backend: the AVX2 gather-based hscale is disabled on Zen 1-3 and Haswell, and the new swscale ops/JIT backends in master are used only with SWS_UNSTABLE ('may be faster, slower, or produce different output').
- The GitHub repository is a read-only mirror. Its README says GitHub pull requests are ignored and patches go to the ffmpeg-devel mailing list, so do not look for bug reports or reviews there.

## Known shortcomings

- libswscale resize at B on the libvips maintainers' wiki run (Threadripper PRO 3955WX, Ubuntu 25.04 packages, 12 August 2025): ffmpeg 7.1.1 2.06 s vs ImageMagick magick 4.41 s. Work is not identical: ffmpeg.sh reads a strip TIFF and uses swscale's default SWS_BICUBIC while im7.sh reads a tiled TIFF, crops on load and uses -filter triangle; the test is IO-dominated. No flags.
- Retiered B to C (retier-10): the libvips wiki's 2.06 s row (dated 12 Aug 2025) cannot come from the committed vips-bench scripts, because ffmpeg.sh was first committed 2025-09-21 and benchmark.sh passed an '-o' option that ffmpeg 7.1 rejects until commit c4dbb24 (2026-04-12), with no re-run afterwards. The pipeline also does different work: FFmpeg's convolution filter is planar-only and tiffenc lacks GBRP, so it converts to limited-range YUV444P, sharpens Y, Cb and Cr and writes a PackBits YCbCr TIFF, not ImageMagick's RGB output.

## Caveats and trade-offs

One trivial I/O-dominated test (the wiki says it flatters libvips), so the 2.1x mostly reflects TIFF reading and writing and pipeline overhead rather than swscale itself. The pipelines are not identical: ffmpeg reads the strip TIFF (it does not support tiled TIFF) and resamples with libswscale's default bicubic filter (a wider kernel than ImageMagick's triangle), while ImageMagick reads the tiled TIFF with crop-on-load, resizes with -filter triangle, and its script runs vipsheader twice inside the timed command. vips-bench issue 8 (homm, 2017, about Pillow) notes that libvips uses 4-point bilinear interpolation while ImageMagick and GraphicsMagick use convolution resizing, so resampling differs per program. Distribution packages with no compiler or flags. Already recorded entries (zimg, yuv2rgb) use libswscale as their baseline rather than ImageMagick. FFmpeg becomes GPL-2.0-or-later when configured with --enable-gpl. [retier] The 2.06 s row is not reproducible from the committed vips-bench scripts: ffmpeg.sh postdates the wiki date (first commit 2025-09-21) and benchmark.sh passed an '-o' option that ffmpeg 7.1 rejects until 2026-04-12, with no re-run afterwards. Output is not equivalent to ImageMagick's: FFmpeg converts to limited-range YUV444P, sharpens the Y, Cb and Cr planes and writes a PackBits YCbCr TIFF. One trivial I/O-dominated test (the wiki says it flatters libvips), so the ratio mostly reflects TIFF reading and writing and pipeline overhead rather than libswscale; ffmpeg reads the strip TIFF and resamples with libswscale's default bicubic while ImageMagick reads the tiled TIFF with crop-on-load and -filter triangle.

The measured tool is the ffmpeg command line, not a lean resize library; peak memory 1338.36 MB. GitHub lists LGPL-2.1 with GPL-2.0 and GPL-3.0 options for some components.

## Maintenance

Very active (last commit 2026-10-03, libswscale major version 10 on master with a new frame-based API). LGPL-2.1-or-later unless built with --enable-gpl. Usable as libraries, but too large to vendor piecemeal.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now C.
- **Tier reason:** The libvips wiki Speed-and-memory-use table is the libvips maintainers' measurement, independent of both FFmpeg and ImageMagick, with public scripts in libvips/vips-bench (ffmpeg.sh, im7.sh, im.sh, benchmark.sh) and a named CPU (Threadripper PRO 3955WX, Ubuntu 25.04, run 12 Aug 2025). All tools are Ubuntu packages with no compiler or flags stated, so B, not A (same call as the GraphicsMagick entry in batch-16).
- **Retiered** B to C: Lowered B to C on the enricher's provenance and equivalence findings (DASP precedent): the libvips wiki row is dated 12 Aug 2025 but vips-bench's ffmpeg.sh was first committed 2025-09-21, and until commit c4dbb24 (2026-04-12) benchmark.sh passed '-o' as its second argument, which ffmpeg 7.1 rejects ('Unrecognized option'), so the committed driver could not have produced the 2.06 s row and the row was not re-run after the fix. The compared work also differs: FFmpeg's convolution filter is planar-only and tiffenc lacks GBRP, so the pipeline converts to limited-range YUV444P, sharpens Y, Cb and Cr and writes a PackBits YCbCr TIFF, not the RGB output ImageMagick produces. The independent measurement exists but is not reproducible from the public scripts, so first-party-grade evidence at most.
- **Verifier notes:** All numbers are on the wiki page in the ffmpeg, magick and convert rows. The record wrongly said ffmpeg read the tiled TIFF and used bilinear: ffmpeg.sh reads x-strip.tif and leaves libswscale at its SWS_BICUBIC default (libswscale/options.c, doc/scaler.texi in release/7.1), which is more resampling work than ImageMagick's triangle filter, so the difference does not favour ffmpeg. Metadata checked on github.com: GitHub mirror of git.ffmpeg.org, 64.7k stars, last commit 2026-10-03 (active).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `hardware`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md>
  - <https://github.com/libvips/vips-bench>
  - <https://raw.githubusercontent.com/jcupitt/vips-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/ffmpeg.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im7.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/benchmark.sh>
  - <https://github.com/libvips/vips-bench/issues/8>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libswscale/options.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libavfilter/vf_scale.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/doc/scaler.texi>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libavfilter/vf_convolution.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/fftools/cmdutils.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/LICENSE.md>
  - <https://github.com/FFmpeg/FFmpeg>
  - <https://github.com/FFmpeg/FFmpeg/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/_history>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/112504a>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/b1a4934>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/73718d9>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/_compare/112504a>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/_compare/b1a4934>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/_compare/f01f393>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/_compare/16a358f>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/_compare/73718d9>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/_compare/349e221>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/ffmpeg.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im7.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/benchmark.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/README.md>
  - <https://github.com/libvips/vips-bench/commits/master/ffmpeg.sh>
  - <https://github.com/libvips/vips-bench/commit/e42117f57d589a385e916e3a61cb6f54a6da4abc>
  - <https://github.com/libvips/vips-bench/commit/c4dbb24ae3dc78f030c4bdfd6ea7e4bfcda0503f>
  - <https://github.com/libvips/vips-bench/issues?q=ffmpeg>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libavcodec/tiffenc.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libavfilter/vf_convolution.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libavfilter/x86/vf_convolution_init.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libavfilter/vf_scale.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libavfilter/avfiltergraph.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/fftools/ffmpeg_filter.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/fftools/ffmpeg_opt.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/fftools/cmdutils.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libswscale/options.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libswscale/x86/scale_avx2.asm>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libswscale/x86/input.asm>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libswscale/x86/swscale.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/7.1/libavutil/x86/cpu.c>
  - <https://github.com/FFmpeg/FFmpeg/tree/release/7.1/libswscale/x86>
  - <https://github.com/FFmpeg/FFmpeg/tree/master/libswscale>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/README.md>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/LICENSE.md>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libswscale/swscale.h>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libswscale/version_major.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/ffmpeg/ffmpeg`) · [data/wave10/enrich/raw/github_com_ffmpeg_ffmpeg.json](../../../data/wave10/enrich/raw/github_com_ffmpeg_ffmpeg.json) (enrichment confidence 0.6)

</details>
