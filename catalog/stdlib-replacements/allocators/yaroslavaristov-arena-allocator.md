# arena-allocator (yaroslavaristov)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Bump-pointer mmap arena for single-threaded HFT hot paths; O(1) allocate/reset, 10x-27x faster than malloc/free.

| | |
|---|---|
| **Beats** | malloc/free (system C allocator; the benchmark calls malloc/free directly, not operator new/delete) |
| **Claimed result** | 10x-27x faster sequential allocation than malloc on AMD EPYC 7763 (N=1 to 1024 objects), 15x faster on a mixed-size batch; on Apple M1 (virtualized) 32x-342x faster sequential allocation and 15x on the mixed batch |
| **Workload** | Google Benchmark: allocate N (1-1024) 64-byte objects then release them in bulk (arena reset() vs N free() calls, both inside the timed loop), plus a mixed 8/64/256-byte alloc+release batch |
| **Metric** | latency |
| **Hardware** | AMD EPYC 7763 (GitHub Codespaces, x86_64, native); Apple M1 (aarch64, via OrbStack virtualization -- author notes 'not native hardware') |
| **Compiler and flags** | g++-14 (hard-coded via CMAKE_CXX_COMPILER in CMakeLists.txt; exact minor version not stated), C++23, Release: -O3 -march=native -funroll-loops -Wall -Wextra -Werror -DNDEBUG |
| **Adoption** | 1 star |
| **Last commit** | 2026-07-21 |
| **Links** | [repository](https://github.com/yaroslavaristov/arena-allocator) · [benchmark](https://github.com/yaroslavaristov/arena-allocator#benchmark-results) |

## Verdict

On AMD EPYC 7763 (GitHub Codespaces, g++-14, C++23, Release flags -O3 -march=native -funroll-loops -DNDEBUG) the arena beat sequential malloc/free by 10x-27x for N=1 to 1024 64-byte objects, and by 15x on a mixed 8/64/256-byte alloc-then-release batch. The same benchmark binary showed 32x-342x and 15x respectively on an Apple M1, but that run was under OrbStack virtualization, which the README itself flags as not native hardware.

## Use it when

- Single-threaded HFT-style hot path: allocate a batch of same-lifetime objects (the benchmarks cover 1-1024 objects, 8-256 bytes each) then discard them all together
- Latency-critical loop where malloc/free tail latency or heap fragmentation is the risk you're trying to eliminate
- A fixed, known-upfront capacity is acceptable and can be rounded up to a power of two
- Linux x86-64 or aarch64 with mmap/mlock available (and tolerance for a stderr warning if HugePages or mlock aren't permitted)
- Already on C++23 with GCC 14+ or Clang 17+, so the toolchain floor isn't a blocker

## Skip it when

- Need to free individual objects before the whole batch ends -- there is no per-object free, only bulk reset()
- Variable or unbounded total allocation size -- capacity is fixed at construction, must be a power of two, and allocate() silently returns nullptr on overflow (callers must check)
- Multi-threaded access to one arena instance -- the class docstring says 'Not thread-safe', no internal synchronization exists
- Need a vetted, general-purpose replacement for malloc/new across a codebase -- this is a single header from one contributor, 1 GitHub star, unaudited, merged in the last two months
- Portability across OSes matters -- Linux-only (mmap/mlock/MAP_HUGETLB), plus a C++23 + GCC14/Clang17 floor rules out older toolchains

## How it is fast

It sidesteps the general-purpose allocator entirely: one mmap/mlock call reserves and pre-faults memory at construction, and allocate() does alignment and bounds checking with bitwise arithmetic on a raw pointer, no heap metadata, freelist, or locking involved. Bulk deallocation is a single pointer reset instead of N individual free() calls, so malloc's per-call bookkeeping and heap fragmentation (visible in the README's own numbers as N grows) never happen on the arena side.

## Compared with alternatives

Pick this over metapool or the ShortAlloc-based arena-allocator when you specifically want an mmap+HugePage-backed arena with mlock'd pages for HFT-style latency floors and don't need per-object free. metapool and ShortAlloc both report much larger multiples on their own benchmarks (up to 1300x and up to 230x respectively), so this entry is not the fastest arena catalogued -- it's a smaller, simpler single-header alternative with a narrower feature set (no per-object free, no stack-allocated buffer option).

## Integration

| | |
|---|---|
| **Form** | header-only (include/arena.hpp) |
| **Dependencies** | none for the library; Google Benchmark is only a dependency of the benchmark target |
| **Minimum toolchain** | C++23, GCC 14+ or Clang 17+ (README-stated requirement); CMakeLists.txt additionally hard-pins CMAKE_CXX_COMPILER to g++-14 |
| **Platforms** | Linux only -- relies on mmap, mlock, and MAP_HUGETLB; no Windows or macOS support documented |
| **Thread safety** | Not thread-safe, per the class docstring ('Designed for single-threaded HFT critical paths'); the header's separate top-of-file comment calling it a 'Lock-free arena allocator' contradicts this and appears to be a mislabel -- there is no synchronization in the code |
| **Drop-in for the baseline** | false -- different API shape: allocate&lt;T, Alignment&gt;(count) is templated and returns nullptr instead of throwing on overflow, there is no delete/free (only bulk reset()), and the arena itself is move-only and must be constructed with an explicit power-of-two byte capacity |

## Gotchas

- Capacity must be an exact power of two or the constructor throws std::invalid_argument
- allocate&lt;T&gt;() returns nullptr (not an exception) when the arena is exhausted -- callers must check the return value
- reset() invalidates every previously returned pointer at once; nothing tracks or flags which pointers are now dangling
- Header comment says 'Lock-free arena allocator' but the class docstring says 'Not thread-safe' -- treat it as strictly single-threaded, not lock-free-safe for concurrent use

## Caveats and trade-offs

Very new (last commit 2026-07-21), 1-star personal project, not peer reviewed. EPYC 7763 numbers come from a shared GitHub Codespaces VM. The largest multiples (97x-342x on Apple M1) were measured under OrbStack virtualization, which the README itself calls not native hardware; the malloc side there may be a non-glibc libc. The workload favors a bump allocator by construction: the arena releases everything with one O(1) reset while malloc pays N individual frees, and the arena has no per-object free.

Bump-pointer only: no per-object free, just a bulk reset(); fixed power-of-two capacity decided at construction; not a general-purpose allocator (no fragmentation handling, no shrink/grow); single header, single contributor, unaudited.

## Maintenance

Actively maintained (last commit 2026-07-21), MIT-licensed and small enough to vendor as one header, but it is a 1-star, single-contributor, zero-open-issues project with no external audit or peer review.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to A. The benchmark code is public (benchmarks/bench.cpp, Google Benchmark, arena vs malloc/free), and CMakeLists.txt pins the compiler to g++-14 with Release flags -O3 -march=native -funroll-loops -DNDEBUG. The README names the CPUs (AMD EPYC 7763; Apple M1 under OrbStack). The &gt;50x cap does not apply because flags are stated.
- **Verifier notes:** All README numbers match the record (10x-27x and 15x on EPYC; 32x-342x and 15x on M1). The tier is upgraded to A because the compiler (g++-14) is pinned in CMakeLists.txt and flags plus CPU are stated. If the pipeline requires the compiler to be named on the results page itself, it drops back to C.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/yaroslavaristov/arena-allocator>
  - <https://github.com/yaroslavaristov/arena-allocator#benchmark-results>
  - <https://github.com/yaroslavaristov/arena-allocator/blob/main/benchmarks/bench.cpp>
  - <https://github.com/yaroslavaristov/arena-allocator/blob/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/yaroslavaristov/arena-allocator>
  - <https://github.com/yaroslavaristov/arena-allocator#benchmark-results>
  - <https://github.com/yaroslavaristov/arena-allocator/blob/main/README.md>
  - <https://github.com/yaroslavaristov/arena-allocator/blob/main/include/arena.hpp>
  - <https://github.com/yaroslavaristov/arena-allocator/blob/main/CMakeLists.txt>
  - <https://github.com/yaroslavaristov/arena-allocator/blob/main/benchmarks/bench.cpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/yaroslavaristov/arena-allocator`) · [data/wave1/enrich/raw/github_com_yaroslavaristov_arena_allocator.json](../../../data/wave1/enrich/raw/github_com_yaroslavaristov_arena_allocator.json) (enrichment confidence 0.7)

</details>
