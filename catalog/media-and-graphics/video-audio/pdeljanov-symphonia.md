# Symphonia

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MPL-2.0` · 🟢 active

> Pure, safe-Rust audio demuxing and decoding library; beats single-threaded libavcodec on FLAC, ALAC, MP1/MP2, high-bitrate MP3.

| | |
|---|---|
| **Beats** | FFmpeg libavcodec native decoders (FLAC, ALAC, MP1, MP2, MP3, AAC-LC, Vorbis, ADPCM), single-threaded, built as the static 'ffbench' example from a pdeljanov/FFmpeg fork |
| **Claimed result** | Relative decode time Symphonia/FFmpeg (below 1.0 means Symphonia is faster). i7-4790K: FLAC 0.71-0.74, ALAC 0.73-0.79, MP1 0.45-0.48, MP2 0.60, MP3 320 kbps 0.84, ADPCM IMA 0.83. M1 Pro: FLAC 0.51-0.64, ALAC 0.77-0.81, MP1 0.63-0.64, MP2 0.72-0.77, ADPCM MS 0.59, MP3 320 kbps 0.81. Raspberry Pi 4B: FLAC 0.96-1.04, ALAC 0.81-0.88, MP1 0.83-0.87, MP2 0.91-0.93, MP3 320 kbps 0.95, ADPCM MS 0.96. Slower than FFmpeg on AAC-LC (1.10-1.27), Vorbis (1.05-1.24) and MP3 128 kbps (1.00-1.07) everywhere, and on ADPCM MS on the i7-4790K (1.13) and ADPCM IMA on the M1 Pro (1.51) and Pi (1.05). The README summarises this as 'generally +/-15%' of FFmpeg. |
| **Workload** | Single-thread decode-only of one or two real audio files per codec (44.1/48/96 kHz), timed with hyperfine (30 runs after 3 warmups), on an Intel Core i7-4790K, an Apple M1 Pro and a Raspberry Pi 4B. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4790K 4C/8T @ 4.0 GHz; Apple M1 Pro (8 Firestorm + 2 Icestorm cores); Raspberry Pi 4B (Broadcom BCM2711, Cortex-A72 @ 1.5 GHz) |
| **Compiler and flags** | Symphonia built with rustc 1.67.0 and RUSTFLAGS='-C target-cpu=native', SIMD enabled. FFmpeg built with a plain './configure' (compiler version and flags not stated). |
| **Adoption** | 3.4k stars |
| **Last commit** | 2026-08-13 |
| **Links** | [repository](https://github.com/pdeljanov/Symphonia) · [benchmark](https://raw.githubusercontent.com/pdeljanov/Symphonia/main/BENCHMARKS.md) |

## Verdict

BENCHMARKS.md (first-party, 2023-02-03) times whole-process hyperfine runs (30 after 3 warmups) of symphonia-play --decode-only (rustc 1.67.0, target-cpu=native) against a statically linked FFmpeg ffbench example (plain ./configure, compiler unstated) on an i7-4790K, an M1 Pro and a Pi 4B, using one or two unpublished files per codec. Symphonia needs 0.45-0.84x FFmpeg's time for MP1/MP2/FLAC/ALAC/320 kbps MP3 on x86 and M1 but loses on AAC-LC and Vorbis. From the code, ffbench uses default decoder options (one thread) and discards frames, and decode-only mode decodes with verification off and gapless trimming on, logging and skipping decode errors; PCM/WAV rows, where an FFmpeg developer reported Symphonia 1.5-2x slower in issue #179, are not in the table.

## Use it when

- Rust applications decoding FLAC, ALAC, MP1/MP2 or 320 kbps MP3 on x86-64 or Apple silicon, where the published table shows 0.45-0.84x of single-threaded FFmpeg's decode time.
- Services that parse untrusted media and want memory safety: symphonia-core is #![forbid(unsafe_code)] and the project fuzzes its demuxers.
- Players needing gapless playback and tag reading in one dependency (FLAC, MP3, Vorbis, ALAC, ADPCM, PCM gapless; WAV, AIFF and OGG gapless demuxing).
- Builds that want to avoid linking FFmpeg: MPL-2.0, a handful of pure-Rust dependencies, and per-codec feature flags to keep the binary small.

## Skip it when

- AAC-LC or Vorbis heavy workloads: 1.10-1.27x and 1.05-1.24x FFmpeg's time in the 2023 table; 128 kbps MP3 is at parity to 7% slower.
- Low-power ARM such as a Raspberry Pi 4: margins shrink to 0.81-0.96 and 16-bit FLAC is 4% slower than FFmpeg.
- Opus, HE-AAC, WavPack, video, encoding or resampling: not implemented (Opus and HE-AAC only through third-party adapters that wrap libopus and libfdk-aac).
- C or C++ codebases: there is no C API, so you need a Rust toolchain and your own FFI shim; libavcodec, dr_flac or minimp3 integrate directly.
- Multi-threaded decoding of one FLAC or ALAC stream: Symphonia decoders use one thread, while FFmpeg can frame-thread those codecs (BENCHMARKS.md footnote).

## How it is fast

The decoders are written so LLVM can auto-vectorize them: the FLAC LPC predictor is a const-generic function specialised for maximum orders 4, 6, 8, 10, 12 and 32, so the common subset orders run fixed-length i64 multiply-accumulate loops. AAC, Vorbis and MP3 compute the IMDCT through an N/2-point complex FFT, backed by rustfft's SSE/AVX/NEON kernels when the default opt-simd features are on. The README warns that speed depends strongly on the rustc version and target CPU because it relies on these LLVM optimisations.

## Compared with alternatives

Pick Symphonia when you want one safe-Rust library that both demuxes and decodes many formats. For a single codec, rusty_flac (FLAC against FFmpeg 8.1.2) or minimp3/nanomp3 (MP3, from C or Rust) are narrower and easier to embed from C/C++.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | lazy_static, log, smallvec, bitflags, bytemuck, num-complex; rustfft (optional, pulled in by the default opt-simd features) |
| **Minimum toolchain** | Rust 1.85, edition 2024 (0.6.x); 0.5.x needs Rust 1.53 |
| **Platforms** | any Rust target; SIMD FFT paths for x86 SSE/AVX and ARM NEON; benchmarked on x86-64 (i7-4790K), Apple M1 Pro and Cortex-A72 (Raspberry Pi 4B) |
| **Thread safety** | FormatReader and AudioDecoder are Send + Sync trait objects, one per stream; each decoder runs on a single thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Default features enable only royalty-free formats (FLAC, Vorbis, ADPCM, PCM, WAV, OGG, MKV): AAC, ALAC, MP1/MP2/MP3, ISO/MP4, AIFF and CAF need the aac, alac, mpa, isomp4, aiff, caf or all features. The README table lists opus and wavpack as default features, but they are neither in Cargo's default list nor implemented.
- 0.6.0 (2026-05-15) is a breaking API redesign with MSRV 1.85; 0.5 code needs the migration guide.
- Safe Rust prevents memory corruption but not panics: open fuzzing reports #559 (index out of bounds on a fragmented MP4 trun) and #560 (unreachable!() on an lpcm sample entry), both in the isomp4 demuxer, so isolate or catch_unwind when parsing hostile files.
- The published numbers use RUSTFLAGS=-C target-cpu=native; a generic distribution build was not measured and may be slower, since the decoders rely on auto-vectorisation.

## Known shortcomings

- Rust (language-filter mismatch). BENCHMARKS.md ratios against FFmpeg's decoders match and ffbench.c confirms FFmpeg ran single-threaded, but FFmpeg's compiler and the input files are unstated, so C; Symphonia loses the ADPCM rows and wins 10 of 16 rows on the Raspberry Pi.
- Whole-process timings with decode-only skipping decode errors and gapless on; the PCM/WAV rows disappeared after issue #179, where an FFmpeg developer reported Symphonia 1.5-2x slower there; the table predates the v0.5.4 and 0.6 speedups, so it is stale. No C API; open isomp4 fuzz panics #559 and #560.

## Caveats and trade-offs

Rust library, not C++ (wave language filter mismatch). First-party results, so tier C: the test files come from the author's personal media library (not published) and only one or two files are used per codec, which the page itself says favours the decoders it was tuned on. The page was last updated 2023-02-03 (rustc 1.67.0, development main of both projects at that date), long before the current v0.6.1, so the numbers may be stale. The FFmpeg C compiler, version and flags are not stated (plain ./configure). Timings are whole-process hyperfine wall times (startup and demuxing included for both; ffbench is statically linked). Results are mixed: Symphonia loses on AAC-LC, Vorbis and MP3 128 kbps everywhere and on ADPCM on some CPUs, and wins mainly on FLAC, ALAC, MP1 and MP2; on the Raspberry Pi the margins are small (10 of 16 rows faster, 0.81-0.96). Like-for-like single thread: ffbench.c opens the decoder with avcodec_open2(dec_ctx, dec, NULL), so libavcodec's default of one thread applies even for FLAC and ALAC, which support frame threading.

Pure Rust audio decoding and demuxing library, no C API yet (listed as planned), so using it from C++ needs a hand-written FFI shim. Decode only, no encoders. Needs a recent rustc, and the README says performance depends strongly on compiler version because the decoders rely on auto-vectorization.

## Maintenance

Actively maintained (v0.6.1 on 2026-08-13, about 15.7 million crates.io downloads), MPL-2.0 and usable as a crate today. The benchmark table predates the v0.5.4 'major optimizations for AAC, FLAC, MP3, and Vorbis' and the 0.6.0 decoding speedups, so current ratios are unmeasured.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** BENCHMARKS.md (2023-02-03) is first-party. The harness is public (hyperfine command, symphonia-play --decode-only, pdeljanov/FFmpeg symphonia-ffbench doc/examples/ffbench.c), CPUs are named and rustc 1.67.0 with -C target-cpu=native is given, but the FFmpeg compiler, version and flags are not stated and the test files are the author's unpublished media, so it falls short of A.
- **Verifier notes:** All quoted ratios match BENCHMARKS.md; I added the omitted ADPCM losses (i7 ADPCM MS 1.13, M1 ADPCM IMA 1.51, Pi ADPCM IMA 1.05) and fixed the claim that it loses on most Pi codecs (it wins 10 of 16 rows there). FFmpeg single-threaded confirmed from ffbench.c. Language is Rust, outside the C++ filter.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/README.md>
  - <https://github.com/pdeljanov/Symphonia>
  - <https://github.com/pdeljanov/Symphonia/commits>
  - <https://raw.githubusercontent.com/pdeljanov/FFmpeg/symphonia-ffbench/doc/examples/ffbench.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/README.md>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/Cargo.toml>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/symphonia/Cargo.toml>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/symphonia-core/Cargo.toml>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/symphonia-core/src/lib.rs>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/symphonia-core/src/codecs/audio.rs>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/symphonia-core/src/formats/mod.rs>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/symphonia-core/src/dsp/mdct.rs>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/symphonia-core/src/dsp/fft/mod.rs>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/symphonia-bundle-flac/src/decoder.rs>
  - <https://raw.githubusercontent.com/pdeljanov/Symphonia/main/symphonia-play/src/main.rs>
  - <https://raw.githubusercontent.com/pdeljanov/FFmpeg/symphonia-ffbench/doc/examples/ffbench.c>
  - <https://github.com/pdeljanov/Symphonia/tree/main/symphonia-core/src/dsp>
  - <https://github.com/pdeljanov/Symphonia/tree/main/symphonia-bundle-flac/src>
  - <https://github.com/pdeljanov/Symphonia/issues?q=is%3Aissue+performance>
  - <https://github.com/pdeljanov/Symphonia/issues?q=is%3Aissue+is%3Aopen+panic>
  - <https://github.com/pdeljanov/Symphonia/issues/308>
  - <https://github.com/pdeljanov/Symphonia/issues/179>
  - <https://github.com/pdeljanov/Symphonia/issues/269>
  - <https://github.com/pdeljanov/Symphonia/releases>
  - <https://crates.io/api/v1/crates/symphonia>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/pdeljanov/symphonia`) · [data/wave10/enrich/raw/github_com_pdeljanov_symphonia.json](../../../data/wave10/enrich/raw/github_com_pdeljanov_symphonia.json) (enrichment confidence 0.8)

</details>
