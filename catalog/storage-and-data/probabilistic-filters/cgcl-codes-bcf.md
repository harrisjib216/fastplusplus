# Better Choice Cuckoo Filter (BCF)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Research patch to efficient/cuckoofilter: inserts go to the less-loaded bucket, claiming 35% fewer relocations, 25% lower insert latency.

| | |
|---|---|
| **Beats** | Cuckoo filter |
| **Claimed result** | 35% fewer average relocations and 25% lower item-insertion latency vs standard Cuckoo Filter |
| **Workload** | Insert 1,048,576 items (12-bit fingerprints) using power-of-two-choices bucket selection, comparing average relocation count and insertion latency against the standard Cuckoo Filter (efficient/cuckoofilter design). |
| **Metric** | latency |
| **Hardware** | Intel Xeon E5-2670 0 @ 2.60GHz, Red Hat Enterprise Linux Server 6.2 |
| **Adoption** | 12 stars |
| **Last commit** | 2019-06-22 |
| **Links** | [repository](https://github.com/CGCL-codes/BCF) · [benchmark](https://github.com/CGCL-codes/BCF#overview) |

## Verdict

The only published numbers are in the abstract of the paywalled ICDCS 2019 paper: 35% fewer average relocations and 25% lower average insertion latency than the standard cuckoo filter on large real-world data sets. The README repeats them and names an Intel Xeon E5-2670 @ 2.60GHz on RHEL 6.2, but gives no compiler, flags, absolute timings or baseline configuration. The repo has no BCF-vs-CF harness. example/test.cc only times windows of about 100 BCF inserts at each \~1% load step of a 2^20-slot, 12-bit table. It uses gettimeofday, calls Contain() before every Add, sleeps 1 s between windows, and is built at -g by default.

## Use it when

- You already vendor efficient/cuckoofilter with SingleTable and want a roughly 10-line change to Add() that cuts relocations when tables run near full. The repo's own test fills a 2^20-slot table until inserts fail.
- Insert latency at high load factor is the pain point, and the lookup path and memory layout must stay exactly the same as upstream's (same 12-bit, 4-way bucket format and the same two-probe Contain).
- Filters are sized with little or no headroom. BCF removed upstream's rule that doubles the bucket count, so the table has about as many slots as the requested capacity, and that is the regime where fewer relocations matter.
- Research or teaching: reproducing the ICDCS 2019 power-of-two-choices result. An IPv4 trace (input/ip_final.txt, addresses as decimal integers) and the relocation-logging example are included.

## Skip it when

- Any use that must never give a false negative. After 1,000 kicks, AddImpl returns InsertFail even though it has already evicted a stored fingerprint. The victim-cache code upstream uses to keep that fingerprint is now unreachable, so an item inserted earlier can silently disappear.
- Production or memory-safety-sensitive code. SingleTable predates upstream's November 2017 padding fix (efficient/cuckoofilter PR #27, 'avoid buffer overrun'), so the unaligned 64-bit bucket reads run past the end of the allocation at the last bucket. The constructor also lacks upstream's num_buckets &gt;= 1 guard.
- Concurrent inserts, even into separate filter objects. Every successful Add writes process-wide globals (NumberOfBuckets_0..4 and NumberOfRelocations), and there is no locking.
- Semi-sorted filters (PackedTable). BCF's Add() calls NumTagsInBucket, which is commented out in packedtable.h, so CuckooFilter&lt;..., PackedTable&gt; no longer compiles once Add is used.
- Low-load or read-heavy filters. Every insert now scans both buckets (8 tag reads) and recounts the destination bucket for statistics, even when the first bucket has room. The claimed gain comes only from avoiding relocations at high load.

## How it is fast

Upstream puts the fingerprint in the first candidate bucket i1 and only moves to i2, then to random-walk eviction, when i1 is full. BCF's Add() first counts the occupied slots in both candidate buckets and inserts into the emptier one, with ties going to i1. This is the 'power of two choices' (balanced allocation) principle. Bucket occupancy stays more even, so at high load fewer inserts find both buckets full, which means fewer cuckoo kick-out chains and lower insert latency. Lookups and deletes are unchanged upstream code: two bucket probes with SWAR tag matching (the haszero/hasvalue12 bit tricks) on 64-bit loads.

## Compared with alternatives

Pick BCF only when you are patching an existing efficient/cuckoofilter deployment (the Cuckoo Filter sibling) and need its exact layout and query path with fewer relocations near full load. Better port the balanced-choice rule than vendor this snapshot. For new code, Morton Filter (1.3-2.5x faster lookups than the reference cuckoo filter), Vacuum Filter (about 25% less space at similar throughput) or Prefix Filter (more than 3.2x faster builds than any cuckoo configuration) are better evidenced.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenSSL (hashutil.cc wraps EVP MD5/SHA1, and the Makefile links -lssl -lcrypto). The Makefile also passes -lpthread. |
| **Minimum toolchain** | C++11 (Makefile --std=c++11, CMake CXX_STANDARD 11). Needs GCC or Clang on a 64-bit target, because the default hash uses unsigned __int128 and the buckets use __attribute__((packed)). |
| **Platforms** | x86-64 little-endian as written. singletable.h includes &lt;xmmintrin.h&gt;, and the tag code relies on unaligned little-endian 64-bit loads ('only works for little-endian' comments). Developed on RHEL 6.2 with a Xeon E5-2670. |
| **Thread safety** | Not documented, and not thread-safe: there is no internal locking, and Add() mutates process-global counters, so inserts race even across different filter instances. |
| **Drop-in for the baseline** | partial — it keeps the class name, template parameters and Add/Contain/Delete API of efficient/cuckoofilter with SingleTable. However, you must define six extern size_t globals. The constructor no longer doubles buckets when load would exceed 96%, kMaxCuckooCount is 1000 instead of 500, failed inserts return InsertFail and drop an evicted fingerprint instead of parking it in the victim cache, and PackedTable is broken. |

## Gotchas

- It does not link out of the box. cuckoofilter.h declares extern NumberOfBuckets_0..4 and NumberOfRelocations, and only example/test.cc defines them. The unchanged upstream benchmarks/ files (bulk-insert-and-query, conext-\*) call Add() without defining them.
- The README says the example reads ./input/ip_final.txt, but example/test.cc opens ./ip_final.txt, so ./test run from the repo root prints 'Error opening file'. The Makefile also defaults to OPT = -g -ggdb with -O3 -DNDEBUG commented out, so turn on optimization before timing anything.
- The README lists NumTagsInBucket() as a filter operation, but it is a method of the private table_ and CuckooFilter does not expose it. The worst-case kick chain before failure is twice upstream's (1000 vs 500).
- A checkout brings seventeen 40 MB .vscode/ipch IntelliSense caches (about 690 MB), a CLion cmake-build-debug directory and prebuilt benchmark .exe files. Copy src/ rather than adding the repo as a submodule.

## Known shortcomings

- A modified copy of efficient/cuckoofilter; the Makefile's default is a debug build; gains are fewer relocations/lower insert latency vs the standard cuckoo filter.
- A copy of early-2017 efficient/cuckoofilter whose only change is that Add() picks the less-loaded bucket. False-negative bug: after 1000 kicks InsertFail drops an evicted fingerprint and the victim cache is unreachable. Misses upstream's padding fix (PR #27), so a 64-bit read overruns the last bucket; no num_buckets&gt;=1 guard. Six extern global counters break linking (benchmarks/ will not link) and are not thread-safe even across instances; PackedTable is broken.
- No BCF-vs-CF harness in the repo and the paper is paywalled (abstract only); the Makefile defaults to -g; the README's data path differs from test.cc. The checkout includes \~690 MB of .vscode/ipch junk; abandoned since 2019.

## Caveats and trade-offs

The code is a modified copy of efficient/cuckoofilter, not a GitHub fork: same src/ files, CMake project named cuckoofilter_master, and the upstream conext benchmarks. The repo's LICENSE file is upstream's Apache-2.0 notice (Copyright 2013 CMU and Intel), which GitHub reports as NOASSERTION. The README adds a 2019 HUST copyright line but no other license. The evidence is the paper: Wang, Chen, Liao, Zhang, Jin, 'The Power of Better Choice: Reducing Relocations in Cuckoo Filter', ICDCS 2019, https://doi.org/10.1109/ICDCS.2019.00043, which is paywalled. The repo's example/test.cc only times BCF insertion of an IP-trace dataset (ip_final.txt, 1,048,576 items, 12-bit fingerprints) with gettimeofday and sleep calls. The Makefile's default OPT is '-g -ggdb', with -O3 -DNDEBUG commented out, and it is unknown which flags the paper used.

Only changes the insertion-time bucket-selection rule (pick the less-loaded of the two candidate buckets); lookup/delete paths are unchanged from a standard Cuckoo Filter, so read performance is unaffected while write performance and load factor improve.

## Maintenance

Abandoned: three commits in May-June 2019, no issues or PRs ever, 12 stars. Apache-2.0 via upstream's CMU/Intel LICENSE (GitHub shows NOASSERTION). The idea is about 10 lines in Add(), so porting it onto current efficient/cuckoofilter is safer than vendoring this pre-2017-fix snapshot.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The README states the 35% reduction in relocations and 25% reduction in insertion latency against the standard Cuckoo Filter. The same figures are in the abstract of the peer-reviewed paper (ICDCS 2019, DOI 10.1109/ICDCS.2019.00043, pp. 358-367). The full paper is behind the IEEE paywall, and the repo gives no compiler or flags, so the entry cannot be A.
- **Verifier notes:** The record wrongly said the repo has no LICENSE file. It has upstream's Apache-2.0 notice, so the license is Apache-2.0 and usability is copyable. The paper abstract (via Semantic Scholar) confirms the 35% and 25% figures. doi.org redirects to IEEE Xplore, where the full text is paywalled. The default Makefile builds a debug binary, so an optimized build is not guaranteed; the Tier B rating rests on the paper alone.
- **Fields the verifier corrected:** `license`, `usability`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/CGCL-codes/BCF>
  - <https://github.com/CGCL-codes/BCF#overview>
  - <https://github.com/CGCL-codes/BCF/blob/master/LICENSE>
  - <https://github.com/CGCL-codes/BCF/blob/master/Makefile>
  - <https://github.com/CGCL-codes/BCF/blob/master/CMakeLists.txt>
  - <https://github.com/CGCL-codes/BCF/blob/master/example/test.cc>
  - <https://github.com/efficient/cuckoofilter>
  - <https://api.crossref.org/works/10.1109/icdcs.2019.00043>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/ICDCS.2019.00043>
  - <https://doi.org/10.1109/ICDCS.2019.00043>
- **Sources the enricher read:**
  - <https://github.com/CGCL-codes/BCF>
  - <https://github.com/CGCL-codes/BCF#overview>
  - <https://github.com/CGCL-codes/BCF/blob/master/src/cuckoofilter.h>
  - <https://github.com/CGCL-codes/BCF/blob/master/src/singletable.h>
  - <https://github.com/CGCL-codes/BCF/blob/master/src/packedtable.h>
  - <https://github.com/CGCL-codes/BCF/blob/master/src/bitsutil.h>
  - <https://github.com/CGCL-codes/BCF/blob/master/src/hashutil.h>
  - <https://github.com/CGCL-codes/BCF/blob/master/src/hashutil.cc>
  - <https://github.com/CGCL-codes/BCF/blob/master/example/test.cc>
  - <https://github.com/CGCL-codes/BCF/blob/master/Makefile>
  - <https://github.com/CGCL-codes/BCF/blob/master/CMakeLists.txt>
  - <https://github.com/CGCL-codes/BCF/blob/master/LICENSE>
  - <https://github.com/CGCL-codes/BCF/blob/master/.gitignore>
  - <https://github.com/CGCL-codes/BCF/blob/master/benchmarks/bulk-insert-and-query.cc>
  - <https://github.com/CGCL-codes/BCF/blob/master/benchmarks/conext-table3.cc>
  - <https://github.com/CGCL-codes/BCF/blob/master/benchmarks/Makefile>
  - <https://raw.githubusercontent.com/CGCL-codes/BCF/master/input/ip_final.txt>
  - <https://github.com/CGCL-codes/BCF/commits/master>
  - <https://github.com/CGCL-codes/BCF/issues>
  - <https://github.com/CGCL-codes/BCF/forks>
  - <https://github.com/efficient/cuckoofilter>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/cuckoofilter.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/singletable.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/packedtable.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/bitsutil.h>
  - <https://github.com/efficient/cuckoofilter/blob/master/src/hashutil.cc>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/bulk-insert-and-query.cc>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/conext-table3.cc>
  - <https://github.com/efficient/cuckoofilter/blob/master/benchmarks/Makefile>
  - <https://github.com/efficient/cuckoofilter/commits/master/src/singletable.h>
  - <https://github.com/efficient/cuckoofilter/commits/master/src/cuckoofilter.h>
  - <https://github.com/efficient/cuckoofilter/pull/27>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/ICDCS.2019.00043>
  - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/ICDCS.2019.00043/citations>
  - <https://api.crossref.org/works/10.1109/icdcs.2019.00043>
  - <http://export.arxiv.org/api/query?id_list=2608.13970>
  - <https://arxiv.org/abs/2608.13970>
  - <https://arxiv.org/pdf/2608.13970>
  - <http://grid.hust.edu.cn/hhchen/>
  - <http://faculty.hust.edu.cn/chenhanhua/en/index.htm>
  - <https://hn.algolia.com/api/v1/search?query=%22better%20choice%20cuckoo%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cgcl-codes/bcf`) · [data/wave6/enrich/raw/github_com_cgcl_codes_bcf.json](../../../data/wave6/enrich/raw/github_com_cgcl_codes_bcf.json) (enrichment confidence 0.82)

</details>
