# wcp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Experimental io_uring recursive file copier for Linux, about 2-3x faster than GNU cp -r on the author's NVMe box.

| | |
|---|---|
| **Beats** | GNU cp (cp -r); rsync also shown |
| **Claimed result** | 20x512MiB: wcp 3.97s (2579.59 MiB/s) vs cp -r 8.44s (1213.38 MiB/s); 7000x1MiB: 2.64s vs 8.29s; 200000x1KiB: 3.92s vs 9.23s (rsync 8.09s). The README headline says 'up to 70% faster than cp', which understates its own table (about 2.1-3.1x, derived from page data). |
| **Workload** | Copying 20 files of 512MiB, 7,000 files of 1MiB and 200,000 files of 1KiB on NVMe |
| **Metric** | throughput |
| **Hardware** | 64GB RAM, Samsung NVMe SSD (CPU model not stated) |
| **Compiler and flags** | CMake -DCMAKE_BUILD_TYPE=Release (compiler not stated) |
| **Adoption** | 222 stars |
| **Last commit** | 2021-05-21 |
| **Links** | [repository](https://github.com/wheybags/wcp) · [benchmark](https://github.com/wheybags/wcp) |

## Verdict

On the author's machine (64 GB RAM, Samsung NVMe SSD, Linux 5.8, CPU and compiler not stated, CMake Release build), wcp copied 20 x 512 MiB files in 3.97 s vs 8.44 s for cp -r, 7,000 x 1 MiB files in 2.64 s vs 8.29 s, and 200,000 x 1 KiB files in 3.92 s vs 9.23 s (rsync 8.09 s). There is no benchmark script, the page-cache state is not stated, and an independent user (issue #13) saw it slower than cp.

## Use it when

- Bulk copies of many small files (thousands to hundreds of thousands of 1 KiB-1 MiB files) on a fast NVMe SSD under Linux 5.6+, where cp's per-file synchronous syscalls dominate
- Large sequential copies (hundreds of MiB per file) where the author measured about 2.1x cp's throughput
- One-off interactive copies where an accurate progress bar and ETA matter
- As reference code for an io_uring copy pipeline (linked read/write SQEs, O_DIRECT alignment handling) to build into your own tool

## Skip it when

- Anything needing cp's options: no -p/-a, so ownership, timestamps and xattrs are not preserved, and there are no flags at all
- Production or scripted use: the author says it is probably not robust enough for daily use, issue #14 (named pipes break it) is open, and earlier issues reported segfaults and SIGTRAP
- Non-Linux systems, kernels older than 5.6, or older distributions (open build failures on CentOS 7.4 and Debian, issues #12 and #10)
- Memory-constrained machines: it allocates at least 1 GiB (10% of physical RAM) of copy buffers up front
- Other hardware: open issue #13 reports wcp slower than cp on Ubuntu 20.04.1 AMD64

## How it is fast

All reads and writes go through io_uring (bundled liburing) as linked read-then-write submissions (IOSQE_IO_LINK), so many files are in flight at once without a syscall per operation, and directory walking runs alongside the copying. Source files are opened with O_DIRECT, which bypasses the page cache on reads, into one large aligned buffer pool of max(RAM/10, 1 GiB) split into 128 MiB blocks. The author's own summary is 'a lot of CPU, as much RAM as I can get away with, and 100% non-portable'.

## Compared with alternatives

liburing is the io_uring library wcp is built on; pick wcp when you want a ready-made copier, and liburing when you are building your own I/O path. parallel-disk-usage is the same kind of parallel tree-walk speedup applied to du, not to copying.

## Integration

| | |
|---|---|
| **Form** | CLI tool (CMake build; also a wcp_lib static library) |
| **Dependencies** | liburing (vendored), pthreads |
| **Minimum toolchain** | C++17 (the record's language field says C, but the code is C++17), CMake 3.11+, Linux kernel 5.6+ (tested on 5.8) |
| **Platforms** | Linux only (x86-64; ARM build fixed in issue #9) |
| **Thread safety** | not applicable (standalone process); not documented for wcp_lib |
| **Drop-in for the baseline** | partial: it covers `cp -r SRC DEST` for one source with default semantics only, with no options |

## Gotchas

- No fsync anywhere in the source: destination writes are buffered, so timings with 64 GB RAM partly measure filling the page cache (cp -r does not fsync either); the README does not say whether caches were dropped between runs, and wcp's O_DIRECT reads skip a warm source cache that cp could use
- The 200,000 x 1 KiB row reports 200.51 MiB/s, but 200,000 KiB in 3.92 s is about 49.8 MiB/s (derived from page data); the files/s and seconds columns agree with each other, so the MiB/s column for small files looks inflated, probably by counting padded O_DIRECT block sizes
- The README headline 'up to 70% faster' understates its own table (2.1-3.1x on wall time, derived from page data)
- Errors in source files (FIFOs, unreadable files) are reported but can stop the status display (issue #14)

## Known shortcomings

- The code is C++17, not C. No fsync anywhere: source reads use O_DIRECT while destination writes go to the page cache, with the cache state unstated. The 1 KiB row's MiB/s is inflated about 4x (200.51 stated against 49.8 derived from page data); the seconds column is consistent, so it is a reporting artifact, not a copy bug. Open issue 13 (slower than cp on Ubuntu 20.04.1) and 14 (named pipes break it); uses a minimum 1 GiB buffer.

## Caveats and trade-offs

First-party numbers with no benchmark script; CPU and compiler not stated. Linux-only, using io_uring on kernel 5.6 or later. The author says it is probably not robust enough for daily use. Last commit 2021-05-21.

Experimental tool, Linux only (io_uring); not a full cp replacement.

## Maintenance

Abandoned since 2021-05-21 (issues from 2021-2024 left open) but MIT-licensed and about 1,500 lines of C++, so small enough to read or vendor as a reference io_uring copy pipeline.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table compares wcp against cp -r and rsync on the author's machine, and the record's numbers match it exactly. The numbers are first-party; there is no benchmark script, and the CPU, compiler and flags are not stated (the build uses CMake Release).
- **Verifier notes:** Metadata checked on github.com: MIT, 222 stars, not a fork, last commit 2021-05-21, so abandoned is correct. The README file is readme.md in lowercase.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/wheybags/wcp>
  - <https://github.com/wheybags/wcp/commits>
  - <https://raw.githubusercontent.com/wheybags/wcp/HEAD/readme.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/wheybags/wcp/HEAD/readme.md>
  - <https://github.com/wheybags/wcp>
  - <https://github.com/wheybags/wcp/tree/master/src>
  - <https://github.com/wheybags/wcp/issues?q=is%3Aissue>
  - <https://github.com/wheybags/wcp/issues/13>
  - <https://raw.githubusercontent.com/wheybags/wcp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/wheybags/wcp/HEAD/src/wcpMain.cpp>
  - <https://raw.githubusercontent.com/wheybags/wcp/HEAD/src/CopyQueue.cpp>
  - <https://raw.githubusercontent.com/wheybags/wcp/HEAD/src/CopyRunner.cpp>
  - <https://raw.githubusercontent.com/wheybags/wcp/HEAD/src/Heap.cpp>
  - <https://raw.githubusercontent.com/wheybags/wcp/HEAD/src/Config.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/wheybags/wcp`) · [data/wave11/enrich/raw/github_com_wheybags_wcp.json](../../../data/wave11/enrich/raw/github_com_wheybags_wcp.json) (enrichment confidence 0.75)

</details>
