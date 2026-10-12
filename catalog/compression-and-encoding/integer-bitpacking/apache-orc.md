# Apache ORC C++ AVX-512 RLE bit-unpacking (ORC-1356)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Apache ORC's C++ reader with opt-in AVX-512 (and RVV) RLEv2 bit-unpacking, claimed 6-7x over ORC's scalar generic unpacker.

| | |
|---|---|
| **Beats** | ORC C++ scalar RLEv2 bit-packing decoder (plainUnpackLongs, pre-change) |
| **Claimed result** | PR author: 'In the funcational micro-performance test I suppose AVX-512 vector decode could bring average 6X \~ 7X performance latency improvement compare vector function vectorUnpackX with the original Rle-bit-packing decode function plainUnpackLongs.' No per-bit-width data is given. |
| **Workload** | Decoding of RLE v2 bit-packed integer runs with widths 1 to 32 bits, comparing AVX-512 decode against the scalar decoder. |
| **Metric** | latency |
| **Hardware** | Intel SKX (Skylake-SP/X) or newer AVX-512 platform per the PR text; exact CPU model not stated |
| **Compiler and flags** | Not stated. CMake option -DBUILD_ENABLE_AVX512=ON (default OFF); runtime override via ORC_USER_SIMD_LEVEL=AVX512 or none |
| **Adoption** | 769 stars (apache/orc) |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/apache/orc) · [benchmark](https://github.com/apache/orc/pull/1375) |

## Verdict

The PR author reports an average 6-7x lower latency for vectorUnpackN versus ORC's scalar plainUnpackLongs in an unpublished micro-test on an unnamed AVX-512 Intel CPU, with no compiler or flags given; a later snippet of the JIRA text says aligned widths see almost no gain and unaligned widths about 6x. The only independent end-to-end test in the thread (ClickHouse, Snappy/LZ4 files) found no improvement.

## Use it when

- You already read ORC files from C++ on Linux x86-64 servers with AVX-512F/CD/VL/DQ/BW (Skylake-SP or newer Intel, Zen 4 or newer AMD) and integer decode shows up in profiles.
- Files written with non-byte-aligned RLEv2 bit widths (for example 3, 5, 7, 11 bits), which the PR author says is where the gain appears; byte-aligned widths already use scalar unrolled unpackers.
- Long direct runs of integers (dozens to 512 values), so the vector loop rather than the scalar head and tail handles most values.
- RISC-V vector hardware: the same dispatch has an RVV path (BUILD_ENABLE_RVV, ORC-2216, committed 2026-09-21).

## Skip it when

- Expecting an end-to-end speedup: a ClickHouse contributor reading a 505 MB, 1.2M-row ORC file saw no improvement, and with only int64 columns selected the AVX-512 run was marginally slower (0.442 s vs 0.440 s median), since decompression and other work dominate.
- Distributing portable binaries: when enabled, the CMake module appends -march=native -mtune=native to CMAKE_CXX_FLAGS for the whole library and only enables AVX-512 if the build host's /proc/cpuinfo lists avx512f, so the build is tied to the build machine's CPU.
- macOS or MinGW builds: the top-level CMakeLists skips the AVX-512 configuration on Apple, and ConfigSimdLevel disables it on MinGW (GCC bug 65782).
- As a general bit-packing library for your own arrays: the code is internal to RleDecoderV2 and tied to its buffer management; use simdcomp, FastPFor or TurboPFor for that.

## How it is fast

For each bit width 1 to 32 a vectorUnpackN routine loads packed bytes with masked AVX-512BW loads (_mm512_maskz_loadu_epi8), or 64-bit gathers (_mm512_i64gather_epi64) for wider fields, rearranges them with _mm512_permutexvar and _mm512_shuffle_epi8, aligns each field with per-lane variable shifts (srlv/sllv) and masks it, decoding 64, 32 or 16 values per 512-bit step into a small scratch buffer that is then widened into the int64_t output. Leading and trailing values that do not fill a vector, and widths above 32, go to the scalar plainUnpackLongs or the existing unrolled byte-aligned unpackers.

## Compared with alternatives

Pick it only if your data already lives in ORC and you control the C++ build and deployment CPU; for your own integer arrays, simdcomp, FastPFor (SIMD-BP128) or TurboPFor give standalone, portable SIMD bit-unpacking with published benchmarks.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | ORC C++ third-party stack (protobuf, zlib, Snappy, LZ4, Zstd), fetched by ThirdpartyToolchain.cmake |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17); compiler must accept -mavx512f -mavx512cd -mavx512vl -mavx512dq -mavx512bw (or /arch:AVX512 on MSVC) |
| **Platforms** | x86-64 with AVX-512F/CD/VL/DQ/BW for the vector path (not macOS, not MinGW); RISC-V with RVV for the RVV path; scalar everywhere else |
| **Thread safety** | not documented for the unpacker; dispatch and CpuInfo are function-local statics initialized once, and each RleDecoderV2 instance holds its own buffers |
| **Drop-in for the baseline** | partial: it replaces ORC's own scalar unpacker transparently, but only after a rebuild with -DBUILD_ENABLE_AVX512=ON and with ORC_USER_SIMD_LEVEL=AVX512 set at run time |

## Gotchas

