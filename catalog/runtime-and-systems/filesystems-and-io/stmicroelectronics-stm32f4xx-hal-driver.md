# STM32 Low Layer (LL) driver library

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> ST's Low Layer (LL) drivers: static inline register-access calls that replace HAL calls such as HAL_GPIO_WritePin.

| | |
|---|---|
| **Beats** | STM32 HAL drivers (HAL_GPIO_WritePin) |
| **Claimed result** | No valid numeric win: the tutorial's LL set/reset rate (1.09 MHz) against HAL_GPIO_WritePin (806 kHz), about 1.35x (derived from page data), comes from an unoptimised build in which the static inline LL functions were not inlined; optimised, LL compiles to the same single store as direct register access. Toggle rates were equal (625 kHz). |
| **Workload** | Third-party GPIO pin toggle loop at 72 MHz: HAL_GPIO_WritePin set/reset versus LL_GPIO_SetOutputPin/LL_GPIO_ResetOutputPin versus HAL_GPIO_TogglePin versus LL_GPIO_TogglePin versus direct BSRR/BRR register writes, toggle frequency measured on PC9 of a NUCLEO-F334R8 (tutorial) and on PA8 in the linked STM32F334_HAL_LL_REG_GPIO project (each variant commented in or out of one while loop). |
| **Metric** | throughput |
| **Hardware** | Tutorial: NUCLEO-F334R8 (STM32F334R8, Cortex-M4F), 8 MHz external clock with PLLMUL 9, 72 MHz system clock. Linked repo's .ioc targets STM32F334C8Tx with a 72 MHz PLL clock. |
| **Compiler and flags** | Not stated. The linked .ioc names STM32CubeIDE as the toolchain (STM32Cube FW_F3 V1.10.0, HAL full assert off); the optimization level is not given and no IDE build configuration is in the repo. |
| **Adoption** | 209 stars, 76 forks (STM32F4 HAL/LL driver repository); the STM32Cube MCU component hal_driver for the STM32F4 series |
| **Last commit** | 2026-06-05 |
| **Links** | [repository](https://github.com/STMicroelectronics/stm32f4xx_hal_driver) · [benchmark](https://github.com/VictorTagayun/Basic_DSMPS_Tutorial) |

## Verdict

A hobby tutorial (VictorTagayun/Basic_DSMPS_Tutorial) toggled PC9 on a NUCLEO-F334R8 at 72 MHz: LL_GPIO_SetOutputPin/ResetOutputPin reached 1.09 MHz against 806 kHz for HAL_GPIO_WritePin (about 1.35x, derived from page data), the two TogglePin calls tied at 625 kHz, and direct BSRR/BRR writes reached 2.94 MHz. Its linked STM32F334 project (PA8) gives 1.18 MHz against 878 kHz, tied toggles at 922 kHz and 5.54-6.00 MHz for register writes; the compiler and optimization level are not stated, and the code was the STM32F3 driver, not this F4 repository.

## Use it when

- Pin set/reset in interrupt handlers, bit-banged protocols or timing-critical loops on STM32F4 where a HAL call per edge is measurable.
- Projects that want register-level code size and speed but keep named, documented calls and STM32CubeMX code generation instead of raw register masks.
- Mixed firmware: HAL for complex stacks (USB, Ethernet) and LL for GPIO, timers and other hot peripheral accesses.
- Flash-constrained parts, where avoiding HAL handles and state machines shrinks the image.

## Skip it when

- Unoptimized Debug builds: the inline calls are not inlined, and the measured LL gain over HAL shrinks to about 1.35x while plain register writes stay 2.7x to 5x faster.
- Pin toggling: LL_GPIO_TogglePin and HAL_GPIO_TogglePin both read ODR and write BSRR, and both sources measured the same toggle frequency for the two.
- Code that must move across STM32 series: ST's release notes say LL is not fully portable across families, unlike HAL.
- When you need HAL's parameter checks, timeouts, locking and error callbacks; LL leaves setup order, clock enabling and error paths to the caller.

## How it is fast

LL_GPIO_SetOutputPin is __STATIC_INLINE WRITE_REG(GPIOx-&gt;BSRR, PinMask) and ResetOutputPin writes PinMask &lt;&lt; 16 to BSRR, so once the compiler inlines them a pin write is one store, the same code as a hand-written BSRR write. HAL_GPIO_WritePin does the same single store behind a branch but lives out of line in stm32f4xx_hal_gpio.c, so each call pays a call and return unless LTO inlines it. The release notes describe LL as inline functions for direct and atomic register access with no handles or state.

## Compared with alternatives

Pick LL over the direct BSRR register entry (Packt Bare-Metal-Embedded-C-Programming) when you want the same single-store pin write with named calls, CubeMX generation and ST maintenance; once inlined the two compile to the same store. The other filesystems-and-io siblings (liburing, SPDK, mmap replacements) solve host file and block I/O and do not apply to microcontroller pins.

## Integration

| | |
|---|---|
| **Form** | source-drop (GPIO output calls are header-only static inline functions in Inc/stm32f4xx_ll_gpio.h; init helpers in Src/stm32f4xx_ll_gpio.c) |
| **Dependencies** | CMSIS Core and CMSIS Device F4 headers in matching versions (the README calls a consistent CMSIS/HAL version set crucial) |
| **Minimum toolchain** | not documented in the files read; plain C with static inline functions |
| **Platforms** | STM32F4 series only; other STM32 series have their own HAL-LL driver repositories with the same LL GPIO API names |
| **Thread safety** | Set and reset are single BSRR stores and safe against interrupts; TogglePin reads ODR then writes BSRR, so concurrent toggles of the same pin can race |
| **Drop-in for the baseline** | partial — one LL call per HAL_GPIO_WritePin call, but different function names and arguments, and set/reset are separate functions |

## Gotchas

- The speedup depends on inlining: the tutorial's LL set/reset loop ran at 1.09 MHz and the linked repo's at 1.18 MHz while the identical BSRR/BRR store loop ran at 2.94 MHz and 5.54-6.00 MHz, which points to builds where the static inline functions were not inlined (optimization level unstated).
- The measurements used STM32F334 parts with STM32Cube FW_F3, not this F4 driver; on F3 LL_GPIO_ResetOutputPin writes BRR, on F4 it writes the upper half of BSRR.
- The two third-party sources disagree by about 2x on the plain register loop, and the linked repo shows the same register code at 5.54 MHz in a HAL-generated project and 6.00 MHz in an LL-generated one, so build settings differed between runs.
- LL_GPIO_Init and the other init helpers exist only when USE_FULL_LL_DRIVER is defined.

## Known shortcomings

- Measured on STM32F3 parts (F334R8 tutorial, F334C8 .ioc), not the F4 driver repo; optimisation level not stated and register-loop rates (2.94 vs 5.54-6.00 MHz) show the builds differed, a Debug build is plausible. ST publishes no numbers. LL set/reset beats HAL_GPIO_WritePin by about 1.35x; toggle equal. filesystems-and-io is a poor fit for GPIO (no embedded-HAL category exists).
- Enricher retier C to D: the static inline LL calls ran at a third of the direct-register rate, so the build was unoptimised and the 1.35x over HAL is a Debug artifact; register-loop rates drift between projects (5.54 vs 6.00 MHz).

## Caveats and trade-offs

The speed numbers are third-party, from a hobby tutorial (Basic_DSMPS_Tutorial, 5 stars) and its linked test repo, not a controlled study, and from the STM32F3 family (STM32F334 with STM32Cube FW_F3), not the F4 driver repo this record points at; the LL GPIO API is shared across families. Compiler optimization level is not stated anywhere (the .ioc says STM32CubeIDE, HAL assert off, PA8 high speed; no build config committed). The two sources disagree on the plain register loop (2.94 MHz on PC9 versus 5.54-6.00 MHz on PA8 for the same BSRR/BRR writes), and the linked repo's comments show the same register code at 5.54 MHz in a HAL-generated project and 6.00 MHz in an LL-generated one, so build settings differed between runs and a low-optimization (Debug) build is plausible for the tutorial figures. The gain is only for separate set/reset calls (about 1.35x); TogglePin shows no LL gain, and direct register writes beat both APIs by 2.7x to 5x. ST's release notes describe the LL drivers as 'optimized and one shot services' without numbers; the repository README makes no speed or footprint claim. Code-size evidence exists only as forum snippets not opened (community.st.com and eevblog.com unreachable): a GPIO plus LPUART build reportedly 10128 bytes with HAL versus 5848 bytes with LL, chip and flags unstated. [retier] Enricher: the same direct-register code ran at 5.54 vs 6.00 MHz across the two projects, showing build drift; measured on STM32F3 parts (F334R8, F334C8), not the F4 driver; the tutorial has no licence.

LL is closer to the registers than HAL: no handle structures, no state machine, little or no parameter validation and no timeout or error handling in the register-level calls, so peripheral setup order, clock enabling and error paths are the caller's job. LL is not offered for every peripheral (ST's driver manuals reportedly say it is not provided where optimized access is not a key feature, USB for example; search snippet only) and code is less portable across STM32 families than HAL.

