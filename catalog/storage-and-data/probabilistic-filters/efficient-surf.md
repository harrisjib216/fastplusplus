# SuRF (Succinct Range Filter)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Static trie-based range filter (SIGMOD'18); beats Bloom filters on range seeks in RocksDB, loses on point lookups.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | RocksDB with SuRF vs RocksDB's Bloom filter at equal filter size: open-range (Open-Seek) queries 1.5x faster, and closed-range queries up to 5x faster (SuRF-Real, when 99% of queries return empty). On the worst-case all-miss point-query workload, the abstract says RocksDB is up to 40% slower with SuRF because of a higher false-positive rate (0.2% vs 0.1%). Fig. 12 point throughput is 32.9 Kops/s for Bloom, 19.8 for SuRF-Hash and 16.4 for SuRF-Real. So SuRF-Real is about 50% slower (derived from page data). |
| **Workload** | RocksDB replacement of its Bloom filters with SuRF on a synthetic 100GB time-series dataset (2K simulated sensors, 128-bit keys); end-to-end open-range, closed-range, and worst-case (all-missing-key) point query throughput, SIGMOD 2018 Best Paper |
| **Metric** | latency |
| **Hardware** | Intel Core i7-6770HQ CPU, 32GB RAM, Intel 540s 480GB SSD |
| **Compiler and flags** | Not stated in the paper. The SuRF repo's CMake Release flags are -O3 -Wall -Werror -mpopcnt -pthread -std=c++11, with the compiler unspecified. The RocksDB end-to-end runs used the efficient/rocksdb fork, whose build flags were not checked. |
| **Adoption** | 554 stars; SIGMOD 2018 Best Paper; evaluated as a RocksDB Bloom-filter replacement |
| **Last commit** | 2022-03-11 |
| **Links** | [repository](https://github.com/efficient/SuRF) · [benchmark](http://www.cs.cmu.edu/~huanche1/publications/surf_paper.pdf) |

## Verdict

The SIGMOD'18 paper replaced RocksDB's Bloom filters with SuRF at equal memory (14 bits/key; SuRF with a 4-bit suffix; public efficient/rocksdb fork on RocksDB 5.8) on a synthetic 100 GB time-series (2K sensors, 128-bit keys, 1 KB values, Snappy) running on an Intel i7-6770HQ with 32 GB RAM, an Intel 540s SSD and a 1 GB block cache; compiler not stated. Open-Seek throughput went from 1.97 to 3.10 Kops/s (about 1.5x) and Closed-Seek was up to 5x faster with 99% empty ranges, but all-miss point queries fell from 32.9 to 19.8 (SuRF-Hash) or 16.4 (SuRF-Real) Kops/s; the paper measured throughput and I/Os per operation, not latency.

## Use it when

- LSM-tree or sorted-run storage (SSTables, immutable segments), where the filter is built once per file from already-sorted keys and you want to skip files on Seek. The paper measured Open-Seek at 1.5x and Closed-Seek at up to 5x over Bloom filters in RocksDB.
- Time-series or event stores that often ask 'did anything happen in [t1, t2]?' and where most short ranges come back empty. The 5x gain was measured with 99% of ranges empty.
- You need an approximate count of keys in a range. The code comment says it can undercount by at most 2 at the boundaries.
- Static key sets of variable-length byte strings, or integers encoded big-endian with the bundled uint64ToString helper so byte order matches numeric order. Budget about 10 bits/key (random 64-bit ints) to 14 bits/key (emails) before suffix bits.
- Many threads doing point lookups or iterator seeks on one shared, read-only filter. The paper's Appendix C shows point-query throughput scaling across 10 cores and 20 hyper-threads.

## Skip it when

- Point-lookup-only workloads. The paper says 'the Bloom filter is usually a better choice than SuRF'. In the RocksDB all-miss test at 14 bits/key, throughput was 32.9 Kops/s for Bloom, 19.8 for SuRF-Hash and 16.4 for SuRF-Real, because I/Os per operation were 0.022 vs 0.047 and 0.056.
- Dynamic sets. The filter is static and needs a full rebuild to add keys; there is no delete. Appendix A only sketches how updates could be added.
- Long keys with long shared prefixes, such as emails or URLs. The paper shows SuRF slower than Bloom on email keys and with higher false-positive rates, and SuRF-Base size has no theoretical upper bound because it depends on the key distribution.
- Adversarial or key-correlated range queries, or anywhere you need a guaranteed range false-positive rate. SuRF's rate depends on the stored and queried key distributions. Later work such as Grafite (arXiv 2311.15380) targets bounded, distribution-independent range false-positive rates.
- Production use without your own hardening. This is research code: x86-only (SSE2 and POPCNT hard-coded), no releases, and correctness bugs fixed as late as March 2022 (issue #13: false negatives from uninitialized label-vector tail bytes). Issue #11, a double free when destroying a deserialized SuRF, is still open. It also gives no benefit for long scans, because the paper saw no speedup on Next.

## How it is fast

It is built on the Fast Succinct Trie (FST), a hybrid LOUDS-DS encoding: the few hot upper levels use LOUDS-Dense (256-bit label and child bitmaps per node, so a child lookup is one array access plus a rank), and the large lower levels use LOUDS-Sparse at about 10 bits per node. Rank is a single-level lookup table over 512-bit blocks plus POPCNT, select uses a table sampled every 64 set bits, sparse-node label search compares 16 labels at a time with SSE2, and lookups prefetch across the parallel bit sequences. The filter keeps only the shortest unique prefix of each key, plus optional hashed suffix bits (fewer point-query false positives) or real key-suffix bits (these also help range queries). The RocksDB gain is avoided I/O: moveToKeyGreaterThan gives each SSTable's smallest candidate key &gt;= the low bound without reading a data block.

## Compared with alternatives

Every sibling here (Prefix, Xor/Binary Fuse, BuRR/Ribbon, Morton, Vacuum) is a point-membership filter; SuRF is the only one that answers range emptiness, seek-to-next-key and approximate counts, so pick it only when range queries matter. For point-only filtering a sibling will be smaller and faster, since SuRF's own paper concedes point queries to Bloom.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the filter itself (C++ standard library and SSE2 intrinsics); GoogleTest for the unit tests; YCSB, Python and the ARF git submodule for the benchmarks; the RocksDB integration lives in the separate efficient/rocksdb fork |
| **Minimum toolchain** | C++11 with GCC/Clang builtins (__builtin_popcountll, __builtin_bswap64, __builtin_ctz, __builtin_prefetch) and -mpopcnt; CMake 2.6+ for the tests and benchmarks; CI config used GCC on Ubuntu 16.04 (xenial); no MSVC support documented |
| **Platforms** | x86-64 only as written (unconditional &lt;emmintrin.h&gt; SSE2 label search, -mpopcnt required); no aarch64 or other fallback |
| **Thread safety** | Building is single-threaded. lookupKey and moveToKeyGreaterThan/LessThan are const and safe for concurrent readers. lookupRange and approxCount(string, string) are non-const and reuse a member iterator, so they are NOT safe to call concurrently on one instance; the author confirmed this in issue #5. For parallel range checks, use moveToKeyGreaterThan with a per-call iterator. |
| **Drop-in for the baseline** | partial — lookupKey matches a Bloom filter's may-contain semantics, but SuRF needs all keys up front as a sorted std::vector&lt;std::string&gt; and cannot take inserts. Using its range filtering in RocksDB needs the efficient/rocksdb fork (RocksDB 5.8 base, last pushed 2018-12), which adds Seek/SeekForPrev hooks to the filter reader interface. |

## Gotchas

- Input must be sorted in byte order, and release builds set -DNDEBUG, so nothing checks this. Issue #6 built from std::to_string(0..9999), which is not in lexicographic order, and got 9 false negatives out of 10,000. Duplicates are skipped. An empty key list or an empty-string key is only guarded by assert.
- The header defines functions that are not inline (config.hpp align/uint64ToString, SuRF::create, LabelVector::search, ...). Including surf.hpp from more than one .cpp gives duplicate-symbol link errors, so wrap it in a single translation unit, as the RocksDB fork does in util/surf.cc.
- Memory is managed by hand. \~SuRF() is empty, so you must call destroy() and then delete. destroy() frees the arrays but not the inner LoudsDense/LoudsSparse/bitvector objects. Copying a SuRF copies raw pointers, which leads to a double free. serialize() returns a new[] buffer the caller owns, in a raw native-endian format with no version or checksum.
- The shipped defaults differ from the paper: kSparseDenseRatio is 16 (the paper says R=64, and the 64 line is commented out) and the LOUDS-Dense rank block is 512 bits, not the paper's 64. Re-tune before comparing against the published numbers.

## Known shortcomings

- Wins only on range queries (open seek \~1.5x, closed seek up to 5x at 99% empty); on all-miss point queries Bloom is faster (32.9 vs 19.8/16.4 Kops/s). Static: keys must be pre-sorted, unchecked under NDEBUG, giving false negatives (#6); no insert/delete. x86-only (SSE2 + POPCNT hard-coded). Non-inline functions in headers cause link errors across translation units. lookupRange/approxCount share a member iterator, so not thread-safe (#5). Manual memory: empty destructor, partial destroy(), shallow copies double-free (#11 open); a false-negative bug was fixed only in 2022-03. Code defaults differ from the paper (ratio 16 vs 64); the RocksDB fork is frozen on 5.8 since 2018.

## Caveats and trade-offs

This is a mixed result, not a strict win. SuRF is 40-50% slower for all-miss point queries at equal filter size, and the paper says adding a few suffix bits per key closes the gap. Its wins (1.5x-5x) are for range queries only. The paper reports throughput in Kops/s, not latency. The end-to-end code lives in the efficient/rocksdb fork (last push 2018-12-20). The microbenchmarks (bench/workload.cpp vs bench/filter_bloom.hpp) ran on a Xeon E5-2680 v2. The GitHub license API says NOASSERTION, but the LICENSE file is the plain Apache-2.0 text. bench/bloom.hpp is LevelDB-derived code under a BSD-style license.

SuRF trades a higher false-positive rate for the ability to answer range queries and approximate range counts, which plain Bloom filters cannot do at all; for pure point-query, moderate-FPP workloads the paper itself says 'the Bloom filter is usually a better choice than SuRF'; construction speed is comparable to Bloom filter's.

## Maintenance

Abandoned (last commit 2022-03-11, no releases or tags, 4 open issues, RocksDB fork frozen since 2018-12) but Apache-2.0 (the GitHub API says NOASSERTION; LICENSE is the plain Apache text) and only about 3.5k lines across 12 headers, so it can be vendored if you accept x86-only and hand-managed memory.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed SIGMOD'18 paper compares RocksDB using SuRF against RocksDB's Bloom filters at equal memory (14 bits/key) on an i7-6770HQ. The code is public: bench/ in the repo and the efficient/rocksdb fork. The paper states no compiler name or version, so the entry cannot be tier A.
- **Verifier notes:** The numbers match the abstract and Sec. 6. Fig. 12 shows SuRF-Real's point-query penalty is about 50%, larger than the abstract's 40%, so this was added. The record's metric 'latency' is wrong: the paper measures throughput and I/Os per operation. The metric field is not correctable here. Metadata checks out: Apache-2.0, 554 stars, last commit 2022-03-11, abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <http://www.cs.cmu.edu/~huanche1/publications/surf_paper.pdf>
  - <https://github.com/efficient/SuRF>
  - <https://raw.githubusercontent.com/efficient/SuRF/master/README.md>
  - <https://raw.githubusercontent.com/efficient/SuRF/master/LICENSE>
  - <https://raw.githubusercontent.com/efficient/SuRF/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/efficient/SuRF/master/bench/bloom.hpp>
  - <https://github.com/efficient/rocksdb>
- **Sources the enricher read:**
  - <https://github.com/efficient/SuRF>
  - <https://github.com/efficient/SuRF/blob/master/README.md>
  - <https://github.com/efficient/SuRF/blob/master/include/surf.hpp>
  - <https://github.com/efficient/SuRF/blob/master/include/surf_builder.hpp>
  - <https://github.com/efficient/SuRF/blob/master/include/config.hpp>
  - <https://github.com/efficient/SuRF/blob/master/include/label_vector.hpp>
  - <https://github.com/efficient/SuRF/blob/master/include/louds_dense.hpp>
  - <https://github.com/efficient/SuRF/blob/master/include/louds_sparse.hpp>
  - <https://github.com/efficient/SuRF/blob/master/include/popcount.h>
  - <https://github.com/efficient/SuRF/blob/master/include/rank.hpp>
  - <https://github.com/efficient/SuRF/blob/master/include/select.hpp>
  - <https://github.com/efficient/SuRF/blob/master/include/bitvector.hpp>
  - <https://github.com/efficient/SuRF/blob/master/include/hash.hpp>
  - <https://github.com/efficient/SuRF/blob/master/CMakeLists.txt>
  - <https://github.com/efficient/SuRF/blob/master/.travis.yml>
  - <https://github.com/efficient/SuRF/blob/master/.gitmodules>
  - <https://github.com/efficient/SuRF/blob/master/simple_example.cpp>
  - <https://github.com/efficient/SuRF/blob/master/bench/filter_surf.hpp>
  - <https://github.com/efficient/SuRF/blob/master/bench/workload_multi_thread.cpp>
  - <https://github.com/efficient/SuRF/issues?q=is%3Aissue>
  - <https://github.com/efficient/SuRF/issues/4>
  - <https://github.com/efficient/SuRF/issues/5>
  - <https://github.com/efficient/SuRF/issues/6>
  - <https://github.com/efficient/SuRF/issues/8>
  - <https://github.com/efficient/SuRF/issues/9>
  - <https://github.com/efficient/SuRF/issues/10>
  - <https://github.com/efficient/SuRF/issues/11>
  - <https://github.com/efficient/SuRF/issues/13>
  - <https://github.com/efficient/SuRF/issues/14>
  - <https://github.com/efficient/SuRF/issues/15>
  - <https://github.com/efficient/SuRF/commits/master>
  - <http://www.cs.cmu.edu/~huanche1/publications/surf_paper.pdf>
  - <https://github.com/efficient/rocksdb>
  - <https://github.com/efficient/rocksdb/blob/master/util/surf.cc>
  - <https://github.com/efficient/rocksdb/blob/master/include/rocksdb/version.h>
  - <https://hn.algolia.com/api/v1/search?query=SuRF%20succinct%20range%20filter&tags=story>
  - <https://arxiv.org/abs/2311.15380>
  - <https://github.com/marcocosta97/grafite>
  - <https://github.com/marcocosta97/grafite/blob/HEAD/bench/reproducibility.md>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/efficient/surf`) · [data/wave6/enrich/raw/github_com_efficient_surf.json](../../../data/wave6/enrich/raw/github_com_efficient_surf.json) (enrichment confidence 0.85)

</details>
