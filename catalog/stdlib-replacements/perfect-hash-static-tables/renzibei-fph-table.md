# fph-table (Flash Perfect Hash)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C++17 dynamic perfect-hash map/set with unordered_map-like API: lookups 1.2-7.6x faster than std::unordered_map, inserts far slower.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | Hit find() at max_load_factor 0.9 on uint64 split-bit-masked keys (hashtable-bench Figures 1-2 and CSVs). AMD 3990X: fph::DynamicFphMap+fph::SimpleSeedHash 2.04 ns vs std::unordered_map+std::hash 10.53 ns at n=32, and 30.98 vs 66.43 ns at n=10^7. That is 2.1-7.6x faster than the best std::unordered_map hash variant across n=32..10^7 (derived from page data). Apple M1 Max: 1.63 vs 2.43 ns (best std::unordered_map variant, robin_hood::hash) at n=32, and 14.79 vs 45.01 ns at n=10^7, i.e. 1.2-7.3x (derived from page data). std::unordered_map+std::hash (libc++) times out on this dataset above \~6000 elements on M1 Max. The fph-table README summarizes this only as a 'clear speed advantage'. |
| **Workload** | find() hits on uint64_t keys where only ceil(log2(n)) fixed split bit positions vary (hashtable-bench dataset 1), uint64_t values, map rehashed at max_load_factor 0.9, sizes 32 to 10^7; the time shown is the average time per operation over a throughput loop, compared across hash-table/hash-function pairs. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen Threadripper 3990X (Zen2); Apple M1 Max (MacBook Pro 16-inch 2021) |
| **Compiler and flags** | gcc 10.2.0 (AMD 3990X, Ubuntu 20.04) and clang 13.1.6 (M1 Max, macOS 12.1); CMAKE_BUILD_TYPE=Release (CMake default -O3 -DNDEBUG) with -std=c++17 -Wall -Wextra, plus -mcpu=native on Apple (hashtable-bench CMakeLists.txt at data commit a6664ff, Jan 2022) |
| **Adoption** | 55 stars |
| **Last commit** | 2026-08-16 |
| **Links** | [repository](https://github.com/renzibei/fph-table) · [benchmark](https://github.com/renzibei/hashtable-bench) |

## Verdict

The author's own hashtable-bench (January 2022 snapshot) measured average ns per hit find() in a throughput loop on uint64 keys where only ceil(log2 n) bits vary, with tables rehashed at max_load_factor 0.9 and n from 32 to 10^7. DynamicFphMap + SimpleSeedHash took 2.04-30.98 ns vs 10.53-66.43 ns for std::unordered_map + std::hash on a Threadripper 3990X (GCC 10.2, libstdc++, Release -O3), 2.1-7.6x faster than the best std::unordered_map pairing; on an M1 Max (Apple clang 13.1.6, libc++, -mcpu=native) it took 1.63-14.79 ns vs 2.43-45.01 ns for the best pairing (robin_hood::hash), 1.2-7.3x, while libc++ std::unordered_map + std::hash timed out on this dataset at larger sizes.

## Use it when

- Read-mostly or static key sets: build once with the range constructor, InsertNoDuplicated() or Build(), then run many find()/contains() calls, e.g. ID-to-record, symbol or routing tables.
- 64-bit integer keys with skewed or structured bit patterns. The default SimpleSeedHash is the identity for integers and the table mixes with random seeds itself. In the author's benchmark on keys where only ceil(log2 n) bits vary, it beat every std::unordered_map + hash pairing 2.1-7.6x on a Threadripper 3990X from n=32 to 10^7.
- Tables of roughly 10^3 to 10^6 entries that fit in L2/L3. The author's 2023 rerun has DynamicFphMap fastest for hit lookups at 8,192 to 3.1M elements on Xeon E-2388G and 8,192 to 1.2M on M1 Max.
- Lookup-bound code that only needs a key-to-unique-index mapping (GetSlotPos, which skips the slot fetch), or whose keys are guaranteed present (GetPointerNoCheck, no compare or branch).
- Large tables with many failed lookups: use fph::MetaFphMap, whose metadata array rejects most misses without reading the slots. The 2023 rerun has it fastest for misses above 6,000 elements on Rocket Lake and above 200,000 on M1 Max.

## Skip it when

- Insert- or erase-heavy workloads. In the same benchmark CSVs on the 3990X, insert-with-reserve at n=10^7 cost about 2,517 ns per element vs 193 ns for std::unordered_map. Erase+insert at n=150,000 cost 2,176 ns vs 59 ns, and at 10^7 it timed out. An insert that breaks perfectness re-places its bucket or rebuilds the whole table.
- Very small tables on x86 and very large hit-lookup tables at default load factor. ska::flat_hash_map + std::hash beat it below about 1,000 elements on the 3990X, and in the 2023 rerun again when data fit in L2 and once it exceeded L3. For large-n misses, absl::flat_hash_map beat DynamicFphMap in the 2022 data.
- Key sets you cannot vet. If the seed search fails, which duplicate keys passed to Build()/InsertNoDuplicated() or poorly distributed hashes can cause, construction throws std::invalid_argument ('timeout when try to build fph map'), or calls std::abort with exceptions disabled. With 64-bit hashes of long keys (strings), the README warns collisions become likely beyond about 10^9 keys.
- Code that needs std::unordered_map's reference stability, node handles (extract/merge), insert_or_assign, or stateful hashers and allocators. None of these are provided.
- Maturity-sensitive deployments. The header logic has not changed since August 2023, the project has 55 stars, and its own CI docs admit an unfixed defect that trips an assert at -O0 and becomes heap corruption under -DNDEBUG, plus a known defect that crashes on x86-64 but passes on arm64. No issue describes either one.

## How it is fast

It is derived from the FCH minimal-perfect-hash algorithm (Fox, Chen, Heath 1992): keys are grouped into about c\*n/(log2 n + 1) buckets (default c = 2.0), and each bucket stores an offset plus one selector bit, found by a randomized seed search at build time, so that every key lands in a distinct power-of-two slot. A lookup is one seed hash, two multiply-and-shift steps with per-table random seeds, one read from the small bucket-parameter array (about 2 bits per key, so it stays in cache), and one slot read followed by a single key compare, with no probe loop. FPH drops FCH's two-step hash selection to remove a branch (paying for it with slower builds), and DynamicFph marks empty slots with a random 'filler' key instead of an occupancy bitmap, avoiding an extra memory load. MetaFph instead adds 1 byte of metadata per slot (7 hash bits plus a position marker), so most misses are rejected without touching the slot array.

## Compared with alternatives

Pick fph-table over the constexpr-oriented siblings (constexpr-phf, ConstexprCore/perfect_hash) and frozen's small fixed tables when keys are only known at run time, number from thousands to millions, or need occasional insert/erase behind an unordered_map-style API. Pick it over cxxmph's mph_map for integer keys: fph reports 2-7x over std::unordered_map, while cxxmph claims 10-50% on large URL-string sets.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only); optional CMake INTERFACE target fph::fph_table via add_subdirectory |
| **Minimum toolchain** | C++17. CI compiles with GCC and Clang at C++17/20/23 on Ubuntu 24.04 (GCC 13, Clang 18) and Apple clang on macOS 15. The README says MSVC compiles but it is not in CI. The published benchmarks used GCC 10.2 and Apple clang 13.1.6. |
| **Platforms** | Portable scalar C++ with no SIMD intrinsics. CI covers Linux x86-64, Linux arm64 and macOS arm64 (LP64). Windows/MSVC compiles per the README but is untested. |
| **Thread safety** | Not documented. The const lookups (find/contains/count/GetSlotPos) only read table state. Any insert can relocate elements or rebuild the whole table, so writers need exclusive access. |
| **Drop-in for the baseline** | partial — member names and semantics mostly match std::unordered_map, but the hash parameter must be a (key, seed) SeedHash (or use the noseed branch). Custom key types need a RandomKeyGenerator for the Dynamic variants, keys must be CopyConstructible, references are invalidated on rehash or rebuild, and there are no node handles and no insert_or_assign. |

