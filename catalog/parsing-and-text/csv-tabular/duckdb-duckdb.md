# DuckDB (CSV reader)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> In-process OLAP SQL engine that queries CSV files directly, beating pandas read_csv + groupby on large files.

| | |
|---|---|
| **Beats** | pandas read_csv |
| **Claimed result** | 47x faster (3.8s vs 180s); 90% less memory (380MB vs 4.2GB) |
| **Workload** | Aggregating a \~50M-row / 8GB CSV access-log file (date parsing, group-by status code, percentile calc) via DuckDB SQL directly on the CSV vs pandas read_csv + groupby |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X, 64GB DDR5 RAM, NVMe SSD |
| **Adoption** | 41.7k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/duckdb/duckdb) · [benchmark](https://duckdblab.org/en/post/duckdb-large-file-processing/) |

## Verdict

A third-party, DuckDB-unaffiliated blog (duckdblab.org) reports that on one Ryzen 9 7950X / 64GB DDR5 / NVMe machine, DuckDB SQL run directly over a synthetic \~8GB/50M-row Nginx access-log CSV (date parsing, group-by status code, percentile calc) took \~3.8s and \~380MB RAM, versus a naive `pd.read_csv` + groupby at \~180s and \~4.2GB RAM — about 47x faster and 90% less memory. DuckDB was 'v1.5.x plus some v2.0 Preview features'; pandas version, compiler flags, and a benchmark script were not published.

## Use it when

- Query, filter, join, or aggregate CSV data larger than comfortably fits in a pandas DataFrame (tens of millions of rows / multi-GB files) without hand-writing chunked pandas code
- The workload is naturally SQL-shaped: group-bys, window functions, percentiles, or joins across multiple CSV/Parquet files
- You want to query CSV/Parquet (including gzip-compressed CSV) in place without a separate ETL/load step
- Single-machine job where you want multi-core throughput on the read+aggregate path without standing up Spark/Dask
- You already use pandas/Polars downstream and just want DuckDB as an accelerator for ingest+aggregate, then hand results back as a DataFrame

## Skip it when

- Pure scanning/row-counting/field-extraction with no aggregation — sibling tools like zsv and xan are reported to beat DuckDB's own CSV reader on those tasks
- Team is committed to pandas' imperative, method-chaining style and can't adopt SQL or a relational API
- CSV has very long lines/fields beyond the default 2MB max_line_size, or wildly inconsistent schemas across many files, without tuning the sniffer (max_line_size, sample_size, files_to_sniff)
- You need guaranteed constant memory regardless of input method: memory behavior currently differs between reading by filename (streams) and reading CSV via a pipe/stdin with the same query (open GH issue #25165 as of Sept 2026)
- Columns contain long numeric IDs — the sniffer has been reported to infer these as DOUBLE instead of HUGEINT/VARCHAR, silently losing precision unless types are pinned explicitly

## How it is fast

It uses a vectorized, columnar execution engine (operates on batches of values rather than row-by-row Python objects) combined with a multi-threaded CSV scanner that reads and parses chunks of the file in parallel (`parallel=true` by default). A CSV "sniffer" auto-detects delimiter, quoting, header, and column types from a sample of the file before the full parallel scan, and query operators (filter/group-by/projection) push down into the scan instead of materializing the whole table first, which is what keeps memory low relative to a full `pd.read_csv` load.

## Compared with alternatives

Pick DuckDB when the job is more than parsing — joins, group-bys, window functions, or percentiles across one or more CSV/Parquet files in a single SQL statement. For pure scanning, row-counting, or field extraction, siblings like zsv and xan are reported faster than DuckDB's own CSV reader and are lighter-weight if a full SQL engine isn't needed.

## Integration

| | |
|---|---|
| **Form** | shared lib / static lib / source-drop (single-file amalgamation) / language packages (pip, npm, etc.) |
| **Dependencies** | none required to build the core (vendors what it needs); optional extensions may pull their own deps |
| **Minimum toolchain** | C++17-compliant compiler, CMake, Python 3 (build-time only, per README) |
| **Platforms** | x86-64 and aarch64 on Linux/macOS/Windows, plus WebAssembly (DuckDB-Wasm) via language clients |
| **Thread safety** | not documented at the API level in what I read; the CSV reader and query engine are internally multi-threaded (parallel=true by default) for a single query |
| **Drop-in for the baseline** | partial — explain: replaces `pd.read_csv().groupby()` with SQL over the file, not a pandas-compatible call, but results can be materialized back into a DataFrame via `.df()`, so it's a drop-in for the data path, not the pandas API |

## Gotchas

- CSV type sniffer reported to infer long numeric ID columns as DOUBLE instead of HUGEINT/VARCHAR, causing precision loss unless column types are pinned explicitly (GH #22750, closed)
- Memory profile isn't uniform across input methods: reading a named CSV file streams in near-constant memory, but reading CSV from a pipe/stdin with the same query has been reported to retain the full projected columns in memory (GH #25165, open)
- Default max_line_size is 2,000,000 bytes and the sniffer samples a bounded prefix by default — very long lines or unusual multi-file schemas may need manual max_line_size/sample_size/files_to_sniff tuning
- The parallel CSV reader has had past correctness bugs combining ignore_errors=true with specific internal vector-size builds (GH #7755, closed) — the multi-threaded CSV path is intricate enough that staying on a current release matters

## Caveats and trade-offs

Published on duckdblab.org, which calls itself an 'Independent DuckDB Technical Blog' not affiliated with DuckDB Labs, not on duckdb.org or a well-known benchmark suite. No linked benchmark script; the workload is introduced as 'Assume we have a real Nginx access log access_log.csv'; versions loosely specified ('DuckDB v1.5.x' plus some v2.0 Preview features); author says 'results may vary by machine'. The pandas baseline is a naive full pd.read_csv load with no chunking or dtype tuning, and a \~4.2GB pandas footprint for an 8GB CSV looks low, so treat the numbers cautiously.

Requires SQL/relational query style instead of pandas' imperative API; adds an embedded OLAP engine dependency.

## Maintenance

Actively developed (repo pushed within the last day of this review, current dev branch v2.0-cyanoptera, 41.7k stars, MIT-licensed) with prebuilt packages for most languages and platforms — no maintenance risk; 'copyable' here just means querying a CSV via DuckDB is a few lines of SQL, not that DuckDB's own source is meant to be vendored.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Third-party blog (duckdblab.org, which calls itself an independent blog, not DuckDB Labs) shows pd.read_csv + groupby vs DuckDB SQL over access_log.csv: \~3.8s vs \~180s (47x), \~380MB vs \~4.2GB, on Ryzen 9 7950X; no benchmark script and not a well-known suite, so C.
- **Verifier notes:** Numbers and hardware match the page. I replaced the caveat that called 47x 'above the 50x threshold' (it is below). The source is weak (an unaffiliated blog with a hypothetical framing), so a stronger first-party or independent DuckDB-vs-pandas CSV source would be better if enrichment finds one.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://duckdblab.org/en/post/duckdb-large-file-processing/>
  - <https://github.com/duckdb/duckdb>
- **Sources the enricher read:**
  - <https://github.com/duckdb/duckdb>
  - <https://github.com/duckdb/duckdb/blob/main/README.md>
  - <https://duckdblab.org/en/post/duckdb-large-file-processing/>
  - <https://duckdb.org/docs/current/data/csv/overview.html>
  - https://github.com/duckdb/duckdb/issues (search: CSV out of memory / wrong result)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/duckdb/duckdb`) · [data/wave3/enrich/raw/github_com_duckdb_duckdb.json](../../../data/wave3/enrich/raw/github_com_duckdb_duckdb.json) (enrichment confidence 0.4)

</details>
