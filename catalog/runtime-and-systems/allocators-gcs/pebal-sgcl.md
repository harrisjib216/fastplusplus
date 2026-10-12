# SGCL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C++20 concurrent garbage collector whose allocation path beats malloc-backed unique_ptr/shared_ptr for small objects on macOS.

| | |
|---|---|
| **Beats** | malloc via std::unique_ptr / std::shared_ptr (macOS libmalloc nano zone); also Go and Java ZGC collectors |
| **Claimed result** | 32 B allocation 2.8 ns on 1 thread vs unique_ptr 17.1 ns and shared_ptr 16.3 ns (about 6x, derived from page data); 32 B on 4 threads 3.5 vs 17.4 and 16.5 ns; 32 B on 24 threads 11.7 vs 23.2 and 22.6 ns; 256 B on 24 threads is slower than malloc: 71.4 vs 23.5 ns |
| **Workload** | Per-object allocation cost in ns for 32 B and 256 B objects on 1, 4 and 24 threads, plus binary-trees and a shared-graph workload, compared with unique_ptr, shared_ptr, Go and Java ZGC |
| **Metric** | latency |
| **Hardware** | Mac Studio Apple M2 Ultra (16 performance + 8 efficiency cores), 64 GB, macOS 26.5 |
| **Compiler and flags** | Apple clang 21.0, -O3 -DNDEBUG; Go 1.27.1 GOGC=100; OpenJDK 26.0.2 generational ZGC |
| **Adoption** | 242 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/pebal/sgcl) · [benchmark](https://github.com/pebal/sgcl/blob/main/docs/garbage_collector/benchmarks.md) |

## Verdict

On a Mac Studio (Apple M2 Ultra, macOS 26.5, Apple clang 21.0 -O3 -DNDEBUG, libc++, macOS nano-zone malloc), the repo's own benchmarks/ programs show a 32 B allocation at 2.8 ns on one thread vs 17.1 ns for std::unique_ptr and 16.3 ns for std::shared_ptr (about 6x), narrowing to 11.7 vs 23.2 ns on 24 threads, while 256 B on 24 threads is about 3x slower than unique_ptr (71.4 vs 23.5 ns). Binary-trees depth 21 runs in 4.43 s wall vs 12.42 s for unique_ptr, but with 9.41 vs 12.39 s process CPU and 292 vs 134 MB peak memory.

## Use it when

- Pointer-heavy C++ code with shared or cyclic graphs (lock-free structures, ASTs, actor/channel programs) where shared_ptr reference counting and destructor cascades cost too much: shared_ptr drop-all took 68-171 ms vs microseconds for SGCL on the shared-graph benchmark.
- Allocation-heavy workloads of small objects (32 B) on 1-24 threads where wall time on the mutator matters more than total CPU.
- Programs that copy pointers to shared objects across threads: 1.4-1.9 ns per copy vs 125-149 ns for contended shared_ptr.
- Projects that want Go-style concurrency (tasks, channels) inside C++ without a separate reclamation scheme such as hazard pointers or epochs.
- Apple Silicon macOS builds with Apple clang, the only tested platform.

## Skip it when

- Linux, Windows or x86-64 targets in production: the current version is built and tested on Apple Silicon only, and no number has been reproduced elsewhere.
- Memory-constrained programs: binary-trees depth 21 peaks at 292 MB vs 134 MB for unique_ptr, and garbage waits for a cycle.
- Many threads allocating 256 B objects: 71.4 ns vs 23.5 ns for unique_ptr on 24 threads.
- CPU-budgeted or core-saturated systems: the win moves destruction to collector threads, so process CPU time is much closer to the baseline than wall time (9.41 vs 12.39 s at binary-trees depth 21) and collector threads compete with mutators for cores.
- Code that needs destructors to run promptly on tracked objects, uses raw pointers as owning references, or stores pointers in std containers, unions, std::variant or std::function.

## How it is fast

Allocation is a bitmap pop from a per-thread page allocator plus one byte of state, with no lock or barrier, and freeing moves off the mutator onto a collector thread that sweeps and runs destructors. The collector is a concurrent, non-moving, generational (sticky mark bits plus card marking) mark-and-sweep with a Dijkstra insertion barrier, no stop-the-world phase and no safepoints; stacks are scanned conservatively while threads run, and the heap is traced through per-type pointer maps narrowed by elimination. Marking is parallelised over helper threads with page-order tracing and a prefetch window.

## Compared with alternatives

The siblings (mimalloc-class allocators such as Kaname-Shiki or FastAlloc, pool allocators such as fast-alloc, mem++) speed up malloc/free behind the same manual or reference-counted ownership; pick SGCL when the cost you want gone is shared_ptr reference counting, destructor cascades or a reclamation scheme for shared and cyclic graphs, and you can adopt a GC pointer type. If you only need faster malloc on Linux, a sibling allocator is the safer choice.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library (CMake interface target optional); on Apple systems the target links Security, CoreFoundation and, for HEIF, ImageIO/CoreGraphics/Accelerate; tests need googletest, zlib, libbz2 and OpenSSL 3 |
| **Minimum toolchain** | C++20; tested only with Apple clang (21.0 in the published benchmarks); gcc on Windows discouraged |
| **Platforms** | macOS on Apple Silicon tested; Linux, Windows and x86-64 written for but pending |
| **Thread safety** | Concurrent collector; any thread can allocate and copy pointers, threads are registered on first pointer copy; atomic&lt;tracked_ptr&gt; with compare-exchange provided for shared mutable slots |
| **Drop-in for the baseline** | partial — make_tracked returns an sgcl::unique_ptr with familiar semantics, but objects must be allocated through SGCL and held in sgcl pointer and container types; it does not replace malloc or std::shared_ptr transparently |

## Gotchas

- A tracked_ptr may live only on a thread's own stack or inside a managed object; in a global, a std container, heap memory from new, a heap-copied lambda or a plain coroutine frame it is never scanned and its object can be collected (use root_ptr there). Alternate signal stacks, fibers and ucontext stacks are not scanned.
- A tracked_ptr must never share storage with data (union with a value, std::variant, std::any, std::function inline storage) because per-type pointer maps are narrowed by elimination; use sgcl::variant, any, function and expected instead.
- Destructors of tracked objects run on collector threads in no particular order; a destructor may not touch its tracked_ptr members except through if_alive().
- The headline baseline is macOS libmalloc's nano zone; earlier runs with MallocNanoZone=0 made the unique_ptr/shared_ptr columns about a quarter slower, and the Go/Java columns come from an older -O2 run.

## Known shortcomings

- Tested on Apple Silicon only; the baseline is the macOS nano-zone malloc and the Go/Java columns come from an older -O2 run. Slower than unique_ptr at 256 B on 24 threads (71.4 vs 23.5 ns) with higher memory (292 vs 134 MB); CPU time is closer (9.41 vs 12.39 s). tracked_ptr placement rules are strict; 7 issues, all closed.

## Caveats and trade-offs

The docs deliberately leave the Boehm-Demers-Weiser GC out of the tables, so there is no head-to-head with Boehm GC. The malloc behind unique_ptr/shared_ptr is the macOS nano zone, not glibc, jemalloc or mimalloc (an earlier run with MallocNanoZone=0 made those columns about a quarter slower). C++ columns are from a 4 October 2026 run at -O3; the Go and Java columns are from 19 September 2026, when the C++ side was built at -O2, and were not rerun. Apple Silicon only; no number reproduced on x86-64, Linux or Windows yet. SGCL is slower than unique_ptr for 256 B objects on 24 threads (71.4 vs 23.5 ns), copies a pointer slower than a raw pointer (1.4-1.9 vs 0.6 ns), and uses more memory than unique_ptr in binary-trees (292 vs 134 MB at depth 21). The wall-time wins move destruction to the collector thread, so process CPU time is closer (binary-trees depth 21: 9.41 vs 12.39 s CPU).

Header-only C++20 concurrent non-moving generational mark-and-sweep GC with its own managed pointer types (tracked_ptr etc.), containers and 15 library modules; programs must adopt sgcl pointer types; conservative stack scanning; tested on Apple Silicon only (Linux and Windows pending).

## Maintenance

Very actively developed (last commit 2026-10-05) by a single author, Apache-2.0 and header-only so it is easy to vendor, but the API is pre-1.0 with stability promised only from 1.0.0, and only macOS on Apple Silicon is tested.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/garbage_collector/benchmarks.md compares SGCL with std::unique_ptr and std::shared_ptr (plus Go and Java ZGC) using the public benchmarks/ programs and benchmarks/run.sh and compare.sh, built with Apple clang 21.0 -O3 -DNDEBUG on an Apple M2 Ultra; code, compiler, flags and CPU are all stated.
- **Verifier notes:** All allocation numbers in claimed_speedup match the Allocation table. The page also shows binary-trees depth 21 at 4.43 s vs 12.42 s unique_ptr and 14.40 s shared_ptr, and shared_ptr drop-all of 68-171 ms vs microseconds for SGCL. baseline_stdlib set to libc++ because Apple clang on macOS uses libc++ (inferred from the toolchain, not stated on the page).
- **Fields the verifier corrected:** `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** first-party benchmarks.md
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pebal/sgcl/HEAD/README.md>
  - <https://raw.githubusercontent.com/pebal/sgcl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pebal/sgcl/HEAD/docs/garbage_collector/benchmarks.md>
  - <https://raw.githubusercontent.com/pebal/sgcl/HEAD/benchmarks/run.sh>
  - <https://raw.githubusercontent.com/pebal/sgcl/HEAD/benchmarks/compare.sh>
  - <https://github.com/pebal/sgcl/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/pebal/sgcl/HEAD/README.md>
  - <https://raw.githubusercontent.com/pebal/sgcl/HEAD/docs/garbage_collector/benchmarks.md>
  - <https://raw.githubusercontent.com/pebal/sgcl/HEAD/docs/garbage_collector/overview.md>
  - <https://raw.githubusercontent.com/pebal/sgcl/HEAD/benchmarks/run.sh>
  - <https://github.com/pebal/sgcl/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/pebal/sgcl`) · [data/wave11/enrich/raw/github_com_pebal_sgcl.json](../../../data/wave11/enrich/raw/github_com_pebal_sgcl.json) (enrichment confidence 0.8)

</details>
