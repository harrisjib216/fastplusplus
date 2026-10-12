# tsl::hopscotch_map (Tessil/hopscotch-map)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 hopscotch-hashing hash map/set, faster than std::unordered_map with dense_hash_map-like speed.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | README: 'a cache-friendly data structure offering better performances than std::unordered_map in most cases'. From the page's raw-results CSV (200K-3M entries; the verifier computed ratios of std::unordered_map time / tsl::hopscotch_map time), hopscotch is faster in every test: inserts 1.08-2.67x, successful lookups 1.51-4.31x, unsuccessful lookups 1.85-5.47x, erase 1.55-10.1x, iteration 4.6-13.2x. It beats google::dense_hash_map in 190 of 315 data points, so the earlier wording 'trailing google::dense_hash_map' was not accurate. |
| **Workload** | int64_t keys (identity hash), 15-char and 50-char std::string keys; insert, successful/unsuccessful lookup, and iteration across table sizes up to millions of elements (same benchmark suite as tsl::robin_map) |
| **Metric** | throughput |
| **Hardware** | Intel i5-5200u, 8GB RAM, Linux 4.11 x64 |
| **Compiler and flags** | Clang 5.0, -O3 -march=native -DNDEBUG |
| **Adoption** | 849 stars |
| **Last commit** | 2025-11-02 |
| **Links** | [repository](https://github.com/Tessil/hopscotch-map) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html) |

## Verdict

Against std::unordered_map (libstdc++, Clang 5.0, -O3 -march=native -DNDEBUG, Intel i5-5200u/8GB RAM/Linux 4.11), the author's benchmark (200K-3M entries, int64 identity-hash and 15/50-char string keys) found hopscotch_map faster in every measured case: 1.08-2.67x on insert, 1.51-5.47x on successful/unsuccessful lookup, 1.55-10.1x on erase, and 4.6-13.2x on iteration.

## Use it when

- Read-heavy workloads (successful/unsuccessful lookup, iteration) with int64 or short-to-medium string keys, in the low-hundred-thousands to low-millions element range (benchmarked at 200K-3M).
- You want a near-drop-in replacement for std::unordered_map without adopting its chained-bucket allocation overhead, and can require C++17 and header-only integration.
- You want dense_hash_map-like throughput but without reserving sentinel/deleted-key values or accepting dense_hash_map's more restrictive API.
- You control the hash function well enough to avoid low-bit collisions, or are willing to switch to the _pg (prime growth) variant if you can't.
- You need optional worst-case DoS resistance (bhopscotch_map/set) for keys that are LessThanComparable, at a throughput cost.

## Skip it when

- Identity or otherwise weak hash functions on adversarial/clustered-bit-pattern keys with the default power-of-two policy: the independent Ankerl 2022 suite reports hopscotch timing out on random insert/erase with identity std::hash.
- Code that depends on std::unordered_map's iterator/reference stability across insert: hopscotch invalidates all iterators and references on any insert (only erase preserves them).
- Move-only value types whose move constructor isn't noexcept: not supported, since rehash needs the nothrow guarantee under open addressing.
- Code relying on bucket-introspection methods (bucket(), bucket_size(), etc.): not implemented.
- Inserting implicitly-converted move-only pairs (e.g. a derived-class unique_ptr into a base-class-keyed map) via the generic insert(P&&) overload: open bug #66, a regression after PR #63, still open as of 2026-09-23.

## How it is fast

Hopscotch hashing keeps every key within a fixed-size neighborhood (bitmap) of its ideal bucket, so a lookup only scans a small, cache-local run of buckets instead of following a chain; neighborhoods are rearranged on insert to preserve this bound. Elements are stored contiguously via open addressing, avoiding the per-node heap allocation std::unordered_map's separate chaining requires. The default power-of-two growth policy replaces modulo with a bitmask; a prime growth policy (_pg variants) is offered when the hash has weak low-bit entropy, at some speed cost. Optional hash caching (StoreHash) and passing a precalculated hash into find() avoid recomputing hashes on rehash/lookup.

## Compared with alternatives

Pick hopscotch_map over robin_map/ska/emhash when you want the bhopscotch_map DoS-resistant option or heterogeneous lookups with dense_hash_map-like throughput and lower memory than dense_hash_map; robin-hood-style siblings (robin_map, ska::flat_hash_map, emhash) tend to edge it out on raw insert throughput in independent benchmarks.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library; Boost Test is needed only to build the test suite |
| **Minimum toolchain** | C++17-compliant compiler |
| **Platforms** | architecture-agnostic; the headers read include only standard library headers, no SIMD intrinsics or platform-specific code observed |
| **Thread safety** | same as std::unordered_map/set per README: safe for multiple concurrent readers with no concurrent writer; no internal synchronization |
| **Drop-in for the baseline** | partial — explain: same method names and semantics as std::unordered_map/set including heterogeneous lookup, but insert/emplace invalidate all iterators and references (erase does not), iterators yield a const value (mutate via .value()), move-only values need a nothrow move constructor, and bucket-introspection methods are missing |

## Gotchas

- Insert/emplace invalidate all iterators and references, unlike std::unordered_map's node-based stability; only erase is safe.
- it-&gt;second is not assignable; iterators dereference to const std::pair, so mutate via it.value() = ...
- Default growth policy is power-of-two; a hash with poor low-bit entropy causes heavy collisions — check overflow_size() and switch to the _pg (prime) variant if it's nonzero.
- Open issue #66: insert(P&&) is broken for implicitly-convertible move-only pairs (e.g. derived-to-base unique_ptr), a regression introduced after PR #63 and unresolved at time of writing.

## Caveats and trade-offs

The benchmark is run by the author and tests 2017-era library versions (page last updated Oct 05, 2017). The page shows charts; the numbers are in the linked raw CSV at https://tessil.github.io/other/hopscotch_map_benchmark_raw_results.csv. libstdc++ std::hash&lt;int64_t&gt; is the identity function. In the independent Ankerl 2022 suite, the geometric mean is about 2.1x better than std::unordered_map with good hashes, but hopscotch times out on random insert/erase with identity std::hash.

Same iterator/pointer invalidation caveat as robin-map; hopscotch neighborhood bookkeeping adds a little per-bucket memory; the bhopscotch variant trades some speed for O(log n) DoS resistance

## Maintenance

Actively maintained (last commit 2025-11-02) under MIT; small and header-only enough to vendor, but requires C++17 and currently has one open correctness bug (#66) in a move-only insert overload.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A. The linked repo Tessil/hash-table-shootout has reproducible benchmark code that runs against std::unordered_map: src/std_unordered_map.cc, src/tsl_hopscotch_map.cc, src/template.c, and a Makefile with CXX_FLAGS=-O3 -march=native -std=c++14 -DNDEBUG. The page states the compiler (Clang 5.0 with libstdc++), the flags, the hardware (i5-5200u, 8GB, Linux 4.11) and 'best of five runs'. The benchmark is run by the library's own author, not an independent party.
- **Verifier notes:** Metadata checks out: MIT, 849 stars, last commit 2025-11-02 (within 12 months, so active), not a fork, not archived. The shootout repo is a fork of mackstann/hash-table-shootout.
- **Fields the verifier corrected:** `baseline_stdlib`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Tessil/hopscotch-map>
  - <https://github.com/Tessil/hopscotch-map/blob/master/README.md>
  - <https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html>
  - <https://tessil.github.io/other/hopscotch_map_benchmark_raw_results.csv>
  - <https://github.com/Tessil/hash-table-shootout>
  - <https://martin.ankerl.com/2022/08/27/hashmap-bench-01/>
  - <https://martin.ankerl.com/files/2022/map_benchmark.js>
- **Sources the enricher read:**
  - <https://github.com/Tessil/hopscotch-map>
  - <https://github.com/Tessil/hopscotch-map/blob/master/README.md>
  - <https://github.com/Tessil/hopscotch-map/blob/master/include/tsl/hopscotch_hash.h>
  - <https://github.com/Tessil/hopscotch-map/issues/66>
  - <https://github.com/Tessil/hopscotch-map/issues/55>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/tessil/hopscotch-map`) · [data/wave1/enrich/raw/github_com_tessil_hopscotch_map.json](../../../data/wave1/enrich/raw/github_com_tessil_hopscotch_map.json) (enrichment confidence 0.72)

</details>
