# jdz_allocator

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟡 stale

> rpmalloc-style span allocator for Zig; claims parity with the rpmalloc Zig port and lower memory, no shown win over malloc.

| | |
|---|---|
| **Beats** | C malloc (glibc via Zig c_allocator), Zig GeneralPurposeAllocator, rpmalloc Zig port, zimalloc |
| **Claimed result** | No numbers in text: charts only; README says global allocator matches rpmalloc 'within the margin of error' with less memory; default config 'significantly slower than rpmalloc at high contention' |
| **Workload** | mimalloc-bench suite via LD_PRELOAD, plus 75,000,000 linearly distributed 1-80000 byte allocations per thread without cross-thread frees. |
| **Metric** | throughput |
| **Hardware** | 8 core Intel i7-11800H @2.30GHz, Linux |
| **Compiler and flags** | zig -O ReleaseFast |
| **Adoption** | 54 stars |
| **Last commit** | 2024-11-09 |
| **Links** | [repository](https://github.com/joadnacer/jdz_allocator) · [benchmark](https://github.com/joadnacer/jdz_allocator) |

## Verdict

First-party charts only: mimalloc-bench via LD_PRELOAD and a Zig microbenchmark (75,000,000 allocations per thread of 1-80000 bytes, no cross-thread frees) on an 8-core i7-11800H under Linux, Zig ReleaseFast, against c_allocator (glibc malloc), Zig GPA, the rpmalloc Zig port and zimalloc. The text claims the global variant matches the rpmalloc Zig port within margin of error with less memory, and that the default variant is significantly slower than rpmalloc at high contention; chart values were not readable here.

## Use it when

- Zig 0.13 programs that want an rpmalloc-like thread-caching allocator behind std.mem.Allocator rather than GeneralPurposeAllocator.
- Zig code that must pass an allocator explicitly and cannot use threadlocal state: JdzAllocator works without deinitThread calls.
- Experiments comparing span allocators in mimalloc-bench through LD_PRELOAD, where its README charts can serve as a starting point.
- Workloads with up to about 8 allocating threads (the default shared_arena_batch_size), where arena stealing and false sharing do not occur.

## Skip it when

- Production C or C++ services: the author says it is not battle-tested and may error under some loads; a TSan data-race report (issue #9) and Windows free() segfaults (issue #6) are open and unanswered.
- When you need a measured speedup over glibc malloc, mimalloc or jemalloc: the README text claims only parity with the rpmalloc Zig port, and mimalloc and jemalloc were never compared.
- High-contention use of the default JdzAllocator: the README says it is significantly slower than rpmalloc there, and with more threads than shared_arena_batch_size arenas are stolen and false sharing follows.
- Systems with pages larger than 64 KiB (some aarch64 and ppc64 kernels): not supported.
- Memory-tight workloads resembling xmalloc-testN, where the global variant shows high RSS that the author was still investigating.

## How it is fast

It copies rpmalloc's design: 64 KiB spans, each holding one size class, with the span header found by masking the pointer, and size classes of 16 B granularity up to 2048 B and 256 B granularity up to 32512 B. Each arena allocates from one thread at a time while other threads may free into it; arenas keep a lock-protected span stack, a bounded MPSC span cache and large-span caches, and the global variant adds bounded MPMC global caches. Spans are mapped in batches of 64 (4 MiB plus 64 KiB padding) to amortize mmap calls.

## Compared with alternatives

Pick it only for Zig projects that want an rpmalloc-like allocator in pure Zig; for C or C++ processes, Spaces, Kaname-Shiki or FastAlloc publish measured wins against glibc, jemalloc or mimalloc, and mem++ at least gives chart values versus jemalloc and mimalloc.

## Integration

| | |
|---|---|
| **Form** | module (Zig package via build.zig.zon) plus static lib and LD_PRELOAD shared libs |
| **Dependencies** | none (libc only for the shared libraries) |
| **Minimum toolchain** | Zig 0.13.0 (master pinned to it; older Zig versions needed older commits) |
| **Platforms** | Linux tested; Windows has an open segfault report; page size must be 64 KiB or less |
| **Thread safety** | thread_safe config flag, on by default unless single-threaded; global variant needs deinitThread per thread; open TSan data-race report (issue #9) |
| **Drop-in for the baseline** | partial — LD_PRELOAD libraries replace malloc for C programs, but libjdzglobalwrap is needed for per-thread cleanup and the core API is Zig's Allocator interface |

## Gotchas

- libso calloc computes size \* count with no overflow check, so a huge product can wrap in ReleaseFast builds and return a buffer smaller than the caller asked for.
- libjdzglobalwrap calls pthread_setspecific in the thread calling pthread_create, not in the new thread, so the destructor that calls jdz_deinit_thread fires only for threads that themselves spawn threads; leaf worker threads may never return their spans.
- malloc(0) returns NULL and aligned_alloc or memalign with an invalid alignment panics instead of returning EINVAL.
- src/bench.zig only times jdz, jdz-global, c_allocator and Zig GPA; the rpmalloc-zig and zimalloc numbers in the charts come from a separate setup not in the repo, and every thread uses the same PRNG seed (1337).

## Known shortcomings

- Zig, not C++. libso calloc multiplies size by count with no overflow check; libjdzglobalwrap calls pthread_setspecific in the parent thread, so leaf threads never deinit. Open issues: 9 (TSan data races) and 6 (Windows free segfault), no maintainer replies. src/bench.zig times only jdz, jdz-global, c and GPA; the rpmalloc-zig and zimalloc numbers come from a setup that is not in the repo. The pastebin and imgur charts were unreadable.

## Caveats and trade-offs

Charts are imgur images and raw results are on pastebin (blocked here), so no speedup over malloc was read; the text claims only parity with the rpmalloc Zig port (not C rpmalloc) for the global allocator and says the default config is significantly slower than rpmalloc at high contention. Author calls the Zig benchmark unrealistic and the allocator not battle-tested; high RSS on xmalloc-testN. No comparison to mimalloc or jemalloc. Weak qualifier.

Zig-only API plus LD_PRELOAD shared libraries; global variant needs deinitThread calls; page sizes above 64 KiB unsupported; high RSS on xmalloc-test.

## Maintenance

Stale since November 2024 (last commit 2024-11-09) with two open bug reports and no maintainer replies; MIT-licensed and small, so it can be vendored by Zig users, but treat it as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README has first-party mimalloc-bench and src/bench.zig charts (normalized to jdzw, capped at 2.0) against c_allocator (C malloc), Zig GPA, rpmalloc-zig and zimalloc on an i7-11800H with ReleaseFast; the numbers are only in chart images and a pastebin raw dump, with no text speedup over malloc, so C.
- **Verifier notes:** Could not view chart images or pastebin (EGRESS_BLOCKED); an enricher that can read https://pastebin.com/QDA2UW67 should pull the calc vs jdzw times. Last commit 2024-11-09, so stale. MIT, 54 stars.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/joadnacer/jdz_allocator>
  - <https://raw.githubusercontent.com/joadnacer/jdz_allocator/main/README.md>
  - <https://raw.githubusercontent.com/joadnacer/jdz_allocator/main/LICENSE>
  - <https://github.com/joadnacer/jdz_allocator/commits>
- **Sources the enricher read:**
  - <https://github.com/joadnacer/jdz_allocator>
  - <https://raw.githubusercontent.com/joadnacer/jdz_allocator/HEAD/README.md>
  - <https://raw.githubusercontent.com/joadnacer/jdz_allocator/HEAD/build.zig>
  - <https://raw.githubusercontent.com/joadnacer/jdz_allocator/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/joadnacer/jdz_allocator/HEAD/src/jdz_allocator.zig>
  - <https://raw.githubusercontent.com/joadnacer/jdz_allocator/HEAD/src/bench.zig>
  - <https://raw.githubusercontent.com/joadnacer/jdz_allocator/HEAD/libso/libjdzglobal.zig>
  - <https://raw.githubusercontent.com/joadnacer/jdz_allocator/HEAD/libso/libjdzglobalwrap.c>
  - <https://raw.githubusercontent.com/joadnacer/jdz_allocator/HEAD/libso/libjdzshared.zig>
  - <https://github.com/joadnacer/jdz_allocator/issues?q=is%3Aissue>
  - <https://github.com/joadnacer/jdz_allocator/issues/9>
  - <https://github.com/joadnacer/jdz_allocator/issues/6>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/joadnacer/jdz_allocator`) · [data/wave11/enrich/raw/github_com_joadnacer_jdz_allocator.json](../../../data/wave11/enrich/raw/github_com_joadnacer_jdz_allocator.json) (enrichment confidence 0.6)

</details>
