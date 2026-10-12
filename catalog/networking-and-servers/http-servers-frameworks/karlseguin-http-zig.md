# http.zig (httpz)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig HTTP/1.1 server library on epoll/kqueue; ties actix-web on hello-world req/s, leading \~5% only at 512 connections.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | the-benchmarker/web-frameworks data.json of 2026-09-24 (develop branch, commit f673364): httpz (commit 52eb187) 146,153 / 168,006 / 171,398 req/s at concurrency 64 / 256 / 512 vs actix (actix-web 4.8) 179,203 / 168,270 / 163,415 req/s, i.e. 0.82x / 1.00x / 1.05x (derived from page data). httpz is slower at c=64, tied at c=256 and about 5% ahead only at c=512. The earlier snapshot on master (commit 0fccb1d, 2026-09-20, older method) shows 189,979 / 152,822 / 156,074 vs 115,638 / 102,329 / 99,835 req/s, i.e. 1.64x / 1.49x / 1.56x (derived from page data). |
| **Workload** | the-benchmarker/web-frameworks develop-branch run of 2026-09-24 (commit f673364): zrk --closed, a closed loop over keep-alive connections (not oha with keep-alive disabled; the README method table dates that model to before 2026-08), 15 s per concurrency level 64/256/512. Each headline req/s is avg() over the three routes in .env (GET /, GET /user/0, POST /user) per .tasks/db.rake; the 1/3 fractions in the values fit a 3-route average. All handlers are hello-world (empty body or echoed id). httpz runs with workers and thread pool sized to the CPU count. |
| **Metric** | throughput |
| **Hardware** | Undisclosed x86_64 Linux host (Fedora 44 kernel 7.2.6-200.fc44), 16 logical CPUs. The cpu_name 'M1 Eight-Core Processor' in data.json is a string hardcoded in .tasks/db.rake, not a measured CPU model. The framework container is pinned to cores 0-3 (SERVER_CPUS) and the load generator to cores 4-15 (LOAD_CPUS). |
| **Compiler and flags** | Zig 0.16.0, zig build -Doptimize=ReleaseFast (zig/Dockerfile), httpz pinned to commit 52eb187. actix-web 4.8 baseline: Rust 1.98 (rust:1.98-slim), cargo build --release with lto=true, codegen-units=1, panic=abort (rust/Dockerfile). |
| **Adoption** | 1.6k stars |
| **Last commit** | 2026-08-26 |
| **Links** | [repository](https://github.com/karlseguin/http.zig) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

In the-benchmarker/web-frameworks run of 2026-09-24 (develop, commit f673364), httpz commit 52eb187 built with Zig 0.16.0 ReleaseFast averaged 146k/168k/171k req/s over three hello-world routes at 64/256/512 closed-loop keep-alive connections vs actix-web 4.8 (Rust 1.98, release, LTO) at 179k/168k/163k, i.e. 0.82x/1.00x/1.05x, with the server pinned to 4 cores of an undisclosed 16-thread x86_64 Linux host. The 2026-09-20 snapshot of the same httpz commit under an older load method showed 1.49x-1.64x, so the ratio depends on how the suite measures, not on httpz changes.

## Use it when

- Your service is already in Zig and needs an HTTP/1.1 API server. In the 2026-09-24 run httpz reached 146k-171k req/s, while zzz, the other Zig framework in that run, reached 57k-69k req/s (derived from page data).
- Deployment behind a reverse proxy such as nginx that terminates TLS and tolerates non-compliant upstreams. The README designs for this and recommends proxy-side timeouts.
- Keep-alive REST/JSON traffic with small requests at high connection counts, where median latency matters. httpz's p50 was lower than actix-web's at every level: 0.29/1.22/2.52 ms vs 0.35/1.52/3.13 ms at c=64/256/512 (derived from page data).
- Actions that make blocking calls, such as a pg.zig pool query. Actions run on a thread pool (default 32 threads) sized separately from the epoll workers, so a blocking action does not stall the event loop.
- You want a bounded memory footprint you can size up front. The README gives a minimum-memory formula from thread_pool, workers and request buffer settings.

## Skip it when

- Tail latency matters. In the same run httpz's p99 was 3.48/5.58/9.13 ms vs actix-web's 0.39/1.58/3.22 ms at c=64/256/512, 2.8x-8.8x higher, and its c=64 throughput was 18% lower (derived from page data).
- You need TLS, HTTP/2 or HTTP/3 in-process. The parser accepts only HTTP/1.0 and HTTP/1.1, and the owner said in issue #148 he would add TLS only if Zig's std gains a tls.Server.
- Clients connect directly without a proxy. The README says httpz 'may never be fully HTTP/1.1 compliant' (e.g. no Date header), timeouts are effectively disabled by default, and non-epoll/kqueue platforms such as Windows use a thread-per-connection blocking mode the README calls easy to DoS.
- You need a stable toolchain or proven concurrency. master targets Zig 0.16.0 and the README calls this port 'not well tested' and 'experimental'. Issue #125, open since 2025-05, reports ThreadSanitizer races and a 'switch on corrupt value' panic under 100 concurrent slow requests on an older version; a later comment traces a crash to epoll returning an fd closed in the previous batch.
- Windows production use. Open issues report a service being killed (#182) and cross-thread websocket writes hanging in blocking mode (#74), and the owner says he cannot reproduce Windows problems.

## How it is fast

N worker threads each run their own epoll (Linux) or kqueue (BSD/macOS) loop over one shared non-blocking listener (the epoll registration uses EPOLLEXCLUSIVE to limit thundering-herd wakeups) and parse requests incrementally into a pre-allocated per-connection Request.State buffer, so bytes that trickle in are not re-parsed. Parsed requests are queued, in batches of up to 16 to cut locking, to a separate thread pool that runs the action and writes the response with blocking writev, then hands the connection back to its worker through a handover list. Per-request memory comes from a FallbackAllocator: a thread-local fixed buffer (thread_pool.buffer_size) first, then the connection's retained arena, plus per-worker pools of large buffers, so the hot path rarely reaches the general-purpose allocator. The parser compares 4-byte words as u32 to match methods and the 'HTTP/1.x' version, and lower-cases header names in place.

## Compared with alternatives

Pick httpz when the application is in Zig and you want a full-featured server library (router, middleware, WebSocket, test helpers) rather than a bare parser. If you are not tied to Zig, fulmine.js (204k), may_minihttp (194k), ohkami-nio (182k) and httpbeast (176k) all beat httpz's 171k req/s at c=512 in the same run, and fulmine.js, may_minihttp and ohkami-nio also had lower p99 (derived from page data).

## Integration

| | |
|---|---|
| **Form** | module (Zig package added with zig fetch and build.zig.zon; compiled from source) |
| **Dependencies** | metrics.zig and websocket.zig (Zig packages pinned in build.zig.zon); links libc (link_libc = true) |
| **Minimum toolchain** | Zig 0.16.0 on master; zig-0.15 branch for Zig 0.15; dev branch tracks Zig master |
| **Platforms** | Linux (epoll) and BSD/macOS (kqueue) in non-blocking mode; everything else, notably Windows, runs a thread-per-connection blocking mode |
| **Thread safety** | Actions run concurrently on the thread pool. The handler instance passed to Server(H).init is shared by all concurrent requests, so its state must be thread-safe; put per-request data in a context built in dispatch. Request and Response objects are per request. |
| **Drop-in for the baseline** | no |

## Gotchas

- res.body and res.header name/value slices must stay valid until the response is sent after the action returns. Allocate them from res.arena, or use res.headerOpts with dupe_name/dupe_value.
- Limits drop data silently: headers beyond request.max_header_count (32), route params beyond max_param_count (10) and query params beyond max_query_count (32) are ignored. formData()/multiFormData() return nothing useful until max_form_count/max_multiform_count are set above their default of 0. All request headers must fit in request.buffer_size (4 KB default), else the request is rejected.
- Chunked request bodies are always buffered fully in memory and ignore lazy_read_size (owner, issue #170). multiFormData() rewrites escaped field names inside the raw body in place, and each SSE stream from startEventStream runs on its own new thread.
- Defaults are 1 epoll worker and 32 pool threads (config.zig); the benchmark set both to the CPU count, so tune workers.count before comparing. The router does not backtrack: with '/:any/users' and '/hello/users/test' registered, '/hello/users' matches nothing, and routes must be lowercase (README).

## Known shortcomings

- The win over actix is marginal and method-dependent: 0.82x/1.00x/1.05x at c=64/256/512 in the 2026-09-24 run versus 1.49-1.64x for the same httpz commit in the 2026-09-20 snapshot with the older load method. p99 is 2.8-8.8x worse than actix (3.48/5.58/9.13 vs 0.39/1.58/3.22 ms) though p50 is lower. fulmine.js, may_minihttp, ohkami-nio and httpbeast all beat it at c=512 in the same run. No TLS (#148), HTTP/1.x only, and the README says it may never be fully HTTP/1.1 compliant (no Date header) and assumes a reverse proxy. The Zig 0.16 port on master is 'experimental'; ThreadSanitizer races and a corrupt-value panic under concurrent slow requests (#125) are open; Windows falls back to an easily DoS'd thread-per-connection mode (#182, #74). Header/param/query limits drop data silently; chunked bodies are fully buffered (#170); the router doesn't backtrack; default is 1 worker.

## Caveats and trade-offs

In the current revision httpz beats actix only at c=512, by about 5%, and loses by 18% at c=64. The suite's README says to treat small differences as noise until repeated; it gives no numeric threshold. The earlier master snapshot shows a 1.5-1.6x lead, so the result is unstable across revisions. The suite changed load generator and model in 2026, and its README says results from different revisions are not comparable. The earlier snapshot still on master (commit 0fccb1d, 2026-09-20) gives different ratios, see claimed_speedup. The suite's saturation probe reports identical values (0.995/0.992/0.988) for every framework checked, so it may not be a per-framework measure. Single synthetic hello-world workload. Hardware metadata is inconsistent ('M1 Eight-Core Processor' on x86_64).

Zig itself is pre-1.0 and its ABI/language still churns between releases; smaller ecosystem/community than Rust web frameworks; no built-in TLS

## Maintenance

Actively maintained (last commit 2026-08-26, 1.6k stars) and MIT-licensed, consumed as a Zig package; the Zig 0.16 port on master is self-described as experimental, and older Zig versions live on zig-X.YY branches.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks) runs httpz and actix in one run with public code (zig/httpz/src/main.zig, zig/httpz/build.zig, zig/Dockerfile, rust/actix, rust/Dockerfile) and stated build flags. Not A: there is no real CPU model, because the cpu_name is a hardcoded string in .tasks/db.rake.
- **Verifier notes:** The c=512 figures match the develop-branch data.json (commit f673364), not the master URL cited, so benchmark_url is pinned. The claim is accurate for c=512 but omits the c=64 loss; claimed_speedup now lists all levels and both snapshots. Metadata verified: MIT, 1,606 stars, last commit 2026-08-26, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
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
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/zig/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/zig/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/zig/httpz/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/zig/httpz/build.zig>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/zig/httpz/src/main.zig>
  - <https://github.com/karlseguin/http.zig>
- **Sources the enricher read:**
  - <https://github.com/karlseguin/http.zig>
  - <https://github.com/karlseguin/http.zig/blob/master/readme.md>
  - <https://github.com/karlseguin/http.zig/blob/master/build.zig.zon>
  - <https://github.com/karlseguin/http.zig/blob/master/build.zig>
  - <https://github.com/karlseguin/http.zig/tree/master/src>
  - <https://github.com/karlseguin/http.zig/blob/master/src/worker.zig>
  - <https://github.com/karlseguin/http.zig/blob/master/src/thread_pool.zig>
  - <https://github.com/karlseguin/http.zig/blob/master/src/request.zig>
  - <https://github.com/karlseguin/http.zig/blob/master/src/response.zig>
  - <https://github.com/karlseguin/http.zig/blob/master/src/router.zig>
  - <https://github.com/karlseguin/http.zig/blob/master/src/httpz.zig>
  - <https://github.com/karlseguin/http.zig/blob/master/src/config.zig>
  - <https://github.com/karlseguin/http.zig/commits/master.atom>
  - <https://github.com/karlseguin/http.zig/issues?q=chunked>
  - <https://github.com/karlseguin/http.zig/issues?q=is:open>
  - <https://github.com/karlseguin/http.zig/issues/74>
  - <https://github.com/karlseguin/http.zig/issues/99>
  - <https://github.com/karlseguin/http.zig/issues/125>
  - <https://github.com/karlseguin/http.zig/issues/148>
  - <https://github.com/karlseguin/http.zig/issues/170>
  - <https://github.com/karlseguin/http.zig/issues/175>
  - <https://github.com/karlseguin/http.zig/issues/182>
  - <https://github.com/karlseguin/http.zig/issues/199>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/0fccb1d5a502432d76dc1364ab6babf709ef1380/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/zig/httpz/src/main.zig>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/zig/httpz/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/zig/httpz/build.zig>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/zig/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/zig/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/README.md>
  - <https://hn.algolia.com/api/v1/search?query=karlseguin%20http.zig>
  - <https://hn.algolia.com/api/v1/items/38950147>
  - <https://hn.algolia.com/api/v1/items/40690763>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/karlseguin/http.zig`) · [data/wave5/enrich/raw/github_com_karlseguin_http_zig.json](../../../data/wave5/enrich/raw/github_com_karlseguin_http_zig.json) (enrichment confidence 0.45)

</details>
