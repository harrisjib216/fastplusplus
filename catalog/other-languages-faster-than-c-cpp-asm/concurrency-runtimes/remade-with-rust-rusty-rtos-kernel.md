# Kairos / rusty_rtos_kernel (FreeRTOS kernel remade in Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> FreeRTOS V11.3.1 scheduler rewritten in safe no_std Rust; fewer instructions per rv32 tick and cooperative switch, less RAM per task, more flash.

| | |
|---|---|
| **Beats** | FreeRTOS V11.3.1 kernel (C), unmodified, with its first-party GCC RISC-V port, built with clang -O2 |
| **Claimed result** | Kairos umbrella README table (headed rv32), retired instructions unless stated: tick 9 vs 15 (0.60x, bench/tick-work, runtime minstret count); scheduler selection 45 vs 27 (1.67x against Kairos); whole cooperative switch 75 vs 110 (0.68x) and whole preemptive switch 119 vs 110 (1.08x against). Both switch rows add the measured selection row to a static llvm-objdump count of the register half from bench/switch-cost (Kairos 30 cooperative and 74 preemptive against FreeRTOS portASM.S 83; the 83/30/74 constants are typed into tick-work/run.sh). List operation 18.47 vs 22.32 instructions per op (0.83x) is not an rv32 row: it is bench/list-cost, callgrind on an x86-64 host, rustc opt-level 3 plus LTO against gcc 15.2 -O2 list.c. The ledger gives gcc -O3 at 21.82 (about 0.85x, derived from page data) and a 32-bit row of 23.75 vs 33.42, and its latest 64-bit Rust figure is 18.80; 18.47 appears only in the README. RAM per task 176 B vs 596 B (0.30x); the C figure includes a 512 B task stack that stackless Kairos tasks do not own. Flash 19,484 B vs 13,924 B (1.40x against); the scorecard says 19,746 B (1.42x) and the kernel README says 22,396 B by default or 17,860 B with the small feature. The kernel README adds Cortex-M3 PendSV 19 vs 19 (parity) and an RV32 preemptive register half of 74 vs 83. |
| **Workload** | Retired instructions per call on RV32IMAC under QEMU virt with -icount shift=0, same operations in both kernels (tick, scheduler selection, whole task switch, list operation), plus RAM per task and flash size; both kernels are first proven trace-identical on 22 conformance scenarios. |
| **Metric** | other |
| **Hardware** | QEMU virt -cpu rv32 (rv32imac) with -icount shift=0 for the tick and selection rows (retired instructions read from minstret, deterministic, independent of the host). The register half is a static disassembly count. The list row ran under callgrind on an x86-64 WSL2 host whose CPU is not stated. ESP32-S3 cycle figures (tick 54, switch 166 cycles) are Kairos-only and predate kernel 0.2.1. |
| **Compiler and flags** | tick-work (tick, selection): C arm clang -target riscv32-unknown-elf -march=rv32imac -mabi=ilp32 -O2 -ffreestanding -fno-builtin, compiled per translation unit and linked with ld.lld (bench/tick-work/run.sh). Rust arm firmware/riscv32-qemu-tick-work [profile.release] opt-level 2, lto false, codegen-units 1, panic abort, overflow-checks off. The script does not pin compiler versions. switch-cost (register half): static instruction counts with llvm-objdump; FreeRTOS portASM.S macros assembled by clang, so both sides of that half are hand-written assembly. list-cost: gcc -O2 and -O3 (gcc 15.2 per LEDGER.md) against Rust release opt-level 3, lto true, one codegen unit, counted under callgrind on an x86-64 WSL2 host. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | README: FreeRTOS pays 110 instructions for every RISC-V switch because its portYIELD() is a trap that saves everything an interrupt could clobber, while Kairos yields cooperatively for 75; the stackless task design removes the per-task stack (RAM); the project itself says the cooperative gain is about where the yield is taken, not about moving registers more cheaply. |
| **Adoption** | 0 stars (kernel repo), 1 star (kairos umbrella repo); rusty_rtos_kernel crate about 424 crates.io downloads |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/Remade-With-Rust/rusty_rtos_kernel) · [benchmark](https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/README.md) |

## Verdict

On QEMU virt rv32imac under -icount shift=0, retired instructions per call (minstret bracket, median of 512, PARITY and POISON gates) for unmodified FreeRTOS V11.3.1 built with clang -O2 per translation unit versus the Rust kernel at opt-level 2, no LTO, one codegen unit: tick 15 vs 9 and scheduler selection 27 vs 45; the 75 vs 110 cooperative and 119 vs 110 preemptive switch rows add a static llvm-objdump count of the register half (30 or 74 vs 83), the 18.47 vs 22.32 list row is callgrind on an x86-64 host at Rust opt-level 3 with LTO against gcc -O2, RAM per task is 176 B vs 596 B (stackless vs TCB plus 512 B stack), and flash is 19,484 B vs 13,924 B against it. No silicon cycle comparison exists.

