# Apache Pulsar

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Multi-tenant pub-sub broker on BookKeeper; vendor benchmark beats Kafka throughput, but the 100-partition win needs journaling off.

| | |
|---|---|
| **Beats** | Kafka |
| **Claimed result** | Max throughput at 100 partitions: Pulsar without journaling 1600MB/s vs Kafka 1087MB/s (\~1.47x, derived from page data). Default Pulsar with journaling reached 800MB/s, which is below Kafka. Single partition: Pulsar 700MB/s without journal / 580MB/s with journal vs Kafka 280MB/s (\~2.5x, derived from page data); the page headlines this as '2.5x maximum throughput'. P99 publish latency at a fixed 500MB/s: Pulsar without journal 1.58ms, with journal 7.89ms, vs Kafka 3.46ms. Kafka's P99.9 was 54.56ms, and the page says both Pulsar configs beat Kafka at P99.9 and above, headlining '100x lower than Kafka at P99.99'. Catch-up reads from a 512GB backlog: Pulsar up to 3.2GB/s vs Kafka 2.0GB/s ('60% more'; headline '1.5x faster historical read rate'). Pulsar drained the backlog \~2.5x faster, while Kafka producers' P99 rose to \~700ms. |
| **Workload** | Linux Foundation OpenMessaging Benchmark with 1KB messages on 3 broker VMs (i3en.6xlarge) and 4 client VMs (m5n.8xlarge) on AWS. Tests: max throughput with 1 and 100 partitions, publish latency at a fixed 500MB/s on 100 partitions, and catch-up read throughput draining a 512GB backlog while producers keep writing. |
| **Metric** | throughput |
| **Hardware** | 3x i3en.6xlarge brokers (24-core, 192GB RAM, 25Gbps, dual NVMe SSD), 4x m5n.8xlarge clients (32-core, 128GB RAM, 25Gbps), t2.small ZooKeeper nodes |
| **Adoption** | 15.3k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/apache/pulsar) · [benchmark](https://streamnative.io/blog/apache-pulsar-vs-apache-kafka-2022-benchmark) |

## Verdict

StreamNative's 2022 OpenMessaging Benchmark (Pulsar 2.9.1 vs Kafka 3.0.0, 1KB messages, 3x i3en.6xlarge brokers with dual NVMe, 4x m5n.8xlarge clients, ZGC on both, Kafka RF3/min-ISR 2/acks=all vs Pulsar 3/3/2) measured no-journal Pulsar at 1600MB/s vs Kafka's 1087MB/s on 100 partitions (\~1.47x), and 700 vs 280MB/s on one partition (\~2.5x). Default journaled Pulsar lost the 100-partition test (800MB/s) and P99 at 500MB/s (7.89 vs 3.46ms), but won at P99.9 and above and on catch-up reads (\~3.2 vs \~2.0GB/s).

## Use it when

- Consumers regularly replay backlogs larger than RAM while producers keep writing, and publish latency must stay flat. In the vendor run Pulsar read at \~3.2GB/s vs Kafka's \~2.0GB/s, while Kafka producers' P99 rose to \~700ms.
- Hot single partitions: in the same run one partition sustained 580MB/s (journaled) or 700MB/s (no journal) vs Kafka's 280MB/s.
- Tail-latency-sensitive publishing at moderate load, where P99.9 and above matter more than P99. Kafka's P99.9 at 500MB/s was 54.56ms, and both Pulsar configs were lower.
- Shared platforms that need multi-tenancy, quotas, auth, geo-replication and tiered offload of old ledgers to object storage in one system.
- Applications that mix queue-style work distribution (shared/key-shared subscriptions, delayed delivery, DLQ) with ordered streaming.

## Skip it when

- You need fsync-before-ack durability and peak throughput at the same time. Default journaled Pulsar reached 800MB/s vs Kafka's 1087MB/s at 100 partitions, with higher P99 at 500MB/s (7.89 vs 3.46ms).
- Small ops teams: a production cluster has three separately scaled tiers (brokers, bookies, metadata store), each needing JVM heap and direct-memory tuning. Standalone mode is for development.
- You depend on the Kafka ecosystem (Kafka clients, Streams, Connect). Pulsar's protocol is different, and the open-source Kafka-on-Pulsar handler (streamnative/kop) is archived.
- You want independent performance evidence. The 2022 result is vendor-run, and Confluent's 2020 OMB run on smaller i3en.2xlarge nodes found the reverse: Kafka 605MB/s vs Pulsar 305MB/s peak, and 5 vs 25ms P99, with Pulsar capped by a saturated journal disk.

## How it is fast

Each topic is a managed ledger, a chain of BookKeeper ledgers written with quorum replication. The benchmark used ensemble 3, write quorum 3 and ack quorum 2, so a producer ack skips the slowest replica, while Kafka with acks=all waits on the in-sync replicas. Bookies interleave entries from many ledgers into sequential entry logs, index them in RocksDB (DbLedgerStorage) and keep their own write and read-ahead caches instead of relying on the OS page cache. The vendor credits these caches and separate disks for keeping catch-up reads from stalling producers. With journaling on, writes are group-committed to a journal on a dedicated disk. Producers batch by a max delay (1ms in the benchmark) rather than waiting on batch size.

## Compared with alternatives

Pick Pulsar over Redpanda or AutoMQ when you want multi-tenancy, queue-style subscriptions and BookKeeper's quorum storage under Apache governance, and can move clients to Pulsar's API. Pick those two when existing Kafka clients must work unchanged. Pick it over Woodpecker (an embedded WAL whose own benchmark put Pulsar at 107MB/s) when you need a full broker with topics and subscriptions.

## Integration

| | |
|---|---|
| **Form** | standalone multi-tier server (broker + BookKeeper bookies + metadata store) shipped as a tarball, Docker images and a Helm chart; the Java client is a published Maven module |
| **Dependencies** | Apache BookKeeper 4.18.1 (bookies run as their own service), a metadata store (ZooKeeper 3.9.5, Oxia, etcd or RocksDB), Netty 4.2, RocksDB 9.9 (bookie index), Jetty 12, protobuf/lightproto, Caffeine |
| **Minimum toolchain** | Broker needs Java 21 on Pulsar 4.x; Java 25 is recommended for 5.0+. The Java client needs Java 17 or 21 from 4.1 (8/11/17/21 on 3.3-4.0). Building master needs JDK 21, 25 or 26 with the Gradle wrapper; bytecode targets Java 17. |
| **Platforms** | 64-bit Linux and macOS; Windows only through Docker; CPU architecture requirements not documented |
| **Thread safety** | Client side (javadoc): PulsarClient is thread-safe and reusable, one Producer can be shared across threads, and all Consumer operations are thread-safe. Broker side: ARCHITECTURE.md says Pulsar has no clearly documented concurrency model. |
| **Drop-in for the baseline** | no |

## Gotchas

- The 1600MB/s no-journal result uses OMB's bookkeeper-skip-journal.conf (journalWriteData=false, journalSyncData=false). That config also lists the two journal disks as ledger directories (4 instead of 2), so it gets more disk bandwidth as well as weaker durability.
- Direct memory is the usual failure point. Bookie, broker and client 'OutOfMemoryError: Direct buffer memory' reports recur (#19334 still open, #9721), and the Java client's default 64MB memoryLimit is documented as too low for high throughput.
- Futures from sendAsync complete on the client's internal Netty I/O thread, so a slow callback on them stalls network processing for other producers (Producer javadoc).
- Performance shifts between releases. The 4.0 shared-subscription rewrite (PIP-379) added \~15% end-to-end latency until the classic-implementation flags were set (#24490), and &gt;200ms publish spikes in long 2.11 OMB runs are still open (#15792).

## Known shortcomings

- Vendor (StreamNative) 2022 benchmark with Pulsar 2.9.1 vs Kafka 3.0.0. The aggregate win is \~1.47x (1600 vs 1087 MB/s); the 2.5x headline is a single partition (700 vs 280). Default journaled Pulsar loses to Kafka (800 vs 1087 MB/s; P99 7.89 vs 3.46 ms).
- The 100-partition win needs the journal off, and that OMB config also adds the two journal disks as ledger dirs (4 vs 2 disks), so it gains disk bandwidth as well as weaker durability. Confluent's 2020 OMB run shows the opposite (Kafka 605 vs Pulsar 305 MB/s). Not Kafka-wire compatible (the OSS KoP handler is archived).
- Recurring direct-memory OOM (#19334 open); three-tier operations (broker, bookie, metadata store). Performance shifts between releases (PIP-379 shared-subscription +15% latency #24490; 2.11 &gt;200 ms publish spikes #15792 open). 4.0 LTS active support ends 2026-10-21.

## Caveats and trade-offs

The benchmark was run and published by StreamNative, whose CTO co-created Pulsar, so it is a vendor-interested comparison rather than an independent third party, even though it uses the public OMB suite. It is dated (2022-04-07; Pulsar 2.9.1 vs Kafka 3.0.0). Default Pulsar (journaling, fsync before ack) loses to Kafka on 100-partition max throughput (800 vs 1087MB/s) and on P99 latency (7.89 vs 3.46ms). The 'equivalent durability' wins use the non-default no-journal config, and Kafka used Confluent's OMB-recommended config with no fsync before ack. Hardware is given as AWS instance types, not a CPU model.

Pulsar's 'no journaling' fastest mode trades some durability guarantees; Pulsar has a more complex operational footprint (separate Broker + BookKeeper + ZooKeeper) than Kafka; JVM-based, so no compiler/flags apply.

## Maintenance

Very active Apache-2.0 project: 4.2.4 and 4.0.13 shipped 2026-08-03 and 5.0.0-M2 on 2026-09-16. Active support for the 4.0 LTS ends 21 Oct 2026 (security fixes to Oct 2027), and Pulsar is deployed as a multi-service cluster, not vendored as a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** This is a vendor-run (StreamNative, 2022-04-07) Linux Foundation OpenMessaging Benchmark comparison. The page links the public workload and driver files in github.com/openmessaging/benchmark (workloads/1-topic-100-partitions-1kb-4p-4c-\*.yaml, driver-pulsar/pulsar.yaml, driver-kafka/kafka-\*.yaml), but hardware is given only as AWS instance types with no CPU model. That makes it first-party numbers short of A, so C, which matches how the vendor OMB run for Redpanda was graded in batch-08.
- **Verifier notes:** The record put '\~2.5x' on the 100-partition 1600 vs 1087MB/s pair, which is really \~1.47x. The page's 2.5x headline comes from the single-partition test (700 vs 280MB/s), so I fixed claimed_speedup. I also caught the '3.2GB/s vs 2.0GB/s' catch-up claim, which is on the page. Metadata checks out: Apache-2.0, 15338 stars, last commit 2026-09-26, not archived or a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://streamnative.io/blog/apache-pulsar-vs-apache-kafka-2022-benchmark>
  - <https://github.com/apache/pulsar>
- **Sources the enricher read:**
  - <https://github.com/apache/pulsar>
  - <https://github.com/apache/pulsar/blob/master/ARCHITECTURE.md>
  - <https://github.com/apache/pulsar/blob/master/gradle/libs.versions.toml>
  - <https://github.com/apache/pulsar/releases>
  - <https://github.com/apache/pulsar/blob/master/pulsar-client-api/src/main/java/org/apache/pulsar/client/api/Producer.java>
  - <https://github.com/apache/pulsar/blob/master/pulsar-client-api/src/main/java/org/apache/pulsar/client/api/Consumer.java>
  - <https://github.com/apache/pulsar/blob/master/pulsar-client-api/src/main/java/org/apache/pulsar/client/api/PulsarClient.java>
  - <https://streamnative.io/blog/apache-pulsar-vs-apache-kafka-2022-benchmark>
  - <https://github.com/openmessaging/benchmark/blob/master/driver-pulsar/pulsar.yaml>
  - <https://github.com/openmessaging/benchmark/blob/master/driver-pulsar/deploy/ssd/templates/bookkeeper.conf>
  - <https://github.com/openmessaging/benchmark/blob/master/driver-pulsar/deploy/ssd/templates/bookkeeper-skip-journal.conf>
  - <https://github.com/openmessaging/benchmark/blob/master/driver-kafka/kafka-throughput.yaml>
  - <https://www.confluent.io/blog/kafka-fastest-messaging-system/>
  - <https://pulsar.apache.org/docs/4.2.x/concepts-architecture-overview/>
  - <https://pulsar.apache.org/docs/next/client-libraries-java-setup/>
  - <https://pulsar.apache.org/docs/next/getting-started-standalone/>
  - <https://pulsar.apache.org/contribute/release-policy/>
  - <https://pulsar.apache.org/security/>
  - <https://bookkeeper.apache.org/docs/getting-started/concepts>
  - <https://github.com/streamnative/kop>
  - <https://github.com/apache/pulsar/issues/15792>
  - <https://github.com/apache/pulsar/issues/24490>
  - <https://github.com/apache/pulsar/issues/19334>
  - <https://hn.algolia.com/api/v1/search?query=pulsar%20kafka%20benchmark&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/apache/pulsar`) · [data/wave6/enrich/raw/github_com_apache_pulsar.json](../../../data/wave6/enrich/raw/github_com_apache_pulsar.json) (enrichment confidence 0.7)

</details>
