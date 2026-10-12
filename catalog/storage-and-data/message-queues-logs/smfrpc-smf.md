# SMF write-ahead-log (Seastar Message Fabric)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Seastar thread-per-core O_DIRECT write-ahead log from the smf project; \~48x lower worst-case produce latency than Kafka 1.0.

| | |
|---|---|
| **Beats** | Kafka |
| **Claimed result** | \~48x lower worst-case (slowest) latency than Apache Kafka: page states 'Kafka.Slowest(1618ms) / SMF.Slowest(34ms) \~= 48 lower latency', after a performance-debugging pass. SMF started '-1.3X slower' than Kafka after the rewrite. No throughput comparison figures are given. |
| **Workload** | Write 100M 100-byte records via Kafka ProducerPerformance (kafka_2.11-1.0.0, i.e. Kafka 1.0.0; acks=1, lz4 compression.codec=3, 32 partitions) vs the SMF smfb low-level client (batch-size 8196, poll mode, pinned cpusets) against a Seastar-based write-ahead log using O_DIRECT on XFS (epoll + Seastar aio, no DPDK), all on one localhost NVMe/XFS/kernel-4.14 host. Measured end-to-end and server-observed latency; a second workload used 100 messages per batch. |
| **Metric** | latency |
| **Hardware** | NVMe + XFS, Linux kernel 4.14.16-300.fc27.x86_64; exact CPU model not stated |
| **Adoption** | 762 stars |
| **Last commit** | 2021-10-17 |
| **Links** | [repository](https://github.com/smfrpc/smf) · [benchmark](https://www.alexgallego.org/perf/toplev/2018/02/08/performance-debugging.html) |

## Verdict

On one localhost Linux 4.14 host (NVMe + XFS; CPU and compiler version not stated; release builds of that era used -O2 -ggdb per CMake/base_flags.cmake), using Seastar epoll + AIO without DPDK, smfb's slowest write took 34 ms versus 1618 ms for Kafka 1.0.0's ProducerPerformance (100M 100-byte records, acks=1, lz4, 32 partitions). That is about 48x on maximum latency only, with no percentile table or throughput. An earlier, since-deleted docs page (2 bare-metal dual Xeon E5-2640 v3 servers, SATA SSD, DPDK server, Kafka 0.11.0.1) reported 34-43x lower latency percentiles and 1.71M vs 0.42M msgs/s with 1 producer, or 2.27M vs 0.96M with 3 producers.

## Use it when

- You are building a Seastar service and want a reference O_DIRECT segment writer with page-aligned chunking, bounded concurrent DMA writes, and a size-or-time flush policy to port.
- Write-heavy ingest of small records (about 100 B) in large client batches, where acknowledging after in-memory buffering (log-writer semantics, as the author concedes) is acceptable.
- Single-node, per-core-partitioned append logs on Linux + XFS + NVMe, where you can pin cores and route each partition to its owning shard.
- Studying a documented profiling case (perf record/stat, toplev, LLC-miss hunting) on a real log-write path.

## Skip it when

- As a Kafka replacement. It has no Kafka protocol, no replication (chain_replication_service::put only appends locally), no consumer groups, and broker-side reads return 500. The reader code has an in-progress 'XXX working on this' path.
- When you need per-write durability. The write path has no fdatasync, the timer flush defaults to 1 minute (smfb used the default), and acks return before DMA writes finish.
- When you want a maintained dependency. It was deleted from master in Feb 2018, is written against the 2018 Seastar API (old &lt;core/...&gt; include paths), and was built with an Ansible-provisioned Seastar, so expect a port before it compiles.
- Non-Linux, non-x86 or small hosts. smfb refuses to start without SSE4.2, throws below 1 GiB of memory per shard unless --developer is set, and logs an error when the log directory is not on XFS.

## How it is fast

It uses Seastar shard-per-core ownership. Each topic/partition is routed to one core by jump consistent hash and has a single reader/writer, with no locks or atomics. Writes are copied into page-aligned 4 KB chunks and sent as O_DIRECT dma_write calls (up to 4 concurrent per segment) once 1 MB is pending or a flush timer fires, with segments rolled at 64 MB and tagged with Seastar IO priority classes. The 48x result came from a perf/toplev pass: removing a per-put std::sort (74% of CPU), replacing a map.find with std::lower_bound over a std::deque (offsets are monotonic), and caching each entry's on-disk size to cut LLC misses.

## Compared with alternatives

Pick Redpanda (a maintained, Kafka-API-compatible C++ broker also built on Seastar) for any production Kafka replacement, and Walrus (maintained Rust log engine) when you need an embeddable log. Pick the SMF WAL only as a small, Apache-2.0 reference design for a Seastar-native O_DIRECT log writer that you will port and harden yourself.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Seastar (early-2018, with libaio; DPDK optional), Flatbuffers, Boost, zstd, lz4, xxHash, RE2, Roaring bitmaps, HdrHistogram; smf RPC for the smfb broker |
| **Minimum toolchain** | GCC with Seastar-era flags (CMake enables -fconcepts for GCC &gt; 6.1); CMake 3.3+; C++ standard inherited from Seastar pkg-config flags, not stated |
| **Platforms** | Linux x86-64 with SSE4.2 (broker check); XFS expected; O_DIRECT/AIO required |
| **Thread safety** | Seastar sharded&lt;T&gt;: each core owns its partitions, and requests must be submitted on the owning core (a wrong-core append throws in debug builds). There is no cross-thread locking. |
| **Drop-in for the baseline** | no |

## Gotchas

- In wal_segment, append() and do_flush() launch dma_write in the background without awaiting it (commented 'send in background - safely!!'). As written, flush() and close() do not wait for in-flight writes, and write errors are not propagated to the ack.
- wal_segment::open() throws if the segment file already exists, and files are opened with create|truncate. Recovery and reopen depend on epoch-named new files, not on appending to old ones.
- Partition routing is the caller's job (jump_consistent_hash(partition, smp::count)). Misrouting shows up as directory or system_error failures, per the header comment.
- The headline numbers disagree across the author's own sources: the blog says 48x (max latency only), the deleted docs page says 34-43x across percentiles, commit 5585e52f45 says '4x faster than kafka to 91X', and issue #195 says '10x lower latency'.

## Known shortcomings

- The 48x is max latency (1618 ms vs 34 ms against Kafka 1.0.0, acks=1); SMF starts about 1.3x slower. Last real commit 2021-10-17 (the 2023 activity is a dependabot branch).
- The WAL was removed from master on 2018-02-24 (issue #203); the repo is now RPC-only and the WAL survives only in history (772474eb02). Weak durability: no fdatasync in the write path, a 1-minute default timer flush, and dma_write not awaited, so acks precede disk writes. Broker get() always returns 500; no Kafka protocol, replication or consumer groups.
- Tied to the 2018 Seastar API (needs porting); Linux x86 SSE4.2 only, expects XFS and &gt;=1 GiB per shard; built -O2 -ggdb. The author's numbers disagree across sources (blog 48x max latency, deleted docs 34-43x, a commit message 91x, issue #195 10x); a deleted docs page shows 1.71M vs 0.42M msg/s throughput.

## Caveats and trade-offs

First-party blog post by the project author (2018); exact CPU model, compiler and flags not stated; localhost-only test (the author notes that network-rack latency is omitted); the headline 48x is max latency only, and the page gives no percentile tables or throughput comparison; old baseline (Kafka 1.0.0 with acks=1); the benchmark client (smfb) is not present on the current master; GitHub SPDX shows NOASSERTION, but the LICENSE file is Apache-2.0; repo abandoned (last default-branch commit 2021-10-17)

Built on Seastar's thread-per-core model with O_DIRECT/AIO; single-node write-ahead-log component, not a full distributed broker with replication/consumer-group semantics like Kafka; blog author is the project's creator (later founded Redpanda, which reuses this storage-engine lineage and is already catalogued)

## Maintenance

Abandoned: the WAL was deleted from master in Feb 2018, and the repo (last master commit 2021-10-17) is now RPC-only. The Apache-2.0 code can be recovered from commit 772474eb02, but it is tied to a 2018 Seastar API and has unfinished reads and weak durability, so treat it as reference code, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party author blog post (2018) comparing against Apache Kafka on the same localhost NVMe/XFS host, with exact commands. It does not state the CPU model, compiler or flags, and does not link benchmark code. The smfb benchmark client it ran no longer exists under src/smfb on master. That is C.
- **Verifier notes:** The 1618ms vs 34ms slowest-latency numbers and the 1.3x-slower starting point are on the page. The record's workload wording ('100-byte and 8196-message batches', 'Kafka 2.11-1.0') was garbled, so it was rewritten from the page's commands. The last commit was corrected: 2023-04-12 was only a dependabot docs-branch push, and master's last commit is 2021-10-17. Still abandoned. License verified as Apache-2.0 from the LICENSE text.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://www.alexgallego.org/perf/toplev/2018/02/08/performance-debugging.html>
  - <https://github.com/smfrpc/smf>
  - <https://github.com/smfrpc/smf/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/smfrpc/smf>
  - <https://www.alexgallego.org/perf/toplev/2018/02/08/performance-debugging.html>
  - <https://github.com/smfrpc/smf/commit/6addb463cc>
  - <https://github.com/smfrpc/smf/commit/5585e52f45>
  - <https://github.com/smfrpc/smf/commit/3d5cbe9e4c>
  - <https://github.com/smfrpc/smf/commit/a23e328201>
  - <https://github.com/smfrpc/smf/issues/203>
  - <https://github.com/smfrpc/smf/issues/195>
  - <https://github.com/smfrpc/smf/issues/185>
  - <https://github.com/smfrpc/smf/issues/61>
  - <https://github.com/smfrpc/smf/blob/772474eb02/README.md>
  - <https://github.com/smfrpc/smf/blob/772474eb02/docs/write_ahead_log.md>
  - <https://github.com/smfrpc/smf/blob/772474eb02/CMakeLists.txt>
  - <https://github.com/smfrpc/smf/blob/772474eb02/CMake/base_flags.cmake>
  - <https://github.com/smfrpc/smf/blob/772474eb02/CMake/Seastar.cmake>
  - <https://github.com/smfrpc/smf/blob/772474eb02/meta/playbooks/libraries.yml>
  - <https://github.com/smfrpc/smf/blob/772474eb02/meta/playbooks/roles/seastar/tasks/main.yml>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/CMakeLists.txt>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/write_ahead_log.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/write_ahead_log.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_opts.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_opts.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_writer.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_writer_node.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_writer_node.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_segment.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_segment.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_write_behind_cache.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_write_behind_cache.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_requests.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_topics_manager.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_partition_manager.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_reader.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_reader_node.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/filesystem/wal_page_cache.h>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/chain_replication/chain_replication_service.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/smfb/main.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/smfb/smfb_command_line_options.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/smfb/client/low_level_client.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/utils/checks/disk.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/utils/checks/cpu.cc>
  - <https://github.com/smfrpc/smf/blob/772474eb02/src/utils/checks/memory.cc>
  - <https://github.com/emaxerrno>
  - <https://hn.algolia.com/api/v1/items/16401053>
  - <https://github.com/redpanda-data/redpanda>
  - <https://github.com/nubskr/walrus>
  - <https://github.com/fluvio-community/fluvio>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/smfrpc/smf`) · [data/wave6/enrich/raw/github_com_smfrpc_smf.json](../../../data/wave6/enrich/raw/github_com_smfrpc_smf.json) (enrichment confidence 0.8)

</details>
