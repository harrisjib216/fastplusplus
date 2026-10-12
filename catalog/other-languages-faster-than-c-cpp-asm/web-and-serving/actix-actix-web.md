# actix-web

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Full-featured Rust HTTP/1.1 and HTTP/2 web framework; in HttpArena it beats Drogon and Cutelyst (C++) but trails nginx and h2o.

| | |
|---|---|
| **Beats** | Drogon (C++) in the HttpArena suite; nginx (C) in two other benchmarks, with mixed results |
| **Claimed result** | baseline-4096: 2,775,120 req/s vs Drogon 2,022,710 (1.37x, derived from page data) and Cutelyst (C++) 2,153,860 (1.29x); behind nginx 3,284,513 and h2o 3,641,609. pipelined-4096: 16,338,425 vs Drogon 7,801,404 and nginx 4,037,345. |
| **Workload** | HttpArena baseline profile (mixed GET/POST with query parsing, 4096 connections, 64-core machine), actix-web 4 flagship entry in standard configuration. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, single NUMA node), 251 GiB RAM, Ubuntu 24.04.4, kernel 6.17.0-22, Docker 29.3.0 (runc), performance governor (site/data/current.json; site/content/docs/hardware/_index.md). Server container and the gcannon/h2load load generator are pinned to separate halves of the same machine (load generator on CPUs 32-63,96-127) and talk over loopback with MTU 1500; 5 s runs, best of 3 (scripts/lib/common.sh, scripts/benchmark.sh). |
| **Compiler and flags** | actix: rust:1.94 image, RUSTFLAGS='-C target-cpu=native' cargo build --release with release profile opt-level=3, codegen-units=1, lto='thin', panic='abort'; actix-web pinned to unreleased git rev 67490f9e, rustls 0.23 with ring for TLS (frameworks/actix/Dockerfile, Cargo.toml). Drogon: unpinned drogonframework/drogon:latest image, app built with CMake Release (C++20), libjemalloc preloaded, no -march=native or LTO (frameworks/drogon). Cutelyst: CMake Release. nginx 1.31.4: -O3 -march=native -DNDEBUG with a custom C handler module. h2o: clang Release with -march=native -mtune=native, no LTO. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 24.9k stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/actix/actix-web) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/actix.json) |

## Verdict

HttpArena (Threadripper PRO 3995WX, 64 cores, server and gcannon load generator pinned to separate halves, loopback, 5 s runs, best of 3) gives actix-web 2,775,120 req/s on baseline-4096, against Drogon 2,022,710 (1.37x, derived from page data) and Cutelyst 2,153,860 (1.29x). It is behind nginx 3,284,513 and h2o 3,641,609. pipelined-4096 gives 16,338,425 vs Drogon 7,801,404 and nginx 4,037,345, but that profile is reference-only. Actix was built with rustc 1.94, target-cpu=native and thin LTO; Drogon used drogonframework/drogon:latest with CMake Release and jemalloc preloaded but no -march=native.

## Use it when

- Rust services that want a full framework (extractors, middleware, rustls TLS, WebSockets) and keep-alive throughput in the C++-framework class: HttpArena baseline-4096 gives 2,775,120 req/s vs Drogon 2,022,710 and Cutelyst 2,153,860 on a 64-core Threadripper PRO 3995WX.
- JSON APIs over TLS on HTTP/1.1, where actix reaches 1,157,219 req/s at json-tls-4096, against Drogon 253,055 and nginx 1,313,755.
- Many concurrent slow or parked requests: async-32000 runs at 2,112,168 req/s with 1,009 MiB RSS, against Drogon 143,001.
- WebSocket echo or pipelined HTTP/1.1 traffic (echo-ws 3.2-3.4M msg/s, echo-ws-pipeline 37.7-43.7M).
- HTTP/2 over TLS at moderate connection counts: baseline-h2-256 gives 3,884,214 req/s vs nginx 3,414,750, though it falls behind nginx at 1024 connections (3,056,936 vs 3,320,285).

## Skip it when

