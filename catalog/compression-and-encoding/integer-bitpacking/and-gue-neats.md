# NeaTS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🟡 stale

> Research C++23 learned compressor for 64-bit integer time series with constant-time random access; paper claims xz-like ratios, faster decompression.

| | |
|---|---|
| **Beats** | xz (and Brotli, Zstd, Lz4, Snappy; time-series codecs Gorilla, Chimp, Chimp128, TSXor, DAC (sdsl dac_vector), plus LeCo and ALP per the paper) |
| **Claimed result** | README text, no numbers on the page: NeaTS provides, simultaneously, compression ratios close to or better than the best existing compressors, a faster decompression speed, and orders of magnitude more efficient random access. Paper (ICDE 2025, arXiv 2412.16266) numbers seen only in WebSearch snippets, not on an opened page: compression ratios close to Xz/Brotli with up to 1 order of magnitude faster decompression and 3 orders of magnitude faster random access; compression ratio better than Lz4 by 52.77% and Snappy by 50.20% on average, and better than Zstd on almost all datasets by 28.49% on average. |
| **Workload** | Lossless compression of 64-bit integer time series (16 datasets in the ICDE 2025 paper per search snippets): compression ratio, full decompression speed and random-access speed; the repo harness measures full decompression MB/s, random access ns per query (1e6 random indexes, 10 runs) and scan speed. |
| **Metric** | throughput |
| **Hardware** | Paper setup per a WebSearch snippet of arXiv 2412.16266v1 (not opened): Intel Xeon Gold 6140M, 1.17 TiB RAM, CentOS 7. The repo states no hardware. |
| **Compiler and flags** | Paper (WebSearch snippet only): C++23 compiled with GCC 13.2.1; optimization flags not seen. Repo CMakeLists.txt sets C++23 and CMAKE_CXX_FLAGS -march=native -mtune=native -mfpmath=sse -mavx512f -fno-math-errno; -O9 and -funroll-loops appear only in CMAKE_C_FLAGS; no CMAKE_BUILD_TYPE default is set, so a plain 'cmake ..' build of the C++ code has no optimization level. |
| **Adoption** | 13 stars; ICDE 2025 paper (Guerra, Vinciguerra, Boffa, Ferragina), pages 1579-1592 |
| **Last commit** | 2025-07-15 |
| **Links** | [repository](https://github.com/and-gue/NeaTS) · [benchmark](https://github.com/and-gue/NeaTS) |

## Verdict

Not verified from an opened source: the ICDE 2025 paper (arXiv 2412.16266, blocked here) reportedly compares NeaTS with xz, Brotli, Zstd, Lz4 and Snappy run through Squash on fixed-size blocks (the harness sweeps 512 to 16384 values per block, default 1000) and with Gorilla, Chimp, Chimp128, TSXor, DAC, LeCo and ALP on 16 datasets, using a Xeon Gold 6140M and GCC 13.2.1 with no flags seen; search snippets say ratios close to xz and Brotli, up to 10x faster decompression and about 1000x faster random access. In the repo, the NeaTS timing code is real (50 full-decompression runs; 1e6 random accesses x 10 runs). Its biases mostly go against NeaTS (allocation and zero-fill of the output inside the timed loop; size_in_bits counts the starting-position Elias-Fano structure twice and adds sizeof(\*this)), except that per-query random-access time is truncated to whole nanoseconds. The random-access gap over block codecs depends on the block size chosen for them.

## Use it when

- Large, smooth or trending integer time series (sensor readings, prices, temperatures after fixed-point scaling) that you query by position many more times than you rewrite.
- Point lookups or short range scans on compressed data where block codecs (xz, Brotli, Zstd on 8 KB blocks) would have to decompress a whole block per query.
- Read-mostly archives where a slow, one-off compression pass is acceptable in exchange for ratios the paper reports as close to xz and Brotli.
- Research or prototyping on Linux x86-64 with GCC 13 or newer, ideally on an AVX-512 machine like the paper's Xeon Gold 6140M.

## Skip it when

- You need a production codec: the repo is research code with 13 stars, no tests, no install target, no release, its last commit was 2025-07-15, and its benchmark harness has most baseline calls commented out.
- Data is noisy or random: the piecewise models only pay off when segments follow a curve; otherwise residual width approaches the raw value width.
- Streaming or append workloads: the structure is built in one pass over the whole array and is static afterwards.
- Very large series: offsets into the residual bit array are 32-bit (x_t = uint32_t by default), so more than 2^32 residual bits (about 512 MiB of residuals) or 2^32 values overflow the counters, and writes then run past the allocated buffer.
- Portable binaries or non-x86 targets: this copy's CMake forces -march=native and -mavx512f, so binaries fail with illegal-instruction errors on CPUs without AVX-512, and &lt;experimental/simd&gt; requires libstdc++. The co-author's copy (gvinciguerra/NeaTS) drops these flags.

## How it is fast

The series is cut into segments, and each segment is approximated by one of four function shapes (linear, exponential, quadratic, square root) whose maximum error fits a chosen residual width; a shortest-path style dynamic program over all (shape, width) pairs picks the partition that minimizes total bits. Each value is stored as its model prediction plus a fixed-width residual, so random access is an Elias-Fano predecessor search on segment starts (sux select), one model evaluation and one bit-field read, with no block to decompress. Full decompression evaluates the models over 8 lanes at a time with std::experimental::simd (AVX-512 on the paper's Skylake Xeon) and adds residuals that are unpacked one field at a time with BEXTR.

## Compared with alternatives

Pick it over LeCo when the series has nonlinear trends (the paper, per search snippets only, reports 12.80% better ratio and 36.26% faster compression than LeCo) and you need per-element random access; prefer FastPFor, TurboPFor or Sprintz when you need a mature, fast, block-decoded codec for posting lists or streaming sensor data rather than random access into smooth series.

## Integration

| | |
|---|---|
| **Form** | header-only (include/NeaTS.hpp plus include/\*.hpp), but distributed as a CMake research project with example executables, not a packaged library |
| **Dependencies** | sdsl-lite and sux (both vendored in lib/); Squash 0.7 only for the Benchmark target |
| **Minimum toolchain** | C++23 (uses &lt;stdfloat&gt; and std::to_underlying), GCC 13+ or Clang 16+ with libstdc++ (needs &lt;experimental/simd&gt;), CMake 3.22 |
| **Platforms** | Linux x86-64; and-gue CMake forces AVX-512F (-mavx512f -march=native); BMI1 BEXTR is used when available, with a portable fallback; the co-author copy adds an aarch64 -mcpu=native branch |
| **Thread safety** | not documented (operator[] and simd_scan are const; simd_decompress is non-const) |
| **Drop-in for the baseline** | no |

## Gotchas

- Lossless output is not guaranteed by construction: segment slopes are fitted in double but stored as float (default T1 = float), and residuals that then fall outside the chosen bit width are silently truncated. main_simd.cpp checks decompression and random access against the input, but on a mismatch it only prints an error count and still prints the CSV row of ratio and speeds. The co-author's March 2026 commit a85ae14 ('Use double precision if compression with float coefficients fails') adds verify-and-retry-with-double to the new neats_compress tool, which confirms that float coefficients can fail on real inputs. Check decompressed output against the input before trusting a result.
- A plain 'cmake ..' as in the README sets no C++ optimization level (only CMAKE_C_FLAGS carry -O9), so pass -DCMAKE_BUILD_TYPE=Release before measuring anything.
- The rank supports (sdsl rank_support_v) hold raw pointers into the compressor's own bit vectors, and the class uses default copy and move, so a copied or moved compressor can point into another object's storage; load() here returns a fresh object by value (the co-author changed it to load in place in March 2026). Build or load it in place and do not copy it.
- The input is shifted by its minimum minus epsilon before compression and the decompressed output is not shifted back by the library; preprocess_data in algorithms.hpp does the shift and postprocess_data the inverse, so callers must keep the offset. Residual widths above 57 bits are unsupported (read_field reads 8 bytes at a byte offset).

## Known shortcomings

- Tier C placeholder: the README carries no numbers; the comparison against xz, Brotli, Zstd, Lz4 and Snappy (52.77%/50.20% ratio vs Lz4/Snappy, 28.49% vs Zstd; Xeon Gold 6140M, GCC 13.2.1) lives in the ICDE 2025 paper (DOI 10.1109/ICDE65448.2025.00122, arXiv 2412.16266), blocked here and seen only in search snippets. Retier to B once the paper is readable.
- Repo harness is not a baseline benchmark: benchmark/neats_lossless.cpp main() runs only squash_scan('lz4') with the other baseline calls commented out, main_simd.cpp's last 'Decompression speed' line times a raw SIMD copy, and CMake sets no C++ optimization level. GPL-3.0; last commit 2025-07-15 (stale); the co-author copy gvinciguerra/NeaTS is active through 2026-03-08 and carries a float-coefficient fallback fix.
- Enricher: possible correctness flaw behind the numbers: slopes are stored as float (T1=float) and out-of-range residuals are silently truncated; main_simd.cpp prints a mismatch count yet still prints the CSV ratio and speeds; co-author commit a85ae14 (gvinciguerra, 2026-03-08) adds a float-to-double fallback, so the float failure is real on some inputs (effect on the paper's numbers unknown, paper unread). Residual offsets are uint32, so more than 2^32 residual bits overflow into a heap overflow; CMake forces -mavx512f with no -O level; a copied or moved compressor leaves its sdsl rank_support pointing at the other object's storage. Harness biases mostly run against NeaTS (output allocation and zero-fill timed; size_in_bits double-counts starting_positions_ef), but random-access times are truncated to whole nanoseconds and block-codec baselines use 1000-value blocks by default.

## Caveats and trade-offs

Paper numbers could not be read: arXiv, IEEE and the author's talk slides are blocked here, and no PDF or result table is checked into the repo (root has LeaTS.cpp, NeaTSL.cpp, SNeaTS.cpp, main_simd.cpp, CMakeLists.txt; benchmark/ holds Chimp, Chimp128, Gorilla, TSXor sources, neats_lossless.cpp, gp_compressors_bench.hpp, st_compressors_bench.hpp; the datasets are on a d4science link not opened). What the search snippets said, not verified on any opened page: NeaTS reaches compression ratios close to xz and Brotli with up to 1 order of magnitude faster decompression and 3 orders of magnitude faster random access (talk-slide snippet); fastest decompression on 10 of 16 datasets; ratio better than Zstd by 28.49% on average, better than Lz4 by 52.77% and Snappy by 50.20%; faster compression than LeCo by 36.26% and ratio better by 12.80% on average; compared compressors Xz, Brotli, Zstd, Lz4, Snappy, Chimp, Chimp128, TSXor, DAC, Gorilla, LeCo, ALP. A snippet figure of 2561.31 MB/s decompression for NeaTS next to PLA 2997.00 and AA 2420.20 appears to belong to the lossy NeaTS-L comparison against PLA and AA, so it is not used as the lossless claim. Repo evidence is thin: benchmark/neats_lossless.cpp main() currently runs only squash_scan with lz4 and has everything else commented out; main_simd.cpp prints NeaTS compression, random-access and full decompression speed but its final 'Decompression speed' line times a SIMD copy of the raw data, not NeaTS; LeCo and ALP are not in the repo harness; no CPU model or build flags are given. The README's plain 'cmake ..' sets no optimization level for C++ code (only the C flags have -O9), so a default build is unoptimized unless -DCMAKE_BUILD_TYPE=Release is passed. Tier C is a placeholder: the paper is peer reviewed (B), and A is possible if it states CPU, compiler and flags since the comparator harness is public; retier when arXiv 2412.16266 or the IEEE page is readable. Files opened: raw README.md, CMakeLists.txt, main_simd.cpp and benchmark/neats_lossless.cpp of and-gue/NeaTS; github.com/and-gue/NeaTS, /commits, /tree/main/benchmark, /tree/main/lib, /tree/main/include. Verifier additions (2026-10-03): a WebSearch snippet of the arXiv HTML (2412.16266v1, not opened) gives the paper's setup as an Intel Xeon Gold 6140M with 1.17 TiB RAM, CentOS 7, C++23 code compiled with GCC 13.2.1; no optimization flags appeared in the snippet, so A still cannot be granted from what was seen. The CSV line of main_simd.cpp does time NeaTS simd_decompress (50 runs, with a value-initialized output vector allocated inside the timed loop) and random access (1e6 random indexes, 10 runs, integer ns per query), so the harness for NeaTS itself is real; the baseline side lives in squash_full/squash_random_access calls in benchmark/neats_lossless.cpp that are commented out except one lz4 scan. Co-author Giorgio Vinciguerra keeps a copy at github.com/gvinciguerra/NeaTS (not marked as a fork, shares the history up to 2025-07-15) with 10 more commits through 2026-03-08, including 'Use double precision if compression with float coefficients fails', 'Fix allocated size not multiple of alignment' and 'Remove architecture-specific compilation flags'; the first suggests the float-coefficient configuration (the default T1=float32 in main_simd.cpp) could fail on some inputs, and that copy's CMakeLists.txt still sets no C++ optimization level. The README says the code is 'released for academic purposes under the terms of the GNU General Public License v3.0'; the license itself is plain GPL-3.0, which allows any use.

Research code, GPL-3.0 (README says released for academic purposes under GPL-3.0) with sdsl-lite and sux vendored in lib/. Needs a C++23 compiler (GCC 13 or Clang 16 or newer), CMake 3.22, and Squash 0.7 for the Benchmark target. SIMD decompression uses std::experimental::simd and the build adds -mavx512f and -march=native, so binaries are not portable. Input is binary 64-bit signed integers with a user-chosen maximum residual bit width, so floating-point series must be converted to integers first. Compression (piecewise nonlinear model partitioning) is the expensive side; random access works on the compressed form without full decompression, which block-based general compressors cannot do.

## Maintenance

Stale research code (13 stars, last commit 2025-07-15, GPL-3.0); the co-author's copy gvinciguerra/NeaTS was updated through 2026-03-08 with portable build flags, float-to-double fallback, serialization fixes and compress/decompress command-line tools, and is the better starting point.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo page and README carry only a qualitative claim; the comparison numbers against xz, Brotli, Zstd, Lz4 and Snappy live in the peer-reviewed ICDE 2025 paper (DOI 10.1109/ICDE65448.2025.00122 cited in the README), which is blocked here and was seen only through WebSearch snippets, and the repo harness (main_simd.cpp, benchmark/neats_lossless.cpp) has its baseline calls commented out. C stays a placeholder: B is warranted once the paper's tables are read, and A only if the paper states optimization flags (snippet gives Xeon Gold 6140M and GCC 13.2.1).
- **Verifier notes:** Record is accurate about the repo: README has no numbers, neats_lossless.cpp main() runs only squash_scan('lz4'), main_simd.cpp's last 'Decompression speed' line times a raw SIMD copy, and CMake sets no C++ -O level. Metadata confirmed on github.com (GPL-3.0, 13 stars, last commit 2025-07-15, so stale); the co-author's copy gvinciguerra/NeaTS is active through 2026-03-08 and may be the better link later. Retier to B once arXiv 2412.16266 or the IEEE page is readable.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** paper tables (blocked)
- **Pages the verifier opened:**
  - <https://github.com/and-gue/NeaTS>
  - <https://github.com/and-gue/NeaTS/commits>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/README.md>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/main_simd.cpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/benchmark/neats_lossless.cpp>
  - <https://github.com/and-gue?tab=repositories>
  - <https://github.com/and-gue/LeaTS>
  - <https://github.com/gvinciguerra?tab=repositories&q=&type=source>
  - <https://github.com/gvinciguerra/NeaTS>
  - <https://github.com/gvinciguerra/NeaTS/commits>
  - <https://raw.githubusercontent.com/gvinciguerra/NeaTS/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/gvinciguerra/NeaTS/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/and-gue/NeaTS>
  - <https://github.com/and-gue/NeaTS/tree/main/include>
  - <https://github.com/and-gue/NeaTS/issues?q=is%3Aissue>
  - <https://github.com/and-gue/NeaTS/issues/1>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/README.md>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/main_simd.cpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/SNeaTS.cpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/include/NeaTS.hpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/include/algorithms.hpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/include/float_pfa.hpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/include/my_elias_fano.hpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/include/piecewise_nonlinear_model.hpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/include/coefficients_space.hpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/include/utils.hpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/benchmark/neats_lossless.cpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/benchmark/gp_compressors_bench.hpp>
  - <https://raw.githubusercontent.com/and-gue/NeaTS/HEAD/benchmark/st_compressors_bench.hpp>
  - <https://github.com/gvinciguerra/NeaTS>
  - <https://github.com/gvinciguerra/NeaTS/commits>
  - <https://github.com/gvinciguerra/NeaTS/commit/a85ae141d676dff4a434d7609cec496c0f128194>
  - <https://raw.githubusercontent.com/gvinciguerra/NeaTS/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/gvinciguerra/NeaTS/HEAD/README.md>
  - <https://raw.githubusercontent.com/gvinciguerra/NeaTS/HEAD/include/NeaTS.hpp>
  - <https://raw.githubusercontent.com/gvinciguerra/NeaTS/HEAD/include/algorithms.hpp>
  - <https://raw.githubusercontent.com/gvinciguerra/NeaTS/HEAD/include/float_pfa.hpp>
  - <https://raw.githubusercontent.com/gvinciguerra/NeaTS/HEAD/neats_compress.cpp>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/and-gue/neats`) · [data/wave9/enrich/raw/github_com_and_gue_neats.json](../../../data/wave9/enrich/raw/github_com_and_gue_neats.json) (enrichment confidence 0.6)

</details>
