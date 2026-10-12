# tsl::robin_map (Tessil/robin-map)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only robin hood open-addressing hash map/set beating std::unordered_map on insert, lookup, erase, and iteration.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | From the page's charts and raw CSV (200K-3M entries; the verifier computed ratios of std::unordered_map time / tsl::robin_map time), robin_map is faster in every test: inserts 1.08-3.63x, successful lookups 1.55-5.34x, unsuccessful lookups 1.66-6.57x, erase 1.58-13.5x, iteration 2.6-5.3x. In the independent Ankerl 2022 suite, the geometric mean over all tests is about 2.4x better (2.42-2.44x with the mumx and robin_hood hashes). |
| **Workload** | int64_t keys (identity hash), 15-char and 50-char std::string keys; insert, successful/unsuccessful lookup, and iteration across table sizes up to millions of elements |
| **Metric** | throughput |
| **Hardware** | Intel i5-5200u, 8GB RAM, Linux 4.11 x64 |
| **Compiler and flags** | Clang 5.0, -O3 -march=native -DNDEBUG |
| **Adoption** | 1508 stars |
| **Last commit** | 2026-06-13 |
| **Links** | [repository](https://github.com/Tessil/robin-map) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html) |

## Verdict

Author-run benchmark (Clang 5.0, -O3 -march=native -DNDEBUG; Intel i5-5200u, 8GB RAM, Linux 4.11 x64; libstdc++) across 200K-3M entries with int64_t and 15/50-char string keys found robin_map faster than std::unordered_map in every measured case: inserts 1.08-3.63x, successful lookups 1.55-5.34x, unsuccessful lookups 1.66-6.57x, erase 1.58-13.5x, iteration 2.6-5.3x. The independent Ankerl 2022 suite puts the geometric-mean advantage around 2.4x, but in that same suite robin_map times out on random insert/erase with an identity std::hash and iterates slower (0.80-0.92x) than std::unordered_map.

## Use it when

- int64_t or other cheap-to-hash keys where you supply a decent hash (not the identity std::hash) and want faster inserts/lookups/erases than std::unordered_map
- std::string keys, especially short (SSO-sized) strings, where robin_map's automatic hash caching gives a large insertion win
- workloads dominated by successful/unsuccessful lookups or full-table iteration at sizes from \~200K to several million elements
- code that needs heterogeneous lookup (find by a different-but-comparable type) or binary serialize/deserialize of the table
- environments where -fno-exceptions or TSL_NO_EXCEPTIONS is desired; the library supports exception-free builds via std::terminate

## Skip it when

- pointer/reference/iterator stability across modification matters: open addressing invalidates all of them on any insert, erase, or rehash, unlike std::unordered_map
- keys hashed with the default identity-like std::hash for integers combined with the default power-of-two growth policy: linear inserts can trigger exponential storage growth (GH issue #39); switch to robin_pg_map/robin_pg_set or supply a better hash
- code that erases elements while iterating and depends on visiting each element exactly once: backward-shift deletion can revisit an already-seen element (GH issue #20, open, no fix planned)
- memory-constrained int64 workloads at large scale: at 3M entries the author's own CSV shows \~202MB for robin_map vs \~126MB for std::unordered_map (\~1.6x)
- key/value types that are not swappable or not copy/move constructible, or where you rely on std::unordered_map's bucket-inspection API (bucket(), bucket_size(), etc.), which robin_map omits

## How it is fast

Robin hood hashing with linear probing keeps entries close to their ideal bucket, so lookups scan a short, cache-resident run instead of chasing pointers through separate chaining nodes. Erase uses backward-shift deletion (no tombstones), which keeps probe sequences short after deletes. Optional per-entry hash caching (StoreHash) and a precalculated_hash parameter let callers skip recomputing hashes on rehash or lookup when the hash or key-equality function is expensive.

## Compared with alternatives

Prefer tsl::robin_map over ska::flat_hash_map/bytell_hash_map or sparsepp when you want an actively maintained, documented library with heterogeneous lookup, binary serialization, and a built-in prime-growth fallback (robin_pg_map) for weak hashes. Prefer tsl::hopscotch_map instead when erase-heavy iteration or memory density at high load factor matters more than raw lookup/insert throughput, since hopscotch avoids robin-map's backward-shift erase cost and identity-hash growth pathology.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library; Boost Test only needed to build the test suite |
| **Minimum toolchain** | C++17 (README: "should work with any C++17 standard-compliant compiler") |
| **Platforms** | portable C++17, no SIMD or arch-specific intrinsics in the source; CI covers Linux and macOS (GCC and Clang) and Windows (MSVC via Visual Studio 2025, x64 and x86) |
| **Thread safety** | Same guarantee as std::unordered_map/set: safe for multiple concurrent readers, not safe with any concurrent writer; no internal locking |
| **Drop-in for the baseline** | partial — API closely mirrors std::unordered_map/set, but iterator invalidation is stricter, map iterators return const std::pair (mutate via it.value(), not it-&gt;second), bucket-inspection methods are absent, and the strong exception guarantee only holds when value_type is nothrow-swappable and nothrow-move-constructible |

## Gotchas

- Any insert, erase, or rehash invalidates all iterators, pointers, and references into the table (stricter than std::unordered_map).
- Default power-of-two growth policy + a poor/identity hash (common for std::hash&lt;integral&gt;) can make a linear insertion sequence blow up storage exponentially; use robin_pg_map/robin_pg_set or a stronger hash.
- erase(iterator) walks forward to the next nonempty bucket to return a valid iterator, which is O(expensive) at low load factor; use void erase_fast(iterator) when you don't need the returned iterator.
- Iterating while erasing can visit one element twice due to backward-shift deletion wrap-around; open upstream issue (#20) since 2019, maintainer's stance is 'that's the way it is'.

## Caveats and trade-offs

The benchmark is run by the author and tests 2017-era versions; the numbers are in the raw CSV at https://tessil.github.io/other/hopscotch_map_benchmark_raw_results.csv. At 3M int64 entries, robin_map uses about 1.6x the memory of std::unordered_map (202 MB versus 126 MB). In Ankerl 2022, robin_map times out on random insert/erase with identity std::hash, and its iteration is slower than std::unordered_map (0.80-0.92x).

Open addressing invalidates iterators/pointers on any modification (unlike std::unordered_map); key/value must be swappable and copy/move-constructible; strong exception guarantee only holds under extra conditions

## Maintenance

Actively maintained (last commit 2026-06-13, 1508 stars, CI green across GCC/Clang/MSVC), MIT-licensed and header-only, so it is trivially vendorable even if upstream development ever stopped.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B to A. The linked repo Tessil/hash-table-shootout (src/tsl_robin_map.cc, src/std_unordered_map.cc, src/template.c, Makefile CXX_FLAGS=-O3 -march=native -std=c++14 -DNDEBUG) runs against std::unordered_map. The page states Clang 5.0 with libstdc++ and an i5-5200u with 8GB on Linux 4.11, best of five runs. The benchmark is run by the author.
- **Verifier notes:** Metadata checks out: MIT, 1508 stars, last commit 2026-06-13, active, not a fork, not archived.
- **Fields the verifier corrected:** `baseline_stdlib`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** Against developer source's SIMD Swiss-table fastcpp::flat_hash_map on 1M uint64 keys, tsl::robin_map was 1.18x faster on hit lookups but 0.49x on misses and 0.82x on build-from-empty, so phmap was adopted instead (absolute ns not published). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-02-libraries)
- **Pages the verifier opened:**
  - <https://github.com/Tessil/robin-map>
  - <https://github.com/Tessil/robin-map/blob/master/README.md>
  - <https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html>
  - <https://tessil.github.io/other/hopscotch_map_benchmark_raw_results.csv>
  - <https://github.com/Tessil/hash-table-shootout>
  - <https://martin.ankerl.com/2022/08/27/hashmap-bench-01/>
  - <https://martin.ankerl.com/files/2022/map_benchmark.js>
- **Sources the enricher read:**
  - <https://github.com/Tessil/robin-map>
  - <https://github.com/Tessil/robin-map/blob/master/README.md>
  - <https://github.com/Tessil/robin-map/blob/master/.github/workflows/ci.yml>
  - <https://github.com/Tessil/robin-map/blob/master/include/tsl/robin_hash.h>
  - <https://github.com/Tessil/robin-map/issues/20>
  - <https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/tessil/robin-map`) · [data/wave1/enrich/raw/github_com_tessil_robin_map.json](../../../data/wave1/enrich/raw/github_com_tessil_robin_map.json) (enrichment confidence 0.75)

</details>
