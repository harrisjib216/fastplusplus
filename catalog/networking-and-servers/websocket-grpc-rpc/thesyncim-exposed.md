# Exposed (reflectionless RPC for Go)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [WebSocket, gRPC and RPC](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🔴 abandoned

> Go RPC library over one batched TCP connection, derived from valyala/fastrpc; README shows \~1.1-3x gRPC echo throughput.

| | |
|---|---|
| **Beats** | gRPC |
| **Claimed result** | README table, 8-byte payload, 1 client, concurrency 50: exposed 527,199.3 op/s vs grpc 394,620.7 op/s (\~1.34x, derived from page data); total memory allocated 472 MB vs 1.4 GB; GC count 111 vs 538. Best mid-size case: 8B, 5 clients, concurrency 5000: 1,003,451.8 vs 329,039.9 op/s (\~3.0x, derived). gRPC is faster in some rows (8B/10 clients/concurrency 50 and 500; 128B/10/50 and 500; 32768B/1/5000). The README has no prose claim of winning across nearly all scenarios; that is a reading of the table. Rows at 32K/64K payload with concurrency 50000 show gRPC at \~0 op/s (failed runs), so ratios from those rows are meaningless. |
| **Workload** | Echo-style RPC round trips, server and client on the same machine; payload 8/128/1024/32768/65536 bytes x 1/5/10 clients x concurrency 1/50/500/5000/50000 (as labelled in the README); reports op/s, MB/s, p50/p95/p99/max latency, GC count and total memory allocated. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-7700HQ @ 2.80GHz, 8GB RAM |
| **Adoption** | 27 stars |
| **Last commit** | 2018-08-02 |
| **Links** | [repository](https://github.com/thesyncim/exposed) · [benchmark](<https://github.com/thesyncim/exposed (README benchmark table)>) |

## Verdict

The README's single table compares exposed with grpc-go (gRPC version, codecs and Go version unstated) on one Intel i7-7700HQ laptop with 8 GB RAM and client and server on the same machine. exposed wins 70 of 75 echo configurations with a median of \~1.4x op/s: \~1.15-1.45x at concurrency 1, up to \~3x at 8 B/5 clients/concurrency 5000 (1,003,452 vs 329,040 op/s). Six of those wins are 32/64 KiB rows at concurrency 50,000 where gRPC failed or collapsed (0-413 op/s). The gRPC harness was never published (issue #6 is open), and the in-repo echo benchmark uses a pass-through codec that skips serialization, so the comparison cannot be reproduced and may be codec-asymmetric.

## Use it when

- Go-to-Go internal calls where you own both ends and want fewer allocations and GCs than grpc-go for small (8 B-1 KiB) messages.
- Few clients with many calls in flight (concurrency 500-50,000 per the README): its largest margins (\~2-3x op/s, several-fold lower p99) come from 1-5 clients at those concurrency levels.
- Throughput-oriented traffic where batching writes is acceptable; MaxBatchDelay trades per-call latency for fewer packets.
- As a small (\~2.2k lines of non-test Go) readable reference implementation of fastrpc-style pipelined RPC to vendor or study.

## Skip it when

- You need gRPC interop, non-Go clients, HTTP/2 proxies or load balancers, metadata/headers, interceptors, service discovery or streaming (the bidirectional-stream PR #9 was never merged).
- Many client connections each running moderate concurrency: with 10 clients at concurrency 50 or 500, grpc-go won at 8 B and 128 B payloads (e.g. 508,941 vs 301,884 op/s at 8 B/500).
- Messages over 16 MiB (hard MaxBytesSize frame limit), or 32-64 KiB payloads at concurrency 50,000, where the table shows multi-second latencies and only \~170 to \~3,300 op/s.
- Anything that needs a maintained dependency: last commit 2018-08-02, no go.mod, 'publish benchmark code' and 'improve test coverage' issues still open, one HN post with 3 points and 0 comments, and the required `expose` codegen repo has no license file.
- Server-side deadlines or cancellation: handlers are called with a nil \*Context, and timeouts and cancellation exist only on the client side.

## How it is fast

It keeps the valyala/fastrpc transport design. Each Client multiplexes every call over a single TCP connection tagged with 4-byte request IDs, with separate reader and writer goroutines and 64 KiB bufio buffers. The writer flushes only when its queue is empty (or after an optional MaxBatchDelay timer), so concurrent requests are coalesced into few syscalls and packets (write batching / pipelining). Framing is bare TLV (8-byte xxhash64 of the operation name + 4-byte length + payload; the response is payload + error) with no HTTP/2 frames or HPACK headers, dispatch is a map lookup on that hash with closure factories instead of reflection, requests/responses/work items are recycled through sync.Pool, and a 1-second coarse clock avoids per-request time.Now/SetDeadline calls. That fits the table's lower allocation and GC counts in most rows (e.g. 472 MB and 111 GCs vs 1.4 GB and 538 GCs).

## Compared with alternatives

Rarely. rpcx (\~2.3-2.6x grpc-go), Kitex (1.5-1.7x) and cmd-stream (\~3-4.6x) are Go siblings with 2026 commits and similar or larger published margins, and DRPC describes itself as a drop-in gRPC replacement. Pick exposed only if you want to vendor a \~2.2k-line fastrpc-style transport and own its fixes.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/cespare/xxhash, github.com/gogo/protobuf, github.com/golang/snappy, github.com/rs/zerolog, golang.org/x/net/trace; optional codegen via github.com/thesyncim/expose (unlicensed) plus gogoproto generation |
| **Minimum toolchain** | Go 1.10+ per README (CI: Go 1.10.x and tip, 2018); no go.mod, so it resolves as pseudo-version v0.0.0-20180802170311-61b3f891f668; builds on current Go not verified |
| **Platforms** | any Go target with net.Conn (TCP by default, custom dialer allowed); CI ran linux and osx |
| **Thread safety** | Client and Server handle concurrent calls (per-connection reader/writer goroutines, mutex-guarded pending map, atomic counters). Handler, type and codec registries are unsynchronized package-level maps: register before Serve / in init(). encoding.Codec implementations must be thread-safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Handlers and their argument/reply factories are stored in process-global maps keyed by xxhash64 of the operation name and shared by every Server in the process; a duplicate name (or hash collision) panics at registration.
- The default protobuf codec panics ('compile with gogoproto') on messages without a generated Unmarshal method, and the JSON codec uses reflection-based encoding/json, so 'reflectionless' describes dispatch, not encoding.
- From reading common.go: for an unknown operation the 'handler not found' error goes to a shared context (h.Response) instead of the request's (eh.Response), so the caller gets an empty reply with no error; with protobuf that decodes as a zero-value success.
- Client has no Close(): each Client starts a connection worker and a stale-request sweeper goroutine that never exit. Call() hard-codes a 120 s deadline. DoContext returns its pooled work item on cancel while connection goroutines may still hold it, and the pooled item's context field is never cleared, which can reach 'BUG:' panics or disable deadline sweeping on reuse. The README server example (`resp.(*string) = req.(*string)`) does not compile.

## Known shortcomings

- The gRPC harness was never published (#6 open); the repo's own echo benchmark uses a pass-through codec that skips serialization, so if the README table used it, exposed skipped encoding while gRPC paid for protobuf; gRPC and Go versions unstated. Wins are uneven: 70 of 75 rows (median \~1.4x), six of them where gRPC collapsed at 32/64 KiB and 50,000 concurrency; gRPC wins with 10 clients at concurrency 50/500 for small messages (e.g. 508,941 vs 301,884 op/s). Code-reading bugs: 'handler not found' is written to a shared context, so callers get an empty success; DoContext returns work items to the pool on cancel while still in use (can hit 'BUG:' panics); Client has no Close and leaks two goroutines; Call hard-codes 120 s; handlers get a nil Context; the README server example doesn't compile. 'Reflectionless' covers dispatch only (gogo codec panics without generated Unmarshal; JSON codec uses reflection). Global unsynchronized handler registry keyed by xxhash64 of names. No streaming (#9), gRPC interop, metadata or interceptors; 16 MiB frame cap. Last commit 2018-08, no go.mod, codegen tool unlicensed; derived from valyala/fastrpc.

## Caveats and trade-offs

Abandoned: last commit 2018-08-02. The gRPC comparison harness is not published; the repo's server_timing_test.go only benchmarks exposed end-to-end. Go version and flags for the table are unstated (Travis CI targets Go 1.10.x). Gains are modest (\~1.1-3x) and not uniform: gRPC wins 5 of the 75 paired configurations. Some high-concurrency, large-payload rows show gRPC at \~0 op/s, i.e. failed runs. LICENSE text is MIT (GitHub reports NOASSERTION because of the dual copyright header). The code derives from valyala/fastrpc.

Go only; reflectionless codec requires code generation via the 'expose' tool; niche adoption, very small community (3 forks, 27 stars)

## Maintenance

Abandoned since 2018-08-02 (27 stars, no tagged releases, no go.mod) but MIT-licensed (dual copyright with fastrpc's author) and small enough to vendor; use it as a starting point, not a dependency, and note that the `expose` codegen tool carries no license.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmark table compares exposed and grpc head-to-head across 75 paired configurations and states the CPU (i7-7700HQ). The gRPC comparison harness is not in the repo; server_timing_test.go benchmarks only exposed itself. The Go version and flags are not stated. That makes this first-party with partial methodology: tier C.
- **Verifier notes:** Numbers verified in the Readme table (the correct row is 1 client, concurrency 50). The record's 'README states outperforms across nearly all scenarios' is a paraphrase and has been corrected. Metadata checked via gh GraphQL: 27 stars, not a fork or archived, last commit 2018-08-02; LICENSE file is MIT.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/thesyncim/exposed>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/Readme.md>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/LICENSE>
  - <https://github.com/thesyncim/exposed/blob/master/server_timing_test.go>
  - <https://github.com/thesyncim/exposed/blob/master/.travis.yml>
  - <https://github.com/valyala/fastrpc>
- **Sources the enricher read:**
  - <https://github.com/thesyncim/exposed>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/Readme.md>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/LICENSE>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/.travis.yml>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/client.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/server.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/common.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/exposed.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/handler.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/register.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/request.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/response.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/context.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/coarseTime.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/server_timing_test.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/go.mod>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/encoding/encoding.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/encoding/codec/json/json.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/encoding/codec/proto/protobuf.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/examples/echo/echo.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/examples/echo/ecodec/codec.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/examples/echo/echoservice/server.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/examples/echo/echoservice/client.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/examples/echo/echoservice/protobuf_types.go>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/examples/echo/echoservice/generated.proto>
  - <https://raw.githubusercontent.com/thesyncim/exposed/master/examples/echo/usage/echo_test.go>
  - <https://github.com/thesyncim/exposed/issues/6>
  - <https://github.com/thesyncim/exposed/issues/7>
  - <https://github.com/thesyncim/exposed/issues/8>
  - <https://github.com/thesyncim/exposed/pull/9>
  - <https://github.com/thesyncim/exposed/pull/2>
  - <https://github.com/thesyncim/expose>
  - <https://raw.githubusercontent.com/thesyncim/expose/master/Readme.md>
  - <https://raw.githubusercontent.com/valyala/fastrpc/master/README.md>
  - <https://proxy.golang.org/github.com/thesyncim/exposed/@v/list>
  - <https://proxy.golang.org/github.com/thesyncim/exposed/@latest>
  - <https://hn.algolia.com/api/v1/search?query=thesyncim%20exposed&restrictSearchableAttributes=url>
  - <https://github.com/smallnest/rpcx>
  - <https://github.com/cloudwego/kitex>
  - <https://github.com/storj/drpc>
  - <https://github.com/cmd-stream/cmd-stream-go>
  - <https://github.com/valyala/fastrpc>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/thesyncim/exposed`) · [data/wave5/enrich/raw/github_com_thesyncim_exposed.json](../../../data/wave5/enrich/raw/github_com_thesyncim_exposed.json) (enrichment confidence 0.4)

</details>
