# APEX (learned index on persistent memory)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Persistent, concurrent learned index for Intel Optane PM; up to 3.8x faster inserts than FAST+FAIR and other PM B+-trees.

| | |
|---|---|
| **Beats** | FAST+FAIR (also compared against LB+-Tree, DPTree, uTree, FPTree, BzTree) |
| **Claimed result** | Single-thread results (paper Fig. 4). Inserts: up to 15x/2.7x/3.8x/1.66x/6.8x/3.7x faster than BzTree/LB+-Tree/FAST+FAIR/DPTree/uTree/FPTree across five datasets (up to 3.8x over FAST+FAIR). On the hardest-to-fit FB dataset, inserts are 1.18x/5.16x/2.3x/1.26x faster than FAST+FAIR/BzTree/uTree/FPTree but 5.77%/42% slower than LB+-Tree/DPTree. Search: up to 7.1x/3.9x/4.1x/3.2x/3.2x/5.8x higher than BzTree/LB+-Tree/FAST+FAIR/DPTree/uTree/FPTree. Scans: up to 7.6x/1.45x/1.46x/1.83x/16.38x/3.1x faster than BzTree/LB+-Tree/FAST+FAIR/DPTree/uTree/FPTree on five datasets. The abstract says up to \~15x better than existing PM indexes; that figure is the BzTree insert case. |
| **Workload** | YCSB-derived and real-world datasets (Longitudes, Longlat, Lognormal, FB, TPC-E), 8-byte integer/double keys, insert/search/scan/update/erase and mixed read-heavy/balanced operation mixes, single NUMA node up to 24 physical cores, on real Intel Optane DC Persistent Memory |
| **Metric** | throughput |
| **Hardware** | 2.1GHz Intel Xeon Gold 6252 (24 cores / 48 hyperthreads, 35.75MB L3), 768GB Intel Optane DCPMM (6 x 128GB) plus 192GB DRAM, Arch Linux kernel 5.10.11 |
| **Compiler and flags** | GCC 10.2 'with all optimizations' (paper section 6.2). The repo's CMakeLists.txt GCC flags are -mrtm -msse4.1 -mavx2 -O3 -g -march=native. |
| **Adoption** | 49 stars. Built on Microsoft's ALEX learned index code (README). Published as PVLDB 15(3):597-610 (Nov 2021, DOI 10.14778/3494124.3494141). |
| **Last commit** | 2023-04-19 |
| **Links** | [repository](https://github.com/baotonglu/apex) · [benchmark](https://arxiv.org/pdf/2105.00683) |

## Verdict

These are the authors' single-thread microbenchmarks on a 24-core Xeon Gold 6252 with 768 GB Optane DCPMM in App Direct mode, compiled with GCC 10.2: 100M bulk-loaded 8-byte keys followed by 100M operations. APEX inserts are up to 3.8x faster than FAST+FAIR (up to 15x vs BzTree) and lookups up to 4.1x faster, but on FB inserts beat FAST+FAIR by only 1.18x and lose to LB+-Tree and DPTree. Every baseline is another PM tree, not a stdlib container, and the authors' modified competitor code is not in the repo, so the comparison cannot be rerun from public code.

## Use it when

- You already run Intel Optane DCPMM in App Direct mode and need a persistent, concurrent ordered index on 8-byte integer or double keys with 8-byte payloads (inline or pointer).
- Point lookups, updates, deletes and short scans dominate, on keys that fit piecewise-linear models (geo coordinates, lognormal, YCSB-style IDs). In the paper, lookups scale almost linearly up to 24 physical cores.
- Restart time matters: the paper measures about 42 ms recovery whether the index holds 50M or 150M keys, then under 0.35 s of warm-up with 24 threads (up to 5.2 s single-threaded).
- You want a reference design or research baseline for persistent learned indexes (probe-and-stash, rebuildable DRAM accelerators, crash-consistent structural changes).

## Skip it when

- You have no Optane: 3D XPoint/Optane was discontinued in July 2022. On DRAM or a RAM disk APEX runs but its persistence buys nothing, so ALEX or LIPP is the simpler choice.
- Your keys are hard to fit, like the FB user-ID set: there APEX inserts are 5.77% slower than LB+-Tree and 42% slower than DPTree, trees get deeper (3.13 levels on average) and scans slow down on long overflow buckets.
- Your insert bursts split nodes heavily at high thread counts: with nearly full nodes at 24 threads, LB+-Tree beat APEX by 1.3x.
- You need string or variable-length keys, duplicate keys, or payloads larger than 8 bytes. A static_assert limits keys to arithmetic types, and duplicates need a pointer to a linked list as the payload.
- You need production-grade crash consistency: open issue #7 (2024) reports that searches can return inserts and updates that are not yet persisted. Also still open: inserting into an empty index hangs (#1) and an out-of-range insert pattern hits a 'Count error' exit (#3). A 2024 comment on issue #5 reports a bulk_load segfault; the issue was closed by its reporter with no fix.

## How it is fast

Each data node's linear model predicts a slot (ALEX-style model-based search). ALEX's gapped arrays shift elements on insert; APEX instead uses probe-and-stash, which probes at most 16 slots (two 256-byte Optane XPLines) and then falls back to a stash array, so most inserts cost one PM write. DRAM-resident accelerators hold 1-byte fingerprints and overflow-bucket pointers for every 16 slots and compare them with SSE, which skips useless PM reads. Data nodes are capped at 256 KB (inner nodes at 16 MB) to keep structural changes cheap, and reads are lock-free, validated by one optimistic version lock per 256 records. Lazy recovery compares a global version number with per-node version numbers and defers repair work to the first access of each node.

## Compared with alternatives

Choose APEX over DPTree on PM when you need double keys, deletes, instant recovery and faster lookups and scans: per the APEX paper, DPTree's code lacks double keys, delete and recovery. DPTree still inserts about 42% faster on hard-to-fit data like FB. Without Optane persistence, use ALEX (the DRAM index APEX is built on) or LIPP instead.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | PMDK libpmemobj/libpmem from a pinned fork (HaoPatrick/pmdk, addr-patch branch; the allocator calls pmemobj_create_addr/pmemobj_open_addr) and XiangpengHao/epoch-reclaimer (headers, master branch), both fetched from GitHub at CMake configure time. The benchmark also links TBB, PAPI, tcmalloc_minimal and libnuma. |
| **Minimum toolchain** | C++14 and CMake 3.12+. Tested only with GCC 10.2 on Linux 5.10.11; the README requires kernel &gt;= 4.17 and glibc &gt;= 2.29. |
| **Platforms** | x86-64 Linux only: needs the CLWB instruction (inline asm) and SSE/AVX2 intrinsics, and builds with -march=native. Persistence needs Optane DCPMM in App Direct mode on a DAX-mounted filesystem; the author suggests a RAM disk for functional testing without PM. |
| **Thread safety** | Built for concurrent insert, search, update, erase and scan. Traversal and reads are lock-free and validated by per-256-record optimistic version locks. Node-level locks serialize structural changes. Epoch-based reclamation is opt-in on each call. Open issue #7 says reads can observe unpersisted writes, which breaks crash consistency. |
| **Drop-in for the baseline** | no |

## Gotchas

- The PM pool path (/mnt/pmem0/baotong/template.data), its 40 GB size and its fixed mapping address are constants in src/util/allocator.h, so you must edit them. There is one static pool per process, and if the pool file already exists the benchmark takes the recovery path, so delete it before a fresh run.
- The headers define non-inline global variables and static data members (allocator.h, apex_base.h, apex.h), so include them from exactly one translation unit or expect duplicate-symbol link errors.
- API semantics: insert does not overwrite an existing key (it returns false). range_scan_by_key is a stub that returns 0. range_scan_by_size allocates its result with new[] if you pass nullptr. Every call's epoch flag defaults to false, which skips the reclamation guard, so pass true under concurrency.
- Erase never shrinks or merges nodes (merge() prints FATAL and exits), so deleted space is not reclaimed. size() is approximate because each thread batches its key-count updates in chunks of 2^19. Internal consistency checks call exit(-1) instead of returning an error.

## Known shortcomings

- The public harness runs only APEX (competitor code is linked upstream only). The 15x is vs BzTree on inserts; vs FAST+FAIR it is 3.8x. Requires Intel Optane persistent memory.
- Requires Intel Optane in App Direct/DAX mode (Optane discontinued in 2022); the pool path/size/address are hard-coded in allocator.h and globals in headers limit it to one translation unit. On hard (FB-like) keys its inserts lose to LB+-Tree (1.3x faster at 24 threads) and DPTree.
- Open bugs: persist race (#7, unanswered), empty-index hang (#1; fix PR #9 unmerged), Count-error exit (#3); bulk_load segfault (#5) closed without a fix. No merge/shrink on erase; range_scan_by_key is a stub; numeric keys of &lt;=8 B only. Code inactive since 2021-09.

## Caveats and trade-offs

All comparisons are against other PM-resident indexes on real Optane DCPMM, not against DRAM-resident RocksDB/LevelDB/LMDB or the RMI/PGM learned indexes. The public repo's benchmark only runs APEX; competitor implementations, including the authors' added range scans for FAST+FAIR, LB+-Tree and uTree and their LB+-Tree fix, are only linked to upstream repos. APEX is slower than LB+-Tree and DPTree on inserts for the FB dataset. Intel Optane DCPMM has been discontinued, so the target hardware is no longer sold.

Requires real Intel Optane DC PM with App Direct mode and DAX filesystem; inherits ALEX's linear-model-fitting assumptions, so performance depends on how well the key distribution fits piecewise-linear models (worst case on the hard-to-fit FB dataset)

## Maintenance

Abandoned: the last code change was in September 2021 (only README edits in 2023), a 2024 crash-consistency bug report is unanswered and a 2026 fix PR is unmerged. It is MIT-licensed but targets hardware discontinued in 2022, so treat it as a research reference rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** This is a peer-reviewed PVLDB 15(3) paper (arXiv extended version) that compares APEX directly against FAST+FAIR and five other PM indexes, and states GCC 10.2 and a Xeon Gold 6252; the repo's CMakeLists.txt gives the flags. It is not tier A because the public harness (src/benchmark/main.cpp) only builds APEX (index_type == "apex"). The competitor code, including the authors' own range-scan additions for FAST+FAIR, LB+-Tree and uTree and their LB+-Tree fix, is only linked to the upstream repos, so the comparison against the baseline cannot be rerun from public code.
- **Verifier notes:** Numbers are accurate, but the record's '15x' was presented as a general insert result; it is the BzTree case, and the insert gain over FAST+FAIR is 3.8x. I added the FB insert regression. Downgraded A to B because baseline code is missing from the artifact. Metadata checks out via gh: MIT, not a fork, last commit 2023-04-19, so abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2105.00683>
  - <https://github.com/baotonglu/apex>
  - <https://github.com/baotonglu/apex/blob/main/CMakeLists.txt>
  - <https://github.com/baotonglu/apex/blob/main/src/benchmark/main.cpp>
  - <https://api.crossref.org/works?query.bibliographic=APEX+A+High-Performance+Learned+Index+on+Persistent+Memory&rows=3>
- **Sources the enricher read:**
  - <https://github.com/baotonglu/apex>
  - <https://github.com/baotonglu/apex/blob/main/CMakeLists.txt>
  - <https://github.com/baotonglu/apex/blob/main/build.sh>
  - <https://github.com/baotonglu/apex/blob/main/run.sh>
  - <https://github.com/baotonglu/apex/blob/main/src/tree.h>
  - <https://github.com/baotonglu/apex/blob/main/src/core/apex.h>
  - <https://github.com/baotonglu/apex/blob/main/src/core/apex_base.h>
  - <https://github.com/baotonglu/apex/blob/main/src/core/apex_nodes.h>
  - <https://github.com/baotonglu/apex/blob/main/src/util/allocator.h>
  - <https://github.com/baotonglu/apex/blob/main/src/util/utils.h>
  - <https://github.com/baotonglu/apex/blob/main/src/benchmark/main.cpp>
  - <https://github.com/baotonglu/apex/issues?q=is%3Aissue>
  - <https://github.com/baotonglu/apex/issues/1>
  - <https://github.com/baotonglu/apex/issues/2>
  - <https://github.com/baotonglu/apex/issues/3>
  - <https://github.com/baotonglu/apex/issues/4>
  - <https://github.com/baotonglu/apex/issues/5>
  - <https://github.com/baotonglu/apex/issues/6>
  - <https://github.com/baotonglu/apex/issues/7>
  - <https://github.com/baotonglu/apex/pull/9>
  - <https://github.com/baotonglu/apex/commits/main>
  - <https://arxiv.org/pdf/2105.00683>
  - <https://en.wikipedia.org/wiki/3D_XPoint>
  - <https://hn.algolia.com/api/v1/search?query=APEX%20learned%20index%20persistent%20memory&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/baotonglu/apex`) · [data/wave6/enrich/raw/github_com_baotonglu_apex.json](../../../data/wave6/enrich/raw/github_com_baotonglu_apex.json) (enrichment confidence 0.85)

</details>
