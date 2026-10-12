# concurrencpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> C++20 coroutine task/executor framework whose thread pool beats libcoro on fork-join, but trails TBB by about 90x.

| | |
|---|---|
| **Beats** | libcoro thread_pool (jbaldwin/libcoro), with HPX as a second weaker baseline |
| **Claimed result** | Faster than libcoro on every fork-join benchmark: skynet 12514888 us vs 119686148 us (about 9.6x, derived from page data), nqueens 8000700 us vs 33347402 us (about 4.2x), fib(39) 20663744 us vs 238019884 us (about 11.5x), matmul(2048) 57383 us vs 374412 us (about 6.5x); peak RSS on skynet 11.38 MB vs libcoro 14.66 GB (derived from page data, about 1300x less). Against HPX only matmul is faster (57383 us vs 59066 us, about 1.03x, within noise); HPX wins skynet, nqueens and fib(39). Memory (separate cpp_tasks_bench repo, i7-8550U under WSL): 605972 kb vs Asio 853144 kb for 1M tasks (about 1.4x less, derived from page data). |
| **Workload** | tzcnt/runtime-benchmarks recursive fork-join suite on 64 threads: skynet (100M tasks), nqueens, fib(39) and matmul(2048), measuring total wall time per runtime (peak RSS also reported). |
| **Metric** | throughput |
| **Hardware** | EPYC 7742 64-core, 64 worker threads (no SMT), Debian 13 Server, CPU boost enabled with schedutil governor |
| **Compiler and flags** | Clang 21.1.7 Release (-O3 -march=native), linked against libtcmalloc_minimal.so.4 |
| **Adoption** | 2.8k stars |
| **Last commit** | 2023-07-15 |
| **Links** | [repository](https://github.com/David-Haim/concurrencpp) · [benchmark](https://github.com/tzcnt/runtime-benchmarks) |

## Verdict

In tzcnt/runtime-benchmarks (third-party suite by the TooManyCooks author), concurrencpp v.0.1.7 built with Clang 21.1.7 -O3 -march=native and tcmalloc on a 64-core EPYC 7742 with 64 threads finished skynet in 12.5 s, nqueens 8.0 s, fib(39) 20.7 s and matmul(2048) 57 ms, beating libcoro on all four (about 4-12x) and using about 11 MB peak RSS where libcoro used 5-16 GB. It beat HPX only on matmul (57.4 vs 59.1 ms) and was about 116-502x slower than the fastest runtime on the three fine-grained benchmarks (derived from page data).

## Use it when

- Applications that want one coroutine-based toolkit for CPU pools, blocking-I/O pools, timers, async locks and condition variables rather than a pure fork-join scheduler.
- Coarse-grained tasks (milliseconds each) where per-task overhead of tens of microseconds is irrelevant; matmul(2048) with a 32x32 serial base case ran in 57 ms, about 1.3x the fastest runtime (libfork 44 ms).
- Replacing a libcoro thread_pool in fine-grained recursive code where libcoro's memory blow-up (5-16 GB peak RSS on skynet, nqueens, fib(39)) is the problem.
- Code bases already on C++20 with MSVC 16.8.2+, GCC 13+ or Clang 14+ that can consume a CMake/vcpkg/Conan static library.

## Skip it when

- Fine-grained fork-join (fib, skynet, nqueens style): in the same suite it is about 88x slower than TBB on skynet and about 96x on fib(39), with a mean ratio to best of 258x; citor, libfork, TooManyCooks, TBB, taskflow or cppcoro are the right tools.
- Machines with 48+ cores: the maintainer acknowledged in issue #174 (April 2025) that the work-sharing algorithm does not scale well there.
- Projects needing an actively maintained dependency: master has had no commit since 'Version 0.1.7' on 2023-07-15, and open issues report build failures on Clang 17/18 (#169), libc++ (#177) and MSVC 19.50 (#178) without maintainer replies.
- Workloads that need FIFO ordering: local (worker-thread) submissions go to a private LIFO queue ahead of foreign submissions (issue #151 shows a later local task running before an earlier foreign one).

## How it is fast

The thread pool is a work-sharing (donation) design, not work stealing: each worker has an unsynchronized private std::deque it pops LIFO and a mutex-protected public deque; before running each task a busy worker scans per-worker padded idle flags and pushes a share of its oldest private tasks to idle workers. Idle workers block on a binary semaphore and exit after max_worker_idle_time, with threads re-created lazily on the next enqueue. Its advantage over libcoro in the suite is mainly memory and per-task scheduling cost (skynet peak RSS 11.38 MB vs libcoro 14.66 GB), not raw scheduler speed; every task still allocates a coroutine frame and result state, and iterator when_all returns a heap std::vector.

## Compared with alternatives

Pick it over citor, Fork Union, dpuyda/scheduling or nexus only when you need its broader coroutine ecosystem (timers, async locks and condition variables, generators, separate background pool) and your tasks are coarse; for fork-join throughput citor and the other suite leaders are about 100-500x faster on fine-grained benchmarks.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none beyond the platform threads library (and librt on Linux when present); CMake 3.16+ |
| **Minimum toolchain** | C++20; MSVC 16.8.2+, GCC 13+, Clang 14+ (Clang 11-13 only with libc++) |
| **Platforms** | Linux, macOS, Windows 10+ |
| **Thread safety** | Executors' submit/post/enqueue are thread-safe; result and lazy_result are move-only single-consumer objects; shared_result allows thread-safe multi-consumer access but not to the value itself. |
| **Drop-in for the baseline** | no |

## Gotchas

- The suite's wins come from v.0.1.7 run in the documented parallel-coroutine style; in issue #174 the maintainer reports an unreleased fork-join rework cutting fib to 1/5-1/6 and skynet to about 1/3 of that time, but it is not on master (the branches page lists only master) or in any release.
- when_all and when_any take the resume executor only as std::shared_ptr, so recursive fork-join code copies a shared_ptr per spawned task (atomic refcount traffic on one control block at 64 threads); parallel coroutines themselves also accept type\* or type&.
- Harness notes for the cited numbers: each result is one run with iter_count = 1 (no repetitions), so the 1.03x matmul edge over HPX is within noise; the fib benchmark removes the README's serial cutoff and spawns every node including leaves, while the suite's libcoro fib returns leaves inline, so concurrencpp schedules about twice as many tasks there (this handicaps concurrencpp and does not inflate its win).
- Waiting with result::get or wait inside pool tasks blocks the worker thread; the README restricts blocking waits to root-level code or blocking/thread executors.

## Known shortcomings

- tzcnt/runtime-benchmarks numbers match (v0.1.7 pinned, Clang 21.1.7 -O3, EPYC 7742) but concurrencpp beats only libcoro, the slowest runtime in the suite, and is about 88-96x slower than TBB. Abandoned (last commit 2023-07-15).
- Enricher: the pool shares work by donation, not stealing; about 88-96x slower than TBB and 116-502x slower than the fastest runtime on skynet, nqueens and fib; the tzcnt suite runs one iteration per cell (iter_count=1), so the 1.03x matmul edge over HPX is noise; its fib drops the README's serial cutoff and schedules every leaf while libcoro's fib returns leaves inline, which handicaps concurrencpp although the libcoro win still stands. Issue #174: maintainer admits poor scaling at 48+ threads, unreleased fork-join rework not on master; open build breaks with Clang 17/18 (#169), libc++ (#177), MSVC 19.50 (#178); when_all needs a shared_ptr executor.

## Caveats and trade-offs

The project makes no numeric performance claim; the README only calls the design fast and clean. The numbers come from a third-party suite written by the author of a competing runtime (TooManyCooks). In that same suite concurrencpp is far slower than the fast runtimes: mean ratio to best 258.19x (TBB 3.25x, taskflow 3.34x, cppcoro 3.67x, libfork 1.18x), for example skynet 12514888 us vs TBB 142887 us (about 88x slower, derived) and fib(39) 20663744 us vs TBB 215592 us (about 96x slower). The win over libcoro is against the slowest runtime in the table (mean ratio 2513.96x). The suite pins concurrencpp v.0.1.7 (cpp/concurrencpp/CMakeLists.txt) and libcoro at commit 44d12235a218a93cf6ce462f67c06a1287901c54; its fib benchmark is the concurrencpp README example with the serial cutoff removed. Last commit is 'Version 0.1.7' dated 2023-07-15, over three years old. Memory results in cpp_tasks_bench lose to tokio (605972 kb vs 214136 kb for 1M tasks) and that repo states no compiler or flags beyond a default Release build.

C++20 coroutine task, executor, timer and result-object framework (thread pool, worker threads, manual and inline executors); full-featured API rather than a minimal work-stealing scheduler.

## Maintenance

Effectively abandoned since v.0.1.7 (2023-07-15) with open build-breakage issues on current Clang and MSVC; MIT-licensed, packaged in vcpkg and Conan, and usable for coarse-grained async work, but not a fast fork-join scheduler.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** tzcnt/runtime-benchmarks is a public third-party suite (build_and_bench_all.py, cpp/concurrencpp/{fib,skynet,nqueens,matmul}.cpp pinned to concurrencpp v.0.1.7, cpp/libcoro pinned to commit 44d12235) whose README states Clang 21.1.7 Release -O3 -march=native, tcmalloc and an EPYC 7742 64-core machine; every libcoro and HPX number in the record matches its summary table. Same suite and tier as the already verified citor entry.
- **Verifier notes:** All suite numbers match the README summary tables; the record's claim that the version is unstated was wrong (v.0.1.7 is pinned in the suite's CMakeLists). Shortcomings: wins only against libcoro (slowest in the suite) and marginally HPX on matmul; about 88-96x slower than TBB on skynet and fib; abandoned (last commit 2023-07-15); third-party suite author maintains a competing runtime. Metadata: MIT, 2.8k stars, master branch, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-56 (wave 11); enricher w11 pair-020
- **Pages the verifier opened:**
  - <https://github.com/tzcnt/runtime-benchmarks>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/build_and_bench_all.py>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/fib.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/libcoro/CMakeLists.txt>
  - <https://github.com/David-Haim/concurrencpp>
  - <https://github.com/David-Haim/concurrencpp/commits>
  - <https://raw.githubusercontent.com/David-Haim/concurrencpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/David-Haim/concurrencpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/David-Haim/concurrencpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/David-Haim/concurrencpp/HEAD/source/executors/thread_pool_executor.cpp>
  - <https://raw.githubusercontent.com/David-Haim/concurrencpp/HEAD/include/concurrencpp/executors/thread_pool_executor.h>
  - <https://github.com/David-Haim/concurrencpp/commits>
  - <https://github.com/David-Haim/concurrencpp/branches>
  - <https://github.com/David-Haim/concurrencpp/issues>
  - <https://github.com/David-Haim/concurrencpp/issues/174>
  - <https://github.com/David-Haim/concurrencpp/issues/169>
  - <https://github.com/David-Haim/concurrencpp/issues/177>
  - <https://github.com/David-Haim/concurrencpp/issues/151>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/build_and_bench_all.py>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/build_all.sh>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/CMakePresets.json>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/fib.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/skynet.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/nqueens.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/matmul.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/libcoro/fib.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/tbb/fib.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/david-haim/concurrencpp`) · [data/wave11/enrich/raw/github_com_david_haim_concurrencpp.json](../../../data/wave11/enrich/raw/github_com_david_haim_concurrencpp.json) (enrichment confidence 0.8)

</details>
