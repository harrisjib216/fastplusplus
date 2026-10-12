# Cuckoo Filter (efficient/cuckoofilter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Reference C++ cuckoo filter from the CoNEXT'14 authors: a Bloom-filter replacement that supports deletes and does faster positive lookups.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | Lookup throughput (Fig. 5, read from the plot): CF is \~12 MOPS at 0% and 100% positive queries and dips to \~10.5 MOPS at 50%. The standard Bloom filter falls from \~8.3 MOPS (0% positive) to \~4.9 MOPS (100% positive), so the CF advantage runs from \~1.45x to \~2.4x (derived from page data, plot-read). Construction is 5.00M keys/sec (CF) vs 3.91M keys/sec (BF) with all filters at 192MB, at 12.60 vs 13.00 bits/item and the same 0.19% FPR (Table 3; \~1.28x, derived from page data). On space, semi-sorted cuckoo filters need fewer bits/item than space-optimized Bloom filters when the target FPR is below 3% (crossover 7.2 bits/item, Fig. 4 and Sec. 6). |
| **Workload** | 192MB filters holding \~120-128M pre-generated 64-bit random-integer keys; lookup throughput measured while varying the fraction of positive queries, and insert throughput measured across load factor, on a two-socket Intel Xeon testbed. |
| **Metric** | throughput |
| **Hardware** | 2x Intel Xeon L5640 @ 2.27GHz, 12MB L3 cache, 32GB DRAM |
| **Adoption** | 1013 stars |
| **Last commit** | 2021-11-12 |
| **Links** | [repository](https://github.com/efficient/cuckoofilter) · [benchmark](http://www.cs.cmu.edu/~binfan/papers/conext14_cuckoofilter.pdf) |

## Verdict

In the CoNEXT'14 paper (2x Xeon L5640, compiler and flags not stated, random 64-bit keys hashed with CityHash, 192MB filters), the cuckoo filter at 12.60 bits/item builds at 5.00M keys/s vs 3.91M for a standard Bloom filter at 13.00 bits/item and the same 0.19% FPR. Plot-read lookup throughput is about 1.45x-2.4x the standard Bloom filter's, and the gap grows with the share of positive queries. The Bloom baseline code is not in the repo. An independent run in the Xor Filters paper (i7-6700, GCC 8.1.0 -O3 -march=native, 10M keys, 25% found) measured a size-flexible Cuckoo 12 at 31 ns vs Bloom 12 at 40 ns, and the original power-of-two version at 30 ns but 20.1 bits/key.

## Use it when

- You need deletions (a counting-Bloom replacement) over 64-bit integer or pre-hashed keys, and you can guarantee that you only delete keys that were actually inserted.
- Lookup-heavy workloads where many queries hit present keys: in the paper's 192MB test, CF stays at about 10.5-12 MOPS while a standard Bloom filter falls to about 4.9 MOPS at 100% positive queries.
- Target FPRs of roughly 0.01-3%, served by 12- or 16-bit fingerprints. Below 3% FPR the semi-sorted variant needs fewer bits per item than a space-optimized Bloom filter (paper Fig. 4, 7.2-bit crossover).
- Capacity known up front and close to 4 x 2^k keys (at most \~0.96 of that), so the power-of-two table is not half empty.
- You want the canonical implementation to reproduce the CoNEXT'14 numbers or to serve as a baseline in your own filter benchmarks.

## Skip it when

- Arbitrary or memory-tight capacities. The bucket count rounds up to a power of two, so memory can reach \~2x the ideal. The repo's own bulk-insert-and-query output shows 46-138% wasted space, and the Xor Filters paper measured the original Cuckoo 12 at 20.1 bits/key vs 12.8 for a size-flexible rewrite at 10M keys.
- Growing or unbounded sets. The filter cannot resize: after 500 relocations the next Add fails for good. Issue #9 reports failures before the capacity the constructor promises, and the Xor paper lowered max load from 0.96 to 0.94 to stop construction failures.
- Raw lookup speed with no deletes. The repo's own AVX2 SIMD blocked Bloom filter runs \~2x faster than Cuckoo12 in bulk-insert-and-query (about 74 vs 37 M finds/s in the file's sample output). The paper's blocked Bloom filter ties CF at 0% positive queries and builds faster (7.64 vs 5.00 M keys/s), though at 2x the FPR of a standard Bloom filter.
- Semi-sorted mode where speed matters. In the repo's figure-5 benchmark, ss-CF lookups run at 9.4-10 MOPS vs 24.8 for plain CF on an i7-4790. At 10M keys the Xor paper measured Cuckoo semiSort 13 at 57 ns vs Bloom 12 at 40 ns.
- Concurrent writers, std::string keys, persistence, big-endian targets or MSVC. None is supported: there is no locking, the default hash accepts only uint64 (issue #39), serialization is missing (issue #28 still open), the bit tricks assume little-endian, and the code uses unsigned __int128.

## How it is fast

The filter is a cuckoo hash table of 4-slot buckets holding short fingerprints, filled with partial-key cuckoo hashing: an item's alternate bucket is its current bucket XOR a hash of its fingerprint, so entries can be moved without the original key. Every lookup reads exactly two buckets, which the paper counts as at most two cache misses. Both 64-bit loads are issued before comparing, and SWAR has-value bit tricks check all four fingerprints of a bucket in one word, so lookup cost stays flat as the share of positive queries grows, whereas a Bloom filter must probe all k bits for each hit. The optional PackedTable ('semi-sorting') sorts each bucket's low 4-bit nibbles and permutation-encodes them, saving 1 bit per fingerprint at a large speed cost.

## Compared with alternatives

Pick it over Xor Filter (immutable, per its paper) or the same repo's SIMD blocked Bloom filter when you need deletes, or a lower FPR per bit than a blocked Bloom filter. Among dynamic cuckoo-style siblings, Morton Filter (1.3-2.5x faster lookups than this reference in its paper) and Vacuum Filter (about 25% less space at similar throughput) are catalogued improvements. This one wins mainly as the simple, widely cited reference.

## Integration

| | |
|---|---|
| **Form** | source-drop (src/\*.h plus src/hashutil.cc; `make install` also builds a static libcuckoofilter.a) |
| **Dependencies** | OpenSSL headers: hashutil.h includes &lt;openssl/evp.h&gt;, so even including cuckoofilter.h needs them. Link with -lssl -lcrypto if you compile hashutil.cc. Nothing else. |
| **Minimum toolchain** | C++11 (both Makefiles use -std=c++11). GCC or Clang, because the code relies on unsigned __int128 and __attribute__((packed)). No MSVC support is documented. |
| **Platforms** | Little-endian 64-bit only: code comments say the bucket reads work only on little-endian, and they use unaligned 64-bit loads. The benchmarks target x86-64 (-march=core-avx2), and simd-block.h needs AVX2, but the cuckoo filter itself uses no intrinsics. Other architectures are not documented. |
| **Thread safety** | Not documented. There is no internal locking. Contain() is const and read-only, so concurrent readers with no writer appear safe. Add/Delete mutate the table and victim stash and call rand() on the kick path, so they need external synchronization. |
| **Drop-in for the baseline** | partial — it fills the Bloom filter's Add/Contain role and adds Delete, but capacity is fixed (Add can return NotEnoughSpace), results come back as a Status enum, you pick a fingerprint width rather than an FPR, and the default hash takes only uint64 keys |

## Gotchas

- Only some fingerprint widths work, and nothing checks at compile time. SingleTable reads tags only for 2, 4, 8, 12, 16 and 32 bits; other widths compile but give false negatives (issue #6; the static_assert PR #35 was never merged). PackedTable at 5, 7 and 9 bits also fails (issue #34), and the Xor Filters authors could get only the 13-bit semi-sorted variant to work correctly.
- When an insert fails after 500 relocations, Add() still returns Ok and parks the displaced fingerprint in a one-entry victim stash. From then on every Add() returns NotEnoughSpace until a Delete frees a slot.
- Deleting a key that was never inserted can remove another key's matching fingerprint, which creates a false negative. Inserting the same key 2b+1 = 9 times fails.
- The class owns a raw table pointer but defines no copy constructor or copy assignment, so copying a CuckooFilter double-frees. The root Makefile also defaults to -g -ggdb, not the -O3 -DNDEBUG used by the benchmarks.

## Known shortcomings

- Figure 5 is overstated in the original record: cuckoo \~12/\~10.5 MOPS vs Bloom \~8.3 falling to \~4.9, so at most about 2.4x (not 2.75x). The Bloom baseline code is not in the repo.
- Table size rounds up to a power of two (up to \~2x memory; the repo's own bench wastes 46-138%; the Xor paper measures 20.1 bits/key). Only fingerprint widths 2/4/8/12/16/32 work; others compile but give false negatives (#6, #34). Cannot resize: after 500 kicks a victim stash is used and then Add fails permanently, sometimes below advertised capacity (#9).
- The same repo's SIMD blocked Bloom filter has \~2x faster lookups; semi-sorted mode is \~2.5x slower than the plain filter. Default hash takes uint64 keys only; no serialization, no locking, and no copy constructor (a copy double-frees). Needs OpenSSL headers; little-endian, GCC/Clang only; abandoned.

## Caveats and trade-offs

Peer-reviewed ACM CoNEXT'14 paper (Fan, Andersen, Kaminsky, Mitzenmacher). It states the hardware (2x Xeon L5640) but not the compiler or flags. The repo's benchmarks/conext-figure5.cc and conext-table3.cc only benchmark CuckooFilter, so the Bloom-filter baseline code is not public. The current benchmarks/Makefile flags (-O3 -march=core-avx2) postdate the paper and could not have run on the Westmere testbed. The CF only ties the paper's blocked Bloom filter at 0% positive queries (\~12 MOPS each); its win is over the standard Bloom filter and grows with the positive-query fraction. Per Sec. 6, the &lt;3% FPR space advantage is stated for the semi-sorting variant. The README has no numbers. GitHub reports the license as NOASSERTION, but the LICENSE file is the Apache-2.0 text. Independent check: the Xor Filters paper (ACM JEA 2020, arXiv 1912.08258; i7-6700, GCC 8.1.0, -O3 -march=native) measures a modified Cuckoo 12 at 31 ns/query vs Bloom 12 at 40 ns (10M keys, 25% find). In the same paper the original implementation measures 30 ns at 20.1 bits/key (Table 4).

Supports deletion unlike standard Bloom filters, but load factor caps insert capacity (\~95% full before insert failures); asymptotically worse in bits/item (O(log n)) than Bloom's O(1), though practically better for realistic table sizes with reasonably sized buckets; duplicate-heavy workloads (same item inserted &gt;2b times) can fail insertion.

## Maintenance

Abandoned: the last commit (2021-11-12) only removed an include flag, the last real fixes landed in 2017, and 22 issues and PRs remain open. The Apache-2.0 src/ is about 2k lines and easy to vendor, but expect to patch sizing, width checks and serialization yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed ACM CoNEXT'14 paper compares the cuckoo filter against a standard Bloom filter (Table 3, Figs. 4-5) on 2x Xeon L5640. It gives no compiler or flags, and the Bloom baselines are not in the repo's benchmarks/ (conext-figure5.cc and conext-table3.cc only exercise CuckooFilter), so it cannot be A.
- **Verifier notes:** The CoNEXT paper's Table 3 and the 7.2-bit/3% crossover check out, but the Fig. 5 paraphrase was overstated: the CF is not flat at \~11 MOPS and the BF bottoms out near \~4.9 MOPS, not \~4. So the peak ratio is \~2.4x, not \~2.75x. Metadata verified: Apache-2.0 LICENSE file, last commit 2021-11-12 (abandoned), 1013 stars, not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <http://www.cs.cmu.edu/~binfan/papers/conext14_cuckoofilter.pdf>
  - <https://github.com/efficient/cuckoofilter>
  - <https://github.com/efficient/cuckoofilter/blob/master/LICENSE>
  - <https://github.com/efficient/cuckoofilter/tree/master/benchmarks>
  - <https://arxiv.org/pdf/1912.08258>
- **Sources the enricher read:**
  - <https://github.com/efficient/cuckoofilter>
  - <https://github.com/efficient/cuckoofilter/blob/master/README.md>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/cuckoofilter.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/singletable.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/packedtable.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/hashutil.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/bitsutil.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/simd-block.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/Makefile>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/Makefile>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/conext-figure5.cc>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/conext-table3.cc>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/bulk-insert-and-query.cc>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/timing.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/example/test.cc>
  - <https://github.com/efficient/cuckoofilter/blob/master/LICENSE>
  - <https://github.com/efficient/cuckoofilter/issues>
  - <https://github.com/efficient/cuckoofilter/pulls>
  - <https://github.com/efficient/cuckoofilter/issues/2>
  - <https://github.com/efficient/cuckoofilter/issues/3>
  - <https://github.com/efficient/cuckoofilter/issues/6>
  - <https://github.com/efficient/cuckoofilter/issues/9>
  - <https://github.com/efficient/cuckoofilter/issues/12>
  - <https://github.com/efficient/cuckoofilter/issues/28>
  - <https://github.com/efficient/cuckoofilter/issues/30>
  - <https://github.com/efficient/cuckoofilter/issues/34>
  - <https://github.com/efficient/cuckoofilter/issues/37>
  - <https://github.com/efficient/cuckoofilter/issues/39>
  - <https://github.com/efficient/cuckoofilter/issues/43>
  - <https://github.com/efficient/cuckoofilter/issues/44>
  - <https://github.com/efficient/cuckoofilter/issues/46>
  - <https://github.com/efficient/cuckoofilter/issues/47>
  - <http://www.cs.cmu.edu/~binfan/papers/conext14_cuckoofilter.pdf>
  - <https://arxiv.org/pdf/1912.08258>
  - <https://hn.algolia.com/api/v1/search?query=cuckoo%20filter&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:cuckoo-filter`) · [data/wave6/enrich/raw/paper_cuckoo_filter.json](../../../data/wave6/enrich/raw/paper_cuckoo_filter.json) (enrichment confidence 0.87)

</details>
