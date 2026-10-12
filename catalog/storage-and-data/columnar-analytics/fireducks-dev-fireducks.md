# FireDucks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Python (compiler-generated C++ backend)` · `BSD-3-Clause` · 🟢 active

> NEC's closed-source drop-in for pandas: lazy IR optimization plus multithreaded Arrow kernels; first-party TPC-H SF10 claims 141x.

| | |
|---|---|
| **Beats** | pandas |
| **Claimed result** | Average speedup over pandas across 22 TPC-H queries: FireDucks 141x (excl. I/O) / 55x (incl. I/O); for comparison on the same page, DuckDB 109x/61x and Polars 58x/50x |
| **Workload** | TPC-H at Scale Factor 10 (\~10GB), all 22 queries, both excluding I/O (RUN_IO_TYPE=skip) and including I/O (RUN_IO_TYPE=parquet), on AWS EC2 m7i.8xlarge (Intel Xeon Gold 6526Y, 32 cores, 512GB RAM, Ubuntu 24.04, performance governor) |
| **Metric** | latency |
| **Hardware** | AWS EC2 m7i.8xlarge, Intel Xeon Gold 6526Y (32 cores), 512GB RAM, Ubuntu 24.04, cpufreq-governor=performance |
| **Adoption** | 927 stars on the GitHub issue-tracker repo; NEC-backed commercial project, widely cited in dataframe-benchmark discussions |
| **Last commit** | 2025-05-22 |
| **Links** | [repository](https://github.com/fireducks-dev/fireducks) · [benchmark](https://fireducks-dev.github.io/docs/benchmarks/) |

## Verdict

FireDucks' own TPC-H SF10 run (22 queries written in pandas by the FireDucks team and executed through the import hook) on an AWS m7i.8xlarge (Xeon Gold 6526Y, 32 cores, 512 GB, Ubuntu 24.04, performance governor) reports an average 141x speedup over pandas excluding I/O and 55x including Parquet I/O, against DuckDB 109x/61x and Polars 58x/50x, so DuckDB wins once I/O counts. No library versions, compiler flags or independent reproduction exist, and result checking is off by default in the harness; in Nov 2024 the Polars author ran an earlier FireDucks through the same harness (including I/O, Polars-generated data, his own unstated hardware) and got slower times than Polars on q1-q9 (e.g. q9 58.6 s vs 1.68 s) and a std::length_error crash on q10.

## Use it when

- Existing vectorized pandas pipelines (read_parquet/read_csv, filter, merge, groupby-agg, sort) that you cannot afford to rewrite in Polars or SQL; try it by running the script under `python -m fireducks.pandas`.
- Multi-GB in-memory tables on many-core Linux x86-64 boxes (the headline run used 32 cores and TPC-H SF10), where pandas' single-threaded execution is the bottleneck.
- Code with a poorly ordered data flow, such as filtering after a merge, sorting whole frames, or selecting columns late. FireDucks' own talk says query-optimizing engines gain most here, because pushdown fixes the order automatically.
- CPU-only machines where cudf.pandas is not an option; Apple Silicon (macOS 14+ arm64) is also supported, as experimental since 1.2.7.

## Skip it when

- Loop-heavy code (iterrows, apply, row-wise loc/iloc, NumPy calls on frames). FireDucks' own PyData 2025 talk rates this code 'Slower' than pandas, UDFs in apply are not compiled, and users report 2-3x slowdowns there (issue #73).
- Workloads that hit unimplemented APIs. Fallbacks convert data to pandas and back and cache copies: users report memory growth that crashed a server (#73), and higher memory, longer runtime and failed end-to-end runs versus pandas on 1.4.3 (#80, Dec 2025).
- Modern or locked-down stacks. 1.4.4 requires pandas &lt;2.4 (pandas 3.0.x is current) and pyarrow 21.0.x exactly; an issue asking for pyarrow &gt;=23.0.1 to fix CVE-2026-25087 (#81, June 2026) has no reply. It does not support Python 3.14, native Windows, Linux aarch64 or glibc &lt;2.28.
- Environments that must audit or vendor code. The engine is a 32 MB closed-source .so from NEC, with no SBOM or build provenance, and the FAQ says no organization offers paid support. The GPU backend is enterprise-only.
- Remote or fsspec inputs (s3://, http URLs), non-default read_parquet arguments, and pandas subclassing or extension dtypes: all of these fall back to pandas or are out of scope.

## How it is fast

Each pandas call adds an op to a dataframe-specific intermediate representation. The wheel bundles LLVM/MLIR and TFRT and its extension exports MLIR symbols. A compiler pass optimizes that IR before it runs: projection pushdown (drop unused columns before sort, merge or groupby), predicate pushdown (filter before merge), pattern rewrites such as where().groupby() into filter-then-groupby, and caching of intermediate results. The default 'dfkl' backend then runs the ops as multithreaded C++ kernels over Apache Arrow columns, adding its own parallelism on top of Arrow compute, where pandas runs single-threaded; data is treated as immutable and column buffers are shared rather than copied.

## Compared with alternatives

Pick FireDucks over cuDF (cudf.pandas) when there is no NVIDIA GPU or the pandas code has an unoptimized data flow, because cuDF executes eagerly and FireDucks reorders lazily. Pick it over chDB when the code must stay pandas rather than become SQL. Prefer cuDF or chDB when you need an open-source, auditable engine or current pandas/pyarrow versions.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | firefw==1.4.4, pandas&gt;=1.5.3,&lt;2.4.0, pyarrow&gt;=21.0,&lt;21.1 (the extension links pyarrow's libarrow/libparquet .so.2100 directly). The wheel statically bundles LLVM/MLIR, TFRT, Abseil, Eigen, libdivide, pybind11 and nlohmann/json per its NOTICE. |
| **Minimum toolchain** | CPython 3.9-3.13 (binary wheels only, no sdist); Linux needs glibc 2.28+ (manylinux_2_28 since 1.4.0); macOS 14+. The extension's build comment names GCC 12.2.1 (Red Hat); flags are not documented. |
| **Platforms** | Linux x86-64 and macOS arm64 (macOS experimental since 1.2.7); no Windows (WSL suggested), no Linux aarch64. The top-level README still says Linux x86-64 only. |
| **Thread safety** | Not documented. Options live in a process-global mutable singleton (FIREDUCKS_FLAGS is read at import), and each op is parallelized internally by the backend. |
| **Drop-in for the baseline** | partial: the import hook covers the pandas API, but by design it differs. Errors surface at evaluation time, not at the call; isinstance(df, pandas.DataFrame) is False; merge/join row order may differ; df.copy(deep=False) does not alias data; subclassing, custom dtypes and underscore/experimental APIs are unsupported; unimplemented calls silently fall back to pandas. |

## Gotchas

- Lazy execution makes per-step timings meaningless. A user's '30,713x faster sort' (#72) and a 'slow head()' (#48) were both deferred work. Use FIREDUCKS_FLAGS="--benchmark-mode" or call ._evaluate() before timing.
- try/except KeyError around df[col] may not fire, because the lookup runs later. Use `if col in df` (non-lazy) or ._evaluate().
- Fallbacks are silent by default. Set FIREDUCKS_FLAGS="-Wfallback" to log them, and "--trace=3 --trace-file=-" for a per-kernel/fallback time profile.
- Memory is held longer than in pandas: column buffers are shared via shared_ptr until every referencing frame dies, the Arrow memory pool does not return freed memory to the OS promptly, and fallback caching can grow memory until gc.collect() runs. A delayed-deallocation bug was fixed in 1.4.0 (#69, #49).

## Known shortcomings

- First-party benchmark from NEC with binary-only wheels (the GitHub repo is an issue tracker, no public source); no compiler/flags and unpinned versions.
- Closed engine (32 MB .so with MLIR+TFRT+Arrow, no SBOM; GPU backend enterprise-only). Pins pandas&lt;2.4 and pyarrow 21.0.x exactly (pyarrow CVE issue #81 unanswered); no release since 1.4.4 (2025-12). Loops/apply/fallbacks are slower than pandas (its own PyData 2025 slides, #73); memory blowups and failed end-to-end runs (#73, #80). The harness's result check is off by default; in Polars' author's Nov 2024 run of the same harness an older FireDucks was slower than Polars on q1-q9 and crashed on q10. Lazy semantics: late errors, different merge row order, isinstance(pandas.DataFrame) is False.

## Caveats and trade-offs

All results are first-party (FireDucks' own docs site), and the TPC-H pandas queries were written by the FireDucks team. The db-benchmark result the page cites is FireDucks' own run of the suite (fireducks-dev.github.io/db-benchmark); the official duckdblabs/db-benchmark has no fireducks solution. FireDucks is closed source: PyPI carries only binary wheels (658 wheel files, no sdist), and the GitHub repo holds just a README and notebooks as an issue tracker. That is why usability is 'reference' even though the README and PyPI classifier say 3-Clause BSD. The page gives no pandas/Polars/DuckDB versions for the TPC-H run, and the README installs them unpinned with 'pip install -U'. Including I/O, DuckDB (61x) beats FireDucks (55x). The GitHub repo's last push was 2025-05-22, but PyPI release 1.4.4 shipped 2025-12-02, so maintenance is judged 'active' from releases.

Drop-in pandas replacement via import hook; compiler-accelerated lazy execution graph. The engine itself is closed-source: this GitHub repo is issue-tracker only (no source files), the wheel is distributed via PyPI, and only Linux x86_64 is supported.

## Maintenance

Rated active from its roughly monthly PyPI releases through 1.4.4 (2025-12-02), though none has shipped in the \~10 months since, the GitHub repo is only an issue tracker, and a pyarrow CVE issue is unanswered. Usability is 'reference': the engine is BSD-3-licensed on paper but ships as a binary-only wheel you can neither audit, patch nor vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** This is a first-party page. The benchmark code is public (fireducks-dev/polars-tpch, branch fireducks_20250204, a fork of pola-rs/polars-benchmark with pandas queries written by the FireDucks team) and the CPU is stated. It is not A: there is no compiler or flags (FireDucks ships as binary wheels only), library versions for the TPC-H run are unpinned, and a 141x gain with flags unstated triggers the &gt;50x cap. No independent or peer-reviewed source exists, so it is C.
- **Verifier notes:** The 141x/55x (FireDucks), 109x/61x (DuckDB) and 58x/50x (Polars) numbers and the m7i.8xlarge / Xeon Gold 6526Y setup all match the page. Tier drops from A to C: the page is first-party, no compiler or flags are possible for a binary-only product, versions are unpinned, and the &gt;50x cap applies. maintenance_status was changed to active because the last PyPI release (2025-12-02) is under 12 months old, even though the issue-tracker repo's last commit is 2025-05-22. The orchestrator may prefer to keep 'stale' by the strict last-commit rule.
- **Fields the verifier corrected:** `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://fireducks-dev.github.io/docs/benchmarks/>
  - <https://github.com/fireducks-dev/fireducks>
  - <https://github.com/fireducks-dev/polars-tpch/blob/fireducks_20250204/README.md>
  - <https://github.com/duckdblabs/db-benchmark>
  - <https://pypi.org/pypi/fireducks/json>
- **Sources the enricher read:**
  - <https://github.com/fireducks-dev/fireducks>
  - <https://github.com/fireducks-dev/fireducks/issues>
  - <https://github.com/fireducks-dev/fireducks/issues/81>
  - <https://github.com/fireducks-dev/fireducks/issues/80>
  - <https://github.com/fireducks-dev/fireducks/issues/73>
  - <https://github.com/fireducks-dev/fireducks/issues/72>
  - <https://github.com/fireducks-dev/fireducks/issues/69>
  - <https://github.com/fireducks-dev/fireducks/issues/58>
  - <https://github.com/fireducks-dev/fireducks/issues/53>
  - <https://github.com/fireducks-dev/fireducks/issues/49>
  - <https://github.com/fireducks-dev/fireducks/issues/48>
  - <https://github.com/fireducks-dev/fireducks/issues/41>
  - <https://github.com/fireducks-dev/fireducks/issues/38>
  - <https://github.com/fireducks-dev/fireducks/issues/22>
  - <https://github.com/fireducks-dev/fireducks/issues/19>
  - <https://github.com/fireducks-dev/fireducks/issues/17>
  - <https://github.com/fireducks-dev/fireducks/issues/75>
  - <https://fireducks-dev.github.io/docs/benchmarks/>
  - <https://fireducks-dev.github.io/docs/>
  - <https://fireducks-dev.github.io/sitemap.xml>
  - <https://fireducks-dev.github.io/en/sitemap.xml>
  - <https://fireducks-dev.github.io/docs/get-started/>
  - <https://fireducks-dev.github.io/docs/user-guide/01-intro/>
  - <https://fireducks-dev.github.io/docs/user-guide/02-exec-model/>
  - <https://fireducks-dev.github.io/docs/user-guide/03-acceleration/>
  - <https://fireducks-dev.github.io/docs/user-guide/04-compatibility/>
  - <https://fireducks-dev.github.io/docs/user-guide/tips/>
  - <https://fireducks-dev.github.io/docs/help/faq/>
  - <https://fireducks-dev.github.io/docs/release-note/>
  - <https://fireducks-dev.github.io/posts/20241206_update_polars-tpch/>
  - <https://fireducks-dev.github.io/posts/data_flow_optimization/>
  - <https://fireducks-dev.github.io/posts/cudf_vs_fireducks/>
  - <https://fireducks-dev.github.io/files/20251209_PyDataGlobal.pdf>
  - <https://pypi.org/pypi/fireducks/json>
  - <https://pypi.org/pypi/firefw/json>
  - <https://pypi.org/pypi/pandas/json>
  - <https://pypi.org/pypi/pyarrow/json>
  - <https://files.pythonhosted.org/packages/93/40/85594652eaab552635e62aefc5baebe267d0841182bd7a4b499340459814/fireducks-1.4.4-cp312-cp312-manylinux_2_28_x86_64.whl>
  - <https://github.com/fireducks-dev/polars-tpch/blob/fireducks_20250204/README.md>
  - <https://github.com/fireducks-dev/polars-tpch/blob/fireducks_20250204/run-fireducks.sh>
  - <https://github.com/fireducks-dev/polars-tpch/blob/fireducks_20250204/Makefile>
  - <https://github.com/fireducks-dev/polars-tpch/blob/fireducks_20250204/queries/fireducks/utils.py>
  - <https://github.com/fireducks-dev/polars-tpch/blob/fireducks_20250204/queries/fireducks/q1.py>
  - <https://github.com/fireducks-dev/polars-tpch/blob/fireducks_20250204/queries/fireducks/__main__.py>
  - <https://hn.algolia.com/api/v1/search?query=fireducks&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=fireducks&tags=comment>
  - <https://news.ycombinator.com/item?id=42204627>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/fireducks-dev/fireducks`) · [data/wave6/enrich/raw/github_com_fireducks_dev_fireducks.json](../../../data/wave6/enrich/raw/github_com_fireducks_dev_fireducks.json) (enrichment confidence 0.8)

</details>
