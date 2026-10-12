# HALAC (High Availability Lossless Audio Compression)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `MIT` · 🟢 active

> Fast lossless audio codec, closed Windows binaries plus an early MIT source; encodes 2.2-4.4x faster than FLAC 1.5.0 at similar size.

| | |
|---|---|
| **Beats** | FLAC 1.5.0 (flac CLI) at -8 and -5. The 0.5.4 notes also list WavPack 5.9.0 -h and HALAC 0.5.1. Monkey's Audio, WavPack and OptimFROG (versions not stated) appear only in the 0.4.8 notes for the 32-bit float set. |
| **Claimed result** | Release 0.5.4 notes, 'AMD Ryzen 9 9600X, Single Thread', six BipTunia albums, 5,883,941,384 bytes of 24-bit/44.1 kHz stereo WAV. HALAC 0.5.4 -plus: 4,232,751,891 bytes, 11.578 s encode, 13.201 s decode. FLAC 1.5.0 -8: 4,243,522,638 bytes, 50.802 s, 14.357 s. That is about 4.4x faster encode and 1.09x faster decode with 0.25% smaller output (derived from page data). HALAC 0.5.4 -normal: 4,268,470,589 bytes, 7.200 s, 9.353 s. FLAC 1.5.0 -5: 4,265,600,750 bytes, 15.857 s, 13.451 s. That is about 2.2x faster encode and 1.44x faster decode with 0.07% larger output (derived from page data). WavPack 5.9.0 -h: 4,263,185,834 bytes, 64.855 s, 49.367 s. Release 0.4.8 notes, 29 tracks of 32-bit float stereo, 2,089,718,160 bytes, 'HALAC AVX2 Single thread', no FLAC row. HALAC normal 1,381,439,835 bytes, 3.050 s / 4.290 s, versus WavPack fast 1,392,225,168 bytes, 20.675 s / 13.914 s, and OptimFROG fast 1,346,477,460 bytes, 39.310 s / 32.179 s. |
| **Workload** | Single-thread encode and decode of six BipTunia albums, 24-bit 44.1 kHz stereo, about 5.88 GB, release 0.5.4 notes; a separate 29-song 32-bit float set (about 2 GB) in release 0.4.8 notes. |
| **Metric** | throughput |
| **Hardware** | 'AMD Ryzen 9 9600X' as written in the 0.5.4 notes (AMD sells the 9600X as a Ryzen 5), single thread. OS not stated; the release assets are Windows .exe files. |
| **Compiler and flags** | Not stated. 0.5.4 ships closed Windows executables built for AVX, AVX2 and AVX512, and the notes do not say which was timed; the 0.4.8 notes say 'HALAC AVX2 Single thread'. FLAC 1.5.0 build and options beyond -8/-5 are not stated. |
| **Adoption** | 48 stars |
| **Last commit** | 2025-11-17 |
| **Links** | [repository](https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression) · [benchmark](https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/tag/0.5.4) |

## Verdict

The author's 0.5.4 notes time single-threaded encode and decode of six albums (5.88 GB, 24-bit/44.1 kHz stereo, about 6.2 hours) on an AMD Ryzen 9600X: HALAC -plus 11.578 s / 13.201 s vs FLAC 1.5.0 -8 50.802 s / 14.357 s at 0.25% smaller output, and -normal 7.200 s / 9.353 s vs FLAC -5 15.857 s / 13.451 s at 0.07% larger output. OS, compilers, FLAC build and options, timing method and the audio are not given. The FLAC and WavPack rows are copied unchanged from the 0.5.1 notes of March 4 rather than re-run with 0.5.4.

## Use it when

- You control both encoder and decoder (archive or cache on Windows x64) and encode speed matters more than format interoperability: the first-party run shows about 1,900x realtime for -plus and 3,100x for -normal on one core for 24-bit/44.1 kHz stereo (derived from page data).
- Bulk re-encoding of large 24-bit stereo or multichannel libraries where FLAC -8's encode time is the bottleneck and the size target is about FLAC -8 (-plus was 0.25% smaller in the author's set).
- 32-bit float stereo (0.4.8 notes) or many-channel float audio (0.6.6 adds 128 channels for float), which FLAC does not support at all.
- As a reference design for a low-complexity lossless audio coder that pairs a fixed LPC with FSE/Huff0 entropy coding (v0.1.9 source, MIT).

## Skip it when

- Anything that needs a published, stable format or players and tools that understand it: .halac has no spec, no FLAC-style ecosystem or tagging, and is versioned only by a closed binary that changes every few weeks.
- Linux, macOS, ARM, or embedding as a library: releases are Windows x64 .exe files only, and the source is a 16-bit-stereo CLI from 2024-2025 that cannot reproduce any published 24-bit or float result.
- Archival where silent corruption matters: the public v0.1.9 format stores no MD5 or CRC, and integrity checks in 0.5.4+ are not documented. FLAC verifies a whole-stream MD5 and per-frame CRCs.
- Maximum compression: in the 0.4.8 float set OptimFROG fast was 2.5% smaller, and at -normal HALAC matches FLAC -5 size, not -8.
- Building from the repository source for real use: see gotchas. v0.1.9 has a decoder overflow-index bug and unchecked WAV header parsing.

