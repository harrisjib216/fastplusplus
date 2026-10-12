# cmd-stream (with MUS codec)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Go client/server framework sending typed Command objects over raw TCP/TLS; author benchmark shows 3.1-4.6x grpc-go echo QPS.

| | |
|---|---|
| **Beats** | gRPC (grpc-go, Protobuf) |
| **Claimed result** | \~3.15x more QPS than grpc-go/Protobuf at 1 client (145,352 vs 46,142 QPS) rising to \~4.56x at 16 clients (288,727 vs 63,285 QPS) (derived from page data: results/qps/qps.csv) |
| **Workload** | Echo-style Distributed-Command-Pattern RPC over TCP with 30ms simulated server processing delay, payloads 17-1024 bytes, 1/2/4/8/16 concurrent client goroutines (go test -bench BenchmarkQPS). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 PRO 5850U with Radeon Graphics, Debian 6.1.148-1 x86_64 (single laptop, charger connected, fan at full speed) |
| **Compiler and flags** | Go 1.24.1; go test -bench BenchmarkQPS -count=10 -timeout=30m |
| **Adoption** | 94 stars |
| **Last commit** | 2026-05-07 |
| **Links** | [repository](https://github.com/cmd-stream/cmd-stream-go) · [benchmark](https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/qps/qps.csv) |

## Verdict

The run is the author's own go-client-server-benchmarks: localhost on one Ryzen 7 PRO 5850U laptop, Go 1.24.1, grpc-go v1.80.0 vs cmd-stream v0.7.1, 4 KB I/O buffers for every framework, a 30 ms server sleep per echo, and every request fired at once in its own goroutine. Over 1-16 connections, cmd-stream/MUS reached 145k-289k QPS against grpc-go's 46k-77k (3.1-4.6x); the Protobuf codec gave 2.4-3.5x and JSON 1.5-2.5x. A fixed burst of 100,000 requests finished 2.7-3.4x faster (0.38-0.61 s vs 1.03-2.09 s).

## Use it when

- Go-only service-to-service links where you own both client and server and need neither gRPC interop nor gRPC tooling.
- Throughput-bound fan-in with a very large number of small requests in flight at once (the benchmark used 17-1024 B payloads, all fired at once), where grpc-go's per-call CPU and allocation cost is the bottleneck.
- Workloads that already fit a command/job model (sagas, persisted or replayable commands), or that need several Results per request without HTTP/2 streaming.
- Teams that can add generated MUS serializers for peak speed. If you keep .proto messages, the Protobuf codec still measured 2.4-3.5x grpc-go in the author's run.

## Skip it when

- Polyglot systems or public APIs. It is Go-only with a custom wire format: no gRPC or HTTP interop, and no grpcurl, gRPC-Gateway or service-mesh support.
- Latency-bound calls across a real network. The only published numbers are from localhost on one laptop, and the author agreed on HN that they measure protocol overhead, not network latency.
- When you need built-in compression, application-level retries, server-side cancellation/deadline propagation, or multi-endpoint balancing. The author says on HN that compression and retries are not provided, and the other two are missing from the code: Sender dials a single address and ctx only bounds the client-side wait.
- Servers exposed to untrusted clients without extra hardening. Every Command runs in its own goroutine with no per-connection concurrency limit, the JSON and Protobuf codecs accept any payload length unless WithMaxLen is set, and authentication is mTLS only.
- Risk-averse production use. The API is pre-1.0 (v0.7.3) and v0.7.0 (May 2026) changed the Cmd.Exec signature. One maintainer wrote 234 of 236 commits, and pkg.go.dev lists no importers outside the author's own repos.

## How it is fast

Each message on the connection is a varint sequence number, a type tag and the payload, with no HTTP/2 frames, HPACK headers or per-stream flow control, and many concurrent Commands share one connection. Writes go into a bufio.Writer, and a CAS flag coalesces flushes on both client and server, so concurrent senders on a connection share one Flush (one write syscall). The MUS codec (mus-stream-go) writes generated serializers straight into the stream, while the JSON and Protobuf codecs marshal into a temporary []byte first. The transport, not the codec, gives most of the gain: cmd-stream with the Protobuf codec still reaches 2.4-3.5x grpc-go QPS, and in the fixed run MUS used about 16 allocs and 3 KB per request against about 139 allocs and 12 KB for grpc-go.

## Compared with alternatives

Pick it over the Go siblings rpcx and Kitex (catalogued at 2.3-2.6x and 1.5-1.7x grpc-go, each on its own benchmark) when both ends are Go, you want the largest cut in per-request overhead, and you accept the command model. In its author's suite, cmd-stream/MUS reached 2.7-5.4x the QPS of Kitex run in gRPC-transport mode. Choose the gRPC-compatible siblings (grpcxx, wtx) or the C++ frameworks (brpc, SRPC) instead when you need cross-language clients or standard gRPC wire compatibility, which cmd-stream gives up.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | mus-format/mus-stream-go, mus-format/common-go, ymz-ncnk/jointwork-go, plus one codec module (codec-json-go, codec-protobuf-go or codec-mus-stream-go; the Protobuf and MUS codecs need code generation) |
| **Minimum toolchain** | Go 1.24.1 (go directive in go.mod) |
| **Platforms** | Any Go target. Built on net.Conn: TCP, TLS and mutual TLS are documented, and NewClient accepts any net.Conn |
| **Thread safety** | Client and Sender are documented as thread-safe and multiplex concurrent Sends. The server runs each Command in its own goroutine, so the Receiver/Invoker must be thread-safe (documented), and Proxy.Send must be safe to call from several goroutines |
| **Drop-in for the baseline** | no |

## Gotchas

- Server WorkersCount (default 8) is the maximum number of connections served at once. Each worker owns one connection for that connection's whole life, and later connections wait in a queue. Size it to your total client connections, as the benchmark does (WorkersCount = client count). Sender defaults to a single connection (ClientsCount=1).
- If Command.Exec returns an error, or the codec fails, the server closes the whole connection and every in-flight Command on it fails; the author's stress test uses a FailCmd to drop connections this way. Send application errors back as Result values instead.
- Cancelling or timing out ctx on the client only abandons the wait (Forget); the server keeps running the Command. SendWithDeadline sets a socket write deadline and does not pass a deadline to the server.
- Core client bugs were fixed only recently: a deadlock on unexpected results (#4, May 2026) and keepalive breaking reconnect (#3, Apr 2026). Codec modules are pseudo-versioned, so pin a matched release set from VERSIONS.md.

## Known shortcomings

- Go, not C++. The benchmark repo is run by the cmd-stream author, and most of the gain is raw TCP vs HTTP/2 (cmd-stream with Protobuf also beats gRPC), not the MUS codec. A 100,000-request run shows a smaller gap (about 2.7-3.4x).
- Only an author-run localhost benchmark on one laptop: all requests launched at once with a 30 ms server sleep, so it measures protocol overhead with huge numbers in flight (the author agreed on HN); the 'p99' column is p99.9 and includes queueing; 4 KB I/O buffers for all; tested v0.7.1; Kitex ran in gRPC-transport mode. Most of the gain is the raw-TCP transport, not MUS (Protobuf still 2.4-3.5x, JSON 1.5-2.5x over grpc-go). Not a gRPC drop-in: command pattern, Go-to-Go only, no gRPC/HTTP interop, codec registration and codegen. Server WorkersCount (default 8) caps concurrent connections; later connections queue. An Exec error closes the whole connection and fails every in-flight command. No server-side cancellation. No compression, retries or multi-server balancing. Unbounded goroutines per command and unlimited JSON/Protobuf lengths unless WithMaxLen is set; mutual TLS is the only auth. Pre-1.0 (v0.7.0 broke Cmd.Exec), one maintainer, no outside importers; client deadlock (#4) and keepalive-reconnect (#3) bugs fixed only in 2026.

## Caveats and trade-offs

The benchmark repo (ymz-ncnk/go-client-server-benchmarks, 17 stars) is maintained by the cmd-stream author, so it is not independent. Methodology, code, Go version and CPU are fully disclosed, so it stays at tier A. The run is on a single laptop, not a controlled server, and no variance is reported beyond -count=10. The comparison is cmd-stream over raw TCP against gRPC over HTTP/2. The protobuf codec on cmd-stream also beats gRPC (108788 vs 46142 QPS at 1 client), so most of the gain comes from the transport, not from the MUS codec. The fixed-count run (100,000 requests, sec.csv) shows a smaller gap: 0.612s vs 2.091s at 1 client (\~3.4x) and 0.383s vs 1.033s at 16 clients (\~2.7x).

Custom Distributed Command Pattern rather than classic request/response RPC; peak speedup requires the companion MUS binary codec (codec-mus-stream-go), which needs code generation; JSON codec variant is much closer to gRPC in throughput.

## Maintenance

Maintained but quiet: the last commit on main is the v0.7.3 release (2026-05-07), and only dependabot PRs have arrived since. It is an MIT-licensed, go-gettable module, but pre-1.0 with frequent breaking releases and a single maintainer.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** qps.csv has cmd-stream_tcp_mus 145352 vs grpc_http2_protobuf 46142 at 1 client and 288727 vs 63285 at 16 clients, so both ratios check out. The benchmark code is public (go-client-server-benchmarks: benchmarks_test.go, cmdstream_test.go, grpc_test.go; go.mod pins grpc v1.80.0), and the README states Go 1.24.1, the exact go test commands and the Ryzen 7 PRO 5850U CPU.
- **Verifier notes:** The numbers match exactly. last_commit is corrected: the latest commit on main is c4737bcb dated 2026-05-07. The 2026-06-07 date was repo pushed_at, which comes from dependabot/feature branches. The status is still active. MIT, 94 stars, not a fork or archived.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cmd-stream/cmd-stream-go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/qps/qps.csv>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/qps/benchmarks.txt>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/benchmarks_test.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/fixed/sec.csv>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/go.mod>
- **Sources the enricher read:**
  - <https://github.com/cmd-stream/cmd-stream-go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/go.mod>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/VERSIONS.md>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/SECURITY.md>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/cmdstream.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/core.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/cmd.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/result.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/proxy.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/cln/client.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/cln/options.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/srv/server.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/srv/options.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/srv/worker.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/srv/conn_receiver.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/core/srv/conn_receiver_options.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/transport/transport.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/transport/codec_transport.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/transport/options.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/transport/codec.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/handler/handler.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/handler/invoker.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/handler/options.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/handler/proxy.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/server/options.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/server/server.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/server/codec.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/server/invoker.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/sender/sender.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/sender/options.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/sender/handler.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/sender/options_make.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/delegate/cln/client_info_delegate.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/delegate/cln/keepalive.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/delegate/srv/server_info_delegate.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/delegate/srv/options.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/delegate/server_info.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/group/strategy_round-robin.go>
  - <https://github.com/cmd-stream/cmd-stream-go/blob/main/client/options.go>
  - <https://github.com/cmd-stream/cmd-stream-go/issues>
  - <https://github.com/cmd-stream/cmd-stream-go/issues/3>
  - <https://github.com/cmd-stream/cmd-stream-go/issues/4>
  - <https://github.com/cmd-stream/cmd-stream-go/pulls>
  - <https://github.com/cmd-stream/cmd-stream-go/releases>
  - <https://github.com/cmd-stream/cmd-stream-go/releases/tag/v0.7.0>
  - <https://github.com/cmd-stream/cmd-stream-go/commits/main>
  - <https://github.com/cmd-stream/cmd-stream-go/graphs/contributors>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/go.mod>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/benchmarks_test.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/cmdstream_test.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/grpc_test.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/common/const.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/projects/cmd-stream/server.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/projects/cmd-stream/sender.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/projects/cmd-stream/tcp_mus/exchange.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/projects/cmd-stream/tcp_mus/echo_cmd.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/projects/cmd-stream/tcp_mus/receiver.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/projects/grpc/http2_protobuf/client.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/projects/grpc/http2_protobuf/server.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/projects/grpc/http2_protobuf/exchange.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/projects/kitex/grpc_protobuf/client.go>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/qps/qps.csv>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/qps/benchmarks.txt>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/fixed/benchmarks.txt>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/fixed/sec.csv>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/fixed/cop.csv>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/fixed/med.csv>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/fixed/p99.csv>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/fixed/max.csv>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/fixed/b.csv>
  - <https://github.com/ymz-ncnk/go-client-server-benchmarks/blob/main/results/fixed/allocs.csv>
  - <https://github.com/cmd-stream/codec-mus-stream-go>
  - <https://github.com/cmd-stream/codec-go/blob/main/codec.go>
  - <https://github.com/cmd-stream/codec-go/blob/main/options.go>
  - <https://github.com/cmd-stream/codec-json-go/blob/main/serializer.go>
  - <https://github.com/cmd-stream/examples-go>
  - <https://github.com/cmd-stream/examples-go/blob/main/rpc/README.md>
  - <https://github.com/cmd-stream/examples-go/blob/main/rpc/service.go>
  - <https://github.com/cmd-stream/stress-test-go>
  - <https://github.com/cmd-stream/stress-test-go/blob/main/cmds.go>
  - <https://github.com/grpc/grpc-go/blob/v1.80.0/internal/transport/defaults.go>
  - <https://github.com/grpc/grpc-go/blob/v1.80.0/server.go>
  - <https://github.com/grpc/grpc-go/blob/v1.80.0/dialoptions.go>
  - <https://hn.algolia.com/api/v1/search?query=cmd-stream&tags=story>
  - <https://hn.algolia.com/api/v1/items/44647772>
  - <https://hn.algolia.com/api/v1/items/36984073>
  - <https://news.ycombinator.com/item?id=44647772>
  - <https://news.ycombinator.com/item?id=36984073>
  - <https://pkg.go.dev/github.com/cmd-stream/cmd-stream-go?tab=importedby>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/cmd-stream/cmd-stream-go`) · [data/wave5/enrich/raw/github_com_cmd_stream_cmd_stream_go.json](../../../data/wave5/enrich/raw/github_com_cmd_stream_cmd_stream_go.json) (enrichment confidence 0.8)

</details>