## Maintenance

Actively maintained by ST (last commit 2026-06-05, release notes at V1.8.5 of 23 July 2025, 1 open issue), BSD-3-Clause, and normally pulled in through STM32CubeMX or the STM32CubeF4 package rather than vendored by hand.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** Third-party hobby tutorial (5-star repo) whose toggle loop code is public (linked VictorTagayun/STM32F334_HAL_LL_REG_GPIO Src/main.c) and whose board and clock are stated, but the optimization flags are not, and it is not a well-known independent suite, so C rather than A or B.
- **Retiered** C to D: C to D: LL_GPIO_SetOutputPin/ResetOutputPin are static inline single BSRR (F3: BRR) stores, the same instruction as the direct-register loop, yet LL measured 1.09/1.18 MHz against 2.94/5.54-6.00 MHz for the register loop, so the LL calls were not inlined: an unoptimised build at an unstated -O level. The only numeric win (about 1.35x over HAL) is a Debug-build artifact, not LL speed (-O0 downgrade precedent; no valid measurement).
- **Verifier notes:** Numbers on the tutorial page match the record; linked repo main.c gives a second, consistent set (LL set/reset about 1.34x over HAL_GPIO_WritePin, toggle equal). Category filesystems-and-io looks wrong for an MCU GPIO driver layer (closer to an embedded/runtime category); consider a category override, and consider pointing repo_url at STMicroelectronics/stm32f3xx_hal_driver since the measurement used F3 parts (not checked here).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-67 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/VictorTagayun/Basic_DSMPS_Tutorial>
  - <https://github.com/VictorTagayun/STM32F334_HAL_LL_REG_GPIO>
  - <https://raw.githubusercontent.com/VictorTagayun/STM32F334_HAL_LL_REG_GPIO/HEAD/Src/main.c>
  - <https://raw.githubusercontent.com/VictorTagayun/STM32F334_HAL_LL_REG_GPIO/HEAD/STM32F334_HAL_LL_REG_GPIO.ioc>
  - <https://github.com/STMicroelectronics/stm32f4xx_hal_driver>
  - <https://github.com/STMicroelectronics/stm32f4xx_hal_driver/commits>
  - <https://raw.githubusercontent.com/STMicroelectronics/stm32f4xx_hal_driver/HEAD/Release_Notes.html>
