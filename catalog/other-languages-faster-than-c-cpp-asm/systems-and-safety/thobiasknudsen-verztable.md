# verztable

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig port of Verstable's chained open-addressing hash table; edges Abseil/Boost/Ankerl on small and string-keyed tables only.

| | |
|---|---|
| **Beats** | absl::flat_hash_map/flat_hash_set, boost::unordered_flat_map/unordered_flat_set and ankerl::unordered_dense::map/set (src/cpp_hashtables_wrapper.cpp); integer keys use each library's default hash, string keys use std::string_view with a shared wyhash. The 'std' column is Zig's std.AutoHashMap/StringHashMap, not std::unordered_map. |
| **Claimed result** | README: 'outperforms Google's Abseil, Boost, and Ankerl on mixed workloads'. BENCHMARKS.md, 100-element u32 set: Reserved Ins. 5 ns vs Abseil 13 / Boost 14 / Ankerl 9 (but the C++ tables are never reserved, see caveats); Delete 4 vs 13 / 6 / 6; Lookup Miss 1 vs 5 / 2 / 3; Tombstone 5 vs 16 / 6 / 8; losses in the same table: Rand. Lookup 3 vs Boost 2, Write-Heavy 12 vs Ankerl 8. Across all 432 per-configuration rows verztable beats the best of the three C++ tables in 156, ties 37 and loses 239; geometric-mean time ratio C++/verztable is about 1.03 vs Boost, 1.33 vs Abseil and 1.46 vs Ankerl (derived from page data). At 100K integer keys it loses nearly every row to Abseil and Boost (u32 set: 0 wins of 16; geomean 0.61x of Boost's speed); its clearest wins are on string keys (8-10 of 16 rows per configuration) and on 100-element tables. The page's 27-configuration average table shows verztable ahead on 10 of 16 operations and behind on random/sequential insert, lookup miss, iteration and write-heavy. |
| **Workload** | u32, u64 and random-length (8-64 char) string keys with void, 4-byte and 64-byte values, at 100, 3K and 100K elements (1M appears only in the memory table); 16 operation mixes (random and sequential insert, reserved insert, update, random lookup, high load, lookup miss, tombstone, delete, iteration, churn, mixed, read-heavy, write-heavy, update-heavy, zipfian); ns per operation, 15 iterations; C++ tables called from Zig through per-operation extern "C" wrappers. |
| **Metric** | latency |
| **Compiler and flags** | Zig 0.15.2+ with -O ReleaseFast for verztable and the Zig std maps; the C++ wrapper and Abseil sources are compiled by Zig's bundled clang with -std=c++17 -O3 -DNDEBUG -fno-exceptions -fno-rtti (build.zig); native target by default; no LTO configured, so C++ calls are not inlined into the Zig benchmark loop. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: hash-fragment filtering skips non-matches without touching bucket data; fast path for strings of 8 bytes or fewer; stores full 64-bit hashes for string keys to skip memcmp. |
| **Adoption** | 15 stars, 0 forks |
| **Last commit** | 2025-12-29 |
| **Links** | [repository](https://github.com/ThobiasKnudsen/verztable) · [benchmark](https://raw.githubusercontent.com/ThobiasKnudsen/verztable/main/BENCHMARKS.md) |

## Verdict

The author's harness (Zig 0.15.2 ReleaseFast; C++ tables compiled by Zig's clang with -std=c++17 -O3 -DNDEBUG and called through non-inlined extern "C" wrappers; malloc for all; CPU and OS not stated) reports mean ns/op over 15 iterations for 16 operation mixes on u32, u64 and string keys at 100, 3K and 100K elements. Verztable beats the best C++ table in 156 of 432 rows and loses 239; by geometric mean it is about 3% faster than Boost and about 1.33x and 1.46x faster than Abseil and Ankerl (derived from page data), with wins concentrated on string keys and 100-element tables and losses on 100K integer tables.

## Use it when

- Zig code that uses std.AutoHashMap or std.StringHashMap for lookup-heavy work: in the author's u32 set tables it beats Zig std on lookups and misses at every size (100K lookup 9 ns vs 13 ns, miss 9 vs 18), though std inserts faster at 100K (25 vs 31 ns).
- String-keyed maps and sets (random 8-64 byte keys), where the stored 64-bit hash avoids repeated memcmp; this is where its wins over the C++ tables cluster.
- Small tables (around 100 elements) with delete/re-insert churn, where tombstone-free deletion keeps chains short.
- Small tables queried mostly with absent keys, where hash-fragment filtering rejects misses cheaply.