## Gotchas

- The const operator[] on DynamicFphMap is noexcept and skips the key check (it calls GetPointerNoCheck). For an absent key it silently returns another element's value or reads an unconstructed slot. Use find() or at() unless the key is known to be present.
- SeedHash and KeyEqual are static constexpr members, so they must be stateless and constexpr default-constructible, and a hasher instance passed to the constructor is ignored. Slot and bucket storage use default-constructed rebound allocators, so stateful allocators are not honored.
- Empty slots in the Dynamic variants hold copies of a randomly generated filler key. Every unused slot therefore holds a constructed key (a random short string for std::string keys), and custom key types must supply a RandomKeyGenerator. MetaFph\* avoids this with its metadata byte.
- Pointers and references can be invalidated by any insert (bucket re-placement or full rebuild), not only by rehash. begin() moves to the most recently inserted or erased element, so iteration order shifts after every modification. The default max_load_factor is 0.6 (settable up to 0.98) over power-of-two slot counts, and the default BucketParamType=uint32_t caps capacity at 2^31 slots.

## Caveats and trade-offs

hashtable-bench is written by the fph-table author, so it is not independent (the tier does not depend on that). The README plots are a Jan-2022 snapshot. Current master added -march=native on Linux (2025) and moved the seeded fph maps to src/backup-seed-maps, so an exact reproduction needs the 2022 commit. The win depends on size and key distribution. On the 3990X, ska::flat_hash_map+std::hash beats fph below \~1000 elements, and absl::flat_hash_map wins large-n miss lookups. On M1 Max, std::unordered_map+std::hash (libc++) degenerates on this masked-bit dataset, so the fair baseline is the robin_hood::hash/absl::Hash variant. fph inserts are very slow (table rebuilds), so it only suits lookup-dominated or static key sets.

