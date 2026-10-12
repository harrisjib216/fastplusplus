# Embedded key-value stores

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md)</sub>

**What these beat:** RocksDB, LevelDB, LMDB, SQLite  
**52 entries:** 4 tier A · 13 tier B · 32 tier C · 3 tier D · 42 copyable, 10 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**ZoneTree**](koculu-zonetree.md) | Pure-C# LSM-tree ordered key-value engine for .NET; beats RocksDB (via RocksDbSharp) and SQLite on its own indexed profile-store benchmark. | **A** | C# | MIT | 🟢 active |
| 2 | [**TurboKV**](kingroryg-turbokv.md) | Async (Tokio) Rust LSM key-value store whose unsynced-WAL mode acknowledges single-caller writes 2-4x faster than fjall 2.11. | **A** | Rust | Apache-2.0 | 🟢 active |
| 3 | [**PsiTri (arbtrie)**](gofractally-arbtrie.md) | C++20 embedded transactional KV store (radix trie, node-level COW) with a RocksDB-API shim; 1.6-3x RocksDB on bank transfers. | **A** | C++ | MIT | 🟢 active |
| 4 | [**mpedb**](punnerud-mpedb.md) | Rust embedded SQL database (mmap'd copy-on-write B+tree, MVCC, sqlite3 C-API shim) that beats SQLite on in-process point operations. | **A** | Rust | LicenseRef-mpedb-1.0… (study only) | 🟢 active |
| 5 | [**F2 (FASTER v2)**](microsoft-faster.md) | Microsoft's two-tier hash-and-log KV store for skewed, larger-than-memory point workloads; its paper reports \~11.8x RocksDB throughput at 10% memory. | **B** | C++ | MIT | 🟢 active |
| 6 | [**LMDB**](lmdb-lmdb.md) | Memory-mapped copy-on-write B+tree key-value store in C; 4.6-8.8x faster reads than RocksDB in redb's harness. | **B** | C | OLDAP-2.8 | 🟢 active |
| 7 | [**SplinterDB**](vmware-splinterdb.md) | Embedded C key-value store for NVMe SSDs; paper reports 6-10x RocksDB insert throughput and 2-2.6x point-query throughput. | **B** | C | Apache-2.0 | 🟢 active |
| 8 | [**KVell**](blepers-kvell.md) | SOSP'19 research key-value store for NVMe/Optane SSDs that has no LSM compaction; 2-8x RocksDB throughput on YCSB point workloads. | **B** | C | MIT | 🟢 active |
| 9 | [**ArceKV (ElasticLSM + Arce)**](ntu-siqiang-group-arcekv.md) | RocksDB fork whose workload-driven compaction and write-stall policy (Arce) beats RocksDB leveling when read/write mixes shift. | **B** | C++ | GPL-2.0 (GitHub-detected… | 🟢 active |
| 10 | [**TreeLine**](mitdbg-treeline.md) | Update-in-place key-value store for NVMe SSDs with record caching and page grouping; beats RocksDB on read-heavy, skewed, scan YCSB. | **B** | C++ | MIT | 🟡 stale |
| 11 | [**DobLIX**](ah89-doblix.md) | Research RocksDB fork replacing the SST index with a block-aware learned string index; paper: 2.21x read-only throughput vs RocksDB. | **B** | C++ | BSD-3-Clause (RocksDB… | 🟡 stale |
| 12 | [**PebblesDB**](utsaslab-pebblesdb.md) | LevelDB-API embedded KV store on a Fragmented LSM tree; several times RocksDB's random-write throughput with less write IO. | **B** | C++ | BSD-3-Clause | 🔴 abandoned |
| 13 | [**HyperLevelDB**](rescrv-hyperleveldb.md) | HyperDex's LevelDB 1.17 fork with parallel writers and cheaper compaction; about 3.4x faster bulk writes than LevelDB, but slower reads. | **B** | C++ | BSD-3-Clause | 🔴 abandoned |
| 14 | [**SpanDB**](spandb-spandb.md) | Modified RocksDB 6.x that writes WAL and top LSM levels to raw SPDK NVMe; up to 8.8x write throughput. | **B** | C++ | GPL-2.0 | 🔴 abandoned |
| 15 | [**MatrixKV**](pds-lab-matrixkv.md) | RocksDB 5.18 fork that moves L0 into Optane persistent memory with fine-grained column compaction; 3.6x NVM-assisted RocksDB random-write throughput. | **B** | C++ | GPL-2.0 OR Apache-2.0 | 🔴 abandoned |
| 16 | [**Nova-LSM**](haoyuhuang-novalsm.md) | LevelDB-based LSM KV server split into RDMA-linked compute and storage parts; beats LevelDB/RocksDB under skewed access. | **B** | C++ | BSD-3-Clause | 🔴 abandoned |
| 17 | [**BVLSM**](paper-bvlsm.md) | Research RocksDB variant that splits big values out at WAL-write time. Paper reports 7.6x RocksDB random-write throughput at 64KB. | **B** | C++ | no license (study only) | ⚪ unknown |
| 18 | [**LevelDB**](google-leveldb.md) | Google's embedded ordered key-value LSM store; 10-17x SQLite3's write and scan rates in its 2011 benchmark. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 19 | [**RocksDB integrated BlobDB**](paper-rocksdb-integrated-blobdb.md) | RocksDB's built-in key-value separation: large values go to blob files, cutting compaction write amp versus stock leveled RocksDB. | **C** | C++ | Apache-2.0 OR GPL-2.0 | 🟢 active |
| 20 | [**Badger (BadgerDB)**](dgraph-io-badger.md) | Pure-Go embedded LSM key-value store using WiscKey key-value separation; 3.7x lower random-read latency than RocksDB in Dgraph's 2017 test. | **C** | Go | Apache-2.0 | 🟢 active |
| 21 | [**Pebble (CockroachDB storage engine)**](cockroachdb-pebble.md) | Go LSM key-value store that replaced RocksDB inside CockroachDB; meets or beats RocksDB on YCSB in vendor benchmarks. | **C** | Go | BSD-3-Clause | 🟢 active |
| 22 | [**UnQLite**](symisc-unqlite.md) | Single-file embedded C key/value and JSON document store (linear hashing); faster than SQLite only for point lookups in one informal Python test. | **C** | C | BSD-2-Clause | 🟢 active |
| 23 | [**Pogreb**](akrylysov-pogreb.md) | Pure-Go embedded key-value store with an on-disk hash index; roughly 10-23x goleveldb random-lookup throughput in the author's chart. | **C** | Go | Apache-2.0 | 🟢 active |
| 24 | [**Reindexer**](restream-reindexer.md) | Embeddable in-memory document database (C++ core, Go API) with secondary and full-text indexes; first-party benchmarks show 3-6x SQLite on indexed reads. | **C** | C++ | Apache-2.0 | 🟢 active |
| 25 | [**SurrealKV**](surrealdb-surrealkv.md) | SurrealDB's pure-Rust async LSM key-value engine with OCC transactions; vendor benchmark shows \~3x RocksDB fsync'd write throughput. | **C** | Rust | Apache-2.0 | 🟢 active |
| 26 | [**Titan (RocksDB plugin)**](tikv-titan.md) | RocksDB plugin that moves large values into separate blob files (WiscKey-style) to cut write amplification versus plain RocksDB. | **C** | C++ | Apache-2.0 | 🟢 active |
| 27 | [**UnisonDB**](ankur-anand-unisondb.md) | Go KV database that puts a WAL and memtable in front of LMDB; about 3x LMDB's SET throughput (first-party). | **C** | Go | Apache-2.0 | 🟢 active |
| 28 | [**DoltLite**](dolthub-doltlite.md) | SQLite fork with a prolly-tree storage engine that adds Git-style branch, merge and diff; 1.1-2.9x slower than SQLite, not faster. | **C** | C | Apache-2.0 | 🟢 active |
| 29 | [**CacheAdvance**](dfed-cacheadvance.md) | Size-capped append-only Swift log file (optional ring-buffer eviction); appends far faster than per-row-committed SQLite inserts. | **C** | Swift | Apache-2.0 | 🟢 active |
| 30 | [**DBX**](bytelogiccore-spec-dbx.md) | Beta pure-Rust HTAP embedded database whose key-value API edges out in-memory SQLite on a 10,000-row first-party benchmark. | **C** | Rust | MIT | 🟢 active |
| 31 | [**VortexDB**](ameetesh-a-vortexdb.md) | Hobby C++17 WiscKey-style key-value store with nested sub-databases; beats LevelDB only on small-value new-key inserts. | **C** | C++ | AGPL-3.0 | 🟢 active |
| 32 | [**lsm-tree-go**](aasheeshlikepanner-lsm-tree-go.md) | Small learning-project LSM-tree KV store in Go; beats bbolt only on batched random writes, loses reads and sequential writes. | **C** | Go | MIT | 🟢 active |
| 33 | [**Speedb**](speedb-io-speedb.md) | RocksDB fork, API-compatible through RocksDB 8.6.7, adding a hash-based memtable and gradual write throttling to beat stock RocksDB. | **C** | C++ | Apache-2.0 | 🟡 stale |
| 34 | [**NuDB**](cppalliance-nudb.md) | Header-only, insert-only on-disk hash table for SSDs; its own benchmark shows higher insert and large-DB fetch throughput than default-config RocksDB. | **C** | C++ | BSL-1.0 | 🟡 stale |
| 35 | [**Starskey**](starskey-io-starskey.md) | Small pure-Go LevelDB/WiscKey-style LSM key-value store; its own bench beats fsync-per-op RocksDB but loses to LMDB. | **C** | Go | MPL-2.0 | 🟡 stale |
| 36 | [**CalicoDB**](andy-byers-calicodb.md) | Small C++17 embedded transactional B+-tree key-value store modeled on SQLite's WAL design; beats SQLite on large-value reads and sequential fills. | **C** | C++ | MIT | 🟡 stale |
| 37 | [**Sophia**](pmwkaa-sophia.md) | Abandoned C MVCC key-value engine (append-only, RAM-disk hybrid); self-reported 2.6x LevelDB random reads in 2013, never reproduced. | **C** | C | BSD-2-Clause | 🔴 abandoned |
| 38 | [**ForestDB**](couchbaselabs-forestdb.md) | Couchbase's embedded key-value engine built on an HB+-trie; first-party 2014 tests show up to 8x faster reads than SQLite. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 39 | [**HSE (Heterogeneous-memory Storage Engine)**](hse-project-hse.md) | Micron's embedded C key-value engine for NVMe SSDs; its own YCSB run shows about 8x RocksDB's load throughput. | **C** | C | Apache-2.0 OR MIT | 🔴 abandoned |
| 40 | [**upscaledb**](cruppstahl-upscaledb.md) | Embedded typed-key B+tree store (formerly hamsterdb) whose in-engine aggregates beat cursor scans in LevelDB and Berkeley DB. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 41 | [**HaloDB**](yahoo-halodb.md) | Java embedded key-value store for point lookups: append-only logs plus an off-heap hash index. Beats RocksDB on random writes and reads in IO-bound tests. | **C** | Java | Apache-2.0 | 🔴 abandoned |
| 42 | [**count-db**](koendeschacht-count-db.md) | Java embedded store for 64-bit-keyed counters; first-party bigram test: \~82x LevelDB write, \~12x read throughput. | **C** | Java | MIT | 🔴 abandoned |
| 43 | [**ToplingDB**](topling-toplingdb.md) | RocksDB 8.10 fork with a trie memtable and searchable compressed SSTs; about 5x RocksDB's in-cache random-read throughput. | **C** | C++ | GPL-2.0 OR Apache-2.0 (study only) | 🟢 active |
| 44 | [**BTreePlus**](koyllis-btreeplus.md) | Binary-only fixed-width B+Tree index for .NET; vendor claims 4.4-7x faster bulk inserts than SQLite (paid Pro build). | **C** | C# | MIT for the Community… (study only) | 🟢 active |
| 45 | [**DiaLSM**](discos-lab-dialsm.md) | Hash-sharded LSM built on RocksDB 8.3.2 that reroutes writes around stalled shards, cutting write stalls \~94%. Code not released. | **C** | C++ | no license (study only) | 🟢 active |
| 46 | [**CompassDB**](paper-compassdb.md) | Paper-only RocksDB-derived KV engine that replaces SST indexes with in-memory two-tier perfect hashing; reports 2.5-4x RocksDB YCSB point-op throughput. | **C** | C++ | no license (study only) | ⚪ unknown |
| 47 | [**LUDA**](paper-luda.md) | Paper-only LevelDB 1.22 fork that moves most compaction work to an NVIDIA GPU; about 2x LevelDB/RocksDB YCSB-A throughput, but only under heavy CPU contention. | **C** | C++ | no license (study only) | ⚪ unknown |
| 48 | [**Mycelium (TE-LSM)**](paper-mycelium-te-lsm.md) | RocksDB fork that splits columns, re-encodes values or builds secondary indexes during compaction, for faster analytic reads than RocksDB. | **C** | C++ | no license (study only) | ⚪ unknown |
| 49 | [**UStore (UDisk engine)**](unum-cloud-ustore.md) | Closed-source NVMe KV engine (UDisk) behind UStore's open C API; vendor numbers show 2-7x RocksDB throughput. | **C** | C++ | Apache-2.0 (study only) | 🔴 abandoned |
| 50 | [**PostgreSQL**](postgres-postgres.md) | Client-server SQL RDBMS; one advocate's durability-off sysbench run beats MySQL 8.0's published point-select peak, not read-write. | **D** | C | PostgreSQL | 🟢 active |
| 51 | [**MySQL**](mysql-mysql-server.md) | Oracle's client-server SQL database (InnoDB). It edges PostgreSQL only on sysbench oltp_read_write in one cross-machine, durability-off comparison. | **D** | C++ | GPL-2.0-only (with Oracle's… | 🟢 active |
| 52 | [**ODB**](codesynthesis-com-odb.md) | Code-generating C++ ORM for MySQL, SQLite, PostgreSQL, Oracle and SQL Server; its 2x-over-Dapper claim compares different databases. | **D** | C++ | GPL-2.0-only or commercial… (study only) | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
