# sst-basic-blocks LanczosResampler (Surge)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT OR GPL-3.0-or-later (LanczosResampler.h is dual licensed; the rest of sst-basic-blocks is GPL-3.0-or-later)` · 🟢 active

> Surge's 8-tap table-driven SSE Lanczos stereo resampler for real-time audio; claimed about 2x faster than libsamplerate's fastest sinc.

| | |
|---|---|
| **Beats** | libsamplerate sinc resampling (SRC_SINC_FASTEST in the NonIntegerSRC harness); the issue says only 'Sinc interpolation' |
| **Claimed result** | Issue 4 on NonIntegerSRC (opened 2026-05-18): 'I found out the Lanczos interpolation was faster by a factor of two on my machine'; no timings given. |
| **Workload** | Third-party run of the NonIntegerSRC src_test harness: resampling a 1,000,000-sample 100 Hz sine at 48k to 96k, 96k to 48k, 44.1k to 48k and 48k to 44.1k in 2048-sample blocks, wall-clock timed with std::chrono, comparing libsamplerate, a Holters-Parker resampler and Surge's Lanczos resampler. |
| **Metric** | throughput |
| **Adoption** | 17 stars; described in its README as the bottom of the stack of the Surge libraries |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/surge-synthesizer/sst-basic-blocks) · [benchmark](https://github.com/jatinchowdhury18/NonIntegerSRC/issues/4) |

## Verdict

The only figure is an unanswered user question (NonIntegerSRC issue 4, 2026-05-18) saying Lanczos ran about 2x faster than 'Sinc' (the harness's libsamplerate SRC_SINC_FASTEST, mono) on an unnamed machine, with no timings, compiler or flags. The harness times a 2021 mono Surge copy (src/src_utils/LanczosResampler.h), not this header, and that copy is buggy: its table has 8,192 rows but is indexed up to 8,192, so every exactly integer read position reads past the array. That is every output for 96k to 48k (dPhaseO = 2.0) and every other output for 48k to 96k (dPhaseO = 0.5). The harness computes but never prints error statistics, so the wrong output went unnoticed (the current sst-basic-blocks header sizes the table at tableObs + 1 and is correct).

## Use it when

- Real-time stereo audio in a plugin or synth (JUCE, iPlug-style code) that needs variable or non-integer rate conversion, for example host rate to a fixed 48 kHz engine rate, with only a few samples of latency (it needs A + 1 = 5 input frames ahead of the read point).
- Upsampling, or ratios close to 1 (44.1k and 48k), where an 8-tap kernel is acceptable and anti-aliasing matters little.
- Code already inside the Surge, Shortcircuit or sst-\* stack, where setup.h and SIMDe are already present.
- Non-GPL projects that need a small permissive resampler: this header is dual-licensed MIT/GPL-3.0, unlike the rest of the repo.

## Skip it when

- Downsampling material with content above the output Nyquist (96k to 48k, 48k to 44.1k): the kernel is not widened with the ratio, so there is no anti-aliasing low-pass and energy between the two Nyquist frequencies aliases. libsoxr, r8brain-free-src or libsamplerate's sinc modes filter it.
- Mastering or offline conversion where measured SNR or passband specs matter: no quality figures are published, and the unit tests only bound the error on a slow sine (|d| &lt; 0.025).
- Mono, multichannel (more than 2), double-precision or integer audio: the class is hard-wired to two float channels.
- Callers that push more than about 4,000 frames before reading: the 4096-frame ring buffer overwrites unread input without any check.
- Choosing on the 2x speed claim alone: no reproducible benchmark of this header exists (see verified_claims_summary).

## How it is fast

It is Lanczos interpolation with A = 4, so each output frame is an 8-tap dot product. The windowed-sinc kernel is precomputed into a static table of 8,193 fractional phases by 8 taps, plus a table of deltas for linear interpolation between phases, so no sin() is evaluated at run time. Each read loads two 4-wide coefficient vectors, blends them with the deltas, multiplies them against two unaligned SSE loads per channel and finishes with a horizontal sum. The stereo pair shares one coefficient computation, and the ring buffer is stored twice so reads never wrap. libsamplerate's SRC_SINC_FASTEST instead convolves about 39 taps per output (half length 2,463 at increment 128, derived from src_sinc.c and fastest_coeffs.h) and widens the filter by 1/ratio when downsampling, so much of the speed gap comes from doing less filtering.

## Compared with alternatives

Pick it over libsoxr, r8brain-free-src or LibFResample when you need a tiny MIT-licensable, push/pull, low-latency stereo interpolator inside a real-time synth and can accept 8-tap quality. Pick those siblings, or NonIntegerSRC's Holters-Parker resampler (17-40x over SRC_SINC_FASTEST in its own chart), when you need band-limited downsampling or published speed and quality numbers.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | sst/basic-blocks/simd/setup.h and mechanics/simd-ops.h (GPL-3.0-or-later); SIMDe on non-x86 targets (without the simde CMake target the build is x86-64 only). For MIT use, copy the header, drop both includes, map SIMD_MM(x) to _mm_x and replace sum_ps_to_float with a horizontal add. |
| **Minimum toolchain** | C++20 (setup.h static_asserts __cplusplus &gt;= 202002L); on MSVC, needs _USE_MATH_DEFINES for M_PI (the CMake target sets it on WIN32). A stripped MIT copy's minimum standard is not documented. |
| **Platforms** | x86-64 (SSE2 native); arm64 and Windows arm64ec through SIMDe |
| **Thread safety** | Not documented. From the code, an instance has mutable state and is single-threaded; the shared static coefficient tables are filled lazily in the constructor behind a plain bool, so constructing the first instance of a given blockSize on two threads at once is a data race. |
| **Drop-in for the baseline** | no |

## Gotchas

- The tables are static per template instantiation: each distinct blockSize carries two 8,193 x 8 float tables (about 512 KiB, derived from the declarations), and each instance holds a 64 KiB stereo ring buffer. The header's own 'Fixme: Make this static and shared' notes this.
- populateNextBlockSize, populateNextBlockSizeOS and the Lin/ZOH variants do no range checks ('dangerous but efficient'); call inputsRequiredToGenerateOutputs first, and note that its source comment still reads 'Check this calculation'.
- Bug history: #63 (2023-09) fixed a wrapped derivative table that caused occasional clicks on 44.1/48 round trips (found at iPlug); #83 (2024-01) fixed a memset that left the right channel's buffer uninitialised; #148 (2024-12) fixed an index error in a then-unused function. Copies of the code taken before late 2023, such as the 2021 copy vendored in NonIntegerSRC, may still carry the first bug.
- The read is centred one sample behind the newest pushed frame, so there is a fixed latency of a few samples; phases are doubles that callers must renormalize (renormalizePhases) on long runs.

## Known shortcomings

- Tier D: the only number is a bare 'faster by a factor of two on my machine' in an unanswered user question (jatinchowdhury18/NonIntegerSRC issue 4) with no timings, CPU, compiler or flags and an unnamed 'Sinc' comparator; that harness times an older vendored mono Surge LanczosResampler copy, not the sst-basic-blocks header, and its CMakeLists sets no optimization flags. Lanczos A=4 (8 taps) is lower quality than libsamplerate's sinc converters, so the comparison is not quality-matched.
- Enricher (e122, 2026-10-05): bug behind the 'factor of two' remark: the timed copy (NonIntegerSRC src/src_utils/LanczosResampler.h) has an 8192-row table indexed up to tidx = 8192, an out-of-bounds read at every integer read position, which is every output sample at 96k to 48k (dPhaseO 2.0) and half at 48k to 96k; calc_stats was never printed, so it went unnoticed. That copy also carries the wrapped-DX bug that sst fixed in #63 (2023-09, 'occasional clicks'); the current sst header is correct (tableObs+1 rows). Not like for like: Lanczos with 8 taps and a kernel not widened when downsampling (no anti-aliasing) against SRC_SINC_FASTEST's roughly 39 taps scaled by 1/ratio (derived from src_sinc.c and fastest_coeffs.h). Requires C++20; static tables of about 512 KiB per blockSize; lazy table init behind a plain bool is a data race. D stands.

## Caveats and trade-offs

Only evidence is an unanswered user question in another repository (jatinchowdhury18/NonIntegerSRC issue 4, opened 2026-05-18, no replies): 'the Lanczos interpolation was faster by a factor of two on my machine', with no CPU, compiler, flags, timings or library versions, and the issue does not say whether the 'Sinc' comparator was libsamplerate (SRC_SINC_FASTEST, the harness's sinc option) or the Holters-Parker resampler. The harness (src/src_test.cpp) wall-clocks one pass over a 1,000,000-sample sine per conversion with std::chrono::high_resolution_clock, one run, no warm-up. It times NonIntegerSRC's vendored 2021 Surge LanczosResampler (src/src_utils/LanczosResampler.h, mono, SSE intrinsics), not sst-basic-blocks' current header (include/sst/basic-blocks/dsp/LanczosResampler.h, templated on block size, stereo, SIMD via sst simd-ops); the libsamplerate wrapper (src/LibSamplerRateSRC.h) runs one channel. CMakeLists.txt sets no CMAKE_BUILD_TYPE or optimization flags and the README builds with plain 'cmake -Bbuild', so a single-config Linux build may be unoptimized. The work differs in quality: the Lanczos kernel is A=4 (8 taps, table-interpolated), far shorter than libsamplerate's band-limited sinc filters, so a 2x speed gap at lower filter quality is not a like-for-like win. The NonIntegerSRC README's own chart reports its Holters-Parker resampler 17-40x faster than libsamplerate, far above the Lanczos 2x. No libsamplerate or r8brain comparison and no benchmark exist in sst-basic-blocks itself. A snippet 'Lanczos 4.5x slower than sinc_best, 2x faster than sinc_fastest' traces to obspy issue 1213 (2015) about ObsPy's own Lanczos against scikits.samplerate, unrelated to Surge, and is not used. License: LanczosResampler.h is dual GPL-3.0/MIT per its header and README, but it includes sst/basic-blocks/simd/setup.h and mechanics/simd-ops.h, which are GPL-3.0-or-later only, so MIT reuse needs those includes and the sum_ps_to_float call replaced (the header says as much).

Small-window Lanczos (A=4, 8 taps) with a 8192-entry interpolated coefficient table and SSE intrinsics, built for 48 kHz to variable-rate use; the header needs sst simd setup and a sum_ps_to_float reduction (or hadd) when copied. Filter quality versus long sinc kernels is not measured in the evidence. Only the three listed headers are MIT; everything else needs GPL-3.0.

## Maintenance

Actively maintained as the bottom layer of the Surge libraries (last commit 2026-09-27, 10 commits to this header, counting the April 2023 move from Surge); the header is copyable under MIT once the GPL simd includes are replaced, but it has no benchmark of its own.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now D.
- **Tier reason:** The only figure is a bare 'faster by a factor of two on my machine' in an unanswered user question (NonIntegerSRC issue 4), with no timings, CPU, compiler or flags and an unnamed 'Sinc' comparator; the harness it refers to (NonIntegerSRC src/src_test.cpp) times an older vendored mono Surge copy (src/src_utils/LanczosResampler.h), not the sst-basic-blocks header, and its CMakeLists.txt sets no build type or optimization flags. No number with a stated setup is reachable, so D.
- **Verifier notes:** Downgraded C to D per batch guidance: no reachable number with setup. Metadata checked: GPL-3.0 sidebar with three dual-licensed headers, 17 stars, not a fork, last commit 2026-09-27 (active). The entry is notable as the Surge XT building-block library, so not a not-notable reject.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** none (bare user remark); none (bare user remark on buggy vendored copy)
- **Pages the verifier opened:**
  - <https://github.com/jatinchowdhury18/NonIntegerSRC/issues/4>
  - <https://github.com/jatinchowdhury18/NonIntegerSRC>
  - <https://github.com/jatinchowdhury18/NonIntegerSRC/tree/main/src>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/README.md>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_test.cpp>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/LanczosSRC.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/LibSamplerRateSRC.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_utils/LanczosResampler.h>
  - <https://github.com/surge-synthesizer/sst-basic-blocks>
  - <https://github.com/surge-synthesizer/sst-basic-blocks/commits/main>
  - <https://raw.githubusercontent.com/surge-synthesizer/sst-basic-blocks/HEAD/include/sst/basic-blocks/dsp/LanczosResampler.h>
  - <https://github.com/obspy/obspy/issues/1213>
- **Sources the enricher read:**
  - <https://github.com/jatinchowdhury18/NonIntegerSRC/issues/4>
  - <https://raw.githubusercontent.com/surge-synthesizer/sst-basic-blocks/HEAD/README.md>
  - <https://raw.githubusercontent.com/surge-synthesizer/sst-basic-blocks/HEAD/include/sst/basic-blocks/dsp/LanczosResampler.h>
  - <https://raw.githubusercontent.com/surge-synthesizer/sst-basic-blocks/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/surge-synthesizer/sst-basic-blocks/HEAD/include/sst/basic-blocks/simd/setup.h>
  - <https://raw.githubusercontent.com/surge-synthesizer/sst-basic-blocks/HEAD/include/sst/basic-blocks/mechanics/simd-ops.h>
  - <https://raw.githubusercontent.com/surge-synthesizer/sst-basic-blocks/HEAD/tests/dsp_tests.cpp>
  - <https://github.com/surge-synthesizer/sst-basic-blocks/commits/main/include/sst/basic-blocks/dsp/LanczosResampler.h>
  - <https://github.com/surge-synthesizer/sst-basic-blocks/commit/6af57de>
  - <https://github.com/surge-synthesizer/sst-basic-blocks/issues?q=lanczos>
  - <https://github.com/surge-synthesizer/sst-basic-blocks/issues/82>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/README.md>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_test.cpp>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/LanczosSRC.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/LibSamplerRateSRC.h>
  - <https://raw.githubusercontent.com/jatinchowdhury18/NonIntegerSRC/HEAD/src/src_utils/LanczosResampler.h>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/HEAD/src/src_sinc.c>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/HEAD/src/fastest_coeffs.h>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/surge-synthesizer/sst-basic-blocks`) · [data/wave10/enrich/raw/github_com_surge_synthesizer_sst_basic_blocks.json](../../../data/wave10/enrich/raw/github_com_surge_synthesizer_sst_basic_blocks.json) (enrichment confidence 0.75)

</details>
