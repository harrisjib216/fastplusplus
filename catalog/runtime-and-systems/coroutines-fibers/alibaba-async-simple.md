# async_simple (Lazy)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Alibaba's C++20 Lazy coroutine task type; about 3x faster than folly::coro::Task on call-chain and fan-out microbenchmarks, near-parity with cppcoro.

| | |
|---|---|
| **Beats** | folly::coro::Task (folly coroutines) and cppcoro::task |
| **Claimed result** | Lazy chain 59745 ns vs folly Task 195801 ns (about 3.3x faster, derived from page data) and cppcoro task 61308 ns (about 1.03x, derived from page data); collectAll 7880137 ns vs folly 23795927 ns (about 3.0x, derived from page data) and cppcoro when_all 8934768 ns (about 1.13x, derived from page data). Wall-clock Time column. |
| **Workload** | Google Benchmark of C++20 stackless coroutines: a 1000-deep co_await call chain, and collectAll/when_all over 5000 tasks each with a 50-deep chain, run through syncAwait / blockingWait / sync_wait. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8163 @ 2.50GHz, 96 logical processors, L1d 32 KiB x48, L2 1024 KiB x48, L3 33792 KiB x2 |
| **Compiler and flags** | Clang 13; optimisation flags, standard library, and folly/cppcoro versions not stated |
| **Adoption** | 2.2k stars |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/alibaba/async_simple) · [benchmark](https://github.com/alibaba/async_simple/blob/main/docs/docs.en/Performance.md) |

## Verdict

In Alibaba's own Google Benchmark run (Clang 13, Intel Xeon Platinum 8163, flags and library versions unstated), a 1000-deep co_await chain took 59.7 us with Lazy vs 195.8 us with folly::coro::Task and 61.3 us with cppcoro::task, and awaiting 5000 tasks of 50-deep chains took 7.9 ms vs 23.8 ms (folly collectAllRange) and 8.9 ms (cppcoro when_all). Only the async_simple rows are in the repo's benchmark source; the doc itself says the test does not show async_simple is better.

## Use it when

- Deep co_await call chains of small coroutine functions where per-call task overhead matters (the 1000-deep chain ran about 60 us per run on a Xeon Platinum 8163, about 3.3x less than folly::coro::Task).
- Code that wants Task-style C++20 coroutines without pulling in folly; Lazy is almost header-only and installs through vcpkg, Conan, CMake find_package or Bazel.
- Codebases that bring their own executor and need fan-out helpers (collectAll, collectAllPara, collectAllWindowedPara, collectAny), cancellation signals and coroutine-local data (LazyLocals).
- Allocation-sensitive services built with recent clang, where custom frame allocators or coro_await_elidable can cut coroutine frame allocations.

## Skip it when

- You need a production event loop or I/O executor out of the box: the Performance doc says async_simple has no production-grade executor, and the ChangeLog (1.2) calls SimpleExecutor and SimpleIOExecutor testing-only.
- You rely on folly's debugging features (async stack traces, context recording on switches) or are already invested in folly::coro; the measured gap is partly the cost of those features.
- Against cppcoro the measured margin is small (about 1.03x on the chain, 1.13x on fan-out), so switching from cppcoro for speed alone buys little.
- Toolchains older than GCC 10.3, clang 10 or Apple clang 14; open issue #449 reports compile errors with GCC 10/11 when coroutines meet template functions, and the README warns of clang 15 bugs with Generator.
- Code that resumes coroutines synchronously with no executor bound (custom callback awaiters, Mutex unlock chains): open issue #404 reports stack overflow in that case, and maintainers advise not starting coroutines without a scheduler.

## How it is fast

Lazy suspends at initial_suspend and uses symmetric transfer: awaiting a Lazy returns the callee's coroutine_handle from await_suspend, and the FinalAwaiter returns the stored continuation, so a co_await chain resumes without recursion or a scheduler hop unless the RescheduleLazy variant is used. The promise carries only a continuation, an Executor pointer and a LazyLocals pointer, and the result is held in a std::variant&lt;monostate, T, exception_ptr&gt;, so there is no async-stack or context recording on each switch (the extra work the Performance doc names for folly's Task). Frames can come from a user allocator via std::allocator_arg_t, and with clang's [[clang::coro_await_elidable]] a callee's frame is folded into the caller's frame so the co_await chain avoids a heap allocation per call.

