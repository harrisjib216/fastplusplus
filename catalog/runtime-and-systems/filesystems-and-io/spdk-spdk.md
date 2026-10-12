# SPDK

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Userspace, polled-mode NVMe driver and storage stack that beats kernel io_uring/libaio on IOPS per core.

| | |
|---|---|
| **Beats** | Linux kernel io_uring and libaio block I/O (also POSIX I/O) |
| **Claimed result** | fio issue #1206 (independent user report): fio io_uring 4K randwrite iodepth 8 on one core reached 638k IOPS (2492 MiB/s) on an Intel P5800X Optane SSD while SPDK perf reached about 4000 MB/s on one core, roughly 2x per core (derived from page data). Paper claims from search snippets only, not opened: CHEOPS '23 (Ren and Trivedi) says io_uring is more than an order of magnitude less efficient than SPDK at high load (QD128, 7 devices); the record's 305 vs 171 KIOPS per core and 5 vs 13 cores figures (attributed to SYSTOR '22, Didona et al.) were not verified. |
| **Workload** | NVMe 4KB random reads with fio and SPDK perf across queue depths, comparing IOPS per core of the userspace polled-mode NVMe driver against kernel io_uring and libaio. |
| **Metric** | throughput |
| **Hardware** | Intel P5800X Optane SSD, single core (fio issue #1206); CPU model not stated |
| **Adoption** | 3.7k stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/spdk/spdk) · [benchmark](https://github.com/axboe/fio/issues/1206) |

## Verdict

The only openable numbers come from an independent fio issue (#1206) on an Intel P5800X Optane SSD, Fedora 33, kernel 5.9.16, fio 3.21. Fio io_uring 4K randwrite at iodepth 8 on one core reached 638k IOPS (2492 MiB/s), while SPDK perf reached about 4000 MB/s on one core, roughly 1.6-2x (derived from page data); no maintainer analysis or tuned io_uring settings appear in the thread. The CHEOPS '23 paper's claim that io_uring is more than an order of magnitude slower than SPDK at high load and scale is known from search snippets only (the PDF host is egress-blocked).

## Use it when

- Dedicated storage appliances or services (NVMe-oF target, vhost for VMs, custom KV/DB engines) that own whole NVMe SSDs
- Small-block (4 KB) random I/O at high queue depth where kernel per-I/O CPU cost is the bottleneck and you want maximum IOPS per core
- Low-latency devices such as Optane/P5800X-class SSDs, where software overhead dominates device latency
- Applications already built around run-to-completion, thread-per-core, message-passing designs
- Benchmarking a device's raw capability with spdk_nvme_perf (the docs say it gets up to 2.6x more IOPS/core than fio with the SPDK plugin)

## Skip it when

- You need a filesystem, page cache, or POSIX file semantics: an unbound device disappears from /dev and kernel filesystems on it are gone
- Shared or general-purpose hosts where several processes or the kernel must use the same disk
- Low or bursty load: polling burns 100% of the dedicated cores unless you use interrupt mode (PCIe and RDMA only, primary process only), which gives up part of the win
- Environments without hugepages, IOMMU/vfio access or root setup (many containers and managed clouds)
- When io_uring with polled I/O and registered buffers is already fast enough; it keeps the kernel stack and needs no device unbinding (see liburing)

## How it is fast

It is a kernel-bypass driver: the device's PCI BAR is mapped into the process, so submissions are MMIO doorbell writes and completions are polled from host memory, with no syscalls, interrupts or context switches. Each NVMe hardware queue pair belongs to one thread and has no locks or atomics, so throughput scales linearly with dedicated cores. Data moves zero-copy via DMA into hugepage-backed buffers.

## Compared with alternatives

Pick SPDK over liburing when you can own the whole NVMe device and dedicate polling cores, and per-core IOPS matters more than keeping kernel filesystems. xNVMe offers one API over both SPDK and io_uring backends if you want to switch later, and XRP keeps the kernel path but pushes lookups into BPF.

## Integration

| | |
|---|---|
| **Form** | static lib (default) or shared lib (--with-shared, libspdk.so); also standalone apps |
| **Dependencies** | DPDK (submodule or system), ISA-L and ISA-L crypto (default on), optional liburing, RDMA verbs, etc.; installed via scripts/pkgdep.sh |
| **Minimum toolchain** | C11 (-std=gnu11), C++11 for C++ parts; GCC or clang; build is ./configure && make |
| **Platforms** | Linux and FreeBSD; x86-64, aarch64, ppc64, riscv64 and loongarch build paths exist in mk/spdk.common.mk |
| **Thread safety** | A queue pair must only be used by one thread at a time (not enforced, violating it is undefined behavior); controller attach/detach/reset functions are documented as not thread safe; some getters are documented as thread safe |
| **Drop-in for the baseline** | no |

## Gotchas

- CONFIG_ARCH defaults to native, so binaries are built with -march=native and may not run on other CPUs; set the architecture explicitly for distributed builds
- Setup needs hugepages plus scripts/setup.sh to bind devices to vfio-pci (preferred with an IOMMU) or uio_pci_generic; some devices misbehave under vfio-pci and need IOMMU passthrough
- I/O buffers must be DMA-safe (allocated with spdk_dma_malloc or from hugepage memory), not ordinary malloc memory
- Blobstore/lvol had data-corruption bugs on concurrent writes and unmaps to unallocated clusters (issues #3688, #3689, closed); the raw NVMe driver path was not implicated

## Known shortcomings

- The only openable numbers are fio issue 1206 (P5800X, kernel 5.9.16: io_uring 638k IOPS against SPDK perf at about 4000 MB/s on one core); the CHEOPS '23 and SYSTOR '22 PDFs are blocked (atlarge-research.com, elib.dlr.de). CONFIG_ARCH=native is the default. Blobstore corruption bugs 3688 and 3689 are closed.

## Caveats and trade-offs

Numbers only from an independent GitHub issue and from search snippets of the CHEOPS '23 / SYSTOR '22 papers (PDFs blocked). The CHEOPS '23 artifact repo https://github.com/atlarge-research/Performance-Characterization-Storage-Stacks has benchmark scripts but no numbers, hardware or flags in its README. SPDK requires dedicating cores to polling, hugepages and unbinding the NVMe device from the kernel; per-core wins come with 100% CPU busy-polling. Repo contains submodules with their own licenses.

Kernel bypass: needs hugepages, dedicated polling cores and a device unbound from the kernel driver; no filesystem or page cache; not a drop-in for POSIX read/write.

## Maintenance

Very active (v26.09 released, v27.01 in progress, last commit 2026-10-01). BSD-3-Clause and copyable, but heavy: it is a framework with DPDK underneath, not a small library to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** No openable page carries the claimed paper numbers (CHEOPS '23 and SYSTOR '22 PDFs on atlarge-research.com and dl.acm.org are egress-blocked; the artifact repo README has no numbers). The only openable numbers are an independent fio issue (#1206: io_uring 638k IOPS 4K randwrite on one core, P5800X Optane, kernel 5.9.16, vs SPDK perf about 2x on one core), which lacks a full methodology, so C pending a paper-access retier.
- **Verifier notes:** Strong candidate for a paper-access retier to B (CHEOPS '23 PDF at atlarge-research.com/pdfs/2023-cheops-iostack.pdf; SYSTOR '22 'Understanding modern storage APIs'). License BSD-3-Clause, last commit 2026-10-01, 3.7k stars confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** snippet and fio issue
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/spdk/spdk/HEAD/README.md>
  - <https://raw.githubusercontent.com/spdk/spdk/HEAD/LICENSE>
  - <https://github.com/spdk/spdk/commits/master>
  - <https://github.com/atlarge-research/Performance-Characterization-Storage-Stacks>
  - <https://github.com/axboe/fio/issues/1206>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/spdk/spdk/master/README.md>
  - <https://raw.githubusercontent.com/spdk/spdk/master/doc/userspace.md>
  - <https://raw.githubusercontent.com/spdk/spdk/master/doc/nvme.md>
  - <https://raw.githubusercontent.com/spdk/spdk/master/doc/nvme_interrupt_mode.md>
  - <https://raw.githubusercontent.com/spdk/spdk/master/doc/system_configuration.md>
  - <https://raw.githubusercontent.com/spdk/spdk/master/doc/getting_started.md>
  - <https://raw.githubusercontent.com/spdk/spdk/master/doc/bdev.md>
  - <https://raw.githubusercontent.com/spdk/spdk/master/include/spdk/nvme.h>
  - <https://raw.githubusercontent.com/spdk/spdk/master/CHANGELOG.md>
  - <https://raw.githubusercontent.com/spdk/spdk/master/CONFIG>
  - <https://raw.githubusercontent.com/spdk/spdk/master/mk/spdk.common.mk>
  - <https://raw.githubusercontent.com/spdk/spdk/master/scripts/pkgdep.sh>
  - <https://github.com/axboe/fio/issues/1206>
  - <https://github.com/spdk/spdk/issues?q=is%3Aissue+performance>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/spdk/spdk`) · [data/wave11/enrich/raw/github_com_spdk_spdk.json](../../../data/wave11/enrich/raw/github_com_spdk_spdk.json) (enrichment confidence 0.7)

</details>
