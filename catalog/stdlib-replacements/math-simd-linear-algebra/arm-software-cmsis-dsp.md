# CMSIS-DSP (FFT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Arm's C library of DSP kernels for Cortex-M and Cortex-A; its FFTs beat textbook plain-C radix-2 FFTs on Cortex-M4.

| | |
|---|---|
| **Beats** | Numerical Recipes in C radix-2 float FFT (textbook plain C); for Q31 a 32-bit adaptation of a textbook fixed-point radix-2 FFT |
| **Claimed result** | Float32 FFT about 35x faster than the Numerical Recipes radix-2 FFT with the FPU enabled for both, and about 4x faster on average with the FPU disabled; Q31 FFT about 1.9x faster at every size tested. Figures taken from a search-result summary of the post (page not opened). |
| **Workload** | Complex FFT at several sizes on a Cortex-M4F microcontroller: CMSIS-DSP float32 and Q31 FFT against textbook plain-C FFTs of the same O(n log n) class, with the FPU enabled and disabled for the float case. |
| **Metric** | latency |
| **Hardware** | STM32F407 (Cortex-M4F) at 30 MHz, zero flash wait states |
| **Compiler and flags** | Keil MDK 4.70a per a search-result summary of the post; optimisation flags not stated |
| **Adoption** | 1.1k stars; ships in CMSIS packs and has Zephyr integration files in the repo |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/ARM-software/CMSIS-DSP) · [benchmark](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/arm-dsp-is-the-way-to-go-an-intern-s-perspective) |

## Verdict

An Arm Community post by an Arm intern (2013 per the verifier) timed CMSIS-DSP's float32 and Q31 complex FFTs against the Numerical Recipes radix-2 float FFT and a 32-bit adaptation of the Roberts/Slaney/Bouras fixed-point FFT on an STM32F407 (Cortex-M4F) at 30 MHz with zero flash wait states, built with Keil MDK 4.70a (flags not stated). The figures (about 35x faster for float with the FPU on, about 4x with it off, about 1.9x for Q31) come only from a search-result summary: the post was unreachable, two searches this session confirmed the setup but not the numbers, and the CMSIS-DSP version and FFT function used are not shown.

## Use it when

- Firmware on Cortex-M4/M7/M33 (DSP extension, single-precision FPU) or Cortex-M55/M85 (Helium) that needs power-of-two FFTs of 16 to 4096 points, FIR or biquad filters, or small matrix kernels.
- Fixed-point (q15/q31) signal chains on cores without an FPU, where the library's fixed per-stage scaling is acceptable.
- Projects already on CMSIS packs, Keil/Arm Compiler 6 or Zephyr: it ships as a CMSIS pack and as a Zephyr module, so integration is a west or pack entry.
- Designing a signal chain in Python with the cmsisdsp wrapper (NumPy-compatible, fixed-point aware) and porting the same calls to C.
- Arm application processors (aarch64 with Neon) when you want one DSP API across MCU and Cortex-A targets, accepting the different Neon FFT API.

## Skip it when

- x86 or other non-Arm production targets: host builds compile as portable scalar C with none of the Arm-specific vector paths.
- FFT sizes that are not powers of two between 16 and 4096 (the documented arm_cfft range), or when you need mixed radix-3/5 lengths.
- Work that needs bit-identical output across cores: the docs say some algorithms give slightly different results on M0, M4/M7 and M55 as a speed trade-off.
- Fixed-point FFTs that need full dynamic range: Q31 input is 1.31 but output is shifted down (5.27 at 16 points up to 11.21 at 1024), so low-order bits are lost.
- Toolchains you cannot tune: the README says GCC currently gives poor Helium code (use the Arm compiler) and that -fno-builtin has a very bad impact; the older radix-2/radix-4 functions are deprecated and slower, and a plain-C fixed-point FFT (SYLT-FFT) reported 15-26% faster than the deprecated arm_cfft_radix2_q31 from CMSIS-DSP 1.4.2 at 256 points.

## How it is fast

