# NOVA (linux-nova)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0` · 🔴 abandoned

> Research Linux kernel file system for persistent memory; per-inode logs beat ext4-DAX, xfs-DAX, PMFS and btrfs on write-heavy workloads.

| | |
|---|---|
| **Beats** | ext4-DAX, xfs-DAX, PMFS, Ext4-data, Btrfs (kernel file systems on NVM) |
| **Claimed result** | FAST'16 paper abstract (search snippet only): in write-intensive workloads 22% to 216x throughput improvement over state-of-the-art file systems and 3.1x to 13.5x over file systems with equally strong consistency guarantees. README: outperforms other DAX-enabled file systems in almost all cases; sub-page updates are an exception (whole-page COW). |
| **Workload** | Log-structured file system for byte-addressable NVMM, Filebench and macro workloads |
| **Metric** | throughput |
| **Adoption** | 443 stars |
| **Last commit** | 2022-02-21 |
| **Links** | [repository](https://github.com/NVSL/linux-nova) · [benchmark](https://github.com/NVSL/linux-nova) |

## Verdict

The FAST'16 paper (Xu and Swanson) measured NOVA on Intel's Persistent Memory Emulation Platform (dual-socket Xeon emulating STT-RAM and PCM latencies with DRAM) and reports 22% to 216x higher throughput than ext4-DAX, xfs-DAX, PMFS, ext4 and btrfs on write-intensive workloads, and 3.1x to 13.5x over equally consistent ext4-data and btrfs; the paper PDF was blocked here, so these figures come from search snippets of the abstract and evaluation, and the README itself states only that NOVA beats other DAX file systems in almost all cases.

## Use it when

- Research or evaluation on persistent memory (Optane DC PMem or memmap-emulated pmem) where you need a strongly consistent file system that is faster than ext4-DAX or xfs-DAX on write-intensive, metadata-heavy workloads such as Filebench fileserver or varmail.
- As the standard comparison baseline for new PM file systems: MadFS, SplitFS and WineFS all report against NOVA.
- Workloads that need atomic file data updates and crash consistency without paying ext4 data-journaling or btrfs costs (the paper reports 3.1x to 13.5x over file systems with equally strong guarantees).
- Studying log-structured, per-CPU NVMM file system design; fs/nova and Documentation/filesystems/nova.txt describe the layout in detail.

## Skip it when

- Production systems: the README says it is not ready for production use, and 53 open issues include crash-consistency and data-loss bugs (data leak on crash during truncate, wrong st_nlink after crash during unlink, unreadable file after crash during append, a kernel hang in the snapshot cleaner).
- Anything that needs a current kernel: the newest branch is Linux 5.1 (others 4.13 to 5.0) and the last commit was 2022-02-21; porting to a modern kernel is on you.
- Small sub-page overwrites: copy-on-write of whole 4 KB pages makes them slower than in-place DAX file systems, which the README names as the main exception to its speedups.
- Non-x86-64 machines, setups needing xattrs/ACLs, quotas, mkfs/fsck tooling, or moving a file system between machines with different CPU counts, all listed as missing.
- Hardware without persistent memory: on block SSDs it has no role, and Optane PMem itself is discontinued, so most users will run it on DRAM emulation.

## How it is fast

It is a log-structured file system with one metadata-only log per inode instead of a global log, so updates to different files proceed in parallel and garbage collection stays cheap; file data lives outside the log and is updated copy-on-write, giving atomic writes without double-writing data through a journal. Multi-inode operations use small fixed-length per-CPU journals, and free space and inode tables are split into per-CPU allocation regions and stripes. Lookup structures (a per-file radix tree, red-black trees) are kept in DRAM and rebuilt from the NVMM logs, which can be scanned by many threads in parallel during recovery.

## Compared with alternatives

Pick NOVA over SplitFS or MadFS when you want an in-kernel file system with atomic data and metadata and no user-space library; choose WineFS instead for memory-mapped workloads (it reports up to 2x over NOVA there), and MadFS for concurrent appends from user space.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Full Linux kernel source tree (5.1 master) with CONFIG_LIBNVDIMM, CONFIG_BLK_DEV_PMEM, CONFIG_FS_DAX and CONFIG_NOVA_FS; selects CRC32 and LIBCRC32C |
| **Minimum toolchain** | Whatever builds Linux 5.1 (older GCC era); not documented beyond the kernel's own requirements |
| **Platforms** | x86-64 Linux only; needs NVMM/pmem hardware or memmap emulation |
| **Thread safety** | Kernel file system; concurrent access through the VFS, with per-inode logs and per-CPU allocators and journals for scalability |
| **Drop-in for the baseline** | partial — POSIX-compatible replacement for ext4-DAX or xfs-DAX at mount level, but only after booting a patched out-of-tree kernel; write() to pages that are mmap'd is not supported |

## Gotchas

- No mkfs: the first `mount -o init` formats the device, and a later mount without init recovers it; remounting with a different option set may fail.
- While a file is DAX-mmap'd, its data is not covered by NOVA's parity protection; the program owns that data until it is unmapped.
- Mounted snapshots are not write-protected; the docs tell users not to write after mounting a snapshot.
- Protection features cost speed and are switchable (data_parity=0, metadata_csum=0, inplace_data_updates=1, wprotect); compare configurations carefully when reading benchmark results.

## Known shortcomings

- 53 open issues, many of them crash-consistency or data-loss bugs: 152 (data leak on a crash during truncate), 125 (st_nlink), 121 (append), 156 (snapshot cleaner hang). Linux 5.1 and x86-64 only, not production ready. Numbers are snippet only (paper PDFs blocked); measured on PMEP emulation hardware.

## Caveats and trade-offs

Paper (Xu and Swanson, FAST'16, https://www.usenix.org/conference/fast16/technical-sessions/presentation/xu) blocked in this environment; numbers from search-result snippets of the abstract. Out-of-tree Linux 5.1 kernel tree, GPL-2.0 WITH Linux-syscall-note; self-described as not production ready (no mkfs/fsck, no xattrs, x86-64 only). Needs NVMM/DAX hardware or emulation. Last commit 2022-02-21.

Kernel tree fork (Linux with NOVA in fs/nova); ties you to an old kernel; copy-on-write cost for sub-page updates.

## Maintenance

Abandoned research code (last commit 2022-02-21, Linux 5.1, 53 open issues) under GPL-2.0, self-described as not production ready; useful as a research baseline rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states qualitatively that NOVA outperforms other DAX file systems in almost all cases (sub-page updates excepted) and defers numbers to the FAST'16 paper; the paper PDF (usenix.org) was egress-blocked, so the peer-reviewed numbers were seen only in search snippets and B cannot be confirmed here.
- **Verifier notes:** Candidate for a paper-access retier to B: the FAST'16 abstract's 22%-216x and 3.1x-13.5x figures were confirmed by two independent search snippets but the USENIX PDF returned a proxy 403. Last commit 2022-02-21 is over 3 years old, so abandoned.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/NVSL/linux-nova>
  - <https://github.com/NVSL/linux-nova/commits/master>
  - <https://raw.githubusercontent.com/NVSL/linux-nova/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVSL/linux-nova/HEAD/COPYING>
- **Sources the enricher read:**
  - <https://github.com/NVSL/linux-nova>
  - <https://github.com/NVSL/linux-nova/issues>
  - <https://raw.githubusercontent.com/NVSL/linux-nova/HEAD/README.md>
  - <https://raw.githubusercontent.com/NVSL/linux-nova/HEAD/Documentation/filesystems/nova.txt>
  - <https://raw.githubusercontent.com/NVSL/linux-nova/HEAD/fs/nova/Kconfig>
  - <https://raw.githubusercontent.com/NVSL/linux-nova/HEAD/fs/nova/Makefile>
  - <https://raw.githubusercontent.com/NVSL/linux-nova/HEAD/Makefile>
  - http://cseweb.ucsd.edu/\~swanson/papers/FAST2016NOVA.pdf (403, blocked)
  - https://www.cs.fsu.edu/\~awang/courses/cop5611_s2024/nova2.pdf (blocked)
  - https://www.usenix.org/system/files/login/articles/login_fall16_04_xu.pdf (blocked)
  - WebSearch: NOVA log-structured file system FAST 2016 Xu Swanson evaluation PMEP ext4-DAX throughput filebench results
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/nvsl/linux-nova`) · [data/wave11/enrich/raw/github_com_nvsl_linux_nova.json](../../../data/wave11/enrich/raw/github_com_nvsl_linux_nova.json) (enrichment confidence 0.7)

</details>
