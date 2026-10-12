# NNG (nanomsg-next-generation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Maintained C rewrite of nanomsg (Scalability Protocols). It beats nanomsg's pub/sub throughput only for very large messages.

| | |
|---|---|
| **Beats** | NanoMsg |
| **Claimed result** | For Inter-Process communication, NNG shows higher throughput than NanoMsg for the two largest message sizes; for TCP communication, NanoMsg throughput peaks around 1.5 GB/s at 128KB then decreases, while NNG throughput monotonically increases and surpasses NanoMsg for large payloads, peaking around 2 GB/s; NNG also becomes more CPU-efficient than ZeroMQ for larger Inter-Process payloads |
| **Workload** | Independent PUB/SUB benchmarking suite comparing ZeroMQ (libzmq 4.3.4), NanoMsg (libnanomsg 1.1.5) and NNG (libnng 1.9.0) across In-Process, Inter-Process, and TCP-loopback transports, varying message size (1KB-512KB) and subscriber count, on a single host |
| **Metric** | throughput |
| **Hardware** | Intel Xeon w3-2435, 8 cores @ 3.1GHz, 64GB RAM; single host, loopback interface for TCP transport |
| **Compiler and flags** | Not stated in the paper. The benchmark repo's bml/Makefile builds the harness with gcc -Wall -Wextra -O2. install_bml.sh installs ZeroMQ and NanoMsg from Ubuntu apt packages and builds NNG v1.9.0 with 'cmake -G Ninja ..' and no CMAKE_BUILD_TYPE (NNG 1.9.0 sets no default). |
| **Adoption** | 4.7k stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/nanomsg/nng) · [benchmark](https://arxiv.org/abs/2508.07934) |

## Verdict

An independent Hitachi Energy study (IEEE SRDS 2025, arXiv 2508.07934) benchmarked PUB/SUB on one Xeon w3-2435 host (8 cores, 64 GB). It compared NNG 1.9.0 (built from source with CMake and no build type) against distro-packaged libnanomsg 1.1.5 and libzmq 4.3.4, using 1-512 KB messages over inproc, IPC and TCP loopback. NNG out-threw nanomsg only at the two largest IPC sizes, and above \~128 KB on TCP, where it reached \~2 GB/s against nanomsg's \~1.5 GB/s peak. ZeroMQ led overall at \~2.9 GB/s. The paper gives no compiler flags; the C harness is built with gcc -O2.

## Use it when

- Single-host PUB/SUB with very large messages: 256-512 KB over IPC, or above \~128 KB over TCP loopback. At these sizes NNG kept scaling toward \~2 GB/s, while nanomsg peaked around 1.5 GB/s and then declined.
- Replacing unmaintained libnanomsg in an existing deployment. NNG talks the same wire protocol to nanomsg and mangos peers, and NNG 1.x can serve many nn_\* callers through its compatibility layer.
- Servers with many sockets, many peers or many in-flight requests. Contexts plus nng_aio let one REQ/REP socket serve many concurrent transactions without raw sockets, and the README says NNG's design gains most in exactly these cases.
- Deployments that need TLS (Mbed TLS, wolfSSL or OpenSSL) or WebSocket transports, or that must build on Linux, macOS, Windows, FreeBSD and illumos from one C codebase.

## Skip it when

- Small or medium messages where latency matters. In the SRDS 2025 study, nanomsg had the best average latency (IPC up to 128 KB) and ZeroMQ the best worst-case latency. NNG's jitter was higher: under \~10 us on average, with spikes at 512 KB.
- Maximum raw throughput. The same study found ZeroMQ fastest across most transports and configurations (\~2.9 GB/s peaks), and nanomsg the most CPU- and memory-efficient.
- Simple single-threaded, synchronous applications. The README itself says legacy nanomsg may perform better there.
- Code that relies on nanomsg's send/receive priorities (NN_SNDPRIO/NN_RCVPRIO), NN_LINGER or its statistics semantics. NNG does not support these, or supports them differently.
- Lossless pub/sub, or cutting bandwidth with publisher-side filtering. PUB sends every message to every subscriber, subscribers filter locally, and both sides drop messages when their queues fill.

## How it is fast

NNG replaces nanomsg's design, where each socket ran on a single worker thread driven by state machines, with an asynchronous I/O framework (nng_aio). Completion callbacks run on a task-thread pool, and platform pollers (epoll, kqueue, event ports) do the I/O. Contexts let one socket run many concurrent state machines. The PUB fan-out does not copy the message: it bumps a refcount per pipe and uses a small bounded queue per pipe. The TCP/IPC transports send an 8-byte length, the header and the body as one scatter-gather write, and on receive they allocate an exact-size message and read the body straight into it. Neither the paper nor the project says which of these mechanisms produces the large-payload win over nanomsg.

## Compared with alternatives

Pick NNG over NanoMsg when you need an actively maintained, wire-compatible library, TLS/WebSocket, multi-threaded concurrency via contexts, or large-payload throughput; stay on NanoMsg for small-message latency and CPU efficiency. Pick it over shared-memory or single-host specialists such as msgq or TCPSHM when you need portable network transports and the full set of SP patterns rather than the lowest same-host latency.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake build) |
| **Dependencies** | none for the core; optional Mbed TLS, wolfSSL or OpenSSL for TLS; CMake 3.15+ to build (Ninja recommended) |
| **Minimum toolchain** | C11 compiler per the README (CMakeLists sets CMAKE_C_STANDARD 99); CMake 3.15+ |
| **Platforms** | Linux, macOS, Windows, FreeBSD, illumos/Solaris, Android, iOS; IPC uses UNIX domain sockets on POSIX and named pipes on Windows |
| **Thread safety** | The 2.0 manual has no blanket statement. Sockets are ID handles resolved through a locked, refcounted table (issue #1724), so calls from multiple threads are supported. nng_aio callbacks may run on other NNG threads and need their own synchronization, and blocking NNG calls from NNG threads are documented as safe. |
| **Drop-in for the baseline** | partial: wire-compatible with nanomsg and mangos peers. NNG 1.x ships an nn_\* compat API (NNG_ENABLE_COMPAT, on by default) that lacks NN_SNDPRIO, NN_RCVPRIO, NN_IPV4ONLY and the stats API. NNG 2.0 removes the compat API and requires porting to nng_\* calls plus an explicit nng_init(). |

## Gotchas

- Pub/sub is lossy by default, and the loss is silent. Each subscriber pipe on the PUB side has a 16-message send queue (NNG_OPT_SENDBUF, counted in messages, not bytes) that drops the oldest message when full. On the SUB side, NNG_OPT_SUB_PREFNEW=true discards older unreceived messages. Watch the tx_discard stats.
- The main branch is 2.0 development (2.0.0-beta.2, Aug 2026) with breaking API changes and no libnanomsg compat layer. The README points production users to the stable branch (1.12.x).
- Security: GHSA-8rrv-25fw-rm86 (integer overflow in nni_msg_alloc) lets a remote peer abort the process with one crafted length header; it is fixed in 1.12.3 and 2.0.0-alpha.7. Set NNG_OPT_RECVMAXSZ for untrusted peers (the 2.0 docs give the default as 1 GiB; 0 means unlimited). The HTTP directory-handler path traversal (GHSA-rv5j-2q4p-qm56) is fixed only in the v1.12.4 tag.
- No default CMAKE_BUILD_TYPE is set. A plain 'cmake -G Ninja ..' build, which is what the benchmark suite used for NNG 1.9.0, is likely unoptimized, so pass -DCMAKE_BUILD_TYPE=Release.

## Known shortcomings

- Mostly loses to ZeroMQ and nanomsg in the SRDS 2025 study; its real win is narrow (large-payload throughput vs nanomsg); NNG was likely built unoptimized (cmake with no build type).
- Beats nanomsg only on large payloads (256/512 KB over IPC, &gt;128 KB over TCP loopback, \~2 vs \~1.5 GB/s); ZeroMQ is fastest overall (\~2.9 GB/s) and nanomsg best on latency and CPU; NNG has higher jitter, spiking at 512 KB. Pub/sub silently drops messages by default (16-message per-pipe PUB queue, drop-oldest). The main branch is 2.0 beta with a breaking API (nn_\* compat removed). SECURITY: remote-abort bug GHSA-8rrv (nni_msg_alloc overflow) fixed in 1.12.3; set RECVMAXSZ for untrusted peers.

## Caveats and trade-offs

This is an independent third-party evaluation, published at IEEE SRDS 2025 (44th Symposium on Reliable Distributed Systems, DOI 10.1109/SRDS69199.2025.00036 per Crossref) and also available as arXiv 2508.07934. It has a public benchmark suite (github.com/hitachienergy/messaging-libraries-benchmark) and states the CPU model and library versions, but the paper gives no compiler or build flags. The suite's install script builds NNG with CMake and no build type, so NNG was likely compiled without optimization, while NanoMsg and ZeroMQ came from distro packages. Across the paper, NNG usually loses to ZeroMQ (highest throughput overall, \~2.9 GB/s peaks) and often to NanoMsg (best latency and CPU efficiency). The qualifying win over NanoMsg is limited to large payloads: the two largest sizes over IPC, and above \~128KB over TCP loopback.

NNG is generally NOT the fastest of the three: the paper's overall conclusion is that ZeroMQ delivers the highest throughput and NanoMsg the best CPU efficiency across most configurations and transports; NNG's wins are narrow (large-payload throughput vs NanoMsg in Inter-Process/TCP, and CPU efficiency vs ZeroMQ at large Inter-Process payloads). NNG also shows worse latency scaling with subscriber count than the other two.

## Maintenance

Actively maintained: last commit 2026-09-21, and stable 1.12.3 plus 2.0.0-beta.2 released 2026-08-27. It is MIT-licensed with commercial support from Staysail Systems; build it with CMake or take it from distro packages.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** This is a peer-reviewed, independent third-party evaluation. Crossref confirms it appeared at the 2025 44th IEEE SRDS (DOI 10.1109/SRDS69199.2025.00036). It compares NNG 1.9.0 against NanoMsg 1.1.5 and ZeroMQ 4.3.4 and states the CPU (Xeon w3-2435). The public suite's bml/Makefile builds the harness with gcc -O2, but the paper states no compiler or flags, and the build flags of the libraries under test are only implied (apt packages, plus NNG built via plain CMake). So it stays at B, not A.
- **Verifier notes:** Observations 4 and 7 in the arXiv PDF match the claimed_speedup text exactly (NNG beats NanoMsg at the two largest IPC sizes; NanoMsg's TCP throughput peaks at \~1.5 GB/s at 128KB while NNG reaches \~2 GB/s). The lead's SRDS 2025 attribution is correct, as Crossref confirms, so I rewrote the caveat that said otherwise. Metadata: MIT license, 4,673 stars, not archived, not a fork. The last commit is 2026-09-21, not 2026-09-03.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2508.07934>
  - <https://arxiv.org/pdf/2508.07934>
  - <https://github.com/nanomsg/nng>
  - <https://github.com/hitachienergy/messaging-libraries-benchmark>
  - <https://raw.githubusercontent.com/hitachienergy/messaging-libraries-benchmark/HEAD/bml/Makefile>
  - <https://raw.githubusercontent.com/hitachienergy/messaging-libraries-benchmark/HEAD/install_bml.sh>
  - <https://raw.githubusercontent.com/hitachienergy/messaging-libraries-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nanomsg/nng/v1.9.0/CMakeLists.txt>
  - <https://api.crossref.org/works?query.bibliographic=Performance+Evaluation+of+Brokerless+Messaging+Libraries&rows=3>
- **Sources the enricher read:**
  - <https://github.com/nanomsg/nng>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/migrate/nanomsg.md>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/proto/pub.md>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/proto/sub.md>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/api/init.md>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/api/sock.md>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/api/ctx.md>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/api/aio.md>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/api/msg.md>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/api/thread.md>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/tran/tcp.md>
  - <https://github.com/nanomsg/nng/blob/main/docs/ref/tran/ipc.md>
  - <https://github.com/nanomsg/nng/blob/main/src/sp/protocol/pubsub0/pub.c>
  - <https://github.com/nanomsg/nng/blob/main/src/core/message.c>
  - <https://github.com/nanomsg/nng/blob/main/src/sp/transport/tcp/tcp.c>
  - <https://github.com/nanomsg/nng/blob/main/CMakeLists.txt>
  - <https://github.com/nanomsg/nng/blob/stable/CMakeLists.txt>
  - <https://github.com/nanomsg/nng/blob/stable/cmake/NNGOptions.cmake>
  - <https://github.com/nanomsg/nng/blob/stable/docs/man/nng_compat.3compat.adoc>
  - <https://github.com/nanomsg/nng/blob/stable/docs/man/nng.7.adoc>
  - <https://github.com/nanomsg/nng/blob/stable/docs/man/nng_socket.5.adoc>
  - <https://github.com/nanomsg/nng/blob/stable/docs/RATIONALE.adoc>
  - <https://github.com/nanomsg/nng/releases>
  - <https://github.com/nanomsg/nng/issues/1737>
  - <https://github.com/nanomsg/nng/issues/1724>
  - <https://github.com/nanomsg/nng/issues/1663>
  - <https://github.com/nanomsg/nng/security/advisories>
  - <https://github.com/nanomsg/nng/security/advisories/GHSA-8rrv-25fw-rm86>
  - <https://arxiv.org/pdf/2508.07934>
  - <https://github.com/hitachienergy/messaging-libraries-benchmark>
  - <https://hn.algolia.com/api/v1/search?query=nng%20nanomsg&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/nanomsg/nng`) · [data/wave6/enrich/raw/github_com_nanomsg_nng.json](../../../data/wave6/enrich/raw/github_com_nanomsg_nng.json) (enrichment confidence 0.6)

</details>
