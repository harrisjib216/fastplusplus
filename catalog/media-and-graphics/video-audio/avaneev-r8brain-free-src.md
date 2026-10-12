# r8brain-free-src

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only MIT C++ audio sample-rate converter; 3.4x to 8.8x libsamplerate's stereo throughput in a third-party near-unity benchmark.

| | |
|---|---|
| **Beats** | libsamplerate 0.2.2 (Secret Rabbit Code, MEDIUM and BEST converters) |
| **Claimed result** | Third-party table (Mframes/s, higher is better), \~120 dB tier: r8brain ReqAtten 120 dB (default 2 % band) mono 35.4 vs libsamplerate MEDIUM 5.2 (about 6.8x, derived from page data), stereo 16.5 vs 4.8 (about 3.4x, derived), 8-ch 4.1 vs 1.9 (about 2.2x, derived); with the 8 % band, stereo 17.9 (about 3.7x, derived). \~140 dB tier, stereo: r8brain at CDSPResampler16 settings (136.45 dB) 18.4 vs libsamplerate BEST 1.6 (about 11.5x, derived), at CDSPResampler24 settings (180.15 dB) 14.1 (about 8.8x, derived). Embedded steady-state instructions per stereo output frame (lower is better), r8brain 120 dB default band vs libsamplerate MEDIUM: Cortex-M55 1,002 vs 2,203 (about 2.2x fewer, derived), Cortex-M33 30,004 vs 49,206 (about 1.6x, derived), Hexagon 6,060 vs 9,025 (about 1.5x, derived). The r8brain README itself states only an absolute rate (38\*n_cores Mrops, 56\*n_cores with Intel IPP, CDSPResampler24, 44100 to 96000, Ryzen 3700X) and names no baseline. |
| **Workload** | Streaming conversion of a float 997 Hz sine at one fixed near-unity ratio (48000 to 48000\*(1+200 ppm) Hz) in 128-frame blocks, million output frames/s, median of 5 (SampleRateTap async/bench/compare/bench_compare.cpp). r8brain runs one r8b::CDSPResampler per channel, linear phase, with ReqAtten 120 dB and a 2 % transition band (plus an 8 % band row), and with the CDSPResampler16/24 preset attenuations (136.45 and 180.15 dB, 2 % band) for the higher tier; the float-to-double (de)interleave is inside the timed loop. libsamplerate runs SRC_SINC_MEDIUM_QUALITY and SRC_SINC_BEST_QUALITY via src_process. Tiers are paired by vendor-stated stopband. The same page also gives QEMU TCG instruction counts per stereo output frame on Cortex-M55, Cortex-M33 and Hexagon. |
| **Metric** | throughput |
| **Hardware** | shared Xeon @ 2.10 GHz (exact model not stated), median of 5, run 2026-09-25 |
| **Compiler and flags** | Benchmark harness built with GCC 13.3 -O3 (CMake Release); r8brain at the pinned commit (version 7.5) in stock configuration with the Ooura FFT; libsamplerate 0.2.2 is the Ubuntu 24.04 package |
| **Adoption** | 743 stars, 84 forks; README lists users including REAPER, Audirvana, Red Dead Redemption 2 and OpenMPT |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/avaneev/r8brain-free-src) · [benchmark](https://github.com/tap/SampleRateTap/blob/main/async/docs/COMPARISON.md) |

## Verdict

SampleRateTap's COMPARISON.md streamed a float 997 Hz sine at 48000 to 48000\*(1+200 ppm) in 128-frame blocks on an unnamed shared Xeon at 2.10 GHz, median of 5. The harness was built with GCC 13.3 -O3 and no -march flag, against r8brain 7.5 (commit 9e73d2dd, Ooura FFT) and Ubuntu 24.04's libsamplerate 0.2.2. Stereo results: r8brain 16.5 (2 % band) and 17.9 (8 % band) vs MEDIUM 4.8 Mframes/s; 14.1 at 180.15 dB vs BEST 1.6. On settings, libsamplerate's own coefficient headers give MEDIUM a 120.61 dB stop band with its -3 dB point at 90.5 % of Nyquist (about a 9.5 % band in r8brain's terms), and BEST 154.67 dB at 96.1 % (about 3.9 %). So the 8 % row (3.7x) is the closest MEDIUM match, the 2 % rows filter more steeply than libsamplerate, the 180.15 dB row (8.8x) beats BEST on both axes, and the 136.45 dB row (11.5x) has about 18 dB less stop band than BEST's design, not the 144 dB the harness comment assumes. A second third-party data point, cmicali/vibe PR #84 (merged 2026-09-28), has r8brain CDSPResampler24 (1 % band, PFFFT double, -O3) using 0.06-0.18 % of one core against 0.9-3.5 % for Apple AudioConverter at Mastering/Max quality on an unnamed Apple silicon Mac, and 0.54-0.56 % vs 3.27-3.39 % on iPhone 17 Pro for 44.1 to 48 kHz.

