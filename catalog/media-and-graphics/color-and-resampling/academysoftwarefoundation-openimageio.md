# OpenImageIO

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> VFX-industry image I/O and processing library; its oiiotool ran a crop, resize and convolve job 1.3x faster than ImageMagick 7.

| | |
|---|---|
| **Beats** | ImageMagick 7.1.1 (magick, convert) |
| **Claimed result** | 3.46 s for oiio vs 4.41 s for magick and 4.44 s for convert (1.3x, derived from page data); the page's own 'times slower than libvips' column reads oiio 6.07 vs magick 7.74 and convert 7.79. |
| **Workload** | libvips vips-bench: load a 10000x10000 8-bit RGB uncompressed tiled TIFF, crop 100 pixels off every edge, resize to 90% and apply a 3x3 convolution, then save. oiiotool 2.5.18 runs '--resize:filter=triangle 90%' with a 3x3 gaussian '--convolve' (the script comment says this blurs rather than sharpens). ImageMagick 7.1.1 ('magick' via im7.sh, 'convert' via im.sh) crops on load and runs '-filter triangle -resize 90x90%' with a 3x3 sharpen '-convolve'. Both are multithreaded, and each time is the fastest real time of five runs. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3955WX 16-core, Ubuntu 25.04 (run 12 Aug 2025) |
| **Compiler and flags** | Not stated (Ubuntu packages). |
| **Adoption** | 2.4k stars; VFX industry standard (Academy Software Foundation) |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/AcademySoftwareFoundation/OpenImageIO) · [benchmark](https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md) |

## Verdict

In the libvips maintainer's vips-bench run (12 Aug 2025, Threadripper PRO 3955WX 16 cores, Ubuntu 25.04 packages, flags not stated), oiiotool 2.5.18 took 3.46 s, best wall time of five, to load a 10000x10000 8-bit tiled TIFF, crop, triangle-resize to 90%, 3x3-convolve and save, against 4.41 s for ImageMagick 7.1.1 magick and 4.44 s for convert, about 1.3x (derived from page data). The oiio script's broken crop made it process a mostly black 10000x10000 frame (about 4% more output pixels than ImageMagick) with a gaussian instead of a sharpen kernel, so the work is comparable but the output is not the intended image.

## Use it when

- Pipelines built around OpenEXR (multi-part, deep), DPX/Cineon, tiled or MIP-mapped TIFF and OCIO colour management, where you need one C++/Python API across formats more than peak resize speed.
- Batch jobs that shell out to ImageMagick convert/magick for crop, resize and convolution of large images on a many-core box: oiiotool 2.5.18 was 1.27x to 1.28x faster in the libvips table.
- Applications that must read huge texture or plate sets with bounded memory: ImageCache keeps a capped working set and is documented as fully thread-safe.
- Renderers and texture tools needing filtered MIP-map lookups (TextureSystem, maketx / oiiotool -otex).

## Skip it when

- Throughput-first thumbnailing or web resizing: in the same libvips table libvips (0.57 s), GraphicsMagick (2.05 s), FFmpeg (2.06 s) and OpenCV (3.15 s) all beat oiio (3.46 s).
- Memory-constrained hosts: oiiotool promotes 8-bit input to float unless --native is given, and peaked at 2236.57 MB against 1500.52 MB for magick and 94.28 MB for libvips.
- Strong downscales with IBA::resize: the 2D gather reads (2\*ceil(r/scale)+1)^2 source pixels per output pixel, so a 10% shrink costs 441 taps with the triangle filter and 3721 with the default lanczos3, against 42 and 122 for a two-pass separable resampler; use a dedicated resizer there (IBA::resample is cheap but does not filter, so it aliases).
- Untrusted input on old or distro builds: SECURITY.md says 2.5.x and earlier get no patches, and the 3.2 changelog lists dozens of reader hardening fixes including CVE-2026-59181 (Cineon), CVE-2026-59156 (FITS), CVE-2026-63422 (OpenEXR out-of-bounds write) and CVE-2026-63420 (PSD).
- Projects that want a small dependency: the required set alone is Imath, OpenEXR, libTIFF, OpenColorIO, libjpeg, zlib, fmt and robin-map, plus CMake 3.23.

## How it is fast

