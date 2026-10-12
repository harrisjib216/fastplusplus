# libvips

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1-or-later` · 🟢 active

> Demand-driven, horizontally threaded C image library; author's crop/resize/sharpen TIFF test: 7.8x faster than ImageMagick 7 convert, 16x less memory.

| | |
|---|---|
| **Beats** | ImageMagick 7.1.1 (convert/magick) |
| **Claimed result** | Speed-and-memory-use wiki table (Threadripper PRO 3955WX, Ubuntu 25.04, run 12 Aug 2025): vips-c 8.18 0.57 s, 94.28 MB peak vs ImageMagick convert 7.1.1 4.44 s, 1499.29 MB ('times slower' column 7.79; magick 7.1.1 4.41 s, 7.74). About 16x less peak memory (derived from page data). Single-threaded 1thr-vips-c 0.77 s is about 5.8x faster than convert (derived from page data). Other rows on the same page: GraphicsMagick gm 1.4 2.05 s, pillow-simd 9.5.0 1.51 s, OpenCV 4.10 3.15 s. |
| **Workload** | Load a 10,000 x 10,000 8-bit RGB tiled TIFF, crop 100 px off every edge, shrink by 10% with bilinear interpolation, sharpen with a 3x3 convolution, save again; quickest real time of five runs, peak RSS sampled with ps. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3955WX 16-core, Ubuntu 25.04, run 12 Aug 2025 |
| **Compiler and flags** | Not stated for the libraries: tools were used 'as packaged for Ubuntu' (Ubuntu 25.04 distribution binaries of libvips 8.18 and ImageMagick 7.1.1). The vips.c driver's comment gives only 'gcc -Wall vips.c `pkg-config vips --cflags --libs` -o vips-c'. |
| **Adoption** | 11.7k stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/libvips/libvips) · [benchmark](https://github.com/libvips/libvips/wiki/Speed-and-memory-use) |

## Verdict

The libvips author's vips-bench test (load a 10,000 x 10,000 8-bit RGB tiled TIFF, crop 100 px per edge, 90% bilinear shrink, 3x3 sharpen, save; quickest real time of five warm-cache runs; RSS sampled with ps) on a 16-core Threadripper PRO 3955WX under Ubuntu 25.04 reports the vips.c program at 0.57 s and 94 MB peak against ImageMagick 7.1.1 convert at 4.44 s and 1499 MB (magick 4.41 s), with both given 16 threads. The ImageMagick side is the Ubuntu package at its default 16-bit quantum; the libvips side was an unreleased 8.18 development build of unknown compiler and flags, and outputs were not compared.

## Use it when

- Server-side batch or request-time processing of large images (thumbnails, resize, crop, sharpen, colour conversion) where peak memory per job matters, for example many concurrent jobs per box.
- Very large inputs (gigapixel TIFF, OpenSlide whole-slide images, image pyramids via dzsave) that do not fit comfortably in RAM.
- Multi-core machines where you want a whole load-process-save pipeline parallelised without writing threading code; the single-threaded row (VIPS_CONCURRENCY=1) was still 0.77 s against 4.44 s for 16-thread convert.
- Applications already on Node (sharp), Ruby on Rails (ActiveStorage), Python (pyvips) or Go that want a mature native engine through an existing binding.

## Skip it when

- You need a single fast in-memory resize kernel with no I/O: specialised resizers in this catalog beat libvips on that narrower task (see siblings).
- Scripts that depend on ImageMagick's command-line syntax, its format coverage or its specific filter behaviour: the vips CLI is a different language, and the vips CLI writes intermediate files to disc (the wiki warns of heavy disc traffic; vips-cli row 1.25 s vs 0.57 s for the C program).
- Random-access operations on formats with only sequential decoders (JPEG, PNG) at large sizes: libvips must decompress them fully to memory or a temporary file first, which costs time and space.
- Projects that cannot meet LGPL-2.1 linking obligations, or that must avoid the large attack surface of optional loaders such as ImageMagick or PDF libraries when handling untrusted files (the README itself warns about this).

## How it is fast

Pixels stream through the pipeline as small overlapping regions instead of whole images, so memory stays near the working set (94 MB peak for a 300 MB image in the table). Threading lives in the image I/O system: each worker gets its own light copy of the whole pipeline (horizontal threading, almost lock-free), and a separate write-behind thread overlaps output with compute. Hot kernels have Google Highway SIMD paths with runtime dispatch, chosen when Highway is present at build time: vips_reduce precomputes 16-bit fixed-point filter tables per sub-pixel position and uses a vector path for 3- and 4-band uchar images, and the integer convolution turns the mask into 8-bit mantissas with a shared exponent for a uchar vector path. Orc run-time code generation is the fallback when Highway is absent.

## Compared with alternatives

Pick libvips for complete load-process-save pipelines on large images where memory and core usage matter: in the same table it beats Pillow-SIMD (1.51 s), GraphicsMagick (2.05 s), FFmpeg (2.06 s), OpenCV (3.15 s) and OpenImageIO (3.46 s). Pick fast_image_resize (which beats libvips 8.15.1 single-threaded on pure RGB8 resize kernels, e.g. Lanczos3 13.52 vs 17.31 ms) or Pillow-SIMD when you only need an in-memory resize inside Rust or Python.

## Integration

| | |
|---|---|
| **Form** | shared lib (static possible with meson --default-library static); also distro packages and Windows binaries |
| **Dependencies** | Required: glib-2.0 (&gt;= 2.52) and expat. Optional, picked up by pkg-config: libjpeg(-turbo/mozjpeg), libtiff, libpng or spng, libwebp, libheif, libjxl, OpenJPEG, lcms2, fftw3, cgif, libimagequant, pangocairo, librsvg, poppler or PDFium, OpenSlide, OpenEXR, cfitsio, matio, libraw, ImageMagick/GraphicsMagick, and Highway (preferred) or Orc for SIMD. |
| **Minimum toolchain** | Meson (README says 0.56+, meson.build declares &gt;= 0.55); C++14 required since 8.18.0, C sources built as gnu11, and the 8.19 ChangeLog formally raises the toolchain requirement to C11. Default meson buildtype is release. |
| **Platforms** | Linux, macOS, other Unix-likes and Windows. SIMD through Highway runtime dispatch (x86-64 and ARM targets; big-endian Highway paths fixed in 8.18.1), else Orc, else plain C. |
| **Thread safety** | Documented as threaded and thread-safe: call VIPS_INIT once single-threaded, then images (immutable) can be created and read from any thread. Exceptions: draw operations mutate their image, VipsRegion is per-thread, and the error buffer is a single global shared by all threads. Worker count defaults to the number of CPU cores (vips_concurrency_set or VIPS_CONCURRENCY). |
| **Drop-in for the baseline** | no |

## Gotchas

- Access mode matters: vips_image_new_from_file defaults to random access, which for JPEG/PNG-style formats means full decompression to memory (under about 100 MB) or to a temporary disc file. Pass access=VIPS_ACCESS_SEQUENTIAL for top-to-bottom pipelines. The benchmark uses uncompressed tiled TIFF, which libtiff can read randomly, the best case for libvips (jpg-vips-c: 0.82 s and 286 MB vs 0.57 s and 94 MB for tiled TIFF).
- Integer convolution on uchar images takes a vector path that rounds the mask to 8-bit mantissas with a shared exponent and only falls back to the exact C path if the mask's DC response is off by more than 2 levels. The benchmark mask (-1 x8, 16, scale 8) is exactly representable, but other masks can give slightly different results from the C path.
- Avoid 8.18.1: issue #4955 reports white artifacts from an underflow in integer convolution with a sharpening mask (introduced in 8.18.1, fixed in 8.18.2, 'convolution: avoid using unsigned accumulators').
- Error handling is a single -1/NULL return plus a process-global error buffer, so under concurrency the message in the buffer may not belong to the failure you just saw.

## Known shortcomings

- Numbers are the libvips wiki table (vips-c 0.57 s and 94.28 MB vs ImageMagick convert 4.44 s and 1499.29 MB) measured with distro packages and no compiler flags; memory and single-thread ratios are derived from page data. Outputs differ: libvips integer convolution vs ImageMagick Q16.
- Provenance flaw in the wiki table: the rows say libvips 8.18 and sat in the 15 Aug 2025 revision 112504a, but 8.18.0 was released 17 Dec 2025, so libvips was an unreleased git build (flags and Highway state unknown) rather than the Ubuntu package used for the others. im.sh and im7.sh run vipsheader twice inside the timed ImageMagick script; only real time is measured (vips-bench issue #7 open since 2017); exit status and output are never checked; the pipeline is 8-bit integer against ImageMagick's 16-bit quantum. 8.18.1 had an integer-convolution underflow (#4955), fixed in 8.18.2.
- Re-found by the wave 1 seed backfill (w1-mine-w) with the same first-party wiki numbers (ImageMagick 7.1.1 4.44 s / 1499 MB vs vips-c 0.57 s / 94 MB, 7.79x; distro package flags unstated); the Electronic Imaging 2025 paper host is blocked, so a retier to B waits on paper access (lead in data/wave10/leads.md).

## Caveats and trade-offs

Benchmark is first-party (the libvips author's wiki and libvips/vips-bench repo; code public, distro packages, no compiler flags). The page itself says the test 'does a lot of file IO and relatively little processing, which flatters libvips' and that tools which do not thread automatically (Pillow, OpenCV) rank lower than they should on the 16-core machine. Workload is mostly tiled-TIFF I/O plus a bilinear shrink and 3x3 sharpen, so it measures a pipeline rather than a pure resampling kernel. The pipelines are not bit-identical: vips.c runs the 8-bit image through vips_reduce (linear kernel) and an integer-precision convolution, while im.sh/im7.sh use ImageMagick's '-filter triangle -resize 90x90%' and '-convolve' at ImageMagick's default 16-bit quantum depth; outputs are not compared. Times are the quickest real time of five runs with a warm disc cache. The single-thread row (1thr-vips-c 0.77 s) is still about 5.8x faster than convert (derived from page data).

Demand-driven streaming pipeline with a C API (also a C++ binding vips8 in the repo); LGPL linking rules apply. Multi-threaded by default. Not a drop-in for ImageMagick command lines.

## Maintenance

Very active (last commit 2026-10-02, 8.18.7 released 20 Sep 2026, 8.19 in development, OSS-Fuzz coverage and a steady stream of hardening fixes); LGPL-2.1-or-later, so link dynamically or meet the relinking terms if you ship it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party wiki table (libvips author) with public driver and per-tool scripts in libvips/vips-bench (vips.c, im.sh, im7.sh, benchmark.sh) and a stated CPU (Threadripper PRO 3955WX), but the measured libraries are Ubuntu 25.04 distribution packages with no compiler version or flags stated; the only compile line is the driver's 'gcc -Wall vips.c `pkg-config vips --cflags --libs`'. Public code plus CPU but missing compiler/flags is C, not A.
- **Verifier notes:** Every number in the record is on the wiki page in the vips-c and convert rows; I only labelled the memory and single-thread ratios as derived and made the compiler field precise. Metadata confirmed on github.com: LGPL-2.1-or-later, 11.7k stars, not archived or forked, last commit 2026-10-02 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** backfill w1-mine-w
- **Pages the verifier opened:**
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use>
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md>
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Benchmarks.md>
  - <https://github.com/libvips/vips-bench>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/README.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/vips.c>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im7.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/benchmark.sh>
  - <https://github.com/libvips/libvips>
  - <https://github.com/libvips/libvips/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Speed-and-memory-use.md>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/_history>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use/112504a3119d49c3a1d4d87669cf59f19d828c35>
  - <https://raw.githubusercontent.com/wiki/libvips/libvips/Why-is-libvips-quick.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/README.md>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/vips.c>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/im7.sh>
  - <https://raw.githubusercontent.com/libvips/vips-bench/master/benchmark.sh>
  - <https://github.com/libvips/vips-bench/commits/master/vips.c>
  - <https://github.com/libvips/vips-bench/issues?q=is%3Aissue>
  - <https://github.com/libvips/vips-bench/issues/7>
  - <https://github.com/libvips/vips-bench/issues/8>
  - <https://raw.githubusercontent.com/libvips/libvips/master/README.md>
  - <https://raw.githubusercontent.com/libvips/libvips/master/ChangeLog>
  - <https://raw.githubusercontent.com/libvips/libvips/master/meson.build>
  - <https://raw.githubusercontent.com/libvips/libvips/master/libvips/resample/reduceh.cpp>
  - <https://raw.githubusercontent.com/libvips/libvips/master/libvips/resample/reducev.cpp>
  - <https://raw.githubusercontent.com/libvips/libvips/master/libvips/resample/templates.h>
  - <https://raw.githubusercontent.com/libvips/libvips/master/libvips/convolution/convi.c>
  - <https://raw.githubusercontent.com/libvips/libvips/master/libvips/include/vips/vector.h>
  - <https://raw.githubusercontent.com/libvips/libvips/master/doc/meson.build>
  - <https://raw.githubusercontent.com/libvips/libvips/master/doc/using-threads.md>
  - <https://raw.githubusercontent.com/libvips/libvips/master/doc/how-it-opens-files.md>
  - <https://github.com/libvips/libvips/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/libvips/libvips/issues?q=is%3Aissue+performance+reduce+OR+conv+OR+threadpool+sort%3Aupdated-desc>
  - <https://github.com/libvips/libvips/issues/4955>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/libvips/libvips`) · [data/wave10/enrich/raw/github_com_libvips_libvips.json](../../../data/wave10/enrich/raw/github_com_libvips_libvips.json) (enrichment confidence 0.85)

</details>
