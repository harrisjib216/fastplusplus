# cpeak (Rust)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Express-style Rust HTTP/1.1 framework on hyper that outruns Drogon, Cutelyst and userver in HttpArena, not nginx or h2o.

| | |
|---|---|
| **Beats** | Drogon (C++) named in the README; userver, hical, Cutelyst (C++) and nginx, h2o, mongoose (C) rows in the same HttpArena tables |
| **Claimed result** | README: 'ranked #1 of 95 frameworks on the HttpArena HTTP/1.1 leaderboard, surpassing Drogon (C++), Vert.x (Java), Bun (TS), Actix Web (Rust) and others'; 2.59 million plain requests per second and 1.28 million JSON responses per second over TLS. HttpArena JSON rows (ratios derived from page data): baseline-4096 2,586,588 vs Drogon 2,022,710 (1.28x), Cutelyst 2,153,860 (1.20x) but nginx 3,284,513 (0.79x); pipelined-4096 14,496,147 vs nginx 4,037,345 (3.59x), Drogon 7,801,404 (1.86x); json-comp-4096 493,187 vs userver 297,311 (1.66x), hical 261,955 (1.88x), Drogon 127,466 (3.87x); async-db-1024 320,543 vs userver 248,628 (1.29x); json-tls-4096 1,284,103 vs nginx 1,313,755 (0.98x), h2o 1,229,462 (1.04x), mongoose 1,102,964 (1.16x). |
| **Workload** | HttpArena profiles on one 64-core machine: baseline (4096 connections), pipelined, json-comp (gzip JSON), json-tls and async-db; cpeak is an Express-style Rust framework on hyper with one single-threaded Tokio event loop per core and sonic-rs JSON. |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine: AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, one NUMA node, 8x DDR4-3200), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (site/data/current.json; site/content/docs/hardware/_index.md). The server container runs with seccomp=unconfined on the cpuset 0-31,64-95 for the H/1.1 profiles and the load generator on CPUs 32-63,96-127 of the same machine over loopback (scripts/lib/framework.sh, scripts/lib/profiles.sh, scripts/lib/common.sh). current.json is undated and describes the machine now, not necessarily at the date of each results file. |
| **Compiler and flags** | cpeak: rust:1.94-bookworm image, cargo build --release with RUSTFLAGS='-C target-cpu=native', [profile.release] codegen-units = 1 and lto = 'thin', cpeak 0.3.0 from crates.io, mimalloc as Cpeak's default allocator (frameworks/cpeak/{Dockerfile,Cargo.toml,README.md}). C/C++ rows: nginx 1.31.4 with a custom C handler module built --with-cc-opt='-O3 -march=native -DNDEBUG' (debian:trixie); h2o pinned commit ccea64b, clang CMake Release -march=native -mtune=native, no LTO; mongoose 7.23 gcc-14 -O3 -march=native -flto; libreactorng pinned 7a65f8b and its server gcc -O3 -march=native; agensio v0.1.0-alpha.23 CMake Release -DAGENSIO_NATIVE=ON; proxygen CMake Release on the pinned facebook/proxygen base image with mimalloc; Drogon CMake Release (handler only) on the unpinned drogonframework/drogon:latest image; userver v3.2 image, CMake Release -march=native; hical gcc-14 CMake Release -march=native -mtune=native (MDA2AV/HttpArena frameworks/&lt;name&gt;/Dockerfile). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Why it wins** | hyper with one single-threaded Tokio event loop per core (no work stealing), sonic-rs JSON and built-in gzip/brotli compression (HttpArena entry description; README says it uses every core out of the box). |
| **Adoption** | 211 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/Cododev-Technology/cpeak) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cpeak.json) |

## Verdict

