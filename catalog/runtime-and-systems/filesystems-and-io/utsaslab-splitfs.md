# SplitFS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> LD_PRELOAD user-space persistent-memory file system layered on ext4 DAX; cuts POSIX data-path overhead versus ext4 DAX and NOVA.

| | |
|---|---|
| **Beats** | ext4 DAX (POSIX file I/O on persistent memory; NOVA also compared in paper) |
| **Claimed result** | README: appends 5.8x faster than ext4 DAX (1.92M vs 0.33M appends/sec); up to 2x on data-intensive workloads; software overhead 4-12x lower than NOVA or ext4 DAX |
| **Workload** | Appends of 4 KB chunks to a file then fsync on persistent memory (README microbenchmark), plus LevelDB, SQLite, Redis, YCSB, tar, git in the SOSP'19 paper |
| **Metric** | throughput |
| **Hardware** | README microbenchmark: Intel CPU with clflush/clflushopt, 32 GB+ DRAM, bare metal, real or emulated PM; experiments.md replication setup for the paper: Intel Xeon E3-1225 v5 @ 3.30GHz, 4 cores, 32 GB DRAM, Ubuntu 16.04 |
| **Compiler and flags** | gcc -O3 for the microbenchmark (README); compiler version not stated |
| **Adoption** | 171 stars |
| **Last commit** | 2021-12-14 |
| **Links** | [repository](https://github.com/utsaslab/SplitFS) · [benchmark](https://github.com/utsaslab/SplitFS) |

## Verdict

First-party README run of micro/rw_experiment.c (gcc -O3, 4 KB sequential pwrite64 appends totalling 128 MB): ext4-DAX 0.33M vs SplitFS 1.92M appends/sec (5.8x), with the relink-on-close excluded from timing and no fsync despite the README text; CPU not named for that run. The SOSP'19 paper (peer-reviewed; PDF blocked here, not opened) and the experiments page report 4-12x lower software overhead than NOVA or ext4 DAX and up to 2x on data-intensive applications, on an Intel Xeon E3-1225 v5 with 32 GB DRAM running Ubuntu 16.04 with emulated or Optane PM.

## Use it when

- Research or prototyping on Intel Optane DC PMM (or memmap-emulated PM) where append- and overwrite-heavy apps such as LevelDB/YCSB or SQLite/TPC-C dominate
- Comparing PM file-system designs: the repo ships scripts for ext4-DAX, NOVA-strict, NOVA-relaxed, PMFS and SplitFS on YCSB, TPC-C, rsync, tar, git, LMDB, Filebench and FIO
- Studying the relink/staging-file technique for append atomicity without data copies
- Single-process workloads on a bare-metal Ubuntu 16.04/18.04 box you can boot into the bundled 4.13 kernel

## Skip it when

- Anything on ordinary SSDs or NVMe: it needs DAX-capable persistent memory, and Intel has discontinued Optane
- Production or modern kernels: it needs the patched Linux 4.13 kernel for relink (issue #46 asks about other kernels), and the last commit was 2021-12-14
- Multi-threaded writers: open issues #64 (fio multi-thread and random writes trip an assertion in tbl_mmaps.c) and #75 (multithreaded SQLite TPC-C fails), plus #27 on multi-thread correctness
- Crash-consistency-critical deployments: open issues #66 (strict-mode append recovery loses data when inode numbers change) and #67 (rename crash consistency)
- Metadata-heavy workloads: the experiments page says SplitFS has a modest overhead on metadata-intensive utilities such as rsync

## How it is fast

Reads and overwrites avoid the syscall and VFS path entirely by copying to and from mmapped DAX file regions. Appends are written with non-temporal stores (MOVNTI=1 in common.mk) into pre-allocated, pre-mapped staging files, and a new relink() syscall later moves those extents into the target file without copying the data. Strict mode adds an operation log in PM for atomicity.

## Compared with alternatives

Pick SplitFS when you need unmodified POSIX applications to keep ext4 DAX as the metadata layer and want per-process consistency modes; MadFS (also user-space, up to 3.6x over ext4-DAX on concurrent workloads) is the better choice for multi-threaded writers, WineFS (same lab) for mmap-heavy apps on a kernel PM file system, and Trio/ArckFS reports beating SplitFS on LevelDB.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | patched Linux 4.13 kernel (relink syscall), ext4 mounted with -o dax on a PM device, Boost, bundled liblfds711, glibc (calls intercepted via Quill) |
| **Minimum toolchain** | gcc with -O3 -m64 (common.mk); Ubuntu 16.04/18.04; compiler version not stated |
| **Platforms** | x86-64 Intel with clflush or clflushopt, bare metal (no VM), at least 32 GB DRAM and 4 cores per README |
| **Thread safety** | Locks are present, but multi-threaded write workloads fail per open issues #64, #75 and #27 |
| **Drop-in for the baseline** | partial — POSIX API is unchanged via LD_PRELOAD, but only for absolute paths under /mnt/pmem_emul, only for the intercepted calls, and only with the custom kernel |

## Gotchas

- The README says the 5.8x microbenchmark appends 128 MB and does an fsync() at the end, but micro/rw_experiment.c has no fsync: it times only the pwrite64 loop with gettimeofday and calls close() after the timer. With LEDGER_YCSB=1 (as the README build step sets) DR_SIZE is 256 MB, so all 128 MB lands in one pre-mapped staging file and the relink that attaches it to the file happens at close, outside the timed region
- The workload is pwrite64 at increasing offsets on a file opened without O_TRUNC; the README removes the file between runs, and a stale test.txt turns the appends into overwrites
- Build-time workload switches (LEDGER_YCSB, LEDGER_TPCC and others in common.mk) change staging-file sizes and counts, so results depend on which flag the library was compiled with
- License mismatch: the LICENSE file is Apache-2.0 but the README says UT Austin holds copyright and asks commercial users to contact the authors; the kernel/ tree is GPL

## Known shortcomings

- Harness discrepancy behind the README's 5.8x: the README says fsync at the end, but micro/rw_experiment.c has no fsync and times only the pwrite64 loop. With LEDGER_YCSB=1, DR_SIZE is 256 MB, so all 128 MB goes into one pre-mapped staging file and the relink runs at close(), outside the timer. Open issues: 64 (fio multi-thread assertion), 66 (strict-mode append recovery data loss), 67 (rename crash consistency), 75 (multithreaded TPC-C fails). Tier B rests on the SOSP 2019 paper (PDF blocked).

## Caveats and trade-offs

The repository LICENSE file is Apache License 2.0 (Copyright 2019 University of Texas at Austin), but the README License section says copyright is held by UT Austin and asks commercial users to contact the authors; treat the Apache-2.0 grant as the license of record but check with the authors before commercial use. The kernel/ directory carries a patched GPL Linux 4.13 kernel (relink syscall) and the library is built on NVSL Quill. Last commit 2021-12-14. SOSP'19 paper PDF not opened (host blocked); the 5.8x and 4-12x figures are on the README page. Results were run on persistent memory (Optane or emulated), so they do not transfer to ordinary SSDs.

User-space LD_PRELOAD library on top of ext4 DAX plus a patched kernel; Ubuntu 16.04/18.04; only POSIX calls intercepted via glibc; persistent memory hardware needed.

## Maintenance

Abandoned research artifact (last commit 2021-12-14, 171 stars, several open crash and correctness issues); Apache-2.0 LICENSE file but README asks commercial users to contact UT Austin, and it is tied to Linux 4.13 and discontinued Optane hardware.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed SOSP'19 paper; README microbenchmark (micro/rw_experiment.c, gcc -O3) shows ext4-DAX 0.33M vs SplitFS 1.92M appends/sec (5.8x) and 4-12x lower software overhead than NOVA or ext4 DAX. Not A: the README run names no CPU model or compiler version for those numbers; experiments.md gives a Xeon E3-1225 v5 for the paper replication setup only.
- **Verifier notes:** LICENSE file is Apache-2.0, contradicting the record's proprietary license; README wording still asks for a commercial licence, so the orchestrator may prefer usability mixed. Last commit 2021-12-14 is more than 3 years old, so maintenance is abandoned.
- **Fields the verifier corrected:** `license`, `usability`, `maintenance_status`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** peer-reviewed paper, snippet only
- **Pages the verifier opened:**
  - <https://github.com/utsaslab/SplitFS>
  - <https://github.com/utsaslab/SplitFS/commits>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/README.md>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/experiments.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/README.md>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/experiments.md>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/micro/rw_experiment.c>
  - <https://github.com/utsaslab/SplitFS/tree/master/splitfs>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/splitfs/Makefile>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/splitfs/common.mk>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/splitfs/README>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/splitfs/ledger.h>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/splitfs/fileops_nvp.c>
  - <https://raw.githubusercontent.com/utsaslab/SplitFS/HEAD/splitfs/fileops_nvp.h>
  - <https://github.com/utsaslab/SplitFS/issues?q=is%3Aissue>
  - <https://github.com/utsaslab/SplitFS/issues/66>
  - <https://github.com/utsaslab/SplitFS/issues/64>
  - https://www.cs.utexas.edu/\~vijay/papers/sosp19-splitfs.pdf (blocked, connect_rejected)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/utsaslab/splitfs`) · [data/wave11/enrich/raw/github_com_utsaslab_splitfs.json](../../../data/wave11/enrich/raw/github_com_utsaslab_splitfs.json) (enrichment confidence 0.75)

</details>