## Use it when

- Offline or file-based conversion at arbitrary ratios (44.1k to 48k, to and from DSD-class rates) where you want linear phase and a 120-180 dB stop band. REAPER, OpenMPT and Audirvana ship it.
- Replacing libsamplerate SINC_MEDIUM or SINC_BEST in a desktop pipeline that can absorb 4-37 ms of filter delay: 3.4-3.7x MEDIUM's stereo throughput and 8.8x BEST's at a stricter 180 dB setting in the third-party table.
- Projects that need a permissive (MIT), header-only resampler with no build step or external dependency.
- Power-of-2 up- or downsampling (2x, 4x, 3x2x, ...), which uses the faster half-band path automatically.
- Resampling of impulse responses or general 1D time series through oneshot() with relaxed attenuation.

## Skip it when

- Low-latency live paths: in the SampleRateTap measurement the default 2 % band holds back 789 input frames (16.4 ms at 48 kHz), the 140-180 dB presets 1,700-1,782 frames (35-37 ms), and the passband-matched 8 % band still 200 frames (4.2 ms). libsamplerate MEDIUM holds back 46 frames.
- Maximum host throughput when LGPL is acceptable: soxr HQ/VHQ is 1.7-3.2x faster than r8brain in every row of the same table.
- FPU-less or FP64-less microcontrollers: the code is double precision only with no fixed-point path, and costs 30,004 instructions per stereo frame on Cortex-M33 in the same report.
- Varispeed or continuously drifting ratios (ASRC): rates are fixed at construction and there is no ratio setter, so you would rebuild the resampler or use an ASRC such as SampleRateTap.
- Interleaved float multichannel callers that cannot afford a per-channel deinterleave and float-to-double conversion around every call.

## How it is fast

The input is first upsampled 2x by single-block overlap-save FFT convolution with a Kaiser-windowed low-pass (Ooura FFT by default, Intel IPP or PFFFT optional), so a long, steep filter costs roughly log-time per sample. A bank of short (8-30 tap) polynomial-interpolated sinc fractional-delay filters then produces the target rate with SSE2/NEON dot products. Power-of-2 and 3x ratios use dedicated half-band stages, and whole-number stepping is used when the GCD of the rates allows. libsamplerate instead runs a time-domain sinc with per-tap coefficient interpolation: about 91 taps per output sample per channel for MEDIUM and about 286 for BEST (half length divided by increment in its coefficient tables). Designed filters and FFT setups sit in a process-wide cache, so creating more resamplers is cheap.

## Compared with alternatives

