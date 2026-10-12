# khttp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟡 stale

> Synchronous Rust HTTP/1.1 micro-framework (memchr and libc only) with an epoll dispatcher; 1.12-1.22x Drogon on the-benchmarker's trivial routes.

| | |
|---|---|
| **Beats** | Drogon 1.9.13 (C++, trantor event loop; the-benchmarker cpp/drogon, cmake release build); also agoo-c 0.7 (C) in the same table |
| **Claimed result** | khttp 0.2 (epoll feature) in data.json updated 2026-10-06: 215,714 / 199,813 / 197,117 req/s at 64 / 256 / 512 connections vs Drogon 177,005 / 178,341 / 171,358 (1.22x / 1.12x / 1.15x, derived from page data); vs agoo-c (C) 1.50x at 64, 0.93x at 256, 0.98x at 512, and vs cwist 3.9 (C, best C row at 64, 186,252) 1.16x (derived from page data). Per busy server core: khttp 87.5k / 83.7k / 84.3k vs Drogon 69.9k / 71.8k / 69.3k req/s (derived from total_requests_per_s / server_cpu_cores). The 2026-10-02 snapshot (commit 8657397) repeats 1.19x / 1.12x / 1.14x, and in the 2026-09-24 snapshot (commit f673364), where both servers were CPU-bound (khttp 93-94%, Drogon 99% of 4 CPUs), khttp 149,536 / 153,180 / 152,315 vs Drogon 126,432 / 134,984 / 131,608 req/s (1.18x / 1.13x / 1.16x, derived from page data). |
| **Workload** | the-benchmarker/web-frameworks minimal HTTP contract (GET /, GET /user/:id, POST /user on port 3000), total_requests_per_s at 64, 256 and 512 connections, each framework in its own container. |
| **Metric** | throughput |
| **Hardware** | data.json hardware field (published 2026-10-06): cpu_name 'M1 Eight-Core Processor', cpus 16, memory 7,733,008 kB, Linux 7.2.7-200.fc44.x86_64 (Fedora). Per-run server_cpu_cores / server_cpu_saturation imply about 4 CPUs allotted to each server container (derived from page data). |
| **Compiler and flags** | Cargo release profile: opt-level 3, codegen-units 1, panic = 'abort', lto = true, overflow-checks = false; khttp 0.2 with feature epoll; Rust 1.98 (rust/config.yaml). Drogon 1.9.13: cmake -DCMAKE_BUILD_TYPE=release (CMake release flags), C++17, no LTO; no C++ compiler version pinned in the suite files read; config.json threads_num 0 (auto), log level WARN, Server and Date headers disabled. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | no |
| **Why it wins** | Minimal dependencies and a custom epoll event loop (README feature list); no mechanism for the margin over Drogon is stated. |
| **Adoption** | 40 stars, 1 fork; khttp crate 4,660 downloads (crates.io, 137 recent) |
| **Last commit** | 2025-09-19 |
| **Links** | [repository](https://github.com/karlivory/khttp) · [benchmark](https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json) |

## Verdict

the-benchmarker/web-frameworks data.json (2026-10-06): zrk closed-loop over keep-alive on three trivial routes, each server pinned to about 4 CPUs on a 16-CPU x86_64 Fedora host labelled 'M1 Eight-Core Processor'. khttp 0.2 (serve_epoll, Rust 1.98, LTO, codegen-units 1) did 215,714 / 199,813 / 197,117 req/s at 64 / 256 / 512 connections against Drogon 1.9.13 (cmake release, no LTO, Date and Server headers off) at 177,005 / 178,341 / 171,358, 1.22x / 1.12x / 1.15x (derived from page data). Both ran at only 58-63% CPU saturation, below the suite's 75% server-bound bar; the 2026-09-24 snapshot, where both were CPU-bound, shows 1.13-1.18x.

## Use it when

- Small internal Rust HTTP/1.1 services on Linux behind a TLS-terminating proxy, where a two-crate dependency tree and a few MB of RSS matter more than features.
- Keep-alive traffic with tiny plaintext or JSON responses on a few cores: in the-benchmarker snapshots with about 4 CPUs per server it serves 1.12-1.22x Drogon's requests per second.
- Code that should stay synchronous (blocking Read bodies, streamed file responses) without bringing in tokio.
- Tools that need an embedded HTTP endpoint plus a minimal client from the same crate (client feature).

## Skip it when

- Anything needing TLS, HTTP/2, WebSockets or async handlers: none exist; it is HTTP/1.1 only.
- Clients that pipeline requests: extra requests that arrive in the same read are silently dropped (see gotchas).
- Untrusted or slow clients without a read timeout: workers block in read(), so as few as max(10, 2 x cores) slow connections can stall the server unless connection_setup_hook sets a read timeout.
- Many-core boxes: one epoll thread feeds every worker through a single Mutex-guarded mpsc queue. Published results stop at 4 server cores (the-benchmarker) and a 14-CPU laptop.
- Projects that need a maintained dependency: last commit and release 0.2.0 on 2025-09-19, single author, 40 stars, one open PR since 2025-09-12.

## How it is fast

The request head is read into a reused thread-local buffer and parsed in place with memchr-based scanning; routing is a small param and wildcard matcher, and the Date header line is cached once per second (code taken from faf). With the epoll feature, one thread runs an epoll loop: edge-triggered accept on the listener, level-triggered readiness on client sockets, and each ready connection is handed to a fixed worker pool (max(10, 2 x available_parallelism) threads), with an in-flight flag so only one worker owns a connection at a time. The crate has two dependencies and builds small; benchmarks.md reports 1.7 MB peak memory against 4.6-43.5 MB for actix-web, axum, may_minihttp and poem.

## Compared with alternatives

In the same the-benchmarker snapshot khttp (197-216K req/s) is level with Tako (Rust, 194-220K) and behind PowPow (Nim, 237-248K) and jet_server (Dart, 240-256K), so pick it for a synchronous, two-dependency Rust server, not for peak throughput. Take actix-web or a tokio-based server when you need TLS, HTTP/2, async I/O or a maintained project.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | memchr; libc (only with the epoll feature) |
| **Minimum toolchain** | Rust edition 2021; no rust-version declared on crates.io (the-benchmarker built it with Rust 1.98) |
| **Platforms** | any std target for serve() and serve_threaded(); the epoll feature is Linux 64-bit only (compile_error elsewhere) |
| **Thread safety** | Handlers run concurrently on a worker thread pool (or one thread per connection with serve_threaded); each connection is processed by one worker at a time |
| **Drop-in for the baseline** | no |

## Gotchas

- No HTTP/1.1 pipelining: read_request parses one head out of a thread-local buffer, and any bytes past it go only to the body reader, which ignores them for a GET with no Content-Length. A second pipelined request in the same read is lost and the client waits forever (src/server/mod.rs, src/body_reader.rs).
- serve_epoll leaks a heap Handle (64-byte aligned, holding an Arc of the handler config) for nearly every closed connection: the worker deletes the fd from epoll and sets closed, but the Handle is freed only if a stale event for it is already in the epoll thread's current batch. Churn-heavy traffic therefore grows memory. serve_epoll also never calls connection_teardown_hook.
- Plain serve() binds each connection to a pool thread for its whole keep-alive life, so with the default max(10, 2 x cores) threads only that many connections are served at once. This is why khttp fell to about 30k req/s at 512 connections in the-benchmarker before its suite entry switched to serve_epoll.
- Client sockets are level-triggered while a worker owns them, so the epoll thread keeps waking on the same ready fd until a worker drains it. That busy-spin burns CPU that shows up in the suite's server_cpu_saturation.

## Known shortcomings

- Rust side built with LTO and codegen-units=1 while Drogon has no LTO; the project's own benchmarks.md has no C/C++ baseline; 1.13-1.18x over Drogon in the 2026-09-24 and 2026-10-02 snapshots with both servers CPU-bound; last commit 2025-09-19; the-benchmarker 2026-10-06 rows sit at 53-62% CPU saturation (the suite counts only above 75% as server-bound); CPU string 'M1 Eight-Core Processor' names no model and the C++ compiler version is not pinned; cwist (C) is the best C row at 64 connections.
- Correctness bugs by code reading: pipelined requests are silently dropped (read_request's leftover is discarded for GET); serve_epoll leaks a Handle per closed connection and skips the teardown hook; blocking worker reads let slow clients stall the pool. Neither touches the measured keep-alive numbers. The 2026-10-06 rows sit at 58-63% saturation, below the suite's 75% bar (the 2026-09-24 CPU-bound snapshot still showed 1.13-1.18x); LTO on the Rust side only; Drogon threads_num 0 is probably 16 threads on a 4-CPU cpuset (unverified).

## Caveats and trade-offs

The suite entry rust/khttp was written by the khttp author (suite commits 0c5757a, 556cd7c and 5abe434 'khttp: switch to epoll backend' on 2026-09-22 by karlivory); it uses khttp's router with a :id parameter and sends Content-Type: text/plain, so its handler work is close to Drogon's (khttp averages 101.3 bytes received per request vs 78.3 for Drogon, derived from total_bytes_received / total_requests). The Rust side is built with LTO, codegen-units 1, panic = abort and overflow-checks off, while Drogon is built without LTO, so the optimisation settings are not equal. The project's benchmarks.md is first-party rewrk on an Intel Core Ultra 5 125U (14 CPUs) against Rust frameworks only (actix-web, axum, may_minihttp, poem): khttp 287,027 / 325,103 / 327,910 req/s at 64 / 256 / 512 connections, behind may_minihttp at 64; it has no C or C++ baseline. Last commit 2025-09-19 (release 0.2.0), 13 months old. HTTP/1.1 only, synchronous; no TLS or HTTP/2 in the pages read; the epoll loop is Linux-only. Before the epoll backend (2026-09-15 and 2026-09-20 snapshots) khttp fell to about 30k req/s at 512 connections. Suite-level weaknesses: published snapshots move a lot between runs (Drogon 101,282-179,279 req/s across the 2026-09-15 to 2026-10-06 snapshots) and a snapshot gives no repeat spread; the suite README says a run is server-bound only above 75% CPU saturation and invalid below 50%, and in the 2026-10-06 snapshot the 60 fastest rows sit at 49-63% (Drogon 62-63%), so the ceiling for the fastest servers may be the load generator or the box rather than the server; the presence of the server_cpu_saturation / server_cpu_cores probe places this snapshot in the README's current zrk --closed keep-alive revision, although the README's contract paragraph still describes oha with keep-alive disabled; the workload is three trivial routes (GET /, GET /user/:id, POST /user) with near-empty bodies. The C/C++ rows are only Drogon 1.9.13 (cmake -DCMAKE_BUILD_TYPE=release, threads_num 0 = auto, Server and Date headers disabled, no LTO), oatpp 1.3, agoo-c 0.7 and cwist 3.9 (C); cwist is the best C row at 64 connections (186,252) and agoo-c at 256 and 512; nginx, h2o and lithium are not rows in this suite. Same table, losers to Drogon at 256 connections: Crystal toro 166,910, Go fasthttp 166,243, C# aspnet-minimal-api 147,805 vs Drogon 178,341. The CPU string 'M1 Eight-Core Processor' on an x86_64 Fedora kernel is not a recognisable CPU model, and no C++ compiler version is pinned in the suite files read (cpp/drogon/config.yaml language version '14/17'), which is why this is B and not A. [retier] Pipelined requests are silently dropped (read_request's leftover discarded for GET), serve_epoll leaks a Handle per closed connection and skips the teardown hook, and blocking worker reads let slow clients stall the pool; none touches the measured keep-alive numbers. The 2026-10-06 rows sit at 58-63% saturation, below the suite's 75% bar (the 2026-09-24 CPU-bound snapshot showed 1.13-1.18x); LTO on the Rust side only; Drogon threads_num 0 is probably 16 threads on a 4-CPU cpuset (unverified).

Synchronous HTTP/1.1 micro-framework with only libc and memchr as dependencies and a custom epoll event loop on Linux; low-level API.

## Maintenance

Stale (last commit and crates.io release 0.2.0 on 2025-09-19, 4,660 downloads) but MIT-licensed and small enough to vendor. Code reading found two correctness gaps behind the fast path: pipelined requests are dropped, and the epoll mode leaks a Handle per closed connection. Neither affects the keep-alive, non-pipelined numbers. Harness caveats: the suite entry was written by the khttp author, only the Rust side has LTO, and Drogon's threads_num 0 probably sizes its IO threads to all 16 host CPUs, since std::thread::hardware_concurrency ignores the cpuset (not checked in run logs).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** data.json (updated 2026-10-06) of the independent the-benchmarker/web-frameworks suite has khttp (framework_id 3169) and Drogon (55) with exactly the quoted req/s; the 2026-10-02 snapshot repeats them and the 2026-09-24 snapshot, where both servers were CPU-bound (93-99%), shows the same 1.13-1.18x margin. Code and build files are public (rust/khttp/src/main.rs, rust/khttp/Cargo.toml, cpp/drogon/\*); not A because the CPU string 'M1 Eight-Core Processor' is not a recognisable model and no C++ compiler version is pinned.
- **Verifier notes:** Numbers verified in data.json (2026-10-06) and repeated in two earlier snapshots, including a 2026-09-24 run where both khttp and Drogon were CPU-bound, the strongest evidence of the three entries in this batch. Shortcomings to record: Rust side built with LTO and codegen-units 1 against a non-LTO Drogon, first-party suite entry, project's own benchmarks.md has no C/C++ baseline, stale (last commit 2025-09-19), 2026-10-06 rows below the suite's 75% server-bound threshold.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-51 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/8657397/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/0fccb1d/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/5d9db56/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/.spec/route_spec.rb>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/main.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/CMakeLists.txt>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/controllers/UserCtrl.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/plugins/SyncPlugin.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/c/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/c/agoo-c/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/commits/master/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/khttp/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/khttp/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/khttp/src/main.rs>
  - <https://github.com/the-benchmarker/web-frameworks/commits/master/rust/khttp>
  - <https://github.com/karlivory/khttp>
  - <https://github.com/karlivory/khttp/commits/main>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/benchmarks.md>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/LICENSE>
  - <https://crates.io/api/v1/crates/khttp>
- **Sources the enricher read:**
  - <https://github.com/karlivory/khttp>
  - <https://github.com/karlivory/khttp/tree/main/src>
  - <https://github.com/karlivory/khttp/tree/main/src/server>
  - <https://github.com/karlivory/khttp/issues?q=is%3Aissue>
  - <https://github.com/karlivory/khttp/pulls>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/README.md>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/benchmarks.md>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/src/server/builder.rs>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/src/server/epoll.rs>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/src/server/mod.rs>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/src/threadpool.rs>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/src/router.rs>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/src/date.rs>
  - <https://raw.githubusercontent.com/karlivory/khttp/HEAD/src/body_reader.rs>
  - <https://crates.io/api/v1/crates/khttp>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/khttp/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/khttp/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/khttp/src/main.rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/main.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/controllers/UserCtrl.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/CMakeLists.txt>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/karlivory/khttp`) · [data/wave14/enrich/raw/github_com_karlivory_khttp.json](../../../data/wave14/enrich/raw/github_com_karlivory_khttp.json) (enrichment confidence 0.6)

</details>
