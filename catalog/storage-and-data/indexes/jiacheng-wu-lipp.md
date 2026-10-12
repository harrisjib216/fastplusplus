# LIPP (Updatable Learned Index with Precise Positions)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only, single-threaded learned index for numeric keys; beats STX B+Tree, ART and ALEX on point-lookup and insert throughput.

| | |
|---|---|
| **Beats** | STX B+Tree; also beats Adaptive Radix Tree (ART), ALEX, PGM-index, BwTree, and a 2-level RMI ("Learned Index") |
| **Claimed result** | Up to 2.8x/6.3x/15.3x/9.8x throughput vs ALEX/PGM/Learned-Index/B+Tree on read-only workloads; 2.9x/13.5x/5.4x/3.7x vs ALEX/PGM/B+Tree/ART on read-write workloads |
| **Workload** | Point lookups/inserts on four datasets (Longitudes 1B, Longlat 200M, Lognormal 190M, YCSB 200M keys) under Read-Only, Read-Heavy, Write-Heavy, Write-Only workloads, single-threaded |
| **Metric** | throughput |
| **Hardware** | Intel Core i7 (4 cores, 8 threads) @ 4.0GHz, 32GB RAM, Ubuntu 18.04, single thread used |
| **Compiler and flags** | GCC 9.0.1, -O3 |
| **Adoption** | 63 stars |
| **Last commit** | 2022-02-07 |
| **Links** | [repository](https://github.com/Jiacheng-WU/lipp) · [benchmark](http://www.vldb.org/pvldb/vol14/p1276-wu.pdf) |

## Verdict

The PVLDB 14(8) 2021 paper ran single-threaded on an unnamed 4.0 GHz Intel Core i7 (4C/8T, 32 GB) with GCC 9.0.1 -O3 on four datasets (Longitudes 1B doubles, Longlat 200M, Lognormal 190M, YCSB 200M int64), and its harness was never published. It reports up to 9.8x STX B+Tree throughput read-only (100M-key bulk-loaded index, lookups of existing keys only) and up to 5.4x on insert/lookup mixes from an empty index, but only 1.47x over ALEX on Longlat, while the independent GRE study (Xeon Platinum 8268, gcc 8.3 -O3) also ranks LIPP and ALEX the top single-threaded indexes, with LIPP slightly below the paper's numbers after its bug fixes and using 4-5x ALEX's memory.

## Use it when

- Single-threaded, lookup-heavy point queries on 64-bit integer or double keys that mostly exist in the index. The paper reports up to 9.8x STX B+Tree throughput read-only, but it only looked up keys that were present.
- Mixed insert/lookup streams (33-67% inserts) with unique keys and a single writer. The paper reports up to 5.4x STX B+Tree and 3.7x ART, and the GRE study also ranks LIPP among the top single-threaded indexes on easy real datasets.
- Machines where index memory is cheap relative to the data: plan for roughly 4-5x ALEX's footprint, plus a large fixed pool allocated at construction.
- As a compact (\~880-line, MIT) starting point or baseline for research on exact-position learned indexes.

## Skip it when

- Any multi-threaded access. There is no concurrency control, and GRE's concurrent rewrite (LIPP+, item-level optimistic locks) stopped scaling once writes were involved, because every insert updates per-node statistics all the way up to the root.
- Memory-constrained deployments. GRE measured LIPP's memory at 4-5x ALEX's, the highest of all indexes it tested, and ALEX tuned to use the same memory beat LIPP on lookups. In issue #1, bulk-loading 200M SOSD keys ran out of memory on a 32 GB machine where ALEX, STX B+Tree and Dynamic PGM fit.
- Workloads that need erase, upsert, ordered iteration or range scans: main has none of them. Even on the range branch the paper reports at most 1.5x on scans, and GRE found the mixed data/child node layout branch-heavy for scans.
- String or composite keys, possible duplicate keys, or untrusted input: keys must be arithmetic, and inserting an existing key kills the process.
- Hard, highly non-uniform key distributions or tail-latency-sensitive writes. The gain over ALEX falls to 1.47x on Longlat. GRE saw high p99.9 insert latency on its osm and genome datasets and found learned indexes losing to traditional ones on hard data with 50% or more writes.

## How it is fast

Each node holds a linear model and a sparse slot array whose predicted slot is exact, so each level of a lookup costs one model evaluation plus a bitmap check, with none of the last-mile binary or exponential search that ALEX, PGM and RMI need. When two keys land on the same slot, LIPP swaps the entry for a pointer to a new small child node ('node chaining') instead of shifting elements. The FMCD (Fastest Minimum Conflict Degree) algorithm picks each node's model in linear time to keep conflicts rare. A subtree is rebuilt with FMCD once it has grown 4x since its last build and conflicts reach 10% of its inserts, which bounds tree height at an amortized O(log^2 N) insert cost; two-key nodes are recycled through a preallocated pool.

## Compared with alternatives

Pick LIPP over ALEX only for single-threaded, point-lookup-heavy work on numeric keys when memory is plentiful and you can do without erase and range scans. ALEX uses 4-5x less memory, beats LIPP on lookups when given the same memory, and has a scalable concurrent variant (ALEX+ in GRE). Prefer PGM-index for static or space-critical data, or insert-only streams (its LSM-style inserts were the fastest at 100% writes in GRE), and rafaelkallis ART for non-numeric keys.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library only; src/core/lipp.h + lipp_base.h) |
| **Minimum toolchain** | C++11 per CMakeLists, using GCC/Clang extensions (__builtin_ctz, compound literals). The range branch and the GRE fork need C++17 (if constexpr). Tested with GCC 9.0.1 (paper) and gcc 8.3.0 (GRE). |
| **Platforms** | Only x86-64 Linux is tested. The GCC/Clang builtins mean MSVC is not supported as written. The 64-bit-key precision fix relies on long double being wider than double. |
| **Thread safety** | Not thread-safe and there is no locking. Even readers alongside a single writer are unsafe, because insert rebuilds and frees subtrees in place. The paper only sketches latch coupling as a future design. |
| **Drop-in for the baseline** | false — the API is only insert/at/exists/bulk_load, with no iterators, erase, lower_bound or allocator parameter, so replacing STX B+Tree or a std::map-style container needs a wrapper and loses ordered access |

