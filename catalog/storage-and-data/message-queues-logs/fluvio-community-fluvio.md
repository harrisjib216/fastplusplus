# Fluvio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust distributed streaming broker with a Kafka-style topic/partition log and in-broker WASM transforms; vendor bench shows 1.4-1.56x Kafka producer throughput.

| | |
|---|---|
| **Beats** | Kafka |
| **Claimed result** | Page summary: "1.5 times the throughput and 20 to 38 times better latency" than Kafka at default configs. M1 Max: 76,923 rec/s / 394.6 MB/s / 5.8ms P99 (Fluvio) vs 49,346 rec/s / 240.95 MB/s / 132ms P99 (Kafka); EC2 c7g.xlarge: 37,195 rec/s / 190.8 MB/s / 10.8ms P99 (Fluvio) vs 26,780 rec/s / 130.77 MB/s / 419ms P99 (Kafka). Per machine: 1.56x (M1) and 1.39x (EC2) throughput, 22.8x and 38.8x lower P99 (derived from page data). |
| **Workload** | Produce 200,000 records at 5120 bytes each via kafka-producer-perf-test.sh vs `fluvio benchmark producer`, run on both a MacBook Pro M1 Max (32GB RAM) and an AWS EC2 c7g.xlarge (Graviton3, 4 vCPU/8GB RAM); measured records/sec, MB/sec throughput, and P99 latency. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro 18, Apple M1 Max, 32GB RAM; AWS EC2 c7g.xlarge (ARM64 Graviton, 4 vCPU, 8GB RAM, Elastic Block Storage) |
| **Adoption** | 5.3k stars |
| **Last commit** | 2026-05-14 |
| **Links** | [repository](https://github.com/fluvio-community/fluvio) · [benchmark](https://infinyon.com/blog/2025/02/kafka-vs-fluvio-bench/) |

## Verdict

In InfinyOn's own Feb 2025 post, kafka-producer-perf-test.sh and `fluvio benchmark producer` each sent 200,000 5,120-byte records to a single local broker at default configs with unstated 'latest' Kafka/JVM/Fluvio versions. Fluvio reached 394.6 vs 240.95 MB/s (1.56x) on an M1 Max MacBook Pro and 190.8 vs 130.77 MB/s (1.39x) on an EC2 c7g.xlarge (Graviton, 4 vCPU). The quoted P99 latencies (5.8 vs 132 ms and 10.8 vs 419 ms) come from two tools that time different intervals, and Kafka's figures include JVM warm-up.

## Use it when

- Greenfield streaming where you control both producers and consumers and do not need the Kafka wire protocol or its ecosystem
- Edge or small-footprint nodes (ARM boards, Graviton, Apple Silicon) where a JVM broker's roughly 1 GB idle memory is too much; the installer ships static musl builds for Linux x86_64/aarch64 plus armv7/arm
- Rust services that want an async client crate and in-broker WASM filtering/mapping instead of running a separate stream processor
- Single-partition producer ingest of medium (\~5 KB) records, where default configs reportedly gave 1.4-1.56x Kafka's MB/s

## Skip it when

- Existing Kafka estates: there is no Kafka wire protocol (a Kafka-protocol implementation was discontinued, and requests #3870 and #4259 closed as stale), so Kafka clients, Streams, Connect and tooling do not carry over
- If you need a trustworthy tail-latency comparison: the vendor's 20-38x P99 figures compare different measured intervals (see gotchas)
- Replicated production clusters sized from these numbers: the only published comparison is single-node, one partition, RF=1 on a laptop and a 4-vCPU VM, and no promised bare-metal or RF=3 follow-up appears on the vendor blog
- Long-term support needs: the last stable release is v0.18.1 (2025-07-04), later commits are mostly dependency bumps, and the README says installs temporarily need the dev FVM channel while builds move from InfinyOn to fluvio-community
- Native Windows servers: the README recommends WSL2

## How it is fast

The design is Kafka-style: each SPU appends encoded record batches to segment files (1 GiB default) with a memory-mapped offset index, and unfiltered consumer fetches are served as file slices through sendfile(2) zero-copy (future-aio zero_copy.rs, Linux and macOS). Producers batch client-side (16 KiB batches, 0 ms linger by default, optional gzip/lz4/snappy/zstd). The vendor attributes the gap to Rust with no JVM or garbage collector rather than to a new algorithm, and the post also reports about 50 MB idle RAM versus about 1 GB for Kafka.

## Compared with alternatives

Choose Fluvio over Redpanda when you want a small Rust broker with in-broker WASM transforms and do not need Kafka API compatibility; Redpanda speaks the Kafka API and publishes far more detailed tail-latency data. Choose it over Walrus or Woodpecker when you need a networked multi-client broker with partitions, replication and consumers, not an embedded WAL or a log-storage layer.

## Integration

| | |
|---|---|
| **Form** | crate (client `fluvio` on crates.io) plus prebuilt broker/CLI binaries installed via fvm |
| **Dependencies** | tokio (async-std-based fluvio-future before June 2025), wasmtime for SmartModules, rustls or openssl for TLS, nix/libc; Kubernetes optional (local cluster mode exists) |
| **Minimum toolchain** | Workspace pins Rust 1.93.0 via rust-toolchain.toml and uses edition 2024 (so Rust 1.85 or newer); the crate declares no rust-version |
| **Platforms** | Linux x86_64/aarch64 (musl), armv7/arm gnueabihf, macOS; Windows via WSL2 recommended; sendfile zero-copy path only on Linux and macOS |
| **Thread safety** | Not documented in the files read; the client is async (Tokio) and the benchmark shares a TopicProducerPool across tasks |
| **Drop-in for the baseline** | partial — same topic/partition/offset model and a Kafka-like batch format, but a different wire protocol, clients and ops tooling; Kafka interop only through connectors |

## Gotchas

- The latency reported by `fluvio benchmark` comes from the producer callback, which records `created_at.elapsed()` before the produce request goes to the SPU (partition_producer.rs, same at the Jan-2025 commit 38535375 that the post used). It is therefore per-batch batching/queueing time and excludes the network round trip and broker ack, while kafka-producer-perf-test times each record from send() to its ack callback. The headline 5.8 ms vs 132 ms P99 is not like-for-like.
- Storage flush tuning is effectively dead code: FlushPolicy (flush_write_count/flush_idle_msec) is marked unused, and write_batch does a blocking write on the async task followed by an async flush(). No fsync, sync_data or sync_all appears in the storage crate files read, so durability rests on the page cache plus replication.
- Running a SmartModule on the consume path turns off zero-copy: batches are read into memory, run through WASM, then re-encoded (stream_fetch.rs).
- The benchmark tool builds every record in memory before sending (issue #4464, open), so large --num-records runs can exhaust RAM. File-descriptor leaks on topic delete with replicas (#4465) and SPU thread growth under long runs (#2215, open) are also reported.

## Known shortcomings

- Kafka and Fluvio were driven by different load generators on localhost, so the \~1.5x (1.56x on M1, 1.39x on EC2) is not a like-for-like comparison.
- The P99 latency comparison is not like-for-like: Fluvio's bench measures batch create-to-dispatch before send, while Kafka's perf test measures per-record send-to-ack. Vendor-only, 1 node, 1 partition, RF=1 on a laptop and a 4-vCPU VM; the promised bare-metal/RF=3 follow-up never appeared. No Kafka wire protocol (connectors only), so not a drop-in.
- Storage: the FlushPolicy config is unused and the storage crate never fsyncs (relies on page cache and replication). Thin maintenance: last stable v0.18.1 in 2025-07, mostly dependabot since. The bench tool builds all records in RAM (#4464); fd leak (#4465) and thread growth (#2215) open.

## Caveats and trade-offs

First-party vendor (InfinyOn, makers of Fluvio) blog post; Kafka, Fluvio, Java and Rust versions not stated (only 'latest'); no compiler flags or JVM tuning; default configs only; single-node localhost broker; different load generators (kafka-producer-perf-test.sh vs `fluvio benchmark producer`); page mentions 'several trials' until performance stabilized but gives no error bars; no public benchmark repo or CI artifact beyond the built-in fluvio-benchmark crate

Fluvio is a Rust/WebAssembly streaming engine following Kafka's conceptual model but a different implementation and ecosystem (no JVM/GC pause overhead); default-config comparison, both systems left largely untuned; Kafka's JVM warm-up period included in results, which understates Kafka's steady-state numbers somewhat

## Maintenance

Apache-2.0 with about 5.3k stars and commits through May 2026, but effectively in community maintenance after moving from InfinyOn to fluvio-community: the last stable release is v0.18.1 (July 2025) and recent commits are mainly dependabot and clippy fixes. It is usable as a crate plus prebuilt binaries, not something you vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party InfinyOn blog (Feb 11, 2025) with a head-to-head Kafka vs Fluvio producer test on named CPUs (M1 Max, Graviton c7g.xlarge) and exact CLI commands, but no Kafka/Fluvio/JVM/Rust versions, no compiler flags, and no published harness repo beyond the built-in `fluvio benchmark` CLI (crates/fluvio-benchmark), so it falls short of A.
- **Verifier notes:** All numbers match the page exactly; the page's '1.5x' is its own rounded summary (derived per-machine ratios are 1.56x and 1.39x). The '10-core' detail in hardware is not on the page, so it was removed. Metadata checked: Apache-2.0, 5,258 stars, last default-branch commit 2026-05-14 (active), not a fork or archived.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://infinyon.com/blog/2025/02/kafka-vs-fluvio-bench/>
  - <https://github.com/fluvio-community/fluvio>
- **Sources the enricher read:**
  - <https://github.com/fluvio-community/fluvio>
  - <https://github.com/fluvio-community/fluvio/blob/master/README.md>
  - <https://github.com/fluvio-community/fluvio/blob/master/Cargo.toml>
  - <https://github.com/fluvio-community/fluvio/blob/master/rust-toolchain.toml>
  - <https://github.com/fluvio-community/fluvio/blob/master/install.sh>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-types/src/defaults.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-storage/src/config.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-storage/src/mut_records.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-storage/src/records.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-storage/src/segment.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-storage/src/segments.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-storage/src/replica.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-storage/src/mut_index.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-storage/Cargo.toml>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-benchmark/src/config/mod.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-benchmark/src/producer_worker.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-benchmark/src/stats_collector.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio/src/producer/config.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio/src/producer/partition_producer.rs>
  - <https://github.com/fluvio-community/fluvio/blob/38535375/crates/fluvio/src/producer/partition_producer.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio/src/producer/memory_batch.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio/src/producer/accumulator.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-spu/src/services/public/stream_fetch.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-spu/src/services/public/fetch_handler.rs>
  - <https://github.com/fluvio-community/fluvio/blob/master/crates/fluvio-spu/src/services/public/produce_handler.rs>
  - <https://github.com/fluvio-community/fluvio/releases>
  - <https://github.com/fluvio-community/fluvio/commits/master>
  - <https://github.com/fluvio-community/fluvio/issues/4259>
  - <https://github.com/fluvio-community/fluvio/issues/3870>
  - <https://github.com/fluvio-community/fluvio/issues/4465>
  - <https://github.com/fluvio-community/fluvio/issues/2215>
  - <https://github.com/fluvio-community/fluvio/issues/4464>
  - <https://github.com/fluvio-community/future-aio/blob/master/src/zero_copy.rs>
  - <https://raw.githubusercontent.com/apache/kafka/3.9/tools/src/main/java/org/apache/kafka/tools/ProducerPerformance.java>
  - <https://crates.io/api/v1/crates/fluvio>
  - <https://crates.io/api/v1/crates/fluvio-future>
  - <https://infinyon.com/blog/2025/02/kafka-vs-fluvio-bench/>
  - <https://infinyon.com/blog/>
  - <https://www.fluvio.io/docs/fluvio/concepts/architecture/overview>
  - <https://hn.algolia.com/api/v1/search?query=fluvio&tags=story>
  - <https://news.ycombinator.com/item?id=43027188>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/fluvio-community/fluvio`) · [data/wave6/enrich/raw/github_com_fluvio_community_fluvio.json](../../../data/wave6/enrich/raw/github_com_fluvio_community_fluvio.json) (enrichment confidence 0.5)

</details>
