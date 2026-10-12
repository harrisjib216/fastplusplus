# nilo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig web framework on zio fibers; beats nginx on HttpArena h2/h2c, TLS-JSON and pipelined rows, loses on plain HTTP/1.1.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, -O3 -march=native -DNDEBUG), h2o (C, clang Release -march=native), agensio and proxygen (C++), Drogon and userver (C++) rows in the same suite |
| **Claimed result** | baseline-h2c-256: 9,010,310 req/s vs nginx 2,456,329 (3.67x, derived from page data), proxygen 5,881,888 (1.53x) but agensio 15,185,367 (0.59x). baseline-h2-256: 7,267,874 vs nginx 3,414,750 (2.13x), proxygen 5,845,844 (1.24x), h2o 16,106,978 (0.45x). json-tls-4096: 1,561,927 vs nginx 1,313,755 (1.19x), h2o 1,229,462 (1.27x), Drogon 253,055 (6.2x), agensio 1,716,076 (0.91x). json-comp-4096: 611,376 vs userver 297,311 (2.06x), Drogon 127,466 (4.8x). pipelined-4096: 12,006,230 vs nginx 4,037,345 (2.97x), Drogon 7,801,404 (1.54x), libreactorng 43,424,448 (0.28x). Slower than nginx at baseline-4096: 3,076,550 vs 3,284,513 (0.94x). |
| **Workload** | HttpArena profiles on nilo, a Zig toolkit whose HTTP server runs on zio fibers (io_uring/epoll): h2/h2c baseline, JSON over TLS, gzip JSON, static h2, 16x pipelined, baseline. |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine: AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, one NUMA node, 8x DDR4-3200), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (site/data/current.json; site/content/docs/hardware/_index.md). The server container runs with seccomp=unconfined on the cpuset 0-31,64-95 for the H/1.1 profiles and the load generator on CPUs 32-63,96-127 of the same machine over loopback (scripts/lib/framework.sh, scripts/lib/profiles.sh, scripts/lib/common.sh). current.json is undated and describes the machine now, not necessarily at the date of each results file. |
| **Compiler and flags** | nilo: Zig 0.17.0 (official tarball on alpine:3.20), zig build -Dtarget=x86_64-linux-musl -Dcpu=x86_64_v3+aes+pclmul --release=fast, stripped static binary; build.zig enables nilo's sql, tls (tls.zig), http2 and libdeflate options (frameworks/nilo/Dockerfile, frameworks/nilo/build.zig). C/C++ rows: nginx 1.31.4 with a custom C handler module built --with-cc-opt='-O3 -march=native -DNDEBUG' (debian:trixie); h2o pinned commit ccea64b, clang CMake Release -march=native -mtune=native, no LTO; mongoose 7.23 gcc-14 -O3 -march=native -flto; libreactorng pinned 7a65f8b and its server gcc -O3 -march=native; agensio v0.1.0-alpha.23 CMake Release -DAGENSIO_NATIVE=ON; proxygen CMake Release on the pinned facebook/proxygen base image with mimalloc; Drogon CMake Release (handler only) on the unpinned drogonframework/drogon:latest image; userver v3.2 image, CMake Release -march=native; hical gcc-14 CMake Release -march=native -mtune=native (MDA2AV/HttpArena frameworks/&lt;name&gt;/Dockerfile). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Fibers on io_uring (zio) with one allocation per request and about 4.7 KB per idle connection (nilo README); the h2 and h2c wins over nginx reflect nginx's slower HTTP/2 path in this suite, not language speed. |
| **Adoption** | 7 stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/nevindra/nilo) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nilo.json) |

## Verdict

On HttpArena's Threadripper PRO 3995WX (server on 64 hardware threads, load generator on the other 64 over loopback, best of three 5 s runs), nilo v0.8.0 built with Zig 0.17 --release=fast for x86_64_v3+aes+pclmul served 9.01M req/s at baseline-h2c-256 and 7.27M at baseline-h2-256 versus nginx 1.31.4 (custom C module, -O3 -march=native) at 2.46M and 3.41M, 1.19x nginx on json-tls and 2.97x on pipelined, but 0.94x nginx on plain baseline-4096 and below h2o and agensio on h2 and h2c.

