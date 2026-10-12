# Caddy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Go web server and reverse proxy with automatic HTTPS; claimed to beat nginx, but measured 4-14x slower in HttpArena.

| | |
|---|---|
| **Beats** | nginx (C), HTTPS reverse proxy |
| **Claimed result** | No verified win. 'Caddy Outperforms Nginx 4x' is the title of HN item 33725154 (snippet only; the post at https://manishrjain.com/reverse-proxy-caddy-nginx, which the benchmark README credits as its inspiration, could not be opened: getaddrinfo ENOTFOUND). patrickdappollonio/nginx-vs-caddy-benchmark (Vegeta, fixed rate 500 req/s for 10 s, HTTPS reverse proxy to a local container): hello-docker response mean latency nginx 337.36 us vs Caddy 385.502 us (nginx 14% faster per the README); 256K file first run Caddy 1.310211 ms vs nginx 1.536594 ms (Caddy 1.17x, derived from page data) with an untuned nginx.conf; after commit 7cb9315c tuned nginx, nginx 1.192198 ms vs Caddy 1.471049 ms (nginx 23% faster per the README). HttpArena (Caddy v2.8.4 serving directly, not proxying): baseline-4096 431,894 vs nginx 3,284,513 req/s (0.13x), limited-conn-4096 237,689 vs 2,626,297 (0.09x), pipelined-4096 761,137 vs 4,037,345 (0.19x), json-tls-4096 321,964 vs 1,313,755 (0.25x), static-tls-1024 159,177 vs 720,869 (0.22x), baseline-h3-64 360,511 vs 4,849,624 (0.07x); ratios derived from page data. |
| **Workload** | Claim: HTTPS reverse proxying (HN title only). Opened benchmark: Vegeta open-loop attack at 500 req/s for 10 s against https://localhost/ through Caddy or nginx in Docker, proxying to patrickdappollonio/hello-docker (20-byte reply) or to docker-http-server serving a 256K data.bin; metric is latency at a fixed rate, not throughput. Cross-check: HttpArena HTTP/1.1, TLS, h2 and h3 origin-serving profiles with custom Go handler modules in Caddy and a custom C module in nginx. |
| **Metric** | throughput |
| **Hardware** | patrickdappollonio benchmark: laptop, 6-core Intel Core i7-10710U, 15.7 GB RAM, Pop!_OS 22.04 LTS, kernel 6.0.6. HttpArena: AMD Ryzen Threadripper PRO 3995WX (64 cores, 128 threads), server container pinned to cpuset 0-31,64-95 (32 cores, 64 threads) per scripts/lib/profiles.sh. |
| **Compiler and flags** | patrickdappollonio benchmark: unpinned caddy:latest and nginx:latest images, no versions or build flags stated. HttpArena cross-check: Caddy v2.8.4 built with xcaddy on golang:1.22-bookworm with the httparena and httparena_json handler modules; nginx 1.31.4 built with --with-cc-opt='-O3 -march=native -DNDEBUG'. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 77.8k stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/caddyserver/caddy) · [benchmark](https://github.com/patrickdappollonio/nginx-vs-caddy-benchmark) |

## Verdict

No opened measurement shows Caddy beating a configured nginx; the '4x' exists only as an HN title. In one Vegeta run (fixed 500 req/s, HTTPS reverse proxy to a local container, i7-10710U laptop, unpinned caddy:latest and nginx:latest), nginx had 14% lower mean latency on a 20-byte reply and, once its config was tuned, 23% lower on a 256 KiB body; Caddy's only win (1.17x) was against the untuned config. HttpArena (Threadripper PRO 3995WX, 32 cores and 64 threads for the server) puts Caddy v2.8.4 as an origin server at 0.07x to 0.25x of nginx 1.31.4's requests per second; nginx there is built at -O3 -march=native with a C handler module.

## Use it when

- Many hostnames that need certificates issued and renewed automatically (ACME, on-demand TLS, internal CA), where operational simplicity matters more than peak requests per second.
- TLS termination and reverse proxying in front of application servers at moderate load, where the upstream dominates latency; at a fixed 500 req/s the only same-workload test had nginx ahead by 14-23% on mean latency, which is small next to typical app latency.
- Deployments that want HTTP/3 and HTTP/2 on by default (protocols h1 h2 h3) and Encrypted ClientHello without extra configuration.
- Teams that prefer extending the server in memory-safe Go modules and changing config through a JSON API rather than C modules, Lua and reloads.

## Skip it when

- Edge or proxy tiers sized for maximum throughput per core: HttpArena baseline-4096 431,894 req/s against nginx 3,284,513 (0.13x), json-tls-4096 0.25x, baseline-h3-64 0.07x (derived from page data).
- Tail-latency-sensitive services at high connection counts: HttpArena p99 113.50 ms vs nginx 6.79 ms on baseline-4096 and 1.99 s vs 52.31 ms on json-tls-4096.
- Static files over HTTP/3 under load: static-h3-64 reached 22,218 req/s at 897% CPU against nginx's 361,025, so the QUIC path was the bottleneck rather than the cores.
- Pipelined HTTP/1.1 clients: Go's net/http answers pipelined requests one at a time per connection (pipelined-4096 761,137 vs nginx 4,037,345 req/s).
- Setups that depend on nginx.conf, njs or OpenResty Lua modules, since none of them carry over.

## How it is fast

No opened measurement shows it beating nginx; it is catalogued as a refuted claim. Its request path is Go's net/http (one goroutine per connection on the runtime's epoll netpoller), crypto/tls and quic-go. reverse_proxy reuses pooled upstream connections by default (http.Transport, MaxIdleConnsPerHost 32, 2-minute idle timeout), copies bodies through a sync.Pool of 32 KiB buffers, and streams responses instead of buffering them; automaxprocs and automemlimit fit GOMAXPROCS and GOMEMLIMIT to container limits. In HttpArena its custom-handler rows land at 0.64x (pipelined) to 1.40x (limited-conn) of a plain Go net/http server (go-stdlib; baseline-4096 0.86x), so its ceiling is net/http's per-request cost, not Caddy's middleware (derived from page data).

