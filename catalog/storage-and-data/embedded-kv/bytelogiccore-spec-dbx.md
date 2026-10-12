# DBX

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Beta pure-Rust HTAP embedded database whose key-value API edges out in-memory SQLite on a 10,000-row first-party benchmark.

| | |
|---|---|
| **Beats** | SQLite |
| **Claimed result** | 10,000 records, both engines in memory: INSERT 25.21 ms vs SQLite 29.4 ms (about 1.17x; the README rounds this to '1.16x faster, 25ms vs 29ms'). Point GET: 2.84 ms vs 33.8 ms (about 11.9x, derived from page data; the page itself says both '11x' and '13x'). Full SCAN: 51 µs vs 340 µs (about 6.7x, derived from page data). |
| **Workload** | Criterion.rs 0.5 bench official_db_comparison.rs: 10,000 string key/value pairs ('key_{i}' / 'value_data_{i}'). INSERT builds a fresh in-memory DB each iteration; GET does 10,000 point lookups; SCAN reads the whole table. DBX (v0.2.0-beta 'Fast-Path', Database::open_in_memory) vs SQLite (rusqlite 0.32 bundled, Connection::open_in_memory, one BLOB-keyed table). Sled 0.34 and Redb 2.1 run on temp dirs in the same suite. |
| **Metric** | throughput |
| **Hardware** | Windows 11 Pro (build 26200) x64 PC, about 16 GB RAM; CPU model not stated. |
| **Compiler and flags** | rustc 1.92.0 / Cargo 1.92.0, Cargo release profile, Criterion.rs 0.5; SQLite is rusqlite 0.32 with the bundled feature. No extra flags stated. |
| **Adoption** | 4 stars |
| **Last commit** | 2026-04-13 |
| **Links** | [repository](https://github.com/bytelogiccore-spec/DBX) · [benchmark](https://github.com/bytelogiccore-spec/DBX/blob/main/docs/english/benchmarks.md) |

## Verdict

The only comparison is a first-party Criterion run (3 Apr 2026; rustc 1.92.0 release profile; Windows 11 x64, 16 GB, CPU unstated) on 10,000 short string pairs, DBX open_in_memory against rusqlite 0.32 bundled in-memory SQLite: INSERT 25.21 ms vs 29.4 ms (\~1.17x), GET 2.84 ms vs 33.8 ms (\~11.9x), SCAN 51 us vs 340 us. Only the INSERT row is a like-for-like (and modest) win. The SQLite harness autocommits every insert and re-prepares SQL on every insert and lookup (conn.execute/query_row), so GET mostly measures statement compilation. The 51 us SCAN figure matches the repo's PERF_TRACKER entry for a DBX SQL SELECT count(\*) (where SQLite's count(\*) took 5.66 us), not the bench's db.scan(), which copies all 10,000 pairs.

## Use it when

- Rust services that want an in-process, ordered byte-key/value store with named tables, CAS helpers and serde struct storage (DatabaseSerde), and that value a pure-Rust API over SQLite's maturity
- Small, memory-resident datasets rebuilt at startup (open_in_memory or open_fast) where per-call SQL overhead would dominate. The only published comparison uses 10,000 short string pairs.
- Prototypes that want KV, SQL, Arrow/Parquet and optional CUDA aggregation in a single crate, and can pin a 0.x beta version and read the source when behaviour is unclear
- Replacing a naive rusqlite pattern (autocommit inserts, conn.execute/query_row re-preparing SQL on every call) where you control both sides and only need point get/put

## Skip it when

- Anything that relies on SQLite's durability record, stable file format or SQL compatibility. DBX is a 0.x beta from one developer with 390 total crates.io downloads, and v0.2.2 (13 Apr 2026) had to fix deletes that were never written to the WAL and get/delete calls routed to the wrong partition.
- Large on-disk tables. Native WOS compaction reads the whole table's SSTable into a BTreeMap and rewrites it every 5,000 WAL entries, so write cost and peak memory grow with table size. Nothing above 10,000 rows is benchmarked.
- Many concurrent readers on file-backed tables. Every get/scan that reaches a file-backed table's WOS takes that table's single Mutex. The in-memory WOS uses one RwLock for all tables, and secondary-index updates take an RwLock (README disclaimer).
- Counts and small aggregates. The repo's own PERF_TRACKER measured SQLite SELECT count(\*) at 5.66 us against 51 us for DBX. In the same run, file-backed per-row DBX inserts took 260.6 ms against 47.03 ms for rusqlite with a prepared statement.
- Lean builds. The default dependencies cannot be turned off and include arrow/parquet 54, tokio, s2n-quic, sqlparser, zstd, reed-solomon-erasure and several crypto crates, even if you only use the KV API.

