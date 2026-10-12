# Boost.Lockfree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Boost's lock-free MPMC/SPSC queue and stack family; beats std::mutex on latency, not contended MPMC throughput.

| | |
|---|---|
| **Beats** | std::mutex |
| **Claimed result** | atomic_queue shootout, Ryzen 5950X (SMT) ping-pong latency: boost::lockfree::spsc_queue mean 51ns vs std::mutex 320ns (\~6.3x lower); boost::lockfree::queue 92ns (\~3.5x lower). 1P/1C throughput: spsc_queue \~114M msg/s and queue \~7.8M msg/s vs std::mutex \~4.1M msg/s. A separate evpp benchmark (Qihoo360, 2017, GCC 4.8.2, Boost 1.58, Xeon E5-2630 v2) reports boost::lockfree::queue averaging \~75%-150% higher throughput than a std::mutex-guarded std::vector with multiple producers, and only a small advantage with 1 producer/1 consumer. |
| **Workload** | Same third-party SPSC/MPMC round-trip ping-pong benchmark as the atomic_queue shootout, on AMD Ryzen 5950X; boost::lockfree::spsc_queue used in the SPSC role, boost::lockfree::queue in the MPMC role. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 5950X, Linux, mitigations=off (primary); Intel Xeon E5-2630 v2 / CentOS 6.2 (corroborating evpp benchmark) |
| **Compiler and flags** | gcc-14.2.0, -march=native -O3 -mtune=native -DNDEBUG (reference Makefile BUILD=release, commit 632bae1) |
| **Adoption** | 160 stars on the standalone mirror repo; ships as part of Boost, one of the most widely deployed C++ library collections |
| **Last commit** | 2026-08-14 |
| **Links** | [repository](https://github.com/boostorg/lockfree) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html) |

## Verdict

An independent third-party benchmark (the atomic_queue shootout; gcc-14.2.0 -O3 -march=native, AMD Ryzen 5950X, Linux) measured ping-pong round-trip latency of spsc_queue at 51ns and queue at 92ns against std::mutex at 320ns (about 6.3x and 3.5x lower). A separate 2017 evpp benchmark (gcc-4.8.2, Xeon E5-2630 v2) found boost::lockfree::queue giving 75-150% higher throughput than a mutex-guarded std::vector, but only with multiple producers. Neither benchmark is Boost's own, and the same shootout's MPMC throughput data shows boost::lockfree::queue losing to std::mutex once 2 or more producer/consumer pairs are contending.

## Use it when

- Exactly one producer thread and one consumer thread need a ring buffer and latency matters (spsc_queue measured at 51ns vs std::mutex 320ns in the atomic_queue shootout)
- MPMC queue with a bounded/fixed-size capacity, where avoiding OS-level allocation and priority inversion matters more than peak contended throughput
- Already depend on Boost and want an actively maintained (last commit 2026-08-14), widely-used lock-free structure without adding a new third-party dependency
- Element type is a small, trivially-copyable POD (ints, small structs, raw pointers used carefully) rather than move-only or exception-throwing

## Skip it when

- Heavily contended MPMC throughput: in the atomic_queue shootout, boost::lockfree::queue loses to a std::mutex-guarded ring buffer at every count of 2+ producer/consumer pairs (5.9M vs 13.0M msg/s at 2 pairs; 1.5M vs 2.3M at 16)
- T is a pointer type: open issue #120 reports a data race where concurrent pop() can hand the same pointer to two threads
- Code depends on pop() returning false only when the queue is truly empty: open issue #119 shows pop() can spuriously return false under concurrent push/pop on a non-empty queue
- Need move-only element types or exception-safety guarantees in push/pop: unsupported (open request #125); docs explicitly discourage exceptions in lock-free code
- Need std::queue/std::stack API compatibility such as iteration or arbitrary resizing: the API is deliberately narrower

## How it is fast

queue implements Michael & Scott's lock-free MPMC algorithm with a tagged-pointer freelist that recycles nodes instead of returning memory to the OS on every pop. spsc_queue is a wait-free single-producer/single-consumer ring buffer (the same technique used in the Linux kernel) with no compare-and-swap on its hot path at all. Skipping mutex acquisition removes the futex/syscall path and priority-inversion risk that dominate std::mutex latency under contention. bounded_ticket_queue additionally implements a Vyukov turnstile algorithm that becomes wait-free when producer or consumer count is fixed to one side.

## Compared with alternatives

Pick Boost.Lockfree when you already depend on Boost and want an actively-maintained, well-tested queue without adding a new dependency. Pick atomic_queue or moodycamel::ReaderWriterQueue instead when SPSC latency is the priority (42-43ns vs Boost's 51ns) or for contended MPMC throughput, where boost::lockfree::queue loses to a plain std::mutex ring buffer.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Boost.Align, Boost.Assert, Boost.Atomic, Boost.Config, Boost.Core, Boost.Parameter, Boost.Predef, Boost.Utility (ships as part of Boost, not standalone) |
| **Minimum toolchain** | C++14 (CMake target_compile_features cxx_std_14); uses C++20 concepts opportunistically when available |
| **Platforms** | any platform with CAS/double-width-CAS atomic support; internal tagged-pointer representation switches between a DCAS scheme and a pointer-compression scheme depending on platform, not documented as restricted to a specific ISA |
| **Thread safety** | push/pop are lock-free (queue, stack) or wait-free (spsc_queue, spsc_value) across concurrent threads; construction and destruction of the container itself must be externally synchronized, per the doc comment in queue.hpp |
| **Drop-in for the baseline** | partial - explain: replaces a std::mutex-guarded container's push/pop calls, but push/pop return bool status codes, there are no iterators, and size/capacity is set via template policies rather than dynamic growth |

## Gotchas

- boost::lockfree::queue&lt;T\*&gt; has an open data-race report (issue #120): concurrent pop() can return the same pointer to two threads
- pop() can spuriously return false on a non-empty queue under concurrent push/pop (issue #119), so a false return does not strictly mean 'empty'
- T must be trivially copy-assignable and trivially destructible for queue; move-only types fail to compile rather than degrading gracefully
- capacity&lt;&gt; and allocator&lt;&gt; policy options are mutually exclusive (static_assert) - pick compile-time-fixed or runtime-allocated sizing, not both

## Caveats and trade-offs

The '100%-500%' figure in the evpp doc is moodycamel::ConcurrentQueue vs std::mutex, not Boost.Lockfree. Boost's figure there is 75%-150% (multi-producer only), and the doc dates from 2017, not 2015. In the atomic_queue MPMC throughput test on the 5950X, boost::lockfree::queue is SLOWER than the std::mutex ring buffer at every count of 2+ producer/consumer pairs (5.9M vs 13.0M msg/s at 2; 1.5M vs 2.3M at 16). The measured win is in latency and SPSC/1P1C, not in contended MPMC throughput. Neither benchmark is Boost.Lockfree's own. [retier] Compiler and CPU are stated on benchmarks.html; the flags are not on that page and come from the reference Makefile's default release build.

boost::lockfree::queue requires either a bounded capacity or a lock-free allocator for unbounded use; elements generally need to be trivially copyable / POD-like for best behaviour; API and iterator semantics differ substantially from std::queue.

## Maintenance

Actively maintained as part of mainline Boost (last commit 2026-08-14); BSL-1.0 licensed and header-only, so it is cheap to adopt if you already take Boost as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now A.
- **Tier reason:** Independent atomic_queue shootout (code in max0x7ba/atomic_queue src/benchmarks.cc; gcc-14.2.0, Boost 1.83.0, Ryzen 5950X) shows spsc_queue at 51ns and queue at 92ns vs std::mutex at 320ns. Qihoo360/evpp docs/benchmark_lockfree_vs_mutex.md is a second independent benchmark. Neither is Boost's own benchmark, so tier B.
- **Retiered** B to A: atomic_queue shootout: code src/benchmarks.cc in max0x7ba/atomic_queue; gcc-14.2.0 and AMD Ryzen 9 5950X stated on benchmarks.html and in results/632bae1.ryzen_5950x.smt1.20260914T121940.gcc-14.32.33.txt; flags from the reference Makefile default BUILD=release at commit 632bae1: -march=native -O3 -mtune=native -DNDEBUG (+ -fno-stack-protector, -falign-functions=64). Independent run against std::mutex: spsc_queue 51-52ns, queue 92ns vs std::mutex 320-321ns per round-trip.
- **Verifier notes:** The shootout numbers (51/92 vs 320 ns) check out. The evpp corroboration was misattributed: 100-500% is moodycamel's margin, and Boost's is 75-150%. The atomic_queue throughput data also shows boost::lockfree::queue losing to std::mutex under MPMC contention. Metadata checked: BSL-1.0, 160 stars, default branch develop, last commit author date 2026-08-14 (committer date 2026-08-15).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://max0x7ba.github.io/atomic_queue/html/benchmarks.html>
  - <https://max0x7ba.github.io/atomic_queue/html/results.js>
  - <https://github.com/max0x7ba/atomic_queue/blob/master/src/benchmarks.cc>
  - <https://github.com/boostorg/lockfree>
  - <https://github.com/Qihoo360/evpp/blob/master/docs/benchmark_lockfree_vs_mutex.md>
- **Sources the enricher read:**
  - <https://github.com/boostorg/lockfree>
  - <https://github.com/boostorg/lockfree/blob/develop/doc/lockfree.qbk>
  - <https://github.com/boostorg/lockfree/blob/develop/include/boost/lockfree/queue.hpp>
  - <https://github.com/boostorg/lockfree/blob/develop/include/boost/lockfree/spsc_queue.hpp>
  - <https://github.com/boostorg/lockfree/blob/develop/CMakeLists.txt>
  - <https://github.com/boostorg/lockfree/issues/120>
  - <https://github.com/boostorg/lockfree/issues/119>
  - <https://github.com/boostorg/lockfree/issues>
  - <https://max0x7ba.github.io/atomic_queue/html/benchmarks.html>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/boostorg/lockfree`) · [data/wave1/enrich/raw/github_com_boostorg_lockfree.json](../../../data/wave1/enrich/raw/github_com_boostorg_lockfree.json) (enrichment confidence 0.72)

</details>
