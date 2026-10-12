# UMap

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-2.1` · 🟢 active

> LLNL user-space mmap replacement built on userfaultfd; beats Linux mmap for large-page, out-of-core reads with tuned paging.

| | |
|---|---|
| **Beats** | mmap (Linux system mmap service) |
| **Claimed result** | Papers (snippets): 1.25x to 2.5x over system mmap on tested applications; 1.22-1.9x over an optimized kernel service across concurrency levels; 1.2-1.5x on Ligra |
| **Workload** | User-space page fault handler via userfaultfd for out-of-core data stores, Ligra, LMAT and N-body style apps |
| **Metric** | throughput |
| **Adoption** | 115 stars |
| **Last commit** | 2026-07-21 |
| **Links** | [repository](https://github.com/LLNL/umap) · [benchmark](https://github.com/LLNL/umap) |

## Verdict

All numbers are first-party and come from paper snippets (PDFs on osti.gov, arxiv.org and web.cels.anl.gov are blocked here): 1.22-1.9x over an optimized kernel-based service across intra-node concurrency, 1.2-1.5x over system mmap on Ligra applications, and about 2.5x over mmap at 8 MiB UMap pages on NVMe/Optane, with UMap ahead only above 64 KiB pages. Hardware, kernel and compiler were not visible in the snippets, and the repo has no benchmark code (applications are in LLNL/umap-apps).

## Use it when

- Out-of-core, read-mostly scans or graph analytics (Ligra BFS-style) over files much larger than RAM on NVMe or Optane, where coarse paging pays off
- Workloads that tolerate large UMap pages (64 KiB and up; the paper snippet reports the best result at 8 MiB pages)
- HPC codes that want per-application control of page size, read-ahead, buffer size and worker counts without kernel changes
- Datasets split over many files or a remote store, via SparseStore or a custom Umap::Store

## Skip it when

- Small-page random access: per the paper snippet UMap only overtakes mmap when the page size exceeds 64 KiB
- Shared mappings or multi-process sharing: UMAP_SHARED is not supported
- Containers with Docker's default seccomp profile, or hosts where vm.unprivileged_userfaultfd=0 and you are not root
- Write-heavy or correctness-critical data without testing: open issue #71 reports pages changing without being marked dirty (eviction miscompare under umapsort, 128 threads); write mode needs kernel &gt;= 5.7 and 5.7-5.9 can hang on writes
- Programs creating many mappings: open issue #91 reports ENOMEM from UFFDIO_REGISTER past about 900 regions; LGPL-2.1 may also rule it out for static linking

## How it is fast

Faults are delivered as userfaultfd messages and resolved by pools of filler and evictor threads, with decoupled fault queues, configurable read-ahead and load balancing across workers. The UMap page size is independent of the 4 KiB system page (UMAP_PAGESIZE), so one fault can pull megabytes in a single bulk read; fewer faults and larger transfers are where the gain over kernel mmap comes from. Eviction uses high/low watermarks on a bounded buffer instead of the global page cache.

## Compared with alternatives

Pick UMap when you need an unmodified kernel and a library-only, mmap-shaped API with tunable large pages; FastMap and vmcache/exmap claim larger gains over mmap but need a kernel module or custom kernel, and TriCache targets transparent caching of whole applications rather than explicit mappings.

## Integration

| | |
|---|---|
| **Form** | shared lib \| static lib (CMake) |
| **Dependencies** | Linux kernel headers with userfaultfd; no other libraries |
| **Minimum toolchain** | C++11, C99, CMake &gt;= 3.5.1 |
| **Platforms** | Linux only; kernel &gt;= 4.3 read-only, &gt;= 5.7 read/write (&gt;= 5.10 preferred); any architecture with userfaultfd |
| **Thread safety** | Not documented per call; the runtime itself is multi-threaded (filler and evictor pools, default hardware_concurrency each) and guards region setup with a global mutex |
| **Drop-in for the baseline** | partial — mmap-shaped signature, but separate umap/uunmap calls, private mappings only, and different fault/flush semantics |

## Gotchas

- Default CMake build type is Debug and ENABLE_LOGGING defaults to On; build with -DCMAKE_BUILD_TYPE=Release before measuring
- Write-protect (read/write) mode is chosen at compile time from the build host's kernel headers; a binary built against 5.10 headers fails at runtime on an older kernel, and some distros (Ubuntu 20.04.2) ship headers that hide the feature
- UMAP_BUFSIZE defaults to 90% of free memory and filler/evictor counts default to hardware_concurrency each, so an untuned process can grab most of RAM and many threads
- Tuning is by environment variables (UMAP_PAGESIZE, UMAP_BUFSIZE, UMAP_PAGE_FILLERS, UMAP_PAGE_EVICTORS, watermarks), read at runtime start, not per region by default

## Known shortcomings

- Open issues 71 (data miscompares: a page is dirty without a dirty mark during eviction) and 91 (ENOMEM past about 900 regions), not tied to the paper numbers. Default build is Debug with logging on. The roughly 2.5x over mmap at 8 MiB pages is a snippet number, and UMap wins only above 64 KiB pages.

## Caveats and trade-offs

Paper PDFs (osti.gov, arxiv.org, ieeexplore) egress-blocked; numbers quoted from search-result snippets, not from an opened page. Snippets confirm 1.22-1.9x over an optimized kernel-based service and 1.3x-1.6x rising with concurrency; the 1.25x-2.5x and Ligra 1.2-1.5x figures were not re-seen in this verification. Repo README has no numbers; applications live in LLNL/umap-apps. Default CMake build is Debug; use -DCMAKE_BUILD_TYPE=Release. Needs userfaultfd (vm.unprivileged_userfaultfd=1 for non-root) and Linux &gt;= 5.10 for read/write mode.

Needs userfaultfd (Linux 4.3+, read/write mode 5.7+), unprivileged_userfaultfd setting; LGPL.

## Maintenance

Recent commits on develop (last 2026-07-21) but the issue tracker is quiet, with 2018-2022 bugs (#71 data miscompares, #91 ENOMEM) still open; LGPL-2.1, small enough to build from source on Linux.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README has no numbers; it cites the TPDS 2021 and MCHPC 2019 papers, whose comparison against Linux mmap (1.22-1.9x over an optimized kernel service; speedup rising 1.3x to 1.6x with concurrency) was seen only in search snippets because osti.gov and arxiv.org are egress-blocked. First-party (LLNL authors) and unopened, so C.
- **Verifier notes:** Metadata matches (115 stars, LGPL-2.1, last commit 2026-07-21 on develop). Paper-access retier to B candidate once the TPDS paper (osti.gov/servlets/purl/1829975) is reachable.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/LLNL/umap>
  - <https://raw.githubusercontent.com/LLNL/umap/HEAD/README.md>
  - <https://github.com/LLNL/umap/commits/develop>
- **Sources the enricher read:**
  - <https://github.com/LLNL/umap>
  - <https://raw.githubusercontent.com/LLNL/umap/develop/README.md>
  - <https://raw.githubusercontent.com/LLNL/umap/develop/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LLNL/umap/develop/cmake/BuildEnv.cmake>
  - <https://raw.githubusercontent.com/LLNL/umap/develop/src/umap/umap.h>
  - <https://github.com/LLNL/umap/tree/develop/docs/sphinx>
  - <https://raw.githubusercontent.com/LLNL/umap/develop/docs/sphinx/environment_variables.rst>
  - <https://raw.githubusercontent.com/LLNL/umap/develop/docs/sphinx/getting_started.rst>
  - <https://raw.githubusercontent.com/LLNL/umap/develop/docs/sphinx/sparse_store.rst>
  - <https://github.com/LLNL/umap/issues?q=is%3Aissue>
  - <https://github.com/LLNL/umap/issues/71>
  - <https://github.com/LLNL/umap/issues/91>
  - https://web.cels.anl.gov/projects/argo/publications/2022-tpds-peng.pdf (EGRESS_BLOCKED)
  - WebSearch snippets: osti.gov purl 1829975 (TPDS 2021), osti.gov purl 1574628 and arxiv 1910.07566 (MCHPC 2019)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/llnl/umap`) · [data/wave11/enrich/raw/github_com_llnl_umap.json](../../../data/wave11/enrich/raw/github_com_llnl_umap.json) (enrichment confidence 0.65)

</details>