## How it is fast

In the public v0.1.9 code each 24 KiB block is split into channels, mid/side transformed (X = L - R, Y = R + X/2), and delta coded. An order-8 Levinson-Durbin LPC (double precision, coefficients stored as float) then predicts each sample. Each zigzagged residual is split into a high byte, coded with Yann Collet's FSE (tANS), and a low byte, coded with his Huff0, with an escape list for values at or above 65535. One fixed-order predictor per block plus table-driven ANS/Huffman decoding is far cheaper than FLAC -8's search over orders, apodizations and Rice partitions. The faster 0.4.x-0.6.x builds add AVX2/AVX-512, multithreading, compression levels and 'Rice coding overflow control' (0.4.9 notes), so the shipped codec also uses Rice coding somewhere. Its internals are not public.

## Compared with alternatives

Choose HALAC over flacenc-rs or go-flac only when FLAC compatibility does not matter and you run Windows x64. flacenc-rs beats flac -8 by about 1.44x but loses to -5, while HALAC's first-party numbers beat both presets, but its output is readable only by HALAC. For anything that must decode in standard players, or a library you can build and audit, stay with libFLAC or flacenc-rs; libfoxenflac and Symphonia cover fast FLAC decoding.

## Integration

| | |
|---|---|
| **Form** | Measured versions: closed Windows x64 executables (0.5.4: HALAC_ENCODE_0.5.4_AVX/AVX2/AVX512.exe plus one HALAC_DECODE_0.5.4.exe; 0.6.6: an x64_avx2 encoder and x64 decoder). Public: source-drop of two v0.1.9 CLI programs with no library API. |
| **Dependencies** | v0.1.9: vendored FiniteStateEntropy (FSE 0.9.x plus Huff0, Yann Collet, dual BSD/GPLv2) in FSE/; standard library only otherwise |
| **Minimum toolchain** | v0.1.9: C++17 (std::filesystem) with GCC or Clang. It relies on variable-length arrays, a GNU extension that MSVC rejects. No build files are provided. |
| **Platforms** | Releases: Windows x64 only (AVX, AVX2 or AVX-512 encoder builds in 0.5.4). v0.1.9 source: little-endian only (raw memcpy of u32/float fields and native-endian WAV header reads); no SIMD. |
| **Thread safety** | v0.1.9: not thread-safe or re-entrant (file handles, header fields and sizes are globals). The multithreaded release binaries are closed and their threading model is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- v0.1.9 decoder bug: escape values are indexed with `u8 counter`, while the encoder's escape count is a u16 (up to 6,144 per channel block). With more than 256 escaped residuals (|residual| of about 32768 or more) in one channel block, the counter wraps and the decoder silently adds the wrong overflow values. Loud, noisy or wide-stereo 16-bit material (for example full-scale white noise) would not round-trip, and with no checksum nothing reports it.
- v0.1.9 input handling: `block_count = INPUT_SIZE / BLOCK_SIZE - 1` is unsigned, so PCM shorter than 24,576 bytes (about 0.14 s of CD audio) underflows to 4,294,967,295 iterations. A WAV with a non-'data' chunk larger than 16 KiB overflows the global METADATA[16384] buffer, in the encoder and, through crafted .halac files, the decoder. WAVE_FORMAT_EXTENSIBLE or fmt chunks other than 16 bytes are misparsed.
- The predictor is floating point (double accumulation of float coefficients, truncated with (int)), so encoder and decoder must round identically. The 0.5.4 release pairs three ISA-specific encoders (AVX/AVX2/AVX-512) with one decoder. If the closed builds keep this predictor and the compiler contracts multiply-adds into FMA differently, cross-build output could differ by one LSB. This is an unverified inference, and no cross-build test is published.
- v0.1.9 keeps a 1 MiB output buffer plus VLAs on the stack, so it needs more than a 1 MiB thread stack.

## Known shortcomings

- Reference only: the measured HALAC 0.5.4 is a closed Windows executable (release notes: AMD Ryzen 9 9600X, single thread; -plus vs FLAC -8 4.4x encode, -normal vs -5 2.2x encode with output 0.07% larger; no script, OS, compiler or AVX build named). The published source is v0.1.9, 16-bit stereo only, which cannot encode the 24-bit test set and computes no MD5 or CRC while FLAC does by default, so the integrity work differs.
- Usability set to reference (retier-12): the catalogued 0.5.4 numbers come from closed binaries, and the public v0.1.9 decoder silently corrupts output past 256 escapes per channel block (u8 counter against a u16 count) with no checksum, plus an unsigned underflow on PCM under 24,576 bytes and a METADATA[16384] overflow. The 0.5.4 table's FLAC and WavPack rows are copied unchanged from the 0.5.1 table; FLAC's MD5 verification likely accounts for part of the decode gap (inference). Not ANS-only (0.4.9 notes mention Rice coding).

