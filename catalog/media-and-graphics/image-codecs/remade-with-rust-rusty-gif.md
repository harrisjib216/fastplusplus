# rusty_gif

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Safe-Rust fork of the image-rs gif crate whose census-routed k-means quantizer claims faster GIF encode than FFmpeg palettegen/paletteuse.

| | |
|---|---|
| **Beats** | FFmpeg 8.1.2 GIF encode via palettegen/paletteuse (dither=none, high-quality path) and FFmpeg's GIF decoder |
| **Claimed result** | README: 1.5-2.5x faster encode at higher PSNR on 8/8 benchmark frames (0.40-0.67x of FFmpeg's CPU time, PSNR +0.2 to +4.1 dB, 15/15 paired wins per frame); decode 'up to 2.5x faster' with no table or workload. |
| **Workload** | Single-frame encode of 8 real-content frames (CIF to 1080p, corpus not published) with content-routed quantization (exact palette, frequency-weighted k-means over unique colours, or NeuQuant on a 125k-sample budget) versus FFmpeg 8.1.2's palettegen/paletteuse dither=none path; pinned CPU time, interleaved A/B, 15 rounds; quality gate is each output's PSNR against the source, which must exceed FFmpeg's PSNR on the same frame. Decode workload not described. |
| **Metric** | throughput |
| **Hardware** | Not stated. |
| **Adoption** | 1 star, 0 forks, 6 commits; crates.io rusty_gif 0.1.0 (only version, 2026-08-12) with 874 downloads on 2026-10-04; the README banner's '874 active installs' equals that crates.io download count. README says it is the GIF codec of Remade-With-Rust/remade_ffmpeg_rs (rff). |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/Remade-With-Rust/rusty_gif) · [benchmark](https://github.com/Remade-With-Rust/rusty_gif) |

## Verdict

First-party only: single-frame encode of 8 unpublished frames (CIF to 1080p), rusty_gif's auto quantizer against FFmpeg 8.1.2 palettegen + paletteuse dither=none, 0.40-0.67x of FFmpeg's CPU time with +0.20 to +4.07 dB PSNR and 15/15 paired wins per frame. CPU, OS, rustc version and flags, the FFmpeg build and command line, and whether palettegen's default reserve_transparent (255-colour palette) was turned off are not stated, and the two arms do different quantization work.

## Use it when

- Rust code already on the gif crate whose time goes into Frame::from_rgb/from_rgba NeuQuant training, especially high-resolution frames with at most 65,536 unique colours (screenshots, UI captures, flat graphics, cartoons), where the census route avoids per-pixel training.
- You want MSE/PSNR-optimal palettes without dithering: weighted k-means minimises exactly the frequency-weighted squared error PSNR measures.
- You need a pure-Rust, #![forbid(unsafe_code)] GIF encoder and decoder with no C toolchain, and can accept a young single-maintainer fork.
- Per-frame encoding of independent stills where the current path is an FFmpeg palettegen + paletteuse filter graph run once per image.

## Skip it when

- You want dithered or perceptually tuned output: there is no dithering on any route, and the only quality gate is PSNR against FFmpeg with dither=none (FFmpeg's default is sierra2_4a).
- You rely on the speed argument: the k-means route ignores it and the high-diversity route overrides it (samplefac 17 at 1080p), so from_rgb no longer means NeuQuant at full quality; set RUSTY_GIF_Q_POLICY=upstream for byte-identical pre-fork output.
- Animations that need one stream-wide palette or frame-difference cropping: Frame::from_rgb\* builds an independent palette per frame, while palettegen's default stats_mode=full builds one palette for the whole stream.
- Decode speed is the goal: the decoder is unchanged gif 0.14.2 code and the decode claim has no table or workload.
- You need a tested, fuzzed codec: the fork carries none of upstream's tests/, fuzz/, gif-afl/ or benches/ directories, only unit tests in src/, and it is one code commit (2026-08-12) plus README and allocator-pin edits.

## How it is fast

Palette building is priced by colour diversity, not pixel count: a HashMap census of unique RGBA colours routes each frame to an exact palette (256 or fewer colours), to median-cut initialisation plus frequency-weighted k-means (Lloyd iterations over the unique colours, 3/2/1 iterations at up to 32,768/49,152/65,536 colours, brute-force nearest of 256 centres), or, above 65,536 colours, to NeuQuant with samplefac = ceil(pixels / 125,000) clamped to [speed, 30] (17 at 1080p). Pixel-to-index mapping is memoised per unique colour instead of searched per pixel, and NeuQuant's contest() loop is split so its decay loop auto-vectorises. LZW is the unmodified weezl crate and the decoder is upstream's, so nothing on the decode side explains the 'up to 2.5x faster decode' line.

## Compared with alternatives

The GIF siblings are C: msf_gif (single-header SSE encoder benchmarked against gif.h and jo_gif) for raw encode throughput in C/C++, and gif_load, giflib-turbo and AnimatedGIF as decoders. Pick rusty_gif only when you need a pure safe-Rust encoder with PSNR-oriented palettes; it has no measured decode edge over any of them.

## Integration

| | |
|---|---|
| **Form** | crate (rusty_gif 0.1.0 on crates.io) |
| **Dependencies** | weezl 0.1.10 (pure-Rust LZW); dev-dependency rusty_alloc-api =1.1.6 used as the examples' global allocator |
| **Minimum toolchain** | Rust 1.85 (rust-version in Cargo.toml), edition 2021 |
| **Platforms** | any std target; no SIMD intrinsics (relies on auto-vectorisation); the crate root is #![cfg(feature = "std")], so a no_std build compiles to an empty crate; CI runs ubuntu, windows and macos latest |
| **Thread safety** | not documented; the quantizer keeps no global state but reads RUSTY_GIF_Q_POLICY and RUSTY_GIF_TRACE from the environment on every frame |
| **Drop-in for the baseline** | partial — not a drop-in for FFmpeg (it is a library, or the rff CLI); for gif-crate users it is the gif 0.14.2 API under a new crate name, but Frame::from_rgb\*/from_rgba\* produce different palettes and bytes |

## Gotchas

- A library that panics on its environment: an unrecognised RUSTY_GIF_Q_POLICY value panics at encode time, and the variable is read per frame.
- Transparency gets no reserved palette slot: the single transparent colour is clustered as an RGBA point (alpha is a fourth k-means channel) and its cluster's index becomes the transparent index, so any opaque colours sharing that cluster would come out transparent; every quantizer test uses opaque pixels only (from reading quantize.rs and kmeans.rs, not run).
- examples/stage_profile.rs rebuilds the pre-fork path (NeuQuant speed 1 on every pixel) and asserts byte equality with Frame::from_rgb, so under the default policy it panics on any frame with more than 256 colours unless RUSTY_GIF_Q_POLICY=upstream; examples/encode_bench.rs times rusty_gif alone (best-of-N wall time under rusty_alloc) and has no FFmpeg arm.
- quantize.rs's module docs and Policy comment still describe the frequency-capped UniqueStream NeuQuant route as the default; the shipped Auto policy never selects it.

## Known shortcomings

- The harness is missing from this repo and from remade_ffmpeg_rs; the 1.5-2.5x encode uses a different quantiser from FFmpeg palettegen, so it is not the same work; the decode claim has no numbers and the fork changes no decoder code; the README's '874 active installs' equals the crates.io download count.
- Enricher (e119, 2026-10-05): C stands, no bug behind the numbers (upstream policy keeps a byte-identical oracle). The harness is still absent: remade_ffmpeg_rs tools/bench/pinab.py (2026-09-10) and codec-bench.ps1 (2026-09-06) both postdate the 2026-08-12 numbers, and the monorepo's crates/rusty_gif holds the same two examples. Possible flaw, not shown: the README says 'pinned CPU time' while codec-bench.ps1 notes the project's Windows CPU timer ticks at 15.625 ms and CIF frames encode in milliseconds. Gotchas: the speed argument is ignored or overridden; an unknown RUSTY_GIF_Q_POLICY panics; the transparent colour gets no reserved slot under k-means; stage_profile.rs panics under the default policy; upstream tests/ and fuzz/ were dropped.

## Caveats and trade-offs

The speedup comes from a cheaper quantizer, not a faster LZW coder: rusty_gif replaces FFmpeg's two-filter palettegen/paletteuse graph with its own census-routed quantizer, so the two arms do different work, and the quality side is judged by PSNR, which the k-means step is built to minimize (no perceptual metric, and dither=none on the FFmpeg side). Not reproducible from the repo: the pinned ABBA harness is referenced in UPSTREAM-CHANGES.md ('see repo bench notes') but is neither in this repo nor in remade_ffmpeg_rs (its readme and docs/benchmarks.md list GIF only as the pure-Rust gif crate, first frame, with no numbers); examples/ holds only encode_bench.rs (best-of-N wall time of rusty_gif alone, under the rusty_alloc-api 1.1.6 global allocator) and stage_profile.rs; CPU, compiler flags, FFmpeg build, thread settings and whether FFmpeg's CLI process time (input decode, filter graph, mux) was counted are not given. The decode claim ('up to 2.5x faster') has no numbers or workload, and UPSTREAM-CHANGES.md lists no decoder change (only vendoring color_quant, the census-routed quantizer, a NeuQuant contest() split and memoized palette mapping), so any decode speed belongs to upstream gif 0.14.2 with weezl. No comparison against giflib or the listed image-codec baselines. Performance fork of image-rs/image-gif (gif 0.14.2 plus color_quant 1.1.0), which has no benchmark data in its page. Rust, not C++. Part of Mata Network's Remade With Rust initiative; README opens with an install-count banner and an advert. Kept as a first-party claim, tier C.

#![forbid(unsafe_code)] throughout; LZW is the external pure-Rust weezl crate. The quantizer is output-changing (exact palette up to 256 colours, k-means up to 65,536, budget NeuQuant above) so palettes differ from upstream gif and from FFmpeg; RUSTY_GIF_Q_POLICY=upstream reproduces the pre-fork output byte for byte.

## Maintenance

Active only in the sense of README edits: one code commit (2026-08-12), two rusty_alloc-api pin bumps, then three 'docs: N active installs' commits whose banner (874) is the crates.io download count; MIT OR Apache-2.0 and small enough to vendor, 1 star, two open bot-style PRs (rusty_alloc-api =2.2.0, release-plz).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README and UPSTREAM-CHANGES.md give first-party encode numbers against FFmpeg 8.1.2 palettegen/paletteuse (0.40-0.67x of its CPU time, PSNR +0.2 to +4.1 dB, 8 frames, 15 rounds), but the pinned ABBA harness, the frame corpus, the CPU, rustc flags and the FFmpeg build are not published; examples/encode_bench.rs times rusty_gif alone. First-party with partial methodology is C.
- **Verifier notes:** Record accurate; added the install-banner and crates.io match, the missing harness in remade_ffmpeg_rs as well, and that the decode claim has no fork-side decoder change behind it. Not a duplicate: remade_ffmpeg_rs is listed for its audio rows only, as with rusty_h265 and rusty_flac.
- **Fields the verifier corrected:** `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party README timings
- **Pages the verifier opened:**
  - <https://github.com/Remade-With-Rust/rusty_gif>
  - <https://github.com/Remade-With-Rust/rusty_gif/commits>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/UPSTREAM-CHANGES.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/LICENSE-APACHE>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/examples/encode_bench.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/examples/stage_profile.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/readme.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/docs/benchmarks.md>
  - <https://crates.io/api/v1/crates/rusty_gif>
- **Sources the enricher read:**
  - <https://github.com/Remade-With-Rust/rusty_gif>
  - <https://github.com/Remade-With-Rust/rusty_gif/commits>
  - <https://github.com/Remade-With-Rust/rusty_gif/pulls>
  - <https://github.com/Remade-With-Rust/rusty_gif/tree/main/src>
  - <https://github.com/Remade-With-Rust/rusty_gif/tree/main/src/reader>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/UPSTREAM-CHANGES.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/NOTICE.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/examples/encode_bench.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/examples/stage_profile.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/src/quantize.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/src/kmeans.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/src/common.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/src/encoder.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_gif/HEAD/src/neuquant.rs>
  - <https://github.com/image-rs/image-gif>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/scripts>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools/bench>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools/quality>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commits/main/tools/bench/pinab.py>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commits/main/tools/bench/codec-bench.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/pinab.py>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/codec-bench.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/build-v3.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/build-v3.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/.cargo/config.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/filters.texi>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_gif>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_gif/examples>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/remade-with-rust/rusty_gif`) · [data/wave10/enrich/raw/github_com_remade_with_rust_rusty_gif.json](../../../data/wave10/enrich/raw/github_com_remade_with_rust_rusty_gif.json) (enrichment confidence 0.7)

</details>
