# httpbeast

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Nim` · `MIT` · 🟡 stale

> Minimal multi-threaded epoll/kqueue HTTP/1.1 server core for Nim; about 7% above actix-web at 256-512 connections on hello-world.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | the-benchmarker/web-frameworks data.json of 2026-09-24 (develop branch, commit f673364): httpbeast 0.4 166,875 / 179,385 / 175,501 req/s at concurrency 64 / 256 / 512 vs actix (actix-web 4.8) 179,203 / 168,270 / 163,415 req/s, i.e. 0.93x / 1.07x / 1.07x (derived from page data). The earlier snapshot on master (commit 0fccb1d, 2026-09-20, older method) shows 128,768 / 106,892 / 104,657 vs 115,638 / 102,329 / 99,835 req/s, i.e. 1.11x / 1.04x / 1.05x (derived from page data). |
| **Workload** | the-benchmarker/web-frameworks develop-branch run of 2026-09-24 (commit f673364): zrk --closed, a closed loop over keep-alive connections (not oha with keep-alive disabled; the README method table dates that model to before 2026-08), 15 s per concurrency level 64/256/512. Each headline req/s is avg() over the three routes in .env (GET /, GET /user/0, POST /user) per .tasks/db.rake; the 1/3 fractions in the values fit a 3-route average. All handlers are hello-world (empty body or echoed id). |
| **Metric** | throughput |
| **Hardware** | Undisclosed x86_64 Linux host (Fedora 44 kernel 7.2.6-200.fc44), 16 logical CPUs. The cpu_name 'M1 Eight-Core Processor' in data.json is a string hardcoded in .tasks/db.rake, not a measured CPU model. The framework container is pinned to cores 0-3 (SERVER_CPUS) and the load generator to cores 4-15 (LOAD_CPUS). |
| **Compiler and flags** | Nim 2.2 (nimlang/nim:2.2 image), nim c --mm:refc --assertions:off -d:release --opt:speed --passC:-flto --passL:-flto server.nim (nim/Dockerfile with nim/httpbeast/config.yaml build_opts). actix-web 4.8 baseline: Rust 1.98 (rust:1.98-slim), cargo build --release with lto=true, codegen-units=1, panic=abort (rust/Dockerfile). |
| **Adoption** | 472 stars; Jester's HTTP backend (jester.nimble requires httpbeast &gt;= 0.4.0); Prologue uses httpx, a separate server derived from httpbeast |
| **Last commit** | 2023-12-10 |
| **Links** | [repository](https://github.com/dom96/httpbeast) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

In the-benchmarker/web-frameworks develop-branch run of 2026-09-24 (commit f673364), httpbeast 0.4 built with Nim 2.2, --mm:refc, -d:release and LTO served 179k and 176k req/s at 256 and 512 keep-alive connections vs actix-web 4.8 (Rust 1.98, LTO) at 168k and 163k (1.07x), but was 7% slower at 64 connections (167k vs 179k). Each server was pinned to 4 cores of an undisclosed 16-thread x86_64 Linux host, and each figure is the average of three hello-world routes; the same data show httpbeast's p99 3.5-20x worse than actix's.

## Use it when

- You are writing a Nim web framework or a resource-constrained Nim service and want the raw HTTP/1.1 core that Jester and the Nim Forum run on.
- Small plaintext/JSON endpoints on Linux (or macOS) behind nginx or another reverse proxy that terminates TLS and sanitizes requests.
- Many keep-alive connections at moderate-to-high concurrency (256-512) where aggregate req/s matters more than tail latency.
- Mostly synchronous handlers that can return a nil Future, or async handlers whose awaits are fd-based (sockets, addTimer).
- Clients that pipeline GET requests.

## Skip it when

- Directly on the open internet: the README says it is not hardened and should sit behind a reverse proxy; a 2023 request-smuggling report (#95) was closed with that same advice, a body longer than its Content-Length trips an assertion (#21, open; with assertions off the connection waits forever), and a GET with a body is never answered (#18, open) because only POST/PUT/PATCH/CONNECT get a body scan.
- Tail-latency-sensitive services: in the same 2026-09-24 run httpbeast's p99 was 8.1/10.9/11.3 ms at 64/256/512 connections vs actix-web's 0.40/1.58/3.22 ms, even though its median was lower.
- You need TLS (#11, open since 2018), HTTP/2, streamed or chunked request bodies (#74, open), built-in WebSockets, or Windows (unsupported by design).
- Nim 2 default ORC memory management with threads: random segfaults are reported (#80 open; #90 SIGSEGV on Nim 2.0 with Jester), and the benchmark itself builds with --mm:refc.
- Large request bodies: reads go through a 256-byte stack buffer copied byte by byte into the connection string, and a user reported Vert.x faster with bodies over about 500 bytes (#86, open).

## How it is fast

Thread-per-core, shared-nothing: with --threads:on every thread opens its own listening socket with SO_REUSEPORT and runs its own Nim `selectors` loop (epoll on Linux, kqueue on macOS), so the kernel spreads accepts and no connection crosses threads. Reads are non-blocking until EAGAIN; end of headers is detected by checking only the last four bytes for CRLFCRLF, with a full scan only for body-carrying methods, and method/path/headers are parsed lazily from the raw buffer when the handler asks. Responses are copied straight into a per-connection send queue by a macro-unrolled append, the Date header is cached and refreshed by a one-second timer, TCP_NODELAY is set, and a handler may return a nil Future to skip asyncdispatch entirely. HTTP pipelining is supported for bodiless requests.

## Compared with alternatives

Pick httpbeast only when the service is written in Nim or you are building a Nim framework. In the same run may_minihttp (194k req/s at 512) and fulmine.js (204k) were faster and http.zig (171k) was comparable, so in Rust, JavaScript or Zig use those instead.

## Integration

| | |
|---|---|
| **Form** | module (Nimble package; about 720 lines of pure Nim source compiled into your program) |
| **Dependencies** | none beyond the Nim stdlib (selectors, asyncdispatch, net, posix); asynctools only for its tests |
| **Minimum toolchain** | httpbeast.nimble says nim &gt;= 0.18.0; CI tests Nim 1.4.8 and a Nim devel commit; code has a Nim 2 branch; benchmarked on Nim 2.2 with --mm:refc |
| **Platforms** | Linux (epoll) and macOS (kqueue), CI on ubuntu-latest and macOS-latest; no Windows by design; multi-threading needs SO_REUSEPORT (where it is missing, as on WSL, it prints that it will not use all threads) |
| **Thread safety** | One selector and event loop per thread; a Request belongs to the thread and connection that produced it. `send` may be called only once per request and raises HttpBeastDefect on a stale request. The request-ID counter is a plain global incremented without atomics. |
| **Drop-in for the baseline** | no |

## Gotchas

- `nimble install httpbeast` resolves to tag v0.4.1: the v0.4.2 bump (Nov 2022) and the Dec 2023 startup-callback change (PR #89, cited in #80/#90 as the ORC crash fix) are untagged, so you need `httpbeast#head` (#91 open).
- The server never closes a connection after responding: it ignores `Connection: close` and HTTP/1.0 semantics, so ApacheBench (`ab`) hangs (#16, open).
- Timers created with `sleepAsync` do not wake the event loop (it waits on its own selector with no timeout), so `await sleepAsync(10)` capped a benchmark at \~100 req/s; fd-based `addTimer` fixed it (#84).
- The `headers` argument of `send` is spliced in raw; a trailing or embedded blank CRLF shifts the body so Content-Length no longer matches (#56, open).

## Known shortcomings

- p99 in the same run is 3.5-20x worse than actix (8.1/10.9/11.3 vs 0.40/1.58/3.22 ms at c=64/256/512) despite a lower median. Not hardened; the README says to put it behind a reverse proxy and a smuggling report (#95) was closed with that advice. Open bugs: a body longer than Content-Length asserts or hangs with assertions off (#21); GET with a body is never answered (#18); never closes connections and ignores Connection: close/HTTP/1.0, so ab hangs (#16); raw header strings can break Content-Length (#56). Threads under ORC (Nim 2's default) segfault (#80, #90); the benchmark builds with --mm:refc. The last tag v0.4.1 lacks later fixes, so nimble installs it unless #head is used (#91). sleepAsync timers don't wake the loop (capped one user at \~100 req/s, #84). No TLS (#11), HTTP/2, streamed/chunked request bodies (#74), WebSockets or Windows; 256-byte read buffer slows large bodies (#86). Stale since 2023-12. may_minihttp and fulmine.js beat it in the same run.

## Caveats and trade-offs

Last default-branch commit is 2023-12-10 (stale, under 3 years). The lead over actix is modest (about 7% at c=256/512) and httpbeast is 7% slower at c=64. The suite's README says to treat small differences as noise until repeated; it gives no numeric threshold. The suite changed load generator and model in 2026, and its README says results from different revisions are not comparable. The earlier snapshot still on master (commit 0fccb1d, 2026-09-20) gives different ratios, see claimed_speedup. There the lead is 4-11%. The suite's saturation probe reports identical values (0.995/0.992/0.988) for every framework checked, so it may not be a per-framework measure. Built with --mm:refc, not Nim 2's default ORC. Single synthetic hello-world workload. Hardware metadata is inconsistent ('M1 Eight-Core Processor' on x86_64).

Raw epoll/httpparser-based server with minimal features (no routing, TLS, etc.); relied upon by higher-level Nim frameworks rather than used directly

## Maintenance

Stale since 2023-12-10 with the last tag at v0.4.1, but MIT-licensed, dependency-free and small enough (about 720 lines) to vendor; it is still Jester's non-Windows backend.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks) runs httpbeast and actix in one run with public code (nim/httpbeast/server.nim, nim/httpbeast/config.yaml, nim/Dockerfile, rust/actix, rust/Dockerfile) and stated build flags. Not A: there is no real CPU model, because the cpu_name is a hardcoded string in .tasks/db.rake.
- **Verifier notes:** The figures match the develop-branch data.json (commit f673364), not the master URL cited, so benchmark_url is pinned. last_commit is corrected from 2024-01-07 (pushedAt) to the default-branch HEAD date 2023-12-10; it is still 'stale'. Prologue depends on httpx, not httpbeast, so stars_or_usage is corrected. Metadata verified: MIT, 472 stars, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/0fccb1d5a502432d76dc1364ab6babf709ef1380/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/README.md>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/.env>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/db.rake>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/actix/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/nim/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/nim/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/nim/httpbeast/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/nim/httpbeast/server.nim>
  - <https://github.com/dom96/httpbeast>
  - <https://github.com/dom96/jester/blob/master/jester.nimble>
  - <https://github.com/planety/prologue/blob/devel/prologue.nimble>
  - <https://github.com/ringabout/httpx>
  - <https://github.com/ringabout/httpx/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/dom96/httpbeast>
  - <https://github.com/dom96/httpbeast/blob/master/readme.md>
  - <https://github.com/dom96/httpbeast/blob/master/httpbeast.nimble>
  - <https://github.com/dom96/httpbeast/blob/master/src/httpbeast.nim>
  - <https://github.com/dom96/httpbeast/blob/master/src/httpbeast/parser.nim>
  - <https://github.com/dom96/httpbeast/blob/master/.github/workflows/main.yml>
  - <https://github.com/dom96/httpbeast/blob/master/tests/tester.nim>
  - <https://github.com/dom96/httpbeast/blob/master/tests/helloworld.nim>
  - <https://github.com/dom96/httpbeast/commits/master.atom>
  - <https://github.com/dom96/httpbeast/tags>
  - <https://github.com/dom96/httpbeast/issues>
  - <https://github.com/dom96/httpbeast/issues/11>
  - <https://github.com/dom96/httpbeast/issues/16>
  - <https://github.com/dom96/httpbeast/issues/18>
  - <https://github.com/dom96/httpbeast/issues/20>
  - <https://github.com/dom96/httpbeast/issues/21>
  - <https://github.com/dom96/httpbeast/issues/56>
  - <https://github.com/dom96/httpbeast/issues/78>
  - <https://github.com/dom96/httpbeast/issues/80>
  - <https://github.com/dom96/httpbeast/issues/84>
  - <https://github.com/dom96/httpbeast/issues/86>
  - <https://github.com/dom96/httpbeast/issues/90>
  - <https://github.com/dom96/httpbeast/issues/95>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/nim/httpbeast/server.nim>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/nim/httpbeast/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/nim/httpbeast/server.nimble>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/nim/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/nim/config.yaml>
  - <https://github.com/dom96/jester/blob/master/jester.nimble>
  - <https://hn.algolia.com/api/v1/search?query=httpbeast>
  - <https://news.ycombinator.com/item?id=47501229>
  - <https://news.ycombinator.com/item?id=36958393>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/dom96/httpbeast`) · [data/wave5/enrich/raw/github_com_dom96_httpbeast.json](../../../data/wave5/enrich/raw/github_com_dom96_httpbeast.json) (enrichment confidence 0.8)

</details>