## Use it when

- You are writing a new service in Zig and want routing, typed handlers, OpenAPI, Postgres/SQLite and TLS in one dependency tree with no C toolchain (libdeflate is the only optional C piece).
- HTTP/2 or h2c-heavy internal APIs or unary gRPC on one port: nilo served 9.01M req/s at baseline-h2c-256 against nginx 2.46M and proxygen 5.88M, and 7.27M at baseline-h2-256 against nginx 3.41M.
- JSON over TLS 1.3 without a terminating proxy, on CPUs with AES-NI and PCLMUL: 1.56M req/s at json-tls-4096 against nginx 1.31M and h2o 1.23M.
- WebSocket echo services: 4.11M msg/s at echo-ws-512, level with mongoose (3.95M) and ahead of proxygen (3.18M).
- Linux deployments where a few MiB of idle RSS matters (author measures 4,669 bytes per idle connection after its pages are returned).

## Skip it when

- Peak plain HTTP/1.1 throughput: baseline-4096 is 3.08M req/s, 0.94x nginx and 0.70x libreactorng; limited-conn-4096 is 0.88x nginx; h2o and agensio serve h2/h2c at about twice nilo's rate.
- Many concurrent HTTP/2 static downloads: static-h2 fell from 862K req/s at 256 connections to 202K at 1,024 (0.25x nginx, 0.14x agensio) while RSS reached 0.7-1.4 GiB; a database-bound handler did 0.28x userver on async-db.
- Fixed-rate load on few cores: latency-500k-8cpu delivered only 88% of the offered 500K req/s with a 1.16 s mean latency, where libreactorng and mongoose held 0.99 and 0.95 of it.
- You need stability: pre-1.0 (v0.8.0), 8 stars, a single maintainer, forty upgrade-affecting entries in v0.8.0 and seventy-one in v0.7.0, and it pins zio main plus forks of pg.zig and tls.zig rather than tagged releases.
- Windows servers (WSL2 only per decided.md), HTTP/3, templates, streaming gRPC, WebSocket over HTTP/2, or state shared across instances outside the database.

## How it is fast

Each connection runs as a stackful coroutine on lalinsky's zio runtime (io_uring with epoll fallback on Linux), pinned to the executor thread it was dealt to with no work stealing (ADR 199), and every executor runs its own accept fiber (ADR 200, which took short-lived-connection throughput from about 0.66M to 1.97M req/s on the author's 8-core box). A request does one arena allocation, which a test enforces, and idle connections hand their buffer pages back. The author's own profile puts nilo's code at about 181 ns, roughly 4% of a served request's CPU, with the kernel's socket path as the rest, so the HttpArena wins over nginx come mostly from nginx's slower HTTP/2 path and from the thread-per-core fiber design, not from Zig codegen.

## Compared with alternatives

