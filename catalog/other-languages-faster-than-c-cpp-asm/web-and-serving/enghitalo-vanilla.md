# vanilla (V HTTP server)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `V` · `MIT` · 🟢 active

> V-language HTTP/1.1 and h2c server engine on raw io_uring/epoll; about 1.31x nginx on HttpArena baseline, level with libreactorng.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, -O3 -march=native -DNDEBUG); same suite rows for libreactorng, libioma, h2o, mongoose (C) and Drogon, agensio, userver (C++) |
| **Claimed result** | baseline-4096 (vanilla-io_uring): 4,307,987 req/s vs nginx 3,284,513 (1.31x), h2o 3,641,609 (1.18x), mongoose 3,707,598 (1.16x), libioma 4,255,834 (1.01x), Drogon 2,022,710 (2.13x), but libreactorng 4,377,377 is ahead (0.98x). limited-conn-4096: 2,685,418 vs nginx 2,626,297 (1.02x), libreactorng 2,685,717 (1.00x), libioma 2,707,029 (0.99x). pipelined-4096 (reference-only): 43,693,484 vs libreactorng 43,424,448 (1.01x), nginx 4,037,345 (10.8x). json-tls-4096: 1,533,275 vs nginx 1,313,755 (1.17x), h2o 1,229,462 (1.25x), but agensio (C++) 1,716,076 is ahead (0.89x). static-tls-1024 (reference-only): 1,112,233 vs nginx 720,869 (1.54x), mongoose 611,058 (1.82x), but agensio 1,191,970 is ahead (0.93x). baseline-h2c-256 (vanilla-epoll entry): 15,623,717 vs agensio 15,185,367 (1.03x), proxygen 5,881,888 (2.66x), nginx 2,456,329 (6.4x). All ratios derived from page data. The json-comp-4096 rows (2,862,233 vs userver 297,311 and Drogon 127,466) are not valid evidence: vanilla compresses once per (count, m) pair and then serves the cached gzipped response bytes, while the C++ rows serialize and compress per request. |
| **Workload** | HttpArena profiles on vanilla, a multi-threaded, lock-free, copy-free HTTP server written in V (io_uring entry and epoll entry): baseline (mixed GET/POST, 4096 connections), 16x pipelined, limited-conn, JSON over TLS, gzip JSON, static over TLS, h2c. |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine: AMD Ryzen Threadripper PRO 3995WX (Zen 2, 64 cores / 128 threads, one NUMA node), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), performance governor (site/data/current.json, site/content/docs/hardware/_index.md). The server container is pinned to cpuset 0-31,64-95 (32 cores / 64 threads) for these profiles and the load generator (gcannon for HTTP/1.1, wrk for the TLS profiles, h2load for h2c) runs on the other half over loopback; 5 s runs, best of 3 (scripts/lib/common.sh RUNS=3, scripts/lib/profiles.sh). current.json is undated and describes the machine now, not necessarily at the date of each results file. |
| **Compiler and flags** | vanilla-io_uring: V pinned master b99970bd (0.5.2) built from source on debian:stable-slim, v -prod -d vanilla_tls with the default (Boehm) GC; V's -prod passes -O3 and -flto (-O2 for a generated C unit of 8 MiB or more, no -flto with -parallel-cc) to the system C compiler, gcc from build-essential, without -march=native (v3_prod_c_optimization_flags in vlib/v/driver/driver.v at b99970bd); vanilla library pinned at 3dd5a79; Mbed TLS 4.1.0 built -O3 -march=native -DNDEBUG with a local RSA-sign-cache patch; gzip is V's compress.gzip, which wraps miniz (C) (frameworks/vanilla-io_uring/Dockerfile, vlib/compress/compress.c.v). vanilla-epoll (h2c row): same toolchain with v -prod -gc none (no garbage collector, nothing is freed). C/C++ rows: nginx 1.31.4 with a custom C handler module, --with-cc-opt='-O3 -march=native -DNDEBUG' (debian:trixie); libreactorng 7a65f8b configured CFLAGS='-O3 -march=native' and its server built gcc -O3 -march=native (no LTO); libioma and mongoose gcc-14 -O3 -march=native -flto; h2o clang CMake Release -march=native -mtune=native, no LTO; agensio CMake Release -DAGENSIO_NATIVE=ON; userver service CMake Release -march=native on the prebuilt userver v3.2 image; Drogon handler only, CMake Release on the unpinned drogonframework/drogon:latest image (MDA2AV/HttpArena frameworks/&lt;name&gt;/Dockerfile). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | io_uring async runtime, one worker per CPU with SO_REUSEPORT, lock-free copy-free handlers returning raw response bytes, JSON built in a single allocation with precomputed prefixes (HttpArena meta.json); no language-level reason is claimed. |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-12 |
| **Links** | [repository](https://github.com/enghitalo/vanilla) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/vanilla-io_uring.json) |

## Verdict

In HttpArena on a Threadripper PRO 3995WX with the server limited to 32 cores / 64 threads (best of three 5 s runs, load generator on the other half), vanilla's io_uring entry (V master b99970bd, -prod, so gcc -O3 -flto without -march=native) served 4.31M req/s at baseline-4096 against 3.28M for nginx 1.31.4 with a custom C module at -O3 -march=native (1.31x), 1.17x nginx on JSON over TLS, but 0.98x libreactorng and 0.89x agensio on those profiles; its json-comp lead is invalid because responses are cached.

## Use it when

- You write V and need a Linux HTTP/1.1 server near the top of HttpArena: the io_uring entry served 4,307,987 req/s at baseline-4096 (nginx with a custom C module 3,284,513; libreactorng 4,377,377; libioma 4,255,834).
- Prior-knowledge h2c serving: the epoll build reached 15,623,717 req/s at baseline-h2c-256 against agensio (C++) 15,185,367, proxygen 5,881,888 and nginx 2,456,329.
- Handlers that must wait on other sockets without blocking a worker, e.g. Postgres via pg_async with cross-request pipelining or upstream HTTPS calls via http1_1.upstream.
- Local services that talk over unix domain sockets, with SO_PEERCRED identity checks.

## Skip it when

- You need request validation out of the box: the core framer passes malformed field lines (obs-fold, space before colon, empty names) to every handler and never honours a client's Connection: close or HTTP/1.0 close default (open issues #311 and #310); only the conformance example validates.
- TLS on io_uring, kqueue or IOCP, or HTTP/2 over TLS: TLS exists only on the epoll backend and ALPN h2 is open (#142); kqueue does not enforce timeouts or max_connections (#154).
- Memory-constrained hosts: the HttpArena vanilla entries ran at about 640-990 MiB RSS versus about 100 MiB for the C entries, and a -gc none build never frees anything a handler allocates.
- You need a stable toolchain: it builds against pinned V master commits, has no tagged release (v.mod 0.0.1), and HttpArena disabled its V entries on 2026-08-24 when they stopped building.
- Raw scored-profile throughput is the only criterion: zix, zeemo, minima-sync, libxev and libreactorng all edge it at baseline-4096.

## How it is fast

One worker per CPU, each with its own event loop and lock-free per-worker state (the epoll backend still hands accepted fds out from one central accept thread); the io_uring backend drives the ring through raw syscalls with SINGLE_ISSUER|DEFER_TASKRUN, one submit_and_wait per batch, multishot accept and recv-at-offset framing, and both backends batch pipelined responses into a single send. Requests are framed by scanning only Content-Length and Transfer-Encoding, routing reads the request line as zero-copy slices, and handlers append precomputed byte literals plus in-place integer formatting so the hot path does no heap allocation (the author's PERF_GAP_ANALYSIS.md attributes the big HttpArena gains to removing per-request allocation under V's GC).

## Compared with alternatives

Among HttpArena siblings, zix (4.44M), zeemo (4.42M), minima-sync (4.39M) and libxev (4.38M) beat vanilla's 4.31M at baseline-4096 while the raw tokio entry (4.19M) and ioxide (4.11M) trail it; pick vanilla when your code is in V and you want a batteries-included engine (kTLS, h2c, WebSocket, async Postgres) whose h2c row leads nilo (9.0M) and agensio (15.2M).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none on Linux for plain HTTP (raw io_uring syscalls, no liburing; links only libc and libm per the README); Mbed TLS 4.x when built with -d vanilla_tls |
| **Minimum toolchain** | Recent V master (HttpArena pins V b99970bd; the README cites a pinned V master build for its upstream fixes); no tagged V version documented |
| **Platforms** | Linux (epoll, io_uring, poll), macOS (kqueue, with timeout and limit gaps), Windows (IOCP, no TLS or suspend reactor yet) |
| **Thread safety** | One worker thread per CPU; each handler call gets its worker's own state and output buffer, so per-worker data needs no locks; state shared across workers must be synchronised by the application (the HttpArena entry guards its shared caches with a mutex) |
| **Drop-in for the baseline** | no |

## Gotchas

- Several HttpArena rows lean on benchmark-shaped handlers: /pipeline matches the raw prefix 'GET /pipeline ' and copies a constant response without parsing the request (the 43.7M req/s pipelined row, a reference-only profile), json-comp replays cached gzip responses per (count, m) (invalid evidence), json-tls renders item JSON prefixes once at startup, and responses carry no Date header (nginx sends one).
- Part of the gap to nginx is less work per request: vanilla's framer checks only framing headers and leaves field-line validation and Connection handling to handlers (#310, #311), whereas nginx parses and validates every header.
- VANILLA_WORKERS defaults to the host's online CPU count and ignores a container cpuset (the HttpArena Dockerfile overrides it with nproc); with -gc none every per-request allocation is a permanent leak, so handlers must stay allocation-free.
- ServerConfig.certificates is never read, so setting it silently serves plaintext (open issue #287); use tls_config on the epoll backend.

## Known shortcomings

- The json-comp 9.6x/22x rows are invalid: main.v write_json_gzip compresses once per (count, m) and replays cached gzip bytes (wazero cache-hit precedent), struck from the claim. The rest only ties the best C (0.98x libreactorng on baseline); json-tls is partly pre-serialized, TLS is Mbed TLS (C) plus kTLS, gzip is miniz (C), and V compiles to C (gcc -O3 -flto); 102.0 bytes per response. Best of 3, cross-run rows.
- Benchmark-shaped handlers: the HttpArena /pipeline path matches the raw prefix 'GET /pipeline ' and copies a constant response without parsing (the 43.7M req/s pipelined row, a reference-only profile), json-comp replays cached gzip responses (struck by the verifier; confirmed by PERF_GAP_ANALYSIS.md), json-tls renders item JSON prefixes at startup, and responses carry no Date header. The core framer reads only Content-Length and Transfer-Encoding; open #310: Connection: close never honoured; open #311: malformed field lines reach handlers (smuggling risk), so vanilla does less validation per request than nginx; open #287: ServerConfig.certificates ignored, plaintext served silently.

## Caveats and trade-offs

The json-comp ratios (9.6x over userver, 22x over Drogon) time a response cache: write_json_gzip in main.v keeps complete gzipped responses keyed by (count, m), compresses once on the first miss and appends the cached bytes on every hit, while HttpArena's json-comp rules forbid pre-compressed caches for standard and tuned entries (vanilla is an 'engine' entry, which has no rules) and the C++ rows compress per request. vanilla's rate there is 2.7x the next entry (zix, which compresses per request). No C engine or nginx runs json-comp. The json-tls body is partly pre-serialized: each item's JSON except total is rendered once at startup into a prefix string, so per request vanilla formats one integer per item and copies prefixes, whereas nginx's infrastructure rules require full per-request serialization; TLS is Mbed TLS (C, patched to cache the RSA signing context) with kTLS record offload in the kernel. static-tls and pipelined are reference-only profiles. At baseline-4096 the entry trails libreactorng (0.98x) and is level with libioma (1.01x) and at limited-conn it ties libreactorng and libioma, so on the scored HTTP/1.1 profiles vanilla matches but does not beat the best C engines. The vanilla-epoll entry is slower at baseline-4096 (3,985,550) and at limited-conn-4096 (1,021,750). V compiles to C (gcc -O3 -flto), so this is a V-generated C server against hand-written C servers, not a different code generator. Bytes per response at baseline-4096 (derived from page data, bandwidth divided by req/s): vanilla 102.0 (Server and Connection headers, no Date), nginx 135.4, Drogon 134.4, libreactorng 108.7, h2o 98.2, libioma 85.8, mongoose 72.5; at baseline-h2c-256 vanilla-epoll writes 43.2 bytes per response against agensio's 25.9. The h2c row comes from the -gc none build, which never frees memory. Each number is the best of 3 runs of 5 s with the server limited to 32 cores / 64 threads; results files are undated and rows come from different runs (vanilla-io_uring.json last written 2026-10-02, vanilla-epoll.json 2026-10-11, agensio.json 2026-10-06, libreactorng.json 2026-09-07, per git history). The vanilla entries are maintained by the vanilla author (meta.json maintainers: enghitalo). The vanilla README publishes no throughput numbers against C servers; docs/PERF_GAP_ANALYSIS.md treats libreactorng, zeemo and tokio as the faster reference servers. The Drogon entry builds only its handler against the unpinned drogonframework/drogon:latest image and userver uses a prebuilt v3.2 image, so those ratios are weaker evidence than the nginx, h2o, libreactorng and libioma ratios. [retier] Benchmark-shaped handlers: /pipeline matches the raw prefix 'GET /pipeline ' and copies a constant response without parsing (the 43.7M req/s pipelined row, reference-only), json-tls renders item JSON prefixes at startup, and responses carry no Date header. The core framer reads only Content-Length and Transfer-Encoding; open #310 (Connection: close never honoured) and #311 (malformed field lines reach handlers, smuggling risk) mean vanilla does less validation per request than nginx; open #287: ServerConfig.certificates ignored, plaintext served silently.

V is a young language (default GC, built from master, 77 open issues on the repo); memory use is high (about 640 MiB to 990 MiB in the entries above versus about 100 MiB for C entries); the io_uring backend has no TLS (TLS runs on the epoll backend).

## Maintenance

Very active single-maintainer MIT project (967 commits, last commit 2026-10-12, 41 stars, 71 open issues, many filed in the past week, no tagged release); the maintainer also maintains its HttpArena entries, so treat it as a fast-moving library rather than a stable dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** Tier A stays for the HTTP/1.1, TLS and h2c rows: every quoted number matches site/data/results/vanilla-io_uring.json, vanilla-epoll.json and the sibling nginx, libreactorng, libioma, h2o, mongoose, agensio, userver and drogon JSON files; the code is public (frameworks/vanilla-io_uring/{Dockerfile,main.v,meta.json}, frameworks/vanilla-epoll/{Dockerfile,main.v}, frameworks/nginx/Dockerfile, scripts/lib/common.sh, scripts/lib/profiles.sh), the V commit and -prod mode are pinned (V's -prod flags read from vlib/v/driver/driver.v at b99970bd), and the CPU model is in site/data/current.json. Downgraded because the headline json-comp claim is invalid: vanilla serves cached gzipped responses.
- **Verifier notes:** Numbers verified, tier A kept, verdict downgrade because the claim was overstated: the json-comp 9.6x and 22x wins time cached gzipped responses (main.v write_json_gzip compresses once per (count, m) and replays the bytes), so they are struck as invalid evidence (wazero cache-hit precedent). Shortcomings to record: on scored HTTP/1.1 profiles it only ties the best C engines (0.98x libreactorng at baseline-4096, 1.00x at limited-conn); json-tls beaten by agensio (0.89x) and partly pre-serialized; TLS is Mbed TLS (C) with kTLS; static-tls and pipelined are reference-only; V compiles to C; vendor-maintained entries; cross-run rows. Metadata confirmed: MIT, 41 stars, last commit 2026-10-12, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-49 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/vanilla-io_uring.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/vanilla-epoll.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/proxygen.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/frameworks.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/hardware/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/scoring/composite-score.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/json-compressed/_index.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/json-compressed/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/json-compressed/validation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/json-tls/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-io_uring/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-io_uring/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-io_uring/main.v>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-io_uring/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-epoll/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-epoll/main.v>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libioma/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/h2o/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/mongoose/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/userver/Dockerfile>
  - <https://raw.githubusercontent.com/vlang/v/b99970bd438a7bdcdfbe38f74d9364db801d5439/vlib/v/driver/driver.v>
  - <https://raw.githubusercontent.com/vlang/v/b99970bd438a7bdcdfbe38f74d9364db801d5439/vlib/compress/compress.c.v>
  - <https://raw.githubusercontent.com/vlang/v/b99970bd438a7bdcdfbe38f74d9364db801d5439/vlib/compress/gzip/gzip.v>
  - <https://github.com/enghitalo/vanilla>
  - <https://github.com/enghitalo/vanilla/commits>
  - <https://raw.githubusercontent.com/enghitalo/vanilla/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/enghitalo/vanilla/HEAD/docs/PERF_GAP_ANALYSIS.md>
  - <https://raw.githubusercontent.com/enghitalo/vanilla/HEAD/BENCHMARK_RESULTS_MACOS.md>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/vanilla-io_uring>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/vanilla-io_uring.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/vanilla-epoll.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/agensio.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/site/content/docs/test-profiles/h1>
- **Sources the enricher read:**
  - <https://github.com/enghitalo/vanilla>
  - <https://github.com/enghitalo/vanilla/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/enghitalo/vanilla/issues/310>
  - <https://github.com/enghitalo/vanilla/issues/311>
  - <https://raw.githubusercontent.com/enghitalo/vanilla/HEAD/README.md>
  - <https://raw.githubusercontent.com/enghitalo/vanilla/HEAD/docs/PERF_GAP_ANALYSIS.md>
  - <https://raw.githubusercontent.com/enghitalo/vanilla/HEAD/v.mod>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-io_uring/main.v>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-io_uring/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-io_uring/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-io_uring/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-epoll/main.v>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/vanilla-epoll/Dockerfile>
  - <https://github.com/MDA2AV/HttpArena/commits/main/frameworks/vanilla-io_uring>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/enghitalo/vanilla`) · [data/wave14/enrich/raw/github_com_enghitalo_vanilla.json](../../../data/wave14/enrich/raw/github_com_enghitalo_vanilla.json) (enrichment confidence 0.66)

</details>
