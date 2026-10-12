# Kaname-Shiki (MemoryAllocator.KanameShiki)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Small (2600-line) thread-caching general-purpose allocator for 64-bit Windows/Linux that beats the MSVC CRT malloc on its own alloc/free stress tests.

| | |
|---|---|
| **Beats** | malloc (MSVC CRT), mimalloc, tcmalloc, jemalloc |
| **Claimed result** | Raw totals in Benchmark/\*.txt (seconds, lower is better, 8 threads, alloc+free only): 0B-1KiB KanameShiki 1.73 vs MSVC malloc 2.33, mimalloc 1.90, jemalloc 2.99, tcmalloc 15.35; 2KiB-32KiB 0.58 vs malloc 3.27, mimalloc 2.31, jemalloc 1.13; 64KiB-1MiB 0.33 vs malloc 27.59, jemalloc 0.60; 2MiB-32MiB 3.22 vs malloc 89.80, mimalloc 49.26, jemalloc 5.35. With memory fill, 0B-1KiB 8 threads: 2.29 vs malloc 2.82, mimalloc 2.53; 2MiB-32MiB 8 threads: 3730.7 vs malloc 6186.0, mimalloc 3085.8 (mimalloc faster but it had 230,000 allocation failures). Single thread 0B-1KiB: 0.036 vs malloc 0.151 but slower than mimalloc 0.022 and tcmalloc 0.029. |
| **Workload** | Cumulative seconds over nine multi-thread tests (testA-testI) and five single-thread tests, sizes 0 B to 32 MiB, with and without memory fill, 8 threads. |
| **Metric** | throughput |
| **Hardware** | Windows 10 Pro 64-bit, Core i7-8700 3.20GHz, 32 GiB |
| **Compiler and flags** | MSVC cl -DNDEBUG -Ox -EHsc |
| **Adoption** | 80 stars |
| **Last commit** | 2019-10-19 |
| **Links** | [repository](https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki) · [benchmark](https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki/tree/master/Benchmark) |

## Verdict

On a Core i7-8700 under Windows 10 with MSVC cl -Ox, the author's harness (Main.cpp, nine tests, 8 threads) totals 1.73 s for 0B-1KiB vs 2.33 s for the MSVC CRT malloc (about 1.35x, derived from page data) and 1.90 s for mimalloc, and 3.22 s vs 89.80 s for 2MiB-32MiB alloc+free only; with memory fill the large-block gap shrinks to 3730.7 s vs 6186.0 s and mimalloc is faster. Raw timings are in Benchmark/\*.txt; the MSVC version is not stated and nobody else has reproduced them.

## Use it when

