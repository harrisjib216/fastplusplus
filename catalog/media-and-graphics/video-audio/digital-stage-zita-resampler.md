# zita-resampler

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `GPL-3.0-or-later` · 🔴 abandoned

> Real-time-safe polyphase windowed-sinc audio resampler (fixed and variable ratio); claims to beat libsamplerate, with no published numbers.

| | |
|---|---|
| **Beats** | libsamplerate (Secret Rabbit Code), named in the library docs as the comparison |
| **Claimed result** | Directional only: 'Even at the highest quality setting libzita-resampler will be faster than most similar libraries providing the same quality, e.g. libsamplerate.' No numbers. Separately, the docs say the 1.8.0 SSE2 build 'will reduce CPU load by a factor of at least 2'; that factor is against the library's own scalar build, not against libsamplerate. The quality/CPU trade-off spans 'approximately 1:6' (CPU load roughly proportional to hlen). |
| **Workload** | No benchmark workload behind the libsamplerate claim. The repo's test/speedtest.cc only times zita-resampler itself (44100 -&gt; 48000 Hz, given channel count and hlen, input frames per second) with no baseline and no published results. |
| **Metric** | throughput |
| **Adoption** | 35 stars, 5 forks (digital-stage GitHub copy). Upstream is packaged in nixpkgs (1.11.2), an older 2012 version is vendored in Ardour (libs/zita-resampler), and it is the resampler behind zita-ajbridge (named in the SampleRateTap comparison table). |
| **Last commit** | 2021-03-10 |
| **Links** | [repository](https://kokkinizita.linuxaudio.org/linuxaudio/zita-resampler-doc/quickguide.html) · [benchmark](https://raw.githubusercontent.com/digital-stage/zita-resampler/main/docs/resampler.html) |

## Verdict

Nothing was measured: the docs say only that at its highest quality zita 'will be faster than most similar libraries providing the same quality, e.g. libsamplerate'. The SSE2 'factor of at least 2' is against its own scalar build, and test/speedtest.cc (44.1 to 48 kHz, input frames per second, CLOCK_REALTIME) times zita alone, with no baseline, hardware or results.

## Use it when

- Inside a JACK or other real-time audio callback: process() and reset() are documented RT-safe (no allocation), while setup() is not.
- Bridging two sound cards or network streams whose clocks drift: VResampler::set_rratio (0.95-16 of the configured ratio) with set_rrfilt smoothing is what zita-ajbridge/zita-njbridge are built on.
- Standard-rate conversion (44.1/48/88.2/96/192 kHz) of multichannel float audio where inaudible aliasing above 20 kHz is acceptable and hlen 32-48 is enough per the author's listening tests.
- Linux audio projects that are already GPL and want a small 4-file library with distribution packages and a stable, padded class layout (reserved _dummy[8] members).

## Skip it when

- When you need measured throughput: no published zita versus libsamplerate, libsoxr or r8brain timing exists, while soxr and r8brain-free-src have third-party tables showing 6.8-11x over libsamplerate.
- When you need deep stopband rejection or full-band transparency (mastering, measurement, 120 dB-class SRC): the filter targets 60 dB at Nyquist, so 'same quality as libsamplerate' depends on that relaxed definition.
- Closed-source or permissively licensed products: GPL-3.0-or-later.
- Integer, double-precision or planar (non-interleaved) buffers, or ratios outside 1/64-64 (Resampler also needs b &lt;= 1000); there is no NEON path in 1.8.0, and the docs only promise ARM NEON for a future release.
- Building this digital-stage copy with its CMakeLists.txt as is: the flags go into CMAKE_CXXFLAGS_FLAGS and CMAKE_CPPFLAGS_FLAGS, which CMake ignores, and ENABLE_SSE2 is never defined, so you get the scalar path with no -O2 unless you set flags yourself (open issue #2 since 2024-01-24).

## How it is fast

It is a constant-bandwidth polyphase FIR: only the output samples are computed, using a precomputed table of np+1 phases x hlen taps of a sinc times a 3-term cosine window (0.384 + 0.5 cos + 0.116 cos 2x). The filter's symmetry halves the table: each output uses phase ph and the mirrored phase np-ph. Input is deinterleaved into one contiguous delay line per channel, so each output is a pair of straight dot products; in 1.8.0 these use SSE2 4-wide multiply-adds when ENABLE_SSE2 is defined, which the docs say cuts CPU load by at least 2x against the library's own scalar build. The filter is deliberately short: it is dimensioned for only 60 dB attenuation at Nyquist and lets the transition band and aliasing sit above 20 kHz for standard rates, with hlen 16-96 giving a CPU range of about 1:6. VResampler linearly interpolates coefficients between 120 fixed phases once per output frame, so the extra cost is shared across channels.

## Compared with alternatives

Pick it over libsoxr or r8brain-free-src when you need a tiny, RT-safe, push/pull API with built-in smooth variable-ratio drift correction inside a GPL Linux audio app; pick libsoxr, r8brain-free-src or LibFResample when you want a resampler whose speed advantage over libsamplerate has actually been measured, or when you need a permissive licence or 120 dB stopbands.

## Integration

| | |
|---|---|
| **Form** | shared or static lib (4 .cc files, easy source-drop) |
| **Dependencies** | pthreads (table registry mutex); nothing else |
| **Minimum toolchain** | Plain C++ (no modern-standard features); the SSE2 path needs GCC or Clang (it subscripts __m128 as S[0]) and posix_memalign; this copy's CMake needs 3.16 |
| **Platforms** | Linux and other POSIX systems; x86 SSE2 path optional; MSVC/Windows needs a port (unmerged PR #1 from 2021 swaps in pthreads4w); no ARM SIMD in 1.8.0 |
| **Thread safety** | One instance per thread; the shared, reference-counted coefficient tables are created and destroyed under a global pthread mutex, so setup()/clear() on different instances from different threads is safe; process() is RT-safe |
| **Drop-in for the baseline** | no |

## Gotchas

- No automatic edge padding: prefill inpsize()/2 - 1 zeros to align first input and output, and append zeros at the end, or the output starts late and is truncated (documented, but easy to miss when coming from libsamplerate's src_simple).
- The scalar path adds and removes a 1e-20 bias to keep the accumulator out of denormals, but the SSE2 path does not and the library never sets FTZ/DAZ: set them in your audio thread when signals decay to silence.
- Docs and code disagree on limits: setup() accepts hlen down to 8 (docs say 16-96), and VResampler's 3-argument setup rejects ratios below 1/16 even though the class documents 1/64; set_rratio silently clamps to 0.95-16.
- Downsampling scales the filter length by 1/r (hl = ceil(hlen/r)), so CPU per output frame and table size grow with the decimation ratio (e.g. 192 kHz to 44.1 kHz at hlen 96 gives about 418 taps per half-filter, derived from resampler.cc).

## Known shortcomings

- Tier D: the docs name libsamplerate but give no numbers, and the only benchmark code (test/speedtest.cc) times zita-resampler alone; the SSE2 'factor of at least 2' is against its own scalar build. The GitHub record is a 2021 import of upstream 1.8.0 (digital-stage, 8 commits, not a fork) whose CMakeLists.txt uses ignored variables and never defines ENABLE_SSE2, so a CMake build gets the scalar path without -O2. Canonical upstream is kokkinizita.linuxaudio.org (Fons Adriaensen, 1.11.2 as of 2025-06-04, blocked here). GPL-3.0-or-later.
- Still no numeric comparison anywhere (SampleRateTap COMPARISON.md unchanged; lastique's src_test covers only speex and soxr), so tier D stands. The filter targets only 60 dB at Nyquist, so 'same quality as libsamplerate' is a relaxed claim. The digital-stage CMake ignores flags (issue #2 open), sets no ENABLE_SSE2 or -O2 and builds no tests; the SSE2 path drops the 1e-20 denormal guard with no FTZ/DAZ; VResampler's 3-argument setup rejects ratios below 1/16 although the docs say 1/64; the Windows port PR #1 has been unmerged since 2021.

## Caveats and trade-offs

Tier D: a first-party directional claim with no numbers. The repo is digital-stage's 2021 import (8 commits, 2021-02-16 to 2021-03-10, no releases, not a GitHub fork) of upstream release 1.8.0 by Fons Adriaensen; its sources, docs and README match 1.8.0 (version macros 1.8, copyright 2006-2020, AUTHORS Fons Adriaensen) with a CMake build added. The canonical upstream is https://kokkinizita.linuxaudio.org/linuxaudio/ (unreachable from this environment), which has moved on to at least 1.11.2 (nixpkgs bumped to it on 2025-06-04), so this copy is behind upstream and abandoned; upstream's own activity date could not be checked. The copy's CMakeLists.txt sets non-standard variables (CMAKE_CXXFLAGS_FLAGS, CMAKE_CPPFLAGS_FLAGS) that CMake ignores and never defines ENABLE_SSE2, so a CMake build of this copy gets the scalar path without -O2 unless the user adds flags; the 'factor of at least 2' SSE2 gain applies to the upstream Makefile build, which enables SSE2 by default. GPL-3.0-or-later copyleft (file headers say 'version 3 ... or any later version'; nixpkgs labels upstream 1.11.2 gpl3Only, not checked at source). The SampleRateTap comparison (now async/docs/COMPARISON.md) lists 'zita-resampler + zita-ajbridge' with 'no published CI-verified figures' and measures only libsamplerate, soxr and r8brain-free-src.

GPL, so copyleft for linked code. Single-precision float only, interleaved multichannel, fixed-ratio Resampler plus variable-ratio VResampler class. Quality/CPU trade-off range of about 1:6.

## Maintenance

The digital-stage copy has been frozen at upstream 1.8.0 since 2021-03-10 (8 commits, 35 stars), with an open CMake-flags bug and an unmerged Windows port. Upstream by Fons Adriaensen has moved on (1.11.2 in nixpkgs per the record), so use a distribution package or the upstream tarball rather than this copy; GPL-3.0-or-later.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** docs/resampler.html names libsamplerate but only says zita-resampler at its highest quality setting 'will be faster than most similar libraries providing the same quality, e.g. libsamplerate', with no numbers, workload or method; the only benchmark code in the repo (test/speedtest.cc, test/vspeedtest.cc) times zita alone (44100 -&gt; 48000, input frames per second) with no baseline and no published results. No reachable source (SampleRateTap async/docs/COMPARISON.md, other GitHub copies, Ardour's vendored copy, nixpkgs packaging) carries a numeric comparison with libsamplerate or libsoxr, so the claim stays directional.
- **Verifier notes:** Kept at D: copy verified as the upstream 1.8.0 release, and no numeric zita vs libsamplerate/libsoxr comparison exists in any reachable source (3 WebSearch queries, GitHub copies, SampleRateTap, Ardour, nixpkgs). Consider a repo_url override to the canonical upstream https://kokkinizita.linuxaudio.org/linuxaudio/ (current 1.11.2), since the digital-stage copy is a frozen 2021 import whose CMake build silently drops the SSE2 path. Licence is GPL-3.0-or-later per file headers.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `license`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/docs/resampler.html>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/README.md>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/AUTHORS>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/LICENSE>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/COPYING>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/resampler.cc>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/resampler-table.cc>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/zita-resampler/resampler-table.h>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/test/speedtest.cc>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/test/vspeedtest.cc>
  - <https://github.com/digital-stage/zita-resampler>
  - <https://github.com/digital-stage/zita-resampler/commits>
  - <https://github.com/digital-stage/zita-resampler/releases>
  - <https://github.com/digital-stage/zita-resampler/tree/main/test>
  - <https://github.com/tap/SampleRateTap>
  - <https://github.com/tap/SampleRateTap/pull/45>
  - <https://github.com/tap/SampleRateTap/pull/45/files>
  - <https://github.com/tap/SampleRateTap/commits/main/docs/COMPARISON.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/main/async/docs/COMPARISON.md>
  - <https://raw.githubusercontent.com/NixOS/nixpkgs/master/pkgs/by-name/zi/zita-resampler/package.nix>
  - <https://github.com/NixOS/nixpkgs/commits/master/pkgs/by-name/zi/zita-resampler/package.nix>
  - <https://raw.githubusercontent.com/jpcima/zita-resampler-mod/HEAD/README.md>
  - <https://raw.githubusercontent.com/Joeboy/zita-resampler/HEAD/README.md>
  - <https://raw.githubusercontent.com/Ardour/ardour/master/libs/zita-resampler/zita-resampler/resampler-table.h>
- **Sources the enricher read:**
  - <https://github.com/digital-stage/zita-resampler>
  - <https://github.com/digital-stage/zita-resampler/issues>
  - <https://github.com/digital-stage/zita-resampler/issues/2>
  - <https://github.com/digital-stage/zita-resampler/issues/3>
  - <https://github.com/digital-stage/zita-resampler/pulls>
  - <https://github.com/digital-stage/zita-resampler/pull/1>
  - <https://github.com/digital-stage/zita-resampler/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/README.md>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/docs/resampler.html>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/AUTHORS>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/resampler.cc>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/resampler-table.cc>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/vresampler.cc>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/cresampler.cc>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/zita-resampler/resampler.h>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/zita-resampler/resampler-table.h>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/zita-resampler/vresampler.h>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/source/zita-resampler/cresampler.h>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/test/speedtest.cc>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/test/vspeedtest.cc>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/.github/workflows/build_cmake.yml>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/.github/workflows/ubuntu.yml>
  - <https://raw.githubusercontent.com/digital-stage/zita-resampler/main/.github/workflows/win.yml>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/main/async/docs/COMPARISON.md>
  - <https://raw.githubusercontent.com/lastique/src_test/gh-pages/index.html>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/digital-stage/zita-resampler`) · [data/wave10/enrich/raw/github_com_digital_stage_zita_resampler.json](../../../data/wave10/enrich/raw/github_com_digital_stage_zita_resampler.json) (enrichment confidence 0.7)

</details>
