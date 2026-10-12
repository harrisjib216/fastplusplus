# mlpack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only C++17 machine learning library (Armadillo-based) whose tree-based k-NN and k-means beat 2012-era scikit-learn, Shogun, MATLAB and Weka.

| | |
|---|---|
| **Beats** | scikit-learn (sklearn); the same tables also compare Shogun Toolkit, MATLAB, Weka and mlpy |
| **Claimed result** | Paper states mlpack k-NN and k-means are 'faster than the competitors in all test cases'. k-NN seconds, mlpack vs sklearn: isolet 13.0197 vs 46.8016, miniboone 20.2045 vs 714.2385 (about 35x, derived from page data), covtype 14.3449 vs 651.6259, corel 4.9716 vs 160.4597, randu 1020.9142 vs 8780.0176; Weka isolet 213.4735. k-means seconds: randu 727.1498 vs Shogun 7443.2675, MATLAB 3117.5177, sklearn 'memory' (out of memory); isolet 4.9762 vs sklearn 7.0902; miniboone 0.1853 vs MATLAB 0.7221, sklearn out of memory. |
| **Workload** | Wall-clock seconds for k-nearest-neighbors (k=3) and k-means (same starting centroids, 1000 iterations max) on ten data sets (eight UCI sets, MNIST 70000x784, a uniform random 1000000x10 set), mlpack 1.0.3 against the libraries' contemporary releases; load time excluded, mean of 5 runs. |
| **Metric** | throughput |
| **Hardware** | AMD Phenom II X6 1100T at 3.3 GHz, 8 GB RAM (single consumer workstation) |
| **Adoption** | 5.7k stars, NumFOCUS sponsored project |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/mlpack/mlpack) · [benchmark](https://raw.githubusercontent.com/mlpack/mlpack.org/master/papers/2013mlpack.pdf) |

## Verdict

The JMLR 2013 MLOSS paper by mlpack's own authors timed mlpack 1.0.3 against 2012-era scikit-learn, Shogun, MATLAB, Weka and mlpy (versions, compiler and flags not stated) on one AMD Phenom II X6 1100T with 8 GB RAM, mean of 5 runs, load time excluded: all-k-NN with k=3 ran, for example, 20.2 s vs scikit-learn's 714.2 s on miniboone (about 35x) and 1020.9 s vs 8780.0 s on a 1,000,000 x 10 uniform set, and k-means from shared starting centroids ran 727.1 s vs MATLAB's 3117.5 s and Shogun's 7443.3 s on that set, with scikit-learn out of memory. An independent HPDC 2017 knor paper reportedly found mlpack and scikit-learn at parity per k-means iteration on Friendster-8 (13.09 s vs 12.84 s, single-threaded; search snippet only, paper not opened).

## Use it when

- Exact all-k-nearest-neighbor or range search on low-to-moderate dimensional data (tens of dimensions) with up to millions of points, from C++ without a Python runtime.
- C++ deployment where you want header-only code with no runtime beyond Armadillo plus a BLAS/LAPACK, and the option to expose the same model to Python, R, Julia or Go.
- k-means with a fixed set of starting centroids where you can choose an accelerated Lloyd step (HamerlyKMeans, ElkanKMeans, DualTreeKMeans) by template parameter.
- Research or prototyping that needs swappable distance metrics, tree types or approximation (epsilon) levels without writing new search code.

## Skip it when

- High-dimensional nearest-neighbor search (hundreds of dimensions or more): trees degrade, the docs point to NAIVE mode for that case, and approximate libraries such as FAISS scale further; even in the 2013 table mnist (784 dimensions) took mlpack 2719.8 s.
- When you want a drop-in acceleration of existing scikit-learn code: the API, data layout (column-major, one point per column) and model objects differ.
- Multi-core k-NN: the neighbor-search code contains no OpenMP, so a single search runs on one thread; only some methods (naive k-means, final k-means assignment) parallelise internally.
- Deep learning at scale or GPU work: the neural-network module is CPU/Armadillo based and nothing here was benchmarked against PyTorch or TensorFlow.
- Projects sensitive to build time: the README warns that the template-heavy code makes compilation slow unless individual headers and extern templates are used.

## How it is fast

k-NN uses space-partitioning trees (kd-tree by default; cover trees, ball trees, R-trees and spill trees available) with the tree-independent dual-tree algorithm, which prunes query-node/reference-node pairs at once instead of searching point by point. Policy-based templates resolve distance metrics and tree types at compile time, and Armadillo expression templates avoid temporary copies. k-means offers Elkan, Hamerly, Pelleg-Moore and dual-tree Lloyd steps besides the naive OpenMP-parallel step, which is the default.

## Compared with alternatives

Pick mlpack over oneDAL/sklearnex when you are writing C++ (not Python) and want exact tree-based neighbor search or swappable k-means variants in a header-only package; pick oneDAL to accelerate existing scikit-learn code in place, and FAISS when vectors are high-dimensional, the data set is huge or approximate search on GPU is acceptable.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Armadillo &gt;= 10.8 (with BLAS and LAPACK), ensmallen &gt;= 2.10.0, cereal &gt;= 1.1.2; bundles STB (images), cpp-httplib (dataset download) and dr_libs (audio), each switchable to system copies or disabled by macros in config.hpp |
| **Minimum toolchain** | C++17; CMake 3.19 for the build and tests; GCC 8+ (CMake check), clang 3.5+, MSVC with /bigobj |
| **Platforms** | Linux, macOS, Windows (vcpkg or source build); docs cover cross-compiling to ARMv7 (Raspberry Pi 2) |
| **Thread safety** | not documented for sharing one KNN or KMeans object across threads; compile with -fopenmp for the internally parallel methods, and a thread-specific random seed bug was fixed in 4.7.0 (#4027) |
| **Drop-in for the baseline** | partial — same algorithms as scikit-learn, but a C++ API (or mlpack's own Python bindings) with different classes, parameters and column-major data layout; existing sklearn code must be rewritten |

## Gotchas

- The headline benchmark is not settings-matched and is unstable across the authors' own papers: on the same AMD Phenom II X6 1100T, a uniform 1,000,000 x 10 all-k-NN took scikit-learn 1550.720 s against mlpack's 1423.949 s (about 1.09x, k=5, CSV load and save included) in the 2011 mlpack paper, but 8780.0176 s against 1020.9142 s (about 8.6x, k=3, load excluded) in the 2013 JMLR table; scikit-learn's version and search algorithm are stated in neither, so the large ratios depend on an undocumented competitor configuration (derived from page data).
- In the 2013 k-means table scikit-learn 'ran out of memory' from miniboone (130,064 x 50, 2 clusters, about 52 MB as doubles, derived from page data) upward on an 8 GB machine, which points to a harness or version problem rather than an algorithmic limit; those six rows are failures, not timings.
- KMeans&lt;&gt; defaults to NaiveKMeans (a per-point distance loop, not a BLAS matrix product); the accelerated Elkan, Hamerly, Pelleg-Moore and dual-tree steps must be selected as the LloydStepType template argument. Issue #4155 (May 2026) measured cover-tree k-NN 3-8x slower than the Beygelzimer reference implementation, with covtype tree construction 26x slower and dual-tree mode slower than single-tree on some data sets; 4.8.0 lists a 5-10x cover-tree construction speedup (#4164).
- KNN copies the reference set unless it is passed with std::move, the tree build reorders points (indices are mapped back), a reused query tree must be reset with ResetTree() between searches, and OpenBLAS 0.3.26 or older built with pthreads oversubscribes threads when combined with -fopenmp (README warning).

## Known shortcomings

- Self-authored JMLR 2013 paper with 2012-era versions: no compiler or flags, competitor versions and settings unstated, only k-NN and k-means compared (isolet 13.0 s vs scikit-learn 46.8 s, miniboone 20.2 vs 714.2 s on an AMD Phenom II X6).
- Enricher: the 2011 mlpack paper on the same Phenom II X6 shows sklearn 1550.7 s vs mlpack 1423.9 s (about 1.09x, k=5, I/O included) where the 2013 JMLR paper shows 8780.0 vs 1020.9 s (about 8.6x); the sklearn version and algorithm are never stated, and the sklearn k-means 'memory' failures start at miniboone (about 52 MB), a harness or version problem. KMeans&lt;&gt; defaults to naive Lloyd; KNN search has no OpenMP; issue #4155 (cover tree 3-8x slower than reference); the knor paper (snippet) puts mlpack and sklearn at parity. Lead: flashxio/knor.

## Caveats and trade-offs

Peer-reviewed (JMLR 14, 2013, pages 801-805, machine learning open source software track) but written by mlpack's own developers. Numbers are from 2012-era releases (mlpack 1.0.3, then LGPL-licensed; competitor versions are not stated in the paper) on a 2011 consumer CPU, so they say little about today's scikit-learn. Only k-NN (k=3) and k-means are tabulated; 'other methods, omitted due to space constraints' are asserted to show similar speedups without data. The paper states neither compiler nor flags, nor which search algorithm or settings each competitor used for k-NN (mlpack 1.0.3 itself offered kd-tree and cover-tree search), so the comparison is not settings-matched on the page. Weka and mlpy are excluded from the k-means table because they cannot take starting centroids; sklearn's k-means rows from miniboone upward are 'memory' (out of memory), not timings. The later public harness github.com/mlpack/benchmarks (107 stars) states no CPU, compiler or flags and does not reference the 2013 tables. The live results page mlpack.org/benchmark.html and the later benchmark system paper were not opened here. The 2018 and 2023 JOSS papers contain no performance numbers except that compilation is 'often an order of magnitude faster' after dropping Boost. No comparison against TensorFlow or PyTorch exists in these sources.

Header-only C++17 library that needs Armadillo plus a BLAS/LAPACK (OpenBLAS pthreads builds 0.3.26 and older can oversubscribe threads, per the README warning); template-heavy so compile time and memory are high unless individual headers are included; bindings for Python, Julia, Go, R and CLI.

## Maintenance

Actively maintained (4.8.0 released 2026-06-07 with further changes already queued in HISTORY.md, NumFOCUS-sponsored, BSD-3-Clause, 5.7k stars) and copyable as headers, but its speed evidence is a 2013 self-run comparison whose competitor settings are unstated and inconsistent with the authors' 2011 run, so re-benchmark against current scikit-learn before relying on the ratios.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** JMLR 14 (2013) MLOSS paper, peer reviewed, Tables 1 and 3 time mlpack 1.0.3 k-NN and k-means against sklearn, Weka, Shogun, MATLAB and mlpy on an AMD Phenom II X6 1100T; every number in claimed_speedup matches the tables. No public harness, compiler or flags for these runs and the authors are mlpack's developers, so B and not A.
- **Verifier notes:** All quoted numbers verified in the PDF (k-NN miniboone 20.2045 vs sklearn 714.2385, about 35x derived; k-means randu 727.1498 vs Shogun 7443.2675, MATLAB 3117.5177, sklearn out of memory). Shortcomings: 2013-era versions, self-authored benchmark, competitor versions/settings and compiler flags unstated, only two algorithms tabulated. Metadata checked: BSD-3-Clause, 5.7k stars, not archived, last commit 2026-10-06.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** JMLR 2013 paper (verifier); enricher paper reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mlpack/mlpack.org/master/papers/2013mlpack.pdf>
  - <https://github.com/mlpack/mlpack>
  - <https://github.com/mlpack/mlpack/commits>
  - <https://github.com/mlpack/benchmarks>
- **Sources the enricher read:**
  - <https://github.com/mlpack/mlpack>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/README.md>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/HISTORY.md>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack/config.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack/core.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack/base.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/doc/user/methods/knn.md>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/doc/user/install.md>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/doc/user/compile.md>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack/methods/kmeans/kmeans.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack/methods/kmeans/kmeans_impl.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack/methods/kmeans/naive_kmeans_impl.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack/methods/neighbor_search/neighbor_search.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack/methods/neighbor_search/neighbor_search_impl.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack/methods/neighbor_search/neighbor_search_rules_impl.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack/HEAD/src/mlpack/core/tree/binary_space_tree/dual_tree_traverser_impl.hpp>
  - <https://raw.githubusercontent.com/mlpack/mlpack.org/master/papers/2013mlpack.pdf>
  - <https://raw.githubusercontent.com/mlpack/mlpack.org/master/papers/2011mlpack.pdf>
  - <https://raw.githubusercontent.com/mlpack/mlpack.org/master/papers/2014automatic.pdf>
  - <https://raw.githubusercontent.com/mlpack/mlpack.org/master/papers/2018mlossmlpack.pdf>
  - <https://raw.githubusercontent.com/mlpack/mlpack.org/master/papers/2018mlpack.pdf>
  - <https://raw.githubusercontent.com/mlpack/mlpack.org/master/papers/2023mlpack.pdf>
  - <https://github.com/mlpack/mlpack.org/tree/master/papers>
  - <https://github.com/mlpack/benchmarks>
  - <https://github.com/mlpack/benchmarks/tree/master>
  - <https://raw.githubusercontent.com/mlpack/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/mlpack/benchmarks/master/methods/scikit/kmeans.py>
  - <https://raw.githubusercontent.com/mlpack/benchmarks/master/methods/mlpack/allknn.py>
  - <https://raw.githubusercontent.com/mlpack/benchmarks/master/base.yaml>
  - <https://raw.githubusercontent.com/mlpack/benchmarks/master/test.yaml>
  - <https://raw.githubusercontent.com/mlpack/benchmarks/master/driver.yaml>
  - <https://github.com/mlpack/mlpack/issues?q=is%3Aissue+knn+slow>
  - <https://github.com/mlpack/mlpack/issues/4155>
  - <https://github.com/flashxio/knor>
  - https://www.mlpack.org/benchmark.html (EGRESS_BLOCKED)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mlpack/mlpack`) · [data/wave8/enrich/raw/github_com_mlpack_mlpack.json](../../../data/wave8/enrich/raw/github_com_mlpack_mlpack.json) (enrichment confidence 0.75)

</details>
