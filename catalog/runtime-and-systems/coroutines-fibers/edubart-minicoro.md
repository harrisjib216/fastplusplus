# minicoro

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Unlicense OR MIT-0 (public domain or MIT No Attribution)` · 🟡 stale

> Single-header C stackful asymmetric coroutines with a hand-written assembly switch, about 40x cheaper than ucontext on x86-64 Linux.

| | |
|---|---|
| **Beats** | POSIX ucontext (swapcontext) |
| **Claimed result** | Linux x86_64 context switch 9 cycles (assembly) versus 352 cycles (ucontext); initialize 31 versus 383 cycles; uninitialize 14 vs 14. Windows: assembly switch 33 cycles vs Windows fibers 69 cycles, initialize 74 vs 10564 cycles (README table). |
| **Workload** | tests/benchmark.c context-switch cycle count (rdtsc), thread_local path excluded |
| **Metric** | latency |
| **Hardware** | Intel Core i7-8750H @ 2.20GHz |
| **Compiler and flags** | gcc (version not stated), -O3 -flto -march=native -DNDEBUG -DMCO_NO_MULTITHREAD (tests/Makefile); harness tests/benchmark.c (rdtsc) |
| **Adoption** | 993 stars |
| **Last commit** | 2024-12-07 |
| **Links** | [repository](https://github.com/edubart/minicoro) · [benchmark](https://github.com/edubart/minicoro#benchmarks) |

## Verdict

First-party README table on an Intel Core i7-8750H: x86-64 Linux assembly backend 9 cycles per switch, 31 cycles init, 14 uninit, versus 352/383/14 for the library's own ucontext backend; on Windows 33/74/14 versus Windows fibers 69/10564/11167. The harness is tests/benchmark.c (10M resume/yield pairs timed with rdtsc, 100k init/uninit on pre-allocated memory), gcc with -O3 -flto -march=native -DMCO_NO_MULTITHREAD; gcc version not stated.

## Use it when

- Generators, iterators or scripting-language coroutines in C where you resume and yield millions of times and ucontext's syscall per switch dominates
- Embedding coroutines in a game engine or language runtime that must run on Windows, macOS, Linux, Android, iOS, RISC-V and the web from one file
- Projects that need a public-domain/MIT-0 single header with custom allocator hooks and ASan/TSan/Valgrind support
- Many coroutines with uneven stack use, with MCO_USE_VMEM_ALLOCATOR (about 8 KB physical per coroutine for 100k coroutines with \~2 MB reserved, per README)

## Skip it when

- C++ code that throws exceptions across a yield or relies on destructors of a suspended coroutine: the README says to avoid exceptions and to resume to completion for RAII (issue #20 asks for unwinding support, not provided)
- When you need symmetric transfer, a scheduler, I/O integration or work-stealing: it is only a switch primitive (compare libdill, libgo, Marl)
- If you need proof it beats Boost.Context, libco or libaco: the README only compares against its own ucontext and fiber backends
- OpenBSD amd64 (open issue #27, crash) and WASI SDK with the asyncify backend (README says it fails)
- Deep recursion in coroutines with default stacks: 56 KB default, overflow is only detected after the fact at yield and is otherwise undefined

## How it is fast

The x86-64 SysV switch (_mco_switch) is 16 instructions: it stores rip/rsp/rbp/rbx/r12-r15 into the from-buffer, loads them from the to-buffer and jumps; it saves no signal mask, so there is no sigprocmask syscall as in glibc swapcontext. The Windows variant also saves xmm6-xmm15 and the TIB stack fields. Init only lays out a stack and a context buffer (inspired by Mike Pall's Lua Coco).

## Compared with alternatives

Pick minicoro over libaco or libco when you need one portable, permissively licensed header that also covers Windows, ARM, RISC-V and WebAssembly; pick libdill or libgo when you want a scheduler and I/O on top, and Neco/llco if you want a similar single-file C design with a runtime included.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (libc; ucontext or Windows fibers only on fallback paths) |
| **Minimum toolchain** | C89 compiler for the library; thread_local/_Thread_local/__thread needed for multithreaded use |
| **Platforms** | x86-64 and i686 (Linux, macOS, Windows), ARM/ARM64 (Android, iOS, macOS, Raspberry Pi), RISC-V rv32/rv64, WebAssembly via Emscripten; ucontext fallback elsewhere |
| **Thread safety** | mco_coro objects are not thread safe (guard with a mutex); the current-coroutine pointer is thread_local unless MCO_NO_MULTITHREAD |
| **Drop-in for the baseline** | partial: replaces swapcontext-based coroutines but with its own mco_\* API; mco_init/mco_uninit allow caller-allocated storage |

## Gotchas

- The README cycle numbers come from tests/benchmark.c built with -O3 -flto -march=native -DNDEBUG -DMCO_NO_MULTITHREAD (tests/Makefile), so the 9-cycle switch excludes the thread_local lookup of the default build; cycles are rdtsc reference ticks, not core cycles
- The switch returns with an indirect jmp rather than ret, which defeats the return-stack predictor; a minicoro-derived fork (PavelGuzenfeld/ucoro #11) measured about 3x Boost.Context before fixing this
- Do not use thread_local inside coroutine bodies if coroutines migrate between threads: the compiler may cache the TLS address
- The x86-64 SysV switch does not save MXCSR or the x87 control word (Boost.Context does), so code that changes FP rounding modes inside a coroutine leaks the setting to the resumer

## Known shortcomings

- The 9-cycle number excludes the thread_local path; the switch ends in an indirect jmp, not ret; no MXCSR or x87 control-word save on SysV. gcc version is not stated.

## Caveats and trade-offs

Baseline is ucontext, not Boost.Context or libco; no cross-library comparison in the README; compiler and flags not stated. A third-party issue (PavelGuzenfeld/ucoro #11) measured a minicoro-derived x86-64 switch at about 3x Boost.Context before a return-mispredict fix, so it may not beat Boost.Context. Public domain / MIT-0 has no patent grant.

Single-header C asymmetric coroutines; stack-per-coroutine memory; avoid C++ exceptions across switches; fiber and asyncify backends elsewhere.

## Maintenance

Stale since the 2024-12-07 commit with 7 open issues (OpenBSD crash, ASan warning, red-zone stack waste), but 993 stars, public domain or MIT-0, and one file that is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks table (first-party) gives Linux x86_64 assembly 9/31/14 cycles vs ucontext 352/383/14 cycles for switch/init/uninit on an i7-8750H; no benchmark code path, compiler or flags stated, so C.
- **Verifier notes:** Numbers, hardware, license (Unlicense or MIT-0), 993 stars and last commit 2024-12-07 all verified on github.com. Baseline is the library's own ucontext/fibers backends, not another coroutine library; no patent grant.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/edubart/minicoro>
  - <https://github.com/edubart/minicoro#benchmarks>
  - <https://raw.githubusercontent.com/edubart/minicoro/HEAD/README.md>
  - <https://raw.githubusercontent.com/edubart/minicoro/HEAD/LICENSE>
  - <https://github.com/edubart/minicoro/commits>
- **Sources the enricher read:**
  - <https://github.com/edubart/minicoro>
  - <https://raw.githubusercontent.com/edubart/minicoro/HEAD/README.md>
  - <https://raw.githubusercontent.com/edubart/minicoro/HEAD/minicoro.h>
  - <https://github.com/edubart/minicoro/tree/main/tests>
  - <https://raw.githubusercontent.com/edubart/minicoro/HEAD/tests/benchmark.c>
  - <https://raw.githubusercontent.com/edubart/minicoro/HEAD/tests/Makefile>
  - <https://github.com/edubart/minicoro/issues?q=is%3Aissue>
  - <https://github.com/edubart/minicoro/issues/11>
  - <https://github.com/edubart/minicoro/issues/20>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/edubart/minicoro`) · [data/wave11/enrich/raw/github_com_edubart_minicoro.json](../../../data/wave11/enrich/raw/github_com_edubart_minicoro.json) (enrichment confidence 0.75)

</details>