- **Sources the enricher read:**
  - <https://github.com/STMicroelectronics/stm32f4xx_hal_driver>
  - <https://github.com/STMicroelectronics/stm32f4xx_hal_driver/commits>
  - <https://github.com/STMicroelectronics/stm32f4xx_hal_driver/issues?q=is%3Aissue+LL>
  - <https://raw.githubusercontent.com/STMicroelectronics/stm32f4xx_hal_driver/HEAD/README.md>
  - <https://raw.githubusercontent.com/STMicroelectronics/stm32f4xx_hal_driver/HEAD/Inc/stm32f4xx_ll_gpio.h>
  - <https://raw.githubusercontent.com/STMicroelectronics/stm32f4xx_hal_driver/HEAD/Src/stm32f4xx_hal_gpio.c>
  - <https://raw.githubusercontent.com/STMicroelectronics/stm32f4xx_hal_driver/HEAD/Release_Notes.html>
  - <https://raw.githubusercontent.com/STMicroelectronics/stm32f3xx_hal_driver/HEAD/Inc/stm32f3xx_ll_gpio.h>
  - <https://github.com/VictorTagayun/Basic_DSMPS_Tutorial>
  - <https://raw.githubusercontent.com/VictorTagayun/STM32F334_HAL_LL_REG_GPIO/HEAD/Src/main.c>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/stmicroelectronics/stm32f4xx_hal_driver`) · [data/wave11/enrich/raw/github_com_stmicroelectronics_stm32f4xx_hal_driver.json](../../../data/wave11/enrich/raw/github_com_stmicroelectronics_stm32f4xx_hal_driver.json) (enrichment confidence 0.6)

</details>
