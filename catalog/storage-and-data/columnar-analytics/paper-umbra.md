# Umbra

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `proprietary` · 🟢 active

> Closed-source TU Munich research SQL database (HyPer successor) that runs ClickBench about 2.4x faster than ClickHouse on one node.

| | |
|---|---|
| **Beats** | ClickHouse |
| **Claimed result** | Sum of hot-run times (min of runs 2-3, identical to best-of-3 here) over all 43 ClickBench queries: Umbra (2026-09-18, image 26.09) 7.41s vs ClickHouse (2026-09-26 run) 18.03s (\~2.4x) and vs DuckDB (2026-05-11 run) 26.25s (\~3.5x). Umbra is faster than ClickHouse on 40 of 43 queries. Cold-run sums are 47.27s vs 114.19s (ClickHouse) and 115.19s (DuckDB). 0 failed queries (derived from page data). |
| **Workload** | ClickBench: 43 analytical SQL queries over the \~100M-row 'hits' web-analytics table, single-node AWS c6a.4xlarge |
| **Metric** | throughput |
| **Hardware** | AWS EC2 c6a.4xlarge, single node |
| **Adoption** | consistently one of the top single-node finishers on ClickBench; commercial spin-off is CedarDB |
| **Links** | [benchmark](<https://github.com/ClickHouse/ClickBench/blob/main/umbra/results/20260918/c6a.4xlarge.json (baselines in the same repo: clickhouse/results/20260926/c6a.4xlarge.json and duckdb/results/20260511/c6a.4xlarge.json)>) |

## Verdict

ClickBench's GitHub Actions automation ran the vendor's umbradb/umbra:26.09 image (submitted in PR #2066 by Umbra team member Tobias Schmidt) on one AWS c6a.4xlarge over the 100M-row hits table, untuned. Summing each query's best hot run over 43 queries gives 7.41s for Umbra, 18.03s for ClickHouse (2026-09-26, about 2.4x) and 26.25s for DuckDB (2026-05-11); cold sums are 47.3s vs 114.2s. ClickHouse wins only Q2 hot (1 ms vs 4 ms), and compiler and flags are unknown because only the binary is tested.

## Use it when

- Single-node ad-hoc analytical SQL over a wide table of about 100M rows (filtered counts, GROUP BY, COUNT(DISTINCT), LIKE '%x%' scans, top-N) when hot-query latency matters: on ClickBench it beats ClickHouse on 40 of 43 queries, often by 2-18x.
- Machines with plenty of RAM: on c6a.metal it completes all 43 queries with a 3.8s hot sum and no concurrent-test errors.
- Loading Parquet into a compressed table: ClickBench ingests the 14 GB hits.parquet through the umbra.parquetview table function in 163s and stores it in 8.3 GB with zstd (ClickHouse: 182s, 9.4 GB).
- Join-heavy analytical SQL: the CIDR 2020 paper reports geometric-mean speedups of 3.0x over HyPer and 4.6x over MonetDB on the Join Order Benchmark (2.3x over MonetDB on TPC-H SF10).
- Research or benchmarking where you want a state-of-the-art compiled engine as a reference point behind a PostgreSQL endpoint and running a Docker container is fine.

## Skip it when

- Production use: the license in the Docker image says the software is 'intended strictly for internal evaluation and review purposes and not for production purposes'. The commercial product from the same group is CedarDB.
- Small-memory machines: in the 2026-09-18 ClickBench run, 14 of 43 queries failed on c6a.large with 'ERROR: unable to allocate memory' (mostly COUNT(DISTINCT) and big GROUP BYs), and 17 failed on t3a.small. ClickHouse finished all 43 on c6a.large. Earlier 16 GB runs also failed during data load.
- Many concurrent clients on mid-size boxes: in ClickBench's 10-connection, 600-second test, 54.7% of attempted queries errored on c6a.4xlarge (58.8% on c8g.4xlarge; ClickHouse 0.1%). The log does not say why.
- Anything that needs source code, patches, audits, embedding in-process or a distributed or replicated cluster: it is a proprietary, binary-only, single-node server.
- ClickHouse-specific workloads: it speaks PostgreSQL SQL and wire protocol, not ClickHouse SQL, HTTP or native protocol, and has no MergeTree-style engines.

## How it is fast

Umbra compiles each query into code organised around the data flow. It uses its own lightweight intermediate representation (IR), generates machine code directly so execution starts almost immediately (the 'Flying Start' backend, with 'FireARM' for AArch64), and hands only long-running pipeline steps to the LLVM optimizing compiler (adaptive compilation). Work is spread across cores with morsel-driven parallelism. Storage sits on a buffer manager derived from LeanStore with variable-size pages (64 KiB minimum, power-of-two size classes), pointer swizzling and optimistic versioned latches, and the CIDR 2020 paper measures its overhead at under 6% on average versus flat memory-mapped tables. Strings use 16-byte headers that store strings of 12 bytes or fewer inline and keep a 4-byte prefix for longer ones.

## Compared with alternatives

Pick Umbra for the fastest single-node SQL engine behind a PostgreSQL endpoint when an evaluation-only, closed-source license is acceptable. Pick chDB (in-process ClickHouse for Python) or Bodo (compiled Python DataFrames) when you need open source, production use, or execution inside a Python process.

## Integration

| | |
|---|---|
| **Form** | Prebuilt Linux Docker image (umbradb/umbra) running a PostgreSQL-wire server plus the umbra-sql CLI; no library or source |
| **Dependencies** | Docker; any PostgreSQL client (psql, libpq, JDBC, etc.) |
| **Minimum toolchain** | not applicable (prebuilt binary); host kernel and Docker version requirements not documented |
| **Platforms** | linux/amd64 and linux/arm64 images (arm64 since the 26.01 tag, January 2026; earlier tags amd64 only); ClickBench ran it on AMD c6a/c7a and Graviton c8g |
| **Thread safety** | Multi-client server with ACID transactions via MVCC (per umbra-db.com); ClickBench's concurrent test shows high error rates under memory pressure |
| **Drop-in for the baseline** | partial: it can replace ClickHouse only as a single-node analytical SQL endpoint. Clients, SQL dialect and schemas (ClickHouse table engines and ORDER BY keys) have to be ported to PostgreSQL equivalents. |

## Gotchas

- In May 2026 the ClickBench maintainer found that Umbra silently returns a NULL row for unimplemented functions (e.g. regexp_substr), with no error, so a query can look like a microsecond-fast success. The note was removed in the 26.09 update, and whether it was fixed is not documented.
- When memory ran out during bulk load, the load transaction errored partway through but the harness carried on, leaving a partial table that gave implausibly fast timings. Check row counts after loading.
- The ClickBench maintainer found memory settings hardcoded in the binary (shared_buffers 128MB, work_mem 4MB): 'SET work_mem' is rejected and ALTER SYSTEM is 'not implemented yet'. The only runtime knob in ClickBench's scripts is the ASYNCIO=0 environment variable.
- It needs raised container limits: Docker Hub's quick-start sets nofile=1048576 and memlock=8 GiB, and ClickBench runs it --privileged with unlimited memlock.

## Known shortcomings

- Closed-source binary (Docker 26.09), proprietary licence, no flags; ClickBench sums check out (7.41 vs ClickHouse 18.03 vs DuckDB 26.25 s; faster on 40/43 queries) but a concurrent-test error ratio of 0.547 is reported (verifier downgrade from A).
- Evaluation-only licence ('not for production purposes'), closed-source binary. Fails on small machines (c6a.large 14/43 and t3a.small 17/43 queries fail with allocation errors, where ClickHouse runs all 43). ClickBench concurrency test (10 connections, 600 s): 54.7% of queries error on c6a.4xlarge and 58.8% on c8g.4xlarge, with no logged cause. The ClickBench maintainer found silent NULL rows for unimplemented functions, hard-coded memory settings, and a failed bulk load that left a partial table with fake-fast timings. Not a ClickHouse drop-in (Postgres wire protocol and dialect); arm64 images only since 26.01.

## Caveats and trade-offs

No public source code. ClickBench's CI runs the closed-source binary from the vendor's prebuilt Docker image (umbradb/umbra:26.09), so compiler/flags are not stated. ClickHouse is re-run daily and its hot sum varies (18.00-18.81s over 2026-09-24..26). The ClickBench README warns that direct comparison across systems is tricky and says to take results with a grain of salt. In the supplementary concurrent-QPS test, Umbra's result records concurrent_error_ratio 0.547 (vs 0.001 for ClickHouse).

Closed-source (research prototype from TU Munich, now commercialized); distributed only as a prebuilt Docker image (umbradb/umbra); PostgreSQL wire-compatible

## Maintenance

Actively released, with roughly monthly Docker tags from 25.01 to 26.09 (pushed 2026-09-16). It is a research project whose license allows only internal evaluation, so use it as a reference point and look at CedarDB for a supported product.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** ClickBench, a well-known third-party suite run by ClickHouse Inc. (Umbra's competitor), measures Umbra against ClickHouse on the same c6a.4xlarge with the public harness (ClickHouse/ClickBench umbra/, clickhouse/, lib/benchmark-common.sh) via its CI. Umbra is closed-source and runs from a prebuilt Docker image (umbradb/umbra:26.09), so compiler/flags are unknown and it cannot be A.
- **Verifier notes:** All three sums re-derive exactly from the raw JSONs (Umbra 7.41 from 20260918, ClickHouse 18.03 from 20260926, DuckDB 26.25 from 20260511). The baseline numbers are in sibling result files, not in the Umbra JSON itself, so I extended benchmark_url. ClickBench flags the entry proprietary: yes, so license is set to 'proprietary'. has_code=false and usability=reference are correct.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/results/20260918/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/umbra/results/20260918/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/umbra/results/20260914/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260926/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260925/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/clickhouse/results/20260924/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c6a.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/umbra/install>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/umbra/start>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/umbra/benchmark.sh>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/README.md>
- **Sources the enricher read:**
  - <https://umbra-db.com/>
  - <https://www.cidrdb.org/cidr2020/papers/p29-neumann-cidr20.pdf>
  - <https://hub.docker.com/v2/repositories/umbradb/umbra/>
  - <https://hub.docker.com/v2/repositories/umbradb/umbra/tags?page_size=15>
  - <https://github.com/umbra-db>
  - <https://github.com/ClickHouse/ClickBench/tree/main/umbra>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/install>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/start>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/load>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/query>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/create.sql>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/queries.sql>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/template.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/results/20260918/c6a.4xlarge.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/results/20260918/c6a.large.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/results/20260918/t3a.small.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/results/20260918/c6a.metal.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/results/20260918/c8g.4xlarge.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/results/20260918/c8g.metal-48xl.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/umbra/results/20260918/c7a.metal-48xl.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/clickhouse/results/20260926/c6a.4xlarge.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/clickhouse/results/20260926/c6a.large.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/duckdb/results/20260511/c6a.4xlarge.json>
  - <https://github.com/ClickHouse/ClickBench/blob/main/README.md>
  - <https://github.com/ClickHouse/ClickBench/blob/main/lib/benchmark-common.sh>
  - <https://github.com/ClickHouse/ClickBench/pull/2066>
  - <https://github.com/ClickHouse/ClickBench/pull/161>
  - <https://github.com/ClickHouse/ClickBench/commit/02f9c9e1b1>
  - <https://github.com/ClickHouse/ClickBench/commit/1d1c476814>
  - <https://github.com/ClickHouse/ClickBench/commit/7377cac442>
  - <https://github.com/ClickHouse/ClickBench/commit/bc7555d77a>
  - <https://github.com/ClickHouse/ClickBench/commit/9e8fff2ead>
  - <https://github.com/ClickHouse/ClickBench/commit/7e23f9d42f>
  - <https://pastila.nl/?00065a7d/b5eba4044b11063a0e38f107e94cbb5a>
  - <https://pastila.nl/?00065a7d/98803ea983b2f75eb94b3be0fd30a333>
  - <https://hn.algolia.com/api/v1/search?query=umbra%20database&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=umbra%20clickbench&tags=comment>
  - <https://news.ycombinator.com/item?id=22153515>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:umbra`) · [data/wave6/enrich/raw/paper_umbra.json](../../../data/wave6/enrich/raw/paper_umbra.json) (enrichment confidence 0.75)

</details>
