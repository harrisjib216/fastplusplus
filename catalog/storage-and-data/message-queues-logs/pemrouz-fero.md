# Fero

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript` · `MIT (declared in the README's License section, 'MIT License © Pedram Emrouznejad', and in package.json as 'pemrouz.mit-license.org'; no LICENSE file, so GitHub reports no SPDX id)` · 🔴 abandoned

> Experimental Node.js library for sharded, replicated in-memory state services; claims sub-millisecond round-trip acks versus Kafka's quoted 2 ms.

| | |
|---|---|
| **Beats** | Apache Kafka |
| **Claimed result** | Round-trip latency over 10,000 messages: median 0.06 ms vs Kafka's reported 2 ms (\~33x), 99th percentile 0.3 ms vs 3 ms (\~10x), 99.9th percentile 1.86 ms vs 14 ms (\~7.5x) (ratios derived from page data). ZeroMQ's reported average of 0.06 ms is about the same as fero's 0.07 ms mean. Throughput at 100-byte messages is \~72 MB/s (755,419 records/s) vs \~75 MB/s (795,064 records/s) for LinkedIn's Kafka, roughly on par. The author reads \~10 vs \~5 MB/s at 10 bytes and \~161 vs \~80 MB/s at 1000 bytes off LinkedIn's graph. On 10-byte vs 3-byte writes, fero does 1,075,657 records/s vs Redis's best-case 552,028.75 records/s (\~1.9x, derived from page data). |
| **Workload** | Single-node fero server + client, fire-and-round-trip-ack of a single message repeated 10,000 times (tests/integration/speed/latency/client); separate throughput test sends 1M messages of 10/100/1000 bytes (tests/integration/speed/sync), modeled on LinkedIn's published Kafka benchmark methodology, and compared against Kafka's and ZeroMQ's own reported latency/throughput figures. |
| **Metric** | latency |
| **Hardware** | Dell XPS 15 9550, Intel Core i7-6700HQ @ 2.60GHz, 4-core/8-thread, 32GB RAM, Windows 10, Node.js v8.0.0 (fero side only; the cited Kafka/ZeroMQ numbers come from LinkedIn's separately-run, multi-machine Kafka benchmark, not a side-by-side run on the same hardware) |
| **Adoption** | 176 stars |
| **Last commit** | 2018-04-22 |
| **Links** | [repository](https://github.com/pemrouz/fero) · [benchmark](https://github.com/pemrouz/fero/blob/master/README.md) |

## Verdict

On one laptop (i7-6700HQ, 32 GB, Windows 10, Node 8.0.0), a single fero client and server on localhost measured 10,000 sequential receipt-acked round trips at 0.06 ms median, 0.3 ms p99 and 1.86 ms p99.9, and receipt-acked 755,419 records/s (72 MB/s) at 100-byte messages over 1M messages. Kafka was never run: the 2/3/14 ms and 795,064 records/s (75.8 MB/s) figures come from LinkedIn's April 2014 end-to-end and consumer-throughput results on a separate multi-machine, 3x-replicated cluster, so the \~33x median-latency gap is indirect and overstates the difference.

## Use it when

- Node.js services that need a small, replicated, in-memory key/value state (sessions, users, config) shared across a handful of processes, with writes to each top-level key serialised on one owner node.
- Prototyping stream- or actor-style microservices on one host or a trusted LAN, where you control every peer and the full data set fits in RAM on every node.
- Fire-and-forget or receipt-acked messaging between Node processes, where the \~0.06 ms loopback round trip (i7-6700HQ, Node 8) matters more than durability.
- As reference code for microtask write coalescing and lazy zero-copy message decoding in Node.js networking.

## Skip it when

- You need a durable log. Nothing is written to disk, the changelog lives in memory (partitions.history.max defaults to Infinity), and every commit is broadcast to every server and client, so memory on every node grows with the total history.
- You want to replace Kafka's API, retention, consumer groups/offsets or replication-factor guarantees. Commits are fire-and-forget broadcasts; a source comment says this 'could be .replicate - broadcast and await replication factor before acking'.
- The network is untrusted or shared. Traffic is plain TCP (Node's net module) and discovery is plaintext UDP multicast; the source has no TLS or authentication, and any host that announces the same service name gets peered.
- Writes are skewed. Partitioning is by top-level key, so a hot key puts all its writes on one owner node.
- You need production support or multi-machine evidence. The last commit was April 2018, the author calls it 'very experimental', the one open issue (a request for peering examples) has had no reply since April 2018, it was benchmarked only on Node 8.0.0, and no multi-node results were published.

## How it is fast

It uses its own binary framing over raw TCP (0x7C marker, 1-byte command, 4-byte big-endian length) with Nagle's algorithm disabled via setNoDelay. Outgoing messages are batched into a 64 KB per-peer outbox buffer that is flushed once per microtask (write coalescing). Receipt acks are cumulative counters written straight from the socket data handler, before the request handler runs, because handler dispatch is deferred to a setTimeout. Decoding is lazy: keys and values are zero-copy sliced from the buffer and memoised only when accessed, and ack/reply Promises exist only if `.on('ack'|'reply')` is called. Owner lookup is a consistent hashring on a red-black tree (djb2 hash, 200 virtual nodes per peer), memoised per change.

## Compared with alternatives

Pick Fero only if you specifically want replicated in-process state inside Node.js services (a sharded plain-object cache with request routing to key owners) and are willing to vendor and maintain it. For a maintained, persistent low-latency broker, take NATS JetStream (catalogued at p50 0.5 ms vs Kafka's 7.2-7.8 ms) or Redpanda; for brokerless low-latency messaging, take Zenoh.

## Integration

| | |
|---|---|
| **Form** | module (npm package `fero`, plain CommonJS JavaScript, plus a `fero` CLI) |
| **Dependencies** | bintrees, chalk, cli-table, colors, easy-table, lodash.merge, lodash.shuffle, minimist, utilise, uuid |
| **Minimum toolchain** | Node.js with async/await (7.6+); benchmarked on Node v8.0.0; package.json has no engines field and modern Node support is not documented |
| **Platforms** | any Node.js platform with TCP and UDP multicast; the benchmark ran on Windows 10 |
| **Thread safety** | Each process runs on the single-threaded Node event loop; you scale by adding processes or nodes. Across nodes, writes for a partition are serialised on its owner, and reads can come from any replica. |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline latency is not like-for-like. The benchmark times a receipt ack that the server writes from its socket data handler before your handler, the commit or any replication runs. Kafka's 2/3/14 ms is producer-to-consumer delivery after full in-sync-replica acknowledgement on LinkedIn's 3x-replicated multi-machine cluster. Likewise, the throughput test's server only echoes (no log append), while LinkedIn's 795,064 records/s is consumer throughput on a 6-partition, 3x-replicated topic.
- The README's constants table disagrees with constants.js: outbox.max is 2^16 in code but 2\*\*28 in the README, connect.wait is 3000 in code but 1000 in the README, and the documented udp.\* options are named multicast.\* in code.
- In the wire format (messages/change.js), key length is stored in one byte and taken from the JS string length rather than the UTF-8 byte length. Keys over 255 characters or with non-ASCII characters look unsafe, and the UTF-8 test covers only values.
- package-lock.json pins minimist 1.2.0 and lodash.merge 4.6.0, both inside GitHub prototype-pollution advisory ranges (minimist CVE-2021-44906 and CVE-2020-7598; lodash.merge GHSA-2m96-9w4j-wgv7 and GHSA-h726-x36v-rx45). The caret ranges in package.json let an install without the lockfile pick up patched versions.

## Known shortcomings

- The Kafka figures (2/3/14 ms, 795k rec/s) are LinkedIn's published numbers, not a head-to-head run on the same hardware; also \~1.9x vs Redis.
- Not like-for-like: Fero acks from the socket handler before the handler/commit/replication run, while the Kafka 2/3/14 ms are LinkedIn's 2014 end-to-end numbers on a 3x-replicated cluster; the throughput bench server only echoes (no log append). No disk persistence (history unbounded in RAM); commits broadcast fire-and-forget. SECURITY: no TLS/auth and plaintext UDP multicast discovery; the lockfile pins vulnerable minimist 1.2.0 and lodash.merge 4.6.0. Keys over 255 chars/non-ASCII are unsafe (1-byte length); abandoned since 2018-04, Node 8 only.

## Caveats and trade-offs

This is an indirect, apples-to-oranges comparison. Fero measures round-trip latency over localhost on one laptop against a single node. The Kafka figures are LinkedIn's end-to-end, producer-to-consumer numbers from a separately run 3-machine benchmark with replication (confirmed on engineering.linkedin.com). The 10-byte and 1000-byte Kafka throughput numbers are the author's readings of LinkedIn's graph. The Redis numbers were taken on a different (Xeon) machine. MIT is declared only in the README and package.json; there is no LICENSE file. The project has been unmaintained since April 2018.

Node.js, single-process-per-node design (no JVM); application-layer sharding via consistent hashring instead of Kafka's fixed partitions/ZooKeeper; author calls the project 'very experimental'; no multi-node clustering benchmark published, no disk-durability model directly comparable to Kafka's log.

## Maintenance

Abandoned since April 2018 (npm v1.7.1, 176 stars, one unanswered open issue), MIT-licensed only through the README and package.json (no LICENSE file), and about 58 KB of plain JavaScript, so it is small enough to vendor, but you would own security fixes and testing on modern Node.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers from the README. The benchmark code is public (tests/integration/speed/latency/client.js, tests/integration/speed/sync) and the hardware and runtime are stated (i7-6700HQ, Node v8.0.0). But Kafka is never run by this benchmark: its figures are quoted from LinkedIn's separate 3-machine 2014 benchmark, so the result falls short of A.
- **Verifier notes:** The README numbers and the LinkedIn figures it cites (2/3/14 ms, 795,064 records/s at 75.8 MB/s) both check out. The main fix is the license: MIT is declared in the README, so the entry is copyable, not reference-only. The metadata is otherwise accurate: 176 stars, last commit 2018-04-22, not archived, not a fork.
- **Fields the verifier corrected:** `license`, `usability`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pemrouz/fero>
  - <https://github.com/pemrouz/fero/blob/master/README.md>
  - <https://github.com/pemrouz/fero/blob/master/package.json>
  - <https://github.com/pemrouz/fero/tree/master/tests/integration/speed>
  - <https://github.com/pemrouz/fero/tree/master/tests/integration/speed/latency>
  - <https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines>
- **Sources the enricher read:**
  - <https://github.com/pemrouz/fero>
  - <https://github.com/pemrouz/fero/blob/master/README.md>
  - <https://github.com/pemrouz/fero/blob/master/package.json>
  - <https://github.com/pemrouz/fero/blob/master/package-lock.json>
  - <https://github.com/pemrouz/fero/blob/master/index.js>
  - <https://github.com/pemrouz/fero/blob/master/cache.js>
  - <https://github.com/pemrouz/fero/blob/master/peer.js>
  - <https://github.com/pemrouz/fero/blob/master/peers.js>
  - <https://github.com/pemrouz/fero/blob/master/server.js>
  - <https://github.com/pemrouz/fero/blob/master/constants.js>
  - <https://github.com/pemrouz/fero/blob/master/dht.js>
  - <https://github.com/pemrouz/fero/blob/master/partition.js>
  - <https://github.com/pemrouz/fero/blob/master/partitions.js>
  - <https://github.com/pemrouz/fero/blob/master/proxy.js>
  - <https://github.com/pemrouz/fero/blob/master/handshake.js>
  - <https://github.com/pemrouz/fero/blob/master/connect.js>
  - <https://github.com/pemrouz/fero/blob/master/retries.js>
  - <https://github.com/pemrouz/fero/blob/master/utils.js>
  - <https://github.com/pemrouz/fero/blob/master/cli>
  - <https://github.com/pemrouz/fero/blob/master/messages/message.js>
  - <https://github.com/pemrouz/fero/blob/master/messages/change.js>
  - <https://github.com/pemrouz/fero/blob/master/messages/ack.js>
  - <https://github.com/pemrouz/fero/blob/master/messages/index.js>
  - <https://github.com/pemrouz/fero/blob/master/discovery/multicast.js>
  - <https://github.com/pemrouz/fero/blob/master/discovery/multicast-udp.js>
  - <https://github.com/pemrouz/fero/blob/master/discovery/multicast-tcp.js>
  - <https://github.com/pemrouz/fero/blob/master/discovery/multicast-tcp-broker.js>
  - <https://github.com/pemrouz/fero/blob/master/discovery/scan.js>
  - <https://github.com/pemrouz/fero/blob/master/tests/integration/speed/latency/client.js>
  - <https://github.com/pemrouz/fero/blob/master/tests/integration/speed/latency/server.js>
  - <https://github.com/pemrouz/fero/blob/master/tests/integration/speed/bench.js>
  - <https://github.com/pemrouz/fero/blob/master/tests/integration/speed/sync/index.js>
  - <https://github.com/pemrouz/fero/blob/master/tests/integration/speed/sync/client.js>
  - <https://github.com/pemrouz/fero/blob/master/tests/integration/speed/sync/peer.js>
  - <https://github.com/pemrouz/fero/blob/master/tests/integration/api/utf8.test.js>
  - <https://github.com/pemrouz/fero/blob/master/tests/integration/api/guarantees.test.js>
  - <https://github.com/pemrouz/fero/issues/1>
  - <https://github.com/pemrouz/fero/issues/2>
  - <https://github.com/pemrouz/fero/commits/master>
  - <https://registry.npmjs.org/fero>
  - <https://api.npmjs.org/downloads/point/last-year/fero>
  - <https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines>
  - <https://hn.algolia.com/api/v1/search?query=fero%20kafka&tags=story>
  - <https://github.com/advisories/GHSA-xvch-5gv4-984h>
  - <https://github.com/advisories/GHSA-vh95-rmgr-6w4m>
  - <https://github.com/advisories/GHSA-2m96-9w4j-wgv7>
  - <https://github.com/advisories/GHSA-h726-x36v-rx45>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/pemrouz/fero`) · [data/wave6/enrich/raw/github_com_pemrouz_fero.json](../../../data/wave6/enrich/raw/github_com_pemrouz_fero.json) (enrichment confidence 0.72)

</details>
