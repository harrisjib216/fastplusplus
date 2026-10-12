# hmp3 (Helix MP3 encoder revival)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `RPSL-1.0 (Helix encoder sources in hmp3/); MIT (other files)` · 🟡 stale

> Maintained build of RealNetworks' Helix MP3 encoder, reputed (not measured here) to encode several times faster than LAME.

| | |
|---|---|
| **Beats** | LAME (MP3 encoder); no baseline comparison in the repository |
| **Claimed result** | None in the repository. No numbers on any opened page. |
| **Workload** | MP3 encoding speed; no benchmark is published in the repository (README, Makefile and issues were read). |
| **Metric** | throughput |
| **Compiler and flags** | Makefile builds with gcc -O3 -flto=auto -DIEEE_FLOAT; no benchmark was run by the project |
| **Adoption** | 38 stars |
| **Last commit** | 2024-05-31 |
| **Links** | [repository](https://github.com/maikmerten/hmp3) |

## Verdict

Nothing measures hmp3 against LAME: the repository has no benchmark, and the 'about three times as fast as LAME' figure is Hydrogenaudio folklore about old Helix builds (search snippets only). The only numbers are the L4cache/hmp3 fork's 5.2.4 release notes, which time hmp3 builds against each other on an 85-minute (5103 s) 48 kHz stereo WAV on a Ryzen 7900X with GCC 14.1.0 and Clang 18.1.6, encoder settings not stated: 7.43 s (686.81x realtime) for plain gcc, 7.58 s for plain clang, 5.92 s (861.99x) for gcc with PGO, znver4 and fast-math.

## Use it when

- Bulk transcoding of large libraries to MP3 where encode time per CPU core matters and you can accept a different quality profile from LAME
- VBR at mid-to-high bitrates (default about 128 kbps VBR; -V100 -HF2 gives about 185 kbps) for 32/44.1/48 kHz stereo music
- Embedding an MP3 encoder in a C++ program whose distribution can carry RPSL source-release terms for the encoder directory
- Server-side encoding where an x86-64-v3 or znver4 build with PGO is acceptable (fork timings show at most about 1.25x over a plain gcc build, 7.43 s to 5.92 s)

## Skip it when

- Low bitrates: CBR below about 48 kbps per channel fails with ENCODER INIT FAIL (issue #8, open since 2025-01), and LAME handles 80 kbps stereo at 32 kHz
- Projects that need LAME's API, presets, ReplayGain, ID3 tagging or bit-exact outputs: hmp3 has none of these, and march/fast-math builds change the encoded bytes
- When you need a measured speed or quality claim: no benchmark against LAME exists in the repository, its issues or its fork
- GPL-only or permissive-only codebases: the encoder is under RPSL-1.0 (reciprocal, not GPL-compatible) or RCSL, and only files outside hmp3/ are MIT
- Long-term maintenance needs: last commit 2024-05-31, single maintainer, 38 stars

## How it is fast

The default acoustic model (CMp3Enc::L3acousticQuick) works on the MDCT energies the encoder already computed ('uses xform energy only, pcm not used'): emapLong/emapShort plus a spreading/SMR pass, with no separate FFT psychoacoustic model, while LAME runs an FFT-based psymodel and iterative noise-shaping loops. Quantization uses table-driven arithmetic: x^(3/4) built from IEEE-754 exponent/mantissa lookup tables in pow34.c (hence -DIEEE_FLOAT), and a fast-rounding inner loop in l3math.c's noise estimate. The Linux build is plain C/C++ at -O3 with LTO (about 3% gain per the commit log); the original i386 assembly in hmp3/src/platform/win/i386 is not used by the Makefile.

## Compared with alternatives

Pick hmp3 over Shine when you want a floating-point encoder with a psychoacoustic model and VBR on desktop or server CPUs (Shine is fixed-point CBR, aimed at FPU-less hardware); pick SuperLAME instead when you need LAME's output and quality and want speed from multiple threads rather than a different encoder.

## Integration

| | |
|---|---|
| **Form** | static lib (libhmp3.a target in the Makefile) plus CLI; or source-drop of hmp3/src |
| **Dependencies** | none beyond libm and libstdc++ |
| **Minimum toolchain** | gcc/g++ with LTO for the Makefile (the L4cache fork built it with GCC 14.1.0 and Clang 18.1.6); MinGW cross builds for win32 (Pentium III, SSE) and win64; Visual Studio 2015 project files |
| **Platforms** | Linux x86-64 and ARM tested per README; Windows via MinGW or VS2015; requires IEEE-754 float (-DIEEE_FLOAT) |
| **Thread safety** | Not documented. CMp3Enc holds per-encoder state, but emdct.c keeps MDCT tables in file-static arrays written at init and xhead.c keeps the Xing TOC in a file-static table, so concurrent encodes in one process are unsafe without care |
| **Drop-in for the baseline** | no |

## Gotchas

- -B sets bitrate per channel: -B64 on stereo input is 128 kbps
- Mixed C and C++ (bitallo\*.cpp, mp3enc.cpp, srcc\*.cpp) compiled through gcc and linked with -lstdc++, so it is not a pure-C library despite the catalog's language field
- Builds with -march or -ffast-math produce slightly different MP3 files from the same input (L4cache 5.2.4 notes); in that fork, clang with znver4 plus fast-math ran about 1.5x slower (1.9x with PGO) than plain clang
- -U2 switches the transform to the 'Pentium III' x-variants (xsbt_L3, xantialias), which on Linux are compiled C, not the original assembly

## Known shortcomings

- Tier D: the repository has no benchmark and no LAME comparison; the 'about three times as fast as LAME' line is Hydrogenaudio folklore about old Helix builds. The fork L4cache/hmp3 (release 5.2.4) times only hmp3 builds against each other (85 min PCM file in 7.43 s standard gcc vs 5.92 s znver4 PGO build on a Ryzen 7900X). The encoder in hmp3/ is under RPSL-1.0 (reciprocal, OSI-approved), the rest MIT; usability set to copyable on that basis. Last commit 2024-05-31.
- Enricher (e114, 2026-10-05): no LAME measurement anywhere (snippets only). The default psymodel L3acousticQuick uses MDCT energy only, no FFT. Mixed C/C++ with a C++ class API, not pure C; file-static state in emdct.c and xhead.c, so not thread-safe. Issue #8: CBR init fails below about 48 kbps per channel. Issue #9 (2026-10-04): a Huffman partition patch gives about 2% smaller files at about 2x slower encode. L4cache 5.2.4: clang znver4 fast-math build 11.6 s vs 7.58 s plain clang (a regression); -march and fast-math builds change the output. D stands.

## Caveats and trade-offs

Tier D because the repository has no speed numbers against LAME. Folklore only, not opened: Hydrogenaudio wiki and forum snippets (hydrogenaudio.org is blocked here) say Helix is roughly three times as fast as LAME, with figures such as x35 realtime versus x8 for LAME and a 5 minute song in 3.6 s with Helix versus 6.5 s with Xing; these are old posts of unknown settings and versions and were not measured on the hmp3 code. The fork L4cache/hmp3 (release 5.2.4 page) times only hmp3 builds against each other: an 85 min 03 s (5103 s) 48 kHz stereo PCM file on a Ryzen 7900X with gcc 14.1.0 and clang 18.1.6, 7.43 s (686.81x realtime) for the standard gcc build and 5.92 s (861.99x) for gcc-znver4-fast-math-pgo; no LAME run, and its encoder settings are not shown. License: the encoder in hmp3/ is under RPSL-1.0 (RealNetworks Public Source License 1.0, OSI-approved but reciprocal, with source-release duties on external deployment, and not GPL-compatible), with the RCSL as an alternative for RealNetworks licensees; files outside hmp3/ are MIT per the README and the Makefile header, and there is no root LICENSE file. The encoder is mixed C and C++ (bitallo\*.cpp, mp3enc.cpp, srcc\*.cpp, test/tomp3.cpp). MP3 patents have expired. Project is small (38 stars, 54 commits).

Helix MP3 encoder (RealNetworks copyright 1995-2004 in the license header; search snippets say it descends from the Xing encoder) with modern-system maintenance: Linux x86-64 and ARM tested, Visual Studio 2015 project files, VBR and CBR, -B bitrate is per channel, highpass and frequency options. Command line tool plus static library.

## Maintenance

Stale since 2024-05-31 (version 5.2.4, 38 stars, one maintainer, two open issues); usable and small, but the encoder sources are RPSL-1.0/RCSL with reciprocal source-release duties, so treat reuse as conditional even though the verifier rated it copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** The repository has no benchmark and no LAME comparison (README and Makefile read); the only speed numbers found are a fork's (L4cache/hmp3 release 5.2.4) timings of hmp3 builds against each other, and the 'roughly three times as fast as LAME' line is a Hydrogenaudio snippet about old Helix builds, not opened. D stands.
- **Verifier notes:** Confirmed at D. Usability corrected from mixed to copyable because both licenses (RPSL-1.0 and MIT) are OSI-approved and no part is unlicensed; set it back to mixed if the catalog treats RPSL's reciprocal terms as a reuse limit. Last commit 2024-05-31 (stale) and 38 stars confirmed; Makefile flags gcc -O3 -flto=auto -DIEEE_FLOAT confirmed.
- **Fields the verifier corrected:** `usability`, `caveats`
- **Shortcomings recorded by:** fork self-timings only; none
- **Pages the verifier opened:**
  - <https://github.com/maikmerten/hmp3>
  - <https://github.com/maikmerten/hmp3/commits/main>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/README.md>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/Makefile>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/LICENSE.txt>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/RPSL.txt>
  - <https://github.com/L4cache/hmp3/releases/tag/5.2.4>
- **Sources the enricher read:**
  - <https://github.com/maikmerten/hmp3>
  - <https://github.com/maikmerten/hmp3/commits/main>
  - <https://github.com/maikmerten/hmp3/commits/main?after=0&page=2>
  - <https://github.com/maikmerten/hmp3/issues?q=is%3Aissue>
  - <https://github.com/maikmerten/hmp3/issues/8>
  - <https://github.com/maikmerten/hmp3/issues/9>
  - <https://github.com/maikmerten/hmp3/pulls?q=is%3Apr>
  - <https://github.com/maikmerten/hmp3/tree/main/hmp3/src>
  - <https://github.com/maikmerten/hmp3/tree/main/hmp3/src/pub>
  - <https://github.com/maikmerten/hmp3/tree/main/hmp3/src/platform/win/i386>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/README.md>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/Makefile>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/LICENSE.txt>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/src/pub/mp3enc.h>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/src/pub/encapp.h>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/src/pub/enc.h>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/src/test/tomp3.cpp>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/src/mp3enc.cpp>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/src/l3math.c>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/src/pow34.c>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/src/emdct.c>
  - <https://raw.githubusercontent.com/maikmerten/hmp3/HEAD/hmp3/src/xhead.c>
  - <https://github.com/L4cache/hmp3>
  - <https://github.com/L4cache/hmp3/releases/tag/5.2.4>
  - WebSearch: hmp3 Helix MP3 encoder speed versus LAME benchmark realtime (snippets: Hydrogenaudio wiki and forum, RareWares)
  - WebSearch: "hmp3" "lame" encode time seconds github
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/maikmerten/hmp3`) · [data/wave10/enrich/raw/github_com_maikmerten_hmp3.json](../../../data/wave10/enrich/raw/github_com_maikmerten_hmp3.json) (enrichment confidence 0.75)

</details>
