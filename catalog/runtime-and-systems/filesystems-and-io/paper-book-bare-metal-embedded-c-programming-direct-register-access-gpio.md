# Direct register access (BSRR) in bare-metal C, Packt Bare-Metal-Embedded-C-Programming companion code

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Drive STM32 GPIO pins with single stores to the BSRR register instead of calling HAL_GPIO_WritePin.

| | |
|---|---|
| **Beats** | STM32 HAL GPIO driver call HAL_GPIO_WritePin |
| **Claimed result** | BSRR register writes give a shorter pulse than HAL_GPIO_WritePin: 40.80 ns vs 396.0 ns at -O2 and -O3 (9.7x), 61.60 ns vs 418.0 ns at -O1 (6.8x), 61.60 ns vs 896.0 ns at -O0 (14.5x); ratios as printed in the benchmark README table. The book itself gives no timing, only qualitative text and a code-size comparison. |
| **Workload** | Third-party oscilloscope measurement of a PC8 set-then-reset loop on an STM32F072 Discovery (Cortex-M0, 48 MHz): two HAL_GPIO_WritePin calls versus two direct GPIOC-&gt;BSRR writes, pulse width read at four optimization levels. |
| **Metric** | latency |
| **Hardware** | STM32F072RBT6 (Arm Cortex-M0) on 32F072BDISCOVERY, HCLK 48 MHz from HSE through PLL, 1 flash wait state, PC8 set to high speed; OWON SDS210S oscilloscope (100 MHz, 1 GS/s) |
| **Compiler and flags** | Keil uVision5 with Arm Compiler 6 (AC6), -O0, -O1, -O2 and -O3 compared; other flags not stated (benchmark repo, not the book) |
| **Adoption** | 317 stars (companion repository) |
| **Last commit** | 2025-12-15 |
| **Links** | [repository](https://github.com/PacktPublishing/Bare-Metal-Embedded-C-Programming) · [benchmark](https://github.com/dotsolvit/stm32f0-gpio-speed-comparison) |

## Verdict

A third-party student project (dotsolvit/stm32f0-gpio-speed-comparison) toggled PC8 on an STM32F072 Discovery board at 48 MHz, built with Keil and Arm Compiler 6, and measured the high-pulse width with an OWON SDS210S oscilloscope: two HAL_GPIO_WritePin calls gave 396 ns at -O2/-O3 versus 40.8 ns for two GPIOC-&gt;BSRR stores (9.7x), 418 versus 61.6 ns at -O1 and 896 versus 61.6 ns at -O0. The book and its repository contain no timing; the measurement is of the technique on a different chip, not of the book's code.

## Use it when

- Bit-banged protocols, chip-select or strobe lines and scope/debug markers where the gap between two pin edges must be a few CPU cycles.
- Interrupt handlers and tight control loops on STM32 parts that already use CMSIS device headers, where a HAL call per pin edge is measurable.
- Setting or clearing pins from both main code and ISRs: a plain BSRR store is atomic, unlike ODR |= or ODR ^= read-modify-write sequences.
- Learning or auditing exactly what the hardware does, or very small firmware images where HAL is not linked at all.

## Skip it when

- Code that must move across STM32 families or vendors: register names, bit positions and clock-enable registers differ (the book targets STM32F411, the benchmark STM32F072).
- When LL (LL_GPIO_SetOutputPin is a static inline BSRR write) or HAL built with -O2 and LTO already meets the timing; the gap is mostly call overhead that inlining removes.
- Peripheral setup and error handling: direct writes skip HAL's clock enabling, parameter checks, state machines and timeouts, so mistakes fail silently.
- Workloads where a pin write is a tiny fraction of the time (pins toggled every few milliseconds); the saving is a few hundred nanoseconds per call.

## How it is fast

BSRR is a write-only set/reset register, so one store changes the pin atomically with no read-modify-write and no function call. In the measured loop the HAL cost is call overhead, not work: the F0 HAL_GPIO_WritePin body is just a branch and one store to BSRR or BRR (assert_param compiles to nothing with USE_FULL_ASSERT off), but it lives in a separate driver file and the Keil project has LTO off, so each write pays a call and return. The 40.8 ns BSRR pulse is about 2 cycles at 48 MHz, which the benchmark author reads as the Cortex-M0 store timing limit.

## Compared with alternatives

Pick raw BSRR writes over the STM32 Low Layer (LL) entry only when you want no ST driver code at all; LL_GPIO_SetOutputPin compiles to the same single BSRR store when inlined, so LL gives the same edge timing with named calls and CubeMX support. The other filesystems-and-io siblings (liburing, SPDK, mmap replacements) solve host file and block I/O and do not apply to microcontroller pins.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CMSIS device header for the target MCU (the book repo ships chip_headers/CMSIS; the benchmark uses STM32CubeMX-generated CMSIS and HAL for setup) |
| **Minimum toolchain** | Any C99 Arm compiler; book code built with the GNU Arm Embedded Toolchain in STM32CubeIDE, benchmark with Keil uVision5 and Arm Compiler 6 |
| **Platforms** | STM32 MCUs with a BSRR GPIO register (book: STM32F411 Cortex-M4; benchmark: STM32F072 Cortex-M0); register layout is per family |
| **Thread safety** | A single BSRR store is atomic with respect to interrupts; ODR read-modify-write forms used elsewhere in the book are not |
| **Drop-in for the baseline** | partial — replaces HAL_GPIO_WritePin calls one for one, but pin masks, clock enabling and pin configuration must be written by hand |

## Gotchas

- The book's own GPIO driver (Chapter7-GpioInput/Src/gpio.c) writes GPIOA-&gt;BSRR |= LED_BS5, which adds a needless read of a write-only register; use a plain store as in the benchmark. Chapters 3 and 6 toggle with ODR ^=, which is not interrupt-safe.
- The benchmark's HAL figures are call overhead across a translation-unit boundary with LTO off; its README attributes the -O0 gap to parameter validation and says HAL is inlined at -O2, but asserts are compiled out and HAL_GPIO_WritePin is a separate function in a non-LTO build.
- Variants are switched by commenting code in main.c (the committed file has the HAL block active) and the Keil project stores a single optimization setting, so each table row was a separate hand-edited build; no build logs or disassembly are committed.
- The book examples use empty for loops as delays (for(int i=0;i&lt;100000;i++){}), which an optimizing compiler may delete; use SysTick or a timer instead.

## Known shortcomings

- dotsolvit README table (9.7x at -O2/-O3) compares register writes against STM32 HAL, which is not a filesystems-and-io baseline; USE_FULL_ASSERT off and LTO off, so the README's 'HAL inlined' claim is unlikely; the -O0 row is a debug build. filesystems-and-io is a poor fit for GPIO (no embedded-HAL category exists).
- Enricher: the measured gap is HAL call overhead only (asserts off, HAL_GPIO_WritePin out of line, LTO off), not parameter checks as the README says; hand-edited builds per row with no logs or disassembly; the benchmark repo has no licence.

## Caveats and trade-offs

The numbers are NOT from the book or its repo: the book measures no time (only code size of the same GPIO setup in HAL, LL, C and assembly on STM32F411 at -O0, not in the repo). They come from an unrelated student repo (dotsolvit/stm32f0-gpio-speed-comparison, 0 stars, no LICENSE file in its top-level listing, commits 2026-09-22 to 2026-09-24) measuring the same technique on a different chip (STM32F072 Cortex-M0, not the book's STM32F411 Cortex-M4). Its main.c loop confirms the code (HAL_GPIO_WritePin(GPIOC, GPIO_PIN_8, ...) versus GPIOC-&gt;BSRR = GPIO_BSRR_BS_8 / GPIO_BSRR_BR_8, switched by commenting; the committed main.c has the HAL block active) and its method meets tier A, so the tier is capped at B because it measures the technique on another chip rather than the book repo's code. The -O0 row (14.5x) is a debug build; use the -O2/-O3 rows (9.7x). The HAL baseline is fair on parameter checks (stm32f0xx_hal_conf.h leaves USE_FULL_ASSERT off), but the README's claim that HAL is inlined at -O2 is unlikely: the Keil project has LTO off (v6Lto 0) and HAL_GPIO_WritePin lives in a separate driver file, so each HAL write is a real call. The measured pulse width is a toggle-loop artifact: at -O2 and -O3 the BSRR pulse train is non-uniform (grouped pulses, gap every 4 cycles, author attributes it to loop unrolling and flash prefetch, unverified) and ringing is visible below 100 ns. The loop only measures two GPIO writes, not a realistic firmware workload. The book repo's own GPIO driver (Chapter7-GpioInput/Src/gpio.c) writes GPIOA-&gt;BSRR |= LED_BS5, a read-modify-write form, not the plain store that was benchmarked. A second independent data point from a tutorial page (VictorTagayun/Basic_DSMPS_Tutorial, NUCLEO-F334R8 at 72 MHz, optimization level not stated): HAL_GPIO_WritePin loop 806 kHz versus GPIOC-&gt;BSRR/BRR 2.94 MHz toggle frequency. LL is not compared in either source. Chapter 2 and 6 comparison code (HAL, LL, C, assembly) is not visible in the repo folder listings opened (Chapter1, Chapter2, Chapter7).

Direct register writes tie the code to one MCU family and its reference manual, skip the HAL parameter checks and state handling (no error reporting, no clock enabling, no init helpers) and are harder to port than HAL or LL calls. The book's own chapters (Chapter3, Chapter6, Chapter7 and later) are register-level for GPIO, timers, ADC, UART, SPI, I2C, DMA, with its own linker script, startup file and CMSIS headers.

## Maintenance

The book repository (MIT, 317 stars, last commit 2025-12-15, 4 open issues about errata and tooling) is teaching code for STM32F411, small enough to copy; the benchmark repository has no license file and 0 stars, so cite its numbers but do not copy its code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party measurement: dotsolvit/stm32f0-gpio-speed-comparison README table gives HAL versus BSRR pulse widths (896.0/61.60, 418.0/61.60, 396.0/40.80, 396.0/40.80 ns at -O0 to -O3, ratios printed) with code (Core/Src/main.c), Arm Compiler 6 and STM32F072RBT6; that method meets A, but it measures the technique on another chip, not the book repo's code (which uses a read-modify-write BSRR form on STM32F411), so B.
- **Verifier notes:** Numbers, hardware, compiler and ratios match the benchmark README exactly; metadata (MIT, 317 stars, last commit 2025-12-15) confirmed. baseline_in_list set false: STM32 HAL is not among the filesystems-and-io baselines (POSIX read/write, mmap, io_uring); the category itself is a poor fit for a GPIO technique, consider a category override.
- **Fields the verifier corrected:** `baseline_in_list`, `caveats`
- **Shortcomings recorded by:** verifier batch-66 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/dotsolvit/stm32f0-gpio-speed-comparison>
  - <https://github.com/dotsolvit/stm32f0-gpio-speed-comparison/commits>
  - <https://github.com/dotsolvit/stm32f0-gpio-speed-comparison/tree/main/MDK-ARM>
  - <https://raw.githubusercontent.com/dotsolvit/stm32f0-gpio-speed-comparison/HEAD/README.md>
  - <https://raw.githubusercontent.com/dotsolvit/stm32f0-gpio-speed-comparison/HEAD/Core/Src/main.c>
  - <https://raw.githubusercontent.com/dotsolvit/stm32f0-gpio-speed-comparison/HEAD/Core/Inc/stm32f0xx_hal_conf.h>
  - <https://raw.githubusercontent.com/dotsolvit/stm32f0-gpio-speed-comparison/HEAD/MDK-ARM/stm32f0-gpio-speed-comparison.uvprojx>
  - <https://github.com/PacktPublishing/Bare-Metal-Embedded-C-Programming>
  - <https://github.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/commits>
  - <https://github.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/tree/main/Chapter7-GpioInput>
  - <https://github.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/tree/main/Chapter2/2_RegisterManipulation-old>
  - <https://raw.githubusercontent.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/HEAD/Chapter7-GpioInput/Src/gpio.c>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Bare-Metal-Embedded-C-Programming>
  - <https://github.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/issues>
  - <https://github.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/tree/main/Chapter6/6_StructureAccess>
  - <https://github.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/tree/main/Chapter3/2_RegisterManipulation>
  - <https://raw.githubusercontent.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/HEAD/Chapter7-GpioInput/Src/gpio.c>
  - <https://raw.githubusercontent.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/HEAD/Chapter7-GpioInput/Src/main.c>
  - <https://raw.githubusercontent.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/HEAD/Chapter6/6_StructureAccess/Src/main.c>
  - <https://raw.githubusercontent.com/PacktPublishing/Bare-Metal-Embedded-C-Programming/HEAD/Chapter3/2_RegisterManipulation/Src/main.c>
  - <https://github.com/dotsolvit/stm32f0-gpio-speed-comparison>
  - <https://raw.githubusercontent.com/dotsolvit/stm32f0-gpio-speed-comparison/HEAD/README.md>
  - <https://raw.githubusercontent.com/dotsolvit/stm32f0-gpio-speed-comparison/HEAD/Core/Src/main.c>
  - <https://raw.githubusercontent.com/dotsolvit/stm32f0-gpio-speed-comparison/HEAD/Core/Inc/stm32f0xx_hal_conf.h>
  - <https://raw.githubusercontent.com/dotsolvit/stm32f0-gpio-speed-comparison/HEAD/Drivers/STM32F0xx_HAL_Driver/Src/stm32f0xx_hal_gpio.c>
  - <https://raw.githubusercontent.com/dotsolvit/stm32f0-gpio-speed-comparison/HEAD/MDK-ARM/stm32f0-gpio-speed-comparison.uvprojx>
  - <https://raw.githubusercontent.com/dotsolvit/stm32f0-gpio-speed-comparison/HEAD/stm32f0-gpio-speed-comparison.ioc>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `paper:book-bare-metal-embedded-c-programming-direct-register-access-gpio`) · [data/wave11/enrich/raw/paper_book_bare_metal_embedded_c_programming_direct_register_access_gpio.json](../../../data/wave11/enrich/raw/paper_book_bare_metal_embedded_c_programming_direct_register_access_gpio.json) (enrichment confidence 0.6)

</details>
