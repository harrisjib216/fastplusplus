# DPTree (Differential Indexing for Persistent Memory)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Research persistent-memory index that buffers writes in DRAM; up to 1.82x faster point lookups than FAST+FAIR on Optane.

| | |
|---|---|
| **Beats** | FAST+FAIR (also FPTree, WORT) |
| **Claimed result** | Single-thread micro-benchmark (25M-100M random 64-bit keys). Point lookups: up to 1.82x/1.85x/2.19x faster than FAST+FAIR/FPTree/WORT. Inserts: 1.27-1.43x lower latency than FAST+FAIR and 1.76-1.78x lower than FPTree. Range scans: up to 3.0x/10.98x faster than FPTree/WORT but up to 1.1x slower than FAST+FAIR. Concurrent YCSB (50M keys, up to 32 threads). InsertOnly: up to 1.36x higher throughput than FAST+FAIR at 32 threads. ReadOnly: 1.32-1.58x (vs FAST+FAIR) and 1.37-1.7x (vs FPTree) higher throughput. ReadUpdate: highest throughput at all thread counts, up to 1.7-5.07x over the other indexes. ScanInsert: FAST+FAIR keeps the highest scan throughput. |
| **Workload** | Single-thread micro-benchmark: 64-bit random integer keys, 16-byte key-value pairs, 25M-100M keys; insert latency, point lookup, and range scan at 0.001%-0.1% selectivity. Concurrent YCSB-style workloads on 50M keys: InsertOnly, ReadOnly, ReadUpdate (50/50), ScanInsert (95% scans/5% inserts) and Mixed, up to 32 threads on one socket, on real Intel Optane DC PMM. |
| **Metric** | throughput |
| **Hardware** | Two Intel Xeon Platinum 8263C @ 2.50GHz (26 physical cores), 35MB LLC, 376GB DRAM, 512GB Intel Optane DC PMM in App Direct mode via ext4-DAX, Linux kernel 4.9. All threads bound to one socket. |
| **Compiler and flags** | g++ 6.4 with -O3 (paper section 4.1) |
| **Adoption** | 61 stars; published as PVLDB 13(4):421-434 (Dec 2019, DOI 10.14778/3372716.3372717; presented at VLDB 2020) |
| **Last commit** | 2021-07-28 |
| **Links** | [repository](https://github.com/zxjcarrot/DPTree-code) · [benchmark](http://www.vldb.org/pvldb/vol13/p421-zhou.pdf) |

## Verdict

These numbers come from the authors' own PVLDB 13(4) paper: 2x Xeon Platinum 8263C with 512 GB Optane DC PMM (App Direct, ext4-DAX), g++ 6.4 -O3, threads pinned to one socket. With 25M-100M random 64-bit keys and 16-byte entries, single-threaded DPTree had 1.27-1.43x lower insert latency and up to 1.82x faster point lookups than FAST+FAIR, while scans were up to 1.1x slower. At 50M keys and up to 32 threads it reached up to 1.36x InsertOnly and 1.32-1.58x ReadOnly throughput over FAST+FAIR. FPTree was the authors' own reimplementation, the baseline harness is not public, and no stdlib comparison was made.

## Use it when

- Research or prototyping on Intel Optane DC PMem (App Direct / DAX) when you need a strong buffered-index baseline to compare against FAST+FAIR, FPTree or WORT.
- Workloads dominated by point lookups, or by 50/50 read-update, on uniformly random 64-bit integer keys with 8-byte values. The paper shows 1.32-1.58x ReadOnly throughput over FAST+FAIR and 1.7-5.07x on ReadUpdate at 50M keys.
- Insert-heavy workloads where the limit is PM write bandwidth or endurance rather than CPU: DPTree issues the fewest flushes and fences per insert of the indexes the paper measured.
- As a readable, MIT-licensed reference for buffered/differential PM indexing (in-place merge, coarse-grained versioning, partitioned PM log) that you port into your own engine.

## Skip it when

- Anything that needs real crash recovery. The public code has no recovery routine (issue #4, open since 2021 with no reply). It allocates its 'PM' with posix_memalign in ordinary DRAM and has no PM pool or allocator. The paper's validity-bit log, restart counters and pending-leaf list are also missing.
- Scan-heavy workloads: scans are up to 1.1x slower than FAST+FAIR single-threaded, FAST+FAIR keeps the highest scan throughput in ScanInsert, and DPTree's scan throughput levels off after about 20 threads.
- Keys that are not uint64: the code hard-codes 8-byte big-endian conversion (__builtin_bswap64). Issue #3 reports very low throughput and segfaults with double keys, and there is no string or variable-length key support.
- Workloads with deletes under concurrency: concur_dptree exposes no erase, and the APEX authors likewise report that DPTree's code does not support delete, recovery or double keys.
- Memory-constrained deployments or non-Optane hardware: 1.7 GB versus 1.26 GB for FAST+FAIR after 50M inserts (about 34% more, from the two metadata copies). Optane is discontinued, so the claimed advantage has no current target hardware.

## How it is fast

It spreads the cost of persistence over a batch of writes: each write costs one cache-line log append (clwb+sfence) plus a DRAM insert. The batch is then merged into PM leaves in place using coarse-grained versioning. Each leaf keeps two metadata copies, and one persisted global-version flip makes a whole merge visible, so the flushes inside the merge need no fences. That comes to 2.26 flushes per insert, against 4.35 for FAST+FAIR and 3.64 for FPTree (paper Table 1). Base-tree leaves are 256-slot hash tables using linear probing plus 1-byte fingerprints, with an order array for sorted scans. A lookup is usually a bloom-filter check on the buffer plus about 2 PM accesses. The concurrent version adds a hash-partitioned PM log with lock-free fetch-and-add appends, an Optimistic Lock Coupling (OLC) B+-tree buffer, RCU-style thread-local epoch words and a parallel background merge.

## Compared with alternatives

APEX is the only persistent-memory sibling. The APEX paper measured it beating DPTree (inserts up to 1.66x, lookups up to 3.2x, scans up to 1.83x), and APEX supports recovery, deletes and double keys, so default to APEX. Pick DPTree only if you want a non-learned design that does not depend on the key distribution (on the hard-to-fit FB dataset APEX's insert throughput was 42% below DPTree's) or you are studying buffered in-place PM merging. The DRAM-only siblings (ALEX, LIPP, HOT, ART) provide no persistence.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | stx-btree (headers), Intel TBB (used by the bundled ARTOLC epoch code), tcmalloc_minimal, pthreads; you must also compile the bundled src/\*.cpp, src/bloom.c and misc/ARTOLC/\*.cpp. The paper's PM allocator (nvm_malloc) is not included. |
| **Minimum toolchain** | C++11 with GCC (paper used g++ 6.4; CMake sets CMAKE_CXX_STANDARD 11 and -fpermissive); CMake 2.8+; README targets Ubuntu 18.04. The CMake default build type is RelWithDebInfo, not the paper's -O3. |
| **Platforms** | Linux x86-64 only. It needs CLWB (Skylake-SP or newer), SSE/AVX and -mrtm, and enables AVX2/AVX-512 flags by reading /proc/cpuinfo. The published numbers need Optane DC PMM in App Direct mode; without it everything runs in DRAM. |
| **Thread safety** | dtree::dpftree is single-threaded with no locking. dptree::concur_dptree allows concurrent insert/upsert/lookup/lookup_range, using an OLC B+-tree, per-thread epoch words and a detached merge thread; writers block when the buffer fills while a previous merge is still running. |
| **Drop-in for the baseline** | no |

## Gotchas

- Stored values are shifted left one bit (the low bit is the tombstone flag), and lookup returns them still encoded, so callers must shift right by 1 (the test drivers call strip_upsert_value). Values are therefore limited to 63 bits. Also, concur_dptree::upsert's in-place base-tree update (update_if_found) writes the raw, unshifted value, which is inconsistent with the other paths.
- dpftree::lookup does not check the tombstone bit in the DRAM buffer, so a key that was erased but not yet merged is still reported as found.
- concur_dptree.hpp defines the non-inline function spin_until_no_ref in the header, so including it in more than one translation unit causes duplicate-symbol link errors. Its thread-local epoch words are static per template instantiation and register with only the first instance's managers, so do not run two instances of the same &lt;K,V&gt; in one process. The embedding program must also define the global int parallel_merge_worker_num.
- The benchmark drivers default to dense keys 0..n-1; pass sparseKey=1 to get the random 64-bit keys the paper used. The public drivers cover only insert and search (plus single-thread scans); the YCSB mixes and the baseline harness are not published.

## Known shortcomings

- The 1.82/1.85/2.19x are point-lookup gains vs FAST+FAIR/FPTree/WORT respectively; scans are up to 1.1x slower than FAST+FAIR. Baseline code not public; requires Intel Optane persistent memory.
- No recovery code (issue #4 open; confirmed by the APEX paper), and its 'PM' allocations are posix_memalign DRAM. uint64 keys only (double keys segfault, #3); the concurrent version has no erase; lookups return the internally encoded (&lt;&lt;1) value and the upsert base-tree path writes raw values, which is inconsistent. Header non-inline functions cause multi-TU link errors; static thread_local epochs allow one instance per type. \~34% more memory; APEX beats it on most operations.

## Caveats and trade-offs

The 1.82x/1.85x/2.19x figures are single-thread point-lookup gains over FAST+FAIR/FPTree/WORT respectively, not gains over FAST+FAIR across workloads. The 3.0x/10.98x figures are range-scan gains over FPTree/WORT; on scans DPTree is up to 1.1x slower than FAST+FAIR, which also keeps the highest scan throughput in ScanInsert. Experiments ran on real Optane DC PMM (App Direct, ext4-DAX), not emulated PM. FPTree is the authors' own reimplementation because the original is closed-source. The public repo contains only DPTree's own benchmark drivers, not the baseline harness. Intel Optane is discontinued.

Splits a DRAM-resident hot buffer (backed by stx-btree) from a cold persistent tree, requiring in-place PM merges; depends on Intel TBB and tcmalloc as external libraries

## Maintenance

Abandoned: the code was published in Sep 2020 and last touched 2021-07-28 (a build fix), and two 2021 issues (missing recovery code, crashes with double keys) are unanswered. It is MIT-licensed and about 6K lines, so treat it as a research reference for discontinued Optane hardware rather than a library to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** This is a peer-reviewed PVLDB 13(4) paper comparing DPTree directly against FAST+FAIR, FPTree and WORT, and it states g++ 6.4 -O3 and 2x Xeon Platinum 8263C. It is not tier A because the public repo only has DPTree's own drivers (test/dptree_test.cxx, test/concur_dptree_test.cxx). The FAST+FAIR/WORT harness, the authors' FPTree reimplementation and their added FAST+FAIR concurrent-update code are not published, so the comparison cannot be reproduced.
- **Verifier notes:** The record misattributed the speedup triple (the 1.82/1.85/2.19 figures are point lookups against three different indexes). It wrongly called the compiler string garbled (it is g++ 6.4 -O3) and guessed emulated PM (the paper used real Optane). The page range is 421-434, not 421-433. Downgraded A to B because baseline code is not public. Metadata checks out via gh: MIT, 61 stars, not a fork, last commit 2021-07-28, so abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <http://www.vldb.org/pvldb/vol13/p421-zhou.pdf>
  - <https://github.com/zxjcarrot/DPTree-code>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/CMakeLists.txt>
  - <https://api.crossref.org/works/10.14778/3372716.3372717>
- **Sources the enricher read:**
  - <https://github.com/zxjcarrot/DPTree-code>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/README.md>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/CMakeLists.txt>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/include/dptree.hpp>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/include/concur_dptree.hpp>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/include/util.h>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/include/btreeolc.hpp>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/include/art_idx.hpp>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/src/util.cpp>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/misc/ARTOLC/Epoche.h>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/test/dptree_test.cxx>
  - <https://github.com/zxjcarrot/DPTree-code/blob/master/test/concur_dptree_test.cxx>
  - <https://github.com/zxjcarrot/DPTree-code/issues/2>
  - <https://github.com/zxjcarrot/DPTree-code/issues/3>
  - <https://github.com/zxjcarrot/DPTree-code/issues/4>
  - <https://github.com/zxjcarrot/DPTree-code/commits/master>
  - <http://www.vldb.org/pvldb/vol13/p421-zhou.pdf>
  - <https://arxiv.org/pdf/2105.00683>
  - <https://hn.algolia.com/api/v1/search?query=DPTree%20persistent%20memory&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/zxjcarrot/dptree-code`) · [data/wave6/enrich/raw/github_com_zxjcarrot_dptree_code.json](../../../data/wave6/enrich/raw/github_com_zxjcarrot_dptree_code.json) (enrichment confidence 0.8)

</details>
