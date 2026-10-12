# ruopus

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Pure-Rust Opus encoder and decoder: SILK/hybrid decode 1.4-1.8x faster than libopus 1.6.1; encode at parity at matched complexity.

| | |
|---|---|
| **Beats** | libopus 1.6.1 (SIMD-enabled C) |
| **Claimed result** | README (x realtime, one pinned core; ratio = ruopus/libopus): decode SILK WB 16 kb/s 2095x vs 1171x (1.79x), hybrid FB 32 kb/s 1199x vs 850x (1.41x), CELT FB 64 kb/s 1389x vs 1566x (0.89x, slower). Encode at matched complexity 0: 734x vs 740x (0.99x), 560x vs 562x (1.00x), 1088x vs 1092x (1.00x). Encode against libopus at complexity 10 (ruopus also set to 10): SILK WB 16 kb/s 703x vs 221x (3.18x), hybrid FB 32 kb/s 424x vs 193x (2.20x), CELT FB 64 kb/s 693x vs 432x (1.60x); ruopus's complexity-10 encoder omits delayed-decision NSQ and warped noise shaping, so these ratios compare unequal work. |
| **Workload** | In-process mono 48 kHz Opus decode and encode of a 6 s synthetic speech/music-like signal (tones under a syllabic envelope plus light noise) in 20 ms frames, one core, reported as x realtime (benches/vs_libopus.rs, timed until each run exceeds about 0.4 s). Decode inputs are libopus-encoded VBR packets for SILK WB 16 kb/s (VoIP), hybrid FB 32 kb/s (VoIP) and CELT FB 64 kb/s (Audio); each repetition builds a new decoder or encoder on both sides. |
| **Metric** | throughput |
| **Hardware** | one core pinned to a single performance core; CPU model not stated |
| **Compiler and flags** | cargo bench --bench vs_libopus --features std; release profile opt-level=3, lto=fat, codegen-units=1 (Cargo.toml); libopus 1.6.1 reached through the opus FFI crate against the system libopus, so its build flags are not stated. |
| **Adoption** | 1 star; on crates.io as ruopus (about 6.9k downloads) |
| **Last commit** | 2026-07-07 |
| **Links** | [repository](https://github.com/jmg049/ruopus) · [benchmark](https://github.com/jmg049/ruopus) |

## Verdict

The author's in-process harness (benches/vs_libopus.rs, built with the release profile: opt-level 3, fat LTO, codegen-units 1) ran on one pinned core against system libopus 1.6.1 through the opus 0.3 FFI crate. Decoding identical libopus-made packets, ruopus was 1.79x (SILK WB 16 kb/s) and 1.41x (hybrid FB 32 kb/s) faster and 0.89x on CELT FB 64 kb/s; encoding identical input, it was 0.99-1.00x at complexity 0 and 1.60-3.18x against libopus at complexity 10, which is unequal work. CPU model, OS, rustc version and libopus build flags are not stated, and the test signal is mostly clipped noise rather than the speech-like tones it is described as (see measurement_notes).

## Use it when

- Rust, wasm32 or no_std targets that need an Opus decoder without a C toolchain. Speech-mode streams decoded 1.79x (SILK wideband 16 kb/s) and 1.41x (hybrid fullband 32 kb/s) faster than libopus 1.6.1 in the author's in-process bench.
- Python pipelines that want Opus encode and decode from pip wheels. The bindings release the GIL around codec calls, and the CHANGELOG reports decode scaling from 810x to 2308x realtime across 1 to 4 threads.
- Pure-Rust speech or VoIP encoding where libopus would otherwise run at its default complexity 10 and the simpler ruopus search is good enough: 1.6-3.2x faster than libopus at complexity 10, and at parity with libopus at complexity 0.
- Projects that want a memory-safe codec whose decoder passes all twelve RFC 8251 vectors (99.2-100% on opus_compare, final ranges bit-exact), with unsafe code limited to Miri-checked SIMD kernels.

## Skip it when

- C++ code bases. There is no C API, so you would write and maintain a Rust FFI layer; for C++ the existing libopus or a C/C++ port is less work.
- Music- or CELT-heavy decoding (0.89x of libopus at 64 kb/s fullband), or pipelines that need PCM bit-identical to libopus.
- Encoders where quality at complexity 10 matters. ruopus lacks delayed-decision NSQ and warped noise shaping, and its encoder quality is checked only by waveform SNR (examples/encoder_quality.rs), not a perceptual metric such as PESQ, POLQA or ViSQOL.
- Encoding on ARM or wasm. The encoder's SIMD kernels exist only for x86-64 (AVX2+FMA detected at runtime, SSE2 baseline), and other targets fall back to scalar code; no non-x86 numbers are published.
- Teams that need a mature dependency. ruopus is at version 0.1.2 (first published 2026-06-29), has one author and 1 star, and has no surround or multistream encoder.

## How it is fast

The decode path has no SIMD of its own. The README does not explain why SILK and hybrid decode beat libopus; it attributes the CELT deficit (0.89x) to libopus's SIMD MDCT. The default 'spectrograms' feature routes the CELT MDCT's inner FFT through realfft/rustfft plans, which Cargo.toml puts at about 10x faster decode than the built-in O(n^2) evaluation. Encode speed comes from profile-driven hot-loop work listed in the v0.1.2 CHANGELOG: AVX2+FMA/SSE2 dot products and a four-lag cross-correlation for SILK and CELT pitch analysis, an SSE2 PVQ pulse search, a port of silk_NSQ_sse4_1's rate-distortion lookup table, LPC filters specialised by prediction order, and stack-allocated scratch buffers; the 1.6-3.2x wins over libopus at complexity 10 come mainly from search that ruopus does not do (delayed-decision NSQ, warped noise shaping).

## Compared with alternatives

Among the Rust Opus siblings, pick ruopus when you need both a conformance-checked decoder that builds no_std and wasm32 and a feature-complete encoder (FEC, DTX, hybrid, Python bindings); ropus (a libopus 1.5.2 port at about 0.96-0.97x time against fixed-point libopus) and opus-rs (encoder within a few percent of libopus) report near-parity speed. A C++ project is better served by opuspp's decoder, which was compared with libopus under identical compiler and flags and needs no FFI layer.

## Integration

| | |
|---|---|
| **Form** | crate (ruopus 0.1.2 on crates.io; rlib + cdylib for the PyO3 module); Python wheels on PyPI; no C header |
| **Dependencies** | none required; default feature 'spectrograms' 2.0 (realfft) for the fast MDCT; optional libm for no_std; pyo3 0.29 + numpy 0.29 behind the 'python' feature |
| **Minimum toolchain** | Rust 1.85 (edition 2024), stable |
| **Platforms** | any Rust target; decoder also no_std + alloc (CI builds thumbv7em-none-eabihf) and wasm32; encoder SIMD AVX2+FMA (runtime-detected) or SSE2 on x86-64, scalar elsewhere |
| **Thread safety** | not documented; encoders and decoders are owned per-stream values with no shared mutable state apart from an atomic cached CPU-feature flag, and the Python bindings release the GIL around codec calls |
| **Drop-in for the baseline** | no |

## Gotchas

- default-features = false, the zero-dependency and no_std configuration, swaps the FFT-backed MDCT for an O(n^2) evaluation. The CHANGELOG puts that at about 10x realtime decode, against 410-730x with the default 'spectrograms' feature.
- decode_packet and encode_auto return a fresh Vec for every packet, and there is no decode-into-buffer call, so tight loops pay an allocation per packet (the bench includes this on the ruopus side).
- encode_auto picks SILK, hybrid or CELT itself, from a cheap energy, tilt and zero-crossing analysis with hysteresis (CELT once the smoothed music probability exceeds 0.7). The encoder defaults to application Audio and signal Auto; call set_application or set_signal if you need libopus-like VoIP behaviour.
- Decoded PCM differs from libopus in float rounding (only the final range is bit-exact), and encoded bitstreams differ from libopus's, so golden-file tests against libopus output will fail.

## Known shortcomings

- Rust with no C API (language-filter mismatch). Baseline is the real libopus 1.6.1 through the opus FFI crate (benches/vs_libopus.rs, in-process, same packets) with no CPU model, OS, rustc or libopus flags. Decode 1.41-1.79x on SILK and hybrid but 0.89x on CELT, like-for-like (RFC 8251 vectors pass, final ranges bit-exact, PCM not bit-exact). Encode is at parity at complexity 0; the 3.18x/2.20x/1.60x at complexity 10 compare unequal work (ruopus skips delayed-decision NSQ and noise shaping) with encoder quality checked by waveform SNR only.
- The harness signal() has a noise-term bug ((seed &gt;&gt; 9)/65535 spans -0.5 to 127.5), so the test input carries a +1.27 DC offset and 0.74 RMS noise against 0.30 RMS tones with 61% of samples over full scale; the record's 'tones plus light noise' workload is wrong, although both sides receive the same input so the ratios stay like-for-like on it. encode_auto mode is simulated and its smoothed music probability peaks at 0.66 (below 0.7), so SILK/hybrid mode likely matches libopus; one timing pass with no variance; encoder SIMD is x86-64 only; with default-features=false decode runs about 10x realtime.

## Caveats and trade-offs

Baseline is libopus itself (not another Rust port), linked via the opus 0.3 FFI crate against the system libopus (1.6.1 per the README); its build flags and SIMD dispatch are not stated, nor are the CPU model, OS or rustc version. Decode is comparable work, but output is not bit-exact PCM: the decoder passes all twelve RFC 8251 vectors at 99.2-100% on opus_compare with bit-exact per-packet final ranges, while PCM differs in float rounding (default spectrograms/rustfft MDCT backend). The encoder produces a different bitstream from libopus, and its quality is checked only by waveform SNR (examples/encoder_quality.rs; the CHANGELOG reports higher SNR than libopus), not a perceptual metric. At complexity 10, ruopus skips delayed-decision NSQ and warped noise shaping that libopus runs, so the 1.6-3.18x encode wins compare unequal work; at matched complexity 0, encode is at parity. In the encode bench, ruopus chooses its mode through encode_auto, while libopus gets an explicit application and VBR setting, and the bench does not check that both pick the same mode. CELT decode is slower than libopus. The signal is synthetic. The library is pure Rust with no C API (Python bindings via PyO3), so C++ use needs a custom FFI shim.

Pure Rust Opus encoder and decoder with Python bindings and wasm32 support; no C API or FFI exposed, so C++ use needs a wrapper. Encoder does not yet implement delayed-decision noise-shaping quantization or warped noise shaping.

## Maintenance

Active (last commit 2026-07-07, crate 0.1.2), but very young, with one author and 1 star. It is MIT-licensed, so wrapping or vendoring it is unrestricted.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance tables come from the public in-process harness benches/vs_libopus.rs against libopus 1.6.1 through the opus FFI crate, and the release profile is in Cargo.toml, but the CPU model, OS, rustc version and the system libopus build flags are not stated, so it is first-party C rather than A.
- **Verifier notes:** The README numbers match the record, and the bench code confirms that libopus 1.6.1 via FFI is the baseline, measured in-process on identical packets and input. The headline 3.18x encode figure compares ruopus at its fixed effort against libopus complexity 10; at matched complexity 0, encode is at parity. The decode wins (1.41-1.79x on SILK and hybrid) are like-for-like work. verify.py does not apply 'language' from corrections, so record it as a decision override.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jmg049/ruopus>
  - <https://github.com/jmg049/ruopus/commits>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/README.md>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/benches/vs_libopus.rs>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/examples/encoder_quality.rs>
  - <https://crates.io/api/v1/crates/ruopus>
- **Sources the enricher read:**
  - <https://github.com/jmg049/ruopus/tree/main/src>
  - <https://github.com/jmg049/ruopus/commits/main>
  - <https://github.com/jmg049/ruopus/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/README.md>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/benches/vs_libopus.rs>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/examples/encoder_quality.rs>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/src/decoder.rs>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/src/encoder.rs>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/src/encoder_analysis.rs>
  - <https://raw.githubusercontent.com/jmg049/ruopus/HEAD/src/simd.rs>
  - <https://crates.io/api/v1/crates/ruopus>
  - <https://crates.io/api/v1/crates/opus>
  - <https://crates.io/api/v1/crates/opus/0.3.0/dependencies>
  - <https://crates.io/api/v1/crates/opus/0.3.1/dependencies>
  - <https://crates.io/api/v1/crates/audiopus_sys>
  - <https://raw.githubusercontent.com/lakelezz/audiopus_sys/HEAD/build.rs>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/jmg049/ruopus`) · [data/wave10/enrich/raw/github_com_jmg049_ruopus.json](../../../data/wave10/enrich/raw/github_com_jmg049_ruopus.json) (enrichment confidence 0.8)

</details>
