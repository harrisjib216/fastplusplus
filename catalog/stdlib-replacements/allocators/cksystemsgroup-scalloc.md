# scalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🟡 stale

> Multicore-scalable, low-fragmentation malloc replacement beating ptmalloc2; drop-in via LD_PRELOAD, rewritten since its OOPSLA'15 paper.

| | |
|---|---|
| **Beats** | ptmalloc2 (glibc's default malloc, part of GNU libc; extends Doug Lea's dlmalloc) |
| **Claimed result** | About 1.28x SPEC ratio vs ptmalloc2 on single-threaded 483.xalancbmk (read from the Figure 5 bar chart, derived from page data). Here scalloc is mid-pack, below TCMalloc (\~1.345), llalloc (\~1.33), TBB (\~1.29) and SuperMalloc (\~1.285), and the paper says the differences among the best allocators are small. For multithreaded workloads the paper claims scalloc 'increases performance on average while consuming less memory than the previously fastest allocator (TBB)' and outperforms/outscales all allocators for varying object sizes that fit virtual spans. |
| **Workload** | SPEC CPU2006 483.xalancbmk single-threaded allocation-intensive workload, plus threadtest/shbench/larson multithreaded microbenchmarks and an ACDC-generated producer-consumer workload |
| **Metric** | throughput |
| **Hardware** | UMA machine, 4x 10-core 2GHz Intel Xeon E7-4850 (2 hardware threads/core), 32KB L1D, 32KB L1I, 256KB L2/core, 24MB L3/processor, 128GB RAM, Linux kernel 3.8.0 |
| **Adoption** | 163 stars |
| **Last commit** | 2025-06-23 |
| **Links** | [repository](https://github.com/cksystemsgroup/scalloc) · [benchmark](https://arxiv.org/pdf/1503.09006) |

## Verdict

The OOPSLA'15 paper (arXiv v2, Aug 2015) reports scalloc at roughly a 1.28x SPEC ratio vs ptmalloc2 on single-threaded SPEC CPU2006 483.xalancbmk (read off a Figure 5 bar, no printed number, no compiler/flags stated), measured on 4x 10-core Xeon E7-4850 with 128GB RAM; it separately claims scalloc beats TBB's average multithreaded throughput while using less memory across threadtest/shbench/larson/ACDC.

## Use it when

- Multithreaded, allocation-heavy C/C++ workloads on Linux or OSX x86 where you want a drop-in swap without recompiling (LD_PRELOAD/DYLD_INSERT_LIBRARIES)
- Producer-consumer or varying-object-size workloads whose object sizes fit within 2MiB virtual spans
- You can tune the environment (overcommit accounting, transparent huge pages) for correct/best behavior
- Memory footprint under concurrency matters as much as raw throughput (paper claims lower memory than TBB at comparable/better speed)
- You're willing to re-benchmark on current hardware and current allocator code rather than trust the 2015 numbers

## Skip it when

- Windows: unsupported (override.h explicitly #errors on non-Linux/non-Apple)
- Build is gyp-based and broken on modern Python (open, unanswered GitHub issue #1, 'Switch to a supported build system')
- Single-threaded throughput vs ptmalloc2 is the goal: the paper's own numbers put scalloc mid-pack (\~1.28x), behind TCMalloc/llalloc/TBB/SuperMalloc
- Address-space-constrained or containerized environments: reserves up to 32TB of virtual space per arena, which can hit mmap/overcommit limits
- Project is stale with a single unresolved open issue; README itself says the allocator was 'completely rewritten from scratch' since the benchmarked paper version, so published speedup numbers may not reflect current code

## How it is fast

Uses 'virtual spans' (2MiB-aligned regions, kVirtualSpanShift=21) to treat small and large objects uniformly instead of separate size-class machinery. Per-thread local allocation buffers (LABs) handle the fast path, while a scalable global span pool reclaims and redistributes spans across cores. Allocation/deallocation are constant-time modulo synchronization, trading memory reuse against spatial locality to avoid false sharing.

## Compared with alternatives

Pick scalloc over SuperMalloc/NUMAlloc/Hoard only when you specifically want its virtual-span design for producer-consumer or mixed-size multithreaded workloads with lower memory use than TBB; for single-threaded throughput vs ptmalloc2, SuperMalloc and TCMalloc beat scalloc in its own paper's numbers, and SuperMalloc/NUMAlloc have more recent or broader comparative benchmarks.

## Integration

| | |
|---|---|
| **Form** | shared lib (built with gyp+make; loaded via LD_PRELOAD/DYLD_INSERT_LIBRARIES) |
| **Dependencies** | gyp (build-time only, fetched via tools/make_deps.sh); no runtime dependencies documented |
| **Minimum toolchain** | not documented (no C++ standard stated); build needs Python for gyp, which is currently broken per open issue #1 |
| **Platforms** | Linux and OSX (&gt;10.6); README's design assumes 64-bit address space; no Windows (override.h errors on any other OS) |
| **Thread safety** | core design goal is safe concurrent/multicore allocation; no separate documented thread-safety contract beyond that |
| **Drop-in for the baseline** | yes |

## Gotchas

- gyp build is broken on modern Python versions; open issue #1 (filed 2025-06-02) is unresolved
- Needs vm.overcommit_memory=1 and transparent huge pages disabled on Linux for correct/best operation
- Reserves up to 32TB of virtual address space per arena; relies on on-demand paging/madvise to keep physical memory low
- OSX preload needs DYLD_FORCE_FLAT_NAMESPACE=1 in addition to DYLD_INSERT_LIBRARIES

## Caveats and trade-offs

The OOPSLA'15 paper (arXiv v2, Aug 2015) is 10+ years old. The current README says the allocator was 'completely rewritten from scratch' since the paper and says to benchmark the current version; the separate cksystemsgroup/scalloc-artifact repo was last updated 2018-03-20. Today's numbers may therefore differ from the paper's. The paper states no compiler or optimization flags. The xalancbmk values exist only as bars in Figure 5, not as printed numbers.

Reserves up to 32TB of virtual address space per arena (relies on on-demand paging / madvise to keep physical memory low); distributed via LD_PRELOAD on Linux / DYLD_INSERT_LIBRARIES on OSX; needs overcommit accounting and transparent-huge-pages tuned for best results.

## Maintenance

maintenance_status is stale and the BSD-2-Clause license makes it easy to vendor, but the gyp build is broken on current Python (open issue #1, unresolved) and the README itself says to re-benchmark since a full rewrite post-paper.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now B.
- **Tier reason:** This is a peer-reviewed OOPSLA'15 paper (Artifact Evaluated) comparing against ptmalloc2 on SPEC 483.xalancbmk and threadtest/shbench/larson/ACDC, with hardware (4x Xeon E7-4850) stated. Neither the paper nor the artifact README (only 'tested on Ubuntu 14.04') gives the compiler or flags, so it is B, not A.
- **Verifier notes:** The record's '\~1.33x, on par with TCMalloc \~1.34x' misread Figure 5: the \~1.33 bar is llalloc, and scalloc's bar is about 1.28. claimed_speedup was corrected and verdict downgraded (tier stays B). The 'artifact not updated since 2019' caveat was corrected to 2018-03-20.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/1503.09006>
  - <https://github.com/cksystemsgroup/scalloc>
  - <https://github.com/cksystemsgroup/scalloc/blob/master/README.md>
  - <https://github.com/cksystemsgroup/scalloc-artifact>
  - <https://github.com/cksystemsgroup/scalloc-artifact/blob/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/cksystemsgroup/scalloc>
  - <https://github.com/cksystemsgroup/scalloc/blob/master/README.md>
  - <https://github.com/cksystemsgroup/scalloc/blob/master/LICENSE>
  - <https://github.com/cksystemsgroup/scalloc/blob/master/src/glue.cc>
  - <https://github.com/cksystemsgroup/scalloc/blob/master/src/globals.h>
  - <https://github.com/cksystemsgroup/scalloc/blob/master/src/platform/globals.h>
  - <https://github.com/cksystemsgroup/scalloc/blob/master/src/platform/override.h>
  - <https://github.com/cksystemsgroup/scalloc/issues/1>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/cksystemsgroup/scalloc`) · [data/wave1/enrich/raw/github_com_cksystemsgroup_scalloc.json](../../../data/wave1/enrich/raw/github_com_cksystemsgroup_scalloc.json) (enrichment confidence 0.7)

</details>