## Skip it when

- Large integer-keyed tables: at 100K u32 keys it loses almost every row to Abseil and Boost even though they pay an FFI call per operation (random insert 31 ns vs 13 and 15 ns, lookup 9 vs 5 and 6 ns).
- C or C++ projects: use Boost unordered_flat_map or Abseil flat_hash_map, or Verstable itself in C; verztable is Zig only (0.15.2+).
- Signed or wider-than-64-bit integer keys with the default hash: negative i32/i64 keys hit an illegal @intCast (see gotchas); supply HashMapWithFns.
- Code that keeps pointers into the table across inserts or removes, or string keys whose bytes do not outlive the map (keys are stored as borrowed slices).
- Production use that needs a track record: single author, v0.1.0, no issues filed yet, tests do not cover signed keys.

## How it is fast

It follows Verstable's design: open addressing with linear probing, but keys that share a home bucket form a chain linked through 16-bit per-bucket metadata (4-bit hash fragment, 1-bit in-home flag, 11-bit displacement to the next chain member). A key always owns its home bucket (a squatter from another chain is evicted), so a lookup walks only its own chain and the fragment rejects about 15/16 of non-matching entries without touching the bucket array; deletion relinks the chain instead of leaving tombstones. For []const u8 keys each bucket stores the full 64-bit hash to skip memcmp, strings of 8 bytes or fewer are hashed as a packed integer, and iteration scans metadata 8 entries at a time with @Vector.

## Compared with alternatives

No hash-table sibling is catalogued in this category (the siblings are sorts, compressors, allocators and compilers); against the C++ tables it was measured with, pick verztable only inside Zig for small or string-keyed tables, and keep Boost unordered_flat_map or Abseil flat_hash_map for large integer-keyed tables in C++.

## Integration

| | |
|---|---|
| **Form** | Zig package (module added through build.zig.zon; tag v0.1.0) |
| **Dependencies** | none for the library; the C++ submodules (abseil-cpp, boost unordered and friends, unordered_dense) are used only by the benchmark |
| **Minimum toolchain** | Zig 0.15.2+ (minimum_zig_version in build.zig.zon) |
| **Platforms** | any Zig target (pure Zig; @Vector SIMD is portable) |
| **Thread safety** | not documented; an unsynchronized struct, so concurrent writers need external locking |
| **Drop-in for the baseline** | partial — near drop-in for Zig std.AutoHashMap/StringHashMap (same method names, allocator at init), not for the C++ Abseil/Boost/Ankerl tables |

## Gotchas

- Harness flaws beyond the verifier's two (C++ tables never reserved in 'Reserved Ins.'; every C++ op is a non-inlined extern "C" call): per-op times are integer-divided (total ns / ops), so 100-element rows move in whole-ns steps and a 1 vs 2 ns 'win' can be a tie; 'High Load' only looks up 95 keys in a 95-key table, repeating Random Lookup at normal load; 'Seq. Insert' is sequential only for u64 (u32 and string rows insert the random keys in order); and the C++ iteration row is a counting loop inside one wrapper call, which over Ankerl's dense value vector clang can reduce to a pointer difference, so Ankerl's 0 ns says nothing about FFI overhead.
- The memory table is not like for like: verztable's figure includes its 2-byte metadata per bucket, but the C++ figures are bucket_count x sizeof(value_type) only, omitting Abseil's control bytes, Boost's group metadata and Ankerl's separate bucket index array (Ankerl keeps values in a dense vector sized by element count). The README's '\~25% more memory' is unreliable in both directions; its own table shows 50% (12.0 KB vs 8.0 KB for 1K u32 keys).
- Correctness: AutoHashFn hashes integers as hashInteger(@as(u64, @intCast(key))), so HashMap(i32, V) or HashMap(i64, V) with negative keys (or u128 keys above 2^64) is illegal behaviour, a panic in Debug/ReleaseSafe and undefined in ReleaseFast; the test suite has no signed-key test.
- Pointer stability: inserting a key whose home bucket holds another chain's key evicts that key to a new bucket, and remove moves the chain's last key into the hole, so pointers from getPtr/getOrPut/getEntry are invalidated by any insert or remove, not only by growth.

## Known shortcomings

