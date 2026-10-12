# TinyTIFF

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-3.0` · 🟡 stale

> Small C library that appends fixed-size uncompressed frames to a multi-page TIFF with less per-frame overhead than libTIFF.

| | |
|---|---|
| **Beats** | libTIFF (libtiff 3.8.2 and 4.6.0) |
| **Claimed result** | Per-frame write times in doc/images/performance_measure_ssd.ods (Ryzen 7 5800H, Win11, SSD, 64-bit Release, libTIFF 4.6.0; units not labelled): 64x64 16-bit frames, speedup column 1.59x at 10 frames, 2.63-2.78x at 100 to 10,000 frames, 1.79x at 100,000 and 3.10x at 1,000,000; frame-size sweep 32x32 to 4096x4096: 5.11x, 1.67x, 3.11x, 5.15x, 4.49x, 2.06x, 1.81x, 1.51x (4096x4096: 70.2 vs 106.2 per frame). README prose: 1.5-3x over frame count and 1.5-5x over frame size on the SSD. Hard-disk run in doc/images/performance_measure.ods (Ryzen 5 3600, Win10, 32-bit Release, libTIFF 3.8.2): speedup grows with frame count from 1.77x at 10 frames to 2421x at 100,000 frames (libTIFF 205.8 vs TinyTIFF 0.085 per frame) and is 289-3674x for 32x32 to 256x256 frames, because libTIFF 3.8.2's per-frame time grows with the number of frames already written; for large frames TinyTIFF was slower there: 0.19x at 1024x1024 (22.28 vs 4.21), 0.96x at 2048x2048, 0.73x at 4096x4096. Write side only. |
| **Workload** | Writing many small uncompressed 16-bit frames (64x64, 10 to &gt;100000 frames) and frames of 64x64 to 4096x4096 into one multi-frame TIFF, compared with libTIFF and with raw fwrite(), using the repo's tests/tinytiffwriter_speedtest program. |
| **Metric** | throughput |
| **Hardware** | Ryzen 5 3600+, Win10, hard disk, libTiff 3.8.2; Ryzen 7 5800H, Win11, SSD, libTiff 4.6.0 |
| **Compiler and flags** | Release builds (32-bit on the Win10 run, 64-bit on the Win11 run); compiler and flags not stated |
| **Adoption** | 163 stars; vcpkg port tinytiff |
| **Last commit** | 2024-05-22 |
| **Links** | [repository](https://github.com/jkriege2/TinyTIFF) · [benchmark](https://github.com/jkriege2/TinyTIFF) |

## Verdict

The author's tinytiffwriter_speedtest writes 64x64 16-bit greyscale frames and a frame-size sweep, timing each frame with QueryPerformanceCounter and reporting a trimmed mean in ms per frame. Against libTIFF 4.6.0 on a Ryzen 7 5800H (Windows 11, SSD, 64-bit Release, compiler not stated), TinyTIFF was 1.6-2.8x faster for 10 to 100,000 frames and 1.5-5.1x faster across frame sizes; against libTIFF 3.8.2 on a Ryzen 5 3600 (Windows 10, hard disk, 32-bit Release), the gap grew with frame count to 2421x at 100,000 frames, but TinyTIFF was slower from 1024x1024 upward.

## Use it when

- Streaming fixed-size camera or microscope frames (8-64-bit integer or float, greyscale or RGB(A)) into one uncompressed multi-page TIFF that ImageJ/Fiji or libTIFF will read later, as long as the file stays under 4 GB.
- Many small frames, where per-frame overhead dominates: on the author's SSD run against libTIFF 4.6.0, 64x64 16-bit frames took 0.018-0.022 ms vs 0.05-0.06 ms per frame (2.6-2.8x) for 100 to 10,000 frames, and 128x128 to 512x512 frames were 3.1-5.1x faster.
- Code still linked against old libTIFF 3.x, whose per-frame write time grows with frame count (205.8 ms vs 0.085 ms per 64x64 frame at 100,000 frames on the author's hard-disk run).
- Projects that want a small C dependency with no zlib, libjpeg or libTIFF behind it, for both writing and reading simple stacks.

## Skip it when

- Output that can exceed 4 GB. There is no BigTIFF; libTIFF 4.x opened with mode "w8" writes BigTIFF. Builds without ftello64/_ftelli64 detected at configure time are limited to 2 GB. Issue #23 (files over 2 GB fail to open in ImageJ, Nov 2023) is still open, although release 4.0.0.0 (May 2024) improved 2-4 GB handling.
- Compressed (LZW, Deflate, JPEG), tiled, palette or pyramidal TIFF, frames that change size or type within a file, or rich metadata (OME-XML, per-frame tags). The writer emits a fixed tag set with resolution 1/1 and a single ImageDescription of at most 1024 characters, and only in the first frame.
- Large frames, where the disk is the bottleneck. On the SSD the gain shrinks to 1.5-2.1x from 1024x1024 upward. On the author's 2020 hard-disk run TinyTIFF was slower than libTIFF 3.8.2 at 1024x1024 (22.28 vs 4.21 ms per frame), 2048x2048 and 4096x4096.
- Reading untrusted TIFF files. Issue #35 (June 2026, no maintainer reply) reports a reproducible memory-safety bug reachable through TinyTIFFReader_open on malformed input; two earlier security reports (#19, #20) were closed in April 2024.
- Projects that cannot accept LGPL-3.0. Issue #16 asks for BSD or dual licensing and is still open.

## How it is fast

All frames share one shape, so the writer reserves a fixed IFD block per frame (500 bytes, at most 20 entries plus space for rational and array values), assembles it in a reused memory buffer, and issues two fwrite calls per frame: the IFD, then the pixels as a single strip in host byte order, with no copy or byte swap. The next-IFD pointer is computed arithmetically from the known frame size, so the writer never seeks back or walks the directory chain; it seeks only at close to end the chain and fill in the ImageDescription. libTIFF 3.8.2's per-frame time grows with the number of directories already written, consistent with walking the IFD chain to link each frame, while libTIFF 4.6.0 caches the last directory offset (tif_lastdiroff in TIFFLinkDirectory) and stays flat. Against current libTIFF the remaining gain (1.5-5x on the author's SSD) comes from libTIFF's per-frame tag serialisation, its roughly 8 KB TIFFDefaultStripSize strips, and the harness's strip-copy loop, not from a different I/O technique.

## Compared with alternatives

None of the catalogued image-codecs siblings writes TIFF; they are PNG, JPEG, QOI or texture codecs, all of which compress. Pick TinyTIFF when you need an uncompressed multi-page TIFF stack that scientific tools open directly, and one of the PNG/QOI encoders (fpng, fpnge, QOI) when the frames are standalone images and size on disk matters.

## Integration

| | |
|---|---|
| **Form** | static or shared lib (CMake; BUILD_SHARED_LIBS defaults to ON; targets TinyTIFF::TinyTIFF and the header-only TinyTIFF::TinyTIFFXX C++ helpers in tinytiff_tools.hxx); vcpkg port 'tinytiff' |
| **Dependencies** | none (libTIFF only for the optional comparison tests) |
| **Minimum toolchain** | C core (pure C since 3.0.0.0; no C standard pinned in CMake), CMake 3.10+; C++ only for the .hxx helpers and tests |
| **Platforms** | Windows (MSVC CI) and Linux (CI); stdio file I/O, with an optional WinAPI path; writes files in host byte order; the reader byte-swaps opposite-endian files |
| **Thread safety** | not documented; each writer and reader handle keeps its own state and the writer has no mutable globals, so separate handles on separate threads look safe from the code |
| **Drop-in for the baseline** | no |

## Gotchas

- Check every TinyTIFFWriter_writeImage return value. When the next frame would push the file past the size limit (0xFFFFFFFE minus 1 KB with 64-bit ftell, otherwise 2 GB), the writer has already written and linked that frame's IFD before it returns false without the pixels. On close the chain therefore ends in a frame whose strip lies beyond the end of the file, and every further call appends another data-less IFD.
- TinyTIFFWriter_writeImagePlanarReorder (interleaved input, planar output) is wrong for samples wider than 8 bits. In tinytiffwriter.c the source index sampidx counts samples but is used as a byte offset into the input, so 16-, 24-, 32- and 64-bit samples are copied from the wrong bytes (derived from reading the code). Issue #32 ('Cannot write RGB images', open) uses this path. The planar-to-chunky direction indexes bytes correctly.
- Without large-file support detected, TINYTIFF_MAX_FILE_SIZE is defined as (2\*1024\*1024\*1024-1), an int expression that overflows, so that build's limit depends on the compiler.
- Issue #21 (RGBA writes missing the alpha channel) is open. Frames must all match the shape given to TinyTIFFWriter_open; there is no per-frame size or type.

## Known shortcomings

- First-party harness tests/tinytiffwriter_speedtest with .ods result sheets; CPUs named but compiler and flags not. SSD run with libTIFF 4.6.0 gives 1.51-5.15x (both sides uncompressed, stripped), but libTIFF writes about 8 KB strips and the timed path includes a copy loop, so the comparison is not configuration-matched. The HDD run (libTIFF 3.8.2, up to 2421x) also shows TinyTIFF slower at 1024x1024 and above (0.19x), and the 1,000,000-frame row is about 8.2 GB, past the 4 GB TIFF limit, so it is not a valid-file comparison.
- The 1,000,000-frame SSD row (3.10x) is invalid on both sides: the SSD sheet was committed 2024-04-30 on pre-fix code whose 32-bit ftell broke offsets past 2 GB (issue #23; the writer now checks TINYTIFF_MAX_FILE_SIZE since 54e8391 of 2024-05-08 but still writes IFDs and skips pixels past the limit), while libTIFF 4.6.0 refuses classic writes past 4 GB and prints from its error handler inside the timed loop, and the harness ignores every return value. The HDD frame-size sweep varies the frame count (10,000 down to 50), so the 289-3674x ratios are a frame-count effect; the RAW reference is opened in text mode. Code bugs not behind the numbers: writeImagePlanarReorder is wrong for samples above 8 bits (sample index used as byte offset; likely issue #32); open reader memory-safety report #35 has no maintainer reply.

## Caveats and trade-offs

First-party; compiler and flags are not stated ('Release-build' only), so not tier A. The harness writes all TinyTIFF configurations, then all raw fwrite() configurations, then all libTIFF configurations, one run each; TinyTIFF beating raw fwrite() in several SSD rows (256x256: 0.103 vs 0.373 for raw) shows run-to-run noise of the same order as some of the gaps. The files are equivalent in kind (uncompressed, stripped, contiguous 16-bit greyscale on both sides), but libTIFF writes TIFFDefaultStripSize strips (about 8 KB, so many strips per large frame) while TinyTIFF writes one strip per frame, and the libTIFF helper TIFFTWriteUint16 copies each strip into a freshly allocated buffer inside the timed region. The very large ratios (up to 2421x and 3674x) come only from the 32-bit libTIFF 3.8.2 hard-disk run; with libTIFF 4.6.0 the per-frame time stays flat as frames accumulate, so against current libTIFF the gain is 1.5-5x. The 1,000,000-frame SSD row writes about 8.2 GB of 64x64 16-bit pixels, past the 4 GB classic-TIFF limit of both writers (TinyTIFF has no BigTIFF support), and I found no file-size check in src/tinytiffwriter.c, so that row does not compare valid files. On the hard disk TinyTIFF was slower than libTIFF 3.8.2 for 1024x1024 to 4096x4096 frames, which the README describes as 'in the same range'. No read-speed comparison against libTIFF is published, although the README calls the reader very fast compared to libtiff. TinyTIFF handles only uncompressed, stripped, non-BigTIFF files whose frames share one size and type.

Basic TIFF only: uncompressed pixel data, limited tag set and pixel formats; the writer pre-reserves a fixed header block per frame. LGPL-3.0 licence.

## Maintenance

Stale: the last commit was on 2024-05-22 (release 4.0.1.0 followed on 2024-05-23), and issues #23, #32 and #35 have no maintainer reply. It is small and dependency-free, but LGPL-3.0, so link it as a library or accept the LGPL terms if you vendor it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Benchmark code is public (tests/tinytiffwriter_speedtest/tinytiffwriter_speedtest.cpp with tests/common_tinytiff_test_lib/libtiff_tools.cpp) and the raw numbers are in doc/images/performance_measure.ods and performance_measure_ssd.ods, with CPUs named in the README (Ryzen 5 3600, Ryzen 7 5800H), but no compiler or flags beyond 'Release-build'; author-run, so C.
- **Verifier notes:** Numbers come from the two .ods result sheets behind the README charts; the record's 1.5-3x and 1.5-5x match the SSD sheet. Flagged the over-4 GB 1,000,000-frame row and TinyTIFF being slower for large frames on the hard-disk run. LGPL-3.0, 163 stars, 48 forks, last commit 2024-05-22 (stale) confirmed on github.com.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jkriege2/TinyTIFF>
  - <https://github.com/jkriege2/TinyTIFF/commits>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/HEAD/README.md>
  - <https://github.com/jkriege2/TinyTIFF/tree/master/tests>
  - <https://github.com/jkriege2/TinyTIFF/tree/master/tests/common_tinytiff_test_lib>
  - <https://github.com/jkriege2/TinyTIFF/tree/master/doc>
  - <https://github.com/jkriege2/TinyTIFF/tree/master/doc/images>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/tinytiffwriter_speedtest/tinytiffwriter_speedtest.cpp>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/tinytiffwriter_speedtest/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/common_tinytiff_test_lib/libtiff_tools.h>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/common_tinytiff_test_lib/libtiff_tools.cpp>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/common_tinytiff_test_lib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/src/tinytiffwriter.c>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/doc/images/performance_measure.ods>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/doc/images/performance_measure_ssd.ods>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/jkriege2/TinyTIFF/issues?q=is%3Aissue>
  - <https://github.com/jkriege2/TinyTIFF/issues/23>
  - <https://github.com/jkriege2/TinyTIFF/issues/32>
  - <https://github.com/jkriege2/TinyTIFF/issues/35>
  - <https://github.com/jkriege2/TinyTIFF/releases>
  - <https://github.com/jkriege2/TinyTIFF/commits/master/src/tinytiff_ctools_internal.h>
  - <https://github.com/jkriege2/TinyTIFF/commits/master/doc/images/performance_measure_ssd.ods>
  - <https://github.com/jkriege2/TinyTIFF/commit/54e8391>
  - <https://github.com/jkriege2/TinyTIFF/commit/54e8391.diff>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/README.md>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/src/tinytiffwriter.c>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/src/tinytiffwriter.h>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/src/tinytiffreader.c>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/src/tinytiffreader.h>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/src/tinytiff_tools.hxx>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/src/tinytiff_ctools_internal.h>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/src/tinytiff_ctools_internal.c>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/src/tinytiff_defs.h>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/tinytiffwriter_speedtest/tinytiffwriter_speedtest.cpp>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/tinytiffwriter_speedtest/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/common_tinytiff_test_lib/libtiff_tools.cpp>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/common_tinytiff_test_lib/libtiff_tools.h>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/common_tinytiff_test_lib/test_results.h>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/common_tinytiff_test_lib/test_results.cpp>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/common_tinytiff_test_lib/testimage_tools.h>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/common_tinytiff_test_lib/tinytiffhighrestimer.h>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/tests/common_tinytiff_test_lib/tinytiffhighrestimer.cpp>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/doc/images/performance_measure.ods>
  - <https://raw.githubusercontent.com/jkriege2/TinyTIFF/master/doc/images/performance_measure_ssd.ods>
  - <https://gitlab.com/libtiff/libtiff/-/raw/v4.6.0/libtiff/tif_write.c>
  - <https://gitlab.com/libtiff/libtiff/-/raw/v4.6.0/libtiff/tif_dirwrite.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/jkriege2/tinytiff`) · [data/wave10/enrich/raw/github_com_jkriege2_tinytiff.json](../../../data/wave10/enrich/raw/github_com_jkriege2_tinytiff.json) (enrichment confidence 0.8)

</details>
