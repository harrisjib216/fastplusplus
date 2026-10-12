# io_uring-echo-server (frevib)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Single-threaded \~200-line C TCP echo server on liburing, benchmarked in 2020 against the same author's minimal epoll echo server.

| | |
|---|---|
| **Beats** | epoll |
| **Claimed result** | 128-byte messages, req/s: io_uring peaks at 216,637 (300 clients) vs epoll's peak of 152,561 (150 clients), \~1.4x; at 1000 clients, io_uring 173,343 vs epoll 108,380, \~1.6x (ratios derived from page data). With 1 client the two are equal (13,093 vs 13,177). The 512- and 1000-byte tables show similar margins. |
| **Workload** | TCP echo server requests/second vs number of concurrent clients (1-1000) and message sizes (128/512/1000 bytes), using the rust_echo_bench load generator, comparing a minimal io_uring (IORING_FEAT_FAST_POLL) echo server against a minimal epoll echo server by the same author |
| **Metric** | throughput |
| **Hardware** | MacBook Pro host: 6 cores, 2.6 GHz, 32 GB RAM (CPU model not named). Guest: VMware Ubuntu 18.04 with 8 GB RAM and 6 vcores (3 physical cores), Linux 5.6.0-rc1+ with IORING_FEAT_FAST_POLL (io_uring-task-poll branch). 2 vcores (one physical core) isolated with isolcpus=0,1, with the echo server pinned to CPU 0 via taskset. |
| **Compiler and flags** | Both servers are built with -Wall -O2 -D_GNU_SOURCE: the io_uring Makefile on branch io-uring-feat-fast-poll has CCFLAGS ?= -Wall -O2 -D_GNU_SOURCE -luring against the bundled liburing, and the frevib/epoll-echo-server Makefile runs gcc -Wall -O2 -D_GNU_SOURCE. The compiler version is not stated. The client (rust_echo_bench) is run with cargo run --release. |
| **Adoption** | 400 stars; linked in at least 7 Hacker News comments across io_uring threads from 2020 to 2025 (HN Algolia API); the Twitter references could not be checked |
| **Last commit** | 2024-01-20 |
| **Links** | [repository](https://github.com/frevib/io_uring-echo-server) · [benchmark](https://github.com/frevib/io_uring-echo-server/blob/io-uring-feat-fast-poll/benchmarks/benchmarks.md) |

## Verdict

In February 2020 the io-uring-feat-fast-poll build (gcc -O2, compiler version unstated) served a peak of 216,637 req/s at 300 clients with 128-byte messages, against a peak of 152,561 for the author's epoll server (about 1.4x). At 1000 clients the gap was about 1.6x (173,343 vs 108,380), and at 1 client the two were equal. Each server was pinned to one isolated vCPU in a VMware Ubuntu 18.04 guest (patched Linux 5.6.0-rc1+) on a 6-core 2.6 GHz MacBook Pro. Load came from rust_echo_bench, a thread-per-connection blocking client doing 60-second closed-loop ping-pong runs on the same VM. Independent re-runs on Linux 5.8 in issue #8 did not reproduce the gap.

## Use it when

- Learning io_uring networking: a short, readable reference for an accept/recv/send completion loop, packing state into the 64-bit user_data, and provided buffers.
- As the starting point for your own epoll-vs-io_uring A/B test on your own kernel and hardware, using the paired epoll-echo-server and rust_echo_bench. Plan to re-measure rather than trust the 2020 numbers.
- Checking whether syscall batching helps a single-core ping-pong workload with hundreds of concurrent connections and small (128-1000 B) messages. That is where the 2020 page showed the gap (about 1.4-1.6x at 150-1000 clients), with no gain at 1 client.
- Linux 5.7+ hosts only. Master exits at startup if IORING_FEAT_FAST_POLL or IORING_OP_PROVIDE_BUFFERS is missing.

## Skip it when

- Production serving. The author calls it 'only a bare minimum show case for io_uring... don't expect production-grade stability' (issue #17). It does not handle short sends, never checks io_uring_get_sqe for NULL, and calls exit(1) on -ENOBUFS.
- Relying on the claimed speedup. In issue #8 (open since 2020, 26 comments), three independent commenters could not reproduce it. On Linux 5.8 (Fedora Rawhide; a 4-vCPU GCP VM), io_uring was equal to or slower than epoll, e.g. 227k vs 235k req/s, or within about +/-2k req/s with the winner alternating. The author replied that results 'most likely are different now'.
- More than about 1000 concurrent clients. Issue #17 reports master crashing every time above 1100 clients on a 16-core AWS instance, and the benchmark page says both servers crash above about 2000 clients.
- Multi-core scaling: it uses one thread and one ring with global buffers, and has no multi-threaded or SO_REUSEPORT mode.
- As an example of current best-practice io_uring. It predates ring-mapped provided buffers (io_uring_register_buf_ring, Linux 5.19+) and multishot accept/recv (5.19/6.0), so it neither shows nor measures those.

## How it is fast

The epoll server calls epoll_wait and then does one recv() and one send() syscall per ready socket. The io_uring server queues accept/recv/send SQEs and submits a whole batch with one io_uring_enter per loop iteration; an strace in issue #8 shows about 60 SQEs submitted per call. It relies on IORING_FEAT_FAST_POLL: a recv on a socket with no data stays pending in the kernel and completes when data arrives, so the loop issues no separate poll requests (README v1.5: 'Remove all polling'). Master also switched to kernel-selected provided buffers (IORING_OP_PROVIDE_BUFFERS), which adds an extra provide-buffers SQE per message; the author says this lowered throughput, and the published numbers are from the earlier per-fd-buffer branch.

## Compared with alternatives

Pick it only to study raw liburing socket calls in about 200 lines, or to seed a controlled io_uring-vs-epoll experiment. For anything that ships, monoio (Rust, thread-per-core) or PhotonLibOS (C++) are maintained io_uring runtimes with their own benchmarks (monoio vs Tokio/epoll on 4 cores; Photon vs boost::asio).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | liburing: a system install on master (the bundled copy was removed in 2021); the benchmarked io-uring-feat-fast-poll branch bundles its own liburing copy (liburing.spec there says 0.6) |
| **Minimum toolchain** | C99 (designated initializers, for-loop declarations); built with \$(CC) -Wall -O2 -D_GNU_SOURCE, and no compiler version is documented. Kernel: Linux 5.7+ for master; the benchmark ran on a patched 5.6.0-rc1+ (io_uring-task-poll branch) |
| **Platforms** | Linux only; no architecture-specific code (the benchmark ran on x86-64) |
| **Thread safety** | Single-threaded event loop with global buffer arrays and one ring; multi-threaded use is not supported or documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The published numbers come from the io-uring-feat-fast-poll branch, not master. That branch indexes fixed per-connection buffers and state by fd number (bufs[fd], conns[fd], 4096 slots, no bounds check). It also calls shutdown() but never close() on disconnect, so fds grow without limit until they overrun those arrays. Master fixed the fd leak in PR #14 (2022); the epoll baseline has the same shutdown-without-close pattern.
- On the benchmarked branch the listen socket is SOCK_NONBLOCK, so an io_uring accept can complete with -EAGAIN. The code then queues a recv on that negative 'fd', indexing conns[] out of bounds, and re-arms accept. PR #6 (merged into master in 2020) says this caused extra CQEs on every loop and suggests it, plus a small queue, may explain the 'uninterruptible sleep' hang the benchmark page reports. The hang was never resolved.
- On master, a read that fails or hits EOF re-provides the buffer ID taken from cqe-&gt;flags &gt;&gt; 16 without checking IORING_CQE_F_BUFFER. Buffer 0 can then be handed to two connections at once, and one client receives another's data (issue #23; fix PR #24 unmerged since June 2025).
- Issue #9 argues the comparison is not like for like: the epoll server does recv/send serially on one thread, while io_uring SQEs may run concurrently on kernel iou-wrk worker threads. The page reports only req/s, not the total CPU used by either server.

## Known shortcomings

- Benchmarks the io-uring-feat-fast-poll branch, not master; the page reports the io_uring server locking up under sustained load. An echo-server demonstration, not a library.
- Not reproduced: in issue #8 three independent testers found io_uring equal to or slower than epoll on Linux 5.8. The benchmarked branch indexes buffers by fd without bounds checks and leaks fds; master has an open buffer-sharing data-corruption bug (#23) and crashes above \~1100 clients (#17). The author calls it a 'bare minimum show case'. Better as a learning reference than a performance claim.

## Caveats and trade-offs

Both servers were written by the same author to isolate epoll vs io_uring. The CPU model and compiler version are not stated, and the run was in a VMware VM on a laptop. The benchmark dates from 2020-02-29 on a pre-mainline IORING_FEAT_FAST_POLL kernel (5.6.0-rc1+), so it may not reflect current io_uring. It covers the io-uring-feat-fast-poll branch; master moved to IORING_OP_PROVIDE_BUFFERS (Linux 5.7+) and the README labels the page 'without buffer selection'. The page reports that the io_uring server became unresponsive (uninterruptible sleep) under sustained load and had to be restarted between message sizes, while the epoll server had no such problem. Both servers crash above \~2000 clients.

At the time of writing, the io_uring echo server needed a per-connection buffer indexed by file descriptor number (segfault risk at high fd counts) and became unresponsive under sustained load with &gt;2000 clients; the epoll counterpart did not show these issues

## Maintenance

Stale: the last commit (2024-01-20) was a small bug fix (PR #20), and the author says the project is 'quite stale' and he will only merge fixes. It is MIT-licensed and small enough to copy as a teaching skeleton, but it is not something to depend on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** benchmarks/benchmarks.md (io-uring-feat-fast-poll branch, Feb 2020) has req/s tables for the io_uring server and the author's epoll server (frevib/epoll-echo-server) at 1-1000 clients and 128/512/1000-byte messages. The claimed peaks (216,637 vs 152,561) and 1000-client figures (173,343 vs 108,380) are there. The code and flags are public (both Makefiles use -Wall -O2 -D_GNU_SOURCE; the client is rust_echo_bench, and a run script is on the page), but there is no compiler version or CPU model (only 'Macbook pro 6-core 2,6 GHz' under a VMware VM), so this is first-party C.
- **Verifier notes:** The numbers match the page exactly. The tier stays C: the code and -O2 flags are public, but there is no compiler version and no CPU model. The fixes are the '(derived from page data)' marking, the server flags (the record said they were unstated; both Makefiles have -O2), and the hardware detail. The metadata checks out (MIT, 400 stars, not a fork or archived, last commit 2024-01-20, stale). The epoll baseline repo is also MIT (53 stars, last pushed 2020-02-29).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/frevib/io_uring-echo-server/blob/io-uring-feat-fast-poll/benchmarks/benchmarks.md>
  - <https://github.com/frevib/io_uring-echo-server>
  - <https://github.com/frevib/io_uring-echo-server/blob/master/README.md>
  - <https://github.com/frevib/io_uring-echo-server/blob/master/Makefile>
  - <https://github.com/frevib/io_uring-echo-server/blob/io-uring-feat-fast-poll/Makefile>
  - <https://github.com/frevib/epoll-echo-server>
  - <https://github.com/frevib/epoll-echo-server/blob/master/Makefile>
  - <https://hn.algolia.com/api/v1/search?query=frevib%2Fio_uring-echo-server&restrictSearchableAttributes=url>
  - <https://hn.algolia.com/api/v1/search?query=%22io_uring-echo-server%22&tags=comment>
- **Sources the enricher read:**
  - <https://github.com/frevib/io_uring-echo-server>
  - <https://github.com/frevib/io_uring-echo-server/blob/master/README.md>
  - <https://github.com/frevib/io_uring-echo-server/blob/master/io_uring_echo_server.c>
  - <https://github.com/frevib/io_uring-echo-server/blob/master/Makefile>
  - <https://github.com/frevib/io_uring-echo-server/blob/io-uring-feat-fast-poll/benchmarks/benchmarks.md>
  - <https://github.com/frevib/io_uring-echo-server/blob/io-uring-feat-fast-poll/io_uring_echo_server.c>
  - <https://github.com/frevib/io_uring-echo-server/blob/io-uring-feat-fast-poll/Makefile>
  - <https://github.com/frevib/io_uring-echo-server/blob/io-uring-feat-fast-poll/README.md>
  - <https://github.com/frevib/io_uring-echo-server/blob/io-uring-feat-fast-poll/liburing/liburing.spec>
  - <https://github.com/frevib/io_uring-echo-server/commits/master>
  - <https://github.com/frevib/io_uring-echo-server/commit/a42497e>
  - <https://github.com/frevib/io_uring-echo-server/issues>
  - <https://github.com/frevib/io_uring-echo-server/issues/3>
  - <https://github.com/frevib/io_uring-echo-server/issues/5>
  - <https://github.com/frevib/io_uring-echo-server/issues/8>
  - <https://github.com/frevib/io_uring-echo-server/issues/9>
  - <https://github.com/frevib/io_uring-echo-server/issues/11>
  - <https://github.com/frevib/io_uring-echo-server/issues/13>
  - <https://github.com/frevib/io_uring-echo-server/issues/17>
  - <https://github.com/frevib/io_uring-echo-server/issues/21>
  - <https://github.com/frevib/io_uring-echo-server/issues/23>
  - <https://github.com/frevib/io_uring-echo-server/pull/2>
  - <https://github.com/frevib/io_uring-echo-server/pull/6>
  - <https://github.com/frevib/io_uring-echo-server/pull/14>
  - <https://github.com/frevib/io_uring-echo-server/pull/16>
  - <https://github.com/frevib/io_uring-echo-server/pull/24>
  - <https://github.com/frevib/epoll-echo-server>
  - <https://github.com/frevib/epoll-echo-server/blob/master/epoll_echo_server.c>
  - <https://github.com/frevib/epoll-echo-server/blob/master/Makefile>
  - <https://github.com/haraldh/rust_echo_bench/blob/master/src/main.rs>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_prep_provide_buffers.3>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_register_buf_ring.3>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_prep_recv_multishot.3>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_prep_multishot_accept.3>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/frevib/io_uring-echo-server`) · [data/wave5/enrich/raw/github_com_frevib_io_uring_echo_server.json](../../../data/wave5/enrich/raw/github_com_frevib_io_uring_echo_server.json) (enrichment confidence 0.8)

</details>
