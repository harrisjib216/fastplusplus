# edge264

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Compact C H.264 (progressive High, MVC) decoder that beats single-threaded FFmpeg libavcodec by about 1.2x in its CI.

| | |
|---|---|
| **Beats** | FFmpeg libavcodec H.264 decoder (README chart also shows LibAVC and OpenH264) |
| **Claimed result** | README-benchmark.svg ('Decoding time measured on 27/07/2026 (lower is better)', median of 5 runs, all decoders single-threaded): x86-64 edge264 Clang 3.9 s, GCC 4.5 s, WASM 5.2 s, FFmpeg 4.6 s, LibAVC 6.4 s, OpenH264 8.2 s; arm64 edge264 Clang 3.8 s, GCC 3.9 s, WASM 5.0 s, FFmpeg 4.7 s, LibAVC 4.5 s, OpenH264 6.8 s. Clang build about 1.18x faster than single-threaded FFmpeg on x86-64 and 1.24x on arm64; the GCC build roughly ties FFmpeg on x86-64 (4.5 vs 4.6 s) and is about 1.2x faster on arm64 (derived from page data). FOSDEM'24 talk title linked from README: reach 10% faster speed and 3x code reduction over the state of the art. |
| **Workload** | Decoding the 1080p 10 s Big Buck Bunny H.264 clip (30 MB, converted to Annex B), median of 5 runs, every decoder single-threaded: edge264_test -by (n_threads 0, YUV comparison off; wall clock via CLOCK_MONOTONIC), ffmpeg -benchmark -threads 1 -c:v h264 -f null (the script reads the utime field, i.e. user CPU time), LibAVC avcdec with --num_cores 1 (wall clock around the process), OpenH264 h264dec (its own reported time); run on GitHub-hosted runners ubuntu-latest (x86-64) and ubuntu-24.04-arm (arm64). |
| **Metric** | throughput |
| **Hardware** | GitHub-hosted runners (ubuntu-latest for x86-64, ubuntu-24.04-arm for arm64) per .github/workflows/benchmarks.yml; CPU model and core count not stated. |
| **Compiler and flags** | Stock GCC and Clang from the runner's Ubuntu apt packages (versions not pinned or stated), make STATIC=yes with Makefile flags -march=native -std=gnu11 -O3 -flax-vector-conversions; WASM via emmake with -mrelaxed-simd under Node; FFmpeg is the Ubuntu apt package (version not stated), LibAVC built with CMake Release, OpenH264 with its default make. |
| **Adoption** | 437 stars |
| **Last commit** | 2026-07-28 |
| **Links** | [repository](https://github.com/tvlabs/edge264) · [benchmark](https://raw.githubusercontent.com/tvlabs/edge264/HEAD/README-benchmark.svg) |

## Verdict

The repo's own workflow_dispatch CI (27 July 2026, GitHub-hosted ubuntu-latest x86-64 and ubuntu-24.04-arm runners, CPU model not recorded, median of 5) decoded the 1080p 10 s Big Buck Bunny clip single-threaded: edge264 Clang 3.9 s and GCC 4.5 s versus apt FFmpeg (-threads 1) 4.6 s on x86-64, and 3.8/3.9 s versus 4.7 s on arm64, built with -march=native -std=gnu11 -O3 using the runner's apt compilers. Reading bench-decoders.py against edge264_test.c shows both native edge264 and FFmpeg figures are user CPU time of the whole process (edge264's 'CPU:' line from getrusage ru_utime, FFmpeg's -benchmark utime), so that pair is like for like; only the WASM bar (wall clock), LibAVC (wall clock around the process) and OpenH264 (self-reported) use other clocks, and the harness never checks that edge264 decoded every frame (-y turns off YUV comparison and the PASS/FAIL count is ignored), although this same clip failed to decode in 2022 (issue #5, since closed).

## Use it when

- Decoding progressive 8-bit 4:2:0 H.264 (High/Main/constrained Baseline without FMO) on one core per stream, for example many concurrent streams on a server
- Embedding a small, dependency-free BSD-3-Clause C decoder instead of linking all of libavcodec
- WebAssembly or browser decoding: the same source builds with emscripten (WASM SIMD, optional relaxed SIMD) and ran at 5.0-5.2 s on the benchmark clip versus 4.6-4.7 s for native FFmpeg
- MVC (stereo 3D) streams: both views come out of one decoder, the second in Edge264Frame.samples_mvc
- x86-64 or arm64 builds where you control the compiler; Clang builds measured faster than GCC builds on x86-64 (3.9 vs 4.5 s)

## Skip it when

- Interlaced (PAFF/MBAFF) broadcast or camera content, 10-bit, 4:2:2 or 4:4:4 streams: unsupported, decode returns ENOTSUP
- Latency-bound single-stream playback where FFmpeg's frame/slice threading counts: multithreading is labelled experimental in edge264_test, issue #30 reports a segfault in worker_loop with n_threads 1-2, and the edge264-mvc fork's chart shows multithreaded FFmpeg ahead
- Untrusted input without your own sandboxing: no fuzzing is set up (issue #8 open since 2024), and open issues report a hang (#21), a crash in add_idct8x8 on ESP32-P4 (#28) and decode failures on user samples (#19)
- Players that depend on exact output order: issues #16 (Main profile) and #32 (High profile, August 2026, a P frame emitted where FFmpeg emits a B frame) are open
- Projects that need a stable ABI or MSVC: pre-1.0 with API renames planned for 1.0 (2027), and only GCC and Clang are supported

## How it is fast

It replaces hand-written assembly with GCC/Clang vector extensions and aliased SSE/NEON intrinsics (about 80% shared code across x86 and ARM, and WASM SIMD via Clang). The slice decoder is a forward pipeline of non-inlined code blocks joined by tail calls, with tree-shaped jump tables for intra prediction, to keep the hot code small enough for L1. Branches are removed with fake 'unavailable' neighbour macroblocks around each frame and relative neighbour offsets, the bitstream reader uses a register-wide cached reader with on-the-fly SIMD unescaping, and CABAC keeps its state in full-width registers so it renormalises less often and decodes bypass bins in batches.

## Compared with alternatives

Among catalogued video decoders, rivet-h26x claims gains over libavcodec mainly with all threads, on H.265 wavefront content; pick edge264 when you want a small embeddable C library for progressive H.264 with single-thread speed, a WASM build or MVC output, and stay with FFmpeg when you need the full H.264 feature set or multithreaded latency.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (Makefile; CMakeLists.txt wraps it as imported target edge264::edge264) |
| **Dependencies** | none beyond libc and pthreads; SDL2 is loaded at runtime only by the edge264_test display mode |
| **Minimum toolchain** | C11 (gnu11) with GCC or Clang vector extensions; Clang 15+ for the generic backend on other ISAs; emscripten for WASM |
| **Platforms** | x86/x64 (SSE; optional runtime dispatch to x86-64-v2/v3 builds via VARIANTS), ARM32/64 with NEON, WASM32/64 SIMD, other little-endian ISAs via Clang generic vectors; macOS, Linux, Windows (MinGW), Android, iOS |
| **Thread safety** | One decoder context per stream; n_threads spawns background workers (experimental). Logging callbacks may run on worker threads for macroblock logs, alloc/free callbacks on the calling thread; concurrent calls into one context are not documented as safe |
| **Drop-in for the baseline** | partial: it replaces libavcodec's h264 decoder only for progressive 8-bit 4:2:0 Annex B streams, through its own NAL-level API rather than avcodec_send_packet/receive_frame |

## Gotchas

- The README API reference is out of date against edge264.h: it documents the decode_NAL callback as free_cb(void \*free_arg, int ret) while the header declares Edge264UnrefCb(int ret, void \*unref_arg), and shows pixel_depth_Y where the header has bit_depth_Y; code to the header.
- The README's CMake FetchContent example pins GIT_TAG v1.0, but the only tag in the repository is v0.1 (2014), so pin a commit hash instead.
- With borrow = 0 a frame is valid only until the next edge264_decode_NAL call, and ENOBUFS means drain frames with edge264_get_frame and resubmit the same NAL; errors are detected late per NAL by clamping, so corrupt input yields frames plus an mb_errors probability map rather than a hard failure.
- Open correctness fixes are unmerged: PR #26 (High profile default scaling matrices per H.264 Table 7-2) and PR #25 (single-threaded decode hang when ready_tasks is zero), both from February 2026.

## Known shortcomings

- Own CI benchmark (.github/workflows/benchmarks.yml, misc-scripts/bench-decoders.py, median of 5, every decoder single-threaded with ffmpeg -threads 1): Clang build 3.9 vs FFmpeg 4.6 s on x86-64 (1.18x) and 3.8 vs 4.7 s on arm64 (1.24x); the GCC build ties on x86-64 (4.5 vs 4.6 s). Timing is like-for-like for the native rows (bench-decoders.py reads edge264's getrusage ru_utime 'CPU:' line and FFmpeg's utime; only the WASM, LibAVC and OpenH264 rows use wall or self-reported time); flags -march=native -O3 but runner CPU model and compiler versions unstated, so C. Decodes progressive High and MVC profiles only; the benchmark skips the output check (-y). The fork edge264-mvc adds multithreading, where FFmpeg with all cores wins.
- The harness never checks decode success (-y, PASS/FAIL ignored), and the same clip failed to decode in 2022 (issue #5, closed). Open issues: #32 and #16 (output order), #30 (multithread segfault), #21 (hang), #28 (idct8x8 crash), #8 (no fuzzing); unmerged fix PRs #26 (scaling-matrix defaults) and #25 (single-thread hang). The README API is out of date against edge264.h (callback argument order); the FetchContent tag v1.0 is missing (only v0.1 exists).

## Caveats and trade-offs

Numbers exist only as labels inside README-benchmark.svg, produced by the project's own CI (workflow_dispatch) on shared GitHub runners whose CPU model is not recorded; compiler and FFmpeg versions are the runner's apt defaults and are not pinned. The comparison is single-threaded only: FFmpeg is run with -threads 1, and stock edge264's multithreading is flagged experimental and is reported broken by the edge264-mvc fork, whose own chart shows multithreaded FFmpeg (2.4 s x86-64, 2.0 s arm64) beating multithreaded edge264-mvc (2.9 s, 2.6 s). Timing is asymmetric: edge264 is wall clock while the FFmpeg figure is the CLI's user CPU time (utime), which excludes system time and includes CLI demux and null-mux overhead. edge264 decodes only 8-bit 4:2:0 progressive High and MVC (no interlaced PAFF/MBAFF, no FMO, no 4:2:2/4:4:4 or high bit depth; 109/224 JVT conformance bitstreams decode), so FFmpeg is a full-featured decoder doing the same work on this progressive clip but covering far more; the benchmark disables output checking (-y). The fork documents correctness bugs in stock edge264 (SSE temporal-direct MV rounding off by up to a quarter pel, PPS scaling-matrix fall-back, high-QP 8x8 dequant overflow); whether the benchmark clip exercises them is not known. Pre-1.0, API freeze targeted for 2027.

Supports Progressive High and MVC 3D profiles only, 8-bit 4:2:0; interlaced, higher bit depths and 4:2:2 are planned. Uses compiler vector extensions instead of hand-written assembly (SSE and NEON from one code path, WASM via Clang). README targets API freeze in 2027.

## Maintenance

Active solo project (971 commits, last commit 2026-07-28, 437 stars) under BSD-3-Clause and easy to vendor, but pre-1.0 with API freeze targeted for 2027 and several open crash, hang and output-order reports.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party chart generated by the repo's own public CI benchmark (.github/workflows/benchmarks.yml running misc-scripts/bench-decoders.py, plotted by misc-scripts/bench-charts.py) with Makefile flags known (-march=native -std=gnu11 -O3 -flax-vector-conversions), but compiler versions are whatever the runner's apt packages provide and the CPU model of the GitHub-hosted runners is not stated, so it falls short of A.
- **Verifier notes:** Chart labels verified by parsing the matplotlib SVG comments and their x positions (series order Clang, GCC, WASM, FFmpeg, LibAVC, OpenH264); record numbers are correct but omitted the WASM bars and the fact that FFmpeg is pinned to one thread. Metadata matches: BSD-3-Clause, 437 stars, not a fork, last commit 2026-07-28.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tvlabs/edge264>
  - <https://github.com/tvlabs/edge264/commits/master>
  - <https://github.com/tvlabs/edge264/tree/master/misc-scripts>
  - <https://github.com/tvlabs/edge264/tree/master/.github/workflows>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/README.md>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/README-benchmark.svg>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/misc-scripts/bench-decoders.py>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/misc-scripts/bench-charts.py>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/src/edge264_test.c>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/tvlabs/edge264>
  - <https://github.com/tvlabs/edge264/commits/master>
  - <https://github.com/tvlabs/edge264/tags>
  - <https://github.com/tvlabs/edge264/forks>
  - <https://github.com/tvlabs/edge264/pulls>
  - <https://github.com/tvlabs/edge264/issues?q=is%3Aissue>
  - <https://github.com/tvlabs/edge264/issues/5>
  - <https://github.com/tvlabs/edge264/issues/30>
  - <https://github.com/tvlabs/edge264/issues/32>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/README.md>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/README-benchmark.svg>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/Makefile>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/edge264.h>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/src/edge264_test.c>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/misc-scripts/bench-decoders.py>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/misc-scripts/bench-charts.py>
  - <https://raw.githubusercontent.com/tvlabs/edge264/HEAD/.github/workflows/benchmarks.yml>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/tvlabs/edge264`) · [data/wave10/enrich/raw/github_com_tvlabs_edge264.json](../../../data/wave10/enrich/raw/github_com_tvlabs_edge264.json) (enrichment confidence 0.8)

</details>
