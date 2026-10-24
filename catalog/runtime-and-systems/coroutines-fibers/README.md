# Coroutines and fibers

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md)</sub>

**What these beat:** Boost.Context, Boost.Coroutine, libco  
**23 entries:** 1 tier A · 1 tier B · 18 tier C · 3 tier D · 22 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**cppcoro**](lewissbaker-cppcoro.md) | C++ coroutine library whose work-stealing static_thread_pool runs fork-join tasks 20-86x faster than concurrencpp or HPX. | **A** | C++ | MIT | 🔴 abandoned |
| 2 | [**libseff**](effect-handlers-libseff.md) | C library of shallow effect handlers on stackful coroutines; OOPSLA 2024 paper reports about 2x faster generators than Tencent libco. | **B** | C | MulanPSL-2.0 | 🟡 stale |
| 3 | [**tbox (coroutine switch)**](tboox-tbox.md) | glib-like C library whose stackful coroutine scheduler switches faster than Boost.Coroutine and libco in its author's benchmark. | **C** | C | Apache-2.0 | 🟢 active |
| 4 | [**async_simple (Lazy)**](alibaba-async-simple.md) | Alibaba's C++20 Lazy coroutine task type; about 3x faster than folly::coro::Task on call-chain and fan-out microbenchmarks, near-parity with cppcoro. | **C** | C++ | Apache-2.0 | 🟢 active |
| 5 | [**libcoro**](jbaldwin-libcoro.md) | C++20 coroutine library with epoll/kqueue TCP, UDP, TLS and DNS; edges cppcoro on single-threaded socket ping-pong. | **C** | C++ | Apache-2.0 | 🟢 active |
| 6 | [**libcopp**](owent-libcopp.md) | Cross-platform stackful coroutine library (with C++20 coroutine helpers) that switches up to about 1.65x faster than Tencent libco at 30,000 coroutines. | **C** | C++ | MIT and BSL-1.0 | 🟢 active |
| 7 | [**libfiber (iqiyi)**](iqiyi-libfiber.md) | C stackful coroutine runtime with libc network hooks; first-party echo-server chart shows about 1.6-1.7x libco's QPS. | **C** | C | LGPL-3.0 | 🟢 active |
| 8 | [**Boost.Cobalt**](boostorg-cobalt.md) | Boost library of C++20 coroutine primitives on Boost.Asio; beats asio stackful spawn and, on channels, asio::awaitable. | **C** | C++ | BSL-1.0 | 🟢 active |
| 9 | [**TurboRoutine**](giangian2-turboroutine.md) | Small x86-64 Linux C library for stackful coroutines with an assembly context switch; README claims about 70x faster round trips than swapcontext. | **C** | C | GPL-3.0 | 🟢 active |
| 10 | [**minicoro**](edubart-minicoro.md) | Single-header C stackful asymmetric coroutines with a hand-written assembly switch, about 40x cheaper than ucontext on x86-64 Linux. | **C** | C | Unlicense OR MIT-0 (public… | 🟡 stale |
| 11 | [**Coros**](mtmucha-coros.md) | Header-only C++23 coroutine fork-join task library with a work-stealing pool; roughly ties oneTBB, beats OpenMP tasks. | **C** | C++ | BSL-1.0 | 🟡 stale |
| 12 | [**libcr**](sm2coin-libcr.md) | Stackless, macro-based C++17 coroutines and protothreads with 1:N and M:N schedulers; 3 ns switches versus 2.5 us kernel thread handoffs. | **C** | C++ | AGPL-3.0 | 🟡 stale |
| 13 | [**libaco**](hnes-libaco.md) | Small C asymmetric-coroutine library for x86/x86-64 whose hand-written switch routine runs about 1.7x faster than Tencent libco's coctx_swap. | **C** | C | Apache-2.0 | 🔴 abandoned |
| 14 | [**libgo**](yyzybb537-libgo.md) | Go-style stackful coroutine runtime for C++11 with multi-thread scheduler and syscall hooks; switches faster than libco and ucontext. | **C** | C++ | MIT | 🔴 abandoned |
| 15 | [**libmill**](sustrik-libmill.md) | Go-style coroutines and channels for C; in a third-party switch shootout it beats libco and sometimes Boost.Context. | **C** | C | MIT | 🔴 abandoned |
| 16 | [**Marl**](google-marl.md) | C++11 hybrid thread/fiber task scheduler from Google; tasks that block on marl primitives yield their worker instead of stalling it. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 17 | [**libdill**](sustrik-libdill.md) | C structured-concurrency library with stackful coroutines; project numbers show roughly 20x cheaper switches than Go goroutines. | **C** | C | MIT | 🔴 abandoned |
| 18 | [**libcsp**](shiyanhui-libcsp.md) | Go-style M:N process scheduler for C (GCC plugin, x86-64 Linux); about 10x faster than Go 1.14 at spawning short-lived tasks. | **C** | C | MIT | 🔴 abandoned |
| 19 | [**CO2**](jamboree-co2.md) | Header-only C++14 macro emulation of N4286 stackless coroutines; resume costs about 6 ns versus 82 ns for Boost.Coroutine2. | **C** | C++ | BSL-1.0 | 🔴 abandoned |
| 20 | [**bluebox**](tidwall-bluebox.md) | Toy Redis-protocol server (SET/GET/DEL/PING) showcasing Neco coroutines; first-party memtier run shows 2.4x redis-server throughput. | **C** | C | no license (study only) | 🟡 stale |
| 21 | [**Neco**](tidwall-neco.md) | Single-file C coroutine runtime with Go-like channels, deterministic scheduler and epoll/kqueue I/O; about 11 ns switches, no baseline measured. | **D** | C | MIT | 🟢 active |
| 22 | [**llco**](tidwall-llco.md) | Single-file C stackful coroutine switch (minicoro-derived assembly) with bring-your-own-stack; no scheduler, no benchmark against any baseline. | **D** | C | Unlicense OR MIT-0 (README… | 🟡 stale |
| 23 | [**coros-fibers**](markpapadakis-coros-fibers.md) | Small x86-64 Linux stackful coroutine switch (libcoro-style assembly) plus a priority fiber scheduler; no baseline compared. | **D** | C++ | MIT | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
