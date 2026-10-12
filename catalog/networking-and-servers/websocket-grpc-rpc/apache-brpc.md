# brpc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Baidu's C++ RPC framework built on bthread M:N scheduling; its 2016 benchmark shows 6-24x gRPC 0.11's QPS.

| | |
|---|---|
| **Beats** | gRPC |
| **Claimed result** | Page text: pooled brpc (baidu-rpc_mc) reached the highest throughput in the test, 2.3GB/s; gRPC 'was at the bottom in almost every test it took part in' and its cross-machine multi-client latency CDF 'is completely out of control' (the same-machine CDF test is where some gRPC requests timed out). Read off the charts (derived from page data): same-machine 16B requests, brpc single-connection \~216k QPS vs gRPC \~33k (\~6.5x) and thrift_mc \~71k (\~3x); 1KB requests at 256 client threads, brpc \~291k vs gRPC \~32k (\~9x) and thrift_mc \~70k (\~4x); cross-machine 32 clients, brpc \~950k vs gRPC \~39k (\~24x) and thrift_mc \~93k (\~10x). Versus Thrift the win is not uniform: thrift_mc and UB beat brpc at 1-8 client threads, and single-connection brpc falls below thrift_mc at 16KB+ requests (pooled brpc stays above). The page says Thrift's cross-machine average latency is clearly higher than brpc's. |
| **Workload** | Same-machine and cross-machine RPC echo workloads: QPS vs request size, QPS vs thread count, and tail-latency CDFs under 1% long-tail requests, single-server and multi-hop server topologies |
| **Metric** | throughput |
| **Hardware** | Single machine: E5-2620 @ 2.00GHz, 24 cores with hyper-threading, 64GB RAM, Linux 2.6.32. Cluster 1: 15x E5-2420 @ 1.90GHz + 8x E5-2620 2.0GHz, 12 cores no HT, 1GbE. Cluster 2: 30x E5-2620 v3 @ 2.40GHz, 12 cores no HT, 96GB RAM, 10GbE. |
| **Adoption** | 17.6k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/apache/brpc) · [benchmark](https://github.com/apache/brpc/blob/master/docs/cn/benchmark.md) |

## Verdict

Baidu's own 2015 to January 2016 benchmark ran internal brpc r31906 against gRPC release-0_11 and an internal Apache Thrift 0.9.1 build (plus Baidu's UB, hulu-pbrpc and sofa-pbrpc), with no compiler or flags stated, on a 24-HT-core E5-2620 box and 1GbE/10GbE E5-2420/2620 clusters running Linux 2.6.32. Read off the charts, single-connection brpc did \~216k QPS vs gRPC's \~33k for 16 B echo requests on one machine, and \~950k vs \~39k server QPS with 32 cross-machine clients at 32 B (\~24x); some gRPC requests timed out in the same-machine latency test.

## Use it when

- C++ backend services that fan out to many downstreams and see long-tail requests, where p99 of normal requests matters. In the benchmark's latency CDFs (1% of requests taking 5-15 ms), brpc's normal requests were barely affected, while sofa-pbrpc and hulu-pbrpc had 2.5-30% of normal requests disrupted and gRPC's timed out or went out of control.
- Small-message (&lt;8 KB) RPC at high concurrency (16+ client threads or many clients) over one multiplexed connection. That is where the benchmark gap over gRPC and Thrift is largest, and it grows with thread and client count.
- Organizations that need one server to speak several protocols on one port (baidu_std, HTTP/h2+json, unary gRPC, Thrift, legacy Baidu nshead/UB), or a thread-safe client for redis, memcached or Thrift.
- Teams that want built-in production tooling: /status, /vars (bvar), /rpcz tracing, CPU, heap and contention profilers, and adaptive concurrency limiting.
- Bulk transfer with pooled connections (baidu-rpc_mc reached 2.3 GB/s on one machine in the benchmark), or RDMA transport (built with -DWITH_RDMA).

## Skip it when

