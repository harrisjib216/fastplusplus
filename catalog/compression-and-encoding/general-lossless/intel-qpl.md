# Intel QPL (IAA hardware deflate path)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Intel's C library that offloads Deflate (4 KB window) to the IAA accelerator on Sapphire Rapids Xeons, beating Snappy, zstd and zlib-ng in database pipelines.

| | |
|---|---|
| **Beats** | zlib-ng and zstd software compression (Intel RocksDB guide); Snappy and CPU deflate execution in DuckDB (ADMS 2025 paper) |
| **Claimed result** | Snippet only, no page opened. ADMS 2025 paper ('A Hot Take on the Intel Analytics Accelerator for Database Management Systems') per search snippet: DuckDB Deflate on IAA reaches 4.59 GB/s compression and 18.24 GB/s decompression; up to 10x faster decompression than DuckDB's Snappy in microbenchmarks and up to 30% lower end-to-end TPC-H query latency. Intel RocksDB tuning guide per search snippet: 103% higher throughput and 64% lower p99 latency than zstd for an 80:20 read/write mix with 16KB blocks and 256B values (this differs from the 34%-95% / 23%-51% range in the original record; neither could be checked against the page). The zlib-ng figures (92%-205% throughput, 53%-74% p99) were not confirmed by any snippet this verifier saw. |
| **Workload** | RocksDB compression/decompression with Intel IAA offload on 4th-gen Xeon (per Intel tuning guide), plus DuckDB and HTSlib tests in third-party papers. |
| **Metric** | throughput |
| **Hardware** | Intel Sapphire Rapids Xeon (4th gen) with IAA accelerator |
| **Adoption** | 110 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/intel/qpl) · [benchmark](https://www.vldb.org/2025/Workshops/VLDB-Workshops-2025/ADMS/ADMS25-05.pdf) |

## Verdict

No benchmark page could be opened. Per search snippets only, the ADMS 2025 workshop paper (CMU, DuckDB Parquet Deflate offloaded to IAA via QPL vs DuckDB's Snappy) reports faster decompression and lower TPC-H latency, but snippets disagree on the size (one says 4.59 GB/s compress, 18.24 GB/s decompress, up to 10x and 30%; another says up to 3.15x and 38%). Intel's vendor RocksDB tuning guide snippet claims 103% higher throughput and 64% lower p99 than zstd on Sapphire Rapids. Compiler, flags and verify settings are unknown. That RocksDB result runs through intel/iaa-plugin-rocksdb, which builds only against RocksDB's unmerged pluggable-compression PR 6717 (a fork branch) and was tested with QPL v1.7.0.

## Use it when

- Columnar or analytic databases (DuckDB Parquet, ClickHouse, RocksDB blocks) on 4th-gen Xeon or later with IAA enabled, where offloading compression frees CPU cores.
- Many small, independent blocks (4-64 KB pages) where canned or static Huffman tables cut header overhead and decompression latency.
- Pipelines that decompress and immediately filter a column (scan/select on packed integers): fused decompress-and-filter avoids a memory round trip.
- You control both ends of the format and can accept a 4 KB Deflate window.

## Skip it when

- Decompressing arbitrary zlib/gzip data from other tools: streams with a history window above 4 KB fail with QPL_STS_BAD_DIST_ERR on both paths (issue #45 hit error 217 on a chunked .zlib file).
- Machines without IAA (AMD, Arm, client Intel, pre-Sapphire Rapids Xeon): only the ISA-L-derived software path runs, and no published benchmark compares it with zlib-ng, libdeflate or ISA-L itself.
- Windows or kernel-mode use: the hardware path is Linux-only (kernel 5.18+ for IAA 1, 6.3+ for IAA 2) and the library is user-mode only.
- Best ratio: the 4 KB window costs ratio against zlib -6 and zstd; pick zstd if ratio matters more than CPU offload.
- Environments where you cannot get root or sysadmin help: IAA needs VT-d in BIOS and accel-config work-queue setup (or membership in the dsadev group with accel-config 3.2+).

## How it is fast

The fast path hands the work to Intel In-Memory Analytics Accelerator (IAA) engines through shared work queues (Intel Accelerator Interfacing Architecture descriptors via the idxd driver), so the CPU cores are free while the device runs Deflate. The software fallback uses Deflate kernels adopted from ISA-L (igzip) behind a CPUID dispatcher (SSE4.2 minimum, AVX-512 recommended). Static, canned (header-less, shared Huffman table) and indexed modes skip per-block table building and parsing for many small buffers, and decompress-plus-filter fusion avoids writing uncompressed columns back to memory.

## Compared with alternatives

Pick QPL over ISA-L (igzip), zlib-ng or libdeflate only on an IAA-equipped Xeon where moving compression off the cores matters more than ratio, and when you control both ends of the format (4 KB window). Without IAA, ISA-L or libdeflate give the same Deflate speed with full-window compatibility and published numbers, and zstd or LZ4 give better ratio/speed if you can leave Deflate.

## Integration

| | |
|---|---|
| **Form** | static lib (shared build supported since issue #31); built from source only, no binary distribution |
| **Dependencies** | nasm 2.15+ to build; libaccel-config 4.0+ (idxd-config) for the hardware path, loaded at run time with dlopen by default so software-only users do not need it; idxd kernel driver |
| **Minimum toolchain** | C++17 compiler (GCC 8.2+, Clang 12.0.1+ for fuzz tests, MSVC 14.1+), CMake 3.16.3+ |
| **Platforms** | Intel 64 only. Software path: x86-64 with SSE4.2 or newer (Linux, Windows). Hardware path: Linux on Xeon with IAA (Sapphire Rapids and later). |
| **Thread safety** | Not documented as a guarantee; state lives in a caller-allocated qpl_job, so one job per thread is the implied model. The device dispatcher picks work queues per NUMA node or socket of the calling thread. |
| **Drop-in for the baseline** | partial — produces RFC 1950/1951/1952-compatible output readable by zlib, but its own decoder rejects streams with windows above 4 KB, and the API is a job interface, not zlib's. intel/zlib-accel is the zlib-API shim. |

## Gotchas

- Auto path gives no API to tell whether a job ran on IAA or the host; only a -DLOG_HW_INIT=ON build prints it. In a multi-job stream only the first job may fall back to the host, and later jobs fail with an error instead of falling back.
- Compression jobs never share history: splitting a stream into many small jobs lowers the ratio, and canned mode cannot span multiple jobs.
- Compression is verified by default (it decompresses and checks the CRC). QPL_FLAG_OMIT_VERIFY skips that, so check which setting any benchmark used. Software-path verification only works with indexing or inputs under 32 KB. Releases 1.6.0 and 1.7.0 fixed verification bugs with IAA 2.0 and with stored blocks on the async path.
- Past fixes: integer overflow in qpl_get_safe_deflate_compression_buffer_size (1.8.0), the huffman_table.cpp overflow from issue #49 (64-bit casts in the current source), out-of-bounds reads found by fuzzing in expand/extract/select (1.9.0), and a symbol clash when linked with ISA-L (1.5.0). Open issue #52 reports hardware-path init error 501, and issue #51 reports throughput stuck at 3.8 GB/s beyond 2 engines with one work queue.

## Known shortcomings

- Numbers are snippet-only (intel.com, vldb.org and cs.cmu.edu blocked); the repo's tools/benchmarks hold IAA-only numbers with no baseline. The RocksDB guide snippet says 103% throughput and 64% p99 vs zstd, which does not match the search record's 34-95%. The IAA hardware path is a different machine class from software codecs. Retier candidate to B once the ADMS 2025 paper is reachable.
- Speed needs IAA hardware: Linux only, kernel 5.18+, VT-d and accel-config setup; the software path has no baseline benchmark. 4 KB Deflate window both ways, so zlib/gzip streams with larger windows fail with QPL_STS_BAD_DIST_ERR (issue #45), only a partial drop-in. Past fixes: overflow in qpl_get_safe_deflate_compression_buffer_size (1.8.0), huffman_table.cpp overflow (#49), fuzz out-of-bounds in expand/extract/select (1.9.0), verify bugs (1.6.0/1.7.0). Open #52 hardware init error 501; #51 stalls at 3.8 GB/s past 2 engines on one work queue. Auto path cannot report hardware vs host. The RocksDB plugin needs an unmerged RocksDB fork. ADMS 2025 snippets disagree (10x decompress / 30% TPC-H vs 3.15x / 38%). MIT plus bundled ISA-L BSD-3.

## Caveats and trade-offs

Hardware-gated: the speedups come from the Intel IAA accelerator on 4th-gen Xeon (Sapphire Rapids) and later, a different machine class from a software codec; QPL's software fallback path has no published comparison against zlib-ng or zstd. Every number is snippet only: intel.com, vldb.org and cs.cmu.edu were EGRESS_BLOCKED, so the paper and guide were not opened. Intel guide is vendor-run (tier C at best); the RocksDB result runs through Intel's separate IAA RocksDB plugin built on QPL. The repo's own benchmark framework (tools/benchmarks, google-benchmark based) reports IAA throughput only, e.g. about 1.26-1.76 GB/s per job in the quick-start sample output, with no baseline. Retier candidate: open the ADMS 2025 paper for a peer-reviewed tier B check.

Needs IAA hardware on Sapphire Rapids or later for the fast path; software fallback is the only option elsewhere. Deflate format only, ratio is lower than zstd. Related shim intel/zlib-accel (Apache-2.0) offloads whole-stream zlib calls to QAT/IAA or igzip but ships no benchmarks and has no streaming support on the accelerators.

## Maintenance

Actively maintained by Intel (develop branch, last commit 2026-09-25, latest tagged release v1.9.0 of 2024-12-10). MIT-licensed with bundled ISA-L code (BSD-3) and gtest/benchmark test dependencies. Copyable, but the speed claims need IAA hardware.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now D.
- **Tier reason:** No page carrying the numbers could be opened: the Intel RocksDB tuning guide (intel.com), the ADMS 2025 paper (vldb.org and cs.cmu.edu copies) are EGRESS_BLOCKED, and the repo README and bench docs (doc/source/documentation/bench_docs/quick_start.rst, tools/benchmarks) show only IAA-path throughput with no software baseline. Snippet-only numbers cannot hold the record above D; the ADMS 2025 paper is a peer-reviewed candidate for tier B once reachable.
- **Verifier notes:** Repo metadata confirmed on github.com: MIT, 110 stars, not archived, not a fork, last commit 2026-09-25 (active). Two WebSearch queries used for snippets; the RocksDB snippet's numbers do not match the record's, so claimed_speedup was rewritten to what the snippets say.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party claim (snippet); first-party claim (snippets)
- **Pages the verifier opened:**
  - <https://github.com/intel/qpl>
  - <https://github.com/intel/qpl/commits/develop>
  - <https://github.com/intel/qpl/tree/develop/tools>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/README.md>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/bench_docs/quick_start.rst>
- **Sources the enricher read:**
  - <https://github.com/intel/qpl>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/README.md>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/third-party-programs.txt>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/get_started_docs/installation.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/introduction_docs/introduction.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/dev_guide_docs/low_level_developer_guide.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/dev_guide_docs/c_use_cases/deflate/c_deflate.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/dev_guide_docs/c_use_cases/deflate/c_deflate_compression.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/dev_guide_docs/c_use_cases/deflate/c_deflate_decompression.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/dev_guide_docs/c_use_cases/deflate/c_deflate_multiple_jobs.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/dev_guide_docs/c_use_cases/deflate/c_deflate_zlib_gzip.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/dev_guide_docs/c_use_cases/c_asynchronous_execution.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/dev_guide_docs/c_use_cases/c_job_structure.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/doc/source/documentation/dev_guide_docs/c_use_cases/advanced/c_advanced_topics.rst>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/include/qpl/qpl.h>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/include/qpl/c_api/job.h>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/include/qpl/c_api/defs.h>
  - <https://raw.githubusercontent.com/intel/qpl/HEAD/sources/middle-layer/compression/deflate/containers/huffman_table.cpp>
  - <https://github.com/intel/qpl/tree/develop/include/qpl>
  - <https://github.com/intel/qpl/issues?q=is%3Aissue>
  - <https://github.com/intel/qpl/issues/45>
  - <https://github.com/intel/qpl/issues/49>
  - <https://github.com/intel/qpl/issues/51>
  - <https://github.com/intel/qpl/releases>
  - <https://raw.githubusercontent.com/intel/iaa-plugin-rocksdb/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/intel/qpl`) · [data/wave9/enrich/raw/github_com_intel_qpl.json](../../../data/wave9/enrich/raw/github_com_intel_qpl.json) (enrichment confidence 0.5)

</details>
