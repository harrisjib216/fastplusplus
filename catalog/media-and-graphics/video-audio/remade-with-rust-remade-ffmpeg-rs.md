# remade_ffmpeg_rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Pure-Rust, Apache-2.0 FFmpeg rebuild whose MP3 decoder and frame-parallel AAC/Vorbis encoders beat FFmpeg's CLI on wall clock.

| | |
|---|---|
| **Beats** | FFmpeg libavcodec native MP3 decoder and native AAC encoder; libvorbis |
| **Claimed result** | Per component, all first-party. MP3 decode (crate rusty_mp3, crates/rusty_mp3/README.md) vs the FFmpeg CLI's native libavcodec MP3 decoder (`-f null -`, not libmp3lame or mpg123), 27.5-minute stream, decode-and-discard, wall clock, 15 alternated pairs: 1 physical core 1,952 vs 2,431 ms (1.24x, 15/15, z = -3.87); 2 physical cores, pipelined build 1,017 vs 1,455 ms (1.39x); total CPU on one core 1,875 vs 2,125 ms (1.13x less CPU, derived from page data). The same table's control row shows the serial rusty_mp3 build on 2 cores at 1,807 ms against FFmpeg's 1,445 ms, i.e. FFmpeg 1.25x faster (derived from page data), because FFmpeg's CLI spreads work over about 2 cores even with -threads 1. AAC-LC encode (crate rusty_aac) vs FFmpeg 8.1.2's native AAC encoder (`-c:a aac`, not libfdk_aac): main README about 6x faster on a 60 s stereo clip (about 450x realtime) via frame-parallel encoding against FFmpeg's single-threaded encoder, about 1.15x single-thread; the crate README reports 3.2-7.9x (mean 5.0x) on 24 s clips (piano 214x vs 57x realtime, guitar 306x vs 39x, vocal 299x vs 93x), best-of-5, unpinned subprocesses. Vorbis encode (crate rusty_vorbis) vs libvorbis via `ffmpeg -c:a libvorbis`: at about 140 kb/s, 443x realtime on 24 cores vs libvorbis 86x (about 5.2x in docs/benchmarks.md, 5.3x in the README), but single-thread 60x vs 87x realtime (about 1.45x slower than libvorbis), and libvorbis is 0.6-0.7 PEAQ ODG ahead on tonal content at matched bitrate. Image rows (PNG decode 2.55-2.89x, lossy WebP decode 1.24-1.29x vs FFmpeg) are outside video-audio. |
| **Workload** | MP3 decode of a 27.5-minute stream, decode-and-discard on the same physical cores, 15 pairs; AAC-LC encode of a 60 s stereo clip with frame-parallel encoding; Vorbis encode of stereo music on 24 cores. |
| **Metric** | throughput |
| **Hardware** | Not stated for the MP3 and AAC rows; docs/benchmarks.md names an Intel Core i7-14650HX for VP9 decode and only a '24-core box' for the Vorbis rows; the harnesses are Windows PowerShell/psutil scripts pinning to one core at High priority |
| **Compiler and flags** | Rust 1.95.0 pinned in rust-toolchain.toml; workspace [profile.release] lto = "thin", codegen-units = 1, panic = "unwind"; default build has no target-cpu flag (AVX kernels are runtime-dispatched); binaries use the in-house rusty_alloc global allocator. FFmpeg 8.1.2 (system build, flags not stated) for the AAC comparison; FFmpeg version for the MP3 and Vorbis rows not stated. |
| **Adoption** | 6 stars, 0 forks; crates.io rusty_mp3 0.8.0 (42,200 downloads), rusty_aac 0.5.0 (7,824), rusty_vorbis 0.1.1 (1,668), all pointing to this repo; README claims 175,858 active installs through MATA Disco (not verifiable) |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/Remade-With-Rust/remade_ffmpeg_rs) · [benchmark](https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/readme.md) |

## Verdict

First-party, unnamed machine, Rust 1.95.0 thin-LTO builds. rusty_mp3's decode loop (the decprof example) against the FFmpeg CLI's native mp3float decoder (`-f null -`, FFmpeg version not stated) on one 27.5-minute stream, 15 alternated wall-clock pairs: 1,952 vs 2,431 ms on 1 physical core and 1,017 vs 1,455 ms on 2 with the two-thread pipeline; the serial build on 2 cores lost, 1,807 vs 1,445 ms. AAC-LC encode via the rff CLI was 3.2-7.9x faster than FFmpeg 8.1.2's native encoder (unpinned subprocesses, best-of-5, all cores against one), and Vorbis encode about 5.2x faster than libvorbis on 24 cores but about 1.45x slower single-threaded.

