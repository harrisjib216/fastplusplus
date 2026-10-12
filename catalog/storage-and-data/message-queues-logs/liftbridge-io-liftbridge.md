# Liftbridge

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Go server adding Kafka-style partitioned, replicated logs on top of NATS; self-reports \~1.1x NATS JetStream publish throughput on one node.

| | |
|---|---|
| **Beats** | NATS JetStream |
| **Claimed result** | \~241K msgs/sec (4 publishers, pub-batch=100, single node, RF=1) vs NATS JetStream's \~220K msgs/sec, which the README quotes 'with similar settings (pubbatch=100, file storage, RF=1)' - about 1.1x higher throughput (derived from page data) |
| **Workload** | Single-node Liftbridge with replication factor 1, 4 concurrent publishers and pub-batch=100. The README's Running Benchmarks section shows the repo's bench/producer tool with 256-byte messages and ack-policy leader, but the table does not state which size or ack policy it used. 'File storage' is stated only for the JetStream side. |
| **Metric** | throughput |
| **Adoption** | 2.8k stars |
| **Last commit** | 2026-07-15 |
| **Links** | [repository](https://github.com/liftbridge-io/liftbridge) · [benchmark](https://github.com/liftbridge-io/liftbridge/blob/master/README.md) |

## Verdict

Using its own bench/producer tool, the repo reports \~241K msgs/sec (P99 2.0 ms) for 4 concurrent publishers, each pipelining 100 async publishes, on a single node with RF=1 and 256-byte messages. The message size comes from the CHANGELOG, and the ack policy is not stated, but the tool's default and the README example are both leader. The \~220K msgs/sec NATS JetStream figure is quoted as 'similar settings (pubbatch=100, file storage, RF=1)' with no source, version, hardware or harness, and no hardware, OS, Go version or run length is given for either side, so the \~1.1x is a cross-run comparison, not a side-by-side measurement.

## Use it when

- You already run NATS and want durable, replayable, partitioned streams on existing subjects without changing the publishers.
- A Go shop that wants Kafka-like semantics (consumer groups, compaction, retention, offset/timestamp replay) from a single self-contained binary with embedded NATS instead of a JVM cluster.
- Small-message ingest (the benchmark uses 256-byte messages) in the roughly 100-250K msgs/sec per-partition range, where the client can batch or pipeline publishes.
- A single-region cluster run with RF=3, AckPolicy_ALL and min.insync.replicas=2 to get quorum-acknowledged, at-least-once delivery.
- Edge or IoT nodes running RF=1, where losing leader-acked but unflushed messages on a crash is acceptable.

## Skip it when

- You need fsync-level durability. Segment writes are never fsynced and the high watermark is checkpointed only every 5 s by default. A configurable sync policy exists only as a proposal in the repo's own bottleneck analysis.
- Multi-region clusters: an engineer who deployed it reported on HN that cross-region latency throttles the Raft metadata protocol, which slows stream creation and ISR changes. Federated clustering is only on the roadmap.
- You need transactions, exactly-once or idempotent producers, message compression, tiered storage, Prometheus metrics or SASL auth. The roadmap lists all of these as not done, and no release has shipped since v26.01.1.
- Read-heavy fan-out: the repo's own analysis flags one-message-at-a-time reads, one gRPC Send per message and per-message allocations on the subscribe path.
- Choosing it over JetStream mainly for speed: the \~1.1x margin is against an unsourced JetStream figure, and no replicated or AckPolicy_ALL throughput is published.

## How it is fast

Streams replicate with a Kafka-style in-sync-replica (ISR) protocol and use Raft (hashicorp/raft) only for cluster metadata, so each message goes into one log rather than a Raft log plus a message log. The partition leader drains its NATS subscription into batches of up to 1,024 messages (batch.max.messages). It appends each batch to a segmented commit log with a memory-mapped offset index, and segment writes go to the OS page cache with no fsync. The January 2026 release that added the benchmark also added an RF=1 fast path. For LEADER/NONE acks it skips the commit queue and advances the high watermark once per batch, and clients can pipeline publishes over the streaming gRPC PublishAsync call.

## Compared with alternatives

Pick it over NATS JetStream when you want Kafka-style partitioned logs with ISR replication, consumer groups and compaction layered onto an existing NATS deployment; if you want the default, better-supported choice inside nats-server, pick JetStream, since the throughput edge is marginal and unverified. Redpanda and Fluvio are catalogued as Kafka replacements with multi-level published numbers (Redpanda up to 1 GB/s). Choose those when throughput or tail latency at scale is the main requirement, and Liftbridge when you want a lighter, Go-native service tied to NATS.

## Integration

| | |
|---|---|
| **Form** | module (standalone Go server; prebuilt linux/darwin/windows tarballs, .deb/.rpm packages and a ghcr.io Docker image; clients speak gRPC) |
| **Dependencies** | NATS Server v2.10.0+ (external, or embedded in-process via nats.embedded); hashicorp/raft + raft-boltdb (metadata), gRPC, tysonmote/gommap (mmap index), google/tink (encryption at rest), casbin (authorization); clients: go-liftbridge v2 (official), plus Java and Rust official clients and community Node.js/Python clients |
| **Minimum toolchain** | Go 1.25.6+ to build from source (raised from Go 1.21 in v26.01.1) |
| **Platforms** | Release binaries for linux, darwin and windows on amd64 and arm64; CI tests run only on ubuntu-latest |
| **Thread safety** | The server accepts many concurrent publishers and subscribers, but a single segment write mutex serializes appends within a partition (per the repo's bottleneck analysis). On the client side, the repo's bench tool warns that pub-batch &gt; 1 combined with more than one concurrent publisher 'may hang due to go-liftbridge client limitations'. |
| **Drop-in for the baseline** | partial: it shares NATS subjects, so plain NATS publishers can feed Liftbridge streams unchanged, but JetStream streams, consumers and client APIs do not carry over; reading and managing streams needs a Liftbridge gRPC client |

## Gotchas

- The headline configuration (4 concurrent publishers with pub-batch=100) is the same combination the repo's bench/producer tool prints a warning about possibly hanging because of go-liftbridge client limitations.
- The default ack policy is LEADER, which acks after the leader's page-cache write. With RF=1 (the default replication factor) and no fsync, acked messages can be lost in a crash; uncommitted messages can also be lost during a leader change.
- Two defaults to change: anonymous telemetry is on and sends instance ID, OS, CPU and memory info to telemetry.basekick.net every 24 h (turn it off with telemetry.enabled: false or LIFTBRIDGE_TELEMETRY_ENABLED=false), and partition data lives under /tmp/liftbridge/&lt;namespace&gt; unless you set data.dir.
- Open security reports: #470, where Subscribe applies the consumer-group replacement (closing the legitimate subscriber) before checking authorization, with fix PR #471 still open; and #468, where NATS credentials embedded in server URLs are written verbatim to the startup log.

## Known shortcomings

- Only \~1.1x vs JetStream (241K vs \~220K msgs/s); the 241K is the RF=1 leader-ack fast path, the JetStream figure has no source and no message size is given.
- SECURITY/PRIVACY: telemetry is on by default (telemetry.basekick.net); open issues include authorization after group replace (#470, fix PR #471 open) and NATS credentials written to logs (#468). No fsync on segment writes, a 5 s high-watermark checkpoint and default LEADER ack with RF=1, so acknowledged messages can be lost on crash; data dir defaults to /tmp/liftbridge. The headline config (4 publishers x batch 100) is one the client's own bench tool warns 'may hang'; 256 B messages, no hardware/Go version. No compression/metrics/exactly-once/tiered storage; no release since v26.01.1.

## Caveats and trade-offs

Self-reported numbers with no hardware, CPU model, OS or Go version for either side. The \~220K msgs/sec JetStream figure has no source, version, benchmark code or run configuration in the repo; the settings are only called 'similar', so this is not a side-by-side run. The \~1.1x margin is small enough to be within run-to-run variation. The same commit (bd763768, 2026-01-06) that added the numbers also added an RF=1 fast path that skips the commit queue under LEADER/NONE ack policies. The headline therefore reflects a single-node, leader-ack setup rather than durable replicated throughput. Liftbridge also requires a NATS server underneath.

Go implementation layered on NATS Streaming/JetStream semantics rather than Kafka's; simpler ops story but a much smaller ecosystem/tooling base than Kafka; only one config point (RF=1, single node) is benchmarked.

## Maintenance

Active in name: Basekick Labs revived it with v26.01.1 in January 2026 after no releases since v1.9.0 in September 2022. Commits since then are mostly dependabot bumps plus one Docker fix (last 2026-07-15), and the roadmap's v26.02 items have not shipped. It is Apache-2.0 with prebuilt binaries and packages, so it is usable as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance section lists first-party single-node, RF=1 numbers (\~241K msgs/sec with 4 publishers and pub-batch=100) and states that NATS JetStream reaches \~220K msgs/sec 'with similar settings'. The bench/producer and bench/consumer tools are public, but no hardware, OS, Go version or message size is tied to the table. The JetStream figure has no source, code or run configuration, so this stays at C.
- **Verifier notes:** Commit bd763768's message confirms the README numbers and the JetStream comparison were added together with the bench tools. Metadata checks out: Apache-2.0, 2,802 stars, last commit 2026-07-15 (active), not a fork or archived. baseline_in_list was left unchanged because I could not check it.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/liftbridge-io/liftbridge>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/README.md>
  - <https://github.com/liftbridge-io/liftbridge/tree/master/bench>
  - <https://github.com/liftbridge-io/liftbridge/commit/bd763768>
- **Sources the enricher read:**
  - <https://github.com/liftbridge-io/liftbridge>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/README.md>
  - <https://github.com/liftbridge-io/liftbridge/tree/master/bench>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/bench/producer/main.go>
  - <https://github.com/liftbridge-io/liftbridge/commit/bd763768>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/CHANGELOG.md>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/go.mod>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/server/partition.go>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/server/api.go>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/server/config.go>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/server/commitlog/segment.go>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/server/commitlog/commitlog.go>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/server/commitlog/index.go>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/server/replicator.go>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/.github/workflows/test.yml>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/documentation/performance-bottleneck-analysis.md>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/documentation/feature_comparison.md>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/documentation/faq.md>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/documentation/overview.md>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/documentation/concepts.md>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/documentation/replication_protocol.md>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/documentation/ha_and_consistency_configuration.md>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/documentation/embedded_nats.md>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/documentation/clients.md>
  - <https://github.com/liftbridge-io/liftbridge/blob/master/documentation/roadmap.md>
  - <https://github.com/liftbridge-io/liftbridge/commits/master>
  - <https://github.com/liftbridge-io/liftbridge/releases>
  - <https://github.com/liftbridge-io/liftbridge/releases/tag/v26.01.1>
  - <https://github.com/liftbridge-io/liftbridge/issues>
  - <https://github.com/liftbridge-io/liftbridge/issues/470>
  - <https://github.com/liftbridge-io/liftbridge/issues/468>
  - <https://github.com/liftbridge-io/liftbridge/issues/437>
  - <https://github.com/liftbridge-io/liftbridge/issues/406>
  - <https://github.com/liftbridge-io/liftbridge/issues/377>
  - <https://github.com/liftbridge-io/liftbridge/issues/321>
  - <https://github.com/liftbridge-io/liftbridge/pull/471>
  - <https://hn.algolia.com/api/v1/search?query=liftbridge&tags=story>
  - <https://news.ycombinator.com/item?id=23010064>
  - <https://news.ycombinator.com/item?id=20560506>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/liftbridge-io/liftbridge`) · [data/wave6/enrich/raw/github_com_liftbridge_io_liftbridge.json](../../../data/wave6/enrich/raw/github_com_liftbridge_io_liftbridge.json) (enrichment confidence 0.75)

</details>
