# riften::Thiefpool (ConorWilliams/Threadpool)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MPL-2.0` · 🔴 abandoned

> Small C++20 work-stealing thread pool on Chase-Lev deques; about 8% faster than BS::thread_pool in one third-party matmul benchmark.

| | |
|---|---|
| **Beats** | BS::thread_pool (bshoshany/thread-pool) |
| **Claimed result** | Clang results (relative to dp::thread_pool with std::function = 100%): Thiefpool 98.3-99.0% vs BS::thread_pool 90.2-94.5%; 1024x1024: 52.80 ms/op vs BS 57.14 ms/op, about 8% faster (derived from page data); 8x8: 172.33 vs 188.16 ms. MSVC 256x256: 93.18 vs 99.73 ms. task_thread_pool beats Thiefpool at 8x8 to 256x256 (e.g. 154.74 vs 172.33 ms at 8x8). |
| **Workload** | Matrix multiplication (8x8 to 1024x1024) split into tasks on the pool, measured with nanobench in a third-party pool comparison. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5800X, 32 GB RAM, Windows (Clang via WSL) |
| **Compiler and flags** | Clang and MSVC; flags not stated |
| **Adoption** | 117 stars |
| **Last commit** | 2023-03-26 |
| **Links** | [repository](https://github.com/ConorWilliams/Threadpool) · [benchmark](https://raw.githubusercontent.com/DeveloperPaul123/thread-pool/HEAD/benchmark/results/benchmark_results_clang.md) |

## Verdict

The only numbers come from dp::thread_pool's own nanobench matrix-multiplication comparison on a Ryzen 7 5800X (Windows, Clang via WSL and MSVC, flags not stated). Thiefpool scored 98.3-99.0% of dp::thread_pool versus 90.2-94.5% for BS::thread_pool (1024x1024: 52.80 vs 57.14 ms/op, about 8% faster, derived from page data), and it trailed task_thread_pool at 8x8 to 256x256. The repo's own bench.cpp (10M enqueues of an atomic increment, three workloads) publishes no results.

## Use it when

- A single producer thread submits many small, independent tasks and wants lower per-task overhead than a mutex-and-condition-variable pool such as BS::thread_pool.
- Fire-and-forget jobs where enqueue_detach skips the std::future allocation.
- C++20 codebases using CPM.cmake that want a tiny pool (one header plus function2 and riften::Deque).
- Coarse parallel chunks (e.g. 256x256 to 1024x1024 matmul tiles) where it measured 52.80 vs 57.14 ms/op against BS::thread_pool.

## Skip it when

- Submitting from several threads or from inside tasks: execute() bumps a non-atomic counter and calls the deque's owner-only emplace from the caller's thread. That is a data race unless one thread does all the enqueuing (open issue #4, no maintainer reply).
- Tasks that block on or depend on later tasks: a worker can go back to sleep while another worker's deque holds a pending task (open issue #2, 'Deadlock due to lack of cross thread signalling').
- Latency- or power-sensitive services: woken workers busy-spin and steal until the global in-flight count reaches zero.
- Fork-join or recursive parallelism: there is no task-local spawn/join; choose libfork, chili or Fork Union style schedulers.
- Small-task workloads where dp::thread_pool or task_thread_pool measured faster (e.g. 8x8 matmul: 172.33 ms vs task_thread_pool 154.74 ms). The project has been abandoned since 2023-03-26.

## How it is fast

Each worker owns a lock-free riften::Deque (Chase-Lev work-stealing deque) of fu2::unique_function tasks, a move-only type-erased function with small-buffer storage. Tasks are dealt round-robin to the deques, and a lightweight semaphore (adapted from Preshing's) wakes the target worker. Workers take from their own deque first; after 100 spins with their own deque empty they steal from a random deque (xoroshiro128\*\*). They keep spinning while a global in-flight counter is above zero. enqueue avoids std::packaged_task type erasure by using a NullaryOneShot wrapper.

## Compared with alternatives

Pick it over BS::thread_pool-style pools only when one thread submits many independent tasks and the C++20 dependency is fine. dp::thread_pool measured 1-2% faster in the same benchmark and is maintained, and Fork Union or citor are the better choice for parallel-for or fork-join throughput.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | function2 (Naios/function2 4.1.0), riften::Deque (ConorWilliams/ConcurrentDeque v1.1.0), Threads; fetched via CPM.cmake |
| **Minimum toolchain** | C++20 (std::jthread, std::stop_token, concepts); CMake 3.14+ |
| **Platforms** | any with C++20 threads; the semaphore has Windows, macOS and POSIX backends |
| **Thread safety** | Workers are concurrent, but enqueue/enqueue_detach are safe only from a single thread (non-atomic round-robin counter; Chase-Lev push is owner-only). Not documented in the README. |
| **Drop-in for the baseline** | partial: future-returning enqueue similar to BS::thread_pool::submit, but no wait-all, parallel loops, pause or resize, and no multi-producer submission |

## Gotchas

- The in-flight counter is decremented before a task runs, so workers sleep while a long task is still executing. A task enqueued to that busy worker's deque waits for it to finish (issue #2).
- Exceptions from enqueue tasks go into the std::future. An exception thrown by an enqueue_detach task escapes the worker thread and calls std::terminate (no try/catch in the worker loop).
- Each deque keeps every buffer it outgrows in a _garbage vector until the pool is destroyed, so memory after a burst is not returned.
- MPL-2.0: file-level copyleft; modified pool files must stay MPL.

## Known shortcomings

- Open issue 4: execute() uses a non-atomic count++ and calls the owner-only Chase-Lev emplace from the caller thread, so multi-producer enqueue is a data race. Open issue 2: a worker sleeps while a pending task waits behind a long task. An exception in an enqueue_detach task calls std::terminate. The single-producer benchmark against dp::thread_pool is unaffected.

## Caveats and trade-offs

The only published numbers come from another pool's README benchmark (dp::thread_pool). The repo has its own benchmark/bench.cpp (10M enqueue micro-benchmark) but publishes no results. Compiler flags not stated, Windows machine with frequency scaling noted, error margins up to 1.4%. Differences are small: Thiefpool is about 1-2% behind dp::thread_pool and behind task_thread_pool at small and medium sizes, ahead only of BS::thread_pool. BS::thread_pool is not TBB, OpenMP or Rayon. Last commit 2023-03-26, more than 3 years ago.

C++20 only; lock-free riften::Deque work stealing; enqueue returns std::future (enqueue_detach avoids the shared state allocation); MPL-2.0 file-level copyleft.

## Maintenance

Abandoned: last commit 2023-03-26, v2.1.1, two open concurrency issues (#2, #4) with no maintainer reply. It is small enough to vendor under MPL-2.0 if you keep submission on one thread.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** A third-party competitor's nanobench comparison (DeveloperPaul123/thread-pool, with public benchmark code) on a Ryzen 7 5800X using Clang and MSVC, but no flags stated and it is not a well-known independent suite, so C.
- **Verifier notes:** Clang and MSVC numbers match the dp::thread_pool result pages. Corrected maintenance to abandoned (last commit 2023-03-26 is more than 3 years before 2026-10) and the caveat about the repo having no benchmark. MPL-2.0 and 117 stars confirmed.
- **Fields the verifier corrected:** `maintenance_status`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/DeveloperPaul123/thread-pool/HEAD/benchmark/results/benchmark_results_clang.md>
  - <https://raw.githubusercontent.com/DeveloperPaul123/thread-pool/HEAD/benchmark/results/benchmark_results_msvc.md>
  - <https://raw.githubusercontent.com/DeveloperPaul123/thread-pool/HEAD/README.md>
  - <https://raw.githubusercontent.com/ConorWilliams/Threadpool/HEAD/README.md>
  - <https://raw.githubusercontent.com/ConorWilliams/Threadpool/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ConorWilliams/Threadpool/HEAD/benchmark/bench.cpp>
  - <https://github.com/ConorWilliams/Threadpool>
  - <https://github.com/ConorWilliams/Threadpool/tree/master/benchmark>
  - <https://github.com/ConorWilliams/Threadpool/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ConorWilliams/Threadpool/HEAD/README.md>
  - <https://raw.githubusercontent.com/ConorWilliams/Threadpool/HEAD/benchmark/bench.cpp>
  - <https://raw.githubusercontent.com/ConorWilliams/Threadpool/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ConorWilliams/Threadpool/HEAD/include/riften/thiefpool.hpp>
  - <https://raw.githubusercontent.com/ConorWilliams/Threadpool/HEAD/include/riften/semaphore.hpp>
  - <https://raw.githubusercontent.com/ConorWilliams/ConcurrentDeque/HEAD/include/riften/deque.hpp>
  - <https://github.com/ConorWilliams/Threadpool/issues?q=is%3Aissue>
  - <https://github.com/ConorWilliams/Threadpool/issues/2>
  - <https://github.com/ConorWilliams/Threadpool/issues/4>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/conorwilliams/threadpool`) · [data/wave11/enrich/raw/github_com_conorwilliams_threadpool.json](../../../data/wave11/enrich/raw/github_com_conorwilliams_threadpool.json) (enrichment confidence 0.75)

</details>
