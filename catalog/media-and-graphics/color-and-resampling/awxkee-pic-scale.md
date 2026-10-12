# pic-scale

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `BSD-3-Clause OR Apache-2.0` · 🟢 active

> Rust SIMD image-resampling crate with 30+ filters and colour-space-aware scaling; no valid speed comparison against fast_image_resize exists.

| | |
|---|---|
| **Beats** | fast_image_resize (the baseline series of the repo's speedtest harness; no published result) |
| **Claimed result** | none valid. The current README has no numbers. README revisions up to v0.6.11 (e.g. commit 927a4fa, 2025-04-30) had a Performance table for downscaling a 4928x3279 image 4x with Lanczos3: RGB pic-scale 10.47 (AVX2) / 6.97 (NEON) against fast_image_resize 15.62 / 21.74; RGBA without premultiplication 11.13 / 7.76 against 20.17 / 25.92, Apple Accelerate 9.98 (NEON); units unstated. Those runs used the pre-0.6.12 kernel-size code (src/scaler.rs: filter_base_size = min_kernel_size, so a Lanczos3 window of radius 1.5 x scale instead of 3 x scale), i.e. pic-scale used roughly half the taps of fast_image_resize. The section was removed in commit 30b40e5 ('Filter generation fix', v0.6.12, 2025-10-16), which doubled the kernel size. |
| **Workload** | No published result found. speedtest/src/runner.rs times RGBA8, u16 and f32 resizes of a 4928x3279 PNG, winter_huge.jpg and sample_fhd.jpg against fast_image_resize 6.0.0, pic-scale-safe 0.1.10 and Apple Accelerate and plots SVG charts. |
| **Metric** | latency |
| **Compiler and flags** | speedtest crate: pic-scale features nightly_f16, rdm, nightly_i8mm, avx, sse; edition 2024; geometric mean of per-iteration times after 10 warm-up runs |
| **Adoption** | 41 stars, 1 fork; crate pic-scale 0.7.12 with about 1.45 million crates.io downloads (1.33 million recent); 5 crates.io dependents (hayro, media-core, oximg, spectrograph, zenresize; some may be dev-dependencies) |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/awxkee/pic-scale) |

## Verdict

Nothing valid is measured. Up to v0.6.11 the README showed a Lanczos3 4x-downscale table against fast_image_resize (for example RGB 10.47 vs 15.62 with AVX2; units and rustc version not given). Those runs used a kernel at half the correct Lanczos3 support, so pic-scale did about half the work, and commit 30b40e5 (v0.6.12) fixed the kernel and deleted the table. The current speedtest harness (4928x3279 RGBA8, single thread on both sides, geometric mean after 10 warm-ups) publishes no results.

## Use it when

- Rust code that needs gamma-correct or perceptual resizing (linear light, Oklab, Lab, sigmoidal) without writing the conversion passes yourself.
- Pipelines with formats most resizers lack: f16 (nightly), AR30/RA30 10-bit packed, 10/12/16-bit u16 with an explicit bit depth, signed i16 planes, or YUV chroma (CbCr) planes.
- Repeated resizes of the same geometry (video frames, tiles), where one plan plus a reused scratch buffer avoids recomputing weights and allocating per call.
- Apple Silicon or other ARMv8.2+/v8.6 hosts where a lower-precision fast path is acceptable for thumbnails (RDM by default, i8mm with nightly_i8mm).
- Projects that already pull it in transitively: its largest crates.io dependent is the hayro PDF renderer (hayro 0.7.1 alone has about 1.26 million downloads).

## Skip it when

- When you need a measured speed advantage: no valid published comparison exists. The old README table was taken on a Lanczos3 kernel at half the correct support (fixed in v0.6.12), and the current speedtest commits no results.
- When output must be bit-exact across CPUs or match a reference: the default PreferSpeed mode picks different arithmetic per ISA (Q0.7 int8 weights on i8mm ARM, RDM i16 on ARMv8.1+, Q15 i16 on x86), and issue #161 (Aug 2026) found SIMD and scalar results diverging; set WorkloadStrategy::PreferQuality if this matters.
- Releases before 0.7.12: issue #161 listed a sign-bit loss in the SSE f32-to-f16 fallback that corrupted Lanczos output with negative taps, an out-of-bounds read in a NEON f16 row kernel, Miri-flagged misaligned NEON loads and an SVE2 kernel that assumed 128-bit vectors. These were fixed in PR #164 (merged 2026-09-10, the day 0.7.12 was published). Issue #150 (an all-zero last row on a 1x5 to 2x5 CatmullRom resize) was fixed in PR #151 in May 2026.
- C or C++ code bases that want a stable, documented library: the C++ header needs a nightly Rust build with -Z build-std, and covers six filters only. zimg (C++) or libvips are more natural there.
- Stable-Rust users who need f16, i8mm or SVE paths: those sit behind nightly-only features.

