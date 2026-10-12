# moodycamel::ReaderWriterQueue

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Header-only lock-free SPSC queue for C++11; beats a mutex-guarded queue by \~7x in ping-pong latency.

| | |
|---|---|
| **Beats** | std::mutex |
| **Claimed result** | moodycamel::ReaderWriterQueue mean round-trip latency 43ns vs std::mutex mean 320ns -&gt; \~7.4x lower latency. (Evidence is from an independent third-party shootout, not the project's own benchmark -- the project's own blog post benchmarks only compare it against another SPSC queue and folly::ProducerConsumerQueue, not std::mutex.) |
| **Workload** | Same third-party SPSC round-trip ping-pong benchmark as the atomic_queue shootout: 2 threads exchange a 4-byte counter via two queue instances, 1,000,000 round trips, on AMD Ryzen 5950X. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 5950X, Linux, mitigations=off |
| **Compiler and flags** | gcc-14.2.0, -march=native -O3 -mtune=native -DNDEBUG (reference Makefile BUILD=release, commit 632bae1) |
| **Adoption** | 4.6k stars |
| **Last commit** | 2026-09-07 |
| **Links** | [repository](https://github.com/cameron314/readerwriterqueue) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html) |

## Verdict

In the independent max0x7ba/atomic_queue SPSC ping-pong shootout (gcc-14.2.0, -O3 -march=native -mtune=native, AMD Ryzen 5950X, readerwriterqueue commit 2ae710d), moodycamel::ReaderWriterQueue measured a 43ns mean round-trip latency versus 320ns for a mutex-guarded ring buffer used as the std::mutex baseline (\~7.4x lower). The project's own benchmarks/bench.cpp never compares against std::mutex at all — only against the 1024cores SPSC queue and folly::ProducerConsumerQueue.

## Use it when

- Exactly one fixed producer thread and one fixed consumer thread that never swap roles
- Passing small, cheaply-movable/copyable values (counters, pointers, small structs) between the two threads
- Need sub-100ns round-trip latency and want to avoid std::mutex-guarded queue overhead entirely
- Want a 2-file header-only drop with zero build step and zero external dependencies
- Running on x86/x86-64 (the best-tested and only architecture the author has directly validated)

## Skip it when

- Need multiple producers or multiple consumers (use the same author's moodycamel::ConcurrentQueue instead)
- Threads need to switch producer/consumer roles at runtime, or use the queue from more than 2 threads
- Targeting AArch64 or another weakly-ordered architecture on an old pinned commit: size_approx() had a real SIGSEGV race from a missing release fence before publishing new blocks (issue #171); fixed, but verify the fix is in your pinned commit
- Need a version-pinned release: the project ships no tags (open issues #144/#146 ask for one), so you pin a raw commit SHA
- Destroying the queue while a thread is blocked in wait_dequeue() is undefined behavior — risky in ad-hoc shutdown paths

## How it is fast

Queue-of-queues design: a circular-linked-list of fixed-size 'block' ring buffers, with the producer owning tail indices/pointers and the consumer owning front indices/pointers so each thread only writes its own state. Enqueue/dequeue are wait-free (no CAS loop, no spinning), O(1) except when a new block must be malloc'd. On x86/x86-64 the required memory barriers compile down to no-ops, so the hot path is just plain loads and stores.

## Compared with alternatives

Pick this over atomic_queue, Boost.Lockfree, xenium, or oneTBB when you want the smallest possible header-only footprint (2 files, no build) purely for the SPSC case and don't need bounded/blocking strategy choices or MPMC support; atomic_queue's AtomicQueue (42ns) and OptimistAtomicQueue (33ns) edge it out slightly in the same shootout, so pick those instead if the last few nanoseconds matter more than dependency count.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (readerwriterqueue.h + atomicops.h; atomicops.h embeds Preshing's zlib-licensed semaphore for the blocking variant) |
| **Minimum toolchain** | C++11; MSVC2010+, GCC 4.7+ (GCC 4.6 has a fence bug), ICC 13+ |
| **Platforms** | x86/x86-64 (only architecture directly tested by the author); portable to ARM/PowerPC per code comments but AArch64 had a confirmed weak-memory-model race, fixed in a recent commit (issue #171); explicitly not for DEC Alpha |
| **Thread safety** | Exactly one producer thread + one consumer thread, fixed roles; concurrent/re-entrant calls from more than one thread per role trip a debug-only assert (issues #151/#162) and are undefined in release builds |
| **Drop-in for the baseline** | partial — same problem domain and a std::queue-like API shape, but SPSC-only and a different type, so call sites using std::mutex + std::queue must be rewritten, not just relinked |

## Gotchas

- size_approx() could dereference a null block on AArch64 due to a missing release fence in inner_enqueue() (issue #171) — fixed, but confirm the fix predates whatever commit you pin
- Plain enqueue() can malloc and grow the queue on demand; only try_enqueue() is guaranteed never to allocate
- Destroying the queue while a thread is blocked in wait_dequeue()/wait_dequeue_timed() is undefined behavior
- No tagged releases exist (open issues #144, #146); vendor a commit SHA rather than expecting semver tags

## Caveats and trade-offs

The project's own benchmarks never compare against std::mutex. benchmarks/bench.cpp and the blog post at moodycamel.com/blog/2013/a-fast-lock-free-queue-for-c++ (updated 2013 and Jan 2015) test only against Dmitry Vyukov's SPSC queue and folly::ProducerConsumerQueue. They ran on an AMD C-50, a Core 2 Duo T6500 and a Linode Xeon L5520 VM, with MSVC2010, ICC 13 and GCC 4.7.2/4.8.1/4.9.2. The std::mutex comparison comes entirely from the independent max0x7ba/atomic_queue shootout, whose 'std::mutex' baseline is a mutex-guarded ring buffer. Its 1P/1C throughput in that shootout varies a lot (5950X mean \~322M msg/s, stdev \~206M). [retier] Compiler and CPU are stated on benchmarks.html; the flags are not on that page and come from the reference Makefile's default release build.

Strictly single-producer/single-consumer only (roles can't switch); non-blocking try_enqueue never allocates but plain enqueue can grow the queue dynamically; blocking variant (BlockingReaderWriterQueue) adds wait_dequeue but destroying the queue while a thread waits on it is undefined behaviour.

## Maintenance

Actively maintained (last commit 2026-09-07, 4.6k stars) but ships no tagged releases; BSD-2-Clause (Simplified BSD, per LICENSE.md — GitHub's license detector shows NOASSERTION) and small enough (2 headers) to vendor directly.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** The independent atomic_queue shootout (src/benchmarks.cc in max0x7ba/atomic_queue; gcc-14.2.0, readerwriterqueue commit 2ae710d, Ryzen 5950X) shows a mean of 43ns vs 320ns for std::mutex. The project's own benchmarks/bench.cpp compares only against the 1024cores SPSC queue and folly::ProducerConsumerQueue, so the std::mutex evidence is third-party only.
- **Retiered** B to A: atomic_queue shootout: code src/benchmarks.cc in max0x7ba/atomic_queue; gcc-14.2.0 and AMD Ryzen 9 5950X stated on benchmarks.html and in results/632bae1.ryzen_5950x.smt1.20260914T121940.gcc-14.32.33.txt; flags from the reference Makefile default BUILD=release at commit 632bae1: -march=native -O3 -mtune=native -DNDEBUG (+ -fno-stack-protector, -falign-functions=64). Independent run against std::mutex: ReaderWriterQueue 43ns vs std::mutex 320-321ns per round-trip.
- **Verifier notes:** The 43ns vs 320ns figure matches the page. GitHub reports the license as NOASSERTION, but LICENSE.md is the Simplified BSD license (BSD-2-Clause). Only the third-party files in benchmarks/ext and Preshing's zlib-licensed semaphore in atomicops.h are excepted, so 'copyable' stands. Stars 4625 and last commit 2026-09-07 verified.
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** 1 producer/1 consumer, 500k items: 9.4 ns/item vs 131.37 ns for std::mutex + std::deque (13.98x best-of-7; medians 11.72 vs 172.71), while moodycamel::ConcurrentQueue on the same SPSC workload cost 61.54 ns (6.5x slower). A separate 10M-item median-of-11 run measured 6.36 vs 173.04 ns for std::mutex + std::queue (27x). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, 4 hardware threads, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://max0x7ba.github.io/atomic_queue/html/benchmarks.html>
  - <https://max0x7ba.github.io/atomic_queue/html/results.js>
  - <https://github.com/cameron314/readerwriterqueue>
  - <https://github.com/cameron314/readerwriterqueue/blob/master/LICENSE.md>
  - <https://github.com/cameron314/readerwriterqueue/blob/master/README.md>
  - <https://github.com/cameron314/readerwriterqueue/blob/master/benchmarks/bench.cpp>
  - <http://moodycamel.com/blog/2013/a-fast-lock-free-queue-for-c++>
- **Sources the enricher read:**
  - https://github.com/cameron314/readerwriterqueue (README, via gh api repos/.../readme)
  - https://github.com/cameron314/readerwriterqueue/git/trees/HEAD (full file tree, via gh api)
  - <https://github.com/cameron314/readerwriterqueue/blob/master/readerwriterqueue.h>
  - <https://github.com/cameron314/readerwriterqueue/blob/master/atomicops.h>
  - https://github.com/cameron314/readerwriterqueue/issues (issue list, via gh issue list)
  - <https://github.com/cameron314/readerwriterqueue/issues/171>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/cameron314/readerwriterqueue`) · [data/wave1/enrich/raw/github_com_cameron314_readerwriterqueue.json](../../../data/wave1/enrich/raw/github_com_cameron314_readerwriterqueue.json) (enrichment confidence 0.82)

</details>
