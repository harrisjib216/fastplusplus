# wut-server

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟡 stale

> Single-purpose Rust HTTPS server that returns the caller's IP; one first-party wrk run beat a one-worker nginx 1.49x.

| | |
|---|---|
| **Beats** | nginx (C; own build with all optimization options, LTO, static OpenSSL, ngx_headers_more; 1 worker, 1024 worker connections, HTTP/2, TLS 1.3 only) |
| **Claimed result** | 38,110.60 requests/s (382,057 requests in 10 s) vs nginx 25,650.31 (257,322), about 49% more per the page (1.49x, derived from page data); transfer 3.27 MB/s vs 2.79 MB/s; max latency 279.57 ms vs 520.46 ms; nginx had connect 95 and read 17 socket errors. |
| **Workload** | wrk, 10 s, 6 threads, 1000 connections (from the wrk output header), against https://ip.erix.dev (nginx, port 443) and https://ip.erix.dev:11313 (wut-server) on the same host. Both servers terminate TLS and return the caller's IP address as the body; wrk speaks HTTP/1.1. |
| **Metric** | throughput |
| **Hardware** | Server: single-core AMD EPYC 7302P, 1 GB ECC RAM, 1 Gbit/s uplink; client: AMD Ryzen 5600, 32 GB ECC RAM, 250 Mbit/s uplink; OS not stated; network benchmark, not loopback. |
| **Compiler and flags** | wut-server: Cargo.toml [profile.release] lto = true, codegen-units = 1, strip = true (default opt-level 3); hyper 0.14 with hyper-rustls 0.24, rustls 0.21 and tokio 1.34; rustc version not stated. nginx: 'all optimization options enabled', LTO, static OpenSSL and ngx_headers_more; version, compiler and exact flags not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 0 stars |
| **Last commit** | 2024-03-09 |
| **Links** | [repository](https://github.com/nixigaj/wut-server) · [benchmark](https://github.com/nixigaj/wut-server) |

## Verdict

One first-party wrk run per server (10 s, 6 threads, 1000 connections, HTTPS with HTTP/1.1) from a Ryzen 5600 client over the internet to a single-core EPYC 7302P server: wut-server 38,110.60 req/s against nginx with one worker, LTO and static OpenSSL at 25,650.31 req/s (1.49x, derived from page data), with nginx logging 95 connect and 17 read errors; versions, compiler flags and the wrk command are not given, and the wut-server output is internally inconsistent (see gotchas).

## Use it when

- You need a self-hosted 'what is my IP' endpoint over HTTPS and want a tiny binary instead of an nginx config.
- Clients connect directly (no reverse proxy or load balancer in front), because the answer is the TCP peer address.
- As a minimal hyper 0.14 + rustls example of a TLS server with ALPN for HTTP/1.1 and HTTP/2.

## Skip it when

- Anything beyond echoing the client IP: no routing, static files, headers, proxying or configuration file.
- Behind a proxy, CDN or load balancer: there is no X-Forwarded-For or PROXY-protocol support, so it reports the proxy's address.
- Where you need current, patched dependencies: the lockfile pins h2 0.3.24, hyper 0.14 and rustls 0.21, and the project has been idle since March 2024.
- Deployments that renew certificates without restarts: certificates are read once at startup and hot reload is only listed as planned.
- Windows: shutdown handling uses tokio::signal::unix, so it builds only on Unix.

## How it is fast

There is no special technique: it is about 290 lines on hyper 0.14 + tokio 1.35 with rustls 0.21 (ring) for TLS, built with LTO, codegen-units = 1 and strip. The IP string is formatted once per connection in make_service_fn and cloned into each response, so a keep-alive connection only clones a short string per request, and hyper's response carries only date and content-length headers (about 90 bytes per response against nginx's 114, derived from page data). Any throughput gap against nginx comes from different TLS stacks and runtimes, not from a language effect.

## Compared with alternatives

Pick it only when the job is literally 'return the client IP over TLS'; for a general static-response server that beats nginx, statico (Rust, tokio or monoio, measured against nginx 'return' at 1 and 4 threads) or routez (fixed and TLS responses against nginx and HAProxy) have broader evidence, and the HttpArena tokio entry is the better-measured raw-tokio data point.

## Integration

| | |
|---|---|
| **Form** | binary (Cargo project; not published on crates.io) |
| **Dependencies** | hyper 0.14.28, hyper-rustls 0.24.2, rustls 0.21.10 (ring 0.17), tokio 1.35.1, tokio-rustls 0.24.1, h2 0.3.24, clap 4.4, anyhow, env_logger, log, rustls-pemfile 1, futures-util |
| **Minimum toolchain** | Rust 2021 edition; exact MSRV not documented |
| **Platforms** | Unix (uses tokio::signal::unix); no architecture-specific code |
| **Thread safety** | tokio multi-thread runtime via #[tokio::main]; per-connection state only, plus one shared atomic counter |
| **Drop-in for the baseline** | partial: replaces only an nginx server block of the form 'return 200 "\$remote_addr"'; nothing else nginx does |

## Gotchas

