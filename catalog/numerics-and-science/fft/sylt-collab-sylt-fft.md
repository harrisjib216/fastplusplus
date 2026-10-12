# SYLT-FFT (fixed-point FFT for Cortex-M4)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `MHG (Moral High Ground) license: the Unlicense text released 'under the single condition that good moral standards are maintained in its use', plus non-binding requests; custom, not an OSI/SPDX license (the README calls it GPL-compatible)` · 🔴 abandoned

> Header-only 32-bit fixed-point radix-2 (I)FFT for Cortex-M4; 15-26% faster than CMSIS-DSP arm_cfft_radix2_q31 on a 256-point inverse.

| | |
|---|---|
| **Beats** | CMSIS-DSP arm_cfft_radix2_q31 (arm_cortexM4I_math.lib 1.4.2) |
| **Claimed result** | +25.6% faster (Keil C 5.01 -O3) and +15.1% faster (GNU ARM 4.8.4 -O3) than arm_cfft_radix2_q31 for fft_inverse at N=256. |
| **Workload** | 256-point inverse 32-bit fixed-point complex FFT on a Freescale Kinetis K20 (Cortex-M4). |
| **Metric** | latency |
| **Hardware** | Freescale Kinetis K20 (Cortex-M4/ARMv7E-M) |
| **Compiler and flags** | Keil C Compiler 5.01 -O3; GNU Tools for ARM Embedded Processors 4.8.4 -O3 |
| **Adoption** | 90 stars |
| **Last commit** | 2021-01-29 |
| **Links** | [repository](https://github.com/sylt-collab/SYLT-FFT) · [benchmark](https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/README.md) |

## Verdict

The README has one data point: a 256-point inverse complex FFT (bare fft_inverse, DIT, 32-bit fixed point) on a Freescale Kinetis K20 Cortex-M4. It ran 25.6% faster than CMSIS-DSP 1.4.2's arm_cfft_radix2_q31 built with Keil C 5.01 -O3, and 15.1% faster built with GNU ARM Embedded GCC 4.8.4 -O3. No cycle counts are published, and the public main.c (FTM0 cycle counter, 100-run average on a zeroed buffer) contains only the SYLT side. The 2021 DIT fix changed only fft_forward, so the benchmarked inverse code is unchanged.

## Use it when

- Cortex-M4-class MCUs (the asm fast paths are enabled for __CORTEX_M &gt;= 4) running small power-of-two complex FFTs, N &lt;= 512 with the shipped table, in 32-bit fixed point where cycles matter more than accuracy
- MCU audio synthesis that builds a spectrum directly (fft_real_phase_magnitude, fft_magnitude) and runs an inverse FFT: the use case it was written and benchmarked for
- Firmware that wants no dependencies, no libm (with the ROM sine table), no plan allocation and minimal stack
- Old Keil or GCC firmware that still calls the legacy CMSIS-DSP arm_cfft_radix2_q31

## Skip it when

- Projects on current CMSIS-DSP: the only comparison is against arm_cfft_radix2_q31 from CMSIS-DSP 1.4.2 (2014), not the later arm_cfft_q31 routines, so the gain over today's CMSIS is unknown
- Accuracy-sensitive work: the README says it is designed for speed, not accuracy. The forward transform halves at every stage, rounding and saturation are off by default, and the caller must prevent overflow (open issue #10 asks how to scale inputs).
- Floating-point data, non-power-of-two lengths, or N &gt; 512 without regenerating the sine table (SINE_BITS goes up to 14, i.e. 65,536 points)
- Code that needs proven correctness: the forward DIT trivial butterfly was wrong from 2014 until January 2021 (issue #5, fixed in c6f58ca); there is no test suite and there have been no commits since
- Organizations whose legal review rejects non-standard licenses: MHG is the Unlicense plus a 'good moral standards' condition

## How it is fast

The radix-2 butterflies are written around Cortex-M4 DSP instructions issued through inline asm: SMMULR/SMMLAR/SMMLSR (32x32 multiply keeping the rounded high word, optionally accumulating), RBIT for bit reversal, and optional QADD/QSUB saturation. Butterflies with trivial twiddles (1 and -j) get their own multiply-free loops. The twiddle loop uses the -j symmetry so one table value serves the butterflies at k and k+stride/4, which is why a 129-entry quarter-wave sine table covers N up to 512. Macros switch the code style per compiler (scalar locals for GCC, struct copies for Keil) for better register allocation.

## Compared with alternatives

Pick it for fixed-point FFTs on Cortex-M microcontrollers, where none of the catalogued siblings fit: Ne10 targets NEON application cores, and meow_fft, PFFFT and PocketFFT are floating-point libraries for larger CPUs.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (no libm needed with SINE_USE_TABLE=1; CMSIS device headers only for the main.c benchmark) |
| **Minimum toolchain** | C99 (README: -std=c99 for GCC); measured with Keil C 5.01 and GNU Tools for ARM Embedded Processors 4.8.4 |
| **Platforms** | ARM Cortex-M4 (ARMv7E-M) for the asm fast paths. Cortex-M0/M3 builds use C fallbacks and print a warning (support merged in 2016). Elsewhere portable C fallbacks apply, except that the GCC qadd asm is not guarded by __arm__, so FFT_SATURATE=1 does not build with GCC on non-ARM hosts. |
| **Thread safety** | Not documented. The transforms touch only the caller's buffer and read-only tables, so separate buffers can be processed concurrently; with SINE_USE_TABLE=0, sine_init() must run first. |
| **Drop-in for the baseline** | no |

## Gotchas

- fft_forward/fft_inverse do not bit-reverse: DIT needs fft_permutate before the call and DIF after it (fft_fft/fft_ifft do this). The published benchmark times bare fft_inverse, so its time excludes the permutation; the CMSIS side is not in the repo, so whether its timing included bit reversal is not documented.
- Scaling is asymmetric: the forward transform divides by N (one halving per stage) and the inverse is unscaled. A round trip returns the input, but an inverse of a large-magnitude spectrum can overflow silently unless FFT_SATURATE is on.
- Functions and the const sinetable[] are defined in the headers without static, so include fft.h in only one C translation unit or the link fails with duplicate symbols
- Configuration means editing config.h (DIT/DIF, rounding, saturation, SINE_BITS). With the ROM table, changing SINE_BITS hits an #error until you paste in a regenerated table.

## Known shortcomings

- Custom MHG license (Unlicense plus a moral-use condition), so reference only; the public harness has no CMSIS side.
- Timed fft_inverse excludes bit reversal and the CMSIS side of the comparison is not public, so the claim is not reproducible. Forward DIT transform was wrong 2014-2021 (#5; fix c6f58ca changed only fft_forward, the benchmarked inverse is unchanged). Functions and sine table defined in headers without static (one translation unit only). GCC qadd inline asm has no ARM guard, so FFT_SATURATE=1 fails to build with GCC on non-ARM hosts.

## Caveats and trade-offs

One data point (256-point inverse) against the 2014 CMSIS-DSP 1.4.2 library, which predates later CMSIS FFT routines (arm_cfft_q31). Only percentages are published, no cycle counts. The public harness main.c (FRDM-K20D50M, FTM0 cycle counter) times only SYLT's fft_inverse; the CMSIS side is not in the repo. License is the custom MHG text: the Unlicense plus a vague 'good moral standards' condition, so it is non-standard and treated as reference. A forward-FFT DIT math error was fixed in Jan 2021. 'Designed for optimal performance, not optimal accuracy'; inputs must be scaled to avoid overflow.

32-bit fixed-point radix-2 only, in place, no plan, tiny twiddle tables; DIT or DIF; optional rounding and saturation. Designed for speed, not accuracy; the caller must prevent overflow.

## Maintenance

Abandoned since 2021-01-29 (17 commits, 90 stars, 5 open questions/requests). Small enough to vendor, but the MHG license's moral-use condition keeps it at reference usability.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party percentages against CMSIS-DSP arm_cfft_radix2_q31 with compilers, -O3 and the MCU (Kinetis K20). The public main.c harness (FTM0 cycle counter, 100 runs) times only SYLT's fft_inverse; there is no CMSIS call or raw cycle count in public code, so not A.
- **Verifier notes:** README numbers match. 90 stars and 24 forks; last commit 2021-01-29 (master), so abandoned (already set). The license field was null; it is now filled with the MHG description. Usability stays reference because of the moral-use condition.
- **Fields the verifier corrected:** `license`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/main.c>
  - <https://github.com/sylt-collab/SYLT-FFT>
  - <https://github.com/sylt-collab/SYLT-FFT/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/main.c>
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/fft.h>
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/config.h>
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/intrinsics.h>
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/HEAD/fpmath.h>
  - <https://raw.githubusercontent.com/sylt-collab/SYLT-FFT/c6f58caa8d3d01c622768b5c66a0be1d7953235b~1/fft.h>
  - <https://github.com/sylt-collab/SYLT-FFT>
  - <https://github.com/sylt-collab/SYLT-FFT/issues?q=is%3Aissue>
  - <https://github.com/sylt-collab/SYLT-FFT/issues/5>
  - <https://github.com/sylt-collab/SYLT-FFT/commits/master>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sylt-collab/sylt-fft`) · [data/wave8/enrich/raw/github_com_sylt_collab_sylt_fft.json](../../../data/wave8/enrich/raw/github_com_sylt_collab_sylt_fft.json) (enrichment confidence 0.75)

</details>
