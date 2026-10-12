# Nelux (NeLux)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (Python package with PyTorch tensor output)` · `AGPL-3.0` · 🟢 active

> FFmpeg-backed Python video reader returning PyTorch tensors; parallel RGB conversion outruns torchcodec and ffmpeg-CLI rgb24 pipes.

| | |
|---|---|
| **Beats** | FFmpeg CLI piped decode (ffmpeg-rgb24 subprocess; ffmpeg-nvdec subprocess for the GPU path); torchcodec also compared |
| **Claimed result** | From tests/output/comprehensive/final/results.json (Windows 11, i9-13900K + RTX 3090), fps for H.264 decode to RGB uint8: default reader (prefetch=False, 'nelux-cpu-sync') 3393.5 / 2563.4 / 539.4 at 720p / 1080p / 4K; prefetch row ('nelux-cpu-fanout', which the README headline labels 'nelux (default)') 3422 / 2642 / 607; torchcodec 2924 / 1589 / 367; ffmpeg CLI -vf format=rgb24 subprocess 2273 / 1102 / 254; ffmpeg decode-only -f null subprocess 2906 / 2638 / 735. Default reader over ffmpeg-rgb24: 1.49x / 2.33x / 2.13x; over torchcodec: 1.16x / 1.61x / 1.47x (derived from page data). With convert_workers=0 (tests/output/thread_modes.json): 3167 vs torchcodec 3090 at 720p, 1755 vs 1728 at 1080p, 394 vs 401 at 4K, i.e. parity. NVDEC fps nelux vs ffmpeg -hwaccel cuda -f null subprocess: 1651 vs 1253, 667 vs 592, 175 vs 162 (1.32x / 1.13x / 1.08x, derived from page data). |
| **Workload** | H.264 decode to RGB uint8 HWC tensors: 720p Big Buck Bunny clip and synthetic 1080p and 4K H.264 clips, 600 frames per run (300 at 4K). nelux and torchcodec are timed in-process after the reader is constructed; the ffmpeg baselines are CLI subprocesses (-vf format=rgb24 -f rawvideo to the null device for CPU; -hwaccel cuda -hwaccel_output_format cuda -f null for NVDEC, which does no RGB conversion) timed including process launch, probe and decoder/CUDA initialisation. The published final/results.json rows are single records (about 0.18-0.6 s of wall time, one resource sample each), not the medians the README describes. |
| **Metric** | throughput |
| **Hardware** | Intel i9-13900K (24 logical cores) + RTX 3090 |
| **Compiler and flags** | Compiler version and flags of the benchmarked wheel not stated. Current CMakeLists.txt forces Release with LTO and fast-math on and AVX2 off; README says Windows builds need MSVC 18; build via scikit-build-core + CMake + Ninja + vcpkg. Decode work is FFmpeg's libavcodec (README: FFmpeg 8.x at benchmark time; wheels now pin TAS-FFMPEG 8.1.2 in tools/ffmpeg.lock). The ffmpeg CLI baseline is whatever ffmpeg is on PATH (shutil.which); tests/output/perf_findings.md names ffmpeg 8.0.1-gyan on the test machine. Results file records nelux_version 0.10.1 while the README says 0.11.0. |
| **Adoption** | 29 stars |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/NevermindNilas/Nelux) · [benchmark](https://github.com/NevermindNilas/Nelux) |

## Verdict

First-party, Windows 11 on an i9-13900K + RTX 3090, nelux 0.10.1/0.11.0 build (compiler and flags not recorded) over FFmpeg 8.x, H.264 to RGB uint8, 600 frames (300 at 4K): default reader 3393 / 2563 / 539 fps at 720p / synthetic 1080p / synthetic 4K vs torchcodec 2924 / 1589 / 367 and an ffmpeg -vf format=rgb24 subprocess 2273 / 1102 / 254. The ffmpeg rows include process start-up while nelux is timed after reader construction, convert_workers=0 brings nelux to torchcodec parity, and the rows are single 0.18-0.6 s runs taken on a build that still had the convert-pool RAM leak.

## Use it when

- Feeding a PyTorch training or inference loop from H.264/HEVC files at 1080p or above, where single-threaded RGB conversion is the bottleneck and the machine has idle cores (first-party: 1.6x torchcodec at 1080p, 1.47x at 4K).
- NVDEC decode straight into cuda:0 tensors with the colour conversion done on the GPU, avoiding a host round-trip.
- Replacing ffmpeg subprocess pipes in Python (decode, process, NVENC or x264 encode, audio passthrough) with an in-process library, especially for many short clips where process start-up dominates; reconfigure() reuses a reader across files.
- ML work that needs per-block motion vectors from FFmpeg's decoder side data (CPU path only).

## Skip it when

- CPU-limited hosts or multi-worker DataLoaders: the default mode used 874-1656% CPU against torchcodec's 344-502% for the published gains, and with convert_workers=0 it is only torchcodec-speed.
- When raw decode speed is the problem: every CPU row is FFmpeg's libavcodec, so it cannot beat ffmpeg's own decoder; the ffmpeg -f null decode-only run was faster than nelux at 4K (735 vs 539 fps).
- Closed-source or hosted products: NeLux is AGPL-3.0 and the bundled FFmpeg is GPL-2.0-or-later (libx264, libx265 linked).
- Environments off its narrow matrix: Python 3.13+, a wheel built per PyTorch minor (currently 2.14), CUDA 13 wheels need compute capability 7.5+ (Pascal/Volta need a source build), macOS is CPU-only.
- Versions before 0.12.5 on long CPU runs: the default convert pool leaked roughly one decoded frame of host RAM per frame.

## How it is fast

Decoding is stock libavcodec with frame threading (num_threads=0 lets FFmpeg pick), so no codec work is faster than FFmpeg. The gain is a pool of convert worker threads that run the per-frame libswscale YUV-to-RGB conversion in parallel, with a sequence-keyed reorder map and bounded in-flight backpressure so conversion no longer serialises behind decode; current code also recycles 64-byte-aligned output buffers wrapped with from_blob instead of allocating a tensor per frame. On NVDEC, a CUDA NV12/P010-to-RGB kernel converts on the GPU and the tensor never leaves the device. The README itself says that with convert_workers=0 fps, CPU and RSS land within about 2% of torchcodec.

## Compared with alternatives

Pick NeLux over video_reader-rs when the consumer is PyTorch (including CUDA tensors from NVDEC) and spare cores can absorb the parallel RGB conversion. It does not decode H.264 faster than libavcodec, so if decode itself is the bottleneck, edge264 or rivet-h26x (faster H.264/H.265 decoders than libavcodec in their own benchmarks) are the relevant siblings.

## Integration

| | |
|---|---|
| **Form** | Python wheel: pybind11 C++20 extension (shared lib) with FFmpeg shared libraries bundled |
| **Dependencies** | PyTorch (must be imported first; wheel tied to one torch minor), numpy, bundled TAS-FFMPEG 9.0.2 (GPL); CUDA 13 runtime from the CUDA torch wheel for NVDEC/NVENC. Source builds: scikit-build-core, CMake, Ninja, vcpkg, MSVC 18 on Windows |
| **Minimum toolchain** | Python 3.13+, C++20 (MSVC 18 on Windows), CMake + Ninja; CUDA 13 for published GPU wheels |
| **Platforms** | Windows x64 and Linux x86_64 (manylinux_2_28+) with CPU + NVDEC/NVENC; macOS arm64 14+ CPU only |
| **Thread safety** | not documented for a shared reader; each reader runs its own producer and convert threads, and the changelog records a fixed race where decode_batch and the prefetch producer shared formatCtx |
| **Drop-in for the baseline** | partial — different API from torchcodec's VideoDecoder and not a CLI replacement for ffmpeg, but same HWC uint8 convention and RGB bytes identical to ffmpeg -vf format=rgb24 on 12 of 14 tested pixel-format/colourspace combos (yuv420p10le differs, PSNR about 48 dB) |

## Gotchas

- The README's 'RSS is essentially identical' line is not supported by its own data. In the in-process comprehensive run every decoder shares one Python process and RSS climbs down the rows (601 MB to 2597 MB at 720p, 4864 MB to 9264 MB at 4K), so it is a running high-water mark, not per-decoder. The per-subprocess thread_modes.json shows nelux default at 1532 / 3769 / 7353 MB against torchcodec 673 / 732 / 1095 MB, which matches the convert-pool host-RAM leak (about one decoded frame retained per frame) that the changelog fixed in 0.12.5, after the published numbers were taken.
- Defaults have drifted from the docs and the benchmark: README and changelog say convert_workers=None means min(hw, 16), but current Decoder.cpp uses clamp(hw - decode threads, 1, 8) (8 on a 24-thread CPU) with an in-flight cap of clamp(64 MB / frame, 4, 16), and FFmpeg is now 9.0.2; the published fps were never re-measured on these.
- import torch must come before import nelux; on Windows another package's avcodec DLL of the same soname can win the load, so check nelux.__ffmpeg_version__ reports '9.0.2-tas'.
- Several wrong-output bugs were fixed in 2026 (decode_batch used BT.601 regardless of colour space, #58; NVDEC set_range returned frames offset from the keyframe, #57; set_range with start&gt;0 aborted the process, #60; unchecked CUDA launches gave silent black frames, #69), so pin a recent release.

## Known shortcomings

- Decoding is FFmpeg's libavcodec, so the win over the ffmpeg CLI comes from parallel swscale colour conversion plus the subprocess start-up counted in the ffmpeg timings (ffmpeg -f null at 720p runs 2906 fps against Nelux's 3394 with RGB output); the CLI baseline is whatever ffmpeg is on PATH (8.0.1-gyan in perf_findings) while the wheel pins TAS-FFMPEG 8.1.2; the README's 'default' row is really the prefetch/fanout row; the NVDEC baseline does no RGB conversion.
- Enricher (e117, 2026-10-05): the benchmarked 0.10.1/0.11.0 build had a default convert-pool host-RAM leak of about one frame per decoded frame (CHANGELOG 0.12.5); tests/output/thread_modes.json shows it (nelux default RSS 1532 / 3769 / 7353 MB vs torchcodec 673 / 732 / 1095 MB at 720p / 1080p / 4K), so the README's 'RSS essentially identical' claim, taken from a cumulative in-process high-water mark, is invalid. fps were never re-measured after the leak fix, pooled buffers, FFmpeg 9.0.2 or the new convert-worker default clamp(hw - decode threads, 1, 8) (README still says min(hw, 16)); the 1080p/4K clips are synthetic testsrc2. Tier C stands (numbers from a build later fixed for a correctness bug); the decoder is FFmpeg's, so the entry could fold under FFmpeg.

## Caveats and trade-offs

Decoding is FFmpeg's libavcodec (software H.264 with frame threads, and FFmpeg's CUDA path for NVDEC), so none of the gain is codec speed. The README itself says the win over torchcodec is entirely the convert worker pool: with convert_workers=0 nelux is within about 2% of torchcodec, and the default fan-out costs about 2.5-3x the CPU (874-1656% vs 344-502%). The ffmpeg baselines are CLI subprocesses timed including process start-up, probe and decoder init, while nelux is timed after reader construction; at 720p the ffmpeg decode-only run (-f null, no RGB conversion) reaches only 2906 fps against nelux's 3394 fps with conversion, which shows the fixed per-process cost in the baseline. The NVDEC baseline does no NV12-to-RGB conversion and its gap shrinks from 32% at 720p to 8% at 4K as per-run time grows, the pattern of amortised start-up rather than faster decode. The README headline row labelled 'nelux (default)' matches the prefetch ('nelux-cpu-fanout') row in final/results.json; the prefetch=False default row is 3393.5 / 2563.4 / 539.4 fps. Published rows are single short runs (about 0.18 s at 720p) without stored medians, measured on nelux 0.10.1/0.11.0; the decode path has changed since (0.16.0-0.20.0). Single hardware data point on Windows 11. AGPL-3.0.

