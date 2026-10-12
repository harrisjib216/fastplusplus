# zenjpeg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `AGPL-3.0 or commercial (dual-licensed)` · 🟢 active

> Safe pure-Rust JPEG encoder/decoder; progressive decode 1.35x libjpeg-turbo, baseline about 6% slower single-threaded.

| | |
|---|---|
| **Beats** | libjpeg-turbo (mozjpeg-sys 2.2 with nasm_simd, C+NASM) |
| **Claimed result** | README (Ryzen 9 7950X, single-threaded, 10 CID22 512x512 photos at Q85 4:2:0): baseline decode 73.8 MiB/s with default Triangle upsampling vs libjpeg-turbo/mozjpeg 78.1 MiB/s (0.94x, slower); 80.4 MiB/s with NearestNeighbor (box) upsampling (1.03x, but that skips the fancy upsampling C performs); progressive decode 46 vs 34 MiB/s (1.35x faster), the one single-thread like-for-like win. Parallel decode with DRI (rayon, --features parallel) vs single-threaded libjpeg-turbo: 1.56 vs 3.86 ms at 1024, 3.05 vs 15.8 ms at 2048, 8.74 vs 65.3 ms at 4096 (about 2.5x, 5.2x, 7.5x, derived from page data); this compares a multi-core decode with a single-thread one. The same synthetic set run single-threaded (CLAUDE.md, 2026-02-15, commit 39f012f) gives 3.66 vs 3.86, 14.8 vs 15.8, 61.9 vs 65.3 ms (about 1.05 to 1.07x faster, derived from page data), and progressive 0.60 to 0.69x of mozjpeg's time on synthetic images. |
| **Workload** | JPEG decode to RGB of 10 CID22-512 training photos (512x512) re-encoded by mozjpeg-rs at Q85 4:2:0, baseline and progressive, timed in interleaved zenbench A/B runs (zenjpeg/benches/decode_zenbench.rs). The parallel-decode table uses synthetic noise+patches images with restart markers at 1024, 2048 and 4096 px (CLAUDE.md Parallel Decode, 2026-02-15). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X (WSL2) |
| **Compiler and flags** | cargo bench --release, default target (no -C target-cpu=native), runtime SIMD dispatch via archmage; rust-toolchain.toml pins channel 'stable' only and the rustc version is not recorded; C reference is mozjpeg-sys 2.2 with nasm_simd, built by its build script with unstated C compiler and flags |
| **Adoption** | 15 stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/imazen/zenjpeg) · [benchmark](https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/README.md) |

## Verdict

First-party zenbench runs on a Ryzen 9 7950X under WSL2, cargo bench with the release profile (debug=true, no LTO, default target, runtime SIMD dispatch, rustc version unrecorded), against mozjpeg v4's libjpeg-turbo-derived decoder through mozjpeg-sys 2.2 with nasm_simd (C built by cc-rs at the Cargo profile's opt level with no -march; C compiler version unrecorded), read one scanline per call with default ISLOW IDCT and fancy upsampling, on 10 CID22 512x512 photos re-encoded by mozjpeg-rs at Q85 4:2:0: baseline 73.8 vs 78.1 MiB/s (0.94x) with defaults, 80.4 MiB/s with box upsampling, progressive 46 vs 34 MiB/s (1.35x); no committed result file or commit hash backs these CID22 figures. The 2.5x to 7.5x parallel figures (Feb 2026 synthetic set, commit 39f012f) compare multi-threaded zenjpeg with single-threaded libjpeg-turbo; single-threaded on the same set zenjpeg was only 1.05x to 1.07x faster.

## Use it when

- Rust services that decode many progressive JPEGs (mozjpeg-style web images): 46 vs 34 MiB/s single-threaded on CID22 512x512 Q85 4:2:0, and 0.60x to 0.69x of mozjpeg's time on the Feb 2026 synthetic 256 to 4096 px set.
- Latency-bound decode of large baseline JPEGs that carry restart markers (DRI) on a multi-core box, with the parallel feature: 3.05 ms vs 15.8 ms single-threaded libjpeg-turbo at 2048x2048 (multi-thread vs one thread).
- Untrusted-input pipelines that want a memory-safe decoder with max_pixels/max_memory caps, cooperative cancellation and Strict to Permissive error policies.
- Bounded-memory decode of very large images through the scanline reader (the wave-parallel path caps its buffer at 6 MB at 4096x4096).
- Pure-Rust jpegli-quality encoding where a C++ toolchain is unwanted; the project's own note puts the encoder about 15 to 20% slower than C++ jpegli at matched quality.

## Skip it when