## Compared with alternatives

Pick Caddy over Traefik, the other Go reverse proxy here, when you configure by file or JSON and want automatic HTTPS with a local CA rather than container-label discovery. For raw proxy throughput neither is the pick: nginx itself, or routez and rproxy, which publish reverse-proxy numbers ahead of nginx, are the candidates to test.

## Integration

| | |
|---|---|
| **Form** | standalone server binary; also a Go module (github.com/caddyserver/caddy/v2) for plugins built with xcaddy |
| **Dependencies** | none at run time (static Go binary, no libc per the README); built on certmagic, quic-go, zap, klauspost/compress, automaxprocs and automemlimit |
| **Minimum toolchain** | Go 1.26.0 to build from source (README and go.mod) |
| **Platforms** | Any OS and architecture Go targets; prebuilt binaries on GitHub Releases |
| **Thread safety** | Not applicable as a library. Each request runs on its own goroutine, so custom handler modules must be safe for concurrent use. |
| **Drop-in for the baseline** | partial — replaces nginx as a TLS terminator, static server and reverse proxy at the deployment level, but needs a rewritten config (Caddyfile or JSON) and has no nginx module compatibility |

## Gotchas

- Harness flaw in the benchmark_url test, in every run: Vegeta sends HTTP/2 when the server offers it (-http2 defaults to true), Caddy offers h2 by ALPN by default, and the nginx server block is 'listen 443 ssl' without http2. So Caddy was measured over HTTP/2 and nginx over HTTP/1.1. The nginx upstream block also has no 'keepalive' directive, so nginx opened a new TCP connection to the backend for each request while Caddy reused pooled ones. Both asymmetries favour Caddy, and the tuned nginx still won.
- The one Caddy win (256K mean 1.310211 ms vs 1.536594 ms) used the first nginx.conf (commit 0b7fd55). That config had worker_connections 1024, access logging on and no proxy_http_version, so nginx proxied over HTTP/1.0. Neither config sets proxy_buffers, so nginx proxied the 256 KiB body through its default buffers (8 x 4k/8k), which can spill to a temporary file.
- The HttpArena Caddy rows are stale: Caddy v2.8.4 built on golang:1.22 with xcaddy, while the go-stdlib row uses Go 1.26 and Caddy is now at v2.11.7 (2026-10-03). v2.11.6 cut allocations in the request hot path and in reverse_proxy, and v2.11.7 roughly halved per-handshake certificate lookup time. Even so, plain net/http on Go 1.26 reaches only 504,598 req/s on baseline-4096, about 0.15x of nginx.
- GC pauses: commenters on the Tyblog Caddy-vs-nginx benchmark reported latency spikes during Go garbage collection, while nginx stayed under 32 MB (search snippet only). In HttpArena Caddy used less memory than nginx's tuned build (80 MiB to 2.3 GiB vs 3.5 to 3.8 GiB), so memory results depend on the configuration.