## How it is fast

It does separable convolution with per-output weight tables computed once at plan time and quantised to fixed point. On x86 the u8 paths use Q15 i16 weights with _mm256_madd_epi16 into i32 (SSE4.1 and AVX2 runtime-dispatched; AVX-VNNI under the avx512 feature). On aarch64 the default WorkloadStrategy::PreferSpeed switches to cheaper arithmetic: with RDM (scale below 8) pixels are shifted left 6 bits into i16 and multiplied with vqrdmulh, and with the nightly_i8mm feature on an i8mm CPU (scale below 10) both passes use Q0.7 int8 weights and vusdot dot products. Rows are processed four at a time, and an optional novtb thread pool splits rows when ThreadingPolicy is Fixed or Adaptive. Optional supersampling pre-shrinks large downscales (3x or more) with Box or Nearest before the quality filter.

## Compared with alternatives

Pick it over fast_image_resize when you need colour-space-aware scaling, f16/AR30/CbCr formats, built-in threading or the exotic EWA/Jinc filters. fast_image_resize is the safer choice for plain 8-bit resizing, because it has reproducible numbers against libvips, the image crate and the resize crate, while pic-scale has none. In C++ projects, zimg or stb-image-resize-opt avoid a nightly Rust build.

## Integration

| | |
|---|---|
| **Form** | crate (plus an optional static library with a C++ header from the picscale/ subcrate) |
| **Dependencies** | num-traits, pxfm; optional novtb (threading, on by default) and colorutils-rs (colorspaces feature) |
| **Minimum toolchain** | Rust 1.89 (rust-version in Cargo.toml, edition 2024); nightly for nightly_f16, nightly_i8mm, nightly_avx512fp16, sve and for building the C bindings |
| **Platforms** | x86-64 and i686 (SSE4.1 and AVX2 detected at run time; AVX-512/AVX-VNNI with the avx512 feature), aarch64 NEON (RDM, i8mm, fp16 detected at run time; SVE2 partial), wasm32 with simd128 enabled at compile time, scalar fallback elsewhere (CI builds powerpc and riscv64) |
| **Thread safety** | Plans are returned as Arc&lt;dyn ResamplingPlan + Send + Sync&gt; and resample through &self, so one plan can serve several threads, each with its own scratch and destination (from reading the source; not stated in the README). Internal threading is off by default (ThreadingPolicy::Single); Fixed(n) or Adaptive opt in. |
| **Drop-in for the baseline** | no |

## Gotchas

- SIMD is a cargo feature, not automatic: default-features = false (for example to drop the novtb threading dependency) turns off neon, rdm, sse and avx and leaves scalar code only. zenresize's paired_bench documents this ('by default pic-scale builds scalar-only') because it depends on pic-scale with default features off.
- WorkloadStrategy::PreferSpeed is the default. On ARM it trades precision for speed (RDM i16 path, or Q0.7 int8 weights when nightly_i8mm is on), and the source comments warn that the RDM path 'won't work really well on huge kernel'. On x86, PreferSpeed turns the AVX-VNNI horizontal u8 kernel off.
- With ThreadingPolicy::Fixed or Adaptive, a new novtb pool is constructed for each filter pass of every call rather than reused. Adaptive uses one thread per 65,536 output pixels, capped at available_parallelism.
- The README example still uses LinearScaler, which needs the non-default 'colorspaces' feature. It also mentions a 'nightly_avx512' feature that Cargo.toml names 'avx512'.

## Known shortcomings

