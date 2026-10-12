# may_minihttp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Bare-bones Rust HTTP/1.1 server on the may stackful-coroutine runtime; 1.19x actix-web on the-benchmarker's empty-body GET.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | 194371.7 req/s vs actix-web 163414.7 req/s at concurrency 512 (\~19% faster; derived from page data) |
| **Workload** | the-benchmarker/web-frameworks: GET / (empty body), zrk --closed closed loop over keep-alive connections, \~15s run, concurrency 512, server container pinned to \~4 cores (server_cpu_cores 3.95, saturation \~0.99) with the load generator on disjoint cores; data.json revision of 2026-09-24 |
| **Metric** | throughput |
| **Hardware** | benchmark metadata reports 16 vCPUs, cpu_name 'M1 Eight-Core Processor', machine 'x86_64' (self-contradictory, see caveats) |
| **Adoption** | 934 stars |
| **Last commit** | 2026-05-06 |
| **Links** | [repository](https://github.com/Xudong-Huang/may_minihttp) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/master/data.json) |

## Verdict

On the-benchmarker/web-frameworks develop-branch data.json of 2026-09-24 (GET / with empty body; zrk closed loop over keep-alive; 15 s; server container on \~3.95 cores at \~99% CPU saturation, load generator on separate cores), may_minihttp 0.1 served 194,372 req/s vs actix-web 4.8's 163,415 at 512 connections (1.19x) and 223,705 vs 179,203 at 64 connections (1.25x), fastest of the 31 Rust entries. All entries were built with Rust 1.98, may_minihttp with thin LTO, codegen-units 1, panic=abort and may's default features off. Host metadata says 16 vCPUs on x86_64 Linux but names the CPU 'M1 Eight-Core Processor', and the master-branch data.json the record links (2026-09-20, earlier revision) shows only 105,982 vs 99,835 (1.06x).

## Use it when

- Tiny hot endpoints (health checks, plaintext or JSON micro-APIs, internal HTTP RPC) served over long-lived keep-alive or pipelined connections, where per-request CPU cost dominates.
- Services you are willing to write in synchronous style on the may runtime, using may-compatible clients (e.g. the author's may_postgres) instead of tokio crates.
- Behind a TLS-terminating reverse proxy or load balancer on x86-64 or aarch64 Linux/macOS, where the proxy handles TLS, HTTP/2, timeouts and hostile clients.
- When you want a server small enough (four compiled source files) to read the whole request path and vendor or patch it.

## Skip it when

- Apps that need routing, middleware, extractors, sessions, TLS, HTTP/2, WebSockets or streamed/chunked responses: none exist, and TLS was explicitly declined (issue #8). actix-web or ohkami provide these.
- Workloads dominated by connection setup: under the-benchmarker's older connection-per-request method a user reported it as the slowest Rust framework (issue #22, Jan 2026), and the earlier master-branch data.json (2026-09-20) has it mid-pack at 105,982 req/s, only 1.06x actix-web.
- Codebases built on tokio crates, thread-local storage or std blocking primitives: may's docs say blocking calls stall a worker thread, and TLS access across a coroutine yield can be undefined behavior.
- Handlers with deep recursion or large stack frames: coroutine stacks are fixed-size (may default 0x1000 words, i.e. 32 KiB on 64-bit, and the TechEmpower example also uses 0x1000), and may's docs say overflow hits a guard page (segfault) or is UB.
- Internet-facing without a proxy: the connection loop has no read/idle timeout, no request-size cap, no chunked request bodies and no `Connection: close`/HTTP/1.0 handling (every reply is HTTP/1.1 and the socket stays open).

## How it is fast

Each accepted connection runs in its own stackful coroutine. The loop drains the non-blocking socket into one reusable 32 KiB `BytesMut`, parses every complete pipelined request in it with `httparse` into a stack array of uninitialized header slots (16 by default), encodes all responses into a second reusable buffer, sends them with one write, and then parks on epoll/kqueue. Responses are assembled by hand: a fixed `Server: M` line, a Date string cached and refreshed every 500 ms by a background coroutine, and an itoa-formatted Content-Length, so the hot path allocates almost nothing. The author credits O(1) coroutine switches, a share-nothing mode (`HttpServiceFactory` uses the socket fd as the coroutine id, which pins each connection to one worker thread), near-SPSC scheduling when may's work-stealing default features are off, and avoiding malloc/free (issue #20); the-benchmarker build uses exactly that setup (`default-features = false`, thin LTO, codegen-units 1, panic=abort).

## Compared with alternatives

ohkami (nio backend) is the other catalogued Rust entry that beats actix-web in the same run, at 181,797 vs 194,372 req/s at c=512. Pick may_minihttp only when that \~7% and a synchronous coroutine model matter more than a real router, typed extractors and middleware. Pick it over Go's fasthttp or the C++ servers (Drogon, Workflow, H2O) when the service has to be Rust.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | may (stackful coroutine runtime; pulls generator, crossbeam, parking_lot, core_affinity, socket2, nix/libc or windows-sys), httparse, bytes, httpdate, itoa, once_cell, log |
| **Minimum toolchain** | Not documented (no rust-version field); edition 2021. Master uses io::Error::other (Rust 1.74+), its CI Dockerfile uses Rust 1.88 for dev-dependencies, and the-benchmarker built it with Rust 1.98. |
| **Platforms** | Per may: x86-64 Linux/Windows/macOS and aarch64 Linux/macOS. The build fails on Windows ARM64 (issue #11, open). Unix uses a non-blocking epoll/kqueue loop; Windows takes a simpler read + write_all path. |
| **Thread safety** | HttpServer needs a Clone + Send + Sync service and clones it for each connection; call takes &mut self, so per-connection state needs no lock. HttpServiceFactory builds one service per connection. Shared state must be Sync and should use may's sync primitives, since std Mutex or sleep blocks the worker thread. may pins its worker threads to cores by default. |
| **Drop-in for the baseline** | no |

## Gotchas

- crates.io still ships 0.1.11 (2024-09-22). The configurable request-header limit (HttpServerWithHeaders/MaxHeaders) and owned (non-'static) response headers exist only on master. In 0.1.11, a request with more than 16 headers is a parse error that drops the connection (issues #18, #26). On master the HttpServiceFactory (share-nothing) path is still fixed at 16, and src/server_builder.rs and config.rs are not compiled (not listed in lib.rs) and carry a TODO.
- A Response holds at most 16 headers because `Response::header` indexes a fixed array, so a 17th header panics. `req.body()` parses Content-Length with `unwrap()`, so a malformed value panics the connection's coroutine; under the panic='abort' profile that the repo and the-benchmarker use, that aborts the whole process.
- A request body is drained only if the handler calls `req.body()` (BodyReader's Drop skips the unread rest). `Request` has no Drop, so an ignored POST body stays in the buffer and is parsed as the next pipelined request. That usually ends in a parse error that closes the connection before the earlier responses are flushed (the symptom in issue #18). If the body is itself valid HTTP, it runs as a second request. Only Content-Length bodies are supported.
- Unsafe code on the hot path: socket reads land in uninitialized BytesMut capacity through transmute, and a background coroutine rewrites the cached Date header through an UnsafeCell with no synchronization. The runtime's dependencies have had RustSec advisories (generator RUSTSEC-2019-0020 and RUSTSEC-2020-0151, may_queue RUSTSEC-2020-0111), all patched in the versions may now uses.

## Known shortcomings

- The 1.19x holds on the suite's develop-branch data.json (2026-09-24); the linked master data.json is an older run where it is only 1.06x and mid-pack. Under the suite's earlier connection-per-request method it was the slowest Rust framework (#22); the lead needs keep-alive or pipelining. The benchmark build disables may's default features (no work stealing) and uses thin LTO, codegen-units 1, panic=abort. The crates.io release 0.1.11 (2024-09) kills connections with more than 16 request headers (#18, #26); fixes are master-only. A 17th response header or a malformed Content-Length panics (process abort under panic=abort). An unread request body is parsed as the next pipelined request, allowing request smuggling; no chunked bodies. No timeouts, size caps, Connection: close or HTTP/1.0 handling; no TLS (#8), HTTP/2, routing or streaming. may's fixed 32 KiB coroutine stacks segfault on overflow, blocking calls stall a worker and TLS-across-yield is UB, so tokio crates are effectively unusable. No Windows ARM64 (#11). Unsafe reads into uninitialized memory and unsynchronized Date-header rewrite on the hot path. Licence is MIT OR Apache-2.0.

## Caveats and trade-offs

Single-route synthetic benchmark (GET / with empty body); real-app overhead (routing, JSON, middleware) is not represented; hardware metadata inconsistent (cpu_name 'M1 Eight-Core Processor' on x86_64 Linux); the suite changed load generator and model in 2026 (oha with a new connection per request until 2026-08, zrk keep-alive after), and the README says results from different revisions are not comparable, so this ratio is valid only for the current revision

Minimal HTTP/1.1 server built on the `may` stackful-coroutine runtime, not tokio; no routing/middleware/ecosystem, so it functions as a raw-throughput micro-server rather than a full framework like actix-web

## Maintenance

Maintained but slow-moving (last commit 2026-05-06; the last crates.io release, 0.1.11, is from 2024-09, so recent fixes are master-only; one reverse dependency on crates.io). Dual MIT/Apache-2.0 per Cargo.toml and README (GitHub detects only Apache-2.0), and small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (the-benchmarker/web-frameworks data.json, updated 2026-09-24) shows may_minihttp (id 3133) at 194371.67 req/s vs actix (id 3052) at 163414.69 req/s at c=512, i.e. \~1.19x. The harness code is public, but no compiler flags are given and the CPU model metadata ('M1 Eight-Core Processor' on x86_64) is contradictory, so it is not A.
- **Verifier notes:** Numbers match data.json exactly. The record's workload said 'oha, keep-alive disabled', which comes from a stale README line. The current data carries server_cpu_saturation/cores metrics that were added 2026-09-20, and the README's methodology table says the current revision uses zrk --closed over keep-alive, so the workload was corrected. Metadata checked: Apache-2.0, 934 stars, last commit 2026-05-06, not a fork, not archived.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/README.md>
  - <https://github.com/Xudong-Huang/may_minihttp>
- **Sources the enricher read:**
  - <https://github.com/Xudong-Huang/may_minihttp>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/README.md>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/Cargo.toml>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/src/lib.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/src/http_server.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/src/request.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/src/response.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/src/date.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/src/config.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/src/server_builder.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/examples/post.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/examples/techempower_no_db.rs>
  - <https://github.com/Xudong-Huang/may_minihttp/issues>
  - <https://github.com/Xudong-Huang/may_minihttp/issues/8>
  - <https://github.com/Xudong-Huang/may_minihttp/issues/11>
  - <https://github.com/Xudong-Huang/may_minihttp/issues/14>
  - <https://github.com/Xudong-Huang/may_minihttp/issues/18>
  - <https://github.com/Xudong-Huang/may_minihttp/issues/19>
  - <https://github.com/Xudong-Huang/may_minihttp/issues/20>
  - <https://github.com/Xudong-Huang/may_minihttp/issues/22>
  - <https://github.com/Xudong-Huang/may_minihttp/issues/23>
  - <https://github.com/Xudong-Huang/may_minihttp/issues/26>
  - <https://github.com/Xudong-Huang/may_minihttp/commits/master>
  - <https://crates.io/api/v1/crates/may_minihttp>
  - <https://crates.io/api/v1/crates/may_minihttp/reverse_dependencies>
  - <https://crates.io/api/v1/crates/may>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/README.md>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/Cargo.toml>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/docs/may_caveat.md>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/coroutine_impl.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/scheduler.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/config.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/io/sys/unix/mod.rs>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/rust/may_minihttp/src/main.rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/rust/may_minihttp/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/rust/may_minihttp/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/rust/config.yaml>
  - https://hn.algolia.com/api/v1/search?query=may_minihttp&tags=(story,comment)
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/generator/RUSTSEC-2019-0020.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/generator/RUSTSEC-2020-0151.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/may_queue/RUSTSEC-2020-0111.md>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/xudong-huang/may_minihttp`) · [data/wave5/enrich/raw/github_com_xudong_huang_may_minihttp.json](../../../data/wave5/enrich/raw/github_com_xudong_huang_may_minihttp.json) (enrichment confidence 0.6)

</details>