## Known shortcomings

- The 4x claim is an HN title only (manishrjain.com unreachable); the only win in the patrickdappollonio repo (1.17x at 256K) used an untuned nginx.conf and reversed to nginx 23% faster after commit 7cb9315c; HttpArena Caddy v2.8.4 is 0.07-0.25x of nginx. Not faster.
- Harness flaw in the benchmark_url test, every run: Vegeta sends HTTP/2 when offered (-http2 defaults to true), Caddy offers h2 by ALPN, and the nginx server block is 'listen 443 ssl' without http2, so Caddy was measured over HTTP/2 and nginx over HTTP/1.1; the nginx upstream block has no keepalive directive, so nginx opened a new backend TCP connection per request while Caddy reused pooled ones. Both asymmetries favour Caddy and the tuned nginx still won. Listed as a refuted claim.

## Caveats and trade-offs

Recorded as an unsupported and contradicted claim. The 4x figure is only an HN submission title; the post could not be opened, so its method, versions and configs are unknown. In the opened benchmark (11 stars, no license, 'quick-and-dirty' by its own description) the first nginx.conf had worker_connections 1024 and no sendfile, access_log or upstream HTTP/1.1 settings, so nginx logged every request and proxied over HTTP/1.0 while Caddy ran with its defaults; the author's commit 7cb9315c tuned nginx (worker_connections 4000, access_log off, sendfile, proxy_http_version 1.1) and nginx then won the 256K test by 23% on mean, 13% on p95 and 11% on p99; nginx had already won the hello test by 14% before tuning. The tuned config still has no upstream keepalive directive. Images are unpinned :latest, single runs at a fixed 500 req/s. HttpArena shows Caddy 4x to 14x slower than nginx on every shared row, but it tests Caddy v2.8.4 (2024, Go 1.22) as an origin server with custom handler modules rather than as a reverse proxy, and the Caddy rows (commit 0a18672, 2026-08-15) and nginx rows (commit df1a679, 2026-08-20) come from different runs; the nginx rows at 0a18672 are within about 2% of the later ones on baseline, limited-conn and pipelined and 9% higher on json-tls, so the gap holds either way. The Caddy README makes no performance claim against nginx. [retier] Recorded as an unsupported and contradicted claim. The 4x figure is only an HN submission title; the post could not be opened, so its method, versions and configs are unknown. In the opened benchmark (11 stars, no license, 'quick-and-dirty' by its own description) the first nginx.conf had worker_connections 1024 and no sendfile, access_log or upstream HTTP/1.1 settings; in every run Vegeta sent HTTP/2 to Caddy (offered by ALPN) and HTTP/1.1 to nginx ('listen 443 ssl' without http2), and the nginx upstream block has no keepalive directive, so nginx opened a new backend TCP connection per request while Caddy reused pooled ones. Both asymmetries favour Caddy, and the tuned nginx still won.

Automatic HTTPS and a Go module system; higher CPU and memory per request than nginx; garbage-collected runtime.

## Maintenance

