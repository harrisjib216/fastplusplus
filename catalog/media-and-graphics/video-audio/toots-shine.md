# Shine (fixed-point MP3 encoder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.0-only` · 🔴 abandoned

> Small fixed-point C MP3 (Layer III) encoder that runs about 2-4x faster than LAME by skipping most of LAME's quality work.

| | |
|---|---|
| **Beats** | LAME 3.100 (M1 Pro run) and LAME 3.99.5 (outdated Raspberry Pi run) CLI, 128 kbps CBR, qval=3, joint stereo with psychoacoustic model |
| **Claimed result** | README, first-party, MacBook Pro M1 Pro (arm64), 2022-12-30: LAME 3.100 at 128 kbps qval=3 reports 88.773x realtime (play/CPU; zsh time 3.609 s total) and Shine 318.0x realtime on a 5:18 stereo 44.1 kHz WAV, about 3.6x faster (derived from page data). The 318.0x is 318 s divided by a whole-second timer reading of 1 s (shineenc uses time()), so the true Shine time could be anywhere under 2 s and the ratio is only bounded below at about 1.8x (derived from page data). Outdated Raspberry Pi run (model not named): LAME 3.99.5 1.8216x (3:06) vs Shine 3.6x (1:35) on a 5:39 file, about 2.0x (derived from page data). Nexus 5: Shine 24.2x realtime, no LAME number. |
| **Workload** | Encoding a 5 min 18 s 44.1 kHz stereo WAV to 128 kbps MP3 with the shineenc CLI versus lame -b 128. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro arm64 M1 Pro (current numbers); Raspberry Pi with model not named and Google Nexus 5 (Shine only) in the outdated section |
| **Compiler and flags** | Not stated for either README run. The repo's Makefile.am builds libshine/shineenc with -O2 -funroll-loops -fno-exceptions -Wall -fsigned-char (compiler not named); the LAME build is a stock 'LAME 3.100 64bits' binary of unknown origin. |
| **Adoption** | 422 stars, 77 forks; github.com/savonet/shine resolves to toots/shine; used as FFmpeg's libshine encoder (issues #22, #28) and by Liquidsoap |
| **Last commit** | 2023-01-01 |
| **Links** | [repository](https://github.com/toots/shine) · [benchmark](https://raw.githubusercontent.com/toots/shine/HEAD/README.md) |

## Verdict

The only numbers are first-party pasted CLI runs from the README: on an M1 Pro (2022-12-30) stock LAME 3.100 -b 128 (qval=3, joint stereo, psychoacoustic model) reports 88.773x realtime by CPU time while shineenc reports 318.0x for a 318 s file, which is 318 s divided by a 1 s reading of whole-second time() wall clock that also includes WAV open and file writes, so Shine's real speed is only bounded to more than about 1.8x LAME's. The code shows Shine skips the psychoacoustic model, block switching, bit reservoir, noise shaping and mid/side, so the ratio compares much less work against LAME at qval=3; the fair comparison (LAME -q 9 or -f) was never run.

## Use it when

- CPUs without an FPU or with weak floating point (ARMv5/armel, MIPS32, microcontrollers): the fixed-point core needs only integer multiplies (issue #29 reports use on STM32).
- Live streaming or transcoding many channels at once (Liquidsoap, FFmpeg -c:a libshine) where CPU per stream matters more than MP3 quality at a given bitrate.
- Constant-bitrate MP3 at 128 kbps or higher where the result only has to decode everywhere (voice, monitoring, previews) and transparency is not required.
- In-browser or Node MP3 encoding through the wasm build; its README reports 46x to 99x realtime on a 5.57 s file in Chrome 108, Firefox 108, Safari 16.2 and Node 19 (first-party, December 2022).

## Skip it when

- Music archiving or any use where quality per bit matters: no psychoacoustic model, no block switching (pre-echo on transients), no bit reservoir and no mid/side stereo, and no quality measurement exists (issue #27 open since 2017).
- Full-scale or clipping-prone input: issue #24 (open since 2017, no reply) reports the output level wobbling on full-amplitude sines, and the README warns the encoder 'may not be exempt of bugs'.
- Bit-exact or strictly valid final frames: issue #37 and the unmerged PR #38 report a truncated last frame, and at HEAD shine_flush() returns only whole 32-bit words, so up to 31 bits left in the bitstream cache are never written.
- VBR/ABR, 24-bit or float input, or LAME-style presets: none are implemented; input is int16 only and bitrate is fixed per encoder.
- Projects needing an active upstream: last commit 2023-01-01, 11 open issues and 5 open PRs (three are dependabot bumps) with no maintainer replies on the bug reports.

## How it is fast

Mostly by doing far less work than LAME, not by a cleverer algorithm. calc_xmin() sets the allowed distortion to zero for every band and the outer loop only binary-searches the global quantizer step (bin_search_StepSize, then the inner rate loop), so there is no psychoacoustic model and no scalefactor noise shaping; only long blocks are coded (no block switching), the bit reservoir is off (ResvMax is fixed at 0, so each granule gets mean_bits and the rest is stuffing), and mode_ext is always 0, so -j only sets the joint-stereo header with no mid/side coding. What remains is a direct-form 32-band polyphase analysis filter and a direct 18x36 MDCT in Q31 fixed point (32x32-to-64-bit multiplies; ARMv6 SMMUL/SMULL and MIPS32 inline asm, plain C int64 elsewhere including AArch64), a 10,000-entry x^(3/4) lookup table for quantization, and loops unrolled by 7.

## Compared with alternatives

Pick Shine over SuperLAME (multi-threaded LAME at LAME quality) when the target has no FPU, only one core per stream, or needs a tiny dependency-free encoder; pick SuperLAME, or glint's LAME 3.100 numbers, whenever MP3 quality at a given bitrate matters.

## Integration

| | |
|---|---|
| **Form** | shared lib or static lib (autotools libshine), or source-drop of the nine src/lib/\*.c files |
| **Dependencies** | libm only (sin/cos/pow at init, log in calc_scfsi, sqrt in the out-of-table quantize path); no other libraries |
| **Minimum toolchain** | C99-era C with GCC-style extensions (statement expressions and inline asm in the ARM and MIPS multiply headers, __attribute__((unused))); Makefile.am adds -O2 -funroll-loops -fsigned-char; Windows needs third-party build files (open PR #40, issue #45) |
| **Platforms** | any with a 64-bit integer multiply; hand-written multiplies for 32-bit ARM (non-Thumb) and MIPS32 only; big-endian via SHINE_BIG_ENDIAN from configure; wasm via emscripten |
| **Thread safety** | not documented; all mutable state lives in the per-encoder shine_t struct (the 2006 conversion made it no-globals) and shared tables are const, so separate encoders on separate threads look safe, but one handle must not be shared |
| **Drop-in for the baseline** | partial: produces standard MP3 that any decoder plays, but the C API differs from libmp3lame's lame_\* API and LAME's quality, VBR and preset options have no equivalent; inside FFmpeg it is a codec swap (-c:a libshine instead of libmp3lame) |

## Gotchas

- Each encode call needs exactly shine_samples_per_pass() samples per channel; the caller pads the last block (shineenc zero-pads), and the returned buffer is only valid until the next call.
- shineenc ignores the WAV data-chunk length (wave.c 'TODO: respect data chunk length'), so trailing chunks after the PCM data are encoded as audio; the library itself is unaffected.
- Joint stereo (-j or JOINT_STEREO) only changes the header: mode_ext is always 0, so channels are coded as plain left/right.
- Issue #39: the padding bit can be wrong at some rate/bitrate pairs (32 kHz/48 kbps reported) because slot accounting uses double arithmetic with truncation in layer3.c.

## Known shortcomings

- README Apple M1 Pro figures (LAME 3.100 at 88.773x realtime vs Shine 318.0x, about 3.6x derived) are single runs with no script or compiler, and shineenc times with time() at 1-second resolution (src/bin/main.c), so 318.0x means 318 s of audio in 1 s and the true ratio is only bounded at about 1.8x or more; the LAME figure is CPU time, Shine's is wall clock. Fixed-point encoder with no psychoacoustic model and plain stereo against LAME qval=3 joint stereo; quality never measured (issue #27 open since 2017); open bugs #24 (full-scale distortion), #37 (final frame truncated), #39 (padding bit at 32 kHz/48 kbps). Raspberry Pi run (model unnamed, outdated): about 2.0x. Last commit 2023-01-01, abandoned.
- The speed comes from skipped work (code-confirmed): calc_xmin is always 0 (no psychoacoustic model or noise shaping), long blocks only, the bit reservoir is off (ResvMax fixed at 0), and mode_ext is always 0 (-j sets the header only, no mid/side), while the LAME baseline at qval 3 does far more work and a fair LAME -q 9 or -f run was never made; timing is whole-second time() wall clock including WAV open and I/O. Bug at HEAD: shine_flush drops up to 31 cached bits (issue #37, PR #38 unmerged). js/package.json declares LGPL-2.0-only.

## Caveats and trade-offs

Speed is bought with lower quality: Shine has no psychoacoustic model (README 'Limitations' says so and calls the algorithm 'rather simple'), encodes plain stereo, while LAME runs its full psychoacoustic model at qval=3 with joint stereo, so the ratio compares different amounts of work at the same bitrate. No quality measurement exists anywhere in the repo (issue #27 'Quality comparison' open since 2017 with no reply). Single runs from pasted CLI output; shineenc's realtime figure uses whole-second time() resolution (src/bin/main.c), so 318.0x means 'finished within about 1 s' and is imprecise. LAME's figure is CPU-time based, Shine's is wall-clock. The two M1 runs used differently named input files (/tmp/decoded.wav, /tmp/bla.wav) of the same length. Open correctness issues: #24 full-amplitude sine input produces distorted output, #37 final frame may be truncated, #39 padding bit wrong at 32 kHz/48 kbps from float truncation in layer3.c; none touches the timing itself. A third-party ARM NAS anecdote on forum.serviio.org (Shine 42 s vs LAME 6:09 on a 3:48 file, '13x faster', little gain on x86) is search-snippet only. README says the code is Gabriel Bouvigne's late-1990s encoder via Pete Everett's fixed-point RISC OS port; issue #25 asks why it is LGPL when the original Shine seemed GPL. Last commit 2023-01-01, more than three years ago.

Fixed-point encoder for CPUs without an FPU; no psychoacoustic model, so quality at a given bitrate is below LAME; LGPL-2.0 (COPYING is GNU Library GPL v2). README notes the encoder may have latent bugs and that work on this fork was limited to reorganizing code into a shared API.

## Maintenance

Abandoned (last commit 2023-01-01, open correctness issues #24, #37, #39 unanswered) but small, dependency-free and LGPL (COPYING is the GNU Library GPL v2 text; js/package.json declares LGPL-2.0-only), so it is copyable as a library or vendored source if LGPL obligations are acceptable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'How fast is it?' section pastes first-party CLI output: on a MacBook Pro M1 Pro (2022-12-30) LAME 3.100 reports 88.773x play/CPU and shineenc reports 318.0x realtime, plus outdated Raspberry Pi runs (LAME 3.99.5 1.8216x, Shine 3.6x). There is no benchmark script, no compiler or flags for either binary, and single runs, so it stays C.
- **Verifier notes:** Numbers match the README exactly; tier C confirmed. Key extra finding: shineenc times with time() at 1 s resolution, so the 318.0x and the derived 3.6x are coarse (true ratio at least about 1.8x); the quality trade-off is unmeasured. COPYING is the GNU Library GPL v2 text with no per-file headers or version clause, so '-only' is not stated anywhere (left uncorrected); forum.serviio.org was EGRESS_BLOCKED.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/toots/shine/HEAD/README.md>
  - <https://github.com/toots/shine>
  - <https://github.com/toots/shine/commits>
  - <https://github.com/savonet/shine>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/COPYING>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/README.old>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/bin/main.c>
  - <https://github.com/toots/shine/tree/main/src/lib>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/types.h>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/mult_noarch_gcc.h>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/mult_sarm_gcc.h>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/layer3.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/l3loop.c>
  - <https://github.com/toots/shine/issues?q=is%3Aissue>
  - <https://github.com/toots/shine/issues/27>
  - <https://github.com/toots/shine/issues/24>
  - <https://github.com/toots/shine/issues/39>
  - <https://github.com/toots/shine/issues/25>
  - <https://github.com/toots/shine/issues/18>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/toots/shine/HEAD/README.md>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/bin/main.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/bin/wave.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/layer3.h>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/layer3.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/types.h>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/l3loop.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/l3mdct.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/l3subband.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/reservoir.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/bitstream.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/bitstream.h>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/l3bitstream.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/huffman.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/tables.c>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/mult_noarch_gcc.h>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/mult_sarm_gcc.h>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/src/lib/mult_mips_gcc.h>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/js/README.md>
  - <https://raw.githubusercontent.com/toots/shine/HEAD/js/package.json>
  - <https://github.com/toots/shine>
  - <https://github.com/toots/shine/issues?q=is%3Aissue>
  - <https://github.com/toots/shine/pulls?q=is%3Apr>
  - <https://github.com/toots/shine/issues/24>
  - <https://github.com/toots/shine/issues/26>
  - <https://github.com/toots/shine/issues/32>
  - <https://github.com/toots/shine/issues/37>
  - <https://github.com/toots/shine/pull/38>
  - <https://github.com/savonet/liquidsoap/discussions/3643>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/toots/shine`) · [data/wave10/enrich/raw/github_com_toots_shine.json](../../../data/wave10/enrich/raw/github_com_toots_shine.json) (enrichment confidence 0.8)

</details>
