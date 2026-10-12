# NanoMsg

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> C library of brokerless messaging patterns (PUB/SUB, REQ/REP, etc.) with lower small-message latency than ZeroMQ on one host.

| | |
|---|---|
| **Beats** | ZeroMQ |
| **Claimed result** | The paper states the win qualitatively and gives no ratios. NanoMsg has the lowest average latency of ZeroMQ, NanoMsg and NNG for payloads up to 64 KB In-Process and up to 128 KB Inter-Process (Obs. 1, 2, 4). It also has the lowest CPU at every size Inter-Process (Obs. 5) and the lowest memory (Obs. 11). The margin is modest. With 1 subscriber and a 1000 us publish interval, average latency at 1 KB is 7.5 us vs ZeroMQ's 10.3 us In-Process (\~1.4x) and 16.2 vs 25.8 us Inter-Process (\~1.6x), shrinking to \~1.1-1.2x at 32 KB (derived from the paper's artifact results/results.csv). Over TCP, NanoMsg leads only up to 8 KB (\~1.2x) and is far slower than ZeroMQ at 16-32 KB (about 560 us vs 40 us, derived from the same CSV). ZeroMQ wins peak throughput (\~4.8 vs \~3.8 GB/s In-Process; \~2.9 GB/s IPC/TCP), large-payload latency and throughput scaling with more subscribers. |
| **Workload** | Brokerless PUB/SUB with all processes on one host, over In-Process, Inter-Process (IPC) and TCP-loopback transports. Payload runs from 1 KB to 512 KB in powers of two (x1000 B) with 1 subscriber, and 1/2/4/8 subscribers are tested at 32 KB. Each run sends C=5000 messages after a 1000 ms publisher delay, averaged over R=4 runs. Latency uses a 1000 us publish interval and throughput/CPU use 0 us. Versions: ZeroMQ (libzmq 4.3.4 + CZMQ 4.2.1), NanoMsg 1.1.5 and NNG 1.9.0. |
| **Metric** | latency |
| **Hardware** | Intel(R) Xeon(R) w3-2435 CPU, 8 cores at 3.1 GHz, 64 GB RAM |
| **Compiler and flags** | The harness (bml/) is built with gcc -Wall -Wextra -O2 (bml/Makefile); the gcc version is not stated. ZeroMQ/CZMQ and NanoMsg come from distro apt packages (libzmq3-dev, libczmq-dev, libnanomsg-dev), with the distro release and build flags not stated. NNG 1.9.0 is built from source with CMake/Ninja defaults. |
| **Adoption** | 6.3k stars |
| **Last commit** | 2026-09-06 |
| **Links** | [repository](https://github.com/nanomsg/nanomsg) · [benchmark](https://arxiv.org/abs/2508.07934) |

## Verdict

An independent Hitachi Energy study (IEEE SRDS 2025) compared nanomsg 1.1.5 with ZeroMQ (libzmq 4.3.4 + CZMQ 4.2.1) and NNG 1.9.0, using a gcc -O2 C harness against prebuilt distro packages (NNG built from source). The test was one-host PUB/SUB on a Xeon w3-2435 (8 cores, 64 GB), 5000 messages x 4 runs. With 1 subscriber at a 1000 us publish interval, nanomsg's mean latency at 1 KB was 7.5 vs 10.3 us in-process and 16.2 vs 25.8 us over IPC (about 1.4-1.6x, derived from the published CSV). The gap narrowed to about 1.1-1.2x at 32 KB and reversed at larger sizes, and ZeroMQ kept the best peak throughput and worst-case latency.

## Use it when

- Same-host PUB/SUB or request/reply with small-to-medium messages (about 1-64 KB in-process, up to 128 KB over IPC), where mean latency and CPU matter more than peak throughput. The SRDS 2025 study measured a 1 KB mean of 7.5 vs 10.3 us in-process and 16.2 vs 25.8 us over IPC against ZeroMQ.
- CPU- or memory-constrained hosts. It is ANSI C89 with no C++ runtime, and the study found it had the lowest CPU at every IPC message size and the lowest memory use of ZeroMQ, nanomsg and NNG.
- Designs that want SURVEY (surveyor/respondent) or BUS as built-in socket types, or REQ sockets with built-in request retry, rather than building these on top of ZeroMQ primitives.
- Existing nanomsg deployments, or peers that must speak the SP wire protocol, including NNG, which upstream says is wire-compatible.

## Skip it when

- New projects. Upstream says the library is in 'sustaining' mode: new features have stopped and only severe defects are fixed. It points users to NNG, which it says is API-compatible for about 99% of apps.
- TCP with 16-64 KB messages at default settings. In the study, mean latency at 16-32 KB was about 560 us vs ZeroMQ's 40 us. NN_TCP_NODELAY defaults to 0 (Nagle on), and upstream closed the request to change that default (#674) as will-not-fix, whereas libzmq always sets TCP_NODELAY. The benchmark harness never set it. If you must use TCP, set NN_TCP_NODELAY=1 and re-measure.
- Large payloads, peak throughput or many subscribers. ZeroMQ won these in the study: peak throughput was about 4.8 vs 3.8 GB/s in-process and 2.9 vs 1.7 GB/s over IPC, and 512 KB in-process latency was 86 vs 118 us. nanomsg funnels all async I/O through one worker thread.
- Workloads that need delivery guarantees, backpressure or persistence on PUB/SUB. Delivery is best-effort, and messages are silently dropped when a subscriber or the TCP stack falls behind (#390). There is no broker and no shared-memory transport (#902).
- Streaming many tiny messages through one inproc pipe as fast as possible. A 2014 report (#300) found PAIR inproc throughput about 4.5x slower than ZeroMQ (2.45 s vs 0.55 s), which contributors attributed to an eventfd signal per message.

## How it is fast

It is plain C that uses intrusive containers to keep allocations per message low. nn_chunkref stores payloads of 32 bytes or less (usually protocol headers) inline. PUB fan-out (nn_dist_send) shares one reference-counted chunk across all subscriber pipes instead of copying the body for each subscriber. SUB sockets match subscriptions against a memory-compact Patricia trie with sparse and dense child nodes, and the library avoids ZeroMQ's double buffering (a user-space queue plus the kernel buffer) by relying on the transport's own buffers. It is not zero-copy, though: the inproc transport still memcpys each message once, and all async I/O runs on a single internal epoll/kqueue worker thread (src/aio/pool.c). That keeps CPU and memory low for small messages but limits how far it scales with large payloads and many subscribers.

## Compared with alternatives

Pick nanomsg over TCPSHM, a Linux-only, header-only, point-to-point channel with acked in-memory resend, when you need one-to-many PUB/SUB fan-out or Windows/macOS. Pick it over Mino, an IDL-typed zero-copy shared-memory framework, when you want a small, stable C library that sends untyped byte messages through a socket-style API. For raw same-host latency, TCPSHM's SHM mode (0.34 us RTT vs ZeroMQ IPC's 30.7 us) is in a different class.

## Integration

| | |
|---|---|
| **Form** | shared lib (default) or static lib (-DNN_STATIC_LIB=ON; Windows callers must also define NN_STATIC_LIB) |
| **Dependencies** | none beyond libc, POSIX pthreads and BSD sockets (Windows: ws2_32, mswsock, advapi32); CMake to build; asciidoctor optional for docs; also packaged in vcpkg and distro repos |
| **Minimum toolchain** | ANSI C89 compiler; CMake 2.8.12+ (CMake 4.x supported since 1.2.2); Windows Vista+ with MSVC 2010+ (mingw-w64 untested) |
| **Platforms** | Linux, macOS, FreeBSD/NetBSD/OpenBSD, Solaris, HP-UX, QNX, Android and Windows per CMakeLists; CI covers Linux, Windows and macOS; architecture-independent C |
| **Thread safety** | Sockets are designed to be safe to use from multiple threads, but upstream still discourages using one socket from several threads in parallel; all async I/O runs on a single internal worker thread |
| **Drop-in for the baseline** | false — the C API (int sockets, nn_\* calls, no context) and the SP wire protocol differ from libzmq/ZMTP, so it cannot replace libzmq in place or talk to ZeroMQ peers; the patterns map closely, so a port is mostly mechanical |

## Gotchas

- Filtering happens on the subscriber side. PUB sends every message to every connected SUB and the SUB's trie discards non-matches, so traffic nobody subscribed to still costs transport bandwidth and CPU.
- NN_RCVMAXSIZE defaults to 1024 kB, so larger messages are refused on receive unless you raise it (-1 removes the limit). NN_MAX_SOCKETS is a build-time cap of 512 sockets per process, and inproc ignores NN_SNDBUF (the receiver's NN_RCVBUF sets the buffer).
- Versions before 1.2.3 have a remotely exploitable buffer overflow in the WebSocket handshake (CVE-2026-97152, CVSS 4.0 score 8.6). 1.2.5 (2026-09) stopped malformed IPC headers from aborting the process. Distro packages such as the benchmarked 1.1.5 predate both fixes.
- The 'nanomsg' name is a trademark, separate from the MIT code license. COPYING names Martin Sustrik as the owner and nanomsg.org names Garrett D'Amore.

## Known shortcomings

- The win is modest (\~1.1-1.6x latency, derived from the paper's CSV) and TCP at 16-32 KB is much worse than ZeroMQ; the library is in sustaining mode (successor: nng). GCC version and flags of the distro-built libraries unstated.
- SECURITY: CVE-2026-97152 (WebSocket handshake overflow) is fixed only in 1.2.3; the benchmarked 1.1.5 distro package predates the fix. TCP has a 16-64 KB latency spike (\~560 vs 40 us) because Nagle is on by default (won't-fix, #674) and the harness never disabled it. ZeroMQ wins peak throughput (4.8 vs 3.8 GB/s inproc), large payloads and many subscribers; PUB/SUB silently drops (#390); 512-socket cap; sustaining mode (upstream recommends NNG).

## Caveats and trade-offs

Peer-reviewed (IEEE SRDS 2025; arXiv 2508.07934 is the preprint), independent of all three projects, with open MIT-licensed code and raw results (github.com/hitachienergy/messaging-libraries-benchmark). The compiler version and the libraries' build flags are not stated (distro packages), which keeps it off tier A. The latency win is modest (\~1.1-1.6x) and holds only for small-to-medium payloads. ZeroMQ wins peak throughput, large payloads and subscriber scaling, and over TCP NanoMsg has a severe latency anomaly at 16-64 KB. The tested nanomsg 1.1.5 is old. Both the paper and the nanomsg README say the library is in 'sustaining' mode: new feature work has ended, only severe bugs get fixed, and new projects are pointed to NNG. All runs used one host, 5000 messages x 4 runs.

Legacy/community-maintained successor project (superseded by NNG per upstream authors, though nanomsg itself still receives commits); no persistence/broker features; "nanomsg" name is a trademark of original author, add as a licensing caveat alongside the MIT-style COPYING text.

## Maintenance

Active by commit date (1.2.5 released 2026-09-06), but officially in sustaining mode: only severe fixes are made and NNG is recommended for new work. It is MIT-licensed pure C that is easy to build via CMake or vcpkg, or to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The paper (arXiv 2508.07934) was peer-reviewed and published at IEEE SRDS 2025 (DOI 10.1109/SRDS69199.2025.00036). It is an independent Hitachi Energy study of NanoMsg vs ZeroMQ (and NNG) that states the CPU (Xeon w3-2435) and publishes its code and raw data in hitachienergy/messaging-libraries-benchmark: bml/pub-sub.c, bml/ops_nanomsg.c, bml/ops_zeromq.c, results/runner.sh and results/results.csv. It is not A: the harness is built with gcc -O2 (bml/Makefile) but the gcc version is unstated, and the libraries under test are prebuilt distro apt packages whose distro release, compiler and flags are never stated.
- **Verifier notes:** The record's claim is accurate in substance. I added magnitudes from the artifact CSV (clearly labelled) and the TCP caveat. The tier stays B, but for a stronger reason than the record gave: the paper is peer-reviewed at SRDS 2025, not just an arXiv preprint. Metadata checks out: MIT license (COPYING is the Expat text; the GitHub API reports NOASSERTION), last commit 2026-09-06, 6.3k stars, not archived. 'Active' follows the commit-date rule even though the project calls itself sustaining.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2508.07934>
  - <https://arxiv.org/pdf/2508.07934>
  - <https://api.crossref.org/works>
  - <https://api.crossref.org/works/10.1109/srds69199.2025.00036>
  - <https://github.com/nanomsg/nanomsg>
  - <https://raw.githubusercontent.com/nanomsg/nanomsg/HEAD/COPYING>
  - <https://raw.githubusercontent.com/nanomsg/nanomsg/HEAD/README.md>
  - <https://github.com/hitachienergy/messaging-libraries-benchmark>
  - <https://raw.githubusercontent.com/hitachienergy/messaging-libraries-benchmark/HEAD/bml/Makefile>
  - <https://raw.githubusercontent.com/hitachienergy/messaging-libraries-benchmark/HEAD/install_bml.sh>
  - <https://raw.githubusercontent.com/hitachienergy/messaging-libraries-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/hitachienergy/messaging-libraries-benchmark/HEAD/results/runner.sh>
  - <https://raw.githubusercontent.com/hitachienergy/messaging-libraries-benchmark/HEAD/results/results.csv>
- **Sources the enricher read:**
  - <https://github.com/nanomsg/nanomsg>
  - <https://github.com/nanomsg/nanomsg/blob/master/README.md>
  - <https://github.com/nanomsg/nanomsg/blob/master/SUPPORT>
  - <https://github.com/nanomsg/nanomsg/blob/master/COPYING>
  - <https://github.com/nanomsg/nanomsg/blob/master/CMakeLists.txt>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/nn.h>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/protocols/pubsub/trie.h>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/protocols/pubsub/xpub.c>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/protocols/pubsub/xsub.c>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/protocols/utils/dist.c>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/utils/chunkref.h>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/utils/chunk.c>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/utils/msg.c>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/core/global.c>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/aio/pool.c>
  - <https://github.com/nanomsg/nanomsg/blob/master/src/transports/inproc/sinproc.c>
  - <https://github.com/nanomsg/nanomsg/blob/master/doc/nn_pubsub.adoc>
  - <https://github.com/nanomsg/nanomsg/blob/master/doc/nn_inproc.adoc>
  - <https://github.com/nanomsg/nanomsg/blob/master/doc/nn_send.adoc>
  - <https://github.com/nanomsg/nanomsg/blob/master/doc/nn_setsockopt.adoc>
  - <https://github.com/nanomsg/nanomsg/blob/master/doc/nn_tcp.adoc>
  - <https://github.com/nanomsg/nanomsg/blob/master/doc/nanomsg.adoc>
  - <https://github.com/nanomsg/nanomsg/blob/master/doc/nn_socket.adoc>
  - <https://github.com/nanomsg/nanomsg/blob/master/rfc/sp-tcp-mapping-01.txt>
  - <https://github.com/nanomsg/nanomsg/releases>
  - <https://github.com/nanomsg/nanomsg/releases/tag/1.2.3>
  - <https://github.com/nanomsg/nanomsg/releases/tag/1.2.5>
  - <https://github.com/nanomsg/nanomsg/commits/master>
  - <https://github.com/nanomsg/nanomsg/pull/1130>
  - <https://github.com/nanomsg/nanomsg/pull/1132>
  - <https://github.com/nanomsg/nanomsg/issues/300>
  - <https://github.com/nanomsg/nanomsg/issues/390>
  - <https://github.com/nanomsg/nanomsg/issues/674>
  - <https://github.com/nanomsg/nanomsg/issues/902>
  - <https://nanomsg.org/documentation-zeromq.html>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=nanomsg>
  - <https://arxiv.org/pdf/2508.07934>
  - <https://github.com/hitachienergy/messaging-libraries-benchmark/blob/HEAD/bml/ops_nanomsg.c>
  - <https://github.com/hitachienergy/messaging-libraries-benchmark/blob/HEAD/bml/ops_zeromq.c>
  - <https://github.com/hitachienergy/messaging-libraries-benchmark/blob/HEAD/results/results.csv>
  - <https://github.com/zeromq/libzmq/blob/master/src/tcp.cpp>
  - <https://github.com/MengRao/tcpshm>
  - <https://github.com/bkcarlos/Mino>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/nanomsg/nanomsg`) · [data/wave6/enrich/raw/github_com_nanomsg_nanomsg.json](../../../data/wave6/enrich/raw/github_com_nanomsg_nanomsg.json) (enrichment confidence 0.82)

</details>
