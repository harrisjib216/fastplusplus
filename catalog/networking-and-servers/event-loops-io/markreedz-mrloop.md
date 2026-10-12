# mrloop

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Tiny single-threaded C event loop on io_uring; README echo test shows 1.51x an unnamed epoll server.

| | |
|---|---|
| **Beats** | unnamed epoll-based echo server (README row 'epoll'; neither libuv nor libev is named) |
| **Claimed result** | Echo server: mrloop 288,169 vs epoll 191,011 responses/sec (1.51x, derived from page data). Same README, against Go's gnet echo server (gnet-io/gnet-benchmarks): mrloop 2,128,669 vs gnet 2,438,766 R/s, i.e. mrloop is slower (0.87x, derived from page data). Also lists the key-value store mrcache built on it: GET of 16B key 9.8m reads/s vs redis 2.7m vs memcached 400k. |
| **Workload** | TCP echo server (examples/echo_server.c on io_uring) driven by haraldh/rust_echo_bench, compared with an epoll echo server whose source is not in the repo; connection count, message length and duration are not stated. |
| **Metric** | throughput |
| **Hardware** | Not stated (no CPU model, core count, kernel version or NIC/loopback note); README only requires Linux kernel 5.4.1+. |
| **Compiler and flags** | Library and examples built with gcc -O3 (Makefile, bld and examples/bld). Compiler version not stated; the epoll baseline's build flags are not stated. |
| **Adoption** | 48 stars; the author's mrcache key-value store is built on it |
| **Last commit** | 2024-04-13 |
| **Links** | [repository](https://github.com/MarkReedZ/mrloop) · [benchmark](https://github.com/MarkReedZ/mrloop) |

## Verdict

The 1.51x row (288,169 vs 191,011 responses/s) dates from the 2019-11-20 README: examples/echo_server.c on io_uring against an epoll echo server that is not named or published, driven by haraldh/rust_echo_bench (one client thread per connection, ping-pong, length check only) with connection count, message size, kernel, compiler version and CPU unstated (the tool defaults are 50 connections, 512 bytes, 60 s). The gnet row (mrloop 2,128,669 vs gnet 2,438,766 R/s, 0.87x) was added on 2024-03-26 with a different harness (gnet-benchmarks: tcpkali, Go servers in multi-threaded mode, 1,000 to 10,000 connections) and an unstated configuration, so the two rows are separate runs more than four years apart.

## Use it when

- A small single-threaded Linux (kernel 5.4.1+) C server with a strict request/response (ping-pong) protocol and well under 1,000 concurrent connections.
- Learning or prototyping how an io_uring readiness-plus-readv event loop is structured; the whole library is one \~570-line C file and one header.
- Programs that want socket I/O, file readv/writev at an offset and timers driven by one ring without pulling in libuv or Boost.Asio.
- Vendoring a starting point for your own io_uring loop that you are prepared to harden yourself.

## Skip it when

- More than about 1,018 open file descriptors: per-connection event slots are fixed arrays of MAX_CONN 1024 indexed by fd with no bounds check.
- Pipelined or streaming protocols, or anything that must handle short writes or write errors: completions of mr_writev are discarded unread.
- Multi-threaded or multi-loop programs: the submit counter, the last-accepted fd and the client read buffer are file-level statics shared by every loop.
- Portable code (non-Linux), IPv6 servers (mr_tcp_server and mr_connect are AF_INET only) or production use: the todo file still lists 'Add tests' and notes completion-queue drops on overflow.
- Workloads where io_uring is known to tie or lose to epoll at high connection counts; the README's own gnet row shows mrloop at 0.87x of a Go epoll loop.

## How it is fast

Completion-based I/O through io_uring: a readiness POLL_ADD is re-armed per connection, then a readv is submitted into the connection's buffer, and reply writevs are queued without a syscall and sent in the same io_uring_enter that re-arms the next poll (or once more than 64 SQEs are pending). The saving over a classic epoll_wait/read/write loop comes from coalescing the write and the poll re-arm into one submission. It does not use later io_uring features such as multishot poll or recv, provided buffers, registered files or SQPOLL, and it handles one completion per loop iteration.

## Compared with alternatives

Pick mrloop over the Asio io_uring backend, Condy or uring_exec only when you want a tiny dependency-light C loop to read or vendor; those siblings are maintained and C++, and frevib/io_uring-echo-server is the better-documented io_uring-vs-epoll echo comparison. For portable production use, libhv or libev remain the safer choices.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | liburing (the Makefile unpacks /usr/lib/liburing.a into libmrloop.a) |
| **Minimum toolchain** | C99 (for-loop declarations); built with gcc -O3; Linux kernel 5.4.1+ per README; header has extern "C" guards for C++ |
| **Platforms** | Linux only (io_uring, timerfd); IPv4 TCP only |
| **Thread safety** | Not documented; not thread-safe in practice because num_sqes, mrfd and the 32 KB client read buffer are static globals in mrloop.c shared by all loops. |
| **Drop-in for the baseline** | no |

## Gotchas

- Memory-safety bug: loop-&gt;read_events[fd] and loop-&gt;read_data_events[fd] are arrays of MAX_CONN 1024 inside mr_loop_t, indexed by the raw accepted or connected fd with no bounds check (the 2019 source even has the check '//if (cfd &gt;= MAX_CONN) { close(cfd); break; }' commented out), so fd 1024 and above aliases or overruns neighbouring fields.
- mr_writev, mr_writevcb and mr_readvcb only call io_uring_submit once more than 64 SQEs are queued; a lone write leaves the process only when something else submits (the next poll re-arm in the read path) or the caller uses mr_flush or mr_writevf. Issue #4 ('echo_server does not echo') and issues #6 and #7 trace back to this; the owner closed them in April 2024 saying the need to flush 'has been documented', but neither the README nor mrloop.h says so. io_uring_get_sqe results are not NULL-checked on the write paths of a 128-entry ring.
- Harness caveat behind the numbers: the echo example reads into and writes from the same 64 KB buffer and ignores short reads, short writes and nread &lt; 0 (issue #5). That is safe only because rust_echo_bench is strict ping-pong (one message in flight per connection, length-only check). The gnet row was produced with gnet-benchmarks, whose echo load generator is tcpkali (streaming, content not verified), where a pending writev can be overwritten by the next readv into the same buffer; whether that run echoed correct bytes was not shown.
- _accept calls exit() on any accept or fcntl error (EAGAIN, EMFILE) and accepts one connection per POLLIN with a listen backlog of 32; the fcntl uses F_GETFD instead of F_GETFL; mr_add_timer truncates fractional seconds at or above 1 s (1.5 becomes 1).

## Known shortcomings

- First-party README only: the epoll baseline is unnamed and not in the repo, no hardware is stated, the README's own row has gnet faster (2,438,766 vs 2,128,669), and the repo is stale (last commit 2024-04-13).
- Enricher (code reading): per-fd event slots are arrays of MAX_CONN 1024 indexed by raw fd with no bounds check (memory corruption at fd 1024 and above); write completions are discarded, so short writes and errors are never seen; writes reach the kernel only after more than 64 are queued or on the next poll re-arm (issues #4, #6, #7); global statics make it not thread-safe. The 1.51x epoll row dates from 2019-11-20 and the gnet row from 2024-03-26 with a different harness (gnet-benchmarks, tcpkali, content unchecked), so the rows are separate runs; the echo example shares one buffer for read and write (issue #5).

## Caveats and trade-offs

First-party README numbers with no hardware, kernel, connection count or message size, and the epoll server being compared is not identified or included in the repo, so the 1.51x cannot be reproduced. The README's own gnet row shows mrloop slower than gnet, a Go event loop that uses epoll on Linux, so the io_uring-over-epoll advantage is workload dependent. The mrcache figures differ between READMEs (mrloop README 9.8m vs redis 2.7m; mrcache README 18.6m vs redis 2.5m), and they measure the application, not the loop. No independent measurement found (one search); the README, Makefile, bld files, todo and examples/echo_server.c were read. The last commit is 2024-04-13 (about 2.5 years old). [retier] Enricher (code reading): per-fd arrays of 1024 indexed by raw fd with no bounds check; write completions discarded; writes flushed only after 64 are queued or on poll re-arm (issues #4, #6, #7). The epoll row (2019-11-20) and gnet row (2024-03-26) come from separate runs with different harnesses.

Linux only (io_uring via liburing, kernel 5.4.1+ per README, while mrcache asks for 5.5 to 5.8). Callback API: the application supplies a per-connection buffer (the echo example allocates 64 KB per connection) and submits writes with mr_writev. Single event loop object; small library (mrloop.c, mrloop.h). The repo's todo file lists 'Add tests' and notes that completion-queue entries can drop on overflow without IORING_SETUP_CQ_NODROP.

## Maintenance

Stale since 2024-04-13 (27 commits, 48 stars, all five issues closed without code changes in April 2024) but MIT-licensed and small enough to vendor; fix the fd-table bounds, write-completion handling and submission flushing before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks section carries every number (mrloop 288,169 vs epoll 191,011 responses/sec with haraldh/rust_echo_bench; gnet 2,438,766 vs mrloop 2,128,669 R/s; mrcache 9.8m vs redis 2.7m vs memcached 400k), but they are first-party with no CPU, kernel, connection count or message size, and the epoll server compared is not in the repo (examples/ holds only mrloop programs), so C.
- **Verifier notes:** Record is accurate: MIT (LICENSE, Copyright 2019 Mark Reed), 48 stars, 27 commits, last commit 2024-04-13 ('c++ updates'), stale; Makefile, bld and examples/bld build with gcc -O3. Shortcomings for the orchestrator: unidentified and unpublished epoll baseline, no hardware or workload parameters, mrloop is slower than gnet on the README's own second row, and mrcache numbers differ between the two READMEs (9.8m vs redis 2.7m here, 18.6m vs redis 2.5m in the mrcache README).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 5 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/MarkReedZ/mrloop>
  - <https://github.com/MarkReedZ/mrloop/commits>
  - <https://github.com/MarkReedZ/mrloop/tree/master/examples>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/Makefile>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/bld>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/examples/bld>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/todo>
  - <https://raw.githubusercontent.com/MarkReedZ/mrcache/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/mrloop.h>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/mrloop.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/examples/echo_server.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/todo>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/Makefile>
  - <https://github.com/MarkReedZ/mrloop/issues?q=is%3Aissue>
  - <https://github.com/MarkReedZ/mrloop/issues/4>
  - <https://github.com/MarkReedZ/mrloop/issues/5>
  - <https://github.com/MarkReedZ/mrloop/issues/6>
  - <https://github.com/MarkReedZ/mrloop/issues/7>
  - <https://github.com/MarkReedZ/mrloop/commits>
  - <https://github.com/MarkReedZ/mrloop/commits/master/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/99814f2adfd8321af11fa3ef94e96ec40a60723d/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/2ccddb253eab96500c752a42f6690bc169a84133/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/47ad1e5f4865959f58a9ddfc9847dd7dc2231824/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/47ad1e5f4865959f58a9ddfc9847dd7dc2231824/mrloop.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/47ad1e5f4865959f58a9ddfc9847dd7dc2231824/examples/echo_server.c>
  - <https://raw.githubusercontent.com/haraldh/rust_echo_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/haraldh/rust_echo_bench/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/gnet-io/gnet-benchmarks/HEAD/README.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/markreedz/mrloop`) · [data/wave5/enrich/raw/github_com_markreedz_mrloop.json](../../../data/wave5/enrich/raw/github_com_markreedz_mrloop.json) (enrichment confidence 0.75)

</details>