- Tier D: the old README table (v0.6.11 at 927a4fa; Lanczos3 RGB 4x downscale 6.97 against fast_image_resize 21.74 ms on NEON, 10.47 against 15.62 on AVX2) was measured on pre-0.6.12 code whose Lanczos3 kernel was half width (radius 1.5x the scale instead of 3x, about half the taps), and the same commit 30b40e5 'Filter generation fix' (2025-10-16) fixed the kernel and deleted the table; the current speedtest runner.rs allocates the fast_image_resize destination at width x width. 1.45M crates.io downloads.
- Enricher (2026-10-04): beyond the half-support Lanczos3 kernel and the width x width destination bug, the speedtest crate enables rdm and nightly_i8mm with the default WorkloadStrategy::PreferSpeed, so on aarch64 it picks Q0.7 int8 weights with vusdot (i8mm, scale below 10) or the RDM i16 path ('slightly lower precision') against fast_image_resize's i16 weights with i32 accumulation: any ARM chart from that harness compares a lower-precision kernel against a higher-precision one. Issue #161 (2026-08-23) documented correctness bugs in released SIMD paths (SSE f32-to-f16 fallback dropped the sign bit, NEON f16 row kernel read out of bounds, Miri misaligned NEON loads and out-of-bounds reads in vertical_f32, SVE2 dot kernel hard-coded 128-bit offsets), fixed in PR #164 (0.7.12, 2026-09-10). SIMD is a cargo feature: default-features = false leaves scalar code only; Fixed/Adaptive threading builds a new novtb pool per filter pass; README example needs the non-default 'colorspaces' feature. Nothing valid is measured; D stands.

## Caveats and trade-offs

The current README, repo page and speedtest folder (src and Cargo.toml only) carry no results. Current harness bug confirmed: in speedtest/src/runner.rs, runner_rgba_fir allocates the fast_image_resize destination with Image::new(target_size.width, target_size.width, ...), i.e. width x width. make_sizes produces proportional non-square targets (w/2 x h/2 and so on for the 4928x3279 PNG), so fast_image_resize renders a taller output than pic-scale, which would flatter pic-scale in any chart. pic-scale reuses a precomputed plan, scratch and destination buffers, while fast_image_resize rebuilds its options per call; fast_image_resize runs single-threaded. Historical numbers are invalid for comparison: the README Performance table (present up to v0.6.11, e.g. commit 927a4fa; Apple M3 Pro for NEON, an unnamed 'Premium Intel CPU Optimized 4 vCPU Digital Ocean instance' for AVX2; criterion benches in app/benches/resize_rgb and resize_rgba, both libraries single-threaded, rustc version and flags not given) was measured when pic-scale's src/scaler.rs set the Lanczos3 kernel size to round(3 x scale) with radius 1.5 x scale, half the support of a correct Lanczos3 window, so pic-scale computed a truncated filter with about half the taps of fast_image_resize. Commit 30b40e5 ('Filter generation fix', v0.6.12, 2025-10-16) doubled the kernel size (src/math/weights.rs) and deleted the Performance section in the same change. The benchmarked pic-scale rows also ran WorkloadStrategy::PreferSpeed (the default, documented as 'prefers speed to quality'). imazen/zenresize ships a paired_bench harness comparing pic-scale 0.7 with fast_image_resize 6 single-threaded but commits no cross-library results. Same author as libblur, sparkyuv, moxcms and yuvutils-rs.

Rust crate with C bindings (picscale/), JS, Python and WASM bindings; runtime-dispatched NEON, SSE4.1, AVX2, AVX-512 and AVX-VNNI; nightly compiler needed for f16, i8mm and AVX-512 paths; 30+ resampling filters and colour-space-aware scaling (Lab, Luv, Oklab, linear, sigmoidal). README table says several paths (planes, SVE, some AVX-512) are only partly SIMD.

## Maintenance