- You need gRPC streaming (client, server or bidi) or the wider gRPC ecosystem. A maintainer confirmed in 2024 that bRPC does not support gRPC streaming (#2791), and the streaming requests #642, #843 and #1589, like the xDS request #2029, are still open.
- Low client concurrency or large single-connection payloads. In the benchmark, Thrift and UB beat brpc at 1-8 client threads, and single-connection brpc fell below thrift_mc at 16 KB+ requests.
- Windows targets, or production on macOS. Supported environments are Linux (and WSL), macOS and Docker, and the docs say macOS performance is worse than Linux and should not be used for performance-critical services.
- Polyglot codebases that expect generated clients per language. Only the C++ implementation is open source; other languages must use HTTP/h2+json or unary gRPC.
- Teams that cannot read Chinese or want a small dependency footprint. 33 of the 75 docs/en pages (including benchmark, load_balancing, flags, rpcz and the profilers) are stubs pointing to the Chinese version, and the build needs gflags, protobuf, leveldb, OpenSSL and zlib.

## How it is fast

Every request runs in its own bthread. bthread is an M:N user-space threading library: each pthread worker has its own run queue, idle workers steal work from others, and a futex-like 'butex' lets bthreads and pthreads wake each other. The edge-triggered epoll EventDispatcher does no reading itself. A per-fd atomic counter starts one bthread per readable fd, which makes dispatch wait-free, and even messages from the same fd are parsed in parallel, so one large or slow message does not hold up the others. Writers to a shared connection go through a wait-free MPSC linked list: the first writer does an atomic exchange on the write head and writes in place, later ones queue, and a KeepWrite bthread sends the rest in batches. With IOBuf (non-contiguous, zero-copy buffers), this lets one multiplexed connection scale with client threads.

## Compared with alternatives

Pick brpc over grpcxx when you need a whole framework (naming, load balancing, multi-protocol, profilers) on C++14 rather than a C++20 unary gRPC server. Pick it over rest_rpc (which measured 1.2-1.9x brpc on a 2019 same-machine echo test, but uses msgpack and has no gRPC or HTTP interop) when you need protobuf and gRPC compatibility. Against SRPC, per SRPC's own charts, brpc is slightly faster on one machine (\~346k vs \~310k QPS) and slower across machines (\~405k vs \~520k), so choose on ecosystem: brpc's Baidu protocols and tooling versus Sogou Workflow integration.

## Integration

| | |
|---|---|
| **Form** | static lib (shared lib also built by default) |
| **Dependencies** | gflags, protobuf (3.0+ per docs; abseil too when protobuf &gt; 4.21; 1.18.0 adds protobuf v35), leveldb, OpenSSL (or BoringSSL), zlib, pthread/dl/rt; optional glog, thrift, snappy, gperftools/tcmalloc, libunwind (bthread tracer), RDMA libs |
| **Minimum toolchain** | C++14 (C++17 when protobuf &gt; 4.21); CMake requires GCC 5+ or Clang 3.5+ (docs prefer GCC 8.2+); CMake 3.16+, config_brpc.sh+make, Bazel, or vcpkg |
| **Platforms** | Linux x86-64 (SSE4.2 enabled for CRC32C) and aarch64 in CI/docs; bthread context-switch code also covers i386, arm, loongarch64 and riscv64; macOS x86-64 and Apple Silicon (slower than Linux); Windows not listed as supported |
| **Thread safety** | Channel::CallMethod and generated stubs are thread-safe and one Channel should be shared across threads; Channel Init/destroy are not thread-safe; a Controller has one user and is not thread-safe |
| **Drop-in for the baseline** | partial — interoperates with gRPC on the wire for unary calls (brpc servers accept gRPC clients unchanged; brpc clients set protocol "h2:grpc"), but the C++ API is protobuf generic services plus Controller/Closure, not gRPC's generated stubs, and gRPC streaming is unsupported |

## Gotchas

- A bthread can resume on a different pthread after any blocking bthread call, so thread_local, __thread, pthread_getspecific and pthread_self() values can change mid-function. Use bthread-local storage (bthread_key_create), and don't hold a pthread mutex across an RPC. With GCC 4, the docs require -D__const__=__unused__ to avoid a stale-errno bug.
- Built-in services (/status, /vars, /flags, profilers) are on by default and served on the main port (has_builtin_services=true, internal_port=-1). Set internal_port or disable them before exposing the server publicly. Auth bypasses around internal_port were fixed only in 1.18.0 (Sept 2026: #3308, #3511, #3525), and that release also fixed many parser bounds and out-of-bounds bugs, so don't run older versions on untrusted networks.
- bRPC uses some protobuf internal APIs, so a protobuf upgrade can break it. 1.8.0+ no longer builds with protobuf 2.x, and .proto files need `option cc_generic_services = true`.
- h2/gRPC flow control is incomplete. Issue #516 still lists as unfixed that a response larger than the peer's window gets RST_STREAM instead of waiting for WINDOW_UPDATE; users worked around it by raising the gRPC client's flow-control window. Client-request flow control arrived only in 1.18.0 (#3430).

## Known shortcomings

- The charts date from January 2016 against gRPC release-0_11, so the 6.5-24x margins over gRPC reflect a very old gRPC. Thrift beats brpc at 1-8 client threads and beats single-connection brpc at requests of 16 KB and up.
- No gRPC streaming (#2791) and incomplete h2 flow control (#516), so only a partial gRPC replacement; C++ API is protobuf cc_generic_services, not gRPC stubs. Built-in services are on the main port by default; auth bypasses and parser bounds fixes landed only in 1.18.0 (2026-09). bthreads can migrate between pthreads, so thread_local values can change mid-function. Many English docs are stubs pointing to Chinese.

## Caveats and trade-offs

Tests were run in 2015/early 2016 (charts timestamped 2016-01-22..24) and the page itself says they may not reflect the latest status. gRPC tested was release-0_11 (pre-1.0) and Thrift was an internal build of 0.9.1, so neither represents modern versions. gRPC was left out of the two multi-server latency tests. Compiler and build flags are not stated and the gRPC/Thrift server code used is not published. Thrift beats brpc at low client-thread counts (1-8) and against single-connection brpc at 16KB+ requests.

Historically closely tied to Baidu's internal protocols and tooling; heavier/more complex than lightweight RPC libs; primarily documented in Chinese.

## Maintenance

Actively maintained Apache project (1.18.0 released 2026-09-17, commits as of 2026-09-26, 17.6k stars) under Apache-2.0. It is a built library with a real dependency chain, available through CMake, Bazel or vcpkg, and its benchmark page is a decade old and flags itself as possibly outdated.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Baidu benchmark (docs/cn/benchmark.md, charts dated 2016-01-22/24) comparing brpc against gRPC release-0_11 and Apache Thrift 0.9.1 with CPU models and test parameters stated, but no compiler/flags and no public harness for the gRPC/Thrift servers, so it stays C.
- **Verifier notes:** Metadata verified via gh: Apache-2.0, not archived, not a fork, 17,620 stars, last commit 2026-09-26 (active). The record's Thrift sentence was inverted: brpc is \~3x Thrift at small requests and single-connection brpc falls behind Thrift at large ones; the 'timeouts' belong to the same-machine CDF, not the cross-machine one. The English docs/en/benchmark.md is an untranslated stub pointing to the Chinese page.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/apache/brpc>
  - <https://github.com/apache/brpc/blob/master/docs/cn/benchmark.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/benchmark.md>
  - <https://github.com/apache/brpc/blob/master/docs/images/qps_vs_reqsize.png>
  - <https://github.com/apache/brpc/blob/master/docs/images/qps_vs_threadnum.png>
  - <https://github.com/apache/brpc/blob/master/docs/images/qps_vs_multi_client.png>
- **Sources the enricher read:**
  - <https://github.com/apache/brpc>
  - <https://github.com/apache/brpc/blob/master/docs/cn/benchmark.md>
  - <https://github.com/apache/brpc/blob/master/docs/images/qps_vs_reqsize.png>
  - <https://github.com/apache/brpc/blob/master/docs/images/qps_vs_multi_client.png>
  - <https://github.com/apache/brpc/blob/master/docs/en/overview.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/getting_started.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/io.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/threading_overview.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/bthread.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/bthread_or_not.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/iobuf.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/http_derivatives.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/client.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/server.md>
  - <https://github.com/apache/brpc/blob/master/docs/en/thread_local.md>
  - <https://github.com/apache/brpc/blob/master/docs/cn/thread_local.md>
  - <https://github.com/apache/brpc/blob/master/THREAT_MODEL.md>
  - <https://github.com/apache/brpc/blob/master/CMakeLists.txt>
  - <https://github.com/apache/brpc/blob/master/src/bthread/context.h>
  - <https://github.com/apache/brpc/blob/master/example/echo_c++/server.cpp>
  - <https://github.com/apache/brpc/blob/master/example/echo_c++/echo.proto>
  - <https://github.com/apache/brpc/blob/master/.github/workflows/ci-linux.yml>
  - <https://github.com/apache/brpc/tree/master/docs/en>
  - <https://github.com/apache/brpc/releases>
  - <https://github.com/apache/brpc/releases/tag/1.18.0>
  - <https://github.com/apache/brpc/issues/2791>
  - <https://github.com/apache/brpc/issues/1589>
  - <https://github.com/apache/brpc/issues/516>
  - <https://github.com/apache/brpc/pull/3525>
  - <https://github.com/apache/brpc/pull/3511>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/apache/brpc`) · [data/wave5/enrich/raw/github_com_apache_brpc.json](../../../data/wave5/enrich/raw/github_com_apache_brpc.json) (enrichment confidence 0.8)

</details>
