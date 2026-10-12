# RabbitMQ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Erlang` · `MPL-2.0` · 🟢 active

> Erlang multi-protocol broker; unbatched per-message delivery gave \~2.5x lower median latency than Kafka at 500 msg/s.

| | |
|---|---|
| **Beats** | Apache Kafka |
| **Claimed result** | RabbitMQ p50 2.6ms vs Kafka p50 6.5ms at 500 msg/s (\~2.5x lower median latency); tails converge at p99.9 (RabbitMQ 11.1ms vs Kafka 11.0ms, effectively tied) (derived from page data for the ratio) |
| **Workload** | One publisher + one consumer, Kafka (confluent-kafka/librdkafka client) and RabbitMQ (pika blocking client) both containerized on the same host, 4 CPU/4GB each, 4 lanes, 256-byte payloads, durability level 'broker' (Kafka acks=1 / RabbitMQ persistent+publisher-confirms), end-to-end publish-to-consume latency at an offered rate of 500 msg/s where both brokers keep up. |
| **Metric** | latency |
| **Hardware** | Apple Silicon laptop, Docker Desktop, both brokers containerized with identical 4 CPU / 4GB limits sharing the host with the load generator; exact chip model (M1/M2/M3/etc.) not stated |
| **Adoption** | 13,880 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/rabbitmq/rabbitmq-server) · [benchmark](https://github.com/i-safonoff/broker-tradeoffs/blob/main/docs/02-latency.md) |

## Verdict

In a personal benchmark repo (i-safonoff/broker-tradeoffs), one Python publisher and one consumer at a fixed 500 msg/s of 256-byte persistent, confirmed messages gave RabbitMQ 4 classic queues (pika blocking client) a p50 of 2.6 ms vs 6.5 ms for Kafka (cp-kafka 7.8.0 image, single KRaft node, acks=1, linger.ms=5, confluent-kafka client), with p99.9 tied at 11.1 vs 11.0 ms; both ran in Docker Desktop on an unspecified Apple Silicon laptop with 4 CPU/4 GB per broker and RF=1. At 2,000 and 8,000 msg/s the single pika publisher topped out near 1,100 msg/s, so those RabbitMQ rows measure load-generator backlog, while Kafka kept up at 4.4 and 3.4 ms p50.

## Use it when

- Work queues at modest rates (hundreds of msg/s per queue, small payloads) where median end-to-end latency matters more than p99.9: 2.6 ms vs Kafka's 6.5 ms p50 at 500 msg/s with 256 B persistent, confirmed messages.
- Per-message routing through exchanges and bindings, plus built-in retry, delay and dead-letter handling that Kafka leaves to the application.
- Absorbing a spike by starting more competing consumers on a queue, with no partition count planned in advance.
- Mixed-protocol estates: AMQP 0-9-1 and 1.0, MQTT 5.0 devices and STOMP or WebSocket clients on one broker.
- Cases where Kafka's low-rate floor is its linger.ms batching delay and you can't or won't trade throughput to set linger.ms=0.

## Skip it when

- Fan-out to many independent readers on classic queues: each reader is a full copy. 8 readers held 176,000 messages vs Kafka's 22,000, and publish rate fell 37% vs 13%. Streams would avoid the copies but were not benchmarked.
- Per-key ordering under parallel consumers: 11.5% of same-key messages were reordered with 8 competing consumers, vs 0% for Kafka, unless you rebuild partitioning with the consistent-hash exchange.
- Replaying history after a bug: an acknowledged classic-queue message is gone.
- High sustained confirmed publish rates from a synchronous client. One pika publisher with per-message confirms capped at \~1,100-1,500 msg/s, against 415,767 msg/s for one Kafka producer in the same suite. The docs also say confirm latency under constant load can reach a few hundred ms.
- Data safety or HA on classic queues: they are non-replicated since 4.0. Quorum queues or streams are the replicated options, and neither was measured here.

## How it is fast

The latency win comes from not batching: each publish goes on the wire at once (listener sockets default to TCP_NODELAY), a direct exchange routes it with a hash lookup, and it lands in a per-queue Erlang process that keeps up to 2,048 messages in memory for a short queue. Persistent messages in a durable classic queue (CQv2) are appended to a per-queue segment store if under the 4,096-byte embedding threshold, or to the shared per-vhost message store if larger. fsync is a group commit: the queue syncs as soon as its mailbox drains, or on a 200 ms timer under load, and only then sends publisher confirms. The benchmark's median gap is mostly Kafka's producer waiting out linger.ms=5 for a batch, which the benchmark page itself calls a tunable dial rather than a broker limit.

## Compared with alternatives

NATS JetStream's catalogued result is a lower p50 (0.5 ms vs Kafka's 7.2-7.8 ms, from a different harness), and LavinMQ speaks only AMQP 0-9-1 and MQTT 3.1.x, so pick RabbitMQ when you need exchange-based routing, dead-lettering and delays, AMQP 1.0/MQTT 5.0/STOMP, or replicated quorum queues and streams. For high-rate log workloads, the Kafka-replacement siblings (Redpanda, AutoMQ, Pulsar) target that case and this entry does not.

