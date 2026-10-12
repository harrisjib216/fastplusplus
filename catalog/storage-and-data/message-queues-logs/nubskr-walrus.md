# Walrus (embedded log/WAL storage engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Message queues and logs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Embeddable Rust per-topic write-ahead log engine; \~8% more unsynced writes/s than a local single-broker Kafka, tied when fsync'd.

| | |
|---|---|
| **Beats** | Kafka |
| **Claimed result** | Unsynced: Walrus avg 1,205,762 writes/s (876.22 MB/s) vs Kafka avg 1,112,120 writes/s (808.33 MB/s), \~8% higher; max 1,593,984 vs 1,424,073 writes/s. Synced/fsync'd writes: roughly tied (Walrus 4,980 vs Kafka 4,921 writes/s avg), with RocksDB slightly ahead of both at 5,222 writes/s avg |
| **Workload** | 10-thread sustained write benchmark (Walrus legacy append_for_topic() path using pwrite(), no io_uring batching) against a single Apache Kafka broker (no replication, no networking overhead; Java producer with acks=all, enable.idempotence=true, linger.ms=0, batch.size=16384, 500-1024-byte random payloads, one topic per thread) and RocksDB's WAL. Measured writes/sec and MB/s for unsynced ('no fsync') and fsync'd writes. |
| **Metric** | throughput |
| **Hardware** | Not stated in the post or README (CPU model, RAM, storage device and OS version unspecified); Walrus's default fd backend is io_uring-based, implying Linux |
| **Adoption** | 1.9k stars |
| **Last commit** | 2026-05-13 |
| **Links** | [repository](https://github.com/nubskr/walrus) · [benchmark](https://nubskr.com/2025/10/20/walrus_v0.2.0) |

## Verdict

On unstated Linux hardware, 10 threads each wrote bursts of 500-1024-byte records to their own topic for a default 120 s: Walrus through its per-record pwrite() path averaged 1,205,762 unsynced writes/s, against 1,112,120 (\~1.08x) for a Java producer (acks=all, idempotence, linger.ms=0) feeding one unreplicated Kafka broker on localhost:9092, and with fsync per write the result was 4,980 to 4,921 with RocksDB's WAL at 5,222. No CPU, disk, kernel, filesystem, Kafka version or broker flush setting is given, and the Kafka harness counts a record when send() enqueues it, not when the broker acknowledges it.

## Use it when

- One Rust process needs a durable append-only log or queue per topic (event log, job queue, local WAL), and you would otherwise run a local Kafka broker just for that.
- Many independent topics written from separate threads: writers are per topic and do not contend with each other (the benchmark used one topic per thread).
- Throughput-first ingestion that can accept a bounded loss window (FsyncSchedule::Milliseconds, default 200 ms) or no durability at all; the measured edge over Kafka exists only in that unsynced mode.
- Linux hosts that permit io_uring, if you plan to rely on the batch append/read APIs; the author says their non-io_uring fallback is roughly 5-10x slower.
- Records of roughly 0.5 KB and up; every entry carries a fixed 256-byte header, so tiny records mostly write overhead.

## Skip it when

- You need Kafka semantics or ecosystem: wire/client compatibility, consumer groups, offset-based seek or replay, time-based retention. Walrus has one consumable cursor per topic and deletes a file once every block in it has been read. On HN the author said a Kafka translation layer was dropped because Walrus is message-based, not offset-based.
- You need per-record durable throughput: with fsync on every write it measured 4,980 writes/s, a tie with Kafka (4,921) and behind RocksDB's WAL (5,222).
- You have latency SLOs: no p50/p99 latency figures are published (a gap called out in the Show HN thread); only throughput was measured.
- Linux sandboxes where io_uring_setup is blocked (AWS Fargate, Lambda, gVisor, restrictive seccomp). The background flush/cleanup thread panics at startup while Walrus::new() still returns Ok, so periodic fsync and file deletion silently stop (open issue #25).
- Windows (does not compile; the maintainer said support is not planned, issue #26), or setups that need replicated data: the distributed mode's README describes Raft for metadata only, with each segment's data held by its leader node.

## How it is fast

Each topic has one writer that puts a 256-byte rkyv-serialized header (length, owning topic, FNV-1a checksum) plus the payload into 10 MB blocks cut from sparse, preallocated 1 GB files with a single pwrite(). So the append path has no network hop, no wire protocol and, in NoFsync or Milliseconds mode, no fsync; a background thread deduplicates dirty files and fsyncs them as one io_uring batch every N ms. The newer batch_append_for_topic path submits up to 2,000 planned writes in one io_uring submission, but that path was not used in the Kafka comparison.

## Compared with alternatives

Pick Walrus when you want a library inside a Rust process rather than a broker to operate; SMF's Seastar-based write-ahead log is the only sibling of similar shape. To replace Kafka as a networked, replicated service, Redpanda (Kafka-compatible, 12-70x lower p99.99 latency), Fluvio (\~1.5x throughput) or Woodpecker (3.5x MB/s in local-FS mode) all claim larger margins than Walrus's \~8% unsynced edge.

## Integration

| | |
|---|---|
| **Form** | crate (walrus-rust on crates.io; latest published release is 0.2.0 from 2025-10-19) |
| **Dependencies** | rand 0.8, memmap2 0.9, libc, rkyv 0.7 (validation), rkyv_derive, bytecheck 0.6, tracing; io-uring 0.7 on Linux only |
| **Minimum toolchain** | Rust edition 2024, so Rust 1.85+; no rust-version declared in Cargo.toml |
| **Platforms** | Linux primary (io_uring for batch I/O and background fsync; mmap backend as alternative); non-Linux Unix code paths exist without io_uring (not benchmarked); Windows does not compile |
| **Thread safety** | Walrus is shared across threads behind Arc (the benchmark does this with 10 threads). Each topic's writer is guarded by mutexes, so appends to the same topic serialize. A single append, or a second batch, sent to a topic while a batch is in progress there returns ErrorKind::WouldBlock instead of waiting. Reader cursors sit behind a per-topic RwLock, and StrictlyAtOnce holds that lock across I/O. |
| **Drop-in for the baseline** | no |

## Gotchas

- The fd backend throws away pwrite's result (`let _ = self.file.write_at(...)` in src/wal/storage.rs), and background fsync errors are only printed. So append_for_topic can return Ok after a failed or short write, for example on a full disk.
- Debug output goes to stdout via println! on every append unless the WALRUS_QUIET env var is set. The benchmark sets WALRUS_QUIET=1, so production callers should too; even in quiet mode each check is an env-var lookup on the hot path.
- Process-wide state leaks across instances. The fsync schedule that decides O_SYNC is a OnceLock set by the first Walrus created, and the fd/mmap backend choice is a global atomic. So the v0.2.0 post's pattern of several instances with different FsyncSchedules in one process does not give each instance its own file-open behavior. Also, SyncEach on the fd backend opens files O_SYNC and still calls fsync after every append.
- Each entry costs a 256-byte header (docs/architecture.md still says 64 bytes). The header embeds the topic name and must serialize into 254 bytes, so very long topic names are rejected. The published MB/s figures count payload bytes only.

## Known shortcomings

- Only about 8% faster unsynced; with fsync it ties. Benchmark code is public but no CPU/compiler/OS is stated.
- The Kafka harness counts messages at send() enqueue, not ack, against a broker on localhost (a loopback hop exists). No latency numbers; hardware given only as 'Linux'. Not a Kafka drop-in: one cursor per topic, no offsets or consumer groups; distributed mode replicates only metadata; crates.io stuck at 0.2.0 (2025-10).
- Durability bugs: the pwrite result is discarded and fsync errors are only printed, so appends return Ok on a full disk. Where io_uring is blocked (Fargate/gVisor/seccomp) the background flush thread panics and fsync and file deletion stop silently (#25 open). No Windows (#26 wontfix). Prints to stdout per append unless WALRUS_QUIET; fsync/backend settings are process-global; 256 B header per entry (docs say 64).

## Caveats and trade-offs

First-party benchmark by the project's sole author; CPU model, RAM, and disk hardware not stated in either release post, so it falls short of Tier A despite having public benchmark code and stated OS/config; numbers are close enough (within noise) for synced writes that the throughput win is really only in the unsynced/no-fsync configuration

Single-node, embedded-in-process engine (no replication/partitioning at the time of this benchmark; distributed mode added later); benchmarked against a single Kafka broker with no replication or network hop, i.e. a best-case setup for Kafka rather than a real cluster; margin over Kafka is modest (\~8% unsynced, roughly tied when fsync'd) rather than a large multiple

## Maintenance

Active but effectively single-author (last commit 2026-05-13, MIT, \~1.9k stars) and small enough to vendor (\~4.8k lines under src/), but crates.io still serves 0.2.0 from October 2025, so the WALRUS_DATA_DIR race fix (PR #22) and the \~13% write-throughput struct-packing change (PR #24) are git-only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party release post and README tables compare against a single-broker Kafka and RocksDB's WAL. Benchmark code is public (benchmarks/multithreaded_benchmark_writes.rs, benchmarks/multithreaded_benchmark_writes_kafka.java, benchmarks/multithreaded_benchmark_writes_rocksdb.rs), but CPU model, compiler and flags are not stated, so it is C, not A.
- **Verifier notes:** All unsynced and synced numbers match the v0.2.0 post and the README tables exactly. The \~8% unsynced edge (1.084x, derived from page data) is modest, and synced writes are a tie, with RocksDB slightly ahead. The Kafka harness confirms 10 threads, acks=all and idempotence; the README confirms single broker, no replication, no network. Metadata checked: MIT, 1,933 stars, last commit 2026-05-13 (active).
- **Fields the verifier corrected:** `hardware`, `workload`
- **Pages the verifier opened:**
  - <https://nubskr.com/2025/10/20/walrus_v0.2.0>
  - <https://github.com/nubskr/walrus>
  - <https://github.com/nubskr/walrus/tree/master/benchmarks>
  - <https://github.com/nubskr/walrus/blob/master/benchmarks/multithreaded_benchmark_writes_kafka.java>
  - <https://github.com/nubskr/walrus/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/nubskr/walrus>
  - <https://github.com/nubskr/walrus/blob/master/README.md>
  - <https://github.com/nubskr/walrus/blob/master/Cargo.toml>
  - <https://github.com/nubskr/walrus/blob/master/Makefile>
  - <https://github.com/nubskr/walrus/blob/master/docs/architecture.md>
  - <https://github.com/nubskr/walrus/blob/master/src/lib.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/config.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/storage.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/block.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/paths.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/runtime/walrus.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/runtime/walrus_write.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/runtime/walrus_read.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/runtime/writer.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/runtime/background.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/runtime/allocator.rs>
  - <https://github.com/nubskr/walrus/blob/master/src/wal/runtime/topic_clean.rs>
  - <https://github.com/nubskr/walrus/blob/master/benchmarks/multithreaded_benchmark_writes.rs>
  - <https://github.com/nubskr/walrus/blob/master/benchmarks/multithreaded_benchmark_writes_kafka.java>
  - <https://github.com/nubskr/walrus/blob/master/benchmarks/multithreaded_benchmark_writes_rocksdb.rs>
  - <https://github.com/nubskr/walrus/blob/master/scripts/compare_walrus_rocksdb.py>
  - <https://github.com/nubskr/walrus/blob/master/distributed-walrus/src/bucket.rs>
  - <https://github.com/nubskr/walrus/issues?q=is%3Aissue>
  - <https://github.com/nubskr/walrus/issues/25>
  - <https://github.com/nubskr/walrus/issues/26>
  - <https://github.com/nubskr/walrus/issues/18>
  - <https://github.com/nubskr/walrus/issues/11>
  - <https://github.com/nubskr/walrus/issues/9>
  - <https://github.com/nubskr/walrus/issues/1>
  - <https://github.com/nubskr/walrus/pull/24>
  - <https://github.com/nubskr/walrus/pull/22>
  - <https://github.com/nubskr/walrus/commits/master>
  - <https://nubskr.com/2025/10/20/walrus_v0.2.0>
  - <https://nubskr.com/2025/10/06/walrus>
  - <https://crates.io/api/v1/crates/walrus-rust>
  - <https://hn.algolia.com/api/v1/search?query=nubskr%20walrus>
  - <https://news.ycombinator.com/item?id=46108557>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/nubskr/walrus`) · [data/wave6/enrich/raw/github_com_nubskr_walrus.json](../../../data/wave6/enrich/raw/github_com_nubskr_walrus.json) (enrichment confidence 0.8)

</details>
