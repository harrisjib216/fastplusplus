# LLFree

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Lock- and log-free page-frame allocator in C; up to 88% (4 KiB) and 98% (2 MiB) lower concurrent allocation time than Linux's buddy allocator.

| | |
|---|---|
| **Beats** | Linux kernel buddy page-frame allocator |
| **Claimed result** | Reduces allocation time for concurrent 4 KiB allocations by up to 88% and for 2 MiB allocations by up to 98% versus the Linux frame (buddy) allocator (USENIX ATC 2023 abstract, per search snippet). The 64% fewer compaction page movements figure was not seen. |
| **Workload** | Concurrent 4 KiB and 2 MiB page-frame allocation in a lock- and log-free allocator, plus compaction page movements. |
| **Metric** | latency |
| **Adoption** | 12 stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/luhsra/llfree-c) · [benchmark](https://www.usenix.org/conference/atc23/presentation/wrenger) |

## Verdict

Per the USENIX ATC 2023 abstract (read via search snippet; the usenix.org PDF is blocked here), the Rust LLFree inside Linux cut concurrent 4 KiB allocation time by up to 88% and 2 MiB allocation time by up to 98% versus the Linux buddy frame allocator, and needed 64% fewer compaction page movements; the paper data came from raw hardware not named on the pages read, with an artifact (Distinguished Artifact Award) validated on Linux 6.0-6.2.

## Use it when

- Kernel or hypervisor page-frame allocation on many-core machines where the buddy allocator's zone lock contention dominates (concurrent 4 KiB and 2 MiB requests)
- Systems that want many 2 MiB huge pages available and less compaction work (paper reports 64% fewer compaction page movements, abstract only)
- Persistent-memory frame allocators that must survive crashes without a log (LLFREE_INIT_RECOVER)
- Research OSes, unikernels or VM memory ballooning (HyperAlloc, EuroSys 2025, builds on it) that need a small C frame allocator

## Skip it when

- Userspace object allocation: it is not a malloc replacement and gives frame numbers, not pointers
- Orders above 4 MiB (order 10) or arbitrary-size ranges: only 4 KiB to 4 MiB allocations are handled
- You need the measured numbers to hold for this exact code: the ATC 2023 evaluation ran the Rust llfree-rs in a modified Linux 6.x, not this C reimplementation
- Small projects wanting a stable API: 12 stars, research code whose API (classing, policy callbacks) changed recently

## How it is fast

No locks and no log: the persistent lower allocator is a bitfield of 512 bits per 2 MiB region (one bit per 4 KiB frame), with a 2 MiB entry holding a free counter and a huge-page flag, all updated with atomic compare-exchange. An upper, volatile layer groups 2 MiB entries into trees (8 by default) and reserves a tree per core and per class (e.g. small vs huge, movable vs immovable), so cores rarely touch the same cache lines and 4 KiB allocations do not fragment 2 MiB regions. The lower layer is crash-consistent on nonvolatile memory and the upper layer is rebuilt on boot.

## Compared with alternatives

The siblings (mimalloc-class mallocs, TLSF, arena and pool allocators) all serve userspace objects; pick LLFree only when you are allocating physical page frames in a kernel or hypervisor, where none of them apply.

## Integration

| | |
|---|---|
| **Form** | static lib (make DEBUG=0 builds build/libllc.a) or source-drop into a kernel tree |
| **Dependencies** | none beyond C11 atomics; you provide llfree_platform.h and llfree_types.h |
| **Minimum toolchain** | Clang by default (Makefile CC := clang, -std=c11); uses GNU statement expressions and C23-style 'enum : uint8_t', so GCC/Clang only |
| **Platforms** | 64-bit platforms with C11 atomics; userspace std/ build on Linux; kernel integration via luhsra/llfree-linux |
| **Thread safety** | Designed for concurrent use from all cores without locks (atomic CAS on bitfields, per-core reservations) |
| **Drop-in for the baseline** | partial — replaces the Linux buddy allocator only through the patched llfree-linux kernel; the API differs from alloc_pages |

## Gotchas

- Release builds use -march=native, so a library built on one machine may not run on an older CPU
- Freed frames must be returned with a matching request (order and class) in llfree_put
- llfree_tree_stats is fast but may be inaccurate; llfree_stats scans the lower allocator for exact counts
- Allocations can come back in a different class than requested (demotion), reported in llfree_result_t.class

## Known shortcomings

- The paper measured the Rust llfree-rs inside Linux 6.x, not this C reimplementation; the 88%, 98% and 64% figures are search-snippet only (the USENIX PDF is blocked). The release build uses -march=native.

## Caveats and trade-offs

Page-frame allocator, a different class from malloc. This repo is the C reimplementation; the ATC 2023 paper evaluated the Rust llfree-rs version inside a modified Linux (llfree-linux). Paper PDF on usenix.org blocked, numbers from search snippet; benchmark scripts in luhsra/llfree-bench and luhsra/linux-alloc-bench need a custom kernel build.

Kernel page-frame allocator, not a userspace malloc; also available as Rust (llfree-rs) and a Linux tree.

## Maintenance

Active (585 commits, last commit 2026-09-17), MIT-licensed and small enough to vendor, but research code with a moving API and few users.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed USENIX ATC 2023 paper (cited in the repo README) reports up to 88% (4 KiB) and 98% (2 MiB) lower concurrent allocation time than the Linux frame allocator; benchmark scripts are public (luhsra/llfree-bench, luhsra/linux-alloc-bench), but the usenix.org PDF is blocked so CPU model and compiler could not be checked for A.
- **Verifier notes:** Metadata from github.com: 12 stars, MIT, last commit 2026-09-17. Paper numbers confirmed only via snippet; the 64% compaction figure is unverified.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/luhsra/llfree-c>
  - <https://github.com/luhsra/llfree-c/commits>
  - <https://raw.githubusercontent.com/luhsra/llfree-c/HEAD/README.md>
  - <https://raw.githubusercontent.com/luhsra/llfree-c/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/luhsra/llfree-bench/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/luhsra/llfree-c>
  - <https://raw.githubusercontent.com/luhsra/llfree-c/HEAD/README.md>
  - <https://raw.githubusercontent.com/luhsra/llfree-c/HEAD/include/llfree.h>
  - <https://raw.githubusercontent.com/luhsra/llfree-c/HEAD/std/llfree_platform.h>
  - <https://raw.githubusercontent.com/luhsra/llfree-c/HEAD/std/llfree_types.h>
  - <https://raw.githubusercontent.com/luhsra/llfree-c/HEAD/Makefile>
  - <https://raw.githubusercontent.com/luhsra/llfree-c/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/luhsra/llfree-rs/HEAD/README.md>
  - <https://github.com/luhsra/llfree-bench>
  - <https://github.com/luhsra/llfree-bench/tree/main/artifact-eval>
  - https://www.usenix.org/system/files/atc23-wrenger.pdf (blocked, 403)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/luhsra/llfree-c`) · [data/wave11/enrich/raw/github_com_luhsra_llfree_c.json](../../../data/wave11/enrich/raw/github_com_luhsra_llfree_c.json) (enrichment confidence 0.65)

</details>
