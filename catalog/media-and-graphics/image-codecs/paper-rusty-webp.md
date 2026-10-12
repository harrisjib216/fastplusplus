# rusty_webp (remade_ffmpeg_rs crates/rusty_webp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Pure safe-Rust WebP codec (image-webp fork): lossless encode 1.6-2.8x faster than libwebp m4, decode faster than FFmpeg.

| | |
|---|---|
| **Beats** | libwebp (default lossless effort m4, driven through FFmpeg 8.1.2's libwebp encoder); decode rows are against FFmpeg's native VP8/VP8L decoder, not libwebp |
| **Claimed result** | Lossless encode: '1.6-2.8x faster than libwebp's default effort (m4)' at '+4...13%' size on photos (smaller than libwebp m0 on every corpus image) and 'up to 39% smaller' than m4 on screen or repeated content. Decode versus FFmpeg: lossy (VP8) 8K '1.24-1.29x faster, bit-exact'; lossless (VP8L) 8K '\~2.15x faster'. |
| **Workload** | Pinned single-core child CPU time, ABBA-interleaved pairs (N = 21-31, null-arm floor 5% or less), on a real-content corpus (Derf video frames 1080p to 8K, screen captures, alpha, odd sizes): lossless VP8L encode versus libwebp m4, plus lossy and lossless WebP decode versus FFmpeg. |
| **Metric** | throughput |
| **Adoption** | remade_ffmpeg_rs 6 stars, 0 forks, 506 commits; crates.io rusty_webp 0.1.1 (1,025 downloads; 0.1.0 and 0.1.1 both published 2026-08-12) |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/Remade-With-Rust/remade_ffmpeg_rs) · [benchmark](https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/README.md) |

## Verdict

First-party only, against FFmpeg 8.1.2 on one pinned core with ABBA-interleaved pairs and child CPU time. Lossless VP8L encode (N=21, per the commit message) ran 1.6-2.8x faster than ffmpeg -c:v libwebp -lossless 1 at the default effort m4. Photo files came out 4-13% larger (but smaller than m0), and screen content up to 39% smaller. An 8K lossy decode test (N=31, two runs) ran 1.24-1.29x faster than FFmpeg's native VP8 decoder with bit-exact YUV output, and 8K lossless decode ran about 2.15x faster than FFmpeg's native VP8L decoder. CPU, OS, rustc flags, corpus files and the WebP harness are not published.

## Use it when

