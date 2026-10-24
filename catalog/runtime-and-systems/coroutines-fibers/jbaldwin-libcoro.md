# libcoro

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Coroutines and fibers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++20 coroutine library with epoll/kqueue TCP, UDP, TLS and DNS; edges cppcoro on single-threaded socket ping-pong.

| | |
|---|---|
| **Beats** | cppcoro (Boost.Cobalt for the channel row) |
| **Claimed result** | Third-party table (us, lower is better): io_socket_st libcoro 483074 vs cppcoro 524717, about 1.09x faster (derived from page data), though Boost.Cobalt (393036) and TooManyCooks (339340) are faster. channel: libcoro_mt 409967 vs cobalt_st_asio 910778, about 2.2x faster (derived from page data), TooManyCooks 390771 / 391661. |
| **Workload** | io_socket_st: TCP ping-pong of 100,000 requests over 20 connections between a single-threaded client and a single-threaded server, each on its own event loop (libcoro io_scheduler with process_tasks_inline against cppcoro io_service from the andreasbuhr fork); channel: async MPMC queue moving 10,000,000 elements with thread_count/2 producers and consumers, libcoro coro::queue on a coro::thread_pool of 64 threads (mt config) against Boost.Cobalt channel on a single thread (st_asio config; the source notes cobalt does not support multiple threads). |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7742 64-core, 64 worker threads (no SMT), Debian 13 Server, CPU boost enabled, schedutil governor |
| **Compiler and flags** | Clang 21.1.7 Release, -O3 -march=native, C++23 for libcoro; libcoro pinned to commit 44d12235a218a93cf6ce462f67c06a1287901c54 with LIBCORO_FEATURE_NETWORKING ON and TLS OFF; linked against tcmalloc_minimal. |
| **Adoption** | 968 stars, 102 forks |
| **Last commit** | 2026-03-31 |
| **Links** | [repository](https://github.com/jbaldwin/libcoro) · [benchmark](https://github.com/tzcnt/runtime-benchmarks) |

## Verdict

In tzcnt/runtime-benchmarks on an AMD EPYC 7742 (Clang 21.1.7, -O3 -march=native, C++23, tcmalloc), a single-threaded TCP ping-pong of 100,000 requests over 20 connections took 483074 us with libcoro's inline io_scheduler against 524717 us for cppcoro's io_service from the andreasbuhr fork, about 1.09x (derived from page data), from one run each with no variance. The channel row (libcoro queue on 64 threads, 409967 us, against Boost.Cobalt on one thread, 910778 us) compares different thread configurations, so it is not like-for-like.

## Use it when

- Linux or macOS network services and clients written as coroutines that want TCP, UDP, TLS and async DNS in one Apache-2.0 library without Boost
- Thread-per-core designs: one inline scheduler per core, where each request does little CPU work (in the third-party io_socket_st row it beat cppcoro by about 9%, 483074 vs 524717 us)
- Async producer/consumer queues on a small thread pool: coro::queue on 64 threads moved 10M elements in 409967 us, close to TooManyCooks at 390771 us
- Projects that also need coroutine primitives such as shared_mutex, semaphore, condition_variable, when_any and timeouts on scheduled tasks (std::stop_source plus a timeout)
- Android targets: the repo ships a test harness for arm64-v8a, armeabi-v7a, x86 and x86_64 with TLS through prebuilt OpenSSL

## Skip it when

- Recursive fork-join or many small CPU tasks: it was the slowest runtime in the suite (mean ratio 2513.96x; skynet 119686148 us vs cppcoro 144907 us) because every schedule() goes through one mutex-guarded FIFO deque; issue #404 is open and the Chase-Lev work-stealing rework (PR #450) is not on main
- Memory-bounded hosts running deep task trees: the FIFO queue turns fork-join into a breadth-first traversal, so peak RSS reached 14.66 GB on skynet, 5.03 GB on nqueens and 15.81 GB on fib(39); issue #446 is open
- Peak single-threaded socket throughput: TooManyCooks (339340 us) and Boost.Cobalt (393036 us) beat it on io_socket_st (483074 us)
- Windows or Emscripten network code: LIBCORO_FEATURE_NETWORKING and TLS are not supported there, and the I/O scheduler (timers, yield_for, schedule_after) requires the networking feature
- Code that must track a stable API: io_scheduler was renamed to scheduler in January 2026 (#435) and a new socket Read/Write API landed in February 2026 (#436)

## How it is fast

The scheduler is a readiness-based event loop over epoll on Linux and kqueue on macOS: each poll() registers the fd one-shot (EPOLLONESHOT), races it against a timer, and removes it when the event fires, with timeouts handled by a timerfd. In process_tasks_inline mode the event-loop thread resumes coroutines itself, so a one-loop-per-core design avoids cross-thread hand-offs. task uses symmetric transfer and when_all joins through one atomic latch; coro::queue hands a pushed element straight to a waiting consumer when one exists. thread_pool is a single std::deque guarded by one mutex and condition variable, with no per-thread queues or work stealing, which is why it does badly on fork-join.

## Compared with alternatives

Pick libcoro over cppcoro when you need maintained Linux/macOS networking with TLS and DNS in plain C++20 (upstream cppcoro has no Linux sockets), and over Boost.Cobalt when you cannot take a Boost dependency or want a multi-threaded queue; pick Boost.Cobalt for faster single-threaded Asio I/O, and cppcoro, Coros or Marl for any CPU fork-join work.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | pthreads; c-ares (git submodule) for networking/DNS; OpenSSL for LIBCORO_FEATURE_TLS; CMake |
| **Minimum toolchain** | C++20 with coroutine support; README lists g++ 11-13, clang++ 16-17 and MSVC 2022 (no networking/TLS on MSVC) |
| **Platforms** | Linux (epoll) and macOS (kqueue) with full features; Windows 2022 and Emscripten without networking or TLS; Android arm64-v8a, armeabi-v7a, x86, x86_64 |
| **Thread safety** | thread_pool, scheduler, queue, ring_buffer and the mutexes are documented as thread-safe; any co_await may resume on another thread, so thread_local must not be used across co_await unless the executor has exactly one thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Do not capture state in coroutine lambdas: the README warns captures are destroyed at the first suspension point (use-after-free); pass by value as arguments or wrap with coro::invoke.
- The benchmarked commit (44d12235, PR #433) predates the io_scheduler-to-scheduler rename (#435), the socket Read/Write API (#436) and the scheduler lock removal (#444), so the suite's harness does not compile against main and current I/O numbers may differ; thread_pool.cpp is unchanged.
- The README says threads can switch through 'work stealing' on libcoro's schedulers, but thread_pool is one shared FIFO deque behind a mutex; the profile in issue #404 shows about 96% of time in kernel spin-lock slow paths on fork-join.
- Harness asymmetries in the io_socket_st row: the cppcoro program's timer includes stopping both io_services and joining both event threads while libcoro's stops before scheduler teardown, and libcoro is linked against tcmalloc while the suite's cppcoro build skips tcmalloc on Linux (mimalloc, jemalloc or glibc malloc).

## Known shortcomings

- Only like-for-like win is io_socket_st against cppcoro, 9%, single run; the channel row is cross-config (64-thread pool vs cobalt on one thread); slowest on fork-join (2513.96x).
- Enricher retier A to C: io_socket_st times cppcoro's teardown (io_service stop() plus two joins) but not libcoro's, and libcoro gets tcmalloc; one run, 9% margin. thread_pool is a mutex-guarded FIFO deque despite the README's work-stealing claim (14.66 GB RSS on fork-join).

## Caveats and trade-offs

Weak result. The only wins are one 9% single-threaded socket row against cppcoro (itself the slowest of the four in that table) and one cross-configuration channel row (libcoro on a 64-thread pool vs Boost.Cobalt on a single thread, so not equal footing; TooManyCooks single-threaded Asio is 1.00x, 2.3x faster than cobalt, while no single-threaded libcoro channel row exists). Each table cell is one process run with no repetitions or variance reported, so the 9% socket margin is not shown to exceed run-to-run noise. On the fork-join benchmarks libcoro is the slowest runtime tested: mean ratio 2513.96x (skynet 119686148 us, nqueens 33347402 us, fib(39) 238019884 us, matmul 374412 us) against cppcoro 3.67x, with peak RSS of 14.66 GB on skynet. The brief baselines (hand-written coroutine task types, std::async/std::future) are not measured anywhere. libcoro's own README gives only server example runs without a baseline: ab TCP echo 110753.80 requests/s and wrk HTTP 200 OK 325778.99 requests/s with 2.96 ms mean latency, both on an Intel Core i7-9750H, so those are not comparisons. Repo test/bench.cpp times coroutine sync_wait, thread_pool and scheduler counters against a plain direct-call loop but publishes no results. The suite author also authors TooManyCooks (a competing runtime); allocator selection differs per library (libcoro tcmalloc first; the suite's cppcoro build skips tcmalloc on Linux and uses mimalloc, jemalloc or glibc malloc). The cppcoro rows measure the andreasbuhr/cppcoro fork. [retier] Enricher: in io_socket_st, cppcoro's timed region includes io_service stop() plus two thread joins while libcoro's ends before scheduler teardown, and libcoro gets tcmalloc against cppcoro's non-tcmalloc allocator; with one run and a 9% margin (41643 us) the win is unproven. The suite pins 44d12235 (PR #433), before the io_scheduler-to-scheduler rename (#435), the Read/Write API (#436) and the scheduler lock removal (#444). thread_pool is a single mutex-guarded FIFO deque at the pin and at HEAD although the README says work stealing; FIFO gives breadth-first fork-join and the 14.66 GB RSS (issues #404 and #446 open, Chase-Lev PR #450 unmerged).

C++20 library (task, generator, event, latch, mutex, ring buffer, thread_pool, io_scheduler, TCP/TLS/DNS networking) that uses a mutex-and-condition-variable thread pool and per-task heap frames; ships Android test harness. Fork-join workloads hit very high peak RSS in the suite: skynet 14.66 GB, nqueens 5.03 GB, fib(39) 15.81 GB against 11-14 MB for TooManyCooks and TBB.

## Maintenance

Active (last commit 2026-03-31, 16 open issues) and Apache-2.0 with a CMake build that is easy to add_subdirectory or FetchContent, but its thread_pool redesign for fork-join is still open (issues #404 and #446).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now C.
- **Tier reason:** tzcnt/runtime-benchmarks README shows io_socket_st libcoro 483074 us vs cppcoro 524717 us and channel libcoro_mt 409967 us vs cobalt_st_asio 910778 us exactly as claimed; code is public (cpp/libcoro/io_socket_st.cpp vs cpp/cppcoro/io_socket_st.cpp, cpp/libcoro/channel.cpp vs cpp/cobalt/channel.cpp) with Clang 21.1.7 Release, -march=native and EPYC 7742 stated. Only the io_socket_st row is a like-for-like win; the channel row compares a 64-thread pool against Boost.Cobalt on one thread.
- **Retiered** A to C: A to C: the only like-for-like win (io_socket_st, 9%, one run) comes from an asymmetric harness: cppcoro's timer includes io_service stop() and two thread joins while libcoro's stops before scheduler teardown, and libcoro links tcmalloc while cppcoro does not; the channel row is cross-config. Asymmetric-baseline downgrade precedent.
- **Verifier notes:** Tier A holds only for the io_socket_st row against cppcoro; the margin is 9% from a single run. Metadata checked on github.com: Apache-2.0, 968 stars, 102 forks, last commit 2026-03-31 (active), not a fork.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-64 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/build_and_bench_all.py>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/libcoro/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/libcoro/build_all.sh>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/libcoro/io_socket_st.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/io_socket_st.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/libcoro/channel.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cobalt/channel.cpp>
  - <https://github.com/jbaldwin/libcoro>
  - <https://github.com/jbaldwin/libcoro/commits/main>
- **Sources the enricher read:**
  - <https://github.com/jbaldwin/libcoro>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/README.md>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/src/thread_pool.cpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/include/coro/thread_pool.hpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/src/scheduler.cpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/include/coro/scheduler.hpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/include/coro/task.hpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/include/coro/queue.hpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/include/coro/when_all.hpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/src/detail/io_notifier_epoll.cpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/include/coro/detail/io_notifier_epoll.hpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/src/detail/io_notifier_kqueue.cpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/HEAD/src/net/tcp/client.cpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/44d12235a218a93cf6ce462f67c06a1287901c54/src/thread_pool.cpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/44d12235a218a93cf6ce462f67c06a1287901c54/include/coro/thread_pool.hpp>
  - <https://raw.githubusercontent.com/jbaldwin/libcoro/44d12235a218a93cf6ce462f67c06a1287901c54/include/coro/io_scheduler.hpp>
  - <https://github.com/jbaldwin/libcoro/commit/44d12235a218a93cf6ce462f67c06a1287901c54>
  - <https://github.com/jbaldwin/libcoro/commits/main>
  - <https://github.com/jbaldwin/libcoro/issues>
  - <https://github.com/jbaldwin/libcoro/issues/404>
  - <https://github.com/jbaldwin/libcoro/issues/446>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/build_and_bench_all.py>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/libcoro/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/libcoro/io_socket_st.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/libcoro/channel.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/libcoro/skynet.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cobalt/channel.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/io_socket_st.cpp>
  - <https://raw.githubusercontent.com/tzcnt/runtime-benchmarks/HEAD/cpp/cppcoro/CMakeLists.txt>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/jbaldwin/libcoro`) · [data/wave11/enrich/raw/github_com_jbaldwin_libcoro.json](../../../data/wave11/enrich/raw/github_com_jbaldwin_libcoro.json) (enrichment confidence 0.75)

</details>
