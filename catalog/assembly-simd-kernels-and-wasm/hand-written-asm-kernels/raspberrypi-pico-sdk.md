# Raspberry Pi Pico SDK hand-coded RP2040 float and memory routines (pico_float, pico_mem_ops)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Pico SDK's ROM-backed float, double and memcpy/memset replacements for RP2040, faster than libgcc soft-float and newlib libm on Cortex-M0+.

| | |
|---|---|
| **Beats** | the compiler's soft-float library (libgcc) and C library memcpy/memset on the Cortex-M0+ cores of the RP2040 |
| **Claimed result** | The SDK itself gives no numbers: its pico_float header says the RP2040 'pico' implementations, hand coded in the bootrom and the SDK, 'are generally faster and smaller than those provided by the C compiler/library'. Independent third-party benchmark tana/pico_float_bench (README results table, single measurement, 4000 Gaussian floats via Box-Muller on a Raspberry Pi Pico): Pico SDK build at 125 MHz 49 081 us generation, 11 560 us mean, 17 100 us variance, versus the Arduino mbed core build (which, per ArduinoCore-mbed issue #325, used the GNU floating point routines instead of the RP2040 ROM routines; clock not stated) at 248 237 us, 27 350 us and 36 410 us: 5.06x, 2.37x and 2.13x (derived from page data). No numbers for pico_mem_ops. |
| **Workload** | Single-precision floating point arithmetic and math functions, and memcpy/memset, on RP2040. The SDK ships a cycle-level harness, test/pico_float_test/float_benchmark.c (and double_benchmark.c), built once per float implementation (compiler, pico, pico_vfp, pico_dcp) and timed with SysTick, but publishes no results. The third-party numbers come from tana/pico_float_bench float_bench.c: generate 4000 Gaussian floats with Box-Muller (rand, logf, sqrtf, cosf, sinf, plus one double multiply by M_PI), then compute a running mean and variance with float multiply, add and divide. |
| **Metric** | throughput |
| **Hardware** | RP2040 (dual Arm Cortex-M0+); RP2350 variants use VFP or DCP hardware instead |
| **Adoption** | 5.0k stars; the standard SDK for Raspberry Pi RP2040 and RP2350 boards |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](https://github.com/raspberrypi/pico-sdk) · [benchmark](https://github.com/tana/pico_float_bench) |

## Verdict

The only numbers are third-party and single-run: tana/pico_float_bench on a Raspberry Pi Pico took 49.1 ms to generate 4000 Box-Muller Gaussians, 11.6 ms for the running mean and 17.1 ms for the variance with the Pico SDK at 125 MHz, versus 248.2, 27.4 and 36.4 ms with the Arduino mbed core, whose build linked libgcc's GNU soft-float routines (issue #325); that is 5.06x, 2.37x and 2.13x (derived from page data), compiler and flags not stated, baseline clock unknown. The SDK itself only says its routines are 'generally faster and smaller' than the compiler's, and nothing measures pico_mem_ops.

## Use it when

- RP2040 firmware that does real soft-float work (trig, log, exp, division in control loops, sensor fusion, DSP) built with the Pico SDK: the default pico_float_pico is already on, so keep it rather than switching to compiler.
- Arduino sketches on RP2040 that are float-bound: the Arduino-Pico core (earlephilhower), which is built on the SDK, measured 44.6 ms against 248.2 ms for the Arduino mbed core on tana's Box-Muller test.
- Flash-constrained RP2040 images: the arithmetic and trig kernels live in ROM, so linking them costs only small wrappers instead of libgcc and newlib libm code.
- Code that needs fast float to fixed-point conversions with saturation (float2fix, fix2float, float2int rounding towards minus infinity).
- RP2350 Arm builds that want hardware single precision plus faster scientific functions (pico_vfp, the default there), or float without enabling the FPU in interrupts and tasks (pico_dcp).

## Skip it when

- Code that needs strict IEEE 754 behaviour: the ROM routines and comparisons flush denormals to zero ('clear mantissa if denormal'), NaNs are not propagated unless PICO_FLOAT_PROPAGATE_NANS=1, and fmaf is computed through double precision with double rounding (the source says 'not exact').
- Trig on large arguments: the ROM sin/cos/tan only accept -128 &lt; x &lt; 128, and the SDK reduces larger inputs with remainderf by the float-rounded 2\*pi (0x40c90fdb), so the phase error grows linearly with |x| (about 2.8e-4 rad at 1e4 and 0.028 rad at 1e6, derived from the constant).
- Any chip other than an RP2-series part: the RP2040 kernels are in mask ROM under a licence that permits use 'solely on a Raspberry Pi RP2040 device' (or GPLv2 from the author), so they cannot be copied to another Cortex-M0+; use Qfplib-M0 there.
- RP2350 RISC-V (Hazard3) builds: only __addsf3, __subsf3 and __mulsf3 are replaced; everything else is the compiler's soft-float.
- memcpy/memset tuning: pico_mem_ops has no published numbers anywhere, and on RP2350 it defaults to the compiler's memcpy (the SDK warns the compiler memcpy cannot be used for unaligned copies in peripheral space).

## How it is fast

On RP2040 the SDK wrappers tail-call through a function table (sf_table) into hand-written Cortex-M0+ Thumb assembly in the chip's mask ROM (Mark Owen's mufplib in pico-bootrom-rp2040), which runs without XIP flash cache misses and costs no flash. Division uses the RP2040 SIO hardware integer divider, square root uses a Newton-Raphson reciprocal estimate with a final remainder step for correct rounding, and sin, cos and sincos use fixed-point CORDIC rotation. The rest of the math library (asinf, powf, hypotf and others) is C in float_math.c built on those primitives, partly through double-precision intermediates. On RP2350 the Arm build inlines VFP (FPU) instructions plus custom scientific functions (pico_vfp) or uses the RP2350 double coprocessor (pico_dcp).

