# uring_exec

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MPL-2.0` · 🟢 active

> Header-only liburing adapter for stdexec (std::execution) senders; beats Asio's io_uring backend on loopback TCP ping-pong.

| | |
|---|---|
| **Beats** | Boost.Asio (io_uring backend) |
| **Claimed result** | 1.27x-3.46x ping-pong throughput over Asio's io_uring backend across the 9 thread/session combos in the README (derived from page data). Examples: 4 threads/1000 sessions 4.411 vs 1.275 GiB/s (\~3.46x); 8 threads/1000 sessions 3.956 vs 1.177 (\~3.36x); 2 threads/10 sessions 3.409 vs 1.868 (\~1.82x); smallest gain 8 threads/100 sessions 2.676 vs 2.107 (\~1.27x). |
| **Workload** | ping-pong network test, blocksize 16384 bytes, timeout 5s, varying thread count (2/4/8) and concurrent session count (10/100/1000) |
| **Metric** | throughput |
| **Hardware** | AMD 5800H, 16 GB RAM, Linux v6.4.8 |
| **Compiler and flags** | gcc v13.2.0 -O3 |
| **Adoption** | 19 stars |
| **Last commit** | 2026-05-01 |
| **Links** | [repository](https://github.com/Caturra000/uring_exec) · [benchmark](https://github.com/Caturra000/uring_exec/blob/master/README.md) |

## Verdict

Loopback TCP ping-pong on one AMD 5800H box (Linux 6.4.8, GCC 13.2 -O3, 16 KiB blocks, 5 s): a uring_exec echo server beat an Asio coroutine echo server built with ASIO_HAS_IO_URING and ASIO_DISABLE_EPOLL by 1.27x-3.46x across 2/4/8 threads and 10/100/1000 sessions (e.g. 4 threads/1000 sessions: 4.411 vs 1.275 GiB/s). The client was uring_exec's own ping in both cases, and there was one run per cell with no variance reported. A newer 10 s table in benchmarks/README adds Asio on epoll, which beats uring_exec at 10-100 sessions with 2+ threads.

## Use it when

- Your code base already uses stdexec/P2300 senders and you want Linux socket or file I/O as composable senders with stop-token cancellation and when_any timeouts.
- Many concurrent TCP connections (1,000-100,000) served by several threads on one box. The author's newer table has it beating Asio epoll there, e.g. 8 threads/10,000 sessions 6.662 vs 2.118 GiB/s.
- A single-threaded event loop: at 1 thread it beat both Asio backends at every session count in the author's table (e.g. 100 sessions: 4.026 vs 3.600 io_uring, 3.052 epoll GiB/s).
- You can give the event loop dedicated cores, because the default run loop polls and yields rather than blocking.
- As a small, readable reference (about 1,600 lines of headers) for mapping io_uring onto sender/receiver before writing your own.

## Skip it when

- Few connections spread over several threads. In 5 of the 6 rows with 10-100 sessions and 2-8 threads, Asio's default epoll backend was 1.4-3.2x faster in the author's own table (4 threads/100 sessions: 8.744 vs 3.226 GiB/s), and the author says io_uring cannot beat epoll on the current kernel.
- Production services that need a maintained dependency: the README calls it effectively archived since 2025, there is one author, the repo has only two test files and no CI config, and the build follows stdexec main, whose upstream changes have broken compilation (issue #2, the 2026-05 fix commit, a \~10x compile-time regression noted for ping_when_any).
- You need TLS, DNS or higher-level socket types. The API is raw file descriptors, and the author says in issue #3 that async OpenSSL is out of scope (workarounds: poll-based SSL or kTLS).
- You want advanced io_uring features: the sender list has no multishot accept/recv, provided buffer rings, registered files/buffers or zero-copy send.
- Non-Linux targets, kernels older than about 6.1 (the recommended minimum), or environments where io_uring is disabled. Also workloads that cancel every I/O, since per-operation cancellation adds overhead according to the benchmarks README.

## How it is fast

Each thread that calls run() lazily gets its own thread-local io_uring ring, created with IORING_SETUP_SINGLE_ISSUER and IORING_SETUP_COOP_TASKRUN, and all rings share one kernel worker pool through IORING_SETUP_ATTACH_WQ. Operation states are immovable and intrusive, with a per-object vtable for type erasure, and the CQE user_data points straight at them, so the library itself does no per-I/O heap allocation. Work scheduled from other threads goes through lock-free CAS intrusive queues split into 16 buckets that run threads drain by round-robin plus random pick. The default run loop submits without blocking, harvests completions in batches with io_uring_peek_batch_cqe (64 per batch, up to 512 per step) and calls yield() when idle instead of sleeping in the kernel. The author gives no explanation of why this beats Asio.

## Compared with alternatives

Pick uring_exec when you specifically want io_uring exposed as std::execution senders. For a maintained C++20-coroutine io_uring runtime that aims to cover most io_uring features and also posts wins over epoll and Asio, Condy is the safer choice. At low connection counts, stock Asio on epoll (or PhotonLibOS, which edges out boost::asio in its own ping-pong) is faster than uring_exec according to the author's own data.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | stdexec (NVIDIA, tracked at main), liburing (link -luring, recent enough for io_uring_prep_futex_wait/bind), pthread; Asio only for the comparison benchmark |
| **Minimum toolchain** | C++20; benchmarked with GCC 13.2; the benchmarks README says Clang also works (there is a clang-19 workaround commit) |
| **Platforms** | Linux only (io_uring), kernel 6.1+ recommended; architecture support not documented (benchmarked on x86-64 AMD 5800H) |
| **Thread safety** | io_uring_exec is documented as MT-safe: any number of threads may call run() on one instance and schedule work from any thread. Each run thread owns a thread-local ring. |
| **Drop-in for the baseline** | no |

## Gotchas

- The default run() never blocks in the kernel. It calls io_uring_submit without waiting, peeks the CQ and calls std::this_thread::yield() when nothing moved, so each run thread keeps a core busy even when idle. run_policy{.waitable=true} switches to io_uring_submit_and_wait.
- An I/O sender submits its SQE to the thread-local ring of whichever thread calls start(). Hop onto the scheduler first (stdexec::schedule or starts_on, as every example does), or the operation sits in a ring that no run() loop drains.
- Thread-local rings are keyed by the io_uring_exec constructor's call site through a template lambda parameter. The header warns that constructing it repeatedly at one site (e.g. in a loop) reuses the same per-thread ring, so treat it as a long-lived singleton. The constructor is noexcept, but ring setup throws std::system_error on failure, which means std::terminate if io_uring is unavailable.
- async_read/async_write default to offset 0, so on a seekable file every call hits byte 0 unless you pass an offset. Errors arrive as set_error(exception_ptr to std::system_error), and -ECANCELED arrives as set_stopped.

## Known shortcomings

- Beats Asio's io_uring backend (1.27-3.46x) but Asio on its default epoll backend beats uring_exec at low session counts (4 threads/100 sessions: 8.744 vs 3.226 GiB/s); the author says io_uring cannot beat epoll on the current kernel and calls the project effectively archived since 2025.
- Loopback benchmark with uring_exec's own client; its run() loop busy-polls (keeps a core busy when idle) while Asio threads block; single runs, no variance. Against Asio on epoll it loses in 5 of 6 rows at 10-100 sessions with 2-8 threads (epoll 1.4-3.2x faster). No TLS or multishot/zero-copy; noexcept constructor terminates if io_uring is unavailable.

## Caveats and trade-offs

The win is only against Asio's opt-in io_uring backend (built with ASIO_DISABLE_EPOLL). The newer table in benchmarks/README adds Asio on its default epoll backend, which beats uring_exec at low session counts (e.g. 4 threads/100 sessions: epoll 8.744 vs uring_exec 3.226 GiB/s), and the author writes that io_uring cannot beat epoll on the current kernel; uring_exec only wins at 1000+ sessions with several threads. Single author-run results with no repeated trials or variance. The README says the project has been effectively archived since 2025, with occasional commits only to track stdexec changes.

Linux io_uring only; ports liburing onto C++26 std::execution (stdexec), so requires stdexec + liburing; asio comparison uses asio's own io_uring backend not epoll, so gain is from sender/receiver design not from switching kernel API; niche/experimental, single author benchmark, exact commit hashes pinned (uring_exec 22a6674, asio 62481a2) so numbers are reproducible but old snapshots

## Maintenance

The author declares it effectively archived since 2025 (the last commit, 2026-05-01, only follows stdexec API renames); it is header-only and MPL-2.0, so it is easy to vendor, but you inherit stdexec churn yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now A.
- **Tier reason:** The README Benchmark table runs uring_exec against Asio built with -DASIO_HAS_IO_URING -DASIO_DISABLE_EPOLL, and states Linux 6.4.8, the AMD 5800H CPU and gcc 13.2.0 -O3. The benchmark code is public (benchmarks/ping.cpp, pong.cpp, pong_asio.cpp, driven by benchmarks/pingpong.py), and xmake.lua and the Makefile add -O3 to the benchmark targets, so tier A holds.
- **Verifier notes:** Claim overstated: the README rows give 1.27x-3.46x, not 1.6x-4.3x, so claimed_speedup is corrected and the verdict is downgrade while tier A stays. maintenance_status corrected from stale to active because the last commit (2026-05-01) is under 12 months old, though the author calls the project effectively archived. Metadata checked: MPL-2.0, not a fork, not archived, 19 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Caturra000/uring_exec>
  - <https://github.com/Caturra000/uring_exec/blob/master/README.md>
  - <https://github.com/Caturra000/uring_exec/blob/master/benchmarks/README>
  - <https://github.com/Caturra000/uring_exec/blob/master/benchmarks/pingpong.py>
  - <https://github.com/Caturra000/uring_exec/blob/master/benchmarks/pong_asio.cpp>
  - <https://github.com/Caturra000/uring_exec/blob/master/xmake.lua>
  - <https://github.com/Caturra000/uring_exec/blob/master/Makefile>
- **Sources the enricher read:**
  - <https://github.com/Caturra000/uring_exec>
  - <https://github.com/Caturra000/uring_exec/blob/master/README.md>
  - <https://github.com/Caturra000/uring_exec/blob/master/benchmarks/README>
  - <https://github.com/Caturra000/uring_exec/blob/master/benchmarks/pingpong.py>
  - <https://github.com/Caturra000/uring_exec/blob/master/benchmarks/ping.cpp>
  - <https://github.com/Caturra000/uring_exec/blob/master/benchmarks/pong.cpp>
  - <https://github.com/Caturra000/uring_exec/blob/master/benchmarks/pong_asio.cpp>
  - <https://github.com/Caturra000/uring_exec/blob/master/xmake.lua>
  - <https://github.com/Caturra000/uring_exec/blob/master/Makefile>
  - <https://github.com/Caturra000/uring_exec/blob/master/include/uring_exec.hpp>
  - <https://github.com/Caturra000/uring_exec/blob/master/include/uring_exec/io_uring_exec.h>
  - <https://github.com/Caturra000/uring_exec/blob/master/include/uring_exec/io_uring_exec_internal.h>
  - <https://github.com/Caturra000/uring_exec/blob/master/include/uring_exec/io_uring_exec_internal_run.h>
  - <https://github.com/Caturra000/uring_exec/blob/master/include/uring_exec/io_uring_exec_operation.h>
  - <https://github.com/Caturra000/uring_exec/blob/master/include/uring_exec/io_uring_exec_sender.h>
  - <https://github.com/Caturra000/uring_exec/blob/master/include/uring_exec/underlying_io_uring.h>
  - <https://github.com/Caturra000/uring_exec/blob/master/include/uring_exec/detail.h>
  - <https://github.com/Caturra000/uring_exec/blob/master/include/uring_exec/utils.h>
  - <https://github.com/Caturra000/uring_exec/commits/master>
  - <https://github.com/Caturra000/uring_exec/commit/e1e0bb47d4464f7ed3510574a6c9945e9ace4965>
  - <https://github.com/Caturra000/uring_exec/issues/1>
  - <https://github.com/Caturra000/uring_exec/issues/2>
  - <https://github.com/Caturra000/uring_exec/issues/3>
  - <https://www.bluepuni.com/archives/porting-liburing-to-stdexec/>
  - <https://github.com/condy-cpp/condy>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/caturra000/uring_exec`) · [data/wave5/enrich/raw/github_com_caturra000_uring_exec.json](../../../data/wave5/enrich/raw/github_com_caturra000_uring_exec.json) (enrichment confidence 0.8)

</details>
