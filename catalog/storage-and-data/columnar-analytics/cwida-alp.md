# ALP (Adaptive Lossless Floating-Point Compression)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Reference C++ primitives for ALP, a lossless double/float column encoding that decodes 17-66x faster than Zstd, Gorilla, Chimp and Patas.

| | |
|---|---|
| **Beats** | Zstd, Gorilla, Chimp, Chimp128, Patas (existing lightweight and general-purpose floating-point compressors) |
| **Claimed result** | SIGMOD'24 paper Table 5 (Ice Lake micro-benchmark, tuples per cycle, averaged over all datasets): ALP compresses 14x faster than Zstd, 9x faster than Gorilla, 12x faster than Chimp and Chimp128, 8x faster than Patas, 47x faster than Elf and 251x faster than PDE. It decompresses 26x faster than Zstd, 55x than Gorilla, 66x than Chimp, 65x than Chimp128, 17x than Patas, 215x than Elf and 7x than PDE. Figure 1: '1-2 orders of magnitude faster in [de]compression than all competing schemes'. End-to-end in Tectorwise (Table 6, Figure 6): SCAN and SUM on ALP beat every other scheme and even uncompressed data. City-Temp compression is 4x faster than Patas and 7x faster than Gorilla, and Zstd is 11x slower. Compression ratio (Table 4): ALP averages 21.7 bits/value against Zstd's 20.6, so Zstd is slightly better on average; ALP beats all the other schemes. |
| **Workload** | Single/multi-threaded (1/8/16 thread) SCAN and SUM queries over compressed double/float columns from real-world datasets (food_prices, city_temperature, bitcoin_transactions, gov26, nyc29), plus separate compression-ratio benchmarks over the Public BI float/double corpus. |
| **Metric** | throughput |
| **Hardware** | Main results (Figure 1, Table 5, end-to-end Figure 6 and Table 6) on Intel Ice Lake Xeon 8375C at 3.5 GHz (AWS i4i.4xlarge; the end-to-end run used 16 cores / 32 SMT and 256 GB RAM). Decompression was also run on AMD EPYC 7R13 (Zen3), Apple M1, AWS Graviton2 (Neoverse-N1) and Graviton3 (Paper Table 3). |
| **Compiler and flags** | clang++ (the root CMakeLists allows only Clang; toolchain/i4i_4xlarge.cmake uses /usr/bin/clang++; version not stated). -O3 per the paper. bench_end_to_end CMake adds -O3 -march=native -mtune=native -mavx512dq. Scalar variant: -O3 -fno-slp-vectorize -fno-vectorize. g++ is used only to build the PDE baseline. |
| **Adoption** | 234 stars; integrated into DuckDB, KuzuDB, and liquid-cache |
| **Last commit** | 2025-10-16 |
| **Links** | [repository](https://github.com/cwida/ALP) · [benchmark](https://ir.cwi.nl/pub/33334/33334.pdf) |

## Verdict

In the authors' SIGMOD 2024 micro-benchmark (Ice Lake Xeon 8375C on AWS i4i.4xlarge, clang -O3, one L1-resident 1,024-value vector timed 300K times, Zstd level 3 given about 1 MB), ALP averaged 0.487 values/cycle compressing and 2.609 decompressing: 8-251x faster compression and 7-66x faster decompression than Zstd (0.035/0.101), Gorilla (0.052/0.047), Chimp (0.042/0.039), Patas (0.060/0.157) and PDE (0.002/0.387), at 21.7 bits/value against Zstd's 20.6 (ratios computed from a size formula, not written bytes). Inside DuckDB 0.10 the gain shrank to 2-4x faster decompression than Patas, and a query over ALP data (0.020 s) was still slower than over uncompressed data (0.012 s).

## Use it when

- You are building a columnar format, database or time-series store and need a float codec whose unit is one 1,024-value vector, so scans can skip or decode single vectors. Zstd, by contrast, must decompress a whole block. The paper's example is 32 vectors of 8 KB inside a 256 KB block.
- Doubles that originate as fixed- or low-precision decimals, such as prices, sensor readings, temperatures and stock ticks. Examples: City-Temp takes 10.7 bits/value against 16.2 for Zstd and 59.7 for Gorilla. Averaged over the 13 time-series datasets, ALP takes 16.4 bits/value against 17.2 for Zstd.
- Scan- or aggregate-heavy analytics where decode CPU dominates. In the authors' Tectorwise run on City-Temp (Ice Lake), single-threaded SCAN over ALP ran at 1.337 tuples/cycle against 0.565 uncompressed and 0.044 for Zstd, and SUM at 0.233 against 0.197 uncompressed.
- Replacing Gorilla, Chimp, Chimp128 or Patas in an existing lightweight float slot. ALP beat Chimp128 and PDE on compression ratio on 27 of 30 datasets and is faster in both directions. DuckDB made exactly this swap in v0.10.
- Mixed hardware fleets: the decoder is plain C++ that auto-vectorizes. The paper measured it on Ice Lake (AVX-512), Zen3 (AVX2), Apple M1 and Graviton2/3 (NEON), and Ice Lake was fastest.

## Skip it when

- You want a compress(buf)/decompress(buf) library like zstd. There is no container or stream format, no bitstream specification (issue #32, left to contributors), and no tags or releases (issue #43). Use FastLanes, or an engine that already ships ALP: DuckDB picks it automatically for FLOAT/DOUBLE at checkpoint since 0.10, and ClickHouse has it as a beta codec behind enable_alp_codec since 26.9.
- High-precision 'real' doubles with no decimal structure, such as radians, simulation output or ML values. POI-lat and POI-lon fall back to ALP_rd at 55.5 and 56.4 bits/value (about 1.15x), worse than Zstd's 48.1 and 53.1. ALP_rd is also about 3x slower to compress and 4x slower to decompress than regular ALP.
- Columns full of exact repeats. On CMS/1, Medicare/1 and NYC/29 ALP needs 35.7, 39.4 and 40.4 bits/value, against 24.5, 28.7 and 20.5 for Zstd and 28.2, 32.3 and 28.7 for Chimp128. You need your own dictionary or RLE stage in front; the paper's cascade reaches 33.1, 35.7 and 24.7.
- Cold storage where ratio beats speed. Across all 30 datasets Zstd level 3 averages 20.6 bits/value against 21.7 for ALP alone. ALP only wins (18.8) when cascaded with dictionary or RLE, which this repo does not provide.
- float16, bfloat16 or fp8 data, or GPU decoding. Reduced-precision types are unsupported (issue #38), and the GPU kernel PR #23 has been open and WIP since October 2024.

## How it is fast

Most real-world doubles began as decimals. ALP multiplies each value by 10^e and 10^-f and rounds with the branch-free magic-number add/subtract trick (2^52+2^51 for double). It keeps the integer only if decoding reproduces the exact bits; values that fail are stored as exceptions and patched in afterwards. The int64s are frame-of-reference bit-packed in FastLanes' interleaved layout and decoded by a generated, branch-free, auto-vectorized kernel per bit width that fuses unpacking with the multiply (a median 40% gain from fusing in the paper). A two-level sample keeps the (e,f) search off the hot path: 8 vectors × 32 values per 102,400-value row group shortlist at most 5 pairs, and each vector tries only those, stopping after two worse ones; non-decimal data switches to ALP_rd, which dictionary-encodes the top 1-16 bits of each value into at most 8 entries and bit-packs the rest.

## Compared with alternatives

Pick this repo when you want only the float/double codec to embed in your own engine or format. Choose FastLanes (same CWI group) if you want ALP packaged with integer and string encodings and a file reader/writer, and Vortex if you want a Rust columnar format that ships its own ALP encoding. Over BtrBlocks, whose float scheme is PseudoDecimals (PDE), ALP measured about 7x faster decompression, 251x faster compression and a 31% better average ratio in the paper's benchmark.

## Integration

| | |
|---|---|
| **Form** | shared lib (the CMake target ALP is built SHARED from headers in include/ plus generated FastLanes sources in src/); in practice teams vendor or port the source |
| **Dependencies** | none for the library (C++17 standard library only). Tests and benchmarks fetch googletest v1.13.0. The paper-reproduction harness also needs Boost, bzip2, OpenSSL, libcurl, g++ (for PDE), Java 8 with Maven (for Elf), and pandas/seaborn for plots. |
| **Minimum toolchain** | C++17; Clang only (CMake stops with 'Only Clang is supported!' and no minimum Clang version is stated); CMake 3.22+; on Linux, clang-tidy must also be installed unless -DALP_ENABLE_CLANG_TIDY=OFF |
| **Platforms** | x86-64 (explicit AVX-512 exception compaction when built with AVX-512F; otherwise scalar or auto-vectorized code) and aarch64 (tested on Graviton2/3 and Apple M1). CI runs on ubuntu-latest and macos-latest. Windows is not documented. |
| **Thread safety** | Encoder scratch arrays were plain function-level statics, shared across threads, until PR #42 made them thread_local on 2025-10-16 (issue #41); older copies race under parallel encoding. alp::state holds mutable per-row-group data (std::vector, std::unordered_map), so give each thread its own. Decode primitives take all parameters explicitly. |
| **Drop-in for the baseline** | no |

## Gotchas

- src/CMakeLists.txt reads the build host's /proc/cpuinfo and adds -mavx512dq, or -march=native on other x86 hosts, as PUBLIC compile options. The flags reach your targets, and the binaries only run on CPUs like the build machine. Issue #33 was a macOS runtime failure the maintainer put down to AVX-512 support that the CPU did not actually have.
- Vector and row-group geometry is compiled into config.hpp: 1,024 values per vector and 100 vectors (102,400 values) per row group. You must pad the last partial vector yourself; PRIMITIVES.md suggests the first non-exception value. In issue #24, a 307,200-value column crashed on the last row group (vector subscript out of range); the maintainer's workaround was to re-init every 100 vectors or edit ROWGROUP_SIZE.
- Only the scalar fused falp kernel (one 1.6 MB generated file) is built into the library. The SSE, AVX2, AVX-512, NEON, SVE and WASM falp variants declared in falp.hpp live in publication/source_code/generated and are not part of the ALP target, so calling them fails to link unless you add those sources. PRIMITIVES.md is also stale: it calls fused falp double-only, though a float overload now exists.
- On AMD Zen 4, the AVX-512 path's _mm512_mask_compressstoreu_pd (VPCOMPRESSPD) is microcoded and slower than scalar code (open issue #45, August 2026, no reply). encode_simdized also casts large finite doubles to int64 without a range check (encode_value&lt;false&gt;). That is the same undefined behaviour UBSan flagged in DuckDB's port (duckdb#24634).

## Known shortcomings

- Zstd compresses slightly better (20.6 vs 21.7 bits/value); the 14x/26x vs Zstd and 55x decode vs Gorilla are from Table 5 on a Xeon 8375C; clang-only build.
- Primitives only: no byte-level API, stream format, spec or releases (compressor.hpp was deleted in 2024-09). The library ships only the scalar kernels; the SIMD kernels live in publication/ and fail to link from the library. CMake is Clang-only, needs clang-tidy on Linux and exports -march=native/-mavx512dq publicly, so binaries are not portable.
- Loses on POI lat/lon (ALP_rd) and many-repeat columns (NYC/29 40.4 vs 20.5 bits/value). In DuckDB 0.10 it was only 2-4x faster than Patas and an ALP query took 0.020 s vs 0.012 s uncompressed. Zen 4 VPCOMPRESSPD slowdown open (#45); an encoder race was fixed only in 2025-10; an unchecked int64 cast is UB (as in duckdb#24634).

## Caveats and trade-offs

The headline numbers are the authors' own (SIGMOD 2024), backed by the SIGMOD ARI package with all three badges (including Results Reproduced) and the SIGMOD Best Artifact Award. The paper is openly available at ir.cwi.nl/pub/33334/33334.pdf and bronze-OA at ACM. Zstd matches or slightly beats ALP's compression ratio on average (20.6 vs 21.7 bits/value); ALP only wins on ratio when cascaded with other lightweight encodings. The ARI report says the Figure 6 plotting script is missing. The repo CSV publication/end_to_end_bench/result holds raw cycle counts, not ratios.

Targets IEEE754 float/double columns specifically, not general-purpose compression; decimal-heavy data benefits most, high-entropy/high-precision random values compress less well and fall back to a dictionary+FoR split scheme.

## Maintenance

Quiet reference repo: the last commit was the thread_local fix on 2025-10-16, with no tags or releases, 234 stars, and 9 open issues including an unanswered Zen 4 slowdown. It is MIT-licensed and small enough to vendor, but DuckDB and ClickHouse each maintain their own implementations rather than depending on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The SIGMOD 2024 paper (open copy at ir.cwi.nl) compares ALP with Zstd, Gorilla, Chimp, Chimp128, Patas, PDE and Elf. It names the CPU model (Intel Xeon 8375C Ice Lake, Table 3) and the -O3 flags, and the repo sets the compiler (toolchain/i4i_4xlarge.cmake uses clang++, and CMake allows only Clang). The benchmark code is public: publication/source_code/bench_speed, bench_end_to_end (-O3 -march=native -mavx512dq) and bench_compression_ratio, run by publication/script/master_script.sh. That meets tier A.
- **Verifier notes:** The record's claim that the paper is paywalled with no preprint is wrong: the CWI repository hosts the full PDF, and I read it. I kept tier A. I replaced the vague claimed_speedup with the Table 5 multipliers and softened the compression-ratio claim against Zstd. The raw end-to-end CSV agrees with the paper: summed cycles show SCAN on ALP about 18-20x cheaper than on Zstd with one thread (derived from page data).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cwida/ALP>
  - <https://github.com/cwida/ALP/blob/main/publication/end_to_end_bench/result>
  - <https://raw.githubusercontent.com/cwida/ALP/main/publication/end_to_end_bench/result_cleaned>
  - <https://github.com/cwida/ALP/blob/main/BENCHMARKING.md>
  - <https://github.com/cwida/ALP/blob/main/availability_reproducibility_initiative_report.md>
  - <https://github.com/cwida/ALP/blob/main/toolchain/i4i_4xlarge.cmake>
  - <https://github.com/cwida/ALP/blob/main/publication/source_code/bench_end_to_end/CMakeLists.txt>
  - <https://github.com/cwida/ALP/blob/main/publication/script/run_end_to_end.sh>
  - <https://github.com/cwida/ALP/blob/main/publication/results/i4i_4xlarge/README.md>
  - <https://dl.acm.org/doi/pdf/10.1145/3626717>
  - <https://api.crossref.org/works/10.1145/3626717>
  - <https://api.openalex.org/works/doi:10.1145/3626717>
  - <https://ir.cwi.nl/pub/33334/33334.pdf>
- **Sources the enricher read:**
  - <https://github.com/cwida/ALP>
  - <https://github.com/cwida/ALP/blob/main/CMakeLists.txt>
  - <https://github.com/cwida/ALP/blob/main/src/CMakeLists.txt>
  - <https://github.com/cwida/ALP/blob/main/src/falp.cpp>
  - <https://github.com/cwida/ALP/blob/main/PRIMITIVES.md>
  - <https://github.com/cwida/ALP/blob/main/BENCHMARKING.md>
  - <https://github.com/cwida/ALP/blob/main/how_to_benchmark_your_dataset.md>
  - <https://github.com/cwida/ALP/blob/main/availability_reproducibility_initiative_report.md>
  - <https://github.com/cwida/ALP/blob/main/include/alp.hpp>
  - <https://github.com/cwida/ALP/blob/main/include/alp/config.hpp>
  - <https://github.com/cwida/ALP/blob/main/include/alp/common.hpp>
  - <https://github.com/cwida/ALP/blob/main/include/alp/constants.hpp>
  - <https://github.com/cwida/ALP/blob/main/include/alp/encoder.hpp>
  - <https://github.com/cwida/ALP/blob/main/include/alp/decoder.hpp>
  - <https://github.com/cwida/ALP/blob/main/include/alp/rd.hpp>
  - <https://github.com/cwida/ALP/blob/main/include/alp/sampler.hpp>
  - <https://github.com/cwida/ALP/blob/main/include/alp/storer.hpp>
  - <https://github.com/cwida/ALP/blob/main/include/alp/falp.hpp>
  - <https://github.com/cwida/ALP/blob/main/test/test_alp_sample.cpp>
  - <https://github.com/cwida/ALP/blob/main/.github/workflows/CI.yaml>
  - <https://github.com/cwida/ALP/blob/main/toolchain/i4i_4xlarge.cmake>
  - <https://github.com/cwida/ALP/blob/main/toolchain/arm64.cmake>
  - <https://github.com/cwida/ALP/blob/main/toolchain/m1.cmake>
  - <https://github.com/cwida/ALP/blob/main/publication/results/i4i_4xlarge/README.md>
  - <https://github.com/cwida/ALP/commits/main>
  - <https://github.com/cwida/ALP/issues?q=is%3Aissue>
  - <https://github.com/cwida/ALP/pulls?q=is%3Apr>
  - <https://github.com/cwida/ALP/issues/45>
  - <https://github.com/cwida/ALP/issues/43>
  - <https://github.com/cwida/ALP/issues/41>
  - <https://github.com/cwida/ALP/issues/40>
  - <https://github.com/cwida/ALP/issues/38>
  - <https://github.com/cwida/ALP/issues/36>
  - <https://github.com/cwida/ALP/issues/35>
  - <https://github.com/cwida/ALP/issues/33>
  - <https://github.com/cwida/ALP/issues/32>
  - <https://github.com/cwida/ALP/issues/24>
  - <https://github.com/cwida/ALP/issues/3>
  - <https://ir.cwi.nl/pub/33334/33334.pdf>
  - <https://github.com/duckdb/duckdb/issues/24634>
  - <https://duckdb.org/2024/02/13/announcing-duckdb-0100.html>
  - <https://github.com/ClickHouse/ClickHouse/blob/master/src/Compression/CompressionCodecALP.cpp>
  - <https://github.com/ClickHouse/ClickHouse/pull/116337>
  - <https://github.com/vortex-data/vortex/tree/develop/encodings>
  - <https://github.com/cwida/FastLanes>
  - <https://hn.algolia.com/api/v1/search?query=ALP%20floating-point%20compression&tags=story>
  - <https://news.ycombinator.com/item?id=49051355>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cwida/alp`) · [data/wave6/enrich/raw/github_com_cwida_alp.json](../../../data/wave6/enrich/raw/github_com_cwida_alp.json) (enrichment confidence 0.8)

</details>