- Windows x64 programs (MSVC) whose hot path is malloc/free or new/delete churn of small blocks up to 1 KiB across 8 or so threads, where the CRT heap is the bottleneck.
- Producer/consumer patterns where blocks are allocated on one thread and freed on another (the benchmark's testF-testI), which the per-slot remote free lists target.
- Console or embedded-style programs that own the machine and can afford the specialized profile's 8 GiB up-front reservation in exchange for fewer OS calls.
- As a small, readable reference design for thread-caching allocators (about 49 KB of source, MIT).

## Skip it when

- When mimalloc is an option: in the author's own single-thread runs mimalloc is faster (0B-1KiB alloc-only 0.022 s vs 0.036 s; with memory fill 0.209 s vs 0.223 s), and with memory fill in the 2MiB-32MiB 8-thread test mimalloc total is 3085.8 s vs 3730.7 s.
- Long-running services that need memory returned to the OS: the large-block speedups come from caching freed blocks in reserver lists, and the specialized profile commits 8 GiB at start-up.
- Production code that needs a maintained allocator: no commits since 2019-10-19, an open unanswered segfault report in the cooperative profile (issue #3, crash in GlobalReserver::Alloc), and the README says MinGW64 g++ and clang++ builds do not work.
- Programs that use posix_memalign/memalign/valloc through the LD_PRELOAD shim (see gotchas), or 32-bit and pre-Haswell x86 targets (the code uses _lzcnt/_tzcnt and assumes 8-byte size_t).

## How it is fast

Size-segregated per-thread allocators: LocalPool (fixed-size pools in 8-byte classes up to 1 KiB), LocalCram (power-of-two classes up to 1 MiB) and LocalAny (one OS mapping per block above 1 MiB). Each has an own-thread free list touched with no atomics and a remote-free list split across several slots; the 'RevolverAtomic' scheme rotates an atomic index on every remote free so concurrent CAS pushes spread over different cache lines instead of contending on one head (Cache.h). Freed pools and blocks are kept in local and global reserver free lists before falling back to a mutex-protected first-fit global heap (doubly linked nodes with coalescing) and then VirtualAlloc/mmap, so repeated large alloc/free pairs avoid OS calls.

## Compared with alternatives

Pick it over fc_malloc or the hobby allocators (Bloodmoon001, atul-singh-as) when you need cross-thread frees and a full malloc surface on Windows with numbers against mimalloc/jemalloc/tcmalloc; pick a maintained allocator such as mimalloc or IsoAlloc instead for production, and Mesh when memory footprint matters more than speed.

## Integration

| | |
|---|---|
| **Form** | static lib (MSVC) or shared lib (g++/clang++ LD_PRELOAD); single-TU source-drop also possible |
| **Dependencies** | none beyond the C++ standard library and the OS (VirtualAlloc or mmap); -lpthread -latomic on Linux |
| **Minimum toolchain** | C++14 (clang++ -std=c++14 in README); MSVC version not stated; g++ build needs -mlzcnt -mbmi |
| **Platforms** | x86-64 only in practice (LZCNT/BMI1 intrinsics, 64-bit size_t constants); Windows 10 and Linux; MinGW64 not working |
| **Thread safety** | Thread-safe; own-thread lists are lock-free and wait-free, remote-free and global reserver lists use CAS, the global heap uses a std::mutex; per-thread state lives in thread_local LocalCntx. |
| **Drop-in for the baseline** | partial — on Linux LD_PRELOAD replaces malloc/free/calloc/realloc; on Windows only operator new/delete are replaced and C code must call KanameShiki::Alloc/Free explicitly (the benchmark does exactly that) |

## Gotchas

- memalign(alignment, size) in src/Posix.cpp calls aligned_alloc(size, alignment) with the arguments swapped, so posix_memalign/memalign/valloc return ENOMEM/nullptr for most size/alignment pairs and an under-aligned block when alignment exceeds size. The published benchmark does not exercise this path.
- calloc computes nmemb \* size with no overflow check, so an overflowing request returns a block smaller than asked for; realloc always allocates a new block and copies, even when shrinking.
- The benchmark's alloc-then-immediately-free loops (testA) reward block caching: mimalloc times about 0.001 s and KanameShiki is similar, while the CRT pays OS-level costs for 2MiB-32MiB blocks (single-thread total 17.05 s vs 0.006 s). In FILL mode Main.cpp re-enables assert and checks every byte in a loop before freeing, so those totals are dominated by the harness's own memset and verify passes.
- Builds differ: the mimalloc binary is linked with -MD -LTCG while malloc, tcmalloc, jemalloc and KanameShiki use the default static CRT; jemalloc 'segfaults frequently' on the author's MSVC build and mimalloc had 234,674 failed allocations in c4 testI (8 threads x 128 blocks of up to 32 MiB exceeds the 32 GiB machine).

## Known shortcomings

- Large-block allocation-only wins up to about 2800x over MSVC malloc (derived) are likely caching; with memory fill, mimalloc is faster.
- Correctness bug in src/Posix.cpp: memalign calls aligned_alloc(size, alignment) with the arguments swapped, so posix_memalign, memalign and valloc return ENOMEM or under-aligned blocks; calloc has no overflow check. The benchmark calls KanameShiki::Alloc/Free directly, so the numbers are not affected. Harness flaws: mimalloc built with -MD -LTCG while the others use the static CRT; mimalloc has 234,674 failed allocations in c4 testI; fill totals are dominated by the harness byte-check loop. Open segfault issue 3 in the cooperative profile; single-thread is slower than mimalloc (0.036 s vs 0.022 s).

## Caveats and trade-offs

Windows-only published results against the MSVC CRT heap; MSVC version not stated. Alloc+free-only large-block tests show implausible gaps (single-thread 2MiB-32MiB: 0.006 s vs malloc 17.0 s, about 2800x derived from page data), likely from caching freed blocks instead of returning them to the OS; with memory fill the gap shrinks to about 1.66x vs malloc and mimalloc is faster. The c4_1.txt rows are labelled KanameShiki0_4.exe/KanameShiki1_4.exe (copy-paste labelling). Author says jemalloc segfaulted frequently on the MSVC build and mimalloc had 230,000 allocation failures in the 2MiB-32MiB test; Mingw64 builds do not work; last commit 2019-10-19.

Lock-free local and other-thread free lists via RevolverAtomic; 2600 lines; two profiles (general-purpose vs reserve-heavy embedded); global heap uses a mutex.

## Maintenance

Abandoned since 2019-10-19 with open crash and benchmark-source issues; MIT and small enough to vendor or study, but treat it as a reference design rather than a production allocator.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: benchmark code is public (Main.cpp, CLog.cpp, build_m.bat at the repo root), the README gives the exact MSVC command lines (cl -DNDEBUG -Ox -EHsc) and the CPU (Core i7-8700 3.20GHz), and the raw timings behind the bar charts are checked in as Benchmark/c\*_\*.txt and fill_c\*_\*.txt. MSVC version is not stated.
- **Verifier notes:** README charts hide numbers, but the Benchmark/ directory holds the raw text results, so the speedups are quotable. Tier A is mechanical (code, flags, CPU stated); the orchestrator may prefer to note the large-block alloc-only rows as unrepresentative.
- **Fields the verifier corrected:** `claimed_speedup`, `benchmark_url`, `caveats`
- **Shortcomings recorded by:** public benchmark code and raw timings; code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki>
  - <https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki/tree/master/Benchmark>
  - <https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki/commits>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/README.md>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Benchmark/c1_8.txt>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Benchmark/c4_8.txt>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Benchmark/c4_1.txt>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Benchmark/fill_c4_8.txt>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Image/c1_8.png>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Image/c4_8.png>
- **Sources the enricher read:**
  - <https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki>
  - <https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki/tree/master/Benchmark>
  - <https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki/tree/master/src>
  - <https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki/issues?q=is%3Aissue>
  - <https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki/issues/2>
  - <https://github.com/EmuraDaisuke/MemoryAllocator.KanameShiki/issues/3>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/README.md>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Main.cpp>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/build_m.bat>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/build_g.sh>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/include/KanameShiki.h>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Benchmark/c1_8.txt>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Benchmark/c4_8.txt>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Benchmark/c4_1.txt>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Benchmark/fill_c4_8.txt>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Benchmark/fill_c1_1.txt>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/KanameShiki.cpp>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/Func.cpp>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/New.cpp>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/Posix.cpp>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/Posix.h>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/GlobalCntx.cpp>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/GlobalHeap.cpp>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/LocalCntx.cpp>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/Config.h>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/Cache.h>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/src/Lzc.h>
  - <https://raw.githubusercontent.com/EmuraDaisuke/MemoryAllocator.KanameShiki/HEAD/Benchmark/c1_1.txt>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/emuradaisuke/memoryallocator.kanameshiki`) · [data/wave11/enrich/raw/github_com_emuradaisuke_memoryallocator_kanameshiki.json](../../../data/wave11/enrich/raw/github_com_emuradaisuke_memoryallocator_kanameshiki.json) (enrichment confidence 0.7)

</details>
