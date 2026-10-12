# tsl::htrie_map (hat-trie)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++11 HAT-trie string map/set using about 3x less memory than std::unordered_map&lt;std::string, T&gt;.

| | |
|---|---|
| **Beats** | std::unordered_map&lt;std::string, int&gt; (memory, and speed on the Askitis set) and cedar::da double-array trie (memory and speed on the Wikipedia set) |
| **Claimed result** | Wikipedia, unsorted: tsl::htrie_map 402.25 MiB (peak 405.22), insert 643.10 ns/key, read 250.87 ns/key; cedar::da 1254.41 MiB, 1102.93 ns, 557.20 ns; std::unordered_map 1246.60 MiB, 590.88 ns, 173.58 ns. Derived from page data: about 3.1x less memory than both, 1.7x faster insert and 2.2x faster read than cedar::da; against std::unordered_map it is about 1.09x slower on insert and 1.45x slower on read. Askitis set: htrie_map 601.79 MiB, 485.45 ns insert, 77.80 ns read; std::unordered_map 2110.19 MiB, 554.02 ns, 105.05 ns; cedar::da 1100.05 MiB, 682.25 ns, 71.98 ns. Derived from page data: about 3.5x less memory than std::unordered_map and 1.8x less than cedar::da, with 1.14x faster insert and 1.35x faster read than std::unordered_map, but a read about 1.08x slower than cedar::da. |
| **Workload** | Insert then look up every key of the English Wikipedia titles dump enwiki-20170320-all-titles-in-ns0 (13,099,148 keys, average length 19.90, int value, shuffled and sorted variants) and the Dr. Askitis distinct_1 set (28,772,169 keys inserted, skew1_1 with 177,999,203 reads); memory is /proc/self/statm growth after insert, speed is ns/key. |
| **Metric** | memory |
| **Hardware** | Intel i5-5200u laptop CPU, 8 GB RAM |
| **Compiler and flags** | GCC 6.3 on Debian Stretch x64 (libstdc++ inferred as the GCC default, not stated); gist Makefile: g++ -std=c++11 -march=native -DNDEBUG -O3 with CityHash64 as hash for the hash-table baselines; README says best of 20 runs |
| **Adoption** | 876 stars |
| **Last commit** | 2025-11-11 |
| **Links** | [repository](https://github.com/Tessil/hat-trie) · [benchmark](https://github.com/Tessil/hat-trie) |

## Verdict

On the author's 2017 benchmark (public gist, GCC 6.3, -O3 -march=native, CityHash64 for every hash structure, libstdc++, Intel i5-5200u laptop), inserting and then reading 13.1M shuffled Wikipedia titles took 402 MiB versus 1247 MiB for std::unordered_map&lt;std::string,int&gt; and 1254 MiB for cedar::da, with reads at 251 ns/key (std::unordered_map 174, cedar::da 557), so it beats the standard map on memory only and other tries on speed; the gist times one pass per run (the README's best-of-20 is not in the code) and its std::unordered_map insert wrapper, map.insert({str, value}), copies each key twice, which inflates that baseline's insert time a little but not its memory or reads. An independent harness (kampersanda/dictionary_bench, g++ 7.3.0 -O3, Xeon E5-2680 v2) reproduced about 3x less memory than std::unordered_map with equal lookup time and slower inserts; no correctness bug was found behind the numbers.

## Use it when

- Millions to hundreds of millions of string keys (titles, URLs, words, paths) where std::unordered_map&lt;std::string, T&gt; memory is the problem: the README shows 402 MiB vs 1247 MiB on 13.1M Wikipedia titles, and an independent run (poplar-trie README) 0.43 vs 1.29 GiB on 14.1M titles and 2.68 vs 6.05 GiB on 39.5M UK URLs.
- You need a dynamic (insert and erase at any time) string dictionary that also answers prefix queries such as autocompletion or longest-prefix routing, which hash maps cannot do.
- Lookup latency close to std::unordered_map is acceptable: the independent run measured identical lookup times (0.27 us/key on Wikipedia titles, 0.51 vs 0.50 us on UK URLs).
- Keys arrive in sorted or clustered order: on the README's sorted Wikipedia run it reads at 68 ns/key versus 174 ns for std::unordered_map.
- You want a vendorable, header-only, MIT-licensed drop-in for a string set or map with on-disk serialization.