## Use it when

- You need MP3 decoding in a Rust or wasm program under a permissive licence with no C or FFI; the authors gate it bit-exact against FFmpeg, and it is bit-exact on wasm32-wasip1 and wasm32-unknown-unknown with zero host imports.
- Offline batch transcoding of whole files to AAC-LC or Vorbis on a many-core box, where wall-clock time matters more than CPU time and the whole input can sit in memory (AAC 3.2-7.9x and Vorbis about 5.2x faster than single-threaded FFmpeg/libvorbis, first-party).
- Embedding an AAC-LC or MP3 encoder in a Rust binary without FFmpeg's LGPL/GPL or FDK's licence; rusty_aac's PEAQ table has it ahead of FFmpeg's native AAC on real mono music at 128 kb/s and above.
- Decoding long MP3 files already in memory on a 2-core budget: `decode_pipelined` measured 1,017 ms against FFmpeg's 1,455 ms on two physical cores.

## Skip it when

- Live or low-latency encoding: the AAC and Vorbis encoders buffer the whole stream and return `Again` from `next_packet` until `finish()`, so the parallel speedup exists only in whole-file mode.
- CPU-bound single-threaded encoding or best quality per bit: single-thread Vorbis is about 1.45x slower than libvorbis and 0.6-0.7 PEAQ ODG behind on tonal music; rusty_aac has no bit reservoir or VBR and trails FFmpeg at 96 kb/s and below, on piano stereo and on noise-like content.
- AAC decoding at scale, HE-AAC or more than 6 channels: the decoder's IMDCT is a naive O(N^2) f64 cosine sum (open issue #16 measured 24.4 ms per 21.3 ms frame on an EPYC 7763), SBR is not reconstructed, and 7+ channels are rejected.
- Video work: VP9 decode runs at 0.16-0.21x of FFmpeg and H.264 decode about 2x behind.
- Anything needing an audited, settled codebase: pre-1.0, 'not yet independently audited', 6 stars, and open issue #14 reports `cargo test` red on all three CI runners (rusty_av2d overflow).

## How it is fast

MP3 decode: five bit-identical changes (an 8-byte word-load bit reader for Huffman peeks, a circularly addressed synthesis V-FIFO instead of a 960-float memmove per pass, a half-work IMDCT that derives mirrored outputs from exact symmetries of the stored cosine tables, runtime-detected AVX matrixing and windowing kept bit-exact by using separate mul+add, and a division-free Huffman pair decode), plus `decode_pipelined`, which splits entropy decoding (bit reservoir) from the transform (IMDCT overlap, synthesis FIFO) across two threads joined by a bounded channel. AAC and Vorbis encode: frame parallelism. Window decisions are made up front, then contiguous frame ranges are encoded on `available_parallelism()` scoped threads. This works because the AAC encoder has no bit reservoir (fixed per-frame budget) and the Vorbis encoder codes independent 2048-sample long blocks. N/4-point FFT MDCTs, AVX2 quantize kernels and a Vorbis energy-bucket residue-class shortlist cut per-frame cost.

## Compared with alternatives

Pick it over Symphonia when you also need encoders (AAC-LC, MP3, Vorbis) or FFmpeg-bit-exact MP3 output. Symphonia is the broader decode-only library, and its comparison against libavcodec runs in-process, which is stronger evidence than this repo's CLI timing. Pick glint instead for a C/C++ AAC encoder with a streaming per-frame C ABI. Pick rusty-opus (same organisation, separate repo) for Opus.

## Integration

| | |
|---|---|
| **Form** | crate (standalone rusty_mp3 0.8.0, rusty_aac 0.5.0, rusty_vorbis 0.1.1; engine library remade-ffmpeg 0.2.0; rff-cli binaries) |
| **Dependencies** | none for the three codec crates (empty [dependencies]); examples, benches and the CLI use the in-house rusty_alloc global allocator |
| **Minimum toolchain** | Rust 1.85 (crate rust-version); workspace pins 1.95.0 in rust-toolchain.toml; rusty_aac's opt-in AVX-512 tier needs Rust 1.89+ |
| **Platforms** | Windows, macOS and Linux for the CLI; x86-64 gets runtime-detected AVX/AVX2 kernels with scalar fallbacks, and other targets run the scalar paths; rusty_mp3 verified bit-exact on wasm32-wasip1 and wasm32-unknown-unknown |
| **Thread safety** | Not documented per type. Decoders and encoders are independent owned values; the encoders spawn `available_parallelism()` scoped threads inside finish/drain; rusty_mp3's stage profiler writes process-global atomics shared by every decoder instance. |
| **Drop-in for the baseline** | partial: the rff CLI mimics common ffmpeg flags and can install as ffmpeg/ffprobe, but codec and container coverage is a subset, and the Rust library APIs do not replace libavcodec's C API |

