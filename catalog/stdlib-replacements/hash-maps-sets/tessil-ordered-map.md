# tsl::ordered_map (Tessil/ordered-map)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Insertion-order-preserving hash map/set beating std::unordered_map on inserts, misses, and iteration.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | README: 'O(1) average time complexity for lookups with performances similar to std::unordered_map but with faster insertions and reduced memory usage'. From the raw CSV linked from the page (tsl::ordered_map v0.4; the verifier computed ratios of std::unordered_map time / tsl::ordered_map time): inserts 1.12-2.87x faster; unsuccessful lookups 2.34-4.40x faster; successful lookups mixed at 0.55-2.02x (slower on read_random_shuffle_range, about equal on 50-char strings); iteration 22-45x faster. Memory at 3M int64 entries is about 84 MB versus 126 MB. |
| **Workload** | Insertion-order-preserving hash map/set benchmarked with the same Tessil shootout suite (int64 and string keys, insert/lookup/iteration) |
| **Metric** | throughput |
| **Hardware** | Intel i5-5200u, 8GB RAM, Linux 4.11 x64 |
| **Compiler and flags** | Clang 5.0, -O3 -march=native -DNDEBUG |
| **Adoption** | 578 stars |
| **Last commit** | 2026-06-13 |
| **Links** | [repository](https://github.com/Tessil/ordered-map) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html) |

## Verdict

Author-run benchmark (Tessil hash-table-shootout, tsl::ordered_map v0.4) on an Intel i5-5200u/8GB RAM/Linux 4.11 with Clang 5.0 -O3 -march=native -DNDEBUG, against libstdc++'s std::unordered_map: inserts 1.12-2.87x faster, unsuccessful lookups 2.34-4.40x faster, iteration 22-45x faster, successful lookups mixed at 0.55-2.02x, and about 84MB vs 126MB memory at 3M int64 entries.

## Use it when

- Insert- and miss-heavy workloads on int64 or short/medium string keys, where 1.12-2.87x (inserts) and 2.34-4.40x (unsuccessful lookups) gains were measured
- Need for insertion-order iteration (config/JSON-like objects, ordered dictionaries) that std::unordered_map cannot provide at all
- Iteration-heavy code paths (serialization, dumping, full-container walks) - 22-45x faster than std::unordered_map in the cited shootout
- Memory-constrained multi-million-entry containers (about 84MB vs 126MB at 3M int64 entries in the cited benchmark)
- C++11-only toolchains that need a header-only, dependency-free drop-in with no build step

## Skip it when

- Erase-heavy workloads that must preserve order: erase() is O(bucket_count); only unordered_erase()/pop_back() are O(1) and they break ordering
- Read-heavy workloads dominated by successful lookups: measured only 0.55-2.02x vs std::unordered_map, sometimes slower (e.g. read_random_shuffle_range)
- Code relying on bucket-level APIs (bucket(), bucket_size(), ...): not supported
- Decisions needing current-version confidence: the cited numbers are from v0.4 (2017) on an old i5-5200u laptop, not part of the newer Ankerl 2022 suite, and ordered_map is absent from the benchmark page's main charts
- Containers needing more than 2^32-1 values without raising the IndexType template parameter

## How it is fast

Open addressing with linear robin hood probing plus backward shift deletion keeps probe sequences short and avoids tombstones, which speeds inserts and unsuccessful lookups relative to libstdc++'s node-based std::unordered_map. Storing values contiguously in a deque/vector instead of scattered nodes gives cache-friendly, pointer-chasing-free iteration, which is where the largest measured gains appear (22-45x). The tradeoff is an O(bucket_count) ordered erase() unless the O(1) pop_back()/unordered_erase() variants are used, which break insertion order.

## Compared with alternatives

Pick tsl::ordered_map over the other cataloged std::unordered_map beaters (hopscotch_map, robin_map, ska flat/bytell, emhash, sparsepp, rigtorp/HashMap, libcuckoo, Verstable, dense_hash_map) when insertion-order iteration is a hard requirement - it is the only one of these that preserves order. Those siblings generally win on raw insert/lookup throughput but give no ordering guarantee at all.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Boost Test only needed to build the test suite) |
| **Minimum toolchain** | C++11 (tested with GCC 4.8.4, Clang 3.5.0, Visual Studio 2015); C++20 required only for the optional module build |
| **Platforms** | any (portable C++11, no SIMD/arch-specific requirement) |
| **Thread safety** | Same guarantee as std::unordered_map: multiple concurrent readers are safe, no concurrent writer |
| **Drop-in for the baseline** | partial — explain: API closely mirrors std::unordered_map/set, but iterators are RandomAccessIterator, operator\*/-&gt; yield const std::pair&lt;Key,T&gt; (mutate via it.value(), not it-&gt;second), operator==/!= are order-dependent, and erase() is O(bucket_count) instead of O(1) |

