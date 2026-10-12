# rusty_flac

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Pure-Rust FLAC encoder and decoder claiming 17% faster encode and 23% faster decode than FFmpeg 8.1.2's flac.

| | |
|---|---|
| **Beats** | FFmpeg 8.1.2 native flac encoder and decoder (libavcodec) |
| **Claimed result** | Single-core, pinned, CPU time on one 180 s 44.1 kHz stereo music clip against FFmpeg 8.1.2's native flac: encode at -compression_level 8 672 ms vs 813 ms (0.83x, 17.3% faster), decode of an FFmpeg-encoded stream 266 ms vs 344 ms (0.77x, 22.7% faster), 31/31 paired wins on both (z = 5.57 is the sign-test value for 31/31). Smaller-file claim (20 of 20 gate combos, e.g. stereo guitar s24 L8 539,087 vs 565,122 bytes) is inflated: FFmpeg's flac muxer writes an 8,192-byte PADDING block by default (libavformat/flacenc.c, metadata_header_padding = -1 becomes 8192) plus a Vorbis comment, which flac_gate.ps1 does not disable, while rusty_flac writes only fLaC + STREAMINFO. Subtracting roughly 8.2 KB of metadata (derived from page data): guitar s24 about -3.2% and piano s16 about -1.1% remain, but pink noise s24 (delta 8,100 B), vocal s16 (8,024 B) and silence (7,964 B) become ties or slightly larger for rusty_flac. |
| **Workload** | Single-core comparison, both binaries pinned to one core at High priority, ABBA-alternated, 31 pairs, on a 180 s 44.1 kHz stereo music clip (guitar, piano, vocal): encode at -compression_level 8, and decode of an FFmpeg-encoded stream. Per the README, outputs are verified lossless before timing; the public tools/flac_gate.ps1 checks lossless round trips in both directions (SHA-256 of decoded PCM) and sizes on 10 clips x levels 5 and 8, but the timing harness itself is not published. |
| **Metric** | throughput |
| **Hardware** | CPU model not stated ('single core, this machine'). The gate script's default FFmpeg path is a Windows Gyan 'ffmpeg-8.1.2-full_build' package, so the box is a Windows x86-64 PC (inferred); four AVX2 kernels are runtime-detected. |
| **Compiler and flags** | Not stated for the timed builds. Cargo.toml only sets edition 2021 and rust-version 1.85 (minimum); no RUSTFLAGS or target-cpu are given. FFmpeg arm is the prebuilt Gyan 'ffmpeg-8.1.2-full_build' Windows binary (default path in remade_ffmpeg_rs tools/flac_gate.ps1). |
| **Adoption** | 1 star, 0 forks; crates.io rusty_flac 1,348 total downloads (0.1.0 on 2026-08-13 to 0.2.0 on 2026-09-30); README claims 321 active installs via one downstream app (RAG Converter), not verifiable |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/Remade-With-Rust/rusty_flac) · [benchmark](https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/README.md) |

## Verdict

First-party README numbers on an unnamed Windows x86-64 machine with an unstated rustc and flags: both binaries pinned to one core, process CPU time, 31 ABBA pairs on one 180 s 44.1 kHz stereo music clip, encode at -compression_level 8 672 ms vs 813 ms and decode of an FFmpeg-encoded stream 266 ms vs 344 ms against the prebuilt Gyan FFmpeg 8.1.2 full_build. The timing harness, the clip and the command lines are still not public (remade_ffmpeg_rs tools/bench holds only codec-bench.ps1, pinab.py and unrelated scripts on 2026-10-04), so it is unknown whether process start-up, WAV/file I/O and, for the FFmpeg arm, the per-frame hand-offs between the demux, decode, filter, encode and mux threads that FFmpeg 7.0+ runs (all time-sliced on the one pinned core) are cancelled, as the sister rusty-opus harness's 300 s minus 150 s slope does for start-up; the smaller-file claim mostly reflects FFmpeg's default padding block, and level 8 means different search work in the two encoders.

