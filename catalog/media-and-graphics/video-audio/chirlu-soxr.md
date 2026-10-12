# libsoxr (SoX Resampler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `LGPL-2.1-or-later` · 🔴 abandoned

> LGPL C audio resampler (the SoX engine) that ran 6.8-22x libsamplerate 0.2.2's throughput in a third-party streaming benchmark.

| | |
|---|---|
| **Beats** | libsamplerate 0.2.2 (Secret Rabbit Code, SRC_SINC_MEDIUM_QUALITY and SRC_SINC_BEST_QUALITY converters) |
| **Claimed result** | Third-party table (Mframes/s, higher is better): stereo \~120 dB tier soxr HQ 52.9 vs libsamplerate MEDIUM 4.8 (about 11x, derived from page data); mono 114.3 vs 5.2 (about 22x, derived from page data); 8-ch 12.9 vs 1.9 (about 6.8x, derived from page data); \~140 dB stereo soxr VHQ 32.1 vs libsamplerate BEST 1.6 (about 20x, derived from page data). The page calls soxr the winner of raw host throughput. |
| **Workload** | Streaming sample-rate conversion of a float32 interleaved 997 Hz sine at a fixed near-unity ratio (48000 to 48009.6 Hz, 1 + 200 ppm) in 128-frame blocks under Google Benchmark, single thread (soxr's default runtime spec is 1 thread), reported as million output frames per second for mono, stereo and 8-channel streams at a \~120 dB tier (soxr HQ vs libsamplerate MEDIUM) and stereo at a \~140 dB tier (soxr VHQ vs libsamplerate BEST); run by the SampleRateTap author, who compares his own resampler against both. |
| **Metric** | throughput |
| **Hardware** | shared Xeon @ 2.10 GHz (exact model not stated), median of 5, run 2026-09-25 |
| **Compiler and flags** | Benchmark harness built with GCC 13.3 -O3 (CMake Release); libsamplerate 0.2.2 and soxr 0.1.3 are the Ubuntu 24.04 distribution packages (their own build flags not stated) |
| **Adoption** | 181 stars on this GitHub mirror; ships as a distribution package (Ubuntu 24.04 soxr 0.1.3) |
| **Last commit** | 2018-02-24 |
| **Links** | [repository](https://github.com/chirlu/soxr) · [benchmark](https://github.com/tap/SampleRateTap/blob/main/async/docs/COMPARISON.md) |

## Verdict

The SampleRateTap author's harness (bench_compare.cpp, Google Benchmark, GCC 13.3 -O3, Ubuntu 24.04 packages soxr 0.1.3 and libsamplerate 0.2.2, unnamed shared Xeon at 2.10 GHz, median of 5, 2026-09-25) streams a float32 interleaved 997 Hz sine from 48 kHz to 48 kHz x (1 + 200 ppm) in 128-frame blocks, single-threaded, counting output frames. soxr HQ vs libsamplerate MEDIUM: 114.3 vs 5.2 (mono), 52.9 vs 4.8 (stereo) and 12.9 vs 1.9 (8-ch) Mframes/s; soxr VHQ vs BEST: 32.1 vs 1.6 (stereo). That is about 6.8-22x, derived from page data. Reading the harness found no flaw: soxr reads input in place while libsamplerate gets an extra 128-frame copy, which is negligible at these rates. The page's THD+N measurement covers VHQ (at the 24-bit format ceiling) but not HQ, so the HQ-to-MEDIUM quality pairing rests on vendor-stated stopbands.

## Use it when

- Offline or batch conversion at real ratios (44.1 to 48 kHz, 96 to 44.1 kHz, downsampling for ML front ends). python-soxr's README times 10 s of 48 to 44.1 kHz at 10.8 ms for soxr HQ against 223 ms for libsamplerate sinc_medium, and 14.5 ms for VHQ against 794 ms for sinc_best.
- Replacing libsamplerate SINC_MEDIUM or SINC_BEST in throughput-bound desktop or server code that can absorb about 10-20 ms of filter delay. In the third-party table HQ gets 52.9 vs 4.8 Mframes/s on stereo, and VHQ gets 32.1 vs 1.6 for BEST.
- Mixed-format pipelines that want one call to deinterleave, convert int16/int32/float64 to the engine's type, resample, apply gain and dither back to int16.
- Multichannel streams on spare cores: with num_threads = 0 and an OpenMP build, soxr processes channels in parallel (the default is 1 thread).
- Applications that need tunable quality, e.g. minimum-phase filters for lower pre-ringing, or 28-33-bit precision for mastering.

## Skip it when

- Live monitoring or other paths with a 1-2 ms budget. In the SampleRateTap measurement HQ holds back 424-788 frames (8.8-16.4 ms at 48 kHz) and VHQ 433 frames. The README itself quotes about 1000 output samples (about 20 ms) for HQ at 44.1/48 kHz. libsamplerate MEDIUM holds 46 frames and SampleRateTap 24.
- Upstream builds on AArch64 (Apple silicon, Graviton). FindSIMD32.cmake tries NEON flags only when the processor name starts with 'arm', and SSE flags otherwise, so 0.1.3 builds its scalar engines there. The dofuuz/soxr fork says it enables AArch64 optimization for an over 2x speed-up.
- Closed-source products that must link statically and cannot meet LGPL-2.1 relinking terms. r8brain-free-src is MIT and header-only.
- Projects that need a maintained upstream. The last release is 0.1.3 (2018-02-24). The GitHub mirror has 9 open issues and 6 open pull requests, including a distortion fix (PR #12, 2023), AArch64 support (PR #9, 2022) and a CMake minimum bump (issue #14) that newer CMake needs.
- Real clock-drift correction. soxr has a variable-rate mode but no ratio estimation, so an external servo must feed soxr_set_io_ratio. SampleRateTap recovers the clock itself.

## How it is fast

The README says the design follows Laurent de Soras' 'The Quest For The Perfect Resampler': Julius O. Smith's bandlimited interpolation combined with FFT-based oversampling. In cr.c a long, steep low-pass runs as overlap-save FFT convolution in large blocks (DFT sizes from 2^10 up to 2^17 by default). For the benchmarked near-unity ratio that block upsamples 2x, then a short polyphase FIR with polynomial-interpolated coefficients produces the fractional step, sized to a 400 kB coefficient budget. Rational ratios with small factors skip the coefficient interpolation, and power-of-two factors use half-band stages. CPUID at run time picks the SIMD engines on x86: HQ runs single precision with SSE and PFFFT (cr32s), and VHQ runs double precision with AVX and PFFFT (cr64s). libsamplerate instead does a per-sample time-domain sinc convolution.

## Compared with alternatives

Pick soxr over r8brain-free-src for raw throughput when LGPL is acceptable: in the same SampleRateTap table it is 3.1-3.2x faster at the 120 dB tier and 1.7-2.3x faster at the 140 dB tier, with less delay than r8brain's default settings (VHQ 433 frames vs 1,700-1,782), all derived from page data. Pick r8brain for an MIT, header-only drop-in. LibFResample's numbers come from a different harness (libsamplerate 0.1.8 on a Phenom II), and zita-resampler (GPL) has only directional claims, so neither can be compared with soxr directly.

## Integration

| | |
|---|---|
| **Form** | shared lib (static via -DBUILD_SHARED_LIBS=OFF); optional libsoxr-lsr with a libsamplerate-style API |
| **Dependencies** | none required beyond libm. Optional: OpenMP (multi-channel threading and the FFT-cache locks), the bundled PFFFT (BSD-like licence, on by default for the HQ SIMD engine), libavcodec as an alternative FFT, and libavutil for NEON detection on 32-bit ARM |
| **Minimum toolchain** | C compiler with 64-bit integers; the library builds as -std=gnu89; CMake 3.1 per CMakeLists.txt (INSTALL says 3.0). CMake 4.x needs a minimum-version bump (issue #14; fixed in the dofuuz fork). |
| **Platforms** | x86 and x86-64 with run-time selection between SSE (HQ) and AVX (VHQ) engines; 32-bit ARM NEON when libavutil is found or SOXR_USE_SIMD is set; scalar elsewhere, including AArch64 in upstream 0.1.3; Windows (MSVC, MinGW), Linux, macOS |
| **Thread safety** | One soxr_t per stream; concurrent calls on the same object are not documented as safe. The process-wide Ooura FFT table (fft4g_cache.h) is guarded by an OpenMP readers-writer lock that compiles to no-ops in builds without OpenMP (ccrw2.h). That table serves minimum- and intermediate-phase filter design and the non-SIMD engines. |
| **Drop-in for the baseline** | partial: soxr-lsr.h and libsoxr-lsr implement the libsamplerate API (src_new, src_process, src_callback_new/read, src_simple, src_set_ratio) for float samples, mapping SRC_SINC_\* to soxr's LSR quality recipes. The README says this is not a full emulation and exposes only some of soxr's features. |

## Gotchas

- Integer output is risky in 0.1.3. The int16/int32 RINT_CLIP path tests fe_test_invalid() and writes a full-scale clip value when the FE_INVALID flag is set. Issue #11 and PR #12 (open since 2023-11) report a stale flag corrupting otherwise valid samples. The float32 output path used in the benchmark does not go through this check.
- int16 output is dithered with a seed built from time(0) and the object's address (soxr.c), so results differ from run to run (issue #8, open). The dofuuz fork makes int16 output reproducible and fixes a periodic-zeros dithering bug.
- soxr_oneshot() defaults to LQ quality, not the HQ default of soxr_create(), so pass an explicit quality spec. Streaming calls return a varying number of output frames, and soxr_delay() changes with the streaming state.
- Environment variables override the application's runtime spec: SOXR_NUM_THREADS, SOXR_COEFS_SIZE, SOXR_MIN_DFT_SIZE, SOXR_LARGE_DFT_SIZE and SOXR_USE_SIMD/SIMD32/SIMD64. Pin or clear them in benchmarks and deployments.

## Known shortcomings

- Tier B on tap/SampleRateTap async/docs/COMPARISON.md, a shootout run by a competitor (Timothy Place; async/bench/compare/bench_compare.cpp, GCC 13.3 -O3, single thread, Ubuntu 24.04 packages, 'shared Xeon @ 2.10 GHz' with no model, so not A): 52.9 vs 4.8 MB/s stereo, 114.3 vs 5.2 mono, 12.9 vs 1.9 8-channel, 32.1 vs 1.6 VHQ against libsamplerate 0.2.2. The ratio tested is near unity (1 plus 200 ppm), not 44.1 to 48 kHz; HQ vs MEDIUM are matched (about 120 dB, 91.3% vs 90% bandwidth), while VHQ vs BEST trades a narrower band (91.3% vs 97%) for more rejection. soxr's own repo and SourceForge wiki carry no comparison. Licence LGPL-2.1-or-later.
- The int16 and int32 output paths carry a stale fe_test_invalid flag that corrupts samples (issue #11; PR #12 open since 2023-11; the float path is unaffected), and int16 dither is seeded with time(0), so output is non-deterministic (issue #8). Upstream CMake builds scalar on AArch64 (FindSIMD32 tries NEON only for '^arm'; the dofuuz fork claims over 2x from fixing it); the FFT-cache lock is a no-op without OpenMP; CMake 4 needs a minimum-version bump (issue #14); soxr_oneshot defaults to low quality. Latency 424-788 frames at HQ.

## Caveats and trade-offs

The numbers come from a competitor's comparison page (SampleRateTap COMPARISON.md, run 2026-09-25 with async/bench/compare/bench_compare.cpp), not from the soxr project; libsoxr's own repo has throughput tests of soxr alone (tests/throughput.c) and no comparison with libsamplerate, and its SourceForge wiki has none either. CPU model is only 'shared Xeon @ 2.10 GHz'; soxr 0.1.3 and libsamplerate 0.2.2 are Ubuntu 24.04 packages with unstated build flags. The throughput workload is a near-unity ratio (1 + 200 ppm), not 44.1/48 kHz conversion. Quality pairing: soxr HQ (20-bit precision, about 120 dB rejection, passband to 91.3% of Nyquist per soxr.h) vs libsamplerate MEDIUM (filter table 120.61 dB stop band, 90% bandwidth per its docs) is a fair match; soxr VHQ (28-bit, about 170 dB, passband 91.3%) vs libsamplerate BEST (154.67 dB, 97% bandwidth) gives soxr more rejection but a narrower preserved band (about 21.9 kHz vs 23.3 kHz at 48 kHz, derived), both flat past 20 kHz; the page's AES17-style THD+N test puts soxr VHQ and libsamplerate sinc_best both at the format ceiling (-143.8 vs -143.5 dB, 24-bit I/O). Supporting evidence at a real conversion ratio: the python-soxr README (Google Colab, CPU unspecified, through Python bindings) times 10 s of 48 kHz to 44.1 kHz at 10.8 ms (soxr HQ) vs 223 ms (samplerate sinc_medium) and 14.5 ms (VHQ) vs 794 ms (sinc_best). soxr's speed comes with large latency (424-788 frames at HQ in this test), so it suits offline or batch work, not 1-2 ms live paths. The GitHub repo mirrors SourceForge; both end at 2018-02-24 (0.1.3); the maintained patched fork dofuuz/soxr (bundled by python-soxr) fixes integer-output dithering and enables NEON on AArch64, neither of which affects these float x86 numbers.

Large algorithmic latency (424-788 frames, 8.8-16.4 ms at HQ; 433 frames at VHQ) because it processes in big SIMD batches, so unsuitable for low-latency live monitoring; the benchmark author says so. LGPL-2.1. Offers a libsamplerate-like header (soxr-lsr.h) but not a full emulation.

## Maintenance

Upstream has been abandoned since 0.1.3 (2018-02-24), but that release is still what Linux distributions ship, and the LGPL-2.1-or-later C sources build with CMake. For ARM64, CMake 4 or reproducible int16 output, use the maintained dofuuz/soxr fork (last commit 2026-06-27), which python-soxr bundles.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party measurement: the SampleRateTap author (a competitor, whose page states soxr beats his own library) benchmarks soxr 0.1.3 against libsamplerate 0.2.2 with public code async/bench/compare/bench_compare.cpp, GCC 13.3 -O3, median of 5; it falls short of A because the CPU is only 'shared Xeon @ 2.10 GHz' and the distribution packages' build flags are not stated. This matches the current merged record's B (the rendered prompt carried the superseded python-soxr record at C).
- **Verifier notes:** All four Mframes/s pairs match COMPARISON.md and the derived ratios check out; the harness code confirms single-thread soxr, float I/O and the near-unity ratio. License in the record should read LGPL-2.1-or-later (LICENCE text says 'version 2.1 ... or (at your option) any later version'). No known correctness bug behind the measured float path.
- **Fields the verifier corrected:** `baseline`, `license`, `workload`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/docs/COMPARISON.md>
  - <https://github.com/tap/SampleRateTap/tree/main/async/bench/compare>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/bench_compare.cpp>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/CMakeLists.txt>
  - <https://github.com/chirlu/soxr>
  - <https://github.com/chirlu/soxr/commits>
  - <https://github.com/chirlu/soxr/tree/master/tests>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/README>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/LICENCE>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/soxr.h>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/tests/README>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/tests/throughput-test>
  - <https://sourceforge.net/p/soxr/wiki/Home/>
  - <https://sourceforge.net/p/soxr/code/ci/master/log/>
  - <https://raw.githubusercontent.com/dofuuz/python-soxr/HEAD/README.md>
  - <https://github.com/dofuuz/soxr/commits>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/0.2.2/src/mid_qual_coeffs.h>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/0.2.2/src/high_qual_coeffs.h>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/HEAD/docs/api_misc.md>
- **Sources the enricher read:**
  - <https://github.com/chirlu/soxr>
  - <https://github.com/chirlu/soxr/tree/master/src>
  - <https://github.com/chirlu/soxr/issues>
  - <https://github.com/chirlu/soxr/issues/11>
  - <https://github.com/chirlu/soxr/issues/8>
  - <https://github.com/chirlu/soxr/pulls>
  - <https://github.com/chirlu/soxr/pull/12>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/README>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/LICENCE>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/INSTALL>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/NEWS>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/TODO>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/cmake/Modules/FindSIMD32.cmake>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/cmake/Modules/FindSIMD64.cmake>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/soxr.h>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/soxr.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/cr.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/cr.h>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/cr-core.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/cr32s.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/data-io.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/filter.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/fft4g_cache.h>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/ccrw2.h>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/fft4g32.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/pffft-wrap.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/pffft64s.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/pffft-avx.h>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/soxr-lsr.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/src/soxr-lsr.h>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/tests/throughput.c>
  - <https://raw.githubusercontent.com/chirlu/soxr/HEAD/tests/README>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/docs/COMPARISON.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/bench_compare.cpp>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dofuuz/python-soxr/HEAD/README.md>
  - <https://github.com/dofuuz/soxr>
  - <https://github.com/dofuuz/soxr/commits>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/chirlu/soxr`) · [data/wave10/enrich/raw/github_com_chirlu_soxr.json](../../../data/wave10/enrich/raw/github_com_chirlu_soxr.json) (enrichment confidence 0.8)

</details>
