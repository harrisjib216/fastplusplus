# Boost.Corosio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Coroutine-only C++20 Boost-track networking library; 9-49% faster coroutine dispatch than Asio coroutines on Windows IOCP, socket I/O at parity.

| | |
|---|---|
| **Beats** | Asio (Boost.Asio coroutines and callbacks) |
| **Claimed result** | 9-50% faster handler dispatch than Asio coroutines (e.g. concurrent post/run: 2.35 Mops/s vs 1.61 Mops/s, +46%); best multithreaded scaling (retains 89% of single-thread throughput at 8 threads vs 58% for Asio coroutines and 53% for Asio callbacks; 1.54 vs 1.03 / 1.51 Mops/s at 8 threads). Losses: Asio callbacks are 51% faster on single-threaded post (2.59 vs 1.71 Mops/s), Asio is 2.5-2.6x faster on 64KB bidirectional throughput (5.74 GB/s vs 2.18 GB/s), and Asio is \~10x faster on timer schedule/cancel (historical; that timer API has since been removed). Socket latency and HTTP server results are ties (within 5%). |
| **Workload** | Handler dispatch, socket throughput/latency, HTTP server, and timer benchmarks on Windows using the IOCP backend, 3 seconds per benchmark |
| **Metric** | throughput |
| **Hardware** | Windows (IOCP backend); exact CPU model not stated |
| **Adoption** | 84 stars; developed under the C++ Alliance (cppalliance) GitHub organization |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/cppalliance/corosio) · [benchmark](https://github.com/cppalliance/corosio/blob/develop/doc/modules/ROOT/pages/benchmark-report.adoc) |

## Verdict

First-party report, Windows IOCP only, 3 s per benchmark; it names no CPU, compiler, flags or Asio version, and issue #352 dates the data to February 2026. Measured against Boost.Asio co_spawn/use_awaitable, spawning and running trivial coroutine tasks (capy::run_async vs co_spawn detached) was 9-49% faster, e.g. 2.35 vs 1.61 Mops/s for 4-thread concurrent post/run. Socket latency and HTTP throughput were within \~5%, and Corosio lost 64 KB bidirectional throughput by 2.5x.

## Use it when

- New C++20 coroutine networking code that would otherwise use Asio co_spawn/use_awaitable and spawns many small tasks: the report shows 1.71 vs 1.57 Mops/s for single-thread post and 2.14 vs 1.60 Mops/s for interleaved post/run on IOCP.
- One io_context run by several threads on a dispatch-heavy workload: 1.54 vs 1.03 Mops/s at 8 threads, keeping 89% of 1-thread throughput vs 58% for Asio coroutines. Treat this as indicative only: in the harness, several threads loop poll()+restart() at once, and Asio's docs forbid calling restart() while other run/poll calls are still in progress.
- You want one coroutine-native API across Windows IOCP, Linux epoll (io_uring optional), macOS/FreeBSD kqueue and a select fallback, with error codes in io_result and stop-token cancellation instead of completion tokens.
- Strictly single-threaded event loops: `locking_mode::unsafe` drops all internal locks, which the docs say removes 15-25% of post/dispatch overhead.
- Build time matters: in a Boost.Redis comparison posted during the Boost review, the Corosio-based client library built in 5.3 s vs 21.7 s for the Asio-based one.

## Skip it when

- Full-duplex bulk streaming (proxies, tunnels, replication links): at 64 KB buffers, bidirectional throughput was 2.18 GB/s vs 5.56 GB/s (Asio coroutines) and 5.74 GB/s (Asio callbacks). Corosio's combined throughput stays at its one-way rate, and the report suspects the read and write paths are serialized.
- Callback-style Asio code or hot single-threaded dispatch: Asio callbacks post at 2.59 vs 1.71 Mops/s and do interleaved post/run at 2.88 vs 2.14 Mops/s. Corosio has no callback interface at all.
- Linux- or macOS-specific performance decisions: no epoll, io_uring or kqueue numbers are published. The only report is IOCP data from February 2026.
- Projects that need a versioned, stable API: there are no tags or releases, both Corosio and Capy are consumed from their develop branches, and the Boost review (September 2026) ended in conditional acceptance with benchmark and docs items still open.
- Needs outside its scope: HTTP/WebSocket (use Boost.Http/Beast2), P2300 senders/receivers, raw sockets. TLS still has an open bug (#312, in-memory transport), and reviewers flagged verification gaps (#297, since closed).

## How it is fast

The benchmark report does not say which mechanism produces the dispatch wins. The design docs point to native C++20 symmetric transfer: await_suspend and dispatch() return a coroutine_handle, so the compiler tail-calls the next coroutine. Asio's awaitable returns void and emulates this with a frame stack and a pump() loop. The executor is passed as an await_suspend parameter, not through thread-local storage. On IOCP, each posted coroutine becomes a completion packet (PostQueuedCompletionStatus) and is dispatched through a function pointer stored in the op; the hot path uses interlocked counters and takes a user-space mutex only on the deferred/fallback path. The epoll/kqueue/select backends add an adaptive 'speculative inline completion' budget, and an opt-in lockless tier matches Asio's UNSAFE concurrency hint.

## Compared with alternatives

Pick Corosio over uring_exec or Condy (Linux io_uring only; they claim 1.27-3.46x and \~1.33x over Asio on socket ping-pong/recv) or PhotonLibOS (\~1.05x over boost::asio) when you need a portable, Boost-track coroutine replacement for Asio that includes Windows IOCP, and your bottleneck is task dispatch across threads rather than socket bandwidth. For Linux socket throughput, pick uring_exec or Condy: Corosio's own report shows no socket-throughput gain over Asio.

## Integration

| | |
|---|---|
| **Form** | static lib (shared when BUILD_SHARED_LIBS is set) |
| **Dependencies** | Boost.Capy (develop branch), Threads, ws2_32 on Windows; optional liburing (io_uring backend) and OpenSSL or WolfSSL (TLS); the benchmarks also need Boost.Asio |
| **Minimum toolchain** | C++20; GCC 12+, Clang 17+, MSVC 14.34+ (VS 2022 17.4+), latest Apple Clang; CMake 3.14+ |
| **Platforms** | Windows (IOCP); Linux x86_64/ARM64 (epoll by default, io_uring optional); macOS ARM64 and FreeBSD (kqueue); select backend on Linux/macOS/FreeBSD |
| **Thread safety** | io_context is thread-safe by default (`locking_mode::safe`): many threads may call run() and any thread may post. Individual sockets and I/O objects are not thread-safe. The `unsafe_io`/`unsafe` tiers allow only one thread, and cross-thread posting under them is undefined behavior. |
| **Drop-in for the baseline** | no |

## Gotchas

- A default-constructed io_context on a multi-core machine (concurrency_hint &gt; 1) silently resets the inline-completion budgets from (2, 16, 4) to (0, 0, 0), which turns off the reactor's inline fast path. Pass explicit io_context_options to keep it. One note in the configuration page contradicts this.
- Lockless tiers: under `unsafe`/`unsafe_io`, cancelling delay()/timeout() through a stop_token from another thread is undefined behavior. Under `unsafe`, DNS resolution and POSIX file open() return operation_not_supported. Before issue #310 was fixed, concurrency_hint == 1 silently enabled lockless mode.
- delay()/timeout() awaited on an executor that does not belong to an io_context terminates the program. timeout() requires the inner result's payload type to be default-constructible.
- The io_context must outlive every posted operation, and stop() abandons pending work instead of draining it. Join all threads that post to or run the context before destroying it.

## Known shortcomings

- Benchmark data dates from 2026-02, IOCP only, with no CPU, OS build, compiler, Asio version or commit (#352 open; the Boost review's conditional acceptance lists current, reproducible measurements as open). The multi-thread scaling harness loops poll()+restart() from several threads, which Asio's docs forbid, and the headline scaling claim rests on it. Dispatch benchmarks spawn trivial coroutines, not socket I/O, on different context types. The report contradicts itself: Asio coroutines lead the 1-thread scaling row (1.78 vs 1.72 Mops/s) and the 4 KB one-way gap is \~11-13%, not 'within 5%'. Real losses: 64 KB two-way throughput 2.5x slower (2.18 vs 5.56-5.74 GB/s) and Asio callbacks beat it single-threaded (2.59 vs 1.71 Mops/s). No tags or releases; Corosio and Capy consumed from develop. Gotchas: a default io_context on multi-core machines silently disables the inline fast path; lockless tiers make cross-thread posting UB; delay()/timeout() terminate on non-io_context executors.

## Caveats and trade-offs

Unusually candid report that documents losses as well as wins. Benchmark code is public (bench/), but the report states no CPU model, compiler or flags, so it is capped at tier C. Windows/IOCP only in this report. The default branch is develop; there is no main branch.

Socket I/O, latency and HTTP-server throughput are roughly equivalent to Asio; Asio still wins decisively on timer schedule/cancel throughput (10x) and large-buffer bidirectional socket throughput.

## Maintenance

Actively developed (created January 2026, last commit 2026-09-25) and BSL-1.0, but pre-release: no tags, both Corosio and Capy come from their develop branches, and Boost conditionally accepted it in September 2026 with an open item to make the benchmark report reproducible and current.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party report compares Corosio against Boost.Asio coroutines and callbacks, and the benchmark code is public in bench/corosio, bench/asio/coroutine and bench/asio/callback. The test environment says only 'Windows (IOCP backend)', with no CPU model, compiler or flags, so the entry cannot be tier A.
- **Verifier notes:** The recorded benchmark_url pointed at a main branch that does not exist (404), so it now points at develop; master holds an older copy with near-identical numbers. The record's claim that Asio's own maintainers maintain the project could not be verified (Asio lives at chriskohlhoff/asio), so it was removed from stars_or_usage. All other metadata checked out: BSL-1.0, not archived, not a fork, 84 stars, last commit 2026-09-25.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cppalliance/corosio>
  - <https://github.com/cppalliance/corosio/blob/main/doc/modules/ROOT/pages/benchmark-report.adoc>
  - <https://github.com/cppalliance/corosio/blob/develop/doc/modules/ROOT/pages/benchmark-report.adoc>
  - <https://github.com/cppalliance/corosio/blob/master/doc/modules/ROOT/pages/benchmark-report.adoc>
  - <https://github.com/cppalliance/corosio/tree/develop/bench>
- **Sources the enricher read:**
  - <https://github.com/cppalliance/corosio>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/README.md>
  - <https://github.com/cppalliance/corosio/blob/develop/doc/modules/ROOT/pages/benchmark-report.adoc>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/CMakeLists.txt>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/doc/modules/ROOT/pages/index.adoc>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/doc/scheduler.md>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/doc/research/dispatch.md>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/doc/queue.md>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/doc/modules/ROOT/pages/4.guide/4c.io-context.adoc>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/doc/modules/ROOT/pages/4.guide/4c2.configuration.adoc>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/doc/modules/ROOT/pages/4.guide/4b.concurrent-programming.adoc>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/doc/modules/ROOT/pages/4.guide/4h.timers.adoc>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/include/boost/corosio/native/detail/iocp/win_scheduler.hpp>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/bench/corosio/io_context_bench.cpp>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/bench/asio/coroutine/io_context_bench.cpp>
  - <https://raw.githubusercontent.com/cppalliance/corosio/develop/bench/asio/callback/io_context_bench.cpp>
  - <https://data.jsdelivr.com/v1/package/gh/cppalliance/corosio@develop/flat>
  - <https://github.com/cppalliance/corosio/issues>
  - <https://github.com/cppalliance/corosio/issues/352>
  - <https://github.com/cppalliance/corosio/issues/343>
  - <https://github.com/cppalliance/corosio/issues/297>
  - https://hn.algolia.com/api/v1/search?query=corosio&tags=(story,comment)
  - <https://hn.algolia.com/api/v1/items/48022121>
  - <https://lists.boost.org/archives/search?q=corosio+review+result>
  - <https://lists.boost.org/archives/search?q=Capy+Corosio+review+results+accepted>
  - <https://lists.boost.org/archives/list/boost@lists.boost.org/message/DRXACCXHE4RCRQHPPVXI56JT2V7CJMFD/>
  - <https://lists.boost.org/archives/list/boost@lists.boost.org/message/HGHEZ3ESO6A4SVQH7GUBVNIIAKR3H3XW/>
  - <https://lists.boost.org/archives/list/boost@lists.boost.org/message/562DYYORZ6VN6AFJ54YMP3EP357OOCKK/>
  - <https://www.boost.org/doc/libs/latest/doc/html/boost_asio/reference/io_context/restart.html>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/cppalliance/corosio`) · [data/wave5/enrich/raw/github_com_cppalliance_corosio.json](../../../data/wave5/enrich/raw/github_com_cppalliance_corosio.json) (enrichment confidence 0.72)

</details>
