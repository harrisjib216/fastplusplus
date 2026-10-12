# Rain

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Small header-only C++23 coroutine runtime for Linux: per-thread epoll loops with SO_REUSEPORT, \~1.13x Tokio req/s on one loopback test.

| | |
|---|---|
| **Beats** | Tokio |
| **Claimed result** | \~12.6% higher requests/sec than Tokio (247,283 req/s vs 219,543 req/s; \~1.13x derived from page data); also lower max latency (9.31 ms vs 18.45 ms) |
| **Workload** | Minimal loopback TCP server that writes a fixed HTTP/1.1 200 'Hello, World!' response per read (no HTTP parsing), driven by wrk -t4 -c256 -d15s on the same machine. Rain uses per-core shared-nothing loops with SO_REUSEPORT; Tokio uses the default #[tokio::main] multi-thread work-stealing runtime. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 5600H (6C/12T) |
| **Compiler and flags** | Rain: CMake CMAKE_BUILD_TYPE=Release, compiler/version not stated (README requires GCC 13+ or Clang 17+); Tokio side: cargo --release with lto=true, codegen-units=1 |
| **Adoption** | 22 stars |
| **Last commit** | 2026-06-25 |
| **Links** | [repository](https://github.com/wzxzhuxi/Rain) · [benchmark](https://github.com/wzxzhuxi/Rain/blob/main/README_EN.md) |

## Verdict

In one first-party loopback run on an AMD Ryzen 5 5600H (6C/12T), with wrk -t4 -c256 -d15s on the same host, Rain (4 SO_REUSEPORT loops, CMake Release, C++ compiler and version not stated) served a canned 'Hello, World!' HTTP/1.1 response at 247,283 req/s (max latency 9.31 ms) against 219,543 req/s (18.45 ms) for a default #[tokio::main] server built with cargo --release, LTO and codegen-units=1. The repo's own perf_matrix.sh says that default Tokio ran 12 workers to Rain's hard-coded 4, unpinned and without warmup, and its pinned thread-parity scenario has no published results; the README table was last edited 2026-04-29, before the June 2026 reactor and timer rewrites.

## Use it when

- Linux servers with many similar, short request/response connections (HTTP keep-alive, small RPCs) where SO_REUSEPORT's kernel distribution keeps the loops evenly loaded
- C++23 codebases that want coroutine networking from a small header-only runtime they can read end to end and vendor
- Targets that stay on plain epoll because io_uring is unavailable or not wanted
- Designs that want explicit placement (EventLoop::submit to a chosen loop) instead of a scheduler that migrates tasks on its own

## Skip it when

- Non-Linux targets: epoll, eventfd and signalfd are hard requirements
- Skewed load (a few heavy connections or CPU-bound handlers): with no work-stealing, a busy connection monopolises its loop while other cores sit idle
- Very high connection counts: every loop iteration runs std::erase_if over all live tasks, then takes a mutex and does an eventfd read() to drain the cross-core queue. The only published run used 256 connections
- Stacks that need TLS, HTTP parsing, UDP or an ecosystem. net/ has TCP only, and fs/ is file I/O on the blocking pool, whose queue is a mutex + condvar Channel that the code itself calls architecture debt
- Maturity-sensitive code: single author, no releases. Use-after-free bugs in block_on and in when_all/when_any, lost cross-core submits, and a timer cascade bug that fired timers a full wheel-lap late were fixed only in June 2026

## How it is fast

It is thread-per-core and shared-nothing: each loop binds its own SO_REUSEPORT listener (on by default), the kernel spreads incoming connections across them, and a task stays on the loop that accepted it, so there is no work-stealing and no cross-thread wakeup on the hot path. The reactor tries read()/write()/accept4() before suspending. Waiters are registered edge-triggered with EPOLLONESHOT in a vector indexed by fd instead of a hash map, so every blocked wait costs one epoll_ctl re-arm. The README attributes the gap over Tokio to skipping work-stealing and relying on kernel SO_REUSEPORT balancing.

## Compared with alternatives

Pick Rain for a small, readable C++23 thread-per-core coroutine runtime on plain epoll; if io_uring is allowed, Condy (header-only C++20 over io_uring) or uring_exec are the C++ options. If the goal is beating Tokio, monoio (\~1.9x Tokio peak echo QPS on 4 cores) and ringline carry much stronger evidence, and ringline's own 2x2 shows a per-core Tokio closes most of the gap, which suggests Rain's win over default Tokio is mostly a scheduler-configuration effect.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond pthreads and Linux headers (CMake INTERFACE target rain_core; there are no install/export rules, so use add_subdirectory or add src/ to the include path) |
| **Minimum toolchain** | C++23 with std::expected. The README says GCC 13+ or Clang 17+ and CMake 3.28+. CI builds with g++-14 and clang++-19, because the repo's CI notes say Clang 18 with libstdc++ 14 hides std::expected |
| **Platforms** | Linux only (epoll, eventfd, signalfd); no architecture-specific code seen; CI runs on GitHub's ubuntu-24.04 runner |
| **Thread safety** | Each EventLoop, with its reactor and timer, is single-threaded. EventLoop::submit(), request_stop() and request_graceful_stop() may be called from any thread (mutex + eventfd wakeup). Task cancellation runs stop_callbacks on the calling thread and touches the reactor, so task.hpp says callers must not request a task's stop from another core |
| **Drop-in for the baseline** | no |

## Gotchas

- ListenOptions defaults to reuse_port=true and backlog=128. A second copy of the server on the same port binds silently and splits the connections; the author's perf_matrix.sh warns about this 'silent stacking'. The benchmark raises backlog to 4096
- Executor::run() sets SIGPIPE to SIG_IGN for the whole process. Worker threads are not pinned to CPUs despite the 'per-core' naming, so use taskset or your own affinity code, as perf_matrix.sh does
- co_await on a Task&lt;T&gt; whose T is not a Result is undefined behavior if the task was cancelled (task.hpp says so). unhandled_exception() replaces any exception with a generic 'unhandled exception' error and loses the original
- The timer wheel ticks at 1 ms and documents a maximum delay of about 18.6 h, but schedule_at() neither clamps nor rejects longer delays, and the behavior for them is not documented

## Known shortcomings

- Unequal threads, which the author's own perf_matrix.sh admits: the README run pits default #[tokio::main] (12 workers on the 5600H) against Rain's 4, unpinned, no warmup, wrk sharing the server CPUs; the fair configuration the script defines has no published results, so the \~1.13x is mostly scheduler configuration. Rain also uses 4 SO_REUSEPORT listeners (backlog 4096) vs Tokio's single accept loop. The numbers (2026-04-29) predate the 2026-06 hardening fixes (use-after-free, lost cross-core submits, late timer cascade) and the reactor/timer rewrite. README reproduction steps build the wrong directory; toolchain claim (Clang 17+) conflicts with CI notes. No work-stealing; each loop iteration scans all live tasks; mutex+condvar blocking pool; SIGPIPE ignored process-wide; reuse_port on by default lets a second instance silently split traffic. One author, no releases, idle since 2026-06-25 (CI with sanitizers, fuzzing and soak is solid).

## Caveats and trade-offs

First-party benchmark with the wrk client on the same machine (loopback). The compiler and version used are not stated. There is one trivial workload: a fixed canned response, no parsing. The author attributes the win to avoiding work stealing, by relying on SO_REUSEPORT kernel balancing, against Tokio's default work-stealing runtime.

Per-core shared-nothing design with no work-stealing; relies on SO_REUSEPORT for kernel-level load balancing across cores instead of an application-level scheduler; Linux-only (epoll, eventfd, signalfd).

## Maintenance

Single-author and MIT-licensed, small enough to vendor; last commit 2026-06-25 (about three months ago) with no tags, releases or outside issues, though CI runs the tests under ASan/UBSan and TSan plus a libFuzzer job and a nightly TSan soak.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README_EN.md has a first-party table (Rain 247,283 vs Tokio 219,543 req/s, Ryzen 5 5600H). The bench code is public (benchmark/echo_bench.cpp, benchmark/tokio_echo, benchmark/run_bench.sh), but the C++ compiler and version are not stated (only 'Release'), so this is C, not A.
- **Verifier notes:** The numbers match README_EN.md exactly, and the Tokio baseline source is in the repo. The 'TCP echo' label is loose: both servers return a fixed HTTP response. License MIT, 22 stars and last commit 2026-06-25 all check out.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/wzxzhuxi/Rain>
  - <https://github.com/wzxzhuxi/Rain/blob/main/README_EN.md>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/benchmark/run_bench.sh>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/benchmark/tokio_echo/src/main.rs>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/benchmark/tokio_echo/Cargo.toml>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/benchmark/echo_bench.cpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/wzxzhuxi/Rain>
  - <https://github.com/wzxzhuxi/Rain/blob/main/README_EN.md>
  - <https://github.com/wzxzhuxi/Rain/blob/main/README.md>
  - <https://github.com/wzxzhuxi/Rain/tree/main/benchmark>
  - <https://github.com/wzxzhuxi/Rain/tree/main/test>
  - <https://github.com/wzxzhuxi/Rain/tree/main/.github/workflows>
  - <https://github.com/wzxzhuxi/Rain/tree/main/src/net>
  - <https://github.com/wzxzhuxi/Rain/pulls?q=is%3Apr>
  - <https://github.com/wzxzhuxi/Rain/commits/main.atom>
  - <https://github.com/wzxzhuxi/Rain/tags.atom>
  - <https://github.com/wzxzhuxi/Rain/commits/main/README_EN.md.atom>
  - <https://github.com/wzxzhuxi/Rain/commits/main/README.md.atom>
  - <https://github.com/wzxzhuxi/Rain/commits/main/benchmark/perf_matrix.sh.atom>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/LICENSE>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/benchmark/run_bench.sh>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/benchmark/perf_matrix.sh>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/benchmark/echo_bench.cpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/benchmark/tokio_echo/src/main.rs>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/benchmark/tokio_echo/Cargo.toml>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/async/task.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/async/event_loop.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/async/io_reactor.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/async/timer.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/runtime/runtime.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/runtime/executor.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/runtime/thread_pool.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/runtime/bridge.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/net/tcp_listener.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/net/tcp_stream.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/net/listen_options.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/net/listener_socket_ops.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/net/stream_io_ops.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/net/accept_awaiter.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/src/sync/channel.hpp>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/Dockerfile.ci>
  - <https://raw.githubusercontent.com/wzxzhuxi/Rain/main/scripts/ci.sh>
  - <https://wzxzhuxi.github.io/Rain/>
  - <https://wzxzhuxi.github.io/Rain/benchmark/>
  - <https://wzxzhuxi.github.io/Rain/install-and-usage/>
  - <https://wzxzhuxi.github.io/Rain/libraries/>
  - <https://hn.algolia.com/api/v1/search?query=wzxzhuxi%20Rain&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=%22C%2B%2B23%20async%20runtime%22>
  - <https://raw.githubusercontent.com/scylladb/seastar/master/README.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/wzxzhuxi/rain`) · [data/wave5/enrich/raw/github_com_wzxzhuxi_rain.json](../../../data/wave5/enrich/raw/github_com_wzxzhuxi_rain.json) (enrichment confidence 0.45)

</details>
