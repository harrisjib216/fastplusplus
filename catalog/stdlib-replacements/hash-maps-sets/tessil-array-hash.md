# tsl::array_map / array-hash (Tessil)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only cache-conscious string hash map/set (Askitis array hash); about half the memory of std::unordered_map&lt;std::string,T&gt;, 1.3-2.3x faster lookups.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | Wikipedia shuffled: read 138.24 ns/key vs 173.58 for std::unordered_map (1.26x faster, derived from page data); memory 678.73 MiB vs 1246.60 MiB (1.84x less, derived from page data); insert with reserve 249.52 vs 350.33 ns/key (1.40x faster, derived from page data); insert without reserve 603.94 vs 590.88 ns/key (about equal, 2% slower). Askitis dataset: read 46.41 vs 105.05 ns/key (2.26x faster, derived from page data); insert with reserve 244.19 vs 309.06 ns/key (1.27x faster, derived from page data); insert without reserve 545.82 vs 554.02 ns/key (about equal); memory 1031.67 vs 2110.19 MiB (2.05x less, derived from page data). |
| **Workload** | String-keyed map (key to 32-bit int): insert all keys, then look up all keys. Wikipedia enwiki-20170320 ns0 titles (13,099,148 keys, avg length 19.90, shuffled) and Askitis distinct_1 insert / skew1_1 read (28,772,169 / 177,999,203 keys, avg length 9.59 / 5.06); memory measured too. All hash maps use CityHash64. |
| **Metric** | throughput |
| **Hardware** | Intel i5-5200u, 8 GB RAM; best of 20 runs (hat-trie README) |
| **Compiler and flags** | GCC 6.3 on Debian Stretch x64 (README); benchmark Makefile in the linked gist: CXXFLAGS=-lcityhash -std=c++11 -march=native -DNDEBUG -O3 |
| **Adoption** | 187 stars |
| **Last commit** | 2025-11-02 |
| **Links** | [repository](https://github.com/Tessil/array-hash) · [benchmark](https://github.com/Tessil/hat-trie#benchmark) |

## Verdict

Tessil's hat-trie benchmark (GCC 6.3, libstdc++, -std=c++11 -O3 -march=native, Intel i5-5200u, CityHash64 for all maps, 2017) inserted then looked up 13.1M shuffled Wikipedia titles: array_map read 138.24 vs 173.58 ns/key for std::unordered_map&lt;std::string,int&gt; (1.26x) at 678.73 vs 1246.60 MiB, inserted 249.52 vs 350.33 ns/key with reserve but 603.94 vs 590.88 without; on the Askitis short-key set it read 46.41 vs 105.05 ns/key (2.26x) at 1031.67 vs 2110.19 MiB. The author's 2017 hash-table-shootout CSV (Clang 5.0, same CPU, std::hash for all) agrees on direction: 3M 50-char keys read 1.70x faster but insert without reserve 1.20x slower (derived from page data).

## Use it when

- Millions of string keys where RSS matters: 678.73 vs 1246.60 MiB for 13.1M Wikipedia titles and 1031.67 vs 2110.19 MiB for 28.8M short Askitis keys against std::unordered_map&lt;std::string,int&gt;.
- Build-once, read-many dictionaries where the key count is known so reserve() avoids rehash (insert with reserve 249.52 vs 350.33 ns/key on Wikipedia titles).
- Lookup-heavy workloads on medium or long keys that do not fit in SSO: 50-char random keys at 3M entries read 0.616 s vs 1.049 s for std::unordered_map in the author's 2017 shootout (1.70x, derived from page data).
- String dictionaries that must be saved and reloaded quickly: serialize/deserialize with the hash_compatible fast path skips rehashing every key.
- C++11 code that wants an MIT, header-only, dependency-free container and can live with a string-only, non-node API.

## Skip it when

- Insert- or erase-heavy use without reserve: inserts are not faster (603.94 vs 590.88 ns/key on Wikipedia titles) and were 20% slower in the 2017 shootout (2.02 vs 1.68 s for 3M 50-char keys); erase was also slower (1.92 vs 1.66 s), because every append reallocs the bucket buffer and rehash re-hashes and copies every key.
- Short keys where raw lookup speed matters most: open-addressing maps beat it (15-char keys at 3M: array_map 0.358 s vs tsl::robin_map 0.234, ska::flat_hash_map 0.249, tsl::hopscotch_map 0.260), and hopscotch_map also read Wikipedia titles faster (119.49 vs 138.24 ns/key).
- Code that needs stable references, std::pair access, node extract/merge, bucket inspection or a custom allocator: any modification invalidates iterators, references and pointers, and memory comes from std::malloc/std::realloc and std::vector with no Allocator parameter (requested in issue #9).
- Non-string keys (the shootout harness exits on its integer tests) or bool values: array_map&lt;char, bool&gt; fails to compile because the values vector is std::vector&lt;bool&gt; (issue #12, open since 2023-04).
- Keys longer than 65,535 characters or more than 2^32 entries unless KeySizeT / IndexSizeT are widened; the insert throws std::length_error otherwise.

## How it is fast

It implements the array hash table of Askitis and Zobel ('Cache-conscious collision resolution in string hash tables', 2005): each bucket is one malloc'd buffer holding [16-bit key length][key chars][32-bit index] records back to back, ended by a sentinel, so a lookup is one hash, one pointer chase into a contiguous buffer and a length-then-memcmp scan, with no per-key node and no std::string heap indirection. Mapped values live in a separate std::vector&lt;T&gt;, which keeps the bucket buffers small; the default max load factor is 2.0 (about two keys per bucket) with power-of-two masking. The memory saving comes from dropping the 32-byte std::string plus node and pointer overhead per key.

## Compared with alternatives

Pick it over tsl::robin_map, tsl::hopscotch_map, absl::flat_hash_map or boost::unordered_flat_map keyed by std::string when memory per string key is the constraint and the map is mostly read (678.73 MiB vs 1077.99 for hopscotch_map and 1677.11 for google::dense_hash_map on Wikipedia titles, at 16% slower reads than hopscotch_map); if you also need prefix search or an even smaller footprint, tsl::htrie_map (402.25 MiB, built on this library) is the better fit.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Boost.Test only for the test suite) |
| **Minimum toolchain** | C++11 (README: tested with GCC 4.8.4, Clang 3.5.0, Visual Studio 2015); string_view overloads and std::hash&lt;string_view&gt; default with C++17; CMake 3.10 for the optional exported target tsl::array_hash |
| **Platforms** | any; CI runs GCC and Clang on Linux x64 (including an ASan/UBSan job) and macOS, and MSVC on Windows x64 and x86 |
| **Thread safety** | Same as STL containers per the README: concurrent const access is fine, any writer needs external synchronisation. |
| **Drop-in for the baseline** | partial — the member set mirrors std::unordered_map, but insert takes (key, value) instead of a std::pair, iterators yield the value and expose key()/key_sv(), keys must be character strings, and iterator/reference invalidation rules are much stricter |

## Gotchas

- Any insert, erase or rehash invalidates all iterators, references and pointers to keys and values; erase removes the key at once but may delay the mapped value's destructor until the erased fraction passes a threshold (0.6) or shrink_to_fit() is called.
- Hash choice is on you: the default is std::hash&lt;std::string_view&gt; under C++17 and a plain FNV-1a otherwise (README: CityHash64 gave about 40% faster reads than FNV-1a), and the default power-of-two policy masks low bits, so use array_pg_map/set with weak or identity-like hashes.
- Rehash needs spare memory because keys are copied, not moved: on Wikipedia titles peak RSS was 823.54 MiB against a final 678.73 MiB without reserve; call reserve() when the count is known.
- Harness notes for the headline numbers: lookups only test find() != end(), and in array_map find() never touches the separate values vector, so reading the value (one more random access into std::vector&lt;T&gt;) is not timed while std::unordered_map's value sits in the node it already loaded; the benchmark also ran array_map with the non-default StoreNullTerminator=false, CityHash64 for every map, a baseline insert that copies the key twice, and a best-of-20 driver that is not in the public gist.

## Known shortcomings

- All figures come from the 2017 hat-trie README benchmark (public gist harness, GCC 6.3, -O3 -march=native, i5-5200U): inserts without reserve are not faster, reads are slower than hopscotch_map and dense_hash_map, no absl::flat_hash_map or tsl::robin_map column, best-of-20 is not in the gist, and the std::unordered_map insert copies the key twice. Filed under stdlib-replacements/hash-maps-sets by category override.
- Enricher: the lookups only test find() != end(), and array_map's find() never touches the separate values vector, so the extra random access to read a value is never timed while std::unordered_map's value sits in a node already loaded; StoreNullTerminator=false is non-default; the best-of-20 driver is not public. The 2017 shootout CSV (Clang 5.0, i5-5200U, tessil.github.io via raw.githubusercontent.com) shows insert without reserve slower (2.02 vs 1.68 s), slower erase and short-key reads behind robin_map, ska and hopscotch; long-key reads 1.70x faster (derived from page data). Only CI and CMake bumps since 2022; issue #12 (array_map&lt;char,bool&gt; fails to compile) open; no custom allocator.

## Caveats and trade-offs

The numbers are on the hat-trie README benchmark section (the array-hash README only links to the author's blog benchmark at tessil.github.io, which is egress-blocked here and was not read, and to the hat-trie page). Benchmark dates from 2017: GCC 6.3, a dual-core ultrabook CPU (i5-5200u, 8 GB), and the comparison set is std::unordered_map, tsl::hopscotch_map, google::dense_hash_map, spp::sparse_hash_map and the tries; absl::flat_hash_map and tsl::robin_map are not in the table, so the listed absl and robin baselines are not covered. Baseline stdlib is libstdc++ by inference (GCC on Debian Stretch), not stated outright. std::unordered_map is keyed on std::string (32 bytes minimum per key), which handicaps it on memory by design, and its insert wrapper in the gist (map.insert({str, value})) builds a std::pair&lt;const std::string, int&gt; temporary and then copies the const key into the node, so each baseline insert copies the key twice (small bias against the baseline; the same flaw is recorded for tsl::htrie_map). Insert is not faster without reserve (603.94 vs 590.88 ns/key on Wikipedia, 545.82 vs 554.02 on Askitis), and lookups are slower than tsl::hopscotch_map (138.24 vs 119.49 ns/key on Wikipedia) and about equal on Askitis, where google::dense_hash_map reads slightly faster (43.62, or 43.09 with reserve, vs 46.41). The Askitis read set (skew1_1) repeats keys heavily (177,999,203 lookups over short keys averaging 5.06 bytes), which favours cache-resident structures. The README says best of 20 runs, but the gist's Makefile builds one binary per structure and bench.cpp times a single pass with std::chrono::high_resolution_clock, so the 20-run driver is not public. Memory is read from /proc/self/statm (resident pages), and peak memory with array_map without reserve (823.54 MiB) is well above final memory (678.73 MiB) because rehash must copy strings (the README notes rehash is slow and needs spare memory). Lookups only test presence (nb_found counter), the value is not read. Flags were read through WebFetch summaries of the gist page, not a raw download (gist.githubusercontent.com is blocked). [retier] 2017 hat-trie README benchmark: long-key reads 1.70x faster than std::unordered_map (Wikipedia 138.24 vs 173.58 ns/key, Askitis 46.41 vs 105.05), but the lookups only test find() != end() and array_map never touches its separate values vector, so the value read is untimed; inserts without reserve (2.02 vs 1.68 s) and erases are slower, short-key reads trail robin_map, ska and hopscotch; no absl::flat_hash_map column; non-default StoreNullTerminator=false; best-of-20 driver not public. Only CI and CMake bumps since 2022. Filed under stdlib-replacements/hash-maps-sets by category override.

Header-only, C++11. Stores keys as packed char arrays instead of std::string, so there is no std::pair&lt;const Key,T&gt; and no stable references: any modifying operation invalidates iterators, references and pointers. Rehash is slow and needs spare memory because keys are copied (cannot be moved). Default max key size 65,535 and max 2^32 elements (template parameters). Erase may delay value destruction. Default hash is std::hash&lt;std::string_view&gt; or FNV-1a, so a faster hash (CityHash gives about 40% faster reads per the README) must be supplied by the user. Bucket-level API is missing.

## Maintenance

Maintenance mode rather than active: the last code change was in 2022 (std::max build fix, clang-format) and the 2023-2025 commits only update CI and CMake for v0.7.2 (2025-11-02); MIT, header-only and covered by an ASan/UBSan CI job, so it is easy to vendor, with the vector&lt;bool&gt; compile error (issue #12) still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The hat-trie README benchmark section lists tsl::array_map and std::unordered_map rows on the same harness; the benchmark code is public (gist Tessil/72e11891fc155f5b2eb53de22cbc4053: bench.cpp plus Makefile with CXXFLAGS -std=c++11 -march=native -DNDEBUG -O3 -lcityhash), compiler GCC 6.3 and CPU Intel i5-5200u are stated. Same evidence that holds the already-listed tsl::htrie_map at tier A.
- **Verifier notes:** All eight claimed figures match the hat-trie README rows exactly (Wikipedia shuffled and Askitis tables); metadata confirmed (MIT, 187 stars, last commit 2025-11-02, active). Not a duplicate: tsl::htrie_map (wave 9 verified, tier A) vendors array-hash under include/tsl/array-hash, but array_map is a separate standalone hash map with its own repo. Shortcomings to record: insert without reserve not faster, slower reads than tsl::hopscotch_map and dense_hash_map, 2017 hardware and no modern baselines (absl, robin_map), README's best-of-20 not in the public harness, baseline insert copies the key twice.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** modern comparison against absl::flat_hash_map and robin_map; lookup benchmark that reads the value
- **Pages the verifier opened:**
  - <https://github.com/Tessil/array-hash>
  - <https://github.com/Tessil/array-hash/commits>
  - <https://raw.githubusercontent.com/Tessil/array-hash/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tessil/array-hash/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Tessil/hat-trie/HEAD/README.md>
  - <https://gist.github.com/Tessil/72e11891fc155f5b2eb53de22cbc4053>
- **Sources the enricher read:**
  - <https://github.com/Tessil/array-hash>
  - <https://raw.githubusercontent.com/Tessil/array-hash/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tessil/array-hash/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Tessil/array-hash/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tessil/array-hash/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/Tessil/array-hash/HEAD/include/tsl/array_hash.h>
  - <https://raw.githubusercontent.com/Tessil/array-hash/HEAD/include/tsl/array_map.h>
  - <https://raw.githubusercontent.com/Tessil/array-hash/HEAD/include/tsl/array_set.h>
  - <https://raw.githubusercontent.com/Tessil/array-hash/HEAD/include/tsl/array_growth_policy.h>
  - <https://github.com/Tessil/array-hash/commits/master>
  - <https://github.com/Tessil/array-hash/issues?q=is%3Aissue>
  - <https://github.com/Tessil/array-hash/issues/12>
  - <https://github.com/Tessil/array-hash/issues/9>
  - <https://raw.githubusercontent.com/Tessil/hat-trie/HEAD/README.md>
  - <https://gist.github.com/Tessil/72e11891fc155f5b2eb53de22cbc4053>
  - <https://github.com/Tessil/tessil.github.io/tree/master/_posts>
  - <https://raw.githubusercontent.com/Tessil/tessil.github.io/master/_posts/2016-08-29-benchmark-hopscotch-map.md>
  - <https://raw.githubusercontent.com/Tessil/tessil.github.io/master/_posts/2017-06-22-hat-trie.md>
  - <https://raw.githubusercontent.com/Tessil/tessil.github.io/master/other/hopscotch_map_benchmark_raw_results.csv>
  - <https://raw.githubusercontent.com/Tessil/tessil.github.io/master/other/hash_table_benchmark.html>
  - <https://raw.githubusercontent.com/Tessil/hash-table-shootout/master/src/tsl_array_map.cc>
  - <https://raw.githubusercontent.com/Tessil/hash-table-shootout/master/src/tsl_array_map_mlf_1_0.cc>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/tessil/array-hash`) · [data/wave9/enrich/raw/github_com_tessil_array_hash.json](../../../data/wave9/enrich/raw/github_com_tessil_array_hash.json) (enrichment confidence 0.85)

</details>
