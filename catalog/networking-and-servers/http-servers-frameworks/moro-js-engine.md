# MoroJS engine (@morojs/engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++ (Node.js native addon via raw V8 bindings)` · `MIT` · 🟢 active

> C++ HTTP/1.1 and WebSocket server addon for Node.js, the engine under MoroJS; beat actix-web 1.11-1.14x on a hello-world shootout.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | the-benchmarker/web-frameworks data.json, develop commit f673364 (2026-09-24): morojs-engine 203,452 / 187,047 / 182,455 req/s at concurrency 64 / 256 / 512 vs actix (actix-web 4.8) 179,203 / 168,270 / 163,415 req/s, i.e. 1.14x / 1.11x / 1.12x (derived from page data). The older-method snapshot on master (commit 0fccb1d, 2026-09-20) shows 121,566 / 104,991 / 103,522 vs 115,638 / 102,329 / 99,835 req/s, i.e. 1.05x / 1.03x / 1.04x (derived from page data). |
| **Workload** | the-benchmarker/web-frameworks develop-branch run of 2026-09-24 (commit f673364): zrk --closed, a closed loop over keep-alive connections (not wrk), 15 s per concurrency level 64/256/512; the framework container is pinned to cores 0-3 and the load generator to cores 4-15 (.env). Each headline req/s is avg() over the three routes in .env (GET / with empty body, GET /user/0 echoing the id, POST /user with empty body) per .tasks/db.rake, so it is not a single plaintext route. All handlers are hello-world. morojs-engine runs as a Node cluster (one worker per available core, SO_REUSEPORT). |
| **Metric** | throughput |
| **Hardware** | Undisclosed x86_64 Linux host (Fedora 44 kernel 7.2.6-200.fc44.x86_64), 16 logical CPUs. The cpu_name 'M1 Eight-Core Processor' (and the memory figure) in data.json are strings hard-coded in .tasks/db.rake, not measured. Server pinned to cores 0-3 (it kept \~3.95 cores busy at \~98.7% saturation per data.json), load generator to cores 4-15. |
| **Compiler and flags** | @morojs/engine ^1.1.6 prebuilt native addon (README: C++ core with raw V8 bindings; release binaries PGO-trained with clang, exact flags not stated) on Node.js 26 (node:26-slim), NODE_ENV=production, node cluster.mjs. Baseline actix-web 4.8: Rust 1.98 (rust:1.98-slim), cargo build --release with opt-level=3, lto=true, codegen-units=1, panic=abort (rust/actix/Cargo.toml, rust/Dockerfile). |
| **Adoption** | 0 stars (repo created 2026-07-09); 723 npm downloads of @morojs/engine in the 30 days to 2026-09-25 |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/Moro-JS/engine) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

the-benchmarker/web-frameworks run of 2026-09-24 (develop f673364): zrk closed loop over keep-alive connections, 15 s per level, with each figure averaged over GET /, GET /user/0 and POST /user. The server was pinned to 4 cores of an undisclosed 16-thread x86_64 Linux host (the CPU name in the data is hard-coded). The raw engine as a Node 26 cluster (^1.1.6, most likely 1.1.7 because the run predates the 1.1.9 publish) did 203,452 / 187,047 / 182,455 req/s at c=64/256/512 against actix-web 4.8 (Rust 1.98, opt-level 3, LTO, codegen-units=1) at 179,203 / 168,270 / 163,415, or 1.14x / 1.11x / 1.12x with both about 99% CPU-saturated. The older-method 2026-09-20 snapshot showed only 1.03-1.05x, and the engine's author submitted the benchmark entry (PR #9801).

## Use it when

- You already run MoroJS on Node 20-26: this is its default engine, with automatic node:http fallback on unsupported platforms or ABIs.
- Node.js HTTP/1.1 services where transport overhead dominates and many responses are fixed or echo one path segment, so static routes, parameter routes and prepared templates can answer without entering JS.
- Pipelined HTTP/1.1 clients: the author's run (Apple M2 Ultra, wrk -c100, pipelined x10) shows raw engine 832,171 req/s vs raw uWebSockets.js 652,934; without pipelining the two were 108,446 vs 106,287.
- You want native HTTPS/WSS termination plus WebSocket with permessage-deflate in one MIT npm package, with prebuilt binaries for glibc, musl, macOS and Windows x64.
- Linux 6.1+ hosts with heavy keep-alive load where you can A/B the opt-in io_uring transport (MORO_ENGINE_TRANSPORT=uring).

## Skip it when

