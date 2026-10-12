# Boost.Cobalt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Boost library of C++20 coroutine primitives on Boost.Asio; beats asio stackful spawn and, on channels, asio::awaitable.

| | |
|---|---|
| **Beats** | Boost.Asio stackful coroutines (spawn on Boost.Context) and asio::awaitable |
| **Claimed result** | posting 50M times: cobalt 2472 ms gcc12 / 2098 ms clang16 vs stackful 3655 / 3725 ms (about 1.5x-1.8x, derived from page data), awaitable 2432 / 2253 ms; parallel zero-size channel 3M: cobalt 1563 / 1468 ms vs awaitable 2800 / 2805 ms (no stackful row); immediate channel 10M: cobalt 1810 / 1864 ms vs awaitable 3109 / 4110 and stackful 3922 / 4705 ms; cobalt::channel 3M: 500 / 350 ms vs awaitable 790 / 770 and stackful 867 / 907 ms |
| **Workload** | Cobalt task vs asio::awaitable vs asio stackful coroutine: 50M asio::post co_awaits, 10M immediate channel send/receive, 3M parallel channel send/receive, channel comparison |
| **Metric** | throughput |
| **Hardware** | 11th Gen Intel Core i7-1185G7 @ 3.00GHz |
| **Compiler and flags** | gcc 12 and clang 16; flags not stated |
| **Adoption** | 349 stars; part of Boost |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/boostorg/cobalt) · [benchmark](https://github.com/boostorg/cobalt/blob/develop/doc/benchmarks.adoc) |

## Verdict

Author's doc/benchmarks.adoc on an i7-1185G7 with gcc 12 and clang 16 (flags not stated; bench/CMakeLists.txt turns on LTO when Boost.Context is found) runs each loop once in bench/\*.cpp: cobalt is about 1.5-1.8x faster than asio stackful spawn on 50M posts but level with asio::awaitable, and 1.6-2.2x faster than asio::awaitable (derived from page data) on immediate and channel exchanges. These are single timings with no repeats.

## Use it when

- Single-threaded io_context servers or clients written with Boost.Asio that want linear async code without stackful-coroutine stack memory
- Pipelines of producer/consumer coroutines on one thread where cobalt::channel's direct hand-off beats asio::experimental::channel (500 vs 790 ms for 3M zero-size exchanges on gcc)
- Code moving off asio::spawn/yield_context (Boost.Context) that suspends on many fast or immediate completions (1810 vs 3922 ms for 10M immediate channel ops)
- Generators and fan-out with race/gather when you already depend on Boost 1.82+ and C++20

## Skip it when

- You need to suspend from nested ordinary function calls: stackless coroutines can only suspend in the coroutine body, so stackful fibers (Boost.Context, Boost.Fiber, minicoro) still fit
- Multi-threaded executors or strands: the library assumes one executor per thread through a thread_local default; on a strand you must pass the executor by hand or get asio::bad_allocator or the wrong executor
- Plain asio::post throughput against asio::awaitable: 2472 vs 2432 ms on gcc 12, so no gain
- MSVC targets: the docs say all MSVC versions have a broken coroutine implementation, worked around by posting frame destruction, with overhead and non-deterministic freeing; issue #172 (access violation on MSVC) is open
- Projects that cannot take Boost: it needs Asio, System, Intrusive, Circular Buffer and Smart Ptr, and a compiled boost_cobalt library

## How it is fast

Stackless C++20 coroutines avoid the separate stack and Boost.Context switch that asio's stackful spawn uses. cobalt::channel hands values over by direct symmetric transfer between the coroutines instead of posting through the executor, which is where the 1.6-2.2x channel gains over asio::awaitable come from. use_op allocates async-operation state from a small-buffer resource (4096 bytes by default, BOOST_COBALT_SBO_BUFFER_SIZE) and race/gather/join use a monotonic resource; coroutine frames come from a thread_local pmr pool. It also skips suspension when an op completes immediately (op::ready).

## Compared with alternatives

Pick Cobalt over libco-style switchers (libaco, libcopp, libgo) or minicoro when the code is already on Boost.Asio and you want standard C++20 coroutines with no assembly context switch or per-coroutine stack; pick those stackful libraries when you must suspend from deep call stacks or need C compatibility.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Boost 1.82+ (Asio, System, Intrusive, Circular Buffer, Smart Ptr; Boost.Container for Clang &lt; 16); OpenSSL optional for boost_cobalt_io_ssl; Threads |
| **Minimum toolchain** | C++20; Clang 14, GCC 10, MSVC 19.30 (avoid GCC 12.1/12.2) |
| **Platforms** | any platform Boost.Asio supports (Linux, Windows, macOS) |
| **Thread safety** | Single-threaded per executor by design; one kernel thread per io_context; cobalt::thread runs a separate event loop per thread |
| **Drop-in for the baseline** | partial — awaits any asio async operation via cobalt::use_op and can spawn tasks onto asio executors, but coroutines must be rewritten from yield_context or asio::awaitable to cobalt::promise/task |

## Gotchas

- promise is eager and nodiscard; dropping a promise without co_await cancels it with a warning, and detaching needs a unary + (+my_task())
- The docs warn GCC 12.1 and 12.2 miscompile coroutines with stack variables, yet the gcc numbers on the benchmark page were taken with gcc 12
- Open bug reports: heap-use-after-free when cancelling a spawned awaitable (#194), racing a range of generators breaks them (#281), generator locals not cleaned up (#221)
- The channel benchmark compares different channel designs (cobalt::channel&lt;void&gt; with gather vs asio::experimental::channel with parallel_group), not just the coroutine machinery

## Known shortcomings

- Single runs, flags not stated. The channel bench compares different channel designs (cobalt::channel against asio::experimental::channel with parallel_group). The docs warn of a GCC 12.1/12.2 coroutine miscompile, yet GCC 12 produced the page numbers. Open issues include a heap-use-after-free (194).

## Caveats and trade-offs

First-party numbers on one laptop CPU, compiler flags unstated, gcc 12 / clang 16 are old. Baseline is asio's spawn/yield_context (Boost.Context based), not Boost.Context or Boost.Fiber directly; it only roughly matches the category baseline. Against asio::awaitable the gain is small or nil for the post benchmark (2472 vs 2432 ms on gcc 12).

C++20 stackless coroutines tied to Boost.Asio (Boost 1.82+); not a general-purpose fiber library and cannot suspend from nested calls like stackful fibers.

## Maintenance

Actively maintained Boost library (last commit 2026-09-24), BSL-1.0, but several crash and memory-safety issues are still open and MSVC support relies on workarounds.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party doc/benchmarks.adoc gives timings vs asio::awaitable and asio stackful (Boost.Context) coroutines on an i7-1185G7 with gcc 12 / clang 16, but no compiler flags, so not A.
- **Verifier notes:** All numbers in the record match the page; added the awaitable rows and the parallel-channel table. License BSL-1.0 (Boost) not re-confirmed from a LICENSE file (raw LICENSE_1_0.txt 404 on develop), left as is. Last commit 2026-09-24 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/boostorg/cobalt/blob/develop/doc/benchmarks.adoc>
  - <https://github.com/boostorg/cobalt>
  - <https://github.com/boostorg/cobalt/commits/develop>
- **Sources the enricher read:**
  - <https://github.com/boostorg/cobalt/blob/develop/doc/benchmarks.adoc>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/readme.md>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/doc/benchmarks.adoc>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/doc/compiler.adoc>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/doc/design/thread_local.adoc>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/doc/reference/config.adoc>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/doc/index.adoc>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/CMakeLists.txt>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/bench/CMakeLists.txt>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/bench/post.cpp>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/bench/immediate.cpp>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/bench/channel.cpp>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/bench/parallel.cpp>
  - <https://raw.githubusercontent.com/boostorg/cobalt/develop/include/boost/cobalt.hpp>
  - <https://github.com/boostorg/cobalt/issues?q=is%3Aissue+bug>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/boostorg/cobalt`) · [data/wave11/enrich/raw/github_com_boostorg_cobalt.json](../../../data/wave11/enrich/raw/github_com_boostorg_cobalt.json) (enrichment confidence 0.75)

</details>
