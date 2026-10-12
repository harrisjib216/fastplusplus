# fulmine.js

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `JavaScript` · `Apache-2.0` · 🟢 active

> Drop-in Express 5 replacement on uWebSockets.js; hello-world suite run: \~5x Express, 1.25x actix-web req/s.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | the-benchmarker/web-frameworks data.json of 2026-09-24 (develop branch, commit f673364): fulmine.js 5.21 223,508 / 210,337 / 203,996 req/s at concurrency 64 / 256 / 512 vs actix (actix-web 4.8) 179,203 / 168,270 / 163,415 req/s, i.e. 1.25x at every level (derived from page data). The earlier snapshot on master (commit 0fccb1d, 2026-09-20, older method) shows 126,063 / 106,586 / 105,030 vs 115,638 / 102,329 / 99,835 req/s, i.e. 1.09x / 1.04x / 1.05x (derived from page data). |
| **Workload** | the-benchmarker/web-frameworks develop-branch run of 2026-09-24 (commit f673364): zrk --closed, a closed loop over keep-alive connections (not oha with keep-alive disabled; the README method table dates that model to before 2026-08), 15 s per concurrency level 64/256/512. Each headline req/s is avg() over the three routes in .env (GET /, GET /user/0, POST /user) per .tasks/db.rake; the 1/3 fractions in the values fit a 3-route average. All handlers are hello-world (empty body or echoed id). fulmine.js runs with cluster:'auto' (one uWS worker per usable core, SO_REUSEPORT). |
| **Metric** | throughput |
| **Hardware** | Undisclosed x86_64 Linux host (Fedora 44 kernel 7.2.6-200.fc44), 16 logical CPUs. The cpu_name 'M1 Eight-Core Processor' in data.json is a string hardcoded in .tasks/db.rake, not a measured CPU model. The framework container is pinned to cores 0-3 (SERVER_CPUS) and the load generator to cores 4-15 (LOAD_CPUS). |
| **Compiler and flags** | Node.js 26 (node 26-slim per javascript/config.yaml), fulmine.js \~5.21.0 on uWebSockets.js v20.71.0 (native C++ addon), NODE_ENV=production, EXPERIMENTAL_FASTCALL=1. actix-web 4.8 baseline: Rust 1.98 (rust:1.98-slim), cargo build --release with lto=true, codegen-units=1, panic=abort (rust/Dockerfile). |
| **Adoption** | 18 stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/nigrosimone/fulmine.js) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

In the-benchmarker/web-frameworks develop-branch run of 2026-09-24 (commit f673364), with the server pinned to 4 cores of an undisclosed 16-thread x86_64 Linux host and zrk driving a closed loop over keep-alive connections, fulmine.js 5.21 (Node 26, uWS 20.71.0, cluster: 'auto', etag off, declarative request values on) averaged 223,508 / 210,337 / 203,996 req/s over three hello-world routes at 64 / 256 / 512 connections vs actix-web 4.8 (Rust 1.98, lto=true, codegen-units=1) at 179,203 / 168,270 / 163,415, i.e. 1.25x. In the same run Express 5.2 reached 42,586 req/s at c=512 (fulmine 4.8x), and the plain uWebSockets.js entry, started with the suite's language-level 'node cluster.mjs' command instead of fulmine's own cluster: 'auto', reached 174,621 req/s; the older master snapshot (commit 0fccb1d, older method) puts fulmine only 1.04x-1.09x ahead of actix.

## Use it when

- An existing Express 5 app where routing and dispatch, not the database or JSON.parse, is the bottleneck; the project's own CI (Node 26, self-reported) shows 1.2x-4.5x over Express on plain routing and 1.7x-5x on requests with a body.
- Large route tables whose paths are plain strings or whole-segment parameters (/users/:id): the docs report 7x-22x over Express at 1,000 routes, because uWS matches in C++ while Express scans every layer.
- Static or id-echo endpoints (health checks, fixed JSON) with no middleware in front and etag off, which compile to responses uWS answers with zero JavaScript per request.
- Multi-core Linux hosts or containers where you want one Node process per core on one port without a primary relaying connections (cluster: 'auto', cgroup-aware).
- Express apps that also need WebSockets served by the same native server (app.ws(), or socket.io via io.attachApp(app.uwsApp)).

## Skip it when