- You must emit lossless WebP from pure Rust with no C, no FFI and #![forbid(unsafe_code)], and encode time matters more than the last 4-13% of file size on photographs.
- Screen captures, UI and other repeated content, where the first-party corpus shows files up to 39% smaller than libwebp m4.
- Video or YUV pipelines that ingest still lossy WebP: read_yuv420() returns the native 4:2:0 planes zero-copy, and the authors report bit-exact output against FFmpeg's decoder (webp to y4m) on their corpus.
- Decoding animated WebP in Rust into composited canvas frames with per-frame durations (FFmpeg's native webp decoder errors on these files).
- You use upstream image-webp and want better lossless compression: upstream's runs-only encoder was 35-53% larger than libwebp on photos, per this fork's NOTICE.md.

## Skip it when

- Lossy WebP encoding. There is no VP8 encoder, and animation encoding is not supported either.
- Smallest lossless files. libwebp m4 is 4-13% smaller on photos. The encoder has no color-indexing (palette) transform, no cross-color transform and no entropy image, so low-colour graphics could fall further behind (an inference; the corpus results are given only as ranges).
- You need to know how it compares with libwebp's decoder (dwebp). That was never measured: the decode baseline is FFmpeg's native VP8/VP8L decoder. Upstream image-webp puts its own decoding at 70-100% of libwebp, and before this fork's speed work it was 1.18x slower than FFmpeg on the 8K lossy test.
- Lossless encoding of very large images on tight memory. Reading the code gives a peak of about 30 bytes per pixel (RGBA copy, residual copy, u32 pixel array, hash-chain links and a 12-byte token per pixel), which is about 1 GB for a 7680x4320 frame. This was derived from the code, not measured.
- You need maturity or outside validation. It is one crate in a 6-star monorepo with two commits (both 2026-08-12) and 1,025 crates.io downloads, against 83 million for upstream image-webp. No numbers have been measured by anyone other than the authors.

## How it is fast

The encoder searches far less than libwebp at m4. It uses greedy hash-chain LZ77 over the ARGB pixels (32 candidates per position, cut to 8 and then 2 in long matchless stretches, an early exit at 128-pixel matches, and an unconditional distance-1 probe). It codes one Huffman group for the whole image, with no entropy image or histogram clustering. The color-cache size is picked from 0, 4, 6, 8 or 10 bits by a Shannon estimate. Per 16x16 tile it picks one of the 14 predictors by summed wrap-around residual magnitude, and the only other transform is subtract-green. A sampling dispatch skips the per-tile search on large run-heavy images. The decoder's speed-ups over upstream are a branch-free i16 select formulation of the normal loop filter, run over whole 16-lane (luma) or 8-lane (chroma) edges so the compiler can auto-vectorize it (no intrinsics), a block-scoped FastSession in the boolean decoder (one state snapshot and one validity check per coefficient block), a DC-only IDCT path, and native YUV output that skips RGB conversion.

## Compared with alternatives

Pick it when the output has to be WebP and the program has to be pure safe Rust. nativewebp is the Go analogue (a pure-Go lossless WebP encoder), @napi-rs/image drives libwebp itself from Node, and libjxl's fjxl, fpnge or QOI/QOIR encode far faster when you are free to choose a different format.

## Integration

| | |
|---|---|
| **Form** | crate (rusty_webp 0.1.1 on crates.io; source in crates/rusty_webp of remade_ffmpeg_rs) |
| **Dependencies** | byteorder-lite 0.1, quick-error 2.0.1; dev only: rand 0.8, rusty_alloc-api (the house allocator used by the example bench) |
| **Minimum toolchain** | Declared rust-version 1.80.1 (inherited from upstream), but encoder.rs calls Option::is_none_or, which became stable in Rust 1.82, so 1.82+ is needed in practice. Edition 2021; the workspace pins 1.95.0. |
| **Platforms** | any Rust target: safe code only, with no arch-specific SIMD (the speed relies on auto-vectorization) |
| **Thread safety** | Not documented. Decoder and encoder are single-threaded owned values, and no global mutable state was found in the crate (the opt-in profile feature only prints timings to stderr). |
| **Drop-in for the baseline** | no |

## Gotchas

- The MSRV is wrong. Cargo.toml says 1.80.1, but the encoder's cache-size selection uses Option::is_none_or (stable since 1.82), so builds on 1.80 or 1.81 fail.
- The bit-exactness claim covers the YUV path only (webp to y4m against FFmpeg). RGB output goes through fancy bilinear upsampling with libwebp's fixed-point constants and was not reported as compared against dwebp. The rff CLI switches to that path only when RFF_WEBP_UPSAMPLE is set.
- Only the normal loop filter received the batched 16-lane kernels. Files encoded with VP8's simple loop filter still run the scalar per-pixel edge functions, so the decode speed-up may not carry over to them.
- Encoder behaviour depends on content. Images over 262,144 pixels where at least 25% of sampled pixels repeat their left neighbour get one fixed 'top' predictor for the whole image instead of the per-tile search. Below that size the 14-way search always runs, at about 14 predictor evaluations per pixel.

## Known shortcomings

- First-party: the WebP harness and corpus are unpublished, CPU and flags unstated, the ffmpeg CLI child-process time is compared against an in-process arm, a custom allocator is used, the decode baseline is FFmpeg rather than libwebp and encode is compared only at method 4 (encode 1.6-2.8x faster but files 4-13% larger on photos). The record's 16-23x figure was upstream image-webp's encoder, not an earlier rusty_webp (corrected). Lives in crates/rusty_webp of remade_ffmpeg_rs, fork of image-rs/image-webp.
- Enricher: the WebP harness is still unpublished and the numbers exist only in the commit 26cad51 message; pinab.py does not fit (it needs an arm that prints 'total ms', which ffmpeg does not); the 'null-arm floor under 5%' is an ffmpeg-vs-itself noise floor, not an overhead bound; child CPU time includes launch, demux, input decode and ffmpeg's RGB32 conversion; the project's later codec-bench.ps1 (2026-09-06) warns that Windows TotalProcessorTime has a 15.625 ms tick lattice that faked earlier published deltas, and the OS of the WebP run is unstated. Lossy 1.24-1.29x is one 8K test over two N=31 runs (run spread, not corpus spread); lossless decode 2.15x has no N or file named; encode compared only against libwebp m4; decode baseline is FFmpeg's native decoder, never dwebp; bit-exact applies to the YUV path only. Cargo.toml says rust-version 1.80.1 but encoder.rs uses Option::is_none_or (Rust 1.82+); no palette, cross-colour or entropy image transforms; encode peak about 30 bytes per pixel. VP8L encoder and loop filter checked against spec, no correctness bug found.

## Caveats and trade-offs

First-party, and the WebP harness is not in the repo: tools/bench has the generic ABBA harness pinab.py (pins one CPU and parses the arm's printed duration; its usage text is audio-shaped) and codec-bench.ps1 but no WebP script, docs/benchmarks.md covers VP9 only (Intel Core i7-14650HX), crates/rusty_webp/examples holds only decode_bench.rs (times rusty_webp alone, under the project's custom global allocator rusty_alloc_api::RustyAlloc), and the Derf corpus is not shipped; compiler, flags and CPU for the WebP rows are unstated. The README says 'child CPU time', which for the ffmpeg CLI arm includes demux and any pixel-format conversion against an in-process Rust arm; the companion remade_ffmpeg_rs record found that pattern inflated its MP3 margin. The libwebp baseline is reached through FFmpeg's libwebp wrapper, not cwebp, and only at m4: there is no speed comparison against libwebp's faster efforts m0-m3, although on photos the encoder lands between m0 and m4 in size (+4-13% over m4). Decode wins are against FFmpeg's native VP8/VP8L decoder, not libwebp's dwebp; upstream image-webp's README says its decode runs at 70-100% of libwebp's speed. NOTICE.md records that upstream image-webp v0.2.4's encoder (the fork's starting point, not a first version of the fork) was 16-23x faster than libwebp but produced 35-53% larger files on photos (+656% on repeated-content screen material), so the 1.6-2.8x is a deliberate size/speed trade and the fork's encoder is much slower than the upstream one it replaced. Repository shows AI assistance (CLAUDE.md, .claude directory, commits co-authored by claude); the rusty_webp path has two commits, both 2026-08-12 (repo-wide last commit 2026-10-05). The repo LICENSE is Apache-2.0; the crate is MIT OR Apache-2.0 with the upstream license files kept. Shares repo_url with the remade_ffmpeg_rs record (video-audio), hence the paper:rusty-webp id.

