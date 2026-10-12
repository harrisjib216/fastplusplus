# uavs3e

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `BSD-4-Clause` · 🔴 abandoned

> Open-source AVS3 (China's AVS3-P2 baseline) encoder with SIMD and fast mode decisions, far faster than the HPM reference encoder.

| | |
|---|---|
| **Beats** | HPM 4.0 (the AVS3 reference software) for encoding speed; x265 veryslow for compression at a roughly similar speed |
| **Claimed result** | Snippet only (paper PDF blocked): uavs3e speed level 3 is 51.8 times faster than HPM 4.0 with a 4.2% overall coding-performance loss; against the x265 veryslow preset 'the coding speed gap is small' while overall coding performance improves by about 27% (average BD-rate savings of 22.7% luma and 46.1% / 46.2% chroma). No speed ratio over x265 was seen; a later real-time-encoder paper claims a 'significant advantage in encoding speed compared to x265' without a number in the snippets. |
| **Workload** | AVS3 encoding (a different codec from HEVC): uavs3e speed level 3 against the HPM 4.0 reference encoder on encode time and BD-rate, and against x265 veryslow on BD-rate at a similar speed. Sequences, thread counts, CPU and compiler were not seen. |
| **Metric** | throughput |
| **Adoption** | 162 stars, 63 forks, 212 commits; Peking University Shenzhen Graduate School, Peng Cheng Laboratory and Guangdong Bohua UHD Innovation Corporation |
| **Last commit** | 2023-08-03 |
| **Links** | [repository](https://github.com/uavs3/uavs3e) · [benchmark](https://www.jdl.link/doc/2011/20220113_An_Efficient_and_Open_Source_Encoder_Uavs3e_for_Video_Compression.pdf) |

## Verdict

Snippet only (the paper PDF on jdl.link is blocked): in 'An Efficient and Open Source Encoder Uavs3e for Video Compression', speed level 3 encodes 51.8 times faster than the AVS3 reference encoder HPM 4.0 at a 4.2% coding loss, and against x265 veryslow (HEVC, a different codec) it has a small speed gap while saving 22.7% luma and 46.1%/46.2% chroma BD-rate. A search snippet adds the test conditions: Intel Xeon Gold 6154 (18 cores, 3.0 GHz), intra period 1 s, fixed QP at four QP points, encoders run single- and multi-threaded; compiler, sequences and which thread setting produced the 51.8x were not seen, and the repository has no benchmark scripts or results.

## Use it when

- You must produce AVS3 bitstreams (for example for a Chinese broadcast or UHD delivery chain) and HPM is too slow for anything beyond conformance testing.
- Research on AVS3 encoder speed-up algorithms, where a readable C encoder with switchable fast-decision flags is a better base than HPM.
- 8-bit 4:2:0 offline encoding on x86-64 with AVX2 or on ARMv8 (the README recommends Kunpeng), where WPP plus frame threads can use many cores.

## Skip it when

- You need HEVC, AVC, AV1 or VVC output: it is not a drop-in for x265 or any FFmpeg encoder, and players and containers with AVS3 support are scarce.
- 10-bit production encoding: bit depth is a compile-time switch, and issue #53 (open, uavs3e 1.3.2, Clang 18.1.8) reports a segfault in uavs3e_if_hor_ver_chroma_w4_avx2 as soon as encoding starts in a 10-bit AVX2 build.
- Projects that need an OSI-approved license: BSD 4-clause with an advertising clause (which names uAVS3d, the decoder).
- Anything that needs ongoing fixes: master's last commit is 2023-08-03, about 40 of 42 issues are open with few replies, and later work went to a separate RealTime branch (uAVS3lib, last updated 2024-10-31) whose own issues report crashes, memory leaks and non-deterministic output.
- Interop-critical pipelines without your own conformance check: issue #43 (open) reports a uavs3e stream that the HPM decoder fails on.

## How it is fast

speed_level gates a stack of encoder-side shortcuts: history-based reuse of split costs at the same CU position, early depth termination, restricted binary/extended-quadtree and DT partition sizes, a coarse intra rough-mode decision on 10 of the angular modes by SATD before refinement, SATD-based pruning of inter and skip candidates, and SAD instead of SATD for sub-pel motion cost. Motion search is TZ-style raster plus diamond search. Rows are encoded in parallel with WPP threads and pictures with a frame-thread pool, and the hot kernels (interpolation, intra prediction, transforms, SAO, ALF, cost functions) have SSE4.2, AVX2 and ARMv8 NEON versions.

## Compared with alternatives

Pick it only when the output must be AVS3; for HEVC use Kvazaar (or x265), for VVC use VVenC and for AV1 use SVT-AV1, all of which are maintained and target formats with broad decoder support.

## Integration

| | |
|---|---|
| **Form** | static lib (shared with BUILD_SHARED_LIBS=1) plus the uavs3enc CLI; Visual Studio 2017 solution on Windows |
| **Dependencies** | libm, pthreads; gawk and CMake 2.8+ for the Linux build (version.sh generates version.h) |
| **Minimum toolchain** | C99 (CMake compiles with -std=c99 -O3, -msse4.2 and -mavx2 per directory); Visual Studio 2017 on Windows. Issue #53 says GCC 14 fails to compile the AVX2 files; PR #23 (open) reports an offsetof redefinition error with GCC 10.2.0. |
| **Platforms** | x86-64 (SSE4.2 with runtime AVX2 dispatch), aarch64 (NEON assembly), loongarch64 (C only); Windows and Linux. macOS build fails per issue #34, and com_api.h forces 8-bit on non-Linux targets. |
| **Thread safety** | Not documented. Each encoder handle owns its WPP and frame thread pools; nothing says separate handles can be driven from different threads. |
| **Drop-in for the baseline** | partial — it replaces HPM as an AVS3 encoder with its own API and config keys; it cannot replace x265 because it emits a different codec |

## Gotchas

- The CLI's 'Total encoding time' and 'Average encoding speed' lines use clock(), which on Linux is CPU time summed over all threads: issue #28 shows 450.6 s reported against 80.2 s wall time with 40 WPP and 40 frame threads. Use the 'Actual encoding time/speed' lines (wall clock, added in PR #17) when timing.
- The pel type in the installed header com_api.h depends on COMPILE_10BIT, so an application must be built with the same macro as the library; 8-bit and 10-bit need separate builds.
- refine_input_cfg() always sets ipf_flag = 0 (intra prediction filter off) whatever the config says, and writes the speed-level partition limits back into the caller's cfg struct.
- The global symbol calculate_histogram is not prefixed and collides when linked into FFmpeg (open PR #38 renames it); the CLI's kbps figure uses integer fps_num / fps_den, so it under-reports bitrate for fractional frame rates such as 24000/1001.

## Known shortcomings

- Snippet-only numbers (jdl.link paper PDF blocked): the 51.8x speed claim is over HPM 4.0, the AVS3 reference encoder, not x265; the paper says the speed gap against x265 veryslow is small with about 27% better coding efficiency. Licence BSD-4-Clause (not OSI approved), usability set to reference. Last commit 2023-08-03, abandoned.
- The CLI's 'Total encoding time' and 'Average encoding speed' use clock(), which on Linux sums CPU time across threads (issue #28: 450.6 s reported against 80.2 s wall with 40 WPP plus 40 frame threads); only the 'Actual' lines are wall time. The paper stays blocked; a snippet gives Xeon Gold 6154 (18 cores, 3.0 GHz), 1 s intra period and 4 fixed QP points, with the thread setting behind the 51.8x unseen. Open 10-bit AVX2 segfault #53; the HPM decoder fails on uavs3e streams (#43); ipf_flag is forced to 0 in refine_input_cfg; an unprefixed calculate_histogram clashes when linking into FFmpeg (PR #38); the RealTime branch has crashes, leaks and nondeterministic output; 40 of 42 issues open.

## Caveats and trade-offs

Snippet only: all numbers come from search snippets of the paper (PDF on jdl.link, blocked here); the repo README has no numbers, methodology or benchmark scripts. The speed win is over the AVS3 reference software HPM 4.0, not over x265: against x265 veryslow the paper reports a small speed gap and better compression, and that comparison crosses codecs (AVS3 vs HEVC). License is BSD 4-clause with an advertising clause (not OSI-approved); the COPYING advertising clause names uAVS3d, the decoder, apparently copied from that project. Last commit 2023-08-03 (loongarch64 fix); 10-bit encoding runs without SIMD.

Encodes AVS3-P2 baseline profile, not HEVC, so it is not a drop-in x265 replacement; SSE4/AVX2 and ARM paths; 10-bit support.

## Maintenance

Abandoned on master since 2023-08-03 and licensed BSD 4-clause (not OSI-approved), so treat it as a reference AVS3 encoder to study or fork rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** C cap: the only numbers are search snippets of the paper 'An Efficient and Open Source Encoder Uavs3e for Video Compression' (PDF host jdl.link blocked), and the repo has no benchmark, results or test conditions. The snippets also show the speed claim is against the AVS3 reference encoder HPM 4.0, not x265, so the record overstated it.
- **Verifier notes:** The record's x265 framing is backwards: per the paper snippet uavs3e roughly matches x265 veryslow on speed and wins on compression, and its 51.8x speed claim is over the HPM 4.0 reference encoder, so I re-pointed the baseline and the benchmark_url (the paper PDF, found via search but blocked; not opened). Usability moved to reference because SPDX marks BSD-4-Clause as not OSI-approved. Metadata checked on github.com: not a fork, not archived, last commit 2023-08-03 (abandoned, over 3 years).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `claimed_speedup`, `workload`, `usability`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/README.md>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/COPYING>
  - <https://github.com/uavs3/uavs3e>
  - <https://github.com/uavs3/uavs3e/commits>
  - <https://github.com/uavs3/uavs3e/tree/master/test>
  - <https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/README.md>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/COPYING>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/test/utest.c>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/test/config.h>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/inc/uavs3e.h>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/inc/com_api.h>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/inc/define.h>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/inc/com_define.h>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/src/uavs3e.c>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/src/lookahead.c>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/src/analyze.c>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/src/me.c>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/src/inter.c>
  - <https://raw.githubusercontent.com/uavs3/uavs3e/HEAD/src/intra.c>
  - <https://github.com/uavs3/uavs3e>
  - <https://github.com/uavs3/uavs3e/tree/master/src>
  - <https://github.com/uavs3/uavs3e/tree/master/src/avx2>
  - <https://github.com/uavs3/uavs3e/tree/master/inc>
  - <https://github.com/uavs3/uavs3e/tree/master/test>
  - <https://github.com/uavs3/uavs3e/tree/RealTime>
  - <https://github.com/uavs3/uavs3e/branches/all>
  - <https://github.com/uavs3/uavs3e/commits/master>
  - <https://github.com/uavs3/uavs3e/issues?q=is%3Aissue>
  - <https://github.com/uavs3/uavs3e/issues?q=is%3Aissue&page=2>
  - <https://github.com/uavs3/uavs3e/issues/16>
  - <https://github.com/uavs3/uavs3e/issues/28>
  - <https://github.com/uavs3/uavs3e/issues/35>
  - <https://github.com/uavs3/uavs3e/issues/37>
  - <https://github.com/uavs3/uavs3e/issues/43>
  - <https://github.com/uavs3/uavs3e/issues/53>
  - <https://github.com/uavs3/uavs3e/issues/61>
  - <https://github.com/uavs3/uavs3e/pulls?q=is%3Apr>
  - <https://github.com/uavs3/uavs3e/pull/38>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/uavs3/uavs3e`) · [data/wave10/enrich/raw/github_com_uavs3_uavs3e.json](../../../data/wave10/enrich/raw/github_com_uavs3_uavs3e.json) (enrichment confidence 0.6)

</details>
