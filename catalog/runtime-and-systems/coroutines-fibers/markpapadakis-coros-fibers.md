# coros-fibers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Small x86-64 Linux stackful coroutine switch (libcoro-style assembly) plus a priority fiber scheduler; no baseline compared.

| | |
|---|---|
| **Beats** | none named (ABI-compliant coroutine switch; libco-style) |
| **Claimed result** | No comparison: README reports 58 to 62 million context switches/s with coro_transfer/coro_restore and 21 million/s through the fibers framework on a Xeon 2 GHz system (about 16-17 ns per switch, derived from page data). |
| **Workload** | Coroutine/fiber context switch rate on x86-64, low-level coro_transfer and fiber scheduler. |
| **Metric** | latency |
| **Hardware** | Xeon 2 GHz |
| **Adoption** | 63 stars |
| **Last commit** | 2016-08-18 |
| **Links** | [repository](https://github.com/markpapadakis/coros-fibers) · [benchmark](https://github.com/markpapadakis/coros-fibers/blob/master/README.md) |

## Verdict

The author reports 58-62 million raw coro_transfer switches per second and 21 million per second through the fiber scheduler on an unnamed 2 GHz Xeon (about 16-17 ns and 48 ns per switch, derived from page data), with no baseline, no compiler version and no published run; the switch benchmark code exists only as disabled example code in coroutines.cpp.

## Use it when

- Reading or borrowing a minimal x86-64 System V context switch (about 30 lines of assembly) for your own runtime.
- Single-threaded, Linux x86-64 event loops that want stackful fibers with simple priorities and are willing to vendor the code.
- Learning material: the comments walk through the ABI rules, the stack layout for new coroutines and how Go's scheduler compares.

## Skip it when

- Any platform other than Linux x86-64: the header has #error for everything else.
- Production use without a review: last commit 2016-08-18, 2 commits, no tests, and it depends on a bundled 'Switch' utility library (26 headers) plus valgrind headers.
- Deep call chains in fibers: scheduler fibers get a 4096-byte malloc'd stack with no guard page (get_fiber calls alloc(4096) without protect).
- When you need a measured comparison: pick a sibling like minicoro or libaco that benchmarks against ucontext or libco.

## How it is fast

coro_transfer is about 15 instructions of hand-written assembly: push the six System V callee-saved registers (rbp, rbx, r12-r15), store rsp, load the other context's rsp, pop six registers and ret. It skips the signal-mask syscall and FPU state that swapcontext saves. The scheduler picks the next fiber in O(1) with a trailing-zeros scan of an 8-bit ready mask over intrusive doubly linked lists, and recycles fibers and stacks from free lists.

## Compared with alternatives

Rarely: minicoro (9 cycles vs 352 for ucontext, cross-platform, single header) and libaco (measured against libco) cover the same niche with benchmarks and maintenance; pick coros-fibers only if you want its tiny priority scheduler as a starting point on Linux x86-64.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | bundled Switch/ headers (switch.h, switch_ll.h, switch_vector.h, timings.h and others); valgrind/valgrind.h because VALGRIND_SUPPORT is hard-defined |
| **Minimum toolchain** | C++14 (Makefile uses -std=c++14 -O3); GCC/Clang inline asm and attributes |
| **Platforms** | Linux x86-64 only |
| **Thread safety** | Scheduler and main context are thread_local, so one scheduler per OS thread; fibers cannot migrate between threads (not documented beyond that) |
| **Drop-in for the baseline** | no |

## Gotchas

- Bug in the low-level API: coro_init(ctx, func, arg, stack) passes func and arg to coro_init_with_trampoline, which ignores both and never writes them to the stack; the default coroInit trampoline then reads func and arg from 16(%rbp) and 8(%rbp), and its own comment says this does not work at -O1 or higher (the Makefile builds at -O3). Only the custom-trampoline path, which the fiber scheduler and the switch benchmark use, is usable.
- The switch saves only the six general-purpose callee-saved registers, not the MXCSR or x87 control words that the ABI also treats as callee-saved, so code that changes rounding modes per coroutine will leak them across switches.
- The benchmark behind the 58-62 million switches/s figure is in coroutines.cpp under #ifdef EXAMPLE but inside #if 0, and it calls s1.Alloc(4096) where the method is alloc, so it does not compile as shipped; the enabled example times 65,536 scheduler yields between two fibers.
- The destructor's non-priority branch compares against &read instead of &ready, so building with HAVE_FIBER_PRIOS undefined fails.

## Known shortcomings

- coro_init bug: func and arg are never stored and the trampoline reads garbage from rbp (the code's own comment says it breaks at -O1 and above; the Makefile uses -O3). The measured numbers are not affected since the benchmark uses the custom-trampoline path. The switch bench lives in coroutines.cpp under #ifdef EXAMPLE inside #if 0 and does not compile (s1.Alloc vs alloc). Fiber stacks are 4096 B with no guard page; MXCSR and the x87 control word are not saved.

## Caveats and trade-offs

No baseline compared anywhere; no benchmark code, compiler or flags; 2016-era single-sentence claim; first-party. Based on the libcoro transfer design. Strictly meets the no-baseline-comparison reject criterion; downgraded to D instead so the orchestrator can apply keep-and-document.

x86-64 only; low-level coro API plus scheduler; author says tracking fewer registers could be faster but breaks ABI.

## Maintenance

Abandoned since 2016 with 2 commits; MIT-licensed and small enough to copy, but the low-level coro_init path is broken and it needs its bundled Switch headers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now D.
- **Tier reason:** README states 58-62 million switches/s (coro_transfer/coro_restore) and 21 million/s via fibers on 'a Xeon 2Ghz system', but compares against nothing and ships no benchmark code or methodology; absolute self-reported rates with no baseline give no faster-than evidence, so D.
- **Verifier notes:** Arguably a reject (no-baseline-comparison, tier D, 63 stars); left as downgrade to D for the keep-and-document rule. License MIT confirmed from LICENSE file; last commit 2016-08-18 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/markpapadakis/coros-fibers/blob/master/README.md>
  - <https://raw.githubusercontent.com/markpapadakis/coros-fibers/HEAD/README.md>
  - <https://raw.githubusercontent.com/markpapadakis/coros-fibers/HEAD/LICENSE>
  - <https://github.com/markpapadakis/coros-fibers/commits>
- **Sources the enricher read:**
  - <https://github.com/markpapadakis/coros-fibers>
  - <https://github.com/markpapadakis/coros-fibers/tree/master/Switch>
  - <https://raw.githubusercontent.com/markpapadakis/coros-fibers/HEAD/README.md>
  - <https://raw.githubusercontent.com/markpapadakis/coros-fibers/HEAD/coroutines.h>
  - <https://raw.githubusercontent.com/markpapadakis/coros-fibers/HEAD/coroutines.cpp>
  - <https://raw.githubusercontent.com/markpapadakis/coros-fibers/HEAD/Makefile>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/markpapadakis/coros-fibers`) · [data/wave11/enrich/raw/github_com_markpapadakis_coros_fibers.json](../../../data/wave11/enrich/raw/github_com_markpapadakis_coros_fibers.json) (enrichment confidence 0.65)

</details>
