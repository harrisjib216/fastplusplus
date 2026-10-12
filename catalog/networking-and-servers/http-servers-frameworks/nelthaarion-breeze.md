# Breeze

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Go` · `MIT` · 🟢 active

> Go web framework on the gnet event loop; about 2.5x Go net/http on hello-world HTTP/1.1 throughput.

| | |
|---|---|
| **Beats** | Go net/http |
| **Claimed result** | the-benchmarker/web-frameworks data.json of 2026-09-24 (develop, commit f673364): breeze 186,467 / 173,403 / 168,851 req/s at concurrency 64 / 256 / 512 vs Go net/http ('nethttp', Go 1.22 ServeMux) 71,499 / 67,382 / 67,239 = 2.61x / 2.57x / 2.51x, and vs actix (actix-web 4.8) 179,203 / 168,270 / 163,415 = 1.04x / 1.03x / 1.03x (derived from page data). The older master snapshot (2026-09-20, different method) gives 124,892 / 108,998 / 107,346 vs nethttp 96,149 / 85,406 / 83,964 (1.30x / 1.28x / 1.28x) and vs actix 115,638 / 102,329 / 99,835 (1.08x / 1.07x / 1.08x) (derived from page data). |
| **Workload** | the-benchmarker/web-frameworks develop-branch run of 2026-09-24 (commit f673364): hello-world handlers (empty body or echoed id), load from zrk --closed (a closed loop over keep-alive connections) at concurrency 64/256/512, headline req/s averaged over the suite's routes; the server container gets about 4 cores. Breeze app at go/breeze/main.go, with a NumCPU worker pool on its gnet-based engine. |
| **Metric** | throughput |
| **Hardware** | Undisclosed x86_64 Linux host (Fedora 44 kernel 7.2.6-200.fc44), 16 logical CPUs, \~7.7 GB RAM reported. The cpu_name 'M1 Eight-Core Processor' in data.json is a hard-coded string, not a measured CPU model. data.json reports breeze using \~3.8 server cores (vs \~3.95 for actix and nethttp). |
| **Compiler and flags** | Go 1.27 (golang:1.27 build image per go/config.yaml), CGO_ENABLED=1, GOAMD64=v3, `go get` then `go build -trimpath` (go/Dockerfile at f673364) |
| **Adoption** | 215 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/nelthaarion/breeze) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

In the-benchmarker/web-frameworks develop run of 2026-09-24 (commit f673364; one run, Linux x86-64 host with 16 logical CPUs and an unmeasured CPU model, server limited to about 4 cores, Go 1.27 with GOAMD64=v3, closed-loop keep-alive load on hello-world routes), Breeze did 186,467 / 173,403 / 168,851 req/s at 64 / 256 / 512 connections vs 71,499 / 67,382 / 67,239 for the net/http entry (2.51-2.61x); it sent about 64-byte responses vs about 88 for net/http. The benchmark app uses the v1 import path and the v1 handler signature, so it almost certainly built v1.6.2 on upstream gnet, not the v2 that the label says.

## Use it when

- Go HTTP/1.1 API services whose handlers are CPU-only (in-memory lookups, small JSON) and where requests per core matter: in the 2026-09-24 the-benchmarker run it did 2.5-2.6x net/http and about 1.3x fasthttp on hello-world routes.
- Internal services behind a proxy or load balancer that terminates TLS and speaks keep-alive or pipelined HTTP/1.1 to the backend.
- Linux (or macOS/BSD) deployments, where gnet uses epoll/kqueue.
- Teams that want one Go module with the router, WebSocket server/client, validation, OpenAPI docs and a dev dashboard already wired to the event-loop engine.
- WebSocket hubs that live in the same process as the HTTP API; the README says upgraded connections skip HTTP parsing and messages arrive per-connection in FIFO order.

## Skip it when

- Handlers that mostly wait on databases or remote calls: these must be registered with `HandleBlocking` and go through the worker pool with `AsyncWrite`, which is the slower path that the benchmark did not measure.
- You need the net/http ecosystem: `http.Handler` middleware, in-process TLS, HTTP/2, or chunked request uploads (requests with Transfer-Encoding get a 400).
- Windows production: the author's changelog says gnet has no epoll/kqueue there and falls back to goroutine-per-connection.
- Tail latency matters more than peak throughput: in the same run, p99 at 512 connections was 5.79 ms vs 3.22 ms for actix-web (net/http: 15.5 ms).
- Risk-averse production: the repo was created in October 2025, one author wrote most commits, there were breaking API changes (v1 to v2 changed `HandlerFunc` to return `error`), graceful shutdown arrived only in September 2026, a dashboard security issue (#51, login fields leak into the URL) is open, and the engine is a 1-star personal fork of gnet.

## How it is fast

gnet runs one epoll/kqueue event loop per core and pins each connection to one loop (round-robin), so there is no goroutine per connection. Non-blocking routes run inline on that event-loop goroutine and answer with a synchronous `Conn.Write`, which skips the worker-pool channel, two goroutine handoffs and an `AsyncWrite` poller wakeup. A hand-written HTTP/1.1 parser loops over pipelined requests in one read event and copies only the header block (none with the opt-in `SetZeroCopyHeaders`). Context, request, response and wire buffers are pooled, status lines and common header blocks are precomputed, and static paths resolve through a per-method map; the author's microbenchmarks put parse+route+serialize at about 325 ns with zero allocations.

## Compared with alternatives

Choose it over fasthttp, the other catalogued Go option, if you want the higher measured throughput (168,851 vs 125,657 req/s at c=512 in the same run) plus built-in WebSocket/OpenAPI/dashboard, and can accept a young project with one main maintainer. If leaving Go is an option, hyper (166,617) and actix-web (163,415) matched it in that run with lower p99, so pick Breeze only to stay in Go.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/nelthaarion/gnet/v2 v2.2.0 (fork of panjf2000/gnet: 7 commits ahead, 0 behind), github.com/nelthaarion/ants/v2, goccy/go-json, andybalholm/brotli, golang-jwt/jwt/v5, gopkg.in/yaml.v3; v1.6.2 used upstream panjf2000/gnet v2.10.0 |
| **Minimum toolchain** | Go 1.26.7 per go.mod on main (the README still says Go 1.25.13+, which is what v1.6.2 requires) |
| **Platforms** | Linux, macOS and \*BSD through gnet epoll/kqueue; Windows builds but gnet falls back to goroutine-per-connection there. Benchmarked only on Linux x86-64. |
| **Thread safety** | Each connection is pinned to one event-loop goroutine. Inline handlers run on it and must not block, or every connection on that loop stalls. Routes registered with HandleBlocking run on the worker pool. Different connections are served concurrently. WebSocket messages reach the handler in per-connection FIFO order. |
| **Drop-in for the baseline** | no |

## Gotchas

- Routes registered with `Handle` run on the event loop by default, so one slow call (SQL, file read, outbound HTTP) stalls every connection on that reactor. Mark such routes with `HandleBlocking`, or turn inline execution off globally.
- With `SetZeroCopyHeaders(true)`, `Path` and header strings point into gnet's reused read buffer and are valid only until the handler returns. A retained string changes its contents without warning and can corrupt a map. Use `strings.Clone`, and check third-party middleware.
- `New` needs a pool whose overflow policy is Spawn or Reject. `NewWorkerPoolWithConfig` defaults to Block, which can stall an event loop; `NewEventLoopWorkerPool` uses Spawn, which can create unbounded goroutines under sustained overload.
- Protocol subset: HTTP/1.0 and 1.1 only, no server-side TLS (gnet has none), request Transfer-Encoding is rejected, responses carry no Date header, and dynamic `:param`/wildcard routes are matched by an ordered scan (the first-registered match wins).

## Known shortcomings

- The benchmark app imports the v1 path and v1 handler type (no error return), so the run built v1.6.2 on upstream gnet v2.10.0, not the labelled '2.0' or the current v2 on the nelthaarion/gnet fork (from source, not built). p99 is worse than actix (5.79 vs 3.22 ms at c=512; 0.88 vs 0.39 ms at c=64), though far better than net/http. Responses are smaller (64 vs \~88 bytes, no Date header). HTTP/1.x only, no TLS, chunked uploads get 400, no http.Handler adapter. Inline execution by default, so blocking handlers stall the event loop unless marked HandleBlocking; opt-in SetZeroCopyHeaders leaves strings pointing into reused buffers; NewEventLoopWorkerPool can spawn unbounded goroutines under overload. No speedup on Windows (gnet falls back to goroutine-per-connection). Created 2025-10, one main author, breaking API changes, graceful shutdown only since 2026-09 (#56), dashboard login fields in URL (#51 open); engine is a 1-star gnet fork; README Go version disagrees with go.mod.

## Caveats and trade-offs

The lead over actix-web is only 3-4%, within noise for a single-run shootout; the meaningful result is \~2.5x over Go's net/http, which is expected of an epoll event-loop engine over goroutine-per-connection. Breeze is built on a fork of gnet (github.com/nelthaarion/gnet/v2 v2.2.0, forked from panjf2000/gnet), which does the I/O. The suite's go/breeze/main.go imports the v1 module path github.com/nelthaarion/breeze while its go.mod requires breeze/v2 v2.0.8, so `go get` likely builds the latest v1 release (v1.6.x), not the '2.0' the label shows (inferred, not built). Breeze responses are smaller, about 64 bytes each vs about 88 for actix and nethttp (total_bytes_received / total_requests), so it likely sends fewer headers. Harness methods changed during 2026 and runs from different revisions do not compare. Low-star project (215 stars).

Small, young, apparently single-maintainer Go framework.

## Maintenance

Active (last push 2026-09-17, v2.1.0 tagged 2026-09-16), MIT, 215 stars, created October 2025, mostly one author. It installs as a normal Go module, but expect API churn between major versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** In the-benchmarker/web-frameworks data.json (develop, commit f673364, 2026-09-24), breeze (framework_id 577) scores 168,851 req/s at c=512 vs actix 163,415 and nethttp (Go net/http) 67,239. It leads both at every concurrency level. This is a well-known independent suite, but it is not tier A: the CPU model is not measured (the 'M1 Eight-Core Processor' string is hard-coded), and it is a single run.
- **Verifier notes:** The record's numbers match breeze's own row. I switched the baseline to Go net/http (also a listed baseline, so baseline_in_list stays true), since the \~3% margin over actix is noise and the same data.json shows a clear 2.5x win over the Go stdlib server; the actix figures are kept in claimed_speedup. Metadata checks out: MIT, 215 stars, last commit 2026-09-17, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/nelthaarion/breeze>
  - <https://raw.githubusercontent.com/nelthaarion/breeze/main/README.md>
  - <https://raw.githubusercontent.com/nelthaarion/breeze/main/go.mod>
  - <https://github.com/nelthaarion/breeze/blob/v1.6.2/go.mod>
  - <https://github.com/nelthaarion/breeze/blob/v2.0.8/go.mod>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/breeze/main.go>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/breeze/go.mod>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/breeze/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/nethttp/main.go>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/Dockerfile>
- **Sources the enricher read:**
  - <https://github.com/nelthaarion/breeze>
  - <https://github.com/nelthaarion/breeze/blob/main/README.md>
  - <https://github.com/nelthaarion/breeze/blob/main/go.mod>
  - <https://github.com/nelthaarion/breeze/blob/main/breeze.go>
  - <https://github.com/nelthaarion/breeze/blob/main/request.go>
  - <https://github.com/nelthaarion/breeze/blob/main/response.go>
  - <https://github.com/nelthaarion/breeze/blob/main/router.go>
  - <https://github.com/nelthaarion/breeze/blob/main/workerpool.go>
  - <https://github.com/nelthaarion/breeze/blob/main/types.go>
  - <https://github.com/nelthaarion/breeze/blob/main/context.go>
  - <https://github.com/nelthaarion/breeze/blob/main/CHANGELOG.md>
  - <https://github.com/nelthaarion/breeze/blob/main/docs/README.md>
  - <https://github.com/nelthaarion/breeze/blob/v1.6.2/go.mod>
  - <https://github.com/nelthaarion/breeze/blob/v1.6.2/breeze.go>
  - <https://github.com/nelthaarion/breeze/blob/v1.6.2/response.go>
  - <https://github.com/nelthaarion/breeze/blob/v1.6.2/router.go>
  - <https://github.com/nelthaarion/breeze/blob/v1.6.2/context.go>
  - <https://github.com/nelthaarion/breeze/tags>
  - <https://github.com/nelthaarion/breeze/releases>
  - <https://github.com/nelthaarion/breeze/issues?q=is%3Aissue>
  - <https://github.com/nelthaarion/breeze/issues/51>
  - <https://github.com/nelthaarion/breeze/graphs/contributors>
  - <https://github.com/nelthaarion/gnet>
  - <https://github.com/panjf2000/gnet/compare/dev...nelthaarion:gnet:dev>
  - <https://raw.githubusercontent.com/nelthaarion/gnet/dev/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/breeze/main.go>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/breeze/go.mod>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/breeze/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/go/Dockerfile>
  - <https://hn.algolia.com/api/v1/search?query=nelthaarion%20breeze&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=github.com%2Fnelthaarion%2Fbreeze>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/nelthaarion/breeze`) · [data/wave5/enrich/raw/github_com_nelthaarion_breeze.json](../../../data/wave5/enrich/raw/github_com_nelthaarion_breeze.json) (enrichment confidence 0.5)

</details>