## Skip it when

- Raw speed is the goal: open-addressing hash maps beat it on random-order lookups and inserts (README: tsl::hopscotch_map 119.5 ns read and 240.6 ns insert with reserve vs 250.9 and 643.1 ns; independent run: robin_map 0.12 and dense_hash_map 0.14 us lookup vs 0.27).
- Inserts dominate: htrie_map inserts slower than std::unordered_map in both independent datasets (0.60 vs 0.50 us/key on titles, 1.08 vs 0.67 on URLs), because each insert reallocs the bucket buffer and leaves periodically burst.
- Memory must be minimal: succinct or compact tries use far less (poplar compact_bonsai_map 0.24 GiB vs 0.43 GiB on titles; JudySL 2.21 vs 2.68 GiB on URLs; static marisa-trie or xcdat smaller still) at the cost of slower lookups or no updates.
- You need ordered iteration (keys inside a leaf are hashed, so iteration order is not lexicographic) or stable iterators across modifications.
- Keys are not char (wchar_t, char16_t, char32_t are rejected at compile time) or exceed 65,535 bytes without raising the KeySizeT template parameter.

## How it is fast

It implements the HAT-trie of Askitis and Sinha (2007): a burst trie whose leaves are cache-conscious array hash tables (Askitis and Zobel 2005). Each array-hash bucket is one malloc'd contiguous buffer of [2-byte length][key bytes][value index] records, so a lookup hashes the key suffix and scans one short buffer instead of chasing a pointer per entry, and no per-key heap node or 32-byte std::string header is stored; values sit in a separate std::vector indexed by a 16-bit position. When a leaf reaches burst_threshold entries (16384 by default) it bursts into a trie node (a 256-entry child-pointer array) keyed on the first character, so common prefixes are stored once. The default max_load_factor of 8 entries per bucket favors memory; lowering it buys faster reads for more memory.

## Compared with alternatives

