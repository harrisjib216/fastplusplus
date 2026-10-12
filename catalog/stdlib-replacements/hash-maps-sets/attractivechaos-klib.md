# klib khash (khash.h)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Single-header C macro hash table (open addressing, 2-bit flags); about 4x less CPU and 3x less memory than std::unordered_map on integer counting.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | udb2 180929 server logs (khash/run-test.log vs c++11/run-test.log): at N=50M khash 5.460 s CPU and 172.457 MB versus std::unordered_map 22.220 s and 493.762 MB, about 4.1x less CPU time and 2.9x less memory (derived from log data); at N=10M 0.652 s versus 2.972 s (4.6x, derived). The run-test-1 pair is two different variants: khash/test-1.c stores a {key,count} struct in a khash set (no separate value array), 4.724 s / 136.742 MB, while c++11/test-1.cpp uses emplace, 22.872 s / 493.363 MB at N=50M (4.8x, derived). The later 191228-server.tgz run shows the same picture: khash 4.061 s / 171.488 MB versus std::unordered_map 17.211 s / 519.270 MB at N=50M (about 4.2x CPU, 3.0x memory, derived from log data). |
| **Workload** | udb2 micro-benchmark: count occurrences of N 32-bit integer keys (about 25% distinct) in a uint32-to-uint32 hash map, with identity hash for both tables, six rounds with N = 10M, 18M, 26M, 34M, 42M, 50M, so rehashing growth is included; reports CPU time and peak-RSS delta. |
| **Metric** | throughput |
| **Hardware** | Linux server, Xeon E5-2683 v3 2.0GHz, 35MB cache, 640GB memory (udb2 README) |
| **Compiler and flags** | gcc 5.4.0 per udb2 README for the server run; khash/Makefile builds with '\$(CC) -O2 -Wall' and c++11/Makefile with '\$(CXX) -O3 -Wall -std=c++11' (verified in the 2018 Makefile at commit 539d6d0, unchanged in substance since), so the baseline got the higher optimization level. libstdc++ is inferred from gcc on Linux, not stated. |
| **Adoption** | 4.7k stars |
| **Last commit** | 2025-12-22 |
| **Links** | [repository](https://github.com/attractivechaos/klib) · [benchmark](https://raw.githubusercontent.com/attractivechaos/udb2/master/__logs/180929-server.tgz) |

## Verdict

In attractivechaos/udb2 (counting occurrences of 32-bit keys, about 25% distinct, six growing rounds), the 2018 server run (Xeon E5-2683 v3, gcc 5.4.0, khash at -O2, std::unordered_map from libstdc++ at -O3) took 5.46 s CPU and 172 MB peak RSS for khash versus 22.22 s and 494 MB for std::unordered_map at N=50M (about 4.1x CPU, 2.9x memory, derived from log data); the 2019 server run gives 4.06 s / 171 MB versus 17.21 s / 519 MB, and both runs print identical unique-key counts and checksums for every implementation.

## Use it when

- C code (or C++ code that must stay template-free) that maps 32- or 64-bit integers to small POD values and counts or deduplicates millions of keys, the udb2 workload where it used about 4.1x less CPU and 2.9x less memory than std::unordered_map at 12.3M distinct keys.
- Memory-bound jobs: with 4-byte keys and values it held 12.3M keys in about 172 MB peak RSS versus 494 MB for std::unordered_map, and less than absl, robin_hood, ska and tsl::robin_map (216-577 MB) in the same udb2 runs.
- Codebases that already vendor klib or htslib-style code, where khash is the house hash table and adding a C++ dependency is not an option.
- Embedding with a custom allocator: kmalloc, kcalloc, krealloc and kfree are overridable macros.

## Skip it when

- C++ projects that can take a dependency: absl::flat_hash_map, boost::unordered_flat_map, ankerl::unordered_dense or tsl::robin_map give a typed, RAII, iterator-based API and matched or beat khash's time on the udb2 server runs (2019: absl 3.49 s, tsl::robin_map 2.78 s, khash 4.06 s at N=50M), at higher memory.
- New C code: the author's own khashl.h (same repo; Fibonacci hashing, linear probing, 1 bit per bucket, no tombstones) was faster and smaller on the same 2019 server run (3.59 s / 132 MB versus 4.06 s / 171 MB); khash.h's algorithm has been frozen since 2013 and only typo fixes landed after 2015.
- Structured integer keys (multiples of a power of two, aligned pointers cast to integers) with the default identity hash: only the low bits pick the bucket, so such keys pile into a fraction of the table; use kh_int_hash_func2 (Wang hash) or your own mixer.
- Delete-heavy or shrinking workloads: deletes leave tombstones and there is no automatic shrinking (TODO in kh_put; issue #121 open since 2019).
- Tables that could exceed about 1.65 billion entries (2^31 buckets times 0.77): bucket indices are 32-bit khint_t and growth past 2^31 buckets is not possible (see gotchas).

## How it is fast

Open addressing over power-of-two tables with triangular quadratic probing (step i\*(i+1)/2, version 0.2.8), keys and values in two separate flat arrays and occupancy kept in a separate 2-bit-per-bucket flag array, so there is no per-entry allocation or node pointer as in a chained std::unordered_map. Growth reallocs the key and value arrays and rehashes in place with a cuckoo-like kick-out loop, so it needs only about 0.25 bytes per bucket of extra working space instead of a second full table. Maximum load factor is 0.77; the default integer hash is the identity, which is cheap but relies on keys already being well distributed.

## Compared with alternatives

Pick khash over uthash or Collections-C when you need a C hash table for small POD keys and care about memory and speed (flat arrays, no per-entry nodes); pick absl::flat_hash_map, boost::unordered_flat_map or ankerl::unordered_dense instead in C++, and prefer the same author's khashl.h for new C code.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (stdlib.h, string.h, limits.h) |
| **Minimum toolchain** | C99 for inline (or C89 with kh_inline defined by the user; MSVC uses __inline); also compiles as C++ |
| **Platforms** | any; portable C, no SIMD or intrinsics |
| **Thread safety** | not documented; no internal locking. kh_get takes a const table pointer, so concurrent readers with no writer look safe by inspection; any kh_put can rehash and move every entry. |
| **Drop-in for the baseline** | no |

## Gotchas

- Growth stops at 2^31 buckets (found by reading khash.h, not tested): kh_resize(h, n_buckets + 1) runs kroundup32 on 2^31+1, which wraps to 0, so the resize becomes a no-op that still returns 0 (success); the table keeps filling past the 0.77 load bound and, once every bucket is occupied, kh_put for an absent key returns the starting bucket, which holds a different key, with \*ret = 0 ('already present') instead of an error.
- kh_put does not initialise the value for a new key: check \*ret (1 new, 2 reused tombstone, 0 present, -1 allocation failure) and set kh_val yourself; returned indices are invalidated by any later kh_put because rehash moves entries in place.
- String tables (KHASH_MAP_INIT_STR) store only the const char\* pointer with the X31 hash; the caller owns the strings and must free them while iterating before kh_destroy (issue #136 shows the double-free pattern this invites).
- The udb2 numbers come from keys that common.c pre-scrambles with the Wang hash before the identity hash is applied, so the benchmark never exercises the identity hash's weakness on structured keys; memory is peak RSS (monotonic across rounds), time is getrusage user+sys CPU from one run per N including about 0.06-0.13 s of key generation.

## Known shortcomings

- Tier A on the udb2 180929-server logs (5.460 s vs 22.220 s at N=50M, identical checksums, gcc 5.4.0, Xeon E5-2683 v3) with the baseline at -O3 and khash at -O2; the run-test-1 pair compares the khash set-of-struct variant with std emplace (not like for like); the 191228 run gives about 4.2x (4.061 vs 17.211 s). 2018 compiler, int keys only, single run; udb2 has no licence.
- Enricher: udb2 logs check out (same checksums for every implementation; baseline at -O3 vs khash at -O2), but keys are pre-scrambled with the Wang hash before khash's identity hash so its weakness on structured keys is never tested, there is one run per N, and timing includes key generation. Code bug (read, not tested): growth stops at 2^31 buckets because kroundup32 wraps to 0 and resize returns success without growing, so the table fills past 0.77 load and, once full, kh_put returns another key's slot with \*ret=0. khash.h unchanged since 2013 (2018 typo fix only); the same author's khashl.h was faster and smaller on the 2019 run (3.586 s/132 MB vs 4.061 s/171 MB); no auto-shrink (issue #121).

## Caveats and trade-offs

The benchmark lives in a separate repo (attractivechaos/udb2, same author, 35 stars, no license file) and the numbers are inside the linked tgz (udb2-lynx-log/khash/run-test.log and c++11/run-test.log); the README itself shows only plots. The 180929 run is from 2018 with gcc 5.4.0 and an old libstdc++ (unordered_map's node-based design has not changed since). udb2 vendors khash.h 0.2.8, identical to klib's current khash.h apart from comments. Only 32-bit integer keys and values (keys pre-scrambled with hash32, then an identity hash in both tables), counting workload; says nothing about string keys or lookup-only loads; a deletion variant exists for khash in 191228-server.tgz but has no std::unordered_map counterpart. The timed loop also includes key generation (about 0.12 s over the 50M sequence, small). CPU time is getrusage user+sys, single run per N. The run-test-1 pair compares a khash set-of-struct variant against an emplace-based std::unordered_map, not like for like. The README's 'results vary with machines' warning applies: the Google Cloud n1-standard-1 run uses different hardware. udb2 also lists many other maps (absl, ska, tsl, robin_hood, unordered_dense, verstable, khashl and others), most of which beat khash on the 2023 runs; khash is far from the fastest option, only clearly faster than std::unordered_map. [retier] udb2 180929/191228 runs: int keys pre-scrambled with the Wang hash (khash identity hash never stressed), one run per N, timing includes key generation, baseline -O3 vs khash -O2, 2018 gcc 5.4.0; run-test-1 pair not like for like. Growth stops at 2^31 buckets (kroundup32 wraps to 0, resize reports success), after which a full table makes kh_put return another key's slot (code reading). khash.h unchanged since 2013; the author's khashl.h was faster and smaller in 2019 (3.586 s/132 MB vs 4.061 s/171 MB); no auto-shrink (#121). udb2 has no licence; klib MIT.

Single-header C macro library (KHASH_INIT instantiates types and functions per key/value type), so no templates, RAII, or iterator stability; open addressing with 32-bit bucket indices (khint_t), values stored in a separate array and relocated on resize; deletion leaves tombstones. Pointers or references into the table are invalidated by insertion. Keys and values must be trivially copyable plain types; custom types need hand-written hash and equality macros. The klib README also advertises kbtree.h (B-tree ordered map), ksort.h, and kvec.h, but no numeric comparison against std::map, std::sort, or std::vector was reachable here (their blog posts are on blocked wordpress).

## Maintenance

The klib repo is active (last commit 2025-12-22, 4.7k stars) but khash.h itself is effectively frozen (algorithm 0.2.8 from 2013, last edit a 2018 typo fix) with the author's development moved to khashl.h; MIT-licensed, one header, widely vendored (git carries a copy), easy to copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public in attractivechaos/udb2 (common.c, khash/test.c, c++11/test.cpp, per-directory Makefiles); the README states the server CPU (Xeon E5-2683 v3) and compiler (gcc 5.4.0), and the 2018 Makefiles (khash -O2, c++11 -O3 -std=c++11, unchanged since commit 539d6d0) give the flags. The 180929-server.tgz logs contain exactly the claimed rows for khash and std::unordered_map, with identical unique-key counts and checksums across implementations.
- **Verifier notes:** Numbers verified line by line in 180929-server.tgz; correctness check passes (same unique-key count and checksum for khash and std::unordered_map). Corrected the second-variant description (khash run-test-1 is a set-of-struct variant) and added the 2019 server run, which agrees (about 4.2x). Baseline built at -O3 versus khash at -O2, so the comparison is not stacked in khash's favour.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-59 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/__logs/180929-server.tgz>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/__logs/191228-server.tgz>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/__logs/231213-M1.tgz>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/common.c>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/khash/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/539d6d0/khash/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/khash/test.c>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/khash/test-1.c>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/khash/khash.h>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/c++11/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/c++11/test.cpp>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/c++11/test-1.cpp>
  - <https://github.com/attractivechaos/udb2>
  - <https://github.com/attractivechaos/udb2/commits/master>
  - <https://github.com/attractivechaos/udb2/commits/master/khash/Makefile>
  - <https://github.com/attractivechaos/udb2/commits/master/c++11/Makefile>
  - <https://github.com/attractivechaos/udb2/tree/master/__logs>
  - <https://github.com/attractivechaos/klib>
  - <https://github.com/attractivechaos/klib/commits/master>
  - <https://raw.githubusercontent.com/attractivechaos/klib/master/khash.h>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/attractivechaos/klib/master/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/klib/master/khash.h>
  - <https://raw.githubusercontent.com/attractivechaos/klib/master/khashl.h>
  - <https://github.com/attractivechaos/klib>
  - <https://github.com/attractivechaos/klib/commits/master/khash.h>
  - <https://github.com/attractivechaos/klib/issues?q=is%3Aissue+khash>
  - <https://github.com/attractivechaos/klib/issues/185>
  - <https://github.com/attractivechaos/klib/issues/136>
  - <https://github.com/attractivechaos/klib/issues/121>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/common.c>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/khash/test.c>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/khash/test-1.c>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/khash/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/c++11/test.cpp>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/c++11/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/__logs/180929-server.tgz>
  - <https://raw.githubusercontent.com/attractivechaos/udb2/master/__logs/191228-server.tgz>
  - https://code.googlesource.com/git/+/refs/heads/seen/khashl.h (WebSearch snippet only)
  - https://git.kpda.ru/ports/ncdu/commit/2d7619009177e0c8abcedeb4c00f7d9ed222a8d5 (WebSearch snippet only: ncdu moved from khash.h to khashl.h for reduced memory)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/attractivechaos/klib`) · [data/wave1/enrich/raw/github_com_attractivechaos_klib.json](../../../data/wave1/enrich/raw/github_com_attractivechaos_klib.json) (enrichment confidence 0.8)

</details>
