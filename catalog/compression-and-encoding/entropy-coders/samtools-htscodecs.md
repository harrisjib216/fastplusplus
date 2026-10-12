# htscodecs (32-way interleaved SIMD rANS)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> CRAM 3.1 codec library whose 32-way SIMD rANS decodes about 2.7x faster than its 4-way rANS and 3.8x faster than FSE.

| | |
|---|---|
| **Beats** | Scalar 4-way rANS4x16 codec in the same library (r4x16 -o0) and FSE order-0 (tANS), both rows on the PR's tables |
| **Claimed result** | PR #26, high-complexity HiSeq quals (101 MB), Xeon Gold 6142, MB/s encode/decode: FSE order-0 416.3/564.4; r4x16 -o0 (4-way) 428.8/773.9; 32x16 (-o4) scalar 358.8/642.4, SSE4 360.9/954.0, AVX2 578.7/1516.0, AVX512 809.9/2124.8. AVX512 decode is about 2.7x r4x16 -o0 and 3.8x FSE (derived from page data); SSE4/scalar 32-way encode is slower than 4-way. Graviton-2 order-0: 4x16 -o0 347.6/452.6, 32x16 scalar 343.8/437.3, NEON 365.4/736.2. |
| **Workload** | rANS 4x16 versus new 32-way unrolled rANS32x16 (scalar, SSE4.1, AVX2, AVX512, ARM NEON) on high-complexity test data, encode and decode MB/s, as reported in samtools/htscodecs pull request 26. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6142 2.60 GHz; AWS Graviton-2 |
| **Compiler and flags** | Ubuntu 18.04 system gcc (PR comment: gcc-7.5.0; gcc-11 encode 268.2 MB/s versus gcc-7 431.5 MB/s; clang-10 393.7 enc / 827.3 dec MB/s); optimisation flags not stated |
| **Adoption** | 40 stars; used by htslib / samtools CRAM 3.1 |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/samtools/htscodecs) · [benchmark](https://github.com/samtools/htscodecs/pull/26) |

## Verdict

In the author's PR #26 on an Intel Xeon Gold 6142 with Ubuntu 18.04's system gcc (flags not stated), 101 MB of HiSeq quality data decoded at 2124.8 MB/s with the AVX-512 32x16 codec versus 773.9 MB/s for the library's own 4-way rANS and 564.4 MB/s for FSE order-0; AVX2 gave 1516.0 MB/s. On Graviton-2 the NEON decoder reached 736.2 MB/s versus 452.6 MB/s for 4-way scalar.

## Use it when

- Order-0 or order-1 static entropy coding of byte streams in the tens-of-KB to MB range where decode speed matters, on x86-64 with AVX2 or AVX-512, or AArch64 with NEON.
- Reading or writing CRAM 3.1, or any format already built on htscodecs/htslib, where the 32x16 codec is part of the spec.
- Small-alphabet data (e.g. quality scores): the PACK and RLE transforms gave the highest rates in BENCHMARKS.md (r32x16-o132 AVX-512: 1050.6 MB/s encode, 3947.9 MB/s decode on 10 MB of NovaSeq qualities).
- When you need a production-hardened, fuzzed (OSS-Fuzz) rANS implementation under a BSD licence rather than a research prototype.

## Skip it when

- CPUs without SIMD: the scalar 32-way path is slower than the 4-way codec (PR #26: 358.8/642.4 vs 428.8/773.9 MB/s encode/decode), so use the 4x16 codec there.
- Peak raw decode speed on enwik8-like data: the hypersonic-rANS sibling reports its fastest AVX2 decoder about 1.27x faster than htscodecs rans32avx2 order-0 on a Ryzen 9 7950X.
- Encode-heavy pipelines with SSE4.1 only: the SSE4 32-way encoder (360.9 MB/s) is no faster than the scalar 4-way encoder.
- Adaptive modelling: the 32-way unrolling covers only static rANS; the adaptive arithmetic coder has no X32 variant and runs near 100 MB/s.
- MSVC-only builds: the build is autotools (configure/make) with GCC/Clang-style -m flags; native MSVC support is not documented.

## How it is fast

Interleaved rANS with 32 independent states and 16-bit renormalisation, so one state per SIMD lane: 8 lanes per AVX2 register, 16 per AVX-512 register, with SSE4.1 and AArch64 NEON versions and runtime CPUID/HWCAP dispatch. Renormalisation is vectorised by compressing the lanes that need a 16-bit word with precomputed permute tables (_mm256_permutevar8x32_epi32), and symbol-table lookups use a simulated gather built from scalar loads by default (true vpgather is opt-in via -DUSE_GATHER). The encoder transposes a 32x32 block of output so the decoder reads its streams contiguously, and order-1 tables live in thread-local storage to avoid malloc churn.

## Compared with alternatives

Pick htscodecs over hypersonic-rANS or rans-tricks when you need a maintained, fuzzed, BSD-licensed library with a stable on-disk format, NEON support and fast SIMD encoders, not just a fast decoder. Pick it over FiniteStateEntropy when decode throughput on AVX2/AVX-512 hardware matters more than portable scalar speed.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (autotools; also used as a git submodule of htslib) |
| **Dependencies** | libbz2 (optional, --disable-bz2; needed to decode some arith streams), pthreads (optional, NO_THREADS build), libm |
| **Minimum toolchain** | C99 compiler with GCC/Clang intrinsics; autoconf to regenerate configure from git; SIMD files compiled only if the compiler accepts -msse4.1/-mavx2/-mavx512f |
| **Platforms** | any (scalar); x86-64 SSE4.1+POPCNT/AVX2/AVX-512F and AArch64 NEON accelerated with runtime detection; Linux, macOS, FreeBSD, Windows (MinGW-style) mentioned in source and CI |
| **Thread safety** | Codec calls are reentrant; CPU detection runs once under pthread_once and scratch buffers are thread-local. A minor data race on the first rans4x16 call was fixed in 1.6.4 (July 2025). |
| **Drop-in for the baseline** | partial: the 32-way codec is a flag (RANS_ORDER_X32) on the same rans_compress_4x16 API as the 4-way baseline, but the byte stream is htscodecs-specific and not compatible with FSE/zstd entropy streams |

## Gotchas

- Intel GDS/Downfall microcode slows hardware AVX2/AVX-512 gathers 2-3x, so the default build uses simulated gathers, which cost 10-30% decode (up to 50% AVX-512 encode) on unpatched Intel CPUs; rebuild with CPPFLAGS=-DUSE_GATHER to opt back in.
- On AMD CPUs the dispatcher prefers AVX2 over AVX-512 when both exist (Zen4 gathers are slow); rans_set_cpu() can force encode/decode SIMD levels for testing.
- Security history: 1.5.2 (Oct 2023) fixed write overruns in fqzcomp and the name tokeniser, an 8-byte read overflow in the AVX2 rANS decoder (gcc builds) and an SSE4 order-1 mis-decode of the final 31 bytes; issue #154 (Sep 2026, open) reports CRAM 3.1 'small' encode failures with many 1 bp reads, suspected in fqzcomp.
- Throughput is compiler-sensitive: the PR notes gcc-11 encoded the 4x16 codec at 268.2 MB/s versus 431.5 MB/s with gcc-7; issue #128 reported rans_compress_to_4x16 failing on blocks above about 1.25 MiB (closed; resolution not read).

## Known shortcomings

- Tier C: BENCHMARKS.md with gcc 7.5 (Ubuntu 18.04) and unstated flags; the FSE order-0 baseline is 416.3/564.4 MB/s, the 773.9 MB/s figure is the 4-way -o0 codec and the 32-way scalar is 642.4 (Graviton 4x16 452.6, NEON 736.2).
- 1.5.2 (Oct 2023) carried security fixes: fqzcomp and name-tokeniser write overruns, an 8-byte read overflow in the AVX2 rANS decoder, an SSE4 order-1 mis-decode. Issue #154 open (Sep 2026): CRAM 3.1 'small' encode fails with many 1 bp reads (fqzcomp suspected); #128 (closed): rans_compress_to_4x16 failed on blocks over 1.25 MiB. Compiler-sensitive: gcc-11 4x16 encode 268.2 vs gcc-7 431.5 MB/s; the default simulated gathers cost 10-30% decode on unpatched Intel.

## Caveats and trade-offs

Numbers are first-party from a 2021 pull-request description (merged April 2022); hardware named, flags not stated. The repo also carries BENCHMARKS.md, a maintained snapshot on the same Xeon Gold 6142 (10 MB NovaSeq quals: r4x16-o0 400.3/716.1 MB/s versus r32x16-o4 AVX512 866.9/2098.6 MB/s) that compares only internal codecs plus fqzcomp and bsc. The 32-way scalar and SSE4 encoders are slower than the 4-way codec; gains are mainly in decode and with AVX2/AVX512. LICENSE.md is BSD (3-clause style, Genome Research Ltd) with listed files (c_range_coder.h, rANS_byte.h, rANS_word.h, ...) public domain/CC0 (no patent grant for those).

32-way scalar code is slower than 4-way scalar; the win exists only with SIMD. Multiple formats (rANS 4x16 order 0/1, arithmetic coder, name and quality codecs). README notes the Intel GDS microcode mitigation slows AVX2 decode and AVX512 encode by 2-3x, so simulated gather is the default.

## Maintenance

Actively maintained by the samtools/htslib team (release 1.6.7 June 2026, last commit 2026-09-24); BSD-licensed with some rANS/range-coder headers public domain/CC0, so copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** PR #26 (jkbonfield, opened 2021-06-17, merged 2022-04-12) gives first-party encode/decode MB/s tables on a named CPU (Xeon Gold 6142) with an FSE order-0 row as an external baseline, but compiler flags are not stated (only 'Ubuntu 18.04 system gcc'), so not A; no independent measurement.
- **Verifier notes:** Record's 'decode 773.9 (4x16 scalar)' is the 4-way -o0 codec, not the 32-way scalar (642.4); Graviton 'NEON 437 to 736' conflated the 32x16 scalar row (437.3) with the 4x16 baseline (452.6), corrected. Last commit 2026-09-24 ('Make all inputs constant (#152)') and 40 stars confirmed.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/samtools/htscodecs/pull/26>
  - <https://github.com/samtools/htscodecs>
  - <https://github.com/samtools/htscodecs/commits>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/LICENSE.md>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/BENCHMARKS.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/README.md>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/LICENSE.md>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/NEWS.md>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/configure.ac>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/Makefile.am>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/htscodecs/rANS_static4x16pr.c>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/htscodecs/rANS_static4x16.h>
  - <https://raw.githubusercontent.com/samtools/htscodecs/master/htscodecs/rANS_static32x16pr_avx2.c>
  - <https://github.com/samtools/htscodecs/pull/26>
  - <https://github.com/samtools/htscodecs/issues?q=is%3Aissue>
  - <https://github.com/samtools/htscodecs/issues/128>
  - <https://github.com/samtools/htscodecs/issues/154>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/samtools/htscodecs`) · [data/wave9/enrich/raw/github_com_samtools_htscodecs.json](../../../data/wave9/enrich/raw/github_com_samtools_htscodecs.json) (enrichment confidence 0.8)

</details>
