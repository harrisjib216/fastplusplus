# libblur

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause OR Apache-2.0` · 🟢 active

> Rust SIMD blur crate (Gaussian, stack, box, median); exact large-kernel Gaussian about 4x faster than multithreaded OpenCV GaussianBlur.

| | |
|---|---|
| **Beats** | OpenCV (Gaussian blur, stack blur and median blur) |
| **Claimed result** | Gaussian blur, 3000x4000 RGB 8-bit, multithreaded (harness uses kernel 155 with sigma 25.83 for both libraries although the README says 151): libblur Exact 49.40 ms (NEON) and 43.41 ms (AVX) versus OpenCV 180.56 ms and 182.44 ms, about 3.7x and 4.2x (derived from page data); libblur FixedPoint, which the README says adds 1-3% error, 26.68 ms and 30.72 ms, about 6.8x and 5.9x (derived). Single plane 3000x4000: Exact 17.59 ms and 15.51 ms versus OpenCV 74.73 ms and 64.20 ms, about 4.2x and 4.1x (derived). The RGBA Gaussian rows (65.13/51.40 ms versus 134.60/185.30 ms) and stack-blur rows (RGB 4.95/5.30 ms versus 8.43/10.36 ms, about 1.7x and 2.0x derived) time OpenCV on a 2-channel BGR565 Mat because of a cvtColor argument bug, and the median rows (RGB 603.51/872.03 ms versus 637.83/959.07 ms, about 1.06x and 1.10x derived) are not produced by the public median harness. |
| **Workload** | Multithreaded 8-bit blur of 3000x4000 RGB, 2828x4242 RGBA and 3000x4000 single-plane images: Gaussian with kernel size 151, stack blur with radius 77, median blur with radius 35. |
| **Metric** | latency |
| **Hardware** | Two unnamed machines labelled NEON and AVX (or SSE) in the README tables; CPU models not stated |
| **Adoption** | 88 stars; crates.io about 101k downloads |
| **Last commit** | 2026-05-08 |
| **Links** | [repository](https://github.com/awxkee/libblur) · [benchmark](https://github.com/awxkee/libblur) |

## Verdict

First-party criterion runs (app/benches/gauss/main.rs) on two unnamed machines labelled NEON and AVX, against OpenCV 4.x through the opencv crate (version, build and thread count unstated), both multithreaded: the Exact Gaussian on a 3000x4000 RGB 8-bit image with kernel 155 and sigma 25.83 (README says 151) took 49.40/43.41 ms against OpenCV's 180.56/182.44 ms (about 3.7x/4.2x, derived from page data), and on a single 3000x4000 plane 17.59/15.51 ms against 74.73/64.20 ms (about 4.2x/4.1x, derived). OpenCV's 8-bit ALGO_HINT_ACCURATE path here is GaussianBlurFixedPoint, which quantizes kernel weights to 8 fractional bits (ufixedpoint16), so it is bit-exact across platforms but not more precise in its weights than libblur's f32 Exact mode. The README's RGBA Gaussian, stack-blur, box and median rows are not backed by matching harness code, and the tables were last edited in May 2025, before the 2026 kernel rewrites.

## Use it when

- Rust pipelines that need a true Gaussian with large kernels (tens to \~150+ taps) on 8-bit RGB, RGBA or grayscale frames in the 10-12 MP range, run multithreaded, without linking OpenCV.
- Code that must run the same SIMD-accelerated blur on x86-64 and aarch64 (Apple silicon, ARM servers), including u16 and f32 images or arbitrary separable kernels.
- UI, thumbnail or background-blur work where an approximation is acceptable: stack_blur, fast_gaussian_next and box_blur are the crate's fastest paths (author's speed order: box, stack, fast_gaussian_next, fast_gaussian, ..., gaussian, bilateral, median).
- Builds that want pure Rust (no C/C++ toolchain); wasm32 with simd128 is partially covered.

## Skip it when

- When output must match OpenCV bit for bit: weights, intermediate rounding and borders differ (libblur benches use Clamp; OpenCV defaults to reflect-101), and the default ConvolutionMode is the approximate FixedPoint.
- From C or C++ without writing your own FFI shim and adding a Rust toolchain; no C header or extern "C" API ships.
- Median blur as a speed play: the README shows only 3-16% over OpenCV (derived) and no public harness produces those rows; the per-pixel cost grows with radius (sliding histogram, not Perreault O(1)).
- Small kernels or small images: the README publishes no numbers below kernel 151 (the gauss harness has 3- and 13-tap cases but no results), and each multithreaded call spawns fresh threads.
- Analysis that needs an analytic Gaussian: the approximations are flagged by the author as unsuitable for advanced analysis, and FixedPoint adds a stated 1-3% error.

## How it is fast

The Gaussian is a separable two-pass convolution that folds the symmetric kernel (adds mirrored taps before one multiply, halving multiplies) in hand-written intrinsics for AVX2+FMA and SSE4.1 (chosen at runtime with is_x86_feature_detected), NEON with RDM, SVE and AVX-512 (opt-in) and wasm simd128. Exact mode uses f32 weights with FMA accumulation; FixedPoint mode scales weights to Q15 integers with i32 accumulators. The vertical pass computes 2 output rows (x86) or 3 (NEON) per iteration to reuse loaded rows, kernels of 61 taps or fewer use a sliding row buffer instead of a full transient image, and rows are split into static zones across threads from the author's novtb crate. Stack and box blurs are O(1)-per-pixel running sums; median is a Huang-style sliding 256-bin histogram per channel.

## Compared with alternatives

Pick libblur over the C++ Gaussian siblings (LibGaussianBlur, archived in 2024; zanazakaryaie/fastGaussianBlur, a tutorial; bfraboni/FastGaussianBlur, an approximation with no OpenCV comparison) when you can take a Rust dependency and want a maintained exact Gaussian plus fast approximations, u16/f32 support and NEON/AVX kernels in one crate. Pick FastBoxBlur or bfraboni's header-only code when you need a C++ source drop and a box or approximate blur is enough.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | num-traits, rayon, num-complex, novtb (author's scoped thread-pool crate, which uses core_affinity); optional image 0.25 (feature image) and zaft (feature fft) |
| **Minimum toolchain** | Rust 1.89 for 0.24.0 (rust-version in Cargo.toml, edition 2024); nightly for the sve, nightly_f16 and nightly_fcma features (avx512 needs nightly before 1.89). The repo's own rust-toolchain.toml pins an unversioned nightly. |
| **Platforms** | x86-64 (SSE4.1 and AVX2+FMA selected at runtime; AVX-512 opt-in feature), aarch64 NEON (RDM on by default; SVE on nightly), wasm32 simd128 partial, scalar fallback elsewhere |
| **Thread safety** | Functions are stateless and work on caller-provided buffers. ThreadingPolicy chooses Single, Adaptive (width\*height/65536 threads capped at available cores), AdaptiveReserve or Fixed. The ThreadingPolicy docs warn that fast bilateral relies on Rayon and can use excessive memory and CPU when it is called from work already scheduled by an outside Rayon pool; issue #67 reported memory not being released when fast_gaussian_next_f32 ran under Rayon with Adaptive/Fixed (closed with linked PR #68). |
| **Drop-in for the baseline** | partial — same operation as cv::GaussianBlur (separable Gaussian from kernel size and sigma, sigma default uses OpenCV's 0.3\*((k-1)/2-1)+0.8 formula), but a Rust-only API, different border default and rounding, so results are not bit-identical |

## Gotchas

- ConvolutionMode::FixedPoint is the default (doc comment: estimated error not less than 1-2%); pass ConvolutionMode::Exact for f32 weights. In both modes the horizontal pass is stored in the image's own type (u8 for 8-bit) before the vertical pass, so 'Exact' means f32 weights and accumulation, not a float intermediate.
- Kernel sizes must be odd: GaussianBlurParams::new with an even size returns BlurError::OddKernel, while new_from_kernel rounds to the nearest odd size and derives sigma.
- Every parallel stage of every call spawns new scoped OS threads through novtb and pins them to cores round-robin with core_affinity; this adds spawn cost per call and can collide with other pinned workloads or thread pools.
- Kernels are rewritten often: 0.23.0 (2026-02-13) skipped rows in the single-plane FixedPoint Gaussian (issue #86, fixed in 0.23.1 by PR #87 'Fix skipped rows'), and earlier f32 Gaussian artifacts were reported in issues #21 and #38. Pin the version and compare output after upgrades.

## Known shortcomings

- Only the Gaussian RGB exact rows (about 3.7-4.2x; app/benches/gauss/main.rs with kernel 155 and sigma 25.83 on both sides, labelled 151; OpenCV on its threaded bit-exact SIMD path without IPP or HAL, border Clamp against reflect-101, OpenCV's destination allocated inside the timed loop) survive scrutiny. Harness bugs invalidate the rest: cvt_color is passed CV_8UC3 (16, which is COLOR_BGRA2BGR565) as the code, so OpenCV's 'RGBA' and stack-blur inputs are 2-channel; the OpenCV stack-blur radius is 38 against libblur's 77; the RGB stack run uses 2828x4242 dimensions on a 3000x4000 buffer; the median harness runs single-threaded at radius 1-4 on different images and cannot produce the README's radius-35 table. No CPU, OpenCV build or flags.
- Enricher (e100, 2026-10-05): the Exact-mode Gaussian win of about 4x holds for RGB and single plane, but OpenCV's 8U ALGO_HINT_ACCURATE path (GaussianBlurFixedPoint) quantizes weights to 8 fractional bits, so the 'approximation vs bit-exact' caveat overstates the precision gap. The box-blur README rows are also unbacked: OpenCV box_filter is called with normalize=false, the 'RGBA' OpenCV input is 3-channel BGR, the RGB row uses kernel 35 rather than the stated 77 radius, and libblur's RGB source is the RGBA test_image_4 buffer read as 3 channels. No C API (cbindgen.toml empty, no FFI in lib.rs). README tables last edited 2025-05-09, before the 2026 kernel rewrites (v0.24.0); the 0.23.0 skipped-rows regression (#86, fixed in 0.23.1) postdates the tables. novtb spawns and core-pins fresh threads on every parallel stage of every call.

## Caveats and trade-offs

First-party README tables with no CPU model (machines labelled only NEON and AVX/SSE), no OpenCV version or build options, no thread count and no rustc flags (rust-toolchain.toml says nightly). Harness review (app/benches): (1) Gaussian RGB is the cleanest comparison: both sides use kernel 155 and sigma 25.83 (README labels it 151) and both are threaded; OpenCV runs with ALGO_HINT_ACCURATE, which in OpenCV 4.x selects the bit-exact fixed-point SIMD path (parallel_for_) and skips the HAL and IPP approximate paths, so the libblur FixedPoint figures (1-3% error) compare an approximation against a bit-exact result; borders differ (libblur Clamp versus OpenCV BORDER_DEFAULT reflect-101) and OpenCV allocates a new 36 MB destination Mat inside the timed loop while libblur reuses a preallocated buffer. (2) The single-plane Exact run uses kernel 151 against OpenCV's 155. (3) Every 'RGBA' and 'RGB' OpenCV input built with cvt_color(&src, &mut dst, CV_8UC3, CV_8UC4, ...) passes CV_8UC3 (=16) as the conversion code, which is COLOR_BGRA2BGR565, so OpenCV actually blurs a 2-channel 8-bit Mat: the RGBA Gaussian rows and both stack-blur rows compare OpenCV on 2 bytes per pixel against libblur on 3-4 bytes per pixel. (4) Stack blur: OpenCV is called with Size(77,77), i.e. radius 38, while libblur uses radius 77, and libblur's RGB run is given the 2828x4242 dimensions of test_image_4.png for the 3000x4000 buffer of test_image_1.jpg (same byte count, wrong geometry), matching the stride and label bugs seen in the author's sparkyuv and yuvutils-rs harnesses. (5) The public median harness (updated 2026-05-05) is single-threaded with radius 1-4 and compares libblur on test_image_2.png (720x1080 RGBA) against OpenCV on test_image_4.png (2828x4242 loaded as 3-channel), so it cannot have produced the README's multithreaded radius-35 median table. Median gain is 3-16% at best (derived). 'Gaussian blur in 100 FPS for 4K photo' is directional. Rust crate with a cbindgen C API.

Rust crate with NEON, SSE, AVX, SVE and partial WASM kernels; calling from C++ needs an FFI wrapper (no C API verified). Includes fast approximations (stack blur, fast gaussian, box) that are not true Gaussian and are flagged by the author as unsuitable for advanced analysis; FixedPoint Gaussian adds 1 to 3 percent error.

## Maintenance

Active: v0.24.0 on crates.io 2026-05-09 (about 101k downloads), last commit 2026-05-08, 685 commits and 0 open issues; dual Apache-2.0/BSD-3-Clause, so copyable, but Rust-only with no C API.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** README tables are first-party and come from public criterion harnesses (app/benches/gauss/main.rs, stack_blur/main.rs, median/main.rs, using the opencv crate 0.98.1), but no CPU model, OpenCV version/build or rustc flags are stated (toolchain is unpinned nightly), so not A. Only the RGB and single-plane Gaussian rows are backed by a harness that matches its label closely; the stack-blur, RGBA and median rows rest on harness bugs or code that does not produce them.
- **Verifier notes:** Real Gaussian win of about 4x for the Exact mode on RGB and single plane is supported by a harness with matching kernel and sigma, but the stack-blur, RGBA and median rows are mislabelled or unbacked (cvtColor code bug makes OpenCV inputs 2-channel; median harness does different work), so the claim was narrowed to the Gaussian rows; tier stays C. License (Apache-2.0 OR BSD-3-Clause), last commit 2026-05-08 and active status confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party README tables
- **Pages the verifier opened:**
  - <https://github.com/awxkee/libblur>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/README.md>
  - <https://github.com/awxkee/libblur/tree/master/app>
  - <https://github.com/awxkee/libblur/tree/master/app/benches>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/app/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/app/benches/gauss/main.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/app/benches/stack_blur/main.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/app/benches/median/main.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/app/benches/box/main.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/assets/test_image_1.jpg>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/assets/test_image_2.png>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/assets/test_image_4.png>
  - <https://github.com/awxkee/libblur/commits/master>
  - <https://github.com/awxkee/libblur/commits/master/app/benches/median/main.rs>
  - <https://crates.io/api/v1/crates/libblur>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/include/opencv2/imgproc.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/smooth.dispatch.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/smooth.simd.hpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/stackblur.cpp>
  - <https://raw.githubusercontent.com/twistedfall/opencv-rust/HEAD/examples/video_facedetect.rs>
- **Sources the enricher read:**
  - <https://github.com/awxkee/libblur>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/cbindgen.toml>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/app/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/app/benches/gauss/main.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/app/benches/stack_blur/main.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/app/benches/median/main.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/app/benches/box/main.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/threading_policy.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/median_blur.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/primitives.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/gaussian/mod.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/gaussian/declaration.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/gaussian/gaussian_hint.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/gaussian/gaussian_util.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/gaussian/gaussian_kernel.rs>
  - <https://github.com/awxkee/libblur/tree/master/src/filter1d>
  - <https://github.com/awxkee/libblur/tree/master/src/filter1d/avx>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/filter.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/filter_1d_approx.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/filter_row_symmetric_approx.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/filter_column_approx_symmetric.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/to_approx_storage.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/filter_scan.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/arena.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/filter_1d_row_handler.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/avx/filter_column_symm_approx_x2.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/avx/filter_row_symm.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/filter1d/avx/filter_column_symm_x2.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/box_filter/mod.rs>
  - <https://raw.githubusercontent.com/awxkee/libblur/HEAD/src/box_filter/box_blur.rs>
  - <https://github.com/awxkee/libblur/issues?q=is%3Aissue>
  - <https://github.com/awxkee/libblur/issues/86>
  - <https://github.com/awxkee/libblur/issues/67>
  - <https://github.com/awxkee/libblur/pull/87>
  - <https://github.com/awxkee/libblur/commits/master>
  - <https://github.com/awxkee/libblur/commits/master/README.md>
  - <https://github.com/awxkee/libblur/commit/4e95210>
  - <https://github.com/awxkee/libblur/commit/63956bf>
  - <https://github.com/awxkee/libblur/commit/0424e41>
  - <https://crates.io/api/v1/crates/libblur>
  - <https://crates.io/api/v1/crates/novtb>
  - <https://raw.githubusercontent.com/awxkee/novtb/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/novtb/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/smooth.dispatch.cpp>
  - <https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/fixedpoint.inl.hpp>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/awxkee/libblur`) · [data/wave10/enrich/raw/github_com_awxkee_libblur.json](../../../data/wave10/enrich/raw/github_com_awxkee_libblur.json) (enrichment confidence 0.75)

</details>