## Use it when

- Rust services, desktop apps or WASM builds that need FLAC encode and decode with no C toolchain and no LGPL code (Apache-2.0); RAG Converter uses it in the browser.
- no_std microcontroller encoders: the README reports about 15-20 ms per 4,096-sample 16 kHz mono block on an ESP32-S3 at 240 MHz and a byte-gated peak heap of about 124 KB for an 8,192-sample stream (first-party).
- Whole-file encoding of 8/16/24-bit PCM (up to 8 channels) that libFLAC or FFmpeg will later decode; round trips are gated against claxon in tests and against FFmpeg in remade_ffmpeg_rs tools/flac_gate.ps1.
- Devices that close one file per chunk (for example one second of audio): Encoder::finish_and_reset keeps buffers and window tables and gives bytes identical to a fresh encoder.
- Decoding trusted 16- or 24-bit FLAC already in memory from Rust code that previously used claxon.

## Skip it when

- C or C++ projects: there is no C API, so you would need an FFI shim, and the comparison was against FFmpeg's flac, not libFLAC, which was never timed.
- Untrusted input through decode(): it reserves Vec::with_capacity(total_samples) per channel straight from the 36-bit STREAMINFO field. Issue #9 (a 42-byte stream can request 80 GB and abort the process) was closed on 2026-09-15, but that line is still in src/decode.rs at HEAD (v0.2.0). Use Decoder::next_frame with your own bounded buffers, or check total_samples against the input length first.
- Real-world files with ID3v2 prefixes, trailing tags or damaged frames, or Ogg FLAC: the decoder requires fLaC at byte 0, a bad sync, CRC-8 or CRC-16 returns an error, and decode() gives up on the whole stream instead of resynchronising.
- 32-bit FLAC: the README says 4-32-bit decode, but 32-bit stereo side channels need 33 bits while BitReader::read_bits/read_signed are written for n &lt;= 32 and samples are i32. The gate matrix tests only 8, 16 and 24 bits, and 32-bit encode is a roadmap item.
- Large or streaming jobs and tagging workflows: the encoder holds the whole input as i32 before finish(), the decoder needs the whole file in memory, there is no seeking, and no seek table, Vorbis comment, picture or padding block is written.

## How it is fast

The encoder does a two-phase, estimate-gated search per fixed 4,096-sample block: every stereo arm (left, right, mid, side) gets a cheap estimate (exact integer autocorrelation over Q15 Tukey windows 0.5 and 0.2, Levinson-Durbin, one-pass fixed-order |residual| sums), and only arms whose stereo mode is within a margin of the best estimate are realized with real residuals and an exact Rice plan. The Rice planner merges partition sums bottom-up so every partition order (to 8) and both Rice and Rice2 are costed in one pass instead of a per-parameter scan, and four runtime-detected AVX2 kernels (autocorrelation, Rice sums, fixed-order sums, FMA LPC residual) sit beside scalar twins; an accumulator bit writer, table CRCs and an unrolled MD5 cut the rest. The decoder uses a 64-bit left-aligned bit reader refilled a word at a time, leading_zeros Rice reads with one refill, and const-generic LPC restore loops for orders 1-12. FFmpeg's level 8, by contrast, uses 4,608-sample blocks at 44.1 kHz, Levinson LPC with its 4-level order search and an estimated stereo mode (libavcodec/flacenc.c), so the two encoders search different spaces.

## Compared with alternatives

