# TinyScaler

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🔴 abandoned

> Python/Cython float32 RGBA image downscaler with SSE C kernels; beats Pillow by skipping antialiasing, loses to OpenCV bilinear.

| | |
|---|---|
| **Beats** | Pillow resize (bilinear) and OpenCV cv2.resize (area filter); scikit-image also timed |
| **Claimed result** | Bilinear, 100 resizes (author's benchmark_bilinear.py): TinyScaler 0.797 s vs OpenCV 0.487 s (OpenCV about 1.6x faster, fair float32 RGBA pair); vs Pillow 12.67 s (about 15.9x, but Pillow received uint8 RGBA and uses a wider antialiased filter); the scikit-image row (164.45 s, about 206x) is invalid (transposed 852x567 output with default Gaussian anti-aliasing). Area filter: TinyScaler 4.35 s vs OpenCV 8.12 s (about 1.9x), but the area kernel is mis-weighted (weights 1-2, overlapping 3x3 mean at 2x). |
| **Workload** | Resize one 4928x3279 image down to 852x567, 100 times, single thread, using bilinear filtering (and area filtering against OpenCV), timed with Python perf_counter. |
| **Metric** | throughput |
| **Hardware** | AMD 1950x (as stated in the README) |
| **Compiler and flags** | C kernels (SSE3 via pmmintrin.h on x86_64, Neon on Arm) built as a Cython extension; setup.py adds no optimization flags on x86_64/arm64 (-mfpu=neon only on 32-bit Arm), so Python's default extension flags apply; compiler, flags and library versions for the benchmark run not stated |
| **Links** | [repository](https://github.com/Farama-Foundation/TinyScaler) · [benchmark](https://github.com/222464/TinyScaler/tree/master/examples) |

## Verdict

The project's scripts (examples/benchmark_bilinear.py and benchmark_area.py, reachable in the author's original 222464/TinyScaler repo, whose scaler.c matches the 1.2.8 sdist) convert the NASA 4928x3279 PNG to float32 RGBA and resize it to 852x567 100 times with OpenCV set to one thread, on an AMD 1950X. Bilinear: TinyScaler 0.797 s vs OpenCV INTER_LINEAR 0.487 s (OpenCV 1.64x faster). Area: TinyScaler 4.35 s vs OpenCV INTER_AREA 8.12 s (1.87x, derived from page data), but on a mis-weighted kernel. Pillow (12.67 s) did antialiased resizing of uint8 RGBA, skimage (164.45 s) produced a transposed, Gaussian-prefiltered output, and compiler, flags and library versions are not stated.

## Use it when

- RL observation preprocessing (Gymnasium/PettingZoo style) where frames are already float32 RGBA and you want to avoid an opencv-python dependency.
- Large non-integer downscale ratios (the benchmark used about 5.8x) where aliasing is acceptable and you need nearest or bilinear speed within about 1.6x of OpenCV.
- Tight loops that reuse a preallocated float32 (h, w, 4) dst buffer; that only avoids allocations when the input is also float32 RGBA.
- Linux or Intel macOS x86_64 builds with GCC or Clang, the only 64-bit targets where the SSE path is compiled.

## Skip it when

- Quality-sensitive downscaling: bilinear has no antialiasing, and 'area' mis-weights pixels (at exactly 2x it averages a 3x3 block that overlaps the next output's block).
- Raw speed when OpenCV is acceptable: cv2.resize INTER_LINEAR was 1.64x faster in the project's own run. Sibling fast_image_resize reports 3.53 ms (AVX2, u8 RGB, antialiased convolution, different machine) for the same NASA 4928x3279 to 852x567 job, against TinyScaler's 7.97 ms per call.
- uint8 RGB pipelines: every call expands to float32 RGBA (16 bytes per pixel instead of 3) and converts back by truncation.
- Apple Silicon, Linux aarch64 and Windows: the SIMD code is guarded by `__x86_64__` (GCC/Clang only, not MSVC) or `__arm__` (32-bit ARM only), so the arm64 macOS slice, aarch64 builds and win_amd64 wheels run the scalar fallback.
- Anything needing a maintained dependency: it was deprecated on 2025-08-11, the Farama GitHub repo now returns 404, and wheels stop at CPython 3.12.

## How it is fast

Each output pixel is one 128-bit SSE vector (NEON on 32-bit ARM) holding all four RGBA float channels. Bilinear is a 2x2 point-sampled lerp with no antialiasing, so its filter support does not grow with the scale factor. 'area' sums a box of source pixels with approximate edge weights. The speedup over Pillow comes from doing far fewer taps than Pillow's support-scaled convolution. There is no separable pass, no precomputed coefficient table and no threading, and the plain C file is built with Python's default extension flags.

## Compared with alternatives

Pick TinyScaler only when you need a dependency-light Python wheel on float32 RGBA frames and can accept aliasing. OpenCV is faster for bilinear and has a correct INTER_AREA, and Pillow-SIMD and Lycon give antialiased or OpenCV-grade resizing from Python. From C, C++ or Rust, stb-image-resize-opt or fast_image_resize are faster and filter correctly.

## Integration

| | |
|---|---|
| **Form** | Python extension module (Cython wrapper over one C file, src/scaler.c plus scaler.h); the C file can be dropped into a C or C++ project |
| **Dependencies** | numpy&gt;=1.21.0 for the Python package; the C core needs only libc and libm |
| **Minimum toolchain** | Python &gt;= 3.8 (wheels for CPython 3.8 to 3.12); building from the sdist needs Cython, setuptools and a C compiler |
| **Platforms** | Wheels for Linux x86_64 (manylinux2014), macOS (universal2 and x86_64) and Windows amd64. SSE path only with GCC/Clang on x86_64, NEON path only on 32-bit ARM (setup.py adds -mfpu=neon there); everything else uses scalar C. |
| **Thread safety** | The C kernels are pure functions with no shared state, but the Cython wrapper calls them while holding the GIL (no nogil block), so Python threads cannot resize in parallel. Conversions are controlled by the module-global `auto_convert` flag. |
| **Drop-in for the baseline** | no |

## Gotchas

- Area weights are wrong. In scale_area_4f32 the second weight term tests area_y == src_upper_y, which the loop never reaches, so it is always 1. Every pixel therefore gets weight 1 to 2 instead of its 0 to 1 coverage, and the upper bound includes the pixel at floor(upper)+1. A 1-D simulation of the code gives a uniform 3-tap average per output at 8 to 4 (exact: 2 taps). At the benchmark's 4928 to 852 ratio, an edge pixel with 3.7% coverage gets 9.2% of the weight.
- Bilinear always loads the right and lower neighbours (p01, p10) even when their weight is zero, so a source 1 pixel wide or 1 pixel high is read past the row or the buffer. Since 0 x NaN = NaN, garbage can reach the output. 'area' falls back to this bilinear path whenever either axis is upscaled.
- `size` is (width, height) while arrays are (height, width, channels). uint8 results are truncated by astype rather than rounded. For uint8 input with 1 or 3 channels the wrapper returns a sliced, non-contiguous view, which scale() rejects ('Input image must be contiguous') if you feed it back in.
- Benchmark harness flaws on the baseline side: Pillow received uint8 RGBA and ran its antialiased BILINEAR, and skimage was called as resize(img, (852, 567)). skimage reads that as (rows, cols), so it produced a transposed 852x567x4 output, and its default anti_aliasing (True when downsampling, per the v0.19.3 source) adds a Gaussian prefilter. The 206x skimage ratio is not a valid comparison.

## Known shortcomings

- Repository gone from github.com (page and raw 404; deprecated 2025-08-11 per a search snippet), so the numbers come from the PyPI 1.2.8 description and the C source from the sdist. The 15.9x against Pillow is not equal work (2x2-tap bilinear, no antialiasing); OpenCV bilinear is 1.6x faster; the area kernel uses approximate weights.
- Corrections (retier-28): the author's original repo 222464/TinyScaler holds the benchmark scripts, so the harness is reachable. The 206x against scikit-image is invalid (skimage was called as resize(img, (852, 567)), a transposed output with default Gaussian anti-aliasing) and Pillow got uint8 RGBA; the fair float32 RGBA pair shows OpenCV bilinear 1.64x faster. The area kernel is mis-weighted (second weight term always 1, so a 2x downscale is an overlapping 3x3 mean) and its 1.87x win runs that kernel; bilinear reads out of bounds for 1-pixel sources; SIMD only on GCC or Clang x86_64 or 32-bit arm (aarch64, Apple Silicon and MSVC wheels scalar); the GIL is held.

## Caveats and trade-offs

The GitHub repo page and raw.githubusercontent.com (README, examples/benchmark.py) all returned 404 on 2026-10-04, and no mirror or fork was found. A WebSearch snippet of the old repo page says the project was deprecated on 2025-08-11 for lack of community use (snippet only). The README text was read from the PyPI description of tinyscaler 1.2.8 (uploaded 2024-08-02), and the C source and MIT license come from its sdist. The benchmark script is not in the sdist, so the run could not be inspected, and it is unknown which dtype and channel layout the other libraries received. TinyScaler itself converts uint8/RGB input to float32 RGBA. The bilinear kernel (src/scaler.c scale_bilinear_4f32) is a 2x2-tap point-sampled bilinear without antialiasing, while Pillow's BILINEAR downscale widens its filter support with the scale factor. The 15.9x win over Pillow therefore compares different work and output quality. OpenCV INTER_LINEAR is the like-for-like comparison and is 1.6x faster than TinyScaler. The area kernel (scale_area_4f32) is an approximate box filter: its loop never reaches src_upper, so the upper partial row/column gets full weight and the lower edge weights are approximate. It does not do exact fractional-area integration like OpenCV INTER_AREA, so the 1.9x area win is also not equal work. Compiler flags and library versions are not stated. Not compared against ImageMagick or stb_image_resize. [retier] Repository moved from Farama-Foundation (404) to the author's github.com/222464/TinyScaler; PyPI 1.2.8 deprecated 2025-08-11. Correctness: the area kernel's second weight term is always 1 (overlapping 3x3 mean at 2x), bilinear reads out of bounds for 1-pixel-wide or -high sources, SIMD builds only with GCC or Clang on x86_64 or 32-bit arm (aarch64, Apple Silicon and MSVC wheels are scalar), and the GIL is held during resize.

Downscaling-focused CPU scaler with SIMD for x86_64 and Arm Neon, exposed to Python through Cython and a C core (src/scaler.c, src/scaler.h in the sdist). Supports only area, bilinear and nearest filters. Input must be a contiguous numpy array and is converted to 4-channel float32. Aimed at replacing OpenCV for resize in Gymnasium and PettingZoo wrappers. Linux and macOS wheels.

## Maintenance

Deprecated by Farama on 2025-08-11 (search snippet) and gone from the Farama GitHub org. The last release is 1.2.8 (2024-08-02); the code is MIT and a single 448-line C file that is easy to vendor, but fix the area weights and the edge reads first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The numbers appear verbatim in the README Performance section mirrored in the PyPI description of tinyscaler 1.2.8, with the CPU stated (AMD 1950x). The benchmark script (examples/benchmark.py) cannot be reached, because the GitHub repo returns 404 and the script is not in the sdist, and no compiler or flags are stated. First-party README text only, so tier C.
- **Verifier notes:** The repo is 404 on github.com (page and raw), as the batch notes said. Tiered C on the PyPI-mirrored README, and the source was checked from the 1.2.8 sdist on files.pythonhosted.org. Both quoted wins compare unequal work (no antialiasing against Pillow, approximate area weights against OpenCV INTER_AREA); the like-for-like bilinear comparison shows OpenCV faster.
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `maintenance_status`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://pypi.org/pypi/tinyscaler/json>
  - <https://pypi.org/project/tinyscaler/>
  - <https://files.pythonhosted.org/packages/0d/59/6b6495fe9bb3153306a4bd6dd24c78ff74eaf64f90fc6e545ede0574cfbe/tinyscaler-1.2.8.tar.gz>
  - <https://github.com/Farama-Foundation/TinyScaler>
  - <https://raw.githubusercontent.com/Farama-Foundation/TinyScaler/HEAD/README.md>
  - <https://raw.githubusercontent.com/Farama-Foundation/TinyScaler/main/README.md>
  - <https://raw.githubusercontent.com/Farama-Foundation/TinyScaler/main/examples/benchmark.py>
- **Sources the enricher read:**
  - <https://github.com/Farama-Foundation/TinyScaler>
  - <https://pypi.org/pypi/tinyscaler/json>
  - <https://pypi.org/project/tinyscaler/>
  - <https://files.pythonhosted.org/packages/0d/59/6b6495fe9bb3153306a4bd6dd24c78ff74eaf64f90fc6e545ede0574cfbe/tinyscaler-1.2.8.tar.gz>
  - <https://github.com/222464?tab=repositories&q=scaler>
  - <https://github.com/222464/TinyScaler>
  - <https://github.com/222464/TinyScaler/tree/main/examples>
  - <https://raw.githubusercontent.com/222464/TinyScaler/HEAD/README.md>
  - <https://raw.githubusercontent.com/222464/TinyScaler/HEAD/setup.py>
  - <https://raw.githubusercontent.com/222464/TinyScaler/HEAD/src/scaler.c>
  - <https://raw.githubusercontent.com/222464/TinyScaler/HEAD/examples/benchmark_bilinear.py>
  - <https://raw.githubusercontent.com/222464/TinyScaler/HEAD/examples/benchmark_area.py>
  - <https://raw.githubusercontent.com/scikit-image/scikit-image/v0.19.3/skimage/transform/_warps.py>
  - <https://raw.githubusercontent.com/Cykooz/fast_image_resize/HEAD/README.md>
  - WebSearch: Farama-Foundation TinyScaler deprecated repository
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/farama-foundation/tinyscaler`) · [data/wave10/enrich/raw/github_com_farama_foundation_tinyscaler.json](../../../data/wave10/enrich/raw/github_com_farama_foundation_tinyscaler.json) (enrichment confidence 0.8)

</details>
