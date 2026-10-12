# Woodpecker

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0 (server/ directory dual-licensed AGPL-3.0-only OR SSPL-1.0)` · 🟢 active

> Go WAL library storing append-only logs on S3/object storage or local disk; vendor test shows 3.5-5.8x Kafka single-stream write throughput

| | |
|---|---|
| **Beats** | Apache Kafka |
| **Claimed result** | Local-FS mode: 450 MB/s vs Kafka's 129.96 MB/s (3.5x) and Pulsar's 107 MB/s (4.2x), with 1.8ms vs Kafka's 58ms latency; S3 mode: 750 MB/s (5.8x vs Kafka) |
| **Workload** | Single-node, single-client, single-log-stream write-ahead-log throughput/latency test comparing Woodpecker (local filesystem, S3, and MinIO backends) against Kafka and Pulsar |
| **Metric** | throughput |
| **Adoption** | 95 stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/zilliztech/woodpecker) · [benchmark](https://github.com/milvus-io/milvus-docs/blob/v3.0.x/site/en/reference/architecture/woodpecker_architecture.md) |

## Verdict

One first-party single-node, single-client, single-log-stream write test, published identically in the README, the Milvus docs and a May 2025 Milvus blog post. Woodpecker to local FS: 450 MB/s at 1.8 ms; to S3: 750 MB/s at 166 ms; to MinIO: 71 MB/s at 184 ms. Kafka: 129.96 MB/s at 58 ms; Pulsar: 107 MB/s at 35 ms. No CPU or instance type (only 'single EC2 instance' for the S3 ceiling), message size, batching, Go version, or Kafka/Pulsar settings (acks, fsync, replication) are given, the repo has no Kafka/Pulsar harness, and the numbers come from early-2025 development builds.

## Use it when

- A Go system (vector DB, database, event-sourced service) that needs an ordered, durable WAL and already runs etcd plus S3/MinIO, and you want to stop operating a Kafka or Pulsar cluster for it.
- Bulk single-stream appends to S3 where \~100-200 ms commit latency is fine: the vendor measured 750 MB/s from one client/stream vs 130 MB/s for Kafka.
- Single-node deployments on local disk that want fsync-acknowledged appends at millisecond latency (vendor: 450 MB/s at 1.8 ms).
- Log retention priced at object-storage rates with stateless compute, where catch-up/replay reads can come straight from object storage.
- Multi-AZ durability via the 3-replica quorum service mode (ack after 2 of 3 replicas, async flush to object storage), if you can run the extra LogStore service.

## Skip it when

- You need the Kafka API or ecosystem (wire protocol, partitions, consumer groups, Connect/Streams, transactions): none of it exists here.
- Latency-sensitive writes over object storage: the vendor's own table shows S3/MinIO modes at 166/184 ms vs Kafka 58 ms and Pulsar 35 ms, and the Milvus docs put embedded MemoryBuffer mode at 200-500 ms.
- Self-hosted MinIO backends: the same table has Woodpecker at 71 MB/s, about half of Kafka's 130 MB/s.
- Many concurrent producers into one log: each log has one exclusive writer (etcd session lock or conditional-write fence); in lock mode failover can wait up to the 10 s session TTL.
- Risk-averse production outside Milvus: still v0.1.x, and a quorum-mode bug that lost acknowledged data after compaction (#320) was only fixed in September 2026.

## How it is fast

Group commit: appends land in an in-memory sequential buffer (entries ordered by id, gaps held back) that is flushed when it hits an entry/byte cap or a timer (defaults 200 ms for object storage, 10 ms for local FS, 1 ms in service mode), turning many small writes into large sequential ones. On object storage each flush is cut into \~2 MB blocks uploaded as separate objects in parallel from a goroutine pool (maxFlushThreads, default 32) while acks are still released strictly in entry order; blocks of a sealed segment are later compacted into merged objects (up to segmentCompactionPolicy.maxBytes, default 2 MB). Local-FS mode appends CRC32-framed records to one segment file and fsyncs once per flushed block. Writer fencing uses object-store conditional PUT (If-None-Match) instead of lock round-trips where the backend supports it; the vendor frames the result as reaching 60-80% of each backend's raw bandwidth.

## Compared with alternatives

No siblings catalogued yet. Against the Kafka baseline, pick it only when you want an embeddable Go WAL on object storage rather than a general-purpose broker.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | etcd (required; only metadata backend supported) plus an S3-compatible object store or local filesystem; Go deps include minio-go, Azure SDK, etcd client/server v3.5, gRPC, Prometheus, OpenTelemetry, zap and hashicorp/memberlist (service-mode gossip). Service mode also ships a LogStore server, Docker images, a Kubernetes operator and the wpcli admin tool. |
| **Minimum toolchain** | Go 1.25 (go.mod declares go 1.25.0) |
| **Platforms** | Pure Go; Docker build images target Linux only (Ubuntu 20.04/22.04, Rocky Linux 8, Amazon Linux 2023); other OSes not documented |
| **Thread safety** | Not documented per method. Cluster-wide there is one exclusive LogWriter per log, enforced by an etcd session lock or conditional-write fence; WriteAsync returns a per-message result channel; multiple independent readers per log are supported. |
| **Drop-in for the baseline** | no |

## Gotchas

- License trap: the embedded client (woodpecker/client/logstore_client_local.go) imports the server/ package, which is AGPL-3.0-only or SSPL-1.0, so embedded mode compiles copyleft code into your binary; only the non-server packages are Apache-2.0.
- Writers can be invalidated under you: when the etcd session expires writes fail with ErrLogWriterLockLost and the app must reopen a writer. With fencePolicy 'auto' on a new cluster, startup fails outright if the object store's conditional-write check fails; there is no silent fallback to locks.
- Docs lag code: the README reader example calls OpenLogReader(ctx, start), but the interface is now OpenLogReader(ctx, from, readerBaseName), and the README config shows 4 MB flushes / 64 threads while current defaults are 2 MB / 32.
- Open reader issues: ReadNext keeps serving data after the reader is closed (#277), and an idle tail reader polls etcd plus a quorum-wide RPC every 200 ms (#352).

## Known shortcomings

- Vendor-only single-stream benchmark from early-2025 builds; no hardware, message size or Kafka/Pulsar acks/fsync/replication settings; no Kafka harness in the repo. Not uniformly faster: MinIO mode 71 vs Kafka 130 MB/s; S3/MinIO latency 166/184 ms vs Kafka 58 ms; embedded mode 200-500 ms. Licence trap: the embedded client imports server/ (AGPL-3.0/SSPL), so embedded use links copyleft code. Not a Kafka replacement (own Go API, no Kafka protocol, partitions or consumer groups; one exclusive writer per log; needs etcd; Go 1.25+, Linux only). v0.1.x: quorum-mode bug losing acknowledged data after compaction (#320) fixed only 2026-09; open reader bugs (#277, #352); README drifts from code.

## Caveats and trade-offs

First-party benchmark from the Milvus/Zilliz docs and project README; no CPU/hardware model stated ("our test machine"); Kafka/Pulsar tuning and dataset are undocumented; no public Kafka/Pulsar comparison harness (tests/benchmark/ covers Woodpecker only); single-node/single-stream test, not a distributed cluster comparison. Not uniformly faster: MinIO mode is slower than Kafka (71 MB/s vs 129.96 MB/s) and S3/MinIO modes have higher latency (166 ms / 184 ms vs Kafka 58 ms, Pulsar 35 ms). License is split: Apache-2.0 except server/ which is AGPL-3.0-only OR SSPL-1.0 (GitHub reports NOASSERTION).

Purpose-built as Milvus's write-ahead-log layer rather than a general-purpose broker; local-FS/S3/MinIO modes trade off durability and availability differently; project explicitly describes results as "early stages of development"

## Maintenance

Actively developed (v0.1.45 released 2026-09-21, releases roughly weekly) and shipped as the default WAL in Milvus 2.6+, but still pre-1.0. Client packages are Apache-2.0 and server/ is AGPL-3.0/SSPL, so embedding it in proprietary software needs legal review.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party table (Milvus docs + identical table in the project README) comparing Woodpecker vs Kafka and Pulsar in a single-node/single-client/single-stream write test; no hardware/CPU model, Kafka/Pulsar configs or payload sizes stated, and the repo's tests/benchmark/ suite only exercises Woodpecker itself (no Kafka/Pulsar harness), so C.
- **Verifier notes:** Original benchmark_url on milvus-docs master now 404s (file absent on master); same page is live on v3.0.x and v2.6.x branches with identical numbers, and the same table appears in the Woodpecker README '🏎 Benchmarks' section. All claimed figures (450 vs 129.96 MB/s = 3.5x, 4.2x vs Pulsar 107 MB/s, 1.8 ms vs 58 ms, S3 750 MB/s = 5.8x) are stated verbatim on the page; metadata (95 stars, last commit 2026-09-24, not fork/archived) checked and correct; usability kept copyable since every part is under an OSI license option (Apache-2.0 / AGPL-3.0).
- **Fields the verifier corrected:** `benchmark_url`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/milvus-io/milvus-docs/blob/master/site/en/reference/architecture/woodpecker_architecture.md>
  - <https://raw.githubusercontent.com/milvus-io/milvus-docs/master/site/en/reference/architecture/woodpecker_architecture.md>
  - <https://raw.githubusercontent.com/milvus-io/milvus-docs/v3.0.x/site/en/reference/architecture/woodpecker_architecture.md>
  - <https://raw.githubusercontent.com/milvus-io/milvus-docs/v2.6.x/site/en/reference/architecture/woodpecker_architecture.md>
  - <https://github.com/milvus-io/milvus-docs/blob/v3.0.x/site/en/reference/architecture/woodpecker_architecture.md>
  - <https://github.com/zilliztech/woodpecker>
  - <https://github.com/zilliztech/woodpecker/blob/master/README.md>
  - <https://github.com/zilliztech/woodpecker/blob/master/LICENSE.txt>
  - <https://github.com/zilliztech/woodpecker/blob/master/tests/benchmark/README.md>
- **Sources the enricher read:**
  - <https://github.com/zilliztech/woodpecker>
  - <https://github.com/zilliztech/woodpecker/blob/master/README.md>
  - <https://github.com/zilliztech/woodpecker/blob/master/LICENSE.txt>
  - <https://github.com/zilliztech/woodpecker/blob/master/go.mod>
  - <https://github.com/zilliztech/woodpecker/blob/master/config/woodpecker.yaml>
  - <https://github.com/zilliztech/woodpecker/blob/master/server/README.md>
  - <https://github.com/zilliztech/woodpecker/blob/master/server/storage/codec/README.md>
  - <https://github.com/zilliztech/woodpecker/blob/master/server/storage/objectstorage/writer_impl.go>
  - <https://github.com/zilliztech/woodpecker/blob/master/server/storage/disk/writer_impl.go>
  - <https://github.com/zilliztech/woodpecker/blob/master/tests/benchmark/README.md>
  - <https://github.com/zilliztech/woodpecker/blob/master/docs/condition_write.md>
  - <https://github.com/zilliztech/woodpecker/blob/master/woodpecker/README.md>
  - <https://github.com/zilliztech/woodpecker/blob/master/woodpecker/woodpecker_embed_client.go>
  - <https://github.com/zilliztech/woodpecker/blob/master/woodpecker/client/logstore_client_local.go>
  - <https://github.com/zilliztech/woodpecker/blob/master/woodpecker/log/log_writer.go>
  - <https://github.com/zilliztech/woodpecker/blob/master/woodpecker/log/log_handle.go>
  - <https://github.com/zilliztech/woodpecker/releases>
  - <https://github.com/zilliztech/woodpecker/issues>
  - <https://github.com/zilliztech/woodpecker/issues/320>
  - <https://github.com/zilliztech/woodpecker/issues/277>
  - <https://raw.githubusercontent.com/milvus-io/milvus-docs/v3.0.x/site/en/reference/architecture/woodpecker_architecture.md>
  - <https://milvus.io/blog/we-replaced-kafka-pulsar-with-a-woodpecker-for-milvus.md>
  - <https://github.com/milvus-io/community/blob/master/blog/en/we-replaced-kafka-pulsar-with-a-woodpecker-for-milvus.md>
  - <https://hn.algolia.com/api/v1/search?query=woodpecker%20WAL>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/zilliztech/woodpecker`) · [data/wave6/enrich/raw/github_com_zilliztech_woodpecker.json](../../../data/wave6/enrich/raw/github_com_zilliztech_woodpecker.json) (enrichment confidence 0.4)

</details>
