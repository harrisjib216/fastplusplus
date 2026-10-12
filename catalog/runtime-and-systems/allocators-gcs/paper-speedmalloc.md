# SpeedMalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Study only · `other` · `no license` · ⚪ unknown

> Hardware proposal: a small in-order support core runs malloc/free for all cores; simulated 1.15x over mimalloc and 1.75x over jemalloc at 16 threads.

| | |
|---|---|
| **Beats** | mimalloc, jemalloc, TCMalloc |
| **Claimed result** | On 16-thread workloads: 1.75x over Jemalloc, 1.18x over TCMalloc, 1.15x over Mimalloc, 1.23x over Mallacc, 1.18x over Memento+; energy savings 1.69x/1.15x/1.12x over Jemalloc/TCMalloc/Mimalloc (search snippets). Per-thread-count Mimalloc figures (1.17x-1.25x at 1-16 threads) could not be confirmed. |
| **Workload** | Multi-threaded allocation-heavy workloads in full-system gem5 simulation (AArch64) with McPAT power/area modelling; allocator runs on a lightweight microcontroller-grade support core (\~1-2% chip area). |
| **Metric** | throughput |
| **Links** | [benchmark](https://arxiv.org/abs/2508.20253) |

## Verdict

In full-system gem5 simulation of AArch64 cores (with McPAT power/area modelling), the paper reports 16-thread speedups of 1.75x over jemalloc, 1.18x over TCMalloc, 1.15x over mimalloc, 1.23x over Mallacc and 1.18x over Memento+, with equal or lower energy; allocator versions, workloads and core configuration could not be checked because the paper was blocked and only search snippets were read.

## Use it when

- Architecture research on allocator offload, metadata cache pollution or heterogeneous helper cores
- Citing a simulated upper bound for what removing allocator synchronization could buy multi-threaded, allocation-heavy code
- Comparing against hardware allocator accelerators such as Mallacc and Memento

## Skip it when

- Any real software project: no existing CPU has the support core or the ISA extensions
- As evidence that mimalloc or jemalloc can be beaten on current hardware: every number comes from gem5 simulation
- When you need reproducible numbers: no code, gem5 configuration or modified compiler release was found
- Single-threaded programs: the claimed benefit comes from removing cross-core synchronization

## How it is fast

All allocator metadata lives in the support core's own L1 caches (for example a 16 KB L1-D), so it no longer pollutes the main cores' L1/L2 and evicts user data. Because one core serializes every metadata update, the allocator needs no atomics and no cross-core metadata synchronization. Hardware message queues with a dispatch queue, a priority scheduler and round-robin fairness absorb bursts; the invocation path is assumed to take 8 cycles.

## Compared with alternatives

Never as a library. Every sibling (v8malloc, Mesh, LLFree, fast-alloc) runs on today's CPUs; cite SpeedMalloc only when the question is hardware offload. Exgen-Malloc, from the same group, is the software single-thread counterpart.

## Integration

| | |
|---|---|
| **Form** | not applicable (hardware/ISA proposal; no software artifact released) |
| **Dependencies** | custom hardware support core, ISA extensions and compiler changes |
| **Minimum toolchain** | modified compiler (not released) |
| **Platforms** | simulated AArch64 only (gem5 full system, McPAT for power and area) |
| **Thread safety** | Serializes all allocator metadata updates on the single support core |
| **Drop-in for the baseline** | no |

## Gotchas

- The 1.75x/1.18x/1.15x figures are for 16-thread workloads, not an average over thread counts
- Energy and area figures come from McPAT models, not silicon
- One support core serves all main cores; the paper says it is not a bottleneck at the core counts simulated, but scaling beyond them is not documented here
- The 8-cycle invocation latency is an assumption of the model

## Known shortcomings

- A hardware proposal, not a software allocator: a support core plus four new ISA instructions (mallocstart, freestart, mallocend, freeend), a modified compiler, an assumed 8-cycle invocation, evaluated only in gem5 AArch64 plus McPAT. The figures are for 16 threads. No code; snippet only.

## Caveats and trade-offs

Hardware proposal evaluated only in gem5 simulation; not usable on existing CPUs and no code release found. arXiv, IEEE CAL author PDF (ut-sysml.ece.utexas.edu), themoonlight and pith.science all blocked here; numbers are snippet-only. The 1.75x/1.18x/1.15x figures are for 16-thread workloads, not an overall average.

Needs a dedicated support core in hardware.

## Maintenance

Simulation-only research proposal with no code release; reference only and not usable on existing hardware.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Paper (arXiv 2508.20253; search results also list an IEEE Computer Architecture Letters 2025 version) reports gem5 full-system simulation speedups over jemalloc, TCMalloc and mimalloc, but every copy was egress-blocked, so the numbers are confirmed only through search snippets; kept at C pending a retier with paper access (peer-reviewed venue could justify B).
- **Verifier notes:** Search results name an IEEE CAL vol. 24 no. 2 (2025) version at ut-sysml.ece.utexas.edu/publications/prints/cal2025_li.pdf; a retier with paper access could move it to B. Authors: Ruihao Li, Lizy K. John et al. (UT Austin).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Sources the enricher read:**
  - WebSearch snippets for arxiv.org/abs/2508.20253, arxiv.org/html/2508.20253v1, alphaxiv.org/abs/2508.20253, themoonlight.io literature review, pith.science/paper/2508.20253
  - https://www.alphaxiv.org/abs/2508.20253 (blocked)
  - https://ut-sysml.ece.utexas.edu/publications/prints/cal2025_li.pdf (blocked, 403)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `paper:speedmalloc`) · [data/wave11/enrich/raw/paper_speedmalloc.json](../../../data/wave11/enrich/raw/paper_speedmalloc.json) (enrichment confidence 0.35)

</details>
