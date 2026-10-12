# Ordered maps and trees

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::map, std::set, std::multimap  
**10 entries:** 4 tier A · 0 tier B · 5 tier C · 1 tier D · 9 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**fast-containers (SIMD/hugepage B+Tree)**](kressler-fast-containers.md) | Header-only C++23 B+tree with SIMD search and hugepage allocators, 2-5x faster than std::map on large trees. | **A** | C++ | BSD-3-Clause | 🟢 active |
| 2 | [**tlx::btree_map / btree_set / btree_multimap (STX B+Tree…**](tlx-tlx.md) | Header-only B+ tree implementing STL's map/set/multimap/multiset; beats libstdc++'s red-black tree at large n. | **A** | C++ | BSL-1.0 | 🟡 stale |
| 3 | [**Flat-Map-RB-Tree (dro::FlatMap)**](drogalis-contiguous-rb-tree-map.md) | Header-only flat red-black tree map/set in a vector; 1.4-1.9x faster than std::map at scale. | **A** | C++ | GPL-3.0 | 🟡 stale |
| 4 | [**S+ tree (Algorithmica static B-tree array layout)**](sslotin-amh-code.md) | SIMD (AVX2) static B+-tree array layout beating std::lower_bound/std::set on batched int32 lookups. | **A** | C++ | no license (study only) | 🔴 abandoned |
| 5 | [**boost::container::flat_set / flat_map**](boostorg-container.md) | Vector-backed sorted set/map beating std::set on insert+remove at small sizes, up to \~256 elements. | **C** | C++ | BSL-1.0 | 🟢 active |
| 6 | [**RadixMap (radix-map)**](lrmoorejr-radix-map.md) | Header-only PATRICIA/radix-tree map beating std::map on insert/contains for string and numeric keys. | **C** | C++ | Apache-2.0 | 🟢 active |
| 7 | [**frozenca/BTree**](frozenca-btree.md) | Header-only C++20 B-tree (BTreeSet/Map) with optional AVX-512 SIMD search, \~5x faster than std::set on int64 keys. | **C** | C++ | Apache-2.0 WITH… | 🟡 stale |
| 8 | [**libart (Adaptive Radix Tree)**](armon-libart.md) | C99 Adaptive Radix Tree: ordered byte-key map/set, algorithmically faster than red-black trees (std::map's structure). | **C** | C | BSD-3-Clause | 🔴 abandoned |
| 9 | [**cpp-btree (Kronuz)**](kronuz-cpp-btree.md) | Header-only B-tree replacement for std::map/set/multimap/multiset with C++17 try_emplace API and lower per-element memory. | **C** | C++ | Apache-2.0 | 🔴 abandoned |
| 10 | [**itlib small and flat containers (itlib::flat_map…**](ibob-itlib.md) | Single-header C++11 flat_map/flat_set (sorted vector) plus small_vector and static_vector; claims to beat std::map for small sizes, unmeasured. | **D** | C++ | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