- As an alternative to actix-web: the 1.25x lead comes from a 3-route hello-world with fulmine-specific settings (etag off, connection headers off, declarative request values on), and actix-web still has the lower p99 latency at 64 and 256 connections in that run (0.39 vs 0.60 ms, 1.58 vs 2.38 ms).
- Alpine/musl images, Debian bookworm images (node:26 and node:26-slim ship glibc 2.36; 2.38+ is required), Bun, Node 23/25, or builds that block git dependencies: uWebSockets.js is not on npm and is fetched from GitHub with git, and pnpm 10.26+ refuses it without an override.
- Requests dominated by JSON.parse on large bodies, zlib, OpenSSL or large streams: the project's own docs cap the ratio versus Express at 1.0x-1.5x there.
- Clients that upload slower than 16 KB/s (uWS drops them, not tunable from JavaScript), headers above 4 KB without UWS_HTTP_MAX_HEADERS_SIZE, or code that needs real 1xx responses (Early Hints, 100-continue), trailers or HTTP/3 (writeEarlyHints/addTrailers are no-ops; http3 is guarded off because the pinned uWS H3App segfaults on Linux).
- Risk-averse production: one maintainer, first npm release 2026-08-03 with 58 versions in about seven weeks, 18 GitHub stars and \~3.4k npm downloads per month; minor releases may contain breaking changes, and CVE-2026-12590 (a body-parser limit that could be silently disabled) was fixed only in 5.21.3.

## How it is fast

uWebSockets.js does HTTP parsing, socket I/O and route matching in C++: routes with plain or whole-segment-parameter paths are registered on the uWS native router, and the middleware chain in front of each route is resolved once at listen(), replacing Express's per-request linear scan of the layer stack. Per-request work is lazy: the body is not read unless a handler asks, headers are not copied out of uWS unless something reads them, and no Readable/Writable stream is built unless used. A handler that only calls res.status/set/type/send/json/end with literal arguments is parsed at registration (acorn over the function source) and compiled into a uWS DeclarativeResponse that C++ answers without entering JavaScript; the opt-in 'declarative request values' setting extends this to echoing a route parameter or query value. cluster: 'auto' forks one worker per usable core (cgroup CPU quota read first), each binding the port with SO_REUSEPORT, so no primary process relays connections the way Node's built-in cluster does.

## Compared with alternatives

Pick fulmine.js only when the code is already Node/Express and a rewrite is off the table; in the same 2026-09-24 run the compiled-language siblings are in the same range at c=512 (may_minihttp 194,372, ohkami nio 181,797, httpbeast 175,501, http.zig 171,398 req/s vs fulmine 203,996), and may_minihttp matches it at c=64 (223,705 vs 223,508) with about half the p99 latency (0.32 vs 0.60 ms). For a new service in Rust, Nim or Zig, those siblings give comparable throughput without Node, the native-addon install constraints, or a seven-week-old codebase.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | uWebSockets.js v20.71.0 (native prebuilt binaries, installed from GitHub via git), acorn, fast-zlib, tseep, iconv-lite and Express's helper modules (accepts, qs, cookie, mime-types, proxy-addr, range-parser, type-is and others); optional peer @nestjs/platform-express &gt;=10 |
| **Minimum toolchain** | Node.js 22, 24 or 26 only (23 and 25 have no uWS binary); glibc 2.38+ on Linux; git available at npm install time |
| **Platforms** | Linux (glibc 2.38+, not Alpine/musl), macOS, Windows; x64 and arm64; not Bun |
| **Thread safety** | Standard Node single-threaded event loop per process; cluster: 'auto' workers are separate processes that share no memory, so in-memory caches, rate-limit counters and session stores are per worker (documented); an internal worker thread reads files (threads option, default 1). |
| **Drop-in for the baseline** | no |

## Gotchas

- The fast paths drop out silently: a route goes back to JavaScript routing if its path uses :from-:to, a \*splat or {} groups, if a later route in the same router overlaps it, or if the request uses a different letter case; a compiled response also needs no middleware in front, literal arguments only, and etag off. Check with npx fulmine.js profile and pin it in CI with express.testing.expectNative / expectDeclarative.
- 'declarative request values' (used by the benchmark app) writes route parameters undecoded, so a malformed percent-encoding gets no 400 and a repeated query key gives its first value, not an array; compiled routes also answer Connection: keep-alive to a client that sent Connection: close, and param echoes go out chunked.
- Requests with untrustworthy framing (duplicate Content-Length, a Transfer-Encoding not ending in chunked, unknown or lowercase methods) are refused by closing the connection with no 400, as a request-smuggling guard over uWS's permissive parser.
- http.createServer(app) works but runs through node:http at Express speed; app.listen() returns the app (which passes instanceof http.Server) but no 'connection'/'request'/'upgrade' events fire, and idle timeouts are set through uwsOptions.idleTimeout.

## Known shortcomings

