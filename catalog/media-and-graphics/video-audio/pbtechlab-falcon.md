# Falcon audio codec

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust (with C and C++ API)` · `MIT` · 🟢 active

> New MIT-licensed MDCT audio codec in Rust, with a C API, whose decoder runs about 1.5x faster than libopus at equal file size.

| | |
|---|---|
| **Beats** | libopus 1.6.1 (float and fixed point), opusfile 0.12, libvorbis 1.3.7, Tremor (decoders) |
| **Claimed result** | Falcon 1114x real time vs libopus 1.6.1 float 731x (Falcon time 0.66x of libopus), libopus fixed point 629x, opusfile 717x, libvorbis 879x (0.79x), Tremor 877x (0.79x) on an x86-64 laptop performance core; Apple M5 1551x vs libopus float 1056x (0.68x) and libvorbis 1297x (0.84x). Faster than libopus on 18 of 18 files on both CPUs; stb_vorbis 1154x is on par on x86-64 and 1.28x faster on M5. 256 voices: 291 ms vs libopus float 365 ms. |
| **Workload** | Library-level single-thread decode of an 18-file 48 kHz stereo corpus (11 real recordings plus 7 synthetic signals) from memory to PCM in 20 ms reads, with Falcon and Opus files at equal size and Vorbis at its own quality setting; total times real time over the corpus, plus 256 simultaneous stereo voices. |
| **Metric** | throughput |
| **Hardware** | Intel Core Ultra 9 185H laptop (Windows 11, thread pinned to one performance, efficiency or low-power efficiency core) and a MacBook Pro with Apple M5 (macOS 26) |
| **Compiler and flags** | Falcon: workspace release profile (opt-level 3, lto = true i.e. fat LTO, codegen-units 1, panic abort), .cargo/config.toml target-cpu=x86-64-v3 on x86-64 targets, default aarch64 target on M5; on Windows the MSVC-toolchain DLL (a MinGW build decodes 1.45x slower, 771x). C decoders: -O3, GCC 15.1 (MinGW-w64) -march=x86-64-v3 on x86-64, Apple clang 17 default target on M5; libopus default SIMD (SSE4.1/AVX2 runtime dispatch, NEON on arm64), stack protector off. Each run times open + whole-file decode + close; at least 10 runs and 1 s per file; best run over two passes. |
| **Adoption** | 2 stars, 0 forks; 5 commits; v2.0.1 (2026-09-29) |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/pbtechlab/Falcon) · [benchmark](https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/README.md) |

## Verdict

First-party, single-thread, library-level decode of an 18-file 48 kHz stereo corpus from memory in 20 ms reads (open, decode and close timed; best run over two passes): Falcon 2.0 through its C API at 1114x real time vs float libopus 1.6.1 at 731x on an Intel Core Ultra 9 185H P-core (Windows 11; Falcon built with the MSVC Rust toolchain for x86-64-v3, C decoders with GCC 15.1 MinGW-w64 -O3 -march=x86-64-v3), and 1551x vs 1056x on Apple M5 (Apple clang 17). Falcon decodes its own files, size-matched to libopus VBR files of 96-214 kbps, while raw libopus is fed pre-extracted packets; the C program that produced the table is not public, the 2.0.0 numbers it replaced were withdrawn the same day (FFmpeg's built-in decoders and cached reference times), and 11 of the 18 corpus files are not redistributed.

## Use it when

- Games or apps that ship their own audio assets, control both encoder and decoder, and want lower CPU per voice than libopus or libvorbis/Tremor at Opus-like file sizes.
- Mixing many simultaneous 48 kHz stereo streams on one thread, where decode CPU matters more than memory (README: 256 voices in 291 ms vs 365 ms for float libopus on x86-64).
- C or C++ engines that want an MIT-licensed codec with a small C ABI and a CMake target, and that can take a Rust-built static or shared library.
- Projects that prefer a codec whose design avoids four named patents (PATENTS.md), accepting that this is the author's own analysis, not legal advice.

## Skip it when

- Anything that must interoperate: browsers, WebRTC, Ogg/Opus or Vorbis files, or third-party players cannot read .falcon, and 1.x files cannot be read by 2.x.
- Real-time voice or lossy networks: no packet-loss concealment, no low-delay mode, 20 ms frames plus encoder look-ahead.
- Memory-tight many-voice playback: about 318-345 KB of heap per stereo stream plus a full copy of the compressed file in the C API (libopus 27 KB), and about 629 KB of decoder code vs 130 KB for libopus.
- When stb_vorbis is an option: in Falcon's own table it is 4% faster on the x86-64 P-core and 1.28x faster on Apple M5, with less memory per stream and a standard format.
- Production use that needs an outside track record: two stars, five commits, first release July 2026, no independent measurement, and the cross-codec harness is not published.

## How it is fast

The format moves every decision to the encoder: the decoder reads static canonical Huffman codes for 27 band energies, derives each band's pulse count from the transmitted energies (no allocation side info), decodes integer pulse vectors from static cell tables (stars-and-bars composition index plus Fischer pyramid enumeration or Golomb-Rice), scales each band in one autovectorized pass and runs one FFT-based inverse MDCT (rustdct/rustfft) per frame, or four short ones on transients. There is no decoder-side psychoacoustics, spreading rotation or anti-collapse logic, the per-band 10^(dB/20) uses a polynomial instead of libm powf, and x86-64 builds default to x86-64-v3 (AVX2, FMA) with fat LTO.

## Compared with alternatives

The catalogued Opus decoders (ruopus, opuspp, opus-pure) report decode gains over libopus 1.6.1 of a similar size (1.27x to 1.79x in their own first-party tests) while keeping the standard Opus bitstream, so take one of those when you need Opus compatibility. Pick Falcon only for a closed asset pipeline where you choose the codec and want an MIT-licensed format with a deliberately simple decoder.

## Integration

| | |
|---|---|
| **Form** | Rust crates (falcon_decoder, falcon_encoder, falcon_core), plus static lib and shared lib via falcon_capi (C99 header falcon.h, C++17 falcon.hpp) |
| **Dependencies** | rustfft, rustdct, num-complex, thiserror, crc, byteorder, once_cell (Rust); the C library links the Rust standard library, plus ntdll on MSVC or pthread, dl and m on Linux/macOS |
| **Minimum toolchain** | Rust 1.70 (declared MSRV), Cargo; C99 or C++17 compiler for the bindings; verified with MSVC and MinGW |
| **Platforms** | Windows, Linux, macOS; x86-64 builds default to x86-64-v3 (AVX2, FMA, BMI) via .cargo/config.toml, aarch64 uses NEON; tuned for 48 kHz |
| **Thread safety** | A decoder handle is not thread-safe; separate handles are independent, and falcon_encode_buffer, falcon_free and the version/error functions can be called from any thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Pulse counts come from f32 powf/exp/ln on both encoder and decoder (falcon_core::alloc), so a different libm can in principle change an integer pulse count and desynchronize the stream; the README says cross-platform agreement has not been tested systematically, and the CLI and C API encoders emit a random-access frame only at the start, so a desync would not recover.
- The release profile sets panic = "abort", so any panic that slips past the decoder's error paths aborts the host process; the corrupt-input coverage is deterministic truncation and byte-flip tests on one synthetic tone, not a coverage-guided fuzzer.
- The default x86-64 build requires AVX2/FMA (x86-64-v3); rebuild with RUSTFLAGS="-C target-cpu=x86-64" for older CPUs. Before 2.0.1 the same setting broke aarch64 builds, which produced invalid output.
- Seeking is linear: a backward seek re-decodes from the file start, and the decoder makes about seven heap allocations (about 8 KB) per 20 ms frame. A MinGW build of the Rust library decodes 1.45x slower (771x) because it links msvcrt pow/exp/log.

## Known shortcomings

- Different codec from libopus, matched only by file size, with quality parity resting on the project's own metrics; the C decoder harness behind the README table (1114x versus libopus 731x realtime, 0.66x time) is not published anywhere (tools/ holds only a Python quality script and an old ffmpeg-subprocess evaluation).
- v2.0.1 fixed aarch64 builds that produced invalid output on the same day the M5 numbers appeared (the README says outputs are SNR-checked); the 2.0.0 numbers were withdrawn (FFmpeg built-in decoders, cached reference times); pulse counts use libm powf on both sides with cross-platform desync untested; panic = abort in release builds; the 'fuzz' tests are fixed truncation and byte-flip cases on one tone. The C comparison program is still unpublished.

## Caveats and trade-offs

First-party numbers on one Intel laptop CPU and one Apple CPU; the C comparison harness that links all decoders is not in the repository (README: 'the cross-codec numbers ... come from a C harness that calls the C API'), so the table cannot be reproduced from public code; the 11 real recordings of the 18-file corpus are not redistributed (the 7 synthetic signals are regenerable with tools/quality/make_torture.py). Different work from the baseline: libopus decodes Opus bitstreams while Falcon decodes its own MDCT format, matched only on file size (Falcon encoded with --target-bytes at &lt;= the Opus file size, 0.998-1.000x on 17 files and 0.53x on the sweep; Opus references are libopus VBR at 96-214 kbps with encoder settings not stated). Quality equivalence rests on Falcon's own metrics: lower MR-STFT on 18/18 and log-mel on 13/18, the perceptual A/B check 'same' overall, Opus better on 4 files (harpsichord, pinkbursts, polychord, sfxtransient), and the perceptual checker is not in the repo. Falcon lacks packet-loss concealment and a low-delay mode, which libopus provides. Raw libopus is fed pre-extracted packets (no Ogg parsing) while opusfile/vorbisfile/stb_vorbis include container parsing. Falcon uses about 318-345 KB heap per stereo stream plus a copy of the compressed file (libopus 27 KB), allocates about seven times per 20 ms frame, and its decoder-only code is 629 KB vs libopus 130 KB. stb_vorbis is 4% faster on the x86-64 P-core and 1.28x faster on M5. Earlier README versions compared against FFmpeg's built-in Opus/Vorbis decoders by mistake; the old Vorbis figures were withdrawn in v2.0.1 (against FFmpeg's Vorbis decoder Falcon wins only 5 of 18 files). Floating-point encoder/decoder agreement across platforms is untested. Very new project (2 stars).

A different codec, not a drop-in decoder for Opus streams: Falcon is an MDCT codec whose decoder is deliberately light and whose quality comes from encoder-side work. Uses more memory per stream than libopus (about 320-345 KB of heap per stereo stream plus a copy of the compressed file, vs 27 KB for libopus) and voice start-up is slower (156 us vs 46 us). Includes a C/C++ API (falcon_capi) with falcon.h and falcon.hpp. Quality claim is on par with Opus on an 18-file corpus, not an independent listening test. Version 2 was redesigned to avoid specific patents.

## Maintenance

Active but very new (five commits, v1.0.0 July 2026, v2.0.0 and v2.0.1 both on 2026-09-29, two stars); MIT-licensed and copyable, but the format is young and the speed claim is first-party with no public harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Decode speed' section gives first-party numbers against libopus 1.6.1 with compilers, flags and CPUs stated (GCC 15.1 MinGW-w64 -O3 -march=x86-64-v3, Apple clang 17; Core Ultra 9 185H, Apple M5), but the C program that links every decoder and produced the table is not published: tools/ holds only quality/ (Python metrics) and eval/ (an older Rust harness that times ffmpeg subprocesses), falcon_capi/examples holds roundtrip/decode examples, and no other pbtechlab repo or release asset carries it. Numbers exist, so C rather than D; no public harness, so not A.
- **Verifier notes:** Numbers in claimed_speedup match the README table exactly (1114x vs libopus float 731x, 0.66x time; M5 1551x vs 1056x; 256 voices 291 ms vs 365 ms). No harness found anywhere public, so the record stays first-party C with the different-codec caveat stated; metadata (MIT, last commit 2026-09-29, not a fork) confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/README.md>
  - <https://github.com/pbtechlab/Falcon>
  - <https://github.com/pbtechlab/Falcon/commits>
  - <https://github.com/pbtechlab/Falcon/tree/main/tools>
  - <https://github.com/pbtechlab/Falcon/tree/main/tools/eval>
  - <https://github.com/pbtechlab/Falcon/tree/main/tools/eval/src>
  - <https://github.com/pbtechlab/Falcon/tree/main/tools/quality>
  - <https://github.com/pbtechlab/Falcon/tree/main/falcon_capi>
  - <https://github.com/pbtechlab/Falcon/tree/main/falcon_capi/examples>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/tools/eval/src/main.rs>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/tools/quality/compare.py>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_capi/README.md>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/.cargo/config.toml>
  - <https://github.com/pbtechlab>
  - <https://github.com/pbtechlab/Falcon/releases/tag/v2.0.1>
- **Sources the enricher read:**
  - <https://github.com/pbtechlab/Falcon>
  - <https://github.com/pbtechlab/Falcon/commits/main>
  - <https://github.com/pbtechlab/Falcon/tree/main/falcon_decoder/src>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/README.md>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/PATENTS.md>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_decoder/Cargo.toml>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_decoder/src/decode.rs>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_decoder/src/imdct.rs>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_decoder/src/lib.rs>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_core/Cargo.toml>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_core/src/alloc.rs>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_core/src/lib.rs>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_capi/README.md>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_capi/Cargo.toml>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_capi/src/lib.rs>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_capi/include/falcon.h>
  - <https://raw.githubusercontent.com/pbtechlab/Falcon/HEAD/falcon_capi/include/falcon.hpp>
  - WebSearch: "Falcon" audio codec pbtechlab MDCT Rust libopus decode faster (no independent measurement found)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/pbtechlab/falcon`) · [data/wave10/enrich/raw/github_com_pbtechlab_falcon.json](../../../data/wave10/enrich/raw/github_com_pbtechlab_falcon.json) (enrichment confidence 0.75)

</details>
