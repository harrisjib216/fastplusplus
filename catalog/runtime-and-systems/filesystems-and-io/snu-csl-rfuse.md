# RFUSE

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0` · 🟢 active

> FAST '24 research FUSE replacement: per-core shared-memory ring channels and hybrid polling; about 2.27x FUSE random-read throughput (paper snippet).

| | |
|---|---|
| **Beats** | FUSE (libfuse kernel-userspace channel) |
| **Claimed result** | Paper (FAST '24), per search snippet only: 2.27x higher throughput than FUSE in random read benchmarks, parity with Ext4 in sequential I/O. The 6.46x user-space time figure was not seen in any opened source. |
| **Workload** | Userspace file system framework with per-core ring channels, evaluated with fio, FxMark, Filebench, NullFS and StackFS |
| **Metric** | throughput |
| **Hardware** | 2-socket x86_64, 40 cores per socket, 256 GB RAM, PCIe 4.0 NVMe SSD, Linux 5.15.0 (artifact README) |
| **Adoption** | 76 stars |
| **Last commit** | 2025-05-08 |
| **Links** | [repository](https://github.com/snu-csl/rfuse) · [benchmark](https://github.com/snu-csl/rfuse) |

## Verdict

Per a search snippet of the FAST '24 paper (usenix.org PDF blocked here), RFUSE with StackFS on a 2-socket 80-core machine with a PCIe 4.0 NVMe SSD and Linux 5.15.0 reached 2.27x the random-read throughput of stock FUSE, with sequential I/O at parity with ext4. The repo's claims.md states the expected trends (RFUSE beats FUSE on random fio, scale_fio, FxMark and Filebench, near ext4) but contains no numbers.

## Use it when

- Research or reproduction of FUSE-overhead work on a Linux 5.15 test machine you control (kernel rebuild and module swap are acceptable).
- Many-core boxes (the artifact ran on 80 cores) with fast NVMe where stock FUSE's single queue limits random-I/O or metadata scalability.
- Benchmarking an existing libfuse 3 filesystem against a faster transport without porting it, since the FUSE API is kept unchanged.
- Pass-through or stackable filesystems (StackFS-like) where random reads and metadata ops dominate.

## Skip it when

- Production systems or distro kernels: it needs a patched 5.15.0 kernel build and replaces the in-tree fuse module; users report 'Invalid module format' and build errors (issues #1, #3).
- Sequential I/O: the artifact's own claims say FUSE, RFUSE and ext4 perform similarly there because of the page cache.
- Small machines: the authors note results may differ on fewer cores and older PCIe; the ring count is a compile-time constant (80 by default).
- Unprivileged or containerized deployments where loading a custom kernel module is not allowed.
- Comparisons with newer upstream mechanisms (FUSE passthrough, FUSE over io_uring in Linux 6.14+): none are made in the repo.

## How it is fast

Per-core ring channels (io_uring-style submission/completion rings, RFUSE_NUM_IQUEUE of them) remove the single global request queue and its lock contention, and avoid inter-NUMA traffic for metadata-heavy parallel work. Hybrid polling cuts context switches and wake-ups: in rfuse_comp.c the kernel side checks for completion and calls schedule() in a loop for up to RFUSE_COMP_MAX_IDLE = 50 us before it sleeps, which pays off for short metadata operations. Shared-memory rings also cut request copying between kernel and user space.

## Compared with alternatives

No catalogued sibling accelerates FUSE itself: pick RFUSE when the filesystem must stay a FUSE daemon, and liburing or SPDK when you control the I/O path directly instead of going through a userspace filesystem.

## Integration

| | |
|---|---|
| **Form** | kernel module + shared lib |
| **Dependencies** | patched Linux 5.15.0 kernel (included), librfuse (libfuse 3.10.5 fork, meson/ninja), build-essential, kernel-package and related packages per README |
| **Minimum toolchain** | Linux 5.15.0, meson &gt;= 0.42, GCC toolchain able to build the 5.15 kernel |
| **Platforms** | Linux x86_64 (tested on Ubuntu 20.04.5, 2x40-core CPUs, PCIe 4.0 NVMe) |
| **Thread safety** | Kernel side uses per-ring spinlocks; daemon threading follows libfuse multithreaded loop semantics (not separately documented). |
| **Drop-in for the baseline** | partial — source-compatible for FUSE filesystems (same API), but requires swapping the kernel module and library, a specific kernel version, and a per-machine RFUSE_NUM_IQUEUE edit |

## Gotchas

- RFUSE_NUM_IQUEUE must be edited by hand in both lib/librfuse/include/rfuse.h and driver/rfuse/rfuse.h to match the core count before building.
- The RFUSE driver builds as fuse.ko, so it replaces stock FUSE on the machine rather than running beside it.
- Hybrid polling spins (schedule() loop) for up to 50 us per request before sleeping, trading CPU time for latency.
- Latency-breakdown numbers (Figures 2 and 7) need debug builds with -DDEBUG timestamp printk, so do not benchmark throughput with those builds.

## Known shortcomings

- The 2.27x random-read figure is from a search snippet only (usenix.org paper blocked); claims.md gives trends without numbers. Builds as fuse.ko and replaces stock FUSE. The hybrid poll spins for up to 50 us (RFUSE_COMP_MAX_IDLE).

## Caveats and trade-offs

Numbers come from a search-result snippet of the FAST '24 paper (usenix.org/system/files/fast24-cho.pdf is egress-blocked); the repo README has no numbers. Needs a patched Linux 5.15.0 kernel and kernel driver; RFUSE_NUM_IQUEUE must be set to the machine's core count before building. Baseline is stock FUSE, not a listed baseline. Retier candidate to B once the paper is reachable.

Needs patched Linux 5.15 kernel and librfuse; per-core config.

## Maintenance

Research artifact with occasional maintenance (last commit 2025-05-08, all four issues closed by Dec 2024), GPL-2.0 kernel code; usable for experiments, not as a maintained production FUSE replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The artifact repo has the benchmark scripts (bench/, fio, FxMark, Filebench, NullFS/StackFS) and generic hardware but no numbers. The FAST '24 paper (peer-reviewed, would support B) is on usenix.org, which is egress-blocked; only a search snippet confirms the 2.27x random-read throughput gain over FUSE, so C until the paper is read.
- **Verifier notes:** GPL-2.0 LICENSE, 76 stars, 17 forks, last commit 2025-05-08 (active), confirmed on github.com. Paper PDF at https://www.usenix.org/system/files/fast24-cho.pdf is blocked here; a retier check from an environment with usenix.org access could raise it to B.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/snu-csl/rfuse>
  - <https://github.com/snu-csl/rfuse/commits>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/README.md>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/snu-csl/rfuse>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/README.md>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/bench/claims.md>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/driver/rfuse/rfuse.h>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/driver/rfuse/rfuse_dev.c>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/driver/rfuse/rfuse_comp.c>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/driver/rfuse/rfuse_comp.h>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/driver/rfuse/Makefile>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/lib/librfuse/meson.build>
  - <https://raw.githubusercontent.com/snu-csl/rfuse/HEAD/lib/librfuse/include/rfuse.h>
  - <https://github.com/snu-csl/rfuse/tree/master/driver/rfuse>
  - <https://github.com/snu-csl/rfuse/issues?q=is%3Aissue>
  - https://www.usenix.org/system/files/fast24-cho.pdf (blocked, 403; search snippets only)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/snu-csl/rfuse`) · [data/wave11/enrich/raw/github_com_snu_csl_rfuse.json](../../../data/wave11/enrich/raw/github_com_snu_csl_rfuse.json) (enrichment confidence 0.6)

</details>