Pick r8brain over libsoxr when you need an MIT, header-only library and can give up about 2-3x of soxr's throughput. Pick it over SampleRateTap when you need real rate conversion at arbitrary ratios, not drift correction around one nominal rate, and can accept 33-45x SampleRateTap's filter delay. Over zita-resampler, it is the permissive-license option.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C++ standard library; optional Intel IPP, or the bundled PFFFT / PFFFT-double .c file compiled into the build |
| **Minimum toolchain** | C++11 for the std::mutex path (pre-C++11 builds use pthread or Windows.h); tested by the author with GCC, Clang, MSVC and Intel C++ |
| **Platforms** | any platform with a 64-bit IEEE double; SSE2 and NEON intrinsic paths; 32- and 64-bit Windows, macOS, Linux |
| **Thread safety** | README says the code is thread-safe with one resampler object per channel or stream; the shared filter and filter-bank caches are guarded by std::mutex during construction |
| **Drop-in for the baseline** | no |

## Gotchas

- process() returns a pointer into the resampler's own buffer and a count that varies per call; early calls return nothing while the filter delay is consumed, so real-time callers need a pull loop around getInputRequiredForOutput().
- The input length must not exceed the aMaxInLen given at construction. This is checked only by R8BASSERT, which r8bconf.h compiles to a no-op by default.
- Issue #33 (2026-10-02) reports that the 7.6 filter-design speedups slightly lowered quality against 7.5 in the Hydrogenaudio SRC test. It was closed with no comment and no follow-up commit visible, and the benchmarked build was 7.5.
- The single-precision R8B_PFFFT back end limits precision to about 24-bit, and the README advises against it for critical work. Use R8B_PFFFT_DOUBLE or IPP for speed without that loss. R8B_EXTFFT trades more latency for speed. Bare-metal builds need a mutex stand-in for the filter cache.

## Known shortcomings

- Tier B on tap/SampleRateTap async/docs/COMPARISON.md (a competitor's shootout; bench_compare.cpp matches the stated settings: linear phase, 2% band, ReqAtten 120/136.45/180.15 dB; GCC 13.3 -O3, 'shared Xeon @ 2.10 GHz' with no CPU model): stereo 16.5 vs libsamplerate MEDIUM 4.8 MB/s, and 18.4/14.1 vs BEST 1.6 at about 140 dB. Quality was paired only by vendor-stated stop-band (the 136.45 dB row sits below BEST's about 144 dB; the 180.15 dB row above it is still 8.8x); one near-unity ratio only; r8brain latency is 16-37 ms against 1-3 ms, and libsoxr is faster than r8brain. The repo itself publishes no comparison; the 7.6 release speeds construction only.
- The SampleRateTap comparison is not quality-matched at the headline: from libsamplerate's coefficient headers, SINC_MEDIUM is 120.61 dB stop band with -3 dB at 90.5% of Nyquist and SINC_BEST 154.67 dB at 96.1% (not the 144 dB the harness comment states), so the 8% transition-band row (3.7x) best matches MEDIUM, the 180.15 dB row (8.8x) beats BEST on both axes, and the 136.45 dB row (11.5x) has about 18 dB less stop band than BEST; quote 8.8x, not 11.5x. CPU model unstated; both libraries built without -march. Issue #33 (2026-10-02) reports version 7.6 lowering quality versus the benchmarked 7.5 (Hydrogenaudio SRC test), closed without comment or fix commit.

## Caveats and trade-offs

Numbers come from a competitor's comparison page (SampleRateTap), not from the r8brain project; r8brain's README publishes no comparison and asks that competing libraries be tuned to linear phase and similar stop-band. The same table shows soxr HQ/VHQ about 1.7-3.2x faster than r8brain in every row (derived from page data), so r8brain beats libsamplerate but is not the fastest resampler measured. Large latency trade-off: r8brain's FFT block convolution withholds 789 input frames (16.4 ms) at the 120 dB default band and 1,700-1,782 frames (35-37 ms) at the \~140 dB tier, against 46 frames (0.96 ms) for libsamplerate MEDIUM and 143 frames (3.0 ms) for BEST; the passband-matched 8 % band still costs 200 frames (4.2 ms). Tier pairing is by vendor-stated stopband; the CDSPResampler16-setting row (136.45 dB) has a lower stopband than libsamplerate BEST (\~144 dB), while the CDSPResampler24-setting row (180.15 dB, still 8.8x) exceeds it; r8brain's 2 % transition band is narrower than libsamplerate MEDIUM's, so the 120 dB row is not doing less filtering. Only one near-unity ratio was timed; the README warns performance varies greatly with ratio. CPU model only 'shared Xeon @ 2.10 GHz'. The benchmark used r8brain 7.5 with the Ooura FFT; version 7.6 (2026-09-30) speeds up filter calculation (a one-time construction cost), which does not change the steady-state throughput measured here. On the Cortex-M builds r8brain's filter-cache std::mutex was replaced by a no-op lock. Ratios are derived from page data.