- C or C++ projects: there is no C API, so you would write and maintain an extern "C" shim, and the code is AGPL-3.0-only unless you buy Imazen's commercial licence.
- Throughput servers that already decode one image per core: single-thread baseline decode is 0.94x of libjpeg-turbo with the default upsampling, and the parallel speedups need restart markers that most camera and web JPEGs lack.
- When output must be pixel-identical to libjpeg-turbo: the default IDCT differs and the default Triangle upsampling is only within max_diff 3; the pixel-exact Libjpeg IDCT is documented as adding about 37% overhead, which would put baseline decode well behind C (not measured in the README).
- BGRA or RGBA output at large sizes until re-measured: the repo's BENCH-AUDIT.md found the streaming path emits RGB and then swizzles, measuring 4096x4096 single-thread Bgra 47% slower than Rgb and the imageflow BGRA bench 9 to 19% behind mozjpeg's JCS_EXT_BGRA (later sink-path work added a garb swizzle).
- Code that needs a stable API: the crate is 0.x (0.9.0 in the repo while the README still says 0.8) and the README calls the decoder API prerelease with breaking changes expected.

## How it is fast

Baseline JPEGs go through a streaming single-pass decoder: Huffman decode, IDCT, chroma upsampling and YCbCr-to-RGB run per MCU row with no coefficient buffer, using fused AVX2 upsample+color-convert kernels, partial dequantization driven by the coefficient count, and a DC-only fast path. Progressive decode, the one clear single-thread win, comes from fused per-scan AC loops with a combined 9-bit Huffman+value lookup and a u64 nonzero-coefficient bitmap per block walked with trailing_zeros during AC refinement (callgrind: 415M vs 580M instructions for zune-jpeg at 2048x2048). The default IDCT is a jpegli-style integer IDCT rather than libjpeg's ISLOW, SIMD is dispatched at runtime through archmage tokens (AVX2/FMA, AVX-512, NEON, SIMD128), and with --features parallel images carrying restart markers are split by restart segment across a rayon pool.

## Compared with alternatives