- Maximum plain HTTP/1.1 req/s: on the same board nginx (3,284,513), h2o (3,641,609), the raw tokio entry (4,187,085) and libreactorng (4,377,377) are all faster at baseline-4096.
- Serving static files at scale through actix-files: static-tls-1024 reaches 55,882 req/s at 4.6 GiB RSS against nginx 720,869, and static-h2 reaches 51,989-64,019 req/s at 11.2-37.0 GiB RSS with p99 latency of 1.58-2.64 s against nginx 796,607-802,090. Put a C server or CDN in front.
- Connection-churn traffic. On limited-conn-4096 (10 requests per connection) it reaches 1,135,157 req/s using about 46 of 64 cores, behind Drogon 1,694,883, Cutelyst 1,736,401 and nginx 2,626,297; the single acceptor thread is the likely limit (inferred, not profiled).
- As evidence that Rust beats C or C++ in general: this is one framework against another, Drogon is built from an unpinned image without -march=native while actix gets target-cpu=native, and the rows come from separate runs.

## How it is fast

actix-server runs one acceptor thread (actix-net accept.rs) that hands sockets round-robin to per-core workers. Each worker owns its own App instance, so the hot path needs no cross-thread locks. actix-http parses and serializes HTTP/1 into reused buffers and supports pipelining, which is why the reference-only pipelined profile reaches 16.3M req/s. The HttpArena entry is built with rustc 1.94, -C target-cpu=native, thin LTO, codegen-units=1 and panic=abort.

## Compared with alternatives

Pick actix-web over the raw tokio, tokio-uring, cpeak or zix HttpArena entries when you need a maintained full framework rather than a minimal benchmark server; those siblings post 3.5-4.4M req/s at baseline-4096 but are not general-purpose frameworks. Over ntex (2,168,712 at baseline-4096), pick it for the larger ecosystem (24.9k stars, about 85M downloads) and the higher baseline score.

## Integration

| | |
|---|---|
| **Form** | crate (actix-web 4.15.0 on crates.io; workspace also ships actix-http, actix-router, actix-files, awc) |
| **Dependencies** | tokio, actix-rt, actix-server, actix-service, actix-codec, actix-http, actix-router, bytes, serde, serde_json, serde_urlencoded, url, http types; optional rustls or openssl, brotli/flate2/zstd for compression, cookie |
| **Minimum toolchain** | Rust 1.88 (MSRV since 4.13.0) |
| **Platforms** | Any tokio target (Linux, macOS, Windows; 4.14.0 added dual-stack IPv6 sockets on Windows); x86-64 and aarch64 |
| **Thread safety** | Multi-worker server: the worker count defaults to std::thread::available_parallelism, the App factory is instantiated at least once per worker, and shared state goes in web::Data (Arc). Each worker has its own blocking pool, defaulting to 512 / available_parallelism threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- The HttpArena json-comp win (541,211 vs Drogon 127,466 req/s) does not measure actix-web's Compress middleware. The entry gzips in the handler with flate2 level 1 because actix-http's encoder compresses in place only below 1 KiB (MAX_CHUNK_SIZE_ENCODE_IN_PLACE) and sends larger bodies to spawn_blocking. The entry's own comment says the stock path sat at 66% CPU at 12k req/s. Its meta.json still describes json-comp as handled by the Compress middleware, so stock Compress on 2-6 KB JSON bodies will be much slower.
- TCP_NODELAY is left at the OS default. Issue #3841 measured HTTP/2 over rustls at 41.45 ms per request against 0.14 ms on HTTP/1.1, caused by Nagle's algorithm. 4.13.0 added an HttpServer method to set TCP_NODELAY, but the default stays off until a major release, so set it yourself for latency-sensitive HTTP/2.
- The defaults cap load per worker: 25k concurrent connections, 256 concurrent TLS handshakes, a backlog of 1024, a 5 s keep-alive and a 5000 ms client request timeout (408 on slow headers). High-fan-in or slow-client deployments need tuning.
- The HttpArena entry runs an unreleased main revision (67490f9e) to get actix-files try_compressed(), so the static rows do not match the crates.io release. Past advisories: RUSTSEC-2020-0048 (use-after-free in BodyStream, CVE-2020-35901) and RUSTSEC-2021-0081 (HTTP/1 request smuggling, CVE-2021-38512, patched in 2.2.1 and 3.0.0-beta.9); both predate the 4.x series.

