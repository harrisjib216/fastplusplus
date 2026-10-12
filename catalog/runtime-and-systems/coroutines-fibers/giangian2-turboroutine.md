# TurboRoutine

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-3.0` · 🟢 active

> Small x86-64 Linux C library for stackful coroutines with an assembly context switch; README claims about 70x faster round trips than swapcontext.

| | |
|---|---|
| **Beats** | POSIX ucontext (swapcontext) |
| **Claimed result** | About 30 ns round trip vs about 2 us for ucontext swapcontext (\~70x, README) and about 83 us for two kernel threads handing off via a condition variable (\~2700x); README notes WSL2 inflates syscall costs for both alternatives. |
| **Workload** | Round-trip resume plus yield cost for hand-written x86-64 assembly switch versus swapcontext and kernel thread handoff. |
| **Metric** | latency |
| **Hardware** | Intel Core i5-7200U under WSL2 |
| **Compiler and flags** | gcc 13.3 -O2 |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-18 |
| **Links** | [repository](https://github.com/giangian2/TurboRoutine) · [benchmark](https://github.com/giangian2/TurboRoutine) |

## Verdict

First-party README table only: on an Intel Core i5-7200U under WSL2 with gcc 13.3 -O2, a resume-plus-yield round trip takes about 30 ns versus about 2 us for glibc swapcontext (about 70x) and about 83 us for a two-thread condition-variable handoff. The switch benchmark source is not in the repo (src/main.c is a self-checking demo of 256 coroutines on 4 workers), and the README itself says WSL2 inflates the syscall cost of both baselines.

## Use it when

- x86-64 Linux C code that needs generators or pipelines yielding from deep call stacks, where ucontext's per-switch syscall shows up
- Slicing long CPU-bound loops (graph traversals, as in the author's TurboGraph) into short cooperative pieces on a worker pool, with one co_checkpoint() line per loop
- Work-stealing or migrating schedulers, where a coroutine is resumed on a thread other than the one that started it (header lookup uses rsp, not TLS)
- Projects that want gdb backtraces through switches (full CFI) and valgrind memcheck/callgrind support for coroutine stacks
- GPL-3.0-compatible codebases small enough to vendor three files

## Skip it when

- Anything outside x86-64 System V Linux: no AArch64, macOS or Windows port
- Code needing deep recursion or large stack frames: stacks are fixed at 64 KB minus a 4 KB guard page (compile-time constant in CoroAbi.h)
- When you want an established, faster or permissively licensed switch: minicoro (9 cycles per switch), libaco, Boost.Context or libdill; TurboRoutine is GPL-3.0 with 1 star and 11 commits
- When you need a scheduler, I/O awaiting or channels out of the box: README lists these as roadmap, not implemented
- Switching from signal handlers, or binaries that require CET shadow stacks (the .S file deliberately drops the SHSTK marking, which disables it for the whole linked binary)

## How it is fast

The switch is a hand-written assembly routine that saves only the callee-saved registers (rbx, rbp, r12-r15) plus MXCSR and the x87 control word on the current stack, swaps rsp through the 64-byte header, and returns. Unlike glibc swapcontext it makes no sigprocmask system call. The running coroutine is found by masking rsp, since every 64 KB slot is aligned to 64 KB and the header sits at the top: (rsp | 0xFFFF) - 63. This takes two instructions, reads no thread-local storage, and lets GCC hoist co_current() out of loops, so the co_checkpoint() fast path is a load, a decrement, a store and a branch.

## Compared with alternatives

Pick it over minicoro or libaco only if you specifically want TLS-free header lookup from rsp (cheap migration across a thread pool) plus built-in co_checkpoint slicing, and GPL-3.0 is fine; for raw switch speed minicoro (9 cycles vs 352 for ucontext) and libdill (about 16 ns) report better numbers, and libaco and libcopp are far more mature.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (POSIX threads; valgrind headers optional) |
| **Minimum toolchain** | C11, gcc (GNU assembler with Intel syntax; uses __has_include and __attribute__((cleanup))) |
| **Platforms** | x86-64 Linux only (System V ABI) |
| **Thread safety** | co_create/co_destroy lock a pool mutex; a coroutine may migrate between threads but must be resumed by at most one thread at a time, and a scheduler must publish it only after co_resume returns |
| **Drop-in for the baseline** | no |

## Gotchas

- fs (the TLS base) is not switched: after migration errno, pthread_self() and _Thread_local variables belong to the new thread; README says to hold no lock or thread-local address across a yield, but does not discuss TLS addresses the compiler itself may keep across the co_yield call.
- co_destroy does not check state or double release: destroying a running coroutine or releasing a slot twice silently corrupts the free list. Resuming a DONE coroutine traps on ud2.
- co_yield, co_current and co_checkpoint are only valid on a coroutine stack; calling them on a normal thread stack masks rsp into an unrelated address (use co_pool_contains() to check).
- Linking the assembly object drops the GNU property note, so CET shadow stack is disabled for the whole binary, not only the coroutine code.

## Known shortcomings

- The switch benchmark source is missing from the repo. CET shadow stack is disabled for the whole binary, co_destroy has no double-free or state check, and fs/TLS are not switched on migration.

## Caveats and trade-offs

The README does not mention Boost.Context or libco at all (the earlier caveat claiming it says so was wrong); it compares only against swapcontext, which does a sigprocmask syscall per switch, and a kernel-thread handoff, both inflated by WSL2. The switch-cost benchmark source is not published in the repo. A 30 ns round trip is likely slower than Boost.Context or minicoro-class switches (not measured here). x86-64 System V only, fixed 64 KB stacks, no scheduler yet. GPL-3.0. Tiny project (1 star, 11 commits). Off-baseline entry.

x86-64 Linux only; GPL-3.0; stack-pointer auto-discovery; 11 commits.

## Maintenance

Active (last commit 2026-09-18) but a one-person project with 1 star, 11 commits and no issues filed; GPL-3.0 and about 400 lines, so easy to read and vendor if the license fits.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance table gives first-party round-trip numbers (\~30 ns vs \~2 us swapcontext, \~83 us condvar thread handoff) on an i5-7200U under WSL2 with gcc 13.3 -O2, but the switch-cost benchmark code is not in the repo (only src/main.c demo and callgrind tools), so not A.
- **Verifier notes:** Metadata from github.com pages (gh api blocked): 1 star, GPL-3.0 LICENSE text confirmed, last commit 2026-09-18. Numbers match README.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/giangian2/TurboRoutine>
  - <https://github.com/giangian2/TurboRoutine/commits>
  - <https://raw.githubusercontent.com/giangian2/TurboRoutine/HEAD/README.md>
  - <https://raw.githubusercontent.com/giangian2/TurboRoutine/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/giangian2/TurboRoutine>
  - <https://raw.githubusercontent.com/giangian2/TurboRoutine/HEAD/README.md>
  - <https://raw.githubusercontent.com/giangian2/TurboRoutine/HEAD/src/coro_x86_64.S>
  - <https://raw.githubusercontent.com/giangian2/TurboRoutine/HEAD/src/coro.c>
  - <https://raw.githubusercontent.com/giangian2/TurboRoutine/HEAD/include/Coro.h>
  - <https://raw.githubusercontent.com/giangian2/TurboRoutine/HEAD/include/CoroAbi.h>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/giangian2/turboroutine`) · [data/wave11/enrich/raw/github_com_giangian2_turboroutine.json](../../../data/wave11/enrich/raw/github_com_giangian2_turboroutine.json) (enrichment confidence 0.7)

</details>
