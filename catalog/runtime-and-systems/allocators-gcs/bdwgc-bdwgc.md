# Boehm-Demers-Weiser GC (bdwgc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Boehm-GC` · 🟢 active

> Conservative mark-sweep garbage collector for C and C++; first-party GCBench runs beat glibc malloc/free on small-object allocation.

| | |
|---|---|
| **Beats** | glibc malloc/free |
| **Claimed result** | docs/scale.md: thread-unsafe collector 9 s vs glibc malloc/free 10.51 s (pthreads not linked), about 1.17x (derived from page data); thread-safe collector (-D GC_THREADS) 10.3 s vs glibc malloc/free 20.90 s (one thread, pthreads linked), about 2.0x (derived from page data); two clients 23.5 s vs 24.55 s, about 1.04x (derived from page data). With -D GC_THREADS -D PARALLEL_MARK -D THREAD_LOCAL_ALLOC the same page lists 1 client 10.45 s (1 marker) / 7.85 s (2 markers) and 2 clients 19.95 s / 12.3 s; against the malloc/free times that is about 2.0x for two clients with two markers (12.3 s vs 24.55 s, derived from page data), though the two-marker runs use the second CPU for marking. The page says the benchmark favors a garbage collector since most objects are small. docs/overview.md says performance is 'typically competitive' with malloc/free, that time and space overhead are 'likely to be only slightly higher' for programs written for malloc/free, that the collector may be faster for very small objects and slower for large ones, and that with thread-local allocation it 'may in some cases significantly outperform' malloc/free; no numbers there. |
| **Workload** | Author's GC benchmark (small-object allocation heavy, C variant), modified to run multiple client threads sharing one heap; elapsed seconds for the GC build versus a malloc/free variant of the same benchmark. |
| **Metric** | throughput |
| **Hardware** | Dual-processor Pentium III/500, Linux 2.2.12, ancient GC release from 2000 |
| **Compiler and flags** | Not stated for the baseline comparison (GC built with -D GC_THREADS; later table adds -D PARALLEL_MARK -D THREAD_LOCAL_ALLOC); optimization level unstated. |
| **Adoption** | 3.5k stars; packaged in many distributions (Repology badge in README) |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/bdwgc/bdwgc) · [benchmark](https://github.com/bdwgc/bdwgc/blob/master/docs/scale.md) |

## Verdict

First-party only: docs/scale.md times a multi-client variant of Boehm's GCBench (C, binary trees, mostly small objects) on a dual Pentium III/500 with Linux 2.2.12, a 2000 collector release and contemporary glibc, compiler and flags unstated: 9 s for the thread-unsafe GC against 10.51 s for malloc/free (about 1.17x), 10.3 s thread-safe against 20.90 s with pthreads linked (about 2.0x), and 12.3 s against 24.55 s for two clients with parallel mark and thread-local allocation using both CPUs (about 2.0x, derived from page data). An independent 2026 V-language issue (Ryzen 7 5800H, 64-byte allocations) measured 18.5 M against 13.0 M allocations/s for libc malloc on one thread (about 1.42x, derived from page data) but about 18 M against 32-33 M at 4-16 threads with thread-local allocation disabled in V's bundled build.

## Use it when

- Language runtimes and compilers that emit C or need a collector with easy C interop (the overview names this as a main use).
- Allocation-heavy code built from many small pointer-linked objects (trees, lists, cons cells, ASTs) where ownership is hard to track; the docs say the collector may be faster than malloc/free when objects are very small.
- Multi-threaded allocation on multi-core machines with thread-local allocation and parallel marking enabled (the CMake and autoconf defaults); scale.md shows two clients in 12.3 s against 24.55 s for malloc/free on two CPUs.
- Legacy C code with leaks or unclear ownership, either linked against libgc with malloc redirected or built in FIND_LEAK mode to report leaks.
- Large pointer-free buffers allocated with GC_MALLOC_ATOMIC, which are neither cleared nor scanned.

## Skip it when

- Programs dominated by large objects: the overview says the collector is slower than malloc/free there, and objects above about 100 KB need GC_malloc_ignore_off_page to avoid false retention.
- Latency-bound or real-time code: collections stop the world by default (the README cites about 5 ms per MB of live data on 2007 hardware), and incremental mode needs VM dirty-bit support and has its own costs (issue #681: gctest 7231 ms with incremental plus parallel mark versus 2305 ms without).
- Memory-tight deployments: a collected heap needs headroom (GC_free_space_divisor defaults to 3) and the docs expect higher space overhead than explicit malloc/free.
- Builds without thread-local allocation on many cores: every GC_malloc then takes the global allocator lock; V's bundled amalgamation (thread-local allocation off) stayed flat at about 18 M allocations/s from 4 to 16 threads while libc malloc reached about 33 M/s (vlang/v issue #27488).
- Code that hides pointers (XOR-linked lists, pointers kept only in system-malloc memory or thread-local storage, compressed or encrypted pointers) or that needs deterministic destruction.

## How it is fast

Non-moving mark-sweep (Boehm-Weiser 1988): allocation pops from segregated per-size, per-kind free lists of 8- or 16-byte granules carved from HBLKSIZE pages, and free is optional, so per-object deallocation work becomes batched collection that is cheap when most objects are small and short-lived. Sweeping is lazy (a page is swept only when an allocation finds its free list empty) and uses size-specialised unrolled sweep loops; fully empty pages go back to the block allocator after touching only headers. With THREAD_LOCAL_ALLOC each thread refills private free lists in bulk through GC_malloc_many (about one HBLKSIZE at a time) and allocates without the global allocator lock, and PARALLEL_MARK splits marking across cores with a shared work queue modelled on Endo, Taura and Yonezawa.

## Compared with alternatives

Pick bdwgc over SGCL when you need a collector for C, or for C++ without rewriting to SGCL's tracked_ptr types, on platforms beyond Apple Silicon, with decades of production use behind it; pick Mesh, IsoAlloc or another malloc replacement when you keep explicit free and want lower memory or hardening rather than automatic reclamation.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (libgc, plus optional libcord and libgccpp or libgctba for C++); a single-file amalgamation extra/gc.c also exists |
| **Dependencies** | none required; pthreads for threaded builds; libatomic_ops only where the compiler lacks atomic intrinsics (notably MSVC) |
| **Minimum toolchain** | Plain C compiler; CMake 3.10+ (recommended), autoconf/automake, Zig (experimental), nmake or Makefile.direct; gc_cpp.h has C++98, C++11, C++14 and C++17 code paths |
| **Platforms** | Flat 32- or 64-bit address spaces: Linux, Android, BSDs, macOS, iOS, Windows (Win32/Win64), Solaris, HP/UX, Tru64, Irix, OS/2 and others; dynamic-library root scanning and incremental mode are limited to some of them |
| **Thread safety** | Thread-safe in the default CMake and autoconf builds (threads, parallel mark and thread-local allocation ON); clients define GC_THREADS before including gc.h so thread creation is wrapped, or register foreign threads with GC_allow_register_threads and GC_register_my_thread. Makefile.direct's default and the one-line manual build are not thread-safe; calling GC routines from a signal handler is unsafe by default. |
| **Drop-in for the baseline** | partial: REDIRECT_MALLOC or '#define malloc(n) GC_malloc(n)' replaces malloc, but pointers stored in system-malloc memory or thread-local storage are invisible to the collector, dynamic-library data roots must be supported on the platform, and free becomes optional rather than required |

## Gotchas

- GC_malloc returns zeroed memory (calloc semantics), so it is not an apples-to-apples malloc; use GC_MALLOC_ATOMIC for pointer-free data, which is neither cleared nor scanned. Calling GC_free on very small objects (8 bytes or less) is documented as a probable performance loss.
- Parallel marking can hurt: issue #320 (Wybe) reports a single-threaded program taking 54 s on a 1-core machine and 220 s on a 12-core machine, fixed only by GC_NPROCS=1, while scale.md warns that GC_NPROCS=1 can cause a 10x slowdown for multi-threaded clients; issue #619 (open) reports a hang with GC_allow_register_threads plus parallel mark on an M1 Max.
- THREAD_LOCAL_ALLOC swaps the allocator lock to spin-then-queue, which slows the standard (non-thread-local) allocation calls; issue #453 still saw a 100-million-node linked-list build take 5.55 s on one thread and 9.21 s on two with thread-local allocation on (closed without a visible fix note).
- Benchmark harness flaw, not a correctness bug: the headline 2.0x compares a thread-safe collector with a 2000-era glibc malloc that paid LinuxThreads locking when pthreads was linked (20.90 s against 10.51 s unlinked), the parallel-mark rows use a second CPU that the malloc run leaves idle, and the multi-client GCBench variant is not published (hboehm.info is unreachable here and the repo holds no GCBench), so the numbers cannot be reproduced.

## Known shortcomings

- Numbers are from docs/scale.md, a 2000 run on a Pentium III/500 with the benchmark code off-repo (hboehm.info); docs/overview.md itself says the collector is 'typically competitive' with malloc/free, and the 2.0x row is against pthreads-linked glibc. The Boehm-GC licence is MIT-style but not OSI-listed; kept copyable on the FFTPACK and MIT-CMU precedent.
- Enricher: independent 2026 numbers in vlang/v issue #27488 (Ryzen 7 5800H, 64 B allocations): GC 18.5 M/s vs libc malloc 13.0 M/s on 1 thread (about 1.42x) but flat at about 18 M/s from 4 to 16 threads while malloc reaches 32-33 M/s, because V's bundled build had thread-local allocation off (fixed in V PR #27544, no after numbers). Known pathologies: issue #320 (single-threaded app 54 s on 1 core vs 220 s on 12 cores with parallel mark; GC_NPROCS=1 workaround), #681 (incremental plus parallel mark 7231 vs 2305 ms gctest), #453 (2 threads slower than 1), #619 (open hang). Lead: wingo/whippet.
- Re-found by seed w11-mine-e with the same docs/scale.md numbers (GC 9 s vs glibc malloc/free 10.51 s, Pentium III, year 2000); no new evidence.

## Caveats and trade-offs

Only first-party numbers, from a roughly 25-year-old collector release (2000) on a dual Pentium III/500 under Linux 2.2.12 with an old glibc and LinuxThreads; compiler and flags unstated; the author says the workload favors a collector (mostly small objects). The benchmark (GCBench, C variant) is hosted on the author's site (hboehm.info, not reachable from this session) and the multi-client variant used for the table is not published, so the run cannot be reproduced from the repo. The single-thread figure is a modest 1.17x; the 2.0x figure compares a pthreads-linked malloc build, where old glibc/LinuxThreads paid locking cost; the parallel-mark rows use a second CPU for marking while malloc/free runs single-threaded. The project's own docs/overview.md describes performance as typically competitive with malloc/free with slightly higher time and space overhead (citing Detlefs, Dosser and Zorn, 'Memory Allocation Costs in Large C and C++ Programs') and slower for large objects, so the faster claim holds only for small-object-heavy workloads. A third-party 1992 technical report by Zorn (seen only as a search snippet) reports a trivial slowdown versus malloc/free with about twice the memory. License: the LICENSE file is an MIT-style permissive notice (SPDX Boehm-GC, not OSI-listed); gc_allocator.h and extra/msvc_dbg.c carry similar per-file terms, and a few GNU build files carry a modified GPL. The lead URL ivmai/bdwgc is the old home of this repository.

Conservative stack/heap scanning means false retention and no precise object layout; the docs say large-object allocation is slower than malloc and programs usually need more memory; collection pauses unless the incremental mode is used; thread-local allocation and parallel marking are build-time options; GC_MALLOC_ATOMIC and root hints are needed for best speed.

## Maintenance

Actively maintained (commits on 2026-10-06, latest stable 8.2.12 from February 2025, 8.3.0 in development) under an MIT-style permissive notice and packaged by most distributions, so copyable; the speed claim rests on a 25-year-old first-party run plus one independent 2026 microbenchmark, with no correctness bug found behind the published numbers but no reproducible harness in the repo.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/scale.md gives first-party elapsed times for the GC build and a glibc malloc/free variant of the author's GC benchmark on a dual Pentium III/500 (Linux 2.2.12, GC release from 2000), but the multi-threaded benchmark variant is not in the repo (only a link to hboehm.info) and compiler and flags are unstated, so not A; no independent measurement, so C.
- **Verifier notes:** All figures match docs/scale.md exactly; added the parallel-mark table rows and the overview's own 'typically competitive' wording, which tempers the faster claim. Usability left as copyable on the precedent of other MIT/BSD-equivalent non-OSI notices (FFTPACK, MIT-CMU); a strict OSI-only reading would make it reference, so the orchestrator may want to decide. Metadata checked: 3.5k stars, not archived, not a fork, last commit 2026-10-06.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** modern re-run against glibc malloc, jemalloc and mimalloc; enricher issue reading; seed w11-mine-e (wave 11)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/docs/scale.md>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/docs/overview.md>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/LICENSE>
  - <https://github.com/bdwgc/bdwgc>
  - <https://github.com/bdwgc/bdwgc/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/README.md>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/docs/scale.md>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/docs/overview.md>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/docs/gcdescr.md>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/docs/macros.md>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/include/gc/gc.h>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/include/gc/gc_cpp.h>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/include/gc/gc_allocator.h>
  - <https://raw.githubusercontent.com/bdwgc/bdwgc/HEAD/include/gc/gc_inline.h>
  - <https://github.com/bdwgc/bdwgc>
  - <https://github.com/bdwgc/bdwgc/commits/master>
  - <https://github.com/bdwgc/bdwgc/releases>
  - <https://github.com/bdwgc/bdwgc/tree/master/tests>
  - <https://github.com/bdwgc/bdwgc/issues?q=is%3Aissue+performance>
  - <https://github.com/bdwgc/bdwgc/issues/320>
  - <https://github.com/bdwgc/bdwgc/issues/453>
  - <https://github.com/bdwgc/bdwgc/issues/619>
  - <https://github.com/bdwgc/bdwgc/issues/681>
  - <https://github.com/vlang/v/issues/27488>
  - <https://github.com/vlang/v/pull/27544>
  - <https://github.com/wingo/whippet>
  - <https://github.com/wingo/whippet/blob/main/benchmarks/README.md>
  - http://www.hboehm.info/gc/gc_bench/ (EGRESS_BLOCKED)
  - WebSearch snippet: CVE-2012-2673 integer overflows in GC_generic_malloc and calloc before 7.2
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/bdwgc/bdwgc`) · [data/wave11/enrich/raw/github_com_bdwgc_bdwgc.json](../../../data/wave11/enrich/raw/github_com_bdwgc_bdwgc.json) (enrichment confidence 0.8)

</details>