## Integration

| | |
|---|---|
| **Form** | standalone server (Erlang/OTP release; distro packages, Docker image, Kubernetes operator); applications use a protocol client library |
| **Dependencies** | Erlang/OTP runtime. Bundled Erlang deps: Ranch, Ra (Raft), Khepri (metadata store), Osiris (streams), Cowboy (HTTP), Seshat (metrics). Plus a client library per protocol (the benchmark used pika). |
| **Minimum toolchain** | Erlang/OTP 27.0+ (4.3.6 supports OTP [27.0, 29.0)); source builds use GNU Make 4 and Elixir 1.17-1.20 for the CLI tools |
| **Platforms** | Linux (Debian/Ubuntu, RPM distros, openSUSE), Windows 10 and Windows Server, macOS; FreeBSD and Solaris run unofficially; not z/OS or hosts with under 100 MB RAM |
| **Thread safety** | Broker is concurrent by design: connections, channels and queues are separate Erlang processes. Each classic queue is one gen_server2 process, so work on a single queue is serialised. Client-side thread safety depends on the client library and is not documented in this repo. |
| **Drop-in for the baseline** | no |

## Gotchas

- The benchmark harness skews both sides. Its RabbitMQ consumer polls with basic_get and sleeps 2 ms whenever all four lane queues are empty, while the Kafka consumer long-polls (fetch.min.bytes=1, fetch.wait.max.ms=10). The harness also sets Kafka's linger.ms=5 explicitly. So neither p50 is a broker constant.
- Confirms for persistent messages wait for fsync, and fsync is group-committed (on queue idle, or on a 200 ms timer). Waiting for one confirm at a time serialises every publish on a round trip; use asynchronous or streamed confirms, or several publishers.
- 4.3.0 is a breaking release. It removed CQv1, so declaring x-queue-mode or x-queue-version=1 now fails. It removed Mnesia in favour of Khepri, so a majority of cluster nodes must be up. It rejects transient non-exclusive queues by default. In-place upgrades are only supported from 4.2.x.
- Security churn: 83 GitHub security advisories were published May-Sep 2026 (2 critical, 20 high; e.g. pre-auth decompression bombs, OAuth/JWKS flaws, topic-wildcard routing blowup). Fixes land in current patch releases, and COMMUNITY_SUPPORT.md says patch releases for series out of community support are not public for non-paying users, so stay on the latest series.

## Known shortcomings

- Evidence is a 0-star personal benchmark repo on unnamed Apple Silicon; Kafka's latency floor comes from linger.ms=5, and pika with publisher confirms tops out at \~1.1k msg/s while Kafka wins at 2k/8k msg/s.
- The harness skews latency (the RabbitMQ consumer polls basic_get with a 2 ms sleep while Kafka long-polls with linger.ms=5); the win holds only at 500 msg/s because one pika publisher caps at \~1,100 msg/s; classic queues only, RF=1, unpinned rabbitmq:4 image. SECURITY: 83 GHSAs from 2026-05 to 09 (2 critical, 20 high), with public patches only for the latest series; 4.3.0 removed CQv1 and Mnesia (breaking).

## Caveats and trade-offs

