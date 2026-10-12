# EvoTrees.jl (Julia gradient-boosted trees) vs XGBoost hist (C++, CPU and GPU)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Julia` · `Apache-2.0` · 🟢 active

> Pure-Julia histogram gradient-boosted trees (CPU and GPU); edges out XGBoost hist only in narrow table rows.

| | |
|---|---|
| **Beats** | XGBoost v3.1.2 (C++/CUDA, 'hist' algorithm) driven from Julia through XGBoost.jl |
| **Claimed result** | No headline claim; README tables only. CPU training is faster only at 10M rows x 10 features (26.45 s vs 30.99 s at depth 6, 51.88 s vs 55.20 s at depth 11; 1.17x and 1.06x derived from page data), equal at 100k x 100 depth 6 (0.79 s both), and slower elsewhere (for example 192.58 s vs 111.69 s at 10M x 100 depth 11, 0.36 s vs 0.21 s at 100k x 10 depth 6); CPU inference is slower in every row. GPU: EvoTrees trains faster at depth 11 with 100 features (2.17 s vs 2.92 s at 100k, 5.07 s vs 6.80 s at 1M, 37.25 s vs 41.98 s at 10M) and infers faster in those rows (0.32 s vs 0.58 s at 1M, 3.57 s vs 5.91 s at 10M); GPU is slower at depth 6 and with 10 features. |
| **Workload** | Regression boosted trees (mse loss, mae eval metric on the training set each round) on uniformly random data, 200 rounds, nobs 100k/1M/10M, nfeats 10/100, EvoTrees max_depth 6/11 (XGBoost run with max_depth - 1, i.e. 5/10), 64 bins, eta 0.05, row and column subsample 0.5; training and inference wall time from a single @elapsed run per cell on CPU (12 threads) and GPU. The script generates Float32 data (T = Float32) although the README says Matrix{Float64}. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5900X (12 threads) and NVIDIA RTX A4000 |
| **Compiler and flags** | Julia 1.10.8; README header says EvoTrees v0.18.3 and XGBoost v3.1.2 (hist on CPU, tree_method 'gpu_hist' on GPU per the last public harness); XGBoost is the prebuilt binary from the Julia package (build flags not stated). The XGBoost harness lived in benchmarks/regressor.jl up to commit 6edfadb (2026-08-18; behind a run_xgb switch committed as false) and was removed in c038532 (2026-08-21); the current script times EvoTrees only. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 201 stars; Julia General registry package |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/Evovest/EvoTrees.jl) · [benchmark](https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/README.md) |

## Verdict

On a Ryzen 5900X (12 Julia threads) and an RTX A4000 with Julia 1.10.8, against XGBoost 3.1.2 hist/gpu_hist called through XGBoost.jl (prebuilt binary), 200 rounds of mse regression on uniform random Float32 data (64 bins, eta 0.05, row and column subsample 0.5, train-set MAE evaluated each round, one timed run per cell): CPU training is faster only at 10M x 10 (26.45 vs 30.99 s and 51.88 vs 55.20 s), GPU training only in the deep 100-feature rows (2.17 vs 2.92 s, 5.07 vs 6.80 s, 37.25 vs 41.98 s), and EvoTrees is slower in every other training row and every CPU inference row. In the October 2025 table (EvoTrees 0.17.1 vs XGBoost 2.5.1) EvoTrees CPU training was up to 3.2x faster (25.31 vs 80.07 s at 10M x 10 depth 6); XGBoost 3.x erased most of that gap.

## Use it when

- A Julia codebase or MLJ pipeline that wants GBDT without shipping a C++ library, with performance in the same range as XGBoost hist.
- Distributional or multi-target regression: :gaussian_mle and :logistic_mle (Fisher-information Newton steps) and joint multi-target fits with one tree structure, which XGBoost does not offer in the same form.
- GPU training of deep trees on wide data: in the README GPU table (RTX A4000) at depth 10 in XGBoost terms with 100 features, training is 1.13-1.35x faster than XGBoost gpu_hist from 100k to 10M rows.
- Very tall, narrow CPU data (about 10M rows x 10 features), where CPU training roughly matches or slightly beats XGBoost (1.06-1.17x in the latest table).
- AMD (ROCm) or Apple (Metal) GPUs through the v0.20 KernelAbstractions extensions.

