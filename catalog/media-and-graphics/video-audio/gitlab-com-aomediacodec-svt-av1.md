# SVT-AV1

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `C` · `BSD-3-Clause-Clear` · 🟢 active

> AOM's production AV1 encoder in C, built to be much faster than libaom at similar efficiency; no published speed numbers.

| | |
|---|---|
| **Beats** | libaom (AV1 reference encoder); the changelog also positions presets against x265 medium and x264 veryfast |
| **Claimed result** | No speed ratio on any page that could be opened. CHANGELOG v0.8.7 (2021-05-08): 'Preset 8 achieving similar speed levels as x265 medium tuned for VOD operating mode'; v0.9 (2022-01-19): 'New faster presets M9-M12, M12 reaching similar complexity level to that of x264 veryfast'. Snippet only (pages blocked): the Netflix Tech Blog 2020 says SVT-AV1 is similar in compression efficiency to libaom master while achieving significantly lower encoding latency on multi-core platforms (no number); uncited third-party guides quote 10-50x faster than libaom. Other CHANGELOG speedups are against earlier SVT-AV1 releases (e.g. AWS Graviton4 with Clang 19/20). |
| **Workload** | AV1 encoding across presets M0 to M13. The CHANGELOG statements match one SVT-AV1 preset to an x265 or x264 preset at a similar speed, so the encoders do different work at different compression levels; no clip set, thread count or machine is given. |
| **Metric** | throughput |
| **Adoption** | 305 stars and 177 forks on the canonical GitLab repo (75 stars on the GitHub mirror); founded by Intel with Netflix, adopted by the Alliance for Open Media Software Implementation Working Group in August 2020 |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://gitlab.com/AOMediaCodec/SVT-AV1) · [benchmark](https://gitlab.com/AOMediaCodec/SVT-AV1/-/blob/master/CHANGELOG.md) |

## Verdict

Nothing was measured on a reachable page. The CHANGELOG pairs SVT-AV1 presets with x265 medium (M8, v0.8.7) and x264 veryfast (M12, v0.9) at 'similar speed', with no clips, machine or method. The libaom comparison ('similar compression efficiency, significantly lower latency on multi-core', and the 10-50x figures in third-party guides) is known only from search snippets of blocked pages.

## Use it when

- You need AV1 output and libaom's encode time is the bottleneck: VOD or archival encodes at presets 4-6 on a many-core x86-64 server (the docs say about 16 cores are used fairly efficiently for 1080p at those presets).
- Live, low-latency or RTC encoding with --rtc (CBR rate control, low-delay prediction structure, presets M7-M12 in RTC mode as of v3.1/v4.2).
- FFmpeg-based transcoding pipelines through libsvtav1, including 10-bit and HDR (BT.2020/PQ/HLG metadata) and film-grain synthesis.
- AVIF and still-image encoding with --avif (lower memory) and the still-image IQ tune added in v4.0.0.
- Large-scale batch encoding where you can split the source into scene chunks and run several instances pinned to core sets (--pin, taskset, with a lower --lp per instance), as the parameter docs suggest.

## Skip it when

- You need measured evidence that it is faster than libaom, x265 or x264 on your workload: the repository publishes no numbers, only qualitative CHANGELOG lines, and its own comparison harness ships without results.
- Decoding AV1: there is no decoder in current releases. Use dav1d.
- Very high core counts on one 1080p stream: the docs say scaling drops off past about 16 cores at presets 4-6, and presets 0-3 parallelize worse. Chunk the video instead.
- Sub-second-latency live encoding pinned to an old preset map: issue #2263 reports low-delay latency rising from 150-250 ms (v2.1.0, presets 11-12) to 4-5 s after the v3.0.0 preset remapping. Re-validate latency after every upgrade.
- Projects whose license policy needs an OSI-approved license with a patent grant: the code is BSD-3-Clause-Clear (FSF-free but not OSI-approved, and it explicitly grants no patent rights), and patents come separately under the AOM Patent License 1.0, which has a defensive-termination clause.

## How it is fast

The encoder runs as a pipeline of stateless 'processes' (picture analysis, motion estimation, rate control, mode decision, loop filters, entropy coding, packetization) that pass work through FIFO-based system resource managers. That gives parallelism at three levels: different stages at once, several pictures at once, and several segments of one picture at once. It does this without tiles, so in default CRF mode --lp 1 and --lp n produce the same output. Presets switch AV1 tools on or off along a documented curve; from M7 up, for example, it uses 64x64 superblocks, turns off filter intra, global motion (already off from M5), wedge and distance-weighted compound prediction (from M3), and the self-guided restoration filter (from M4). The hot kernels are hand-written SIMD: NASM and intrinsics from SSE2 to AVX2/AVX-512 on x86 (AVX-512 on by default since v2.3.0), and Neon, SVE and SVE2 on AArch64. The build scripts offer LTO and PGO.

