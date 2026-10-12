# FSST (Fast Static Symbol Table)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Symbol-table string compressor with per-string random access; beats LZ4 on ratio and compression speed for short database strings.

| | |
|---|---|
| **Beats** | LZ4 1.8.1 |
| **Claimed result** | PVLDB 2020 paper Table 1 (22 dbtext sets, 8 MB files, single thread): FSST compression speed beats LZ4 on 21 of 22 sets (e.g. genome 1,307 vs 566 MB/s, uuid 1,113 vs 632, credentials 984 vs 439; LZ4 wins on hex 1,097 vs 944) with a higher compression factor on 21 of 22 (e.g. genome 3.32 vs 1.59, uuid 2.44 vs 1.55; LZ4 wins on urls 2.77 vs 2.16); paper text gives average factor 2.28x vs LZ4 1.70x. Decompression speed is mixed: FSST faster on 12 sets (e.g. genome 2,838 vs 1,126 MB/s, c_name 3,519 vs 2,960), LZ4 faster on 10 (e.g. hex 1,891 vs 1,546, email 2,388 vs 1,547) (counts derived from page data). |
| **Workload** | Compression of short strings (22 'dbtext' data sets, each an 8 MB file, single-threaded) with random access per string; LZ4 used in file-based mode. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-7900X 3.3 GHz (10 cores, AVX512), 32 GB RAM, Linux 4.18 |
| **Compiler and flags** | g++ 8.3.1, -O3 -march=native |
| **Adoption** | 546 stars; used in DuckDB, MonetDB |
| **Last commit** | 2026-04-06 |
| **Links** | [repository](https://github.com/cwida/fsst) · [benchmark](https://github.com/cwida/fsst/blob/master/fsstcompression.pdf) |

## Verdict

In the PVLDB 2020 paper (g++ 8.3.1 -O3 -march=native, Intel i9-7900X with AVX-512, single thread), FSST against LZ4 1.8.1 in file mode on 22 8 MB dbtext sets compressed faster on 21 sets and to a higher ratio on 21 sets (paper: 34% better average factor, 60% higher compression speed), while decompression speed was about equal on average (FSST faster on 12 sets, LZ4 on 10). The replication package and corpus are in the repo's paper/ directory.

## Use it when

- Columnar or row stores holding many short strings (under about 100 bytes) with many distinct values, where dictionary encoding does not pay off and LZ4 on single values expands the data (paper: LZ4 compression factor 0.46 on 16-byte blocks).
- Selective scans and point lookups that need one value from a compressed block; FSST output rate does not depend on selectivity, while LZ4-block must decode the whole block (paper Figure 5).
- Machine-generated text such as UUIDs, emails, URLs, genome strings and TPC-H comments, where the paper measures the biggest ratio gains (genome 3.32x vs LZ4 1.59x).
- Joins, aggregations or network shuffles that can keep strings compressed and compare them for equality without decoding.
- x86-64 servers with AVX-512, where the SIMD encoder is enabled at runtime and is 2.5x faster than the scalar encoder (paper Table 2).

## Skip it when

- General byte streams, binaries, large files or archives: on Silesia FSST is 25% worse than LZ4 on the binary files, and on large XML/JSON its ratio is 2-2.5x worse than LZ4 (paper section 6.3). Use LZ4 or zstd for those.
- Decompression-bound pipelines: average decompression speed is about equal to LZ4, and LZ4 wins on 10 of 22 dbtext sets (for example hex, email).
- ARM or other non-AVX-512 machines expecting the paper's compression speed: issue #39 (Aug 2025) reports about 112 MB/s on an Apple M1 against about 900 MB/s in the paper, with no maintainer reply visible.
- Workloads whose value distribution shifts away from the training sample: the table is static per block, and unseen bytes are escaped at 2 bytes each, so mismatched data can double in size.
- Projects that need tagged releases or a stable format contract: there is no release process yet (issue #34 open) and the format version constant is still 20190218.

## How it is fast

Table construction runs five rounds of bottom-up symbol generation on a 16 KB sample (sample fraction 8/128 rising to 128/128), keeping the highest-gain symbols and pair concatenations. Encoding finds the longest match with a 'lossy perfect hash' table (1024 buckets keyed on the next 3 bytes) plus a 65,536-entry shortCodes[A][B] array for 1-2 byte symbols, selected with a conditional move and no loops or branches. On AVX-512 CPUs a 'meatgrinder' kernel encodes 24 strings at once (8 lanes, unrolled 3x) using gather/scatter and compress-store/expand-load lane refills; the paper reports about 4.1 cycles/byte on an i9-7900X. Decoding is a table lookup that stores 8 bytes unaligned per code, checking 4 codes at a time for escapes with a SWAR test.

## Compared with alternatives

Pick FSST over LZ4, zstd or LZAV when values are short strings that must be decoded one at a time or compared while compressed; those siblings are block or stream compressors that need kilobytes of context to compress well. For whole files, logs or binary data, LZ4, zstd or ZXC are the better fit.

## Integration

| | |
|---|---|
| **Form** | static lib (libfsst.cpp plus fsst_avx512.cpp built with CMake); the decoder is an inline function in fsst.h |
| **Dependencies** | none beyond the C++ standard library (CMake links Threads only for the command-line tool) |
| **Minimum toolchain** | C++17 (CMakeLists sets CMAKE_CXX_STANDARD 17); public header is C-compatible via extern "C"; GCC, Clang and MSVC paths exist |
| **Platforms** | README: 64-bit x86 on Linux, Windows and macOS, plus macOS arm64; AVX-512 encoder only when compiled with __AVX512F__ and detected via CPUID at runtime, scalar elsewhere; 32-bit builds define NONOPT_FSST; big-endian handled with byte swaps |
| **Thread safety** | Encoder objects are not shareable: use fsst_duplicate() to make one per thread. The decoder struct is read-only and the header states it can be shared between decompressing threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- CMakeLists adds -march=native whenever the compiler accepts it, so a default build is tied to the build machine's CPU; set flags yourself for distributed binaries.
- fsst_compress() returns how many strings fit in the output buffer, which can be fewer than requested; the first string needs at least 7+2\*length bytes of space. Issue #30 (Feb 2025, closed via PR #32) fixed an AVX-512 path that over-reported this count.
- fsst_decoder() leaves the version field of fsst_decoder_t uninitialized (issue #50, opened 2026-09-25, still open); decoding is unaffected, but writing the struct to disk gives non-reproducible bytes.
- Past sanitizer and robustness issues were reported and closed: makeSample buffer overflow (#17), out-of-bounds reads (#9), UBSan errors (#4), and an endless loop in buildSymbolTable on 32-bit ARM with GCC (#37).

## Known shortcomings

- Upgraded B to A: the paper/ directory holds the replication package (Makefile, compare.sh, dbtext corpus) and the PVLDB paper states g++ 8.3.1 -O3 -march=native on an i9-7900X. Compression is faster on 21 of 22 data sets, but decompression is mixed (LZ4 faster on 10 of 22).
- Issue #39 (Aug 2025, no maintainer reply): Apple M1 compresses at about 112 MB/s against about 900 MB/s in the paper; the AVX-512 encoder exists only on x86 with an __AVX512F__ build. Paper section 6.3: XML/JSON ratio 2-2.5x worse than LZ4, binaries 25% worse. No releases (#34); open #50 (2026-09-25): fsst_decoder() leaves the version field uninitialized; CMake forces -march=native.

## Caveats and trade-offs

Peer-reviewed (PVLDB vol 13 no 12, 2020); numbers read from the paper PDF checked into the repo (via raw.githubusercontent.com). LZ4 version is old (1.8.1) with g++ 8.3.1. Decompression is on par with LZ4, slower on 10 of 22 sets; the main win is compression ratio, compression speed and per-string random access. File mode is LZ4's best case per the paper. Replication package (paper/ directory with dbtext corpus and Makefile) is in the repo; it needs Linux perf counters and LZ4 1.8.1 on PATH.

Strings only (symbol table of up to 8-byte symbols mapped to 1-byte codes); static table per block, random access to single strings without block decode; not a general-purpose byte-stream compressor. Best on short-string columns, ratio gain largest on machine-generated IDs.

## Maintenance

Active (last commit 2026-04-06; 546 stars), MIT-licensed and small (libfsst.cpp and libfsst.hpp total about 1,100 lines, plus the AVX-512 kernel), so it is easy to vendor, but it has no tagged releases and a few open hygiene issues (#49, #50).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B: the PVLDB 2020 paper (fsstcompression.pdf) states g++ 8.3.1 -O3 -march=native, LZ4 1.8.1 and an i9-7900X, and the repo's paper/ directory holds the replication package (Makefile with 'make experiments', compare.sh post-processing Table 1, linetest.cpp, filtertest.cpp, and the dbtext corpus), so code, compiler, flags and CPU are all public.
- **Verifier notes:** All quoted Table 1 numbers match the paper. Tier raised to A because the replication package and dbtext corpus are in the repo's paper/ directory.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier read the PVLDB 2020 PDF in the repo; enricher
- **Pages the verifier opened:**
  - <https://github.com/cwida/fsst>
  - <https://github.com/cwida/fsst/commits/master>
  - <https://github.com/cwida/fsst/tree/master/paper>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/fsstcompression.pdf>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/README.md>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/cwida/fsst>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/README.md>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/fsst.h>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/libfsst.hpp>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/libfsst.cpp>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/fsst_avx512.cpp>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/cwida/fsst/HEAD/fsstcompression.pdf>
  - <https://github.com/cwida/fsst/issues?q=is%3Aissue>
  - <https://github.com/cwida/fsst/issues/39>
  - <https://github.com/cwida/fsst/issues/50>
  - <https://github.com/cwida/fsst/issues/30>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/cwida/fsst`) · [data/wave9/enrich/raw/github_com_cwida_fsst.json](../../../data/wave9/enrich/raw/github_com_cwida_fsst.json) (enrichment confidence 0.85)

</details>
