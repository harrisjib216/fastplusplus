# smmalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Lock-free, thread-cached proxy allocator for small (16-992B) game allocations; passes everything else through to CRT malloc.

| | |
|---|---|
| **Beats** | CRT malloc/free (C runtime heap, the allocator under default operator new) |
| **Claimed result** | \~40 cycles/op with thread cache (README feature claim); \~3.9x CRT at 1 thread (92,615,384 vs 23,853,865) and \~2.6x CRT at 5 threads (38,303,161 vs 14,636,381) on i7-2600 (derived from page data); \~8.1x CRT at 1 thread on PS4 (36,065,574 vs 4,444,444) (derived from page data) |
| **Workload** | Multi-threaded small-object malloc/free stress test (the current harness uses random 16-80 byte sizes). The README tables give unlabeled per-allocator counts; the current harness, smmalloc_perf01.cpp with smmalloc_test_impl.inl, computes ops/sec. Covers 1-5 threads on Windows 10/i7-2600 and 1-4 threads on PS4, comparing smmalloc against CRT malloc, rpmalloc, Hoard, ltalloc, dlmalloc(+mutex) and mspace (PS4 only). |
| **Metric** | throughput |
| **Hardware** | Windows 10, Intel Core i7-2600; PlayStation 4 |
| **Adoption** | 335 stars; shipped in Warface (PS4, Xbox One, Switch) |
| **Last commit** | 2023-10-13 |
| **Links** | [repository](https://github.com/SergeyMakeev/smmalloc) · [benchmark](https://github.com/SergeyMakeev/smmalloc#performance) |

## Verdict

README's own (unreproduced, Tier C) tables show smmalloc's ops/sec beating CRT malloc/free on a multithreaded random 16-80B alloc/free stress test: \~3.9x at 1 thread and \~2.6x at 5 threads on Windows 10/i7-2600, and \~8.1x at 1 thread on PS4; neither table states the compiler or optimization flags used.

## Use it when

- Multithreaded C++ game/engine code with many repeated small (roughly 16-992B under the default partitioning) allocations and frees, e.g. per-frame temporaries
- You already have a general-purpose fallback allocator and just want a fast path for a handful of known hot small sizes
- Console targets where the platform default heap is a bottleneck (shipped in Warface on PS4, Xbox One, Switch)
- You can manage explicit thread-cache create/destroy calls as part of each worker thread's lifecycle
- You're fine choosing bucket counts/size classes up front rather than using a fully general allocator

## Skip it when

- You need a true process-wide drop-in replacement for operator new/malloc (no LD_PRELOAD/global-override support; issue #5 requesting this is open, unresolved since 2022)
- Your allocation sizes fall mostly outside the configured buckets — those pass straight through to the fallback allocator with no benefit
- You need active upstream maintenance: no commits since 2023-10-13, and several issues (plain-C usage, LD_PRELOAD, Conan packaging) are open and unanswered
- You need a pure C API/codebase — this is C++11 (templates, namespaces, std::atomic); issue #7 asking about plain-C use has no reply
- You need independently reproduced numbers or a stated compiler/optimization-flag methodology — the README benchmark names hardware but not compiler or flags

## How it is fast

Each thread keeps a small local cache (stack of up to SMM_MAX_CACHE_ITEMS_COUNT items per bucket) so most alloc/free calls touch no shared state. When a thread cache misses, each size-class bucket is backed by a lock-free singly-linked freelist using an atomic tagged-index (tag+offset packed into a 64-bit head) compare-and-swap to avoid ABA races without a lock. No per-allocation header/metadata is stored, so overhead is near zero, matching the README's own \~40-cycles-per-op figure for cache hits. Bucket sizes are computed algorithmically (default piecewise-linear partitioning) instead of via a lookup table.

## Compared with alternatives

Pick smmalloc over ltalloc or rpmalloc when you want a thin proxy layer restricted to a few known small size classes (e.g. per-frame game allocations) rather than a full malloc replacement; on the same i7-2600/CRT benchmark smmalloc's own reported numbers beat ltalloc (\~3.9x vs \~2.6x CRT at 1 thread) and it has real console shipping history (Warface on PS4/X1/Switch) that the smaller general-purpose siblings don't claim.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C++ standard library only: &lt;atomic&gt;, &lt;memory&gt;, &lt;array&gt;, etc.) |
| **Minimum toolchain** | C++11 (CMakeLists.txt sets CMAKE_CXX_STANDARD 11 / -std=c++11 for GCC) |
| **Platforms** | x86/x64; CI (GitHub Actions) builds and runs tests on Ubuntu and macOS with g++/clang++ and on Windows (Win32 and x64) with MSVC; also shipped on PS4 per README, though PS4 isn't in public CI |
| **Thread safety** | Allocator instance and buckets are thread-safe via lock-free freelists with atomic tagged-index CAS; each thread must explicitly create and destroy its own thread-local cache (_sm_allocator_thread_cache_create/_destroy) around its use of the allocator |
| **Drop-in for the baseline** | partial — same malloc/free/realloc-shaped verbs but proxy-only: only configured bucket sizes get the fast path, everything else is forwarded to a separate fallback allocator (CRT malloc in the sample) |

## Gotchas

- Must call _sm_allocator_thread_cache_create for every thread that allocates/frees through smmalloc and destroy it before the thread exits, or you lose the fast path or leak the cache
- Bucket count and total pool size are fixed at _sm_allocator_create time; undersizing them silently routes more traffic to the fallback allocator with no error
- The three bucket-size partitioning schemes (linear/piecewise-linear/float) are compile-time #defines, not runtime options — switching requires recompiling smmalloc
- No per-allocation size/metadata is stored, so _sm_free/_sm_msize must be called against the same allocator instance that produced the pointer; mixing instances is undefined behavior

## Caveats and trade-offs

README benchmark states hardware but not compiler or optimization flags, so capped at Tier C rather than A/B; numbers are raw op counts from the project's own charts/tables, not independently reproduced. No commits since 2023.

Proxy allocator: only handles configured small-size buckets, passes everything else through to a fallback allocator; requires explicit per-thread cache create/destroy calls; not a drop-in std::allocator without a wrapper.

## Maintenance

Maintenance is stale (no commits since 2023-10-13, and issues on LD_PRELOAD support and plain-C usage remain open and unanswered), but it's MIT-licensed, dependency-free, and small enough (4 source files) to vendor as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance tables compare smmalloc against the CRT malloc baseline (the 'crt' row; smmalloc_perf01.cpp defines it as malloc/free) on a named CPU (i7-2600) and on PS4. The benchmark code is public, but no compiler or flags are stated, so these are first-party numbers with partial methodology: Tier C.
- **Verifier notes:** All table numbers check out. The ratios were missing the '(derived from page data)' marker, so it is now added. The CRT baseline is malloc/free, not operator new, and the README does not label the units (the harness computes ops/sec). Metadata matches: MIT, 335 stars, last commit 2023-10-13, stale.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `workload`
- **Pages the verifier opened:**
  - <https://github.com/SergeyMakeev/smmalloc>
  - <https://github.com/SergeyMakeev/smmalloc#performance>
  - <https://github.com/SergeyMakeev/smmalloc/blob/master/smmalloc_perf01.cpp>
  - <https://github.com/SergeyMakeev/smmalloc/blob/master/smmalloc_test_impl.inl>
- **Sources the enricher read:**
  - <https://github.com/SergeyMakeev/smmalloc>
  - <https://github.com/SergeyMakeev/smmalloc#performance>
  - <https://github.com/SergeyMakeev/smmalloc/blob/master/SmMalloc/smmalloc.h>
  - <https://github.com/SergeyMakeev/smmalloc/blob/master/CMakeLists.txt>
  - <https://github.com/SergeyMakeev/smmalloc/blob/master/.github/workflows/build.yml>
  - <https://github.com/SergeyMakeev/smmalloc/issues>
  - <https://github.com/SergeyMakeev/smmalloc/issues/7>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/sergeymakeev/smmalloc`) · [data/wave1/enrich/raw/github_com_sergeymakeev_smmalloc.json](../../../data/wave1/enrich/raw/github_com_sergeymakeev_smmalloc.json) (enrichment confidence 0.6)

</details>
