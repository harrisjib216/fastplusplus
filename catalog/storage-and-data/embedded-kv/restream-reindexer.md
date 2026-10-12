# Reindexer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Embeddable in-memory document database (C++ core, Go API) with secondary and full-text indexes; first-party benchmarks show 3-6x SQLite on indexed reads.

| | |
|---|---|
| **Beats** | SQLite 3.17.0 via mattn/go-sqlite3 and sqlx, opened with DSN '/tmp/foo.db?mode=memory&cache=shared' (no 'file:' prefix, so go-sqlite3 drops the query string and SQLite runs as an on-disk /tmp/foo.db with default settings, not in memory), with indexes on name and year and an FTS5 table; also compared with Redis, Tarantool, MySQL, MongoDB, Elasticsearch, Sphinx, ArangoDB, RethinkDB and (web only) ClickHouse |
| **Claimed result** | Single-core by-ID 4,224 ns/op vs SQLite 23,735 (5.6x) and Redis 47,492 (11.2x), 1-condition 3.5x, 2-condition 2.7x (derived from page data) stand; the web-table rows and the 32x full-text row serve cached object pointers against unmarshalling baselines and are not like for like. |
| **Workload** | 100K-document set (id, name, year with tree index, description with text index); Go benchmarks in-process on one core for get-by-id, 1-condition and 2-condition queries (limit 10) and full-text; plus wrk web benchmark on 8 cores for by-id, filters, full-text and update. |
| **Metric** | latency and throughput |
| **Hardware** | 2.7 GHz Intel Core i7, MacBook Pro Retina 15-inch mid 2016 (exact SKU not stated); web runs in Ubuntu 16.04 Docker on the same laptop with 8 cores |
| **Compiler and flags** | Go 1.9.3 and clang-802.0.42 (Apple clang); optimisation flags not stated |
| **Adoption** | 812 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/Restream/reindexer) · [benchmark](https://github.com/Restream/reindexer-benchmarks) |

## Verdict

Restream's own Go benchmarks (Go 1.9.3, clang-802.0.42, 2016 MacBook Pro 2.7 GHz Core i7, 100K documents, one core) show Reindexer by-ID gets at 4,224 ns/op vs 23,735 for SQLite 3.17.0 through go-sqlite3 (5.6x) and 1-condition queries at 17,403 vs 60,749 ns/op (3.5x), with both sides unmarshalling; an 8-core wrk web test in Docker on the same laptop gives 158,797 vs 28,496 by-ID RPS, but there Reindexer serves from its object cache while SQLite unmarshals and re-prepares per request. The SQLite baseline ran on disk despite an in-memory DSN.

## Use it when

- A Go service that needs microsecond-scale, in-process lookups by primary key or indexed fields on a data set that fits in RAM: single-core by-ID gets measured at 4,224 ns with full unmarshalling vs 23,735 ns for SQLite via go-sqlite3.
- Read-heavy catalogue or metadata stores (the benchmark's 100K-document shape: id, name, year, description) that need filters, sorting, joins and full-text search in one embedded engine instead of SQLite plus FTS5.
- Read-mostly workloads that can use the object cache with treat-as-immutable results, where by-ID gets drop to 2,530 ns with zero allocations.
- You need to switch later from embedded to client-server without changing the query API (builtin, builtinserver and standalone modes share the Go interface).

## Skip it when

- Data larger than RAM: every namespace is loaded fully into memory and disk is only a LevelDB backup.
- Write-heavy or durability-critical work: disk writes happen asynchronously in background batches, and in the vendor's own web table Redis (30,025 RPS) and Tarantool (33,905) beat embedded Reindexer (27,000) on updates.
- Non-Go applications wanting an embedded library: the embedded path is the Go binding; Python and Java connectors exist, and the internal C++ API is documented as unstable.
- Ad-hoc SQL over arbitrary columns or multi-statement transactions with fine-grained isolation: only indexed fields are queryable and each transaction takes an exclusive lock on its namespace.

## How it is fast

Documents and indexes live in dense C++ structs outside Go's garbage collector, with about 32 bytes overhead per document plus 4-16 bytes per index, duplicate strings merged and sync.Pool-reused query buffers, so most queries allocate nothing. Indexed lookups go straight to per-field hash indexes (EQ/SET) or tree indexes (ranges, sorting) with no SQL parse or plan step on the builder path. On the Go side an optional object cache returns already-deserialized structs, and AllowUnsafe(true) hands back shared pointers into that cache, which is where the fastest benchmark rows come from. Writes to disk are batched asynchronously in the background.

## Compared with alternatives

Pick Reindexer over mpedb or LMDB when you want an in-memory document store with secondary, sorted and full-text indexes behind a Go query builder rather than a raw key-value or SQL interface; pick LMDB when data exceeds RAM or commits must be durable on return, and SQLite-replacement siblings such as mpedb when you need SQL semantics.

## Integration

| | |
|---|---|
| **Form** | static lib (C++ core linked into a Go program through the builtin cgo binding) or standalone server with Go, Python and Java clients |
| **Dependencies** | CMake, LevelDB (snappy in the Go module); OpenMP and BLAS/LAPACK only for FAISS-based IVF vector indexes (HNSW-only build available) |
| **Minimum toolchain** | C++20: g++ 10+, clang 15+ or mingw64; Go 1.24 for the v5 module |
| **Platforms** | Linux x86_64 packages (RHEL/CentOS/Fedora, Debian/Ubuntu, Redos, AltLinux), Windows 64- and 32-bit installers (32-bit HNSW-only), macOS from source; other architectures not documented |
| **Thread safety** | Database handle usable from many goroutines (one binding multiplexes up to 32 simultaneous streams); Transaction objects are not thread safe; objects returned with AllowUnsafe(true) are shared and must not be modified |
| **Drop-in for the baseline** | no |

## Gotchas

- Web table is not like for like: the benchmark server's main.go calls ForceObjCache() on the Reindexer repo, so every 'Reindexer Embeded/Standalone' web row serves shared pointers from the object cache while SQLite, MySQL and the others unmarshal every row; in addition the SQL repos call Preparex and Close on every HTTP request (each handler runs QueryByID(1, ...) and the like), so SQLite and MySQL recompile their statement per request. The readme discloses neither.
- Single-core full-text rows are not like for like either: the Reindexer QueryFullText harness always sets AllowUnsafe(true) (object cache on, 109 B and 1 alloc per op) while SQLite StructScans every row, and the SQLite query adds ORDER BY rank (BM25 sort of all matches) over an FTS5 table that also indexes id, name and year; the 32x full-text figure is therefore not a fair engine comparison. The by-ID and 1-/2-condition 'object cache disabled' rows do unmarshal on both sides.
- SQLite ran on disk, not in memory: repo/sqlite.go opens '/tmp/foo.db?mode=memory&cache=shared' without the 'file:' prefix, and go-sqlite3 v1.6.0 cuts the query string in that case (sqlite3.go line 859), so updates paid a synced rollback journal with a 5,000 ms busy timeout under 8 pooled connections, and sqlUpdate only logs errors, so failed updates still count as served requests. Reindexer itself persists asynchronously, so the 27,000 vs 452 update gap is mostly durability.
- Smaller asymmetries: the SQLite by-ID benchmark draws one random id per benchmark call and re-reads it N times while Reindexer draws a new id per iteration (favours SQLite); Redis, Tarantool, MySQL and the other servers are reached over TCP while Reindexer embedded and SQLite run in-process; the harness imports an internal git.restream.ru module path, so it cannot be rebuilt as published.

## Known shortcomings

- Tier C: the reindexer-benchmarks SQLite baseline is not in-memory (the DSN '/tmp/foo.db?mode=memory&cache=shared' lacks the 'file:' prefix and go-sqlite3 v1.6.0 strips the query, so it ran as an on-disk file with a synced journal), making the update row (27,000 vs 452) a durability artefact; Redis and Tarantool are faster on update; Dockerfile versions differ from the README; Go 1.9.3 and clang-802.0.42 stated, flags and CPU SKU missing; Redis over TCP vs Reindexer in-process.
- Enricher: the web-table rows are not a fair engine comparison because benchmark main.go calls ForceObjCache(), so every Reindexer web row serves shared object-cache pointers while SQLite and MySQL unmarshal, and the SQL repos Preparex+Close per HTTP request; the 32x full-text figure likewise runs QueryFullText with AllowUnsafe(true) while SQLite StructScans and adds ORDER BY rank. SQLite ran on disk; Reindexer persists asynchronously so the update gap is durability; sqlUpdate logs errors but still counts the request; the harness imports an internal git.restream.ru path so it cannot be rebuilt. The single-core by-ID, 1-condition and 2-condition rows (5.6x, 3.5x, 2.7x) unmarshal on both sides and stand.

## Caveats and trade-offs

First-party benchmark (Restream) on one 2016 laptop with 2018-era versions (Go 1.9.3, Tarantool 1.7.6.12, Elasticsearch 5.4.3, SQLite 3.17.0, MongoDB 3.4.5); optimisation flags and exact CPU SKU not stated, so tier C rather than A. SQLite baseline misconfigured: repo/sqlite.go opens '/tmp/foo.db?mode=memory&cache=shared' without the 'file:' prefix, and go-sqlite3 (v1.6.0 sqlite3.go Open) strips the query string in that case, so SQLite ran as an on-disk file with the default rollback journal and synchronous=FULL rather than in memory; this mostly inflates the update row (27,000 vs 452 RPS) and adds syscall cost to reads. The Dockerfile used for the web runs installs Go 1.9.2, Elasticsearch 6.x and MongoDB 3.6, not the versions the README lists, and builds Reindexer with make EXTRA_CFLAGS=-DNDEBUG; wrk results are the best of ten 2-second runs per cell (run_benches.sh). The current harness code (go-redis with context API) postdates the published numbers, and the benchmark repo has 2 commits and 1 star. The README labels Redis '2.3.9', which looks like a client or typo rather than a server release; Redis is reached over TCP on 127.0.0.1:6379 through go-redis while Reindexer and SQLite run in-process, so the Redis and other server rows include a network round trip. Redis 1-condition query is a ZRANGEBYSCORE on a sorted set of JSON blobs and Redis has no 2-condition or full-text row. Reindexer is not fastest on update in the web table: Redis 30,025 RPS and Tarantool 33,905 RPS beat embedded Reindexer 27,000. 'Object cache' rows (2,530 ns/op) skip unmarshalling in the other databases, so are not like for like. The benchmark repo imports an internal module path (git.restream.ru/itv-backend/reindexer) instead of the public GitHub path. Reindexer main README claims only 'on par with a typical key-value database' and up to 500K by-id queries/sec per core. Initial category guess was caches; moved to embedded-kv because the benchmark's closest like-for-like baseline is in-process SQLite. [retier] SQLite ran on disk; Reindexer persists asynchronously (update gap is durability); harness imports an internal git.restream.ru path and cannot be rebuilt; sqlUpdate counts failed requests.

In-memory database: the whole data set lives in RAM (persisted to disk, but sized by memory). C++ core with a Go API; other bindings and a standalone server mode exist (standalone mode is 30 to 35 percent slower than embedded in the web table). Document model with its own query builder, not a plain key-value API.

## Maintenance

Actively maintained (v5.17.0 on 2026-09-26, code arrives as periodic vendor drops plus a few community PRs), Apache-2.0 and production-used, but the benchmark repo has 2 commits, 2018-era database versions and harness asymmetries that favour Reindexer on the web and full-text rows.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Restream benchmark with public Go harness (reindexer-benchmarks: bench_queries_test.go, bench_text_test.go, repo/\*.go, run_benches.sh, Dockerfile) and Go 1.9.3 / clang-802.0.42 named, but no optimisation flags for the Mac build and no exact CPU SKU, and the SQLite baseline is misconfigured; tier C.
- **Verifier notes:** All quoted numbers are on the reindexer-benchmarks readme; metadata confirmed (Apache-2.0, 812 stars, last commit 2026-09-26 'Update to version v5.17.0'). Shortcoming to record: the SQLite baseline described as in-memory actually ran on disk because go-sqlite3 ignores 'mode=memory&cache=shared' without a 'file:' prefix (update row 60x is a durability artifact), plus 2018-era versions, Docker versions differing from README, and Redis/Tarantool faster on update.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-89 (wave 6); enricher w6 pair-016
- **Pages the verifier opened:**
  - <https://github.com/Restream/reindexer-benchmarks>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/readme.md>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/init_test.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/bench_queries_test.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/run_benches.sh>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/Dockerfile>
  - <https://github.com/Restream/reindexer-benchmarks/tree/main/repo>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/repo/sqlite.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/repo/sql.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/repo/reindex.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/repo/redis.go>
  - <https://raw.githubusercontent.com/mattn/go-sqlite3/v1.6.0/sqlite3.go>
  - <https://github.com/Restream/reindexer>
  - <https://github.com/Restream/reindexer/commits>
- **Sources the enricher read:**
  - <https://github.com/Restream/reindexer>
  - <https://github.com/Restream/reindexer/commits/master>
  - <https://github.com/Restream/reindexer/issues?q=is%3Aissue+crash+OR+segfault+OR+performance>
  - <https://github.com/Restream/reindexer/pull/100>
  - <https://raw.githubusercontent.com/Restream/reindexer/HEAD/readme.md>
  - <https://raw.githubusercontent.com/Restream/reindexer/HEAD/cpp_src/readme.md>
  - <https://raw.githubusercontent.com/Restream/reindexer/HEAD/go.mod>
  - <https://github.com/Restream/reindexer-benchmarks>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/readme.md>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/init_test.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/bench_queries_test.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/bench_text_test.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/main.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/http.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/run_benches.sh>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/repo/sqlite.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/repo/sql.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/repo/reindex.go>
  - <https://raw.githubusercontent.com/Restream/reindexer-benchmarks/HEAD/repo/redis.go>
  - <https://raw.githubusercontent.com/mattn/go-sqlite3/v1.6.0/sqlite3.go>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/restream/reindexer`) · [data/wave6/enrich/raw/github_com_restream_reindexer.json](../../../data/wave6/enrich/raw/github_com_restream_reindexer.json) (enrichment confidence 0.75)

</details>
