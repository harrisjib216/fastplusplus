# Eclipse Mosquitto

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `EPL-2.0 OR EDL-1.0` · 🟢 active

> Lightweight C MQTT broker; one 2023 vendor study measured \~2.7x lower 64 B latency than Kafka, but lower message rate.

| | |
|---|---|
| **Beats** | Kafka |
| **Claimed result** | Latency (64 B ping-pong, RTT/2), per Tab. 2/3: MQTT 27 us vs Kafka 73 us on a single machine (\~2.7x), and 45 us vs 84 us multi-machine (\~1.9x) (derived from page data). The throughput win is narrow. On a single machine at 32 KiB, MQTT gets 7.6 Gbps vs Kafka's 3.6 Gbps (\~2.1x); at 16 KiB it is 4.8 vs 4.2 Gbps (\~1.1x) (derived from page data, Tab. 5). Multi-machine at 32 KiB it is 8.6 vs 4.6 Gbps (\~1.9x) (derived from page data, Tab. 7). Kafka wins elsewhere: message rate at 8 B is 61.6K vs 34.2K msg/s (\~1.8x in Kafka's favour), and at 64 KiB Kafka reaches 3.6 Gbps vs MQTT's 222 Mbps (\~16x in Kafka's favour) (derived from page data). |
| **Workload** | Same pub/sub throughput and ping-pong latency suite as the Cyclone DDS entry: MQTT via Eclipse Mosquitto 2.0.15 broker + Paho MQTT C client vs Kafka 3.2.1 broker (rdkafka client), payload 8B-512MiB, single- and multi-machine (100GbE). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5800X @ fixed 4.0 GHz, Ubuntu 20.04.3 LTS; multi-machine scenario used 100 Gb Ethernet |
| **Adoption** | 11.2k stars |
| **Last commit** | 2026-09-03 |
| **Links** | [repository](https://github.com/eclipse-mosquitto/mosquitto) · [benchmark](https://arxiv.org/pdf/2303.09419v1) |

## Verdict

A 2023 arXiv preprint (v1, not peer-reviewed) by the ZettaScale Zenoh team and National Taiwan University compared Mosquitto 2.0.15 with Paho C 1.3.11 clients at QoS 0 (inflight and queue limits unlimited) against Kafka 3.2.1 with the rdkafka 0.28.0 client (acks=0, linger.ms=0, no compression). It ran on a Ryzen 7 5800X fixed at 4.0 GHz under Ubuntu 20.04, on one host and over 100 GbE, gave no compiler or flags, and its harness repo now returns 404. Mosquitto won 64 B ping-pong latency (27 vs 73 us on one host, 45 vs 84 us networked) and won bitrate only around 16-32 KiB payloads (about 8-9 Gbps vs Kafka's 3-5 Gbps). Kafka had the higher message rate for small payloads and far higher bitrate from 64 KiB up to 512 KiB, where its client stopped working.

## Use it when

- Small-message pub/sub (up to about 32 KiB) where broker-relayed latency matters: the study measured 27 us on one host and 45 us over 100 GbE, against Kafka's 73 and 84 us.
- IoT and edge telemetry that needs the MQTT standard, so any off-the-shelf MQTT client or device can connect to one small C broker with TLS, websockets and ACL/password/dynamic-security plugins.
- Live fan-out where each hop only needs QoS 0/1/2 delivery and there is no need to reread history.
- Many publishers feeding a few subscribers. To scale out, the maintainer recommends running several independent brokers behind a load balancer (#3356).
- Replacing Kafka where it was only ever used as a low-latency message bus and retention or replay were never needed.

## Skip it when

- You need a durable, partitioned, replayable log with consumer offsets. Mosquitto has none of these. Built-in persistence snapshots every 1800 s by default, so a crash loses everything since the last snapshot. The docs recommend plugin-based persistence (persist-sqlite) instead.
- Your workload is a high rate of small messages. In the study Kafka held 53-62K msg/s below 2 KiB against Mosquitto's 32-38K msg/s, and Zenoh and Cyclone DDS were one to two orders of magnitude faster than both.
- Your payloads are larger than 32 KiB. Mosquitto's bitrate collapsed beyond 32 KiB (the record's table data puts Kafka about 16x ahead at 64 KiB), and the multi-machine test failed above 64 MiB.
- You need more than one CPU core per broker, or high availability. The broker is single-threaded (maintainer, #2182), and clustering is explicitly not planned for the core (#3356); users run 14 instances behind HAProxy instead (#3574).
- You need end-to-end delivery guarantees. QoS covers a single hop only. Once max_queued_messages (default 1000) is reached, the broker silently drops messages while still sending PUBACK (#3687), and control packets such as UNSUBACK can also be dropped when the queue is full (#3542, open).

## How it is fast

The broker is a single-threaded, non-blocking reactor. One process multiplexes every socket through epoll on Linux, kqueue on BSD and macOS, or poll elsewhere, so the publish path has no locks and no hand-offs between threads. Subscriptions are held in a topic tree with one uthash table per level; the '+' and '#' wildcard children are found by precomputed hash values. Each published message is stored once and reference-counted across subscriber queues rather than copied. Nothing is written to disk on the hot path, because built-in persistence is a periodic snapshot. At QoS 0, which is what the study measured, there are no acks either.

## Compared with alternatives

The same study found Zenoh ahead of Mosquitto on throughput (33x at 8 KB, 6x at 32 KB) and Cyclone DDS ahead on latency (8 us vs 27 us on one host). Pick Mosquitto when you specifically need standard MQTT, with its client ecosystem and simple brokered deployment. Pick Redpanda, Pulsar or AutoMQ when you actually need Kafka's durable log.

## Integration

| | |
|---|---|
| **Form** | Standalone broker daemon built with make or CMake. Client side: libmosquitto as a shared or static C library, plus the mosquittopp C++ wrapper. The benchmark used the Paho MQTT C client, not libmosquitto. |
| **Dependencies** | cJSON is required on current master (2.1). Optional: OpenSSL (TLS), c-ares (SRV lookups), libmicrohttpd (HTTP API), sqlite3 (persist-sqlite plugin), libedit (mosquitto_ctrl shell), pthreads (client-library threading) and xsltproc/docbook (man pages). uthash and utlist are bundled. |
| **Minimum toolchain** | C99 (-std=gnu99 in the Makefile build); CMake 3.24+ for the CMake build on current master |
| **Platforms** | Linux (epoll), macOS and BSD (kqueue, added in 2.1), Windows (up to 8192 connections where supported), with AIX linker scripts in the tree. Plain C with no architecture-specific code paths found. |
| **Thread safety** | The broker runs one single-threaded event loop per process. libmosquitto is thread safe, except for mosquitto_lib_init, when built with threading support and after the application calls mosquitto_threaded_set; without threading support it is not guaranteed to be safe. |
| **Drop-in for the baseline** | false — it speaks a different wire protocol (MQTT, not the Kafka protocol), has no partitions, consumer offsets or log replay, and its MQTT v5 shared subscriptions do round-robin load balancing, which is not the same as Kafka consumer groups. |

## Gotchas

- The benchmark set max_inflight_messages and max_queued_messages to unlimited; the defaults are 20 and 1000. The maintainer warns that unlimited means storing unlimited messages per client, and on a single-threaded broker that can push CPU and memory to their limits (#2182).
- Since 2.1, max_packet_size defaults to 2,000,000 bytes (earlier versions allowed up to the 256 MB MQTT limit). Clients sending larger packets are disconnected unless you raise the limit, and v3.1.1 clients cannot be told about it.
- set_tcp_nodelay defaults to false. Messages sent back to back can hit Nagle-style delays of about 40 ms (#433); enable the option for latency-sensitive traffic.
- Version 2.0.15, the one benchmarked, is affected by CVE-2023-28366, CVE-2023-0809 and CVE-2023-3592, all fixed in 2.0.16. Use 2.0.23 or 2.1.x, and re-benchmark, because 2.1 also changed defaults and allocation behaviour.

## Known shortcomings

- Same preprint and dead harness as Cyclone DDS. The latency win is real (27 vs 73 us, 45 vs 84 us) but the throughput win holds only at 16-32 KiB; Kafka is ahead elsewhere (\~16x at 64 KiB).
- Single-threaded broker with no clustering planned (#3356); no log, replay or offsets; persistence is a snapshot every 1800 s by default; queue overflow is silently dropped but still PUBACKed (#3687). The benchmark set inflight/queue limits to unlimited (the maintainer warns of CPU/memory blowup); the benchmarked 2.0.15 has 3 CVEs fixed in 2.0.16; the client was Paho, not libmosquitto.

## Caveats and trade-offs

Same paper/harness as the Cyclone DDS entry (github.com/ZettaScaleLabs/zenoh-perf, code public, hardware stated, compiler/flags not stated -&gt; capped at B). Authored by the Zenoh/ZettaScale team as a reference comparison for their own Zenoh paper, not by Mosquitto or Kafka maintainers; the win is narrow (one payload size/metric) and message-rate throughput actually favors Kafka.

MQTT is a lightweight pub/sub protocol with no partitioned commit log, no replay, and weaker durability/ordering guarantees than Kafka; throughput degrades badly for payloads above 32 KiB in this benchmark, and the multi-machine test failed entirely above 64 MiB payloads.

## Maintenance

Actively maintained Eclipse project: latest tag v2.1.2 (2026-02-09), with 2.1.3 fixes queued and master commits through 2026-09-03. Dual-licensed EPL-2.0 or BSD-3-Clause, with binaries on mosquitto.org and a vcpkg port; it is meant to be deployed as a service rather than vendored.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** This is the same arXiv 2303.09419 v1 preprint, measuring Mosquitto 2.0.15 with the Paho C client against Kafka 3.2.1. The CPU is stated, but there is no compiler or flags, the cited benchmark code (ZettaScaleLabs/zenoh-perf, comparison/mqtt) is 404, and the paper is not peer-reviewed. It is a Zenoh vendor study rather than an established independent suite, so C.
- **Verifier notes:** The record's figures are right, but its claim that the harness is public is false: zenoh-perf returns 404. The paper's prose swaps the two latencies ('MQTT and Kafka have a latency of 73 us and 27 us, respectively'), but Tab. 2 gives Kafka 73 and MQTT 27, which the record correctly follows. The metric field says throughput, but the more robust win is latency, which holds in both scenarios; the throughput win exists only at 16-32 KiB. The license is EDL-1.0, which is BSD-3-Clause (LICENSE.txt SPDX: EPL-2.0 OR BSD-3-Clause), and the last commit (2026-09-03) and stars (11.2k) check out.
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2303.09419v1>
  - <https://arxiv.org/abs/2303.09419>
  - <https://github.com/eclipse-mosquitto/mosquitto>
  - <https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/HEAD/NOTICE.md>
  - <https://github.com/ZettaScaleLabs/zenoh-perf>
  - <https://github.com/ZettaScaleLabs/zenoh-perf/tree/master/comparison>
  - <https://api.crossref.org/works>
- **Sources the enricher read:**
  - <https://github.com/eclipse-mosquitto/mosquitto>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/README.md>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/ChangeLog.txt>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/develop/ChangeLog.txt>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/src/mux_epoll.c>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/src/subs.c>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/src/database.c>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/src/loop.c>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/src/mosquitto.c>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/src/mosquitto_broker_internal.h>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/include/mosquitto/libmosquitto.h>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/config.mk>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/CMakeLists.txt>
  - <https://github.com/eclipse-mosquitto/mosquitto/blob/master/man/mosquitto.conf.5.xml>
  - <https://github.com/eclipse-mosquitto/mosquitto/tags>
  - <https://github.com/eclipse-mosquitto/mosquitto/commits/master>
  - <https://github.com/eclipse-mosquitto/mosquitto/issues/3574>
  - <https://github.com/eclipse-mosquitto/mosquitto/issues/3687>
  - <https://github.com/eclipse-mosquitto/mosquitto/issues/3542>
  - <https://github.com/eclipse-mosquitto/mosquitto/issues/2182>
  - <https://github.com/eclipse-mosquitto/mosquitto/issues/433>
  - <https://github.com/eclipse-mosquitto/mosquitto/issues/3356>
  - <https://arxiv.org/pdf/2303.09419v1>
  - <https://export.arxiv.org/api/query?id_list=2303.09419>
  - <https://github.com/ZettaScaleLabs/zenoh-perf>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/eclipse-mosquitto/mosquitto`) · [data/wave6/enrich/raw/github_com_eclipse_mosquitto_mosquitto.json](../../../data/wave6/enrich/raw/github_com_eclipse_mosquitto_mosquitto.json) (enrichment confidence 0.6)

</details>