Pick nilo over zix, zeemo or libxev (each about 4.4M req/s at baseline-4096 against nilo's 3.08M) when you need HTTP/2, unary gRPC, TLS and a SQL layer in the same Zig framework rather than the fastest HTTP/1.1 path; if raw h2c rate is the goal, the vanilla (V) entry reached 15.6M req/s on baseline-h2c-256 against nilo's 9.0M.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | zio (lalinsky/zio, pinned main commit) for plain HTTP; behind build flags: pg.zig and zqlite (bundles SQLite) for nilo_sql, a tls.zig fork for TLS 1.3, libdeflate (C) for gzip |
| **Minimum toolchain** | Zig 0.17.0 for v0.8.0 (v0.7.0 and earlier need Zig 0.16.0) |
| **Platforms** | Linux x86_64 and aarch64 (io_uring with epoll fallback), macOS via kqueue; Windows only for four loop-free modules, servers under WSL2. TLS needs -Dcpu with aes+pclmul (x86_64) or aes+sha2 (aarch64), or AES-GCM runs about 70x slower |
| **Thread safety** | One executor thread per core by default; a connection and its handler stay on one OS thread across every wait, so per-request state needs no locks, while shared services need nilo.Mutex unless threads = 1 |
| **Drop-in for the baseline** | no |

## Gotchas

- The json-comp lead (2.06x userver, 4.8x Drogon) runs libdeflate, a C library, through nilo's -Dlibdeflate flag; nginx, h2o and agensio do not run that profile, so it compares only against C++ frameworks.
- Throughput rows come from different HttpArena runs (nilo.json 2026-10-11 against nginx and h2o rows from 2026-08-30), and the author's bench/result/http.md shows several framework changes (Date header, 4,096 backlog, no stealing, one acceptor per executor) made in response to earlier HttpArena readings; the pinned scheduling doubled saturated p50 at baseline-4096 and pushed pipelined p99.9 past 1 s in its own before/after table.
- The README's 4,669 bytes per connection is an idle connection; the author measures about 29.5 KiB per active connection (483 MiB over 16,384 WebSockets), and json-tls-4096 shows a 309 ms p99 against a 3.1 ms mean.
- The README throughput figure (1,401,412 req/s on four cores) and its p99 table come from nilo's own harness against Zig, Rust, Go, Node and Bun servers only; HttpArena is the only C/C++ comparison. The entry's handlers use the documented API (standard mode) and do the JSON arithmetic and compression per request; no shortcut was found in frameworks/nilo/src/main.zig.

## Known shortcomings

- HttpArena rows: behind nginx on baseline (0.94x), limited-conn (0.88x) and static-h2 (0.25x); h2o and agensio ahead on h2/h2c; the json-comp win comes from libdeflate (C). Entry maintained by the nilo author; best of 3 runs; rows from different runs on the same machine (entries Sep-Oct vs nginx/h2o 2026-08-30).
- Entry handlers are clean (standard mode, JSON math and gzip per request, no shortcut in frameworks/nilo/src/main.zig). static-h2 drops from 862K to 202K req/s at 1,024 connections (0.25x nginx); latency-500k-8cpu delivers 88% of the rate with a 1.16 s mean; async-db is 0.28x userver; json-tls p99 is 309 ms against a 3.1 ms mean; the author's own bench/result/http.md admits about 29.5 KiB per active connection, not 4,669 bytes; several framework ADRs (197-200) were tuned after HttpArena readings. Pins zio main plus pg.zig and tls.zig forks.

## Caveats and trade-offs

Mixed result: wins over nginx on the h2/h2c, TLS-JSON and pipelined profiles, but h2o and agensio are clearly ahead on h2 and h2c, the plain HTTP/1.1 baseline-4096 is 0.94x nginx and below h2o, mongoose, libreactorng, libioma and agensio, limited-conn-4096 is 0.88x nginx (2,301,647 vs 2,626,297), and static-h2-1024 is 0.25x nginx. The json-comp win is not Zig's: the entry's build.zig switches nilo's gzip to libdeflate, a C library (ADR 248), while the C++ rows compress with their own stacks; nginx, h2o and agensio do not run json-comp, so that profile compares only against the C++ frameworks userver, Drogon, hical and proxygen. TLS, by contrast, is tls.zig (pure Zig AES-GCM, needs the +aes+pclmul CPU flags). The README's '#2 of 79' is the framework board among untuned entries (nilo is type 'experimental'); nginx, h2o and agensio are 'infrastructure' and mongoose, libreactorng, libioma and proxygen are 'engine' entries, ranked on separate boards. The README's 1,401,412 req/s on four cores comes from nilo's own docs/comparison.md harness (Ryzen 7 9700X), which compares only Zig, Rust, Go, Node and Bun servers, no C/C++. Each HttpArena number is the best of 3 runs of 5 s (scripts/lib/common.sh RUNS=3, scripts/benchmark.sh), and rows come from different runs on the same machine: nilo.json was last written 2026-10-11 (PR #1539 by the nilo author), nginx.json and h2o.json 2026-08-30, drogon.json 2026-09-06, userver.json 2026-09-11 (git history). The nilo entry is maintained by the nilo author (meta.json maintainers: nevindra). The C competitor entries (nginx with a custom C handler module, libreactorng, libioma, h2o, mongoose) are minimal hand-written handlers built by the suite maintainers or contributors; the Drogon entry builds only its handler against the unpinned drogonframework/drogon:latest image, so the Drogon ratios are weaker evidence than the nginx and h2o ratios. Bytes per response differ (derived from page data, bandwidth divided by req/s at baseline-4096): nilo, h2o, cpeak and kestrel 98.2, nginx 135.4, Drogon 134.4, libreactorng 108.7, libioma 85.8, mongoose 72.5. Pipelined (16x batched) and async-db are reference-only in HttpArena's framework composite score (site/content/docs/scoring/composite-score.md). 7 stars, released v0.8.0. [retier] Entry handlers are clean (standard mode, JSON math and gzip per request). static-h2 drops from 862K to 202K req/s at 1,024 connections (0.25x nginx); latency-500k-8cpu delivers 88% of the rate with a 1.16 s mean; async-db is 0.28x userver; json-tls p99 is 309 ms against a 3.1 ms mean; the author's own bench/result/http.md admits about 29.5 KiB per active connection. Several framework ADRs (197-200) were tuned after HttpArena readings; pins zio main plus pg.zig and tls.zig forks.

Experimental Zig 0.17 toolkit (HTTP/1.1, h2, gRPC, TLS, OpenAPI, Postgres); HTTP/3 not supported; HttpArena marks the entry experimental.

## Maintenance

Very active single-maintainer MIT project (504 commits, 15 of them on 2026-10-12 alone, v0.8.0 tag, 8 stars) whose author also maintains its HttpArena entry; fine to depend on for a Zig service, but expect breaking changes each release and untagged upstream pins.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Every nilo number and every ratio matches site/data/results/nilo.json and the sibling nginx/h2o/proxygen/agensio/drogon/userver/libreactorng JSON files in MDA2AV/HttpArena; the benchmark code is public (frameworks/nilo/{Dockerfile,build.zig,src/main.zig}, frameworks/nginx/Dockerfile, frameworks/h2o/Dockerfile, scripts/benchmark.sh, scripts/lib/profiles.sh), compilers and flags for both sides are in the Dockerfiles, and the CPU model (Threadripper PRO 3995WX) is in site/data/current.json and the hardware docs, the HttpArena tier-A precedent (wtx, cutelyst, actix, dusty, libxev, ntex).
- **Verifier notes:** All quoted numbers and ratios verified against the HttpArena JSON files; tier A kept on the HttpArena precedent. Corrected: runs are best of 3, not one; bytes per response for nilo is 98.2, not 62.9; same_algorithm set false because json-comp gzip is libdeflate (C) and the stacks differ. Shortcomings to record: behind nginx on baseline, limited-conn and static-h2, behind h2o and agensio on h2/h2c, json-comp win is libdeflate and only against C++ frameworks, pipelined reference-only, cross-run rows (nilo 2026-10-11 vs nginx 2026-08-30), entry maintained by the nilo author, 7 stars.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-41 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nilo.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/scoring/composite-score.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/add-framework/meta-json.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/framework.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nilo/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nilo/build.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nilo/src/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nilo/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/h2o/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/userver/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/proxygen/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/mongoose/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nilo.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/h2o.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/drogon.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/userver.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/nilo>
  - <https://github.com/nevindra/nilo>
  - <https://github.com/nevindra/nilo/commits>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/README.md>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/docs/comparison.md>
- **Sources the enricher read:**
  - <https://github.com/nevindra/nilo>
  - <https://github.com/nevindra/nilo/commits>
  - <https://github.com/nevindra/nilo/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/README.md>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/docs/comparison.md>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/bench/result/http.md>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/docs/decided.md>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/docs/guide/deploying.md>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/build.zig>
  - <https://raw.githubusercontent.com/nevindra/nilo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lalinsky/zio/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nilo/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nilo/build.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nilo/build.zig.zon>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nilo/src/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nilo/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nilo.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/nevindra/nilo`) · [data/wave14/enrich/raw/github_com_nevindra_nilo.json](../../../data/wave14/enrich/raw/github_com_nevindra_nilo.json) (enrichment confidence 0.64)

</details>
