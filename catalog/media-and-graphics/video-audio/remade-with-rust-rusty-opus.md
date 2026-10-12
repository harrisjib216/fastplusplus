# rusty-opus

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Pure-Rust Opus codec (opus-rs performance fork) claiming 1.5-1.6x libopus single-core CELT encode speed; SILK 4% slower.

| | |
|---|---|
| **Beats** | libopus (C reference encoder); also FFmpeg's native Opus encoder |
| **Claimed result** | CELT speech 436x realtime vs libopus 291x (1.50x faster, FFmpeg native 310x); CELT stereo music 213x vs 133x (1.60x faster, FFmpeg native 71x); SILK 139x vs 145x (0.96x, libopus 4% ahead). Frame-parallel encoding adds wall-clock speedup on top. Quality: mean BD-ODG -0.015 vs libopus over 13 core classes (parity), +1.532 vs FFmpeg's native Opus encoder. |
| **Workload** | Process-level encode timing from tools/bench_encode_3way.ps1: rusty-opus via its examples/encode_ogg binary, libopus via 'ffmpeg -c:a libopus', FFmpeg's native encoder via 'ffmpeg -strict -2 -c:a opus'. Sources are corpus clips looped to 300 s and 150 s (speech_clean.wav at 48 kHz/32 kb/s audio, mus_guitar_st.wav stereo at 48 kHz/128 kb/s audio, fixtures/answer_16k.wav at 16 kHz/16 kb/s voip); the metric is the median slope t(300 s) - t(150 s) of Windows process CPU time, pinned to one core at High priority, 31 ABBA-alternated reps with a null arm; coding path (CELT or SILK) verified from TOC bytes. |
| **Metric** | throughput |
| **Hardware** | Intel i7-14650HX, Windows, x86-64 AVX2 |
| **Compiler and flags** | Not stated. Cargo release build of examples/encode_ogg with no [profile.release] override in Cargo.toml (edition 2024, rust-version 1.85, actual rustc not given); AVX2/FMA kernels selected at runtime. The libopus arm uses the ffmpeg build on PATH; its libopus version and build flags are not stated. |
| **Adoption** | 5 stars, 4 forks, 148 commits; crates.io rusty-opus 0.9.1, 34,214 downloads (crate created 2026-07-29); README banner claims 4,827 active installs (not verifiable). Opus backend of Remade-With-Rust/remade_ffmpeg_rs. |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/Remade-With-Rust/rusty-opus) · [benchmark](https://github.com/Remade-With-Rust/rusty-opus) |

## Verdict

First-party, i7-14650HX on Windows: each encoder runs as a process on looped 300 s and 150 s clips, the slope of process CPU time is taken, pinned to one core at High priority, ABBA order, 31-41 reps with a null arm: CELT 48 kHz speech at 32 kb/s 436x vs libopus 291x realtime (1.50x), CELT stereo music at 128 kb/s 213x vs 133x (1.60x), SILK 16 kHz VoIP at 16 kb/s 139x vs 145x (0.96x), with the coded path checked from TOC bytes; rustc and flags are unstated and the libopus arm is ffmpeg -c:a libopus from PATH (docs/benchmarks.md names FFmpeg 8.1.2 for its earlier run) with no libopus version or build flags. The slope cancels start-up but not FFmpeg's per-frame CLI work (WAV demux, PCM decode, filtergraph, Ogg mux and, since FFmpeg 7.0, thread hand-offs between those stages, here time-sliced on the one pinned core), speed is compared at nominal bitrate although the README says libopus's VBR overshoots by 15-20% on this corpus, and the complexity 9 vs 10 mismatch adds almost no libopus work (libopus 1.5.2 float gates nothing above complexity 8 except a fixed-point-only analysis switch); no correctness bug was found behind the numbers.

## Use it when

- Rust applications that need Opus encode and decode without a C toolchain, bindgen or cross-compiled libopus, under the same BSD-3-Clause licence as libopus.
- CELT-path encoding (48 kHz music, or speech the classifier routes to CELT, at about 32-128 kb/s) where the first-party table shows 1.50x and 1.60x libopus single-core throughput.
- Offline or batch transcoding of long files on multi-core machines, where encode_parallel trades a little extra CPU (warm-up frames per chunk) and byte-identity for wall-clock speed.
- Real-time voice or streaming stacks in Rust that need the libopus feature set (FEC, DTX, PLC, CNG, multistream surround) rather than a decode-only crate.

## Skip it when

- SILK and VoIP speech at low rates: libopus is 4% faster on the only SILK row (about 3 Windows timer quanta), Hybrid mode was not timed at all, and the README's own quality table puts the encoder behind libopus on VoIP-application speech (BD-ODG -0.200 to -0.416) and on stereo piano and guitar (-0.217, -0.162).
- C or C++ projects: there is no C API, so linking libopus directly is simpler and is the measured baseline anyway.
- When encoder output must match libopus byte for byte: decisions differ by design (zero-lookahead analysis with a 10-frame warm-up guard, opt-in tonality VBR boost, default complexity 9), and only the decoder claims bit-exact conformance on the 12 RFC vectors.
- Integer PCM pipelines or 44.1 kHz input without a resampler: the API takes f32 only and the encoder accepts 8, 12, 16, 24 or 48 kHz.
- Teams that need an engaged upstream: no issue has ever been filed, the last library change was 0.9.1 on 2026-08-08 (later commits are README install-count bumps and CI), and docs/benchmarks.md in the same repo still says SILK is 2.9x and Hybrid 2.7x slower than libopus, which the README later calls a mis-measurement and re-measures only for SILK.

## How it is fast

It is a structural port of libopus's float encoder (tonality analysis, CELT MDCT, band energy and PVQ, SILK NSQ) with hand-written SIMD kernels chosen at runtime and kept beside scalar twins: AVX/AVX+FMA CELT kernels and AVX2 pitch/PVQ/comb-filter code inherited from opus-rs, plus three byte-identical AVX2 SILK kernels the fork added (LPC short-term prediction, warped autocorrelation, cross-state NSQ noise-shaping filter), and NEON on aarch64. The CELT encoder allocates its per-frame work buffers once in CeltEncoder::new. docs/benchmarks.md says the single-thread CELT lead was already in upstream opus-rs (music 250x upstream vs 262x for the fork, with the fork's own gains on SILK/Hybrid) and warned then that the encoder's VBR was effectively CBR with less tonality/VBR analysis than libopus; the fork has since wired in the missing analysis signals, while libopus's tonality VBR boost is still opt-in (RUSTY_OPUS_TONAL_VBR). For wall-clock time, encode_parallel splits a stream into chunks on std::thread workers, each re-encoding 8 warm-up frames to prime its state (PEAQ delta-ODG &lt;= 0.03, not byte-identical).

