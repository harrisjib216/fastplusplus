# file_io_benchmark (Windows unbuffered multi-threaded loading)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Windows benchmark showing multi-threaded FILE_FLAG_NO_BUFFERING reads reach 11.3 GB/s on NVMe versus fread and memory mapping.

| | |
|---|---|
| **Beats** | fread / memory-mapped file reads |
| **Claimed result** | Unbuffered auto threads 11.3-11.4 GB/s vs fread 4.2-5.0 GB/s (auto) and memory mapping 6.8-7.3 GB/s (auto); single thread: unbuffered 4.7-4.9 GB/s vs fread 4.4-6.3 GB/s (fread can win single-threaded) and memory mapping 1.2 GB/s |
| **Workload** | Loading 1,000 chunks of 1 MiB (1.0 GB) from NVMe on Windows with unbuffered multi-threaded reads versus fread and memory mapping, 5 repetitions. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 7950X, Samsung SSD 9100 PRO 4TB |
| **Adoption** | 2 stars |
| **Last commit** | 2026-01-22 |
| **Links** | [repository](https://github.com/m-schuetz/file_io_benchmark) · [benchmark](https://github.com/m-schuetz/file_io_benchmark) |

## Verdict

On an AMD Ryzen 9 7950X with a Samsung SSD 9100 PRO 4TB, loading 1,000 x 1 MiB chunks over 5 repetitions with the file evicted from cache, unbuffered multi-threaded reads reached 11.3-11.4 GB/s versus 6.8-7.3 GB/s for multi-threaded memory mapping and 4.2-6.3 GB/s for fread; compiler and flags are not stated (CMake project, MSVC implied). The fread rows read sequentially rather than in the shuffled order, so the comparison is not like-for-like, though the bias favors fread.

## Use it when

- Windows apps that read large files once (point clouds, assets, model weights) and do not benefit from the OS cache.
- Chunked loads of 1 MiB-scale, sector-aligned blocks that can be issued from many threads at once to saturate a PCIe 4/5 NVMe drive.
- As a reference for writing your own Windows direct-I/O loader before reaching for IoRing or DirectStorage.
- When memory mapping tops out (about 7 GB/s here with many threads, 1.2 GB/s with one) and you need the remaining drive bandwidth.

## Skip it when

- Linux or macOS: the code is Windows-only (MappedFile.h has a literal TODO for Linux and will not compile there); use liburing or O_DIRECT instead.
- Single-threaded readers: unbuffered at one thread (4.7-4.9 GB/s) did not beat fread (4.4-6.3 GB/s) in the author's table.
- Data read repeatedly or small/unaligned reads: bypassing the cache throws away reuse, and offsets, sizes and buffer addresses must be multiples of the physical sector size.
- Anything you need to ship as a dependency: no LICENSE file, 2 commits, no tests, error handling is exit() with a stack trace.

## How it is fast

Unbuffered (direct) I/O skips the Windows file cache, so data goes from the SSD by DMA straight into a sector-aligned user buffer with no extra copy and no cache bookkeeping. Throughput comes from parallelism: std::for_each(std::execution::par) runs many threads, each issuing one blocking 1 MiB overlapped ReadFile and waiting on GetOverlappedResult, which keeps enough requests in flight to approach the drive's rated 14.8 GB/s. Single-threaded, the same path reaches only 4.7-4.9 GB/s.

## Compared with alternatives

Pick it when you are on Windows and want the simplest pattern for saturating NVMe; on Linux, liburing (io_uring) or SPDK are the catalogued choices, and LLFIO is the cross-platform library that wraps direct I/O properly.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Windows SDK (windows.h, winmm.lib); a C++23 standard library with &lt;print&gt;, &lt;stacktrace&gt; and parallel algorithms (MSVC) |
| **Minimum toolchain** | C++23 (CMAKE_CXX_STANDARD 23), CMake 3.22; MSVC-specific (_aligned_malloc, #pragma comment(lib)) |
| **Platforms** | Windows x86-64 only |
| **Thread safety** | UnbufferedFile::read is called concurrently on one HANDLE from many threads, each with its own OVERLAPPED and event; otherwise not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the fread benchmarks never call fseek, so every fread reads the next sequential 1 MiB of the file instead of the shuffled range.offset; the reference-value check still passes because the same first 1,000 MiB are read in some order. fread therefore got sequential reads with OS read-ahead while the other methods read in random order, and in the 'auto' case all threads share one FILE\* whose CRT lock serializes them (which explains the author's puzzle that fread par is slower than fread seq).
- UnbufferedFile::read ignores the bytes-read count from GetOverlappedResult and creates and closes a Windows event per call; short reads at end of file would go unnoticed.
- Cache eviction relies on an undocumented trick (open the file with FILE_FLAG_NO_BUFFERING and close it, repeated 10 times); the author confirmed it with RamMap, but it is not a supported API.
- Throughput is computed with 1 GB = 10^9 bytes over 1,000 MiB actually read, and only every 1,000th byte is inspected, so the work after loading is near zero; the mapped-file numbers measure page-fault cost, not a copy into a buffer.

## Known shortcomings

- Harness flaw in the fread rows: no fseek, so they read the file sequentially instead of the shuffled range.offset order, and the shared FILE\* lock serializes fread in the parallel case. The reference-value check still passes and the bias favours fread, so the unbuffered win holds, but the rows are not like for like. No LICENSE file; Windows and MSVC C++23 only.

## Caveats and trade-offs

No license; compiler and flags not stated; Windows-only APIs; page-cache state between repetitions unspecified; 2 commits; single-threaded unbuffered is not faster than fread (4.7-4.9 vs 4.4-6.3 GB/s); the win comes from multi-threaded unbuffered reads. Technique harvested from a benchmark repo, not a library.

Windows APIs; benchmark code and technique, not a reusable library.

## Maintenance

Two commits on 2026-01-22 and no LICENSE file, so all rights reserved: treat it as a reference for the technique and rewrite the roughly 100 lines you need.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README table compares unbuffered reads against fread and memory mapping on a stated Ryzen 9 7950X and Samsung 9100 PRO; code in src/ is public, but compiler and flags are not stated, so not A; first-party, so C.
- **Verifier notes:** Numbers match the README exactly. Repo is a 2-commit benchmark harness (both commits 2026-01-22), no LICENSE file, so reference only.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `maintenance_status`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/m-schuetz/file_io_benchmark>
  - <https://github.com/m-schuetz/file_io_benchmark/commits>
- **Sources the enricher read:**
  - <https://github.com/m-schuetz/file_io_benchmark>
  - <https://github.com/m-schuetz/file_io_benchmark/tree/main/src>
  - <https://raw.githubusercontent.com/m-schuetz/file_io_benchmark/HEAD/readme.md>
  - <https://raw.githubusercontent.com/m-schuetz/file_io_benchmark/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/m-schuetz/file_io_benchmark/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/m-schuetz/file_io_benchmark/HEAD/src/UnbufferedFile.h>
  - <https://raw.githubusercontent.com/m-schuetz/file_io_benchmark/HEAD/src/MappedFile.h>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/m-schuetz/file_io_benchmark`) · [data/wave11/enrich/raw/github_com_m_schuetz_file_io_benchmark.json](../../../data/wave11/enrich/raw/github_com_m_schuetz_file_io_benchmark.json) (enrichment confidence 0.6)

</details>
