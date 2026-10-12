# Faster Base64 Encoding/Decoding using AVX2 (base64simd)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-2-Clause` · 🟡 stale

> Muła's research harness of SSE/AVX2/AVX-512/NEON/RVV base64 kernels; origin of the AVX2 algorithm measured 7-11x faster than Chrome's.

| | |
|---|---|
| **Beats** | base64 |
| **Claimed result** | Paper: for large random inputs the AVX2 codec uses about 0.25 cycles per input byte, against Chrome's codec at about 2.7 (encode) and 1.8 (decode). The paper calls this 'eleven times faster at encoding and over seven times faster at decoding'; the abstract rounds to about 10x and 7x. In Table VI, decoding real files takes 0.21-0.27 cycles/byte against Chrome's 1.8-2.1. The repo README, comparing against its own scalar code only, reports 2-4x faster encoding and 2-2.7x faster decoding. |
| **Workload** | Single-threaded encoding/decoding of byte streams to/from base64 on a Skylake processor, measured in CPU cycles per input byte, vs Google Chrome's base64 codec |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700 (Skylake) @ 3.4 GHz, Turbo Boost disabled, 32 kB L1d / 256 kB L2 / 8 MB L3 (paper Section 5) |
| **Compiler and flags** | GNU GCC 5.3, -O3 -march=native |
| **Adoption** | 172 stars; underlying algorithm merged into simdutf (Node.js, Chromium, WebKit) |
| **Last commit** | 2025-02-21 |
| **Links** | [repository](https://github.com/WojciechMula/base64simd) · [benchmark](https://arxiv.org/abs/1704.00605) |

## Verdict

The Chrome comparison comes from the Muła–Lemire paper, whose measured codec and harness live in lemire/fastbase64: on an i7-6700 Skylake at 3.4 GHz with Turbo off and GCC 5.3 -O3 -march=native, about 0.25 cycles/byte against Chrome's 2.7 (encode) and 1.8 (decode). This repo's own data compares only with its scalar code. On the same i7-6700, AVX2 encoding of 192 MiB is 4.39x faster than 64-bit scalar (GCC 5.3), and AVX2 decoding is 2.9x faster than improved scalar (GCC 5.4.1). On a Xeon W-2104 (GCC 8.1), AVX2 decodes at 0.22 cycles/op against 2.05 for scalar, and AVX512BW at 0.14.

## Use it when

- Choosing or porting a base64 kernel for a specific ISA: variants are benchmarked side by side, with stored results for Westmere, Bulldozer, Haswell, Skylake, Knights Landing, Skylake-X, Cannon Lake and ARMv7.
- Research or teaching alongside Muła's 0x80.pl articles and the 2018 paper: each lookup and pack idea is isolated in its own function.
- Lifting one AVX2 or AVX-512 kernel (about 100 lines) into a codec of your own that already handles tails, padding and errors (BSD-2-Clause; issue #8 says the author is fine with reuse under Apache-2).
- Experimenting with RISC-V Vector base64, including a whitespace-skipping RVV decoder added in 2024 (the author tested it only on the spike simulator; issue #9 has user numbers from C908/C920 boards).

## Skip it when

- As a base64 codec: no tail or '=' handling, no public API and no length helpers. The README's 'Known problems' section says so and recommends aklomp/base64 instead.
- URL-safe alphabet or whitespace-tolerant decoding on x86: neither is implemented, and issue #7 (URL-safe) has been open since 2020.
- Code built without exceptions or in C: invalid input is reported only by throwing a C++ exception.
- RVV encoders: PR #10 (merged 2025) reports that on a Milk-V Jupiter board only a few RVV encode variants passed verify, and the others crashed on free() of the output buffer.
- Assuming AVX-512 target names match hardware: issue #5 (still open) found that a kernel labelled AVX512BW used vpermb (AVX512VBMI) and crashed with SIGILL on Skylake-SP.

## How it is fast

Encoding: a pshufb places each 3-byte group into a 32-bit lane, then vpmulhuw/vpmullw with constants 0x04000040 and 0x01000010 shift all four 6-bit fields at once. The 'pshufb improved' lookup then turns 6-bit values into ASCII by computing a range index and adding an offset taken from a 16-entry pshufb table. Decoding: the 'pshufb bitmask' lookup (aqrit's idea from issue #3) classifies each byte through high- and low-nibble pshufb tables, validates 32 bytes with a single test and adds the per-range offset. The 'multiply-add' pack uses pmaddubsw + pmaddwd to merge four 6-bit fields into 24 bits, and a pshufb compacts them. These are the techniques of the Muła–Lemire ACM TWEB paper; the repo also keeps the slower alternatives (naive, byte-blend, BMI2 pext packing) for comparison.

## Compared with alternatives

Pick base64simd only to study or benchmark individual kernels across ISAs (x86 generations, XOP, Knights Landing, NEON, RVV) in one harness. To ship a codec, use simdutf (maintained, whitespace/URL-safe support, cites this paper, and its README lists Node.js, Bun, WebKit and Chromium as users), aklomp/base64 (the spec-complete codec this README recommends) or lemire/fastbase64 (the paper's exact AVX2 codec with the Chrome comparison harness).

## Integration

| | |
|---|---|
| **Form** | source-drop (header-less .cpp kernels #included into benchmark programs) |
| **Dependencies** | none for the kernels; Python scripts only for result tables |
| **Minimum toolchain** | C++14 (-std=c++14); GCC 5.3+ for the AVX-512 targets per the README; RVV needs a compiler with RVV intrinsics (-march=rv64gcv) |
| **Platforms** | x86-64 (SSE4, AVX2+BMI2, AVX-512F/BW/VBMI/VL, AMD XOP); 32-bit ARMv7 NEON (Makefile uses -mfpu=neon); RISC-V RVV; the ISA is chosen at compile time only, with no runtime dispatch |
| **Thread safety** | Not documented. The SIMD kernels are pure functions over caller buffers, but the scalar decoder tables are mutable static arrays filled by prepare_lookup(), so call it once before using them from several threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- The AVX2 encoder loads 16 bytes at i and at i+12 for every 24-byte block, so the last block reads 4 bytes past the end of the input. The harness pads its buffers; your code must do the same or handle the tail separately.
- The 'speedup' columns are relative to the repo's own scalar code, not to Chrome or glibc. On the i7-6700, AVX2 encode is 4.39x the 64-bit scalar, and AVX2 decode is 2.9x the 'improved scalar' but 7.0x the plain scalar.
- The BMI2 pext packing variants are slower than pure AVX2. On the Skylake decode run, AVX2 & BMI2 took 0.0199 against 0.0071 for AVX2 pshufb-bitmask/multiply-add.
- The README lists no RISC-V support and does not describe the newer check_ws/benchmark_rvv targets; the Makefile is the real documentation.

## Known shortcomings

- The paper's benchmark code and codec live in lemire/fastbase64, not this repo; this repo's own benchmark compares only against its own scalar code (2-4x encode, 2-2.7x decode). No tail/padding handling. Overlaps lemire/fastbase64.
- Research harness, not a codec: no tail or '=' handling, no API, errors are C++ throws, decode size must be a multiple of 32. AVX2 encoder over-reads 4 bytes past the last block. The 'AVX512BW' kernel actually needs VBMI (SIGILL, #5 open); RVV encoders mostly fail verification or crash (PR #10). No URL-safe alphabet (#7).

## Caveats and trade-offs

The paper's measured codec and its benchmark harness are in lemire/fastbase64; this repo is Muła's research harness of algorithm variants (SSE, AVX2, AVX-512, BMI2, NEON, XOP), each benchmarked only against its own scalar versions. Its README says the code does not process the data tail or '=' padding, so it is not a spec-complete codec; it points users to aklomp/base64 and lemire/fastbase64 for that. The paper, the algorithm and the Chrome comparison are the same as in the lemire/fastbase64 record.

Requires x86 SSE/AVX2/AVX-512 or ARM NEON; falls back to scalar on unsupported CPUs; strict base64 validation

## Maintenance

Stale rather than dead: not archived, but the only activity since 2019 is 2024-25 RISC-V Vector work, with the last commit on 2025-02-21. The code is BSD-2-Clause and easy to copy kernel by kernel, but it is not a usable codec as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** A peer-reviewed paper (ACM TWEB, arXiv 1704.00605) shows the Muła/Lemire AVX2 algorithms beating Chrome's codec by about 11x on encode and 7x on decode, with GCC 5.3 -O3 -march=native on an i7-6700 stated. However, the paper's public benchmark harness and the codec it measured live in lemire/fastbase64 (benchmarks/basic_benchmark.c), not in this repo. base64simd's own benchmark programs and results (decode/results/\*.csv, encode/results/\*.txt, benchmark_results/) compare only against its own scalar routines. That makes it B, not A.
- **Verifier notes:** The numbers are quoted correctly from the paper, but they measure fastbase64's implementation, not this repo's code, so I set the tier to B. Consider merging this entry with lemire/fastbase64, or keeping it as the algorithm-origin entry. The metadata checks out: BSD-2-Clause, 172 stars, not a fork, last commit 2025-02-21 (stale). I did not verify the simdutf/Node/Chromium usage claim.
- **Fields the verifier corrected:** `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** Own benchmark (i7-6700): encode 4.39x, decode 2.9x/7.0x vs its own scalar code.
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/1704.00605>
  - <https://arxiv.org/pdf/1704.00605>
  - <https://github.com/WojciechMula/base64simd>
  - <https://github.com/WojciechMula/base64simd/blob/master/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/base64simd/master/decode/results/skylake-i7-6700-gcc5.4.1-avx2.csv>
- **Sources the enricher read:**
  - <https://github.com/WojciechMula/base64simd>
  - <https://github.com/WojciechMula/base64simd/blob/master/README.rst>
  - <https://github.com/WojciechMula/base64simd/blob/master/Makefile>
  - <https://github.com/WojciechMula/base64simd/blob/master/config.h>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/README.rst>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/Makefile>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/decode.avx2.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/decoders.avx2.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/lookup.avx2.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/pack.avx2.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/decode.common.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/decode.scalar.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/decode.rvv.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/check_ws.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/decode/function_registry.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/encode/README.rst>
  - <https://github.com/WojciechMula/base64simd/blob/master/encode/Makefile>
  - <https://github.com/WojciechMula/base64simd/blob/master/encode/encode.avx2.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/encode/lookup.avx2.cpp>
  - <https://github.com/WojciechMula/base64simd/blob/master/encode/encode.scalar.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/base64simd/master/encode/results/skylake-i7-6700-gcc5.3.0-avx2.txt>
  - <https://raw.githubusercontent.com/WojciechMula/base64simd/master/decode/results/skylake-i7-6700-gcc5.4.1-avx2.csv>
  - <https://github.com/WojciechMula/base64simd/blob/master/benchmark_results/skylakex/results.meta>
  - <https://github.com/WojciechMula/base64simd/blob/master/benchmark_results/skylakex/decode_results.txt>
  - <https://github.com/WojciechMula/base64simd/blob/master/benchmark_results/skylakex/encode_results.txt>
  - <https://github.com/WojciechMula/base64simd/blob/master/benchmark_results/cannonlake/decode_cannonlake.txt>
  - <https://github.com/WojciechMula/base64simd/commits/master>
  - <https://github.com/WojciechMula/base64simd/issues?q=is%3Aissue>
  - <https://github.com/WojciechMula/base64simd/issues/5>
  - <https://github.com/WojciechMula/base64simd/issues/7>
  - <https://github.com/WojciechMula/base64simd/issues/8>
  - <https://github.com/WojciechMula/base64simd/issues/9>
  - <https://github.com/WojciechMula/base64simd/pull/10>
  - <https://arxiv.org/abs/1704.00605>
  - <https://arxiv.org/pdf/1704.00605>
  - <https://arxiv.org/abs/1910.05109>
  - <https://github.com/lemire/fastbase64>
  - <https://github.com/simdutf/simdutf#readme>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/wojciechmula/base64simd`) · [data/wave7/enrich/raw/github_com_wojciechmula_base64simd.json](../../../data/wave7/enrich/raw/github_com_wojciechmula_base64simd.json) (enrichment confidence 0.85)

</details>
