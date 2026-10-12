# google::dense_hash_map (sparsehash)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Open-addressing C++ hash map beating std::unordered_map on lookups/inserts at large memory cost.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | Tessil hash-table-shootout, from the raw results CSV linked from the page (the page itself shows charts): read_random_full at n=3,000,000: std::unordered_map 0.297209 s vs google::dense_hash_map 0.054073 s (\~5.5x, derived from page data); insert_random_full at n=3,000,000: 1.055850 s vs 0.308572 s (\~3.4x, derived from page data). Across all tests and sizes, dense_hash_map is faster in 20 of 21 tests with a \~2.3x overall geometric-mean speedup (derived from page data); per-test geomeans range from 0.90x (insert_string) to 13.05x (delete_random_full) (derived from page data). |
| **Workload** | rigtorp/HashMap HashMapBenchmark delete-heavy loop: look up a random key and erase it if present, otherwise insert it; size_t keys drawn from a uniform int range, 24-byte values, CRC32 hash; working set inside L3 (-c 100000 -i 100000000) and larger than L3 (-c 10000000 -i 1000000000) |
| **Metric** | latency |
| **Hardware** | Intel i5-5200u |
| **Compiler and flags** | Clang 5.0, -O3 -march=native -DNDEBUG |
| **Adoption** | 1601 stars |
| **Last commit** | 2020-08-12 |
| **Links** | [repository](https://github.com/sparsehash/sparsehash) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html) |

## Verdict

On Tessil's independent hash-table shootout (Clang 5.0, -O3 -march=native -DNDEBUG, libstdc++, Intel i5-5200u), google::dense_hash_map beat std::unordered_map in 20 of 21 tests, a \~2.3x geometric-mean speedup, including read_random_full at n=3,000,000 (0.054s vs 0.297s, \~5.5x) and insert_random_full (0.309s vs 1.056s, \~3.4x); its sole loss was insert_string at \~0.90x.

## Use it when

- Read-heavy workloads with fixed-size keys (integers, pointers, short strings) where lookup latency matters more than memory footprint.
- Data sets that comfortably fit in RAM with headroom to spare for a doubling resize.
- You can carve out two sentinel key values (empty + deleted) that will never appear as real data.
- You can build and run under an older/stable C++ toolchain (GCC/Clang pre-C++20) and pin -DNDEBUG so asserts don't eat the speed gain.
- You're fine vendoring a BSD-3-Clause, unmaintained-since-2020 header set rather than depending on active upstream support.

## Skip it when

- Memory-constrained services: README states a 2-4x steady-state overhead, rising to a 6x 'high-water mark' mid-resize (old 2x table plus new 4x table coexist).
- Heavy erase/reinsert cycles near max_load_factor(1): issue #141 shows find() on a missing key can loop forever once every bucket is either occupied or a deleted-tombstone.
- Very large datasets: issue #123 reports dense_hash_map hanging/failing around \~900M entries (16-process distributed job) where std::unordered_map ran fine.
- Element counts that land just below a power of two: issue #172 (open, filed Dec 2025) reports an unresolved, order-of-magnitude slowdown in the 2.0.4 release near power-of-two sizes, absent in 2.0.3.
- String-heavy or variable-length keys, and any build on GCC 11+ with -std=c++20/c++2b: Tessil's shootout shows it losing on insert_string (0.90x vs std::unordered_map), and open PRs/issues (#165, #166) report c++20 build fixes needed and a c++2b segfault in libc_allocator_with_realloc.

## How it is fast

It stores all key/value pairs inline in one contiguous array (densehashtable.h) using quadratic-probing open addressing, so lookups walk cache lines instead of chasing per-node pointers/allocations the way node-based chaining maps do. A reserved empty-key sentinel marks free slots without a separate occupancy bitmap, and erase() writes a deleted-key tombstone instead of compacting, which avoids iterator invalidation but leaves stale entries until a resize. Confirmed against README.md, the dense_hash_map header, and densehashtable.h in the repo, and against Tessil's independent shootout (Clang 5.0, -O3 -march=native -DNDEBUG, Intel i5-5200u), which measured it fastest in 20 of 21 tests.

## Compared with alternatives

Within the sparsehash family, pick dense_hash_map over sparsepp when you have RAM to spare and want the fastest lookups; sparsepp trades some of that speed for much lower memory and reportedly beats dense_hash_map's stability at very large sizes. Against actively maintained alternatives (tsl::robin_map, ska::flat_hash_map, emhash), dense_hash_map's only real draw is its long-proven quadratic-probing design — those get comparable or better speed without the mandatory empty/deleted-key setup or an unmaintained-since-2020 codebase with open hang/perf-regression reports.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none at the API level, but the build needs autotools (./configure/make install) or an equivalent packaged sparseconfig.h to generate the platform's HASH_FUN_H macro before the headers are usable |
| **Minimum toolchain** | C++03/11-era API (tr1-style hash&lt;&gt;); upstream has not verified newer standards - open reports of build failures/segfaults under -std=c++20/c++2b on GCC 11+ |
| **Platforms** | any (README reports Linux, Solaris, FreeBSD, macOS, and Windows/MSVC support, last verified against toolchains circa 2010-2015; pure C++, no SIMD/intrinsics required) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — explain: API superset of std::unordered_map, but set_empty_key() is mandatory before first use and set_deleted_key() is mandatory before any erase(); inserting either sentinel value is undefined behavior |

## Gotchas

- set_empty_key() must be called right after construction (or passed to the iterator-range constructor) and set_deleted_key() before any erase() call; skipping either, or inserting a key equal to one, causes undefined/mysterious failures per the header comments.
- erase() never reclaims memory or invalidates iterators; repeated erase/insert cycles bloat memory until you call resize(0), and at max_load_factor(1) a fully-occupied table (valid + deleted buckets only) can make find() on an absent key loop forever (issue #141).
- Resizing needs up to 6x the raw entry size as a transient high-water mark (README), so budget memory headroom well beyond the steady-state 2-4x overhead.
- dense_hash_map's disk-serialization methods (write_metadata/write_nopointer_data) are present in the API but unimplemented and always fail — only sparse_hash_map actually supports save/restore to disk.

## Caveats and trade-offs

The numbers come from a third-party benchmark (rigtorp/HashMap) whose optimization flags are not stated. On worst-case latency, dense_hash_map is far worse than std::unordered_map (max 689,846 ns vs 10,299 ns in cache; 226,083,255 ns vs 22,422 ns out of cache), so only the mean favors it. sparsehash's own doc/performance.html (2004, gcc 2.95.3 -g -O2, Pentium 4) compares against the SGI hash_map, not std::unordered_map. Its src/time_hash_map.cc can also time the native unordered_map, but the repo publishes no such results. sparsepp's bench.md notes that dense_hash_map ran out of memory at 70M entries because of resize memory spikes. No commits since 2020-08-12. [retier] The page says integer tests use libstdc++'s identity std::hash for all maps. dense_hash_map loses on insert_string (0.90x, derived from page data), and the page notes it does poorly on read misses relative to other open-addressing maps and needs more memory at high load factors.

Extremely high memory use vs chaining maps: stores entries in one contiguous array and doubles on 50% load, causing up to 6x the steady-state memory footprint during a resize; requires reserving sentinel 'empty' and 'deleted' key values.

## Maintenance

Abandoned since its last commit on 2020-08-12 — the repo has 20+ open issues/PRs including an unresolved December 2025 report of a severe performance regression near power-of-two sizes in the 2.0.4 release; it's BSD-3-Clause and small enough to vendor, but expect friction building under modern C++ standards/compilers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** The quoted numbers come from independent third-party benchmarks. One is rigtorp/HashMap src/HashMapBenchmark.cpp: gcc 10.2.1 on a Ryzen 9 3900X, but the optimization flags are not stated. The other is sparsepp's bench.md (g++ 4.8.4). Tessil's hash-table shootout, which states its compiler, flags, and hardware, also includes dense_hash_map vs std::unordered_map, but only in charts. It is not A because the sparsehash repo has no published run against std::unordered_map, and the third-party run does not state its flags.
- **Retiered** B to A: A rests on Tessil's independent shootout, not the record's rigtorp numbers (rigtorp README and CMakeLists state no -O flags): code Tessil/hash-table-shootout src/google_dense_hash_map.cc vs src/std_unordered_map.cc, Clang 5.0, -O3 -march=native -DNDEBUG, Intel i5-5200u, libstdc++. Raw CSV shows dense_hash_map faster in 20 of 21 tests (geomean \~2.3x; insert_string 0.90x), so benchmark_url and claimed_speedup should be switched to the Tessil run.
- **Verifier notes:** The rigtorp numbers (49 vs 67 and 111 vs 408 mean ns/iter) and the sparsepp quote ('consistently the fastest, often by a quite significant margin', until it runs out of memory at 60M entries) are both accurate. Tier A is not justified: the code is not in or linked from the repo, and the flags are unstated. Metadata checks out: BSD-3-Clause, 1601 stars, last commit 2020-08-12, abandoned.
- **Fields the verifier corrected:** `workload`, `caveats`, `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`
- **Pages the verifier opened:**
  - <https://github.com/sparsehash/sparsehash>
  - <https://github.com/sparsehash/sparsehash/blob/master/README>
  - <https://github.com/sparsehash/sparsehash/blob/master/doc/performance.html>
  - <https://github.com/sparsehash/sparsehash/blob/master/src/time_hash_map.cc>
  - <https://github.com/rigtorp/HashMap>
  - <https://github.com/rigtorp/HashMap/blob/master/src/HashMapBenchmark.cpp>
  - <https://github.com/greg7mdp/sparsepp/blob/master/bench.md>
  - <https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html>
- **Sources the enricher read:**
  - <https://github.com/sparsehash/sparsehash>
  - <https://github.com/sparsehash/sparsehash/blob/master/README>
  - <https://github.com/sparsehash/sparsehash/blob/master/doc/dense_hash_map.html>
  - <https://github.com/sparsehash/sparsehash/blob/master/src/sparsehash/dense_hash_map>
  - <https://github.com/sparsehash/sparsehash/blob/master/NEWS>
  - <https://github.com/sparsehash/sparsehash/issues/172>
  - <https://github.com/sparsehash/sparsehash/issues/123>
  - <https://github.com/sparsehash/sparsehash/issues/141>
  - <https://github.com/sparsehash/sparsehash/issues/110>
  - <https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/sparsehash/sparsehash`) · [data/wave1/enrich/raw/github_com_sparsehash_sparsehash.json](../../../data/wave1/enrich/raw/github_com_sparsehash_sparsehash.json) (enrichment confidence 0.7)

</details>
