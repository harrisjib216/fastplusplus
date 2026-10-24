# VerneMQ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Erlang` · `Apache-2.0` · 🟢 active

> Clustered Erlang/OTP MQTT 3.1/3.1.1/5.0 broker that uses all cores, sustaining loads that saturate single-threaded Mosquitto, at far higher memory and latency.

| | |
|---|---|
| **Beats** | Eclipse Mosquitto 2.0.15 (persistence disabled); also EMQX 4.4.16 |
| **Claimed result** | Sustains the 50k:50k msg/s offered load while Mosquitto 2.0.15 stabilises at 37,300/s for both pub and sub (about 1.34x higher sustained rate, derived from page data); 1M-connection (5k cps) scenario average connection latency 2.47 ms against Mosquitto 5.74 ms (about 2.3x lower, derived from page data; p50 2 ms for both). Latency is the opposite in the 50K:50K run: 2136.62 ms average pub-to-sub for VerneMQ against 353.82 ms for Mosquitto and 1.58 ms for EMQX. Against EMQX 4.4.16 VerneMQ loses in every scenario (1M connections: 2.47 ms vs EMQX 2.4 ms). |
| **Workload** | EMQX-run Open MQTT Benchmark Suite, enterprise set, point-to-point 50K publishers : 50K subscribers at QoS 1 for 30 minutes, plus a 1M-connections-at-5k-connections-per-second scenario, on one AWS c5.4xlarge broker node with XMeter as load generator. |
| **Metric** | throughput |
| **Hardware** | AWS c5.4xlarge (16 vCPU, 32 GB), Ubuntu 22.04.1 amd64, all machines in one VPC subnet; CPU model not stated |
| **Adoption** | about 3.6k stars, 432 forks |
| **Last commit** | 2026-10-22 |
| **Links** | [repository](https://github.com/vernemq/vernemq) · [benchmark](https://github.com/emqx/blog/blob/main/en/202305/open-mqtt-benchmarking-comparison-mqtt-brokers-in-2023.md) |

## Verdict

EMQ, which sells the competing EMQX broker, ran its Open MQTT Benchmark Suite with XMeter 3.2.4 against VerneMQ 1.12.6.2, Mosquitto 2.0.15 (persistence disabled), EMQX 4.4.16 and NanoMQ 0.17.0, each on one AWS c5.4xlarge (16 vCPU, 32 GB, Ubuntu 22.04.1, CPU model not stated) with 16-byte QoS 1 payloads and no TLS or auth. VerneMQ's only clear wins over Mosquitto are holding the 50k:50k msg/s offered load (Mosquitto plateaued at 37.3k/s using about one core, 6% CPU) and lower average connect latency at 1M connections (2.47 ms vs 5.74 ms, identical p50-p90 of 2 ms); it lost on latency and memory everywhere else and lost to EMQX in every scenario.

## Use it when

- A single Mosquitto instance is pinned at one core and cannot keep up with tens of thousands of QoS 1 messages per second across many independent topics (the cited 50K:50K point-to-point case, where Mosquitto settled at 37.3k/s and VerneMQ held the 50k/s offered load).
- You need horizontal scaling or failover: several broker nodes sharing one subscription view, with session takeover between nodes.
- Large connection counts (hundreds of thousands to about 1M devices) on a machine with ample RAM, where connection-setup latency matters more than memory (2.47 ms vs 5.74 ms average at 5k connects/s, driven by Mosquitto's p99 tail).
- You need offline message storage for persistent sessions plus pluggable auth (webhooks, Redis, PostgreSQL, MySQL, MongoDB) inside the broker.
- Your team already runs Erlang/OTP and can build and operate an OTP release itself.

## Skip it when

- Latency-sensitive delivery near saturation: in the same vendor test VerneMQ's 50K:50K average pub-to-sub latency was 2,136.62 ms (p99 16.5 s) against 353.82 ms for Mosquitto, and in the low-load basic set Mosquitto had lower average latency in every scenario (for example 0.25 ms vs 0.4 ms point-to-point).
- Fan-in through shared subscriptions at high rate: VerneMQ 1.12.6.2 collapsed to 7.6k pub / 3.5k sub per second with about 117 s average latency where Mosquitto delivered 50k in / 40k out.
- Memory-constrained hosts or edge gateways: it used about 4x to 22x more memory than Mosquitto in the cited runs (1.2 GB vs 254 MB average at the basic 1K:1K load; 22.4 GB and still rising vs 1 GB at 1M connections; derived from page data) and 90% CPU vs 6% at 50K:50K.
- High-rate single-topic fan-out: both VerneMQ and Mosquitto stalled near 80k/s against a 250k/s target, while EMQX and NanoMQ reached it.
- You want a vendor-supported binary without paying: official .deb/.rpm packages and Docker images are under the VerneMQ EULA and need a paid subscription for commercial use; the free path is building from source.

## How it is fast

Each TCP connection (Ranch acceptor) and each subscriber queue (vmq_queue) is its own lightweight Erlang process, so the BEAM schedulers spread work across every core instead of one event loop. Topic matching runs in the publishing session's process against public ETS tables opened with read_concurrency (a topic trie in vmq_reg_trie, with an optional vmq_reg_ordered_trie for sessions holding many subscriptions), and matched messages are pushed straight into each subscriber's queue process. Version 2.2.0 added experimental fan-out sharding (hidden settings fanout.shard_count and fanout.async_handoff) that splits large subscriber lists across worker processes; it postdates the cited benchmark and has no published numbers.

## Compared with alternatives

Pick VerneMQ over the catalogued Eclipse Mosquitto when one Mosquitto process is CPU-bound or you need a clustered MQTT broker, and accept far higher memory and worse latency at moderate load; for Kafka-style log streaming or non-MQTT messaging, RabbitMQ or NATS JetStream are the closer fits. No other MQTT broker (EMQX, NanoMQ, HiveMQ) is catalogued yet; in the same vendor test EMQX 4.4.16 and NanoMQ 0.17.0 beat VerneMQ on every enterprise scenario.

## Integration

| | |
|---|---|
| **Form** | standalone server (Erlang/OTP release built with `make rel`) |
| **Dependencies** | Erlang/OTP, libsnappy-dev and a C compiler for the eleveldb NIF (LevelDB offline message store); rebar3-fetched libraries including Ranch, Cowboy, Hackney, Cuttlefish and ReplayQ |
| **Minimum toolchain** | Erlang/OTP 27 (rebar.config minimum_otp_vsn 27.0; README says OTP 27-29) |
| **Platforms** | Linux and macOS (CI), ARM builds documented (Raspberry Pi, Apple M1); paid binary packages for Debian/Ubuntu, Amazon Linux 2023 and Alpine on x86-64 and ARM64 |
| **Thread safety** | Not applicable as a library; it is a network server. Internally one Erlang process per connection and per session queue, with shared state in concurrent ETS tables. |
| **Drop-in for the baseline** | partial: same MQTT 3.1/3.1.1/5.0 wire protocol, so clients need no change, but mosquitto.conf, password/ACL setup, bridges and monitoring must be redone in vernemq.conf and VerneMQ plugins |

## Gotchas

- Per-session queues default to max_online_messages = 1000 and max_offline_messages = 1000; excess messages are dropped (queue_message_drop metric) rather than blocking the publisher, so fan-out subscribers that fall more than 1000 messages behind lose data unless you raise the limits. The benchmark post does not say whether these defaults were changed or whether drops occurred.
- In a cluster, allow_register_during_netsplit, allow_publish_during_netsplit and allow_subscribe_during_netsplit all default to off, so a netsplit blocks new connections, publishes and subscribes until the cluster is consistent again; allow_anonymous also defaults to off.
- Memory growth reports recur: the 2023 benchmark saw memory climb from 18 GB to 22.4 GB after 1M connections were established; issue #2130 (1.12.6.2, memory growing for weeks, closed for inactivity) and open issue #2395 (2.0.1 cluster with reconnecting clients growing to about 16 GB) were never root-caused.
- 2.2.0 regressed webhook-based auth_on_publish/on_publish latency about 20x (issue #2534, Nagle's algorithm in the Hackney update); 2.2.1 adds connect_options with no_delay to fix it, so skip 2.2.0 if you use webhooks.

## Known shortcomings

- Vendor-run by EMQ, which sells the competing EMQX (commercial XMeter; emqx/mqttbs has prose, results and images only, no scripts or configs; no CPU model). VerneMQ's 1.34x throughput (derived) over Mosquitto comes from using all cores (VerneMQ 90% CPU and 6.02 GB vs Mosquitto 6%, about one core, and 318 MB); 50k msg/s is the offered-load cap; p50 latency equal and Mosquitto's average latency is far lower; EMQX and NanoMQ beat both. An Erlang broker filed under storage-and-data message queues next to Mosquitto.
- Enricher: vendor-run (EMQ) 2023 test of 1.12.6.2; the win is multi-core VerneMQ against Mosquitto on about one core, 50k/s is offered load, the 1M-connection average win comes only from Mosquitto's p99 tail, and default 1000-message session queues may have dropped messages unreported; official binaries need a paid subscription for commercial use.

## Caveats and trade-offs

Weak, mixed evidence; recorded because it is the only numeric head-to-head against a listed baseline that could be opened. (1) Vendor-run: EMQ sells EMQX, a competing broker, and runs the suite itself; XMeter is the load generator, the emqx/mqttbs repo holds only prose scenario definitions (no scripts), broker configurations are not published except Mosquitto persistence disabled, and the CPU model is not stated, so not reproducible (tier C). (2) The win over Mosquitto is narrow: VerneMQ only sustains the target rate, while its latency is far worse (avg 2136.62 ms vs 353.82 ms; p50 467 vs 361 ms; p99 16,500 vs 417 ms). In the 250K fan-out QoS 1 scenario both stall near 80k/s (VerneMQ 80k, Mosquitto 81k; avg latency 11,802.11 vs 12,240.83 ms); in the 50K fan-in shared-subscription scenario VerneMQ collapses (pub 7.6k, sub 3.5k, avg 116,888.61 ms) while Mosquitto reaches pub 50k, sub 40k (12,723.07 ms). In the basic set Mosquitto has lower average latency (0.25 vs 0.4 ms point-to-point, 5.73 vs 21.55 ms fan-out, 0.20 vs 0.34 ms fan-in, 0.6 vs 0.89 ms for 10K connections). The 1M-connection latency edge over Mosquitto is 2.47 vs 5.74 ms average with equal p50 (2 ms). (3) Old versions: VerneMQ 1.12.6.2 and EMQX 4.4.16 from the 2023 post; current VerneMQ is 2.2.x. (4) The repo README has only qualitative claims (high-performance, low latency), no numbers, and no benchmark is linked from the repo page. (5) Independent studies seen only as WebSearch snippets because mdpi.com, arxiv.org and koziolek.de are blocked from this container: Koziolek 2020 edge-gateway study reports maximum sustainable throughput VerneMQ 10K msg/s, EMQX 28K, HiveMQ 8K (no Mosquitto or RabbitMQ); the MDPI Energies 2021 stress-test paper is reported to put VerneMQ 1.11.0 first on QoS 1 latency in its cloud tests (copies disagree, unverified). A small third-party suite (lkskrt/mqtt-broker-benchmark) lists VerneMQ as considered but has no VerneMQ results. No number against RabbitMQ MQTT plugin was found. (6) Domain/category corrected from the Haiku guess (other-languages / concurrency-runtimes) to storage-and-data / message-queues-logs, where the Mosquitto wave-6 entry already sits. (7) Verifier addendum: the throughput edge is a multi-core vs single-threaded design difference, not a faster per-core path. In the 50K:50K run Mosquitto used 6% average CPU of 16 vCPU (about one core) and 318M average memory, while VerneMQ used 90% average CPU and 6.02G average memory; the 50k/s figure is the offered-load target, so VerneMQ's ceiling was not measured. In the 1M-connection run VerneMQ's memory never stabilised (18 GB at 1M connections, rising to 22.4 GB by the end of the 30-minute test) against 1G for Mosquitto. (8) EMQ's own C broker NanoMQ 0.17.0, also in the post, reaches 50k:50k at 91 ms average latency with 30% CPU, so VerneMQ is not the strongest alternative to Mosquitto on this page. (9) Mosquitto's sustained rate is 37,300/s per the page prose (table shows 37k:37k). [retier] Enricher: the sustained-rate win is multi-core VerneMQ against Mosquitto using about one core (6% of 16 vCPU); 50k/s is offered load, not a measured ceiling. The 1M-connection average win comes only from Mosquitto's p99 tail: p50-p90 are equal at 2 ms and VerneMQ's p95 is worse (3 vs 2 ms). VerneMQ's default max_online_messages and max_offline_messages of 1000 drop excess messages per session, and the post does not say whether drops occurred in the fan-out runs. Official binaries and Docker images need a paid subscription for commercial use. Memory growth issues #2130 (closed for inactivity) and #2395 (open) were never root-caused; 2.2.0 regressed webhook latency about 20x (#2534, fixed in 2.2.1).

Erlang/OTP broker (needs OTP 27-29, libsnappy-dev and a C compiler for the LevelDB offline store), not C or C++. In the same benchmark it used much more memory than Mosquitto (6.30G vs 341M at 50K:50K; 22.4G and still rising at 1M connections vs 1G) and more CPU (91% vs 6%). Features per README: MQTT 3.1, 3.1.1, 5.0, clustering, shared subscriptions, LevelDB offline storage, plugins, load shedding.

## Maintenance

Actively maintained (2.2.1 released in September 2026, commits through October 2026) and Apache-2.0 source you can build and run freely, but official binary packages and Docker images require a paid subscription for commercial use, and the only numeric comparison is a 2023 vendor-run test of version 1.12.6.2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** EMQ (vendor of the competing EMQX broker) ran its own Open MQTT Benchmark Suite with the commercial XMeter tool; emqx/mqttbs holds only README prose, results pages and images, with no scripts or broker configs, and the CPU model is not stated, so not reproducible and not an independent suite: tier C. No peer-reviewed VerneMQ-vs-Mosquitto win could be opened (MDPI Energies 2021 Mishra et al. seen only as search snippets without results).
- **Verifier notes:** All quoted numbers match the emqx/blog page (50K:50K rates and latencies, p50/p99, fan-out, fan-in, 1M-connection rows, versions VerneMQ 1.12.6.2, Mosquitto 2.0.15, EMQX 4.4.16). Metadata checked on github.com: Apache-2.0, 3.6k stars, 432 forks, not archived or a fork, last commit 2026-10-22 (after this prompt's 2026-10-11 date, so active). Win over Mosquitto is narrow and comes from using all 16 cores; caveats extended with CPU/memory and NanoMQ context.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-120 (wave 14 book seed pass, 2026-10-24); enrichment (wave 14 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/emqx/blog/blob/main/en/202305/open-mqtt-benchmarking-comparison-mqtt-brokers-in-2023.md>
  - <https://raw.githubusercontent.com/emqx/blog/main/en/202305/open-mqtt-benchmarking-comparison-mqtt-brokers-in-2023.md>
  - <https://github.com/vernemq/vernemq>
  - <https://github.com/vernemq/vernemq/commits>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/README.md>
  - <https://github.com/emqx/mqttbs>
  - <https://raw.githubusercontent.com/emqx/mqttbs/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/vernemq/vernemq>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/README.md>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/changelog.md>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/rebar.config>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/PROMISES.md>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/SECURITY.md>
  - <https://github.com/vernemq/vernemq/tree/main/apps>
  - <https://github.com/vernemq/vernemq/tree/main/apps/vmq_server/src>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/apps/vmq_server/src/vmq_reg_trie.erl>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/apps/vmq_server/src/vmq_reg.erl>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/apps/vmq_server/src/vmq_queue.erl>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/apps/vmq_server/src/vmq_fanout_shard_worker.erl>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/apps/vmq_server/src/vmq_shared_subscriptions.erl>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/apps/vmq_server/src/vmq_ranch.erl>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/apps/vmq_server/src/vmq_server.app.src>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/apps/vmq_server/priv/vmq_server.schema>
  - <https://raw.githubusercontent.com/vernemq/vernemq/HEAD/apps/vmq_acl/priv/default.acl>
  - <https://raw.githubusercontent.com/vernemq/docker-vernemq/HEAD/README.md>
  - <https://github.com/vernemq/vernemq/releases>
  - <https://github.com/vernemq/vernemq/issues?q=is%3Aissue%20memory>
  - <https://github.com/vernemq/vernemq/issues?q=is%3Aissue%20latency%20OR%20throughput%20OR%20slow>
  - <https://github.com/vernemq/vernemq/issues/2395>
  - <https://github.com/vernemq/vernemq/issues/2534>
  - <https://github.com/vernemq/vernemq/issues/2130>
  - <https://raw.githubusercontent.com/emqx/blog/main/en/202305/open-mqtt-benchmarking-comparison-mqtt-brokers-in-2023.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/vernemq/vernemq`) · [data/wave14/enrich/raw/github_com_vernemq_vernemq.json](../../../data/wave14/enrich/raw/github_com_vernemq_vernemq.json) (enrichment confidence 0.75)

</details>