- Harness inconsistency (derived from page data): the wut-server wrk output reports 38,110.60 req/s at 45.00 ms average latency, which by Little's law needs about 1,715 requests in flight, but wrk with 6 threads and 1000 connections opens 996 connections with one request each, capping throughput near 22,100 req/s at that latency. The nginx run is consistent (about 720 in flight). So the wut-server output was not a plain single-request-per-connection wrk run as printed (an unshown pipelining script, or output from different runs); the wrk command line and any script are not published.
- The server's own 'Requests per second' log counts connections, not requests (the counter is incremented in make_service_fn, once per connection), and start_counter stores the interval delta in prev_elapsed_time instead of the cumulative time, so per-interval rates are wrong after the second interval; the server log cannot cross-check the wrk numbers.
- Cargo.lock pins h2 0.3.24, inside RUSTSEC-2024-0332 (CONTINUATION frame flood, patched in 0.3.26), and HTTP/2 is enabled by default through with_all_versions_alpn; rustls 0.21.10 is inside RUSTSEC-2024-0336's range, though that advisory says the tokio-rustls path is not affected. Run cargo update before deploying.
- Default bind is 127.0.0.1:11313 and [::1]:11313, so it is unreachable from outside until -b is set; the private key file must hold exactly one key (EC, PKCS#8 or RSA) or startup fails.

## Known shortcomings

- Single non-interleaved first-party run; TLS stacks differ (rustls/ring vs static OpenSSL); both servers terminate TLS; nginx logged 95 connect errors.
- Harness flaw: the wut-server wrk output fails Little's law: 38,110.60 req/s at 45.00 ms average latency needs about 1,715 requests in flight, but wrk opened 996 connections, so about 22,100 req/s is the maximum at that latency; either an unshown pipelining script or not one plain run. The nginx run is consistent (about 720 in flight); bytes per response check out (90 vs 114, nginx's extra Connection header). The server log counts connections, not requests. Cargo.lock pins h2 0.3.24 (RUSTSEC-2024-0332).

## Caveats and trade-offs

First-party single run per server, with no variance, no wrk command line, no versions, and the two runs were not interleaved. The author calls it a 'non-scientific comparison'. Both servers use TLS 1.3 over HTTPS (the wut-server wrk URL is https://...:11313, and the binary requires --cert-path and --key-path), but the TLS stacks differ: rustls 0.21 with ring on the Rust side, statically linked OpenSSL in nginx. Average latency is higher for wut-server (45.00 ms vs 28.07 ms), while max latency is lower (279.57 ms vs 520.46 ms). nginx logged 95 connect and 17 read socket errors, so it served fewer than the 1000 connections. wut-server formats the client IP once per connection, while nginx evaluates \$remote_addr per request. The benchmark harness is not in the repo. The repo has 2 commits and 0 stars. [retier] The wut-server wrk output fails Little's law: 38,110.60 req/s at 45.00 ms average latency needs about 1,715 requests in flight, but wrk opened 996 connections, so about 22,100 req/s is the maximum at that latency; either an unshown pipelining script or not one plain run. The nginx run is consistent (about 720 in flight); bytes per response check out (90 vs 114). The server log counts connections, not requests. Cargo.lock pins h2 0.3.24 (RUSTSEC-2024-0332).

Single-purpose server that returns the caller's public IP over HTTP and HTTP/2; not a general web server.

## Maintenance

Stale since 2024-03-09 (2 commits, the second a README typo fix; 0 stars; no issues; not on crates.io) but MIT-licensed and small enough to copy, with superseded hyper 0.14 and rustls 0.21 dependencies that need upgrading; the speed claim should be treated as unreliable because the published wrk output fails a Little's-law check.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The README has first-party, self-described 'non-scientific' wrk output for nginx and wut-server (25,650.31 vs 38,110.60 req/s) with the CPU models and the nginx config. The nginx version, compiler, flags and wrk command line are not given, and the harness is not in the repo, so C.
- **Retiered** C to D: Enricher: the wut-server wrk output violates Little's law (38,110 req/s at 45 ms average latency needs about 1,715 requests in flight on 996 connections), so the headline is not one plain run as shown; a single non-interleaved first-party run with no valid measurement: C to D.
- **Verifier notes:** README numbers match the record (38,110.60 vs 25,650.31 req/s, about 49% more per the page). The record's caveat that wut-server might not terminate TLS was wrong and is corrected: both sides serve HTTPS. Shortcomings: single non-interleaved first-party run, different TLS libraries (rustls/ring vs OpenSSL) so the win is not a language effect, nginx connect errors, higher average latency, versions unstated. Metadata confirmed: MIT, 0 stars, last commit 2024-03-09, stale.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-44 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/nixigaj/wut-server>
  - <https://github.com/nixigaj/wut-server/commits>
  - <https://raw.githubusercontent.com/nixigaj/wut-server/HEAD/README.md>
  - <https://raw.githubusercontent.com/nixigaj/wut-server/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/nixigaj/wut-server/HEAD/src/main.rs>
- **Sources the enricher read:**
  - <https://github.com/nixigaj/wut-server>
  - <https://github.com/nixigaj/wut-server/commits>
  - <https://github.com/nixigaj/wut-server/commit/fee006a>
  - <https://github.com/nixigaj/wut-server/issues?q=is%3Aissue>
  - <https://github.com/nixigaj/wut-server/tree/master/example_certs>
  - <https://raw.githubusercontent.com/nixigaj/wut-server/HEAD/README.md>
  - <https://raw.githubusercontent.com/nixigaj/wut-server/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/nixigaj/wut-server/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/nixigaj/wut-server/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/nixigaj/wut-server/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/hyperium/hyper/v0.14.28/src/server/tcp.rs>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/h2/RUSTSEC-2024-0332.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/rustls/RUSTSEC-2024-0336.md>
  - <https://github.com/nixigaj/wut>
  - <https://crates.io/api/v1/crates/wut-server>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/nixigaj/wut-server`) · [data/wave14/enrich/raw/github_com_nixigaj_wut_server.json](../../../data/wave14/enrich/raw/github_com_nixigaj_wut_server.json) (enrichment confidence 0.6)

</details>
