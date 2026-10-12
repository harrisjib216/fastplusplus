# metapool

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only, TLS pool allocator with compile-time size classes; up to 1380x faster reserve() than std::vector, 3.6x vs pmr::vector.

| | |
|---|---|
| **Beats** | std::allocator (via std::vector), std::pmr::unsynchronized_pool_resource |
| **Claimed result** | README headline: up to 1300x faster construction and reserve() than std::vector and up to 3.5x faster than std::pmr::vector. Results image: reserve microbenchmark 939.81x-1380.19x faster than std::vector (one outlier of 4762.93x at large2) and 2.65x-3.63x faster than pmr::vector; emplace 1.20x-1.61x faster than std; selective construct path 1.21x-15.40x faster than std; churn simulation ranges from 1.58x slower to 1.66x faster than std; raw alloc 1.81x-287.40x faster than malloc. |
| **Workload** | Construction and reserve() of mtp::vault (pool-backed dynamic array) vs std::vector (std::allocator/ptmalloc) and std::pmr::vector (pmr pool + monotonic_buffer_resource), across element counts. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 PRO 8840U, Arch Linux kernel 6.15.8, glibc 2.42 (ptmalloc), 64GB DDR5 |
| **Compiler and flags** | clang 20.1.8; -O3 -march=native -fstrict-aliasing -flto |
| **Adoption** | 37 stars |
| **Last commit** | 2026-02-21 |
| **Links** | [repository](https://github.com/esterlein/metapool) · [benchmark](https://github.com/esterlein/metapool#benchmark) |

## Verdict

On an AMD Ryzen 7 PRO 8840U (Arch Linux, glibc 2.42/ptmalloc, clang 20.1.8, -O3 -march=native -fstrict-aliasing -flto), metapool's mtp::vault construction+reserve() beat std::vector (std::allocator/ptmalloc) by roughly 940x-1380x (one 4763x outlier) and beat std::pmr::vector (pmr pool resource + monotonic_buffer_resource) by 2.65x-3.63x in the reserve microbenchmark; in the more representative emplace_back benchmark the margin over std::vector was only 1.2x-1.6x, and a churn simulation ranged from 1.58x slower to 1.66x faster than std depending on element size.

## Use it when

- Game/simulation-style workloads with known, stable allocation size distributions that can be pre-declared in a metaset
- Hot single-thread loops doing frequent same-size alloc/dealloc or reserve() cycles, where the TLS lock-free path beats malloc/free churn
- Codebases that can adopt the std::allocator or std::pmr::memory_resource adapter to plug metapool into existing containers without rewriting them
- Bounded working sets that fit a preallocated arena, where avoiding heap/kernel allocation variance matters (e.g. real-time frame loops)
- Projects already on a C++23-capable compiler (tested: clang 20.1.8) that are fine vendoring a header-only library

## Skip it when

- Allocation sizes are unpredictable or span a wide unbounded range: no fallback exists beyond the configured strides
- Multiple threads need to share one allocator instance concurrently: no mutex/atomic found in the reviewed source, so mtp::shared is not proven thread-safe without external locking
- You need organic growth past the compile-time arena: exhaustion calls a noreturn fatal() that terminates the process, and reset() invalidates all live objects without running destructors
- Toolchain is not C++23-capable, or you need verified GCC/MSVC/ARM support (only clang 20.1.8 on x86-64 is documented/tested)
- You're chasing the headline &gt;1000x number: that figure is from a single-vector reserve()/destroy microbenchmark dominated by glibc malloc/free of large blocks; realistic emplace_back gains are only 1.2x-1.6x, and one churn case (4096B/16384B elements) is up to 1.58x slower than std

## How it is fast

Allocations are grouped into stride (size-class) segregated freelists, each an intrusive singly-linked list carved once from a monotonic arena, so alloc/free are O(1) pointer push/pop with a 2-byte inline per-block header for O(1) stride lookup on free. Instances are thread-local by default, so the hot path needs no locking or atomics (confirmed: no mutex/atomic in allocator.hpp, freelist.hpp, or memory_model.hpp). The arena is sized to fit L1/L2 cache and is grabbed once, avoiding the malloc/free syscalls and heap bookkeeping std::vector triggers on every reserve().

## Compared with alternatives

All 10 catalogued siblings (NUMAlloc, SuperMalloc, Hoard, scalloc, both arena-allocators, ltalloc, rpmalloc, smmalloc, SpeedMalloc) are general-purpose malloc/operator-new replacements. metapool is the only one requiring compile-time, per-workload tuning of a fixed stride layout (metaset) instead of being a drop-in allocator — pick it when allocation sizes are known ahead of time and you want a header-only, TLS, lock-free pool packed into L1/L2 cache (e.g. a game engine's per-frame allocations); pick a general allocator like rpmalloc or smmalloc instead when sizes vary unpredictably or you need a true whole-app malloc replacement.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C++23; tested with clang 20.1.8 (no GCC/MSVC verification found) |
| **Platforms** | x86-64 tested (AMD Ryzen 7 PRO 8840U, Arch Linux); no ARM/other-arch support documented in files reviewed |
| **Thread safety** | not documented explicitly; source shows a thread_local default instance (no cross-thread sharing) and a mtp::shared variant with no mutex/atomic anywhere in allocator.hpp, freelist.hpp, or memory_model.hpp — treat concurrent access to a shared instance as unsynchronized |
| **Drop-in for the baseline** | partial — explain: the std::allocator and std::pmr::memory_resource adapters let metapool back existing std/pmr containers directly, but the flagship mtp::vault container is a separate API from std::vector, not a drop-in replacement |

## Gotchas

- MTP_ASSERT (bounds/pointer sanity checks throughout the alloc/free path) compiles to a no-op under NDEBUG, so release builds skip these checks entirely
- Total freelist exhaustion across all strides calls a [[noreturn]] fatal() that prints a framed error to stderr and terminates the process — this is not a C++ exception and cannot be caught
- reset() (needed to reclaim arena space) invalidates all previously constructed objects without calling destructors
- Allocations round up to the nearest configured stride; a gap in the metaset (e.g. smallest stride 1024B for a 2B request) wastes the difference per block

## Caveats and trade-offs

The \~1000x+ figures come only from the reserve microbenchmark, where each frame creates one std::vector, calls reserve(count), and frees it. glibc malloc/free of large blocks likely dominates that path, so it is not general alloc/free churn. In the more realistic tables the gains shrink to 1.2x-1.6x (emplace), and churn simulation is 1.06x-1.58x slower than std for 4096B and 16384B elements. Results are published only as a PNG image. New project (created Aug 2025, 37 stars) with no independent verification found.

Compile-time fixed pool layout (metaset) must be tuned per workload; no general fallback beyond configured strides; header-only but requires C++23; cannot grow arbitrarily beyond the preallocated arena without a reset.

## Maintenance

Active (last commit 2026-02-21), MIT-licensed, header-only and small enough to vendor; but a young single-author project (created Aug 2025, 37 stars, 3 forks, 0 open issues) with benchmark results published only as a PNG and no independent verification found.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public in benchmark/ (benchmark_micro.hpp, benchmark_selective.hpp, CMakeLists.txt, build.sh), and the README states clang 20.1.8, -O3 -march=native -fstrict-aliasing -flto, and an AMD Ryzen 7 PRO 8840U. It compares directly against std::vector with std::allocator and against std::pmr::unsynchronized_pool_resource. Flags are stated, so the &gt;50x cap does not apply.
- **Verifier notes:** Headline numbers match the README text and the results image. baseline_stdlib = libstdc++ is inferred: build.sh adds -stdlib=libc++ only on macOS, and the test system is Arch Linux clang, which defaults to libstdc++. Per-case numbers were read from the results PNG (https://github.com/user-attachments/assets/c7692e54-...).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/esterlein/metapool>
  - <https://github.com/esterlein/metapool#benchmark>
  - <https://github.com/user-attachments/assets/c7692e54-3de6-4ac2-beed-31a98bbf6b73>
  - <https://github.com/esterlein/metapool/blob/master/benchmark/CMakeLists.txt>
  - <https://github.com/esterlein/metapool/blob/master/benchmark/build.sh>
  - <https://github.com/esterlein/metapool/blob/master/benchmark/benchmark_micro.hpp>
- **Sources the enricher read:**
  - <https://github.com/esterlein/metapool>
  - <https://github.com/esterlein/metapool#benchmark>
  - <https://github.com/esterlein/metapool/blob/master/license>
  - <https://github.com/esterlein/metapool/blob/master/mtp_memory.hpp>
  - <https://github.com/esterlein/metapool/blob/master/container/vault.hpp>
  - <https://github.com/esterlein/metapool/blob/master/mtp/fail.hpp>
  - <https://github.com/esterlein/metapool/blob/master/mtp/metapool.hpp>
  - <https://github.com/esterlein/metapool/blob/master/mtp/freelist.hpp>
  - <https://github.com/esterlein/metapool/blob/master/mtp/freelist_proxy.hpp>
  - <https://github.com/esterlein/metapool/blob/master/mtp/allocator.hpp>
  - <https://github.com/esterlein/metapool/blob/master/mtp/monotonic_arena.hpp>
  - <https://github.com/esterlein/metapool/blob/master/mtp/mtpint.hpp>
  - <https://github.com/esterlein/metapool/blob/master/mtp/memory_model.hpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/esterlein/metapool`) · [data/wave1/enrich/raw/github_com_esterlein_metapool.json](../../../data/wave1/enrich/raw/github_com_esterlein_metapool.json) (enrichment confidence 0.62)

</details>
