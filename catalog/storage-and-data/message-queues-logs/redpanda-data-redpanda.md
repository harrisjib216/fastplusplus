# Redpanda

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `BUSL-1.1 (core; converts to Apache-2.0 four years after each release) + Redpanda Community License (enterprise features); GitHub reports no SPDX id` · 🟢 active

> Kafka-API-compatible streaming broker in C++ on Seastar; vendor OMB runs show 12-70x lower p99.99 latency than Kafka.

| | |
|---|---|
| **Beats** | Apache Kafka |
| **Claimed result** | 12x lower p99.99 latency at 50MB/s (164.57ms -&gt; 13.91ms), 23x at 500MB/s (388.66ms -&gt; 16.658ms), 70x at 1GB/s (5509.73ms -&gt; 79.574ms) |
| **Workload** | OpenMessaging-Benchmark-based test at three sustained throughput levels (50 MB/s, 500 MB/s, 1 GB/s) with a 1:1 read/write ratio and 4 partitions/core, comparing p99.99 tail latency on AWS instances |
| **Metric** | latency |
| **Hardware** | AWS: 4x m5n.8xlarge clients (128GB RAM, 32 vCPU, 25Gbps); brokers: i3en.large / is4gen.medium (small, 50MB/s), i3en.3xlarge (medium, 500MB/s), i3en.6xlarge (large, 1GB/s); 3 Redpanda nodes in all tiers vs 3/4/6 Kafka nodes; CPU model not stated |
| **Adoption** | 12.6k stars |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/redpanda-data/redpanda) · [benchmark](https://redpanda.com/blog/redpanda-vs-kafka-performance-benchmark) |

## Verdict

Redpanda's own 2022 OpenMessaging Benchmark (v22.2.2 vs Kafka 3.2.0, TLS+SASL-SCRAM, 1:1 read/write, 4 partitions per core, i3en brokers, 4x m5n.8xlarge clients, no CPU model or build/JVM flags given) measured p99.99 latency of 13.9 / 16.7 / 79.6 ms vs Kafka's 164.6 / 388.7 / 5509.7 ms at 50 MB/s, 500 MB/s and 1 GB/s. Kafka had 3/4/6 brokers against Redpanda's 3, ran on Java 11, and was set to fsync every batch (log.flush.interval.messages=1). A 2023 vendor rerun against Kafka 3.4 KRaft showed a similar pattern (p99.9 24.4 ms vs 98.0 ms on i3en.6xlarge, 3 vs 6+3 nodes). Confluent's Jack Vanlightly repeated the test on 3x i3en.6xlarge with Kafka at default durability and Java 17 and could not reproduce the gap, so treat 12-70x as a vendor best case.

## Use it when

- You already use Kafka clients and need low p99.9/p99.99 produce-to-consume latency with acks=all and fsync before ack (Redpanda's production default), on dedicated Linux hosts with local NVMe.
- Moderate partition counts with well-batched producers, where you want fewer brokers and no JVM/GC tuning. The vendor ran 50 MB/s to 1 GB/s on 3 i3en brokers against 3-6 Kafka brokers.
- You want one binary with built-in consensus (Raft; no ZooKeeper or KRaft controller quorum), plus schema registry, HTTP proxy and tiered storage, on x86-64 or Arm64 (the vendor claims about 2x the 50 MB/s workload on Arm is4gen.medium).
- Local development and CI against the Kafka API: `rpk container start` brings up a local cluster via Docker (dev mode, not durable).

## Skip it when

- You would offer it to third parties as a hosted streaming or queuing service. BSL 1.1 forbids that until each release's change date (4 years), and enterprise features need an RCL license.
- Many producers, many partitions, small batches or keyed records. Vanlightly's independent re-run saw about 24 s end-to-end latency with 50 producers, a cap near 330 MB/s with record keys (288 partitions, 100 producers) while Kafka reached the 500 MB/s target, and consumer backlogs that never drained under 800 MB/s-1 GB/s produce load. He attributes this to small 16 KB fsync'd writes across many partitions (about 200K fsyncs/s).
- Long sustained runs or disks sitting at their retention limit: the same re-run measured p99 3.5 s and p99.99 up to 26 s after about 12 h, with step increases once retention kicked in. With acks=1 at NVMe saturation, Kafka reached 1900 MB/s against Redpanda's 1400 MB/s.
- Shared or containerised hosts, macOS/Windows production, NFS or IPv6-only networks. It needs Linux (RHEL 8+/Ubuntu 20.04+, kernel 4.19+ recommended), x86-64 Westmere+ or aarch64, XFS/ext4 on local SSD, IPv4, and at least 2 GB RAM per core plus 2 MB per partition replica. Thread-per-core assumes it owns its cores.
- You depend on Kafka request-rate quotas (request_percentage), KIP-890 server-side transaction defense, or several SCRAM mechanisms per user.

## How it is fast

It uses a thread-per-core, shared-nothing design built on Redpanda's fork of the Seastar framework. There is one pinned reactor thread per core, memory is allocated up front and split per core, cores talk by message passing instead of locks, and all I/O runs as futures/coroutines rather than OS-scheduled threads. The storage layer skips the Linux page cache: segment_appender batches data into page-aligned chunks and issues Seastar dma_write calls with adaptive fallocate, and reads come from a per-shard LRU batch_cache that Seastar's memory reclaimer can shrink. There is no JVM, so no GC pauses (the vendor's stated cause of Kafka's tail latency). The build has Clang ThinLTO and PGO configurations.

## Compared with alternatives

Pick Redpanda over FluxMQ (a Rust Kafka-compatible broker claiming 20 implemented Kafka APIs, 8 stars) when you need a production-grade Kafka-protocol broker with Raft replication, tiered storage and years of regular releases. Pick it over Woodpecker (an embedded Go WAL on object storage with its own API, no topics or consumer groups) or Zenoh (a different pub/sub protocol) when your applications must keep speaking the Kafka API.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (deb/rpm/tar.gz/Docker, amd64 and arm64), not a linkable library; built from source with Bazel |
| **Dependencies** | Nothing to install at runtime on Linux (Docker needed on macOS). Source build pins everything hermetically via Bazel: a Redpanda fork of Seastar, Boost, Abseil, fmt, protobuf, OpenSSL (+FIPS variant), liburing, lz4/zstd/snappy/zlib, c-ares, hwloc, re2, yaml-cpp, krb5, Avro, rapidjson, HdrHistogram and others, plus Go for rpk and Rust for some components. |
| **Minimum toolchain** | C++23 with Clang + libc++ (hermetic LLVM 23.1.0-rc2 from Redpanda's llvm-project fork via toolchains_llvm), Bazel via bazelisk; Go and Rust toolchains are fetched by Bazel |
| **Platforms** | Linux x86-64 (Westmere or newer) and aarch64; RHEL/CentOS 8+ or Ubuntu 20.04+; XFS or ext4 on local SSD/NVMe (NFS unsupported); IPv4 required; macOS only as rpk + Docker for development; Windows not supported |
| **Thread safety** | Not applicable to users (it is a server). Internally it is shared-nothing: one reactor thread per core, and cross-core work goes through message passing. Client-side thread safety is whatever your Kafka client library documents. |
| **Drop-in for the baseline** | partial — wire-compatible with Kafka clients, so producer/consumer code works unchanged, but the broker is a different server: its own config keys and rpk tooling instead of kafka-\*.sh, Raft instead of ISR, different fsync semantics, and a few Kafka features unsupported (request_percentage quotas, server-side KIP-890, multiple SCRAM mechanisms per user, topic/ACL CRUD via HTTP proxy) |

## Gotchas

- Development mode (the default for rpk container/dev setups) skips fsync, runs --overprovisioned and turns off the tuners. rpk's own help says this gives 'unrealistically fast clusters and may result in data loss', so only benchmark in production mode after `rpk redpanda tune`.
- write.caching / write_caching_default turns acks=all into 'acked by a majority in memory, fsync later' (flush.ms/flush.bytes), which is roughly Kafka's default durability. It is on by default in dev mode, off in production, and never applies to transactions or consumer offsets. Check which mode any comparison used.
- Seastar's per-core heap fragments. The project's own guide says contiguous allocations over 128 KiB after startup can fail even when plenty of memory is free, and 'oversized allocation' bugs keep appearing (e.g. #22737, #18325). Memory is budgeted per core and per partition, so size RAM to cores × partitions.
- Licensing is split: the core is BSL-1.1 (becomes Apache-2.0 four years after each release) and enterprise features are under the Redpanda Community License. GitHub reports no SPDX id, so automated license scanners may flag it.

## Known shortcomings

- Vendor benchmark; Confluent's 2023 re-run (Vanlightly) disputes it. Kafka ran on 4-6 nodes vs Redpanda's 3 in the vendor setup. BUSL-1.1 plus Redpanda Community License (not OSI).
- The 70x is the vendor's best case (Kafka forced to fsync per batch, Java 11, more nodes); Vanlightly's re-run did not reproduce it. Degrades under load in that re-run: 50 producers \~24 s end-to-end, keyed \~330 MB/s vs Kafka 500, 12 h p99.99 of 26 s, backlogs that never drain. BSL-1.1 forbids offering it as a hosted streaming service. Linux only, takes over cores, needs \~2 GB RAM per core; dev mode skips fsync. Kafka wire-compatible but missing request_percentage quotas, server-side KIP-890 and multiple SCRAM credentials per user.

## Caveats and trade-offs

First-party vendor benchmark (Redpanda v22.2.2 vs Kafka v3.2.0, TLS+SASL-SCRAM, 'maximum data safety' configs). Kafka got more nodes than Redpanda in the medium (4 vs 3) and large (6 vs 3) runs. The modified OpenMessaging Benchmark fork is public (github.com/redpanda-data/openmessaging-benchmark; the page links its PR #37), but compiler/JVM flags and CPU models are not stated. Independent rebuttal: Jack Vanlightly (Confluent), 'Kafka vs Redpanda Performance - Do the claims add up?' (2023-05-15), re-ran it with his own OMB fork (github.com/Vanlightly/openmessaging-benchmark-custom) on 3x i3en.6xlarge. He found Kafka misconfigured (log.flush.interval.messages=1 forcing fsync per batch, Java 11), could not get Redpanda to 1000 MB/s with TLS, and saw Redpanda degrade with 50 producers (end-to-end latency up to \~24 s), after \~12 h sustained load (p99.99 \~26 s), with record keys (capped \~330 MB/s vs Kafka 500 MB/s) and at retention limits. He concludes the claims are 'greatly exaggerated'. Treat the 70x as a vendor claim.

Business Source License restricts running Redpanda as a competing hosted service (source-available, not OSI-approved); benchmark hardware given as AWS instance families rather than exact CPU model

## Maintenance

Very active (v26.2.2 and v26.1.17 released August 2026, 12.6k stars, 525 open issues) and shipped as prebuilt packages, so you deploy it as a server rather than vendor the code; read the BSL terms before offering it as a service.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Vendor blog (Tristan Stevens, 2022-10-13) has a summary table with exactly the claimed Kafka vs Redpanda p99.99 numbers (12x/23x/70x). The modified OMB harness is public (redpanda-data/openmessaging-benchmark, linked via PR #37), but the page gives no build/JVM flags or CPU model (only AWS instance types), so this is first-party C, not A.
- **Verifier notes:** The numbers match the page exactly, and the metadata checks out (12,573 stars, last commit 2026-08-20, not archived, not a fork). The Confluent/Vanlightly 2023 independent re-run disputes the claim and is recorded in caveats; the tier stays C.
- **Fields the verifier corrected:** `caveats`, `license`, `hardware`
- **Pages the verifier opened:**
  - <https://redpanda.com/blog/redpanda-vs-kafka-performance-benchmark>
  - <https://github.com/redpanda-data/redpanda>
  - <https://github.com/redpanda-data/redpanda/tree/dev/licenses>
  - <https://github.com/redpanda-data/openmessaging-benchmark>
  - <https://github.com/redpanda-data/openmessaging-benchmark/pull/37>
  - <https://jack-vanlightly.com/blog/2023/5/15/kafka-vs-redpanda-performance-do-the-claims-add-up>
- **Sources the enricher read:**
  - <https://github.com/redpanda-data/redpanda>
  - <https://github.com/redpanda-data/redpanda/blob/dev/CLAUDE.md>
  - <https://github.com/redpanda-data/redpanda/blob/dev/src/v/README.md>
  - <https://github.com/redpanda-data/redpanda/blob/dev/MODULE.bazel>
  - <https://github.com/redpanda-data/redpanda/blob/dev/.bazelrc>
  - <https://github.com/redpanda-data/redpanda/blob/dev/bazel/repositories.bzl>
  - <https://github.com/redpanda-data/redpanda/blob/dev/licenses/README.md>
  - <https://github.com/redpanda-data/redpanda/blob/dev/licenses/bsl.md>
  - <https://github.com/redpanda-data/redpanda/blob/dev/docs/writing-scalable-and-high-performance-code.md>
  - <https://github.com/redpanda-data/redpanda/blob/dev/src/v/storage/segment_appender.h>
  - <https://github.com/redpanda-data/redpanda/blob/dev/src/v/storage/segment_appender_chunk.h>
  - <https://github.com/redpanda-data/redpanda/blob/dev/src/v/storage/batch_cache.h>
  - <https://github.com/redpanda-data/redpanda/blob/dev/src/go/rpk/pkg/cli/redpanda/mode.go>
  - <https://github.com/redpanda-data/redpanda/blob/dev/src/go/rpk/pkg/config/config.go>
  - <https://github.com/redpanda-data/redpanda/issues/13824>
  - <https://github.com/redpanda-data/redpanda/issues?q=oversized+allocation>
  - <https://github.com/redpanda-data/redpanda/issues?q=label%3Aperformance+is%3Aopen>
  - <https://github.com/redpanda-data/redpanda/security-advisories>
  - <https://github.com/redpanda-data/redpanda/releases>
  - <https://redpanda.com/blog/redpanda-vs-kafka-performance-benchmark>
  - <https://redpanda.com/blog/kafka-kraft-vs-redpanda-performance-2023>
  - <https://jack-vanlightly.com/blog/2023/5/15/kafka-vs-redpanda-performance-do-the-claims-add-up>
  - <https://docs.redpanda.com/current/develop/kafka-clients/>
  - <https://docs.redpanda.com/current/deploy/redpanda/manual/production/requirements/>
  - <https://docs.redpanda.com/current/get-started/architecture/>
  - <https://docs.redpanda.com/current/develop/manage-topics/config-topics/>
  - <https://hn.algolia.com/api/v1/search?query=redpanda%20kafka&tags=story>
  - <https://github.com/gosuda/fluxmq>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/redpanda-data/redpanda`) · [data/wave6/enrich/raw/github_com_redpanda_data_redpanda.json](../../../data/wave6/enrich/raw/github_com_redpanda_data_redpanda.json) (enrichment confidence 0.8)

</details>
