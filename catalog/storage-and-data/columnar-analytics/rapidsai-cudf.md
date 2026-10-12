# cuDF (cudf.pandas)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> NVIDIA GPU DataFrame library; cudf.pandas runs unmodified pandas code on NVIDIA GPUs, 50-290x faster in vendor join/groupby benchmarks.

| | |
|---|---|
| **Beats** | pandas |
| **Claimed result** | Headline 'nearly 150x' (body: 'up to 150x faster', 'minutes to 1 or 2 seconds'). Figure 1 on 5GB: Join takes 4 min 27 s with pandas on CPU vs 1 s with cudf.pandas, and Groupby Advanced 4 min 34 s vs 2 s (\~267x and \~137x, derived from page data with GPU times rounded to whole seconds) |
| **Workload** | H2O.ai/DuckDB 'database-like ops' benchmark (join and groupby operations) on a \~5GB dataset, pandas vs cudf.pandas zero-code-change GPU accelerator |
| **Metric** | throughput |
| **Hardware** | Blog Figure 1 states 'HW: NVIDIA Grace Hopper, CPU: Intel Xeon Platinum 8480C' (the GH200 SKU is not named); SW pandas v2.2, RAPIDS cuDF 23.10. The linked RAPIDS per-query results (run 2023-11-06, data.rapids.ai/duckdb-benchmark) are labelled 'CPU: Intel(R) Xeon(R) Platinum 8480CL, GPU: NVIDIA H100' |
| **Adoption** | 9.8k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/NVIDIA/cudf) · [benchmark](https://developer.nvidia.com/blog/rapids-cudf-accelerates-pandas-nearly-150x-with-zero-code-changes/) |

## Verdict

NVIDIA ran the public duckdblabs db-benchmark itself, on the 5 GB (1e8-row) join and advanced-groupby tasks. It compared pandas 2.2 on a Xeon Platinum 8480C/8480CL with cudf.pandas from cuDF 23.10 on a Grace Hopper/H100 GPU; the per-query run is dated 2023-11-06. The blog headline is 4m27s to 1s for join and 4m34s to 2s for groupby-advanced. The per-query charts work out to roughly 129-293x (join) and about 50x (groupby-advanced), and DuckDB on the same CPU was only about 2-8x slower than cudf.pandas. The results are vendor-run, absent from the official DuckDB Labs results, not normalized for cost or power, and give no build flags.

## Use it when

- Existing pandas scripts or notebooks doing vectorized read_parquet/read_csv, merge, groupby-aggregate and filtering over millions of rows to tens of GB, on a Linux or WSL2 box with a Volta-or-newer NVIDIA GPU. The FAQ's rough threshold for a gain is 10,000-100,000+ rows.
- Interactive analysis in Jupyter where you want GPU speed without rewriting code: `%load_ext cudf.pandas` as the first cell, and the profiler shows which calls ran on the GPU.
- Datasets somewhat larger than GPU memory on native Linux: the default managed-memory pool oversubscribes GPU RAM instead of falling back to the CPU.
- Pipelines that feed GPU libraries such as cuML, XGBoost or PyTorch, where frames can stay on the device. These integrations are covered by nightly third-party CI.
- When the comparison really is single-threaded pandas: the vendor's own numbers show much smaller gains against a multithreaded CPU engine such as DuckDB.

## Skip it when

- No NVIDIA GPU, or a GPU older than Volta (compute capability below 7.0), macOS, native Windows (WSL2 only) or AMD/Intel GPUs: none of these are supported.
- Row-wise code: Python for-loops over cells, scalar indexing, and `.apply` with arbitrary Python UDFs. An open issue (#16491) reports an element-by-element loop running about 100x slower than plain pandas because each scalar access goes through the GPU, and non-vectorizable UDFs fall back to the CPU anyway.
- Small frames, under about 10k-100k rows: kernel launch and transfer overhead outweigh the parallelism.
- Code that depends on exact pandas semantics. The docs say joins do not preserve pandas row order, in-place mutation is not guaranteed across fallback, pickles written by plain pandas cannot be unpickled, and global state mutated inside a CPU-fallback UDF is lost. About 93% of pandas' 187k+ unit tests pass, and open bugs remain, e.g. groupby().all() on string dtype (#19312).
- Multi-GPU, distributed or truly out-of-core jobs: cudf.pandas is single-process and single-GPU. The FAQ points to Dask (cuDF backend) or Spark RAPIDS instead. If you can switch engines rather than keep pandas, DuckDB on the same Xeon was only about 2-8x slower than cudf.pandas in NVIDIA's own per-query results.

## How it is fast

Data is held column-wise in GPU memory, and each operation is a data-parallel CUDA kernel spread over thousands of threads with HBM bandwidth. The pandas baseline, by contrast, mostly runs on one CPU core. On current main, hash groupby inserts row indices into a cuco::static_set (linear probing, 50% load factor). It aggregates in per-thread-block shared-memory hash tables when key cardinality is low (threshold 128) and with global-memory atomics otherwise, and switches to a sort-based groupby for aggregations that cannot be hashed. Hash join builds an open-addressed table of 32-bit slots, each holding a build-row index plus a hash fingerprint, inserted lock-free with compare-and-swap and linear probing; duplicate build keys are grouped in CSR form. cudf.pandas adds an RMM pool allocator over CUDA managed memory with prefetching, which cuts allocation cost and lets data exceed GPU memory. Data is copied between host and device only when a call falls back to the CPU.

## Compared with alternatives

Pick cudf.pandas when you have an NVIDIA GPU and pandas code you do not want to rewrite. chDB (embedded ClickHouse SQL on DataFrames) and Bodo DataFrames (JIT-compiled Python) are the better fit on CPU-only machines, and Sirius, which is also built on libcudf, is the GPU choice when the workload is SQL on DuckDB rather than pandas.

## Integration

| | |
|---|---|
| **Form** | module (Python packages cudf-cu12 / cudf-cu13 on PyPI or conda -c rapidsai, wrapping the prebuilt libcudf CUDA C++ shared library, which is also shipped separately as libcudf) |
| **Dependencies** | NVIDIA driver plus CUDA 12 (driver &gt;= 525.60.13) or CUDA 13 (driver &gt;= 580.65.06); Python deps libcudf, pylibcudf, rmm, cupy, numba and numba-cuda, cuda-bindings, pyarrow &gt;= 19, numpy 2.x, and pandas 3.0.x (the 26.08.1 wheels pin pandas &gt;=3.0.0,&lt;3.0.4) |
| **Minimum toolchain** | Python 3.11+ for the wheels. Building libcudf from source needs C++20/CUDA C++20, GCC 13.3+, nvcc 12.9+ and CMake 3.29.6+, with a CUDA 12.2+ runtime |
| **Platforms** | Linux x86-64 and aarch64 (manylinux_2_28 wheels, glibc &gt;= 2.28), and Windows 11 via WSL2 only; needs an NVIDIA GPU with compute capability &gt;= 7.0 (Volta or newer; Pascal dropped in 24.02) |
| **Thread safety** | The libcudf developer guide calls it 'thread-safe, single-GPU' primitives. Work goes on the default CUDA stream (per-thread default stream is opt-in via CUDF_USE_PER_THREAD_DEFAULT_STREAM), and calls should be treated as asynchronous. Thread safety of cudf.pandas is not documented beyond a test that the per-thread disable_module_accelerator context works under ThreadPoolExecutor. Joblib is listed as not working. |
| **Drop-in for the baseline** | partial - the full pandas API is reachable through the import-hook proxy (CPU fallback covers what cuDF lacks), but only the cuDF-supported subset runs on the GPU. Join row order, mutation, pickling and some dtype edge cases differ from pandas, and the proxy must be installed before pandas is imported, including in multiprocessing workers. |

## Gotchas

- Fallback is silent. An unsupported call, an unsupported keyword argument or a GPU OOM quietly runs in pandas on the CPU, with GPU-to-host copies. A 2024 tracking issue (#17458) says fewer than half of the pandas tests actually ran on the GPU. Use `python -m cudf.pandas --profile` / `--line-profile` or `%%cudf.pandas.profile` to see where time goes. For benchmarking, `CUDF_PANDAS_FALLBACK_MODE=1` forces the CPU path.
- Activation order matters: once pandas has been imported (even indirectly), cudf.pandas cannot take over, so restart the kernel. Multiprocessing or ProcessPoolExecutor workers need `cudf.pandas.install()` at the very top of the script. A cudf.pandas session also cannot be mixed with a direct `import cudf`.
- Proxy arrays subclass numpy.ndarray and make an eager device-to-host copy when created (e.g. from `.unique()`) so the NumPy C API sees a valid buffer. Calls that return arrays therefore pay a hidden transfer.
- pandas pinning is tight and moves every release (26.08.1 requires pandas &gt;=3.0.0,&lt;3.0.4), while the FAQ still says 'only compatible with pandas 2'. Upgrading pandas independently can break the install. On WSL2 managed memory is not used, so data is capped at physical GPU memory.

## Known shortcomings

- NVIDIA ran db-benchmark itself; cudf.pandas isn't in the official DuckDB Labs results. A GPU (H100, Xeon 8480CL host) against mostly single-threaded pandas with no cost normalization; against DuckDB on the same CPU the gain is only \~2-8x (derived). Repo moved to NVIDIA/cudf (verifier downgrade).
- Unsupported operations, keyword arguments or GPU OOM fall back silently to CPU pandas (a 2024 report, #17458, found under half of pandas tests actually ran on GPU; the profiler is needed to see it). Row loops, scalar access and Python UDFs are slow (a loop \~100x slower than plain pandas, #16491). Semantic gaps (join row order, mutation/pickle/global-UDF quirks; \~93% of 187k pandas tests pass). NVIDIA Volta+ only; Linux or WSL2 (no managed-memory oversubscription on WSL2); single GPU; tight pandas version pin; stale FAQ.

## Caveats and trade-offs

The benchmark was run and published by NVIDIA (the vendor) on the public H2O.ai/DuckDB db-benchmark harness, and cudf.pandas is not in the official DuckDB Labs results. The hardware is asymmetric: a data-center GPU (Grace Hopper per the blog, H100 per the per-query charts) against pandas on a Xeon Platinum 8480C/8480CL, with pandas executing these operations largely single-threaded, and no cost or power normalization is given. The blog says some operations fall back to the CPU. Figure 1's CPU totals (4m27s, 4m34s) do not match the per-query charts, which sum to about 169s for join and about 140s for groupby-advanced. On those per-query charts, cudf.pandas takes 1.31s/0.57s (join) and about 2.85s/2.80s (groupby-advanced) over runs 1 and 2, which is about 129-293x and about 50x over pandas. DuckDB on the same CPU takes 6.17s/4.71s and 7.27s/6.58s, so the GPU gain over a multithreaded CPU engine is only about 2-8x (all derived from page data). Compiler/build flags are not stated.

Requires an NVIDIA GPU; cudf.pandas silently falls back to CPU pandas for unsupported operations, so realized speedup on arbitrary code varies widely from the headline figure

## Maintenance

Very active: 26.08.1 was released 2026-08-25, there are commits daily and 9.8k stars. The code is Apache-2.0 and installs from PyPI or conda, and the repo has moved from rapidsai/cudf to NVIDIA/cudf. The Python layer tracks each pandas release closely, so expect version pins to follow pandas.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** This is NVIDIA's own run of the public duckdblabs/db-benchmark suite, patched to use cudf.pandas (the diff is documented at docs.nvidia.com/cudf/latest/cudf_pandas/benchmarks/). cudf.pandas is not part of the official DuckDB Labs suite or results, which have no cudf solution, so these are first-party numbers on a third-party harness. Hardware and versions are stated but no build details are, so C, not B.
- **Verifier notes:** The 150x headline and the minutes-to-seconds figures are on the page, but the evidence is vendor-run on its own GPU hardware, so C. The record's 'GH200' is not stated (the blog says Grace Hopper) and the per-query results page says H100, a discrepancy. rapidsai/cudf now redirects to NVIDIA/cudf (Apache-2.0, 9,764 stars, last commit 2026-09-25, not a fork); consider updating repo_url.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://developer.nvidia.com/blog/rapids-cudf-accelerates-pandas-nearly-150x-with-zero-code-changes/>
  - <https://developer-blogs.nvidia.com/wp-content/uploads/2024/03/150x-pandas.png>
  - <https://docs.rapids.ai/api/cudf/stable/cudf_pandas/benchmarks/>
  - <https://docs.nvidia.com/cudf/latest/cudf_pandas/benchmarks/>
  - <https://data.rapids.ai/duckdb-benchmark/index.html>
  - <https://data.rapids.ai/duckdb-benchmark/duckdb-benchmark-pandas-Join-results-20231106.png>
  - <https://data.rapids.ai/duckdb-benchmark/duckdb-benchmark-cudf.pandas-Join-results-20231106.png>
  - <https://data.rapids.ai/duckdb-benchmark/duckdb-benchmark-pandas-Groupby%20Advanced-results-20231106.png>
  - <https://data.rapids.ai/duckdb-benchmark/duckdb-benchmark-cudf.pandas-Groupby%20Advanced-results-20231106.png>
  - <https://data.rapids.ai/duckdb-benchmark/duckdb-benchmark-duckdb-Join-results-20231106.png>
  - <https://data.rapids.ai/duckdb-benchmark/duckdb-benchmark-duckdb-Groupby%20Advanced-results-20231106.png>
  - <https://github.com/duckdblabs/db-benchmark>
  - <https://github.com/rapidsai/cudf>
- **Sources the enricher read:**
  - <https://github.com/NVIDIA/cudf>
  - <https://api.github.com/repos/NVIDIA/cudf>
  - <https://github.com/NVIDIA/cudf/blob/main/README.md>
  - <https://github.com/NVIDIA/cudf/blob/main/docs/cudf/source/cudf_pandas/how-it-works.md>
  - <https://github.com/NVIDIA/cudf/blob/main/docs/cudf/source/cudf_pandas/faq.md>
  - <https://github.com/NVIDIA/cudf/blob/main/docs/cudf/source/cudf_pandas/benchmarks.md>
  - <https://github.com/NVIDIA/cudf/blob/main/docs/cudf/source/cudf_pandas/usage.md>
  - <https://github.com/NVIDIA/cudf/blob/main/docs/cudf/source/cudf_pandas/developer_guide.md>
  - <https://github.com/NVIDIA/cudf/blob/main/CONTRIBUTING.md>
  - <https://github.com/NVIDIA/cudf/blob/main/VERSION>
  - <https://github.com/NVIDIA/cudf/blob/main/cpp/CMakeLists.txt>
  - <https://github.com/NVIDIA/cudf/blob/main/python/cudf/pyproject.toml>
  - <https://github.com/NVIDIA/cudf/blob/main/cpp/src/groupby/groupby.cu>
  - <https://github.com/NVIDIA/cudf/blob/main/cpp/src/groupby/hash/compute_groupby.cu>
  - <https://github.com/NVIDIA/cudf/blob/main/cpp/src/groupby/hash/helpers.cuh>
  - <https://github.com/NVIDIA/cudf/blob/main/cpp/include/cudf/join/hash_join.hpp>
  - <https://github.com/NVIDIA/cudf/blob/main/cpp/src/join/hash_join/hash_join_impl.cuh>
  - <https://github.com/NVIDIA/cudf/blob/main/cpp/src/join/hash_join/hash_csr.cuh>
  - <https://github.com/NVIDIA/cudf/blob/main/cpp/doxygen/developer_guide/DEVELOPER_GUIDE.md>
  - <https://github.com/NVIDIA/cudf/blob/main/python/cudf/cudf_pandas_tests/test_disable_per_thread_safety.py>
  - <https://github.com/NVIDIA/cudf/blob/main/python/cudf/cudf_pandas_tests/data/disable_cudf_pandas_multi_thread.py>
  - <https://github.com/NVIDIA/cudf/issues/17458>
  - <https://github.com/NVIDIA/cudf/issues/16491>
  - <https://github.com/NVIDIA/cudf/issues/19312>
  - <https://github.com/NVIDIA/cudf/issues/20178>
  - <https://github.com/NVIDIA/cudf/issues/15976>
  - <https://github.com/NVIDIA/cudf/releases>
  - <https://github.com/NVIDIA/cudf/issues?q=is%3Aissue+cudf.pandas+slow>
  - <https://github.com/NVIDIA/cudf/issues?q=is%3Aissue+cudf.pandas+memory+OOM>
  - <https://github.com/NVIDIA/cudf/pulls?q=is%3Apr+is%3Amerged+%22pandas+3%22>
  - <https://pypi.org/pypi/cudf-cu12/json>
  - <https://pypi.org/pypi/cudf-cu13/json>
  - <https://developer.nvidia.com/blog/rapids-cudf-accelerates-pandas-nearly-150x-with-zero-code-changes/>
  - <https://docs.nvidia.com/datascience/install/>
  - <https://data.rapids.ai/duckdb-benchmark/index.html>
  - <https://hn.algolia.com/api/v1/search?query=cudf.pandas&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=cudf%20pandas%20150x>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/rapidsai/cudf`) · [data/wave6/enrich/raw/github_com_rapidsai_cudf.json](../../../data/wave6/enrich/raw/github_com_rapidsai_cudf.json) (enrichment confidence 0.78)

</details>
