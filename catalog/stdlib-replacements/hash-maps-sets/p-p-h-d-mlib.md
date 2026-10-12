# M\*LIB (m-dict hash map, DICT_DEF2)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Hash maps and sets](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Header-only C99/C11 generic container library whose DICT_DEF2 hash map ran 12.6x faster than libstdc++ std::unordered_map in its author's harness.

| | |
|---|---|
| **Beats** | std::unordered_map (GNU libstdc++ STL; also std::vector, std::set, std::string in the same suite) |
| **Claimed result** | EPYC 7763 run on the repo's result branch: UMap U64 M\*LIB dict 923.10 ms vs STL unordered_map 11670.18 ms (12.6x, derived from page data), dict Bulk 737.57 ms (15.8x, derived), open-addressing dict 934.82 ms; UMap Str dict 815.71 ms vs STL umap 2930.79 ms (3.6x, derived); UMap Big dict 1139.77 ms vs STL umap 4185.96 ms (3.7x, derived); Seq(Array) 690.71 ms vs STL vector 1560.62 ms (2.3x, derived); SSet B+tree 813.29 ms vs STL Rbtree 2627.84 ms (3.2x, derived); String Replace 536.51 ms vs STL 1396.06 ms (2.6x, derived). Memory for UMap U64 dict 589.90M vs STL umap 933.78M. README says 'M\*LIB is on par with the STL or even faster' (graphs only, GNU C++ STL v10.2). |
| **Workload** | c-stl-comparison bench: UMap U64 inserts 20,000,000 random unsigned long key/value pairs then performs 20,000,000 random lookups (about half found); the same harness also times a string-key map, a 256-byte-key map, a growing array, a sorted set and string replace. Time is best of 3 runs. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7763 64-Core Processor (lscpu line in BENCH.md; GitHub Actions ubuntu-latest runner per ci.yml; the latest result commit 7012595 was published by the CI run of 2026-08-10); an i5-3210M result is also published in the repo (master branch bench/doc/BENCH.md). |
| **Compiler and flags** | bench/Makefile: CFLAGS=-O2 -march=native -Wall; C side built with `cc -std=c11`, STL side with `c++ -std=c++11` (g++ and libstdc++ on the GitHub Actions ubuntu-latest image per .github/workflows/ci.yml, which runs `cc -v` but shows the output only in the CI log, viewable after sign-in); each bench run with --quiet --best --repeat 3. The GCC version is not in BENCH.md. The 'Compiler used is GCC 16.1' line in the c-stl-comparison README belongs to its code-size comparison, not to the CI benchmark run (the wiki link Benchmark-result showed the README content with no compiler version for the benchmark). The M\*LIB README graphs state GNU C++ STL v10.2. |
| **Adoption** | 1.2k stars |
| **Last commit** | 2026-07-22 |
| **Links** | [repository](https://github.com/P-p-H-d/mlib) · [benchmark](https://github.com/P-p-H-d/c-stl-comparison/blob/result/bench/doc/BENCH.md) |

## Verdict

In the author's c-stl-comparison harness on a GitHub Actions AMD EPYC 7763 runner (gcc/g++ from ubuntu-latest, version not printed on the page; -O2 -march=native; best of 3), inserting 20M unsigned long pairs and doing 20M lookups (half hits) took 923.10 ms with DICT_DEF2 versus 11670.18 ms with libstdc++ std::unordered_map using default std::hash and no reserve (12.6x, derived from page data). Smaller wins hold for string keys (3.6x), 256-byte keys (3.7x) and the B+tree ordered set (3.2x), while std::sort beat M\*LIB's sort (1105.64 vs 1706.60 ms) and std::set beat M\*LIB's red-black tree.

## Use it when

- C (not C++) code bases that want typed hash maps, sets, arrays and trees with one consistent API and no dependency beyond libc.
- Large integer-keyed or string-keyed maps where the per-node allocation of std::unordered_map-style chaining dominates (20M-entry u64 map: 923 ms vs 11670 ms and 590M vs 934M memory in the author's run).
- Batch lookups or inserts of many small keys, where the DICT_OA bulk API with prefetching applies (737.57 ms on the same 20M-key test).
- Embedded or freestanding-adjacent C projects that need a custom allocator (M_MEMORY_ALLOC/REALLOC macros, optional per-call context for arenas) or abort-free error handling through m-try.

## Skip it when

- C++ code: the API is a C macro interface, so boost::unordered_flat_map, absl::flat_hash_map or ankerl::unordered_dense give a std-compatible API with comparable open-addressing speed.
- Hash tables exposed to attacker-chosen keys: the default integer hash is a shift-xor without multiplication and the byte hash's own source comment says collisions are trivial to generate and M_USE_HASH_SEED does not prevent them.
- Code that keeps pointers into the map across inserts or erases: elements move on growth (and on shrink for the OA variant), unlike std::unordered_map's stable node addresses.
- Maps beyond about 3.0 billion entries unless rebuilt with M_USE_DICT_LARGE_INDEX (the default index type is uint32_t).
- Teams unfamiliar with macro-generated code: compile errors surface deep inside preprocessor expansions and the README recommends -ftrack-macro-expansion=0 and a preprocess-then-compile script to debug them.

## How it is fast

DICT_DEF2 is an open-addressing index table of (32-bit slot index, 32-bit hash) pairs probed with triangular (quadratic) steps, pointing into a dense pair array recycled through a freelist; storing the hash in the index means most probes compare one integer before touching the key, and there is no per-entry node allocation as in std::unordered_map. The table is a power of two kept between 0.2 and 0.7 load. DICT_OA_DEF2 stores keys and values inline and marks empty and deleted slots with reserved 'out of range' key values instead of a separate metadata array; its bulk_get/bulk_set API hashes 16 keys ahead and issues software prefetches. Integer keys use a cheap shift-xor hash, (a&gt;&gt;33)^a^(a&lt;&lt;11), selected through C11 _Generic.

## Compared with alternatives

Pick M\*LIB over klib khash when you want a full typed container family with ownership-aware nested objects rather than a single hash macro (khash used slightly less memory, 552.77M vs 589.90M, and ran 1257.84 ms vs 923.10 ms in the same table); in C++ prefer boost::unordered_flat_map or ankerl::unordered_dense for a std-compatible API.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (libc only; optional pthread/C11 threads for the concurrent headers) |
| **Minimum toolchain** | ISO C99 (some features need C11, e.g. the _Generic integer hash selection); MSVC needs /Zc:preprocessor /Zc:__cplusplus |
| **Platforms** | any platform with a C99 compiler; CI-tested with GCC and Clang |
| **Thread safety** | Plain containers such as DICT are not thread-safe; m-buffer, m-snapshot and m-shared-ptr provide documented thread-safe variants. |
| **Drop-in for the baseline** | no |

## Gotchas

- Weak default integer hash: (a&gt;&gt;33)^a^(a&lt;&lt;11) keeps the low key bits and the table uses a power-of-two mask, so strided keys collide; for example keys k&lt;&lt;20 with k below 2^13 all hash to slot 0 in a table of up to 2^20 slots. Supply a mixing HASH in the oplist for patterned keys.
- name_set_at overwrites an existing value (unlike std::unordered_map::insert), name_get returns a borrowed pointer that the next insert can invalidate, and DICT_OA keys need OOR_EQUAL/OOR_SET operators that reserve two key values (0 and 1 in the bench) which must never be inserted.
- Harness quirk behind the numbers: the bench LCG (x\*31421+6927 mod 2^32) yields 32-bit keys and, because every second output is a key, all inserted keys are even and every missed lookup key is odd. M\*LIB's hash keeps bit 0, so hits and misses start on disjoint slot parities while libstdc++'s prime-modulo buckets are unaffected; the direction of the effect on the 12.6x was not measured.
- Build with NDEBUG for release: without it M_ASSERT contract checks run on every operation (the bench defines NDEBUG at the top of bench-mlib.c). Issue #137 (reserve then erase tripped a lower_limit contract assertion) is fixed in the current _update_limit.

## Known shortcomings

- Tier A on BENCH.md (U64 dict 923.10 vs 11670.18 ms, 12.6x vs std::unordered_map; symmetric bench-stl.cpp/bench-mlib.c; EPYC 7763) with CI VM noise and the GCC version only in a sign-in-gated CI log (the record's 'GCC 16.1' came from the code-size section); std::unordered_map run with no reserve while Boost's flat map is already 7.97x; STL sort is 1.54x faster than M\*LIB and the STL Rbtree beats M\*LIB's; the mislabelled STL USet row is std::unordered_set (6189.18 vs 778.50 ms). If tier A requires a printed compiler version this is C.
- Enricher: the bench LCG (x\*31421+6927 mod 2^32) makes every inserted key even and every missed lookup odd, and M\*LIB's int hash (a&gt;&gt;33)^a^(a&lt;&lt;11) keeps bit 0 under a power-of-two mask, so hits and misses start on disjoint slot parities (simulated; effect on the 12.6x not measured). Weak int hash: keys k&lt;&lt;20 all land in slot 0 (verified); the source says HASH_SEED does not stop collisions; the 'dict Bulk' row is DICT_OA with prefetch, not DICT_DEF2; pointers are invalidated on insert; issue #137 reserve assert fixed in _update_limit.

## Caveats and trade-offs

Benchmark harness is the library author's own repo (P-p-H-d/c-stl-comparison), run on a shared GitHub-hosted CI VM (run of 2026-08-10), so timings are noisy and no CPU pinning is stated; the GCC version is printed only in the CI log, not in BENCH.md (the README's 'GCC 16.1' refers to the code-size comparison). STL rows use default std::hash (identity for integers), no reserve() and operator[] inserts, so the 12.6x U64 gap is partly default-std::unordered_map node-allocation cost, and other open-addressing C++ maps would narrow it (Boost unordered flat map is 1464.12 ms on the same page, 7.97x faster than STL; KLIB khash 1257.84 ms). The 'dict Bulk' row uses M\*LIB's bulk API, not the plain per-key loop. M\*LIB is not uniformly faster: in the same BENCH.md STL Sort is 1105.64 ms vs M\*LIB Sort 1706.60 ms (STL 1.54x faster; stable sort 1237.25 vs 1285.71 ms, close) and STL SSet(Rbtree) 2627.84 ms beats M\*LIB SSet(Rbtree) 3092.66 ms (the win is the B+tree). Seq(Deque) 896.94 vs 1799.15 ms, Seq(List) 971.39 vs 1193.67 ms and String Concat 535.55 vs 607.03 ms are smaller wins. The unordered-set test row labelled 'STL USet Longest(dict oa)' is std::unordered_set&lt;int&gt; (label copied from M\*LIB in bench-stl.cpp): M\*LIB dict oa 778.50 ms and dict 932.71 ms vs STL 6189.18 ms (7.9x and 6.6x, derived from page data). Ratios are derived from page data, not stated by the project. The M\*LIB README Performance section shows only PNG graphs against GNU C++ STL v10.2, so the table above is the checkable evidence. The mlib commit pinned in BENCH.md (4acdfe4, 2026-07-22) is the current master head. [retier] BENCH.md on CI VMs (noise; GCC version only in CI log): U64 dict 923.10 vs std::unordered_map 11670.18 ms (12.6x) with no reserve on the STL side; Boost flat map already 7.97x; STL sort 1.54x faster and STL Rbtree faster than M\*LIB's; 'dict Bulk' row is DICT_OA with prefetch. Bench LCG yields only even inserted keys and odd missed lookups, and the int hash keeps bit 0 under a power-of-two mask (hits and misses on disjoint slot parities; effect unmeasured); keys k&lt;&lt;20 all collide in slot 0. Pointers invalidated on insert.

Pure C99/C11 header-only library that generates typed containers with preprocessor macros (oplists); explicit init/clear calls, no copy by assignment, container hands out borrowed pointers; default policy aborts the program on allocation failure (customisable); no C++ templates, exceptions or iterators in the STL sense. Sorted-set variants include a B+tree that is not API-equivalent to std::set.

## Maintenance

Actively maintained (last master commit 2026-07-22, 4,000+ commits, 1.2k stars, no open dict issues in the issue listing), BSD-2-Clause and header-only, so it is easy to vendor; evidence is the author's own harness on a shared CI VM.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** BENCH.md on the c-stl-comparison result branch has STL rows (std::unordered_map, std::vector, std::set, std::string via g++/libstdc++) next to M\*LIB rows, with public harness code (bench/bench-mlib.c, bench/bench-stl.cpp, bench/common.c, bench/Makefile with -O2 -march=native, best of 3), the CPU model (AMD EPYC 7763, lscpu line) and a GCC toolchain (cc/c++ on the ubuntu-latest GitHub Actions image per .github/workflows/ci.yml). Every number in claimed_speedup matches the page; the only gap is that the GCC version is printed only in the CI log (sign-in needed), not on the page.
- **Verifier notes:** All claimed numbers and derived ratios check out against the result-branch BENCH.md, and the harness is symmetric (same rand_get key/value order, same 50% hit ratio, C_N_UMAP_U64 = 20,000,000). Kept at A on public code + Makefile flags + EPYC 7763 + GCC via ubuntu-latest cc; if the orchestrator requires a printed compiler version for A, this falls to C (version only in a sign-in-gated CI log). The record's attribution of 'GCC 16.1' to the benchmark was wrong and is corrected.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-67 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/P-p-H-d/c-stl-comparison/blob/result/bench/doc/BENCH.md>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/doc/BENCH.md>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/Makefile>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/bench-stl.cpp>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/bench-mlib.c>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/common.h>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/README.md>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/master/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/master/bench/doc/BENCH.md>
  - <https://github.com/P-p-H-d/c-stl-comparison/wiki/Benchmark-result>
  - <https://github.com/P-p-H-d/c-stl-comparison/tree/master/.github/workflows>
  - <https://github.com/P-p-H-d/c-stl-comparison/actions>
  - <https://github.com/P-p-H-d/c-stl-comparison/actions/runs/31335447413>
  - <https://github.com/P-p-H-d/c-stl-comparison/commits/result>
  - <https://github.com/P-p-H-d/mlib>
  - <https://github.com/P-p-H-d/mlib/commits/master>
  - <https://raw.githubusercontent.com/P-p-H-d/mlib/master/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/P-p-H-d/mlib/master/README.md>
  - <https://raw.githubusercontent.com/P-p-H-d/mlib/master/m-dict.h>
  - <https://raw.githubusercontent.com/P-p-H-d/mlib/master/m-core.h>
  - <https://raw.githubusercontent.com/P-p-H-d/mlib/master/m-thread.h>
  - <https://raw.githubusercontent.com/P-p-H-d/mlib/master/m-genint.h>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/doc/BENCH.md>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/Makefile>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/bench-stl.cpp>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/bench-mlib.c>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/common.h>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/bench/common.c>
  - <https://raw.githubusercontent.com/P-p-H-d/c-stl-comparison/result/README.md>
  - <https://github.com/P-p-H-d/mlib>
  - <https://github.com/P-p-H-d/mlib/issues?q=is%3Aissue+dict>
  - <https://github.com/P-p-H-d/mlib/issues/137>
  - <https://github.com/P-p-H-d/mlib/issues/143>
  - <https://github.com/P-p-H-d/mlib/commits/master>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/p-p-h-d/mlib`) · [data/wave1/enrich/raw/github_com_p_p_h_d_mlib.json](../../../data/wave1/enrich/raw/github_com_p_p_h_d_mlib.json) (enrichment confidence 0.8)

</details>
