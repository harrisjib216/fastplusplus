# DuckDB-Wasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++ (DuckDB) compiled to WebAssembly with Emscripten, TypeScript API` · `MIT` · 🟢 active

> DuckDB's columnar SQL engine compiled to WebAssembly. Analytical queries in the browser run several times to tens of times faster than Arquero or SQLite WASM.

| | |
|---|---|
| **Beats** | Arquero (JavaScript dataframe library) and SQLite WASM; danfo also in the table |
| **Claimed result** | Independent repo (timlrx/browser-data-processing-benchmarks README; times in seconds, Date.now() difference / 1000 in index.js), i7-1165G7 with Chrome 116: Test 1 top-level metrics Arquero 0.067 s vs DuckDB-Wasm 0.014 s (4.8x, derived from page data); Test 2 group by day 1.05 s vs 0.163 s (6.4x, derived from page data); Test 3 top 5 countries 4.847 s vs 0.114 s (42x, derived from page data); Test 4 10 random rows 0.517 s vs 0.032 s (16x, derived from page data). Against in-memory SQLite WASM without indexes DuckDB-Wasm also wins Tests 1-4 (e.g. Test 1 0.376 s vs 0.014 s, 27x, derived from page data). On the M2 MacBook Air with Firefox 117 the Arquero gaps are smaller (Test 3 0.852 s vs 0.132 s, 6.5x; Test 2 0.634 s vs 0.169 s, 3.8x; derived from page data). DuckDB-Wasm loses the load step (4.309 s vs Arquero 2.866 s and SQLite 0.893 s on Chrome), loses to indexed SQLite on Tests 2 and 4 (0.005 s and 0.002 s vs 0.163 s and 0.032 s), and loses every transactional test to in-memory SQLite WASM (1000 indexed selects 1.048 s vs 0.054 s, 1000 inserts 1.397 s vs 0.041 s, 1000 deletes 2.376 s vs 0.035 s). VLDB 2022 paper abstract (search snippet only): outperforms previous data processing libraries for the Web on TPC-H at multiple scale factors; no figures seen. |
| **Workload** | Third-party in-browser benchmark on 1,000,000 Bandcamp sales rows (24 columns): analytical SELECTs (overall metrics, group by day, top 5 countries per item and slug type, random rows) plus index, update, insert and delete tests, run on a separate browser thread. |
| **Metric** | latency |
| **Hardware** | 11th Gen Intel Core i7-1165G7 @2.80GHz Windows laptop with Chrome 116; Apple M2 MacBook Air with Firefox 117 |
| **Adoption** | 2.1k stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/duckdb/duckdb-wasm) · [benchmark](https://github.com/timlrx/browser-data-processing-benchmarks) |

## Verdict

One independent, single-run browser benchmark (1M-row, 24-column Bandcamp sales table; i7-1165G7 with Chrome 116 and M2 MacBook Air with Firefox 117; @duckdb/duckdb-wasm ^1.27.0, arquero ^5.2.0 and @sqlite.org/sqlite-wasm ^3.43.0, 2023) reports these results. DuckDB-Wasm ran the four analytical SELECTs 4.8-42x faster than Arquero on Chrome (3.8-6.5x for Tests 2-3 on Firefox) and faster than in-memory SQLite WASM. It loaded slower and lost every point-lookup and DML test. The SQLite SELECT times in that harness are time to first row. The VLDB 2022 TPC-H comparison was seen only as an abstract snippet, because vldb.org does not resolve here.

## Use it when

- Dashboards or notebooks running ad-hoc GROUP BY, window-function and aggregate SQL over roughly 10^5 to 10^7 rows in the browser. On a 1M-row table it ran these in 0.014-0.163 s, against 0.067-4.847 s for Arquero on Chrome.
- Data already in Parquet or Arrow, or remote Parquet you want to query with HTTP range reads instead of downloading and parsing in JS.
- Apps that want query work kept off the main thread: the browser API runs every query in a Web Worker.
- Teams that prefer SQL to a dataframe API and want the same dialect as native DuckDB (database files are readable by both).

## Skip it when

- Transactional workloads with many small queries. In the same benchmark, 1000 indexed point selects took 1.048 s against 0.054 s for in-memory SQLite WASM, and 1000 inserts 1.397 s against 0.041 s. That is about 1 ms per query (derived from page data), mostly async worker round-trips.
- Pages where startup dominates: loading the 1M-row Parquet took 4.309 s against 0.893 s for SQLite deserialising a database file and 2.866 s for Arquero. The Wasm bundle plus lazily fetched extensions (Parquet, JSON, ICU) are a large download.
- Data larger than the Wasm heap: builds cap memory at 4 GB, spilling to OPFS is an open request (#2061), and multithreading is experimental and off by default.
- Remote data behind servers without CORS or HTTPS: DuckDB-Wasm upgrades requests to HTTPS and needs cross-origin access, and its HTTP stack differs from native DuckDB's.

## How it is fast

DuckDB executes queries in vectorised, columnar pipelines, so aggregations, hash group-bys and window functions process batches of column values rather than one row at a time as SQLite's bytecode VM does. Parquet scans push down projections and filters and can fetch byte ranges over HTTP. Results cross into JavaScript as Arrow columnar buffers instead of per-row JS objects. Separate bundles target plain Wasm (mvp), Wasm exception handling (eh) and an experimental pthreads build (coi).

## Compared with alternatives

Pick DuckDB-Wasm over absurd-sql (SQLite persisted to IndexedDB) when the workload is read-mostly aggregation over large columnar data rather than durable row-level updates. Among the other wasm library entries (hash-wasm, libxml2-wasm and the like) it is the only general analytical query engine.

## Integration

| | |
|---|---|
| **Form** | module (npm @duckdb/duckdb-wasm: .wasm bundles plus worker scripts and TypeScript API) |
| **Dependencies** | apache-arrow (JS) for results; extensions fetched at runtime from extensions.duckdb.org; building from source needs Emscripten (version not documented in the README) |
| **Minimum toolchain** | Browser with WebAssembly (mvp bundle), Wasm exception handling for the eh bundle, cross-origin isolation (SharedArrayBuffer) for the experimental coi threads bundle; Node.js for the sync binding |
| **Platforms** | Chrome, Firefox, Safari and Node.js (README); any CPU the JS engine runs Wasm on |
| **Thread safety** | Browser API is asynchronous and serialises work inside one Web Worker; default build single-threaded; pthreads build experimental |
| **Drop-in for the baseline** | partial: replaces Arquero or SQLite WASM for read-mostly analytical SQL, but the API is async, returns Arrow, and differs from Arquero's verbs and SQLite's synchronous oo1 API |

## Gotchas

- Harness flaw in the independent benchmark (timlrx/browser-data-processing-benchmarks): SQLite runs each SELECT with db.exec({sql}) and no callback, resultRows or rowMode. In sqlite-wasm 3.43.0's oo1 API (ext/wasm/api/sqlite3-api-oo1.js), such a call steps each statement only once, so every SQLite SELECT time measures the first result row only. That makes the indexed-SQLite wins over DuckDB (Test 2 0.005 s and Test 4 0.002 s vs 0.163 s and 0.032 s) artefacts: an expression index on DATE(utc_date,'unixepoch') lets SQLite return its first group without finishing the GROUP BY. It also makes DuckDB's Test 4 win over unindexed SQLite conservative, since that scan stops at the first match. DuckDB's c.query() materialises the full Arrow result.
- Timings are one run per browser, taken with Date.now() around a Comlink call. DuckDB's AsyncDuckDB adds a second nested worker hop per query, which explains much of its per-query cost in the 1000-query tests. Browser variance is large: Arquero Test 3 takes 4.847 s on Chrome and 0.852 s on Firefox, and issue #2183 reports a DuckDB-Wasm query 6x slower on Chrome than on Firefox (20 s vs 3.4 s).
- Open issue #2258: once the Wasm heap passes 2 GiB, the EM_ASM blocks in lib/src/http_wasm.cc read signed pointers. HTTP request headers (Range, Authorization) are then dropped and POST/PUT bodies are silently zeroed. The report comes from a fork and is a code review of upstream; there is no maintainer response yet.
- The project's own TPC-H harness (packages/benchmarks) runs in Node with the synchronous binding. It skips Arquero Q9 and Q21 at SF &gt;= 0.1 and sql.js Q17, Q20 and Q22 at SF &gt;= 0.25, so 'beats on TPC-H' covers subsets of the 22 queries for those baselines.

## Known shortcomings

- timlrx/browser-data-processing-benchmarks numbers verified (seconds; 7-star repo, single run, 2023 package versions): slower load than Arquero and SQLite, loses every transactional and indexed-lookup test to SQLite WASM; VLDB figures unseen (snippet only); no native DuckDB comparison.
- Enricher: the timlrx harness calls SQLite db.exec({sql}) with no callback or resultRows, so sqlite-wasm 3.43.0 oo1 steps each SELECT once and all SQLite SELECT times are first-row only; the indexed-SQLite 'wins' (Test 2 0.005 s via a DATE(utc_date) index, Test 4 0.002 s) are artefacts and the DuckDB Test 4 win over unindexed SQLite is conservative; open #2258 (heap above 2 GiB drops HTTP headers and zeroes POST/PUT bodies), #2183 (Chrome 6x slower than Firefox); the repo TPC-H harness skips Arquero Q9/Q21 at SF&gt;=0.1 and sql.js Q17/Q20/Q22 at SF&gt;=0.25.

## Caveats and trade-offs

The VLDB PDF (vldb.org), duckdb.org and ir.cwi.nl were not reachable (DNS-blocked here); the paper claim comes from a search snippet, though the repo's packages/benchmarks/src holds TPC-H suites for DuckDB-Wasm, sql.js, Arquero and Lovefield that match the snippet's comparison set. The independent repo (7 stars, 23 commits) is a single run per browser on one machine, timed in seconds with Date.now() around a Comlink call to a web worker (so worker messaging and 1 ms clock resolution are included in the 0.002-0.03 s rows); its README says fetch and load timings are noisy. It pins old packages (@duckdb/duckdb-wasm ^1.27.0, @sqlite.org/sqlite-wasm ^3.43.0-build3, arquero ^5.2.0, 2023), and the workloads are not identical: the Arquero group-by-day test also sorts its output, which the DuckDB query does not. DuckDB-Wasm is slower to load than Arquero and SQLite and far slower than SQLite WASM on point lookups, updates, inserts and deletes; its wins are analytical scans and aggregations. No comparison against native DuckDB (the category's 'same library compiled natively' baseline) was found. Default build is single-threaded; multithreading is experimental.

Large WASM download; extensions such as Parquet, JSON and ICU are autoloaded lazily; HTTP stack differs from native DuckDB (CORS and HTTPS required); weaker than SQLite WASM on small transactional updates.

## Maintenance

Actively maintained by the DuckDB team (last commit 2026-09-29, 'Bump to 1.5.6'; 2.1k stars, MIT, no GitHub releases, published on npm). It is production-usable for browser analytics, with experimental multithreading and the open 2 GiB-heap HTTP bug.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed PVLDB 15 (2022) demo paper whose abstract (search snippet only) reports beating previous Web data libraries on TPC-H at several scale factors, with the paper's harness public in packages/benchmarks/src/suite_system_tpch_{duckdb,sqljs,arquero,lovefield}.ts; plus an independent repo (timlrx/browser-data-processing-benchmarks, public code, CPU and browser stated) whose Chrome table matches the claimed numbers. Not A: wasm build flags of the prebuilt npm bundles are not stated and the paper's CPU and results could not be opened.
- **Verifier notes:** Numbers verified against the timlrx README tables and harness (index.js, benchmarks/duckdb.js, benchmarks/arquero.js); unit is seconds. Metadata holds (MIT, 2.1k stars, last commit 2026-09-29). Shortcomings to record: slower load than Arquero and SQLite, loses all transactional and indexed point-lookup tests to SQLite WASM, independent repo is a 7-star single-run harness on 2023 package versions, VLDB paper figures unseen (snippet only), no native-DuckDB comparison.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-13 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/duckdb/duckdb-wasm>
  - <https://github.com/duckdb/duckdb-wasm/commits>
  - <https://github.com/duckdb/duckdb-wasm/tree/main/packages/benchmarks>
  - <https://github.com/duckdb/duckdb-wasm/tree/main/packages/benchmarks/src>
  - <https://raw.githubusercontent.com/duckdb/duckdb-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/duckdb/duckdb-wasm/HEAD/LICENSE>
  - <https://github.com/timlrx/browser-data-processing-benchmarks>
  - <https://github.com/timlrx/browser-data-processing-benchmarks/tree/main/workers>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/index.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/package.json>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/workers/duckdb-worker.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/benchmarks/duckdb.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/benchmarks/arquero.js>
- **Sources the enricher read:**
  - <https://github.com/duckdb/duckdb-wasm>
  - <https://github.com/duckdb/duckdb-wasm/commits/main>
  - <https://github.com/duckdb/duckdb-wasm/issues?q=is%3Aissue+performance+OR+slow+OR+memory>
  - <https://github.com/duckdb/duckdb-wasm/issues/2183>
  - <https://github.com/duckdb/duckdb-wasm/issues/2258>
  - <https://github.com/duckdb/duckdb-wasm/tree/main/packages/benchmarks/src>
  - <https://raw.githubusercontent.com/duckdb/duckdb-wasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/duckdb/duckdb-wasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/duckdb/duckdb-wasm/HEAD/packages/duckdb-wasm/README.md>
  - <https://raw.githubusercontent.com/duckdb/duckdb-wasm/HEAD/packages/benchmarks/package.json>
  - <https://raw.githubusercontent.com/duckdb/duckdb-wasm/HEAD/packages/benchmarks/src/suite_system_tpch_duckdb.ts>
  - <https://raw.githubusercontent.com/duckdb/duckdb-wasm/HEAD/packages/benchmarks/src/suite_system_tpch_sqljs.ts>
  - <https://raw.githubusercontent.com/duckdb/duckdb-wasm/HEAD/packages/benchmarks/src/suite_system_tpch_arquero.ts>
  - <https://github.com/timlrx/browser-data-processing-benchmarks/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/index.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/package.json>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/benchmarks/duckdb.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/benchmarks/arquero.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/benchmarks/sqlite.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/benchmarks/sqlite-indexed.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/benchmarks/danfo.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/workers/duckdb-worker.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/workers/arquero-worker.js>
  - <https://raw.githubusercontent.com/timlrx/browser-data-processing-benchmarks/HEAD/workers/sqlite-worker.js>
  - <https://raw.githubusercontent.com/sqlite/sqlite/version-3.43.0/ext/wasm/api/sqlite3-api-oo1.js>
  - <https://raw.githubusercontent.com/sqlite/sqlite/master/ext/wasm/api/sqlite3-api-oo1.c-pp.js>
  - https://www.vldb.org/pvldb/vol15/p3574-kohn.pdf (ENOTFOUND, not readable)
  - WebSearch: DuckDB-Wasm VLDB 2022 Kohn TPC-H sql.js Arquero Lovefield (snippets only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/duckdb/duckdb-wasm`) · [data/wave13/enrich/raw/github_com_duckdb_duckdb_wasm.json](../../../data/wave13/enrich/raw/github_com_duckdb_duckdb_wasm.json) (enrichment confidence 0.8)

</details>
