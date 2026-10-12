# ayafileio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (C++ native extension)` · `MIT` · 🟢 active

> Python async file I/O with a C++ native core on io_uring, IOCP and Dispatch I/O; beats thread-pool aiofiles on small cached reads.

| | |
|---|---|
| **Beats** | aiofiles (thread-pool async file I/O) |
| **Claimed result** | Linux io_uring random 4 KiB reads vs aiofiles: 191.5K vs 9.8K ops/s at x1 (19.6x), 361.6K vs 10.2K at x16 (35.4x), 361.2K vs 12.5K at x64 (28.9x); small 4 KiB sequential reads 9.2x; macOS 4 KiB sequential read 499K ops/s (27.2x over aiofiles; the README's 6.8K figure is the earlier value, not aiofiles); Windows (local) sequential write 3,046 MB/s at 4 MiB (stated 1.47x over aiofiles) |
| **Workload** | Random and sequential 4 KiB async reads and writes at 16-64 concurrent operations on Linux (io_uring), macOS (Dispatch I/O) and Windows (IOCP). |
| **Metric** | throughput |
| **Adoption** | 43 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/Patchouli-CN/ayafileio) · [benchmark](https://github.com/Patchouli-CN/ayafileio) |

## Verdict

First-party tests/t_compare.py runs on GitHub Actions runners (Python 3.14, CPU and kernel not recorded; median of 3 one-second rounds after a 0.3 s warmup) against aiofiles at its defaults. On Linux io_uring, random cache-hot 4 KiB reads ran 19.6x-35.4x faster and small sequential reads 9.2x faster, but 4 MiB sequential writes ran 0.4x. Windows headline write figures are local, unspecified NVMe runs.

## Use it when

- asyncio services doing many small (4-64 KiB) reads of page-cache-hot files, where aiofiles' per-op executor round-trip dominates
- Random positioned reads from many coroutines on one handle (read_at), which aiofiles cannot do without seek+read
- Loading or writing many files concurrently from asyncio (read_bytes_many / write_bytes_many with parallel aopen), e.g. config or model-shard fan-out
- Linux with kernel 5.19+ for the COOP_TASKRUN inline path; prebuilt wheels cover CPython 3.10-3.15 including free-threaded builds

## Skip it when

- Large sequential buffered writes on Linux: the README's CI run has aiofiles ahead at 4 MiB blocks (0.4x)
- As a C++ library: there is no C++ API; use liburing directly instead
- When you need tested, stable semantics: version 1.11.2 (2026-10-06) still fixes fd-lifetime races on macOS, and 1.11.1 fixed a use-after-free in aopen's error path. The project moves fast, with commits labelled AI-assisted.
- Windows CI-class VMs: the windows-2022 runner measured 64 KiB sequential read at 0.79x and 4 KiB small reads at 0.62x of aiofiles
- Cold-cache or O_DIRECT workloads: none of the published cells measure uncached storage

## How it is fast

Each operation is submitted to a kernel completion API instead of an asyncio executor thread. Results are delivered to the event loop through an adaptive completion batcher (call_soon_threadsafe on count threshold or last in-flight op). Cache-hit fast paths resolve the future inline, so await never yields: io_uring IORING_SETUP_COOP_TASKRUN with an inline CQ peek after submit, Windows FILE_SKIP_COMPLETION_PORT_ON_SUCCESS, and macOS mincore residency check plus pread. Reads go zero-copy into a pre-built PyBytes, writes go zero-copy from a held buffer view, and a thread-local IORequest freelist avoids per-op allocation.

## Compared with alternatives

Pick it over aiofiles when you are in Python asyncio and need fast small or concurrent reads. From C or C++, liburing (or LLFIO for a portable C++ API) gives the same kernel paths without the Python layer. couring is only a teaching demo of the coroutine-over-io_uring pattern.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime (prebuilt wheels); building from source needs scikit-build-core &lt;1.1, nanobind &gt;=2.12, CMake 3.15+, and liburing on Linux (otherwise io_uring is disabled and the thread-pool fallback is used) |
| **Minimum toolchain** | Python 3.10+, C++20 compiler for source builds (built -O3 / MSVC /O2, Release) |
| **Platforms** | Linux (io_uring, kernel 5.1+; x86-64, aarch64, riscv64 wheels), Windows 7+ (IOCP), macOS 10.10+ (Dispatch I/O) |
| **Thread safety** | Concurrent positioned reads/writes on one handle are supported; seek+read on a shared handle races by design (the benchmark avoids it), and overlapping concurrent writes have unspecified ordering |
| **Drop-in for the baseline** | partial: open() mirrors the aiofiles API (async with, read/write/seek, text modes), but ayafileio is unbuffered by default and write buffers must not be mutated until the write future resolves |

## Gotchas

- The comparison is lopsided: in the random-read cell aiofiles does await seek() plus await read() (two executor round-trips per op), while ayafileio does one read_at. aiofiles runs buffered, ayafileio unbuffered. All reads hit a 256 MiB file that was just written, so they are page-cache hot.
- README arrow figures (6.8K to 499K, 929 to 3,046 MB/s) are this library's own before/after versions; only the parenthesised ratios compare against aiofiles.
- The macOS 499K ops/s small-read figure was measured on 1.11.1, whose close-path fd fix was itself racy (ABA on the dup'd descriptor, possible EBADF on an unrelated file). 1.11.2 rewrote it, and the README has not been re-measured since.
- Zero-copy writes pin the caller's buffer until the future resolves; mutating it in place changes what gets written.

## Known shortcomings

- Python library. Harness skew: aiofiles random reads do seek plus read (two executor round trips) against one read_at for ayafileio; aiofiles is buffered while ayafileio is unbuffered; reads are page-cache hot. The macOS 499K ops/s was measured on 1.11.1, whose close-path fd fix was racy (ABA, possible EBADF on an unrelated file); 1.11.2 (2026-10-06) rewrote it and the README was not re-measured. 1.11.1 also fixed a use-after-free in the aopen error path.

## Caveats and trade-offs

Baseline is aiofiles, a thread-pool wrapper, not POSIX pread or io_uring; reads are cache-hot (macOS small reads complete inline via mincore + pread); hardware and flags not captured; CI runner numbers swing about 2x run to run. Not faster everywhere: aiofiles pulls ahead on Linux 4 MiB sequential writes (0.4x), and the windows-2022 CI run measured 64 KiB sequential read at 0.79x and 4 KiB small reads at 0.62x of aiofiles. README arrow figures (6.8K to 499K, 929 to 3,046 MB/s) mix before/after values with the aiofiles ratio. Python package, only weakly in scope for the C++ filter. Commits are labelled AI-assisted.

Python API (aiofiles compatible); native C++ extension is not a C++ library API.

## Maintenance

Very active (1.11.2 on 2026-10-06, 376 commits, MIT, PyPI wheels marked Production/Stable), but the low-level backends still get frequent race and lifetime fixes, so pin a version.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers from tests/t_compare.py on GitHub Actions runners (Python 3.14) against aiofiles; benchmark code is public but no CPU model or compiler flags, and Windows headline figures are local unspecified NVMe runs.
- **Verifier notes:** Numbers verified in the README Benchmarks section; corrected the macOS phrasing (6.8K is not the aiofiles number since 499/6.8 is about 73x) and documented the cells where it is slower than aiofiles. License MIT, last commit 2026-10-05, 43 stars confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/Patchouli-CN/ayafileio>
  - <https://github.com/Patchouli-CN/ayafileio/commits>
  - <https://raw.githubusercontent.com/Patchouli-CN/ayafileio/HEAD/README.md>
  - <https://raw.githubusercontent.com/Patchouli-CN/ayafileio/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/Patchouli-CN/ayafileio>
  - <https://raw.githubusercontent.com/Patchouli-CN/ayafileio/HEAD/README.md>
  - <https://raw.githubusercontent.com/Patchouli-CN/ayafileio/HEAD/tests/t_compare.py>
  - <https://raw.githubusercontent.com/Patchouli-CN/ayafileio/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/Patchouli-CN/ayafileio/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Patchouli-CN/ayafileio/HEAD/docs/CHANGES.md>
  - <https://raw.githubusercontent.com/Patchouli-CN/ayafileio/HEAD/src/backends/io_uring_backend.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/patchouli-cn/ayafileio`) · [data/wave11/enrich/raw/github_com_patchouli_cn_ayafileio.json](../../../data/wave11/enrich/raw/github_com_patchouli_cn_ayafileio.json) (enrichment confidence 0.7)

</details>
