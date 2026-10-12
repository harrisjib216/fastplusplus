# robin_hood::unordered_map

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only, single-file open-addressing hash map/set beating std::unordered_map on speed and memory.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | Insert & Erase 100M int, both maps using robin_hood::hash: robin_hood::unordered_flat_map 16.9s / 1717MB vs std::unordered_map 99.7s / 3986MB (5.9x faster); robin_hood::unordered_node_map 45.5s / 2293MB (2.2x faster) (derived from page data) |
| **Workload** | Author's 2019 multi-map benchmark series (map_benchmark): insert/clear/reinsert/erase of 100M int pairs, random insert/erase of uint64_t and std::string, successful/unsuccessful find over 1-2000, 1-500k uint64_t and 1-1M std::string keys, and iteration; each map run with 5 hashes (robin_hood::hash, absl::Hash, FNV1a, libstdc++ std::hash, folly::hasher), median of 9 runs. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-8700 @ 3.20GHz, locked to 3200MHz (per benchmark-series overview page) |
| **Compiler and flags** | g++ 8.2.0, -O3 -march=native, CMake Release build (stated on the benchmark-series overview page, not in the robin-hood-hashing repo itself) |
| **Adoption** | 1.62k stars |
| **Last commit** | 2023-04-21 |
| **Links** | [repository](https://github.com/martinus/robin-hood-hashing) · [benchmark](https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-03-01-result-InsertHugeInt/) |

## Verdict

On the author's 2019 map_benchmark suite (g++ 8.2.0, -O3 -march=native, libstdc++ std::unordered_map as baseline, Intel Core i7-8700 @3.2GHz locked), robin_hood::unordered_flat_map inserted+erased 100M int pairs in 16.9s using 1717MB vs. std::unordered_map's 99.7s / 3986MB (5.9x faster, \~2.3x less peak memory), both using robin_hood::hash; robin_hood::unordered_node_map took 45.5s / 2293MB (2.2x faster). Numbers are first-party, from a 2019-era g++ 8.2/libstdc++ toolchain.

## Use it when

- Hot-path integer- or string-keyed maps/sets where insert/erase/find throughput dominates and you use robin_hood::hash (or another well-mixed hash)
- Large bulk workloads (tens of millions of entries) where std::unordered_map's per-node allocation and pointer chasing dominate runtime and RSS
- You want a drop-in std::unordered_map-shaped API without rewriting call sites: unordered_flat_map for max speed, unordered_node_map when pointer/reference stability is required
- Header-only vendoring is acceptable (single \~2500-line file, MIT) and you're fine freezing on an unmaintained snapshot
- C++11/14/17/20 codebase, including non-x86/non-AVX platforms, since the implementation is portable scalar C++

## Skip it when

- You need iterator stability across inserts — neither variant guarantees it, and unordered_flat_map also invalidates references/pointers on rehash
- You rely on a poorly-mixed or identity hash for integer keys (e.g. libstdc++'s default std::hash&lt;int&gt;) — the record's own caveats note robin_hood times out in several benchmarks without its own hash, and a badly mixed hash can make insert throw std::overflow_error
- Your workload spikes memory and then shrinks — unordered_node_map's bulk allocator never returns freed blocks to the OS for the life of the map, so peak RSS persists (GitHub issue #107)
- You need heterogeneous/transparent lookup (e.g. find by string_view into a map&lt;std::string,...&gt;) — attempts to use it hit unresolved problems per an open issue (#80)
- You need active maintenance, custom-allocator support, or a cheap operator= — the repo is archived since 2023 (author recommends ankerl::unordered_dense), custom allocators aren't supported (issue #136, closed unimplemented), and copy-assignment has an open perf bug where it frees then reallocates instead of reusing the buffer (issue #149)

## How it is fast

Open addressing with Robin Hood hashing bounds probe-sequence-length variance, and backward-shift deletion removes the need for tombstones, so there's no per-node allocation or pointer chasing on the hot path. Each slot carries a 1-byte 'info' field packing probe distance plus hoisted hash bits, so most negative lookups are rejected without a full key comparison; the flat layout keeps keys/values contiguous for cache locality. A custom robin_hood::hash (multiply-shift avalanche, specialized fast paths for integers and std::string) is used by default; the node variant additionally uses a bulk pool allocator to avoid per-insert malloc calls. No SIMD is used — it's portable scalar C++ relying on bit-scan intrinsics, not vector instructions.

## Compared with alternatives

Pick robin_hood over abseil::flat_hash_map, Boost.Unordered, or folly::F14 when you want a single dependency-free header to vendor and can't pull in Abseil/Boost/Folly; for any new project, the author's own successor ankerl::unordered_dense is the better default since robin_hood is explicitly unmaintained and unordered_dense is the sibling entry it was retired in favor of.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++11 (header explicitly targets 11/14/17/20; the project's own CMakeLists.txt defaults CMAKE_CXX_STANDARD to 14) |
| **Platforms** | any (portable scalar C++, no SIMD/AVX requirement); README states 'platform independent' and CI badges cover Linux/macOS (Travis) and Windows (AppVeyor) |
| **Thread safety** | not documented — no internal synchronization visible in the header; treat like std::unordered_map (safe for concurrent reads only, external locking required for any write) |
| **Drop-in for the baseline** | partial — explain: same map/set method surface as std::unordered_map, but unordered_flat_map gives up reference/pointer stability, and with a badly-mixed hash insert can throw std::overflow_error where std::unordered_map would simply degrade in performance |

## Gotchas

- unordered_node_map's bulk allocator never frees memory back to the OS during the map's lifetime — a one-time size spike leaves RSS elevated until the map is destroyed (issue #107)
- A sufficiently bad/adversarial hash can make insert throw std::overflow_error instead of degrading gracefully like std::unordered_map (README 'Design Choices' section)
- Heterogeneous/transparent lookup via is_transparent hash+equal does not work as expected in practice (issue #80, open)
- copy-assignment (operator=) frees all memory and reallocates from scratch rather than reusing the existing buffer (issue #149, open)

## Caveats and trade-offs

Repo archived since 2023; the author points users to unordered_dense. Results are from 2019 (g++ 8.2, libstdc++) and first-party. Other sub-pages, same robin_hood::hash, flat map vs std::unordered_map (derived): Insert & Erase uint64_t 11.8s vs 55.2s (4.7x); Find 1-500k uint64_t 14.4 vs 53.2 ns avg (3.7x); Iterating 8.87s vs 25.4s (2.9x); Find 1-1M std::string 38.0 vs 107 ns avg (2.8x). With libstdc++'s identity std::hash on integer keys the robin_hood maps time out in several benchmarks, so the win depends on its own default robin_hood::hash. Methodology is on the overview page https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-01-overview/.

robin_hood::unordered_flat_map has no reference/pointer stability; robin_hood::unordered_node_map trades speed for that stability via a custom bulk allocator; author has since stopped development and recommends ankerl::unordered_dense as the successor.

## Maintenance

Abandoned: the author stopped development (last commit 2023-04-21, repo carries a 'deprecated' issue template) and publicly recommends migrating to ankerl::unordered_dense, but it's MIT-licensed and small enough (one header) to vendor and freeze indefinitely.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: the series' sub-pages carry the numbers as inline Plotly data/text labels (readable, not images), the code is public at github.com/martinus/map_benchmark (e.g. src/benchmarks/Insert.cpp), and the overview page states g++ 8.2.0, -O3 -march=native, Intel Core i7-8700 locked at 3.2 GHz, libstdc++ std::unordered_map.
- **Verifier notes:** Tier upgraded C to A (verdict confirm): the chart numbers were extractable from the pages' inline Plotly data, and the benchmark_url now points at a results page. Metadata correct (MIT, 1,621 stars, archived, last commit 2023-04-21).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-01-overview/>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-03-01-result-InsertHugeInt/>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-03-02-result-RandomDistinct2/>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-03-03-result-RandomInsertErase/>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-03-04-result-RandomInsertEraseStrings/>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-04-02-result-RandomFind_2000/>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-04-03-result-RandomFind_500000/>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-04-04-result-RandomFindString/>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-04-05-result-RandomFindString_1000000/>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-04-06-result-IterateIntegers/>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-05-conclusion/>
  - <https://github.com/martinus/robin-hood-hashing>
  - <https://github.com/martinus/map_benchmark>
- **Sources the enricher read:**
  - <https://github.com/martinus/robin-hood-hashing>
  - <https://github.com/martinus/robin-hood-hashing/blob/master/README.md>
  - <https://github.com/martinus/robin-hood-hashing/blob/master/src/include/robin_hood.h>
  - <https://github.com/martinus/robin-hood-hashing/blob/master/CMakeLists.txt>
  - <https://github.com/martinus/robin-hood-hashing/issues/136>
  - <https://github.com/martinus/robin-hood-hashing/issues/107>
  - <https://github.com/martinus/robin-hood-hashing/issues/164>
  - <https://github.com/martinus/robin-hood-hashing/issues/149>
  - <https://github.com/martinus/robin-hood-hashing/issues/80>
  - <https://martin.ankerl.com/2019/04/01/hashmap-benchmarks-03-01-result-InsertHugeInt/>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/martinus/robin-hood-hashing`) · [data/wave0-seed/enrich/raw/github_com_martinus_robin_hood_hashing.json](../../../data/wave0-seed/enrich/raw/github_com_martinus_robin_hood_hashing.json) (enrichment confidence 0.85)

</details>
