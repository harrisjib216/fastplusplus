# uthash

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-1-Clause` · 🟢 active

> Header-only intrusive C hash table (macros); in one third-party benchmark it iterates and erases faster than std::unordered_map but loses most lookups.

| | |
|---|---|
| **Beats** | std::unordered_map (libstdc++ from GCC 13.2.0) |
| **Claimed result** | Article text: "uthash's iteration is about twice as fast as std::unordered_map's iteration (albeit still extremely slow)". Heatmap for 0-20M keys (total time relative to the fastest table, std::unordered_map vs uthash): iterate 87.83 vs 37.39 (32-bit keys), 24.67 vs 10.53 (64-bit key/448-bit value), 79.94 vs 30.64 (string keys), i.e. 2.3-2.6x (derived from page data); erase existing 11.26 vs 7.79, 9.84 vs 6.10, 3.21 vs 2.41, i.e. 1.3-1.6x (derived from page data); erase nonexisting 5.25 vs 3.72, 5.83 vs 3.91, 2.43 vs 1.93, i.e. 1.3-1.5x (derived from page data); lookup nonexisting 3.67 vs 3.22, 3.96 vs 3.24, 2.32 vs 1.83, i.e. 1.1-1.3x (derived from page data); insert 64-bit/448-bit 4.91 vs 4.11 and string 2.87 vs 2.61 (1.1-1.2x, derived from page data); string-key lookup existing 1.59 vs 1.38 and replace 1.52 vs 1.46 (1.04-1.15x, derived from page data). uthash is NOT faster for 32-bit-key insert (6.75 vs 6.39), 32-bit and 64-bit/448-bit replace (3.80 vs 2.71, 2.90 vs 2.34), or 32-bit and 64-bit/448-bit lookup of existing keys (2.58 vs 2.28, 2.45 vs 2.41). |
| **Workload** | Third-party C/C++ hash-table benchmark (uthash v2.3.0 vs std::unordered_map among 15 tables): tables grown to 20,000,000 keys at max load factor 0.875 with a shared MurmurHash3-finalizer/FNV-1a hash, measuring insert, erase and replace of existing keys, erase and lookup of existing and nonexisting keys, and iteration, for three key/value shapes (32-bit/32-bit, 64-bit/448-bit, 16-char string/64-bit). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 5800H, frequency locked at 90% |
| **Compiler and flags** | GCC 13.2.0 via MinGW-w64, C++20, -O3 -DNDEBUG (README build line: g++ -I. -std=c++20 -static -O3 -DNDEBUG -Wall -Wpedantic main.cpp) |
| **Adoption** | 4.8k stars |
| **Last commit** | 2026-06-25 |
| **Links** | [repository](https://github.com/troydhanson/uthash) · [benchmark](https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/docs/index.md) |

## Verdict

Jackson Allan's c_cpp_hash_tables_benchmark compared uthash v2.3.0 with libstdc++ std::unordered_map, both using the same MurmurHash3-finalizer or FNV-1a hash and std set to max_load_factor 0.875. It was built with GCC 13.2.0 (MinGW-w64, -O3 -DNDEBUG, C++20) and run on a Ryzen 7 5800H locked at 90% frequency under Windows. Over 0-20M keys uthash iterated 2.3-2.6x faster and erased existing and nonexisting keys 1.1-1.6x faster, but lost 32-bit inserts, replacements and existing-key lookups. In the 0-200,000-key run it won only iteration.

## Use it when

- Plain C code that needs a hash index over existing structs without templates or code generation: one header, macros only.
- Elements must keep fixed addresses, carry their own storage, or sit in several hashes at once (one UT_hash_handle per table).
- Insertion-order iteration over large node-based tables, the one operation where it beat std::unordered_map in every run (about 2.3-2.6x in the 0-20M-key heatmap, 1.45-1.73x summed over the 0-200,000-key run, derived from the published CSV).
- Cold-cache tables with millions of keys and frequent erasures or failed lookups, where it was 1.1-1.6x faster than std::unordered_map in the 0-20M-key run.

## Skip it when

- Performance is the goal: the benchmark's author concludes uthash 'should be avoided due to all-around poor performance' and the open-addressing tables (Verstable, CC cc_map, boost::unordered_flat_map, absl, ankerl) are far faster; uthash's own user guide says faster and more memory-efficient tables now exist.
- Small integer keys with lookup or replace-heavy traffic: 32-bit-key inserts, replacements and existing-key lookups were slower than std::unordered_map in the 0-20M run, and in the 0-200,000-key run uthash lost every insert, lookup, replace and erase case except 64-bit/448-bit erase (std/uthash 0.53-0.91x summed adjusted averages, derived from CSV).
- Memory-constrained programs: each element carries a 56-byte UT_hash_handle on x86-64 plus its own malloc block, on top of the bucket array.
- Keys that are structs with padding, floats or pointers to data, unless you supply HASH_FUNCTION and HASH_KEYCMP: the defaults hash (Jenkins) and memcmp raw bytes.
- Concurrent writers: no internal synchronisation.

## How it is fast

It is a node-based separate-chaining table like std::unordered_map, so it is not fast in general; its wins over libstdc++ come from layout details. Every handle is on a doubly linked insertion-order list (hh.prev/hh.next), so iteration and unlinking need no predecessor search, and each bucket points straight at its chain head with the 32-bit hash cached in each handle (compared before the key). libstdc++'s table, by contrast, is one singly linked list whose buckets store the node before the bucket's first node, and walking a bucket checks the following node's hash to detect the bucket's end (hashtable.h layout comment), which adds dependent loads on misses and erasures. Growth is bucket doubling triggered when one chain reaches 10 items (times a per-bucket expand_mult), not a load-factor limit.

## Compared with alternatives

Pick uthash over Verstable, abseil, Boost.Unordered or ankerl::unordered_dense only when you need an intrusive, node-stable table in plain C with insertion-ordered iteration and accept slower lookups and more memory; for speed in C use Verstable, and in C++ use boost::unordered_flat_map or ankerl::unordered_dense.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (libc malloc/free, memcmp, memset, strlen) |
| **Minimum toolchain** | Any C or C++ compiler; needs &lt;stdint.h&gt; unless HASH_NO_STDINT is defined; uses __typeof or decltype when available, with a NO_DECLTYPE fallback |
| **Platforms** | any; user guide lists Linux, Windows (Visual Studio 2008 and 2010), Solaris, OpenBSD, FreeBSD and Android as tested |
| **Thread safety** | Caller must lock: concurrent readers are allowed (since 1.5), but add, delete and sort need an exclusive (write) lock; the guide suggests a pthread rwlock |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: the shim cannot apply the benchmark's MAX_LOAD_FACTOR of 0.875, because uthash doubles buckets only when one chain reaches 10 x (expand_mult+1) items. The article nevertheless says every table except GCC's std::unordered_map grows at 0.875. A simulation of uthash.h's expansion rule with random 32-bit hashes (scratch script, not measured in the benchmark) gives about 0.9-3.4 items per bucket up to 20M keys, against std's 0.44-0.875. So uthash ran with fewer buckets and longer chains, which hurts its lookups rather than inflating its wins.
- Harness: the iteration benchmark walks 1,000 elements (main.cpp breaks at k == 1000 in both the 2024-05-24 and 2024-05-29 revisions around the 2024-05-28 runs), while the article, graphs and CSV call it 'iterate over 5,000 keys'. Ratios are unaffected. The iterated table is insert-only, so uthash's insertion-order list probably matches allocation order, while libstdc++'s list is grouped by bucket; the iteration win may shrink after heavy erase and reinsert churn. The erase benchmark also removes a contiguous run of insertion order, a drawback the author acknowledges.
- The benchmark bypasses uthash's defaults: the shim passes a precomputed MurmurHash3-finalizer or FNV-1a hash through HASH_FIND_BYHASHVALUE and HASH_ADD_BYHASHVALUE, truncated to unsigned int, and redefines HASH_KEYCMP. Default uthash, which hashes with Jenkins over the key bytes and compares with memcmp, was not measured.
- The head pointer must start as NULL, and add and delete operations can change it. On malloc failure uthash calls exit(-1) unless you define HASH_NONFATAL_OOM or override uthash_fatal. HASH_FUNCTION and HASH_KEYCMP are macros, so each one applies to every table that uses it in a translation unit. In C++, hh.next needs an explicit cast.

## Known shortcomings

- Tier A (JacksonAllan heatmap, main.cpp plus shims/, GCC 13.2.0 MinGW -O3 -DNDEBUG, Ryzen 7 5800H) but the win is mixed: iterate 2.3-2.6x and erase 1.3-1.6x faster than std::unordered_map, slower on the 0-200k run (32-bit lookup 35,300 vs 15,700 ns at N=200,000) and on int insert and replace; 64-bit and 448-bit lookup-existing rows a slight loss (2.45 vs 2.41).
- Enricher: the shim cannot apply the suite's MAX_LOAD_FACTOR 0.875 because uthash doubles only when one chain reaches 10x(expand_mult+1), so uthash ran at 0.9-3.4 items per bucket vs 0.44-0.875 for std (simulation; handicaps uthash lookups, does not inflate wins); the iteration loop breaks at k == 1000 (revisions 4ff5b8e, f1b93d7) while the article, graphs and CSV say 5,000 keys (ratios unaffected). The iteration win likely comes from the insert-only table's insertion-order list matching allocation order while libstdc++'s list is grouped by bucket; the erase benchmark removes a contiguous run of insertion order (author admits); the shim bypasses the default Jenkins hash and memcmp (BYHASHVALUE macros, HASH_KEYCMP redefined), so default uthash was never measured. In the 0-200,000 CSV uthash wins only iteration (1.45-1.73x summed) and loses the rest at 0.53-0.91x, except 64-bit/448-bit erase-existing at 1.04x (derived from CSV).

## Caveats and trade-offs

The numbers are a third-party comparison; uthash's own repo carries no benchmarks and never claims to beat std::unordered_map. The article's author concludes uthash 'should be avoided due to all-around poor performance' (it is far slower than open-addressing tables) and says its comments about std::unordered_map's poor performance also apply to uthash; the win over std::unordered_map is mixed. Heatmap figures are totals over the 0-20M-key run normalized to the fastest table, and the ratios here are derived from them. In the 0-200,000-key run (docs/result_2024-05-28T04_06_21.csv) uthash is slower than std::unordered_map for most insert, lookup and replace cases (for example 32-bit lookup of existing keys at N=200,000: 35,300 vs 15,700 in the CSV's time units, 2.25x slower, derived from CSV data), while at N=200,000 its iteration is faster only for the 64-bit/448-bit and string keys (derived from CSV data). Benchmarked version is uthash v2.3.0; the repo is now at v2.4.0. Run on Windows with MinGW-w64, so libstdc++ behaviour (including std::unordered_map growth policy) is specific to that build. The published article lives on github.io, which was blocked here; the numbers were read from the article source docs/index.md in the benchmark repo. [retier] JacksonAllan suite: shim bypasses uthash's default Jenkins hash and memcmp (BYHASHVALUE macros), and uthash ignores the suite's 0.875 load factor (grows only when a chain reaches 10x(expand_mult+1), so 0.9-3.4 items per bucket vs 0.44-0.875 for std); iteration loop runs 1000 keys although the article says 5,000. Wins: iterate 2.3-2.6x (insertion-order list matches allocation order in an insert-only table) and erase 1.3-1.6x (contiguous insertion-order run). Loses int insert, replace and the whole 0-200k run (0.53-0.91x) except erase-existing 1.04x (derived from CSV). BSD-1-Clause.

Macro-based intrusive hash table: every item embeds a 56-byte UT_hash_handle (per the benchmark article), node-based separate chaining like std::unordered_map, rudimentary API with the user writing much of the scaffolding. By default keys are hashed and compared byte-by-byte, which is unsafe for structs with padding bytes. Pure C, single header, BSD-1-Clause.

## Maintenance

Maintained (v2.4.0 released 2026-06-25, maintainers favour keeping it unchanged). It is a BSD-1-Clause single header that is trivial to vendor, but it is a convenience choice, not a performance one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party benchmark with public code (JacksonAllan/c_cpp_hash_tables_benchmark main.cpp plus shims/ and blueprints/), compiler GCC 13.2.0 via MinGW-w64, flags -O3 -DNDEBUG (README: g++ -I. -std=c++20 -static -O3 -DNDEBUG -Wall -Wpedantic main.cpp) and CPU AMD Ryzen 7 5800H all stated; heatmap values for std and uthash match the record exactly.
- **Verifier notes:** All heatmap figures in the record were re-extracted from the SVG in docs/index.md and match; added the omitted string-key lookup/replace rows and the 64-bit/448-bit lookup-existing loss. Shortcomings: win over std::unordered_map is mixed and confined to the 0-20M run (the 0-200,000 CSV shows uthash slower for nearly all insert, lookup and replace cases, e.g. 32-bit lookup existing at N=200,000 35,300 vs 15,700), the article author calls uthash all-around poor and far behind open-addressing tables, benchmarked v2.3.0 (repo now v2.4.0), Windows/MinGW libstdc++ only, and std::unordered_map was run with max load factor 0.875 rather than its default 1.0. License BSD-1-Clause (single retention clause, OSI-approved), 4.8k stars, last commit 2026-06-25 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-55 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/docs/index.md>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/docs/result_2024-05-28T04_06_21.csv>
  - <https://github.com/JacksonAllan/c_cpp_hash_tables_benchmark>
  - <https://github.com/troydhanson/uthash>
  - <https://github.com/troydhanson/uthash/commits>
  - <https://raw.githubusercontent.com/troydhanson/uthash/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/troydhanson/uthash>
  - <https://github.com/troydhanson/uthash/issues?q=is%3Aissue+performance+OR+slow+OR+bug+OR+overflow>
  - <https://github.com/troydhanson/uthash/issues/119>
  - <https://raw.githubusercontent.com/troydhanson/uthash/HEAD/README.md>
  - <https://raw.githubusercontent.com/troydhanson/uthash/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/troydhanson/uthash/HEAD/src/uthash.h>
  - <https://raw.githubusercontent.com/troydhanson/uthash/HEAD/doc/userguide.txt>
  - <https://raw.githubusercontent.com/troydhanson/uthash/HEAD/doc/ChangeLog.txt>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/config.h>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/shims/uthash/shim.h>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/shims/std_unordered_map/shim.h>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/blueprints/uint32_uint32_murmur/blueprint.h>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/blueprints/uint64_struct448_murmur/blueprint.h>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/blueprints/cstring_uint64_fnv1a/blueprint.h>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/docs/index.md>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/HEAD/docs/result_2024-05-28T04_06_21.csv>
  - <https://github.com/JacksonAllan/c_cpp_hash_tables_benchmark/commits/main/main.cpp>
  - <https://github.com/JacksonAllan/c_cpp_hash_tables_benchmark/commit/f1b93d7>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/f1b93d7/main.cpp>
  - <https://raw.githubusercontent.com/JacksonAllan/c_cpp_hash_tables_benchmark/4ff5b8e/main.cpp>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-13.2.0/libstdc++-v3/include/bits/hashtable.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/troydhanson/uthash`) · [data/wave1/enrich/raw/github_com_troydhanson_uthash.json](../../../data/wave1/enrich/raw/github_com_troydhanson_uthash.json) (enrichment confidence 0.8)

</details>