The f32 complex FFT is a mixed-radix decimation-in-frequency transform: several radix-8 stages plus one radix-2 or radix-4 stage, driven by precomputed per-length twiddle and bit-reversal tables, so no trig or twiddle recurrence runs at transform time. Q15/Q31 FFTs use radix-4 stages plus one radix-2 stage with a fixed down-scale in each stage to avoid overflow. Separate code paths use Helium (MVE) vector butterflies with rearranged twiddle tables on Cortex-M55/M85 and Ne10-derived mixed-radix kernels on Neon; fixed-point kernels read a 32-bit word as two q15 or four q7 values. Part of the large float gap in the cited benchmark is probably the baseline: the Numerical Recipes routine keeps its twiddle recurrence in double, which a single-precision Cortex-M4F FPU must emulate (inference, not measured).

## Compared with alternatives

Pick CMSIS-DSP for transforms, filters and fixed-point DSP on Arm microcontrollers. libfixmath covers scalar fixed-point arithmetic, and SLEEF, xsimd, SIMDe and NumKong target elementwise or vector math on application-class CPUs, so none of the catalogued siblings offers its FFT and filter kernels.

## Integration

| | |
|---|---|
| **Form** | static lib or source-drop (build Source, Include, PrivateInclude; also a CMSIS pack, a Zephyr module and a CMake package exporting CMSISDSP::CMSISDSP); the DSP++ C++ layer is header-only |
| **Dependencies** | CMSIS-Core headers for Cortex-M builds (HOST=ON removes this for host builds); the in-repo ComputeLibrary and Ne10 sources for Neon builds; nothing else |
| **Minimum toolchain** | C11 in the repo's own build configs (-std=c11; DSP++ configs use -std=c++17); arm_math_types.h supports Arm Compiler 6, GCC, Clang, IAR, TI, Cosmic, Tasking and MSVC; CMake 3.14+ for the CMake build |
| **Platforms** | Cortex-M (scalar, DSP extension, Helium/MVE on M55/M85), Cortex-A and aarch64 with Neon (-DARM_MATH_NEON or cmake NEON=ON), plus scalar host builds on x86 Linux, Windows and macOS |
| **Thread safety** | Not documented. The docs say the FFT instance tables are constant and not modified during a transform, and transforms work on the caller's buffer, so concurrent transforms on separate buffers that share one instance should be safe (inference). |
| **Drop-in for the baseline** | partial — the same in-place transform on interleaved complex data, but with a different call signature, a required instance or init call, different scaling (the inverse includes 1/N; Q31 output is down-shifted), and on Neon an out-of-place API with a temporary buffer |

## Gotchas

- arm_cfft_f32 runs in place and arm_rfft_fast_f32 overwrites its input; in issue #228 the maintainer says the only way to keep the input is a temporary copy.
- Use length-specific init functions (arm_cfft_init_64_f32 and similar): the generic arm_cfft_init_f32 stops the linker from dropping unused twiddle tables, and the Helium build requires an init call rather than the constant structs.
- Build flags decide the speed: the README asks for -O3 -ffast-math and an FPU-enabled target (else soft-float emulation); -fno-builtin stops the memcpy-based type punning from being inlined; some compilers need -munaligned-access; define DISABLEFLOAT16 if f16 is unused, since it can break compilation.
- Neon builds change the f32 CFFT/RFFT API (separate input, output and temporary buffers, no bit-reverse flag), and DSP++ does not compile with ARM_MATH_NEON. Issue #247 (a Zephyr toolchain hitting an alignment fault in arm_rfft_init_q31 on Helium) was closed wontfix as a compiler problem.

## Known shortcomings

- The blog's 35x/4x/1.9x figures are seen only through search (developer.arm.com and the blog host were unreachable); the Numerical Recipes baseline may be handicapped by double-precision twiddles on Cortex-M4F (unverified). Counter-evidence: SYLT-FFT's Q31 inverse FFT is 25.6% (Keil) and 15.1% (GCC) faster than CMSIS 1.4.2.
- Enricher: the 35x, 4x and 1.9x FFT figures are still unconfirmed search-summary numbers (developer.arm.com unreachable; D candidate if never confirmed); CMSIS-DSP version and FFT function used are unknown; the SYLT-FFT counter-evidence was against the deprecated arm_cfft_radix2_q31.

## Caveats and trade-offs

