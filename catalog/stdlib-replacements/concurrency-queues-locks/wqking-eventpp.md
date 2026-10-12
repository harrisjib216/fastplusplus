# eventpp::SpinLock (eventpp GeneralThreading policy)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟡 stale

> Header-only spinlock policy for eventpp's EventQueue/EventDispatcher, swapping std::mutex for a std::atomic_flag test-and-set lock at &lt;=core-count thread counts.

| | |
|---|---|
| **Beats** | std::mutex |
| **Claimed result** | 10M events, 100 event types/listeners (doc/benchmark.md): 1 enqueue/1 process thread: SpinLock 1303 ms vs std::mutex 1824 ms (\~1.4x faster, derived from page data); 1/3: 3186 vs 2989 ms (SpinLock slower); 2/2: 3049 vs 3151 ms (slightly faster); 4/4: 1659 vs 1657 ms (tie); 16/16: 1891 vs 708 ms (SpinLock \~2.7x SLOWER, derived from page data). |
| **Workload** | EventQueue enqueue/process microbenchmark: N enqueue threads and N process threads (1 to 16) moving 10M events across 100 event types/listeners, protected by either std::mutex or eventpp::SpinLock as the Threading::Mutex policy. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-8300H @ 2.30GHz, 16GB RAM, Windows 10 (per doc/benchmark.md, described by the author as 'pretty medium to low end') |
| **Compiler and flags** | MinGW GCC 11.3.0 (stated default compiler for this table; MSVC 2022 also used elsewhere in the same doc for other tables; optimization flags not stated) |
| **Adoption** | 1.7k stars |
| **Last commit** | 2024-12-08 |
| **Links** | [repository](https://github.com/wqking/eventpp) · [benchmark](https://github.com/wqking/eventpp/blob/master/doc/benchmark.md) |

## Verdict

On one Intel Core i5-8300H laptop (4 cores/8 threads, Windows 10) compiled with MinGW GCC 11.3.0, moving 10M events across 100 event types/listeners through eventpp's EventQueue: eventpp::SpinLock beat std::mutex only at 1 enqueue/1 process thread (1303ms vs 1824ms, \~1.4x faster) and was roughly tied at 2/2 and 4/4 threads; it lost at 1/3 threads (3186 vs 2989ms) and was \~2.7x slower than std::mutex at 16/16 threads (1891 vs 708ms). The doc itself attributes this to thread count exceeding core count. No optimization flags or build type are stated, so evidence is capped at tier C.

## Use it when

- Thread count is roughly at or below the physical core count (benchmark shows a win at 1/1 and near-ties at 2/2 and 4/4 threads on a 4-core/8-thread laptop)
- You are already using eventpp's EventQueue, EventDispatcher, or CallbackList and want a drop-in policy swap without restructuring code
- Critical sections guarding the event/listener list are short (enqueue/dequeue bookkeeping, not long listener execution)
- Throughput on the enqueue/process path matters more than CPU headroom for other work
- You can control or know the thread count won't exceed available cores

## Skip it when

- Thread count exceeds CPU cores: the 16-enqueue/16-process benchmark shows SpinLock \~2.7x slower than std::mutex from busy-wait CPU burn
- Listeners or event processing hold the lock for any non-trivial time, since spinning wastes cycles instead of descheduling
- You need try_lock, timed_lock, recursive locking, or fairness/ordering guarantees; SpinLock implements only lock()/unlock()
- Power- or CPU-budget-constrained environments (laptops on battery, oversubscribed containers/VMs) where busy-waiting steals cycles from co-scheduled work
- You want portable, well-controlled benchmark evidence: only one first-party Windows/MinGW run exists with no stated optimization flags (evidence tier C)

## How it is fast

It is a raw test-and-set spinlock: one std::atomic_flag, with lock() spinning on test_and_set(memory_order_acquire) and unlock() calling clear(memory_order_release) - no backoff, no OS involvement. This skips the kernel-mutex path (futex/CRITICAL_SECTION) std::mutex takes under contention, which wins when critical sections are short and thread count is at or below the core count. There is no yielding, so once threads outnumber cores it just burns CPU instead of sleeping.

## Compared with alternatives

The sibling entries (atomic_queue, Boost.Lockfree, moodycamel::ReaderWriterQueue, oneTBB concurrent_bounded_queue, xenium) are all standalone lock-free concurrent queues usable in any C++ codebase, with consistent multi-x nanosecond-latency wins over std::mutex. eventpp::SpinLock is not a queue at all — it only makes sense if you're already using eventpp's EventQueue/EventDispatcher/CallbackList and want to shave mutex overhead there at &lt;=core-count thread counts; for a general-purpose concurrent queue outside eventpp, pick one of the lock-free siblings instead, since their evidence is stronger and their wins don't flip to a loss at higher thread counts the way SpinLock's does.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C++11 for the library; author tests MSVC 2019/2022, MinGW GCC 7.2+, Ubuntu GCC 5.4, Intel C++ 2022, macOS GCC (benchmark itself used MinGW GCC 11.3.0) |
| **Platforms** | any platform with a conforming C++11 compiler and std::atomic_flag (portable standard C++, no arch-specific intrinsics); benchmarked on Windows/x86-64 |
| **Thread safety** | eventpp::SpinLock itself implements only BasicLockable (lock/unlock) via std::atomic_flag; not recursive, no try_lock/timed_lock. It substitutes for std::mutex only at eventpp's Threading::Mutex policy point (GeneralThreading&lt;SpinLock&gt;), which is documented as thread-safe for the enclosing EventQueue/EventDispatcher/CallbackList. |
| **Drop-in for the baseline** | partial — explain: implements enough of std::mutex's interface (lock/unlock) to slot into eventpp's Threading::Mutex policy in place of std::mutex with a one-line policy change, but it lacks try_lock/timed_lock so it is not a general-purpose std::mutex replacement outside that policy point. |

## Gotchas

- Plain test-and-set spinning with no backoff/pause/yield: it will peg a CPU core at 100% while waiting, unlike std::mutex which can block via the OS
- No fairness or ordering guarantee — it's a simple TAS lock, not a ticket/queued lock, so waiting threads can be starved under heavy contention
- Only takes effect where you explicitly wire it in via a custom Threading policy (GeneralThreading&lt;SpinLock&gt;); the library's default remains std::mutex
- Missing try_lock/timed_lock means code that needs std::unique_lock's try-lock or timed variants can't use it as-is

## Caveats and trade-offs

First-party benchmark. The doc states the CPU model and compilers but not the optimization flags or build type, so the tier is capped at C. Results are mixed: a win at 1/1 threads, a loss at 1/3, near-ties at 2/2 and 4/4, and a clear loss at 16/16. The benchmark doc itself says SpinLock is only better when threads are about equal to or fewer than cores. Single laptop CPU, benchmarked December 2023.

SpinLock busy-waits (burns CPU) instead of blocking via the kernel; degrades badly under thread oversubscription; only a real win when thread count is at or below the physical core count; not a safe general drop-in replacement for std::mutex.

## Maintenance

Stale but not abandoned: last commit 2024-12-08, the README calls the project 'actively maintained' despite release gaps; Apache-2.0 licensed (GitHub's license detector shows NOASSERTION but the LICENSE file text is Apache-2.0) and header-only, so it's low-risk to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** doc/benchmark.md has a SpinLock vs std::mutex table (MinGW GCC 11.3.0, i5-8300H) that matches the record. The benchmark code is public (tests/benchmark/b3_b5_eventqueue.cpp), but no optimization flags or build type are stated. The CMake files set only warnings, and the makefile offers both release and debug MinGW targets, so C.
- **Verifier notes:** The table is verified, including the 1/3 row the record left out, where SpinLock loses. This is a conditional win only. GitHub reports the license as NOASSERTION, but the license file is Apache License 2.0, so Apache-2.0 and copyable are correct. Last commit is 2024-12-08 (stale); 1,685 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/wqking/eventpp/blob/master/doc/benchmark.md>
  - <https://github.com/wqking/eventpp>
  - <https://github.com/wqking/eventpp/blob/master/license>
  - <https://github.com/wqking/eventpp/blob/master/tests/CMakeLists.txt>
  - <https://github.com/wqking/eventpp/blob/master/tests/benchmark/CMakeLists.txt>
  - <https://github.com/wqking/eventpp/blob/master/tests/build/makefile>
- **Sources the enricher read:**
  - <https://github.com/wqking/eventpp>
  - <https://github.com/wqking/eventpp/blob/master/doc/benchmark.md>
  - <https://github.com/wqking/eventpp/blob/master/doc/policies.md>
  - <https://github.com/wqking/eventpp/blob/master/doc/eventqueue.md>
  - <https://github.com/wqking/eventpp/blob/master/include/eventpp/eventpolicies.h>
  - <https://github.com/wqking/eventpp/blob/master/license>
  - <https://github.com/wqking/eventpp/issues?q=spinlock>
  - <https://github.com/wqking/eventpp/issues?q=performance>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/wqking/eventpp`) · [data/wave1/enrich/raw/github_com_wqking_eventpp.json](../../../data/wave1/enrich/raw/github_com_wqking_eventpp.json) (enrichment confidence 0.55)

</details>
