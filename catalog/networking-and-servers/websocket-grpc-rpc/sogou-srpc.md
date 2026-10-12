# SRPC (Sogou C++ Workflow RPC)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++ RPC framework on Sogou Workflow speaking SRPC, Thrift-framed and bRPC wire protocols; \~1.6-2.8x Apache Thrift server QPS.

| | |
|---|---|
| **Beats** | Apache Thrift (binary protocol) |
| **Claimed result** | Read off README charts (derived from page data). Same machine, 1024B requests (benchmark3): SOGOU srpc-std \~310k QPS vs 'FACEBOOK thrift-binary' (Apache Thrift TNonblockingServer per benchmark/thrift_server.cc) \~145k at 32 client threads (\~2.1x) and \~309k vs \~191k at 256 threads (\~1.6x). Same machine, 100 threads, by request size (benchmark1): \~319k vs \~185k at 16B (\~1.7x) to \~254k vs \~158k at 16KB (\~1.6x) and \~205k vs \~133k at 32KB. Cross-machine: srpc \~470-520k vs \~167-220k at 64-1024 threads (benchmark2, \~2.3-2.8x); \~310k-670k vs \~145k-222k at 1-16 client processes (benchmark4, \~2.1-3.0x). Latency CDFs at fixed QPS (benchmark5/6): srpc stays under \~170us to the 99.9th percentile same-machine while Apache Thrift sits at \~235-480us; cross-machine Thrift is \~3.8ms+ at p80. SRPC's own thrift-binary server beats Apache Thrift by a little more (\~331k vs \~145k at 32 threads). Versus Baidu brpc, srpc-std is slightly slower same-machine (\~310k vs \~346k at 32 threads) but faster cross-machine (\~520k vs \~405k; \~670k vs \~407k). |
| **Workload** | Echo RPC with empty responses, driven by SRPC's own async client (benchmark/client.cc) against each server: same-machine QPS vs client threads (1-256, 1024B) and vs request size (16B-32KB, 100 threads); cross-machine QPS vs client threads (64-1024, 32B) and vs client processes (1-16 x 32 threads, 32B); latency CDFs at fixed QPS with 1% slow outliers (same-machine 10k QPS 1024B; cross-machine 32 clients x 2500 QPS 512B). Compared: SOGOU srpc-std, SOGOU brpc-std, SOGOU thrift-binary, BAIDU brpc-std and 'FACEBOOK thrift-binary' (Apache Thrift TNonblockingServer, TBinaryProtocol, 16 IO + 16 worker threads). |
| **Metric** | throughput |
| **Hardware** | 2-chip/8-core/32-thread Intel Xeon E5-2630 v3 @2.40GHz, 128GB RAM, 10 Gigabit Ethernet |
| **Compiler and flags** | Not stated in the README. benchmark/CMakeLists.txt (2020 initial commit) builds SRPC's benchmark as CMAKE_BUILD_TYPE RelWithDebInfo with -Wall -fPIC -pipe -std=c++11 -fno-exceptions (now -std=c++17). A comment in benchmark/GNUmakefile builds the Thrift server with 'g++ ... -O2 -g -std=c++11'. No compiler version is given. |
| **Adoption** | 2.1k stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/sogou/srpc) · [benchmark](https://github.com/sogou/srpc/blob/master/README.md#benchmark) |

## Verdict

These are SRPC's own README charts from 2020, pre-open-source data. SRPC's async client drove empty-response echo servers, each with 16 IO and 16 handler threads, on a 2x8-core Xeon E5-2630 v3 with 128 GB and 10 GbE. srpc-std reached \~310k QPS vs \~145k for Apache Thrift TNonblockingServer (TBinaryProtocol) at 32 concurrent 1 KB requests on one machine (\~2.1x), and \~470-520k vs \~167-220k across machines (\~2.3-2.8x). The compiler and Thrift version are not stated; the build files show a CMake RelWithDebInfo build for SRPC and -O2 -g for the Thrift server.

## Use it when

- You run Apache Thrift C++ servers with TBinaryProtocol over framed transport at 16+ concurrent requests: SRPC's ThriftServer speaks the same wire format, and its charts show \~2x server QPS at 32-256 concurrent 1 KB requests on one machine.
- One handler implementation must be served over several protocols at once, such as Thrift framed for legacy clients, bRPC-std, and HTTP+JSON for other languages.
- RPC handlers call other backends (HTTP, other RPCs, timers) and you want to do this without blocking threads, by pushing Workflow tasks onto ctx-&gt;get_series().
- Unary RPC with tail-latency targets at a fixed load: the README's CDFs show srpc under \~170 us to p99.9 on one machine at 10k QPS, while Apache Thrift sits at \~235-480 us.
- You want the framework to handle gzip/zlib/snappy/lz4 compression and OpenTelemetry/Prometheus trace and metrics reporting.

## Skip it when

- You need gRPC wire compatibility or streaming RPC. SRPC speaks neither: gRPC support is an open TODO (issue #85), and maintainers call the lack of streaming a weak spot (#230).
- Your Thrift setup uses TMultiplexedProtocol, several services on one port with native Thrift clients, oneway methods, or a protocol other than binary. ThriftServer implements only binary protocol over framed or HTTP transport, serves one Thrift service per port (#394), and the generator skips oneway methods (#100).
- Low concurrency or blocking callers. At 1-8 in-flight requests the chart shows srpc only \~1.05-1.4x ahead of Apache Thrift, and a blocking caller thread gets at most about 1/RTT calls per second (maintainer, #376).
- Many small requests on NICs with a packets-per-second limit, such as virtio VMs. SRPC has no single-connection pipelining mode. One user measured 56-75k cross-VM QPS against the README's \~500k, and brpc's single-connection mode did better in that setup (#376).
- Your team does not want Workflow's callback/task programming model or a dependency on the Workflow engine. The library is also built with -fno-exceptions.

## How it is fast

It runs on the Sogou C++ Workflow engine. Poller threads handle epoll/kqueue I/O and deserialize messages as bytes arrive, and a separate handler thread pool runs service methods and callbacks. Handlers never need to block a thread, because extra work goes into the request's SeriesWork as async tasks. Protobuf payloads are serialized through a ZeroCopyOutputStream straight into a chunked RPCBuffer (2 KB-256 KB pieces) that is handed to the socket as an iovec array for scatter-gather writes. Clients keep a keep-alive connection pool with one connection per in-flight request, and there is no pipelining. The README does not break down where the gap to Apache Thrift's TNonblockingServer comes from.

## Compared with alternatives

Pick SRPC over brpc when you need Apache Thrift framed-binary and bRPC-std interoperability from one set of handlers plus Workflow's async task model. SRPC's charts show it roughly level with brpc (slower on one machine, faster across machines), but brpc offers streaming and a single-connection mode. Pick grpcxx if you need gRPC wire compatibility; among the catalogued siblings only SRPC is measured against Apache Thrift.

## Integration

| | |
|---|---|
| **Form** | static lib + shared lib (libsrpc.a / libsrpc.so) plus the srpc_generator code generator; CMake or Bazel; Debian (sid) and Fedora packages |
| **Dependencies** | Sogou Workflow (git submodule, v1.1.0 as of 2026-09), Protobuf &gt;= 3.5 with protoc, OpenSSL (&gt;= 1.1 recommended), zlib, snappy &gt;= 1.1.6, lz4 (snappy and lz4 from submodules or system) |
| **Minimum toolchain** | C++17 on master since 2026-09-10 (protobuf 30+/abseil need it; earlier releases built as C++11/14); CMake &gt;= 3.6; minimum compiler version not documented |
| **Platforms** | Linux, macOS, Windows (needs Workflow's IOCP-based windows branch; srpc_tools unsupported there). Workflow claims x86 32/64-bit, big- and little-endian ARM, Loongson and Android. |
| **Thread safety** | Not documented for SRPC's public classes. Service methods run concurrently on Workflow's handler thread pool, and the benchmark issues calls on one shared client object from many callbacks. RPCBuffer is documented as not thread-safe. The Thrift-style sync status (thrift_last_sync_ctx) is per thread. |
| **Drop-in for the baseline** | partial — ThriftServer/ThriftClient interoperate with Apache Thrift over binary protocol and framed transport, and the generated handlers keep Apache-style signatures. You still regenerate stubs with srpc_generator, change headers, base classes and the build, and lose multiplexed, non-binary and oneway support. |

## Gotchas

- The README charts are from before the 2020 open-source release (maintainer, #376). In a 2024 re-run on a 10-core box (same machine, 32 B requests, brpc protocol), maintainers measured srpc and pooled brpc at rough parity: about 124k-172k QPS for every client/server pairing.
- SRPC has two Thrift modes. ThriftServer/ThriftClient (tutorials 07/08) speak native Thrift framed. SRPCServer with Thrift IDL (tutorials 03/04) uses SRPC's private protocol and cannot talk to Apache Thrift peers (#351, #394).
- The Thrift IDL parser is hand-written and has broken on real IDLs. It dropped Hbase.thrift method parameters (fixed in PR #352), and issue #392 (bad code for two-level namespaces) is still open. Test your .thrift files before committing to a port.
- v0.10.5 (2026-09-15) added a missing check of meta_len against payload length in BRPC/TRPC message parsing, so upgrade if you face untrusted peers. Master now requires C++17, but the README quick-start still compiles with -std=c++11.

## Known shortcomings

- Slightly slower than brpc on same-machine tests (faster cross-machine). The Thrift baseline is Apache Thrift's TNonblockingServer built -O2 -g. No compiler version stated.
- The README charts predate the 2020 release; the maintainers' 2024 re-run shows srpc and pooled brpc at rough parity, and the \~2x over Thrift was never re-measured (only \~1.05-1.4x at 1-8 in-flight requests). No pipelining (one pooled connection per in-flight request). Partial Thrift compatibility, no gRPC or streaming. v0.10.5 (2026-09) fixed a missing meta_len bounds check.

## Caveats and trade-offs

Project's own benchmark. Values are read visually off PNG charts, not a numeric table. The chart label 'FACEBOOK thrift-binary' is the Apache Thrift C++ TNonblockingServer (benchmark/thrift_server.cc uses apache::thrift, TBinaryProtocol, 16 IO + 16 worker threads), not fbthrift. The Thrift version is not stated; the server code uses boost::shared_ptr and PosixThreadFactory, which point to an older Apache Thrift. All servers are driven by SRPC's client, so only server-side speed is compared. Responses are empty. Compiler is not stated. The charts date from the 2020 open-source release. srpc-std is slightly slower than Baidu brpc on the same-machine tests.

Numbers read off line charts (no numeric table provided), so precision is approximate; tightly coupled to the Sogou C++ Workflow async engine, adding a dependency/learning curve beyond a plain RPC library.

## Maintenance

Actively maintained: v0.10.5 came out on 2026-09-15 with commits the same month. It is Apache-2.0 with 2.1k stars and is packaged in Debian and Fedora. It is a normal built library, but it pulls in the whole Workflow engine.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README charts (docs/images/benchmark1-6.png) state the CPU (Xeon E5-2630 v3), RAM, NIC and test parameters. The harness is public in benchmark/ (server.cc, client.cc, thrift_server.cc on Apache Thrift TNonblockingServer). No compiler or version is stated and flags appear only in build files, so it is not A. It is first-party, so not B.
- **Verifier notes:** The record's numbers match the charts. I fixed the caveat that guessed the baseline was Facebook's own Thrift: the harness shows it is Apache Thrift's TNonblockingServer, which matches the record's baseline field. I also widened the workload to all six charts and added the build flags from benchmark/. Metadata verified: Apache-2.0, not a fork, not archived, 2,143 stars, last commit 2026-09-15 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/sogou/srpc>
  - <https://github.com/sogou/srpc/blob/master/README.md#benchmark>
  - <https://github.com/sogou/srpc/blob/master/docs/images/benchmark1.png>
  - <https://github.com/sogou/srpc/blob/master/docs/images/benchmark2.png>
  - <https://github.com/sogou/srpc/blob/master/docs/images/benchmark3.png>
  - <https://github.com/sogou/srpc/blob/master/docs/images/benchmark4.png>
  - <https://github.com/sogou/srpc/blob/master/docs/images/benchmark5.png>
  - <https://github.com/sogou/srpc/blob/master/docs/images/benchmark6.png>
  - <https://github.com/sogou/srpc/blob/master/benchmark/thrift_server.cc>
  - <https://github.com/sogou/srpc/blob/master/benchmark/client.cc>
  - <https://github.com/sogou/srpc/blob/master/benchmark/CMakeLists.txt>
  - <https://github.com/sogou/srpc/blob/master/benchmark/GNUmakefile>
  - <https://github.com/sogou/srpc/blob/master/benchmark/test.py>
  - <https://github.com/sogou/srpc/blob/master/benchmark/benchmark_thrift.thrift>
- **Sources the enricher read:**
  - <https://github.com/sogou/srpc>
  - <https://github.com/sogou/srpc/blob/master/README.md#benchmark>
  - <https://github.com/sogou/srpc/blob/master/docs/images/benchmark2.png>
  - <https://github.com/sogou/srpc/blob/master/docs/images/benchmark3.png>
  - <https://github.com/sogou/srpc/blob/master/docs/en/installation.md>
  - <https://github.com/sogou/srpc/blob/master/docs/en/rpc.md>
  - <https://github.com/sogou/srpc/blob/master/docs/en/docs-03-server.md>
  - <https://github.com/sogou/srpc/blob/master/docs/en/docs-04-client.md>
  - <https://github.com/sogou/srpc/blob/master/docs/en/docs-05-context.md>
  - <https://github.com/sogou/srpc/blob/master/docs/en/docs-06-workflow.md>
  - <https://github.com/sogou/srpc/blob/master/CMakeLists.txt>
  - <https://github.com/sogou/srpc/blob/master/.gitmodules>
  - <https://github.com/sogou/srpc/blob/master/src/CMakeLists.txt>
  - <https://github.com/sogou/srpc/blob/master/.github/workflows/ci.yml>
  - <https://github.com/sogou/srpc/blob/master/benchmark/thrift_server.cc>
  - <https://github.com/sogou/srpc/blob/master/benchmark/server.cc>
  - <https://github.com/sogou/srpc/blob/master/benchmark/client.cc>
  - <https://github.com/sogou/srpc/blob/master/benchmark/CMakeLists.txt>
  - <https://github.com/sogou/srpc/blob/master/benchmark/GNUmakefile>
  - <https://github.com/sogou/srpc/blob/master/src/rpc_buffer.h>
  - <https://github.com/sogou/srpc/blob/master/src/rpc_zero_copy_stream.h>
  - <https://github.com/sogou/srpc/blob/master/src/rpc_task.inl>
  - <https://github.com/sogou/srpc/blob/master/src/rpc_client.h>
  - <https://github.com/sogou/srpc/blob/master/src/generator/printer.h>
  - <https://github.com/sogou/srpc/blob/master/src/message/rpc_message_thrift.cc>
  - <https://github.com/sogou/srpc/blob/master/src/message/rpc_message_srpc.cc>
  - <https://github.com/sogou/srpc/blob/master/tutorial/tutorial-07-thrift_thrift_server.cc>
  - <https://github.com/sogou/srpc/blob/master/tutorial/tutorial-08-thrift_thrift_client.cc>
  - <https://github.com/sogou/srpc/releases>
  - <https://github.com/sogou/srpc/commits/master>
  - <https://github.com/sogou/srpc/commit/43ecc5603fcf595cf0a551b00710d7257a14cc44>
  - <https://github.com/sogou/srpc/issues/376>
  - <https://github.com/sogou/srpc/issues/100>
  - <https://github.com/sogou/srpc/issues/85>
  - <https://github.com/sogou/srpc/issues/230>
  - <https://github.com/sogou/srpc/issues/351>
  - <https://github.com/sogou/srpc/issues/394>
  - <https://github.com/sogou/srpc/issues/410>
  - <https://github.com/sogou/srpc/issues?q=thrift+idl>
  - <https://github.com/sogou/workflow>
  - <https://github.com/sogou/workflow/blob/master/docs/en/about-config.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/sogou/srpc`) · [data/wave5/enrich/raw/github_com_sogou_srpc.json](../../../data/wave5/enrich/raw/github_com_sogou_srpc.json) (enrichment confidence 0.72)

</details>
