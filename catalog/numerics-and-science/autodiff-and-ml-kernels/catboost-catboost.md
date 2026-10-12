# CatBoost

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Yandex gradient-boosted-tree library whose oblivious-tree CPU evaluator scored batches 27-60x faster than XGBoost 0.80 and LightGBM 2.2.1.

| | |
|---|---|
| **Beats** | XGBoost 0.80 and LightGBM 2.2.1 (gradient boosted tree model prediction on CPU) |
| **Claimed result** | 32 threads: CatBoost 184 ms vs XGBoost 4.89 s and LightGBM 11.1 s (about 27x and 60x, derived from page data). 1 thread: CatBoost 1.98 s vs XGBoost 1 min 12 s and LightGBM 1 min 56 s (about 36x and 59x, derived from page data). Same repo, CPU training of 1000 iterations at depth 6 on Epsilon: CatBoost 266.77 s vs XGBoost 8935.36 s and LightGBM 1323.40 s; GPU tree construction on Epsilon: 17.9 ms/tree vs XGBoost 488 ms and LightGBM 40 ms (P100, 15 bins). |
| **Workload** | Batch prediction of an 8000-tree model on the Epsilon test split (400K train / 100K test samples, 2000 dense features per the same repo's GPU benchmark README) with each library's own predictor, timed with %timeit (5 runs) at 32 threads and with a single run at 1 thread. |
| **Metric** | throughput |
| **Hardware** | Not stated for the prediction notebook (32 threads; Python 3.7.3 kernel). The training_speed README states Intel Xeon E312xx (Sandy Bridge) 32 cores for CPU runs and NVIDIA GTX1080TI + Intel Core i7-6800K for its GPU table; the 17.9 ms/tree GPU tree-construction comparison (gpu_vs_cpu_training_speed README) ran on an NVIDIA P100 with an Intel Xeon E5-2660 host. |
| **Adoption** | 9.1k stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/catboost/catboost) · [benchmark](https://github.com/catboost/benchmarks/blob/master/model_evaluation_speed/model_evaluation_benchmark.ipynb) |

## Verdict

In a first-party notebook (catboost/benchmarks model_evaluation_speed; CPU model and compiler unstated; library versions probably catboost 0.10.3, xgboost 0.80 and lightgbm 2.2.1 per the sibling README), scoring the 100K-row, 2000-feature Epsilon test split with 8000 trees took 184 ms for CatBoost vs 4.89 s for XGBoost and 11.1 s for LightGBM at 32 threads, and 1.98 s vs 72 s and 116 s on one thread (about 27x/60x and 36x/59x, derived from page data). The competitor models were fed feature columns shifted by one and no outputs were checked.

## Use it when

- High-throughput batch scoring on CPU of large tree ensembles (thousands of trees, many rows per call), where you control training and can keep the default SymmetricTree grow policy.
- Tabular data with many categorical features, which CatBoost encodes natively instead of requiring one-hot or target encoding upstream.
- C, C++, JVM or Rust services that embed the inference-only library or exported C++ code, avoiding Python wrapper overhead.
- GPU training on dense, wide data: the first-party gpu_vs_cpu README reports 17.9 ms per tree on Epsilon vs XGBoost 488 ms and LightGBM 40 ms on a P100.

## Skip it when

- You must serve existing XGBoost or LightGBM models: CatBoost cannot load them, so you would have to retrain (and revalidate) the model.
- CPU training time is the bottleneck: the repo's own table has CatBoost slower on letters (259.75 s vs 176.82 s and 112.74 s) and airline (974.1 s vs 611.9 s and 526.2 s), and szilard/GBM-perf finds it slower than both on CPU and slower than XGBoost on GPU.
- Single-row prediction from Python: issue #1346 (open since 2020-06-29) reports 1000 single-row calls taking about 0.40 s vs XGBoost 0.088 s and LightGBM 0.142 s, with a C++ export 30x faster than the wrapper.
- Models trained with Depthwise or Lossguide grow policies: these go through a scalar per-document node walk (CalcIndexesNonSymmetric) rather than the SSE oblivious path, and the benchmark did not test them.
- Building from source on an arbitrary toolchain: it needs CMake &gt;= 3.24 and &lt; 4.0, clang 18-22, lld, Conan and C++20, so most users rely on the prebuilt packages.

## How it is fast

By default CatBoost grows oblivious (symmetric) trees: every node at one depth uses the same feature/border split, so a depth-6 tree is just 6 splits plus a 64-entry leaf table. The CPU evaluator first quantizes each 128-document block of float features to ui8 bin indices with SSE compares (quantization.h). For every tree it then builds leaf indexes for 16 documents per SSE register, one byte compare and OR per depth level (CalcIndexesSseDepthed in evaluator_impl.cpp), and gathers the leaf values. There is no per-node pointer chasing or data-dependent branching, unlike the node-by-node row walks of XGBoost 0.80 and LightGBM 2.2.1.

## Compared with alternatives

No gradient-boosted-tree siblings are catalogued: the category's other entries (PyTorch, MXNet, FBGEMM, OpenVINO, MNN and others) serve neural networks. Pick CatBoost when the model is a tree ensemble and batch CPU scoring throughput matters more than CPU training time.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Prebuilt inference library (libcatboostmodel, C API in catboost/libs/model_interface/c_api.h) needs nothing else; the Python package imports numpy, pandas, scipy, six and graphviz (plus plotting extras); source builds pull dependencies through Conan; CUDA toolkit for GPU training |
| **Minimum toolchain** | Source build: C++20 (CMAKE_CXX_STANDARD 20), CMake &gt;= 3.24 and &lt; 4.0, clang 18-22 with lld on Linux, Xcode clang 15+ on macOS, Visual Studio 2022 clang-cl on Windows; prebuilt wheels avoid this |
| **Platforms** | Linux, macOS and Windows on x86-64 (SSE evaluator) and aarch64, plus an Android target; NVIDIA CUDA GPUs for training and optional GPU evaluation (EnableGPUEvaluation) |
| **Thread safety** | C API error state is thread-local (c_api.h); Python predict takes a per-call thread_count; concurrent prediction on one shared model handle is not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the benchmark notebook: XGBoost.model (num_feature 2001, no split on feature 0) and LightGBM_model.txt (max_feature_idx=2000, feature_infos 'none' for Column_0) were trained on 1-based libsvm-style feature indices, but X_test from catboost.datasets.epsilon has 2000 zero-based columns. XGBoost and LightGBM therefore scored every row on features shifted by one (feature 2000 missing), and no cell checks predictions or accuracy. The CatBoost model (features 0-1999) is aligned. Depth-bounded tree walks make the timing effect small for XGBoost, but the competitor outputs are wrong, and recent LightGBM releases reject this shape mismatch unless predict_disable_shape_check is set.
- The ensembles are not identical in size. Over the first 8000 trees, CatBoost has 64 leaves per tree at depth 6. XGBoost (19,730 trees in the file) has depth at most 6, a mean of 44.4 leaves and a mean leaf depth of 5.7. LightGBM (14,835 trees) has 4121 trees at 64 leaves, depths up to 25 and a mean leaf depth of 8.2. XGBoost therefore did no more comparisons per tree than CatBoost, so the 27x gap comes from the evaluator, not from a larger competitor model.
- Timing setup: the XGBoost DMatrix and the CatBoost Pool are built outside the timed cells (this corrects the record's note that XGBoost's time includes input handling); only LightGBM receives a raw numpy array. LightGBM's thread count is never set, so it follows the process OpenMP default (in the 1-thread section its wall time equals its CPU time). The 1-thread rows are single %time runs, not %timeit.
- The benchmark is from 2018-2019 (catboost 0.10.3, xgboost 0.80 and lightgbm 2.2.1 per the training README; the notebook kernel is Python 3.7.3), so later XGBoost and LightGBM predictors and model compilers such as Treelite and lleaves probably narrow the ratio.

## Known shortcomings

- First-party prediction notebook (184 ms vs 4.89 s / 11.1 s) with no CPU model, compiler or library versions. Slower than XGBoost and LightGBM at training on letters, airline and szilard/GBM-perf.
- Enricher: in the prediction notebook the competitor models were trained on 1-based libsvm features (XGBoost.model num_feature 2001 never splits feature 0; LightGBM max_feature_idx=2000 with Column_0 'none') while X_test has 2000 zero-based columns, so XGBoost and LightGBM were scored on features shifted by one and outputs were never checked; CatBoost's features are aligned. Model shapes do not explain the gap (XGBoost depth at most 6, mean 44.4 leaves vs CatBoost's 64 in the first 8000 trees). The XGBoost DMatrix is built outside the timed cell, so only the LightGBM timing includes input handling, and the LightGBM thread count is never set.

