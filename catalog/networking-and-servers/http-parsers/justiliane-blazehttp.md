# blazehttp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Go HTTP/1.1+HTTP/2 server/client with zero-copy header parser; \~11-14% more HTTP/1.1 req/s than fasthttp (author's wrk runs).

| | |
|---|---|
| **Beats** | valyala/fasthttp |
| **Claimed result** | HTTP/1.1 server vs fasthttp (wrk -t4 -c128 -d10s, doc/BENCHMARKS.md): Plaintext 329,836 vs 298,122 req/s (+10.6%); JSON 328,986 vs 293,992 (+11.9%); POST 1KB echo 313,474 vs 275,830 (+13.6%); p50 latency 179 vs 216 us, but p90/p99 slightly worse (2.99 vs 2.73 ms, 6.41 vs 6.26 ms). Header parsing (README table, pkg/header/parser_bench_test.go): Simple GET (1 header) 252 ns/0 allocs vs fasthttp 1,336 ns/1 alloc = 5.3x; Typical (8 headers) 2,377 vs 6,198 ns = 2.6x; Many headers (20) 4,776 vs 10,077 ns = 2.1x. HTTP/2 vs net/http (h2load): +56.9% to +133.9% req/s. |
| **Workload** | Go micro-benchmark of HTTP/1.1 request header parsing at three sizes (1 header, 8 headers, 20 headers), ns/op and allocs/op, BlazeHTTP's zero-alloc parser vs fasthttp's request parser |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2698 v4 @ 2.20GHz, 80 cores, 125 GiB RAM, Linux 5.15.0 (doc/BENCHMARKS.md environment; the README header-parse table is not explicitly tied to it) |
| **Compiler and flags** | Go 1.24.0 (go.mod and doc/BENCHMARKS.md); go build/test flags not stated; GOGC=100; wrk -t4 -c128 -d10s --latency; h2load -n1000000 -c{N} -m{M} |
| **Adoption** | 2 stars |
| **Last commit** | 2026-02-24 |
| **Links** | [repository](https://github.com/justIliane/blazehttp) · [benchmark](https://github.com/justIliane/blazehttp#-performance) |

## Verdict

The author ran wrk -t4 -c128 -d10s once per case on a non-isolated 80-core Xeon E5-2698 v4 (Linux 5.15, Go 1.24.0, GOGC=100, build flags not stated). BlazeHTTP served 329.8k plaintext req/s vs 298.1k for fasthttp v1.69.0 (+10.6%), +11.9% on JSON and +13.6% on 1 KB POST echo. p50 latency was lower (179 vs 216 us), but p90/p99 were slightly higher. fasthttp ran with default settings and also wrote Server and Date headers that BlazeHTTP omits. The 2.1-5.3x header-parse speedups come from go test benchmarks in which fasthttp reads through a bufio.Reader over a fresh bytes.Reader (1 alloc/op) into its own header struct, while BlazeHTTP slices the input buffer. Treat them as upper bounds, not a like-for-like parser comparison.

## Use it when

- You want an HTTP/2 or h2c server in Go with a fasthttp-style zero-allocation handler API. fasthttp has no HTTP/2. In the author's h2load runs, it served 1.6-2.3x the req/s of net/http.
- You are prototyping or benchmarking small, keep-alive HTTP/1.1 request/response traffic (headers and bodies well under 4 KB, no pipelining), and a \~10% req/s gain over fasthttp matters.
- You need a Go HTTP/2 client that presents browser-like JA3/JA4 and Akamai HTTP/2 fingerprints, with connection pooling, proxies (CONNECT, SOCKS5) and multiplexed DoBatch.
- You want a small, readable reference for a zero-copy HTTP/1.1 head parser or a zero-allocation HPACK codec in Go to study or vendor.

## Skip it when

- Internet-facing HTTP/1.1 serving. In server/http1/handler.go at HEAD, readUntilComplete grows only a local copy of the 4 KB read buffer, so a header section over 4 KB makes the caller slice past its capacity. That is a panic, and no recover exists in the server or worker code. The function also returns as soon as CRLFCRLF arrives, so a body not already in that read gives ErrNeedMore, which ServeConn answers with 400 and a closed connection.
- Clients that pipeline HTTP/1.1 requests. ServeConn copies the leftover bytes to the front of the buffer, but the next read writes over them from offset 0. The CHANGELOG still claims pipelining support.
- Deployments behind a proxy, or anywhere request smuggling matters. The parser is lenient, with no strict mode (see gotchas).
- HTTP/2 handlers that block (database or RPC calls). Requests go to a fixed worker pool with a queue of n\*4. When the queue is full, new streams get REFUSED_STREAM instead of waiting.
- Anything that needs a mature, supported library, or fasthttp middleware and routers. It has 2 stars, 1 fork and no issues. Development ran only 2026-02-22 to 2026-02-24. The API is not fasthttp-compatible.

## How it is fast

The HTTP/1.1 parser is a plain scalar byte loop with zero copies. It scans for CRLFCRLF, then fills a fixed 128-entry array of key/value slices that point into the read buffer. While parsing, it records Content-Length, chunked and keep-alive using a switch on the first byte of the header name. It uses no SIMD and no bytes.IndexByte. Requests, responses and contexts are recycled with sync.Pool, and buffers come from a size-class pool (64 B to 64 KB). Responses are appended into one pooled buffer, and accepted sockets get TCP_NODELAY, plus TCP_QUICKACK on Linux. HTTP/2 uses a read loop, a fixed worker-goroutine pool (default NumCPU\*256) and a write loop, with its own zero-allocation HPACK (hashed static-table lookup, ring-buffer dynamic table).

## Compared with alternatives

fasthttp is the only Go sibling. Pick blazehttp over it only if you need HTTP/2/h2c or a browser-fingerprinted client in a fasthttp-style API and can live with an unproven codebase. For plain HTTP/1.1, fasthttp's pipelining, large-request handling and long production record outweigh a \~10% req/s gain. For a standalone request-head parser, the long-established C and Rust siblings (picohttpparser, httparse) or iohttpparser's strict profile are the better-tested choices.

## Integration

| | |
|---|---|
| **Form** | module (go get github.com/justIliane/blazehttp; packages server, server/http1, server/http2, client, pkg/header, pkg/hpack, ...) |
| **Dependencies** | refraction-networking/utls v1.8.2 (client fingerprinting); go.mod also requires valyala/fasthttp v1.69.0 (benchmarks/tests), with golang.org/x/{crypto,net,sys,text}, klauspost/compress and andybalholm/brotli as indirect dependencies |
| **Minimum toolchain** | Go 1.24.0 (go.mod) |
| **Platforms** | Pure Go with unsafe zero-copy string/[]byte conversions, so any Go target in principle. TCP_QUICKACK is set only on Linux (sockopt_linux.go). The benchmarks cover only Linux x86-64. |
| **Thread safety** | Each connection runs in its own goroutine; HTTP/2 handlers run on a shared worker pool. RequestCtx is pooled and must not be kept after the handler returns (documented). ParsedRequest and Request slices point into the network buffer and are valid only until release. Handler panics are not recovered. |
| **Drop-in for the baseline** | false — own RequestCtx types (similar in shape to fasthttp's, but different packages and methods); adapters exist only for net/http, not for fasthttp |

## Gotchas

- The README quick start calls server.New(), s.HandleHTTP2(...) and ListenAndServeTLS(":8443"), and none of these exist in the code. The real API is &server.Server{Addr, Handler, TLSConfig} with ListenAndServe(), ListenAndServeTLS() or ListenAndServeTLSCert(cert) (see examples/hello).
- ReadTimeout, WriteTimeout and IdleTimeout default to zero, which means no deadlines. The README's slowloris 'Read timeouts' mitigation applies only if you set them. Responses carry no Date or Server header.
- The parser is lenient. It trims spaces before the colon, so 'Transfer-Encoding : chunked' counts as TE. It does not validate header names as tokens or reject control characters, and it keeps a bare LF inside a value. It ignores an unparseable Content-Length instead of rejecting it, and the last duplicate Content-Length wins. It treats only an exact 'chunked' as chunked, so 'gzip, chunked' is not. It accepts only CRLF line endings and methods of A-Z only.
- With HTTP1Handler left nil, every HTTP/1.1 request is copied into an http2.RequestCtx and back through a bridge. The HTTP/1.1 benchmark server set a native HTTP1Handler, so the published numbers do not include that copy.

## Known shortcomings

- Code-reading findings (not run): header sections over 4 KB slice past the read buffer and panic with no recover, crashing the process; bodies beyond the first read get 400; leftover pipelined bytes are overwritten, so pipelining is broken despite the CHANGELOG. Lenient parser (smuggling risk): space before the colon trimmed ('Transfer-Encoding : chunked' counts), no token check on header names, control characters and bare LF in values kept, unparseable Content-Length ignored, last duplicate wins, only exact 'chunked', CRLF only. Benchmark asymmetry: fasthttp's default server emits Server and Date headers BlazeHTTP doesn't, and the header-parse micro-benchmark compares a copying bufio read against slicing, so 2.1-5.3x is an upper bound. README quick start calls functions that don't exist; timeouts default to zero despite slowloris claims; the fixed HTTP/2 worker pool refuses streams when its queue fills. Idle since 2026-02, 2 stars.

## Caveats and trade-offs

Each wrk/h2load run was done once on a non-isolated system (doc/BENCHMARKS.md), and p90/p99 latency is slightly worse than fasthttp. In the header-parse harness, fasthttp reads through bufio.Reader wrapping a fresh bytes.NewReader on every iteration (the 1 alloc), while BlazeHTTP parses the byte slice directly, so part of the 2-5x micro gap is harness asymmetry. The README does not say which fasthttp variant (reuse or non-reuse) produced the Typical row. The header-parse numbers are not in doc/BENCHMARKS.md, so they are not explicitly tied to the stated CPU. Very low adoption: 2 stars and 18 commits, all 2026-02-21 to 2026-02-24.

From-scratch Go HTTP/1.1 + HTTP/2 implementation adding TLS/HTTP2 fingerprint evasion (JA3/JA4, browser emulation) that fasthttp does not attempt; fasthttp still lacks HTTP/2 entirely so the HTTP/2 numbers compare against net/http instead; only one external dependency (uTLS)

## Maintenance

MIT-licensed single-author project: created 2026-02-22, last push 2026-02-24, so seven months idle as of 2026-09-26 despite the 'active' label. Its one fork has the same HTTP/1.1 handler. pkg/header and pkg/hpack are small enough to vendor or study, but the HTTP/1.1 server needs its buffer-growth and pipelining bugs fixed before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. doc/BENCHMARKS.md gives the environment (Intel Xeon E5-2698 v4 @ 2.20GHz, 80 cores, Linux 5.15, Go 1.24.0), the exact wrk command and the RPS tables against fasthttp. The server code for both sides is public (bench/blazehttp/main.go, bench/fasthttp/main.go; go.mod pins fasthttp v1.69.0), and the header-parse table maps to pkg/header/parser_bench_test.go. Go build flags are not stated, which matches the Go A-tier precedent (rpcx, cmd-stream-go).
- **Verifier notes:** All README numbers match. The record's caveat said no benchmark source was public; that is wrong, because pkg/header/parser_bench_test.go, bench/ and doc/BENCHMARKS.md exist. fasthttp is a confirmed catalog entry (wave5 batch-26), so baseline_in_list is now true.
- **Fields the verifier corrected:** `baseline_in_list`, `hardware`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/justIliane/blazehttp>
  - <https://github.com/justIliane/blazehttp#-performance>
  - <https://github.com/justIliane/blazehttp/blob/main/doc/BENCHMARKS.md>
  - <https://github.com/justIliane/blazehttp/blob/main/pkg/header/parser_bench_test.go>
  - <https://github.com/justIliane/blazehttp/blob/main/bench/bench_test.go>
  - <https://github.com/justIliane/blazehttp/blob/main/bench/fasthttp/main.go>
  - <https://github.com/justIliane/blazehttp/blob/main/bench/blazehttp/main.go>
  - <https://github.com/justIliane/blazehttp/blob/main/go.mod>
- **Sources the enricher read:**
  - <https://github.com/justIliane/blazehttp>
  - <https://github.com/justIliane/blazehttp#-performance>
  - <https://github.com/justIliane/blazehttp/blob/main/doc/BENCHMARKS.md>
  - <https://github.com/justIliane/blazehttp/blob/main/doc/ARCHITECTURE.md>
  - <https://github.com/justIliane/blazehttp/blob/main/doc/CONFORMANCE.md>
  - <https://github.com/justIliane/blazehttp/blob/main/doc/CHANGELOG.md>
  - <https://github.com/justIliane/blazehttp/blob/main/go.mod>
  - <https://github.com/justIliane/blazehttp/blob/main/Makefile>
  - <https://github.com/justIliane/blazehttp/blob/main/pkg/header/parser.go>
  - <https://github.com/justIliane/blazehttp/blob/main/pkg/header/parser_bench_test.go>
  - <https://github.com/justIliane/blazehttp/blob/main/pkg/header/parser_test.go>
  - <https://github.com/justIliane/blazehttp/blob/main/pkg/header/fuzz_test.go>
  - <https://github.com/justIliane/blazehttp/blob/main/pkg/bytespool/pool.go>
  - <https://github.com/justIliane/blazehttp/blob/main/internal/util/unsafe.go>
  - <https://github.com/justIliane/blazehttp/blob/main/bench/bench_test.go>
  - <https://github.com/justIliane/blazehttp/blob/main/bench/blazehttp/main.go>
  - <https://github.com/justIliane/blazehttp/blob/main/bench/fasthttp/main.go>
  - <https://github.com/justIliane/blazehttp/blob/main/server/server.go>
  - <https://github.com/justIliane/blazehttp/blob/main/server/sockopt_linux.go>
  - <https://github.com/justIliane/blazehttp/blob/main/server/tls.go>
  - <https://github.com/justIliane/blazehttp/blob/main/server/http1/handler.go>
  - <https://github.com/justIliane/blazehttp/blob/main/server/http1/request.go>
  - <https://github.com/justIliane/blazehttp/blob/main/server/http1/response.go>
  - <https://github.com/justIliane/blazehttp/blob/main/server/http1/handler_test.go>
  - <https://github.com/justIliane/blazehttp/blob/main/server/server_test.go>
  - <https://github.com/justIliane/blazehttp/blob/main/server/http2/conn.go>
  - <https://github.com/justIliane/blazehttp/blob/main/server/http2/handler.go>
  - <https://github.com/justIliane/blazehttp/blob/main/blazehttp.go>
  - <https://github.com/justIliane/blazehttp/blob/main/examples/hello/main.go>
  - <https://api.github.com/repos/justIliane/blazehttp/forks>
  - <https://raw.githubusercontent.com/brandonseydel/blazehttp/main/server/http1/handler.go>
  - <https://raw.githubusercontent.com/valyala/fasthttp/v1.69.0/server.go>
  - <https://raw.githubusercontent.com/valyala/fasthttp/v1.69.0/header.go>
  - <https://hn.algolia.com/api/v1/search?query=blazehttp&tags=story>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/justiliane/blazehttp`) · [data/wave5/enrich/raw/github_com_justiliane_blazehttp.json](../../../data/wave5/enrich/raw/github_com_justiliane_blazehttp.json) (enrichment confidence 0.65)

</details>
