# gperftools TCMalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Thread-caching malloc replacement for glibc's ptmalloc2; per-thread free lists cut lock contention and per-call cost.

| | |
|---|---|
| **Beats** | glibc 2.3 malloc (ptmalloc2) |
| **Claimed result** | "ptmalloc2 takes approximately 300 nanoseconds to execute a malloc/free pair on a 2.8 GHz P4 (for small objects). The TCMalloc implementation takes approximately 50 nanoseconds for the same operation pair." (\~6x faster, verbatim from docs/tcmalloc.adoc Motivation section) |
| **Workload** | single malloc/free round-trip for small objects, single-threaded, as described in TCMalloc's original design writeup |
| **Metric** | latency |
| **Hardware** | 2.8 GHz Intel Pentium 4 (32-bit), circa mid-2000s |
| **Adoption** | 9.0k stars; historically used in Chrome/Chromium, widely packaged as libtcmalloc in Linux distros |
| **Last commit** | 2026-09-05 |
| **Links** | [repository](https://github.com/gperftools/gperftools) · [benchmark](https://github.com/gperftools/gperftools/blob/master/docs/tcmalloc.adoc) |

## Verdict

The first-party \~2005 design doc claims ptmalloc2 (glibc 2.3) took \~300ns per small malloc/free pair versus \~50ns for TCMalloc, both measured on a single 2.8 GHz 32-bit Pentium 4, with no compiler, flags, or benchmark harness given. A Dec 2024 maintainer's note in the same document calls those exact numbers obsolete while still asserting gperftools remains somewhat faster than modern glibc.

## Use it when

- Multi-threaded C++ services with frequent small (&lt;=256KB) alloc/free churn where ptmalloc2 lock contention or per-thread-arena memory stranding is a measured problem
- You want the bundled pprof-compatible heap/CPU profiler alongside the allocator, not just a faster malloc
- Linux/x86, aarch64, or riscv targets with native TLS, where gperftools documents its fast path as fully optimized
- Retrofitting an existing binary via LD_PRELOAD without rebuilding
- Workloads that hand large blocks of memory off between phases or threads, where ptmalloc2's per-thread arenas can't reclaim it

## Skip it when

- You need a modern, reproducible speed number vs glibc: the \~6x claim is a 2005-era 32-bit P4 measurement, and the maintainer's Dec 2024 note says glibc has since closed much of that gap
- Your code loads the allocator via dlopen(): TCMalloc's initial-exec TLS model breaks under dlopen (documented in INSTALL)
- Heavy fork() + multithreading without an immediate exec(): internal locks aren't fully wrapped in pthread_atfork (open issue #1425), so children can hang or profiling data can corrupt on exit()
- musl libc targets where you need profiling: backtracing/profiling has repeated musl-specific breakage (issues #1282, #1602, #693); plain malloc is more reliable there
- Windows or heap-profiling on non-Linux platforms: Windows support is tcmalloc_minimal only (no heap/CPU profiler), and CMake build support is explicitly called 'preliminary'

## How it is fast

Gives each thread a lock-free thread-local cache of free lists spanning \~88 size-classes for objects &lt;=256KB; medium/large objects go through a central page heap and a best-fit red-black tree instead. The allocation/deallocation fast path only touches the thread-local free list, so it takes no locks at all in the common case. A slow-start algorithm resizes each per-thread free list to balance central-list traffic against idle memory, and a build-time --with-tcmalloc-pagesize option trades memory for fewer page-heap operations.

## Compared with alternatives

Pick gperftools when you also want its bundled pprof-compatible CPU/heap profiler and are specifically displacing glibc's ptmalloc2 on Linux with a mature, widely-packaged allocator. For a pure allocator-speed decision today, snmalloc and mimalloc publish newer benchmarks claiming wins over tcmalloc itself, so prefer those siblings' Tier B/A evidence over tcmalloc's 2005-era numbers when raw throughput is the deciding factor.

## Integration

| | |
|---|---|
| **Form** | shared lib (static lib also supported) |
| **Dependencies** | none for tcmalloc_minimal; full tcmalloc/profiler builds use libunwind (default on most platforms) or built-in backtrace (s390, macOS) for stack unwinding |
| **Minimum toolchain** | C++17 (AX_CXX_COMPILE_STDCXX 17 mandatory in configure.ac); autotools (primary, fully supported) or CMake 3.12+ (preliminary); MSVC 2019+ or MinGW for Windows |
| **Platforms** | x86, aarch64, riscv Linux (primary, fully tested); FreeBSD, NetBSD, macOS (aarch64), Solaris x86, QNX, AIX (partial, per INSTALL); Windows via MSVC 2019+/MinGW limited to tcmalloc_minimal |
| **Thread safety** | Thread-safe by design (per-thread caches), but not documented as safe to load via dlopen(), and internal locks are not fully wrapped with pthread_atfork as of the open 2024 issue, so fork()-after-threads has known hang risk |
| **Drop-in for the baseline** | partial — true for ordinary link-time or LD_PRELOAD use as a malloc/new replacement, but breaks if loaded via dlopen() and has documented fork-safety caveats |

## Gotchas

- Loading via dlopen() breaks tcmalloc's TLS assumptions; it must be linked at startup or LD_PRELOADed, not dlopen'd (INSTALL)
- CPU profiling doesn't work correctly across fork() unless the child immediately exec()s; if the child calls exit() instead of _exit(), profile data can be corrupted (README)
- --with-tcmalloc-pagesize and CXXFLAGS=-DTCMALLOC_SMALL_BUT_SLOW are build-time, not runtime, speed/memory tradeoffs (INSTALL)
- musl libc builds have a history of breakage in backtracing/profiling code across multiple issues; core malloc is more reliable there than the profilers

## Caveats and trade-offs

Numbers are from the original \~2005 TCMalloc design writeup, kept verbatim in current docs with an explicit 2024 editor's warning: "referenced glibc versions are now long obsolete. And amount of time per malloc call is far from correct anymore. And the description is for 32-bit computers." No compiler, flags, or reproducible benchmark harness are given (project's own partial-methodology claim), so this is capped at Tier C rather than B, per the rule that the project's own benchmark code/claims with partial methodology is C, not B.

\~1% space overhead for small objects claimed vs ptmalloc2's larger per-object header/rounding overhead (same doc); per-thread caches can strand memory across allocation phases if arenas mismatch; project's own current maintainer notes glibc has since closed much of this original gap

## Maintenance

Actively maintained (last commit 2026-09-05, 8,976 stars, not archived), BSD-3-Clause and small enough to vendor or package; historically used in Chrome/Chromium and widely distributed as libtcmalloc across Linux distros.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party design doc states verbatim that ptmalloc2 (glibc 2.3) takes \~300ns and TCMalloc \~50ns per small malloc/free pair on a 2.8 GHz P4. There is no benchmark code, compiler, or flags, and a Dec 2024 maintainer note calls the timings obsolete, so C.
- **Verifier notes:** Quote and the Dec 2024 editor's warning were verified verbatim in docs/tcmalloc.adoc. The same note adds qualitatively that glibc is 'still being somewhat slower than gperftools' today. The Performance Notes section has no numbers. Metadata (BSD-3-Clause, 8,976 stars, last commit 2026-09-05, not archived) matches.
- **Pages the verifier opened:**
  - <https://github.com/gperftools/gperftools/blob/master/docs/tcmalloc.adoc>
  - <https://github.com/gperftools/gperftools>
- **Sources the enricher read:**
  - <https://github.com/gperftools/gperftools>
  - <https://github.com/gperftools/gperftools/blob/master/docs/tcmalloc.adoc>
  - <https://github.com/gperftools/gperftools/blob/master/README>
  - <https://github.com/gperftools/gperftools/blob/master/INSTALL>
  - <https://github.com/gperftools/gperftools/blob/master/CMakeLists.txt>
  - <https://github.com/gperftools/gperftools/blob/master/configure.ac>
  - <https://github.com/gperftools/gperftools/issues/1425>
  - <https://github.com/gperftools/gperftools/issues/1282>
  - <https://github.com/gperftools/gperftools/issues/1602>
  - <https://github.com/gperftools/gperftools/issues/693>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/gperftools/gperftools`) · [data/wave0-seed/enrich/raw/github_com_gperftools_gperftools.json](../../../data/wave0-seed/enrich/raw/github_com_gperftools_gperftools.json) (enrichment confidence 0.7)

</details>
