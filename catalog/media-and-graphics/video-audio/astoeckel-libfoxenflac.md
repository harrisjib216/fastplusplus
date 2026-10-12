# libfoxenflac

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1-or-later` · 🟡 stale

> Tiny C99 FLAC decoder with no libc and no heap use; author claims about 25% faster than the flac CLI.

| | |
|---|---|
| **Beats** | flac command-line reference decoder application (Xiph flac, built on libFLAC); no comparison against libFLAC's API, FFmpeg or dr_flac is published |
| **Claimed result** | "reasonably fast, being about 25% faster than the flac reference decoder application on x86_64 systems"; performance on ARM6 "significantly worse". |
| **Workload** | FLAC decoding on x86_64; README does not state the file, flags or timing method. |
| **Metric** | throughput |
| **Adoption** | 84 stars |
| **Last commit** | 2025-03-29 |
| **Links** | [repository](https://github.com/astoeckel/libfoxenflac) · [benchmark](https://github.com/astoeckel/libfoxenflac) |

## Verdict

The only speed evidence is one 2018 README sentence: about 25% faster than the flac command-line decoder on x86_64, with no file, machine, compiler, flags, flac version (likely 1.3.2, the release current then) or timing method, and no harness in the repo. That baseline does different work: flac -d always enables MD5 checking (FLAC__stream_decoder_set_md5_checking(..., true) in src/flac/decode.c) and writes a WAV file, while libfoxenflac computes no MD5 and may or may not have had CRCs enabled (FX_FLAC_NO_CRC). So the figure compares a stripped decoder with a full CLI pipeline, not library against library.

## Use it when

- Microcontrollers, bare-metal firmware or WASM builds that must decode FLAC with no C runtime and no malloc (8.8 KiB of WebAssembly per the README).
- Streaming playback where FLAC bytes arrive in arbitrary chunks (network, DMA buffers) and you want a push-style decoder with no callbacks.
- 16- or 24-bit, 1-8 channel Subset files, where the integration tests compare every sample against the flac reference decoder; 48 kHz stereo needs only about 40 KiB of decoder state.
- Projects that want to vendor two source files (src/foxen-flac.c and src/foxen-flac.h) instead of building libFLAC.

## Skip it when

- As a desktop or server throughput choice: there are no published numbers against libFLAC's library API, FFmpeg or dr_flac, and the bit-at-a-time Rice loop is simpler than libFLAC's word-wise count-leading-zeros reader. The author calls the code 'not optimized' and says ARM6 performance is 'significantly worse'.
- 32-bit FLAC (written by FLAC 1.4.0 and later, defined in RFC 9639): sample-size code 7 maps to -1 in fx_flac_sample_sizes_, so every frame header is rejected, and 33-bit side channels cannot fit the int32 buffers. The README's 'Supports all FLAC features' predates 32-bit FLAC.
- Seeking, cue sheets, tags, pictures or ReplayGain: none of these are implemented, and seeking is explicitly out of scope.
- When you need integrity verification of the decoded audio: the STREAMINFO MD5 is exposed but never computed.
- Proprietary static linking without LGPL obligations: the licence is LGPL-2.1-or-later (since March 2025), so vendoring the .c file into closed code brings relinking terms.

## How it is fast

Mostly by doing less, not by clever kernels: there is no MD5 computation, no file or WAV output, no allocation and no metadata parsing beyond STREAMINFO. The hot loops are plain C: a 64-bit MSB-first bit buffer refilled one byte at a time, Rice residuals whose unary prefix is read one bit per call, CRC-8/CRC-16 updated per byte through a table-driven callback, and a generic int64-accumulator LPC restore loop for every order; no SIMD and no count-leading-zeros tricks. libFLAC's current decoder, by contrast, reads Rice blocks word-wise with count-leading-zeros (plus a BMI2 variant), updates CRC-16 over whole words and has order-specialised LPC restore with 32-bit accumulation when safe. A compile-time switch FX_FLAC_NO_CRC (off by default, under #if 0) drops all CRC checks, which the source says makes the decoder 'significantly faster'.

## Compared with alternatives

Pick it over Symphonia or rusty_flac when the target is C or C++ with no runtime and no heap (MCU, WASM, kernel-like code) and footprint matters more than speed; those Rust siblings publish measured decode-speed tables against FFmpeg, which libfoxenflac does not. go-flac is an encoder and does not compete.

## Integration

| | |
|---|---|
| **Form** | source-drop (two files) or Meson-built static/shared library |
| **Dependencies** | none (only assert.h, stddef.h, stdint.h, stdbool.h); the FX_FLAC_ALLOC_\* convenience macros call malloc |
| **Minimum toolchain** | C99 compiler; Meson for the tests; MSVC 19.28 (Visual Studio 2019) fixes merged in PR #7; Emscripten for WASM |
| **Platforms** | any: x86_64, ARM (Arduino support merged Feb 2025), WebAssembly; plain C with no SIMD |
| **Thread safety** | Per instance: one decoder decodes one stream at a time and has no global mutable state (only static const tables), so separate instances can run in separate threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- Output samples are left-justified to fill the whole int32 (decoded value shifted left by 32 minus bit depth); shift right by (32 - FLAC_KEY_SAMPLE_SIZE) to get native PCM.
- Errors after the metadata are not reported: a CRC mismatch, a reserved value, or a frame whose block size or channel count exceeds what the instance was sized for makes the decoder silently resynchronise to the next frame, so an undersized FX_FLAC_ALLOC_SUBSET_FORMAT_DAT() instance drops audio without an error.
- The integration test (test_flac_integration.c) only checks 16- and 24-bit files against flac -d and skips other bit depths with 'we're probably fine'; the runner covers the IETF flac-test-files subset/ directory but not uncommon/ (which holds the 32 bps, changing-bitdepth and 768 kHz files).
- README build notes look stale: it says to add flac.c and flac.h (the files are src/foxen-flac.c/.h) and its emcc command names subprojects/libfoxenbitstream, whose code is now copied into foxen-flac.c.

## Known shortcomings

- One README sentence (2018-08-05): 25% faster than the flac CLI application on x86_64, with no machine, compiler, flags or benchmark code, and nothing against the libFLAC API, FFmpeg or dr_flac. The CLI likely verifies MD5 and writes a file while libfoxenflac never computes MD5, so the work may differ. Licence LGPL-2.1-or-later.
- The 25% claim compares unlike work: the flac reference application always verifies MD5 (src/flac/decode.c) and writes WAV, while libfoxenflac computes no MD5 and its CRC checking may be off (FX_FLAC_NO_CRC). The decoder hot loop is scalar (unary Rice read one bit per call, per-byte CRC callback, generic int64 LPC loop) against libFLAC's word-wise CLZ Rice, word CRC16 and order-specialised LPC, so a library-versus-library win is unlikely. 32-bit FLAC (FLAC 1.4.0+, RFC 9639) is rejected (fx_flac_sample_sizes_[7] = -1) although the README claims all FLAC features; tests cover the IETF subset only; an undersized instance drops frames silently; README build paths are stale.

## Caveats and trade-offs

Single README sentence from August 2018 (so the flac decoder of that era, likely 1.3.x), no numbers beyond '25%', no benchmark code, no machine, compiler or flags stated, and no input files named. The baseline is the flac command-line application, which also writes an output file and, as far as I know, verifies the stream MD5 by default, whereas libfoxenflac stores the STREAMINFO MD5 field but never computes it (CRC checks are on by default), so the two may not do the same work. No comparison against libFLAC's API, FFmpeg or dr_flac exists. The author says the code is not optimised and that ARM6 performance is significantly worse. Re-licensed to LGPL-2.1-or-later in March 2025. Last commit 2025-03-29 (README fix).

Tiny C99 decoder with no libc dependency and no heap allocation (8.8 kiB of WebAssembly); callable from C++. No seeking, no metadata other than STREAMINFO, no frame-header access. Decoder only (no encoder).

## Maintenance

Stale (last commit 2025-03-29, a README fix, after the Feb 2025 Arduino support PR and the March 2025 relicence), 84 stars and no open issues, but it is small, dependency-free and LGPL-2.1-or-later, so it is easy to vendor for embedded or WASM decoding as long as 32-bit FLAC is not needed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** A single first-party README sentence ('about 25% faster than the flac reference decoder application on x86_64 systems', last changed in commit 7eb71412 on 2018-08-05) with no benchmark code, machine, compiler, flags or input files; the repo's test/ directory holds only correctness tests (test_flac_integration_runner.py compares output with the flac decoder and times nothing).
- **Verifier notes:** The claim is real but thin and dated: no machine is stated, the baseline is the flac CLI rather than libFLAC itself, and nothing was published against dr_flac or FFmpeg (one WebSearch found no independent numbers). Metadata confirmed: 84 stars, LGPL-2.1-or-later, not a fork, last commit 2025-03-29, so stale.
- **Fields the verifier corrected:** `baseline`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/README.md>
  - <https://github.com/astoeckel/libfoxenflac>
  - <https://github.com/astoeckel/libfoxenflac/commits>
  - <https://github.com/astoeckel/libfoxenflac/blame/master/README.md>
  - <https://github.com/astoeckel/libfoxenflac/tree/master/test>
  - <https://github.com/astoeckel/libfoxenflac/tree/master/examples>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/test/test_flac_integration_runner.py>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/test/test_flac_integration.c>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/meson.build>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/src/foxen-flac.c>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/examples/flac_decoder.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/README.md>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/meson.build>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/src/foxen-flac.c>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/src/foxen-flac.h>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/examples/flac_decoder.c>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/test/test_flac_integration.c>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/test/test_flac_integration_runner.py>
  - <https://raw.githubusercontent.com/astoeckel/libfoxenflac/HEAD/LICENSE>
  - <https://github.com/astoeckel/libfoxenflac/tree/master/test>
  - <https://github.com/astoeckel/libfoxenflac/issues?q=is%3Aissue>
  - <https://github.com/astoeckel/libfoxenflac/issues/4>
  - <https://github.com/astoeckel/libfoxenflac/issues/8>
  - <https://github.com/astoeckel/libfoxenflac/issues/9>
  - <https://github.com/astoeckel/libfoxenflac/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/xiph/flac/HEAD/src/flac/decode.c>
  - <https://raw.githubusercontent.com/xiph/flac/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/xiph/flac/HEAD/src/libFLAC/bitreader.c>
  - <https://raw.githubusercontent.com/xiph/flac/HEAD/src/libFLAC/lpc.c>
  - <https://github.com/ietf-wg-cellar/flac-test-files/tree/main/uncommon>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/astoeckel/libfoxenflac`) · [data/wave10/enrich/raw/github_com_astoeckel_libfoxenflac.json](../../../data/wave10/enrich/raw/github_com_astoeckel_libfoxenflac.json) (enrichment confidence 0.75)

</details>