The measured path has no special algorithm. Every ImageBufAlgo call is split by parallel_image across all cores by default, and oiiotool converts 8-bit input to float once at read time. In 2.5.18, and unchanged on main, IBA::resize evaluates the triangle filter as a direct 2D gather of xtaps x ytaps source pixels per output pixel (5x5 at 90%), with separable tap weights precomputed per column and per row, and IBA::convolve is a plain 3x3 gather; both are scalar loops over ImageBuf iterators. Google Highway SIMD exists in 3.2 only for resample (nearest/bilinear) and some per-pixel arithmetic, so the margin over ImageMagick comes from whole-pipeline threading and lower per-operation overhead (inferred from the code, not profiled), not from a faster resampler.

## Compared with alternatives

Pick OpenImageIO over libvips, GraphicsMagick or FFmpeg only when you need its VFX format coverage (deep and multi-part EXR, DPX, MIP-mapped textures), OCIO colour management or ImageCache/TextureSystem; for batch resize and convolution throughput libvips was 6x faster and used about 24x less memory in the same table, and fast_image_resize or zimg are better single-kernel resizers.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Required: Imath &gt;= 3.1, OpenEXR &gt;= 3.1, libTIFF &gt;= 4.1, OpenColorIO &gt;= 2.3, libjpeg &gt;= 9 or libjpeg-turbo &gt;= 2.1, zlib &gt;= 1.2.7, fmt &gt;= 9 and robin-map &gt;= 1.3 (the last two auto-downloaded if missing). Optional per format or feature: libpng, LibRaw, FFmpeg, OpenJPEG, OpenJPH, libheif, libwebp, libjxl, giflib, DCMTK, OpenVDB, Ptex, Freetype, libultrahdr, TBB, OpenCV, Qt (iv viewer), Python with nanobind or pybind11, Google Highway (OIIO_USE_HWY). |
| **Minimum toolchain** | C++17 (also C++20/23/26); gcc 9.3-16, clang 10-22, MSVC 2017-2026 (v19.14+), Intel oneAPI 2022+; CMake &gt;= 3.23 for the 3.2 line |
| **Platforms** | Linux, macOS, Windows; x86-64 builds default to an SSE4.2 baseline in 3.2 (x86-64-v2 on main), with NEON paths on aarch64 |
| **Thread safety** | ImageCache is documented as completely thread-safe; ImageBufAlgo functions parallelise internally over nthreads (default: all cores; pass 1 if the caller is already multithreaded). 3.2 fixed an ImageBuf data race that could corrupt multithreaded reads (#5325). |
| **Drop-in for the baseline** | no |

## Gotchas

- The libvips oiio.sh bug survives on current main: the script passes '--crop 9800+100+100' (undefined \$widthx), and scan_offset on main still parses the leading '9800+100' as an offset and ignores the rest, so a re-run on OIIO 3.2 again processes a mostly black 10000x10000 frame.
- oiiotool works in float by default; use --native (or read with the native type in the C++ API) to keep 8-bit data, at your own speed and accuracy trade-off (not benchmarked).
- The docs say Highway SIMD is enabled by default, but the OIIO_USE_HWY CMake option is OFF ('experimental'), so check how your build was configured before expecting those speedups; the filtered resize and convolve paths have no Highway code either way.
- IBA::resize takes filter options through KWArgs (filtername, filterwidth); with no name it picks lanczos3 when shrinking and blackman-harris when enlarging, and widens the filter by the enlargement ratio, so pin the filter for reproducible output and cost.

## Known shortcomings

- Tier B on the libvips maintainers' wiki run (12 August 2025, Threadripper PRO 3955WX, Ubuntu 25.04 packages, no flags): oiio 2.5.18 3.46 s vs ImageMagick magick 4.41 s and convert 4.44 s (1.27-1.28x derived), both triangle-filter resizes. Harness bug: oiio.sh's crop geometry uses an undefined \$widthx (since 2014), so oiiotool treats it as an offset and processes a mostly black 10000x10000 frame, about 4% more pixels with wrong output; the timing is comparable but the output is not.

## Caveats and trade-offs

The 1.3x margin is modest, and the test is trivial and I/O-dominated (the wiki says it flatters libvips). The wiki notes that oiiotool 'may not be the best way to test the library'. The run is by the libvips maintainer, a third party for OpenImageIO and ImageMagick. Both oiio and ImageMagick use triangle-filter convolution resizing, so the work is comparable, unlike libvips' affine bilinear (vips-bench issue 8, opened by the Pillow-SIMD author). oiio.sh has an unfixed bug, unchanged since 2014: it passes '--crop \$widthx\$height+100+100', and because widthx is an undefined shell variable this expands to '9800+100+100'. oiiotool 2.5.18's adjust_geometry parses that string as an origin offset (+9800+100) and keeps the 10000x10000 size, so oiio resizes and convolves a mostly black 10000x10000 frame instead of the 9800x9800 crop. That is about 4% more pixels, so the time is not flattered by doing less work, but the output is not the intended image. oiio also uses a gaussian kernel instead of the sharpen kernel (the cost is the same). Programs are distro builds with unstated flags, and 2.5.18 predates the current OpenImageIO 3.x line.

Large dependency set; peak memory 2236.57 MB in this run, higher than ImageMagick (1500.52 MB) and libvips (94.28 MB).

## Maintenance

Very active Academy Software Foundation project (3.2.1.0 released 1 Oct 2026, commits on 3 Oct 2026, monthly patch releases) under Apache-2.0; the benchmarked 2.5 line no longer gets security fixes, so use 3.2.x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** The libvips 'Speed and memory use' wiki table (run by the libvips maintainer on 12 Aug 2025, AMD Ryzen Threadripper PRO 3955WX, Ubuntu 25.04) lists oiio 2.5.18 at 3.46 s against magick 4.41 s and convert 4.44 s, and the scripts are public in libvips/vips-bench (oiio.sh, im.sh, im7.sh, benchmark.sh). This is an independent third-party measurement, but every program came from Ubuntu packages and no compiler or flags are stated, so it is B, not A.
- **Verifier notes:** The numbers match the wiki row exactly (oiio 3.46 s, 6.07x vs magick 4.41 s, 7.74x and convert 4.44 s, 7.79x). The ratio is 1.27x to 1.28x (derived from page data). I read the oiiotool v2.5.18.0 geometry parser to confirm the crop-bug behaviour; the bug adds work rather than removing it, so it is recorded as a caveat. fawick/speedtest-resize (opened) has no OpenImageIO or Skia rows; it compares Go resizers with ImageMagick and GraphicsMagick.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/README.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/oiio.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im7.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/benchmark.sh>
  - <https://github.com/libvips/vips-bench/commits/master/oiio.sh>
  - <https://github.com/libvips/vips-bench/issues/8>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/v2.5.18.0/src/oiiotool/oiiotool.cpp>
  - <https://github.com/AcademySoftwareFoundation/OpenImageIO>
  - <https://github.com/AcademySoftwareFoundation/OpenImageIO/commits/main>
  - <https://raw.githubusercontent.com/fawick/speedtest-resize/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/AcademySoftwareFoundation/OpenImageIO>
  - <https://github.com/AcademySoftwareFoundation/OpenImageIO/commits/main>
  - <https://github.com/AcademySoftwareFoundation/OpenImageIO/issues?q=is%3Aissue+resize+slow>
  - <https://github.com/AcademySoftwareFoundation/OpenImageIO/tree/main/src/doc>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/README.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/INSTALL.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/SECURITY.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/CHANGES.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/v2.5.18.0/src/libOpenImageIO/imagebufalgo_xform.cpp>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/src/libOpenImageIO/imagebufalgo_xform.cpp>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/v2.5.18.0/src/libOpenImageIO/imagebufalgo.cpp>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/src/libOpenImageIO/imagebufalgo.cpp>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/v2.5.18.0/src/oiiotool/oiiotool.cpp>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/src/oiiotool/oiiotool.cpp>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/v2.5.18.0/src/doc/oiiotool.rst>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/v2.5.18.0/src/tiff.imageio/tiffoutput.cpp>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/v2.5.18.0/src/tiff.imageio/tiffinput.cpp>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/src/doc/imagebufalgo.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/src/doc/imagecache.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/src/doc/imageinput.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/src/doc/imagebuf.md>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/src/doc/oiiotool.md>
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md>
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Benchmarks.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/README.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/oiio.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im7.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/benchmark.sh>
  - <https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenImageIO/main/src/libutil/filter.cpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/academysoftwarefoundation/openimageio`) · [data/wave10/enrich/raw/github_com_academysoftwarefoundation_openimageio.json](../../../data/wave10/enrich/raw/github_com_academysoftwarefoundation_openimageio.json) (enrichment confidence 0.75)

</details>
