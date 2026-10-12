# TCMalloc (google/tcmalloc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Google's per-CPU-cache C/C++ allocator, positioned as a faster-at-scale alternative to glibc malloc, though unquantified in the repo.

| | |
|---|---|
| **Beats** | glibc malloc |
| **Workload** | No specific benchmark named; docs/overview.md frames TCMalloc as "an alternative to the one provided by the C standard library (on Linux usually through glibc)" and states it is "designed to be more efficient at scale than other implementations", without a stated test. |
| **Metric** | other |
| **Adoption** | 5.4k stars; used throughout Google's production C++ services |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/google/tcmalloc) · [benchmark](https://github.com/google/tcmalloc/blob/master/docs/overview.md) |

## Verdict

No numeric benchmark of google/tcmalloc vs glibc malloc (or std::allocator/operator new) appears in the repo; overview.md only claims it is 'designed to be more efficient at scale.' The only peer-reviewed numbers found (Hunter, Kennelly et al., OSDI 2021) measure TCMalloc's hugepage-aware TEMERAIRE backend against TCMalloc's own prior legacy pageheap, not glibc: +7.7% RPS / -2.4% RAM (abstract), +5.2% average throughput (Table 1) across 8 Google WSC apps, pageheap overhead 14.3%-&gt;10.6% (Fig. 15), fleet IPC +1.2%, and Redis 6.0.9 +0.75%/+0.44% RPS (LLVM -O3, Skylake Xeon, 2000 trials).

## Use it when

- Highly parallel, multi-threaded C++ server workloads on Linux x86-64/AArch64 with RSEQ kernel support (&gt;=4.18)
- Already building with Bazel and Abseil, or willing to add both as dependencies
- Need built-in heap telemetry/sampling (MallocExtension) for fleet-scale memory tracking
- Large-fleet deployments where small reductions in pageheap overhead/RAM matter at scale (per the OSDI 2021 TEMERAIRE data)
- OK rebuilding from source at or near HEAD rather than linking a stable prebuilt library

## Skip it when

- Non-Linux targets: no documented Windows/macOS support; only Linux is supported, PPC is 'best effort'
- Kernels &lt;4.18 or RSEQ disabled: falls back to legacy per-thread caching, losing the main fast-path win
- Code that needs std::bad_alloc/exception-based OOM handling: TCMalloc crashes directly on allocation failure instead of throwing
- Projects that cannot add Abseil (and Bazel, or the experimental CMake path) as build dependencies
- Anything needing dynamic load/unload of the allocator or ABI stability across TCMalloc versions: neither is supported or promised

## How it is fast

Fast-path allocation/free happens in a per-CPU cache (default) or per-thread cache (fallback), both lock-free for the common case. Per-CPU mode uses Linux restartable sequences (RSEQ, kernel &gt;=4.18) so a core-local push/pop either completes atomically or is transparently restarted on preemption/migration, avoiding atomic instructions. Cache misses refill from a CentralFreeList/TransferCache middle-end sized by allocatable size-classes, backed by a hugepage-aware page-heap (TEMERAIRE) that cuts TLB pressure and fragmentation versus the legacy pageheap.

## Compared with alternatives

Pick over gperftools' tcmalloc when you want the actively developed successor with per-CPU RSEQ caching and the hugepage-aware TEMERAIRE backend, instead of gperftools' legacy per-thread-only pageheap. Pick mimalloc/jemalloc/snmalloc instead when you want a documented head-to-head number against your baseline in-repo — none of google/tcmalloc's docs quantify it against glibc, std::allocator, or those allocators.

## Integration

