# iceoryx (iceperf)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Zero-copy shared-memory publish/subscribe IPC for C++ and C; sub-microsecond same-host latency versus POSIX message queues and Unix sockets.

| | |
|---|---|
| **Beats** | POSIX message queue and Unix domain socket (SOCK_DGRAM) |
| **Claimed result** | Average latency in microseconds, README example output: 1 kB payload iceoryx 0.73 vs message queue 3.1 and Unix domain socket 4.3 (about 4x and 6x, derived from page data); 4096 kB payload iceoryx 0.61 vs message queue 1.2e+03 and Unix domain socket 1.7e+03 (about 2,000x and 2,800x, derived from page data). iceoryx stays at about 0.6 us for every payload size. |
| **Workload** | iceperf example: leader and follower processes ping-pong 100000 round trips per payload size from 1 kB to 4096 kB (README run; the code default is 10000). The reported figure is one-way latency: total loop time divided by 2 x round trips (base.cpp). Timing covers loan/allocation, release and the send/receive calls only; the payload is never filled beyond a small header. All three transports busy-poll the receiver (nonblocking mq_receive / recvfrom loops, iceoryx take() loop). On Linux the message queue and Unix domain socket baselines send at most 4 kB per message (MAX_MESSAGE_SIZE in mq.hpp and uds.hpp), so a 4096 kB payload is split into 1024 messages per direction. |
| **Metric** | latency |
| **Hardware** | Intel Xeon E3-1505M v5 @ 2.80GHz, Ubuntu 18.04 (README example output) |
| **Adoption** | 2.2k stars; README lists ROS 2 (rmw_iceoryx), Cyclone DDS and AUTOSAR Adaptive integrations |
| **Last commit** | 2026-08-18 |
| **Links** | [repository](https://github.com/eclipse-iceoryx/iceoryx) · [benchmark](https://github.com/eclipse-iceoryx/iceoryx/blob/main/iceoryx_examples/iceperf/README.md) |

## Verdict

First-party iceperf example output on a Xeon E3-1505M v5 under Ubuntu 18.04 (compiler and flags not stated, single run, 100,000 round trips, one-way latency taken as half the round trip): iceoryx about 0.6-0.73 us at every payload from 1 kB to 4096 kB versus 3.1 us (message queue) and 4.3 us (Unix domain socket) at 1 kB, about 4x and 6x. The 4096 kB ratios (1.2e+03 and 1.7e+03 us, about 2,000x and 2,800x) come from baselines fragmenting into 1024 repeated 4 kB sends while iceoryx passes a pointer and never touches the payload.

## Use it when

- Moving large messages (camera frames, point clouds, tensors from hundreds of kB to MB) between processes on the same machine, where a socket or message queue would copy the payload through the kernel on every hop.
- Robotics and automotive stacks already on ROS 2 (rmw_iceoryx), Cyclone DDS shared-memory transport, eCAL or AUTOSAR Adaptive bindings that build on iceoryx.
- Latency-sensitive one-to-many pub/sub on Linux or QNX where you can dedicate a polling core or accept WaitSet wake-up cost, and payload sizes are bounded and known up front.
- Existing iceoryx deployments that need a stable, security-patched C++ IPC layer while planning a move to iceoryx2.

## Skip it when

- New projects: the README says iceoryx classic is in maintenance mode (security fixes only, no further major releases) and will reach end of life shortly after iceoryx2 v1.0; the maintainers recommend iceoryx2.
- Communication across machines: there is no network transport; remote traffic needs a gateway such as iceoryx-gateway-dds.
- Small, infrequent messages where a Unix socket's few microseconds do not matter: you pay for a daemon, shared-memory sizing (/dev/shm, Docker --shm-size) and a loan/release API discipline.
- Untrusted peers: all participants map the same shared-memory segments; open bug reports include possible double free of chunks (#562), mutex-owner-died chunk locking errors (#2193) and RouDi or Listener deadlock risks (#1546, #1711, #2202).
- Unbounded or highly variable payload sizes: a loan larger than the biggest configured mempool fails, and exhausting a pool yields MEPOO__MEMPOOL_GETCHUNK_POOL_IS_RUNNING_OUT_OF_CHUNKS unless you resize the RouDi config.

## How it is fast

True zero-copy: the payload is written once into a pre-allocated shared-memory chunk and only a chunk reference (iceoryx's RelativePointer, valid in every process's mapping) travels through lock-free shared-memory queues (hoofs SpscSofi / MpmcLockfreeQueue) to each subscriber, so per-message cost does not grow with payload size. Chunks come from fixed-size mempools configured at RouDi start-up (for example 128 B to 4 MB) and are handed out by a lock-free free list (MpmcLoFFLi), so a polling receiver's hot path has no kernel copy, no syscall and no heap allocation; event-driven receivers can block on a WaitSet or Listener instead.

## Compared with alternatives

The catalogued siblings (eRPC, Homa, Machnet, brpc, DRPC and the gRPC alternatives) all move bytes over a network stack; pick iceoryx only when both endpoints share one host and payloads are large, where passing a shared-memory pointer beats any socket-based RPC. For cross-machine RPC, eRPC (kernel bypass) or brpc remain the relevant choices.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | iox-roudi daemon at run time; libacl (Linux and QNX); optional cpptoml for TOML RouDi config and ncurses for the introspection tool; built with CMake 3.16+ (Bazel build also offered) |
| **Minimum toolchain** | C++17-era hoofs (README describes STL constructs beyond C++17); GCC 8.3+, Clang 9+, MSVC 2019+, CMake 3.16+ |
| **Platforms** | Linux and QNX (full feature set, shared-memory access rights), macOS, FreeBSD and Windows 10 (no shared-memory access rights); 64-bit for production, 32-bit is a technology preview |
| **Thread safety** | not documented as a blanket guarantee; publishers and subscribers are per-process endpoints, RouDi and the WaitSet/Listener are designed for concurrent processes |
| **Drop-in for the baseline** | partial: a different API (loan/publish/take/release with a central daemon) replaces mq_send/sendto; the protocol shape (one-way pub/sub or request/response on one host) is the same |

## Gotchas

- The README benchmark table is old: the same Xeon E3-1505M v5 output appears in the v0.90.0 README (apps then named iceperf-laurel/hardy) and was never regenerated; the current harness also runs 16 B to 512 B payloads and an iceoryx WaitSet (blocking receive) variant, neither of which has published numbers.
- Harness flaw behind the large-payload ratios: the message-queue and Unix-socket baselines are capped at 4 kB per message (2 kB for the socket on macOS) and, for bigger payloads, send the same first 4 kB slice of the buffer subPackets times into a single 4 kB receive buffer; the 4096 kB rows are therefore 1024 cache-hot syscall pairs, not a 4 MB copy, while iceoryx never writes or reads beyond the 12-byte header. The 2,000x-2,800x figures measure syscall count, not data movement.
- Every transport busy-polls (nonblocking mq_receive/recvfrom loops, iceoryx take() loop), and only a single average per size is printed (no percentiles, one run); blocking wake-up latency, which dominates real event-driven receivers, is not in the published data.
- In the iceperf iceoryx path, a failed loan (payload larger than the largest mempool, or pool exhausted) silently sends nothing, so the leader spins forever rather than reporting an error; size the RouDi mempools (iceperf ships iceperf-roudi with pools up to 4 MB) before benchmarking.

## Known shortcomings

- iceperf README numbers are example output with no compiler or flags; the message-queue and Unix-domain-socket baselines are capped at 4 kB per message (a 4096 kB payload is 1024 sends) with a per-send heap allocation, so the 2,000x+ ratios are inflated; latency is one-way (round trip / 2) and every transport busy-polls. Maintenance mode.
- Enricher: the README table is stale (identical in the v0.90.0 README of 2020, never rerun; the current harness adds 16-512 B rows and a WaitSet variant, unpublished). The MQ/UDS baselines resend the same first 4 kB slice subPackets times into one 4 kB receive buffer, so the 4096 kB rows are 1024 cache-hot syscall pairs, not a 4 MB copy, and iceoryx never touches payload past its 12-byte header: the 2,000-2,800x measures syscall count. Busy-poll only, single average, a failed loan hangs silently. Maintenance mode, end of life after iceoryx2 v1.0.

## Caveats and trade-offs

First-party example output from the README, a single run on a mobile Xeon under Ubuntu 18.04; compiler, flags and build type are not stated, so it stays C although the iceperf source is public. Latency is flat by construction: iceoryx passes a pointer into shared memory while the message queue and Unix domain socket must copy the payload through the kernel, and the timing excludes filling and reading the payload, so it is not an end-to-end application figure. The baselines are also handicapped at large sizes: in the current harness both are capped at 4 kB per message on Linux (message queue depth 8), so a 4096 kB payload becomes 1024 syscall-level sends and receives each way, and each baseline send heap-allocates a payload-sized buffer inside the timed loop. The 2,000x-2,800x large-payload ratios therefore mostly reflect fragmentation plus copying, not a tuned baseline; the 1 kB ratios (about 4x and 6x) are the fairer figure. All three transports busy-poll, so wake-up latency of a blocking receiver is not measured. The Unix domain socket baseline is nonblocking SOCK_DGRAM; its sender retries on ENOBUFS/EAGAIN without sleeping (the 10 ms retry sleep is only in the connection handshake, outside the timing). No comparison with other shared-memory IPC (Boost.Interprocess, ZeroMQ ipc, Cyclone DDS shm). The repo page says iceoryx classic is in maintenance mode with only security fixes, iceoryx2 being the successor; the repo now carries a SECURITY.md.

Shared-memory zero-copy transport on one machine only; needs the iox-roudi daemon and loaned-sample API (publisher fills the shared buffer directly); no network transport itself (README lists a Cyclone DDS gateway for remote traffic).

## Maintenance

Apache-2.0, 2.2k stars and widely integrated (ROS 2, Cyclone DDS, eCAL, AUTOSAR stacks), latest release v2.0.8, but iceoryx classic is in maintenance mode with security fixes only and end of life planned shortly after iceoryx2 v1.0, so use it for existing integrations and evaluate iceoryx2 for new work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party example output in iceoryx_examples/iceperf/README.md compares iceoryx with POSIX message queues and Unix domain sockets and names the CPU (Xeon E3-1505M v5, Ubuntu 18.04). The harness is public (iceoryx_examples/iceperf: base.cpp, iceoryx.cpp, mq.cpp, uds.cpp), but the compiler, flags and build type are not stated and it is a single example run, so it stays C.
- **Verifier notes:** README numbers match the record exactly (iceoryx C++ and C API rows are identical). I read the harness: latency is one-way (round trip / 2), all transports busy-poll, and the MQ/UDS baselines fragment payloads into 4 kB messages and allocate a buffer per send, which inflates the large-payload ratios; the record's claim that the UDS sender sleeps between retries was wrong and is corrected. Shortcomings to record: example output only (no compiler/flags), large-payload ratios inflated by 4 kB baseline fragmentation, not end-to-end, maintenance mode. Category websocket-grpc-rpc is a loose fit for shared-memory IPC middleware; the last commit date could not be re-checked (commits page HTTP 429), so it is left as recorded.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** first-party iceperf README (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/eclipse-iceoryx/iceoryx/blob/main/iceoryx_examples/iceperf/README.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/README.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/base.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/iceoryx.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/mq.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/mq.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/uds.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/uds.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/main_leader.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/SECURITY.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/LICENSE>
  - <https://github.com/eclipse-iceoryx/iceoryx>
- **Sources the enricher read:**
  - <https://github.com/eclipse-iceoryx/iceoryx>
  - <https://github.com/eclipse-iceoryx/iceoryx/releases>
  - <https://github.com/eclipse-iceoryx/iceoryx/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/README.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/README.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/base.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/base.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/iceoryx.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/iceoryx_c.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/iceoryx_wait.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/mq.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/mq.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/uds.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/uds.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/main_leader.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/main_follower.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/iceperf_leader.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/iceperf_leader.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/roudi_main_static_config.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/topic_data.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/example_common.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/iceperf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/v0.90.0/iceoryx_examples/iceperf/README.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/v0.90.0/iceoryx_examples/iceperf/base.cpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/v0.90.0/iceoryx_examples/iceperf/mq.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/v0.90.0/iceoryx_examples/iceperf/uds.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/v1.0.0/iceoryx_examples/iceperf/README.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/v1.0.0/iceoryx_examples/iceperf/mq.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/v2.0.0/iceoryx_examples/iceperf/mq.hpp>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_examples/README.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/doc/website/FAQ.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/doc/website/getting-started/installation.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/doc/goals-non-goals.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_hoofs/README.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/iceoryx_platform/cmake/IceoryxPackageHelper.cmake>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx/main/SECURITY.md>
  - <https://raw.githubusercontent.com/eclipse-iceoryx/iceoryx2/main/README.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/eclipse-iceoryx/iceoryx`) · [data/wave5/enrich/raw/github_com_eclipse_iceoryx_iceoryx.json](../../../data/wave5/enrich/raw/github_com_eclipse_iceoryx_iceoryx.json) (enrichment confidence 0.75)

</details>
