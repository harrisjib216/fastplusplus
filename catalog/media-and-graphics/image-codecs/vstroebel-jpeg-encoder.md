# jpeg-encoder

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `(MIT OR Apache-2.0) AND IJG` · 🟢 active

> Pure-Rust baseline/progressive JPEG encoder with optional AVX2 DCT and color conversion; informally about 2x the image crate's encoder on x86.

| | |
|---|---|
| **Beats** | image crate JPEG encoder (informal); libjpeg-turbo and mozjpeg not compared |
| **Claimed result** | No numbers in the README or repo. Third-party issue #35 (2026-06-01): 'the fact that x86 is like twice as fast as image seems to indicate that something is wrong on arm'; on a Raspberry Pi 5 the image crate outperforms jpeg-encoder, and the std_simd branch was about 5% slower. |
| **Workload** | Informal user observation in issue #35 as part of the reporter's application, not a cargo bench: x86 versus the image crate encoder, and Raspberry Pi 5 (Cortex-A76) versus the image crate at higher qualities. |
| **Metric** | throughput |
| **Adoption** | 33 stars, 13 forks; crates.io 8,025,519 total downloads (1,404,009 recent) and 83 reverse dependencies, including zune-image, pdf-writer, kornia-io, dicom-transfer-syntax-registry, tiff-writer and makepad-studio |
| **Last commit** | 2026-07-27 |
| **Links** | [repository](https://github.com/vstroebel/jpeg-encoder) · [benchmark](https://github.com/vstroebel/jpeg-encoder/issues/35) |

## Verdict

No measured speedup exists: the only comparison is issue #35, where a user said that inside their own app the crate is 'like twice as fast as image' on an unnamed x86 CPU and slower than the image crate at higher qualities on a Raspberry Pi 5, with no harness, flags or figures. The repo's criterion benches compare its scalar and AVX2 paths only (PR #22 reported 0.1-4.5% end-to-end gains on Zen 4 from AVX2 color-conversion changes), so the D tier stands.

## Use it when

- You need a JPEG encoder in pure Rust (no C toolchain, no libjpeg-turbo/mozjpeg linking), including no_std + alloc targets.
- x86-64 servers or desktops with AVX2, where the 'simd' feature enables the AVX2 DCT and color conversion and the issue #35 reporter saw roughly twice the image crate's encode speed.
- Default build must contain no unsafe code: without 'simd' the crate is #![forbid(unsafe_code)].
- You need CMYK/YCCK output, ICC or EXIF embedding, restart markers or custom quantization tables, which the image crate's encoder does not all expose.
- Streaming encode of large baseline images: the interleaved path keeps only one MCU row of samples in memory.

## Skip it when

- ARM (Raspberry Pi 5, Apple silicon, Graviton) with the released crate: 0.7.1 has no NEON path at all, and issue #35 (open) reports it slower than the image crate's encoder at higher qualities on a Cortex-A76; the wide-based DCT is only on unreleased HEAD and does not cover color conversion.
- You want smallest files at a given quality: no trellis quantization, and progressive mode does only spectral selection (no successive approximation), so mozjpeg-rs, mozjpeg or zenjpeg/jpegli produce smaller output.
- You need a published speed claim to rely on: there is no benchmark against libjpeg-turbo, mozjpeg or the image crate anywhere in the repo; the only outside comparison is one informal issue comment with no figures.
- Images wider or taller than 65,535 pixels (width and height are u16), or input with 12-bit samples (extended JPEG is open request #32).
- Multi-core throughput on a single image: encoding is single-threaded with no rayon option, unlike zenjpeg's rayon-based parallel feature.

## How it is fast

The forward DCT is a Rust port of the libjpeg/mozjpeg jpeg_fdct_islow integer DCT (Loeffler-Ligtenberg-Moschytz, 12 multiplies, 13-bit fixed point), and with the 'simd' feature a port of libjpeg-turbo's jfdctint-avx2.asm plus an AVX2 RGB/BGR(A) to YCbCr converter, both chosen at run time with is_x86_feature_detected!("avx2"). Coefficient blocks are 32-byte aligned (PR #28) so loads vectorize, and the default interleaved baseline path streams one MCU row at a time instead of buffering the image. At HEAD only, an unreleased 'use_wide' feature (PR #25) computes the DCT with the portable wide crate (SSE2, NEON, WASM SIMD); its author reported about 50% faster DCT on SSE2 and about 20% slower than the hand-written AVX2 path.

## Compared with alternatives

Pick it over jpeg-rusturbo when you need progressive mode, 4:4:4/4:2:2 and other sampling factors, CMYK or no_std, since jpeg-rusturbo's measured 5x win over the image crate covers only its 4:2:0 path; pick mozjpeg-rs or zenjpeg instead when file size per quality matters more than encode speed, and libjpeg-turbo when a C dependency is acceptable and you need fast encoding on ARM too.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none by default; optional wide 1.0 + bytemuck 1.24 for the HEAD-only 'use_wide' feature; jpeg-decoder 0.3 as a dev-dependency for tests |
| **Minimum toolchain** | Rust 1.87 for crates.io 0.7.1 (edition 2024); Rust 1.89 at HEAD (0.8.0) |
| **Platforms** | any (scalar, no_std + alloc); AVX2 acceleration on x86/x86-64 with the 'simd' feature (runtime-detected, scalar fallback); wide-crate DCT for SSE2/NEON/WASM only on unreleased HEAD |
| **Thread safety** | not documented; Encoder consumes itself on encode, holds no global state and spawns no threads, so separate encoders can run on separate threads |
| **Drop-in for the baseline** | partial: different API from image's JpegEncoder (own Encoder/ColorType/ImageBuffer types), but takes the same raw 8-bit pixel slices; image's ImageBuffer types need a small adapter shown in the docs |

## Gotchas

- The 'simd' feature only accelerates x86 AVX2; on other CPUs, or x86 without AVX2, it silently runs the scalar code, and it switches off the forbid(unsafe_code) guarantee.
- use_wide (portable SIMD DCT for ARM64/WASM/SSE2) is merged on main but missing from crates.io 0.7.1, which was published from the commit just before PR #25 merged; the README does not document it either.
- Turning on optimized Huffman tables, progressive mode or a sampling factor that cannot be interleaved switches to a path that buffers every component plane plus every quantized 8x8 block (roughly 3 bytes of samples plus 6 bytes of coefficients per pixel for RGB) before writing anything.
- The repo's criterion/benches/fdct.rs was last changed in October 2024 and still passes a [i16; 64] to fdct(), which PR #28 changed to take the crate-private AlignedBlock; reading the source, that bench no longer compiles at HEAD (not built here). The encode and ycbcr benches only time jpeg-encoder against itself.
- The forward-DCT code is IJG-licensed: binary distributions must state they are based in part on the work of the Independent JPEG Group (LICENSE-IJG, added July 2026).

## Known shortcomings

- Tier D: the only comparison is issue #35's informal in-app test ('like twice as fast' as the image crate on x86, slower at higher qualities on a Raspberry Pi 5 A76) with no harness, CPU or flags; the criterion benches time only its own code; the simd feature is AVX2-only. Widely used (8.0M crates.io downloads, 83 reverse dependencies including zune-image and kornia-io).
- Enricher (e124, 2026-10-05): D stands, no numbers. crates.io 0.7.1 has no NEON; the wide-crate DCT for ARM, WASM and SSE2 (PR #25, feature flag use_wide, not in the README) exists only on the unreleased 0.8.0 HEAD (MSRV 1.89). Progressive mode does spectral selection only; width and height are capped at u16; the optimised-Huffman and progressive paths buffer the whole image. criterion/benches/fdct.rs has not been touched since 2024-10 and still passes [i16; 64] to fdct(&mut AlignedBlock), which has been crate-private since PR #28, so the bench no longer builds (code read, not built).

## Caveats and trade-offs

No benchmark against libjpeg-turbo, mozjpeg or the image crate is published. The criterion/ bench crate (benches encode, fdct, ycbcr) depends only on jpeg-encoder with its internal 'benchmark' feature and compares its own scalar and SIMD paths. The only outside comparison is issue #35, an informal observation inside the reporter's app (not a cargo bench): roughly 2x faster than the image crate on x86 (no CPU model, flags or numbers), slower than the image crate at higher qualities on a Raspberry Pi 5 (Cortex-A76), and the std_simd branch about 5% slower than main. The 'simd' feature is AVX2-only per the README, which explains the ARM gap. justin13888/image-evaluation includes it as a tested encoder, but its repo README carries no results (canonical run is on a website not reachable here). Low star count, but widely used as a dependency (8.0M crates.io downloads, 83 reverse dependencies).

Optional AVX2 path (simd feature) adds unsafe code; default build has no unsafe; no_std plus alloc supported; MSRV 1.89; baseline and progressive modes, optimized Huffman tables, restart intervals; IJG attribution clause applies to the forward-DCT code.

## Maintenance

Actively maintained (several PRs merged 2026-07-27, crates.io 0.7.1 the same day, 8.0M downloads and 83 reverse dependencies); dual MIT/Apache-2.0 plus IJG for the DCT, small, dependency-free and easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** Issue #35 (paul-fornage, 2026-06-01) is an informal in-app observation: 'x86 is like twice as fast as image' and the image crate is faster on a Raspberry Pi 5 at higher qualities, with no harness, no x86 CPU model, no flags and no measured figures; the repo's own criterion/ benches (encode, fdct, ycbcr) only time jpeg-encoder itself. Approximate words without a measurement are directional, so D.
- **Verifier notes:** Record accurate: issue #35 text, license (MIT OR Apache-2.0) AND IJG from Cargo.toml, and last commit 2026-07-27 all check out (HEAD Cargo.toml already says 0.8.0 while crates.io max is 0.7.1). Usage is far higher than the stars suggest, so the 'not notable' caveat was replaced. I could not check the 'vendored into rusty_jpeg' claim, so it is left as recorded.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** none
- **Pages the verifier opened:**
  - <https://github.com/vstroebel/jpeg-encoder/issues/35>
  - <https://github.com/vstroebel/jpeg-encoder>
  - <https://github.com/vstroebel/jpeg-encoder/commits>
  - <https://github.com/vstroebel/jpeg-encoder/commits/main.atom>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/README.md>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/criterion/Cargo.toml>
  - <https://crates.io/api/v1/crates/jpeg-encoder>
  - <https://crates.io/api/v1/crates/jpeg-encoder/reverse_dependencies?per_page=20>
  - <https://raw.githubusercontent.com/justin13888/image-evaluation/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/vstroebel/jpeg-encoder>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/README.md>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/src/encoder.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/src/fdct.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/src/writer.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/src/image_buffer.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/src/huffman.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/src/quantization.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/src/avx2.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/src/avx2/fdct.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/src/avx2/ycbcr.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/criterion/Cargo.toml>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/criterion/benches/encode.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/criterion/benches/fdct.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/criterion/benches/ycbcr.rs>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/.github/workflows/rust.yml>
  - <https://github.com/vstroebel/jpeg-encoder/issues?q=is%3Aissue>
  - <https://github.com/vstroebel/jpeg-encoder/pulls?q=is%3Apr>
  - <https://github.com/vstroebel/jpeg-encoder/issues/35>
  - <https://github.com/vstroebel/jpeg-encoder/issues/16>
  - <https://github.com/vstroebel/jpeg-encoder/pull/22>
  - <https://github.com/vstroebel/jpeg-encoder/pull/24>
  - <https://github.com/vstroebel/jpeg-encoder/pull/25>
  - <https://github.com/vstroebel/jpeg-encoder/pull/28>
  - <https://github.com/vstroebel/jpeg-encoder/commits/main>
  - <https://github.com/vstroebel/jpeg-encoder/commits/main/criterion/benches/fdct.rs>
  - <https://crates.io/api/v1/crates/jpeg-encoder>
  - <https://crates.io/api/v1/crates/jpegli-rs>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/mozjpeg-rs/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/vstroebel/jpeg-encoder`) · [data/wave10/enrich/raw/github_com_vstroebel_jpeg_encoder.json](../../../data/wave10/enrich/raw/github_com_vstroebel_jpeg_encoder.json) (enrichment confidence 0.8)

</details>
