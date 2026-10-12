# monolake

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🔴 abandoned

> Rust io_uring thread-per-core proxy framework (ByteDance, archived) edging nginx on small-body HTTPS proxying; slower on plain HTTP.

| | |
|---|---|
| **Beats** | nginx 1.24.0 (C); build flags not stated |
| **Claimed result** | No numbers in the text; four chart images only. Approximate values read from the charts (not stated by the project). HTTPS vs worker threads: 16 threads about 526k req/s vs nginx about 450k (about 1.17x), 12 threads about 436k vs about 370k (about 1.18x), 8 threads about 359k vs about 334k (about 1.07x), 4 threads about 148k vs about 126k. HTTPS vs body size: 512 B about 152k vs about 128k (about 1.19x), 4096 B about 124k vs about 108k (about 1.15x), roughly equal at 8192 B, then nginx ahead at 16384 B (about 55k vs about 59k), 32768 B (about 34k vs about 41k) and 65536 B (about 20k vs about 23k). Plain HTTP: nginx ahead or equal everywhere, 16 threads about 707k vs about 688k (monolake about 0.97x), 4 threads about 194k vs about 168k (about 0.87x), 512 B about 186k vs about 168k (monolake about 0.91x), equal at 32768 and 65536 B. Older tabulated first-party proxy run (benchmark/README.md at commit d02397f, Nov 2024, wrk2, 4-core proxy, nginx backend): HTTPS tiny 141,883.70 req/s vs nginx as proxy 127,167.08 (1.12x, derived from page data), small 116,831.85 vs 114,350.27 (1.02x), medium 63,390.91 vs 62,450.58 (1.02x); HTTP tiny 161,101.29 vs 187,973.44 (0.86x); against Envoy 1.31.0 (C++): HTTP tiny 4.36x, HTTPS tiny 4.15x (derived from page data, Envoy configuration not tuned or stated). |
| **Workload** | HTTP and HTTPS proxy/serving throughput of the Monolake reference proxy (Rust on the io_uring-based monoio runtime) against nginx, measured as requests per second versus response body size (512 B to 64 KiB) and versus worker threads (1 to 16); load generator, nginx configuration and backend setup are not stated. |
| **Metric** | throughput |
| **Hardware** | AWS c6a.8xlarge, AMD EPYC 7R13, 16 cores / 32 threads, 64 GB RAM, Linux 6.1.94-99.176.amzn2023.x86_64 (Amazon Linux 2023.5.20240805), nginx 1.24.0 (README Performance section) |
| **Compiler and flags** | Not stated for the README charts. Repository pins Rust nightly (rust-toolchain.toml); the older benchmark/README.md built Monolake with cargo build --release (a release-lto profile exists in Cargo.toml, use not stated) and installed nginx from the Amazon Linux package (yum), so nginx build flags are the distro's and unstated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | Thread-per-core io_uring runtime (monoio) with no work stealing, versus nginx's epoll workers; the README gives no explicit explanation for the HTTPS win. |
| **Adoption** | 66 stars, 12 forks; README says it was deployed in production at ByteDance |
| **Last commit** | 2025-08-29 |
| **Links** | [repository](https://github.com/cloudwego/monolake) · [benchmark](https://github.com/cloudwego/monolake) |

## Verdict

On an AWS c6a.8xlarge (AMD EPYC 7R13, Amazon Linux 2023, kernel 6.1) the README charts (images only, nginx 1.24.0 with unstated build and config, load generator not named) show Monolake at about 1.15-1.19x nginx's HTTPS requests per second for 512 B-4 KiB bodies and 1.07-1.18x at 8-16 worker threads, a tie at 8 KiB, and nginx ahead for 16-64 KiB HTTPS and for plain HTTP. The only tabulated run (Nov 2024, wrk2, 4-vCPU c5a.xlarge proxy in front of an nginx origin, roughly 340 B to 166 KB responses derived from page data) gives HTTPS 141,884 vs 127,167 req/s tiny (1.12x) and 1.02x small and medium, with nginx ahead on HTTP tiny 187,973 vs 161,101.

## Use it when

- Building a custom Rust gateway on Linux that must speak Thrift/TTHeader or convert HTTP to Thrift, where you are prepared to own the code.
- TLS-terminating reverse proxy for small responses (512 B to 4 KiB) on Linux with io_uring, where the published charts show about 1.1-1.2x nginx requests per second.
- Studying a production-used (at ByteDance) monoio service-composition design (service-async, certain-map, hot-reloaded service factories) before building your own.

## Skip it when

- Plain HTTP proxying: nginx was equal or faster in every published run (Nov 2024 4-vCPU run: 161,101 vs 187,973 req/s tiny, 0.86x; medium 0.79x; README charts nginx ahead or tied).
- Large HTTPS responses (16-64 KiB), where the README charts put nginx ahead.
- Anything needing security updates or support: archived 2025-08-29 with a 'no longer recommended for use' notice, pinned to Rust nightly and rustls 0.21.
- Hostname upstreams: upstream DNS lookups were not cached (issue #114, open at archival; 105 req/s and 23,514 wrk2 timeouts until upstreams were given as IPs).
- Teams wanting nginx feature parity (rewrites, LB health checks, gRPC were open issues #152, #158, #150).

## How it is fast

Thread-per-core: each worker thread runs its own monoio runtime on io_uring (the default runtime type, 32768 ring entries, falling back to the epoll 'legacy' driver if io_uring is unavailable) with no work stealing, so a connection's state stays on one core. The HTTP and Thrift codecs (monoio-http, monoio-thrift) are written for io_uring's owned-buffer I/O, upstream connections are pooled (ConnectionReuseHandler), and monoio is built with its splice feature. HTTPS terminates in rustls 0.21 through monoio-rustls built with unsafe_io, which saves one buffer copy per operation; the project itself never explains its HTTPS edge.

## Compared with alternatives

Pick Monolake only when you want a Rust proxy framework with Thrift support on io_uring and accept an archived codebase; for a plain reverse proxy that beats nginx on HTTP too, routez (1.26x on keep-alive upstream proxying) is the stronger catalogued claim, and statico has a monoio variant for fixed in-memory responses.

## Integration

| | |
|---|---|
| **Form** | crate (monolake 0.3.0, monolake-core, monolake-services 0.3.2 on crates.io, last published 2024-11-16) plus a reference proxy binary |
| **Dependencies** | monoio 0.2, monoio-http, monoio-transports, monoio-thrift, service-async, certain-map, hyper 1 with monoio-compat; default tls feature pulls rustls 0.21 (monoio-rustls) and native-tls (monoio-native-tls, OpenSSL on Linux) |
| **Minimum toolchain** | Rust nightly (rust-toolchain.toml); monolake-services at HEAD uses edition 2024 |
| **Platforms** | Linux with io_uring (docs say kernel 5.1+) for the fast path; epoll fallback on Linux, kqueue on macOS; only x86-64 (AMD EPYC) measured |
| **Thread safety** | Thread-per-core: each worker thread runs its own monoio runtime and gets its own service instances from the broadcast config; library-level guarantees not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The HTTPS comparison is rustls versus OpenSSL: the per-server TLS `stack` setting defaults to rustls (TlsStack #[default] Rustls at both the Nov 2024 benchmark commit d02397f and HEAD) and the benchmark's monolake.toml sets no stack, while nginx came from the Amazon Linux package; the catalogue's earlier note that the default is native-tls is wrong (the default cargo feature only compiles native-tls in alongside rustls).
- Harness flaw in the only tabulated run (benchmark/ at d02397f, removed before archival): wrk2 offered different -R target rates per proxy (HTTPS tiny 160,000 for Monolake vs 150,000 for nginx; HTTP tiny 200,000 vs 210,000; HTTP large 100,000 vs 10,000, where Monolake logged 618 timeouts vs nginx's 22), nginx's HTTPS locations used proxy_buffering off while its HTTP ones buffered, and the large rows move about 10-12 Gbit/s for every proxy, so they look link-bound (derived from page data). The current README charts have no scripts, configs or tables in the repo.
- monolake-services enables monoio-transports' rustls-unsafe-io, which turns on monoio-rustls unsafe_io; that crate's Cargo.toml warns the I/O future must not be dropped before it returns ready. Monolake applies keepalive and upstream read timeouts, so audit cancellation paths before trusting it with untrusted clients.
- Upstream hostnames are resolved without caching (issue #114); `cargo run --config` fails with 'expected string but found table in list' unless written `cargo run -- --config` (issue #162).

## Known shortcomings

- Win only for small-body HTTPS, none for plain HTTP; no flags or nginx config given; an older tabulated run in the removed benchmark/ directory (commit d02397f) shows the HTTPS edge at 1.02-1.12x and the Envoy rows (4x behind) on stock config; repository archived 2025-08-29.
- Record correction: the TLS stack defaults to rustls (TlsStack #[default] Rustls at d02397f and HEAD), not native-tls, and the benchmark config sets no stack, so the HTTPS rows are rustls 0.21 against the distribution's OpenSSL nginx. Harness flaws in the d02397f run: the wrk2 -R targets differ per proxy (HTTPS tiny 160k vs 150k; HTTP large 100k vs 10k, with Monolake 618 timeouts vs nginx 22); nginx proxy_buffering is off for HTTPS only; the large rows are link-bound at about 10-12 Gbit/s. monoio-rustls is built with unsafe_io (dropping a future before it is ready is unsafe); upstream DNS is not cached (#114, open).

## Caveats and trade-offs

First-party charts with no tabulated numbers, so values here are eyeballed from PNGs. The win is confined to HTTPS with small bodies (and more worker threads); plain HTTP and large HTTPS bodies favour nginx or tie. The nginx build and configuration (workers, logging, TLS library), whether the charts measure proxying or direct serving, the body size used in the thread charts and the load generator are not stated for the current charts. Monolake's default tls feature uses monoio-native-tls (OpenSSL on Linux), with rustls also available; which stack the charts used is not stated. An older benchmark/ directory (present at commit d02397f, Nov 2024; gone from HEAD) had wrk2 scripts, a three-machine proxy topology with an nginx backend, and a tabulated 4-core run showing only a 1.02-1.12x HTTPS edge and nginx 14% ahead on HTTP tiny; its Envoy and Traefik rows ran stock configurations, so the 4x lead over Envoy is weak evidence. Repository archived on 2025-08-29 with a notice that the project is no longer recommended. Tier C: first-party, partial methodology. [retier] Record correction: the TLS stack defaults to rustls (TlsStack #[default] Rustls at d02397f and HEAD) and the benchmark config sets no stack, so the HTTPS rows are rustls 0.21 against the distribution's OpenSSL nginx. Harness flaws in the d02397f run: the wrk2 -R targets differ per proxy (HTTPS tiny 160k vs 150k; HTTP large 100k vs 10k, Monolake 618 timeouts vs nginx 22); nginx proxy_buffering is off for HTTPS only; the large rows are link-bound at about 10-12 Gbit/s. monoio-rustls is built with unsafe_io; upstream DNS is not cached (#114, open).

Archived by the owner on 2025-08-29 and marked no longer recommended for use; needs Rust nightly and Linux io_uring (falls back to epoll elsewhere); HTTP/Thrift proxy framework rather than a general web server.

## Maintenance

Archived 2025-08-29 by CloudWeGo as no longer recommended (insufficient engineering resources) despite earlier ByteDance production use; MIT or Apache-2.0, so it can be forked, but it needs Rust nightly, an io_uring kernel and a TLS dependency refresh before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README charts (four PNGs, no tabulated numbers) against nginx 1.24.0 on a stated CPU (AMD EPYC 7R13, c6a.8xlarge), but the scripts behind these charts are not in the repository at HEAD and no compiler flags or nginx configuration are given; an older benchmark/ directory with wrk2 scripts (commit d02397f, removed before archival) lacked flags and a CPU model too.
- **Retiered** C to D: Enricher: the d02397f run drove the two proxies at different wrk2 -R target rates (HTTPS tiny 160k vs 150k; HTTP large 100k vs 10k) with nginx proxy_buffering off for HTTPS only and the large rows link-bound, so the first-party charts are not like-for-like; the TLS stack is rustls, not native-tls as recorded. No valid like-for-like measurement: C to D.
- **Verifier notes:** Chart values in the record check out against the four README PNGs (minor additions: 12-thread HTTPS point, HTTP ties at 32-64 KiB). Found an older tabulated first-party run in the removed benchmark/ directory (commit d02397f) with a smaller HTTPS edge (1.02-1.12x) and an Envoy (C++) comparison; still tier C. Shortcomings to record: eyeballed charts only, win limited to small-body HTTPS, no plain-HTTP win, no flags or nginx config, repository archived.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-50 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/cloudwego/monolake>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/README.md>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/.github/images/https_req_per_sec_vs_body_size.png>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/.github/images/http_req_per_sec_vs_body_size.png>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/.github/images/https_req_per_sec_vs_worker_threads.png>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/.github/images/http_req_per_sec_vs_worker_threads.png>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/docs/overview/_index.md>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/monolake/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/README.md>
  - <https://github.com/cloudwego/monolake/commits/main>
  - <https://github.com/cloudwego/monolake/tree/main/docs>
  - <https://github.com/cloudwego/monolake/tree/main/docs/overview>
  - <https://github.com/cloudwego/monolake/tree/main/.github>
  - <https://github.com/cloudwego/monolake/pull/141>
  - <https://github.com/cloudwego/monolake/pull/141/files>
  - <https://github.com/cloudwego/monolake/pull/142/files>
  - <https://github.com/cloudwego/monolake/pull/165/files>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/README.md>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/monolake/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/docs/overview/_index.md>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/docs/getting-started/_index.md>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/docs/config-guide/_index.md>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/docs/faq/_index.md>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/monolake/src/main.rs>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/monolake/src/factory.rs>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/monolake/src/config/mod.rs>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/monolake-core/src/config/mod.rs>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/monolake-services/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudwego/monolake/HEAD/monolake-services/src/tls/mod.rs>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/README.md>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/proxy/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/proxy/monolake/monolake.toml>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/client/benchmark-monolake-http.sh>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/client/benchmark-monolake-https.sh>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/client/benchmark-nginx-http.sh>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/client/benchmark-nginx-https.sh>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/pipeline-proxy-monolake.sh>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/pipeline-proxy-nginx.sh>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/benchmark/pipeline-client-monolake.sh>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/monolake/src/config/mod.rs>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/monolake/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudwego/monolake/d02397f5f69902adf094e5a847f45f445b74711d/monolake-services/Cargo.toml>
  - <https://raw.githubusercontent.com/monoio-rs/monoio-tls/HEAD/monoio-rustls/Cargo.toml>
  - <https://raw.githubusercontent.com/monoio-rs/monoio-tls/HEAD/monoio-rustls/README.md>
  - <https://raw.githubusercontent.com/monoio-rs/monoio-transports/HEAD/Cargo.toml>
  - <https://github.com/cloudwego/monolake/tree/d02397f5f69902adf094e5a847f45f445b74711d/benchmark>
  - <https://github.com/cloudwego/monolake/tree/main/docs>
  - <https://github.com/cloudwego/monolake/commits/main/.github/images>
  - <https://github.com/cloudwego/monolake/pull/113>
  - <https://github.com/cloudwego/monolake/pull/141>
  - <https://github.com/cloudwego/monolake/pull/146>
  - <https://github.com/cloudwego/monolake/pull/165>
  - <https://github.com/cloudwego/monolake/issues?q=is%3Aissue>
  - <https://github.com/cloudwego/monolake/issues/114>
  - <https://github.com/cloudwego/monolake/issues/116>
  - <https://github.com/cloudwego/monolake/issues/162>
  - <https://crates.io/api/v1/crates/monolake>
  - <https://crates.io/api/v1/crates/monolake-services>
  - <https://crates.io/api/v1/crates/monoio>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/cloudwego/monolake`) · [data/wave14/enrich/raw/github_com_cloudwego_monolake.json](../../../data/wave14/enrich/raw/github_com_cloudwego_monolake.json) (enrichment confidence 0.8)

</details>
