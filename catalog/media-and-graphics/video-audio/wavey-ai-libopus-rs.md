# libopus-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🔴 abandoned

> Archived pure-Rust Opus CELT-only codec (48 kHz); encodes 1-2% faster than trunk libopus at 5 ms, 192-320 kb/s.

| | |
|---|---|
| **Beats** | libopus, Opus trunk commit 03647f524a40b05a1898522e92033810b58103c7 (static .libs/libopus.a from an autotools tree; configure flags not recorded), called through the full opus_encode/opus_encode24 and opus_decode/opus_decode24 API |
| **Claimed result** | Encode 1.19-2.36% less time than trunk libopus in all 12 aggregate cells (e.g. 16-bit CBR 192 kb/s: 371.9 ms vs 380.9 ms per 40 s of audio); Rust encoder 96.8-107.6x realtime. The decode lead (1.50-4.64%) is withdrawn by the author's 2026-08-25 same-packet re-test (+0.51% on C packets, -0.30% on Rust packets, +0.10% combined): parity. The encode margin is the same order as the run-to-run drift (about 0.5 percentage points) and the Rust side skips libopus's MLP/GRU analysis classifier. |
| **Workload** | 48 kHz stereo CELT-only, 5 ms (240-sample) frames, OPUS_APPLICATION_AUDIO, fullband, complexity 10, 16-bit and 24-bit PCM, CBR and constrained VBR at 192/256/320 kb/s. Direct in-process encode and decode of four 10 s excerpts from the private SoundKit diverse-v1 corpus. A 5 s warm-up, three alternating Rust/C rounds of seven internal repeats, the median per source, and four source medians summed per cell (40 s of audio). The C side runs the full Opus encoder/decoder layer (opus_encode with OPUS_SIGNAL_MUSIC). The Rust side runs the crate's own CELT-only raw-frame Encoder/Decoder. |
| **Metric** | throughput |
| **Hardware** | GCP c4-highcpu-4 (4 vCPUs), Intel Xeon Platinum 8581C; measured processes pinned to CPU 2 with taskset; one x86 host only |
| **Compiler and flags** | Rust 1.97.1 / Cargo 1.97.1: release mode, ThinLTO, codegen-units=1, -C target-cpu=native. C driver tools/raw_celt_bench.c: GCC 12.2.0, -O3 -DNDEBUG -march=native, linked against the static libopus.a from the trunk commit. The libopus library's own configure string (optimisation level, intrinsics, --enable-float-approx) is recorded as unavailable. The final timing JSON records both build-flag fields as unknown because the binaries were reused. |
| **Adoption** | 0 stars, 0 forks, 53 commits; archived 2026-08-25. crates.io libopus-rs 0.0.2 (2026-06-30, before the benchmarked August checkpoint), 4,277 downloads. |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/wavey-ai/libopus-rs) · [benchmark](https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/performance-results/2026-08-24-native-48k/README.md) |

## Verdict

Encode: on four 10 s excerpts from a private music corpus (48 kHz stereo CELT, 5 ms frames, complexity 10, 16- and 24-bit, CBR and constrained VBR at 192/256/320 kb/s), Rust used 1.19-2.36% less time than trunk libopus 03647f5. The C side was a static libopus.a with an unrecorded configure, driven through opus_encode with OPUS_APPLICATION_AUDIO. The run used one GCP c4-highcpu-4 Xeon Platinum 8581C pinned to CPU 2, with three alternating rounds of seven repeats. Decode results moved between checkpoints with no decoder change, which the report calls normal variance: about 0.5 points weighted and about 1 point at the ends of the per-cell range, the same order as the encode margin. The catalogued 1.50-4.64% decode lead is superseded by the author's same-packet re-test, which shows parity (+0.10%).

## Use it when

- Pure-Rust builds that cannot link C and need 48 kHz stereo music encoding at 192-320 kb/s with 5 ms frames (low-latency streaming), with measured quality parity to trunk libopus: ViSQOL MOS-LQO 4.5731 vs 4.5724 on 240 round trips.
- Signed 24-bit pipelines: encode_i24/decode_i24 take sign-extended i32 samples directly, so audio never passes through 16-bit PCM.
- Projects that require #![forbid(unsafe_code)] in the codec crate itself; all unsafe code sits in a separate audited kernel crate with documented invariants (SAFETY.md).
- As reference code for the successor wavey-ai/soundkit (soundkit-opus 0.13.0 on crates.io), which carries the same codec, newer fixes and the corrected decoder measurement.

