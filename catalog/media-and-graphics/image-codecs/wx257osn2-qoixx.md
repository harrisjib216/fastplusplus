# qoixx

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Single-header C++20 QOI codec with an AVX2/NEON/SVE encoder, 1.4-1.8x faster than the reference qoi.h.

| | |
|---|---|
| **Beats** | qoi.h (reference QOI implementation, phoboslab/qoi) |
| **Claimed result** | README (grand total for the QOI benchmark suite, 20 iterations): on Intel Core i9-10900 with g++ 11.1.0, qoi decodes in 2.2389 ms (207.326 mpps) and encodes in 2.5434 ms (182.504 mpps), against qoixx at 1.3477 ms (344.431 mpps) and 1.5255 ms (304.280 mpps), about 1.66x decode and 1.67x encode. Across all seven machines qoixx is 1.37-1.66x faster at decoding and 1.47-1.76x faster at encoding (derived from page data), with identical output size (463 KB, 28.2%). |
| **Workload** | QOI encode and decode of the QOI benchmark suite (grand total, 20 iterations), ms and megapixels per second, on seven CPUs. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-10900; AMD Ryzen 7 2700X; Ryzen 7 3800X; Ryzen 9 3950X; AWS Graviton3; Qualcomm Kryo 585; Apple M1 Max |
| **Compiler and flags** | g++ per machine as listed in the README: 11.1.0 (i9-10900, Kryo 585), 11.0.0 20200622 experimental (Ryzen 7 2700X), 12.0.0 20211219 experimental (Ryzen 7 3800X), 11.2.0 MSYS2 ucrt64 (Ryzen 9 3950X, Windows), 11.2.0 (Graviton3, Apple M1 Max). Makefile CXXFLAGS: -std=c++2a -O3 -march=native -mtune=native. qoi.h is compiled into the same qoibench binary with the same flags. |
| **Adoption** | 42 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/wx257osn2/qoixx) · [benchmark](https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/README.md) |

## Verdict

