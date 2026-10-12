# Traefik (Go reverse proxy; TLS latency vs Nginx and HAProxy)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Go` · `MIT` · 🟢 active

> Go reverse proxy and load balancer; one small third-party Docker test shows lower TLS (HTTP/2) tail latency than nginx at 5k req/s.

| | |
|---|---|
| **Beats** | Nginx 1.28.3 (C, official nginx:1.28.3 image) and HAProxy 3.3.6 (C, official haproxy:3.3.6 image) in Docker. Configs read: nginx worker_processes auto, epoll, multi_accept, upstream keepalive 64, TLSv1.2/1.3 with ECDHE AES-GCM ciphers, no ssl_session_cache, proxy_buffers 8 4k; HAProxy maxconn 20000, no-tls-tickets, http-reuse always, alpn h2,http/1.1. All proxies use the same self-signed RSA-4096 certificate. |
| **Claimed result** | README Key Findings (approximate best-per-scenario values, 0% errors for all four proxies at 5,000 req/s): HTTPS/1.1 Traefik best mean about 0.48 ms and best P99 about 1.47 ms, Nginx P99 about 24 ms; HTTPS/2 Traefik best mean about 0.46 ms and P99 about 1.37 ms, HAProxy next at about 1.79 ms P99. Plain HTTP/1.1: all four within about 5%, Caddy/HAProxy best mean (about 0.41 ms), HAProxy best P99 (about 1.09 ms), so no Traefik win. The only committed chart (assets/local-results/benchmark.png, generated 2026-04-10) shows mean latency and throughput only: unrestricted HTTPS means are all near or below about 2 ms; in the 2-core restricted run Nginx means are about 32 ms (HTTPS/1.1) and 34 ms (HTTPS/2) against about 1.3 ms for Traefik on HTTPS/1.1 (read from chart, approximate). Per-proxy P99 tables are not published. Note: the 'HTTPS/1.1' row is really HTTP/2 (vegeta -http2 defaults to true and the harness never passes -http2=false). |
| **Workload** | Fixed-rate Vegeta v12.13.0 load of 5,000 req/s for 20 s (5 s warmup per proxy/protocol, shuffled run order) for GET /data.json (\~20 KB static JSON served by an nginx 1.28.3 backend) through each proxy; load generator, proxies and backend share one Docker host. -connections=64 sets only Vegeta's max idle connections per host (MaxIdleConnsPerHost), not the connection count. Both TLS scenarios negotiate HTTP/2 via ALPN (vegeta's -http2 flag defaults to true; nginx listens 'ssl http2', HAProxy advertises 'alpn h2,http/1.1', Go servers advertise h2), so requests are multiplexed over few TLS connections; the plain-HTTP scenario is HTTP/1.1. Run twice: unrestricted and restricted (cpus 2.0, mem_limit 4G per proxy via docker-compose.restricted.yml). |
| **Metric** | latency |
| **Hardware** | Chart footer: host with 24 cores, 29.0 GB RAM, Ubuntu 24.04.4 LTS (CPU model not stated); all containers on the same host; optional restricted run limits each proxy to 2 CPUs (CFS quota) and 4 GB. |
| **Compiler and flags** | Official container images: Nginx 1.28.3, Caddy 2.11.2, Traefik 3.6.13, HAProxy 3.3.6; Vegeta v12.13.0; no compiler flags (prebuilt images) |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 65.2k stars (per the GitHub topic listing) |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/traefik/traefik) · [benchmark](https://github.com/fabianwimberger/reverse-proxy-benchmark) |

## Verdict

In fabianwimberger/reverse-proxy-benchmark (third-party, archived), Vegeta v12.13.0 at a fixed 5,000 req/s for 20 s fetched a \~20 KB JSON through official images of Traefik 3.6.13, nginx 1.28.3, HAProxy 3.3.6 and Caddy 2.11.2 to an nginx backend on one Docker host (24 cores, 29 GB RAM, Ubuntu 24.04.4, CPU model not stated); the README reports Traefik best in both TLS rows (mean \~0.46-0.48 ms, P99 \~1.37-1.47 ms) against nginx P99 \~24 ms and HAProxy \~1.79 ms, with no win on plain HTTP/1.1. Both TLS rows are really HTTP/2, P99 values exist only as README prose, and the chart (means only) shows nginx at \~32-34 ms only in the 2-CPU restricted run.

## Use it when

- Container or Kubernetes platforms where routes appear and disappear often and you want them discovered from labels or CRDs with hot reload instead of templating nginx.conf.
- TLS-terminating edge at moderate fixed request rates (thousands of req/s, not saturation) where clients multiplex HTTP/2 and P99 matters more than peak throughput; the only evidence is one small third-party test.
- Teams that want automatic ACME/Let's Encrypt certificates and built-in metrics without extra modules.
- Small CPU quotas in containers when running Traefik built with Go 1.25+, whose GOMAXPROCS follows the container CPU limit (unlike nginx's worker_processes auto in the tested config).

## Skip it when

- Maximum plaintext throughput: the benchmark's own author credits nginx for plaintext throughput, and the plain HTTP/1.1 row shows no Traefik win (HAProxy best P99 about 1.09 ms). Search snippets of other tests (not opened) point the same way: an August 2026 local lab put NGINX 1.30.4 at 53,359 req/s vs Traefik 3.7.12 at 37,705 (p99 3.40 vs 8.01 ms, no TLS), and HAProxy's 2020 vendor ingress test had HAProxy 42,000 vs Traefik 19,000 req/s.
- CPU- or memory-budgeted deployments where you need numbers: this suite records no CPU or memory use, and Traefik issue #6954 (higher CPU in v2 than v1, TLS involved) was closed in 2023 without a root cause.
- If you need to keep existing nginx.conf logic (rewrites, Lua, caching): configuration is not portable.
- If the decision rests on this benchmark alone: tier C, one archived 0-star repo, no CPU model, prebuilt images, P99 values only as approximate README prose.

## How it is fast

Traefik is not a speed-first design. It serves clients with Go's net/http server and crypto/tls (one goroutine per connection, HTTP/2 streams handled concurrently on goroutines spread over all cores) and forwards with Go's httputil.ReverseProxy, a sync.Pool of 32 KiB copy buffers and a keep-alive upstream pool (maxIdleConnsPerHost 64 in the test). When a client multiplexes everything over one HTTP/2 TLS connection, as Vegeta does here, Traefik spreads those streams across CPUs while nginx serves each connection inside one worker process, which is the most plausible design reason for its lower TLS tail in this test. An experimental fastProxy built on valyala/fasthttp (pkg/proxy/fast, v3.2+, HTTP/1 backends only) exists but was not enabled in the benchmark.

## Compared with alternatives

Pick Traefik over Caddy when you want provider-driven dynamic routing (Docker labels, Kubernetes CRDs) more than Caddy's automatic HTTPS; neither has a verified speed win over nginx, and in this same suite Caddy's restricted TLS row was the slowest of all. Over small first-party proxies such as routez, rproxy or Spire, pick Traefik for maturity and features, not for throughput.

## Integration

| | |
|---|---|
| **Form** | standalone binary or official Docker image (Go module source) |
| **Dependencies** | none at runtime (single binary); built from source with Go 1.25 (go.mod go 1.25.0) |
| **Minimum toolchain** | Go 1.25 to build v3.6.13 (go.mod); prebuilt binaries and images need no toolchain |
| **Platforms** | Go-supported OS/architectures; supported release architectures were not checked this session |
| **Thread safety** | not applicable (separate proxy process); dynamic configuration is swapped at runtime without restart |
| **Drop-in for the baseline** | partial — replaces nginx as a reverse proxy on the wire, but routing, TLS and middleware configuration must be rewritten in Traefik's own model |

## Gotchas

- Mislabelled rows: the suite's 'HTTPS/1.1' scenario is HTTP/2 because Vegeta's -http2 flag defaults to true (v12.13.0 attack.go) and only -insecure is passed, so both TLS rows measure the same HTTP/2 workload over a few multiplexed connections.
- Harness asymmetry (new, untested): the suite's nginx.conf sets keepalive_requests 10000, which nginx 1.28 also applies to HTTP/2 (ngx_http_v2.c sends GOAWAY once connection requests reach keepalive_requests). At 5,000 req/s over one multiplexed connection, nginx forces a reconnect about every 2 s (about 10 per 20 s run), each a full RSA-4096 handshake, since Vegeta's tls.Config has no ClientSessionCache and nginx has no ssl_session_cache. Traefik's keep-alive cap is opt-in (KeepAliveMaxRequests/KeepAliveMaxTime, middleware installed only when set), so its connection is never rotated. Plausible contributor to nginx's \~24 ms P99.
- Run-to-run noise exceeds the claimed gap: in the restricted run Caddy, which uses the same Go crypto/tls as Traefik, shows about 86 ms mean on the 'HTTPS/1.1' row and about 1 ms on the 'HTTPS/2' row, which are the same HTTP/2 workload (read from benchmark.png). A single run per scenario cannot separate a Traefik advantage from noise, and Caddy's result argues against a 'Go TLS is faster' explanation.
- Restricted-run asymmetry: nginx worker_processes auto counts the host's 24 CPUs under a 2-CPU CFS quota, while Traefik v3.6.13 (Go 1.25) sizes GOMAXPROCS to the quota; the backend nginx and the Vegeta container are unrestricted and share the host.

## Known shortcomings

- The harness 'HTTPS/1.1' row is actually HTTP/2 (vegeta -http2 defaults to true; the harness passes only -insecure); archived 0-star personal benchmark with prebuilt images, flags unknown on both sides, no CPU model (24 cores, 29.0 GB, Ubuntu 24.04.4), means only from a chart, no raw results, p99 approximate; no HTTP/1.1 win; the restricted run is uneven (nginx worker_processes auto starts 24 workers under a 2-CPU quota while Traefik's Go 1.25 gets a container-aware GOMAXPROCS); probable cause is harness and config (nginx one worker per HTTP/2 connection), not the language.
- Harness flaw (untested): the suite's nginx.conf keepalive_requests 10000 also caps HTTP/2 (ngx_http_v2.c sends GOAWAY), so nginx reconnects about every 2 s at 5k req/s, about 10 full RSA-4096 handshakes per run, with no Vegeta ClientSessionCache and no nginx ssl_session_cache, while Traefik's keep-alive cap is opt-in and never rotates. Run noise: the restricted Caddy (Go TLS) shows about 86 ms mean on the 'HTTPS/1.1' row against about 1 ms on 'HTTPS/2' for the same HTTP/2 workload, so one run cannot separate Traefik's edge from noise.

## Caveats and trade-offs

Benchmark repo (fabianwimberger/reverse-proxy-benchmark) is a third-party suite but a 0-star personal repo the owner archived on 2026-07-17; hardware lacks a CPU model and the proxies are prebuilt images with unknown build flags on both sides. Fixed-rate latency test at 5,000 req/s, not saturation throughput; all four proxies sustain the rate with 100% success, so differences are sub-millisecond except tails. Harness flaw: the 'HTTPS/1.1' scenario is actually HTTP/2 because vegeta's -http2 flag defaults to true (attack.go v12.13.0) and the harness only passes -insecure, so both TLS rows measure HTTP/2 over a few multiplexed connections; Nginx serves each connection from a single worker process, which plausibly explains its tail latency more than any language effect. The P99 values exist only as approximate README prose; the committed chart shows means only and raw vegeta JSON is not committed. Restricted-run asymmetry: nginx worker_processes auto counts the host's 24 CPUs under a 2-CPU CFS quota, whereas Traefik v3.6.13 (go.mod go 1.25.0) gets Go 1.25's container-aware GOMAXPROCS (likely cause of Nginx's \~32 ms restricted means; not tested). No HTTP/1.1 win: the author credits Nginx with plaintext throughput and calls HTTP/1.1 'extremely tight'. Not a same-algorithm comparison: different proxy designs and TLS stacks (Go crypto/tls vs OpenSSL). [retier] The suite's nginx.conf keepalive_requests 10000 also caps HTTP/2 (ngx_http_v2.c sends GOAWAY), so nginx reconnects about every 2 s at 5k req/s with about 10 full RSA-4096 handshakes per run, no Vegeta ClientSessionCache and no nginx ssl_session_cache, while Traefik's keep-alive cap is opt-in and never rotates (untested). The restricted Caddy shows about 86 ms mean on the 'HTTPS/1.1' row against about 1 ms on 'HTTPS/2' for the same HTTP/2 workload, so one run cannot separate Traefik's edge from noise.

The benchmark records latency percentiles and success rate only; CPU and memory use are not reported. The author states that Nginx wins plaintext throughput and recommends running the suite on one's own hardware.

## Maintenance

Traefik is actively maintained (last commit 2026-10-08, 65.2k stars, MIT) and widely deployed, but the speed claim rests on a single archived third-party run with a nginx-only connection-rotation handicap, so treat it as tier C evidence of TLS tail latency, not a general win over nginx.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** Third-party harness is public (Makefile, docker-compose.yml, configs/\*) with pinned prebuilt images, but it is a 0-star archived personal repo, not a well-known suite; the chart footer gives only '24 cores, 29.0 GB RAM, Ubuntu 24.04.4 LTS' with no CPU model, no compiler flags exist for either side, the P99 figures appear only as approximate README prose (the chart shows means only, raw results are not committed), and the 'HTTPS/1.1' scenario actually negotiates HTTP/2. Tier C stands.
- **Retiered** C to D: Enricher: the suite's nginx keepalive_requests cap forces HTTP/2 reconnects with full RSA-4096 handshakes (no session cache on either side) while Traefik never rotates, and the same workload shows 86x run-to-run noise on another proxy, so one run cannot establish Traefik's edge; crippled baseline with no valid measurement: C to D.
- **Verifier notes:** Numbers in the record match the README text; added that the 'HTTPS/1.1' scenario is really HTTP/2 (vegeta -http2 default true, verified in tsenart/vegeta v12.13.0 attack.go and lib/attack.go), that -connections=64 is only an idle-pool cap, and that the P99 figures are prose-only with no committed raw results. Record shortcomings: TLS rows mislabelled (both HTTP/2), single-host Docker run without CPU model, prebuilt images with unknown flags, restricted-run GOMAXPROCS/worker_processes asymmetry, no HTTP/1.1 win; not a language-level result (same_algorithm false). Traefik metadata checked: MIT, 65.2k stars, not a fork, last commit 2026-10-08 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-96 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/fabianwimberger/reverse-proxy-benchmark>
  - <https://github.com/fabianwimberger/reverse-proxy-benchmark/commits/main/README.md>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/Makefile>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/docker-compose.restricted.yml>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/nginx/default.conf>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/haproxy/haproxy.cfg>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/traefik/traefik.yml>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/traefik/dynamic.yml>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/caddy/Caddyfile>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/backend/nginx.conf>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/analyze_results.py>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/scripts/summarize.py>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/assets/local-results/benchmark.png>
  - <https://raw.githubusercontent.com/tsenart/vegeta/v12.13.0/attack.go>
  - <https://raw.githubusercontent.com/tsenart/vegeta/v12.13.0/lib/attack.go>
  - <https://raw.githubusercontent.com/traefik/traefik/v3.6.13/go.mod>
  - <https://github.com/traefik/traefik>
  - <https://github.com/traefik/traefik/commits>
- **Sources the enricher read:**
  - <https://github.com/traefik/traefik>
  - <https://github.com/traefik/traefik/issues?q=is%3Aissue+label%3Akind%2Fbug%2Fperformance+OR+performance+latency+sort%3Acomments-desc>
  - <https://github.com/traefik/traefik/issues/6954>
  - <https://raw.githubusercontent.com/traefik/traefik/v3.6.13/go.mod>
  - <https://raw.githubusercontent.com/traefik/traefik/v3.6.13/pkg/proxy/httputil/proxy.go>
  - <https://raw.githubusercontent.com/traefik/traefik/v3.6.13/pkg/proxy/httputil/bufferpool.go>
  - <https://raw.githubusercontent.com/traefik/traefik/v3.6.13/pkg/proxy/fast/proxy.go>
  - <https://raw.githubusercontent.com/traefik/traefik/v3.6.13/pkg/server/server_entrypoint_tcp.go>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/Makefile>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/docker-compose.yml>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/docker-compose.restricted.yml>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/nginx/default.conf>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/haproxy/haproxy.cfg>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/traefik/traefik.yml>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/traefik/dynamic.yml>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/caddy/Caddyfile>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/configs/backend/nginx.conf>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/analyze_results.py>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/scripts/summarize.py>
  - <https://raw.githubusercontent.com/fabianwimberger/reverse-proxy-benchmark/HEAD/assets/local-results/benchmark.png>
  - <https://raw.githubusercontent.com/tsenart/vegeta/v12.13.0/attack.go>
  - <https://raw.githubusercontent.com/tsenart/vegeta/v12.13.0/lib/attack.go>
  - <https://raw.githubusercontent.com/nginx/nginx/release-1.28.0/src/http/v2/ngx_http_v2.c>
  - WebSearch: traefik experimental fastProxy (doc.traefik.io fastproxy pages, snippets only)
  - WebSearch: Traefik vs Nginx vs HAProxy benchmark (snippets of dev-website.teramont.net/blog/nginx-vs-traefik-comparison and haproxy.com ingress benchmark news, not opened)
  - https://community.traefik.io/t/traefik-performance-lags-behind-nginx-and-caddy/28919 (ENOTFOUND, not read)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/traefik/traefik`) · [data/wave14/enrich/raw/github_com_traefik_traefik.json](../../../data/wave14/enrich/raw/github_com_traefik_traefik.json) (enrichment confidence 0.3)

</details>
