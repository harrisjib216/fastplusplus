# swerver

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig HTTP/1.1, HTTP/2 and HTTP/3 server and gateway on io_uring; edges an -O3 nginx on HttpArena plaintext and TLS, loses badly on HTTP/3.

| | |
|---|---|
| **Beats** | nginx (openresty/openresty:alpine Docker image, unpinned tag; tuned nginx.conf with worker_processes auto, reuseport, 'return 200' for /health and content_by_lua for /echo) |
| **Claimed result** | GET /health, 100 VUs, 30 s: swerver 147,435 req/s vs nginx 118,061 (1.25x, derived from page data), actix 133,691; no keep-alive connections/s 90,657 vs nginx 19,206 (4.7x); rapid-fire 143,437 vs nginx 125,346; error handling 114,455 vs nginx 80,053; TLS /health h2 161,781 vs nginx 107,741. |
| **Workload** | swerver-benchmarks: k6 scenarios against minimal endpoints (/health, /echo, /blob) in Docker with 2 CPUs and 512 MB per container, swerver vs nginx, actix, http-zig and APISIX. |
| **Metric** | throughput |
| **Hardware** | Docker Desktop VM on macOS Apple Silicon (chip not stated), 2 CPUs and 512 MB per server container via docker-compose limits, k6 load generator in an unconstrained container on the same VM, April 2026 |
| **Compiler and flags** | swerver (April 2026 results, harness commit f5eb7c1): Zig 0.16.0-dev.3133+5ec8e45f3 aarch64-linux, zig build -Doptimize=ReleaseFast (servers/swerver/Dockerfile); HEAD now builds a bench app with .ReleaseFast hard-coded in servers/swerver/app/build.zig on Zig 0.16.0. nginx: openresty/openresty:alpine image, whose OpenResty configure adds -O2 by default (util/configure) and whose Dockerfile passes only -D/-I cc-opts, so nginx is built at -O2, not -O3. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | io_uring backend plus a pre-encoded response cache for hot endpoints that skips the router, middleware and response encoder (swerver-benchmarks README). |
| **Adoption** | 35 stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/justinGrosvenor/swerver) · [benchmark](https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/README.md) |

## Verdict

Catalogued claim: the author's own k6 suite (Docker Desktop on an unnamed Apple Silicon Mac, 2 CPUs and 512 MB per container, single run, April 2026) has swerver at 147,435 req/s on GET /health against 118,061 for OpenResty-alpine nginx built at -O2, 1.25x. Stronger data on HttpArena (independent harness, AMD Threadripper PRO 3995WX, Zig 0.16.0 ReleaseFast vs nginx 1.31.4 at -O3 -march=native, pre-encoded cache off; nginx rows from mid-August, swerver rows from late August to September, derived from page data): baseline-4096 3,668,682 vs 3,284,513 (1.12x), json-tls 1.15x, baseline-h2-256 1.18x, limited-conn tie, baseline-h3 0.18x.

## Use it when

- Self-hosted Linux edge or gateway in one binary that has to terminate TLS and speak HTTP/1.1, h2 and h2c: on HttpArena it beats an -O3 -march=native nginx on json-tls (1.15x), static-tls (1.54x) and h2c (2.6-5.1x).
- HTTP/1.1 pipelined or keep-alive traffic with tiny responses, where the io_uring loop helps (HttpArena pipelined 5.7x nginx, baseline 1.12x).
- Zig projects that want to embed a full server (routing, middleware, proxy, Postgres client) as a library, not link a C server.
- Experiments with WASM edge filters or x402 payment gating on the request path, which nginx does not ship.

## Skip it when

