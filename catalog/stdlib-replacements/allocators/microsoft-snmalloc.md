# snmalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++ allocator using lock-free message-passing frees, beating glibc malloc on cross-thread and batch-deallocation workloads.

| | |
|---|---|
| **Beats** | glibc malloc |
| **Claimed result** | Figure 5 (producer/consumer malloc-test, random 8-2048B objects, thread sweep): at 64 threads snmalloc \~190M and snmalloc-1mib \~220M allocs/sec vs glibc \~47M (\~4x, derived from page data, approximate chart reading). Figure 4 (symmetric workload): at 64 threads snmalloc \~180M vs glibc \~105M allocs/sec (\~1.7x, derived from page data, approximate), with tcmalloc/jemalloc/SuperMalloc ahead of snmalloc. Figure 6 (producer/consumer by object size): snmalloc \~570M vs glibc \~110M at 16B (\~5x) and \~250M vs \~27M at 1KiB (\~9x), with glibc near zero above \~4KiB while snmalloc stays at or above \~120M up to 32KiB (derived from page data, approximate). SPECspeed Integer (Fig 12), verbatim: snmalloc performs "as well or better than the widely used jemalloc, tcmalloc and glibc's allocator on all benchmarks". |
| **Workload** | ISMM 2019 paper micro-benchmarks: a symmetric workload (each thread allocates, swaps with another thread, and deallocates) and a producer/consumer workload (malloc-test, half the threads allocate batches of 4096 objects sized 8-2048B, the other half deallocate), swept from 1 to 64 threads; also a SPECspeed 2017 Integer suite run and two real-application integrations (FaRM, FreeBSD libc) |
| **Metric** | throughput |
| **Hardware** | Micro-benchmarks (Figs 4-10): Ubuntu 18.04 Azure Standard F64s_v2 VM, 64 vCPUs on dual-socket Intel Xeon Platinum 8168, 128 GB RAM; SPECspeed suite: Ubuntu 18.04 Azure Standard D3_v2 VM, 4 vCPUs (Intel Xeon E5-2673), 14 GB RAM |
| **Adoption** | 2.0k stars; Rust bindings via the snmalloc-rs crate (linked from README) |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/microsoft/snmalloc) · [benchmark](https://github.com/microsoft/snmalloc/blob/main/snmalloc.pdf) |

## Verdict

ISMM 2019 paper, producer/consumer malloc-test thread sweep (64 threads, Ubuntu 18.04 on an Azure F64s_v2 VM, 64 vCPUs, dual-socket Xeon Platinum 8168, 128 GB RAM): snmalloc reaches roughly 190-220M allocs/sec versus glibc ptmalloc2's \~47M (\~4x, read off chart data). On the symmetric same-thread workload the gap narrows to \~1.7x and jemalloc/tcmalloc/SuperMalloc beat snmalloc outright. No compiler or flags are given, which caps this at evidence tier B.

## Use it when

- Multi-threaded C/C++ services with heavy cross-thread free (producer/consumer queues, thread pools, work-stealing schedulers).
- Workloads with bursty batch deallocation (freeing thousands of objects at once) that stall thread-caching allocators.
- Need a glibc- or jemalloc-API-compatible drop-in on Linux/BSD via LD_PRELOAD or static link.
- Rust services wanting the same allocator via the snmalloc-rs crate.
- Security-conscious C++ services that can absorb &lt;5% overhead for the hardened build (guard pages, freelist-corruption checks, randomization).

## Skip it when

- Single-threaded or same-thread-dominated allocation patterns: the paper's own symmetric-workload chart (Fig 4) shows jemalloc, tcmalloc and SuperMalloc ahead of snmalloc there.
- OpenBSD: BUILDING.md lists it as a supported PAL, but issue #594 (open since 2023, still unresolved as of a Sept 2025 comment) says pagemap init fails because OpenBSD has no overcommit.
- NetBSD without a libatomic implementation or without Clang, since the default NetBSD toolchain emits libatomic calls snmalloc needs.
- Building with GCC — the project itself calls this 'not recommended' due to extra libatomic calls for 128-bit atomics.
- Long-running processes with certain shapes: open issues report committed-memory growth over time (#814, #846) and slab thrashing for transient large-object alloc/dealloc pairs (#811), unresolved as of Sept 2026.

## How it is fast

Frees on the allocating thread take no lock and no atomic operation. Frees from a different thread go through a lock-free message-passing scheme that batches remote deallocations and returns them to the owner with a single atomic operation instead of one per free, so throughput scales with core count. Large page ranges (superslabs) amortize metadata bookkeeping, and the malloc/free fast path is two branches under Clang on Linux.

## Compared with alternatives

Pick snmalloc over mimalloc/jemalloc/TCMalloc when the workload is dominated by cross-thread free or bursty batch deallocation — that's the specific case its message-passing remote-free design targets. The paper itself shows jemalloc and tcmalloc ahead of snmalloc on same-thread alloc/free, so prefer one of those siblings when allocation and deallocation mostly happen on the same thread.

## Integration

| | |
|---|---|
| **Form** | header-only (also static/shared lib via CMake) |
| **Dependencies** | none at runtime; build needs CMake 3.21+ and Ninja |
| **Minimum toolchain** | C++17 minimum (SNMALLOC_USE_CXX17 flag for legacy support); default build and PAL concept checks assume C++20; Clang 6.0+ recommended |
| **Platforms** | Linux, macOS/iOS (XNU), Windows (Visual Studio 2019+/clang-cl), FreeBSD, NetBSD, Android out of the box; x86-64/ARM/PowerPC/RISC-V/SPARC plus experimental CHERI; OpenBSD is listed but currently broken (issue #594) |
| **Thread safety** | Core design goal, not an afterthought: same-thread free requires no synchronization; cross-thread free is lock-free via message passing |
| **Drop-in for the baseline** | partial — LD_PRELOAD gives an ABI-level drop-in swap for glibc malloc on ELF platforms and jemalloc_compat.cc adds jemalloc-API compatibility; globally overriding malloc/free/new/delete on Windows is still an open problem per issues #700, #782, #783 |

## Gotchas

- Remote deallocation batches into a default 1 MiB outgoing buffer before memory returns to the owning thread — tunable, trades some memory for throughput.
- Hardened build (libsnmalloc-checks.so) adds guard pages, freelist-corruption checks and randomization; measured at &lt;5% overhead on mimalloc-bench on a 72-core Azure VM, but it's a separate opt-in build, not the default.
- Metadata layout has changed significantly since the 2019 ISMM paper (per the README's own admission), so current performance and internals differ from what's described in snmalloc.pdf.
- RISC-V Linux: flat pagemap reservation is reported oversized on Sv39 (issue #861, open).

## Caveats and trade-offs

Speedups vs glibc are read off linear-scale throughput charts (Figs 4-6), not stated as ratios in prose, so they are approximate. The only verbatim vs-glibc statement is the SPECspeed 'as well or better' sentence. On the symmetric workload (Fig 4), jemalloc and tcmalloc beat snmalloc. No compiler or flags are given, so B not A. The FreeBSD 12.0 libc integration in the paper was the authors' own experiment (24 Makefile lines) to show ease of adoption; it did not make snmalloc FreeBSD's default malloc, and FreeBSD libc still ships jemalloc. The README says the implementation 'has evolved significantly since the initial paper... most of the meta-data layout has changed', so current performance may differ from the 2019 figures.

message-passing remote deallocation adds an outgoing-buffer/batching mechanism (tunable, default 1MiB) which trades a little memory for throughput; higher implementation complexity than simple thread-caching allocators; paper notes SuperMalloc needed &gt;100s to reach peak throughput while snmalloc/glibc/rpmalloc warm up in about 20s

## Maintenance

Actively maintained — commits as recent as 2026-09-21 and 53 open issues being triaged; MIT-licensed and header-only so it vendors easily, but its internals have diverged substantially from the 2019 paper the headline numbers come from.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): downgrade; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed ACM ISMM '19 paper compares against ptmalloc2 from glibc 2.27 in throughput charts (Figs 4-6) and in SPECspeed (Fig 12), where the prose says snmalloc performs 'as well or better than the widely used jemalloc, tcmalloc and glibc's allocator on all benchmarks'. It gives no compiler or flags, so it stays B and cannot be A.
- **Verifier notes:** Tier B stands, but the record had a false claim: that snmalloc has been FreeBSD libc's default since 12.0 (in stars_or_usage and claimed_speedup). The paper calls FreeBSD libc 'using jemalloc' the baseline, and freebsd-src lib/libc/stdlib/malloc/ contains only jemalloc. The chart numbers (150-200M vs &lt;50M at 64 threads) belong to Figure 5's thread sweep, not the 1KiB-32KiB size sweep (Fig 6b), where glibc is far lower. The hardware split was also wrong: the Xeon 8168 is the CPU of the F64s_v2 VM.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/microsoft/snmalloc/blob/main/snmalloc.pdf>
  - <https://github.com/microsoft/snmalloc>
  - <https://github.com/microsoft/snmalloc#readme>
  - <https://github.com/freebsd/freebsd-src/tree/main/lib/libc/stdlib/malloc>
- **Sources the enricher read:**
  - <https://github.com/microsoft/snmalloc>
  - <https://github.com/microsoft/snmalloc/blob/main/docs/BUILDING.md>
  - <https://github.com/microsoft/snmalloc/blob/main/docs/PORTING.md>
  - <https://github.com/microsoft/snmalloc/blob/main/CMakeLists.txt>
  - <https://github.com/microsoft/snmalloc/issues>
  - <https://github.com/microsoft/snmalloc/issues/594>
  - <https://github.com/microsoft/snmalloc/tree/main/src/snmalloc/override>
  - <https://github.com/microsoft/snmalloc/blob/main/src/snmalloc/override/malloc.cc>
  - <https://github.com/microsoft/snmalloc/blob/main/docs/security/README.md>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/microsoft/snmalloc`) · [data/wave0-seed/enrich/raw/github_com_microsoft_snmalloc.json](../../../data/wave0-seed/enrich/raw/github_com_microsoft_snmalloc.json) (enrichment confidence 0.62)

</details>