Pick it over Symphonia (decode-only, multi-format, single-threaded tables against FFmpeg's native decoders) or flacenc-rs (encoder only, measured against the libFLAC flac 1.4.3 CLI) when you want one dependency-free Apache-2.0 crate that both encodes and decodes FLAC, including no_std encoding on a microcontroller. For decoding untrusted or messy real-world files, or when the comparison you care about is libFLAC rather than FFmpeg's flac, those siblings or libFLAC itself are the safer choice.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none required; optional libm (pure Rust) for no_std; dev-dependencies claxon and rusty_alloc-api |
| **Minimum toolchain** | Rust 1.85 (rust-version in Cargo.toml), edition 2021 |
| **Platforms** | any Rust target; Windows, Linux and macOS build and test per the README; no_std checked in CI on riscv32imac-unknown-none-elf and thumbv7em-none-eabihf; runs on ESP32-S3; AVX2/FMA kernels only on x86-64 with the std feature (runtime-detected) |
| **Thread safety** | Not documented. Encoder and Decoder own their scratch buffers (the old thread-local pools were folded into each encoder) and the crate has only constant tables, so separate instances can run on separate threads; encoding of one stream is single-threaded. |
| **Drop-in for the baseline** | partial — the rff CLI of remade_ffmpeg_rs replaces ffmpeg's FLAC encode and decode with this code; as a library it is a different API from libavcodec or libFLAC |

## Gotchas

- Output carries only STREAMINFO (no Vorbis comment, no padding), so tag editors must rewrite the whole file; that missing 8,192-byte PADDING block is most of the README's 'smaller on 20/20' headline against FFmpeg.
- Encoded bytes changed in 0.2.0 (integer autocorrelation); the CHANGELOG says to pin one version wherever two builds must agree byte for byte, and to enable the libm feature on the host for host-chip byte identity.
- The decoder parses the STREAMINFO MD5 but never computes it; only frame CRC-8 and CRC-16 are checked.
- unsafe is confined to four #[target_feature(enable = "avx2")] kernels, each with a bit-identity test against its scalar twin; the in-repo flacbench example hard-codes 44,100 Hz and runs under the org's rusty_alloc global allocator, which the project says is required for comparable numbers.

## Known shortcomings

- Rust (language-filter mismatch). Downgraded to C: README times (672/813 ms encode, 266/344 ms decode, single core each) have no CPU model, compiler or flags, the FLAC timing harness and clip are unpublished, and all four times are exact multiples of the 15.625 ms Windows tick. The 'smaller on 20/20' claim is inflated by FFmpeg's default 8,192-byte PADDING block (libavformat/flacenc.c in FFmpeg 8.1); pink noise, vocal and silence are not smaller once it is removed. Lossless interoperability is gated by the public flac_gate.ps1.
- The FLAC timing harness is still unpublished (remade_ffmpeg_rs tools/bench as of 2026-10-04), so whether start-up, I/O and FFmpeg 7+ CLI thread hand-offs on the pinned core were cancelled is unknown, and the encoders do a different level-8 search (FFmpeg 4608-sample blocks with 4LEVEL order search). Security: issue #9 (a 42-byte stream causing an 80 GB allocation and abort) was closed on 2026-09-15 but decode() still does Vec::with_capacity(total_samples) at HEAD v0.2.0. 32-bit stereo (33-bit side channel) is not handled (read_bits n of 32 or less into i32; tests gate 8, 16 and 24 bits only); no resync on a bad frame; no ID3; MD5 is never checked; only STREAMINFO is written. The README's 'Active Installs' banner is the crates.io total download count.

## Caveats and trade-offs

Rust crate, not C++ (wave language filter mismatch). First-party claim: CPU model, compiler and rustc flags are not stated, and the pinned ABBA CPU-time harness for FLAC is not identifiable in remade_ffmpeg_rs tools/bench (pinab.py reads a self-reported time with a kbps argument; codec-bench.ps1 is a video-frame harness), so its command lines (for example whether FFmpeg got -threads 1) are unknown. Like-for-like on threading: both arms are pinned to one core and FFmpeg's flac encoder is single-threaded; FFmpeg's flac decoder has frame threading (AV_CODEC_CAP_FRAME_THREADS), so without -threads 1 any extra FFmpeg threads would share the pinned core and add overhead to the FFmpeg decode arm. All four timing figures are integer multiples of the Windows 15.625 ms CPU-time tick (43, 52, 17 and 22 ticks, derived from page data), the clock the group's own codec-bench.ps1 calls tick accounting rather than a clock; the gaps are 9 and 5 ticks, so the direction is plausible but each ratio has about 2-6% resolution. Single 180 s clip for speed; the timed clip and the corpus are not published. Compression levels do not do the same work: rusty_flac's level maps to LPC order only with estimate-gated search, FFmpeg's level 8 uses its own order-search method. The smaller-file claim is inflated by FFmpeg's default 8,192-byte PADDING block (see claimed_speedup); on pink noise, vocal and silence rusty_flac's audio payload is not smaller. The baseline is FFmpeg's flac, not the reference libFLAC, which was not tested. Lossless interop is gated in public code (flac_gate.ps1) on 20 clip-level combos. Young project with rapid release churn (48 commits, v0.2.0 on 2026-09-30).

Pure Rust (no_std plus alloc capable, unsafe only in four AVX2 kernels with scalar twins), no C API, so C++ use needs an FFI shim. FLAC subset with LPC orders up to 12. Part of the Remade With Rust ecosystem, which also ships remade_ffmpeg_rs.

## Maintenance

Active but very young (49 commits, last commit 2026-10-04 bumping the README banner, v0.2.0 on 2026-09-30, a v0.2.1 release PR open); Apache-2.0 and dependency-free, so easy to vendor, but it has 1 star and the README's '1,358 Active Installs' banner equals the crates.io total download count (1,358), not a measured install base.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README numbers (672 vs 813 ms encode, 266 vs 344 ms decode, 31/31, z = 5.57) with no CPU model, compiler or flags, and the FLAC timing harness, its command lines and the timed 180 s clip are not published (remade_ffmpeg_rs tools/flac_gate.ps1 only covers interop and size; corpus/ is not in the repo). Tier stays C; the downgrade is for the overstated smaller-file claim.
- **Verifier notes:** Speed numbers are on the README and plausible but first-party and tick-quantized; the 20/20 smaller-file headline largely reflects FFmpeg's default 8 KiB metadata padding, verified in FFmpeg 8.1 libavformat/flacenc.c and rusty_flac src/encode.rs. Language is Rust, outside the C++ filter. Unlike other Remade-With-Rust repos, this one compares single core against single core.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/README.md>
  - <https://github.com/Remade-With-Rust/rusty_flac>
  - <https://github.com/Remade-With-Rust/rusty_flac/commits>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/examples/flacbench.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/src/encode.rs>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools/bench>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/flac_gate.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/pinab.py>
  - <https://raw.githubusercontent.com/Remade-With-Rust/remade_ffmpeg_rs/main/tools/bench/codec-bench.ps1>
  - <https://crates.io/api/v1/crates/rusty_flac>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/8.1/libavformat/flacenc.c>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/8.1/libavformat/options_table.h>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/8.1/libavformat/version.h>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/8.1/libavcodec/flacdec.c>
- **Sources the enricher read:**
  - <https://github.com/Remade-With-Rust/rusty_flac>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/src/encode.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/src/decode.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/src/bitio.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/src/md5.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/tests/gates.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/examples/flacbench.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/examples/corpus_size.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/docs/plans/esp32-encoder-cost.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_flac/HEAD/LICENSE>
  - <https://github.com/Remade-With-Rust/rusty_flac/issues?q=is%3Aissue>
  - <https://github.com/Remade-With-Rust/rusty_flac/issues/9>
  - <https://github.com/Remade-With-Rust/rusty_flac/pulls?q=is%3Apr>
  - <https://github.com/Remade-With-Rust/rusty_flac/commits/main>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools>
  - <https://github.com/Remade-With-Rust/remade_ffmpeg_rs/tree/main/tools/bench>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/release/8.1/libavcodec/flacenc.c>
  - <https://crates.io/api/v1/crates/rusty_flac>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/remade-with-rust/rusty_flac`) · [data/wave10/enrich/raw/github_com_remade_with_rust_rusty_flac.json](../../../data/wave10/enrich/raw/github_com_remade_with_rust_rusty_flac.json) (enrichment confidence 0.7)

</details>
