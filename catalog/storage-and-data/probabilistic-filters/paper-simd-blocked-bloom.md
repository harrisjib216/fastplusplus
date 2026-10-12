# SIMD Blocked Bloom Filter (src/simd-block.h, Impala-derived)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> AVX2 split-block Bloom filter: one 32-byte block per key, about 2-3x faster queries than a standard Bloom filter.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | Xor Filters paper (Graf & Lemire, ACM JEA 2020), testing the Impala AVX2 blocked Bloom that is also used in efficient/cuckoofilter, modified for flexible sizes. Membership tests take 16 ns/query vs 31 ns (Bloom 8) and 40 ns (Bloom 12) at 10M keys with 25% find, and 20 ns vs 53 ns and 58 ns at 100M keys (Table 3; \~1.9-2.9x, derived from page data). Construction takes 10 ns/key vs 40 and 60 ns/key at 10M keys, and 20 ns/key vs 70 and 90 ns/key at 100M keys (Table 2). The trade-off is 10.7 bits/key at 0.94% FPP vs 0.31% for Bloom 12. |
| **Workload** | Single-threaded bulk construction and membership tests on 10M and 100M pseudo-random 64-bit keys (Murmur-finalizer hash), with 25% of queries on existing keys. Blocked Bloom (10.7 bits/key) is compared with standard Bloom filters at 8, 12 and 16 bits/key, using FastFilter/fastfilter_cpp benchmarks/bulk-insert-and-query.cc. |
| **Metric** | throughput |
| **Hardware** | Intel i7-6700 (Skylake) @ 3.4 GHz, 8 MB L3 |
| **Compiler and flags** | GNU GCC 8.1.0, -O3 -march=native (per paper) |
| **Adoption** | 1013 stars (host repo) |
| **Last commit** | 2021-11-12 |
| **Links** | [repository](https://github.com/efficient/cuckoofilter) · [benchmark](https://arxiv.org/pdf/1912.08258) |

## Verdict

The Xor Filters paper (Graf & Lemire, ACM JEA 2020) benchmarked a modified copy of this kernel (fastfilter_cpp's SimdBlockFilterFixed: non-power-of-2 sizing, 10.7 bits/key, Murmur-finalizer hash) single-threaded with GCC 8.1.0 -O3 -march=native on an Intel i7-6700 Skylake at 3.4 GHz. With 25% of queries present it took 16 ns per query vs 31 ns (Bloom, 8 bits/key) and 40 ns (Bloom, 12 bits/key) at 10M keys, 20 ns vs 53/58 ns at 100M keys, and 10-20 vs 40-90 ns/key to build, at 0.94% FPP vs 2.2% (Bloom 8) and 0.31% (Bloom 12).

## Use it when

- Read-heavy membership pre-checks (join or semi-join filters, skipping disk or LSM or Parquet-style reads) where a false-positive rate of roughly 0.4-19% is acceptable, the range its author gives. fastfilter_cpp's tuning notes put its lowest space overhead near 1-1.4% FPP.
- Large filters that spill out of cache (10M-100M+ keys), where the single-block access pays off most: 20 ns vs 53-58 ns per query at 100M keys in the Xor Filters paper.
- Insert-heavy or streaming construction: 10-20 ns/key vs 40-90 ns/key for standard Bloom. Unlike a cuckoo filter, Add never fails.
- x86-64 servers with AVX2 (Haswell or later) whose keys are already 64-bit integers or 64-bit hashes.
- As a \~140-line reference kernel to vendor. The same block scheme (identical salt constants) is standardized as Parquet's split block Bloom filter and is used in Impala, Kudu, Arrow and StarRocks.

## Skip it when

- You need a false-positive rate below about 0.4%. With a fixed 8 bits set per key, space grows fast: Parquet's SBBF table needs 16.9 bits/key for 0.1% and 26.4 for 0.01%, while an optimal standard Bloom filter needs 1.44\*log2(1/eps), about 14.4 bits/key for 0.1%.
- Memory is the binding constraint. In the paper it used 10.7 bits/key at 0.94% FPP, while Xor8 used 9.8 bits/key at 0.39%. The author's note says a standard Bloom filter reaches 0.63% in the space this filter needs for 1.0%.
- You need deletes, counting, serialization, or OR-merging of filters. The hash seed is random per instance, so two filters built separately cannot be unioned.
- Non-AVX2 x86, ARM, MSVC or Windows. The code uses AVX2 intrinsics, posix_memalign, unsigned __int128 and GCC builtins, and the constructor throws std::runtime_error on CPUs without AVX2.
- You want maintained code. simd-block.h has not changed since Dec 2016 or the repo since Nov 2021, and PR #32 (a hashing change the author reports as 15% faster) was never merged.

## How it is fast

It is a split block Bloom filter, combining Putze et al.'s cache-blocked Bloom filter with Broder-Mitzenmacher split filters. One hash picks a 256-bit block, and one AVX2 multiply (_mm256_mullo_epi32 by eight odd constants, shift right 27) turns the rest into eight 5-bit indices that set one bit in each 32-bit lane. Insert is a single OR-store and lookup a single _mm256_testc_si256, so each operation touches one 32-byte-aligned block with a fixed, branch-free instruction count. A standard Bloom filter does k scattered memory probes instead, which is why the gap grows from about 2x at 10M keys to about 2.7-2.9x at 100M keys.

## Compared with alternatives

Pick it over the Cuckoo Filter in the same repo when you never delete and can live with about 1% FPR: the repo's own benchmark shows 55-74M adds/sec vs 23-35M for Cuckoo8, and inserts cannot fail. Pick it over the Xor Filter or BuRR/Ribbon when keys arrive incrementally or build and query speed beat space (10 vs 110 ns/key build, 16 vs 23 ns query at 10M keys vs Xor8); pick those when bits/key matter.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | OpenSSL headers, pulled in transitively by hashutil.h (#include &lt;openssl/evp.h&gt;) even though the filter does not use them. The repo Makefiles also link -lssl -lcrypto. The filter needs nothing else. |
| **Minimum toolchain** | C++11 (the repo builds with --std=c++11). Needs GCC or Clang extensions (__builtin_cpu_supports, [[gnu::always_inline]], unsigned __int128); MSVC support is not documented. |
| **Platforms** | x86-64 with AVX2 only (the benchmarks compile with -march=core-avx2), on POSIX systems (posix_memalign). fastfilter_cpp's derived SimdBlockFilterFixed adds aarch64 NEON and SSE4.1 variants. |
| **Thread safety** | Not documented. By code inspection, Find is const and read-only, so concurrent lookups on a finished filter are safe. Add does a non-atomic 256-bit load-OR-store, so concurrent Adds need external locking or they can lose bits, which causes false negatives. |
| **Drop-in for the baseline** | partial — same insert-only, false-positives-only semantics as a Bloom filter, but a different interface: the constructor takes log2(bytes), keys are uint64_t only, and there is no FPR/k parameter, union or serialization |

## Gotchas

- The move constructor copies directory_ without nulling the source's pointer, so both destructors free the same buffer if a move actually runs. Returning the filter by value, as the repo's benchmark does, only works because of copy elision.
- Size is always 2^log_heap_space bytes, so bits/key and FPR jump with n. The repo's own benchmark, using the same sizing rule, shows 8.95-15.79 bits/item and 0.14%-2.07% FPR across runs. Overfilling degrades FPR silently rather than failing; Parquet's spec cites about 18% at 5 bits/key.
- The default TwoIndependentMultiplyShift hash is seeded from std::random_device in every constructor, so filters are not reproducible across runs or processes and cannot be merged. It is only 2-independent, and the repo's random.h warns that multiply-shift behaves non-randomly on some structured inputs. The paper's benchmark used a Murmur finalizer instead.
- Build flags: it needs -mavx2 (or -march) and, per its own comment, -fno-strict-aliasing, because of the __m256i reinterpret_casts. It also relies on transitive includes for memset and std::runtime_error, since there is no &lt;cstring&gt; or &lt;stdexcept&gt;.

## Known shortcomings

- The paper's blocked Bloom filter is not simd-block.h (added 2016-12); independent numbers come from the Xor filter paper (arXiv 1912.08258): 16 ns vs 31/40 ns at 10M keys, measured with fastfilter_cpp.
- From code reading (not run): the move constructor never nulls the source pointer, so a move double-frees; Add is not thread-safe. Power-of-two sizing (its own bench: 8.95-15.79 bits/key, 0.14-2.07% FPR); FPR below 0.4% is costly (0.1% needs 16.9 bits/key per the Parquet SBBF spec). AVX2 + POSIX + GCC/Clang only; needs OpenSSL headers; per-instance random seed prevents merge/serialize.
- Abandoned; a +15% PR (#32) is unmerged. Maintained successor: jbapple/libfilter.

## Caveats and trade-offs

The original record wrongly attributed the CoNEXT'14 paper's blk-BF numbers (Table 3's 7.64M keys/sec, the Fig. 5 '\~4 MOPS' gap) to this code. The paper's blocked Bloom is its own 2014 implementation with 64-byte blocks and k=9. src/simd-block.h was added to efficient/cuckoofilter by Jim Apple in Dec 2016, two years later. This repo's own benchmarks/bulk-insert-and-query.cc header shows SimdBlock8 at \~55-75M adds/sec and \~58-75M finds/sec, vs Cuckoo12 at \~16-24M adds/sec and \~32-37M finds/sec. It includes no standard Bloom and no hardware (first-party, Tier C on its own). The peer-reviewed numbers come from a modified copy in FastFilter/fastfilter_cpp src/bloom/simd-block.h, credited there as 'from apache/impala (via the cuckoo filter)'. The filter needs AVX2 (x86-only) and has a higher FPR per bit than a standard Bloom filter.

Higher false positive rate than standard Bloom at equal space (0.43% vs 0.19% at 13 bits/item, Table 3) because hashing items to one of many small per-block filters creates imbalanced "hot"/"cold" blocks even with strong hash functions; no deletion support.

## Maintenance

Abandoned (simd-block.h untouched since Dec 2016, repo since Nov 2021) but Apache-2.0 and about 140 lines, so easy to vendor; for maintained code, use the author's jbapple/libfilter (C/C++/Java/Go, last push Aug 2023, with an NDV/FPP sizing API) or fastfilter_cpp's non-power-of-2 variant.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** The CoNEXT'14 blk-BF (64-byte blocks, k=9) is not src/simd-block.h, which Jim Apple added to the repo in Dec 2016. The valid evidence is the peer-reviewed Xor Filters paper (ACM JEA 2020), which benchmarks this Impala-derived AVX2 blocked Bloom against standard Bloom filters with full methodology (i7-6700, GCC 8.1.0, -O3 -march=native, code in FastFilter/fastfilter_cpp benchmarks/bulk-insert-and-query.cc). The benchmarked copy is a modified one (non-power-of-2 sizes) in fastfilter_cpp, not this repo's file, so the tier is B rather than A.
- **Verifier notes:** This is a real, well-known fast filter, but the record's evidence described a different implementation. It is replaced with the Xor Filters JEA 2020 comparison, which supports the win over standard Bloom with complete methodology. If the orchestrator re-points repo_url to FastFilter/fastfilter_cpp, the entry would qualify for Tier A. Host repo metadata was verified (Apache-2.0, last commit 2021-11-12, 1013 stars).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <http://www.cs.cmu.edu/~binfan/papers/conext14_cuckoofilter.pdf>
  - <https://github.com/efficient/cuckoofilter>
  - <https://github.com/efficient/cuckoofilter/commits/master/src/simd-block.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/bulk-insert-and-query.cc>
  - <https://arxiv.org/pdf/1912.08258>
  - <https://api.crossref.org/works/10.1145/3376122>
  - <https://github.com/FastFilter/fastfilter_cpp>
- **Sources the enricher read:**
  - <https://github.com/efficient/cuckoofilter>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/simd-block.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/hashutil.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/Makefile>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/Makefile>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/bulk-insert-and-query.cc>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/random.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/LICENSE>
  - <https://github.com/efficient/cuckoofilter/commits/master/src/simd-block.h>
  - <https://github.com/efficient/cuckoofilter/issues/36>
  - <https://github.com/efficient/cuckoofilter/pulls?q=is%3Apr>
  - <https://github.com/efficient/cuckoofilter/pull/32>
  - <https://github.com/efficient/cuckoofilter/pull/38>
  - <https://arxiv.org/pdf/1912.08258>
  - <https://github.com/FastFilter/fastfilter_cpp/blob/master/src/bloom/simd-block.h>
  - <https://github.com/FastFilter/fastfilter_cpp/blob/master/src/bloom/simd-block-fixed-fpp.h>
  - <https://github.com/FastFilter/fastfilter_cpp/blob/master/benchmarks/bulk-insert-and-query.cc>
  - <https://github.com/apache/parquet-format/blob/master/BloomFilter.md>
  - <https://export.arxiv.org/api/query?search_query=all:%22split%20block%20Bloom%20filters%22>
  - <https://arxiv.org/pdf/2101.01719>
  - <https://github.com/jbapple/libfilter>
  - <https://hn.algolia.com/api/v1/search?query=split%20block%20bloom%20filter&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:simd-blocked-bloom`) · [data/wave6/enrich/raw/paper_simd_blocked_bloom.json](../../../data/wave6/enrich/raw/paper_simd_blocked_bloom.json) (enrichment confidence 0.8)

</details>