Pure Rust, #![forbid(unsafe_code)], lossless VP8L encode and VP8/VP8L/animated decode, native YUV 4:2:0 output; no lossy (VP8) encoder. The encode speed comes with larger files than libwebp m4 on photographs (+4 to 13%). Lives as one crate in the remade_ffmpeg_rs monorepo (crates/rusty_webp), also published as the rusty_webp crate.

## Maintenance

The monorepo is active (506 commits, latest 2026-10-05), but the rusty_webp crate has not changed since it was created on 2026-08-12. The crate is MIT OR Apache-2.0, safe code with two small dependencies, and about 9.6k lines, so it is easy to vendor. The first-party numbers have no published harness to reproduce them.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table against FFmpeg 8.1.2 (libwebp encoder at default m4, native VP8/VP8L decoder) with a described method (pinned single core, ABBA pairs, null-arm floor) but no WebP harness script, corpus, CPU, rustc version or flags published; the only bench code, examples/decode_bench.rs, times rusty_webp alone.
- **Verifier notes:** README numbers verified verbatim (lossy 8K decode 1.24-1.29x bit-exact, lossless 8K decode \~2.15x, lossless encode 1.6-2.8x faster than libwebp m4 at +4-13% size on photos, up to 39% smaller on screen content); metadata matches. Corrected the NOTICE reading: the 16-23x / 35-53% figures describe upstream image-webp's encoder, not an earlier rusty_webp. Not a duplicate: the existing remade_ffmpeg_rs record covers the audio codecs. Shortcomings to record: harness and corpus unpublished, CPU and flags unstated, CLI child-time against in-process arm, custom allocator, decode baseline is FFmpeg not libwebp, encode compared only at m4.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** published harness comparing against libwebp in-process; published harness against dwebp and cwebp m1-m6
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/NOTICE.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/examples/decode_bench.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/tools/bench/pinab.py>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/tools/bench/codec-bench.ps1>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commits>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commits/main/crates/rusty_webp>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_webp>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_webp/examples>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools/bench>
  - <https://crates.io/api/v1/crates/rusty_webp>
  - <https://raw.githubusercontent.com/image-rs/image-webp/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/NOTICE.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/examples/decode_bench.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/encoder.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/decoder.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/loop_filter.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/vp8.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/vp8_arithmetic_decoder.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/lossless.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/lossless_transform.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/yuv.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/transform.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/huffman.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rusty_webp/src/extended.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rff-codec-webp/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/crates/rff-codec-webp/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/tools/bench/pinab.py>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/HEAD/tools/bench/codec-bench.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/readme.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/docs/compatibility.md>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_webp/src>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/docs/finished>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/docs/plans>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commits/main/crates/rusty_webp>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commits/main/tools/bench/codec-bench.ps1>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commit/26cad51cc0079ff6950404fcf288fd0e1dad9da9>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/issues?q=is%3Aissue%20webp>
  - <https://crates.io/api/v1/crates/rusty_webp>
  - <https://crates.io/api/v1/crates/image-webp>
  - <https://crates.io/api/v1/crates/rff-codec-webp>
  - <https://raw.githubusercontent.com/image-rs/image-webp/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `paper:rusty-webp`) · [data/wave10/enrich/raw/paper_rusty_webp.json](../../../data/wave10/enrich/raw/paper_rusty_webp.json) (enrichment confidence 0.55)

</details>
