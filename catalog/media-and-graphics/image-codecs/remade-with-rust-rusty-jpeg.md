# rusty_jpeg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `(MIT OR Apache-2.0) AND IJG` · 🟢 active

> Pure-Rust JPEG/MJPEG decoder and encoder with AVX2/NEON kernels; by its own measurement at parity with FFmpeg's native MJPEG codec, not faster.

| | |
|---|---|
| **Beats** | FFmpeg 8.1.2 native MJPEG encoder and decoder (not libjpeg-turbo) |
| **Claimed result** | No speedup: README states parity with FFmpeg 8.1.2. Encode median 0.96x (paired interleaved, N=41, z -3.59, matched output size with ours 3.1% smaller); decode median 1.02x (WHYS.md: 15/31, z -0.18, median 1.0157, inside noise). WHYS.md gives the ratio as FFmpeg time over ours, so encode is about 4% slower and decode about 2% faster within noise. WHYS.md shows the same encode comparison reading 1.4510 at N=15, 1.0286 at N=21 and 0.9608 at N=41; CHANGES.md withdraws the earlier 1.19-1.45x claims of 0.1.x to 0.2.x as small-N artifacts, and the earlier 'decode 1.04x faster' was N=15. |
| **Workload** | Encode: 40-frame 1920x1080 4:2:0 clip at about 680 KB per frame to MJPEG at matched output size with fixed Huffman tables on both sides. Decode: one photographic still stream-copied to 300 frames, both arms discarding output. One pinned core each, CPU time, paired interleaved runs. |
| **Metric** | throughput |
| **Hardware** | CPU model not stated; one pinned core; the author notes the test box drifts about 15 percent. Harness scripts in WHYS.md are PowerShell (.ps1). |
| **Compiler and flags** | Not stated. Cargo.toml has no custom release profile; default features enable AVX2/SSE4.1 kernels with runtime detection (NEON on aarch64). FFmpeg run with -threads 1 per WHYS.md. |
| **Adoption** | 1 star; README claims 2,784 active installs (RAG Converter runs it as WebAssembly) |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/Remade-With-Rust/rusty_jpeg) · [benchmark](https://github.com/Remade-With-Rust/rusty_jpeg) |

## Verdict

First-party, on an unnamed Windows machine (PowerShell harness), one pinned core, CPU time, against FFmpeg 8.1.2's native MJPEG codec at -threads 1. Encoding a 40-frame 1080p 4:2:0 clip at matched output size (ours 3.1% smaller, fixed Huffman tables on both sides) gave a median ratio of 0.96 (ours about 4% slower, 9 of 41 pairs won), and decoding one still stream-copied to 300 frames gave a median of 1.02 (15 of 31, inside noise). CPU model, rustc flags and the harness scripts are not published, so this is parity, not a speedup.

## Use it when

- You need a JPEG encoder and decoder with no C or FFI in a Rust media pipeline (MJPEG, camera frames) and single-core speed roughly level with FFmpeg's native MJPEG codec is enough.
- Planar or camera input and output: encode yuv420p/422p/444p planes or packed YUYV without an RGB round trip, and decode_planar() when the consumer wants YCbCr.
- no_std + alloc targets: the RISC-V ESP32-C6/P4 classes are built in CI (the S3 via espup); decode from a slice with 1/2-1/8 scaling, and encode into a caller buffer that returns BufferTooSmall instead of a truncated file.
- Chroma quality on encode: chroma is box-averaged on downsampling rather than point-sampled (first-party -17.12% BD-rate on chroma-detailed content).
- Host and chip must emit identical bytes, provided both use the scalar kernels (no_std, platform_independent, or std without simd).

## Skip it when

- You want to beat libjpeg-turbo: it has never been measured against libjpeg-turbo, only FFmpeg's native MJPEG codec, and its own log puts the entropy decoder at about 14 cycles per symbol with nothing left to gain without hand-written assembly.
- You need a reliable speed figure: the project's own encode-versus-FFmpeg readings for one comparison range from 1.45x faster to 4% slower (see measurement notes).
- You want small files cheaply: optimized Huffman tables save 7.4% for 2.09x encode time, and trellis costs +144% encode time with a BD-rate gain measured only on a synthetic corpus whose cost figure was 46x off.
- Default x86 builds must match other targets byte for byte: the AVX2 forward DCT and SSSE3 inverse DCT round differently from the scalar kernels (plus or minus 1 LSB).
- You need a long track record: it is single-maintainer with 1 star, and recent releases fixed a panic on every progressive file in a 960-file libjpeg corpus (0.2.1/0.2.2), an 8 GiB allocation from a small malformed progressive header (0.2.2), and corrupt streams from optimized Huffman tables with restart intervals (0.4.0).

## How it is fast

Decode: an AVX2 IDCT that runs two 8x8 blocks per instruction stream, one per 128-bit lane, and is byte-identical to the SSSE3 kernel run twice; entropy decode fused with the IDCT on baseline interleaved scans, which removes a write-zero-read round trip of about 18.8 MB per 1080p frame through the coefficient row buffer; a devirtualised per-MCU call into the synchronous worker; a shared buffered reader instead of per-symbol read_exact; a DC-only fill. rayon stays off because it measured slower at every size. Encode: hand-written AVX2 quantize, AVX2 forward DCT and colour conversion, a 64-bit non-zero mask from one AVX2 compare stepped with trailing_zeros (1.28x same-binary), and SIMD block extraction using maddubs for the 4:2:0 chroma box filter (1.25x same-binary), feeding a libjpeg-turbo-style 64-bit bit accumulator with bulk 8-byte flushes. These are wins against the crate's own earlier builds; against FFmpeg the result is parity.

## Compared with alternatives

Pick it over libjpeg-turbo-rs and zenjpeg, which publish numbers against libjpeg-turbo, only when you need no_std/ESP32 builds, planar or YUYV input and output, and both directions in one pure-Rust crate. Over jpeg-encoder (vstroebel), the upstream of its encoder half, it adds the AVX2/NEON encode kernels and box-averaged chroma. For raw speed, libjpeg-turbo (or a crate measured against it) remains the pick.

## Integration

| | |
|---|---|
| **Form** | crate (rusty_jpeg 0.4.1 on crates.io) |
| **Dependencies** | none by default; optional rayon behind the off-by-default rayon feature; dev-dependency rusty_alloc-api 0.4 used as the examples' global allocator |
| **Minimum toolchain** | Rust 1.85 (rust-version), edition 2021 |
| **Platforms** | any target via the scalar kernels; x86-64 AVX2/SSE4.1/SSSE3 kernels with runtime detection (simd feature, default); aarch64 NEON quantize and forward DCT; no_std RISC-V ESP32 targets in CI; the platform_independent feature drops arch code and forbids unsafe |
| **Thread safety** | the default decoder hands rows to a worker thread for larger images; set_single_threaded(true) decodes on the calling thread (about 38% less CPU per WHYS.md); RUSTY_JPEG_\* environment knobs are read once and cached in a OnceLock under std; otherwise not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Decoding is multithreaded by default, and the inherited upstream jpeg-decoder heuristic that picks the worker multiplies width by width (select_worker reads output_size.width twice), so any image wider than 128 px starts a thread whatever its height; call set_single_threaded(true) for one-core use. Before 0.1.2 that flag did nothing on baseline JPEGs.
- The GitHub repo description still says 'Encodes 1.19x faster than FFmpeg ... decodes 1.05x faster', and WHYS.md has a 'FINAL STANDING' table (1.19x encode, 1.04x decode) that a later section supersedes; only the README and CHANGES.md 0.3.0 parity figures are current.
- SIMD and scalar kernels differ by plus or minus 1 LSB, so tests/no_std_surface.rs pins two golden rows; use the scalar build as the oracle for an embedded target.
- Downstream packagers: issue #6 (open since 2026-09-11) asks for the provenance and redistribution terms of tests/fixtures/progressive_libjpeg.jpg, and the licence is (MIT OR Apache-2.0) AND IJG, which requires IJG attribution for the forward-DCT files.

## Known shortcomings

- Not faster: parity with FFmpeg 8.1.2 (encode 0.96x, N=41, z -3.59; decode median 1.0157, N=31, z -0.18) after the earlier 1.19-1.45x claims were withdrawn; the PowerShell harness is not in the repo and no CPU or rustc flags are stated.
- Enricher (e119, 2026-10-05): C stands. The project's own numbers conflict: 0.2.3 reports 781 vs 953 ms (1.22x faster), two same-binary wins (1.28x, 1.25x) imply about 1.95x (derived), yet the published ratio is 0.96x; the same comparison gave 12/15 (z +2.32) and then 9/41 (z -3.59), opposite significant results, so the instrument drifts and the parity figure is unresolved (0.96x-1.45x). CHANGES' '25 pairs, z 3.36' is wrong (z matches 14/15). The README decode run uses 300-frame (about 2 s) arms that its own D1-FINAL rule rejects. Inherited jpeg-decoder select_worker uses width twice (threading heuristic only). The stale GitHub description still says 1.19x/1.05x. Issue #6 asks for the licence of the progressive_libjpeg.jpg fixture.

## Caveats and trade-offs

Not faster than the baseline: the project's own final standing is parity, and its encode test (N=41) reads about 4% slower. Threads: one pinned core each and ffmpeg -threads 1, but WHYS.md D6f records that the 'single-threaded' arm was silently multithreaded (decoder.rs hard-coded PreferWorkerKind::Multithreaded) until repaired, and an earlier 'decode 1.17x faster' reading came entirely from extra cores. Timer is pinned CPU time; decode bitstream and per-frame checksums are identical across arms, while encode outputs differ (matched size only, ours 3.1% smaller; no output-quality comparison at matched size). Reproducibility is poor: the PowerShell harness scripts (pinned.ps1, paired.ps1, paired2.ps1) named in WHYS.md are not in the repo tree, CPU model and rustc settings are missing (Cargo.toml has no release profile; MSRV 1.85), and the author notes the box drifts about 15% and that the same ffmpeg command drifted 953 to 1266 ms within one session. FFmpeg's native MJPEG codec is a different baseline from libjpeg-turbo. WHYS.md also documents several void measurements and a trellis cost claim off by 46x (CHANGES.md: trellis was +144% encode time on real footage, not +3.1%). The crate is a vendored merge of jpeg-decoder 0.3.2 (image-rs) and jpeg-encoder 0.7.0 (vstroebel, already in the catalog at tier D) with its own AVX2/NEON kernels, fused decode-IDCT and mask-driven AC scan; not a GitHub fork. The '2,784 active installs' figure is a first-party README badge (RAG Converter, WebAssembly). Kept as a flagged entry.

no_std plus alloc builds for ESP32-class chips; x86 AVX2 DCT and SSSE3 IDCT kernels are not bit-identical to the scalar twins (plus or minus 1 LSB); trellis quantization is off by default because it costs +144% encode time; optimized Huffman tables give -7.4% size for 2.09x encode time; chroma is box-averaged on downsample, so output differs from FFmpeg's. IJG attribution clause applies to the forward-DCT files.

## Maintenance

Young and single-maintainer: 18 crates.io versions between 2026-07-31 and 2026-09-03, with no code change since v0.4.1 (2026-09-03) beyond README banner edits whose '2,784 active installs' tracks the crates.io download total (2,875 on 2026-10-05); a release-v0.4.2 PR has been open since 2026-09-03. It is copyable under (MIT OR Apache-2.0) AND IJG.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party only: README Performance table (encode median 0.96x, N=41, z -3.59; decode median 1.02x, N=31, z -0.18) and WHYS.md/CHANGES.md logs against FFmpeg 8.1.2 -threads 1, but the paired.ps1/paired2.ps1/pinned.ps1 harness is not in the repo (examples/ holds only decode_bench.rs and other single-binary tools), and no CPU model or rustc flags are stated, so not A.
- **Verifier notes:** Parity verified in README, WHYS.md (Standing table, lines \~1340-1360) and CHANGES.md; confirm at C as a not-faster flagged entry per orchestrator. jpeg-encoder (vstroebel) is a separate catalog entry; rusty_jpeg carries substantial own SIMD work, so not marked duplicate. Repo: 1 star, 0 forks, 38 commits, last commit 2026-10-04, license (MIT OR Apache-2.0) AND IJG.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party paired runs
- **Pages the verifier opened:**
  - <https://github.com/Remade-With-Rust/rusty_jpeg>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/commits>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/tree/main/examples>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/WHYS.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/examples/decode_bench.rs>
- **Sources the enricher read:**
  - <https://github.com/Remade-With-Rust/rusty_jpeg>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/commits>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/issues>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/issues/6>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/pulls?q=is%3Apr>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/tree/main/src>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/tree/main/src/decode>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/tree/main/src/encode>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/tree/main/tests>
  - <https://github.com/Remade-With-Rust/rusty_jpeg/tree/main/examples>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/WHYS.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/CHANGES.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/src/decode/decoder.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/src/decode/upsampler.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/src/decode/worker/mod.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/src/encode/encoder.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_jpeg/HEAD/examples/decode_bench.rs>
  - <https://raw.githubusercontent.com/image-rs/jpeg-decoder/master/src/decoder.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/scripts/sync-rusty-jpeg-mirror.sh>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_jpeg>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/scripts>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools/bench>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/codec-bench.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/pinab.py>
  - <https://crates.io/api/v1/crates/rusty_jpeg>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/remade-with-rust/rusty_jpeg`) · [data/wave10/enrich/raw/github_com_remade_with_rust_rusty_jpeg.json](../../../data/wave10/enrich/raw/github_com_remade_with_rust_rusty_jpeg.json) (enrichment confidence 0.75)

</details>
