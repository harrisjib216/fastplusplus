# oneDAL (oneAPI Data Analytics Library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Intel's C++ classical-ML library (k-means, SVM, kNN, linear models, PCA) behind sklearnex; beats stock scikit-learn on multi-core x86.

| | |
|---|---|
| **Beats** | scikit-learn 1.8.0 (stock CPU implementation); the oneDAL README separately compares against Apache Spark MLlib |
| **Claimed result** | sklearnex README text: 'average speed up of 8.5x on training and inference', 'up to 100X'. README chart image (scikit-learn-acceleration.PNG, combined FP32 and FP64 averages): fit LinearRegression 48.5x, SVR 28.8x, Ridge 15.2x, SVC 14.6x, KMeans 7.7x, DBSCAN 3.0x, ElasticNet 1.2x, Lasso 1.1x, KNeighborsClassifier(brute) fit 1.0x; predict NuSVR 395.8x, NuSVC 377.7x, SVR 330.5x, SVC 236.3x, KNeighborsRegressor(kd_tree) 153.3x, KMeans 24.6x, ElasticNet 1.1x, Lasso 1.1x. oneDAL README: '3-18x increase in performance compared to the default Apache Spark MLlib' (chart: Implicit ALS 3.6x, K-means 7.4x, Linear Regression 13.8x, Correlation 18.1x, PCA 18.2x). |
| **Workload** | Training (fit) and inference (predict/transform) time per scikit-learn estimator, Extension for Scikit-learn (sklearnex 2026.0.0, which calls oneDAL) against stock scikit-learn 1.8.0, combined FP32 and FP64 averages on one socket of a Xeon 6767P; oneDAL README adds Implicit ALS, K-means, linear regression, correlation and PCA against Apache Spark MLlib on 7 x AWS m5.2xlarge. |
| **Metric** | throughput |
| **Hardware** | 1 node, 6th Gen Intel Xeon 6767P, 64 cores per socket, 2 sockets (1 used), HT on, Turbo on, SNC on, 1024 GB DDR5-8800; tested by Intel as of 2026-06-01. Spark chart: 7 x m5.2xlarge AWS instances (CPU model not given). |
| **Compiler and flags** | Not stated; prebuilt packages: Python 3.12.13, NumPy 2.4.4, pandas 3.0.2, SciPy 1.17.1, scikit-learn 1.8.0, scikit-learn-intelex 2026.0.0, Ubuntu 24.04.3, kernel 6.8.0-47; run with numactl --physcpubind=0-63 --membind=0,1 |
| **Adoption** | 652 stars; powers scikit-learn-intelex (1.4k stars) and OAP MLlib; UXL Foundation project (moved from oneapi-src/oneDAL) |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/uxlfoundation/oneDAL) · [benchmark](https://raw.githubusercontent.com/uxlfoundation/scikit-learn-intelex/HEAD/README.md) |

## Verdict

Intel ran its scikit-learn_bench harness on one socket (64 physical cores, numactl-bound) of a two-socket Xeon 6767P, comparing stock scikit-learn 1.8.0 with sklearnex 2026.0.0 using prebuilt packages (no compiler flags given). It reports combined FP32/FP64 speedups (the harness's report tool aggregates by geometric mean) from 1.0x (brute kNN fit) to 48.5x (LinearRegression fit) for training and from 1.1x (Lasso, ElasticNet) to 395.8x (NuSVR predict) for inference, against README text of '8.5x average' and 'up to 100X'. The separate Spark chart (DAAL 2020 via OAP MLlib against Spark MLlib 2.4.4 on 7 x m5.2xlarge, double precision) shows 3.6-18.2x.

## Use it when

- Existing scikit-learn code on a many-core Intel Xeon using SVC, SVR, NuSVC or NuSVR (vendor chart: fit 11.7-28.8x, predict 236-396x on 64 cores), kd_tree kNN predict (138-153x), KMeans (fit 7.7x, predict 24.6x) or Ridge fit (15.2x).
- Tall dense least-squares or ridge problems (hundreds of thousands to millions of rows, tens to thousands of features) whose X^T X is well conditioned.
- C++ services that need classical ML without Python, with batch, online and distributed (MPI/SPMD) modes in one library.
- Offloading the same scikit-learn estimators to Intel GPUs via SYCL (sklearnex config_context(target_offload='gpu:0')).

## Skip it when

- Lasso and ElasticNet (1.1-1.2x), brute-force kNN fit (1.0x) or PCA fit (1.7x): the vendor's own chart shows little gain.
- Sparse matrices, sample_weight, positive=True, ball_tree kNN or non-lloyd KMeans: sklearnex falls back to stock scikit-learn for these (its algorithms page lists the conditions).
- Ill-conditioned least squares where you need the SVD-based accuracy of scipy lstsq, or results bit-identical to scikit-learn; sklearnex promises only 'equivalent mathematical accuracy'.
- Non-Intel CPUs and Arm CPUs without SVE: every published number is on Intel Xeon, and the Arm backend has no NEON path (binaries require SVE).
- Single-core or latency-bound jobs, where the share of the speedup that comes from 64-way threading shrinks.

## How it is fast

Each kernel is compiled for SSE2, AVX2 and AVX-512 and picked at runtime, data is processed in cache-sized blocks on a oneTBB-based threading layer, and the heavy arithmetic is cast as oneMKL BLAS/LAPACK calls. SVM training uses a ThunderSVM-style working-set SMO solver with an LRU kernel cache, and SVM prediction computes test-row by support-vector kernel blocks as matrix-matrix products instead of libsvm's per-sample loop. Linear regression accumulates X^T X and X^T y and solves the normal equations by Cholesky (eigendecomposition pseudo-inverse fallback) instead of scikit-learn's SVD-based scipy.linalg.lstsq. Against stock scikit-learn, much of the gain is simply using every core where scikit-learn (libsvm) runs single-threaded.

## Compared with alternatives

mlpack is the catalogued sibling that is also measured against scikit-learn (k-NN and k-means in its paper). Pick oneDAL when you want to keep scikit-learn code unchanged on Intel x86, or need SVM and linear models with GPU or MPI modes from a vendor-maintained library. CatBoost covers gradient-boosted-tree inference, which this chart does not test. The deep-learning siblings (FlashAttention, oneDNN Graph Compiler, LIBXSMM) target different workloads.

## Integration

| | |
|---|---|
| **Form** | shared lib (static libs also built; Python users install the scikit-learn-intelex wheel or conda package) |
| **Dependencies** | oneTBB, oneMKL (or the OpenBLAS reference backend), oneDPL; DPC++ compiler plus oneMKL for SYCL/GPU builds; MPI or oneCCL for distributed samples |
| **Minimum toolchain** | C++17 (makefile compiles with -std=c++17); Intel ICX is the default compiler, GCC, Clang and MSVC 2022 also supported; clang-cl from LLVM 22.1.8+ on Windows arm64; sklearnex supports Python 3.10-3.14 and scikit-learn 1.6-1.9 |
| **Platforms** | x86-64 Linux and Windows (runtime dispatch SSE2, AVX2, AVX-512); Linux aarch64 and Windows arm64 SVE-only; riscv64 listed as a makefile platform; Intel GPUs via SYCL; MPI clusters |
| **Thread safety** | not documented in the pages read; internal parallelism runs on a oneTBB-based threading layer whose API is internal |
| **Drop-in for the baseline** | partial — patch_sklearn() keeps the scikit-learn API for supported estimator/parameter combinations and silently falls back otherwise; the C++ API is a separate descriptor/train/infer interface |

## Gotchas

- Fallback is silent: unsupported parameters or inputs run stock scikit-learn, and only the INFO-level 'sklearnex' logger shows 'running accelerated version on' versus 'fallback to original Scikit-learn'. Turn that logger on before trusting a speedup.
- LinearRegression swaps the algorithm: oneDAL solves the normal equations by Cholesky with a hard-coded 1e-6 diagonal cutoff (the source comment calls the thresholds 'just a guess') and falls back to an eigendecomposition pseudo-inverse, while scikit-learn 1.8 calls SVD-based scipy.linalg.lstsq. The 48.5x fit bar therefore partly measures a cheaper, less stable method. Ridge (15.2x) is the like-for-like comparison, since scikit-learn's 'auto' solver on dense data is also Cholesky.
- Harness asymmetries in IntelPython/scikit-learn_bench: the SVM rows pit 64-thread oneDAL against single-threaded libsvm, so with perfect scaling the per-core gain would be only about 3.7-6.2x for SVC/SVR/NuSVC/NuSVR predict (derived from page data). The 'physical_cpus' n_jobs value comes from psutil.cpu_count(logical=False), which counts all 128 cores of the two-socket host even though the run was bound to 64 with numactl, so the kNN baselines probably ran oversubscribed. configs/common/linear_model.json also puts the scikit-learn n_jobs, solver and tol settings outside 'algorithm', so they are silently ignored; that is harmless with scikit-learn 1.8 defaults. The datasets behind each bar are in an unpublished 'backup'.
- Open correctness bugs: oneDAL #3820 (opened 2026-09-29) reports that the multinomial cross_entropy_loss value and gradient vary between calls at 4+ threads (relative error up to 1.1e-4 and 7.2e-3), which makes L-BFGS stop early; the reporter saw test log loss degrade from 0.603 to 0.763 with sklearnex 2026.1.0 and suspects the AVX2 path. #3329 reports an OpenBLAS-backend race on the global BLAS thread count.

## Known shortcomings

- Intel vendor charts measured through the sklearnex Python wrapper on 64 cores (Xeon 6767P) against scikit-learn 1.8.0, no flags or workload sizes; NuSVR predict 395.8x and NuSVC 377.7x exceed the 'up to 100X' headline while KNeighbors brute fit is 1.0x. Repo renamed from oneapi-src/oneDAL.
- Enricher: the SVM bars compare 64-thread oneDAL with single-threaded libsvm (per-core gain about 3.7-6.2x for predict, derived); the LinearRegression 48.5x swaps algorithms (normal-equations Cholesky with a hard-coded 1e-6 cutoff vs scipy SVD lstsq; Ridge 15.2x is the like-for-like bar); scikit-learn_bench's physical_cpus uses psutil.cpu_count(logical=False), giving 128 cores while numactl bound the run to 64, so the kNN baselines were probably oversubscribed; per-bar datasets sit in an unpublished backup. Open bugs #3820 (multinomial loss nondeterministic at 4+ threads) and #3329 (OpenBLAS-backend race). OAP MLlib (the Spark 3-18x path) was archived 2026-07-06 with known security issues; Arm builds are SVE-only.

## Caveats and trade-offs

First-party Intel numbers on Intel hardware (vendor selling the CPUs), not peer reviewed, so C. The speedup is measured through the Python sklearnex wrapper on stock scikit-learn, not through oneDAL's C++ API, and runs on 64 physical cores of one socket, so part of the gain is threading against stock estimators that are partly single-threaded (for example libsvm-based SVC/SVR). Benchmark code is linked (github.com/IntelPython/scikit-learn_bench, Apache-2.0, 124 stars) but the README does not say which configs or data sizes produced the chart, and no compiler or flags are given, so it is short of A. The 8.5x average and 'up to 100X' are README text; per-algorithm values were read from the chart, whose largest bars (NuSVR predict 395.8x, NuSVC predict 377.7x) exceed the 'up to 100X' text, while several estimators gain little (Lasso and ElasticNet 1.1-1.2x, KNeighborsClassifier(brute) fit 1.0x). The Spark MLlib chart is older (Intel DAAL 2020 Gold, Spark 2.4.4, emr-5.27.0, double precision, 7 x m5.2xlarge, no benchmark code, no CPU model). The old repo URL https://github.com/oneapi-src/oneDAL now lives at uxlfoundation/oneDAL. The arXiv 1909.11822 scaling paper cited by the README was not opened (arxiv.org blocked).

Intel-led, x86 SIMD and cache tuning for CPUs plus SYCL GPU and MPI distributed modes; results are 'equivalent mathematical accuracy' rather than bit-identical to scikit-learn; some estimators gain little (ElasticNet, Lasso, brute-force KNN regressor fit about 1.0 to 1.2x).

## Maintenance

Actively maintained under the UXL Foundation (last commit 2026-10-06, 2026.x releases) and Apache-2.0. The build is heavy (Intel make/Bazel plus oneTBB and oneMKL), so most users take the conda, NuGet or pip packages. The Spark path in the README, OAP MLlib, was archived on 2026-07-06 with a notice that Intel will not support it and that it has known security issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Vendor (Intel) numbers in the sklearnex README chart and oneDAL README chart, not peer reviewed; the chart states CPU and software versions but no compiler/flags or per-estimator workload sizes, and the linked IntelPython/scikit-learn_bench does not identify the configs behind the chart, so C.
- **Verifier notes:** Both README charts were opened and every quoted number matches; claimed_speedup extended with the chart's largest and smallest bars (NuSVR/NuSVC predict above 100x, KNeighbors brute fit 1.0x). Shortcomings: vendor benchmark through the Python wrapper, workload sizes and flags unstated, threading included, Spark chart from 2020-era DAAL. Metadata checked: Apache-2.0, 652 stars, not archived, last commit 2026-10-06.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** vendor charts (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/uxlfoundation/scikit-learn-intelex/HEAD/README.md>
  - <https://raw.githubusercontent.com/uxlfoundation/scikit-learn-intelex/HEAD/doc/sources/_static/scikit-learn-acceleration.PNG>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/README.md>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/docs/readme-charts/intel%20oneDAL%20Spark%20samples%20vs%20Apache%20Spark%20MLlib.png>
  - <https://github.com/uxlfoundation/oneDAL>
  - <https://github.com/uxlfoundation/oneDAL/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/README.md>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/makefile>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/dev/make/function_definitions/32e.mk>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/dev/make/compiler_definitions/gnu.mk>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/docs/source/contribution/threading.rst>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/docs/source/contribution/cpu_features.rst>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/cpp/daal/src/algorithms/svm/svm_train_thunder_impl.i>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/cpp/daal/src/algorithms/svm/svm_predict_impl.i>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/cpp/daal/src/algorithms/linear_model/linear_model_train_normeq_finalize_impl.i>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/cpp/daal/src/algorithms/service_kernel_math.h>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/examples/oneapi/cpp/source/kmeans/kmeans_lloyd_dense_batch.cpp>
  - <https://raw.githubusercontent.com/uxlfoundation/oneDAL/HEAD/examples/oneapi/cpp/CMakeLists.txt>
  - <https://github.com/uxlfoundation/oneDAL>
  - <https://github.com/uxlfoundation/oneDAL/releases>
  - <https://github.com/uxlfoundation/oneDAL/tree/main/cpp/daal/src/algorithms/svm>
  - <https://github.com/uxlfoundation/oneDAL/tree/main/docs/source/contribution>
  - <https://github.com/uxlfoundation/oneDAL/issues?q=is%3Aissue%20label%3Abug>
  - <https://github.com/uxlfoundation/oneDAL/issues/3820>
  - <https://github.com/uxlfoundation/oneDAL/issues/3329>
  - <https://raw.githubusercontent.com/uxlfoundation/scikit-learn-intelex/HEAD/README.md>
  - <https://raw.githubusercontent.com/uxlfoundation/scikit-learn-intelex/HEAD/doc/sources/_static/scikit-learn-acceleration.PNG>
  - <https://raw.githubusercontent.com/uxlfoundation/scikit-learn-intelex/HEAD/doc/sources/algorithms.rst>
  - <https://raw.githubusercontent.com/uxlfoundation/scikit-learn-intelex/HEAD/sklearnex/linear_model/linear.py>
  - <https://raw.githubusercontent.com/uxlfoundation/scikit-learn-intelex/HEAD/onedal/linear_model/linear_model.py>
  - <https://github.com/uxlfoundation/scikit-learn-intelex/issues?q=is%3Aissue%20label%3Abug>
  - <https://github.com/uxlfoundation/scikit-learn-intelex/issues/1712>
  - <https://github.com/uxlfoundation/scikit-learn-intelex/issues/1831>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/configs/README.md>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/configs/BENCH-CONFIG-SPEC.md>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/configs/regular/svm.json>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/configs/regular/knn.json>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/configs/regular/linear_model.json>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/configs/common/sklearn.json>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/configs/common/svm.json>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/configs/common/knn.json>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/configs/common/linear_model.json>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/configs/common/kmeans.json>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/sklbench/benchmarks/sklearn_estimator.py>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/sklbench/utils/measurement.py>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/sklbench/utils/special_params.py>
  - <https://raw.githubusercontent.com/IntelPython/scikit-learn_bench/HEAD/sklbench/report/implementation.py>
  - <https://github.com/IntelPython/scikit-learn_bench/tree/main/configs>
  - <https://github.com/IntelPython/scikit-learn_bench/tree/main/configs/regular>
  - <https://raw.githubusercontent.com/scikit-learn/scikit-learn/1.8.X/sklearn/linear_model/_base.py>
  - <https://github.com/oap-project/oap-mllib>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/uxlfoundation/onedal`) · [data/wave8/enrich/raw/github_com_uxlfoundation_onedal.json](../../../data/wave8/enrich/raw/github_com_uxlfoundation_onedal.json) (enrichment confidence 0.75)

</details>
