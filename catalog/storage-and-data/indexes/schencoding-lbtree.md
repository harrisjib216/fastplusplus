# LB+-Trees (persistent B+-Tree optimized for 3D XPoint memory)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · 🔴 abandoned

> Persistent B+-Tree for Intel Optane PM; 1.12-2.92x faster inserts than WB+-Tree and FP-Tree, similar lookups.

| | |
|---|---|
| **Beats** | WB+-Tree and FP-Tree (state-of-the-art NVM-optimized persistent B+-trees) |
| **Claimed result** | Abstract: up to 1.12-2.92x speedups over state-of-the-art NVM-optimized indexes. Single-thread insertions vs WB+-Tree / FP-Tree: 70%-full leaves 1.20-1.24x / 1.12-1.21x; 100%-full leaves 2.55-2.92x / 2.31-2.45x; dense (monotonic) insertions 2.31-2.69x / 2.22-2.33x; overall 1.20-2.92x / 1.12-2.45x. With 1-16 threads: 70%-full 1.17-1.30x / 1.22-1.38x; 100%-full 2.35-2.69x / 2.10-2.53x; dense 1.90-2.38x / 1.89-2.55x. Search and deletion are similar to WB+-Tree and FP-Tree. Memcached: 1.05-1.29x over WB+-Tree and 1.06-1.22x over FP-Tree. The Get / sequential-Put / random-Put figures (1-thread 1.31-1.54x / 1.44-1.80x / 1.46-1.83x; 16-thread 1.25-1.40x / 1.35-1.64x / 1.28-1.46x) are X-Engine results against divided-skiplist, not against WB+-Tree or FP-Tree. |
| **Workload** | Micro-benchmarks: bulkload 2 billion 8B-key/8B-value entries (32GB) at 70% or 100% leaf fill, then random and dense (monotonically increasing) insertions, lookups and deletions, single-threaded and 1-16 threads, with node sizes of 256B-1KB, on real Intel Optane DC PM. Also X-Engine db_bench (8B key / 20B value Get, sequential Put and random Put at 1 and 16 threads) against divided-skiplist, and Memcached mc-benchmark (500K random 20-byte string keys) against WB+-Tree and FP-Tree. |
| **Metric** | throughput |
| **Hardware** | Dual-socket Intel Cascade Lake-SP, 28 cores/socket @ 2.5GHz (Turbo Boost 3.8GHz), 32KB L1i/d, 1MB L2 per core, 39MB shared L3, 512GB Intel Optane DC PM, Linux 4.9.135 |
| **Compiler and flags** | Not stated in the paper; the repo Makefile builds with g++ -O3 -std=c++11 -pthread -mrtm -msse4.1 -mavx2 and links libpmem. |
| **Adoption** | 49 stars; published as PVLDB 13(7):1078-1090 (2020); listed as a baseline competitor in the later APEX (VLDB'22) paper |
| **Last commit** | 2020-09-06 |
| **Links** | [repository](https://github.com/schencoding/lbtree) · [benchmark](http://www.vldb.org/pvldb/vol13/p1078-liu.pdf) |

## Verdict

On a dual-socket Cascade Lake-SP with 512GB Optane DC PM (fsdax, Linux 4.9.135), each tree was bulkloaded with 2 billion 8B/8B entries and then given 50K-300K random or monotonic inserts. LB+-Tree beat WB+-Tree and FP-Tree, implemented in the same framework, by 1.12-2.92x (up to 2.69x with 1-16 threads), with lookups and deletes on par; the paper gives no compiler or flags and the baseline code is not public. The independent VLDB'22 'Part Two' evaluation (Xeon Gold 6242R, GCC 11.1, PMDK) also found it the best performer in most cases, but only after its authors fixed persistence and added scans.

## Use it when

- Benchmarking or studying persistent B+-Trees on Intel Optane DC PM in App Direct/fsdax mode with 8-byte integer keys and 8-byte values or pointers
- Insert-heavy workloads with full leaves (frequent splits) or monotonic, hot-spot inserts such as time-ordered keys: this is where the paper shows 2.2-2.9x over WB+-Tree and FP-Tree
- Multi-threaded insert or update throughput on one socket: the independent VLDB'22 'Part Two' evaluation found its inserts scale best, 2.09x faster than FPTree and 1.55-3.07x faster than ROART, DPTree and PACTree
- As a strong baseline to beat in new PM-index work (APEX and the 'Part Two' evaluation both use it)

## Skip it when

- Anything in production: there is no license, no crash-recovery code, no range scan, a known read-uncommitted bug and no HTM fallback path
- Machines without Optane (discontinued) or without working Intel TSX/RTM plus clwb: TSX is off by default in Linux according to the author, and the code does not run correctly without it
- Scan-heavy workloads: the 14-entry 256B leaves made scans about 30% slower than FPTree single-threaded, and much worse multi-threaded, in the independent evaluation, and the repo has no scan anyway
- Variable-length or string keys: the repo only handles 8-byte keys, the paper's X-Engine/Memcached key-pointer variant is not published, and an independent test found pointer chasing dominates, with trie-based ROART winning
- Lookup-dominant or instant-restart needs: search only matches WB+-Tree and FP-Tree, APEX searches up to 3.9x faster, and restart must rebuild the DRAM inner nodes, whereas FAST+FAIR and APEX recover in under a second

## How it is fast

Entry moving: Optane write cost depends on how many 64B lines are written, not how many words change. So when an insert lands in a slot outside the header line, the code also moves entries out of line 0 into free slots in the target line. Later inserts then find a free slot next to the header and need only one clwb'd line (the paper derives at least 1.35x fewer line writes per insert in a stable tree). Logless leaf split: each leaf has two alternative sibling pointers and an alt bit, and one 8-byte NVM atomic write of the header word flips alt and the bitmap after the new node is persisted, so there is no write-ahead log as in WB+-Tree and FP-Tree. It also uses 256B nodes matching Optane's internal 256B access size, FP-Tree-style DRAM inner nodes, 14 one-byte fingerprints probed with a single SSE _mm_cmpeq_epi8, and Intel RTM transactions plus a per-leaf lock bit so that clwb/sfence run outside the transaction.

## Compared with alternatives

Pick LB+-Tree over FAST+FAIR or DPTree when multi-threaded insert or update throughput on Optane with DRAM inner nodes matters most and you can live with a rebuild at restart and a TSX dependency. Pick it over APEX when keys are hard for learned models to fit or splits are frequent: APEX was 5.8% slower on the FB dataset for inserts and 1.3x slower with intensive splits at 24 threads. For everything else APEX is faster (up to 2.7x inserts and 3.9x lookups) and FAST+FAIR recovers instantly.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | PMDK libpmem; an x86 CPU with Intel RTM (TSX) and the clwb instruction; an Optane PM file on a DAX file system (mempool.h can be edited to use DRAM via memalign for testing) |
| **Minimum toolchain** | C++11 with g++ (Makefile: -O3 -std=c++11 -pthread -mrtm -msse4.1 -mavx2); uses GCC builtins and inline asm; no compiler version is documented |
| **Platforms** | Linux x86-64 on Intel CPUs with TSX enabled and clwb (tested on Cascade Lake-SP with Optane DC PM); a user had to swap clwb for clflush on Broadwell |
| **Thread safety** | Concurrent lookup, insert and delete use RTM transactions plus a lock bit in each leaf. Memory pools are per thread and indexed by a thread_local worker_id that the driver sets. A leaf lock is released before its flush (issue #2), so readers can see non-durable data. |
| **Drop-in for the baseline** | no |

## Gotchas

- If _xbegin() fails, the code just jumps back and retries with no bound and no lock fallback, so with TSX disabled every operation spins forever (issues #1 and #7). The author's fix is the boot options tsx=on tsx_async_abort=off mds=off, which also switch off the MDS mitigation.
- Two community fixes have been open and unmerged since 2021. PR #6 fixes read-uncommitted isolation by releasing the lock with a non-temporal store. PR #5 fixes a signed overflow in the inner-node binary search (r = key - p-&gt;k(m)) that UBSAN caught and that can misroute keys.
- LEAF_SIZE is hard-wired to 256B (#error otherwise), so the paper's multi-256B 'distributed headers' variant is not in the repo. The fptree-src and wbtree-src baselines are also missing (issue #4).
- A user reported that bulkload must run before inserts to initialise the tree. Issue #8 (unanswered) reports that the first store to each DAX page aborts RTM after a restart, and that recycled NVM nodes are neither zeroed nor persistently allocated.

## Known shortcomings

- The Get/Put numbers are vs a divided skip list, not WB+-tree/FP-tree; search is on par; baseline source missing; abandoned since 2020-09. Requires 3D XPoint persistent memory.
- Not a library: a benchmark executable with main(); API is bulkload/lookup/insert/del only (no scan, update or recovery). The RTM retry loop has no fallback and hangs if TSX is off (#1, #7); needs Optane with clwb. Read-uncommitted bug (#2) and signed-overflow search bug (PR #5) with fixes unmerged since 2021; no license ('TBD'); 8 B integer keys only. The independent VLDB'22 study confirms the best multi-threaded inserts (2.09x FPTree) but \~30% slower scans.

## Caveats and trade-offs

The repository has no license file (all rights reserved by default), so the code can be studied but not redistributed without asking the authors. The README lists fptree-src and wbtree-src, but they are not in the repo, so the baseline comparisons cannot be reproduced from it. Gains are insert-side only: search and delete match WB+-Tree and FP-Tree. It needs Intel RTM (TSX), PMDK and Optane PM hardware, which Intel has discontinued. The paper gives the CPU only as Cascade Lake-SP with no SKU and states no compiler or flags.

Uses Intel RTM (hardware transactional memory) for concurrency control and requires real 3D XPoint/Optane hardware or PMDK-based emulation; per-entry fingerprint metadata adds memory overhead

## Maintenance

Abandoned: six commits on 2020-09-06, fix PRs open since 2021, no license file (the headers say 'LICENSE TBD'), and it is tied to discontinued Optane and TSX hardware, so treat it as a reference design to study rather than code to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** The PVLDB'20 paper compares LB+-Tree with WB+-Tree and FP-Tree on real Optane (Cascade Lake-SP), but states no compiler or flags and no exact CPU SKU. The repo holds only lbtree-src: the fptree-src and wbtree-src directories listed in its README are absent and their Makefile targets are commented out, so the baseline benchmark code is not public. That makes it a peer-reviewed B, not A.
- **Verifier notes:** The headline 1.12-2.92x is correct, but the record credited the X-Engine-vs-divided-skiplist per-operation numbers to WB+-Tree and FP-Tree, which overstates Get (search is actually on par). The default-branch last commit is 2020-09-06; the record's 2021-04-04 is pushed_at. Still abandoned. No license (null) was confirmed; the APEX baseline listing was confirmed in the APEX paper.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <http://www.vldb.org/pvldb/vol13/p1078-liu.pdf>
  - <https://github.com/schencoding/lbtree>
  - <https://arxiv.org/pdf/2105.00683>
- **Sources the enricher read:**
  - <https://github.com/schencoding/lbtree>
  - <https://github.com/schencoding/lbtree/blob/master/README.md>
  - <https://github.com/schencoding/lbtree/blob/master/Makefile>
  - <https://github.com/schencoding/lbtree/blob/master/lbtree-src/lbtree.h>
  - <https://github.com/schencoding/lbtree/blob/master/lbtree-src/lbtree.cc>
  - <https://github.com/schencoding/lbtree/blob/master/common/tree.h>
  - <https://github.com/schencoding/lbtree/blob/master/common/tree.cc>
  - <https://github.com/schencoding/lbtree/blob/master/common/mempool.h>
  - <https://github.com/schencoding/lbtree/blob/master/common/mempool.cc>
  - <https://github.com/schencoding/lbtree/blob/master/common/nvm-common.h>
  - <https://github.com/schencoding/lbtree/issues/1>
  - <https://github.com/schencoding/lbtree/issues/2>
  - <https://github.com/schencoding/lbtree/issues/3>
  - <https://github.com/schencoding/lbtree/issues/4>
  - <https://github.com/schencoding/lbtree/issues/7>
  - <https://github.com/schencoding/lbtree/issues/8>
  - <https://github.com/schencoding/lbtree/pull/5>
  - <https://github.com/schencoding/lbtree/pull/6>
  - <https://github.com/schencoding/lbtree/commits/master>
  - <https://github.com/schencoding/lbtree/forks>
  - <http://www.vldb.org/pvldb/vol13/p1078-liu.pdf>
  - <https://arxiv.org/pdf/2105.00683>
  - <https://arxiv.org/pdf/2201.13047v2>
  - <http://export.arxiv.org/api/query?search_query=ti:%22Evaluating%20Persistent%20Memory%20Range%20Indexes%22>
  - <https://hn.algolia.com/api/v1/search?query=LB%2B-Tree%203DXPoint&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/schencoding/lbtree`) · [data/wave6/enrich/raw/github_com_schencoding_lbtree.json](../../../data/wave6/enrich/raw/github_com_schencoding_lbtree.json) (enrichment confidence 0.85)

</details>
