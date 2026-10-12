# Tako (per-thread server)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust multi-transport web framework on hyper; its thread-per-core HTTP/1.1 server out-served Drogon 1.12-1.24x in the-benchmarker.

| | |
|---|---|
| **Beats** | Drogon 1.9.13 (C++, trantor event loop; the-benchmarker cpp/drogon, cmake release build); also agoo-c 0.7 (C) in the same table |
| **Claimed result** | the-benchmarker data.json (updated 2026-10-06): tako 2.4 219,732 / 200,361 / 193,822 req/s at 64 / 256 / 512 connections vs Drogon 1.9.13 177,005 / 178,341 / 171,358 (1.24x / 1.12x / 1.13x, derived from page data); vs agoo-c 0.7 (C) 143,753 / 214,704 / 200,748 (1.53x at 64, 0.93x at 256, 0.97x at 512, derived); vs CWIST 3.9 (C) 186,252 / 166,573 / 162,101 (1.18x / 1.20x / 1.20x, derived). Corroborated in HttpArena (MDA2AV/HttpArena site/data/results/tako.json and drogon.json, Threadripper PRO 3995WX): baseline-4096 3,258,564 vs Drogon 2,022,710 (1.61x), limited-conn-4096 2,474,910 vs 1,694,883 (1.46x), pipelined-4096 22,082,892 vs 7,801,404 (2.83x), json-comp-4096 212,739 vs 127,466 (1.67x), json-tls-4096 904,303 vs 253,055 (3.57x), latency-500k-8cpu 470,285 vs 374,962 (1.25x), 8gbit-512 48,998 vs 49,360 (0.99x), all derived from page data. |
| **Workload** | the-benchmarker/web-frameworks minimal HTTP contract (GET /, GET /user/:id, POST /user on port 3000), total_requests_per_s at 64, 256 and 512 connections, each framework in its own container. |
| **Metric** | throughput |
| **Hardware** | the-benchmarker data.json hardware field: cpu_name 'M1 Eight-Core Processor' (does not name a recognisable CPU model), 16 logical CPUs, 7,733,008 kB RAM, Linux 7.2.7-200.fc44.x86_64; per-run server_cpu_cores / server_cpu_saturation imply about 4 CPUs allotted to each server container (derived from page data). HttpArena current.json: AMD Ryzen Threadripper PRO 3995WX (64 cores, 128 threads), 251 GiB, Ubuntu 24.04.4, kernel 6.17.0-22, governor performance. |
| **Compiler and flags** | the-benchmarker: tako built in rust:1.98-slim with cargo build --release, Cargo.toml release profile opt-level 3, lto = true, codegen-units = 1, panic = abort (the Dockerfile repeats lto/panic/codegen-units via --config), tako-rs 2.4 with feature per-thread, no target-cpu. Drogon v1.9.13 built in debian:trixie-slim with build-essential (GCC 14 from Debian trixie, inferred from the image) via cmake -DCMAKE_BUILD_TYPE=release (CMake's Release flags -O3 -DNDEBUG), C++17, no LTO, no -march; config.json threads_num 0 (one IO thread per core). HttpArena: tako built in rust:1.99-trixie with RUSTFLAGS='-C target-cpu=native', lto = 'fat', codegen-units = 1; Drogon built from drogonframework/drogon:latest with CMAKE_BUILD_TYPE=Release (no -march=native, compiler version not stated) and run with LD_PRELOAD jemalloc. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | no |
| **Why it wins** | Thread-per-core design with one current-thread runtime per CPU and SO_REUSEPORT listeners (from the HttpArena entry description and the README). |
| **Adoption** | 163 stars; tako-rs crate 5,186 downloads (crates.io API, 2026-10-12; latest 2.4.1) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/rust-dd/tako) · [benchmark](https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json) |

## Verdict

