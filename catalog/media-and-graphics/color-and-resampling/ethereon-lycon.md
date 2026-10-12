# Lycon

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python with C++ core` · `BSD-3-Clause (OpenCV-derived code) and MIT (Lycon changes)` · 🔴 abandoned

> Small OpenCV-derived resize and JPEG/PNG I/O extension for NumPy; beats Pillow 4.0 and scikit-image, ties OpenCV.

| | |
|---|---|
| **Beats** | Pillow (PIL) 4.0.0 and scikit-image 0.12.3 via their Python APIs; OpenCV 3.2+ cv2 (whose code Lycon reuses) runs at parity |
| **Claimed result** | Seconds, Lycon vs PIL: upsample bilinear 0.4852 vs 7.2940 (15x), downsample bilinear 0.0258 vs 1.3122 (51x), downsample bicubic 0.1324 vs 1.8153 (13.7x), downsample Lanczos 0.3317 vs 2.4058 (7.2x); resize speed equals OpenCV (0.0258 vs 0.0257 for downsample bilinear); JPG read 0.3409 vs OpenCV 0.5085 (1.5x) and PIL 1.4081 (4.1x). |
| **Workload** | Resize of a 16k (15360x8640) RGB image with nearest, bilinear, bicubic, Lanczos and area interpolation, plus JPEG and PNG read and write, averaged over 10 runs. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 (Skylake), Ubuntu 14.04; OpenCV 3.2+ (master a85b4b5), Pillow 4.0.0, skimage 0.12.3, Python 2.7.3 |
| **Compiler and flags** | CMakeLists.txt: -std=c++11 -march=native -O3 -fPIC -DNDEBUG -pthread (static libstdc++ on Linux); compiler and version not stated. |
| **Adoption** | 288 stars |
| **Last commit** | 2019-01-21 |
| **Links** | [repository](https://github.com/ethereon/lycon) · [benchmark](https://raw.githubusercontent.com/ethereon/lycon/HEAD/README.md) |

## Verdict

First-party 2017 table (perf/benchmark.py, mean of 10 runs after one warm-up, 15360x8640 RGB image, Ubuntu 14.04 on an unnamed Skylake Core i7, compiler not named): Lycon's resize ties OpenCV 3.2+ to within 1-3% and beats single-threaded Pillow 4.0.0 by 2.3x-51x and float64 scikit-image 0.12.3 by 66x-200x, but it runs OpenCV's multi-threaded, non-antialiased kernels against Pillow's wider filters. Its only gains over OpenCV are JPEG read (1.5x) and JPEG write (1.3x), with no explanation of the libjpeg builds.

## Use it when

- Python data loaders on x86-64 Linux that need OpenCV-equivalent resize speed and JPEG/PNG I/O in RGB order without pulling in all of OpenCV.
- Bulk upscaling or downscaling of large 8-bit or float32 RGB arrays where OpenCV's interpolation (no antialiasing on downscale) is acceptable.
- Replacing Pillow 4-era or scikit-image resize calls in old pipelines where the multi-threaded OpenCV kernels give 2.3x-51x on a 15360x8640 image (README table).

## Skip it when

- Anywhere opencv-python(-headless) is already installed: the README itself says the advantages are minimal, and the table shows resize at 1x OpenCV.
- Quality-sensitive downscaling: bilinear, bicubic and Lanczos use fixed 2/4/8-tap kernels with no antialiasing, unlike Pillow's support-widened filters, so Pillow output differs and aliases less.
- Apple Silicon, PowerPC, Windows or modern Python: issue #29 (cv_vrndq_u32_f32 undefined on arm64 macOS), #21 (-march=native rejected on PowerPC), #15 (no Windows support) and install failures #22/#23/#30 are open; PyPI has only source tarballs, the last being 0.2.0 from 2019-01-21.
- Long-running processes on CPython older than 3.12 that call lycon.save many times: the binding returns Py_None without a new reference and crashes with 'Fatal Python error: deallocating None' (issue #26, about 10,000 calls).
- Formats beyond JPEG and PNG, alpha-aware or EXIF-orientation control, or decoding from memory buffers (issues #12, #13, #24 open).

## How it is fast

Speed comes from OpenCV's separable fixed-tap resize kernels (SSE2/SSE4.1 on x86 with runtime CPUID checks, NEON for the cubic, Lanczos and area paths only), split across all cores by a pthreads parallel_for_, with the GIL released during load, save and resize. An exact 2x INTER_LINEAR downscale is rewritten to a 2x2 box average (area fast path), and the PNG writer defaults to zlib level 1 with the SUB filter and Z_RLE strategy. The CMake build compiles everything with -O3 -march=native.

## Compared with alternatives

Pick Lycon over OpenCV only when you need cv2.resize behavior in a tiny source-built extension with RGB order and can build on x86-64; otherwise opencv-python-headless gives the same kernels, maintained. Pick Pillow-SIMD when you need antialiased downscaling in a Pillow-compatible API, and fast_image_resize (Rust) for a maintained SIMD resizer with convolution filters.

## Integration

| | |
|---|---|
| **Form** | Python extension module built from source by CMake through setup.py (pip sdist); static C++ library 'lycon' with no install rules |
| **Dependencies** | libjpeg, libpng, NumPy, CMake 2.8.11+, make, a C++11 compiler |
| **Minimum toolchain** | C++11 (GCC or Clang); tested in 2017 with Python 2.7 and 3.5 |
| **Platforms** | Linux and macOS on x86-64 as tested in 2017; arm64 macOS build fails (issue #29); no Windows |
| **Thread safety** | Releases the GIL around load, save and resize; resize uses an internal pthreads pool sized to the online CPU count; thread safety of concurrent calls is not documented |
| **Drop-in for the baseline** | partial: same algorithms and speed as cv2.resize, imread and imwrite (RGB order instead of BGR), but not an API replacement for Pillow or scikit-image |

## Gotchas

- lycon.save ends with 'return Py_None;' and the resize failure path does the same, with no Py_INCREF, so every save call drops a reference to None; CPython below 3.12 eventually aborts (issue #26). On 3.12+ None is immortal, which hides it.
- The PNG writer defaults to zlib level 1, SUB filter and Z_RLE (OpenCV's speed setting), while Pillow 4.0 defaults to compress_level -1 (zlib level 6): the 4.2x PNG-write win over PIL partly buys larger files. Pass Encode options for a fair comparison.
- -march=native is hard-coded in CMakeLists.txt, so a build is tied to the build machine's CPU (issue #28: prebuilt wheel fails on another CPU) and breaks on compilers that reject the flag.
- JPEG decoding can differ from Pillow's: issue #19 reports about 11% of pixels off by an average of 1.46 on one JPEG, from whichever libjpeg the build linked.

## Known shortcomings

- Python with a C++ (OpenCV-derived) core (language-filter mismatch). perf/benchmark.py with -O3 -march=native, compiler unnamed, CPU only 'Core i7 Skylake'. Measured work differs: Lycon's resize is multithreaded (pthreads parallel_for_) against single-threaded Pillow 4.0, the 2x bilinear downsample becomes a 2x2 area average with no anti-aliasing versus Pillow's widened convolution, PIL times include fromarray/asarray copies and skimage outputs float64. Same speed as OpenCV, whose code it reuses.
- Correctness bug (not behind the timings): save and the resize failure path return Py_None without Py_INCREF, so CPython before 3.12 aborts with 'deallocating None' after about 10k saves (issue #26). The 4.2x PNG-write win partly buys bigger files: default zlib level 1 with SUB filter and Z_RLE against Pillow 4.0's compress_level -1 (level 6). Build broken on arm64 macOS (#29) and PowerPC -march=native (#21); sdist only, last release 0.2.0 on 2019-01-21; JPEG pixels differ from Pillow (#19).

## Caveats and trade-offs

First-party 2017 numbers from perf/benchmark.py (mean of 10 runs after one warm-up, 15360x8640 RGB image) against Pillow 4.0.0, scikit-image 0.12.3 and OpenCV 3.2+, on an unnamed Skylake Core i7 with no compiler named. The measured code does different work from the Pillow and skimage baselines: (1) Lycon's resize is OpenCV's resize code and runs multi-threaded through its pthreads parallel_for_ (src/lycon/util/defs.h HAVE_PTHREADS_PF; transform/resize/invoker.h), while Pillow 4.0 resizes on one thread; (2) for the exact 2x downsample used, Lycon (like OpenCV) turns INTER_LINEAR into the fast 2x2 area average (invoker.h line 207, hence Downsample Bilinear 0.0258 s = Downsample Area 0.0258 s), and its bicubic/Lanczos use fixed 4x4/8x8 taps without antialiasing, while Pillow's BILINEAR/BICUBIC/LANCZOS convolve with support widened by the reduction factor, so the 51x/13.7x/7.2x downsample ratios compare different filters; (3) the PIL timings include Image.fromarray and np.asarray copies of a \~400 MB image; (4) skimage.transform.resize returns float64. Against OpenCV, which does the same work, resize is at parity (1x) and only JPEG read/write is faster (1.3-1.5x, likely a libjpeg build difference). Old Pillow (before Pillow-SIMD-era and 5.x resize work). Last commit 2019-01-21.

Small subset of OpenCV's resize derived from OpenCV, with JPEG and PNG I/O and NumPy zero-copy interop; Linux and macOS only; the README says its advantages over OpenCV are minimal if OpenCV is installed.

## Maintenance

Abandoned since January 2019 (37 commits, 16 open issues including build failures on arm64 and an interpreter-crashing refcount bug); BSD-3-Clause plus MIT, so the resize code can still be vendored, but upstream OpenCV is the maintained source of the same kernels.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README table compares Lycon with OpenCV 3.2+, Pillow 4.0.0 and scikit-image 0.12.3 and every quoted number matches; the harness is public (perf/benchmark.py) and flags are in CMakeLists.txt (-std=c++11 -march=native -O3), but the compiler is never named and the CPU is only 'Intel Core i7 (Skylake)', so first-party with partial methodology: C.
- **Verifier notes:** Numbers are accurate to the README, but the resize gains are versus slower, single-threaded, differently-filtered Pillow and float64 skimage; versus OpenCV, the code it was derived from, there is no resize gain. Language field should read 'Python with C++ core' via a decision override (corrections cannot set language). Metadata confirmed: 288 stars, BSD-3-Clause (OpenCV-derived) plus MIT, not archived, not a fork, abandoned.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ethereon/lycon/HEAD/README.md>
  - <https://github.com/ethereon/lycon>
  - <https://github.com/ethereon/lycon/commits>
  - <https://github.com/ethereon/lycon/tree/master/perf>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/perf/benchmark.py>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/LICENSE>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/setup.py>
  - <https://github.com/ethereon/lycon/tree/master/src/lycon>
  - <https://github.com/ethereon/lycon/tree/master/src/lycon/util>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/transform/resize.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/transform/resize/invoker.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/util/parallel.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/util/parallel.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/util/parallel_pthreads.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/defs.h>
- **Sources the enricher read:**
  - <https://github.com/ethereon/lycon>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/README.md>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/setup.py>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/LICENSE>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/perf/benchmark.py>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/lycon/__init__.py>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/lycon/core.py>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/lycon/enum.py>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/python/module.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/python/module.io.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/python/module.transform.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/python/macros.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/python/interop.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/transform/resize.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/transform/resize/invoker.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/transform/resize/linear.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/transform/resize/cubic.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/transform/resize/lanczos.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/transform/resize/area.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/transform/resize/nearest.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/transform/resize/common.h>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/io/io.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/io/jpeg.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/io/png.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/util/parallel.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/util/parallel_pthreads.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/util/hardware.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/mat/allocator.cc>
  - <https://raw.githubusercontent.com/ethereon/lycon/master/src/lycon/defs.h>
  - <https://github.com/ethereon/lycon/issues?q=is%3Aissue>
  - <https://github.com/ethereon/lycon/issues/19>
  - <https://github.com/ethereon/lycon/issues/26>
  - <https://github.com/ethereon/lycon/issues/29>
  - <https://pypi.org/pypi/lycon/json>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/4.0.0/PIL/PngImagePlugin.py>
  - <https://raw.githubusercontent.com/python-pillow/Pillow/4.0.0/PIL/JpegImagePlugin.py>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/ethereon/lycon`) · [data/wave10/enrich/raw/github_com_ethereon_lycon.json](../../../data/wave10/enrich/raw/github_com_ethereon_lycon.json) (enrichment confidence 0.8)

</details>