Pick it over poplar-trie when lookup speed matters more than the last factor of memory (0.27 vs 0.68-1.02 us/key lookups for 0.43 vs 0.24-0.64 GiB in poplar's own run), and over marisa-trie, xcdat or darts-clone when the dictionary must accept inserts and erases after construction; those static tries are smaller but must be rebuilt to change.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (array-hash is vendored under include/tsl/array-hash; Boost.Test only for the test suite) |
| **Minimum toolchain** | C++11; README says tested with GCC 4.8.4, Clang 3.5.0 and Visual Studio 2015; CMake 3.10 for the exported tsl::hat_trie target |
| **Platforms** | any (portable C++; no SIMD or architecture-specific code) |
| **Thread safety** | README: thread-safety and exception guarantees similar to STL containers (concurrent const reads OK, any writer needs external locking) |
| **Drop-in for the baseline** | partial — API mirrors std::unordered_map, but there is no std::string key object (it.key() rebuilds one), value_type is not std::pair, every insert/emplace/erase invalidates all iterators, no allocator parameter, and iteration order differs |

## Gotchas

- Every modifying operation (insert, emplace, operator[], erase, clear) invalidates all iterators, not just those to the touched element.
- Default hash is std::hash&lt;std::string_view&gt; only when compiled as C++17 or later; under C++11/14 it falls back to a byte-at-a-time FNV-1a, and the README reports CityHash64 gives about 20% faster reads, so pass a better hash functor on older standards (the published benchmark used CityHash64).
- Memory comes from malloc/realloc and new with no allocator template parameter, so custom or shared-memory allocators are not supported (issue #59 asks how to use it with shared memory).
- erase_prefix had crash bugs: issue #57 (iteration after erase_prefix, fixed August 2024) and issue #62 (equal_prefix_range on a fully erased prefix dereferenced a null bucket, fixed by commit ef3213d 'Bugfix on erase_prefix when erasing a full hash_node' in v0.7.1, November 2025, although the issue is still open); use 0.7.1 or newer. burst_threshold values of 65536 or more misbehaved before a clamp was added in August 2024 (issue #54).

## Known shortcomings

- The win is memory, not speed: about 3.1x less memory than std::unordered_map and cedar::da on 13.1M Wikipedia titles (402 MiB vs 1247/1254) and 1.7x/2.2x faster insert/read than cedar, but slower than std::unordered_map there (643 vs 591 ns insert, 251 vs 174 ns read); it beats std::unordered_map only on the Askitis set (1.14x insert, 1.35x read, 3.5x less memory) and on sorted input (2.3x/2.5x). cedar's prefix trie is only 1.18-1.23x bigger. Baselines were hashed with CityHash64; GCC 6.3, i5-5200u (2017-era run). Loose fit for succinct-structures (dynamic string dictionary).
- Enricher: the gist benchmark has no repeat loop, so the README's 'best of 20' is not in the code, and its std::unordered_map insert wrapper copies each key twice (small bias against the baseline). erase_prefix crash (issue #62) fixed in v0.7.1 (commit ef3213d) though the issue stays open; no allocator parameter; C++11 default hash is FNV-1a. kampersanda/dictionary_bench run: 0.69 vs 1.29 GiB and lookup 0.14 vs 0.27 us against std::unordered_map, insert slower (0.73 vs 0.50 us).

## Caveats and trade-offs

The speed win holds against other tries (cedar::da, the C hat-trie, qp trie, crit-bit, Judy), not against hash tables: on the Wikipedia set std::unordered_map was faster (590.88 vs 643.10 ns insert, 173.58 vs 250.87 ns read), and the Askitis win over std::unordered_map is small (1.14x insert, 1.35x read) and reverses on insert if std::unordered_map is given reserve (309.06 vs 485.45 ns insert, while read stays behind at 109.89 vs 77.80 ns). The memory win over hash tables is partly caused by std::string keys costing at least 32 bytes each in those baselines (the README says so). Numbers are from 2017 hardware (laptop i5-5200u) and GCC 6.3. The gist (bench.cpp, Makefile) was read through WebFetch only, because gist.githubusercontent.com is blocked here, so flags and timing code come from the fetch tool's extraction; the README says best of 20 runs while the gist timing code looked like a single pass per invocation. Independent run, same insert and lookup protocol, found in the poplar-trie README (opened) on a Xeon E5-2680 v2 2.80 GHz, g++ 7.3.0 -O3, code at kampersanda/dictionary_bench (CMakeLists.txt opened: Release default -O3 -DNDEBUG -march=native): Wikipedia titles Sep 2018, 14,130,439 keys: tsl::htrie_map 0.43 GiB, insert 0.60 us/key, lookup 0.27 us/key; std::unordered_map 1.29 GiB, 0.50, 0.27; cedar::da reduced trie 1.19 GiB, 0.89, 0.59. UK-domain URLs, 39,459,925 keys: htrie_map 2.68 GiB, 1.08, 0.51; std::unordered_map 6.05 GiB, 0.67, 0.50; cedar::da prefix trie 2.02 GiB, 2.20, 2.28 (the cedar prefix trie uses less memory than htrie_map on this set, 2.02 vs 2.68 GiB, but its lookup is about 4.5x slower, 2.28 vs 0.51 us/key). That run confirms about 3x less memory than std::unordered_map and no speed win over it. Files opened: README.md of Tessil/hat-trie (raw), gist 72e11891fc155f5b2eb53de22cbc4053 (WebFetch), github.com/Tessil/hat-trie and /commits, raw README.md of kampersanda/poplar-trie, raw CMakeLists.txt of kampersanda/dictionary_bench, github.com/kampersanda/dictionary_bench. Verifier additions (2026-10-03): the 3.1x memory figure against cedar::da uses the plain double-array trie; cedar::da's double-array prefix trie is much closer, 496.54 MiB on unsorted Wikipedia (about 1.23x htrie_map's 402.25 MiB) and 712.59 MiB on the Askitis set (about 1.18x of 601.79 MiB), and in the poplar-trie run it is 0.63 GiB against 0.43 GiB on Wikipedia (ratios derived from page data). In the README's sorted Wikipedia run (keys inserted and read in alphabetical order) htrie_map beats std::unordered_map, 255.76 vs 594.85 ns insert and 68.08 vs 173.54 ns read (about 2.3x and 2.5x, derived from page data), but sorted access is a favorable locality case and there cedar::da ORDERED=false prefix trie inserts faster (187.98 ns) and cedar::da double-array trie reads faster (54.72 ns). The hash-table baselines, std::unordered_map included, use CityHash64 rather than std::hash, so the std::unordered_map rows are not the out-of-the-box configuration. The category fit is loose: a HAT-trie is a memory-efficient dynamic trie, not a succinct structure.

Header-only C++11 library (htrie_map and htrie_set, MIT). Any modifying operation (insert, emplace, erase) invalidates all iterators. Supports prefix search (equal_prefix_range, erase_prefix) and longest-prefix match, binary keys, serialization. Memory versus read speed is tunable with max_load_factor: README rows go from 402 MiB with read 251 ns (default) to 710 MiB with read 191 ns (max_load_factor=1) on the unsorted Wikipedia set. It is a dynamic pointer-based string dictionary, not a succinct or static structure, so the listed baselines SDSL and sux do not apply directly. Plain hash tables with reserve (tsl::hopscotch_map 119.49 ns read, tsl::array_map with reserve 128.28 ns) read faster and insert faster than it on the shuffled Wikipedia set and the Askitis set (on the sorted Wikipedia set htrie_map reads faster: 68.08 ns vs 117.20 ns for hopscotch_map with reserve).

## Maintenance

Maintained at a slow pace (v0.7.1, last commit 2025-11-11, erase_prefix bug fixed in that release, one open PR removing the vtable pointer from nodes); MIT, header-only and portable, so it is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** README tables compare tsl::htrie_map with std::unordered_map and cedar::da; the benchmark code is public (gist Tessil/72e11891fc155f5b2eb53de22cbc4053, bench.cpp and Makefile with g++ -std=c++11 -march=native -DNDEBUG -O3) and the README states GCC 6.3, Debian Stretch and an Intel i5-5200u. An independent public harness (kampersanda/dictionary_bench, g++ 7.3.0, Release -O3 -DNDEBUG -march=native, Xeon E5-2680 v2) reproduces the roughly 3x memory win over std::unordered_map.
- **Verifier notes:** Every number in claimed_speedup matches the README rows and the derived ratios check out (3.12x/3.10x memory, 1.71x insert and 2.22x read vs cedar::da; 3.51x/1.83x memory, 1.14x insert, 1.35x read on Askitis). The win is memory, not speed against hash tables; metadata confirmed (MIT, 876 stars, last commit 2025-11-11, active, not a fork).
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Tessil/hat-trie>
  - <https://github.com/Tessil/hat-trie/commits>
  - <https://raw.githubusercontent.com/Tessil/hat-trie/HEAD/README.md>
  - <https://gist.github.com/Tessil/72e11891fc155f5b2eb53de22cbc4053>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/README.md>
  - <https://raw.githubusercontent.com/kampersanda/dictionary_bench/HEAD/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/Tessil/hat-trie>
  - <https://raw.githubusercontent.com/Tessil/hat-trie/HEAD/README.md>
  - <https://raw.githubusercontent.com/Tessil/hat-trie/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Tessil/hat-trie/HEAD/include/tsl/htrie_map.h>
  - <https://raw.githubusercontent.com/Tessil/hat-trie/HEAD/include/tsl/htrie_set.h>
  - <https://raw.githubusercontent.com/Tessil/hat-trie/HEAD/include/tsl/htrie_hash.h>
  - <https://raw.githubusercontent.com/Tessil/hat-trie/HEAD/include/tsl/array-hash/array_hash.h>
  - <https://raw.githubusercontent.com/Tessil/hat-trie/HEAD/include/tsl/array-hash/array_map.h>
  - <https://github.com/Tessil/hat-trie/issues?q=is%3Aissue>
  - <https://github.com/Tessil/hat-trie/issues/62>
  - <https://github.com/Tessil/hat-trie/issues/58>
  - <https://github.com/Tessil/hat-trie/commits>
  - <https://github.com/Tessil/hat-trie/commits/master>
  - <https://github.com/Tessil/hat-trie/commit/ef3213da48f23440dc084d184c3f597a13dc3cce>
  - <https://github.com/Tessil/hat-trie/pulls>
  - <https://gist.github.com/Tessil/72e11891fc155f5b2eb53de22cbc4053>
  - <https://raw.githubusercontent.com/kampersanda/poplar-trie/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/tessil/hat-trie`) · [data/wave9/enrich/raw/github_com_tessil_hat_trie.json](../../../data/wave9/enrich/raw/github_com_tessil_hat_trie.json) (enrichment confidence 0.85)

</details>
