# Boost.Fiber

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Async tasks and thread pools](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Cooperative user-space fibers with a std::thread-like API, spawning and context-switching orders of magnitude cheaper than std::thread/std::async.

| | |
|---|---|
| **Beats** | std::thread, std::async |
| **Claimed result** | fiber (16C/32T, work-stealing, tcmalloc): 0.05-0.09 us/fiber (average over 1,000,000) vs std::thread 52-73 us/thread and std::async 106-122 us/thread (average over 10,000, because 1,000,000 threads exhausted resources); \~580-1460x lower time-per-unit vs std::thread and \~1180-2440x vs std::async (derived from page data). Single-thread round-robin fiber (1C/1T): 1.69-1.79 us/fiber, still \~30-40x lower than std::thread (derived from page data). |
| **Workload** | skynet microbenchmark (ported from atemerev/skynet): spawn 10 threads-of-execution recursively until 1,000,000 total actors/fibers are created (only 10,000 for std::thread/std::async/pthread due to resource exhaustion); each returns its ordinal number, summed back up to the root; average time-per-unit measured with std::chrono::high_resolution_clock |
| **Metric** | latency |
| **Hardware** | dual Intel Xeon E5-2620v4 2.2GHz, 16 cores/32 threads, 64GB RAM, Linux x86_64 |
| **Compiler and flags** | gcc-6.3.1, variant=release, optimization=speed |
| **Adoption** | 511 stars on the standalone mirror; ships as part of the Boost C++ Libraries collection used industry-wide |
| **Last commit** | 2026-06-15 |
| **Links** | [repository](https://github.com/boostorg/fiber) · [benchmark](https://github.com/boostorg/fiber/blob/master/doc/performance.qbk) |

## Verdict

On gcc-6.3.1 (variant=release, optimization=speed), dual Xeon E5-2620v4 (16C/32T), Linux x86_64, Boost's ported skynet microbenchmark (1,000,000 spawned actors; 10,000 for std::thread/std::async, which exhausted OS resources beyond that) measured std::thread at 52-73 us/unit and std::async at 106-122 us/unit versus Boost.Fiber at 0.05-0.09 us/unit with a work-stealing scheduler and tcmalloc (1.69-1.79 us/unit single-threaded round-robin).

## Use it when

- Spawning very large numbers of short-lived concurrent tasks (100k-1M+) where std::thread/std::async hit OS resource exhaustion
- Latency-sensitive, switch-heavy workloads where sub-microsecond task handoffs matter more than raw parallel throughput
- Existing Boost.Asio async I/O code that wants synchronous-looking control flow (fiber + yield) instead of callback chains
- Multi-core scaling via boost::fibers::algo::work_stealing across worker threads on many-core hardware (benchmarked on 16C/32T)
- Projects already on Boost (BSL-1.0, C++11+) that can add a compiled Boost library dependency

## Skip it when

- Code with blocking syscalls (file I/O, blocking sockets) not routed through the fiber-aware scheduler/Asio integration — one blocking call stalls every fiber on that thread
- CPU-bound fibers that never yield: there is no preemption, so they starve sibling fibers on the same thread
- Teams wanting a mechanical std::thread/std::async replacement — fiber is a different type with different join/sync semantics; call sites must be rewritten
- Toolchains that can't take a compiled (non-header-only) Boost dependency, or predate C++11
- Treating the &gt;500x headline ratio as current: it's from gcc-6.3.1 (\~2017) hardware/compiler, with tcmalloc required and no republished numbers on modern toolchains

## How it is fast

Fiber creation and context switching save/restore registers and swap the stack pointer entirely in user space via Boost.Context primitives, skipping the kernel thread-creation syscall and stack guard-page setup that std::thread/std::async pay for. The fastest measurements add a work-stealing scheduler with per-thread local run queues (stealing idle fibers from other threads) plus tcmalloc in place of glibc's allocator to cut malloc contention under the skynet microbenchmark's million spawns.

## Compared with alternatives

The sibling entries (dispenso, TooManyCooks, utl::parallel, Taskflow, libfork, meet1214/thread-pool, BS::thread_pool) are all task/thread-pool schedulers for CPU-bound work units. Pick Boost.Fiber instead when you need actual blocking-style semantics — mutex, condition_variable, future.get() — that suspend only the calling task, e.g. porting synchronous networking or actor-style code to run as massed lightweight tasks, not a parallel-for or task graph.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib |
| **Dependencies** | Boost.Context (stack switching), Boost.Config, Boost.Assert, Boost.IntrusivePtr, Boost.Predef; optional Boost.Asio for async I/O integration |
| **Minimum toolchain** | C++11 minimum (README: "Boost.fiber requires C++11!"); benchmark used gcc-6.3.1 |
| **Platforms** | x86-64 Linux is the only platform verified this session (benchmark hardware); broader OS/arch support rides on Boost.Context but was not independently confirmed |
| **Thread safety** | Fiber sync primitives (mutex, condition_variable, promise/future) are designed to be thread-safe, i.e. usable to synchronize fibers running on different OS threads, not just within one thread (doc/rationale.qbk); a build option exists to disable this cross-thread support for extra performance |
| **Drop-in for the baseline** | partial — API shape echoes boost::thread/std::thread (callable ctor, join()) but fiber is a distinct type needing an explicit scheduler; std::thread call sites must be rewritten, not just relinked |

## Gotchas

- Cooperative model: fibers must yield/block through the library's own API (or Asio's fiber-aware yield in examples/asio/round_robin.hpp); a raw blocking syscall stalls the whole underlying thread
- Stack allocator choice (fixedsize_stack vs segmented_stack) affects both speed and memory footprint; the headline numbers used fixedsize_stack
- BOOST_FIBERS_NO_ATOMICS disables inter-thread fiber synchronization entirely and has a confusing open compile-error report (issue #285, open since 2021)
- The fiber-side benchmark numbers are tcmalloc-only; the doc doesn't state whether the std::thread/std::async rows used the same allocator, so the comparison isn't fully allocator-matched

## Caveats and trade-offs

Numbers come from Boost's own project documentation (first party), though the benchmark code itself (performance/thread/skynet_std.cpp and the fiber counterpart in the same repo) is public and the compiler/flags/hardware are all stated, meeting the tier-A bar despite the source being first-party. The raw ratio (&gt;50x) looks extreme, but it is explained by mechanism (fiber creation/context switch avoids syscalls and stack-guard-page setup that std::thread/std::async incur) rather than a flawed methodology; std::thread could only be tested at 10,000 units instead of 1,000,000 due to OS resource exhaustion, so the two are not run at identical scale. Measurements were taken with gcc-6.3.1, an old compiler (circa 2017); the fiber library and hardware landscape have moved on since, and the doc gives no indication the numbers were re-run on newer toolchains.

Cooperative user-space scheduling: a blocking syscall or CPU-bound fiber can stall all fibers on its worker thread unless paired with async I/O (e.g. Boost.Asio integration); best numbers require a non-default allocator (tcmalloc) and a work-stealing scheduler configuration; different programming model (fiber-per-task) than raw std::thread/std::async call sites.

## Maintenance

Actively maintained as part of Boost (last commit 2026-06-15), BSL-1.0 licensed and freely copyable; the performance numbers themselves date to gcc-6.3.1 (\~2017) and the docs give no indication they were re-run on a modern toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** doc/performance.qbk gives time per unit for pthread, std::thread (52-73 us) and std::async (106-122 us) against Boost.Fiber (0.05-0.09 us work-stealing with tcmalloc; 1.69-1.79 us 1C/1T round robin). It states gcc-6.3.1, build options variant=release optimization=speed, and dual Xeon E5-2620v4. The benchmark code is public in performance/thread/skynet_{std,async,pthread}.cpp and performance/fiber/skynet_\*.cpp.
- **Verifier notes:** Numbers match the page exactly. The old '\~600-1400x' ratio covered only std::thread, so the corrected claim adds separate ranges for std::thread and std::async. The page says fibers were linked with tcmalloc (-ltcmalloc) but not whether the thread runs were, and the two sides ran at different unit counts. GitHub license spdx is null because there is no LICENSE file, but the headers state Boost Software License 1.0, so BSL-1.0 is correct. Stars (511) and last commit (2026-06-15) were checked and are correct.
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/boostorg/fiber>
  - <https://github.com/boostorg/fiber/blob/master/doc/performance.qbk>
  - <https://github.com/boostorg/fiber/tree/master/performance>
  - <https://github.com/boostorg/fiber/blob/master/include/boost/fiber/fiber.hpp>
- **Sources the enricher read:**
  - <https://github.com/boostorg/fiber>
  - <https://github.com/boostorg/fiber/blob/master/README.md>
  - <https://github.com/boostorg/fiber/blob/master/doc/performance.qbk>
  - <https://github.com/boostorg/fiber/blob/master/doc/rationale.qbk>
  - <https://github.com/boostorg/fiber/blob/master/include/boost/fiber/fiber.hpp>
  - https://github.com/boostorg/fiber (repo tree listing: CMakeLists.txt, doc/asio.qbk, examples/asio/\*)
  - <https://github.com/boostorg/fiber/issues/151>
  - <https://github.com/boostorg/fiber/issues/285>
  - <https://github.com/boostorg/fiber/issues/111>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/boostorg/fiber`) · [data/wave1/enrich/raw/github_com_boostorg_fiber.json](../../../data/wave1/enrich/raw/github_com_boostorg_fiber.json) (enrichment confidence 0.68)

</details>
