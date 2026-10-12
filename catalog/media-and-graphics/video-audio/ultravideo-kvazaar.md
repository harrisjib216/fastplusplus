# Kvazaar

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> BSD-licensed HEVC/H.265 encoder in C from Tampere University; papers report faster all-intra encoding than x265 at equal BD-rate.

| | |
|---|---|
| **Beats** | x265 |
| **Claimed result** | Snippet only (papers not opened): a C implementation of Kvazaar is 19% faster than x265 for the same coding efficiency with 8 threads and 38% faster with 16 threads (SiPS 2015 parallelisation paper); at high-speed presets Kvazaar has 4.5% better coding efficiency while twice as fast as x265; AVX2-optimised Kvazaar is 20% faster than AVX2-optimised x265 ultrafast with 9.1% bit-rate gain; Jetson all-intra evaluation (J. Real-Time Image Processing, 2024): Kvazaar is 65.44% and 69.4% faster than x265 with 1.88% and 0.6% BD-rate improvement at the high-speed and high-quality presets. |
| **Workload** | HEVC encoding at equal coding efficiency (BD-rate) versus x265; papers cover multi-core intra encoding, AVX2-optimised intra encoding, and an all-intra evaluation on Nvidia Jetson. |
| **Metric** | throughput |
| **Adoption** | 966 stars; developed by the Ultravideo research group (Tampere University) |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/ultravideo/kvazaar) · [benchmark](https://users.ics.forth.gr/~karam/SiPS2015/Papers/MainConference/SiPS_2015_submission_66.pdf) |

## Verdict

Snippet only; no paper or benchmark page could be opened, and the repository has no x265 comparison (tests/speed_tests.c times only SIMD kernels). The Kvazaar authors' SiPS 2015 paper reports the C implementation 19% faster than x265 at the same intra coding efficiency with 8 threads and 38% with 16; their AVX2 paper reports, on an 8-core Intel i7, 16-thread AVX2 Kvazaar ultrafast at real-time 30 fps intra up to 1080p and 20% faster than AVX2 x265 ultrafast with a 9.1% bit-rate gain. A 2024 Journal of Real-Time Image Processing paper by a different group (R. James, M. Abo-Zahhad, K. Inoue et al.) finds all-intra Kvazaar 65.44% and 69.4% faster than x265 on an Nvidia Jetson, with 1.88% and 0.6% BD-rate gains at high-speed and high-quality presets. x265 versions, compilers and test sequences were not seen.

## Use it when

- You need an HEVC encoder library under a permissive license (BSD-3-Clause) instead of x265's GPLv2 or commercial license, for example inside a closed-source product.
- All-intra or low-delay 8-bit 4:2:0 encoding on multicore x86-64 with AVX2, where the published papers place its fast presets ahead of x265 ultrafast/high-speed presets at equal BD-rate.
- Research or teaching on HEVC encoder speed-ups: the C99 codebase is readable, has per-tool switches and is actively maintained (commits through 2026-09-30).
- Real-time or embedded pipelines with the same group's uvgRTP for RTP transport of the HEVC output.

## Skip it when

- Best compression at slow presets or general random-access encoding: every speed claim is all-intra, and no published comparison against a current x265 release was found.
- Speed-critical encoding without your own benchmark: open issue #378 (2023-12-14) reports Kvazaar slower than x265 in the reporter's test, 'not conforming to the paper introduction'.
- 10-bit or 4:2:2/4:4:4 production work: bit depth is fixed at build time (KVZ_BIT_DEPTH), the AVX2 SAD/SATD/SSD picture kernels compile only for 8-bit builds, FFmpeg's libkvazaar wrapper accepts only yuv420p, and 4:2:2 support was merged only on 2026-09-14.
- ARM servers or phones where SIMD matters: there are no NEON kernels, only generic C (plus Altivec picture kernels on POWER).
- Workflows that rely on correct level signalling (strict decoders, MIAF/HEIF): by default it signals HEVC level 6.2 for every stream (open issue #451).

## How it is fast

Fast presets skip full rate-distortion optimisation (rd=0) and decide modes on SATD costs, with limited intra/inter PU depths, zero-block CU split termination, early skip, hexagon-based motion search (hexbs) and fast residual-cost estimation. Parallelism comes from wavefront (WPP) rows plus overlapped wavefront frames (--owf), scheduled by a dependency-driven thread queue that auto-sizes threads and OWF from the picture size. SAD, SATD, SSD, DCT, intra prediction, interpolation, quantisation, SAO and CABAC coding-tree kernels have AVX2, SSE4.1 and SSE2 versions (Altivec picture kernels on POWER) picked at run time by a CPUID-based strategy selector.

## Compared with alternatives

Pick it over uavs3e when you need HEVC rather than AVS3, and over VVenC or SVT-AV1 when decoder support for HEVC matters more than the extra compression of VVC or AV1; pair it with uvgRTP when the output is streamed over RTP.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (libkvazaar, pkg-config) plus the kvazaar CLI; Docker image; FFmpeg encoder 'libkvazaar' |
| **Dependencies** | POSIX threads (also on Windows; open issue #403 asks for the native Windows thread API); optional Crypto++ for tile encryption; the HM decoder (TAppDecoderStatic) and ffmpeg only for the test scripts |
| **Minimum toolchain** | C99 (no VLAs, Visual Studio 2015.2+); Autotools or CMake on Linux/macOS; on MinGW use Clang because GCC builds disable AVX2 |
| **Platforms** | x86-64 (AVX2 with BMI/BMI2/LZCNT/POPCNT, SSE4.1, SSE2, runtime dispatch), other CPUs via generic C (Altivec picture kernels on POWER); Linux, Windows, macOS |
| **Thread safety** | Each kvz_encoder owns its thread queue, but kvazaar_open() re-runs kvz_strategyselector_init(), which writes process-wide function pointers and hardware flags; issue #444 (open) reports helgrind errors, including pthread_mutex_destroy with an invalid argument in kvz_close_rdcost_outfiles, when several encoders run in parallel threads. Open and close encoders from one thread. |
| **Drop-in for the baseline** | partial — produces standard HEVC streams and has an FFmpeg wrapper (-c:v libkvazaar), but its API, option names and preset tunings differ from libx265 and x265's preset names map to different tool sets |

## Gotchas

- Preset names copy x264/x265 but the tool sets do not match x265's (for example ultrafast has SAO off and rd=0), so equal preset names are not equal work; the papers compare at presets matched for BD-rate instead.
- --threads and --owf default to auto (logical CPU count, 4 if unknown); for fair timing against x265, pin both encoders' thread counts and check the '--owf=auto value set to' log line.
- Because kvz_strategyselector_init sets global function pointers, a per-encoder cpuid setting (cfg-&gt;cpuid) changes the kernels used by every encoder in the process.
- tests/util.sh valgrind_test_422 calls prepare_444, so the 4:2:2 CI test feeds a 4:4:4 Y4M file with --input-format=P422 and may not exercise real 4:2:2 input.

## Known shortcomings

- Snippet-only numbers (SiPS 2015 paper on forth.gr and researchportal.tuni.fi, both blocked): the repo, doc/ and wiki carry no numbers. Intra-only comparison with presets matched by BD-rate, so the work differs from x265's; issue #378 reports Kvazaar slower than x265 in practice.
- The repo has no x265 benchmark (tests/speed_tests.c times kernels only). The default level 6.2 is always signalled (#451, cfg.c lines 154-155); kvazaar_open reruns kvz_strategyselector_init and writes global function pointers (multi-encoder races, #444); AVX2 SAD, SATD and SSD exist only for KVZ_BIT_DEPTH 8; no NEON; the FFmpeg libkvazaar wrapper is yuv420p only; tests/util.sh's valgrind_test_422 calls prepare_444.

## Caveats and trade-offs

Snippet only: all numbers come from search-result snippets of blocked papers (SiPS 2015 'Parallelization of Kvazaar HEVC Intra Encoder for Multi-core Processors', 'AVX2-optimized Kvazaar HEVC intra encoder', 'Kvazaar HEVC encoder for efficient intra coding', and 'Performance evaluation of all intra Kvazaar and x265 HEVC encoders on embedded system Nvidia Jetson platform', J. Real-Time Image Processing 2024, https://link.springer.com/article/10.1007/s11554-024-01429-5); x265 versions, presets and CPU models were not seen. All comparisons are all-intra (intra-only) encoding, not general inter coding, and speed is compared at preset pairs matched for coding efficiency, so the two encoders run different presets (different work); the 2015-2016 numbers are against x265 of that era. The Kvazaar README itself carries no benchmark numbers. Counter-evidence: issue #378 (open since 2023-12-14, no maintainer reply) reports Kvazaar encoding slower than x265 in the reporter's test, 'not conforming to the paper'.

HEVC encoder only; README states speed and RD quality 'will continue to improve'.

## Maintenance

Actively maintained (v2.3.2 released 2025-09-16, commits to 2026-09-30, 62 open issues) and BSD-3-Clause, so it can be copied or linked into closed products; the speed advantage over x265 rests on all-intra papers from 2015-2024.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Every number exists only in search-result snippets of blocked papers (IEEE SiPS 2015 and AVX2 papers by the Kvazaar authors; J. Real-Time Image Processing 2024 Jetson evaluation); the repository (README, doc/, wiki) carries no benchmark numbers or scripts, so C at most per the snippet-only rule. The paper pages could not be opened (forth.gr, Springer, IEEE, researchportal.tuni.fi blocked), so x265 versions, presets and CPU models were not seen.
- **Verifier notes:** Metadata confirmed on GitHub: BSD-3-Clause, 966 stars, last commit 2026-09-30, latest release v2.3.2 (2025-09-16), not archived. benchmark_url set to the SiPS 2015 paper PDF found in search results (not opened: forth.gr is blocked); the snippet-confirmed claims (19%/38% at 8/16 threads, 2x at high-speed presets, AVX2 20% vs x265 ultrafast with 9.1% bit-rate gain, Jetson 65.44%/69.4%) match claimed_speedup.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/README.md>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/LICENSE>
  - <https://github.com/ultravideo/kvazaar>
  - <https://github.com/ultravideo/kvazaar/commits>
  - <https://github.com/ultravideo/kvazaar/tree/master/doc>
  - <https://github.com/ultravideo/kvazaar/wiki>
  - <https://github.com/ultravideo/kvazaar/issues/378>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/README.md>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/src/Makefile.am>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/src/kvazaar.h>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/src/kvazaar.c>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/src/encoder.c>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/src/cfg.c>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/src/strategyselector.c>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/src/strategies/strategies-picture.c>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/src/strategies/strategies-ipol.c>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/src/strategies/avx2/picture-avx2.c>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/tests/speed_tests.c>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/tests/util.sh>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/tests/test_owf_wpp_tiles.sh>
  - <https://raw.githubusercontent.com/ultravideo/kvazaar/HEAD/tests/test_chroma_subsampling_422.sh>
  - <https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/libkvazaar.c>
  - <https://github.com/ultravideo/kvazaar>
  - <https://github.com/ultravideo/kvazaar/commits/master>
  - <https://github.com/ultravideo/kvazaar/tree/master/src/strategies>
  - <https://github.com/ultravideo/kvazaar/tree/master/tests>
  - <https://github.com/ultravideo/kvazaar/tree/master/tools>
  - <https://github.com/ultravideo/kvazaar/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/ultravideo/kvazaar/issues/378>
  - <https://github.com/ultravideo/kvazaar/issues/444>
  - <https://github.com/ultravideo/kvazaar/issues/451>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/ultravideo/kvazaar`) · [data/wave10/enrich/raw/github_com_ultravideo_kvazaar.json](../../../data/wave10/enrich/raw/github_com_ultravideo_kvazaar.json) (enrichment confidence 0.6)

</details>
