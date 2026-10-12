# Spaces

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Single-file C malloc replacement for Linux x86-64 with destroyable region heaps; README ranks it ahead of jemalloc on several mimalloc-bench workloads.

| | |
|---|---|
| **Beats** | jemalloc (also snmalloc, tcmalloc, Hoard in the same table) |
| **Claimed result** | larson 124 M ops/s, ranked #2 and ahead of jemalloc, snmalloc, tcmalloc and Hoard; malloc-large 6.0 ms/alloc #2 (beats jemalloc, snmalloc, Hoard); mleak 0.26 s #2; glibc-simple 6.9 s #3 (beats jemalloc, snmalloc); top 3 on 7 of 8 workloads, #6 on glibc-thread |
| **Workload** | mimalloc-bench workloads (larson, malloc-large, mleak, glibc-simple, xmalloc-test, mstress, spacesbench, glibc-thread) built against libspaces.a; median of 3 runs |
| **Metric** | throughput |
| **Compiler and flags** | gcc -O3 -pthread -fPIC for spaces.c; bench.sh builds the mimalloc-bench workloads with \$compiler -O3 -pthread against libspaces.a; how the competitor allocators were built is not stated |
| **Adoption** | 64 stars |
| **Last commit** | 2026-03-29 |
| **Links** | [repository](https://github.com/xtellect/spaces) · [benchmark](https://github.com/xtellect/spaces#performance) |

## Verdict

The README table gives Spaces' own numbers on mimalloc-bench workloads built with gcc -O3 against libspaces.a (larson 124 M ops/s, malloc-large 6.0 ms per allocation, mleak 0.26 s, glibc-simple 6.9 s, xmalloc-test 10.6 M/s, mstress 6.9 s) with a rank against jemalloc, snmalloc, tcmalloc and Hoard; competitor values, the #1 allocator, CPU, core count and compiler version are not given.

## Use it when

- C or C++ programs on x86-64 Linux that want arena-style teardown (parsers, compilers, per-request heaps) and a general malloc in the same library.
- Subsystems that need a hard memory budget enforced by the allocator (spaces_chunk_set_ceiling returns NULL or calls your handler).
- Debugging or diagnostics where walking every live allocation in a region at run time, with no profiler or rebuild, is useful.
- Workloads like larson (cross-thread producer-consumer) and large 5-25 MB blocks, where the README ranks it #2 among the allocators it tested.
- Fixed-size object pools (list nodes, connection structs) through spaces_chunk_create_fixed.

## Skip it when

- Anything other than x86-64 Linux: the single-file distribution is pre-processed for that one target only.
- Heavy thread churn or many threads allocating widely varying sizes: README says it ranks #6 on glibc-thread and that the slab working set does not stay cache-hot with 500 threads.
- Memory-tight services: each slab has a 64 KB virtual footprint, the 4 KB slab header wastes about 6% per segment, and freed memory is not returned with MADV_FREE, so RSS stays high until reuse.
- Choosing on speed alone: mimalloc-style allocators appear to rank #1 on the README's workloads, and no competitor numbers, CPU model or compiler version are published.
- Projects needing mature, audited code: 2 commits (2026-03-23 and 2026-03-29), no releases, 64 stars.

## How it is fast

Slabs are 64 KB-aligned, so free() finds size class, owner thread and region by masking the pointer (ptr & \~0xFFFF) with no page map or radix tree. There are 52 size classes from 8 B to 8 KB with a per-thread intrusive freelist cache (832 B in total), so same-thread malloc/free uses no atomics or locks; cross-thread frees go to a per-slab ABA-safe Treiber stack (one CAS each). Allocations above 8 KB come straight from mmap with huge-page support; slabs come from 4 MB batch regions (about one mmap per 64 slabs), and heap state is pooled across thread create/destroy.

## Compared with alternatives

Pick Spaces over Mesh or IsoAlloc when you want region destroy, per-region ceilings and live-allocation walking in the same library as a fast malloc; pick a mainstream general-purpose allocator (the catalog's jemalloc/mimalloc class) or v8malloc when raw multi-threaded throughput or portability matters more, since Spaces publishes no competitor numbers and runs only on x86-64 Linux.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc and pthreads (uses System V shm/sem headers) |
| **Minimum toolchain** | GCC (Makefile uses gcc -O3 -pthread -fPIC; uses GCC __sync builtins and pragmas); minimum version not documented |
| **Platforms** | x86-64 Linux only |
| **Thread safety** | Thread-safe by default (per-thread caches, CAS-based remote free); thread-exclusive mode drops locking and must only be used when one thread owns all allocations in that chunk |
| **Drop-in for the baseline** | partial: drop-in malloc replacement for jemalloc when statically linked with -Wl,--whole-archive (libspaces.so is also built); the region API is extra and not jemalloc-compatible (no mallctl) |

## Gotchas

- The default error handler is interactive: on double free, bad pointer or ceiling violation it prints to stderr and loops on getchar() asking Abort/Retry/Ignore; the loop has no EOF case, so with stdin closed or at end-of-file it spins forever. Install spaces_set_error_handler early in main() for servers, daemons and CI (README says the same).
- Intrusive freelist overwrites the first 8 bytes of a freed object, and the minimum allocation is 8 bytes.
- bench.sh only times Spaces itself (median wall time and peak RSS over 3 runs, stdout discarded, non-zero exits still counted); it builds no competitor allocators and does not include the 'spacesbench' workload, so the README ranks cannot be reproduced from the repo. The Makefile's bench-all target passes -a -T, which bench.sh does not accept.
- Include spaces.h after &lt;stdlib.h&gt; and other headers that declare malloc.

## Known shortcomings

- Harness flaw: bench.sh times only Spaces (wall time and RSS, stdout discarded, nonzero exits counted), builds no competitors and lacks spacesbench, so the README's rank against the other allocators is not reproducible from the repo. Makefile bench-all passes -a -T, which bench.sh rejects. The default error handler loops on getchar() with no EOF case, so it spins forever if stdin is closed.

## Caveats and trade-offs

First-party table gives ranks and absolute numbers for Spaces only, not the competitors' numbers; the 'beats' lists differ per row (mleak beats only jemalloc and snmalloc; xmalloc-test beats snmalloc and tcmalloc; mstress beats tcmalloc and Hoard), and the allocator ranked #1 is never named (likely mimalloc). CPU model, core count, kernel and compiler version are not stated; repo has only 2 commits (2026-03-23 and 2026-03-29); x86-64 Linux only. Loses on glibc-thread (#6).

x86-64 Linux only in the single-file build; 8-byte minimum allocation; 64 KB virtual footprint per slab; every free() reads the slab header (one possible L1 miss); explicit heap regions, budgets, heap walking and shared-memory heaps in addition to malloc replacement; weak on heavy thread churn (500 threads).

## Maintenance

Active but very young (2 commits, last 2026-03-29); MIT-licensed single file that is easy to vendor, but x86-64 Linux only and unproven outside its author's benchmarks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance table gives Spaces' own absolute numbers plus rank against jemalloc, snmalloc, tcmalloc and Hoard on mimalloc-bench workloads; competitor numbers, CPU model and compiler version are absent, so first-party C despite public bench.sh.
- **Verifier notes:** Numbers match the README table exactly. MIT confirmed via LICENSE; 64 stars, not archived, last commit 2026-03-29.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/xtellect/spaces/HEAD/README.md>
  - <https://raw.githubusercontent.com/xtellect/spaces/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/xtellect/spaces/HEAD/LICENSE>
  - <https://github.com/xtellect/spaces/commits>
- **Sources the enricher read:**
  - <https://github.com/xtellect/spaces>
  - <https://raw.githubusercontent.com/xtellect/spaces/HEAD/README.md>
  - <https://raw.githubusercontent.com/xtellect/spaces/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/xtellect/spaces/HEAD/Makefile>
  - <https://raw.githubusercontent.com/xtellect/spaces/HEAD/spaces.c>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/xtellect/spaces`) · [data/wave11/enrich/raw/github_com_xtellect_spaces.json](../../../data/wave11/enrich/raw/github_com_xtellect_spaces.json) (enrichment confidence 0.7)

</details>
