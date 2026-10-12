# routez

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Zig` · `no license` · 🟢 active

> nginx-style edge server in pure Zig (HTTP/1.1, TLS 1.3, HTTP/3, proxy); beats nginx on fixed, proxied and TLS keep-alive rows.

| | |
|---|---|
| **Beats** | nginx 1.30.5 (C) and HAProxy 3.2.23 (C) |
| **Claimed result** | requests/s routez vs nginx: fixed response 627k vs 529k (1.19x, derived from page data), reverse proxy to keep-alive upstream 262k vs 208k (1.26x), TLS fixed response 582k vs 324k (1.8x), TLS 10 KB static file 208k vs 152k (1.4x), TLS new connection per request 17k vs 13k; p99 at a held 208k req/s fixed response 3.6 ms vs nginx 21.2 ms. |
| **Workload** | nginx-style edge server in Zig 0.17 measured with wrk, keep-alive, 256 connections, 3 workers each, median of 3 x 10 s runs, on Docker Desktop on an Apple M-series Mac (10 cores). |
| **Metric** | throughput |
| **Hardware** | Apple M-series Mac, 10 cores, Docker Desktop VM (the author writes 'a VM is not a benchmark machine'), 20 Sep 2026 |
| **Compiler and flags** | routez: zig build -Doptimize=ReleaseFast -Dcpu=native (native+aes+sha2 on arm64) with Zig 0.17.0 inside an ubuntu:26.04 container (bench/lib.sh, bench/Dockerfile); nginx 1.30.5 is the nginx.org stable Ubuntu package and HAProxy 3.2 comes from the vbernat PPA, both on OpenSSL 3.5, with compile flags not stated. nginx config (bench/conf/nginx.conf) is tuned: reuseport, keepalive_requests 100000, open_file_cache, sendfile, TLS 1.3 pinned to AES-128-GCM and X25519. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Worker threads with SO_REUSEPORT on libxev, an open-file cache and sendfile for plain-HTTP static files (README feature list); no profile attribution for the wins. |
| **Adoption** | 6 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/endel/routez) · [benchmark](https://raw.githubusercontent.com/endel/routez/HEAD/README.md) |

## Verdict

First-party wrk runs (256 keep-alive connections, 3 workers per server, pinned cores, median of 3 x 10 s) on Docker Desktop on an Apple M-series Mac, 20 Sep 2026, routez 53d2011 built ReleaseFast -Dcpu=native with Zig 0.17.0 against nginx 1.30.5 and HAProxy 3.2.23 packages on OpenSSL 3.5: fixed response 627k vs nginx 529k (1.19x), keep-alive proxy 262k vs 208k (1.26x), TLS fixed response 582k vs 324k (1.8x), TLS 10 KB file 208k vs 152k (1.37x), resumed TLS new connections 17k vs 13k; the plain 10 KB static file is a tie and many other rows lose.

## Use it when

- Small-response or keep-alive HTTP/1.1 front ends where the author's rows show it ahead of nginx: fixed responses (627k vs 529k req/s) and proxying to a keep-alive upstream (262k vs 208k).
- TLS 1.3 termination of keep-alive traffic with ECDSA or Ed25519 certificates: TLS fixed response 582k vs 324k and TLS 10 KB file 208k vs 152k in its table.
- Many idle WebSocket tunnels where memory per connection matters (5.3 KB vs nginx 17.8 KB at 50k connections in its ws suite).
- Experiments or study of a modern edge server whose benchmark harness gates response bodies and TLS parameters before measuring and publishes its losing rows.

## Skip it when

- Anything you need to ship or modify: the repo has no LICENSE file, so it is reference only.
- RSA certificates, handshake-heavy traffic or TLS 1.2 clients: full RSA-2048 handshakes run 1.0k/s vs nginx 3.6k/s, ECDSA 7.1k vs HAProxy 8.8k, and TLS 1.2 is not supported.
- HTTP/3 serving, on-the-fly gzip or large proxied responses: it trails on HTTP/3 10 KB (94k vs 247k) and 1 MB files, gzip through the proxy (5.5k vs HAProxy 15k) and 1 MB proxied responses (4.7k vs 7.5k).
- Tail-latency-sensitive proxying or frequent reloads: held-rate proxied p99 4.30 ms vs HAProxy 1.79 ms, 27% vs 56% throughput kept under a connection storm, and 74 failed requests vs 0 with a reload every 2 s.
- Production deployments generally: 6 stars, one author, and its TLS/QUIC dependency quic-zig says 'Not production-ready' in its README.

## How it is fast

Each worker thread runs its own libxev event loop (quic-zig selects libxev's epoll backend on Linux, the same readiness model nginx uses) on its own SO_REUSEPORT listener. Static files go through a per-worker open-file cache and, when the page cache holds the data (openat2 RESOLVE_CACHED, RWF_NOWAIT or mincore), are served inline on the worker; plain-HTTP bodies over 32 KiB use sendfile and layer-4 bulk traffic uses splice(2). TLS is quic-zig's sans-IO TLS 1.3 in Zig using hardware AES-128-GCM when built with -Dcpu=native(+aes+sha2). The README gives no profile that explains the fixed-response and TLS keep-alive wins.

## Compared with alternatives

Pick routez over proxy-only claimants such as rproxy, Arc or Spire when you want static files, TLS, HTTP/3 and ACME in one process and a harness that gates identical bodies and TLS parameters and publishes its losses; the HttpArena entries (zeemo, zix, vanilla) are application servers with custom handlers, not nginx replacements. The missing license rules it out wherever code must be reused.

## Integration

| | |
|---|---|
| **Form** | standalone server executable built from source (zig build -Doptimize=ReleaseFast) |
| **Dependencies** | libc; endel/quic-zig as a sibling checkout referenced by path (MIT), which pins a fork of libxev (endel/libxev 8cc9850) |
| **Minimum toolchain** | Zig 0.17.0 (minimum_zig_version in build.zig.zon) |
| **Platforms** | Linux (epoll, SO_REUSEPORT spreads connections across workers); macOS builds on kqueue but does not spread connections across SO_REUSEPORT listeners, so extra workers do not help; on arm64 the build must detect AES or TLS falls back to software |
| **Thread safety** | Not a library; worker threads each own an event loop, with a shared pool of file I/O threads (4 by default); upstream pools and health state are per worker. |
| **Drop-in for the baseline** | partial — nginx-like semantics and directives, but a ZON config instead of nginx.conf, TLS 1.3 only, a backtracking-free PCRE subset (no backreferences or lookaround), gzip-only on-the-fly compression and HTTP-01-only ACME |

## Gotchas

- No license: the repo has no LICENSE file and GitHub shows none, so code cannot be copied; quic-zig, which it needs at build time, is MIT.
- Benchmark caveats from the harness code: the bench.sh gate compares status and body only (headers are not compared, though routez does send Server and Date like nginx), and the held-rate suite (rate.sh, oha at half the slowest server's peak from a separate 4 s wrk pass) checks only for status 200. All rows come from Docker Desktop on an unnamed Apple M-series Mac, where the author saw 90% drift between separate runs, and the 10 KB static row reads 308k vs 312k (a tie) in the main table but '343k/s, 10% ahead' in the 'come off this list' table.
- routez is built -Dcpu=native (native+aes+sha2 on arm64) while nginx and HAProxy are generic distribution packages; their OpenSSL 3.5 selects AES and SHA instructions at run time, so this mainly affects non-crypto code. Zig 0.16 builds inside VMs could miss AES entirely and run TLS about 10x slower.
- The open-file cache is on by default: within valid_ms (1 s) a file edited in place is served with its old length and ETag, so a truncated file cuts the response short and a grown one omits the extra bytes.

## Known shortcomings

- Public harness (bench/run.sh, Dockerfile, tuned nginx.conf) but run in a Docker Desktop VM on an unnamed Apple M-series Mac with 90% run-to-run drift admitted in the README; routez built -Dcpu=native against the generic nginx.org package; many losing rows; no LICENSE (reference).
- No correctness bug behind the headline rows; both sides use epoll (quic-zig picks libxev Epoll on Linux, not io_uring). bench.sh's gate checks status and body only, rate.sh checks status 200 only, and the held rate is 0.5x the slowest server's peak from a separate 4 s wrk pass. Still no LICENSE; quic-zig's README says 'Not production-ready'.

## Caveats and trade-offs

The author's own table is mixed: 10 KB static file 308k vs nginx 312k (a tie); full RSA-2048 TLS handshakes 1.0k/s vs nginx 3.6k/s; HTTP/3 10 KB static file 94k/s vs 247k/s; gzip on the fly through the proxy 5.5k/s vs HAProxy 15k/s; a new connection per request 187k/s vs nginx 231k/s; p99 at a held rate proxied 4.30 ms vs HAProxy 1.79 ms; at the held 208k req/s fixed-response row HAProxy's p99 (3.2 ms) beats routez's 3.6 ms; a reload every 2 s under load fails 74 requests vs HAProxy 0. Rows come from different passes: the 10 KB static row reads 308k (tie) in the main table but '343k/s, 10% ahead' in the 'rows that have come off this list' table. The README itself says two runs of one build on a busy Mac differed by 90% and that a VM is not a benchmark machine; numbers are a median of 3 x 10 s runs on Docker Desktop on an unnamed Apple M-series Mac. routez is built with -Dcpu=native while nginx and HAProxy are generic distribution packages. The build needs a sibling checkout of endel/quic-zig (public, MIT). No LICENSE file in the repo (LICENSE returns 404, GitHub shows no license), so usability is reference. Harness strengths: a correctness gate checks byte-identical responses and identical TLS parameters before each row, servers are measured one at a time with rotated order and pinned cores, and nginx gets its best settings. [retier] Both sides use epoll (quic-zig picks libxev Epoll on Linux, not io_uring). bench.sh's gate compares status and body only, rate.sh checks status 200 only, and the held rate is 0.5x the slowest server's peak from a separate 4 s wrk pass. quic-zig's README says 'Not production-ready'.

Pure Zig edge server with HTTP/1.1, HTTP/3, TLS 1.3, ACME, reverse proxy and load balancing; no license file found, so reference only.

## Maintenance

Actively developed (192 commits, last 2026-10-03) by one author with 6 stars and 0 forks; no license, so reference only, and it depends on quic-zig, which describes itself as not production-ready.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Benchmark code is public (bench/run.sh, bench/bench.sh, bench/lib.sh, bench/Dockerfile, bench/conf/nginx.conf, bench/workloads.txt) and the routez build flags are stated, but the hardware is 'Apple M-series Mac (10 cores)' under a Docker Desktop VM (no CPU model) and nginx is a distribution package with unstated compile flags, so not A; first-party, so C.
- **Verifier notes:** All claimed numbers match README.md (fixed 627k vs 529k, proxy 262k vs 208k, TLS fixed 582k vs 324k, TLS 10 KB 208k vs 152k, TLS new connection 17k vs 13k, p99 3.6 vs 21.2 ms). Shortcomings to record: VM on a vague Apple M-series host, single first-party run set with a stated 90% run-to-run drift, native-tuned routez vs generic nginx package, many rows where routez loses, no license. Metadata checked: 6 stars, 0 forks, not a fork, last commit 2026-10-03 (active).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-20 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/endel/routez/HEAD/README.md>
  - <https://github.com/endel/routez>
  - <https://github.com/endel/routez/commits>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/run.sh>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/workloads.txt>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/Dockerfile>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/bench.sh>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/lib.sh>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/conf/nginx.conf>
  - <https://github.com/endel/quic-zig>
- **Sources the enricher read:**
  - <https://github.com/endel/routez>
  - <https://github.com/endel/routez/tree/main/src>
  - <https://github.com/endel/routez/tree/main/src/http1>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/README.md>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/build.zig>
  - https://raw.githubusercontent.com/endel/routez/HEAD/LICENSE (404)
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/run.sh>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/bench.sh>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/rate.sh>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/lib.sh>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/Dockerfile>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/workloads.txt>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/report.lua>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/report.py>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/conf/nginx.conf>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/conf/haproxy.cfg>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/conf/routez.zon>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/conf/upstream.conf>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/bench/conf/wrk-openssl.cnf>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/src/http1/server_conn.zig>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/src/worker.zig>
  - <https://raw.githubusercontent.com/endel/routez/HEAD/src/exchange.zig>
  - <https://raw.githubusercontent.com/endel/quic-zig/HEAD/README.md>
  - <https://raw.githubusercontent.com/endel/quic-zig/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/endel/quic-zig/HEAD/build.zig>
  - <https://raw.githubusercontent.com/endel/quic-zig/HEAD/src/lib.zig>
  - <https://raw.githubusercontent.com/endel/quic-zig/HEAD/src/event_loop.zig>
  - <https://raw.githubusercontent.com/endel/quic-zig/HEAD/src/xev_backend.zig>
  - <https://github.com/endel/quic-zig/tree/main/src/tls>
  - <https://raw.githubusercontent.com/endel/quic-zig/HEAD/src/tls/common.zig>
  - <https://raw.githubusercontent.com/endel/quic-zig/HEAD/src/tls/server.zig>
  - <https://raw.githubusercontent.com/endel/libxev/8cc9850dd27ee906a68e1cb94afb26bc775f7a92/src/main.zig>
  - <https://raw.githubusercontent.com/endel/libxev/8cc9850dd27ee906a68e1cb94afb26bc775f7a92/src/backend.zig>
  - <https://raw.githubusercontent.com/endel/libxev/8cc9850dd27ee906a68e1cb94afb26bc775f7a92/build.zig>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/endel/routez`) · [data/wave14/enrich/raw/github_com_endel_routez.json](../../../data/wave14/enrich/raw/github_com_endel_routez.json) (enrichment confidence 0.45)

</details>
