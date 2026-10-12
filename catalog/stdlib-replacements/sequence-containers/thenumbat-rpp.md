# rpp (TheNumbat/rpp) compile-time-oriented containers and allocators

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟡 stale

> Rust-style C++20 base library (Vec, Map, String, allocators, threads, async) that avoids STL headers to cut compile time.

| | |
|---|---|
| **Beats** | std::vector, std::unordered_map and the other STL container headers (MSVC STL) |
| **Claimed result** | Unverified here (seen only by the search agent in a search snippet of the blocked 'Oxidizing C++' post): slowest translation unit about 10 s in the MSVC frontend for an earlier STL-based project vs 1.4 s for a separate, roughly 100k-line rpp-based project (about 7x, derived from page data, not like-for-like); rpp's core header under 200 ms per translation unit on average; optimized build under 3 s. The repo README only lists 'Fast Compilation' and 'High Performance' as goals, without numbers. |
| **Workload** | Author's anecdotal whole-project comparison: an earlier STL-based project against a rendering project of about 100k lines written on rpp, compared by frontend compile time per translation unit. |
| **Metric** | compile-time |
| **Hardware** | AMD 5950X, Windows 11 |
| **Compiler and flags** | MSVC 19.38 (flags not known) |
| **Adoption** | 218 stars, 5 forks |
| **Last commit** | 2024-12-25 |
| **Links** | [repository](https://github.com/TheNumbat/rpp) · [benchmark](https://thenumb.at/rpp/) |

## Verdict

Nothing measured could be seen this session: the blog post at thenumb.at is unreachable and the repo has no compile-time or runtime benchmark. The only figures, from a search-agent snippet, are an author anecdote comparing two separate codebases (slowest translation unit about 10 s with an earlier STL-based project versus 1.4 s for a roughly 100k-line rpp project, MSVC 19.38 on an AMD 5950X, Windows 11), which the author says is not a proper benchmark.

## Use it when

- A new MSVC or Clang 17+ codebase (game, renderer, tool) that wants short per-translation-unit compile times and is willing to adopt a non-STL vocabulary everywhere.
- Projects that want per-allocator leak checking and allocation statistics out of the box (named Mallocator&lt;"Name"&gt; types, Profile::finalize()).
- Code that benefits from scoped region (arena) allocation and fixed-size pools selected by a template parameter rather than by runtime allocator objects.
- As a readable reference for a compact Robin Hood map, Rust-style Opt/Box/Rc and static-allocator containers in C++20.

## Skip it when

- When you need a measured runtime speedup over std::vector or std::unordered_map: no benchmark exists, and the only numbers are an anecdotal compile-time comparison of two different codebases.
- GCC builds (rejected with #error in base.h and a FATAL_ERROR in CMake), MSVC before 19.39, Clang before 17, 32-bit targets (static_assert sizeof(void\*) == 8) or any OS other than Windows, Linux and macOS.
- Code that relies on exceptions, RTTI or STL interop: the library builds with -fno-exceptions/-fno-rtti (MSVC /EHa- /GR-, _HAS_EXCEPTIONS=0), and passing rpp containers to STL-based APIs needs conversion.
- Long-lived production dependencies: last commit 2024-12-25, one maintainer, no releases, 218 stars.
- Maps updated by repeated insert() of existing keys (see gotchas: length() overcounts and the table keeps growing).

## How it is fast

The compile-time claim rests on not including STL or most system headers: rpp re-implements the few std pieces the language needs (std/initializer_list.h, std/coroutine.h) and keeps the library at about 10k lines, built as one static library from unity-build .cpp files. Runtime choices are conventional: Vec grows by doubling from 8 and memcpy-relocates trivially movable types; Map is an open-addressing Robin Hood table with power-of-two capacity, 75% max load, a 64-bit 'squirrel5' integer-mix hash, top-bit indexing and backward-shift deletion, storing the full hash in every slot. No runtime benchmark against the STL exists in the repo.

## Compared with alternatives

Pick rpp only if you want a complete STL-free base library with compile time as the main goal; for a measured runtime win on vector-like containers with an STL-shaped API, EASTL's eastl::vector, ankerl::svector (small vectors) or sfl-library are better-documented choices.

## Integration

| | |
|---|---|
| **Form** | static lib (headers plus unity-build rpp/impl/unify.cpp and a platform unify.cpp; CMake add_subdirectory or git submodule) |
| **Dependencies** | none beyond the C runtime and OS (pthread on Linux and macOS; ws2_32 and Synchronization on Windows); base.h still includes &lt;new&gt; (Clang) or vcruntime_new.h (MSVC) |
| **Minimum toolchain** | C++20; MSVC 19.39+ or Clang 17+; CMake 3.17+ |
| **Platforms** | Windows x64 (MSVC), Linux x64 and aarch64 (Clang), macOS x64 and aarch64 (Clang); other Linux architectures untested |
| **Thread safety** | Containers are not synchronized; Mpool and the allocation profiler take a global mutex per call; Thread, Async::Pool and Arc are provided for concurrency |
| **Drop-in for the baseline** | no |

## Gotchas

- Map::insert and Map::emplace add 1 to length_ even when insert_slot finds the key already present and only overwrites it (map.h, insert(K&&, V&&) and the duplicate branch of insert_slot). length() then overcounts, and because full() compares length_ with 75% of capacity, a map whose existing keys are re-inserted keeps doubling its table; get_or_insert() checks first and is safe. Found by code reading; the test suite has no duplicate-insert case.
- Map::reserve(n) uses n as the capacity without rounding to a power of two, while clone() rebuilds at next_pow2(capacity) with a different shift and copies slots by position, so cloning a map reserved to a non-power-of-two size yields a table whose lookups can miss entries (code reading, not executed). try_erase also does not stop at an empty slot and scans on to the next occupied one.
- assert() is defined by rpp and stays active in Release: Vec and Slice indexing is bounds-checked, allocation failure asserts, and a failed check logs and calls exit(1).
- The default allocator (Mdefault) records every allocation and free in a global mutex-protected map unless RPP_RELEASE_BUILD is defined; the CMake file defines it only for Release and MinSizeRel, so RelWithDebInfo builds and builds without CMake pay that cost on every allocation. Mpool blocks are aligned to at most 16 bytes.

## Known shortcomings

- Downgraded C to D: the compile-time claim (10 s vs 1.4 s, snippet only; thenumb.at blocked) is a two-codebase anecdote the author calls not a proper benchmark, with no runtime benchmark in the repo; stale (2024-12-25), 218 stars.
- Enricher: no benchmark in the repo and the blog is unreachable, so tier D stands; Map insert/emplace of an existing key overwrites but still adds 1 to length_ (overcount, table keeps doubling on repeated overwrites); Map::reserve(n) does not round to a power of two and clone() copies slots by position into a next_pow2 table with a different shift, so clone lookups can miss (code reading); assert stays on in Release (bounds checks, exit(1)); Mdefault logs every allocation under a global mutex unless RPP_RELEASE_BUILD; macOS x64/aarch64 are supported and base.h includes &lt;new&gt; and &lt;pthread.h&gt;.

## Caveats and trade-offs

Snippet only and not re-confirmed: thenumb.at could not be opened (getaddrinfo ENOTFOUND for the search agent and the verifier), and the verifier's three WebSearch queries did not surface the post or its figures. Per the search agent's snippet, the author says it is not a proper benchmark because it compares two entirely separate codebases. Hardware and compiler (AMD 5950X, MSVC 19.38, Windows 11) also come from that snippet; the README lists MSVC 19.39+ and Clang 17+ as the supported compilers. Compile-time claim only: the README, the tree (rpp, test, .github) and the search results contain no runtime benchmark against std::vector, std::unordered_map or std::allocator, and no compile-time harness. README to-do list admits open performance items (Map still stores hashes of integer keys; Range_Allocator overhead; per-thread pools). Last commit 2024-12-25, so stale.

Not a drop-in STL: Rust-inspired own API (Vec, Map, String, Box, Rc, Opt, Region allocators with statically associated allocators), explicit code, no STL or system headers pulled in, about 10k lines. Supports only MSVC 19.39+ on x64 and Clang 17+ on x64 and aarch64 (GCC not supported); uses GCC/Clang vector extensions for SIMD; C++20 required.

## Maintenance

Stale since 2024-12-25 (one open issue, no releases) but MIT-licensed and about 10k lines, so vendoring is feasible for MSVC 19.39+/Clang 17+ projects; review the Map insert-count and reserve/clone issues before relying on Map.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** thenumb.at is unreachable here (getaddrinfo ENOTFOUND) and three WebSearch queries returned no snippet carrying the 10 s / 1.4 s, 200 ms or 3 s figures, while the repo README has no numbers and the repo has no compile-time or runtime benchmark, so no number could be seen. Even as the search agent reported it, the figure compares two separate codebases and the author calls it not a proper benchmark, so it is directional only.
- **Verifier notes:** Downgraded C to D: benchmark page blocked and the numbers could not be re-confirmed by any snippet; the claim is an anecdote comparing two different codebases (author admits not a proper benchmark), no benchmark in the repo, compile time only. Metadata checked: MIT, 218 stars, 5 forks, last commit 2024-12-25 (stale). Low notability (218 stars) noted, kept per keep-and-document policy.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-73 (wave 1, stdlib decomposition); enricher (wave 1 stdlib seeds, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/TheNumbat/rpp>
  - <https://github.com/TheNumbat/rpp/commits>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/TheNumbat/rpp>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/CMakeLists.txt>
  - <https://github.com/TheNumbat/rpp/tree/main/rpp>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/base.h>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/vec.h>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/map.h>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/hash.h>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/alloc0.h>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/alloc1.h>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/math.h>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/profile.h>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/log.h>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/std/initializer_list.h>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/impl/unify.cpp>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/impl/profile.cpp>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/rpp/impl/alloc.cpp>
  - <https://raw.githubusercontent.com/TheNumbat/rpp/HEAD/test/map.cpp>
  - <https://github.com/TheNumbat/rpp/commits>
  - <https://github.com/TheNumbat/rpp/issues?q=is%3Aissue>
  - https://thenumb.at/rpp/ (getaddrinfo ENOTFOUND)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/thenumbat/rpp`) · [data/wave1/enrich/raw/github_com_thenumbat_rpp.json](../../../data/wave1/enrich/raw/github_com_thenumbat_rpp.json) (enrichment confidence 0.55)

</details>