the-benchmarker data.json (updated 2026-10-06; zrk closed-loop keep-alive on GET /, GET /user/:id and POST /user, server pinned to 4 of 16 cores on an x86_64 host whose CPU string 'M1 Eight-Core Processor' is unidentifiable): tako 2.4 per-thread 219,732 / 200,361 / 193,822 req/s versus Drogon 1.9.13 (GCC from Debian trixie, CMake release, no LTO) 177,005 / 178,341 / 171,358 at 64 / 256 / 512 connections, 1.12-1.24x, with both servers at 56-63% CPU saturation. HttpArena on a Threadripper PRO 3995WX confirms the HTTP/1.1 lead over Drogon (baseline-4096 1.61x, pipelined-4096 2.83x) with a native-tuned tako build.

## Use it when

- Linux HTTP/1.1 APIs in Rust that want a full framework (extractors, middleware, OpenAPI, gRPC) with hyper-class throughput: in the-benchmarker tako matched plain hyper within 2% and beat Drogon 1.9.13 by 1.12-1.24x.
- Keep-alive or pipelined HTTP/1.1 traffic at high connection counts: HttpArena pipelined-4096 22.1M req/s vs plain hyper 16.2M and Drogon 7.8M; baseline-4096 3.26M vs hyper 3.00M and actix 2.78M.
- CPU-constrained deployments where cost per request matters: derived from the-benchmarker's core counts, tako used about 10.2 us of server CPU per request at 64 connections versus Drogon's 14.3 us, and HttpArena latency-1m held the same 1M req/s target at 2,641% CPU versus Drogon's 3,552%.
- One codebase that must also expose WebSocket, gRPC, SSE or raw TCP/UDP listeners next to the HTTP API under a single router and middleware model.

## Skip it when

- HTTP/2, h2c or HTTP/3 heavy services: per-thread workers serve HTTP/1.1 only, and tako's multi-thread h2 path served 741,740 req/s on HttpArena baseline-h2-256 versus 6,974,787 for the plain hyper entry and 3,884,214 for actix (h2c-256: 747,323 vs actix 5,918,827).
- Thousands of concurrent WebSocket connections: echo-ws-4096 420,836 msg/s versus actix 3,409,380 (tied at 512 connections), and echo-ws-pipeline-4096 5.35M versus actix 43.1M.
- Compressed JSON with the stock compression plugin: json-comp-4096 212,739 req/s versus actix 541,211.
- Teams that need a stable, widely used framework: one maintainer, 5,191 crates.io downloads, Rust 1.95+ with edition 2024, and five releases from 2.1.0 (2026-09-27) to 2.4.1 (2026-10-11), with migration guides for 2.1, 2.2, 2.3 and 2.4.
- Expecting a win over the fastest C servers: HttpArena puts it level with nginx on baseline-4096 (3,258,564 vs 3,284,513) and far behind on static TLS and HTTP/2; Nim PowPow and Dart jet_server rows outscore it in the-benchmarker.

## How it is fast

The HTTP/1.1 engine is hyper's http1 connection driver (keep-alive, pipeline_flush on, TCP_NODELAY set per socket); tako's contribution is the thread-per-core shell: current-thread Tokio runtimes driving connections with spawn_local so requests never cross threads, kernel SO_REUSEPORT fan-out, and a least-live-connections hand-off (balance_connections, on by default) that moves a freshly accepted socket to a less busy worker over an unbounded channel. The 2.4 docs add that a hello-world request no longer allocates. Actix Web and ntex use the same shape, and the author's own wrk runs put per-thread 3-17% ahead of Actix Web and 27-31% ahead of tako's default multi-thread server (3.2x at 100 loopback connections).

## Compared with alternatives

Pick tako over actix-web or ntex when HTTP/1.1 throughput and a multi-transport router in one crate matter most: it edged actix 4.8 by 1.03-1.05x in the-benchmarker and 1.17x on HttpArena baseline-4096, and its own wrk runs put it 3-17% ahead of Actix Web. Choose actix-web for h2, many WebSocket connections or compressed JSON, where actix leads by 2.5-8x on HttpArena, and note that jet_server and PowPow posted higher the-benchmarker rates than tako.

## Integration

