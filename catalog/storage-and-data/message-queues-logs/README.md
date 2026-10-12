# Message queues and logs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md)</sub>

**What these beat:** Kafka, NATS, ZeroMQ  
**28 entries:** 2 tier A · 2 tier B · 24 tier C · 0 tier D · 24 copyable, 4 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**NATS JetStream**](nats-io-nats-server.md) | CNCF Go messaging server whose built-in JetStream persistence showed \~14x lower median latency than Kafka at light load. | **A** | Go | Apache-2.0 | 🟢 active |
| 2 | [**Monocoque**](vorjdux-monocoque.md) | Pure-Rust, ZeroMQ wire-compatible (ZMTP 3.x) async messaging library; about 3x lower REQ/REP latency than libzmq. | **A** | Rust | MIT | 🟢 active |
| 3 | [**NanoMsg**](nanomsg-nanomsg.md) | C library of brokerless messaging patterns (PUB/SUB, REQ/REP, etc.) with lower small-message latency than ZeroMQ on one host. | **B** | C | MIT | 🟢 active |
| 4 | [**NNG (nanomsg-next-generation)**](nanomsg-nng.md) | Maintained C rewrite of nanomsg (Scalability Protocols). It beats nanomsg's pub/sub throughput only for very large messages. | **B** | C | MIT | 🟢 active |
| 5 | [**Apache Pulsar**](apache-pulsar.md) | Multi-tenant pub-sub broker on BookKeeper; vendor benchmark beats Kafka throughput, but the 100-partition win needs journaling off. | **C** | Java | Apache-2.0 | 🟢 active |
| 6 | [**RabbitMQ**](rabbitmq-rabbitmq-server.md) | Erlang multi-protocol broker; unbatched per-message delivery gave \~2.5x lower median latency than Kafka at 500 msg/s. | **C** | Erlang | MPL-2.0 | 🟢 active |
| 7 | [**Eclipse Mosquitto**](eclipse-mosquitto-mosquitto.md) | Lightweight C MQTT broker; one 2023 vendor study measured \~2.7x lower 64 B latency than Kafka, but lower message rate. | **C** | C | EPL-2.0 OR EDL-1.0 | 🟢 active |
| 8 | [**AutoMQ**](automq-automq.md) | Kafka 3.9 fork with S3-backed stateless brokers; beat Kafka's publish latency only with a now-commercial EBS WAL. | **C** | Java | Apache-2.0 | 🟢 active |
| 9 | [**Fluvio**](fluvio-community-fluvio.md) | Rust distributed streaming broker with a Kafka-style topic/partition log and in-broker WASM transforms; vendor bench shows 1.4-1.56x Kafka producer throughput. | **C** | Rust | Apache-2.0 | 🟢 active |
| 10 | [**Zenoh**](eclipse-zenoh-zenoh.md) | Rust pub/sub and query protocol that can run with or without a broker; in one 2023 study it moved 10-65x Kafka's bitrate. | **C** | Rust | Apache-2.0 OR EPL-2.0 | 🟢 active |
| 11 | [**Liftbridge**](liftbridge-io-liftbridge.md) | Go server adding Kafka-style partitioned, replicated logs on top of NATS; self-reports \~1.1x NATS JetStream publish throughput on one node. | **C** | Go | Apache-2.0 | 🟢 active |
| 12 | [**Apache Fluss**](apache-fluss.md) | Columnar (Arrow) streaming table storage for Flink/lakehouse; cuts bandwidth vs Kafka for wide tables with many column-selective consumers. | **C** | Java | Apache-2.0 | 🟢 active |
| 13 | [**Walrus (embedded log/WAL storage engine)**](nubskr-walrus.md) | Embeddable Rust per-topic write-ahead log engine; \~8% more unsynced writes/s than a local single-broker Kafka, tied when fsync'd. | **C** | Rust | MIT | 🟢 active |
| 14 | [**Eclipse Cyclone DDS**](eclipse-cyclonedds-cyclonedds.md) | C implementation of OMG DDS brokerless pub/sub over UDP; one 2023 vendor-adjacent test measured \~37x Kafka's small-message rate. | **C** | C | EPL-2.0 OR BSD-3-Clause | 🟢 active |
| 15 | [**LavinMQ**](cloudamqp-lavinmq.md) | AMQP 0-9-1/MQTT 3.1.1 broker in Crystal with a very small RAM footprint; one customer replaced managed Kafka with it. | **C** | Crystal | Apache-2.0 | 🟢 active |
| 16 | [**msgq (comma.ai)**](commaai-msgq.md) | comma.ai's shared-memory ring-buffer pub/sub for one machine, callable from Python and C++; about 3.2x pyzmq IPC on Python-driven ping-pong. | **C** | C++ | MIT | 🟢 active |
| 17 | [**Woodpecker**](zilliztech-woodpecker.md) | Go WAL library storing append-only logs on S3/object storage or local disk; vendor test shows 3.5-5.8x Kafka single-stream write throughput | **C** | Go | Apache-2.0 (server/… | 🟢 active |
| 18 | [**FluxMQ**](gosuda-fluxmq.md) | Single-binary Rust broker that speaks the Kafka wire protocol; claims \~29% more producer msg/s than Kafka 3.9. | **C** | Rust | MIT | 🟢 active |
| 19 | [**StrangeQ**](maxpert-strangeq.md) | Single-node Go AMQP 0.9.1 broker speaking RabbitMQ's wire protocol; author measures 1.1-4.5x RabbitMQ 4.3's durable, confirmed throughput. | **C** | Go | MIT | 🟢 active |
| 20 | [**Mino**](bkcarlos-mino.md) | C++20 shared-memory pub/sub framework passing slab handles over SPSC rings; beat Protobuf+ZeroMQ in author's six-process pipeline benchmark. | **C** | C++ | LGPL-3.0 | 🟢 active |
| 21 | [**SMF write-ahead-log (Seastar Message Fabric)**](smfrpc-smf.md) | Seastar thread-per-core O_DIRECT write-ahead log from the smf project; \~48x lower worst-case produce latency than Kafka 1.0. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 22 | [**TCPSHM**](mengrao-tcpshm.md) | Header-only C++11 framework for crash-recoverable point-to-point messaging over TCP or shared memory; claims \~4.8x lower RTT than ZeroMQ. | **C** | C++ | MIT | 🔴 abandoned |
| 23 | [**Fero**](pemrouz-fero.md) | Experimental Node.js library for sharded, replicated in-memory state services; claims sub-millisecond round-trip acks versus Kafka's quoted 2 ms. | **C** | JavaScript | MIT (declared in the… | 🔴 abandoned |
| 24 | [**High-performance pub/sub (uWS broadcast-coalescing…**](skyformat99-high-performance-pub-sub.md) | 150-line C++11 µWebSockets demo of broadcast coalescing for pub/sub fan-out; claims 89 ms vs Redis pub/sub's 5 s. | **C** | C++ | Zlib | 🔴 abandoned |
| 25 | [**Redpanda**](redpanda-data-redpanda.md) | Kafka-API-compatible streaming broker in C++ on Seastar; vendor OMB runs show 12-70x lower p99.99 latency than Kafka. | **C** | C++ | BUSL-1.1 (core; converts to… (study only) | 🟢 active |
| 26 | [**Wisp**](iamd3vil-wisp.md) | Experimental Rust server speaking the NATS Core client protocol; about 3.7-4.4x nats-server throughput on 1,000-subscriber loopback fan-out. | **C** | Rust | no license (study only) | 🟢 active |
| 27 | [**Harper (formerly HarperDB)**](paper-harper-formerly-harperdb.md) | Node.js runtime fusing RocksDB-backed tables, app code and MQTT/WebSocket pub/sub; vendor benchmark: lower latency than Kafka stacks at ≤1k events/s. | **C** | JavaScript | The Harper Pro image under… (study only) | 🟢 active |
| 28 | [**SocketPro**](udaparts-socketpro.md) | C++ async RPC framework with a built-in persistent server queue; the vendor claims 3.6-54x RabbitMQ's enqueue/dequeue speed. | **C** | C++ | no license (study only) | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