## Skip it when

- Speech or low-bitrate VoIP (SILK/hybrid), sample rates other than 48 kHz, Ogg Opus files, packet-loss concealment, FEC, multistream or multi-frame packets: the decoder returns Error::Unimplemented for anything but single-frame fullband CELT-only packets.
- If you want faster decoding: the author's 2026-08-25 correction (soundkit-opus report) found the 1.50-4.64% decode lead came from timing each decoder on its own encoder's packets. On identical packets (i24, 192 kb/s constrained VBR) Rust was +0.51% slower on C packets, -0.30% on Rust packets and +0.10% combined, which is parity.
- Other frame sizes or bitrates: no current numbers exist outside the 5 ms, 192-320 kb/s cells. The README's older full-matrix snapshot on a synthetic fixture had Rust slower in nearly every cell (often 10-65% on encode and 50-160% on decode). In the browser WASM comparison, Rust encoding was slower than libopusjs (81-82x vs 110.9x realtime at 128 kb/s).
- Production deployments: the repo is archived, both crates.io releases are yanked, and the README calls the encoder experimental and 'not production replacements for libopus'.
- Non-x86 hosts: the native result covers one Xeon Platinum 8581C only; the report says AArch64 and WASM parity are not established.

## How it is fast

It is a close port of libopus's CELT pipeline (MDCT, PVQ/CWRS band quantization, energy coding, pitch prefilter and the tonality analysis) in safe Rust using the `wide` SIMD crate. Profiler-chosen unsafe kernels sit behind checked wrappers in an in-tree crate: an AVX2/FMA pitch correlation with a static tail mask, unchecked-index MDCT rotations, a pulse-cache lookup, a stereo 24-bit deemphasis kernel and an AArch64 NEON radix-5 FFT. Allocation-free scratch buffers do the rest. Each of these changes was accepted by an alternating A/B and was worth about 0.1-0.7%. Part of the margin is less work or different builds, not better code. The Rust analysis port leaves out libopus's MLP/GRU speech/music classifier (compute_dense/compute_gru in analysis.c). The i16 decode path hard-clamps instead of soft-clipping. Rust was built with -C target-cpu=native, ThinLTO and one codegen unit, while the libopus.a build flags were not recorded.

## Compared with alternatives

Pick it over opus-pure, ruopus, opus-rs or ropus only for 48 kHz stereo music at 192-320 kb/s with 5 ms frames, 24-bit I/O and published perceptual-parity data against trunk libopus. Even then, prefer its successor soundkit-opus. Those siblings implement SILK/hybrid and claim larger margins against libopus 1.6.1 or 1.5.2, and opuspp is the C++ choice for decode speed.

## Integration

| | |
|---|---|
| **Form** | crate (rlib/cdylib; optional wasm feature via wasm-bindgen; an npm/WASM build exists) |
| **Dependencies** | wide 0.7; in-tree path crate libopus-rs-kernels (publish = false); optional wasm-bindgen 0.2 |
| **Minimum toolchain** | Rust edition 2021; no MSRV declared; the benchmark used Rust 1.97.1 |
| **Platforms** | any Rust target with scalar fallbacks; x86-64 AVX2+FMA pitch kernel (runtime-checked), AArch64 NEON FFT kernel, wasm32 simd128 build; measured only on x86-64 |
| **Thread safety** | not documented; Encoder and Decoder are owned values used through &mut self, and the CELT mode tables are shared immutable statics |
| **Drop-in for the baseline** | no |

## Gotchas

- Both crates.io releases (0.0.1 and 0.0.2) are yanked, and 0.0.2 (2026-06-30) predates the kernel crate and the August optimizations. Building from git needs the in-tree crates/libopus-rs-kernels path crate; for new work, use soundkit-opus.
- decode_i16 converts with a hard clamp (float_to_i16), while libopus's opus_decode in float builds soft-clips (OPTIONAL_CLIP=1; opus_decode24 does not). Output differs on hot masters, and the extra C pass is consistent with the 16-bit decode lead (3.55-4.64%) being about twice the 24-bit one (1.50-1.97%).
- The 'packet identity gate' is weak. packet_checksum hashes only each packet's length and first and last bytes, and the decode checksum sums 3 samples per frame. Mid-payload changes from a speed patch would go undetected, and the report uses this gate to carry the earlier full-length quality pass forward to the final binaries.
- The only encoder controls are bitrate, VBR and an experimental direct-cubic mode. There is no complexity, bandwidth, signal or DTX setter, and the encoder always runs the maximum-complexity path. Direct-cubic packets are not decodable by standard Opus decoders.

