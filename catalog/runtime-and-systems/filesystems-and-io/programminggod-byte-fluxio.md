# FluxIO

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 io_uring (SQPOLL, fixed files and buffers) O_DIRECT block I/O engine; out-runs Boost.Asio file I/O and Go on 4 KiB writes.

| | |
|---|---|
| **Beats** | Boost.Asio C++20 file I/O and Go os.O_DIRECT with goroutines (not POSIX pread/pwrite) |
| **Claimed result** | Peak IOPS (4KiB O_DIRECT): sequential write 715,827.6 vs Go 239,383.5 and Boost.Asio 86,783.1 (2.99x, 8.25x); random write 542,998.1 vs 248,800.8 and 86,821.4 (2.18x, 6.25x); random read 434,377.9 vs 308,629.1 and 22,192.8 (1.41x, 19.57x); sequential read 278,054.8 vs Go 302,860.5 (0.92x) and Asio 43,625.2. QD128 random write with FileBlockManager 429,229.3 IOPS vs Go 29,074.7 and Asio 28,411.3 on unmanaged sparse files. |
| **Workload** | 4KiB O_DIRECT sequential/random read and write at queue depths 1-128 on a physical consumer NVMe SSD, io_uring with SQPOLL and fixed buffers. |
| **Metric** | throughput |
| **Hardware** | Consumer NVMe SSD, Core 2 affinity pinned; CPU model not stated |
| **Compiler and flags** | g++ -std=c++20 -O3 -luring (build line; benchmark flags not separately stated) |
| **Adoption** | 6 stars |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/programmingGod-byte/FluxIO) · [benchmark](https://github.com/programmingGod-byte/FluxIO) |

## Verdict

First-party runs of benchmark/bench_fluxio.cpp (4 KiB O_DIRECT, 20,000-50,000 ops per point, QD 1-128, 256 MB file, thread pinned to core 2, consumer NVMe, CPU model not stated) peak at 715,827.6 IOPS sequential and 542,998.1 random write vs Go os.O_DIRECT with goroutines (239,383.5 and 248,800.8) and Boost.Asio C++20 file I/O (86,783.1 and 86,821.4), using about 200% CPU vs about 100%. The Go and Asio harnesses are not in the repo, and the sparse-file QD128 comparison quotes FluxIO's QD16 result.

## Use it when

- Linux NVMe workloads issuing many independent 4 KiB O_DIRECT reads or writes at queue depth 4-128 from one thread, e.g. a storage engine, log or block cache.
- When you can spare a second core for the SQPOLL kernel thread in exchange for higher IOPS from a single submitting thread.
- Write-heavy streams into preallocated files, where it measured about 0.5-0.7 M IOPS (sequential and random 4 KiB writes) on a consumer NVMe drive.
- As a compact, readable example of SQPOLL plus fixed files and buffers to copy into your own engine (MIT, a few headers).

## Skip it when

- Sequential reads: it measured 278,054.8 IOPS vs Go's 302,860.5 (0.92x), and IOPS per core is roughly on par with Go once the SQPOLL thread is counted (README).
- Requests larger than the page size (default 4096 B): each request must fit one registered buffer, so larger I/O must be split by the caller.
- Non-Linux, buffered or non-x86 environments: io_uring and O_DIRECT only, and the code calls __builtin_ia32_rdtsc directly for timestamps.
- Multi-threaded submission: rings are single-producer/single-consumer and the engine holds no locks.
- Production use without your own testing: 9 commits in under a week (2026-09-30 to 2026-10-04), no CVE or issue history, and the benchmark harness does not check per-I/O results.

## How it is fast

It sets up io_uring with IORING_SETUP_SQPOLL so a kernel thread polls the submission queue (no io_uring_enter per batch while it is awake), registers the file descriptors (IOSQE_FIXED_FILE) and a pool of page-aligned buffers (io_uring_register_buffers, read_fixed/write_fixed) so the kernel skips per-I/O fd lookup and page pinning. Free buffer slots come from a 128-bit bitmask allocated with ctz, and request/completion queues are cache-line-aligned SPSC rings. FileBlockManager fallocate()s 10 MB chunks with FALLOC_FL_KEEP_SIZE ahead of the write frontier (80% watermark) to cut extent allocation on sparse files.

## Compared with alternatives

Pick it over raw liburing when you want SQPOLL, fixed files and buffers, slot management and fallocate-ahead already wired up for 4 KiB O_DIRECT blocks; pick liburing itself (or SPDK for full userspace NVMe) when you need arbitrary request sizes, multiple threads, or measured, mature behavior.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | liburing (optional; without it the POSIX pread/pwrite backend is used), pthread; pybind11 only for the Python module |
| **Minimum toolchain** | C++20 (concepts, &lt;bit&gt;); README builds with g++ -std=c++20 -O3 |
| **Platforms** | Linux only; io_uring backend effectively x86-64 (direct __builtin_ia32_rdtsc and pause calls); SQPOLL may need root or CAP_SYS_NICE on older kernels (README runs the benchmark with sudo) |
| **Thread safety** | single-threaded per engine: lock-free SPSC submission and completion rings, one producer and one consumer |
| **Drop-in for the baseline** | no |

## Gotchas

- The README headline 'QD128 random write with FileBlockManager 429,229.3 IOPS vs Go 29,074.7 and Asio 28,411.3' uses FluxIO's QD16 row: its own Mode 2 table shows 28,335.9 IOPS at QD128 (and 16,816.5 at QD64), the same as the Go and Asio sparse-file numbers, so the claimed fix for the ext4 inode-lock collapse is not supported at QD128.
- bench_fluxio.cpp counts every completion as a finished op and never checks comp.failed or comp.result, so failed or short I/Os would still inflate IOPS; register_file silently reopens without O_DIRECT if the filesystem returns EINVAL, which would turn the run into page-cache I/O.
- io_uring register_file() only opens files that already exist (it never passes O_CREAT on a missing path) and a failed open hits FLUXIO_SAFE_CHECK, which calls abort(); the POSIX backend does create the file.
- Writes are memcpy'd into the registered buffer and reads are copied out of it on completion, so 'fixed buffers' does not mean zero-copy for the caller; the SQPOLL thread spins for 2000 ms after each burst (sq_thread_idle).

## Known shortcomings

- README harness flaw: the headline 'QD128 FileBlockManager 429,229.3 IOPS vs Go 29,074.7 and Asio 28,411.3' is FluxIO's QD16 row; its own Mode 2 at QD128 is 28,335.9 IOPS, the same as the baselines. bench_fluxio.cpp never checks comp.failed or the result, and register_file silently drops O_DIRECT on EINVAL.

## Caveats and trade-offs

Baselines are Boost.Asio C++20 file I/O and Go, not POSIX pread/pwrite or plain liburing; Go and Asio benchmark sources are not in the repo; FluxIO uses \~200% CPU (SQPOLL kernel thread) vs \~100% for Go/Asio and the README says IOPS per core is roughly on par with Go; sequential read is slower than Go (0.92x); the QD128 sparse-write comparison pits FluxIO's preallocation against unpreallocated baselines. First-party, no CPU model. Very young repo (9 commits, 2026-09-30 to 2026-10-04). [retier] The README 'QD128 429,229.3 IOPS' headline is the QD16 row; FluxIO's own Mode 2 at QD128 is 28,335.9 IOPS, equal to the Go and Asio baselines; bench_fluxio.cpp never checks comp.failed or the result; register_file silently drops O_DIRECT on EINVAL; Go and Boost.Asio harnesses are not in the repo; uses about 200% CPU.

Uses a kernel SQPOLL thread plus a busy-poll user thread (about 200% CPU); Linux only; needs liburing; O_DIRECT only.

## Maintenance

Active but brand new (9 commits, 2026-09-30 to 2026-10-04, 6 stars, no issues); MIT and small enough to vendor, but treat it as a reference design rather than a hardened dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README 'Language & Framework Comparison' table gives FluxIO vs Go os.O_DIRECT vs Boost.Asio IOPS; only benchmark/bench_fluxio.cpp is in the repo (Go and Asio harnesses absent), no CPU model, so first-party C.
- **Verifier notes:** Numbers match README. MIT license file present; 6 stars; not a fork (WebFetch reported '1 fork', meaning forked by others). Last commit 2026-10-04 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/programmingGod-byte/FluxIO>
  - <https://github.com/programmingGod-byte/FluxIO/commits>
  - <https://raw.githubusercontent.com/programmingGod-byte/FluxIO/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/programmingGod-byte/FluxIO>
  - <https://raw.githubusercontent.com/programmingGod-byte/FluxIO/HEAD/README.md>
  - <https://raw.githubusercontent.com/programmingGod-byte/FluxIO/HEAD/benchmark/bench_fluxio.cpp>
  - <https://raw.githubusercontent.com/programmingGod-byte/FluxIO/HEAD/include/fluxio/backend/io_uring_backend.h>
  - <https://raw.githubusercontent.com/programmingGod-byte/FluxIO/HEAD/include/fluxio/backend/file_state.h>
  - <https://raw.githubusercontent.com/programmingGod-byte/FluxIO/HEAD/include/fluxio/backend/fileBlockManager.h>
  - <https://raw.githubusercontent.com/programmingGod-byte/FluxIO/HEAD/include/fluxio/backend/posix_backend.h>
  - <https://raw.githubusercontent.com/programmingGod-byte/FluxIO/HEAD/include/fluxio/util/fluxio_macros.h>
  - <https://raw.githubusercontent.com/programmingGod-byte/FluxIO/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/programminggod-byte/fluxio`) · [data/wave11/enrich/raw/github_com_programminggod_byte_fluxio.json](../../../data/wave11/enrich/raw/github_com_programminggod_byte_fluxio.json) (enrichment confidence 0.7)

</details>