## Use it when

- FreeRTOS-style firmware on RV32 (QEMU virt, ESP32-C6 class), Cortex-M or ESP32-S3 where you want a memory-safe kernel that keeps the FreeRTOS API names and is diff-tested against the C kernel's own trace.
- Many small tasks under RAM pressure, written as state machines: 176 B per stackless task against 596 B for a FreeRTOS TCB plus a 512 B stack; the project puts the flash/RAM crossover at about 13-14 tasks.
- Yield-heavy workloads on RISC-V (queues that block, semaphore takes, taskYIELD), where a cooperative switch counts 75 instructions against FreeRTOS's 110.
- Migrating an existing FreeRTOS C code base gradually: the C ABI crate lets the standard demo files link unmodified against the Rust kernel.
- Evaluating differential conformance testing of a kernel rewrite: the trace oracle, Kani proofs and mutant counts are public.

## Skip it when

- Flash-constrained parts: 19,484 B against FreeRTOS's 13,924 B (1.40x) for kernel plus RISC-V port, 22,396 B in the default speed build per the kernel README, 17,860 B with the small feature.
- Preemption- or interrupt-heavy systems: a preemptive switch counts 119 against 110 and scheduler selection 45 against 27, so the cooperative-switch win does not carry over.
- Anything needing an MPU, privilege separation, xTaskCreateStatic-style static allocation, co-routines, more than two cores, core affinity or queue items larger than 8 bytes; none is supported.
- Production or certified products today: first published 2026-09-16, eight releases in three weeks (0.3.3 on 2026-10-04), 0 GitHub stars, about 425 crates.io downloads and no independent users or measurements.
- When you need wall-clock or cycle evidence: the C-compared rows are retired-instruction counts under QEMU, and the only silicon cycle figures (ESP32-S3, predating 0.2.1) have no C arm.

## How it is fast

The wins are design, not code generation. A Kairos cooperative yield happens at a call site and saves only the 14 registers the ABI says are live, while FreeRTOS's RISC-V portYIELD() is an ecall trap that saves all 28 GPRs (83 instructions for every switch); on Cortex-M, where both kernels pend PendSV, the counts are equal (19 vs 19). Stackless tasks remove the per-task stack, which is where the 176 B vs 596 B RAM row comes from. The tick row came from caching the running task's priority (removing a generational-handle arena resolve) and masking a 64-bit tick compare down to one 32-bit bltu. Selection is slower than C (45 vs 27) because of handle validation and the stackless bookkeeping.

## Compared with alternatives

Pick it over Embassy when you want FreeRTOS's API, semantics and C demo compatibility with trace-level equivalence to the C kernel rather than a Rust-native async executor; the other catalogued concurrency entries (Tokio, GHC threads, ring buffers) target hosted systems and do not compete on microcontrollers.

## Integration

| | |
|---|---|
| **Form** | crate (rusty_rtos_kernel facade over the no_std rusty_rtos_kernel-core, optional alloc), plus separate port crates and the rusty_rtos-capi C ABI crate |
| **Dependencies** | rusty_rtos_core 0.2.5 (shared vocabulary); a rusty_rtos_port-&lt;arch&gt; crate for real hardware (the only place unsafe is allowed); no C, no FFI in the kernel |
| **Minimum toolchain** | Rust 1.85 (edition 2024); the published instruction-count bench also needs the unstable '-C target-feature=+relax', which its own config says a stable toolchain cannot produce |
| **Platforms** | host sim (x86-64 Windows and Linux), Cortex-M (thumbv7m, thumbv7em, thumbv8m.main), riscv32imac/imafc, xtensa-esp32s3 (esp toolchain); conformance corpus run on QEMU M3, QEMU RV32 and a XIAO ESP32-S3 |
| **Thread safety** | One Kernel object owned by the firmware; methods take &mut self and critical sections come from the port; two-core SMP is supported without affinity, with cross-core yields drained by Kernel::take_core_yields() and FromISR variants for interrupt context. |
| **Drop-in for the baseline** | partial: rusty_rtos-capi links unmodified FreeRTOS demo C files (25-26 of them pass their own checkers), but there is no static allocation, no MPU, no co-routines, queue items are limited to 8 bytes, and the native Rust API is stackless (blocking calls return Wait::Blocked). |

## Gotchas

