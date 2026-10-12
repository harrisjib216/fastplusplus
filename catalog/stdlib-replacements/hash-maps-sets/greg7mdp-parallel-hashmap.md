# parallel-hashmap (phmap)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only, Abseil-derived flat/node hash maps and a btree; drop-in for std::unordered_map/map, \~3x faster inserts.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | Writeup: "the Abseil flat_hash_map is significantly faster that the default stl implementation, typically about three times faster". That quote is literally about absl::flat_hash_map vs VS2017 std::unordered_map. phmap's own flat/parallel maps are graphed as nearly indistinguishable from it, and parallel_flat_hash_map is slightly slower for small tables and converges above \~80M values. Repo raw data (benchmark/results/output_stl_flat_par), 100M random inserts: std::unordered_map 48.38 s vs phmap::flat_hash_map 14.41 s vs phmap::parallel_flat_hash_map 14.47 s, \~3.4x (derived from repo data). |
| **Workload** | Inserting up to 100 million key/value pairs (two 8-byte integers) into phmap::flat_hash_map vs std::unordered_map, per the project's online design writeup. |
| **Metric** | throughput |
| **Compiler and flags** | Visual Studio 2017 MSVC (cl -EHsc -DNDEBUG -O2 per benchmark/Makefile), 64-bit, run from Cygwin |
| **Adoption** | 3.2k stars, 313 forks |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/greg7mdp/parallel-hashmap) · [benchmark](https://greg7mdp.github.io/parallel-hashmap/) |

## Verdict

Per the record's verification of the repo's own raw benchmark data (100M random 8-byte-integer-key inserts, MSVC Visual Studio 2017, cl -EHsc -DNDEBUG -O2, CPU model not stated): std::unordered_map took 48.38s vs phmap::flat_hash_map 14.41s vs phmap::parallel_flat_hash_map 14.47s, roughly 3.4x faster than std::unordered_map. The writeup's own '\~3x faster' sentence actually describes absl::flat_hash_map vs VS2017's std::unordered_map, not phmap directly.

## Use it when

- Insert/lookup-heavy replacement for std::unordered_map/set where you can accept flat_hash_map's pointer/iterator invalidation on mutation.
- Need pointer stability but still want a faster-than-std table: use node_hash_map/set instead of flat.
- Multithreaded code with a few large maps read/written from many threads: parallel_flat_hash_map/parallel_node_hash_map with an explicit mutex template argument (std::mutex, boost::shared_mutex, etc.) and if_contains/modify_if/try_emplace_l.
- Header-only C++11 codebase (old GCC/Clang/MSVC, embedded/toolchain-constrained) that can't pull in full Abseil.
- Want a std::map/set-like ordered container with lower memory than a red-black tree: btree_map/btree_set family.

## Skip it when

- Code relies on std::unordered_map/std::map pointer/iterator stability across mutation: flat_hash_map and all btree containers move elements in memory on rehash/mutation.
- Highly skewed concurrent insert workloads (most inserts hitting one key/submap): parallel_flat_hash_map throughput collapses under submap-lock contention (repo issue #215: 240M inserts, \~239M identical keys, CPU usage dropped to \~19%, 233s vs 17s for a Windows concurrent_unordered_map).
- Assuming built-in thread safety: the parallel_\* default mutex is NullMutex (no locking); concurrent read+write without supplying a real mutex template parameter is undefined behavior and has produced real crashes (issue #181, EXC_BAD_ACCESS).
- Need Abseil's randomized iteration order for DoS resistance against adversarial keys: phmap disables that randomization by default (opt-in via PHMAP_NON_DETERMINISTIC).
- Large, expensive-to-move value types (roughly &gt;100 bytes per README's own caveat): flat_hash_map's in-place moves get costly; node_hash_map is the safer choice.

## How it is fast

Uses Abseil's swiss-table design: an open-addressed table with a parallel one-byte-per-slot metadata array probed with SSE2 (checks 16 slots at once), letting load factor run up to 87.5% before resizing. flat_hash_map/set store keys and values directly in the bucket array (no per-node allocation/indirection). parallel_\* variants split the table into N (default 16) independently resizable submaps, which lowers peak resize memory and lets different threads lock different submaps concurrently.

## Compared with alternatives

phmap is the only sibling that bundles flat AND node hash variants, submap-sharded parallel_\* variants with built-in per-submap locking, and a btree ordered-map family in one header-only, actively maintained package — pick it over ska::flat_hash_map/tsl::robin_map/sparsepp/Verstable when you specifically want that locking-capable multithreaded variant or the flat/node choice, and over libcuckoo when your concurrency needs are moderate (a few large maps, not massively parallel) since phmap's parallel_\* design loses badly under heavy single-key contention (issue #215) where libcuckoo's design is built for exactly that.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none required; optional Abseil headers (include before phmap.h + define PHMAP_USE_ABSL_HASH) to use absl::Hash instead of std::hash, optional boost::hash_value() support |
| **Minimum toolchain** | C++11 required (C++14/17 APIs like try_emplace available when the compiler supports them); GCC 4.7+, Xcode/Apple clang 4.2.1+, MSVC roughly VS2015 update3+ per phmap_config.h version gate; README states CI coverage on GCC 4.8-12, Clang 3.9-16, VS2015/2017/2019/2022, Intel 18/19 |
| **Platforms** | tested on Windows, Linux, macOS; x86/x86-64 uses SSE2 for the parallel probe (per swiss-table design); phmap_config.h also has __arm__/__aarch64__ branches, so ARM builds are supported through the portable path |
| **Thread safety** | Follows std library rules: a single table is safe for concurrent reads only; concurrent read+write to the same table needs external synchronization unless using a parallel_\* table instantiated with a mutex type as the last template parameter, in which case if_contains()/modify_if()/try_emplace_l()/lazy_emplace_l() lock at the submap level. Iterators/references from standard APIs are never protected by that mutex. |
| **Drop-in for the baseline** | partial — explain: same insert/find/erase/iterator surface as std::unordered_map/std::map, but under the phmap:: namespace, with different iterator/pointer invalidation guarantees for flat_hash_\* and btree_\* (elements move in memory), and no synchronization at all unless you opt into the parallel_\* variants with a mutex. |

## Gotchas

- flat_hash_map/set and all btree containers can relocate stored elements in memory on mutation, invalidating pointers/iterators — unlike std::unordered_map/std::map. Use node_hash_map/set if you need stability.
- parallel_\* tables default to NullMutex (no locking); you must supply a real mutex type as the template's last parameter to get thread-safe concurrent access, or you risk crashes under concurrent read/write (issue #181).
- parallel_\* insert throughput can collapse under extreme key skew because most threads contend for the same submap's lock (issue #215: near-total single-key workload dropped to \~19% CPU use and lost to a naive concurrent map).
- Abseil-style randomized iteration order (DoS mitigation) is off by default in phmap; enable explicitly with #define PHMAP_NON_DETERMINISTIC 1 before including phmap.h if that matters for your use case.

## Caveats and trade-offs

The '\~3x faster' sentence in the writeup refers to Abseil's flat_hash_map, of which phmap is a header-only derivative. The phmap-vs-std number comes from the repo's raw results CSV and graphs, not from a sentence. No CPU model is stated anywhere, so it is capped at Tier C. The benchmark is insert-only with random 8-byte integer keys on MSVC 2017 STL only (no libstdc++/libc++). The results date from \~2019.

flat_hash_map/flat_hash_set move keys and values in memory, so pointers/iterators are invalidated on mutation, unlike std::unordered_map's node-based stability; node_hash_map avoids that at some speed/memory cost; the parallel_\* variants add multithreading support and lower peak resize memory at the cost of being slightly slower for small tables. The author now steers new users to the C++20 successor repo 'gtl' (also by greg7mdp, not filed separately here since it shares the same design and no independent benchmark was found for it).

## Maintenance

Actively maintained (last commit 2026-09-10, 3.2k stars, Apache-2.0, header-only so trivially vendorable), but the author is directing new feature development to the C++20 successor repo 'gtl'; treat parallel-hashmap as the stable C++11-compatible branch rather than where new capabilities land.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The writeup graphs insertion of up to 100M values into std::unordered_map (VS2017) vs flat_hash_map vs parallel_flat_hash_map. It links the repo with benchmark/bench.cc, a Makefile (cl -EHsc -DNDEBUG -O2) and raw CSV results. The compiler is named, but no CPU model is stated anywhere, so it stays C.
- **Verifier notes:** Real, notable entry (3,217 stars, Apache-2.0, active, last commit 2026-09-10). The record's caveat saying there was no linked raw data or script was wrong: the writeup links the repo, which contains benchmark/bench.cc, the Makefile and CSV results. Tier C unchanged.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** On 1M uint64 keys phmap::flat_hash_map found hits in 14.625 ns vs 18.911 ns for developer source's own SIMD Swiss table (1.29x) and 33.687 ns for std::unordered_map, and misses in 7.006 ns vs 9.723 ns (1.39x) and 44.665 ns (6.4x). It lost build-from-empty to the in-repo map, 38.07 vs 34.72 ns per key (1.10x). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-02-core); On a closed 92-key C++ keyword set (200k words, 1:8 keyword:identifier) phmap::flat_hash_map took 19.787 ns per lookup vs 5.322 ns for a compile-time perfect hash table (3.7x slower) and 29.168 ns for std::unordered_map. (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-02-libraries); At 1M uint64 keys phmap::btree_map beat std::map 18.72x on in-order iteration (7.106 vs 133.05 ns per element), 3.89x on lower_bound range queries (255.2 vs 991.946 ns) and 3.65x on build from random key order (267.5 vs 977.2 ns). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party); Inversion: at 10k cache-resident keys std::map beat phmap::btree_map on lookups, 36.773 vs 54.947 ns for hits (std::map 1.49x) and 38.3 vs 53.7 ns for misses, while btree_map won 1M-key lookups by only 1.26x. Iteration still favoured btree_map at 10k (1.16 vs 9.14 ns, 7.9x). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://greg7mdp.github.io/parallel-hashmap/>
  - <https://github.com/greg7mdp/parallel-hashmap>
  - <https://github.com/greg7mdp/parallel-hashmap/blob/master/benchmark/BENCHMARK.md>
  - <https://github.com/greg7mdp/parallel-hashmap/blob/master/benchmark/Makefile>
  - <https://github.com/greg7mdp/parallel-hashmap/blob/master/benchmark/results/output_stl_flat_par>
- **Sources the enricher read:**
  - <https://github.com/greg7mdp/parallel-hashmap>
  - <https://github.com/greg7mdp/parallel-hashmap/blob/master/README.md>
  - <https://github.com/greg7mdp/parallel-hashmap/blob/master/parallel_hashmap/phmap_config.h>
  - <https://github.com/greg7mdp/parallel-hashmap/issues/215>
  - <https://github.com/greg7mdp/parallel-hashmap/issues/181>
  - <https://github.com/greg7mdp/parallel-hashmap/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/greg7mdp/parallel-hashmap`) · [data/wave1/enrich/raw/github_com_greg7mdp_parallel_hashmap.json](../../../data/wave1/enrich/raw/github_com_greg7mdp_parallel_hashmap.json) (enrichment confidence 0.75)

</details>
