# SNKV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Apache-2.0` · 🟢 active

> C key-value API on SQLite's B-tree, pager and WAL minus the SQL layer; 1.6-2x SQLite in first-party KV microbenchmarks.

| | |
|---|---|
| **Beats** | SQLite |
| **Claimed result** | 1.64x-2x faster than SQLite (1M records): sequential writes 232K vs 142K ops/s (1.64x), random reads 160K vs 90K ops/s (1.77x), sequential scan 2.89M vs 1.56M ops/s (1.85x), random updates 31K vs 16K ops/s (1.9x), random deletes 31K vs 16K ops/s (\~2x), mixed workload 62K vs 34K ops/s (1.79x). |
| **Workload** | 1M records on Linux; sequential writes, random reads, sequential scan, random updates/deletes, and mixed workload, comparing SNKV (talks directly to SQLite's B-tree engine, skipping the SQL layer) against SQLite itself. Both use WAL mode, synchronous=NORMAL, 8MB cache, 4KB pages; SQLite uses a WITHOUT ROWID table. |
| **Metric** | throughput |
| **Hardware** | unspecified Linux machine (no CPU model stated) |
| **Compiler and flags** | Not stated with the results. SNKV Makefile: gcc, default BUILD=debug (-g -O0 -DDEBUG), BUILD=release gives -O2 -DNDEBUG. The SQLite comparison repo (hash-anu/sqllite-benchmark-kv) Makefile: gcc -g -Wall with no -O flag, i.e. GCC's default -O0. |
| **Adoption** | 78 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/hash-anu/snkv) · [benchmark](https://github.com/hash-anu/snkv#benchmarks) |

## Verdict

This is a first-party, single-threaded C microbenchmark on Linux x86-64 with an unnamed CPU (the docs page adds 'NVMe'), gcc with no version given, and both Makefiles defaulting to -O0 builds. It loaded 1M records with 12-byte sequential 'key_%08d' keys and 61-byte values; both engines used WAL, synchronous=NORMAL, a 2000-page (8 MB) cache and 4 KB pages, and SQLite 3.51.0 ran a WITHOUT ROWID BLOB-key table through prepared statements. SNKV was 1.64x faster on 1000-row-batch sequential inserts, 1.77x on 50K random reads, 1.85x on a full scan, 1.9-2x on 10K random updates and 5K random deletes, and 1.79x on a 20K-op 70/20/10 read/write/delete mix. The docs page's methodology (16-byte random keys, 100-byte values, an 80/20 mix, and both '3 runs averaged' and 'best time reported') does not match that code.

## Use it when

- You already use SQLite from C/C++ as a plain key-value table (one key column, WITHOUT ROWID) and want the same crash-safe B-tree/WAL storage with less CPU per operation. Small records fit best: the benchmark used 12-byte keys and 20-61-byte values.
- Ordered-key workloads in one embedded file that need range, prefix and reverse iteration; a full sequential scan was 1.85x faster than SQLite's ORDER BY key scan.
- Session stores, caches and leases that need per-key expiry without a background thread: native TTL with lazy eviction plus an explicit kvstore_purge_expired().
- Embedded or small-footprint C targets where one generated header (snkv.h) or a static library with no external dependencies is easier to ship than LMDB or RocksDB. CI builds and tests on Linux x86-64 and arm64, macOS and Windows (MSYS2 MinGW).
- Setups that already replicate or back up SQLite at the page/WAL level, such as LiteFS, and want a KV interface on top.

## Skip it when

- You need SQL, secondary indexes, the sqlite3 CLI or any other schema-level SQLite tooling: an SNKV file is not a readable SQLite database, and existing SQLite databases cannot be opened as SNKV stores.
- Maximum write throughput or read latency matters most. The README itself points to RocksDB for write throughput and LMDB for read speed, and the gain over SQLite is only 1.6-2x (1.17x on a single-transaction bulk insert, per the docs page).
- Large values. Key and value share one B-tree cell, so an entry larger than the index page's local-payload limit ((usable-12)\*64/255-23 bytes, about 1 KB on 4 KB pages) spills to overflow pages, and any seek comparison that lands on such a cell first copies the whole key+value payload into a malloc'd buffer.
- Data you cannot afford to lose on a young engine. It has one maintainer, every release is marked pre-release (v0.7.x), the repo was created in January 2026, and fixes in June-July 2026 covered an encrypted-open bug that bricked stores, a use-after-free in kvstore_errmsg and 'atomicity issues'. SQLite upstream fixes arrive only when the maintainer ports them (the project started on a SQLite 3.3.0-era B-tree before moving to 3.51.2, issue #5). Nobody has independently reproduced the benchmarks.

## How it is fast

Each entry is one blob, [4-byte big-endian key length][key][value], in an index-style (BLOBKEY) SQLite B-tree. SNKV replaces sqlite3VdbeRecordCompare with a plain memcmp on the key, so a get is a direct sqlite3BtreeIndexMoveto with no VDBE bytecode dispatch, statement reset or record-format encoding. Each handle also keeps a persistent read transaction and one cached read cursor per column family, which skips the per-statement cursor open/close and transaction begin/end that SQLite pays. On Hacker News the author said the cached cursor, not SQL parsing, is the bigger source of the gain (the SQLite benchmark already uses prepared statements). Page layout, WAL, cache and fsync policy are all unchanged SQLite code, so the gain can be no more than the SQL layer's per-operation overhead, which these benchmarks put at roughly 1.2-2x.

## Compared with alternatives

Among the siblings benchmarked against SQLite, CalicoDB and ForestDB are separate storage engines that claim larger gains (for example about 4.3x on CalicoDB's 100 KB-value random reads, and up to 8x reads for ForestDB), and CacheAdvance is an append-only log rather than a keyed store. Pick SNKV when you want to keep SQLite's exact B-tree, WAL format and crash-recovery code (and LiteFS compatibility) and only drop the SQL-layer overhead from C. For LSM-scale write throughput, a RocksDB-class sibling such as SplinterDB or Speedb fits better, as SNKV's own README concedes.

## Integration

| | |
|---|---|
| **Form** | static lib (libsnkv.a via make) or single-header amalgamation (snkv.h generated by make snkv.h and attached to releases since v0.7.2) |
| **Dependencies** | none external: SQLite 3.51.2's B-tree/pager/WAL/OS layers and Monocypher are bundled; links pthread and libm on POSIX. The optional vector build bundles usearch and needs a C++ compiler. |
| **Minimum toolchain** | Not documented. The Makefile defaults to gcc, and the code mixes declarations and statements, so it needs at least C99. The vector build needs g++ with -std=c++17. On Windows the README requires MSYS2 MinGW-w64 (a v0.1.3 release fixed MSVC, but MSVC is not in CI). |
| **Platforms** | Linux x86-64 and arm64, macOS, and Windows (MSYS2 MINGW64) are built and tested in CI; 32-bit, big-endian and other OSes are not documented |
| **Thread safety** | One KVStore handle per thread or process is the default model: WAL locks give one writer and concurrent readers across handles. Sharing one handle between threads requires KVStoreConfig.fullMutex=1, which kvstore_open() never sets; iterators must stay on one thread. The API spec says every call is always mutex-protected, but the header and code disagree: without fullMutex the handle-level mutex is a no-op and only a per-column-family mutex is taken. |
| **Drop-in for the baseline** | partial — it replaces SQLite only where SQLite serves as a key-value table from C/C++, behind a different, SQL-free API; the file formats are not interchangeable at the schema level |

## Gotchas

- A zeroed KVStoreConfig does not give you the defaults. journalMode 0 means DELETE (rollback journal), not WAL, and syncLevel 0 means SYNC_OFF, so opening with `KVStoreConfig cfg = {0}` gives a non-WAL store with no fsync unless you set both fields. The header comment claims unset fields fall back to defaults; the code and README contradict it. Passing NULL, or calling kvstore_open(), does give WAL + NORMAL.
- By default there is no automatic WAL checkpoint (walSizeLimit=0), whereas SQLite auto-checkpoints every 1000 pages. The -wal file grows until you call kvstore_checkpoint() or set walSizeLimit. The published benchmark ran with this default while the SQLite side kept auto-checkpointing, which flatters SNKV's write numbers.
- Each handle keeps a persistent read transaction open between calls and reopens it only when that handle writes, rolls back or checkpoints; gets never refresh it. Reading the source, a handle that only reads seems to stay on the WAL snapshot it opened and may not see other connections' commits. Also, until a June 2026 fix, a stale cached cursor stopped kvstore_checkpoint() from truncating the WAL. Test cross-handle freshness before relying on it.
- kvstore_get returns a heap copy that you must free with snkv_free (one allocation per read), while iterator key/value pointers are borrowed and valid only until the next move. The key/value size limits are compile-time macros (KVSTORE_MAX_KEY_SIZE, KVSTORE_MAX_VALUE_SIZE), and there are at most 64 column families.

## Known shortcomings

- Both benchmark builds default to -O0 (SNKV Makefile BUILD=debug; the SQLite side is gcc -g -Wall with no -O), and the win comes from skipping SQLite's SQL layer.
- The speedup comes from skipping SQLite's VDBE bytecode interpreter plus a cached read cursor and a read transaction held open between calls (the SQLite side already used prepared statements). Asymmetric bench: SQLite auto-checkpoints every 1000 pages while SNKV never checkpoints by default. The documented methodology does not match the benchmark code.
- A zeroed KVStoreConfig gives a rollback journal (not WAL) with no fsync, contrary to the header comment; the WAL grows until a manual checkpoint; a read-only handle likely stays on an old snapshot (from source reading). Pre-release v0.7.x from a single maintainer, with 2026-06/07 fixes for a bricked encrypted store, a use-after-free and atomicity; the handle mutex is off unless fullMutex=1.

## Caveats and trade-offs

The SNKV side comes from tests/test_benchmark.c. The SQLite side comes from a separate 0-star repo, hash-anu/sqllite-benchmark-kv, whose README only says 'run make test'. No CPU model, compiler version or build mode is stated. That repo compiles sqlite3.c with gcc -g -Wall and no optimization flag (-O0), and SNKV's Makefile defaults to a -O0 debug build, so both sides may have been unoptimized; the result may not hold at -O2/-O3. SNKV is SQLite's own B-tree/pager/WAL with the SQL parser, planner and VDBE removed, so the gain is from skipping the SQL layer, not from a faster storage engine. The linked LMDB and RocksDB comparison repos (hash-anu/lmdb-benchmark, hash-anu/rocksdb-benchmark) contain only source code and no published numbers; the README itself suggests RocksDB for maximum write throughput and LMDB for maximum read speed.

Skips SQL layer entirely (no parser/query planner/VDBE), so loses SQL query capability; gains native TTL, encryption, column families and an optional HNSW vector index. Not compatible with the sqlite3 CLI for schema-level access.

## Maintenance

Active single-maintainer project (created January 2026, last commit 2026-09-26, 78 stars, pre-release v0.7.x tags). It is Apache-2.0 with bundled public-domain SQLite and CC0 Monocypher and easy to vendor as one generated header; the Python bindings moved off master to a separate branch in September 2026.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks table compares SNKV directly against SQLite (WAL, synchronous=NORMAL, 8 MB cache, 4 KB pages, WITHOUT ROWID), and every claimed number matches. The code is public (tests/test_benchmark.c and the separate hash-anu/sqllite-benchmark-kv repo), but no CPU model, compiler version or build mode is stated, so these are first-party numbers with partial methodology: tier C. The Makefiles suggest both sides may be -O0 builds, which would also cap it at C.
- **Verifier notes:** Metadata checks out via gh: Apache-2.0, 78 stars, not a fork, not archived, last commit 2026-09-26, so active. The main new finding is that both benchmark builds default to -O0; tier stays C.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/hash-anu/snkv>
  - <https://github.com/hash-anu/snkv#benchmarks>
  - <https://github.com/hash-anu/snkv/blob/master/tests/test_benchmark.c>
  - <https://github.com/hash-anu/snkv/blob/master/Makefile>
  - <https://github.com/hash-anu/sqllite-benchmark-kv>
  - <https://github.com/hash-anu/sqllite-benchmark-kv/blob/master/Makefile>
  - <https://github.com/hash-anu/lmdb-benchmark>
  - <https://github.com/hash-anu/rocksdb-benchmark>
- **Sources the enricher read:**
  - <https://github.com/hash-anu/snkv>
  - <https://github.com/hash-anu/snkv#benchmarks>
  - <https://github.com/hash-anu/snkv/blob/master/include/kvstore.h>
  - <https://github.com/hash-anu/snkv/blob/master/src/kvstore.c>
  - <https://github.com/hash-anu/snkv/blob/master/src/btree.c>
  - <https://github.com/hash-anu/snkv/blob/master/Makefile>
  - <https://github.com/hash-anu/snkv/blob/master/tests/test_benchmark.c>
  - <https://github.com/hash-anu/snkv/blob/master/tests/test_multiprocess.c>
  - <https://github.com/hash-anu/snkv/blob/master/tests/test_review_fixes.c>
  - <https://github.com/hash-anu/snkv/blob/master/docs/api/API_SPECIFICATION.md>
  - <https://github.com/hash-anu/snkv/blob/master/docs/benchmark.html>
  - <https://github.com/hash-anu/snkv/blob/master/.github/workflows/c-cpp.yml>
  - <https://github.com/hash-anu/snkv/issues/5>
  - <https://github.com/hash-anu/snkv/issues/11>
  - <https://github.com/hash-anu/snkv/issues/65>
  - <https://github.com/hash-anu/snkv/pull/77>
  - <https://github.com/hash-anu/snkv/pull/78>
  - <https://github.com/hash-anu/snkv/commit/458a6589ea71973fc6435114d2a72a3a31664ea3>
  - <https://github.com/hash-anu/snkv/commit/c6dca6428a08657f0cd6789cec98b641be7dd09c>
  - <https://github.com/hash-anu/snkv/commits/master>
  - <https://github.com/hash-anu/snkv/releases>
  - <https://github.com/hash-anu/sqllite-benchmark-kv>
  - <https://github.com/hash-anu/sqllite-benchmark-kv/blob/main/Makefile>
  - <https://github.com/hash-anu/sqllite-benchmark-kv/blob/main/tests/sqlite-kv-benchmark.c>
  - <https://github.com/hash-anu/sqllite-benchmark-kv/blob/main/include/sqlite3.h>
  - <https://raw.githubusercontent.com/hash-anu/sqllite-benchmark-kv/main/src/sqlite3.c>
  - <https://github.com/hash-anu/lmdb-benchmark>
  - <https://github.com/hash-anu/rocksdb-benchmark>
  - https://hn.algolia.com/api/v1/search?query=snkv&tags=(story,comment)
  - <https://hn.algolia.com/api/v1/items/47136553>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/hash-anu/snkv`) · [data/wave6/enrich/raw/github_com_hash_anu_snkv.json](../../../data/wave6/enrich/raw/github_com_hash_anu_snkv.json) (enrichment confidence 0.78)

</details>
