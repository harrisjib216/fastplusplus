# Storage and data

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

Embedded key-value stores, caches, indexes, probabilistic filters, columnar engines and message logs measured against RocksDB, Redis, Kafka and others.

**234 entries in 7 categories:** 24 tier A · 77 tier B · 129 tier C · 4 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [Caches](caches/README.md) | 39 | 1 | 17 | 21 | 0 | memcached, Redis, LRU baselines the benchmark names |
| [Columnar analytics](columnar-analytics/README.md) | 36 | 4 | 12 | 20 | 0 | Apache Arrow, DuckDB, ClickHouse, pandas, polars |
| [Database client drivers](database-client-drivers/README.md) | 1 | 0 | 0 | 1 | 0 | QtSql with the QMYSQL driver |
| [Embedded key-value stores](embedded-kv/README.md) | 52 | 4 | 13 | 32 | 3 | RocksDB, LevelDB, LMDB, SQLite |
| [Indexes](indexes/README.md) | 34 | 3 | 20 | 11 | 0 | B-tree/LSM in the above; learned index baselines |
| [Message queues and logs](message-queues-logs/README.md) | 29 | 2 | 2 | 25 | 0 | Kafka, NATS, ZeroMQ |
| [Probabilistic filters](probabilistic-filters/README.md) | 43 | 10 | 13 | 19 | 1 | Bloom filter, cuckoo filter, xor filter |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**RocksDB Ribbon Filter**](probabilistic-filters/facebook-rocksdb.md) | RocksDB's built-in Ribbon SST filter: same FP rate as its Bloom filter in about 30% less memory, at 3-4x CPU. | [Probabilistic filters](probabilistic-filters/README.md) | **A** | C++ | Apache-2.0 OR GPL-2.0 | 🟢 active |
| 2 | [**NATS JetStream**](message-queues-logs/nats-io-nats-server.md) | CNCF Go messaging server whose built-in JetStream persistence showed \~14x lower median latency than Kafka at light load. | [Message queues and logs](message-queues-logs/README.md) | **A** | Go | Apache-2.0 | 🟢 active |
| 3 | [**TidesDB**](indexes/tidesdb-tidesdb.md) | Embeddable transactional LSM key-value engine in C; the author's benchmark shows 4-5x RocksDB's iterator-seek throughput at about 3.5x the memory. | [Indexes](indexes/README.md) | **A** | C | MPL-2.0 | 🟢 active |
| 4 | [**ZoneTree**](embedded-kv/koculu-zonetree.md) | Pure-C# LSM-tree ordered key-value engine for .NET; beats RocksDB (via RocksDbSharp) and SQLite on its own indexed profile-store benchmark. | [Embedded key-value stores](embedded-kv/README.md) | **A** | C# | MIT | 🟢 active |
| 5 | [**Xor Filter (xor_singleheader)**](probabilistic-filters/fastfilter-xor-singleheader.md) | Header-only C99 xor and binary fuse filters: static membership filters with fewer bits/key and faster lookups than Bloom/cuckoo. | [Probabilistic filters](probabilistic-filters/README.md) | **A** | C | Apache-2.0 | 🟢 active |
| 6 | [**fastfilter (hexops)**](probabilistic-filters/code-hexops-org-hexops-fastfilter.md) | Zig binary fuse and xor filters; binary fuse builds 1.7-3.8x faster than xor, with smaller filters and equal lookups. | [Probabilistic filters](probabilistic-filters/README.md) | **A** | Zig | MIT OR Apache-2.0 | 🟢 active |
| 7 | [**TurboKV**](embedded-kv/kingroryg-turbokv.md) | Async (Tokio) Rust LSM key-value store whose unsynced-WAL mode acknowledges single-caller writes 2-4x faster than fjall 2.11. | [Embedded key-value stores](embedded-kv/README.md) | **A** | Rust | Apache-2.0 | 🟢 active |
| 8 | [**ALP (Adaptive Lossless Floating-Point Compression)**](columnar-analytics/cwida-alp.md) | Reference C++ primitives for ALP, a lossless double/float column encoding that decodes 17-66x faster than Zstd, Gorilla, Chimp and Patas. | [Columnar analytics](columnar-analytics/README.md) | **A** | C++ | MIT | 🟢 active |
| 9 | [**indexset**](indexes/lucidarium-systems-indexset.md) | Rust two-level B-tree (sorted Vec leaves) with positional indexing; beats std BTreeMap/BTreeSet on scans and Mutex-wrapped std under contention. | [Indexes](indexes/README.md) | **A** | Rust | Apache-2.0 OR MIT | 🟢 active |
| 10 | [**Minarrow**](columnar-analytics/spacecell-minarrow.md) | Lean Rust Apache Arrow implementation with enum-dispatched typed arrays; about 1.7x faster than arrow-rs on a 1,000-element sum microbenchmark. | [Columnar analytics](columnar-analytics/README.md) | **A** | Rust | Apache-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
