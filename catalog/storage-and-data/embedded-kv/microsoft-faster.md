# F2 (FASTER v2)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Microsoft's two-tier hash-and-log KV store for skewed, larger-than-memory point workloads; its paper reports \~11.8x RocksDB throughput at 10% memory.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | 2-11.9x better throughput than existing KV stores (abstract). Fig. 10 (YCSB + MixGraph, 16 cores, memory = 10% of dataset) averages: 11.8x RocksDB v8.11.4, 2.1x FASTER, 2x LeanStore, 4.6x SplinterDB, 11.9x KVell. Average request latency vs RocksDB: 1.4x lower read and 3.5x lower write (Table 1). |
| **Workload** | YCSB (A/B/C/D/F/W) and MixGraph benchmarks, 250M keys (8B key/100B value), Zipfian skew, on CloudLab NVMe RAID-0, memory budget 10% of dataset size |
| **Metric** | throughput |
| **Hardware** | CloudLab sm110p node: 16-core Intel Xeon Silver 4314, 128GiB RAM, 4x Samsung PM9A3 NVMe SSD (PCIe 4.0) in RAID-0, Linux kernel 5.4, ext4 |
| **Adoption** | 6.6k stars |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/microsoft/FASTER) · [benchmark](https://arxiv.org/abs/2305.01516) |

## Verdict

Setup, from the PVLDB 18(12) 2025 paper: CloudLab node with a 16-core Xeon Silver 4314 and 4 PM9A3 NVMe drives in RAID-0, 250M 8 B-key/100 B-value YCSB records (A/B/C/D/F/W) plus MixGraph, 16 threads, memory capped at 10% of the data. Every system ran with Direct I/O and no WAL, compression or checksums, and RocksDB v8.11.4 was tuned with 10-bit Bloom filters and the data-block hash index. F2 averaged 11.8x RocksDB's throughput, and single-thread latency was 1.4x lower on reads and 3.5x lower on writes. The compiler is not stated and the RocksDB harness is not published.

## Use it when

- Point-only traffic (get/put/delete/RMW) with Zipfian-like skew on a dataset roughly 5-40x larger than the RAM you can give it. The paper used 250M keys (\~30 GiB) under a 3 GiB cap.
- Update- or RMW-heavy state such as counters, per-entity or per-function state, or streaming join synopses, where RocksDB's compaction write amplification hurts. Paper: 3.3-3.9 us single-thread write latency vs RocksDB's 6.7-17.3 us, and write amplification of 1.2-2.4 vs 2.5-5.8.
- Workloads where the read-hot and write-hot key sets differ; the read cache keeps disk-resident read-hot records in memory without pulling them back into the write log.
- Billions of keys where index RAM is the constraint: the cold-log index is tunable to under 1 B per key.
- A Linux x86-64 NVMe server running a custom C++ service (up to 96 threads) where you control the per-thread loop (sessions, Refresh, CompletePending).

## Skip it when

- You need range scans, prefix seeks, ordered iteration, snapshots, transactions, column families or compression. F2Kv exposes point operations only; the paper even dropped MixGraph's 3% seeks.
- Low-skew or uniform read-heavy access. Every cold-log read costs about two extra I/Os, the paper shows YCSB-B throughput falling as skew drops (alpha &lt;= 50), and once memory reaches 20% or more of the dataset, the original FASTER matches F2.
- Production use that needs a maintained engine. Since Aug 2026 the README says the repo is no longer actively maintained and points to Garnet/Tsavorite (C#). The F2 infinite-compaction/RMW-test-failure issue #944 is still open, its fix #947 has been an unmerged draft since Sep 2025, and the paper says F2 has not been tested on production workloads.
- macOS or other non-Linux/non-Windows targets. The POSIX I/O backend requires Linux libaio (or liburing), and Windows CI runs only the in-memory tests, not the F2 tests.
- You want a drop-in RocksDB swap. The callback/context API, compile-time key/value types and manual checkpointing make a port a rewrite.

## How it is fast

Write-hot records stay in a FASTER HybridLog, which is updated in place in its in-memory mutable region, flushed append-only to disk and indexed by a latch-free in-memory hash table. Background hot-cold compaction moves write-cold records to a separate cold log. That log uses a two-level hash index: an in-memory table points to 256 B 'hash chunks' kept on disk, costing under 1 byte of RAM per cold key versus FASTER's 8 bytes. Compaction is multi-threaded and lookup-based, built on a Conditional-Insert primitive that copies a record only if no newer version of its key has been appended; the paper measures it 5.2x faster than FASTER's scan-based compaction while using 25x less memory. A second-chance FIFO read cache, chained into the hot index, serves read-hot records that live on disk, so a hot key needs no I/O and a cold key needs about two (index chunk plus record) instead of an LSM level probe.

## Compared with alternatives

Pick F2 over KVell and SplinterDB for pure point/RMW traffic with heavy skew and RAM around 10% of the data: in the same paper it averaged 11.9x KVell's and 4.6x SplinterDB's throughput, though SplinterDB had slightly lower single-thread YCSB-B read latency (42.1 vs 45.3 us). Pick SplinterDB, whose entry reports it matching RocksDB on small range queries, or another LSM sibling when you need ordered scans.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Linux: libaio, libuuid, Intel TBB, stdc++fs, pthread (optional liburing via USE_URING). Windows: rpcrt4. CMake FetchContent downloads toml11 v4.3.0 and googletest v1.14.0 at configure time. The optional Azure blob device also needs cpprestsdk and azure-storage-cpp. |
| **Minimum toolchain** | CMake 3.14+. On Linux, GCC in -std=c++17 mode (the headers also use designated initializers, which GCC accepts as an extension). On Windows, Visual Studio 2022 with /std:c++20. CI uses Ubuntu 22.04 g++ and windows-2022. |
| **Platforms** | Linux x86-64 (libaio or io_uring) and Windows x64. No macOS I/O backend. ARM is not documented, and the io_uring spinlock uses the x86-only __builtin_ia32_pause. |
| **Thread safety** | Latch-free, linearizable concurrent operations. Each thread must call StartSession(), then call Refresh()/CompletePending() periodically, then StopSession(). At most 96 threads (Thread::kMaxNumThreads); going over throws 'Too many threads!'. Only one Checkpoint() may run at a time; a second one throws. |
| **Drop-in for the baseline** | no |

## Gotchas

- Reads of disk-resident keys return Status::Pending, and the callback fires only when that same thread calls CompletePending(). The bundled benchmark calls Refresh() every 64 ops and CompletePending() every 1,600.
- Auto-compaction is on by default, with disk budgets of only 1 GiB (hot) and 8 GiB (cold). The paper set them to 125% of dataset size (5 GiB / 35 GiB for 30 GiB of data), and budgets under 64 MiB throw. The read cache is off by default (DEFAULT_READ_CACHE_CONFIG.enabled = false) and has to be enabled and sized explicitly.
- The hot index table_size must be a power of two and at most INT32_MAX or the constructor throws std::invalid_argument. The paper advises sizing both indexes to the expected unique-key counts to avoid extra I/Os per lookup. Misuse is reported through C++ exceptions.
- The F2 configuration samples on the docs page do not compile as written (for example the typos hlog_copaction_config and hot-config). Start from cc/benchmark-dir/benchmark_f2.cc instead. That harness also differs from the paper's setup: 8-byte values, read cache disabled, 4 GiB hot + 12 GiB cold in-memory logs (its comment says 6/10 GiB), and only workloads A, B, C and 100% RMW.

## Known shortcomings

- Venue is PVLDB 18(12) 2025 (not VLDB 2023). The 11.8x is an average over YCSB and MixGraph; latency gains are 1.4x read and 3.5x write. The RocksDB harness and compiler are not published.
- No longer actively maintained: since 2026-08 the README points to Garnet/Tsavorite (C#); the only C++ change since the F2 merge (2025-02) is overflow hardening. Open bug #944 (F2 compaction hang, failing RMW test) has only an unmerged draft fix (#947, since 2025-09); the paper admits no production-workload testing.
- The public benchmark_f2.cc differs from the paper (8 B values vs 100 B, read cache off, 4+12 GiB in-memory split, workloads A/B/C/RMW only), so the paper's numbers are not reproducible from the repo. Point operations only (no scan/iterator/transactions/compression); durability is manual Checkpoint with no WAL; the context+callback+session API is not a drop-in for RocksDB. Linux (libaio) and Windows x64 only, max 96 threads. Gains shrink at low skew and FASTER ties F2 at &gt;=20% memory.

## Caveats and trade-offs

The paper is PVLDB 18(12):4910-4923, 2025 (VLDB 2025, doi:10.14778/3750601.3750615), not VLDB 2023; 2023 is the arXiv v1 date. The 11.8x RocksDB average covers YCSB and MixGraph, not YCSB alone. The latency win is 1.4x on reads and 3.5x on writes, not 3.5x on both. All systems ran with Direct I/O and with WAL/persistence, compression and checksums disabled (non-default). RocksDB was further tuned with 10-bit Bloom filters and the data-block hash index via OptimizeForPointLookup(). Memory was capped at 10% of dataset (3GiB YCSB, 4GiB MixGraph). F2's benchmark code is public (cc/benchmark-dir/benchmark_f2.cc; Release builds with -O3 -g), but the compiler/version is unstated and the RocksDB harness is not in the repo, so the tier stays B.

Two-tier hash-index + record-log design optimized for skewed, larger-than-memory workloads; latch-free multi-threaded compaction adds implementation complexity; tuned for direct I/O with WAL/compression/checksums disabled in the benchmark, which is not RocksDB's typical durable-by-default configuration.

## Maintenance

MIT-licensed and public, but the README has said since Aug 2026 that the repo is no longer actively maintained (successor: Garnet/Tsavorite, in C#), not 'active' as recorded. The only C++ source change since F2 merged in Feb 2025 is an integer-overflow hardening patch, and the F2 compaction-hang fix (#947) is still an unmerged draft.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed PVLDB 18(12) 2025 paper compares F2 against RocksDB v8.11.4 on a stated CPU (Xeon Silver 4314). The F2/FASTER benchmark is public (cc/benchmark-dir/benchmark_f2.cc), and CMake Release pins -O3 -g on Linux. It is not A because the compiler/version is not stated and the RocksDB (and other baseline) harness is not published.
- **Verifier notes:** The numbers are real, but the venue/year was wrong (VLDB 2023 -&gt; PVLDB 18, 2025), the 11.8x scope was mislabeled, and the read latency was overstated (1.4x, not 3.5x). Metadata checks out via gh: MIT, 6,634 stars, not archived or a fork, last commit 2026-08-19.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2305.01516>
  - <https://arxiv.org/pdf/2305.01516>
  - <https://github.com/microsoft/FASTER>
  - <https://github.com/microsoft/FASTER/tree/main/cc/benchmark-dir>
  - <https://github.com/microsoft/FASTER/blob/main/cc/benchmark-dir/README.md>
  - <https://github.com/microsoft/FASTER/blob/main/cc/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/microsoft/FASTER>
  - <https://github.com/microsoft/FASTER/blob/main/cc/README.md>
  - <https://github.com/microsoft/FASTER/blob/main/cc/CMakeLists.txt>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/CMakeLists.txt>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/core/f2.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/core/config.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/core/thread.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/core/address.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/core/key_hash.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/core/record.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/core/alloc.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/core/light_epoch.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/environment/file_linux.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/index/mem_index.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/index/cold_index.h>
  - <https://github.com/microsoft/FASTER/blob/main/cc/src/index/hash_table.h>
  - <https://github.com/microsoft/FASTER/tree/main/cc/benchmark-dir>
  - <https://github.com/microsoft/FASTER/blob/main/cc/benchmark-dir/README.md>
  - <https://github.com/microsoft/FASTER/blob/main/cc/benchmark-dir/benchmark_f2.cc>
  - <https://github.com/microsoft/FASTER/blob/main/cc/benchmark-dir/benchmark.h>
  - <https://github.com/microsoft/FASTER/blob/main/docs/_docs/29-fasterkv-cpp.md>
  - <https://github.com/microsoft/FASTER/blob/main/azure-pipelines.yml>
  - <https://github.com/microsoft/FASTER/commits/main>
  - <https://github.com/microsoft/FASTER/issues/944>
  - <https://github.com/microsoft/FASTER/issues/924>
  - <https://github.com/microsoft/FASTER/issues/913>
  - <https://github.com/microsoft/FASTER/pull/947>
  - <https://github.com/microsoft/FASTER/pull/960>
  - <https://arxiv.org/abs/2305.01516>
  - <https://arxiv.org/pdf/2305.01516>
  - <https://hn.algolia.com/api/v1/search?query=F2%20FASTER%20key-value&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/microsoft/faster`) · [data/wave6/enrich/raw/github_com_microsoft_faster.json](../../../data/wave6/enrich/raw/github_com_microsoft_faster.json) (enrichment confidence 0.82)

</details>
