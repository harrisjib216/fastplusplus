# jpeg-rusturbo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure-Rust SIMD JPEG encoder and decoder with libjpeg-turbo-derived kernels; encodes about 5x faster than the image crate's encoder.

| | |
|---|---|
| **Beats** | Rust image crate 0.25: its own built-in scalar JPEG encoder (4:2:0 only) and its zune-jpeg-backed decoder. libjpeg-turbo is never measured. |
| **Claimed result** | Encode 4:2:0 4K single thread: Apple M-series 13.41 ms vs 67.61 ms for image (5.04x); Intel Xeon Platinum 8272CL 57.27 ms vs 320.93 ms (5.60x). Encode with threads=auto 4K: 6.83 ms vs 68.47 ms (10.02x) on Apple M, 46.77 ms vs 320.95 ms (6.86x) on Xeon. Decode 4K natural-like: 5.93 ms vs 7.00 ms (1.18x) Apple M, 28.01 ms vs 34.26 ms (1.22x) Xeon; decode at 1592x1124 on Xeon is parity or slightly slower (0.97x to 0.98x). |
| **Workload** | benches/vs_image.rs. Encode: 3-byte RGB of the synthetic XOR full-AC pattern only, q=80, at 1592x1124, 1080p and 4K, with threads=1 and threads=auto on jpeg-rusturbo's side; image is single-threaded and 4:2:0-only, so only the 4:2:0 rows compare like with like. Decode: jpeg-rusturbo's own q=80 4:2:0 output, decoded to RGB, on the synthetic and natural-like generated images. Each figure is the mean of one batch of 50 iterations after 3 warm-ups. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8272CL @ 2.60 GHz, 4 vCPU (AVX2); Apple Silicon M-series developer laptop, 8 cores (exact model not stated), NEON. |
| **Compiler and flags** | cargo bench --bench vs_image with release profile lto = "fat", codegen-units = 1; SIMD build with runtime-dispatched AVX2 / NEON kernels. rustc version not stated (crate MSRV 1.85, edition 2024, no pinned toolchain file). |
| **Adoption** | 0 stars; crates.io jpeg-rusturbo 0.9.2, 7,763 downloads in total (7,617 of them on 0.9.2) |
| **Last commit** | 2026-06-08 |
| **Links** | [repository](https://github.com/naoto256/jpeg-rusturbo) · [benchmark](https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/BENCH.md) |

## Verdict

The first-party harness benches/vs_image.rs (release profile with fat LTO and codegen-units=1, unstated rustc, mean of one 50-iteration batch) encodes a synthetic 4K RGB pattern at q=80 4:2:0 in 13.41 ms against 67.61 ms for the image 0.25 crate's own scalar encoder on an unnamed Apple M-series laptop (5.04x), and 57.27 against 320.93 ms on a 4-vCPU Xeon Platinum 8272CL (5.60x); threads=auto raises that to 10.02x and 6.86x against single-threaded image. Decoding its own q=80 output, it runs 0.97x to 1.22x of image's zune-jpeg path, and libjpeg-turbo is never measured.

## Use it when

- Rust services that encode many JPEGs and currently use the image crate's encoder: about 5x (Apple M) to 5.6x (Xeon 8272CL) faster single-threaded at 4:2:0 q=80, and more with threads on many-core hosts.
- You need encoder features image's encoder lacks: 4:4:4/4:2:2, progressive output, optimized Huffman (about 5% smaller), restart markers, EXIF/ICC pass-through, CMYK.
- You want a pure-Rust build with no C toolchain or nasm on x86_64 (AVX2) or aarch64 (NEON); CI covers Linux, macOS, Windows x64 and Windows on Arm, with a bit-exact scalar fallback elsewhere.
- Decode, operate and re-encode pipelines that must preserve EXIF and ICC on both sides.

## Skip it when

- You can link C: libjpeg-turbo (catalogued, whose kernels these are) or the libjpeg-turbo-rs and zenjpeg ports were benchmarked against libjpeg-turbo itself, while this crate never was. Its speed relative to libjpeg-turbo is unknown.
- Decode-heavy workloads: the decoder is at parity with image's zune-jpeg backend (0.97x to 1.22x), and the 4K lead is partly harness overhead (see gotchas). Use zune-jpeg or libjpeg-turbo for decode speed.
- You need arithmetic-coded, lossless, hierarchical or 12-bit JPEG, CMYK-to-RGB conversion, or progressive grayscale/CMYK encode: all return Unsupported.
- Many-core scaling on small VMs: on the 4-vCPU Xeon, threads=auto adds only 1.06x at 1080p and 1.22x at 4K over one thread.
- Smallest files at a given quality: there is no trellis quantization (mozjpeg-rs and mozjpeg do that), and no output-size or quality comparison against any other encoder is published.

## How it is fast

The encoder front end (RGB to YCbCr, 4:2:0/4:2:2 downsample, integer LL&M forward DCT, reciprocal-multiply quantize) is a translation of libjpeg-turbo's NEON and AVX2 kernels, selected at compile time on aarch64 and by runtime AVX2 detection on x86_64. The Huffman AC emit walks a SIMD-built 64-bit nonzero bitmap with trailing_zeros jumps, and set_threads splits quantize and bitmap work across MCU rows on rayon. Its profile puts about 65% of single-thread encode in the scalar Huffman emitter, so further front-end SIMD buys little. The decoder ports libjpeg-turbo's jidctint IDCT (with DC-only and sparse-row fast paths), fancy upsample and YCC-to-RGB, and adds a SWAR bit-reader refill.

## Compared with alternatives

Pick it over libjpeg-turbo when you must stay pure Rust with no C or nasm in the build and encode is the bottleneck. Pick it over mozjpeg-rs when encode speed matters more than the last few percent of file size. libjpeg-turbo-rs and zenjpeg are the Rust alternatives with published numbers against libjpeg-turbo itself, so prefer them when you need that assurance.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rayon (image and minifb are dev-dependencies only) |
| **Minimum toolchain** | Rust 1.85 (edition 2024) |
| **Platforms** | x86_64 (AVX2 runtime-detected, SSE2 baseline, scalar fallback), aarch64 (NEON), any other target via the scalar path; CI on ubuntu-latest, macos-14, windows-latest, windows-11-arm |
| **Thread safety** | Encoder and Decoder are per-call values with no documented global state. set_threads(0) runs on the caller's ambient rayon pool, and set_threads(n&gt;1) builds a fresh rayon ThreadPool inside every encode call. |
| **Drop-in for the baseline** | partial — the encoder's constructor and encode_rgb/encode_rgba methods mirror image's JpegEncoder, but it does not implement image::ImageEncoder or accept DynamicImage, and the decoder has its own API |

## Gotchas

- The decode comparison is not like for like: benches/vs_image.rs times image's ImageReader::decode().to_rgb8(), which converts into a second full-frame buffer (about 24.9 MB at 4K RGB), while jpeg-rusturbo decodes straight into an uninitialised output Vec. The 1.18-1.22x 4K natural-content lead may be mostly that copy. Encode was compared only on a synthetic XOR full-AC pattern, with one 50-iteration mean, no Cargo.lock (image 0.25.x and zune-jpeg versions unrecorded) and no size or quality check.
- decode/mod.rs compose_output calls Vec::set_len on uninitialised u8 memory (clippy::uninit_vec allowed) to skip zero-fill. This rests on every byte being written before it is read, and the code comment's claim that u8 makes it sound contradicts set_len's documented precondition. CI runs no Miri or fuzzing, so treat the decoder as unhardened for untrusted input.
- set_threads(n) for n&gt;1 spawns a new thread pool per encode, which hurts small images. Benchmarks used threads=auto (0), which reuses the global pool.
- Before 0.9.1 the encoder returned Ok with a corrupt JPEG for dimensions above 65535 and accepted zero quant-table entries; pin 0.9.1 or later.

## Known shortcomings

- No number against libjpeg-turbo anywhere; the baseline is the image crate's own scalar JPEG encoder (not jpeg-encoder) and zune-jpeg. Encode is compared on a synthetic XOR pattern only and the decode baseline pays an extra to_rgb8 copy; rustc version unstated. Kernels are translated from libjpeg-turbo (NOTICE.md), so it is a partial port (libjpeg-turbo-rs precedent kept).
- Decode flaw: the image-crate side times decode().to_rgb8() (an extra copy of about 24.9 MB at 4K) while jpeg-rusturbo writes into an uninitialised Vec, so the 1.18-1.22x 4K lead may be mostly that copy; encode against image uses an XOR pattern only with no size or quality check and no Cargo.lock (image and zune-jpeg versions unrecorded). decode/mod.rs uses Vec::set_len on uninitialised u8 (clippy::uninit_vec allowed) with no Miri or fuzzing in CI; set_threads(n) above 1 builds a new rayon pool per encode; before 0.9.1 the encoder returned Ok with a corrupt JPEG above 65535 px.

## Caveats and trade-offs

There is no comparison with libjpeg-turbo or mozjpeg anywhere. The baseline is the image crate, whose built-in encoder is scalar and 4:2:0-only; the vs_image.rs header names image's own encoder, not the jpeg-encoder crate. The 5x single-thread and 6.9x to 10x threads=auto encode wins therefore say nothing about libjpeg-turbo. The threads=auto rows also set a rayon-parallel encoder against a single-threaded one. Per NOTICE.md, the encoder's four hot kernels (colour conversion, 4:2:0 downsample, integer forward DCT, quantize) are translated from libjpeg-turbo's NEON/AVX2 SIMD code, and so are the decoder's IDCT, fancy upsample and YCC-to-RGB kernels. In part, then, this is a Rust port of libjpeg-turbo (catalogued). The encode comparison uses only the synthetic XOR full-AC pattern, both sides at q=80, with no output size or quality comparison between the two encoders. In the decode comparison the image side calls ImageReader::decode().to_rgb8(). That adds a full-frame conversion copy (about 24.9 MB at 4K) that jpeg-rusturbo's side does not pay, so part of the 1.18x to 1.22x lead at 4K may be harness overhead. Otherwise decode is at parity with zune-jpeg and slightly slower at 1592x1124 on the Xeon (0.97x to 0.98x); the decode numbers come from an older campaign. Inputs are generated images, not a photo corpus. The Apple host had light background load. Rust (language-filter mismatch).

Rust crate with unsafe SIMD kernels (AVX2 and NEON only, AVX-512 and SVE explicitly not planned). Encoder handles baseline and progressive, RGB/gray/CMYK, EXIF/ICC pass-through; decoder handles baseline and progressive Huffman. Optional rayon threading.

## Maintenance

Single-author pre-1.0 crate (0.9.2, 197 commits, last commit 2026-06-08, 0 stars, about 7.8k crates.io downloads) under MIT OR Apache-2.0, with libjpeg-turbo's BSD-3 notice kept in NOTICE.md for the translated kernels.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party harness: benches/vs_image.rs and BENCH.md, with release profile lto=fat, codegen-units=1 and a named Xeon Platinum 8272CL. The rustc version is not stated (only MSRV 1.85), the Apple M-series model is not named, and timing is one batch of 50 iterations (mean) with no statistics.
- **Verifier notes:** All claimed numbers match BENCH.md and the README; no libjpeg-turbo number exists. Corrected the baseline label: the encoder is image's own, not jpeg-encoder. The kernels are translated from libjpeg-turbo, so the orchestrator may treat this as a partial port of the listed libjpeg-turbo; the precedent libjpeg-turbo-rs was kept. Metadata checked: MIT OR Apache-2.0, last commit 2026-06-08, 0 stars, not a fork.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/BENCH.md>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/README.md>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/benches/vs_image.rs>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/NOTICE.md>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/jpeg-rusturbo>
  - <https://github.com/naoto256/jpeg-rusturbo>
  - <https://github.com/naoto256/jpeg-rusturbo/commits>
- **Sources the enricher read:**
  - <https://github.com/naoto256/jpeg-rusturbo>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/README.md>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/BENCH.md>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/benches/vs_image.rs>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/NOTICE.md>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/src/decode/mod.rs>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/src/encode/mod.rs>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/docs/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/naoto256/jpeg-rusturbo/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/vstroebel/jpeg-encoder/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/naoto256/jpeg-rusturbo`) · [data/wave10/enrich/raw/github_com_naoto256_jpeg_rusturbo.json](../../../data/wave10/enrich/raw/github_com_naoto256_jpeg_rusturbo.json) (enrichment confidence 0.75)

</details>
