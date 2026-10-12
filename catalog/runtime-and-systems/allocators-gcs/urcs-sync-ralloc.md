# Ralloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Lock-free recoverable persistent-memory malloc (LRMalloc-based); about 10x faster than PMDK libpmemobj and Makalu on allocator microbenchmarks.

| | |
|---|---|
| **Beats** | PMDK libpmemobj, Makalu |
| **Claimed result** | ISMM 2020 paper (search snippet): about 10x faster than Makalu and PMDK on Threadtest and Shbench, up to 37x faster than Makalu on Larson. Repo CSVs (derived from page data): Threadtest 1 thread 28.7 s vs Makalu 298 s, PMDK 1690 s, jemalloc 38.4 s; 40 threads 2.31 s vs Makalu 52.2 s, PMDK 118 s; Larson 88 threads 4.8e8 ops vs Makalu 1.27e7, PMDK 6.46e6, jemalloc 5.2e8. |
| **Workload** | Threadtest, Shbench, Larson and other allocator microbenchmarks on persistent memory, recoverable lock-free allocator built on LRMalloc. |
| **Metric** | throughput |
| **Adoption** | 48 stars |
| **Last commit** | 2020-10-23 |
| **Links** | [repository](https://github.com/urcs-sync/ralloc) · [benchmark](https://github.com/urcs-sync/ralloc/tree/master/data) |

## Verdict

The ISMM 2020 paper (seen via search snippet, PDF blocked here) reports about 10x over Makalu and PMDK on Threadtest and Shbench and up to 37x over Makalu on Larson; the repo's own CSVs agree (Threadtest 1 thread 28.7 s vs Makalu 298 s and PMDK 1690 s; Larson 88 threads 4.8e8 ops vs Makalu 1.27e7, derived from page data), built with GCC -O3 per test/Makefile, CPU model not stated in the repo.

## Use it when

- Persistent-memory data structures (lock-free queues, maps, trees) that need a non-blocking, crash-recoverable allocator under many threads
- Replacing PMDK libpmemobj or Makalu allocation in a research or prototype system where allocation rate is the bottleneck
- Small-object workloads: blocks up to about 14 KiB come from size classes (MAX_SZ = 8 KiB + 3 x 2 KiB in pm_config.hpp)
- Systems that can tolerate a GC pass at restart in exchange for no per-allocation logging during normal operation
- Emulated persistence on DRAM (/dev/shm) for testing persistent algorithms on machines without NVM

## Skip it when

- Ordinary transient heaps: the repo CSVs show it on par with jemalloc at low thread counts and 2-3x slower on Threadtest and Shbench above 48 threads
- You need failure-atomic transactions over your own data (PMDK's tx API); Ralloc only keeps allocator metadata consistent
- Production use: abandoned since 2020-10-23, open bug #12 on restart with /dev/shm, open issue #15 (only one Ralloc instance per application) and #16 (redundant concurrent heap expansion)
- Pure C programs that need precise recovery: the README warns filter functions are not supported in pure C, leaving only conservative GC
- Very high thread counts with the bundled LRMalloc build: hazard counter overflow and segfaults reported above about 72 threads (README warning)

## How it is fast

It reuses LRMalloc's lock-free design (thread-local caches of size-class blocks, 64 KiB superblocks with CAS-updated anchors) and persists only what cannot be rebuilt (superblock descriptors and roots) with clwb/clflush plus fences, keeping free lists and thread caches transient. Instead of logging every allocation like PMDK, recovery after a crash runs a mark-and-sweep garbage collection from the persistent roots, conservative by default or guided by user-supplied filter functions, to reconstruct free lists. Position-independent offset pointers let the heap be remapped at a different address on restart.

## Compared with alternatives

No catalogued sibling targets persistent memory; pick Ralloc only when allocations must survive crashes, and pick mimalloc-class allocators such as those in this category (SpeedMalloc, v8malloc, Mesh) for ordinary transient heaps, where Ralloc trails jemalloc at high thread counts.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | libjemalloc (necessary per README, used for transient allocations), pthread, libatomic; PMDK and Makalu only to run the comparison benchmarks |
| **Minimum toolchain** | GCC with C++11 (Makefile builds with -O3 -fpermissive) |
| **Platforms** | Linux x86-64 (clwb/clflush inline asm, MAP_SYNC DAX mapping at /mnt/pmem or /dev/shm emulation) |
| **Thread safety** | Lock-free and thread-safe; threads should be created through RP_pthread_create (pm_thread_create) so thread caches are handled |
| **Drop-in for the baseline** | partial - malloc-like RP_\* calls replace pmemobj_alloc/Makalu allocation, but roots, recovery and filter functions differ and PMDK transactions have no equivalent |

## Gotchas

- The heap path is compiled in: without SHM_SIMULATING files go to /mnt/pmem/ (edit src/pm_config.hpp for another mount); RP_init defaults to a 5 GiB heap and regions grow in 1 GiB steps
- Pointers stored in the persistent heap must be reachable from RP_set_root roots or they are reclaimed by the recovery GC after a crash
- Conservative recovery treats any word that looks like a heap pointer as live, so it can leak blocks; precise filter functions are C++ only
- The benchmark 'lr' build is Ralloc with -DPWB_IS_NOOP (no flushes or fences), not upstream LRMalloc; read the repo CSV labels with that in mind

## Known shortcomings

- Slower than jemalloc above 48 threads (transient use); abandoned since 2020. Open bugs: 12 (restart with /dev/shm), 15 (single instance only) and 16 (heap over-expansion). The repo's 'lr' baseline is Ralloc built with -DPWB_IS_NOOP, not upstream LRMalloc; the Makefile uses -O3 GCC and the CPU is still unknown.

## Caveats and trade-offs

Baselines are persistent-memory allocators (Makalu, PMDK libpmemobj); against transient jemalloc it is roughly on par at low thread counts and 2-3x slower on Threadtest and Shbench above 48 threads (repo CSVs). Paper PDF blocked here; claim cross-checked against repo data/\*.csv only. Bundled LRMalloc hazard counter can overflow above \~72 threads (README warning). Last commit 2020-10-23.

Requires persistent memory or DRAM simulation via /dev/shm; C++11; needs filter functions for recovery, not supported in pure C; LRMalloc counter may overflow above 72 threads.

## Maintenance

Abandoned research code (last commit 2020-10-23, open restart bug #12) but MIT-licensed and small enough to vendor for persistent-memory prototypes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** ISMM 2020 peer-reviewed paper (PDF blocked; claim seen in search snippet), and the repo's own result CSVs under data/{threadtest,shbench,larson}/ with the benchmark code in test/ corroborate it: threadtest 28.7 s vs Makalu 298 s and PMDK 1690 s at 1 thread, Larson 4.8e8 vs Makalu 1.27e7 ops at 88 threads (about 37x, derived from page data). Compiler flags and CPU model not seen, so not A.
- **Verifier notes:** MIT LICENSE confirmed; 48 stars, 13 forks, last commit 2020-10-23 (abandoned). Repo data independently supports the paper's ratios.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** peer-reviewed paper and repo CSVs
- **Pages the verifier opened:**
  - <https://github.com/urcs-sync/ralloc/tree/master/data>
  - <https://github.com/urcs-sync/ralloc/tree/master/data/threadtest>
  - <https://github.com/urcs-sync/ralloc/commits>
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/data/threadtest/threadtest_r.csv>
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/data/larson/larson_r.csv>
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/data/shbench/shbench_r.csv>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/src/ralloc.hpp>
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/src/BaseMeta.hpp>
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/src/pm_config.hpp>
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/src/pfence_util.h>
  - <https://raw.githubusercontent.com/urcs-sync/ralloc/HEAD/test/Makefile>
  - <https://github.com/urcs-sync/ralloc/issues?q=is%3Aissue>
  - <https://github.com/urcs-sync/ralloc/issues/16>
  - <https://github.com/urcs-sync/ralloc/issues/17>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/urcs-sync/ralloc`) · [data/wave11/enrich/raw/github_com_urcs_sync_ralloc.json](../../../data/wave11/enrich/raw/github_com_urcs_sync_ralloc.json) (enrichment confidence 0.7)

</details>