## How it is fast

Writes land in a Tier-1 'Delta' store: one crossbeam SkipMap per table inside a DashMap. There is no SQL parsing, statement preparation or per-statement transaction on the KV path. When the global entry count reaches 10,000 (the default threshold, and exactly the benchmark size), insert() drains Delta into the WOS on the calling thread. For open_in_memory the WOS is a std BTreeMap per table behind one RwLock, so the benchmarked GET is essentially a BTreeMap lookup plus a Vec clone. The file-backed 'Native WOS' is a dirty buffer, an append-only WAL and a 4 KB-page SSTable with a sparse index and LRU page cache. The v0.2.0 'Fast-Path' changes the SQL executor (it skips the distributed DAG scheduler and mpsc channels), not the storage.

## Compared with alternatives

The other catalogued SQLite-beaters, CalicoDB (C++17 B+-tree, \~4.3x faster random reads), SNKV (1.6-2x at 1M records) and ForestDB (up to 8x reads), are measured at larger scale and on durable storage. Pick DBX only if you need a pure-Rust crate that bundles KV, SQL, Arrow/Parquet and optional CUDA, and you accept beta risk. For a proven on-disk KV store, prefer a sibling.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | arrow 54, parquet 54, tokio, s2n-quic + rcgen, sqlparser 0.52, dashmap, crossbeam-skiplist, rayon, zstd, reed-solomon-erasure, aes-gcm-siv/chacha20poly1305/hkdf/sha2, bincode, serde, cron, chrono, tempfile, and others (all non-optional); optional cudarc 0.19 (CUDA 12.5) behind the 'gpu' feature |
| **Minimum toolchain** | Rust edition 2024 (so Rust 1.85+); no rust-version declared; the benchmarks used rustc 1.92.0 |
| **Platforms** | Pure Rust. CI builds and tests on ubuntu-latest (x86-64) only, and the published benchmarks ran on Windows 11 x64. A prebuilt win32-x64-msvc Node binary is committed. macOS and aarch64 support are not documented. GPU paths need NVIDIA CUDA. |
| **Thread safety** | Methods take &self, Database::open returns Arc&lt;Database&gt;, and the transactions guide shares one handle across threads. The Delta tier uses DashMap + SkipMap, the in-memory WOS one global RwLock, and the file WOS one Mutex per table. Snapshot isolation is claimed for begin_transaction(). Send/Sync bounds are not documented explicitly. |
| **Drop-in for the baseline** | no |

## Gotchas

- The MVCC tags can collide with user bytes. scan() treats values that start with [0x00,0x01] as MVCC values and strips those 2 bytes. It treats values that start with [0x00,0x02] as tombstones and drops the row. Keys of 10+ bytes that end in [0xDB,0x58] are parsed as versioned keys and lose their last 10 bytes. The get() fast path returns raw bytes, so get and scan can disagree on binary data. A source comment wrongly assumes binary data never starts with 0x00.
- Database::open defaults to DurabilityLevel::Lazy. append_to_wal only requests an fsync at Full, so acknowledged writes can be lost on a crash. Use open_safe for per-write fsync. open_in_memory has no WAL at all.
- insert() flushes Delta into the WOS synchronously on the caller's thread when the global entry count (all tables, overwrites included) reaches 10,000, which causes periodic latency spikes. Every insert also allocates a lossy UTF-8 copy of the key for partition routing.
- The docs are inconsistent. The storage-layers guide still says the WOS is built on sled (removed in 0.2.0) and that Tier 1 is a BTreeMap (the code uses DashMap + SkipMap). The benchmarks page mixes v0.0.6 and v0.2.0 numbers. open_in_memory also spawns a background worker thread per database.

## Known shortcomings

- INSERT is only 1.16x vs SQLite; the GET \~11.9x / SCAN \~6.7x are derived. The SQLite harness re-prepares statements each call and the benchmark page contradicts itself; no CPU model.
- The only fair win is INSERT (\~1.17x, 10k rows, in-memory); the 11.9x GET is inflated because the SQLite side re-prepares SQL each call. The 51 us SCAN is DBX's SQL count(\*), not the benchmarked scan(); the same doc shows SQLite count(\*) at 5.66 us (9x faster) and DBX file inserts at 260.6 ms vs rusqlite 47 ms.
- Data bug: values starting 0x00 0x01/0x02, or 10+ byte keys ending 0xDB 0x58, are mangled or dropped by scan() (get() and scan() disagree). Compaction rewrites the whole table every 5k WAL entries; default Lazy durability loses acknowledged writes on crash. Heavy non-optional dependencies (arrow/parquet, tokio, s2n-quic); beta, one developer, no commits since 2026-04-13 (whose CI failed); docs stale.

## Caveats and trade-offs

