# kornia-rs (Image.resize and imgproc kernels, kornia-py)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust/Python (PyO3) vision library whose NEON u8 resize and colour kernels beat OpenCV bilinear resize on aarch64 Jetson.

| | |
|---|---|
| **Beats** | OpenCV 4.13.0 cv2.resize (INTER_LINEAR, INTER_CUBIC, INTER_LANCZOS4) and cv2.cvtColor; Pillow 12.2.0 Image.resize (LANCZOS) |
| **Claimed result** | kornia-py/benchmarks.md (Jetson Orin Cortex-A78AE, best-of-N min, random-noise 1080p RGB u8). The bake-off row 'resize 1080p-&gt;720p (Lanczos)' reads kornia 1.67 ms vs cv2 7.36 ms (4.4x) vs PIL 43.6 ms, but bake_off_pil_cv2.py calls k_img.resize(1280, 720) and Image.resize defaults to interpolation="bilinear" (pyo3 signature in kornia-py/src/image.rs, same at commit 9e040c4 where the bake-off was added), so that row is kornia bilinear against Lanczos4/LANCZOS, not a Lanczos result. Like-for-like bilinear rows from the resize matrix (kornia bilinear vs cv2 INTER_LINEAR): 1080p-&gt;2160p 1.78 vs 9.80 ms (5.52x, exact-2x vrhaddq_u8 fast path), 1080p-&gt;224x224 0.25 vs 0.72 ms (2.84x), 1080p-&gt;540p 0.42 vs 0.82 ms (1.97x), 640-&gt;320 0.09 vs 0.29 ms (3.09x). Lanczos: kornia's kernel is 3-lobe against OpenCV's 4-lobe INTER_LANCZOS4 (bench_resize_vs_libs.py docstring); with antialias=False kornia is 1.64x (1080p-&gt;540p, 4.15 vs 6.80 ms), 2.47x (224x224), 1.66x (640-&gt;320) and 1.07x (2160p up) faster; with the default antialias=True kornia Lanczos is slower than cv2 on downscale, 8.63 vs 6.80 ms (0.79x), 7.13 vs 4.57 ms (0.64x), 2.90 vs 2.53 ms (0.87x), and bicubic AA 0.85x and 0.55x at 1080p (derived from page data), but faster than Pillow LANCZOS with the same AA semantics: 5.3x, 4.2x, 3.1x (derived from page data). Bicubic antialias=False vs INTER_CUBIC: 1.75x, 2.93x, 1.60x, 1.21x. Colour conversions vs cv2.cvtColor (1080p f32): RGB-&gt;Lab 1.55x, grayscale u8 1.48x, XYZ 1.03x, HLS 1.00x, HSV 0.91x, Luv 0.87x; the page's byte-exactness table gives different ratios for the same ops (Lab 1.35x, XYZ 1.08x, YCbCr 0.84x, HSV 0.73x, HLS 0.69x, Luv 0.61x). JPEG decode 39.64 vs 39.3 ms (tie, libjpeg-turbo on all sides), JPEG encode 0.94x. |
| **Workload** | Python bake-off on a random-noise 1080p RGB u8 array, best-of-N minimum time per call with GC disabled (kornia-py/benchmarks/bake_off_pil_cv2.py and _bench.py), plus a resize matrix over bilinear, bicubic and lanczos with antialias on and off for several shapes and a colour-conversion table; no output comparison is published alongside the timings (bench_resize_vs_libs.py can print byte fidelity but its results are not on the page). |
| **Metric** | latency |
| **Hardware** | NVIDIA Jetson Orin (aarch64), Cortex-A78AE, 6 cores at 1.728 GHz max, LPDDR5, JetPack R36.4.3, Linux 5.15.148-tegra |
| **Compiler and flags** | Rust 1.93.0, release build with opt-level=2 (LLVM bug workaround for faer), NEON intrinsics, rayon; pyo3 0.28, Python 3.10.12 (the script header says pixi py312), numpy 2.2.6, OpenCV 4.13.0 (build not stated; the script's install hint is opencv-python; no cv2.setNumThreads call, so OpenCV ran with its default threading), Pillow 12.2.0; run at commit 07e52d7 on branch feat/gray-f32-neon (2026-06-20), a commit that returns 404 on GitHub |
| **Adoption** | 720 stars, 205 forks; crates.io crate kornia and PyPI package kornia-rs; v0.2.0 released 2026-09-26 |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/kornia/kornia-rs) · [benchmark](https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks.md) |