- Possible harness flaw behind the headline tick row (9 vs 15), unverified without disassembly: the Rust arm calls a generic Kernel method that is monomorphised into the bench crate itself (codegen-units = 1), so 'no LTO' does not stop it being inlined into the bracket, the result is discarded with 'let _ =', and minstret is read through asm declared options(nomem), which lets the optimiser move kernel loads and stores across the counter reads. The C arm calls xTaskIncrementTick across a translation-unit boundary and computes its return value. The executed source path (suspended check, tick load-add-store, wrap test, unblock compare) is already about 8 instructions, before the time-slice list-length test, the yield-pending test, a call and a return, so 9 is consistent with the switch_required computation being dead-code-eliminated. The project's own ledger documents the same 'a probe that discards a result measures the discarding' defect in its flash bench, and the POISON gate (two calls must count at least 1.5x one) cannot detect it.
- The RAM-per-task win applies to stackless state-machine tasks: the native API returns Wait::Blocked instead of blocking and the task is called again; C-style tasks with their own stacks need a port's stack swap and pay for the stack as FreeRTOS does.
- The bench configuration differs from the shipped build: tick-work runs on SimPort unless --features real-port is passed (run.sh does not pass it; the scorecard says the three C-compared rows are identical on both), sets overflow-checks = false while the kernel workspace's hardening policy sets overflow-checks = true in release, and needs the unstable +relax target feature.
- Numbers drift between documents: bench/tick-work/README.md still prints tick 56 and selection 79 (cooperative switch 109 vs 110), the C FreeRTOSConfig.h says run.sh builds the C arm with and without the stack-overflow check but run.sh never sets KAIROS_STACK_CHECK, flash appears as 19,484, 19,746 and 22,396 B, and the kernel README opens with an unrelated 'In The Wild with 870 Active Installs' RAGconverter.com banner while crates.io shows about 425 downloads.

## Known shortcomings

- Counts retired instructions, not time, with -O2 on both arms; the list row (18.47 vs 22.32) is x86-64 callgrind with Rust opt-level 3 plus LTO against gcc -O2 (gcc -O3 gives 21.82, about 0.85x derived), not rv32; the switch rows are composites with typed-in register-half constants; wins come from design (call-site yield vs ecall trap, stackless tasks), not Rust; mixed result (selection 45 vs 27 worse) and figures stale across docs.
- Likely harness flaw behind the tick row (9 vs 15 retired instructions), not proven without disassembly: the Rust arm's generic Kernel is monomorphised into the bench crate (codegen-units=1), so inlining is possible despite no LTO, `let _ = kernel.increment_tick()` discards the result, and the minstret asm is options(nomem), while the C arm is a cross-TU call that computes its return value; the source path alone is about 8 instructions before the time-slice test plus call and ret, so 9 fits dead-code elimination. The project ledger documents the same discard defect in its flash bench, and the POISON gate cannot catch it. The bench needs unstable +relax, sets overflow-checks off while the shipped profile sets them on, and the tick-work README is stale (56/79).

## Caveats and trade-offs

The metric is retired instructions under an emulator, not wall-clock time or cycles. The project says these are work rows, not cycle rows, and its only silicon cycle figures have no C arm. Both arms of the tick-work rows are matched at -O2 with no LTO, not -O3. The list row breaks the matching: Rust at opt-level 3 with LTO against gcc -O2, measured on an x86-64 host but shown under an rv32 heading. Against gcc -O3 (21.82) it is still about 0.85x (derived from page data). The headline cooperative-switch win (75 vs 110) is a composite of a runtime count and a static count of hand-written assembly. Its gap is structural, not Rust codegen: FreeRTOS's RISC-V portYIELD() is an ecall trap that saves all 28 GPRs, while a Kairos yield happens at a call site and saves 14. The project's own Cortex-M3 control shows parity (19 vs 19). The RAM-per-task win compares stackless state-machine tasks with FreeRTOS tasks that own a 512 B stack. The tick win came from a cached current_priority (one arena resolve removed) and a 32-bit compare fix (LEDGER 2026-09-28); neither the ledger nor the scorecard explains why 9 ends up below C's 15. Mixed result: preemptive switch, scheduler selection and flash are worse than C. Numbers drift between documents. bench/tick-work/README.md still prints the older 56 vs 15 tick and 79 selection. Flash appears as 19,484, 19,746 and 22,396 B. The README says thirteen rows have a C arm with three against Kairos, the scorecard says eleven with one loss. The ledger records two corrected harness defects (a hand-rolled NoTrace that inflated the silicon and selection rows 305 to 79, and a broken work-parity anchor) and a list-cost bench that once could not run. First-party only, no independent measurement, near-zero adoption (0 stars on the kernel repo, 1 on the umbrella, 424 crates.io downloads). An RTOS scheduler is a loose fit for concurrency-runtimes. [retier] Likely harness flaw behind the tick row (9 vs 15 retired instructions), not proven without disassembly: the Rust arm's generic Kernel is monomorphised into the bench crate (codegen-units=1), `let _ = kernel.increment_tick()` discards the result and the minstret asm is options(nomem), while the C arm is a cross-TU call that computes its return value; the source path alone is about 8 instructions before the time-slice test plus call and ret, so 9 fits dead-code elimination. The project ledger documents the same discard defect in its flash bench; the POISON gate cannot catch it. The bench needs unstable +relax and sets overflow-checks off while the shipped profile sets them on.