## Compared with alternatives

Pick it over cppcoro when you want an actively maintained Task type with executor plumbing, cancellation and GCC support (cppcoro's README lists only MSVC 2017 and Clang 5/6 with libc++, and its Linux io_context is unimplemented), accepting that raw task speed is about the same. Pick libcoro or Boost.Cobalt instead if you want a ready I/O runtime rather than bringing your own executor.

## Integration

| | |
|---|---|
| **Form** | header-only (Lazy, Future, collect helpers); static or shared lib for Uthread |
| **Dependencies** | none for Lazy; libaio optional (IO), googletest for tests, Google Benchmark for benchmarks, standalone asio for the demo |
| **Minimum toolchain** | C++20; clang 10+, GCC 10.3+ or Apple clang 14+ (GCC 12 needs -Wno-maybe-uninitialized; clang 17+ suggested for Generator; MSVC may need /EHa for C4737); C++20 module build needs clang 16+ |
| **Platforms** | Linux, macOS and Windows build instructions (CMake, Bazel, vcpkg, Conan, xmake); libaio IO parts Linux-only; Uthread is not usable in Compiler Explorer and needs installation; CPU architectures for Uthread not documented |
| **Thread safety** | Not documented for Lazy objects themselves; work moves between threads only through the executor you bind. syncAwait asserts if called from a thread inside the Lazy's own executor (deadlock risk), and LazyLocals are destroyed before the start() callback runs. |
| **Drop-in for the baseline** | partial — same lazily started Task model as folly::coro::Task and cppcoro::task, but different names for the awaiting and fan-out functions, Try&lt;T&gt; results and its own Executor interface, so call sites must be ported |

## Gotchas

- collectAllPara only runs children in parallel when the awaiting Lazy has an executor; under plain syncAwait with no executor (exactly how the benchmark runs it) the children execute serially on the calling thread, as Lazy.md warns.
- Lazy&lt;T&gt; requires alignof(T) &lt;= alignof(std::max_align_t) (ChangeLog 1.2), and a Lazy may only be co_awaited from inside another Lazy function.
- Statements after a co_await may never run if the awaited task throws; exceptions propagate to the root and are retrieved via syncAwait's throw, the start() callback's Try&lt;T&gt;, or coAwaitTry.
- The benchmarked code predates release 1.4 (2025-07-29), which added cancellation; the current collectAll creates a Signal and one heap-allocated LazyLocalBase per child, and the published numbers were not re-run on it.

## Known shortcomings

- First-party Performance.md numbers with Clang 13 and a Xeon 8163 but no flags, standard library or baseline versions; part of the 3.3x gap over folly Task is folly recording context on each switch, a feature async_simple's Lazy lacks; only 1.03-1.13x over cppcoro.
- Enricher: collectAllPara benchmarked with no executor, so children run serially on the calling thread; numbers predate the 1.4 cancellation changes; open issue #404 (stack overflow without an executor).

## Caveats and trade-offs

First-party document whose own closing note says the test is a simple one and does not mean async_simple is better, and adds that folly's Task has more functionality (it records context on each switch for debuggability), so the folly gap partly reflects that feature cost. Flags (-O level), libstdc++/libc++ choice and baseline library versions are missing, so it falls short of tier A. Only task creation, call-chain and fan-out speed are measured, not real I/O or an executor, because the doc says async_simple has no production-grade executor. Doc was last edited 2023-03-24 (file created 2022-02-21) and numbers are from Clang 13. The benchmark source in the repo (benchmarks/Lazy.bench.cpp) contains only the async_simple rows (plus RescheduleLazy variants); folly and cppcoro rows exist only in the doc's listing. Against cppcoro the margin is within a few percent on the chain case (about 1.03x). std::async is not benchmarked. The repo's other published comparisons (docs/docs.en/QuantitativeAnalysisReportOfCoroutinePerformance.md, Xeon E5-2650 v2, Google Benchmark) compare Lazy only with the project's own stackful Uthread (about 100x faster switching), and docs/docs.en/ImproveNetLibWithAsyncSimple.md shows a coroutine HTTP server at 72363 qps vs a blocking server at 32483 qps (2.2x, Xeon E5-2682 v4, wrk); neither names a listed baseline. Maintainer discussion #309 estimates a coroutine switch costs about 10 ns (estimate, not a measurement). [retier] Enricher: the benchmark runs syncAwait with no executor, so collectAllPara runs its children serially on the calling thread (Lazy.md calls this usage wrong); how folly's collectAllRange dispatches under blockingWait was not checked. The numbers predate 1.4 (2025-07-29, cancellation), whose collectAll adds a Signal and one heap LazyLocalBase per child; not re-measured. Open issue #404: stack overflow without an executor.

Lazy is a lazily started C++20 task type. folly::coro::Task offers more functionality, notably async-stack/context recording on switches for debuggability, which is the cost the doc itself names for the slower folly rows. Stackful Uthread is a separate, non-header-only component. Requires clang &gt;= 10, gcc &gt;= 10.3 or Apple-clang &gt;= 14.

## Maintenance

Actively maintained (release 1.4 in July 2025, commits through September 2026), Apache-2.0 and mostly header-only, so it is easy to vendor, though issue triage is slow (27 open issues, some from 2022).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party doc docs/docs.en/Performance.md lists the full Google Benchmark program, Clang 13 and the CPU (Xeon Platinum 8163), but no optimisation flags, standard library or folly/cppcoro versions, and the repo's benchmarks/Lazy.bench.cpp holds only the async_simple rows, so it falls short of A; first-party with partial methodology is C.
- **Verifier notes:** All six Time values and the derived ratios (3.3x, 1.03x, 3.0x, 1.13x) match the doc; file history (Init 2022-02-21, last edit 2023-03-24) and repo metadata (Apache-2.0, 2.2k stars, last commit 2026-09-13, not archived) check out. Only change: caveat now cites the doc's own remark that folly Task does extra context recording.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-65 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/docs/docs.en/Performance.md>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/benchmarks/Lazy.bench.cpp>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/benchmarks/CMakeLists.txt>
  - <https://github.com/alibaba/async_simple>
  - <https://github.com/alibaba/async_simple/commits/main>
  - <https://github.com/alibaba/async_simple/commits/main/docs/docs.en/Performance.md>
- **Sources the enricher read:**
  - <https://github.com/alibaba/async_simple>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/README.md>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/docs/docs.en/Performance.md>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/benchmarks/Lazy.bench.cpp>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/async_simple/coro/Lazy.h>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/async_simple/coro/Collect.h>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/async_simple/coro/SyncAwait.h>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/async_simple/coro/PromiseAllocator.h>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/docs/docs.en/Lazy.md>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/docs/docs.en/QuantitativeAnalysisReportOfCoroutinePerformance.md>
  - <https://raw.githubusercontent.com/alibaba/async_simple/main/ChangeLog>
  - <https://github.com/alibaba/async_simple/issues?q=is%3Aissue+performance>
  - <https://github.com/alibaba/async_simple/issues>
  - <https://github.com/alibaba/async_simple/issues/404>
  - <https://github.com/lewissbaker/cppcoro>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/alibaba/async_simple`) · [data/wave11/enrich/raw/github_com_alibaba_async_simple.json](../../../data/wave11/enrich/raw/github_com_alibaba_async_simple.json) (enrichment confidence 0.8)

</details>
