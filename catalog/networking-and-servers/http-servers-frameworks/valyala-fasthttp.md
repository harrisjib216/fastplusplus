# fasthttp (Go HTTP server/client package)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟢 active

> Zero-allocation HTTP/1.1 server and client for Go; about 5x faster per request than net/http in its own benchmarks.

| | |
|---|---|
| **Beats** | Go net/http |
| **Claimed result** | README: 'fasthttp server is up to 6 times faster than net/http' and 'fasthttp client is up to 4 times faster'. The 'up to 10x' is the GitHub repo description, not the README. Server, GOMAXPROCS=4, 10K reqs/conn: net/http 2179 ns/op (2386 B/op, 21 allocs/op) vs fasthttp 451.4 ns/op (0 B/op, 0 allocs/op), about 4.8x. The same case at GOMAXPROCS=1 is 7151 vs 1422 ns/op, about 5.0x. The best server row is 14010 vs 2208 ns/op, about 6.3x (GOMAXPROCS=1, 2 reqs/conn, 10K clients). Client end-to-end is about 2.0-2.3x over TCP and 4.9-11.7x in-memory, peaking at 31010 vs 2645 ns/op with 1000 in-memory conns at GOMAXPROCS=4. All ratios are derived from page data. |
| **Workload** | Go testing benchmarks (server_timing_test.go, client_timing_test.go; go test -bench -benchmem -benchtime=10s) at GOMAXPROCS=1 and 4. Server tests send a GET that gets a small fake response over an in-memory fake listener and connections, with no real network. They cover 1/2/10/10K requests per connection, and 1/2/10/100 requests per connection with 10K clients, comparing fasthttp.Server with net/http's http.Server. Client tests run an end-to-end GET over TCP (1/10/100 conns) and in-memory (1-1000 conns; fasthttp also 10K). |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) CPU @ 2.20GHz (exact model number not given; from `go test` output header) |
| **Adoption** | 23.5k stars; also referenced in TechEmpower Benchmark round 23 plaintext results |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/valyala/fasthttp) · [benchmark](https://github.com/valyala/fasthttp#http-server-performance-comparison-with-nethttp) |

## Verdict

The project's own go test benchmarks run on an unnamed 'Intel Xeon CPU @ 2.20GHz' with no Go version stated. They push a small GET through in-memory fake connections with no real network. fasthttp takes 1418-3009 ns/op at 0 allocs vs net/http's 7151-17152 ns/op at 21-36 allocs (about 5.0-6.3x at GOMAXPROCS=1, 3.0-5.5x at GOMAXPROCS=4; derived). The client is 2.0-2.3x faster over loopback TCP and up to about 11.7x in memory. This measures the whole server path, not the parser alone, and one independent real-network test saw only 30-70% gains.

## Use it when

- Go services that handle thousands of small-to-medium HTTP/1.1 requests per second, where pprof shows net/http allocations and GC as a top cost (the README's own condition for using it)
- Proxies, gateways, ad or edge servers with very many keep-alive connections; the README cites VertaMedia production at up to 200K rps from more than 1.5M concurrent keep-alive connections per server
- High-rate outbound calls to a few hosts: HostClient/PipelineClient run at 0 allocs/op and about 2.0-2.3x the net/http client over loopback TCP in the README benchmarks
- Multi-core hosts where you can run one prefork/reuseport process per core with GOMAXPROCS=1. In TechEmpower R23 plaintext (verifier-derived), fasthttp-prefork reaches about 14.6M rps vs about 1.6M for Go net/http, but single-process fasthttp reaches only about 0.57M
- You already use a framework built on it (Fiber, atreugo, Gearbox) and accept that it is a separate ecosystem from net/http

## Skip it when

- You need HTTP/2 or HTTP/3 served directly: fasthttp is HTTP/1.x only. The fasthttp/http2 add-on describes itself as 'Under construction' and has had no push since January 2022. Terminate h2 at a proxy instead
- You depend on net/http middleware and libraries (http.Handler chains, httptest, oauth2 and similar). fasthttpadaptor converts handlers, but the README says to rewrite handlers natively to get the speed
- Large or streaming bodies: bodies are buffered in memory by default (server MaxRequestBodySize default is 4 MiB; StreamRequestBody is opt-in). The README lists request and response streaming, and more HTTP corner cases, as net/http advantages
- The handler, DB or serialization dominates: the README warns that a blind switch gives no boost. An independent 2022 real-network test (40-core Xeon Silver 4114, hey, 200-16000 keep-alive connections) measured only 30-70% more throughput than net/http
- Internet-facing servers or clients on default settings: a maintainer says the defaults 'are about being fast', not safe. Read and write timeouts are unlimited by default, and Slowloris memory growth is still open (#2037). The client default has no response-body limit, so one huge Content-Length header can kill the process with an uncatchable OOM (#2344, closed with documentation only)

## How it is fast

The main technique is object reuse. RequestCtx, Request/Response and the bufio readers and writers are recycled through sync.Pool and reset instead of reallocated. This is possible only because the API forbids keeping ctx after the handler returns, which net/http's Request lifetime does not allow. Headers are stored as a slice of key/value byte-slice pairs (argsKV), not net/http's map[string][]string of strings, so there is no per-header string conversion. Name case is normalized with 256-entry lookup tables, and unsafe b2s/s2b conversions avoid copies. Connections go to a FILO goroutine worker pool, where the most recently idle worker takes the next connection to keep caches warm. The whole response is buffered until the handler returns, and the flush is skipped while more pipelined requests are already in the read buffer.

## Compared with alternatives

Every catalogued sibling is a standalone parser component: picohttpparser and its forks or rewrites, httparse, iohttpparser, zttp/llhttp, Puma's http11_parser, plus URL and HPACK parsers in C, Rust, Zig, Python or Ruby. fasthttp is the only complete Go server and client, so pick it when you are in Go and want the whole request path to be faster. Pick httparse or a picohttpparser variant when you are writing your own server loop in Rust or C and need only a parser.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/klauspost/compress, github.com/molecule-man/go-brrr (brotli), github.com/valyala/bytebufferpool, golang.org/x/crypto, golang.org/x/net, golang.org/x/sys (golang.org/x/text indirect) |
| **Minimum toolchain** | Go 1.26.0 (go.mod); README says the project supports the same Go versions as the Go team, and CI tests Go 1.26.x and 1.27.x |
| **Platforms** | Any Go target, pure Go. It has OS-specific listener and socket code for Linux, Darwin, Windows, AIX, Solaris, z/OS s390x and js/wasm. On Windows the FS handler has a path-traversal history (CVE-2022-21221; issue #1691, now blocked by rejecting '..' segments on Windows) and a maintainer has called Windows FS not production-safe |
| **Thread safety** | Methods on Server, Client, HostClient and PipelineClient are safe to call from concurrent goroutines. Request, Response, RequestHeader, ResponseHeader and RequestCtx must not be used concurrently or copied. RequestCtx and its members must not be kept after the handler returns; only TimeoutError\* may be called concurrently |
| **Drop-in for the baseline** | partial — different handler signature (func(\*RequestCtx)), []byte accessors, no ServeMux, and a different client API. fasthttpadaptor wraps net/http handlers, but that gives up much of the gain |

## Gotchas

- Pooled objects: any []byte from ctx (Path(), Peek(), PostBody()) or a pointer to ctx kept after the handler returns is later overwritten, which causes data races or corrupt data. Copy the data out, or use TimeoutHandler/TimeoutError, and run the race detector
- ctx.Done() closes only at server shutdown, not per request or on client disconnect, so it cannot be used to cancel a request
- ReadBufferSize (default 4096) also caps total request-header size, so big cookies or long URIs fail with ErrSmallBuffer until you raise it. Pooled buffers stay allocated after load spikes, so RSS drops slowly (maintainer on #2037)
- The response goes on the wire only after the handler returns. The flush is also skipped while pipelined requests are buffered; the code comment says this is an optimization for TechEmpower that 'could be argued as being wrong'. Exported UnsafeString/UnsafeBytes share memory, and mutating the bytes is undefined behavior

## Known shortcomings

- Go, not C++. The server benchmark uses in-memory fake connections; 'up to 10x' is the repo description (README says up to 6x server, 4x client). TechEmpower R23 is mixed: non-prefork fasthttp is below Go net/http on plaintext. Not a drop-in for net/http (different API, no HTTP/2).
- The server benchmark times the whole server path over in-memory fake connections, not HTTP parsing, so it is filed with the servers. An independent real-network test (2022, 40-core Xeon Silver 4114, hey) measured 30-70% over net/http, far below the README's 6x and the description's 10x. TechEmpower gains depend on prefork; single-process plaintext fell from 6.67M rps (2021) to 0.37M (2023), partly a per-request mutex fixed in PR #1986 (2025-04); the server skips flushing while pipelined requests are buffered, which its own comment calls arguably wrong. Defaults favour speed over safety: unlimited read/write timeouts, Slowloris memory growth open (#2037), client's unlimited response body allows an uncatchable OOM (#2344, docs-only fix); the project skips CVE assignment. HTTP/1.x only (http2 add-on abandoned 2022), bodies buffered in memory, not a drop-in for net/http. Keeping ctx or its []byte after the handler returns races. Windows FS handler path-traversal history (CVE-2022-21221, #1691 open). Needs Go 1.26+.

## Caveats and trade-offs

The benchmark is first-party (the project's own go test code) with partial methodology. The CPU is only the generic 'Intel(R) Xeon(R) CPU @ 2.20GHz' string, and no Go version is given. The server benchmarks use in-memory fake connections, so they measure the whole server path (parsing, allocation, handler dispatch) without real network I/O. They do not isolate HTTP parsing. The 'up to 10x' headline is the repo description; the README text says up to 6x (server) and 4x (client), although its in-memory client rows reach about 11.7x. The README itself warns that for most cases net/http is the better choice.

Deliberately breaks net/http API compatibility (custom RequestCtx-based API, no `net/http` Handler interface) to avoid allocations; reused/pooled request and response objects require careful lifetime handling (documented 'gotchas' around retaining pointers past handler return); benchmarks measure full request/response handling, not an isolated parser microbenchmark.

## Maintenance

Actively maintained: roughly monthly releases (v1.74.0 on 2026-09-07), last commit 2026-09-26, MIT, 23.5k stars. The API still changes between minor versions, and the security policy says the project currently skips CVE assignment.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README section compares fasthttp against net/http with first-party go test output. The benchmark code is public (server_timing_test.go, client_timing_test.go). The CPU is only the generic 'Intel(R) Xeon(R) CPU @ 2.20GHz' string and no Go version is stated, so this is first-party evidence with partial methodology: C.
- **Verifier notes:** All quoted server numbers match the README. The only misstatement was attributing 'up to 10x' to the README; it comes from the repo description, and the README client in-memory rows support up to about 11.7x (derived). TechEmpower R23 raw data (results/round23/ph.json, totalRequests/15 s, derived) is mixed. fasthttp-prefork reaches about 14.6M plaintext rps vs 2.0M for go-pgx-prefork and 1.6M for go (net/http). Non-prefork fasthttp manages only about 0.57M plaintext rps, but beats go in JSON (0.58M vs 0.39M). So no tier upgrade from TechEmpower. Metadata is correct: MIT, 23,476 stars, last commit 2026-09-26, not fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/valyala/fasthttp#http-server-performance-comparison-with-nethttp>
  - <https://github.com/valyala/fasthttp>
  - <https://github.com/valyala/fasthttp/blob/master/server_timing_test.go>
  - <https://www.techempower.com/benchmarks/results/round23/ph.json>
- **Sources the enricher read:**
  - <https://github.com/valyala/fasthttp>
  - <https://github.com/valyala/fasthttp#http-server-performance-comparison-with-nethttp>
  - <https://github.com/valyala/fasthttp/blob/master/go.mod>
  - <https://github.com/valyala/fasthttp/blob/master/server.go>
  - <https://github.com/valyala/fasthttp/blob/master/workerpool.go>
  - <https://github.com/valyala/fasthttp/blob/master/header.go>
  - <https://github.com/valyala/fasthttp/blob/master/headerscanner.go>
  - <https://github.com/valyala/fasthttp/blob/master/http.go>
  - <https://github.com/valyala/fasthttp/blob/master/client.go>
  - <https://github.com/valyala/fasthttp/blob/master/coarsetime.go>
  - <https://github.com/valyala/fasthttp/blob/master/bytesconv_table_gen.go>
  - <https://github.com/valyala/fasthttp/blob/master/server_timing_test.go>
  - <https://github.com/valyala/fasthttp/blob/master/uri.go>
  - <https://github.com/valyala/fasthttp/blob/master/uri_windows.go>
  - <https://github.com/valyala/fasthttp/blob/master/fs.go>
  - <https://github.com/valyala/fasthttp/blob/master/fs_windows.go>
  - <https://github.com/valyala/fasthttp/blob/master/stackless/doc.go>
  - <https://github.com/valyala/fasthttp/blob/master/prefork/README.md>
  - <https://github.com/valyala/fasthttp/blob/master/SECURITY.md>
  - <https://github.com/valyala/fasthttp/blob/master/TODO>
  - <https://github.com/valyala/fasthttp/releases>
  - <https://github.com/valyala/fasthttp/issues/2037>
  - <https://github.com/valyala/fasthttp/issues/1608>
  - <https://github.com/valyala/fasthttp/issues/1691>
  - <https://github.com/valyala/fasthttp/issues/2344>
  - <https://github.com/valyala/fasthttp/issues/1975>
  - <https://github.com/valyala/fasthttp/pull/1986>
  - <https://github.com/valyala/fasthttp/pull/1698>
  - <https://github.com/advisories/GHSA-fx95-883v-4q4h>
  - <https://github.com/fasthttp/http2>
  - <https://hn.algolia.com/api/v1/search?query=fasthttp&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=fasthttp%20net%2Fhttp&tags=comment>
  - <https://www.sobyte.net/post/2022-03/nethttp-vs-fasthttp/>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/valyala/fasthttp`) · [data/wave5/enrich/raw/github_com_valyala_fasthttp.json](../../../data/wave5/enrich/raw/github_com_valyala_fasthttp.json) (enrichment confidence 0.8)

</details>