## Gotchas

- erase() is O(bucket_count); use unordered_erase()/pop_back() for O(1) removal, but this breaks insertion order
- Iterators expose const std::pair&lt;Key,T&gt;; modify values through it.value(), not it-&gt;second
- operator==/!= are order-dependent: two containers with identical key/value pairs inserted in different order compare unequal
- Default IndexType caps the container at 2,294,967,295 (2^32-1) values; raise the IndexType template parameter for larger sizes

## Caveats and trade-offs

tsl::ordered_map is not in the page's main charts. Its data appears only in the linked interactive chart page (https://tessil.github.io/other/hash_table_benchmark.html) and the raw CSV. The benchmarked version is v0.4 from 2017. It is not in the Ankerl 2022 suite. The README says erase() is O(bucket_count), so the speed claim is mainly about inserts and misses.

Higher memory footprint (8 bytes/bucket by default) to preserve insertion order; ordered erase is O(bucket_count) unless using the provided O(1) pop_back()/unordered_erase()

## Maintenance

Active (last commit 2026-06-13, CI passing, MIT-licensed); header-only form makes it trivial to vendor and keep working even if upstream maintenance later lapses.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A. The linked repo Tessil/hash-table-shootout has src/tsl_ordered_map.cc and src/std_unordered_map.cc (Makefile CXX_FLAGS=-O3 -march=native -std=c++14 -DNDEBUG). The page lists tsl::ordered_map v0.4 as tested and states Clang 5.0 with libstdc++ and an i5-5200u with 8GB on Linux 4.11. The benchmark is run by the author.
- **Verifier notes:** Metadata checks out: MIT, 578 stars, last commit 2026-06-13, active, not a fork, not archived. numbers_found_on_page is false because the claim is a README quote and the main page does not chart ordered_map, although the linked raw data does support the claim.
- **Fields the verifier corrected:** `baseline_stdlib`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Tessil/ordered-map>
  - <https://github.com/Tessil/ordered-map/blob/master/README.md>
  - <https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html>
  - <https://tessil.github.io/other/hash_table_benchmark.html>
  - <https://tessil.github.io/other/hopscotch_map_benchmark_raw_results.csv>
  - <https://github.com/Tessil/hash-table-shootout>
- **Sources the enricher read:**
  - <https://github.com/Tessil/ordered-map>
  - <https://github.com/Tessil/ordered-map/blob/master/README.md>
  - <https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html>
  - <https://tessil.github.io/other/hash_table_benchmark.html>
  - https://github.com/Tessil/ordered-map (file tree via gh api git/trees)
  - https://github.com/Tessil/ordered-map (issue search: bug OR performance OR slow, no results)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/tessil/ordered-map`) · [data/wave1/enrich/raw/github_com_tessil_ordered_map.json](../../../data/wave1/enrich/raw/github_com_tessil_ordered_map.json) (enrichment confidence 0.6)

</details>