Flash is 1.40x larger (handle validation, stackless resume machinery, u16 list ids); queue items are at most 8 bytes; SMP only on two cores with no affinity; no MPU, no static allocation and no co-routines; no privilege separation between tasks; a C ABI crate (rusty_rtos-capi) lets unmodified FreeRTOS C demos link against it.

## Maintenance

Very active but very young (220 commits, last commit 2026-10-09, crate 0.3.3 of 2026-10-04, MIT OR Apache-2.0) and with no outside adoption yet; well documented and heavily self-tested, but the tick row's bracket should be checked against a disassembly before quoting the 0.60x.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The tick and scheduler-selection rows are reproducible from public code (kairos bench/tick-work/run.sh building unmodified FreeRTOS V11.3.1 plus firmware/riscv32-qemu-tick-work) with the compiler, flags (-O2 both arms, no LTO) and machine (QEMU virt -cpu rv32, -icount shift=0, minstret) stated, so the A tier holds for those rows. The verdict is a downgrade of the claim, not the tier: the record overstated the list row, the composite switch rows and same_algorithm.
- **Retiered** A to C: Enricher: the tick-work row (the main Rust win) discards increment_tick's result inside a monomorphised bench crate, so its 9 retired instructions fit dead-code elimination of the counted work (the project's own ledger documents the same defect in its flash bench), and nothing was checked by disassembly; the bench also needs unstable +relax and differs from the shipped profile. Measured row likely not doing the work: A to C.
- **Verifier notes:** Tier A kept for bench/tick-work (tick 9 vs 15, selection 45 vs 27), which is public, deterministic and gated by PARITY and POISON checks against unmodified FreeRTOS V11.3.1 at matched -O2. Record shortcomings: the list row is mislabelled as rv32 and opt-mismatched, the switch rows are composites with typed-in register-half constants, the wins come from design (call-site yield vs ecall trap, stackless tasks, index arenas) rather than the language, the C baseline is -O2 rather than -O3, the result is mixed, and figures are stale across documents. Metadata checked: MIT OR Apache-2.0, 0 stars, 220 commits, last commit 2026-10-09, crate 424 downloads.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/tick-work/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/tick-work/run.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/switch-cost/run.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/list-cost/run.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/list-cost/rs/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/tick-work/c/FreeRTOSConfig.h>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/docs/plans/freertos-scorecard.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/docs/LEDGER.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/docs/LEDGER.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/firmware/riscv32-qemu-tick-work/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/LICENSE-MIT>
  - <https://github.com/Remade-With-Rust/rusty_rtos_kernel>
  - <https://github.com/Remade-With-Rust/rusty_rtos_kernel/commits/main>
  - <https://github.com/Remade-With-Rust/kairos>
  - <https://crates.io/api/v1/crates/rusty_rtos_kernel>
- **Sources the enricher read:**
  - <https://github.com/Remade-With-Rust/rusty_rtos_kernel>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/docs/LEDGER.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/crates/rusty_rtos_kernel-core/src/kernel.rs>
  - <https://github.com/Remade-With-Rust/rusty_rtos_kernel/tree/main/crates/rusty_rtos_kernel-core/src>
  - <https://github.com/Remade-With-Rust/rusty_rtos_kernel/tree/main/firmware/riscv32-qemu-tick-work>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/firmware/riscv32-qemu-tick-work/Cargo.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/firmware/riscv32-qemu-tick-work/.cargo/config.toml>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_kernel/HEAD/firmware/riscv32-qemu-tick-work/src/main.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/rusty_rtos_port/HEAD/crates/rusty_rtos_port-riscv/src/lib.rs>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/tick-work/README.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/tick-work/run.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/tick-work/c/main.c>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/tick-work/c/FreeRTOSConfig.h>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/switch-cost/run.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/bench/list-cost/run.sh>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/docs/plans/freertos-scorecard.md>
  - <https://raw.githubusercontent.com/Remade-With-Rust/kairos/HEAD/docs/LEDGER.md>
  - <https://crates.io/api/v1/crates/rusty_rtos_kernel>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/remade-with-rust/rusty_rtos_kernel`) · [data/wave14/enrich/raw/github_com_remade_with_rust_rusty_rtos_kernel.json](../../../data/wave14/enrich/raw/github_com_remade_with_rust_rusty_rtos_kernel.json) (enrichment confidence 0.62)

</details>
