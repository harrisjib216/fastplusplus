# ska::flat_hash_map / ska::bytell_hash_map

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSL-1.0` · 🔴 abandoned

> Header-only Robin Hood open-addressing hash map/set beating std::unordered_map on lookups, inserts, and erases.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | Ankerl 2022, normalized runtimes with the same hash for both maps (the verifier computed the ratios std::unordered_map / ska from the page's table data). flat_hash_map: geometric mean over all tests 2.06-2.32x; number find 2.8-3.6x; string find 1.55-1.95x; random insert & erase 4.0-4.6x; but iteration is slower at 0.79-0.97x, and Ankerl states it is 'not the fastest hashtable in any of my benchmarks'. bytell_hash_map: geometric mean 2.12-2.31x; insert-then-erase 4.4-4.6x. Tessil 2017 shootout raw CSV: flat_hash_map successful lookups 1.34-4.17x faster than std::unordered_map, inserts 0.84-3.18x. In his 2017 post the author claims 'I have the fastest lookups of any hashtable I could find', with results as graphs only. |
| **Workload** | Successful/unsuccessful lookups, inserts (with/without reserve), erases, and mixed insert/erase sequences, on int and string keys with 4-, 32-, and 1024-byte values. |
| **Metric** | latency |
| **Hardware** | Intel i7-8700 locked at 3200 MHz, Manjaro Linux (Ankerl 2022) |
| **Compiler and flags** | clang++ 13, -O3 -march=native (Ankerl 2022) |
| **Adoption** | 1858 stars |
| **Last commit** | 2018-07-15 |
| **Links** | [repository](https://github.com/skarupke/flat_hash_map) · [benchmark](https://martin.ankerl.com/2022/08/27/hashmap-bench-01/) |

## Verdict

Ankerl 2022 (martinus/map_benchmark; clang++13 -O3 -march=native; Intel i7-8700 @3200MHz; libstdc++), normalizing to the same hash function for both sides, measured ska::flat_hash_map at 2.06-2.32x std::unordered_map geometric-mean runtime (number find 2.8-3.6x, string find 1.55-1.95x, random insert/erase 4.0-4.6x, iteration 0.79-0.97x i.e. slightly slower) and ska::bytell_hash_map at 2.12-2.31x geomean (insert-then-erase 4.4-4.6x). The author's own 2017 post claims the fastest lookups he tested, but shows only graphs with no stated compiler or hardware.

## Use it when

- Hot lookup/insert/erase paths on int or short string keys, single-threaded, where you control hash quality: Ankerl 2022 shows 2.06-2.32x geomean over libstdc++ std::unordered_map with the same hash.
- Sizes known up front (reserve()-able) with light iteration, since the gain is on insert/erase/find, not on scanning.
- Insert/erase churn workloads, especially with bytell_hash_map (insert-then-erase \~4.4-4.6x vs std::unordered_map) where the 0.9375 load factor also keeps memory tight.
- Small vendorable dependency for game/offline C++11-14 code that can't take on Abseil or a newer-toolchain-only library.
- Trusted, non-adversarial key inputs (internal data, not user-controlled strings from the network).

## Skip it when

- Iteration-heavy code: flat_hash_map's iteration is 0.79-0.97x std::unordered_map (Ankerl 2022) and described by that benchmark as one of the slowest tested; memory use is also high.
- bytell_hash_map erase-during-iteration loops: issue #41 reports duplicate elements returned after erase() while iterating; a fix was posted in comments but never merged.
- Builds using -O2 -DNDEBUG with bytell_hash_map: issue #11 reports a 'free(): invalid pointer' SIGSEGV traced to sherwood_v8_block::empty_block()'s static sentinel; unresolved since 2018.
- Untrusted/attacker-influenced keys: no seeded/randomized hashing (issue #17, 'Unsafe with attacker controlled keys'), same exposure as raw std::hash but with nobody patching it.
- Code shared across shared-library/module boundaries: issues #43 and #26 describe static-data (empty_default_table) problems when the header is instantiated in multiple translation units.
- Anywhere you rely on std::unordered_map's iterator/reference stability: backward-shift deletion relocates other elements on erase (issue #30, 'Insert invalidate iterators').

## How it is fast

Both use Robin Hood open addressing with backward-shift deletion (no tombstones) and cap worst-case probe length at max(4, log2(bucket_count)), so lookups stay bounded regardless of hash quality. flat_hash_map defaults to a fibonacci hash policy (multiply-shift, no modulo) with a low 0.5 max load factor to keep probe chains short; a power_of_two_std_hash wrapper opts into masking instead. bytell_hash_map keeps the same Robin Hood core but stores per-slot state in packed metadata blocks (a triangular-number jump-distance table) and raises max load factor to 0.9375, trading some speed for a smaller footprint.

## Compared with alternatives

Pick this over emhash, sparsepp, robin-map, or rigtorp::HashMap when the independent Ankerl 2022 head-to-head numbers (same-hash, normalized geomean) matter more than a vendor's own benchmark, or when you specifically want bytell_hash_map's lower memory overhead (0.9375 load factor) at some cost to lookup/iteration speed. Prefer an actively maintained sibling (e.g. tsl::robin_map, emhash) if you need try_emplace, bucket() semantics, or bug fixes — this repo has had zero commits since 2018-07-15 and 42 open issues, including the correctness/crash bugs above.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the STL (&lt;cstdint&gt; &lt;cstddef&gt; &lt;functional&gt; &lt;cmath&gt; &lt;algorithm&gt; &lt;iterator&gt; &lt;utility&gt; &lt;type_traits&gt;; bytell_hash_map.hpp additionally includes flat_hash_map.hpp, &lt;vector&gt;, &lt;array&gt;) |
| **Minimum toolchain** | C++11 (variadic templates, rvalue refs, allocator_traits; ships its own void_t shim rather than relying on C++14/17, so no later standard is required) |
| **Platforms** | any standard C++ target, no SIMD/intrinsics; open issues note past failures on 32-bit ARM (fix referenced in issue #18) and a still-open concern about jump_distances on x86 builds for bytell_hash_map (issue #37) |
| **Thread safety** | not documented; no locking or atomics in the source — treat as single-writer, same as std::unordered_map |
| **Drop-in for the baseline** | partial — explain: method names match std::unordered_map (operator[], at, emplace, insert, insert_or_assign, erase, find, equal_range, reserve, swap, max_load_factor, ==/!=), but there is no try_emplace (open issues #19/#21), no bucket()/bucket_count() on flat_hash_map/bytell_hash_map itself, and erase/rehash can relocate other elements' storage (Robin Hood backward-shift), unlike std::unordered_map's node-based stability. |

## Gotchas

- erase() performs backward-shift deletion: elements after the erased slot get moved in memory, invalidating their iterators/references too, not just the erased one's (sherwood_v3_table::erase; issue #30).
- bytell_hash_map: duplicate-item-after-erase bug when erasing during iteration (issue #41), fix posted in comments but never merged.
- bytell_hash_map: reported SIGSEGV under -O2 -DNDEBUG tied to sherwood_v8_block::empty_block()'s static sentinel (issues #11, #14), unresolved.
- No seeded hashing; adversarial keys can force worst-case probing exactly like plain std::hash (issue #17).

## Caveats and trade-offs

The author's 2017 post is graph-only, states no compiler or hardware, and predates bytell_hash_map (added in a 2018 post). An independent benchmark contradicts the 'fastest' claim, though both maps still beat std::unordered_map. flat_hash_map uses more memory and iterates slowly. The repo has no LICENSE file; BSL-1.0 is declared in each header. There have been no commits since 2018-07-15. This is a different repo from skarupke/ska_sort, which is on the known-list.

Robin Hood hashing with a log2(n) probe-count cap bounds worst-case lookup but adds complexity; default policy uses prime sizing (max load factor 0.5), power-of-two policy available as an alternative.

## Maintenance

Abandoned since 2018-07-15 with 42 open issues, including two unresolved correctness/crash bugs specific to bytell_hash_map; declared BSL-1.0 in every header despite GitHub showing no LICENSE file, so it's freely copyable and small enough to vendor and patch yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to B. The author's post alone is C: its results are graphs, it states no compiler, flags or hardware, and it links no benchmark code. The well-known independent Ankerl 2022 suite (martinus/map_benchmark; clang++ 13 -O3 -march=native; i7-8700; libstdc++) tests both ska::flat_hash_map and ska::bytell_hash_map at the repo's last commit 2c468743 and shows both beating std::unordered_map.
- **Retiered** B to A: Independent Ankerl 2022 suite: code martinus/map_benchmark src/maps/ska_flat_hash_map and src/maps/ska_bytell_hash_map vs src/maps/std_unordered_map, clang++ 13, -O3 -march=native, Intel i7-8700 locked at 3200 MHz. map_benchmark.js geomean std::unordered_map/ska = flat 2.25x/2.32x, bytell 2.29x/2.31x (mumx/robin_hood::hash).
- **Verifier notes:** Metadata checks out: 1858 stars, last commit 2018-07-15, abandoned, not a fork, not archived. GitHub reports no license, but all three headers state the Boost Software License 1.0, so BSL-1.0 and 'copyable' stand. benchmark_url now points to the independent Ankerl 2022 suite.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/skarupke/flat_hash_map>
  - <https://github.com/skarupke/flat_hash_map/blob/master/flat_hash_map.hpp>
  - <https://github.com/skarupke/flat_hash_map/blob/master/bytell_hash_map.hpp>
  - <https://github.com/skarupke/flat_hash_map/blob/master/unordered_map.hpp>
  - <https://probablydance.com/2017/02/26/i-wrote-the-fastest-hashtable/>
  - <https://martin.ankerl.com/2022/08/27/hashmap-bench-01/>
  - <https://martin.ankerl.com/files/2022/map_benchmark.js>
  - <https://github.com/martinus/map_benchmark>
  - <https://tessil.github.io/other/hopscotch_map_benchmark_raw_results.csv>
- **Sources the enricher read:**
  - <https://github.com/skarupke/flat_hash_map>
  - <https://github.com/skarupke/flat_hash_map/blob/master/flat_hash_map.hpp>
  - <https://github.com/skarupke/flat_hash_map/blob/master/bytell_hash_map.hpp>
  - <https://github.com/skarupke/flat_hash_map/blob/master/unordered_map.hpp>
  - <https://github.com/skarupke/flat_hash_map/issues>
  - <https://github.com/skarupke/flat_hash_map/issues/41>
  - <https://github.com/skarupke/flat_hash_map/issues/11>
  - <https://martin.ankerl.com/2022/08/27/hashmap-bench-01/>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/skarupke/flat_hash_map`) · [data/wave1/enrich/raw/github_com_skarupke_flat_hash_map.json](../../../data/wave1/enrich/raw/github_com_skarupke_flat_hash_map.json) (enrichment confidence 0.62)

</details>
