# igraph

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Graph algorithms](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `GPL-2.0-or-later` · 🟢 active

> C network-analysis library with Python/R/Mathematica bindings; 5-49x faster than pure-Python NetworkX on loading, PageRank, k-core, SCC.

| | |
|---|---|
| **Beats** | NetworkX 2.4 (pure Python); SNAP 5.0.0 as a second row |
| **Claimed result** | Median seconds, igraph vs NetworkX (Amazon / Google / Pokec), from runtime_results.png: PageRank 0.57 / 2.42 / 23.39 vs 8.59 / 33.5 / 239.75 (about 15x / 14x / 10x, derived from page data); k-core 0.15 / 0.92 / 5.99 vs 3.63 / 42.6 / 296.26 (about 24x / 46x / 49x, derived); strongly connected components 0.22 / 1.38 / 3.96 vs 2.22 / 7.77 / 61.74 (about 10x / 5.6x / 16x, derived); loading 0.57 / 3.87 / 25.75 vs 4.72 / 19.24 / 140.19 (about 8x / 5x / 5x, derived); shortest path 0.05 / 0.41 vs 1.37 / 3.41 on Amazon / Google (about 27x / 8x, derived). The Pokec shortest-path row (igraph 0.6 s vs NetworkX 5.65 s, SNAP 2.3 s) is not like-for-like: the igraph and SNAP scripts start from vertex 0 while the NetworkX script switches to node '1' for Pokec. Versus SNAP: loading 25.75 vs 52.73 s on Pokec (about 2x, derived); SNAP is faster on PageRank. |
| **Workload** | Median wall time of graph loading, single-source shortest path, PageRank (damping 0.85, tol 1e-3), k-core and strongly connected components on the SNAP datasets amazon0302, web-Google and soc-Pokec, through the Python bindings (python-igraph 0.8.2 against networkx 2.4, Python 3.8). |
| **Metric** | throughput |
| **Hardware** | Google Compute n1-standard-16 (16 vCPU Haswell 2.3 GHz, 60 GB); exact CPU model not given |
| **Compiler and flags** | not stated; python-igraph 0.8.2 installed as a conda-forge binary (setup/setup.md), Python 3.8 |
| **Adoption** | 2.0k stars (igraph/igraph); widely used R, Python and Mathematica bindings |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/igraph/igraph) · [benchmark](https://github.com/timlrx/graph-benchmarks) |

## Verdict

A third-party suite (timlrx/graph-benchmarks, 2020) timed python-igraph 0.8.2 from conda-forge against NetworkX 2.4 on Python 3.8, medians of 100 runs (10 on Pokec) on a GCE n1-standard-16 (Haswell 2.3 GHz, no CPU model or compiler flags): loading about 5-8x, PageRank 10-15x, k-core 24-49x, strongly connected components 5.6-16x and shortest path 8-27x faster on amazon0302, web-Google and soc-Pokec. The Pokec shortest-path row is invalid (igraph and SNAP start from an isolated phantom vertex 0, NetworkX from node 1), and the PageRank row is not like-for-like: NetworkX 2.4 stops once the L1 change is below N\*tol, which with tol=1e-3 on graphs of hundreds of thousands of nodes means after one power iteration, while igraph's PRPACK ignores eps=1e-3 and solves to 1e-10 and SNAP iterates until the L1 change is below 1e-3; igraph wins despite doing more work, but the ratios (and SNAP's PageRank lead) do not compare equal accuracy.

## Use it when

- Python or R analysis of static graphs with roughly 10^5-10^7 edges where NetworkX takes seconds to minutes per whole-graph query (PageRank, coreness, strongly connected components, edge-list loading)
- C or C++ code that needs a broad, maintained algorithm catalogue (community detection, centralities, isomorphism, generators) and can accept GPL-2.0-or-later
- Build-once, query-many workloads: create the graph from one edge vector in bulk, then run many whole-graph algorithms
- When an accurate PageRank matters: the default PRPACK path solves to a 1e-10 tolerance regardless of the eps argument

