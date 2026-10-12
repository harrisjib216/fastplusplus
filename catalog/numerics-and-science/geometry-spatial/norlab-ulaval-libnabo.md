# libnabo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> Eigen-based C++ kd-tree for exact (or epsilon-approximate) k-NN in low dimensions; the README claims 5-20% faster than ANN.

| | |
|---|---|
| **Beats** | ANN (Approximate Nearest Neighbor library, exact-search kd-tree); tests/knnbench.cpp benchmarks ANN (stack and priority search) when ANN is installed. A FLANN code path exists but is switched off in knnbench.cpp ('currently disable FLANN', #undef HAVE_FLANN). |
| **Claimed result** | README: 'On the average, libnabo is 5% to 20% faster than ANN.' |
| **Workload** | Exact k-nearest-neighbour search in low-dimensional spaces (ICP registration workloads), libnabo vs ANN. |
| **Metric** | throughput |
| **Adoption** | 489 stars |
| **Last commit** | 2025-07-16 |
| **Links** | [repository](https://github.com/norlab-ulaval/libnabo) · [benchmark](https://github.com/norlab-ulaval/libnabo) |

## Verdict

The only speed claim is first-party: the README and the doxygen FAQ say libnabo is 'about 5% to 20% faster than ANN (both -O3 -NDEBUG), probably due to the smaller memory footprint', with no CPU, dataset or table. tests/knnbench.cpp compares against ANN only when ANN is installed, and publishes nothing. In its current form it times libnabo's matrix knn(), OpenMP-parallel when OpenMP is found, against ANN queried one point at a time on one thread, so today's 'make test' numbers would not be a like-for-like comparison. The JOSER 2012 paper (co-authored by the libnabo author) that should hold the measurements was unreachable here (stephane.magnenat.net and uni-wuerzburg.de are egress-blocked); search snippets confirm only that it compares 3DTK, ANN, CGAL, FLANN, libnabo, SpatialIndex and STANN for ICP.

## Use it when

- ICP or point-cloud registration in 2D or 3D on CPU, especially if your code already uses Eigen matrices. The ICP paper the README cites evaluates exactly this use, and the CHANGELOG muted Ubuntu jammy 'until libpointmatcher build pass on jammy', so the two projects are built together.
- Many queries at once: pass them as one matrix so the size checks run once and OpenMP spreads the queries across threads.
- Exact or bounded-error kNN with a per-query maximum radius to prune the search, for example outlier rejection in registration.
- Replacing ANN in old C++ code with a reentrant, BSD-licensed library templated on scalar type (float or double).
- Projects that also want Python (pynabo, via Boost.Python) or a pure-Rust port (nabo-rs) of the same algorithm.

## Skip it when

- High-dimensional data (descriptors, embeddings): it is built for low dimensions and offers only Euclidean distance, with no approximate high-dimensional index. Use FLANN or an ANN-graph library.
- Header-only or zero-dependency builds: it is a compiled CMake library that needs Eigen, plus Boost for the Python bindings. nanoflann is header-only.
- Dynamic point sets: the tree is built once over the given cloud, with no insert or delete. Pkd-tree supports batch updates.
- Fixed-radius searches that return every point within r: knn() returns at most k results, and the radius only prunes.
- New projects on recent toolchains: CI tests only Ubuntu 18.04 and 20.04, the project builds as C++11, and Eigen 5 compatibility (#147) and MSVC build failures (#124, #113) are open issues.

## How it is fast

It is ANN's sliding-midpoint kd-tree (ANN_KD_SL_MIDPT) with a more compact memory layout. Points sit in buckets at the leaves (default bucketSize 8). Nodes live in one contiguous array; the left child is implicitly the next node, and the split dimension and right-child index share one packed uint32. Cell bounds are not stored, and the search tracks incremental offsets as in ANN's paper. The authors credit the roughly 5-fold smaller memory footprint for the speed, since the search is memory-bound. Two heap variants exist: a linear vector heap for small k (up to about 30) and an STL tree heap for larger k. The matrix knn() overload runs queries in parallel with OpenMP, which is on by default in CMake.

## Compared with alternatives

Pick libnabo over nanoflann, picoflann or PicoTree when you already store points as Eigen matrices in an ICP stack and want batched, OpenMP-parallel exact kNN with per-query radius limits. nanoflann (header-only, no Eigen requirement) and PicoTree (which publishes numbers against nanoflann) are easier to adopt and better documented on speed. SPRK-tree's harness benchmarks nabo, but no numbers were seen.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Eigen 2 or 3 (header-only); optional Boost.Python for pynabo; optional OpenMP (on by default, links gomp under GCC); optional OpenCL code paths are disabled by default ('not up-to-date with API') |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11), CMake 3.10.2+ |
| **Platforms** | x86 and arm64 on Ubuntu 18.04 and 20.04 (tested in CI); macOS and Windows 'reportedly' work, per the README |
| **Thread safety** | The FAQ says it is reentrant, unlike ANN. Each knn() call keeps its own heap, and the matrix overload is OpenMP-parallel internally. Concurrent knn() calls on one const object look safe from the source, but the README does not state this. |
| **Drop-in for the baseline** | partial — same sliding-midpoint kd-tree and bucket size as ANN, but an Eigen-matrix API, Euclidean distance only and no BD-tree, so calling code must be rewritten |

## Gotchas

- The point matrix is held by reference: 'M must stay alive throughout the use of libnabo, otherwise the results of knn are undefined.' create() returns a raw owning pointer you must delete.
- Self-matches are excluded by default. The check is squared distance &gt; numeric_limits&lt;T&gt;::epsilon() (about 1.2e-7 for float), so exact duplicate points and any neighbour closer than about 3.5e-4 units in float are silently dropped unless you pass ALLOW_SELF_MATCH.
- Results are unsorted unless SORT_RESULTS is set. Missing neighbours (radius limit) come back as InvalidIndex and infinite distance. Asking for k &gt;= cloud size (k &gt; size - 1 without self-match) throws std::runtime_error.
- The node index shares a 32-bit field with the split dimension, so the constructor throws if cols/(bucketSize/2) could exceed 2^(32 - dimBits) - 1 nodes, and Index is a 32-bit int. Very large or higher-dimensional clouds need a larger bucketSize.

## Known shortcomings

- FLANN path disabled in knnbench.cpp, so only ANN is raced; ethz-asl URL redirects to norlab-ulaval (transferred, not a fork); JOSER 2012 paper unreachable here, so B is possible if it can be read.
- Claim not like-for-like: knnbench.cpp times libnabo batched kNN with OpenMP (default ON) against single-threaded ANN. JOSER 2012 paper unreachable here. Default self-match exclusion drops any neighbour with dist2 &lt;= machine epsilon, including true duplicates. Wrappers jefferis/nabor (R) and enlightware/nabo-rs (Rust) are ports, not separate entries.

## Caveats and trade-offs

README claim only ('5% to 20% faster than ANN'), no published benchmark output, hardware, compiler or flags. Numbers presumably sit in the cited peer-reviewed paper (Elseberg, Magnenat, Siegwart, Nuechter, 'Comparison of nearest-neighbor-search strategies and implementations for efficient shape registration', JOSER 3(1) 2012, doi 10.6092/JOSER_2012_03_01_P2), co-authored by the libnabo author; it was not opened (doi.org, the author's site and uni-wuerzburg.de are blocked here), so tier C until someone reads it. 'make test' runs tests/knnbench.cpp on a bundled 3D scan (K=1/10/30) against ANN if installed; FLANN comparison is disabled in that file. The repo was transferred from ethz-asl (github.com/ethz-asl/libnabo redirects to norlab-ulaval/libnabo); it is not a fork. ANN is not a listed incumbent here.

Eigen-based, scalar-type-agnostic templates, compact data types, optional Python bindings; low-dimensional spaces; CPU (and OpenCL in some builds).

## Maintenance

Stale: last commit 2025-07-16, last release 1.1.2 (2024-05-23), recent changes mostly CI and Docker work under NorLab maintenance. It is BSD-3-Clause and small enough to vendor, but the build targets older Ubuntu and Eigen 3.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README only states 'On the average, libnabo is 5% to 20% faster than ANN' with no methodology; tests/knnbench.cpp benchmarks ANN when it is installed but publishes no results, CPU or flags, and the cited JOSER 2012 paper (which could raise this to B) could not be opened from this container.
- **Verifier notes:** Metadata checked on github.com: 489 stars, BSD-3-Clause (LICENSE file read), not a fork, not archived, last master commit 2025-07-16 (stale is right). An enricher with access to the JOSER paper should check whether it shows the libnabo-over-ANN win; if it does, B is justified.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/norlab-ulaval/libnabo>
  - <https://github.com/norlab-ulaval/libnabo/commits>
  - <https://github.com/norlab-ulaval/libnabo/tree/master/tests>
  - <https://github.com/ethz-asl/libnabo>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/README.md>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/tests/knnbench.cpp>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/tests/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/norlab-ulaval/libnabo>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/README.md>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/nabo/nabo.h>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/nabo/nabo_private.h>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/nabo/kdtree_cpu.cpp>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/nabo/nabo.cpp>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/tests/knnbench.cpp>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/package.xml>
  - <https://raw.githubusercontent.com/norlab-ulaval/libnabo/HEAD/CHANGELOG.rst>
  - <https://github.com/norlab-ulaval/libnabo/issues?q=is%3Aissue>
  - <https://github.com/norlab-ulaval/libnabo/issues/126>
  - https://stephane.magnenat.net/publications/Comparison%20of%20nearest-neighbor-search%20strategies%20and%20implementations%20for%20efficient%20shape%20registration%20-%20Elseberg%20et%20al.%20-%20JOSER%20-%202012.pdf (EGRESS_BLOCKED)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/norlab-ulaval/libnabo`) · [data/wave8/enrich/raw/github_com_norlab_ulaval_libnabo.json](../../../data/wave8/enrich/raw/github_com_norlab_ulaval_libnabo.json) (enrichment confidence 0.75)

</details>