## Compared with alternatives

Pick it over Qfplib-M0-full (same author, Mark Owen; portable Cortex-M0 float library with its own cycle table against GCC) whenever the target is an RP2040: the equivalent kernels are already in ROM, cost no flash and come wired into the SDK; on any other Cortex-M0/M0+ use Qfplib. For memcpy on non-RP2040 Cortex-M parts, rt_memcpy_cm at least publishes a measurement, which pico_mem_ops does not.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake INTERFACE libraries pico_float, pico_double and pico_mem_ops inside the Pico SDK, linked into the firmware through pico_stdlib) |
| **Dependencies** | Pico SDK (pico_bootrom, hardware_divider), the RP2040 bootrom at runtime; build needs CMake, Python 3 and an arm-none-eabi cross compiler (GCC or Clang) |
| **Minimum toolchain** | CMake 3.13; arm-none-eabi GCC (minimum version not documented); RP2350 RISC-V needs a separate GCC 14 prebuilt toolchain |
| **Platforms** | RP2040 (Cortex-M0+, ROM routines); RP2350 Arm Cortex-M33 (VFP or DCP variants); RP2350 RISC-V (single-precision add, sub and mul only) |
| **Thread safety** | Stateless routines. __aeabi_fdiv saves and restores the per-core SIO divider state when it is dirty, so it is safe from interrupts; building with PICO_DIVIDER_DISABLE_INTERRUPTS=1 instead disables interrupts around the call. Otherwise not documented. |
| **Drop-in for the baseline** | partial — transparent inside a Pico SDK build (float operators and math.h calls are rerouted by --wrap), but not usable outside the SDK or on non-RP2 chips, and results differ from libgcc and newlib at edge cases (denormals, NaNs, large trig arguments) |

## Gotchas

