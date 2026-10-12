# NonIntegerSRC (Holters-Parker resampler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `GPL-3.0` · 🔴 abandoned

> SSE Holters-Parker IIR resampler, timed 17-40x faster than libsamplerate SINC_FASTEST at far lower, unmatched quality.

| | |
|---|---|
| **Beats** | libsamplerate (SRC_SINC_FASTEST) |
| **Claimed result** | Speed factor of the Holters-Parker resampler over libsamplerate SRC_SINC_FASTEST, from doc/speed_chart.png: 48k to 96k 39.8x, 96k to 48k 16.9x, 44.1k to 48k 21.2x, 48k to 44.1k 21.8x (doc/writeup.md: '10-40x faster'). Not quality-matched: the HP resampler runs a 4th-order IIR filter, libsamplerate SINC_FASTEST is a 97 dB SNR / 80% bandwidth sinc converter. |
| **Workload** | One timed pass (std::chrono, no warm-up, no repeats) resampling a 1,000,000-sample 100 Hz float sine in 2048-sample blocks, mono, for four ratios (2.0, 0.5, 1.088, 0.919; the 44.1k/48k ratios are rounded), comparing the SSE-vectorised Holters-Parker multi-rate IIR resampler (src/HPResampler.h, src/src_utils/HPFilters.h) against libsamplerate SRC_SINC_FASTEST (src/LibSamplerRateSRC.h), harness src/src_test.cpp. |
| **Metric** | throughput |
| **Hardware** | Linux machine with an Intel i7 CPU, model not stated (doc/writeup.md); the author also reports comparable results on a Mac and close to 40x on Windows, without numbers. |
| **Compiler and flags** | Compiler and version not stated. Documented build is 'cmake -Bbuild; cmake --build build --config Release'; on a single-config Linux generator '--config Release' is ignored and neither the top-level CMakeLists.txt nor the current libsamplerate and libsndfile CMakeLists.txt set a default CMAKE_BUILD_TYPE, so the optimisation level of the measured build is unknown (possibly unoptimised). libsamplerate is built from the third_party/libsamplerate submodule with the same flags as the HP code. |
| **Adoption** | 38 stars, 4 forks |
| **Last commit** | 2021-07-12 |
| **Links** | [repository](https://github.com/jatinchowdhury18/NonIntegerSRC) · [benchmark](https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/doc/speed_chart.png) |

## Verdict

The only numbers are a spreadsheet screenshot (doc/speed_chart.png) of single std::chrono passes of src/src_test.cpp, with no warm-up or repeats, on an unnamed Intel i7 Linux machine with compiler and flags unrecorded. It shows the HP resampler 39.8x (48k to 96k), 16.9x (96k to 48k), 21.2x (44.1k to 48k) and 21.8x (48k to 44.1k) faster than libsamplerate 0.2.1 SRC_SINC_FASTEST, resampling a 1,000,000-sample mono 100 Hz sine in 2048-sample blocks. The documented build ('cmake -Bbuild; cmake --build build --config Release') applies no optimisation flags with a single-config Linux generator, because neither the top-level CMakeLists.txt nor the pinned libsamplerate 0.2.1 (aae58e2) or libsndfile 1.0.31 (949c891) sets a default CMAKE_BUILD_TYPE, so the published Linux ratios may come from -O0 builds of both sides (not recorded either way).

## Use it when

- Fixed-ratio mono float conversion on x86 (SSE2) inside a plugin or synth where CPU matters far more than fidelity, such as internal modulation paths, previews or effects that low-pass the signal anyway.
- Upsampling, where the filter cutoff at the input Nyquist does act as an anti-imaging filter (the 48k to 96k case is also the largest timed win, 39.8x).
- As a starting point for your own Holters-Parker resampler: the four-poles-per-SSE-register layout is the reusable idea, provided you fix the time units and cutoff (see gotchas) and measure quality yourself.
- Comparing SRC approaches: the harness (src/src_test.cpp) times libsamplerate, the HP resampler and Surge's Lanczos resampler on the same input, and src_sndfile converts WAV files for listening tests.

## Skip it when

- Any path where the output is listened to critically or distributed: the author's own plot (doc/HP_compare.png) shows spurious components up to about -47 dB against a smooth libsamplerate spectrum, and the writeup says the author was 'primarily interested in speed rather than quality'.
- Downsampling: the filter cutoff is fixed at the input Nyquist for every ratio, so 96k to 48k has no effective anti-aliasing filter below the 24 kHz output Nyquist.
- ARM or Apple Silicon builds: the code uses SSE2 intrinsics (emmintrin.h) with no NEON or scalar fallback.
- Variable-ratio, multichannel or library-style use: the ratio is fixed in prepare(), audio is mono, there is no build target for the resampler itself, and the repo has been inactive since 2021-07-12 with three unanswered issues.
- Projects that cannot accept GPL-3.0: the SSE helpers and Lanczos code come from the GPL-3.0 Surge Synthesizer.

## How it is fast

Instead of a windowed-sinc FIR evaluated at each output instant, the converter runs a 4th-order analog filter expanded into four complex one-pole sections whose state is updated once per output sample, with all four sections packed into one SSE register (SSEComplex, from Surge), so a 4th-order filter costs about the same as a first-order one. Each input sample adds only a complex multiply-accumulate of its step (y - y_old) weighted by a per-sample coefficient that is advanced by a precomputed complex rotation (calcG), and sin/cos come from polynomial approximations (FastMath::fastsinSSE/fastcosSSE). libsamplerate SINC_FASTEST, by contrast, evaluates a sinc filter rated at 97 dB SNR and 80% bandwidth, so most of the gap comes from doing far less filtering work.

## Compared with alternatives

Pick libsoxr (about 11x libsamplerate MEDIUM at the \~120 dB tier), r8brain-free-src, LibFResample, SampleRateTap or zita-resampler whenever the output is audible, since their speedups over libsamplerate are quality-matched. NonIntegerSRC only makes sense when a crude 4th-order IIR result is acceptable for minimum x86 CPU, or as research code on the Holters-Parker approach.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | None for the HP resampler headers (SSE2 intrinsics, &lt;complex&gt;, &lt;functional&gt;); the benchmark harness links libsamplerate 0.2.1 (submodule aae58e2) and the WAV tool links libsndfile 1.0.31 (submodule 949c891) |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17 in CMakeLists.txt); CMake 3.1+ for the harness |
| **Platforms** | x86 / x86-64 with SSE2 only |
| **Thread safety** | Not documented; all state lives in the HPResampler instance (filter banks, tn, y_old) with no globals, so one instance per stream or thread is the safe use. |
| **Drop-in for the baseline** | no |

