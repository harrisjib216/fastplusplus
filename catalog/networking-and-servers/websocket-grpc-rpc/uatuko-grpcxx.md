# grpcxx

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Small C++20 unary-only gRPC server on nghttp2 and libuv; author's hello-world h2load runs show \~2.3-3x gRPC C++ throughput.

| | |
|---|---|
| **Beats** | gRPC |
| **Claimed result** | README benchmark table (req/s, h2load unary hello world): scenario 3b (100 clients x 10 streams), grpcxx v0.2.0 libuv single-threaded 452k vs gRPC C++ v1.48.4 callback 142k (\~3.2x, derived from page data). gRPC's best cell is 152k in 2b, where grpcxx does 449k (\~3.0x, derived from page data). README says '3x faster compared to the official implementation(s)'. In the same table grpc-go v1.56.2 peaks at 308k and tonic v0.10.2 at 212k (both 3b). In the only same-machine comparison (PR #2), grpcxx multi-threaded commit 4b13fce reached 346k (2b) and 355k (3b) vs gRPC 152k and 142k (\~2.3-2.5x, derived from page data). The asio backend is slower: 114k-290k in 3b. |
| **Workload** | Unary gRPC 'hello world' requests at varying client/concurrency levels (1, 10, 100 clients x 0 or 10 concurrent streams) over HTTP/2 |
| **Metric** | throughput |
| **Hardware** | MacBook Pro 2021, Apple M1 Max, 32GB RAM. grpcxx v0.2.0 ran on macOS 14.2.1 (23C71) (issue #25). The gRPC v1.48.4 and grpc-go rows come from PR #2 (2023-10-29), and issue #20 says that device and macOS differ from the later runs. |
| **Adoption** | 115 stars |
| **Last commit** | 2026-05-19 |
| **Links** | [repository](https://github.com/uatuko/grpcxx) · [benchmark](https://github.com/uatuko/grpcxx#benchmarks) |

## Verdict

The author ran h2load (single client thread) against the unary helloworld example on an M1 Max MacBook Pro. grpcxx v0.2.0 (libuv, single-threaded) reached 452k req/s at 100 clients x 10 streams, against 142k for the gRPC C++ v1.48.4 callback server (\~3.2x). The gRPC row comes from a 2023 run on a different M1 Max and macOS; the only same-machine comparison (PR #2) gives \~2.3-2.5x. Compiler and build flags are not stated for either side, and the repo's bench.sh builds through a Makefile that sets no CMAKE_BUILD_TYPE. grpcxx's 2b and 3b cells both plateau near 450k whatever the worker count, which suggests the load generator, not the server, sets the ceiling.

## Use it when

- Internal C++ unary services whose callers are ordinary gRPC stubs in any language, with TLS terminated by a proxy or sidecar (the author suggests Envoy in issue #29).
- Small request/response messages at high request rates over many multiplexed HTTP/2 connections, the shape the published benchmark measures.
- Builds where the full grpc++ dependency tree and its generated code are unwanted: grpcxx needs only nghttp2, libuv (or Asio) and protobuf, and generates one short header per .proto.
- Programs that already run a libuv loop or use systemd socket activation: listen() returns the uv_loop_t, run() accepts a pre-bound socket, and shutdown uses std::stop_token.

## Skip it when

- Any client, server or bidirectional streaming RPC: not supported. The streaming request (issue #49) was moved to a discussion with no implementation.
- You need in-process TLS/mTLS, ALTS, compression or auth plugins (TLS issue #47 is open; issue #29 confirms none are supported), or a gRPC client (issue #48 is open; the library is server-only).
- Blocking or long-running handlers. A connection stops reading while its batch runs, so requests on one connection are processed one after another. With workers = 0 a slow handler stalls the whole I/O loop. There is no async handler API, grpc-timeout deadline or cancellation.
- Large messages: the libuv backend reads through a fixed 1 KiB buffer (FIXME), and every chunk makes a round trip to a worker thread. No large-payload benchmark exists.
- Windows with the default libuv backend: MSVC fails to build it (C2894), so CI builds only the Asio backend on Windows.

## How it is fast

HTTP/2 framing is delegated to nghttp2 in its in-memory mode (nghttp2_session_mem_recv2 / mem_send2), driven by one libuv event loop that owns all socket I/O and wraps reads and writes in C++20 coroutines (Asio with coroutines is an optional, slower backend). Each read batch is parsed into complete requests and handed to a small mutex/condition-variable worker pool (or run inline when workers = 0). All HEADERS, DATA and trailer frames produced for that batch go into one buffer, which is flushed with a single uv_write. Dispatch is two hash lookups (service, then method) into std::function handlers, with no completion queues, call objects, interceptors, deadlines, TLS or compression on the path. No profile explaining the gap to gRPC C++ is published; PR #24 (keeping all I/O on one loop) is the change that pushed throughput past 400k req/s.

## Compared with alternatives

Pick grpcxx over brpc when you want only a lean unary gRPC server that stock gRPC clients can call, not brpc's larger multi-protocol framework (brpc also serves h2/gRPC and adds clients, streaming RPC and load balancing). The SRPC and rest_rpc READMEs do not list gRPC wire support (SRPC lists SRPC/bRPC/Thrift/tRPC; rest_rpc has its own coroutine client), so choose them only when you control both ends. No benchmark compares grpcxx with any of the three.

## Integration

| | |
|---|---|
| **Form** | static lib (shared with BUILD_SHARED_LIBS); CMake project consumed via FetchContent, or find_package after install; no distro packages |
| **Dependencies** | nghttp2 &gt;= 1.64.0; libuv &gt;= 1.51.0 (default) or Asio &gt;= 1.28 / Boost.Asio &gt;= 1.81 (GRPCXX_USE_ASIO); Protobuf &gt;= 3.15 (must be installed on the system); fmt &gt;= 11.1.4 for the protoc plugin. The default GRPCXX_HERMETIC_BUILD=ON fetches libuv, nghttp2 and fmt. |
| **Minimum toolchain** | C++20, CMake &gt;= 3.27. Clang/AppleClang builds add -fexperimental-library for std::stop_token. CI builds GCC and Clang on Ubuntu 26.04 and macOS, plus MSVC (Asio only). Minimum compiler versions are not documented. |
| **Platforms** | Linux and macOS (CI); Windows only with the Asio backend; no architecture-specific code (benchmarks ran on Apple M1 Max, arm64) |
| **Thread safety** | Not documented. From source: libuv server(n) runs I/O on one loop thread and handlers on n worker threads (default hardware_concurrency, 0 = inline on the loop). Handlers for different connections therefore run concurrently, so ServiceImpl must be thread-safe. add() the services before run(); services must outlive the server. |
| **Drop-in for the baseline** | partial — wire-compatible with standard gRPC clients for unary calls over plaintext HTTP/2, but server code must be rewritten to grpcxx's template API, and there is no client, streaming, TLS, compression, interceptors or deadlines |

## Gotchas

- SETTINGS_MAX_CONCURRENT_STREAMS is hard-coded to 10 per connection (FIXME in lib/grpcxx/h2/session.cpp). Clients that open more streams on one connection queue behind that limit.
- Length-prefix parsing looks fragile (from reading the code; no issue filed). PR #51 masked only the last prefix byte, so bytes 1-3 still sign-extend from char on x86-64 and Apple arm64. That decodes request lengths with bit 15 or 23 set (for example 32-64 KiB) as huge values. A 5-byte prefix split across two reads is also appended incorrectly. In either case the handler can receive an empty or default request. Test with your real message sizes.
- Handler exceptions derived from std::exception become INTERNAL status, including protobuf parse failures of bad input. Any other thrown type escapes a noexcept function and calls std::terminate. All grpc-\* request headers (grpc-timeout, grpc-encoding) are ignored, and the compressed-flag byte is read but not used.
- The test suite has no request/response round-trip test; test/uv/test_server.cpp notes testing was manual (Postman) until a client exists. Open issue #62: non-hermetic builds fail against system fmt 12.

## Known shortcomings

- The README's gRPC rows come from a different machine, macOS version and h2load settings; on the one same-machine comparison (PR #2) the gap is about 2.3-2.5x, not 3.2x. No compiler or flags stated.
- Server-only and unary-only: no streaming, TLS, client, deadlines or cancellation. SETTINGS_MAX_CONCURRENT_STREAMS is hard-coded to 10 (the benchmark sits exactly at it). Possible length-prefix decoding bugs for 32-64 KiB messages and split prefixes (source reading). Requests on a connection run serially; no round-trip tests.

## Caveats and trade-offs

Author's own benchmark. The README table mixes runs: the gRPC C++ and grpc-go rows come from PR #2 on a different M1 Max device and macOS than the grpcxx v0.2.0 rows (issue #20 warns of this). h2load settings also differ (gRPC: --requests=100000; grpcxx v0.2.0: --duration=3). PR #2 warns that single-threaded h2load may cap near \~300k req/s. Compiler and build flags for the C++ builds (grpcxx and gRPC) are not stated. gRPC v1.48.4 is an older release; the benchmark is a trivial hello-world unary call.

Much smaller feature set than official gRPC C++ (README claims '95% less generated code'); C++20 only; fewer language/ecosystem integrations; project is small/young so API stability and edge-case coverage are unproven.

## Maintenance

Actively maintained (v0.7.0 in May 2026, last commit 2026-05-19) and MIT-licensed, but pre-1.0 with 115 stars, shipped only as source through CMake FetchContent, and with an open build break against fmt 12 in non-hermetic builds.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Author's own h2load runs of examples/helloworld, with full logs in issues/PRs and the Apple M1 Max CPU stated, but no compiler or build flags for grpcxx or gRPC C++. The gRPC v1.48.4 row comes from a 2023-10-29 run on a different machine and macOS than the grpcxx v0.2.0 run. That makes it first-party with partial methodology, so tier C.
- **Verifier notes:** Issue #25 (the original benchmark_url) shows only grpcxx v0.2.0 numbers (452k etc.), not gRPC; the README Benchmarks table is the page that puts gRPC and grpcxx side by side, so benchmark_url was changed to it. The record's pairing of 452k (3b) with 152k (gRPC's 2b cell) was relabeled; \~3x still holds. Metadata verified: MIT, not a fork, not archived, 115 stars, last commit 2026-05-19 (active).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/uatuko/grpcxx>
  - <https://github.com/uatuko/grpcxx/blob/main/README.md>
  - <https://github.com/uatuko/grpcxx/issues/25>
  - <https://github.com/uatuko/grpcxx/pull/2>
  - <https://github.com/uatuko/grpcxx/pull/20>
  - <https://github.com/uatuko/grpcxx/issues/21>
  - <https://github.com/uatuko/grpcxx/pull/26>
- **Sources the enricher read:**
  - <https://github.com/uatuko/grpcxx>
  - <https://github.com/uatuko/grpcxx/blob/main/README.md>
  - <https://github.com/uatuko/grpcxx/blob/main/docs/README.md>
  - <https://github.com/uatuko/grpcxx/blob/main/docs/api.md>
  - <https://github.com/uatuko/grpcxx/blob/main/docs/protoc-gen-grpcxx.md>
  - <https://github.com/uatuko/grpcxx/blob/main/CMakeLists.txt>
  - <https://github.com/uatuko/grpcxx/blob/main/cmake/dependencies.cmake>
  - <https://github.com/uatuko/grpcxx/blob/main/changelog.md>
  - <https://github.com/uatuko/grpcxx/blob/main/Makefile>
  - <https://github.com/uatuko/grpcxx/blob/main/bin/bench.sh>
  - <https://github.com/uatuko/grpcxx/blob/main/examples/helloworld/README.md>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/CMakeLists.txt>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/h2/session.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/h2/session.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/server.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/server_base.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/server_base.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/rpc.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/service.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/request.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/message.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/message.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/response.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/context.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/uv/server.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/uv/server.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/uv/conn.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/uv/conn.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/uv/scheduler.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/uv/scheduler.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/uv/reader.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/uv/reader.h>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/uv/writer.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/uv/loop.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/asio/server.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/lib/grpcxx/asio/conn.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/test/uv/test_server.cpp>
  - <https://github.com/uatuko/grpcxx/blob/main/.github/workflows/build.yaml>
  - <https://github.com/uatuko/grpcxx/blob/main/.github/workflows/ci.yaml>
  - <https://github.com/uatuko/grpcxx/issues?q=is%3Aissue>
  - <https://github.com/uatuko/grpcxx/pulls?q=is%3Apr>
  - <https://github.com/uatuko/grpcxx/issues/6>
  - <https://github.com/uatuko/grpcxx/issues/21>
  - <https://github.com/uatuko/grpcxx/issues/25>
  - <https://github.com/uatuko/grpcxx/issues/29>
  - <https://github.com/uatuko/grpcxx/issues/34>
  - <https://github.com/uatuko/grpcxx/issues/37>
  - <https://github.com/uatuko/grpcxx/issues/47>
  - <https://github.com/uatuko/grpcxx/issues/48>
  - <https://github.com/uatuko/grpcxx/issues/49>
  - <https://github.com/uatuko/grpcxx/issues/62>
  - <https://github.com/uatuko/grpcxx/pull/2>
  - <https://github.com/uatuko/grpcxx/pull/20>
  - <https://github.com/uatuko/grpcxx/pull/24>
  - <https://github.com/uatuko/grpcxx/pull/26>
  - <https://github.com/uatuko/grpcxx/pull/51>
  - <https://github.com/apache/brpc>
  - <https://github.com/sogou/srpc>
  - <https://github.com/qicosmos/rest_rpc>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/uatuko/grpcxx`) · [data/wave5/enrich/raw/github_com_uatuko_grpcxx.json](../../../data/wave5/enrich/raw/github_com_uatuko_grpcxx.json) (enrichment confidence 0.8)

</details>
