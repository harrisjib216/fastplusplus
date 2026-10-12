# Morton Filter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> AMD Research's compressed, cache-line-blocked cuckoo filter with batched APIs; beats Fan et al.'s cuckoo filter on large, DRAM-resident filters.

| | |
|---|---|
| **Beats** | cuckoo filter |
| **Claimed result** | Paper vs Fan et al.'s reference cuckoo filter (CF): lookups 1.3x-2.5x faster (1.3x-2.5x for true negatives, Fig. 11; 1.6x-2.4x for true positives, Fig. 10), insertions 0.9x-15.5x (Fig. 12), deletions 1.3x-1.6x (Fig. 13). The README's 'up to 15.5x, 1.3x, and 2.5x' understates deletion; the paper says up to 1.6x. The MF uses about 11.71 bits/item at 0.95 load vs a 12-bit-fingerprint CF. The paper does not benchmark Bloom filters. Its point about using fewer bits than a Bloom filter below \~1-3% FPR is a general statement about cuckoo/quotient filters. |
| **Workload** | Fan et al.'s reference cuckoo filter (plus semi-sorted CF and RSQF) vs a Morton filter with 128\*1024\*1024 slots and 8-bit fingerprints (3-slot buckets). The filters are filled to each load factor in steps of 0.05. Then 0.1% of total slots are inserted, deleted or looked up with 64-bit random keys. Results are the average of 5 trials (VLDB 2018 paper). |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper 1950X (2x8 cores, 32 MB L3), frequency fixed at 3400 MHz, 128 GB DDR4-2133, Ubuntu 16.04.4 LTS (Linux 4.11.0) |
| **Compiler and flags** | g++ 5.4.0-6 with -Ofast -march=native (paper Sec. 6). The repo benchmarking/Makefile uses -Ofast -march=native -mpopcnt -std=c++11. The README recommends g++ 5.4 and reports a GCC 8.x performance regression as of March 2019. |
| **Adoption** | 90 stars; developed at AMD Research, published at VLDB 2018 with an extended version in the VLDB Journal (2019) |
| **Last commit** | 2020-12-16 |
| **Links** | [repository](https://github.com/AMDComputeLibraries/morton_filter) · [benchmark](https://www.vldb.org/pvldb/vol11/p1041-breslow.pdf) |

## Verdict

In the VLDB'18 paper, on an AMD Threadripper 1950X fixed at 3.4 GHz (g++ 5.4.0, -Ofast -march=native, single-threaded, 128M-slot filters, average of 5 trials), Morton3_8 at 11.71 bits/item was 1.3x to 2.5x faster than Fan et al.'s 12-bit reference cuckoo filter on negative lookups, 1.6x to 2.4x on positive lookups, 0.9x to 15.5x on inserts and 1.3x to 1.6x on deletes, measured over load factors 0.05 to 0.95. The same paper's Skylake-X run shows smaller gains (lookups 1x to 1.8x, deletes about 1.2x, inserts about 0.67x to 3x), and a later deletion correctness fix cut peak Morton delete throughput from about 38 to about 28 MOPS, so current code may not reach the paper's delete numbers.

## Use it when

- Filters of hundreds of MB (the paper uses 128M slots, about 187 MB) that live in DRAM, where memory bandwidth rather than hashing limits throughput.
- Workloads that can issue operations in batches of 128 uint64 keys, such as bulk loading or batched probes in a join or LSM lookup path.
- Dynamic sets that need deletions and are filled to high load (0.75 to 0.95), where the paper measured inserts about 3x to 15x faster than a stock cuckoo filter.
- Sets whose size you cannot predict and cannot rebuild from source keys: in-place 2x/4x/8x growth works without a backing store, at the cost of roughly one fingerprint bit of false-positive accuracy per doubling.
- About 0.3% false-positive rate at about 11.7 bits/item (Morton3_8), or about 10 bits/item with Morton7_8, on AMD Zen-class CPUs where the paper's tuning was done.

## Skip it when

- One-at-a-time queries. The README discourages them, and the Xor filter paper (i7-6700, GCC 8.1) measured Morton single queries at 47 and 65 ns/key (10M and 100M keys) against 31 and 38 ns for a 12-bit cuckoo filter and 23 and 32 ns for Xor8.
- Intel servers without retuning. The paper's own Skylake-X run shows lookups only on par to 1.8x faster and inserts at about 2/3 of the cuckoo filter's speed below 0.5 load; the Vacuum Filter paper (Xeon E5-2687W) measured Morton at about 6x Bloom-filter throughput vs about 10x for cuckoo; the Prefix Filter paper (Ice Lake) dropped Morton as strictly worse than the vector quotient filter.
- Static sets built once: xor, binary fuse or ribbon filters use less space (Xor8 about 9.8 bits/key at a similar FPR) and query faster.
- Production code that must be robust. The author calls it an academic prototype; errors, including allocation failure, call exit(1); the repo has no unit tests; nothing has been committed since December 2020.
- MSVC or non-x86 builds: the code depends on __uint128_t and GCC vector extensions, the README says only g++ is supported (Clang fixes came in late 2020), and only x86-64 has been tested.

## How it is fast

Each 512-bit (cache-line) block holds a compressed Fingerprint Storage Array (46 x 8-bit slots in Morton3_8), a Fullness Counter Array (64 x 2-bit counters for 64 logical 3-slot buckets) and a 16-bit Overflow Tracking Array. Buckets are logically underloaded but empty slots are not stored ('decoupled logical sparsity'), and a bucket's offset is found by a branchless popcount-based prefix sum over the counters. Insertions are heavily biased to the primary hash H1, and the OTA records overflows, so most lookups, positive or negative, touch one cache line (about 1.05 to 1.11 lines per query at 0.95 load in the paper). The alternate bucket is chosen with a bounded odd offset rather than Fan et al.'s XOR, which keeps both candidates on the same page (fewer TLB misses) and drops the power-of-two table size requirement; keys are processed in batches of 128 (the paper's Fig. 14 credits batching with about 2x and the popcount reduction with another 2x to 3x).

## Compared with alternatives

Pick it over Xor/Binary Fuse and BuRR when the set changes after construction (they are static), and over Prefix Filter when you need deletions (Prefix Filter is insert-only by design). Otherwise its only distinctive feature is in-place growth without the source keys: on Intel, the Vacuum Filter paper (Xeon E5-2687W) puts Morton at about 6x Bloom-filter throughput against about 10x for cuckoo and 11x for Vacuum, with Vacuum also supporting deletions and resizing, and the Prefix Filter authors found Morton strictly worse than the vector quotient filter.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the filter itself; the benchmark harness clones Fan et al.'s cuckoofilter at a pinned commit and links -lcrypto |
| **Minimum toolchain** | C++11 (Makefile uses -std=c++11), GCC with GNU extensions; the README recommends g++ 5.4 and reports a GCC 8.x slowdown; Clang fixes (the issue #2 128-bit-shift UB and a non-constexpr log2) landed only in the final Dec 2020 commit |
| **Platforms** | x86-64 is the only tested target (benchmarks built with -march=native -mpopcnt; BMI2 is used if present); no MSVC (__uint128_t, GCC vector extensions); other architectures not documented |
| **Thread safety** | not documented; the code has no locks or atomics and uses the global rand() during evictions, so treat it as single-threaded or synchronize externally |
| **Drop-in for the baseline** | partial: same operations as a cuckoo filter (insert, lookup, delete; delete only keys that were inserted), but a different API. Operations are batched over std::vector&lt;uint64_t&gt; with a std::vector&lt;bool&gt; status output, keys are uint64_t (32-bit only by editing CCF_KEY_SIZE), and the configuration is chosen through 17 template parameters or the preset typedefs. |

## Gotchas

- The batch loops always process full 128-key chunks and read keys[i..i+127]. If num_keys is not a multiple of 128 they read past the end of the input (a README known issue). insert_many always returns true, so check the status vector, which must be pre-sized.
- There is no stash or victim cache. After 300 cuckoo kicks the insert returns false with the fingerprint it was carrying dropped, and that fingerprint can belong to an earlier key, which can cause a false negative. Deleting a key that was never inserted can also delete another key's fingerprint.
- util.h and test_util.h define non-inline functions (operator&lt;&lt; for __uint128_t, Test::pass) in headers, so including the library from more than one .cc file gives duplicate-symbol link errors unless you patch them to inline.
- The class owns raw aligned_alloc buffers and has a destructor but no copy constructor or assignment operator, so copying a filter double-frees. Resizing is compiled off in every preset (resizing_enabled = false), so double_capacity() calls exit(1) unless you flip it. Issue #4 (open since 2021): Morton1_8 fails to compile because of an over-broad static_assert.

## Known shortcomings

- Batch API needs key counts that are multiples of 128 (else reads past the input) and insert_many always returns true. No stash/victim cache: after 300 kicks a dropped fingerprint (possibly an earlier key's) causes false negatives. Non-inline functions in headers cause duplicate-symbol link errors; no copy constructor (copies double-free); exit(1) on errors; Morton1_8 doesn't compile (#4). Abandoned since 2020-12, g++/x86 only.

## Caveats and trade-offs

The README says this is an academic prototype. The batch API works correctly only when the input is a multiple of 128. A later deletion correctness fix cut peak deletion throughput from about 38 to about 28 MOPS, so current code may not reproduce the paper's deletion numbers. Insertion speedup is 0.9x (slower) at some load factors. The repo has no commits since 2020-12-16.

Supports self-resizing (grow capacity without a backing structure) unlike vanilla cuckoo filters; requires only a multiple-of-two bucket count rather than a power of two; author explicitly labels the code 'academic-style prototype', not hardened for production.

## Maintenance

Abandoned: the last commit is a December 2020 bug-fix merge (the author no longer has write access) and one issue remains open; the code is an MIT-licensed academic prototype that is small enough to vendor but needs local patches (the multiple-of-128 batch limit, inline fixes for the header ODR problem, and copy safety) before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A. The VLDB'18 paper (Sec. 6) states the CPU (AMD Ryzen Threadripper 1950X fixed at 3.4 GHz), the compiler (g++ 5.4.0-6) and the flags (-Ofast -march=native). The benchmark code is public in the repo: benchmarking/benchmark_mf.cc and benchmarking/benchmark_cf.cc, whose Makefile clones Fan et al.'s efficient/cuckoofilter at a pinned commit and patches it for the head-to-head baseline.
- **Verifier notes:** The paper's methodology is complete and the benchmark harness is in the repo, so the tier is upgraded to A. claimed_speedup is corrected to the paper's ranges. The README's deletion figure (1.3x) is the low end of the paper's 1.3x-1.6x. Metadata checks out: MIT license, 90 stars, last commit 2020-12-16, abandoned, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `workload`, `caveats`
- **Shortcomings recorded by:** Independent: the Xor filter paper (i7-6700) measured single-query Morton at 47/65 ns vs cuckoo CF12 31/38 ns; the Prefix filter paper (Ice Lake) found it strictly worse than VQF; an own Skylake-X run had inserts \~0.67x cuckoo at low load.
- **Pages the verifier opened:**
  - <https://www.vldb.org/pvldb/vol11/p1041-breslow.pdf>
  - <https://github.com/AMDComputeLibraries/morton_filter>
  - <https://raw.githubusercontent.com/AMDComputeLibraries/morton_filter/master/README.md>
  - <https://raw.githubusercontent.com/AMDComputeLibraries/morton_filter/master/benchmarking/Makefile>
  - <https://raw.githubusercontent.com/AMDComputeLibraries/morton_filter/master/LICENSE.txt>
- **Sources the enricher read:**
  - <https://github.com/AMDComputeLibraries/morton_filter>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/README.md>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/morton_filter.h>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/compressed_cuckoo_filter.h>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/compressed_cuckoo_config.h>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/morton_sample_configs.h>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/vector_types.h>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/util.h>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/hash_util.h>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/test_util.h>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/benchmarking/Makefile>
  - <https://github.com/AMDComputeLibraries/morton_filter/blob/master/benchmarking/benchmark_mf.h>
  - <https://github.com/AMDComputeLibraries/morton_filter/commits/master>
  - <https://github.com/AMDComputeLibraries/morton_filter/issues/1>
  - <https://github.com/AMDComputeLibraries/morton_filter/issues/2>
  - <https://github.com/AMDComputeLibraries/morton_filter/pull/3>
  - <https://github.com/AMDComputeLibraries/morton_filter/issues/4>
  - <https://www.vldb.org/pvldb/vol11/p1041-breslow.pdf>
  - <https://arxiv.org/pdf/1912.08258>
  - <https://arxiv.org/pdf/2203.17139>
  - <https://www.vldb.org/pvldb/vol13/p197-wang.pdf>
  - <https://github.com/FastFilter/fastfilter_cpp>
  - <https://hn.algolia.com/api/v1/search?query=morton%20filter&tags=story>
  - <https://news.ycombinator.com/item?id=19757797>
  - <https://news.ycombinator.com/item?id=19725282>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/amdcomputelibraries/morton_filter`) · [data/wave6/enrich/raw/github_com_amdcomputelibraries_morton_filter.json](../../../data/wave6/enrich/raw/github_com_amdcomputelibraries_morton_filter.json) (enrichment confidence 0.82)

</details>
