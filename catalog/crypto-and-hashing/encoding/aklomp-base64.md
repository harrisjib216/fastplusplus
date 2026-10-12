# aklomp/base64 (SIMD Base64 C99 library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Portable C99 SIMD base64 codec with runtime CPU dispatch; the Muła–Lemire paper measured its decoder about 4x faster than Chrome's.

| | |
|---|---|
| **Beats** | base64 |
| **Claimed result** | Muła & Lemire (ACM TWEB 2018) Table VI, decode on real files: AVX2 (Klomp) 0.43 cycles/byte vs Google Chrome base64 1.8 and Linux kernel base64 20 on lena.jpg (\~4.2x vs Chrome, \~46x vs Linux, derived from page data). Also Turbo-Base64 README (1 MB buffer, i7-9700K, gcc 11.2): b64avx2 26,153 MB/s encode / 22,515 MB/s decode vs Google Chrome base64 2,541/4,289 MB/s (\~10x encode, \~5x decode, derived from page data) |
| **Workload** | Single-threaded base64 decode of real files (images, text, 1.4-330 KB) with error checking, from the Muła & Lemire paper; plus encode/decode of a 1 MB buffer from the Turbo-Base64 README shootout |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700 (Skylake) @ 3.4 GHz, Turbo Boost disabled (paper); Intel i7-9700K @ 3.6 GHz (Turbo-Base64 table) |
| **Compiler and flags** | GCC 5.3 -O3 -march=native (Muła & Lemire paper, lemire/fastbase64 Makefile adds -mavx2). The Turbo-Base64 table states only gcc 11.2, with no flags given for the competitor builds |
| **Adoption** | 1,022 stars |
| **Last commit** | 2026-07-12 |
| **Links** | [repository](https://github.com/aklomp/base64) · [benchmark](https://arxiv.org/pdf/1704.00605) |

## Verdict

Muła & Lemire (ACM TWEB 2018) timed single-threaded decoding with error checking on six real files (1.4–330 KB) on an i7-6700 with Turbo Boost off, GCC 5.3 -O3 -march=native. Klomp's AVX2 decoder took about 0.43 cycles/byte on lena.jpg against 1.8 for Chrome's codec and 20 for the Linux kernel's. That is the pre-August-2017 range-compare version, which the paper found about 2x slower than its own AVX2 codec. The current decoder adopted the paper authors' LUT method in commit 0a69845 (+64% AVX2 decode on an i7-4870HQ, per the commit message). Turbo-Base64's 2022.02 run (i7-9700K, gcc 11.2, 1 MB) puts b64avx2 at 26.2/22.5 GB/s encode/decode against 2.5/4.3 GB/s for Chrome's codec, but that harness is not public.

## Use it when

- A C or C++ program that encodes or decodes large, clean standard-alphabet base64 blobs (tens of KB to MB: images, attachments with the line breaks already stripped, binary payloads) and today uses a scalar codec like Chrome's modp_b64, the Linux kernel's, or a hand-rolled table loop.
- Binaries shipped to unknown x86 machines: one build carries SSSE3 through AVX-512 codecs and picks one at runtime. The CMake build turns all the x86 SIMD paths on by default.
- Code with a GPL-3.0 problem: this is BSD-2-Clause, while Turbo-Base64, which beats it in Turbo-Base64's own tables, is GPL-3.0.
- Chunked or streaming I/O (a socket or file read in blocks), where the stream_\* API keeps partial quads between calls without buffering the whole input.
- AArch64, including Apple M1 and Windows ARM64 (NEON64 support added in 2025). NEON is chosen at compile time, not detected at runtime.

## Skip it when

- Input containing whitespace or line breaks (MIME, PEM, 76-column output from GNU base64). Any character outside the alphabet makes decode fail. Whitespace skipping has been an open discussion since 2016 (#33), and the author said in reply to #33 that it is not currently planned.
- base64url or other alphabets. Only '+/' is supported (#66, open since 2020); the SIMD code relies on arithmetic tied to the standard alphabet, so you would have to translate '-_' yourself before and after.
- Many short strings (under about 100 bytes). In Turbo-Base64's 2022.02 run on an i7-9700K, b64avx2 manages 891/734 MB/s encode/decode on 4–16 byte strings against 2,330/2,161 MB/s for Turbo-Base64, and it stays about 2–4x behind up to 128 bytes. There is also no public way to skip the per-call dispatch (#65).
- Strict validation. Decode does not check for canonical encoding (non-zero trailing bits pass, #159) and has no way to require or forbid padding (#160). The OpenMP decoder accepts '=' at the end of an interior slice (#158).
- Peak throughput on AVX-512 or Apple Silicon. Decoding has no AVX-512 path (it reuses AVX2). On an M1, Turbo-Base64's table shows NEON64 at 19.1/12.5 GB/s against 24.0/15.4 GB/s for tb64v128.

## How it is fast

There are separate codecs for SSSE3, SSE4.1, SSE4.2, AVX, AVX2, AVX-512 (VL+VBMI, encode only), NEON32 and NEON64. On x86, the first init call picks one with CPUID/XGETBV and stores it in a global function-pointer pair. The AVX2 decoder turns 32 characters into 24 bytes per round. It uses Muła/aqrit's nibble-LUT method (the Aug 2017 rewrite): vpshufb lookups on the high and low nibbles validate the input (vptest sends any invalid byte to the scalar path), a third 'roll' vpshufb adds the per-range offset, and vpmaddubsw + vpmaddwd + vpshufb + vpermd pack the result, the same packing as Fig. 9 of Muła & Lemire. The AVX2 encoder uses hand-written inline asm on 64-bit GCC/Clang. The scalar fallback moves 32 or 64 bits per step through 12-bit encode and 32-bit decode tables, and an optional OpenMP build splits buffers of 20,000 bytes or more across threads.

## Compared with alternatives

Pick it over Turbo-Base64 when you need BSD-2-Clause rather than GPL-3.0 and mostly process long buffers, where the gap in Turbo's own 1 MB table is about 11% on encode and 32% on decode; Turbo wins clearly on short strings. Pick it over lemire/fastbase64 and base64simd, which are research code (fastbase64 is archived), when you want a maintained library with a streaming API, runtime dispatch and NEON. Pick simdutf's base64 instead when the input may contain whitespace or needs base64url.

## Integration

| | |
|---|---|
| **Form** | static lib (a single lib/libbase64.o from make) or static/shared library via CMake 3.10.2+; it can also be vendored as source |
| **Dependencies** | none (OpenMP optional) |
| **Minimum toolchain** | C99 compiler. The x86 AVX dispatch needs GCC 4.2+ or Clang 3+ for inline xgetbv; MSVC goes through __cpuidex. The README recommends Clang over GCC for NEON and warns of a GCC 4.6 miscompile of vst4q_u8. |
| **Platforms** | x86/x86-64 with runtime dispatch (SSSE3, SSE4.1, SSE4.2, AVX, AVX2, AVX-512 VL+VBMI encode); 32-bit ARM NEON and AArch64 NEON chosen at compile time (AArch64 NEON on by default in CMake, also on Windows ARM64); a portable 32/64-bit scalar path everywhere else, CI-tested on macOS arm64, Linux aarch64 and Windows ARM64 among others |
| **Thread safety** | The README claims 're-entrant and threadsafe'. Encode and decode keep all state in the caller's struct base64_state. The chosen codec is an unsynchronized static function-pointer pair that the first init writes and that any call with non-zero flags rewrites. ThreadSanitizer flags this as a race (#65); in practice it is benign because every thread writes the same value. |
| **Drop-in for the baseline** | partial — the job is the same (standard RFC 4648 base64 with padding) but the API is its own: caller-sized buffers, 1/0/-1 return codes, no whitespace handling. Code that decodes with coreutils `base64 -d` or with line-wrapped input needs changes. |

## Gotchas

- A plain `make` builds only the scalar codec. You have to set AVX2_CFLAGS=-mavx2, SSSE3_CFLAGS=-mssse3 and so on, or the SIMD paths compile to stubs. CMake, by contrast, turns all the x86 SIMD paths on by default.
- Passing any BASE64_FORCE_\* flag re-runs codec selection and overwrites the process-wide codec for every thread. A forced codec that was not compiled in makes decode return -1 rather than falling back.
- The SIMD loops store full 32-byte vectors while advancing the output by only 24 bytes (decode) and read 4 bytes before the current block (AVX2 encode). The library guards this internally, but output buffers should still get the margin the header asks for rather than exactly 3/4 or 4/3 of the input.
- The installed bin/base64 conflicts with coreutils' /usr/bin/base64 when packaged (#154). Under CMake, the test suite runs every compiled-in codec and aborts with SIGILL on CPUs that lack an ISA it was built for (#152).

## Known shortcomings

- Tier A rests on the 2017 Muła & Lemire paper run (lemire/fastbase64 harness, GCC 5.3, i7-6700): AVX2 decode 0.43 cycles/byte vs Chrome 1.8 (\~4.2x) and Linux 20. The Turbo-Base64 comparison page it cited is third-party with a closed harness.
- The paper's comparison used the pre-Aug-2017 range-compare decoder; commit 0a69845 later adopted the Muła/aqrit nibble-LUT decoder (+64% AVX2), so the paper's gap is stale. No whitespace skipping (#33), no base64url (#66), no canonical/padding check (#159/#160); OpenMP decoder accepts interior '=' (#158). Short strings 2-4x behind Turbo-Base64 (Turbo's table only). No AVX-512 decoder. Plain `make` builds only the scalar codec unless \*_CFLAGS are set.

## Caveats and trade-offs

The paper benchmarks a 2017 copy of aklomp's AVX2 decoder vendored into lemire/fastbase64 ('based on Alfred Klomp's code with minor modifications'), decode only. The paper's own AVX2 codec is about 2x faster than Klomp's. The Turbo-Base64 numbers come from a competitor's 2022.02 run against aklomp v2022.02, and its comparison harness is not public. The latest commit (2026-07) only touches CI; the last code change was 2025-05.

C99 API; OpenMP option for extra parallel speedup; no NEON tuning as aggressive as competitors

## Maintenance

Maintained, slowly: the last release is v0.5.2 (Jan 2024), the last code change was NEON on Windows ARM64 (May 2025), and there have been only CI updates since. 37 issues are open, including recent validation-strictness reports. BSD-2-Clause, C99 and dependency-free, so it is easy to vendor; pybase64 wraps it, and ClickHouse integrated it (#65).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The cited Turbo-Base64 table is only tier C: its third-party harness (xtb64.mak, xb64test.h, xtb64test_.c) is not in the public repo, and it gives no flags beyond 'gcc 11.2'. Stronger evidence exists and keeps tier A: Muła & Lemire, 'Faster Base64 Encoding and Decoding Using AVX2 Instructions' (ACM TWEB 2018, arXiv 1704.00605), Table VI benchmarks aklomp's AVX2 decoder against Chrome and Linux base64 on an i7-6700 with GCC 5.3 -O3 -march=native. Its public artifact is lemire/fastbase64: benchmarks/basic_benchmark.c, src/klompavxbase64.c and a Makefile with -O3 -march=native -mavx2.
- **Verifier notes:** Tier A holds, but through the peer-reviewed paper and its artifact repo, not through the cited Turbo-Base64 page, which alone would be tier C. benchmark_url was switched to the paper. Metadata checks out: BSD-2-Clause, 1,022 stars, not archived or a fork.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `last_commit`, `caveats`
- **Shortcomings recorded by:** Muła & Lemire, ACM TWEB 2018: AVX2 decode 0.43 cyc/B vs Chrome 1.8, Linux 20 (i7-6700, GCC 5.3 -O3 -march=native).
- **Pages the verifier opened:**
  - <https://github.com/powturbo/Turbo-Base64#readme>
  - <https://github.com/powturbo/Turbo-Base64>
  - <https://github.com/aklomp/base64>
  - <https://arxiv.org/pdf/1704.00605>
  - <https://github.com/lemire/fastbase64>
- **Sources the enricher read:**
  - <https://github.com/aklomp/base64>
  - <https://github.com/aklomp/base64/blob/master/README.md>
  - <https://github.com/aklomp/base64/blob/master/include/libbase64.h>
  - <https://github.com/aklomp/base64/blob/master/lib/codec_choose.c>
  - <https://github.com/aklomp/base64/blob/master/lib/lib.c>
  - <https://github.com/aklomp/base64/blob/master/lib/lib_openmp.c>
  - <https://github.com/aklomp/base64/blob/master/lib/arch/avx2/codec.c>
  - <https://github.com/aklomp/base64/blob/master/lib/arch/avx2/dec_loop.c>
  - <https://github.com/aklomp/base64/blob/master/lib/arch/avx2/dec_reshuffle.c>
  - <https://github.com/aklomp/base64/blob/master/lib/arch/avx2/enc_loop.c>
  - <https://github.com/aklomp/base64/blob/master/lib/arch/avx512/codec.c>
  - <https://github.com/aklomp/base64/blob/master/lib/arch/generic/dec_tail.c>
  - <https://github.com/aklomp/base64/blob/master/CMakeLists.txt>
  - <https://github.com/aklomp/base64/blob/master/Makefile>
  - <https://github.com/aklomp/base64/commits/master>
  - <https://github.com/aklomp/base64/releases>
  - <https://github.com/aklomp/base64/commit/0a698455df8cd90c066382a375c7886d6158069d>
  - <https://github.com/aklomp/base64/issues>
  - <https://github.com/aklomp/base64/issues/33>
  - <https://github.com/aklomp/base64/issues/65>
  - <https://github.com/aklomp/base64/issues/66>
  - <https://github.com/aklomp/base64/issues/69>
  - <https://github.com/aklomp/base64/issues/152>
  - <https://github.com/aklomp/base64/issues/155>
  - <https://github.com/aklomp/base64/issues/158>
  - <https://github.com/aklomp/base64/issues/159>
  - <https://arxiv.org/pdf/1704.00605>
  - <https://github.com/lemire/fastbase64>
  - <https://github.com/lemire/fastbase64/blob/master/src/klompavxbase64.c>
  - <https://github.com/powturbo/Turbo-Base64#readme>
  - <https://github.com/powturbo/Turbo-Base64>
  - <https://github.com/WojciechMula/base64simd>
  - <https://github.com/mayeut/pybase64#readme>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/aklomp/base64`) · [data/wave7/enrich/raw/github_com_aklomp_base64.json](../../../data/wave7/enrich/raw/github_com_aklomp_base64.json) (enrichment confidence 0.8)

</details>
