# Hash maps and sets

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::unordered_map, std::unordered_set  
**27 entries:** 18 tier A · 1 tier B · 8 tier C · 0 tier D · 26 copyable, 1 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**folly F14 (F14ValueMap)**](facebook-folly.md) | SIMD 14-way probing hash map (F14) in Facebook's Folly library; 2-4x faster build/find/churn, 16x faster iteration than std::unordered_map. | **A** | C++ | Apache-2.0 | 🟢 active |
| 2 | [**abseil (absl::flat_hash_map, Swiss tables)**](abseil-abseil-cpp.md) | SwissTable-based hash map beating std::unordered_map on build, find, churn, and iteration speed. | **A** | C++ | Apache-2.0 | 🟢 active |
| 3 | [**EASTL hash_map / hash_set (eastl::hash_map)**](paper-eastl-hash-map-hash-set.md) | EA's chained hash table (eastl::hash_map/hash_set), about 1.3x faster than libstdc++ std::unordered_map in Ankerl's 2019 suite. | **A** | C++ | BSD-3-Clause | 🟢 active |
| 4 | [**uthash**](troydhanson-uthash.md) | Header-only intrusive C hash table (macros); in one third-party benchmark it iterates and erases faster than std::unordered_map but loses most lookups. | **A** | C | BSD-1-Clause | 🟢 active |
| 5 | [**klib khash (khash.h)**](attractivechaos-klib.md) | Single-header C macro hash table (open addressing, 2-bit flags); about 4x less CPU and 3x less memory than std::unordered_map on integer counting. | **A** | C | MIT | 🟢 active |
| 6 | [**tsl::robin_map (Tessil/robin-map)**](tessil-robin-map.md) | Header-only robin hood open-addressing hash map/set beating std::unordered_map on insert, lookup, erase, and iteration. | **A** | C++ | MIT | 🟢 active |
| 7 | [**ankerl::unordered_dense**](martinus-unordered-dense.md) | Vector-backed hash map beating std::unordered_map on build, iteration, and string-key workloads, with weaker reference stability. | **A** | C++ | MIT | 🟢 active |
| 8 | [**sparsepp (spp::sparse_hash_map, greg7mdp/sparsepp)**](greg7mdp-sparsepp.md) | Header-only open-addressing hash map/set beating std::unordered_map on memory and, per two independent suites, speed. | **A** | C++ | BSD-3-Clause | 🟢 active |
| 9 | [**M\*LIB (m-dict hash map, DICT_DEF2)**](p-p-h-d-mlib.md) | Header-only C99/C11 generic container library whose DICT_DEF2 hash map ran 12.6x faster than libstdc++ std::unordered_map in its author's harness. | **A** | C | BSD-2-Clause | 🟢 active |
| 10 | [**tsl::hopscotch_map (Tessil/hopscotch-map)**](tessil-hopscotch-map.md) | Header-only C++17 hopscotch-hashing hash map/set, faster than std::unordered_map with dense_hash_map-like speed. | **A** | C++ | MIT | 🟢 active |
| 11 | [**emhash (ktprime/emhash: emhash5/6/7/8 + emilib)**](ktprime-emhash.md) | Header-only open-addressing C++ hash table family; emhash7 beats std::unordered_map on insert/find/erase/iterate at 10M elements. | **A** | C++ | MIT | 🟢 active |
| 12 | [**tsl::ordered_map (Tessil/ordered-map)**](tessil-ordered-map.md) | Insertion-order-preserving hash map/set beating std::unordered_map on inserts, misses, and iteration. | **A** | C++ | MIT | 🟢 active |
| 13 | [**Boost.Unordered (boost::unordered_flat_map)**](boostorg-unordered.md) | Header-only SIMD open-addressing hash map/set for Boost; unordered_flat_map is 2.7x-11.6x faster than std::unordered_map. | **A** | C++ | BSL-1.0 | 🟢 active |
| 14 | [**Verstable**](jacksonallan-verstable.md) | Single-header C hash table beating std::unordered_map on lookups, erasures, and iteration; insertion only average. | **A** | C | MIT | 🟡 stale |
| 15 | [**tsl::array_map / array-hash (Tessil)**](tessil-array-hash.md) | Header-only cache-conscious string hash map/set (Askitis array hash); about half the memory of std::unordered_map&lt;std::string,T&gt;, 1.3-2.3x faster lookups. | **A** | C++ | MIT | 🟡 stale |
| 16 | [**ska::flat_hash_map / ska::bytell_hash_map**](skarupke-flat-hash-map.md) | Header-only Robin Hood open-addressing hash map/set beating std::unordered_map on lookups, inserts, and erases. | **A** | C++ | BSL-1.0 | 🔴 abandoned |
| 17 | [**robin_hood::unordered_map**](martinus-robin-hood-hashing.md) | Header-only, single-file open-addressing hash map/set beating std::unordered_map on speed and memory. | **A** | C++ | MIT | 🔴 abandoned |
| 18 | [**google::dense_hash_map (sparsehash)**](sparsehash-sparsehash.md) | Open-addressing C++ hash map beating std::unordered_map on lookups/inserts at large memory cost. | **A** | C++ | BSD-3-Clause | 🔴 abandoned |
| 19 | [**libcuckoo (cuckoohash_map, efficient/libcuckoo)**](efficient-libcuckoo.md) | Header-only concurrent cuckoo hash map with per-bucket locks; beats std::unordered_map only under real multi-core contention. | **B** | C++ | Apache-2.0 | 🟢 active |
| 20 | [**parallel-hashmap (phmap)**](greg7mdp-parallel-hashmap.md) | Header-only, Abseil-derived flat/node hash maps and a btree; drop-in for std::unordered_map/map, \~3x faster inserts. | **C** | C++ | Apache-2.0 | 🟢 active |
| 21 | [**CCAN htable (ccan/htable)**](rustyrussell-ccan.md) | Compact C open-addressing hash table of object pointers with hash bits folded into spare pointer bits; beats JudyL on random lookups. | **C** | C | LGPL-2.1-or-later | 🟢 active |
| 22 | [**Ultimate++ (U++ Core: VectorMap, String, Stream, heap)**](ultimatepp-ultimatepp.md) | U++ framework's VectorMap/Index hash containers plus String and heap; 1.8-2.4x over std::unordered_map in a first-party word-index test. | **C** | C++ | BSD-2-Clause | 🟢 active |
| 23 | [**Direct-indexed std::array maps in the matching-engine order…**](paper-book-building-low-latency-applications-with-cpp-array-indexed-or-2516eccb.md) | Matching-engine order book using preallocated direct-indexed std::array maps instead of std::unordered_map; about 7% fewer cycles in the book's run. | **C** | C++ | MIT | 🟢 active |
| 24 | [**fastcpp::flat_hash_map (developer source)**](private-developer-source-hash-maps-sets.md) | Header-only SwissTable-style hash map: 1.8-5.5x faster than std::unordered_map on 1M uint64 keys, but slower than phmap on lookups. | **C** | C++ | MIT | 🟢 active |
| 25 | [**SIGMOD 2025 Contest Solution - Hash Join Pipeline (Robin…**](ariss44-sigmod-2025-contest-solution.md) | Coursework hash-join pipeline: four custom open-addressing tables plus a columnar 'Unchained' design that beat std::unordered_map on an IMDB join benchmark. | **C** | C++ | MIT | 🟢 active |
| 26 | [**rigtorp/HashMap**](rigtorp-hashmap.md) | Header-only open-addressing hash map with backshift deletion, up to \~5x faster than std::unordered_map on delete-heavy workloads. | **C** | C++ | MIT | 🟡 stale |
| 27 | [**CYBHash**](chenyibo1029-cybhash.md) | Header-only bit-packing + BMI2 pext lookup for fixed-format Chinese futures/stock/option ticker symbols, vs std::unordered_map. | **C** | C++ | no license (study only) | 🟡 stale |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