HttpArena on a 64-core Threadripper PRO 3995WX (server on 32 cores/64 threads, load generator on the rest over loopback), best of 3 runs of 5 s: baseline-4096 2,586,588 req/s vs Drogon 2,022,710 (1.28x) and nginx 3,284,513 (0.79x); json-comp-4096 493,187 vs userver 297,311 (1.66x) and Drogon 127,466 (3.87x); json-tls-4096 1,284,103 vs nginx 1,313,755 (0.98x). Cpeak's rows were saved 2026-10-11 by its author in PR #1547 (a first run 3% higher was not saved) while the C/C++ rows come from runs between 2026-08-30 and 2026-09-11; nginx runs a custom C handler module built -O3 -march=native and Drogon an unpinned drogon:latest image.

## Use it when

- A new Rust HTTP/1.1 JSON API where an Express/Node-style API matters and Drogon-class throughput (about 1.3x Drogon on HttpArena baseline-4096) is enough
- Compressed JSON responses: on HttpArena json-comp-4096 it served 493,187 req/s vs userver 297,311, hical 261,955 and Drogon 127,466 with similar bytes per response
- HTTPS JSON serving on many cores: json-tls-4096 1,284,103 req/s, level with nginx (1,313,755) and h2o (1,229,462)
- Apps that pair a Node.js and a Rust service and want the same routing, cookie-signing and token formats on both sides

## Skip it when

- Maximum plain HTTP/1.1 throughput: at baseline-4096 it is 0.79x nginx and behind h2o, mongoose, hical (3,228,043) and even actix-web (2,775,120) and the raw Tokio entry (4,187,085)
- HTTP/2, HTTP/3 or WebSocket: the crate enables only hyper's http1 feature and has no h2, QUIC or WebSocket rows
- Memory-constrained hosts: HttpArena RSS is 384 MiB at baseline-4096 vs Drogon 147 MiB and h2o 75 MiB, and 1.6 GiB in the 32,000-connection async profile
- CPU-limited deployments: on the 8-CPU latency-500k profile it held only 76.7% of the target rate (383,482 req/s, p99 5.6 s), about Drogon's level and behind mongoose (474,223), hical (429,185) and actix-web (421,612)
- Production systems that need a stable API: the README says 0.x releases are not recommended for production, and the crate has 54 downloads in total

## How it is fast

Thread-per-core: one current-thread Tokio runtime per core, each with its own SO_REUSEPORT listener on Linux (an acceptor thread hands out connections elsewhere), so nothing is shared between workers. A custom AsyncFd socket registers only for readable events (writable interest only when a write would block), responses from pipelined requests are held back and flushed in one write per hyper turn (up to 64 KB), and a background 10 s timer keeps hyper's per-request header timers from forcing an epoll re-arm syscall. JSON is serialized with sonic-rs (SIMD), in-memory bodies are gzip-compressed with libdeflate (a C library) at level 6, the allocator is mimalloc and TLS is rustls on ring.

## Compared with alternatives

Pick it over actix-web when TLS JSON, connection churn (limited-conn-4096 2,118,981 vs 1,135,157 req/s) or an Express-style API matters; actix-web is ahead on plain baseline, pipelined and raw json-comp rps, supports HTTP/2 and WebSocket, and is far more mature. The raw Tokio and C# minima-sync HttpArena entries are faster but are hand-written servers, not frameworks.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio, hyper 1 (http1), hyper-util, socket2, serde/serde_json, sonic-rs, memchr, flate2 (zlib-rs), brotli, libdeflater (C), rustls 0.23 on ring, mimalloc (C, default feature), sha2, hmac, pbkdf2, getrandom, httpdate, regex, libc on unix |
| **Minimum toolchain** | Rust 1.85 (async closures); HttpArena built it with rust 1.94 and -C target-cpu=native |
| **Platforms** | Linux gets one SO_REUSEPORT listener per worker; other unix and non-unix targets fall back to a single acceptor thread; Windows support is not documented |
| **Thread safety** | Route and middleware closures are shared by all worker threads, so captured state must be thread-safe (Arc&lt;Mutex&lt;...&gt;&gt; or a pool); per-request state stays on one worker thread; panics in handlers are routed to handle_err |
| **Drop-in for the baseline** | no |