[verify] The verifier's own searches confirmed the post's setup (CMSIS-DSP FFT against the Numerical Recipes radix-2 float FFT and a 32-bit adaptation of the Roberts/Slaney/Bouras fixed-point FFT, Cortex-M4, zero-wait-state memory, FPU enabled) but did not surface the 35x, 4x or 1.9x figures, so those remain unconfirmed search-summary numbers. Likely mechanism for the large float gap (inference, not stated in any opened source): the Numerical Recipes four1 routine keeps its twiddle recurrence in double, which a single-precision-only Cortex-M4F FPU must emulate in software, so the baseline is handicapped on this core. Further counter-evidence opened: SYLT-FFT's README (Freescale Kinetis K20 Cortex-M4, Keil 5.01 -O3 and GCC 4.8.4 -O3) reports its 256-point fixed-point inverse FFT 25.6% (Keil) and 15.1% (GCC) faster than arm_cfft_radix2_q31 from CMSIS-DSP 1.4.2, so tuned plain-C FFTs can beat the library's radix-2 Q31 path. [retier] Enricher: the CMSIS-DSP version and FFT function used in the post are unknown. SYLT-FFT's 15-26% win was against the deprecated arm_cfft_radix2_q31 (CMSIS-DSP 1.4.2), not the current arm_cfft_q31. The Q31 FFT output is down-shifted (by 11.21 bits at 1024 points), so outputs need rescaling before comparison. arm_rfft_fast_f32 overwrites its input (#228); Neon builds use a different CFFT/RFFT API; the README asks for -O3 -ffast-math and an FPU-enabled target.

Targets Arm Cortex-M (and Neon on Cortex-A); the README says best speed needs -O3 -ffast-math, that GCC currently gives poor Helium code so the Arm compiler is advised, and that -fno-builtin badly hurts the memcpy-based type punning. The docs note some algorithms give slightly different results on different architectures (M0, M4/M7, M55) as a speed trade-off.

## Maintenance

Actively maintained by Arm (last commit 2026-09-10; the CMake version fallback is 1.18.0), Apache-2.0, and distributed as a CMSIS pack, a Zephyr module and a pip wrapper, so it is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The Arm Community post (Nov 2013, Arm intern, first-party) could not be opened (getaddrinfo ENOTFOUND developer.arm.com); search snippets confirm it benchmarks CMSIS-DSP FFTs against a Numerical Recipes radix-2 float FFT and an adapted Roberts/Slaney/Bouras fixed-point FFT on a Cortex-M4 with zero-wait-state memory, but the speedup figures are snippet-only and no benchmark code, flags or committed results are public, so at most C.
- **Verifier notes:** Confirmed at C on the snippet-only rule; numbers could not be re-confirmed (developer.arm.com and openaudio.blogspot.com unreachable). Metadata confirmed: Apache-2.0, 1.1k stars, not a fork, last commit 2026-09-10 (active). Issue 70 counter-evidence checked (arm_biquad_cascade_df2T_f32 Neon about 80% slower than reporter's C on Cortex-A57, GCC 7.3 -Ofast); its open/closed state was ambiguous on the fetched page.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-88 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/ARM-software/CMSIS-DSP>
  - <https://github.com/ARM-software/CMSIS-DSP/commits/main>
  - <https://github.com/ARM-software/CMSIS-DSP/issues/70>
  - <https://github.com/stg/SYLT-FFT>
- **Sources the enricher read:**
  - <https://github.com/ARM-software/CMSIS-DSP>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-DSP/HEAD/README.md>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-DSP/HEAD/Source/TransformFunctions/arm_cfft_f32.c>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-DSP/HEAD/Source/TransformFunctions/arm_cfft_q31.c>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-DSP/HEAD/Include/dsp/transform_functions.h>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-DSP/HEAD/Include/arm_math_types.h>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-DSP/HEAD/CMakeLists.txt>
  - <https://github.com/ARM-software/CMSIS-DSP/tree/main/dsppp>
  - <https://raw.githubusercontent.com/ARM-software/CMSIS-DSP/HEAD/dsppp/cdefault.yml>
  - <https://github.com/ARM-software/CMSIS-DSP/issues?q=is%3Aissue+fft>
  - <https://github.com/ARM-software/CMSIS-DSP/issues/228>
  - <https://github.com/ARM-software/CMSIS-DSP/issues/247>
  - <https://raw.githubusercontent.com/stg/SYLT-FFT/HEAD/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/arm-software/cmsis-dsp`) · [data/wave1/enrich/raw/github_com_arm_software_cmsis_dsp.json](../../../data/wave1/enrich/raw/github_com_arm_software_cmsis_dsp.json) (enrichment confidence 0.65)

</details>
