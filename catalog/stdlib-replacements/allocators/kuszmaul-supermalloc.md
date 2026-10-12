# SuperMalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT OR GPL-3.0-or-later` · 🔴 abandoned

> Research malloc(3) replacement using 2MiB virtual-memory superblocks and optional Haswell HTM; beats DLmalloc/JEmalloc/Hoard/TBBmalloc.

| | |
|---|---|
| **Beats** | best of DLmalloc, JEmalloc, Hoard, and TBBmalloc |
| **Claimed result** | \~2.1x faster than the best of DLmalloc/JEmalloc/Hoard/TBBmalloc with 1 thread; 2.75x faster with 8 threads + HTM; 3.4x faster with 32 threads (no HTM) |
| **Workload** | malloc-test multithreaded allocate/free microbenchmark at 1, 8 (with hardware transactional memory), and 32 threads on 64-bit Linux |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-4770 (Haswell-DT, 4 cores / 8 HW threads, 3.4GHz, 1 socket) for the HTM results; 2-socket 16-core Intel Xeon E5-2665 (Sandy Bridge, 2.4GHz, 32 HW threads) for the non-HTM 32-thread results |
| **Compiler and flags** | gcc 4.8.3 on Linux 3.15.7 / glibc 2.18 (Fedora 20), per the paper. Release build flags -O3 -flto -pthread -fPIC, plus -mrtm for the HTM build (release/Makefile, Makefile.include). Compared against Hoard 3.10, jemalloc 3.6.0, tbb43_20140724 and DLmalloc 2.8.6. |
| **Adoption** | 292 stars |
| **Last commit** | 2017-10-25 |
| **Links** | [repository](https://github.com/kuszmaul/SuperMalloc) · [benchmark](https://raw.githubusercontent.com/kuszmaul/SuperMalloc/master/paper/ismm15/supermalloc.tex) |

## Verdict

On the author's malloc-test multithreaded allocate/free microbenchmark (ISMM'15 paper, gcc 4.8.3 -O3 -flto on Fedora 20/glibc 2.18), SuperMalloc reached \~2.1x the throughput of the best of DLmalloc 2.8.6, JEmalloc 3.6.0, Hoard 3.10, and TBBmalloc tbb43_20140724 at 1 thread; 2.75x at 8 threads using Haswell HTM on a Core i7-4770; and 3.4x at 32 threads without HTM on a 2-socket Xeon E5-2665.

## Use it when

- Reproducing or extending the ISMM'15 malloc-test throughput results on period-matched hardware/toolchain (Haswell+ with TSX, gcc 4.8.3-class compiler)
- Research into HTM-assisted allocator design or virtual-address-space-heavy (superblock/chunk) allocator layouts
- Workloads shaped like malloc-test: many threads doing tight fixed-size-class allocate/free cycles
- Willing to vendor and patch a \~2015-era C++11 source drop (dual MIT/GPLv3) instead of taking a maintained package
- Have access to Haswell+ HTM for the full-speed build, or accept the pthread-lock fallback build otherwise

## Skip it when

- Need an actively maintained allocator: last commit 2017-10-25, no response to open issues since
- Need production reliability: open/closed issues report crashes under mysql and sysbench, and 'make check results in Aborted (core dumped)' on some setups
- Need 8-byte-aligned allocation support: issue #36 requesting that mode is still open, i.e. unimplemented
- No Haswell+ TSX hardware and don't want to fall back to the slower pthread-mutex build
- Need current comparisons: no head-to-head vs mimalloc/snmalloc/rpmalloc exists, only vs 2014-era DLmalloc 2.8.6/Hoard 3.10/JEmalloc 3.6.0/TBBmalloc tbb43
- Virtual address space is constrained: allocates 2MiB chunks per size class rather than tightly packing

## How it is fast

