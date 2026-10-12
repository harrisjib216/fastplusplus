# Zenoh

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR EPL-2.0` · 🟢 active

> Rust pub/sub and query protocol that can run with or without a broker; in one 2023 study it moved 10-65x Kafka's bitrate.

| | |
|---|---|
| **Beats** | Kafka |
| **Claimed result** | Single-machine bitrate, Zenoh peer mode vs Kafka 3.2.1 (rdkafka 0.28.0 client): 65x at 8B payload, 24x at Zenoh's 8KB peak, 10x at 32KB (all stated on page). Multi-machine 100GbE: best \~50 Gbps (P2P) / \~34 Gbps (brokered) vs Kafka's best 5 Gbps, i.e. \~10x / \~6.8x (derived from page data) |
| **Workload** | Independent NTU-team evaluation: single-machine and 100Gb-Ethernet multi-machine pub/sub throughput sweep across payload sizes 8B-512MB, comparing Zenoh 0.7.0-rc (peer & brokered modes), Apache Kafka 3.2.1 (rdkafka 0.28.0 client), Eclipse Mosquitto 2.0.15 (MQTT), and Cyclone DDS |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5800X fixed at 4.0GHz (8-core/16-thread), 32GB DDR4-3200MHz, Ubuntu 20.04.3 LTS; multi-machine scenario over 100Gb Ethernet |
| **Adoption** | 3.2k stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/eclipse-zenoh/zenoh) · [benchmark](https://zenoh.io/blog/2023-03-21-zenoh-vs-mqtt-kafka-dds/) |

## Verdict

A National Taiwan University team ran Zenoh 0.7.0-rc against a Kafka 3.2.1 broker driven by the Rust rdkafka 0.28.0 client (linger.ms=0, batch.size=400KB, acks=0, no compression) on a Ryzen 7 5800X fixed at 4.0 GHz with Ubuntu 20.04, reporting medians. Single-machine, Zenoh peer mode got 65x Kafka's bitrate at 8 B, 24x at 8 KB and 10x at 32 KB. Over 100 GbE, Zenoh reached \~50 Gbps P2P and \~34 Gbps brokered against Kafka's 5 Gbps. No compiler or flags are given, Kafka could not be run above 512 KB, the benchmark repo now returns 404, and the page's multi-machine iperf ceiling (44 Gbps) is below Zenoh's own 50 Gbps figure.

## Use it when

- High-rate small messages (8 B to 8 KB) between services, sensors or robots. In the NTU test Zenoh passed 4M msg/s, while Kafka stayed at 56K-63K msg/s for payloads under 2 KB.
- Latency-sensitive fan-out where losing the broker hop matters: 10 us (Zenoh P2P) vs 73 us (Kafka) single-machine median one-way latency with 64 B pings.
- Topologies that span edge to cloud (robotics, V2X, IoT) and need to switch between peer-to-peer, client and routed modes without changing application code.
- Large payloads between processes on the same host, using the opt-in shared-memory feature (reference-counted SHM buffers, automatic conversion to non-SHM when data leaves the host).
- Mixed-language systems, including microcontrollers through zenoh-pico, that need one protocol from C/C++ through Python to Rust.

## Skip it when

- You need Kafka's durable, replayable, partitioned log: retention, consumer groups, offsets, rewinds. Zenoh storages keep only the latest value per key. AdvancedPublisher history is an in-memory per-publisher cache (default depth 1) behind the unstable feature.
- You depend on the Kafka ecosystem (existing clients, Connect, Streams, schema tooling). Zenoh is not wire- or API-compatible.
- You need exactly-once or transactional delivery. The docs read for this entry do not cover either.
- Large messages over slow or lossy links with default settings: the default Drop congestion control can discard multi-MB messages even without real congestion (open issue #2258).
- You plan to size a deployment from the headline ratios. They come from 2023's 0.7.0-rc, which predates the 0.11 Tokio port and the 1.0 batching rework, and the benchmark code is gone.

## How it is fast

The wire protocol is compact: variable-length integer encoding, and key expressions are declared once and then sent as small numeric resource IDs. That gives a minimum of 5 bytes of overhead per message. A multi-stage transmission pipeline serializes many small messages into each frame (automatic batching), reuses pre-allocated batch buffers, and fragments large ones. The team says it keeps heap allocations off the critical path and limits async to the network-facing code, to keep future stack frames small. Payloads are zero-copy ZBytes. There is an opt-in shared-memory transport for same-host traffic and an opt-in io_uring receive path on Linux. In peer mode the broker hop disappears, and nothing is appended to a durable log on the data path.

## Compared with alternatives

Pick Zenoh over Redpanda or Woodpecker when the job is moving live data with low latency, not keeping a durable log. Those two stay Kafka-style storage systems. Over TCPSHM, pick it when you need many-to-many routing, discovery and multiple languages rather than a single point-to-point C++ link with sub-microsecond latency.

## Integration

| | |
|---|---|
| **Form** | crate (Rust); zenoh-c builds a C library from the same Rust core; zenoh-cpp is header-only C++ over zenoh-c or zenoh-pico; zenohd router binary |
| **Dependencies** | tokio, rustls/tokio-rustls, quinn (QUIC), serde, lz4_flex, flume/crossbeam and others; the Cargo features transport_tcp/udp/tls/quic/ws/unixsock are on by default; shared-memory, uring, transport_serial/vsock/unixpipe and unstable are opt-in |
| **Minimum toolchain** | Rust 1.75 (some dependencies may need newer; zenoh-pinned-deps-1-75 pins compatible versions); zenoh-cpp needs C++17 |
| **Platforms** | Linux, macOS, Windows (all in CI); io_uring receive path is Linux-only; zenoh-pico covers microcontrollers |
| **Thread safety** | Session is an Arc around shared state: cheap to clone and documented as shareable across tasks and threads. The API works both async (Tokio) and blocking (.wait()). |
| **Drop-in for the baseline** | no |

## Gotchas

- Publications default to CongestionControl::Drop, so a full queue silently drops data. The benchmark used Block. BlockFirst was added to mitigate large-message drops.
- Block can stall a router: open issue #1876 (still reported on 1.9.0) shows a router looping on 'Unable to push non droppable network message' when a link is cut or congested, without closing the transport.
- Reliability::Reliable does not retransmit at the Zenoh layer; it only selects a reliable link such as TCP. Loss detection and recovery need AdvancedPublisher and AdvancedSubscriber, which are in the unstable API.
- The express flag turns batching off: better latency, lower throughput. Batching behaviour changed with the 0.11 Tokio port and was reworked in 1.0, and 1.0 was not backward compatible with 0.11.

## Known shortcomings

- The benchmark URL 404s (branch master, not main; now the zenoh.io blog) and the ZettaScaleLabs/zenoh-perf bench repo is gone; no compiler stated; the arXiv comparison is a non-peer-reviewed preprint (verifier downgrade from A).
- Not a Kafka drop-in: no durable log, offsets or consumer groups; storages keep only the latest value per key. The benchmark is a 2023 vendor blog on 0.7.0-rc (before the Tokio port and 1.0 batching rework); the page's multi-machine iperf 'ideal' (44 Gbps) is below Zenoh's own P2P figure (50 Gbps); Kafka ran with linger.ms=0, acks=0 via rdkafka; nothing measured above 512 KB. Default publisher congestion control is Drop (silent drops; the bench used Block); multi-MB drops (#2258) and Block stalling the router (#1876) are open. 'Reliable' only selects the link; Zenoh itself doesn't retransmit.

## Caveats and trade-offs

Contributed by a National Taiwan University team but published on Zenoh's own blog, with a foreword by the Zenoh lead, so it is not arm's-length. The benchmark code repo cited by both the blog and the paper (ZettaScaleLabs/zenoh-perf, comparison/) is now 404, so the results cannot be reproduced from public code. No compiler versions or flags are stated. The arXiv 2303.09419 companion is a v1 preprint, not peer-reviewed. The headline ratios pit Zenoh peer-to-peer mode against brokered Kafka (Zenoh brokered mode also wins, by less). The tested Zenoh 0.7.0-rc dates from 2023. Kafka could not be measured above 512KB because the Rust Kafka binding failed on messages over 1MB.

Evaluation used Zenoh 0.7.0-rc, a 2023 pre-release version; the rdkafka Kafka bindings used failed to send messages above 1MB, limiting the comparison at large payload sizes; benchmark exercised the Rust zenoh core, not the official zenoh-c/zenoh-cpp C/C++ bindings directly (though they wrap the same core)

## Maintenance

Actively maintained Eclipse project (release 1.10.1 on 2026-09-07, last main commit 2026-09-15), dual Apache-2.0/EPL-2.0 licensed; use it as a Cargo dependency or through zenoh-c/zenoh-cpp, not as a small vendorable source drop.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** The blog states the Kafka ratios directly: Zenoh peer mode gets 65x Kafka's bitrate at 8B, 24x at the 8KB peak and 10x at 32KB (single machine). The Ryzen 7 5800X and the component versions are given, but no compiler or flags are stated in the blog or in the arXiv 2303.09419 v1 preprint. The linked benchmark code (github.com/ZettaScaleLabs/zenoh-perf/tree/master/comparison) now returns 404 on both the GitHub API and github.com. With no public code, no compiler, and a preprint that is not peer-reviewed (no journal-ref) published on the vendor's blog, this cannot be A or B, so C.
- **Verifier notes:** The original benchmark_url (zenoh-web blob/main/...) was 404 because the repo's default branch is master. I replaced it with the published zenoh.io page, which is identical to blob/master. The last commit on the default branch is 2026-09-15 (pushed_at 2026-09-25 is from another branch). License confirmed as EPL-2.0 OR Apache-2.0 (Cargo.toml SPDX and LICENSE).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/eclipse-zenoh/zenoh>
  - <https://raw.githubusercontent.com/eclipse-zenoh/zenoh/main/LICENSE>
  - <https://raw.githubusercontent.com/eclipse-zenoh/zenoh/main/Cargo.toml>
  - <https://github.com/zenoh-rs/zenoh-web/blob/main/content/blog/2023-03-21-zenoh-vs-mqtt-kafka-dds.md>
  - <https://github.com/zenoh-rs/zenoh-web/blob/master/content/blog/2023-03-21-zenoh-vs-mqtt-kafka-dds.md>
  - <https://raw.githubusercontent.com/zenoh-rs/zenoh-web/master/content/blog/2023-03-21-zenoh-vs-mqtt-kafka-dds.md>
  - <https://zenoh.io/blog/2023-03-21-zenoh-vs-mqtt-kafka-dds/>
  - <https://github.com/ZettaScaleLabs/zenoh-perf/tree/master/comparison>
  - <https://arxiv.org/abs/2303.09419>
  - <https://arxiv.org/pdf/2303.09419>
- **Sources the enricher read:**
  - <https://github.com/eclipse-zenoh/zenoh>
  - <https://github.com/eclipse-zenoh/zenoh/blob/main/Cargo.toml>
  - <https://github.com/eclipse-zenoh/zenoh/blob/main/zenoh/Cargo.toml>
  - <https://github.com/eclipse-zenoh/zenoh/blob/main/zenoh/src/lib.rs>
  - <https://github.com/eclipse-zenoh/zenoh/blob/main/zenoh/src/api/session.rs>
  - <https://github.com/eclipse-zenoh/zenoh/blob/main/io/zenoh-transport/src/common/pipeline.rs>
  - <https://github.com/eclipse-zenoh/zenoh/blob/main/commons/zenoh-protocol/src/core/mod.rs>
  - <https://github.com/eclipse-zenoh/zenoh/blob/main/commons/zenoh-uring/README.md>
  - <https://github.com/eclipse-zenoh/zenoh/blob/main/zenoh-ext/src/advanced_publisher.rs>
  - <https://github.com/eclipse-zenoh/zenoh/blob/main/zenoh-ext/src/advanced_cache.rs>
  - <https://github.com/eclipse-zenoh/zenoh/blob/main/.github/workflows/ci.yml>
  - <https://github.com/eclipse-zenoh/zenoh/releases>
  - <https://github.com/eclipse-zenoh/zenoh/commits/main>
  - <https://github.com/eclipse-zenoh/zenoh/security/advisories>
  - <https://github.com/eclipse-zenoh/zenoh/issues/2258>
  - <https://github.com/eclipse-zenoh/zenoh/issues/1876>
  - <https://github.com/eclipse-zenoh/zenoh/issues/2721>
  - <https://github.com/eclipse-zenoh/zenoh/issues/2770>
  - <https://github.com/eclipse-zenoh/zenoh/issues?q=throughput>
  - <https://github.com/eclipse-zenoh/zenoh/issues?q=memory+leak>
  - <https://github.com/eclipse-zenoh/zenoh-cpp>
  - <https://raw.githubusercontent.com/zenoh-rs/zenoh-web/master/content/blog/2023-03-21-zenoh-vs-mqtt-kafka-dds.md>
  - <https://raw.githubusercontent.com/zenoh-rs/zenoh-web/master/content/blog/2021-07-05-zenoh-overhead.md>
  - <https://raw.githubusercontent.com/zenoh-rs/zenoh-web/master/content/blog/2021-07-13-zenoh-performance-async.md>
  - <https://raw.githubusercontent.com/zenoh-rs/zenoh-web/master/content/blog/2024-10-21-zenoh-firesong.md>
  - <https://raw.githubusercontent.com/zenoh-rs/zenoh-web/master/content/docs/manual/plugin-storage-manager.md>
  - <https://github.com/ZettaScaleLabs/zenoh-perf/tree/master/comparison>
  - <https://arxiv.org/abs/2303.09419>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/eclipse-zenoh/zenoh`) · [data/wave6/enrich/raw/github_com_eclipse_zenoh_zenoh.json](../../../data/wave6/enrich/raw/github_com_eclipse_zenoh_zenoh.json) (enrichment confidence 0.75)

</details>
