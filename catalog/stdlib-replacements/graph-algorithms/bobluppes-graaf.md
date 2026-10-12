# Graaf

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Graph algorithms](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 graph library positioned as a lighter Boost.Graph alternative; measured slower than Boost.Graph on every benchmarked algorithm.

| | |
|---|---|
| **Beats** | Boost Graph Library (Boost.Graph 1.84.0, via the perf/boost benchmarks for Dijkstra, BFS, Kruskal, Prim, greedy and Welsh-Powell colouring) |
| **Claimed result** | NO SPEEDUP CLAIMED, AND THE NUMBERS SHOW GRAAF IS SLOWER. README says only 'doesn't sacrifice on performance' and 'lightweight alternative to the Boost Graph Library'. Pull-request numbers (web_google / web_berkstan, Graaf time relative to Boost) after the September 2026 vector-storage optimisations: Kruskal 1.14x / 1.60x slower (PR #451, was 3.48x / 3.20x); Prim 2.01x / 1.85x slower (PR #452); greedy colouring 2.13x / 7.70x slower (PR #455); Welsh-Powell 2.59x / 5.71x slower (PR #456); BFS 3.55x / 8.65x slower (PR #449); Dijkstra single path 4.38x / 12.56x slower (PR #453, still open when read); dijkstra_shortest_paths 6.94x / 17.01x slower (PR #454). Initial comparison (PR #419): Graaf 13.39 s vs Boost 1.33 s on web-Google and 14.11 s vs 0.69 s on web-BerkStan. |
| **Workload** | Graaf's perf/ executables (Google Benchmark v1.8.2, Release build) running the same algorithms in Graaf and in Boost.Graph on SNAP web-Google and web-BerkStan edge lists; per-algorithm ratios are quoted in the project's own pull requests. |
| **Metric** | throughput |
| **Compiler and flags** | Release build; compiler and flags not stated in the PRs (their tests ran on g++-12 and clang++-16 in Debug mode) |
| **Adoption** | 420 stars, 68 forks |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/bobluppes/graaf) · [benchmark](https://github.com/bobluppes/graaf/pull/451) |

## Verdict

Graaf's own pull requests (#419, #449, #451-#456) time Graaf against Boost.Graph 1.84.0 adjacency_list&lt;vecS, vecS, undirectedS&gt; with Google Benchmark v1.8.2 in a Release build on SNAP web-Google and web-BerkStan with unit weights; after the September 2026 vector-storage PRs Graaf remains slower everywhere, from 1.14x (Kruskal, web-Google) to 17.01x (all-targets Dijkstra, web-BerkStan; Graaf 14.54 s vs about 0.85 s for Boost, derived from page data). No CPU, compiler version or flags beyond 'Release' are stated.

## Use it when

- Small to medium graphs (thousands to low hundreds of thousands of edges) where readable code and user-defined vertex/edge structs matter more than raw speed.
- Teaching, prototyping or tooling where you want a one-include, dependency-free C++20 library with DOT output instead of Boost's property-map and visitor machinery.
- Code that needs the full path to every vertex from Dijkstra or A\* returned as a ready-made container rather than reconstructed from a predecessor map.
- Projects that cannot take a Boost dependency but need the common textbook algorithms (MST, SCC, topological sort, colouring, cliques, PageRank).

## Skip it when

- Any throughput-sensitive workload: on SNAP web-Google and web-BerkStan the project's own numbers put it 1.14x (Kruskal) to 17.01x (all-targets Dijkstra) slower than Boost.Graph 1.84 adjacency_list&lt;vecS, vecS, undirectedS&gt;.
- Large weighted graphs: every edge-weight read goes through an unordered_map&lt;pair, edge_t&gt; lookup, and dijkstra_shortest_paths returns a std::list per reachable vertex, so memory grows with the sum of all path lengths.
- When you need Boost.Graph features such as property maps, visitors, max-flow, isomorphism, betweenness or articulation points (max-flow, articulation points, centrality and isomorphism are open feature issues #331, #332, #337, #338).
- Concurrent use: thread-safety guarantees are undocumented (issue #323, marked stale), and CI covers Linux only (Windows/macOS CI is open issue #322).
- If you need a stable, released version of the faster code: the September 2026 vector-storage work is unreleased (latest release v1.2.0 of 12 Sep 2026, 186 commits behind main).

## How it is fast

It is not faster than its named baseline. Since September 2026 the graph keeps vertices and neighbour lists in dense std::vector storage indexed by vertex id (PRs #434, #438, #442, #446) and the algorithms replaced unordered_map/unordered_set bookkeeping with lazily grown vectors (BFS uses vector&lt;bool&gt;, Kruskal a vector-backed union-find with union by rank and path compression, Prim and Dijkstra binary heaps with lazy deletion). Edge payloads still live in one std::unordered_map keyed by the (sorted) vertex pair, so every weighted relaxation does a hash lookup (open issue #444), and dijkstra_shortest_paths materialises a std::list path for every reachable vertex, which is where most of its 7-17x gap comes from.

## Compared with alternatives

No siblings catalogued yet; against its own named baseline, pick Boost.Graph whenever speed matters and Graaf only when the simpler API and zero dependencies are worth a 1.1-17x slowdown.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library (fmt was removed in #305); the perf/ and test/ builds fetch Google Benchmark v1.8.2, fmt 9.1.0, GoogleTest and, opt-in, Boost 1.84.0 |
| **Minimum toolchain** | C++20 (CMakeLists sets CMAKE_CXX_STANDARD 20; CI tests g++-12 and clang++-16; v1.2.0 notes include fixes for gcc-14 and gcc 16 / clang 23 includes) |
| **Platforms** | any platform with a C++20 compiler in principle; CI is Linux only |
| **Thread safety** | not documented (issue #323 'Document thread-safety guarantees' is open and stale); algorithms take the graph by const reference and allocate their own state |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the Boost single-pair Dijkstra benchmark (PR #453 numbers): perf/boost/utils/farthest_vertex.cpp picks std::max_element over Boost's distance map, but the Boost graph is pre-sized to max dataset id + 1 and unreachable vertices keep distance std::numeric_limits&lt;int&gt;::max(), so the chosen 'farthest' target is an unreachable vertex; the stop_at_target_visitor never fires and Boost always runs a full single-source Dijkstra, while Graaf (whose dijkstra_shortest_paths map only holds reachable vertices) stops at the true farthest vertex. The bias works against Boost, so the 4.38x / 12.56x gap is if anything understated; the shared-source perf/common code otherwise builds identical edge lists for both libraries. A smaller bias the other way: the Boost Welsh-Powell benchmark re-sorts one persistent order vector inside the timed loop, so after the first iteration it sorts already-sorted input.
- The full-graph BFS and Dijkstra benchmarks pass start vertex 1 to both libraries, but the Boost reader uses raw dataset ids while the Graaf reader remaps ids in first-seen order, so Graaf's vertex 1 is the second distinct id in the file, not dataset node 1; both very probably sit in the giant component (855,802 of 875,713 vertices in web-Google, 654,782 of 685,230 in web-BerkStan per the repo's own comment), so the effect should be small. The Prim benchmark avoids this by remapping inside perf/common/connected_subgraph.h, and its comment ('re-scans every fringe vertex's neighbor list') is stale since #387 switched Prim to a binary heap, which is why it still runs on capped 85,000/80,000-vertex subgraphs.
- add_edge throws std::invalid_argument when either vertex is missing or when the edge already exists (update in place via get_edge instead); dijkstra throws on a negative edge weight; prim_minimum_spanning_tree returns std::nullopt for a disconnected graph instead of a spanning forest.
- README installs from the release page, which ships v1.2.0 without the September 2026 vector-storage changes; the perf comparison against Boost is opt-in (GRAAF_BUILD_BOOST_PERF and GRAAF_DOWNLOAD_PERF_DATASETS, both OFF) and the web-BerkStan download points at snap-sentiment.stanford.edu rather than snap.stanford.edu (not checked here).

## Known shortcomings

- Not faster than Boost.Graph 1.84.0 on any algorithm (1.14x-17.01x slower) in its own first-party PR numbers (no CPU or compiler); PR #449's BFS gap figures do not match its own timings and #453 is still open; all perf PRs carry a Claude co-author trailer. No spec category fits (kept under the off-spec graph-algorithms label; nearest is wave 8 sparse-and-solvers).
- Enricher: perf/boost/utils/farthest_vertex.cpp runs max_element over Boost's distance map, where unreachable vertices hold INT_MAX, so it picks an unreachable target and Boost's single-pair Dijkstra (PR #453, now merged) always runs full SSSP (bias against Boost, so the gap is if anything understated); BFS/Dijkstra start vertex 1 is not the same node in both libraries (Boost uses the raw dataset id, Graaf remaps ids in order seen); the Boost Welsh-Powell loop re-sorts an already-sorted vector. Perf work is unreleased (v1.2.0 of 2026-09-12 is 186 commits behind main); dijkstra_shortest_paths builds a std::list path per reachable vertex.

## Caveats and trade-offs

FLAGGED NOT FASTER: every numeric comparison against the named baseline (Boost.Graph 1.84.0) shows Graaf slower, from 1.14x (Kruskal, web_google) to 17.01x (dijkstra_shortest_paths, web_berkstan); the README claims only a lightweight, easy-to-use alternative that 'doesn't sacrifice on performance'. The numbers are first-party PR descriptions with no hardware, no compiler version and no flags beyond 'Release' (the g++-12 and clang++-16 mentions refer to Debug test runs). The Boost comparison executable is opt-in (GRAAF_BUILD_BOOST_PERF, off by default); it uses boost::adjacency_list&lt;vecS, vecS, undirectedS&gt; and builds the graph outside the timed loop, as the Graaf benchmarks do, so the harness is like-for-like at a glance. The BFS gap figures in PR #449 do not match its own before/after timings: the implied Boost BFS time is about 672 ms before vs 374 ms after on web_google and about 229 ms vs 170 ms on web_berkstan (derived from page data), so the Boost reference was not stable between runs; the other PRs' gap ratios are internally consistent. PR #453 (dijkstra_shortest_path vector storage) was still open when read on 2026-10-07. Every perf PR in the series (#449, #451-#456) and the later commits carry a Claude co-author trailer (not only #454). The gaps are moving quickly (perf PRs merged 2026-09-19 to 2026-09-27, last commit 2026-09-28), so later commits may close more of the gap. Kept as a record only so the catalogue can show the evidence is negative. Category: graph-algorithms is not a spec category.

Header-only C++20, general user-defined vertex and edge types, free-function algorithms, DOT output; storage is hash-map based (unordered_map keyed by vertex id) which the ongoing perf PRs are replacing with vectors internally while keeping unordered_map return types. Smaller algorithm set than Boost.Graph.

## Maintenance

Actively developed (last commit 2026-09-28, a burst of perf PRs 2026-09-18 to 2026-09-27, several with a Claude co-author trailer) and MIT-licensed, so copyable, but the performance work is unreleased and the library is a convenience alternative to Boost.Graph, not a faster one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers in the project's own PR descriptions (#419, #449, #451-#456) from public benchmark code (perf/graaflib/\*_benchmark.cpp vs perf/boost/\*_benchmark.cpp, Google Benchmark v1.8.2, Boost 1.84.0 tarball pinned in perf/CMakeLists.txt), but no CPU model, compiler version or flags beyond 'Release' are stated, so not A; every number shows Graaf slower than Boost.Graph.
- **Verifier notes:** Numbers all match the PRs (#419: Graaf 13.39 s vs Boost 1.33 s on web-Google, 14.11 s vs 0.69 s on web-BerkStan; latest gaps 1.14x-17.01x slower). Shortcomings to record: not faster than Boost.Graph on any algorithm; first-party, no CPU/compiler/flags; BFS gap in #449 inconsistent with its own timings; #453 unmerged. Category: no spec category fits a general graph-algorithms library; the nearest existing one is wave 8 sparse-and-solvers, which already holds graph-analytics entries (gunrock/graphblast, algebraic-programming/alp benchmarked on BFS/SSSP against SuiteSparse:GraphBLAS), but Graaf is a container-plus-algorithms library with Boost.Graph as its baseline, so either keep graph-algorithms as an off-spec category (baseline Boost Graph Library) or file it under sparse-and-solvers by override.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party PRs (verifier, not faster); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/bobluppes/graaf>
  - <https://github.com/bobluppes/graaf/commits>
  - <https://github.com/bobluppes/graaf/pull/451>
  - <https://github.com/bobluppes/graaf/pull/419>
  - <https://github.com/bobluppes/graaf/pull/449>
  - <https://github.com/bobluppes/graaf/pull/452>
  - <https://github.com/bobluppes/graaf/pull/453>
  - <https://github.com/bobluppes/graaf/pull/454>
  - <https://github.com/bobluppes/graaf/pull/455>
  - <https://github.com/bobluppes/graaf/pull/456>
  - <https://github.com/bobluppes/graaf/tree/main/perf>
  - <https://github.com/bobluppes/graaf/tree/main/perf/boost>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/breadth_first_search_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/breadth_first_search_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/utils/dataset_reader.h>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/README.md>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/common/dataset.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/common/dataset_dir.h.in>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/common/connected_subgraph.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/utils/dataset_reader.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/utils/dataset_reader.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/utils/connected_subgraph.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/utils/connected_subgraph.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/utils/farthest_vertex.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/utils/farthest_vertex.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/breadth_first_search_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/dijkstra_shortest_paths_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/dijkstra_shortest_path_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/kruskal_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/prim_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/greedy_graph_coloring_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/boost/welsh_powell_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/utils/dataset_reader.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/utils/dataset_reader.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/utils/connected_subgraph.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/utils/connected_subgraph.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/utils/farthest_vertex.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/utils/farthest_vertex.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/breadth_first_search_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/dijkstra_shortest_paths_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/dijkstra_shortest_path_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/kruskal_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/prim_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/greedy_graph_coloring_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/perf/graaflib/welsh_powell_benchmark.cpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/include/graaflib/types.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/include/graaflib/graph.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/include/graaflib/graph.tpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/include/graaflib/edge.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/include/graaflib/algorithm/graph_traversal/breadth_first_search.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/include/graaflib/algorithm/graph_traversal/breadth_first_search.tpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/include/graaflib/algorithm/shortest_path/dijkstra_shortest_paths.tpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/include/graaflib/algorithm/shortest_path/common.h>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/include/graaflib/algorithm/minimum_spanning_tree/kruskal.tpp>
  - <https://raw.githubusercontent.com/bobluppes/graaf/HEAD/include/graaflib/algorithm/minimum_spanning_tree/prim.tpp>
  - <https://github.com/bobluppes/graaf/tree/main/perf>
  - <https://github.com/bobluppes/graaf/pull/452>
  - <https://github.com/bobluppes/graaf/pull/453>
  - <https://github.com/bobluppes/graaf/pull/454>
  - <https://github.com/bobluppes/graaf/commits>
  - <https://github.com/bobluppes/graaf/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/bobluppes/graaf/issues>
  - <https://github.com/bobluppes/graaf/releases>
  - <https://github.com/bobluppes/graaf/releases/latest>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/bobluppes/graaf`) · [data/wave1/enrich/raw/github_com_bobluppes_graaf.json](../../../data/wave1/enrich/raw/github_com_bobluppes_graaf.json) (enrichment confidence 0.75)

</details>
