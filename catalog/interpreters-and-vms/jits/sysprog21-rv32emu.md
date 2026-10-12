# rv32emu (tiered JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> RV32 RISC-V emulator in C with an interpreter, template JIT and LLVM tier; charted 1.25-2.85x faster than QEMU 9.0 user mode.

| | |
|---|---|
| **Beats** | QEMU v9.0.0 (RV32 user-mode emulation) |
| **Claimed result** | docs/benchmark.md says rv32emu with tiered JIT 'outperforms QEMU v9.0.0 across all benchmarks'; the speedup appears only in a normalised bar chart (docs/jit-bench.png, reciprocal of mean elapsed time over 200 iterations, QEMU = 1.0), read by eye (chart image, not stated in text): numeric sort about 2.07x, string sort about 2.6x, bitfield about 2.04x, emfloat about 1.5x, assignment about 2.85x, idea about 2.5x, huffman about 2.37x, dhrystone about 2.65x, primes about 1.25x, sha512 about 1.26x. Reference table on the same page (no QEMU column): Threadripper 2990WX Dhrystone 33,365 DMIPS (T2C) vs 2,533 (interpreter), about 13x (derived from page data); CoreMark 13,272 vs 1,835 iterations/s, about 7.2x (derived from page data). |
| **Workload** | RV32IM guest programs: nbench-derived numeric sort, string sort, bitfield, emfloat, assignment, idea, huffman plus dhrystone, primes and sha512, elapsed time averaged over 200 iterations, rv32emu with tiered JIT versus QEMU. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-11700 at 2.5 GHz, Ubuntu 22.04.1 LTS (QEMU comparison); AMD Threadripper 2990WX and Ampere eMAG (DMIPS/CoreMark table) |
| **Compiler and flags** | RV32IM guest toolchain GCC v14.2.0; host build flags of rv32emu and QEMU not stated (DMIPS table lists GCC 14.2 on Threadripper and Clang 18.1 on Ampere eMAG) |
| **Adoption** | 594 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/sysprog21/rv32emu) · [benchmark](https://github.com/sysprog21/rv32emu/blob/master/docs/benchmark.md) |

## Verdict

The project's own chart (docs/benchmark.md, Intel Core i7-11700 at 2.5 GHz, Ubuntu 22.04.1, guests built with GCC 14.2.0 for RV32IM, mean of 200 iterations) shows tiered-JIT rv32emu faster than QEMU v9.0.0 user mode on all ten nbench-derived and crypto kernels. Read by eye, that is about 1.25x on primes and sha512 and about 2.0-2.85x on the sorts, bitfield, assignment, idea, huffman and Dhrystone. Separately, on Threadripper 2990WX with GCC 14.2, T2C reaches 33,365 DMIPS vs 2,533 for the interpreter (about 13x, derived from page data) and CoreMark 13,272 vs 1,835 iterations/s, with CoreMark rejected on a checksum mismatch.

## Use it when

- Running compute-bound RV32 bare-metal or newlib programs on an x86-64 or Arm64 host where qemu-riscv32 is the incumbent; the vendor chart shows about 2-2.85x on integer, sorting and crypto kernels.
- Teaching, research or simulators that need a readable RISC-V reference you can modify (C99/C11, MIT licence) and that still runs fast.
- Embedding an RV32 guest in a C program, for example a scripting or sandbox layer, with JIT speed on desktop hosts and an interpreter fallback elsewhere.
- Running RV32 programs in the browser through the WebAssembly build (interpreter only, since the JIT targets native x86-64 and Arm64).

## Skip it when

- You need RV64, the D/Q extensions, full V, multiple harts, or Linux user-mode syscall emulation: rv32emu supports RV32 only with partial V, and its user mode is a newlib syscall layer.
- Linux workloads under system emulation that create many short-lived processes: SFENCE.VMA flushes throw away compiled blocks, and the page's fork+exec column shows T1C and T2C barely ahead of the interpreter (10,324 and 10,397 ms vs 10,974 ms on Threadripper).
- Programs that rewrite their own code in user mode: the JIT does not invalidate translated code when the guest modifies its instructions (docs/codegen.md).
- Hosts other than x86-64 and Arm64, where the default build falls back to the interpreter, or builds where LLVM 18-21 cannot be installed, which leaves only T1C.
- Picking an emulator because of the QEMU chart: the speedups are vendor-measured, shown only as a PNG, and come from an unstated tier configuration.

## How it is fast

There are three tiers. First, a tail-call-threaded interpreter (musttail handlers, no switch dispatch) with IR constant folding and macro-op fusion such as lui+addi into one op. Second, a template JIT (T1C) for hot basic blocks on x86-64 and Arm64, with a small dynamic register allocator and block chaining that patches direct branches to jump straight between translated blocks. Third, an LLVM tier (T2C) that compiles hot regions: it traces successor blocks, keeps guest registers in LLVM locals, and predicts indirect jumps that hit one target at least 90% of the time so call-heavy loops become one region. T2C compiles on a background thread.

## Compared with alternatives

Pick it over rv8 (the CARRV 2017 RISC-V-to-x86-64 translator, an x86-64-only research codebase) when you need an actively maintained RV32 emulator with an Arm64 JIT and a Linux system mode. Pick libriscv when the job is embedding sandboxed guest calls with nanosecond call overhead, and RVVM if you want its tracing JIT without an LLVM dependency (RVVM publishes no numbers); rv32emu is the choice for RV32 newlib or Linux guests with an LLVM-optimised hot tier.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Berkeley SoftFloat (git submodule, for the F extension); SDL2 and SDL2_mixer for the default build (can be turned off); LLVM 18-21 development package for T2C; pthreads |
| **Minimum toolchain** | GCC or Clang with C11 (built as -std=gnu11), musttail support for the threaded interpreter; LLVM 18-21 for T2C (LLVM 20+ validated in CI); LTO on by default needs llvm-ar when the compiler is Clang |
| **Platforms** | JIT on x86-64 and Arm64 hosts (Linux and macOS in CI); interpreter on other hosts; WebAssembly build via Emscripten |
| **Thread safety** | Single hart, single guest thread. With T2C one background compiler thread is created, and its handle is a static global in src/riscv.c, so more than one T2C-enabled emulator per process is not documented as supported. |
| **Drop-in for the baseline** | partial — it runs the same static RV32 newlib binaries from the command line as qemu-riscv32 user mode, but has no Linux syscall ABI, no RV64 and no multi-hart support, and its system mode is a minimal virt-like machine rather than QEMU's device set |

## Gotchas

- Harness flaw in the headline claim: the QEMU comparison is a PNG chart only (docs/jit-bench.png). The script that produced it, QEMU's build and run flags, rv32emu's host flags, whether T2C was on, and whether elapsed time includes process start-up are all unstated. The page text says primes, sha512 and emfloat gain the most, but the chart shows them as the three smallest gains (about 1.25x, 1.26x and 1.5x).
- T2C compiles on a separate pthread (t2c_runloop in src/riscv.c), so wall-clock comparisons against single-threaded QEMU TCG user mode give rv32emu a second host core for LLVM work. On a host limited to one CPU the gap may be smaller.
- The default build (make defconfig) is T1C only. T2C needs make jit_defconfig with LLVM installed, so a default build will not reach the T2C figures (for example Dhrystone 16,269 vs 33,365 DMIPS on Threadripper).
- Misaligned halfword and word accesses trap as on hardware unless you pass -m. Run-time-generated guest code is not scanned or invalidated.

## Known shortcomings

- QEMU v9.0.0 speedups are chart-only (jit-bench.png, about 1.25x-2.85x eyeballed) and the prose contradicts the chart (primes, sha512 and emfloat are said to gain most but show the smallest bars); no QEMU script, host flags or charted tiers, and the VMIL'24 paper is snippet only. Off-baseline (QEMU).
- Enricher: the T2C tier compiles on a background pthread (t2c_runloop in src/riscv.c), so wall clock against single-threaded QEMU TCG gets an extra core; the default defconfig is T1C only; the JIT does not invalidate self-modifying user code; no script, QEMU flags or tier configuration behind docs/jit-bench.png.

## Caveats and trade-offs

Numbers for the QEMU comparison exist only in a PNG chart, values here are eyeballed. The page text calls primes, sha512 and emfloat the biggest gains while the chart shows them as the three smallest, so prose and chart disagree. QEMU flags, the rv32emu host build flags, which tiers were enabled (T1C only or T1C plus LLVM-based T2C) and the script that produced the chart are not named on the page (tests/interpreter_bench.py is for the libriscv comparison, tests/bench.py has no QEMU mode). The default build has since moved to T1C (defconfig), so the chart may not reflect the current default. Baseline is not one of PyPy, LuaJIT, V8, HotSpot. The peer-reviewed VMIL'24 paper (dl.acm.org/doi/10.1145/3689490.3690399) is blocked here; its abstract (search snippet only) reports 12%/35% overhead versus native x86/ARM code and says the result beats RV8 and QEMU.

RV32I[MAFC] guest only; an emulator rather than a general language JIT; tiered JIT (modes T1C and T2C in the page's tables); in system mode runs under Linux gain little because SFENCE.VMA flushes discard compiled blocks (page says so).

## Maintenance

Actively maintained (last commit 2026-10-03, 1,751 commits, per-PR benchmark CI with paired 'duet' runs); MIT-licensed and copyable, but the QEMU comparison predates the current T1C default, and the VMIL'24 paper behind it could not be opened here (dl.acm.org and the NCKU research portal are blocked).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/benchmark.md compares rv32emu (tiered JIT) with QEMU v9.0.0 on an Intel Core i7-11700 with GCC 14.2.0 guest builds, but the speedups exist only in the jit-bench.png chart, the script that produced it is not named, and the host build flags of rv32emu and QEMU are not stated, so first-party with partial methodology. The VMIL'24 paper (abstract snippet only: 12%/35% overhead versus native x86/ARM, better than RV8 or QEMU) could not be opened; a paper-access retier could raise this to B.
- **Verifier notes:** Chart values match the record's 1.25x-2.85x range; record kept at C. Shortcomings: QEMU numbers chart-only, prose-chart contradiction on which benchmarks gain most, no named QEMU-comparison script or host flags, tier configuration of the charted run unstated. Metadata checked: MIT, 594 stars, not a fork or archived, last commit 2026-10-03.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/docs/benchmark.md>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/docs/jit-bench.png>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/README.md>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/LICENSE>
  - <https://github.com/sysprog21/rv32emu>
  - <https://github.com/sysprog21/rv32emu/commits/master>
  - <https://github.com/sysprog21/rv32emu/issues/689>
- **Sources the enricher read:**
  - <https://github.com/sysprog21/rv32emu>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/README.md>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/docs/benchmark.md>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/docs/jit-bench.png>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/docs/build.md>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/docs/codegen.md>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/configs/defconfig>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/configs/jit_defconfig>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/configs/interpreter_defconfig>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/Makefile>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/tests/bench.py>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/src/riscv.h>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/src/riscv.c>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/src/t2c.c>
  - <https://raw.githubusercontent.com/sysprog21/rv32emu/HEAD/src/main.c>
  - <https://github.com/sysprog21/rv32emu/issues?q=is%3Aissue+jit>
  - <https://github.com/sysprog21/rv32emu/issues/689>
  - <https://github.com/sysprog21/rv32emu/issues/322>
  - <https://github.com/sysprog21/rv32emu/commits/master/docs/jit-bench.png>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/sysprog21/rv32emu`) · [data/wave12/enrich/raw/github_com_sysprog21_rv32emu.json](../../../data/wave12/enrich/raw/github_com_sysprog21_rv32emu.json) (enrichment confidence 0.65)

</details>