Single laptop, single node each, RF=1 with no replication tested. Results depend as much on the client libraries (confluent-kafka/librdkafka vs pika's blocking adapter) as on the brokers. The page itself says Kafka's low-rate floor is its configured linger.ms=5 batching delay ('a dial, not a property'), which accounts for most of the p50 gap. The win exists only at 500 msg/s. At 2,000 and 8,000 msg/s one pika publisher with confirms topped out near 1,100 msg/s (p50 8.9 s and 65.5 s, a load-generator backlog), while Kafka kept up with a p50 of 4.4 ms and 3.4 ms. RabbitMQ 4 classic queues only. Exact CPU model not given ('Apple Silicon'). The benchmark repo is a 0-star personal project, though its methodology is unusually rigorous: repeated runs, a documented coordinated-omission fix, and committed raw JSON results.

RabbitMQ loses badly on fan-out in the same suite (22,000 vs Kafka's 176,000 messages retained for 8 readers) and reorders 11.5% of same-key messages at 8 consumers vs 0% for Kafka; RabbitMQ's confirmed-publish throughput here is capped by pika's lack of batched confirms (one round trip per message), so above \~1,100 msg/s the 'RabbitMQ' numbers actually measure the load generator's backlog, not the broker.

## Maintenance

Actively maintained by Broadcom's RabbitMQ team (4.3.6 released 2026-09-14, last push 2026-09-26) with an MPL-2.0 core that is free to deploy, but community support and public patch releases cover only the latest release series.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** docs/02-latency.md has exactly the 500 msg/s row: RabbitMQ p50 2.6 ms vs Kafka 6.5 ms, p99.9 11.1 vs 11.0 ms. The harness is public (src/brokerlab/, results/latency/), but it is a personal 0-star repo, not a peer-reviewed paper or a well-known suite, and methodology.md gives only 'Apple Silicon' with no chip model, so it is not B or A.
- **Verifier notes:** The numbers are accurate, but the record overstates the tier: a personal benchmark repo is not a 'well-known independent third-party suite', so the tier is C. The license API returns NOASSERTION. The LICENSE file says the core and tier-1 plugins are MPL-2.0 and some OCF files are Apache-2.0, so the license stays copyable. Stars (13,880) and last commit (2026-09-26) are verified.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/docs/02-latency.md>
  - <https://github.com/i-safonoff/broker-tradeoffs>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/docs/methodology.md>
  - <https://github.com/rabbitmq/rabbitmq-server>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/docs/02-latency.md>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/docs/methodology.md>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/docs/01-durability.md>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/docs/03-fanout.md>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/docs/04-ordering.md>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/docs/choosing.md>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/docker-compose.yml>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/ops/rabbitmq.conf>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/src/brokerlab/transport/rabbit.py>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/src/brokerlab/transport/kafka.py>
  - <https://github.com/i-safonoff/broker-tradeoffs/blob/main/results/latency/latency__rabbitmq__61fbc5970eca.json>
  - <https://github.com/rabbitmq/rabbitmq-server>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/AGENTS.md>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/COMMUNITY_SUPPORT.md>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/docs/compatibility.json>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/release-notes/4.3.0.md>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/release-notes/4.3.6.md>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/deps/rabbit/Makefile>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/deps/rabbit/src/rabbit_classic_queue_store_v2.erl>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/deps/rabbit/src/rabbit_classic_queue_index_v2.erl>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/deps/rabbit/src/rabbit_variable_queue.erl>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/deps/rabbit/src/rabbit_msg_store.erl>
  - <https://github.com/rabbitmq/rabbitmq-server/blob/main/deps/rabbit/src/rabbit_amqqueue_process.erl>
  - <https://github.com/rabbitmq/rabbitmq-server/releases>
  - <https://github.com/rabbitmq/rabbitmq-server/security/advisories>
  - <https://github.com/rabbitmq/rabbitmq-server/issues/16141>
  - <https://github.com/rabbitmq/rabbitmq-server/issues?q=latency>
  - <https://github.com/rabbitmq/rabbitmq-website/blob/main/docs/confirms.md>
  - <https://github.com/rabbitmq/rabbitmq-website/blob/main/docs/classic-queues.md>
  - <https://github.com/rabbitmq/rabbitmq-website/blob/main/docs/platforms.md>
  - <https://github.com/rabbitmq/rabbitmq-website/blob/main/docs/streams.md>
  - <https://github.com/cloudamqp/lavinmq>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/rabbitmq/rabbitmq-server`) · [data/wave6/enrich/raw/github_com_rabbitmq_rabbitmq_server.json](../../../data/wave6/enrich/raw/github_com_rabbitmq_rabbitmq_server.json) (enrichment confidence 0.7)

</details>
