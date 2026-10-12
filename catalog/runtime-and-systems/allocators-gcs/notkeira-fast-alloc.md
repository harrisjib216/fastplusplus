# fast-alloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Small C++20 pool, stack and free-list arenas for game code; beats new/delete and malloc only on fixed-size or frame-scoped patterns.

| | |
|---|---|
| **Beats** | malloc/free and new/delete |
| **Claimed result** | Linux (GCC 14.2.0, Ryzen 7 PRO 8700GE): pool allocate/free 2.00 ns vs 6.03 ns new/delete (3.0x); stack allocate/reset 1.99 vs 4.77 ns malloc/free (2.4x); stack 1,000-allocation frame 1205 vs 14385 ns (11.9x); free-list first-fit 4.66 vs 4.67 ns (1.0x); best-fit 0.76x and thread-safe pool 0.60x (slower). The larger ratios are from single-repetition CI runs against weaker system allocators: Windows MSVC pool 14.9x, stack 20.1x/24.0x, free-list 6.7x; macOS pool 4.0x, stack 4.7x/7.0x, free-list 2.2x/1.7x. |
| **Workload** | 64-byte allocations: pool, stack and free-list allocators against new/delete, frame workloads. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 PRO 8700GE (Linux); Apple Silicon arm64; Windows CI runner |
| **Compiler and flags** | GCC 14.2.0 -O3 -march=native (Linux); Apple Clang 21.0 and MSVC 19.51 Release |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/NotKeira/fast-alloc) · [benchmark](https://github.com/NotKeira/fast-alloc) |

## Verdict

Google Benchmark 1.9.1, 64-byte blocks, GCC 14.2.0 -O3 -march=native on an AMD Ryzen 7 PRO 8700GE (Debian 13, pinned core, median of 7): pool allocate/free 2.00 ns vs 6.03 ns operator new/delete (3.0x), stack allocate/reset 1.99 vs 4.77 ns malloc/free (2.4x), 1,000-allocation frame 1205 vs 14385 ns (11.9x, inflated by the baseline's pointer-array allocation); free list ties or loses, thread-safe pool 0.60x. The bigger 4-24x ratios come from single 0.1 s CI runs against the macOS and MSVC system allocators on hosted runners.

## Use it when

- Many same-size objects (particles, entities, nodes) with a known upper count, where O(1) pop/push from a preallocated pool beats a general allocator's \~6 ns new/delete pair on glibc.
- Per-frame or per-request scratch memory that is released all at once: bump allocation plus a single reset() replaces thousands of individual free() calls.
- Windows MSVC or macOS builds, where the system allocator measured much slower (34.9 ns and 18.5 ns per 64-byte new/delete pair in CI) so even the free-list allocator came out ahead.
- As a readable, MIT-licensed reference or starting point for writing your own game-engine arena; the core files are a few hundred lines each.

## Skip it when

- As a general malloc replacement: there is no global operator new hook, no size classes and fixed capacity; use mimalloc, jemalloc or another listed general allocator instead.
- Multithreaded allocation hot paths: the thread-safe pool is a single global mutex and was slower than new/delete even uncontended on Linux (9.98 ns vs 6.03 ns, 0.60x); contention results are not published.
- Variable-size allocation on Linux: the free list matched glibc malloc with first-fit (4.66 vs 4.67 ns) and lost with best-fit (0.76x), and that was its best case with a one-block free list; search cost grows linearly with fragmentation.
- Code that needs destructors run on reset or pool teardown, or debug-checked ownership in Release: double frees and foreign pointers are caught only by Debug asserts.
- Projects wanting a mature dependency: 0 stars, single author, no tagged ecosystem users.

## How it is fast

The pool is an intrusive singly linked free list threaded through the unused fixed-stride blocks, so allocate and deallocate are an O(1) pointer pop and push with no size-class lookup or headers. The stack allocator is a bump pointer with alignment rounding, and a whole frame is released by resetting one pointer instead of 1,000 free calls. The free-list allocator is a classic address-sorted first-fit/best-fit list with block headers and coalescing on free, which is O(n) in free-list length and only ties glibc malloc on Linux. The thread-safe pool wraps the same pool in a std::mutex.

## Compared with alternatives

Pick it over general allocators like mimalloc, v8malloc or FastAlloc only when you control the allocation pattern and want an explicit fixed-size pool or frame arena; versus similar small arenas such as obstack (cleeus) or ArenaAllocator (privateMwb), it is the one with a pinned, repeated Linux benchmark, sanitizer CI on three platforms and configurable alignment.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the library (Threads::Threads); Catch2 3.5.0 and Google Benchmark 1.9.1 fetched by CMake only for tests and benchmarks |
| **Minimum toolchain** | C++20, CMake 3.20; CI covers GCC, Clang, Apple Clang 21 and MSVC 19.51 |
| **Platforms** | any (CI on Linux, macOS arm64, Windows); -march=native is opt-in via FAST_ALLOC_NATIVE_ARCH |
| **Thread safety** | Only ThreadSafePoolAllocator synchronises (std::mutex); Pool, Stack and FreeList need external locking. |
| **Drop-in for the baseline** | partial — explicit allocator objects with their own allocate/deallocate API; no operator new/malloc replacement and no std::allocator adapter |

## Gotchas

- Allocators return raw storage: deallocate() and reset() never run destructors, and stack allocations cannot be freed individually.
- Invalid sizes or non-power-of-two alignments throw std::invalid_argument (also in Release), while exhaustion returns nullptr, so callers must handle both.
- Pool and free-list deallocate validate ownership only with assert, so a pointer from the wrong pool silently corrupts the free list in Release builds.
- The recorded frame benchmark's malloc side also allocated and released a std::vector of pointers inside the timed loop (README note; benchmarks since changed), so the 11.9x Linux frame ratio overstates the gap and new runs are not comparable.

## Known shortcomings

- Pool, stack and free-list allocators only. The Linux free-list result is 1.0x/0.76x and the thread-safe pool 0.60x (slower). The free-list benchmark is the best case (a one-block list). Release builds check block ownership with assert only. The recorded malloc 'frame' baseline timed pointer-array allocation, so the 11.9x is inflated (the README says so).

## Caveats and trade-offs

Compares special-purpose pool, stack and free-list arenas, preallocated outside the timed loop, with the general system allocator, a weak baseline; no jemalloc or mimalloc comparison. On Linux the free-list matches malloc (first-fit) or is slower (best-fit, 0.76x), and the thread-safe pool is slower than new/delete on one thread (0.60x). The recorded malloc frame benchmark also allocated and released a pointer array inside the timed loop, which inflates the frame speedups (README says the setup has since changed and fresh results are not comparable). macOS and Windows tables are one CI repetition at 0.1 s minimum time on GitHub-hosted runners with no CPU model. Native CPU optimisation became opt-in on 2026-10-04, after the recorded run. 0 stars; not run.

Specialised fixed-size pool, stack and free-list allocators for game code, not general-purpose malloc replacements.

## Maintenance

Actively maintained (v1.2.0, 75 commits, last commit 2026-10-04) and MIT-licensed, small enough to vendor, but unproven in production with 0 stars and 0 issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** README Performance section gives Google Benchmark 1.9.1 code in benchmarks/ (bench_pool.cpp, bench_stack.cpp, bench_freelist.cpp, bench_threadsafe_pool.cpp) against operator new/delete and malloc/free, with GCC 14.2.0, -O3 -march=native (FAST_ALLOC_NATIVE_ARCH=ON), AMD Ryzen 7 PRO 8700GE, pinned CPU and 7 repetitions; the Linux row alone meets A. The macOS and Windows rows are single CI repetitions on runners with no CPU model given.
- **Verifier notes:** Numbers match the README tables exactly; the record's headline ranges mix the Linux run with the much larger Windows CI ratios, so claimed_speedup now separates them. baseline_stdlib widened because the three tables cover GCC/libstdc++, Apple Clang/libc++ and MSVC STL operator new.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/benchmarks/bench_pool.cpp>
  - <https://github.com/NotKeira/fast-alloc/commits>
- **Sources the enricher read:**
  - <https://github.com/NotKeira/fast-alloc>
  - <https://github.com/NotKeira/fast-alloc/issues>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/benchmarks/bench_pool.cpp>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/benchmarks/bench_stack.cpp>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/benchmarks/bench_freelist.cpp>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/benchmarks/bench_threadsafe_pool.cpp>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/src/pool_allocator.cpp>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/src/stack_allocator.cpp>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/src/freelist_allocator.cpp>
  - <https://raw.githubusercontent.com/NotKeira/fast-alloc/HEAD/src/threadsafe_pool_allocator.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/notkeira/fast-alloc`) · [data/wave11/enrich/raw/github_com_notkeira_fast_alloc.json](../../../data/wave11/enrich/raw/github_com_notkeira_fast_alloc.json) (enrichment confidence 0.75)

</details>
