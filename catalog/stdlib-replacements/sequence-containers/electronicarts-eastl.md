# eastl::vector (EASTL)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> EA's from-scratch STL reimplementation for games; eastl::vector targets faster push_back/indexing than std::vector.

| | |
|---|---|
| **Beats** | std::vector |
| **Claimed result** | push_back ratio (std STL time / EASTL time) by platform: 1.63x on Windows/Pentium4/VC8, 2.18x on 64-bit PowerPC console/VC7, 1.02x on Linux/Pentium4/GCC4.1/libstdc++, 1.59x on Mac OS X G5 PowerPC/GCC4.0/libstdc++; operator[] on Linux/libstdc++ was 1.29x; sort on Linux/libstdc++ was 0.92x (i.e. slightly slower than std STL) |
| **Workload** | vector&lt;uint64&gt; erase/insert/iteration/operator[]/push_back/sort micro-benchmarks from the original EASTL design paper's benchmark appendix |
| **Metric** | throughput |
| **Hardware** | Pentium 4 x86 (Windows/Linux), 64-bit PowerPC console, Mac G5 PowerPC 32-bit |
| **Compiler and flags** | Linux: GCC 4.1 -O3; Mac: GCC 4.0 -Os; Windows: VC8 -Og -Oi -Ot -Oy -Ob2 -GF -Gy; Console: VC7 -Ox -Ob2 -Oi -Os |
| **Adoption** | 9,367 stars; used across Electronic Arts game engines |
| **Last commit** | 2025-10-29 |
| **Links** | [repository](https://github.com/electronicarts/EASTL) · [benchmark](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2007/n2271.html) |

## Verdict

The only available measurement is a first-party 2007 EA/WG21 committee paper (N2271, evidence tier C) comparing eastl::vector&lt;uint64&gt; against std::vector: push_back was 1.63x faster on Windows/Pentium4/VC8, 2.18x on a 64-bit PowerPC console/VC7, 1.02x on Linux/Pentium4/GCC4.1/libstdc++, and 1.59x on Mac G5 PowerPC/GCC4.0/libstdc++; operator[] on Linux/libstdc++ was 1.29x faster; sort on Linux/libstdc++ was 0.92x (slower than std::sort).

## Use it when

- Game/console codebases where debug (unoptimized) container performance matters and you can standardize on one non-standard container library across all target platforms
- Workloads dominated by push_back/reallocation of trivially-copyable structs, where the memcpy/memmove optimization applies
- You also want fixed_vector/intrusive_list-style zero-allocation containers alongside vector, not just a faster vector
- Targeting older or console toolchains (VC7/VC8-era, GCC 3.x+) where std STL implementations were measurably weak
- You're comfortable vendoring a large source-drop plus its EABase dependency rather than a single header

## Skip it when

- You need a literal drop-in for std::vector with zero porting cost: allocator model, exception semantics, and operator= behavior differ
- You're on an EASTL release older than 3.27.00 (Oct 2025): eastl::vector::push_back(v.back()) (self-referential push_back) silently corrupted data on reallocation (issue #524), fixed only in that release
- Concurrent writers without your own locking: EASTL containers are not thread-safe for mutation from multiple threads, same as std::vector
- You need certainty of a speedup on current hardware: the only public numbers are a first-party 2007 WG21 paper (evidence tier C) on Pentium 4/PowerPC-era hardware and compilers; libstdc++ push_back gain was only 1.02x and eastl::sort was 0.92x (slower) than std::sort on libstdc++
- Sort-heavy workloads on libstdc++-class standard libraries, where the same paper showed EASTL losing to std::sort

## How it is fast

EASTL avoids the deep, virtual-free but call-heavy chains that make debug-build STL slow, so its win is largest in unoptimized builds and on weak historical STL implementations (MSVC VC7/VC8, console STL). For trivially-copyable element types it uses memcpy/memmove during vector reallocation instead of invoking copy/move constructors per element (documented in doc/Gotchas.md). It also guarantees no allocation for a newly-constructed empty container and supports fully disabling exception handling, removing that overhead from the container/allocator path.

## Compared with alternatives

Pick eastl::vector when you want one consistent container ecosystem (fixed_\*, intrusive_\*, allocator model) across an entire codebase, especially on older/console toolchains, rather than swapping in a single faster vector type. For a narrowly-scoped, better-evidenced vector replacement alone, fast_vector or veque have more direct current benchmarks; plf::colony is the better pick if the workload is erase-heavy rather than push_back-heavy.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | EABase (EA's base config/type-traits header library; CMakeLists.txt fetches it via FetchContent) |
| **Minimum toolchain** | C++14 per CMakeLists.txt (target_compile_features cxx_std_14), but include/EASTL/vector.h currently uses unguarded `if constexpr`, which warns/fails below C++17 (open issue #587) -- C++17 recommended in practice |
| **Platforms** | any C++14+ compiler, 32-bit and 64-bit; no OS-specific code path required, historically used across PC, console, and Mac/Linux toolchains |
| **Thread safety** | Not thread-safe for concurrent mutation of the same container instance; per doc/FAQ.md, EASTL uses no static/global state and leaves synchronization (e.g. a mutex) to the caller, same model as std::vector |
| **Drop-in for the baseline** | partial -- explain: same template surface and most member functions as std::vector, but allocator interface, exception-handling toggle, and operator=() (doesn't copy the allocator) differ from the standard |

## Gotchas

- eastl::vector::push_back(v.back()) (self-referential push_back) silently corrupted data on reallocation before release 3.27.00 (Oct 2025) -- pin to &gt;=3.27.00 (issue #524)
- vector::operator=() does not copy the source container's allocator, unlike some std implementations
- vector::size() is computed by pointer subtraction and can trigger an integer division when sizeof(T) isn't a power of two
- Overriding the global allocator requires supplying EASTL's two custom operator new[] overloads, not a standard C++ allocator

## Caveats and trade-offs

Data is from a 2007 WG21 paper, a first-party EA submission and not peer-reviewed or independent. Hardware (Pentium 4, G5 and console PowerPC) and compilers (GCC 4.0/4.1, VC7/8) are about two decades old. On libstdc++ the push_back gain is only 1.02x; the larger wins are against compiler-supplied MSVC STL (VC8) and the console VC7 STL. On Linux/libstdc++, sort (0.92x) was slower. The current repo ships benchmark/source/BenchmarkVector.cpp, but no recent published numbers confirm these ratios.

Different allocator model and some container semantics diverge from the standard; results are inconsistent across operations (sort was slower on libstdc++), so 'faster' is workload- and platform-dependent rather than universal

## Maintenance

Actively maintained by EA (latest release 3.27.01, Nov 2025), BSD-3-Clause, 9,367 stars; usable via source-drop or CMake, but it's a large, non-trivial dependency (EABase plus a big header/source tree), not a lightweight vendor-in.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** N2271 Appendix item 20 is a first-party performance table from EA, not peer-reviewed and not an independent suite. It shows the vector&lt;uint64&gt; ratios exactly as claimed (push_back 1.63/2.18/1.02/1.59; Linux operator[] 1.29; sort 0.92). It is not A: the paper's benchmark source is only 'distributed with this document' and not linked, and the CPU is given only by family (Pentium 4, 64-bit PowerPC, G5).
- **Verifier notes:** All ratios were verified in the Appendix 20 table (columns: A Windows VC8, B Console VC7, C Linux GCC 4.1/libstdc++, D Mac GCC 4.0/libstdc++). Tier lowered from B to C because a first-party committee paper is not peer review. last_commit corrected to the default-branch commit date; 2025-11-15 was pushed_at from another branch. Still active; BSD-3-Clause, 9,367 stars.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2007/n2271.html>
  - <https://github.com/electronicarts/EASTL>
  - <https://github.com/electronicarts/EASTL/tree/master/benchmark/source>
- **Sources the enricher read:**
  - <https://github.com/electronicarts/EASTL>
  - <https://github.com/electronicarts/EASTL/blob/master/doc/Introduction.md>
  - <https://github.com/electronicarts/EASTL/blob/master/doc/FAQ.md>
  - <https://github.com/electronicarts/EASTL/blob/master/CONTRIBUTING.md>
  - <https://github.com/electronicarts/EASTL/blob/master/CMakeLists.txt>
  - <https://github.com/electronicarts/EASTL/blob/master/doc/Gotchas.md>
  - <https://github.com/electronicarts/EASTL/issues/524>
  - <https://github.com/electronicarts/EASTL/issues/587>
  - <https://github.com/electronicarts/EASTL/releases>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/electronicarts/eastl`) · [data/wave1/enrich/raw/github_com_electronicarts_eastl.json](../../../data/wave1/enrich/raw/github_com_electronicarts_eastl.json) (enrichment confidence 0.4)

</details>
