# XGBoost

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Multithreaded gradient-boosted-tree library; trained 3-9x faster than R gbm and 120-375x faster than 2015 scikit-learn GBM.

| | |
|---|---|
| **Beats** | scikit-learn GradientBoostingClassifier 0.15.2 and R gbm package (gradient-boosted trees training) |
| **Claimed result** | Time in seconds, xgboost vs R gbm: 10K A 6 vs 20, B 1 vs 3; 100K A 40 vs 200, B 4 vs 30; 1M A 400 vs 3000 (7.5x, derived from page data), B 45 vs 400 (8.9x, derived from page data); R gbm has no 10M run in A, 10M B 5000 vs xgboost 1000. xgboost vs scikit-learn: 10K A 6 vs 1100 (about 183x, derived from page data), B 1 vs 120; 100K B 4 vs 1500 (375x, derived from page data); scikit-learn has no larger runs. AUC similar (e.g. 10K A 70.3 xgboost vs 69.9 scikit-learn vs 64.9 R; 1M A 76.9 xgboost vs 74.1 R). |
| **Workload** | Training time of gradient-boosted trees for binary classification (flight-delay prediction from the airline dataset, 10K to 10M rows, mostly categorical features, AUC measured on a 100K test set). Experiment A: 1000 trees, depth 16, learn rate 0.01, subsample 0.5. Experiment B: 300 trees, depth 6, learn rate 0.1. |
| **Metric** | other |
| **Hardware** | Amazon EC2 c3.8xlarge (32 cores, 60 GB RAM); r3.8xlarge (32 cores, 250 GB RAM) for some larger runs. Ubuntu 14.04, R 3.2.0, scikit-learn 0.15.2, xgboost 0.4-0 (github snapshot 2015-05-16). CPU model and xgboost build flags not stated. |
| **Compiler and flags** | Not stated. Per 0-init/1-install.md, xgboost's R-package was built from GitHub source with devtools::install_github on Ubuntu 14.04 (R's default compiler flags); scikit-learn came from Anaconda 2.2.0 and gbm from CRAN. |
| **Adoption** | 28.8k stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/dmlc/xgboost) · [benchmark](https://github.com/szilard/benchm-ml) |

## Verdict

In szilard/benchm-ml (2015, independent; EC2 c3.8xlarge, 32 cores, Ubuntu 14.04, R 3.2.0, XGBoost R package built from the 2015-05-16 GitHub snapshot with R's default flags, CPU model not stated), XGBoost with nthread = detectCores() trained 1000 depth-16 trees on 1M airline rows in 400 s vs 3000 s for single-threaded R gbm and 10K rows in 6 s vs 1100 s for single-threaded scikit-learn 0.15.2 on dense one-hot input; gbm's trees were capped at 16 splits rather than depth 16, so the models were not equivalent.

## Use it when

- Tabular classification or regression with 100K to 10M rows on a multicore CPU: szilard/GBM-perf (r4.8xlarge, software as of 2024-06-04, 100 trees, depth 10) trains the airline data in 0.4 s at 100K and 2.7 s at 1M rows, ahead of LightGBM (2.3 s, 4.0 s), CatBoost (1.9 s, 7.0 s) and H2O (11 s, 12 s).
- GPU training: the same suite on one V100 trains 10M rows in 5 s vs LightGBM 40 s and CatBoost 23 s, and 100M rows in 80 s with 6 GB of GPU memory and no extra host RAM.
- Sparse or one-hot inputs with missing values, where the sparsity-aware split finding skips absent entries instead of scanning dense zero columns.
- Python code built around scikit-learn estimators that needs a faster boosted-tree model with the same fit/predict_proba interface (XGBClassifier), or C/C++, JVM or R services that need one model format across languages.

## Skip it when

- Very large CPU training jobs: GBM-perf has LightGBM about 2x faster at 10M rows (20 s vs 40 s) and about 3.5x faster at 100M rows on a c7i.metal-48xl (55 s vs 190 s); on m5.12xlarge at 100M rows XGBoost also used 15 GB of training RAM vs 5 GB for LightGBM.
- Hosts with two sockets or hyperthreading and default thread counts: GBM-perf measured XGBoost 1M-row training at 120 s on 64 threads (2 sockets plus HT) vs 12 s on 16 physical cores in May 2019; fixes by September 2020 brought both to about 5 s, but the author still advises pinning to the physical cores of one socket.
- tree_method='exact', the algorithm behind the 2015 numbers: the project's own docs call it computationally slower than approx and hist and it does not support distributed training or external memory.
- Accuracy at fixed settings on categorical-heavy data: in GBM-perf's one-configuration runs XGBoost reached AUC 0.749 at 1M rows vs 0.765 for LightGBM and 0.762 for H2O, so tune before assuming the fastest tool is also the best model.
- Minimal-dependency installs: the default Linux PyPI wheel (3.4.1) pulls nvidia-nccl-cu13; use the separate xgboost-cpu wheel for CPU-only machines.

## How it is fast

The 2015 snapshot that was benchmarked predates the tree_method option (v0.6, 2016) and the hist method (v0.7, 2017-12-30), so it ran the exact greedy column-wise updater: data is pre-sorted into compressed sparse column pages, OpenMP threads enumerate split candidates per feature in parallel (UpdateSolution in updater_colmaker.cc) for all nodes of one depth in a single scan, and only non-missing entries are stored, with a learned default direction for missing values, so one-hot dummy columns cost time proportional to their non-zeros. Since 2.0 the default is hist: features are quantile-binned once and per-node gradient histograms are built row-wise with software prefetching (RowsWiseBuildHistKernel in common/hist_util.cc), the LightGBM-style approach; a CUDA hist path covers GPUs.

## Compared with alternatives

Against CatBoost, the only other boosted-tree entry, pick XGBoost when training time matters: GBM-perf has it 2.6-4.8x faster on CPU at 100K to 1M rows and 4.6x faster on a V100 at 10M rows; pick CatBoost when batch CPU scoring of large ensembles dominates. The neural-network siblings (PyTorch, MXNet, oneDNN-based runtimes) do not train tree ensembles.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | OpenMP and the vendored dmlc-core submodule for the C++ library; optional CUDA, NCCL, RMM and a SYCL plugin; the Python package needs numpy and scipy (plus nvidia-nccl-cu13 on Linux for the default wheel; xgboost-cpu omits it) |
| **Minimum toolchain** | C++17; CMake 3.18+; GCC 8.1+, Clang 9+, AppleClang 11+ or Visual Studio 2019+ (checked in CMakeLists.txt); Python 3.12+ for the 3.4.1 wheels |
| **Platforms** | Linux, macOS and Windows on x86-64 and aarch64 (PyPI wheels for manylinux x86-64/aarch64 and macOS x86-64/arm64); NVIDIA GPUs through CUDA; distributed via Dask, Spark, Kubernetes |
| **Thread safety** | Since 1.4, all prediction functions (predict, inplace_predict, SHAP) are thread-safe for gbtree and dart boosters; training and prediction on the same model concurrently, or calling set_params inside a predict function, is undefined behaviour (doc/prediction.rst) |
| **Drop-in for the baseline** | partial — XGBClassifier follows the scikit-learn estimator API and can replace GradientBoostingClassifier in a pipeline, but hyperparameter semantics and defaults differ; there is no drop-in replacement for R gbm calls |

## Gotchas

- Harness flaw in the R gbm comparison: gbm's interaction.depth is a split count, not a depth. Its tree.cpp grow loop performs one best-first split per iteration for cMaxDepth iterations, so interaction.depth = 16 in 1-gbm.R builds trees with 16 splits (17 non-empty leaves), while xgboost max_depth = 16 in 6-xgboost.R allows depth-16 trees with thousands of leaves (min_child_weight = 1). The 'matched' hyperparameters therefore gave R gbm much smaller trees; XGBoost was faster despite doing more work per tree, but the AUC gap (e.g. 64.9 vs 70.3 at 10K) partly reflects model size, and the time ratio is not a like-for-like per-model comparison.
- The scikit-learn ratios (183x, 375x) do not include the encoding step: 2-boost.py times pd.get_dummies in a separate %time cell and %time md.fit only on the resulting dense frame of about 1K dummy columns. What they measure is single-threaded exact splitting over dense mostly-zero columns (scikit-learn 0.15.2) against XGBoost's 32-thread sparse column scan; the README says scikit-learn is only 1.5x slower than R with integer encoding.
- In the same benchm-ml table XGBoost is not the fastest at 10M rows: H2O trained experiment A in 3500 s vs XGBoost 9000 s and experiment B in 300 s vs 1000 s (2.6x and 3.3x in H2O's favour, derived from page data), although XGBoost still led at 1M (400 s vs 900 s in A, 45 s vs 60 s in B). The multi-x headline holds only against the single-threaded R and Python baselines.
- Defaults changed under users: 2.0 made hist the default tree method (earlier versions chose exact or approx depending on input and environment), so models and timings differ across versions; issue #9013 (closed) reported 80-90 s per iteration with QuantileDMatrix in 1.7.4 vs 4-5 s with DMatrix in 1.4.2 after the automatic switch.

## Known shortcomings

- szilard/benchm-ml (EC2 c3.8xlarge, 2015 versions): 32 threads against single-threaded R gbm and scikit-learn 0.15.2, scikit-learn timed on dense one-hot input (the README says it is only 1.5x slower than R with integer encoding, so the 183x/375x mostly measures encoding); off-category baselines; the KDD paper is blocked (snippet says over 10x vs scikit-learn).
- Harness flaw in szilard/benchm-ml: R gbm's interaction.depth=16 counts splits, not depth (gbm tree.cpp grows one split per iteration), so gbm built 16-split trees against xgboost depth-16 trees; the models are not equivalent. The scikit-learn ratios exclude encoding (timed separately) and compare a dense one-hot exact split on 1 thread against a sparse scan on 32 threads. In the same table H2O is faster than xgboost at 10M rows (3500 vs 9000 s on A, 300 vs 1000 s on B). The measured version used the exact updater (hist arrived in v0.7).

## Caveats and trade-offs

Independent third-party suite (szilard/benchm-ml, scripts 3-boosting/1-gbm.R, 2-boost.py, 6-xgboost.R) but the comparison is not like for like. Threads: xgboost used nthread = detectCores() (32 cores) while the README calls R gbm 'a single-threaded implementation', and scikit-learn's GradientBoostingClassifier is also single-threaded, so most of the 5-9x gap over R gbm is core count. Encoding: the scikit-learn script one-hot encodes the categoricals into a dense pandas frame (pd.get_dummies), and the README itself says 'Python is very slow with one-hot encoding of categoricals, but almost as fast as R (just 1.5x slower) with simple/integer encoding', so the 183x and 375x ratios against scikit-learn mostly measure that dense encoding, not the boosting code; xgboost received a sparse.model.matrix. Hyperparameters are matched only approximately and the resulting models differ somewhat in AUC. Versions date from 2015 (xgboost 0.4-0 GitHub snapshot 2015-05-16, scikit-learn 0.15.2 before HistGradientBoostingClassifier existed, R 3.2.0); the benchmark's own May 2017 update says LightGBM is now the fastest GBM tool and moved GBM tracking to szilard/GBM-perf; scikit-learn only ran for 10K and 100K rows and R gbm has no 10M run in experiment A. CPU model and compiler flags are not stated (EC2 c3.8xlarge, r3.8xlarge occasionally for larger runs). XGBoost is itself an incumbent of this category and the comparison is off the category's listed baselines (oneDNN, cuDNN, XNNPACK, Eigen tensor). The KDD 2016 paper (arXiv 1603.02754) could not be opened (arxiv.org, ar5iv and mirrors EGRESS_BLOCKED); a search snippet says its Higgs-1M exact-greedy comparison (dense data so scikit-learn could run) has XGBoost 'more than 10x faster than scikit-learn' and R gbm faster per tree only because it expands one branch with lower accuracy (snippet only, numbers not recorded). The repo's demo/kaggle-higgs/speedtest.py publishes no numbers. [retier] benchm-ml (szilard) is independent but not like for like: xgboost used all 32 cores while R gbm is single-threaded and its interaction.depth=16 means 16 splits per tree, not depth 16 (gbm tree.cpp); scikit-learn ratios exclude encoding and compare a dense exact split on 1 thread with a sparse scan on 32 threads; H2O beat xgboost at 10M rows in the same table (3500 vs 9000 s, 300 vs 1000 s). Measured version used the exact updater (hist arrived in v0.7).

Multithreaded exact/histogram tree boosting with sparse-aware data structures, distributed and GPU modes; the benchmark's xgboost run used a sparse one-hot matrix and nthread = detectCores(). Memory was 1 GB at 1M rows (6 GB at 10M in experiment A).

## Maintenance

Actively maintained (commits through 2026-10-07, PyPI 3.4.1 released 2026-08-15, 405 open issues, 28.8k stars) and Apache-2.0; install the prebuilt packages rather than vendoring the C++ core.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent third-party suite (szilard/benchm-ml, 1.9k stars) with public scripts (3-boosting/1-gbm.R, 2-boost.py, 6-xgboost.R) and install/version notes (0-init/1-install.md, 0-init/1a-versions.txt) showing XGBoost training faster than R gbm and scikit-learn GradientBoostingClassifier; not A because no CPU model (only EC2 c3.8xlarge/r3.8xlarge) and no compiler or flags are stated (xgboost was built from source by devtools::install_github with R's default flags).
- **Verifier notes:** All claimed numbers match the Boosting table in the benchm-ml README (e.g. 1M A 400 vs 3000 s R, 10K A 6 vs 1100 s Python; derived ratios are correct). Main shortcomings: 32 threads vs single-threaded baselines, scikit-learn timed on dense one-hot input that the README itself says makes it slow (1.5x of R with integer encoding), 2015 versions, and an off-category baseline.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** szilard/benchm-ml (verifier); enricher (wave 8)
- **Pages the verifier opened:**
  - <https://github.com/szilard/benchm-ml>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/README.md>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/3-boosting/1-gbm.R>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/3-boosting/2-boost.py>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/3-boosting/6-xgboost.R>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/0-init/1a-versions.txt>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/0-init/1-install.md>
  - <https://github.com/dmlc/xgboost>
  - <https://github.com/dmlc/xgboost/commits/master>
- **Sources the enricher read:**
  - <https://github.com/dmlc/xgboost>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/README.md>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/doc/build.rst>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/doc/treemethod.rst>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/doc/prediction.rst>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/doc/faq.rst>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/NEWS.md>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/src/tree/updater_colmaker.cc>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/src/common/hist_util.cc>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/python-package/xgboost/sklearn.py>
  - <https://raw.githubusercontent.com/dmlc/xgboost/master/include/xgboost/c_api.h>
  - <https://github.com/dmlc/xgboost/issues?q=is%3Aissue+slow+training+label%3Aperformance>
  - <https://github.com/dmlc/xgboost/issues/9013>
  - <https://pypi.org/pypi/xgboost/json>
  - <https://pypi.org/pypi/xgboost-cpu/json>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/README.md>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/3-boosting/1-gbm.R>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/3-boosting/2-boost.py>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/3-boosting/6-xgboost.R>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/0-init/1a-versions.txt>
  - <https://raw.githubusercontent.com/szilard/benchm-ml/HEAD/0-init/1-install.md>
  - <https://raw.githubusercontent.com/szilard/GBM-perf/master/README.md>
  - <https://raw.githubusercontent.com/gbm-developers/gbm/master/src/tree.cpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dmlc/xgboost`) · [data/wave8/enrich/raw/github_com_dmlc_xgboost.json](../../../data/wave8/enrich/raw/github_com_dmlc_xgboost.json) (enrichment confidence 0.8)

</details>
