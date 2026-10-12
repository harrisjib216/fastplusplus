# EASTL hash_map / hash_set (eastl::hash_map)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> EA's chained hash table (eastl::hash_map/hash_set), about 1.3x faster than libstdc++ std::unordered_map in Ankerl's 2019 suite.

| | |
|---|---|
| **Beats** | std::unordered_map (directly in Ankerl's map_benchmark, Linux build); EASTL's own tables used the pre-standard stdext::hash_map of VC++ 7.1 (Dinkumware) and STLport's hash_map, and N2271 used GCC 4.1 libstdc++ |
| **Claimed result** | Ankerl map_benchmark all.txt (independent, g++-8 -O3 -march=native, taskset-isolated core): geomean 1.31x over std::unordered_map across 56 of 63 rows, result checksums identical; EASTL's own find_as/char\* rows (3.70x VC7.1, 12.49x STLport Debug, 1.04x STLport Release find) compare against a baseline that builds a temporary std::string per lookup |
| **Workload** | Independent: Ankerl map_benchmark 2019 workloads (random find at 200, 2,000 and 500,000 entries with 0-100% success, random insert/erase at 4-24 bits for 50M cycles, string find and string insert/erase, 100M-int insert/reinsert/remove/clear, iteration while adding/removing, distinct counting), same hash functor for both maps, five hashes. First-party: stopwatch (CPU cycles) comparison of eastl::hash_map against the compiler-supplied hash map on 10,000 random pairs with keys drawn from [0,5000), for uint32_t-&gt;TestObject and string-&gt;uint32_t, timing insert, find, operator[], count, erase, iteration and clear. |
| **Metric** | throughput |
| **Hardware** | Ankerl 2019 run: Intel i7-8700 at 3.2 GHz, one isolated core, frequency scaling disabled (search snippet only; blog blocked). EASTL doc/Benchmarks.md gives no CPU. N2271 lists Pentium 4 x86 (Windows and Linux columns), a 64-bit PowerPC console and a G5 PowerPC Mac, without exact models. |
| **Compiler and flags** | Ankerl map_benchmark: CMake Release; the current CMakeLists.txt sets -DNDEBUG -O3 -march=native, but the 2019 run's compiler version and flags are not confirmed (blog blocked). EASTL doc/Benchmarks.md: Microsoft Visual C++ 7.1 (version 1310), 'Full optimization. Inlining enabled' (exact flags not given), PPMalloc::GeneralAllocator. N2271: Windows column VC8 -Og -Oi -Ot -Oy -Ob2 -GF -Gy; Linux column GCC 4.1 -O3 with libstdc++. |
| **Adoption** | 9.4k stars, 1.0k forks; Electronic Arts' in-house STL replacement, open-sourced |
| **Last commit** | 2025-10-29 |
| **Links** | [repository](https://github.com/electronicarts/EASTL) · [benchmark](https://github.com/martinus/map_benchmark/blob/master/data/all.txt) |

## Verdict

In Martin Ankerl's 2019 map_benchmark, eastl::hash_map beat libstdc++ std::unordered_map using the same hash functor in 56 of 63 workloads: geomean 1.31x with robin_hood::hash and 1.31-1.42x across five hashes, random find 1.21-1.72x, insert/erase 1.05-1.77x (derived from page data). It lost on clear (0.53x), destruction (0.39x) and 5% and 100% distinct counting, and its result checksums matched std's in every row. The build per the repo at the time (tools/build.sh and CMakeLists.txt at commit 512810d) was g++-8 Release, -O3 -march=native, C++14, pinned with taskset to an isolated core pair of a 6-core/12-thread CPU with 4.6 GHz max; the blog names it an i7-8700 (snippet only). EASTL's first-party 0.96 tables (VC++ 7.1, against the pre-standard stdext::hash_map) show 1.2-3.8x, but near parity against STLport.

## Use it when

- Codebases already on EASTL, or built without exceptions, that want a std::unordered_map-shaped table with stable node addresses and EASTL's allocator model.
- Lookup-heavy maps of integers or short strings when the alternative is libstdc++ std::unordered_map: Ankerl's 2019 data show 1.2-1.7x faster random find at 200 to 500,000 entries with the same hash.
- Insert/erase churn on small-to-medium tables (Ankerl random insert/erase 1.26-1.77x faster than std at 4-24 bits).
- String-keyed maps queried by const char\* or by a precomputed hash (find_as, find_by_hash), which avoids building temporary keys.

## Skip it when

- When an open-addressing map is acceptable. In the same 2019 data absl::flat_hash_map is about 2.4x faster and robin_hood::unordered_flat_map about 2.9x faster (geomean), and EASTL wins none of 63 rows against either (derived from page data).
- When you need pointer stability and speed together. Node-stable maps also beat it there: absl::node_hash_map about 1.85x (EASTL wins 4 of 63 rows), robin_hood::unordered_node_map about 2.2x (wins 0) and folly::F14NodeMap about 1.3x (wins 16 of 64), all derived from page data.
- Teardown-heavy or iterate-and-erase workloads: clear of 100M ints ran at 0.53x of std, the destructor at 0.39x, iterate-while-removing at 0.84x and distinct counting at 0.80-0.85x. DoFreeNodes walks every bucket.
- Projects that would adopt EABase, EASTL's build and its operator new[] allocator hooks just for one container.

## How it is fast

It uses separate chaining with one singly linked list per bucket: a node is the value plus a next pointer, with no cached hash unless bCacheHashCode is set. Bucket counts come from a static prime table (index = hash % prime), with max load factor 1.0 and 2x growth. A new empty table points at a shared two-entry bucket array, so it allocates nothing, and a trailing non-null sentinel bucket keeps iteration's end check cheap. Its edge over libstdc++ is a constant factor within the same node-based design, not a different algorithm. In Ankerl's data it used less memory at 500k entries (11.3 vs 19.9 MB) and 24-bit insert/erase (312 vs 510 MB), but more at 100M ints (4153 vs 3986 MB).

## Compared with alternatives

Pick it only when you are already on EASTL or need its no-exceptions and allocator model. On speed, absl::flat_hash_map, robin_hood, tsl::robin_map and ska::flat_hash_map beat it in nearly every row of the same 2019 data, and node-stable alternatives (absl::node_hash_map, F14NodeMap) win most rows. It does beat boost::unordered_map 1.65 (about 1.15x geomean, derived from page data).

## Integration

| | |
|---|---|
| **Form** | static lib (headers plus source/hashtable.cpp, which defines the shared empty bucket array and the prime table) |
| **Dependencies** | EABase (CMake FetchContent); with the default allocator the application must define EASTL's two operator new[] overloads |
| **Minimum toolchain** | C++14 (target_compile_features cxx_std_14); hashtable.h did not compile under -std=c++14 until the October 2025 fixes (issue #585, commits #586/#588) |
| **Platforms** | any (portable C++, no SIMD or platform-specific code in hashtable.h) |
| **Thread safety** | No internal locking, so concurrent mutation needs external synchronization; hashtable.h avoids writing the global shared empty-bucket array so that empty tables in different threads do not race |
| **Drop-in for the baseline** | partial: same member-function shape and node/reference stability as std::unordered_map, but a different namespace, allocator model and type, so APIs taking std::unordered_map need changes |

## Gotchas

- reserve(n) always rehashes: it allocates a new bucket array, relinks every node and frees the old one, even when the bucket count would not change. With n below size() it shrinks the bucket count, so the load factor rises until the next insert triggers growth (hashtable.h reserve, rehash and DoRehash; issue #521 has been open since 2023 with no maintainer reply).
- begin() and iterator increment scan empty buckets, and clear() keeps the bucket array (clear(true) frees it). begin() on a large, mostly empty table is O(bucket_count), so erase(begin()) loops can turn quadratic.
- EASTL's own benchmark tables mislead on two rows. The find_as/char\* rows compare EASTL's find_as with the baseline's find(c_str()), which builds a temporary std::string per lookup, so most of the 3.70x (VC++ 7.1), 2.73x (STLport Release) and 12.49x (STLport Debug) gain is that conversion; STLport Release find is 1.04x. The uint32_t maps in benchmark/source/BenchmarkHash.cpp also use each library's default hash (std::hash vs eastl::hash) instead of a shared functor.
- With bCacheHashCode=true the hash code is stored and used as uint32_t, so the high 32 bits of a 64-bit hash are dropped; the default (false) uses the full size_t hash modulo a prime. The rehash policy works in uint32_t, and the largest bucket count is 4294967291.

## Known shortcomings

- Raised C to B on Ankerl's 2019 map_benchmark raw data (martinus/map_benchmark data/all.txt): EASTL faster than std::unordered_map on 56 of 63 rows, geomean 1.31x (derived from page data), but about 2.4x behind absl::flat_hash_map and 2.9x behind the robin_hood flat map and slower on clear/destroy; 2019 toolchain unconfirmed, i7-8700 from a snippet only. The repo's own Benchmarks.md compares against pre-standard stdext::hash_map, is near parity with STLport and slower than libstdc++ 4.1 on find (N2271).
- Enricher: the Ankerl all.txt geomean recomputes to 1.31x over 56 of 63 rows with result checksums identical to std in every row; EASTL's own find_as/char\* rows compare against a baseline find(c_str()) that builds a temporary std::string per lookup (3.70x VC7.1, 12.49x STLport Debug; STLport Release find only 1.04x); the uint32 rows use different default hashes; reserve() always rehashes and can shrink buckets (issue #521); the 2019 toolchain is confirmed in map_benchmark history (tools/build.sh g++-8 Release, -O3 -march=native C++14 at 512810d, taskset-isolated core on a 6C/12T 4.6 GHz CPU) while the i7-8700 name is snippet-only.

## Caveats and trade-offs

Independent evidence: Martin Ankerl's 2019 hashmap benchmark (raw results in data/all.txt of github.com/martinus/map_benchmark, whose lineup of boost 1_65_1, emilib1, spp and eastl::hash_map matches the 2019 run) timed eastl::hash_map against std::unordered_map with the same hash functor; EASTL is faster in 56 of 63 workload rows (geomean 1.31x with robin_hood::hash, derived from page data) but loses on clear of 100M ints (0.53x), destruction (0.39-0.51x), iterate while removing (0.84x), 100% distinct counting (0.85x) and empty-map construct/destroy (about 0.03 s vs a std time of about 1e-7 s, i.e. std's was optimized away). The same data shows the chained, node-based EASTL map far behind flat maps: absl::flat_hash_map about 2.4x faster and robin_hood::unordered_flat_map about 2.9x faster (geomean, EASTL wins 0 of 63 rows against either), folly::F14ValueMap about 1.6x faster (EASTL wins 10 of 63); EASTL beats boost::unordered_map 1.65 by about 1.11x (all derived from page data). The 2019 blog page (martin.ankerl.com) is blocked here; its i7-8700 machine, isolated core and disabled frequency scaling come from a search snippet only, and the 2019 compiler version and flags are not confirmed (the current CMakeLists.txt sets -DNDEBUG -O3 -march=native). The eastl adapter is no longer in map_benchmark's src/maps at HEAD, the 2022 rerun dropped EASTL, and the 2019 overview calls EASTL 'a bit dated' (snippet). First-party tables: doc/Benchmarks.md (EASTL 0.96.00, Win32, Microsoft Visual C++ 7.1, PPMalloc allocator, no CPU, 'Full optimization. Inlining enabled' without exact flags, single stopwatch run in CPU cycles, no variance) compares against the pre-standard stdext::hash_map of the Dinkumware STL and STLport's hash_map, not std::unordered_map; against STLport in Release EASTL is near parity and slower on uint32 find (0.81x) and insert (0.90x). The 2007 WG21 paper N2271 (doc/EASTL-n2271.pdf, by EASTL's author) Linux column (Pentium 4, GCC 4.1 -O3, libstdc++) shows uint32-key find 0.76x, insert 0.91x, operator[] 1.37x and string-key find 0.75x, iteration 0.54x, insert 3.52x, operator[] 3.00x, so EASTL was slower than libstdc++ on find. The current benchmark/source/BenchmarkHash.cpp targets std::unordered_map (10,000 pairs, keys in [0,5000), FNV-1a string hash for both) but its results are not published, and the tables are cache-resident. The library-wide claim in doc/Design.md and doc/FAQ.md that 'EASTL is faster than all existing STL implementations' is not supported for this facility. hash_set has no separate numbers; the record covers hash_map. [retier] First-party find_as rows pit a c_str lookup against std::string construction; uint32 rows use different default hashes; reserve() always rehashes and can shrink buckets (issue #521); CPU name snippet-only

Node-based separate-chaining table (hashtable.h: prime bucket counts, load-factor rehash policy, optional cached hash code via bCacheHashCode), so it keeps std::unordered_map's pointer and reference stability and its cache behaviour, not an open-addressing layout. Adds find_as and heterogeneous lookup to avoid temporary string keys. The default allocator model needs the application to supply the EASTL operator new[] overloads (name, flags, alignment arguments). Different types from std, so no drop-in interchange with std::unordered_map in APIs.

## Maintenance

Actively maintained: last commit 2025-10-29 with C++14 build fixes, 9.4k stars, BSD-3-Clause. It is usable today, but the measured advantage is over std::unordered_map only, its own tables are about 20 years old, and the 2022 rerun of Ankerl's suite dropped it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to B: Martin Ankerl's well-known independent hashmap benchmark (2019 run, raw results in martinus/map_benchmark data/all.txt) timed eastl::hash_map directly against std::unordered_map with the same hash and shows EASTL faster in 56 of 63 rows (geomean 1.31x, derived from page data). Not A: the eastl adapter is gone from the suite's HEAD, the 2019 compiler version and flags are unconfirmed, and the CPU (i7-8700) comes from a search snippet; EASTL's own doc/Benchmarks.md (VC++ 7.1, no CPU, inexact flags) alone would be C.
- **Retiered** B to A: Enricher (2026-10-12): the independent Ankerl map_benchmark run is fully reproducible: tools/build.sh with g++-8 Release, CMakeLists at 512810d sets -O3 -march=native C++14, runs were pinned with taskset on an isolated core of a 6C/12T 4.6 GHz CPU, and the all.txt rows recompute to a 1.31x geomean over 56 of 63 rows with result checksums identical to std; the CPU is named (i7-8700) only in a search snippet, which is the one residual gap.
- **Verifier notes:** Numbers in the record match doc/Benchmarks.md's Win32.VC71.MS.Release table exactly (uint32 iteration 1.18x was omitted; added). Upgraded to B on Ankerl's third-party raw data, where eastl::hash_map beats std::unordered_map about 1.3x geomean but trails absl::flat_hash_map about 2.4x and robin_hood flat map about 2.9x and loses on clear/destroy. Shortcomings: 20-year-old first-party tables against pre-standard hash_map, near parity with STLport, slower than libstdc++ on find in N2271, eastl adapter dropped from the current suite, 2019 toolchain unconfirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-73 (wave 1, stdlib decomposition); enricher (wave 1 stdlib seeds, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/Benchmarks.md>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/benchmark/source/BenchmarkHash.cpp>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/EASTL-n2271.pdf>
  - <https://github.com/electronicarts/EASTL>
  - <https://github.com/electronicarts/EASTL/commits>
  - <https://github.com/martinus/map_benchmark>
  - <https://github.com/martinus/map_benchmark/tree/master/src/maps>
  - <https://github.com/martinus/map_benchmark/tree/master/data>
  - <https://github.com/martinus/map_benchmark/blob/master/data/all.txt>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/HEAD/data/all.txt>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/electronicarts/EASTL>
  - <https://github.com/electronicarts/EASTL/commits>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/internal/hashtable.h>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/hash_map.h>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/include/EASTL/hash_set.h>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/source/hashtable.cpp>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/benchmark/source/BenchmarkHash.cpp>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/doc/Benchmarks.md>
  - <https://raw.githubusercontent.com/electronicarts/EASTL/HEAD/CMakeLists.txt>
  - <https://github.com/electronicarts/EASTL/issues?q=is%3Aissue+hash_map>
  - <https://github.com/electronicarts/EASTL/issues?q=is%3Aissue+hashtable>
  - <https://github.com/electronicarts/EASTL/issues/521>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/HEAD/data/all.txt>
  - <https://github.com/martinus/map_benchmark/commits/master/data/all.txt>
  - <https://github.com/martinus/map_benchmark/tree/master/src/maps>
  - <https://github.com/martinus/map_benchmark/commits/master/src/maps/eastl_hash_map>
  - <https://github.com/martinus/map_benchmark/tree/2f094ef38c690f0c05b8f01b56cfa68672a9d963/src/maps/eastl_hash_map>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/2f094ef38c690f0c05b8f01b56cfa68672a9d963/src/maps/eastl_hash_map/Map.h>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/2f094ef38c690f0c05b8f01b56cfa68672a9d963/src/maps/eastl_hash_map/Map.cpp>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/2f094ef38c690f0c05b8f01b56cfa68672a9d963/src/maps/std_unordered_map/Map.h>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/2f094ef38c690f0c05b8f01b56cfa68672a9d963/CMakeLists.txt>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/2f094ef38c690f0c05b8f01b56cfa68672a9d963/README.md>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/512810d7bfc568067a653581847b02bb1c683ea9/CMakeLists.txt>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/512810d7bfc568067a653581847b02bb1c683ea9/README.md>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/512810d7bfc568067a653581847b02bb1c683ea9/.gitmodules>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/512810d7bfc568067a653581847b02bb1c683ea9/tools/build.sh>
  - <https://raw.githubusercontent.com/martinus/map_benchmark/512810d7bfc568067a653581847b02bb1c683ea9/tools/bench.rb>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:eastl-hash-map-hash-set`) · [data/wave1/enrich/raw/paper_eastl_hash_map_hash_set.json](../../../data/wave1/enrich/raw/paper_eastl_hash_map_hash_set.json) (enrichment confidence 0.75)

</details>
