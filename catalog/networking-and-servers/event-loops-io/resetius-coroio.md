# COROIO

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> C++23 coroutine networking library with compile-time epoll/kqueue/IOCP/io_uring backends; lower dispatch latency than libevent at small descriptor counts.

| | |
|---|---|
| **Beats** | libevent (epoll backend; libevent commit 4c993a0, its bench.c methodology) |
| **Claimed result** | No headline ratio in the README (results are charts); the raw result files in bench/ give p50 microseconds, lower is better. i7-12800H, 1 active connection, epoll: 64 us vs libevent 88 us at 1 descriptor (1.38x faster, derived from page data), 59 vs 92 at 4 descriptors (1.56x), 100 vs 95 at 1024 (coroio 5% slower), 110 vs 103 at 2048 (7% slower), 124 vs 129 at 131072 (parity). 100 active connections on the same CPU: 594 vs 955 us at 1 descriptor (1.61x), 879 vs 980 at 1024, but 1313 vs 1010 at 4096 and 1551 vs 1142 at 16384 (coroio 30-36% slower), parity at 65536 and above. i5-11400F (WSL2), 1 active, epoll: 47 vs 61 us at 1 descriptor, 78 vs 108 at 16384 (1.38x); 100 active: 1.17x to 1.74x faster across all sizes. Apple M1 kqueue, 1 active: 85 vs 100 us at 1 descriptor, 93 vs 137 at 16384 (1.47x). Separate actor-ring README table (i5-11400F, Ubuntu 25.04, author-run, against Akka, Caf and Ydb/actors rather than the listed baselines): local ring 442,151 msg/s vs Akka 473,966 (coroio slower), Caf 302,930, Ydb/actors 151,972; distributed ring 10 processes batch 1024 payload 0: 1,137,790 msg/s vs Ydb/actors 182,525, Caf 55,540, Akka 5,765. |
| **Workload** | libevent bench methodology: N pipe descriptors registered, then 1 active (or 100 active) connection passes 1-byte writes around the ring; p50 elapsed microseconds over 25 runs, epoll backend (coroio TEPoll vs libevent epoll), N from 1 to 131072. |
| **Metric** | latency |
| **Hardware** | Intel Core i7-12800H (Ubuntu 23.04, performance governor, isolcpus=10,11); Intel Core i5-11400F under WSL2 kernel 6.1.21.1; Apple M1 MacBook Air 16 GB macOS 12.6.3. |
| **Compiler and flags** | clang 16 on Ubuntu 23.04 for the i7-12800H run (README heading); optimization flags and CMAKE_BUILD_TYPE not stated (the root CMakeLists sets no default build type; the library target gets cxx_std_23 and -Wall -Wextra -Wpedantic -Werror). Benchmark program examples/bench.cpp, built as build/bench; the libevent side is build/bench-libevent, whose source and build are not in the repo. Taskset pinned to CPU 10 with isolcpus/nohz_full and the performance governor per bench/run.sh comments. |
| **Adoption** | 131 stars; used by miniraft-cpp and qumir (author's projects) |
| **Last commit** | 2026-08-06 |
| **Links** | [repository](https://github.com/resetius/coroio) · [benchmark](https://github.com/resetius/coroio/tree/master/bench) |

## Verdict

The author's port of libevent's bench.c (examples/bench.cpp) passes 1-byte writes around a ring of N descriptors and reports the p50 of 25 runs in microseconds; results from April-May 2023, CPU pinned with isolcpus, build flags not stated. On an i7-12800H (Ubuntu 23.04, clang 16) with epoll and 1 active connection, COROIO took 64 vs libevent's 88 us at 1 descriptor (1.38x) and 59 vs 92 at 4 (1.56x), was 5-7% slower at 1024-2048 and at parity near 131072; with 100 active it was 1.61x-1.87x faster from 1 to 256 descriptors (below 100 descriptors the 100 initial writes all land on the first pipe, in both harnesses) but 13-36% slower from 2048 to 32768, while the i5-11400F (WSL2) and M1 (kqueue) runs favor COROIO by up to 1.74x. COROIO's side uses pipe() pairs, while stock libevent bench.c uses AF_UNIX socketpairs with recv/send unless built with USE_PIPES, and the bench-libevent build is not in the repo, so the two sides may be timing different kernel primitives.

## Use it when

- Single-threaded C++23 servers or clients that want co_await-style I/O with the same code on Linux (epoll or io_uring), macOS/FreeBSD (kqueue) and Windows (IOCP).
- Event dispatch with few registered descriptors (1 to 256) where the author's i7-12800H epoll bench shows 1.11x-1.56x lower p50 latency than libevent with 1 active connection and 1.61x-1.87x with 100 active (derived from page data).
- Small services that also need DNS, an HTTP server, TLS or a lightweight actor system without pulling in Asio or Seastar (the author's miniraft-cpp Raft implementation uses it).
- Distributed actor messaging between processes: its README ring benchmark shows 1,137,790 msg/s vs 182,525 for Ydb/actors (author-run).

## Skip it when

- Thousands of registered descriptors with many active connections: on the i7-12800H with 100 active connections it is 13-36% slower than libevent from 2048 to 32768 descriptors.
- Multi-core scaling inside one process: the loop is single-threaded and there is no built-in multi-threaded scheduler.
- Toolchains without C++23 support (the library target requires cxx_std_23).
- Projects needing a WebSocket server, binary WebSocket frames or an HTTP client (WebSocket is client-only and text-only; HTTP client and server upgrade are open issues #131 and #130).
- Production use of io_uring with TLS or of connect error handling until open bugs #35 (io_uring+SSL assertion failure) and #93 (failed connect reported as success) are fixed.

## How it is fast

The poller is a template parameter, so the backend (TEPoll, TKqueue, TIOCp, TUring, TPoll, TSelect) is fixed at compile time with no virtual dispatch on the hot path. ReadSome/WriteSome try the non-blocking syscall first and only register with the poller on EAGAIN; registrations go into a change list applied in one batch at the start of each Poll, and an fd that the same coroutine re-arms keeps its epoll registration, so the steady state issues no epoll_ctl calls. Ready events resume the waiting coroutine handle directly instead of going through callback and event structures.

## Compared with alternatives

Pick COROIO over libhv or libev when you want coroutines rather than callbacks and one API across epoll, kqueue, IOCP and io_uring in a single-threaded loop; libhv is the better-measured choice for multi-threaded servers (its README beats both libevent and libuv at 1,000 connections). For Linux-only io_uring throughput, Condy or uring_exec carry their own measured wins, and Boost.Corosio is the choice inside a Boost/Asio codebase.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none required; optional liburing (io_uring backend) and OpenSSL (TLS) found via pkg-config; ws2_32 and bundled wepoll on Windows |
| **Minimum toolchain** | C++23 (cxx_std_23; TFuture stores results in std::expected), CMake 3.22; benchmarks built with clang 16 |
| **Platforms** | Linux (epoll, io_uring, poll, select), macOS and FreeBSD (kqueue, poll, select), Windows (IOCP, wepoll, poll, select) |
| **Thread safety** | Single-threaded event loop; no locking in the poller, so each loop and its sockets belong to one thread (actors also run one per thread) |
| **Drop-in for the baseline** | no |

## Gotchas

- TVoidTask silently swallows exceptions; use TFuture&lt;T&gt; when you need errors to propagate. ReadSome/WriteSome return -1 on transient errors (EAGAIN, EINTR) and throw std::system_error on others, so callers must handle both.
- The Linux epoll backend calls epoll_pwait2, a Linux 5.11+ syscall, so TEPoll will not work on older kernels.
- Closing a socket removes its registration but does not resume a coroutine still waiting on it (poller.hpp: 'TODO: resume waiting coroutines here'), so such a coroutine can stay suspended forever.
- TWebSocket holds a reference to the socket, which must outlive it.

## Known shortcomings

- No optimisation flags or build type; the bench-libevent source is not in the repo; p50 differences can be one rank apart. Slower than libevent at 512-2048 fds (1 active) and 13-36% slower at 2048-32768 fds (100 active) on the 12800H, and at 1024-2048 on the 11400F; the actor baselines (Akka, CAF, YDB) are not listed baselines.
- libevent comparison likely differs in transport (pipe vs socketpair, unproven); numbers from April-May 2023, not re-run

## Caveats and trade-offs

Author-run on three machines; first-party with partial methodology (flags and build type not stated), so tier C. Mixed result: on the i7-12800H libevent epoll is as fast or faster for 512 to 2048 descriptors (and at 8192 and 32768) with 1 active connection, and coroio is 13-36% slower for 2048 to 32768 descriptors with 100 active connections; the clear wins are at small descriptor counts and on the i5-11400F and M1. On the i5-11400F with 1 active connection coroio is also slightly slower at 1024 and 2048 descriptors (74 vs 70 us, 79 vs 73 us), and the libevent file has no values at 65536 and 131072. The libevent side is libevent's own bench.c built as bench-libevent (build flags and the program source are not in the repo); run_libevent.sh takes the 12th smallest output line while coroio's bench.cpp prints index 12 of 25 sorted runs (13th smallest), a one-rank difference that slightly favors libevent if it prints one line per run. Both sides measure pipe event dispatch, not real socket echo or HTTP serving. No comparison against Boost.Asio or libuv exists in the repo. The actor-ring numbers use baselines outside the listed set and Akka is faster on the local ring. Charts in the README are images; the numbers above were read from bench/\*.txt files and compared with a script (ratios derived from page data). [retier] Enricher: the libevent comparison likely differs in transport (libevent's bench-style harness over pipes against COROIO's socketpair setup; not proven from the code), so the per-descriptor ratios may mix transport costs with loop costs. Results date from April-May 2023 and were not re-run on the current code. With 100 active connections COROIO wins by up to 1.87x at 128 descriptors (derived from page data). Gotchas: the epoll backend calls epoll_pwait2 (Linux 5.11+); closing a socket does not resume a coroutine waiting on it (poller.hpp TODO), so it can stay suspended; TVoidTask swallows exceptions; ReadSome/WriteSome return -1 on EAGAIN/EINTR and throw std::system_error otherwise; TWebSocket keeps a reference to its socket.

Single-threaded event loop, C++23 required, coroutine frame allocation per task; pluggable backends (epoll, io_uring, kqueue, IOCP, poll, select). WebSocket is client-only, text frames only. No built-in multi-threading.

## Maintenance

Actively developed (last commit August 2026) and BSD-2-Clause, but the benchmark data dates from April-May 2023 and has not been re-run on the current code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** bench/ holds coroio and libevent p50 result files for three machines, the run scripts and examples/bench.cpp (25 runs, p50 of sorted microsecond timings); README names CPU and clang 16 for one machine, but no optimization flags or build type are stated anywhere and the bench-libevent program source is not in the repo, so first-party partial methodology: C.
- **Verifier notes:** All quoted p50 pairs and ratios re-derived from bench/netlib_\* and bench/libevent_\* files and match (1.38x at 1, 1.56x at 4, 1.61x 100-active at 1, 1.17-1.74x on 11400F 100-active, 1.47x M1 at 16384). Metadata matches: BSD-2-Clause, 131 stars, last commit 2026-08-06, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-83 (wave 5 book seed pass, 2026-10-24); enrichment (wave 5 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/resetius/coroio>
  - <https://github.com/resetius/coroio/commits>
  - <https://github.com/resetius/coroio/tree/master/bench>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/README.md>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/run.sh>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/run_libevent.sh>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/libevent_12800H_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/netlib_12800H_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/libevent_12800H_100_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/netlib_12800H_100_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/libevent_11400F_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/netlib_11400F_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/libevent_11400F_100_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/netlib_11400F_100_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/libevent_M1_kqueue.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/netlib_M1_kqueue.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/examples/CMakeLists.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/coroio/CMakeLists.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/examples/bench.cpp>
- **Sources the enricher read:**
  - <https://github.com/resetius/coroio>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/README.md>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/coroio/CMakeLists.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/coroio/socket.hpp>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/coroio/poller.hpp>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/coroio/loop.hpp>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/coroio/backends/epoll.hpp>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/coroio/backends/epoll.cpp>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/coroio/corochain.hpp>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/coroio/promises.hpp>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/examples/bench.cpp>
  - <https://raw.githubusercontent.com/resetius/coroio/ae9d389/examples/bench.cpp>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/run.sh>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/run_libevent.sh>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/netlib_12800H_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/libevent_12800H_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/netlib_12800H_uring.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/netlib_12800H_100_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/libevent_12800H_100_epoll.txt>
  - <https://raw.githubusercontent.com/resetius/coroio/HEAD/bench/netlib_12800H_100_uring.txt>
  - <https://github.com/resetius/coroio/tree/master/bench>
  - <https://github.com/resetius/coroio/commits/master/bench>
  - <https://github.com/resetius/coroio/commits/master/examples/bench.cpp>
  - <https://github.com/resetius/coroio/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/libevent/libevent/4c993a0/test/bench.c>
  - <https://raw.githubusercontent.com/libevent/libevent/master/test/bench.c>
  - <https://raw.githubusercontent.com/libevent/libevent/4c993a0/CMakeLists.txt>
  - <https://raw.githubusercontent.com/libevent/libevent/4c993a0/test/include.am>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/resetius/coroio`) · [data/wave5/enrich/raw/github_com_resetius_coroio.json](../../../data/wave5/enrich/raw/github_com_resetius_coroio.json) (enrichment confidence 0.75)

</details>
