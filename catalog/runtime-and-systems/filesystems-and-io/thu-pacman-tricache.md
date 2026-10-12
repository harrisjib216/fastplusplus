# TriCache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> User-space multi-level block cache over SPDK SSDs that runs unmodified in-memory programs out-of-core, beating Linux swap and mmap.

| | |
|---|---|
| **Beats** | mmap and Linux swap (OS page cache) |
| **Claimed result** | Search-result snippets of the OSDI'22 paper (not opened): speedups over OS swapping 6.30x on PageRank and 26.1x on WCC; up to 12.4x over mmap at 32 GB memory; more than an order of magnitude over the Linux page cache in places. The 0.85x BFS figure could not be confirmed. |
| **Workload** | Out-of-core graph processing (Ligra PR, WCC, BFS), RocksDB, Terasort and LiveGraph run unmodified on a user-transparent multi-level block cache over SSDs |
| **Metric** | throughput |
| **Hardware** | 2x AMD EPYC 7742, &gt;=512 GB RAM, 8x Intel P4618 SSDs, Debian 11.1, Linux 5.10 (artifact recommendations) |
| **Adoption** | 77 stars |
| **Last commit** | 2025-12-08 |
| **Links** | [repository](https://github.com/thu-pacman/TriCache) · [benchmark](https://github.com/thu-pacman/TriCache) |

## Verdict

Per WebSearch snippets of the OSDI'22 paper (the PDF and the project page are egress-blocked): on uk-2014 with Ligra, TriCache's speedups 'over OS swapping and FlashGraph' are given as 6.30x and 5.31x on PageRank, 26.1x and 1.46x on WCC, and 0.85x and 2.05x on BFS; the snippet's pairing is ambiguous, so which baseline the BFS 0.85x belongs to is not certain. The snippets also report up to 12.4x over mmap for LiveGraph, 2-3 orders of magnitude over mmap for out-of-core RocksDB, and up to 39.3x over swapping for GNU sort, on 2x EPYC 7742, 512 GB RAM and 8x Intel P4618 SSDs. The repo holds the scripts to reproduce these but no result numbers.

## Use it when

- An existing in-memory C/C++ program must run on a dataset several times larger than DRAM and rewriting it for out-of-core is not an option.
- Linux swap or mmap thrashes on random-access out-of-core workloads such as PageRank or WCC on large graphs, RocksDB PlainTable over mmap, or LiveGraph.
- A dedicated server with many NVMe SSDs that can be handed to SPDK, plus spare cores for cache server threads.
- Research or prototyping that compares against FastMap, FlashGraph or swap, where the OSDI'22 artifact scripts can be reused.

## Skip it when

- BFS-like traversals: per the paper snippet, the BFS result is 0.85x (a slowdown) in the swap/FlashGraph comparison.
- Shared or production machines: the configured SSDs are reformatted repeatedly, md RAIDs on the host will be broken, and setup needs password-free sudo, unlimited memlock and transparent hugepages disabled.
- Programs not built with clang: libcache and the instrumentation plugin need Clang (clang-13 in the scripts), and code that is not instrumented will not go through the cache.
- Small or commodity setups: the artifact targets 2x EPYC 7742, at least 512 GB RAM and 8 SSDs; there is no evidence for laptop-scale use.
- Long-term maintained dependencies: it is an artifact branch (osdi-ae) with 4 issues, one open (LiveGraph SF100 run fails, 2025-11-30).

## How it is fast

Address translation and concurrency control are split across levels: a per-thread (or per-fiber) direct cache and a private cache serve repeated accesses to the same page without locking, and only misses reach a shared cache partitioned across dedicated server cores, each owning SSDs through SPDK (with libaio and io_uring backends also present). It uses a compact hash page table and CLOCK/LRU replacement in user space, so no page faults or kernel page-cache locks sit on the hot path. Per the paper abstract, this exploits spatial and temporal locality to make per-access storage-to-memory translation cheap enough for a virtual-memory interface.

## Compared with alternatives

Pick TriCache over UMap, FastMap or vmcache when the program cannot be changed and you can recompile with Clang and give it whole SSDs. UMap needs explicit umap() regions, FastMap is a kernel patch on 4.14, and vmcache/exmap is a buffer manager you build a DBMS around. Choose SPDK or liburing directly when you control the I/O code.

## Integration

| | |
|---|---|
| **Form** | static lib (libcache) plus LLVM pass plugin; header-only C++ core (cache_header) |
| **Dependencies** | SPDK v21.04 with TriCache's patch (DPDK), Boost (fiber, thread), libnuma, libaio, optional liburing, OpenMP, bundled mimalloc and fadec |
| **Minimum toolchain** | C++17; Clang 13 (scripts) for libcache and the plugin; CMake; built with -march=native and ThinLTO |
| **Platforms** | Linux x86-64 with NVMe SSDs (tested Debian 11.1, kernel 5.10) |
| **Thread safety** | Designed for multithreaded programs: per-thread/per-fiber direct and private caches in front of a partitioned shared cache; pthread_create is hooked to register clients |
| **Drop-in for the baseline** | partial — no source changes, but the program must be recompiled with the Clang plugin and linked against libcache, and SSDs must be given to SPDK |

## Gotchas

- Startup throws if CACHE_PHY_SIZE, CACHE_VIRT_SIZE, CACHE_NUM_CLIENTS, CACHE_CONFIG or CACHE_MALLOC_THRESHOLD is unset; how to size them came up in issue #1.
- Only allocations above CACHE_MALLOC_THRESHOLD, and mmaps above the configured file threshold, are redirected into the cache; smaller ones stay in DRAM.
- libcache replaces memcpy, memset, memcmp, strlen, read, write and other libc symbols process-wide, which can interact badly with other interposers or sanitizers.
- Builds use -march=native, so binaries are not portable across CPUs.

## Known shortcomings

- A BFS 0.85x figure now appears in a search snippet that pairs 'OS swapping and FlashGraph' (PR 6.30x/5.31x, WCC 26.1x/1.46x, BFS 0.85x/2.05x); which baseline the 0.85x belongs to is unclear. Other snippet numbers: RocksDB 2-3 orders of magnitude over mmap and GNU sort up to 39.3x over swapping. Open issue 4: the LiveGraph SF100 run fails. The USENIX PDF was not opened.

## Caveats and trade-offs

Paper PDF (usenix.org/system/files/osdi22-feng.pdf) is egress-blocked in this environment; numbers come from search-result snippets, not an opened page, and the BFS 0.85x figure from the search record was not seen. Repo README (osdi-ae branch) lists the compared systems and hardware but has no numbers. Compiler flags not stated. Needs heavy hardware (2x EPYC 7742, 512 GB RAM, 8 SSDs, SPDK). OSDI'22 paper, so tier would be B if the paper were opened.

Needs SPDK-style SSD access (devices get formatted), huge memory and many SSDs; BFS is slower than swap (0.85x); intrusive setup.

## Maintenance

Research artifact (osdi-ae default branch, last touched 2025-12-08 for dataset links), Apache-2.0 and reproducible with the bundled scripts, but intrusive and hardware-heavy; treat it as a reference design rather than a library to depend on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Repo README (osdi-ae artifact) sets up comparisons against Linux swap and mmap with hardware stated but carries no numbers; the OSDI'22 paper (usenix.org) is egress-blocked, and search snippets confirm 6.30x on PR and 26.1x on WCC over OS swapping and 12.4x over mmap at 32 GB. Would be B (or A with flags) once the paper is opened.
- **Verifier notes:** Retier candidate to B once usenix.org PDF is reachable. Apache-2.0, 77 stars, last commit 2025-12-08 on osdi-ae confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/thu-pacman/TriCache>
  - <https://github.com/thu-pacman/TriCache/commits>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/thu-pacman/TriCache>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/README.md>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/scripts/build.sh>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/bind/hook.cpp>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/bind/cache.cpp>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/bind/segfault_handler.cpp>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/include/replacement.hpp>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/include/direct_cache.hpp>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/include/integrated_cache.hpp>
  - <https://raw.githubusercontent.com/thu-pacman/TriCache/HEAD/include/io_backend.hpp>
  - <https://github.com/thu-pacman/TriCache/issues?q=is%3Aissue>
  - <https://github.com/thu-pacman/TriCache/tree/osdi-ae/llvm-plugin>
  - <https://github.com/thu-pacman/TriCache/tree/osdi-ae/include>
  - https://pacman.cs.tsinghua.edu.cn/\~cwg/publication/tricache-2022/ (EGRESS_BLOCKED)
  - WebSearch snippets of https://www.usenix.org/system/files/osdi22-feng.pdf and https://www.usenix.org/conference/osdi22/presentation/feng
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/thu-pacman/tricache`) · [data/wave11/enrich/raw/github_com_thu_pacman_tricache.json](../../../data/wave11/enrich/raw/github_com_thu_pacman_tricache.json) (enrichment confidence 0.65)

</details>