Very active (v2.11.7 released 2026-10-03, last commit 2026-10-10, 77.8k stars, 198 open issues) and Apache-2.0; a production-grade server, but listed here as a refuted speed claim rather than as a faster nginx.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** No opened page supports a Caddy win over a configured nginx: the 4x exists only as an HN submission title (the linked post, manishrjain.com/reverse-proxy-caddy-nginx, did not resolve), the benchmark_url's one Caddy win (256K mean latency 1.310211 ms vs 1.536594 ms) came from an untuned nginx.conf and reversed to nginx 1.23x faster after the author's tuning commit 7cb9315c (crippled-baseline precedent), and HttpArena (public code, A-grade suite) shows Caddy 0.07x to 0.25x of nginx on every shared row.
- **Verifier notes:** Downgraded C to D: no opened page shows Caddy beating a configured nginx; the 4x is an HN title only, the benchmark_url's 1.17x win came from an untuned nginx.conf and reversed to nginx 23% faster after the author's tuning commit 7cb9315c, and HttpArena shows Caddy at 0.07x to 0.25x of nginx (origin serving, Caddy v2.8.4, cross-run rows). Shortcomings to record: not faster, claim unverifiable (post unreachable), crippled nginx config in the only win, unpinned images, latency at a fixed 500 req/s rather than throughput. Metadata confirmed: Apache-2.0, 77.8k stars, last commit 2026-10-10, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-102 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/patrickdappollonio/nginx-vs-caddy-benchmark>
  - <https://github.com/patrickdappollonio/nginx-vs-caddy-benchmark/commit/7cb9315c>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/nginx.conf>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/0b7fd55/nginx.conf>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/Caddyfile>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/docker-compose.caddy.yaml>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/docker-compose.nginx.yaml>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/docker-compose.caddy-alt.yaml>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/docker-compose.nginx-alt.yaml>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/caddy.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/0a18672/site/data/results/caddy.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/df1a679/site/data/results/caddy.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/0a18672/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/df1a679/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/scripts/lib/profiles.sh>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/caddy/Caddyfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/caddy/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/caddy/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/caddy/meta.json>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/caddy>
  - <https://github.com/MDA2AV/HttpArena/commits/main/site/data/results/nginx.json>
  - <https://github.com/caddyserver/caddy>
  - <https://github.com/caddyserver/caddy/commits>
- **Sources the enricher read:**
  - <https://github.com/caddyserver/caddy>
  - <https://github.com/caddyserver/caddy/releases>
  - <https://github.com/caddyserver/caddy/issues?q=is%3Aissue%20label%3Aoptimization>
  - <https://github.com/caddyserver/caddy/issues?q=is%3Aissue%20reverse_proxy%20performance>
  - <https://github.com/caddyserver/caddy/issues/6751>
  - <https://github.com/caddyserver/caddy/issues/5334>
  - <https://raw.githubusercontent.com/caddyserver/caddy/HEAD/README.md>
  - <https://raw.githubusercontent.com/caddyserver/caddy/HEAD/go.mod>
  - <https://raw.githubusercontent.com/caddyserver/caddy/HEAD/modules/caddyhttp/reverseproxy/reverseproxy.go>
  - <https://raw.githubusercontent.com/caddyserver/caddy/HEAD/modules/caddyhttp/reverseproxy/httptransport.go>
  - <https://raw.githubusercontent.com/caddyserver/caddy/HEAD/modules/caddyhttp/reverseproxy/streaming.go>
  - <https://raw.githubusercontent.com/caddyserver/caddy/HEAD/modules/caddyhttp/server.go>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/nginx.conf>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/0b7fd55/nginx.conf>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/Caddyfile>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/docker-compose.caddy.yaml>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/docker-compose.nginx.yaml>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/docker-compose.caddy-alt.yaml>
  - <https://raw.githubusercontent.com/patrickdappollonio/nginx-vs-caddy-benchmark/HEAD/docker-compose.nginx-alt.yaml>
  - <https://raw.githubusercontent.com/tsenart/vegeta/HEAD/README.md>
  - <https://github.com/MDA2AV/HttpArena/tree/main/frameworks/caddy/httparena>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/caddy/Caddyfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/caddy/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/caddy/README.md>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/caddy/meta.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/caddy/httparena/httparena.go>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/caddy/httparena/go.mod>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/frameworks/go-stdlib/Dockerfile>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/current.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/caddy.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/nginx.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/go-stdlib.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/gin.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/echo.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/chi.json>
  - <https://raw.githubusercontent.com/MDA2AV/HttpArena/HEAD/site/data/results/fiber.json>
  - https://blog.tjll.net/reverse-proxy-hot-dog-eating-contest-caddy-vs-nginx/ (blocked: getaddrinfo ENOTFOUND; search snippets only)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/caddyserver/caddy`) · [data/wave14/enrich/raw/github_com_caddyserver_caddy.json](../../../data/wave14/enrich/raw/github_com_caddyserver_caddy.json) (enrichment confidence 0.8)

</details>