## Verdict

These are first-party numbers from kornia-py/benchmarks.md on a Jetson Orin (Cortex-A78AE, 6 cores, Rust 1.93.0 at opt-level=2, OpenCV 4.13.0 at default threads, Pillow 12.2.0), best-of-N minimum on random 1080p RGB u8, run at commit 07e52d7, which is not on GitHub. The like-for-like bilinear comparison against cv2 INTER_LINEAR shows 1.55-1.97x at 1080p to 540p, 1.33x (derived from page data) to 2.84x at 1080p to 224x224, 3.09x to 4.1x (derived from page data) at 640 to 320, and 5.52x on the exact-2x upscale. Each range spans the matrix's aa=True and aa=False columns, which run identical code because antialias does not affect bilinear, so the spread is run-to-run noise. The 2x-upscale output carries a +0.74 LSB rounding bias that the page does not disclose.

## Use it when

- Python or Rust pipelines on aarch64 edge boards (Jetson Orin, Raspberry Pi 5, Apple silicon) that call cv2.resize INTER_LINEAR on u8 RGB frames. The Orin page shows 1.55-1.97x at 1080p to 540p and 3.09x at 640 to 320, plus 5.52x on an exact 2x upscale, where the output is slightly biased (see gotchas).
- Model-input preprocessing: resize_normalize_to_tensor fuses resize, /255, mean/std and HWC-to-CHW into one pass to f32, replacing a cv2-plus-numpy chain; a CUDA Preprocessor does the same on device.
- Replacing Pillow LANCZOS or BICUBIC with the same antialiased semantics on ARM, where Pillow-SIMD has no NEON path: kornia's antialiased Lanczos is 3.1-5.3x faster than Pillow 12.2.0 on the Orin (derived from page data).
- RGB to Lab in f32 where colour-grade precision is enough: 1.35-1.55x faster than cv2.cvtColor, and closer to true Lab than OpenCV's LUT-interpolated f32 path, according to the page.
- Free-threaded CPython (3.13t/3.14t) or GIL-free Rust services that want thread-safe image ops with numpy and DLPack zero-copy.

## Skip it when

