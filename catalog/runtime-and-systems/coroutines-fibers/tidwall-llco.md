# llco

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `Unlicense OR MIT-0 (README: Public Domain or MIT No Attribution)` · 🟡 stale

> Single-file C stackful coroutine switch (minicoro-derived assembly) with bring-your-own-stack; no scheduler, no benchmark against any baseline.

| | |
|---|---|
| **Beats** | none named |
| **Claimed result** | No numbers in the llco README. The neco README says llco-powered switching takes about 11 ns on an AMD Ryzen 9 5950X, with no baseline comparison. |
| **Workload** | Low-level stackful coroutine switch (assembly adapted from minicoro and Lua Coco); powers neco and sco. |
| **Metric** | latency |
| **Adoption** | 78 stars |
| **Last commit** | 2024-07-25 |
| **Links** | [repository](https://github.com/tidwall/llco) |

## Verdict

Nothing is measured in the llco repository; the only number is the neco README's statement that an llco-based context switch takes about 11 ns on the author's AMD Ryzen 9 5950X, with no compiler, flags, benchmark code or baseline (no ucontext, Boost.Context or minicoro comparison).

## Use it when

- You are writing your own scheduler, generator or actor runtime in C and want only the stack switch, with full control over stack allocation (pool, mmap with guard pages, arena).
- Embedded or no-malloc settings: llco itself never allocates; stacks come from the caller.
- Portable switching across Linux, macOS, FreeBSD, iOS, Android, RISC-V, 32-bit ARM and i386 from a single .c file under a public-domain/MIT-0 license.
- You want built-in stack unwinding (llco_unwind via _Unwind_Backtrace) to print backtraces from inside coroutines.

## Skip it when

- You need a scheduler, channels, sleeping or I/O: use neco (built on llco) or libdill/libmill instead.
- You need numbers: llco ships no benchmark at all, and the only figure (about 11 ns per switch in the neco README) has no baseline or code; minicoro, whose assembly llco adapts, publishes 9 vs 352 cycles against ucontext.
- Windows on anything but x86_64 (Windows Fibers fallback is an #error) or any Windows build that falls back to setjmp/longjmp stack switching (#error 'Windows stackjmp not supported').
- Android NDK r27 builds: open issue #1 reports a conflicting dladdr declaration in the unwind code (workaround: -DLLCO_NOUNWIND, not documented as such).
- Projects needing active maintenance or sanitizer support: last commit 2024-07-25, issue #2 (LLVM sanitizer support) open.

## How it is fast

On x86-64 System V the switch is a 17-instruction hand-written routine that saves and restores only the callee-saved registers (rip, rsp, rbp, rbx, r12-r15) in a struct, with no signal-mask syscall, unlike swapcontext. Windows x64 also saves rdi, rsi, xmm6-xmm15 and the TEB stack/fiber fields; aarch64, ARM EABI, RISC-V and i386 have their own assembly. llco_switch has a fast path that skips the cleanup bookkeeping when neither side is finishing. Where no assembly exists it starts coroutines with makecontext/setcontext once and then switches with _setjmp/_longjmp rather than swapcontext.

## Compared with alternatives

Pick llco over minicoro when you want an even thinner layer (no coroutine object allocation, no yield/resume data stack) under a public-domain/MIT-0 license, or the same switch neco uses; pick minicoro when you want measured numbers, a status/resume API and active maintenance, and libdill or neco when you need a scheduler.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc; libgcc unwind/dladdr for llco_unwind on GCC/Clang; emscripten fiber API on WebAssembly) |
| **Minimum toolchain** | C99 or later with GCC/Clang inline asm (MSVC on Windows x64 via a byte blob in .text); Emscripten needs -sASYNCIFY |
| **Platforms** | Assembly: x86-64 (Linux, macOS, Windows), aarch64, ARM EABI, RISC-V 32/64, i386; ucontext+setjmp fallback elsewhere; WebAssembly via emscripten fibers |
| **Thread safety** | Per-thread state in __thread variables; each thread has its own main context and current coroutine. A coroutine must be switched to only from the thread that runs it (not documented beyond the TLS layout). |
| **Drop-in for the baseline** | partial — replaces ucontext's makecontext/swapcontext role, but with a different API (descriptor struct, final flag, cleanup callback) and no argument passing on switch |

## Gotchas

- The struct llco handle a coroutine gets from llco_current() lives on that coroutine's own stack (llco_entry_wrap declares it locally), so it dangles once the coroutine finishes with final=true.
- The x86-64 System V switch does not save MXCSR or the x87 control word, so FP rounding-mode changes leak between coroutines (same as minicoro).
- Stack cleanup runs lazily on the next switch target (llco_cleanup_last); calling llco_start, llco_switch or llco_current from inside the cleanup callback aborts the process.
- The README says uco_method(0) but the function is llco_method; the asmctx_make reserves a 128-byte red zone and requires stack_size &gt;= 16384 or it aborts with 'stack too small'.

## Known shortcomings

- No numbers or baseline of its own; the only figure is about 11 ns per switch on a Ryzen 9 5950X quoted in the neco README, with no libco, Boost.Context or ucontext comparison. Directional only (tier D).
- No benchmark in the repo; stale since 2024-07-25. Open issue 1 (Android NDK r27 dladdr conflict) and 2 (sanitizer support). The x86-64 SysV switch skips MXCSR and the x87 control word; the llco_current handle lives on the coroutine stack and dangles after the final switch; the README names a nonexistent uco_method.

## Caveats and trade-offs

No benchmark against ucontext, Boost.Context or minicoro; the 11 ns figure (neco README) has no baseline or code. Assembly derived from minicoro and Lua Coco. Public-domain option carries no patent grant (MIT-0 alternative also has none). Stale since 2024-07-25.

No scheduler; caller supplies stack; Windows x86_64 only; WebAssembly needs -sASYNCIFY.

## Maintenance

Stale since 2024-07-25 with two open issues (Android NDK build error, sanitizer support), but it is about 1,200 lines in one file, dual-licensed Unlicense/MIT-0 and easy to vendor; the actively maintained copy is the amalgamated llco inside neco.c.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): reject; tier before verification D, tier now D.
- **Tier reason:** llco README has no numbers and no baseline; the only figure is in the neco README (about 11 ns per context switch on an AMD Ryzen 9 5950X), with no baseline and no benchmark code.
- **Verifier notes:** Tier D with 78 stars; rejected per the prompt rule, but it is the switch engine behind tidwall/neco, so the orchestrator's keep-and-document rule may apply. License (Unlicense or MIT-0) confirmed from LICENSE file; last commit 2024-07-25.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/tidwall/llco>
  - <https://github.com/tidwall/llco/commits>
  - <https://raw.githubusercontent.com/tidwall/llco/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/llco/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tidwall/llco/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/llco/HEAD/llco.h>
  - <https://raw.githubusercontent.com/tidwall/llco/HEAD/llco.c>
  - <https://raw.githubusercontent.com/tidwall/llco/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tidwall/llco/HEAD/test.c>
  - <https://github.com/tidwall/llco/issues?q=is%3Aissue>
  - <https://github.com/tidwall/llco/issues/1>
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/README.md>
  - <https://raw.githubusercontent.com/tidwall/neco/HEAD/neco.c>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/tidwall/llco`) · [data/wave11/enrich/raw/github_com_tidwall_llco.json](../../../data/wave11/enrich/raw/github_com_tidwall_llco.json) (enrichment confidence 0.8)

</details>
