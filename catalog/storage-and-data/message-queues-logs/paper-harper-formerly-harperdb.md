# Harper (formerly HarperDB)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Study only · `JavaScript (unverified - Harper's source is not public; only the benchmark harness is)` · `The Harper Pro image under test is Elastic-2.0 (source-available, non-OSI; source at github.com/HarperFast/harper-pro). The open-source Harper core (github.com/HarperFast/harper) is Apache-2.0, and the benchmark harness is Apache-2.0.` · 🟢 active

> Node.js runtime fusing RocksDB-backed tables, app code and MQTT/WebSocket pub/sub; vendor benchmark: lower latency than Kafka stacks at ≤1k events/s.

| | |
|---|---|
| **Beats** | Apache Kafka (plus Postgres/Redis/Debezium/Kafka Streams ecosystem, workload-dependent) |
| **Claimed result** | W1: p50 9ms vs 876ms (\~100x); W2: p50 12.5ms vs 165ms (\~13x); W3 freshness: p50 1.05s vs 3.65s (\~3x); W4: p50 1.4ms vs 57ms (\~40x); Kafka Streams wins the W3 point-lookup case: 2.75ms (Kafka) vs 17ms (Harper) (\~6x Kafka faster) (all verbatim from the repo README results table) |
| **Workload** | Four workloads run on identical single-VM hardware (24GB RAM / 8 vCPU): (W1) durable write + downstream notify, (W2) filtered fan-out messaging to subscriber subsets, (W3) 5-minute windowed running-total analytics plus point lookups, (W4) sustained log ingestion at 1,000 events/sec. Conventional stack = Kafka (+ Postgres + Debezium + Redis + Kafka Streams as needed per workload) tuned idiomatically (acks=all, lz4, batched) vs a single Harper cluster with matched durability guarantees. |
| **Metric** | latency |
| **Hardware** | A single virtualized environment on an Apple Silicon Mac (M-series; exact chip not stated) under OrbStack, with 24 GB RAM, 8 vCPU and virtualized storage. Each of the 3 Harper nodes is capped at 2.6 vCPU and 4.6 GB. |
| **Adoption** | 0 stars on the benchmark repo; Harper is a commercially-backed database/streaming product |
| **Last commit** | 2026-05-28 |
| **Links** | [repository](https://github.com/HarperFast/harper) · [benchmark](https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/README.md) |

## Verdict

This is a Harper-affiliated whole-stack benchmark run in one OrbStack VM on an Apple Silicon Mac (24 GB, 8 vCPU; chip not stated). It pits a 3-node Harper Pro cluster (digest-pinned image, RocksDB default) against 3 Kafka brokers at RF=3 plus Postgres/Debezium/Redis/Kafka Streams as each workload needs. Harper's p50 was 9.4 ms vs 876 ms with Go glue, or 523 ms with language-matched Node glue, which the authors' own decision log adopts as the headline (\~56x, not \~100x); 12.5 ms vs 165 ms on W2; 1.05 s vs 3.65 s on W3 freshness; and 1.4 ms vs 57 ms on W4 at 1,000 events/s, while Kafka Streams won point lookups (2.75 ms vs 17 ms). The runs were short (15-30 s at 10-1,000 events/s, 3 paired runs, one run per stack for W3), W1 delivered only 83-84% on both stacks although the README says 100%, and a containerized Harper W4 variant cut the W4 gap to about 10-20x.

## Use it when

- Write-then-notify or filtered fan-out at tens to about 1,000 events/s, where you would otherwise wire up Postgres + Debezium + Kafka + Redis. The benchmark measured 9.4 ms vs 523 ms p50 at 50 events/s and 12.5 ms vs 165 ms at 10 events/s.
- Pushing live state to browsers or devices over MQTT or WebSockets when the consumer needs the latest value per key, not every intermediate change.
- Live dashboards with windowed aggregates at low per-key event rates, where Kafka Streams' suppress-until-window-close holds back results (W3 freshness: 1.05 s vs 3.65 s p50, 1.56 s vs 13.6 s p95).
- Node.js teams that want the database, API and pub/sub in one deployable unit, and that accept Harper Pro (Elastic-2.0) or Harper Fabric for multi-node.

## Skip it when

- Throughput-bound log ingestion at 10^5-10^6 events/s. The benchmark never ran a steady state above about 1,000 events/s, and its authors expect Kafka to win or tie on real multi-node hardware.
- CDC, event sourcing or audit consumers that need every change. Record subscriptions over in-process subscribe(), SSE and MQTT coalesce intermediate updates under burst writes, dropping up to 88.5% at threads: 4, with no gap marker (harper#2483, open).
- Point reads against live aggregates. Kafka Streams Interactive Queries answered in 2.75 ms p50 vs Harper's 17 ms through a REST endpoint.
- Stacks that depend on Kafka clients, Connect, Streams or Schema Registry, because Harper does not speak the Kafka protocol.
- When you need OSI-licensed multi-node replication. Replication ships in Harper Pro under Elastic-2.0, which forbids offering it as a hosted or managed service.

## How it is fast

The speedup comes from removing hops. The durable write, the enrichment lookups and the downstream notify all run in one process against embedded RocksDB (the `@harperfast/rocksdb-js` native binding; LMDB is the legacy engine), with a WeakRef-based LRU record cache, so there is no network or serialization step between database, cache and broker. Subscribers are fed from the audit (transaction) log: each 'committed' event schedules one `setImmediate` pass that walks the log and dispatches to per-key subscriber maps on every worker thread. Bursts collapse into one pass, and a QoS 0 MQTT frame is encoded once and shared by all matching subscribers. In the benchmark, the conventional stack pays for Debezium's WAL polling (the authors estimate 100-300 ms, not measured) and for a 50 ms Kafka consumer batch window, and Harper's MQTT path has neither.

## Compared with alternatives

Choose Harper over standalone brokers such as NATS JetStream, RabbitMQ or Mosquitto when the broker would otherwise sit beside a separate database and cache, and your app logic can run as Node.js inside the same process. Choose Redpanda or AutoMQ instead when you need Kafka API compatibility and Kafka-scale throughput.

## Integration

| | |
|---|---|
| **Form** | module: npm package `harper` with a CLI (`npm i -g harper`) or a Docker image; it is a server runtime with native addons, not an embeddable library |
| **Dependencies** | About 70 npm dependencies, including the native addons @harperfast/rocksdb-js, lmdb and argon2, plus fastify, msgpackr, cbor-x, ws and mqtt-packet. Optional: uWebSockets.js (glibc only, no musl) and the HNSW/fulltext addons. Multi-node replication needs Harper Pro. |
| **Minimum toolchain** | Node.js ^22.18.0 or &gt;=24 (package.json engines). There is a Bun integration-test target, but Node is the primary runtime. |
| **Platforms** | The Harper Pro README says it is tested on Linux amd64/arm64, macOS Intel/Apple Silicon and Windows. The core's Windows CI gate runs only a subset of the unit tests. |
| **Thread safety** | Each node runs several worker threads, and application modules load once per thread, so module-level side effects and subscriptions run N times. Record writes are RocksDB transactions with conflict retries. Cross-node writes resolve last-writer-wins by timestamp. table.lock() excludes only other lock() callers, and only on a single node (Phase 0). |
| **Drop-in for the baseline** | false: there is no Kafka wire protocol or client API, so producers and consumers must be rewritten for MQTT/WebSocket/SSE/REST or Harper Resource classes |

## Gotchas

- In the benchmark's Harper handlers, async work fired after the handler returned was cancelled (most fire-and-forget notifies were dropped). The harness therefore awaits an outbound HTTP notify inside the request. That notify is logged on failure and never retried, unlike the durable Debezium-to-Kafka path it is compared against.
- Resource modules load once per worker thread. A table.subscribe-based notifier fired about 7 times per node (21 times across 3 nodes), and W3 window-close notifies fired 2-21 times. At benchmark time there was no leader-election or compare-and-swap primitive to deduplicate them.
- Durability comparable to Kafka's acks=all must be opted into per request with `this.getContext().replicatedConfirmation = N`, where N counts peers. The default is async replication, and the MQTT broker has no per-write confirmation.
- Several subscription bugs are open: ending a subscription during fan-out makes the next subscriber miss that event (#2771), deletes are reported as empty puts or bare nulls (#2738, #2438), and startTime replay drops events committed after the audit cursor ends (#2311).

## Known shortcomings

- Vendor benchmark on an Apple Silicon M-series OrbStack VM; the open-source core is Apache-2.0 but harper-pro features are Elastic-licensed.
- The W1 \~100x is stale (its own decision log says \~56x); runs are tiny (15-30 s, 3 runs, W3 one run) and W1 delivered only 83-84% on both stacks (the README says 100%). Harper's notify is an awaited HTTP call in the handler, not durable, and per-thread load produced 7-21x duplicate notifies; the containerized MQTT variant is \~10-20x, not 40x. Replication is only in Harper Pro (ELv2); subscriptions can drop up to 88.5% of intermediate changes under burst (#2483), bad for CDC/log use; not a Kafka-protocol drop-in.

## Caveats and trade-offs

The author discloses Harper affiliation and invites Kafka experts to audit the setup. Everything runs on a single Apple Silicon laptop VM, which the README calls 'the largest known limitation'. The README says W4 above \~1,000 events/s is 'a laptop-VM artifact, not a system limit' and does not reflect Kafka's real throughput ceiling. No exact CPU model is given. The \~100x (W1) and \~40x (W4) figures compare whole stacks (PG+Debezium+Kafka, Kafka+Redis), not bare Kafka. Harper's source is public: the core is Apache-2.0 and Harper Pro is source-available under Elastic-2.0.

Harper itself is closed/source-available (pulled as a pinned Docker image, not built from public source in this repo), so only the benchmark harness is inspectable, not the system under test; single-VM test bed, not a multi-node production comparison; author is openly Harper-affiliated.

## Maintenance

The core is under active development: v5.2.14 and v5.3.0-beta.3 were released 2026-09-25, and the repo has 941 open issues and 90 stars. The core is Apache-2.0, but the replication behind the benchmarked 3-node setup is Elastic-2.0 Harper Pro, and the benchmark repo is a 0-star snapshot created and last pushed on 2026-05-28.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** A Harper-affiliated first-party benchmark. The harness is public (harness/, baseline/, harper/, scripts/campaign-w\*.sh) and the Kafka settings are stated. The hardware is given only as 'Apple Silicon Mac (M-series)' running an OrbStack VM with 24 GB and 8 vCPU, with no exact CPU model, so it is not A. It is not independent or peer-reviewed, so it is not B.
- **Verifier notes:** Every number in claimed_speedup matches the README table exactly, including the p50 figures and Kafka's W3 point-lookup win. The record wrongly says Harper's source is not public: HarperFast/harper (JavaScript, Apache-2.0, 90 stars, active) and HarperFast/harper-pro (Elastic License) both exist. The orchestrator may want repo_url set to https://github.com/HarperFast/harper, since that field is not correctable here. The benchmark_url on blob/master 302-redirects to main, the only branch.
- **Fields the verifier corrected:** `benchmark_url`, `hardware`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/HarperFast/kafka-v-harper-perf-test>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/master/README.md>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/README.md>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/LICENSE>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/docs/methodology.md>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/docs/reproducibility.md>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/docs/whitepaper.md>
  - <https://github.com/HarperFast/harper>
  - <https://github.com/HarperFast/harper-pro>
  - <https://github.com/HarperFast/harper-pro/blob/main/LICENSE.md>
- **Sources the enricher read:**
  - <https://github.com/HarperFast/harper>
  - <https://github.com/HarperFast/harper/blob/main/package.json>
  - <https://github.com/HarperFast/harper/blob/main/AGENTS.md>
  - <https://github.com/HarperFast/harper/blob/main/DESIGN.md>
  - <https://github.com/HarperFast/harper/blob/main/resources/DESIGN.md>
  - <https://github.com/HarperFast/harper/blob/main/server/DESIGN.md>
  - <https://github.com/HarperFast/harper/blob/main/dependencies.md>
  - <https://github.com/HarperFast/harper/blob/main/server/mqtt.ts>
  - <https://github.com/HarperFast/harper/blob/main/resources/transactionBroadcast.ts>
  - <https://github.com/HarperFast/harper/blob/main/resources/record-locks.md>
  - <https://github.com/HarperFast/harper/releases>
  - <https://github.com/HarperFast/harper/issues/2483>
  - <https://github.com/HarperFast/harper/issues/2771>
  - <https://github.com/HarperFast/harper/issues/906>
  - <https://github.com/HarperFast/harper/issues/1663>
  - <https://github.com/HarperFast/harper/issues?q=mqtt>
  - <https://github.com/HarperFast/harper/issues?q=subscription>
  - <https://github.com/HarperFast/harper-pro>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/README.md>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/docs/methodology.md>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/docs/decisions.md>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/docs/whitepaper.md>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/infrastructure/harper/docker-compose.yml>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/infrastructure/harper/.env.example>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/harper/app/w1/resources/W1Publish.js>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/harper/app/w1/schemas/w1.graphql>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/harper/app/w2/resources/W2Publish.js>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/harper/app/w3/resources/W3Publish.js>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/harper/app/w3/resources/W3Query.js>
  - <https://github.com/HarperFast/kafka-v-harper-perf-test/blob/main/harper/app/w4/resources/W4Publish.js>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:harper-formerly-harperdb`) · [data/wave6/enrich/raw/paper_harper_formerly_harperdb.json](../../../data/wave6/enrich/raw/paper_harper_formerly_harperdb.json) (enrichment confidence 0.7)

</details>
