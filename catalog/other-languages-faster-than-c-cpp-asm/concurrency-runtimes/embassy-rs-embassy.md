# Embassy (async Rust executor) vs FreeRTOS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Async Rust embedded framework whose cooperative executor replaces an RTOS; claimed smaller than FreeRTOS, latency win unproven.

| | |
|---|---|
| **Beats** | FreeRTOS (C RTOS, used through the CMSIS-RTOS v2 wrapper in an STM32CubeIDE project) on an STM32F446ZE |
| **Claimed result** | README quote: 'It obsoletes the need for a traditional RTOS with kernel context switching, and is faster and smaller than one!' No figures appear on any page that was opened; the blog post that carries them (tweedegolf.nl, async-rust-vs-rtos-showdown) could not be reached from this environment. |
| **Workload** | Same toy firmware on a NUCLEO-F446ZE at 180 MHz in Embassy, RTIC and FreeRTOS (CMSIS-RTOS v2 over ST HAL): one task blinks an LED every 100 ms, a button task waits on the EXTI13 user-button interrupt and toggles GPIO PG1 (interrupt-to-task latency read on an oscilloscope), formats a 32-byte message and queues it to a UART writer task. Per search-result summaries (blog unreachable), the post compares interrupt latency, program size, static RAM and ease of programming. |
| **Metric** | other |
| **Hardware** | STM32F446ZE (Arm Cortex-M4F) on NUCLEO-F446ZE |
| **Compiler and flags** | Rust (rust/Cargo.toml): nightly toolchain (feature type_alias_impl_trait), [profile.release] opt-level = 3, lto = true, codegen-units = 1, incremental = false, debug = true (debug info only), embassy and embassy-stm32 from git master of early 2022. C (c/.cproject, STM32CubeIDE 1.8.0, MCU ARM GCC arm-none-eabi-): Release configuration C optimization -O3 with -g0 and no LTO (C++ option -Os, unused by this C project); the Debug configuration leaves the optimization level at the IDE default. The repo does not say which C configuration was measured, and no compiler versions are stated for either side. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README: async tasks compile into cooperatively scheduled state machines that share one stack, need no per-task stack sizing and no dynamic allocation, so no kernel context switch is paid. |
| **Adoption** | embassy-rs/embassy: 9.9k stars, 1.7k forks; tweedegolf/async-rtos-showdown: 18 stars, 2 forks, 3 commits (2022-01-04 to 2022-02-17) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/embassy-rs/embassy) · [benchmark](https://github.com/tweedegolf/async-rtos-showdown) |

## Verdict

The README links a 2022 Tweede Golf post that ran one toy firmware (LED blink, EXTI button, UART queue) in Embassy, RTIC and FreeRTOS via CMSIS-RTOS v2 on an STM32F446ZE at 180 MHz and compared interrupt latency, flash and static RAM; the post is unreachable, and secondary summaries say Embassy used less flash and RAM while FreeRTOS had better interrupt latency. No figure was readable, so 'faster' is unsupported and 'smaller' rests on an untuned, non-LTO C build.

## Use it when

- New Rust firmware on Cortex-M, RISC-V or ESP32 where flash and static RAM are tight and tasks mostly wait on I/O, timers or interrupts.
- Designs with many small concurrent activities (protocol state machines, sensor polling, USB plus networking) that would otherwise need many sized RTOS stacks.
- Low-power devices: the executor sleeps the core whenever no task is ready, with no tick-driven busy loop.
- Teams already on embassy-stm32/nrf/rp HALs who want DMA-driven async drivers instead of blocking HAL calls.

## Skip it when

- Hard real-time paths where worst-case interrupt-to-task latency must be bounded and proven: tasks on one executor are cooperative, and the only public comparison (Tweede Golf, 2022) reportedly had FreeRTOS ahead on interrupt latency and measured spread, not worst case.
- Code that runs long CPU-bound loops without awaiting: it blocks every other task on the same executor; move it to a higher-priority interrupt executor or split it.
- Existing C/C++ firmware or vendor stacks built around FreeRTOS APIs (queues, semaphores, CMSIS-RTOS); there is no C or C++ interface, and porting is a rewrite in Rust.
- Projects that need safety-certification artefacts for the scheduler: the Embassy and embassy-executor READMEs mention none, whereas FreeRTOS-based options are the usual route.

## How it is fast

The compiler turns each async task into a state machine stored in its own static, so tasks share one stack, need no per-task stack sizing and no heap, and switching between them is a function return plus a poll rather than a kernel context switch. A wake polls only the woken task; when nothing is ready the core sleeps (WFE/WFI) and interrupt handlers wake the executor through a 'pender' callback. Priorities come from running several executors, some in interrupt context (InterruptExecutor), so a higher-priority executor preempts a lower one via NVIC.

## Compared with alternatives

Pick Embassy over Kairos/rusty_rtos_kernel when you want async tasks with no per-task stacks and an integrated HAL ecosystem rather than a FreeRTOS-compatible preemptive kernel; Kairos has instruction-count numbers against FreeRTOS, Embassy has none that could be read. Tokio is the hosted counterpart for servers, not an option on a microcontroller.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | embassy-executor plus a platform (feature platform-cortex-m, platform-riscv32, platform-aarch32, platform-spin, platform-std, or a HAL-provided one); embassy-time with a time driver; a chip HAL such as embassy-stm32 |
| **Minimum toolchain** | Latest stable Rust (README: guaranteed only on latest stable); embassy-executor 0.10.0 uses edition 2024, so Rust 1.85 or newer. Since 0.8.0 task pools are statically allocated on stable; the 2022 benchmark needed nightly (type_alias_impl_trait). |
| **Platforms** | Cortex-M (thumbv6m/v7em/v8m), Cortex-A/R (aarch32), RISC-V 32/64, Xtensa ESP32 via esp-hal, AVR (nightly), WASM, std hosts |
| **Thread safety** | Executor is single-core and not Send; cross-executor or interrupt sharing goes through embassy-sync primitives parameterised by a RawMutex (NoopRawMutex, CriticalSectionRawMutex); multicore support is per HAL (embassy-rp, esp-rtos). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the only benchmark: the Rust firmware sets up PG0 as the 'button_interrupt' scope marker and calls core::mem::forget on it ('We're going to use this pin inside embassy'), but rust/Cargo.lock pins unmodified upstream embassy commit 59f909e, whose EXTI on_irq() never touches PG0; the C firmware (EXTI15_10_IRQHandler) and RTIC firmware (EXTI15_10 task) do toggle PG0. The interrupt-entry timing for Embassy therefore came from a local patch that is not published, so the latency row cannot be reproduced from the repo.
- The C baseline does different work: it waits on two rising edges because its 'only react to falling edges' block repeats EXTI-&gt;RTSR |= pin; EXTI-&gt;FTSR &= \~pin, it sends UART bytes with blocking polled HAL_UART_Transmit while Embassy uses DMA, it formats with newlib snprintf (reentrant newlib on) versus core::fmt, and it goes through ST HAL callbacks plus the CMSIS-RTOS v2 wrapper with an untuned CubeMX FreeRTOSConfig.h (15360-byte heap, trace facility, timers, generic task selection).
- Build settings are unequal: Rust release uses opt-level 3 with LTO and codegen-units = 1; the C Release config is -O3 without LTO, and which C configuration was flashed is not stated, so the size and RAM comparison favours Rust by construction.
- A task that never awaits starves its executor; priority only exists between executors, so latency depends on how the application is partitioned across interrupt executors.

## Known shortcomings

- No number on any reachable page (tweedegolf.nl blog blocked; search snippets say FreeRTOS won interrupt latency); the C side is unequal (blocking polled HAL_UART_Transmit vs Embassy DMA, newlib snprintf vs core::fmt, a falling-edge EXTI bug, an untuned CubeMX FreeRTOS with a 15360 B static heap and the CMSIS-RTOS v2 wrapper, C Release -O3 without LTO vs Rust LTO with codegen-units=1); a February 2022 snapshot.
- Harness flaw in the only benchmark: the Rust firmware forgets the PG0 ISR-marker pin 'to use inside embassy', but rust/Cargo.lock pins unmodified upstream embassy 59f909e whose EXTI on_irq() never touches PG0, while the C and RTIC firmware do toggle it, so Embassy's latency instrumentation came from an unpublished local patch and the latency row cannot be reproduced. The C side waits on two rising edges, uses polled UART against DMA and has no LTO. No numbers reachable (tweedegolf.nl, redlib, news.hada.io, segmentfault all ENOTFOUND).

## Caveats and trade-offs

Tier D because no number could be read from any opened page; the blog post with the figures (tweedegolf.nl/en/blog/65/async-rust-vs-rtos-showdown) was unreachable (DNS ENOTFOUND), as were the zeli.app and hn.svelte.dev mirrors. Secondary search summaries (snippet only) say Embassy used less RAM and flash but FreeRTOS had better interrupt latency, so 'faster' is not established; Reddit r/embedded and Hacker News commenters said worst-case latency was not measured, only the standard deviation, and flagged the C app's static RAM figure. The verifier read the C side and found it does not do the same work as the Rust side: (1) the UART writer uses blocking polled HAL_UART_Transmit, while Embassy writes over DMA asynchronously; (2) the C message formatting uses newlib snprintf (configUSE_NEWLIB_REENTRANT 1), while Rust uses core::fmt into an ArrayString; (3) the C button task's 'only react to falling edges' block sets the same RTSR/FTSR bits as the rising-edge block (EXTI-&gt;RTSR |= pin; EXTI-&gt;FTSR &= \~pin), so the C firmware waits on two rising edges and never on a falling edge; (4) the EXTI path goes through the ST HAL callback and the CMSIS-RTOS v2 wrapper (osThreadFlagsSet) instead of native FreeRTOS calls. FreeRTOSConfig.h is the untuned CubeMX default: a static 15360-byte heap (configTOTAL_HEAP_SIZE), three 512-byte task stacks, trace facility, software timers, recursive mutexes and generic task selection (configUSE_PORT_OPTIMISED_TASK_SELECTION 0) all on, which inflates the C side's static RAM and flash. Build settings are not equivalent: the Rust side uses LTO and codegen-units = 1 at opt-level 3, the C Release build -O3 without LTO (larger code than -Os), and the repo does not say whether the Debug or Release C build was measured. The showdown repo is a Feb 2022 snapshot built on Embassy master of that date, so the result predates four years of Embassy and FreeRTOS changes. A cooperative executor versus a preemptive RTOS is not a like-for-like scheduling comparison. The only claim in the embassy repo itself is a README sentence linking the blog. [retier] Harness flaw in the only benchmark: the Rust firmware forgets the PG0 ISR-marker pin 'to use inside embassy', but rust/Cargo.lock pins unmodified upstream embassy 59f909e whose EXTI on_irq() never touches PG0 (the C and RTIC firmware do toggle it), so Embassy's latency instrumentation came from an unpublished local patch and that row cannot be reproduced. The C side waits on two rising edges, uses polled UART against DMA and has no LTO.

Cooperative async tasks, not preemptive threads: a task that does not yield blocks the others, and priorities work through multiple executors/interrupts. Needs Rust nightly features in the 2022 snapshot; no C++ API.

## Maintenance

Very active (9.9k stars, 510 open issues, embassy-executor 0.10.0 released 2026-03-20, about 3.3M crate downloads), MIT or Apache-2.0 and copyable; the 2022 comparison predates four years of Embassy changes and is not a current benchmark.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The benchmark repo (tweedegolf/async-rtos-showdown) holds the Embassy (rust/), RTIC (rtic/) and FreeRTOS (c/) firmware, but neither it nor the Embassy README carries a single number; the figures exist only in the tweedegolf.nl blog post, which is unreachable here (DNS ENOTFOUND), and two WebSearch passes returned no figures even in snippets, so the entry stays at D.
- **Verifier notes:** Confirm at D: Embassy is notable (9.9k stars) and the comparison code is public, but no numbers were reachable and secondary summaries say FreeRTOS won interrupt latency. Shortcomings to record: no numbers reachable (blog blocked); C baseline is untuned CubeMX FreeRTOS behind the CMSIS-RTOS v2 wrapper and ST HAL with a 15 KB static heap, blocking polled UART vs Embassy DMA, newlib snprintf vs core::fmt, a falling-edge EXTI configuration bug, and no LTO on the C side against LTO plus codegen-units = 1 on the Rust side; worst-case latency not measured; 2022 snapshot. If the blog is ever reached, the tier could rise only to C or B, not A, because the C and Rust firmware do different work and the measured C configuration and compiler versions are unstated.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-32 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tweedegolf/async-rtos-showdown>
  - <https://github.com/tweedegolf/async-rtos-showdown/commits/master>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/README.md>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/rust/src/main.rs>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/c/.cproject>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/c/Core/Src/main.c>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/c/Core/Inc/FreeRTOSConfig.h>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/rtic/Cargo.toml>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/rtic/src/main.rs>
  - <https://github.com/embassy-rs/embassy>
  - <https://github.com/embassy-rs/embassy/commits/main>
  - <https://raw.githubusercontent.com/embassy-rs/embassy/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/embassy-rs/embassy>
  - <https://raw.githubusercontent.com/embassy-rs/embassy/HEAD/README.md>
  - <https://raw.githubusercontent.com/embassy-rs/embassy/HEAD/embassy-executor/README.md>
  - <https://raw.githubusercontent.com/embassy-rs/embassy/HEAD/embassy-executor/CHANGELOG.md>
  - <https://raw.githubusercontent.com/embassy-rs/embassy/HEAD/embassy-executor/Cargo.toml>
  - <https://raw.githubusercontent.com/embassy-rs/embassy/59f909e66533097b56093ec55fdd1341dbff6744/embassy-stm32/src/exti.rs>
  - <https://github.com/embassy-rs/embassy/issues?q=is%3Aissue+latency+OR+stack+overflow+OR+performance>
  - <https://crates.io/api/v1/crates/embassy-executor>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/README.md>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/rust/Cargo.lock>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/rust/.cargo/config.toml>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/rust/src/main.rs>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/c/Core/Src/main.c>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/c/Core/Src/stm32f4xx_it.c>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/c/Core/Inc/main.h>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/c/Core/Inc/FreeRTOSConfig.h>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/rtic/Cargo.toml>
  - <https://raw.githubusercontent.com/tweedegolf/async-rtos-showdown/HEAD/rtic/src/main.rs>
  - https://tweedegolf.nl/en/blog/65/async-rust-vs-rtos-showdown (ENOTFOUND)
  - https://redlib.hbubli.cc/r/embedded/comments/she3u9/async_rust_vs_rtos_showdown (ENOTFOUND)
  - https://news.hada.io/topic?id=25698 (ENOTFOUND)
  - https://segmentfault.com/p/1210000046643521 (ENOTFOUND)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/embassy-rs/embassy`) · [data/wave14/enrich/raw/github_com_embassy_rs_embassy.json](../../../data/wave14/enrich/raw/github_com_embassy_rs_embassy.json) (enrichment confidence 0.3)

</details>