- HTTP/3: on HttpArena baseline-h3 nginx serves 4,849,624 req/s against swerver's 890,094 (nginx 5.4x faster), and the README calls the QUIC stack young, with no 0-RTT.
- HTTP/2 over TLS at scale against h2o: h2o does 16.1M vs 4.0M req/s on baseline-h2-256 (4x ahead); connection churn is a tie with nginx and h2o (limited-conn 2.63M vs 2.63M and 2.65M).
- Production gateways that need a stable API or audited code: alpha release (v0.1.0-alpha.33), the API in src/lib.zig will change, the security audit is still on the 1.0 roadmap, 35 stars and one maintainer.
- Windows (no IOCP backend, cross-compile only), and setups that rely on the prebuilt release binaries, which ship without TLS, HTTP/2 or HTTP/3.
- Teams that need nginx configuration, modules or OpenResty Lua: nothing carries over.

## How it is fast

Linux builds pick an io_uring backend (multishot accept and multishot recv) over epoll, with kqueue on macOS; each worker is a forked process running a single-threaded event loop behind SO_REUSEPORT. All buffers come from a fixed-size pool allocated at startup, and requests are parsed in place so header names and values are slices into the receive buffer. An optional pre-encoded response cache serves registered hot endpoints as a memcpy of cached wire bytes, skipping the router, middleware and encoder. It is opt-in at HEAD and turned off in the HttpArena entry (preencoded: false), but it was on for /health in the April swerver-benchmarks runs.

## Compared with alternatives

Pick swerver over the plaintext-only HttpArena siblings (zeemo, minima-sync, libxev, tokio) when you need TLS, h2, h3, routing and a proxy in one Zig binary. If you only want raw HTTP throughput, take zix, the other Zig entry: it is ahead on nearly every shared HttpArena profile (baseline-4096 4.44M vs 3.67M, h3 9.1M vs 0.89M, pipelined 58.8M vs 23.1M).

## Integration

| | |
|---|---|
| **Form** | module (Zig package via build.zig.zon) or standalone binary |
| **Dependencies** | OpenSSL 3.5+ for TLS, HTTP/2 and HTTP/3 (QUIC TLS callback API); zlib for compression; optional secp256k1 path for x402; none for a plain HTTP/1.1 build |
| **Minimum toolchain** | Zig 0.16.0 (stable); the April swerver-benchmarks runs used Zig 0.16.0-dev.3133 |
| **Platforms** | Linux x86-64 and aarch64 (io_uring or epoll), macOS (kqueue); Windows cross-compile only |
| **Thread safety** | Multi-process: each worker is a fork with its own single-threaded event loop and its own copy of process globals; handlers run on that loop and must not block (async handlers park on timers or events) |
| **Drop-in for the baseline** | partial — it can replace nginx as an HTTP/1.1, h2 or h3 front server or reverse proxy, but it is configured by its own JSON schema or Zig code, with no nginx.conf, module or Lua compatibility |

## Gotchas

- The first-party Docker k6 suite behind the catalogued 1.25x and 4.7x is weak: one run on an unnamed Apple Silicon chip under Docker Desktop; k6 runs closed-loop with 100 VUs in an unconstrained container on the same VM, so all five servers land within 91K-147K req/s on /health while the native wrk run of one swerver process reached 274,617 (the load generator and VM likely cap it); nginx's worker_processes auto counts the VM's CPUs, not the 2-CPU CFS quota from docker-compose cpus: 2; swerver answered /health from its pre-encoded cache. HttpArena's limited-conn (connection churn on dedicated hardware) shows a tie with nginx, not 4.7x.
- The README's HttpArena table is stale: it claims json-tls 1,950,310 req/s, but site/data/results/swerver.json now has 1,510,149. Its json and static rows are for profiles HttpArena removed on 2026-08-29.
- The README CLI table says --workers defaults to 1, but src/config.zig defaults workers to 0 (one worker per CPU). Inside a CPU-quota container, nproc reports the host's CPUs, so pin workers explicitly.
- The opt-in per-IP connection limit (per_ip_limit, default 0) uses a linear-probing table in src/server/accept.zig that deletes by zeroing the key with no tombstones, so an IP whose slot sat past a freed slot can gain a second counter and leak the first; the limit can then be exceeded or misapplied after connection churn.

## Known shortcomings