## Skip it when

- CPU inference throughput: slower than XGBoost in every README CPU row, about 2.5-2.7x slower in the 100-feature depth-6 rows (for example 6.44 s vs 2.56 s at 10M x 100).
- CPU training with many features or deep trees: 192.58 s vs 111.69 s at 10M x 100 depth 11 (1.72x slower) and 0.36 s vs 0.21 s at 100k x 10 depth 6.
- Shallow trees or few features on GPU: XGBoost trains about 2x faster (1.37 s vs 0.58 s at 1M x 10 depth 6; 7.53 s vs 3.83 s at 10M x 10 depth 6).
- Categorical features scored in small batches, or early stopping, until open issues #368 and #356 are fixed (see gotchas).
- Interop with Python/R/C++ model tooling: models are saved as BSON for Julia only, and the layout changed in v0.20 (a loader shim reads pre-v0.20 files).

## How it is fast

Features are quantile-binned once into an observation-major UInt8 matrix (edges from a 1000\*nbins-row sample, at most 255 bins), and trees grow level-wise from gradient histograms. Histograms are built only for one child per split and the sibling is derived by the subtraction trick (h[child] = h[parent] - h[sibling]); the build threads over node x feature tiles with software prefetch through llvm.prefetch and a loop unrolled per loss width via Val(NK), which Julia's JIT specializes per objective. GPU training (v0.18+) uses KernelAbstractions kernels with Atomix atomics, so the same code targets CUDA, ROCm and Metal.

## Compared with alternatives

The other Julia library entries in this category (NonuniformFFTs.jl vs FINUFFT, Ripserer.jl vs Ripser, NativeMinuit.jl vs Minuit2) show clearer wins over their C++ incumbents; pick EvoTrees for Julia-native GBDT with MLE or multi-target losses or non-CUDA GPUs, and keep XGBoost (catalogued in wave 8) when raw CPU training or inference speed is the goal.

## Integration

| | |
|---|---|
| **Form** | module (Julia package in the General registry) |
| **Dependencies** | BSON, CategoricalArrays, Distributions, MLJModelInterface, StatsBase, Tables; optional weak deps CUDA (5 - 6.3), AMDGPU, Metal, KernelAbstractions + Atomix for GPU, Makie for plots |
| **Minimum toolchain** | Julia 1.9 (Project.toml compat); README benchmarks on Julia 1.10.8 |
| **Platforms** | any Julia CPU platform; GPU on NVIDIA CUDA, AMD ROCm and Apple Metal via package extensions (v0.20) |
| **Thread safety** | training is multithreaded with Base.Threads (@threads over nodes and feature tiles), so start Julia with -t N; concurrent fits on shared objects are not documented |
| **Drop-in for the baseline** | false: different API and parameter names (eta, nbins, rowsample, colsample, max_depth), Julia-only BSON model files, no XGBoost model import |

## Gotchas

