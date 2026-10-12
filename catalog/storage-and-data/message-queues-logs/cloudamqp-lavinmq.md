# LavinMQ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Crystal` · `Apache-2.0` · 🟢 active

> AMQP 0-9-1/MQTT 3.1.1 broker in Crystal with a very small RAM footprint; one customer replaced managed Kafka with it.

| | |
|---|---|
| **Beats** | Apache Kafka |
| **Claimed result** | Memory usage dropped from 5 GB to under 40 MB in a development instance; message-consuming times decreased 3x, message-publishing times improved 300x versus the prior Kafka integration; daily message volume grew from \~4,000 to 50,000+ after migration |
| **Workload** | Elixir/Broadway messaging platform (DAT Systems, serving LWMC's 16,000+ employees over WhatsApp/Telegram/WeChat). The memory figure comes from a local development install of LavinMQ next to the local Kafka. The 3x/300x figures compare production on a serverless (managed, provider unnamed) Apache Kafka service with CloudAMQP's hosted LavinMQ service. |
| **Metric** | memory |
| **Adoption** | 1,018 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/cloudamqp/lavinmq) · [benchmark](https://lavinmq.com/blog/dat-systems-user-story) |

## Verdict

The only evidence against Kafka is a customer story on the vendor's blog (DAT Systems, 25 Oct 2024, Elixir/Broadway clients). It reports memory falling from 5 GB to under 40 MB on a development instance, consume times 3x lower and publish times 300x better than its earlier integration with an unnamed serverless Kafka service that had 'broker not found' and 'leader missing' errors. No hardware, sizing, Kafka configuration or method is given, so read these numbers as a migration anecdote, not a benchmark.

## Use it when

- You use Kafka as a plain work or event queue at modest volume (the case study ran \~4,000 to 50,000 messages a day) and the JVM broker's memory or operational weight is the main cost.
- You run RabbitMQ-style AMQP 0-9-1 workloads and want the same client libraries with lower RAM: the README lists 35 MB for 1,000 queues and 70 MB for 1,000 connections.
- Queues sometimes build very deep backlogs and you do not want broker RAM to grow with queue depth (messages live in mmap'd segments and the page cache).
- You want one small broker for both IoT MQTT 3.1.1 devices and AMQP backend consumers, or a replayable stream at moderate scale with header, key-value or geo filtering on the server.
- You run on small instances: vendor lavinmqperf runs show \~570k msg/s at 16 B with one producer and one consumer on a t4g.micro (2 vCPU, 1 GiB).

## Skip it when

- You depend on the Kafka API or its ecosystem (Connect, Streams, existing Kafka clients) or on partitioned topics with consumer-group rebalancing. LavinMQ is not wire-compatible.
- You need write throughput spread across nodes. The cluster has a single leader that takes all writes and replicates everything to followers, so adding nodes adds redundancy, not capacity.
- You need AMQP 1.0, MQTT 5 or MQTT QoS 2. QoS 2 publishes are downgraded to QoS 1, and only AMQP 0-9-1 and MQTT 3.1.x are listed.
- You need long-term or tiered log retention. Blob/S3 storage for streams is still an open feature request (#1070), so the log is bounded by local disk.
- You need mature failure handling in clustered mode. Open issues include a leader that never fails over when its disk stalls (#2151) and a stream-replay memory spike that killed a production node (#2226).

## How it is fast

Storage is disk-first. Each queue is a series of 8 MB segment files mapped with mmap (MAP_SHARED). A publish is a memcpy appended to the last segment. Consumers read the segments sequentially. An ack writes a 4-byte position to a per-segment ack file, and a segment is deleted once every message in it is acked. Messages are not cached on the heap: the OS page cache does the caching and madvise(DONTNEED) releases pages, so resident memory stays flat as queues grow (the README says 25 MB of RAM with 100M messages enqueued). Publisher confirms are group-committed: one syncfs(2) call on a dedicated thread flushes every pending confirm in a batch. The code is compiled by LLVM to a native binary and uses a fiber/CSP event loop for I/O.

## Compared with alternatives

Pick LavinMQ over Redpanda, AutoMQ or Fluvio when you are willing to leave the Kafka protocol for AMQP routing (exchanges, DLX, TTL, priority and delayed queues) and want the smallest footprint. Pick it over RabbitMQ when you want the same AMQP 0-9-1 clients with a single-binary, low-RAM broker and can live without AMQP 1.0, MQTT 5 or QoS 2 and with a younger clustering implementation.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (deb/rpm packages, Homebrew, AUR, Docker image cloudamqp/lavinmq) |
| **Dependencies** | Runtime: libssl and liblz4 (per the Dockerfile); etcd for clustering. Build: Crystal plus the shards amqp-client, amq-protocol, systemd, lz4 and mqtt-protocol. |
| **Minimum toolchain** | Crystal 1.21.0 to build from source (shard.yml); prebuilt packages need no toolchain |
| **Platforms** | Linux (x86-64 and arm64; vendor benchmarks run on Graviton), macOS via Homebrew, Windows only through WSL. The syncfs group commit is Linux-only; other OSes fall back to a global sync(). |
| **Thread safety** | Server process that serves concurrent clients on fibers. Parts have been multi-threaded since 2.4.0 (Crystal execution contexts), and the confirm/syncfs loop runs on its own isolated thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Confirm semantics changed in 2.9.0 (2026-06). Confirms now wait for a filesystem-wide syncfs and, in a cluster, for every in-sync follower. Before that, the broker confirmed once the message was in the mmap. The October 2024 case study predates this change, and --no-sync gets the speed back at the cost of durability.
- The mmap-per-segment design has sharp edges: SIGBUS when bursts of writes hit mapped pages right after a disk-full alarm clears (#2180), an open use-after-munmap SIGSEGV when stream retention runs during delivery (#2181), and one CPU core pinned during queue churn on Linux 7.0 to 7.1.8 on arm64 (a kernel bug, #2259).
- Write amplification: page-granular mmap writes plus a syncfs per confirm batch produced 30-200x more disk writes than network bytes received in the reporter's clusters (#2176). This matters on IOPS-billed volumes.
- Requeue and redelivery state lives only in memory. After a restart the redelivered flag and x-delivery-count reset, so a poison message can dodge x-delivery-limit (#1911). Stream consumers also inherit a default prefetch of 65,535.

## Known shortcomings

- A vendor customer case study: the baseline is an unnamed serverless Kafka and the 5 GB to 40 MB memory figure is a local dev install.
- Not Kafka wire-compatible (AMQP 0-9-1 and MQTT 3.1.x only; no AMQP 1.0, no MQTT 5, QoS2 downgraded to QoS1). Single-leader cluster (more nodes add redundancy, not write capacity), etcd required, zombie-leader bug on disk stall open (#2151). Since 2.9.0 confirms wait on syncfs and ISR followers, so the case study's numbers predate this. mmap risks: SIGBUS after a disk alarm (#2180), use-after-munmap (#2181), 30-200x disk write amplification (#2176), redelivery state lost on restart (#1911).

## Caveats and trade-offs

First-party case study (a customer testimonial on the vendor's own site) with no hardware or instance sizing for either side and no independent reproduction. The memory figure is explicitly from a development instance. The production baseline was an unnamed serverless/managed Kafka service that had reliability problems ('broker not found', 'leader missing'), not a tuned self-hosted Kafka, so the 300x publish-time gain likely reflects provider, network and client differences more than the broker. The growth from \~4,000 to 50,000+ messages a day is business growth, not a performance measurement.

AMQP 0-9-1/MQTT semantics differ from Kafka's log-based model (no offset replay, different consumer-group semantics); numbers come from one customer's migration writeup, not a controlled apples-to-apples benchmark; the prior Kafka deployment's sizing/tuning is unstated.

## Maintenance

Very active: v2.10.0 shipped on 2026-09-25 after 2.9.3 on 2026-09-09, with frequent patch releases. It is Apache-2.0 and deployed as a packaged server, and CloudAMQP sells a hosted version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The CloudAMQP/LavinMQ customer story (2024-10-25, DAT Systems) quotes 5 GB to under 40 MB of memory 'in an instance in a development environment', consume times 3x lower and publish times 300x better than 'our previous Kafka integration'. These are first-party testimonial numbers with no methodology or sizing, so the tier is C.
- **Verifier notes:** The quotes match. The baseline was 'serverless Apache Kafka' (unnamed provider), which weakens the comparison, but tier C is already right. Metadata is verified: Apache-2.0, 1,018 stars, last commit 2026-09-25.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://lavinmq.com/blog/dat-systems-user-story>
  - <https://github.com/cloudamqp/lavinmq>
- **Sources the enricher read:**
  - <https://github.com/cloudamqp/lavinmq>
  - <https://github.com/cloudamqp/lavinmq/blob/main/README.md>
  - <https://github.com/cloudamqp/lavinmq/blob/main/CONTRIBUTING.md>
  - <https://github.com/cloudamqp/lavinmq/blob/main/shard.yml>
  - <https://github.com/cloudamqp/lavinmq/blob/main/CHANGELOG.md>
  - <https://github.com/cloudamqp/lavinmq/blob/main/Makefile>
  - <https://github.com/cloudamqp/lavinmq/blob/main/Dockerfile>
  - <https://github.com/cloudamqp/lavinmq/blob/main/src/lavinmq/mfile.cr>
  - <https://github.com/cloudamqp/lavinmq/blob/main/src/lavinmq/message_store.cr>
  - <https://github.com/cloudamqp/lavinmq/blob/main/src/lavinmq/persister.cr>
  - <https://github.com/cloudamqp/lavinmq/blob/main/src/lavinmq/vhost.cr>
  - <https://github.com/cloudamqp/lavinmq/blob/main/src/lavinmq/amqp/queue/durable_queue.cr>
  - <https://github.com/cloudamqp/lavinmq/blob/main/src/lavinmq/config/options.cr>
  - <https://github.com/cloudamqp/lavinmq/blob/main/docs/streams.md>
  - <https://github.com/cloudamqp/lavinmq/blob/main/docs/publisher-confirms.md>
  - <https://github.com/cloudamqp/lavinmq/issues/2226>
  - <https://github.com/cloudamqp/lavinmq/issues/2180>
  - <https://github.com/cloudamqp/lavinmq/issues/2176>
  - <https://github.com/cloudamqp/lavinmq/issues/2151>
  - <https://github.com/cloudamqp/lavinmq/issues/2181>
  - <https://github.com/cloudamqp/lavinmq/issues/2228>
  - <https://github.com/cloudamqp/lavinmq/issues/1911>
  - <https://github.com/cloudamqp/lavinmq/issues/2259>
  - <https://github.com/cloudamqp/lavinmq/releases>
  - <https://github.com/cloudamqp/lavinmq-benchmark>
  - <https://github.com/cloudamqp/lavinmq-benchmark/blob/main/results/v2.9.3/throughput.md>
  - <https://github.com/cloudamqp/lavinmq-benchmark/blob/main/results/v2.9.3/latency_P99.md>
  - <https://github.com/cloudamqp/lavinmq-benchmark/blob/main/results/lavinmq_throughput.md>
  - <https://lavinmq.com/blog/dat-systems-user-story>
  - <https://hn.algolia.com/api/v1/search?query=LavinMQ&tags=story>
  - <https://news.ycombinator.com/item?id=47933145>
  - <https://news.ycombinator.com/item?id=39959686>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cloudamqp/lavinmq`) · [data/wave6/enrich/raw/github_com_cloudamqp_lavinmq.json](../../../data/wave6/enrich/raw/github_com_cloudamqp_lavinmq.json) (enrichment confidence 0.72)

</details>
