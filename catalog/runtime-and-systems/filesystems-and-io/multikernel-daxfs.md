# DAXFS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0` · 🟢 active

> Linux kernel filesystem on DAX memory with lock-free CAS overlay; authors report up to 2.68x tmpfs random-write throughput.

| | |
|---|---|
| **Beats** | tmpfs (kernel in-memory file system, POSIX read/write) |
| **Claimed result** | Paper snippet (arXiv 2604.01620): up to 2.68x higher random write throughput than tmpfs with 4 threads and 1.18x higher random read throughput at 64 KB |
| **Workload** | DaxFS on single-host DRAM-backed DAX vs tmpfs: random write throughput with 4 threads and random read throughput at 64 KB (paper title: DAXFS: A Lock-Free Shared Filesystem for CXL Disaggregated Memory) |
| **Metric** | throughput |
| **Adoption** | 102 stars |
| **Last commit** | 2026-08-16 |
| **Links** | [repository](https://github.com/multikernel/daxfs) · [benchmark](https://arxiv.org/abs/2604.01620) |

## Verdict

The authors' arXiv preprint 2604.01620 (seen only through search-result snippets; arxiv.org and alphaxiv are egress-blocked) reports that on single-host DRAM-backed DAX DaxFS beats tmpfs on all write workloads, up to 2.68x random-write throughput at 4 threads, and 1.18x random-read throughput at 64 KB; hardware, kernel, compiler and fio parameters were not visible. The same snippet describes cross-host validation only under QEMU-emulated CXL 3.0, with '&gt;99% CAS accuracy', a wording that does not obviously match its 'no lost updates' claim.

## Use it when

- Several kernel instances on one cache-coherent machine (multikernel) that must share one read-mostly tree, such as a container base image or LLM model weights, without N copies in memory
- Zero-copy CPU or GPU access to file data held in a dma-buf or DMA heap
- Concurrent small random writes from several threads to an in-memory filesystem, where the authors measured up to 2.68x tmpfs throughput at 4 threads on DRAM-backed DAX
- Research or prototyping on CXL shared-memory filesystems, as a lock-free alternative to famfs's single-master model

## Skip it when

- Block devices or SSDs: the design needs byte-addressable DAX memory and cannot run on block storage
- Real multi-host CXL deployments today: the cxl3 backend is a scaffold, and COHERENCE.md says multi-host operation is unsupported until a validation gate passes on CXL 3.0 hardware
- Workloads that need strict POSIX write semantics or crash durability: issue #26 reports unserialised i_size updates in daxfs_write_iter() (no inode_lock), #28 says replace-rename is not crash-atomic, and #23 says daxfs_mem_sync() does not flush cache lines
- Large or growing writable data sets: the overlay hash table size is fixed at creation, files are capped at about 1M pages (4 GB) by the 20-bit page offset (#22, reported as -ENOSPC), and lookups degrade to a full-table scan once the table fills (#19)
- Big-endian machines (#20: CAS loops never terminate) and setups that need device nodes, FIFOs or sockets (no mknod)

## How it is fast

Reads are direct loads from the DAX region with no page-cache copy. Writes go to a copy-on-write hash overlay: an open-addressing, linear-probing table of 16-byte buckets claimed with cmpxchg (FREE to USED), and entries come from a bump allocator advanced with atomic fetch-and-add, so there is no journal, no log and no lock between writers in one coherence domain. A direct-mapped shared page cache with a CAS-driven FREE/PENDING/VALID state machine and clock eviction serves backing-file data to all participants.

## Compared with alternatives

Pick DAXFS over NOVA, WineFS or SplitFS when the need is sharing one in-memory filesystem across kernel instances or a dma-buf with lock-free concurrent writers, rather than durable persistent-memory storage for a single kernel; MadFS and SplitFS are user-space PM file systems for one host and do not offer a shared namespace.

## Integration

| | |
|---|---|
| **Form** | Linux kernel module (out-of-tree, built with make) plus user-space tools mkdaxfs and daxfs-inspect |
| **Dependencies** | Linux 5.11+ with CONFIG_FS_DAX; DAX-capable memory (pmem, CXL, DMA heap or dma-buf, or a physical range via /dev/mem) |
| **Minimum toolchain** | Kernel build environment for the target kernel (5.11+); exact compiler not documented |
| **Platforms** | Linux; coherence primitives described in terms of x86 LOCK CMPXCHG; little-endian only in practice (issue #20) |
| **Thread safety** | Lock-free CAS coordination is correct only within one hardware cache-coherence domain (COHERENT backend, default); cross-host CXL3 backend unvalidated; concurrent extending writes race on i_size per issue #26 |
| **Drop-in for the baseline** | partial: same POSIX file API as tmpfs once mounted, but needs a DAX memory region and mkdaxfs-created image, a fixed-size overlay, and lacks mknod |

## Gotchas

- The overlay table and pool are sized at mkdaxfs time (-O, -B); the pool is never compacted, and a full table makes every new page cost a full-table scan (issue #19).
- The default mem_model=coherent means one coherence domain; selecting mem_model=cxl3 on ordinary DRAM only exercises plumbing and validates nothing about cross-host coherence.
- The performance numbers come from the April 2026 preprint, before May-August 2026 write-path fixes (O_APPEND honoured in the overlay write path, generic_write_checks() and s_maxbytes added), so the measured write path did less checking than the current one.
- Mounting an image from untrusted sources should use the validate mount option; issue #21 reports daxfs_mem_ptr() bounds-checks only the start offset of a read span.

## Known shortcomings

- Numbers come from write-path code that was fixed after the April 2026 preprint (O_APPEND on May 30, generic_write_checks on Aug 16); issue 26 says daxfs_write_iter takes no inode_lock (unserialised i_size, which may help write throughput against tmpfs). The snippet says '&gt;99% CAS accuracy' next to 'no lost updates', which is inconsistent. Open: 19 (full-table O(n) lookup), 20 (big-endian CAS hang), 21 (bounds check covers the start offset only), 23 (no cache-line flush), 28 (rename not crash-atomic); the cxl3 backend is unvalidated. Paper snippet only.

## Caveats and trade-offs

Numbers only from WebSearch snippet of the authors' arXiv preprint 2604.01620 (arxiv.org egress-blocked, paper not opened); repo README states no performance numbers. Measured on DRAM-backed DAX on a single host, not on CXL hardware; cross-host CXL coherence is described by the README as gated, unvalidated future work. tmpfs is not in the listed baselines. Linux kernel module (GPL-2.0).

Needs DAX-capable memory (PM, CXL, DMA buffers), not block devices; GPL kernel module.

## Maintenance

Active but single-maintainer (all recent commits by congwang-mk, last 2026-08-16), 102 stars, 11 open issues including six labelled bugs; GPL-2.0 kernel code is copyable but needs a kernel build and a DAX setup.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Repo README has no numbers (only a qualitative 'Why Not tmpfs' table); the 2.68x random-write and 1.18x 64 KB random-read figures vs tmpfs come from the authors' own arXiv preprint 2604.01620 (not peer-reviewed, first-party, Cong Wang is the repo's main committer), seen only via search snippet since arxiv.org is egress-blocked.
- **Verifier notes:** Metadata checked on github.com: GPL-2.0, 102 stars, last commit 2026-08-16, not a fork. benchmark_url pointed at the repo, which has no numbers; corrected to the arXiv abstract URL returned by search (not opened, blocked). A paper-access retier could move it once the PDF is reachable.
- **Fields the verifier corrected:** `benchmark_url`, `workload`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/multikernel/daxfs>
  - <https://github.com/multikernel/daxfs/commits>
  - <https://raw.githubusercontent.com/multikernel/daxfs/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/multikernel/daxfs>
  - <https://raw.githubusercontent.com/multikernel/daxfs/HEAD/README.md>
  - <https://raw.githubusercontent.com/multikernel/daxfs/HEAD/docs/COHERENCE.md>
  - <https://github.com/multikernel/daxfs/tree/main/tests>
  - <https://github.com/multikernel/daxfs/issues>
  - <https://github.com/multikernel/daxfs/issues/26>
  - <https://github.com/multikernel/daxfs/issues/19>
  - <https://github.com/multikernel/daxfs/commits>
  - WebSearch: DAXFS lock-free shared filesystem CXL disaggregated memory arXiv 2604.01620 (snippet of https://arxiv.org/abs/2604.01620)
  - https://www.alphaxiv.org/abs/2604.01620 (EGRESS_BLOCKED)
  - https://linuxiac.com/daxfs-proposed-as-a-zero-copy-shared-memory-filesystem-for-linux/ (EGRESS_BLOCKED)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/multikernel/daxfs`) · [data/wave11/enrich/raw/github_com_multikernel_daxfs.json](../../../data/wave11/enrich/raw/github_com_multikernel_daxfs.json) (enrichment confidence 0.55)

</details>