## Compared with alternatives

Pick it over upstream opus-rs for the same API plus AVX2 SILK kernels, frame-parallel encode and the later quality fixes, and over ruopus, opus-pure or ropus when you want the full libopus feature set (FEC, DTX, PLC, multistream, repacketizer) in a crate already shipped inside remade_ffmpeg_rs. If the decision rests on a controlled libopus comparison, ropus's in-process cc-built harness and the libopus 1.6.1 baselines named by opus-pure and ruopus are better documented than this README's FFmpeg-hosted libopus of unknown version.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none at runtime; dev-dependencies criterion, proptest and rusty_alloc-api (benches and examples only) |
| **Minimum toolchain** | Rust 1.85 (rust-version in Cargo.toml), edition 2024 |
| **Platforms** | std targets; AVX/AVX2/FMA kernels on x86-64 and NEON on aarch64, runtime-detected with scalar fallbacks; benchmarked only on Windows x86-64 (i7-14650HX) |
| **Thread safety** | Not documented. Encoders and decoders are independent owned objects; encode_parallel runs one stream across std::thread workers, each with its own primed encoder (deterministic chunk boundaries, worker count defaults to available_parallelism). |
| **Drop-in for the baseline** | partial — same bitstream and libopus-style knobs (interop with libopus in both directions per the README), but a Rust API with public fields, f32-only PCM and no C ABI |

