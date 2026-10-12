# Hoard

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Drop-in multithreaded malloc replacement beating Solaris/Ptmalloc via per-processor heaps and bounded blowup.

| | |
|---|---|
| **Beats** | Solaris default allocator, Ptmalloc (glibc malloc backing operator new/delete) |
| **Claimed result** | Paper abstract: up to 60x over the standard Solaris allocator on 14 processors, and up to 18x over the next best allocator tested. At 14 processors: Larson 18x faster than Ptmalloc, threadtest 278% faster than Ptmalloc, shbench 85% faster than Ptmalloc. Uniprocessor: BEMengine 10.3% faster than the Solaris allocator, but the average over the uniprocessor benchmarks is 6.2% slower than Solaris. |
| **Workload** | Uniprocessor and multiprocessor (1-14 way Sun Enterprise 5000) allocation-intensive benchmarks: threadtest, shbench, Larson server simulation, active/passive false-sharing tests, BEMengine PDE solver, Barnes-Hut n-body solver, plus single-threaded espresso/Ghostscript/LRUsim/p2c. |
| **Metric** | throughput |
| **Hardware** | Sun Enterprise 5000, 2GB RAM, 14x 400MHz UltraSPARC CPUs, 4MB L2 cache, Solaris 7 |
| **Compiler and flags** | GNU C++ at -O6 (Sun Workshop C++ compiler 5.0 used only for Barnes-Hut) |
| **Adoption** | 1.25k stars; historically used by AOL, Cisco, SAP, Reuters, RBC and others per README; standard allocator option in SPEC CPU2006 |
| **Last commit** | 2026-07-19 |
| **Links** | [repository](https://github.com/emeryberger/Hoard) · [benchmark](http://www.cs.utexas.edu/users/mckinley/papers/asplos-2000.pdf) |

## Verdict

The ASPLOS 2000 paper (14x400MHz UltraSPARC Sun Enterprise 5000, Solaris 7, GNU C++ -O6) measured up to 60x over the Solaris default allocator and up to 18x over Ptmalloc at 14 processors on Larson, with threadtest 278% and shbench 85% faster than Ptmalloc at 14p, but a 6.2% average uniprocessor slowdown versus Solaris. The current README adds unreviewed first-party benchmarks on a 192-core 2-node AMD EPYC system claiming 1.3-1.5x higher Larson throughput than glibc/mimalloc/jemalloc and 1.6x over glibc at 128 threads on NUMA, while conceding jemalloc wins the linux-scalability workload.

## Use it when

- Multithreaded server-style workloads with many short-lived allocations and cross-thread object passing (Larson-style)
- Multi-socket NUMA machines, where README claims up to 1.6x over glibc at 128 threads
- Realloc-heavy workloads (repeated grow/shrink), where README claims 2-5x over other allocators
- Programs suffering false sharing or heap contention from the default allocator on multiprocessor hardware
- Deployments wanting a mature (25+ yr), Apache-2.0, provably-bounded-blowup allocator rather than a newer research allocator

## Skip it when

- Single-threaded/uniprocessor programs — the original ASPLOS paper measured Hoard averaging 6.2% slower than the Solaris allocator uniprocessor (shbench +49.2% runtime, Ghostscript +10.6% runtime)
- Very high pure malloc/free-pair throughput with no work between calls (linux-scalability benchmark) — current README concedes jemalloc wins this workload
- Windows binaries statically linking the CRT (/MT) — Hoard cannot intercept allocation calls embedded in the executable, only /MD dynamic-CRT builds
- Code wanting a std::allocator-compatible template to plug into individual STL containers — Hoard replaces malloc/new globally, not per-container
- Extreme thread counts (256+) where README shows Hoard only matching mimalloc rather than leading

## How it is fast

Per-processor heaps plus a global heap reduce lock contention, with objects grouped into size-class "superblocks" that move between per-thread and global heaps to keep memory use provably bounded rather than growing per-CPU. Thread-local allocation buffers (TLAB, see hoardtlab.h/percputlab.h) give a lock-free fast path, and a remote-free queue (remotefreequeue.h) lets a thread free memory another thread allocated without a global lock. Superblocks are cache-line aligned to avoid false sharing, and the spinlock (futexlock.h) uses PAUSE/YIELD exponential backoff.

## Compared with alternatives

Pick Hoard over NUMAlloc/scalloc when you want a long-deployed (AOL/Cisco/SAP-era), Apache-2.0, SPEC CPU2006-standard allocator with a proven bounded-blowup guarantee rather than a newer research allocator. SuperMalloc's own README claims to beat the best of DLmalloc/JEmalloc/Hoard/TBBmalloc outright, so prefer SuperMalloc if squeezing out more raw throughput matters more than Hoard's maturity and simpler (non-HTM) build.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none at runtime beyond libc; build fetches Heap-Layers, printf (allocation-free printf), and alloc8 (interposition library) via CMake FetchContent |
| **Minimum toolchain** | CMake 3.15+; targets C++23 but CMAKE_CXX_STANDARD_REQUIRED is OFF; Linux needs libstdc++-dev installed |
| **Platforms** | Linux, macOS (Intel + Apple Silicon arm64/arm64e), Windows (x86, x64, ARM, ARM64 via Microsoft Detours) |
| **Thread safety** | not documented as a formal guarantee, but the architecture (per-processor heaps, TLAB fast path, remote-free queue) is built specifically for safe cross-thread alloc/free |
| **Drop-in for the baseline** | partial — LD_PRELOAD/DYLD_INSERT_LIBRARIES or link-time replacement on Unix is a true drop-in; on Windows it requires /MD dynamic-CRT linkage and DLL injection or import-table patching, and cannot intercept /MT static-CRT executables |

## Gotchas

- Windows apps must be built with /MD; /MT static-CRT binaries embed their own allocator and Hoard can't hook them
- Historical Windows crashes from CRT/DLL interop (e.g. _onexit shimming, ucrtbase heap corruption) took years to fully resolve per issue #51; worth checking current behavior on your exact Windows/CRT version
- Multi-heap design bounds memory blowup mathematically but does not eliminate it — expect some extra memory versus a single-heap allocator in exchange for scalability
- linux-scalability (pure malloc/free pairs, no intervening work) is explicitly called out in the README as adversarial to Hoard's superblock design

## Caveats and trade-offs

Primary evidence is the ASPLOS 2000 paper, run on 14x 400MHz UltraSPARC with Solaris 7 against the Solaris and Ptmalloc allocators of that era; the GNU C++ version is unstated. Uniprocessor, Hoard averaged 6.2% slower than the Solaris allocator (shbench +49.2%, espresso +15.9%, Ghostscript +10.6% runtime). The current README adds first-party modern results (code in benchmarks/, 192-core 2-node AMD EPYC, exact CPU model, compiler, and flags unstated, charts only). Those results claim 1.3-1.5x higher Larson throughput than glibc, mimalloc, and jemalloc, and 1.6x faster than glibc at 128 threads on NUMA. The README concedes that jemalloc wins linux-scalability. Hoard is also in daanx/mimalloc-bench as 'hd', but those results are chart images only.

Multi-heap design trades some memory for scalability (bounded blowup, not zero); link-time/LD_PRELOAD drop-in malloc replacement, not a std::allocator template adapter; per-processor heap hashing can cause heap/thread collisions.

## Maintenance

Actively maintained (last commit 2026-07-19, open PR/issue #84 adding hot-path optimizations); Apache-2.0 and a simple drop-in library, so easy to vendor or pin even if development slowed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed ASPLOS 2000 paper compares Hoard against the Solaris 7 default allocator and Ptmalloc (glibc) on a 14-way Sun Enterprise 5000 with GNU C++ -O6. The compiler version is unstated and the benchmark code is not tied to the paper, so it falls short of A.
- **Verifier notes:** The old record had '10.6% faster (BEMengine)'. The paper's BEMengine figure is 10.3% faster; 10.6% is Ghostscript, where Hoard is slower. The earlier caveat said no modern reproduction exists, but the README now has modern first-party benchmarks against glibc. Those are tier C material, so the paper keeps this entry at B.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/emeryberger/Hoard>
  - <http://www.cs.utexas.edu/users/mckinley/papers/asplos-2000.pdf>
  - <https://www.cs.utexas.edu/~mckinley/papers/asplos-2000.pdf>
  - <https://github.com/daanx/mimalloc-bench>
- **Sources the enricher read:**
  - <https://github.com/emeryberger/Hoard>
  - <https://github.com/emeryberger/Hoard/blob/main/README.md>
  - <https://github.com/emeryberger/Hoard/blob/main/CMakeLists.txt>
  - <https://github.com/emeryberger/Hoard/blob/main/src/README.md>
  - <https://github.com/emeryberger/Hoard/blob/main/src/include/hoard/README>
  - <https://github.com/emeryberger/Hoard/issues/51>
  - <https://github.com/emeryberger/Hoard/issues/84>
  - <https://github.com/emeryberger/Hoard/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/emeryberger/hoard`) · [data/wave1/enrich/raw/github_com_emeryberger_hoard.json](../../../data/wave1/enrich/raw/github_com_emeryberger_hoard.json) (enrichment confidence 0.6)

</details>
