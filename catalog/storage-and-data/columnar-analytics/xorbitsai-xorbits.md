# Xorbits

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Python` · `Apache-2.0` · 🟡 stale

> Distributed pandas/NumPy-API engine built on Mars. On 100 GB-1 TB TPC-H it beats Dask DataFrame, Modin and pandas-on-Spark.

| | |
|---|---|
| **Beats** | Dask (DaskDF) |
| **Claimed result** | Docs comparisons page: on TPC-H SF100, '\~8 times faster than DaskDF and \~4 times quicker than Modin', with Koalas 'comparable' in speed but hitting task failures; at SF1000 Xorbits ran all queries while DaskDF, Koalas and Modin 'stumbled on most'. ICDE 2024 paper: 2.66x average speedup over the fastest baseline on operations all baselines support; 29x faster than Dask and 37x faster than Modin on TPCx-AI UC10 SF100 (data skew); 2.65x faster than Modin (the fastest baseline) on the census pipeline; 3.86x faster than PySpark on plasticc; pandas was slowest on the single-node pipelines (figure only, no ratio given). |
| **Workload** | TPC-H queries at SF100 (\~100GB) and SF1000 (\~1TB) scale, run as a distributed pandas-API-compatible dataframe workload against DaskDF, Modin, and Koalas. |
| **Metric** | throughput |
| **Hardware** | Paper: AWS r6i family; supervisor on r6i.large, workers on up to 16 r6i.8xlarge (32 vCPU, 256 GB each). CPU model not named. The docs comparisons page gives no hardware. |
| **Adoption** | 1.2k stars |
| **Last commit** | 2025-04-21 |
| **Links** | [repository](https://github.com/xorbitsai/xorbits) · [benchmark](https://arxiv.org/abs/2401.00865) |

## Verdict

The ICDE 2024 paper is by the Xorbits authors. Setup: AWS r6i workers, each r6i.8xlarge with 32 vCPU and 256 GB, CPU model unnamed; 4 workers for TPC-H SF100 (36 GB Parquet) and 16 for SF1000 (358 GB). Versions were Xorbits 0.6.3, Dask 2023.9, Modin 0.24.1 on Ray, pandas-on-Spark 3.5.0 and pandas 2.1.1, all with default configs, averaged over 7 runs with the max and min dropped. Xorbits averaged 2.66x over the fastest baseline on operations every system supports and was 29x/37x faster than Dask/Modin on skewed TPCx-AI UC10. TPC-H relative times count only the queries each baseline finished. The docs' '\~8x DaskDF, \~4x Modin at SF100' figure gives no hardware.

## Use it when

- Existing pandas code on 100 GB-1 TB Parquet/CSV that no longer fits one node, when you want to keep the pandas API rather than rewrite into Spark SQL or Dask idioms.
- Merges between a huge fact table and a tiny dimension table (skewed keys). There Dask and Modin stall on one core; the paper measured 29x and 37x on TPCx-AI UC10 (34 GB joined to 3.2 MB).
- Single-node multi-core speedup on 20 GB-class CSV feature-engineering pipelines. The paper reports 2.65x over Modin on census and 3.86x over PySpark on plasticc, with single-threaded pandas slowest.
- Mixed dataframe and distributed-array work (QR, linear regression) where you would otherwise pair Dask DataFrame with Dask Array. The paper reports 5.88x and 1.74x average throughput over Dask Array.
- Teams already running Kubernetes, SLURM or a plain supervisor/worker cluster (the xorbits-supervisor and xorbits-worker CLIs) that want a pandas-shaped front end.

## Skip it when

- Data that fits comfortably in one machine's RAM when raw speed is the goal. The paper compares only against pandas-API frameworks, never DuckDB, Polars or SQL engines, and it calls pandas-API TPC-H 'fundamentally unfair' against SQL systems.
- Small or interactive workloads. Startup is slow (the docs say to call xorbits.init() before timing), and too many chunks make the supervisor spend its time scheduling.
- Anything that needs an actively maintained dependency. The last release was 0.8.2 (2024-12-26) and the last main commit 2025-04-21. There are 84 open issues, including open correctness bugs (#691 reset_index on unexecuted groupby output, #671 head(100) wrong on TPC-H Q18 output).
- Python 3.13+: PyPI has wheels only for CPython 3.9-3.12.
- GPU (cuDF/CuPy) production use. Many GPU-labelled bugs are still open, such as nunique failing on GPU (#344), cuDF NA deserialization errors (#406) and CUDA memory not being released on shutdown (#377).

## How it is fast

Data is split into chunks that plain pandas/NumPy runs in separate worker processes, so there is no GIL, and intermediate results go to a shared-memory storage service (disk, mmap or Vineyard backends are optional). The core idea is dynamic (iterative) tiling: Xorbits executes the first chunks, collects their real shapes, sizes and dtypes, and only then tiles the rest of the graph. That lets it choose tree-reduce or shuffle-reduce for groupby.agg, merge small chunks up to chunk_store_limit (512 MB by default), and handle skewed joins that Dask and Modin partition blindly. It adds coloring-based graph-level fusion of the chunk graph into subtasks, operator fusion through NumExpr/JAX/CuPy, column pruning, and breadth-first plus locality-aware scheduling onto NUMA-node or GPU 'bands'. The paper's ablation credits dynamic tiling with 7.08x (TPC-H Q2, SF1000) and 10.59x (Q7, SF100), and graph fusion with 3.80x (Q7) and 2.04x (Q8).

## Compared with alternatives

Pick it over Modin when data exceeds one node or merges are skewed: in the paper Modin on Ray OOMed on SF1000 and was 37x slower on skewed UC10, even though both reach 96.7% pandas-API coverage. FireDucks and cuDF (cudf.pandas) are single-machine pandas accelerators with much larger speedups over pandas, so Xorbits is only the right choice when you need multi-node scale-out behind the pandas API.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | xoscar (actor runtime), numpy, pandas, scipy, scikit-learn, pyarrow, fsspec, cloudpickle, pyyaml, psutil, tornado, sqlalchemy, defusedxml, tqdm, uvloop (non-Windows). Optional: ray, kubernetes, vineyard, jax, numexpr/lz4, s3fs, adlfs, datasets. |
| **Minimum toolchain** | Python &gt;=3.9. PyPI 0.8.2 wheels cover CPython 3.9-3.12, and building from source needs Cython &gt;=0.29.33. setup.cfg declares pandas &gt;=1.0, but CI carries a TODO that pandas 2.2.3 does not work well with numpy 2.2 / pyarrow 19. |
| **Platforms** | Wheels for Linux x86-64/aarch64 (manylinux2014), macOS x86-64/arm64 and Windows amd64. Cluster deployment is via CLI, Kubernetes (including EKS) or SLURM. Optional NVIDIA GPU through cuDF/CuPy (gpu=True on loaders). |
| **Thread safety** | Not documented. Execution runs in separate worker processes behind a client session created by xorbits.init() (or implicitly on the first compute). |
| **Drop-in for the baseline** | partial — it is not API-compatible with Dask. Code written with dd.\*, .compute(), map_partitions or repartition must be rewritten as plain pandas-style code (the Xorbits equivalent of map_partitions is map_chunk). As a pandas replacement it is close to drop-in: the paper reports 96.7% coverage on 30 pandas asv cases, against 46.7% for Dask. Unimplemented methods fall back to pandas (see gotchas). |

## Gotchas

- Silent-scale fallback: any pandas method Xorbits has not implemented is emitted as a RuntimeWarning '&lt;Type&gt;.&lt;method&gt; will fallback to Pandas'. It then runs after rechunking the whole object into one chunk (core/adapter.py), so a single worker must hold the full frame. On 1 TB data that means OOM.
- Deferred execution plus iterative tiling means a statement can trigger partial execution mid-plan whenever metadata such as a post-filter shape is unknown. Errors and cost appear later than they would in pandas. Call xorbits.run() to force evaluation, and warm up with xorbits.init() before benchmarking.
- Performance depends on chunk_store_limit (512 MB by default). The docs say raising it helps little on CPU but should be raised on GPU. chunk_size= on constructors is meant for debugging.
- Open operational bugs include 'Too many open files' (#769, #731), gzip read_csv using only one core (#738), and read_parquet memory-allocation errors (#729).

## Known shortcomings

- The \~8x vs Dask / \~4x vs Modin come from the authors' ICDE 2024 paper on AWS r6i; Dask/Modin are not listed baselines.
- Unimplemented pandas methods fall back by squashing the whole frame to one chunk on one worker (OOM at TB scale). Not a Dask drop-in (no dd.\*, .compute(), map_partitions), though \~96.7% pandas-compatible. Stale: last release 0.8.2 (2024-12), last main commit 2025-04, 84 open issues including correctness bugs (#691 reset_index, #671 head), no Python 3.13 wheels. First-party paper with no CPU model, compared only with pandas-API frameworks (never DuckDB/Polars), and TPC-H ratios skip queries where baselines failed.

## Caveats and trade-offs

baseline_in_list=false: the main comparisons are against distributed pandas-API systems (Dask DataFrame, Modin on Ray, pandas API on Spark). The paper includes pandas only on the single-node census/plasticc pipelines, where it is slowest (figure only). The paper is by the Xorbits authors, so it is first-party even though peer-reviewed. Versions are stated (Xorbits 0.6.3, pandas 2.1.1, PySpark 3.5.0, Dask 2023.9, Modin 0.24.1), with default configurations and 7 runs dropping the max and min, but no CPU model. The paper notes that TPC-H via the pandas API is 'fundamentally unfair' vs SQL systems. The last default-branch commit was 2025-04-21 (about 17 months ago), so it is stale.

Because the workload sizes (100GB-1TB) exceed single-node pandas memory, pandas itself is not directly benchmarked here (would OOM); the real comparison is against other distributed pandas-API frameworks (Dask/Modin/Koalas), not the pandas baseline itself.

## Maintenance

Stale: last release 0.8.2 in December 2024, last main commit April 2025 (cuDF 25.2 compat), later pushes are dependabot branches only. It is Apache-2.0 and pip-installable with prebuilt wheels, but the large Mars-derived codebase is not something you can realistically vendor or maintain yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C. The companion paper was peer-reviewed and published at ICDE 2024, Industrial and Application Track (DOI 10.1109/ICDE60146.2024.00392, pp. 5211-5223, per Crossref). It shows wins over pandas, Dask, Modin and PySpark with stated versions on AWS r6i instances, and TPC-H code is in the repo (benchmarks/tpch/run_queries.py). The paper names no CPU model, compiler or flags, so it cannot reach A.
- **Verifier notes:** The comparisons-page numbers match. I upgraded C to B because the arXiv companion paper is confirmed published at ICDE 2024 (peer-reviewed industrial track). Metadata checks out: Apache-2.0, 1,199 stars, main last commit 2025-04-21 (repo pushed_at 2026-02-14 is from a non-default branch).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://xorbits.readthedocs.io/en/latest/getting_started/why_xorbits/comparisons.html>
  - <https://arxiv.org/abs/2401.00865>
  - <https://arxiv.org/pdf/2401.00865v2>
  - <https://api.crossref.org/works?query.bibliographic=Xorbits+Automating+Operator+Tiling+for+Distributed+Data+Science&rows=3>
  - <https://github.com/xorbitsai/xorbits>
  - <https://github.com/xorbitsai/xorbits/tree/main/benchmarks/tpch>
- **Sources the enricher read:**
  - <https://github.com/xorbitsai/xorbits>
  - <https://github.com/xorbitsai/xorbits/blob/main/python/setup.cfg>
  - <https://github.com/xorbitsai/xorbits/blob/main/python/pyproject.toml>
  - <https://github.com/xorbitsai/xorbits/blob/main/python/xorbits/pandas/pandas_adapters/core.py>
  - <https://github.com/xorbitsai/xorbits/blob/main/python/xorbits/core/adapter.py>
  - <https://github.com/xorbitsai/xorbits/blob/main/benchmarks/tpch/README.md>
  - <https://github.com/xorbitsai/xorbits/blob/main/.github/workflows/python.yaml>
  - <https://github.com/xorbitsai/xorbits/blob/main/doc/source/user_guide/best_practices.rst>
  - <https://github.com/xorbitsai/xorbits/blob/main/doc/source/user_guide/deferred_execution.rst>
  - <https://github.com/xorbitsai/xorbits/blob/main/doc/source/user_guide/storage_backend.rst>
  - <https://github.com/xorbitsai/xorbits/blob/main/doc/source/user_guide/chunking.rst>
  - <https://github.com/xorbitsai/xorbits/blob/main/doc/source/user_guide/operator_fusion.rst>
  - <https://github.com/xorbitsai/xorbits/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/xorbitsai/xorbits/issues/671>
  - <https://github.com/xorbitsai/xorbits/issues/691>
  - <https://github.com/xorbitsai/xorbits/issues/499>
  - <https://github.com/xorbitsai/xorbits/issues/738>
  - <https://github.com/xorbitsai/xorbits/releases>
  - <https://github.com/xorbitsai/xorbits/commits/main>
  - <https://github.com/xorbitsai/xorbits/branches>
  - <https://xorbits.readthedocs.io/en/latest/getting_started/why_xorbits/comparisons.html>
  - <https://xorbits.readthedocs.io/en/latest/getting_started/why_xorbits/fast.html>
  - <https://xorbits.readthedocs.io/en/latest/getting_started/why_xorbits/pandas.html>
  - <https://xorbits.readthedocs.io/en/latest/user_guide/deployment.html>
  - <https://xorbits.readthedocs.io/en/latest/user_guide/deployment_local.html>
  - <https://arxiv.org/pdf/2401.00865v2>
  - <https://pypi.org/pypi/xorbits/json>
  - <https://pypi.org/pypi/xorbits/0.8.2/json>
  - <https://hn.algolia.com/api/v1/search?query=xorbits&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/xorbitsai/xorbits`) · [data/wave6/enrich/raw/github_com_xorbitsai_xorbits.json](../../../data/wave6/enrich/raw/github_com_xorbitsai_xorbits.json) (enrichment confidence 0.75)

</details>
