# sse4_crc32

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Node.js native addon computing CRC-32C with the SSE4.2 crc32 instruction, 2.5-3.7x faster than its own slice-by-8 fallback.

| | |
|---|---|
| **Beats** | CRC32 |
| **Claimed result** | Native SSE4.2 CRC-32C vs native table-based CRC-32C: 4.319142 ms vs 10.726345 ms for 10000 iterations over a fixed buffer (\~2.5x, derived from page data); 60.194043 ms vs 225.459861 ms over 10000 random-length buffers (\~3.7x, derived from page data) |
| **Workload** | Node.js native-addon benchmark (benchmark/single_fixed_size_buffer.benchmark.js and benchmark/multiple_random_size_buffers.benchmark.js): CRC-32C over a single fixed 1024-byte text buffer and over 10000 random-length buffers of 0-65535 bytes, 10000 iterations each |
| **Metric** | throughput |
| **Hardware** | MacBook Air, Intel Core i7, 8GB RAM |
| **Compiler and flags** | node-gyp Release build; the SSE4.2 unit is compiled with -msse4.2 (binding.gyp); compiler and optimisation level are not stated |
| **Adoption** | 133 stars; npm package sse4_crc32 had \~952k downloads in the last month (2026-08-27 to 2026-09-25) |
| **Last commit** | 2022-03-27 |
| **Links** | [repository](https://github.com/anandsuresh/sse4_crc32) · [benchmark](http://engineering.voxer.com/2013/12/02/hardwareaccelerated-crc32-for-nodejs/) |

## Verdict

These are the author's own single-pass process.hrtime timings from `node benchmark` (current README, rewritten 2018-05-29), run on an unspecified 'Intel Core i7' MacBook Air (the current README says 16 GB RAM) with no compiler or optimisation level stated. The SSE4.2 path took 4.32 ms vs 10.73 ms for the addon's own slice-by-8 table on 10,000 calls over a fixed \~1 KiB buffer (\~2.5x), and 60.19 ms vs 225.46 ms over 10,000 random 0–64 KiB buffers (\~3.7x, roughly 5.4 vs 1.5 GB/s derived). Both figures include N-API call overhead, and there is no comparison against zlib or any external CRC library.

## Use it when

- Node.js services that must produce CRC-32C specifically, such as iSCSI/SCTP/ext4-style checksums or cloud-storage object checksums. Old issue titles show gcloud/Google Cloud Storage client users pulling it in, and today most installs arrive through the fast-crc32c wrapper.
- Checksumming medium-to-large Buffers (KiB to tens of KiB each) on x86-64, where the README run shows \~5 GB/s against \~1.5 GB/s for the table path (derived, 0–64 KiB random buffers)
- Incremental or streamed checksums of files and network data via `fromStream()` or chained `calculate(chunk, prevCrc)`
- Environments where a node-gyp native build at install time is acceptable and you want an automatic software fallback instead of a crash on non-SSE4.2 CPUs

## Skip it when

- You need zlib/PNG/gzip-compatible CRC-32 (IEEE polynomial 0xEDB88320): this computes only CRC-32C (0x82F63B78) and will produce different values
- ARM hosts (Apple Silicon, Graviton): only the software table path is built there, with no ARMv8 CRC32C instructions. Version 6.0.1, still the most-downloaded, fails to load on arm64 at all (issue #84, fixed in 7.0.0).
- Installs without a C++ toolchain and Python (Alpine or slim Docker images, locked-down CI): the install script is `node-gyp rebuild` and no prebuilt binaries ship. Build and load failures (Windows, Docker 'Exec format error') fill the issue tracker.
- Maximum throughput on large buffers: the single-chain `_mm_crc32_u64` loop is latency-bound. Interleaved or folded kernels such as komrad36/CRC (\~3x per cycle) or corsix fast-crc32 go considerably faster.
- Anything needing maintenance guarantees or CRC combine: the last release (7.0.0) was 2022-03-27, CI covers only Node 10–16, and `crc32_combine`-style merging is an open request (issue #73)

## How it is fast

On x86 it calls the SSE4.2 CRC32 instruction through the `_mm_crc32_u8/u32/u64` intrinsics. It byte-steps to 8-byte alignment, then feeds 8 bytes per instruction in a single dependent chain, then handles the u32/u16/u8 tail. The file is compiled separately with -msse4.2 and selected at load time by a CPUID leaf-1 ECX bit-20 check. The fallback is Mark Adler's slicing-by-8 table method (8x256 uint32 tables). There is no multi-stream interleaving or PCLMULQDQ folding, so it runs well below the instruction's peak throughput.

## Compared with alternatives

Pick it when you need CRC-32C from JavaScript on Node with zero integration work. The C/C++/Rust siblings (crc32c by htot, komrad36/CRC, corsix fast-crc32, crc-fast) are much faster kernels but are not Node packages. komrad36's own numbers put a plain 8-byte hardware CRC loop, which is exactly what this addon does, at \~21 bits/cycle against \~62 for its interleaved 'Golden' kernel. If you are not tied to Node, or you need IEEE CRC-32, use crc-fast, crc32fast or klauspost/crc32 instead.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | bindings ^1.3.0, node-addon-api ^1.3.0; build-time node-gyp with Python and a C++ compiler (compiled on npm install) |
| **Minimum toolchain** | package.json says Node &gt;=4, but it is N-API based and CI tests only Node 10.x–16.x; any C++ compiler that supports node-addon-api and -msse4.2 (Xcode settings target macOS 10.7+) |
| **Platforms** | x86/x86-64 for the hardware path (SSE4.2, Nehalem or later), with runtime CPUID fallback; other architectures, including arm64 since 7.0.0, get the software table path only. CI runs macOS and Ubuntu; Windows build settings exist but are not in the current CI. |
| **Thread safety** | Calls are synchronous and stateless apart from a process-global slicing-by-8 table filled at module init. There is no async or worker offload, so big buffers block the event loop. Multi-worker-thread use is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- The README's JavaScript comparison rows are labelled CRC-32C but use the `crc32` npm package, which computes IEEE CRC-32 (issue #82, still open). Only the native table-vs-SSE4.2 rows are a like-for-like comparison.
- Strings are UTF-8-encoded and copied into a std::string before hashing. Pass Buffers to avoid the copy and to get the CRC of the exact bytes you mean.
- The table fallback XORs raw 8-byte words into the CRC and indexes low byte first, which appears to assume little-endian hosts despite a source comment claiming it works on all platforms
- fast-crc32c 2.0.0 pins `sse4_crc32 ^6.0.1`, so most installs (\~146k/week on 6.0.1 vs \~3.2k on 7.0.0) never get the arm64 fix. index.js also checks `process.NODE_ENV` rather than `process.env.NODE_ENV`, so the debug exports (`sse42_crc`, `table_crc`, `hardware_support`) are always present.

## Known shortcomings

- Node.js native addon; numbers are from 2018 and ratios are derived. Baseline is its own slice-by-8 software CRC-32C, not a named library. Last commit 2022-03-27. \~952k npm downloads/month.
- Single-chain _mm_crc32_u64 loop is latency-bound (\~3x below the 3-way designs); arm64 uses the table path only; 6.0.1 breaks on M1. The JS rows labelled CRC-32C use an IEEE crc32 package (#82). CRC-32C only (not a zlib drop-in); node-gyp build at install, no prebuilt binaries; dead since 2022-03. Most downloads (\~146k/week) come via fast-crc32c pinning 6.0.1.

## Caveats and trade-offs

The current README numbers date from the 2018-05-29 README/benchmark rewrite (commit 304ac875), not 2013; the 2013 and 2016 README versions showed different numbers and 8GB RAM. No compiler or optimisation level is stated, and the CPU is given only as 'Intel Core i7'. The baseline is the project's own table-based fallback (Mark Adler's slice-by-8 code) inside the same addon, not zlib crc32() or another external library. Timings include Node N-API call overhead on small buffers. The implementation is C++ (src/\*.cpp), not C. The last commit on master is 2022-03-27 (the 2023-07-08 push date comes from a branch), so the repo is abandoned (&gt;3 years). The Voxer/sse4_crc32 fork was created 2020-02-26, not 2019.

Requires SSE4.2 hardware support (falls back to software CRC32 otherwise); this is CRC32C (Castagnoli polynomial) via the hardware CRC32 instruction, not the CRC-32/ISO-HDLC polynomial used by zlib's crc32(), so it is not a drop-in replacement for zlib's checksum without a polynomial change.

## Maintenance

Abandoned: the last master commit and the 7.0.0 npm release are 2022-03-27, with dependabot PRs left open since 2023. It still gets about 950k npm downloads a month, mostly the older 6.0.1 pulled in by fast-crc32c. It is MIT-licensed, and its few hundred lines of C++ are easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README performance section shows first-party timings of the native SSE4.2 CRC-32C against the addon's own table-based (slice-by-8) CRC-32C. The benchmark code is public (benchmark/\*.js), but the compiler and optimisation level are unstated and the CPU is given only as 'Intel Core i7' on a MacBook Air. That is not A, so C.
- **Verifier notes:** The numbers match the README exactly. The ratios were not stated on the page, so they are now marked as derived. Metadata checked via gh: MIT, 133 stars, not a fork, not archived; master last commit 2022-03-27 corrected from 2023-07-08. The language field should read C++ (not a correctable field here).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/anandsuresh/sse4_crc32>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/README.md>
  - <https://github.com/anandsuresh/sse4_crc32/commits/master/README.md>
  - <https://raw.githubusercontent.com/anandsuresh/sse4_crc32/cc78defa/README.md>
  - <https://raw.githubusercontent.com/anandsuresh/sse4_crc32/81b3dda8/README.md>
  - <https://raw.githubusercontent.com/anandsuresh/sse4_crc32/304ac875/README.md>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/binding.gyp>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/common.gypi>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/src/table.cpp>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/benchmark/single_fixed_size_buffer.benchmark.js>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/benchmark/multiple_random_size_buffers.benchmark.js>
  - <https://github.com/Voxer/sse4_crc32>
  - <https://api.npmjs.org/downloads/point/last-month/sse4_crc32>
- **Sources the enricher read:**
  - <https://github.com/anandsuresh/sse4_crc32>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/README.md>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/index.js>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/package.json>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/binding.gyp>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/common.gypi>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/Makefile>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/src/crc32c.cpp>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/src/sse42.cpp>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/src/sse42.h>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/src/table.cpp>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/.github/workflows/test.yml>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/test/index.test.js>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/benchmark/index.js>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/benchmark/single_fixed_size_buffer.benchmark.js>
  - <https://github.com/anandsuresh/sse4_crc32/blob/master/benchmark/multiple_random_size_buffers.benchmark.js>
  - <https://github.com/anandsuresh/sse4_crc32/issues>
  - <https://github.com/anandsuresh/sse4_crc32/issues/82>
  - <https://github.com/anandsuresh/sse4_crc32/issues/84>
  - <https://github.com/anandsuresh/sse4_crc32/issues/79>
  - <https://github.com/anandsuresh/sse4_crc32/issues/73>
  - <https://github.com/anandsuresh/sse4_crc32/pulls>
  - <https://github.com/anandsuresh/sse4_crc32/pull/89>
  - <http://engineering.voxer.com/2013/12/02/hardwareaccelerated-crc32-for-nodejs/>
  - <https://archive.org/wayback/available?url=engineering.voxer.com/2013/12/02/hardwareaccelerated-crc32-for-nodejs/>
  - <https://registry.npmjs.org/sse4_crc32>
  - <https://registry.npmjs.org/fast-crc32c/latest>
  - <https://api.npmjs.org/downloads/point/last-month/sse4_crc32>
  - <https://api.npmjs.org/downloads/point/last-month/fast-crc32c>
  - <https://api.npmjs.org/versions/sse4_crc32/last-week>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/anandsuresh/sse4_crc32`) · [data/wave7/enrich/raw/github_com_anandsuresh_sse4_crc32.json](../../../data/wave7/enrich/raw/github_com_anandsuresh_sse4_crc32.json) (enrichment confidence 0.65)

</details>
