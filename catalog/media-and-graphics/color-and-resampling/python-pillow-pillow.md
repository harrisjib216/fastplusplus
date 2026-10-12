# Pillow

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python with C core` · `MIT-CMU` · 🟢 active

> Python's standard imaging library (C core): 3-4x faster resizing and 10-30x faster grayscale/3D-LUT than single-threaded ImageMagick 6.9.

| | |
|---|---|
| **Beats** | ImageMagick 6.9.7-4 (via Wand) |
| **Claimed result** | Core i5-4430, docs/src/data/i5-4430.json (derived from page data): Lanczos 2560x1600 to 320x200 40.46 ms for Pillow 7.0.0 vs 134.41 ms for ImageMagick 6.9.7-4 (3.3x); bilinear 15.83 vs 47.76 ms (3.0x); Lanczos upscale to 5478x3424 374.84 vs 1495.61 ms (4.0x); RGB to L conversion 5.25 vs 51.45 ms (9.8x); 3D LUT with a 4^3 table 111.19 vs 3353.63 ms (30x); blur radius 1 px 185.67 vs 675.34 ms (3.6x), 10 px 187.53 vs 1768.07 ms (9.4x), 30 px 186.41 vs 4090.08 ms (21.9x); JPEG load 21.39 vs 27.38 ms (1.3x). Same direction on the other three machines in docs/src/data (c5.large Xeon 8124M, m5a.large EPYC 7571, macbook.2019 Core i5-8279U): Lanczos to 320x200 2.2x to 3.1x, RGB to L 7.8x to 13.1x, 4^3 LUT 26x to 30x (derived from page data). |
| **Workload** | pillow-perf test suite: a 2560x1600 RGB image resized to 26x16, 320x200, 2048x1280 and 5478x3424 with Bilinear, Bicubic and Lanczos, RGB to L conversion, 3D colour LUT, Gaussian blur and JPEG load/save; Pillow 7.0.0 against ImageMagick 6.9.7-4 through Wand, both single-threaded (MAGICK_THREAD_LIMIT=1), median of 5 to 11 runs. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-4430 @ 3.00GHz, Ubuntu 18.04.3 (same trends on Xeon 8124M, EPYC 7571, Core i5-8279U) |
| **Compiler and flags** | Not fully stated: auto/run.sh builds Pillow 7.0.0 from source with python setup.py develop and empty CFLAGS (distutils defaults; the Pillow-SIMD builds add -msse4 or -mavx2); compiler and version not recorded. ImageMagick comes from Ubuntu's libmagickwand-dev package (auto/install_ubuntu.sh) through Wand, limited to one thread by MAGICK_THREAD_LIMIT=1 in testsuite/cases/wand.py. |
| **Adoption** | 13.9k stars; the standard Python imaging library |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/python-pillow/Pillow) · [benchmark](https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/i5-4430.json) |

## Verdict

In pillow-perf on an Intel Core i5-4430 under Ubuntu 18.04.3, Pillow 7.0.0 was built from source with default CFLAGS and no -march (the compiler is not recorded); run.sh checks out the upstream 7.0.0 tag, whose README is plain Pillow, from a pillow-simd clone. It was compared with ImageMagick 6.9.7-4 through Wand with MAGICK_THREAD_LIMIT=1 on a 2560x1600 RGB image, taking the median of 5 runs (3 for ImageMagick blur and LUT, 11 for convert and load). Results: Lanczos to 320x200 40.5 vs 134.4 ms (3.3x); Lanczos upscale to 5478x3424 374.8 vs 1495.6 ms (4.0x); RGB to L 5.3 vs 51.5 ms (9.8x); 4^3 3D LUT 111 vs 3354 ms (30x); JPEG load 21.4 vs 27.4 ms (1.3x). All ratios are derived from page data. The resize and LUT rows are like for like; the blur and grayscale rows are not.

## Use it when

- Python services that thumbnail or resize 8-bit RGB/RGBA images and currently call ImageMagick through Wand or a subprocess: Lanczos and bilinear downscales ran about 3x faster, and 2.14x upscales about 4x faster, with the same filter families.
- Large-radius blurs: Pillow's GaussianBlur took 186-188 ms on a 4-megapixel frame at radius 1, 10 and 30, while ImageMagick grew from 0.68 s to 4.1 s; accept that it is a box approximation.
- Colour grading with 3D LUTs (Color3DLUT, 4^3 to 36^3 tables): about 111 ms per 2560x1600 frame against 3.1-3.4 s for ImageMagick's HaldClut on an i5-4430.
- You want broad format I/O plus basic processing in one permissively licensed (MIT-CMU) dependency, with wheels for Linux, macOS and Windows; JPEG save also ran 2.2x faster than ImageMagick (21.8 vs 48.0 ms).

## Skip it when

- C or C++ code: there is no public C API, so embedding CPython is the only route; use libvips, OpenCV or a dedicated resizer instead.
- Maximum single-core resize speed: in the same data files, Pillow-SIMD 7.0 AVX2 is about 4-7x faster at resizing with the same API, and single-threaded OpenCV 4.1.2 upscaled to 5478x3424 3.9x faster bilinear (57.7 vs 222.9 ms) and 2.6x faster bicubic (115.3 vs 298.3 ms).
- Small blur radii or an exact Gaussian: OpenCV blurred at radius 1 in 69 ms against Pillow's 186 ms, and Pillow's result is a three-box approximation, not a true Gaussian kernel.
- Using all cores on one large image: each kernel runs on one thread, so parallelism means tiling or processing different images on different threads; libvips threads automatically.
- Parsing untrusted images in a privileged process without staying current: 12.3.0 alone fixed about a dozen CVEs (out-of-bounds writes in Image.paste() and RankFilter, PDF and font decompression bombs, a McIdas out-of-bounds read).

## How it is fast

Resampling is a separable two-pass convolution. The filter coefficients are precomputed once per output column and row, with support widened by the downscale factor so the result is properly antialiased. 8-bit images are accumulated in 32-bit fixed point (22 fractional bits) and clipped through a lookup table, and the horizontal pass only processes the source rows the vertical pass will read. GaussianBlur is three passes of an extended box filter (Gwosdek et al., SSVM 2011) using running sums, with a transpose for the vertical pass, so its cost does not depend on the radius. Color3DLUT does trilinear interpolation in 16-bit fixed point, and RGB-to-L is a single fixed-point multiply-add per channel (ITU-R 601-2 weights). None of these kernels uses SIMD intrinsics (that is the Pillow-SIMD fork); each releases the GIL while it runs.

## Compared with alternatives

Pick plain Pillow over Pillow-SIMD when you need the official wheels on every platform (ARM, ppc64le, s390x, PyPy) and prompt security releases, and accept giving up roughly 4-7x of resize speed. Pick it over OpenCV when you need correctly antialiased convolution downscaling, large-radius blurs or 3D LUTs together with broad format I/O from Python. For multi-threaded or out-of-core pipelines, libvips is the better choice.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | CPython; zlib and libjpeg are required for source builds by default (they can be disabled), and libtiff, libwebp, FreeType, LittleCMS, OpenJPEG, libavif and libraqm are optional; binary wheels bundle them |
| **Minimum toolchain** | Python 3.11+ on main (13.0.0 drops 3.10; 12.0.0 dropped 3.9); a C compiler only for source builds |
| **Platforms** | CI on Linux x86-64 (Alpine, Amazon Linux, Arch, CentOS Stream, Debian, Fedora, Gentoo, Ubuntu), Ubuntu 26.04 arm64v8/ppc64le/s390x, macOS arm64 and x86-64, Windows x86 and x86-64, and PyPy3 |
| **Thread safety** | The C kernels release the GIL (ImagingSectionEnter calls PyEval_SaveThread), so different images can be processed on parallel threads. The 12.3.0 notes dropped the Python 3.13 free-threaded wheels now that 3.14 officially supports free threading. Sharing one Image object across threads is not documented as safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- GaussianBlur(radius) treats radius as the standard deviation and computes three extended box passes, so its output differs from ImageMagick's -blur/-gaussian-blur; pillow-perf's 3.6-21.9x blur ratios compare these two different algorithms.
- convert('L') applies ITU-R 601-2 luma weights (fixed point 19595/38470/7471) to gamma-encoded values, so it will not match ImageMagick's grayscale type conversion.
- Image.thumbnail() defaults to reducing_gap=2.0 (a fast integer box reduce, plus JPEG draft decoding, before the final filter), while Image.resize() defaults to reducing_gap=None, so the two calls trade speed and accuracy differently.
- Decompression-bomb guard: Image.MAX_IMAGE_PIXELS (89,478,485 pixels) raises a warning above the limit and DecompressionBombError above twice the limit; very large legitimate images need the limit raised.

## Known shortcomings

- Python library with a C core (language-filter mismatch). First-party pillow-perf run (i5-4430.json: Pillow 7.0.0 vs ImageMagick 6.9.7-4 through Wand, both single-thread; harness public, compiler unrecorded). Resize and LUT are equivalent work; the blur row is not (box approximation vs true Gaussian).
- Numbers are stale: the pillow-perf run used upstream Pillow 7.0.0 (run.sh checks out the 7.0.0 tag inside the pillow-simd clone) and the 12.3.0 release notes claim up to 5.6x on resample and filter since; the blur and greyscale rows are not like-for-like, and in the same file OpenCV 4.1.2 upscales 3.9x (bilinear) and 2.6x (bicubic) faster than Pillow and blurs 1 px in 69 ms against 186 ms. Pillow's kernels have no SIMD. 12.3.0 fixed about a dozen 2026 CVEs.

## Caveats and trade-offs

The benchmark repository belongs to the python-pillow organisation and was written by the Pillow-SIMD authors (first-party, hence tier C); the compiler is not recorded. The ImageMagick baseline is the old 6.9.7-4 (Ubuntu 18.04 package, version given in docs/src/data/index.js), forced to one thread, and every Wand case clones the source image inside the timed region. Not all operations do the same work: Pillow's Gaussian blur is a three-pass extended-box approximation whose cost does not depend on the radius, while ImageMagick runs a true Gaussian (MagickBlurImage with radius 2.5r and sigma r), so the 3.6x to 21.9x blur ratios compare different algorithms; ImageMagick's grayscale conversion (setting the image type) need not match Pillow's L formula. Resizing (Lanczos/lanczos, Bilinear/triangle) and the 3D LUT (Color3DLUT against a Hald CLUT of the same 4^3, 16^3 and 36^3 sizes) are equivalent operations. Pillow-SIMD 7.0 AVX2 is about 4 to 7 times faster than plain Pillow at resizing in the same files (derived from page data). The libvips Speed-and-memory-use table includes only Pillow-SIMD, not plain Pillow.

Python-only API (not callable from C++ without embedding CPython); single-threaded; Lanczos resize is convolution-based with proper anti-aliasing.

## Maintenance

Very active (quarterly releases on Jan 2, Apr 1, Jul 1 and Oct 15; 12.3.0 is current and 13.0.0 is on main) and MIT-CMU licensed. The catalogued numbers are from the old 7.0.0, and the 12.3.0 release notes claim up to 5.6x speedups for resample, filter, matrix and other operations, so current Pillow is probably at least as fast (not re-measured).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The pillow-perf harness is public (testsuite/run.py, testsuite/cases/pillow_scale.py, wand_scale.py, pillow_blur.py, wand_blur.py, pillow_lut.py, wand_lut.py, auto/run.sh) and the data file names the CPU (Intel Core i5-4430, Ubuntu 18.04.3), but no compiler or compiler version is recorded and Pillow 7.0.0 is built with empty CFLAGS (distutils defaults), so it falls short of A; the benchmark belongs to the python-pillow organisation and was run by the Pillow-SIMD authors, so it is first-party (C).
- **Verifier notes:** All numbers match the pillow-perf i5-4430.json rows for pillow-7.0 and imagemagick-6.9; the 6.9.7-4 version label is in docs/src/data/index.js. Language cannot be changed through verifier corrections: please set the language override to 'Python with C core' in decisions.json. Licence is MIT-CMU (pyproject.toml), a permissive HPND-style licence, so copyable stands.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/i5-4430.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/index.js>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/macbook.2019.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/c5.large.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/m5a.large.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/index.html>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/index.js>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/README.md>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/run.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/requirements.txt>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/__init__.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/base.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_blur.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_blur.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_lut.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_lut.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_convert.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_convert.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_load.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_load.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/auto/run.sh>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/auto/install_ubuntu.sh>
  - <https://github.com/python-pillow/pillow-perf>
  - <https://github.com/python-pillow/pillow-perf/tree/master/docs/src>
  - <https://github.com/python-pillow/Pillow>
  - <https://github.com/python-pillow/Pillow/commits>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/pyproject.toml>
- **Sources the enricher read:**
  - <https://github.com/python-pillow/Pillow>
  - <https://github.com/python-pillow/Pillow/security>
  - <https://github.com/python-pillow/Pillow/releases>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/README.md>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/src/libImaging/Resample.c>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/src/libImaging/Reduce.c>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/src/libImaging/BoxBlur.c>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/src/libImaging/ColorLUT.c>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/src/libImaging/Convert.c>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/src/libImaging/Imaging.h>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/src/libImaging/ImPlatform.h>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/src/_imaging.c>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/src/PIL/Image.py>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/src/PIL/ImageFilter.py>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/docs/installation/platform-support.rst>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/docs/installation/building-from-source.rst>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/docs/releasenotes/index.rst>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/docs/releasenotes/12.3.0.rst>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/HEAD/docs/releasenotes/13.0.0.rst>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/README.md>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/auto/run.sh>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/auto/install_ubuntu.sh>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/run.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/__init__.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/base.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/cv2.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/cv2_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_blur.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_blur.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_lut.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_lut.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_convert.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_convert.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_load.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_load.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/i5-4430.json>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/index.js>
  - <https://github.com/uploadcare/pillow-simd/tree/7.0.0>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/python-pillow/pillow`) · [data/wave10/enrich/raw/github_com_python_pillow_pillow.json](../../../data/wave10/enrich/raw/github_com_python_pillow_pillow.json) (enrichment confidence 0.8)

</details>
