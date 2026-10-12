# libfiber (iqiyi)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-3.0` · 🟢 active

> C stackful coroutine runtime with libc network hooks; first-party echo-server chart shows about 1.6-1.7x libco's QPS.

| | |
|---|---|
| **Beats** | libco (Tencent) |
| **Claimed result** | Bar chart only (values read from res/benchmark.png, approximate): at 100 concurrency libfiber \~232k QPS vs libmill \~201k, golang \~155k, libco \~147k; at 200 \~214k vs libco \~136k; at 500 \~196k vs libco \~128k; at 1000 \~178k vs libmill \~132k, golang \~123k, libco \~106k (about 1.6-1.7x vs libco, derived from page data) |
| **Workload** | TCP echo server IOPS at 100/200/500/1000 concurrent connections, libfiber sample vs libmill, Go and libco samples. |
| **Metric** | throughput |
| **Adoption** | 817 stars |
| **Last commit** | 2026-01-04 |
| **Links** | [repository](https://github.com/iqiyi/libfiber) · [benchmark](https://github.com/iqiyi/libfiber) |

## Verdict

A first-party bar chart (res/benchmark.png) shows echo-server QPS at 100 to 1000 connections: libfiber about 232k at 100 and 178k at 1000, against libco about 147k and 106k (about 1.6-1.7x, derived from page data), with libmill and a Go server in between. No hardware, OS, compiler or flags are given; the libco and libmill server sources are in the repo's benchmark/ directory and the client is acl's lib_fiber/samples/client2.

## Use it when

- Network servers or clients in C or C++ on Linux/BSD/macOS that want sequential code with thousands of concurrent connections
- Making existing blocking client libraries (MySQL driver, DNS lookups via getaddrinfo) coroutine-friendly without patching them, through the libc hooks
- Windows applications, including MFC/WTL GUI apps, that want coroutine-style networking on the GUI message pump or iocp
- Projects already on the acl framework that want its HTTP server, master/worker process model and fiber pools
- Memory-tight services with very many mostly idle fibers, using shared-stack mode on Linux

## Skip it when

- When you need raw switch speed for generators or compute-only coroutines: the tboox benchbox switch page lists libfiber(acl) slower than boost and tbox, and minicoro, libaco or tbox are leaner
- When LGPL-3.0 is not acceptable for static linking into a closed product
- When you need work-stealing across cores: the scheduler is single-threaded, one scheduler per thread, with no migration of fibers between threads
- When global symbol interposition of close/read/write/connect/epoll is unwelcome (other libraries, sanitizers, or your own hooks in the same process)
- When you want a header-only or small dependency: it is a built C library with a large API, and the C++ convenience pieces lean on the acl codebase

## How it is fast

Context switches on x86-64 use a hand-written inline-assembly setjmp/longjmp (x86_jmp.h, the Makefile default USE_JMP_DEF) that saves only callee-saved registers, rsp and the resume address; ARM builds use Boost.Context's jump_fcontext, and ucontext is only a fallback. Linux builds compile with -DSHARE_STACK, so fibers created with go_share or the share-stack attribute run on one shared stack and copy only their used portion on switch, which cuts memory at high fiber counts. I/O waits go straight to the per-thread epoll/kqueue/io_uring loop through the hooked syscalls, so a blocked fiber costs one event registration rather than a thread.

## Compared with alternatives

Pick libfiber over libco or libgo when you want a maintained (2026 commits) hook-based network coroutine runtime that also covers Windows iocp/GUI and io_uring; pick libaco, minicoro or tbox when you only need the fastest bare context switch and no I/O runtime.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the C core (links -ldl -lpthread); optional liburing when built with HAS_IO_URING=yes; C++ HTTP server and fiber_pool samples need acl (lib_acl_cpp) |
| **Minimum toolchain** | C compiler with GNU inline asm on x86-64 (gcc or clang); C++11 for go_fiber.hpp lambdas; Visual Studio solutions (vc2012-2015, built with vc2019) on Windows; MinGW-w64 mentioned in issue #41 |
| **Platforms** | Linux, FreeBSD, macOS, Windows; x86-64 custom asm switch, arm/arm64 via Boost.Context fcontext |
| **Thread safety** | Each thread runs its own scheduler and fibers stay on it. Cross-thread sync must use ACL_FIBER_EVENT / acl::fiber_mutex or fiber_tbox; the FAQ warns that pthread mutexes held across coroutine switches can deadlock threads. |
| **Drop-in for the baseline** | partial — same model as libco (stackful coroutines plus hooked blocking syscalls), but a different API (acl_fiber_\* vs co_create/co_resume) and different event-loop entry point |

## Gotchas

- Shared-stack fibers are not available when Boost.Context jumps are used (arm/arm64 builds, and the code #errors if both are set), so the memory-saving mode is x86-64 Linux only in practice.
- The README's own server sample has a Windows-only typo (timeout \*= 1000 on an undeclared name), and on Windows the hooks are absent, so code must call acl_fiber_recv/acl_fiber_send explicitly.
- Open issue #54 (Feb 2026) reports a memory leak on Windows; closed issue #26 reported a leak in fiber_timer::start().
- Benchmark compares whole echo-server samples (libfiber vs libmill, libco and a Go program) with no CPU, OS, compiler or flags, so it measures event-loop plus syscall-hook overhead, not context-switch cost.

## Known shortcomings

- Custom x86-64 asm setjmp switch, Boost fcontext on ARM, shared stack Linux-only, libc hooks. The benchmark is an echo-server QPS with no hardware or flags stated. Open issue 54: Windows memory leak.

## Caveats and trade-offs

First-party chart only; the page gives no CPU, OS, compiler or flags and no numeric table. Benchmark sources for libco and libmill are in the repo benchmark directory, golang sample and client live in acl-dev repos. Measures network echo IOPS, not raw context switch cost. libfiber is extracted from acl-dev/acl lib_fiber; the tboox benchbox switch page lists it as libfiber(acl), where it is slower than boost and tbox for raw switches.

LGPL-3.0. Hooks libc network APIs on Unix so blocking drivers become coroutine-friendly; runs event loops (epoll, io_uring, iocp). C API with C++ wrappers.

## Maintenance

Active (last commit 2026-01-04, 817 stars) and copyable under LGPL-3.0; it tracks acl-dev/acl lib_fiber, which is where most development happens.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README bar chart (res/benchmark.png) of echo-server QPS vs libmill, golang and libco; benchmark sources are in the repo's benchmark/ directory but no CPU, OS, compiler or flags are given, so C.
- **Verifier notes:** Chart values in the record match the image I downloaded. LGPL-3.0, 817 stars, last commit 2026-01-04 confirmed on github.com.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/iqiyi/libfiber>
  - <https://github.com/iqiyi/libfiber/commits>
  - <https://raw.githubusercontent.com/iqiyi/libfiber/HEAD/README.md>
  - <https://raw.githubusercontent.com/iqiyi/libfiber/HEAD/res/benchmark.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/iqiyi/libfiber/HEAD/README.md>
  - <https://github.com/iqiyi/libfiber/tree/master/c/src>
  - <https://github.com/iqiyi/libfiber/tree/master/c/src/fiber>
  - <https://raw.githubusercontent.com/iqiyi/libfiber/HEAD/c/src/fiber/fiber_unix.c>
  - <https://raw.githubusercontent.com/iqiyi/libfiber/HEAD/c/src/fiber/x86_jmp.h>
  - <https://raw.githubusercontent.com/iqiyi/libfiber/HEAD/c/Makefile>
  - <https://github.com/iqiyi/libfiber/tree/master/benchmark>
  - <https://github.com/iqiyi/libfiber/issues>
  - <https://github.com/iqiyi/libfiber/issues?q=is%3Aissue+is%3Aclosed>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/iqiyi/libfiber`) · [data/wave11/enrich/raw/github_com_iqiyi_libfiber.json](../../../data/wave11/enrich/raw/github_com_iqiyi_libfiber.json) (enrichment confidence 0.7)

</details>
