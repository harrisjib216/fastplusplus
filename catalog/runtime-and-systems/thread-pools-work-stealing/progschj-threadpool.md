# ThreadPool (progschj)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Zlib` · 🔴 abandoned

> Single-header C++11 fixed-size thread pool returning futures; not shown to beat std::async thread-per-task overall.

| | |
|---|---|
| **Beats** | std::async(std::launch::async), one thread per task (labelled 'C++ thread' in the benchmark) |
| **Claimed result** | Red-Portal benchmark: +3.7% on a degenerate fluid solver and -15% on matmul vs std::async thread-per-task; no valid measurement. |
| **Workload** | Third-party 'Thread Pool Colosseum' runs a 2048x2048 fluid solver and a 1024x1024 float matrix multiplication (one task per row, 1024 tasks) and reports total wall time of forking plus joining; progschj ThreadPool uses 4 workers. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-7700HQ, Manjaro Linux |
| **Compiler and flags** | clang 6.0.0; flags effectively unstated: the benchmark's CMakeLists.txt builds a BUILD_FLAGS string with -std=c++14 -g -O3 but only prints it and never applies it to the target, so a default CMake build is probably unoptimized |
| **Adoption** | about 8.8k stars, about 2.3k forks |
| **Last commit** | 2014-09-26 |
| **Links** | [repository](https://github.com/progschj/ThreadPool) · [benchmark](https://github.com/Red-Portal/thread-pool-benchmark) |

## Verdict

In Red-Portal's 'Thread Pool Colosseum' (one run per row, clang 6.0.0, i7-7700HQ, Manjaro, optimization flags never applied), ThreadPool with 4 workers took 562.66 ms against 488.52 ms for std::async-per-row on a 1024x1024 float matrix multiplication (about 15% slower). It took 1567.72 against 1628.18 ms on a 2048x2048 fluid solver (about 3.7% faster, but on a zero-field workload whose tasks all write the same row). Its one clear advantage was enqueue cost: 0.29 ms against 473.69 ms spent launching std::async threads.

## Use it when

- Coarse, independent tasks (milliseconds each or more) where creating a thread per task is the cost to avoid. In the benchmark, 1024 std::async launches spent 473.7 ms forking, against 0.29 ms of enqueue calls for ThreadPool.
- Capping concurrency at a fixed thread count in a service or tool that would otherwise call std::async per request.
- Projects that want a tiny, auditable, dependency-free header under the permissive Zlib licence, or a teaching example of the mutex-plus-condition-variable pool pattern.
- Pre-C++17 codebases (C++11/14) that need futures from a pool.

## Skip it when

- Fine-grained tasks: every task takes the global queue lock and several heap allocations. In issue #84, 1,000,000 trivial tasks on 10 threads took about 5 s, against 0.005 s for a plain loop.
- Throughput-critical parallel loops: in the only benchmark, the Sean Parent pools, GCD and TBB all finished both workloads faster (matrix multiplication 423.7-490.0 ms vs 562.7 ms; fluid solver 1158.4-1235.6 ms vs 1567.7 ms).
- Recursive or fork-join code where tasks block on futures of tasks they enqueue: with a fixed worker count and no work stealing, every worker can end up waiting and the pool deadlocks.
- C++20 builds: it uses std::result_of, which fails to compile with clang 16 in C++20 mode (issue #109). MSVC already flags it in C++17 (C4996/STL4014, issue #89).
- Unmaintained since 2014-09-26 with 41 open issues; choose a maintained pool if you need fixes or features.

## How it is fast

The only saving is thread reuse. Workers are created once, so an enqueue costs a mutex lock, a push onto one std::queue&lt;std::function&lt;void()&gt;&gt; and a condition_variable::notify_one, instead of creating an OS thread per task. Each task still allocates a std::packaged_task through make_shared, its future's shared state and a std::function wrapper. All workers share one mutex-protected FIFO; there is no work stealing or per-worker queue.

## Compared with alternatives

Pick it only for the smallest dependency-free C++11 pool with futures. riften::Thiefpool and dp::thread_pool (per-worker or work-stealing queues, measured faster than BS::thread_pool), inkooboo/thread-pool-cpp (about 20x faster job reposting than a boost::asio pool) or nexus are better whenever per-task overhead or throughput matters.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library threads; link the platform thread library, e.g. -pthread) |
| **Minimum toolchain** | C++11; C++17 compiles with deprecation warnings; C++20 needs std::result_of replaced with std::invoke_result_t |
| **Platforms** | any platform with std::thread |
| **Thread safety** | enqueue may be called from several threads (the queue is guarded by one mutex). Not documented in the README; enqueue after the destructor has set stop throws std::runtime_error. |
| **Drop-in for the baseline** | partial: enqueue(f, args...) returns a std::future like std::async(std::launch::async, ...), but tasks share n workers, can queue behind each other, and the returned future does not block in its destructor as a std::async future does |

## Gotchas

- Arguments go through std::bind, which passes them to the callable as lvalues, so a move-only argument such as std::unique_ptr taken by value does not compile (issue #93). Enqueue a lambda that move-captures it instead.
- The destructor runs every queued task before joining (workers exit only when stop is set and the queue is empty), so destroying a pool with a backlog blocks. ThreadPool(0) starts no workers, so its futures never become ready.
- A task's exception is stored in its future by std::packaged_task; if the caller drops the future, the exception is lost silently.
- The benchmark behind the record is flawed. Its CMakeLists.txt never applies -O3, so the build was probably unoptimized. ThreadPool was hard-coded to 4 workers on a 4-core/8-thread i7-7700HQ, while the Sean Parent pools use hardware_concurrency() and std::async uses a thread per task. The fluid solver never calls addInflow, so all fields stay zero and the pressure solve exits after one sweep. Each of its 2048 row tasks restarts idx at 0, so they all write row 0 of _dst (a data race), and check_result compares zeros with zeros, so it cannot catch this. The 3.7% fluid 'win' is measured on that racy, degenerate workload.

## Known shortcomings

- Not faster: +3.7% on the fluid solver (1567.7 vs 1628.2 ms) and -15% on matmul (562.7 vs 488.5 ms) against std::async thread-per-task; the benchmark CMake never applies -O3, so the build is likely unoptimized.
- Enricher: the Red-Portal benchmark is degenerate: fluid_solver.cpp never calls addInflow so all fields stay zero and project exits after one sweep; each of the 2048 row tasks restarts idx at 0 so all write row 0 of _dst (data race) and check_result compares zeros with zeros; ThreadPool is hard-coded to 4 workers on a 4C/8T i7-7700HQ while the Sean Parent pools use hardware_concurrency(); -O3 is never applied; matmul _C is not reset between runners. std::result_of fails with clang 16 C++20 (#109); move-only arguments fail through std::bind (#93); 1M trivial tasks take 5 s vs 0.005 s in a loop (#84); abandoned 2014-09-26.

## Caveats and trade-offs

Benchmark is a small third-party repo (Red-Portal/thread-pool-benchmark, 30 stars, archived 2022-06-10, GPL-3.0 benchmark code) with only two workloads and a single 'example results' run per row; its CMakeLists.txt builds a BUILD_FLAGS string with -std=c++14 -g -O3 but only prints it and never applies it, and no CMAKE_BUILD_TYPE is set, so the times are probably from an unoptimized build. Baseline is std::async(std::launch::async) spawning one thread per task (1024 row tasks for the matrix multiplication), the weakest std::thread usage; ThreadPool (4 workers) wins by 3.7% on the fluid solver and loses by 15% on the matrix multiplication, and every other pool in the table (Sean Parent variants, GCD, TBB) beats it on both, so it is not shown to be faster. The ThreadPool repo has no benchmark or performance number of its own and was last committed on 2014-09-26 (no maintenance). [retier] fluid_solver.cpp never calls addInflow (zero fields), all 2048 row tasks write row 0 (data race), check_result vacuous; -O3 never applied; 4 hard-coded workers vs hardware_concurrency(); abandoned 2014-09-26; 1M trivial tasks 5 s (#84).

Single header (ThreadPool.h), C++11, fixed worker count chosen at construction, one mutex-protected FIFO queue plus condition variable, enqueue returns std::future via packaged_task. No work stealing, priorities, cancellation or resizing; the shared queue lock limits scaling with many tiny tasks.

## Maintenance

Abandoned since 2014-09-26 (28 commits, 8.8k stars, 41 open issues). It is a Zlib-licensed header of about 100 lines that is easy to vendor after swapping std::result_of for std::invoke_result_t. Its only third-party benchmark is broken (unoptimized build, 4 workers against 8 hardware threads, racy all-zero fluid workload), so treat it as a convenient pool, not a fast one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** Third-party benchmark code is public (Red-Portal/thread-pool-benchmark: main.cpp, benchmark_candidates/cpp_threads/cpp_threads.cpp, benchmark_candidates/progschj_ThreadPool/progschj_ThreadPool.cpp) with compiler and CPU model stated, but its CMakeLists.txt never applies the -O3 flags and sets no build type, so the run was probably unoptimized (capped at C); single run, obscure 30-star suite.
- **Retiered** C to D: Lowered C to D: the only numbers come from a degenerate benchmark (fluid solver on all-zero fields with a data race on row 0 and a check that compares zeros with zeros, matmul results never reset, no -O3 applied, pool hard-coded to 4 workers), so nothing valid was measured; directional only, and the library is not faster than std::async per task in any case.
- **Verifier notes:** Numbers match the Red-Portal README exactly (fluid 1567.72 vs 1628.18 ms, matmul 562.66 vs 488.52 ms); baseline really is std::async per task, and ThreadPool is mixed to slower against it, so record shortcomings 'not faster' and 'unoptimized build likely'. Metadata confirmed: Zlib, 8.8k stars, 2.3k forks, 28 commits, last commit 2014-09-26, not archived.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-62 (wave 11); enricher w11 pair-028
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_candidates/cpp_threads/cpp_threads.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_candidates/progschj_ThreadPool/progschj_ThreadPool.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_problems/matrix_multiplication.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_problems/fluid_solver.cpp>
  - <https://github.com/Red-Portal/thread-pool-benchmark>
  - <https://github.com/progschj/ThreadPool>
  - <https://github.com/progschj/ThreadPool/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/progschj/ThreadPool/HEAD/README.md>
  - <https://raw.githubusercontent.com/progschj/ThreadPool/HEAD/ThreadPool.h>
  - <https://raw.githubusercontent.com/progschj/ThreadPool/HEAD/example.cpp>
  - <https://raw.githubusercontent.com/progschj/ThreadPool/HEAD/COPYING>
  - <https://github.com/progschj/ThreadPool>
  - <https://github.com/progschj/ThreadPool/issues>
  - <https://github.com/progschj/ThreadPool/issues/115>
  - <https://github.com/progschj/ThreadPool/issues/93>
  - <https://github.com/progschj/ThreadPool/issues/89>
  - <https://github.com/progschj/ThreadPool/issues/84>
  - <https://github.com/progschj/ThreadPool/issues/109>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/include/pool_bench.hpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_candidates/cpp_threads/cpp_threads.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_candidates/progschj_ThreadPool/progschj_ThreadPool.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_candidates/sean_parent/sean_parent.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_candidates/sean_parent/sean_parent_naive.hpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_candidates/thread_building_blocks/thread_building_blocks.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_candidates/grand_central_dispatch/grand_central_dispatch.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_problems/matrix_multiplication.cpp>
  - <https://raw.githubusercontent.com/Red-Portal/thread-pool-benchmark/HEAD/benchmark_problems/fluid_solver.cpp>
  - https://techpowerup.com/cpu-specs/core-i7-7700hq.c3098 (search-result snippet only: 4 cores, 8 threads)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/progschj/threadpool`) · [data/wave11/enrich/raw/github_com_progschj_threadpool.json](../../../data/wave11/enrich/raw/github_com_progschj_threadpool.json) (enrichment confidence 0.8)

</details>
