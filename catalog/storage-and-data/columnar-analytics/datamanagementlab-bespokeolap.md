# Bespoke OLAP

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> LLM agent that writes an in-memory C++ OLAP engine per fixed SQL workload; beats DuckDB and Umbra.

| | |
|---|---|
| **Beats** | DuckDB |
| **Claimed result** | Single-threaded, all systems pinned to the same core with data in memory: TPC-H SF20 total 4.4s vs DuckDB 49.2s (11.17x) and CEB SF2 0.4s vs 19.5s (45.33x). Vs Umbra: 7.24x (TPC-H) and 9.56x (CEB). Per-query vs DuckDB: 2.83x-102x on TPC-H and 11.6x-1500x on CEB. Multi-threaded, 1-64 threads: 7.65x vs DuckDB and 6.12x vs Umbra on TPC-H; 23.97x vs DuckDB and 1.87x vs Umbra on CEB. |
| **Workload** | TPC-H (SF20) and CEB, a templated JOB workload on IMDB (SF2, query 8a excluded). An autonomous LLM synthesis pipeline builds a separate workload-specific C++ engine for each benchmark (Bespoke-TPCH, Bespoke-CEB). Headline results compare it single-threaded, pinned to the same core and in memory, against DuckDB 1.4.1 and Umbra 26.02. A 1-64 thread scaling study adds multi-threaded results. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9654P 96-core processor, 768GB RAM (stated in paper) |
| **Compiler and flags** | g++ (default \$CXX, version unstated) with -std=c++20 -O3 -flto -fPIC -g for optimized builds (misc/fasttest/compiler.py, tools/fasttest/run.py) |
| **Adoption** | 50 stars (main repo); companion artifacts repo https://github.com/DataManagementLab/BespokeOLAP_Artifacts has 7 stars |
| **Last commit** | 2026-07-22 |
| **Links** | [repository](https://github.com/DataManagementLab/BespokeOLAP) · [benchmark](https://arxiv.org/abs/2603.02001) |

## Verdict

With every system single-threaded, pinned to the same core and holding data in memory (the DuckDB harness sets PRAGMA threads=1 and pins core 3), the paper reports TPC-H SF20 at 4.4s vs 49.2s for DuckDB 1.4.1 (11.17x) and CEB SF2 at 0.4s vs 19.5s (45.33x, with Q8a excluded), plus 7.24x and 9.56x over Umbra 26.02. These are on an AMD EPYC 9654P with 768 GB RAM, built with g++ -std=c++20 -O3 -flto (version unstated). With 1-64 threads the gaps shrink to 7.65x and 23.97x over DuckDB. The repo's harness scripts only the Bespoke and DuckDB runs, not Umbra.

## Use it when

- A stable set of parameterized query templates, such as a dashboard or reporting suite, that runs repeatedly over data you can reload from Parquet.
- The whole dataset fits in RAM. The engines are in-memory only; the paper's runs were TPC-H SF20-100 and CEB SF2-10 on a 768 GB box.
- You can pay for synthesis: the paper reports \$276 (TPC-H) and \$303 (CEB) in LLM API costs and 10-30 hours of wall-clock time per engine.
- Research, or as a reference: studying what workload-specific storage and per-query C++ look like. The Apache-2.0 generated TPC-H and CEB engines are published in BespokeOLAP_Artifacts.
- Linux x86-64 with GCC or Clang, Apache Arrow/Parquet C++ libraries and an LLM API key.

## Skip it when

- Ad-hoc or evolving SQL. Anything outside the query templates it was synthesized for needs a separate engine (DuckDB), and substantial workload drift means re-running the paid synthesis.
- Data larger than memory. The paper says its disk-based mode does not yet reach the in-memory speedups.
- Workloads with inserts or updates. Data enters only through a Parquet ingest step, and incremental updates are not documented.
- Production use. The repo is archived and deprecated. The maintainer calls it 'a research prototype published for inspirational purposes only' (issue #3), and that issue, an assertion failure in run_gen_base_impl.py when W&B logging is on, is still open.
- Workloads that need exact decimal results. Validation accepts answers within 1% of DuckDB's, and the multi-threaded TPC-H Q1 accumulates money sums in doubles.

## How it is fast

Most of the gain comes from a workload-specific physical layout. Examples: lineitem sorted by l_shipdate then l_orderkey, with zone maps that skip 64K-row blocks; dictionary codes; 16-bit date offsets; scaled-integer decimals; an 8-byte AoS pack of the four hottest aggregate columns; a precomputed discounted_price column; string arenas carrying per-row letter and bigram bitmasks for LIKE filters. In the paper's ablation (Table 1), optimized code over flat struct-of-arrays storage reaches only 5.18x (TPC-H) and 8.09x (CEB) over DuckDB. With bespoke storage it reaches 12.35x and 51.40x. The per-query code is fused and abstraction-free: inline aggregation (97% of queries), bitmap semi-joins (74%), O(1) hash-index joins, __restrict, branch hints, software prefetch and, in the multi-threaded artifacts, AVX-512 kernels. Join orders are picked by benchmarking candidates on sampled parameter values, not by a cost model.

## Compared with alternatives

Pick it over GenDB (also an LLM-generated engine; about 2.8x over DuckDB on 5 TPC-H SF10 queries) when you want all 22 TPC-H queries plus CEB with the generated source published, and over JetStream when you need code you can actually get. Stay with Umbra, DuckDB or Sirius (GPU) whenever queries are ad hoc: in the paper's multi-threaded runs on CEB, Bespoke's lead over Umbra shrinks to 1.87x.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Apache Arrow and Parquet C++ libraries (the generated engines). The generator needs Python &gt;=3.10 per pyproject (the README badge says 3.12+), uv, openai 2.11.0, openai-agents[litellm], duckdb&gt;=1.4.3 as the correctness reference, landlock, an LLM API key, and optionally W&B/weave. |
| **Minimum toolchain** | C++20. Builds use \$CXX (default g++) with -std=c++20 -O3 -flto; no minimum compiler version is documented. |
| **Platforms** | Linux x86-64 per the README. The multi-threaded TPC-H Q1 artifact calls an AVX-512 kernel ([[gnu::target("avx512f,...")]]) with no runtime CPU check, so it needs an AVX-512-capable CPU. |
| **Thread safety** | Not documented. The headline engines are single-threaded by construction. The multi-threaded variants share one ThreadPool whose size and core pinning come from the CORE_IDS environment variable. |
| **Drop-in for the baseline** | no |

## Gotchas

- Correctness means matching DuckDB on sampled parameter values at small scale factors, with atol=rtol=1e-2 on float columns (run_and_check_queries.py). Parameter values outside the tested samples are not validated.
- The benchmark times cover query execution only. Building the custom layout (sorts, dictionaries, zone maps, derived columns, hash indexes) is timed separately as 'Ingest ms' and is not reported in the paper. The agent's prompt (optim_constraints.txt) forbids indexes and query-specific precomputation, yet the paper reports hash indexes in 47% of queries, precomputed derived columns in 37%, and denormalized columns in Q5.
- The numbers depend on which synthesis run you look at. The April 2026 ADRS blog post (paper v1) reported 11.78x on TPC-H, 9.76x on CEB and about \$120. Paper v2 reports 11.17x, 45.33x and \$276/\$303, and its text still says synthesis costs 'a few dollars'.
- The published artifacts do not match the paper's description of the final Q1. The single-threaded bespoke_tpch Q1 is the 4-way unrolled scalar scan with branch hints that the paper attributes to earlier stages. The artifacts' run.py hardcodes /mnt/labstore/bespoke_olap as the Parquet path and runs only the single-threaded variants.

## Known shortcomings

- The 11.17x/45.33x are single-threaded; multi-threaded it is 7.65x/23.97x vs DuckDB. Engines are synthesized per workload, not a general-purpose library.
- The repo is archived and deprecated; its successor SynnoDB is PolyForm Noncommercial (not Apache-2.0). One engine per fixed workload, no SQL front end, in-memory only, Linux x86-64; the multi-threaded Q1 artifact uses AVX-512 without a CPU check. Correctness is checked only on sampled parameters and accepts results within 1% of DuckDB; ingest time is excluded.
- The agent prompt bans indexes/precomputation, yet the paper reports hash indexes in 47% of queries. Numbers shift between paper versions (v1 11.78x/9.76x/\~\$120; v2 11.17x/45.33x/\$276-303) while the text still says 'a few dollars'. The published single-threaded Q1 is the pre-final scalar version, not the paper's AVX-512 one; open assertion crash with W&B logging (#3).

## Caveats and trade-offs

The GitHub repo is archived (read-only) and was last pushed 2026-07-22, so it is tagged abandoned. The generated engines are workload-specific (one per benchmark, code in DataManagementLab/BespokeOLAP_Artifacts), not general-purpose. The headline 11.17x and 45.33x figures are single-threaded. DuckDB was not multi-threaded in them, contrary to the original record. CEB Q8a was excluded because of unstable DuckDB runtimes. The compiler version is unstated. The repo harness scripts only the bespoke and duckdb runners, so the Umbra comparison is not scripted. Per-query multipliers up to 1500x reflect workload-specific storage layouts.

Synthesizes one engine per fixed workload ('one-size-fits-one'); not usable as a drop-in general-purpose replacement for DuckDB; per-query speedup is highly variable (as low as 2.83x, as high as 1500x)

## Maintenance

The repo was archived and deprecated after its last push on 2026-07-22, and the README points to SynnoDB, which is PolyForm Noncommercial rather than Apache-2.0. The Apache-2.0 generator and generated engines can still be copied as a reference, but they are fixed to TPC-H and CEB and need the Arrow/Parquet toolchain plus LLM API access to regenerate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to A. The paper (arXiv 2603.02001 v2, §5.1) states an AMD EPYC 9654P with 768 GB RAM. The public harness benchmark/run.py with benchmark/systems/duckdb.py and bespoke.py runs against DuckDB. Optimized builds use g++ (the default \$CXX) with -std=c++20 -O3 -flto per misc/fasttest/compiler.py and tools/fasttest/run.py. Flags are stated, so the 50x cap does not apply.
- **Verifier notes:** The record mislabeled the 11.17x/45.33x figures as multi-threaded; they are single-threaded. The multi-threaded figures are lower (7.65x / 23.97x vs DuckDB), and claimed_speedup is fixed accordingly. The paper carries a PVLDB 19(11) header, but I did not confirm publication. Metadata checks out: Apache-2.0, 50 stars, archived, last commit 2026-07-22; the artifacts repo has 7 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2603.02001>
  - <https://arxiv.org/pdf/2603.02001>
  - <https://github.com/DataManagementLab/BespokeOLAP>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/benchmark/README.md>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/misc/Makefile>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/misc/fasttest/compiler.py>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/tools/fasttest/run.py>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/benchmark/systems/bespoke.py>
  - <https://github.com/DataManagementLab/BespokeOLAP_Artifacts>
- **Sources the enricher read:**
  - <https://github.com/DataManagementLab/BespokeOLAP>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/README.md>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/pyproject.toml>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/benchmark/README.md>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/benchmark/systems/bespoke.py>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/benchmark/systems/duckdb.py>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/misc/Makefile>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/misc/fasttest/compiler.py>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/misc/fasttest/db.cpp>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/misc/fasttest/query_api.hpp>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/misc/fasttest/builder_impl.hpp>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/misc/fasttest/loader_impl.hpp>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/misc/fasttest/cpu_affinity.hpp>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/tools/fasttest/run.py>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/tools/validate_tool/duckdb_connection_manager.py>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/tools/validate_tool/query_validator_class.py>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/tools/validate_tool/run_and_check_queries.py>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/conversations/prompts/optim_constraints.txt>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/conversations/prompts/optim_pinning.txt>
  - <https://github.com/DataManagementLab/BespokeOLAP/blob/main/conversations/prompts/expert_knowledge.txt>
  - <https://github.com/DataManagementLab/BespokeOLAP/issues/2>
  - <https://github.com/DataManagementLab/BespokeOLAP/issues/3>
  - <https://arxiv.org/abs/2603.02001>
  - <https://arxiv.org/pdf/2603.02001>
  - <https://github.com/DataManagementLab/BespokeOLAP_Artifacts>
  - <https://github.com/DataManagementLab/BespokeOLAP_Artifacts/blob/main/run.py>
  - <https://github.com/DataManagementLab/BespokeOLAP_Artifacts/blob/main/pyproject.toml>
  - <https://github.com/DataManagementLab/BespokeOLAP_Artifacts/blob/main/bespoke_tpch/storage_plan.txt>
  - <https://github.com/DataManagementLab/BespokeOLAP_Artifacts/blob/main/bespoke_tpch/builder_impl.hpp>
  - <https://github.com/DataManagementLab/BespokeOLAP_Artifacts/blob/main/bespoke_tpch/query_q1.cpp>
  - <https://github.com/DataManagementLab/BespokeOLAP_Artifacts/blob/main/bespoke_tpch_multithreading/query1.cpp>
  - <https://github.com/DataManagementLab/BespokeOLAP_Artifacts/blob/main/bespoke_tpch_multithreading/storage_plan.txt>
  - <https://github.com/SynnoDB/SynnoDB>
  - <https://hn.algolia.com/api/v1/search?query=Bespoke%20OLAP&tags=story>
  - <https://ucbskyadrs.github.io/blog/bespoke-olap/>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/datamanagementlab/bespokeolap`) · [data/wave6/enrich/raw/github_com_datamanagementlab_bespokeolap.json](../../../data/wave6/enrich/raw/github_com_datamanagementlab_bespokeolap.json) (enrichment confidence 0.8)

</details>