- Harness flaw behind the only numbers: tana/pico_float_bench compares a Pico SDK build at 125 MHz with the whole Arduino mbed core stack (Mbed OS RTOS, unknown clock per ArduinoCore-mbed issue #221, unstated compiler and flags, heap array via malloc and micros() instead of a stack array and get_absolute_time), one run each. A same-stack baseline would be the SDK built with pico_set_float_implementation(target compiler); that was never measured. The Arduino-Pico row (SDK float code at 133 MHz: 44,557 / 10,420 / 15,168 us, about 47.4 / 11.1 / 16.1 ms scaled to 125 MHz) matches the SDK row, which supports blaming the mbed gap on the float routines but does not isolate their speedup.
- The benchmark's phases do not time what their names suggest: generation includes two newlib rand() calls per pair and a double-precision multiply (2 \* M_PI \* random2 promotes to double: f2d, dmul, d2f), so pico_double is timed too; the mean and variance loops are dominated by two size_t-to-float conversions and one float divide per element, not by multiply and add.
- The SDK's own test/pico_float_test/float_benchmark.c (one SysTick-timed call per input, averaged over 4 inputs, every implementation built copy_to_ram with PICO_FLOAT_IN_RAM=1) is a fair like-for-like harness, but its inputs include edge values (sinf/cosf at 1.6e15 take the remainderf path, logf(0)) and no results are published.
- RP2350 regression: with SDK 2.1.1 and the default pico_vfp, sinf(1.565) returned -0.547 and cosf -0.837 (issue #2406, layout-dependent); fixed through PR #2429 for 2.2.0, so pin 2.2.0 or later on RP2350.

## Known shortcomings

- Tier C rests on the independent tana/pico_float_bench run (5.06x/2.37x/2.13x derived against the Arduino mbed core build, which used GNU soft-float): one run, baseline clock unknown, whole stack compared, no numbers for pico_mem_ops; the repo's own test/pico_float_test/float_benchmark.c publishes no results.
- The only numbers are tana/pico_float_bench, one run, Pico SDK at 125 MHz against the whole Arduino mbed stack (RTOS, clock unknown, malloc array, micros()); the fair baseline (pico_set_float_implementation compiler) was never measured. The Arduino-Pico row is SDK float at 133 MHz (44,557 us, about 47.4 ms scaled), matching the SDK row, so the gap is the float routines but the speedup is not isolated; the generation phase also times rand() and a double multiply, and the mean/variance phases are mostly size_t-to-float conversion plus fdiv. The RP2040 kernels sit in mask ROM (Mark Owen's mufplib) under a licence 'solely on a Raspberry Pi RP2040 device' or GPLv2, so 'copyable' covers only the SDK shims. Not IEEE: denormals flushed, NaNs not propagated, fmaf double-rounded, sinf/cosf at |x| &gt;= 128 reduced by a float 2\*pi; RP2350 sinf/cosf bug in 2.1.1 (#2406) fixed in 2.2.0. No pico_mem_ops numbers.

## Caveats and trade-offs

The SDK's own performance statement is qualitative; the RP2040 datasheet cycle tables were unreachable from this session (datasheets.raspberrypi.com did not resolve). The third-party comparison is a single measurement, states no compiler or flags, does not know the mbed core's clock (it cites ArduinoCore-mbed issue #221, F_CPU undefined), and compares whole software stacks (Pico SDK versus the RTOS-based Arduino mbed core), not only the float routines. ArduinoCore-mbed issue #325 (mbed core placed GNU float routines in RAM instead of using the ROM routines) was closed as completed on 2021-11-08 after a patch, although the benchmark README says the situation was similar in November 2023; when the 248 ms row was measured is not stated. The workload multiplies by M_PI in double precision, so it also exercises double routines. Part of the RP2040 float code lives in the chip bootrom (the header says 'from the bootrom and the SDK'), not in this SDK alone, and the routines do not support all features of a fully compliant IEEE implementation. On RP2350 the SDK uses VFP or DCP hardware instead. No numbers were found for pico_mem_ops.

RP2-series only. The RP2040 software float routines are not fully IEEE-compliant ('usually fine for the majority of cases'). On RP2350 the fastest option relies on the Arm FPU or the double-precision coprocessor rather than hand-written software routines.

## Maintenance

Actively maintained (release 2.3.1 on 2026-09-04, BSD-3-Clause, the standard SDK for RP2040 and RP2350), but 'copyable' covers only the SDK wrappers and float_math.c: the RP2040 arithmetic and trig kernels that do the work live in mask ROM under an RP2040-only licence, and the evidence is a whole-stack comparison, so tier C is right.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D: an independent third-party benchmark (tana/pico_float_bench, public code float_bench.c, RP2040 at 125 MHz) times the Pico SDK float routines against an Arduino mbed core build that linked the GNU soft-float routines, but it is a single run with no compiler or flags, an unknown baseline clock and a whole-stack baseline, so numbers without full methodology stay at C; the SDK's own harness test/pico_float_test/float_benchmark.c publishes no results.
- **Verifier notes:** Record said the repo has no benchmark for these routines; it does (test/pico_float_test/float_benchmark.c, per-implementation SysTick timing) but publishes no results. Found independent numbers in tana/pico_float_bench (5.06x generation, 2.37x mean, 2.13x variance, derived) and raised the tier from D to C. Shortcomings to record: whole-stack baseline with unknown clock, single run, no compiler or flags, part of the code is in the RP2040 bootrom, not fully IEEE compliant, no numbers for pico_mem_ops.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-115 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_float/include/pico/float.h>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_mem_ops/include/pico/mem_ops.h>
  - <https://github.com/raspberrypi/pico-sdk>
  - <https://github.com/raspberrypi/pico-sdk/commits/master>
  - <https://github.com/raspberrypi/pico-sdk/tree/master/test>
  - <https://github.com/raspberrypi/pico-sdk/tree/master/test/pico_float_test>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/test/pico_float_test/float_benchmark.c>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/master/test/pico_float_test/CMakeLists.txt>
  - <https://github.com/raspberrypi/pico-sdk/releases/tag/2.0.0>
  - <https://github.com/tana/pico_float_bench>
  - <https://raw.githubusercontent.com/tana/pico_float_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/tana/pico_float_bench/HEAD/float_bench.c>
  - <https://raw.githubusercontent.com/tana/pico_float_bench/HEAD/CMakeLists.txt>
  - <https://github.com/arduino/ArduinoCore-mbed/issues/325>
  - <https://github.com/arduino/ArduinoCore-mbed/issues/221>
- **Sources the enricher read:**
  - <https://github.com/raspberrypi/pico-sdk>
  - <https://github.com/raspberrypi/pico-sdk/releases>
  - <https://github.com/raspberrypi/pico-sdk/issues?q=is%3Aissue%20pico_float%20OR%20sinf%20OR%20fdiv%20OR%20%22float%22%20bug>
  - <https://github.com/raspberrypi/pico-sdk/issues/2406>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/README.md>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_float/include/pico/float.h>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_float/CMakeLists.txt>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_float/float_aeabi_rp2040.S>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_float/float_math.c>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_float/float_init_rom_rp2040.c>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_float/float_v1_rom_shim_rp2040.S>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_mem_ops/include/pico/mem_ops.h>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_mem_ops/CMakeLists.txt>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/src/rp2_common/pico_mem_ops/mem_ops_aeabi.S>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/test/pico_float_test/float_benchmark.c>
  - <https://raw.githubusercontent.com/raspberrypi/pico-sdk/HEAD/test/pico_float_test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/raspberrypi/pico-bootrom-rp2040/HEAD/README.md>
  - <https://raw.githubusercontent.com/raspberrypi/pico-bootrom-rp2040/HEAD/bootrom/mufplib.S>
  - <https://raw.githubusercontent.com/tana/pico_float_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/tana/pico_float_bench/HEAD/float_bench.c>
  - <https://raw.githubusercontent.com/tana/pico_float_bench/HEAD/CMakeLists.txt>
  - <https://github.com/tana/pico_float_bench/tree/main/float_bench_arduino>
  - <https://raw.githubusercontent.com/tana/pico_float_bench/main/float_bench_arduino/float_bench_arduino.ino>
  - <https://github.com/arduino/ArduinoCore-mbed/issues/325>
  - <https://github.com/arduino/ArduinoCore-mbed/issues/221>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/raspberrypi/pico-sdk`) · [data/wave13/enrich/raw/github_com_raspberrypi_pico_sdk.json](../../../data/wave13/enrich/raw/github_com_raspberrypi_pico_sdk.json) (enrichment confidence 0.65)

</details>
