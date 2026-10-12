# SplinterDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Embedded C key-value store for NVMe SSDs; paper reports 6-10x RocksDB insert throughput and 2-2.6x point-query throughput.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | 6-10x faster insertions and 2-2.6x faster point queries than RocksDB, with about 2x lower write amplification, while matching RocksDB on small range queries |
| **Workload** | YCSB-derived trace replay (load phase and workloads A-F, 24B keys, 100B values and a 1KiB-value set) plus microbenchmarks, on an Optane 905p NVMe SSD with memory limited to about 10% of the dataset size (usually 4GiB), per the USENIX ATC'20 paper 'SplinterDB: Closing the Bandwidth Gap for NVMe Key-Value Stores'. |
| **Metric** | throughput |
| **Hardware** | Dell PowerEdge R720, 32-core 2.00 GHz Intel Xeon CPU (exact model not named), 256 GiB RAM, 960GiB Intel Optane 905p PCIe 3.0 NVMe SSD, 4096-byte blocks; memory capped at 4GiB via a Linux cgroup (per paper section 6.1) |
| **Adoption** | 732 stars |
| **Last commit** | 2026-07-31 |
| **Links** | [repository](https://github.com/vmware/splinterdb) · [benchmark](https://www.usenix.org/conference/atc20/presentation/conway) |

## Verdict

The USENIX ATC'20 paper replayed YCSB-derived traces (load and A-F, 24B keys, 100B and 1KiB values) against an unnamed version of RocksDB (and PebblesDB) on a Dell R720 with a 32-core 2.0 GHz Xeon and an Optane 905p SSD, memory capped at 4GiB by a cgroup: SplinterDB was 6-10x faster on inserts, 2-2.6x on point queries, roughly equal on short scans, with half the write amplification. Compiler and flags were not reported; the repo's tests/functional/ycsb_test.c is a SplinterDB trace replayer, but the traces and the RocksDB side of the harness are not in the repo.

## Use it when

- Write-heavy ingest of small pairs (paper: 24B keys, 100B values) on fast NVMe, where RocksDB is CPU-bound rather than device-bound
- Datasets far larger than RAM (paper caps memory at about 10% of the dataset, 4GiB) that still need fast point lookups
- Many-threaded clients: the paper reports point reads at 18.5x single-thread throughput with 24 threads (YCSB C)
- Workloads that can express changes as blind updates (append, increment) through a custom data_config, skipping read-modify-write
- Research systems or prototypes on Linux that can accept an unstable API and unversioned on-disk format

## Skip it when

- Data that must survive a crash: the write-ahead log is off unless use_log is set, there is no fsync/commit API, and core_mount still says crash recovery (log replay + allocator rebuild) is not wired, so a database that was not cleanly closed refuses to mount
- Short range scans on small values: the paper measured YCSB E about 15% slower than RocksDB with 100B values (about 15% faster with 1KiB values)
- Anything needing transactions/atomic multi-put, range delete, a stable API, or an on-disk format that survives upgrades (all listed in docs/limitations.md)
- Non-Linux targets: macOS and Windows are unsupported because the I/O layer is built on libaio
- Long-running production ingest before re-testing: open issues #560 (critical assert in routing_filter_add on large small-pair insert runs, 2023) and #585 (segfault in routing_filter_lookup under YCSB-C) have no recorded resolution

## How it is fast

The core structure is the STBε-tree (size-tiered Bε-tree): a trunk tree of fanout 8-16 whose nodes point to immutable B-tree 'branches', each paired with a quotient filter instead of a Bloom filter. Size-tiering plus a flush-then-compact policy rewrite each key fewer times than leveled LSM compaction (about half RocksDB's write amplification in the paper) and let many small, local compactions run in parallel. A concurrent memtable (hand-over-hand locking) and a user-level clock cache with distributed reader-writer locks and O_DIRECT I/O remove the CPU and lock contention that, per the paper, holds RocksDB to about 30% of an Optane SSD's bandwidth.

## Compared with alternatives

Pick SplinterDB for write-heavy, small-pair ordered workloads on NVMe when you can accept an experimental engine with weak crash safety; choose TerarkDB or Titan to stay RocksDB-compatible (Titan for large values), libmdbx for read-mostly ACID transactions, and NuDB for append-only insert/fetch with no ordering.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | libaio, libxxhash, pthread, libm (build docs also install libconfig-dev) |
| **Minimum toolchain** | C with GNU extensions; minimum version not documented; CI uses GCC 13 and Clang 19; public headers are C++-compatible (extern "C") |
| **Platforms** | Linux only; CI runs on x86-64 Ubuntu; the Makefile adds -march=native on x86-64 and skips it elsewhere, but aarch64 support is not documented or tested |
| **Thread safety** | One splinterdb handle is designed for concurrent use by many threads, which auto-register on first call; only one process may open a database file/device; a lookup_result object must not be shared across threads |
| **Drop-in for the baseline** | partial — iterator semantics mirror RocksDB's, but it is a different C API with no Seek, column families, WriteBatch, transactions or options compatibility |

## Gotchas

- The default release build uses -O3 -ffast-math -flto and, on x86-64, -march=native, so a library built on one machine can fault on an older CPU
- cache_size and data_config (key compare, merge functions) are not stored in the database and must be supplied identically on every open; disk size is fixed at create time
- Iterators must be deinitialized; the header warns a live iterator can block inserts, deletes and close from the same thread
- docs/limitations.md lags the code: it still says keys and values must be smaller than the 4KiB page, but PR #674 (May 2026) added values larger than a page

## Known shortcomings

- No crash recovery: log replay is 'not wired yet' in src/core.c, an uncleanly closed DB refuses to mount, WAL off by default, no fsync API. \~15% slower than RocksDB on YCSB E short scans; the paper names no RocksDB version, CPU model, compiler or flags; traces and the RocksDB harness are not public. Linux-only (libaio), x86-64 CI only, Release uses -march=native -ffast-math. Open critical assert on small-pair inserts (#560) and segfault on YCSB-C (#585) since 2023. No releases; 'not for production before 1.0'.

## Caveats and trade-offs

Numbers come from the 2020 peer-reviewed paper against the RocksDB of that time, so the current code and current RocksDB may differ. The paper gives the machine (32-core 2.00 GHz Xeon, Optane 905p) but not the exact CPU model, compiler, or flags. It is not confirmed that the paper's YCSB trace replayer is in the public repo.

Project's own docs say it is not recommended for production before v1.0; gains are specifically tuned for NVMe device bandwidth characteristics.

## Maintenance

Actively developed by VMware Research (values larger than a page, async scans and checkpointing all landed in 2026) under Apache-2.0, but there are no releases and the maintainers say it is not for production before 1.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed USENIX ATC'20 paper whose abstract says SplinterDB beats RocksDB by 6-10x on insertions and 2-2.6x on point queries, matches it on small range queries, and cuts write amplification 2x. The paper names the machine but not the exact Xeon model, compiler, or flags, and its trace-replay harness was not confirmed public, so it is B, not A.
- **Verifier notes:** The abstract numbers match the record exactly. last_commit was the repo pushed_at date (2026-08-18); the newest commit on main is 2026-07-31. License Apache-2.0, 732 stars, not archived and not a fork, all confirmed.
- **Fields the verifier corrected:** `hardware`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/conference/atc20/presentation/conway>
  - <https://www.usenix.org/system/files/atc20-conway.pdf>
  - <https://github.com/vmware/splinterdb>
- **Sources the enricher read:**
  - <https://github.com/vmware/splinterdb>
  - <https://github.com/vmware/splinterdb/blob/main/docs/README.md>
  - <https://github.com/vmware/splinterdb/blob/main/docs/usage.md>
  - <https://github.com/vmware/splinterdb/blob/main/docs/limitations.md>
  - <https://github.com/vmware/splinterdb/blob/main/docs/build.md>
  - <https://github.com/vmware/splinterdb/blob/main/include/splinterdb/splinterdb.h>
  - <https://github.com/vmware/splinterdb/blob/main/include/splinterdb/data.h>
  - <https://github.com/vmware/splinterdb/blob/main/Makefile>
  - <https://github.com/vmware/splinterdb/blob/main/src/splinterdb.c>
  - <https://github.com/vmware/splinterdb/blob/main/src/core.c>
  - <https://github.com/vmware/splinterdb/blob/main/src/blob.h>
  - <https://github.com/vmware/splinterdb/blob/main/src/blob_build.h>
  - <https://github.com/vmware/splinterdb/blob/main/tests/functional/ycsb_test.c>
  - <https://github.com/vmware/splinterdb/blob/main/examples/README.md>
  - <https://github.com/vmware/splinterdb/blob/main/examples/splinterdb_wide_values_example.c>
  - <https://github.com/vmware/splinterdb/blob/main/.github/workflows/run-tests.yml>
  - <https://github.com/vmware/splinterdb/commits/main>
  - <https://github.com/vmware/splinterdb/issues>
  - <https://github.com/vmware/splinterdb/issues/236>
  - <https://github.com/vmware/splinterdb/issues/560>
  - <https://github.com/vmware/splinterdb/issues/585>
  - <https://github.com/vmware/splinterdb/issues/591>
  - <https://github.com/vmware/splinterdb/pull/683>
  - <https://github.com/vmware/splinterdb/pull/675>
  - <https://github.com/vmware/splinterdb/pull/674>
  - <https://github.com/vmware/splinterdb/pull/665>
  - <https://github.com/vmware/splinterdb/pull/658>
  - <https://github.com/vmware/splinterdb/pull/491>
  - <https://www.usenix.org/conference/atc20/presentation/conway>
  - <https://www.usenix.org/system/files/atc20-conway.pdf>
  - <https://hn.algolia.com/api/v1/search?query=splinterdb&tags=story>
  - <https://news.ycombinator.com/item?id=31515765>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/vmware/splinterdb`) · [data/wave6/enrich/raw/github_com_vmware_splinterdb.json](../../../data/wave6/enrich/raw/github_com_vmware_splinterdb.json) (enrichment confidence 0.8)

</details>
