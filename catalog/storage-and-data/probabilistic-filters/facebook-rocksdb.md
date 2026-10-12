# RocksDB Ribbon Filter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0 OR GPL-2.0` · 🟢 active

> RocksDB's built-in Ribbon SST filter: same FP rate as its Bloom filter in about 30% less memory, at 3-4x CPU.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | arXiv:2103.02515 Table 2, at an FP rate around 1% (r=7): Standard Ribbon w=128 (the 128-bit variant RocksDB ships) has 6-8% space overhead over the information-theoretic bound, depending on n. RocksDB's FastLocalBloom blocked Bloom has 49.8% and another blocked Bloom has 52.0%. The cost is CPU: at n=10^6, Ribbon takes 166 vs 21 ns/key to build and 58 vs 10 ns/key to query; at n=10^8 it is 235 vs 72 and 140 vs 36 ns/key. The RocksDB blog (2021-12-29) gives \~30% space savings for 3-4x CPU (typical 7 bits/key Ribbon vs 10 bits/key Bloom at the same FP rate). It also says 100M keys in one filter still save 27% vs 30% at 100K keys. Its filter_bench figures are 140 vs 32 ns/key to construct (\~4.4x, derived from page data) and 600 vs 500 ns/key to query (\~20% slower, derived from page data). |
| **Workload** | Static-filter space overhead, construction time and query time at an FP rate around 1% for n=10^6 and 10^8 keys. Source: the Ribbon paper's fastfilter_cpp fork benchmark (bulk-insert-and-query.cc via ribbon-benchmark.sh), which runs a copy of RocksDB's ribbon_\*.h code against RocksDB FastLocalBloom and other Bloom variants. Also the RocksDB blog's filter_bench figures (`./filter_bench -impl=2\|3 -quick -m_keys_total_max=200 -use_full_block_reader`, 'Random filter' queries). |
| **Metric** | memory |
| **Hardware** | Single-socket Intel Xeon D-2191 (Skylake DE), 64GB RAM (paper Table 2); not stated for the blog's filter_bench numbers |
| **Compiler and flags** | GCC 8.4.1, g++ -O3 -DNDEBUG -march=skylake-avx512 (paper Table 2); not stated for the blog's filter_bench numbers |
| **Adoption** | 32.1k stars; Ribbon filter shipped in production RocksDB since v6.15 |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/facebook/rocksdb) · [benchmark](https://arxiv.org/abs/2103.02515) |

## Verdict

arXiv:2103.02515 Table 2 used a 2021 copy of RocksDB's ribbon code in the fastfilter_cpp fork (Xeon D-2191 Skylake DE, GCC 8.4.1 -O3 -march=skylake-avx512, FP rate about 1%). Standard Ribbon w=128 had 6-8% space overhead vs 49.8% for RocksDB's FastLocalBloom, but cost 166 vs 21 ns/key to build and 58 vs 10 ns/key to query at n=10^6, and 235 vs 72 and 140 vs 36 ns/key at n=10^8. The RocksDB blog's filter_bench figures (no hardware stated) are 7 vs 10 bits/key, 140 vs 32 ns/key to construct and 600 vs 500 ns/key to query; no std:: baseline applies.

## Use it when

- RocksDB databases where SST filters stay resident in RAM for a long time (defaults, or cache_index_and_filter_blocks with optimize_filters_for_hits) and filter blocks take a large share of block cache; the blog's example LOG shows 14% of a 9 GB cache.
- Leveled or universal LSMs with long-lived lower levels. Use the hybrid (bloom_before_level=N) so flushes and L0 get Bloom and deeper levels get Ribbon. The blog's cost model puts the break-even at about 1 hour of filter lifetime.
- FP rates around 1-10%. Standard Ribbon w=128 is 6-8% over the information-theoretic minimum there, against about 50% for blocked Bloom.
- Roughly 10K-10M keys per filter, the range r=128 is tuned for. The blog says even 100M keys in one filter save 27% vs Bloom.
- Outside RocksDB: a static key set known up front, when you want portable C++ with fractional bits/key and are willing to vendor util/ribbon_\*.h the way pdillinger/fastfilter_cpp did.

## Skip it when

- Short-lived filters (flush/L0 output, data living under about an hour) or write-bound workloads. Construction costs 3-8x Bloom CPU, and the wiki warns it 'could slow peak write rates in some cases.'
- CPU-bound point lookups on memory-resident data. Paper Table 2 has queries at 58 vs 10 ns/key (n=10^6) and 140 vs 36 ns/key (n=10^8) against RocksDB's FastLocalBloom, and Ribbon queries get relatively costlier at low FP rates.
- Sets that grow after build. Ribbon is static, and RocksDB's memtable filter stays Bloom.
- Compaction hosts that are tight on memory and build huge unpartitioned filters. Construction needs about 230 bits/key of temporary memory vs about 75 for Bloom: 3 GB vs 1 GB for 100M keys in one filter, untracked unless cache charging is enabled.
- Partitioned filters over cold data without optimize_filters_for_hits, where only some filters are resident; the blog says the benefit is 'not as clear' there.

## How it is fast

The win is space, not speed. Ribbon (Rapid Incremental Boolean Banding ON-the-fly) is a perfect-hash static function over GF(2). Each key hashes to a start column and a 128-bit coefficient row, which approximates a band matrix (Dietzfelbinger-Walzer). The system is solved by on-the-fly Gaussian elimination that behaves like linear-probing hash insertion, followed by back-substitution. A query computes the parity of an r-bit window in an 'interleaved' column-major solution that spans 1-3 adjacent cache lines. The XOR construction avoids Bloom's roughly 1.44-1.5x space factor. Splitting between b-1 and b solution columns gives fractional bits/key.

## Compared with alternatives

Pick it over BuRR, which gets below 1% overhead with bumped Ribbon but is research code, and over xor/binary fuse (xor_singleheader: faster queries, about 13-23% overhead, single header), when you already run RocksDB or want a production-hardened C++ Ribbon with Bloom-like fractional bits/key. Choose BuRR for minimum space and xor/binary fuse for the fastest static-filter queries; ribbonGo is the Go option.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (built into RocksDB); standalone use is a source-drop of the templated util/ribbon_alg.h + ribbon_impl.h headers |
| **Dependencies** | Inside RocksDB: RocksDB itself (compression libs and gflags optional). Standalone: a handful of RocksDB support headers (math128.h, fastrange.h, port.h, etc.; the fastfilter_cpp fork ships coding_lean.h, fastrange.h, lang.h, math.h, math128.h, port.h) |
| **Minimum toolchain** | Current RocksDB: C++20, GCC &gt;= 11 or Clang &gt;= 10 (INSTALL.md; CMake defaults to C++20). The Ribbon headers themselves say they are written for C++11, and the 2021 paper copy built with GCC 8.4.1. |
| **Platforms** | Any platform RocksDB supports (Linux, macOS, Windows VS2017+, AIX, BSDs per INSTALL.md). The Ribbon code uses no processor intrinsics, only compiler built-ins for prefetch, clz/ctz and parity, with native 128-bit ints when available and a fallback otherwise. Open issue #14065: an upcoming MSVC flags a potential divide-by-zero (C4723) in ribbon_impl.h, which fails warnings-as-errors builds. |
| **Thread safety** | Managed by RocksDB. Each SST's filter builder has a single owner; only EstimateEntriesAdded() is documented as thread-safe (for parallel compression). Thread safety of the standalone ribbon_\*.h classes is not documented. |
| **Drop-in for the baseline** | partial — inside RocksDB it is a one-line swap of NewBloomFilterPolicy(bpk) for NewRibbonFilterPolicy(bpk) at the same FP rate, and either policy reads both filter kinds (RocksDB &gt;= 6.15). It covers only static SST filters, and as a standalone structure it is not a Bloom replacement: there is no incremental insert and all keys must be known before build. |

## Gotchas

- Default bloom_before_level=0 still writes Bloom filters for memtable flushes under leveled and universal compaction, so savings only appear as compaction rewrites files. Use -1 for all-Ribbon. Since 8.7 the option can be changed at runtime through SetOptions.
- It silently falls back to Bloom, with only an info-log warning, when a filter has more than 950M keys, when a small filter (&lt;1024 slots) would be smaller as Bloom, after 256 failed re-seeds, or when cache charging for the banding memory hits the limit.
- Temporary construction memory is untracked by default. Enable block-cache charging for filter construction (reserve_table_builder_memory in 6.27, now cache_usage_options / CacheEntryRole::kFilterConstruction), or use partitioned filters or smaller SSTs.
- Downgrading to RocksDB &lt; 6.15 reads Ribbon filters as 'no filter' until compaction rebuilds them. RocksJava has only a BloomFilter class and no dedicated Ribbon class.

## Known shortcomings

- Ribbon trades speed for space: 6-8% space overhead vs 49.8% for RocksDB's FastLocalBloom, but build costs 166 vs 21 ns/key and queries 58 vs 10 ns/key (arXiv:2103.02515 Table 2). The blog's 4.4x/20% ratios are derived; the record's 'ESA 2021' venue could not be confirmed.
- Ribbon costs CPU: builds are 3-8x Bloom's and queries 58 vs 10 ns/key at 1e6 keys (140 vs 36 at 1e8); the wiki warns it can slow peak writes. Build temp memory is \~230 vs \~75 bits/key (3 GB vs 1 GB at 100M keys), untracked unless cache charging is on. With the default bloom_before_level=0 flushes stay Bloom, and it silently falls back to Bloom above 950M keys, for tiny filters, after 256 reseeds or at the cache limit.
- Static filters only (the memtable filter stays Bloom); no RocksJava Ribbon class; RocksDB &lt;6.15 reads Ribbon filters as no filter; open MSVC C4723 issue (#14065). The paper's numbers come from a 2021 fastfilter_cpp copy, not the in-database path, and the blog's filter_bench gives no hardware.

## Caveats and trade-offs

Tier A rests on arXiv:2103.02515. The paper has no journal reference on arXiv and no Crossref record, so the earlier claim that it 'appeared at ESA 2021' could not be verified and is dropped. The paper benchmarks a 2021 copy of RocksDB's ribbon_\*.h code (Facebook copyright headers) inside the pdillinger/fastfilter_cpp fork (last pushed 2021-04-27). That is neither RocksDB's in-database filter path nor its current code. The memory win costs CPU: Ribbon construction is 3-8x slower and queries are several times slower than RocksDB's FastLocalBloom (Table 2), so RocksDB recommends a Ribbon+Bloom hybrid policy for long-lived levels. The blog's filter_bench numbers state no hardware or compiler.

Higher construction CPU and \~3x more temporary memory during build (\~230 bits/key vs \~75 for Bloom); relatively worse (more CPU) at low false-positive rates; RocksDB recommends Ribbon only for filters kept in memory beyond roughly an hour

## Maintenance

RocksDB is actively maintained (last push 2026-09-25). The Ribbon code itself is stable: the headers have only had reformat/modernize commits since 2024 and filter_policy.cc last changed in Nov 2025. It has been production-ready since 6.22, its SST schema has been long-term supported since 6.20, and it is dual GPLv2/Apache-2.0, so the headers can be vendored.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. Table 2 of arXiv:2103.02515, by the author of RocksDB Ribbon, benchmarks Standard Ribbon w=128 against RocksDB's own FastLocalBloom and another blocked Bloom filter. The code is public in pdillinger/fastfilter_cpp (dev branch: benchmarks/bulk-insert-and-query.cc, driven by benchmarks/ribbon-benchmark.sh, with src/ribbon/ribbon_impl.h copied from RocksDB). The paper states an Intel Xeon D-2191 (Skylake DE) and GCC 8.4.1 with g++ -O3 -DNDEBUG -march=skylake-avx512. The blog's filter_bench numbers are verified verbatim but give no hardware.
- **Verifier notes:** Blog numbers verified verbatim; the 4.4x and 20% ratios are derived and now marked as such. Tier upgraded to A through the paper's artifact fork, which benchmarks RocksDB's own Ribbon code against RocksDB's FastLocalBloom with full methodology. License verified: GitHub reports GPL-2.0, but the README says the project is dual-licensed GPLv2/Apache 2.0, so the record's 'Apache-2.0 OR GPL-2.0' stands. Other metadata is correct: 32,137 stars, last commit 2026-09-25, active.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://rocksdb.org/blog/2021/12/29/ribbon-filter.html>
  - <https://export.arxiv.org/abs/2103.02515>
  - <https://arxiv.org/pdf/2103.02515>
  - <https://api.crossref.org/works?query.bibliographic=Ribbon+filter+practically+smaller+than+Bloom+and+Xor&rows=5&select=title,container-title,DOI,published,author>
  - <https://github.com/facebook/rocksdb>
  - <https://github.com/facebook/rocksdb/blob/main/util/filter_bench.cc>
  - <https://github.com/facebook/rocksdb/blob/main/util/ribbon_impl.h>
  - <https://github.com/pdillinger/fastfilter_cpp>
  - <https://github.com/pdillinger/fastfilter_cpp/blob/dev/src/ribbon/ribbon_impl.h>
  - <https://github.com/pdillinger/fastfilter_cpp/blob/dev/benchmarks/ribbon-benchmark.sh>
- **Sources the enricher read:**
  - <https://github.com/facebook/rocksdb>
  - <https://github.com/facebook/rocksdb/blob/main/include/rocksdb/filter_policy.h>
  - <https://github.com/facebook/rocksdb/blob/main/include/rocksdb/c.h>
  - <https://github.com/facebook/rocksdb/blob/main/util/ribbon_alg.h>
  - <https://github.com/facebook/rocksdb/blob/main/util/ribbon_impl.h>
  - <https://github.com/facebook/rocksdb/blob/main/util/ribbon_config.h>
  - <https://github.com/facebook/rocksdb/blob/main/util/math128.h>
  - <https://github.com/facebook/rocksdb/blob/main/table/block_based/filter_policy.cc>
  - <https://github.com/facebook/rocksdb/blob/main/microbench/ribbon_bench.cc>
  - <https://github.com/facebook/rocksdb/blob/main/docs/_posts/2021-12-29-ribbon-filter.markdown>
  - <https://github.com/facebook/rocksdb/blob/main/HISTORY.md>
  - <https://github.com/facebook/rocksdb/blob/main/INSTALL.md>
  - <https://github.com/facebook/rocksdb/blob/main/CMakeLists.txt>
  - <https://github.com/facebook/rocksdb/blob/main/java/rocksjni/filter.cc>
  - <https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter>
  - <https://github.com/facebook/rocksdb/issues/14065>
  - <https://github.com/facebook/rocksdb/issues?q=ribbon>
  - <https://arxiv.org/pdf/2103.02515>
  - <https://github.com/pdillinger/fastfilter_cpp/tree/dev>
  - <https://engineering.fb.com/2021/07/09/data-infrastructure/ribbon-filter/>
  - <https://news.ycombinator.com/item?id=27792558>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/facebook/rocksdb`) · [data/wave6/enrich/raw/github_com_facebook_rocksdb.json](../../../data/wave6/enrich/raw/github_com_facebook_rocksdb.json) (enrichment confidence 0.85)

</details>