Actively maintained by one author (last commit and 0.7.12 release 2026-09-10, 803 commits, 0 open issues) and dual BSD-3-Clause/Apache-2.0, so copyable; it has only 41 stars, and its crates.io volume comes largely from dependents such as hayro. Treat any speed claim as unmeasured until someone publishes a like-for-like run.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** No valid speed number exists. The current README has none and speedtest/src/runner.rs commits no results. Older README revisions (up to v0.6.11, e.g. commit 927a4fa) had a Lanczos3 table against fast_image_resize, but it was measured on filter code that built Lanczos3 kernels at half the correct support, so pic-scale did about half the convolution work of the baseline. The table was deleted in the same commit that fixed this (30b40e5, v0.6.12), so it cannot support a tier above D.
- **Verifier notes:** Stays D. The record said there were no numbers, but older README revisions had a pic-scale vs fast_image_resize table. It was measured on a Lanczos3 kernel truncated to half width, a bug fixed in v0.6.12 by the same commit that deleted the table. Notable by usage (about 1.45 million crates.io downloads), so keep.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** none valid
- **Pages the verifier opened:**
  - <https://github.com/awxkee/pic-scale>
  - <https://github.com/awxkee/pic-scale/commits/master>
  - <https://github.com/awxkee/pic-scale/commits/master/README.md>
  - <https://github.com/awxkee/pic-scale/tree/master/speedtest>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/speedtest/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/speedtest/src/runner.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/speedtest/src/main.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/927a4fa/README.md>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/314c784/README.md>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/30b40e5/README.md>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/927a4fa/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/927a4fa/app/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/927a4fa/app/benches/resize_rgb/main.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/927a4fa/app/benches/resize_rgba/main.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/927a4fa/src/scaler.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/927a4fa/src/sampler.rs>
  - <https://github.com/awxkee/pic-scale/commit/30b40e5>
  - <https://github.com/awxkee/pic-scale/commit/30b40e5acfe9ab110bce4c51466a4e22a0cc89af.diff>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/30b40e5acfe9ab110bce4c51466a4e22a0cc89af/src/math/weights.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/30b40e5acfe9ab110bce4c51466a4e22a0cc89af/src/sampler.rs>
  - <https://crates.io/api/v1/crates/pic-scale>
  - <https://crates.io/api/v1/crates/pic-scale/reverse_dependencies>
  - <https://raw.githubusercontent.com/imazen/zenresize/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/zenresize/HEAD/benchmarks/README.md>
- **Sources the enricher read:**
  - <https://github.com/awxkee/pic-scale>
  - <https://github.com/awxkee/pic-scale/tree/master/src>
  - <https://github.com/awxkee/pic-scale/tree/master/src/plan>
  - <https://github.com/awxkee/pic-scale/tree/master/src/factory>
  - <https://github.com/awxkee/pic-scale/tree/master/src/neon>
  - <https://github.com/awxkee/pic-scale/tree/master/src/avx2>
  - <https://github.com/awxkee/pic-scale/commits/master>
  - <https://github.com/awxkee/pic-scale/commits/master/README.md>
  - <https://github.com/awxkee/pic-scale/commit/7440da0>
  - <https://github.com/awxkee/pic-scale/issues?q=is%3Aissue>
  - <https://github.com/awxkee/pic-scale/issues/161>
  - <https://github.com/awxkee/pic-scale/issues/156>
  - <https://github.com/awxkee/pic-scale/issues/150>
  - <https://github.com/awxkee/pic-scale/pull/157>
  - <https://github.com/awxkee/pic-scale/pull/164>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/7440da0/README.md>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/fdc2eca/README.md>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/42c9b42/README.md>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/speedtest/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/speedtest/src/runner.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/scaler.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/threading_policy.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/colors/mod.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/math/weights.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/sampler.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/filter_weights.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/support.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/handler_provider.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/convolution.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/factory/mod.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/factory/rgba_u8.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/factory/rgb_u8.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/plan/mod.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/plan/planner.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/plan/trampoline_filtering.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/plan/vertical_filtering.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/neon/rgba_u8_rdm.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/neon/rgba_u8_dot.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/avx2/rgba_u8.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/src/avx2/vertical_u8.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/picscale/include/picscale.h>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/picscale/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/picscale/src/lib.rs>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/app/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/pic-scale/HEAD/.github/workflows/build_push.yml>
  - <https://crates.io/api/v1/crates/pic-scale>
  - <https://crates.io/api/v1/crates/pic-scale/reverse_dependencies?per_page=50>
  - <https://raw.githubusercontent.com/imazen/zenresize/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/zenresize/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/imazen/zenresize/HEAD/Cargo.toml>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/awxkee/pic-scale`) · [data/wave10/enrich/raw/github_com_awxkee_pic_scale.json](../../../data/wave10/enrich/raw/github_com_awxkee_pic_scale.json) (enrichment confidence 0.8)

</details>