Objects are allocated from 2MiB chunks that each hold one size class; chunk-number-to-metadata lookup uses a big mostly-uncommitted array instead of a tree, and most size classes use a prime number of cache lines (plus random alignment for large objects) to avoid cache associativity conflicts. Allocation/free paths use a 3-level cache (10-object per-thread cache, a per-CPU cache sized to roughly one L2's worth of objects per size class, and a global cache), with objects moved between levels in O(1) via array/bitmap operations. Everything a critical section needs is prefetched beforehand so the section itself is short, which speeds ordinary locking and raises the commit rate of the RTM hardware-transaction path.

## Compared with alternatives

Pick SuperMalloc over the sibling allocators (NUMAlloc, Hoard, scalloc, arena/pool allocators) when the question is specifically HTM-assisted allocator design validated by an A-tier paper benchmark against DLmalloc/JEmalloc/Hoard/TBBmalloc — not for production use, where NUMAlloc (maintained, benchmarked vs glibc 2.28 and mimalloc) or Hoard (still maintained) are safer choices.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc/libdl (-ldl); vendored copies of Hoard/jemalloc/tbb exist only under other-mallocs/ for building benchmark comparisons, not for SuperMalloc itself |
| **Minimum toolchain** | C++11 (-std=c++11) / C11; needs GCC with LTO (release build uses -O3 -flto); a Makefile comment notes it does not compile with gcc 4.8.0 |
| **Platforms** | 64-bit Linux, x86-64 only; the RTM/HTM build additionally needs a Haswell+ CPU with TSX, otherwise use the libsupermalloc_pthread.so build |
| **Thread safety** | designed as a thread-safe malloc via per-thread and per-CPU caches backed by either RTM hardware transactions or pthread-mutex-protected shared structures; no separate documented thread-safety contract beyond that |
| **Drop-in for the baseline** | true — exposes malloc/calloc/free/realloc/posix_memalign/memalign/aligned_alloc/malloc_usable_size with standard C signatures for linking or LD_PRELOAD |

## Gotchas

- Two separate shared libraries ship (HTM vs pthread); the README says a runtime auto-detect was 'planned' but was never added, so you must pick the right one yourself
- Runtime behavior is gated by undocumented env vars (SUPERMALLOC_THREADCACHE, SUPERMALLOC_TRANSACTIONS, SUPERMALLOC_PREDO) used throughout the benchmark Makefiles
- Reported crashes against real workloads: mysql (issue #23) and sysbench (issue #33)
- 8-byte-aligned allocation is requested but not implemented (issue #36, open)

## Caveats and trade-offs

The benchmark toolchain (gcc 4.8.3 / glibc 2.18 / Fedora 20) is from 2015. The last commit on any branch is 2017-10-25 (GitHub pushed_at of 2019-11-15 has no matching commit), and there is no recent head-to-head vs mimalloc/snmalloc/rpmalloc. The numbers come from the author's own malloc-test variant in the ISMM'15 paper. The paper's 'DLmalloc' is standalone Doug Lea dlmalloc 2.8.6 linked separately, not glibc's ptmalloc2-based default malloc, so glibc malloc itself was not measured. The fastest path relies on Haswell TSX/HTM; a pthread-mutex build also exists. Dual-licensed: MIT (expat) or GPLv3-or-later.

Full-speed path requires Haswell+ hardware transactional memory; ships a separate pthread-lock build (libsupermalloc_pthread.so) for machines without HTM. Uses more virtual address space via a superblock design. Author Bradley Kuszmaul's ISMM'15 paper implementation, not a maintained production allocator.

## Maintenance

Abandoned: last commit 2017-10-25 with 20 open issues including build failures on CentOS 6.5 and lto1 errors; dual MIT/GPLv3-licensed C++11 source is small enough to vendor but expect to patch around a 2015-era toolchain assumption.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The ISMM'15 paper source states gcc 4.8.3 / glibc 2.18 / Fedora 20 and the CPUs (i7-4770, Xeon E5-2665). The benchmark code is public in the same repo (tests/new-malloc-test.c, with raw data in paper/ismm15/\*.data), and release/Makefile sets -O3 -flto (-mrtm for HTM). That meets A.
- **Verifier notes:** The abstract states 2.1x / 2.75x / 3.4x over the best of DLmalloc/JEmalloc/Hoard/TBBmalloc verbatim. Metadata fixes: the license is MIT OR GPL-3.0-or-later (the GPL text says 'or any later version'), and last_commit is 2017-10-25, not 2019-11-15. compared_against_cpp_std_directly is set to false because the 'DLmalloc' baseline is standalone dlmalloc 2.8.6, not the system glibc malloc.
- **Fields the verifier corrected:** `license`, `last_commit`, `hardware`, `compiler_and_flags`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kuszmaul/SuperMalloc/master/paper/ismm15/supermalloc.tex>
  - <https://github.com/kuszmaul/SuperMalloc>
  - <https://github.com/kuszmaul/SuperMalloc/blob/master/LICENSE>
  - <https://github.com/kuszmaul/SuperMalloc/blob/master/README>
  - <https://github.com/kuszmaul/SuperMalloc/blob/master/release/Makefile>
  - <https://github.com/kuszmaul/SuperMalloc/blob/master/Makefile.include>
  - <https://github.com/kuszmaul/SuperMalloc/tree/master/tests>
  - <https://github.com/kuszmaul/SuperMalloc/tree/master/paper/ismm15>
- **Sources the enricher read:**
  - <https://github.com/kuszmaul/SuperMalloc>
  - <https://github.com/kuszmaul/SuperMalloc/tree/master>
  - <https://github.com/kuszmaul/SuperMalloc/blob/master/src/supermalloc.h>
  - <https://github.com/kuszmaul/SuperMalloc/blob/master/Makefile.include>
  - <https://github.com/kuszmaul/SuperMalloc/blob/master/release/Makefile>
  - <https://raw.githubusercontent.com/kuszmaul/SuperMalloc/master/paper/ismm15/supermalloc.tex>
  - <https://github.com/kuszmaul/SuperMalloc/blob/master/LICENSE>
  - <https://github.com/kuszmaul/SuperMalloc/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/kuszmaul/supermalloc`) · [data/wave1/enrich/raw/github_com_kuszmaul_supermalloc.json](../../../data/wave1/enrich/raw/github_com_kuszmaul_supermalloc.json) (enrichment confidence 0.8)

</details>