- Choosing a stack on this number alone: the win over actix-web comes from hello-world handlers where GET / and POST /user are engine static routes that never run JS. No data covers handlers that do real work in JS.
- Tail-latency-sensitive services at low or medium concurrency: in the same run p99 was 0.72 ms vs actix 0.39 ms at c=64 and 2.42 vs 1.58 ms at c=256. It was lower only at c=512 (3.05 vs 3.22 ms).
- You need HTTP/2, HTTP/3, multi-certificate SNI or OCSP stapling. The engine is HTTP/1.1 only; ALPN HTTP/2 is listed as in progress.
- Direct internet exposure of the TLS and HTTP parsers without a proxy: no external security audit has been done, and THREAT_MODEL.md says to front it with a proxy or review it first. maxConnections defaults to unlimited.
- Risk-averse production use: repo created 2026-07-09, one npm maintainer, 0 stars, 0 issues filed, 723 npm downloads in 30 days, nine releases in 11 weeks. Also not for streaming large uploads: request bodies are buffered in full before onRequest (10 MB default cap).

## How it is fast

A batched boundary: one JS crossing delivers method index and path, and one corked call sends status, headers and body (the design doc says 2-4 crossings per request against about 10-20 for a general binding), with V8 Fast API call targets on the hot response functions. Fixed replies can skip JS entirely: setStaticRoute and (since 1.1.9) setParamRoute answer inside C++, and prepareResponse builds a header block once for reuse on each request. The warm path avoids allocation (reused per-connection scratch buffers and header strings, a Date header cached once per second, uv_try_write with no write-request allocation, one write for each pipelined batch), multi-core runs as SO_REUSEPORT workers, and release binaries are built with clang -O3 -flto plus PGO. The parser is a scalar, table-driven RFC 9112 parser: the source has no SIMD intrinsics, although DESIGN.md calls it 'SIMD-friendly'.

## Compared with alternatives

In the same 2026-09-24 run, uWebSockets.js (189,157 / 178,265 / 174,621 req/s) was 4-8% behind, fulmine.js (223,508 / 210,337 / 203,996) was 10-12% ahead and Ultimate Express (179,836 / 170,080 / 165,795) was about 10% behind. Pick this engine when you use MoroJS or want its id-based native API with in-process TLS and automatic node:http fallback. Pick fulmine.js for the top raw number, or Ultimate Express if you need Express API compatibility.

## Integration

| | |
|---|---|
| **Form** | module (npm meta package @morojs/engine with prebuilt .node binaries in per-platform optional packages, one for each Node ABI; source build via tools/build.mjs) |
| **Dependencies** | none at runtime beyond the per-platform binary package; links the libuv, OpenSSL and zlib inside the host Node binary. Source builds fetch Node headers and a sha-pinned v8-fast-api-calls.h. |
| **Minimum toolchain** | Node.js &gt;= 20 (ABIs 115/127/131/137/141/147 = Node 20/22/23/24/25/26). Source builds: C++20; the release lane uses clang-18 + lld for LTO/PGO, MSVC /std:c++20 on Windows. Minimum compiler version not documented. |
| **Platforms** | darwin arm64/x64, linux x64/arm64 (glibc and musl), win32 x64. Release x64 binaries target -march=x86-64-v2 (SSE4.2/POPCNT) and arm64 targets armv8.2-a. The io_uring transport needs Linux 6.1+ and is opt-in. SO_REUSEPORT is POSIX-only (ignored on Windows). |
| **Thread safety** | Single-threaded per event loop: each thread (main or worker_threads) runs its own servers, request/WebSocket ids never cross threads, and there are no locks. For multi-core, run one engine per worker thread or process with reusePort. |
| **Drop-in for the baseline** | no |

## Gotchas

- Before 1.1.7, callbacks ran outside a Node callback scope. A response sent from a promise continuation could stall for 5-29 s, and under load none such completed. Use &gt;= 1.1.7 and check probe().capabilities.callbackScope.
- V8 Fast API targets install only when the running V8 major.minor matches the one the binary was built against. They apply only to Smi ids and sequential one-byte string bodies. Otherwise calls silently take the slower regular path; probe().fastApi reports why.
- Static and parameter routes run no JS, so no middleware, logging or auth runs for them. Only an exact method match short-circuits (HEAD against a GET route reaches JS). A parameter segment is sent undecoded ('a%20b' stays 'a%20b').
- The io_uring transport falls back to libuv silently under Docker's default seccomp profile, gVisor or kernels before 6.1. The default is still libuv because io_uring used more CPU per request in small-batch cases; check probe().transport.

## Known shortcomings

