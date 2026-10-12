# dp::thread_pool (DeveloperPaul123/thread-pool)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 thread pool with per-worker mutex queues and stealing; first-party bench shows \~7% over BS::thread_pool 3.5.

| | |
|---|---|
| **Beats** | BS::thread_pool (bshoshany/thread-pool), task_thread_pool, riften::Thiefpool |
| **Claimed result** | Own MSVC table (256x256 matmul, relative to dp::thread_pool with std::function): dp std::function 93.27 ms/op (100%), dp std::move_only_function 90.66 ms/op (102.9%), dp fu2::unique_function 94.50 ms/op (98.7%), BS::thread_pool 99.73 ms/op (93.5%), task_thread_pool 91.29 ms/op (102.2%), riften::Thiefpool 93.18 ms/op (100.1%). README says it is faster than other thread pool libraries in most cases, but riften pulls ahead in some cases and task_thread_pool with many small tasks. |
| **Workload** | 256x256 matrix multiplication run through each pool, timed with nanobench, relative to dp::thread_pool with std::function. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5800X (16 x 3800 MHz), 32 GB RAM |
| **Compiler and flags** | MSVC for the quoted table; flags not stated |
| **Adoption** | 568 stars |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/DeveloperPaul123/thread-pool) · [benchmark](https://github.com/DeveloperPaul123/thread-pool#benchmarks) |

## Verdict

Author's nanobench run on a Ryzen 7 5800X under Windows (MSVC table; clang table via WSL also published, flags not stated) puts dp::thread_pool with std::move_only_function about 3% ahead of its std::function variant and about 7-10% ahead of BS::thread_pool_light 3.5.0, level with riften::Thiefpool, and behind task_thread_pool on the small cases; the timed loop measures task submission, not completion, and the 'NxN' sizes are really sqrt(N)-sided matrices.

## Use it when

- You want a small, readable, MIT, header-only C++20 pool to vendor, with futures or detached tasks.
- Many independent, flat tasks submitted from one producer thread (the shape the benchmarks exercise).
- Toolchains with std::move_only_function (C++23 library: MSVC 2022, recent libstdc++/libc++), where enqueue avoids a shared_ptr allocation per task.
- You need a per-thread init callback (constructor takes an init function receiving the worker id).

## Skip it when

- Recursive or nested parallelism where tasks wait on child futures: issue #57 (open, labelled bug) documents deadlock when all workers block in .get(); use a work-stealing fork-join runtime instead.
- Very fine-grained tasks or many producers: every enqueue takes two mutexes (the round-robin id queue and the target deque) and wakes a semaphore; task_thread_pool already beats it on small tasks in the author's own clang table (109.7% vs 100% at the 8-element case).
- When you need a parallel_for, priorities, cancellation of running tasks, or scheduling against TBB/OpenMP/Taskflow class runtimes; none were benchmarked.
- If you need evidence of end-to-end task completion speed: the published matrix benchmark times only submission (see gotchas).

## How it is fast

Each worker owns a std::deque guarded by a std::mutex plus a std::counting_semaphore; enqueue picks a target worker round-robin from a mutex-protected 'priority queue' of worker ids and signals that worker. Idle workers drain their own queue from the front, then steal one task from the back of a peer's queue, looping while an atomic unassigned-task counter is positive. The speed edge over BS::thread_pool comes mostly from per-worker queues (less contention than one shared queue) and from std::move_only_function avoiding the shared_ptr&lt;promise&gt; that std::function forces for enqueue(); there is no lock-free deque.

## Compared with alternatives

Pick it over riften::Thiefpool when you want a simpler mutex-based header that the author maintains and that matches Thiefpool within \~1-2% in the shared harness; pick nexus, Fork Union or a fork-join runtime (chili-style, Heartbeat, Nowa) for fine-grained or recursive work, where this pool's two-mutex submit path and blocking futures are weak points.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (benchmarks pull nanobench, doctest, function2 and the compared pools via CPM) |
| **Minimum toolchain** | C++20 (concepts, std::jthread, std::counting_semaphore, std::atomic::wait); README lists Visual Studio 2022, Clang 10+, GCC 11+, CMake 3.25+ |
| **Platforms** | any platform with a C++20 standard library; CI on Ubuntu and Windows |
| **Thread safety** | enqueue/enqueue_detach are safe from any thread (mutex-protected queues); clear_tasks is best-effort and can race with stealing per its own doc comment |
| **Drop-in for the baseline** | partial — similar enqueue/future model to BS::thread_pool but different method names (enqueue/enqueue_detach vs submit/push_task), no parallel loops |

## Gotchas

- Benchmark harness flaw: in benchmark/source/matrix_multiplication.cpp the provider lambdas return void, so the results vector stays empty and each nanobench epoch only enqueues 25k-100k detached tasks and returns without waiting for them; the ms/op figures measure submission throughput (with earlier epochs' backlog still running), not time to finish the work.
- The labels overstate the work: multiply_array uses sqrt(a.size()) as the side length, so '256x256' is a 16x16 int matmul (8 is 2x2, 1024 is 32x32); argument vectors are copied into each task.
- Baseline is old: the benchmark pins bshoshany/thread-pool 3.5.0 and uses BS::thread_pool_light, not the current BS::thread_pool releases.
- enqueue_detach swallows exceptions silently; constructor throws std::invalid_argument for 0 threads; destructor waits for all queued tasks.

## Known shortcomings

- Benchmark flaw in benchmark/source/matrix_multiplication.cpp: the providers return void and the results vector stays empty, so the timed loop only enqueues detached tasks and never waits; ms/op is submission throughput, not completion time. Matrix sizes are mislabelled (multiply_array uses sqrt(size), so '256x256' is 16x16 and '1024x1024' is 32x32). Baseline is the old bshoshany 3.5.0 thread_pool_light. Open issue 57: deadlock on recursive tasks.

## Caveats and trade-offs

Margins against BS::thread_pool are about 7 percent; task_thread_pool beats the std::function variant and riften ties it; one workload only; run on Windows with frequency scaling noted by the author; compares against other small thread pools, not TBB, OpenMP or Rayon; compiler version and flags not stated. Repo now lives at github.com/ptsouchlos/thread-pool (old DeveloperPaul123 URL redirects). [retier] Timed loop only enqueues detached tasks and never waits for completion, so ms/op is submission throughput; matrix sizes are mislabelled ('256x256' is 16x16, '1024x1024' is 32x32); baseline is the old bshoshany 3.5.0 thread_pool_light; open issue 57 reports a deadlock on recursive tasks.

Simple shared-queue pool with per-thread queues and work stealing; C++20; needs std::move_only_function for best speed. Not a fork-join or task-graph scheduler.

## Maintenance

Active (last commit 2026-09-10, release 0.7.0, 568 stars, account renamed from DeveloperPaul123 to ptsouchlos); MIT and small enough to vendor, but the speed claim rests on a submission-only first-party benchmark.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** README Benchmarks section shows a nanobench MSVC table (code in ./benchmark, CPU Ryzen 7 5800X stated) against BS::thread_pool, task_thread_pool and riften::Thiefpool, but compiler version and flags are not given; first-party, margins within a few percent, so C.
- **Retiered** C to D: Downgraded from C. The matrix_multiplication benchmark never waits for results (providers return void, the results vector stays empty), so the timed loop measures task submission throughput, not completion; sizes are mislabelled (sqrt). Kept as a submission-throughput comparison and documented, not rejected: the numbers are real, only mislabelled.
- **Verifier notes:** Repo was renamed/moved to ptsouchlos/thread-pool; README CPM snippet uses that path. MIT license, 568 stars, last commit 2026-09-10 confirmed. Clang results file linked in README was not opened.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/DeveloperPaul123/thread-pool/HEAD/README.md>
  - <https://raw.githubusercontent.com/DeveloperPaul123/thread-pool/HEAD/LICENSE>
  - <https://github.com/DeveloperPaul123/thread-pool/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/README.md>
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/include/thread_pool/thread_pool.h>
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/include/thread_pool/thread_safe_queue.h>
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/benchmark/source/main.cpp>
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/benchmark/source/matrix_multiplication.cpp>
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/benchmark/source/thread_pool_scaling.cpp>
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/benchmark/source/count_primes.cpp>
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/benchmark/include/utilities.h>
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/benchmark/results/benchmark_results_clang.md>
  - <https://raw.githubusercontent.com/ptsouchlos/thread-pool/HEAD/benchmark/results/benchmark_results_msvc.md>
  - <https://github.com/ptsouchlos/thread-pool/tree/main/benchmark/source>
  - <https://github.com/ptsouchlos/thread-pool/issues?q=is%3Aissue>
  - <https://github.com/ptsouchlos/thread-pool/issues/57>
  - <https://github.com/ptsouchlos/thread-pool>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/developerpaul123/thread-pool`) · [data/wave11/enrich/raw/github_com_developerpaul123_thread_pool.json](../../../data/wave11/enrich/raw/github_com_developerpaul123_thread_pool.json) (enrichment confidence 0.75)

</details>
