# rpmalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Lock-free, per-thread-caching malloc replacement for C/C++, drop-in via LD_PRELOAD or override, faster than glibc/tcmalloc/jemalloc under threaded churn.

| | |
|---|---|
| **Beats** | crt (system glibc malloc on Ubuntu 16.10, backing operator new/delete); charts also include tcmalloc, ptmalloc3, jemalloc, lockfree-malloc, scalloc, lockless |
| **Claimed result** | Page text: rpmalloc is faster than all tested allocators except lockfree-malloc in a few cases when threads exceed cores; tcmalloc and jemalloc trail behind \~15%. Versus crt (glibc malloc), charts show about 2.3x at 1 thread and 3.4x at 4 threads in random [16,1000]B, and about 2.4x at 1 thread in [512,160000]B (derived from page data, read approximately from chart images). |
| **Workload** | Multi-threaded interleaved allocation/deallocation benchmark (random and fixed sizes 16B-160000B range, with cross-thread deallocation), measuring memory operations per CPU-second across thread counts. |
| **Metric** | throughput |
| **Hardware** | Ubuntu 16.10 machine with 8 logical cores (4 physical + HT) and 12GiB RAM; CPU model not stated. Windows 10 and macOS results are listed as 'coming soon' and are not published. |
| **Adoption** | 2.5k stars; used in Haiku OS |
| **Last commit** | 2026-07-15 |
| **Links** | [repository](https://github.com/mjansson/rpmalloc) · [benchmark](https://github.com/mjansson/rpmalloc-benchmark/blob/master/BENCHMARKS.md) |

## Verdict

Verifier-confirmed numbers come from the project's own (now separate) rpmalloc-benchmark suite run on one Ubuntu 16.10 machine (8 logical cores; CPU model and compiler unstated): roughly 2.3x crt (glibc malloc) throughput at 1 thread and 3.4x at 4 threads for random 16-1000B allocations, and about 2.4x at 1 thread for 512B-160000B allocations, all read approximately off chart images (tier C, no raw numbers in the page text). The suite's own 'lockless' allocator beats rpmalloc in the large-size chart, contradicting the page's 'faster than all tested allocators except lockfree-malloc' claim.

## Use it when

- Multi-threaded C/C++ workloads with heavy alloc/free churn, especially cross-thread frees (producer/consumer handoff) where lock contention dominates.
- Need a quick libc malloc swap to test allocator impact via LD_PRELOAD/DYLD_INSERT_LIBRARIES without recompiling the target binary.
- Want natural 16-byte alignment on every allocation without calling aligned-alloc variants.
- Want a small (\~3.3k-line core), single-vendor C11 allocator you can vendor as source and actually read.
- Workloads whose high/low allocation water-mark swing fits the free-page retention thresholds, so committed pages stay resident instead of thrashing decommit/recommit.

## Skip it when

- Code that relies on operator new throwing std::bad_alloc on OOM — rpnew.h's overrides call rpmalloc() directly and return null on failure instead of throwing, silently breaking exception-based OOM handling.
- You need a std::allocator-compatible type to plug into individual std:: containers rather than a global malloc replacement.
- Threads that touch a few blocks from many different size classes each commit a page per class, wasting resident memory versus a single shared arena.
- Windows with explicit huge pages enabled: huge-page-backed ranges can't be partially decommitted and stay committed until the whole span unmaps.
- Targets outside Windows/Linux/macOS/iOS/Android on x86-64/arm64 (also LoongArch, arm64ec per changelog) — no WASM or other embedded targets in CI.

## How it is fast

Each thread owns a private heap and the hot allocate/free path takes no locks. Memory is organized span (256MiB-aligned) -&gt; page -&gt; block by fixed size class, so free() locates the owning span/page header in O(1) by masking the pointer's low bits instead of a table lookup. Blocks freed by a non-owning thread are pushed to a per-page atomic deferred free list and reclaimed lazily by the owner thread, avoiding the double thread-cache hop other allocators pay on producer/consumer handoff.

## Compared with alternatives

Pick rpmalloc over the arena/pool-style siblings (metapool, the two arena-allocator entries, ShortAlloc) when you need a general-purpose, thread-safe, drop-in replacement for the whole process's malloc rather than a scoped bump/arena allocator for one object's lifetime; pick it over SuperMalloc, Hoard, scalloc, or NUMAlloc when you want a small, single-vendor, actively maintained C11 source you can vendor and read, instead of a research-grade or NUMA/HTM-specific allocator with heavier build or hardware requirements.

## Integration

| | |
|---|---|
| **Form** | source-drop (rpmalloc.c/h, \~3.3k LOC core; also builds as static/shared lib via configure.py + ninja) |
| **Dependencies** | none |
| **Minimum toolchain** | C11 (C++ optional, only needed for the operator new/delete override in rpnew.h) |
| **Platforms** | Windows, Linux (glibc and musl/Alpine), macOS, iOS, Android; x86-64 and arm64 covered in CI |
| **Thread safety** | Per-thread heaps with a lock-free hot alloc/free path; cross-thread frees are deferred to the owning thread via an atomic per-page free list. The optional first-class heap API (RPMALLOC_FIRST_CLASS_HEAPS) is explicitly not thread-safe — each heap object must be used by a single thread at a time. |
| **Drop-in for the baseline** | partial — explain: replaces the malloc-family functions via LD_PRELOAD/DYLD_INSERT_LIBRARIES or ENABLE_OVERRIDE=1, and overrides global operator new/delete (automatic on non-Windows, requires #include &lt;rpnew.h&gt; in exactly one translation unit on Windows), but it is not a std::allocator template for use with individual containers. |

## Gotchas

- Overridden operator new returns null on allocation failure instead of throwing std::bad_alloc (confirmed in rpnew.h — no null-check/throw logic anywhere in the override), breaking code that expects exception-based OOM handling.
- If rpmalloc is compiled as a static lib and the caller only ever invokes plain malloc/free (never an rp\*-prefixed symbol), the linker can drop the override object entirely; call the provided rpmalloc_linker_reference() dummy, or include rpmalloc.h in a translation unit, to force inclusion.
- On Windows, huge-page-backed memory can't be partially decommitted, so unused ranges stay committed until the whole span unmaps; on Linux, unused huge-page ranges are only decommitted on kernel 5.18+.
- The custom memory_map/memory_unmap interface changed in 2.0 (gained separate commit/decommit callbacks) and is not source-compatible with pre-2.0 custom map/unmap implementations.

## Caveats and trade-offs

Results come from the project's own suite. CPU model, compiler, and flags are not stated, and only Ubuntu 16.10 chart images are published, so ratios are approximate readings. Hoard is in the suite's code but not in the published charts. The page's 'faster than all except lockfree-malloc' text is contradicted in the [512,160000]B chart: 'lockless' beats rpmalloc at 1 thread (\~14.5 vs \~8.9 M ops/CPU-s) and roughly ties it at higher thread counts. rpmalloc also appears in daanx/mimalloc-bench as 'rp', but only as chart images whose allocator legend is not in the image.

Malloc replacement (override new/delete or LD_PRELOAD), not a std::allocator template; thread-caching adds roughly 10-15% memory overhead vs some allocators.

## Maintenance

Actively maintained (last commit 2026-07-15, current release 2.0.1) and public-domain/MIT dual-licensed; the verified crt numbers predate a major 2.0.0 architecture redesign (span-&gt;page-&gt;block replacing the earlier span-&gt;block design, confirmed in the CHANGELOG read this session), so they may not reflect current performance — the current README/BENCHMARKS.md use a newer mimalloc-bench-based methodology that has not been independently verified to this tier.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The project's own rpmalloc-benchmark suite (code public, benchmark/ with crt, jemalloc, and others) plots rpmalloc against crt (glibc malloc) on Ubuntu 16.10. CPU model, compiler, and flags are not stated, and results are chart images only, so it is C.
- **Verifier notes:** The claim text matches BENCHMARKS.md, but no numbers vs crt appear in text. The crt ratios come from 2 of the chart images and are marked approximate. Hoard was removed from the baseline list because it does not appear in the published charts. Repo metadata checks out (MIT, 2,508 stars, last commit 2026-07-15).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** Developer source's allocator selection put rpmalloc at about 2x glibc malloc on allocate/free churn (approximate figure, no per-row table published), the same order as jemalloc's measured 2.71x via LD_PRELOAD (11.738 to 4.33 ns). (developer source, private repo; selection measurement cited in docs/allocators.md and results/fastest.json row allocator_churn, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://github.com/mjansson/rpmalloc>
  - <https://github.com/mjansson/rpmalloc-benchmark>
  - <https://github.com/mjansson/rpmalloc-benchmark/blob/master/BENCHMARKS.md>
  - <https://docs.google.com/spreadsheets/d/1NWNuar1z0uPCB5iVS_Cs6hSo2xPkTmZf0KsgWS_Fb_4/pubchart?oid=1979506104&format=image>
  - <https://docs.google.com/spreadsheets/d/1NWNuar1z0uPCB5iVS_Cs6hSo2xPkTmZf0KsgWS_Fb_4/pubchart?oid=1203594510&format=image>
  - <https://github.com/daanx/mimalloc-bench>
- **Sources the enricher read:**
  - <https://github.com/mjansson/rpmalloc>
  - <https://github.com/mjansson/rpmalloc/blob/HEAD/README.md>
  - <https://github.com/mjansson/rpmalloc/blob/HEAD/BENCHMARKS.md>
  - <https://github.com/mjansson/rpmalloc/blob/HEAD/CHANGELOG>
  - <https://github.com/mjansson/rpmalloc/blob/HEAD/rpmalloc/rpmalloc.h>
  - <https://github.com/mjansson/rpmalloc/blob/HEAD/rpmalloc/rpnew.h>
  - <https://github.com/mjansson/rpmalloc/blob/HEAD/.github/workflows/ci.yml>
  - <https://github.com/mjansson/rpmalloc/issues>
  - <https://github.com/mjansson/rpmalloc-benchmark>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/mjansson/rpmalloc`) · [data/wave1/enrich/raw/github_com_mjansson_rpmalloc.json](../../../data/wave1/enrich/raw/github_com_mjansson_rpmalloc.json) (enrichment confidence 0.5)

</details>
