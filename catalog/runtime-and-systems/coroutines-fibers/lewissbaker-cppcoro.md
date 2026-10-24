# cppcoro

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> C++ coroutine library whose work-stealing static_thread_pool runs fork-join tasks 20-86x faster than concurrencpp or HPX.

| | |
|---|---|
| **Beats** | concurrencpp (also HPX and libcoro thread-pool runtimes) |
| **Claimed result** | Third-party table, absolute times in us: skynet 144907 (cppcoro) vs 12514888 (concurrencpp), 11965484 (HPX), 119686148 (libcoro); nqueens 162773 vs 8000700 / 3452638 / 33347402; fib(39) 269384 vs 20663744 / 10789290 / 238019884. Mean ratio to best 3.67x for cppcoro vs 258.19x concurrencpp, 186.81x HPX, 2513.96x libcoro. Derived from page data: cppcoro is about 86x, 49x and 77x faster than concurrencpp on skynet, nqueens and fib, and about 83x, 21x and 40x faster than HPX. It is slower than tbb (3.25x), taskflow (3.34x), libfork (1.18x) and TooManyCooks (1.32x) on the same table. |
| **Workload** | Recursive fork-join coroutine benchmarks on 64 worker threads: skynet (100M tasks, forks x10), nqueens (forks up to x14) and fib(39) (forks x2), run with cppcoro's static_thread_pool; matmul(2048) is a tie. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7742 64-core, 64 worker threads (no SMT), Debian 13 Server, CPU boost enabled, schedutil governor |
| **Compiler and flags** | Clang 21.1.7 Release (CMake preset clang-linux-release, so -O3 -DNDEBUG), -march=native, C++20; code pinned to andreasbuhr/cppcoro commit f05170fbc71aaae06dc31e32812f1caba9525377. Allocator for the cppcoro binaries is not certain: cpp/cppcoro/CMakeLists.txt links mimalloc if found, else jemalloc, and deliberately skips tcmalloc on Linux (falls back to glibc malloc), while the README's machine note says the run was linked against libtcmalloc_minimal.so.4 (which the concurrencpp, HPX and libcoro builds pick first). Baselines pinned in the suite: concurrencpp v.0.1.7, HPX v1.11.0, libcoro commit 44d12235a218a93cf6ce462f67c06a1287901c54. |
| **Adoption** | 3.9k stars, 509 forks |
| **Last commit** | 2022-09-02 |
| **Links** | [repository](https://github.com/lewissbaker/cppcoro) · [benchmark](https://github.com/tzcnt/runtime-benchmarks) |

## Verdict

In tzcnt/runtime-benchmarks on an AMD EPYC 7742 with 64 worker threads, Clang 21.1.7 -O3 -march=native, the andreasbuhr fork's static_thread_pool took 144907 us on skynet (100M tasks) against 12514888 us for concurrencpp and 11965484 us for HPX, about 86x and 83x faster (derived from page data), with 49x/21x on nqueens and 77x/40x on fib(39); matmul(2048) is a tie. Each cell is one timed run after one warm-up with no variance reported, the suite's author also writes the competing TooManyCooks, and the baselines got tcmalloc while cppcoro got mimalloc, jemalloc or glibc malloc, which if anything disadvantages cppcoro.

## Use it when

- Recursive fork-join on a CPU pool (divide-and-conquer, tree search, parallel reductions) where you want lazy tasks plus when_all and the alternative is concurrencpp or HPX: about 86x and 83x faster than them on 100M-task skynet in the third-party suite
- Clang builds on Linux or Windows where symmetric transfer is enabled and you can pair it with mimalloc or jemalloc, since every coroutine frame is a heap allocation
- Code that needs coroutine-aware synchronisation primitives (async_mutex, async_manual_reset_event, async_latch, single/multi_producer_sequencer) on top of a thread pool
- Teaching or prototyping coroutine abstractions: the README documents every type in detail and the code is small enough to read and vendor

## Skip it when

- Peak fork-join throughput: it trails citor, libfork, TooManyCooks, TBB and Taskflow on mean ratio (3.67x vs 1.06-3.34x), and Coros on skynet (144907 vs 94532 us) and fib(39) (269384 vs 187136 us)
- Memory-constrained hosts: peak RSS was about 134 MB on skynet, nqueens and fib(39) against 9-14 MB for TBB, Taskflow, libfork, TooManyCooks, Coros and concurrencpp
- Single-threaded socket servers: in the io_socket_st row it was the slowest of four (524717 us vs libcoro 483074, Boost.Cobalt 393036, TooManyCooks 339340), and upstream has no Linux io_service, file I/O or networking at all
- GCC users or anyone needing a maintained upstream: lewissbaker/cppcoro hard-codes &lt;experimental/coroutine&gt;, enables symmetric transfer only for Clang, builds with the Python 2.7 Cake system, and has 92 open issues and 21 open PRs without activity since 2022
- Code that cannot tolerate known open bugs: issue #209 (ThreadSanitizer race in sync_wait with static_thread_pool) and #221 (cancellation deadlock) are open with no response

## How it is fast

static_thread_pool is a work-stealing scheduler: work enqueued from a pool thread goes into that thread's lock-free LIFO ring buffer (initially 256 slots, doubled on demand), work from outside goes into a global lock-free FIFO list, and idle threads drain the global queue, then steal from the back of other threads' queues, spinning about 30 rounds before sleeping on an event. schedule() never throws and normally allocates nothing because the schedule_operation node lives in the awaiting coroutine's frame and is linked intrusively. task&lt;T&gt; is lazy and, on Clang 7+, hands control back to the awaiting coroutine through symmetric transfer (await_suspend returning a coroutine_handle) instead of an atomic handshake; when_all joins children with a single atomic countdown (when_all_counter), so per-task overhead is the heap frame, an intrusive queue push and one fetch_sub.

## Compared with alternatives

Pick cppcoro (via the andreasbuhr fork) over Marl or Coros when you want lazy C++20 tasks with when_all on a work-stealing pool and a rich set of async primitives; pick async_simple Lazy for a maintained library with similar task cost (59745 vs 61308 ns on its chain test), Boost.Cobalt or libcoro for single-threaded I/O, and libfork or TooManyCooks if raw fork-join speed and memory matter most.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none beyond the C++ standard library; upstream Linux builds need Clang + libc++ and Python 2.7 for the Cake build, Windows needs the Windows 10 SDK; the andreasbuhr fork builds with CMake |
| **Minimum toolchain** | Upstream: Coroutines TS with MSVC 2017 (/await) or Clang 5.0+ and libc++ (&lt;experimental/coroutine&gt;). andreasbuhr fork: C++20 coroutines, tested on GCC 10.2-16, Clang 13-22, MSVC 2017-2026 |
| **Platforms** | Windows (x86, x64) fully; Linux upstream only for tasks, generators, sync primitives and static_thread_pool (no io_service, file or socket I/O); the andreasbuhr fork adds an epoll-based io_service and sockets on Linux; macOS not documented |
| **Thread safety** | static_thread_pool, async_mutex, async events, async_latch and the sequencers are built for multi-threaded use; single_consumer_\* types allow one awaiter; task&lt;T&gt; is a move-only single-awaiter handle, shared_task&lt;T&gt; supports concurrent awaiters at a reference-counting cost |
| **Drop-in for the baseline** | no |

## Gotchas

- The benchmarked code is the andreasbuhr/cppcoro fork, not this repo. The fork's README lists only include, namespace, CMake and CI changes, but its static_thread_pool also differs (notify_intent_to_sleep uses an exchange so each sleeper is counted once, upstream uses a plain store) and it adds a Linux epoll io_service, so the io_socket_st row cannot be reproduced with upstream on Linux.
- Symmetric transfer is switched on only for Clang 7+ in config.hpp; on GCC and MSVC task&lt;T&gt; falls back to a void await_suspend with an atomic&lt;bool&gt; continuation handshake (issue #216 asks for GCC/MSVC support), so the Clang 21 numbers may not carry over.
- The per-thread local queue cap check compares m_mask (size minus 1) with max_local_queue_size (a power of two), so the intended 1 MB cap is never hit and a thread's ring buffer keeps doubling under very wide fork trees; the same code is in the fork.
- Every task allocates its frame on the heap, and the suite's CMake notes cppcoro is allocator-sensitive: it links mimalloc or jemalloc if found, skips tcmalloc on Linux because it was slower for cppcoro, and otherwise uses glibc malloc.

## Known shortcomings

- Measured code is the andreasbuhr fork; the suite's CMake skips tcmalloc on Linux (mimalloc/jemalloc else glibc) while the README machine lists tcmalloc_minimal, so cppcoro's allocator is unknown. Loses to TBB, taskflow, libfork, TMC and citor; one run per cell.
- Enricher: the measured andreasbuhr fork differs from upstream (thread-pool sleeper counting, a Linux epoll io_service upstream lacks); symmetric transfer only on Clang 7+; the 1 MB local-queue cap check is unreachable; open issues #209 (tsan race) and #221 (cancellation deadlock).

## Caveats and trade-offs

Neither the repo README nor any first-party page carries timings: the README makes only qualitative design claims (the static_thread_pool schedule() will not allocate memory in the common case; async_mutex is lock-free). The numbers come from the third-party tzcnt/runtime-benchmarks suite, which measures the maintained fork https://github.com/andreasbuhr/cppcoro (its README lists only build-system, CI and header/namespace-selection changes versus upstream; no performance changes are listed), not lewissbaker/cppcoro itself. The baselines it beats (concurrencpp v.0.1.7, HPX v1.11.0, libcoro) are other coroutine runtimes, not the std::future/std::async baseline from the brief, and no std::async row exists. cppcoro loses to TBB, Taskflow, libfork, TooManyCooks and citor on the fork-join benchmarks (it roughly ties TBB on skynet: 144907 us vs 142887 us) and uses about 10x the memory of TBB or Taskflow (134 MB vs 11-14 MB); in the io_socket_st TCP ping-pong row it is the slowest of four (524717 us vs libcoro 483074 us, Boost.Cobalt 393036 us, TooManyCooks 339340 us). The author of the suite also authors TooManyCooks (a competing runtime). Allocators differ per library: the suite's cppcoro CMake prefers mimalloc, then jemalloc, and otherwise uses glibc malloc on Linux (tcmalloc disabled because it was slower for cppcoro), while the other runtimes take tcmalloc first; the README says the summary machine had tcmalloc_minimal, so which allocator cppcoro actually used is not stated. Each table cell is one process run (warmup plus timed loop) with no repetitions or variance reported. The upstream repo is dormant since 2022-09-02, and the book lead calls it unmaintained. [retier] Enricher: the measured code is the andreasbuhr/cppcoro fork (active through 2026-06-12), which differs from upstream: its static_thread_pool counts sleepers once (notify_intent_to_sleep uses exchange) and it adds a Linux epoll io_service and sockets, so upstream cannot run io_socket_st on Linux. Symmetric transfer is enabled only on Clang 7+ (GCC and MSVC fall back to an atomic handshake, issue #216); the local-queue cap check (m_mask == max_local_queue_size) is unreachable, so the 1 MB cap never applies. Open issues #209 (tsan race in sync_wait) and #221 (cancellation deadlock).

Experimental library by its own description; no standard-coroutine-header support in upstream (uses std::experimental style on older compilers), Windows-oriented networking, cmake/cake build. Peak RSS on the fork-join benchmarks is about 134 MB (skynet, nqueens, fib) against 9-14 MB for tbb, taskflow, libfork and TooManyCooks, because the thread-pool runtime allocates a coroutine frame per task.

## Maintenance

Upstream is dormant since 2022-09-02 with 92 open issues and 21 open PRs, but MIT-licensed; use the andreasbuhr/cppcoro fork (MIT, commits through June 2026, CI on current GCC, Clang and MSVC), which is the code that was benchmarked.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** tzcnt/runtime-benchmarks README summary table carries the cppcoro, concurrencpp, HPX and libcoro rows exactly as claimed; benchmark code is public (cpp/cppcoro/skynet.cpp, nqueens.cpp, fib.cpp, matmul.cpp and the matching cpp/concurrencpp, cpp/HPX, cpp/libcoro files, driven by build_and_bench_all.py) with Clang 21.1.7 Release (-O3 via CMAKE_BUILD_TYPE Release, -march=native) on an EPYC 7742 stated. Timers start after pool creation and a warmup, so the harness looks fair; gains above 50x are not capped because compiler and flags are stated.
- **Verifier notes:** Numbers verified against the live README of tzcnt/runtime-benchmarks. The measured code is the andreasbuhr/cppcoro fork; the orchestrator may want a repo_url note or keep the upstream id. Corrected the allocator statement (the suite does not guarantee a high-performance allocator for cppcoro on Linux).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-64 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/build_and_bench_all.py>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/CMakePresets.json>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/build_all.sh>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/skynet.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/skynet.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/concurrencpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/HPX/CMakeLists.txt>
  - <https://github.com/lewissbaker/cppcoro>
  - <https://github.com/lewissbaker/cppcoro/commits/master>
- **Sources the enricher read:**
  - <https://github.com/lewissbaker/cppcoro>
  - <https://raw.githubusercontent.com/lewissbaker/cppcoro/HEAD/README.md>
  - <https://raw.githubusercontent.com/lewissbaker/cppcoro/HEAD/lib/static_thread_pool.cpp>
  - <https://raw.githubusercontent.com/lewissbaker/cppcoro/HEAD/include/cppcoro/static_thread_pool.hpp>
  - <https://raw.githubusercontent.com/lewissbaker/cppcoro/HEAD/include/cppcoro/task.hpp>
  - <https://raw.githubusercontent.com/lewissbaker/cppcoro/HEAD/include/cppcoro/config.hpp>
  - <https://raw.githubusercontent.com/lewissbaker/cppcoro/HEAD/lib/io_service.cpp>
  - <https://raw.githubusercontent.com/lewissbaker/cppcoro/HEAD/include/cppcoro/detail/when_all_ready_awaitable.hpp>
  - <https://github.com/lewissbaker/cppcoro/issues>
  - <https://github.com/lewissbaker/cppcoro/issues/209>
  - <https://github.com/andreasbuhr/cppcoro>
  - <https://github.com/andreasbuhr/cppcoro/commits/main>
  - <https://raw.githubusercontent.com/andreasbuhr/cppcoro/HEAD/README.md>
  - <https://raw.githubusercontent.com/andreasbuhr/cppcoro/HEAD/lib/static_thread_pool.cpp>
  - <https://raw.githubusercontent.com/andreasbuhr/cppcoro/HEAD/lib/io_service.cpp>
  - <https://raw.githubusercontent.com/andreasbuhr/cppcoro/HEAD/include/cppcoro/config.hpp>
  - <https://raw.githubusercontent.com/andreasbuhr/cppcoro/HEAD/include/cppcoro/detail/when_all_ready_awaitable.hpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/build_and_bench_all.py>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/skynet.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/fib.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/io_socket_st.cpp>
  - <https://raw.githubusercontent.com/andreasbuhr/cppcoro/HEAD/include/cppcoro/detail/when_all_counter.hpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/lewissbaker/cppcoro`) · [data/wave11/enrich/raw/github_com_lewissbaker_cppcoro.json](../../../data/wave11/enrich/raw/github_com_lewissbaker_cppcoro.json) (enrichment confidence 0.8)

</details>
