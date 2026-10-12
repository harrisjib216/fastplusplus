# Orion Proxy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust L4/L7 proxy configured through Envoy's xDS and bootstrap protobufs; first-party wrk charts show 2.3-6x Envoy's HTTP req/s.

| | |
|---|---|
| **Beats** | Envoy Proxy (C++) |
| **Claimed result** | README: '2x-4x better throughput and latency than Envoy Proxy'. HTTP chart (docs/pics/performance/baseline/wrk-reqsec.png), requests/s orion-mr-st vs envoy: 2048 connections, 1 core 46,593 vs 12,819 (3.63x, derived from page data), 48 cores 1,881,522 vs 310,231 (6.06x, derived); 16384 connections, 1 core 38,573 vs 17,059 (2.26x, derived), 48 cores 1,410,611 vs 514,254 (2.74x, derived). HTTPS chart (tls/wrk-reqsec.png): 2048 connections, 1 core 30,398 vs 11,268 (2.7x, derived), 48 cores 1,478,634 vs 324,135 (4.56x, derived); 16384 connections, 1 core 26,354 vs 14,096 (1.87x, derived), 48 cores 738,429 vs 483,069 (1.53x, derived). The latency chart (baseline/wrk-latency.png, microseconds, percentile not stated, lower is better) does not support a 2x-4x latency win across the board: with 2048 connections Orion's latency is higher than Envoy's at 2, 8, 16, 24, 32 and 48 cores (e.g. 48 cores 251,325 vs 201,636; 16 cores 193,495 vs 85,659) and lower only at 1 core (280,347 vs 323,953), about equal at 4; with 16384 connections Orion is worse at 1, 2 and 4 cores (1,879,395 vs 1,789,400; 1,944,476 vs 1,769,852; 971,338 vs 633,244) and better at 8-48 cores (e.g. 270,335 vs 1,815,855 at 16 cores). |
| **Workload** | HTTP reverse proxy to an nginx upstream, wrk at 2048 and 16384 connections, 1 to 48 cores assigned to the proxy. |
| **Metric** | throughput |
| **Hardware** | Two-host testbed: DUT proxy host and tester host with wrk on NUMA 0 and nginx upstream on NUMA 1, 25 Gbps Mellanox and Intel NICs, IRQ affinity tuned (CPU model not stated) |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README credits Rust's zero-cost abstractions and memory safety guarantees (no profiling or mechanism analysis is given). |
| **Adoption** | 39 stars |
| **Last commit** | 2026-03-02 |
| **Links** | [repository](https://github.com/kmesh-net/orion) · [benchmark](https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/performance/performance.md) |

## Verdict

On a two-host testbed (wrk on NUMA 0 and an nginx 12-byte in-memory upstream on NUMA 1 of the tester, 25 Gbps NICs, tuned IRQ affinity, CPU model, Envoy version and both builds unstated), Orion in its multi-runtime single-thread mode proxied 46,593 vs Envoy's 12,819 HTTP req/s on 1 core (3.6x) and 1,881,522 vs 310,231 on 48 cores (6.1x) with 2048 connections, 2.3-2.7x with 16384 connections, and 1.5-4.6x over HTTPS. The README's latency half of '2x-4x' is not supported by its own tail-latency charts, which are mixed.

## Use it when

- You run Envoy as an L7 gateway or Istio/Kmesh waypoint with a common feature subset (routing, header matching, retries, TLS termination, round-robin or least-request LB) and want to trial more req/s per core while keeping the xDS control plane.
- Kubernetes Gateway API ingress through the Kubvernor controller, where Orion passes the basic Gateway API and Inference Extension conformance suites.
- High connection counts (thousands of keep-alive HTTP/1.1 clients) on many-core Linux hosts where per-core pinned runtimes and SO_REUSEPORT sharding pay off.
- Plain L4 TCP proxying, where the published chart shows Orion at 0.9-2.3M req/s against an Envoy setup that never exceeded 408k.

## Skip it when

- Production traffic today: RELEASE-NOTES.md for 0.1.0 says the project 'is still very unstable and not ready for use in production environments', and the workspace version is only 0.2.0.
- Configs that rely on Envoy features Orion lacks: HTTP RBAC, set_filter_state, internal connections, connection draining across listener versions and Istio sidecar mode are open issues (#119, #126, #105, #102, #113); ext_proc FULL_DUPLEX_STREAMED has an open bug (#149).
- Latency-sensitive tuning based on the README's '2x-4x better latency': the project's own latency charts show Orion's tail latency higher than Envoy's at most core counts with 2048 HTTP connections and at 5 of 8 core counts with 16384 TLS connections.
- Non-Linux deployments: core pinning, SO_REUSEPORT sharding and original-destination recovery are Linux-oriented, and no other platform is documented.
- Teams that need Envoy's extension ecosystem (Lua, Wasm, the full HTTP filter catalogue); Orion targets 'the most common or popular use-cases' only.

## How it is fast

Thread-per-core, shared-nothing design: by default it starts one current-thread Tokio runtime per CPU, optionally pinned to cores by a per-runtime or NUMA-grouped affinity strategy (orion-proxy/src/core_affinity.rs), and each runtime binds its own SO_REUSEPORT listener so the kernel spreads accepts without cross-core handoff (orion-proxy/src/runtime.rs, orion-lib/src/listeners/listener.rs). The data path is hyper 1.x plus a vendored hyper-util fork, Bytes buffers and rustls on aws-lc-rs, built with fat LTO, codegen-units=1 and opt-level 3. The project gives no profile or mechanism analysis beyond 'Rust's zero-cost abstractions'; Envoy also runs one event loop per worker with per-worker listeners, so the measured gap is not explained by the thread model alone.

## Compared with alternatives

Pick Orion over Spire, monolake, routez or rproxy when you need to keep an Envoy xDS control plane (Istio, Kmesh, Gateway API); Spire has a fuller published table against Envoy 1.22.8 (2.38x) but no xDS compatibility. Pick linkerd2-proxy instead when you want a production-proven Rust sidecar and can adopt Linkerd's control plane.

## Integration

| | |
|---|---|
| **Form** | standalone binary (Cargo workspace; docker/Dockerfile builds a release image) |
| **Dependencies** | tokio, hyper 1.x with a vendored hyper-util 0.1.18 fork (patched via [patch.crates-io]), h2, rustls 0.23 with aws-lc-rs, tonic/prost for xDS, hickory-resolver, axum (admin), prometheus, opentelemetry; build needs protoc and the Envoy data-plane-api, xds, googleapis and protobuf git submodules |
| **Minimum toolchain** | Rust 1.86 (workspace rust-version); the Dockerfile builds with rust:1.91.1 |
| **Platforms** | Linux (x86-64 tested in the published benchmark); other platforms not documented |
| **Thread safety** | Not applicable as a library; the proxy runs N independent runtimes plus one services runtime (xDS client, admin, access logs) that pushes configuration changes to each runtime over channels. |
| **Drop-in for the baseline** | partial — accepts Envoy bootstrap and xDS protobufs and serves common HTTP/TCP routes, but implements only a subset of Envoy filters and listener features, and the CLI and runtime YAML differ from Envoy's. |

## Gotchas

- The latency charts plot a tail value, not a mean, and the percentile is not stated: by Little's law the mean at 48 cores with 2048 HTTP connections would be about 1.1 ms for Orion (1,881,522 req/s) and 6.6 ms for Envoy (310,231 req/s), but the chart shows 251,325 and 201,636 microseconds (derived from page data). Single noisy runs: Envoy's TLS latency at 16384 connections drops from 1,405,509 at 24 cores to 735,516 at 16.
- Harness flaw in the baseline: the TCP (L4) chart shows Envoy at 53 and 47 req/s on 1-2 cores and 0 req/s on 1-4 cores at 16384 connections (743 at 8 cores) while Orion does 90k-288k, which points to a broken or misconfigured Envoy L4 setup; no Envoy config, version or circuit-breaker settings are published, although Envoy's benchmarking FAQ says circuit breaking and some stats must be adjusted for a fair test.
- Upper core counts are testbed-bound: Orion's L4 rate plateaus at 2.30M, 2.29M and 2.20M req/s at 24, 32 and 48 cores, close to the upstream nginx's stated 2.6M req/s hard limit, and the methodology text (1-32 cores, 'Envoy, Ng-proxy, and Nginx') does not match the charts (1-48 cores, Orion and Envoy only).
- Each per-core listener socket is opened with SO_REUSEPORT and a hard-coded listen backlog of 128 (configure_and_start_tcp_listener); 'N cores' for Orion also excludes its separate services thread (num_service_threads defaults to 1). jemalloc is an opt-in Cargo feature (off by default), and which allocator and features the benchmarked build used is not stated.

## Known shortcomings

- Numbers only in chart PNGs with no harness, configs, CPU model or Envoy build in the repo; the latency chart contradicts the "2x-4x latency" claim (Orion latency higher at 2048 connections on 2 and 8-48 cores) and the Envoy L4 chart shows 0-53 req/s, so the Envoy setup looks broken.
- Baseline harness flawed: in the TCP chart Envoy does 53/47 req/s on 1-2 cores and 0 on 1-4 cores at 16,384 connections, with no Envoy configuration or circuit-breaker settings published; the latency charts plot an unstated tail value, not a mean (Little's law gives about 1.1 ms against the chart's 251,325 us at 48 cores) and do not back the README's latency claim; the top core counts are capped by the testbed (L4 plateaus at 2.3M near nginx's 2.6M limit). RELEASE-NOTES says not ready for production.

## Caveats and trade-offs

First-party; the numbers exist only as chart images, and the repo carries no benchmark scripts, wrk invocation, Envoy or Orion configuration (docs/performance holds only performance.md; tools/ has no bench files). The methodology lists 'Envoy, Ng-proxy, and Nginx' as compared proxies and scaling at 1-32 cores, but the charts show only Orion (series 'orion-mr-st', a runtime mode the page does not explain) and Envoy, at 1-48 cores. Envoy version, build and config, Orion build flags and the CPU model are not stated, so tier C. The README's 2x-4x is lower than the 6x seen in the 2048-connection HTTP chart at 48 cores and does not hold for latency: the latency chart is mixed (with 2048 connections Orion's latency is higher than Envoy's at 2 and 8-48 cores; with 16384 connections it is worse at 1-4 cores and better at 8-48 cores). The TCP (L4) chart shows Envoy at 53 and 47 req/s on 1-2 cores with 2048 connections and 0 req/s on 1-4 cores with 16384 connections, which points to a broken or saturated Envoy setup in this testbed and casts doubt on how Envoy was configured for the other charts. [retier] In the TCP chart Envoy does 53/47 req/s on 1-2 cores and 0 on 1-4 cores at 16,384 connections, with no Envoy configuration or circuit-breaker settings published; the latency charts plot an unstated tail value, not a mean (Little's law gives about 1.1 ms against the chart's 251,325 us at 48 cores) and do not back the README's latency claim; the top core counts are capped by the testbed (L4 plateaus at 2.3M near nginx's 2.6M limit). RELEASE-NOTES says not ready for production.

Envoy xDS-compatible Rust proxy aiming at a drop-in replacement for common use cases only; not the full Envoy filter set.

## Maintenance

Apache-2.0, 39 stars, version 0.2.0 with 359 commits; last commit 2026-03-02 (Gateway API conformance and host-matching fixes), recent commits mostly by one Huawei developer; self-described as not production-ready, and backed only by first-party chart images with no published harness or configs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party chart images (docs/pics/performance/{baseline,tls,tcp}/wrk-\*.png) compare Orion with Envoy; the repo holds no benchmark scripts, wrk commands, Envoy or Orion configs, and no CPU model, Envoy version or build flags are given, so it falls short of A.
- **Verifier notes:** Chart labels match the record's HTTP numbers exactly; added TLS rows and the latency and L4 observations. Shortcomings to record: no published harness or configs, no CPU model or Envoy build, latency half of the 2x-4x claim contradicted at 2048 connections (Orion latency higher at most core counts), Envoy L4 rows near zero suggest a misconfigured baseline. Metadata checked: Apache-2.0, 39 stars, 22 forks, not a fork, last commit 2026-03-02 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-20 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/performance/performance.md>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/README.md>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/baseline/wrk-reqsec.png>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/baseline/wrk-latency.png>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/tls/wrk-reqsec.png>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/tcp/wrk-reqsec.png>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/testbed_conf.png>
  - <https://github.com/kmesh-net/orion>
  - <https://github.com/kmesh-net/orion/commits>
  - <https://github.com/kmesh-net/orion/tree/main/tools>
  - <https://github.com/kmesh-net/orion/tree/main/docs/performance>
- **Sources the enricher read:**
  - <https://github.com/kmesh-net/orion>
  - <https://github.com/kmesh-net/orion/commits>
  - <https://github.com/kmesh-net/orion/issues>
  - <https://github.com/kmesh-net/orion/tree/main/orion-proxy/src>
  - <https://github.com/kmesh-net/orion/tree/main/orion-lib/src/listeners>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/README.md>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/performance/performance.md>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/RELEASE-NOTES.md>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/NOTES.txt>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/Makefile>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/config.yaml>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/envoy-bootstrap.yaml>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docker/README.md>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/hyper-util-fork/README.md>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/hyper-util-fork/Cargo.toml>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/orion-proxy/Cargo.toml>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/orion-proxy/conf/orion-runtime.yaml>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/orion-proxy/src/runtime.rs>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/orion-proxy/src/proxy.rs>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/orion-proxy/src/core_affinity.rs>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/orion-proxy/src/main.rs>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/orion-lib/Cargo.toml>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/orion-lib/src/listeners/listener.rs>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/orion-configuration/src/config/runtime.rs>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/baseline/wrk-reqsec.png>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/baseline/wrk-latency.png>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/tls/wrk-reqsec.png>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/tls/wrk-latency.png>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/tcp/wrk-reqsec.png>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/tcp/wrk-latency.png>
  - <https://raw.githubusercontent.com/kmesh-net/orion/HEAD/docs/pics/performance/testbed_conf.png>
  - <https://github.com/kmesh-net/community/issues/14>
  - <https://github.com/zoxy-io/benchmark>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/kmesh-net/orion`) · [data/wave14/enrich/raw/github_com_kmesh_net_orion.json](../../../data/wave14/enrich/raw/github_com_kmesh_net_orion.json) (enrichment confidence 0.55)

</details>