## Gotchas

- Behaviour depends on environment variables read when an encoder is built or once per process: RUSTY_OPUS_FORCE_MODE, RUSTY_OPUS_SILENCE_FLAG=0, RUSTY_OPUS_TONAL_VBR, RUSTY_OPUS_ANALYSIS_WARMUP, RUSTY_OPUS_MODE_DWELL and RUSTY_OPUS_LSB_DEPTH change the bitstream, RUSTY_OPUS_GATE_HARVEST=&lt;path&gt; makes the library append a CSV row per encoded frame to that file, and the unprefixed names CELT_PF_OFF (turns off the CELT pitch prefilter) and NO_STEREO_TRIM also apply process-wide.
- lsb_depth defaults to 24 (libopus float-API default); the source says to set 16 for s16-sourced material to match opus_demo, since the analysis noise floor depends on it.
- encode_parallel output differs from serial encoding at chunk seams, and every chunk re-encodes 8 warm-up frames, so it spends more total CPU than one serial encoder.
- Benches and examples run under the org's rusty_alloc global allocator (a dev-dependency; the library itself sets none). CHANGELOG 0.9.1 reports no measurable encode-speed change from that switch because steady-state encode reuses its buffers.

## Known shortcomings

- Rust fork of restsend/opus-rs with its own 3-way harness (tools/bench_encode_3way.ps1, i7-14650HX), so not inherited numbers. Complexity mismatch: rusty-opus defaults to 9 while ffmpeg's libopus defaults to 10; libopus version and build and the rustc version are unstated.
- The timing slope does not cancel ffmpeg's per-frame CLI work (demux, filter, Ogg mux, thread hand-offs); libopus VBR overshoots the nominal rate by 15-20%; complexity 9 against 10 costs almost nothing extra in libopus 1.5.2 float (nothing is gated above 8 except fixed-point-only analysis), so the verifier's complexity caveat is weak. The in-repo docs/benchmarks.md still says SILK 2.9x and Hybrid 2.7x slower and Hybrid was never re-timed; the CELT lead is inherited from opus-rs; the library reads environment variables that change the bitstream or write files (CELT_PF_OFF, NO_STEREO_TRIM, RUSTY_OPUS_GATE_HARVEST); last code change 0.9.1 on 2026-08-08; the README's 'Active Installs' banner is the crates.io total download count.

## Caveats and trade-offs

First-party numbers on one laptop CPU (i7-14650HX, Windows); rustc version, build flags and the libopus version/build are not stated. Settings are not matched: rusty-opus's encoder defaults to complexity 9 (src/lib.rs; encode_ogg does not change it) while FFmpeg's libopus wrapper defaults to compression_level 10 (libavcodec/libopusenc.c), so libopus runs at a higher complexity setting in the comparison; the effect on the ratio is not measured. The libopus and FFmpeg-native timings also include ffmpeg's per-sample WAV demux and Ogg mux work, which the slope does not cancel (probably small, not measured). Only three configurations are timed, two CELT and one SILK, each on one looped clip; the README tagline '\~1.5x ... measured across 18 content classes' mixes the 18-class quality corpus with the 3-configuration speed test, and on the SILK path libopus is 4% faster. The quality claim uses PEAQ ODG on short public-domain and synthetic clips, as the README itself says. Performance fork of restsend/opus-rs (not a GitHub fork) whose own AVX2 SILK/CELT kernels and harness produce numbers distinct from opus-rs's, so it does not just inherit the upstream claims. Rust, not C++. Part of Mata Network's 'Remade With Rust' initiative; README opens with an install-count banner and an advert. Script header comment still describes 60 s/30 s clips, but its defaults (300 s/150 s) match the README.

