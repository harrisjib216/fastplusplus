# jianrong7/http-parser (Go zero-alloc parser)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP parsers](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Go` · `no license` · 🟢 active

> Tiny zero-allocation Go HTTP/1.x request parser that records byte offsets; \~5-10x faster than net/http.ReadRequest, with far less validation.

| | |
|---|---|
| **Beats** | net/http (Go standard library, http.ReadRequest) |
| **Claimed result** | \~10x faster on simple GET (133ns vs 1,377ns) and POST+body (161ns vs 1,602ns), \~5x faster on GET with 8 headers (374ns vs 2,021ns); 0 B/op vs 5,177-5,345 B/op allocations; 495-641 MB/s vs 48-98 MB/s throughput |
| **Workload** | Go benchmarks (testing.B, go test -bench) parsing a simple GET (2 headers), a POST with JSON body, and a GET with 8 headers, measuring ns/op, allocations, and MB/s |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro |
| **Adoption** | 0 stars |
| **Last commit** | 2026-02-08 |
| **Links** | [repository](https://github.com/jianrong7/http-parser) · [benchmark](https://github.com/jianrong7/http-parser/blob/main/README.md) |

## Verdict

The author's go test -bench on an Apple M1 Pro (Go version and flags not stated) compares Parser.Parse against http.ReadRequest over a fresh 4 KB bufio.Reader per iteration: 133 vs 1,377 ns (2-header GET), 161 vs 1,602 ns (POST) and 374 vs 2,021 ns (8-header GET), with 0 vs 5,177-5,345 B/op. The POST case declares Content-Length: 27 but carries a 24-byte body, so on that row Parse returns (0, nil) 'incomplete' on every iteration and times only header parsing; net/http's Body.Close error is not checked either.

## Use it when

- Studying or prototyping a zero-copy Go request parser. It is \~380 readable lines with a unit-test and benchmark file, and the README lists its gaps honestly.
- Trusted, well-formed HTTP/1.1 requests (internal tooling, load-generator harnesses, fixed clients) that arrive complete in one buffer, with at most 64 headers and bodies framed by Content-Length.
- Hot paths that only need the method, raw URI and a few header spans, where net/http's per-request \*http.Request, header map and URL parsing cost more than the work you actually do.
- Small requests, where the reported gap is largest: \~10x for the 2-header cases, narrowing to \~5x at 8 headers.

## Skip it when

- Any internet-facing server. The method (after its first byte), the URI, header values and the version are not validated, so CR, LF, NUL and other control bytes are accepted. CL/TE conflicts and duplicate Content-Length are not rejected (the last value wins), and an invalid Content-Length such as 'abc' or '+5' is silently treated as 'no body'.
- Requests with an empty header value such as 'X-Foo:' or 'X-Foo: '. Traced from parser.go, the value state consumes the CR unchecked, so the next header line is swallowed into that value. If the empty header is the last one, Parse returns (0, nil) forever.
- Chunked uploads, bare-LF clients or streaming bodies. A chunked request is 'complete' at the end of its headers with raw chunk framing left for you. Bare-LF lines are absorbed into the version or header value, or the request never completes; they are not rejected with an error, despite what the README says.
- Large header blocks or long URIs where scan speed matters. It scans one byte at a time at 495-641 MB/s, while SIMD parsers in this category report GB/s (for example thhp at 4.4 GB/s with SSE4.2, on other hardware).
- Anything that needs a dependency you can legally ship. There is no license, it is a single 'init' commit with 0 stars, and the module path is 'http-parser', not github.com/jianrong7/http-parser, so it cannot be fetched with go get.

## How it is fast

A hand-written, byte-at-a-time finite-state machine (one switch per byte, with no SIMD, SWAR or lookup tables) stores [start,end) offset spans in a fixed [64]Header array embedded in the Parser struct. Nothing reaches the heap, and Reset only zeroes counters. Content-Length and Transfer-Encoding are found by name length (14 or 17 bytes) followed by an ASCII case-insensitive compare; no other header is interpreted. Most of the gap versus net/http is work that this parser skips: http.ReadRequest reads the request line as a string through a textproto reader, checks validMethod, runs url.ParseRequestURI, builds the header map with readMIMEHeader, reconciles Host and sets up the body reader in readTransfer.

## Compared with alternatives

The only Go sibling is blazehttp, a tier-A, zero-alloc header parser inside a full HTTP/1.1 and HTTP/2 server benchmarked against fasthttp. Pick blazehttp for anything real, and pick this one only as a \~380-line teaching or prototyping parser to copy (license permitting) when you want offsets without a framework. The C and Rust siblings (picohttpparser forks, httparse, thhp) are far more mature choices outside Go.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (parser.go imports nothing, not even the standard library) |
| **Minimum toolchain** | go.mod declares 'go 1.24.1', which Go 1.21+ toolchains enforce as a minimum. The code itself uses only basic language features. The toolchain used for the benchmarks is not documented. |
| **Platforms** | any GOOS/GOARCH (pure Go, no unsafe, no assembly); benchmarked only on an Apple M1 Pro |
| **Thread safety** | Not goroutine-safe per Parser (the README calls it 'single-threaded' and the struct has no locking). The package has no mutable globals, so use one Parser per connection or goroutine. |
| **Drop-in for the baseline** | no |

## Gotchas

- Body() returns everything from the end of the headers to the end of the buffer, not ContentLength() bytes, so pipelined next requests or trailing garbage show up in the body. Slice with the returned n, or with bodyStart+ContentLength, yourself.
- All accessors alias your buffer and are valid only while it is unchanged. Copy them before recycling a pooled read buffer. HeaderAt(i) does not check i against HeaderCount(), so an out-of-range index returns stale spans from an earlier request or panics.
- Chunked detection is a case-insensitive substring match on the Transfer-Encoding value ('xchunkedx' counts). Header values keep trailing whitespace, and duplicate headers are stored separately.
- Parse returns (0, nil) for incomplete input but keeps its state. Re-calling it with the grown, contiguous buffer resumes, but the whole request must end up in one slice, and a Content-Length that overflows int can make it wait forever or swallow the rest of the buffer.

## Known shortcomings

- The POST benchmark row is invalid: its Content-Length (27) exceeds the 24-byte body, so Parse returns 'incomplete' every iteration and the 161 ns times header parsing only (net/http's failure is hidden by an ignored Body.Close error). The net/http side allocates a new 4 KB bufio.Reader per iteration; the gap shrinks from \~10x to \~5x as headers grow, and the speed is mostly skipped work (byte-at-a-time, no SIMD, 495-641 MB/s). Empty header values (legal) swallow the next line or never complete (traced, not run). Almost no validation: control bytes accepted, invalid Content-Length treated as no body, last duplicate CL wins, CL+TE accepted, 'chunked' matched by substring; the README's bare-LF claim is wrong. Body() returns the rest of the buffer (pipelined requests leak in); HeaderAt has no bounds check. Module path 'http-parser' breaks go get, no licence, one init commit (2026-02-08), 0 stars: reference only.

## Caveats and trade-offs

The benchmark code (parser/parser_test.go) is public and the hardware (Apple M1 Pro) is stated. The Go toolchain version and flags are not stated; go.mod only has the 'go 1.24.1' language directive, so it is not Tier A. The comparison is not like-for-like. The net/http benchmarks create a new bufio.NewReader (4 KB buffer) on every iteration and build a full \*http.Request, which accounts for much of the 5 KB/op, while this parser only records byte offsets. The README also lists missing features that net/http has: no chunked decoding, no request-smuggling (CL/TE conflict) checks, silent Content-Length overflow, no header size cap, no bare-LF or obs-fold handling, and requests only. net/http is not one of the named category baselines (llhttp, http-parser, picohttpparser), but it is the de facto Go incumbent. No license, 0 stars, a single commit.

In-place, zero-copy parsing into caller-owned byte slices - offsets are only valid while the buffer is unmodified; README lists explicit 'What's Missing' gaps versus net/http's full feature set (e.g. no chunked-body reassembly convenience, no cookie jar/multipart helpers mentioned).

## Maintenance

The record says active, but the repo is a single 'init' commit from 2026-02-08, untouched for \~7.5 months, with 0 stars, 0 issues, no releases and no license. That makes it usable only as a reference to read, not as a dependency to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table matches the record exactly (133 vs 1,377, 161 vs 1,602 and 374 vs 2,021 ns/op; 0 vs 5,177-5,345 B/op; 495-641 vs 48-98 MB/s), measured against net/http.ReadRequest on an Apple M1 Pro. The benchmark code is public (parser/parser_test.go), but the Go toolchain version and flags are not stated, so it stays C.
- **Verifier notes:** Numbers verified word for word against the README and the benchmark code. The record's metric is 'throughput', but the headline figures are ns/op latency, with MB/s given as secondary; metric is not a correctable field. Metadata checked and correct (no license, 0 stars, last commit 2026-02-08, not a fork).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jianrong7/http-parser>
  - <https://github.com/jianrong7/http-parser/blob/main/README.md>
  - <https://raw.githubusercontent.com/jianrong7/http-parser/main/README.md>
  - <https://raw.githubusercontent.com/jianrong7/http-parser/main/parser/parser_test.go>
  - <https://raw.githubusercontent.com/jianrong7/http-parser/main/go.mod>
- **Sources the enricher read:**
  - <https://github.com/jianrong7/http-parser>
  - <https://raw.githubusercontent.com/jianrong7/http-parser/main/README.md>
  - <https://github.com/jianrong7/http-parser/tree/main/parser>
  - <https://raw.githubusercontent.com/jianrong7/http-parser/main/parser/parser.go>
  - <https://raw.githubusercontent.com/jianrong7/http-parser/main/parser/parser_test.go>
  - <https://raw.githubusercontent.com/jianrong7/http-parser/main/main.go>
  - <https://raw.githubusercontent.com/jianrong7/http-parser/main/go.mod>
  - <https://github.com/jianrong7/http-parser/issues>
  - <https://github.com/jianrong7/http-parser/pulls>
  - https://api.github.com/graphql (repository jianrong7/http-parser: license, stars, commit history)
  - <https://hn.algolia.com/api/v1/search?query=jianrong7&restrictSearchableAttributes=url>
  - <https://hn.algolia.com/api/v1/search?query=%22jianrong7%2Fhttp-parser%22>
  - <https://raw.githubusercontent.com/golang/go/master/src/net/http/request.go>
  - <https://raw.githubusercontent.com/h2o/picohttpparser/master/picohttpparser.h>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/jianrong7/http-parser`) · [data/wave5/enrich/raw/github_com_jianrong7_http_parser.json](../../../data/wave5/enrich/raw/github_com_jianrong7_http_parser.json) (enrichment confidence 0.7)

</details>
