# NVthreads

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C/C++` · `GPL-2.0` · 🔴 abandoned

> pthreads replacement that makes lock-based C/C++ programs crash-consistent on NVM; beats Atlas and Mnemosyne, slower than pthreads.

| | |
|---|---|
| **Beats** | Atlas (HP persistent-memory failure-atomic-section library) and Mnemosyne (word-level STM persistent memory); plain pthreads is faster than NVthreads |
| **Claimed result** | EuroSys 2017 paper: 'NVthreads is 2x-10x faster than Mnemosyne and more than 2x faster than Atlas'; 'in 10 out of the 12 workloads on which Atlas ran, NVthreads is from 7% to 100x faster depending upon the workload' (about 7% and 50% slower than Atlas on streamcluster and reverse index); microbenchmark 'NVthreads is 3x-30x faster than these systems' (Mnemosyne and Atlas 70x to over 200x slower than pthreads, NVthreads 25x down to 5x slower). PageRank on the Slashdot graph at 12 cores: 170 ms per iteration vs 500 ms Atlas (about 2.9x, derived from page data) and 5 s Mnemosyne (about 29x, derived from page data; the paper's prose says '10x faster than Mnemosyne'); LiveJournal: 5 s vs 29 s for Atlas, 'almost 6x faster', while the pthreads version takes under 1 s per iteration. Against plain pthreads NVthreads is slower: 9 of 14 apps under 28% overhead, but reverse index (5.5x), canneal (4.1x), dedup (6.7x) and ferret (4.8x) are over 4x. |
| **Workload** | Making multi-threaded programs durable on emulated NVM (modified tmpfs on DRAM adding a 1,000 ns delay to each 4 KB page write): 14 Phoenix and PARSEC benchmarks with 12 threads against pthreads, DThreads and Atlas (Atlas could not run canneal or dedup); a microbenchmark that allocates 1000 pages (4 MB) and has 4 threads modify a random fraction (5%-100%) of each page, against Atlas and Mnemosyne; PageRank on the Slashdot graph (82K vertices, 950K edges) against Atlas and Mnemosyne, and on the 1.2 GB LiveJournal graph against Atlas only (Mnemosyne could not run it). |
| **Metric** | throughput |
| **Hardware** | Two Intel Xeon X5650 (12 cores at 2.67 GHz), 198 GB RAM, 600 GB SSD, Ubuntu 14.04 (Linux 3.16.7); NVM emulated with a modified tmpfs on DRAM adding 1000 ns per 4 KB page write |
| **Compiler and flags** | Not stated in the paper; the library's src/Makefile builds with g++ -g -m64 -msse2 -O3 -DNDEBUG -shared -fPIC -DLOCK_OWNERSHIP -DDETERM_MEMORY_ALLOC (compiler version unstated). |
| **Adoption** | 27 stars; EuroSys 2017 paper (doi 10.1145/3064176.3064204) |
| **Last commit** | 2017-08-02 |
| **Links** | [repository](https://github.com/HewlettPackard/nvthreads) · [benchmark](https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/doc/nvthreads-eurosys.pdf) |

## Verdict

The EuroSys 2017 paper (doc/nvthreads-eurosys.pdf) runs 12 threads on two Xeon X5650s (Ubuntu 14.04, Linux 3.16.7) with NVM emulated by a delay-injecting tmpfs: NVthreads beats Atlas by 7% to 100x on 10 of the 12 PARSEC/Phoenix apps Atlas could run (it is 7% and 50% slower on streamcluster and reverse_index), is 3x-30x faster than Atlas and Mnemosyne on a 4 MB page-modification microbenchmark, and runs a Slashdot PageRank iteration in 170 ms vs 500 ms (Atlas) and 5 s (Mnemosyne) and a LiveJournal iteration in 5 s vs 29 s (Atlas), while plain pthreads stays faster everywhere but linear_regression. The benchmark apps were built with gcc -march=core2 -mtune=core2 -O5 -g (eval/Default.mk; compiler version unstated), and the Atlas comparison credits NVthreads with an assumed clflushopt cost the test CPU lacked.

## Use it when

- Research or prototyping on persistent memory: making an existing lock-based pthreads program crash-consistent with almost no code changes.
- Iterative batch computations (k-means, PageRank) where resuming from the last completed critical section after a crash saves hours; the paper reports 1.4x-1.9x faster convergence after late crashes in k-means.
- Workloads that synchronize rarely and dirty few pages: the paper's Phoenix apps other than reverse_index logged 27 to about 12K dirty pages and ran at 1.1x-1.5x of pthreads.
- Comparing against fine-grained persistence systems (Atlas, Mnemosyne) on page-dense write patterns, where page-granularity logging amortizes best.

## Skip it when

- Any program that needs speed over plain pthreads: it is always slower except linear_regression (0.3x, false sharing removed), and 4.1x-6.7x slower on canneal, ferret, reverse_index and dedup, with canneal not scaling at all.
- Lock-free code, atomics, reader-writer locks, spinlocks or semaphores: the paper says lock-free structures are unsupported and libdthread.cpp intercepts none of rwlock, spinlock or sem_\* calls.
- Programs that write a few bytes per page across many pages, or synchronize very often: each lock release writes a full 4 KB page image per dirty page (logs reached 11 GB for reverse_index and 29 GB for canneal with truncation disabled).
- Production or modern NVM: the README calls it a research prototype not to be deployed in production, it predates real Optane/CXL persistent memory, and the emulated-NVM file system (dummy_nvmfs) targets Linux 3.16.7.
- Projects that cannot accept GPL-2.0 for a library that replaces pthreads at link time.

## How it is fast

It reuses the DThreads design: threads run as processes with copy-on-write private pages (mprotect plus a page-fault handler tracks dirty 4 KB pages), so no individual store is instrumented and uncommitted writes never reach shared memory, which removes the need for an undo log. At each lock release the dirty pages are written as whole-page redo-log entries plus an end-of-log marker and made durable with fdatasync, then diffs are merged into shared state; application data itself is never force-flushed (no-force, like ARIES), and only the log is ordered. Per-mutex tokens replace DThreads' single global token for some workloads, and dependence tracking between nested critical sections delays log commit until the outermost lock is released.

## Compared with alternatives

None of the catalogued thread-pool siblings (citor, Fork Union, Taskflow-style schedulers, Weave) offer crash consistency, and all of them aim to beat a scheduler on speed; pick NVthreads only when the requirement is durability of a lock-based pthreads program on persistent memory and a 1.1x to 6.7x slowdown over pthreads is acceptable.

## Integration

| | |
|---|---|
| **Form** | shared lib (libnvthread.so / libnvthread32.so built by src/Makefile; link or preload in place of libpthread) |
| **Dependencies** | libdl and libpthread; g++ with multilib for the 32-bit build; a file system mounted at /mnt/ramdisk with /mnt/ramdisk/nvthreads (the dummy_nvmfs kernel module adds emulated NVM delays; a plain directory works without delays); crash state kept in /tmp/nvlib.crash |
| **Minimum toolchain** | g++ (version not documented); src/Makefile builds with -g -m64 -msse2 -O3 -DNDEBUG -fPIC -DLOCK_OWNERSHIP -DDETERM_MEMORY_ALLOC |
| **Platforms** | Linux x86-64 and x86-32 only (clone-based processes, mprotect page tracking, x86 inline assembly); dummy_nvmfs for Linux 3.16.7 |
| **Thread safety** | It is the threading layer: shared heap data must be protected by mutexes, and updates become visible to other threads only at synchronization points (DThreads-style isolation), so racy code behaves differently than under pthreads |
| **Drop-in for the baseline** | partial — it links in place of pthreads for lock-based programs without code changes, but recovery needs nvmalloc/nvrecover calls, and it shares no API with Atlas or Mnemosyne |

## Gotchas

- Harness flaw behind the Atlas comparison: NVthreads' durability cost is an injected 1,000 ns per write() call on a DRAM tmpfs (mknvmfs1000 mounts wr_delay_ns_fixed=1000, wr_delay_ns_per_kb=0, and fdatasync on that file system is the only flush), a figure the paper derives by assuming clflushopt is 8x cheaper than its own 6,400 ns clflush-per-page estimate; the Xeon X5650 test machine has no clflushopt, and Atlas on the same machine paid real clflush costs (half its overhead, per the paper). The paper's own Figure 11 shows the five write-heavy apps degrading once the page-write delay passes about 1 us, so the 'faster than Atlas' margins depend on hardware the test box did not have.
- Paper and repository inconsistencies: the text says 9 of 14 apps run under 28% overhead, but its Table 2 lists only 8 at 1.2x or below (kmeans is 1.5x and streamcluster 3.7x); only reverse_index and canneal used the per-mutex-token build, so the per-app numbers mix two library variants; the Atlas-ported PARSEC/Phoenix sources that eval/eval-atlas.py runs live at a private path (/mnt/ssd/terry/workspace/Atlas-github/multicore-tests/...), and the third-parties/ directory the README and eval/Default.mk reference is not in the repository, so the Atlas and DThreads columns cannot be rebuilt from it.
- Only heap memory obtained through the intercepted malloc is logged (the commit path logs only when _isHeap), globals are not persisted, and pointers inside recovered objects are not relocated: issue #3 reports st1-&gt;next dereferences failing after recovery, so each linked object needs its own named nvmalloc/nvrecover.
- Open issue #4 (2018): three threads contending for one mutex can hang with probability high enough to notice, spinning at 100% CPU waiting for the token in xrun.h. Other rough edges: pthread_kill is unsupported, sched_yield is a no-op, pthread_attr settings are ignored, the 64-bit protected heap is fixed at 8 GB and globals at 40 MB, ReadConfig returns before reading /tmp/nvthread.config so the log path is hard-coded, and a stale /tmp/nvlib.crash makes the next run take the recovery path.

## Known shortcomings

- EuroSys 2017 paper (PDF in the repo): baselines are Mnemosyne and Atlas (off-list) on emulated NVM, and NVthreads is slower than pthreads (over 4x on 4 apps, about 5x on LiveJournal); the paper's prose says 10x over Mnemosyne on Slashdot while its own 170 ms vs 5 s gives 29x; LiveJournal PageRank is vs Atlas only; no compiler given. GPL-2.0; abandoned 2017-08-02.
- Enricher: NVthreads' flush cost is a fixed 1,000 ns injected per write() on tmpfs (mknvmfs1000), justified by assuming clflushopt, which the Xeon X5650 used lacks, while Atlas paid real clflush on the same machine; the paper says 9 of 14 apps are under 28% overhead but its Table 2 shows 8 (kmeans 1.5x) and per-app numbers mix two builds. The third-parties/ directory is absent from the repo and the Atlas-ported benchmarks sit at a private path; app flags are gcc -march=core2 -O5 -g (eval/Default.mk). Only the heap is logged; issue #4 (token-wait hang at 100% CPU) and #3 (recovered pointers not relocated) open; no rwlock, spin or semaphore interception.

## Caveats and trade-offs

The baselines are other research persistence systems (Atlas, Mnemosyne), not std::thread or pthreads; NVthreads is slower than unmodified pthreads (over 4x on four PARSEC/Phoenix apps, about 5x on LiveJournal PageRank), so it is not faster than the category incumbent. NVM is emulated with software delays; Atlas could not run canneal and dedup, Mnemosyne ran only the microbenchmark and the small Slashdot PageRank graph (it crashes above 4 MB of durable data), and Mnemosyne's constant 2 s fork/pmalloc overhead was excluded. The paper's prose ratio for Mnemosyne on Slashdot (10x) does not match its own 170 ms vs 5 s figures (about 29x). Compiler flags for the benchmark applications are not stated in the paper. The root COPYING is GPL-2.0 (copyleft for a drop-in pthreads replacement) while the awesome-cpp listing says LGPL-2.1, and third-parties/ vendors Atlas, Mnemosyne and DThreads under their own licenses. The README calls it a research prototype under development, not for production. Category thread-pools-work-stealing is the closest wave-11 fit; the project is really persistent-memory threading.

Drop-in pthreads replacement that adds persistence: Dthreads-style multi-process execution with copy-on-write page buffering, page-granularity redo logs and recovery; overhead versus plain pthreads is 20 to 28% on easy workloads and over 4x on others; needs an NVM filesystem; research prototype ('use at your own risk'); log space 165 MB to 300 MB versus 550 MB-3.2 GB for Mnemosyne in the microbenchmark.

## Maintenance

Abandoned research prototype (last commit 2017-08-02, two open issues including a token-wait hang), GPL-2.0, x86 Linux only; its wins over Atlas and Mnemosyne rest on an emulated 1 us page-write cost that assumes clflushopt the test CPU lacked, so read it as a design reference for page-granularity redo logging rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed EuroSys 2017 paper (checked into the repo as doc/nvthreads-eurosys.pdf) compares NVthreads with Atlas and Mnemosyne on stated hardware (2x Xeon X5650, Ubuntu 14.04, Linux 3.16.7), and the eval/ and apps/ code is public, but the paper states no compiler version or flags, so it falls short of A.
- **Verifier notes:** All quoted figures appear in the paper PDF; small fixes: LiveJournal PageRank was against Atlas only, and the paper's prose says 10x (not the derived 29x) over Mnemosyne on Slashdot. Keep at B with shortcomings: off-baseline (research systems, not pthreads), slower than pthreads, emulated NVM, GPL-2.0, abandoned since 2017-08-02.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** EuroSys 2017 paper (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/doc/nvthreads-eurosys.pdf>
  - <https://github.com/HewlettPackard/nvthreads>
  - <https://github.com/HewlettPackard/nvthreads/commits/master>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/COPYING>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/HewlettPackard/nvthreads>
  - <https://github.com/HewlettPackard/nvthreads/tree/master>
  - <https://github.com/HewlettPackard/nvthreads/commits/master>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/README.md>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/COPYING>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/doc/nvthreads-eurosys.pdf>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/mknvmfs1000>
  - <https://github.com/HewlettPackard/nvthreads/tree/master/src>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/include/logger.h>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/include/xpersist.h>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/include/xdefines.h>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/include/xrun.h>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/include/nvrecovery.h>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/source/libdthread.cpp>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/source/logger.cpp>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/source/nvrecovery.cpp>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/src/source/xthread.cpp>
  - <https://github.com/HewlettPackard/nvthreads/tree/master/eval>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/eval/Default.mk>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/eval/eval-atlas.py>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/eval/README>
  - <https://raw.githubusercontent.com/HewlettPackard/nvthreads/HEAD/eval/README_fix.txt>
  - <https://github.com/HewlettPackard/nvthreads/tree/master/third-parties>
  - <https://github.com/HewlettPackard/nvthreads/tree/master/tests>
  - <https://github.com/HewlettPackard/nvthreads/tree/master/tests/atlas>
  - <https://github.com/HewlettPackard/nvthreads/tree/master/apps>
  - <https://github.com/HewlettPackard/nvthreads/tree/master/apps/pagerank>
  - <https://github.com/HewlettPackard/nvthreads/issues?q=is%3Aissue>
  - <https://github.com/HewlettPackard/nvthreads/issues/3>
  - <https://github.com/HewlettPackard/nvthreads/issues/4>
  - <https://github.com/HewlettPackard/dummy_nvmfs>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/hewlettpackard/nvthreads`) · [data/wave11/enrich/raw/github_com_hewlettpackard_nvthreads.json](../../../data/wave11/enrich/raw/github_com_hewlettpackard_nvthreads.json) (enrichment confidence 0.8)

</details>
