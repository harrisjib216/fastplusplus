# fRPC (frpc-go)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟡 stale

> Go proto3 RPC generator that swaps gRPC's HTTP/2 and Protobuf for 8-byte-header TCP framing and Polyglot encoding.

| | |
|---|---|
| **Beats** | gRPC |
| **Claimed result** | Per-client throughput is 2-4x gRPC depending on message size, per the page: 32B about 4x (112 vs 29 RPC/s per client at 8192 clients); 512B '2-3x' (98 vs 29); 128KB '3-4x' (192 vs 65 at 100 clients); 1MB is claimed '3-4x', but the page's own totals (about 3.6 vs 1.7 GB/s) are about 2.1x (derived from page data). Server throughput is more than 2,000,000 RPC/s vs just under 500,000 for gRPC at 8192 clients (over 4x). With 50us of blocking work it is about 1,600,000 vs about 400,000 RPC/s. |
| **Workload** | Echo RPC service (same proto3 file and service implementation for both) at 32B, 512B, 128KB and 1MB message sizes with increasing concurrent clients (up to 8192). Also a server-throughput test with 10 concurrent RPCs per client, and a variant with 50-microsecond time.Sleep blocking server work in goroutine-per-RPC mode. |
| **Metric** | throughput |
| **Hardware** | Bare-metal host running Debian 11, 2x AMD EPYC 7643 48-core CPUs, 256GB DDR4, local network |
| **Adoption** | 462 stars |
| **Last commit** | 2025-09-22 |
| **Links** | [repository](https://github.com/loopholelabs/frpc-go) · [benchmark](https://frpc.io/performance/grpc-benchmarks) |

## Verdict

These are first-party results from August 2022 code: fRPC on frisbee-go v0.6.0 against grpc-go v1.48.0 with a default grpc.NewServer(), a single-string-field echo proto, go.mod 'go 1.18', and the actual Go toolchain and flags not stated, on a bare-metal Debian 11 host with 2x AMD EPYC 7643 and 256 GB RAM over a local network. fRPC reached 112 vs 29 RPC/s per client at 32 B and 98 vs 29 at 512 B (8192 clients), 192 vs 65 at 128 KB (100 clients), and about 3.6 vs 1.7 GB/s at 1 MB (about 2.1x, although the page says 3-4x); server throughput was over 2M vs just under 500k RPC/s, and about 1.6M vs 400k with a 50 us sleep in the default goroutine-per-RPC mode.

## Use it when

- Go-to-Go services you own on both ends, on a trusted network, where you want proto3 schemas without HTTP/2 and Protobuf overhead.
- Many small, non-blocking unary RPCs per connection (echo, metrics, telemetry), where the single-goroutine-per-connection mode applies.
- Thousands of concurrent client connections to one server; this is where the project's benchmark shows grpc-go's per-client throughput falling off hardest (112 vs 29 RPC/s per client at 8192 clients).
- Protocols that mix request/reply with custom Frisbee messaging patterns (e.g. pub/sub) or hand the TCP connection to something else after the RPCs.

## Skip it when

- Any non-Go peer, browser, gRPC tooling (grpcurl, reflection) or gRPC-aware proxy or mesh: the wire format is Frisbee plus Polyglot, and the roadmap still lists JS/TS, Rust and WebSocket support as planned.
- Rolling deploys where client and server run different schema versions: Polyglot encodes fields in declaration order with no tags, and the maintainers confirmed on HN (2022) that it lacks protobuf's forward/backward compatibility.
- When you rely on gRPC features: there is no built-in load balancing or retries (per the roadmap), no status codes (errors go over the wire as Polyglot error values), no interceptor/metadata API, and no deadline propagation (ctx cancellation only stops the client waiting).
- Untrusted or internet-facing peers: the 32-bit length field is honored with no max-message-size check, so the read buffer grows to whatever size the peer declares.
- Anything needing an active upstream: the README calls it early Alpha, the last code change was November 2024, and later commits are only dependency bumps.

## How it is fast

HTTP/2 framing is replaced by Frisbee's fixed 8-byte packet header (uint16 request id, uint16 operation, uint32 length) on a plain TCP or TLS net.Conn. Protobuf is replaced by Polyglot, which writes fields positionally with typed encode calls and no field tags. Packets and header buffers come from pools, and the unary server handler reuses the incoming packet as the response buffer. Writes go into a 64 KiB bufio.Writer that a separate flush goroutine drains, so many small RPCs are coalesced into fewer syscalls; the headline numbers also used the mode that runs handlers inline on each connection's goroutine instead of spawning one per RPC.

## Compared with alternatives

Pick fRPC over rpcx or cmd-stream when you want to keep proto3 files and grpc-go-shaped handler signatures while generating Go-only code. Its claimed gap over grpc-go (roughly 2-4x) is in the same band as rpcx (2.3-2.6x) and cmd-stream (3.2-4.6x), so let its alpha status and stale maintenance, not the numbers, decide.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Build time: protoc (proto3) and the protoc-gen-go-frpc plugin. Runtime (go.mod): github.com/loopholelabs/frisbee-go v0.10.2, github.com/loopholelabs/polyglot/v2, github.com/loopholelabs/logging. |
| **Minimum toolchain** | Go 1.22 (go.mod and README badge; the docs site still says 1.18+) |
| **Platforms** | Any platform Go supports, over any net.Conn transport; no OS- or CPU-specific code found |
| **Thread safety** | Generated client methods can be called concurrently: the id counter and in-flight map are mutex-guarded. Frisbee's SetConcurrency doc says server handlers must be thread-safe when they share state across connections, and also per connection unless concurrency is 1. |
| **Drop-in for the baseline** | partial — server handler signatures match grpc-go, so service code ports with little change; client/server construction differs (NewServer(svc..., \*tls.Config, logger), a single NewClient), the wire protocol is not gRPC so every peer must switch, and oneof, interceptors, status codes, load balancing and retries are missing |

## Gotchas

- The published numbers used SetConcurrency(1) (the benchmark server sets it unless sleeping), not the default of one goroutine per RPC. In that mode handlers run inline on the connection's read goroutine, so one slow handler stalls every RPC on that connection.
- oneof is not rejected: the generator flattens it into ordinary struct fields and encodes all of them, with no 'which field is set' semantics. The README lists OneOf as unsupported.
- Unary request ids are uint16, per method, per client, and wrap around. More than 65,535 concurrent in-flight calls to one method on one client can collide in the in-flight map.
- Frisbee applies a fixed 5 s deadline (DefaultDeadline) to every socket read and write and sends a PING every 500 ms (DefaultPingInterval), and the generated fRPC API exposes neither. A write that cannot complete within 5 s closes the connection.

## Known shortcomings

- Benchmark measured 2022 code (frisbee-go v0.6.0 vs default grpc-go v1.48.0); the shipped release (frisbee v0.10.2) was never measured; toolchain and flags not stated. Headline numbers use SetConcurrency(1), where one slow handler stalls every RPC on the connection; the default mode appears only in the 50 us sleep test (\~1.6M vs 400k RPC/s). Echo of a single string field, so Polyglot vs Protobuf is barely tested. The page's '3-4x' at 1 MB is \~2.1x by its own totals. No schema evolution (no field tags; regenerate both sides); oneof silently flattened. Not gRPC-compatible, Go-only, no load balancing, retries, status codes, interceptors or server-side deadlines. uint16 request ids per method wrap past 65,535 in-flight calls; no max message size (peer-declared 32-bit length); fixed 5 s deadlines and 500 ms ping not configurable. Docs outdated (Go 1.18 vs go.mod 1.22; streaming 'unsupported'). Last real code change 2024-11; README still says early Alpha.

## Caveats and trade-offs

Benchmark is on the project's own docs site (first-party). The hardware is stated, but the Go version and build flags are not. The linked benchmark repo (loopholelabs/frpc-go-benchmarks) was archived on Jul 21, 2026. The 1MB section's '3-4x' contradicts its own totals (about 2.1x). The main results used fRPC's non-default single-goroutine-per-connection mode.

fRPC was still Alpha per its own README (missing OneOf message types); relies on the loopholelabs/frisbee-go messaging layer; smaller ecosystem/tooling maturity than gRPC

## Maintenance

Stale: the last commit was 2025-09-22 (dependency bumps), the last release v0.10.2 on 2024-11-07, Dependabot PRs including a frisbee-go 0.11.0 bump sit unmerged, and the benchmark repo was archived on 2026-07-21. It is Apache-2.0 and small enough to vendor (Go templates plus a generator), but you also inherit frisbee-go and polyglot.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party docs page with public benchmark code (loopholelabs/frpc-go-benchmarks, now archived) and a stated CPU model (2x AMD EPYC 7643). The Go version and build flags are not stated, so it is not A, and it is not independent.
- **Verifier notes:** The record's '\~3-4x across tested message sizes' slightly overstated the 512B case (the page says 2-3x), so I corrected it. The tier stays C. Metadata was checked via github.com HTML and the atom feed: Apache-2.0 (LICENSE.md), 462 stars, last commit 2025-09-22 (just over 12 months, so stale), frpc-go itself not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://frpc.io/performance/grpc-benchmarks>
  - <https://github.com/loopholelabs/frpc-go>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/README.md>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/LICENSE.md>
  - <https://github.com/loopholelabs/frpc-go/commits.atom>
  - <https://github.com/loopholelabs/frpc-go-benchmarks>
- **Sources the enricher read:**
  - <https://github.com/loopholelabs/frpc-go>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/README.md>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/go.mod>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/templates/server.templ>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/templates/client.templ>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/templates/constants.templ>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/templates/interfaces.templ>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/templates/imports.templ>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/templates/customDecode.templ>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/pkg/generator/generator.go>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/pkg/generator/test/test.frpc.go>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go/main/examples/test/test.proto>
  - <https://github.com/loopholelabs/frpc-go/issues>
  - <https://github.com/loopholelabs/frpc-go/pulls>
  - <https://frpc.io/performance/grpc-benchmarks>
  - <https://frpc.io/performance/twirp-benchmarks.md>
  - <https://frpc.io/llms.txt>
  - <https://frpc.io/introduction.md>
  - <https://frpc.io/getting-started/overview.md>
  - <https://frpc.io/getting-started/quick-start.md>
  - <https://frpc.io/getting-started/concepts.md>
  - <https://frpc.io/getting-started/architecture.md>
  - <https://frpc.io/getting-started/roadmap.md>
  - <https://frpc.io/performance/optimizations.md>
  - <https://frpc.io/reference/server-methods.md>
  - <https://frpc.io/reference/client-methods.md>
  - <https://github.com/loopholelabs/frisbee-go>
  - <https://github.com/loopholelabs/frisbee-go/issues>
  - <https://raw.githubusercontent.com/loopholelabs/frisbee-go/v0.10.2/README.md>
  - <https://raw.githubusercontent.com/loopholelabs/frisbee-go/v0.10.2/frisbee.go>
  - <https://raw.githubusercontent.com/loopholelabs/frisbee-go/v0.10.2/async.go>
  - <https://raw.githubusercontent.com/loopholelabs/frisbee-go/v0.10.2/server.go>
  - <https://raw.githubusercontent.com/loopholelabs/frisbee-go/v0.10.2/conn.go>
  - <https://raw.githubusercontent.com/loopholelabs/frisbee-go/v0.10.2/options.go>
  - <https://raw.githubusercontent.com/loopholelabs/frisbee-go/v0.10.2/pkg/metadata/metadata.go>
  - <https://github.com/loopholelabs/frpc-go-benchmarks>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go-benchmarks/master/go.mod>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go-benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go-benchmarks/master/frpc/server/main.go>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go-benchmarks/master/grpc/server/main.go>
  - <https://raw.githubusercontent.com/loopholelabs/frpc-go-benchmarks/master/frpc/client/main.go>
  - <https://hn.algolia.com/api/v1/search?query=fRPC&tags=story>
  - <https://hn.algolia.com/api/v1/items/32593197>
  - <https://hn.algolia.com/api/v1/items/32616794>
  - <https://hn.algolia.com/api/v1/items/42104528>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/loopholelabs/frpc-go`) · [data/wave5/enrich/raw/github_com_loopholelabs_frpc_go.json](../../../data/wave5/enrich/raw/github_com_loopholelabs_frpc_go.json) (enrichment confidence 0.75)

</details>
