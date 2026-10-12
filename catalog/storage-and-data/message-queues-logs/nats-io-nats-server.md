# NATS JetStream

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> CNCF Go messaging server whose built-in JetStream persistence showed \~14x lower median latency than Kafka at light load.

| | |
|---|---|
| **Beats** | Apache Kafka |
| **Claimed result** | p50 0.5ms vs Kafka's 7.2-7.8ms (\~14-15x), p99 0.9ms vs 12.7-13.5ms (\~14x), p999 2.8ms vs 14.0-19.1ms (\~5-7x) (derived from page data) |
| **Workload** | Single-node docker-compose deployment (Kafka 3.6 via cp-kafka 7.6.1 in KRaft mode vs NATS 2.10 with JetStream enabled), single partition/stream, no replication, small JSON payloads. Steady-state mode: producer paced at 500 msg/s with the consumer already tailing, 5s warm-up plus a 20s measurement window. Native Go clients: franz-go with default producer settings (no ProducerLinger set) for Kafka, and nats.go JetStream PublishAsync with an explicit-ack consumer for NATS. Latency measured with HdrHistogram. |
| **Metric** | latency |
| **Hardware** | Apple M4 (10 cores, 16GB RAM), macOS 26.5; containers under OrbStack (Docker 29.4.0, linux/arm64) with a VM of 10 CPUs / \~7.8GB; all brokers single-node, unreplicated, sharing the host with each other and the load generator |
| **Compiler and flags** | Bench client: Go 1.25 toolchain (bench/go.mod go 1.25.0), run with `go run .` from the Makefile (default flags), franz-go v1.21.4, nats.go v1.52.0, HdrHistogram-go v1.2.0. Brokers are prebuilt Docker images nats:2.10-alpine (-js) and confluentinc/cp-kafka:7.6.1 (Apache Kafka 3.6, KRaft). |
| **Adoption** | 20,771 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/nats-io/nats-server) · [benchmark](https://github.com/nipunnair/streaming-showdown/blob/main/COMPARISON.md) |

## Verdict

A personal benchmark (nipunnair/streaming-showdown) ran single-node, unreplicated nats:2.10-alpine JetStream (default file storage, R1) against Kafka 3.6 (cp-kafka 7.6.1, KRaft) in Docker under OrbStack on an Apple M4. Go 1.25 clients (nats.go PublishAsync plus an explicit-ack pull consumer, vs franz-go v1.21.4 at defaults) sent small JSON at 500 msg/s for 20 s after a 5 s warm-up, and HdrHistogram end-to-end latency came out at NATS p50 0.5 / p99 0.9 / p999 2.8 ms vs Kafka 7.2-7.8 / 12.7-13.5 / 14.0-19.1 ms; much of Kafka's median is plausibly franz-go's default 10 ms producer linger, which the bench never lowered, and NATS acked without fsync, so treat this as a light-load, client-default-sensitive result rather than a broker ceiling.

## Use it when

- Internal service-to-service events, fan-out and request/reply where you want replayable persistence and sub-millisecond p50 at modest rates (the test: 0.5 ms p50 at 500 msg/s with small JSON messages).
- Edge, IoT or small deployments that want one static binary with no JVM and no separate controller quorum. Release builds cover Linux on many architectures, macOS, Windows and FreeBSD.
- Workloads that need both queue semantics (work-queue retention, per-message ack and redelivery, shared pull consumers) and log-style replay in one system, plus KV or object storage.
- Many fine-grained or hierarchical subjects consumed with wildcard filters (for example per-entity subjects), instead of a fixed set of partitioned topics.

## Skip it when

- You depend on Kafka's wire protocol or ecosystem (Connect, Kafka Streams, ksqlDB, schema registry, key-based log compaction). NATS offers a Kafka bridge connector, not API compatibility.
- You need acknowledged writes to survive power loss and plan to run the defaults. JetStream acks before fsync (sync_interval 2 min). Jepsen (NATS 2.12.1, Dec 2025) lost 131,418 of 930,005 acked writes under coordinated power failure, and issues #7549, #7556, #7564 and #7567 (loss from .blk bit-flips, stream deletion from corrupt snapshots, deferred fsync, split-brain) were still open on 2026-09-26.
- High-throughput partitioned ingestion: the same benchmark's burst mode showed no clear throughput win (NATS \~269-339K vs Kafka \~252-333K msg/s producer-side), and replicated or multi-partition setups were not measured at all.
- Very high subject or dedup-ID cardinality on file-backed streams: per-subject and dedup indexes stay in RAM, and open issue #8485 reports OOMs or GC-driven latency when memory is capped.

## How it is fast

In this test the gap is mostly per-message path length and client defaults, not a storage algorithm: nats.go flushes each publish as soon as its flusher goroutine is kicked (no linger timer), while franz-go defaults to a 10 ms producer linger. On the server, the file store appends each record with a HighwayHash-64 checksum into a write-through cache of the current message block and, for unreplicated streams, writes it straight to the OS ("flush in place"), with fsync only every 2 minutes by default. A signal goroutine then matches the subject against the stream's consumer sublist and wakes the consumer loop, which serves the waiting pull request from that cache. Per-subject state is kept in an adaptive radix trie (server/stree).

## Compared with alternatives

Pick it over Redpanda (Kafka-API compatible, but it trailed Kafka in this same single-core, 500 msg/s test) when you don't need Kafka clients and care about small-message latency in one lightweight binary. Wisp beats NATS core pub/sub throughput but has no persistence, JetStream or clustering, so pick JetStream whenever you need durable, replayable streams.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (tar.gz/zip/deb/rpm and the official `nats` Docker image); JetStream enabled with `-js` or a `jetstream {}` config block; the source is the Go module github.com/nats-io/nats-server/v2 |
| **Dependencies** | None at runtime (single Go binary). Go module deps: klauspost/compress (S2), minio/highwayhash, nats-io jwt/nkeys/nuid/nats.go, golang.org/x/crypto, x/sys, x/time, google/go-tpm, antithesis-sdk-go (no-op build). Apps need a NATS client with JetStream support (the benchmark used nats.go v1.52.0). |
| **Minimum toolchain** | Prebuilt binaries need nothing. Building from source needs Go 1.26.0 (go.mod declares toolchain go1.26.8). The benchmark client was built with Go 1.25. |
| **Platforms** | v2.15.0 release binaries: Linux amd64/386/arm64/arm6/arm7/loong64/mips64le/ppc64le/riscv64/s390x, macOS amd64/arm64, Windows amd64/386/arm64, FreeBSD amd64. The benchmark ran linux/arm64 containers under OrbStack on an Apple M4. |
| **Thread safety** | Server: a concurrent network service, so not a user concern. nats.go documents its connection as safe to use from multiple goroutines concurrently. |
| **Drop-in for the baseline** | no |

## Gotchas

- Durability is opt-in. `sync_interval` defaults to 2 minutes, so an R1 stream can lose acknowledged messages on an OS crash or power loss, and the docs say even R3 can lose them under correlated failures. `sync_interval: always` fsyncs before every ack, which the docs call the slowest setting.
- Shared pull consumers are partition-less, so two sequential messages on the same subject can go to different subscribers and ordering across parallel workers is lost. Use `partition()` subject mapping if you need per-key ordering.
- JetStream publish is at-least-once. Exactly-once needs the `Nats-Msg-Id` header deduplicated within the stream's DuplicateWindow, plus consumer-side double ack. Messages are capped at 1 MB by default; the Object Store chunks larger objects.
- nats.go PublishAsync allows 4000 in-flight acks by default and then stalls, waiting up to 200 ms by default. The docs also say Replicas=2 brings no benefit, so use R1, R3 or R5.

## Known shortcomings

- Kafka's p50 in this benchmark is likely inflated by franz-go's default 10 ms linger, so the \~14x p50 gap overstates the difference; single Apple M4 machine.
- Default JetStream acks before fsync (2-minute sync interval): Jepsen (2025-12, NATS 2.12.1) lost 131k of 930k acknowledged writes on correlated power loss, and issues #7549/#7556/#7564/#7567 remain open. Burst mode shows no throughput win; replication and multi-partition were not tested; the bench ran 2.10 (current 2.15.0). Not a Kafka drop-in; pull consumers have no partitions (ordering lost across parallel workers); subject/dedup indexes stay in RAM (#8485 OOM when memory is capped).

## Caveats and trade-offs

Benchmark repo has 0 stars and no license and is a personal project. Single node, single partition, no replication, 20s windows at one light load (500 msg/s). The repo's own burst-mode latency numbers are called 'not meaningful' by its author, so only the steady-state numbers are used here. LEARNINGS.md says these were stable within \~5% across repeated runs. Much of Kafka's \~7 ms p50 is probably the franz-go v1.21.4 default producer linger of 10 ms (pkg/kgo/config.go), which the bench never overrides, so the 14x median gap partly reflects a client default rather than the broker. Older broker versions (NATS 2.10, Kafka 3.6). Not independently reproduced elsewhere.

Single-broker, no replication, no consumer-group/partition parallelism exercised; author explicitly cautions that this single-core, low-concurrency setup doesn't exercise thread-per-core designs and shouldn't be read as a general ranking; JetStream lacks Kafka's log-compaction/Kafka-Streams/Connect/schema-registry ecosystem.

## Maintenance

Actively maintained CNCF project (v2.15.0 released 2026-09-17, commits through 2026-09-25, \~20.8k stars, Apache-2.0, Trail of Bits audit April 2025), though the benchmark used the older 2.10 line and the four Jepsen durability issues filed in Nov 2025 remain open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. COMPARISON.md's steady-state table has Kafka p50 7.2-7.8 / p99 12.7-13.5 / p999 14.0-19.1 ms vs NATS 0.5 / 0.9 / 2.8 ms. The harness is public (bench/steady.go, bench/nats_adapter.go, bench/kafka_adapter.go, run via `go run . -mode=steady` in the Makefile). LEARNINGS.md states the Go 1.25 toolchain with default build flags, the Apple M4 CPU, and the pinned images nats:2.10-alpine and cp-kafka:7.6.1, which meets the A criteria as applied to go-sieve in batch 58.
- **Verifier notes:** The record's caveats were wrong in two places: LEARNINGS.md does name the CPU (Apple M4), and the author reports repeated runs, not a single run. With the Go toolchain, run command, CPU and pinned images all stated, tier A applies. Flag for the orchestrator: the franz-go default 10 ms linger likely inflates Kafka's latency at this low rate.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `workload`, `caveats`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/nipunnair/streaming-showdown/blob/main/COMPARISON.md>
  - <https://github.com/nipunnair/streaming-showdown>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/LEARNINGS.md>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/Makefile>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/bench/kafka_adapter.go>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/bench/nats_adapter.go>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/bench/steady.go>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/bench/go.mod>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/docker-compose.nats.yml>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/docker-compose.kafka.yml>
  - <https://raw.githubusercontent.com/twmb/franz-go/v1.21.4/pkg/kgo/config.go>
  - <https://github.com/nats-io/nats-server>
- **Sources the enricher read:**
  - <https://github.com/nats-io/nats-server>
  - <https://github.com/nats-io/nats-server/blob/main/README.md>
  - <https://github.com/nats-io/nats-server/blob/main/go.mod>
  - <https://github.com/nats-io/nats-server/blob/main/server/filestore.go>
  - <https://github.com/nats-io/nats-server/blob/main/server/stream.go>
  - <https://github.com/nats-io/nats-server/blob/main/server/consumer.go>
  - <https://github.com/nats-io/nats-server/blob/main/server/stree/stree.go>
  - <https://github.com/nats-io/nats-server/blob/main/server/memstore.go>
  - <https://github.com/nats-io/nats-server/blob/main/server/thw/thw.go>
  - <https://github.com/nats-io/nats-server/releases/tag/v2.15.0>
  - <https://github.com/nats-io/nats-server/issues/7549>
  - <https://github.com/nats-io/nats-server/issues/7556>
  - <https://github.com/nats-io/nats-server/issues/7564>
  - <https://github.com/nats-io/nats-server/issues/7567>
  - <https://github.com/nats-io/nats-server/issues/8485>
  - <https://github.com/nats-io/nats-server/issues?q=is%3Aopen+label%3Adefect>
  - <https://github.com/nats-io/nats-server/issues?q=jetstream+latency>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/COMPARISON.md>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/LEARNINGS.md>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/bench/nats_adapter.go>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/bench/kafka_adapter.go>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/bench/steady.go>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/docker-compose.nats.yml>
  - <https://github.com/nipunnair/streaming-showdown/blob/main/Makefile>
  - <https://raw.githubusercontent.com/twmb/franz-go/v1.21.4/pkg/kgo/config.go>
  - <https://github.com/nats-io/nats.go/blob/main/nats.go>
  - <https://github.com/nats-io/nats.go/blob/main/jetstream/pull.go>
  - <https://github.com/nats-io/nats.go/blob/main/jetstream/jetstream.go>
  - <https://github.com/nats-io/nats.go/blob/main/jetstream/publish.go>
  - <https://github.com/nats-io/nats.docs/blob/master/nats-concepts/jetstream/README.md>
  - <https://github.com/nats-io/nats.docs/blob/master/nats-concepts/jetstream/streams.md>
  - <https://github.com/nats-io/nats.docs/blob/master/nats-concepts/overview/compare-nats.md>
  - <https://github.com/nats-io/nats.docs/blob/master/nats-concepts/subject_mapping.md>
  - <https://jepsen.io/analyses/nats-2.12.1>
  - <https://hn.algolia.com/api/v1/search?query=jepsen%20nats&tags=story>
  - <https://github.com/iamd3vil/wisp>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/nats-io/nats-server`) · [data/wave6/enrich/raw/github_com_nats_io_nats_server.json](../../../data/wave6/enrich/raw/github_com_nats_io_nats_server.json) (enrichment confidence 0.72)

</details>
