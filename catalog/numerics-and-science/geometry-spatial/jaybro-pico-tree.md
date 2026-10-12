# PicoTree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++17 kd-tree for exact and approximate kNN, radius and box search; builds faster than nanoflann and OpenCV FLANN.

| | |
|---|---|
| **Beats** | nanoflann v1.7.1 (also OpenCV FLANN 4.11.0, SciPy KDTree, scikit-learn KDTree, pykdtree) |
| **Claimed result** | C++ build 0.54 s vs nanoflann 1.42 s (2.6x, derived from page data) and OpenCV FLANN 0.99 s; C++ knn 1.13 s vs nanoflann 1.40 s (1.2x, derived from page data) and OpenCV FLANN 2.30 s. Python knn 1.64 s vs SciPy KDTree 212.04 s, scikit-learn 11.90 s, pykdtree 2.95 s; Python build 0.54 s vs SciPy 1.37 s and scikit-learn 3.60 s, but pykdtree builds faster (0.43 s). |
| **Workload** | Single-threaded kd-tree build over a 7,733,372-point LiDAR cloud and nearest-neighbour (knn=1) queries with a second 7,200,863-point cloud, max_leaf_size=10. |
| **Metric** | build-time |
| **Hardware** | Intel Core i9-14900HX |
| **Compiler and flags** | README table (i9-14900HX run): compiler not stated; root CMakeLists.txt defaults CMAKE_BUILD_TYPE to Release. docs/benchmark.md (29-08-2021 run, PicoTree v0.7.4 vs nanoflann v1.3.2): MinGW GCC 10.3, flags not stated. |
| **Adoption** | 49 stars |
| **Last commit** | 2025-08-10 |
| **Links** | [repository](https://github.com/Jaybro/pico_tree) · [benchmark](https://github.com/Jaybro/pico_tree) |

## Verdict

The author's README table compares PicoTree v1.0.0 with nanoflann 1.7.1 and OpenCV FLANN 4.11.0 (C++), and with SciPy 1.15.2, scikit-learn 1.6.1 and pykdtree 1.3.7 (Python), on an Intel Core i9-14900HX: one thread, max_leaf_size=10, knn=1, a 7,733,372-point Bremen LiDAR cloud to build and a 7,200,863-point cloud to query. The compiler and flags are not stated. PicoTree is 1.2x faster than nanoflann at knn and 2.0x faster than OpenCV FLANN, and it builds 1.8x faster than OpenCV FLANN. The 2.6x build gap against nanoflann is inflated: since nanoflann 1.4 its KDTreeSingleIndexAdaptor constructor already calls buildIndex(), and examples/benchmark/bm_nanoflann.cpp then calls tree.buildIndex() again inside the timed loop, so nanoflann's 1.42 s covers two builds. That matches the '90% slower in nanoflann v1.5.0' note in docs/benchmark.md. Halving it suggests about a 1.3x real gap (derived estimate, not measured). In Python, pykdtree builds faster (0.43 s vs 0.54 s).

## Use it when

- Static 3D point clouds (LiDAR scans, ICP correspondence search) where the tree is rebuilt often: on the author's 7.7M-point scan a single-threaded build took 0.54 s vs 0.99 s for OpenCV FLANN and 1.42 s reported for nanoflann 1.7.1
- Single-nearest-neighbour or small-k queries over millions of query points in C++: knn=1 took 1.13 s vs 1.40 s (nanoflann) and 2.30 s (OpenCV FLANN) for 7.2M queries
- Python pipelines that need exact kNN on NumPy float arrays: knn=1 took 1.64 s vs 2.95 s for pykdtree, 11.9 s for scikit-learn and 212 s for SciPy KDTree in the README, and the bindings can parallelize queries with OpenMP
- Data already in Eigen matrices, cv::Mat or a flat float buffer, used without copying (pass a std::reference_wrapper or space_map)
- Robotics or planar problems with angular coordinates (SO(2), SE(2)) where the metric has to wrap around

## Skip it when

- Point sets that change: builds are static only, with no insert or remove. Use nanoflann's dynamic/incremental adaptors or Pkd-tree for batch updates
- Build-dominated workloads on multi-core machines: construction is single-threaded, while nanoflann 1.5+ has n_thread_build and Pkd-tree builds in parallel
- High-dimensional approximate search (descriptors, embeddings): only the (1+e) kd-tree approximation and an example KdForest exist, so FAISS or an HNSW library is a better fit
- pip-only Python environments: there is no PyPI package (pypi.org/pypi/pico_tree returns 404), so you build from source with scikit-build, pybind11 and OpenMP
- Projects that need an actively maintained dependency: the last commit is 2025-08-10, there are 49 stars, and the 7 issues ever filed are all closed

## How it is fast

The default split rule is sliding midpoint (Maneewongvatana and Mount, 'It's okay to be skinny, if your friends are fat'): it cuts the longest box side at its middle with a linear std::partition and falls back to std::nth_element only when one side would be empty, which avoids median selection at every level. During construction each leaf's box is shrunk to the points it holds, and the parent stores the actual left-child max and right-child min on the split axis, so queries pick the nearer child from the real gap and prune with tighter bounds. Nearest-neighbour search uses Arya-Mount incremental distance calculation (only the split-axis term of the box distance is updated per step) with non-square-rooted metrics. Nodes come from a pool allocator in chunks of 256 rather than per-node new or std::deque, and fixing the dimension at compile time lets the distance loops unroll.

## Compared with alternatives

Pick PicoTree over nanoflann when you rebuild static trees often on one thread, need box search or wrap-around metrics, or want NumPy bindings in the same package. Pick nanoflann when you need dynamic insert/remove, a multi-threaded build, distro/vcpkg/Conan packaging or active maintenance. picoflann, Janos95/kdtree and kd3 make similar nanoflann-beating claims but cover fewer query types.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the C++ core; Eigen and OpenCV are optional (traits headers only); Python bindings need pybind11, NumPy, OpenMP and scikit-build (Python 3.10+); Google Benchmark, nanoflann and OpenCV only for the benchmarks; Google Test for the unit tests |
| **Minimum toolchain** | C++17 (issue #32: does not compile with GCC 7.5 on Ubuntu 18.04); CMake 3.12+ if you use the CMake package rather than copying src/pico_tree |
| **Platforms** | any; no SIMD intrinsics. CI builds on the latest macOS, Ubuntu and Windows runners |
| **Thread safety** | README lists 'Thread safe queries': the search methods are const, so many threads can query one built tree. Construction is single-threaded. The Python bindings run queries over the input array with OpenMP (set OMP_NUM_THREADS to control it) |
| **Drop-in for the baseline** | no |

## Gotchas

- With the default metric_l2_squared, radius inputs and all returned distances are squared, and approximate-search error ratios must be squared too (pass tree.metric()(1 + e))
- The tree takes the point set by value: pass std::move(points) or a std::reference_wrapper to avoid a copy. The tree holds pointers into its node pool, so it is move-only, and a referenced point set must outlive it and stay unchanged
- The default index type is int (32-bit signed). Query and tree scalar types must match exactly (a double query against a float tree fails to compile), and an empty input is caught only by assert
- save/load is a same-machine convenience: no endianness handling, no check that the stored tree matches the point set or template arguments, and the point set itself is not saved

## Known shortcomings

- Compiler for the README table unstated (benchmark code in examples/benchmark).
- README nanoflann build number counts two builds: bm_nanoflann.cpp constructs KDTreeSingleIndexAdaptor (whose constructor calls buildIndex() since nanoflann 1.4) and then calls buildIndex() again inside the timed loop, so the 2.6x faster build is inflated (real gap \~1.3x, derived estimate, not measured); the same bug explains the docs' 'nanoflann 1.5.0 regressed 90%' note. kNN numbers unaffected. Not on PyPI.

## Caveats and trade-offs

Author's own benchmark on one LiDAR dataset (Bremen Gaussian Point scans), single thread, max_leaf_size=10, knn=1. Benchmark code is public in examples/benchmark/ (Google Benchmark), but compiler and flags for the README table are not stated. docs/benchmark.md says nanoflann's build regressed by about 90% in v1.5.0, which inflates the build gap against nanoflann v1.7.1; the detailed C++ comparison there is a 2021 run (nanoflann v1.3.2) shown only as plots. pykdtree beats PicoTree on Python build time. nanoflann is not a listed incumbent for this category. [retier] The 2.6x build ratio is inflated: bm_nanoflann.cpp builds the nanoflann index twice in the timed loop (since nanoflann 1.4 the constructor already calls buildIndex()). The real build gap is about 1.3x (estimate). kNN numbers are unaffected. An independent suite, Lawson/Gropp/Lofstead 'Exploring Spatial Indexing for Accelerated Feature Retrieval in HPC' (arXiv 2106.13972; CCGrid 2022 per search results; code at github.com/mlawsonca/benchmarking_suite_range_searching_libraries, Release build), benchmarks 20 C/C++ libraries including pico_tree (TEST_PICO_TREE) and nanoflann (TEST_NANOFLANN). Its results are only in the paper, which was not opened (arxiv.org, osti.gov and researchgate are blocked), so a retier to B is pending paper access.

Header-only C++ kd-tree with Python bindings; Eigen, OpenCV and custom point types; sliding-midpoint build; range and knn search.

## Maintenance

Stale (last commit 2025-08-10, v1.0.0 is the latest release, 49 stars) but MIT-licensed, header-only and small enough to vendor by copying src/pico_tree; the Python bindings must be built from source.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README table compares PicoTree v1.0.0 with nanoflann v1.7.1 and OpenCV FLANN 4.11.0 (C++) and SciPy, scikit-learn and pykdtree (Python) on an Intel Core i9-14900HX, and the benchmark code is public (examples/benchmark/bm_pico_kd_tree.cpp, bm_nanoflann.cpp, bm_opencv_flann.cpp). The compiler and flags for that run are not stated (the root CMakeLists.txt only defaults to a Release build), so it falls short of A and stays first-party C.
- **Verifier notes:** All README numbers match the record. Metadata checked on github.com: MIT (COPYING.txt), 49 stars, not archived or a fork, last commit 2025-08-10 (stale, about 13.5 months).
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/Jaybro/pico_tree>
  - <https://github.com/Jaybro/pico_tree/commits>
  - <https://github.com/Jaybro/pico_tree/tree/main/examples/benchmark>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/README.md>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/docs/benchmark.md>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/examples/benchmark/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/Jaybro/pico_tree/tree/main/src/pico_tree/pico_tree>
  - <https://github.com/Jaybro/pico_tree/tree/main/src/pico_tree/pico_tree/internal>
  - <https://github.com/Jaybro/pico_tree/issues?q=is%3Aissue>
  - <https://github.com/Jaybro/pico_tree/releases>
  - <https://github.com/Jaybro/pico_tree/releases/tag/v1.0.0>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/README.md>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/docs/benchmark.md>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/COPYING.txt>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/setup.py>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pico_tree/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pico_tree/pico_tree/kd_tree.hpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pico_tree/pico_tree/core.hpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pico_tree/pico_tree/metric.hpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pico_tree/pico_tree/internal/kd_tree_builder.hpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pico_tree/pico_tree/internal/kd_tree_node.hpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pico_tree/pico_tree/internal/kd_tree_search.hpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pico_tree/pico_tree/internal/kd_tree_data.hpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pico_tree/pico_tree/internal/memory.hpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pico_tree/pico_tree/internal/search_visitor.hpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/src/pyco_tree/pico_tree/_pyco_tree/kd_tree.hpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/examples/benchmark/bm_pico_kd_tree.cpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/examples/benchmark/bm_nanoflann.cpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/examples/benchmark/bm_opencv_flann.cpp>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/examples/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/examples/python/kd_tree.py>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/.github/workflows/build-and-test.yml>
  - <https://raw.githubusercontent.com/Jaybro/pico_tree/HEAD/.github/workflows/pip.yml>
  - <https://pypi.org/pypi/pico_tree/json>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/HEAD/CHANGELOG.rst>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/v1.7.1/include/nanoflann.hpp>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/v1.3.2/include/nanoflann.hpp>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/v1.4.3/include/nanoflann.hpp>
  - <https://raw.githubusercontent.com/jlblancoc/nanoflann/v1.5.0/include/nanoflann.hpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jaybro/pico_tree`) · [data/wave8/enrich/raw/github_com_jaybro_pico_tree.json](../../../data/wave8/enrich/raw/github_com_jaybro_pico_tree.json) (enrichment confidence 0.8)

</details>
