# opus-pure

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause` · 🟢 active

> Pure-Rust Opus encoder, decoder and Ogg container with hand-written SIMD; encodes 1.09-1.76x as fast as libopus 1.6.1 on an M1 Pro.

| | |
|---|---|
| **Beats** | libopus 1.6.1 (float build) |
| **Claimed result** | Encode 1.09-1.76x faster than libopus (SILK 1.09-1.12x, e.g. 218x vs 195x realtime for SILK NB 8 kb/s mono; CELT 128 kb/s 204x vs 116x realtime = 1.76x); decode slower or at parity, 0.84-1.02x of libopus (e.g. SILK NB 3432x vs 3958x realtime). |
| **Workload** | Encode and decode of generated, bit-reproducible 48 kHz test signals (speech for the SILK/hybrid rows with application voip and signal voice; music for the CELT rows with application audio, fullband, signal music), 20 ms frames, complexity 9 (plus complexity 0/5/10 rows), 8 s of audio per case. Fastest of 12 passes, a fresh encoder per pass built outside the timed region, OPUS_SET_LSB_DEPTH(24), and libopus constrained VBR at its default. Covers SILK, hybrid and CELT modes, mono and stereo. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro (aarch64 NEON) |
| **Compiler and flags** | Rust: cargo default release profile (no LTO or codegen-units override; the reference harness package adds debug=1 line tables only), no RUSTFLAGS, no target-cpu; the rustc version is not stated (MSRV 1.88.0). libopus 1.6.1 (sha256-pinned tarball) is built by reference/build.sh as a static CMake -DCMAKE_BUILD_TYPE=Release float build, NEON on with runtime dispatch, plus an OPUS_FIXED_POINT=ON build for the second table. The harness cspeed.c is compiled with cc -O2 -ffp-contract=off. The C compiler is the system cc (clang per the README), version not stated. Neither side uses -march=native. |
| **Adoption** | 2 stars, 3 forks, 19 commits; crates.io opus-pure 0.2.2 (2026-09-28), 15,474 downloads |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/stephenberry/opus-pure) · [benchmark](https://github.com/stephenberry/opus-pure/tree/main/reference/speed) |

## Verdict

The repo's own harness (reference/speed: rspeed vs cspeed.c) ran on an Apple M1 Pro on 2026-08-23 against static libopus 1.6.1 (sha256-pinned, CMake Release float build, NEON with runtime dispatch). It used 8 s of generated speech or music at 48 kHz, 20 ms frames, complexity 9, a fresh encoder per pass and the fastest of 12 passes; rustc and clang versions were not recorded. Encode ran 1.09-1.12x (SILK), 1.14-1.15x (hybrid) and 1.34-1.76x (CELT) of libopus's speed, and decode 0.84-0.92x except 1.02x for stereo hybrid. Each stack decodes its own packets, and the README text says the hybrid rows code 6-10% fewer bits than libopus and the SILK rows 6-11% more, so only the CELT rows (both within 1% of target) time equal work. The published table omits the delivered-bitrate column that run.sh prints and flags.

## Use it when

- Rust services that encode Opus at scale (music or mixed content at 64-256 kb/s, CELT mode) on aarch64 hosts such as Apple silicon. This is where the measured lead is largest: 1.34-1.76x libopus encode throughput.
- Rust projects that want Opus with no C toolchain, system libopus or build.rs, for example to cross-compile to targets where linking C is awkward.
- Reading and writing .opus files in Rust with correct pre-skip, end-trim and granule handling, including gapless round trips and zero-allocation looping playback (0.2.2).
- VoIP encoders on SILK or hybrid at complexity 9-10, where the encoder ran 1.09-1.15x libopus's float build and 1.15x at complexity 10 in SILK wideband.

## Skip it when

- Decode-bound workloads. Decode is 0.84-0.92x of libopus in 9 of 10 measured rows, and the only win, stereo hybrid at 1.02x, decoded a bitstream about 6-10% smaller than libopus's.
- C or C++ codebases. There is no C header or ABI, so calling it means writing and maintaining an FFI layer, and libopus itself is the simpler choice there.
- x86-64 deployments that need proven speed. All published numbers are from one Apple M1 Pro. The AVX2 kernels run only on Linux x86-64 CI, and the README says the Rosetta runs used during development never reached them.
- Low-complexity SILK encoding (complexity 0 or 5), where it is slightly slower than libopus (0.97x, 0.95x). The same applies to workflows needing an encoder bit-exact with libopus in CELT or hybrid: only SILK and the i16 API are byte-exact.
- Very young code: first release on 2026-08-27, 3 stars, one maintainer, and a fork of a fork (rusty-opus 0.9.1, itself from restsend/opus-rs). Its own docs list several SIMD and rate-control defects fixed only recently.

## How it is fast

It is a function-by-function port of libopus (names mirror the C sources) with hand-written SIMD kernels for CELT's hot loops: NEON on aarch64 and SSE/AVX/AVX2 on x86-64, chosen at run time through a cached feature probe. The kernels cover the KISS FFT radix-2/3/4/5 butterflies, the MDCT pre/post-rotation and TDAC fold, the pitch cross-correlation and inner products, band energy, renormalisation and stereo theta. The author attributes the 1.34-1.76x CELT encode lead to these kernels. libopus's float FFT and MDCT run its C code, since the build used no NE10. SILK is the fixed-point encoder, within a few percent of fixed-point libopus (0.97-1.11x). Decode reached 0.84-1.02x after profiling-driven fixes: integer divisions were removed from de-emphasis, per-band buffer zeroing was dropped, and the 16-tap SILK LPC synthesis loop was reordered so that only the newest tap sits on the loop-carried dependency chain.

## Compared with alternatives

Pick opus-pure over its ancestors rusty-opus and opus-rs (both catalogued) when you need the Ogg layer, documented libopus interop (440-configuration sweep, byte-exact SILK) and the defect fixes its docs list, including the hybrid per-channel rate split and the aarch64 NEON kernel fixes. For decode-heavy Rust use, ruopus reports decode faster than libopus 1.6.1 (1.41-1.79x) on its own harness, and opuspp is the C++ option for a faster decoder. All of these come from different harnesses and machines, so cross-entry ratios are not directly comparable.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none |
| **Minimum toolchain** | Rust 1.88.0 (edition 2024) |
| **Platforms** | any Rust target. aarch64 uses NEON as baseline; x86-64 selects SSE, AVX or AVX2 at run time; other targets use scalar paths. CI covers Linux x86-64, Linux aarch64, macOS aarch64 and Windows x86-64. |
| **Thread safety** | Encoders and decoders are independent owned values driven through &mut methods, one per stream. The only shared global state is the atomic CPU-feature cache. encode_parallel spawns scoped threads, each with its own encoder. Send and Sync guarantees are not documented. |
| **Drop-in for the baseline** | partial: settings, defaults (64 kb/s, complexity 9, constrained VBR), packet format and the i16 API match libopus behaviour, but the API is Rust-only with no C ABI, so existing libopus callers must be rewritten or wrapped. |

## Gotchas

- 'Pure Rust' does not mean unsafe-free. The SIMD kernels are unsafe fns using intrinsics, and PR #3 (2026-09-03, after the published measurements) fixed out-of-bounds reads in the NEON xcorr_kernel (when len == 0) and in the NEON short-prediction path of silk/nsq_del_dec.rs. The maintainer verified that encoder output stayed byte-identical.
- Decoded float output can exceed plus or minus 1, as in libopus. Use decode_s16 or SoftClip before converting. encode_s16 declares 16-bit input depth and the float API declares 24-bit, so the two produce different packets for the same audio.
- encode_parallel is not equivalent to a serial encode: the worst frame at a chunk boundary lands about 4 dB below serial, and workers are capped at one per 8 s of audio. The Ogg reader can only rewind to the start; there is no arbitrary seek.
- The README says encode makes about ten short-lived allocations per frame (about 500 per second per stream), mostly in tonality analysis. 0.2.2 moved some of that scratch into encoder state, so measure before hosting hundreds of streams per process.

## Known shortcomings

- Rust (language-filter mismatch), derived from rusty-opus which forks restsend/opus-rs. Downgraded A to C: reference/speed/README.md states the harness, flags, Apple M1 Pro and a sha256-pinned libopus 1.6.1 CMake Release float build with matched settings, but the rustc version (MSRV 1.88.0 only) and clang version are missing. CELT encode is not bit-exact (SILK byte-exact against fixed-point libopus) and decode is 0.84-1.02x.
- Decode rows compare each stack's own packets rather than the same packets: the hybrid rows code 6-10% fewer bits than libopus and the SILK rows 6-11% more, so only the CELT rows are equal work, and the stereo hybrid decode 1.02x win is on a smaller bitstream. The published table omits the kb/s flags that run.sh prints; results of 2026-08-23 predate the 0.1.0 import (2026-08-27), and PR #3 later fixed out-of-bounds reads in the unsafe NEON xcorr_kernel and the SILK nsq_del_dec short prediction (output byte-identical); cspeed.c says the crate lacks constrained VBR although encoder.rs defaults to RateControl::ConstrainedVbr. A substantive fork of the listed rusty-opus and opus-rs (adds an Ogg layer, fixes and its own harness), kept as its own entry.

## Caveats and trade-offs

One aarch64 machine (Apple M1 Pro) only, no x86 numbers, and the toolchain versions are not pinned. Decode is slower than libopus in 9 of 10 rows (0.84-0.92x), with parity at 1.02x only for stereo hybrid. The large wins are CELT encode only (1.34-1.76x). SILK encode is a fixed-point port, so the float-libopus column compares different algorithms. Against fixed-point libopus, SILK encode is 0.97-1.11x and hybrid encode 1.09-1.13x. The README says hybrid matches neither libopus build exactly. Encoder output is not bit-exact with libopus except SILK, which is byte-exact against fixed-point libopus in 22 configurations. CELT and hybrid encoders are only interoperable, with 433 of 440 whole-stream configurations decoding within 100 dB SNR of libopus. Delivered bitrate is checked per row, and CELT lands within 0-1% of target on both stacks. In SILK the crate is slightly slower than libopus at complexity 0 and 5 (0.97x, 0.95x). The code derives from rusty-opus 0.9.1, itself a fork of restsend/opus-rs (both BSD-3-Clause), per ATTRIBUTION.md.

Pure Rust, no C API or FFI exposed (callable from C++ only by writing a wrapper); no dependencies; hand-written NEON/SIMD kernels for CELT. Decode is not faster than libopus. Chunk-parallel encode is lossy relative to serial encode. Ogg reader seeks only to the start.

## Maintenance

Active (0.2.2 on 2026-09-28, 19 commits, 15,710 crates.io downloads, one open PR) and BSD-3-Clause with no dependencies, so it is easy to adopt in Rust. The speed table predates the 0.1.0 import and has not been re-run for 0.2.2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** reference/speed/README.md (Results, 2026-08-23) has every quoted number (e.g. SILK NB 8 kb/s 218x vs 195x, CELT 128 kb/s stereo 204x vs 116x = 1.76x, SILK NB decode 3432x vs 3958x). The harness is public: reference/speed/run.sh, reference/speed/cspeed.c, reference/rust/src/speed.rs, and reference/build.sh, which builds a sha256-pinned libopus 1.6.1 with CMake Release. Flags and the CPU (Apple M1 Pro) are stated. Neither compiler version is: rustc appears only as the 1.88.0 MSRV, and the C side is the system cc (clang per the README text), unversioned. Under this project's precedent, missing compiler versions make it first-party C, one field short of A.
- **Verifier notes:** The comparison is careful and like-for-like in settings: matched bitrate, complexity, application, bandwidth and signal; a fresh encoder per pass; delivered-bitrate and mode-mismatch flags. It would be tier A if the rustc and Apple clang versions were recorded. The ancestor restsend/opus-rs is from the same organisation as rustrtc; check whether rusty-opus or opus-rs are already listed before enrichment.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `is_fork_of`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/stephenberry/opus-pure/tree/main/reference/speed>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/speed/README.md>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/speed/run.sh>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/speed/cspeed.c>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/build.sh>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/README.md>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/ATTRIBUTION.md>
  - <https://github.com/stephenberry/opus-pure>
  - <https://github.com/stephenberry/opus-pure/commits/main>
  - <https://crates.io/api/v1/crates/opus-pure>
- **Sources the enricher read:**
  - <https://github.com/stephenberry/opus-pure>
  - <https://github.com/stephenberry/opus-pure/commits/main>
  - <https://github.com/stephenberry/opus-pure/pulls>
  - <https://github.com/stephenberry/opus-pure/pull/3>
  - <https://github.com/stephenberry/opus-pure/tree/main/src>
  - <https://github.com/stephenberry/opus-pure/tree/main/src/celt>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/README.md>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/ATTRIBUTION.md>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/speed/README.md>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/speed/run.sh>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/speed/cspeed.c>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/rust/src/speed.rs>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/reference/build.sh>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/docs/interop-validation.md>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/src/encoder.rs>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/src/cpu_features.rs>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/src/parallel.rs>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/src/celt/pitch.rs>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/src/celt/kiss_fft.rs>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/src/celt/mdct.rs>
  - <https://raw.githubusercontent.com/stephenberry/opus-pure/HEAD/src/celt/bands.rs>
  - <https://crates.io/api/v1/crates/opus-pure>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/stephenberry/opus-pure`) · [data/wave10/enrich/raw/github_com_stephenberry_opus_pure.json](../../../data/wave10/enrich/raw/github_com_stephenberry_opus_pure.json) (enrichment confidence 0.8)

</details>