The README runs src/qoibench.cpp, which compiles qoi.h and qoixx into one binary with the same -std=c++2a -O3 -march=native flags and checks round trips with memcmp before timing (20 runs plus a warm-up). On the public QOI benchmark suite qoixx was 1.37-1.66x faster at decoding and 1.47-1.76x faster at encoding on seven CPUs, for example i9-10900 with g++ 11.1.0: 344 vs 207 Mpx/s decode and 304 vs 183 Mpx/s encode. The 'ms' and 'size kb' columns are per-image means, not suite totals (issue #10, wontfix). The numbers date from 2022, before the 2024 encoder and decoder speed-ups (PRs #19 and #25) and before the fix for a decoder bug when the first opcode is QOI_OP_RUN (PR #23). The harness's memcmp check passed, so the timed decodes were correct for those inputs.

## Use it when

- You already store or stream QOI and encoding is the bottleneck, for example screen capture, game frame dumps or webcam streams on x86-64 with AVX2 or on ARMv8 servers and phones
- C++20 code bases that want a dependency-free single header that writes into std::vector or unique_ptr buffers without a malloc/free C API
- AArch64 targets with SVE (for example AWS Graviton3), which get a dedicated SVE encoder that qoi.h lacks
- Batch conversion where output must stay readable by any QOI decoder: CI diffs its decodes against the reference qoiconv on the official test images

## Skip it when

- If compression ratio or format reach matters more than speed: QOI stores the benchmark suite at 28.2% of raw size with no effort levels, and few tools read it; siblings fpnge (PNG output) or QOIR (better ratio options) fit that case
- Decode-dominated workloads: the README says the decoder is scalar and 'with some input, original implementation is faster', and the MSVC-built decoder is slow (FAQ: use MinGW-w64)
- Toolchains older than C++20, builds with -fno-exceptions (errors are thrown as std::runtime_error/std::invalid_argument), or 32-bit ARM, where SIMD is disabled (issue #26 open)
- Untrusted input on any commit before 2026-09-29: until PR #32 the decoder's remaining-byte counter included the 14-byte header, so truncated files could read past the end of the input buffer

## How it is fast

The encoder processes 32 pixels per AVX2 iteration (or one NEON/SVE vector). It computes channel deltas against the shifted previous pixels in one pass, skips whole runs of identical pixels with a single test, and builds candidate DIFF and LUMA opcodes plus colour hashes for all lanes before a short serial emit step. The scalar paths avoid qoi.h's per-pixel branching: the hash is a single 64-bit multiply, and 3-byte copies are split into 2+1-byte memcpy calls. On x86 the decoder updates the colour-index hash incrementally from constexpr lookup tables (QOIXX_DECODE_WITH_TABLES), and on AArch64 it writes long runs with 8-pixel NEON stores.

## Compared with alternatives

Pick qoixx over the reference qoi.h (phoboslab/qoi) whenever you can compile C++20 and want the same files faster, especially encode on AVX2, NEON or SVE. Pick qoi-rust instead in Rust code (its M1 decode gain over qoi.h, about 1.5x, is similar). Pick fpnge or QOIR when compression ratio or PNG compatibility matters more than staying on QOI.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (standard library plus immintrin.h, arm_neon.h or arm_sve.h when SIMD is enabled; QOIXX_NO_SIMD removes them) |
| **Minimum toolchain** | C++20 (concepts, &lt;bit&gt;, std::endian); CI builds with GCC and Clang on Ubuntu x86-64 and arm64, plus MSYS2 on Windows |
| **Platforms** | x86-64 (AVX2 encoder when compiled with -mavx2 or -march=native, otherwise scalar), AArch64 (NEON, or SVE at any vector length from 128 to 2048 bits), any other target via the scalar paths; SIMD is chosen at compile time with no runtime dispatch |
| **Thread safety** | not documented; by inspection all state is local to each call (lookup tables are function-local static constexpr), so concurrent calls on separate buffers are safe |
| **Drop-in for the baseline** | partial: same .qoi bitstream (files are interchangeable with qoi.h), but a C++20 template API instead of qoi.h's C functions, and no qoi_read/qoi_write file helpers |

## Gotchas

- Likely bug (from reading the code, not run): decoding a 4-channel file with channels = 3 drops alpha before computing the colour-index hash, while the QOI spec hashes r\*3+g\*5+b\*7+a\*11. Images with any alpha other than 255 can then fetch the wrong colour on QOI_OP_INDEX. CI only decodes at the file's own channel count, so this path is untested. Decode at native channels and strip alpha yourself.
- The SIMD encoder runs only when both input and output containers are contiguous (vector, unique_ptr pair or pointer pair). A custom non-contiguous container silently falls back to the scalar encoder.
- Output bytes differ from qoi.h even though sizes match: a 1-pixel run is written as QOI_OP_INDEX of the previous pixel instead of QOI_OP_RUN. Both are valid and decode identically, but byte-for-byte comparisons against qoi.h output fail.
- Images are capped at 400,000,000 pixels, and width or height 0 throws, the same limits as qoi.h.

## Known shortcomings

- Tier A on src/qoibench.cpp with Makefile -O3 -march=native (unchanged since February 2022), g++ version and CPU stated per machine; the numbers date from 2022. Baseline is qoi.h, not a listed incumbent (baseline_in_list false); an independent C++20 re-implementation of QOI, not a port, so kept beside phoboslab/qoi.
- README numbers are from 2022 code, older than the 2024 speedups (PRs #19 and #25) and the decoder fix for a first-op QOI_OP_RUN (PR #23); the benchmark's memcmp verification passed on its inputs, so the timed decodes were correct and the tier stands. A decoder read overrun on truncated input was fixed only on 2026-09-29 (PR #32; the size counter included the 14-byte header). Likely bug from code reading (not run): an RGBA file decoded with channels=3 hashes without alpha, giving wrong INDEX pixels when alpha is not 255, a path untested by CI. The ms/kb columns are per-image means (issue #10).

## Caveats and trade-offs

Baseline is the qoi.h reference implementation, not libpng/libwebp, so this qualifies only through the QOI entry (phoboslab/qoi vs libpng). The README numbers date from 2022 (benchmark sections added March-June 2022) against the qoi.h revision of that time; the README gives no commit for them. Per the README, the decoder is a scalar implementation and 'with some input, original implementation is faster', and MSVC-built decoders are slow (FAQ recommends MinGW-w64). Results use -march=native builds and need C++20.

Single-header C++20 QOI codec with SIMD encoder (AVX2, SVE or NEON, scalar fallback via QOIXX_NO_SIMD). Decoder is optimized scalar and 'with some input, original implementation is faster'. Output size is identical to qoi.h (463 KB total). Decoder built with MSVC is not fast per the FAQ.

## Maintenance

Actively maintained by a single author (last commits 2026-09-29: buffer-overrun fix and CI update), MIT and small enough to vendor; use a commit from 2026-09-29 or later.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The README table runs public benchmark code (src/qoibench.cpp, which compiles qoi.h and qoixx into one binary and cross-checks decodes with memcmp) on the public QOI benchmark suite. The Makefile states the flags (-std=c++2a -O3 -march=native -mtune=native, unchanged since Feb 2022), and the README gives the g++ version and CPU model for each of the seven machines.
- **Verifier notes:** Not a duplicate of the phoboslab/qoi record: qoixx is an independent C++20 re-implementation of the QOI format (its own 1400-line qoixx.hpp with AVX2/NEON/SVE encoders), not a wrapper or port of qoi.h. Only the benchmark harness is adapted from qoi's qoibench, hence LICENSES/qoi.LICENSE. baseline_in_list stays false. MIT, 42 stars, last commit 2026-09-29 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/README.md>
  - <https://github.com/wx257osn2/qoixx>
  - <https://github.com/wx257osn2/qoixx/commits>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/Makefile>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/.gitmodules>
  - <https://github.com/wx257osn2/qoixx/tree/master/LICENSES>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/src/qoibench.cpp>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/include/qoixx.hpp>
  - <https://github.com/wx257osn2/qoixx/commits/master/Makefile>
  - <https://github.com/wx257osn2/qoixx/commits/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/wx257osn2/qoixx>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/README.md>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/Makefile>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/src/qoibench.cpp>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/include/qoixx.hpp>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/src/test.cpp>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/src/qoiconv.cpp>
  - <https://raw.githubusercontent.com/wx257osn2/qoixx/HEAD/.github/workflows/linux.yml>
  - <https://github.com/wx257osn2/qoixx/issues?q=is%3Aissue>
  - <https://github.com/wx257osn2/qoixx/issues/10>
  - <https://github.com/wx257osn2/qoixx/pulls?q=is%3Apr>
  - <https://github.com/wx257osn2/qoixx/pull/23>
  - <https://github.com/wx257osn2/qoixx/pull/30>
  - <https://github.com/wx257osn2/qoixx/pull/30/files>
  - <https://github.com/wx257osn2/qoixx/pull/32>
  - <https://github.com/wx257osn2/qoixx/commit/81c57c9>
  - <https://github.com/wx257osn2/qoixx/commits/master>
  - <https://github.com/ShadowMitia/libqoi/issues/1>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/wx257osn2/qoixx`) · [data/wave10/enrich/raw/github_com_wx257osn2_qoixx.json](../../../data/wave10/enrich/raw/github_com_wx257osn2_qoixx.json) (enrichment confidence 0.8)

</details>
