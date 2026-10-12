# Boost.Context

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++ and assembly` · `BSL-1.0` · 🟢 active

> Boost's assembly-backed stackful context switch (fiber, callcc/continuation): about 9 ns per switch versus 547 ns for glibc swapcontext.

| | |
|---|---|
| **Beats** | glibc ucontext_t user-space context switch (::swapcontext/makecontext), as wrapped by Boost.Context's own continuation_ucontext.hpp backend (b2 context-impl=ucontext), run through the same callcc()/continuation benchmark |
| **Claimed result** | fcontext_t (hand-written per-platform jump_fcontext/make_fcontext assembly): 9 ns / 19 CPU cycles per switch; ucontext_t: 547 ns / 1130 CPU cycles; Windows Fiber: 49 ns / 98 CPU cycles. Roughly 61x lower latency and 59x fewer cycles than ucontext_t (derived from page data). |
| **Workload** | Round-trip context switch through callcc()/continuation, reported as the average per jump (two jumps per round trip) in nanoseconds and CPU cycles, release build. |
| **Metric** | latency |
| **Hardware** | dual Intel Xeon E5-2620v4 2.2 GHz, 16C/32T, 64 GB RAM, Linux x86_64 |
| **Compiler and flags** | gcc-6.3.1; b2 properties variant=release, optimization=speed (performance/callcc/Jamfile.v2 also sets link=static, threading=multi and -DBOOST_DISABLE_ASSERTS) |
| **Adoption** | 370 stars; Boost library |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/boostorg/context) · [benchmark](https://raw.githubusercontent.com/boostorg/context/HEAD/doc/performance.qbk) |

## Verdict

The project's doc/performance.qbk (about 2017) reports a callcc()/continuation round trip divided by two: 9 ns / 19 TSC ticks per switch with the fcontext_t assembly backend versus 547 ns / 1130 for the same API on the ucontext_t backend (glibc swapcontext), built with gcc-6.3.1 at b2 variant=release optimization=speed on a dual Xeon E5-2620 v4 under Linux; about 55-61x lower latency given the truncated ns figure (derived from page data). The 49 ns Windows-Fiber figure was necessarily measured on another OS.

## Use it when

- Building coroutines, generators, green threads or a fiber scheduler in C++ where a switch must cost tens of nanoseconds, not a system call.
- Replacing makecontext/swapcontext (deprecated in POSIX.1-2004, removed in POSIX.1-2008) in existing code on x86-64, AArch64, ARM, i386, RISC-V64, POWER, MIPS, s390x, SPARC64, LoongArch64 or Alpha.
- Asymmetric or symmetric stackful switching where code must suspend from deep inside nested calls, which stackless C++20 coroutines cannot do.
- Projects already depending on Boost, or wanting the battle-tested layer that Boost.Fiber and Boost.Coroutine2 use, with pluggable stack allocators and guard pages.

## Skip it when

- Code that relies on a per-context signal mask: fcontext switches do not preserve it (stated in the rationale), only the slow ucontext backend does.
- Builds that need AddressSanitizer: sanitizers are supported only with context-impl=ucontext plus BOOST_USE_ASAN, i.e. on the backend that is about 60x slower per the project's table; Valgrind needs valgrind=on and BOOST_USE_VALGRIND.
- PPC64 code that keeps live values in floating-point registers across switches: issue #232 (open since 2023, patch offered 2026-08) reports FP14-FP31 are not preserved since about Boost 1.61.
- Windows ARM64 with fcontext (b2 defaults that target to WinFiber; issue #336 reports a 16-byte stack-pointer skew in ontop_fcontext that breaks /GS and SEH unwinding), AArch64 builds that require GCS or PAC (issues #332, #338), and WebAssembly/Emscripten (issues #109, #292).
- Tiny C or embedded projects that want a single-file switcher without Boost's build system and assembler setup.

## How it is fast

The default fcontext_t backend is a hand-written jump_fcontext/make_fcontext/ontop_fcontext routine per architecture, ABI and binary format. On x86-64 SysV it pushes only the callee-saved registers (R12-R15, RBX, RBP) plus MXCSR and the x87 control word onto the current stack, uses the stack pointer itself as the context handle, swaps RSP and jumps to the saved return address; data is passed in registers as a transfer_t. Unlike glibc swapcontext it does not save or restore the signal mask, so no rt_sigprocmask system call happens per switch, which is where most of the 60x gap to the ucontext_t backend comes from (the library's own rationale says ucontext_t is slow because preserving the signal mask needs system calls).

## Compared with alternatives

Against libco (higan-emu), the only switcher among the siblings, pick Boost.Context when you need a C++ API with stack allocators, guard pages, forced unwinding and a wider ABI list (s390x, LoongArch64, RISC-V64, SPARC64, MIPS, XCOFF) maintained inside Boost; pick libco when you want a tiny C library with no build system. The other siblings are compute kernels, not context switchers.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (Boost compiled library with per-platform assembly; fiber and continuation front ends are headers) |
| **Dependencies** | Boost headers (Config, Assert, Core and others); GNU as and the C preprocessor on POSIX, MASM on Windows x86, ARMasm on Windows ARM; the benchmark also links Boost.Chrono and Boost.ProgramOptions |
| **Minimum toolchain** | C++11; documented minimums MSVC 14.0 (VS2015), GCC 4.8, Clang 3.4; b2 or CMake (BOOST_CONTEXT_IMPLEMENTATION, BOOST_CONTEXT_ABI, BOOST_CONTEXT_BINARY_FORMAT cache variables) |
| **Platforms** | fcontext: x86_64 (SysV/x32 ELF, MS PE, Mach-O), i386, arm/aarch64 (ELF, Mach-O, PE), ppc32/ppc64 (ELF, XCOFF, Mach-O), mips O32/N64, riscv64, s390x, sparc64, loongarch64, alpha; elsewhere ucontext_t or WinFiber fallback |
| **Thread safety** | A fiber or continuation runs on one thread at a time and may be migrated to another thread between resumes (README); handles are one-shot and move-only, so no concurrent use of one handle. Not documented further. |
| **Drop-in for the baseline** | partial: replaces ucontext_t switching only after porting to the fiber or callcc API; the same library can be rebuilt with context-impl=ucontext, so behaviour other than the signal mask matches |

## Gotchas

- Harness detail: the 'CPU cycles' column is rdtsc ticks at the TSC's nominal rate, not core cycles (1130/547 = 2.07 and 19/9 = 2.1 ticks per ns, which also points to a 2.1 GHz clock rather than the doc's 2.2 GHz); the ns figures are integer-truncated after dividing by 1,000,000 round trips and by 2, so '9 ns' means 9.0-9.99 ns and the speedup is 55-61x, from one unrepeated run.
- Measured through the callcc()/continuation wrapper, not raw jump_fcontext (performance/fcontext exists but is not in the table) and not the newer fiber API; the Windows-Fiber column cannot come from the Linux machine named on the page.
- An exception escaping a context-function calls std::terminate; do not switch from inside a catch block; catch(...) handlers must rethrow detail::forced_unwind or destroying an unfinished fiber cannot unwind its stack.
- With -fstack-protector define BOOST_CONTEXT_TLS_STACK_PROTECTOR; on Windows with fcontext turn off /GL, use /EHs instead of /EHsc and pass asmflags=\safeseh; issue #327 (open) reports detail/invoke.hpp failing to compile where std::result_of is gone (removed in C++20).

## Known shortcomings

- 2017 run with gcc 6.3.1 (doc/performance.qbk); the baseline cost is mostly glibc swapcontext's sigprocmask syscall (Boost's continuation_ucontext wrapper); the Windows-Fiber column cannot come from the stated Linux box.
- Enricher: the 'CPU cycles' column is rdtsc ticks, not core cycles (1130/547 = 2.07 per ns, a 2.1 GHz TSC rather than the documented 2.2 GHz); ns figures are integer-truncated single runs, so the speedup is 55-61x rather than a flat 61x; measured through the callcc wrapper, not raw jump_fcontext; open platform bugs: PPC64 FP14-FP31 not preserved (#232), Windows ARM64 ontop_fcontext 16-byte SP skew (#336), std::result_of compile failure (#327); fcontext does not preserve the signal mask; ASan only with the slow ucontext backend.

## Caveats and trade-offs

Numbers come from the project's own doc table (about 2017, gcc-6.3.1, Broadwell-era Xeon) and were not re-run; the callcc()/continuation API they measure is now the older of Boost.Context's two APIs (fiber is the newer one). Compiler flags are given as b2 build properties (variant=release, optimization=speed, plus link=static, threading=multi, -DBOOST_DISABLE_ASSERTS in performance/callcc/Jamfile.v2), not literal -O flags. The page does not say how the ucontext_t column was built; the context-impl=ucontext recipe is inferred from build/Jamfile.v2. The Windows-Fiber column cannot have been measured on the Linux machine the page names, so the table mixes at least two setups without saying so. The ucontext baseline is Boost's wrapper around glibc ::swapcontext, which makes a signal-mask system call per swap on x86-64 Linux, so the \~61x gap mostly measures avoiding that call rather than hand-written assembly versus compiled code; a context switch cannot be written in portable C, so no -O3 C comparison exists. Other user-space switchers (libco, minicoro) are not compared. Per-switch figures are a round trip divided by two after subtracting measured clock overhead. The assembly is only part of the repo (src/asm/jump_\*/make_\*/ontop_\* per platform).

Hand-written assembly per ABI and OS: src/asm holds jump_, make_ and ontop_ files for x86_64, i386, arm, arm64, mips32/64, ppc32/64, riscv64, s390x, sparc64, loongarch64 and alpha across ELF, Mach-O, PE and XCOFF. Stackful switch only; the caller supplies or allocates stacks. ucontext and Windows Fiber backends remain selectable as portable fallbacks (context-impl feature).

## Maintenance

Actively maintained (latest commit 2026-10-07, merges through Sept-Oct 2026 adding Alpha support and ASan fixes) and BSL-1.0, but the performance table has not been re-run since the gcc-6.3.1 era, and several platform assembly bugs (PPC64 FP registers #232, Windows ARM64 ontop SP skew #336) are open without maintainer fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** doc/performance.qbk gives 9 ns / 19 cycles (fcontext_t) versus 547 ns / 1130 cycles (ucontext_t) per switch, states gcc-6.3.1, b2 variant=release optimization=speed and dual Xeon E5-2620v4, and the harness is public (performance/callcc/performance.cpp with performance/callcc/Jamfile.v2, clock.hpp overhead correction, cycle_x86-64.hpp). Code, compiler, flags and CPU model are all present, so A holds.
- **Verifier notes:** Numbers match doc/performance.qbk exactly; 547/9 = 60.8x and 1130/19 = 59.5x (derived from page data). Main shortcomings: old single first-party run, Windows-Fiber column inconsistent with the stated Linux test machine, baseline cost dominated by glibc swapcontext's sigprocmask system call; the doc's 2.2 GHz clock also differs from the E5-2620 v4's usual 2.1 GHz base rating (not re-checked here). Not a duplicate: Boost.Fiber (wave 11) builds on it but is a separate library.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-106 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/doc/performance.qbk>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/callcc/Jamfile.v2>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/callcc/performance.cpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/fcontext/performance.cpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/clock.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/cycle.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/build/Jamfile.v2>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/include/boost/context/continuation_ucontext.hpp>
  - <https://github.com/boostorg/context>
  - <https://github.com/boostorg/context/commits/develop>
- **Sources the enricher read:**
  - <https://github.com/boostorg/context>
  - <https://github.com/boostorg/context/commits/develop>
  - <https://github.com/boostorg/context/issues>
  - <https://github.com/boostorg/context/issues/232>
  - <https://github.com/boostorg/context/issues/327>
  - <https://github.com/boostorg/context/issues/336>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/README.md>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/doc/performance.qbk>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/doc/context.qbk>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/doc/overview.qbk>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/doc/requirements.qbk>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/doc/architectures.qbk>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/doc/rationale.qbk>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/doc/fiber.qbk>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/doc/callcc.qbk>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/doc/stack.qbk>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/callcc/Jamfile.v2>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/callcc/performance.cpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/fcontext/performance.cpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/clock.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/cycle.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/performance/cycle_x86-64.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/build/Jamfile.v2>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/include/boost/context/continuation_ucontext.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/include/boost/context/continuation_fcontext.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/include/boost/context/fiber_fcontext.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/include/boost/context/fiber.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/include/boost/context/continuation.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/include/boost/context/detail/config.hpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/src/continuation.cpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/src/fiber.cpp>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/src/asm/jump_x86_64_sysv_elf_gas.S>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/src/asm/make_x86_64_sysv_elf_gas.S>
  - <https://raw.githubusercontent.com/boostorg/context/HEAD/src/asm/jump_arm64_aapcs_elf_gas.S>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/boostorg/context`) · [data/wave13/enrich/raw/github_com_boostorg_context.json](../../../data/wave13/enrich/raw/github_com_boostorg_context.json) (enrichment confidence 0.82)

</details>
