# bolt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MPL-2.0` · 🔴 abandoned

> AVX2 vector-quantization library that encodes float vectors into 4-bit codes and computes approximate distances and dot products far faster than PQ or exact float math.

| | |
|---|---|
| **Beats** | Eigen dense float matrix multiply (`out.noalias() = X * Q`, the repo's 'matmul' rows; README and slides call it BLAS) and the repo's own product quantization (PQ, OPQ) encoders; FAISS is not benchmarked |
| **Claimed result** | README: Bolt 'can probably save you 10-200x space and compute time'; slides (assets/bolt-slides.pdf): 10x faster than PQ/OPQ and 100x faster than raw floats for distance computation, matrix multiply faster than BLAS even when encoding first. Result files, medians of the listed trials (derived from page data): Eigen matmul 0.054 ms (N=128), 0.405 ms (256), 3.1 ms (512), 25.1 ms (1024), 203 ms (2048), 1,654 ms (4096), 13,190 ms (8192); Bolt&lt;8&gt; without matrix encoding 0.040, 0.137, 0.54, 2.2, 11.2, 46.8, 231 ms (1.4x, 3.0x, 5.8x, 11x, 18x, 35x, 57x faster) and Bolt&lt;8&gt; with encoding 0.067, 0.226, 0.92, 3.7, 17.4, 77.5, 350 ms (0.8x, 1.8x, 3.4x, 6.7x, 12x, 21x, 38x). Below N = 128 Bolt is slower than Eigen (N = 64: 0.024 ms vs 0.009 ms with encoding). Encoding 10,000 128-dimensional vectors into 16 bytes (D=128, M=16 file): PQ 39.8 ms, OPQ 46.2 ms vs Bolt 2.29 ms (about 17x vs PQ); query lookup-table build 34.7 ms (PQ float) vs 1.42 ms (Bolt, about 24x). |
| **Workload** | experiments/results (C++ Catch profile tests, 10 repetitions x 5 trials): square float32 matrix multiply of N x N matrices for N = 64 ... 8192 with Bolt approximate multiplication (8, 16 or 32 byte codes, with and without encoding the matrix), plus encoding and distance-scan timings for 10,000-vector batches of 128-dimensional vectors and 16-byte codes. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated in the result files. experiments/README says Bolt has only been tested with Clang on OS X and that the paper's timings come from Xcode builds, not the Bazel build in the repo; flags not given. AVX2 required. |
| **Adoption** | 2.5k stars; KDD 2017 paper |
| **Last commit** | 2022-06-24 |
| **Links** | [repository](https://github.com/dblalock/bolt) · [benchmark](https://raw.githubusercontent.com/dblalock/bolt/HEAD/experiments/results/matmul/square_matmul_results.txt) |

## Verdict

First-party Catch timing dumps (best of 5, 10 repetitions; the paper snippet names one thread on a 2013 MacBook Pro with a 2.6 GHz Core i7-4960HQ and Clang/Xcode builds) show Bolt with 8-byte codes computing an approximate uint16 N x N product 1.4x (N = 128) to 57x (N = 8192) faster than an exact float32 Eigen GEMM, and encoding 10,000 128-dimensional vectors in 2.29 ms against 39.8 ms for the repo's own PQ; Eigen's 13.19 s at N = 8192 is about 83 GFLOP/s, consistent with one AVX2/FMA core (derived from page data).

## Use it when

- Large collections of mostly dense float vectors (embeddings, descriptors) where approximate L2 distances or dot products are acceptable and memory or scan throughput is the bottleneck: the repo's D = 128, 16-byte run scans about 1.26 billion uint8 distances per second (1e6 codes in 0.79 ms) on one core.
- Batch encoding of many vectors: 10,000 128-dimensional vectors encode to 16-byte codes in 2.29 ms (about 4.4 million vectors/s, about 2.2 GB/s of float input, derived) against 39.8 ms for the repo's own PQ encoder.
- Candidate generation for nearest-neighbour or maximum-inner-product search, followed by exact re-ranking of the top hits, since the slides say Bolt has to retrieve more points than PQ/OPQ for a given compression level.
- Approximate matrix products where one operand is reused many times and the error is tolerable: the square matmul timings run 5.8x faster than single-threaded Eigen at N = 512 and 57x at N = 8192 without re-encoding (3.4x and 38x when the matrix is encoded inside the timed call).
- x86-64 servers or desktops with AVX2 (Haswell, 2013, or later) where you can build C++14 sources directly.

## Skip it when

- You need exact results or float outputs: Bolt returns quantized uint16 scores, its dot products are 'slightly less accurate than others' per the authors' slides, and 8-bit scans saturate at 255.
- Small problems: below N = 128 the square matmul is slower than Eigen (N = 64: 0.024 ms with encoding vs 0.009 ms), and the speedup needs enough rows to amortize table construction.
- ARM, Apple Silicon or any non-AVX2 target: the kernels are AVX2-only; the README invites ARM contributions (issue #2), issue #23 asking for other vector instruction sets is still open, and issue #25 reports an install failure on an M1 Mac.
- Python-first projects that need a working package: the README says the Python wrapper 'seems to be no longer building' for many people (issues #4, #15, #31, #37), and it is slower than the C++ path.
- You need a maintained library: the last commit is from June 2022, open issues from 2022 to 2025 (#35, #37, #39, #40, #41) have no fix, and FAISS was never benchmarked against it in the repo.

## How it is fast

Product-quantization style encoding with K = 16 centroids per subspace instead of PQ's 256, so each code is 4 bits and a 16-entry lookup table fits in one 128-bit lane; the scan does table lookups with vpshufb (_mm256_shuffle_epi8) on 32 codes at a time, accumulating with saturating 8-bit or 16-bit adds and writing with non-temporal stores. Query lookup tables are quantized from float to uint8 with a learned per-table offset and scale (quantile-based, so outliers do not blow the range), and codes are stored in 32-row column-major blocks so one 256-bit load feeds 32 rows. Much of the encoding and table-build speedup over PQ is the K = 16 choice itself: for D = 128 and 16 bytes, Bolt evaluates 32 codebooks x 16 centroids x 4 dimensions (2,048 multiply-adds) against PQ's 16 x 256 x 8 (32,768), a 16x reduction in work before any SIMD (derived from the profile constants).

## Compared with alternatives

Pick Bolt over PQ Fast Scan or Quick ADC (technicolor-research) when encoding speed and approximate dot products or matrix products matter as much as scan speed, since Bolt also vectorizes encoding and quantizes its lookup tables with learned offsets; pick PQ Fast Scan when you must return exactly the same results as a standard PQ scan, which Bolt's 4-bit codes and 8-bit tables do not.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Eigen (vendored in cpp/src/external); SWIG and NumPy for the Python wrapper; Bazel for the provided build (or the Xcode project the author used) |
| **Minimum toolchain** | C++14 (Bazel copts: -O3 -march=native -mavx -ffast-math -std=c++14); only tested with Clang on OS X per experiments/README |
| **Platforms** | x86-64 with AVX2 only |
| **Thread safety** | not documented; all kernels are single-threaded free functions and BoltEncoder holds mutable state (codes, lookup tables), so share one encoder across threads only with external locking |
| **Drop-in for the baseline** | no |

## Gotchas

- Layout and size constraints: bolt_encode requires nrows to be a multiple of 32, ncols divisible by 2 x NBytes and a 32-byte-aligned output buffer, and bolt_scan writes with _mm256_stream_si256, so its output must be 32-byte aligned too; issue #35 (open) reports a general protection fault from an aligned _mm256_load_ps in the repo's AVX sgemm helper when given a non-aligned stride.
- The square-matmul speedups grow with N partly because code length is fixed: Bolt's cost is about N^2 x (16 + M) against GEMM's N^3, so at N = 8192 Bolt&lt;8&gt; represents each 8,192-float row with 16 four-bit codes (512 dimensions per codebook). The profile runs on random codes, centroids and offsets and measures speed only, so accuracy at those sizes is never shown.
- Harness weaknesses in cpp/test/quantize/profile_bolt.cpp: _run_bolt_matmul takes the centroid, code, lookup-table and output matrices by value (the ColMatrix codes are even converted to RowMatrix on each call, and the 134 MB uint16 output is copied at N = 8192), so the product is written into a temporary copy while the anti-dead-code check prevent_optimizing_away_dists reads the caller's untouched out matrix; nothing proves the scan ran, although times rising with code length (231, 252 and 306 ms for 8, 16 and 32 bytes at N = 8192) suggest it did. The 'bolt scan uint16 safe' row is written bolt_scan&lt;(M, true)&gt;(...), a comma expression that sets NBytes to 1, so in the current source that row times a 1-byte scan (it is not one of the catalogued numbers).
- Correctness bug in an unbenchmarked path: in the uint16 bolt_scan with SignedLUTs = true, the even-indexed lanes are computed as _mm256_srai_epi16(_mm256_srai_epi16(x, 8), 8), which yields the sign of the odd byte instead of the sign-extended low byte (_mm256_srai_epi16(_mm256_slli_epi16(x, 8), 8)), so half of the rows get wrong scores with signed lookup tables; the matmul and scan timings use unsigned tables and are unaffected.

## Known shortcomings

- Medians match the result files (57x vs Eigen at N=8192), but approximate uint16 output is compared with exact float GEMM, the PQ baselines are the repo's own code, codes are random, no CPU or flags are stated, and the project is abandoned since 2022; the KDD 2017 paper could move it to B.
- Enricher: profile_bolt.cpp's anti-DCE check reads the caller's untouched output while Bolt writes into a by-value copy, so nothing proves the scan ran (times do scale with M); the 'bolt scan uint16 safe' row calls bolt_scan&lt;(M, true)&gt;, a comma expression giving NBytes=1; bolt.hpp's SignedLUTs uint16 path computes even lanes as srai(srai(x,8),8), wrong scores on half the rows (not benchmarked); with fixed 8-32 B codes one code covers 512 dimensions per codebook at N=8192, so the speedup grows with N and accuracy is never measured. The paper ran one thread on a 2013 i7-4960HQ (snippet).

## Caveats and trade-offs

First-party raw timing outputs with no CPU model and no compiler flags, so tier C even though a peer-reviewed KDD 2017 paper exists (arXiv, ar5iv and the ACM copy were not reachable; a search snippet of the abstract says approximate dot products can multiply matrices faster than a state-of-the-art BLAS even counting compression time, and gives distance and dot-product speedups up to 10x; the paper's hardware and baselines were not verified). The comparison is not the same computation: Bolt returns an approximate, quantized uint16 product built from 4-bit codes and 8-bit lookup tables, while the baseline is an exact float32 Eigen GEMM (`out.noalias() = X * Q`; single- or multi-threaded not stated, though the README's Xcode/Apple Clang build suggests single-threaded). The Bolt matmul rows use random codes, random centroids and random offsets (cpp/test/quantize/profile_bolt.cpp) and measure speed only; approximation quality is evaluated separately in Python. In that profile the helper _run_bolt_matmul takes the centroid, code, LUT and output matrices by value, so each timed call copies them (a cost charged to Bolt, up to a 134 MB output copy at N = 8192) and writes the product into the copy. The checked-in square_matmul test now enables only N = 64, 128 and 256 (the larger sizes are commented out), so the 512-8192 rows come from an earlier configuration. The 'PQ' and 'OPQ' baselines are the repo's own implementations, not FAISS, and the timing files contain no PQ scan row, so the slides' 10x-vs-PQ scan claim could not be reproduced from the files; only the encoding and lookup-table rows could. The Python README example says '\~10x here' for numpy dot products, not C++ numbers. AVX2 required; the README says the Python wrapper no longer builds for many people. Last commit 2022-06-24. [retier] Enricher: the anti-DCE check reads an untouched buffer (Bolt writes a by-value copy); the 'uint16 safe' row instantiates NBytes=1 through a comma expression; the SignedLUTs uint16 path is wrong on half the rows; with fixed-size codes the speedup grows with N and accuracy is not measured; one thread on a 2013 i7-4960HQ.

Lossy: Bolt approximates distances and dot products with learned 4-bit codebooks (error bounded in the paper's theory), needs a training pass (k-means) before encoding, and is only worthwhile for large collections of mostly dense vectors. AVX2 only, no ARM port. Python wrapper is reported as no longer building for many users and is slower than the C++ path. The MADDNESS successor ('mithral') is in the same repo.

## Maintenance

Abandoned research code since June 2022 (the MADDNESS successor 'mithral' lives in the same repo) but MPL-2.0 and small enough to vendor as C++14 source for AVX2 machines; the Python package is not reliably buildable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party raw Catch timing dumps (experiments/results/matmul/square_matmul_results.txt, experiments/results/timing/mcq_D=128_M=16.txt) from the repo's own cpp/test/quantize/profile_bolt.cpp, with no CPU model and no compiler flags (experiments/README only says Clang on OS X via Xcode). The KDD 2017 paper was unreachable (arXiv and ar5iv blocked); its abstract (snippet only) claims faster-than-BLAS matrix multiply even counting compression, so a paper-access retier could move it to B.
- **Verifier notes:** Confirmed at C; all medians in claimed_speedup re-derived from the result files (Eigen 13,190 ms vs Bolt&lt;8&gt; 231 ms at N = 8192, 57x; encode 39.8 ms PQ vs 2.29 ms Bolt; LUT 34.7 vs 1.42 ms). Shortcomings: approximate quantized output against exact float GEMM, self-implemented PQ baselines, no CPU or flags, random codes, abandoned since 2022; paper-access retier (KDD 2017, arXiv 1706.10283) could reach B.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-126 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/dblalock/bolt>
  - <https://github.com/dblalock/bolt/commits>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/experiments/results/matmul/square_matmul_results.txt>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/experiments/README.md>
  - <https://github.com/dblalock/bolt/tree/master/experiments/results>
  - <https://github.com/dblalock/bolt/tree/master/experiments/results/timing>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/experiments/results/timing/mcq_D%3D128_M%3D16.txt>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/cpp/test/quantize/profile_bolt.cpp>
  - <https://github.com/dblalock/bolt/tree/master/assets>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/README.md>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/experiments/README.md>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/experiments/results/matmul/square_matmul_results.txt>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/experiments/results/timing/mcq_D%3D128_M%3D16.txt>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/cpp/test/quantize/profile_bolt.cpp>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/cpp/test/testing_utils/testing_utils.hpp>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/cpp/src/utils/timing_utils.hpp>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/cpp/src/quantize/bolt.hpp>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/cpp/src/include/public.hpp>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/cpp/BUILD>
  - <https://raw.githubusercontent.com/dblalock/bolt/HEAD/assets/bolt-slides.pdf>
  - <https://github.com/dblalock/bolt/tree/master/assets>
  - <https://github.com/dblalock/bolt/tree/master/cpp/src>
  - <https://github.com/dblalock/bolt/tree/master/cpp/src/external>
  - <https://github.com/dblalock/bolt/issues?q=is%3Aissue>
  - <https://github.com/dblalock/bolt/issues/35>
  - WebSearch snippet of arXiv 1706.10283 (experimental setup: single thread, 2013 MacBook Pro, Core i7-4960HQ, best of 5 averaged over 10 trials)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/dblalock/bolt`) · [data/wave13/enrich/raw/github_com_dblalock_bolt.json](../../../data/wave13/enrich/raw/github_com_dblalock_bolt.json) (enrichment confidence 0.8)

</details>
