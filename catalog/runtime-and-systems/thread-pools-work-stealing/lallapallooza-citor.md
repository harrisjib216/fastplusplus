# citor

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 thread pool with Chase-Lev fork-join and sub-microsecond parallelFor; tops oneTBB and Taskflow on recursive fork-join.

| | |
|---|---|
| **Beats** | oneTBB, Taskflow, OpenMP, dispenso, libfork, TooManyCooks |
| **Claimed result** | README: on single-CCD Zen 5 'citor wins the vast majority of contested bench cells'; runtime-benchmarks 64-core EPYC 7742: mean ratio to best 1.06x vs libfork 1.18x, TooManyCooks 1.32x, tbb 3.25x, taskflow 3.34x; skynet 24932 us vs tbb 142887 us, taskflow 185019 us; fib(39) 49966 us vs tbb 215592 us, taskflow 156590 us |
| **Workload** | Header-only C++20 pool with Chase-Lev forkJoin and parallelFor/Reduce/Scan; bundled parallel_bench covers dispatch latency, fan-out, reduce, scan, forkJoin vs ten peer pools; also in tzcnt/runtime-benchmarks recursive fork-join suite. |
| **Metric** | throughput |
| **Hardware** | runtime-benchmarks: EPYC 7742 64 cores no SMT, Debian 13; own bench: Zen 5 9950X3D single CCD pinned, governor=performance, boost off; also AWS c7a.metal-48xl and c7i.metal-24xl |
| **Compiler and flags** | runtime-benchmarks: Clang 21.1.7 Release -O3 -march=native, tcmalloc; own CI GCC 14 / Clang 19, C++20 |
| **Adoption** | 54 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/Lallapallooza/citor) · [benchmark](https://github.com/tzcnt/runtime-benchmarks) |

## Verdict

In tzcnt/runtime-benchmarks (Clang 21.1.7 -O3 -march=native, tcmalloc, EPYC 7742 with 64 threads and no SMT, boost on, schedutil), citor's mean ratio to the best runtime was 1.06x vs libfork 1.18x, TooManyCooks 1.32x, tbb 3.25x and taskflow 3.34x; skynet took 24932 us vs tbb 142887 us, and fib(39) took 49966 us vs tbb 215592 us and taskflow 156590 us. The suite's citor adapter is a straight port of the libfork fib/skynet code and pins citor v0.4.5 by default, while the current release is 0.6.2; citor's own Zen 5 sweep is published only as charts.

## Use it when

- Recursive fork-join (fib, skynet, cilksort, Strassen, BVH builds) on Linux x86-64, where it had the best mean ratio (1.06x to best) in tzcnt/runtime-benchmarks on a 64-core EPYC 7742.
- Latency-sensitive loops with many short parallel regions, where sub-microsecond empty fan-out and runPlex's spin rendezvous between phases cut per-dispatch overhead.
- Reductions that must be bit-identical across worker counts (FixedBlockOrder or KahanCompensated determinism).
- Single-CCD AMD Zen 4/Zen 5 desktops and workstations with workers pinned inside one shared L3, the stated design target.
- Projects that want a header-only dependency (single_include/citor.hpp, pthread only) instead of linking oneTBB or an OpenMP runtime.

## Skip it when

- Barrier-bound stencils on multi-CCD AMD or Intel mesh servers: the README says these lose to OpenMP because the producer's done-epoch scan is linear in participant count.
- Heavy-tailed reductions: parallelReduce is statically partitioned with no stealing after local completion, so oneTBB's auto_partitioner wins.
- Memory-tight runs: peak RSS in runtime-benchmarks was 44.5 MB on fib(39) vs 11.69 MB for tbb and 51.01 MB vs 10.51 MB for libfork on nqueens.
- nqueens- or matmul-like fork-join on many cores, where libfork and TooManyCooks were faster (nqueens 80765 us vs 69010 us; matmul(2048) 48069 us vs 44140 us).
- I/O-bound or blocking task bodies, async futures, or non-x86 targets: it is a CPU-bound synchronous engine and only Linux and Windows x86-64 are validated.

## How it is fast

forkJoin uses per-worker Chase-Lev work-stealing deques (Le et al. 2013 memory orderings) in the Cilk-5 spawn-parent shape: children go on the calling worker's own deque, the last child runs inline, and the join is a per-frame pendingTasks counter, with steals biased to same-CCD victims. Fan-out dispatch puts the job descriptor on the producer's stack with no hot-path allocation, joins through per-slot done-epoch barriers, parks workers with raw futexes, and pins one worker per physical core using a sysfs topology probe. Small calls fall back to running inline on the caller with no wake-up.

## Compared with alternatives

Pick citor over Fork Union when you need recursive work stealing, deterministic reductions or scans in addition to fast parallel-for dispatch; pick it over Taskflow or Nowa-style runtimes when fork-join throughput matters, since it beat Taskflow by 3-7x on skynet and fib(39) in an outside suite.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond pthread (Threads::Threads); MSVC needs Synchronization.lib |
| **Minimum toolchain** | C++20; CI uses GCC 14, Clang 19 (Clang 18 for sanitizer jobs), MSVC 2022 |
| **Platforms** | Linux x86-64 (latency contract validated), Windows x86-64 (builds and tests, latency not validated); non-x86 compiles with Deadline disabled |
| **Thread safety** | Concurrent producers on one pool are safe and serialize through a dispatch lease; nested same-pool parallelFor/forkJoin run in parallel, other nested primitives run inline on the caller. |
| **Drop-in for the baseline** | no |

## Gotchas

- ThreadPool(n) counts the calling thread, clamps to physical cores and the affinity mask, and auto-pins the producer on Linux; check pool.participants() for the real count.
- Bodies are captured by a non-owning FunctionRef, so callables must outlive the call; the pool is non-copyable and non-movable.
- The Chase-Lev deque keeps every superseded ring buffer until the deque is destroyed, which is one source of the higher peak RSS.
- Open issue #1: the header declares a member named slots, which breaks compilation when Qt's slots macro is in scope; submitDetached spawns a new std::thread per call.

## Known shortcomings

- The runtime-benchmarks citor adapter is a straight port of the libfork fib/skynet code but pins citor v0.4.5 by default; the current release is 0.6.2. Peak RSS is 2-5x its peers', partly because the Chase-Lev deque keeps every superseded buffer until destruction. Open issue 1: a member named `slots` breaks builds when Qt is in scope.

## Caveats and trade-offs

Own README admits a lower win rate on multi-CCD and Intel mesh hosts. It loses to OpenMP on barrier-bound stencils, to oneTBB on heavy-tailed reductions, and to libfork on recursive fork-join with a multi-CCD pool. In runtime-benchmarks, nqueens (80765 us vs libfork 69010 us) and matmul(2048) (48069 us vs libfork 44140 us) are slower than libfork and TooManyCooks. Peak RSS is higher than its peers' (e.g. fib(39) 44.5 MB vs tbb 11.69 MB). runtime-benchmarks is maintained by the TooManyCooks author (Unlicense), with CPU boost enabled and the schedutil governor. The README's single-CCD Zen 5 'wins the vast majority' claim is qualitative in the text (charts only).

Tuned for single-CCD Zen with physical-core pinning; header-only C++20.

## Maintenance

Actively developed (v0.6.2, last commit 2026-10-05, pre-1.0 with a stable public surface), MIT, header-only and easy to vendor; 54 stars, so production use outside the author is not documented.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** tzcnt/runtime-benchmarks (public build_and_bench_all.py suite) lists citor next to tbb and taskflow, and it states Clang 21.1.7 Release -O3 -march=native, tcmalloc and an EPYC 7742 64-core machine; every number in the record matches its summary table.
- **Verifier notes:** Numbers verified on the runtime-benchmarks README. MIT license and 54 stars confirmed; last_commit was not re-checked.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://github.com/Lallapallooza/citor>
  - <https://raw.githubusercontent.com/Lallapallooza/citor/HEAD/README.md>
  - <https://raw.githubusercontent.com/Lallapallooza/citor/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Lallapallooza/citor/HEAD/README.md>
  - <https://github.com/Lallapallooza/citor/tree/main/include/citor/detail>
  - <https://raw.githubusercontent.com/Lallapallooza/citor/HEAD/include/citor/detail/chase_lev_deque.h>
  - <https://raw.githubusercontent.com/Lallapallooza/citor/HEAD/include/citor/detail/forkjoin_state.h>
  - <https://github.com/Lallapallooza/citor/issues?q=is%3Aissue>
  - <https://github.com/Lallapallooza/citor/issues/1>
  - <https://github.com/Lallapallooza/citor/commits>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/README.md>
  - <https://github.com/tzcnt/runtime-benchmarks/tree/main/cpp>
  - <https://github.com/tzcnt/runtime-benchmarks/tree/main/cpp/citor>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/citor/fib.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/citor/skynet.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/citor/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/tbb/fib.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/lallapallooza/citor`) · [data/wave11/enrich/raw/github_com_lallapallooza_citor.json](../../../data/wave11/enrich/raw/github_com_lallapallooza_citor.json) (enrichment confidence 0.82)

</details>