## Gotchas

- Every internal failure goes through RT_ASSERT, which prints to stderr and then calls exit(0). The triggers are: inserting a key that already exists (insert is not an upsert, issue #8), unsorted or duplicate bulk_load input, a model parameter going non-finite, and an insert path deeper than MAX_DEPTH=128. Each one ends the process with a success exit code.
- at(key) defaults to skip_existence_check=true and, for a missing key, returns whatever the predicted slot holds (garbage). Call exists() first. Passing false does not help, because a miss then triggers RT_ASSERT and exit(0).
- The constructor eagerly builds and pools 10 million two-key nodes, so even an empty LIPP is slow to construct and holds a lot of heap. From the struct layout I estimate about 1.6 GB for int/int up to about 2.3 GB for 64-bit key/value, before malloc overhead. Issue #14 (./example killed) may be this, but it was never diagnosed.
- Precision and depth edge cases. Models convert keys to long double; PR #11 (from the GRE authors) fixed segfaults and non-finite-model asserts on SOSD 64-bit datasets (issues #2, #10), and it may not hold where long double is only 64-bit, which is untested. Nodes built from more than 1e6 keys are marked fixed and never rebuilt. Inserting 100M sequential ints into an empty index hit MAX_DEPTH (issue #13); the maintainer's fix is to raise the constant by hand.

## Known shortcomings

- No CPU model ('i7 4.0GHz') and no public harness against the baselines (repo is core + examples); the GRE benchmark (VLDB'22) found 2 bugs whose fixes slightly lower performance (verifier downgrade from A).
- Single-threaded; in GRE the concurrent LIPP+ stops scaling once writes appear. Memory is 4-5x ALEX's (highest in GRE), and ALEX given the same memory wins lookups.
- The main branch has no erase/update/range scan (only on the range branch or GRE's fork). RT_ASSERT calls exit(0), so a duplicate insert, unsorted bulk_load, NaN model or depth &gt;128 kills the process with a success code; at() on a missing key returns garbage. The constructor pre-pools \~1e7 nodes (\~1.6-2.3 GB, estimated from struct layout); paper harness unpublished.

## Caveats and trade-offs

Single-threaded benchmarks only. Gains vary strongly by dataset: as low as 1.47x vs ALEX on the highly non-uniform Longlat dataset. The paper names no CPU model (only '4.0 GHz Intel Core i7') and its benchmark harness against the baselines is not public; the repo ships only the core header and examples. The GRE study (PVLDB 15(11) 2022) found and fixed two bugs in LIPP (merged as PRs #11/#12). It reports that the fixes gave slightly lower performance than the LIPP paper reported, and that LIPP's unified node design scales poorly with multiple threads. Repo unmaintained since Feb 2022.

No concurrency support; amortized O(log^2 N) insert cost vs B+Tree's better worst case; needs periodic subtree adjustment; benefit shrinks a lot on highly non-uniform key distributions

## Maintenance

Abandoned since the Feb 2022 commit that merged the GRE bug fixes (in issue #3 the authors said they had moved to other work, though they still answered an issue in 2025), but it is MIT-licensed and a single \~880-line header that is easy to vendor, and for remove/update/range scans the GRE fork pohchaichon/lipp@a1189c3 is the better copy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** The PVLDB 14(8) 2021 paper is peer-reviewed. Section 6.2 compares LIPP with STX B+Tree, ART, ALEX, PGM, Learned Index and BwTree, and it states GCC 9.0.1 at O3. It does not reach A: the CPU is given only as a '4.0 GHz Intel Core i7 (4 cores and 8 threads)' with no model number, and the comparison harness was never published (the repo holds only src/core and src/examples).
- **Verifier notes:** The numbers match Sections 6.2.1 and 6.2.2 exactly: 2.8x/6.3x/15.3x/9.8x read-only and 2.9x/13.5x/5.4x/3.7x read-write, plus the 1.47x Longlat figure. The metadata checks out: MIT, 63 stars, last commit 2022-02-07, not a fork. An independent third-party suite, GRE (github.com/gre4index/GRE, src/benchmark/microbench.cpp vs src/competitor/btree/btree.h = STX), states gcc 8.3.0 -O3 on a Xeon Platinum 8268 and shows LIPP/ALEX beating traditional indexes single-threaded. Its heatmap gives no numeric ratios, though, so I did not use it to keep tier A; enrichment could pull numbers from GRE runs.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <http://www.vldb.org/pvldb/vol14/p1276-wu.pdf>
  - <https://github.com/Jiacheng-WU/lipp>
  - <https://www.vldb.org/pvldb/vol15/p3004-wongkham.pdf>
  - <https://github.com/gre4index/GRE>
- **Sources the enricher read:**
  - <https://github.com/Jiacheng-WU/lipp>
  - <https://github.com/Jiacheng-WU/lipp/blob/main/README.md>
  - <https://github.com/Jiacheng-WU/lipp/blob/main/src/core/lipp.h>
  - <https://github.com/Jiacheng-WU/lipp/blob/main/src/core/lipp_base.h>
  - <https://github.com/Jiacheng-WU/lipp/blob/main/CMakeLists.txt>
  - <https://github.com/Jiacheng-WU/lipp/blob/main/src/examples/example.cpp>
  - <https://github.com/Jiacheng-WU/lipp/blob/main/src/examples/example_bulk_load.cpp>
  - <https://github.com/Jiacheng-WU/lipp/blob/main/src/examples/example_without_fmcd.cpp>
  - <https://github.com/Jiacheng-WU/lipp/issues?q=is%3Aissue>
  - <https://github.com/Jiacheng-WU/lipp/issues/1>
  - <https://github.com/Jiacheng-WU/lipp/issues/2>
  - <https://github.com/Jiacheng-WU/lipp/issues/3>
  - <https://github.com/Jiacheng-WU/lipp/issues/4>
  - <https://github.com/Jiacheng-WU/lipp/issues/5>
  - <https://github.com/Jiacheng-WU/lipp/issues/8>
  - <https://github.com/Jiacheng-WU/lipp/issues/9>
  - <https://github.com/Jiacheng-WU/lipp/issues/10>
  - <https://github.com/Jiacheng-WU/lipp/issues/13>
  - <https://github.com/Jiacheng-WU/lipp/issues/14>
  - <https://github.com/Jiacheng-WU/lipp/pull/11>
  - <https://github.com/Jiacheng-WU/lipp/pull/12>
  - <https://github.com/Jiacheng-WU/lipp/commits/main>
  - <https://github.com/Jiacheng-WU/lipp/compare/main...range>
  - <https://github.com/Jiacheng-WU/lipp/compare/main...develop>
  - <https://github.com/Jiacheng-WU/lipp/blob/range/src/core/lipp.h>
  - <https://github.com/Jiacheng-WU/lipp/blob/range/src/range.cpp>
  - <http://www.vldb.org/pvldb/vol14/p1276-wu.pdf>
  - <https://www.vldb.org/pvldb/vol15/p3004-wongkham.pdf>
  - <https://github.com/gre4index/GRE>
  - <https://github.com/gre4index/GRE/blob/master/src/competitor/lipp/lipp.h>
  - <https://github.com/pohchaichon/lipp/tree/a1189c3956ebfef1335d252f8e13b91eb99fe8cf>
  - <https://github.com/pohchaichon/lipp/blob/a1189c3956ebfef1335d252f8e13b91eb99fe8cf/src/core/lipp.h>
  - <https://hn.algolia.com/api/v1/search?query=%22Updatable%20Learned%20Index%20with%20Precise%20Positions%22>
  - <https://hn.algolia.com/api/v1/search?query=LIPP%20learned%20index>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/jiacheng-wu/lipp`) · [data/wave6/enrich/raw/github_com_jiacheng_wu_lipp.json](../../../data/wave6/enrich/raw/github_com_jiacheng_wu_lipp.json) (enrichment confidence 0.85)

</details>
