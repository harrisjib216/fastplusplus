# JetStream

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · ⚪ unknown

> MIT research prototype: LLM agents generate query-specific accelerators that plug into DuckDB or PostgreSQL; claims 833x geomean over single-threaded DuckDB.

| | |
|---|---|
| **Beats** | DuckDB |
| **Claimed result** | Stateful accelerators: 833x geomean read-only speedup over single-threaded DuckDB on TPC-H SF=20 (the Figure 6 legend says 843x) and 3544x over PostgreSQL (the legend says 3554x). The paper compares this with 34.07x for multi-threaded GenDB and 12.35x for single-threaded Bespoke OLAP. Stateless accelerators reach only 1.99x over single-threaded DuckDB. Under TPC-H RF1/RF2 refreshes the geomean is 733x at 300 s, 629x at 120 s and 375x at 60 s. On the unseen SEC-EDGAR workload (SF=3) it is 102x over DuckDB and 486x over PostgreSQL. |
| **Workload** | TPC-H at SF=20 with periodic refreshes, plus a leakage-resistant SEC-EDGAR (SF=3) workload; an agentic pipeline generates query-specific accelerators (optionally with persistent auxiliary state) that extend an existing DBMS |
| **Metric** | latency |
| **Hardware** | Dual-socket server with 2x Intel Xeon Gold 6230 (40 physical cores, 80 hardware threads), 376 GiB memory and a 1 TB NVMe SSD. Query experiments are single-threaded unless noted. |
| **Links** | [benchmark](https://arxiv.org/abs/2608.22476) |

## Verdict

On TPC-H SF=20 (all 22 queries, warm reads, state already built), stateful accelerators were 833x faster by geomean than single-threaded DuckDB and 3544x faster than PostgreSQL 18.4, on a 2x Xeon Gold 6230 server with 376 GiB RAM. Stateless accelerators were 1.99x faster, and with RF1/RF2 refreshes every 60, 120 or 300 s the geomean including maintenance was 375x, 629x or 733x. On SEC-EDGAR SF=3 it was 102x over DuckDB and 486x over PostgreSQL. No compiler, flags, DuckDB version or code are given.

## Use it when

- A fixed set of parameterized analytical templates (reports, dashboards) runs repeatedly on DuckDB or PostgreSQL, and each query reduces to a small aggregate over parameters you can key state on.
- The workload is read-heavy and writes arrive in batches. With TPC-H RF1/RF2 refreshes (about 0.1% of the database each) every 60 s, the workload geomean including maintenance was still 375x over DuckDB.
- You want the existing DBMS to remain the single copy of the data, with ad-hoc SQL and transactions intact. GenDB and Bespoke OLAP instead rewrite storage or keep a second copy.
- You are researching LLM-synthesized database specialization. The workflow is reusable: an external orchestrator owns the differential tests and A/B benchmarks so the coding agent cannot game them.
- You have memory to spare. Stateful accelerators used 28.1 GB at TPC-H SF=20, against 10.3 GB for stateless.

## Skip it when

- Anything production-bound. No code, license or release is public, so the only option is to reimplement the design from a v1 arXiv preprint with no venue.
- Ad-hoc or exploratory SQL. Only the pre-declared templates are accelerated; every other query runs at plain DuckDB or PostgreSQL speed.
- Memory-constrained hosts. At SF=20, stateful JetStream needs 28.1 GB, against 18.1 GB for GenDB, 16.12 GB for Bespoke OLAP and 10.3 GB for stateless JetStream.
- Write-heavy workloads. The TPC-H geomean falls from 733x to 375x as refreshes go from every 300 s to every 60 s. On SEC-EDGAR with point writes every 0.5 s it is only 8.8x over DuckDB and 4.0x over PostgreSQL.
- You only need faster execution without precomputation. Stateless accelerators give 1.99x, and that is against single-threaded DuckDB; multi-threaded DuckDB was not used as a baseline.

## How it is fast

Almost all of the speedup comes from persistent, query-specific auxiliary state. This is generated sufficient statistics keyed on the query's parameters: per-month revenue for TPC-H Q14; per brand/container 2-D range trees over part size x quantity for Q19, so each predicate branch becomes one range-sum probe; a q-gram inverted index plus a baseline histogram with sparse corrections for Q13; dense-ID bitmaps for distinct counts in SEC-EDGAR Q1. A read then touches a few state partitions instead of scanning, joining and aggregating the base tables. Without that state, the generated kernels over native scans reach only 1.99x. Writes go through generated maintenance code, similar to incremental view maintenance. At pre-commit a per-accelerator cost model picks one of four actions (apply delta, rebuild the affected partitions, full rebuild, or invalidate and repair lazily), and the result is published optimistically under per-partition versions.

## Compared with alternatives

Sirius also speeds up DuckDB workloads, but as a GPU engine with public code that is about 5.5x faster at SF100 on general queries. Umbra and Velox are general-purpose engines. Pick JetStream's approach only for a fixed set of parameterized templates on DuckDB or PostgreSQL, where you will trade memory and a from-paper reimplementation for precomputed state; otherwise use one of the siblings.

## Integration

| | |
|---|---|
| **Form** | not applicable: no artifact is released. Per the paper, generated accelerators compile into a shared library loaded as a DuckDB table function or a PostgreSQL extension function. |
| **Dependencies** | Not documented, since there is no code. The paper names these requirements: a host DBMS (DuckDB, version not stated, or PostgreSQL 18.4); a DuckDB patched with extra transaction hooks for stateful maintenance; and, for synthesis, GPT-5.6 Terra Pro through the OpenAI Agents SDK plus DeepSeek V4 Pro through the Codex exec harness. |
| **Minimum toolchain** | not documented; the paper names no implementation language, compiler or flags |
| **Platforms** | Not documented. The only evaluation platform is x86-64 (2x Xeon Gold 6230). |
| **Thread safety** | The paper describes a transactional protocol. Mutations are buffered transaction-locally and are invisible to other transactions. Maintenance is chosen at pre-commit, and each partition image is published optimistically only if its source version is still current. A conflict invalidates that partition, and reads fall back to base-table execution. Accelerators can be generated single- or multi-threaded, but the evaluation is single-threaded. Other concurrent-access guarantees are not documented. |
| **Drop-in for the baseline** | partial: accelerators run inside DuckDB or PostgreSQL over their native tables, but the paper shows accelerated queries invoked through generated functions (SELECT \* FROM accel_qN_aux(...)) rather than the original SQL; automatic routing of unchanged SQL is not described, and stateful mode on DuckDB needs a patched DuckDB |

## Gotchas

- The Figure 6 numbers are warm reads with valid state and exclude the one-time state build. After an invalidation or a publish conflict, the affected queries run on the base-table fallback path until the state is repaired.
- Correctness is checked empirically, not proven. It rests on differential tests against the host DBMS and an audit agent with extra hidden tests. Each query gets unique LLM-written code (plus maintenance logic) that someone has to review and own.
- The geomean hides a wide spread. Section 3.4 reports about 8.6x best-valid for Q13 and about 2638x for Q19. The SEC-EDGAR figure plots only six selected queries (Q1-Q4, Q6, Q24) out of a 1000-query SQLSmith set.
- The text and the Figure 6 legend disagree (833x vs 843x, and 3544x vs 3554x for PostgreSQL). The DuckDB baseline is single-threaded with no version given, while GenDB is plotted multi-threaded. Changing a template means re-running synthesis, which cost \$41.63 for all 22 stateful TPC-H accelerators.

## Known shortcomings

- Paper only: no code, compiler or flags. The baseline is single-threaded DuckDB; the figure legend says 843x while the text says 833x (also 3544x vs PostgreSQL).
- The 833x needs persistent per-query state (range trees, q-gram index, bitmaps); stateless it is only 1.99x, and memory rises to 28.1 GB vs 10.3 GB. Writes erode the gain (733x to 375x as the refresh interval drops from 300 s to 60 s; point writes 8.8x). Needs patched DuckDB transaction hooks and queries go through an accel_qN_aux() table function, so it is not a drop-in; the SEC figure plots only 6 selected queries.

## Caveats and trade-offs

The 833x/375x/102x/486x figures are geomeans over workload-specific accelerators that LLMs generated (GPT-5.6 Terra Pro for analysis, DeepSeek V4 Pro for implementation). The accelerators precompute persistent, query-specific auxiliary state such as per-date aggregates, multidimensional summaries and range trees, so many queries become sub-millisecond lookups. JetStream is not a general-purpose engine replacement, and it costs more memory than stateless execution or the GenDB/Bespoke OLAP baselines. The DuckDB baseline is single-threaded by default. The text and the Figure 6 legend disagree (833x vs 843x, and 3544x vs 3554x for PostgreSQL). Ratios exceed the 50x plausibility threshold and no compiler or flags are given, so the tier is capped at C. This is an arXiv preprint (MIT CSAIL authors including Tim Kraska) with no venue stated. No code or artifact link appears on the arXiv abstract page, in the HTML or in the PDF, and none was found by GitHub search.

Headline number depends on precomputed, query-specific auxiliary state (materialized statistics/range trees), not general query acceleration; drops to a much more modest 1.99x with no persistent state allowed; no public code repository found

## Maintenance

Reference only: an MIT CSAIL arXiv preprint (v1, 23 Aug 2026) with no code, license or release; a co-author's publication page links only the paper and BibTeX, so maintenance status is unknown.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The arXiv preprint (v1, 23 Aug 2026, no venue) compares directly against DuckDB and PostgreSQL 18.4. It states the CPU (2x Xeon Gold 6230) but gives no compiler or flags and links no code, so these are first-party numbers short of A and not peer-reviewed. The ratios above 50x with unstated flags also cap it at C.
- **Verifier notes:** The abstract, section 3.1 setup and section 3.2 text all check out against the record. The PDF does not name the implementation language; accelerators compile into a shared library loaded as a DuckDB table function or a PostgreSQL extension, so the record's 'C++' is plausible but unconfirmed. has_code=false, license=null and maintenance_status=unknown stay as they are, since there is no repo.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2608.22476>
  - <https://arxiv.org/pdf/2608.22476>
  - <https://arxiv.org/html/2608.22476>
  - <https://hn.algolia.com/api/v1/search?query=JetStream%20query%20accelerators&tags=story>
  - <https://api.crossref.org/works?query.bibliographic=JetStream+Generating+Query+Accelerators+for+Existing+Database+Systems&rows=3>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2608.22476>
  - <https://arxiv.org/pdf/2608.22476>
  - <https://arxiv.org/html/2608.22476>
  - <https://hn.algolia.com/api/v1/search?query=JetStream%20Generating%20Query%20Accelerators>
  - <https://github.com/search?q=JetStream+query+accelerators&type=repositories>
  - <https://github.com/search?q=jetstream+duckdb+accelerator&type=repositories>
  - <https://api.github.com/users/geoffxy/repos>
  - <https://github.com/geoffxy/geoffxy.github.io/blob/HEAD/index.html>
  - <https://github.com/geoffxy/duckdb>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:jetstream`) · [data/wave6/enrich/raw/paper_jetstream.json](../../../data/wave6/enrich/raw/paper_jetstream.json) (enrichment confidence 0.7)

</details>