- The win comes from server design, not the Zig language (io_uring vs epoll, a pre-encoded response cache, disable_middleware in the bench config); first-party numbers on an unnamed Apple Silicon chip under Docker Desktop; nginx built at -O2 (OpenResty default) with worker counts not pinned equal; results are mixed (mixed-workload tie, nginx ahead on /echo latency, actix ahead on TLS, h2 and error rows); the harness changed after the April results.
- The first-party k6 suite is one run on Docker Desktop with k6 closed-loop on the same VM, so all five servers land at 91K-147K req/s on /health while native wrk on one swerver process hit 274,617; nginx's worker_processes auto counts VM CPUs, not the 2-CPU quota; swerver's /health came from the pre-encoded cache; the 4.7x connection-churn win vanishes on HttpArena limited-conn (2,629,113 vs 2,626,297, a tie). HttpArena (Threadripper PRO 3995WX, nginx -O3 -march=native, swerver preencoded off): baseline-4096 1.12x, json-tls 1.15x, h2-256 1.18x over nginx, but 0.18x on baseline-h3 and 0.25x of h2o on h2; nginx rows date from Aug 15-20 and swerver rows from Aug 25-Sep 25 (cross-run). The README's json-tls 1,950,310 is stale (file now 1,510,149). Opt-in per_ip_limit table deletes without tombstones.

## Caveats and trade-offs

First-party benchmark by the swerver author, single run reported (no medians or repeat counts). Hot endpoints (/health, /plaintext, /json) are served from a per-second-refreshed pre-encoded response cache that skips the router, middleware and encoder, and the HEAD bench config sets disable_middleware: true; nginx answers /health with 'return 200' and /echo through content_by_lua. swerver container runs with seccomp unconfined so io_uring is used; nginx uses epoll. nginx is built at -O2 (OpenResty default), not -O3. Worker counts are not pinned equal (nginx worker_processes auto; swerver --workers defaults to 1 per its README, April image ran it without a config). Hardware is an unnamed Apple Silicon chip under Docker Desktop's VM. Results are mixed: mixed workload 36,929 vs nginx 36,969 (tie), /echo latency scenario nginx 8,659 vs swerver 8,517, actix-web ahead of swerver on TLS throughput (171,726 vs 161,781), h2 throughput (129,428 vs 111,698) and error handling (141,755 vs 114,455). The native wrk table (274,617 req/s on /health) has no nginx row. swerver's own README concedes feature-stripped reference servers edge it by 1-2% on raw HTTP/1.1 HttpArena tests. The harness has changed since the April results (Jul 2026 commit 'serve the benchmark endpoints + unbreak the baseline build'), so HEAD does not reproduce the measured build exactly. [retier] The k6 suite is one closed-loop run on Docker Desktop, so all five servers land at 91K-147K req/s on /health while native wrk on one swerver process hit 274,617; nginx's worker_processes auto counts VM CPUs, not the 2-CPU quota; /health came from the pre-encoded cache; the 4.7x connection-churn win vanishes on HttpArena limited-conn (2,629,113 vs 2,626,297, a tie). HttpArena (Threadripper PRO 3995WX, nginx -O3 -march=native, preencoded off): baseline-4096 1.12x, json-tls 1.15x, h2-256 1.18x over nginx, but 0.18x on baseline-h3 and 0.25x of h2o on h2; nginx rows date from Aug 15-20 and swerver rows from Aug 25-Sep 25 (cross-run). The README's json-tls 1,950,310 is stale (file now 1,510,149).

Alpha release; library API will change; HTTP/3 first version runs at 16.5K req/s.

## Maintenance