| | |
|---|---|
| **Form** | crate (tako-rs on crates.io, imported as `tako`; `per-thread` feature pulls in tako-rs-server-pt) |
| **Dependencies** | tokio, hyper 1.x, hyper-util, socket2 (per-thread server); optional compio, rustls, quinn/h3, core_affinity, tikv-jemallocator, tonic and many integrations behind cargo features |
| **Minimum toolchain** | Rust 1.95, edition 2024 |
| **Platforms** | Linux for the per-thread server's kernel load balancing (SO_REUSEPORT); on macOS/BSD and Windows the Tokio workers rely on the balance_connections hand-off and the code warns when it is off; Compio flavour targets io_uring, IOCP or kqueue |
| **Thread safety** | Router is shared across worker threads through an Arc; each connection and its handler futures stay on one worker's current-thread runtime (spawn_local); cross-request shared state must be thread-safe |
| **Drop-in for the baseline** | no |

## Gotchas

- The same table that shows the Drogon win also shows it is hyper's: the-benchmarker's plain hyper 1.5 entry (about 40 lines, default multi-thread work-stealing Tokio runtime, one listener) scored 216,185 / 201,964 / 198,218 req/s at 64 / 256 / 512 connections, within 2% of tako's 219,732 / 200,361 / 193,822, and actix 4.8 and khttp sit in the same band, all at 55-62% server CPU saturation. In this generator-bound run the thread-per-core design adds nothing measurable over plain hyper; it does show up in HttpArena (baseline-4096 1.08x, pipelined-4096 1.36x over hyper).
- Likely baseline handicap: the-benchmarker's Drogon config sets threads_num 0, which Drogon 1.9.13 (ConfigLoader.cc) resolves with std::thread::hardware_concurrency(). glibc-based implementations ignore CPU affinity there, so inside a --cpuset-cpus container sized to 4 cores on a 16-CPU host Drogon probably started about 16 event loops, while tako's available_parallelism() honours the cpuset (inferred, not observed). Drogon's latency profile fits that oversubscription: p50 0.1-0.7 ms but p99 11-21 ms, against tako's p99 0.3-2.7 ms, roughly equal to its p50.
- HttpArena rows mix servers: per its meta.json only plain HTTP/1.1 and WebSocket on :8080 use the per-thread server; json-tls (904,303 vs Drogon 253,055), h2, h2c and h3 run tako's multi-thread Server. The tako entry there is built with -C target-cpu=native and fat LTO against a generic Drogon build, uses tako 2.4.1 (the-benchmarker snapshot predates 2.4.1, so it ran 2.4.0), and is maintained by tako's author.
- Per-thread defaults changed recently: pin_to_core went off by default in 2.4.0 (the author measured pinning 3% slower on loopback and 5% faster pipelined), balance_connections is on, and header_read_timeout closes idle connections after 30-45 s. TLS, h2c and PROXY-protocol listeners need the regular Server builder, so a mixed deployment runs two runtimes in one process, as the HttpArena entry does.

## Known shortcomings

