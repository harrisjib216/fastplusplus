# AutoMQ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟢 active

> Kafka 3.9 fork with S3-backed stateless brokers; beat Kafka's publish latency only with a now-commercial EBS WAL.

| | |
|---|---|
| **Beats** | Kafka |
| **Claimed result** | At a fixed 500MB/s (128000 msg/s x 4KB, 1000 partitions): pub latency avg 3.4ms vs Kafka 4.2ms and P99 15.19ms vs 30.21ms (2024-06-13 run). Later 500MB/s runs gave P99 15.69 vs 37.65ms and 14.6 vs 40.48ms. At \~100MB/s (25600 msg/s): avg/P99 8.08/30.62ms vs Kafka 17.98/75.13ms (2024-06-24) and 6.81/25.36ms vs 12.3/72.54ms (2024-07-08). E2E latency was mixed: in the 2024-06-13 run Kafka had lower E2E avg (6.31 vs 6.54ms) and P95 (12.39 vs 15.91ms), while AutoMQ had lower E2E P99 (34.16 vs 42.31ms). In two 1-minute smoke runs at producerRate 100, AutoMQ had higher avg pub latency (3.05 vs 2.54ms, 2.71 vs 2.28ms). The fixed producerRate pinned throughput equal. Estimated total cost at 500MB/s was \$2373.35 for AutoMQ vs \$10647.35 for Kafka. |
| **Workload** | OpenMessaging-benchmark-style 1-topic/1000-partitions/4KB messages at fixed producer rates (128000 msg/s and 25600 msg/s) run repeatedly in CI against AutoMQ, Apache Kafka, and AWS MSK clusters on identical topic/producer/consumer configs. |
| **Metric** | latency |
| **Hardware** | AWS EC2 via the repo's driver-\*/deploy/aws-cn Terraform. The issue never states instance types per run, and var.tfvars changed during the run series (2024-06-12 'use free tier', 2024-06-20 'use small size'; currently r6i.large). replicationFactor was 1 for AutoMQ and 3 for Kafka. |
| **Adoption** | 10.9k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/AutoMQ/automq) · [benchmark](https://github.com/AutoMQ/kafka-provider-comparison/issues/1) |

## Verdict

AutoMQ's own OpenMessaging Benchmark fork, run by GitHub Actions in June and July 2024, compared AutoMQ (replication factor 1, gp3 EBS WAL plus S3) with Apache Kafka (RF 3, flush.messages=1, acks=all) at fixed rates of 128,000 and 25,600 msg/s of 4 KB messages over 1,000 partitions. The EC2 instance type is not stated per run; the rig's tfvars now say r6i.large. AutoMQ's publish P99 was 14.6-15.7 ms vs Kafka's 30-40 ms at \~500 MB/s, and 25-31 ms vs 70-75 ms at \~100 MB/s. Throughput was equal by design, E2E latency was mixed, and this is a JVM build with no compiler flags involved.

## Use it when

- Kafka on AWS or GCP where EBS, cross-AZ replication traffic and over-provisioning dominate the bill, and produce latency of hundreds of milliseconds (open-source S3 WAL) is acceptable.
- Bursty or fast-growing throughput where you want to add or remove brokers in seconds without copying partition data.
- Log, telemetry or CDC pipelines with long retention, where object storage makes retained capacity effectively unbounded and cheap.
- Teams that want the actual Kafka codebase and ecosystem (stock clients, Kafka Connect, KRaft) rather than a protocol reimplementation.
- Kafka feeding a lakehouse: Table Topic writes topics out as Apache Iceberg tables through AWS Glue, HMS, REST catalogs or S3 Tables.

## Skip it when

- Latency-sensitive produce paths on the open-source build. Since 1.5.0 only the S3 WAL exists, and AutoMQ's docs describe its latency as 'hundred-millisecond'. AutoMQ's own S3-WAL benchmark reports 472 ms average and 823 ms P99 produce latency at 1 GiB/s. The EBS and NFS WALs behind the \~15 ms P99 result are commercial-only.
- Self-hosted setups without a fast S3-compatible store. After the block WAL was removed, a user running 1.6.0 on local MinIO reported more than 100x degradation and about 7 s average producer latency with 4 KB records (issue #3037).
- Anything that needs Kafka 4.x features or operators such as Strimzi 1.x. AutoMQ is still on the Kafka 3.9 kernel, and issue #2950 has had no committed 4.x timeline since October 2025.
- Small latency-critical clusters on local NVMe, where Redpanda or plain Kafka fit better. The README calls production deployment 'challenging' and points to paid support.
- Large metadata scale without your own testing. A 1.7.1 user with about 5,000 topics hit recurring controller crashes from S3 object-cleanup retries (issue #3477, closed as probably fixed by #3369).

## How it is fast

Produce requests are acknowledged once they reach the WAL. Data is then batched and uploaded to object storage asynchronously. Fresh reads come from an in-memory LogCache, and older data comes from a prefetching BlockCache. Durability comes from shared storage instead of Kafka's 3-way ISR replication, which removes the follower-replication round trip from acks=all produces. In the benchmarked 2024 builds the WAL was a 10 GB gp3 EBS raw device written with Direct IO. Since 1.5.0 the only open-source WAL is S3 itself, with default batches of 8 MiB or 250 ms, which gives up that latency in exchange for zero local state.

## Compared with alternatives

Pick AutoMQ over Redpanda or Apache Pulsar when you want to keep the Apache Kafka codebase and protocol unchanged while cutting cloud storage and replication cost and scaling brokers without moving data. Pick Redpanda when low produce tail latency on local disks is the requirement, because open-source AutoMQ now writes its WAL to S3 at hundred-millisecond latency.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | S3-compatible object storage (AWS S3, MinIO, etc.) for both WAL and data; a KRaft controller quorum (no ZooKeeper); bundled AWS SDK v2, Netty, OpenTelemetry and Iceberg (for Table Topic). |
| **Minimum toolchain** | Java 17 (build.gradle minJavaVersion = 17); Kafka 3.9.0 codebase with Scala 2.13 |
| **Platforms** | Linux JVM, via tarball, Docker images or Kubernetes (Strimzi-based deployments appear in issues). Runs on x86-64 (the comparison rig used r6i) and arm64 (AutoMQ's S3-WAL benchmark used m7g). |
| **Thread safety** | Not applicable (network server); clients are stock Kafka clients with their usual thread-safety rules |
| **Drop-in for the baseline** | partial — it uses Kafka's wire protocol and codebase, so stock clients and Connect work. But it needs S3-compatible storage, replication factor no longer means broker copies, it lags upstream (3.9 kernel, no 4.x), and the low-latency WAL options are commercial-only. |

## Gotchas

- The catalogued latency numbers came from 2024 builds whose WAL was a 10 GB gp3 EBS raw device (s3.wal.path pointed at the EBS NVMe device). PR #2516 (May 2025, 'remove ebs wal') deleted BlockWALService from open source, and DefaultWalFactory now throws 'Unsupported WAL protocol' for anything except s3.
- The license changed between the benchmark and today. In 2024 the S3Stream storage engine was under a revised Business Source License. The repo became Apache-2.0 only in April 2025 (PR #2433), in the same release (1.5.0) that dropped the EBS WAL.
- S3-WAL throughput depends heavily on client batching. Maintainers answer slow S3-WAL reports by pointing to client batch.size and linger.ms tuning, and the README's own perf-test example uses linger.ms=100 and batch.size=524288.
- The docs promise to track upstream Kafka 'within T+1 month', but the 4.x upgrade has been blocked since October 2025 over dropped old-client compatibility.

## Known shortcomings

- Vendor benchmark: end-to-end results are mixed, low-rate smoke runs are slower, Kafka was handicapped with flush.messages=1, and replication factor was 1 vs 3. AutoMQ is a fork of Apache Kafka.
- NOT REPRODUCIBLE WITH CURRENT OSS: the latency win came from the 2024 EBS WAL, which PR #2516 (2025-05) removed from the open-source build; OSS is now S3-WAL only (docs say 'hundred-millisecond'; its own S3-WAL bench shows 472 ms average / 823 ms P99 produce), and EBS/NFS WAL are commercial-only. The benchmark-era S3Stream was under a revised BSL (Apache-2.0 only since 2025-04).
- Stuck on the Kafka 3.9 kernel (no 4.x, #2950); a MinIO S3-WAL user saw &gt;100x slowdown (#3037); controller crash at \~5k topics (#3477).

## Caveats and trade-offs

The benchmark repo (AutoMQ/kafka-provider-comparison, an OMB fork) is AutoMQ-authored, and its last commit was 2024-07-12. It is abandoned as a comparison tool even though AutoMQ itself is active. The instance or CPU model is not stated and changed during the run series. The shared topic config sets flush.messages=1 (fsync per message, a non-default setting that penalizes Kafka's latency), and replication is asymmetric (AutoMQ RF=1 on shared storage vs Kafka RF=3). Throughput was capped by producerRate, so this is a latency/cost claim, not a throughput-speedup claim, and E2E results were mixed. AutoMQ is a source fork of Apache Kafka, so the baseline is its own upstream.

AutoMQ is a diskless Kafka-protocol-compatible broker backed by S3; lower replication factor (1 vs Kafka's 3) reduces write durability model even though data lands on S3; results are self-reported CI runs by the AutoMQ team, not run by a neutral third party.

## Maintenance

AutoMQ is actively released (1.7.5-rc1 on 2026-09-24) and Apache-2.0 since 2025, but the open-source edition is now S3-WAL-only and the benchmark repo has been idle since July 2024, so today's open-source code cannot reproduce the catalogued latency win.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The numbers are CI-bot reports (github-actions, 2024-06-13 to 2024-07-08) in AutoMQ's own OMB fork (AutoMQ/kafka-provider-comparison: workflow_scripts/, driver-automq, driver-kafka, .github/workflows/prepare-vs-benchmark.yml). The code is public, but the issue never states instance or CPU model, so these are first-party numbers with partial methodology: C.
- **Verifier notes:** The claimed pub-latency and cost numbers match the bot comments on issue #1 exactly. I added the mixed E2E and low-rate results and the flush.messages=1 config, which likely handicaps Kafka. The README says 'AutoMQ is a fork of the open-source Apache Kafka', so I set is_fork_of (it is not a GitHub fork). The rest of the metadata checks out: Apache-2.0, 10872 stars, last commit 2026-09-24.
- **Fields the verifier corrected:** `claimed_speedup`, `is_fork_of`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/AutoMQ/kafka-provider-comparison/issues/1>
  - <https://github.com/AutoMQ/kafka-provider-comparison>
  - <https://raw.githubusercontent.com/AutoMQ/kafka-provider-comparison/main/driver-automq/deploy/aws-cn/var.tfvars>
  - <https://raw.githubusercontent.com/AutoMQ/kafka-provider-comparison/main/driver-kafka/deploy/aws-cn/var.tfvars>
  - <https://raw.githubusercontent.com/AutoMQ/kafka-provider-comparison/main/.github/workflows/prepare-vs-benchmark.yml>
  - <https://github.com/AutoMQ/automq>
  - <https://raw.githubusercontent.com/AutoMQ/automq/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/AutoMQ/automq>
  - <https://raw.githubusercontent.com/AutoMQ/automq/main/README.md>
  - <https://github.com/AutoMQ/kafka-provider-comparison/issues/1>
  - <https://github.com/AutoMQ/kafka-provider-comparison>
  - <https://github.com/AutoMQ/kafka-provider-comparison/blob/main/driver-automq/deploy/aws-cn/var.tfvars>
  - <https://github.com/AutoMQ/kafka-provider-comparison/blob/main/driver-automq/deploy/aws-cn/templates/server.properties>
  - <https://github.com/AutoMQ/kafka-provider-comparison/blob/main/driver-automq/deploy/aws-cn/templates/broker.properties>
  - <https://github.com/AutoMQ/kafka-provider-comparison/blob/main/driver-automq/deploy/aws-cn/deploy.yaml>
  - <https://github.com/AutoMQ/kafka-provider-comparison/blob/main/driver-automq/deploy/aws-cn/hosts.ini.tpl>
  - <https://github.com/AutoMQ/kafka-provider-comparison/blob/main/driver-kafka/deploy/aws-cn/var.tfvars>
  - <https://github.com/AutoMQ/kafka-provider-comparison/blob/main/.github/workflows/prepare-vs-benchmark.yml>
  - <https://github.com/AutoMQ/kafka-provider-comparison/blob/main/cost-explanation/automq.md>
  - <https://github.com/AutoMQ/kafka-provider-comparison/commits/main>
  - <https://github.com/AutoMQ/automq/blob/main/s3stream/src/main/java/com/automq/stream/s3/wal/WalFactory.java>
  - <https://github.com/AutoMQ/automq/blob/main/core/src/main/scala/kafka/log/stream/s3/wal/DefaultWalFactory.java>
  - <https://github.com/AutoMQ/automq/blob/main/s3stream/src/main/java/com/automq/stream/s3/wal/impl/object/ObjectWALConfig.java>
  - <https://github.com/AutoMQ/automq/blob/main/gradle.properties>
  - <https://github.com/AutoMQ/automq/blob/main/build.gradle>
  - <https://github.com/AutoMQ/automq/blob/main/gradle/dependencies.gradle>
  - <https://github.com/AutoMQ/automq/releases>
  - <https://github.com/AutoMQ/automq/pull/2516>
  - <https://github.com/AutoMQ/automq/pull/2433>
  - <https://github.com/AutoMQ/automq/pull/2665>
  - <https://github.com/AutoMQ/automq/pull/2678>
  - <https://github.com/AutoMQ/automq/pull/2681>
  - <https://github.com/AutoMQ/automq/pull/2682>
  - <https://github.com/AutoMQ/automq/commit/4596c26983>
  - <https://github.com/AutoMQ/automq/commit/6056681bd6>
  - <https://github.com/AutoMQ/automq/tree/1.1.0>
  - <https://github.com/AutoMQ/automq/tree/1.4.0>
  - <https://github.com/AutoMQ/automq/tree/1.5.0>
  - <https://github.com/AutoMQ/automq/issues/3037>
  - <https://github.com/AutoMQ/automq/issues/3210>
  - <https://github.com/AutoMQ/automq/issues/2926>
  - <https://github.com/AutoMQ/automq/issues/2950>
  - <https://github.com/AutoMQ/automq/issues/3477>
  - <https://github.com/AutoMQ/automq/issues/2520>
  - <https://docs.automq.com/automq/architecture/s3stream-shared-streaming-storage/wal-storage>
  - <https://docs.automq.com/automq/benchmarks/automq-vs-apache-kafka-benchmarks-and-cost>
  - <https://docs.automq.com/automq/what-is-automq/compatibility-with-apache-kafka>
  - <https://news.ycombinator.com/item?id=39966114>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/automq/automq`) · [data/wave6/enrich/raw/github_com_automq_automq.json](../../../data/wave6/enrich/raw/github_com_automq_automq.json) (enrichment confidence 0.8)

</details>
