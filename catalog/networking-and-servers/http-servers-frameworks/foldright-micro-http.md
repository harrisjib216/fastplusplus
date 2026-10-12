# micro-http (foldright)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Tiny tokio HTTP/1.1 server and web framework; matches actix-web on hello-world throughput, ahead \~2% only at 512 connections.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | the-benchmarker/web-frameworks data.json, develop commit f673364 (2026-09-24): micro-web 0.3 169,642 / 166,580 / 166,409 req/s at concurrency 64 / 256 / 512 vs actix (actix-web 4.8) 179,203 / 168,270 / 163,415 req/s, i.e. 0.95x / 0.99x / 1.02x (derived from page data). It is slower at c=64 and c=256 and \~2% faster only at c=512. The older-method snapshot on master (commit 0fccb1d, 2026-09-20) shows 135,783 / 113,734 / 112,482 vs 115,638 / 102,329 / 99,835 req/s, i.e. 1.17x / 1.11x / 1.13x (derived from page data). |
| **Workload** | the-benchmarker/web-frameworks develop-branch run of 2026-09-24 (commit f673364): zrk --closed, a closed loop over keep-alive connections (not wrk), 15 s per concurrency level 64/256/512; the framework container is pinned to cores 0-3 and the load generator to cores 4-15 (.env). Each headline req/s is avg() over the three routes in .env (GET / with empty body, GET /user/0 echoing the id, POST /user with empty body) per .tasks/db.rake, so it is not a single plaintext route. All handlers are hello-world. |
| **Metric** | throughput |
| **Hardware** | Undisclosed x86_64 Linux host (Fedora 44 kernel 7.2.6-200.fc44.x86_64), 16 logical CPUs. The cpu_name 'M1 Eight-Core Processor' (and the memory figure) in data.json are strings hard-coded in .tasks/db.rake, not measured. Server pinned to cores 0-3 (it kept \~3.95 cores busy at \~98.7% saturation per data.json), load generator to cores 4-15. |
| **Compiler and flags** | micro-web 0.3 (crates.io) on tokio multi-thread, Rust 1.98 (rust:1.98-slim), cargo build --release with opt-level=3, lto=true, codegen-units=1, panic=abort (rust/micro-web/Cargo.toml, rust/Dockerfile). Baseline actix-web 4.8: Rust 1.98 (rust:1.98-slim), cargo build --release with opt-level=3, lto=true, codegen-units=1, panic=abort (rust/actix/Cargo.toml, rust/Dockerfile). |
| **Adoption** | 29 stars; micro-web crate 12,055 all-time crates.io downloads (109 recent) |
| **Last commit** | 2026-08-01 |
| **Links** | [repository](https://github.com/foldright/micro-http) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

the-benchmarker/web-frameworks ran micro-web 0.3.0 from crates.io against actix-web 4.8 on 2026-09-24 (develop f673364). Setup: zrk closed-loop keep-alive, 15 s per level, averaging hello-world GET /, GET /user/0 and POST /user; both built with Rust 1.98, LTO, codegen-units=1 and panic=abort; server pinned to 4 cores of an undisclosed 16-thread x86-64 Linux host whose 'M1' CPU label is hard-coded. Results were 169,642 / 166,580 / 166,409 vs 179,203 / 168,270 / 163,415 req/s at 64 / 256 / 512 connections (0.95x / 0.99x / 1.02x), with micro-web's p99 1.6-1.9x higher (0.65 vs 0.40 ms at c=64, 6.03 vs 3.22 ms at c=512). The 1.11-1.17x lead cited elsewhere comes only from the superseded 2026-09-20 master snapshot.

## Use it when

- Internal HTTP/1.1 text/JSON services behind a TLS-terminating reverse proxy, where hello-world throughput about equal to actix-web is enough (about 166-170k req/s on 4 pinned cores in the 2026-09-24 run).
- Embedding an HTTP/1.1 endpoint over a custom transport: micro-http's `HttpConnection` takes any AsyncRead + AsyncWrite pair (for example a Unix socket or an in-memory duplex) and a `Handler` that returns `http::Response<B>` with `B: Body<Data = Bytes>`. Its core dependencies are small (httparse, http, bytes, tokio-util).
- Studying or forking a compact HTTP/1.1 implementation (about 7,000 lines across both crates' src, including tests and doc comments) that covers chunked and Content-Length bodies in both directions plus Expect: 100-continue.
- Prototypes that want axum-style extractor handlers (`async fn h(method: &Method, Json(u): Json<User>) -> String`) and can live with alpha-stage API churn.

## Skip it when

- You need a real throughput win over actix-web. In the current-method run it is 0.95x / 0.99x / 1.02x at 64 / 256 / 512 connections, its p99 latency is 1.6-1.9x worse at every concurrency, and hyper, ohkami and may_minihttp all beat it in the same run.
- Directly internet-facing servers. It has no TLS, no HTTP/2 or HTTP/3, no read, idle or header timeouts (so it is exposed to slowloris), and no handling of `Connection: close`. The Bytes, String, Json and Form extractors also buffer the whole request body with no size limit.
- Streaming responses (SSE, large downloads) on the crates.io release. 0.3.0 encodes every response frame into an in-memory buffer and writes it to the socket only when the body ends, so SSE events arrive only when the stream closes and large bodies sit fully in RAM. Only the unreleased git head streams.
- Services that need graceful shutdown. `Server::start` stops accepting only on Ctrl-C (SIGINT); it does not handle SIGTERM and does not drain open connections.
- Production use that needs maturity or lean builds. The README calls it alpha; it has one maintainer, 29 stars and 0 crates.io reverse dependencies; it has no tower middleware and no WebSocket/Upgrade support. micro-web always pulls in zstd (a C library), brotli, flate2 and the dhat heap profiler, none of them optional.

## How it is fast

There is no novel technique; it is a thin layer over tokio that skips work. httparse parses each request head into a stack `MaybeUninit` header array (at most 64 headers). The head is then split off the read buffer once (`BytesMut::split_to().freeze()`), and the URI and every header value become ref-counted `Bytes` slices of it, built with unsafe `HeaderValue::from_maybe_shared_unchecked` to skip re-validation (the code comment credits this trick to actix). The Date header is formatted by a background task every 800 ms and shared through ArcSwap, accepted sockets get TCP_NODELAY, and each connection is one spawned task on the app's tokio runtime (the benchmark used the default multi-thread runtime). The benchmarked 0.3.0 encodes the whole response into a reused per-connection buffer (8 KB initial) and does one write plus flush per response; the unreleased git head (2026-08-01) sends head and body in one vectored write with no flush.

## Compared with alternatives

In the same 2026-09-24 run, hyper 1.5 (also tokio) beat micro-web at all three concurrencies (173.6k / 168.8k / 166.6k vs 169.6k / 166.6k / 166.4k req/s), and may_minihttp (194k at c=512) and ohkami-nio (182k) were clearly faster. Pick micro-web only if you specifically want its small codebase and extractor-style API over hyper's bare service API; choose may_minihttp or ohkami for throughput and actix-web or hyper for maturity.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | micro-http 0.3.0: tokio, tokio-util, httparse, http, http-body, http-body-util, bytes, futures, mime, thiserror, trait-variant, tracing, tracing-subscriber. micro-web 0.3.0 adds matchit, serde, serde_json, serde_urlencoded, serde_qs, flate2, zstd (C library), brotli, dhat, arc-swap, once_cell, async-trait, dynosaur, hlist2, tower-layer, pin-project-lite and faf-http-date, all non-optional. |
| **Minimum toolchain** | Rust 1.90 (MSRV; edition 2024); CI tests 1.90, stable, beta and nightly |
| **Platforms** | Anywhere tokio runs, in principle; CI covers ubuntu-latest only, and other platforms are not documented |
| **Thread safety** | Handlers must be Send + Sync (micro-http `Handler: Sync` with Send futures); the Server and its router are shared across tasks through an Arc. Each connection is one tokio task, and requests on a connection are handled one at a time. |
| **Drop-in for the baseline** | no |

## Gotchas

- `Server::start()` installs its own global tracing subscriber at WARN level with `set_global_default(...).expect(...)`, so it panics if your app has already installed one. It also `unwrap()`s `set_nodelay` and address resolution. If you need control over these, drive micro-http's `HttpConnection` yourself.
- The response header encoder calls `status.canonical_reason().unwrap()`, so a status code with no canonical reason (for example a custom 5xx/4xx) panics the connection task. Responses whose version is not HTTP/1.1 are rejected as Unsupported.
- `EncodeDecorator` compresses gzip and deflate at `Compression::best()` (level 9), which is CPU-heavy, and turns the response into a chunked stream. It checks for Content-Encoding on the request rather than the response, so a body the handler has already compressed can be encoded twice.
- Version trap. Published 0.3.0, the version the benchmark ran, buffers whole responses (see above). The git head fixes streaming, but since 2026-01-19 it passes the request body as a raw-pointer vtable (`unsafe impl Send for StreamingReqBody`), and `ReqBody` has no lifetime, so moving it out of the handler (for example into `tokio::spawn`) can outlive its backing state. The README Quick Start still pins `micro-web = "0.1"`, and 0.1.1 fails to compile on Rust 1.92 (issue #3).

## Known shortcomings

- In the current run (2026-09-24) it is slower than actix at c=64 (0.95x) and c=256 (0.99x) and only 1.02x at c=512; the record cherry-picked c=512. Only the older 2026-09-20 snapshot (different method) shows 1.11-1.17x. The benchmark used micro-web 0.3 from crates.io (2025-10), not the repo head.
- p99 is 1.6-1.9x worse than actix at every concurrency (0.65 vs 0.40 ms at c=64; 6.03 vs 3.22 ms at c=512) with \~6x the stdev at c=512; hyper and ohkami-tokio beat it at all three levels. The benchmarked crates.io 0.3.0 buffers whole response bodies until the end (SSE arrives only on close; large streams sit in RAM); only unreleased git head streams. Git head's request body is a raw-pointer vtable with unsafe impl Send and no lifetime, so moving it into tokio::spawn can outlive its state (code reading). Not internet-safe: no TLS, HTTP/2/3 or WebSocket; no read/idle/header timeouts (slowloris); Connection: close ignored; body extractors unbounded; SIGINT only, no draining. Server::start panics if a tracing subscriber already exists; non-standard status codes panic via canonical_reason().unwrap(). Compression at level 9 checks the request's Content-Encoding, so pre-compressed bodies can be compressed twice. Non-optional zstd, brotli, flate2 and dhat dependencies. Alpha, one maintainer, 0 reverse dependencies; README Quick Start points at 0.1 (fails on Rust 1.92, #3). Licence is MIT OR Apache-2.0. The benchmark entry was added by the project's author.

## Caveats and trade-offs

Very low notability. The shootout measured micro-web 0.3 from crates.io (last published 2025-10-03), not the repo head (e.g. the 2026-08-01 response-write-path optimization). In the current-method 2026-09-24 run it is at parity with actix (0.95x / 0.99x / 1.02x at c=64/256/512); the 1.11-1.17x lead appears only in the superseded-method 2026-09-20 snapshot, and the suite's README says results from different revisions are not comparable. The project's own README makes no speed claim and says it is 'not in this benchmark yet'. Single synthetic hello-world workload (3-route average). Hardware metadata is inconsistent ('M1 Eight-Core Processor' on x86_64, hard-coded).

Very small/young project with a minimal feature set compared to full actix-web.

## Maintenance

Actively committed alpha with one maintainer: last commit 2026-08-01, but the last crates.io release is 0.3.0 from 2025-10-03, so the benchmark did not include the newer write-path change. Dual-licensed MIT OR Apache-2.0 per Cargo.toml and the README (GitHub shows only Apache-2.0).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks) runs micro-web (the micro-http workspace's framework crate) and actix in one run with public code (rust/micro-web/src/main.rs, rust/micro-web/Cargo.toml, rust/Dockerfile, rust/actix) and stated Rust flags, but no real CPU model (hard-coded cpu_name), so not A. It stays B only because the older-method 2026-09-20 snapshot shows a 1.11-1.17x win; the current 2026-09-24 run shows parity, so the claim is overstated.
- **Verifier notes:** The numbers belong to the 'micro-web' row (id 3142, website foldright/micro-http) and match to rounding (166,408.52 req/s). The claim picks the only concurrency where micro-web beats actix; at c=64 and c=256 in the same run it is slower, so the verdict is downgrade (tier source still B). Metadata verified: Apache-2.0, 29 stars, last commit 2026-08-01, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/0fccb1d5a502432d76dc1364ab6babf709ef1380/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/8ae370ae89075281c056a138e57de25682d36e02/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.env>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/db.rake>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/src/main.rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/micro-web/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/micro-web/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/micro-web/src/main.rs>
  - <https://github.com/foldright/micro-http>
  - <https://raw.githubusercontent.com/foldright/micro-http/main/README.md>
  - <https://crates.io/api/v1/crates/micro-web>
- **Sources the enricher read:**
  - <https://github.com/foldright/micro-http>
  - <https://github.com/foldright/micro-http/blob/main/README.md>
  - <https://github.com/foldright/micro-http/blob/main/Cargo.toml>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/Cargo.toml>
  - <https://github.com/foldright/micro-http/blob/main/crates/web/Cargo.toml>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/README.md>
  - <https://github.com/foldright/micro-http/blob/main/crates/web/README.md>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/CHANGELOG.md>
  - <https://github.com/foldright/micro-http/blob/main/crates/web/CHANGELOG.md>
  - <https://github.com/foldright/micro-http/blob/main/crates/web/src/server.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/src/connection/http_connection.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/src/connection/message_writer.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/src/codec/header/header_decoder.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/src/codec/header/header_encoder.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/src/codec/request_decoder.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/src/protocol/body/req_body.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/src/handler/mod.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/web/src/date/mod.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/web/src/router/mod.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/web/src/body.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/web/src/handler.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/web/src/extract/extract_body.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/web/src/encoding/encoder.rs>
  - <https://github.com/foldright/micro-http/blob/main/crates/http/benches/http_bench.rs>
  - <https://github.com/foldright/micro-http/blob/main/.github/workflows/ci.yml>
  - https://github.com/foldright/micro-http/tree/main (all .rs files under crates/ via raw.githubusercontent.com)
  - <https://raw.githubusercontent.com/foldright/micro-http/v0.3.0/crates/http/src/protocol/body/req_body.rs>
  - <https://raw.githubusercontent.com/foldright/micro-http/v0.3.0/crates/http/src/connection/http_connection.rs>
  - <https://raw.githubusercontent.com/foldright/micro-http/v0.3.0/crates/web/src/server.rs>
  - <https://raw.githubusercontent.com/foldright/micro-http/v0.3.0/crates/http/src/codec/header/header_encoder.rs>
  - <https://github.com/foldright/micro-http/commits/main>
  - <https://github.com/foldright/micro-http/commit/bc5409b>
  - <https://github.com/foldright/micro-http/issues/3>
  - <https://github.com/foldright/micro-http/pull/2>
  - <https://github.com/foldright/micro-http/issues?q=is%3Aissue>
  - <https://crates.io/api/v1/crates/micro-web>
  - <https://crates.io/api/v1/crates/micro-http>
  - <https://crates.io/api/v1/crates/micro-web/0.3.0/dependencies>
  - <https://crates.io/api/v1/crates/micro-http/0.3.0/dependencies>
  - <https://crates.io/api/v1/crates/micro-web/reverse_dependencies>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/.env>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/micro-web/src/main.rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/micro-web/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/micro-web/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/src/main.rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/Cargo.toml>
  - <https://hn.algolia.com/api/v1/search?query=micro-http%20rust>
  - <https://hn.algolia.com/api/v1/search?query=micro-web%20rust>
  - <https://hn.algolia.com/api/v1/search?query=foldright>
  - <https://raw.githubusercontent.com/foldright/micro-http/v0.3.0/crates/http/src/connection/message_writer.rs>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/foldright/micro-http`) · [data/wave5/enrich/raw/github_com_foldright_micro_http.json](../../../data/wave5/enrich/raw/github_com_foldright_micro_http.json) (enrichment confidence 0.7)

</details>
