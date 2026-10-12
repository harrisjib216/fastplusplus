# liburing

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT OR LGPL-2.1-or-later` · 🟢 active

> Userspace wrapper around Linux's io_uring ring-buffer syscall interface; beats libaio and POSIX-AIO on IOPS and syscall overhead.

| | |
|---|---|
| **Beats** | libaio |
| **Claimed result** | Direct I/O (uncached NVMe): io_uring 1,417,000-1,486,000 IOPS vs linux-aio 1,322,000 IOPS (\~1.07-1.12x, derived from page data) and vs synchronous read/write 814,000 IOPS (\~1.74-1.83x, derived from page data). Buffered I/O (hot cache): io_uring 5,024,000 IOPS vs linux-aio 4,127,000 (\~1.22x, derived from page data) and vs synchronous 4,906,000 (\~1.02x, derived from page data). Optane single-CPU: io_uring 346 MB/s / 1,470us vs linux-aio 330 MB/s / 1,549us (author states \~5% faster). Author summary: 'Both io_uring and linux-aio are around twice as fast as the synchronous read interface, which in turn is twice as fast as the thread pool approach employed by posix-aio'. |
| **Workload** | fio random-read IOPS with 1KB blocks across 4 files, 8 CPUs running 72 fio jobs, iodepth=8; tested both direct I/O on NVMe (uncached) and buffered I/O with a hot page cache; a separate single-CPU 512-byte test on Intel Optane measured throughput and latency. |
| **Metric** | throughput |
| **Hardware** | 8 CPUs (exact model not stated) with NVMe storage; separate single-CPU test on Intel Optane. Kernel version and fio version not stated. |
| **Adoption** | 3.8k stars; the standard userspace helper library for Linux io_uring, used by QEMU, RocksDB, ScyllaDB/Seastar, and many other async-I/O consumers |
| **Last commit** | 2026-09-11 |
| **Links** | [repository](https://github.com/axboe/liburing) · [benchmark](https://www.scylladb.com/2020/05/05/how-io_uring-and-ebpf-will-revolutionize-programming-in-linux/) |

## Verdict

ScyllaDB (independent third party) ran fio 1KB random reads across 4 files on an 8-CPU/NVMe box, 72 jobs, iodepth=8: direct I/O gave io_uring 1.42-1.49M IOPS vs libaio 1.32M (\~7-12% faster) and sync read/write 814K (\~1.7-1.8x); hot-cache buffered I/O gave io_uring 5.02M IOPS vs libaio 4.13M (\~22% faster, where libaio degrades toward sync behavior). A separate single-CPU 512B test on Intel Optane showed io_uring at 346MB/s / 1,470us vs libaio 330MB/s / 1,549us (\~5% faster). CPU model, kernel version, fio version and compiler flags are not stated on the page.

## Use it when

- High-IOPS NVMe/direct-I/O or socket workloads on Linux 5.1+ where syscall count per operation matters (fio-style random read/write, proxies, storage engines).
- Workloads that naturally batch many concurrent I/Os per thread, so ring-based submit/reap amortizes across a batch.
- Need I/O opcodes beyond read/write/fsync — accept, connect, splice, openat, provided-buffer recv, etc. — from one interface.
- Willing to dedicate a kernel thread (SQPOLL) to shave submission syscalls for sustained high-throughput pipelines.
- Already a Linux-only codebase (QEMU, RocksDB, ScyllaDB/Seastar are existing adopters) where portability isn't a constraint.

## Skip it when

- Need portability off Linux, or must support pre-5.1 kernels / distros that disable io_uring by policy (some hardened container platforms, ChromeOS).
- Low-concurrency, latency-insensitive I/O where the \~7-12% direct-I/O / \~22% buffered-I/O gain over libaio doesn't justify the added ring-management complexity.
- Security-sensitive or multi-tenant environments wary of io_uring's kernel-side CVE history.
- Constrained memlocked rlimit environments (older kernels, small containers) where registering buffers or large rings can hit RLIMIT_MEMLOCK.
- Need to submit from multiple threads against a single ring without adding your own locking — concurrent unsynchronized submission isn't documented as safe.

## How it is fast

The submission and completion queues are ring buffers shared via mmap, so many I/O requests can be queued and many results reaped without a syscall per operation — io_uring_enter can submit a whole batch of SQEs and/or reap a batch of CQEs in one call. Optional SQPOLL mode runs a kernel-side thread that polls the SQ directly, letting the application skip io_uring_enter for submission entirely. This avoids POSIX-AIO's thread-pool dispatch overhead and cuts the per-op syscall count that libaio still pays for io_submit/io_getevents, which is what produces the reported IOPS gains (largest over POSIX-AIO, smaller over libaio).

## Compared with alternatives

no siblings catalogued yet

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none beyond the Linux kernel UAPI headers |
| **Minimum toolchain** | not documented precisely; GCC/Clang with GNU extensions (built with -D_GNU_SOURCE), built via ./configure && make |
| **Platforms** | Linux only, kernel 5.1+ (more opcodes/features on newer kernels); dedicated syscall/lib.h for x86, x86-64, aarch64, riscv64, generic fallback elsewhere |
| **Thread safety** | not documented in headers/man pages; recurring GitHub issues (e.g. #39, #604) about cross-thread use suggest a ring's SQ is not safe for concurrent unsynchronized submission — use one ring per thread or add your own locking |
| **Drop-in for the baseline** | no |

## Gotchas

- fio's io_uring engine (engines/io_uring.c) issues raw io_uring_enter syscalls directly and does not link liburing — the ScyllaDB benchmark measures the kernel io_uring interface liburing wraps, not liburing's own call overhead.
- SQPOLL and registered buffers eat into RLIMIT_MEMLOCK; a low default (\~64K) can silently cap ring/buffer registration on kernels &lt;=5.11.
- One vendored kernel header ships GPL-with-Linux-syscall-note-exception rather than the LGPL/MIT dual license covering the rest of the repo.
- CQEs can complete out of submission order; correlate them via user_data, not position.

## Caveats and trade-offs

The page benchmarks the kernel io_uring interface, not liburing itself. fio's io_uring engine (engines/io_uring.c) issues raw io_uring_enter syscalls and does not link liburing. The win is therefore attributable to the interface that liburing wraps. The canonical evidence, Jens Axboe's 'Efficient IO with io_uring' paper at kernel.dk/io_uring.pdf, could not be opened because of a TLS certificate/hostname mismatch on kernel.dk. The CPU model, kernel version, fio version and compiler flags are not stated. Gains over linux-aio are modest (\~7-12% direct I/O; \~22% buffered, where linux-aio degrades to synchronous behaviour). The larger win is over synchronous read/write and especially over thread-pool POSIX aio.

Linux-only (5.1+ kernel, more features on newer kernels); API is substantially more complex than read/write or epoll; io_uring has had a number of kernel-side CVEs, leading some distros/hardened environments (e.g. some container platforms, ChromeOS, and Google's production fleet historically) to disable or restrict it by default. One small vendored kernel header is GPL-with-Linux-syscall-note-exception rather than the LGPL/MIT dual license covering the rest of the repo.

## Maintenance

Actively maintained (latest release 2.15 per liburing.spec, commits as recently as 2026-09-11); MIT/LGPL-2.1+ dual license (one GPL-with-syscall-note kernel header excepted) and small enough to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification B, tier now B.
- **Tier reason:** ScyllaDB, an independent third party, ran fio (a well-known benchmark tool) comparing io_uring with linux-aio, sync reads and posix-aio. The workload is described precisely, but the CPU model, kernel version, fio version and flags are not given, so the result falls short of A.
- **Verifier notes:** All IOPS, MB/s and latency figures match Tables 1-2 and the Optane block on the ScyllaDB page, and the ratios are marked as derived. The license was corrected: all source files carry SPDX MIT, the README says 'dual licensed LGPL and MIT', and liburing.spec says 'LGPLv2+' (so not LGPL-2.1-only). I removed 'fio' from the list of users because fio does not use liburing.
- **Fields the verifier corrected:** `license`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** For 256 round trips of 64B through a pipe, io_uring at batch=1 took 515.97 ns per round trip, 1.79x slower than blocking write+read (288.352 ns) with the same 2.0 kernel entries. batch=256 with registered files and buffers reached 158.753 ns (1.82x faster), but going from batch=64 to 256 cut kernel entries 4x and bought nothing (200.81 vs 201.874 ns). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz with meltdown/retbleed 'Not affected', run 2026-09-03-third-party); Kernel entry measured about 100 ns (getppid 100.464 ns), which is \~70% of a pipe round trip (ceiling 3.3x) but only \~11% of a loopback TCP round trip (1833.73 ns, ceiling 1.12x). IORING_SETUP_SQPOLL removed all syscalls yet measured 1.8x slower than the same ring without it and burned an extra core (1.97 CPU-seconds per wall-second). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz with meltdown/retbleed 'Not affected', run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://www.scylladb.com/2020/05/05/how-io_uring-and-ebpf-will-revolutionize-programming-in-linux/>
  - <https://github.com/axboe/liburing>
  - <https://github.com/axboe/liburing/blob/master/README>
  - <https://github.com/axboe/liburing/blob/master/COPYING>
  - <https://github.com/axboe/liburing/blob/master/liburing.spec>
  - <https://github.com/axboe/fio/blob/master/engines/io_uring.c>
  - <https://kernel.dk/io_uring.pdf>
- **Sources the enricher read:**
  - <https://github.com/axboe/liburing>
  - <https://github.com/axboe/liburing/blob/master/README>
  - <https://github.com/axboe/liburing/blob/master/CHANGELOG>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring.7>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_submit.3>
  - <https://github.com/axboe/liburing/blob/master/man/io_uring_sqpoll.7>
  - <https://github.com/axboe/liburing/blob/master/src/include/liburing.h>
  - <https://github.com/axboe/liburing/blob/master/liburing.spec>
  - <https://github.com/axboe/liburing/blob/master/configure>
  - <https://github.com/axboe/liburing/issues?q=CVE>
  - <https://github.com/axboe/liburing/issues?q=%22not+thread+safe%22>
  - <https://www.scylladb.com/2020/05/05/how-io_uring-and-ebpf-will-revolutionize-programming-in-linux/>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/axboe/liburing`) · [data/wave0-seed/enrich/raw/github_com_axboe_liburing.json](../../../data/wave0-seed/enrich/raw/github_com_axboe_liburing.json) (enrichment confidence 0.75)

</details>
