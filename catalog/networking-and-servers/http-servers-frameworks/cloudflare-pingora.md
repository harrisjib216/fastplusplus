# Pingora

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust async framework for building HTTP proxies; replaced Cloudflare's NGINX-based edge proxy with less CPU, memory and TTFB.

| | |
|---|---|
| **Beats** | nginx |
| **Claimed result** | 5ms lower median TTFB, 80ms lower p95 TTFB, \~70% less CPU and \~67% less memory at equivalent traffic; one customer's connection reuse ratio rose from 87.1% to 99.92% (160x fewer new origin connections) (verbatim from blog) |
| **Workload** | Cloudflare production edge traffic, comparing the retired NGINX-based proxy service to Pingora at scale (real production load, not a synthetic benchmark) |
| **Metric** | latency |
| **Adoption** | 27.5k stars; runs Cloudflare's production edge proxy |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/cloudflare/pingora) · [benchmark](https://blog.cloudflare.com/how-we-built-pingora-the-proxy-that-connects-cloudflare-to-the-internet/) |

## Verdict

Cloudflare's 2022 blog compares production edge traffic on Pingora with its retired NGINX-based proxy: 5 ms lower median and 80 ms lower p95 TTFB, about 70% less CPU and 67% less memory for the same load, and one customer's upstream connection reuse rising from 87.1% to 99.92% (160x fewer new origin connections). These are unreproducible production aggregates with no hardware, compiler or methodology stated, and the blog attributes the latency gain to cross-thread connection sharing rather than faster code.

## Use it when

- Building a custom reverse proxy, API gateway or load balancer in Rust where routing, retry and header logic must be code rather than config
- High-connection-count proxying to many origins where per-worker pools in NGINX give low upstream connection reuse and extra TLS handshakes
- Replacing an OpenResty/Lua or C/C++ proxy module with memory-safe code while keeping phase-style request/response hooks
- Linux x86_64 or aarch64 deployments that need zero-downtime binary upgrades via listening-socket handoff
- gRPC and WebSocket proxying with pluggable TLS backends (OpenSSL, BoringSSL, s2n-tls)

## Skip it when

