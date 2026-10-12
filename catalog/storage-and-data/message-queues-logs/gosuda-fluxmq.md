# FluxMQ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Single-binary Rust broker that speaks the Kafka wire protocol; claims \~29% more producer msg/s than Kafka 3.9.

| | |
|---|---|
| **Beats** | Apache Kafka |
| **Claimed result** | 476K msg/sec average (+28.6%) and 554K msg/sec peak (+49.6%) vs Apache Kafka at 370K msg/sec in the page's comparison table (results dated 2025-11-24); 0.002 ms vs 0.003 ms latency (-33.3%) |
| **Workload** | Kafka-wire-protocol-compatible broker throughput/latency test using Java Kafka client tooling; exact record size/partition count not documented |
| **Metric** | throughput |
| **Compiler and flags** | RUSTFLAGS="-C target-cpu=native -C opt-level=3", cargo build --release (from install instructions; not confirmed as the exact flags used for the cited benchmark numbers) |
| **Adoption** | 8 stars |
| **Last commit** | 2026-03-20 |
| **Links** | [repository](https://github.com/gosuda/fluxmq) · [benchmark](https://github.com/gosuda/fluxmq/blob/main/docs/PERFORMANCE.md) |

## Verdict

docs/PERFORMANCE.md (dated 2025-11-24) reports 476K msg/s average and 554K peak for FluxMQ vs 370K for Apache Kafka. In the repo harness, that comes from 4 Java producer threads (kafka-clients 4.1.0) sending 100K messages of about 740 bytes with acks=1, 128 KB batches, linger 1 ms and no compression, which is only about 0.2 s of timed work. The harness's Kafka side is 3.9.0 in ZooKeeper mode with 3 partitions, 8 network / 16 IO threads, logs in /tmp and RF 1, but the page never ties the 370K figure to that setup. No CPU or OS is stated (an older doc says 'Apple Silicon M-series or Intel x86_64, 16GB+'), and no raw results are committed. The 0.002 ms 'latency' is duration divided by message count, not per-message ack latency. FluxMQ was storing messages only in heap memory while Kafka was writing its log, so this is not a like-for-like broker comparison.

## Use it when

- Local development or CI as a throwaway Kafka-protocol endpoint that starts in under a second, where losing every message on restart is acceptable
- Studying how to implement the Kafka wire protocol (record-batch parsing, ApiVersions negotiation, consumer-group coordinator) in Rust
- Producer-side load experiments with acks=1 against a single node, where only the client-to-broker protocol path matters
- Environments with no JVM, where a small single binary matters more than retention, durability or ecosystem

## Skip it when

- Any workload that needs the data kept. Produced messages live only in process memory, and nothing on the produce path writes them to disk, so a restart or crash loses everything
- Producers using acks=0. Both Kafka produce paths in the broker return before parsing or storing the batch when acks=0, so those messages are silently dropped (this is the config behind the docs' 601K msg/s 'MegaBatch' figure)
- Long-running or high-volume topics. There is no retention or eviction on the in-memory Vec, so RSS grows with every produced byte and the 100-400 MB memory figures only hold for short runs
- Multi-broker HA. With replication on, the leader produce path only logs a debug line ('In a full implementation, we'd wait for replication acknowledgments'), and the Java-client produce path in server.rs skips it entirely
- Production use in general: one contributor (37 commits), 8 stars, no issues filed, no GitHub releases, no HN or third-party discussion found

## How it is fast

At HEAD, the produce path parses the record batch and appends the messages to a per-partition Vec&lt;(Offset, Message)&gt;. That Vec sits behind a parking_lot RwLock in a DashMap keyed by (topic, partition), and offsets are reserved with a Relaxed atomic fetch_add. No disk write, fsync or replication wait happens before the ack. The docs credit the gains to mmap segments with madvise(SEQUENTIAL/WILLNEED/HUGEPAGE), MS_ASYNC msync, 'SIMD' copies (really ptr::copy_nonoverlapping plus target-cpu=native) and zero-copy sendfile/io_uring. In the source I read, the mmap tier is only read on fetch, the disk-persistence Append command is never enqueued, and the io_uring/sendfile handler is marked dead_code. The measured speed therefore mostly reflects in-heap appends, plus mimalloc, fat LTO, codegen-units=1 and pipelined request handling.

## Compared with alternatives

Redpanda is the catalogued Kafka-API alternative with fsync'd Raft storage and a production track record. Pick FluxMQ over it only for an ephemeral, in-memory Kafka-protocol stand-in or to study the codebase. Woodpecker (a durable log with object-storage backing) and Zenoh (a different pub/sub protocol) are not Kafka-wire drop-ins, so FluxMQ is only relevant among these when unmodified Kafka clients must connect.

## Integration

| | |
|---|---|
| **Form** | Standalone server binary built from a Cargo workspace (core/). The crates.io 'fluxmq' crate is stale at 0.1.0 from 2025-09, while the repo is at 0.4.1. |
| **Dependencies** | tokio, dashmap, parking_lot, crossbeam, flume, memmap2, crc32fast/crc32c, lz4_flex, snap, flate2, zstd, rustls/tokio-rustls, mimalloc (default feature), optional tikv-jemallocator; io-uring crate on Linux, mach on macOS, winapi on Windows |
| **Minimum toolchain** | The README says Rust 1.70+, but the workspace depends on rand 0.10.0, whose crates.io rust_version is 1.85 (edition 2024), so Rust 1.85+ in practice. Edition 2021. |
| **Platforms** | The release CI matrix builds x86_64 Linux (musl), x86_64 Windows (MSVC) and x86_64 macOS. .cargo/config.toml forces target-cpu=native for x86_64/aarch64 Linux and macOS and for x86_64 Windows. The io-uring feature needs Linux 5.1+ according to the docs. aarch64 builds from source are implied, not tested in CI. |
| **Thread safety** | The broker serves many concurrent client connections on tokio, and per-partition state is guarded by DashMap plus RwLock. From reading the code, the offset is reserved before the write lock is taken, so concurrent producers to one partition could push batches out of offset order, which the binary-search fetch assumes cannot happen. Not documented or tested upstream. |
| **Drop-in for the baseline** | partial — unmodified Kafka Java and Python clients connect on 9092 and can produce, fetch and use consumer groups, but there is no durable log, no retention, and no working replication. acks=0 data is discarded, protocol versions top out around the Kafka 2.8 era (Produce v7, Fetch v11), and Kafka's admin tooling, Connect and Streams are out of scope. |

## Gotchas

- acks=0 is a silent no-op: the server returns without storing the batch, so fire-and-forget benchmarks look fast because nothing is written
- --data-dir is parsed and logged, but MessageHandler builds its storage with a hard-coded HybridStorage::new("./data"), and --recovery-mode reloads directories that the produce path does not appear to write
- The release profile sets panic = "abort", so any panic in a request handler kills the whole broker rather than one connection
- The repo's .cargo/config.toml bakes in target-cpu=native, so a binary built on one machine may crash with SIGILL on an older CPU. The README install URL and support links still point to github.com/yourusername/fluxmq

## Known shortcomings

- Not a durable broker: the produce path stores messages only in an in-memory Vec and never sends the disk-write command, so all data is lost on restart, while Kafka persists to its log; acks=0 returns before storing and silently drops messages (the docs' 601K MegaBatch figure used acks=0). Replication is a stub that only logs; no retention, so RAM grows without bound. The bench (4 threads, 100K \~740 B messages, \~0.2 s timed) isn't tied to the Kafka 3.9 harness run; no hardware; 'latency' is time divided by message count. io_uring/sendfile handler is dead code; --data-dir is ignored; panic=abort and target-cpu=native baked in; real MSRV is Rust 1.85 (README says 1.70). One author, 8 stars, no releases.

## Caveats and trade-offs

No CPU/hardware is stated for the cited numbers. The README is heavily marketing-styled. The repo's harness installs Kafka 3.9.0 (benchmark-suite/setup/install_kafka.sh), but the page never says which Kafka version, tuning or dataset produced the 370K figure, and no raw results are committed. The FluxMQ-tuned client config uses acks=0, lz4, 1MB batches and linger 15ms. The 0.002 ms 'latency' looks like amortized per-message time, not end-to-end latency. Treat as an unverified first-party claim.

Single binary, no ZooKeeper/JVM dependency; Kafka protocol compatibility is partial (20 APIs implemented); very young, low-adoption project with placeholder repo URL fields in its own README

## Maintenance

Active, single-author project (last commit 2026-03-20, MIT) that is easy to build and run but not usable where data must survive: treat it as experimental and verify durability yourself before relying on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/PERFORMANCE.md (results dated 2025-11-24) shows 476K avg and 554K peak msg/s vs Apache Kafka at 370K msg/s (+28.6% / +49.6%), and 0.002 vs 0.003 ms latency. A comparison harness exists (benchmark-suite/runners/run_comparison.sh, fluxmq-java-tests MultiThreadBenchmark), but no CPU, record size or partition count is given, and the Kafka version is not tied to the numbers. That is first-party with partial methodology, so C.
- **Verifier notes:** Language mismatch: this came from a search filtered to C++, but FluxMQ is a Rust Kafka-protocol broker. Metadata checks out (MIT, 8 stars, not a fork, last commit 2026-03-20, active). The win is small (+29%) and poorly documented but real as claimed, so C stands.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/gosuda/fluxmq>
  - <https://github.com/gosuda/fluxmq/blob/main/docs/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/gosuda/fluxmq/main/docs/PERFORMANCE.md>
  - <https://raw.githubusercontent.com/gosuda/fluxmq/main/README.md>
  - <https://raw.githubusercontent.com/gosuda/fluxmq/main/benchmark-suite/README.md>
  - <https://raw.githubusercontent.com/gosuda/fluxmq/main/benchmark-suite/runners/run_comparison.sh>
  - <https://raw.githubusercontent.com/gosuda/fluxmq/main/benchmark-suite/setup/install_kafka.sh>
- **Sources the enricher read:**
  - <https://github.com/gosuda/fluxmq>
  - <https://github.com/gosuda/fluxmq/blob/main/README.md>
  - <https://github.com/gosuda/fluxmq/blob/main/docs/PERFORMANCE.md>
  - <https://github.com/gosuda/fluxmq/blob/main/Cargo.toml>
  - <https://github.com/gosuda/fluxmq/blob/main/core/Cargo.toml>
  - <https://github.com/gosuda/fluxmq/blob/main/.cargo/config.toml>
  - <https://github.com/gosuda/fluxmq/blob/main/.github/workflows/release.yml>
  - <https://github.com/gosuda/fluxmq/blob/main/benchmark-suite/runners/run_comparison.sh>
  - <https://github.com/gosuda/fluxmq/blob/main/benchmark-suite/setup/install_kafka.sh>
  - <https://github.com/gosuda/fluxmq/blob/main/benchmark-suite/setup/configure_kafka.sh>
  - <https://github.com/gosuda/fluxmq/blob/main/benchmark-suite/README.md>
  - <https://github.com/gosuda/fluxmq/blob/main/fluxmq-java-tests/BENCHMARK_RULES.md>
  - <https://github.com/gosuda/fluxmq/blob/main/fluxmq-java-tests/pom.xml>
  - <https://github.com/gosuda/fluxmq/blob/main/fluxmq-java-tests/src/main/java/com/fluxmq/tests/MultiThreadBenchmark.java>
  - <https://github.com/gosuda/fluxmq/blob/main/fluxmq-java-tests/src/main/java/com/fluxmq/tests/ComprehensiveBenchmark.java>
  - <https://github.com/gosuda/fluxmq/blob/main/core/src/storage/mod.rs>
  - <https://github.com/gosuda/fluxmq/blob/main/core/src/broker/server.rs>
  - <https://github.com/gosuda/fluxmq/blob/main/core/src/broker/handler.rs>
  - <https://github.com/gosuda/fluxmq/blob/main/core/src/main.rs>
  - <https://github.com/gosuda/fluxmq/blob/main/core/src/performance/mod.rs>
  - <https://github.com/gosuda/fluxmq/blob/main/core/src/performance/mmap_storage.rs>
  - <https://github.com/gosuda/fluxmq/blob/main/core/src/protocol/kafka/api_versions.rs>
  - <https://github.com/gosuda/fluxmq/blob/main/core/src/replication/mod.rs>
  - <https://github.com/gosuda/fluxmq/blob/main/core/PERFORMANCE_BENCHMARK_RESULTS.md>
  - <https://github.com/gosuda/fluxmq/blob/main/docs/ARCHITECTURE.md>
  - <https://github.com/gosuda/fluxmq/commits/main>
  - <https://github.com/gosuda/fluxmq/issues>
  - <https://github.com/gosuda/fluxmq/tags>
  - <https://crates.io/api/v1/crates/fluxmq>
  - <https://crates.io/api/v1/crates/rand/0.10.0>
  - <https://crates.io/api/v1/crates/tokio/1.50.0>
  - <https://hn.algolia.com/api/v1/search?query=fluxmq&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/gosuda/fluxmq`) · [data/wave6/enrich/raw/github_com_gosuda_fluxmq.json](../../../data/wave6/enrich/raw/github_com_gosuda_fluxmq.json) (enrichment confidence 0.7)

</details>
