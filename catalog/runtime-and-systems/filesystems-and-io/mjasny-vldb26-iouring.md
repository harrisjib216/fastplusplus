# vldb26-iouring (io_uring for DBMSs artifact)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · 🟢 active

> VLDB'26 artifact measuring which io_uring settings speed up DBMS buffer managers and network shuffles compared with default io_uring and epoll.

| | |
|---|---|
| **Beats** | io_uring default configuration, epoll, pread/libaio style I/O in a DBMS |
| **Claimed result** | Paper (search snippets only): zero-copy with registered buffers up to 3.5x fewer cycles per transmitted byte than default io_uring for large messages; zero-copy send/receive about 2.5x over epoll for network shuffling with large tuples; zero-copy with registered buffers about 11% higher YCSB throughput (238k tx/s); applying the guidelines to PostgreSQL's io_uring integration gave 14% |
| **Workload** | VLDB'26 study of io_uring in DBMS buffer managers and network shuffle: registered buffers, SQPOLL, zero-copy send and receive, PostgreSQL patch |
| **Metric** | throughput / CPU cycles |
| **Hardware** | AMD EPYC 9654P (96 cores), 768 GiB DDR5, 8x KIOXIA PCIe Gen 5 SSDs, 400 Gbit ConnectX-7; kernels 6.15 and 6.17 |
| **Compiler and flags** | GCC 13.3.0, glibc 2.39, Ubuntu 24.04 (README); CMakeLists.txt Release build: -O3 -flto plus -march=native -mavx512f -mavx512bw |
| **Adoption** | 19 stars |
| **Last commit** | 2026-03-31 |
| **Links** | [repository](https://github.com/mjasny/vldb26-iouring) · [benchmark](https://github.com/mjasny/vldb26-iouring) |

## Verdict

According to search snippets of the PVLDB'26 paper (PDF blocked here), on an AMD EPYC 9654P with 8 PCIe Gen 5 SSDs and 400 Gbit NICs, built with GCC 13.3.0 at -O3 -flto -march=native, zero-copy with registered buffers cut cycles per byte up to 3.5x against default io_uring for large messages, zero-copy shuffling was about 2.5x faster than epoll for large tuples, YCSB throughput rose about 11% (238k tx/s), and the guidelines gave PostgreSQL's io_uring path 14%. None of these numbers are in the repository README.

## Use it when

- You are designing or tuning io_uring in a storage engine or buffer manager and want measured guidance on which setup flags (SQPOLL, IOPOLL, COOP_TASKRUN, fixed buffers and files) pay off
- I/O-bound OLTP where many reads miss the buffer pool (YCSB, TPC-C with SSD page loads and evictions); the paper reports the largest gains here
- Network-bound shuffles with large tuples, where the snippets report zero-copy send/receive at about 2.5x over epoll
- You want a ready-made PostgreSQL 18-era AIO patch showing fixed buffers plus SQPOLL in method_io_uring.c (the snippets report 14% on PostgreSQL)

## Skip it when

- Mostly in-memory, compute-bound workloads: the paper says the I/O path contributes little there and the optimizations have correspondingly small effect
- You need a reusable library: this is study code with no API, no license file and two commits, so it can be read for reference but not copied
- Stock distro kernels: experiments ran on kernels 6.15 and 6.17 built from source, with zero-copy receive bug fixes at a pinned for-next commit, and zero-copy receive needs NIC support (ConnectX-7 here)
- CPU-constrained hosts: SQPOLL and IOPOLL spend dedicated cores polling to save syscalls and interrupts
- Machines without AVX-512: CMakeLists.txt hard-codes -march=native -mavx512f -mavx512bw

## How it is fast

The gains come from io_uring features that remove per-I/O kernel work: registered (fixed) buffers that skip page pinning and enable zero-copy DMA, registered file descriptors, SQPOLL kernel submission threads (optionally shared via IORING_SETUP_ATTACH_WQ), IOPOLL completion polling, COOP_TASKRUN, and zero-copy send and multishot or zero-copy receive for networking. The PostgreSQL patch registers the whole shared buffer pool (BufferBlocks, NBuffers\*BLCKSZ) with io_uring_register_buffers, uses read_fixed/readv_fixed with sparse fixed-file slots, and runs a shared SQPOLL thread with sq_thread_idle=100. According to search snippets of the paper (the PDF was blocked), the guidelines are registered buffers for payloads above about 1 KiB, passthrough I/O for device-specific workloads, and multishot receive for messages under 1 KiB.

## Compared with alternatives

Use liburing as the library; read this artifact to decide which liburing features to turn on for a DBMS. Unlike SPDK or XRP it keeps the kernel I/O path and gives configuration guidance rather than replacing the I/O stack.

## Integration

| | |
|---|---|
| **Form** | source-drop (benchmark harness plus PostgreSQL patch; reference only) |
| **Dependencies** | liburing (submodule), Boost 1.89 fiber (FetchContent), vmcache, distexprunner, fio, PostgreSQL source tree, Nix for the experiment environment, R for plots |
| **Minimum toolchain** | C++23 with -fcoroutines, GCC 13.3.0, CMake 3.20, Linux 6.15+ |
| **Platforms** | Linux x86-64 with AVX-512; tested on AMD EPYC 9654P with 400 Gbit ConnectX-7 and PCIe Gen 5 SSDs |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The PostgreSQL patch selects its io_uring mode at compile time (uring_config.h RUN_MODE 6: SQPOLL with a shared SQ thread, fixed fds and fixed buffers, no IOPOLL), not through a GUC; it also force-defines IOMETHOD_IO_URING_ENABLED and IORING_SETUP_NO_MMAP in aio.h even when configure did not detect liburing
- The patch is mostly clang-format reflow of PostgreSQL's files (about 4,200 lines), so the functional changes are hard to pick out; its register-buffers error message prints ret instead of rc
- The patch loosens PostgreSQL's submit check from ret != num_staged_ios to ret &lt; num_staged_ios because the strict check fails under SQPOLL
- The second set(CMAKE_CXX_FLAGS ...) overwrites the first, so -Wall -Wextra are silently dropped; Release adds -O3 -flto and the build always adds -g

## Known shortcomings

- Paper numbers are snippet only (arXiv and mirrors blocked); registered buffers help above 1 KiB and multishot recv below 1 KiB. The PostgreSQL patch hard-codes RUN_MODE 6 (shared SQPOLL, fixed buffers and files) at compile time, force-enables io_uring in aio.h and loosens the submit check for SQPOLL. AVX-512 is hard-coded; no license.

## Caveats and trade-offs

This is a study artifact (benchmark harness, a PostgreSQL patch, vmcache and fio submodules), not a reusable library; its result is guidance on configuring io_uring (registered buffers, SQPOLL, zero-copy) against epoll and default io_uring. The paper PDF is egress-blocked here (TU Darmstadt, arXiv, ResearchGate), so the numbers come from search-result snippets. The record had the 2.5x zero-copy receive figure against default io_uring; the snippet says against epoll. No license file in the repository (LICENSE, LICENSE.md, LICENSE.txt and COPYING all 404), so the code is reference only. Two commits (2025-12-01 submission, 2026-03-31 revision). Kernels 6.15 and 6.17 built from source, with zero-copy receive bug fixes at a pinned commit.

Benchmarks and a PostgreSQL patch rather than a reusable library; needs recent kernels and Nix environment.

## Maintenance

Paper artifact with two commits (last 2026-03-31) and no license file, so it is reference only; useful as a reading guide to io_uring tuning, not as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** VLDB'26 peer-reviewed study with a public artifact (src/, experiments/, CMakeLists.txt Release -O3 -flto -march=native, GCC 13.3.0, AMD EPYC 9654P), so it is A-eligible on methodology, but the paper with the numbers could not be opened (TU Darmstadt, arXiv and ResearchGate all blocked) and the README carries no results, so it stays at B.
- **Verifier notes:** Could upgrade to A once someone opens the paper and ties the numbers to this harness; methodology (code, GCC 13.3.0, -O3 -flto -march=native, EPYC 9654P) is complete. Baseline is configuration-level (default io_uring, epoll), not a competing library.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** snippet only
- **Pages the verifier opened:**
  - <https://github.com/mjasny/vldb26-iouring>
  - <https://github.com/mjasny/vldb26-iouring/commits>
  - <https://raw.githubusercontent.com/mjasny/vldb26-iouring/HEAD/README.md>
  - <https://raw.githubusercontent.com/mjasny/vldb26-iouring/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mjasny/vldb26-iouring/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/mjasny/vldb26-iouring>
  - <https://github.com/mjasny/vldb26-iouring/tree/master/src>
  - <https://raw.githubusercontent.com/mjasny/vldb26-iouring/HEAD/README.md>
  - <https://raw.githubusercontent.com/mjasny/vldb26-iouring/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mjasny/vldb26-iouring/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/mjasny/vldb26-iouring/HEAD/0001-uring-opts.patch>
  - <https://raw.githubusercontent.com/mjasny/vldb26-iouring/HEAD/src/bench_buf_reg.cpp>
  - <https://raw.githubusercontent.com/mjasny/vldb26-iouring/HEAD/src/CMakeLists.txt>
  - WebSearch: High-Performance DBMSs with io_uring (snippets of arxiv.org/abs/2512.04859, TU Darmstadt PDF, emergentmind; pages themselves EGRESS_BLOCKED)
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/mjasny/vldb26-iouring`) · [data/wave11/enrich/raw/github_com_mjasny_vldb26_iouring.json](../../../data/wave11/enrich/raw/github_com_mjasny_vldb26_iouring.json) (enrichment confidence 0.6)

</details>