- You want a configurable server you run without writing Rust: there is no config language, static file serving (issue #40 still open) or module ecosystem comparable to nginx
- Short-lived upstream connections or simple pass-through proxying: in one user's 8-core wrk test (issue #372) Pingora matched nginx at \~30K req/s but used \~70% CPU vs \~50%; it only pulled ahead (\~50K req/s) with upstream keepalive, at \~80% CPU
- You need HTTP/3/QUIC: issue #95 is still open and labeled 'Long Term Goal'
- You need a stable API or non-Linux production: pre-1.0 (0.9.0, 2026-09-04) with breaking changes each minor release, caching labeled experimental, macOS best-effort and Windows community-only
- Running versions before 0.8.0 on untrusted traffic: two critical request-smuggling CVEs (CVE-2026-2833, CVE-2026-2835) and a cache-poisoning CVE (CVE-2026-2836) were fixed only in 0.8.0

## How it is fast

One multithreaded process on Tokio instead of NGINX's worker processes, so upstream connection pools are shared across all threads; Cloudflare says the TTFB gain comes from this connection reuse, not faster per-request code. The pool keeps a small lock-free hot queue (crossbeam ArrayQueue, 16 slots) per connection group in front of a mutex-protected map. pingora-runtime adds a non-work-stealing multi-thread runtime (N isolated single-threaded Tokio runtimes), and pingora-timeout replaces tokio::time::timeout with lazily-armed timers rounded to 10 ms ticks and shared across timeouts (claimed \~4 ns vs \~107 ns per iteration).

## Compared with alternatives

Pick Pingora over H2O or Sogou Workflow when the job is a programmable reverse proxy or load balancer and you want Rust memory safety plus upstream connection pools shared across threads; pick H2O for a configurable HTTP server with static files, or Workflow for a C++ server/client framework with a published QPS benchmark against nginx.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio, h2, httparse, http, bytes, parking_lot, crossbeam-queue, flate2/brotli/zstd and more; TLS via one feature: openssl (needs Perl), boringssl (needs Clang), s2n, or rustls (experimental) |
| **Minimum toolchain** | Rust 1.85 (rolling 6-month MSRV; pingora-foundations needs 1.88) |
| **Platforms** | Linux x86_64 and aarch64 (tier 1); other Unix incl. macOS best-effort with missing features; Windows preliminary/community-only |
| **Thread safety** | Multithreaded by design: each Service owns its own Tokio runtime (work-stealing by default, or N isolated single-threaded runtimes), one task per downstream connection; your ProxyHttp impl and its per-request CTX must be Send + Sync |
| **Drop-in for the baseline** | partial — replaces nginx's reverse-proxy role only after you write the proxy logic in Rust; no nginx.conf compatibility, no static file serving or nginx modules |

## Gotchas

- Only one TLS feature (openssl, boringssl, s2n, rustls) can be enabled at a time; with none, only plaintext HTTP is available, and rustls is marked highly experimental
- Connection reuse is keyed on the full Peer (IP:port, scheme, SNI, client cert, verification and proxy settings); any difference means a separate pool, and idle_timeout 0 disables pooling
- Before 0.8.0 the default cache key ignored the Host header (CVE-2026-2836); the default was removed and you must write your own cache key callback
- Several users reported memory that grows under load and does not come back (issues #372, #447); a contributor suggested jemalloc, and an empty-PoolNode leak (#748) was fixed only in 0.9.0

## Known shortcomings

- No reproducible benchmark: the numbers are 2022 production aggregates with no hardware or method, and the blog attributes the TTFB gain to connection pools shared across threads, not faster code. An independent test (#372, 2024, wrk -c1000, 8 cores, pass-through proxy) found no gain over nginx (29,767 vs 30,014 req/s) at higher CPU (\~70% vs \~50%) until upstream keepalive was on (\~49-51K req/s); ab (HTTP/1.0) requests timed out. Five advisories: request smuggling (CVE-2025-4366, fixed 0.5.0), MadeYouReset HTTP/2 DoS (CVE-2025-8671, 0.6.0), critical request smuggling (CVE-2026-2833, CVE-2026-2835, CVSS 9.3, 0.8.0), cache poisoning from a Host-less default cache key (CVE-2026-2836, 0.8.0). Memory growth under load reported (#372, #447); empty pool entry leak (#748) fixed only in 0.9.0 (2026-09-04). A Rust library, not an nginx drop-in: no config language or static file serving (#40); pre-1.0 with breaking minors; caching experimental. No HTTP/3 (#95); macOS best-effort, Windows community-only; rustls option highly experimental.

## Caveats and trade-offs

No controlled or reproducible benchmark; aggregate production metrics with no stated hardware or measurement methodology; the blog explicitly says the improvement is 'not because we run code faster'

Pingora is a proxy-building framework/library, not a drop-in nginx replacement or config-compatible server; the blog attributes gains to architecture (shared connection pools, multithreading vs. multiprocessing) rather than raw per-request speed

## Maintenance

Actively maintained by Cloudflare (0.9.0 released 2026-09-04, last commit 2026-09-11), Apache-2.0 and usable as crates today, but pre-1.0 with frequent breaking changes and a caching layer still labeled alpha/experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Cloudflare blog (2022-09-14) states verbatim: '5ms reduction on median TTFB and 80ms reduction on the 95th percentile', '70% less CPU and 67% less memory compared to our old service with the same traffic load', and connection reuse '87.1% to 99.92%... 160x'. These are production aggregates with no benchmark code, hardware or methodology, so C.
- **Verifier notes:** The baseline is Cloudflare's old NGINX-based proxy service. The blog attributes the TTFB gain to connection reuse ('This is not because we run code faster'), so the latency claim is architectural, not per-request speed. Metadata checked: Apache-2.0, 27533 stars, last commit 2026-09-11, not a fork, not archived.
- **Pages the verifier opened:**
  - <https://blog.cloudflare.com/how-we-built-pingora-the-proxy-that-connects-cloudflare-to-the-internet/>
  - <https://github.com/cloudflare/pingora>
- **Sources the enricher read:**
  - <https://github.com/cloudflare/pingora>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/README.md>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/pingora/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/pingora-core/Cargo.toml>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/docs/quick_start.md>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/docs/user_guide/internals.md>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/docs/user_guide/pooling.md>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/docs/user_guide/conf.md>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/docs/user_guide/graceful.md>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/docs/user_guide/panic.md>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/pingora-runtime/src/lib.rs>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/pingora-pool/src/lib.rs>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/pingora-pool/src/connection.rs>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/pingora-timeout/src/lib.rs>
  - <https://blog.cloudflare.com/how-we-built-pingora-the-proxy-that-connects-cloudflare-to-the-internet/>
  - <https://blog.cloudflare.com/pingora-open-source/>
  - <https://github.com/cloudflare/pingora/security>
  - <https://rustsec.org/packages/pingora-core.html>
  - <https://rustsec.org/packages/pingora-cache.html>
  - <https://rustsec.org/advisories/RUSTSEC-2026-0033.html>
  - <https://rustsec.org/advisories/RUSTSEC-2026-0034.html>
  - <https://rustsec.org/advisories/RUSTSEC-2026-0035.html>
  - <https://rustsec.org/advisories/RUSTSEC-2025-0037.html>
  - <https://rustsec.org/advisories/RUSTSEC-2025-0070.html>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/pingora-proxy/src/lib.rs>
  - <https://raw.githubusercontent.com/cloudflare/pingora/main/pingora-proxy/src/proxy_trait.rs>
  - <https://github.com/cloudflare/pingora/issues/372>
  - <https://github.com/cloudflare/pingora/issues/748>
  - <https://github.com/cloudflare/pingora/issues/95>
  - <https://github.com/cloudflare/pingora/issues/40>
  - https://hn.algolia.com/api/v1/search?query=pingora%20benchmark&tags=(story,comment)&hitsPerPage=15
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/cloudflare/pingora`) · [data/wave5/enrich/raw/github_com_cloudflare_pingora.json](../../../data/wave5/enrich/raw/github_com_cloudflare_pingora.json) (enrichment confidence 0.8)

</details>
