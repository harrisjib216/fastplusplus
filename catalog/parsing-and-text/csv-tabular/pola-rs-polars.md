# Polars

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust DataFrame engine with lazy query optimization and SIMD execution; \~45x faster CSV writing than pandas.

| | |
|---|---|
| **Beats** | pandas (CSV write path; independent benchmarks separately report CSV read speedups) |
| **Claimed result** | \~45x faster than pandas, \~3.5x faster than pyarrow (CSV write); Polars 0.20.30 itself is \~40% faster than 0.20.19 (8.975s vs 14.684s) on the same task |
| **Workload** | Reading 15 Parquet files (\~800MB, NYC Yellow Tripdata) into memory and writing the result out to CSV, comparing Polars, pandas, and pyarrow |
| **Metric** | throughput |
| **Hardware** | MacBook Pro M3 (2023), 24GB RAM |
| **Adoption** | 39.9k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/pola-rs/polars) · [benchmark](https://pola.rs/posts/polars-in-aggregate-jun24/) |

## Verdict

An official Polars blog post benchmarked reading 15 Parquet files (\~800MB, NYC Yellow Tripdata) and writing the result to CSV on a MacBook Pro M3 (24GB RAM): Polars 0.20.30 is reported \~45x faster than pandas and \~3.5x faster than pyarrow on the CSV write step (ratios read from plots, no absolute pandas/pyarrow times or benchmark code given), and 0.20.30 itself is \~40% faster than 0.20.19 (8.975s vs 14.684s) due to PR #15576's per-datatype serializer.

## Use it when

- Reading/writing large Parquet or CSV files (hundreds of MB to multi-GB) where pandas' single-threaded loops bottleneck
- Datasets larger than RAM, using the streaming engine (`collect(engine='streaming')`)
- Multi-core machines where a query (joins, group-by, filters) can be parallelized across threads and columns
- Teams willing to adopt the expression/lazy API instead of pandas indexing semantics
- Multi-language pipelines (Python/Rust/Node/R) that want to share Arrow memory zero-copy

## Skip it when

- Codebases tightly coupled to pandas' `.loc`/`.iloc`/index-based API - migrating is real engineering work, not a swap
- Row counts above \~4.2 billion (2^32) - the default build uses 32-bit indexing and needs a bigidx build
- Pre-2011 CPUs or CPUs without AVX2 - the default release build targets modern instruction sets; use the `LTS_CPU=1` build instead
- x86-64 Python installs running under Rosetta on Apple Silicon need special install handling per the docs
- Treating the 45x/3.5x numbers as proof of CSV \*read\* speed - this benchmark measures a Parquet-read + CSV-write pipeline on a first-party blog post with no published benchmark code or build flags, and pandas/pyarrow figures come from plots, not stated absolute times

## How it is fast

The core engine is multi-threaded and vectorized (SIMD) over Arrow's columnar memory layout, with a lazy execution mode whose query optimizer applies predicate/projection pushdown so only needed data is read and computed. The specific CSV-writer speedup (0.20.19 to 0.20.30) came from PR #15576, which replaced generic per-value serialization with a dedicated serializer per datatype, cutting function-call overhead and type conversions during writing.

## Compared with alternatives

Most siblings in this category (xan, cisv, qsv, zsv, Sep, go-simdcsv, simd-csv, vroom, zsv-ruby) are single-purpose CSV parsers; DuckDB is the closest comparable full engine. Pick Polars when you need a full DataFrame/query engine (joins, group-by, lazy optimization, larger-than-RAM streaming) and are migrating off pandas, not just parsing CSV as fast as possible — for pure CSV-read throughput, a dedicated parser like zsv/qsv/DuckDB is the better-evidenced choice since this benchmark only covers Polars' CSV write path.

## Integration

| | |
|---|---|
| **Form** | crate (Rust workspace of polars-\* crates) + prebuilt Python wheel / Node package / R package |
| **Dependencies** | none required beyond the language runtime for prebuilt packages; internally vendors its own Arrow implementation (polars-arrow) rather than depending on the reference Arrow crate |
| **Minimum toolchain** | Rust edition 2024 (recent rustc, e.g. 1.85+) for building from source; Python &gt;=3.10 for py-polars |
| **Platforms** | x86-64 (AVX2 assumed by default release build; LTS_CPU=1 build for older CPUs), aarch64; optional NVIDIA GPU acceleration for query execution |
| **Thread safety** | not documented beyond 'multi-threaded execution' internally; README does not state whether DataFrame/LazyFrame objects are safe to mutate concurrently from application code |
| **Drop-in for the baseline** | partial — expression-based lazy/eager API differs from pandas; not a drop-in for pandas.read_csv/to_csv call sites, requires code changes |

## Gotchas

- Default release binaries assume AVX2; pre-2011 CPUs need the separate LTS_CPU=1 build
- Default build indexes rows with 32-bit integers, capping datasets at \~4.2 billion (2^32) rows without a bigidx build
- Apple Silicon users running an x86-64 Python build under Rosetta need special installation handling (per the install guide)
- The quoted 45x/3.5x figures come from a plot in a first-party blog post with no benchmark code or build flags published, and measure Parquet-read+CSV-write, not a pure CSV-read microbenchmark

## Caveats and trade-offs

First-party official blog post. The M3 hardware sentence opens the same CSV-writer benchmark section as the pandas/pyarrow relative-speedup plots, but the post does not say outright that the 45x figure comes from the same run. No benchmark code or build flags are given, and the pandas/pyarrow ratios come from plots, with no absolute times for those libraries. This is a CSV write benchmark (Parquet read + CSV write), not CSV read.

Expression-based API differs from pandas, requiring code migration; this specific post benchmarks the CSV write path via a parquet-to-CSV pipeline rather than a pure read_csv microbenchmark.

## Maintenance

Actively maintained — pushed to today, 39,859 stars, \~2,930 open issues on a large fast-moving repo; MIT-licensed and installable via `pip install polars` / `cargo add polars`, so vendoring is unnecessary.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Official Polars blog, 'CSV writer speed up' section: 'The latest Polars version is \~45x times faster than pandas and \~3.5x faster than pyarrow', plus 0.20.30 8.975s vs 0.20.19 14.684s on a MacBook Pro M3 24GB; no benchmark code or build flags, so first-party C.
- **Verifier notes:** All quoted numbers are verbatim on the page. MIT, 39,859 stars and a last commit of 2026-09-25 are confirmed. The record's mention of independent 2-16x CSV read benchmarks was not checked.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://pola.rs/posts/polars-in-aggregate-jun24/>
  - <https://github.com/pola-rs/polars>
- **Sources the enricher read:**
  - <https://github.com/pola-rs/polars>
  - https://github.com/pola-rs/polars (README)
  - <https://github.com/pola-rs/polars/blob/main/Cargo.toml>
  - <https://github.com/pola-rs/polars/blob/main/py-polars/pyproject.toml>
  - <https://pola.rs/posts/polars-in-aggregate-jun24/>
  - https://github.com/pola-rs/polars (issue search: performance regressions, thread-safety/panic/leak reports)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/pola-rs/polars`) · [data/wave3/enrich/raw/github_com_pola_rs_polars.json](../../../data/wave3/enrich/raw/github_com_pola_rs_polars.json) (enrichment confidence 0.45)

</details>