- Off twice by default: even in a BUILD_ENABLE_AVX512=ON build, CpuInfo reads ORC_USER_SIMD_LEVEL and treats unset as NONE, which clears the AVX512 flag, so the vector path runs only when the environment variable is AVX512 (README says so; easy to miss when benchmarking).
- Any value other than AVX512 or NONE (case-insensitive) makes CpuInfo construction throw ParseError('Invalid value for ORC_USER_SIMD_LEVEL'), which surfaces at the first integer decode.
- The quoted 6-7x is against plainUnpackLongs, the generic bit-by-bit loop; the scalar default path already uses unrolled unpackers for widths 4, 8, 16, 24, 32, 40, 48, 56 and 64, so the realistic baseline for aligned widths is much faster than the PR's comparison.
- No timing harness ships with the change: c++/test/TestRleVectorDecoder.cc checks correctness only, so the speed claim cannot be rerun from the repository.

## Known shortcomings

- Tier C: PR #1375 (merged 2023-05-07) carries a hedged author claim ('I suppose... average 6X \~ 7X', vectorUnpackX vs scalar plainUnpackLongs) with no CPU model, compiler, flags or timing harness (TestRleVectorDecoder.cc tests correctness only); a ClickHouse tester saw no gain. Entry stands for ORC's C++ reader (ORC-2216 RVV bit-unpacking landed 2026-09-21).
- The AVX-512 RLEv2 path needs both -DBUILD_ENABLE_AVX512=ON and ORC_USER_SIMD_LEVEL=AVX512 at run time; unset means NONE. Enabling it appends -march=native -mtune=native to the whole library's CMAKE_CXX_FLAGS and checks the build host's /proc/cpuinfo, so binaries are not portable; skipped on macOS and MinGW. The 6-7x is against plainUnpackLongs (a bit-by-bit loop) while the scalar path already has unrolled unpackers for widths 4/8/16/24/32/40/48/56/64. A ClickHouse test in the PR thread saw no gain (int64-only 0.442 s vs 0.440 s). No timing harness in the repo.

## Caveats and trade-offs

First-party PR claim, hedged by the author ('I suppose'), from a micro-benchmark that is not in the repository, with no CPU model, compiler or flags. A ClickHouse contributor (taiyang-li) tested a 505 MB, 1.2M-row ORC file in the PR thread and saw no measurable improvement; the author suggested gains may appear only for non-aligned bit widths. Blocks smaller than 512 bits fall back to scalar decoding. AVX-512 path is off by default at build time. Baseline is ORC's own scalar decoder, not varint, Simple8b or FastPFor. Merged 2023-05-07; a RISC-V Vector (RVV) bit-unpacking path for RLEv2 (ORC-2216) was committed on 2026-09-21.

AVX-512 path is opt-in at build time and selected at run time; scalar path remains. The commits page also shows a later RVV (RISC-V vector) bit-unpacking change (ORC-2216) for the same decoder.

## Maintenance

Apache ORC is actively maintained (last commit 2026-09-21, RVV path just added) and Apache-2.0, but the AVX-512 file's own history shows only the original 2023-05-07 commit and the feature stays opt-in at both build and run time.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #1375 (merged 2023-05-07) gives only the author's hedged statement of an average 6X-7X latency gain for vectorUnpackX over the scalar plainUnpackLongs in a 'functional micro-performance test'; no CPU model, compiler, flags, per-width data or timing harness are published (c++/test/TestRleVectorDecoder.cc is a correctness test with no timing code). First-party numbers without methodology are tier C.
- **Verifier notes:** Catalog rule: apache/orc is on data/known_list.txt only because merging this record put it there (commit e5783ba, 'Wave 9: merge w9-intpack-registry'); no earlier wave lists ORC as an entry (wave 6 mentions it only as a BtrBlocks baseline), so there is nothing to fold into. Recommend keeping it as the single entry for Apache ORC's C++ reader (RLEv2 SIMD bit-unpacking, now AVX-512 and RVV) under the repo id; later ORC findings should fold into it as evidence.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; first-party PR benchmark (ORC-1356)
- **Pages the verifier opened:**
  - <https://github.com/apache/orc/pull/1375>
  - <https://github.com/apache/orc>
  - <https://github.com/apache/orc/commits/main>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/test/TestRleVectorDecoder.cc>
- **Sources the enricher read:**
  - <https://github.com/apache/orc/pull/1375>
  - <https://github.com/apache/orc/tree/main/c++/src>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/Bpacking.hh>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/BpackingAvx512.cc>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/BpackingAvx512.hh>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/BitUnpackerAvx512.hh>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/BpackingDefault.cc>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/BpackingRvv.cc>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/CpuInfoUtil.cc>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/Dispatch.hh>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/RleDecoderV2.cc>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/RLEv2.hh>
  - <https://raw.githubusercontent.com/apache/orc/main/c++/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/apache/orc/main/cmake_modules/ConfigSimdLevel.cmake>
  - <https://raw.githubusercontent.com/apache/orc/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/apache/orc/main/README.md>
  - <https://github.com/apache/orc/commits/main/c++/src/BpackingAvx512.cc>
  - WebSearch: Apache ORC C++ AVX512 BUILD_ENABLE_AVX512 bit-unpacking bug (snippets incl. issues.apache.org/jira/browse/ORC-1356)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/apache/orc`) · [data/wave9/enrich/raw/github_com_apache_orc.json](../../../data/wave9/enrich/raw/github_com_apache_orc.json) (enrichment confidence 0.75)

</details>
