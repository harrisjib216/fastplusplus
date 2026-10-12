# Modin

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `Apache-2.0` · 🟢 active

> Parallel, partitioned pandas API on Ray, Dask or MPI; wins over pandas on heavy single ops, loses on small ones.

| | |
|---|---|
| **Beats** | pandas |
| **Claimed result** | \~7x faster than pandas for the groupby().apply() workload (author notes Modin only wins once a pandas op takes &gt;5s; it lost in the for-loop anti-pattern example). |
| **Workload** | Kaggle 'customer-segmentation' workflow (its data.csv; size not stated on the page) run in a mixed mode where only the heavy groupby().apply() with a custom aggregation is wrapped in Modin. The page also has a 'heaviest pandas operations' showcase chart and a for-loop anti-pattern example; the linked for_loop_vs_groupby.py script uses 10M rows x 10 columns with 1M unique goods (about 80 s loop). |
| **Metric** | throughput |
| **Hardware** | HP ZCentral 4R Workstation: Intel Xeon W-2245, 8 cores/16 threads, 64GB RAM |
| **Adoption** | 10.4k stars |
| **Last commit** | 2026-02-10 |
| **Links** | [repository](https://github.com/modin-project/modin) · [benchmark](https://dchigarev.github.io/modin_perf_examples/gh_page_1.html) |

## Verdict

The benchmark is a single timed run from a first-party blog post by Modin contributor dchigarev (Mar 2024). A simplified Kaggle customer-segmentation script ran a groupby(['CustomerID','StockCode']).apply() with an iterrows-based UDF: pandas 2.2.1 took 257.6 s, Modin 0.28.0 on Ray 2.9.1 took 35.0 s when only that block was wrapped (about 7.4x, conversions and Ray start-up included) and 30.7 s under a full import swap (8.4x by arithmetic; the table labels it 8.56x). The machine was an 8-core/16-thread Xeon W-2245 with 64 GB on Ubuntu 22.04 and Python 3.9.18; there are no compiler flags (pure Python), and the dataset size is not stated.

## Use it when

- A pandas pipeline where one or a few operations dominate the runtime and each already takes more than about 5 s in pandas, especially groupby().apply() with an arbitrary Python UDF. The benchmark's 258 s groupby.apply dropped to 31-35 s.
- Row-wise or column-wise apply(), groupby().rolling() and large read_csv on multi-GB data. The author's chart shows 6.2x for apply, 4.3x for groupby-rolling, 2.0x for merge and 1.7x for read_csv on 8 cores, conversion time included.
- Machines with at least 4 cores / 8 threads and 32 GB RAM (the blog's stated minimum), or an existing Ray/Dask cluster you want to point pandas code at without rewriting it.
- Data somewhat larger than RAM on a single node, using Ray object-store spilling to disk, when you must keep the pandas API.
- Keeping the rest of the workflow in plain pandas and converting only the hot block (from_pandas ... to_pandas). In the benchmark this mixed mode beat a full import swap end to end: 40.8 s vs 55.0 s, against 263.5 s for pandas.

## Skip it when

- Short operations or many small ones. In the benchmark, every non-groupby stage got slower under full Modin (read and preprocess 1.0 s to 6.2 s, fit/predict 2.6 s to 7.4 s). A 10,000-iteration Python for-loop over df filters went from 79 s in pandas to 905 s in Modin, about 11x slower (0.007 s vs 0.09 s per iteration).
- Vectorized analytical queries on modest data or few cores. Issue #6948 reported TPC-H Q1/Q6 at SF1 slower than pandas on a 4-core box, and a maintainer then reproduced poor results up to SF10 on a 16-core machine. He traced it to deferred-execution metadata being materialized sequentially.
- Stacks on pandas 3.x or new Python versions. setup.py pins pandas &gt;=2.2,&lt;2.4 and CI tests only Python 3.9-3.11.
- Long-lived production code that needs an active upstream. The last release was 0.37.1 on 2025-10-02 and the only later commit is a typo fix (2026-02-10). Issue #7704 (July 2026), which asks whether the project will be archived, has no reply, and correctness bug reports from Nov-Dec 2025 (#7690-#7694) have no response.
- Code that needs bit-for-bit pandas results. The troubleshooting guide documents per-partition dtype inference differences in read_csv, and range-partitioned groupby on multiple keys may return unsorted results even with sort=True (#6875).

## How it is fast

Modin gets no faster kernels. It runs ordinary pandas code on many partitions at once in worker processes, which sidesteps pandas' single thread and the GIL. A query compiler maps pandas calls onto a small dataframe algebra: map, MapReduce-style reduce, full-axis (whole row or column) functions and shuffles. groupby.apply(), transform() and rolling() always use a range-partitioning shuffle, which moves each group into one partition so the Python UDF runs per partition in parallel. That is how the benchmark's iterrows-heavy UDF gained about 8x. Low-cardinality groupby aggregations use MapReduce, merge defaults to a broadcast join, and Ray can spill the object store to disk for data larger than memory.

## Compared with alternatives

Pick Modin over cuDF (cudf.pandas) when you have no NVIDIA GPU, and over FireDucks when you need Apache-2.0 source, Windows or a multi-node Ray/Dask cluster, or when your hot spot is a Python-UDF groupby.apply, which Modin runs in parallel and FireDucks' own catalog entry lists as slower than pandas. For vectorized TPC-H-style pipelines, Xorbits (which claims \~4x faster than Modin at SF100), FireDucks or chDB are likely the better choice.

## Integration

| | |
|---|---|
| **Form** | module (pure-Python package `modin` on PyPI/conda-forge; engines installed as extras: modin[ray], modin[dask], modin[mpi], modin[all]) |
| **Dependencies** | pandas&gt;=2.2,&lt;2.4, numpy&gt;=1.22.4, fsspec, psutil, packaging, typing-extensions; plus one engine: ray&gt;=2.10,&lt;3 with pyarrow&gt;=10.0.1, or dask/distributed&gt;=2.22, or unidist[mpi] (needs a system MPI implementation installed first) |
| **Minimum toolchain** | Python &gt;=3.9 (CI runs 3.9 by default and 3.10/3.11 on scheduled runs; newer versions are not in CI); pandas 2.2-2.3 only |
| **Platforms** | Linux, macOS and Windows via pip (per README; CI clean-install on Ubuntu and Windows); single node or multi-node Ray/Dask/MPI clusters |
| **Thread safety** | Not documented. The docs strongly advise against combining Modin with Python multiprocessing, because it duplicates Ray clusters and causes undefined behavior, and they say that changing the engine after the first operation is undefined behavior. |
| **Drop-in for the baseline** | partial: the import swap works for most code (the README badge shows 90.8% DataFrame and 88.05% Series API coverage), but uncovered methods silently fall back to single-threaded pandas at a conversion cost, passing pandas objects into Modin calls slows them down or raises an error, and some results differ (read_csv dtypes, groupby sort order) |

## Gotchas

- Default-to-pandas is a performance cliff. An unimplemented method gathers the whole partitioned frame into one pandas DataFrame, runs it single-threaded, then re-partitions it, and the only signal is a warning.
- Benchmarking is tricky. Execution is deferred on Ray, so call modin.utils.execute(df) before stopping a timer. The first operation also pays engine start-up and worker warm-up (the troubleshooting guide's 'poor performance of the first operation'), so warm up before timing.
- Partitioning needs tuning on wide or square frames. NPartitions caps splits per axis, so a square frame gets NPartitions^2 blocks: the docs' 112-core example has 12,544 partitions and 10x df.abs() taking 23.64 s, versus 0.25 s after setting NPartitions to sqrt(cores). Frames can also become unbalanced after many column inserts, which needs df._repartition().
- merge defaults to a broadcast join that turns the right frame into pandas and ships it to every left row partition. Put the smaller frame on the right, or set cfg.RangePartitioning, which covers only left/inner joins on a single `on` column.

## Known shortcomings

- Vendor/project benchmark (\~7x vs pandas) with Modin 0.28.0, pandas 2.2.1 and Ray 2.9.1; gains depend on multi-core parallelism and dataset size.
- The \~7.4-8.4x groupby.apply win comes from running the Python UDF in parallel worker processes, not faster kernels; small operations lose (other stages 3-8x slower; a for-loop 79 s to 905 s), and TPC-H SF1-SF10 is slower than pandas (#6948, reproduced by a maintainer). Effectively stalled: last release 0.37.1 (2025-10), archival question #7704 unanswered, pinned to pandas &lt;2.4 with CI on Python 3.9-3.11 only. Silent fallback to single-threaded pandas; lazy execution and first-op warmup skew timings; open correctness bugs (#7690-7694) unanswered; read_csv dtype drift across partitions.

## Caveats and trade-offs

The blog is by Dmitry Chigarev (dchigarev), the #3 contributor to modin-project/modin, so it is first-party, not independent. Contrary to the earlier caveat, the appendix does state the hardware (HP ZCentral 4R, Xeon W-2245 8C/16T, 64 GB), Modin 0.28.0, pandas 2.2.1, Ray 2.9.1, Python 3.9.18 and Ubuntu 22.04.2 LTS, and the scripts are public in dchigarev/modin_perf_examples. The 7x is a rounded text figure and the groupby dataset size is not stated on the page. The author says Modin tends to win only when a pandas op takes more than 5 s, that full-Modin adoption slowed other parts of the workflow, and that the for-loop example is an anti-pattern where Modin should not be used.

Modin's own benchmark author states its implementation is only faster than pandas when the pandas operation already takes &gt;5 seconds; a small/short-running or sequential for-loop workload was slower under Modin than plain pandas.

## Maintenance

The record says active, but development has effectively stalled: the last release was 0.37.1 (Oct 2025), the only commit since is a Feb 2026 typo fix, and a July 2026 issue asking about archival has no reply. It is Apache-2.0, pure Python and pip-installable today, but it is pinned to pandas &lt;2.4.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party blog post by dchigarev, Modin's #3 contributor, states 'you get a 7x speed-up for this groupby' against pandas on a named Xeon W-2245, and gives Modin 0.28.0, pandas 2.2.1, Ray 2.9.1 and Python 3.9.18. The scripts are public (dchigarev/modin_perf_examples gh_page_1/customer_segmentation_simplified.py, which has a PANDAS_MODE=Pandas/Modin/Mixed switch). The 7x is a rounded figure, the dataset size is not stated on the page, and no compiler or flags are given, so it stays C.
- **Verifier notes:** The record's claim matches the page. I corrected the caveat that said versions were missing (they are in the appendix) and noted that the benchmark scripts are public. It is near-A apart from the missing compiler/flags and dataset size, so it stays C.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://dchigarev.github.io/modin_perf_examples/gh_page_1.html>
  - <https://raw.githubusercontent.com/dchigarev/modin_perf_examples/master/gh_page_1/for_loop_vs_groupby.py>
  - <https://raw.githubusercontent.com/dchigarev/modin_perf_examples/master/gh_page_1/customer_segmentation_simplified.py>
  - <https://github.com/modin-project/modin>
- **Sources the enricher read:**
  - <https://github.com/modin-project/modin>
  - <https://github.com/modin-project/modin/blob/main/setup.py>
  - <https://github.com/modin-project/modin/blob/main/docs/supported_apis/defaulting_to_pandas.rst>
  - <https://github.com/modin-project/modin/blob/main/docs/usage_guide/optimization_notes/index.rst>
  - <https://github.com/modin-project/modin/blob/main/docs/usage_guide/optimization_notes/range_partitioning_ops.rst>
  - <https://github.com/modin-project/modin/blob/main/docs/getting_started/faq.rst>
  - <https://github.com/modin-project/modin/blob/main/docs/getting_started/troubleshooting.rst>
  - <https://github.com/modin-project/modin/blob/main/docs/getting_started/why_modin/out_of_core.rst>
  - <https://github.com/modin-project/modin/blob/main/docs/development/architecture.rst>
  - <https://github.com/modin-project/modin/blob/main/modin/core/storage_formats/pandas/query_compiler.py>
  - <https://github.com/modin-project/modin/blob/main/.github/workflows/ci.yml>
  - <https://github.com/modin-project/modin/commits/main>
  - <https://github.com/modin-project/modin/releases>
  - <https://github.com/modin-project/modin/issues/6948>
  - <https://github.com/modin-project/modin/issues/7704>
  - <https://github.com/modin-project/modin/issues/7693>
  - <https://github.com/modin-project/modin/issues?q=slower+than+pandas>
  - <https://pypi.org/pypi/modin/json>
  - <https://dchigarev.github.io/modin_perf_examples/gh_page_1.html>
  - <https://github.com/dchigarev/modin_perf_examples>
  - <https://github.com/dchigarev/modin_perf_examples/blob/master/gh_page_1/customer_segmentation_simplified.py>
  - <https://github.com/dchigarev/modin_perf_examples/blob/master/requirements.txt>
  - <https://raw.githubusercontent.com/dchigarev/modin_perf_examples/master/docs/imgs/img2_customer_segmentation_pandas_vs_modin.jpg>
  - <https://raw.githubusercontent.com/dchigarev/modin_perf_examples/master/docs/imgs/img3_customer_segmentation_mixed_pandas_modin.jpg>
  - <https://raw.githubusercontent.com/dchigarev/modin_perf_examples/master/docs/imgs/img4_heavy_operations.jpg>
  - <https://raw.githubusercontent.com/dchigarev/modin_perf_examples/master/docs/imgs/img6_modin_in_a_for_loop.jpg>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/modin-project/modin`) · [data/wave6/enrich/raw/github_com_modin_project_modin.json](../../../data/wave6/enrich/raw/github_com_modin_project_modin.json) (enrichment confidence 0.8)

</details>
