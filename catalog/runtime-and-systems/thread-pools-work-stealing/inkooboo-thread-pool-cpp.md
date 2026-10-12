# inkooboo/thread-pool-cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT (MPMCBoundedQueue is BSD-2-Clause, Dmitry Vyukov)` · 🔴 abandoned

> Header-only C++11 thread pool with per-worker Vyukov MPMC queues; reposts jobs about 20x faster than an asio io_service pool.

| | |
|---|---|
| **Beats** | boost::asio thread pool |
| **Claimed result** | Reposting 1,000,001 jobs in 61.7-70.3 ms vs 1,381.6-1,393.2 ms for the boost::asio io_service based pool (about 20x, derived from page data). |
| **Workload** | Reposting 1,000,001 jobs through the pool (benchmark/benchmark.cpp). |
| **Metric** | throughput |
| **Adoption** | 585 stars |
| **Last commit** | 2018-02-06 |
| **Links** | [repository](https://github.com/inkooboo/thread-pool-cpp) · [benchmark](https://github.com/inkooboo/thread-pool-cpp) |

## Verdict

The README shows one example run of benchmark/benchmark.cpp: 16 concurrent chains each reposting a job 1,000,001 times, 61.7-70.3 ms per chain versus 1,381.6-1,393.2 ms with an author-written boost::asio io_service pool using hardware_concurrency threads (about 20x, derived from page data); no compiler, flags, Boost version or CPU are given. The workload favours this design: a repost from a worker lands in that worker's own lock-free queue, while the asio pool funnels everything through one shared io_service queue.

## Use it when

- Many tiny fire-and-forget tasks where std::function allocation and a mutex-guarded shared queue dominate cost
- Tasks that repost continuations from inside workers (actor-style or chained callbacks), which stay on the local queue
- Projects that want a small, dependency-free, header-only C++11 pool they can vendor and modify
- Callables with captures under 128 bytes (static_assert enforced) or a custom FixedFunction size via ThreadPoolImpl

## Skip it when

- Latency-sensitive work after idle periods: idle workers poll with a 1 ms sleep, so wake-up latency is up to \~1 ms and idle threads burn CPU (issue #20)
- When you need every posted task to run at shutdown: the destructor stops workers immediately and drops queued tasks (open issue #32, also #17 and #27)
- Bursty producers: the per-worker queue is bounded, and post() throws std::runtime_error when the chosen worker's queue is full
- Fork-join or recursive divide-and-conquer workloads: no join/wait primitive and stealing is from one neighbour only; use a real work-stealing scheduler (TBB, Taskflow, libfork) instead
- Projects needing maintenance: last commit 2018-02-06, open issues include a deadlock when used as a global in a DLL (#29)

## How it is fast

Each worker has its own Dmitry Vyukov bounded MPMC ring buffer (per-cell sequence numbers, one CAS per push/pop, cache-line padding), so a post from a worker thread goes to that worker's own queue with no shared lock. Posts from non-worker threads are spread round-robin with a relaxed atomic counter. FixedFunction avoids heap allocation per task. An idle worker steals one task at a time from a single fixed neighbour (worker i+1) and otherwise sleeps 1 ms.

## Compared with alternatives

Pick it over nexus or dp::thread_pool only when you need a tiny C++11-compatible, header-only fire-and-forget pool you will vendor and patch yourself; for fork-join or parallel-for, Fork Union, citor or a Taskflow/TBB-class scheduler are better documented and maintained, and nexus publishes comparisons against Taskflow and BS::thread_pool rather than an author-written asio pool.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (boost::asio only for the optional benchmark comparison; googletest for tests) |
| **Minimum toolchain** | C++11 (CMake builds with -std=c++11) |
| **Platforms** | any platform with std::thread and thread_local |
| **Thread safety** | post/tryPost are safe from any thread (lock-free MPMC queues); construction, move and destruction are not thread-safe |
| **Drop-in for the baseline** | partial: post(handler) matches io_service::post in shape, but there is no run()/IO integration, no strand and tasks must be nullary and fit in 128 bytes |

## Gotchas

- All exceptions thrown by tasks are silently swallowed by a catch(...) in the worker loop.
- Move constructors of ThreadPoolImpl, Worker and MPMCBoundedQueue are written as '\*this = rhs;' with rhs a named rvalue reference, which cannot bind to the move-assignment operator; they fail to compile if instantiated, so treat the pool as non-movable.
- Work stealing is a single ring: worker i only steals from worker i+1, one task at a time, from the FIFO end of an MPMC queue, so imbalance spreads slowly.
- Queue size must be a power of two (&gt;= 2) or the constructor throws std::invalid_argument; Worker::stop uses a relaxed store on the running flag.

## Known shortcomings

- The benchmark favours the design: a repost lands in the worker's own queue while the asio pool uses one shared io_service queue. The destructor drops queued tasks (open issue 32, also 17 and 27); idle workers poll with a 1 ms sleep (20); a DLL-global deadlock (29); post() throws when the 1024-slot queue is full; exceptions are swallowed; the move constructors (\*this = rhs) will not compile if used; steals only from the neighbour i+1.

## Caveats and trade-offs

Not compared against TBB, OpenMP or Rayon; baseline is an author-written asio io_service pool with a single shared queue, while reposting from a worker hits that worker's own queue, so the benchmark favors the work-distribution design. README gives no compiler, flags or CPU. MPMCBoundedQueue is under Vyukov's BSD-2-Clause terms (OSI-approved). The yvoinov/thread-pool-cpp fork reports the same numbers.

Header-only C++11; work-stealing and work-distribution modes; MPMC bounded queue. Fixed-size task wrapper.

## Maintenance

Abandoned since February 2018 (585 stars, 127 forks, not archived) with open bugs on shutdown task loss and DLL-global deadlock, but MIT plus BSD-2-Clause and about 600 lines, so it is easy to vendor and fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README shows an example run of benchmark/benchmark.cpp (job reposting, 16 concurrent chains of 1,000,001 reposts) against an author-written boost::asio io_service pool (benchmark/asio_thread_pool.hpp); no compiler, flags or CPU given, so first-party C.
- **Verifier notes:** The separately licensed part turned out to be BSD-2-Clause, so usability moves from mixed to copyable. Last commit 2018-02-06 ('Fix multiple link units'), 585 stars, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `usability`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/benchmark/asio_thread_pool.hpp>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/include/thread_pool/mpmc_bounded_queue.hpp>
  - <https://github.com/inkooboo/thread-pool-cpp/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/benchmark/asio_thread_pool.hpp>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/include/thread_pool.hpp>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/include/thread_pool/thread_pool.hpp>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/include/thread_pool/worker.hpp>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/include/thread_pool/fixed_function.hpp>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/include/thread_pool/mpmc_bounded_queue.hpp>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/include/thread_pool/thread_pool_options.hpp>
  - <https://raw.githubusercontent.com/inkooboo/thread-pool-cpp/HEAD/CMakeLists.txt>
  - <https://github.com/inkooboo/thread-pool-cpp>
  - <https://github.com/inkooboo/thread-pool-cpp/issues?q=is%3Aissue>
  - <https://github.com/inkooboo/thread-pool-cpp/issues/32>
  - <https://github.com/inkooboo/thread-pool-cpp/issues/20>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/inkooboo/thread-pool-cpp`) · [data/wave11/enrich/raw/github_com_inkooboo_thread_pool_cpp.json](../../../data/wave11/enrich/raw/github_com_inkooboo_thread_pool_cpp.json) (enrichment confidence 0.8)

</details>