## Gotchas

- From code reading (not executed): HPResampler keeps its sub-sample clock tn and the per-step advance in seconds (Ts = 1/fs, Ts_out = ratio/fs, about 1e-5), but OutputFilterBank::set_time and set_delta use them as exponents of a per-output-sample pole (pow(pole, 1 - tn); fast_complex_pow also keeps only the pole's angle). The timing-dependent weight therefore stays within about 1e-4 of constant, so every input step gets almost the same weight wherever it falls between output samples, and the output behaves like a filtered sample-and-hold rather than a Holters-Parker resampler. That is consistent with the spurs in doc/HP_compare.png. chowdsp_utils' BBDDelayLine uses the same seconds-based convention in its default mode and normalises tn by Ts only in its 'ALIEN' mode. The operation count does not depend on this, so the speed ratios are not inflated by it, but the measured code does not deliver the method's intended quality.
- process() does not bounds-check its inner loop: for non-integer downsampling (the 0.919 case) it can read input[num_samples], one sample past the block, and the next call then consumes that sample again. It also writes outputs with no capacity argument, so the caller must size the output for about n\*ratio+1 samples.
- The filter cutoff is hard-wired to sample_rate\*0.5 (the input Nyquist) for both directions, and the 44.1k/48k ratios in the harness are rounded to 1.088 and 0.919.
- Only the output-filter ('rectangular') variant is compiled; the input-filter ('Dirac') variant sits behind #if 0, and issue #2 (2024, unanswered) asks whether cascading both would reduce aliasing. prepare() still allocates both filter banks and an unused 'middle' buffer.

## Known shortcomings

- C++17 plus SSE. Chart numbers (39.8/16.9/21.2/21.8x) come from one timed pass of src/src_test.cpp on a 1M-sample 100 Hz sine against libsamplerate SRC_SINC_FASTEST (97 dB SNR, 80% bandwidth) built in-tree; not quality-matched: the Holters-Parker side is a single 4th-order IIR (JUNO-60 BBD poles) whose own doc/HP_compare.png shows spurs at about -47 dB, and the cutoff sits at the input Nyquist so a 96k to 48k conversion is barely anti-aliased. Machine 'Intel i7' only (doc/writeup.md), no compiler, and the documented cmake build sets no build type.
- Usability set to reference (retier-14): by code reading, tn/delta in seconds is used as the exponent of a per-sample pole, so the sub-sample weight is near constant (within 1e-4) and the output behaves as a filtered sample-and-hold, matching the spurs in the repo's HP_compare.png; the timed code is not a working Holters-Parker resampler although the operation count and ratios are unaffected (the chowdsp BBDDelayLine default mode shares the convention; its ALIEN mode normalises by Ts). process() over-reads input[num_samples] at the 0.919 ratio; the pinned libsamplerate 0.2.1 and libsndfile 1.0.31 builds set no CMAKE_BUILD_TYPE, so the documented Linux build is probably -O0 on both sides.

## Caveats and trade-offs

The two sides do different work. The HP resampler uses one 4th-order analog filter (the JUNO-60 bucket-brigade filter poles and zeros from Holters and Parker's DAFx 2018 paper, per src/src_utils/HPFilters.h; the README and writeup call it a 4th-order Butterworth), while libsamplerate SRC_SINC_FASTEST is documented at 97 dB SNR and 80% bandwidth (docs/api_misc.md). The author's own quality plot doc/HP_compare.png shows HP output with spurious components up to about -47 dB against a roughly -10 dB fundamental, where libsamplerate's spectrum stays smooth (read from the plot), and doc/writeup.md says 'I'm primarily interested in speed rather than quality'. In src/HPResampler.h the filter cutoff is set to the input Nyquist (sample_rate\*0.5) for every ratio, so for 96k to 48k the anti-aliasing cutoff (48 kHz) sits above the 24 kHz output Nyquist (derived from code reading). Timing is a single pass on a 100 Hz sine with no repeats; quality stats are computed in src_test.cpp but never printed. Compiler, flags and CPU model are not stated. The code uses SSE intrinsics (x86 only) and code from the GPL-3.0 Surge Synthesizer. Last commit 2021-07-12. [retier] Likely correctness bug (code reading, not run): tn/delta in seconds is used as the exponent of a per-sample pole, so the sub-sample weight is near constant and the output acts as a filtered sample-and-hold (visible as spurs in HP_compare.png); the timing ratios are not inflated by this, but the timed code is not a working Holters-Parker resampler. process() over-reads input[num_samples] at ratio 0.919. The pinned libsamplerate and libsndfile builds set no CMAKE_BUILD_TYPE, so both sides were probably built at -O0.

Holters-Parker resampler uses SSE-vectorised 4th-order IIR filters (from a DAFx-2018 paper) rather than a windowed-sinc FIR, so quality (aliasing and passband) differs from libsamplerate; the Lanczos resampler and SSE complex classes are borrowed from Surge Synthesizer. GPLv3 copyleft.

## Maintenance

Abandoned research code (15 commits, last 2021-07-12, 38 stars, 3 open unanswered issues) under GPL-3.0 with Surge-derived SSE code. It is small enough to copy, but treat it as a sketch: fix the time units, cutoff and bounds check and measure quality before using it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party only: doc/speed_chart.png gives speed factors 39.81, 16.92, 21.17 and 21.85 over libsamplerate SRC_SINC_FASTEST, produced by the public harness src/src_test.cpp, but compiler, flags and CPU model are not stated (doc/writeup.md says only 'Linux system running an Intel i7 CPU'), and there is no raw output. Not A without compiler, flags and CPU model.
- **Verifier notes:** The chart numbers match the record. The 10-40x figure is also in the in-repo doc/writeup.md, so the record's note that it appears only in a blocked blog is wrong. The measured code does much less filtering than the baseline (a 4th-order IIR against a 97 dB sinc converter), so this is a speed-for-quality trade, not like-for-like work. baseline_in_list is set to false because libsamplerate is not among the video-audio baselines (FFmpeg components, x264/x265, Opus). verify.py does not apply 'language' from corrections, so record it as a decision override.
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`, `usability`
- **Pages the verifier opened:**
  - <https://github.com/jatinchowdhury18/NonIntegerSRC>
  - <https://github.com/jatinchowdhury18/NonIntegerSRC/commits>
  - <https://github.com/jatinchowdhury18/NonIntegerSRC/tree/main/src>
  - <https://github.com/jatinchowdhury18/NonIntegerSRC/tree/main/doc>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/README.md>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/doc/speed_chart.png>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/doc/writeup.md>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/doc/HP_compare.png>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/doc/BBD_Filters.png>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_test.cpp>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/HPResampler.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/LibSamplerRateSRC.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/utils.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_utils/HPFilters.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/tests.py>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/master/docs/api_misc.md>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libsndfile/libsndfile/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/jatinchowdhury18/NonIntegerSRC>
  - <https://github.com/jatinchowdhury18/NonIntegerSRC/tree/main/third_party>
  - <https://github.com/jatinchowdhury18/NonIntegerSRC/issues>
  - <https://github.com/jatinchowdhury18/NonIntegerSRC/issues/2>
  - <https://github.com/jatinchowdhury18/NonIntegerSRC/issues/4>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/README.md>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/doc/writeup.md>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/doc/speed_chart.png>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/doc/HP_compare.png>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_test.cpp>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/HPResampler.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/LibSamplerRateSRC.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/LanczosSRC.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/BaseSRC.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/utils.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_sndfile.cpp>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_utils/HPFilters.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_utils/SSEComplex.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_utils/FastMath.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/tests.py>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/aae58e2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libsndfile/libsndfile/949c891/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Chowdhury-DSP/chowdsp_utils/master/modules/dsp/chowdsp_dsp_utils/Delay/BBD/chowdsp_BBDFilterBank.h>
  - <https://raw.githubusercontent.com/Chowdhury-DSP/chowdsp_utils/master/modules/dsp/chowdsp_dsp_utils/Delay/BBD/chowdsp_BBDDelayLine.h>
  - <https://raw.githubusercontent.com/surge-synthesizer/surge/main/src/common/dsp/effects/chowdsp/bbd_utils/BBDFilterBank.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/jatinchowdhury18/nonintegersrc`) · [data/wave10/enrich/raw/github_com_jatinchowdhury18_nonintegersrc.json](../../../data/wave10/enrich/raw/github_com_jatinchowdhury18_nonintegersrc.json) (enrichment confidence 0.7)

</details>
