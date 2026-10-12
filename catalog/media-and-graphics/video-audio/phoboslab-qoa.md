# QOA (Quite OK Audio)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Single-header C codec for fixed 3.2-bit/sample lossy audio; author's run encodes 12x and decodes 7x faster than ffmpeg Opus.

| | |
|---|---|
| **Beats** | Opus (libopus); also MP3 encoding |
| **Claimed result** | Snippet only (author's post 'QOA Benchmark Results and File Format Specification', blocked here): on a 2 h 43 min (9807 s, 1650 MB) 44.1 kHz stereo track, single-threaded on an i7-6700K, QOA encode 25.752 s and decode 2.996 s; Opus via ffmpeg default settings encode 315.232 s and decode 20.410 s (116 MB file); MP3 via ffmpeg encode 146.223 s and decode 9.631 s (149 MB); Vorbis via ffmpeg decode 8.732 s. Versus Opus 12.2x encode and 6.8x decode; versus MP3 5.7x encode and 3.2x decode (derived from snippet data). The author's informal summary: 'QOA encodes 10x faster and decodes 7x faster than Opus'. The repo README, qoa.h and issues contain no numbers. |
| **Workload** | Single-threaded encode and decode of one 2 h 43 min 44.1 kHz stereo film soundtrack (author's 2023 blog benchmark), QOA's reference implementation versus Opus, MP3 and Vorbis run through the ffmpeg CLI at ffmpeg's default settings with output to /dev/null. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700K, single-threaded (from search snippets of the author's blog post) |
| **Compiler and flags** | Not stated for the benchmark. The repo Makefile builds qoaconv with CC ?= gcc and -std=c99 -O3. |
| **Adoption** | 985 stars; supported in Godot 4.3, raylib, SerenityOS, Qmmp, OpenCubicPlayer |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/phoboslab/qoa) · [benchmark](https://phoboslab.org/log/2023/04/qoa-specification) |

## Verdict

Seen only through search snippets of the author's April 2023 post (blocked here): qoaconv encoded a 2 h 43 min 44.1 kHz stereo WAV (Blade Runner 2049 soundtrack, 1650 MB) in 25.752 s and decoded it in 2.996 s on one thread of an i7-6700K, against 315.232 s / 20.410 s for Opus and 146.223 s / 9.631 s for MP3 through the ffmpeg CLI at default settings, about 12.2x/6.8x versus Opus and 5.7x/3.2x versus MP3 and about 3,270x real-time decode (derived from snippet data). The codecs ran at very different bitrates (QOA 333 MB vs Opus 116 MB), the ffmpeg runs carry CLI overhead, and neither QOA build flags nor the timing method were published; qoaconv only gained its own timing printout in Sep 2024, and it defines QOA_RECORD_TOTAL_ERROR and chooses output format by file extension, so it cannot have written to /dev/null as the ffmpeg runs did (both effects add work on QOA's side, not ffmpeg's).

## Use it when

- Games and engines that play many sound effects or music streams and want near-zero decode CPU; Godot 4.3 (WAV-to-QOA import), raylib's raudio and SerenityOS already ship it.
- Microcontrollers or small embedded players where an Opus or MP3 decoder is too large or too slow: the decoder keeps 8 ints of LMS state per channel and needs one frame buffer (4136 bytes for a stereo frame by QOA_FRAME_SIZE).
- Assets that need cheap random access: frame size is fixed by the channel count, so seek offsets are computed rather than searched (qoaplay seeks this way).
- Fast batch conversion of 16-bit PCM where a fixed 5x size reduction is enough and the quality target is 'often not audible' rather than perceptually optimised.

## Skip it when

- Bandwidth- or storage-bound delivery: in the author's own run QOA produced 333 MB against 116 MB for Opus and 149 MB for MP3 at ffmpeg defaults, and the format has no bitrate control.
- Untrusted input: the README says the implementation has not been fuzzed; 2026 commits fixed a heap overflow from malformed frame lengths (issue #82), out-of-bounds reads on bad slices, an unchecked QOA_MAX_CHANNELS in decode and a buffer-size wrap-around, and crafted frame weights can still push the int32 LMS predictor into signed overflow (weights grow by up to 896 per sample with no clamp; read from source).
- Material where encoder artefacts are unacceptable without checking: open issue #69 (Aug 2025) reports a 5120-sample mono file whose samples 74-240 all encode to -32768, and the third-party brute-force encoder ETDAW (issue #79) exists because qoaconv's greedy per-slice choice leaves audible high-frequency noise on some audio.
- 24-bit, float or more-than-8-channel sources: input is 16-bit only, this implementation caps channels at QOA_MAX_CHANNELS 8 (the spec was clarified to 31 in Sep 2026), and it only handles files with a known total sample count, not the streaming header with samples = 0.

## How it is fast

It is a pure time-domain coder: a 4-tap sign-sign LMS predictor in fixed point predicts each sample, and the residual is quantized to 3 bits against one of 16 per-slice scalefactors, with a lookup table for dequantization. Decoding is one 4-term dot product, one table lookup, one 16-bit clamp (with a rarely taken branch) and four weight updates per sample; there is no transform, psychoacoustic model, entropy coding or bit reservoir. The encoder brute-forces all 16 scalefactors per 20-sample slice, but starts with the previous slice's winner, abandons a candidate as soon as its accumulated squared error exceeds the best so far, and replaces the division by a .16 fixed-point reciprocal multiply. There is no SIMD and no threading; the speed comes from doing very little work per sample.

## Compared with alternatives

Pick QOA over minimp3, nanomp3, Falcon or the libopus ports (opus-rs, ruopus, opuspp) when decode cost, code size and instant seeking matter more than file size and you control both the encoder and the player; pick an Opus implementation for bandwidth-bound delivery and minimp3/nanomp3 when the files are already MP3.

## Integration

| | |
|---|---|
| **Form** | header-only (qoa.h, STB style: define QOA_IMPLEMENTATION in one translation unit) |
| **Dependencies** | none beyond libc: malloc/free (overridable through QOA_MALLOC/QOA_FREE) and stdio for qoa_read/qoa_write unless QOA_NO_STDIO; the qoaconv tool optionally uses dr_mp3.h/dr_flac.h and qoaplay uses sokol_audio.h |
| **Minimum toolchain** | C99 (Makefile: -std=c99 -O3 for qoaconv, -std=gnu99 for qoaplay); callable from C++ through extern "C"; a GCC 15 build failure (issue #73) was closed in Dec 2025 |
| **Platforms** | any: portable scalar C with byte-wise big-endian I/O, no SIMD or intrinsics; qoaplay is marked 'not yet tested on Windows/macOS' in the Makefile |
| **Thread safety** | not documented; the source has no mutable globals (only const tables), so separate qoa_desc instances can run concurrently, but one qoa_desc must not be shared |
| **Drop-in for the baseline** | no |

## Gotchas

- qoa_decode allocates whole 5120-sample frames for the entire file and returns NULL when frames x 5120 x channels exceeds 0x7fffffff samples (about 6.7 h of 44.1 kHz stereo); qoa_read sizes the file with int/ftell, so files over 2 GB fail. Long material should go through qoa_decode_frame.
- qoa_encode computes the output size in unsigned int and does not check the malloc result: with 3 or more channels and more than about 1.07e10 total samples the size wraps and the encoder writes past the buffer. The decoder got the equivalent wrap-around guard in June 2026 (PR #80); the encoder did not.
- The encoder keeps 32-bit LMS weights but stores them in each frame header masked to 16 bits; if a weight leaves the int16 range at a frame boundary the decoder restarts from different weights than the encoder assumed. Open issue #56 asks whether this overflow is intended; the weights penalty in the encoder is what normally keeps them small.
- Driving qoa_encode_frame yourself (streaming encode) means initialising qoa-&gt;lms to weights {0, 0, -8192, 16384} and zero history as qoa_encode does, and only the last frame may be short (since the #82 fix the decoder stops at the first short frame). QOA_FREE is defined only inside the implementation, so callers cannot portably free qoa_decode's buffer with the matching allocator (open issue #64), and defining QOA_MALLOC without QOA_FREE breaks the stdio helpers.

## Known shortcomings

- Different work from Opus: a time-domain codec at about 280 kbit/s against Opus at about 96 kbit/s run through ffmpeg. The repo, qoa.h and issues carry no numbers; the blog table (Opus 315.232/20.410 s against QOA 25.752/2.996 s, 12.2x encode and 6.8x decode derived) is a search snippet of the blocked phoboslab.org post.
- Enricher (e118, 2026-10-05): no correctness bug behind the numbers; C stands. A snippet confirms the QOA side was timed with qoaconv (333 MB vs Opus 116 MB); timing method and build flags are unpublished and qoaconv's timing printout was only added in September 2024. The decoder was hardened in 2026 (#82 heap overflow, out-of-bounds slices, unchecked QOA_MAX_CHANNELS, PR #80 wrap-around). The encoder's size calculation is still unsigned int with the malloc result unchecked (wraps with 3 or more channels and very long input); crafted weights can overflow the int32 LMS predictor; open #69 encoder saturates samples 74-240 to -32768; open #56 weights stored as 16-bit.

## Caveats and trade-offs

Numbers come only from search-result snippets of the author's 2023 blog post (phoboslab.org, qoaformat.org and news.ycombinator.com are blocked here); the repo has no benchmark harness (qoaconv only prints clock() timings for its own decode/encode). Different work: QOA is a fixed-rate time-domain codec at 3.2 bits per sample (about 280 kbit/s for 44.1 kHz stereo, roughly 330 MB here, derived from qoa.h), while Opus at ffmpeg's default bitrate produced 116 MB (about 95-99 kbit/s, derived from snippet data) using a transform codec with psychoacoustic analysis, so the speed gap compares different bitrates and quality targets. Opus and MP3 timings include ffmpeg CLI overhead (the author notes ffmpeg's considerable overhead) and, for Opus, resampling 44.1 kHz to 48 kHz. The code has changed since 2023 (2026 fixes for out-of-bounds access and integer wrap-around in decoding). The README warns the implementation has not been fuzzed and must not be used with untrusted input. A Hacker News commenter argues QOA is slower than ADPCM and compresses less than MP3. Ports (qoa-fu, qoaudio, goqoa, qoa-format and others) are reimplementations of the same format.

Fixed-rate lossy time-domain codec (LMS predictor plus quantisation), far simpler than Opus. HN comment snippets say Opus is better in every way except complexity and CPU cost, and that QOA compresses less than MP3 and sounds worse. Best fit is games or microcontrollers that need cheap decoding. Single-header C/C++ API. Format has a 31 channel limit (latest commit message).

## Maintenance

Actively maintained (last commit 2026-09-27; most 2026 commits harden the decoder against malformed files after outside reports), MIT-licensed and a single 759-line header that is trivial to vendor, but still unfuzzed by the author's own README.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo (README, qoa.h, qoaconv.c, Makefile, issues) has no comparison numbers; the only numbers are the author's 2023 blog benchmark table (phoboslab.org, blocked here) seen through search snippets, which name the file, CPU (i7-6700K) and single-threaded ffmpeg default settings but no QOA build flags or harness. Snippet-only first-party numbers cap it at C.
- **Verifier notes:** Kept at C under the snippet-only rule: the blog URL came from search results and could not be opened, so page_compares_against_baseline and numbers_found_on_page are null; two separate snippets gave a consistent table. Notable (985 stars, 57 forks, used by Godot 4.3, raylib, SerenityOS); MIT and last commit 2026-09-27 confirmed on github.com.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** first-party timing
- **Pages the verifier opened:**
  - <https://github.com/phoboslab/qoa>
  - <https://raw.githubusercontent.com/phoboslab/qoa/HEAD/README.md>
  - <https://raw.githubusercontent.com/phoboslab/qoa/HEAD/qoa.h>
  - <https://raw.githubusercontent.com/phoboslab/qoa/HEAD/qoaconv.c>
  - <https://raw.githubusercontent.com/phoboslab/qoa/HEAD/Makefile>
  - <https://github.com/phoboslab/qoa/commits>
  - <https://github.com/phoboslab/qoa/issues?q=is%3Aissue+speed>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/phoboslab/qoa/HEAD/README.md>
  - <https://raw.githubusercontent.com/phoboslab/qoa/HEAD/qoa.h>
  - <https://raw.githubusercontent.com/phoboslab/qoa/HEAD/qoaconv.c>
  - <https://raw.githubusercontent.com/phoboslab/qoa/HEAD/qoaplay.c>
  - <https://raw.githubusercontent.com/phoboslab/qoa/HEAD/Makefile>
  - <https://raw.githubusercontent.com/phoboslab/qoa/HEAD/LICENSE>
  - <https://github.com/phoboslab/qoa/commits>
  - <https://github.com/phoboslab/qoa/issues?q=is%3Aissue>
  - <https://github.com/phoboslab/qoa/issues/87>
  - <https://github.com/phoboslab/qoa/issues/69>
  - <https://github.com/phoboslab/qoa/issues/79>
  - <https://github.com/phoboslab/qoa/issues/56>
  - <https://github.com/phoboslab/qoa/issues/82>
  - WebSearch snippet of https://phoboslab.org/log/2023/04/qoa-specification (page itself blocked)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/phoboslab/qoa`) · [data/wave10/enrich/raw/github_com_phoboslab_qoa.json](../../../data/wave10/enrich/raw/github_com_phoboslab_qoa.json) (enrichment confidence 0.7)

</details>
