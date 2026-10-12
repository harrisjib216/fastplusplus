# SIGMOD 2025 Contest Solution - Hash Join Pipeline (Robin Hood/Hopscotch/Cuckoo/Unchained)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Coursework hash-join pipeline: four custom open-addressing tables plus a columnar 'Unchained' design that beat std::unordered_map on an IMDB join benchmark.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | README summary: std::unordered_map baseline \~112 s; Part 1 custom tables \~108 s (\~3%); Part 2 column store + Unchained \~16 s; Part 3 parallel \~7 s; 'Final speedup: \~16x faster than baseline' covers the whole pipeline, including late materialization, column store and 14-core parallelism, against a single-threaded baseline. Like-for-like hash-table swaps (REPORT.md, 113 queries): row store, Cuckoo 108,366 ms vs std::unordered_map 111,923 ms (\~1.03x); Column_t layout, Hopscotch 22,578 ms vs std::unordered_map 24,696 ms total (\~1.09x, derived from page data) and 12,383.89 vs 14,560.06 ms hash insert+lookup (\~1.18x, derived from page data); single-threaded Unchained hashtable 7,343.33 ms insert+lookup / 15,698 ms total vs Column_t std::unordered_map 14,560.06 / 24,696 ms (\~2.0x / \~1.57x, derived from page data). |
| **Workload** | Hash-join pipeline over the IMDB dataset (SIGMOD 2025 Programming Contest query set), comparing a std::unordered_map-based join baseline against custom open-addressing hash tables (Robin Hood, Hopscotch, Cuckoo) and then a custom 'Unchained' hashtable with columnar late-materialization and parallel build/probe. |
| **Metric** | latency |
| **Hardware** | MacBook Pro, Apple M4 Pro (14 cores), 48GB RAM |
| **Compiler and flags** | CMake -DCMAKE_BUILD_TYPE=Release plus -march=native (CMakeLists.txt). The README lists 'Clang 18 (recommended)' as a prerequisite but does not state the compiler actually used. |
| **Adoption** | 1 star |
| **Last commit** | 2026-08-08 |
| **Links** | [repository](https://github.com/ArisS44/Sigmod-2025-contest-solution) · [benchmark](https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/REPORT.md) |

## Verdict

On a 113-query IMDB hash-join benchmark (MacBook Pro, Apple M4 Pro, 14 cores, 48GB RAM; CMake Release + -march=native; compiler unstated), swapping std::unordered_map for the Unchained hashtable cut single-threaded hash insert+lookup time from 14,560ms to 7,343ms (\~2.0x) and column-store total runtime from 24,696ms to 15,698ms (\~1.57x), per REPORT.md's per-stage tables. Robin Hood, Hopscotch, and Cuckoo alone (row-store, Part 1) were only 3-18% faster than std::unordered_map. The repo's own 'Final speedup: \~16x' headline additionally folds in column-store layout, late materialization, and 14-core parallel execution against a single-threaded baseline -- it is not a hash-table-vs-std::unordered_map number.

## Use it when

- You want a worked, single-file reference for Robin Hood, Hopscotch, Cuckoo, or 'Unchained' (directory + adjacency array + Bloom tags) hashing in modern C++17.
- You're building your own analytical hash-join engine over int32 join keys and can adopt the surrounding column-store/late-materialization design, not just swap a container.
- Build-then-probe multimap workloads (many row-ids per key) rather than a general mutable map with deletes.
- 8-16+ core x86-64 or aarch64 machines where a work-stealing parallel build/probe pipeline amortizes across many queries.
- Benchmarking/prototyping hash-table variants against std::unordered_map on your own dataset before picking one.

## Skip it when

- You need a drop-in std::unordered_map replacement: the API is insert(key,row)/find(key), not the STL container interface (no erase, no iterators, no operator[]), and only int32 keys are exercised in tests/benchmarks despite the Key template parameter.
- You need a thread-safe table for concurrent insert/lookup from multiple threads on one instance: none of the four tables have internal synchronization -- the repo's own parallelism partitions data across separate thread-local structures instead.
- Your target lacks SSE4.2 (x86) or the ARM CRC32 extension: Unchained.hpp hashes via hardware CRC32 intrinsics (nmmintrin.h / arm_acle.h) with no portable software fallback.
- You need key deletion: none of the four HashMultiMap implementations expose remove/erase.
- You need production maturity: 1-star, 3-student university coursework repo with no independent replication and no issue/CVE history to check.

## How it is fast

Part 1's three tables use open addressing to shorten probe chains versus std::unordered_map's separate chaining: Robin Hood displaces by probe-sequence length, Hopscotch checks a 32-64-slot neighborhood bitmap, Cuckoo uses two tables with a splitmix64 second hash -- this alone is only \~3-18% faster. Most of the headline speedup comes from architecture: late materialization defers string payloads to (table,column,page,offset) references, an 8KB-paged column-store improves sequential access, and 'Unchained' sorts tuples by hash prefix into one contiguous adjacency array with a directory of precomputed 16-bit Bloom-filter tags per slot, trading pointer chasing for sequential scans and rejecting most misses before touching the array. Part 3 parallelizes tuple collection/build/probe across 16 threads via a 3-level slab allocator (each thread owns a private memory region, no allocator contention) and atomic-counter work stealing over fixed-size chunks.

## Compared with alternatives

Pick this over the catalogued sibling hash maps only when you want a worked example of pairing a hash table with a column-store + late-materialization join pipeline and parallel build/probe, and are willing to extract and adapt a header (e.g. RobinHoodHash.hpp) yourself. For a maintained, general-purpose std::unordered_map replacement, prefer emhash, tsl::robin_map, or ska::flat_hash_map -- all have broader validation, non-coursework provenance, and don't require hardware CRC32 support.

## Integration

| | |
|---|---|
| **Form** | header-only for Robin Hood/Hopscotch/Cuckoo (single .hpp each); source-drop for Unchained (Unchained.hpp + Unchained.cpp, plus slab_allocator/tuple_collector/parallel_probing headers if you want the parallel build) |
| **Dependencies** | none for the hash tables themselves beyond the C++ standard library, plus hardware CRC32 intrinsics for Unchained only (nmmintrin.h on x86 / arm_acle.h on ARM). The surrounding application pulls in abseil, re2, nlohmann/json, sql-parser, range-v3, fmt, DuckDB, and Catch2 via CMake FetchContent, but those are not required to use the hash tables in isolation. |
| **Minimum toolchain** | C++17 (CMakeLists.txt sets CMAKE_CXX_STANDARD 17), CMake &gt;= 3.16; README recommends 'Clang 18 (recommended)' but the compiler actually used to produce the published numbers is not stated |
| **Platforms** | x86-64 (SSE4.2 needed for Unchained's CRC32 intrinsic) or aarch64 (ARM CRC32 feature); CMakeLists.txt unconditionally adds -march=native except on PowerPC, so built binaries are tied to the build machine's CPU unless that flag is changed |
| **Thread safety** | not documented / not thread-safe for concurrent access to a single table instance -- insert() and find() have no locking or atomics in any of the four implementations |
| **Drop-in for the baseline** | partial — explain: same insert-then-lookup usage pattern as std::unordered_map for multimap-style joins, but the API (insert(key,row_idx), find(key)-&gt;vector&lt;size_t&gt;\*) is not the STL container interface, so call sites need adapting rather than a type swap |

## Gotchas

- Robin Hood (max_load 0.4) and Cuckoo (max_load 0.6) rehash by doubling; Cuckoo caps kick-outs at max_kicks=512 before forcing a full rehash+reinsert, a latency spike on adversarial key sets.
- Hopscotch throws std::runtime_error('Rehash failed during rehashing...') if neighborhood displacement fails while already rehashing -- an unguarded abort path under pathological hash distributions rather than a graceful fallback.
- Unchained caches a 64-bit CRC32-derived hash per tuple (HashTuple.hash) and reuses it across build passes to avoid recomputing CRC32+multiplication; if you repurpose the struct, keep that field in sync with your own hash function.
- All four tables are templated on Key via std::hash&lt;Key&gt;, but only int32 join keys are covered by the benchmarks and unit tests -- correctness/performance for string or composite keys is not demonstrated.

## Caveats and trade-offs

University of Athens K23a coursework (3 students, 1 star), with no independent replication. The \~16x headline mostly comes from architecture (late materialization, column store) and 14-core parallelism against a single-threaded std::unordered_map baseline. Swapping the hash table alone gives about 3-18%, and the Unchained table about 1.6-2x single-threaded. libc++ is inferred from the macOS toolchain and is not stated. The compiler actually used is not stated.

This is a full application pipeline built for one contest workload (column-store, late materialization, custom slab allocator, work-stealing parallel probe), not a drop-in std::unordered_map replacement library -- the individual header files (RobinHoodHash.hpp, HopscotchHash.hpp, CuckooHash.hpp, Unchained.hpp) could be extracted, but only \~3% of the eventual 16x came from swapping the hash table itself; the rest came from column-store layout and parallelism. Single dataset (IMDB) benchmark.

## Maintenance

Last commit 2026-08-08 (active), but this is University of Athens K23a coursework by 3 students with 1 star, zero pull requests, and no bug-tagged issues to check; MIT-licensed and small enough to vendor the individual headers, but treat it as a reference implementation rather than a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party coursework numbers. The code and CPU (Apple M4 Pro) are public and stated, and CMake gives Release plus -march=native. However, the README lists only 'Clang 18 (recommended)' as a prerequisite and never says which compiler produced the numbers, so this is not A. The headline 16x is also not a hash-table-vs-std::unordered_map comparison.
- **Verifier notes:** Downgraded A to C. The compiler is only 'recommended', and the 16x figure overstates the hash table's own contribution. I pointed benchmark_url to REPORT.md (Greek), which has per-hash-table insert/lookup timings. Metadata checked: MIT, 1 star, last commit 2026-08-08 (active), not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution#performance-summary>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/REPORT.md>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/CMakeLists.txt>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/runtimes/unorderedmap.txt>
- **Sources the enricher read:**
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/README.md>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/REPORT.md>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/CMakeLists.txt>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/include/RobinHoodHash.hpp>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/include/HopscotchHash.hpp>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/include/CuckooHash.hpp>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/include/Unchained.hpp>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/blob/main/include/hash.hpp>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/issues>
  - <https://github.com/ArisS44/Sigmod-2025-contest-solution/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/ariss44/sigmod-2025-contest-solution`) · [data/wave1/enrich/raw/github_com_ariss44_sigmod_2025_contest_solution.json](../../../data/wave1/enrich/raw/github_com_ariss44_sigmod_2025_contest_solution.json) (enrichment confidence 0.55)

</details>
