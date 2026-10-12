# LibFResample

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🔴 abandoned

> BSD-licensed C polyphase sinc resampler for 16-bit mono/stereo using SSE2/AltiVec; roughly 8-13x libsamplerate at comparable bandwidth.

| | |
|---|---|
| **Beats** | libsamplerate (Secret Rabbit Code 0.1.8) |
| **Claimed result** | Stereo, System C (3.2 GHz AMD Phenom II, GCC 4.7): LibFResample Q=5 Medium 1276x realtime vs libsamplerate Sinc Med. 35x and Sinc Fast 68x; Q=8 High 318x vs Sinc Best 8.5x; System D (1.7 GHz Core i5, Clang 4.0): Q=5 1247x vs Sinc Med. 39x. Mono Q=2 Low 3195x vs libsamplerate Linear 1112x (System D). Pairs closer in passband width: Q=8 High (19.5 kHz) vs Sinc Med. (90% bandwidth) 318x vs 35x on System C (about 9.1x, derived from page data) and 303x vs 39x on System D (about 7.8x, derived from page data); Q=10 Ultra (21.2 kHz) vs Sinc Best (97% bandwidth) 107x vs 8.5x on System C (about 12.6x, derived from page data) and 87x vs 11x on System D (about 7.9x, derived from page data). |
| **Workload** | Resampling 16-bit stereo and mono audio from 48 kHz to 44.1 kHz, measured as multiples of real time on four machines. |
| **Metric** | throughput |
| **Hardware** | 1.6 GHz Intel Atom, 2.0 GHz PowerPC G5, 3.2 GHz AMD Phenom II, 1.7 GHz Intel Core i5 |
| **Compiler and flags** | GCC 4.4 (System A), GCC 4.0 (B), GCC 4.7 (C), Clang 4.0 (D); optimization flags not stated |
| **Adoption** | 59 stars |
| **Last commit** | 2022-05-31 |
| **Links** | [repository](https://github.com/depp/libfresample) · [benchmark](https://github.com/depp/libfresample) |

## Verdict

First-party README table, 48 to 44.1 kHz: LibFResample, timed by its own CLI with clock() over 20 whole-buffer passes of 2 minutes of pink noise after one warm-up, against libsamplerate 0.1.8 figures taken from SRC's throughput test. Optimisation flags are not stated; the machines are a 1.6 GHz Atom (GCC 4.4), a 2.0 GHz G5 (GCC 4.0), a 3.2 GHz Phenom II (GCC 4.7) and a 1.7 GHz Core i5 (Clang 4.0). The 36x Q=5 headline pairs a 24-tap 16-bit filter with SRC Medium's roughly 91-tap float filter (tap count per the r8brain-free-src entry), so the fairer pairs are Q=8 vs Sinc Medium (about 8-9x) and Q=10 vs Sinc Best (about 8-13x), both derived from page data. The SRC throughput test (checked in 0.1.9; 0.1.8 is not tagged on GitHub) converts mono float data at ratio 0.99, so the stereo table's SRC rows are probably mono figures that flatter SRC rather than LibFResample.

## Use it when

- Offline or batch conversion of 16-bit PCM at a fixed ratio (e.g. 48 kHz to 44.1 kHz) when throughput matters more than a 120 dB stop band. At Q=8 (19.5 kHz passband, 92 dB measured SNR) the README's numbers are 303-318x realtime vs 35-39x for libsamplerate Sinc Medium on a Phenom II and a 2012 Core i5.
- Games, voice or embedded audio pipelines that already work in int16 and want a permissive (BSD-2-Clause) resampler without libsamplerate's GPL history or soxr's LGPL.
- Low-quality fast paths: Q=2 (8 taps, 13.3 kHz bandwidth) beats libsamplerate's linear interpolator on mono, 3195x vs 1112x realtime on System D.
- PowerPC/AltiVec targets, which few other resamplers vectorise.

## Skip it when

- Float, 24-bit or multichannel (&gt;2) audio: only native s16 mono/stereo is implemented, and other formats are silently dropped.
- Mastering-grade conversion: Q=5 is a 24-tap filter designed for about 60-74 dB stop band (84 dB measured SNR). The ultra preset uses 272 taps and is still only nominally 120 dB, and every output carries 1-LSB dither.
- Real-time streaming where you want a simple push API: you must track fractional positions and input overlap yourself. Issue #2 'Cannot figure out the API' and open issue #3 'API Simplification' confirm this.
- ARM: no NEON path (issue #1 open since 2016), so ARM gets the scalar code.
- Projects that need error reporting or maintenance: the README says the library is not release quality, there is no error return (filter allocation failure calls abort()), and the code has not changed since April 2013 (the 2022 commits only port Python scripts and the README).

## How it is fast

The filter is precomputed for the given ratio as a bank of 2^k+1 fractional-phase copies laid out contiguously. Each output sample linearly interpolates between two adjacent phases, using 14-bit weights packed for pmaddwd. When 16-bit coefficients meet the error budget (Q&lt;=5 here), the dot product runs entirely in 16-bit integer SIMD (_mm_madd_epi16, eight taps per pair of instructions, four output frames combined per store). Filters of 8-24 taps get unrolled fast paths. Higher presets switch to float coefficients with SSE packed multiply-adds. The filter length is the Kaiser-formula minimum rounded up to a multiple of 8. For 48 to 44.1 kHz that gives 24 taps (16-bit) at Q=5, 72 taps (float) at Q=8 and 272 at Q=10, derived from the presets in lib/param.c and the length formula in lib/filter_new.c. The r8brain-free-src catalog entry puts libsamplerate MEDIUM at about 91 taps per output sample. Dispatch to SSE2 or AltiVec happens at run time via CPUID or sysctl, with a scalar fallback.

## Compared with alternatives

Pick LibFResample over libsoxr (LGPL, about 11x libsamplerate MEDIUM in a third-party table) or r8brain-free-src (MIT, double-precision, 120-180 dB) only when your data is 16-bit, a 90-100 dB class filter is enough, and you want the smallest permissive C code. For float pipelines, higher stop bands or maintained code, prefer r8brain-free-src or soxr; for drifting-ratio ASRC, SampleRateTap.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc and libm); the test and benchmark scripts need Python 3, SoX and SciPy |
| **Minimum toolchain** | C compiler with SSE2 intrinsics (-msse2) or AltiVec; README benchmarks used GCC 4.0-4.7 and Clang 4.0. The autoconf/genmake build and Xcode projects are described as broken; Visual C++ projects (libfresample.sln, libfresample_static.vcxproj) were added in 2013 although the README still says there is no Windows port. |
| **Platforms** | x86 and x86-64 (SSE2, runtime-detected), PowerPC (AltiVec); scalar fallback elsewhere; little- and big-endian |
| **Thread safety** | not documented; resampler state (position, dither) lives in caller variables and filters are read-only after creation, but CPU-feature flags are a lazily initialised global and lfr_setcpufeatures writes it |
| **Drop-in for the baseline** | no |

## Gotchas

- Parameter bug in lfr_param_calculate: the pass-band branch tests ISSET(ATTEN) instead of ISSET(FPASS). Setting ATTEN alone makes the filter read an FPASS value that was never set (malloc'd garbage), and setting FPASS alone is ignored. The quality presets used in the benchmarks are not affected.
- lfr_resample returns silently, writing nothing, unless both formats are LFR_FMT_S16_NATIVE and nchan is 1 or 2. The header's promise of intermediate conversion buffers is not implemented.
- Buffer lengths and positions are int frames with a 32.32 fixed-point position, so a single call cannot exceed 2^31 frames, and the caller must keep pos and dither across calls for gapless streaming.
- Dither (an LCG adding 1 LSB of uniform noise before truncation) is always on; output is reproducible only if you reuse the same dither seed.

## Known shortcomings

- README numbers only; the headline Q=5 setting (16.3 kHz bandwidth, 84 dB) does less work than libsamplerate's Sinc Medium (90% bandwidth, 97 dB). Bandwidth-matched pairs (Q=8/Q=10) are still about 8-13x (derived). The libsamplerate side comes from a different harness (its own mono throughput test).
- From source: Q=5 is a 24-tap int16 filter (about 73.5 dB design), Q=8 a 72-tap float filter and Q=10 272 taps, so the Q=5 36x headline is not like-for-like with SRC's best quality. SRC's throughput_test (0.1.9) runs mono float at ratio 0.99, so the stereo-table SRC rows are likely mono figures (which flatters SRC). param.c tests ISSET(ATTEN) where ISSET(FPASS) was meant (garbage FPASS when ATTEN is set alone; presets unaffected); lfr_resample silently no-ops for non-s16 formats; code frozen since 2013-04; VC++ projects exist despite the README's 'no Windows'.

## Caveats and trade-offs

Numbers are from 2005-2012 hardware and libsamplerate 0.1.8. The headline Q=5 Medium setting does less work than the libsamplerate converters it is paired with: by LibFResample's own quality table Q=5 keeps 16.3 kHz at 84 dB SNR, while libsamplerate documents 97 dB SNR at 90% bandwidth for Sinc Medium (about 19.8 kHz at 44.1 kHz output) and 80% (about 17.6 kHz) for Sinc Fast, and its MEDIUM filter table states 120.61 dB stop-band attenuation. Q=8 and Q=10 match libsamplerate's Medium and Best bandwidths more closely but measure 92 dB SNR (limited by the 16-bit dithered test floor), so stop-band parity is unproven. The two sides were timed by different harnesses: LibFResample on 16-bit pink noise (tests/benchmark.py, 20 iterations), libsamplerate by its own throughput test, which in the current libsamplerate source runs mono float data at ratio 0.99 through src_simple, so the stereo SRC rows are likely mono-test figures (not confirmed for 0.1.8). Optimization flags are not stated. The README says the library is not release quality (16-bit mono/stereo only, no error reporting). Baseline is not an FFmpeg component, so baseline_in_list is false. Last commit 2022-05-31.

Only 16-bit mono/stereo input, no error reporting, SSE2 and AltiVec only, no Windows port; README itself says it is not release quality. Quality table: Q=5 gives 16.3 kHz bandwidth and 84 dB SNR, Q=8 19.5 kHz and 92 dB; filter is a plain Kaiser-windowed sinc.

## Maintenance

Abandoned: the code is unchanged since April 2013, the README and Python scripts were touched in May 2022, and four issues are open (three on a Version 1.0 milestone). BSD-2-Clause, about 30 small C files, easy to vendor if 16-bit-only input and the caller-managed streaming API are acceptable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table; LibFResample side timed by its own tests/benchmark.py, libsamplerate side taken from SRC's own throughput test divided by 44100, compilers named but no flags and CPUs given only as clock and family (e.g. '3.2 GHz AMD Phenom II'), so C.
- **Verifier notes:** All quoted figures match the README table exactly. The main issue is quality pairing: Q=5 is narrower and noisier than Sinc Medium, so the 36x headline is not like-for-like; bandwidth-matched pairs still show about 8-13x (derived). Metadata (BSD-2-Clause, 59 stars, last commit 2022-05-31) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/depp/libfresample>
  - <https://github.com/depp/libfresample/commits>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/README.md>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/tests/benchmark.py>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/HEAD/docs/api_misc.md>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/HEAD/src/mid_qual_coeffs.h>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/HEAD/tests/throughput_test.c>
- **Sources the enricher read:**
  - <https://github.com/depp/libfresample>
  - <https://github.com/depp/libfresample/commits>
  - <https://github.com/depp/libfresample/issues?q=is%3Aissue>
  - <https://github.com/depp/libfresample/tree/master/lib>
  - <https://github.com/depp/libfresample/tree/master/src>
  - <https://github.com/depp/libfresample/tree/master/tests>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/README.md>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/comparison.txt>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/include/fresample.h>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/genmake.py>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/tests/benchmark.py>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/lib/param.c>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/lib/filter_new.c>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/lib/filter_new_window.c>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/lib/filter.h>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/lib/resample.c>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/lib/resample_s16func.c>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/lib/resample_s16n2s16_sse2.c>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/lib/resample_s16n2f32_sse2.c>
  - <https://raw.githubusercontent.com/depp/libfresample/HEAD/lib/cpu.c>
  - <https://github.com/libsndfile/libsamplerate/tags>
  - <https://raw.githubusercontent.com/libsndfile/libsamplerate/0.1.9/tests/throughput_test.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/depp/libfresample`) · [data/wave10/enrich/raw/github_com_depp_libfresample.json](../../../data/wave10/enrich/raw/github_com_depp_libfresample.json) (enrichment confidence 0.8)

</details>
