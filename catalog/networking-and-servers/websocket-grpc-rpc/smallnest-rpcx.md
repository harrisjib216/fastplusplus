# rpcx

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Go RPC framework with its own binary TCP protocol and built-in service governance; 2.3-2.6x grpc-go throughput in author's benchmark.

| | |
|---|---|
| **Beats** | gRPC (grpc-go 1.39.0); also Go standard library net/rpc (Go 1.16.6) |
| **Claimed result** | \~2.3x-2.6x higher throughput than grpc-go 1.39.0 across 100-5000 concurrent clients (249,308 vs 96,463 TPS at 100; 303,287 vs 116,608 at 1000; 317,874 vs 136,108 at 2000; 315,397 vs 121,989 at 5000), and \~1.3x-1.5x over the Go standard library net/rpc (249,308 vs 189,221 at 100; 315,397 vs 204,503 at 5000) (derived from page data: the raw-data table image data.png on the 2021 post) |
| **Workload** | Synchronous RPC with a 581-byte Protobuf BenchmarkMessage: the server sets one field to OK and returns it. Client and server run on the same machine over loopback, with a shared client pool and warmup. Each scenario sends 10,000,000 requests at 100/200/500/1000/2000/5000 concurrent clients, with no simulated processing delay. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Silver 4110 @ 2.10GHz, 2 sockets (the post states 8 physical cores and 32 logical cores with hyper-threading), 128GB RAM; client and server on the same machine over loopback |
| **Compiler and flags** | Go 1.16.6; rpcx 1.6.5, grpc 1.39.0, go std rpc 1.16.6, kitex 0.0.3, arpc 1.1.5; run as ./xxx_server -d 127.0.0.1:8972 and ./xxx_client -c &lt;concurrency&gt; -n 10000000 -s 127.0.0.1:8973 (go build flags not stated) |
| **Adoption** | 8317 stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/smallnest/rpcx) · [benchmark](https://colobu.com/2021/08/01/benchmark-of-rpc-frameworks/) |

## Verdict

The rpcx author's 2021 benchmark ran over loopback (Go 1.16.6, 2x Xeon Silver 4110, 32 threads), with 10M requests per run and 100-5000 concurrent callers sharing 10 client connections. rpcx 1.6.5 echoed a 581-byte gogofaster Protobuf message at 249-318k TPS, against 96-136k for grpc-go 1.39.0 (2.3-2.6x) and 189-219k for Go's net/rpc (1.3-1.5x), and at 5000 callers its mean/P99.9 latency was 15/52 ms against grpc-go's 40/294 ms. Earlier rounds by the same author show a smaller or reversed gap, and no independent reproduction was found.

## Use it when

- Go-to-Go services where you own both ends and want more unary RPC throughput than grpc-go for small (\~0.5-1 KB) Protobuf messages at 100-5000 concurrent callers.
- Teams that want Dubbo-like service governance (registry discovery, weighted/consistent-hash/geo/ping selection, failover, circuit breaking, backup requests) inside the RPC library rather than in a service mesh.
- Code-first services: exposing existing Go methods as RPCs without writing .proto files, with the codec (Protobuf, MessagePack, JSON, raw bytes) chosen per client.
- High-fan-in servers that care about tail latency: in the author's 2021 run, P99.9 at 5000 callers was 52 ms for rpcx and 294 ms for grpc-go.
- Deployments that want to switch transports (TCP, Unix socket, QUIC, KCP, in-process memconn) without changing service code.

## Skip it when

- You need gRPC wire compatibility: grpc-web or browser clients, Envoy/Istio gRPC routing, polyglot clients generated from .proto, or standard gRPC health and reflection tooling. rpcx speaks only its own protocol.
- APIs built on typed streaming: rpcx offers one-way calls, server-to-client push on the same connection and a StreamService that hands you a raw net.Conn on a separate port, but nothing like gRPC's typed client, server or bidirectional streams.
- You need independently reproduced numbers. Every rpcx vs grpc-go result comes from the rpcx author, and the gap changes a lot between rounds: about 1.5x in 2018 (when Go's net/rpc beat rpcx), grpc-go ahead at some concurrency levels in 2019 and 2020, and 2.3-2.6x in 2021.
- Handler-dominated or cross-network workloads: the verified gap is for a near-empty handler over loopback, and real processing time or network round trips shrink the framework's share of latency.
- Servers exposed to untrusted peers on default settings: MaxMessageLength and MaxDecompressedLength default to 0 (unlimited), so a peer can force large allocations or gzip bombs before auth runs.

## How it is fast

Each call is one compact custom frame multiplexed by sequence id over a plain TCP connection. The frame is a 12-byte header (magic byte, version, flag bits, codec byte, 8-byte sequence id) followed by length-prefixed service path, method, metadata and payload, so there is no HTTP/2 framing, HPACK or flow-control windows as in grpc-go. Frames are encoded into size-classed sync.Pool buffers (512 B to 4 KB) and sent with a single conn.Write. Decoded arg/reply structs are recycled through per-type sync.Pools, and each request runs on its own goroutine or, optionally, a pond worker pool (WithPool). In the benchmark both sides used the same gogofaster-generated Protobuf code and 10 pooled client connections, so the gap comes from transport and framework overhead, not the codec.

## Compared with alternatives

Pick rpcx over Kitex (the other Go framework here) if you want a standard-netpoller Go stack with registry-based governance built in. In rpcx's own 2021 run, Kitex 0.0.3 reached 178-213k TPS with P99.9 up to 1,081 ms at 5000 clients, against 249-318k TPS and 52 ms for rpcx; current Kitex was not tested. Choose wtx or grpcxx instead if you must keep the gRPC wire protocol, and cmd-stream-go if you want a lean Go command transport (benchmarked at 1-16 clients) rather than a full microservice framework.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | About 35 direct Go modules at HEAD, including quic-go, kcp-go, godzie44/go-uring, smallnest/gordma, gogo/protobuf, google.golang.org/protobuf, apache/thrift, vmihailenco/msgpack, tinylib/msgp, go-redis, soheilhy/cmux, alitto/pond, rcrowley/go-metrics and rubyist/circuitbreaker. The etcd, ZooKeeper, Consul and Redis registries are separate rpcxio modules. |
| **Minimum toolchain** | Go 1.26 at HEAD (go.mod declares go 1.26.0); the benchmarked rpcx 1.6.5 was built with Go 1.16.6 |
| **Platforms** | Any Go target for TCP/HTTP. The reuseport and Unix-socket listeners are !windows only. The io_uring listener is Linux-only, and the client-side io_uring connection is a stub that falls back to TCP. QUIC, KCP and RDMA are behind build tags, and RDMA needs libibverbs on Linux. |
| **Thread safety** | The maintainer calls XClient thread-safe for concurrent Call/Go (issue #362, where race-detector reports on shutdown flags were later fixed). Use one XClient per service. Calls to a server are multiplexed over one connection, and XClientPool/OneClientPool round-robin several clients. Server handlers run concurrently, one goroutine or pool worker per request. |
| **Drop-in for the baseline** | partial — you can reuse your Protobuf message types as args and replies, but services must be rewritten as Method(ctx, \*Args, \*Reply) error, clients must move to XClient, and rpcx is not wire-compatible with gRPC clients or servers. |

## Gotchas

- client.DefaultOption uses MessagePack, not Protobuf. The benchmark explicitly set option.SerializeType = protocol.ProtoBuffer. Plain structs under the default go through reflection-based vmihailenco/msgpack unless you generate tinylib/msgp code.
- Arg and reply objects that implement Reset() (every generated Protobuf message does) are reset and returned to a sync.Pool as soon as the handler returns. Do not keep them or hand them to other goroutines.
- Message size and decompressed size are unlimited by default. Set WithMaxMessageLength and WithMaxDecompressedLength on any server that accepts untrusted traffic.
- APIs have churned. The 2021 benchmark server sets server.UsePool, which does not exist at HEAD (the pool is now the WithPool option, added in 1.8.0), and the etcd/ZooKeeper/Consul plugins moved to separate modules in 1.7-1.8, so older tutorials' imports break. The README names the stable branch as both v1.7.x and v1.9.4, and open issue #945 reports that six example links on the official site 404 because they point at a main branch instead of master.

## Known shortcomings

- Go, not C++. Rounds of the author's own benchmark disagree: in 2018 Go's standard net/rpc beat rpcx, and in 2019/2020 gRPC led at 100-256 clients; the 2021 run gives about 2.3-2.6x over grpc-go.
- First-party benchmark only, with the gap varying a lot between rounds (grpc-go wins some 2019-2020 points; net/rpc beat rpcx in 2018); no independent reproduction. The benchmark no longer builds against HEAD (server.UsePool removed; WithPool since 1.8.0). Measured setup differs from defaults: Protobuf instead of the default MessagePack, near-empty handler, loopback. MaxMessageLength and MaxDecompressedLength default to 0 (unlimited), allowing memory or gzip-bomb attacks before auth. Pooled args/replies (every generated Protobuf message) are reset and returned to a sync.Pool when the handler returns, so handlers must not keep them. Not wire-compatible with gRPC; streaming is a raw net.Conn on a separate port. HEAD needs Go 1.26; the io_uring client is a stub; reuseport/Unix listeners don't build on Windows. Docs contradict on the stable branch and six site examples 404 (#945).

## Caveats and trade-offs

All results are first-party: the rpcx author runs the benchmark and publishes it on his blog, colobu.com. The rounds in the same benchmark project disagree. The 2018 chart (Go 1.9.0, E5-2630 v3; linked from the rpcx README) shows \~1.5x over grpc-go (\~205k/199k/200k vs \~135k/131k/129k calls/s at 500/2000/5000 clients) and \~2.7-2.9x over Thrift (\~75k/70k/72k). In that round the Go standard library net/rpc (\~290k) beat rpcx. The 2019 table in the rpcx-ecosystem/rpcx-benchmark README has grpc ahead at 256 concurrency (130,642 vs 122,166 TPS) and rpcx only \~1.15x ahead at 512/1024. The 2020 test_data.md has grpc ahead at c=100 (108,928 vs 100,926) and rpcx 1.30x ahead at c=1000 (171,600 vs 132,037). The size of the gap therefore depends heavily on the round, the hardware and the concurrency. The 2021 numbers are in an image table only. HEAD of rpcxio/rpcx-benchmark has since moved to grpc v1.48.0 and rpcx v1.8.33, so reproducing the exact run needs commit 699aab8d. GitHub's license API reports NOASSERTION, but the LICENSE file is the standard Apache License 2.0 notice (Copyright 2017 Chao yuepan).

Uses its own service-discovery/governance stack (zookeeper/etcd/consul) layered on top of the RPC core; multiple codecs supported (Protobuf/JSON/MessagePack) with the compared numbers specific to Protobuf.

## Maintenance

Actively maintained (last commit 2026-09-03, tag v1.9.4, 8.3k stars, 4 open issues) and licensed Apache-2.0: GitHub's API says NOASSERTION, but the file is the standard Apache 2.0 text. It is an ordinary Go module, though HEAD now needs Go 1.26.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The 2021 run is fully disclosed. The post gives CPU, Go 1.16.6, versions of every framework (rpcx 1.6.5, grpc 1.39.0), the exact server/client commands and a raw data table: rpcx 249,308-317,874 TPS against grpc 96,463-136,108. The code is public in rpcxio/rpcx-benchmark (rpcx/, grpc/ and go_stdrpc/ each have server/ and client/ folders; the run commit is 699aab8d, 2021-08-01). The original 2018 evidence is chart-only and gives no framework versions or build commands, so it alone would be weaker.
- **Verifier notes:** The original benchmark_url (rpcx-ecosystem/rpcx-benchmark README) compares against grpc. Its tables are different data (Go 1.7 on E5-2620 v2, and a 2019 table where grpc sometimes wins). The record's numbers come from the colobu.com 2018 chart linked in the rpcx README, and the grpc values match that chart approximately. The Thrift values were misread (the chart shows \~70-75k, not 55-70k). I repointed the evidence to the stronger, fully disclosed 2021 run, which keeps the entry at tier A. License Apache-2.0 confirmed from the file. Last commit 2026-09-03, active, 8317 stars.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/smallnest/rpcx>
  - <https://github.com/smallnest/rpcx/blob/master/LICENSE>
  - <https://github.com/rpcx-ecosystem/rpcx-benchmark>
  - <https://github.com/rpcx-ecosystem/rpcx-benchmark/blob/master/test_data.md>
  - <https://github.com/rpcxio/rpcx-benchmark>
  - <https://github.com/rpcxio/rpcx-benchmark/blob/master/grpc/go.mod>
  - <https://github.com/rpcxio/rpcx-benchmark/blob/master/rpcx/go.mod>
  - <https://colobu.com/2018/01/31/benchmark-2018-spring-of-popular-rpc-frameworks/>
  - <https://colobu.com/2018/01/31/benchmark-2018-spring-of-popular-rpc-frameworks/p0-throughput.png>
  - <https://colobu.com/2021/08/01/benchmark-of-rpc-frameworks/>
  - <https://colobu.com/2021/08/01/benchmark-of-rpc-frameworks/data.png>
- **Sources the enricher read:**
  - <https://github.com/smallnest/rpcx>
  - <https://github.com/smallnest/rpcx/blob/master/README.md>
  - <https://github.com/smallnest/rpcx/blob/master/go.mod>
  - <https://github.com/smallnest/rpcx/blob/master/CHANGELOG.md>
  - <https://github.com/smallnest/rpcx/blob/master/protocol/message.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/server.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/server_conn.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/server_dispatch.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/server_response.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/pool.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/option.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/service.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/stream.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/listener.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/listener_linux.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/listener_unix.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/quic.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/kcp.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/listener_rdma.go>
  - <https://github.com/smallnest/rpcx/blob/master/server/memconn.go>
  - <https://github.com/smallnest/rpcx/blob/master/client/client.go>
  - <https://github.com/smallnest/rpcx/blob/master/client/xclient.go>
  - <https://github.com/smallnest/rpcx/blob/master/client/connection_iouring.go>
  - <https://github.com/smallnest/rpcx/blob/master/client/xclient_pool.go>
  - <https://github.com/smallnest/rpcx/blob/master/client/oneclient_pool.go>
  - <https://github.com/smallnest/rpcx/blob/master/codec/codec.go>
  - <https://github.com/smallnest/rpcx/blob/master/util/buffer_pool.go>
  - <https://github.com/smallnest/rpcx/blob/master/docs/refactor-simplify-design.md>
  - <https://github.com/smallnest/rpcx/issues/362>
  - <https://github.com/smallnest/rpcx/issues/743>
  - <https://github.com/smallnest/rpcx/issues?q=performance>
  - <https://github.com/smallnest/rpcx/issues?q=leak>
  - <https://github.com/smallnest/rpcx/issues/945>
  - <https://github.com/smallnest/rpcx/security/advisories>
  - <https://github.com/rpcxio/rpcx-benchmark>
  - <https://github.com/rpcxio/rpcx-benchmark/blob/699aab8d707efd72f48649760d561cc4f9965d1d/README.md>
  - <https://github.com/rpcxio/rpcx-benchmark/blob/699aab8d707efd72f48649760d561cc4f9965d1d/rpcx/client/rpcx_client.go>
  - <https://github.com/rpcxio/rpcx-benchmark/blob/699aab8d707efd72f48649760d561cc4f9965d1d/rpcx/server/rpcx_server.go>
  - <https://github.com/rpcxio/rpcx-benchmark/blob/699aab8d707efd72f48649760d561cc4f9965d1d/grpc/client/grpc_client.go>
  - <https://github.com/rpcxio/rpcx-benchmark/blob/699aab8d707efd72f48649760d561cc4f9965d1d/grpc/server/grpc_server.go>
  - <https://github.com/rpcxio/rpcx-benchmark/blob/699aab8d707efd72f48649760d561cc4f9965d1d/grpc/pb/gen.sh>
  - <https://github.com/rpcxio/rpcx-benchmark/blob/699aab8d707efd72f48649760d561cc4f9965d1d/proto/gen.sh>
  - <https://github.com/rpcxio/rpcx-benchmark/pull/18>
  - <https://colobu.com/2021/08/01/benchmark-of-rpc-frameworks/>
  - <https://colobu.com/2021/08/01/benchmark-of-rpc-frameworks/data.png>
  - <https://hn.algolia.com/api/v1/search?query=rpcx&tags=story>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/smallnest/rpcx`) · [data/wave5/enrich/raw/github_com_smallnest_rpcx.json](../../../data/wave5/enrich/raw/github_com_smallnest_rpcx.json) (enrichment confidence 0.72)

</details>
