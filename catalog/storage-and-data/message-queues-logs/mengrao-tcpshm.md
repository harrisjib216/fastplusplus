# TCPSHM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++11 framework for crash-recoverable point-to-point messaging over TCP or shared memory; claims \~4.8x lower RTT than ZeroMQ.

| | |
|---|---|
| **Beats** | ZeroMQ |
| **Claimed result** | TCP mode RTT 8.81837us vs ZeroMQ TCP REQ/REP 42.268us (\~4.8x, derived from page data); SHM mode RTT 0.338221us vs ZeroMQ IPC (Unix domain socket) 30.6534us (\~90.6x, derived from page data) |
| **Workload** | Echo client/server round-trip-time benchmark on the same host, variable message sizes randomly chosen from (16, 36, 68, 200) bytes |
| **Metric** | latency |
| **Hardware** | Ubuntu 14.04, Intel Xeon E5-2687W @ 3.10GHz, cpupin enabled on both client and server |
| **Compiler and flags** | g++ -std=c++11 -O3 -lrt -lpthread (test/build.sh; g++ version not stated; ZeroMQ build not given) |
| **Adoption** | 480 stars |
| **Last commit** | 2020-05-04 |
| **Links** | [repository](https://github.com/MengRao/tcpshm) · [benchmark](https://github.com/MengRao/tcpshm#performance) |

## Verdict

The author ran an echo ping-pong on one Ubuntu 14.04 host (Xeon E5-2687W, 3.1 GHz, threads pinned), measuring average RTT only (total elapsed time divided by message count, no percentiles): 8.82 us over TCP loopback against 42.27 us for ZeroMQ REQ/REP over TCP (about 4.8x), and 0.338 us in SHM mode against 30.65 us for ZeroMQ IPC over a Unix domain socket (about 90x, but that compares busy-polled shared memory with a kernel socket). TCPSHM was built with g++ -std=c++11 -O3 (version not stated) while the ZeroMQ version, build and benchmark code are not published, and the README's 16/36/68/200-byte message mix matches the 2018 test code, but a 2020-05-04 commit changed HEAD's test to 4-16-byte payloads and a different clock, so HEAD does not reproduce the published numbers.

## Use it when

- Same-host IPC between two C++ processes where latency dominates, for example a trading gateway and a strategy, and you can give a core to each busy-polling thread. SHM mode measured 0.34 us average RTT on the author's machine.
- Point-to-point streams or request/response of small binary structs (under 64 KB including the 8-byte header) that must resume automatically after either side crashes or reconnects, without running a broker.
- Sessions that should reset on a schedule: renaming the server (for example 'Server20180714') discards the previous session's unhandled messages, as the README's daily trading example describes.
- A small, known set of clients where you want to map connection groups to threads yourself, and a dependency-free header-only codebase (nine headers, about 56 KB) that you can vendor and audit.

## Skip it when

- You need durability through power loss or host reboot. The README says it does not persist data to disk: queues live in the page cache (mmap-ed files with no fsync) or in /dev/shm.
- You need pub/sub, fan-out, topics, brokered storage or clients in other languages. It is C++-only and point-to-point.
- The host is CPU-constrained or shared, or you need many connections. Every polling thread spins (the bundled echo example spins 2 threads in the SHM client and 3 in the server), and the README says performance degrades past about 1000 live connections.
- Non-x86 or weakly ordered CPUs such as ARM. The shared-memory queue orders memory with compiler-only asm barriers and no hardware fences or atomics, which relies on x86 total store order. Issue #4 about ARM was only fixed in the test timer code. It is also Linux-only and IPv4-only.
- Untrusted networks or multi-user hosts. There is no TLS, and authentication is only a user-defined login blob. The code assumes a logged-in client 'will not attack us' when it processes acks, and shared-memory files are created with mode 0666 (before umask).

## How it is fast

SHM mode uses a bounded single-producer/single-consumer variable-length ring buffer (SPSCVarQueue, from the author's SPSC_Queue project) in a shm_open segment: 64-byte cache-line blocks, read and write indices on separate 128-byte-aligned lines, a producer-side cached read index, and messages built in place, synchronized only by compiler barriers with no atomics, locks or syscalls on the data path. Both sides busy-poll, so there is no kernel wakeup cost. TCP mode is a non-blocking, TCP_NODELAY socket polled from the user's thread, with the ack sequence piggybacked in each 8-byte message header, optional batching via PushMore(), and a send queue that is an mmap-ed file with no fsync/msync. The library creates no threads and does no logging, exceptions or clock reads.

## Compared with alternatives

Every sibling is a broker or pub/sub system (Wisp/NATS, Zenoh, FluxMQ, Redpanda and Woodpecker as Kafka-class systems, SocketPro), so pick TCPSHM only for one C++ point-to-point link that needs sub-microsecond same-host latency and automatic resend after a crash, with no topics, fan-out or disk durability. Zenoh is the closer, maintained alternative if you need pub/sub with optional shared memory (a feature flag you must enable).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond Linux POSIX APIs (sockets, shm_open, mmap). The test build links -lrt -lpthread. |
| **Minimum toolchain** | C++11 (test/build.sh uses g++ -std=c++11 -O3). It uses GCC builtins (__builtin_bswap\*, __BYTE_ORDER__) and GNU inline asm, so it needs GCC or Clang. Tested compiler versions are not documented. |
| **Platforms** | Linux only; x86-64 is the only tested architecture (the benchmark host is a Xeon E5-2687W); IPv4 only |
| **Thread safety** | Each connection is single-threaded: read and write it only from its polling thread (README Limitations), and push messages from other threads through your own queue. The server's PollCtl, PollTcp and PollShm can each run on its own thread, and the client's PollTcp and PollShm can run on separate threads. Cross-thread visibility uses compiler barriers, with no mutexes or atomics. |
| **Drop-in for the baseline** | no |

## Gotchas

- The interface doc and examples show the constructor as (ptcp_dir, name), but TcpShmClient and TcpShmServer actually take (name, ptcp_dir) (open issue #6). The examples pass the same string for both, which hides the mismatch.
- All capacities are compile-time Conf constants with small defaults: ShmQueueSize is 2048 B (32 64-byte blocks) and TcpQueueSize is 2000 B, and Alloc() returns nullptr when the queue is full, so the caller has to retry. In SHM mode every message takes whole 64-byte blocks, so a 12-byte message uses 64 B.
- A server connection slot is bound to a client name at first login and stays bound until Stop(). Once MaxShmConnsPerGrp or MaxTcpConnsPerGrp distinct names have logged into a group, new names are rejected with 'Max client cnt exceeded'. If persisted sequence numbers disagree at login, the connection fails through OnSeqNumberMismatch and must be fixed by hand.
- There are no transactions. A crash between Pop() and Push() can drop a response, and doing Push() before Pop() can duplicate one on recovery. The TCP side closes the connection if a message is larger than TcpRecvBufMaxSize, or if a send splits an 8-byte block and then gets EAGAIN; the connection recovers when it reconnects.

## Known shortcomings

- The ZeroMQ bench code and version are not public; the shared-memory vs ZeroMQ IPC comparison is not apples-to-apples. Abandoned since 2020. Flags are g++ -std=c++11 -O3 (test/build.sh).
- README bench predates HEAD (a 2020 commit changed message sizes and the clock), so HEAD doesn't reproduce it; average RTT only, no percentiles. The \~90x SHM figure is busy-polled shared memory vs Unix sockets; the echo example busy-spins 2 client and 3 server threads. The SHM queue uses compiler-only barriers (no atomics/fences), so it is only correct on x86-TSO, not ARM. Linux + IPv4 only; no fsync or power-loss durability; no TLS; shm files mode 0666 and the code assumes logged-in clients won't attack. Documented constructor argument order is wrong (#6); slots stay bound to a client name until Stop(); tiny compile-time default queues.

## Caveats and trade-offs

Same-host loopback echo only (not networked). SHM vs ZeroMQ IPC compares busy-polled shared memory against a Unix domain socket, so the \~90x is not apples-to-apples. ZeroMQ benchmark code and version are not in the repo ('exactly the same benchmark method'). g++ version not stated. Busy-polling, no persistence. Inactive since 2020.

Header-only, no disk persistence, non-blocking busy-poll design raises CPU usage, degrades past \~1000 live connections, single-writer-thread-per-connection constraint, message length capped at uint16_t

## Maintenance

Abandoned: the last commit (2020-05-04) was a cache-padding tweak, and the open issues #5 (2020) and #6 (2025) have no replies. It is MIT-licensed, about 56 KB of dependency-free headers, and easy to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance section gives exactly the claimed RTTs vs ZeroMQ, plus the CPU (Xeon E5-2687W), and TCPSHM's own bench is public (test/echo_client.cc, echo_server.cc; test/build.sh: g++ -std=c++11 -O3). The ZeroMQ side's benchmark code, ZeroMQ version and g++ version are not published, so the baseline run is not reproducible: C, not A.
- **Verifier notes:** The numbers and hardware match the README. The record wrongly said the flags were unstated: test/build.sh gives g++ -O3. The metadata matches: MIT, 480 stars, last commit 2020-05-04, abandoned, copyable.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/MengRao/tcpshm>
  - <https://github.com/MengRao/tcpshm#performance>
  - <https://github.com/MengRao/tcpshm/tree/master/test>
  - <https://github.com/MengRao/tcpshm/blob/master/test/build.sh>
  - <https://github.com/MengRao/tcpshm/blob/master/test/README.md>
- **Sources the enricher read:**
  - <https://github.com/MengRao/tcpshm>
  - <https://github.com/MengRao/tcpshm#performance>
  - <https://github.com/MengRao/tcpshm/blob/master/doc/interface.md>
  - <https://github.com/MengRao/tcpshm/blob/master/spsc_varq.h>
  - <https://github.com/MengRao/tcpshm/blob/master/ptcp_queue.h>
  - <https://github.com/MengRao/tcpshm/blob/master/ptcp_conn.h>
  - <https://github.com/MengRao/tcpshm/blob/master/tcpshm_conn.h>
  - <https://github.com/MengRao/tcpshm/blob/master/tcpshm_client.h>
  - <https://github.com/MengRao/tcpshm/blob/master/tcpshm_server.h>
  - <https://github.com/MengRao/tcpshm/blob/master/mmap.h>
  - <https://github.com/MengRao/tcpshm/blob/master/msg_header.h>
  - <https://github.com/MengRao/tcpshm/blob/master/endian.h>
  - <https://github.com/MengRao/tcpshm/tree/master/test>
  - <https://github.com/MengRao/tcpshm/blob/master/test/README.md>
  - <https://github.com/MengRao/tcpshm/blob/master/test/build.sh>
  - <https://github.com/MengRao/tcpshm/blob/master/test/common.h>
  - <https://github.com/MengRao/tcpshm/blob/master/test/echo_client.cc>
  - <https://github.com/MengRao/tcpshm/blob/master/test/echo_server.cc>
  - <https://github.com/MengRao/tcpshm/blob/c799c577/test/echo_client.cc>
  - <https://github.com/MengRao/tcpshm/blob/c799c577/test/timestamp.h>
  - <https://github.com/MengRao/tcpshm/blob/1cebc630/test/common.h>
  - <https://github.com/MengRao/tcpshm/commit/d4b3d649>
  - <https://github.com/MengRao/tcpshm/commits/master>
  - <https://github.com/MengRao/tcpshm/issues?q=is%3Aissue>
  - <https://github.com/MengRao/tcpshm/issues/2>
  - <https://github.com/MengRao/tcpshm/issues/4>
  - <https://github.com/MengRao/tcpshm/issues/5>
  - <https://github.com/MengRao/tcpshm/issues/6>
  - <https://github.com/MengRao/SPSC_Queue>
  - <https://github.com/eclipse-zenoh/zenoh>
  - <https://github.com/iamd3vil/wisp>
  - <https://hn.algolia.com/api/v1/search?query=tcpshm>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/mengrao/tcpshm`) · [data/wave6/enrich/raw/github_com_mengrao_tcpshm.json](../../../data/wave6/enrich/raw/github_com_mengrao_tcpshm.json) (enrichment confidence 0.8)

</details>