## Compared with alternatives

It is the only C AV1 encoder catalogued for speed (rusty-av1-toolkit is a tuned rav1e), so pick it whenever the target format is AV1 and libaom is too slow; VVenC, Kvazaar and uavs3e serve VVC, HEVC and AVS3 instead. Pair it with the catalogued dav1d for decoding, since SVT-AV1 no longer ships a decoder.

## Integration

| | |
|---|---|
| **Form** | static or shared lib (CMake) plus the SvtAv1EncApp CLI; FFmpeg libsvtav1 wrapper |
| **Dependencies** | NASM 2.14+ (or yasm) for x86 builds; cpuinfo (system copy, or fetched and built in since v3.0.0); nothing else at runtime |
| **Minimum toolchain** | C99, CMake 3.16+; GCC 5.4+ or Clang on Linux, Visual Studio 2017/2019 on Windows (per Build-Guide.md) |
| **Platforms** | x86-64 primary (SIMD from SSE2 up; AVX2 recommended, AVX-512 kernels built by default); AArch64 with Neon, SVE and SVE2 kernels; validated on Windows, Linux and macOS; any other target with a C99 compiler runs the C path |
| **Thread safety** | Each encoder handle manages its own internal thread pools (--lp picks a parallelism level, not a thread count; issue #2317 notes many threads are created regardless). Running several encoder instances in one process has a history of hangs: v4.1 added mutexes for this (!2603, !2605, !2619), but issue #2186 (hang when only some instances use preset 8) and #2226 (crash under a fully loaded machine) are still open. |
| **Drop-in for the baseline** | partial: it produces standard AV1 bitstreams that any AV1 decoder reads, but its API, presets and options differ from libaom's aomenc/aom_codec interface |

## Gotchas

- Preset numbers are not stable across releases: v1.7.0 shifted M2-M6 by one preset, v3.0.0 'repositioned the presets and removed one preset resulting in a max preset of M10', and v3.1.0 re-enabled M11/M12 for RTC. The CHANGELOG's 'M8 about x265 medium' (v0.8.7, 2021) and 'M12 about x264 veryfast' (v0.9, 2022) refer to old preset maps.
- Public API breaks at major versions: v3.0.0 (issue 2217) and v4.0.0 removed fields, macros and deprecated structs. Pin the version and recheck callers on upgrade.
- It never inserts keyframes at scene changes, whatever the scd setting (CommonQuestions.md); use an external scene splitter if you need them.
- Open crash reports to check against your configuration: #2356 (SIGSEGV in svt_aom_blend_a64_mask_avx2 on v3.1.2 with GCC 13), #2395 (--hbd-mds 1 at preset 2 with 10-bit input) and #2396 (deblocking not signalled for non-reference frames when CDEF and restoration are off).

## Known shortcomings

- Downgraded to D: Docs/, README and CHANGELOG carry no measured libaom or x265 comparison (CHANGELOG only says preset 8 has 'similar speed' to x265 medium and M12 'similar complexity' to x264 veryfast, at different quality levels); the 10-50x over libaom exists only in search snippets of blocked SPIE 2020/2024 papers and the AOM CTC results. Paper-access retier could reach B. Licence BSD-3-Clause-Clear (no patent grant; SPDX marks it not OSI approved), usability set to reference. Canonical repo is gitlab.com/AOMediaCodec/SVT-AV1 (305 stars, last commit 2026-10-01).
- The in-repo harness test/benchmarking (Meta 2025, libaom against SVT-AV1, CPU time via /usr/bin/time -p) has no committed results and its libaom command lines carry --psnr while the svtav1 command does not, tilting timing toward SVT-AV1. The CHANGELOG's x265 and x264 preset equivalences are stale (presets remapped in v1.7.0 and v3.0.0); the decoder was removed in v2.1.1; open issues #2186 (multi-instance hang), #2263 (low-delay latency 4-5 s) and #2356 (AVX2 crash). Papers remain blocked (arXiv 2307.05208, arXiv 2401.16067, SPIE, AOM CTC PDF); tune forks psy-ex/svt-av1-psy, juliobbv-p/SVT-AV1-HDR and 5fish/SVT-AV1 are quality tunes (duplicates if found).

## Caveats and trade-offs

No numeric speed comparison against libaom, x265 or x264 on any reachable first-party page; the CHANGELOG 'similar speed' statements pair presets at different compression levels and name no hardware. The libaom ratios (10-50x) are snippet-only from blocked third-party pages. The README links peer-reviewed SPIE 2020 ('The SVT-AV1 encoder: overview, features and speed-quality tradeoffs'), SPIE 2021, SPIE 2024 ('Benchmarking hardware and software encoder quality and performance') and the AOM SIWG adaptive-streaming common test conditions document; all were unreachable here (spiedigitallibrary.org and aomedia.org blocked), and a retier from them could reach B. License is BSD-3-Clause-Clear from v0.9 on (BSD-2-Clause up to v0.8.7), which is FSF-free but not OSI-approved and explicitly grants no patent rights; patents are licensed separately under the AOM Patent License 1.0.

Encoder only. Faster presets give up compression efficiency; at the slowest presets it only reaches similar efficiency to libaom. Licensed BSD-3-Clause-Clear plus the AOM Patent License 1.0.

## Maintenance

Very active (v4.2.0 released 2026-07-14, last activity 2026-10-03, 305 stars and 177 forks on GitLab, maintained by the AOM Software Implementation Working Group and used through FFmpeg), but the evidence is D-tier and the BSD-3-Clause-Clear license (not OSI-approved, patents via the separate AOM Patent License) is why the record is marked reference rather than copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now D.
- **Tier reason:** D: the CHANGELOG only says preset 8 reaches 'similar speed levels as x265 medium' and M12 a 'similar complexity level to that of x264 veryfast', with no numbers, machine or method, and the Docs (user guide, Ffmpeg.md, CommonQuestions.md) carry no comparison with libaom or x265; the libaom ratios exist only in search snippets of blocked pages. The peer-reviewed SPIE 2020/2024 papers linked from the README could support B but could not be opened here.
- **Verifier notes:** Downgraded C to D: Docs/, README and CHANGELOG on GitLab carry no measured comparison with libaom or x265, and the AOM CTC PDF and SPIE papers are blocked; a paper-access retier is worth queuing given how notable the project is (do not reject). Usability changed to reference only because SPDX marks BSD-3-Clause-Clear as not OSI-approved (same call the batch-25 verifier made for vvenc); the orchestrator may prefer to rule it copyable by policy. Metadata checked: last commit 2026-10-01, GitHub mirror not archived; commit and release counts in the record were not rechecked.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `stars_or_usage`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/CHANGELOG.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/README.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/LICENSE.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/CommonQuestions.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/Ffmpeg.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/svt-av1_encoder_user_guide.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/README.md>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/repository/tree?path=Docs&per_page=100>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/repository/commits?per_page=1&ref_name=master>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/wikis/Home>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/issues/886>
  - <https://github.com/AOMediaCodec/SVT-AV1>
  - <https://github.com/googleinterns/av1-codec-comparison>
  - <https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json>
- **Sources the enricher read:**
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/README.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/CHANGELOG.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/LICENSE.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/PATENTS.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/CMakeLists.txt>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/CommonQuestions.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/System-Requirements.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/svt-av1-encoder-design.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/svt-av1_encoder_user_guide.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/Parameters.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/Build-Guide.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/ARM-Build-Guide.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/Ffmpeg.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Docs/Appendix-Profiling.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/Source/API/EbSvtAv1Enc.h>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/test/benchmarking/README.md>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/test/benchmarking/run_comparison.sh>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/test/benchmarking/encode.py>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/test/benchmarking/utils.py>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/test/benchmarking/configs/test_video_config.yaml>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/test/benchmarking/configs/test_image_config.yaml>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/test/benchmarking/scripts/libaom/get_and_build.sh>
  - <https://gitlab.com/AOMediaCodec/SVT-AV1/-/raw/master/test/benchmarking/scripts/svtav1/get_and_build.sh>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/repository/tree?path=Docs&per_page=100>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/repository/tree?per_page=100>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/repository/tree?path=test&per_page=100&recursive=true>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/repository/tree?path=test/benchmarking&per_page=100&recursive=true>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/repository/tree?path=.gitlab&per_page=100&recursive=true>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/repository/tree?path=Build&per_page=100&recursive=true>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/issues?state=opened&per_page=100&order_by=updated_at>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/issues/2263>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/issues/2317>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/issues/2186>
  - <https://gitlab.com/api/v4/projects/AOMediaCodec%2FSVT-AV1/issues/2356>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://gitlab.com/aomediacodec/svt-av1`) · [data/wave10/enrich/raw/gitlab_com_aomediacodec_svt_av1.json](../../../data/wave10/enrich/raw/gitlab_com_aomediacodec_svt_av1.json) (enrichment confidence 0.75)

</details>
