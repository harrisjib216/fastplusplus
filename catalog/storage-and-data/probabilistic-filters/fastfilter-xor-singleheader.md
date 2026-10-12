# Xor Filter (xor_singleheader)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Header-only C99 xor and binary fuse filters: static membership filters with fewer bits/key and faster lookups than Bloom/cuckoo.

| | |
|---|---|
| **Beats** | Bloom filter, cuckoo filter |
| **Claimed result** | This record covers both filters in FastFilter/xor_singleheader. (1) Xor filters, JEA 2020 (arXiv 1912.08258, Table 3, 25% of queried keys present): at 10M keys, Xor8 takes 23 ns/query at 9.8 bits/key, against Bloom12 at 40 ns (12.0 bits/key) and Cuckoo12 at 31 ns (12.8 bits/key). Xor16 takes 27 ns (19.7 bits/key), against Bloom16 at 48 ns (16.0 bits/key) and Cuckoo16 at 32 ns (17.0 bits/key). At 100M keys, Xor8 takes 32 ns, against Bloom12 at 58 ns and Cuckoo12 at 38 ns. (2) Binary fuse filters, JEA 2022 (arXiv 2201.01174): the 3-wise filter reaches about 9 bits/key (12.5% above the lower bound) and the 4-wise filter about 8.6 bits/key (7.5% above). Xor uses 9.84 bits/key (23% above) and Bloom at least 44% above. Construction is more than 2x faster than xor filters, and xor and cuckoo construction are both slower. The 3-wise query speed is on par with xor and faster than Bloom filters. The 4-wise query speed is similar to cuckoo filters. The binary fuse figures come only from plots; the paper has no table. |
| **Workload** | Single-threaded membership-query time against space overhead for 10M and 100M random 64-bit keys, with 25% of queried keys present (fastfilter_cpp benchmarks/bulk-insert-and-query.cc). The binary fuse paper adds construction time per key and bits/key across set sizes up to 100M keys. |
| **Metric** | latency |
| **Hardware** | Intel i7-6700 @ 3.4GHz (Skylake) with 8MiB L3, the primary platform in both papers. The binary fuse paper also uses a secondary AMD EPYC 7262 (Zen 2), which has a 25% error margin. |
| **Compiler and flags** | Xor paper: GNU GCC 8.1.0, -O3 -march=native, 64-bit Linux executable. Binary fuse paper: GCC 10, -O3, plus -march=native on x64. |
| **Adoption** | 432 stars; used in production by Databend, ntop nDPI, InfiniFlow, and CockroachDB Pebble |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/FastFilter/xor_singleheader) · [benchmark](https://arxiv.org/abs/1912.08258) |

## Verdict

The xor paper's Table 3 benchmarks the C++ fastfilter_cpp release 1.0 code (GCC 8.1 -O3 -march=native, i7-6700 Skylake, single thread, non-inlined queries, 25% of queried keys present). At 10M keys, Xor8 took 23 ns/query at 9.8 bits/key, against 40 ns for Bloom12 (12 bits/key) and 31 ns for Cuckoo12 (12.8 bits/key); at 100M keys the figures were 32, 58 and 38 ns. The binary fuse paper (GCC 10 -O3, same i7-6700 plus an EPYC 7262) shows, in plots only, that 3-wise fuse reaches about 9 bits/key with xor-level query speed and builds more than 2x faster than xor. Neither paper benchmarked this C header; its own query benchmark prints no Bloom or cuckoo comparison, and the README sample output looks like placeholder numbers.

## Use it when

- The key set is known up front and read-only: SSTable or segment filters in an LSM/columnar store, leaked-password lists, precomputed deny-lists shipped to clients.
- Memory per key matters: binary_fuse8 is about 9 bits/key at 0.39% FPP for sets of 1M keys or more, against 12 bits/key for a Bloom filter at a similar (0.31%) FPP.
- Most queried keys are present: xor and fuse lookups always do exactly three loads, while standard Bloom filters get slower on hits (xor paper Fig. 4).
- You want a dependency-free file to vendor into C or C++ (nDPI and InfiniFlow Infinity embed binaryfusefilter.h), with serialization and mmap-friendly loading.
- You need a very low FPP without a big filter: binary_fuse16 gives about 0.0015% at roughly 18 bits/key.

## Skip it when

- You need inserts, deletes or filter unions: there is no add/remove, and filters built on partitions cannot be OR-ed together the way Bloom filters can (issue #35). Rebuilding needs the full key set.
- Lowest query latency matters more than memory: the blocked Bloom filter was faster in both papers (16 ns vs Xor8's 23 ns at 10M keys) at 10.7 bits/key and about 0.94% FPP.
- Construction memory or time is tight: binary fuse needs about 24 bytes/key of temporary memory (2.4 GB for 100M keys), construction is single-threaded, and at 10M keys xor construction took 110-120 ns/key, against 10 ns for blocked Bloom and 40-90 ns for standard Bloom (xor paper, Table 2). Binary fuse builds more than 2x faster than xor.
- You need the smallest possible filter: this header ships only 3-wise fuse (about 12.5% over the lower bound). The 4-wise variant (7.5%) exists only in C++ fastfilter_cpp (issue #69), and BuRR/ribbon filters go below 1%. For sets under about 20,000 keys, the paper says xor may even beat binary fuse on size.
- You need an FPP below 1/65536 or cross-endian files: there are no 32-bit fingerprints (issues #8 and #75 are open), and serialization is native byte order only.

## How it is fast

Each key maps to three array slots, and construction stores fingerprints so that the XOR of those three slots equals the key's fingerprint. A query is one hash, three independent memory loads and a compare, with the same cost for hits and misses; a Bloom filter needs up to k probes and slows down when most queried keys are present. Construction is hypergraph peeling: slots touched by exactly one key are removed repeatedly, then assigned in reverse order, retrying with a new seed if peeling stalls. Binary fuse filters (spatially coupled, after Dietzfelbinger and Walzer) keep the three slots in consecutive small segments and pre-bucket hashes by segment, which improves cache locality and shrinks the array from about 1.23n to 1.125n slots. Index reduction uses multiply-shift instead of modulo.

## Compared with alternatives

Choose this over BuRR when you want a single dependency-free C99 file and faster lookups: the binary fuse paper measured ribbon queries slower than 3-wise binary fuse. BuRR still wins clearly on space, with overhead under 1% against about 12.5%. Choose it over Prefix Filter when the set is static and you cannot require Intel AVX-512 and C++17, which the Prefix-Filter README mandates; Prefix Filter supports incremental inserts and this library does not.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | C standard library plus libm (binaryfusefilter.h calls log, floor and round; the CMake INTERFACE target links m) |
| **Minimum toolchain** | C99 (CMake c_std_99, Makefile -std=c99). CI uses GCC 13 and Clang 18 on Ubuntu 24.04 and MinGW-w64 GCC on Windows. It uses __uint128_t where available, __umulh on MSVC x64/ARM64, and a portable fallback otherwise. |
| **Platforms** | Any platform with a C99 compiler. CI covers only Linux x86-64 and Windows MinGW 32/64-bit; macOS, ARM and MSVC are not in CI. No SIMD required. |
| **Thread safety** | Not documented. From the source, contain() takes a const pointer and there is no global mutable state, so concurrent lookups on a finished filter look safe. populate() is single-threaded and must not overlap queries on the same filter. |
| **Drop-in for the baseline** | partial: it replaces a Bloom or cuckoo filter only for static sets. You must supply every 64-bit key at build time, and there is no incremental add or delete. |

## Gotchas

- populate() can return false, so always check it. The source comment calls failure rarer than a cosmic ray, but issue #77 showed binary_fuse16_populate failing on 20-40% of distinct key sets at about 11,480-11,521 keys. That was fixed only in v2.2.0 (2026-09-21), so update any vendored copy made before then.
- Deduplicate keys yourself. When populate() sees duplicates, it sorts and deduplicates your array in place. xor8/xor16 first waste 10 failed seeds before trying that. The qsort comparator returns (int)(a - b) on uint64 keys, which is not a consistent ordering, so this fallback cannot be relied on.
- binary_fuse\*_populate() returns false unless the key count equals the size passed to allocate(); despite the 'up to size' comment, that size must be exact. Sizes are uint32_t, so one filter holds under about 4 billion keys.
- Serialization changed format in v2.0.0 (a Size field was added). deserialize() takes no buffer length and trusts ArrayLength from the buffer, so never feed it untrusted bytes. The README's 16-bit example also names binary_fuse8_contain/free where it means the fuse16 functions.

## Known shortcomings

- Paper numbers are for the C++ fastfilter_cpp code, not this header (the papers say so); the repo's own query bench has no Bloom/cuckoo comparison. The header has only 3-wise binary fuse (4-wise, 8.6 bits/key, is C++-only, #69) and no 32-bit fingerprints (#8, #75). fuse16 populate failed on 20-40% of key sets near 11.5k keys until v2.2.0 (2026-09-21, #77), so older vendored copies are affected. The dedup fallback compares u64 keys with an (int)(a-b) qsort comparator and mutates the caller's keys in place; fuse populate needs the exact allocated size; deserialize() has no length check; serialization format changed in v2.0.0 and is native-endian only; \~24 B/key temporary build memory, single-threaded; below \~20k keys xor may be smaller than fuse.
- Packaging note: oschonrock/binfuse wraps this header's binary fuse filters in a C++ library with persistence; its own benchmark reports absolute numbers only.

## Caveats and trade-offs

This record covers both xor filters and binary fuse filters. The repo ships xorfilter.h and binaryfusefilter.h, and the README recommends binary fuse, which is smaller and faster to build than xor. Xor filter is itself a listed baseline in this category, so this entry's claim is measured against Bloom and cuckoo filters. The blocked Bloom filter is faster for queries (16 ns against Xor8's 23 ns at 10M keys) at 10.7 bits/key and about 0.94% false-positive probability. The 2020 paper found xor construction roughly half as fast as Bloom and cuckoo construction, and binary fuse removes most of that cost. The filters are static: no inserts after construction. The paper numbers were measured on the C++ implementations in fastfilter_cpp release 1.0, not on this C header, although the current harness can run the single-header code. All runs are single-threaded on one 2015-era Skylake CPU. The sample query-benchmark output in the README (98.765 ns/q, 0.123456 s) looks like placeholder text, not a measurement.

Immutable once built (no add/remove; must know the full key set upfront); needs a strong \~64-bit hash of the input keys; construction is slower than Bloom/blocked-Bloom (\~110-130ns/key vs \~10-40ns/key at 10M keys per Table 2 of the same paper); naturally compressible with gzip/zstd, unlike Bloom/cuckoo.

## Maintenance

Actively maintained: v2.2.0 shipped 2026-09-21 with a construction-failure fix. It is Apache-2.0 and small enough to vendor, as nDPI and InfiniFlow Infinity do; Pebble and Databend, named in the README, use the Go and Rust ports rather than this header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Table 3 of the JEA 2020 paper matches the record exactly. The paper states GCC 8.1.0 -O3 -march=native on an i7-6700 (Skylake). The benchmark code is public in FastFilter/fastfilter_cpp benchmarks/bulk-insert-and-query.cc, which today also includes Xor8-singleheader and BinaryFuse8-singleheader entries. The binary fuse paper (arXiv 2201.01174) states GCC 10 -O3 -march=native on the same i7-6700 and uses the same harness.
- **Verifier notes:** Tier A confirmed. The JEA 2020 Table 3 numbers match the record exactly. I checked the binary fuse claims in arXiv 2201.01174 and folded them into claimed_speedup and caveats, as the orchestrator asked. Metadata (Apache-2.0, 432 stars, last commit 2026-09-21, active, not a fork) is correct, and the README lists the Databend, nDPI, InfiniFlow and Pebble production users.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/1912.08258>
  - <https://arxiv.org/pdf/1912.08258>
  - <https://arxiv.org/abs/2201.01174>
  - <https://arxiv.org/pdf/2201.01174>
  - <https://github.com/FastFilter/xor_singleheader>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/README.md>
  - <https://github.com/FastFilter/fastfilter_cpp>
  - <https://github.com/FastFilter/fastfilter_cpp/tree/master/benchmarks>
  - <https://github.com/FastFilter/fastfilter_cpp/blob/master/benchmarks/bulk-insert-and-query.cc>
  - <https://github.com/FastFilter/fastfilter_cpp/blob/master/benchmarks/Makefile>
- **Sources the enricher read:**
  - <https://github.com/FastFilter/xor_singleheader>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/README.md>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/include/binaryfusefilter.h>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/include/xorfilter.h>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/CMakeLists.txt>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/Makefile>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/.github/workflows/ubuntu.yml>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/.github/workflows/msys2.yml>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/benchmarks/query.c>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/benchmarks/bench.c>
  - <https://github.com/FastFilter/xor_singleheader/blob/master/tests/unit.c>
  - <https://github.com/FastFilter/xor_singleheader/issues>
  - <https://github.com/FastFilter/xor_singleheader/pulls>
  - <https://github.com/FastFilter/xor_singleheader/tags>
  - <https://github.com/FastFilter/xor_singleheader/issues/77>
  - <https://github.com/FastFilter/xor_singleheader/pull/78>
  - <https://github.com/FastFilter/xor_singleheader/issues/13>
  - <https://github.com/FastFilter/xor_singleheader/issues/25>
  - <https://github.com/FastFilter/xor_singleheader/issues/35>
  - <https://github.com/FastFilter/xor_singleheader/issues/36>
  - <https://github.com/FastFilter/xor_singleheader/issues/38>
  - <https://github.com/FastFilter/xor_singleheader/issues/42>
  - <https://github.com/FastFilter/xor_singleheader/issues/53>
  - <https://github.com/FastFilter/xor_singleheader/issues/63>
  - <https://github.com/FastFilter/xor_singleheader/issues/67>
  - <https://github.com/FastFilter/xor_singleheader/issues/69>
  - <https://github.com/FastFilter/xor_singleheader/issues/70>
  - <https://github.com/FastFilter/xor_singleheader/pull/71>
  - <https://github.com/FastFilter/xor_singleheader/issues/73>
  - <https://github.com/FastFilter/xor_singleheader/issues/76>
  - <https://arxiv.org/pdf/1912.08258>
  - <https://arxiv.org/pdf/2201.01174>
  - <https://github.com/FastFilter/fastfilter_cpp/blob/master/benchmarks/bulk-insert-and-query.cc>
  - <https://github.com/infiniflow/infinity/blob/main/src/storage/fast_rough_filter/binary_fuse_filter.cppm>
  - https://github.com/ntop/nDPI (code search: binaryfusefilter.h, src/lib/ndpi_bitmap64_fuse.c)
  - <https://github.com/cockroachdb/pebble/blob/master/go.mod>
  - <https://github.com/databendlabs/databend/blob/main/src/query/storages/common/index/Cargo.toml>
  - <https://hn.algolia.com/api/v1/search?query=binary%20fuse%20filters&tags=story>
  - <https://news.ycombinator.com/item?id=46658128>
  - <https://news.ycombinator.com/item?id=44669318>
  - <https://github.com/TomerEven/Prefix-Filter>
  - <https://github.com/lorenzhs/BuRR>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/fastfilter/xor_singleheader`) · [data/wave6/enrich/raw/github_com_fastfilter_xor_singleheader.json](../../../data/wave6/enrich/raw/github_com_fastfilter_xor_singleheader.json) (enrichment confidence 0.87)

</details>
