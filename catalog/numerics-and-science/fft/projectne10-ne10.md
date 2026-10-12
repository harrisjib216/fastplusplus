# Ne10 (NEON FFT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> ARM's NEON-optimized C library whose FFTs (float, Q31, Q15) beat FFmpeg's assembly FFT on an Android phone.

| | |
|---|---|
| **Beats** | FFmpeg libavcodec FFT (assembly); also tricl_fft and CkFft |
| **Claimed result** | Issue #165 table ('Cycles', unit and measurement method not explained): SuperpoweredFFT 7375; ne10_fft (asm) 10125; libavcodec (asm) 14375; tricl_fft_fft 21833; CkFft 25000. So Ne10 is about 1.42x faster than libavcodec (derived from page data) and SuperpoweredFFT is about 1.37x faster than Ne10 (derived from page data). The issue says further optimization of Ne10 is possible. |
| **Workload** | Complex FFT of length 1024 on an Android Samsung Galaxy S6, 'Cycles' per library, posted in Ne10 GitHub issue #165 ('Ne10 vs Superpowered', 2017-04-20) by GitHub user lieff, who writes 'we made some fft benchmarks' and does not claim to have written any of the libraries. |
| **Metric** | latency |
| **Hardware** | Samsung Galaxy S6 (Android) |
| **Adoption** | 1.5k stars, 424 forks, 282 commits |
| **Last commit** | 2018-11-15 |
| **Links** | [repository](https://github.com/projectNe10/Ne10) · [benchmark](https://github.com/projectNe10/Ne10/issues/165) |

## Verdict

A single third-party post (issue #165, 2017) reports cycles for a 1024-point complex FFT on a Samsung Galaxy S6: Ne10 (asm) 10125 vs FFmpeg libavcodec (asm) 14375, about 1.42x faster (derived from page data), also ahead of tricl_fft and CkFft but behind SuperpoweredFFT (7375). The post gives no compiler, flags, Ne10 version, timing method or code, and does not define 'cycles'.

## Use it when

- 32-bit ARMv7-A Android or Linux targets with NEON where you need a small, permissively licensed FFT; the hand-written assembly path is enabled only on ARMv7.
- Audio and DSP on phones and embedded Cortex-A: power-of-two complex or real FFTs (e.g. 256-4096 points) reusing one config per size.
- Fixed-point pipelines that need Q15 or Q31 FFTs with optional per-stage scaling (scaled_flag), which most float-only libraries lack.
- Projects that already use other Ne10 DSP blocks (FIR, IIR) and want one consistent ARM library.

## Skip it when

- x86 or any non-ARM target: CMake refuses non-ARM Linux builds, and there is no SSE/AVX code.
- Double precision, multi-dimensional or batched transforms: not provided (issues #243, #234 and #251 ask for doubles and 2-D).
- Arbitrary lengths: float C2C needs 2^a\*3^b\*5^c (NEON also needs N % 4 == 0 above 2), and the int32, int16 and real transforms are powers of two only; alloc returns NULL otherwise.
- If you need the fastest NEON FFT: the only head-to-head (issue #165) has SuperpoweredFFT about 1.37x faster than Ne10 at N=1024 (derived from page data), and there is no comparison against FFTW, KissFFT or PFFFT on the repo pages read here.
- Toolchain-sensitive builds: reports of all-zero output with NDK r20 clang (#237), broken r2c/c2r at N &gt;= 4096 under -Ofast (#241) and AArch64 NDK/iOS build failures (#239, #252), with no maintainer fixes since 2018.

## How it is fast

It runs a mixed-radix Cooley-Tukey FFT (radix 2/3/4/5, with a combined radix-8 first stage) over twiddle and factor tables precomputed in the config. For sizes divisible by 4 the NEON path splits the transform into four interleaved sub-FFTs processed across NEON lanes, then finishes with a 'super twiddle' last stage. Power-of-two kernels exist as NEON intrinsics and, on ARMv7 builds, as hand-written NEON assembly (\*.neon.s); the issue #165 figure is for that '(asm)' path.

## Compared with alternatives

Pick Ne10 over SYLT-FFT when the target is a NEON-capable Cortex-A rather than a Cortex-M4. Pick it over PFFFT or PocketFFT when you need Q15/Q31 fixed-point FFTs or ARMv7 hand-tuned assembly; prefer those for portable or x86 code or maintained sources.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (shared library optional via -DNE10_BUILD_SHARED=ON) |
| **Minimum toolchain** | CMake; GCC with GNU assembler syntax (C built as gnu99, some FFT files are C++); Android NDK with API level &gt;= 21 and GCC &gt;= 4.8 for AArch64; iOS 7.0+ |
| **Platforms** | ARMv7-A with NEON and AArch64 on Linux, Android and iOS; math and physics modules are ARMv7-only; no non-ARM support |
| **Thread safety** | One config per thread: each cfg holds a scratch buffer used during the transform, and issue #218 (open, unanswered) reports that sharing a plan across threads fails. |
| **Drop-in for the baseline** | no |

## Gotchas

- Call ne10_init() before using the generic names (ne10_fft_c2c_1d_float32 and so on); they are function pointers that ne10_init() binds to the NEON or C variant.
- Scaling: by default only the inverse transform is scaled by 1/N; the fixed-point variants take a scaled_flag; sizes below 15 silently fall back to the C path.
- The root CMakeLists.txt aborts unless CMAKE_SYSTEM_PROCESSOR starts with 'arm', so native builds on hosts that report 'aarch64' hit that check; the GAS-syntax assembly is also awkward for clang outside the iOS toolchain file.
- NEON and C fixed-point Q31 results differ slightly (#233), and the R2C example comment in NE10_dsp.h is reported wrong (#267).

## Known shortcomings

- 'Cycles' unit undefined; the issue poster (lieff) does not claim to be SuperpoweredFFT's author (record fixed).
- Open correctness issues without fix: #237 FFT returns all zeros with NDK r20 clang, #241 -Ofast breaks real FFTs at N&gt;=4096, #218 a plan cannot be shared across threads, #233 NEON and C fixed-point results differ; root CMake aborts unless CMAKE_SYSTEM_PROCESSOR matches ^arm (blocks native aarch64 builds); still only one benchmark (#165), no FFTW or KissFFT comparison.

## Caveats and trade-offs

Weak evidence: one issue post with one size, one phone, no code and no methodology or Ne10 version; the 'Cycles' unit is not defined. The record previously said the measurement came from SuperpoweredFFT's author; the issue does not say that. It does not compare to KissFFT or FFTW. Ne10's own ARM community blog posts reportedly compare against FFTW, OpenMax DL, kissFFT and pffft (search snippets say Ne10 beats FFTW in most cases), but developer.arm.com is blocked here, so those numbers are not recorded; a dlib discussion (#3030) says Ne10 FFTs are much faster than FFTW on ARM but gives no numbers. Last commit 2018-11-15.

Arm NEON-optimized FFT (assembly noted for the FFT in the issue comment) for ARMv7 and AArch64 with a complex FFT sample in the repo; part of a larger NEON math library.

## Maintenance

Abandoned since 2018-11-15 (no releases or maintainer replies to the FFT bug reports read here, about 100 open issues) but BSD-3-Clause (ARM Limited), 1.5k stars and small enough to vendor; pin your toolchain and test outputs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** A single GitHub issue (#165, 2017-04-20) lists 'Cycles' for five FFT libraries on one phone at one size with no code, compiler, Ne10 version or methodology; numbers without methodology are C.
- **Verifier notes:** Issue numbers confirmed verbatim; misattribution of the poster corrected. BSD-3-Clause (ARM Limited) confirmed from LICENSE; 1.5k stars; last commit 2018-11-15 on master (abandoned). A better tier needs the ARM blog benchmark page, which a non-cloud run could open.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/projectNe10/Ne10/issues/165>
  - <https://github.com/projectNe10/Ne10>
  - <https://github.com/projectNe10/Ne10/commits>
  - <https://raw.githubusercontent.com/projectNe10/Ne10/HEAD/LICENSE>
  - <https://github.com/davisking/dlib/discussions/3030>
- **Sources the enricher read:**
  - <https://github.com/projectNe10/Ne10>
  - <https://github.com/projectNe10/Ne10/commits/master>
  - <https://github.com/projectNe10/Ne10/tree/master/modules/dsp>
  - <https://github.com/projectNe10/Ne10/issues?q=is%3Aissue+fft>
  - <https://github.com/projectNe10/Ne10/issues/165>
  - <https://github.com/projectNe10/Ne10/issues/218>
  - <https://github.com/projectNe10/Ne10/issues/237>
  - <https://github.com/projectNe10/Ne10/issues/241>
  - <https://raw.githubusercontent.com/projectNe10/Ne10/HEAD/README.md>
  - <https://raw.githubusercontent.com/projectNe10/Ne10/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/projectNe10/Ne10/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/projectNe10/Ne10/HEAD/doc/building.md>
  - <https://raw.githubusercontent.com/projectNe10/Ne10/HEAD/inc/NE10_dsp.h>
  - <https://raw.githubusercontent.com/projectNe10/Ne10/HEAD/inc/NE10_init.h>
  - <https://raw.githubusercontent.com/projectNe10/Ne10/HEAD/samples/NE10_sample_complex_fft.c>
  - <https://raw.githubusercontent.com/projectNe10/Ne10/HEAD/modules/dsp/NE10_fft.c>
  - <https://raw.githubusercontent.com/projectNe10/Ne10/HEAD/modules/CMakeLists.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/projectne10/ne10`) · [data/wave8/enrich/raw/github_com_projectne10_ne10.json](../../../data/wave8/enrich/raw/github_com_projectne10_ne10.json) (enrichment confidence 0.7)

</details>
