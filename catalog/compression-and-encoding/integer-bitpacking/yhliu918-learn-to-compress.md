# LeCo (Learn-to-Compress)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · 🟡 stale

> Research codec (SIGMOD'24): per-block linear regression plus bit-packed residuals for integer columns; better ratio than FOR and Elias-Fano, faster random access than Delta.

| | |
|---|---|
| **Beats** | Frame of Reference (FOR), Delta encoding (fixed and variable partitions), Elias-Fano (thirdparty succinct) and rANS, all built inside the repo; Parquet default encoding and RocksDB default index blocks in the system experiments |
| **Claimed result** | Technical report (SIGMOD'24 version): on nine integer data sets LeCo 'achieves a Pareto improvement'; versus FOR and Elias-Fano it improves compression ratio by up to 81% with comparable decompression and random-access speed; versus Delta encoding it is 'an order of magnitude faster in random access' with competitive or better ratio. In Parquet, a filter-scan query runs up to 3.9x faster and bitmap-scan up to 12.6x (up to 5.6x versus FOR); RocksDB throughput rises 16%. Compression throughput (Table 1, GB/s): FOR 0.81, Elias-Fano 0.58, Delta-fix 1.04, Delta-var 0.04, LeCo-fix 0.78, LeCo-var 0.02. |
| **Workload** | Lightweight compression of integer columns (fixed-length FOR/Delta/LeCo and variable-length Delta/LeCo variants) measured by compression ratio and random access speed, then integrated into Arrow/Parquet and RocksDB index blocks. |
| **Metric** | other |
| **Hardware** | Intel Xeon (Ice Lake) Platinum 8369B @ 2.70GHz, 32GB DRAM, single thread (microbenchmark); 4x Xeon Platinum 8269CY @ 2.50GHz for the system experiments |
| **Compiler and flags** | -O3 -march=native, C++17, CMake Release build (CMakeLists.txt); compiler not named (README requires Ubuntu 20.04.4 LTS) |
| **Adoption** | 17 stars, 3 forks |
| **Last commit** | 2024-03-26 |
| **Links** | [repository](https://github.com/yhliu918/Learn-to-Compress) · [benchmark](https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/c5ea4ef5eeea7217a2d13955e879b94eaf5a3d83/technical_report.pdf) |

## Verdict

The SIGMOD'24 technical report (read from repo history) runs single-threaded on a Xeon Platinum 8369B (Ice Lake) at -O3 -march=native over nine integer datasets. Against FOR and Elias-Fano, LeCo improves compression ratio by up to 81% at comparable decode and random-access speed; it is about 10x faster than Delta on random access; and in Arrow/Parquet scans it is up to 3.9x faster (filter) and 12.6x (bitmap). The published abstract (WebSearch snippet only) says up to 5.2x in Arrow and +16% RocksDB throughput. All baselines are in-repo implementations, not FastPFor or simdcomp.

## Use it when

- Read-mostly integer columns with strong serial correlation (sorted keys, monotone IDs, timestamps, index offsets) where compression ratio and point lookups matter more than encode speed.
- You want O(1) random access into a compressed column and Delta encoding's prefix-sum cost is the bottleneck (the paper reports an order of magnitude faster random access than Delta).
- Columnar or LSM index-block prototypes: the paper's Arrow/Parquet filter and bitmap scans (up to 3.9x in the technical report, 5.2x in the published abstract) and a 16% RocksDB throughput gain come from the companion repos.
- Research or re-implementation: the idea (regression model plus fixed-width residuals per block) is simple to port into your own codec.

## Skip it when

- Production use: there is no LICENSE file, so it is all rights reserved by default and cannot legally be copied (the vendored FastPFor, ALEX, ART, stx-btree and FSST code carry their own licences).
- Fast encoding: LeCo-fix compresses slightly slower than FOR (0.78 vs 0.81 GB/s) and LeCo-var about 40x slower (0.02 GB/s).
- Random, high-entropy or non-monotone integers: residuals then gain nothing over FOR, and a block whose residual needs the full type width is stored raw.
- SIMD bulk decode throughput: the siblings FastPFor, simdcomp and TurboPFor decode at several GB/s with explicit SIMD; LeCo decode is scalar 64/128-bit shift loops.
- Platforms other than x86-64 Ubuntu 20.04: setup.sh uses apt and sudo symlinks into /usr/include, src/CMakeLists.txt adds -msse4.1/-mssse3 unconditionally, and everything builds with -march=native.

## How it is fast

It is a learned generalisation of Frame-of-Reference. FOR stores value minus block minimum; LeCo stores value minus a least-squares regression prediction, recentred so that residuals are symmetric, so on near-linear data (sorted keys, timestamps, IDs) the residual bit width falls far below FOR's. Random access costs one multiply-add plus one unaligned 64-bit load and mask, against Delta's prefix sum over the block. The variable-length variant (LeCo-var) adds cost-model-driven partitioning, which explains its 0.02 GB/s compression throughput. There is no explicit SIMD; the build depends on -O3 -march=native auto-vectorisation.

## Compared with alternatives

Pick it over FastPFor, simdcomp or TurboPFor only when the data is serially correlated, you need constant-time random access, and ratio beats raw SIMD decode speed. ds2i's partitioned Elias-Fano is the closest licensed alternative for sorted sequences. Treat LeCo as a design to re-implement, since the repo has no licence.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Eigen3, GMP/gmpxx, Snappy, Boost (setup.sh installs libboost-all-dev), vendored FSST; CMake 3.16+ (setup.sh upgrades to 3.22) |
| **Minimum toolchain** | C++17 (CMake), GCC with __int128 support; tested only on Ubuntu 20.04.4 LTS; compiler version not named |
| **Platforms** | x86-64 only in practice (-msse2/-msse3/-mssse3/-msse4.1 always on, -march=native); little-endian assumed by the raw uint64 reinterpret loads |
| **Thread safety** | not documented; Leco_int keeps per-instance state (blocks, block_size, mul_add_diff_set), so use one codec object per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Encoder/decoder flag mismatch (source reading, not run): encodeArray8_int stores a block raw only when max_bit == sizeof(T)\*8, but decodeArray8 treats any maxerror &gt;= sizeof(T)\*8-1 as raw and memcpys. A block whose residual width is exactly 63 bits (uint64) or 31 bits (uint32) is therefore written as model plus packed residuals but bulk-decoded as raw bytes, giving wrong output; randomdecodeArray8 checks == sizeof(T)\*8 and stays correct.
- Benchmark timing caveat: CMakeLists.txt overrides CMAKE_CXX_FLAGS_RELEASE with "-O3 -march=native", which drops CMake's default -DNDEBUG. The #ifndef NDEBUG verification loops in experiments/\*_fix_template.cpp then run inside the timed decode-all and random-access regions, adding a full compare pass and an extra random DRAM read of the original array per lookup for every codec. Absolute ns figures are inflated and ratios between codecs are compressed, unless the paper runs used other flags (not documented).
- Unaligned, type-punned 64/128-bit loads (reinterpret_cast&lt;const uint64_t\*&gt;/uint128_t\*) at offsets such as 17 bytes into a block. The word-at-a-time reader can load up to one word past the packed residuals of an exact-size realloc'd buffer: this is UB, and ASan/UBSan would flag it, though it works on x86.
- Predictions are double-precision (long long)(theta0 + theta1\*i), so for uint64 values above 2^53 accuracy depends on encoder and decoder rounding identically under -march=native (FMA contraction); unsigned/signed mixing in the encoder (uint64 data compared with int64 predictions) forces raw fallback when predictions go negative.

## Known shortcomings

- Upgraded C to B on the technical report found in the repo history (commit c5ea4ef, technical_report.pdf: Xeon Platinum 8369B, -O3 -march=native, compiler not named). No license, so reference.
- Bug found by reading source (not run): decodeArray8 treats maxerror &gt;= sizeof(T)\*8-1 as raw, but the encoder stores raw only at max_bit == 64, so blocks needing exactly 63 bits (31 for uint32) decode wrong; random access stays correct. Timing caveat: CMakeLists sets CMAKE_CXX_FLAGS_RELEASE to -O3 -march=native, which drops -DNDEBUG, so verification loops run inside the timed decode and random-access regions for every codec (shared harness, so tier B kept). Unaligned type-punned 64/128-bit loads with a possible one-word overread; doubles used for uint64 predictions. No LICENSE (vendored FastPFor/ALEX/ART/stx-btree/FSST carry their own). Ubuntu 20.04 x86-only build.

## Caveats and trade-offs

No license file in the repo (usability reference). Baselines are FOR, Delta, Elias-Fano and rANS implemented or vendored inside the repo, not FastPFor, simdcomp or Simple8b. The main win is compression ratio at comparable decode speed, plus random-access speed over Delta; LeCo-fix compression throughput is slightly below FOR (0.78 vs 0.81 GB/s) and LeCo-var is about 40x slower to compress than FOR (0.02 GB/s). Numbers come from the technical report that was deleted from the repo on 2023-12-22 (commit 15d679e) and read from history; the published SIGMOD version was not opened (ACM and arXiv blocked). Compiler not named.

Learned (regression-based) model per segment instead of a fixed frame, so it adds model parameters and training/partitioning cost at encode time. Targets immutable columnar data with random access, not streaming SIMD bit packing.

## Maintenance

Stale since 2024-03-26 and unlicensed (reference only): useful as the reproducible artefact of a peer-reviewed paper, not as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the SIGMOD'24 paper's technical report, recovered from the repo history (technical_report.pdf at commit c5ea4ef), benchmarks LeCo against FOR, Elias-Fano, Delta and rANS on a stated Intel Xeon Platinum 8369B with public benchmark code (benchmark/fix_int, benchmark/auto_int) and -O3 -march=native in CMakeLists.txt; the compiler is never named, so not A.
- **Verifier notes:** Tier raised to B from a peer-reviewed paper version found in the repo's git history. Metadata matches: 17 stars, 3 forks, no license, last commit 2024-03-26 (stale). The Parquet 3.9x and RocksDB 16% claims are end-to-end system results, not the integer microbenchmark.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; peer-reviewed paper (SIGMOD 2024)
- **Pages the verifier opened:**
  - <https://github.com/yhliu918/Learn-to-Compress>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/README.md>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/CMakeLists.txt>
  - <https://github.com/yhliu918/Learn-to-Compress/commits>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/c5ea4ef5eeea7217a2d13955e879b94eaf5a3d83/technical_report.pdf>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/README.md>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/scripts/setup.sh>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/benchmark/fix_int_benchmark.py>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/benchmark/auto_int_benchmark.py>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/experiments/leco_int_fix_template.cpp>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/experiments/FOR_int_fix_template.cpp>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/headers/piecewise_fix_integer_template.h>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/headers/bit_read.h>
  - <https://raw.githubusercontent.com/yhliu918/Learn-to-Compress/HEAD/LICENSE>
  - <https://github.com/yhliu918/Learn-to-Compress/tree/main/headers>
  - <https://github.com/yhliu918/Learn-to-Compress/tree/main/experiments>
  - <https://github.com/yhliu918/Learn-to-Compress/issues?q=is%3Aissue>
  - <https://github.com/yhliu918?tab=repositories>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/yhliu918/learn-to-compress`) · [data/wave9/enrich/raw/github_com_yhliu918_learn_to_compress.json](../../../data/wave9/enrich/raw/github_com_yhliu918_learn_to_compress.json) (enrichment confidence 0.7)

</details>
