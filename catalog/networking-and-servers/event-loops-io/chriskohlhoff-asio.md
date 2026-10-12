# Asio io_uring backend (ASIO_HAS_IO_URING)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Opt-in io_uring backend inside Asio/Boost.Asio that replaces the epoll reactor on Linux 5.10+ without API changes.

| | |
|---|---|
| **Beats** | epoll |
| **Claimed result** | Linux 5.10, epoll: real 0m1.602s (user 0.563s, sys 1.039s); io_uring: real 0m1.158s (user 0.342s, sys 0.807s), about 1.38x faster wall-clock (derived from page data). The maintainer notes this excludes io_uring kernel worker-thread CPU, so total CPU use is higher than with epoll. |
| **Workload** | Single-threaded io_context: 100 pipe rings, each made of 3 pipes, pass a 13-byte message with async_read_some/async_write_some until each ring reaches 10000 iterations. Asio's epoll reactor is compared with its io_uring backend (ASIO_HAS_IO_URING, then on the io-uring-1 branch) on Linux 5.10. |
| **Metric** | latency |
| **Hardware** | CPU not stated; Linux 5.10 kernel |
| **Adoption** | 6.2k stars; widely used C++ networking library (basis of Boost.Asio) |
| **Last commit** | 2026-07-18 |
| **Links** | [repository](https://github.com/chriskohlhoff/asio) · [benchmark](https://github.com/chriskohlhoff/asio/issues/401) |

## Verdict

In a 2021 comment on issue #401, the maintainer ran a single-threaded io_context over 100 rings of 3 pipes, passing a 13-byte message until each ring reached 10,000 iterations: 1.602 s wall-clock with epoll vs 1.158 s with the pre-release io_uring backend (about 1.38x), on Linux 5.10 with CPU, compiler and flags not stated. The io_uring figure leaves out kernel worker-thread CPU, and a 2022 WSL2 rerun (kernel 5.10.102.1, Boost 1.79) found epoll faster.

## Use it when

- Existing Asio or Boost.Asio code on Linux 5.10+ where you want io_uring from a recompile rather than a rewrite, and to A/B test it against epoll by flipping two macros.
- A single-threaded io_context (concurrency_hint 1) driving many descriptors with small messages; the maintainer's test (300 pipes, 13-byte messages) finished about 1.38x faster in wall-clock time.
- Async file I/O through asio::stream_file / random_access_file, which require io_uring on Linux anyway.
- Workloads that can pre-register buffers (register_buffers), so reads and writes use io_uring's fixed-buffer READ_FIXED/WRITE_FIXED path.

## Skip it when

- When total CPU matters more than wall-clock time: the maintainer notes the benchmark leaves out io_uring kernel worker-thread CPU, and total CPU use was higher than with epoll.
- On virtualised or WSL2 hosts without measuring first: one user's WSL2 run of the same benchmark had epoll faster (2.97 s vs 3.66 s).
- A multi-threaded io_context on the default single ring: all threads share one SQ/CQ behind a mutex, and the maintainer said the backend works best single-threaded. Per-thread rings (reactor/io_uring_ring_count) only arrived in 1.38.2 (July 2026), and no published benchmark covers them.
- Timer-heavy code with io_uring as the default backend: open issues report a steady_timer firing only once (#1530) and a timer segfault (#1349), and #1235 reports UBSan errors when an io_context used with coroutines is destroyed.
- Non-Linux platforms or kernels older than 5.10: the build hits a compile-time #error below 5.10, and other OSes keep their usual backends.

## How it is fast

With epoll, each operation takes a readiness notification plus a separate read or write syscall. Here each async operation becomes a completion-based submission queue entry (SQE): IORING_OP_RECVMSG for receives, or READ_FIXED/WRITE_FIXED when buffers are registered. SQEs are batched: a posted submit operation flushes them, or they go out at once when 128 are pending (reactor/io_uring_submit_batch_size), so one io_uring_submit call covers many operations, and the run loop collects completions from the completion queue (CQ). An operation that returns would_block (for example, on an fd with O_NONBLOCK set) falls back to IORING_OP_POLL_ADD plus a non-blocking recv, which works like epoll.

## Compared with alternatives

Pick it when you already have Asio or Boost.Asio code and want io_uring without a rewrite. For new io_uring-first code, uring_exec reports 1.27x-3.46x the ping-pong throughput of Asio's io_uring backend, and Condy's recv benchmark only measured Asio's epoll path (1588 MB/s vs Condy's 2110 MB/s).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | liburing (headers at compile time, -luring at link time); Boost only if you use the Boost.Asio variant (BOOST_ASIO_HAS_IO_URING) |
| **Minimum toolchain** | C++11 (Asio 1.29+); Linux kernel headers 5.10+; liburing (the io_uring_iowait option needs liburing 2.12+ and kernel 6.15+) |
| **Platforms** | Linux 5.10+ only; the backend has no architecture-specific code |
| **Thread safety** | Same as Asio in general: an io_context may be run from several threads, and per-I/O-object locking is on by default (reactor/io_locking). By default all threads share one ring guarded by a mutex; from 1.38.2, reactor/io_uring_ring_count assigns each thread one of N rings, round-robin. |
| **Drop-in for the baseline** | partial — same Asio API and source, but the backend is chosen per build by macros (ASIO_HAS_IO_URING + ASIO_DISABLE_EPOLL), applies to the whole program, and the code has no runtime fallback to epoll |

## Gotchas

- Define ASIO_HAS_IO_URING the same way in every translation unit: it changes the recycling allocator's chunk_size (8 vs 4), and open issue #1635 reports a heap buffer overflow when units disagree. ASIO_ENABLE_VERSION_NAMESPACE puts the io_uring setting into the inline namespace name, so mismatched units do not share the same symbols.
- Per the docs, ASIO_DISABLE_EPOLL on its own forces select. Only together with ASIO_HAS_IO_URING does it make io_uring the default (ASIO_HAS_IO_URING_AS_DEFAULT), and ASIO_HAS_IO_URING alone leaves sockets on epoll.
- Each ring defaults to 16384 entries (reactor/io_uring_ring_size), which locks memory per ring; lower it where RLIMIT_MEMLOCK is small. If io_uring_queue_init fails, the service throws instead of falling back to epoll.
- By default a thread waiting on the ring counts as iowait whenever SQEs are pending, including socket polls and timers, which inflates iowait metrics. Set reactor/io_uring_iowait=false (needs liburing 2.12+ and kernel 6.15+).

## Known shortcomings

- Only evidence is a 2021 maintainer issue comment (\~1.38x on a pipe-ring workload, Linux 5.10) with no CPU, compiler or flags; another commenter found epoll faster under WSL2. Opt-in via ASIO_HAS_IO_URING.
- The io_uring time excludes kernel worker-thread CPU (the maintainer says total CPU was higher than epoll). Open correctness issues: heap overflow when translation units disagree on ASIO_HAS_IO_URING (#1635), timer fires once (#1530), timer segfault (#1349). Compile-time selection with no runtime fallback if io_uring_queue_init fails.

## Caveats and trade-offs

The numbers come from a 2021 GitHub issue comment by Asio's maintainer, run on the pre-release io-uring-1 branch, and are not a dedicated benchmark file. CPU model, compiler and flags are not stated, and the benchmark source is inline in the comment. The io_uring time excludes io_uring kernel worker-thread CPU, so overall CPU use is higher than epoll. A WSL2 run (kernel 5.10.102.1, Boost 1.79) by another commenter showed epoll faster (2.97s vs 3.66s elapsed). The backend is opt-in (ASIO_HAS_IO_URING, plus ASIO_DISABLE_EPOLL for sockets), and the maintainer said it worked best with a single-threaded io_context.

Original single-threaded-only limitation and multi-threaded io_context instability under Linux 5.13 noted by maintainer at time of posting; io_uring backend now merged into asio mainline (io_uring_service.hpp etc. present) but is opt-in via ASIO_HAS_IO_URING; a third commenter (WSL2, kernel 5.10.102) reported epoll actually faster than io_uring in their environment, showing result is not universal

## Maintenance

Actively maintained and BSL-1.0 licensed: the io_uring backend has shipped opt-in since Asio 1.21.0, 1.38.2 (July 2026) added multi-ring and batching settings, and one user reports four years of production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** In issue #401, maintainer chriskohlhoff (2021-08-20) posts the full benchmark source and time output for Asio's epoll reactor against its io_uring backend on Linux 5.10. No CPU model, compiler or flags are given, so these are first-party numbers with partial methodology, which is tier C.
- **Verifier notes:** Numbers match the maintainer's comment; the stated 1.4x is 1.602/1.158 = 1.38x. The metric is wall-clock time for a fixed workload rather than per-operation latency (metric is not a correctable field). License: the GitHub API returns NOASSERTION, but COPYING and LICENSE_1_0.txt are the Boost Software License 1.0, so BSL-1.0 and copyable are correct. Last commit 2026-07-18 and 6204 stars confirmed; the repo is not a fork and not archived.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/chriskohlhoff/asio>
  - <https://github.com/chriskohlhoff/asio/issues/401>
  - <https://github.com/chriskohlhoff/asio/blob/master/COPYING>
  - <https://github.com/chriskohlhoff/asio/blob/master/LICENSE_1_0.txt>
- **Sources the enricher read:**
  - <https://github.com/chriskohlhoff/asio>
  - <https://github.com/chriskohlhoff/asio/blob/master/README>
  - <https://github.com/chriskohlhoff/asio/issues/401>
  - <https://github.com/chriskohlhoff/asio/blob/master/src/doc/overview/implementation.qbk>
  - <https://github.com/chriskohlhoff/asio/blob/master/src/doc/overview/configuration.qbk>
  - <https://github.com/chriskohlhoff/asio/blob/master/src/doc/overview/files.qbk>
  - <https://github.com/chriskohlhoff/asio/blob/master/src/doc/history.qbk>
  - <https://github.com/chriskohlhoff/asio/blob/master/src/doc/using.qbk>
  - <https://github.com/chriskohlhoff/asio/blob/master/include/asio/detail/config.hpp>
  - <https://github.com/chriskohlhoff/asio/blob/master/include/asio/detail/io_uring_service.hpp>
  - <https://github.com/chriskohlhoff/asio/blob/master/include/asio/detail/impl/io_uring_service.ipp>
  - <https://github.com/chriskohlhoff/asio/blob/master/include/asio/detail/io_uring_socket_recv_op.hpp>
  - <https://github.com/chriskohlhoff/asio/blob/master/include/asio/detail/thread_info_base.hpp>
  - <https://github.com/chriskohlhoff/asio/issues/1635>
  - <https://github.com/chriskohlhoff/asio/issues/1530>
  - <https://github.com/chriskohlhoff/asio/issues/1349>
  - <https://github.com/chriskohlhoff/asio/issues/1235>
  - <https://github.com/chriskohlhoff/asio/issues/1633>
  - <https://github.com/chriskohlhoff/asio/issues/1744>
  - <https://github.com/chriskohlhoff/asio/issues/1754>
  - <https://github.com/chriskohlhoff/asio/issues/965>
  - <https://github.com/Caturra000/uring_exec>
  - <https://github.com/condy-cpp/condy/blob/master/docs/bench.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/chriskohlhoff/asio`) · [data/wave5/enrich/raw/github_com_chriskohlhoff_asio.json](../../../data/wave5/enrich/raw/github_com_chriskohlhoff_asio.json) (enrichment confidence 0.55)

</details>
