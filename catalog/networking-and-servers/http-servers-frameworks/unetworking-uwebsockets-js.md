# uWebSockets.js

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `JavaScript (Node.js bindings over a C++ core)` · `Apache-2.0` · 🟢 active

> Node.js addon running the uWebSockets C++ server behind JS callbacks; 2.6x Fastify, about 1.06x actix-web on hello-world.

| | |
|---|---|
| **Beats** | actix-web |
| **Claimed result** | the-benchmarker/web-frameworks data.json, develop commit f673364 (2026-09-24): uwebsockets (uWebSockets.js v20.71.0) 189,157 / 178,265 / 174,621 req/s at concurrency 64 / 256 / 512 vs actix (actix-web 4.8) 179,203 / 168,270 / 163,415 req/s, i.e. 1.06x / 1.06x / 1.07x (derived from page data). The older-method snapshot on master (commit 0fccb1d, 2026-09-20) shows parity: 120,152 / 102,932 / 99,147 vs 115,638 / 102,329 / 99,835 req/s, i.e. 1.04x / 1.01x / 0.99x (derived from page data). |
| **Workload** | the-benchmarker/web-frameworks develop-branch run of 2026-09-24 (commit f673364): zrk --closed, a closed loop over keep-alive connections (not wrk), 15 s per concurrency level 64/256/512; the framework container is pinned to cores 0-3 and the load generator to cores 4-15 (.env). Each headline req/s is avg() over the three routes in .env (GET / with empty body, GET /user/0 echoing the id, POST /user with empty body) per .tasks/db.rake, so it is not a single plaintext route. All handlers are hello-world. uWebSockets.js runs as a Node cluster (one worker per available core) with ordinary JS callbacks in this run. |
| **Metric** | throughput |
| **Hardware** | Undisclosed x86_64 Linux host (Fedora 44 kernel 7.2.6-200.fc44.x86_64), 16 logical CPUs. The cpu_name 'M1 Eight-Core Processor' (and the memory figure) in data.json are strings hard-coded in .tasks/db.rake, not measured. Server pinned to cores 0-3 (it kept \~3.95 cores busy at \~98.7% saturation per data.json), load generator to cores 4-15. |
| **Compiler and flags** | uWebSockets.js v20.71.0 prebuilt V8 addon installed from GitHub, Node.js 26 (node:26-slim), NODE_ENV=production, EXPERIMENTAL_FASTCALL=1, node cluster.mjs; addon compiler flags not stated. Baseline actix-web 4.8: Rust 1.98 (rust:1.98-slim), cargo build --release with opt-level=3, lto=true, codegen-units=1, panic=abort (rust/actix/Cargo.toml, rust/Dockerfile). |
| **Adoption** | 9,161 stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/uNetworking/uWebSockets.js) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

In the-benchmarker/web-frameworks run of 2026-09-24 (zrk closed loop, hello-world GET/GET-param/POST routes averaged, server pinned to 4 cores of an undisclosed 16-thread x86-64 Linux host), uWebSockets.js v20.71.0 on Node 26 as a one-worker-per-core cluster with plain JS callbacks did 189,157 / 178,265 / 174,621 req/s at c=64/256/512 against 179,203 / 168,270 / 163,415 for actix-web 4.8 (Rust 1.98, LTO, codegen-units=1), 1.06-1.07x. Other snapshots gave 0.99-1.04x and 1.33-1.42x, so read it as parity with actix and roughly 2.6x Fastify and 4.1x Express in the same run; the README's '13x faster than Fastify' compares the author's microcached endpoint with an uncached Fastify hello-world.

## Use it when

- Node.js 22/24/26 services that must stay on Node and are bound by HTTP or WebSocket I/O: in the same 2026-09-24 run it did 174,621 req/s at c=512 against 68,128 for Fastify and 42,586 for Express on the same 4 cores.
- WebSocket fan-out such as chat, game or market-data servers that need pub/sub, per-socket backpressure limits (maxBackpressure, closeOnBackpressureLimit, drain) and permessage-deflate options without extra packages.
- Hot endpoints with static or templated answers (DeclarativeResponse), or idempotent 'dynamic but public' GET endpoints that tolerate brief staleness (experimental microcache; wired only for non-TLS App GET routes, expiry units not documented).
- Teams that accept a low-level, callback-first API and will put their own routing and middleware conventions on top.

