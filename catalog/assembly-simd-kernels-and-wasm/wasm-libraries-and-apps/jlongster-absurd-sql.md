# absurd-sql

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `JavaScript backend for SQLite compiled to WebAssembly (sql.js)` · `MIT` · 🔴 abandoned

> IndexedDB-backed block storage for sql.js (SQLite in WebAssembly); its own browser benchmark shows it beating one-row-per-record IndexedDB.

| | |
|---|---|
| **Beats** | IndexedDB used directly in the browser |
| **Claimed result** | README: 'It consistently beats IndexedDB performance up to 10x' for reads and bulk-insert writes (shown only as chart images, no numbers readable). |
| **Workload** | SQLite on top of IndexedDB blocks: read 'SELECT SUM(value) FROM kv' and bulk insert, compared with plain IndexedDB, in Chrome. |
| **Metric** | throughput |
| **Hardware** | 2015 MacBook Pro (CPU model not given) |
| **Adoption** | 4.3k stars |
| **Last commit** | 2023-08-06 |
| **Links** | [repository](https://github.com/jlongster/absurd-sql) · [benchmark](https://github.com/jlongster/absurd-sql) |

## Verdict

The author's own browser benchmark (src/examples/bench) times SELECT SUM(value) over a kv table and bulk inserts of 100 to 100,000 rows through sql.js on absurd-sql, against the same operations on a raw IndexedDB object store with one record per row, in Chrome on a 2015 MacBook Pro, and the README reports up to 10x in favour of absurd-sql; the per-size values exist only as chart images that could not be opened here, and the baseline uses per-record cursor reads and an unawaited clear inside the write timer.

## Use it when

- You want a relational, transactional, persistent store in the browser and are already using sql.js; absurd-sql gives page-granular persistence instead of exporting the whole database image.
- Workloads that scan or bulk-insert many small rows (tens of thousands and up), where one IndexedDB record per row is the bottleneck.
- Apps that can serve COOP/COEP cross-origin isolation headers and run all database work in a dedicated Web Worker.
- Legacy code bases built on it (Actual Budget used it) that need to keep an existing IndexedDB-resident database readable.

## Skip it when

- New projects: the official SQLite WASM build and wa-sqlite now persist through the Origin Private File System (synchronous access handles), which avoids the IndexedDB indirection altogether; absurd-sql's own description still says 'hopefully a better backend soon'.
- Production apps that need a maintained dependency: last commit 2023-08-06, 37 open issues and 4 open PRs, a community fork (trong-orm/better-absurd-sql) was started because the project 'looks more abandoned than live', and the author asked users to move questions to Discussions.
- Sites that cannot set Cross-Origin-Opener-Policy/Cross-Origin-Embedder-Policy headers, or need to run on the main thread or in a service worker; without SharedArrayBuffer the fallback mode allows only one writing tab at a time.
- Small key-value lookups: the benchmark only shows full-table SUM scans and bulk inserts, and a well-batched IndexedDB pattern (getAll/getAllKeys pages, chunked records) was never measured against it.
- Large datasets on the pinned sql.js: issue #53 reports a severe memory leak in the @jlongster/sql.js 1.6.7 build used by absurd-sql (fixed upstream in sql.js commit ec44c18 but not in the published fork).

## How it is fast

IndexedDB has a high per-request and per-record overhead, and SQLite packs roughly a hundred small rows into one 4 KB page, so a full scan or bulk insert touches far fewer IndexedDB records than storing one record per row. SQLite's synchronous VFS calls are bridged to the asynchronous IndexedDB API with SharedArrayBuffer and Atomics.wait, which lets one IndexedDB transaction stay open for the whole SQLite lock span (shared lock maps to a readonly transaction, exclusive lock to readwrite). The IndexedDB worker detects three forward or backward sequential block reads within 10 blocks and switches from get() to an openCursor()/advance() read-ahead, and dirty pages are buffered until fsync and written as one bulk put in a single transaction.

## Compared with alternatives

Pick absurd-sql over DuckDB-Wasm when you need persistent, transactional row storage in IndexedDB with SQLite semantics rather than in-memory analytical scans; none of the other wasm siblings (hash-wasm, sax-wasm, markdown-wasm and similar) address browser persistence at all.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | @jlongster/sql.js 1.6.7 (the author's sql.js fork with register_for_idb), safari-14-idb-fix; a bundler that can build Web Workers |
| **Minimum toolchain** | Browser with WebAssembly, Web Workers and IndexedDB; SharedArrayBuffer and Atomics plus cross-origin isolation for the main mode; package.json declares no engine or TypeScript types (issue #35) |
| **Platforms** | Browsers only (benchmarked in Chrome); Safari runs in the fallback mode without SharedArrayBuffer, with worker creation proxied through the main thread because it lacked nested workers; no official supported-browser list (issue #45); not Node |
| **Thread safety** | Single worker per connection; multi-tab access is coordinated by mapping SQLite locks to IndexedDB transactions, and in fallback mode a second writing tab gets an error instead of corrupting the database |
| **Drop-in for the baseline** | partial — no: it replaces direct IndexedDB access with SQL through sql.js, with a worker and cross-origin isolation required; existing IndexedDB object stores are not readable through it. |

## Gotchas

- Harness flaw on the write benchmark: main.worker.js populate() calls q.clear(db) without awaiting it, and for raw IndexedDB clear() opens its own readwrite transaction; the timed populate transaction on the same store cannot start until that clear commits, so every raw-IndexedDB write timing in writeBench (100 to 100,000 rows) also includes deleting the previous run's rows, while the SQLite clear (DROP/CREATE TABLE) runs synchronously before its timer starts.
- Read benchmark baseline is the slowest IndexedDB pattern: queries-raw-idb.js sumAll walks openCursor() one record per continue() over one record per row, while absurd-sql reads about a hundred rows per 4 KB block; the SQLite timer starts after db.prepare() with performance.now(), the raw timer includes transaction creation and uses millisecond Date.now(), which makes the 100- to 1,000-row points mostly noise.
- The charts that carry the '10x' claim are images only; readBench/writeBench loop over 100, 500, 1,000, 5,000, 10,000, 50,000 and 100,000 rows (populateLarge's 400,000 rows is a separate demo button), on a 2015 MacBook Pro in Chrome with no CPU model or browser version.
- Open bug #72: 'Failed to execute 'advance' on 'IDBCursor': The transaction has finished' is reported as frequent and random in Chrome, from the sequential-read cursor path; #74 reports VACUUM not working (closed without a linked fix).

## Known shortcomings

- Only text number is the README 'up to 10x' (chart images unreachable); the baseline in src/examples/bench/queries-raw-idb.js reads one record per IDB cursor step and does one put per row, and Nolan Lawson's post says batched getAll closes much of the gap (snippet only); no CPU model. Abandoned 2023-08-06.
- Harness flaw: main.worker.js populate() calls q.clear(db) without awaiting it, and raw IndexedDB clear() opens its own readwrite transaction, so every raw-IndexedDB write timing in writeBench also includes deleting the previous run's rows, while the SQLite clear runs synchronously before its timer. The read baseline walks openCursor one record per row; timers are asymmetric (SQLite performance.now after prepare, raw IDB Date.now including transaction creation). The 10x charts are images only (user-images.githubusercontent.com blocked here). Open bug #72 (IDBCursor advance after the transaction finished) and sql.js memory leak #53; abandoned since 2023-08-06.

## Caveats and trade-offs

First-party only; the headline 'up to 10x' is the only number in text, and the chart images (user-images.githubusercontent.com) could not be opened here, so per-test values were not read. Hardware is a 2015 MacBook Pro with no CPU model; Chrome version not stated. Baseline harness (src/examples/bench/queries-raw-idb.js) is the slowest raw-IndexedDB pattern: sumAll walks an openCursor one record per step and populate issues one store.put per row, while absurd-sql packs rows into 4096-byte SQLite blocks; Nolan Lawson's follow-up post 'Speeding up IndexedDB reads and writes' (2021-08-22) argued batched getAll()/getAllKeys() pagination and relaxed durability close much of that gap (search snippet only: in Chrome a 50,000-row cursor read took 1194.2 vs 488.3 with 1,000-item batches, units not shown). Timing is asymmetric: the SQLite sumAll timer starts after db.prepare, the raw-IDB timer includes opening the transaction. The harness's populateLarge inserts 400,000 rows. Requires the author's sql.js fork (@jlongster/sql.js), SharedArrayBuffer with COOP/COEP headers, and a worker; Hackaday's write-up (snippet only) says native SQLite is 2-3x faster than absurd-sql. This is a storage-layer win over the IndexedDB API, not a wasm compute win. Last commit 2023-08-06 (a merged @actualbudget patch); abandoned. [retier] First-party only; the headline 'up to 10x' is the only number in text and the chart images (user-images.githubusercontent.com) could not be opened, so per-test values were not read; readBench/writeBench loop over 100 to 100,000 rows on a 2015 MacBook Pro in Chrome with no CPU model or browser version. Harness flaw on writes: main.worker.js populate() calls q.clear(db) without awaiting it, and raw IndexedDB clear() opens its own readwrite transaction, so the timed populate transaction waits for that clear to commit and every raw-IndexedDB write timing includes deleting the previous run's rows, while the SQLite clear (DROP/CREATE TABLE) runs synchronously before its timer. Read baseline is the slowest raw-IndexedDB pattern: sumAll walks openCursor one continue() per row while absurd-sql reads about a hundred rows per 4 KB block; the SQLite timer starts after db.prepare() with performance.now(), the raw timer includes transaction creation and uses millisecond Date.now(), so the 100- to 1,000-row points are mostly noise. Nolan Lawson's follow-up 'Speeding up IndexedDB reads and writes' (2021-08-22) argued batched getAll()/getAllKeys() and relaxed durability close much of the gap. Requires the author's sql.js fork (@jlongster/sql.js, memory leak #53), SharedArrayBuffer with COOP/COEP headers and a worker; open bug #72 (IDBCursor advance after the transaction finished); a storage-layer win over the IndexedDB API, not a wasm compute win. Abandoned since 2023-08-06.

Needs SharedArrayBuffer (cross-origin isolation headers); Safari fallback allows only one writing tab at a time; relies on sql.js (SQLite WASM).

## Maintenance

Abandoned since 2023 (last commit 2023-08-06, 37 open issues) but MIT-licensed and small; usable for legacy sql.js projects, while new code should look at OPFS-backed SQLite WASM; a harness flaw was found (raw-IndexedDB write timings include clearing the previous run's rows through an unawaited clear transaction).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README states 'It consistently beats IndexedDB performance up to 10x' with read (SELECT SUM) and bulk-insert charts as images, measured on a 2015 MacBook Pro in Chrome; the benchmark code is public (src/examples/bench: queries.js, queries-raw-idb.js, main.worker.js) but CPU model, browser version and the charted values are not given in text, so not A, and no independent measurement was reachable, so not B.
- **Verifier notes:** README claim and benchmark code confirmed; record accurate at C. Shortcomings: baseline uses one-record IDB cursors and per-row puts instead of batched getAll (independent critique by Nolan Lawson, snippet only), chart values unreadable, no CPU model or browser version, abandoned since 2023.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-14 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/jlongster/absurd-sql>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/README.md>
  - <https://github.com/jlongster/absurd-sql/commits/master>
  - <https://github.com/jlongster/absurd-sql/tree/master/src/examples/bench>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/examples/bench/queries-raw-idb.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/examples/bench/queries.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/examples/bench/main.worker.js>
- **Sources the enricher read:**
  - <https://github.com/jlongster/absurd-sql>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/README.md>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/package.json>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/index.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/examples/bench/queries-raw-idb.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/examples/bench/queries.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/examples/bench/main.worker.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/examples/bench/main.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/sqlite-file.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/sqlite-fs.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/indexeddb/backend.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/indexeddb/file-ops.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/indexeddb/worker.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/indexeddb/file-ops-fallback.js>
  - <https://raw.githubusercontent.com/jlongster/absurd-sql/HEAD/src/sqlite-util.js>
  - <https://github.com/jlongster/absurd-sql/issues?q=is%3Aissue>
  - <https://github.com/jlongster/absurd-sql/issues/72>
  - <https://github.com/jlongster/absurd-sql/issues/53>
  - <https://github.com/jlongster/absurd-sql/issues/58>
  - <https://github.com/jlongster/absurd-sql/issues/34>
  - WebSearch: absurd-sql vs OPFS sqlite wasm benchmark IndexedDB VFS wa-sqlite (snippets from powersync.com and rxdb.info; no head-to-head numbers)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jlongster/absurd-sql`) · [data/wave13/enrich/raw/github_com_jlongster_absurd_sql.json](../../../data/wave13/enrich/raw/github_com_jlongster_absurd_sql.json) (enrichment confidence 0.65)

</details>