## Known shortcomings

- At HttpArena baseline-4096 beats only Drogon and Cutelyst of nine C/C++ entries, loses to both at limited-conn-4096, and sits behind nginx on scored HTTP/1.1, TLS and static; the pipelined row is reference-only; the Drogon image is unpinned and built without -march=native.
- The HttpArena json-comp win (541,211 vs Drogon 127,466 req/s) gzips in the handler with flate2 level 1, bypassing the Compress middleware (the stock path sends bodies over 1 KiB to spawn_blocking); its meta.json says otherwise. TCP_NODELAY is off by default (issue #3841: HTTP/2 41.45 ms vs 0.14 ms per request); actix-files static-h2 reached 11-37 GiB RSS; behind nginx at limited-conn (one acceptor thread, inferred, not profiled); baseline-h2-256 beats nginx (3,884,214 vs 3,414,750) but trails at 1024 connections.

## Caveats and trade-offs

Mixed against C and C++ on the same board. At baseline-4096 actix (2,775,120) beats only Drogon (2,022,710) and Cutelyst (2,153,860) among nine C/C++ entries; it trails nginx 3,284,513, h2o 3,641,609, mongoose 3,707,598, agensio (C++) 3,558,559, hical (C++) 3,228,043, libreactorng 4,377,377 and libioma 4,255,834. At limited-conn-4096 it is behind Drogon and Cutelyst too (1,135,157 vs 1,694,883 and 1,736,401) and far behind nginx 2,626,297. json-tls: 1,157,219 vs nginx 1,313,755, h2o 1,229,462 and agensio 1,716,076 (ahead of Drogon 253,055 and mongoose 1,102,964). static-tls 55,882 and static-h2 51,989-64,019 vs nginx 720,869 and 796,607-802,090. Wins over Drogon also on json-comp (541,211 vs 127,466, where Drogon's jsoncpp allocation churn dominates), async-32000 (Drogon entry runs every delay timer on one loop, per wave 5) and fixed-rate CPU per request (latency-1m 24.9 vs 32.1 us). pipelined-4096 (16,338,425 vs Drogon 7,801,404 and nginx 4,037,345) is a reference-only profile excluded from HttpArena's composite score. actix.json still carries baseline-h2c/json-h2c rows although actix's meta.json no longer subscribes to them (stale). Rows come from separate runs on the same machine (actix last saved 2026-09-06, Drogon 2026-09-06, nginx 2026-08-30); the actix entry runs an unreleased actix-web git revision; Drogon is built from an unpinned image without -march=native while actix gets target-cpu=native and thin LTO; handlers are minimal (nginx is a custom C module). Third-party swerver-benchmarks (Docker Desktop on Apple Silicon, 2 CPUs) has actix 133,691 vs nginx 118,061 req/s, while statico's README has nginx ahead (832,082 vs 798,809 at four threads, 286,960 vs 213,756 at one). [retier] Mixed against C and C++ on the same board. At baseline-4096 actix (2,775,120) beats only Drogon (2,022,710) and Cutelyst (2,153,860) among nine C/C++ entries and trails nginx 3,284,513, h2o 3,641,609, mongoose 3,707,598, agensio 3,558,559, hical 3,228,043, libreactorng 4,377,377 and libioma 4,255,834; at limited-conn-4096 it is behind Drogon, Cutelyst and nginx (1,135,157 vs 2,626,297; one acceptor thread is the inferred cause, not profiled); baseline-h2-256 beats nginx (3,884,214 vs 3,414,750) but trails at 1024 connections. The json-comp win (541,211 vs Drogon 127,466 req/s) gzips in the handler with flate2 level 1, bypassing actix-web's Compress middleware (whose stock path sends bodies over 1 KiB to spawn_blocking); the entry's meta.json says otherwise. TCP_NODELAY is off by default (issue #3841: HTTP/2 41.45 ms vs 0.14 ms per request); actix-files static-h2 reached 11-37 GiB RSS.

Full-featured framework (routing, middleware, rustls TLS, actix-files); the actix-web README only says it is among the fastest per TechEmpower, with no numbers.

## Maintenance

Actively maintained: 4.15.0 released 2026-08-21, 5,221 commits, 24.9k stars, about 85M crates.io downloads, dual MIT OR Apache-2.0, 145 open issues. Production-grade and copyable as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A: the numbers match site/data/results/actix.json and the sibling drogon/cutelyst/nginx/h2o JSON files in MDA2AV/HttpArena, the benchmark code is public (frameworks/actix/{Dockerfile,Cargo.toml}, frameworks/drogon/{Dockerfile,CMakeLists.txt,main.cc}, frameworks/nginx/{Dockerfile,nginx.conf}, scripts/benchmark.sh, scripts/lib/common.sh), toolchains and flags are in the Dockerfiles, and the CPU model (Threadripper PRO 3995WX) is in site/data/current.json and the hardware docs, the same basis on which wave 5 kept wtx and Cutelyst at A on this harness.
- **Verifier notes:** Tier upgraded to A (CPU model is published in HttpArena's current.json and hardware docs); all quoted numbers verified. Shortcomings to record: beats only Drogon and Cutelyst of nine C/C++ entries at baseline-4096 and loses to both at limited-conn-4096; behind nginx on the scored H/1.1, TLS and static profiles; pipelined win is reference-only; Drogon built without -march=native/LTO from an unpinned image; framework-vs-framework, not a language-level win.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-16 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/actix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cutelyst.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hical.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/framework.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/actix/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/actix/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/actix/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/main.cc>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/main/frameworks/drogon/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/h2o/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/actix.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/drogon.json>
  - <https://github.com/actix/actix-web>
  - <https://github.com/actix/actix-web/commits>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/awgn/statico/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/actix/actix-web/HEAD/actix-web/README.md>
  - <https://raw.githubusercontent.com/actix/actix-web/HEAD/actix-web/Cargo.toml>
  - <https://raw.githubusercontent.com/actix/actix-web/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/actix/actix-web/HEAD/actix-web/CHANGES.md>
  - <https://raw.githubusercontent.com/actix/actix-web/HEAD/actix-http/Cargo.toml>
  - <https://raw.githubusercontent.com/actix/actix-web/HEAD/actix-http/src/encoding/encoder.rs>
  - <https://raw.githubusercontent.com/actix/actix-web/HEAD/actix-web/src/server.rs>
  - <https://raw.githubusercontent.com/actix/actix-net/HEAD/actix-server/src/accept.rs>
  - <https://github.com/actix/actix-web>
  - <https://github.com/actix/actix-web/commit/67490f9e75d3262446449481c510e5ab36c9bcfa>
  - <https://github.com/actix/actix-web/issues?q=is%3Aissue+is%3Aopen+label%3AC-perf>
  - <https://github.com/actix/actix-web/issues?q=is%3Aissue+performance+sort%3Aupdated-desc>
  - <https://github.com/actix/actix-web/issues/3444>
  - <https://github.com/actix/actix-web/issues/3841>
  - <https://crates.io/api/v1/crates/actix-web>
  - <https://github.com/rustsec/advisory-db/tree/main/crates/actix-http>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/actix-http/RUSTSEC-2021-0081.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/actix-http/RUSTSEC-2020-0048.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/actix/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/actix/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/actix/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/actix/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/main.cc>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/actix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/actix/actix-web`) · [data/wave14/enrich/raw/github_com_actix_actix_web.json](../../../data/wave14/enrich/raw/github_com_actix_actix_web.json) (enrichment confidence 0.8)

</details>
