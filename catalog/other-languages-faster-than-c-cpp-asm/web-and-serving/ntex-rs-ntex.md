# ntex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust framework for HTTP/1, HTTP/2, WebSocket and TLS services; in HttpArena it edges Drogon on keep-alive requests but loses on connection churn.

| | |
|---|---|
| **Beats** | Drogon (C++) in the HttpArena baseline profile; lithium and cinatra (C++) in the TechEmpower Round 22 plaintext leaderboard |
| **Claimed result** | HttpArena baseline-4096: 2,168,712 req/s vs Drogon 2,022,710 (1.07x, derived from page data) and Cutelyst 2,153,860 (1.007x, a tie), behind nginx 3,284,513, h2o 3,641,609 and libreactorng 4,377,377. limited-conn-4096: ntex 1,449,176 is slower than Drogon 1,694,883 (0.86x, derived) and Cutelyst 1,736,401 (0.83x, derived). Workload profiles where ntex leads Drogon: async-32000 963,884 vs 143,001 (6.7x, derived) and Cutelyst 761,563 (1.27x); json-comp-4096 589,934 vs 127,466 (4.6x, derived); json-tls-4096 1,254,763 vs Drogon 253,055 (4.96x, derived), level with h2o 1,229,462 and behind nginx 1,313,755. TechEmpower Round 22 plaintext screenshot: ntex [raw] 7,000,539 vs cinatra 6,998,076, lithium 6,993,976 (+0.1%, a tie) and userver[bare] 5,974,256 (1.17x, derived). |
| **Workload** | HttpArena baseline profile (mixed GET/POST with query parsing, 4096 connections) with ntex 2 on its tokio-backed runtime; and TechEmpower Round 22 plaintext (ntex [raw]). |
| **Metric** | throughput |
| **Hardware** | HttpArena: AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads), with the server pinned to cpuset 0-31,64-95 (32 cores / 64 threads) and gcannon on the other half over loopback (MTU 1500), per site/content/docs/hardware/_index.md. TechEmpower Round 22: Dell R440 Xeon Gold + 10 GbE, as printed on the leaderboard image; the gnet README describing that environment gives 28 HT cores of Intel Xeon Gold 5120, 32 GB RAM and Debian 12. |
| **Compiler and flags** | HttpArena: ntex built in the rust:1.94 image with cargo build --release, Cargo profile.release opt-level=3 and codegen-units=1, and no target-cpu=native and no LTO (the Dockerfile comment cites rustc SIGSEGV and GCC ICE history). Drogon: CMake Release (CMake's default -O3 -DNDEBUG) in the drogonframework/drogon:latest image, without -march=native, with jemalloc LD_PRELOADed. Cutelyst: CMake Release with Ubuntu 26.04 g++. TechEmpower Round 22: build flags not verified. The current FrameworkBenchmarks ntex.dockerfile (rust:1.93, RUSTFLAGS=-C target-cpu=native) postdates Round 22 (2023), and its benchmark_config.json no longer has an 'ntex [raw]' variant, so it does not describe the run that produced 7,000,539. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 2.5k stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/ntex-rs/ntex) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/ntex.json) |

## Verdict

HttpArena ran ntex 2.18 on tokio (rustc 1.94, opt-level 3, codegen-units 1, no LTO, no target-cpu=native) against Drogon (CMake Release from drogonframework/drogon:latest, jemalloc preloaded, no -march=native) on a Threadripper PRO 3995WX, with the server on 32 cores / 64 threads and the gcannon load generator on the other half, best of three 5 s runs. ntex leads Drogon by 1.07x on baseline-4096 and trails it 0.86x on limited-conn-4096; the large json-comp, json-tls and async leads come from Drogon-entry choices (level-6 gzip, jsoncpp copies, a single timer loop). Per the verified record, TechEmpower Round 22 plaintext had ntex [raw] at 7,000,539 vs cinatra 6,998,076 and lithium 6,993,976, a 0.1% tie with unknown build flags.

## Use it when

- Rust HTTP/1.1 APIs that want framework features (routing, extractors, middleware, TLS) with keep-alive throughput in Drogon's class: HttpArena baseline-4096 gives 2,168,712 req/s vs Drogon 2,022,710 and Cutelyst 2,153,860 on a Threadripper PRO 3995WX (server on 32 cores / 64 threads).
- JSON over TLS with many keep-alive clients: json-tls-4096 reached 1,254,763 req/s at 159 MiB RSS, level with h2o (1,229,462) and close to nginx (1,313,755).
- Services that also speak MQTT, AMQP or gRPC and want one runtime and buffer model across protocols (ntex-mqtt, ntex-amqp, ntex-grpc).
- Deployments that want to choose the I/O backend per build: tokio, compio, or the native polling or io_uring reactor through Cargo features.
- Memory-lean servers: HttpArena RSS was 40-148 MiB on most profiles, against Drogon's 1.3 GiB on limited-conn-4096.

## Skip it when

- Connection churn (short-lived connections): limited-conn-4096 (10 requests per connection) gives 1,449,176 req/s, slower than Drogon 1,694,883 and Cutelyst 1,736,401.
- Top plain HTTP/1.1 throughput: nginx 3,284,513, h2o 3,641,609, libreactorng 4,377,377 and actix-web 2,775,120 all beat it on baseline-4096. At a pinned 1M req/s it spent 35.03 us of CPU per request vs Drogon 32.13 us, and on 8 logical CPUs it held 337,940 of the 500,000 req/s offered vs Drogon 374,962.
- Sub-16 ms sleeps or timeouts: ntex::time::sleep rounds up to the 16 ms wheel tick (UNITS = 4 in ntex-util 2.16 and still on main). The HttpArena 10 ms delay averaged 30.63 ms.
- Teams that need a stable API: 3.0 shipped 2026-02-02 and 4.0 on 2026-10-08. 4.x reversed middleware registration order on purpose (issue #1106, documented only in the migration guide) and changed HttpServer::bind to take a SharedCfg.
- Production use of the new default io_uring reactor without testing: issue #932 (ntex 3.10.0 with ntex-bytes 1.7.6) served stale bytes at the start of static-file bodies until ntex-net 1.13.1, #911 reported flaky first requests on io-uring, and #1113 (open) says Compress gzips the empty body of a 304.

## How it is fast

Each worker thread runs its own single-threaded runtime (thread-per-core, no work-stealing), so services and state use Rc and Cell instead of Arc and locks. Ntex 2.x can run on tokio, compio or its own neon runtime, and ntex 4 defaults to a native io_uring reactor on Linux. Reads and writes go through ntex-io filter buffers drawn from ntex-bytes memory pools (PoolId). HTTP/1 heads are parsed with httparse into a stack array of uninitialised header slots, the Date header is cached by a per-thread DateService, and keep-alive and read-rate timeouts run on a hierarchical timer wheel with 16 ms ticks (ntex-util time/wheel.rs, modelled on the Linux kernel timer wheel), which keeps timers cheap but coarse.

## Compared with alternatives

Pick actix-web over ntex for the larger ecosystem and its higher baseline-4096 score (2,775,120 vs 2,168,712 req/s). Pick ntex when you want one stack for HTTP, MQTT, AMQP and gRPC, or a build-time choice of tokio, compio or native io_uring. The raw tokio, tokio-uring, zix and zeemo HttpArena entries (3.5-4.4M req/s) are minimal benchmark servers, not frameworks.

## Integration

| | |
|---|---|
| **Form** | crate (ntex 4.2.0 on crates.io; workspace crates ntex-io, ntex-server, ntex-rt, ntex-net, ntex-http, ntex-router, ntex-tls, ntex-util, ntex-bytes, ntex-service) |
| **Dependencies** | httparse, http types, serde, serde_json, serde_urlencoded, log, bitflags, slab, futures-timer, nanorand and the ntex-\* workspace crates; optional tokio, compio, polling or io-uring, rustls or openssl, flate2 (zlib-rs backend since 4.2.0) and zstd for compress, cookie |
| **Minimum toolchain** | Rust 1.97 for ntex 4.x (README MSRV badge and crates.io rust_version); the ntex 2.18.0 that HttpArena measured needs Rust 1.82 |
| **Platforms** | Linux (io_uring with polling fallback, or tokio/compio), other Unix (polling), Windows (IOCP); CI runs on Linux, macOS and Windows |
| **Thread safety** | One single-threaded runtime per worker. The App factory runs once per worker and services are !Send (Rc-based), so shared state is passed through State and cloned or Arc-wrapped per worker. Worker count defaults to core_affinity::get_core_ids() (the CPU affinity set), else available_parallelism. |
| **Drop-in for the baseline** | no |

## Gotchas

- Version gap: the HttpArena entry pins ntex = "2" with the tokio feature, which resolves to 2.18.0 (2026-02-01). Current ntex is 4.2.0 (2026-10-10), two breaking majors later, with a native io_uring runtime by default on Linux, so none of the measured rows describe ntex 4.
- The async-32000 lead (963,884 vs Drogon 143,001 req/s, 6.7x) measures the two entries' timer choices, not HTTP stack speed. ntex's 16 ms timer tick turns the 10 ms delay into a 30.63 ms average, which caps it near 32,000 / 33 ms. Drogon's handler schedules every delay with app().getLoop(), which Drogon documents as the framework's main event loop rather than an I/O loop, so all 32,000 timers run on one thread (812% CPU, 221 ms average latency).
- The json-comp lead (589,934 vs 127,466 req/s, 4.6x) compares unequal work. ntex gzips in the handler at flate2 level 1 (flate2 1.x default backend). Drogon's stock enableGzip path calls deflateInit2 with Z_DEFAULT_COMPRESSION (level 6), and its handler deep-copies jsoncpp Values per item. Bandwidth divided by req/s gives about 1,718 bytes per ntex response vs 1,393 for Drogon (derived from page data). The profile retires each connection after 25 requests (-r 25), so the 116,073 reconnects are by design.
- Harness asymmetry against ntex: the entry wraps the App in middleware::Logger::default().exclude("/"). No route is "/", so every request calls SystemTime::now, clones the log format and renders the request line, remote address, Referer and User-Agent into heap Strings, then boxes the body in a StreamLog. No logger is installed, so the output is discarded, while Drogon runs at log level kError. The baseline, limited-conn and latency rows probably understate a Logger-free ntex, by an amount not measured.

## Known shortcomings

- Only 1.07x Drogon on the HttpArena baseline and slower than Drogon and Cutelyst on limited-connection (0.86x, 0.83x); the big json/async leads are over Drogon's jsoncpp path only; the TechEmpower R22 plaintext lead is a 0.1% tie and the R22 build flags are unknown (the cited dockerfile postdates R22).
- The big margins over Drogon are unequal work: async-32000 6.7x because the Drogon entry puts every delay on app().getLoop() (a single main event loop at 812% CPU) while ntex's sleep rounds to a 16 ms tick, so a 10 ms delay averages 30.63 ms; json-comp 4.6x because ntex gzips at level 1 against Drogon's Z_DEFAULT_COMPRESSION level 6 (about 1,718 vs 1,393 bytes per response, derived). Measured ntex 2.18 on tokio; current 4.2.0. A flaw against ntex: the entry runs Logger middleware on every request with no logger installed, so baseline and limited-conn likely understate it. The only equal rows: baseline 1.07x, limited-conn 0.86x, latency-1m 35.03 vs 32.13 us CPU per request.

## Caveats and trade-offs

The win over C++ is mixed and small where the work is equal. On baseline ntex is level with Cutelyst and 7% over Drogon, behind nginx, h2o and libreactorng (C), and on limited-conn it is 14-17% slower than both C++ frameworks. The large json-comp, json-tls and async margins are over Drogon only: its JSON path deep-copies jsoncpp Values per item (a library choice), and Drogon's gzip level was not checked against ntex's flate2 level 1. ntex is built without target-cpu=native, while nginx and h2o use -march=native and Drogon does not. The TechEmpower margin over lithium and cinatra is 0.1%, noise on a saturated plaintext test: the first 19 rows are within 6% of each other and the first nine within 0.3%, which is network and pipelining bound. Those numbers come from a screenshot of the Round 22 leaderboard hosted in the gnet author's illustrations repo (https://raw.githubusercontent.com/panjf2000/illustrations/master/benchmark/techempower-plaintext-top50-light.jpg), since the primary results site was not reachable. The ntex README itself makes no performance claim. The HttpArena results JSON files are undated and are rerun by the suite's maintainers. [retier] async-32000 6.7x: the Drogon entry puts every delay on app().getLoop() (a single main event loop at 812% CPU) while ntex's sleep rounds to a 16 ms tick, so a 10 ms delay averages 30.63 ms; json-comp 4.6x: ntex gzips at level 1 against Drogon's level 6 (about 1,718 vs 1,393 bytes per response). The entry runs Logger middleware on every request with no logger installed, so baseline and limited-conn likely understate ntex. Measured ntex 2.18 on tokio; current 4.2.0.

Composable networking framework with its own runtimes (tokio, neon, compio); the README gives no benchmark figures.

## Maintenance

Very active: 4.2.0 released 2026-10-10 after 4.0.0 on 2026-10-08, 5,458 commits, 2.5k stars, about 1.1M crates.io downloads, 3 open issues, dual MIT or Apache-2.0. Copyable as a dependency, but expect API breaks between majors.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B. The HttpArena numbers match site/data/results/ntex.json and the sibling drogon/cutelyst/nginx/h2o.json files. The benchmark code is public (frameworks/ntex/{Dockerfile,Cargo.toml,src/main.rs}, frameworks/drogon/{Dockerfile,CMakeLists.txt,main.cc}, scripts/lib/profiles.sh), toolchains and flags are in the Dockerfiles and Cargo.toml, and the CPU is named in site/content/docs/hardware/_index.md (Threadripper PRO 3995WX), the same basis as the wtx/cutelyst precedent. The TechEmpower R22 row was checked on the gnet-hosted screenshot and is supporting tier-B evidence only.
- **Verifier notes:** Numbers verified, and the TechEmpower screenshot was read directly. Tier raised B to A on HttpArena's named CPU (wtx/cutelyst precedent). Shortcomings to record: only 1.07x over Drogon on baseline and slower than Drogon and Cutelyst on limited-conn (0.86x, 0.83x); big json/async leads are over Drogon's jsoncpp path only; the TechEmpower plaintext lead is a 0.1% tie; the R22 build flags are unknown because the cited ntex.dockerfile is the current master, not Round 22.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-18 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/ntex.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cutelyst.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ntex/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ntex/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ntex/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ntex/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/main.cc>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cutelyst/Dockerfile>
  - <https://raw.githubusercontent.com/panjf2000/gnet/HEAD/README.md>
  - <https://raw.githubusercontent.com/panjf2000/illustrations/master/benchmark/techempower-plaintext-top50-light.jpg>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/ntex/ntex.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/Rust/ntex/benchmark_config.json>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/C++/lithium/lithium.dockerfile>
  - <https://raw.githubusercontent.com/TechEmpower/FrameworkBenchmarks/HEAD/frameworks/C++/cinatra/cinatra.dockerfile>
  - <https://github.com/ntex-rs/ntex>
  - <https://github.com/ntex-rs/ntex/commits>
- **Sources the enricher read:**
  - <https://github.com/ntex-rs/ntex>
  - <https://raw.githubusercontent.com/ntex-rs/ntex/HEAD/README.md>
  - <https://raw.githubusercontent.com/ntex-rs/ntex/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ntex-rs/ntex/HEAD/ntex/Cargo.toml>
  - <https://raw.githubusercontent.com/ntex-rs/ntex/HEAD/ntex/CHANGES.md>
  - <https://raw.githubusercontent.com/ntex-rs/ntex/HEAD/ntex-util/src/time/wheel.rs>
  - <https://github.com/ntex-rs/ntex/issues?q=is%3Aissue+sort%3Aupdated-desc>
  - <https://github.com/ntex-rs/ntex/issues/946>
  - <https://github.com/ntex-rs/ntex/issues/867>
  - <https://github.com/ntex-rs/ntex/issues/1106>
  - <https://github.com/ntex-rs/ntex/issues/932>
  - <https://github.com/rustsec/advisory-db/tree/main/crates/ntex>
  - <https://crates.io/api/v1/crates/ntex>
  - <https://crates.io/api/v1/crates/ntex/2.18.0/dependencies>
  - <https://crates.io/api/v1/crates/ntex-util>
  - <https://crates.io/api/v1/crates/ntex-server>
  - <https://static.crates.io/crates/ntex/ntex-2.18.0.crate>
  - <https://static.crates.io/crates/ntex-util/ntex-util-2.16.0.crate>
  - <https://static.crates.io/crates/ntex-server/ntex-server-2.8.1.crate>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/ntex.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ntex/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ntex/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ntex/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/ntex/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/main.cc>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/tools/gcannon.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/drogonframework/drogon/HEAD/lib/src/Utilities.cc>
  - <https://raw.githubusercontent.com/drogonframework/drogon/HEAD/lib/inc/drogon/HttpAppFramework.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/ntex-rs/ntex`) · [data/wave14/enrich/raw/github_com_ntex_rs_ntex.json](../../../data/wave14/enrich/raw/github_com_ntex_rs_ntex.json) (enrichment confidence 0.8)

</details>