Active (last commit 2026-09-24, HttpArena results updated 2026-09-25, 465 commits) and MIT-licensed, but an alpha with an unfrozen API and one maintainer. Harness flaw found: the first-party k6 numbers are probably capped by the co-located load generator and the VM, and use mismatched worker counts and a response cache. The independent HttpArena rows (1.12x baseline, 1.15x json-tls vs -O3 nginx) are the better evidence, and on the precedent of the other HttpArena entries they would support a retier above C.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party k6 suite by the swerver author (harness public in swerver-benchmarks: docker-compose.yml, servers/\*/Dockerfile, servers/nginx/config/nginx.conf, k6/scenarios/\*.js) with swerver built ReleaseFast and nginx from the OpenResty alpine image at OpenResty's default -O2, but the hardware is only 'Docker Desktop on macOS Apple Silicon' with no chip model, so it falls short of A; no independent nginx comparison found.
- **Verifier notes:** All claimed numbers match the swerver-benchmarks README tables (throughput 147,435 vs 118,061; connections 90,657 vs 19,206, page states 4.7x; rapid-fire 143,437 vs 125,346; error handling 114,455 vs 80,053; TLS h2 /health 161,781 vs 107,741). For wave 14 the win is not a language-level one: different server architectures (io_uring plus response cache vs epoll nginx), nginx at -O2 rather than -O3, so same_algorithm and same_opt_level are false; the baseline is tuned, not crippled, so tier C stands. License MIT, 35 stars, 1 fork, not a fork, last commit 2026-09-24 confirmed on github.com; swerver also appears to be submitted to HttpArena (MDA2AV/HttpArena, which carries h2o but no visible nginx entry), whose leaderboard site was not checked.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-21 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/README.md>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/servers/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/servers/nginx/config/nginx.conf>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/servers/swerver/Dockerfile>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/servers/swerver/app/build.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/servers/swerver/config.json>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/.env.example>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/k6/scenarios/throughput.js>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/k6/scenarios/connections.js>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/f5eb7c1658670fee623337979ed12d3827abcdfe/servers/swerver/Dockerfile>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/f5eb7c1658670fee623337979ed12d3827abcdfe/servers/nginx/config/nginx.conf>
  - <https://raw.githubusercontent.com/openresty/docker-openresty/master/alpine/Dockerfile>
  - <https://raw.githubusercontent.com/openresty/openresty/master/util/configure>
  - <https://github.com/justinGrosvenor/swerver>
  - <https://github.com/justinGrosvenor/swerver/commits>
  - <https://github.com/justinGrosvenor/swerver-benchmarks/commits>
  - <https://github.com/justinGrosvenor/swerver-benchmarks/commits/main/servers/swerver>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/README.md>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/build.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/config.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/server/accept.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/server/http1.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/server/dispatch.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/server/preencoded.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/runtime/connection.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/runtime/io.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/server.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/lib.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/master.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/bootstrap.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver/HEAD/src/main.zig>
  - <https://github.com/justinGrosvenor/swerver>
  - <https://github.com/justinGrosvenor/swerver/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/servers/nginx/config/nginx.conf>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/servers/swerver/Dockerfile>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/servers/swerver/config.json>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/servers/swerver/app/build.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/servers/swerver/app/main.zig>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/k6/Dockerfile>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/k6/lib/helpers.js>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/k6/scenarios/throughput.js>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/k6/scenarios/connections.js>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/k6/scenarios/rapid-fire.js>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/k6/scenarios/error-handling.js>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/k6/scenarios/latency.js>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/HEAD/scripts/run-benchmark.sh>
  - <https://github.com/justinGrosvenor/swerver-benchmarks/tree/main/k6/scenarios>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/f5eb7c1658670fee623337979ed12d3827abcdfe/servers/swerver/Dockerfile>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/f5eb7c1658670fee623337979ed12d3827abcdfe/servers/nginx/Dockerfile>
  - <https://raw.githubusercontent.com/justinGrosvenor/swerver-benchmarks/f5eb7c1658670fee623337979ed12d3827abcdfe/servers/nginx/config/nginx.conf>
  - <https://github.com/MDA2AV/HttpArena>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/swerver>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/swerver/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/swerver/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/swerver/build.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/swerver/main.zig>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/swerver/entrypoint.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/swerver/config-multi.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/nginx/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/swerver.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/h2o.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/zix.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/swerver.json>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/justingrosvenor/swerver`) · [data/wave14/enrich/raw/github_com_justingrosvenor_swerver.json](../../../data/wave14/enrich/raw/github_com_justingrosvenor_swerver.json) (enrichment confidence 0.6)

</details>