## Gotchas

- The '#1 of 95' rank is HttpArena's H/1.1 framework board (flagship and emerging types, tuned entries shown); nginx, h2o and the C engines (mongoose, libreactorng, libioma) are on separate infrastructure and engine boards, and hical is experimental, so the rank beats only Drogon, Cutelyst and userver among C/C++ entries. The entry is 'tuned' because the HttpArena maintainer required that mode for sonic-rs, which is not Rust's standard serializer (PR #1547).
- The json-comp lead over the C++ frameworks runs through libdeflate, a C library, at gzip level 6; mimalloc (C) is the global allocator and ring's AES-GCM is BoringSSL-derived assembly, so the json-comp and json-tls wins are not pure-Rust code paths.
- Harness check: the HttpArena /async-db handler answers 200 with an empty item list whenever the Postgres pool, prepare or query fails, which would count failures as 2xx; the saved row averages 1,872 bytes per response vs 1,907-1,928 for userver, hical and actix-web, consistent with Cpeak's roughly 40-byte smaller headers, so the 320,543 req/s row does not look inflated (and async-db is reference-only in the composite).
- Cpeak makes mimalloc the program's #[global_allocator] by default; an app that sets its own allocator must use default-features = false or it will not compile.

## Known shortcomings

- '#1 of 95' is the framework board only (nginx, h2o and C engines ranked separately); 0.79x nginx on baseline; meta mode 'tuned'; pipelined and async-db wins are reference-only; built with RUSTFLAGS target-cpu=native, codegen-units=1 and thin LTO; rows from different runs on the same machine.
- No harness flaw behind the numbers. 'tuned' mode was forced by the HttpArena maintainer for sonic-rs (PR #1547); the json-comp win runs gzip level 6 through libdeflate (C) with the mimalloc (C) allocator. latency-500k-8cpu held only 0.767 of the target rate (383,482 req/s, p99 5.6 s), Drogon level, behind mongoose, hical and actix; RSS 384 MiB against Drogon's 147 at baseline; actix-web is ahead on baseline, pipelined and raw json-comp; HTTP/1.1 only. The Rust code has been public only since 2026-10-11 (crate 54 downloads); /async-db returns 200 with an empty list on DB failure, though bytes per response (1,872 vs 1,907-1,928) say the row is real.

## Caveats and trade-offs

The README's '#1 of 95' (rust/README.md; the root README says '#1') is the HttpArena framework board filtered to flagship and emerging types with tuned entries shown (badge link type=emerging,flagship&tuned=1). nginx, h2o and agensio are 'infrastructure' and mongoose, libreactorng, libioma and proxygen are 'engine' entries, ranked on separate boards, and hical is 'experimental' (hidden by default), so the '#1' beats only the C++ frameworks Drogon, Cutelyst and userver. In the raw rows cpeak is 0.79x nginx at baseline-4096 and 0.81x at limited-conn-4096 (2,118,981 vs 2,626,297), and behind h2o, mongoose, agensio, libreactorng, libioma and hical (3,228,043) at baseline-4096. cpeak's meta.json declares mode 'tuned' (non-default configuration in HttpArena's terms) while the C++ framework entries are 'standard', though the entry README says default configuration. Pipelined and async-db are reference-only in the framework composite; the pipelined ratio vs nginx is mostly nginx's pipelining cost. TLS is rustls on ring, whose AES-GCM is BoringSSL-derived assembly. The cpeak entry was added 2026-10-11 by the cpeak author (meta.json maintainers: agile8118), and the README numbers were added the same day (commit c8fb314); rows come from different runs on the same machine (cpeak.json 2026-10-11, nginx.json and h2o.json 2026-08-30, drogon.json 2026-09-06, userver.json 2026-09-11 per git history). Each number is the best of 3 runs of 5 s. Every entry is a minimal hand-written handler for the same endpoint contract (nginx runs a custom C handler module), baseline-4096 mixes GET and POST with query parsing, and Drogon is built against the unpinned drogonframework/drogon:latest image. The http-arena.com board itself could not be opened here (DNS failure), so the rank is taken from the README. [retier] 'tuned' mode was forced by the HttpArena maintainer for sonic-rs (PR #1547); the json-comp win runs gzip level 6 through libdeflate (C) with the mimalloc (C) allocator. latency-500k-8cpu held only 0.767 of the target rate (p99 5.6 s), Drogon level, behind mongoose, hical and actix; RSS 384 MiB against Drogon's 147 at baseline; actix-web is ahead on baseline, pipelined and raw json-comp; HTTP/1.1 only. Rust code public only since 2026-10-11 (crate 54 downloads).

Rust framework with a Node.js sibling; started as an educational project; HttpArena lists the entry as 'emerging' and 'tuned' mode, so the #1 claim is on the tuned leaderboard filter.

## Maintenance

Very new and active (Rust port public since 2026-10-11, crate 0.3.0, MIT, 211 stars on a repo shared with the Node.js package); copyable, but 0.x with an explicit not-for-production notice, HTTP/1.1 only, and no independent users yet beyond Cododev's own products.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A: every quoted number matches site/data/results/cpeak.json and the sibling drogon/cutelyst/nginx/userver/hical/h2o/mongoose JSON files; the code is public (frameworks/cpeak/{Dockerfile,Cargo.toml,src}, frameworks/drogon/Dockerfile, frameworks/nginx/Dockerfile, scripts/benchmark.sh), toolchains and flags are in the Dockerfiles and Cargo.toml, and the CPU model (Threadripper PRO 3995WX) is in site/data/current.json and the hardware docs, the HttpArena tier-A precedent.
- **Verifier notes:** Numbers verified; tier raised B to A on the HttpArena CPU-model precedent. Corrected compiler_and_flags: the Dockerfile sets RUSTFLAGS='-C target-cpu=native' and Cargo.toml uses codegen-units=1 and thin LTO, so same_opt_level is true. Shortcomings to record: '#1' is the framework board only (nginx, h2o, C engines excluded), 0.79x nginx at baseline and 0.81x at limited-conn, entry declared 'tuned' vs standard C++ entries, wins on pipelined and async-db are reference-only, entry and README numbers both added by the author on 2026-10-11, cross-run rows.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-41 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cpeak.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cutelyst.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hical.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/scoring/composite-score.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/add-framework/meta-json.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cpeak/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cpeak/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cpeak/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cpeak/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/hical/meta.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/cpeak.json>
  - <https://github.com/Cododev-Technology/cpeak>
  - <https://github.com/Cododev-Technology/cpeak/commits>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/README.md>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/README.md>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/Cododev-Technology/cpeak>
  - <https://github.com/Cododev-Technology/cpeak/commits/main>
  - <https://github.com/Cododev-Technology/cpeak/issues?q=is%3Aissue>
  - <https://github.com/Cododev-Technology/cpeak/tree/main/rust/src/internal>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/README.md>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/README.md>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/src/lib.rs>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/src/internal/server.rs>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/src/internal/socket.rs>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/src/internal/json.rs>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/src/internal/compression.rs>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/src/internal/tls.rs>
  - <https://raw.githubusercontent.com/Cododev-Technology/cpeak/HEAD/rust/src/internal/router.rs>
  - <https://crates.io/api/v1/crates/cpeak>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cpeak/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cpeak/Cargo.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cpeak/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cpeak/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/cpeak/src/main.rs>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cpeak.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/hical.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/cutelyst.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/actix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/tokio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/scoring/composite-score.md>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/cpeak>
  - <https://github.com/MDA2AV/HttpArena/pull/1547>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/cododev-technology/cpeak`) · [data/wave14/enrich/raw/github_com_cododev_technology_cpeak.json](../../../data/wave14/enrich/raw/github_com_cododev_technology_cpeak.json) (enrichment confidence 0.8)

</details>