- Antialiased (default) bicubic or Lanczos downscaling as a cv2 replacement: it is slower than OpenCV on the page's own matrix, Lanczos at 0.64-0.87x and bicubic AA at 0.55-0.85x. Its antialias=False Lanczos is 3-lobe (6 taps) against OpenCV's 8-tap INTER_LANCZOS4, so even those wins do less work.
- x86-64: there are no published x86 numbers. The general bilinear row kernel is scalar on every architecture, the exact-2x downscale and upscale row kernels are scalar off aarch64, and the CIE colour kernels fall back to scalar under AVX2. Issue #667 (January 2026, open, hardware unstated, predates the April-June 2026 tuning) reported bilinear resize 1.7-4.9x slower than OpenCV.
- Pipelines that need byte-for-byte OpenCV output: bicubic uses a = -0.5 (Pillow) while OpenCV INTER_CUBIC uses A = -0.75, Lanczos has 3 lobes against OpenCV's 4, Lab and Luv differ by up to 0.67, and the exact-2x upscale is biased.
- Non-u8 resizing (f32/u16 fast resize is the open issue #862), and HSV, HLS, Luv or YCbCr conversions, where kornia is at parity or slower than cv2 (0.61-1.08x across the page's two colour tables).
- Codec speed claims from the same bake-off: JPEG is a tie (libjpeg-turbo on all sides). In the 23x WebP row, cv2.imencode('.webp') with no parameters actually runs lossless libwebp (OpenCV grfmt_webp.cpp falls back to lossless when no quality is given), which contradicts the page's 'lossy' note; PIL's is lossy. File sizes are not reported, and PNG level 1 is set against PIL's default level.

## How it is fast

A dispatch cascade sends special cases to dedicated kernels. An exact 2x bilinear downscale becomes a 2x2 box average (NEON vpaddlq_u8 plus vrshrn), and an exact 2x upscale uses fixed {0.25, 0.75} weights computed with vrhaddq_u8 pairs. General bilinear precomputes Q14 tap LUTs per column and spreads 16-row chunks across rayon threads; the per-row loop itself is scalar. Bicubic and Lanczos3 follow the Pillow-style separable two-pass Q14 convolution: an i16 intermediate, u16 column LUTs, a 4-row NEON horizontal kernel that shares coefficient loads, and an L2-aware strip-fused H-then-V plan. antialias=False fixes the taps at 4 or 6 instead of widening them with the scale. The f32 colour kernels deinterleave with vld3q, apply the 3x3 matrix in registers, and use a degree-4 log2 / degree-3 exp2 pow and a one-iteration Halley cbrt (about 4e-4 and 2.3e-5 relative error).

## Compared with alternatives

Pick kornia-rs on aarch64 (Python or Rust) when you want numpy-in, numpy-out, multi-threaded bilinear resize and colour conversion that beats cv2 there, with optional CUDA dispatch. Pick fast_image_resize for antialiased convolution resizing in Rust on x86-64 AVX2 (single-thread, beats libvips), Pillow-SIMD for antialiased resizing in Python on x86, and OpenCV itself for bicubic/Lanczos downscales or byte-exact cv2 output.

## Integration

| | |
|---|---|
| **Form** | crate (kornia or kornia-imgproc), plus a PyO3 wheel (kornia-rs on PyPI) and C++ bindings (kornia-cpp) |
| **Dependencies** | kornia-imgproc: rayon, wide, num-traits, thiserror, kornia-image/-tensor/-algebra; optional cudarc and half (cuda feature). Python wheel: numpy; turbojpeg (needs nasm to build) on by default in kornia-py |
| **Minimum toolchain** | Rust 1.89 (workspace rust-version); Python 3.8-3.14 including free-threaded builds; maturin &gt;= 1.9 to build the wheel |
| **Platforms** | aarch64 NEON first (Linux incl. Jetson, macOS, Windows arm64); x86-64 with AVX2 for some resize kernels (blend, separable H/V passes) chosen at run time, scalar elsewhere; wheels for manylinux x86_64/aarch64, macOS x86_64/arm64, win_amd64/arm64; optional CUDA path loaded lazily |
| **Thread safety** | The README says it is thread-safe, including under free-threaded Python. Each call runs internally across the global rayon pool, so concurrent callers share those threads. |
| **Drop-in for the baseline** | partial: it accepts numpy u8 arrays and returns numpy, but the API, argument order (imgproc.resize takes (h, w), cv2 takes (w, h)), defaults (antialias=True) and kernels differ from cv2.resize and Pillow |

## Gotchas

- The exact-2x bilinear upscale fast path (the 5.52x row) computes 0.75a+0.25b as rhadd(a, rhadd(a, b)) in both passes and requantizes to u8 between them. The code comment says this equals round(0.75a+0.25b), but double rounding always rounds up: a pure-Python replay of the scalar reference on random u8 input gave a +0.74 LSB mean bias against float64 bilinear, with 71% of pixels 1 LSB above the correctly rounded value (max 1 LSB). The unit test checks only the four corner pixels, and bench_resize_vs_libs.py has no 2x-upscale case, so a 1920x1080 to 3840x2160 resize comes out slightly brighter than a 3838-wide one, which takes the general Q14 path.
- Image.resize on 1- or 4-channel images silently ignores the interpolation argument and runs a floor-convention nearest-neighbour resize. Only 3-channel input reaches the bilinear, bicubic and Lanczos kernels.
- Image.resize defaults to interpolation="bilinear", antialias=True. The page's '1080p-&gt;720p (Lanczos)' bake-off row actually ran this bilinear default against cv2 INTER_LANCZOS4 and PIL LANCZOS, so it says nothing about Lanczos speed.
- The rust doc of xyz_from_rgb says it gamma-decodes, but the kernel is matrix-only (to match cv2 COLOR_RGB2XYZ), so it is not colorimetric sRGB-to-XYZ; use linear_rgb_from_rgb first if you need that. The bicubic/Lanczos column LUT is u16, guarded only by a debug_assert, so release builds would silently wrap source columns for images wider than 65,535 px.

## Known shortcomings

- Downgraded A to C: bake_off_pil_cv2.py calls k_img.resize(1280, 720) with Image.resize's default interpolation bilinear (at HEAD and 9e040c4), so the 'Lanczos 4.4x' pits bilinear against cv2 INTER_LANCZOS4 and PIL LANCZOS; kornia's Lanczos is 3-lobe against cv2's 4-lobe, and with antialias on its Lanczos downscale is slower than cv2 (0.79x, 0.64x, 0.87x, derived from page data). The matrix aa and PIL columns are not produced by the committed scripts, the run commit 07e52d7 is a 404, cv2.setNumThreads is never set and the OpenCV build is unstated. The like-for-like bilinear wins (5.52x, 2.84x, 1.97x, 3.09x) stand.
- Enricher (e112, 2026-10-05): numeric flaw behind the 5.52x 2x-upscale row: pyrup_2x_rgb_u8 double-rounds rhadd(a, rhadd(a, b)) in both passes, a +0.74 LSB mean bias with 71% of pixels 1 LSB high (Python replay of the scalar reference); the test checks corners only and the fidelity script lacks the 2x-up case. The bilinear matrix's aa=True and aa=False columns run identical code yet differ 2.2x (224^2: 1.33x vs 2.84x), so the bilinear ratios are noise-bound. Image.resize on 1- or 4-channel images silently falls back to nearest; bicubic uses a=-0.5 vs OpenCV's A=-0.75; the general bilinear row is scalar on all architectures, x86 pyrdown/pyrup rows are scalar and CIE colour AVX2 falls back to scalar; cv2.imencode('.webp') defaults to lossless, so the page note is wrong; the u16 column LUT wraps above 65535 px (debug_assert only). Issue #667 user report: resize 1.7-4.9x slower than OpenCV (2026-01, hardware unstated). C stands.

## Caveats and trade-offs

First-party numbers on one ARM machine (Jetson Orin), no x86 results. The headline 4.4x 'Lanczos' resize is kornia bilinear (the default interpolation of Image.resize) against cv2 INTER_LANCZOS4 and PIL LANCZOS, so it compares different work and the page's 'at the same kernel' note is wrong. kornia's Lanczos is 3-lobe while OpenCV's INTER_LANCZOS4 is 4-lobe, so even the antialias=False rows do fewer taps than OpenCV; with the default antialias=True kornia Lanczos and bicubic are slower than OpenCV on downscale and only beat Pillow. kornia runs rayon across 6 cores; OpenCV threading is left at its default and not reported. The resize matrix has aa=True, aa=False and PIL columns that the committed bench_resize_modes.py does not produce (it times only the default antialias against cv2 and has no 640x640 case), and the measured commit 07e52d7 is not reachable on GitHub, so the published table cannot be regenerated exactly from public code. The page states 'OpenCV 4.13.0' in the run info but labels the colour section 'OpenCV 5', and two colour tables on the same page give different ratios for the same conversions. Inputs are uniform random noise. The page itself says resize 1080p is noise-bound (1.81-2.03x run to run). JPEG decode and encode are ties because all three use libjpeg-turbo; WebP and PNG encode wins compare different settings (kornia lossless WebP vs lossy, PNG level 1 vs PIL default). A WebSearch snippet of arXiv 2501.13131 (page blocked, snippet only) reports JPEG decode on Apple M4 Max of 1034 images/s for kornia-rs vs 1016 for OpenCV and 775 for Pillow; the current ternaus/imread_benchmark README does not mention kornia, so that figure is unverified. The bilinear rows (kornia bilinear vs INTER_LINEAR, max 1 LSB difference per bench_resize_vs_libs.py) are the defensible like-for-like claims and could support tier A on a rerun of bench_resize_modes.py at a public commit with the OpenCV build and thread count stated.

Aarch64 NEON fast paths come first and AVX2 exists only for some ops; rayon multithreading; Rust crate plus PyO3 Python wheels and kornia-cpp bindings; antialias=True matches PIL semantics and antialias=False matches OpenCV INTER_CUBIC and LANCZOS4 semantics (different work). Pillow-SIMD is not in the matrix because it is x86-only.

## Maintenance

Actively developed: 1,001 commits, v0.2.0 released 2026-09-26, last commit 2026-09-27, 720 stars, kornia-imgproc at about 47.6k crates.io downloads. Apache-2.0 and usable as a crate or a wheel, but the speed work targets aarch64 first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** The harness is public (kornia-py/benchmarks/bake_off_pil_cv2.py, _bench.py, bench_resize_modes.py) and Rust 1.93.0 opt-level=2 on a Cortex-A78AE is stated, but the headline 'resize 1080p-&gt;720p (Lanczos)' row times kornia's default bilinear against cv2 INTER_LANCZOS4 and PIL LANCZOS, the resize matrix's aa=False and PIL columns are not produced by any committed script, the measured commit 07e52d7 returns 404 on GitHub, and the OpenCV build and thread count are unstated, so the numbers are first-party with partial methodology.
- **Verifier notes:** Downgraded A to C: the 4.4x Lanczos headline is bilinear vs Lanczos4 (Image.resize default interpolation="bilinear" at HEAD and at 9e040c4), matrix columns are not regenerable from committed scripts, and run commit 07e52d7 is 404. Best like-for-like claim is bilinear: 5.52x on exact-2x upscale, 1.97x-3.09x elsewhere; antialiased Lanczos and bicubic lose to OpenCV on downscale.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `workload`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** first-party benchmark vs OpenCV
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks.md>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks/bake_off_pil_cv2.py>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks/_bench.py>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks/bench_resize_modes.py>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks/bench_resize_vs_libs.py>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks/bench_resize.py>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/python/kornia_rs/image.pyi>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/src/image.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/src/resize.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/9e040c4/kornia-py/src/image.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/9e040c4/kornia-py/benchmarks/bake_off_pil_cv2.py>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/07e52d7/kornia-py/src/image.rs>
  - <https://github.com/kornia/kornia-rs>
  - <https://github.com/kornia/kornia-rs/commits/main>
  - <https://github.com/kornia/kornia-rs/commit/07e52d7>
  - <https://github.com/kornia/kornia-rs/tree/main/kornia-py>
  - <https://github.com/kornia/kornia-rs/tree/main/kornia-py/benchmarks>
  - <https://github.com/kornia/kornia-rs/tree/main/kornia-py/python/kornia_rs>
  - <https://github.com/kornia/kornia-rs/tree/main/kornia-py/src>
  - <https://raw.githubusercontent.com/ternaus/imread_benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/kornia/kornia-rs>
  - <https://github.com/kornia/kornia-rs/commits/main>
  - <https://github.com/kornia/kornia-rs/issues?q=is%3Aissue+resize>
  - <https://github.com/kornia/kornia-rs/issues/667>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks.md>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks/bake_off_pil_cv2.py>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks/_bench.py>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks/bench_resize_modes.py>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/benchmarks/bench_resize_vs_libs.py>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/src/image.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/src/resize.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/Cargo.toml>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/kornia-py/pyproject.toml>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/Cargo.toml>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/lib.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/resize/mod.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/resize/pyramid.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/resize/kernels.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/resize/separable.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/resize/common.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/resize/bilinear.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/resize/nearest.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/resize/opencv_compat.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/interpolation/mod.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/color/mod.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/color/cie/mod.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/color/cie/kernels.rs>
  - <https://raw.githubusercontent.com/kornia/kornia-rs/HEAD/crates/kornia-imgproc/src/color/gray/mod.rs>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/resize.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgcodecs/src/grfmt_webp.cpp>
  - <https://crates.io/api/v1/crates/kornia-imgproc>
  - <https://pypi.org/pypi/kornia-rs/json>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/kornia/kornia-rs`) · [data/wave10/enrich/raw/github_com_kornia_kornia_rs.json](../../../data/wave10/enrich/raw/github_com_kornia_kornia_rs.json) (enrichment confidence 0.8)

</details>