Pure Rust Opus encoder and decoder with hand-written AVX2/FMA and NEON kernels (unsafe confined to SIMD), runtime CPU detection; adds frame-parallel encoding with PEAQ-neutral seams. Rust only. Quality at parity with libopus except lower on VoIP-application speech and some stereo music classes.

## Maintenance

Code last changed with 0.9.1 on 2026-08-08 and later commits through 2026-10-04 only bump the README banner or CI; BSD-3-Clause, 5 stars, 4 forks, no issues ever filed, and the README's '35,223 Active Installs' equals the crates.io total download count (35,223), not a measured install base.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README table (436x vs 291x, 213x vs 133x, 139x vs 145x realtime) comes from the public harness tools/bench_encode_3way.ps1 on a named CPU (i7-14650HX, Windows), but the rustc version and build flags are not stated and the libopus arm is whatever ffmpeg build is on PATH (-c:a libopus) with no version or flags, so first-party C rather than A.
- **Verifier notes:** Not a copy of the opus-rs claims: opus-rs reported 2-28% wins on mono speech with a C-comparison bench missing from its repo, while rusty-opus has its own public 3-way harness and 1.50x/1.60x CELT figures, so it can stay a separate entry with is_fork_of restsend/opus-rs (orchestrator may still fold the two if one Opus-in-Rust row is preferred). Language is Rust (already set), a mismatch with the C++ language filter of the search. Opus/libopus is a wave-10 list baseline, so baseline_in_list true stands.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Remade-With-Rust/rusty-opus>
  - <https://github.com/Remade-With-Rust/rusty-opus/commits>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/tools/bench_encode_3way.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/examples/encode_ogg.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/COPYING>
  - <https://raw.githubusercontent.com/restsend/opus-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/libopusenc.c>
  - <https://crates.io/api/v1/crates/rusty-opus>
- **Sources the enricher read:**
  - <https://github.com/Remade-With-Rust/rusty-opus>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/COPYING>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/tools/bench_encode_3way.ps1>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/examples/encode_ogg.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/examples/encode_speed.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/examples/decode_bit.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/docs/benchmarks.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/src/celt.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/src/parallel.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/src/pvq.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/tests/oracle_bitexact.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/.github/workflows/portfolio-check.yml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/tools/gate_ladder.py>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty-opus/HEAD/tools/corpus_coverage.py>
  - <https://github.com/Remade-With-Rust/rusty-opus/commits/main>
  - <https://github.com/Remade-With-Rust/rusty-opus/pulls?q=is%3Apr>
  - <https://github.com/Remade-With-Rust/rusty-opus/issues?q=is%3Aissue>
  - <https://github.com/Remade-With-Rust/rusty-opus/tree/main/.github/workflows>
  - <https://github.com/Remade-With-Rust/rusty-opus/tree/main/tests>
  - <https://github.com/Remade-With-Rust/rusty-opus/tree/main/examples>
  - <https://github.com/Remade-With-Rust/rusty-opus/tree/main/docs>
  - <https://raw.githubusercontent.com/xiph/opus/v1.5.2/src/opus_encoder.c>
  - <https://raw.githubusercontent.com/xiph/opus/v1.5.2/celt/celt_encoder.c>
  - <https://raw.githubusercontent.com/xiph/opus/v1.5.2/celt/bands.c>
  - <https://raw.githubusercontent.com/xiph/opus/v1.5.2/silk/control_codec.c>
  - <https://crates.io/api/v1/crates/rusty-opus>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/remade-with-rust/rusty-opus`) · [data/wave10/enrich/raw/github_com_remade_with_rust_rusty_opus.json](../../../data/wave10/enrich/raw/github_com_remade_with_rust_rusty_opus.json) (enrichment confidence 0.7)

</details>