## Skip it when

- C++ programs: use the uWebSockets core directly. This repository adds only the V8 glue (src/addon.cpp and the \*Wrapper.h files) on top of it.
- Apps that need the Express/Connect middleware ecosystem, a fetch-style Request that survives await, or streams-based node:http compatibility. Ultimate Express or fulmine.js give that API on the same core.
- Bun users or peak-JS-throughput chasers: the maintainer says Bun (built on a uWS fork) now beats this addon 'by a wide margin' on WebSocket echo, because every C++-to-JS call must go through node::MakeCallback (issue #1288).
- Alpine/musl, Deno, Node versions other than 22/24/26, or 32-bit targets: only prebuilt glibc Linux x64/arm64, macOS x64/arm64 and Windows x64 binaries exist, one per Node ABI (127/137/147).
- Organisations that require npm-registry packages, provenance, or a plain OSS licence: it installs from GitHub tags only, and the README says 'all rights reserved' except where an Apache-2.0 notice is given.

## How it is fast

HTTP parsing, routing, TLS (BoringSSL), WebSocket framing and compression run in the uWebSockets C++ core, driven by Node's own libuv loop (built with LIBUS_USE_LIBUV, attached via node::GetCurrentEventLoop) and compiled with clang -O3 -flto. The binding keeps its own overhead small: req/res are clones of pre-built V8 object templates holding a raw pointer, incoming data arrives as zero-copy ArrayBuffers detached after the callback, and the synchronous part of each handler runs corked so its writes leave in one syscall. Two paths skip JS entirely: DeclarativeResponse compiles a response into opcodes that C++ replays per request, and v20.71.0 added experimental per-route microcaching with coalesced refreshes. What the binding costs is the C++-to-JS crossing: every handler call goes through node::MakeCallback, which the maintainer names as the main bottleneck (issues #1209, #1288).

## Compared with alternatives

Pick the raw binding over Ultimate Express or fulmine.js (Express-compatible layers on the same core) when you write to uWS's own API and need its WebSocket pub/sub and backpressure control; it is not automatically faster, since fulmine.js, which answers simple handlers without running JS, scored 203,996 req/s against this binding's 174,621 at c=512 in the same run. If you can leave Node, Elysia on Bun (173,877 req/s) runs a uWS fork without the MakeCallback toll.

## Integration

| | |
|---|---|
| **Form** | module (prebuilt native .node addon plus uws.js loader, installed with npm from a GitHub tag; not on the npm registry) |
| **Dependencies** | none at runtime; the prebuilt binary statically bundles the uWebSockets/uSockets core, BoringSSL and lsquic (HTTP/3) |
| **Minimum toolchain** | Node.js 22, 24 or 26 (v8 ABI 127/137/147); rebuilding from source needs clang-18 on Linux (clang on macOS/Windows), CMake, and C++20 |
| **Platforms** | glibc Linux x86-64 and aarch64, macOS x86-64 and arm64 (macOS 12 target), Windows x86-64; not musl |
| **Thread safety** | Each Node worker thread or cluster process creates its own App on its own event loop. Multi-core scaling uses SO_REUSEPORT listening (Linux) or an acceptor App that round-robins sockets to child apps via addChildAppDescriptor. Sharing App/res/ws objects across threads is not documented. The built-in KV store (getString/setString and friends) is process-global and guarded only by explicit lock()/unlock(). |
| **Drop-in for the baseline** | no |

## Gotchas

- A handler that returns without responding and without calling res.onAborted() makes the C++ core call std::terminate(); the process dies and process.on('uncaughtException') never fires (issue #1296). ASAN builds in the binaries-asan branch help locate such crashes.
- req is unusable after the first await or after the handler returns, and res is unusable after end() or abort; both throw. onData/onDataV2 chunks and WebSocket message ArrayBuffers are detached after the callback, so copy them if you keep them.
- Writes made after an await or from timers/DB callbacks must be wrapped in res.cork(); otherwise the addon prints a warning on each write and loses the one-syscall batching.
- Performance tweaks have regressed before: v20.62.0 disabled the WebSocket.send V8 fast call after reports of broken apps, and the v20.63.0 string fast path sent Latin-1 bytes instead of UTF-8 until v20.65.0 reverted it. The ESM wrapper is hard-coded (open issue #1314), and the benchmark suite loaded 20.71.0 through CommonJS to avoid it.

## Known shortcomings

- Results swing between runs of the same suite: 1.06-1.07x over actix on 2026-09-24, parity (0.99-1.04x) on 09-20, 1.33-1.42x on 09-18. Not on the npm registry (installs from GitHub tags). After this run the suite's app switched to a mode that answers in C++ without JavaScript (PR #9828), so later numbers aren't like-for-like. Distinct from the catalogued uWebSockets C++ core (own binding code and own actix comparison).
- Not an N-API binding: a raw V8/node.h addon with one prebuilt binary per Node ABI (Node 22/24/26 only; glibc Linux x64/arm64, macOS, Windows x64; no musl). Every C++-to-JS handler call goes through node::MakeCallback, which the maintainer names as the bottleneck (#1209, #1288); he says Bun's uWS fork now beats the addon 'by a wide margin' on WebSocket echo. The benchmark's EXPERIMENTAL_FASTCALL=1 flag is read nowhere (the send fast call has been disabled since v20.62.0). The actix lead is within run-to-run spread; the meaningful same-run result is \~2.6x Fastify and \~4.1x Express at c=512; fulmine.js (built on it) beat the raw binding. The README's '13x faster than Fastify' compares a microcached endpoint with uncached Fastify. A handler that returns without responding or onAborted() calls std::terminate() (uncatchable, #1296). v20.63.0 sent Latin-1 instead of UTF-8 until v20.65.0; the ESM wrapper is hard-coded (#1314). Licence: 'all rights reserved' with Apache-2.0 only where noticed; forks must rename.

## Caveats and trade-offs

Node.js V8-addon binding over the already-catalogued uWebSockets C++ core (git submodule); its speed is uWebSockets', so C++ users should use uWebSockets directly. Distinct repo, but not published to the npm registry (installed from GitHub tags). The 2026-09-24 run used plain JS callbacks; the suite switched its app to DeclarativeResponse (answered in C++) after that run (PR #9828), so later numbers are not like-for-like. Run-to-run variation is large: 1.06-1.07x on 2026-09-24, 0.99-1.04x (parity) in the superseded-method 2026-09-20 snapshot, 1.33-1.42x on 2026-09-18 (commit 8ae370a). README says Apache-2.0 applies where explicit notice is given. Single hello-world workload; hardware metadata hard-coded.

Thin Node.js/N-API binding around the already-catalogued uWebSockets C++ core; performance credit largely belongs to that core rather than to JS-specific code.

## Maintenance

Actively maintained by its original author (uWS dates from 2016, this binding from 2018; v20.71.0 released 2026-09-16, last push 2026-09-20). It ships only as GitHub-hosted prebuilt binaries tied to three Node majors, under an 'all rights reserved, Apache-2.0 where noticed' licence statement, and the maintainer has said the Node binding will eventually 'fade into the background' in favour of Bun.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks) runs uWebSockets.js and actix in one run with public code (javascript/uwebsockets/app.mjs, cluster.mjs, package.json, javascript/config.yaml, rust/actix, rust/Dockerfile); 1.06-1.07x at all three concurrencies in the 2026-09-24 run. Not A: no real CPU model (cpu_name hard-coded) and no compiler flags for the prebuilt addon.
- **Verifier notes:** Judged a distinct entry, not a known-project duplicate: separate repo and package with its own binding code (src/addon.cpp, \*Wrapper.h) and its own independent evidence vs actix, consistent with how bindings such as zsv-ruby and aws-lc-rs were kept; the known_list line for uwebsockets.js comes from this record's wave-5 merge. GitHub reports C++ as the primary language (JS is \~3 KB). Metadata verified: Apache-2.0, 9,161 stars, last commit 2026-09-20, not a fork, not archived.
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
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets/package.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets/app.mjs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets/cluster.mjs>
  - <https://github.com/the-benchmarker/web-frameworks/commit/cb8ab6f.patch>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/dd442171b7b92a71d9a23148ea12741599396f5c/javascript/uwebsockets/app.mjs>
  - <https://github.com/uNetworking/uWebSockets.js>
  - <https://raw.githubusercontent.com/uNetworking/uWebSockets.js/master/README.md>
  - <https://raw.githubusercontent.com/uNetworking/uWebSockets.js/master/.gitmodules>
  - <https://github.com/uNetworking/uWebSockets>
- **Sources the enricher read:**
  - <https://github.com/uNetworking/uWebSockets.js>
  - <https://raw.githubusercontent.com/uNetworking/uWebSockets.js/master/README.md>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/src/addon.cpp>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/src/uws.js>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/src/AppWrapper.h>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/src/HttpResponseWrapper.h>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/src/HttpRequestWrapper.h>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/src/WebSocketWrapper.h>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/src/Utilities.h>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/src/FastTimers.h>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/src/host.cpp>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/build.c>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/Makefile>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/.github/workflows/build.yml>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/.github/workflows/build-asan.yml>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/.gitmodules>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/LICENSE>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/misc/npm.md>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/docs/index.d.ts>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/examples/WorkerThreads.mjs>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/examples/AsyncFunction.mjs>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/examples/Backpressure.mjs>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/examples/HelloWorld.mjs>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/examples/Router.mjs>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/examples/H3lloWorld.mjs>
  - <https://github.com/uNetworking/uWebSockets.js/blob/master/examples/HttpCache.mjs>
  - <https://github.com/uNetworking/uWebSockets.js/tree/binaries>
  - <https://github.com/uNetworking/uWebSockets.js/blob/binaries/package.json>
  - <https://github.com/uNetworking/uWebSockets.js/blob/binaries/ESM_wrapper.mjs>
  - <https://github.com/uNetworking/uWebSockets.js/blob/binaries/source_commit>
  - <https://github.com/uNetworking/uWebSockets.js/releases/tag/v20.71.0>
  - <https://github.com/uNetworking/uWebSockets.js/releases/tag/v20.65.0>
  - <https://github.com/uNetworking/uWebSockets.js/releases/tag/v20.63.0>
  - <https://github.com/uNetworking/uWebSockets.js/releases/tag/v20.62.0>
  - <https://github.com/uNetworking/uWebSockets.js/releases/tag/v20.61.0>
  - <https://github.com/uNetworking/uWebSockets.js/releases>
  - <https://github.com/uNetworking/uWebSockets.js/issues/1296>
  - <https://github.com/uNetworking/uWebSockets.js/issues/1200>
  - <https://github.com/uNetworking/uWebSockets.js/issues/1209>
  - <https://github.com/uNetworking/uWebSockets.js/issues/1288>
  - <https://github.com/uNetworking/uWebSockets.js/issues/1054>
  - <https://github.com/uNetworking/uWebSockets.js/issues/1146>
  - <https://github.com/uNetworking/uWebSockets.js/issues/1036>
  - <https://github.com/uNetworking/uWebSockets.js/issues/1314>
  - <https://github.com/uNetworking/uWebSockets.js/issues?q=segfault>
  - <https://github.com/uNetworking/uWebSockets.js/issues?q=crash>
  - <https://github.com/uNetworking/uWebSockets.js/issues?q=memory+leak>
  - <https://github.com/uNetworking/uWebSockets.js/issues?q=performance>
  - <https://github.com/uNetworking/uWebSockets.js/issues?q=slower>
  - <https://github.com/uNetworking/uWebSockets.js/issues?q=bun>
  - <https://github.com/uNetworking/uWebSockets.js/issues?q=ESM>
  - <https://raw.githubusercontent.com/uNetworking/uSockets/master/src/bsd.c>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets/app.mjs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets/cluster.mjs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets/package.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/javascript/uwebsockets.Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/pull/9828>
  - <https://github.com/nigrosimone/fulmine.js>
  - <https://hn.algolia.com/api/v1/search?query=uWebSockets.js&tags=story&hitsPerPage=15>
  - <https://hn.algolia.com/api/v1/search?query=uws%20npm%20deprecated&hitsPerPage=10>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/unetworking/uwebsockets.js`) · [data/wave5/enrich/raw/github_com_unetworking_uwebsockets_js.json](../../../data/wave5/enrich/raw/github_com_unetworking_uwebsockets_js.json) (enrichment confidence 0.5)

</details>