About 2.5-3x the CPU use of torchcodec in default mode (convert worker pool); needs PyTorch imported first; AGPL-3.0, and the bundled FFmpeg binaries are GPL-2.0-or-later (libx264 and libx265 linked in). Python API over a C++ core.

## Maintenance

Very active (0.20.0 in pyproject.toml, last commit 2026-09-28, releases every few weeks), installable with pip on Windows, Linux and macOS, but AGPL-3.0 with GPL FFmpeg inside, and the benchmark tables date from 0.11.0 (May 2026) while the decode pipeline and defaults have changed since.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party numbers from a public harness (tests/comprehensive_bench.py, tests/bench_thread_modes.py, tests/utils/bench_harness.py) with checked-in results (tests/output/comprehensive/final/results.json, tests/output/thread_modes.json) and a named CPU (i9-13900K), but no compiler version or flags for the benchmarked wheel, so C. The claim is overstated: the decode is FFmpeg's libavcodec in every row, and the margins over the ffmpeg CLI come from parallel libswscale conversion and from the baseline paying process start-up per run.
- **Verifier notes:** Not a thin binding (own threaded convert pool and fused CUDA NV12-to-RGB kernel over FFmpeg), so not marked duplicate, but its speed claim over FFmpeg is pipeline and threading, not decoding; the orchestrator may still prefer folding it under the FFmpeg entry. Numbers are real (they match checked-in result files); the overstatement is the 'default' label and the start-up-handicapped subprocess baseline.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party results.json
- **Pages the verifier opened:**
  - <https://github.com/NevermindNilas/Nelux>
  - <https://github.com/NevermindNilas/Nelux/commits/master>
  - <https://github.com/NevermindNilas/Nelux/tree/master/tests/output>
  - <https://github.com/NevermindNilas/Nelux/tree/master/tests/output/comprehensive>
  - <https://github.com/NevermindNilas/Nelux/tree/master/tests/output/comprehensive/final>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/README.md>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/comprehensive_bench.py>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/bench_thread_modes.py>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/utils/bench_harness.py>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/output/comprehensive/final/results.json>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/output/comprehensive/current_v2/results.json>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/output/comprehensive/current/results.json>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/output/comprehensive/REPORT.md>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/output/thread_modes.json>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/output/perf_findings.md>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/docs/CHANGELOG.md>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tools/ffmpeg.lock>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/README.md>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/docs/CHANGELOG.md>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/comprehensive_bench.py>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/bench_thread_modes.py>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/utils/bench_harness.py>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/output/perf_findings.md>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/output/comprehensive/REPORT.md>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/output/thread_modes.json>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tests/output/comprehensive/final/results.json>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/tools/ffmpeg.lock>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/src/Nelux/backends/Decoder.cpp>
  - <https://raw.githubusercontent.com/NevermindNilas/Nelux/HEAD/include/Nelux/backends/Decoder.hpp>
  - <https://github.com/NevermindNilas/NeLux/commits/master/tests/output/comprehensive/final/results.json>
  - <https://github.com/NevermindNilas/NeLux/issues?q=is%3Aissue>
  - <https://github.com/NevermindNilas/python-decoders-benchmarks>
  - <https://github.com/NevermindNilas/python-decoders-benchmarks/tree/main>
  - <https://raw.githubusercontent.com/NevermindNilas/python-decoders-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/NevermindNilas/python-decoders-benchmarks/HEAD/1280x720_results_frame_count_comparison.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/nevermindnilas/nelux`) · [data/wave10/enrich/raw/github_com_nevermindnilas_nelux.json](../../../data/wave10/enrich/raw/github_com_nevermindnilas_nelux.json) (enrichment confidence 0.75)

</details>
