# Exgen-Malloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C` · `no license` · ⚪ unknown

> Single-threaded malloc built by stripping mimalloc's thread machinery; paper reports 1.03-1.05x over mimalloc and 1.17-1.19x over dlmalloc on SPEC CPU2017.

| | |
|---|---|
| **Beats** | dlmalloc, mimalloc |
| **Claimed result** | Geometric mean 1.19x over dlmalloc and 1.03x over mimalloc on SPEC CPU2017; 6.2%, 0.1% and 25.2% memory savings over mimalloc on SPEC CPU2017, redis-benchmark and mimalloc-bench (search snippet). The 1.93x-over-dlmalloc mimalloc-bench figure was not seen. |
| **Workload** | Single-threaded allocator tested on mimalloc-bench, SPEC CPU2017 and redis-benchmark. |
| **Metric** | throughput |
| **Links** | [benchmark](https://ieeexplore.ieee.org/document/11075519/) |

## Verdict

IEEE Computer Architecture Letters 2025 (arXiv 2510.10219) reports geometric-mean speedups on SPEC CPU2017 of 1.17-1.19x over dlmalloc and 1.03-1.05x over mimalloc, 1.10x/1.01x on redis-benchmark and 1.93x/1.02x on mimalloc-bench, with 6.2%/0.1%/25.2% memory savings over mimalloc, measured on two Intel Xeon machines; compiler, flags and exact CPU models are not known because every copy of the paper was blocked here and the numbers come from search snippets.

## Use it when

- Single-threaded, allocation-heavy batch programs (SPEC CPU2017-style compilers, interpreters, simulators) where dlmalloc or glibc malloc is the current allocator
- Single-threaded servers such as a redis-like event loop, where the paper reports a small gain (1.01x over mimalloc, 1.10x over dlmalloc)
- Workloads shaped like mimalloc-bench's single-threaded tests, where the paper reports 1.93x over dlmalloc and 25.2% less memory than mimalloc
- As a design reference for specializing mimalloc when you control the threading model

## Skip it when

- Any program that allocates or frees from more than one thread: the design removes the logic needed for thread safety and remote frees
- Production use today: no public repository, license or release was found
- If you already run mimalloc: the reported gain is only about 1.03-1.05x on SPEC and 1.01x on redis, inside the noise of many deployments
- When you need hardening, profiling hooks or the mature tooling of jemalloc/mimalloc

## How it is fast

It keeps mimalloc's segment/page layout (segments of about 4 MiB split into pages per size class) but uses one centralized heap instead of per-thread heaps, so there is no remote-free coordination. Each page has a single free-block list instead of mimalloc's sharded local/thread/remote free lists, and no atomics or synchronization are needed. The paper also tunes when memory is committed and when it is returned, trading allocation speed against footprint.

## Compared with alternatives

Choose it over LWMalloc or rlsf only for study, since none of them ships a usable Exgen-Malloc; for a real single-threaded deployment, mimalloc (its parent) gets nearly the same speed with thread safety. SpeedMalloc from the same group targets multi-threaded code and needs new hardware.

## Integration

| | |
|---|---|
| **Form** | not documented (no code release found) |
| **Dependencies** | not documented |
| **Minimum toolchain** | not documented |
| **Platforms** | evaluated on two Intel Xeon platforms (per search snippet); others not documented |
| **Thread safety** | Not thread-safe by design (single-threaded only) |
| **Drop-in for the baseline** | partial — meant to replace malloc/free in single-threaded programs, but no artifact is available to drop in |

## Gotchas

- Search snippets disagree: one version says 1.17x over dlmalloc and 1.05x over mimalloc on SPEC CPU2017, another (the abstract wording the verifier used) says 1.19x and 1.03x; probably different arXiv/CAL revisions
- A library that spawns a helper thread (logging, async I/O, OpenMP) quietly breaks the single-thread assumption
- The 1.93x mimalloc-bench figure is against dlmalloc; against mimalloc the same suite shows only 1.02x

## Known shortcomings

- No code release found. Built by stripping mimalloc down to one centralized heap with one free list per page, single-thread only, about 2000 LOC, measured on two Intel Xeon machines. Snippets give two sets of numbers (1.17x/1.05x and 1.19x/1.03x against dlmalloc and mimalloc on SPEC CPU2017); the mimalloc-bench 1.93x is against dlmalloc and only 1.02x against mimalloc. Snippet only (arXiv and mirrors blocked).

## Caveats and trade-offs

IEEE CAL 2025 short paper; arXiv (2510.10219), the UT Austin PDF and IEEE page are blocked, so numbers come from search snippets only. Snippets disagree with the original record (1.19x vs 1.17x over dlmalloc, 1.03x vs 1.05x over mimalloc). No repository found; single-threaded only.

Single-thread only, about 2000 lines, built by trimming mimalloc.

## Maintenance

Research prototype with no public code or license found; reference-only, and the paper itself could not be opened in this session.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed IEEE Computer Architecture Letters 2025 paper ('Old is Gold: Optimizing Single-Threaded Applications With ExGen-Malloc') comparing against dlmalloc and mimalloc on SPEC CPU2017; the PDF hosts (arXiv 2510.10219, ut-sysml.ece.utexas.edu, IEEE) are egress-blocked, so the numbers come from search snippets only and no code was found.
- **Verifier notes:** Corrected speedups to the abstract snippet wording (1.19x dlmalloc, 1.03x mimalloc). A paper-access retier could check compiler/CPU and a code release.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Sources the enricher read:**
  - WebSearch snippets for arxiv.org/pdf/2510.10219, ut-sysml.ece.utexas.edu/publications/prints/cal2025_li.pdf, ieeexplore.ieee.org/document/11075519, emergentmind.com/topics/exgen-malloc, researchgate.net/publication/396458314 (all pages EGRESS_BLOCKED on direct fetch)
  - https://arxiv.org/pdf/2510.10219 (blocked, 403)
  - https://ut-sysml.ece.utexas.edu/publications/prints/cal2025_li.pdf (blocked, 403)
  - https://www.emergentmind.com/topics/exgen-malloc (blocked)
  - https://sigops.org/s/conferences/hotos/2023/papers/li.pdf (blocked, 403)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `paper:exgen-malloc`) · [data/wave11/enrich/raw/paper_exgen_malloc.json](../../../data/wave11/enrich/raw/paper_exgen_malloc.json) (enrichment confidence 0.4)

</details>