- The benchmark app uses non-default settings: etag and connection headers off, and 'declarative request values' compiles /user/:id into a response uWS answers without running JS (writing the parameter undecoded); the project's own #9 admits its CI benchmark measures a non-default path. It beats raw uWebSockets.js partly because the suites launch them differently (own cluster vs generic cluster.mjs). actix has lower p99 at c=64 and c=256. A Node framework compared with Rust actix: it replaces Express (\~4.8x in the same run), not actix; the older snapshot shows only 1.04-1.09x. Very young (first npm release 2026-08-03, 58 versions, one maintainer, 18 stars); versions track Express rather than semver; CVE-2026-12590 (body-parser limit silently disabled) fixed only in 5.21.3 while the benchmark pins \~5.21.0. Needs glibc 2.38+ (no Alpine/bookworm), uWebSockets.js fetched from GitHub (not npm), Node 22/24/26 only; uWS drops uploads slower than 16 KB/s; no 1xx, trailers or HTTP/3.

## Caveats and trade-offs

Low-star project (18 stars). fulmine.js is an Express-5-compatible layer over uWebSockets.js, whose C++ core does the HTTP work; the plain uwebsockets entry in the same run scores 174,621 req/s at c=512. The benchmark app turns on fulmine-specific options: 'declarative request values' lets the /user/:id route be answered by uWS in C++ without entering JavaScript, and etag and connection headers are off. Single synthetic hello-world workload. The suite changed load generator and model in 2026, and its README says results from different revisions are not comparable. The earlier snapshot still on master (commit 0fccb1d, 2026-09-20) gives different ratios, see claimed_speedup. There the lead over actix is only 4-9%. The suite's saturation probe reports identical values (0.995/0.992/0.988) for every framework checked, so it may not be a per-framework measure. Hardware metadata is inconsistent ('M1 Eight-Core Processor' on x86_64).

Very low adoption (18 stars, apparently single-maintainer); minimal Node.js HTTP framework, production-readiness unclear

## Maintenance

Actively developed (5.21.5 released 2026-09-23, 58 npm versions since 2026-08-03) but single-maintainer and very young; Apache-2.0 and installable from npm, with the major version tracking Express rather than semver, so pin the minor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks, 7.1k stars) runs fulmine.js and actix in one run with public code (javascript/fulmine.js/app.mjs, javascript/fulmine.js/config.yaml, javascript/config.yaml, rust/actix, rust/Dockerfile). Not A: there is no real CPU model, because the cpu_name is a hardcoded string in .tasks/db.rake.
- **Verifier notes:** The record's numbers match data.json on the default develop branch (commit f673364), not the master URL cited, so benchmark_url is pinned to that commit. The load model is corrected from oha without keep-alive to zrk --closed over keep-alive. Metadata verified: Apache-2.0, 18 stars, last commit 2026-09-23, not a fork, not archived.
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
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/fulmine.js/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/fulmine.js/app.mjs>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/fulmine.js/package.json>
  - <https://github.com/nigrosimone/fulmine.js>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/README.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/package.json>
- **Sources the enricher read:**
  - <https://github.com/nigrosimone/fulmine.js>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/README.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/package.json>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/docs/why.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/docs/performance.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/docs/differences.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/docs/compare.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/docs/deployment.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/docs/compatibility.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/docs/attribution.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/CHANGELOG.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/SECURITY.md>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/src/index.js>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/src/declarative.js>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/src/application.js>
  - <https://github.com/nigrosimone/fulmine.js/blob/main/src/cluster.js>
  - <https://github.com/nigrosimone/fulmine.js/issues?q=is%3Aissue>
  - <https://github.com/nigrosimone/fulmine.js/issues/6>
  - <https://github.com/nigrosimone/fulmine.js/issues/7>
  - <https://github.com/nigrosimone/fulmine.js/issues/9>
  - <https://github.com/nigrosimone/fulmine.js/issues/10>
  - <https://github.com/nigrosimone/fulmine.js/issues/11>
  - <https://github.com/nigrosimone/fulmine.js/issues/12>
  - <https://registry.npmjs.org/fulmine.js>
  - <https://api.npmjs.org/downloads/point/last-month/fulmine.js>
  - <https://api.npmjs.org/downloads/point/last-month/ultimate-express>
  - <https://hn.algolia.com/api/v1/search?query=fulmine.js&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=fulmine%20express>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/fulmine.js/app.mjs>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/fulmine.js/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/fulmine.js/package.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets/app.mjs>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/ultimate-express/app.mjs>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/ultimate-express/config.yaml>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/nigrosimone/fulmine.js`) · [data/wave5/enrich/raw/github_com_nigrosimone_fulmine_js.json](../../../data/wave5/enrich/raw/github_com_nigrosimone_fulmine_js.json) (enrichment confidence 0.4)

</details>
