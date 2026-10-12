# FAST+FAIR (Failure-Atomic ShifT + Failure-Atomic In-place Rebalancing B+-Tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `GPL-3.0` · 🔴 abandoned

> Crash-consistent persistent-memory B+-tree using failure-atomic in-place shifts; range scans 6-33% faster than FP-tree/wB+-tree (emulated PM).

| | |
|---|---|
| **Beats** | wB+-tree, FP-tree, WORT and SkipList (single-threaded); FP-tree, B-link tree and SkipList (concurrent) |
| **Claimed result** | FAST'18 paper: range queries up to 20x faster than SkipList and 6-27% faster than FP-tree / 25-33% faster than wB+-tree (10M 8-byte random keys, 1KB nodes, 300ns PM read latency). Insertion: FAST+FAIR, FP-tree and WORT are comparable and beat wB+-tree and SkipList 'by a large margin' (wB+-tree issues 1.7x more cache-line flushes); as PM write latency rises FAST+FAIR consistently outperforms FP-tree, wB+-tree and SkipList, but WORT is fastest. The 'up to 1.61x faster than wB+-tree' figure is from the ARM (Nexus 5 / Snapdragon 800) non-TSO insertion experiment, not the Xeon runs. TPC-C mixes W1-W4: FAST+FAIR consistently outperforms the other indexes (figure only, no ratio). Concurrency is self-scaling only: search throughput rises about 11.7x from 1 to 16 threads, insertion about 12.5x at 16 threads (FP-tree 7.7x, B-link 4.4x), and the mixed workload reaches up to 11.44x the single-thread throughput. The '\~2.2x higher than B-link tree at 8 threads' figure belongs to FP-tree (TSX), not FAST+FAIR. |
| **Workload** | Single- and multi-threaded (up to 16 threads) synthetic key-value insert/search/range-query workload with 8-byte integer keys on emulated byte-addressable persistent memory (NVM), varying node size and range-query selection ratio |
| **Metric** | throughput |
| **Hardware** | Workstation with two Intel Xeon Haswell-EX E7-4809 v3 @ 2.0GHz (16 vCPUs with hyper-threading, 20MB L3), 64GB DDR3 DRAM; threads bound to one socket with numactl for the concurrent runs; PM latency emulated with the Quartz DRAM-based emulator. The ARM experiment ran on a Nexus 5 (Snapdragon 800 @ 2.26GHz) with nop-injected PM write latency. |
| **Compiler and flags** | g++ 4.8.2 -O3 (single-threaded); concurrent implementations compiled without -O3 because the optimizer reorders memory operations needed by the lock-free logic |
| **Adoption** | 118 stars; evaluated as a baseline in later persistent-memory index papers including DPTree (PVLDB 13(4)) and APEX (VLDB'22). The LB+-Tree (PVLDB 13(7)) and BzTree (PVLDB 11(5)) papers do not evaluate it. |
| **Last commit** | 2020-06-12 |
| **Links** | [repository](https://github.com/DICL/FAST_FAIR) · [benchmark](https://www.usenix.org/system/files/conference/fast18/fast18-hwang.pdf) |

## Verdict

In the FAST'18 paper (g++ 4.8.2 -O3 single-threaded on a Xeon E7-4809 v3, with PM emulated by Quartz at 300 ns), range queries over 10M random 8-byte keys in 1 KB nodes were 6-27% faster than FP-tree, 25-33% faster than wB+-tree and up to 20x faster than SkipList. Inserts were on par with FP-tree and WORT, and WORT won inserts at higher write latency. Concurrent results were measured at -O0 and are self-scaling only (11.7x search, 12.5x insert at 16 threads versus 7.7x and 4.4x for FP-tree and B-link tree); the baseline implementations are not published in the repo.

## Use it when

- Reproducing or baselining persistent-memory index research on 8-byte integer keys: DPTree, APEX and RECIPE all benchmark against this code.
- Range-scan-heavy ordered index on PM with 64-bit integer keys: RECIPE's independent evaluation on real Optane DCPMM (16 threads, 64M keys) found FAST & FAIR beat P-ART, P-HOT, P-Masstree and P-BwTree on range scans.
- Studying or prototyping log-free failure-atomic B+-tree techniques: each variant is a single \~1,000-line header that is easy to read and modify.
- Read-mostly multi-threaded lookups where read-uncommitted visibility is acceptable: in the paper, lock-free search scaled about 11.7x from 1 to 16 threads on emulated PM.

## Skip it when

- Holding data you cannot lose. Known correctness bugs: concurrent internal-node splits can place a key in the wrong node so it is never found (issue #5/PR #4, confirmed by the RECIPE authors, fix unmerged), the lock-free inner-node search can follow the wrong child (#16), concurrent range scans can return duplicate or unsorted results (#7), and RECIPE lost keys after consecutive crashes during split and merge.
- Needing actual restart and recovery. single/ and concurrent/ keep nodes in volatile DRAM, and the PMDK variants segfault when reopening a pool that already holds data, because volatile lock pointers are stored inside persistent nodes (issue #12, open).
- String or variable-length keys, upserts, or NULL or duplicate values: keys are int64_t only, values must be unique non-null char\* pointers (NULL is the end-of-node sentinel), and there is no update operation.
- Write-heavy or point-lookup-heavy workloads on real Optane: RECIPE measured P-ART up to 1.6x faster on write-heavy and P-HOT 1.5x faster on read-heavy YCSB, and 2.5-5x gaps with string keys. The catalogued DPTree and APEX also beat it.
- Non-x86 targets or commercial use: the code uses x86-only inline asm (rdtsc, pause, clflush, mfence), and the source headers restrict use to non-commercial research despite the GPL-3.0 LICENSE file.

## How it is fast

FAST (Failure-Atomic ShifT) inserts into a sorted node by shifting entries right one 8-byte store at a time. It flushes only when the shift crosses a cache-line boundary, and a transiently duplicated pointer marks an in-flight shift that readers skip, so no undo/redo log is needed. FAIR (Failure-Atomic In-place Rebalancing) splits and merges nodes in place using B-link-style sibling pointers, and later traversals tolerate a half-finished split and repair it lazily. Keys stay sorted in small nodes (512 B by default) that are scanned linearly. That keeps range scans sequential and prefetcher-friendly, and it lets readers run lock-free by scanning in the direction given by a per-node switch_counter (the paper found linear search beat binary search below 4 KB nodes).

## Compared with alternatives

Pick FAST+FAIR over DPTree, APEX or LB+-Tree only when you want a simple sorted-leaf PM B+-tree baseline, or a range-scan-heavy 64-bit-integer workload, and can live with research-grade code. DPTree has up to 1.82x faster lookups and APEX up to 3.8x faster inserts than FAST+FAIR, while LB+-Tree targets real 3D XPoint. For DRAM-only ordered indexes, prefer ALEX, LIPP, HOT or ART, since FAST+FAIR's flushes are pure overhead there.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for single/ (libc, -lrt -lm); pthread for concurrent/; libpmemobj (PMDK) for single_pmdk/ and concurrent_pmdk/ |
| **Minimum toolchain** | C++11 with GNU inline asm; the Makefiles use g++ -std=c++11 and the paper used g++ 4.8.2. The code uses the `register` storage class, which C++17 removed. |
| **Platforms** | x86-64 only (the ARM/non-TSO variant from the paper is not in the repo); Linux |
| **Thread safety** | single/: none. concurrent/: writers take a per-node std::mutex and readers are lock-free at read-uncommitted isolation, and it must be built at -O0 because there are no atomics or compiler barriers. concurrent_pmdk/: pthread rwlocks, with readers taking read locks in leaves. Known concurrency bugs are listed above. |
| **Drop-in for the baseline** | false (a research prototype with its own int64-key/char\*-value API; the named baselines wB+-tree, FP-tree, WORT and SkipList are not in the repo) |

## Gotchas

- The concurrent Makefiles compile with -O0 on purpose. The paper says -O3 reorders memory operations the lock-free reads depend on, because the read path uses plain loads with no std::atomic or compiler fences, so turning on optimization can silently break correctness.
- btree.h defines globals (for example write_latency_in_ns) and non-inline member functions at namespace scope, plus `using namespace std;`. Include it in exactly one translation unit, or you get duplicate-symbol link errors.
- Every flush is clflush fenced by mfence on both sides, with an rdtsc spin loop for emulated write latency (CPU_FREQ_MHZ is hard-coded to 1994). Keep write_latency_in_ns at 0 on real hardware, and expect no clwb/clflushopt.
- Memory is never reclaimed: there is no btree destructor, merged nodes are only marked is_deleted, and concurrent deletes skip rebalancing entirely. btree_search_range writes into an unbounded caller buffer, and lookup misses print "NOT FOUND" to stdout.

## Known shortcomings

- The repo has no baseline code; the 1.61x is ARM only, the 2.2x is FP-tree's figure, 12.5x is at 16 threads and 20x is only vs a skip list; the LB+-tree and BzTree papers do not evaluate it. Requires persistent memory.
- Open concurrency bugs: a key is lost on concurrent split (#5, confirmed by RECIPE; fix PR #4 unmerged), wrong-child search (#16), duplicate/unsorted range scans (#7). No real recovery: non-PMDK builds keep nodes in DRAM and PMDK builds segfault on pool reopen (#12). The concurrent build must use -O0 (no atomics or fences); readers are read-uncommitted.
- License clash: LICENSE says GPL-3.0 but btree.h headers say UNIST non-commercial only. x86 asm only; int64 keys and unique non-null char\* values only; no upsert; nodes never freed. On real Optane (RECIPE) it has the best range scans but P-ART is 1.6x faster write-heavy and P-HOT 1.5x read-heavy. Abandoned since 2020-06.

## Caveats and trade-offs

PM was emulated (Quartz on DRAM; nop injection on ARM), not real Optane. FAST+FAIR is not uniformly fastest: WORT wins insertion at higher PM write latency; FP-tree searches slightly faster when read latency exceeds 600ns; on ARM at DRAM latency FAST+FAIR is slower than FP-tree. The repo ships only FAST+FAIR, not the baseline implementations. Concurrent builds omit -O3. These are the 2018 paper's numbers; later papers such as DPTree (up to 1.82x/1.85x/2.19x faster than FAST+FAIR) and APEX beat it, so it is now a baseline rather than the fastest option.

Relies on 8-byte failure-atomic word writes specific to NVM consistency model; leaf nodes use an unsorted array (linear search) trading insert speed for slower lookups at large node sizes; concurrent version uses per-node std::mutex-style locks, not fully lock-free

## Maintenance

Abandoned research code: the last master commit was 2020-06-12 (the issue-13 branch was last touched in 2021-03), and bug-fix PRs #4 and #15 remain unmerged. The LICENSE file is GPL-3.0 but every btree.h header grants only a non-commercial research license from UNIST, so clear the licensing before any product use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** The FAST'18 paper compares FAST+FAIR with wB+-tree, FP-tree, WORT and SkipList (plus B-link tree for concurrency) and states g++ 4.8.2 -O3 and the Xeon E7-4809 v3. It is not tier A because the DICL/FAST_FAIR repo holds only the FAST+FAIR code (single/, concurrent/, \*_pmdk/ test programs) with no wB+-tree, FP-tree, WORT, SkipList or B-link implementations, so the published benchmark code does not run against the named baselines; that makes it a peer-reviewed B.
- **Verifier notes:** Several sub-claims were misattributed: 1.61x vs wB+-tree is ARM-only, 2.2x over B-link is FP-tree's figure, 12.5x is at 16 threads (not 8), and 20x is vs SkipList only. The default-branch (master) last commit is 2020-06-12; the record's 2021-03-12 is pushed_at, which matches a 2021-03-11 commit on the non-default issue-13 branch. Still abandoned either way. License GPL-3.0, not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `hardware`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/conference/fast18/fast18-hwang.pdf>
  - <https://github.com/DICL/FAST_FAIR>
  - <http://www.vldb.org/pvldb/vol13/p421-zhou.pdf>
  - <https://arxiv.org/pdf/2105.00683>
  - <http://www.vldb.org/pvldb/vol11/p553-arulraj.pdf>
  - <http://www.vldb.org/pvldb/vol13/p1078-liu.pdf>
- **Sources the enricher read:**
  - <https://github.com/DICL/FAST_FAIR>
  - <https://github.com/DICL/FAST_FAIR/blob/master/README.md>
  - <https://github.com/DICL/FAST_FAIR/blob/master/LICENSE>
  - <https://github.com/DICL/FAST_FAIR/blob/master/single/src/btree.h>
  - <https://github.com/DICL/FAST_FAIR/blob/master/single/src/test.cpp>
  - <https://github.com/DICL/FAST_FAIR/blob/master/single/Makefile>
  - <https://github.com/DICL/FAST_FAIR/blob/master/concurrent/src/btree.h>
  - <https://github.com/DICL/FAST_FAIR/blob/master/concurrent/src/test.cpp>
  - <https://github.com/DICL/FAST_FAIR/blob/master/concurrent/Makefile>
  - <https://github.com/DICL/FAST_FAIR/blob/master/single_pmdk/src/btree.h>
  - <https://github.com/DICL/FAST_FAIR/blob/master/single_pmdk/Makefile>
  - <https://github.com/DICL/FAST_FAIR/blob/master/concurrent_pmdk/src/btree.h>
  - <https://github.com/DICL/FAST_FAIR/blob/master/concurrent_pmdk/src/test.cpp>
  - <https://github.com/DICL/FAST_FAIR/blob/master/concurrent_pmdk/Makefile>
  - <https://github.com/DICL/FAST_FAIR/issues>
  - <https://github.com/DICL/FAST_FAIR/issues/16>
  - <https://github.com/DICL/FAST_FAIR/issues/13>
  - <https://github.com/DICL/FAST_FAIR/issues/12>
  - <https://github.com/DICL/FAST_FAIR/issues/10>
  - <https://github.com/DICL/FAST_FAIR/issues/7>
  - <https://github.com/DICL/FAST_FAIR/issues/6>
  - <https://github.com/DICL/FAST_FAIR/issues/5>
  - <https://github.com/DICL/FAST_FAIR/issues/3>
  - <https://github.com/DICL/FAST_FAIR/issues/2>
  - <https://github.com/DICL/FAST_FAIR/pull/4>
  - <https://github.com/DICL/FAST_FAIR/pull/15>
  - <https://github.com/DICL/FAST_FAIR/commits/master>
  - <https://www.usenix.org/system/files/conference/fast18/fast18-hwang.pdf>
  - <http://export.arxiv.org/api/query?search_query=ti:RECIPE+AND+ti:persistent&max_results=5>
  - <https://arxiv.org/pdf/1909.13670v4>
  - <https://hn.algolia.com/api/v1/search?query=FAST%20FAIR%20persistent%20B%2B-tree&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/dicl/fast_fair`) · [data/wave6/enrich/raw/github_com_dicl_fast_fair.json](../../../data/wave6/enrich/raw/github_com_dicl_fast_fair.json) (enrichment confidence 0.86)

</details>
