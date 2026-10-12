# minimp3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `CC0-1.0` · 🟢 active

> CC0 single-header float MP1/MP2/MP3 decoder with SSE2/NEON paths; ISO-conformant and 2.0-6.4x fewer cycles per file than keyj's minimp3.

| | |
|---|---|
| **Beats** | keyj's minimp3 (Martin J. Fiedler's fixed-point single-file MP3 decoder, https://keyj.emphy.de/minimp3/) |
| **Claimed result** | README tables (clockticks, lower is better): compl.bit 14,306,684 vs 31,849,373 for keyj's minimp3 (about 2.2x fewer, derived from page data); he_44khz 21,296,300 vs 41,628,861 (about 2.0x, derived); hecommon 3,169,715 vs 20,437,779 (about 6.4x, derived); sin1k0db 24,842,977 vs 55,569,636 (about 2.2x, derived). Conformance: PSNR 107-144 dB for this minimp3 versus 0.15-72 dB for keyj's, which fails conformance on all vectors. |
| **Workload** | Decoding the ISO/IEC 11172-4 and 13818-4 MP3 conformance vectors (compl.bit, he_\*.bit, si\*.bit, sin1k0db.bit); CPU clockticks measured with perf, I/O included. |
| **Metric** | throughput |
| **Hardware** | i7-6700K, speedstep effects avoided, measured with perf |
| **Adoption** | 2.0k stars; basis of dr_mp3 |
| **Last commit** | 2026-07-27 |
| **Links** | [repository](https://github.com/lieff/minimp3) · [benchmark](https://github.com/lieff/minimp3) |

## Verdict

The README times whole decoder processes with perf (clockticks, i7-6700K, compiler and flags not stated, file I/O included) on the ISO conformance vectors: compl.bit 14.3M vs 31.8M cycles for keyj's fixed-point minimp3 (2.2x), he_44khz 21.3M vs 41.6M (1.95x), hecommon 3.2M vs 20.4M (6.4x), sin1k0db 24.8M vs 55.6M (2.2x), while keyj's decoder fails conformance on every vector. A fit over the ten vectors puts keyj's cost at about 14M cycles fixed per run plus 1.48x minimp3's cycles (derived from page data), so on long files the gap is closer to 1.5x than the per-file 2-6x.

## Use it when

- Games, tools and apps that need to play or load MP3 (and MP1/MP2) assets with a dependency-free, vendorable single header and no licence friction (CC0).
- Many short clips or sound effects decoded at load time: there is no runtime table set-up, which is where its lead over keyj's decoder is largest (hecommon.bit, 1.6 s of audio: 3.2M vs 20.4M cycles).
- x86-64 or aarch64 targets, where the SSE2/NEON paths are always on; a scalar build (MINIMP3_NO_SIMD) still exists for other CPUs.
- You need ISO-conformant output (README: PSNR above 96 dB on all ISO vectors), free-format streams, or sample-accurate seeking through minimp3_ex.h.

## Skip it when

- Untrusted or attacker-supplied files without sandboxing or fuzzing of your own: open reports include OOB reads in the core L3_huffman (#145, unfixed), a heap OOB read in mp3dec_ex_read_frame after a seek (#147), an integer overflow in Xing/Info parsing leading to a \~10 TB allocation request (#140), and an MSan uninitialised-value report in mp3dec_decode_frame (#141).
- You need evidence that it is the fastest MP3 decoder: the repo has no numbers against libmpg123, FFmpeg or dr_mp3, and in Rust nanomp3 reports higher throughput than minimp3's SIMD build (76.0 vs 71.9 MiB/s on 48 kHz stereo 320 kb/s).
- Small MCUs with no FPU or very tight RAM: decoding is float, each mp3dec_t is about 6.7 KB, and mp3dec_decode_frame puts about 16 KB of scratch on the stack.
- Anything beyond MPEG audio decoding (encoding, AAC, Opus, container demuxing), or projects that need tagged releases and a stable version number (none exist; issue #152 asks for them).

## How it is fast

It is a floating-point rewrite instead of keyj's fixed-point FFmpeg port: stereo processing, antialias butterflies, the 36-point IMDCT, the 32-band DCT-II and the polyphase synthesis window all have 4-wide float SIMD paths through a small macro layer (VLD/VMAC/VMUL over SSE or NEON intrinsics). Huffman decoding uses a 32-bit bit cache with peek/flush macros. Dequantisation (n^(4/3)) uses a 145-entry table plus a quadratic correction instead of a large runtime-built table, and all tables are static const, so there is no init-time table generation. On x86-64 and aarch64 the SIMD path is compiled in unconditionally (MINIMP3_ONLY_SIMD); 32-bit x86 checks for SSE2 with cpuid.

## Compared with alternatives

Pick minimp3 in C or C++ when you want a tiny CC0 MP3-only decoder you can vendor as one header; in Rust, nanomp3 (faster than minimp3 in its own benchmark) or Symphonia (many codecs, measured against FFmpeg's decoders) are the better catalogued choices.

## Integration

| | |
|---|---|
| **Form** | header-only (minimp3.h, plus optional minimp3_ex.h); define MINIMP3_IMPLEMENTATION in exactly one translation unit |
| **Dependencies** | none beyond the C standard library (the test program links -lm); minimp3_ex.h's file functions use stdio and can be excluded with MINIMP3_NO_STDIO |
| **Minimum toolchain** | C89: CI builds the test program with gcc -O2 -std=c89 -Wall -Wextra -Werror; also usable from C++ (extern "C" guards). |
| **Platforms** | any C target; SSE2 on x86 (always on x86-64, cpuid-detected on 32-bit x86), NEON on aarch64 and on 32-bit ARM when built with NEON, ARMv6 saturating clip on ARMv6 (no longer enabled for ARMv6-M since Jul 2026), scalar fallback otherwise |
| **Thread safety** | Not documented. From the code: all decoder state lives in the caller's mp3dec_t plus a stack scratch struct, and tables are static const, so separate decoders on separate threads are independent; the only global is a lazily set SSE2-detection flag in 32-bit x86 builds. Never share one mp3dec_t between threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- Feed it enough data: mp3dec_decode_frame needs at least one full frame, short buffers can false-sync and produce 'squealing' artefacts, the README recommends about 16 KB (10 frames) per call, free-format streams need 3 frames, and trailing ID3v1/APE tags should be stripped first.
- Return values are overloaded: 0 samples with frame_bytes &gt; 0 means skipped ID3 or garbage, 0 with frame_bytes == 0 means not enough data, and the info fields may be stale in the second case.
- Float output (MINIMP3_FLOAT_OUTPUT) can go outside [-1, 1] (open issue #104), so clamp before converting or mixing.
- Seeking by byte (mp3dec_decode_frame at an arbitrary offset) is probabilistic sync, not guaranteed; use mp3dec_ex_seek with MP3D_SEEK_TO_SAMPLE for exact positions, and note the open #147 report against that path.

## Known shortcomings

- README clock-tick table's only baseline is keyj's older minimp3, which is broken on several conformance vectors (sin1k0db PSNR 0.15 dB, he_free 0 samples); no number against libmpg123, FFmpeg or dr_mp3. The only independent figure is FastLED's Callgrind run of the vendored minimp3-float, 9% fewer instructions than Helix.
- The keyj column carries a fixed per-run cost of about 14M cycles (fit over the 10 vectors: keyj = 14.1M + 1.48 x minimp3, derived from page data), probably FFmpeg-style runtime table initialisation, so the marginal decode advantage is about 1.5x and the 2.0-6.4x per-file ratios are mostly start-up on short clips; the keyj site and harness are unreachable. Open unfixed security reports: #145 (L3_huffman out-of-bounds reads in the core decoder), #147 (mp3dec_ex_read_frame heap out-of-bounds), #140 (Xing overflow, about 10 TB allocation), #141 (MSan). Maintenance sporadic (gap November 2021 to March 2026, 37 open issues, no tagged releases).

## Caveats and trade-offs

Baseline is the original keyj minimp3, a small fixed-point hobby decoder that fails conformance on every vector (PSNR 71-72 dB on most, 27.80 dB on si_huff.bit and 0.15 dB on sin1k0db.bit) and decodes nothing on he_free.bit, so on several vectors it is not producing correct output (sin1k0db sample counts also differ, 730,368 vs 725,760); the speed rows compare a conformant decoder with a broken one. No number against libmpg123, libmad, FFmpeg or dr_mp3 is published in the repo, and none was found elsewhere. The only independent figure found is FastLED's Callgrind count (agents/docs/mp3-decoder-performance.md, its vendored minimp3-float build, scalar -DMINIMP3_NO_SIMD at -O2, x86-64): 202,832,660 instructions vs 222,939,814 for the Helix MP3 decoder, about 9% fewer, instruction counts rather than time. Compiler and flags for the README table are not stated (the CI script scripts/build.sh builds with gcc -O2 -std=c89); the timed process includes file I/O and the PSNR comparison against the reference PCM. Numbers are first-party, from an i7-6700K, and the README calls it a 'rough benchmark'. CC0-1.0 dedication carries no patent grant.

Single-header C decoder with SSE and NEON intrinsics, floating-point output; CC0 means no patent grant. The baseline is a fixed-point decoder with no vector code, so the comparison is between different design points.

## Maintenance

Sporadically maintained: after a gap from Nov 2021, hardening PRs for VBR-tag and seek OOB reads were merged in Mar 2026 and an ARMv6-M fix on 27 Jul 2026, but 37 issues are open, including several unfixed memory-safety reports; CC0 and one header, so it is easy to vendor and patch yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables of perf clockticks on an i7-6700K against keyj's minimp3; scripts/perf.sh (perf stat -e cycles over vectors/\*.bit) is public, but the compiler and flags used for the table are not stated and the keyj harness is not published, so it stays C.
- **Verifier notes:** All four quoted clocktick pairs match the README tables. Asked about stronger baselines: none against libmpg123, FFmpeg or dr_mp3 exists (dr_mp3 is itself derived from minimp3); FastLED's Callgrind table against Helix (AMD EPYC 7763, clang 18, -O2 scalar) is the only independent number, a 9% instruction-count edge for its vendored float build, so I noted it in caveats rather than upgrading. Metadata confirmed: CC0-1.0, about 2.0k stars, 271 forks, not a fork, last commit 2026-07-27.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/README.md>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/scripts/perf.sh>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/scripts/test.sh>
  - <https://github.com/lieff/minimp3>
  - <https://github.com/lieff/minimp3/commits>
  - <https://github.com/lieff/minimp3/tree/master/scripts>
  - <https://github.com/FastLED/FastLED/issues/4138>
  - <https://raw.githubusercontent.com/FastLED/FastLED/HEAD/agents/docs/mp3-decoder-performance.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/README.md>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/minimp3.h>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/minimp3_ex.h>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/minimp3_test.c>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/scripts/perf.sh>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/scripts/test.sh>
  - <https://raw.githubusercontent.com/lieff/minimp3/HEAD/LICENSE>
  - <https://github.com/lieff/minimp3/commits/master>
  - <https://github.com/lieff/minimp3/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/lieff/minimp3/issues/145>
  - <https://github.com/lieff/minimp3/issues/147>
  - <https://raw.githubusercontent.com/fredrikhederstierna/minimp3/master/minimp3.c>
  - WebSearch: keyj minimp3.c "mp3_create" "table_4_3" github
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/lieff/minimp3`) · [data/wave10/enrich/raw/github_com_lieff_minimp3.json](../../../data/wave10/enrich/raw/github_com_lieff_minimp3.json) (enrichment confidence 0.8)

</details>