## Caveats and trade-offs

First-party release-note numbers with no benchmark script, compiler, OS or timing method, and the test albums are not distributed, so tier C. The measured code is not public. The repository source is only v0.1.9 (halac_encode/decode_v.0.1.9 plus FSE), last changed 2025-11-17. Its encoder prints 'Only 16 bit, 2 channels .wav types are supported for input!', reads 2-byte samples, and its main() walks a hard-coded Windows test directory, so it cannot even encode the 24-bit benchmark set. The release 'Source code' archives for 0.4.8 and 0.5.4 are that same 2025-11-17 snapshot, and the 0.5.4 encoder exists only as HALAC_ENCODE_0.5.4_AVX/AVX2/AVX512.exe (2026-04-10). The comparison names the machine and the settings (single thread; HALAC -plus vs FLAC -8 and -normal vs FLAC -5, levels paired by similar output size). It does not say whether FLAC's default whole-stream MD5 and per-frame CRCs were left on. The public v0.1.9 encoder computes no MD5 or CRC, so if 0.5.4 also skips them, the two encoders do different integrity work. The headline 4.4x is against FLAC's slowest standard preset; against -5 it is 2.2x encode, and the decode gap is small (1.09x to 1.44x). Releases continue to 0.6.6 (dated 26 Sep, year not shown). Independent threads on hydrogenaudio and encode.su exist but are blocked from this environment. FLAC is not in this category's baseline list. [retier] Closed-source binaries produce the catalogued numbers; the public v0.1.9 decoder corrupts output silently past 256 escapes per channel block (u8 counter against a u16 count) and has an unsigned underflow on PCM under 24,576 bytes and a METADATA[16384] overflow. The 0.5.4 table's FLAC and WavPack rows are copied from the 0.5.1 table, not re-run; FLAC verifies MD5 while HALAC checks nothing. Not ANS-only (0.4.9 notes mention Rice coding).

Uses ANS (FSE) entropy coding instead of Rice coding, trading a few percent of compression for speed; OptimFROG compresses better. Releases cover 16/24-bit and 32-bit float PCM and up to 128 channels. No SIMD/GPU in early versions, AVX2 and multithreading added from 0.4.3.

## Maintenance

Releases are active (0.6.6 on 2026-09-26, adding 128-channel float), but the repository source has not moved past v0.1.9 (last commit 2025-11-17, 13 commits, every release's 'Source code' archive is that snapshot). The MIT code is an early 16-bit prototype with a lossless-roundtrip bug, so 'reference' fits better than 'mixed'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The 0.5.4 release notes give first-party single-thread timings and sizes for HALAC -plus/-normal against FLAC 1.5.0 -8/-5 and name the CPU ('AMD Ryzen 9 9600X'). There is no benchmark script, OS, compiler, FLAC build or timing method, the test albums are not distributed, and the measured 0.5.4 encoder is a closed Windows binary. That is tier C.
- **Verifier notes:** Confirmed at C with has_code set to false: the benchmarked 0.5.4 build is binary-only, and the repo's v0.1.9 source is a 16-bit-only early version that cannot reproduce the 24-bit test. usability left as 'mixed' (MIT v0.1.9 source copyable, measured version closed). The orchestrator may prefer 'reference'. Metadata checked: MIT, 48 stars, 4 forks, not a fork, last commit 2025-11-17 (active), latest release 0.6.6.
- **Fields the verifier corrected:** `has_code`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`, `usability`
- **Pages the verifier opened:**
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/commits>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/tag/0.5.4>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/expanded_assets/0.5.4>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/tag/0.4.8>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/expanded_assets/0.4.8>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/tag/0.6.6>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/README.md>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/halac_encode_v.0.1.9.cpp>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/halac_encode_v.0.1.9.h>
- **Sources the enricher read:**
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/tree/main/FSE>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/tag/0.5.4>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/tag/0.5.1>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/tag/0.4.9>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/expanded_assets/0.5.4>
  - <https://github.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/releases/expanded_assets/0.6.6>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/README.md>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/halac_encode_v.0.1.9.cpp>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/halac_encode_v.0.1.9.h>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/halac_decode_v.0.1.9.cpp>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/halac_decode_v.0.1.9.h>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/FSE/fse.h>
  - <https://raw.githubusercontent.com/Hakan-Abbas/HALAC-High-Availability-Lossless-Audio-Compression/HEAD/FSE/huf_compress.c>
  - WebSearch snippets only (pages not opened): https://hydrogenaudio.org/index.php/topic,125248.0.html and https://encode.su/threads/4180-HALAC(High-Availability-Lossless-Audio-Compression)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/hakan-abbas/halac-high-availability-lossless-audio-compression`) · [data/wave10/enrich/raw/github_com_hakan_abbas_halac_high_availability_lossless_audio_compression.json](../../../data/wave10/enrich/raw/github_com_hakan_abbas_halac_high_availability_lossless_audio_compression.json) (enrichment confidence 0.7)

</details>
