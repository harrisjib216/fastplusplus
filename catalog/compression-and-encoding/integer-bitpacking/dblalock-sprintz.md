# Sprintz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Integer compression and bit-packing](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Research codec for 8/16-bit multivariate integer time series; beats Simple8b, FastPFor and SIMD-BP128 on ratio at GB/s decode.

| | |
|---|---|
| **Beats** | Simple8b, FastPFor, SIMD-BP128 (also LZ4HC, Brotli, Blosc, FSE, LZO in the author's wider runs) |
| **Claimed result** | README: 'state-of-the-art compression ratios, and can decompress at multiple GB/s in a single thread'; with 1KB and 10KB blocks 'Sprintz does even better relative to other methods'. Paper abstract (search snippet only; arXiv and ACM blocked): decompresses at up to 3GB/s in a single thread with under 1KB of memory. No per-codec numbers on the README page. |
| **Workload** | Compression ratio and single-thread decompression speed on quantized 8-bit and 16-bit multivariate integer time series (AMPDs, MSRC-12, PAMAP, UCI Gas, UCR archive), against general and integer codecs run through the author's lzbench fork. |
| **Metric** | other |
| **Compiler and flags** | Not stated in README; it says only 'tested with Clang on OS X' |
| **Adoption** | 80 stars; peer-reviewed paper (Sprintz, arXiv 1808.02515) |
| **Last commit** | 2021-01-10 |
| **Links** | [repository](https://github.com/dblalock/sprintz) · [benchmark](https://github.com/dblalock/sprintz) |

## Verdict

The IMWUT 2018 paper and README compare Sprintz with Simple8b, FastPFor and SIMD-BP128 (fed 8/16-bit data zero-padded to 32 bits, ratios divided by the padding factor) and with LZ4, Zstd-class codecs on AMPDs, MSRC-12, PAMAP, UCI Gas and UCR datasets via the author's lzbench fork, reporting top compression ratios and single-thread decompression above 3 GB/s (paper abstract, search snippet only). The fork's Makefile builds with -O3 -march=native; the CPU model is not given on any page reachable here, and one user (issue #3) could not reproduce the speeds.

## Use it when

- IoT or wearable sensor streams already quantized to 8 or 16 bits, many channels sampled together, where you want ratio near general-purpose codecs and multi-GB/s single-thread decode.
- Small blocks (1 KB to 10 KB) on memory-constrained nodes, where the README's extra figures show Sprintz gaining relative to other codecs.
- Smooth or slowly drifting signals where delta or FIRE prediction leaves small residuals, and long flat stretches that the zero-block RLE removes.
- As a research baseline when evaluating time-series codecs, using the author's lzbench fork for comparable runs.

## Skip it when

- Sorted 32/64-bit integer lists (posting lists, IDs): only 8- and 16-bit element types exist; use FastPFor, simdcomp or TurboPFor there.
- Non-x86 targets: sprintz_xff.h static_asserts __AVX2__ and bitpack.h includes immintrin.h for pext/pdep; issue #6 (2024, open) reports it fails to build on Apple M2.
- Untrusted or possibly corrupt input: decompress takes no source length or destination capacity and trusts the header's ngroups and ndims.
- Production use that needs a maintained library: last commit 2021-01-10, six open issues unanswered, no build system other than an Xcode project and the lzbench fork's Makefile, and issue #3 reports the paper's speeds could not be reproduced.

## How it is fast

Each sample is predicted from earlier samples (plain delta, or FIRE, a per-channel online-learned autoregressive filter updated with downsampled sign gradients), and the zigzag-encoded residuals of 8-row blocks are bit-packed per channel with a 3- or 4-bit width header; all-zero blocks become runs (15-bit run counter), so sparse or constant data collapses. Packing uses BMI2 pext/pdep and decode is AVX2 (_mm256 zigzag decode, prediction and prefix-add across 32 channels per vector), with state of a few bytes per channel. The paper adds an optional Huffman stage for higher ratio (search snippet only; paper blocked).

## Compared with alternatives

Pick Sprintz over FastPFor, simdcomp or TurboPFor only for multichannel 8/16-bit sensor time series, where its prediction plus per-channel packing exploits correlation in time that those uint32 codecs ignore (the README notes they reach almost no compression on unpadded bytes); for sorted 32-bit lists or any non-x86 target, those siblings (or Stream VByte for varint-style data) are the safer choice.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the codec (AVX2 and BMI2 intrinsics); benchmarks need the separate dblalock/lzbench fork plus Python, joblib, pandas, seaborn |
| **Minimum toolchain** | C++11 (lzbench fork builds it with -std=c++0x -O3 -march=native); README says only tested with Clang on OS X; issue #2 reports Clang errors 'object backing the pointer will be destroyed at the end of the full-expression' |
| **Platforms** | x86-64 with AVX2 and BMI2 only |
| **Thread safety** | not documented; functions keep no global mutable state beyond static const tables and allocate scratch per call, so separate calls on separate buffers look independent |
| **Drop-in for the baseline** | no |

## Gotchas

- Compressor leaks memory on every call: compress_rowmajor_xff_rle callocs header_bytes and coef_counters_ar and never frees them (only stripe_\* arrays and errs are freed), so long-running encoders grow without bound.
- No output-size bound or capacity argument: the encoder comments that its memset 'can overrun dest buff', and the AVX2 decoder writes whole 32-byte vectors, so size destination buffers with slack; the needed slack is not documented.
- Every call mallocs and frees scratch arrays, which costs time on small blocks; the README's GB/s figure comes from lzbench runs on large buffers.
- Source files carry 'Copyright 2017 D Blalock. All rights reserved.' headers while the repository LICENSE is Apache-2.0; the LICENSE file governs, but keep it with any vendored copy.

## Known shortcomings

- Tier B on the peer-reviewed IMWUT 2018 paper; the raw results live in the author's lzbench fork (the sprintz/results path 404s) with no flags or CPU. Last commit 2021-01-10.
- Encoder leaks memory: compress_rowmajor_xff_rle callocs header_bytes and coef_counters_ar and never frees them. Decompress takes no source length or destination capacity and trusts the header; an encoder comment says its memset 'can overrun dest buff' and the AVX2 decoder writes whole 32-byte vectors. Hard AVX2+BMI2 requirement (static_assert __AVX2__); issue #6 fails to build on Apple M2. Build files are only an Xcode project and the lzbench-fork Makefile (-std=c++0x -O3 -march=native). Issue #2 reports Clang dangling-pointer errors; issue #3 could not reproduce the paper's speeds. Six open issues, none answered. Files say 'All rights reserved' but LICENSE is Apache-2.0. Uint32 baselines were fed zero-padded data. No CPU model given.

## Caveats and trade-offs

Benchmark harness and raw results live in the separate fork https://github.com/dblalock/lzbench (results/ucr, results/multicore, results/ndims_speed and others), not in the sprintz repo (sprintz/results returns 404); the numbers files were not opened, and the paper (arXiv, ACM) is blocked in this environment. FastPFor, SIMD-BP128 and Simple8b were run on 8/16-bit data zero-padded to 32 bits and their ratios divided by the padding factor (README says so), which favours the byte-aware Sprintz. README states the speed claim without CPU model or flags and says the code was only tested with Clang on OS X. Last commit 2021-01-10 (github.com commits page).

Built for small-memory streaming of integer time series (a few bytes of state per variable), not for sorted posting lists. Benchmarks need Python, joblib, pandas and the separate dblalock/lzbench fork. Only tested with Clang on macOS.

## Maintenance

Abandoned research code since 2021-01-10 with no maintainer replies to six open issues; Apache-2.0 and small enough to vendor, but plan to fix the encoder leak and add bounds checks yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed paper (Proc. ACM IMWUT 2(3), Article 93, 2018) compares Sprintz with SIMD-BP128, FastPFOR and Simple8b on ratio and decompression speed; the README names these baselines and links the harness (dblalock/lzbench fork, results/ directory), but no compiler flags or CPU model are stated on pages reachable here, so not A.
- **Verifier notes:** Metadata matches: Apache-2.0 (LICENSE file), 80 stars, 14 forks, not archived, last commit 2021-01-10, so abandoned is right. Paper venue is ACM IMWUT 2018 (DOI 10.1145/3264903, from search results). The benchmark harness is a fork of inikep/lzbench with 3 stars.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark (paper)
- **Pages the verifier opened:**
  - <https://github.com/dblalock/sprintz>
  - <https://raw.githubusercontent.com/dblalock/sprintz/HEAD/README.md>
  - <https://raw.githubusercontent.com/dblalock/sprintz/HEAD/LICENSE>
  - <https://github.com/dblalock/sprintz/commits>
  - <https://github.com/dblalock/lzbench>
  - <https://github.com/dblalock/lzbench/tree/master/results>
- **Sources the enricher read:**
  - <https://github.com/dblalock/sprintz>
  - <https://raw.githubusercontent.com/dblalock/sprintz/HEAD/README.md>
  - <https://github.com/dblalock/sprintz/tree/master/cpp>
  - <https://github.com/dblalock/sprintz/tree/master/cpp/Compress>
  - <https://raw.githubusercontent.com/dblalock/sprintz/HEAD/cpp/Compress/sprintz.h>
  - <https://raw.githubusercontent.com/dblalock/sprintz/HEAD/cpp/Compress/sprintz.cpp>
  - <https://raw.githubusercontent.com/dblalock/sprintz/HEAD/cpp/Compress/sprintz_xff.h>
  - <https://raw.githubusercontent.com/dblalock/sprintz/HEAD/cpp/Compress/sprintz_xff_rle.cpp>
  - <https://raw.githubusercontent.com/dblalock/sprintz/HEAD/cpp/Compress/bitpack.h>
  - <https://raw.githubusercontent.com/dblalock/sprintz/HEAD/cpp/Compress/format.h>
  - <https://raw.githubusercontent.com/dblalock/sprintz/HEAD/cpp/Compress/macros.h>
  - <https://github.com/dblalock/sprintz/issues?q=is%3Aissue>
  - <https://github.com/dblalock/sprintz/issues/2>
  - <https://github.com/dblalock/sprintz/issues/3>
  - <https://github.com/dblalock/sprintz/issues/6>
  - <https://raw.githubusercontent.com/dblalock/lzbench/master/Makefile>
  - WebSearch: Sprintz time series compression FIRE forecasting bit packing run-length Huffman decompression GB/s (snippets of arxiv.org/pdf/1808.02515)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/dblalock/sprintz`) · [data/wave9/enrich/raw/github_com_dblalock_sprintz.json](../../../data/wave9/enrich/raw/github_com_dblalock_sprintz.json) (enrichment confidence 0.7)

</details>
