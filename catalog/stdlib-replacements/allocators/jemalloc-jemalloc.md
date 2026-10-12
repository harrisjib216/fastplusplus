# jemalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> General-purpose malloc(3) with per-thread arenas and decay-based purging; beats FreeBSD's phkmalloc under concurrency.

| | |
|---|---|
| **Beats** | phkmalloc (FreeBSD libc malloc, the incumbent jemalloc replaced) |
| **Claimed result** | Single-threaded programs (mean run time, phkmalloc vs jemalloc, from the paper's tables): cca 77.73s vs 69.37s (\~1.12x, derived from page data); gs 42.48s vs 34.24s (\~1.24x, derived from page data); sh6bench 6.96s vs 4.50s (\~1.55x, derived from page data); smlng 13.89s vs 11.49s (\~1.21x, derived from page data); cfrac 11.45s vs 10.55s (\~1.09x, derived from page data). Multi-threaded malloc-test (Figure 6, log scale): jemalloc plateaus at roughly 3x10^7 allocations/sec from 4 threads upward (with a dip above 16 threads), while phkmalloc falls below 1x10^5 allocations/sec by 10 threads and was not run beyond 10 threads (on the order of 400x at 10 threads, derived from page data, approximate reading of the log-scale plot) |
| **Workload** | malloc-test microbenchmark (Lever & Boreham 2000): tight alloc/dealloc loop, 40,000,000 cycles total divided across up to 20 threads, one 512-byte object per cycle; plus five single-threaded real programs (cca, cfrac, GhostScript, sh6bench, smlng) and a MySQL super-smack query-throughput benchmark |
| **Metric** | throughput |
| **Hardware** | four-processor system (dual-dual AMD Opteron 275), FreeBSD-CURRENT/amd64, April 2006 |
| **Adoption** | 11.2k stars; default allocator for FreeBSD libc, used by Redis, historically Firefox, and many large-scale services at Meta |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/jemalloc/jemalloc) · [benchmark](http://people.freebsd.org/~jasone/jemalloc/bsdcan2006/jemalloc.pdf) |

## Verdict

Evans' 2006 BSDCan paper (first-party, not peer-reviewed, no compiler/flags given, on a 4-CPU dual-dual AMD Opteron 275 / FreeBSD-CURRENT box) shows jemalloc beating FreeBSD's phkmalloc by roughly 1.1x-1.55x mean run time across five single-threaded programs (cca, gs, sh6bench, smlng, cfrac), and by roughly two orders of magnitude or more in throughput on a 20-thread malloc-test microbenchmark, where phkmalloc collapses below 1e5 allocs/sec by 10 threads while jemalloc plateaus near 3e7.

## Use it when

- Multi-threaded servers/daemons with heavy concurrent alloc/dealloc (its own paper's use case: Redis-, MySQL-style workloads) where a single global heap lock serializes threads
- Long-running processes where fragmentation avoidance over time matters more than the fastest possible single-thread malloc/free pair
- You want built-in heap profiling/leak detection (--enable-prof, jeprof) instead of bolting on a separate tool
- Target platform is Linux, FreeBSD, macOS, illumos, or Windows (all have dedicated CI workflows in the repo) and you're willing to link or LD_PRELOAD it
- You're prepared to tune arena count / decay times / percpu_arena for your workload rather than accept the generic defaults

## Skip it when

- Single-threaded or low-concurrency programs, where multiple arenas can raise peak RSS without a throughput win (per the record's tradeoffs note)
- Short-lived CLI tools where allocator warm-up and tuning overhead isn't worth it
- You need documented, current jemalloc-vs-glibc numbers: README/TUNING.md carry no benchmarks, and the only numeric evidence in the repo's history is a 2006 phkmalloc/dlmalloc comparison
- You want a simple mental model: open issues (#2688, #2751, #2808) show users struggling to reason about dirty/muzzy decay and HPA purging behavior in production
- You're pinning a malloc_conf tuning string from before 5.4.0 — that release silently drops seven legacy tcache mallctls (lg_tcache_nslots_mul and friends), so an old config may stop tuning anything without an error

## How it is fast

Splits the heap into multiple independent arenas (selected per-CPU or per-thread) so unrelated threads rarely contend on the same lock, backed by per-thread caches (tcache) that serve small size-class allocations without touching an arena at all. Size-class segregation limits fragmentation, and unused pages are reclaimed via time-based decay (dirty_decay_ms/muzzy_decay_ms) instead of immediate unmap, trading a little steady-state memory for fewer syscalls. The 5.4.0 release (Sep 2026) adds an HPA (huge-page-aware) extent allocator and demand-adaptive tcache refill/flush, replacing the older fixed-size tcache tuning knobs.

## Compared with alternatives

Pick jemalloc over mimalloc/snmalloc/TCMalloc when you need its mature jeprof heap-profiling and fine-grained arena/decay tuning knobs, or you're already on a codebase built around it (Redis, FreeBSD libc); the sibling entries' own numbers (mimalloc &gt;2.5x faster than jemalloc on sh6bench, snmalloc \~4x glibc at 64 threads) suggest mimalloc or snmalloc are more likely to win a raw throughput shootout today.

## Integration

| | |
|---|---|
| **Form** | source-drop, built via autoconf into a static or shared lib |
| **Dependencies** | none to build from a release tarball; autoconf is required only when building from a git/dev checkout (autogen.sh) |
| **Minimum toolchain** | not documented — README/INSTALL.md give no minimum C standard or compiler version, only that autoconf is needed |
| **Platforms** | Linux, FreeBSD, macOS, illumos, Windows (per .github/workflows: linux-ci, freebsd-ci, illumos-ci, macos-ci, windows-ci); specific CPU architectures are not enumerated in the README |
| **Thread safety** | not stated as a single explicit line, but the whole design (arenas, tcache, background threads) exists to serve concurrent multi-threaded allocation safely |
| **Drop-in for the baseline** | partial — explain: default symbol prefix is empty on Linux/FreeBSD (can replace malloc/free/calloc/realloc directly), but on macOS it overlays the malloc zone without replacing the symbols, and --with-jemalloc-prefix/--with-mangling exist specifically to avoid symbol collisions when it isn't used as a full drop-in |

## Gotchas

- Decay-based purging is a frequent confusion point: open issues report dirty_decay_ms 'not taking effect' (#2688) and ask for clearer docs on decay/purging (#2751), so memory isn't released back to the OS as immediately or predictably as a naive malloc
- Retained/metadata memory can accumulate and has no obvious release path (#2675, 'How to release retained and metadata')
- 5.4.0 removed seven legacy tcache tuning mallctls (lg_tcache_nslots_mul, tcache_nslots_small_min/max, etc.); malloc_conf strings referencing them are now silently ignored rather than erroring
- Under vm.overcommit_memory=2, vm.max_map_count can grow steadily from jemalloc's extent/arena mmap behavior (#1328), which matters for containers with strict map-count limits

## Caveats and trade-offs

Evidence is jemalloc's own founding paper (Evans, 'A Scalable Concurrent malloc(3) Implementation for FreeBSD', BSDCan 2006), which compares against phkmalloc (FreeBSD's libc malloc at the time) and dlmalloc 2.8.3, not glibc. BSDCan is a practitioner conference, not a peer-reviewed venue, and benchmarks are 'available upon request' with no compiler/flags, so tier C. Numbers are \~20 years old on a dual-dual Opteron 275. dlmalloc beat jemalloc on cfrac, gs and sh6bench. On MySQL super-smack the paper says phkmalloc's median throughput is 'typically about the same as for jemalloc'; jemalloc's gain there is in worst-case variability. No modern jemalloc-vs-glibc numbers were found in the repo (README, TUNING.md have none).

multiple arenas reduce contention but can raise peak memory in low-concurrency cases; larger tuning surface (narenas, dirty/muzzy decay_ms, percpu_arena); jemalloc's own README/TUNING.md carries no numeric benchmarks

## Maintenance

Actively maintained: 5.4.0 shipped Sep 17 2026 with 160+ commits and the dev branch was pushed the same day as this review; BSD-2-Clause licensed and small enough to vendor, but the repo itself carries no modern jemalloc-vs-glibc benchmark numbers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification B, tier now C.
- **Tier reason:** The single-threaded run-time tables (cca, gs, sh6bench, smlng vs phkmalloc) are verbatim in the paper, but it is the jemalloc author's own write-up for BSDCan, a practitioner conference that is not a refereed paper venue. Benchmarks are only 'available upon request' and no compiler or flags are given, so these are first-party numbers with partial methodology (C), not B.
- **Verifier notes:** Tier lowered from B to C because a BSDCan paper by the project author is first-party, not peer-reviewed. The Figure 6 reading was corrected: jemalloc plateaus near 3e7, not 2e7, and phkmalloc is below 1e5 at 10 threads, so the gap is about 400x rather than 100x (still approximate). The GitHub license API returns NOASSERTION, but COPYING is 2-clause BSD text with an 'Unless otherwise specified' preamble, so BSD-2-Clause and copyable stand. FreeBSD libc's malloc directory still holds only jemalloc.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** Loaded into the same binary with LD_PRELOAD (no rebuild), jemalloc cut new/delete churn (200k allocate/free pairs in unrelated order, 4096 live 48-byte objects) from 11.738 to 4.33 ns vs glibc malloc (2.71x). It also closed a fragmented 200k-node list walk from 13.028 to 3.965 ns per node, so most of the apparent arena locality win was a glibc fragmentation loss. (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party); jemalloc did not replace an arena: when 200k nodes were allocated and then all freed, new/delete under jemalloc only improved from 18.682 to 12.63 ns per node, against 3.15 ns for a bump arena (4.0x, derived). std::pmr::unsynchronized_pool_resource stayed at 42.77 ns on churn under jemalloc. (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <http://people.freebsd.org/~jasone/jemalloc/bsdcan2006/jemalloc.pdf>
  - <https://github.com/jemalloc/jemalloc>
  - <https://github.com/jemalloc/jemalloc/blob/dev/COPYING>
  - <https://github.com/freebsd/freebsd-src/tree/main/lib/libc/stdlib/malloc>
- **Sources the enricher read:**
  - <https://github.com/jemalloc/jemalloc>
  - <https://github.com/jemalloc/jemalloc/blob/dev/README>
  - <https://github.com/jemalloc/jemalloc/blob/dev/INSTALL.md>
  - <https://github.com/jemalloc/jemalloc/blob/dev/ChangeLog>
  - <https://github.com/jemalloc/jemalloc/blob/dev/TUNING.md>
  - <https://github.com/jemalloc/jemalloc/tree/dev>
  - <https://github.com/jemalloc/jemalloc/issues?q=performance>
  - <https://github.com/jemalloc/jemalloc/issues?q=CVE+OR+vulnerability+OR+security>
  - <http://people.freebsd.org/~jasone/jemalloc/bsdcan2006/jemalloc.pdf>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/jemalloc/jemalloc`) · [data/wave0-seed/enrich/raw/github_com_jemalloc_jemalloc.json](../../../data/wave0-seed/enrich/raw/github_com_jemalloc_jemalloc.json) (enrichment confidence 0.55)

</details>
