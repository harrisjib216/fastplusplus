# Staccato

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++11 work-stealing scheduler storing task objects inside its deques; lower spawn overhead than TBB 4.3 and Cilk Plus.

| | |
|---|---|
| **Beats** | Intel TBB 4.3 and Intel Cilk Plus 7.3 |
| **Claimed result** | Numbers only in README charts (docs/final.dat-\*.png, execution time in us on a natural-log axis): at 56 threads fib(42) Staccato \~14.03 vs Cilk Plus \~14.48 vs TBB \~14.92 log-us, about 1.6x faster than Cilk and 2.4x faster than TBB; dfs 9^9 Staccato \~13.38 vs Cilk \~14.3 vs TBB \~14.6, about 2.5x and 3.4x (derived from page data, chart-read, approximate). Staccato is faster at every thread count on fib/dfs; README says memory-bound matmul/blkmul are almost unaffected. |
| **Workload** | fib(42), dfs 9^9 tree, matmul 3500x350, blkmul 4096x4096 on 56 threads. |
| **Metric** | throughput |
| **Hardware** | 2x Intel Xeon E5 v4 (14 cores each, 56 threads) |
| **Compiler and flags** | g++ 7.2.1 -O3, Linux 4.13 Fedora 27 |
| **Adoption** | 37 stars |
| **Last commit** | 2018-06-13 |
| **Links** | [repository](https://github.com/rkuchumov/staccato) · [benchmark](https://github.com/rkuchumov/staccato) |

## Verdict

On two Xeon E5 v4 sockets (14 cores each, 56 threads), g++ 7.2.1 -O3, Linux 4.13, the README charts show fib(42) at 56 threads about 1.6x faster than Intel Cilk Plus 7.3 and 2.4x faster than TBB 4.3, and dfs 9^9 about 2.5x and 3.4x faster (ratios read off log-scale PNG charts by the verifier, approximate), with matmul and blkmul nearly unchanged. The checked-in benchmarks/run.sh is left in a debug state (2 runs at 3-4 threads, only staccato fib enabled), so the published charts used settings that the script no longer runs by default.

## Use it when

- Recursive divide-and-conquer with tiny tasks (fib, tree search, recursive sums) where scheduler overhead dominates, which is where its fib(42) and dfs 9^9 charts show the gap over TBB and Cilk Plus.
- Task graphs whose maximum fan-out per task is known at compile or design time (for example 2 for binary recursion).
- As a small, readable reference implementation of a task-object-storing work-stealing deque to study or vendor.
- Projects stuck on C++11 that want a dependency-free header drop.

## Skip it when

- Memory-bound kernels (matmul, block matmul): the README says the gain there is negligible.
- Irregular task graphs with unbounded or data-dependent fan-out: you must fix the maximum subtasks per task up front.
- Production code needing parallel algorithms, futures, cancellation, exceptions across tasks or mixed task types: only spawn/wait on one type T exists; use oneTBB, Taskflow or libfork instead.
- Anything needing maintenance: last commit 2018-06-13; open issues include the matmul benchmark consuming 128 GB+ of memory (#4) and benchmark crashes on atoi (#3), both unanswered.
- Latency-sensitive or shared machines: idle workers spin in a steal loop calling std::this_thread::yield() rather than sleeping.

## How it is fast

Instead of a Chase-Lev deque of task pointers, each worker keeps a chain of fixed-size task_deque arrays (one per task-graph level) that hold the task objects themselves, so spawning a task never calls the heap allocator and finished slots are reused in LIFO order. Per-worker memory comes from a bump-style lifo_allocator with no thread safety or fragmentation handling, keeping tasks contiguous; the README shows fewer LLC misses than TBB and Cilk Plus. The deque uses relaxed atomics with explicit fences (top/bottom/nstolen counters) so it is valid on weak memory models.

## Compared with alternatives

Pick it over Nowa or Heartbeat Scheduling only when you want a tiny dependency-free C++11 header to study or vendor for fixed-fan-out recursion; for maintained, general-purpose work stealing citor, Fork Union or Taskflow-class libraries are safer, and Weave (Nim) reports similar overhead wins over TBB with more benchmarks.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (pthreads via std::thread) |
| **Minimum toolchain** | C++11; tested with g++ 7.2.1 |
| **Platforms** | any platform with C++11 threads and atomics; benchmarked only on x86-64 Linux |
| **Thread safety** | Scheduler is driven from one master thread (root()/spawn()/wait()); spawn/wait inside execute() are per-worker; not documented beyond that |
| **Drop-in for the baseline** | no |

## Gotchas

- Not truly header-only for multi-file builds: include/lifo_allocator.hpp defines non-template, non-inline member functions (lifo_allocator::page::set_next, page::alloc, lifo_allocator::alloc, inc_tail and others) at namespace scope, so including the scheduler from two translation units gives duplicate-symbol link errors unless you patch in 'inline'.
- Tasks must be constructed with placement new over child()/root() memory; allocating them any other way breaks the scheduler's memory model.
- The scheduler(degree, nthreads, height) constructor rounds degree up to a power of two and preallocates per-level deques; exceeding the declared fan-out is not checked in release builds.
- The TBB comparison uses blocking-style TBB tasks (wait_for_all) without continuation passing or scheduler bypass; issue #1 notes TBB's gap would shrink with those.

## Known shortcomings

- Header bug: lifo_allocator.hpp has non-inline out-of-class definitions, so including it in two or more translation units gives duplicate-symbol link errors. The TBB fib baseline is blocking style with no continuation passing (issue 1), so the TBB gap is likely overstated. benchmarks/run.sh is left in a debug configuration (2 runs, 3-4 threads). Open issues 3 (atoi crash) and 4 (matmul needs 128 GB+) were never answered.

## Caveats and trade-offs

Old baselines (TBB 4.3, Intel Cilk Plus 7.3, both superseded/deprecated). Numbers are read from PNG charts, no text table; ratios assume the log axis is natural log (consistent with fib(42) sequential \~1.4 s). Requires declaring max subtasks per task up front. CPU model not stated beyond Xeon E5 v4. Last commit 2018-06-13.

Header-only C++11, spawn/wait API, supports weak memory models.

## Maintenance

Abandoned since 2018 (37 stars, four open issues with no replies) but MIT-licensed and only about 950 lines of headers, so it is easy to vendor after adding 'inline' to the lifo_allocator definitions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Benchmark code for staccato, tbb, cilk, openmp and sequential is public in benchmarks/ (run.sh), with g++ 7.2.1 -O3 stated, but the CPU is given only as 'two Intel Xeon E5 v4, 14 cores each' without a model number, so not A; first-party only.
- **Verifier notes:** Charts were readable via raw.githubusercontent.com; approximate ratios added and marked derived. benchmarks/ also has an openmp variant not shown in the charts.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `caveats`
- **Shortcomings recorded by:** first-party charts
- **Pages the verifier opened:**
  - <https://github.com/rkuchumov/staccato>
  - <https://github.com/rkuchumov/staccato/commits>
  - <https://github.com/rkuchumov/staccato/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/README.md>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/master/docs/final.dat-fib.png>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/master/docs/final.dat-dfs.png>
- **Sources the enricher read:**
  - <https://github.com/rkuchumov/staccato>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/README.md>
  - <https://github.com/rkuchumov/staccato/tree/master/include>
  - <https://github.com/rkuchumov/staccato/tree/master/benchmarks/staccato>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/include/scheduler.hpp>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/include/task.hpp>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/include/task_deque.hpp>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/include/worker.hpp>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/include/lifo_allocator.hpp>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/benchmarks/run.sh>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/benchmarks/staccato/fib/main.cpp>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/benchmarks/staccato/fib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/benchmarks/tbb/fib/main.cpp>
  - <https://raw.githubusercontent.com/rkuchumov/staccato/HEAD/benchmarks/cilk/fib/main.cpp>
  - <https://github.com/rkuchumov/staccato/issues?q=is%3Aissue>
  - <https://github.com/rkuchumov/staccato/issues/1>
  - <https://github.com/rkuchumov/staccato/issues/4>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/rkuchumov/staccato`) · [data/wave11/enrich/raw/github_com_rkuchumov_staccato.json](../../../data/wave11/enrich/raw/github_com_rkuchumov_staccato.json) (enrichment confidence 0.75)

</details>
