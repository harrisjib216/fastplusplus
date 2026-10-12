# Pillow-SIMD

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C (Python extension)` · `MIT-CMU (HPND-family; LICENSE file)` · 🟢 active

> SSE4/AVX2 fork of Python's Pillow; resizes 8-bit RGB images 11-23x faster than ImageMagick 6 via Wand, single core.

| | |
|---|---|
| **Beats** | ImageMagick 6.9 (via Wand) in the pillow-perf results; ImageMagick 7.1.1 in the libvips wiki table. pillow-perf also compares Pillow, OpenCV, Skia, libvips and Intel IPP. |
| **Claimed result** | pillow-perf c5.large.txt, 2560x1600 RGB, single core, Pillow-SIMD 7.0.0.post3 -mavx2 vs Wand (ImageMagick 6.9): to 320x200 Lanczos 0.00523 s vs 0.10633 s, about 20x; bilinear 0.00192 s vs 0.03792 s, about 20x; bicubic 0.00313 s vs 0.07111 s, about 23x; to 5478x3424 Lanczos 0.10035 s vs 1.22571 s, about 12x. Across all 12 scale cases the file gives 11.2x to 22.7x over Wand and 2.9x to 7.8x over Pillow 7.0.0 (all ratios derived from page data), so the README's 'always 16 to 40 times faster than ImageMagick' is not reproduced by this file (the upscale cases fall to 11-12x). Independent: libvips wiki table (crop, 10% bilinear shrink, 3x3 sharpen, save, 10000x10000 TIFF, Threadripper PRO 3955WX, Ubuntu 25.04): pillow-simd 9.5.0 1.51 s vs ImageMagick 7.1.1 convert 4.44 s, about 2.9x (derived from page data); libvips (vips-c 8.18) is faster still at 0.57 s. |
| **Workload** | pillow-perf scale suite: resize a 2560x1600 RGB image (synthetic color_circle.png upscaled) to 26x16, 320x200, 2048x1280 and 5478x3424 with bilinear, bicubic and Lanczos filters (ImageMagick via Wand with triangle, catrom and lanczos, MAGICK_THREAD_LIMIT=1); run.py reports the median, of 11 runs for the Pillow-SIMD builds and of 5 runs for Pillow 7.0.0 and Wand (auto/run.sh passes -n5). Independent libvips/vips-bench pipeline: load 10000x10000 TIFF, crop 100 px, shrink 10% bilinear, 3x3 sharpen, save. |
| **Metric** | throughput |
| **Hardware** | AWS EC2 c5.large (CPU model not printed in the file); libvips table: AMD Ryzen Threadripper PRO 3955WX 16-core, Ubuntu 25.04. Other pillow-perf result files cover i5-4430, AMD A10-7800, c3/c4/m5a.large and MacBooks. |
| **Compiler and flags** | pillow-perf auto/run.sh builds each Pillow-SIMD tag with CFLAGS='-msse4' or '-mavx2' via 'python setup.py develop' with the system cc (ccache cc in the bento/ubuntu-16.04 Vagrant box); the compiler and version are not printed in c5.large.txt. libvips table: Pillow-SIMD installed with pip (vips-bench README); flags not stated. |
| **Adoption** | 2.3k stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/uploadcare/pillow-simd) · [benchmark](https://github.com/python-pillow/pillow-perf/blob/master/docs/src/data/c5.large.txt) |

## Verdict

On an AWS c5.large, one core, a 2560x1600 RGB image resized with Pillow-SIMD 7.0.0.post3 built with -mavx2 took 0.00523 s to 320x200 (Lanczos) versus 0.10633 s for ImageMagick 6.9 through Wand with MAGICK_THREAD_LIMIT=1 (about 20x), and 11-23x across all 12 size and filter cases; compiler, exact CPU and Python overhead in the Wand path are not controlled, and ImageMagick works in 16-bit quantum. The independent libvips crop, 10% bilinear shrink, sharpen and save pipeline on a Threadripper PRO 3955WX timed pillow-simd 9.5.0 (installed with plain pip, so the default SSE4 build) at 1.51 s against ImageMagick 7.1.1 convert at 4.44 s (about 2.9x).

## Use it when

- Python services that already use Pillow for thumbnails or resizing of 8-bit RGB/RGBA images on x86 and can build from source.
- Downscaling large photos with bilinear, bicubic or Lanczos filters: the pillow-perf c5.large file shows 4.5-7.8x over Pillow 7.0.0 for downscales with the AVX2 build.
- Pipelines that also lean on Pillow's filter(), box/Gaussian blur, alpha_composite or mode conversion, which have SIMD paths too.
- Fleets where you control the CPU (AVX2 everywhere) and can compile per target, as Uploadcare does in production since 2015.

## Skip it when

- Anything outside Python, including C++ code: the SIMD kernels are not exposed as a standalone library.
- ARM (Apple Silicon, Graviton) or other non-x86 hosts: setup.py adds -msse4 unconditionally and the build fails there (issues #116, #143); a RISC-V Vector PR (#158) is still open.
- Grayscale (mode L), 16-bit (I;16) or float (I, F) images: in Resample.c only the 4-byte-per-pixel UINT8 path is vectorised; image8 and 16bpc paths stay scalar.
- End-to-end pipelines dominated by decode and encode: in the same c5.large file, load+resize+save is only about 4.5x faster than Wand (0.039 s vs 0.176 s), and in the libvips wiki pipeline libvips is 2.6x faster than pillow-simd (0.57 s vs 1.51 s) because it threads and streams.
- Binary-wheel deployments: PyPI carries only sdists, so every install needs a compiler and Pillow's native dependencies (zlib, libjpeg); issues #157 and #120 are zlib-not-found build failures.

## How it is fast

Resampling is Pillow's separable two-pass convolution, but coefficients are quantised to INT16 with an adaptive precision (at most 15 bits) so each tap pair can go through _mm_madd_epi16/_mm256_madd_epi16 after a pshufb that interleaves RGBA bytes into 16-bit lanes. The horizontal pass processes four output rows at once (ImagingResampleHorizontalConvolution8u4x) with 4-tap unrolling, and the vertical pass works on 8 (AVX2) or 4 (SSE4) pixels per iteration. Other kernels use the same fixed-point integer SIMD pattern.

## Compared with alternatives

Pick it over libvips or OpenCV when the code base is already PIL-based Python and you want a speedup without rewriting calls; pick libvips for whole pipelines (2.6x faster than pillow-simd and far less memory in the libvips table), fast_image_resize for Rust, and OpenCV when bilinear upscaling dominates (cv2 single-threaded 0.052 s vs Pillow-SIMD AVX2 0.076 s to 5478x3424 in the same c5.large file).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | CPython (or PyPy) &gt;=3.10 for the 12.x line; build needs setuptools&gt;=77, pybind11, a C compiler, and Pillow's native libraries (zlib and libjpeg required; libtiff, libwebp, freetype, lcms2 optional) |
| **Minimum toolchain** | C compiler accepting -msse4 (GCC or Clang); AVX2 build via CC="cc -mavx2"; MSVC x64 gets the SSE4 path through a macro in ImagingSIMD.h |
| **Platforms** | x86 and x86-64 only (SSE4.1 required; AVX2 optional at build time, no runtime dispatch) |
| **Thread safety** | Same as Pillow: resample kernels run inside ImagingSectionEnter/Leave, Pillow's GIL-release section, so different images can be processed on parallel threads; each operation itself is single-threaded |
| **Drop-in for the baseline** | partial — drop-in for Pillow of the same version (pip uninstall pillow first), not for ImageMagick, whose API and filters differ |

## Gotchas

- The instruction set is fixed at compile time: an AVX2 build (CC="cc -mavx2") on a build host will crash with an illegal instruction on a CPU without AVX2, and the default build needs SSE4.1. There is no CPU check at import.
- Output is not bit-identical to upstream Pillow: Pillow-SIMD normalises filter coefficients to INT16 with at most 15 bits of precision, while upstream Pillow uses INT32 coefficients with 22 bits (PRECISION_BITS), so some pixels can differ by rounding.
- Installing it next to Pillow is unsupported; both provide the PIL package, so a later dependency that pulls in Pillow will silently overwrite the SIMD build.
- Older pillow-simd releases lag upstream security fixes: PR #149 (ImageMath.eval environment restriction) has been open since 2024-10-08, and the libvips benchmark used 9.5.0; prefer a .post release of a current Pillow (12.1.1.post0 is on PyPI, the repo is at 12.3.0.post0).

## Known shortcomings

- Python extension in C (fork of python-pillow/Pillow, MIT-CMU). Tier B on the independent libvips vips-bench (pillow-simd 9.5.0 1.51 s vs ImageMagick 7.1.1 convert 4.44 s, Threadripper PRO 3955WX). Its own c5.large.txt shows 11-23x vs Wand, not the README's 16-40x; results are the median of 11 runs (5 for Wand). ImageMagick runs Q16 while Pillow-SIMD uses 8-bit fixed point.
- Only 4-byte UINT8 resampling is vectorised (L, I;16 and F modes stay scalar); INT16 coefficients hold at most 15 bits against upstream Pillow's 22-bit INT32, so output is not bit-identical to Pillow. setup.py hard-codes -msse4 with no runtime dispatch and the ARM build fails (#116, #143); sdist only, no wheels; open PR #149 (ImageMath.eval hardening). The libvips wiki row is probably the SSE4 build (plain pip install); in the same c5.large pillow-perf file cv2 beats it on bilinear upscale (0.052 against 0.076 s).

## Caveats and trade-offs

pillow-perf is maintained by the Pillow-SIMD author, so its numbers are first-party; the README's '16 to 40 times' figure lives on the blocked github.io page, and the checked-in c5.large file shows 11-23x. Different precision: ImageMagick in the pillow-perf run comes from Ubuntu's libmagickwand-dev (ImageMagick 6 Q16, 16-bit quantum) while Pillow-SIMD works in 8-bit fixed point; the Wand path also includes Python binding overhead and an image clone per run. Pillow-SIMD 7.0.0 in the result file is old. In the libvips table pillow-simd is single-threaded while ImageMagick may thread, and the task includes TIFF load and save, not only resampling. Language filter mismatch: Pillow-SIMD is a CPython extension (C kernels with SSE4/AVX2 behind a Python API), not a standalone C/C++ library, so it is not directly callable from C++. ImageMagick (on the category list) is present; stb_image_resize is not. GitHub fork of python-pillow/Pillow that tracks Pillow releases.

Drop-in replacement for Pillow in Python only (must replace the Pillow install; x86 only, SSE4 and AVX2). C core is not a standalone library, so it is not callable from C++ without embedding Python. Pillow license is HPND (listed in the repo as PIL/PILLOW license).

## Maintenance

Active: SIMD kernels were re-landed on Pillow 12.3.0 on 2026-09-17 and sdists up to 12.1.1.post0 were uploaded to PyPI on 2026-09-15 after a two-year gap at 9.5.0, but there are still no wheels; MIT-CMU licensed and maintained mainly by one Uploadcare developer (homm).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the libvips 'Speed and memory use' wiki table, an independent and widely cited suite with public code (libvips/vips-bench pillow.py vs im.sh), measures pillow-simd 9.5.0 at 1.51 s against ImageMagick 7.1.1 convert at 4.44 s on a Threadripper PRO 3955WX, but the pillow-simd build flags and compiler are not stated, so not A. The first-party pillow-perf data (c5.large.txt, testsuite/run.py, auto/run.sh with -msse4/-mavx2) alone would be C: compiler and exact CPU model are not printed.
- **Verifier notes:** All c5.large.txt numbers verified; the record wrongly said 'mean of 11 runs' (it is a median, 5 runs for Wand and Pillow). The libvips wiki row is independent and lifts the tier to B. License is MIT-CMU per the LICENSE file, and the repository is a GitHub fork of python-pillow/Pillow.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `license`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/c5.large.txt>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/HEAD/README.md>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/LICENSE>
  - <https://github.com/uploadcare/pillow-simd>
  - <https://github.com/uploadcare/pillow-simd/commits/simd/master>
  - <https://github.com/python-pillow/pillow-perf>
  - <https://github.com/python-pillow/pillow-perf/tree/master/docs/src/data>
  - <https://github.com/python-pillow/pillow-perf/tree/master/testsuite>
  - <https://github.com/python-pillow/pillow-perf/tree/master/testsuite/cases>
  - <https://github.com/python-pillow/pillow-perf/tree/master/auto>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/auto/run.sh>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/auto/install_ubuntu.sh>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/auto/Vagrantfile>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/run.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand.py>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use>
  - <https://github.com/libvips/vips-bench>
  - <https://raw.githubusercontent.com/libvips/vips-bench/HEAD/pillow.py>
  - <https://raw.githubusercontent.com/libvips/vips-bench/HEAD/im.sh>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/HEAD/README.md>
  - <https://github.com/uploadcare/pillow-simd>
  - <https://github.com/uploadcare/pillow-simd/commits/simd/master>
  - <https://github.com/uploadcare/pillow-simd/tree/simd/master/src/libImaging>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/src/libImaging/ImagingSIMD.h>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/src/libImaging/ResampleSIMDHorizontalConv.c>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/src/libImaging/ResampleSIMDVerticalConv.c>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/src/libImaging/Resample.c>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/src/libImaging/ImPlatform.h>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/src/libImaging/Imaging.h>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/src/PIL/_version.py>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/setup.py>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/pyproject.toml>
  - <https://raw.githubusercontent.com/uploadcare/pillow-simd/simd/master/_custom_build/backend.py>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/main/src/libImaging/Resample.c>
  - <https://pypi.org/pypi/pillow-simd/json>
  - <https://github.com/uploadcare/pillow-simd/issues?q=is%3Aissue>
  - <https://github.com/uploadcare/pillow-simd/issues/155>
  - <https://github.com/uploadcare/pillow-simd/issues/157>
  - <https://github.com/uploadcare/pillow-simd/issues/133>
  - <https://github.com/uploadcare/pillow-simd/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/docs/src/data/c5.large.txt>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/run.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/base.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/pillow_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/cases/wand_scale.py>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/testsuite/requirements.txt>
  - <https://raw.githubusercontent.com/python-pillow/pillow-perf/HEAD/auto/run.sh>
  - <https://raw.githubusercontent.com/emcconville/wand/0.5.8/wand/resource.py>
  - <https://raw.githubusercontent.com/emcconville/wand/master/wand/resource.py>
  - <https://github.com/libvips/libvips/wiki/Speed-and-memory-use>
  - <https://raw.githubusercontent.com/libvips/vips-bench/HEAD/pillow.py>
  - <https://raw.githubusercontent.com/libvips/vips-bench/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/uploadcare/pillow-simd`) · [data/wave10/enrich/raw/github_com_uploadcare_pillow_simd.json](../../../data/wave10/enrich/raw/github_com_uploadcare_pillow_simd.json) (enrichment confidence 0.85)

</details>