- The benchmark app answers GET / and POST /user entirely inside the C++ engine as static routes, so only /user/:id reaches JavaScript: tuned for the benchmark. Brand new (0 stars, \~723 npm downloads/month).
- The engine's author submitted its benchmark entry (the-benchmarker PR #9801, 2026-09-16) and the suite's CPU-saturation tasks (#9662); the 1.1.9 release note targets 'the benchmark shape every harness runs'. The engine version isn't pinned (^1.1.6; most likely 1.1.7 was tested). p99 is worse than actix at c=64 (0.72 vs 0.39 ms) and c=256 (2.42 vs 1.58 ms). Margin is 1.11-1.14x on 2026-09-24 but 1.03-1.05x on 09-20; fulmine.js was 10-12% faster in the same run. Created 2026-07-09, nine releases in 11 weeks, no external audit; THREAT_MODEL.md says to put a proxy in front of its TLS; maxConnections unlimited by default. Docs claim a 'SIMD-friendly' parser (it's scalar) and disagree on BoringSSL vs Node's OpenSSL. Before 1.1.7 promise-continuation responses could stall 5-29 s. V8 fast calls silently turn off on V8 mismatch and io_uring falls back to libuv under Docker's default seccomp (probe() reports both). Release flags: -std=c++20 -O3 -flto, clang PGO, -fno-exceptions -fno-rtti, -march=x86-64-v2/armv8.2-a.

## Caveats and trade-offs

Brand-new, 0 stars; mainly the engine behind the MoroJS framework. The shootout app registers GET / and POST /user as engine static routes, answered in C++ without entering JavaScript (a documented engine feature, but benchmark-tuned); only /user/:id reaches JS. Margin over actix is 1.11-1.14x in the 2026-09-24 run but only 1.03-1.05x in the superseded-method 2026-09-20 snapshot, and the suite says revisions are not comparable. Single synthetic hello-world workload. Hardware metadata is inconsistent ('M1 Eight-Core Processor' on x86_64, hard-coded).

Very new (created \~2.5 months before this search), single-maintainer project; also has its own first-party benchmark repo (github.com/Moro-JS/benchmark) comparing against node:http/Express/Fastify/Koa/Hono/Bun, but that repo does not include actix-web or nginx as baselines.

## Maintenance

Active: 1.1.9 released 2026-09-24, 45 commits since the repo was created on 2026-07-09. MIT, installable from npm with prebuilt binaries, but young, single-maintainer and not externally audited.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks) runs morojs-engine and actix in one run with public code (javascript/morojs-engine/app.mjs, cluster.mjs, package.json, javascript/config.yaml, rust/actix, rust/Dockerfile); faster at all three concurrencies in the 2026-09-24 run and in the older 2026-09-20 snapshot. Not A: no real CPU model (cpu_name hard-coded) and the engine's own compiler flags are unstated.
- **Verifier notes:** Numbers match the 'morojs-engine' row (id 1477, website Moro-JS/engine); it ranks 4th of 387 at c=512 vs actix 20th. benchmark_url pinned to commit f673364 and workload corrected from wrk/plaintext to zrk --closed with a 3-route average. Metadata verified: MIT, 0 stars, last commit 2026-09-24, not a fork, not archived.
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
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/node.Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets.Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/rust/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/morojs-engine/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/morojs-engine/package.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/morojs-engine/app.mjs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/morojs-engine/cluster.mjs>
  - <https://github.com/Moro-JS/engine>
  - <https://raw.githubusercontent.com/Moro-JS/engine/main/README.md>
  - <https://registry.npmjs.org/@morojs%2Fengine>
  - <https://api.npmjs.org/downloads/point/last-month/@morojs%2Fengine>
- **Sources the enricher read:**
  - <https://github.com/Moro-JS/engine>
  - <https://github.com/Moro-JS/engine/blob/main/README.md>
  - <https://github.com/Moro-JS/engine/blob/main/docs/DESIGN.md>
  - <https://github.com/Moro-JS/engine/blob/main/docs/API.md>
  - <https://github.com/Moro-JS/engine/blob/main/docs/ROADMAP.md>
  - <https://github.com/Moro-JS/engine/blob/main/docs/THREAT_MODEL.md>
  - <https://github.com/Moro-JS/engine/blob/main/packages/engine/README.md>
  - <https://github.com/Moro-JS/engine/blob/main/packages/engine/package.json>
  - <https://github.com/Moro-JS/engine/blob/main/v1.1.7.md>
  - <https://github.com/Moro-JS/engine/blob/main/v1.1.8.md>
  - <https://github.com/Moro-JS/engine/blob/main/v1.1.9.md>
  - <https://github.com/Moro-JS/engine/blob/main/tools/build.mjs>
  - <https://github.com/Moro-JS/engine/blob/main/.github/workflows/release.yml>
  - <https://github.com/Moro-JS/engine/blob/main/src/http_parser.h>
  - <https://github.com/Moro-JS/engine/blob/main/src/server.h>
  - <https://github.com/Moro-JS/engine/blob/main/src/response_template.h>
  - <https://github.com/Moro-JS/benchmark>
  - <https://github.com/the-benchmarker/web-frameworks/pull/9801>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/morojs-engine/app.mjs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/morojs-engine/cluster.mjs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/morojs-engine/package.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/morojs-engine/config.yaml>
  - <https://registry.npmjs.org/@morojs%2Fengine>
  - <https://registry.npmjs.org/@morojs%2Fengine-win32-x64>
  - <https://api.npmjs.org/downloads/point/last-month/@morojs%2Fengine>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/moro-js/engine`) · [data/wave5/enrich/raw/github_com_moro_js_engine.json](../../../data/wave5/enrich/raw/github_com_moro_js_engine.json) (enrichment confidence 0.4)

</details>