- Win comes from the thread-per-core design, not the Rust language; server CPU at 56-63% (the-benchmarker's grey zone); the CPU string 'M1 Eight-Core Processor' names no model; Rust built with LTO (plus target-cpu=native in HttpArena) while Drogon is built plain; agoo-c (C) beats it at 256/512 connections; far behind nginx on HTTP/2, HTTP/3 and static TLS.
- In the same the-benchmarker table the plain hyper 1.5 entry (default work-stealing Tokio) scores 216,185 / 201,964 / 198,218 req/s, within 2% of tako, so the Drogon margin belongs to hyper, not to thread-per-core; all top rows sit at 55-62% CPU saturation, so the load generator is the bottleneck. Likely Drogon handicap (inferred, not observed): threads_num 0 resolves to std::thread::hardware_concurrency() (ConfigLoader.cc) and glibc ignores affinity, so Drogon probably ran about 16 IO loops on a 4-core cpuset (its p99 of 11-21 ms against a p50 of 0.1-0.7 ms fits). On HttpArena the json-tls and h2/h3 rows run tako's multi-thread Server, not per-thread; weak spots: h2 741,740 vs hyper 6,974,787; echo-ws-4096 420,836 vs actix 3,409,380; json-comp 2.5x behind actix.

## Caveats and trade-offs

The suite win is architectural (thread-per-core runtime with SO_REUSEPORT listeners), not a Rust language effect, and margins are small (1.12-1.24x over Drogon; agoo-c (C) beats tako at 256 and 512 connections). The README's own benchmark compares only against Actix Web, ntex and Axum on a 24 vCPU EPYC 9655P container (not C or C++). the-benchmarker weaknesses: one published snapshot (data.json updated 2026-10-06, no repeat spread); the suite README says above 75% server CPU saturation the number is the framework's and below 50% it is not, and tako (56-57%) and Drogon (62-63%) both sit in the band between; the 57 of the 60 fastest rows at 256 connections that carry a saturation value range 49-69% (suite median 71%), so the fastest servers may be generator-bound; the README describes the current method as zrk --closed keep-alive (saturation fields exist only in that method, so this snapshot is probably that revision, inferred) but an older paragraph still describes oha with keep-alive disabled; three trivial routes with near-empty bodies. Flags differ: Rust side uses LTO and codegen-units 1, Drogon has no LTO; in HttpArena the Rust side is built with target-cpu=native and Drogon generically, and the HttpArena tako entry is maintained by the tako author (meta.json maintainers dancixx). HttpArena does not generalise the win to nginx: level on baseline-4096 (3,258,564 vs nginx 3,284,513, 0.99x) and far behind on HTTP/2 and HTTP/3 (baseline-h2-256 741,740 vs 3,414,750; baseline-h3-64 534,205 vs 4,849,624) and static TLS (142,858 vs 720,869). nginx, h2o and lithium are not rows in the-benchmarker; same-table losers to Drogon at 256 connections include Crystal toro, Go fasthttp and C# aspnet-minimal-api. [retier] The plain hyper 1.5 entry (default work-stealing Tokio) scores 216,185 / 201,964 / 198,218 req/s in the same table, within 2% of tako, so the Drogon margin belongs to hyper, not thread-per-core; all top rows sit at 55-62% CPU saturation, so the load generator is the bottleneck. Drogon's threads_num 0 resolves to hardware_concurrency() and glibc ignores affinity, so it probably ran about 16 IO loops on a 4-core cpuset (inferred; p99 11-21 ms against p50 0.1-0.7 ms fits). On HttpArena the json-tls and h2/h3 rows run tako's multi-thread Server; h2 741,740 vs hyper 6,974,787, echo-ws-4096 420,836 vs actix 3,409,380, json-comp 2.5x behind actix.

Multi-transport Rust framework (HTTP/1.1, h2, h3, WebSocket, SSE, gRPC) on Tokio or Compio; the fast path is the thread-per-core 'per-thread' server with current-thread runtimes and SO_REUSEPORT listeners.

## Maintenance

Actively developed by a single maintainer (all recent commits by dancixx, 2.4.1 released 2026-10-11), MIT, 163 stars and about 5,200 crates.io downloads; usable for HTTP/1.1-heavy Linux services, but young and churning fast, so pin the minor version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent, well-known suite (the-benchmarker/web-frameworks, 7.1k stars): data.json rows tako 2.4 (id 3313) 219,732 / 200,361 / 193,822 req/s and drogon 1.9 (id 55) 177,005 / 178,341 / 171,358 at 64/256/512 match the record; build files (rust/tako/Cargo.toml, rust/Dockerfile, cpp/drogon/config.yaml, cpp/Dockerfile) are public, but the published cpu_name 'M1 Eight-Core Processor' does not identify a CPU model, the C++ compiler version is only implied by the debian:trixie-slim build-essential image, and both servers ran at 57-62% CPU saturation, inside the band the suite's README calls neither valid nor invalid, so not A.
- **Verifier notes:** Numbers verified in the-benchmarker data.json and corroborated by HttpArena, where tako also beats Drogon by 1.25-3.57x on most shared tests (8gbit tie), though HttpArena builds tako with target-cpu=native against a generic Drogon build. Shortcomings: architectural not language-level win, 1.12-1.24x margins, saturation in the suite's grey zone, unidentifiable CPU string, LTO/native-flag asymmetry, loses to agoo-c (C) at 256/512 and to nginx on HTTP/2, HTTP/3 and static TLS in HttpArena.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-52 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/tako/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/tako/src/main.rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/CMakeLists.txt>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/c/agoo-c/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks>
  - <https://github.com/the-benchmarker/web-frameworks/tree/develop/cpp>
  - <https://github.com/rust-dd/tako>
  - <https://github.com/rust-dd/tako/commits>
  - <https://crates.io/api/v1/crates/tako-rs>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/data>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/data/results>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/tako.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/tako/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/tako/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/tako/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/meta.json>
- **Sources the enricher read:**
  - <https://github.com/rust-dd/tako>
  - <https://github.com/rust-dd/tako/commits/main>
  - <https://github.com/rust-dd/tako/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/rust-dd/tako/HEAD/README.md>
  - <https://raw.githubusercontent.com/rust-dd/tako/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-dd/tako/HEAD/tako-rs/Cargo.toml>
  - <https://github.com/rust-dd/tako/tree/main/tako-rs-server-pt/src>
  - <https://raw.githubusercontent.com/rust-dd/tako/HEAD/tako-rs-server-pt/Cargo.toml>
  - <https://raw.githubusercontent.com/rust-dd/tako/HEAD/tako-rs-server-pt/src/lib.rs>
  - <https://raw.githubusercontent.com/rust-dd/tako/HEAD/tako-rs-server-pt/src/config.rs>
  - <https://raw.githubusercontent.com/rust-dd/tako/HEAD/tako-rs-server-pt/src/listener.rs>
  - <https://raw.githubusercontent.com/rust-dd/tako/HEAD/tako-rs-server-pt/src/worker.rs>
  - <https://raw.githubusercontent.com/rust-dd/tako/HEAD/tako-rs-server-pt/src/balance.rs>
  - <https://raw.githubusercontent.com/rust-dd/tako/HEAD/tako-rs-server-pt/src/shutdown.rs>
  - <https://github.com/rust-dd/tako/tree/main/website>
  - <https://raw.githubusercontent.com/rust-dd/tako/main/website/content/docs/benchmarks.mdx>
  - <https://raw.githubusercontent.com/rust-dd/tako/main/website/content/docs/deployment.mdx>
  - https://tako.rust-dd.com/docs/benchmarks (DNS failure, not reachable)
  - <https://crates.io/api/v1/crates/tako-rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/README.md>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/tako/src/main.rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/tako/Cargo.toml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/tako/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/rust/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/rust/hyper/src/main.rs>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/rust/hyper/Cargo.toml>
  - <https://github.com/the-benchmarker/web-frameworks/tree/master/cpp/drogon>
  - <https://github.com/the-benchmarker/web-frameworks/tree/master/cpp/drogon/plugins>
  - <https://github.com/the-benchmarker/web-frameworks/tree/master/cpp/drogon/controllers>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/main.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/drogon/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/cpp/drogon/CMakeLists.txt>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/cpp/drogon/plugins/SyncPlugin.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/cpp/drogon/controllers/UserCtrl.cc>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/Dockerfile>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/HEAD/cpp/config.yaml>
  - <https://raw.githubusercontent.com/drogonframework/drogon/v1.9.13/lib/src/ConfigLoader.cc>
  - <https://raw.githubusercontent.com/drogonframework/drogon/v1.9.13/lib/src/HttpAppFrameworkImpl.cc>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/tako/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/tako/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/tako/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/tako/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/tako.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/hyper.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/results/actix.json>
  - https://reviews.llvm.org/D38481 (WebSearch snippet: glibc hardware_concurrency ignores thread affinity)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/rust-dd/tako`) · [data/wave14/enrich/raw/github_com_rust_dd_tako.json](../../../data/wave14/enrich/raw/github_com_rust_dd_tako.json) (enrichment confidence 0.75)

</details>
