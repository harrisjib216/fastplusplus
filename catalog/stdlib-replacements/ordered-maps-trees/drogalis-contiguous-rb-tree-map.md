# Flat-Map-RB-Tree (dro::FlatMap)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Ordered maps and trees](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0` · 🟡 stale

> Header-only flat red-black tree map/set in a vector; 1.4-1.9x faster than std::map at scale.

| | |
|---|---|
| **Beats** | std::map |
| **Claimed result** | Exact means from the repo's benchmarks/results/\*.txt (charts in README plot the same data): 10,000,000 int32 elements: insert 622 ns vs std::map 855 ns, find 551 ns vs 774 ns, erase 627 ns vs 916 ns; 1,000,000 elements: insert 283 vs 461 ns, find 234 vs 438 ns, erase 281 vs 470 ns (about 1.4-1.9x, derived from page data). Versus boost::flat_map, insert/erase explode past a few thousand elements (1M: 146,200 ns insert) but boost::flat_map FIND is faster than dro::FlatMap at large sizes (1M: 134 ns vs 234 ns), and folly::heap_vector_map find is faster than dro from \~100K elements up per the find chart. |
| **Workload** | mean random-insertion and mean random-find time for int32 keys, container sizes swept from 100 to 10,000,000 elements; std::map, boost::flat_map, and folly::heap_vector_map plotted alongside dro::FlatMap |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-9300H CPU @ 2.40GHz (4 cores), isolcpus enabled on cores 2 and 3, Linux kernel 6.10.11-200.fc40.x86_64 |
| **Compiler and flags** | gcc 14.2.1, CMAKE_BUILD_TYPE=Release |
| **Adoption** | 14 stars |
| **Last commit** | 2024-11-16 |
| **Links** | [repository](https://github.com/drogalis/contiguous-rb-tree-map) · [benchmark](https://github.com/drogalis/contiguous-rb-tree-map/blob/main/README.md) |

## Verdict

On gcc 14.2.1 with libstdc++, -DCMAKE_BUILD_TYPE=Release, on an isolcpus-pinned Intel Core i5-9300H (4 cores), dro::FlatMap beat std::map at 10,000,000 int32 elements: insert 622ns vs 855ns, find 551ns vs 774ns, erase 627ns vs 916ns (\~1.4-1.9x across sizes); numbers are from the repo's committed benchmarks/results/\*.txt, not chart-reading.

## Use it when

- Insert/find/erase-heavy workloads on int32-like keys where std::map's per-node allocation dominates, especially at 1M-10M elements (1.4-1.9x measured gain).
- You can pick a MaxSize index type (uint8_t-uint64_t) matching your expected element count for space efficiency.
- Keys/values are default-constructible and you don't need pointer/reference stability across inserts/erases.
- You want ordered iteration plus a map-like API without accepting flat_map's insert/erase cost.

## Skip it when

- Find-dominated workloads at large sizes: boost::flat_map find is faster than dro::FlatMap by 1M elements (134ns vs 234ns), and folly::heap_vector_map overtakes dro on find from \~100K elements.
- Code that holds iterators across modifying operations: every insert/erase/clear invalidates ALL iterators, not just erased ones.
- Long-lived containers with heavy erase churn: erased slots stay allocated until shrink_to_fit() or destruction, so memory can grow unbounded between compactions.
- Key/value types that aren't default-constructible.
- Production use requiring maturity: project is self-labeled Beta Testing with \~50% test coverage and has no issue-tracker history to gauge stability (issue tracker is empty).

## How it is fast

Storing nodes in a vector keeps the tree cache-contiguous and lets the implementation prefetch the next probed level during binary search on insert/erase, cutting cache misses versus a pointer-chasing red-black tree. Rotations swap node and child slots in place rather than relocating via pointers, and erase swaps the deleted key with the in-order successor then moves it to the vector's end instead of freeing/reallocating a node.

## Compared with alternatives

Pick over boost::container::flat_set/flat_map when insert/erase throughput matters more than find at scale (boost::flat_map degrades sharply on insert/erase, e.g. 146,200ns at 1M vs dro's 283ns), but pick boost::flat_map instead if find dominates. Versus fast-containers or frozenca/BTree (larger, more mature B-tree alternatives with wider verified gains), dro::FlatMap is a smaller header-only option but is explicitly beta with \~50% test coverage.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only: &lt;vector&gt;, &lt;stdexcept&gt;, &lt;concepts&gt;, &lt;type_traits&gt;, etc.) |
| **Minimum toolchain** | C++20 per README; repo's own CMakeLists.txt builds with C++23 |
| **Platforms** | not documented (no architecture-specific intrinsics in the header; no platform restrictions stated) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — API mirrors std::map/std::set (at, operator[], find, insert, erase, iterators) but requires default-constructible key/value, invalidates all iterators on any modification, and doesn't auto-deallocate erased slots |

## Gotchas

- All iterators are invalidated by any modifying operation (insert/erase/clear/swap), not just iterators to erased elements as in std::map.
- erase() does not free memory; call shrink_to_fit() or destroy the container to reclaim space from erased slots.
- Key and Value types must be default-constructible in addition to copy/move-assignable.
- The MaxSize template parameter (an integral type) bounds max_size() and throws std::runtime_error if the container grows past it.

## Caveats and trade-offs

Charts are PNG but exact numbers are in benchmarks/results/\*.txt; each size is a single run reporting mean ns/op over the op count with no variance; only one hardware/compiler configuration (libstdc++ via gcc 14.2.1); project is self-described beta (\~50% test coverage); the 'faster than boost::flat_map' claim applies to insert/erase only, not find.

any modifying operation invalidates ALL iterators (std::map only invalidates iterators to erased elements); erased slots are not deallocated until shrink_to_fit() or destruction; key and value types must be default-constructible; author labels the project "Beta Testing" with \~50% test coverage

## Maintenance

Stale: last commit 2024-11-16, GPL-3.0, and the project self-labels 'Beta Testing' with \~50% coverage — usable as a copyable single header, but treat as unmaintained and verify against current libstdc++ before relying on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public benchmark code benchmarks/flat-rb-tree-benchmark.cpp times dro::FlatMap vs std::map (plus boost/folly); README states gcc 14.2.1, -DCMAKE_BUILD_TYPE=Release, and Intel Core i5-9300H with isolcpus; exact per-size results are committed as text in benchmarks/results/\*.txt, so A holds.
- **Verifier notes:** Chart readings in the record were close to the committed text results (e.g. 10M find 551 vs 774 ns); corrected to exact values and fixed the overstated boost::flat_map find claim. Metadata verified: GPL-3.0, 14 stars, last commit 2024-11-16 (stale), not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/drogalis/contiguous-rb-tree-map/blob/main/README.md>
  - <https://github.com/drogalis/contiguous-rb-tree-map>
  - <https://github.com/drogalis/contiguous-rb-tree-map/blob/main/benchmarks/results/1_000_000_elem.txt>
  - <https://github.com/drogalis/contiguous-rb-tree-map/blob/main/benchmarks/results/10_000_000_elem.txt>
  - <https://github.com/drogalis/contiguous-rb-tree-map/blob/main/benchmarks/flat-rb-tree-benchmark.cpp>
  - <https://github.com/drogalis/contiguous-rb-tree-map/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/drogalis/contiguous-rb-tree-map/blob/main/cmake/Sanitizers.cmake>
  - <https://raw.githubusercontent.com/drogalis/Flat-Map-RB-Tree/refs/heads/main/assets/Average%20Random%20Insertion%20Time.png>
  - <https://raw.githubusercontent.com/drogalis/Flat-Map-RB-Tree/refs/heads/main/assets/Average%20Random%20Find%20Time.png>
- **Sources the enricher read:**
  - <https://github.com/drogalis/contiguous-rb-tree-map>
  - <https://github.com/drogalis/contiguous-rb-tree-map/blob/main/README.md>
  - <https://github.com/drogalis/contiguous-rb-tree-map/blob/main/CMakeLists.txt>
  - <https://github.com/drogalis/contiguous-rb-tree-map/blob/main/include/dro/flat-rb-tree.hpp>
  - <https://github.com/drogalis/contiguous-rb-tree-map/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/drogalis/contiguous-rb-tree-map`) · [data/wave1/enrich/raw/github_com_drogalis_contiguous_rb_tree_map.json](../../../data/wave1/enrich/raw/github_com_drogalis_contiguous_rb_tree_map.json) (enrichment confidence 0.7)

</details>