Pick zenjpeg over libjpeg-turbo-rs (pure-Rust libjpeg-turbo port claiming 0.77x to 0.93x of libjpeg-turbo 3.1.2's baseline decode time) when progressive decode, jpegli-class encoding, bounded-memory streaming or safety limits matter more than baseline libjpeg-compatible speed; pick jpeg-nitro (C) or plain libjpeg-turbo for C++ code, and mozjpeg-rs (same author) if you only need a mozjpeg-compatible encoder.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | Pure-Rust crates only (archmage, magetypes, garb, zenyuv, zenpixels, zencodec, zenanalyze, enough, memchr, aligned-vec, bytemuck, imgref, rgb, tinyvec, thiserror, whereat, linear-srgb); optional rayon (parallel), moxcms (color management), ultrahdr crates; no C dependencies |
| **Minimum toolchain** | Rust 1.93 (MSRV, edition 2024); rust-toolchain.toml pins the stable channel only |
| **Platforms** | x86-64 (AVX2/FMA and AVX-512 by runtime dispatch, no target-cpu flags needed), aarch64 NEON, wasm32 SIMD128 (build with -C target-feature=+simd128), scalar fallback elsewhere; CI covers Linux, macOS and Windows on x86-64 and ARM64 plus i686 |
| **Thread safety** | Not documented beyond usage: the benches reuse one Decoder value across decode calls. With the parallel feature, decode runs on the global rayon pool by default (num_threads(0) = auto) whenever DRI is present and the image has 1024+ MCU blocks; num_threads(1) forces sequential. |
| **Drop-in for the baseline** | no |

## Gotchas

- With --features parallel, a single decode() call fans out over every rayon thread when restart markers are present; in a server that already parallelizes across images set num_threads(1) to avoid oversubscription.
- Open issue #215 (2026-10-02): decode_into() fails with 'internal error: coefficient data unavailable (streaming decode consumed entropy data)' on some baseline 4:2:0 JPEGs with restart markers (1024x768 with 11 RST, 2048x2048 photos with 31 RST), while decode() on the same bytes works.
- The headline baseline numbers use non-pixel-exact defaults: the Jpegli integer IDCT plus Triangle upsampling within max_diff 3; the NearestNeighbor 1.03x figure uses a cheaper box upsample than libjpeg-turbo's fancy h2v2.
- Bench-harness issues in zenjpeg/benches/decode_zenbench.rs, none of which change the README ratios: throughput is MiB/s of compressed JPEG input, not decoded pixels; the lane labelled 'zenjpeg LibjpegCompat (Libjpeg IDCT)' only sets Triangle upsampling (the default), so it re-runs the default config under a wrong label; and load_or_generate_pixels logs 'loaded' even when it falls back to synthetic pixels. CLAUDE.md attributes the 4096 parallel scaling to 'an 8-thread system' although the stated CPU is a 16-core Ryzen 9 7950X, so the thread count of the parallel table is unclear.

## Known shortcomings

- Rust (language-filter mismatch). Bench code public (zenjpeg/benches/decode_zenbench.rs) but rustc unpinned and mozjpeg-sys C flags unstated. Single-thread like-for-like: baseline decode 0.94x (slower), progressive 1.35x faster, and the default Jpegli IDCT is not pixel-exact (exact IDCT costs about 37%). The headline 2.5-7.5x is rayon multi-threading against single-threaded C on synthetic images, a comparison the repo's own bench rules forbid.
- decode_zenbench.rs counts compressed input bytes for MiB/s; the lane labelled 'zenjpeg LibjpegCompat (Libjpeg IDCT)' only sets Triangle upsampling, so the default configuration runs under the wrong label; load_or_generate_pixels logs 'loaded' even for synthetic pixels; CLAUDE.md says the parallel table ran on an 8-thread system despite the 7950X claim. The C side is mozjpeg v4 via mozjpeg-sys cc-rs at the Cargo profile's opt level with no -march, release profile debug=true and no LTO. BENCH-AUDIT.md notes BGRA output 47% slower than RGB at 4096x4096 single-threaded; open issue #215 (decode_into InternalError on baseline 4:2:0 with RST markers).

## Caveats and trade-offs

First-party benchmark; tiny project (15 stars). The C reference is mozjpeg-sys 2.2 (mozjpeg's libjpeg-turbo-derived decoder via FFI), not stock libjpeg-turbo 3.x. Single-thread baseline decode is 6% slower than C on CID22 with the default Triangle upsampling; NearestNeighbor only matches C by doing cheaper upsampling. The default decoder uses the 'Jpegli' integer IDCT, not libjpeg's ISLOW; the README says the pixel-exact Libjpeg IDCT adds about 37% overhead, so the progressive 1.35x win is measured with output that differs slightly from libjpeg-turbo (like-for-like margin unmeasured). The parallel table compares rayon multi-threaded zenjpeg with single-threaded libjpeg-turbo, against the repo's own benchmarks/README rule never to compare single-threaded and thread-pooled contenders; its libjpeg-turbo column comes from synthetic noise+patches images (Feb 2026), not CID22. The Feb 2026 synthetic single-thread table shows zenjpeg 5 to 7% faster on baseline, the newer CID22 run shows it 6% slower. rustc version not recorded. AGPL-3.0 copyleft (commercial license sold separately).

AGPL-3.0 or paid commercial licence. Pure Rust, so C++ needs bindings. Baseline decode is slightly slower than libjpeg-turbo with libjpeg-compatible upsampling; the large win needs restart markers (DRI) and the parallel feature (multi-threaded versus single-threaded libjpeg-turbo). Decoder API is prerelease. Encoder lands within about 15 to 20% of jpegli at matched quality.

## Maintenance

Actively developed (last commit 2026-09-28, about 2,600 commits, 15 stars, 20 open issues, 7 open PRs) with frequent correctness fixes in 2026; usable as source only under AGPL-3.0 or with a paid (or \$1 startup) commercial licence, and the decoder API is still prerelease.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers with public bench code (zenjpeg/benches/decode_zenbench.rs: interleaved zenbench over 10 CID22-512 photos, C reference via mozjpeg-sys FFI) and a stated CPU (Ryzen 9 7950X, WSL2) and flags (release, default target), but no rustc version (rust-toolchain.toml pins only 'stable') and no C compiler/flags for the mozjpeg-sys build, so not A. No committed result file holding the README's CID22 MiB/s figures was found.
- **Verifier notes:** Claimed numbers match README; the only genuine single-thread like-for-like win is progressive decode (1.35x, non-pixel-exact IDCT). Parallel 2.5x to 7.5x is multi-thread vs single-thread and should not be quoted as a speedup over libjpeg-turbo. Rust entry under a C++-filtered category: language-filter mismatch.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/CLAUDE.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/BENCH-AUDIT.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/docs/TUNING_HISTORY.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/zenjpeg/benches/decode_zenbench.rs>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/Cargo.toml>
  - <https://github.com/imazen/zenjpeg>
  - <https://github.com/imazen/zenjpeg/commits>
- **Sources the enricher read:**
  - <https://github.com/imazen/zenjpeg>
  - <https://github.com/imazen/zenjpeg/commits/main>
  - <https://github.com/imazen/zenjpeg/pulls>
  - <https://github.com/imazen/zenjpeg/issues?q=is%3Aissue+decode>
  - <https://github.com/imazen/zenjpeg/issues/215>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/README.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/BENCH-AUDIT.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/CLAUDE.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/docs/TUNING_HISTORY.md>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/zenjpeg/benches/decode_zenbench.rs>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/zenjpeg/src/lib.rs>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/zenjpeg/Cargo.toml>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/imazen/zenjpeg/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/kornelski/mozjpeg-sys/HEAD/src/build.rs>
  - <https://raw.githubusercontent.com/kornelski/mozjpeg-sys/HEAD/Cargo.toml>
  - <https://github.com/google/decoder-benchmarks-for-rust>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/imazen/zenjpeg`) · [data/wave10/enrich/raw/github_com_imazen_zenjpeg.json](../../../data/wave10/enrich/raw/github_com_imazen_zenjpeg.json) (enrichment confidence 0.75)

</details>
