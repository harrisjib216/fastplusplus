# halloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-2.0 or OpenIB BSD (dual, per LICENSE.txt)` · 🔴 abandoned

> Kepler-era CUDA device-side slab allocator (hamalloc/hafree) for small blocks, built to beat in-kernel CUDA malloc on throughput.

| | |
|---|---|
| **Beats** | CUDA device-side malloc (in-kernel allocator) |
| **Claimed result** | More than 1.5 billion mallocs/s (more than 1 billion malloc/free pairs/s) on K20X with 16-byte allocations |
| **Workload** | GPU dynamic allocation: 16-byte allocations by tens of thousands of threads with more than 100 MiB allocated on K20X. |
| **Metric** | throughput |
| **Hardware** | Nvidia K20X and K40 (compute capability 3.5) |
| **Compiler and flags** | CUDA 5.0+, tested with CUDA 6.5 |
| **Adoption** | 112 stars |
| **Last commit** | 2015-01-28 |
| **Links** | [repository](https://github.com/canonizer/halloc) · [benchmark](https://github.com/canonizer/halloc) |

## Verdict

First-party only: the README claims more than 1.5 billion mallocs/s and more than 1 billion malloc/free pairs/s for 16-byte allocations by tens of thousands of threads with more than 100 MiB allocated on a K20X, and calls this 'much higher' than other GPU allocators without giving CUDA-malloc or competitor numbers. Perf drivers (throughput, phase-throughput and others) are in tst/perf. Independent comparisons exist in the Gelado-Garland 2019 and Winter et al. 2021 papers, but those were blocked here; snippets only.

## Use it when

- Kernels that make many small (16-256 B) device-side allocations from tens of thousands of threads, such as dynamic graphs, per-thread lists or particle buffers, on Kepler/Pascal-class GPUs.
- Replacing in-kernel CUDA malloc when allocation throughput is the bottleneck and the heap stays well below its reserved capacity.
- Research baselines: it is one of the standard allocators in GPU allocator surveys (Winter et al. PPoPP 2021, memmansurvey).

## Skip it when

- Volta and newer GPUs with stock code: it uses the pre-CUDA-9 warp intrinsics (__ballot, __any, __shfl, PTX without .sync) and warp-synchronous loops. Issue #3 reports hangs on a TITAN V (CUDA 10.2) for sizes above 256 B at 10K threads and above 32 B at 100K threads, and the memmansurvey port notes the masks 'are quite hard to translate to modern CUDA' and it only works in its sync build.
- Modern CUDA toolkits without makefile edits: it builds for sm_20/sm_30/sm_35 only (sm_20 was dropped in CUDA 9 and sm_30 in CUDA 11), and issue #1 reports the build failing on an empty bin/ directory.
- Heaps that run near full: search snippets of later papers say halloc fails to allocate beyond about 50% utilization (not verified here, papers blocked).
- Allocations above 3 KiB: they go to CUDA's own allocator and get no speedup.
- Workloads that need to resize the heap or release memory: there is no way to grow after ha_init, and ha_shutdown is a no-op.

## How it is fast

Memory is split into 4 MiB slabs (superblocks), each serving one size class. Size classes are 2x or 3x a power-of-two unit, from 16 to 3072 bytes. Free chunks are tracked in per-slab bit arrays. A thread picks a starting chunk by hashing a warp-aggregated per-size counter, claims it with one atomicOr, and on collision re-probes with a size-specific hash step, so threads spread over the slab instead of contending on a list head. Slabs move between free, sparse, roomy and busy sets by occupancy thresholds (0.012, 0.6, 0.835). The leader lane of a warp swaps in a new head slab for every lane of the same size, and hafree is a single atomicAnd on the bit array plus a counter decrement.

## Compared with alternatives

It is the only GPU device-side general allocator among the catalogued siblings. LLFree targets the Linux kernel page allocator and the others are CPU mallocs, so pick halloc only for in-kernel CUDA allocation on pre-Volta hardware (or after porting to \*_sync intrinsics).

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | CUDA toolkit (device runtime malloc for large blocks); tests use thrust |
| **Minimum toolchain** | CUDA 5.0+ (tested 6.5), nvcc with -rdc=true; README requires compute capability 2.0+ |
| **Platforms** | NVIDIA GPUs; tested on CC 3.5 (K20X, K40); user report of tests passing on GTX 1070 (sm_61, CUDA 10.1) after makefile edits; hangs reported on Volta (sm_70) |
| **Thread safety** | hamalloc/hafree are thread-safe across threads and concurrent kernels per README; relies on pre-Volta lockstep warp execution |
| **Drop-in for the baseline** | partial — same semantics as device malloc/free but different names (hamalloc/hafree), needs ha_init first, and pointers cannot be freed with free/cudaFree; the malloc/free and operator new overrides in halloc.h are disabled as unstable |

## Gotchas

- ha_init calls cudaDeviceSetCacheConfig(cudaFuncCachePreferL1) for the whole device and sets cudaLimitMallocHeapSize to the 25% remainder, which silently changes the behaviour of the rest of your program.
- Licence correction: LICENSE.txt offers a choice of GPL-2.0 or the OpenIB.org BSD licence (Forschungszentrum Juelich, 2015), so the code can be used under BSD terms, not only GPL-2.0.
- Host-side init bug in halloc.cu: `memset(sbs, 0xff, MAX_NSBS * sizeof(uint))` targets sbs instead of the just-malloc'd sb_counters, so counters for unreserved slab slots are left uninitialized. It looks harmless for slabs actually reserved, and it does not touch the measured fast path.
- Size classes are 2u/3u steps, so internal waste is up to about a third (for example 49 B rounds to 64 B); the library was tuned with -Xptxas -maxrregcount=64 and -dlcm=cg, and the register count matters for occupancy of the calling kernel.

## Known shortcomings

- Pre-Volta warp intrinsics; issue 3 reports hangs on a TITAN V; the makefile targets sm_20/30/35 only. Minor init bug: memset(sbs, 0xff, ...) should target sb_counters (not on the timed path). The independent numbers are snippet only (research.nvidia.com blocked); memmansurvey lists Halloc as working only in its sync build.

## Caveats and trade-offs

README gives an absolute throughput number only; no CUDA device malloc or other allocator numbers on the page. Independent papers (DynaSOAr, Springer and Masuhara; NVIDIA's Gelado and Garland 2019 throughput-oriented allocator paper; Vinkler and Havran CGF 2015) benchmark Halloc against the CUDA allocator, and search snippets say Halloc is fastest on raw small-object allocation but fails to allocate beyond about 50% utilization; those papers were blocked here (snippet only). Allocations above 3 KiB fall through to the CUDA allocator. Kepler-era, not compiled for sm_50+; abandoned since 2015; GPL-2.0.

Slab allocator using bit arrays and hashing for GPUs; Kepler only, Maxwell unsupported; no resize after init; allocations above 3 KiB fall back to CUDA allocator.

## Maintenance

Abandoned since 2015-01-28 and dual GPL-2.0/BSD-licensed, so copyable; usable on Kepler/Pascal, needs a warp-intrinsic port for Volta+ and a makefile update for current CUDA.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README states the absolute first-party figure (more than 1.5 billion mallocs/s, more than 1 billion malloc/free pairs/s on K20X, 16-byte allocations) and only asserts it is 'much higher than other state-of-the-art GPU allocators'; no baseline numbers, flags or harness output on the page, though perf tests exist in tst/perf.
- **Verifier notes:** Kept at C. Candidate for a B retier if the DynaSOAr or Vinkler CGF 2015 paper can be opened (both blocked: arxiv.org, dcgi.fel.cvut.cz). Metadata matches: 112 stars, GPL-2.0 (COPYING), last commit 2015-01-28.
- **Fields the verifier corrected:** `caveats`, `license`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/canonizer/halloc>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/README>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/COPYING>
  - <https://github.com/canonizer/halloc/commits>
- **Sources the enricher read:**
  - <https://github.com/canonizer/halloc>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/README>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/COPYING>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/makefile>
  - <https://github.com/canonizer/halloc/tree/master/src>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/src/halloc.cu>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/src/halloc.h>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/src/slab.cuh>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/src/slab.h>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/src/size-info.h>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/src/globals.cuh>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/src/grid.cuh>
  - <https://raw.githubusercontent.com/canonizer/halloc/HEAD/src/sbset.cuh>
  - <https://github.com/canonizer/halloc/tree/master/tst/perf>
  - <https://github.com/canonizer/halloc/issues?q=is%3Aissue>
  - <https://github.com/canonizer/halloc/issues/3>
  - <https://github.com/canonizer/halloc/issues/4>
  - <https://github.com/chillenzer/memmansurvey>
  - <https://raw.githubusercontent.com/chillenzer/memmansurvey/HEAD/README.md>
  - <https://raw.githubusercontent.com/chillenzer/memmansurvey/HEAD/Notes.md>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/canonizer/halloc`) · [data/wave11/enrich/raw/github_com_canonizer_halloc.json](../../../data/wave11/enrich/raw/github_com_canonizer_halloc.json) (enrichment confidence 0.75)

</details>
