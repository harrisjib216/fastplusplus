# Qfplib-M0-full (Cortex-M0 floating-point library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly` · `GPL-2.0-only` · 🔴 abandoned

> Hand-written ARMv6-M assembly float/double library for Cortex-M0, 1.3-14x fewer cycles than GCC's soft-float and math routines.

| | |
|---|---|
| **Beats** | The GCC toolchain's floating-point library on ARMv6-M ('GCC library' in the README): libgcc soft-float for add/sub/mul/div, and presumably the toolchain's C math library (such as newlib libm) for sqrt, sin, cos, tan, atan2, exp and ln; version and flags not stated |
| **Claimed result** | Cycles Qfplib vs GCC library: fadd 76 vs 102, fmul 62 vs 166, fdiv 83 vs 475, fsqrt 67 vs 460, fsin 584 vs 3300, fexp 261 vs 1930, dmul 163 vs 377, ddiv 200 vs 1190, dsqrt 174 vs 1305, dln 464 vs 4375. README also says the double-precision Qfplib routines are faster than the GCC single-precision ones in every case. |
| **Workload** | Average cycle counts per call for single- and double-precision add, sub, mul, div, sqrt, sin, cos, tan, atan2, exp and ln on an NXP LPC11U68 (Cortex-M0, single-cycle flash), non-exceptional arguments, calling overhead included. |
| **Metric** | latency |
| **Hardware** | NXP LPC11U68 (ARM Cortex-M0+, ARMv6-M), single-cycle flash; the library source targets .cpu cortex-m0plus |
| **Adoption** | 17 stars, 8 forks (RT-Thread packaging of the upstream Qfplib; README links quinapalus.com/qfplib.html for the original) |
| **Last commit** | 2021-05-26 |
| **Links** | [repository](https://github.com/mysterywolf/Qfplib-M0-full) · [benchmark](https://github.com/mysterywolf/Qfplib-M0-full/blob/master/README.md) |

## Verdict

The README table gives approximate average cycle counts, including calling overhead, for non-exceptional arguments on an NXP LPC11U68 (Cortex-M0+, single-cycle flash) against an unversioned 'GCC library' (libgcc soft-float, plus presumably newlib libm for the scientific functions): fadd 76 vs 102 (1.34x), fmul 62 vs 166 (2.7x), fdiv 83 vs 475 (5.7x), fsqrt 67 vs 460 (6.9x), fsin 584 vs 3300 (5.7x), fln 277 vs 3960 (14.3x), dmul 163 vs 377 (2.3x), ddiv 200 vs 1190 (6.0x), dln 464 vs 4375 (9.4x) (ratios derived from page data). No compiler version, flags or harness are given.

## Use it when

- FPU-less Cortex-M0/M0+ firmware whose hot loop does float division or square roots: qfp_fdiv 83 vs 475 cycles and qfp_fsqrt 67 vs 460 for the GCC library.
- Scientific functions on an M0 with bounded arguments (|x| up to 128 for single, 1024 for double) where about 1 ulp suffices: qfp_fsin 584 vs 3300 cycles, qfp_fln 277 vs 3960.
- Double precision on an M0 without paying for it: every Qfplib double routine is faster than GCC's single-precision one (qfp_dmul 163 vs GCC fmul 166).
- Flash- and RAM-tight or certification-minded projects: under 6 KB of code, no static data, statically analysable stack use.
- GPLv2-compatible RT-Thread projects built with GCC, where enabling the package is a menuconfig switch.

## Skip it when

- Proprietary firmware that cannot carry GPLv2-only code (the README says to ask the author for other licensing).
- Code that relies on IEEE special values: NaNs become infinities and denormals are flushed to zero, so isnan() checks and gradual underflow break.
- Trigonometry on large or very small arguments: single-precision sin/cos/tan need |x| below 128 (double below 1024), and the fixed-point reduction gives absolute rather than relative accuracy near multiples of pi, including near zero.
- Cortex-M3/M4/M7: the README says it runs there but is not optimised; use the hardware FPU or a library tuned for ARMv7-M.
- Keil (armcc) or IAR builds: only the GCC assembler source is in the repo; on RP2040 use the pico-sdk float routines, which call the same author's code in ROM.

## How it is fast

Every routine is hand-scheduled Thumb-1 code that works on unpacked two's-complement mantissas in registers, with no static storage and no recursion. Add, sub, mul, div and sqrt are correctly rounded integer-mantissa routines. The scientific functions use CORDIC-style shift-and-add iterations in fixed point (rotation mode for sin/cos with the remaining iterations collapsed into one multiplication, vector mode for atan2, table-driven x += x&gt;&gt;i steps for exp, tan as sin/cos plus one divide), so each call is a short integer sequence instead of a chain of generic soft-float operations. Double sin/cos reduce the argument to a residual below 2^-32 in Q62 plus Q62 cos/sin of the reduced angle.

## Compared with alternatives

The pico-sdk entry's RP2040 float routines are the same author's code: the RP2040 bootrom's mufplib.S (Copyright 2020 Mark Owen, licensed for RP2040 use only, also available under GPLv2) has the identical Q24 CORDIC sin/cos path. Pick Qfplib-M0-full for other Cortex-M0/M0+ parts (non-RP2040) where GPLv2 is acceptable; on an RP2040 use the SDK. rt_memcpy_cm from the same RT-Thread packager covers memcpy, not floating point.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none |
| **Minimum toolchain** | GNU assembler from arm-none-eabi-gcc (unified Thumb syntax, .cpu cortex-m0plus); RT-Thread SCons for the package build; compiler version used for the README numbers not documented |
| **Platforms** | ARMv6-M Cortex-M0/M0+ (soft-float calling convention); the README says it also runs, unoptimised, on Cortex-M3 and M4 |
| **Thread safety** | reentrant by design: the README states no static storage and no recursion, with statically analysable stack use |
| **Drop-in for the baseline** | partial — functionally equivalent for non-exceptional arguments, but you must call qfp_\* explicitly; no __aeabi_\* or libm aliases are exported, so a + b and sinf() in C still go to libgcc and libm |

## Gotchas

- Single-precision trig is fixed point with absolute, not relative, error: qfp_fsin calls qfp_float2fix(x, 24), which truncates the argument toward minus infinity to Q24 and clamps on overflow, then reduces it by repeated subtraction of a Q24 2\*pi and runs a Q29 CORDIC (with a '+9 fiddle factor to make sin(0)==0'). By code reading (not run), arguments below 2^-24 return 0, x = 1e-6 is evaluated as 16\*2^-24 = 9.54e-7 (about 4.6% low), and |x| of 128 or more is silently clamped instead of flagged. This is the README's 'poorer near a multiple of pi' caveat, quantified, and part of why it beats a full-range sinf.
- Calling convention: the header declares plain float/double prototypes and the assembly reads its arguments from r0-r3 (qfp_fadd unpacks r0 and r1). On an FPU core built with -mfloat-abi=hard the compiler passes floats in FPU registers, so the README's 'runs on Cortex-M4' only holds with the soft or softfp ABI.
- The RT-Thread SConscript adds \*_rvds.S for armcc and \*_iar.S for IAR, but only qfplib-m0-full_gcc.S exists, so a Keil or IAR build compiles nothing from the package and every qfp_\* call fails at link time.
- The speed table is the upstream author's approximate averages, including call overhead, for non-exceptional arguments on an LPC11U68 (Cortex-M0+) running from single-cycle flash. The GCC version, flags and math library are not stated, the argument distribution for the scientific functions is not given (the sin/cos range-reduction loop grows with |x|), no harness is in the repo, and the 'GoFast' column is inferred from an ARM7TDMI page; GoFast beats Qfplib on fsin, fcos, dsin and dcos.

## Known shortcomings

- Author's approximate cycle table with GCC version and flags unstated and no harness; the LPC11U68 is a Cortex-M0+; the sin/cos/exp/ln baseline is the toolchain libm, not libgcc; reduced range and accuracy versus libm (NaN to inf, denormal flush, trig range limits); an RT-Thread repackaging of Mark Owen's code, abandoned 2021-05-26. GPL-2.0-only.
- Code reading (not run): qfp_fsin floors its argument to Q24 and uses a Q29 CORDIC, so the error is absolute, not relative: x below 2^-24 returns 0, x = 1e-6 gives 9.54e-7 (4.6% low), and |x| &gt;= 128 is silently clamped; this quantifies the README caveat and is part of the speed gap against a full-range sinf. The SConscript globs \*_rvds.S and \*_iar.S files that do not exist, so Keil and IAR builds compile nothing and fail at link; the header has no pcs attribute, so -mfloat-abi=hard breaks calls; no __aeabi aliases, so not a drop-in; the RP2040 bootrom mufplib.S is the same author's code (identical sin path).

## Caveats and trade-offs

README table only: the Qfplib and GCC cycle counts are approximate averages over non-exceptional arguments with calling overhead included; GCC version, flags and the exact library (libgcc vs newlib libm for the scientific functions) are not stated, and no benchmark harness or C reference is in the repo (files: qfplib-m0-full_gcc.S, qfplib-m0-full.h, SConscript, README, LICENCE). Measured on a Cortex-M0+ (LPC11U68), not a plain Cortex-M0. Not a drop-in replacement for IEEE libm: NaNs become infinities, denormals are flushed to zero, single-precision trig needs arguments in -128..+128 and double-precision trig in -1024..+1024, and the scientific functions are about 1 ulp, so part of the speed gap against a full-range libm comes from reduced range and accuracy. The 'GoFast' column was inferred from an ARM7TDMI page, not measured, and is faster than Qfplib on fsin, fcos, dsin and dcos. The repo is an RT-Thread packaging of Mark Owen's Qfplib (copyright 2019-2020, quinapalus.com, not opened: host unreachable from this session), not a GitHub fork. Last commit 2021-05-26.

ARMv6-M (Cortex-M0) only, GNU assembler source (qfplib-m0-full_gcc.S) with a C header. Under 6 kbyte of program memory, no static storage, no recursion. Not drop-in IEEE-exact for exceptional arguments: README says the cycle figures are for non-exceptional arguments. GPLv2; the README points to the author for other licensing. Replacing libgcc routines needs explicit calls to the qfp_\* API.

## Maintenance

An RT-Thread packaging (4 commits, last 2021-05-26, no issues) of Mark Owen's 2019-2020 Qfplib, abandoned as a package but small enough to vendor (one .S file under 6 KB) and GPLv2-only; upstream quinapalus.com did not resolve from this session, so newer upstream releases or fixes were not checked.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's Speed table gives the author's own approximate average cycle counts against the 'GCC library' on a named NXP LPC11U68, with no harness, GCC version or flags; first-party numbers with partial methodology are tier C.
- **Verifier notes:** Every cycle count in claimed_speedup matches the README table, as does the 'double faster than GCC single' line. Corrected the hardware (LPC11U68 is a Cortex-M0+, and the .S file targets cortex-m0plus) and noted that the sin/cos/exp/ln baseline is the toolchain's math library rather than libgcc. GPL-2.0-only is confirmed by the file header and LICENCE; 17 stars, 8 forks, 4 commits, abandoned (2021-05-26).
- **Fields the verifier corrected:** `baseline`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-72 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/mysterywolf/Qfplib-M0-full>
  - <https://github.com/mysterywolf/Qfplib-M0-full/commits>
  - <https://raw.githubusercontent.com/mysterywolf/Qfplib-M0-full/HEAD/README.md>
  - <https://raw.githubusercontent.com/mysterywolf/Qfplib-M0-full/HEAD/qfplib-m0-full_gcc.S>
  - <https://raw.githubusercontent.com/mysterywolf/Qfplib-M0-full/HEAD/LICENCE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mysterywolf/Qfplib-M0-full/HEAD/README.md>
  - <https://raw.githubusercontent.com/mysterywolf/Qfplib-M0-full/HEAD/qfplib-m0-full_gcc.S>
  - <https://raw.githubusercontent.com/mysterywolf/Qfplib-M0-full/HEAD/qfplib-m0-full.h>
  - <https://raw.githubusercontent.com/mysterywolf/Qfplib-M0-full/HEAD/SConscript>
  - <https://raw.githubusercontent.com/mysterywolf/Qfplib-M0-full/HEAD/LICENCE>
  - <https://github.com/mysterywolf/Qfplib-M0-full/commits>
  - <https://github.com/mysterywolf/Qfplib-M0-full/issues?q=is%3Aissue>
  - <https://www.quinapalus.com/qfplib.html>
  - <https://raw.githubusercontent.com/raspberrypi/pico-bootrom/HEAD/bootrom/mufplib.S>
  - <https://raw.githubusercontent.com/mysterywolf/Qfplib-M0-tiny/HEAD/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mysterywolf/qfplib-m0-full`) · [data/wave13/enrich/raw/github_com_mysterywolf_qfplib_m0_full.json](../../../data/wave13/enrich/raw/github_com_mysterywolf_qfplib_m0_full.json) (enrichment confidence 0.75)

</details>
