# vmcache (with exmap)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Single-file C++20 database buffer manager that uses virtual memory for page translation; beats mmap-based LMDB and WiredTiger on TPC-C.

| | |
|---|---|
| **Beats** | mmap-based buffer management (and OS page cache) |
| **Claimed result** | SIGMOD'23 paper (snippet only, PDF not opened): vmcache with exmap beats the mmap-based LMDB and WiredTiger on TPC-C and random-read workloads, and exmap is required to scale to high IOPS. The record's 'up to 67% and 35% read/s' figures could not be confirmed. |
| **Workload** | Database buffer manager using virtual-memory-assisted page translation, TPC-C and random-read workloads; exmap kernel module for scalable page-table manipulation |
| **Metric** | throughput |
| **Adoption** | 86 stars |
| **Last commit** | 2025-09-09 |
| **Links** | [repository](https://github.com/viktorleis/vmcache) · [benchmark](https://www.cs.cit.tum.de/fileadmin/w00cfj/dis/_my_direct_uploads/vmcache.pdf) |

## Verdict

The SIGMOD'23 paper (snippets only; the TUM, TUHH, TU Braunschweig and ACM copies are egress-blocked here) compares vmcache and vmcache+exmap with LeanStore, WiredTiger and mmap-based LMDB on TPC-C and random lookups: in memory vmcache reaches almost 90 M lookups/s and about 3 M TPC-C txn/s, WiredTiger trails significantly and LMDB does not scale on TPC-C, and out of memory exmap adds about 60% on random lookups, though LeanStore stays faster there. The repo has the driver and the Makefile flags but no results, hardware or CPU model.

## Use it when

- Building or studying a storage engine whose working set exceeds RAM on fast NVMe, where you want mmap-like pointer access without mmap's uncontrolled eviction and write-back
- In-memory or mostly-cached OLTP workloads: the paper (snippet) reports almost 90 M lookups/s and about 3 M TPC-C transactions/s with a 128 GB pool
- Out-of-memory random reads on Linux where you can load a kernel module: exmap adds about 60% over plain vmcache by sidestepping kernel eviction scalability limits (snippet)
- As an MIT-licensed reference for optimistic latching and virtual-memory-based page translation to port into your own engine

## Skip it when

- Out-of-memory random lookups where peak steady-state throughput matters: the paper snippet says vmcache is substantially slower than LeanStore there because it is bound by the kernel
- Workloads that delete data: storage free-space management is an open TODO and allocCount only grows, so pages are never reused on disk
- Environments where you cannot set vm.overcommit_memory=1 or load kernel modules (exmap uses a kallsyms workaround for non-exported symbols and has no LICENSE file)
- Heavy lock contention: latches spin; C++ wait/notify is listed as a TODO
- Non-Linux platforms: depends on Linux mmap/madvise semantics, libaio and O_DIRECT

## How it is fast

Page IDs map straight to virtual addresses, so hot-path page access needs no hash-table lookup or pointer swizzling; correctness comes from optimistic version-validated latches in a 64-bit atomic state word per page. Eviction is a clock over a lock-free resident-page hash set and drops frames in batches (BATCH, default 64) with madvise(MADV_DONTNEED). With the optional exmap kernel module, page allocation and freeing go through per-thread ioctl batches on a VMA the kernel does not manage, which avoids Linux's TLB-shootdown and page-table locking bottlenecks during eviction.

## Compared with alternatives

Pick vmcache over UMap or FastMap when you are writing a DBMS and want the engine, not the kernel, to decide eviction and I/O, with an MIT license; pick TriCache or UMap when you need to accelerate an unmodified mmap-based application instead of rewriting its storage layer.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | libaio; optional exmap kernel module (tuhhosg/exmap, MODULE_LICENSE GPL, no LICENSE file) |
| **Minimum toolchain** | C++20 (Makefile: g++ -DNDEBUG -O3 -std=c++20 -fnon-call-exceptions -fasynchronous-unwind-tables) |
| **Platforms** | Linux x86-64 (tested by the authors); needs a block device or file opened with O_DIRECT |
| **Thread safety** | Multi-threaded by design (up to 128 worker threads, maxWorkerThreads), optimistic and exclusive page latches; each thread needs a workerThreadId |
| **Drop-in for the baseline** | no |

## Gotchas

- VIRTGB must be at least the device size and larger values need vm.overcommit_memory=1; running out of virtual pages exits with 'VIRTGB is too low'
- Page size is a compile-time 4096; issue #1 reports that switching to 2MB pages made the B-tree allocate far too many pages (closed without a documented fix)
- Built with -fnon-call-exceptions because optimistic reads can touch evicted pages and restart via exceptions; keep those flags if you vendor the code
- Default BLOCK is /tmp/bm, a regular file, so default runs do not measure a raw NVMe device

## Known shortcomings

- Snippet numbers: in memory about 90M lookups/s and about 3M TPC-C txn/s; exmap about +60% on out-of-memory random lookups; LeanStore is still faster out of memory. The 67% and 35% figures remain unconfirmed. Makefile flags g++ -O3 -std=c++20. No free-space management, fixed 4 KB pages, issue 1 (2 MB pages) closed without a documented fix.

## Caveats and trade-offs

Numbers come from search snippets only, because the paper PDF host is egress-blocked; the record's 67%/35% exmap figures are unconfirmed. The comparison is against mmap-based systems (LMDB) and other buffer managers, not against a bare mmap loop. The repo README has the benchmark driver (TPC-C and random read via env vars) but no results. exmap (tuhhosg/exmap) is a separate Linux kernel module with no LICENSE file; module/driver.c declares MODULE_LICENSE("GPL"). vmcache itself is MIT and runs without exmap (EXMAP=0).

Needs libaio, vm.overcommit_memory=1, and the exmap kernel module for best scaling (exmap repo has no LICENSE file seen); research code with TODOs.

## Maintenance

Research code with recent commits (2025-09-09) and an MIT license; small enough (one 1,855-line vmcache.cpp plus TPC-C headers) to vendor, but missing storage free-space management.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo README has no numbers; the numbers live in the SIGMOD'23 paper it links (cs.cit.tum.de vmcache.pdf), and every copy of that paper (TUM, osg.tuhh.de, ibr.cs.tu-bs.de, dl.acm.org) is egress-blocked here. A search snippet says WiredTiger and the mmap-based LMDB are significantly slower than vmcache and LeanStore, and that exmap is needed to reach full speed on fast storage. The paper is peer-reviewed, so this could become B once someone opens it; it stays C because the figures are snippet-only.
- **Verifier notes:** Metadata checked on github.com: MIT, 86 stars, not a fork, last commit 2025-09-09 (active). Opening the paper (SIGMOD'23, DOI 10.1145/3588687) would allow a retier to B.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/viktorleis/vmcache>
  - <https://github.com/viktorleis/vmcache/commits>
  - <https://raw.githubusercontent.com/viktorleis/vmcache/HEAD/README.md>
  - <https://raw.githubusercontent.com/viktorleis/vmcache/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tuhhosg/exmap/HEAD/README.md>
  - <https://raw.githubusercontent.com/tuhhosg/exmap/HEAD/module/driver.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/viktorleis/vmcache/HEAD/README.md>
  - <https://raw.githubusercontent.com/viktorleis/vmcache/HEAD/Makefile>
  - <https://raw.githubusercontent.com/viktorleis/vmcache/HEAD/vmcache.cpp>
  - <https://github.com/viktorleis/vmcache/issues?q=is%3Aissue>
  - <https://github.com/viktorleis/vmcache/issues/1>
  - <https://raw.githubusercontent.com/tuhhosg/exmap/HEAD/README.md>
  - <https://github.com/tuhhosg/exmap>
  - WebSearch: Virtual-Memory Assisted Buffer Management evaluation (snippets of the paper)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/viktorleis/vmcache`) · [data/wave11/enrich/raw/github_com_viktorleis_vmcache.json](../../../data/wave11/enrich/raw/github_com_viktorleis_vmcache.json) (enrichment confidence 0.65)

</details>