Very small, very new project (4 stars, created Feb 2026, single first-party report dated 3 Apr 2026). No CPU model, and the sample is only 10,000 records. The benchmarks page contradicts itself: INSERT is called both 14% and 18% faster, GET both 11x and 13x, and the conclusion cites older v0.0.6 numbers (INSERT 44.92 ms, SCAN 1.60 ms). The 'Fast-Path' section says DBX scan fell from 340 µs to 51 µs, and 340 µs is also the figure given for SQLite. The bench code does not match the documented method. The doc says SQLite runs inside a transaction, but the code inserts in autocommit mode. SQLite lookups use conn.query_row, which re-prepares the SQL for every one of the 10,000 lookups; that handicaps the 'GET 11-13x' result. The README says Tier 1 is a BTreeMap, but the benchmarks page says DashMap + SkipMap. The README is marketing-heavy and has an unfilled Ko-fi placeholder link. GitHub reports NOASSERTION because the LICENSE file adds a donation/sponsorship section after the standard MIT text; the grant itself is plain MIT. Low confidence.

0.2.0-beta software; the README's larger '29x' and '4.5x GPU' claims are versus 'traditional B-Tree engines' and CUDA baselines, not versus SQLite directly, so only the 1.16x figure is a real SQLite comparison.

## Maintenance

Young single-author project: created Feb 2026, 197 commits, no issues ever filed, 4 stars. The last commit and 0.2.2 release were on 13 Apr 2026, and that commit's CI run failed in the Node-binding job. It is MIT-licensed (a donation appendix makes GitHub show NOASSERTION) and usable from crates.io, but it is too large and immature to vendor as a SQLite replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Criterion run against bundled SQLite (rusqlite 0.32). The bench code is public (core/dbx-benchmarks/benches/official_db_comparison.rs) and rustc 1.92.0 with the release profile is stated, but no CPU model is given (only 'Windows 11 Pro, x64, 16 GB'), so it cannot be A.
- **Verifier notes:** The README figures (1.16x, 25ms vs 29ms) are on the README and match the fuller table in docs/english/benchmarks.md, so benchmark_url now points to that page, which also has the methodology. The GET and SCAN wins over SQLite are larger, but they rest on a SQLite harness that re-prepares statements. Metadata checked: 4 stars, not a fork or archived, last default-branch (main) commit 2026-04-13 (active), MIT.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bytelogiccore-spec/DBX>
  - <https://github.com/bytelogiccore-spec/DBX#-2-blazing-fast-performance>
  - <https://raw.githubusercontent.com/bytelogiccore-spec/DBX/main/docs/english/benchmarks.md>
  - <https://raw.githubusercontent.com/bytelogiccore-spec/DBX/main/core/dbx-benchmarks/benches/official_db_comparison.rs>
  - <https://raw.githubusercontent.com/bytelogiccore-spec/DBX/main/core/dbx-benchmarks/Cargo.toml>
  - <https://raw.githubusercontent.com/bytelogiccore-spec/DBX/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/bytelogiccore-spec/DBX>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/README.md>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/docs/english/benchmarks.md>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-benchmarks/benches/official_db_comparison.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-benchmarks/benches/phase7_tiering_benchmarks.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/PERF_TRACKER.md>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/CHANGELOG.md>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/Cargo.toml>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/Cargo.toml>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/LICENSE>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/.github/workflows/ci.yml>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/engine/crud.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/engine/constructors.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/engine/database.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/engine/types.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/engine/utilities.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/storage/delta_store.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/storage/memory_wos.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/storage/native_wos/mod.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/storage/native_wos/backend.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/storage/native_wos/table_store.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/core/dbx-core/src/transaction/mvcc/version.rs>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/docs/english/architecture.md>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/docs/english/guides/storage-layers.md>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/docs/english/guides/transactions.md>
  - <https://github.com/bytelogiccore-spec/DBX/blob/main/docs/english/getting-started.md>
  - <https://github.com/bytelogiccore-spec/DBX/issues>
  - <https://github.com/bytelogiccore-spec/DBX/pulls>
  - <https://github.com/bytelogiccore-spec/DBX/actions/workflows/ci.yml>
  - <https://github.com/bytelogiccore-spec/DBX/graphs/contributors>
  - <https://crates.io/api/v1/crates/dbx-core>
  - <https://hn.algolia.com/api/v1/search?query=bytelogiccore&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=DBX%20HTAP%20embedded%20database%20Rust>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/bytelogiccore-spec/dbx`) · [data/wave6/enrich/raw/github_com_bytelogiccore_spec_dbx.json](../../../data/wave6/enrich/raw/github_com_bytelogiccore_spec_dbx.json) (enrichment confidence 0.8)

</details>