| | |
|---|---|
| **Form** | source-drop / static lib (built from source with Bazel; no prebuilt binary, no header-only mode) |
| **Dependencies** | Abseil (hard dependency, pinned in MODULE.bazel); also pulls in protobuf, re2, bazel_skylib as Bazel deps |
| **Minimum toolchain** | C++17 (C11 for C code); gcc 12.1+ or clang 11.0+; Bazel 4.0+ (CMake support experimental) |
| **Platforms** | Linux x86 and AArch64, little-endian 64-bit, libstdc++/libc++ (PPC best-effort); no Windows/macOS documented |
| **Thread safety** | Thread-safe allocator; default per-CPU caching (needs Linux RSEQ, kernel &gt;=4.18) or per-thread fallback, both avoiding locks on the fast path (docs/overview.md, docs/rseq.md) |
| **Drop-in for the baseline** | partial — replaces malloc/operator new via build-system linkage (e.g. Bazel's `malloc` attribute), same C11/C++17 allocation API surface, but does not throw on OOM (crashes instead) and offers no ABI stability |

## Gotchas

- No ABI stability: docs/compatibility.md says build from source (ideally HEAD), don't depend on a compiled representation, don't open namespace tcmalloc, don't take the address of its API functions
- Allocation failure crashes the process instead of throwing std::bad_alloc, which can surprise code relying on exception-based OOM handling
- No dynamic loading/unloading support
- The RSEQ fast path is fragile in practice: closed issue #292 documents crashes on Linux &gt;=6.19 from RSEQ ABI interaction with glibc's own rseq registration

## Caveats and trade-offs

No public numeric benchmark of google/tcmalloc vs glibc malloc, std::allocator, or operator new/delete was found in the repo's docs, so this is tier D on the qualitative overview.md claim. Peer-reviewed numeric evidence exists only against TCMalloc's OWN legacy pageheap: Hunter, Kennelly et al., 'Beyond malloc efficiency to fleet efficiency: a hugepage-aware memory allocator' (OSDI 2021). TEMERAIRE improved RPS by 7.7% and cut RAM by 2.4% across 8 applications (abstract). Table 1 averages +5.2% throughput across WSC apps. Fleet IPC rose 1.2%, and pageheap overhead fell from 14.3% to 10.6% (Fig. 15). Redis 6.0.9 gained +0.75% with periodic release off and +0.44% with it on (Intel Skylake Xeon, LLVM cd442157cf -O3, 2000 trials of redis-benchmark with 1,000,000 requests each). That is TCMalloc vs TCMalloc, not vs a listed baseline. google/tcmalloc is the documented successor ('abseil tcmalloc') to gperftools' tcmalloc, whose quoted glibc comparison is recorded under the 'gperftools TCMalloc' entry.

hard dependency on Abseil; default per-CPU caching fast path requires Linux RSEQ support (kernel &gt;=4.18), else falls back to slower per-thread caching; heavier build/dependency footprint than gperftools' tcmalloc

## Maintenance

Actively maintained (commits current as of the record date) and Apache-2.0/copyable, but not a drop-in swap: expect to vendor the source, add Abseil, and build with Bazel rather than link a stable prebuilt library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification D, tier now D.
- **Tier reason:** docs/overview.md only says TCMalloc is an alternative to the glibc/C++ standard library allocator and is 'designed to be more efficient at scale than other implementations'. There are no numbers, and none vs glibc in design.md, temeraire.md, tuning.md, rseq.md, gperftools.md or lifetime-based-allocator.md. Tier D, notable (5.4k stars), so not rejected.
- **Verifier notes:** Tier D was correct. I fixed the caveat's OSDI numbers: the '+3.2% average CPU throughput' figure does not appear in the paper. The paper reports +7.7% RPS / -2.4% RAM (abstract), a +5.2% Table 1 average, and +1.2% fleet IPC; the 14.3%-&gt;10.6% and Redis +0.75%/+0.44% figures are correct. The input record had no claimed_speedup key; I set it to null.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/google/tcmalloc/blob/master/docs/overview.md>
  - <https://github.com/google/tcmalloc>
  - <https://github.com/google/tcmalloc/blob/master/docs/design.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/temeraire.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/tuning.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/rseq.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/gperftools.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/lifetime-based-allocator.md>
  - <https://www.usenix.org/system/files/osdi21-hunter.pdf>
- **Sources the enricher read:**
  - <https://github.com/google/tcmalloc>
  - <https://github.com/google/tcmalloc/blob/master/docs/platforms.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/quickstart.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/compatibility.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/overview.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/rseq.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/gperftools.md>
  - <https://github.com/google/tcmalloc/blob/master/docs/design.md>
  - <https://github.com/google/tcmalloc/blob/master/MODULE.bazel>
  - https://github.com/google/tcmalloc/issues (search: bug, label:bug)
  - <https://github.com/google/tcmalloc/issues/292>
  - <https://github.com/google/tcmalloc/issues/253>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/google/tcmalloc`) · [data/wave0-seed/enrich/raw/github_com_google_tcmalloc.json](../../../data/wave0-seed/enrich/raw/github_com_google_tcmalloc.json) (enrichment confidence 0.3)

</details>