- Harness flaw behind the table: the CPU and GPU tables come from different runs. The GPU table has been unchanged since 97840b9 (2025-12-24, EvoTrees 0.18.3), while the CPU table was re-measured in db96e75 (2026-09-04, package 0.20.0) under the stale 'EvoTrees v0.18.3' header, after the XGBoost harness had been removed from benchmarks/regressor.jl (c038532, 2026-08-21). Between the two CPU tables, with the same declared XGBoost 3.1.2 and machine, the XGBoost column moved by up to 55% (2.37 s to 3.67 s at 100k x 100 depth 11; 10.08 s to 13.40 s at 1M x 100 depth 11) while EvoTrees moved at most about 3%. Each cell is a single @elapsed with warm-up only for the first configuration, so the 1.06-1.17x CPU wins sit inside the baseline's run-to-run drift.
- max_depth changed meaning in v0.20.0 (NEWS: now the number of splits on a leaf path, as in XGBoost). The README rows still say 6/11, the pre-v0.20 convention under which XGBoost was given max_depth - 1 = 5/10, while the current script uses 5/10; v0.20 users who set max_depth=6 get trees one level deeper than the table measured.
- Open issue #368 (PR #379 pending): at predict time categorical columns are re-encoded against the scoring batch's own level pool instead of the training levels, so single-row or partial-batch scoring returns silently wrong predictions (every category maps to the first training level when scored alone); the workaround is to pass the full training levels on the scoring column.
- Other open correctness reports: #356 early stopping records best_iter but the returned model keeps every later tree (use ntree_limit); #350 table columns typed Union{Missing,Float64} are silently dropped when feature_names is not given; #393 bin edges ignore w_train; #374 offset_name corrupts the scale parameter for EvoTreeGaussian/EvoTreeMLE.

## Known shortcomings

- Mostly slower than XGBoost: wins only at 10M x 10 on CPU (1.06-1.17x) and depth 11 x 100 on GPU (1.13-1.35x); the XGBoost harness was removed from regressor.jl on 2026-08-21 but the CPU table was re-run 2026-09-04 under a stale v0.18.3 label; script data is Float32 while the README says Float64.
- Cross-run tables: the CPU table is a September 2026 v0.20.0 run (db96e75) under a stale v0.18.3 header, after the XGBoost harness had been removed from benchmarks/regressor.jl (c038532, 2026-08-21); the GPU table dates from December 2025. The XGBoost CPU column moved up to 55% between runs with the same declared v3.1.2 while EvoTrees moved at most 3%, so the 1.06-1.17x CPU wins sit inside the baseline's run-to-run drift; one @elapsed per cell. v0.20 changed the meaning of max_depth while the rows still say 6/11. Open bugs #368 (categorical predict silently wrong), #356, #350, #393, #374. The October 2025 table (XGBoost 2.5.1) had EvoTrees up to 3.2x faster; XGBoost 3.x erased most of that gap.

## Caveats and trade-offs

The README does not claim to beat XGBoost; the wins are read off its own tables and are regime-specific (CPU only at 10M rows x 10 features, 1.06-1.17x; GPU only at depth 11 with 100 features, 1.13-1.35x training). EvoTrees is slower in most rows, and CPU inference is slower in every row. The CPU table was re-measured in commit db96e75 (2026-09-04, 'Jdb/v20', package now v0.20.0) while the version header still says EvoTrees v0.18.3, and the XGBoost harness had already been removed from the public script on 2026-08-21, so the current CPU XGBoost column cannot be reproduced from the repository; the GPU table dates from 97840b9 (2025-12-24). The script generates Float32 data while the README says Float64. Models are trained on random data; model quality or equal tree structure is not compared, and the two libraries bin features differently. Each cell is one @elapsed run with a warm-up only for the first configuration; no variance reported. One machine. [retier] Cross-run tables: the CPU table is a September 2026 v0.20.0 run (db96e75) under a stale v0.18.3 header, made after the XGBoost harness had been removed from benchmarks/regressor.jl (c038532, 2026-08-21); the GPU table dates from December 2025. The XGBoost CPU column moved up to 55% between runs with the same declared v3.1.2 while EvoTrees moved at most 3%, so the 1.06-1.17x CPU wins sit inside the baseline's drift; one @elapsed per cell. v0.20 changed the meaning of max_depth while the rows still say 6/11. Open bugs #368 (categorical predict silently wrong), #356, #350, #393, #374.

Slower than XGBoost in most CPU rows and all CPU inference rows; supports multi-target and maximum-likelihood objectives natively in Julia.

## Maintenance