## Known shortcomings

- Rust (language-filter mismatch), archived 2026-08-25 (soundkit-opus/libopus-rs link 404). Downgraded A to C: Rust 1.97.1 and GCC 12.2.0 are stated but libopus.a configure flags are 'unavailable', the timing JSON build flags 'unknown' and the corpus private; the 1-2% gain is too small to rule out build asymmetry, the C side ran full opus_encode with 4 ms lookahead (312 vs 120 sample alignment), and output is not bit-exact (ViSQOL parity only).
- The decode claim is invalid (retier-25): the 1.50-4.64% decode lead timed each decoder on its own encoder's packets, and the author's 2026-08-25 same-packet re-test (soundkit-opus performance-results) gives +0.51% on C packets, -0.30% on Rust packets and +0.10% combined, parity. The encode margin (1.19-2.36%) is the same order as the run-to-run drift (about 0.5 percentage points) and the work is asymmetric (the analysis port skips libopus's MLP/GRU classifier; i16 decode hard-clamps where C soft-clips); the identity checksum covers only packet length plus first and last byte; both crates.io releases are yanked.

## Caveats and trade-offs

The gain is small (encode 1.19-2.36%, decode 1.50-4.64%) and covers one configuration family (48 kHz stereo CELT, 5 ms frames, maximum complexity, 192-320 kb/s) on one x86 host. The libopus.a build configuration was not recorded, and the project's own README warns that intrinsics and --enable-float-approx materially change the C baseline. Meanwhile the Rust side was built with target-cpu=native, ThinLTO and one codegen unit. At a 1-2% margin, build asymmetry cannot be ruled out. The work is not identical. C goes through the full opus_encode/opus_decode layer, including the 4 ms OPUS_APPLICATION_AUDIO delay compensation: the quality gate aligns C at 312 samples versus 120 for Rust. Rust is a CELT-only raw-frame codec that ports the tonality analysis but not that lookahead. Output is not bit-exact with libopus, and the README says the encoder does not target byte identity. CBR byte totals match (fixed by the bitrate), constrained-VBR totals differ by 350-527 B over 400 s, aligned SNR is within about 0.04 dB, and ViSQOL MOS-LQO is 4.5731 versus 4.5724. The packet-identity gate compares Rust with its own previous checkpoint, not with C. The codec is incomplete (no SILK, hybrid, Ogg Opus or other sample rates), and the README says it is not a production replacement for libopus. The timing corpus is licensed local audio that is not in the repo, and the raw timing JSONs are published only as SHA-256 hashes, so the run cannot be reproduced as published. The repository was archived on 2026-08-25 in favour of wavey-ai/soundkit (soundkit-opus). The README's soundkit-opus/libopus-rs link returned 404 on main. The crates.io release predates the measured optimisations. [retier] Decode claim invalid (each decoder was timed on its own encoder's packets; same-packet re-test shows parity). Work asymmetry favours Rust: the analysis port skips the MLP/GRU classifier and i16 decode hard-clamps where C soft-clips. The identity checksum covers only packet length plus first and last byte. Both crates.io releases are yanked; successor crate soundkit-opus 0.13.0.

Incomplete codec: only 48 kHz CELT-only raw frames are supported; no SILK, hybrid or Ogg Opus. Not a drop-in replacement for libopus, no C API, and encoder packets are not byte-identical to libopus. Encoder is marked experimental. Uses a private SIMD kernel path dependency crate.

## Maintenance

Archived on 2026-08-25 with 0 stars, both crates.io versions yanked and no issues filed. The BSD-3-Clause code can be vendored from git, but development and the corrected results moved to wavey-ai/soundkit (soundkit-opus 0.13.0, MIT AND BSD-3-Clause).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** The report's timing matrix matches the record (e.g. 16-bit CBR 192 kb/s encode 371.9126 vs 380.9057 ms, decode 95.3447 vs 99.9845 ms; 96.80-107.55x and 338.14-430.05x realtime). The harness is public (tools/raw_celt_bench.c, tools/run_raw_celt_bench.sh, tools/run_soundkit_flac_corpus.py), and the report names Rust 1.97.1, GCC 12.2.0, the Rust and C-driver flags and the Xeon Platinum 8581C. But the baseline library's own build is not stated: the libopus configure string is recorded as unavailable, and the final timing JSON records the build flags as unknown. The corpus is private and only hashes of the raw timing JSONs are published, so these are first-party numbers with partial methodology: C, not A.
- **Verifier notes:** Real, honest first-party comparison against trunk libopus. It falls short of A because the baseline library's build flags were not recorded and the corpus is private, which matters at a 1-2% margin. The record wrongly said compiler versions were missing; the report states Rust 1.97.1 and GCC 12.2.0. Archived status is a caveat, not a reject. The successor wavey-ai/soundkit is public (MIT, 3 stars) and has a soundkit-opus directory; it was not verified.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `workload`, `stars_or_usage`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/performance-results/2026-08-24-native-48k/README.md>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/tools/raw_celt_bench.c>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/tools/run_raw_celt_bench.sh>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/tools/run_soundkit_flac_corpus.py>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/PORTING.md>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/src/analysis.rs>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/src/encoder.rs>
  - <https://github.com/wavey-ai/libopus-rs>
  - <https://github.com/wavey-ai/libopus-rs/tree/main/src>
  - <https://github.com/wavey-ai/libopus-rs/commits/main>
  - <https://crates.io/api/v1/crates/libopus-rs>
  - <https://github.com/wavey-ai/soundkit>
  - <https://github.com/wavey-ai/soundkit/tree/main/soundkit-opus/libopus-rs>
- **Sources the enricher read:**
  - <https://github.com/wavey-ai/libopus-rs>
  - <https://github.com/wavey-ai/libopus-rs/tree/main/src>
  - <https://github.com/wavey-ai/libopus-rs/tree/main/crates/libopus-rs-kernels>
  - <https://github.com/wavey-ai/libopus-rs/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/performance-results/2026-08-24-native-48k/README.md>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/tools/raw_celt_bench.c>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/tools/run_raw_celt_bench.sh>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/tools/run_soundkit_flac_corpus.py>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/examples/raw_celt_bench.rs>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/PORTING.md>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/SAFETY.md>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/src/encoder.rs>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/src/decoder.rs>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/src/analysis.rs>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/src/celt/mathops.rs>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/crates/libopus-rs-kernels/Cargo.toml>
  - <https://raw.githubusercontent.com/wavey-ai/libopus-rs/HEAD/crates/libopus-rs-kernels/src/lib.rs>
  - <https://crates.io/api/v1/crates/libopus-rs>
  - <https://crates.io/api/v1/crates/libopus-rs/0.0.2/dependencies>
  - <https://raw.githubusercontent.com/xiph/opus/03647f524a40b05a1898522e92033810b58103c7/src/analysis.c>
  - <https://raw.githubusercontent.com/xiph/opus/03647f524a40b05a1898522e92033810b58103c7/src/opus_encoder.c>
  - <https://raw.githubusercontent.com/xiph/opus/03647f524a40b05a1898522e92033810b58103c7/src/opus_decoder.c>
  - <https://raw.githubusercontent.com/xiph/opus/03647f524a40b05a1898522e92033810b58103c7/configure.ac>
  - <https://raw.githubusercontent.com/xiph/opus/03647f524a40b05a1898522e92033810b58103c7/celt/mathops.h>
  - <https://github.com/wavey-ai/soundkit/tree/main/soundkit-opus>
  - <https://github.com/wavey-ai/soundkit/tree/main/soundkit-opus/performance-results>
  - <https://raw.githubusercontent.com/wavey-ai/soundkit/HEAD/soundkit-opus/README.md>
  - <https://raw.githubusercontent.com/wavey-ai/soundkit/HEAD/soundkit-opus/Cargo.toml>
  - <https://raw.githubusercontent.com/wavey-ai/soundkit/HEAD/soundkit-opus/CODEC.md>
  - <https://raw.githubusercontent.com/wavey-ai/soundkit/HEAD/soundkit-opus/performance-results/2026-08-24-native-48k/README.md>
  - <https://raw.githubusercontent.com/wavey-ai/soundkit/HEAD/soundkit-opus/performance-results/2026-08-25-native-48k-follow-up/README.md>
  - <https://crates.io/api/v1/crates/soundkit-opus>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/wavey-ai/libopus-rs`) · [data/wave10/enrich/raw/github_com_wavey_ai_libopus_rs.json](../../../data/wave10/enrich/raw/github_com_wavey_ai_libopus_rs.json) (enrichment confidence 0.8)

</details>