## Gotchas

- rusty_mp3's per-stage profiler ships in the library on every target except wasm32-unknown-unknown: each stage of each granule calls `Instant::now()` twice and does a global atomic `fetch_add` (about 26 scope pairs per frame, about 1% self-tax per decprof's comment), and those counters are shared across threads.
- `decode_pipelined(&[u8]) -> Vec<DecodedAudio>` takes the complete stream and returns all PCM at once (582 MB of f32 for the 27.5-minute benchmark stream), so the 2-core speedup is not available to the streaming `Mp3Decoder` API.
- The main README says '100% safe Rust on the core path', but rusty_mp3's synthesis uses `unsafe` AVX intrinsics (matrixing_avx, window_avx) and rusty_aac's SIMD is `unsafe` behind its default `simd` feature; build rusty_aac with `--no-default-features` for a fully safe scalar build.
- Main-README figures lag the crate READMEs: the MP3-encoder gap to LAME is still quoted as 0.72/1.08 ODG at 192/128 kb/s, while rusty_mp3's README re-measured 0.08/0.23 on a different corpus; MP3 VBR output was undecodable by FFmpeg through 0.4.1, so pin 0.5.0 or later.

## Known shortcomings

- Rust (language-filter mismatch); one repo holding rusty_mp3, rusty_aac and rusty_vorbis. Harnesses public (codec-bench.ps1, pinab.py, aac_vs_ffmpeg.py; Rust 1.95.0, thin LTO) but no CPU named for the audio rows and no FFmpeg flags. MP3 decode (rusty_mp3 vs FFmpeg's native decoder through the CLI) is 1.24x on one core, while the repo's own control row has FFmpeg 1.25x ahead of the serial build on two cores (derived). The AAC 5-6x (vs FFmpeg 8.1.2 native encoder) and Vorbis 5.3x (vs libvorbis) are multi-thread against single-thread; single-thread Vorbis is 1.45x slower with lower PEAQ quality.
- The MP3 one-core 1.24x pits an in-process decprof loop against the whole ffmpeg CLI run with -f null -, which also performs an fltp-to-s16 filtergraph plus pcm_s16le encode (nullenc.c) with pipeline threads sharing one core; the project's own two-core control row bounds the libavcodec decoder at 1,455 ms against serial rusty_mp3's 1,807 ms, so decoder for decoder FFmpeg is about 1.25x faster (derived) and the per-core 1.39x is a thread-count effect. The MP3 table's command, CPU, FFmpeg version and affinity masks are unpublished; codec-bench.ps1 pins one logical CPU and is video-shaped. The AAC and Vorbis encoders are batch-only (no packets before finish); the AAC PEAQ downmixes to mono so stereo rows are blind; the AAC decoder uses a naive O(N^2) f64 IMDCT (open issue #16); the profiler is always on in rusty_mp3; the crate README's 1.30x control row is really 1.25x.

## Caveats and trade-offs

Rust workspace (language-filter mismatch for a C++-first catalog); one repo holds several crates and each number belongs to one of them: MP3 decode to rusty_mp3, AAC encode to rusty_aac, Vorbis encode to rusty_vorbis; any standalone listing needs a paper: id. The only per-core speed win of substance is MP3 decode (1.24x on one physical core, about 1.13x less CPU, derived), measured against the FFmpeg CLI rather than libavcodec directly, and the README's own control row has FFmpeg 1.25x ahead of the serial rusty_mp3 build on two cores; the 1.39x two-core figure uses a two-thread pipeline. AAC's 5-6x and Vorbis's 5.3x are multi-threaded frame-parallel encodes against single-threaded encoders (different work); single-thread AAC is about 1.15x faster and single-thread Vorbis is about 1.45x slower than libvorbis, with lower PEAQ quality at matched bitrate. docs/benchmarks.md lists MP3 and AAC decode as 'not yet benchmarked' even though the READMEs carry MP3 decode numbers. Harness code is public (tools/bench/codec-bench.ps1, tools/bench/pinab.py, tools/quality/aac_vs_ffmpeg.py) but the CPU model and FFmpeg build flags for the audio rows are not stated. The earlier CLI-to-CLI comparison had MP3 decode 1.20x behind before output and profiling asymmetries were removed. Video rows are slower than FFmpeg (VP9 decode 0.16-0.21x, H.264 decode about 2x behind). AI-assisted repo (CLAUDE.md, .claude/). The Opus numbers in the README belong to the separate Remade-With-Rust/rusty-opus fork of opus-rs, not to this repo.

Pure-Rust 'FFmpeg remade' with permissive licences; codecs are also published as standalone crates (rusty_mp3, rusty_aac, rusty_vorbis, rusty_png, rusty_webp). Rust only. The AAC and Vorbis headline speedups come from multi-threaded frame-parallel encoding against single-threaded baselines. Video codecs are slower than the incumbents: VP9 decode about 0.16-0.21x of FFmpeg, VP9 encode about 0.3x at +36% bit rate, H.264 decode about 2x behind FFmpeg's native decoder, MP3 encoder about 0.7-1.1 ODG behind LAME on average (1.4-1.8 on transients).

## Maintenance

Active (394 commits; last code commit 2026-09-16, last commit a 2026-10-04 install-count banner edit), Apache-2.0, pre-1.0 with 2 open issues and 6 open dependency-bump PRs; the codec crates are small and dependency-free enough to vendor, but they were first split out and published only in July-August 2026.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers with public harnesses (tools/bench/codec-bench.ps1, tools/bench/pinab.py, tools/quality/aac_vs_ffmpeg.py) and a pinned toolchain (Rust 1.95.0, thin LTO, codegen-units 1), but no CPU model for the MP3 and AAC rows (docs/benchmarks.md gives only a '24-core box' for Vorbis), no FFmpeg build flags, and no stated command for the MP3 decode table, so not A.
- **Verifier notes:** Numbers match the README and the crate READMEs; the record's figures are accurate, but the corrections separate per-core wins (MP3 decode, slight AAC) from thread-count wins (AAC, Vorbis), name which crate and which C encoder or decoder each belongs to, and add the MP3 control row that favours FFmpeg. The language already reads Rust; verify.py apply ignores the language key. If the catalog wants a component listing, rusty_mp3 (MP3 decode vs FFmpeg) is the only candidate with a per-core claim.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/readme.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/Cargo.toml>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commits/main>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/scripts>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools/bench>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools/quality>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/docs>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_mp3>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_mp3/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_aac/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_vorbis/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/pinab.py>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/codec-bench.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/quality/aac_vs_ffmpeg.py>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/build-v3.sh>
  - <https://crates.io/api/v1/crates/rusty_mp3>
  - <https://crates.io/api/v1/crates/rusty_aac>
  - <https://crates.io/api/v1/crates/rusty_vorbis>
- **Sources the enricher read:**
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commits/main>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/issues?q=is%3Aissue>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/issues/16>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/pulls>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commits/main/crates/rusty_mp3/README.md>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/commit/55ef2d5d2e3d8cc5aa5f24a0d41cff7738686ee0>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools/bench>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/docs>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/docs/plans>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/docs/finished>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_mp3/examples>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_mp3/src>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_mp3/src/decode>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/crates/rusty_aac/src>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/readme.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/CLAUDE.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/docs/compatibility.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/docs/plans/mp3-gate-ledger.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/docs/finished/codec-aac-encoder.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/docs/finished/perf-threading.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/pinab.py>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/codec-bench.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/icount.py>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/quality/aac_vs_ffmpeg.py>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_mp3/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_mp3/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_mp3/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_mp3/src/decode/mod.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_mp3/src/decode/synthesis.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_mp3/examples/decprof.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_aac/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_aac/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_aac/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_aac/src/dsp.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_aac/src/decode.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_aac/src/encode.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_vorbis/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_vorbis/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/crates/rusty_vorbis/src/lib.rs>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/nullenc.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/allcodecs.c>
  - <https://crates.io/api/v1/crates/rusty_mp3>
  - <https://crates.io/api/v1/crates/rusty_aac>
  - <https://crates.io/api/v1/crates/rusty_vorbis>
  - <https://crates.io/api/v1/crates/rff-cli>
  - <https://crates.io/api/v1/crates/remade-ffmpeg>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/remade-with-rust/remade_ffmpeg_rs`) · [data/wave10/enrich/raw/github_com_remade_with_rust_remade_ffmpeg_rs.json](../../../data/wave10/enrich/raw/github_com_remade_with_rust_remade_ffmpeg_rs.json) (enrichment confidence 0.6)

</details>