Dynamic perfect hash table rebuilds the whole table whenever an insert breaks perfectness, so insert/erase are slow and are 'the slowest in the benchmark' per the Ankerl suite; needs a seed-aware hash functor (not plain std::hash) unless using the no-seed branch; keys must be CopyConstructible, values MoveConstructible; MetaFphMap trades hit-lookup speed for faster miss-lookup

## Maintenance

Header logic frozen since August 2023, but the author added an Apache-2.0 license and an extensive CI suite (compile matrix, ctest, ASan/UBSan, asm/callgrind lookup gates) in August 2026, so it is lightly maintained, and at two self-contained headers of about 4k lines each it is easy to vendor and pin.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Upgraded from C. hashtable-bench states the compilers (gcc 10.2.0 on the Threadripper 3990X under Ubuntu 20.04; clang 13.1.6 on the M1 Max under macOS 12.1) and the CPU models. Its README gives the build as CMAKE_BUILD_TYPE=Release, and CMakeLists.txt at the Jan-2022 data commit a6664ff adds -Wall -Wextra, plus -mcpu=native on Apple. The benchmark code is public (src/benchmark.cpp, src/maps/std_unordered_map/Map.h, src/seed-maps/dy_fph_map at 2bafe80), and it runs std::unordered_map directly against fph::DynamicFphMap, with per-size CSVs in results/data-3990x and results/m1-max.
- **Verifier notes:** Metadata matches: Apache-2.0, 55 stars, not a fork, last commit 2026-08-16. The record's claim that no compiler is stated was wrong, because the hashtable-bench README names both compilers. The record's metric 'latency' is really throughput (average ns per operation); hashtable-bench measures latency separately and only on x86. hashtable-bench has no license, which does not affect fph-table's Apache-2.0. The linked blog (renzibei.com) shows newer Xeon E-2388G/M1 Max results but names no compilers.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/renzibei/fph-table>
  - <https://github.com/renzibei/fph-table/blob/master/show/3990x/figs/%3Cmask_split_bits_uint64_t,uint64_t%3E,avg_hit_find_with_rehash.png>
  - <https://github.com/renzibei/fph-table/blob/master/show/m1-max/figs/%3Cmask_split_bits_uint64_t,uint64_t%3E,avg_hit_find_with_rehash.png>
  - <https://github.com/renzibei/hashtable-bench>
  - <https://github.com/renzibei/hashtable-bench/blob/master/CMakeLists.txt>
  - <https://github.com/renzibei/hashtable-bench/blob/a6664ff5c2/CMakeLists.txt>
  - <https://github.com/renzibei/hashtable-bench/blob/2bafe803dd/src/benchmark.cpp>
  - <https://github.com/renzibei/hashtable-bench/blob/2bafe803dd/src/maps/std_unordered_map/Map.h>
  - <https://github.com/renzibei/hashtable-bench/tree/master/results/data-3990x/csv>
  - <https://github.com/renzibei/hashtable-bench/tree/master/results/m1-max/csv>
  - <https://renzibei.com/en/hashtable-bench/>