Actively maintained (v0.20.0, last commit 2026-10-09, 19 open issues and 10 open PRs including several fresh correctness reports), Apache-2.0 and installable from the Julia General registry; choose it for Julia integration and its loss functions, not for speed over XGBoost.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** README Performance tables compare EvoTrees with XGBoost hist on CPU (Ryzen 5900X) and GPU (RTX A4000) with Julia 1.10.8 and package versions, but XGBoost is a prebuilt binary with unstated build flags and the current benchmarks/regressor.jl no longer contains the XGBoost harness, so the comparison is not reproducible from the public code; first-party numbers, C.
- **Retiered** C to D: Enricher: the CPU table's XGBoost column was not re-measured with the EvoTrees column (the XGBoost harness was removed from benchmarks/regressor.jl before the September 2026 re-run) and moved up to 55% between runs, so the 1.06-1.17x CPU wins are cross-run and within the baseline's drift; the GPU table is a different run. Cross-run precedent: C to D.
- **Verifier notes:** Confirm C. Numbers in claimed_speedup match the current README exactly. Key shortcomings: mostly slower than XGBoost, narrow wins only; the public script no longer runs XGBoost (removed 2026-08-21) although the CPU table with XGBoost columns was updated 2026-09-04 under a stale v0.18.3 label; Float32 data vs README's Float64. same_algorithm left null: same histogram-GBDT family with matched hyperparameters, but separate implementations and no equal-model check. Baseline XGBoost is already listed (wave 8, https://github.com/dmlc/xgboost). Metadata (Apache-2.0, 201 stars, last commit 2026-10-09) checked and correct.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-74 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/README.md>
  - <https://github.com/Evovest/EvoTrees.jl>
  - <https://github.com/Evovest/EvoTrees.jl/commits/main>
  - <https://github.com/Evovest/EvoTrees.jl/commits/main/README.md>
  - <https://github.com/Evovest/EvoTrees.jl/commits/main/benchmarks/regressor.jl>
  - <https://github.com/Evovest/EvoTrees.jl/tree/main/benchmarks>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/benchmarks/regressor.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/97840b9/benchmarks/regressor.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/bece6ac/benchmarks/regressor.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/c038532/benchmarks/regressor.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/6edfadb/benchmarks/regressor.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/97840b9/README.md>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/d1ffd16/README.md>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/db96e75/README.md>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/Project.toml>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/benchmarks/regressor-df.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/benchmarks/regressor-mlj.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/benchmarks/regressor-grps.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/benchmarks/Project.toml>
- **Sources the enricher read:**
  - <https://github.com/Evovest/EvoTrees.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/README.md>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/Project.toml>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/NEWS.md>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/benchmarks/regressor.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/benchmarks/Project.toml>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/src/EvoTrees.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/src/learners.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/src/fit.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/src/fit-utils.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/src/split.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/src/init.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/main/src/structs.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/6edfadb/benchmarks/regressor.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/97840b9/benchmarks/regressor.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/c038532/benchmarks/regressor.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/db96e75/benchmarks/regressor.jl>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/97840b9/README.md>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/d1ffd16/README.md>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/db96e75/README.md>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/97840b9/Project.toml>
  - <https://raw.githubusercontent.com/Evovest/EvoTrees.jl/db96e75/Project.toml>
  - <https://github.com/Evovest/EvoTrees.jl/commits/main/README.md>
  - <https://github.com/Evovest/EvoTrees.jl/issues?q=is%3Aissue>
  - <https://github.com/Evovest/EvoTrees.jl/issues/368>
  - <https://github.com/Evovest/EvoTrees.jl/issues/356>
  - <https://github.com/Evovest/EvoTrees.jl/issues/350>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/evovest/evotrees.jl`) · [data/wave14/enrich/raw/github_com_evovest_evotrees_jl.json](../../../data/wave14/enrich/raw/github_com_evovest_evotrees_jl.json) (enrichment confidence 0.75)

</details>