## Caveats and trade-offs

First-party benchmark with a public notebook and checked-in model files, but the prediction notebook states no CPU model, compiler, flags or library versions (the catboost 0.10.3 / xgboost 0.80 / lightgbm 2.2.1 versions are listed only in the training_speed README; the notebook kernel is Python 3.7.3), so tier C. The models are comparable in size: LightGBM_model.txt holds about 14.8k trees with 64 leaves each, truncated to 8000 at predict time, matching CatBoost's 8000 depth-6 (64-leaf) symmetric trees; CatBoost's speed comes from oblivious-tree evaluation. The LightGBM predict call sets no thread count, and the XGBoost/LightGBM timings include their own input handling while the CatBoost Pool is built outside the timed cell. XGBoost and LightGBM have been optimised since 2018, so the ratio is probably smaller today. Independent training benchmark szilard/GBM-perf shows CatBoost slower than both on CPU (1M rows: CatBoost 7.0 s vs XGBoost 2.7 s and LightGBM 4.0 s; 10M rows: 70 s vs 40 s and 20 s) and slower than XGBoost on GPU (3.4 s vs 1.3 s on 1M rows); it does not test prediction. In the repo's own CPU training table CatBoost is also slower on letters (259.75 s vs XGBoost 176.82 s and LightGBM 112.74 s) and airline (974.1 s vs XGBoost 611.9 s and LightGBM 526.2 s). The benchmarks repo README contains no numbers; the model_evaluation_speed folder has no README. [retier] First-party prediction notebook (184 ms vs XGBoost 4.89 s and LightGBM 11.1 s) with no CPU model, compiler or library versions. The competitor models were trained on 1-based libsvm features (XGBoost.model num_feature 2001 never splits feature 0; LightGBM max_feature_idx=2000, Column_0 'none') while X_test has 2000 zero-based columns, so XGBoost and LightGBM were scored on features shifted by one and their outputs were never checked; CatBoost's features 0-1999 are aligned. Model shapes do not explain the 27x (XGBoost depth at most 6, mean 44.4 leaves vs CatBoost's symmetric 64 over the first 8000 trees; LightGBM mean leaf depth 8.2). The XGBoost DMatrix is built outside the timed cell, so only the LightGBM timing includes input handling, and the LightGBM thread count is never set. Training is slower than XGBoost and LightGBM on letters, airline and szilard/GBM-perf.

Symmetric (oblivious) trees give very fast evaluation; Python, R, Java and C++ APIs, native categorical features, GPU and Spark training. Training on CPU is not always the fastest (see caveats).

## Maintenance

Actively maintained (commits through 2026-10-07; PyPI release 1.2.10 on 2026-02-18, 672 open issues) and Apache-2.0. Use the prebuilt packages or the inference-only library rather than vendoring, because the source build needs a pinned clang/Conan toolchain.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party notebook (catboost/benchmarks model_evaluation_speed/model_evaluation_benchmark.ipynb, with the three model files checked in) shows CatBoost 184 ms vs XGBoost 4.89 s and LightGBM 11.1 s at 32 threads and 1.98 s vs 1 min 12 s and 1 min 56 s at 1 thread, but states no CPU model, compiler, flags or library versions, so C.
- **Verifier notes:** All prediction and training numbers verified in the notebook and the training_speed / gpu_vs_cpu_training_speed READMEs; ratios correct. Shortcomings: first-party, 2018-2019 library versions, no CPU model/compiler for the prediction run, CatBoost slower than XGBoost/LightGBM for training on several datasets and in szilard/GBM-perf. Metadata (Apache-2.0, 9.1k stars, last commit 2026-10-07) confirmed.
- **Fields the verifier corrected:** `hardware`, `caveats`
- **Shortcomings recorded by:** first-party notebook (verifier); enricher notebook and model reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/catboost/benchmarks/master/model_evaluation_speed/model_evaluation_benchmark.ipynb>
  - <https://github.com/catboost/benchmarks>
  - <https://github.com/catboost/benchmarks/tree/master/model_evaluation_speed>
  - <https://raw.githubusercontent.com/catboost/benchmarks/master/model_evaluation_speed/LightGBM_model.txt>
  - <https://raw.githubusercontent.com/catboost/benchmarks/master/training_speed/README.md>
  - <https://raw.githubusercontent.com/catboost/benchmarks/master/gpu_vs_cpu_training_speed/README.md>
  - <https://raw.githubusercontent.com/szilard/GBM-perf/HEAD/README.md>
  - <https://github.com/catboost/catboost>
  - <https://github.com/catboost/catboost/commits/master>
  - <https://raw.githubusercontent.com/catboost/catboost/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/catboost/catboost>
  - <https://raw.githubusercontent.com/catboost/catboost/master/README.md>
  - <https://raw.githubusercontent.com/catboost/catboost/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/catboost/catboost/master/catboost/CatboostModelAPI.md>
  - <https://raw.githubusercontent.com/catboost/catboost/master/catboost/docs/en/installation/build-environment-setup-for-cmake.md>
  - <https://raw.githubusercontent.com/catboost/catboost/master/catboost/libs/model/cpu/evaluator_impl.cpp>
  - <https://raw.githubusercontent.com/catboost/catboost/master/catboost/libs/model/cpu/evaluator.h>
  - <https://raw.githubusercontent.com/catboost/catboost/master/catboost/libs/model/cpu/quantization.h>
  - <https://raw.githubusercontent.com/catboost/catboost/master/catboost/libs/model_interface/c_api.h>
  - <https://github.com/catboost/catboost/issues?q=is%3Aissue+predict+slow>
  - <https://github.com/catboost/catboost/issues/1346>
  - <https://pypi.org/pypi/catboost/json>
  - <https://raw.githubusercontent.com/catboost/benchmarks/master/model_evaluation_speed/model_evaluation_benchmark.ipynb>
  - <https://github.com/catboost/benchmarks/tree/master/model_evaluation_speed>
  - <https://raw.githubusercontent.com/catboost/benchmarks/master/model_evaluation_speed/XGBoost.model>
  - <https://raw.githubusercontent.com/catboost/benchmarks/master/model_evaluation_speed/LightGBM_model.txt>
  - <https://raw.githubusercontent.com/catboost/benchmarks/master/model_evaluation_speed/epsilon8k_64.bin>
  - <https://raw.githubusercontent.com/catboost/benchmarks/master/training_speed/README.md>
  - <https://github.com/szilard/GBM-perf/issues/4>
  - <https://raw.githubusercontent.com/siboehm/lleaves/HEAD/README.md>
  - <https://raw.githubusercontent.com/guitargeek/XGBoost-FastForest/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/catboost/catboost`) · [data/wave8/enrich/raw/github_com_catboost_catboost.json](../../../data/wave8/enrich/raw/github_com_catboost_catboost.json) (enrichment confidence 0.8)

</details>
