# Bloodmoon001/memory-allocator

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 fixed-capacity, single-type pool with intrusive free list; about 10x faster than MSVC malloc/free on alloc-free pairs.

| | |
|---|---|
| **Beats** | malloc/free |
| **Claimed result** | README table: Single int allocate+free 2,731 ns vs 29,067 ns (10.6x); std::string create+destroy 7,240 vs 19,826 ns (2.7x); bulk 10,000 allocations 54,860 vs 433,902 ns (7.9x); throughput 188M vs 23M ops/s (8.1x). Per bench_allocator.cpp each 'single' iteration is a loop of 1024 alloc+free pairs (about 2.7 ns vs 28 ns per pair, derived from page data) and each string iteration is 256 create+destroy pairs. |
| **Workload** | Google Benchmark: 1024 back-to-back int alloc+free pairs per iteration (pool vs malloc/free and new/delete), 256 std::string create+destroy pairs, and bulk 100/1,000/10,000 int allocations (pool releases with an O(1) reset, malloc side frees each pointer). |
| **Metric** | throughput |
| **Hardware** | Intel i5-12450H, Windows 11 |
| **Compiler and flags** | MSVC 2022, Visual Studio x64-Release configuration (optimization flags not stated) |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/Bloodmoon001/memory-allocator) · [benchmark](https://github.com/Bloodmoon001/memory-allocator) |

## Verdict

Author-run Google Benchmark on an Intel i5-12450H, Windows 11, MSVC 2022 x64-Release (flags not stated): 1024 LIFO int alloc+free pairs take 2,731 ns vs 29,067 ns with malloc/free (about 2.7 vs 28 ns per pair), 256 std::string create+destroy take 7,240 vs 19,826 ns, and 10,000 bulk allocations take 54,860 vs 433,902 ns; the 188M vs 23M ops/s throughput row matches the bulk-10,000 row restated as items per second (derived from page data). In the bulk test the pool side releases with reset(), which re-links all 100,000 slots each iteration, while malloc frees each pointer, so the two sides do different release work.

## Use it when

- Single-threaded code that churns one small object type (nodes, messages, particles) with a known upper bound on live objects.
- Hot loops on Windows/MSVC where the CRT heap is the bottleneck and the objects never escape a single owner.
- Embedded or no-heap settings where a static, compile-time-sized arena for one type is wanted.
- As a teaching-sized (about 130 lines) pool to copy into a project and adapt.

## Skip it when

- Any multi-threaded use: there are no atomics or locks, and thread-safety is not documented.
- Mixed sizes or types, or an unknown maximum count: capacity is the template argument N and allocate() returns nullptr when exhausted, with no growth.
- Large N on the stack: slots_ is an inline array, so PoolAllocator&lt;int, 100000&gt; as used in the benchmark is 800 KB of stack, near the 1 MB Windows default.
- Code that needs std::allocator or pmr integration, or drop-in replacement of malloc/new.
- As evidence of beating mimalloc or glibc: only MSVC UCRT malloc was compared, and modern general allocators have thread-local fast paths for this pattern.

## How it is fast

Classic fixed-size pool (segregated free list): free slots store a next pointer inside themselves, so allocation pops the list head and deallocation pushes onto it, a few loads and stores with no size lookup, no locking and no header. Storage is a contiguous inline array, so a LIFO alloc/free loop keeps reusing one hot cache line. Against Windows UCRT malloc (a heap call per request) that is enough for about 2.7 ns vs 28 ns per pair.

## Compared with alternatives

Choose it over fast-alloc (NotKeira) or atul-singh-as/custom-memory-allocator only if you want the smallest single-header, single-type pool with create/destroy and owns(); for anything thread-safe or general-purpose, use a real allocator such as mimalloc or a TLSF like XenoAtom.Allocators, and for scoped bulk lifetime an arena such as cleeus/obstack.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (Google Test and Google Benchmark via vcpkg only for tests/bench) |
| **Minimum toolchain** | C++17 (uses std::byte); built with MSVC 2022, CMake 3.20+ for the project files |
| **Platforms** | any (portable C++17; only tested on Windows 11 x64 per README) |
| **Thread safety** | not documented; no synchronization in the code, so not thread-safe |
| **Drop-in for the baseline** | partial — explicit pool object with allocate/deallocate or create/destroy for one type T; not a malloc/new replacement |

## Gotchas

- reset() is O(N), not O(1): it re-links all N slots every call, and it does not run destructors of live objects; the destructor also leaves live objects undestroyed.
- deallocate() checks ownership only with assert, so in Release builds a foreign pointer or a double free silently corrupts the free list.
- allocate() returns uninitialised storage cast to T\*; use create() for non-trivial types. The free-list links are accessed through reinterpret_cast without std::launder.
- N = 0 is not rejected and the constructor then indexes slots_[N - 1].

## Known shortcomings

- reset() is O(N), not O(1): it relinks all 100,000 slots every bulk iteration, so the bulk harness is biased against the pool. The 188M vs 23M ops/s throughput row restates the bulk-10,000 row. No thread safety; double free is checked only by assert (unchecked in Release).

## Caveats and trade-offs

Bench is not like for like: the pool single-int loop reuses the same LIFO slot, and the pool bulk benchmark releases with an O(1) reset() and never uses DoNotOptimize on the returned pointers, while the malloc side frees every pointer individually. Windows UCRT malloc baseline is slow relative to glibc/mimalloc. Numbers taken from the README, not rerun. Fixed-size, single-threaded pool; thread-safety not stated. 3 commits.

Header-only C++17 fixed-size pool with intrusive free list, O(1) alloc/free; single-size slots only, not a general allocator; likely not thread-safe.

## Maintenance

Active but brand-new (3 commits, 0 stars, last commit 2026-09-29); MIT-licensed and tiny, so copyable, but a learning-project pool rather than a hardened allocator.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README table (i5-12450H, Windows 11, MSVC 2022 x64-Release) matches the claimed numbers and benchmarks/bench_allocator.cpp is public, but no compiler flags are stated (CMakeLists sets none; x64-Release is a Visual Studio configuration name, no CMakePresets.json in the repo), so not A; first-party, so C.
- **Verifier notes:** README speedups confirmed; harness biases recorded in caveats. MIT, 0 stars, not a fork, last commit 2026-09-29.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Bloodmoon001/memory-allocator/HEAD/README.md>
  - <https://raw.githubusercontent.com/Bloodmoon001/memory-allocator/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Bloodmoon001/memory-allocator/HEAD/benchmarks/bench_allocator.cpp>
  - <https://raw.githubusercontent.com/Bloodmoon001/memory-allocator/HEAD/CMakeLists.txt>
  - <https://github.com/Bloodmoon001/memory-allocator/commits>
- **Sources the enricher read:**
  - <https://github.com/Bloodmoon001/memory-allocator>
  - <https://raw.githubusercontent.com/Bloodmoon001/memory-allocator/HEAD/README.md>
  - <https://raw.githubusercontent.com/Bloodmoon001/memory-allocator/HEAD/include/alloc/PoolAllocator.h>
  - <https://raw.githubusercontent.com/Bloodmoon001/memory-allocator/HEAD/benchmarks/bench_allocator.cpp>
  - <https://raw.githubusercontent.com/Bloodmoon001/memory-allocator/HEAD/tests/test_allocator.cpp>
  - <https://raw.githubusercontent.com/Bloodmoon001/memory-allocator/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/bloodmoon001/memory-allocator`) · [data/wave11/enrich/raw/github_com_bloodmoon001_memory_allocator.json](../../../data/wave11/enrich/raw/github_com_bloodmoon001_memory_allocator.json) (enrichment confidence 0.8)

</details>
