# libgo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Go-style stackful coroutine runtime for C++11 with multi-thread scheduler and syscall hooks; switches faster than libco and ucontext.

| | |
|---|---|
| **Beats** | libco (Tencent), Linux ucontext |
| **Claimed result** | Gist table (2019-09-29), libgo (current version) vs libco (static stack pool) vs linux ucontext: 1-coroutine switch 30 ns vs 84 ns vs 439 ns; 30000-coroutine switch 150 ns vs 450 ns vs 890 ns. The 1000-coroutine switch cell for libgo reads '32 us' on the page (likely a typo for ns; libco 168 ns, ucontext 505 ns). Creation is slower for libgo (8.3 us vs libco 3.9 us at 1000). C++20 stackless coroutines are faster than all stackful rows. |
| **Workload** | Context switch overhead at 1, 1000 and 30000 coroutines, measured by a third party (libcopp author) in a gist across libcopp, libco, libgo, ucontext and goroutines. |
| **Metric** | latency |
| **Hardware** | not stated (CPU unspecified) |
| **Compiler and flags** | g++ -O2 -g -DNDEBUG -ggdb -Wall -Werror -fPIC (per gist); compiler version not stated |
| **Adoption** | 3.3k stars; vcpkg port 'libgo' |
| **Last commit** | 2023-03-10 |
| **Links** | [repository](https://github.com/yyzybb537/libgo) · [benchmark](https://gist.github.com/owent/1842b56ac1edd5a7db54590d41af1c44) |

## Verdict

A gist by the libcopp author (2019-09-29, g++ -O2, CPU and compiler version not stated, co_yield ping-pong) measured libgo switch cost at 30 ns for one coroutine and 150 ns at 30000 coroutines vs libco (static stack pool) 84 and 450 ns and Linux ucontext 439 and 890 ns; libgo's 1000-coroutine cell prints '32 us', likely a typo, and older 2018 libgo builds were much slower.

## Use it when

- Server code on Linux that must call blocking client libraries (MySQL, Redis) from many concurrent tasks without one OS thread per connection.
- Porting Go-style designs (goroutines plus channels) to C++11 with a built-in multi-thread scheduler.
- Workloads with tens of thousands of mostly idle coroutines where switch latency matters more than creation cost (gist: 150 ns switch at 30000 coroutines vs libco 450 ns).
- Replacing a ucontext-based coroutine layer on x86-64 Linux, macOS or Windows (VS2015/2017).

## Skip it when

- New projects wanting a maintained library: last commit 2023-03-10, open issue #292 asks whether the project is dead, and several crash reports (#216, #248, #251, #280) are unanswered.
- Creation-heavy workloads: creating 1000 coroutines took 8.3 us vs 3.9 us for libco in the same gist.
- Memory-tight deployments: stacks are malloc'd per coroutine at 1 MB by default (README: 1 million coroutines need about 4.5 GB); no shared-stack mode like libco's.
- Code that relies on thread-local storage or non-reentrant TLS-based libc functions; coroutines can resume on other threads and the README warns against TLS.
- When C++20 stackless coroutines fit: the same gist shows them faster than every stackful row.

## How it is fast

Context switches use Boost.Context's hand-written fcontext assembly (make_fcontext/jump_fcontext, copied from a vendored boost.context and renamed libgo_\* at configure time), which saves only callee-saved registers instead of the signal mask and full register set that swapcontext handles. Scheduling is per-thread processors (P) with load-based work stealing; a dispatcher thread steals tasks from a P whose coroutine runs past a timeout.

## Compared with alternatives

Pick libgo over libco, libaco or libcopp when you want a whole runtime (multi-thread scheduler, channels, libc hooks) rather than a bare switch primitive; pick minicoro or libaco instead for the lowest raw switch cost in a single thread, and Boost.Cobalt or C++20 coroutines when stackless is acceptable and maintenance matters.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at runtime (vendored boost.context sources used at configure time for the asm; Boost needed only for the tests); static_hook archive for fully static links |
| **Minimum toolchain** | C++11; CMake; VS2015 or later on Windows |
| **Platforms** | Linux, macOS, Windows 7+ (x86, x64); other CPUs only as far as the vendored boost.context asm selection covers them (not documented) |
| **Thread safety** | Multi-threaded scheduler with work stealing; channels and co_mutex are the documented synchronization primitives; TLS usage across switches is unsafe |
| **Drop-in for the baseline** | no |

## Gotchas

- Syscall hooking interposes libc symbols; link libgo first (and -ldl), and for static builds use -Wl,--whole-archive -lstatic_hook -lc -lpthread, or hooks silently do not apply.
- Coroutine stacks come from std::malloc with no guard page by default (protect_stack_page = 0), so a stack overflow corrupts the heap unless you enable protect pages.
- config.h warns that a 2 MB stack_size commits about 10x more memory than 1 MB on Linux; the gist's 1000+ coroutine rows used 2 MB stacks.
- Build runs a b2 bootstrap inside third_party/boost.context to pick the asm file, so cross-compiling needs care.

## Known shortcomings

- The default stack_size is 1 MB (config.h) while the gist's 1000+ coroutine rows used 2 MB stacks; the switch asm is vendored from boost.context; no guard page by default. Issue 292 asks whether the project is dead; crash issues 216, 248, 251 and 280 are unanswered.

## Caveats and trade-offs

Gist written by a competing library author (libcopp); CPU not stated, compiler version not stated. The table's libgo 1000-coroutine switch cell reads '32 us', probably a typo for ns. libgo uses 2 MB stacks vs 64 KB for libco/libcopp; a separate row for 2018 libgo built on boost is much slower (197 ns single switch). Gist comments ask for more libraries (librf, boost::fiber) and memory metrics; they do not dispute the libgo numbers. libgo's own README compares only against Go (2018 MacBook i5, graphs only). Boost.Context was not a column. Last commit 2023-03-10, over 3 years old.

Full multi-thread scheduler, channels, hooks of libc blocking calls; heavier than a bare context switch library. Uses boost.context internally in newer versions.

## Maintenance

Abandoned since March 2023 with unanswered crash reports, but MIT-licensed, packaged in vcpkg and still usable as a reference runtime.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Third-party gist by the libcopp author (2019-09-29) with a table covering libgo, libco and linux ucontext; flags given (g++ -O2 -g -DNDEBUG) but no compiler version or CPU model and no well-known suite status, so C.
- **Verifier notes:** Numbers match the gist except the 1000-coroutine libgo cell, which the page prints as 32 us. Last commit 2023-03-10 is more than 3 years before today, so abandoned rather than stale. MIT and 3.3k stars confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** first-party gist
- **Pages the verifier opened:**
  - <https://gist.github.com/owent/1842b56ac1edd5a7db54590d41af1c44>
  - <https://github.com/yyzybb537/libgo>
  - <https://github.com/yyzybb537/libgo/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yyzybb537/libgo/HEAD/README.md>
  - <https://raw.githubusercontent.com/yyzybb537/libgo/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yyzybb537/libgo/HEAD/libgo/context/context.h>
  - <https://raw.githubusercontent.com/yyzybb537/libgo/HEAD/libgo/context/fcontext.cpp>
  - <https://raw.githubusercontent.com/yyzybb537/libgo/HEAD/libgo/common/config.h>
  - <https://raw.githubusercontent.com/yyzybb537/libgo/HEAD/libgo/common/config.cpp>
  - <https://raw.githubusercontent.com/yyzybb537/libgo/HEAD/libgo/scheduler/scheduler.h>
  - <https://raw.githubusercontent.com/yyzybb537/libgo/HEAD/third_party/select_asm.sh>
  - <https://github.com/yyzybb537/libgo/tree/master/libgo/context>
  - <https://github.com/yyzybb537/libgo/issues?q=is%3Aissue+crash>
  - <https://gist.github.com/owent/1842b56ac1edd5a7db54590d41af1c44>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/yyzybb537/libgo`) · [data/wave11/enrich/raw/github_com_yyzybb537_libgo.json](../../../data/wave11/enrich/raw/github_com_yyzybb537_libgo.json) (enrichment confidence 0.75)

</details>
