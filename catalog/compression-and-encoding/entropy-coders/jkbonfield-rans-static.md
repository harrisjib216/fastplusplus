# rans_static (rANS_static4x16, r32x16b_avx2 SIMD rANS experiments)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `no license` · 🔴 abandoned

> James Bonfield's 2014-2018 static rANS experiments; the 32-way AVX2 decoder runs about 4x faster than the CRAM rANS_static4c codec.

| | |
|---|---|
| **Beats** | rANS_static4c (4-way interleaved scalar rANS, the CRAM variant) and arith_static (unrolled static arithmetic coder), both in the same repo |
| **Claimed result** | Order-0 decode, gcc 6.2.0, Q8: r32x16b_avx2 1430.6 MB/s vs rANS_static4c 335.2 MB/s and arith_static 146.5 MB/s; Q40: 1415.0 MB/s vs 360.4 MB/s (rANS_static4c) and 144.0 MB/s (arith_static). Order-1 decode, gcc: Q8 1039.4 vs 280.7 MB/s, Q40 985.9 vs 204.5 MB/s (rANS_static4c). Scalar rANS_static4x16 order-0 decode 664.5 MB/s (Q8) vs 335.2 MB/s for rANS_static4c. Ratios of about 4.3x (Q8) and 3.9x (Q40) order-0 decode for r32x16b_avx2 over rANS_static4c are derived from page data. Encode is not much faster (534.7 vs 294.2 MB/s Q8 order-0). |
| **Workload** | Order-0 and order-1 static-model encode and decode of two DNA-sequencing quality-value files (Q8: 73,124,567 bytes; Q40: 94,602,182 bytes), single thread, reported in MB/s with compressed size. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Core(TM) i5-4570 CPU @ 3.20GHz (from /proc/cpuinfo, Ubuntu Trusty) |
| **Compiler and flags** | gcc 6.2.0, clang 3.7.0 and icc 15.0.0 (README); Makefile CFLAGS=-O3 -g -mtune=native -Wall, with BLK_SIZE 1013\*1047 and NTRIALS=1 in DEFINES |
| **Adoption** | 92 stars, 6 forks; README points to samtools/htscodecs as the maintained successor |
| **Last commit** | 2022-03-15 |
| **Links** | [repository](https://github.com/jkbonfield/rans_static) · [benchmark](https://github.com/jkbonfield/rans_static) |

## Verdict

On a Haswell i5-4570 with gcc 6.2.0, single-threaded in-memory order-0 decode of two DNA quality-score files (73 MB and 95 MB) ran at 1430.6 and 1415.0 MB/s for r32x16b_avx2 against 335.2 and 360.4 MB/s for the CRAM codec rANS_static4c (about 4.3x and 3.9x, derived from page data); encode improved only 1.8x and compressed size was within 0.02%. The clang 3.7 and icc 15 runs show the same ordering (1220.7 and 1359.0 MB/s on Q8); the test files are not shipped.

## Use it when

- Studying or porting SIMD rANS: the AVX2 32-state decoder is a compact, readable worked example of the gather-plus-permute renormalisation trick.
- Benchmarking your own entropy coder against the historical CRAM-era codecs (rANS_static4c, arith_static) with the same harness.
- Low-alphabet, statistically stable byte data such as sequencing quality scores, where a static order-0 model compressed in \~1 MB blocks is enough.
- Decode-heavy workloads on AVX2 x86-64: decode reached 1430.6 MB/s versus encode 534.7 MB/s on Q8 order-0.

## Skip it when

- Production code: there is no licence (issue #1 asking for one was closed in March 2022 and the README now redirects to htscodecs), so you cannot legally ship it.
- Untrusted input: the decoders parse the frequency table and read the stream without bounds checks on in_size, and only an assert (after the table is filled) checks that frequencies stay under TOTFREQ.
- Adaptive or context-mixing needs: models are static per block and the frequency table is stored in each block, so tiny blocks pay heavily for the header.
- Non-x86 or pre-AVX2 CPUs for the fast path; the scalar 4x16 coder is the portable fallback at about half the AVX2 decode speed.
- Order-1 encoding speed: the r32x16b_avx2 order-1 encoder is scalar (TODO in the source), so order-1 encode stays near 237 MB/s, and r32x16_avx2 order-1 fails (ERR in the README).

## How it is fast

Interleaved rANS: many independent rANS states share one output buffer, so decode steps have no dependency on each other and can run in SIMD lanes. Moving from 8-bit to 16-bit renormalisation (state kept as 15+16 bits, as in ryg's SIMD variant) means at most one renormalisation per symbol, which alone roughly doubles scalar decode (rANS_static4x16). The r32x16b_avx2 decoder keeps 32 states in four AVX2 registers, looks up a packed freq/base/symbol table with _mm256_i32gather_epi32, updates states with _mm256_mullo_epi32, and handles renormalisation by compress-and-permute (_mm256_permutevar8x32_epi32 with a precomputed permute table) to load 16-bit words only for the lanes that need them.

## Compared with alternatives

Pick it only as a reference to learn the technique: for real use, htscodecs (the same author's maintained, BSD-licensed successor with more aggressive SIMD, per this README) and hypersonic-rANS (which reports about 3 GiB/s decode on enwik8 on newer hardware) are licensed and newer, and ryg_rans is the public-domain scalar origin.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C standard library; x86intrin.h and the in-repo permute.h for SIMD variants; OpenMP flag in the Makefile) |
| **Minimum toolchain** | C99 compiler with AVX2 intrinsics; tested with gcc 6.2.0, clang 3.7.0 and icc 15.0.0 |
| **Platforms** | x86-64; AVX2 (-march=core-avx2) for the r\*_avx2 variants, SSE4.1 for r8x16_sse, AVX-512 (KNL) variants commented out of the Makefile; scalar variants are portable |
| **Thread safety** | not documented; the codec functions use stack-local tables and caller-provided or malloc'd buffers, so separate calls on separate buffers look independent |
| **Drop-in for the baseline** | partial: same function-call shape as rANS_static4c, but the 4x16 and 32x16 streams are not compatible with CRAM's 4x8/4c format |

## Gotchas

- Each file defines its own copies of the ryg_rans helpers and similarly named functions (the README warns r16x16_avx2 exposes rans_compress_O1_4x16), so linking several variants into one binary clashes.
- Order-1 4x16-family tables use 9 bits (TF_SHIFT_O1 9) against 12 bits in 4c/4x8, so order-1 speed comparisons are not like-for-like and compression is slightly worse.
- The README calls the SIMD codecs experimental, with many warnings and commented-out code; some order-1 SIMD paths do not work.
- Benchmarks read the input in BLK_SIZE blocks (1013\*1047 in the Makefile) and time in-memory encode and decode with gettimeofday, with NTRIALS=1 by default in the Makefile.

## Known shortcomings

- Tier C: README numbers reproduce (i5-4570, gcc 6.2.0 / clang 3.7.0 / icc 15.0.0) but the Q8/Q40 inputs are not shipped and the flags are not tied to runs; the order-1 comparison is not like for like (9-bit vs 12-bit tables) and the order-1 encoder is not SIMD. No licence, so reference; htscodecs is the maintained successor. Last commit 2022-03-15.
- No licence file (issue #1 asked for one in 2022 and was closed without one; README points to htscodecs, which is BSD). Decoders do not check in_size. Frequency-table overflow is caught only by an assert that runs after s3[] is written, so unsafe on untrusted input. The r32x16b_avx2 order-1 encoder is scalar. Benchmark harness defaults to NTRIALS=1. Same-named functions in different variant files clash if linked together.

## Caveats and trade-offs

First-party numbers only. The Q8/Q40 test files are not shipped in the repo, so the run cannot be reproduced exactly (sample lines are shown in the README). The baselines are the author's own earlier rANS and arithmetic coder variants (rANS_static4c is the CRAM codec), not Huffman, FSE or ryg_rans itself. Order-1 results are not like-for-like: the README says the 4x16 family uses 9-bit order-1 frequency tables against 12 bits in 4x8/4c, and r32x16b_avx2 compresses order-1 slightly worse (15,872,840 vs 15,849,499 bytes on Q8). The r32x16b_avx2 order-1 encoder is not SIMD (TODO in the source). The third icc block is labelled 'order 0' but appears to be the order-1 run (README typo). The Makefile flags (-O3 -g -mtune=native, plus -march=core-avx2 for the AVX2 builds) are the current ones; the README does not state which flags produced the tables. Compilers are old (gcc 6.2, clang 3.7, icc 15) and the test CPU is a 2013 Haswell. There is no licence file, and the GitHub sidebar shows none. Embedded ryg_rans code is public domain, but the repo itself states no licence, so treat it as reference only. The maintained, more heavily SIMD-optimised successor htscodecs is already catalogued. Compiled AVX-512 variants exist in the source but are commented out of the Makefile and absent from the README results.

Static (non-adaptive) order-0/1 models with a frequency table sent in the stream; 16-bit renormalisation and 32 interleaved states cost a little compression (Q8 order-0: 16,853,107 bytes for r32x16b_avx2 vs 16,850,374 for rANS_static4c). Needs AVX2 for the fast variants; the order-1 SIMD variants are described as non-functioning or not updated for some entries (r32x16_avx2 shows ERR for order 1). The author calls the SIMD codecs experimental with many warnings and commented-out code.

## Maintenance

Abandoned: last code commit 2018-04-09 and a README-only update in March 2022 pointing users to samtools/htscodecs; no licence, so reference only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Benchmarks section times r32x16b_avx2, rANS_static4x16, rANS_static4c (the CRAM rANS codec) and arith_static on an i5-4570 with gcc 6.2.0, clang 3.7.0 and icc 15.0.0, and every quoted number matches. The harness (TEST_MAIN in each .c) is public, but the Q8/Q40 inputs are not shipped and the README does not tie the Makefile flags to these runs, so the first-party numbers are not reproducible enough for A; C stands.
- **Verifier notes:** Every number in claimed_speedup matches the README tables (derived ratios correctly labelled). License null and usability reference confirmed (no LICENSE/COPYING file; sidebar shows none). Last commit 2022-03-15 (a README update; the last code commit was 2018-04-09) confirmed, which makes it abandoned. Not a fork.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/jkbonfield/rans_static>
  - <https://github.com/jkbonfield/rans_static/commits>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/README.md>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/r32x16b_avx2.c>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/rANS_static4c.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/README.md>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/r32x16b_avx2.c>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/rANS_static4x16.h>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/rANS_static.h>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/rANS_static4c.c>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/rANS_static4x16pr.c>
  - <https://raw.githubusercontent.com/jkbonfield/rans_static/HEAD/permute.h>
  - <https://github.com/jkbonfield/rans_static/issues?q=is%3Aissue>
  - <https://github.com/jkbonfield/rans_static/issues/1>
  - <https://github.com/jkbonfield/rans_static/commits>
  - <https://raw.githubusercontent.com/samtools/htscodecs/HEAD/LICENSE.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/jkbonfield/rans_static`) · [data/wave9/enrich/raw/github_com_jkbonfield_rans_static.json](../../../data/wave9/enrich/raw/github_com_jkbonfield_rans_static.json) (enrichment confidence 0.8)

</details>
