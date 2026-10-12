# FastMap

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `LGPL-2.1` · 🟡 stale

> Linux 4.14 kernel module replacing the mmap page-fault and eviction path for fast block devices; 3.7-7x more page faults/s than mmap at high thread counts.

| | |
|---|---|
| **Beats** | mmap (Linux kernel memory-mapped I/O path) |
| **Claimed result** | Stock FastMap versus the Linux page cache (mmap) on null_blk: 3.7x read / 6.6x write at 32 threads, 4.7x / 7x at 80; 11.89x only with out-of-tree SPF kernel patches; Ligra BFS 5.27x on DRAM-backed pmem and 3.31x on Optane (from the author's thesis) |
| **Workload** | Microbenchmarks tests/rand_threads_\*.c on null_blk and pmem, plus Ligra BFS |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2630 v3 and E5-4610 v3, Linux 4.14.72 |
| **Adoption** | 37 stars |
| **Last commit** | 2021-09-29 |
| **Links** | [repository](https://github.com/CARV-ICS-FORTH/FastMap) · [benchmark](https://www.usenix.org/conference/atc20/presentation/papagiannis) |

## Verdict

Author-run measurements (ATC'20 paper, restated in Papagiannis's PhD thesis) on Linux 4.14.72, CentOS 7.3, 2x Xeon E5-2630 v3 (32 hyper-threads) and 4x Xeon E5-4610 v3 (80 hyper-threads), 256 GB DDR4, Intel Optane P4800X, null_blk and pmem: random page-fault IOPS 3.7x/6.6x (read/write) over Linux mmap at 32 threads and 4.7x/7x at 80 threads; 11.89x read IOPS only with SPF patches; Ligra BFS 3.31x on Optane, 5.27x on pmem; Kreon YCSB about 2x on average; MonetDB TPC-H +6.06%. Compiler and flags not stated; the random page-fault microbenchmarks (tests/rand_threads_read.c, tests/rand_threads_write.c) are in the repo.

## Use it when

- Research or reproduction work on mmap-heavy applications (mmap-based key-value stores such as Kreon, graph processing with Ligra, an mmap'd heap for Silo) on Optane-class NVMe where page-fault throughput, not the device, is the bottleneck.
- Many threads (16-80) taking random page faults on one mapping, where Linux mmap stops scaling beyond about 8 threads on the authors' 32-core box.
- Out-of-memory datasets on a fast block device where you can dedicate a fixed DRAM cache to the mapping.
- A machine you can pin to Linux 4.14 (the evaluated kernel is 4.14.72) and where crashing the kernel is acceptable.

## Skip it when

- Any production system: open issue #2 (2022) reports a kernel panic on random writes (rand_threads_write) on 4.14.123 with no maintainer reply.
- Modern kernels: the module resolves unexported symbols with kallsyms_lookup_name, which kernels from 5.7 on no longer export, and the README only supports 4.14.
- Machines whose core count is not 32 or 80: NUM_FREELISTS is hard-coded to 32 in shared_defines.h and mmap_buffer_hash_table.c only has tables for 1, 32 or 80 (otherwise '#error NUM_FREELISTS number is not supported!'); issue #1 reports a crash on a 256-core server.
- Mostly sequential workloads: the thesis reports only 6.06% average gain on MonetDB TPC-H.
- If you can change the application's I/O model: io_uring or SPDK (siblings) avoid the page-fault path entirely and are maintained.

## How it is fast

Per the author's PhD thesis (chapter 4, based on the ATC'20 paper): it removes the centralized contention points of the Linux mmap path by keeping separate clean and dirty trees per core (radix and red-black trees, pages assigned to cores round-robin), uses full per-page reverse mappings instead of Linux object-based rmap to cut CPU work on eviction, and runs a dedicated DRAM cache with per-core free lists and clean queues plus batched TLB shootdowns. It also raises device queue depth, and adds a user-set read-ahead to pre-map pages for sequential access.

## Compared with alternatives

Pick FastMap over UMap (userfaultfd, user space) or TriCache when the application must keep using kernel mmap semantics and you can run a 4.14 kernel module; pick vmcache/exmap, UMap, liburing or SPDK for anything maintained or on a current kernel.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Linux 4.14 kernel source/headers; userspace ioctl tools in the repo; WrapFS (included) for the file-system mode |
| **Minimum toolchain** | Kernel build toolchain for Linux 4.14 (compiler not documented) |
| **Platforms** | Linux 4.14 only; evaluated on x86-64 Intel Xeon (E5-2630 v3, E5-4610 v3) |
| **Thread safety** | Designed for concurrent page faults from many threads (per-core structures); stability bugs reported (issue #2 kernel panic on writes) |
| **Drop-in for the baseline** | partial — applications keep calling mmap(), but only on /dev/dmap/dmapN or files under a WrapFS mount after the module is loaded with a fixed DRAM cache size |

## Gotchas

- The README's cache-size example is wrong: perma_mmap_buf_size=1024 is 1024 4 KB pages, i.e. 4 MB, not the 4 GB it states; the default in main.c is PAGES_16G (16 GB of DRAM reserved at load).
- The headline 11.8x (11.89x in the thesis) needs out-of-tree Speculative Page Fault kernel patches modified for FastMap; stock FastMap without SPF gives 4.7x (read) and 7x (write) on 80 threads, and 3.7x / 6.6x on 32 threads, all on null_blk, which discards I/O.
- The 5.27x figure is Ligra BFS on a DRAM-backed pmem block device (21.9 s vs 4.15 s); on the Optane SSD the same run is 3.31x (21.3 s vs 6.42 s).
- Licensing is mixed: the LICENCE file is LGPL-2.1, but main.c declares MODULE_LICENSE("GPL").

## Known shortcomings

- Issue 2 reports a kernel panic on writes (unanswered); NUM_FREELISTS only supports 1, 32 or 80 (#error otherwise, issue 1 crashes on 256 cores); uses kallsyms_lookup_name so it does not build on kernel 5.7+; README cache example says 4GB but means 4MB; LICENCE is LGPL-2.1 while MODULE_LICENSE says GPL. The headline 11.8x needs out-of-tree SPF kernel patches.

## Caveats and trade-offs

Paper (usenix.org) egress-blocked; numbers from WebSearch snippets of the abstract, not an opened page. Repo README has no numbers, only the citation. The 11.8x figure is on null_blk (an in-memory null block device), not real storage; 5.27x is on Optane SSD. Kernel module for Linux 4.14 only; last commit 2021-09-29. Peer-reviewed, so a paper-access retier could raise it to B.

Runs only on Linux 4.14 kernel module build; needs reserved DRAM cache size at load; unmaintained.

## Maintenance

Research prototype, stale since 2021-09-29 with two unanswered crash/scalability issues; LGPL-2.1 code is copyable, but it is tied to Linux 4.14 and is useful mainly as a design reference.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** Repo README has no numbers, only the USENIX ATC'20 citation; the peer-reviewed paper (which would justify B) could not be opened (usenix.org egress-blocked), and its abstract figures are known only from search snippets, so the record stays C until a retier opens the paper.
- **Retiered** C to B: Raised from C to B: peer-reviewed USENIX paper plus the author's PhD thesis (read via raw.githubusercontent.com/tpapagian/tpapagian.github.io/master/files/apapag_phd_thesis.pdf). Corrections from the thesis: the 11.8x (11.89x) needs out-of-tree SPF kernel patches; stock FastMap gives 3.7x/6.6x read/write at 32 threads and 4.7x/7x at 80 on null_blk. The 5.27x is Ligra BFS on DRAM-backed pmem, not Optane; Optane is 3.31x.
- **Verifier notes:** LICENCE file opened: LGPL-2.1 text with FORTH-ICS copyright header, so copyable is right. 37 stars, 18 commits, last commit 2021-09-29 (stale). Candidate for B on paper retier.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`, `hardware`, `workload`
- **Shortcomings recorded by:** peer-reviewed paper and author thesis
- **Pages the verifier opened:**
  - <https://github.com/CARV-ICS-FORTH/FastMap>
  - <https://github.com/CARV-ICS-FORTH/FastMap/commits>
  - <https://raw.githubusercontent.com/CARV-ICS-FORTH/FastMap/HEAD/README.md>
  - <https://raw.githubusercontent.com/CARV-ICS-FORTH/FastMap/HEAD/LICENCE>
- **Sources the enricher read:**
  - <https://github.com/CARV-ICS-FORTH/FastMap>
  - <https://raw.githubusercontent.com/CARV-ICS-FORTH/FastMap/HEAD/README.md>
  - <https://github.com/CARV-ICS-FORTH/FastMap/tree/main/driver>
  - <https://github.com/CARV-ICS-FORTH/FastMap/issues>
  - <https://github.com/CARV-ICS-FORTH/FastMap/issues/1>
  - <https://github.com/CARV-ICS-FORTH/FastMap/issues/2>
  - <https://github.com/CARV-ICS-FORTH/FastMap/tree/main/tests>
  - <https://raw.githubusercontent.com/CARV-ICS-FORTH/FastMap/HEAD/driver/shared_defines.h>
  - <https://raw.githubusercontent.com/CARV-ICS-FORTH/FastMap/HEAD/driver/kernel_syms.c>
  - <https://raw.githubusercontent.com/CARV-ICS-FORTH/FastMap/HEAD/driver/main.c>
  - <https://raw.githubusercontent.com/CARV-ICS-FORTH/FastMap/HEAD/driver/mmap_buffer_hash_table.c>
  - <https://raw.githubusercontent.com/CARV-ICS-FORTH/FastMap/HEAD/scripts/load-it-fs.sh>
  - <https://raw.githubusercontent.com/CARV-ICS-FORTH/FastMap/HEAD/scripts/load-it-blkdev.sh>
  - <https://raw.githubusercontent.com/CARV-ICS-FORTH/FastMap/HEAD/Makefile>
  - <https://raw.githubusercontent.com/tpapagian/tpapagian.github.io/master/files/apapag_phd_thesis.pdf>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/carv-ics-forth/fastmap`) · [data/wave11/enrich/raw/github_com_carv_ics_forth_fastmap.json](../../../data/wave11/enrich/raw/github_com_carv_ics_forth_fastmap.json) (enrichment confidence 0.8)

</details>
