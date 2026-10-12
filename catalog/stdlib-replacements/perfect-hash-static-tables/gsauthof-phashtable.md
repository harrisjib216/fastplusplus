# phashtable (gsauthof)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Perfect hashing and static tables](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSL-1.0` · 🔴 abandoned

> Tiny C/C++ two-level perfect hash index, built at startup, that flattens worst-case lookup latency versus std::unordered_map.

| | |
|---|---|
| **Beats** | std::unordered_map |
| **Claimed result** | README tables, ns, min-max across keys. Atom C3758: ptable_sdbm 43-44 vs umap_sdbm 22-61, and ptable_stl 37-69 vs umap_stl 30-101. Xeon Gold 6246: ptable_sdbm 11-12 vs umap_sdbm 9-34, and ptable_stl 10-11 vs umap_stl 11-36. The worst-case (slowest-key) lookup is about 1.4x lower on Atom and 2.8x lower on Xeon with sdbm. With libstdc++'s std::_Hash_bytes it is about 1.5x (Atom) and 3.3x (Xeon) lower (derived from page data). The best case is not better with sdbm: umap_sdbm's minimum is 22 vs 43 ns on Atom and 9 vs 11 ns on Xeon. The README states that the perfect table 'levels the worst-case access costs up to best-case' while std::unordered_map access times vary by up to about 3x. |
| **Workload** | Google Benchmark micro-benchmark (bench.cc). Tables are built from the 2,776 ISINs in isin-small-sample.lst (SLOTS_TO_TEST=2776, hosted at georg.so/pub). Each benchmark case repeatedly looks up one fixed key, and cases cover all 2,776 keys. The comparison is gms::Phash_Table vs std::unordered_map&lt;const char\*, uint32_t&gt; with custom hash/equality, each with 3 key hashes: sdbm, SipHash, and libstdc++ std::_Hash_bytes ('stl'). run-bench.sh runs it 3 times pinned with taskset. describe.py takes each key's minimum cpu_time over the 3 runs, floors it to ns, and reports the min and max across keys. The 1.4M-ISIN sample is used only by the test_hash_table space-usage example, not by the benchmark. |
| **Metric** | latency |
| **Hardware** | Intel Atom C3758 (Fedora 31, process pinned to an isolated core, frequency management disabled); Intel Xeon Gold 6246 (RHEL 7, isolated core, frequency locked to 4.1GHz) |
| **Compiler and flags** | Atom C3758: g++ -std=gnu++17 -Wall -DSLOTS_TO_TEST=2776 -O3 -march=goldmont-plus, linked with Google Benchmark (build-bench.sh). The g++ version is not stated for this run; code comments reference libstdc++ 9 headers. Xeon Gold 6246: GCC 9 on RHEL 7. build-bench.sh says to adjust -march for other targets, and the Xeon -march value is not stated. |
| **Adoption** | 15 stars |
| **Last commit** | 2020-11-22 |
| **Links** | [repository](https://github.com/gsauthof/phashtable) · [benchmark](https://github.com/gsauthof/phashtable#measurements) |

## Verdict

The author's Google Benchmark code hammers each of 2,776 ISINs in turn against gms::Phash_Table and libstdc++ std::unordered_map&lt;const char\*, uint32_t&gt; (custom hash/equality functors), keeping each key's best of 3 pinned runs. With SDBM the slowest key costs 44 vs 61 ns on an Atom C3758 (g++ -O3 -march=goldmont-plus) and 12 vs 34 ns on a Xeon Gold 6246 (GCC 9, RHEL 7, 4.1 GHz), about 1.4x and 2.8x lower, though unordered_map's fastest keys still win (22 vs 43 and 9 vs 11 ns) and hot-key repetition means cache-miss latency was not measured.

## Use it when

- The key set is fixed or reloaded wholesale (for example a daily instrument/ISIN master file), and rebuilding at startup or re-init is acceptable.
- Latency-sensitive paths where the slowest key matters. On the author's Xeon, the per-key cost stays at 11-12 ns, while std::unordered_map ranges from 9 to 34 ns depending on the key.
- Short, fixed-length string keys with a cheap hash (the benchmark uses 12-byte ISINs with SDBM), especially on low-end cores like Atom, where the hash cost dominates.
- Large runtime key sets where gperf is impractical. The README builds 1.4M ISINs into about 11.4 MB, and reports that gperf did not finish on that set.
- C code, or C++ code that wants a \~370-line BSL-1.0 source drop mapping keys to positions in an existing array.

## Skip it when

- The set changes incrementally: there is no insert or delete, and any change means a full rebuild.
- You care about the best case or the average. unordered_map's fastest keys beat it (22 vs 43 ns on Atom, 9 vs 11 ns on Xeon, both with SDBM), because every lookup pays for two hash calls.
- Memory is tight. The index alone costs about 8.1-8.6 bytes/key on top of your item array, vs about 5.33 for a 75%-full open-addressing index; cmph's CHD needs about 2 bits/key.
- Many lookups are for absent keys, or the key set is untrusted. Lookup always returns some index, and a bad hash or duplicate keys make the build fail (bucket overflow gives -2; no collision-free secondary table gives -3).
- You need a maintained, tested dependency. The repo has 12 commits from Oct-Nov 2020, no tests beyond one example program, and no CI.

## How it is fast

It uses two-level perfect hashing in the style of the classic FKS scheme: a first-level table with n/2 buckets stores an offset, a secondary size (at most 255) and an 8-bit hash parameter per bucket. At build time, a per-bucket search over sizes and parameters makes every secondary table collision-free. Both levels map hashes to slots with Lemire's fast-range multiply-shift instead of modulo, and the default hash is SDBM with a parametrized multiplier (65599 + param). Every lookup runs two hash calls, two multiply-shifts and two table loads with no probing or chaining, even when the bucket's parameter is 0, so that every key costs the same.

## Compared with alternatives

Pick it over frozen (compile-time constexpr keys) when the keys arrive at run time and number in the millions, and over cmph when you want a tiny BSL-1.0 C drop-in that returns your original array index with flat per-key cost and can accept about 8 bytes/key vs CHD's \~2 bits/key. Choose fph-table instead if you want a C++17, std::unordered_map-like container that allows occasional inserts.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the library (libc calloc/free/memset). The example program uses POSIX getline. The benchmark needs Google Benchmark, an external SipHash checkout (not vendored) and libstdc++ internals (std::_Hash_bytes). |
| **Minimum toolchain** | C99 for phash_table.c/.h (compound literals, stdbool) and C++11 for the phash_table.hh wrapper. The published benchmarks were built with g++ -std=gnu++17 (GCC 9). |
| **Platforms** | Portable C with no intrinsics or arch-specific code, so any platform should work. It was only measured on x86-64 Linux (Atom C3758 on Fedora 31, Xeon Gold 6246 on RHEL 7). |
| **Thread safety** | Not documented. By code inspection, lookup only reads the const tables, so concurrent lookups after the build look safe. Build and free need exclusive access. |
| **Drop-in for the baseline** | false — it is a key-to-array-index function with a user-supplied hash callback. It does no key comparison, has no membership result, no mutation and no iteration. You wrap it and keep your own item array. |

## Gotchas

- Lookup never says 'not found'. It returns an index for any key, and absent keys can land on unfilled slots that hold 0. Always compare the key stored at that index, as bench.cc and test_hash_table.c do with memcmp.
- One callback signature does two jobs. Build calls hfn(items, i, param) and lookup calls hfn(key, 0, param), so you normally write two functions that must hash identically. Only the low 8 bits feed the second level, with parameters 0-23 and secondary tables of at most 255 slots.
- C++ wrapper pitfalls. A plain `gms::Phash_Table t;` in automatic storage leaves the pointers uninitialized (the defaulted constructor sits over a C struct), and the destructor then frees them. Move assignment overwrites without freeing the old tables. Use `{}` or construct with data.
- Edge cases are unchecked. With n = 1 the bucket count is n/2 = 0, and the build writes out of bounds. The build computes 2\*n in uint32_t, which caps sets below 2^31 keys. The makefile's default target references pybind11 sources that are not in the repo, so compile phash_table.c yourself.

## Caveats and trade-offs

The project claims latency consistency (worst case and jitter), not a faster average or best case. The 2020-11-22 follow-up post (gms.tf/perfect-hashing.html) says the same and adds boxenplots but no extra numbers. Each benchmark case hammers a single hot key. The numbers therefore reflect per-key probe or collision cost in cache, not random-access or cache-miss latency. Only a 2,776-key table is benchmarked. The std::unordered_map side uses custom const char\* hash and equality functors rather than std::hash&lt;std::string&gt;. For the Atom column, the hardware, compiler and flags are stated and the code is public, so the methodology is Tier A. The Xeon column lacks its -march flag.

Static/rebuild-only table (no incremental insert/delete, meant to be built at startup or re-init); \~8.6 bytes/item overhead vs \~5.33 bytes/item for a 75%-loaded open-addressing hash table; gperf comparison in its own docs notes gperf doesn't terminate in reasonable time on the same 1.4M-key ISIN set

## Maintenance

Abandoned since 2020-11-22 (12 commits, no issues or PRs ever filed) but BSL-1.0 and about 370 lines in three files, so it is easy to vendor and audit; the last known-good compiler is GCC 9.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The README Measurements section runs gms::Phash_Table against std::unordered_map using public Google Benchmark code: bench.cc, build-bench.sh, run-bench.sh and describe.py. For the Atom C3758 column, the compiler (g++) and flags (-std=gnu++17 -O3 -march=goldmont-plus) are stated in build-bench.sh, and the CPU model is stated in the README. The Xeon Gold 6246 column states GCC 9, but its -march value is not given.
- **Verifier notes:** The README numbers match the record exactly. I corrected the workload: the benchmark uses only the 2,776-ISIN sample, and 'min/max' means the min and max across keys of per-key repeated-lookup time, not a per-lookup latency distribution. I added derived worst-case ratios. Metadata (BSL-1.0, 15 stars, last commit 2020-11-22, abandoned, not a fork) checks out via gh. The benchmark dataset URL is still live.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/gsauthof/phashtable>
  - <https://github.com/gsauthof/phashtable#measurements>
  - <https://github.com/gsauthof/phashtable/blob/master/bench.cc>
  - <https://github.com/gsauthof/phashtable/blob/master/build-bench.sh>
  - <https://github.com/gsauthof/phashtable/blob/master/run-bench.sh>
  - <https://github.com/gsauthof/phashtable/blob/master/describe.py>
  - <https://github.com/gsauthof/phashtable/blob/master/makefile>
  - <https://gms.tf/perfect-hashing.html>
  - <https://georg.so/pub/isin-small-sample.lst>
- **Sources the enricher read:**
  - <https://github.com/gsauthof/phashtable>
  - <https://github.com/gsauthof/phashtable#measurements>
  - <https://github.com/gsauthof/phashtable/blob/master/README.adoc>
  - <https://github.com/gsauthof/phashtable/blob/master/phash_table.h>
  - <https://github.com/gsauthof/phashtable/blob/master/phash_table.c>
  - <https://github.com/gsauthof/phashtable/blob/master/phash_table.hh>
  - <https://github.com/gsauthof/phashtable/blob/master/instrument.h>
  - <https://github.com/gsauthof/phashtable/blob/master/instrument.c>
  - <https://github.com/gsauthof/phashtable/blob/master/test_hash_table.c>
  - <https://github.com/gsauthof/phashtable/blob/master/makefile>
  - <https://github.com/gsauthof/phashtable/blob/master/bench.cc>
  - <https://github.com/gsauthof/phashtable/blob/master/build-bench.sh>
  - <https://github.com/gsauthof/phashtable/blob/master/run-bench.sh>
  - <https://github.com/gsauthof/phashtable/blob/master/describe.py>
  - <https://github.com/gsauthof/phashtable/blob/master/notebook.ipynb>
  - <https://github.com/gsauthof/phashtable/blob/master/libphash-lookup.dot>
  - <https://github.com/gsauthof/phashtable/commits/master>
  - <https://github.com/gsauthof/phashtable/issues?q=>
  - <https://github.com/gsauthof/phashtable/network/members>
  - <https://gms.tf/perfect-hashing.html>
  - <https://github.com/renzibei/fph-table>
  - <https://github.com/serge-sans-paille/frozen>
  - <https://github.com/zvelo/cmph>
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `https://github.com/gsauthof/phashtable`) · [data/wave1-phf/enrich/raw/github_com_gsauthof_phashtable.json](../../../data/wave1-phf/enrich/raw/github_com_gsauthof_phashtable.json) (enrichment confidence 0.85)

</details>
