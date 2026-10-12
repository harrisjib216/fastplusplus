# WineFS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C` · `CC-BY-NC-4.0` · 🔴 abandoned

> Linux kernel file system for Intel Optane persistent memory that keeps 2MB hugepage mappings after aging; beats ext4-DAX, xfs-DAX, NOVA on mmap workloads.

| | |
|---|---|
| **Beats** | ext4-DAX, xfs-DAX and NOVA (kernel PM file systems); mmap workloads |
| **Claimed result** | README: outperforms ext4-DAX, NOVA and xfs-DAX by up to 2x on memory-mapped workloads (RocksDB, LMDB), and matches or beats them on Filebench and WiredTiger. Paper abstract (search snippet): in an aged setup LMDB gets 2x the write throughput of NOVA and 70% more than ext4-DAX; reads of a memory-mapped persistent radix tree have 56% lower median latency than NOVA |
| **Workload** | Memory-mapped RocksDB (YCSB) and LMDB workloads, plus Filebench and WiredTiger, on a hugepage-aware persistent-memory file system aged to 75% utilization with Geriatrix |
| **Metric** | throughput |
| **Hardware** | Experiments.md requirements: Intel Optane DC PM (500 GiB or more per socket), Cascade Lake CPU with clwb; exact CPU model not seen |
| **Adoption** | 36 stars |
| **Last commit** | 2022-01-13 |
| **Links** | [repository](https://github.com/utsaslab/WineFS) · [benchmark](https://github.com/utsaslab/WineFS) |

## Verdict

The SOSP'21 paper and artifact compare WineFS with ext4-DAX, xfs-DAX and NOVA on Linux 5.1 with Optane DC PM (2 sockets, 28 cores each, at least 500 GiB PM per socket), file systems aged to 75% with Geriatrix: up to 2x on mmap RocksDB (YCSB) and LMDB, LMDB 2x the write throughput of NOVA and 70% above ext4-DAX, and 56% lower median latency than NOVA for reads of a mmap'd radix tree (abstract figures via search snippet; paper PDF blocked here). Filebench and WiredTiger on clean file systems are parity or better. Compiler, flags and the exact CPU model are not given in the repo.

## Use it when

- Research or reproduction on Intel Optane DC PM (fsdax namespace, Cascade Lake with clwb) where you compare PM file systems
- Memory-mapped databases or key-value stores (LMDB, mmap-mode RocksDB, persistent radix trees) on a long-lived, highly utilized PM file system where ext4-DAX/NOVA fall back to 4KB pages
- Studying aging effects: the artifact comes with Geriatrix aging scripts and parse scripts for RocksDB/YCSB, LMDB, Filebench and WiredTiger
- Reading a compact example of hugepage-aware extent allocation and per-CPU journaling in a DAX file system

## Skip it when

- Any commercial use: the license is CC BY-NC 4.0, not an open-source software license
- Production data: the issue tracker has many open crash-consistency reports (non-atomic writes in strict mode #5, fast write path #16/#18, unlink #22, truncate #9/#20, evict_inode data loss #26, xattr bugs #24) with no maintainer fixes visible
- Modern kernels or hardware without Optane PM: code targets Linux 5.1 and Optane was discontinued; a build report (#10) shows an undefined sched_setaffinity symbol when building the module
- Clean, low-utilization file systems or POSIX-only workloads, where the paper's own summary is parity rather than a large win
- VMs: the README requires a bare-metal machine

## How it is fast

A dual-allocation policy: files that are memory-mapped get extents from a hugepage-aligned allocator (balloc.c keeps a separate huge_aligned_block_free_tree per CPU), while other POSIX files go to a hole-filling allocator over the unaligned tree, so 2MB-aligned free extents survive fragmentation. Page faults on aligned extents are served with hugepages, which cuts page-fault and TLB-miss counts. Per-CPU journaling, per-CPU free lists and auxiliary metadata keep metadata-heavy POSIX workloads on par with or ahead of ext4-DAX and NOVA.

## Compared with alternatives

Pick WineFS over NOVA (linux-nova) or SplitFS when the workload is memory-mapped and the PM file system is aged or nearly full, since hugepage preservation is its whole point; MadFS or SplitFS are better fits for POSIX read/write-heavy apps, and Trio/ArckFS reports beating WineFS on LevelDB.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Linux 5.1 kernel tree from the repo (FS_DAX, CRC16), ndctl to create an fsdax namespace with --align=1G |
| **Minimum toolchain** | not documented (kernel toolchain for Linux 5.1; Ubuntu 16.04-20.04 or Fedora 27/30 listed) |
| **Platforms** | x86-64 with Intel Optane DC PM and clwb (Cascade Lake); bare metal, at least 4 cores and 32 GB DRAM |
| **Thread safety** | Kernel file system; concurrent access via per-CPU journals and free lists (issue #2 reported a segfault creating 5 files on 4 cores, since closed) |
| **Drop-in for the baseline** | partial — same POSIX/mmap interface as ext4-DAX, but needs its own kernel build and reformatting the pmem device |

## Gotchas

- Kconfig still names the option DUOFS and the code calls itself pmfs internally; the module builds as winefs.ko from CONFIG_DUOFS
- pmfs_init_free_list in balloc.c only sets start_block for two-NUMA-node machines when the CPU count is exactly 96 or 32; with two nodes and any other count start_block is left uninitialized (read from the code, not tested)
- Strict mode is advertised as giving data atomicity, but open issue #5 (Hayley LeBlanc, 2021) shows an uncommitted overwrite surviving a simulated crash
- Experiments.md warns absolute numbers vary with NVDIMM firmware and wear, and RocksDB YCSB run C has high variance; average several runs

## Known shortcomings

- Many open crash-consistency issues with no maintainer fixes visible: 5 (strict-mode write not atomic), 16 and 18 (fast write path), 22 (unlink), 9 and 20 (truncate), 26 (evict_inode data loss), 24 (xattr). Code-read gotcha, not tested: balloc.c pmfs_init_free_list leaves start_block uninitialized on 2-NUMA-node machines unless the CPU count is exactly 96 or 32 (the paper machine had 112 threads). Numbers are abstract snippets only (paper PDF blocked). License is CC-BY-NC-4.0.

## Caveats and trade-offs

The license is Creative Commons Attribution-NonCommercial 4.0, which is not OSI-approved, so the code is reference only; it ships as a loadable module inside a Linux 5.1 kernel tree derived from PMFS. The SOSP'21 paper was not opened (cs.utexas.edu, pdl.cmu.edu and ACM all blocked); the paper figures come from search snippets. The record's 54% over ext4-DAX was not found; the snippet says 70% over ext4-DAX for LMDB when aged. Needs Optane PM hardware. Last commit 2022-01-13.

Kernel file system for Intel Optane PM; non-commercial license; research code on old kernels.

## Maintenance

Abandoned research code (last commit 2022-01-13) on Linux 5.1 for discontinued Optane hardware, CC BY-NC 4.0 and many open crash-consistency bugs, so it is reference only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SOSP'21 paper; the README and its linked Experiments.md artifact compare WineFS against ext4-DAX, xfs-DAX and NOVA and state an up-to-2x win on memory-mapped RocksDB and LMDB. The README has no compiler, flags or CPU model and the paper is blocked here, so it does not reach A.
- **Verifier notes:** Paper numbers come from abstract snippets only; README is qualitative (up to 2x). Last commit 2022-01-13 is more than 3 years old, so maintenance is abandoned.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `last_commit`, `maintenance_status`, `workload`, `caveats`
- **Shortcomings recorded by:** peer-reviewed paper, snippet only
- **Pages the verifier opened:**
  - <https://github.com/utsaslab/WineFS>
  - <https://github.com/utsaslab/WineFS/commits>
  - <https://raw.githubusercontent.com/utsaslab/WineFS/HEAD/README.md>
  - <https://raw.githubusercontent.com/rohankadekodi/WineFS/HEAD/Experiments.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/utsaslab/WineFS/HEAD/README.md>
  - <https://raw.githubusercontent.com/utsaslab/WineFS/HEAD/Experiments.md>
  - <https://github.com/utsaslab/WineFS/issues?q=is%3Aissue>
  - <https://github.com/utsaslab/WineFS/issues/5>
  - <https://github.com/utsaslab/WineFS/issues/16>
  - <https://github.com/utsaslab/WineFS/tree/main/Linux-5.1/fs/winefs>
  - <https://raw.githubusercontent.com/utsaslab/WineFS/HEAD/Linux-5.1/fs/winefs/balloc.c>
  - <https://raw.githubusercontent.com/utsaslab/WineFS/HEAD/Linux-5.1/fs/winefs/Kconfig>
  - <https://raw.githubusercontent.com/utsaslab/WineFS/HEAD/Linux-5.1/fs/winefs/Makefile>
  - WebSearch: WineFS SOSP 2021 evaluation (snippets of the abstract)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/utsaslab/winefs`) · [data/wave11/enrich/raw/github_com_utsaslab_winefs.json](../../../data/wave11/enrich/raw/github_com_utsaslab_winefs.json) (enrichment confidence 0.7)

</details>