- **Sources the enricher read:**
  - <https://github.com/renzibei/fph-table>
  - <https://github.com/renzibei/fph-table/blob/master/include/fph/dynamic_fph_table.h>
  - <https://github.com/renzibei/fph-table/blob/master/include/fph/meta_fph_table.h>
  - <https://github.com/renzibei/fph-table/blob/master/CMakeLists.txt>
  - <https://github.com/renzibei/fph-table/blob/master/docs/ci.md>
  - <https://github.com/renzibei/fph-table/blob/master/.github/workflows/ci.yml>
  - <https://github.com/renzibei/fph-table/blob/master/CONTRIBUTING.md>
  - <https://github.com/renzibei/fph-table/blob/master/tests/CMakeLists.txt>
  - <https://github.com/renzibei/fph-table/blob/master/tests/test_fph_table.cpp>
  - <https://github.com/renzibei/fph-table/blob/master/tests/main.cpp>
  - <https://github.com/renzibei/fph-table/blob/master/tests/ci/compile-matrix.sh>
  - <https://github.com/renzibei/fph-table/blob/master/tests/ci/compile_probe.cpp>
  - <https://github.com/renzibei/fph-table/blob/master/tests/ci/counter_probe.cpp>
  - <https://github.com/renzibei/fph-table/blob/master/tests/ci/lib.sh>
  - <https://github.com/renzibei/fph-table/issues?q=is%3Aissue>
  - <https://github.com/renzibei/fph-table/issues/1>
  - <https://github.com/renzibei/fph-table/issues/5>
  - <https://github.com/renzibei/fph-table/issues/6>
  - <https://github.com/renzibei/fph-table/issues/7>
  - <https://github.com/renzibei/fph-table/pulls?q=is%3Apr>
  - <https://github.com/renzibei/fph-table/pull/8>
  - <https://github.com/renzibei/fph-table/commits/master>
  - <https://github.com/renzibei/fph-table/commit/b550b93>
  - <https://github.com/renzibei/fph-table/commit/611c08f>
  - <https://github.com/renzibei/fph-table/branches>
  - <https://github.com/renzibei/fph-table/commits/noseed>
  - <https://github.com/renzibei/fph-table/compare/master...ci/github-actions>
  - <https://github.com/renzibei/fph-table/commits/ci/github-actions>
  - <https://github.com/renzibei/hashtable-bench>
  - <https://github.com/renzibei/hashtable-bench/tree/master/results>
  - <https://github.com/renzibei/hashtable-bench/blob/master/results/data-3990x/csv/fph::DynamicFphMap__fph::SimpleSeedHash__mask_split_bits_uint64_t__uint64_t.csv>
  - <https://github.com/renzibei/hashtable-bench/blob/master/results/data-3990x/csv/std::unordered_map__std::hash__mask_split_bits_uint64_t__uint64_t.csv>
  - <https://github.com/renzibei/hashtable-bench/blob/master/results/data-3990x/csv/std::unordered_map__robin_hood::hash__mask_split_bits_uint64_t__uint64_t.csv>
  - <https://github.com/renzibei/hashtable-bench/blob/master/results/data-3990x/csv/std::unordered_map__absl::Hash__mask_split_bits_uint64_t__uint64_t.csv>
  - <https://github.com/renzibei/hashtable-bench/blob/master/results/m1-max/csv/fph::DynamicFphMap__fph::SimpleSeedHash__mask_split_bits_uint64_t__uint64_t.csv>
  - <https://github.com/renzibei/hashtable-bench/blob/master/results/m1-max/csv/std::unordered_map__std::hash__mask_split_bits_uint64_t__uint64_t.csv>
  - <https://github.com/renzibei/hashtable-bench/blob/master/results/m1-max/csv/std::unordered_map__robin_hood::hash__mask_split_bits_uint64_t__uint64_t.csv>
  - <https://github.com/renzibei/hashtable-bench/blob/master/results/m1-max/csv/std::unordered_map__absl::Hash__mask_split_bits_uint64_t__uint64_t.csv>
  - <https://renzibei.com/en/hashtable-bench/>
  - <https://renzibei.com/en/int-lookup-throughput/>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/renzibei/fph-table`) · [data/wave1-phf/enrich/raw/github_com_renzibei_fph_table.json](../../../data/wave1-phf/enrich/raw/github_com_renzibei_fph_table.json) (enrichment confidence 0.82)

</details>
