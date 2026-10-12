# zix

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `BSD-3-Clause` · 🟢 active

> Pure-Zig network library with io_uring HTTP/1.1, HTTP/2 and HTTP/3 engines; beats nginx, h2o and Drogon in HttpArena.

| | |
|---|---|
| **Beats** | nginx 1.31.4 (C, custom handler module, -O3 -march=native -DNDEBUG); same suite rows for libreactorng (C, io_uring), libioma (C), h2o (C), mongoose (C), agensio (C++), Drogon (C++) and userver (C++) |
| **Claimed result** | baseline-4096: 4,442,329 req/s vs nginx 3,284,513 (1.35x), h2o 3,641,609 (1.22x), mongoose 3,707,598 (1.20x), agensio (C++) 3,558,559 (1.25x), libioma 4,255,834 (1.04x), libreactorng 4,377,377 (1.01x, within noise), Drogon 2,022,710 (2.20x). The static-h2-256 win (1.08x agensio, 2.11x nginx) is struck: the zix-http2/http3 entries pre-load every static file and its .br/.gz twins into an entry-side cache that is never revalidated, against HttpArena's engine rule. json-h2c 4.0x over nginx is not like-for-like (zix pre-renders item JSON at startup; 1.64x over agensio, which uses the same trick, is fair). |
| **Workload** | HttpArena profiles across three zix engines: H/1.1 profiles (baseline, pipelined 16x, limited-conn, json-tls, static-tls, latency-1m) on the zix.Http1 URING dispatch engine (frameworks/zix, zix branch 0.5.x); baseline-h2, static-h2, baseline-h2c and json-h2c on the separate zix.Http2 URING engine (frameworks/zix-http2, zix 0.5.x-rc1); baseline-h3 and static-h3 on the zix.Http3 engine, pure-Zig QUIC on std.crypto (frameworks/zix-http3). Each engine runs per-worker SO_REUSEPORT io_uring loops. Load generator (gcannon/h2load/zrk) pinned to CPUs 32-63,96-127, server on the rest; scripts/benchmark.sh keeps the best of 3 runs of 5 s (RUNS=3, DURATION=5s in scripts/lib/common.sh). |
| **Metric** | throughput |
| **Hardware** | HttpArena dedicated machine per site/data/current.json: AMD Ryzen Threadripper PRO 3995WX 64-Cores (64 cores, 128 threads), 251 GiB RAM, Ubuntu 24.04.4 LTS, kernel 6.17.0-22-generic, Docker 29.3.0 (runc), CPU governor performance; each entry runs in a container. current.json is undated and may differ from the machine state of the run behind a given results file. |
| **Compiler and flags** | zix: Zig 0.16.0, zig build -Dtarget=x86_64-linux-musl -Dcpu=x86_64_v3+aes+pclmul+adx --release=fast (frameworks/zix, zix-http2 and zix-http3 Dockerfiles; zix fetched from codeberg by branch 0.5.x or 0.5.x-rc1, not a pinned commit). nginx 1.31.4: custom C module, ./configure --with-cc-opt='-O3 -march=native -DNDEBUG', quictls for TLS/QUIC, brotli built -Ofast -march=native -flto. libreactorng (pinned commit 7a65f8b, patched for Connection: close): gcc -O3 -march=native. libioma (pinned b027f05): gcc-14 -O3 -march=native -flto. mongoose 7.23: gcc-14 -O3 -march=native -flto, OpenSSL TLS, epoll. h2o (pinned ccea64b): clang, CMake Release -march=native -mtune=native, no LTO. agensio v0.1.0-alpha.23: CMake Release, Ninja, -DAGENSIO_NATIVE=ON (Debian trixie toolchain). Drogon: handler built with CMake Release against the prebuilt drogonframework/drogon:latest image, jemalloc preloaded. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Per-worker SO_REUSEPORT io_uring loops with a comptime router and staged send sink (HttpArena meta.json and frameworks.json). The fastest C entries use the same thread-per-core io_uring design, so the gain over nginx (epoll) is architecture, not the language. |
| **Adoption** | 10 stars, 1 fork (GitHub mirror of codeberg.org/prothegee/zix) |
| **Last commit** | 2026-09-05 |
| **Links** | [repository](https://github.com/prothegee/zix) · [benchmark](https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zix.json) |

## Verdict

In HttpArena on a Threadripper PRO 3995WX (64 cores, kernel 6.17, Docker), zix built with Zig 0.16.0 --release=fast (x86_64_v3+aes+pclmul+adx, musl) served 4.44M req/s at baseline-4096 against nginx 1.31.4 (C module, -O3 -march=native) at 3.28M (1.35x), h2o 3.64M and Drogon 2.02M, but only 1-4% over the io_uring C servers libreactorng and libioma; best-of-3 runs of 5 s, each entry's results file saved at a different time. It loses on baseline-h2 to h2o, on baseline-h2c and static-h3 to agensio, and comes last in static-tls; its static-h2 win uses an entry-built in-memory file cache that the profile rules forbid.

## Use it when

- A new Linux service written in Zig that needs plaintext HTTP/1.1 throughput at or above nginx with a custom C module (HttpArena baseline-4096: 4.44M vs 3.28M req/s, 1.35x)
- Many keep-alive connections with small responses on a many-core box, where per-core io_uring loops pay off (pipelined-4096: 58.8M req/s, 1.35x libreactorng)
- h2c JSON APIs or HTTP/3 baseline traffic where you want one pure-Zig stack with no OpenSSL or C QUIC library to vendor
- Projects that want server and matching clients for HTTP, gRPC, WebSocket, SSE, raw TCP/UDP and FIX from one library with one config vocabulary

## Skip it when

- C or C++ codebases: it is a Zig source module consumed through build.zig.zon, with no C ABI library to link
- TLS static-file serving: in static-tls-1024 zix came last (339,689 req/s vs nginx 720,869, mongoose 611,058 and agensio 1,191,970)
- HTTP/2 over TLS at small payloads, where h2o (16.1M vs 14.1M req/s at baseline-h2-256) and agensio are ahead, and h2c baseline where agensio leads at every connection count
- Non-Linux production: .EPOLL and .URING are rejected off Linux and only .ASYNC runs there; Windows, macOS and the BSDs are cross-compile only with no maintainer
- Anything needing API stability: pre-1.0 (0.5.0, released 2026-08-17), about 4,950 commits since March 2026, a breaking-changes tracker on Codeberg, one maintainer, and an unaudited from-scratch TLS, QUIC and brotli

## How it is fast

Under .URING each worker owns its own SO_REUSEPORT listener and io_uring ring (thread-per-core, shared-nothing, no cross-thread fd handoff); accept, recv, send and close (prep_close) all go through the ring so syscalls are batched. Routes are matched by a comptime router (StaticStringMap for exact paths) with no runtime allocation, connection buffers come from a per-worker demand-paged slab, and pipelined responses are staged and leave as one send. The HttpArena H1 entry also turns off the Date header and caps response headers, so each reply is about 63-66 bytes against about 135 for nginx.

## Compared with alternatives

Pick zix over libxev (an event loop only, tied at 4.38M req/s baseline-4096) or zeemo (4.42M, a tie) when you need a complete pure-Zig protocol stack with HTTP/2, HTTP/3, gRPC and TLS rather than just an H1 loop; on H1 plaintext it is in the same band as vanilla (V, 4.31M), ioxide (4.11M) and the C# minima-sync entry (4.39M), so the choice there is language, not speed.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (Zig standard library only; build step generates the brotli dictionary) |
| **Minimum toolchain** | Zig 0.16.0 (0.17.0-dev experimental) |
| **Platforms** | x86_64-linux and aarch64-linux maintained; Windows, macOS, FreeBSD, NetBSD, OpenBSD cross-compile only with .ASYNC dispatch |
| **Thread safety** | Shared-nothing per worker under .EPOLL/.URING (per-worker response cache, slab and ring, no locks); handlers run on worker threads; Logger documented safe from background threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the static-h2 (and static-h3) rows: the HttpArena zix-http2 and zix-http3 entries scan /data/static with getdents64 at startup (prewarmStatic) and read every file and its .br/.gz twin into process-lifetime buffers that are never revalidated. HttpArena's static-h2 and static-h3 rules for engines say the cache 'must be the framework's own rather than one assembled in the entry, and it must follow the disk'; validate.sh runs its disk-staleness probe only for static-tls, so this is not caught. The static-h2-256 win (1,692,045 req/s vs agensio 1,571,021 and nginx 802,090, which sendfiles per request with no open_file_cache) rests on an entry-built cache the profile forbids.
- json-h2c is not like-for-like against nginx: zix-http2's dataset.zig pre-renders each item's JSON fields at startup and only appends total per request, while the nginx module ngx_sprintf-serializes every field per request; engines have no json-h2c rules, and agensio uses the same prefix trick, so the 1.64x over agensio is fair but the 4.0x over nginx compares different work. The H1 json-tls entry, by contrast, serializes every field per request through jzon.
- The HttpArena H1 entry sets send_date_header = false and writes a hard-coded 66-byte /pipeline response; nginx sends Date and Server headers. RFC 9110 requires Date from an origin server with a clock, so production zix configs with the header on will write more bytes per response than the benchmarked one.
- When io_uring is unavailable (old kernel, low RLIMIT_MEMLOCK, sandbox) .URING silently folds to .EPOLL with only a log notice; the response cache (off in the benchmark) works only under .EPOLL/.URING and keys on method, path and query, so it must not be used for responses that vary by header or cookie.

## Known shortcomings

- Win over the same-design io_uring C engines (libreactorng, libioma) is 0-4%, within noise; the big wins over nginx, h2o, mongoose and Drogon come from io_uring vs epoll; H/2 and H/3 rows come from separate zix engines (zix-http2, zix-http3, pure-Zig QUIC); loses to h2o at h2-1024, to agensio (C++) on all h2c baseline rows and static-h3, and is last on static-tls (sends uncompressed bytes); result files saved on different dates, zix fetched by branch name rather than a pinned commit, fewer response bytes than most C entries; runs are best of 3 x 5 s.
- Harness flaw: the HttpArena zix-http2 and zix-http3 entries read all static files plus their .br/.gz twins into their own in-memory cache at startup (prewarmStatic, getdents64) and never revalidate, breaking the static-h2/static-h3 engine rule (the cache must follow the disk); validate.sh's staleness probe covers only static-tls, so it was not caught, and the static-h2-256 win (1.08x agensio, 2.11x nginx) is invalid. json-h2c: zix-http2 pre-renders item JSON at startup while nginx serializes every field per request, so the 4.0x is not like-for-like (agensio uses the same prefix trick; 1.64x over it is fair). The H1 entry sets send_date_header=false and hard-codes a 66-byte /pipeline reply while nginx sends Date and Server. The baseline-4096 1.35x over nginx stands. codeberg.org blocked, so zix issues went unread.

## Caveats and trade-offs

The margin over the fastest C entries at baseline-4096 and limited-conn-4096 is 0-4% (libreactorng, libioma), within run-to-run noise; the clear wins are over nginx, h2o, mongoose, agensio and Drogon, which use epoll or Asio rather than io_uring, and on the pipelined, json-tls, h2c-json, h3 and static-h2 profiles. scripts/benchmark.sh keeps the best of 3 runs of 5 s per profile, but the results files record only the winning run, and each entry's file is saved at a different time (zix.json and nginx.json last changed 2026-08-30, libreactorng.json 2026-09-07 after a Connection: close fix), so rows are cross-run comparisons on the same machine; current.json (the CPU and kernel record) is undated. zix itself is fetched by branch name (0.5.x, 0.5.x-rc1), so the exact commit behind the numbers is not recorded. The H/2 and H/3 rows come from separate zix engines (zix.Http2, zix.Http3 with pure-Zig QUIC on std.crypto), not the Http1 engine. The C competitor entries (nginx with a custom C handler module, libreactorng, libioma, h2o, mongoose) are minimal handlers built by the suite maintainers or contributors; nginx is reasonably tuned (access_log off, reuseport, worker_processes auto). The Drogon entry compiles only its handler against the prebuilt drogon:latest image, so its 2x to 8x ratios are weaker evidence. Response sizes differ (bytes per response derived from bandwidth / req/s: baseline-4096 nginx 135.4, Drogon 134.4, libreactorng 108.7, libioma 85.8, mongoose 72.5, zix 62.9; baseline-h3 zix about 7.6, agensio about 17.4, nginx about 76), so zix writes the fewest bytes per request. In static-tls zix sends about 11.9 KB per response against about 3.1 KB for nginx and agensio (derived), consistent with nginx (gzip_static, brotli_static) and agensio serving precompressed variants that zix does not, so that profile is not like-for-like either way. The pipelined profile is reference-only in HttpArena's composite score. The zix README only links to HttpArena badges and gives no numbers. [retier] The zix-http2 and zix-http3 entries read all static files plus .br/.gz twins into their own in-memory cache at startup (prewarmStatic, getdents64) and never revalidate, breaking the static-h2/static-h3 engine rule; validate.sh's staleness probe covers only static-tls. The H1 entry sets send_date_header=false and hard-codes a 66-byte /pipeline reply while nginx sends Date and Server.

Young Zig 0.16 network library and HTTP engine; the URING dispatch model is Linux-only and needs a recent kernel; the TLS static-file path is slower than nginx; project is pre-1.0.

## Maintenance

Very active (last mirror commit 2026-09-05, Codeberg is the main repository) single-maintainer BSD-3-Clause Zig module at 0.5.0, copyable but pre-1.0 with announced breaking changes and the benchmark built from an unpinned branch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** HttpArena (independent suite) publishes every entry's code and build: frameworks/zix{,-http2,-http3}/Dockerfile (Zig 0.16.0 --release=fast, -Dcpu=x86_64_v3+aes+pclmul+adx), frameworks/nginx/Dockerfile (--with-cc-opt='-O3 -march=native -DNDEBUG') and the libreactorng, libioma, mongoose, h2o, agensio Dockerfiles, run by scripts/benchmark.sh on the Threadripper PRO 3995WX named in site/data/current.json; every req/s figure in the record matches site/data/results/\*.json.
- **Verifier notes:** Numbers verified against the HttpArena results JSON files for zix, nginx, libreactorng, libioma, h2o, mongoose, agensio, Drogon and userver; tier A holds since every Dockerfile, flag and the CPU are public. Corrections: H/2 and H/3 rows come from separate zix engines; runs are best-of-3 x 5 s, not a single run; more loss rows added (h2o at h2-1024, agensio on all baseline-h2c rows and static-h3, zix last in static-tls, which also serves uncompressed bytes); same_algorithm set false because the large wins are io_uring vs epoll. Shortcomings to record: win over same-design C engines within noise, cross-run result files, unpinned zix version, fewer response bytes than most C entries.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-50 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libreactorng.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/libioma.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/mongoose.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/agensio.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/drogon.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/userver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http2/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http2/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http3/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http3/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-grpc/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-ws/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libreactorng/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/libioma/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/mongoose/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/h2o/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/drogon/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/benchmark.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/common.sh>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/zix.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/libreactorng.json>
  - <https://github.com/prothegee/zix>
  - <https://github.com/prothegee/zix/commits>
- **Sources the enricher read:**
  - <https://github.com/prothegee/zix>
  - <https://github.com/prothegee/zix/commits>
  - <https://raw.githubusercontent.com/prothegee/zix/HEAD/README.md>
  - <https://raw.githubusercontent.com/prothegee/zix/HEAD/README-en.md>
  - <https://raw.githubusercontent.com/prothegee/zix/HEAD/build.zig>
  - <https://raw.githubusercontent.com/prothegee/zix/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/prothegee/zix/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/prothegee/zix/HEAD/LICENSE-BSD>
  - <https://raw.githubusercontent.com/prothegee/zix/HEAD/src/lib.zig>
  - <https://raw.githubusercontent.com/prothegee/zix/HEAD/docs/concurrency-en.md>
  - <https://raw.githubusercontent.com/prothegee/zix/HEAD/docs/hld-tls-en.md>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/zix>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/zix/src>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/zix/src/handlers>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/zix/src/shared>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/zix-http2>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/zix-http2/src>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/zix-http3/src>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/src/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/src/handlers/baseline.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/src/handlers/pipeline.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/src/handlers/json.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/src/shared/dataset.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/src/shared/response.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/build.zig.zon>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix/build.zig.zon.template>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http2/src/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http2/src/handler.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http2/src/dataset.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http2/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http2/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http3/src/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http3/src/handler.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/zix-http3/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zix.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/validate.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h2/static-h2/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h3/static-h3/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h2/json-h2c/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/static-tls/implementation.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/content/docs/test-profiles/h1/baseline/implementation.md>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/nginx>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/ngx_http_httparena_module.c>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/nginx.conf>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/agensio>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/agensio.toml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/agensio/meta.json>
  - https://codeberg.org/prothegee/zix/issues (EGRESS_BLOCKED)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/prothegee/zix`) · [data/wave14/enrich/raw/github_com_prothegee_zix.json](../../../data/wave14/enrich/raw/github_com_prothegee_zix.json) (enrichment confidence 0.75)

</details>
