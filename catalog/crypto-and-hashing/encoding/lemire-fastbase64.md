# fastbase64 (lemire)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `C` · `no license` · 🔴 abandoned

> Archived research AVX2 base64 codec from the Muła–Lemire paper; roughly 7-11x faster than Chrome's scalar codec on Skylake.

| | |
|---|---|
| **Beats** | base64 (glibc/Linux base64 utility and Google Chrome's base64 implementation) |
| **Claimed result** | Paper (i7-6700, GCC 5.3 -O3 -march=native): for large random inputs the AVX2 codec uses about 0.25 cycles per input byte, against Chrome's codec at about 2.7 (encode) and 1.8 (decode). The paper calls this 'eleven times faster at encoding and over seven times faster at decoding'. In Table VI, decoding real files takes 0.21-0.27 cycles/byte against Chrome's 1.8-2.1 (lena: 0.21 vs 1.8). In an independent table in the Turbo-Base64 README (i7-9700K, gcc 11.2, 1 MB), fb64avx2 runs at 23,686/21,231 MB/s encode/decode against Google Chrome base64 at 2,541/4,289 MB/s (about 9.3x encode and 4.9x decode, derived from page data). |
| **Workload** | Single-threaded base64 decoding of real base64 payloads: the lena, peppers and mandril JPEGs, a Moby Dick quote, and Google and Bing inline images. Encoding and decoding of random data of varying size. Measured in cycles per input byte with rdtsc, Turbo Boost disabled, minimum of 500 runs. Secondary: 1 MB encode/decode in the Turbo-Base64 README table. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700 (Skylake) @ 3.4 GHz, Turbo Boost disabled, 32 GB DDR4-2133 (paper); Intel i7-9700K @ 3.6 GHz (Turbo-Base64 table) |
| **Compiler and flags** | GNU GCC 5.3, -O3 -march=native (paper; the repo Makefile also sets -O3 -march=native -mavx2). Turbo-Base64 table: gcc 11.2, no flags stated. |
| **Adoption** | 445 stars, repo archived |
| **Last commit** | 2024-04-04 |
| **Links** | [repository](https://github.com/lemire/fastbase64) · [benchmark](https://arxiv.org/abs/1704.00605) |

## Verdict

The paper measured on an i7-6700 Skylake at 3.4 GHz with Turbo off, GCC 5.3 -O3 -march=native, taking the minimum rdtsc count over 500 runs. There the AVX2 codec needs about 0.25 cycles/byte on large random inputs, against 2.7 (encode) and 1.8 (decode) for Chrome 56's modp_b64, and it decodes six real files at 0.21-0.27 cycles/byte against Chrome's 1.8-2.1 and Klomp AVX2's 0.43-0.53. In Turbo-Base64's independent 1 MB table (i7-9700K, gcc 11.2) fb64avx2 reaches 23,686/21,231 MB/s encode/decode against Chrome's 2,541/4,289, but by then it trails aklomp's b64avx2 (26,153/22,515).

## Use it when

- Reproducing or extending Muła & Lemire (ACM TWEB 2018): this repo is the paper's artifact, with basic_benchmark.c, the test images and the rival codecs in one harness.
- Reading a minimal reference of the AVX2 base64 kernels (about 200 lines in src/fastavxbase64.c) before porting the technique into your own code.
- Only if you must vendor a tiny C kernel and cannot take simdutf: strict, padded, whitespace-free standard-alphabet data of about 200 bytes or more (data URIs, embedded images) on AVX2 x86-64 that you build for yourself.

## Skip it when

- Anything in production: the README says it is unmaintained research code and not for production, the repo is archived, and the author sends users to simdutf.
- MIME/PEM or other input with line breaks or spaces, URL-safe alphabet, or missing padding: the Chromium fallback returns MODP_B64_ERROR and there are no options.
- Short strings: the paper says that under about 100 bytes the AVX2 codec is no faster than scalar code.
- The AVX-512BW encoder: issue #17 (2024) reports garbage output for a 64-byte input on Sapphire Rapids while still returning the expected length. It was closed without a fix.
- Non-x86 targets: the POWER9 AltiVec port is only about 2-2.4x Chrome at 2 KB (decode 0.32 vs 0.65 ns/byte, encode 0.27 vs 0.66), the NEON file is decode-only and not built by the Makefile, and there is no aarch64 encoder.

## How it is fast

Encoding: a vpshufb puts each 3-byte group into a 32-bit lane. A vpmulhuw/vpmullw multiply-shift then extracts all four 6-bit fields at once, and ASCII translation uses a saturating-subtract/compare range index into a 16-entry vpshufb offset table instead of a 64-byte lookup table. Decoding uses aqrit's nibble-LUT scheme: two vpshufb lookups on the high and low nibbles produce bitmasks whose vptest catches any invalid byte, and a third vpshufb supplies the per-range offset. Then vpmaddubsw + vpmaddwd pack four 6-bit values into 24 bits, and vpshufb + vpermd compact 32 characters into 24 bytes. The paper counts about 11 vector instructions per 24 input bytes for encoding and 14 per 32 for decoding, which is about 0.25 cycles/byte on Skylake. Tails shorter than 28 bytes (encode) or 45 characters (decode) go to the Chromium scalar code.

## Compared with alternatives

For real use, pick simdutf (maintained descendant of this algorithm, runtime dispatch, whitespace and URL-safe support), aklomp/base64 (maintained C99 library that adopted these kernels) or Turbo-Base64 (29,086/29,748 MB/s vs fastbase64's 23,686/21,231 MB/s encode/decode in the same i7-9700K table). Pick fastbase64 only to reproduce the paper or to read the smallest reference version of the AVX2 kernels.

## Integration

| | |
|---|---|
| **Form** | source-drop (Makefile can also build libfastbase64.a/.so) |
| **Dependencies** | none (C99 and &lt;x86intrin.h&gt;) |
| **Minimum toolchain** | C99 compiler with AVX2 intrinsics; the paper used GCC 5.3 -O3 -march=native; the Makefile's -Wpsabi flag is GCC-only (clang warns) |
| **Platforms** | x86-64 with AVX2 (AVX-512BW variant optional); ppc64le POWER9 AltiVec port; NEON decoder source only; no runtime CPU dispatch |
| **Thread safety** | Not documented. The functions are stateless and read only static const tables (per the source), so concurrent calls on separate buffers look safe. |
| **Drop-in for the baseline** | partial — same signature and return convention as Chromium's modp_b64 (chromium_base64_encode/decode), so it swaps in where that API is used; not a drop-in for coreutils/glibc base64, OpenSSL or any whitespace-tolerant decoder |

## Gotchas

- No CPU detection: fast_avx2_\* crashes with SIGILL on CPUs without AVX2, and the Makefile builds everything with -march=native, so the binaries are not portable.
- Each decode step stores 32 bytes but advances only 24, so the region past the current output position gets scratch bytes. By our reading this stays inside a buffer sized for the decoded output. On invalid input the function returns MODP_B64_ERROR after writing partial output.
- The encoder's first load is a masked vpmaskmovd from str-4 (that lane is masked, so no fault per Intel docs). Turbo-Base64's source calls fastbase64 'unsafe, can reads/writes beyound i/o buffers'; we did not confirm that for the AVX2 path, and the unit tests cover only three fixed strings plus an invalid-character sweep.
- Decoding requires a length that is a multiple of 4. The header says encode returns strlen+1, but the code returns strlen and writes a NUL terminator.

## Known shortcomings

- Research artifact of the Muła & Lemire paper (arXiv 1704.00605): numbers are from GCC 5.3 -O3 -march=native on an i7-6700 (Skylake, 2017). The Turbo-Base64 comparison figures come from a closed third-party harness (C-level on their own).
- Archived; README says research-only and points to simdutf. Strict input only (no whitespace, no URL-safe, length must be a multiple of 4); no runtime dispatch (SIGILL without AVX2); no gain under \~100 bytes. AVX-512BW encoder emits garbage on 64-byte input (#17, closed unfixed); NEON is decode-only and not built. In the independent Turbo-Base64 1 MB table it trails aklomp/base64 and Turbo-Base64 (23.7/21.2 vs 26.2/22.5 and 29.1/29.7 GB/s).

## Caveats and trade-offs

The paper's numbers date from 2017. The repo is archived, and its README says it is unmaintained research code, not for production, and that users should switch to simdutf. The AVX2 codec needs AVX2 hardware and falls back to scalar code for short inputs (under about 100 bytes it gains nothing). Turbo-Base64's source comments call fastbase64 'unsafe, can reads/writes beyound i/o buffers'; that is a competitor's claim and is unverified.

No declared license (NOASSERTION) — can be studied/reimplemented but not copied; project archived, no further maintenance

## Maintenance

Archived, with the last commit on 2024-04-04; the README and issue #17 call it obsolete and point to simdutf. The LICENSE file is standard BSD-2-Clause text (GitHub shows NOASSERTION), so vendoring is allowed, but every fix is yours.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** A peer-reviewed paper (Muła & Lemire, ACM TWEB, doi 10.1145/3132709, arXiv 1704.00605) names this repo as its software. The paper benchmarks the codec against Chrome's codec (src/chromiumbase64.c) using benchmarks/basic_benchmark.c, and it states GNU GCC 5.3, -O3 -march=native and an Intel i7-6700, so every tier A condition is met. The cited Turbo-Base64 page on its own would support only C, because its comparison harness is not public and it gives no flags.
- **Verifier notes:** I moved the evidence to the peer-reviewed paper, whose artifact is this repo. The Turbo-Base64 numbers in the original claim are accurate and belong to the fb64avx2 row, but that harness is closed and gives no flags. The paper and algorithm are the same as in the WojciechMula/base64simd record in this batch, and the successor is simdutf, so dedupe with care. GitHub reports the license as NOASSERTION, but the LICENSE file is the standard BSD 2-clause text.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** Turbo-Base64 1 MB table: fastbase64 23.7/21.2 GB/s enc/dec vs aklomp 26.2/22.5, TB64 29.1/29.7.
- **Pages the verifier opened:**
  - <https://github.com/powturbo/Turbo-Base64#readme>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Base64/master/README.md>
  - <https://github.com/lemire/fastbase64>
  - <https://raw.githubusercontent.com/lemire/fastbase64/master/README.md>
  - <https://raw.githubusercontent.com/lemire/fastbase64/master/LICENSE>
  - <https://raw.githubusercontent.com/lemire/fastbase64/master/Makefile>
  - <https://arxiv.org/abs/1704.00605>
  - <https://arxiv.org/pdf/1704.00605>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Base64/master/tb64app.c>
- **Sources the enricher read:**
  - <https://github.com/lemire/fastbase64>
  - <https://raw.githubusercontent.com/lemire/fastbase64/master/README.md>
  - <https://github.com/lemire/fastbase64/blob/master/include/fastavxbase64.h>
  - <https://github.com/lemire/fastbase64/blob/master/src/fastavxbase64.c>
  - <https://github.com/lemire/fastbase64/blob/master/include/chromiumbase64.h>
  - <https://github.com/lemire/fastbase64/blob/master/src/chromiumbase64.c>
  - <https://github.com/lemire/fastbase64/blob/master/include/fastavx512bwbase64.h>
  - <https://github.com/lemire/fastbase64/blob/master/src/fastavx512bwbase64.c>
  - <https://github.com/lemire/fastbase64/blob/master/include/altivecbase64.h>
  - <https://github.com/lemire/fastbase64/blob/master/src/altivecbase64.c>
  - <https://github.com/lemire/fastbase64/blob/master/src/neonbase64.cc>
  - <https://github.com/lemire/fastbase64/blob/master/tests/unit.c>
  - <https://github.com/lemire/fastbase64/blob/master/Makefile>
  - <https://github.com/lemire/fastbase64/blob/master/LICENSE>
  - <https://github.com/lemire/fastbase64/blob/master/results/ice_lake.gnuplot>
  - <https://github.com/lemire/fastbase64/blob/master/results/ice_lake_dec.txt>
  - <https://github.com/lemire/fastbase64/blob/master/results/ice_lake_enc.txt>
  - <https://github.com/lemire/fastbase64/blob/master/results/power9_dec.txt>
  - <https://github.com/lemire/fastbase64/blob/master/results/power9_enc.txt>
  - <https://github.com/lemire/fastbase64/commits/master>
  - <https://github.com/lemire/fastbase64/issues?q=is%3Aissue>
  - <https://github.com/lemire/fastbase64/pulls?q=is%3Apr>
  - <https://github.com/lemire/fastbase64/issues/17>
  - <https://github.com/lemire/fastbase64/issues/15>
  - <https://github.com/lemire/fastbase64/issues/11>
  - <https://github.com/lemire/fastbase64/issues/3>
  - <https://arxiv.org/abs/1704.00605>
  - <https://arxiv.org/pdf/1704.00605>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Base64/master/README.md>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Base64/master/tb64app.c>
  - <https://github.com/simdutf/simdutf#readme>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/lemire/fastbase64`) · [data/wave7/enrich/raw/github_com_lemire_fastbase64.json](../../../data/wave7/enrich/raw/github_com_lemire_fastbase64.json) (enrichment confidence 0.85)

</details>
