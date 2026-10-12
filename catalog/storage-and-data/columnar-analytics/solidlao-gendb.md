# GenDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> LLM-agent pipeline that writes a custom C++ executable per SQL query; 2.8x faster than DuckDB on 5 TPC-H queries.

| | |
|---|---|
| **Beats** | DuckDB |
| **Claimed result** | TPC-H SF10 (Q1, Q3, Q6, Q9, Q18): GenDB 214 ms total vs DuckDB 594 ms and Umbra 590 ms (2.8x), and 11.2x vs ClickHouse. Q9 runs in 38 ms, 6.1x faster than DuckDB. SEC-EDGAR (6 queries): 328 ms, 5.0x vs DuckDB and 3.9x vs Umbra. The 163x figure (TPC-H Q18, 12,147 ms to 74 ms) and the 13.3x / 12.7x figures (SEC-EDGAR Q4 / Q6) are GenDB's own gains between optimization iterations, not speedups over a baseline. |
| **Workload** | TPC-H SF10 representative subset (Q1, Q3, Q6, Q9, Q18) and SEC-EDGAR: 5 GB of 2022-2024 SEC financial-statement data, with 6 queries sampled from 1,000 SQLSmith-generated ones. LLM agents (Claude Sonnet 4.6 in the paper) generate per-query C++ executables. Baselines are DuckDB v1.4.4, Umbra (February 2026), MonetDB v11.55.1, ClickHouse v26.2.1 and PostgreSQL v18.2, measured on hot, in-memory runs. |
| **Metric** | latency |
| **Hardware** | 2x Intel Xeon Gold 5218 (2.3 GHz, 32 physical cores total), 384 GB RAM, Ubuntu (stated in paper) |
| **Compiler and flags** | g++ -O3 -march=native -std=c++17 -fopenmp (src/gendb/orchestrator.mjs; compiler version unstated) |
| **Adoption** | 75 stars |
| **Last commit** | 2026-06-08 |
| **Links** | [repository](https://github.com/SolidLao/GenDB) · [benchmark](https://arxiv.org/abs/2603.02081) |

## Verdict

On the paper's setup (2x Xeon Gold 5218, 64 threads, 384 GB RAM, hot in-memory runs, mean of 3 runs after a warm-up), Sonnet 4.6-generated C++ built with g++ -O3 -march=native -fopenmp ran 5 TPC-H SF10 queries in 214 ms. That compares with 594 ms for DuckDB v1.4.4 and 590 ms for Umbra (2.8x). Per query versus DuckDB: Q1 40 vs 84 ms, Q3 55 vs 83, Q6 14 vs 19, Q9 38 vs 231, Q18 68 vs 177. On SEC-EDGAR (6 queries) it took 328 ms, versus 1,549 ms for DuckDB and 1,280 ms for Umbra. The later template-native version (VLDB 2026 demo paper) reports smaller gains: 249 ms, 2.4x versus DuckDB and 2.7x versus Umbra on TPC-H, and 403 ms, 3.8x versus DuckDB on SEC-EDGAR.

## Use it when

- A fixed set of recurring, templated OLAP queries (scheduled reports, dashboards) where a one-off generation run pays for itself. The demo paper puts it at about \$14 and 91 minutes for 5 TPC-H queries, and \$23 and 140 minutes for 6 SEC-EDGAR queries, with Sonnet 4.6.
- Read-mostly analytical data that fits in RAM on a many-core Linux x86-64 server, where hot latency in the tens of milliseconds at the \~10 GB scale matters.
- A hybrid setup, which the authors themselves recommend: DuckDB or Umbra keep serving ad-hoc SQL while the hottest query templates are routed to GenDB binaries.
- A readable starting point for hand-tuning a critical query. The generated C++ is plain, self-contained code, and the repo's language comparison got a further 1.30x on TPC-H with a human-directed refinement pass.
- Research on LLM-synthesized query processing: the full pipeline is open, and ablation, model-comparison and iteration-history data are checked in.

## Skip it when

- Ad-hoc or exploratory SQL. Every new query shape needs an LLM generation run (minutes to hours, and paid API use), and nothing at runtime can answer a query that was not generated in advance.
- Data that changes or grows. Storage is a custom format produced by a generated ingest program, and the binaries hard-code SF10 key ranges and thread counts. Inserts, updates and transactions are not documented.
- Workloads that need guaranteed correct answers. Validation only matches results against DuckDB ground truth, plus fuzzing across template parameters in the newer version, and the authors say this does not prove semantic equivalence. The paper documents LLM bugs: dropped DECIMAL scale divisions that gave wrong results, and open-addressing tables with no resize or probe bound that looped forever.
- Non-Linux, non-x86 or mixed hardware fleets. The pipeline reads /proc/cpuinfo, lscpu and lsblk, the binaries are built with -march=native, and every published number comes from one 2x Xeon Gold 5218 server.
- Anything production-critical. Results vary a lot between generation runs: a later Sonnet 4.6 run got 285 ms on TPC-H (paper: 214 ms) and 830 ms on SEC-EDGAR (paper: 328 ms). The README warns that Sonnet 4.6 agents now hang, and baselines were compared on only 5 TPC-H queries and 6 SEC-EDGAR queries.

## How it is fast

Five agents (workload analyzer, storage/index designer, query planner, code generator, query optimizer) write code specialized to the exact data statistics and machine. The generated code narrows columns to fit the data (for example, lineitem price stored as int32 cents and discount and quantity as uint8). It picks aggregation by cache fit: a direct per-thread array for Q1's 6 groups, and for Q3's roughly 4M groups a shared open-addressing table with keys and values in separate arrays, updated with lock-free CAS. It also uses zone-map pruning with branchless scans, and query-specific derived structures built at ingest, such as Q9's nibble-packed orderkey-to-year file. Everything runs over mmap'd columns with OpenMP and is compiled with g++ -O3 -march=native. A profiling feedback loop then rewrites slow queries; Q18 went from 12,147 ms to 74 ms when a cache-thrashing hash aggregation was replaced with an index-aware sequential scan.

## Compared with alternatives

Pick GenDB over Bespoke OLAP (also LLM-synthesized per workload, headline numbers single-threaded) and JetStream (generates accelerators that sit beside an existing DBMS) when you want standalone, multi-threaded C++ executables per query template from an Apache-2.0 pipeline that can use either Claude or Codex agents. Pick Umbra, Sirius or plain DuckDB whenever you need a real SQL engine that handles arbitrary queries without a generation step.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Generator: Node.js 18+ with npm packages @anthropic-ai/claude-agent-sdk, @anthropic-ai/claude-code, @openai/codex-sdk and openai; an Anthropic or OpenAI API key or subscription; Python 3 for result comparison and benchmarks; DuckDB for ground truth. Generated binaries: g++ with OpenMP, pthreads and POSIX mmap only. |
| **Minimum toolchain** | C++17 (g++ -O3 -march=native -std=c++17 -fopenmp); the GCC version is not documented; Node.js 18+ |
| **Platforms** | Linux x86-64 in practice (tested only on 2x Xeon Gold 5218 with AVX-512 and 64 threads). The hardware probe recognizes NEON, but aarch64 is not documented or tested. |
| **Thread safety** | Not applicable in the usual sense. Each query is a separate process that uses all cores through OpenMP (one run hard-codes N_THREADS = 64), and the orchestrator runs one query at a time while timing. Running several concurrently is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- The query times are not measured the same way for GenDB and the baselines. GenDB's number is the binary's own [TIMING] total minus its output phase. DuckDB, Umbra and the others are timed from the Python client and include fetchall(). Work done at ingest time (indexes, derived files like Q9's orderkey-to-year nibble file) is not counted at all.
- Generated code is sized for the data it was generated against. Examples: Q9 declares part_bitset[2000001] and suppkey_nk[100001] with N_THREADS = 64, and the latest Q3 uses BITMAP_MAX = 1500001, all SF10 key ranges. A larger dataset or a different machine needs regeneration; the orchestrator re-benchmarks on a hardware-fingerprint change.
- Bug in the shared helper src/gendb/utils/hash_utils.h: when CompactHashMap::operator[] displaces an entry (Robin Hood), it overwrites `key` with the displaced key before its final lookup. It then returns the displaced key's value slot, so `m[k] += v` can update the wrong group. The generated files checked use find() plus insert(), which avoids this path.
- The checked-in runs cannot execute from a fresh clone. The storage folders (12 GB for TPC-H, 3.3 GB for SEC-EDGAR) must be downloaded from Google Drive. The stable paper version is on branch arxiv-03-02-2026, and main has since moved to template-native generation.

## Known shortcomings

- The 163x is GenDB's own iteration gain on Q18 (12,147 to 74 ms), not vs DuckDB; on SEC-EDGAR it is 5.0x. Engines are LLM-synthesized per query set, not a general-purpose library.
- Not an engine: an LLM writes a C++ binary per query, so ad-hoc SQL is impossible; generation costs \$14-62 and 1.5-4 h per 5-6 queries. Timing is unequal (GenDB uses an in-binary timer minus output; baselines use a Python client including fetchall) and ingest-time derived files are not counted. Large run-to-run swings (a rerun gave 285 vs 214 ms on TPC-H, 830 vs 328 on SEC-EDGAR); the template-native demo paper shows only 2.4x vs DuckDB.
- SF10 sizes and 64 threads hard-coded, -march=native, Linux only. hash_utils.h CompactHashMap::operator[] returns the wrong slot after a Robin Hood swap; correctness is checked only by matching DuckDB. Last code 2026-03-27; package.json says ISC while LICENSE says Apache.

## Caveats and trade-offs

This is the authors' own paper (an arXiv preprint) and repo. The code is LLM-generated per query, so results depend on a particular generation run. Only 5 of the 22 TPC-H queries are used, at SF10. The compiler version is unstated. Baselines use their automatically created indexes, and a second variant adds GenDB-generated indexes. The largest multipliers in the paper (163x, 12-13x) are iteration-over-iteration self-improvements, not comparisons with a baseline.

Generates a bespoke C++ execution program per query/workload/hardware via an LLM agent rather than being one general-purpose engine; synthesis has its own latency/cost the headline numbers don't include; early research prototype (paper: Lao & Trummer, 2026, arXiv:2603.02081)

## Maintenance

A Cornell research prototype (arXiv 2603.02081 plus a VLDB 2026 demo paper), licensed Apache-2.0 although package.json still says ISC, with 75 stars. The last code change was 2026-03-27 and the 2026-06-08 commit only touched the README, so 'active' is generous. You can run the generator if you have LLM API access and a Linux server; the reusable output is generated C++ per query, not a library to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to A. The paper (arXiv 2603.02081, §4.1) states 2x Intel Xeon Gold 5218 CPUs with 384 GB RAM. The public harness benchmarks/benchmark.py and benchmarks/lib/runners.py (duckdb_benchmark, plus Umbra, ClickHouse, MonetDB and PostgreSQL runners) runs against DuckDB. Generated code is compiled with g++ -O3 -march=native -std=c++17 -fopenmp (src/gendb/orchestrator.mjs).
- **Verifier notes:** The record garbled the 163x figure. It is Q18 improving from 12,147 ms to 74 ms across GenDB's own iterations, not '594 ms to 74 ms' and not a speedup vs DuckDB. The headline 2.8x vs DuckDB/Umbra is correct, and the README repeats it. Metadata checks out: Apache-2.0, 75 stars, not archived, last commit 2026-06-08 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2603.02081>
  - <https://arxiv.org/pdf/2603.02081>
  - <https://github.com/SolidLao/GenDB>
  - <https://github.com/SolidLao/GenDB/blob/main/README.md>
  - <https://github.com/SolidLao/GenDB/blob/main/benchmarks/benchmark.py>
  - <https://github.com/SolidLao/GenDB/blob/main/benchmarks/lib/runners.py>
  - <https://github.com/SolidLao/GenDB/blob/main/benchmarks/lib/systems.py>
  - <https://github.com/SolidLao/GenDB/blob/main/src/gendb/orchestrator.mjs>
  - <https://github.com/SolidLao/GenDB/blob/main/output/tpc-h-sf10-3.19/ingest/Makefile>
- **Sources the enricher read:**
  - <https://github.com/SolidLao/GenDB>
  - <https://github.com/SolidLao/GenDB/blob/main/README.md>
  - <https://github.com/SolidLao/GenDB/blob/main/package.json>
  - <https://github.com/SolidLao/GenDB/blob/main/docs/ablation.md>
  - <https://github.com/SolidLao/GenDB/blob/main/docs/model-comparison.md>
  - <https://github.com/SolidLao/GenDB/blob/main/docs/language-comparison.md>
  - <https://github.com/SolidLao/GenDB/blob/main/src/gendb/gendb.config.mjs>
  - <https://github.com/SolidLao/GenDB/blob/main/src/gendb/orchestrator.mjs>
  - <https://github.com/SolidLao/GenDB/blob/main/src/gendb/utils/hardware.mjs>
  - <https://github.com/SolidLao/GenDB/blob/main/src/gendb/utils/mmap_utils.h>
  - <https://github.com/SolidLao/GenDB/blob/main/src/gendb/utils/hash_utils.h>
  - <https://github.com/SolidLao/GenDB/blob/main/src/gendb/utils/timing_utils.h>
  - <https://github.com/SolidLao/GenDB/blob/main/src/gendb/agents/code-generator/prompt.md>
  - <https://github.com/SolidLao/GenDB/blob/main/benchmarks/lib/runners.py>
  - <https://github.com/SolidLao/GenDB/blob/main/benchmarks/lib/gendb.py>
  - <https://github.com/SolidLao/GenDB/blob/main/benchmarks/lib/config.py>
  - <https://github.com/SolidLao/GenDB/blob/main/benchmarks/tpc-h/results/sf10/metrics/benchmark_results.json>
  - <https://github.com/SolidLao/GenDB/blob/main/output/deprecated/tpc-h/2026-02-26T06-27-28/generated/queries/q9.cpp>
  - <https://github.com/SolidLao/GenDB/blob/main/output/deprecated/tpc-h/2026-03-07T21-21-01/queries/Q9/iter_4/q9.cpp>
  - <https://github.com/SolidLao/GenDB/blob/main/output/deprecated/sec-edgar/2026-03-08T22-08-07/generated/queries/q24.cpp>
  - <https://github.com/SolidLao/GenDB/blob/main/output/tpc-h-sf10-3.19/queries/Q3/v1/q3.cpp>
  - https://github.com/SolidLao/GenDB/tree/main/output/tpc-h-sf10-3.19/queries (Q1-Q22 v1/meta.json)
  - <https://github.com/SolidLao/GenDB/issues/2>
  - <https://github.com/SolidLao/GenDB/issues/3>
  - <https://github.com/SolidLao/GenDB/commits/main>
  - <https://arxiv.org/pdf/2603.02081>
  - <https://export.arxiv.org/api/query?id_list=2603.02081>
  - <https://arxiv.org/abs/2607.20630>
  - <https://arxiv.org/pdf/2607.20630>
  - <https://hn.algolia.com/api/v1/search?query=GenDB&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/solidlao/gendb`) · [data/wave6/enrich/raw/github_com_solidlao_gendb.json](../../../data/wave6/enrich/raw/github_com_solidlao_gendb.json) (enrichment confidence 0.8)

</details>
