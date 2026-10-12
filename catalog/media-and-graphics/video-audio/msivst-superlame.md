# SuperLAME

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-2.0-or-later` · 🟢 active

> Multithreaded MP3 encoder CLI that runs many LAME r6531 instances on chunks; beats single-threaded LAME on wall time, not per core.

| | |
|---|---|
| **Beats** | LAME (stock single-threaded libmp3lame 3.101 beta) |
| **Claimed result** | README: 'roughly 8x faster than stock single-threaded LAME at the same quality'; v1.1.0 on a Ryzen 7 5800X3D, 44-minute album, CBR 320: 13.8 s at 2 threads down to 3.9 s at 16 (\~680x realtime), parallel efficiency \~93% at t2 and \~61% at t16 (no stock-LAME time is given for that run). docs/SCALING_NOTES.md (42-minute 440 MB album, mode not stated): stock LAME \~28 s versus SuperLAME \~3.6 s at -t2 to -t16, '\~8x'; SuperLAME -t1 takes \~42 s (0.7x stock). docs/COMPARISON_REPORT.md (2026-06-29, pre-v1.1.0 build, 16 threads versus the same patched LAME r6531 core single-threaded, 4 albums): VBR -V2 5.84x to 6.17x (e.g. 4.19 s vs 24.46 s for a 50-minute album), CBR 320 1.49x to 4.73x (e.g. 17.19 s vs 25.60 s). The v1.1.0 CHANGELOG reports multithreaded encodes became 1.8x to 1.9x faster after that report (t16 7.2 s to 3.9 s on the 44-minute CBR 320 album), so the June table understates the current build. |
| **Workload** | Multithreaded MP3 encoding of full albums (16-bit/44.1 kHz WAV) at VBR -V2 and CBR 320: SuperFast runs many libmp3lame instances on overlapping chunks and a serial repacker re-chains the bit reservoir. Measured with 16 threads on an 8-core/16-thread CPU against the same LAME r6531 core encoding single-threaded; the v1.1.0 scaling figures use the in-RAM --bench mode at 2 to 16 threads. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5800X3D (8 cores / 16 threads, Zen 3), Windows 11 |
| **Compiler and flags** | clang 21.1.6 targeting x86_64-unknown-windows-msvc (Windows 11): libmp3lame engines built with -O3 -march=znver5 / znver4 / znver3 / x86-64 (build/build_dispatch.sh; znver3 engine used on the test CPU); frontend clang++ -std=c++17 -O2 -march=x86-64 and dr_flac clang -O2 -march=x86-64 (build/build_final.sh). Build flags of the stock-LAME baseline binary (build/phase2-build/lame.exe) are not stated. |
| **Adoption** | 3 stars, 0 forks, 21 commits |
| **Last commit** | 2026-08-21 |
| **Links** | [repository](https://github.com/MSIVST/SuperLAME) · [benchmark](https://github.com/MSIVST/SuperLAME/blob/master/docs/COMPARISON_REPORT.md) |

## Verdict

First-party only, on a Ryzen 7 5800X3D (Zen 3, 8C/16T, Windows 11) using the clang 21.1.6 -O3 -march=znver3 engine. docs/COMPARISON_REPORT.md (2026-06-29, before v1.1.0) times 16-thread SuperLAME against a single-threaded lame.exe built from the same patched LAME r6531 (its flags unstated) on four commercial albums: VBR -V2 5.84-6.17x and CBR 320 1.49-4.73x. The v1.1.0 fix took the 44-minute CBR 320 album from 7.19 to 3.85 s at 16 threads, but no stock-LAME run was repeated on v1.1.x, and the timing method for the June table is not documented, so the README's '\~8x' rests on SCALING_NOTES (about 28 s against about 3.6 s, mode unstated, pre-v1.1.0).

## Use it when

- Turning one long file (album, audiobook, DJ mix) into an MP3 as fast as possible on a many-core x86-64 Windows machine, where single-file latency matters more than total CPU spent.
- VBR -V2 encodes: the largest measured gains (5.84-6.17x with 16 threads against single-threaded LAME in the June 2026 report).
- You want LAME r6531 with the maikmerten q4 CBR/ABR quality patch, plus native FLAC/24-bit/hi-res input and a complete Xing/Info tag even when writing to stdout.
- Hi-res or FLAC sources that need resampling to an MP3 rate: r8brain resampling is parallelized and done up front.

## Skip it when

- Batch conversion of many files: one stock LAME process per file keeps every core busy with no seam overlap or serial repacker (SuperLAME's own docs recommend one process per file; v1.1.0 reports only \~61% parallel efficiency at 16 threads).
- You need output that is byte-identical to a reference LAME encode: multithreaded output differs at chunk seams (ST-vs-MT decoded difference -45 to -87 dB in the June report), and single-thread output matches only a LAME built with the same -march flags.
- Linux, macOS or ARM: build scripts target clang with x86_64-windows-msvc and all tests are PowerShell; no non-Windows build is documented and the engines are x86-64 only.
- Streaming or memory-constrained encoding: the whole input, its float copy and the output MP3 are held in RAM (about 1-2 GB practical input), and nothing is written until the encode finishes.
- CBR on dense, loud material: the June report measured only 1.49x (Static-X) and 2.02x (American Head Charge) at CBR 320, because the repacker needs more seam retries in CBR.

## How it is fast

Chunk-level thread parallelism (Robert Kausch's fre:ac/BoCA 'SuperFast' technique): workers encode overlapping blocks (128 frames, overlap 4\*1152/frameSize = 4 MPEG-1 frames) and flush with lame_encode_flush_nogap; a single serial SuperRepacker then unpacks each frame's main data, rewrites main_data_begin, zero-fills surplus reservoir, re-picks VBR bitrate indices, enlarges earlier frames (padding or bitrate) when the reservoir runs short, and asks a worker to re-encode with dummy frames when a frame still does not fit. Since v1.1.0 worker handoffs use condition variables instead of a 1 ms sleep-poll that Windows rounded to \~15.6 ms, which made MT encodes 1.8-1.9x faster. The LAME core is unchanged apart from per-CPU builds (-O3 -march=znver3 etc.); per thread SuperLAME is no faster than LAME.

## Compared with alternatives

Pick it over fre:ac's SuperFast drivers (enzo1982/superfast), which use the same technique, when you want a standalone LAME-style CLI with FLAC/hi-res input and the post-2018 BoCA repacker fixes, rather than a full converter GUI. Pick it over Shine when you need LAME quality and have many cores; Shine is a fixed-point encoder aimed at weak or embedded CPUs and trades quality for speed.

## Integration

| | |
|---|---|
| **Form** | CLI application (prebuilt Windows .exe in releases) or source-drop of the C++17 frontend; not a library |
| **Dependencies** | LAME trunk r6531 plus patches (q4 clamp, ID3v2.4 synchsafe sizes), libmpg123 &gt;= 1.26 (1.33.6 used), r8brain-free-src (header-only), dr_flac (vendored); build needs clang/LLVM 21 with llvm-ar, llvm-nm and llvm-objcopy, plus CMake and NASM for mpg123. build/build_dispatch.sh also reads a LAME config.h from build/phase4-znver3/, which is not in the repository. |
| **Minimum toolchain** | C++17; clang/LLVM 21 (tested 21.1.6) targeting x86_64-windows-msvc; MSVC cannot build the SIMD paths |
| **Platforms** | x86-64 Windows (tested on Windows 11, Zen 3); CPUID picks a znver5, znver4 (AVX-512), znver3 (AVX2/FMA) or SSE2 engine; znver4/znver5 engines are built but never run, and Intel CPUs are untested |
| **Thread safety** | Not applicable as a library; internally one dispatcher thread drives N worker threads (one lame_t each) and a single serial repacker |
| **Drop-in for the baseline** | partial — accepts the common LAME CLI flags (-b, -V, --abr, --preset, -q, -m, --resample, ID3 flags) and reads WAV/AIFF/FLAC, but it is not a libmp3lame replacement, many LAME options are absent, and -q is clamped to &gt;=4 for CBR/ABR |

## Gotchas

- The speed and realtime figures SuperLAME prints come from a timer that covers only encode and repack (main.cpp starts it after input read and resampling and stops before the file write), whereas stock LAME's time includes reading the WAV; compare whole-process wall time or use --bench, which reports wall and CPU clocks.
- The self-heal safety net (FrameChainValid, which re-encodes single-threaded if the MT stream is broken) only walks frame headers; a repacker error that leaves headers intact but corrupts main_data_begin chaining would not trigger it.
- The regression suite never compares against a stock lame.exe: it checks ST against MT (&lt;= -40 dB) and znver3 against SSE2 (&lt;= -50 dB, the two differ by FMA-contraction rounding), so 'bit-identical to stock LAME' holds only for a LAME built the same way.
- Files under about 300 MB become cache-resident and give flat, misleading thread-scaling timings (the project's own warning); docs/SCALING_NOTES.md and CONTRIBUTING.md still describe a plateau at about 2 workers and a -t1 1.5x slower than LAME, figures that predate the v1.1.0 sleep-poll fix.

## Known shortcomings

- Multithreaded LAME front end, not a faster codec: four CPU-dispatched LAME r6531 builds plus fre:ac/BoCA SuperFast parallel chunks and a repacker; the baseline is the same LAME core single-threaded, so the win is 16 threads against 1, and its own -t1 run is about 1.5x slower than stock LAME. docs/COMPARISON_REPORT.md: VBR -V2 5.84-6.17x, CBR 320 1.49-4.73x (pre-v1.1.0); SCALING_NOTES about 28 s vs 3.6 s. No public stock-LAME script, baseline flags unstated, test albums commercial.
- The built-in timer (main.cpp, t0 at line 1335) covers encode plus repack only and excludes WAV read, resample and write, while the June table's timing method is undocumented, so the multithreaded side may omit I/O that stock LAME pays; there is no stock-LAME rerun on v1.1.x and the README's 'about 8x' rests on pre-v1.1.0 SCALING_NOTES (mode unstated); the '-t1 1.5x slower' and 'plateau at 2 workers' notes are stale (pre-v1.1.0 15.6 ms sleep-poll stalls). 'Bit-identical to stock LAME' is untested: regression.ps1 never runs stock lame.exe and the znver3 and SSE2 builds already differ (FMA rounding, below -50 dB); the baseline phase2 lame.exe flags are unknown and the build needs a config.h not in the repo. FrameChainValid checks headers only. v1.0.1 lost 6.6% of audio on resampled outputs and v1.1.1 lost frames at CBR 8-56 (the -V2 and CBR 320 rows are unaffected).

## Caveats and trade-offs

First-party numbers only. The win comes from parallelism: 16 threads versus single-threaded stock LAME; per thread SuperLAME is slower (its -t1 is about 1.5x slower than stock LAME). No public script runs the stock-LAME comparison, the baseline binary's build flags are unstated and the test albums are commercial recordings, so the comparison cannot be reproduced. Multithreaded output is not bit-identical to stock LAME (decoded differences of -45 to -87 dB at chunk seams; single-thread output is identical). CBR gains are much smaller than VBR gains (1.49x to 4.73x versus 5.84x to 6.17x in the June report). The docs disagree on scaling: SCALING_NOTES says it plateaus at about 2 workers, while the v1.1.0 README shows gains up to 16 threads after the sleep-poll fix. Earlier builds had a repacker desync bug (fixed by porting fre:ac/BoCA fixes) and v1.1.1 fixed lost frames at low CBR bitrates. The znver4/znver5 engines are unverified; the build and tests are Windows-only (clang, PowerShell). Very new repo (3 stars). Built on LAME r6531 plus a port of fre:ac/BoCA SuperFast (GPL), not a GitHub fork.

Runs many libmp3lame instances in parallel on chunks and repairs the bit reservoir, so the gain is thread parallelism. Single-thread output is bit-identical to stock LAME; multi-thread output differs by an inaudible (below -45 dB) reconciliation at chunk seams. Whole input and output are held in RAM (about 1-2 GB input limit). Needs clang to build the SIMD paths; GPL because it combines LGPL LAME and mpg123 with GPL code ported from fre:ac/BoCA.

## Maintenance

Active (v1.1.1 released 2026-08-21, 21 commits, 3 stars, one closed issue, no pull requests), maintained by one person on a best-effort basis; GPL-2.0-or-later because it combines LGPL LAME and mpg123 with GPL code ported from fre:ac/BoCA, so it is copyable only under GPL terms.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party only: docs/COMPARISON_REPORT.md and docs/SCALING_NOTES.md time SuperLAME against the same LAME r6531 core run single-threaded on a Ryzen 7 5800X3D, and the engine build flags (clang 21.1.6, -O3 -march=znverN in build/build_dispatch.sh) are public, but no public script runs the stock-LAME comparison (tests/scaling.ps1 only compares SuperLAME thread counts with its own -t1), the baseline binary's flags are unstated and the test albums are commercial recordings, so it falls short of A.
- **Verifier notes:** SuperLAME is a new multithreaded frontend that links four CPU-dispatched builds of LAME r6531 and ports Robert Kausch's fre:ac/BoCA SuperFast parallel-chunk encoder and bit-reservoir repacker; it is not a SIMD port of LAME. The baseline is the same LAME core single-threaded, so the speedup is thread-level parallelism (16 threads vs 1), not a faster encoder; I moved benchmark_url to the comparison report because the README never shows a stock-LAME time. Metadata checked on github.com: GPL-2.0-or-later, not a fork, last commit 2026-08-21 (v1.1.1).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/HEAD/README.md>
  - <https://github.com/MSIVST/SuperLAME>
  - <https://github.com/MSIVST/SuperLAME/commits>
  - <https://github.com/MSIVST/SuperLAME/tree/master/docs>
  - <https://github.com/MSIVST/SuperLAME/tree/master/tests>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/COMPARISON_REPORT.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/SCALING_NOTES.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/CHANGELOG.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/BENCHPLAN.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/PROJECT_REPORT.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/BUILDING.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/BUILD_PLAN.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/tests/scaling.ps1>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/build/build_dispatch.sh>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/build/build_final.sh>
- **Sources the enricher read:**
  - <https://github.com/MSIVST/SuperLAME>
  - <https://github.com/MSIVST/SuperLAME/issues?q=is%3Aissue>
  - <https://github.com/MSIVST/SuperLAME/pulls?q=is%3Apr>
  - <https://github.com/MSIVST/SuperLAME/releases>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/README.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/COMPARISON_REPORT.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/SCALING_NOTES.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/CHANGELOG.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/BENCHPLAN.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/PROJECT_REPORT.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/BUILDING.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/BUILD_PLAN.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/docs/FFMPEG-NOTES.md>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/tests/scaling.ps1>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/tests/regression.ps1>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/build/build_dispatch.sh>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/build/build_final.sh>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/src/main.cpp>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/src/worker.cpp>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/src/worker.h>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/src/repacker.cpp>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/src/repacker.h>
  - <https://raw.githubusercontent.com/MSIVST/SuperLAME/master/src/lame_dispatch.cpp>
  - <https://github.com/maikmerten/hmp3>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/msivst/superlame`) · [data/wave10/enrich/raw/github_com_msivst_superlame.json](../../../data/wave10/enrich/raw/github_com_msivst_superlame.json) (enrichment confidence 0.75)

</details>
