# linkerd2-proxy (Rust) vs Envoy as service-mesh sidecars

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust sidecar micro-proxy of the Linkerd mesh; vendor benchmarks show 6-9x less per-proxy memory than Istio's Envoy.

| | |
|---|---|
| **Beats** | Envoy (C++), as the Istio sidecar proxy |
| **Claimed result** | Buoyant posts on linkerd.io (source markdown in linkerd/website): (1) 'Why Linkerd doesn't use Envoy' (2020-12-03), internal benchmark on Kinvolk's harness at 4,000 RPS: Linkerd2-proxy 14-15 MB vs Istio's Envoy 135-175 MB ('ten times the size'), CPU 15 ms per instance vs 22-156 ms ('from 50% more to 10x more'), called 'not an entirely fair comparison'. (2) 'Benchmarking Linkerd and Istio' (2021-05-27, Linkerd 2.10.2 vs Istio 1.10.0 minimal, 2,000 RPS): max data-plane proxy memory 17.8 MB vs 154.6 MB (8.7x, derived from page data), max proxy CPU time 10 ms vs 88 ms; added latency 9 ms vs 15 ms at the median and 47 ms vs \~253 ms at the max (Istio 438% more at the max, derived from page data). The Buoyant press release's '36% more median latency' is snippet only and does not match the post's data (67% more, derived from page data). (3) 2021 Redux (2021-11-29, Linkerd 2.11.1 vs Istio 1.12.0, 2,000 RPS): 26.3 MB vs 156.2 MB memory (5.9x, derived from page data), 36 ms vs 67 ms CPU (1.86x), added latency 6 ms vs 17 ms median and 42 ms vs \~350 ms max. (4) The 2019 Kinvolk study (Linkerd 2.3-edge vs Istio 1.1.6, 500 and 600 RPS) as summarised by Buoyant: 5.7 MB vs 47 MB average per proxy, but data-plane CPU comparable and Linkerd's 15% higher at 600 RPS. |
| **Workload** | Kinvolk service-mesh-benchmark harness (wrk2 load against emojivoto-style microservices, mTLS on, metrics on, no retries or tracing) at 20, 200 and 2,000 RPS, 10-minute runs, 5 kept runs per level after discarding outliers, reporting the maximum memory and CPU time of any single data-plane proxy plus client-side latency percentiles; the 2020 figures come from an internal run at 4,000 RPS. |
| **Metric** | memory |
| **Hardware** | 2021 runs: Equinix Metal dfw2, 6 worker nodes plus one load-generator node of type s3.xlarge.x86 (Intel Xeon 4214, 24 physical cores at 2.2 GHz, 192 GB RAM), Kubernetes v1.19 (May) or v1.21.4 (Nov) on Lokomotive; hardware of the 2020 4,000 RPS run not stated. |
| **Compiler and flags** | Release binaries: Linkerd 2.10.2 default install vs Istio 1.10.0 minimal profile (May 2021), Linkerd 2.11.1 vs Istio 1.12.0 (Nov 2021); build flags not stated for either proxy. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Purpose-built minimal sidecar proxy in Rust versus the general-purpose Envoy (design scope, per the vendor); the language effect is not isolated. |
| **Adoption** | about 2.1k stars; data plane of the Linkerd service mesh |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/linkerd/linkerd2-proxy) · [benchmark](https://github.com/linkerd/website/blob/main/linkerd.io/content/blog/2021/0527-linkerd-vs-istio-benchmarks/index.md) |

## Verdict

Buoyant ran Kinvolk's open harness (wrk2 against emojivoto, mTLS on) on Equinix Metal Xeon 4214 nodes. At 2,000 RPS the largest Linkerd 2.10.2 proxy peaked at 17.8 MB and 10 ms of CPU time against 154.6 MB and 88 ms for Istio 1.10.0's Envoy (May 2021); in Nov 2021, Linkerd 2.11.1 against Istio 1.12.0, it was 26.3 MB and 36 ms against 156.2 MB and 67 ms, with lower added client-side latency. These compare two meshes in vendor-chosen configurations, not a Rust proxy against a C++ proxy.

## Use it when

- Choosing a sidecar service mesh for Kubernetes where per-pod proxy memory matters (many small pods): in the vendor runs at 2,000 RPS the largest Linkerd proxy peaked at 17.8-26.3 MB against 154.6-156.2 MB for Istio's Envoy.
- You want mTLS, golden metrics and latency-aware load balancing between pods with no proxy configuration to write or maintain.
- A memory-safe data plane is a requirement: the binary crate is #![forbid(unsafe_code)], the proxy is fuzzed, and it had a third-party fuzzing audit (Ada Logics, 2021).
- Meshed traffic that is sensitive to tail latency at moderate load: the vendor runs report 42-47 ms of added max latency against about 253-350 ms for Istio at 2,000 RPS, measured at the client.

## Skip it when

- Anything outside Linkerd: it needs Linkerd's Destination, identity and policy services and has no standalone configuration. Use Envoy, nginx or a sibling proxy for ingress, edge or gateway roles.
- You need Envoy's breadth (Wasm or Lua filters, extensive header and route manipulation, rate limiting, the xDS ecosystem) or must stay on Istio.
- You need supported stable builds without a subscription: since February 2024 the open-source project ships only edge releases, which may break at any point. Stable builds come from Buoyant Enterprise for Linkerd, which is free only for non-production use or companies under 50 employees (WebSearch snippet only).
- Long-lived HTTP/1.1 keep-alive traffic where slow memory growth would hurt: linkerd2 issue #11012 ('Proxy memory leak over HTTP 1') has been open and pinned since June 2023 with no root cause, and #14204 reported higher proxy memory after 2.18.
- Hosts other than Linux containers: the README says it 'may also work' on other Unix-like systems but targets Linux in Kubernetes.

## How it is fast

It does one job: a single pod's sidecar, about 30 KLOC against Envoy's 172 KLOC of C++ (vendor's 2020 count). It is built from Tokio (async I/O), hyper and h2 (HTTP) and tower middleware stacks. The runtime is single-threaded by default: linkerd/workers Workers::cores returns 1 unless LINKERD2_PROXY_CORES, _CORES_MAX or _CORES_MAX_RATIO is set. Other choices: jemalloc as the global allocator on x86-64 Linux glibc, LTO release builds, rustls on aws-lc-rs for mTLS, and power-of-two-choices balancing over EWMA latency (linkerd/pool/p2c, linkerd/ewma). The vendor credits the narrow design for the resource gap; no Rust-versus-C++ effect is isolated.

## Compared with alternatives

Orion Proxy and Spire are the catalogued Rust challengers to Envoy as standalone proxies, judged on throughput and latency; pick linkerd2-proxy only when Linkerd is your mesh, since it is that mesh's only data plane and its evidence is per-sidecar memory and client-side latency rather than requests per second. For an edge proxy or gateway, look at those siblings or the nginx challengers such as monolake.

## Integration

| | |
|---|---|
| **Form** | static binary shipped in Linkerd's proxy container image and injected as a Kubernetes sidecar; the workspace crates are not published (publish = false) |
| **Dependencies** | Linkerd control plane (Destination, identity, policy); crates tokio, hyper 1, h2, tower, tonic/prost, rustls on aws-lc-rs (optional FIPS feature), tikv-jemallocator on x86-64 Linux glibc |
| **Minimum toolchain** | Rust 1.90.0 pinned in rust-toolchain.toml (edition 2021); built with just and cargo or the provided dev container |
| **Platforms** | Linux containers on amd64 and arm64 (Dockerfile); other Unix-like systems such as macOS 'may also work' (README) |
| **Thread safety** | Not a library. The binary runs a current-thread Tokio runtime by default, or a multi-threaded one when the LINKERD2_PROXY_CORES variables raise the worker count (capped by the cgroup-aware CPU count). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry in the memory metric: the Kinvolk suite script (scripts/run_benchmarks.sh) deploys 60 emojivoto namespaces, and Istio ran its 'minimal' profile with no Sidecar resources. Istio's documented default (quoted in a Cisco post, WebSearch snippet only) programs every sidecar with configuration for every workload in the mesh, and Cisco measured about 40% less Envoy memory once namespaces were isolated. Part of the 6-9x per-proxy memory gap is therefore Istio's default config fan-out, not Rust against C++. The posts do not state how many app instances Buoyant deployed.
- Metric and reporting quirks: the figures are the maximum memory and maximum CPU time of any single proxy, not totals or cores, and the May 2021 post itself says cumulative cost would be more representative. Outlier runs were dropped by maximum latency; in Nov 2021, at 2,000 RPS, the worst run per mesh was 'manually discarded' because of deadline constraints. The Nov 2021 'Winner' lines at 20 and 200 RPS compare Linkerd's added median latency (8 ms) with Istio's total median (26 ms; its added median is 20 ms). The May 2021 summary says Linkerd delivered '75% of the additional median latency', but its own 9 ms vs 15 ms is 60%.
- The numbers are sensitive to configuration: moving to jemalloc in Linkerd 2.11.1 raised the largest proxy's memory from about 17 MB (2.11.0) to 26.3 MB in the same harness. The proxy core count, which drives both CPU time and memory, is not stated for either mesh. In current code the default is one worker thread, while the main.rs comment still says 'the number of available CPUs'.
- The CPU lead is not stable: 8.8x in May 2021 but 1.86x in Nov 2021, and in the 2019 Buoyant-commissioned Kinvolk study Linkerd's data plane used 15% more CPU than Istio's at 600 RPS (though Istio could not sustain that rate).

## Known shortcomings

- Vendor-run by Buoyant (May 2021 post, sources read in the linkerd/website repo); the language effect is not isolated; the gap shrank in the November 2021 run (1.86x CPU, 5.9x memory); the '36% median' press-release figure is snippet only and does not match the post data (67%).
- Harness flaw: the Kinvolk suite deploys 60 emojivoto namespaces and Istio minimal ran with no Sidecar scoping, so every Envoy carries configuration for the whole mesh (Cisco reports about 40% less memory with isolation, snippet only); part of the 6-9x memory gap is config fan-out, not C++. The November 2021 'Winner' lines compare Linkerd's added median 8 ms with Istio's total 26 ms (added 20); the May 2021 '75%' summary contradicts its own 9 vs 15 ms (60%); the worst run per mesh at 2,000 RPS was manually discarded. The current proxy defaults to 1 worker thread; open HTTP/1 leak #11012.

## Caveats and trade-offs

Vendor benchmarks: every post is by William Morgan of Buoyant, which sells Linkerd products, and the 2019 Kinvolk study was commissioned by Buoyant; the posts themselves say the 2020 numbers are internal and 'not an entirely fair comparison'. The comparison is Linkerd versus Istio, so the Envoy side carries Istio's sidecar configuration and feature set, and the language effect is not isolated from the design difference (a purpose-built micro-proxy versus general-purpose Envoy). The metrics are the maximum memory and CPU time of any single proxy, as the posts note, not cumulative cost. The gap narrows over time: CPU 8.8x in May 2021 but 1.86x in Nov 2021 after Linkerd 2.11.1 moved to jemalloc (proxy memory rose from 17.8 to 26.3 MB), and in the 2019 study Linkerd's data plane used more CPU than Istio's at 600 RPS. Raw data is in Google Sheets and the reproduction steps are on a linkerd2 wiki page; the harness repo kinvolk/service-mesh-benchmark (Apache-2.0, 142 stars) was archived on 2024-02-06 and lists no results. linkerd.io, buoyant.io, kinvolk.io and the CNCF mirror were not opened (blocked); the numbers were read in the post sources in the linkerd/website GitHub repo. The linkerd2-proxy README itself has no benchmark. [retier] The Kinvolk suite deploys 60 emojivoto namespaces and Istio minimal ran with no Sidecar scoping, so every Envoy carries configuration for the whole mesh (about 40% less memory with isolation per a Cisco snippet); part of the 6-9x memory gap is config fan-out, not C++. The November 2021 'Winner' lines compare Linkerd's added median 8 ms with Istio's total 26 ms; the May 2021 '75%' summary contradicts its own 9 vs 15 ms (60%); the worst run per mesh at 2,000 RPS was manually discarded. The current proxy defaults to 1 worker thread; open HTTP/1 leak #11012.

Purpose-built for Linkerd (mTLS, retries, load balancing for sidecar use), not a general reverse proxy; far smaller feature surface than Envoy.

## Maintenance

Actively developed (2.1k stars, 4,145 commits, last commit 2026-10-05) and Apache-2.0, but usable only as Linkerd's data plane; since February 2024 the open-source project ships edge releases only, and stable builds come through Buoyant Enterprise for Linkerd (WebSearch snippet only).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The numbers are now read on the blog posts' source files in the linkerd/website repo (the linkerd.io pages are blocked here): Buoyant-run benchmarks on the public Kinvolk harness with versions and the Xeon 4214 hardware stated, but written and run by the vendor (Buoyant's CEO) with no build flags, so vendor-blog tier C; the 2019 Kinvolk study was commissioned by Buoyant and its own report is unreachable.
- **Verifier notes:** Benchmark page found: the record's snippet numbers are confirmed in the source of 'Why Linkerd doesn't use Envoy' (4,000 RPS) and the May 2021 post (438% derived; 36% median figure is press-release only and inconsistent with the post). Metadata confirmed: Apache-2.0, 2.1k stars, last commit 2026-10-05, active. Shortcomings: vendor-run, Linkerd-vs-Istio not Rust-vs-C++ isolated, max-per-proxy metric, CPU gap shrank to 1.86x in the Nov 2021 redux.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-91 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/linkerd/linkerd2-proxy>
  - <https://github.com/linkerd/linkerd2-proxy/commits/main>
  - <https://github.com/kinvolk/service-mesh-benchmark>
  - <https://github.com/linkerd/website/blob/main/linkerd.io/content/blog/2021/0527-linkerd-vs-istio-benchmarks/index.md>
  - <https://raw.githubusercontent.com/linkerd/website/main/linkerd.io/content/blog/2021/0527-linkerd-vs-istio-benchmarks/index.md>
  - <https://raw.githubusercontent.com/linkerd/website/main/linkerd.io/content/blog/2021/1129-linkerd-vs-istio-benchmarks/index.md>
  - <https://raw.githubusercontent.com/linkerd/website/main/linkerd.io/content/blog/2019/0518-linkerd-benchmarks/index.md>
  - <https://raw.githubusercontent.com/linkerd/website/main/linkerd.io/content/blog/2020/1203-why-linkerd-doesnt-use-envoy/index.md>
- **Sources the enricher read:**
  - <https://github.com/linkerd/linkerd2-proxy>
  - <https://raw.githubusercontent.com/linkerd/linkerd2-proxy/main/README.md>
  - <https://raw.githubusercontent.com/linkerd/linkerd2-proxy/main/Cargo.toml>
  - <https://raw.githubusercontent.com/linkerd/linkerd2-proxy/main/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/linkerd/linkerd2-proxy/main/Dockerfile>
  - <https://raw.githubusercontent.com/linkerd/linkerd2-proxy/main/justfile>
  - <https://raw.githubusercontent.com/linkerd/linkerd2-proxy/main/linkerd2-proxy/Cargo.toml>
  - <https://raw.githubusercontent.com/linkerd/linkerd2-proxy/main/linkerd2-proxy/src/main.rs>
  - <https://raw.githubusercontent.com/linkerd/linkerd2-proxy/main/linkerd2-proxy/src/rt.rs>
  - <https://raw.githubusercontent.com/linkerd/linkerd2-proxy/main/linkerd/workers/src/lib.rs>
  - <https://raw.githubusercontent.com/linkerd/linkerd2-proxy/main/linkerd/rustls/Cargo.toml>
  - <https://raw.githubusercontent.com/linkerd/website/main/linkerd.io/content/blog/2021/0527-linkerd-vs-istio-benchmarks/index.md>
  - <https://raw.githubusercontent.com/linkerd/website/main/linkerd.io/content/blog/2021/1129-linkerd-vs-istio-benchmarks/index.md>
  - <https://raw.githubusercontent.com/linkerd/website/main/linkerd.io/content/blog/2020/1203-why-linkerd-doesnt-use-envoy/index.md>
  - <https://raw.githubusercontent.com/linkerd/website/main/linkerd.io/content/blog/2019/0518-linkerd-benchmarks/index.md>
  - <https://raw.githubusercontent.com/kinvolk/service-mesh-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/kinvolk/service-mesh-benchmark/master/scripts/run_benchmarks.sh>
  - <https://github.com/kinvolk/service-mesh-benchmark/tree/master/configs/emojivoto/templates>
  - <https://raw.githubusercontent.com/kinvolk/service-mesh-benchmark/master/configs/emojivoto/templates/deployment.yaml>
  - <https://raw.githubusercontent.com/kinvolk/service-mesh-benchmark/master/configs/benchmark/values.yaml>
  - <https://github.com/linkerd/linkerd2/issues?q=is%3Aissue+proxy+memory+leak>
  - <https://github.com/linkerd/linkerd2/issues/11012>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/linkerd/linkerd2-proxy`) · [data/wave14/enrich/raw/github_com_linkerd_linkerd2_proxy.json](../../../data/wave14/enrich/raw/github_com_linkerd_linkerd2_proxy.json) (enrichment confidence 0.7)

</details>
