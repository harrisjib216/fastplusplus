# NUMAlloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · 🔴 abandoned

> NUMA-aware LD_PRELOAD malloc replacement, \~21% faster than glibc malloc and \~16% faster than mimalloc on 128-thread NUMA workloads.

| | |
|---|---|
| **Beats** | default Linux allocator (glibc 2.28 malloc) |
| **Claimed result** | 15.7% faster on average than the second-best allocator (mimalloc-1.6.7) and 20.9% faster than the default Linux allocator (glibc 2.28) across PARSEC, CORAL-2 OpenMP/MPI and real applications. 26.1% faster than glibc on the OpenMP/MPI apps alone. Best case fluidanimate: up to 5.3x faster than glibc, 4.8x faster than TBB and 4.6x faster than mimalloc (ISMM'23 manuscript). The earlier SC'22 draft (SC2022/evaluation.tex) reported 19.0% vs glibc, 6.8x vs Scalloc, and a Rodinia average of 2.44x vs glibc / 2.33x vs mimalloc. The Rodinia claim is commented out of the ISMM'23 manuscript. |
| **Workload** | PARSEC (native inputs), five CORAL-2 OpenMP/MPI apps (Nekbone, QMCPACK, LAMMPS, AMG, Quicksilver) and real apps (Apache httpd, MySQL, Memcached, SQLite, Aget, Pfscan, Pbzip2) at 128 threads on an 8-node NUMA machine, plus Hoard synthetic scalability tests (threadtest, larson, cache-scratch, cache-thrash) |
| **Metric** | throughput |
| **Hardware** | Intel Xeon(R) Platinum 8153, 2.00GHz, 8 NUMA nodes x 16 physical cores (128 cores total), 512GB RAM, 32KB L1/1MB L2 per core, 22MB LLC per node |
| **Compiler and flags** | GCC-8.3.0 on Linux Debian 10. The paper gives no optimization flags; the repo's source/Makefile builds the allocator with -g -O2 -std=c++14. Hyperthreading off, transparent huge pages and AutoNUMA enabled, 128 threads (= core count). |
| **Adoption** | 2 stars |
| **Last commit** | 2023-03-01 |
| **Links** | [repository](https://github.com/UTSASRG/numalloc) · [benchmark](https://raw.githubusercontent.com/UTSASRG/numalloc/master/ISMM2023/evaluation.tex) |

## Verdict

Per the ISMM'23 manuscript (source/ISMM2023/evaluation.tex, read directly): on an Intel Xeon Platinum 8153 (8 nodes x 16 cores, 512GB RAM, Debian 10, GCC-8.3.0, THP+AutoNUMA on, hyperthreading off), averaged over 30 runs at 128 threads across PARSEC, five CORAL-2 OpenMP/MPI apps, and 7 real applications, NUMAlloc was 20.9% faster than glibc-2.28's default malloc and 15.7% faster than the next-best allocator tested (mimalloc-1.6.7), also beating TCMalloc, TCMalloc-NUMA, and TBB by 18-21%; the OpenMP/MPI subset alone showed 26.1% over glibc and 16.5% over mimalloc; best case fluidanimate was 5.3x glibc and 4.6x mimalloc. A superseded SC'22 draft in the same repo reports different numbers (19.0% vs glibc) for an overlapping but not identical benchmark set.

## Use it when

- Multi-socket/multi-node NUMA Linux servers (paper: 8-node, 128-core Xeon Platinum 8153) running allocation-heavy, multi-threaded HPC or server workloads similar to PARSEC, CORAL-2 OpenMP/MPI, httpd, MySQL, or Memcached
- You can rebuild the allocator with -DNUMA_NODES=&lt;actual node count&gt; -- it's hardcoded at compile time and the shipped Makefile defaults to 2
- A plain C/C++ executable you can LD_PRELOAD, not something needing a vendored/linked allocator API
- You can pin to an old toolchain matching the paper (GCC 8.3.0, C++14, Debian 10) and, critically, a pre-2.34 glibc
- Research/reference use where you can independently validate results, not a production dependency

## Skip it when

- Any current Linux distro: an open, unmerged PR (#1, filed 2026-07-08) shows NUMAlloc infinite-recurses and crashes via an assertion the moment a second thread is created on glibc &gt;= 2.34 (Ubuntu 22.04+, Debian 12+, effectively any 2022+ distro), because its pthread_create interposition looks for a libpthread.so.0 that glibc merged into libc.so.6
- Single-socket/single-NUMA-node machines -- the whole design is cross-node locality, so on one node you likely get the \~10-12% THP memory overhead for no throughput gain
- Production or license-sensitive use -- no top-level LICENSE file; core NUMA-specific headers (pernodeheap.hh, perthreadheap.hh, interheap.hh) carry no license header at all, and files inherited from the FreeGuard project are GPL-2.0-or-later
- Need active maintenance -- last push 2023-03-01, 2 GitHub stars, and the repo is a research dump of \~10 UTSASRG projects plus a dozen near-duplicate source-\* variant folders with no indication which one produced the paper's numbers
- Serial-phase-heavy programs -- the interleaved inter-heap exists specifically to offset interleaving costs during single-threaded phases, so a program that spends most of its time before spawning threads pays extra bookkeeping for little benefit

## How it is fast

Layers a fast per-thread heap over a per-node heap tier, so the common malloc/free path never touches cross-node state; freed objects are returned to the heap tier matching the node they came from ('origin-aware' return) instead of a shared free list, keeping frees node-local under NUMA. During a program's single-threaded startup/teardown, an optional interleaved 'inter-heap' spreads allocations across all nodes to avoid one node absorbing all pre-fork memory. It's also built with transparent huge pages (-DUSE_HUGE_PAGE) to cut TLB misses on the large per-node heaps, which the ISMM'23 paper's own remote-access/TLB-miss profiling (perf) ties directly to the wins on dedup, fluidanimate, pbzip2, streamcluster and swaptions.

## Compared with alternatives

Pick NUMAlloc over SuperMalloc/Hoard/scalloc/rpmalloc/ltalloc/smmalloc only if you specifically need NUMA-node-local allocation on an 8-node-class multi-socket server, can rebuild for your topology, and are willing to fix the glibc&gt;=2.34 pthread_create crash yourself; those siblings target single-node thread-count scaling and work off the shelf today, whereas NUMAlloc is an abandoned research prototype that currently fails to launch multi-threaded programs on modern Linux.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | libnuma (-lnuma), pthread, librt, libdl -- all linked directly in source/Makefile |
| **Minimum toolchain** | C++14 (Makefile CFLAGS); shipped Makefile builds with clang++, but the paper's numbers were built with GCC-8.3.0 -O2 -std=c++14 on Debian 10 |
| **Platforms** | Linux x86-64 only -- uses inline rdtscp asm and Linux's numa.h; NUMA_NODES is a compile-time #define that must be set to match the target machine's actual node count |
| **Thread safety** | Not documented beyond source comments; relies on per-thread heaps for the fast path with locking in the shared per-node/global tiers, and the pthread_create/join/kill interposition itself is currently broken (infinite recursion) on any glibc &gt;= 2.34 system per open PR #1 |
| **Drop-in for the baseline** | partial -- explain: LD_PRELOAD replaces malloc/free/calloc/realloc transparently with zero source changes, but it also interposes pthread_create/join/kill, and that interposition unconditionally crashes multi-threaded programs on glibc &gt;= 2.34 as of this writing, so it is only a working drop-in on older glibc |

## Gotchas

- Open, unmerged PR #1 (2026-07-08): pthread_create resolves to the library's own wrapper instead of the real symbol on glibc &gt;= 2.34, causing infinite self-recursion and an assertion crash on the second thread spawned under LD_PRELOAD; the author confirms the same bug exists in all \~12 source-\* copies in the repo
- NUMA_NODES is a compile-time constant (Makefile default 2, paper implies 8) -- building for the wrong node count is a silent topology mismatch, not a runtime-detected error
- Heap is placed at a fixed virtual address (0x100000000000) rather than obtained from mmap(NULL, ...), which can collide with sanitizers or other tools that reserve that address range
- About 10-12% higher RSS than glibc from transparent-huge-page use; drops to roughly glibc-comparable memory use with THP disabled (dropping -DUSE_HUGE_PAGE), per the input record's tradeoffs

## Caveats and trade-offs

No top-level LICENSE. Some source files (e.g. libnumalloc.cpp, inherited from FreeGuard) carry GPL-2.0-or-later headers, but most NUMA-specific files (pernodeheap, perthreadheap, interheap) have no license header, so the license is unclear (usability=reference). The repo bundles sources and paper drafts for about 10 UTSASRG projects plus many source-\* variant folders, and source/Makefile is configured for NUMA_NODES=2, so which build produced the paper numbers is not obvious. The original benchmark_url was an unpublished SC'22 draft whose numbers differ from the later ISMM'23 manuscript (19.0% vs 20.9% over glibc; Rodinia claim dropped). The draft also contradicts itself on fluidanimate (5.3x vs 2.9x over glibc). Last push 2023-03-01 (&gt;3 years ago): abandoned.

About 10-12% higher memory footprint than the default allocator due to transparent-huge-page use (drops to comparable with THP disabled); designed around NUMA-aware node/thread binding, so benefits are largest on multi-socket/multi-node machines and smaller on single-socket systems; needs origin-aware object return and an interleaved heap that can hurt serial-phase-heavy applications.

## Maintenance

Abandoned since its last push on 2023-03-01 (2 GitHub stars) and usability is 'reference' only -- no top-level LICENSE, several core headers unlicensed, GPL-2.0-or-later on FreeGuard-derived files, and an unresolved crash-on-second-thread bug on any glibc &gt;= 2.34 system as of this writing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now B.
- **Tier reason:** The allocator source is public (source/) and GCC-8.3.0 plus the Xeon Platinum 8153 CPU are stated. But no optimization flags are given for the benchmarks, and the PARSEC/CORAL-2/Rodinia harness is not in the repo, so it is not A. The work was published peer-reviewed at ISMM 2023 (DOI 10.1145/3591195.3595276, confirmed via Crossref), so it is B.
- **Verifier notes:** The numbers in the original record do appear verbatim in SC2022/evaluation.tex, but that is a pre-publication draft. The peer-reviewed venue is ISMM 2023, so benchmark_url and claimed_speedup were re-pointed to the ISMM2023 manuscript in the repo; the published ACM text itself was not opened. Downgraded from A to B because the paper states no compile flags and the repo has no benchmark harness.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/UTSASRG/numalloc/master/SC2022/evaluation.tex>
  - <https://raw.githubusercontent.com/UTSASRG/numalloc/master/ISMM2023/evaluation.tex>
  - <https://github.com/UTSASRG/numalloc>
  - <https://github.com/UTSASRG/numalloc/blob/master/README.md>
  - <https://github.com/UTSASRG/numalloc/blob/master/source/Makefile>
  - <https://github.com/UTSASRG/numalloc/blob/master/source/libnumalloc.cpp>
  - <https://api.crossref.org/works?query.bibliographic=NUMAlloc+A+Faster+NUMA+Memory+Allocator&rows=3>
  - <https://dblp.org/search?q=NUMAlloc>
- **Sources the enricher read:**
  - <https://github.com/UTSASRG/numalloc>
  - <https://github.com/UTSASRG/numalloc/blob/master/README.md>
  - <https://github.com/UTSASRG/numalloc/blob/master/source/Makefile>
  - <https://github.com/UTSASRG/numalloc/blob/master/source/libnumalloc.cpp>
  - <https://github.com/UTSASRG/numalloc/blob/master/source/xdefines.hh>
  - <https://github.com/UTSASRG/numalloc/blob/master/source/numaheap.hh>
  - <https://github.com/UTSASRG/numalloc/pulls>
  - <https://github.com/UTSASRG/numalloc/pull/1>
  - <https://github.com/UTSASRG/numalloc/releases>
  - <https://raw.githubusercontent.com/UTSASRG/numalloc/master/ISMM2023/evaluation.tex>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/utsasrg/numalloc`) · [data/wave1/enrich/raw/github_com_utsasrg_numalloc.json](../../../data/wave1/enrich/raw/github_com_utsasrg_numalloc.json) (enrichment confidence 0.78)

</details>
