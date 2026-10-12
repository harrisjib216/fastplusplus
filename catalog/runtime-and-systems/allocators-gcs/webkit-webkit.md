# libpas

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `BSD-2-Clause (per the Apple copyright header in libpas source files)` · 🟢 active

> Apple's libpas: isoheap-capable malloc toolkit behind WebKit's bmalloc, faster and leaner than the bmalloc it replaced.

| | |
|---|---|
| **Beats** | bmalloc (WebKit's previous allocator); HN thread also says it beats system malloc in WebKit and JSC |
| **Claimed result** | ReadMe: segregated heaps 'beat the original bmalloc at object churn performance' and use less memory because pages are returned sooner; no numbers on the page |
| **Workload** | Object churn and memory use inside WebKit; no standalone benchmark data in the repo |
| **Metric** | throughput |
| **Adoption** | Ships in Safari/WebKit as bmalloc's backend |
| **Links** | [repository](https://github.com/WebKit/WebKit/tree/main/Source/bmalloc/libpas) · [benchmark](https://github.com/WebKit/WebKit/blob/main/Source/bmalloc/libpas/ReadMe.md) |

## Verdict

The ReadMe says segregated heaps beat the original bmalloc at object churn and that libpas uses much less memory because it returns pages sooner, with no numbers. Documentation.md (Filip Pizlo, February 2022) adds that moving WebKit from bmalloc and MetaAllocator to libpas gave about a 2% Speedometer2 speedup and about 8% lower memory on several memory benchmarks, with no hardware, compiler or harness given; the baseline is bmalloc, not system malloc.

## Use it when

- You need type-segregated heaps (isoheaps), one heap per type, for use-after-free hardening, and want them cheap enough to create in large numbers
- Allocation-heavy C or C++ code on Apple platforms or Linux where the allocator has to keep metadata out of line (no free-list pointers inside freed objects)
- Special allocators such as executable/JIT memory (jit_heap) or MTE-tagged memory next to ordinary malloc in one library
- Long-running processes that should hand empty pages back to the OS quickly (configurable decommit delay, e.g. 300 ms)

## Skip it when

- You want a malloc you can LD_PRELOAD or link in place of glibc malloc: libpas does not override malloc and free, and you must build your own heap config (as bmalloc does)
- You need published numbers against mimalloc, jemalloc or tcmalloc: the only figures are WebKit's own (about 2% Speedometer2 and about 8% memory against bmalloc and MetaAllocator)
- Toolchains other than Clang: several heap config .c files use a clang-only C extension (compound-literal field access in file-scope initializers)
- You want a small vendorable allocator: it lives in the WebKit monorepo, is large, and the design leans on intricate fine-grained locking that is hard to audit

## How it is fast

Segregated heaps use simple segregated storage (each page holds one size class) plus thread-local caches with per-size-class local allocators and a deallocation log, so the common alloc and free paths need no atomics or fences, just a few loads, adds and stores. Deallocation logs are flushed in batches with lock-sharing tricks that cut lock acquisitions. A scavenger thread (every 100 ms by default) decommits pages that have been empty for a while through a physical page sharing pool, which is where the memory savings over bmalloc come from. Bitfit (first-fit, one bit per minalign granule) and a cartesian-tree first-fit large heap cover the bigger sizes.

## Compared with alternatives

Pick libpas over IsoAlloc when you want isoheaps with production-tested performance at browser scale and can live with a Clang-built source drop; pick Mesh or mimalloc-class allocators when you need a malloc replacement with published cross-allocator benchmarks.

## Integration

| | |
|---|---|
| **Form** | source-drop (pulled into the host project's build; standalone build.sh/CMake makes a dylib and test binaries) |
| **Dependencies** | none outside the libpas tree (pthreads); the test suite is C++ |
| **Minimum toolchain** | Clang required for some files; CMake 3.21+, C23 and C++23 in the standalone CMakeLists |
| **Platforms** | Darwin (macOS/iOS, arm64/arm64e, x86-64), Linux, Windows and PlayStation macros present in pas_platform.h; tuned mainly for Apple platforms |
| **Thread safety** | thread-safe; thread-local caches plus fine-grained locks, with a scavenger thread that may suspend threads to stop their allocators |
| **Drop-in for the baseline** | partial: it is a drop-in for bmalloc inside WebKit (PAS_BMALLOC), not for system malloc |

## Gotchas

- The scavenger suspends threads that own thread-local caches to stop their allocators, which can surprise code that is sensitive to signals or thread suspension
- Thread-local caches can grow large (inline allocator state); WebKit measured them at up to about 1% of memory and added partial TLC decommit
- The bitfit heap is space-efficient but much slower than segregated heaps and has an upper size bound
- The record id is the whole WebKit repository; the code is in Source/bmalloc/libpas

## Known shortcomings

- libpas is not a malloc override and uses a clang-only C extension in its heap config files; it needs C23/C++23 CMake. Documentation.md (Pizlo, Feb 2022) gives about 2% on Speedometer 2 and about 8% memory against bmalloc plus MetaAllocator, with no hardware or harness. The entry is the whole WebKit repo; libpas commits continue to 2026-10-01.

## Caveats and trade-offs

Qualitative claim only, baseline is bmalloc rather than a general-purpose incumbent; the 'beats other mallocs' numbers come from the HN thread 'All About Libpas, Phil's Super Fast Malloc' (item 31581727) and a blocked blog post, seen only as search snippets; last commit date not checked.

Allocator toolkit built around isoheaps (type-segregated heaps) for security; configurable heap kinds (segregated, bitfit); lives inside the WebKit tree and is built via its own build.sh or CMake; mostly tuned for Apple platforms and WebKit.

## Maintenance

Actively maintained inside WebKit (libpas commits through 2026-10-01, e.g. MTE work); BSD-2-Clause and shipped in Safari, but you have to extract it from the monorepo and write your own heap config to use it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** ReadMe.md says segregated heaps 'beat the original bmalloc at object churn performance' and that libpas 'achieves much better memory usage than bmalloc' because it returns pages sooner, with no numbers or methodology.
- **Verifier notes:** Kept at D despite no numbers because libpas is widely deployed (WebKit/Safari/JSC). BSD-2-Clause confirmed from the Apple copyright header in src/libpas/pas_heap.h. Repo id is the whole WebKit monorepo; libpas lives in Source/bmalloc/libpas.
- **Shortcomings recorded by:** first-party documentation
- **Pages the verifier opened:**
  - <https://github.com/WebKit/WebKit/blob/main/Source/bmalloc/libpas/ReadMe.md>
  - <https://github.com/WebKit/WebKit/blob/main/Source/bmalloc/libpas/src/libpas/pas_heap.h>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/WebKit/WebKit/main/Source/bmalloc/libpas/ReadMe.md>
  - <https://raw.githubusercontent.com/WebKit/WebKit/main/Source/bmalloc/libpas/Documentation.md>
  - <https://raw.githubusercontent.com/WebKit/WebKit/main/Source/bmalloc/libpas/CMakeLists.txt>
  - <https://raw.githubusercontent.com/WebKit/WebKit/main/Source/bmalloc/libpas/build.sh>
  - <https://raw.githubusercontent.com/WebKit/WebKit/main/Source/bmalloc/libpas/src/libpas/pas_heap.h>
  - <https://raw.githubusercontent.com/WebKit/WebKit/main/Source/bmalloc/libpas/src/libpas/pas_platform.h>
  - <https://github.com/WebKit/WebKit/commits/main/Source/bmalloc/libpas>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/webkit/webkit`) · [data/wave11/enrich/raw/github_com_webkit_webkit.json](../../../data/wave11/enrich/raw/github_com_webkit_webkit.json) (enrichment confidence 0.7)

</details>