- The "Reserved Ins." row compares a reserved verztable against C++ tables that never reserve; every C++ operation pays a non-inlined FFI call; loses 239 of 432 rows to the best C++ table, about 1.03x geomean against Boost (derived from page data); no CPU model.
- Integer division quantizes the 100-element rows to whole nanoseconds; 'High Load' is a plain lookup at normal load; Ankerl's 0 ns iteration is a loop clang can reduce to a pointer difference, not FFI evidence; the memory table omits the C++ control bytes and Ankerl's bucket array, so 'about 25% more memory' is unreliable (its own table shows 50%). Correctness bug: the auto hash does @intCast(key) to u64, so negative i32/i64 keys panic (Debug/ReleaseSafe) or are UB (ReleaseFast), with no signed-key test; pointers are invalidated by any insert or remove (eviction, swap-on-erase).

## Caveats and trade-offs

Own harness, no CPU model or OS stated. Harness asymmetries: (1) 'Reserved Ins.' calls ensureTotalCapacity for verztable and Zig std, but benchCpp's setup for .insert_reserved does nothing and the wrapper has no reserve function, so the C++ columns in that row are plain un-reserved inserts (verztable 'wins' 22 of 27 such rows); (2) every C++ operation goes through a non-inlined extern "C" call (insert also memcpys the value into a temporary), which adds roughly a call's cost to 1-5 ns operations, the size range where verztable wins most; the README's argument that Ankerl's 0 ns iteration shows minimal FFI overhead does not hold because iteration is a single wrapper call that counts inside C++. The string fast path (keys up to 8 bytes packed into a u64) and stored 64-bit hashes are design features the competitors do not use. Uses about 25% more memory than the competitors by the README's own trade-off note (string sets 3.3 MB vs 1.9-2.0 MB at 100K). Verstable (C) is the algorithmic inspiration, not a benchmark target. 15 stars, single author. [retier] Integer division quantises the 100-element rows to whole nanoseconds; 'High Load' is a plain lookup at normal load; Ankerl's 0 ns iteration is a loop clang can reduce to a pointer difference; the memory table omits the C++ control bytes and Ankerl's bucket array (its own table shows 50% more memory, not 25%). The auto hash does @intCast(key) to u64, so negative i32/i64 keys panic (Debug/ReleaseSafe) or are UB (ReleaseFast); pointers are invalidated by any insert or remove.

Uses about 25% more memory than the C++ tables (12.0 KB vs 8.0 KB for 1K u32 keys, 12.0 MB vs 8.0 MB at 1M); Zig only.

## Maintenance

Single-author port released as v0.1.0 (tag 2025-12-28, last commit 2025-12-29, 46 commits, 15 stars, no issues filed); MIT and one source file of about 1,450 lines, so easy to vendor, but young, Zig 0.15-specific and unsafe for signed keys with the default hash.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party harness is public (src/benchmark.zig, src/cpp_hashtables_wrapper.cpp, C++ flags in build.zig) and BENCHMARKS.md has the quoted numbers, but no CPU model or machine is stated, so not A; tier stays C, and the claim is downgraded because the headline rows are partly harness artifacts and verztable loses most integer-key rows at 3K and 100K elements.
- **Verifier notes:** Real table with a public harness, but the claim is overstated: the cited Reserved Ins. win compares reserved verztable against un-reserved C++ tables, all C++ operations pay a non-inlined FFI call, and verztable loses 239 of 432 rows to the best C++ table (beats Boost by only about 3% geomean, loses most integer rows at 3K/100K). Record shortcomings: harness asymmetry (no reserve for C++, per-op FFI), no CPU model, not faster than Boost on integer keys at scale, higher memory use.
- **Fields the verifier corrected:** `baseline`, `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-30 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/README.md>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/main/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/build.zig>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/src/cpp_hashtables_wrapper.cpp>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/src/benchmark.zig>
  - <https://github.com/ThobiasKnudsen/verztable>
  - <https://github.com/ThobiasKnudsen/verztable/commits>
- **Sources the enricher read:**
  - <https://github.com/ThobiasKnudsen/verztable>
  - <https://github.com/ThobiasKnudsen/verztable/tags>
  - <https://github.com/ThobiasKnudsen/verztable/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/README.md>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/build.zig>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/src/root.zig>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/src/benchmark.zig>
  - <https://raw.githubusercontent.com/ThobiasKnudsen/verztable/HEAD/src/cpp_hashtables_wrapper.cpp>
  - <https://raw.githubusercontent.com/martinus/unordered_dense/HEAD/include/ankerl/unordered_dense.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/thobiasknudsen/verztable`) · [data/wave14/enrich/raw/github_com_thobiasknudsen_verztable.json](../../../data/wave14/enrich/raw/github_com_thobiasknudsen_verztable.json) (enrichment confidence 0.7)

</details>
