# yuvutils-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Color conversion and resampling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause OR Apache-2.0` · 🟢 active

> Pure-Rust SIMD YUV/RGB conversion crate (yuv) that matches or beats libyuv by 1.1-2x on NEON and Linux x86.

| | |
|---|---|
| **Beats** | libyuv built from source by the yuv-sys 0.3.x crate (livekit/rust-sdks, required as 0.3.7 in app/Cargo.toml); libyuv commit not stated |
| **Claimed result** | Valid like-for-like rows (README, derived from page data; libyuv 1886 via yuv-sys 0.3.7, tables from Nov 2024 to Jan 2025): NV12 to RGBA 377.59 vs 621.11 us on NEON (1.64x), 917.52 vs 979.96 us on AVX2 (1.07x), 736.21 vs 800.85 us on AVX-512 (1.09x); YUV 4:2:0 to RGB 346.13 vs 675.72 us NEON (1.95x), 923.83 us vs 1.42 ms AVX2 (1.54x), 614.19 us vs 1.16 ms AVX-512 (1.89x); YUV 4:2:0 to RGBA 396.58 vs 710.88 us NEON (1.79x), 942.92 us vs 1.03 ms AVX2 (1.09x), 733.88 vs 870.64 us AVX-512 (1.19x). The RGB to YUV 4:2:0 encode rows (1.13-1.35x) come from benches commented out at HEAD; the Windows column and the NEON 10-bit rows compare SIMD against libyuv C fallbacks and are not valid. |
| **Workload** | 8-bit RGB/RGBA to YUV 4:2:0/4:2:2/4:4:4 and YUV to RGB/RGBA on a 1997x1331 image, plus 10-bit and rotation benchmarks, criterion timings. |
| **Metric** | latency |
| **Hardware** | README: 'Mac Pro M3' (aarch64, NEON); AWS m4.large with Ubuntu 24.04 (AVX2, CPU model not stated); Windows 11 Intel Core i9-14900HX (AVX2); AWS c5.large with Ubuntu 24.04 (AVX-512, CPU model not stated); 1997x1331 test image (assets/bench.jpg) |
| **Compiler and flags** | cargo bench --bench yuv8 --manifest-path ./app/Cargo.toml --features fast_mode,professional_mode,rdm (AVX-512: cargo +nightly bench ... --features nightly_avx512,fast_mode,professional_mode); criterion 0.6, sample size 500, 7 s measurement time; Rust toolchain version not stated (app/Cargo.toml also enables the yuv crate's nightly_i8mm and nightly_f16 features); libyuv compiled by the yuv-sys build script through the cc crate, flags not stated |
| **Adoption** | 126 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/awxkee/yuvutils-rs) · [benchmark](https://github.com/awxkee/yuvutils-rs/blob/master/README.md) |

## Verdict

These are first-party Criterion runs (500 samples, 7 s) on one 1997x1331 JPEG against libyuv built by the yuv-sys crate's cc build (0.3.7 vendors libyuv 1886). On an M3 (NEON), 8-bit decode to RGB/RGBA is 1.64-1.95x libyuv and RGB to 4:2:0 encode is 1.20x. On Linux AVX2 (m4.large) and AVX-512 (c5.large), CPU models unstated, the lead is 1.07-1.89x and libyuv wins several rows. The Windows i9-14900HX column and the NEON 10-bit rows are not fair comparisons: libyuv there runs C or SSSE3 row code, as the measurement notes explain.

## Use it when

- Rust code (AVIF/HEIF/video pipelines) that wants libyuv-class speed without linking C. It is a pure crate with no build script, and at 4.27M downloads it is widely used.
- 8-bit YUV 4:2:0/4:2:2/NV12 to RGB/RGBA on Apple silicon or other aarch64, where the README shows 1.6-1.95x over libyuv's NEON rows.
- 10/12/14/16-bit formats (I010/I210/I410, P010/P210/P016) to 16-bit or F16/AR30 RGB, which libyuv covers only partly.
- Sharp YUV encoding, YCgCo-R, or a choice between libyuv-equivalent and higher-precision encoding.

## Skip it when

- C++ projects that cannot add a Rust FFI layer: the crate has no C header or C ABI.
- x86 workloads dominated by 4:4:4 or 4:0:0 decode, or by RGBA to 4:2:0/4:2:2 encode on AVX-512: libyuv wins or ties several of these rows in the README.
- Pipelines that need bit-identical output across platforms: issue #144 (open, 2 Oct 2026) reports the AVX2/SSE kernels differing from the scalar path by up to 2 levels on 29-35% of samples, so wasm and x86 builds decode the same AVIF differently.
- When you must reproduce the published numbers exactly: the tables are from Nov 2024 to Jan 2025 (git blame), the crate has since moved to 0.8.19, and the harness no longer runs some rows.

## How it is fast

Each format has hand-written row kernels for NEON (with RDM vqrdmulh and optional i8mm), SSE4.1, AVX2, AVX-512BW/VBMI (nightly) and WASM simd128. x86 picks a kernel at runtime with is_x86_feature_detected; aarch64 checks for RDM at runtime. Planar decoding runs 13-bit fixed-point arithmetic with rounding shifts, which is more precise than libyuv's 6-bit coefficients, and 4:2:0/4:2:2 decoding uses dedicated 422 kernels that reuse each chroma sample for two pixels. Encoding offers a libyuv-precision Fast mode, a default higher-precision Balanced mode and a Professional mode.

## Compared with alternatives

Pick it over sparkyuv (same author's archived C++ predecessor) for anything new: it is maintained, has more formats and has a precision knob. Pick xxYUV or libyuv itself when you need a C/C++ library without a Rust toolchain or FFI glue.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | num-traits; optional rayon (feature rayon) and fast_transpose (feature geometry). The benchmarks also use yuv-sys (libyuv built from source), image and criterion. |
| **Minimum toolchain** | Rust 1.82 (rust-version). The nightly_avx512, nightly_i8mm and nightly_f16 features need a nightly compiler, and the repo's rust-toolchain.toml selects an undated nightly. |
| **Platforms** | x86/x86-64 (SSE4.1, AVX2, AVX-512BW/VBMI with nightly; runtime dispatch), aarch64 NEON (RDM runtime-detected, i8mm opt-in), wasm32 with simd128 enabled at compile time; scalar fallback elsewhere. Big-endian YUV via the big_endian feature. |
| **Thread safety** | Not documented. The functions are stateless and work on caller-provided slices; the rayon feature splits work across threads internally. |
| **Drop-in for the baseline** | partial: the formats and BT.601/709 matrices match libyuv, but the API is Rust structs plus enums rather than libyuv's C functions, and Balanced/Professional output differs numerically from libyuv. |

## Gotchas

- The x86 SIMD kernels have shipped wrong output before. #92 (yuyv422_to_yuv420 broken with SSE/AVX), #97 (AVX rgba_to_yuv400 black vertical lines) and #130 (SSE 16-bit bilinear wrong chroma, i414 panics) are all fixed. The fuzz crate builds yuv with default-features = false and without sse/avx/rdm, so those kernels are not fuzzed by default; the fuzzers check only for panics and the alpha value, not against a reference.
- The default YuvConversionMode is Balanced, not libyuv-equivalent. Fast (libyuv precision) and Professional exist only when the fast_mode/professional_mode features are enabled.
- AVX-512 needs both the nightly_avx512 feature and a nightly compiler. Without them, x86 tops out at AVX2 even on AVX-512 hardware.
- Unit tests check round trips within a per-mode tolerance (for example max_diff of 3 levels); nothing in the repo compares output with libyuv.

## Known shortcomings

- Rust (language-filter mismatch). Downgraded to C: the headline NV12 2.3x is not like-for-like (the libyuv row rs_NV21ToABGR writes 4 bytes per pixel against 3-byte RGB); like-for-like rows are 1.07-1.64x on NV12 and 1.1-2x elsewhere (derived), libyuv wins several x86 rows, and the Windows libyuv build was likely a partial-SIMD build. Issue #144 open.
- README tables (Nov 2024 to Jan 2025, yuv-sys 0.3.7 = libyuv 1886): the Windows column is invalid because cc builds libyuv with cl.exe and libyuv 1886 on x64 MSVC has SSSE3 rows only for I422/I444ToARGB (everything else C); the NEON 10-bit 2x is SIMD against C (no I210ToARGBRow_NEON in 1886); the RGB to YUV 4:2:0 benches behind the 1.20x encode headline are commented out at HEAD (app/benches/yuv8/main.rs lines 128-344). No output comparison against libyuv; open #144 (SIMD versus scalar off by 2); fuzz crate skips sse and avx paths; undated nightly toolchain. Valid wins: 8-bit NEON and Linux x86 rows at 1.07-1.95x. Retier-02 corrects the record.

## Caveats and trade-offs

libyuv wins several rows: YUV 4:0:0 to RGBA on AVX2 (635.61 vs 651.88 us) and AVX-512 (525.56 vs 600.43 us), YUV 4:4:4 to RGBA on AVX2 (963.66 us vs 1.10 ms) and AVX-512 (803.62 vs 819.17 us), YUV 4:2:2 to RGBA on AVX2 (1.04 vs 1.10 ms), RGBA to YUV 4:2:0 and 4:2:2 on AVX-512, and 10-bit to RGBA8 on AVX2. The Windows AVX2 column has libyuv at 2.70-6.86 ms on the encode, RGB24-output and 10-bit rows but 525.90-579.24 us on 4:2:0, 4:2:2 and 4:4:4 to RGBA, consistent with a libyuv build (likely MSVC) missing some SIMD row paths (inference, not stated), so the 7-16x gaps on those rows should be ignored. The README rows do not say which YuvConversionMode (Fast, Balanced, Professional) was timed; Fast is documented as libyuv-level precision, Balanced as more precise and about 30% slower. The libyuv 4:2:2 encode row uses ABGRToJ422 (full range) against yuvutils limited range. SIMD and scalar yuvutils paths disagree by up to 2 levels on x86 (issue #144, open, opened 2026-10-02); bit-exactness against libyuv was not shown either way. [retier] Windows column invalid (cl.exe-built libyuv 1886 has SSSE3 only for I422/I444ToARGB; other rows run C); NEON 10-bit 2x is SIMD against C. No output comparison against libyuv; open issue #144 (SIMD and scalar paths differ by 2); the fuzz crate skips the sse and avx paths; toolchain is an undated nightly. libyuv wins several AVX2 and AVX-512 rows (4:0:0, 4:4:4 and 4:2:2 to RGBA; RGBA to YUV 4:2:0 and 4:2:2 on AVX-512; 10-bit to RGBA8 on AVX2).

Pure Rust YUV conversion with approximate (fast_mode) and exact (professional_mode) paths; 8 to 16-bit depths; no C API stated, so not callable from C++ without a shim.

## Maintenance

Actively maintained (last commit 17 Sep 2026, 1,062 commits, 126 stars, 21 forks; crate yuv 0.8.19 with 4.27M downloads), dual BSD-3-Clause OR Apache-2.0, so it is copyable, but only from Rust or through an FFI shim you write.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party criterion tables in README.md with public harness (app/benches/yuv8/main.rs, app/Cargo.toml) and bench commands, but no Rust toolchain version, no libyuv commit, and CPU models only for the M3 and i9-14900HX columns (m4.large and c5.large CPUs unstated), so not A; no independent measurement, so not B. Tier stays C; verdict is downgrade because the headline 2.3x NV12 ratio is not like-for-like.
- **Verifier notes:** Rust crate (yuv on crates.io, 4.27M downloads), language-filter mismatch for a C++-first catalog; language field Rust is already right. Every number in the record is in README.md, but the NV12 headline compares 3-byte RGB output with libyuv's 4-byte ABGR (NV21) call, so the real lead is 1.1-1.6x on NV12 and 1.1-2x elsewhere, with libyuv ahead on several x86 rows. Metadata checked on github.com: BSD-3-Clause OR Apache-2.0, 126 stars, not archived or a fork, last commit 2026-09-17 (active).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/awxkee/yuvutils-rs>
  - <https://github.com/awxkee/yuvutils-rs/commits/master>
  - <https://github.com/awxkee/yuvutils-rs/issues/144>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/app/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/app/benches/yuv8/main.rs>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/src/yuv_support.rs>
  - <https://crates.io/api/v1/crates/yuv-sys>
  - <https://crates.io/api/v1/crates/yuv>
  - <https://raw.githubusercontent.com/livekit/rust-sdks/main/yuv-sys/build.rs>
- **Sources the enricher read:**
  - <https://github.com/awxkee/yuvutils-rs>
  - <https://github.com/awxkee/yuvutils-rs/tree/master/src>
  - <https://github.com/awxkee/yuvutils-rs/tree/master/fuzz>
  - <https://github.com/awxkee/yuvutils-rs/issues?q=is%3Aissue>
  - <https://github.com/awxkee/yuvutils-rs/issues/144>
  - <https://github.com/awxkee/yuvutils-rs/commits/master/README.md>
  - <https://github.com/awxkee/yuvutils-rs/blame/master/README.md>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/app/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/app/Cargo.lock>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/app/benches/yuv8/main.rs>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/app/benches/yuv16/main.rs>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/src/yuv_to_rgba.rs>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/src/rgba_to_yuv.rs>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/src/yuv_support.rs>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/src/images.rs>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/fuzz/Cargo.toml>
  - <https://raw.githubusercontent.com/awxkee/yuvutils-rs/HEAD/fuzz/yuv_to_rgb/yuv_to_rgb.rs>
  - <https://raw.githubusercontent.com/livekit/rust-sdks/main/yuv-sys/build.rs>
  - <https://raw.githubusercontent.com/livekit/rust-sdks/main/yuv-sys/Cargo.toml>
  - <https://crates.io/api/v1/crates/yuv-sys/versions>
  - <https://crates.io/api/v1/crates/yuv>
  - <https://crates.io/api/v1/crates/yuv-sys/0.3.7/download>
  - <https://raw.githubusercontent.com/lemenkov/libyuv/HEAD/include/libyuv/row.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/awxkee/yuvutils-rs`) · [data/wave10/enrich/raw/github_com_awxkee_yuvutils_rs.json](../../../data/wave10/enrich/raw/github_com_awxkee_yuvutils_rs.json) (enrichment confidence 0.8)

</details>
