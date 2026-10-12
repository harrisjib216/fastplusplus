# liburing_b3sum

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · 🔴 abandoned

> Demo BLAKE3 file hasher in C/C++ that reads through io_uring and beats Rust b3sum on cold-cache NVMe reads.

| | |
|---|---|
| **Beats** | official Rust b3sum (read/mmap based) and cat to /dev/null |
| **Claimed result** | 1 GiB cold cache: 0.301s (singlethread, median) vs 0.386s b3sum --no-mmap median (min 0.381s) and 0.4105s b3sum --num-threads 1 median (0.404-0.416s); cat to /dev/null 0.302s. 10 GiB: 2.899s vs cat to /dev/null 2.904s (medians). The author says it is about 25% faster than official b3sum and at NVMe line rate (about 3533 MiB/s). |
| **Workload** | Cold-cache BLAKE3 hash of a 1 GiB and a 10 GiB file on NVMe using an io_uring ring-buffer reader (O_DIRECT, queue depth 2-4, 512 KiB blocks). |
| **Metric** | throughput |
| **Hardware** | NVMe drive advertised at 3500MB/s; CPU model not stated (author mentions AMD64 with sha_ni and AVX2, no AVX512) |
| **Compiler and flags** | gcc -O3 -D_GNU_SOURCE ... -luring libblake3.a (GCC 11.2.0 for the b3sum example); Debian 12, kernel 6.1.0-9, ext4 |
| **Adoption** | 3 stars |
| **Last commit** | 2023-08-02 |
| **Links** | [repository](https://github.com/1f604/liburing_b3sum) · [benchmark](https://github.com/1f604/liburing_b3sum/blob/main/article.md) |

## Verdict

On Debian 12 (kernel 6.1.0-9, ext4, unencrypted NVMe advertised at 3500 MB/s, unnamed AMD64 CPU with AVX2 and no AVX-512), with drop_caches before each run and the median of 10 runs, the single-threaded O_DIRECT build hashed a 1 GiB random file in 0.301 s. Rust b3sum 1.4.1 took 0.386 s with --no-mmap and 0.4105 s with --num-threads 1 (about 1.28x and 1.36x, derived from page data); cat to /dev/null took 0.302 s and fio io_uring 0.3025 s, so the gain over cat is noise and the result is disk-bound.

## Use it when

- Hashing large files once each from fast NVMe on Linux, where you want disk-limited throughput and do not want to fill the page cache (single-threaded build with O_DIRECT).
- As a reference or starting point for an in-order io_uring streaming reader (checksums, parsers, uploaders) that must consume blocks sequentially.
- On machines where single-core BLAKE3 is faster than the disk; there it matches cat/fio line rate (10 GiB in 2.899 s, about 3533 MiB/s).
- Learning io_uring queue-depth and block-size tuning: the article includes BS/QD sweep tables and an instrumented build that counts requests in flight.

## Skip it when

- When the file is already in the page cache, or the CPU hashes slower than the disk reads: the C BLAKE3 has no multithreading, so Rust b3sum with multiple threads (or mmap) may win.
- When you need a maintained tool or library: 7 commits, last activity 2023-08, no tests, no packaging, hashes only one file per run (batch mode is an open enhancement issue).
- Non-Linux platforms or kernels without io_uring; the hand-written libblake3.a recipe in the README is x86-64 assembly only.
- Network or FUSE file systems where short reads can happen: the program prints 'panic: short read' and exits instead of reissuing the request.
- If you need a LICENSE file: the repo has none, only an SPDX MIT header in the source, which came from the liburing io_uring-cp.c example it modifies.

## How it is fast

A fixed ring buffer of aligned blocks, each cell in one of three states (requested, available, consumed), lets io_uring keep 2-4 sequential reads in flight while the consumer hashes completed blocks in file order with the single-threaded C BLAKE3 (AVX2/SSE dispatch). Using O_DIRECT with large blocks (512 KiB) skips the page cache copy, so on the author's machine, where hashing (about 4.26 GB/s cached) is faster than the disk (about 3.55 GB/s), the run is bound by disk speed. The multithreaded version puts the io_uring submit/complete loop and the hasher on separate threads, synchronised with atomics, and stays fast without O_DIRECT.

## Compared with alternatives

Pick this over liburing's own examples or couring when you want a small worked example of an io_uring pipeline that reads in file order with a fixed ring buffer and has published cold-cache numbers. Use liburing itself (or SPDK for kernel-bypass) for production I/O code.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | liburing (liburing-dev on Debian 12), BLAKE3 C library built into libblake3.a by hand |
| **Minimum toolchain** | gcc with -D_GNU_SOURCE for the C version; g++ with C++11 (std::thread, std::atomic) for the multithreaded version; Linux kernel with io_uring (tested on 6.1.0-9) |
| **Platforms** | Linux x86-64 as documented (the README build uses SSE2/SSE4.1/AVX2/AVX-512 .S files); other architectures not documented |
| **Thread safety** | Single-use program built on global state; the multithreaded variant uses one producer thread and one consumer thread synchronised with atomics; not reentrant |
| **Drop-in for the baseline** | partial — prints the same BLAKE3 hash as b3sum for one file, but takes eight positional arguments instead of b3sum's CLI and has no --check, no multiple-file mode and no stdin input |

## Gotchas

- Block size must be a multiple of 4 KiB (assert on ALIGNMENT); the best block size and queue depth depend on the machine (512 KiB/QD 2 with O_DIRECT here, 128 KiB/QD 20 without).
- The single-threaded build without O_DIRECT is about 25% slower (0.378 s vs 0.301 s per GiB); use the multithreaded build if you want page-cache reads.
- Any read error or short read aborts the program with exit(1); no retry, although the article explains how to add one.
- Turning on the IOSQE_IO_DRAIN, IOSQE_IO_LINK or inner-loop options makes it slower, according to the author's tables.

## Known shortcomings

- Disk-bound: 0.301 s against cat at 0.302 s, so the gain over cat is noise. No LICENSE file (source has an SPDX MIT header copied from liburing io_uring-cp.c). A short read aborts with exit(1); the single-threaded build needs O_DIRECT to be fast.

## Caveats and trade-offs

First-party blog numbers; CPU model not stated, so tier C. No license file (LICENSE 404), so reference only. The gain over cat (0.301s vs 0.302s) is within noise; the real gap is versus Rust b3sum on a cold disk. The page cache is flushed before each run, so the test is I/O-bound by design. The author reports output hashes match official b3sum.

Single-threaded variant needs O_DIRECT to be fast; hashing only, a demo program rather than a library; depends on liburing and libblake3.

## Maintenance

Abandoned since August 2023 (7 commits, 3 stars); the source carries an SPDX MIT header but the repo has no LICENSE file, so it is listed as reference-only, and it is small enough to read and re-create.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** article.md gives min/median/max over 10 runs against Rust b3sum, cat, dd and fio, with code, gcc -O3 compile lines, Debian 12 and kernel 6.1.0-9; the CPU model is never named (only 'AMD64 with sha_ni, AVX2, no AVX512'), so not A.
- **Verifier notes:** All numbers verified in article.md (table columns are min/median/max). I did not see the last commit date on the page, so I left 2023-08-02 unchanged. 3 stars confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/1f604/liburing_b3sum>
  - <https://raw.githubusercontent.com/1f604/liburing_b3sum/HEAD/article.md>
  - <https://raw.githubusercontent.com/1f604/liburing_b3sum/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/1f604/liburing_b3sum>
  - <https://github.com/1f604/liburing_b3sum/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/1f604/liburing_b3sum/HEAD/README.md>
  - <https://raw.githubusercontent.com/1f604/liburing_b3sum/HEAD/article.md>
  - <https://raw.githubusercontent.com/1f604/liburing_b3sum/HEAD/liburing_b3sum_singlethread.c>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/1f604/liburing_b3sum`) · [data/wave11/enrich/raw/github_com_1f604_liburing_b3sum.json](../../../data/wave11/enrich/raw/github_com_1f604_liburing_b3sum.json) (enrichment confidence 0.8)

</details>
