# LLFIO

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0 OR BSL-1.0` · 🟢 active

> Low-level, zero-copy, race-free C++17 file and memory-map i/o library; no head-to-head numbers against POSIX read/write.

| | |
|---|---|
| **Beats** | POSIX read/write (physical device latency used as reference) |
| **Claimed result** | No speedup ratio. Readme says i/o overhead including syscalls benchmarked at 100 ns on Linux; 100% read QD1 4Kb direct transfer latencies at &lt;99%: NVMe Windows 37us, FreeBSD 70us, Linux 30us; SATA flash Windows 290us, Linux 158us (versus manufacturer-claimed device latencies, not versus another library). |
| **Workload** | fs_probe_results.yaml device latency profiles (direct QD1 4K read p99 about 96 us on PM9A1 XFS, Threadripper PRO 5975WX); no io_uring backend (still on the Readme todo list; multiplex.hpp is an interface stub) |
| **Metric** | latency |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-08-24 |
| **Links** | [repository](https://github.com/ned14/llfio) · [benchmark](https://github.com/ned14/llfio) |

## Verdict

The README gives about 100 ns of software overhead per i/o on Linux and 99th-percentile QD1 4 KiB direct read latencies of 30 us (Linux), 37 us (Windows) and 70 us (FreeBSD) on NVMe, set beside manufacturer device latencies; no baseline library, compiler, flags or exact hardware are tied to those figures. The repo's fs_probe_results.yaml carries raw latency profiles (for example AMD Threadripper PRO 5975WX, Linux 5.15, RAID0 Samsung PM9A1 on XFS: direct QD1 4 KiB read p99 about 96 us), which are device characterisations, not comparisons.

## Use it when

- Storage engines or databases that do 4 KiB direct (O_DIRECT) i/o on NVMe or Optane and need per-op overhead well under the device latency.
- Portable code across Linux, Windows and FreeBSD that wants memory-mapped files, sparse files, hole punching and large/huge pages through one API.
- Filesystem algorithms that must be race-free against concurrent renames (anchored path_handle opens, no stored paths).
- Builds with exceptions and RTTI disabled that still need rich error codes (original NT kernel error codes are preserved).

## Skip it when

- You need an async submission-queue backend: Linux io_uring support is still on the README's todo list and multiplex.hpp is only an interface sketch; use liburing or SPDK directly.
- You want a measured speedup over read/write or std::fstream: the project publishes overhead and device latency figures only, never a comparison against another library.
- Mac OS deployments: the README says it is less well tested there.
- Header-only use on Windows without status_code or a shared ntkernel error category: Build.md warns error-code comparisons can randomly fail.
- Small tools that just read a few files: the API surface is large and the build pulls in QuickCppLib and Outcome via a CMake bootstrap.

## How it is fast

The design target is near-zero software overhead per i/o: no malloc, no exceptions and no whole-machine memory copy on the i/o path, path_view instead of allocated std::filesystem::path, and thin wrappers over pread/pwrite-style syscalls (the README says about 100 ns per i/o on Linux, syscall included). It exposes O_DIRECT and seven kernel caching modes, plus memory-mapped scatter-gather i/o with large and huge page support, so you can pick the caching and copy behaviour per handle. It does not add a faster algorithm on top of the OS; the gain is avoiding the allocation, copying and locking that iostreams and std::filesystem add.

## Compared with alternatives

Pick LLFIO over liburing or SPDK when you want a portable, synchronous, race-free file and mmap abstraction across Linux and Windows rather than a Linux-only async queue; for raw IOPS at high queue depth liburing or SPDK are the measured options. Unlike FastMap or UMap it does not replace the kernel mmap path, it wraps it.

## Integration

| | |
|---|---|
| **Form** | header-only, static lib or shared lib (selectable; also vcpkg 'llfio' and prebuilt release binaries) |
| **Dependencies** | QuickCppLib and Outcome (fetched by the CMake bootstrap); git submodules ntkernel-error-category and wg14_signals; an STL with working &lt;filesystem&gt; |
| **Minimum toolchain** | C++17 with std::filesystem; CMake 3.9+; CI covers GCC and Clang on Linux, Xcode, Visual Studio (Android NDK and MinGW build only) |
| **Platforms** | Linux, Windows, FreeBSD, Mac OS (less tested), Android/iOS build-only; README targets kernels back to Linux 2.6.32 and Windows 8.1 |
| **Thread safety** | not documented per handle; the v2 redesign removed all internal use of multiple threads and shared_ptr, so synchronise shared handles yourself |
| **Drop-in for the baseline** | no |

## Gotchas

- Header-only mode on Windows can produce binaries where semantic error-code comparisons fail; define LLFIO_EXPERIMENTAL_STATUS_CODE=1 or link the prebuilt library.
- map_handle's page cache does not self-trim; you must call trim_cache() or allocations accumulate.
- Open Windows bugs: mapped_temp_inode leaks space (#160) and map(section, reserve) does not work (#121); algorithm::traverse relies on vector&lt;list&lt;move-only&gt;&gt; (#98).
- Clone with --recursive and do an out-of-tree build or the CMake build fails; Build.md itself is flagged as inaccurate for POSIX (#111).

## Known shortcomings

- No head-to-head numbers anywhere; fs_probe_results.yaml holds only device latency profiles (Threadripper PRO 5975WX, PM9A1 XFS, direct QD1 4K read p99 about 96 us). io_uring is still on the Readme todo list and multiplex.hpp is an interface stub only. Open Windows bugs 160 and 121.

## Caveats and trade-offs

No head-to-head against read/write or mmap on the page I opened; claim is overhead vs device latency, not a speedup over a named baseline; hardware and flags not stated there. Benchmark detail may live in docs not opened.

Large API surface (P1031 proposal); standardisation attempt abandoned in 2025; needs C++17.

## Maintenance

Active (last commit 2026-08-24), dual Apache-2.0/BSL-1.0, mature and in production use per the README, but the standardisation effort was abandoned in 2025 and io_uring remains unimplemented.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** Readme.md states 100 ns i/o overhead on Linux and lists &lt;99% QD1 4Kb latencies (NVMe Linux 30us, SATA Linux 158us) next to manufacturer device latencies, but has no head-to-head against POSIX read/write, mmap or std::fstream and no methodology. No baseline comparison, so D; kept as notable (1.1k stars, Boost-reviewed, production use cited).
- **Verifier notes:** Numbers confirmed in Readme.md (README.md path 404s; file is Readme.md, default branch develop). License file offers Apache-2.0 or BSL-1.0; last commit 2026-08-24; not archived. Readme notes the WG21 standardization effort was abandoned in 2025.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`
- **Shortcomings recorded by:** public benchmark code
- **Pages the verifier opened:**
  - <https://github.com/ned14/llfio>
  - <https://github.com/ned14/llfio/commits/develop>
  - <https://raw.githubusercontent.com/ned14/llfio/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/ned14/llfio/HEAD/Licence.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ned14/llfio/develop/Readme.md>
  - <https://raw.githubusercontent.com/ned14/llfio/develop/Build.md>
  - <https://raw.githubusercontent.com/ned14/llfio/develop/programs/fs-probe/fs_probe_results.yaml>
  - <https://raw.githubusercontent.com/ned14/llfio/develop/.gitmodules>
  - <https://raw.githubusercontent.com/ned14/llfio/develop/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ned14/llfio/develop/include/llfio/v2.0/multiplex.hpp>
  - <https://raw.githubusercontent.com/ned14/llfio/develop/include/llfio/v2.0/map_handle.hpp>
  - <https://github.com/ned14/llfio/tree/develop/include/llfio/v2.0>
  - <https://github.com/ned14/llfio/tree/develop/include/llfio/v2.0/detail/impl/posix>
  - <https://github.com/ned14/llfio/issues?q=is%3Aissue+is%3Aopen+bug>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/ned14/llfio`) · [data/wave11/enrich/raw/github_com_ned14_llfio.json](../../../data/wave11/enrich/raw/github_com_ned14_llfio.json) (enrichment confidence 0.7)

</details>
