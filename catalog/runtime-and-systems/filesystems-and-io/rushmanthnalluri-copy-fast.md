# copy-fast

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · 🟢 active

> Student C11 Linux file-copy tool with threaded pipeline and io_uring backends, compared only against its own naive read/write loop.

| | |
|---|---|
| **Beats** | project's own naive sequential read/write backend (backend_naive.c); 1-worker run for the multi-file test |
| **Claimed result** | Dense 100 MB file: pipeline 0.0376s vs naive 0.0869s (2.31x), io_uring 0.0487s (1.78x). 1,000-file tree: 4 workers 0.0302s vs 1 worker 0.3170s (10.49x), 8 workers 0.0917s (3.45x). Sparse 500 MB file: naive 0.0018s faster than pipeline 0.0071s and io_uring 0.0022s. |
| **Workload** | Copy dense files and multi-file trees with pipeline and io_uring backends on Linux NVMe. |
| **Metric** | throughput |
| **Hardware** | Linux 6.18 x86_64, NVMe storage (CPU model not stated) |
| **Compiler and flags** | GCC or Clang, C11, -O3 (per README Makefile note; compiler version not stated) |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/rushmanthnalluri/copy-fast) · [benchmark](https://github.com/rushmanthnalluri/copy-fast) |

## Verdict

The README's single-run table, produced by bench/benchmark.c and bench/run_benchmarks.sh, shows a 100 MB page-cache-resident file copied in 0.0376 s by the threaded pipeline vs 0.0869 s by the project's own sequential read/write loop (2.31x) and 0.0487 s by io_uring, on Linux 6.18 x86_64 with -O3 and an unstated CPU and compiler; GNU cp was never measured. The 1,000-file 10.49x figure compares 4 workers on the naive path against 1 worker on the heavier per-file pipeline path, so it is not a clean parallelism measurement.

## Use it when

- Reading a compact, readable example of a reader/writer bounded-buffer copy pipeline in C11 with pthreads
- Studying a minimal liburing read-then-write copy loop with fixed slot buffers
- Teaching SEEK_HOLE/SEEK_DATA sparse copying and a resume journal design
- Linux-only experiments on page-cache-resident files where you want to compare overlap strategies yourself

## Skip it when

- As a production replacement for GNU cp, rsync, fcp or wcp: no license, 7 commits, 0 stars, and it was never benchmarked against cp
- On filesystems where cp would reflink or use copy_file_range (Btrfs, XFS, NFS server-side copy): copyfast always moves bytes through user space
- When you need durability: no backend fsyncs the destination unless -v or an interrupt triggers fdatasync, so timings and 'done' mean data is only in the page cache
- Non-Linux platforms: requires liburing and Linux syscalls
- Trees of many small files with -j 1: each file takes the pipeline path, which spawns two threads and allocates 8 x 1 MB buffers per file

## How it is fast

The pipeline backend runs a reader pthread (pread) and a writer pthread (pwrite) over a bounded pool of 4 KB-aligned 1 MB slots, so reads and writes overlap. The io_uring backend submits up to queue_depth reads via liburing and chains a write SQE on each read completion. Directory copies use a bounded work queue drained by -j N worker threads. Sparse files are walked with lseek(SEEK_HOLE/SEEK_DATA) and holes are skipped. It does not use copy_file_range, sendfile or reflinks (FICLONE), which are what make modern cp fast.

## Compared with alternatives

Only for reading the code: for real copies prefer fcp or wcp (both measured against GNU cp, the latter with an io_uring design) or uring-sync for many small files, all of which beat cp itself rather than a self-written naive loop.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | pthreads, liburing (liburing-dev) |
| **Minimum toolchain** | C11 (GCC or Clang, -std=c11 -D_GNU_SOURCE); compiler versions not documented |
| **Platforms** | Linux only (io_uring needs a 5.x+ kernel; README results on Linux 6.18 x86_64) |
| **Thread safety** | not applicable as a library; internal stats use C11 atomics, and the work queue and buffer pool use mutex plus condition variables |
| **Drop-in for the baseline** | partial — a cp-style CLI with different flags (-R, -j, -b, -S, -p); not a GNU cp drop-in |

## Gotchas

- Multi-file benchmark confound: copy_file_dispatch sends files under 512 KB to the naive backend only when jobs &gt; 1, so the -j 1 'baseline' copies each 32 KB file via the pipeline backend (two pthread_create calls plus 8 MB of posix_memalign per file) while -j 4/-j 8 use the naive loop. The 10.49x 4-worker figure therefore mixes a backend change with parallelism, which also explains why it is super-linear and why 8 workers (3.45x) is slower than 4.
- The io_uring backend ignores short writes (a completion with res smaller than the requested length is counted and the slot freed with no resubmission), and its SQ-full fallback discards the pwrite return value, so a partial write could silently truncate data; none of this affects the published numbers on a local filesystem but it is a correctness gap.
- bench/benchmark.c times one run per backend, in a fixed order, on a 100 MB file just written to /tmp and still page-cache resident, with no destination fsync; results measure memory-to-page-cache copy, not NVMe throughput (and /tmp may be tmpfs). The dense test also runs with sparse_aware=true.
- posix_fadvise is called with POSIX_FADV_SEQUENTIAL | POSIX_FADV_WILLNEED; these are enum values, not flags, so the OR evaluates to WILLNEED only.

## Known shortcomings

- Harness flaw behind the numbers: copy_file_dispatch (src/backends.c) sends files under 512 KB to the naive backend only when jobs &gt; 1, so the -j 1 baseline runs the pipeline backend per 32 KB file (2 pthread_create plus 8x1 MB posix_memalign each) while -j 4 and -j 8 run naive; the 10.49x mixes a backend change with parallelism, which explains the super-linear 4-worker result and the slower 8 workers. The io_uring backend ignores short writes (silent truncation risk); the bench is a single run on a page-cache-resident /tmp file with no destination fsync; fadvise SEQUENTIAL|WILLNEED ORs enum values. No license; GNU cp never measured.

## Caveats and trade-offs

No license file (LICENSE, LICENSE.md, LICENSE.txt all 404); baseline is its own naive backend, never GNU cp; 10.49x is 4 workers vs 1 worker, and 8 workers is slower than 4, which with sub-0.1s timings on 100 MB suggests page-cache, noisy single runs; io_uring backend slower than the threaded pipeline; README's 'orders-of-magnitude' claim is unsupported; a 7-commit student OS-course project (12-week syllabus); no CPU model or compiler version.

Linux only; resume, sparse and verify options; student project documentation.

## Maintenance

Seven-commit OS-course project (Week 12 viva checklist, syllabus matrix) last updated 2026-10-04 with no license file, so it is reference-only and cannot legally be copied.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** README table and bench/benchmark.c are first-party; baseline is the project's own naive read/write backend, not GNU cp; no CPU model or compiler stated (Makefile -O3 per README). C, with the claim's baseline overstated.
- **Verifier notes:** Downgraded for the overstated baseline (GNU cp never measured); tier stays C. Usability reference due to no license.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/rushmanthnalluri/copy-fast>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/rushmanthnalluri/copy-fast>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/README.md>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/Makefile>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/bench/benchmark.c>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/bench/run_benchmarks.sh>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/src/backend_naive.c>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/src/backend_pipeline.c>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/src/backend_uring.c>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/src/backends.c>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/src/work_queue.c>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/src/buffer_pool.c>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/src/sparse.c>
  - <https://raw.githubusercontent.com/rushmanthnalluri/copy-fast/HEAD/include/copyfast.h>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/rushmanthnalluri/copy-fast`) · [data/wave11/enrich/raw/github_com_rushmanthnalluri_copy_fast.json](../../../data/wave11/enrich/raw/github_com_rushmanthnalluri_copy_fast.json) (enrichment confidence 0.8)

</details>
