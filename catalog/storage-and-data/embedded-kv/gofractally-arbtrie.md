# PsiTri (arbtrie)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 embedded transactional KV store (radix trie, node-level COW) with a RocksDB-API shim; 1.6-3x RocksDB on bank transfers.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | PsiTriRocks (RocksDB-API drop-in) vs RocksDB, April 2026 AMD EPYC-Turin, batch=1: 2.3x write throughput (369,446 vs 157,588 transfers/sec) and 4.9x reader throughput under concurrent writes (1,416,652 vs 289,627 reads/sec). Native PsiTri vs RocksDB in the batch=100 run: 376,691 vs 126,341 transfers/sec on Apple M5 Max, about 2.98x (derived from page data); 163,614 vs 104,102 transfers/sec on AMD EPYC-Turin, about 1.57x (derived from page data). |
| **Workload** | TPC-B-style bank-transfer benchmark. Each transfer is one atomic transaction of 5 KV ops (2 reads, 2 updates, 1 insert), with triangular-skew access and a fixed seed. The main runs use 1M accounts, 10M transfer attempts, 100 transfers per commit and sync=none. The PsiTriRocks drop-in comparison is a separate April 2026 EPYC run: 1M accounts, 1M transactions, batch=1, sync=none, write-only and write plus one concurrent reader. |
| **Metric** | throughput |
| **Hardware** | Apple M5 Max, 128 GB unified memory (macOS); AMD EPYC-Turin, 8 cores/16 threads at 2.4 GHz with 121 GB RAM (Vultr cloud VM, Linux 6.17, exact SKU not given) |
| **Compiler and flags** | Apple M5 Max: Clang 17, C++20, -O3 -flto=thin. AMD EPYC-Turin: Clang 20, C++20, -O3 -flto -march=native (AVX-512 enabled) |
| **Adoption** | 4 stars |
| **Last commit** | 2026-04-28 |
| **Links** | [repository](https://github.com/gofractally/arbtrie) · [benchmark](https://gofractally.github.io/arbtrie/benchmarks/bank/) |

## Verdict

The project's own TPC-B-style bank benchmark counts 5 KV ops per atomic transfer, uses triangular skew and runs with sync=none. At batch=1 on an 8-core AMD EPYC-Turin Vultr VM (Clang 20, -O3 -flto -march=native), the RocksDB-API shim PsiTriRocks wrote 2.3x as many transfers/s as RocksDB (369K vs 158K), and its concurrent reader did 4.9x as many reads/s (1.42M vs 290K). At batch=100, native PsiTri was about 2.98x RocksDB 9.9.3 on an Apple M5 Max (Clang 17, -O3 -flto=thin) but only about 1.57x on the EPYC VM, where MDBX (239K) and TidesDB (167K) beat it (164K).

## Use it when

- Small read-modify-write transactions (ledger or balance updates, blockchain or game state) that touch a few keys atomically, where durability via a periodic flush is acceptable instead of an fsync per commit.
- One writer plus concurrent point readers that need consistent snapshots. In the bank runs, native PsiTri's write throughput did not drop with a reader attached (+1.5% on M5 Max, +10.7% on EPYC).
- A RocksDB app that only uses Put/Get/Delete/WriteBatch/iterators/snapshots on the default column family and wants to try another engine by relinking.
- Workloads that count or delete key ranges often, or that store hierarchical data (nested subtrees, O(1) snapshot of a subtree).
- Linux or macOS on x86-64 or ARM64 with a dataset up to about 2x RAM. The scale benchmark held &gt;300K inserts/s and &gt;11M reads/s (12 threads) up to that point.

## Skip it when

- You need durability on every commit. All published benchmarks use sync=none, and unflushed DWAL WAL entries are lost on crash. PsiTriRocks ignores WriteOptions::sync and Options::use_fsync; only Flush() syncs the WAL.
- Disk space is tight. Data is never compressed, and files run 2-4x the live data under sustained writes: 1,088 MB for PsiTri vs 320 MB for RocksDB in the M5 bank run, and 76.7 GB vs 51.5 GB at 200M random upserts.
- Your code depends on RocksDB merge operators, bloom filters, block cache, compression, statistics or compaction tuning. PsiTriRocks accepts these silently and ignores them, and Merge behaves as Put.
- Scan-heavy or bulk-load-heavy work. MDBX scanned 2-4x faster in the bank runs, and RocksDB bulk-loaded faster than PsiTriRocks on both machines (1.96M vs 1.80M and 1.16M vs 0.96M ops/s).
- You need a proven production engine. It is pre-1.0 (the authors say the API may change and it is not battle-tested), has 4 stars and no independent replication, and native PsiTri lost to MDBX on the x86 VM (164K vs 239K transfers/s). Writes to the same root are serialized by a mutex.

## How it is fast

The index is an adaptive radix trie crossed with a B-tree. Inner nodes route on 1-byte dividers found with a SIMD lower_bound (NEON, SSE2/SSSE3 or AVX-512, chosen at compile time), and leaves are sorted \~2 KB nodes with hash-accelerated lookup. Copy-on-write happens per node in 64-byte multiples instead of 4 KB pages. Every object is reached through a 32-bit ID in a control-block table, so the segment allocator (SAL) can move an object with a memcpy plus one CAS, while writers bump-allocate in private 32 MB segments. The DWAL write path puts commits into a writer-private in-memory ART buffer plus a buffered WAL append with no fsync. Two background merge threads then drain 100K-entry batches into the COW trie, so there is no LSM compaction and readers get lock-free MVCC snapshots.

## Compared with alternatives

Pick PsiTri over SplinterDB, KVell or F2 when the workload is small multi-key atomic transactions with concurrent readers that need snapshots. Those siblings' catalogued wins measure raw insert or lookup throughput, while PsiTri's evidence is on transactions. If you rely on merge operators, compression or bloom filters, or need to reopen existing RocksDB data, prefer an engine that keeps RocksDB's feature set and format, because PsiTriRocks drops them.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Threads plus in-repo libraries (sal, ucc, art, hash, bundled xxhash). A standalone build also requires Boost.program_options, Catch2 3 (tests are on by default) and fetches abseil via CMake FetchContent; PsiTriRocks links absl::btree privately. The SQLite and DuckDB layers are optional. |
| **Minimum toolchain** | C++20 and CMake 3.16+. The README says Clang 15+ or GCC 12+, but the top-level CMakeLists states that LLVM clang is required and GCC is not supported, and on macOS it hard-codes Homebrew LLVM's clang++. The benchmarks used Clang 17 and Clang 20. |
| **Platforms** | Linux and macOS (POSIX mmap/mlock; no Windows code path found). Runs on x86-64 (SSE2/SSSE3/AVX-512 paths) and ARM64 (NEON), with scalar fallbacks. -march=native is on by default, so binaries are not portable unless you turn it off. CI runs on Ubuntu only. |
| **Thread safety** | The database handle is thread-safe. Sessions are thread-affine: create each one on the thread that uses it, with at most 50 application write sessions of 32 MB each. Each of the 512 roots allows one writer at a time, and writes to the same root are serialized by a mutex. Readers use lock-free MVCC snapshots, except that the 'latest' read mode, which PsiTriRocks uses for Get, takes a shared lock against the writer. |
| **Drop-in for the baseline** | partial — source-compatible only. PsiTri ships its own subset of the rocksdb/\*.h headers, so you relink to psitri::psitrirocks; it is not ABI-compatible and cannot open existing RocksDB data directories, since it uses its own on-disk format. Put/Get/MultiGet/Delete/DeleteRange/WriteBatch/iterators/snapshots and up to 512 column families work. Merge becomes Put; bloom filters, cache, compression, statistics, compaction options and WAL options are ignored; Iterator::Refresh returns NotSupported. |

## Gotchas

- In PsiTriRocks, WriteBatch drops the column-family argument (Put(cf, k, v) forwards to Put(k, v)), and DB::Write always writes to root 0, so column-family writes made through a batch land in the default column family.
- OpenForReadOnly just calls Open, which opens the database read-write. Flush() and CompactRange() are accepted but only sync the WAL or do nothing; to reclaim disk space you must call compact_and_truncate (the psitri.compact_and_truncate property through the shim).
- Long-lived snapshots compete with live nodes for cacheline slots, and inner-node fan-out can drop from 256 to as low as 16 until they are released. Recovery after a crash scans the whole database, which the docs estimate at minutes for a 100 GB database.
- Write sessions are heavy (32 MB buffer each, backed by thread_local storage). Do not create them per request or pass them between threads. DWAL merges also stall: in the 200M-key random-upsert run the minimum round throughput was 24,791 ops/s, vs 85,161 for RocksDB.

## Known shortcomings

- Workload is TPC-B (not TATP); the 2.3x/4.9x come from a separate batch=1 run and the 4.9x is reader throughput under a concurrent writer, with sync=none. TidesDB and MDBX beat it on EPYC.
- All benchmarks run with sync=none, and the RocksDB shim ignores WriteOptions::sync and use_fsync, so unflushed WAL is lost on crash. The shim's WriteBatch drops the column family (writes go to the default root), OpenForReadOnly opens read-write, Merge is treated as Put, and Bloom/compression/stats options are ignored; source-compatible only, cannot open RocksDB data.
- Files are 2-4x live data (1,088 vs 320 MB); loses bulk load to RocksDB; MDBX beats it on EPYC and on scans. CMake says clang only (README says GCC 12+), -march=native by default, no Windows, CI Ubuntu only. Pre-1.0, 4 stars, no independent replication; snapshots shrink fan-out; recovery time grows with DB size.

## Caveats and trade-offs

Only 4 GitHub stars and no independent replication. All runs use sync=none (no forced durability). On the AMD EPYC-Turin VM, both MDBX (239,041) and TidesDB (167,093) beat native PsiTri (163,614 transfers/sec), so the win over RocksDB is not a win over every engine tested. The 4.9x figure measures reader throughput under a concurrent writer, not a pure read workload. First-party benchmark.

Also ships PsiTri-SQLite (SQLite drop-in) claiming 1.06x write / 13.5x read vs SQLite in the same bank benchmark, and separately 47x (sync=off) / 3.8x (sync=full) on a TATP telecom benchmark without hardware stated for that specific table. Very new project; README/repo name mismatch (repo is 'arbtrie', product now called 'PsiTri') suggests a recent rename/pivot, so API and durability guarantees may still be in flux.

## Maintenance

The project is actively developed but pre-1.0: the last main commit (2026-04-28) was one of a burst of MVCC and recovery fixes, the repo has 4 stars and is still named arbtrie, and it is MIT-licensed and installable as a CMake static library, though the authors warn the API may change and it has no production track record.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The bank benchmark page runs PsiTri against RocksDB (plus MDBX, TidesDB and SQLite) using public code (programs/bank_bench.cpp, driven by bench/suites/bank_tpcb.sh; raw logs and machine.json are in docs/data/bank_tpcb/). It states the CPUs (Apple M5 Max; AMD EPYC-Turin 8c/16t 2.4 GHz), the compilers (Clang 17 / Clang 20) and the flags (-O3 -flto=thin / -O3 -flto -march=native).
- **Verifier notes:** All record numbers appear on the page and belong to the right rows. I made clarifying fixes: the workload is TPC-B-style, not TATP, and the 2.3x/4.9x figures come from a separate batch=1 run. Metadata checks out: MIT license, 4 stars, last main commit 2026-04-28, active.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://gofractally.github.io/arbtrie/benchmarks/bank/>
  - <https://github.com/gofractally/arbtrie>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/data/bank_tpcb/2026-04-06/vultr/machine.json>
- **Sources the enricher read:**
  - <https://github.com/gofractally/arbtrie>
  - <https://gofractally.github.io/arbtrie/benchmarks/bank/>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/benchmarks/bank.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/benchmarks/rocksdb-api.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/benchmarks/random-upsert.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/benchmarks/scale.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/benchmarks/x86_simd.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/getting-started/rocksdb-migration.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/getting-started/api.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/why-psitri/tradeoffs.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/why-psitri/design.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/internals/known-issues.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/internals/recovery.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/internals/data-integrity.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/architecture/dwal.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/architecture/concurrent-writers.md>
  - <https://github.com/gofractally/arbtrie/blob/main/docs/architecture/overview.md>
  - <https://github.com/gofractally/arbtrie/blob/main/BUGS.md>
  - <https://github.com/gofractally/arbtrie/blob/main/TODO>
  - <https://github.com/gofractally/arbtrie/blob/main/CMakeLists.txt>
  - <https://github.com/gofractally/arbtrie/blob/main/libraries/psitri/CMakeLists.txt>
  - <https://github.com/gofractally/arbtrie/blob/main/libraries/psitrirocks/CMakeLists.txt>
  - <https://github.com/gofractally/arbtrie/blob/main/libraries/sal/CMakeLists.txt>
  - <https://github.com/gofractally/arbtrie/blob/main/libraries/psitrirocks/src/db_impl.cpp>
  - <https://github.com/gofractally/arbtrie/blob/main/libraries/psitrirocks/include/rocksdb/write_batch.h>
  - <https://github.com/gofractally/arbtrie/blob/main/libraries/psitri/include/psitri/dwal/dwal_database.hpp>
  - <https://github.com/gofractally/arbtrie/blob/main/libraries/sal/include/sal/simd_utils.hpp>
  - <https://github.com/gofractally/arbtrie/blob/main/libraries/sal/src/mapping.cpp>
  - <https://github.com/gofractally/arbtrie/blob/main/libraries/psitri-sqlite/README.md>
  - <https://github.com/gofractally/arbtrie/blob/main/.github/workflows/coverage.yml>
  - <https://github.com/gofractally/arbtrie/commits/main>
  - <https://github.com/gofractally/arbtrie/issues?q=is%3Aissue>
  - <https://hn.algolia.com/api/v1/search?query=psitri&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=arbtrie>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/gofractally/arbtrie`) · [data/wave6/enrich/raw/github_com_gofractally_arbtrie.json](../../../data/wave6/enrich/raw/github_com_gofractally_arbtrie.json) (enrichment confidence 0.8)

</details>
