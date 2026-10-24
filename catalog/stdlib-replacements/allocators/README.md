# Allocators

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::allocator, operator new/delete, std::pmr  
**18 entries:** 4 tier A · 4 tier B · 9 tier C · 1 tier D · 16 copyable, 2 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**mimalloc**](microsoft-mimalloc.md) | General-purpose malloc drop-in replacement using sharded per-thread free lists; beats jemalloc/tcmalloc on multi-threaded workloads. | **A** | C | MIT | 🟢 active |
| 2 | [**metapool**](esterlein-metapool.md) | Header-only, TLS pool allocator with compile-time size classes; up to 1380x faster reserve() than std::vector, 3.6x vs pmr::vector. | **A** | C++ | MIT | 🟢 active |
| 3 | [**arena-allocator (yaroslavaristov)**](yaroslavaristov-arena-allocator.md) | Bump-pointer mmap arena for single-threaded HFT hot paths; O(1) allocate/reset, 10x-27x faster than malloc/free. | **A** | C++ | MIT | 🟢 active |
| 4 | [**SuperMalloc**](kuszmaul-supermalloc.md) | Research malloc(3) replacement using 2MiB virtual-memory superblocks and optional Haswell HTM; beats DLmalloc/JEmalloc/Hoard/TBBmalloc. | **A** | C++ | MIT OR GPL-3.0-or-later | 🔴 abandoned |
| 5 | [**snmalloc**](microsoft-snmalloc.md) | Header-only C++ allocator using lock-free message-passing frees, beating glibc malloc on cross-thread and batch-deallocation workloads. | **B** | C++ | MIT | 🟢 active |
| 6 | [**Hoard**](emeryberger-hoard.md) | Drop-in multithreaded malloc replacement beating Solaris/Ptmalloc via per-processor heaps and bounded blowup. | **B** | C++ | Apache-2.0 | 🟢 active |
| 7 | [**scalloc**](cksystemsgroup-scalloc.md) | Multicore-scalable, low-fragmentation malloc replacement beating ptmalloc2; drop-in via LD_PRELOAD, rewritten since its OOPSLA'15 paper. | **B** | C++ | BSD-2-Clause | 🟡 stale |
| 8 | [**NUMAlloc**](utsasrg-numalloc.md) | NUMA-aware LD_PRELOAD malloc replacement, \~21% faster than glibc malloc and \~16% faster than mimalloc on 128-thread NUMA workloads. | **B** | C++ | no license (study only) | 🔴 abandoned |
| 9 | [**jemalloc**](jemalloc-jemalloc.md) | General-purpose malloc(3) with per-thread arenas and decay-based purging; beats FreeBSD's phkmalloc under concurrency. | **C** | C | BSD-2-Clause | 🟢 active |
| 10 | [**gperftools TCMalloc**](gperftools-gperftools.md) | Thread-caching malloc replacement for glibc's ptmalloc2; per-thread free lists cut lock contention and per-call cost. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 11 | [**rpmalloc**](mjansson-rpmalloc.md) | Lock-free, per-thread-caching malloc replacement for C/C++, drop-in via LD_PRELOAD or override, faster than glibc/tcmalloc/jemalloc under threaded churn. | **C** | C | MIT | 🟢 active |
| 12 | [**ltalloc**](r-lyeh-archived-ltalloc.md) | Single-file source drop-in overriding operator new/delete; thread-local free lists speed up many small (&lt;256B) allocations vs CRT malloc. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 13 | [**fastcpp::arena (developer source)**](private-developer-source-allocators.md) | Header-only bump/arena allocator for same-lifetime objects; 5.4x faster than glibc new/delete when a whole batch is freed at once. | **C** | C++ | MIT | 🟢 active |
| 14 | [**smmalloc**](sergeymakeev-smmalloc.md) | Lock-free, thread-cached proxy allocator for small (16-992B) game allocations; passes everything else through to CRT malloc. | **C** | C++ | MIT | 🟡 stale |
| 15 | [**Lockless Memory Allocator**](locklessinc-com.md) | Abandoned GPL x86 malloc replacement (per-thread slabs, lock-free remote frees); 1.15-1.48x faster than glibc malloc in Ruby tests. | **C** | C | GPL-3.0-or-later | 🔴 abandoned |
| 16 | [**FreeGuard**](utsasrg-freeguard.md) | Research secure malloc (CCS 2017) with near-glibc speed, far faster than the DieHarder and OpenBSD secure allocators. | **C** | C++ | GPL-2.0 | 🔴 abandoned |
| 17 | [**arena-allocator (ShortAlloc)**](shantanu-arena-allocator.md) | Single-file bump-pointer arena allocator with an STL-compatible wrapper; beats glibc malloc via std::vector, especially above the mmap threshold. | **C** | C++ | no license (study only) | 🟡 stale |
| 18 | [**TCMalloc (google/tcmalloc)**](google-tcmalloc.md) | Google's per-CPU-cache C/C++ allocator, positioned as a faster-at-scale alternative to glibc malloc, though unquantified in the repo. | **D** | C++ | Apache-2.0 | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
