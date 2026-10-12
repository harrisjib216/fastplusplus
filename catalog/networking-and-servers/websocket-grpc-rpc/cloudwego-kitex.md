# Kitex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> ByteDance's Go RPC framework whose gRPC-compatible transport, built on the Netpoll event loop, out-serves grpc-go on small unary RPCs.

| | |
|---|---|
| **Beats** | gRPC (grpc-go) |
| **Claimed result** | 1.70x higher QPS than grpc-go at concurrency=1000 (193,970.54 vs 114,054.24 QPS, 1KB echo); 1.51x at concurrency=100 (156,167.24 vs 103,178.46 QPS) (derived from page data: scripts/reports/grpc.csv linked from the README) |
| **Workload** | Echo RPC service, Kitex's gRPC-compatible transport vs official grpc-go, 1KB request/response, concurrency swept 100-1000, client pinned to 16 CPUs / server to 4 CPUs. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 5118 @ 2.30GHz; server pinned to 4 CPUs, client to 16 CPUs (taskset/numactl) on the same host over loopback; OS Debian, kernel 5.4.56.bsk.1-amd64 |
| **Compiler and flags** | Go 1.17.2; plain `go build -v` (default flags) per scripts/build_grpc.sh. The published data commit 251be0c (2022-08-26) pins kitex v0.3.5-0.20220819080849-d19ff0111efa and google.golang.org/grpc v1.42.0 |
| **Adoption** | 8052 stars; used in production at ByteDance |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/cloudwego/kitex) · [benchmark](https://github.com/cloudwego/kitex-benchmark) |

## Verdict

In ByteDance's own kitex-benchmark (data from August 2022), a Kitex server on its gRPC transport was compared with a default grpc.NewServer() from grpc-go v1.42.0 on a 1KB protobuf echo. Both were built with Go 1.17.2 and default flags, on a Xeon Gold 5118 with the server pinned to 4 CPUs and the client to 16 on the same host over loopback. Kitex served 156,167 vs 103,178 QPS at 100 concurrent callers (1.51x) and 193,971 vs 114,054 at 1000 (1.70x). The Kitex side also used fastpb-generated codecs against standard protoc-gen-go code, so the measured gain is transport plus codec, not transport alone.

## Use it when

- Go services on Linux handling many small unary protobuf RPCs (around 1KB) where server CPU is the limit. With 4 server cores the benchmark showed 1.5-1.7x the QPS of grpc-go, and p99 fell from 3.15 to 1.73 ms at 100 concurrent callers.
- You must stay on the gRPC wire protocol to interoperate with existing grpc-go or other-language clients, and you want governance (discovery, LB, retry, circuit breaking) built into the framework.
- Streaming-heavy services: a December 2024 rerun against grpc-go v1.66.2 measured 1.33x the QPS of grpc-go streaming at 100 streams (377k vs 283k) while using less server CPU (296% vs 335%), and 1.42x at 1000 streams.
- Organisations running Thrift and gRPC side by side that want one Go RPC stack and one server port for both.

## Skip it when

- Windows: Kitex falls back to Go's net package there because Netpoll does not support Windows. Maintainers say gRPC on Windows is unsupported, and an open issue (#1154) reports a server panic ('close of closed channel').
- You need TLS or mTLS terminated in-process on the server. Netpoll has no TLS, the FAQ says Kitex does not natively support TLS, and there is no server gRPC TLS option. Maintainers point to an Envoy sidecar or to switching the server to the gonet transport, which gives up Netpoll. Clients get TLS only through WithGRPCTLSConfig.
- Tail-latency-sensitive streaming at high fan-in: in the 2024 streaming CSV, Kitex's p99 is higher than grpc-go's from 400 concurrent streams up (8.12 vs 6.16 ms at 1000).
- proto2 schemas: Kitex's Protobuf support is proto3-only.
- Code built around grpc-go's API (grpc.Dial, grpc.NewServer, its ServerOptions and interceptors). Stubs must be regenerated with the kitex tool, and middleware must be ported to Kitex's model.

## How it is fast

The gRPC transport (pkg/remote/trans/nphttp2) is grpc-go v1.26.0's HTTP/2 transport, forked onto Netpoll. Netpoll is ByteDance's epoll/kqueue event-loop network library, and it replaces Go's net package, which blocks one goroutine per connection. Netpoll reads into LinkBuffer, a linked buffer built from pooled blocks. A fork of golang.org/x/net/http2's framer parses frames straight out of that buffer, reuses frame objects, and batches writes into a per-connection buffer (32KB by default, allocated at twice that size). The poller calls epoll_wait with timeout 0 while events keep arriving and -1 when idle; ByteDance measured this as about 18% cheaper per call. In the benchmark, the Kitex stubs also used fastpb-generated FastRead/FastWrite codecs, which compute the size first and then write, rather than the standard protoc-gen-go code.

## Compared with alternatives

Among Go options, pick Kitex over rpcx (its own binary protocol) or cmd-stream (MUS codec) when callers must keep speaking standard gRPC. Those siblings post bigger margins over grpc-go but abandon the gRPC wire format. wtx reports larger gains as a gRPC server but is Rust, and brpc and grpcxx are C++, so Kitex is the pick for a gRPC-compatible Go stack with governance included.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | cloudwego/netpoll, bytedance/gopkg, bytedance/sonic, cloudwego/frugal, fastpb, prutal, dynamicgo, thriftgo, golang.org/x/net, google.golang.org/protobuf and more (see go.mod). Code generation needs the kitex CLI plus protoc (Protobuf) or thriftgo (Thrift). |
| **Minimum toolchain** | Go 1.20 (go.mod directive); the docs promise support for the latest three Go releases |
| **Platforms** | Linux and macOS use Netpoll (epoll/kqueue). Windows compiles and runs since v0.4.0 but uses Go net, and gRPC there is unsupported per maintainers (issue #1154). CPU architecture limits are not documented. |
| **Thread safety** | A client object is safe for concurrent use and should be created once per downstream service and cached (docs warn against a client per request). RPCInfo is pooled via sync.Pool and must not be used after the handler returns; use rpcinfo.FreezeRPCInfo or KITEX_DISABLE_RPCINFO_POOL=true. |
| **Drop-in for the baseline** | partial — it is wire-compatible with gRPC over HTTP/2, but you regenerate stubs with the kitex tool and program against Kitex's client/server API and middleware instead of grpc-go's |

## Gotchas

- A Kitex Protobuf client sends Kitex Protobuf, not gRPC, unless the IDL has streaming methods or you set client.WithTransportProtocol(transport.GRPC). Pointing a default Kitex client at a grpc-go server therefore fails.
- The HTTP/2 transport is a 2019-era fork (grpc-go v1.26.0 transport; x/net/http2 framer from Go 1.17.4), so upstream fixes do not arrive automatically. Open reports include streams stuck in flow control (writeQuota.get) and Send returning nil on a dead peer (#1865, v0.14.1). Server panics on client disconnect were reported through v0.11.3 (#974).
- FastWrite computes the message size first and then serialises into a buffer of that size. If another goroutine mutates a request or response object in between, you get index-out-of-range or nil-pointer panics inside generated fastWriteField code; the docs classify this as a data race in user code that FastWrite exposes.
- The client keeps GOMAXPROCS\*3/2 HTTP/2 connections per target by default (grpc-go uses one ClientConn). The docs warn that resizing it with WithGRPCConnPoolSize can hurt performance.

## Known shortcomings

- Go, not C++. The 1.70x over grpc-go comes from 2022 data (kitex v0.3.5-pre, grpc-go v1.42.0, Go 1.17.2) and has not been re-run; the comparison is against grpc-go, not gRPC C++.
- Unary gRPC data last regenerated 2022-08 (kitex v0.3.5-pre vs grpc-go v1.42.0, Go 1.17.2). The 2024 streaming rerun (v0.11.3-pre vs grpc 1.66.2) shows 1.33-1.42x QPS but worse p99 from 400 streams up (8.12 vs 6.16 ms at 1000); its Go version is not actually stated. Transport and codec are mixed: Kitex used fastpb FastRead/FastWrite, grpc-go standard protoc-gen-go. First-party loopback runs with unequal client pools (6 vs 10 connections) and a per-call 1 s timeout context only on the grpc-go side. No in-process server TLS (Envoy sidecar or gonet; #1312, #952). Windows falls back to net and gRPC there is unsupported (#1154 panic open). Transport is a grpc-go v1.26 fork: streams stuck in flow control (#1865, open), close-of-closed-channel panic (#974). Proto3 only; Kitex Protobuf is not gRPC unless configured; stubs need the kitex tool. RPCInfo pooled (don't keep it); mutating a message during FastWrite panics. No independent benchmark.

## Caveats and trade-offs

The published numbers date from 2022-08 (commit 251be0c) and use kitex v0.3.5-pre against grpc-go v1.42.0 with Go 1.17.2. The current go.mod pins kitex v0.14.1 and grpc v1.66.2, and the README data has not been refreshed since. Client and server share one host over loopback, and the README itself warns that ksoftirqd threads escape taskset. The client pools also differ: Kitex uses a gRPC connection pool of 6, and grpc-go uses the runner default of 10 connections. The benchmark is first-party.

Kitex is primarily a Thrift-first framework (gRPC support is one of several transport/codec combinations); its own docs caution 'performance benchmark can only provide a limited reference' since production factors vary.

## Maintenance

Actively developed (v0.16.2 in May 2026, commits through 2026-09-22), Apache-2.0 and consumed as a normal Go module. However, the published unary gRPC numbers were last regenerated in August 2022; only the streaming comparison was rerun, in December 2024.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** The kitex-benchmark README GRPC section links the raw data, and scripts/reports/grpc.csv has Kitex (gRPC transport) at 193970.54 QPS against grpc-go at 114054.24 QPS at c=1000 with a 1KB echo. The code is public (grpc/kitex/, grpc/grpc/ using google.golang.org/grpc, scripts/benchmark_grpc.sh, scripts/build_grpc.sh with plain `go build -v`), and the README states the Go version (1.17.2) and CPU (Xeon Gold 5118). Code, compiler, flags and CPU are all stated, so I upgraded C to A. This follows the earlier plain-`go build` precedent.
- **Verifier notes:** The record said CPU, OS and Go version were not stated, but the README Specification section states all three. The exact QPS values sit in scripts/reports/grpc.csv, so no chart reading is needed, and the record's approximate numbers match. The metadata checks out: Apache-2.0, not archived or a fork, 8052 stars, last commit 2026-09-22.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cloudwego/kitex-benchmark>
  - <https://github.com/cloudwego/kitex>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/scripts/reports/grpc.csv>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/scripts/build_grpc.sh>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/scripts/benchmark_grpc.sh>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/scripts/base.sh>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/go.mod>
  - <https://github.com/cloudwego/kitex-benchmark/blob/251be0c05aa0334cc611a1738bec34c046d86d94/go.mod>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/grpc/grpc/main.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/grpc/grpc/client/grpc_client.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/grpc/kitex/main.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/grpc/kitex/client/kitex_client.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/runner/main.go>
- **Sources the enricher read:**
  - <https://github.com/cloudwego/kitex>
  - <https://github.com/cloudwego/kitex/blob/main/go.mod>
  - <https://github.com/cloudwego/kitex/releases>
  - <https://github.com/cloudwego/kitex/blob/main/pkg/remote/trans/nphttp2/grpc/doc.go>
  - <https://github.com/cloudwego/kitex/blob/main/pkg/remote/trans/nphttp2/grpc/framer.go>
  - <https://github.com/cloudwego/kitex/blob/main/pkg/remote/trans/nphttp2/grpc/grpcframe/frame_reader.go>
  - <https://github.com/cloudwego/kitex/blob/main/pkg/remote/trans/nphttp2/conn_pool.go>
  - <https://github.com/cloudwego/kitex/blob/main/pkg/remote/trans/nphttp2/server_handler.go>
  - <https://github.com/cloudwego/kitex/blob/main/internal/server/remote_option.go>
  - <https://github.com/cloudwego/kitex/blob/main/internal/server/remote_option_windows.go>
  - <https://github.com/cloudwego/kitex/blob/main/internal/client/remote_option_windows.go>
  - <https://github.com/cloudwego/kitex/issues/1312>
  - <https://github.com/cloudwego/kitex/issues/952>
  - <https://github.com/cloudwego/kitex/issues/1586>
  - <https://github.com/cloudwego/kitex/issues/1154>
  - <https://github.com/cloudwego/kitex/issues/1865>
  - <https://github.com/cloudwego/kitex/issues/974>
  - <https://github.com/cloudwego/kitex/issues/1687>
  - <https://github.com/cloudwego/kitex-benchmark>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/scripts/reports/grpc.csv>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/scripts/reports/streaming.csv>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/scripts/reports/to_csv.sh>
  - <https://github.com/cloudwego/kitex-benchmark/blob/251be0c05aa0334cc611a1738bec34c046d86d94/scripts/reports/to_csv.sh>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/scripts/base.sh>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/scripts/benchmark_grpc.sh>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/grpc/kitex/client/kitex_client.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/grpc/grpc/client/grpc_client.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/grpc/kitex/main.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/main/grpc/grpc/main.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/251be0c05aa0334cc611a1738bec34c046d86d94/codec/protobuf/kitex_gen/echo/echo-kitex.pb.fast.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/251be0c05aa0334cc611a1738bec34c046d86d94/runner/counter.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/cbf7440/runner/counter.go>
  - <https://github.com/cloudwego/kitex-benchmark/blob/cbf7440/go.mod>
  - <https://github.com/cloudwego/kitex-benchmark/commits/main/scripts/reports/grpc.csv>
  - <https://github.com/cloudwego/kitex-benchmark/commit/cbf7440>
  - <https://github.com/cloudwego/netpoll>
  - <https://github.com/cloudwego/fastpb>
  - <https://github.com/cloudwego/prutal>
  - <https://github.com/cloudwego/cloudwego.github.io/blob/main/content/en/docs/kitex/Getting%20started/prerequisite.md>
  - <https://github.com/cloudwego/cloudwego.github.io/blob/main/content/en/docs/kitex/Tutorials/basic-feature/protocol/transport_protocol.md>
  - <https://github.com/cloudwego/cloudwego.github.io/blob/main/content/en/docs/kitex/Tutorials/basic-feature/protocol/serialization-protocol/protobuf.md>
  - <https://github.com/cloudwego/cloudwego.github.io/blob/main/content/en/docs/kitex/Tutorials/basic-feature/protocol/streaming/gRPC/_index.md>
  - <https://github.com/cloudwego/cloudwego.github.io/blob/main/content/en/docs/kitex/FAQ/_index.md>
  - <https://github.com/cloudwego/cloudwego.github.io/blob/main/content/en/docs/kitex/Tutorials/options/client_options.md>
  - <https://github.com/cloudwego/cloudwego.github.io/blob/main/content/en/docs/kitex/Tutorials/options/server_options.md>
  - <https://github.com/cloudwego/cloudwego.github.io/blob/main/content/en/docs/kitex/Best%20Practice/usage_attention.md>
  - <https://github.com/cloudwego/cloudwego.github.io/blob/main/content/en/docs/kitex/Best%20Practice/self_check/fast_write_read_panic.md>
  - <https://github.com/cloudwego/cloudwego.github.io/blob/main/content/en/blog/news/Kitex_perf_optimize_practices/index.md>
  - <https://github.com/smallnest/rpcx>
  - <https://hn.algolia.com/api/v1/search?query=kitex%20grpc>
  - <https://hn.algolia.com/api/v1/search?query=cloudwego>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/cloudwego/kitex`) · [data/wave5/enrich/raw/github_com_cloudwego_kitex.json](../../../data/wave5/enrich/raw/github_com_cloudwego_kitex.json) (enrichment confidence 0.6)

</details>
