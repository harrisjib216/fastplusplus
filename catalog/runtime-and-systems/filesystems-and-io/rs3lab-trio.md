# Trio / ArckFS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0` · 🔴 abandoned

> SOSP '23 research userspace NVM file system (ArckFS) on Optane PM that outscales NOVA, WineFS, OdinFS and ext4-DAX at high core counts.

| | |
|---|---|
| **Beats** | NOVA, PMFS, WineFS, Strata, SplitFS, ODINFS (kernel and user-space NVM file systems; ext4 DAX) |
| **Claimed result** | LevelDB (Table 5): Fill100K 3.81 vs 1.23 and Fill sync 291 vs 17 against ext4-DAX (the abstract's 3.1x-17x is against ext4-DAX only); against WineFS, the second best, only 1.01x-2.0x (derived from Table 5) |
| **Workload** | User-space NVM file system architecture, LevelDB, Filebench, FxMark and FIO |
| **Metric** | throughput |
| **Hardware** | 8-socket 224-core Xeon Platinum 8276L, 6144 GB Optane, Linux 5.13.13 |
| **Compiler and flags** | libfs -Ofast, kfs -O3 -mtune=native (Makefiles) |
| **Adoption** | 1 star (artifact repo) |
| **Last commit** | 2023-08-24 |
| **Links** | [repository](https://github.com/rs3lab/Trio) · [benchmark](https://github.com/rs3lab/rs3lab.github.io/blob/HEAD/assets/papers/2023/zhou:trio.pdf) |

## Verdict

The SOSP '23 paper (opened via the rs3lab.github.io repo) ran on an 8-socket, 224-core Intel Xeon Platinum 8276L with 6144GB Optane PM DIMMs, Ubuntu 20.04, Linux 5.13.13: single-thread db_bench LevelDB (100-byte values, 1M objects) shows ArckFS 1.5x-17x over ext4-DAX and 1.01x-2.0x over WineFS (derived from Table 5), FIO 2MB read/write 3.1x-25x and 2.0x-15x over other file systems, and Filebench Webproxy/Varmail 2.2x-8.0x and 2.4x-34.2x with eight NUMA nodes; customized KVFS and FPFS add 1.3x and 1.2x over ArckFS. The SOSP '25 ArckFS+ follow-up reports its bug-fixed version at 97.1%-102.1% of ArckFS throughput on Webproxy and Varmail.

## Use it when

- Research or reproduction work on Intel Optane PM in devdax mode, especially many-socket machines where NVM bandwidth collapses under concurrent kernel-FS access.
- High thread counts (above about 16-56 threads in the authors' FIO runs) doing 4KB or larger file I/O, or 2MB sequential reads and writes where delegation parallelizes copies.
- Metadata-heavy small-file workloads (Webproxy, Varmail-like mail spools, many open/create/delete) where the paper reports 2.2x-34.2x over kernel PM file systems.
- Studying how to give untrusted processes direct NVM access with integrity verification, or building a customized libfs (KVFS/FPFS pattern) without kernel changes.

## Skip it when

- Any production system: Optane PM is discontinued, it needs a custom 5.13.13 kernel, and the SOSP '25 follow-up found implementation bugs causing occasional operation failures and possible crash inconsistencies during inode creation; the fixes live in a separate repo.
- Low thread counts: main-claim.md says ArckFS performs similarly to or worse than others below 56 threads (4KB, one NUMA node) or 16 threads, and with one NUMA node Fileserver/Webserver results are similar across file systems.
- Small single-threaded I/O: the paper reports ArckFS 21% slower than ArckFS without delegation on 4KB, and ArckFS-nd 21%-34% faster than ArckFS on most LevelDB workloads.
- Hosts that constantly spawn threads or processes (k8s services): thread numbering from gettid() differences can make ArckFS panic (README known issue 4).
- Apps whose libraries do file syscalls before the libfs initializes, or that rely on mmap, stdio or calls the libfs does not wrap.

## How it is fast

Direct NVM access from userspace for both data and metadata removes kernel traps and VFS overhead (the paper measures NOVA and Strata spending at least 42% and 44.5% of create time in VFS and digestion). Opportunistic delegation (from OdinFS) hands large accesses to per-NUMA-node delegation threads that stripe data across Optane nodes, avoiding Optane's collapse under many concurrent or remote accesses. Per-file DRAM indexes use hash tables and radix arrays plus BRAVO reader-writer locks for scalable metadata operations.

## Compared with alternatives

Pick Trio/ArckFS over NOVA, WineFS or SplitFS when the target is many-socket Optane hardware at high concurrency, or when untrusted processes need direct userspace NVM metadata access with integrity checks; MadFS is the simpler userspace PM option for ext4-DAX users, and on current hardware without Optane none of these apply, so look at SPDK, liburing or DAXFS instead.

## Integration

| | |
|---|---|
| **Form** | shared lib (LD_PRELOAD-style libsufs.so) plus out-of-tree kernel module |
| **Dependencies** | Intel Optane PM in devdax mode (ndctl), the bundled Linux 5.13.13 kernel, libnuma, tcmalloc_minimal, libdl; eval needs Filebench, FxMark, fio and LevelDB |
| **Minimum toolchain** | gcc with -Ofast (libfs) and -O3 -mtune=native gnu99 (kernel module); scripts target Ubuntu 20.04.4 |
| **Platforms** | x86-64 Linux 5.13.13 only, with Optane PM; VM and container setups only for functional testing |
| **Thread safety** | Multithreaded by design (per-thread TLS, BRAVO rwlocks, delegation rings), but limited to SUFS_MAX_THREADS (aborts with 'Too many threads!') and sensitive to background thread churn |
| **Drop-in for the baseline** | partial: same POSIX calls via interception, so unmodified binaries can run on the ArckFS mount, but it needs its own kernel module, kernel and mount, and the README ships pre-built fio and workloads because library init order can break interception |

## Gotchas

- entry.c resolves the passthrough chmod with dlsym(RTLD_NEXT, "chown"), so chmod on paths outside the ArckFS mount calls chown with the mode as uid and an undefined gid.
- stat interception hooks __xstat/__fxstat/__lxstat, which glibc 2.33+ no longer routes stat() through; on newer distributions stat calls may bypass the libfs.
- The setup grants everyone access with 'chmod 666 /dev/supremefs' as a documented hack, and kernel modules must be reinserted after every reboot.
- Abstract's '3.1x to 17x on LevelDB' is versus ext4-DAX only (Table 5: Fill 100K 3.81 vs 1.23 ops/ms, Fill sync 291 vs 17, derived from page data); versus WineFS, the second-best, ArckFS's Table 5 gains are 1.01x to 2.0x (Read random 144 vs 142, Delete random 494 vs 245, derived from page data), not the 'up to 3.1x' the text states.

## Known shortcomings

- A SOSP 2025 follow-up paper reports ArckFS bugs (operation failures, crash inconsistency on inode creation); no patches in the repo. Numbers here come from search snippets only (paper host blocked).
- entry.c sets orig_chmod = dlsym(RTLD_NEXT, 'chown'), so chmod outside the mount calls chown (not in the benchmark path); the __xstat hooks miss stat() on glibc 2.33+. The SOSP '25 ArckFS+ bug fixes measure at 97.1-102.1% of ArckFS, so the later-fixed cap is arguably not needed.

## Caveats and trade-offs

Numbers quoted from search-result snippets of the paper abstract, not from an opened page (paper PDF host egress-blocked). Repo README and docs/main-claim.md give only qualitative claims; main-claim.md says ArckFS performs similarly to or worse than others below 56 threads (4KB) or 16 threads in FIO small-access tests, and wins mainly at high concurrency on the 224-core machine. A SOSP '25 follow-up (Analyzing and Enhancing ArckFS, KAIST with the Trio authors) found implementation bugs causing occasional operation failures and potential crash inconsistencies during inode creation; its patches reportedly keep the performance claims, but the bug-fixed code is not in this repo (see github.com/psb0623/trio-sosp23-ae). Optane PM is discontinued hardware. Artifact repo, 1 star, last commit 2023-08-24.

Needs Optane PM and custom 5.13.13 kernel; full evaluation about 572 minutes.

## Maintenance

Abandoned artifact repo (last commit 2023-08-24, Apache-2.0) tied to discontinued Optane hardware and a 5.13.13 kernel; copyable code with full eval scripts for all baselines, but the bug-fixed ArckFS+ is in psb0623/trio-sosp23-ae and nothing here is production-ready.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** Repo is the SOSP '23 artifact (best paper) with full eval scripts for NOVA, PMFS, WineFS, Strata, SplitFS, OdinFS and ext4, and docs/main-claim.md states qualitative wins, but no numbers are on any opened repo page; the 3.1x-17x LevelDB and 1.3x figures come only from search snippets of the paper abstract (PDF host rs3lab.github.io blocked). Stays C until the paper is opened; a retier to B is likely once it is.
- **Retiered** C to B: Raised from C to B: the SOSP 2023 paper was opened from the group's repo (raw.githubusercontent.com/rs3lab/rs3lab.github.io/HEAD/assets/papers/2023/zhou:trio.pdf) and the evaluation code is public; machine 8-socket 224-core Xeon Platinum 8276L, 6144 GB Optane, Linux 5.13.13; flags from the Makefiles (libfs -Ofast, kfs -O3 -mtune=native). Claim correction: the abstract's '3.1x-17x on LevelDB' is against ext4-DAX only (Table 5: Fill100K 3.81 vs 1.23, Fill sync 291 vs 17); against WineFS, the second best, the gain is only 1.01x-2.0x (derived from Table 5), and the text's 'up to 3.1x vs WineFS' is not in the table.
- **Verifier notes:** Peer-reviewed source exists, so a paper-access retier to B is a candidate (QUEUE paper-access list). Bugs found by the SOSP '25 artifact study should be recorded as a shortcoming; per the later-fixed-code rule tier would stay capped at C anyway unless the follow-up re-measured.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `hardware`, `caveats`, `claimed_speedup`, `compiler_and_flags`, `benchmark_url`
- **Shortcomings recorded by:** snippet only; peer-reviewed paper, read from a repo copy
- **Pages the verifier opened:**
  - <https://github.com/rs3lab/Trio>
  - <https://raw.githubusercontent.com/rs3lab/Trio/HEAD/README.md>
  - <https://raw.githubusercontent.com/rs3lab/Trio/HEAD/docs/main-claim.md>
  - <https://github.com/rs3lab/Trio/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rs3lab/Trio/HEAD/README.md>
  - <https://raw.githubusercontent.com/rs3lab/Trio/HEAD/docs/main-claim.md>
  - <https://raw.githubusercontent.com/rs3lab/Trio/HEAD/docs/minimal-examples.md>
  - <https://raw.githubusercontent.com/rs3lab/Trio/HEAD/arckfs/compile.sh>
  - <https://raw.githubusercontent.com/rs3lab/Trio/master/arckfs/libfs/Makefile>
  - <https://raw.githubusercontent.com/rs3lab/Trio/master/arckfs/kfs/Makefile>
  - <https://raw.githubusercontent.com/rs3lab/Trio/master/arckfs/libfs/syscall.c>
  - <https://raw.githubusercontent.com/rs3lab/Trio/master/arckfs/libfs/delegation.c>
  - <https://raw.githubusercontent.com/rs3lab/Trio/master/arckfs/libfs/entry.c>
  - <https://github.com/psb0623/trio-sosp23-ae>
  - <https://raw.githubusercontent.com/psb0623/trio-sosp23-ae/HEAD/README.md>
  - <https://raw.githubusercontent.com/rs3lab/rs3lab.github.io/HEAD/assets/papers/2023/zhou:trio.pdf>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/rs3lab/trio`) · [data/wave11/enrich/raw/github_com_rs3lab_trio.json](../../../data/wave11/enrich/raw/github_com_rs3lab_trio.json) (enrichment confidence 0.75)

</details>