Linear-phase FFT block convolution, so large latency (789 frames / 16.4 ms at the default 2% transition band, 1,700-1,782 frames at the 140 dB tier). Mono per instance, double precision I/O. Header-only, MIT. Optional Intel IPP or PFFFT FFT back ends for extra speed.

## Maintenance

Actively maintained: versions 7.2-7.6 shipped between July and September 2026 and no issues are open. MIT, header-only and widely shipped, so it is easy to vendor; pin 7.5 if issue #33's quality report matters to you.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent measurement by a competing project (SampleRateTap), whose harness async/bench/compare/bench_compare.cpp (Google Benchmark) is public and whose COMPARISON.md states GCC 13.3 -O3 (CMake Release), libsamplerate 0.2.2 and the r8brain 7.5 commit pin, but the CPU is only 'shared Xeon @ 2.10 GHz' with no model, so it falls short of A. r8brain's own repo publishes no comparison against libsamplerate or any other resampler (absolute Mrops only).
- **Verifier notes:** All Mframes/s numbers match the r8brain and libsamplerate rows of COMPARISON.md and the harness code matches the stated settings (ReqAtten 120/136.45/180.15, fprLinearPhase, SRC_SINC_MEDIUM/BEST_QUALITY). The QEMU instruction-count table has public code, named compilers (arm-none-eabi-gcc 13.2.1, hexagon-clang 19.1.5, -O3) and named cores, but counts instructions rather than time, so I kept B. Metadata confirmed: MIT, not a fork, last commit 2026-09-30 (Version 7.6).
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** Third-party in-app comparison (cmicali/vibe PR #84, merged 2026-09-28): r8brain 0.06-0.18% of one core versus Apple AudioConverter 0.9-3.5% on an unnamed Apple silicon Mac; iPhone 17 Pro 0.54-0.56% versus 3.27-3.39%.
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/docs/COMPARISON.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/bench_compare.cpp>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/cmake/r8brain.cmake>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/README.md>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/LICENSE>
  - <https://github.com/avaneev/r8brain-free-src>
  - <https://github.com/avaneev/r8brain-free-src/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/README.md>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/CDSPResampler.h>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/CDSPBlockConvolver.h>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/CDSPFracInterpolator.h>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/CDSPFIRFilter.h>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/r8bbase.h>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/r8bconf.h>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/CDSPHBUpsampler.h>
  - <https://raw.githubusercontent.com/avaneev/r8brain-free-src/HEAD/CDSPHBDownsampler.h>
  - <https://github.com/avaneev/r8brain-free-src>
  - <https://github.com/avaneev/r8brain-free-src/commits>
  - <https://github.com/avaneev/r8brain-free-src/issues?q=is%3Aissue>
  - <https://github.com/avaneev/r8brain-free-src/issues/33>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/docs/COMPARISON.md>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/bench_compare.cpp>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/compare/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/cmake/r8brain.cmake>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tap/SampleRateTap/HEAD/async/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/master/src/mid_qual_coeffs.h>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/master/src/high_qual_coeffs.h>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/master/src/src_sinc.c>
  - <https://github.com/cmicali/vibe/pull/84>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/avaneev/r8brain-free-src`) · [data/wave10/enrich/raw/github_com_avaneev_r8brain_free_src.json](../../../data/wave10/enrich/raw/github_com_avaneev_r8brain_free_src.json) (enrichment confidence 0.75)

</details>
