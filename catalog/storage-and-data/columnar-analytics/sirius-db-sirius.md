# Sirius

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> DuckDB extension that runs DuckDB's SQL plans on NVIDIA GPUs via libcudf; vendor TPC-H hot runs 2.7-5.7x faster than DuckDB.

| | |
|---|---|
| **Beats** | DuckDB |
| **Claimed result** | 5.5x faster at SF100 (1.71s vs 9.37s), 5.7x at SF300 (4.48s vs 25.72s), 5.2x at SF500 (8.14s vs 42.25s), 2.7x at SF1000 (31.79s vs 85.91s); also 2.1x-5.3x cheaper per run |
| **Workload** | TPC-H benchmark (22 queries) hot runs at scale factors SF100/300/500/1000 (100GB-1TB), Sirius (a GPU execution engine plugged into DuckDB via Substrait) vs plain DuckDB on CPU |
| **Metric** | throughput |
| **Hardware** | Sirius (GPU): best of AWS g7e.2xlarge/4xlarge/8xlarge per scale factor (which size won at each SF is not stated), NVIDIA RTX PRO 6000 96GB; DuckDB (CPU) v1.5.5: AWS Graviton5 m9g.16xlarge |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/sirius-db/sirius) · [benchmark](https://github.com/sirius-db/sirius/blob/main/docs/README.md) |

## Verdict

The README chart (first-party) gives TPC-H 22-query hot-run totals for Sirius on the best of AWS g7e.2xlarge/4xlarge/8xlarge (RTX PRO 6000 96 GB) against DuckDB v1.5.5 on a Graviton5 m9g.16xlarge: 1.71s vs 9.37s at SF100 (5.5x), 4.48s vs 25.72s at SF300, 8.14s vs 42.25s at SF500 and 31.79s vs 85.91s at SF1000 (2.7x), with 2.1-5.3x lower cost per run. The chart states no compiler flags, per-SF instance, config or pinning setup, and the comparison is across hardware; independent ClickBench data (March 2026, p5.4xlarge, legacy path) shows a 1.50s hot sum against DuckDB's 11.29s on c8g.metal-48xl, but a far slower cold run.

## Use it when

- Repeated (hot) analytical SQL, i.e. TPC-H-style multi-way joins plus group-by, over 100 GB-1 TB of Parquet or file-backed DuckDB, with the hot tables pinned in GPU or pinned-host memory
- You already run DuckDB and have a Linux box with an NVIDIA Turing-or-newer GPU. You want existing SQL to run faster without rewrites, and you accept that unsupported queries keep working on the CPU
- Cost per query matters more than raw box size: the vendor chart shows 2.1-5.3x lower cost per TPC-H run on AWS g7e (RTX PRO 6000) than DuckDB on a Graviton5 m9g.16xlarge
- Data sits on local NVMe that supports O_DIRECT, so the io_uring scan path and prefetch cache can feed the GPU
- GPU query-processing research: operators can be swapped between libcudf and hand-written CUDA kernels, and DuckDB serves as a built-in CPU baseline

## Skip it when

- Cold or one-shot queries. Data still reaches the GPU through a CPU-mediated scan. In ClickBench (March 2026, legacy path, p5.4xlarge) Sirius's cold-run sum was 977.9s against DuckDB's 161.5s on c8g.metal-48xl, even though its hot-run sum was 1.50s against 11.29s. CUDA/cuDF startup can take minutes, and the first NVRTC JIT pass cost about 19s on the SF1000 run
- Queries built around window functions, ASOF JOIN, nested types (STRUCT/variable LIST), HUGEINT/128-bit types, BIGINT SUM or BIGINT arithmetic (no INT128 accumulator). These fall back and run at plain DuckDB CPU speed
- In-memory DuckDB databases (`:memory:` tables): the native scan requires a single-file block manager, so these queries fall back to the CPU
- Correctness-critical production use without your own GPU-vs-CPU validation. Wrong-result bugs are open: #1452 (pinned table + ORDER BY over a decimal expression races and silently duplicates and drops rows), #1312 (prefetch cache + multiple GPUs returns wrong sums) and #1123 (latent join-filter pushdown below LIMIT/TOP_N inherited from the pinned DuckDB)
- No NVIDIA GPU, or macOS/Windows, or containers that block the io_uring syscalls. The advantage also shrinks as data outgrows GPU memory (5.5x at SF100 down to 2.7x at SF1000 in the vendor chart), and the tuned SF1000 repro used 251.7 of 256 GB of GPU memory plus about 470 GB of host RAM

## How it is fast

It runs columnar operators on the GPU at HBM bandwidth using libcudf primitives: cuDF hash join and groupby, sort, and cuDF AST or NVRTC-JIT expression evaluation (`cudf::compute_column_jit`). The current "Super Sirius" engine is task-based and pipelined. It uses cuCascade tiered memory (GPU, then pinned host, then disk), adaptive hash partitioning, spilling and a 3-phase sample/partition/merge sort, so inputs can be larger than GPU memory. Scans get less data through dynamic filters built on the hash-join build side (Bloom, cuco IN-list set, zone maps), Parquet row-group pruning, io_uring O_DIRECT reads with a prefetch cache, and optional Simpatico-compressed pinned tables (for example delta-&gt;bitpack) that skip file I/O and decode on hot runs.

## Compared with alternatives

Pick Sirius over cuDF (cudf.pandas) when the workload is SQL over DuckDB tables or Parquet, with large joins that may exceed GPU memory, rather than pandas code. Pick it over the CPU engines (Umbra, chDB, Velox-based Prestissimo) only when you have an NVIDIA GPU and repeated hot queries on pinned data; for cold scans, or with no GPU, those CPU engines are the safer choice.

## Integration

| | |
|---|---|
| **Form** | shared lib (loadable, unsigned `sirius.duckdb_extension`, or statically built into a bundled `duckdb` binary); source build only, with no tagged releases or prebuilt binaries |
| **Dependencies** | libcudf 26.08.01 (RAPIDS), RMM, NVIDIA cuCascade, CUDA toolkit + NVRTC, a patched DuckDB 1.5.5 fork (sirius-db/duckdb v1.5.5-patches), liburing, yaml-cpp, abseil, spdlog 1.8, CRoaring, protobuf and a Rust toolchain, all managed through Pixi |
| **Minimum toolchain** | C++20 / CUDA C++20, CMake &gt;= 3.30.4 (Pixi pins 4.x), conda GCC or Clang 21; CUDA 12.x (driver &gt;= 525.60.13) or CUDA 13.x (driver &gt;= 580.65.06) |
| **Platforms** | Linux x86-64 or aarch64 with glibc &gt;= 2.28; NVIDIA GPU of compute capability 7.5+ (Turing or newer); io_uring enabled at runtime; no macOS/Windows engine build |
| **Thread safety** | Each DuckDB connection gets a SiriusContext that owns the engine's thread pools and memory tiers. The vendor ran a 7-stream TPC-H throughput test, but the project lists multi-query GPU memory isolation and admission control as open problems. Guarantees are otherwise not documented. |
| **Drop-in for the baseline** | partial — after LOAD you use the same DuckDB SQL, CLI and Python API with no query rewrites. However, it needs a Sirius-built DuckDB 1.5.5 (patched fork, unsigned extension), and unsupported operators or types silently run on DuckDB's CPU engine |

## Gotchas

- Fallback is silent by default. Set `enable_duckdb_fallback = false` to surface errors. The scan docs say a runtime (not plan-time) fallback can poison the connection so that the next GPU query on it deadlocks, and S3 scans have no CPU fallback at all.
- Hot-run speed depends on `pin_table`, because Sirius otherwise re-reads storage on every query. Pinned DuckDB tables reject UPDATE, MERGE ... UPDATE and ON CONFLICT DO UPDATE, and an explicit CHECKPOINT invalidates the pin until you re-pin.
- Defaults take 95% of GPU memory plus 8 GiB of pinned host memory per NUMA node, and use the interpreted AST expression evaluator. The SF1000 repro found `SET expression_evaluator_strategy = 'ast_jit'` 4.17% faster, but it is not the default. A pre-optimizer hook also disables some DuckDB optimizers (IN_CLAUSE, COMPRESSED_MATERIALIZATION, LATE_MATERIALIZATION), and plans still come from DuckDB's CPU cost model.
- The README and the CIDR'26 paper describe integration through Substrait, but the current DuckDB path consumes DuckDB's logical plan through optimizer hooks (the Substrait include is commented out in sirius_extension.cpp). The ClickBench entry was run with the legacy in-memory `gpu_processing` path, which is no longer built by default.

## Known shortcomings

- Vendor charts compare an RTX PRO 6000 GPU with Graviton5 CPUs (hardware asymmetry; the cost figures 2.1-5.3x cheaper are the vendor's).
- Cold runs lose badly (ClickBench cold sum 977.9 s vs DuckDB 161.5 s; hot 1.50 vs 11.29 s): CUDA/cuDF init takes minutes and the first JIT pass \~19 s; hot speed needs a manual pin_table. Silent CPU fallback for window, ASOF, nested types, HUGEINT, BIGINT SUM/arithmetic and :memory: tables; a runtime fallback can deadlock the next GPU query; S3 scans have no fallback. Open wrong-result bugs (#1452 duplicate/dropped rows with pin + ORDER BY decimal; #1312 prefetch + multi-GPU; #1123). No releases; source build only against pinned libcudf 26.08.01 and a patched DuckDB 1.5.5 fork; Linux, NVIDIA Turing+ and io_uring only. Docs describe a Substrait path the code no longer uses; the ClickBench entry used a legacy mode no longer built by default. Speedup shrinks with scale (5.5x at SF100 to 2.7x at SF1000).

## Caveats and trade-offs

First-party benchmark read from a README chart PNG (docs/super-sirius-perf.png); there is no raw results table, and no compiler/build flags are stated. These are hot runs only, and the Sirius time is the best of three g7e instance sizes. The hardware is asymmetric: an RTX PRO 6000 96GB GPU instance against a Graviton5 m9g.16xlarge CPU instance. The chart partly normalizes for this by reporting cost per run (Sirius 2.1-5.3x cheaper). The speedup shrinks from 5.5x at SF100 to 2.7x at SF1000. The page gives no reason, so the earlier explanation (GPU memory/bandwidth bottleneck) is speculation.

Requires an NVIDIA GPU (Turing+, CUDA 12.x/13.x) and Linux with io_uring enabled; plugs into DuckDB via Substrait and falls back silently to CPU for unsupported operators; only DuckDB is a supported target today (StarRocks integration planned)

## Maintenance

Actively developed by NVIDIA, UW-Madison and about 40 contributors (last commit 2026-09-24, \~150 open issues) under Apache-2.0, but it has no releases (CMake version 0.0.0), so expect to build from source with Pixi against pinned libcudf 26.08.01 and a patched DuckDB 1.5.5, and to track fast-moving internals.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README performance chart (docs/super-sirius-perf.png) is first-party and shows every cited time, speedup and cost ratio for Sirius against DuckDB v1.5.5 on TPC-H SF100-SF1000. The TPC-H harness is public (test/tpch_performance/), but no compiler or flags are stated and the per-SF instance and run configuration are not given, so not A. There is no paper or independent suite behind these TPC-H numbers, so C.
- **Verifier notes:** Every number in the record matches the chart. I changed last_commit from pushed_at to the default-branch commit date and removed the unsupported bottleneck explanation. The independent ClickBench suite also has Sirius entries: sirius/results/20260309/p5.4xlarge.json has a hot-run sum of 1.50s, against DuckDB at 11.29s (c8g.metal-48xl) and 17.32s (c6a.metal) in the 2026-05-11 runs. That comparison is cross-hardware (GPU vs CPU) and across dates, all derived; re-pointed to it, the record could support tier B.
- **Fields the verifier corrected:** `benchmark_url`, `last_commit`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/sirius-db/sirius>
  - <https://github.com/sirius-db/sirius/blob/main/docs/README.md>
  - <https://raw.githubusercontent.com/sirius-db/sirius/main/docs/super-sirius-perf.png>
  - <https://github.com/sirius-db/sirius/blob/main/docs/sirius-for-research.md>
  - <https://github.com/sirius-db/sirius/tree/main/test/tpch_performance>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/sirius/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/sirius/results/20260309/p5.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/sirius/results/20260309/lambda-GH200.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c8g.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c6a.metal.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c7a.metal-48xl.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c6a.4xlarge.json>
- **Sources the enricher read:**
  - <https://github.com/sirius-db/sirius>
  - <https://github.com/sirius-db/sirius/blob/main/docs/README.md>
  - <https://raw.githubusercontent.com/sirius-db/sirius/main/docs/super-sirius-perf.png>
  - <https://github.com/sirius-db/sirius/blob/main/docs/gpu_execution.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/gpu_processing.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/UPDATING.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/DEVELOPMENT.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/sirius-for-research.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/super-sirius/README.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/super-sirius/architecture-overview.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/super-sirius/optimizations.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/super-sirius/operators.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/super-sirius/memory-management.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/super-sirius/configuration.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/super-sirius/scan.md>
  - <https://github.com/sirius-db/sirius/blob/main/docs/super-sirius/multi-gpu-architecture.md>
  - <https://github.com/sirius-db/sirius/blob/main/bench/sf1000-repro/README.md>
  - <https://github.com/sirius-db/sirius/blob/main/CMakeLists.txt>
  - <https://github.com/sirius-db/sirius/blob/main/pixi.toml>
  - <https://github.com/sirius-db/sirius/blob/main/cmake/sirius-targets.cmake>
  - <https://github.com/sirius-db/sirius/blob/main/cmake/sirius-dependencies.cmake>
  - <https://github.com/sirius-db/sirius/blob/main/.gitmodules>
  - <https://github.com/sirius-db/sirius/blob/main/src/sirius_extension.cpp>
  - <https://github.com/sirius-db/sirius/commits/main>
  - <https://github.com/sirius-db/sirius/releases>
  - <https://github.com/sirius-db/sirius/issues?q=is%3Aopen+label%3Abug>
  - <https://github.com/sirius-db/sirius/issues/1452>
  - <https://github.com/sirius-db/sirius/issues/1312>
  - <https://github.com/sirius-db/sirius/issues/1123>
  - <https://arxiv.org/abs/2508.04701>
  - <https://arxiv.org/pdf/2508.04701v3>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/sirius/README.md>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/sirius/benchmark.sh>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/sirius/install>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/sirius/load>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/sirius/query>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/sirius/server.py>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/sirius/results/20260309/p5.4xlarge.json>
  - <https://raw.githubusercontent.com/ClickHouse/ClickBench/main/duckdb/results/20260511/c8g.metal-48xl.json>
  - <https://news.ycombinator.com/item?id=44404876>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/sirius-db/sirius`) · [data/wave6/enrich/raw/github_com_sirius_db_sirius.json](../../../data/wave6/enrich/raw/github_com_sirius_db_sirius.json) (enrichment confidence 0.75)

</details>
