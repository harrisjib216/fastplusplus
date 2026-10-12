# moodycamel::ConcurrentQueue

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause OR BSL-1.0` · 🟢 active

> Lock-free MPMC C++11 queue with per-producer sub-queues and bulk ops, beating boost::lockfree::queue on throughput.

| | |
|---|---|
| **Beats** | boost::lockfree::queue |
| **Claimed result** | 8-core AWS c1.xlarge, balanced workload, 8 threads: moodycamel (with tokens) 795.01k ops/s vs boost::lockfree::queue 647.96k ops/s (\~1.23x, derived from page data) vs tbb::concurrent_queue 692.97k ops/s (\~1.15x, derived from page data). Only-enqueue (all producers), 8 threads: moodycamel with tokens (single-item enqueue, not bulk) 65.56M ops/s vs boost::lockfree 289.71k ops/s (\~226x, derived from page data) vs tbb 936.20k ops/s (\~70x, derived from page data). Overall weighted average ops/s/thread: moodycamel (including bulk) 19.04M vs boost::lockfree 4.07M (\~4.7x, derived from page data) vs tbb 5.09M (\~3.7x, derived from page data). The 32-core cc2.8xlarge run gives 18.50M vs 3.27M vs 4.21M. LockBasedQueue (a naive linked-list queue guarded by std::mutex) degrades in the balanced test from 2.6149us/op at 2 threads to 0.1120ms/op at 16 threads. |
| **Workload** | Producer/consumer microbenchmarks on AWS 8-core (c1.xlarge, Xeon E5506 @2.13GHz) and 32-core (cc2.8xlarge, Xeon E5-2670 @2.60GHz) instances, varying thread counts, comparing moodycamel::ConcurrentQueue (with/without tokens, incl. bulk ops), boost::lockfree::queue, tbb::concurrent_queue, and a std::mutex-locked queue (LockBasedQueue), under balanced mixed producer/consumer and producer-only workloads. |
| **Metric** | throughput |
| **Hardware** | AWS c1.xlarge: 8-core Intel Xeon E5506 @ 2.13GHz, Ubuntu. AWS cc2.8xlarge: 32-core Intel Xeon E5-2670 @ 2.60GHz, Ubuntu. Also a Linode VM, 8-core Intel Xeon E5-2650L @ 1.80GHz, Fedora 19. Also a dual-core AMD C-50 @ 1.0GHz netbook, Windows 7. |
| **Compiler and flags** | g++ (version not stated for the AWS runs; 'g++ 4.81' stated for the Linode/Fedora 19 and MinGW-w64 netbook runs); optimization flags not stated on the blog page |
| **Adoption** | 12.5k stars; packaged in vcpkg, used across many C++ game/systems projects |
| **Last commit** | 2026-07-11 |
| **Links** | [repository](https://github.com/cameron314/concurrentqueue) · [benchmark](http://moodycamel.com/blog/2014/a-fast-general-purpose-lock-free-queue-for-c++#benchmarks) |

## Verdict

On an 8-core AWS c1.xlarge, moodycamel with tokens reached 795.01k ops/s vs boost::lockfree::queue's 647.96k ops/s (\~1.2x) at 8 threads under a balanced producer/consumer workload; the large 70-226x figures are from a producer-only, single-item-with-tokens enqueue microbenchmark, and the \~4-5x weighted averages include moodycamel's bulk operations, which boost and tbb do not support. g++ version and optimization flags are not stated for the AWS runs.

## Use it when

- Producer/consumer pipelines with many independent threads, where cross-producer linearizability is not required
- Workloads that can batch items — bulk enqueue/dequeue is where the largest measured gains are (up to \~226x on producer-only microbenchmarks vs boost::lockfree in this record)
- Need both non-blocking (spin/poll) and blocking (wait_dequeue) consumer modes from one library
- Header-only C++11 codebase that can't take a Boost or TBB dependency
- Per-item ordering only needs to hold within a single producer, not globally

## Skip it when

- Need strict global linearizable ordering across independent producers — explicitly not guaranteed
- NUMA machines where cross-socket memory reuse patterns matter — not NUMA-aware by the author's own admission
- Single-item, low-contention enqueue only, where boost::lockfree::queue is just \~1.2x slower and you'd rather have a narrower API
- Compilers older than g++4.8 / pre-VS2012, or g++4.6 specifically (documented std::atomic bug)
- Strict per-producer FIFO ordering is load-bearing: issue #437 (open, reported Dec 2025) describes a model-checker-found case where bulk, token-less enqueue/dequeue with small block sizes may reorder a producer's own sequence; unresolved as of this write-up

## How it is fast

Each producer gets its own internal sub-queue built from contiguous, freelist-recycled blocks (default 32 elements) instead of a shared linked list, so producers rarely contend; consumers scan sub-queues for a non-empty one. Tokens let a thread cache its producer/consumer handle to skip repeated lookups, and bulk enqueue/dequeue amortize per-operation atomic/CAS overhead across many elements at once. try_enqueue never allocates once the queue is correctly pre-sized, trading a possible false-full return for zero lock/alloc cost on the hot path.

## Compared with alternatives

no siblings catalogued yet

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for ConcurrentQueue; BlockingConcurrentQueue additionally needs lightweightsemaphore.h, shipped in the same repo |
| **Minimum toolchain** | C++11; VS2012+ or g++ 4.8+ (g++4.6 has a known std::atomic bug and is unsupported) |
| **Platforms** | any (pure C++11 atomics, no inline assembly); CI cross-compiles and runs tests for riscv64 Linux under QEMU; author-tested on Linux (Fedora) and Windows on x86 |
| **Thread safety** | Fully thread-safe for concurrent use from any number of threads; not linearizable across independent producers; tokens themselves are not thread-safe (one per thread/task) |
| **Drop-in for the baseline** | partial — same general templated-queue usage pattern as boost::lockfree::queue (enqueue/try_dequeue), but adds no-throw bulk ops and tokens, and drops boost's trivial-constructor/trivial-destructor restriction; not an API/ABI-identical drop-in |

## Gotchas

- Not linearizable across independent producers; ordering is only guaranteed within a single producer's own enqueues
- try_enqueue never allocates — correct pre-sizing requires working through the block-size/producer-count formulas in the README, and even then contention can cause spurious false-full returns under weak memory ordering
- Exception safety requires element destructors and any bulk-operation iterators to never throw; only enqueue-side constructor exceptions roll back cleanly
- Open issue #437 (unresolved) questions whether bulk, token-less dequeue can skip a prefix of a sub-queue under certain interleavings with small block sizes

## Caveats and trade-offs

This is a first-party benchmark: the author's 2014 blog post plus the repo's own benchmarks/ directory. The blog compares against Boost 1.55 lockfree::queue and TBB 4.3 concurrent_queue, which are now old versions. Optimization flags are not stated. The 226x only-enqueue figure compares single-item enqueue with tokens against boost; it is not a bulk operation. However, it is an extreme-contention producer-only microbenchmark. The overall weighted averages include moodycamel's bulk operations, which boost and tbb do not support, so they are not like-for-like. LockBasedQueue is a hand-written linked list guarded by std::mutex, not std::queue.

Not linearizable across independent producers; not NUMA-aware; single-header C++11; the largest speedups (\~70-226x) come from its bulk enqueue/dequeue API rather than single-item ops, where the advantage over boost::lockfree is closer to \~1.2x in this benchmark.

## Maintenance

Actively maintained (last commit 2026-07-11, 12.5k GitHub stars, packaged in vcpkg); dual BSD-2-Clause/BSL-1.0 single header, trivial to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** These are first-party numbers from the author's blog, produced with the repo's own benchmarks/benchmarks.cpp. The CPU models are stated, but the optimization flags are not, and the g++ version is not stated for the AWS runs. This is C under the own-benchmark-with-partial-methodology rule, and the 226x figure is capped at C anyway because flags are unstated.
- **Verifier notes:** All claimed numbers are on the page and belong to the correct rows. The original record wrongly attributed 65.56M to bulk enqueue and did not mark its ratios as derived; both are fixed. GitHub reports license NOASSERTION. LICENSE.md confirms a dual license, Simplified BSD or Boost Software License 1.0. Other checks: 12,493 stars, not archived, not a fork, last commit 2026-07-11.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** 2 producers/2 consumers, 1M items: with ProducerToken/ConsumerToken 115.76 ns/item vs 176.76 ns for std::mutex + std::deque (1.53x), but the plain enqueue()/try_dequeue() API measured 243.01 ns and lost to the mutex. Nothing warns at compile time. (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, 4 hardware threads, run 2026-09-03-third-party); Aggregate throughput fell from 1P1C to 2P2C (with tokens 29.2 to 15.3 M items/s, 0.52x; without tokens 15.8 to 6.2 M/s) while std::mutex + std::queue rose from 5.8 to 7.4 M/s. Single-threaded and uncontended, the bare queue was slower than a mutex (16.64 vs 7.94 ns). (developer source, private repo; selection measurement in third_party/concurrentqueue/VENDORING.md, median of 11 runs, shared 4-core VM; evaluation for run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <http://moodycamel.com/blog/2014/a-fast-general-purpose-lock-free-queue-for-c++>
  - <https://github.com/cameron314/concurrentqueue>
  - <https://github.com/cameron314/concurrentqueue/blob/master/LICENSE.md>
  - <https://github.com/cameron314/concurrentqueue/tree/master/benchmarks>
  - <https://github.com/cameron314/concurrentqueue/blob/master/benchmarks/lockbasedqueue.h>
  - <https://github.com/cameron314/concurrentqueue/blob/master/build/makefile>
- **Sources the enricher read:**
  - <https://github.com/cameron314/concurrentqueue>
  - <https://github.com/cameron314/concurrentqueue/blob/master/README.md>
  - <https://github.com/cameron314/concurrentqueue/blob/master/CMakeLists.txt>
  - https://github.com/cameron314/concurrentqueue (repo file tree)
  - <https://github.com/cameron314/concurrentqueue/issues/437>
  - <https://github.com/cameron314/concurrentqueue/issues/399>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/cameron314/concurrentqueue`) · [data/wave0-seed/enrich/raw/github_com_cameron314_concurrentqueue.json](../../../data/wave0-seed/enrich/raw/github_com_cameron314_concurrentqueue.json) (enrichment confidence 0.75)

</details>
