# Scheduling (dpuyda)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT OR Apache-2.0` · 🟡 stale

> Header-only C++20 work-stealing thread pool and task-graph runner, under 600 lines, benchmarked faster than Taskflow on fine-grained tasks.

| | |
|---|---|
| **Beats** | Taskflow |
| **Claimed result** | README Google Benchmark wall times: Fibonacci n=35 1,661 ms vs Taskflow 15,058 ms (\~9x, derived from page data); linear chain of 33,554,432 tasks 4,158 ms vs 9,951 ms (\~2.4x, derived from page data); matrix multiplication is slower than Taskflow at every size (2048: 4,134 ms vs 3,970 ms; 256: 8.20 ms vs 4.13 ms). |
| **Workload** | Google Benchmark: recursive Fibonacci n=35, linear chain of 33,554,432 tasks, 2048x2048 matrix multiplication task graph. |
| **Metric** | throughput |
| **Hardware** | Stated as 'Intel(R) Xeon(R) CPU i7-1165G7 @ 2.80GHz with 32 CPUs', Debian GNU/Linux 12 (that CPU name and count are inconsistent: the i7-1165G7 has 8 threads) |
| **Adoption** | 67 stars; arXiv 2407.15805 paper |
| **Last commit** | 2024-11-29 |
| **Links** | [repository](https://github.com/dpuyda/scheduling) · [benchmark](https://github.com/dpuyda/scheduling) |

## Verdict

The author's Google Benchmark run (Scheduling commit ae8a367 vs Taskflow, built from benchmarks/taskflow.cmake at v3.7.0; compiler and flags not stated; hardware reported inconsistently as an 'Intel Xeon i7-1165G7' with 32 CPUs on Debian 12) shows wall time of 1,661 ms vs 15,058 ms for recursive Fibonacci(35) and 4,158 ms vs 9,951 ms for a 33,554,432-task linear chain, but Scheduling was slower on the matrix-multiplication task graph at every size; large sizes were single-iteration runs.

## Use it when

- Many tiny fire-and-forget tasks or recursive fork-join code on a single pool, where per-task overhead dominates (recursive Fibonacci was about 9x faster than Taskflow 3.7 subflows at n=35 in the author's run).
- Long dependency chains or sparse DAGs of small tasks, where inline execution of the ready successor avoids queue traffic (linear chain of 33.5M tasks: 4.16 s vs 9.95 s).
- Projects that want a tiny, readable, vendorable scheduler (one header, no dependencies) and are on C++20.
- Statically linked binaries on Linux, macOS or Windows (CI covers GCC 13, Clang, MSVC, with TSAN/ASAN/UBSAN jobs).

## Skip it when

- Data-parallel loops or coarse task graphs: the matrix-multiplication task graph was slower than Taskflow at every size (2048: 4,134 ms vs 3,970 ms; 256: 8.20 ms vs 4.13 ms), and there are no built-in parallel algorithms.
- Shared libraries or plugins: the README states dynamic linking is unsupported because of the static thread_local queue index.
- Several threads that are not pool workers submitting concurrently, or more than one ThreadPool in a process: all non-worker threads push into the same owner-only Chase-Lev deque (index 0), and the thread_local index is shared by every ThreadPool instance, so a worker of one pool submitting to another pool pushes into that pool's queue i (racing its owner, or out of range if the second pool is smaller). Neither case is documented as safe.
- Power- or CPU-sensitive deployments: idle workers spin through 100 steal attempts before blocking, keep spinning while any task is outstanding, and Wait(predicate) is a pure busy loop.
- Projects needing exceptions, priorities, futures or long-term maintenance: an exception escaping a task terminates the program (no handling in Execute), there are no releases, and the last commit is from November 2024.

## How it is fast

One Chase-Lev work-stealing deque per worker (the lock-free deque copied from Google Filament, made growable with Taskflow's Array buffer) plus one extra queue for non-worker threads; the queue is chosen through a thread_local index instead of a thread-id map. When a task finishes, the first successor whose predecessor count hits zero runs inline on the same worker (continuation passing), so a linear chain never touches a queue. The recursive Fibonacci pattern uses Wait(predicate), which helps by running queued tasks instead of creating Taskflow-style subflow graphs, which is where most of the 9x gap comes from.

## Compared with alternatives

Pick it over nexus or ThunderBolt-HT when you need explicit dependency graphs with cancellation in one small, dependency-free C++20 header; pick Fork Union for parallel-for dispatch, and libfork, citor or Staccato when fork-join performance is the main goal and you want evidence measured against more than Taskflow.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Google Benchmark, Taskflow v3.7.0 and GoogleTest are fetched only for the benchmarks/tests) |
| **Minimum toolchain** | C++20 (concepts, std::atomic wait/notify); CMake 3.21 for the bundled CMakeLists |
| **Platforms** | any platform with C++20 threads and atomic wait; CI on Ubuntu (GCC 13, Clang), macOS, Windows MSVC |
| **Thread safety** | Submit from worker threads is the intended path; submitting the same graph from several threads at once is forbidden by the README; concurrent Submit from multiple non-worker threads is not documented and pushes into one single-owner deque |
| **Drop-in for the baseline** | no |

## Gotchas

- Task objects in a graph must not move or be destroyed until the pool finishes them (reserve the vector first); README issue #33 reported its own graph example printing 0 for every result (closed Oct 2024) and #35 a dangling reference in an example.
- Recursive Wait(predicate), as in the Fibonacci example, grows the stack with recursion depth; the README warns it can overflow.
- Deque indices top_/bottom_ are std::atomic&lt;int&gt; while Array::Get/Put take size_t; top_ only ever increases, so a queue that sees more than about 2^31 steals in one pool lifetime overflows a signed int. Old buffers after a resize are kept until the pool is destroyed.
- Benchmark harness asymmetries: Google Benchmark's CPU-time column counts only the main thread, so the CPU-time charts (e.g. matmul 11.9 ms vs 29.5 ms) say nothing about worker CPU use; the Taskflow matmul loop allocates the three n x n matrices inside the timed loop while the Scheduling loop allocates them once outside, which favours Scheduling yet it still loses; scripts/build.sh sets no CMAKE_BUILD_TYPE, and the README does not state the build type or flags used.

## Known shortcomings

- Harness flaws: the Taskflow matmul allocates 3 matrices inside the timed loop while Scheduling allocates outside (favours Scheduling, which still loses); the CPU-time column counts the main thread only; scripts/build.sh sets no CMAKE_BUILD_TYPE so flags are unknown. Undocumented races: all non-worker threads push into one owner-only Chase-Lev deque (index 0); thread_local index_ is shared by every ThreadPool; int top_/bottom_ overflow after 2^31 steals.

## Caveats and trade-offs

First-party numbers; compiler and flags not stated; single-iteration runs for the large sizes. Matrix multiplication is slower than Taskflow at all sizes. The hardware string is self-contradictory (i7-1165G7 reported as Xeon with 32 CPUs). The arXiv preprint (2407.15805, blocked here) is not peer-reviewed. Baseline is Taskflow, not oneTBB. The large Fibonacci gap may reflect Taskflow's subflow overhead for recursive tasks.

Header-only C++20, Chase-Lev work-stealing, under 1000 lines, task graphs.

## Maintenance

Stale (last commit November 2024, 37 commits, no releases, issue #38 about tasks_count_ accounting unanswered since November 2025), but MIT-licensed with Apache-2.0 Filament code and small enough to vendor and audit.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** First-party Google Benchmark results in the README against Taskflow (Taskflow's own fibonacci, linear_chain and matrix_multiplication examples at commit 9616467). Hardware is stated but compiler and flags are not, and the arXiv 2407.15805 preprint is by the same author and not peer-reviewed, so the record is C, not B.
- **Verifier notes:** MIT OR Apache-2.0, 67 stars and last commit 2024-11-29 were confirmed from the repo pages.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/dpuyda/scheduling>
  - <https://github.com/dpuyda/scheduling/commits/main>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/dpuyda/scheduling>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/README.md>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/include/scheduling/scheduling.hpp>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/benchmarks/scheduling.cpp>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/benchmarks/taskflow.cpp>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/benchmarks/benchmark.cmake>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/benchmarks/taskflow.cmake>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/.github/workflows/build.yml>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/dpuyda/scheduling/HEAD/tests/CMakeLists.txt>
  - <https://github.com/dpuyda/scheduling/issues?q=is%3Aissue>
  - <https://github.com/dpuyda/scheduling/issues/38>
  - <https://github.com/dpuyda/scheduling/issues/33>
  - <https://github.com/dpuyda/scheduling/issues/1>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/dpuyda/scheduling`) · [data/wave11/enrich/raw/github_com_dpuyda_scheduling.json](../../../data/wave11/enrich/raw/github_com_dpuyda_scheduling.json) (enrichment confidence 0.75)

</details>
