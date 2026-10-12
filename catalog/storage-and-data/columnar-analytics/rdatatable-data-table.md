# data.table (R)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MPL-2.0` · 🟢 active

> R's in-memory data.frame replacement with C/OpenMP radix grouping and joins; \~3-4x faster than pandas on db-benchmark groupby.

| | |
|---|---|
| **Beats** | pandas |
| **Claimed result** | \~3.3x faster than pandas on groupby 'sum v1 by id1' over 100M rows/100 groups: data.table 1.16.99 0.456-0.524s vs pandas 2.2.3 1.525-1.528s in the same 2025-02-10 batch on c6id.metal. Across all 10 groupby questions in that batch, data.table is \~4.2x faster by geometric mean (29.7s vs 150.7s total) and wins 9/10 (derived from page data). The original H2O 2021 run gave data.table 1.14.1 0.863-0.97s vs pandas 1.2.5 2.841-3.021s (\~3.3x) in its last batch, 2021-06-30. |
| **Workload** | db-benchmark groupby question 'sum v1 by id1' on the 100M-row, 100-group synthetic table G1_1e8_1e2_0_0 (in-memory, two runs per question), plus the other 9 groupby questions on the same data. |
| **Metric** | throughput |
| **Hardware** | DuckDB Labs run: AWS c6id.metal, Intel Xeon Platinum 8375C @ 2.90GHz, 128 cores, 250GB (stated on the report page). Original H2O run: node mr-dl11, Intel Xeon E5-2630 v4 @ 2.20GHz, 40 cores, 125.78GB RAM (stated on the report page). The r3-8xlarge in the H2O README is only a setup guide, not the benchmark machine. |
| **Adoption** | 3.9k stars; long-standing R data-manipulation package |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/Rdatatable/data.table) · [benchmark](<https://duckdblabs.github.io/db-benchmark/ (current DuckDB Labs continuation, report generated 2026-08-17; raw timings in https://github.com/duckdblabs/db-benchmark/blob/main/time.csv); original 2021 H2O run: https://h2oai.github.io/db-benchmark/>) |

## Verdict

On db-benchmark (DuckDB Labs, batch 2025-02-10, AWS c6id.metal: Xeon Platinum 8375C, 128 cores, 250GB), data.table 1.16.99 dev with setDTthreads(0) against pandas 2.2.3 (pyarrow CSV reader, categorical ids) on 100M rows and 100 groups: 'sum v1 by id1' took 0.456-0.524s vs 1.525-1.528s (3.3x), and all 10 groupby questions were 4.2x faster by geometric mean (9/10 wins), recomputed from time.csv. No compiler or flags are published, and the 1B-row out-of-memory gap belongs to the original 125GB H2O node: on c6id.metal, pandas 2.2.2 finished 9-10 of 10 1B-row questions in 2024 (q1 \~17.2s vs data.table 5.1s in a later batch).

## Use it when

- You work in R and run grouped aggregations over roughly 10M to 1B+ in-memory rows. On db-benchmark it was 2.4-5.1x faster than pandas by geometric mean per dataset, and joins were 4.9-6.4x faster.
- Time-series or interval work that needs rolling (last observation carried forward, or nearest), non-equi or overlap-range joins, which pandas covers only partly (merge_asof).
- Memory-constrained pipelines where in-place column updates (:=, set\*) avoid the copies that data.frame or dplyr would make.
- Production R code that needs a stable dependency: it depends on base R only, supports back to R 3.5.0 (2018), and keeps a careful API lifecycle.
- Fast CSV ingest and export via fread/fwrite (memory-mapped, multithreaded), even if the rest of your stack is not data.table.

## Skip it when

- Your stack is Python. There is no drop-in path from pandas, and the fastest single-node engines are elsewhere. On the same c6id.metal machine type (different batches), DuckDB was \~9.8x and Polars \~2.3x faster than data.table by geometric mean over the 6 groupby questions they share on 100M rows.
- Tables over 2^31-1 rows. There is no long-vector support (issue #3957, open since 2019), and fread can build a larger table that then fails on print or subset (#7438).
- j expressions that GForce cannot rewrite, such as arbitrary R functions or combined expressions, especially with many groups. These run single-threaded R code per group (#5200). It is the one db-benchmark groupby question where pandas wins: max(v1)-min(v2) by id3, 5.72s vs 5.04s.
- Many tiny queries in a loop. The R-level dispatch overhead of [.data.table can dominate on small inputs (#5636, #5650 report single-column/single-row subsets far slower than base R). At 10M rows with 2 id1 groups, the lead over pandas shrinks to 1.65x geomean and q1 is roughly a tie.
- Larger-than-RAM data. It is purely in-memory with no out-of-core or streaming execution.

## How it is fast

Ordering and grouping use forder.c, a parallel MSD byte-wise radix sort built on Terdiman/Herf float twiddling; it skips unused byte buckets, packs compressed keys across byte boundaries and splits skewed groups in parallel (an earlier version became base R's radix sort). 'GForce' rewrites simple j expressions (sum, mean, min, max, median, var, sd, prod, first, last, head, tail, .N) into C kernels (gsumm.c) that scatter rows into per-thread batches keyed by the high and low 16-bit halves of the group id and aggregate them in parallel, with no R evaluation per group. Joins are multi-column binary searches over sorted keys (bmerge.c), and := writes columns in place with no copy.

## Compared with alternatives

Among catalogued pandas-beaters, pick data.table when you are in R and want an in-memory dataframe with ordered, rolling and non-equi joins and in-place updates, on CPU only. Pick chDB (embedded ClickHouse SQL) or cuDF.pandas (needs an NVIDIA GPU) to stay in Python, and DataFusion if you want an embeddable SQL engine; on db-benchmark DataFusion was \~6.9x faster than data.table on the shared groupby questions.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none beyond base R (Imports only the base packages methods, stats, utils); OpenMP optional at build time |
| **Minimum toolchain** | R &gt;= 3.5.0 plus a C compiler to build from source (CRAN ships binaries); OpenMP needed for multithreading, and Apple clang lacks the runtime (install libomp or use LLVM/GCC per the Installation wiki) |
| **Platforms** | any platform R/CRAN supports (Linux, macOS, Windows; x86-64 and arm64). Without OpenMP it runs single-threaded. |
| **Thread safety** | Internally multithreaded via OpenMP. Every parallel region uses num_threads(getDTthreads()), which defaults to 50% of logical CPUs (setDTthreads, R_DATATABLE_NUM_THREADS, OMP_THREAD_LIMIT honored). It switches to single-threaded inside forked children (mclapply, foreach) and by default restores afterwards. The R-level API is single-threaded like R itself. |
| **Drop-in for the baseline** | partial — it is an R package, not a Python library, so pandas code must be rewritten in R and DT[i, j, by] syntax. Only the concepts (group-by, merge, pivot) carry over. |

## Gotchas

- GForce only recognises its listed functions used standalone in j. In CRAN releases through 1.18.6.1, max(x) - min(x) is not optimised and falls back to per-group R evaluation. The unreleased 1.18.99 NEWS says arithmetic on GForce calls and type conversions such as sum(as.numeric(x)) now optimise.
- Default threads are 50% of logical CPUs. The benchmark called setDTthreads(0L), all 128 logical CPUs, so out-of-the-box runs on a big box use half the threads the published numbers used.
- := and set\* modify in place, so any other variable that shares the table sees the change (use copy()). data.table sorts strings in C locale, which can differ from base R's order().
- Correctness regression: grouped sum() on an integer64 column containing NA gave silently wrong results under GForce until the fix in 1.18.2.1 (Jan 2026, #7571). Use 1.18.2.1 or later.

## Known shortcomings

- R, not C++; evidence is the H2O/DuckDB Labs db-benchmark (last H2O run 2021-06; \~3.3x vs pandas 2.2.3 on the DuckDB Labs fork).
- At 1e7 rows with K=2 the lead drops to 1.65x; loses q7 (max-min not GForce-optimized in CRAN &lt;=1.18.6.1). Not the fastest: DuckDB is \~9.8x and Polars \~2.3x faster on shared questions. Max 2^31-1 rows (#3957); default uses 50% of CPUs while the benchmark used all 128; GForce int64 sum with NA gave silent wrong results until 1.18.2.1 (#7571). R only; numbers from dev builds.

## Caveats and trade-offs

The original h2oai/db-benchmark is abandoned: its last timing batch was 2021-06-30, not 2021-01-20, and its master branch was last committed 2021-06-09. The duckdblabs/db-benchmark fork is active (commit 2026-09-23) and shows the margin holding against pandas 2.x (\~3.3x on this question, \~4.2x geomean across the groupby questions). data.table timings there come from dev builds (1.16.99/1.17.99). pandas has not been re-run since early 2025, and data.table is not the fastest entrant: DuckDB and Polars beat it. data.table loses to pandas on 'max v1 - min v2 by id3' (5.72s vs 5.04s). No compiler or flags are published.

R, not C++/Python-native (though internals are C); pandas also failed to complete the 1e9-row (1B row) groupby tasks in this suite at all (out of memory) while data.table, polars, and pydatatable completed them, a bigger practical gap than the raw timing ratio suggests at the largest scale.

## Maintenance

Actively maintained (CRAN 1.18.6.1 published 2026-08-24, master commit 2026-09-10, NumFOCUS-sponsored), MPL-2.0; install from CRAN, though the benchmark numbers come from unreleased dev builds and pandas has not been re-run since Feb 2025.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** db-benchmark is a well-known independent third-party suite, first run by H2O and now maintained by DuckDB Labs. It runs data.table and pandas on the same data with public scripts (datatable/groupby-datatable.R, pandas/groupby-pandas.py), and the report states the CPU model. It is not A: no compiler or flags are stated for the data.table build or the pandas wheel.
- **Verifier notes:** The record's pandas 1.2.4 numbers (2.726/2.882s) are real but come from the 2021-04-29 batch, and its data.table range mixes several May 2021 batches. Hardware was wrong (r3-8xlarge vs the stated Xeon E5-2630 v4 node). I repointed the entry to the maintained DuckDB Labs fork, which confirms \~3.3x against pandas 2.2.3 and refutes the 'likely narrower' caveat. last_commit was pushed_at, and I fixed it to the default-branch commit date.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://h2oai.github.io/db-benchmark/>
  - <https://h2oai.github.io/db-benchmark/time.csv>
  - <https://github.com/h2oai/db-benchmark>
  - <https://raw.githubusercontent.com/h2oai/db-benchmark/master/README.md>
  - <https://github.com/duckdblabs/db-benchmark>
  - <https://raw.githubusercontent.com/duckdblabs/db-benchmark/main/README.md>
  - <https://raw.githubusercontent.com/duckdblabs/db-benchmark/main/time.csv>
  - <https://duckdblabs.github.io/db-benchmark/>
  - <https://github.com/Rdatatable/data.table>
- **Sources the enricher read:**
  - <https://github.com/Rdatatable/data.table>
  - <https://github.com/Rdatatable/data.table/blob/master/README.md>
  - <https://github.com/Rdatatable/data.table/blob/master/DESCRIPTION>
  - <https://github.com/Rdatatable/data.table/blob/master/src/forder.c>
  - <https://github.com/Rdatatable/data.table/blob/master/src/gsumm.c>
  - <https://github.com/Rdatatable/data.table/blob/master/src/openmp-utils.c>
  - <https://github.com/Rdatatable/data.table/blob/master/src/bmerge.c>
  - <https://github.com/Rdatatable/data.table/blob/master/src/fread.c>
  - <https://github.com/Rdatatable/data.table/blob/master/man/datatable-optimize.Rd>
  - <https://github.com/Rdatatable/data.table/blob/master/man/openmp-utils.Rd>
  - <https://github.com/Rdatatable/data.table/blob/master/NEWS.md>
  - <https://github.com/Rdatatable/data.table/tags>
  - <https://github.com/Rdatatable/data.table/issues/3957>
  - <https://github.com/Rdatatable/data.table/issues/5200>
  - <https://github.com/Rdatatable/data.table/issues/5650>
  - <https://github.com/Rdatatable/data.table/issues/7438>
  - <https://github.com/Rdatatable/data.table/issues?q=label%3Aperformance+is%3Aopen>
  - <https://github.com/Rdatatable/data.table/wiki/Installation>
  - <https://cran.r-project.org/web/packages/data.table/index.html>
  - <https://duckdblabs.github.io/db-benchmark/>
  - <https://raw.githubusercontent.com/duckdblabs/db-benchmark/main/time.csv>
  - <https://raw.githubusercontent.com/duckdblabs/db-benchmark/main/logs.csv>
  - <https://github.com/duckdblabs/db-benchmark/blob/main/datatable/groupby-datatable.R>
  - <https://github.com/duckdblabs/db-benchmark/blob/main/pandas/groupby-pandas.py>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/rdatatable/data.table`) · [data/wave6/enrich/raw/github_com_rdatatable_data_table.json](../../../data/wave6/enrich/raw/github_com_rdatatable_data_table.json) (enrichment confidence 0.8)

</details>