## Skip it when

- Peak single-machine speed on large graphs: in the same 2020 table graph-tool, NetworKit and LightGraphs beat igraph on nearly every algorithm (Pokec PageRank 23.39 s vs 1.1 / 0.21 / 0.24 s) and SNAP is faster on PageRank and Google shortest path
- Proprietary or permissively licensed products: GPL-2.0-or-later is copyleft
- Graphs edited one edge at a time: the sorted oi/ii indexes and cumulative os/is offsets must be maintained on every change (inferred from the igraph_t layout), so batch edits
- Many tiny queries on a huge weighted graph: fixed per-call checks can dominate; open issue #2300 measured A\* on a 10,000-vertex complete graph at 0.014 s without weight validation and 11.8 s with it
- Multi-threaded embedding built without thread-local storage or against external BLAS/ARPACK/GLPK: igraph_error.h says the error-handling stack is likely not thread-safe

## How it is fast

The graph is stored as an indexed edge list: flat integer vectors from/to, sorted index permutations oi/ii and cumulative per-vertex offsets os/is (O(|V|+|E|) memory), so neighbour scans are contiguous array walks in C instead of CPython dict-of-dicts traversals. The algorithms are standard ones compiled to C: Batagelj-Zaversnik O(m) core decomposition (NetworkX's core_number uses the same algorithm in Python), two-pass iterative-DFS strongly connected components, BFS for unweighted shortest paths, and the vendored C++ PRPACK solver for PageRank, with optional OpenMP used notably by PageRank. Most of the measured gap over NetworkX is compiled code versus the interpreter, not an algorithmic novelty.

## Compared with alternatives

Pick igraph over Graaf (a lightweight C++ alternative to Boost.Graph whose own perf benchmarks show it slower than Boost) when you need a large, mature algorithm set with Python/R bindings and can live with GPL; Graaf only makes sense for a small embedded C++ graph container, and neither is the fastest option against NetworKit or graph-tool.

## Integration

| | |
|---|---|
| **Form** | static lib by default (BUILD_SHARED_LIBS OFF) or shared lib, built with CMake; also prebuilt Python wheels (PyPI 'igraph'), the R package and Mathematica IGraph/M |
| **Dependencies** | none mandatory; GMP (mini-gmp fallback), BLAS, LAPACK, ARPACK, GLPK and plfit use system copies or vendored internal ones; optional libxml2 (GraphML), OpenMP and bundled Infomap; flex/bison optional |
| **Minimum toolchain** | C99 plus a C++14 compiler (required since 1.0), CMake 3.18+ |
| **Platforms** | no architecture restriction documented; CI on Azure Pipelines and MinGW; igraph_int_t is 64-bit on 64-bit targets and 32-bit otherwise (IGRAPH_INTEGER_SIZE AUTO) |
| **Thread safety** | IGRAPH_ENABLE_TLS (AUTO, on when the compiler supports thread-local storage) makes igraph globals thread-local and sets IGRAPH_THREAD_SAFE; the build file notes this should really hold only with all-internal dependencies, and igraph_error.h still says error handling is likely not thread-safe |
| **Drop-in for the baseline** | no |

## Gotchas

- The default error handler igraph_error_handler_abort prints a message and aborts the process; embedders must install their own with igraph_set_error_handler and check the returned igraph_error_t codes.
- Edge-list readers create vertices 0..max id, so 1-based or gappy id files gain isolated phantom vertices; this is what made the benchmark's Pokec shortest-path row search from an isolated vertex 0.
- Harness flaw behind the cited PageRank row: python-igraph 0.8.2's default PRPACK implementation ignores eps (its docstring says eps and niter apply only to the old power method; the C core always passes 1e-10), while NetworkX 2.4 stops when the L1 change is below N\*tol, i.e. after one power iteration with tol=1e-3 on these graphs, and SNAP iterates to an L1 change below 1e-3; the 10-15x ratio and SNAP's PageRank lead therefore compare unequal accuracy. A user-supplied eps also does not speed igraph up.
- 1.0 broke the 0.10 API (igraph_integer_t renamed igraph_int_t, PageRank parameter order changed, RNG_BEGIN/RNG_END removed so callers must seed the RNG or call igraph_setup()); the unreleased main branch also fixes an igraph_adjlist_init property-cache bug (IGRAPH_PROP_HAS_MULTI set wrongly) that could make several functions return invalid results.

## Known shortcomings

- Tier B on timlrx/graph-benchmarks (python-igraph 0.8.2 vs NetworkX 2.4), but the Pokec shortest-path row is invalid: the igraph and SNAP scripts start at vertex 0, which is not in the Pokec data (the NetworkX script switches to node '1'), so that row's 9x (0.6 vs 2.3 s) must be dropped. The win is only against pure-Python NetworkX; igraph is slower than graph-tool, NetworKit and LightGraphs in the same suite. No CPU model or flags.
- Enricher: the PageRank row is not like for like (NetworkX 2.4 stops when err &lt; N\*tol, so tol=1e-3 means one power iteration; python-igraph 0.8.2's PRPACK ignores eps and solves to 1e-10; SNAP iterates until the L1 change is below 1e-3), so the 10-15x ratio and SNAP's PageRank lead compare unequal accuracy; the Pokec shortest-path flaw is confirmed. The default error handler aborts the process; open issue #2300 (A\* weight checks 0.014 s vs 11.8 s); 1.0 API break; property-cache HAS_MULTI bug fixed on main only.

## Caveats and trade-offs

Numbers are third-party (timlrx/graph-benchmarks, MIT, 85 stars, 2020) and appear only in the README image runtime_results.png; the linked timlrx.com blog post is egress-blocked here. The win is against pure-Python NetworkX, not a C or C++ library. In the same table igraph is slower than graph-tool, LightGraphs (Julia) and NetworKit on nearly every algorithm (Google PageRank 2.42 s vs 0.36 / 0.06 / 0.10 s; Pokec PageRank 23.39 s vs 1.1 / 0.21 / 0.24 s) and slower than SNAP on PageRank (Google 2.42 vs 2.31 s, Pokec 23.39 vs 8.62 s) and on Google shortest path (0.41 vs 0.26 s); only loading is faster than graph-tool and LightGraphs. Harness flaw on Pokec shortest path: networkx_profile.py starts at node '1' for Pokec (soc-pokec ids are not 0-based; download_data.sh only strips comment lines, no remapping), but igraph_profile.py runs g.shortest_paths([g.vs[0]]) and Graph.Read(format='edges') creates vertices 0..max id, so igraph's 0.6 s is a search from an isolated phantom vertex plus building a 1.6M-entry distance row, not a real traversal; snap_profile.py also asks for node 0. The Pokec shortest-path ratios (about 9x vs NetworkX, 0.6 vs 2.3 s vs SNAP) should not be cited. igraph returns a full 1 x N distance list while NetworkX returns a dict of reachable nodes. Versions are from 2020 (python-igraph 0.8.2 from conda-forge, networkx 2.4, SNAP 5.0.0 on Python 3.7); igraph has changed since. NetworkX loading uses read_edgelist into a DiGraph. Compiler, flags and exact CPU model are not stated, hence tier B not A. Medians over 100 runs (Amazon, Google) or 10 runs (Pokec); NetworkX was run fewer times (count not stated). The category graph-algorithms is a suggestion: the guessed sequence-containers does not fit. [retier] timlrx/graph-benchmarks (python-igraph 0.8.2 vs NetworkX 2.4): win only against pure-Python NetworkX; slower than graph-tool, NetworKit and LightGraphs. Drop the Pokec shortest-path row (igraph and SNAP start at vertex 0, absent from the data). PageRank row compares unequal accuracy (NetworkX one power iteration at tol=1e-3, igraph PRPACK to 1e-10, SNAP L1 1e-3). No CPU model or flags. Default error handler aborts the process; 1.0 API break.

GPL license (copyleft) limits embedding in permissive projects. The C core is called through wrappers (R, Python, Mathematica); the benchmark measures the Python binding, so interpreter overhead and type conversion are included.

## Maintenance

Actively maintained (1.0.0 released with a stable-API versioning policy alongside 0.10.17 on 2025-09-19, then 1.0.1; commits continue on main) with 2.0k stars and widely used R and Python bindings, copyable only into GPL-compatible projects; the cited 2020 numbers carry two harness flaws (the Pokec shortest-path row starts igraph at an isolated phantom vertex, and PageRank pits a 1e-10 PRPACK solve against a single NetworkX power iteration).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (timlrx/graph-benchmarks, MIT, profiling scripts code/igraph_profile.py, code/networkx_profile.py, code/snap_profile.py, run_profiler.sh) with a public median-time table (runtime_results.png) that matches every number in the record; hardware is only 'n1-standard-16, 16 vCPU Haswell 2.3 GHz' with no CPU model and the libraries are conda-forge/pip binaries with no compiler or flags, so not A.
- **Verifier notes:** All table numbers re-checked against runtime_results.png and the profiling scripts; metadata confirmed (2.0k stars, GPL-2.0 file with 'or any later version' source headers, last commit 2026-10-01, not archived). Shortcoming to record: Pokec shortest-path row starts igraph and SNAP at a vertex 0 absent from the dataset while NetworkX starts at node 1, so that row is invalid; the rest of the comparison stands, and igraph trails graph-tool, NetworKit and LightGraphs.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-61 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/timlrx/graph-benchmarks>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/runtime_results.png>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/setup/setup.md>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/run_profiler.sh>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/code/igraph_profile.py>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/code/networkx_profile.py>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/code/snap_profile.py>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/code/benchmark.py>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/data/download_data.sh>
  - <https://github.com/igraph/igraph>
  - <https://github.com/igraph/igraph/commits>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/README.md>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/COPYING>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/include/igraph.h>
- **Sources the enricher read:**
  - <https://github.com/igraph/igraph>
  - <https://github.com/igraph/igraph/releases>
  - <https://github.com/igraph/igraph/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance>
  - <https://github.com/igraph/igraph/issues/2300>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/README.md>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/CONTRIBUTING.md>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/etc/cmake/features.cmake>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/etc/cmake/dependencies.cmake>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/etc/cmake/tls.cmake>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/include/igraph_datatype.h>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/include/igraph_error.h>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/src/centrality/prpack.cpp>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/src/centrality/coreness.c>
  - <https://raw.githubusercontent.com/igraph/igraph/HEAD/src/connectivity/components.c>
  - <https://raw.githubusercontent.com/igraph/igraph/0.8.2/src/prpack.cpp>
  - <https://raw.githubusercontent.com/igraph/python-igraph/0.8.2/src/igraph/__init__.py>
  - <https://raw.githubusercontent.com/igraph/python-igraph/0.8.2/src/_igraph/graphobject.c>
  - <https://pypi.org/pypi/igraph/json>
  - <https://raw.githubusercontent.com/networkx/networkx/networkx-2.4/networkx/algorithms/link_analysis/pagerank_alg.py>
  - <https://raw.githubusercontent.com/networkx/networkx/networkx-2.4/networkx/algorithms/core.py>
  - <https://raw.githubusercontent.com/snap-stanford/snap/master/snap-core/centr.h>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/code/igraph_profile.py>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/code/networkx_profile.py>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/code/snap_profile.py>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/code/benchmark.py>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/run_profiler.sh>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/setup/setup.md>
  - <https://raw.githubusercontent.com/timlrx/graph-benchmarks/HEAD/data/download_data.sh>
  - <https://github.com/networkit/networkit>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/igraph/igraph`) · [data/wave1/enrich/raw/github_com_igraph_igraph.json](../../../data/wave1/enrich/raw/github_com_igraph_igraph.json) (enrichment confidence 0.8)

</details>
