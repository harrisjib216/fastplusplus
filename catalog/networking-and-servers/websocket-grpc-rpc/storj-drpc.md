# DRPC

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Storj's small Go replacement for grpc-go, using its own framed protocol instead of HTTP/2; not wire-compatible with gRPC.

| | |
|---|---|
| **Beats** | gRPC |
| **Claimed result** | Unitary time/op is 68-72% lower than gRPC (small: 29.7us-&gt;8.3us; large: 1.70ms-&gt;0.54ms), and unitary speed is +214% to +243% (large: 618MB/s-&gt;1939MB/s). Across all call types and sizes, time/op is 46-73% lower and speed is +86% to +263%. Streaming calls with small and medium payloads show smaller gains (about +86% to +176%). |
| **Workload** | In-process microbenchmark of unary, input-stream, output-stream, and bidirectional-stream RPC calls at three payload sizes (small/medium/large), no real network transport involved |
| **Metric** | latency, throughput |
| **Adoption** | 1.6k stars (1,632); README says it has been used in production for years across tens of thousands of servers |
| **Last commit** | 2026-08-18 |
| **Links** | [repository](https://github.com/storj/drpc) · [benchmark](https://github.com/storj/drpc#benchmarks) |

## Verdict

Go testing benchmarks in internal/grpccompat compare DRPC with grpc-go v1.64.0 (README refreshed 2024-05-31). Both run over an in-memory io.Pipe with one connection and one sequential caller, with DRPC using ManualFlush. Messages are a few bytes, 2 KiB or 1 MiB. Time per op fell 46-73% (unary 68-72%), throughput rose 86-263%, and allocations fell 83-97%. No hardware or Go version is stated, and the README says the environment was not controlled and neither side was tuned.

## Use it when

- Go-only services on protobuf and grpc-go where per-call CPU, allocations or GC pressure matter. Storj reported 81% of one storage node's heap in gRPC before switching.
- Large messages of about 1 MiB, unary or streaming: the README shows about 3x grpc-go's throughput (for example 618 MB/s vs 1939 MB/s unary)
- Custom or unusual transports, including reverse connections where the TCP client serves the RPCs, because DRPC only needs a byte stream
- Builds sensitive to binary size or dependency count: go.mod has 3 requirements and the core is about 3,600 lines

## Skip it when

- Polyglot systems: only Go is complete. The C++, Rust and Node ports are marked Incomplete, and JS/web and Python support are open issues.
- Many concurrent RPCs to one peer over a single connection: calls on one Conn are serialized, so you need drpcpool, a yamux-based third-party package or QUIC streams
- Setups that need gRPC ecosystem features, such as built-in load balancing, name resolution, service config, or interop with gRPC proxies and non-Go gRPC clients
- Network-bound workloads: the published speedup excludes the network, so end-to-end gains will be smaller

## How it is fast

DRPC drops HTTP/2 (no HPACK, header parsing or flow-control windows). Each frame is a 1-byte header (control bit, 6-bit kind, done bit) plus protobuf varints for stream ID, message ID and length. There is no stream multiplexing: a size-1 semaphore allows one active RPC per connection, and the reader rejects stream IDs that do not increase, which keeps packet reassembly simple. The client marshals into one reused buffer per connection (MarshalAppend), so a unary call makes 7-9 allocations against 182-280 for grpc-go in the README table.

## Compared with alternatives

Pick DRPC over rpcx, Kitex or cmd-stream when you want to keep your .proto files and grpc-go-shaped generated Go code with a 3-dependency core, rather than adopt a different framework or codec. Note that those siblings report multi-client QPS, while DRPC's numbers come from one in-process connection, so they are not directly comparable. If you must stay wire-compatible with existing gRPC clients, look at wtx (Rust) instead.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/zeebo/errs, google.golang.org/protobuf (github.com/zeebo/assert for tests) |
| **Minimum toolchain** | Go 1.19 (go.mod); protoc plus protoc-gen-go-drpc for code generation |
| **Platforms** | any Go target (pure Go) |
| **Thread safety** | Conn can be shared, but only one Invoke or stream is active at a time. Other callers block on a semaphore until it finishes or their context is canceled; nothing is multiplexed. |
| **Drop-in for the baseline** | partial — generated Go client and server interfaces mirror grpc-go, so application code changes little. The wire protocol differs, so both ends must switch; drpcmigrate.ListenMux can serve gRPC and DRPC on one port during the move. |

## Gotchas

- Canceling a context while its RPC is still unfinished closes the whole connection by default. drpcmanager.Options.SoftCancel sends a cancel message instead. Issue #37, open since 2022, reports pooled connections failing with context.Canceled after an earlier cancel.
- Messages larger than 4 MiB fail with a 'data overflow' protocol error. Raise drpcwire.ReaderOptions.MaximumBufferSize to allow larger ones.
- The published benchmark enables drpcstream ManualFlush. With it on, you must type-assert the stream and call RawFlush yourself, so default-config numbers may differ.
- drpcpool caps how many idle connections it caches, but it does not limit concurrency, so a burst of concurrent calls dials a burst of connections

## Known shortcomings

- Benchmark is in-process over io.Pipe, one connection, one sequential caller, DRPC with ManualFlush vs default grpc-go (v1.64.0, refreshed 2024-05); no hardware or Go version; the README says neither side was tuned. One RPC per connection at a time (semaphore of 1); concurrency needs drpcpool, yamux or QUIC, so multi-client QPS numbers of rpcx/Kitex/cmd-stream are not comparable. Cancelling a context mid-RPC closes the whole connection unless SoftCancel is set (#37 open since 2022, flaky pooled test). 4 MiB default message limit ('data overflow'). Not wire-compatible with gRPC (drpcmigrate.ListenMux helps migrate). Go only; C++/Rust/Node ports incomplete. v1.0.0 (2025-07) but README still says beta; original author left Storj; sparse commits.

## Caveats and trade-offs

The README explicitly states the benchmark was not run in a controlled environment (CPU scaling not disabled, not noiseless) and that the comparison inherently favors DRPC because its author is more familiar with its internals -- capped at tier C for these self-admitted methodology gaps

Smaller feature surface than gRPC (fewer official language implementations, some marked Incomplete); microbenchmark is in-process only, so it excludes the network/transport cost that dominates real RPC latency

## Maintenance

Maintained but slow-moving: v1.0.0 was tagged in 2025 and the last commit was 2026-08-18. The original author has left Storj, and Storj staff keep it going. It is MIT-licensed, pure Go and small enough to audit or vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party in-process microbenchmark table in the README comparing against gRPC. Benchmark code is public (internal/grpccompat/benchmark_test.go), but no hardware, Go version or flags are given, and the README admits the environment was uncontrolled and untuned.
- **Verifier notes:** The record's '+214% to +243%' throughput range applies only to unitary calls, so I clarified it with the full range from the table. Metadata was checked via github.com HTML and the atom feed because the API was rate-limited: MIT, last commit 2026-08-18, not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/storj/drpc>
  - <https://raw.githubusercontent.com/storj/drpc/main/README.md>
  - <https://raw.githubusercontent.com/storj/drpc/main/LICENSE>
  - <https://github.com/storj/drpc/tree/main/internal>
  - <https://github.com/storj/drpc/tree/main/internal/grpccompat>
  - <https://github.com/storj/drpc/commits.atom>
- **Sources the enricher read:**
  - <https://github.com/storj/drpc>
  - <https://raw.githubusercontent.com/storj/drpc/main/README.md>
  - <https://raw.githubusercontent.com/storj/drpc/main/go.mod>
  - <https://raw.githubusercontent.com/storj/drpc/main/doc.go>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcconn/conn.go>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcconn/README.md>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcmanager/manager.go>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcmanager/README.md>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcwire/packet.go>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcwire/doc.go>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcwire/reader.go>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcpool/README.md>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcstream/README.md>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcmigrate/README.md>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcserver/README.md>
  - <https://raw.githubusercontent.com/storj/drpc/main/drpcenc/README.md>
  - <https://raw.githubusercontent.com/storj/drpc/main/internal/grpccompat/benchmark_test.go>
  - <https://raw.githubusercontent.com/storj/drpc/main/internal/grpccompat/common_test.go>
  - <https://raw.githubusercontent.com/storj/drpc/main/internal/grpccompat/go.mod>
  - <https://raw.githubusercontent.com/storj/drpc/main/internal/grpccompat/README.md>
  - <https://github.com/storj/drpc/tree/main/internal/grpccompat>
  - <https://github.com/storj/drpc/wiki/Docs:-Wire-protocol>
  - <https://github.com/storj/drpc/tags>
  - <https://github.com/storj/drpc/commits.atom>
  - <https://github.com/storj/drpc/commit/94aa9aa61011ae6e7ed3d23a963ba67da97c1ccb.patch>
  - <https://github.com/storj/drpc/issues>
  - <https://github.com/storj/drpc/issues/14>
  - <https://github.com/storj/drpc/issues/37>
  - <https://github.com/storj/drpc/issues/39>
  - <https://github.com/storj/drpc/issues/56>
  - <https://www.storj.io/blog/introducing-drpc-our-replacement-for-grpc>
  - <https://storj.github.io/drpc/docs.html>
  - <https://hn.algolia.com/api/v1/search?query=drpc%20storj&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=drpc&tags=comment&hitsPerPage=20>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/storj/drpc`) · [data/wave5/enrich/raw/github_com_storj_drpc.json](../../../data/wave5/enrich/raw/github_com_storj_drpc.json) (enrichment confidence 0.8)

</details>
