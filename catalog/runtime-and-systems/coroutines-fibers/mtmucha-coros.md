# Coros

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟡 stale

> Header-only C++23 coroutine fork-join task library with a work-stealing pool; roughly ties oneTBB, beats OpenMP tasks.

| | |
|---|---|
| **Beats** | Intel oneTBB and OpenMP task runtimes (GCC libgomp, LLVM libomp); libfork is not in the graphs |
| **Claimed result** | Values read from README graphs (derived from page data): Fibonacci(30) x86 at 16 threads Coros \~27 ms vs oneTBB \~25 ms (parity), libomp \~140 ms, libgomp \~3000 ms; Fibonacci ARM at 16 threads Coros \~22 ms vs oneTBB \~27 ms, libomp \~85 ms, libgomp \~5000 ms; matrix multiplication x86 at 16 threads Coros \~818 ms vs oneTBB \~840 ms, libomp \~860 ms, libgomp \~900 ms. |
| **Workload** | Fork-join task parallelism with C++20/23 coroutines: Fibonacci(30) task-spawn overhead and matrix multiplication, 1-16 threads, on unnamed x86 and ARM machines. |
| **Metric** | latency |
| **Adoption** | 334 stars |
| **Last commit** | 2024-09-13 |
| **Links** | [repository](https://github.com/mtmucha/coros) · [benchmark](https://github.com/mtmucha/coros) |

## Verdict

README graphs (read by eye) show fib(30) time vs threads (1-16) and a 1024x1024 recursive int matmul against oneTBB, GCC libgomp and LLVM libomp: at 16 threads x86 fib Coros \~27 ms vs oneTBB \~25 ms, libomp \~140 ms, libgomp \~3000 ms; ARM fib \~22 ms vs \~27 ms oneTBB; matmul \~818 ms vs \~840 ms oneTBB. Benchmark CMake uses -std=c++23 -O3 (-fcoroutines -fopenmp for GCC, libc++ and libomp for Clang); compiler versions and CPU models are not stated, and the committed oneTBB harness pins 4 threads.

## Use it when

- C++23 code (GCC 13+ or Clang 17+) that wants fork-join recursion expressed with co_await instead of TBB lambdas or OpenMP pragmas
- Very fine-grained recursive tasks (fib-style spawn trees) where OpenMP tasks, especially GCC libgomp, are orders of magnitude slower per the README graphs
- Small codebases that want a vendorable, header-only, BSL-1.0 scheduler with exception propagation via std::expected
- Moving work between several thread pools (wait_tasks(tp, ...) resumes the awaiting task on a named pool)

## Skip it when

- If oneTBB is already in use: the README graphs show parity on x86 (Coros \~27 ms vs oneTBB \~25 ms for fib(30) at 16 threads) and only modest wins on ARM
- Latency- or power-sensitive processes: idle workers busy-spin forever (run() loops on noop_coroutine; thread yielding is a TODO), burning 100% CPU on every pool thread
- MSVC builds (not supported) or toolchains without std::expected
- Clang on x86 at high steal rates: open issue #2 reports the seq_cst atomic_thread_fence in Dequeue::steal() compiles to mfence and dominates matmul time
- Long-lived pools with bursty spawning: grown deque buffers are kept in old_buffers_ until the pool is destroyed

## How it is fast

Each worker owns a Chase-Lev work-stealing deque (circular power-of-two buffer, grown 4x on overflow, after Le et al.'s correct weak-memory-model deque) storing coroutine handles; idle workers pick a random victim and scan all queues, then fall back to a shared moodycamel::ConcurrentQueue for tasks submitted from outside. Stackless coroutines make a spawn a heap-allocated coroutine frame plus a deque push, and co_await on a child uses symmetric transfer so nested waits do not grow the stack. top_ and bottom_ are padded with hardware_destructive_interference_size to avoid false sharing.

## Compared with alternatives

The other coroutines-fibers entries (minicoro, libaco, libco-style switchers, Boost.Cobalt) are context-switch or async I/O primitives; pick Coros when you need a parallel fork-join scheduler on stackless C++ coroutines, and Marl when you need stackful fibers that may block.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (vendors moodycamel concurrentqueue.h in include/) |
| **Minimum toolchain** | C++23, GCC 13+ (with -fcoroutines) or Clang 17+ (libc++); MSVC not supported |
| **Platforms** | x86-64 and ARM per the README graphs; any platform with C++23 threads and atomics otherwise not documented |
| **Thread safety** | ThreadPool is shared by its workers; tasks from outside go through a lock-free MPMC queue; the pool must outlive its tasks. CI runs ASan and TSan builds. |
| **Drop-in for the baseline** | no |

## Gotchas

- Exceptions thrown inside enqueue_tasks tasks are rethrown immediately, since nothing awaits them; Task&lt;void&gt; has no value()/operator\*
- Lambda coroutines with captures are unsafe once the lambda dies; pass state through coroutine parameters
- Published harness flaw: benchmarks/tbb/fib_tbb.h and mat_tbb.h hard-code tbb::task_arena arena(4) and ignore g_thread_num, so the committed oneTBB benchmark always runs 4 threads; the oneTBB thread sweep in the README graphs cannot be reproduced from the repo as committed
- Each harness writes 50 millisecond-resolution runs per thread count to text files; how the plotted value was derived (mean, median) is not documented, and the TBB matmul uses std::atomic&lt;int&gt; inputs where Coros uses plain int

## Known shortcomings

- Harness flaw: benchmarks/tbb/fib_tbb.h and mat_tbb.h hard-code tbb::task_arena arena(4) and ignore g_thread_num, so the committed oneTBB bench always runs 4 threads and the README oneTBB thread sweep is not reproducible from the repo. Idle workers busy-spin at 100% CPU (yield TODO); issue 2: the seq_cst fence in Dequeue::steal() becomes an mfence on Clang x86; MSVC unsupported.

## Caveats and trade-offs

Results are graphs only, read by eye; compiler, flags and CPU models are not stated. Roughly ties oneTBB on x86 (slightly slower at some thread counts) and beats it modestly on ARM; large wins only over OpenMP tasks, especially libgomp. Requires C++23 std::expected (GCC 13+, Clang 17+). Task-parallelism library, only loosely coroutines-fibers. Stale since 2024-09-13.

Needs C++23 (std::expected); stackless coroutines, so not a Boost.Context replacement; own ThreadPool.

## Maintenance

Stale since 2024-09-13 with one open performance issue (#2); BSL-1.0 and header-only, so easy to vendor, but treat it as a well-built student-scale scheduler rather than a TBB replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgrade from D: the README graphs (images/graph_w1.png, graph_w2.png, coros_graphs_13.png, coros_graphs_14.png) are readable plots of time in ms vs thread count against oneTBB, libgomp and libomp, and benchmark code is public in benchmarks/ (coros_fib.h, openmp_fib.h, tbb/, main.cpp); compiler, flags and CPU model are not stated, so C.
- **Verifier notes:** Read the four PNGs from raw.githubusercontent.com. The record's claim that libfork is compared was not supported; the comparisons are oneTBB, libgomp and libomp. Stars 334, BSL-1.0 confirmed, last commit 2024-09-13.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/mtmucha/coros>
  - <https://github.com/mtmucha/coros/commits>
  - <https://github.com/mtmucha/coros/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/README.md>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/images/graph_w1.png>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/images/graph_w2.png>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/images/coros_graphs_13.png>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/README.md>
  - <https://github.com/mtmucha/coros/tree/main/include>
  - <https://github.com/mtmucha/coros/tree/main/benchmarks>
  - <https://github.com/mtmucha/coros/tree/main/benchmarks/tbb>
  - <https://github.com/mtmucha/coros/issues?q=is%3Aissue>
  - <https://github.com/mtmucha/coros/issues/2>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/include/thread_pool.h>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/include/deque.h>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/include/task.h>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/benchmarks/main.cpp>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/benchmarks/coros_fib.h>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/benchmarks/coros_mat.h>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/benchmarks/openmp_fib.h>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/benchmarks/openmp_mat.h>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/benchmarks/tbb/main.cpp>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/benchmarks/tbb/fib_tbb.h>
  - <https://raw.githubusercontent.com/mtmucha/coros/HEAD/benchmarks/tbb/mat_tbb.h>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/mtmucha/coros`) · [data/wave11/enrich/raw/github_com_mtmucha_coros.json](../../../data/wave11/enrich/raw/github_com_mtmucha_coros.json) (enrichment confidence 0.7)

</details>
