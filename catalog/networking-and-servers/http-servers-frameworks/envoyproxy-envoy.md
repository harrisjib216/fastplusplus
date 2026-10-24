# Envoy Proxy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> CNCF C++ L7 proxy for service meshes and edges; in third-party HTTP/1 runs it is slower than NGINX and HAProxy.

| | |
|---|---|
| **Beats** | NGINX 1.22.1 and HAProxy 2.7.3 as L7 reverse proxies |
| **Claimed result** | Not faster. Proxy-Benchmarks (hey, 100,000 requests, 250 connections): Envoy 25,852 req/s vs NGINX 33,506 and HAProxy 39,437 (Envoy 0.77x of NGINX and 0.66x of HAProxy, derived from page data); mean latency 9.5 ms vs 7.2 ms (NGINX) and 6.1 ms (HAProxy); p50 8.9 ms vs 5.7 and 4.1 ms. Envoy is lower only at p90 to p99: p90 12.6 ms vs 14.7 (NGINX) and 13.8 (HAProxy), p95 13.9 vs 18.7 and 18.5, p99 19.5 ms vs 27.5 and 30.6 (29% and 36% lower, derived from page data), but these are measured at 23-34% lower throughput in a closed loop, and the extreme tail is worse: slowest request 111.0 ms vs 67.1 ms (NGINX) and 91.6 ms (HAProxy), with 250 Envoy requests above 56 ms against 5 NGINX requests above 54 ms and 161 HAProxy requests above 55 ms (derived from the page's histograms). Envoy issue 5536 (wrk, 100 connections, 10 threads, 60 s, 4 workers each, nginx backend): Envoy 39,748.81 req/s, 2.73 ms average, 7.10 ms p99, 413.43 ms max vs HAProxy 88,446.34 req/s, 1.14 ms average, 2.20 ms p99, 31.04 ms max. |
| **Workload** | Third-party Proxy-Benchmarks suite: hey -n 100000 -c 250 GET from a client VM through each proxy to a jmalloc/echo-server backend VM; all five proxies run as Docker containers on one proxy VM (ports 8000-8004 via -p port mapping) and are tested one after another in a single run_tests.sh pass, one run per proxy, on AWS m5.xlarge instances (Envoy 1.22.8 default concurrency, NGINX worker_processes 3 with upstream keepalive 32, HAProxy 2.7.3 config with no tuning). Second source: Envoy issue 5536, wrk -c100 -t10 -d60s against Envoy (concurrency 4) and HAProxy (nbproc 4) in Docker with host networking in front of an nginx backend. |
| **Metric** | latency |
| **Hardware** | AWS m5.xlarge for client, backend and proxy VMs (variables.tf default, us-east-2); CPU model not stated. |
| **Compiler and flags** | Not applicable: prebuilt container images (Envoy 1.22.8, NGINX 1.22.1, HAProxy 2.7.3, Caddy 2.6.4, Traefik 2.9.8) deployed with Terraform and Docker; no build flags. |
| **Adoption** | 29.1k stars; used as a sidecar proxy in service meshes (per the book lead) |
| **Last commit** | 2026-10-24 |
| **Links** | [repository](https://github.com/envoyproxy/envoy) · [benchmark](https://github.com/NickMRamirez/Proxy-Benchmarks) |

## Verdict

No speedup: in NickMRamirez/Proxy-Benchmarks (hey, 100,000 GETs over 250 connections, prebuilt Docker images on AWS m5.xlarge VMs, CPU model not stated, one run) Envoy 1.22.8 served 25,852 req/s against 33,506 for NGINX 1.22.1 and 39,437 for HAProxy 2.7.3, beating them only on p90-p99 latency at that lower throughput while its slowest request was worse. In issue 5536 (wrk, 100 connections, 4 workers each, Docker host networking, hardware not stated) Envoy reached 39,749 req/s against HAProxy's 88,446.

## Use it when

- Service-mesh sidecars and gateways where routes, clusters and certificates change at runtime through xDS from a control plane (Istio, Envoy Gateway) without reloads.
- You need per-request telemetry (stats, tracing via OpenTelemetry, Zipkin or Datadog, access logs), circuit breaking and per-worker connection pooling built into the proxy rather than added by modules.
- HTTP/2, gRPC and HTTP/3 traffic where one proxy must speak all three on both sides.
- Extending the proxy with C++ filters, Lua or Proxy-Wasm, with the same filter model at the edge and in the mesh.

## Skip it when

- Raw HTTP/1 reverse-proxy throughput per core is the goal: third-party runs put Envoy at 0.77x of NGINX and 0.66x of HAProxy (Proxy-Benchmarks) and 0.45x of HAProxy (issue 5536), and a direct_response test reached 123,949 req/s against 446,352 for an nginx return (issue 17266, Envoy 1.18.3 with request ids and stats turned off).
- Very high core counts with many HTTP/1 upstream hosts: each worker has its own upstream pool, so connections scale with workers times backends; issue 38554 hit about 64k upstream sockets and 2-5x NGINX's CPU on a 128-core host until workers were cut to 32 (then about 20-30% behind NGINX).
- Small teams wanting a hand-edited config and simple builds: the YAML/protobuf config is verbose, and building from source needs Bazel, Clang 18+ (or GCC 13+) and about 2 GB RAM per build core.
- Windows hosts: the build docs state Windows support has ended; ppc64le is best-effort and outside the security policy.
- You want a static-file web server or an in-process application host: Envoy's role is proxying, with direct_response limited to fixed replies.

## How it is fast

One process with a main thread for xDS, stats flushing and admin, plus N worker threads (default one per hardware thread) that each run a libevent-based Dispatcher; a connection stays on one worker for life, so the hot path takes no locks. Shared state such as cluster membership and stats reaches workers through thread-local slots updated by posted closures, and each worker keeps its own upstream connection pools. HTTP/1 is parsed by QUICHE's Balsa parser (codec_impl.cc no longer constructs the old http-parser), HTTP/2 by nghttp2 or oghttp2, and an io_uring I/O path exists but is still being worked toward stable support. None of this makes it faster than the baselines in the measurements found; its design target is dynamic configuration and observability at acceptable per-request cost.

## Compared with alternatives

Pick Envoy over Pingora when you want a ready-made proxy driven by xDS or a mesh control plane rather than writing proxy logic in Rust, and over nghttpx or Pipy when you need its filter ecosystem, telemetry and gRPC/HTTP/3 support; for maximum plain HTTP/1 proxying speed per core NGINX, HAProxy or H2O are the better choice.

## Integration

| | |
|---|---|
| **Form** | standalone binary (statically linked; official Docker images), built from source with Bazel; extensions are compiled in |
| **Dependencies** | Built in through Bazel modules: BoringSSL, libevent, nghttp2, QUICHE (Balsa HTTP/1 parser, HTTP/3), abseil-cpp, protobuf, gRPC, c-ares, yaml-cpp, re2, zlib-ng, brotli, zstd, tcmalloc (gperftools fallback), plus optional extensions (LuaJIT, Proxy-Wasm, Hyperscan/Vectorscan, Kafka and others). |
| **Minimum toolchain** | Clang &gt;= 18 (CI uses Clang 22) or GCC &gt;= 13; C++20; Bazel 9.3.1 per .bazelversion |
| **Platforms** | Linux x86-64 and aarch64 (primary); macOS builds with tcmalloc disabled; s390x and ppc64le community CI builds, ppc64le best-effort and not covered by the security policy; Windows support ended |
| **Thread safety** | Multi-threaded daemon: main thread plus --concurrency worker threads; each connection is pinned to one worker, and filter code runs single-threaded on its worker's Dispatcher, with cross-thread data through thread-local slots |
| **Drop-in for the baseline** | partial — fills the reverse-proxy and load-balancer role of NGINX/HAProxy, but needs a new Envoy YAML or xDS config; no nginx.conf/haproxy.cfg compatibility, modules or static file serving |

## Gotchas

- Defaults are not benchmark-neutral: Envoy's own FAQ says to disable circuit breaking (defaults such as 1024 connections per cluster), generate_request_id and dynamic_stats, set --concurrency to match the other proxy, and measure below the latency knee with an open-loop generator. The Proxy-Benchmarks envoy.yaml leaves all of these at defaults while its nginx.conf adds upstream keepalive 32, so its Envoy row is a default-config result.
- That suite's echo backend returns what it receives, and the Envoy row reports 253 B per request against 126 B for NGINX; headers Envoy adds by default (such as a request id) plausibly account for part of the difference, so the proxies did not move identical bytes (inference, not measured).
- HTTP/2 codec regression: from v1.34.0 the oghttp2 codec raised average latency about 15-25% in one sidecar test (issue 40070, still open); PR 42319 (merged Dec 2025) made nghttp2 the default again, and envoy.reloadable_features.http2_use_oghttp2=false is the workaround on affected releases.
- Security cadence is high: the advisory list runs to 14 pages, with a critical Brotli decompressor out-of-bounds write (Oct 23, 2026) and several 2026 crash and auth-bypass fixes in filters (OAuth2, ext_authz, RBAC); stable branches get fixes for 12 months, so plan regular upgrades.

## Known shortcomings

- Not faster than NGINX or HAProxy (verifier reject not-faster overridden to keep): Proxy-Benchmarks and issue 5536 show Envoy slower on throughput and on mean and median latency; its p90-p99 edge comes from a closed-loop hey run where it served 23-34% fewer req/s, and its slowest request (111.0 ms) is worse than NGINX (67.1 ms) and HAProxy (91.6 ms). Single pass, all 5 proxies co-resident in Docker on one 4-vCPU VM, differing configs and response sizes, no CPU model.
- Proxy-Benchmarks ran Envoy with default request-id, stats and circuit-breaker settings while NGINX got upstream keepalive

## Caveats and trade-offs

Envoy loses on throughput and on median and mean latency in both sources, and its only favourable numbers (lower p90 to p99 in Proxy-Benchmarks) come from a closed-loop hey run where each proxy is driven at a different request rate: Envoy served 23-34% fewer requests per second, so its tighter p90-p99 is not a like-for-like latency win, and its extreme tail is worse (slowest 111.0 ms vs 67.1 ms NGINX and 91.6 ms HAProxy; a separate cluster of 250 requests at 56-111 ms against 5 NGINX requests above 54 ms, derived from the histograms). The run is one 100,000-request pass lasting 2.5 to 3.9 s per proxy, no warm-up, no repetitions, hey client (coordinated omission possible), all five proxies co-resident as Docker containers on one 4-vCPU proxy VM behind bridge port mapping, proxies configured differently (NGINX worker_processes 3 with upstream keepalive 32; Envoy and HAProxy at default thread counts), and response sizes differ per proxy (253 B Envoy, 126 B NGINX, 140 B HAProxy per request). CPU model not stated (m5.xlarge only). The repo was last updated Aug 2023 (313 stars) and tests Envoy 1.22.8, an old release. The repo owner's GitHub account also hosts HAProxy practice and syntax projects, and a WebSearch snippet lists a Nick Ramirez as HAProxy Technologies Director of Product Marketing on haproxy.com/authors; that this is the same person is not confirmed, but the suite may not be independent of the HAProxy baseline. Issue 5536 is from Jan 2019, hardware not stated, labelled question and closed by the stale bot in Jan 2020; a commenter said the HAProxy config was not optimal, another profiled Envoy and attributed part of the gap to its CPU-intensive HTTP/1 parser, and the reporter noted the nginx backend reached only 60% CPU in the Envoy run. A 2020 HAProxy Technologies Kubernetes ingress benchmark and other write-ups seen in search snippets could not be opened, so they are not used. The Envoy README itself carries no comparison with NGINX or HAProxy. [retier] Enricher: the Proxy-Benchmarks envoy.yaml ignores Envoy's own benchmarking FAQ (generate_request_id, dynamic_stats and circuit breakers left at defaults) while NGINX gets upstream keepalive 32, so the Envoy row is a default-config result; the echo backend returns what it receives, so Envoy's added request headers likely inflate its 253 B body (inference, not measured); issue 5536's HAProxy ran with http-reuse aggressive. More independent sources agree Envoy is slower: issue 17266 (direct_response 123,949 req/s vs nginx return 446,352, Envoy 1.18.3 with request ids and stats off) and issue 38554 (2-5x the NGINX CPU on 128 cores, about 20-30% behind after cutting workers to 32). Issue 5536's 'CPU-intensive parser' remark is stale: codec_impl.cc now builds only the QUICHE Balsa parser. oghttp2 had a latency regression (issue 40070); nghttp2 is the default again via PR 42319.

Broad feature set (filter chains, dynamic configuration, observability) gives up raw proxy speed in these runs; a contributor in issue 5536 attributes part of the gap to a relatively CPU-intensive HTTP/1 parser. Bazel build.

## Maintenance

Very active CNCF project (29.1k stars, v1.40.1 released Oct 23, 2026, main at 1.41.0-dev) under Apache-2.0, with quarterly releases and 12 months of stable-branch fixes; usable as a prebuilt binary or image, but not a library you vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification B, tier now B.
- **Tier reason:** Independent third-party harness is public (NickMRamirez/Proxy-Benchmarks: main.tf, variables.tf, client/run_tests.sh, nginx/nginx.conf, envoy/envoy.yaml, haproxy/haproxy.cfg, \*_setup.sh with pinned images envoyproxy/envoy:v1.22.8, nginx:1.22.1, haproxytech/haproxy-ubuntu:2.7.3) but names only AWS m5.xlarge, no CPU model, and is a single run, so not A; issue 5536 is an independent user report without hardware. Both measurements show Envoy slower than NGINX and HAProxy on throughput and mean/median latency.
- **Verifier notes:** Numbers on both pages match the record exactly, but Envoy is slower than both baselines on throughput and median/mean latency; the p90-p99 edge is at lower throughput in a closed loop and the max/extreme tail is worse, so not-faster. If kept per house rules, keep tier B with the not-faster shortcoming and the possible HAProxy affiliation of the suite author.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-84 (wave 5 book seed pass, 2026-10-24); enrichment (wave 5 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/NickMRamirez/Proxy-Benchmarks>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/variables.tf>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/main.tf>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/client/run_tests.sh>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/envoy/envoy.yaml>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/haproxy/haproxy.cfg>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/webserver/docker-compose.yml>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/envoy/envoy_setup.sh>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/nginx/nginx_setup.sh>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/haproxy/haproxy_setup.sh>
  - <https://github.com/NickMRamirez/Proxy-Benchmarks/commits>
  - <https://github.com/NickMRamirez>
  - <https://github.com/envoyproxy/envoy/issues/5536>
  - <https://github.com/envoyproxy/envoy>
  - <https://github.com/envoyproxy/envoy/commits/main>
- **Sources the enricher read:**
  - <https://github.com/envoyproxy/envoy>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/README.md>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/VERSION.txt>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/.bazelversion>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/.bazelrc>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/MODULE.bazel>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/RELEASES.md>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/bazel/README.md>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/docs/root/start/building.rst>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/docs/root/intro/arch_overview/intro/threading_model.rst>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/docs/root/intro/arch_overview/upstream/circuit_breaking.rst>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/docs/root/faq/performance/how_fast_is_envoy.rst>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/docs/root/faq/performance/how_to_benchmark_envoy.rst>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/source/common/http/http1/BUILD>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/source/common/http/http1/codec_impl.cc>
  - <https://raw.githubusercontent.com/envoyproxy/envoy/HEAD/source/common/runtime/runtime_features.cc>
  - <https://github.com/envoyproxy/envoy/releases>
  - <https://github.com/envoyproxy/envoy/security/advisories>
  - <https://github.com/envoyproxy/envoy/issues/5536>
  - <https://github.com/envoyproxy/envoy/issues/17266>
  - <https://github.com/envoyproxy/envoy/issues/38554>
  - <https://github.com/envoyproxy/envoy/issues/40070>
  - <https://github.com/envoyproxy/envoy/issues/48467>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/main.tf>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/client/run_tests.sh>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/envoy/envoy.yaml>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/NickMRamirez/Proxy-Benchmarks/HEAD/haproxy/haproxy.cfg>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/envoyproxy/envoy`) · [data/wave5/enrich/raw/github_com_envoyproxy_envoy.json](../../../data/wave5/enrich/raw/github_com_envoyproxy_envoy.json) (enrichment confidence 0.8)

</details>
