# MadFS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · 🔴 abandoned

> LD_PRELOAD userspace persistent-memory file layer over ext4-DAX; FAST '23 reports up to 3.6x ext4-DAX concurrent throughput.

| | |
|---|---|
| **Beats** | ext4-DAX and NOVA persistent-memory filesystems (POSIX file API) |
| **Claimed result** | Up to 3.6x throughput versus ext4-DAX on concurrent workloads; 48% speedup for YCSB on LevelDB and 85% for TPC-C on SQLite versus NOVA |
| **Workload** | Userspace persistent-memory filesystem; concurrent file workloads, YCSB on LevelDB and TPC-C on SQLite. |
| **Metric** | throughput |
| **Adoption** | 51 stars; FAST 2023 paper |
| **Last commit** | 2023-03-05 |
| **Links** | [repository](https://github.com/ShawnZhong/MadFS) · [benchmark](https://github.com/ShawnZhong/MadFS) |

## Verdict

The FAST '23 paper abstract, reproduced in the README, reports up to 3.6x ext4-DAX throughput on concurrent microbenchmarks and 48% (YCSB on LevelDB) and 85% (TPC-C on SQLite) speedups over NOVA. Benchmark drivers (Google Benchmark micro_st/micro_mt, bench_tpcc.py, bench_ycsb.py) are public and compare MadFS, ext4-DAX, NOVA and SplitFS, built with -march=native and LTO. The PM hardware and CPU are given only in the paper, which was not reachable (usenix.org blocked; a WebSearch did not return them).

## Use it when

- Research or prototyping on Intel Optane PM (or DRAM-emulated PM via memmap) where you want to compare a userspace PM filesystem against ext4-DAX, NOVA or SplitFS; the repo ships scripts that drive all four.
- Multi-threaded or multi-process pread/pwrite workloads on shared files, where ext4-DAX inode locking limits scaling and OCC helps.
- Running unmodified LevelDB or SQLite on PM to measure what userspace metadata buys (the paper's YCSB and TPC-C experiments).
- Studying a working implementation of embedded-log CoW crash consistency and user-level OCC for file I/O.

## Skip it when

- Production storage: research code, no license file, last commit 2023-03-05, and Optane PM is discontinued.
- Workloads that need truncate, ftruncate or flock: these PANIC in src/lib/misc.cpp.
- Programs that use stdio (fopen/fread): fopen is passed straight to glibc, so those files do not get MadFS handling.
- Anything without a DAX-capable PM device or emulated pmem: it relies on MAP_SYNC mmap of a DAX mount.
- Workloads that depend on fcntl results or fcntl locks: the fcntl/fcntl64 wrappers return 0 for every fd without making the call.

## How it is fast

Per-file virtualization: block mapping, crash consistency and concurrency control live in userspace inside the mmap'ed file, so data and most metadata operations skip the kernel. Writes are copy-on-write blocks committed by appending to the embedded log, and cross-process synchronization uses lock-free optimistic concurrency control (OCC) on the log tail instead of kernel inode locks. Persistence uses MAP_SYNC mappings plus clwb/clflushopt, and by default transaction entries are flushed only at fsync (MADFS_TX_FLUSH_ONLY_FSYNC).

## Compared with alternatives

Pick MadFS over SplitFS when many threads or processes write the same file and you want metadata and concurrency control in userspace without a kernel module (SplitFS still sends metadata to ext4 and its benchmarks are in MadFS's own scripts). Pick it over NOVA or WineFS when you cannot load a custom kernel filesystem, since MadFS runs on a stock ext4-DAX mount.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | libpmem2 (PMDK), oneTBB 2021.5 and magic_enum 0.8.0 (fetched by CMake), pthread, libatomic, libdl |
| **Minimum toolchain** | C++20; GCC 10.3+/11.3 or Clang 10/14 per README; CMake 3.16+ |
| **Platforms** | Linux x86-64 only in practice (built with -march=native; uses clwb/clflushopt, AVX-512 detected); needs a DAX filesystem on PM or emulated PM |
| **Thread safety** | Designed for concurrent threads and processes on the same file via user-level OCC (mutex, spinlock and rwlock variants are build options); the TSAN data race in issue #210 was closed in 2022. |
| **Drop-in for the baseline** | partial: runs unmodified POSIX programs via LD_PRELOAD, but only for regular files created by MadFS (or converted with tools/to_madfs) with block-aligned sizes; truncate/ftruncate/flock abort, fcntl is a no-op, openat64 ignores dirfd, and O_WRONLY opens are upgraded to O_RDWR. |

## Gotchas

- fcntl and fcntl64 return 0 at their first line for every descriptor, so F_GETFL/F_SETLK and similar calls silently do nothing, MadFS file or not. SQLite's POSIX advisory locks become no-ops under MadFS, which also takes those syscalls out of the TPC-C/SQLite runs.
- openat64 ignores dirfd ('TODO: implement the case where pathname is relative to dirfd'), so relative paths resolve against the CWD.
- An existing non-empty file is used as a MadFS file only if it has the shm xattr and a block-aligned size; otherwise it falls back to plain syscalls with only a log warning, so you can unknowingly benchmark ext4-DAX.
- Each process prints its build and runtime options to stderr when the library loads, and prints 'MadFS unloaded' on exit, which can break tools that parse stderr.

## Known shortcomings

- Usage gaps: truncate, ftruncate and flock PANIC; fcntl and fcntl64 return 0 for every fd without calling the real function; openat64 ignores dirfd; fopen is not intercepted. Possible bias, not proven: under MadFS SQLite's fcntl locks become no-ops, which may flatter the TPC-C/SQLite 85% against NOVA. Paper hardware still unknown (usenix.org blocked).

## Caveats and trade-offs

Numbers from the FAST 2023 paper abstract reproduced in the README; the paper PDF (usenix.org) was blocked, so hardware (Optane PM machine) and exact flags were not checked. Requires persistent memory (DAX) hardware to use. No LICENSE file (raw LICENSE 404, none shown on the repo page), so reference only. Last commit 2023-03-05.

Needs persistent memory (emulated or real) and a Linux preload layer; C++20; per-file virtualization in userspace.

## Maintenance

Abandoned research artifact (last commit 2023-03-05, 0 open of 48 issues, 51 stars) with no LICENSE file, so reference only; it needs Optane-class or emulated PM to run.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed FAST '23 paper; the README abstract states up to 3.6x ext4-DAX throughput on concurrent workloads and 48% (YCSB/LevelDB) and 85% (TPC-C/SQLite) speedups over NOVA. Benchmark scripts are public (scripts/bench_st.py, bench_mt.py, bench_tpcc.py, bench_ycsb.py) and compilers are listed (GCC 10.3/11.3, Clang 14), but the CPU/PM hardware is only in the paper PDF (usenix.org blocked), so not A.
- **Verifier notes:** Numbers match README abstract exactly. usenix.org egress-blocked; a paper-access retier could check hardware for A (benchmark code public, compilers listed).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** peer-reviewed paper, snippet only
- **Pages the verifier opened:**
  - <https://github.com/ShawnZhong/MadFS>
  - <https://github.com/ShawnZhong/MadFS/commits>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/README.md>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/README.md>
  - <https://github.com/ShawnZhong/MadFS>
  - <https://github.com/ShawnZhong/MadFS/issues?q=is%3Aissue>
  - <https://github.com/ShawnZhong/MadFS/tree/main/src/lib>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/src/lib/lib.cpp>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/src/lib/open.cpp>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/src/lib/misc.cpp>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/src/lib/mmap.cpp>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/src/file/file.h>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/src/tx/read.h>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/scripts/bench_mt.py>
  - <https://raw.githubusercontent.com/ShawnZhong/MadFS/HEAD/scripts/fs.py>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/shawnzhong/madfs`) · [data/wave11/enrich/raw/github_com_shawnzhong_madfs.json](../../../data/wave11/enrich/raw/github_com_shawnzhong_madfs.json) (enrichment confidence 0.75)

</details>
