# LZFSE (Apple reference implementation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Apple's LZ77 + finite-state-entropy codec in plain C99; zlib -6 ratio at about 3.4x the compress and 2.3x the decompress speed.

| | |
|---|---|
| **Beats** | zlib (zlib 1.3.2) |
| **Claimed result** | README: 'targets similar compression rates at higher compression and decompression speed compared to deflate using zlib' (no numbers in the README). lzbench 2.4 table: lzfse 91.1 MB/s compress, 732 MB/s decompress, ratio 31.91; zlib 1.3.2 -6 26.8 MB/s, 314 MB/s, ratio 32.19; zlib -9 11.3 MB/s, 318 MB/s, ratio 31.92. That is about 3.4x faster compression and 2.3x faster decompression than zlib -6 at nearly the same ratio (derived from page data). |
| **Workload** | Silesia tar, single-thread in-memory compression and decompression versus zlib at several levels, through lzbench. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04; silesia.tar (211,947,520 bytes) |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 1.8k stars; Apple's Compression framework algorithm; vcpkg port lzfse |
| **Last commit** | 2017-05-22 |
| **Links** | [repository](https://github.com/lzfse/lzfse) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

lzbench 2.4 (gcc 15.2.0 release binary, one thread of an AMD EPYC 9555P at 3.20 GHz, turbo off, silesia.tar) lists lzfse 2017-03-08 at 91.1 MB/s compress and 732 MB/s decompress at 31.91% versus zlib 1.3.2 -6 at 26.8 / 314 MB/s and 32.19%, about 3.4x and 2.3x faster at a slightly better ratio (derived from page data). Against zlib -9 (11.3 / 318 MB/s, 31.92%) the compression gap is about 8x.

## Use it when

- Reading or writing data that Apple's Compression framework, Apple archives or iOS/macOS tools produce or consume (COMPRESSION_LZFSE), from Linux or Windows.
- One-shot in-memory compression of whole buffers where you want zlib -6 to -9 ratio (31.91% vs 32.19% on Silesia) with faster encoding than zlib and no external dependencies.
- Embedding in a C or C++ project that wants a tiny, BSD-3 codec with caller-supplied scratch memory and no internal allocation.

## Skip it when

- New formats with no Apple interop requirement: zstd -2 (352 MB/s, 1257 MB/s, 32.70%) and zstd -3 beat it on both speeds at similar or better ratio in the same lzbench run, and libdeflate -6 decodes faster (820 vs 732 MB/s) with a slightly better ratio while staying deflate-compatible.
- Streaming, chunked or bounded-memory pipelines: only whole-buffer calls exist, the caller must know or guess the decompressed size, and there is no frame checksum.
- Single inputs above 2 GiB: issue #64 (open) shows int32_t history positions overflowing and ratio dropping from 3.01x to 2.24x on a 3 GiB file.
- Big-endian targets (issue #23, open since 2016, fails on ppc64be) or toolchains without GCC builtins/MSVC intrinsics (issue #37); unaligned loads also broke asm.js (issue #43).
- Untrusted input in a security-sensitive service without your own fuzzing: the repo has had no commits since 2017 and UBSan pointer-overflow reports in the decoder (issue #53) were only closed, with no visible fix release.

## How it is fast

The decoder uses table-driven tANS (Collet's Finite State Entropy) instead of Huffman: literals are decoded up front with four interleaved FSE states, then L/M/D (literal length, match length, distance) triplets drive a copy loop that uses deliberately oversized copies with a 32-byte safety margin on the fast path. The encoder uses a 2^14-entry hash history table, 4 candidate positions per line, and keeps a pending match it can replace (lazy matching), emitting immediately once a match exceeds 40 bytes. Inputs under 4096 bytes switch to the simpler LZVN coder.

## Compared with alternatives

Pick it over zstd, libdeflate or zlib-ng only when you need the LZFSE bitstream for Apple interoperability; on raw speed and ratio zstd -2/-3 and libdeflate -6 dominate it in the same lzbench table. Its sibling LZVN mode (69 / 799 MB/s, 38.13%) is not a reason to choose it over LZ4 or Snappy.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (libc only; malloc used only when scratch_buffer is NULL) |
| **Minimum toolchain** | C99 (Makefile and CMake set -std=c99); README tested gcc 5.2.1 and clang 3.6.2; MSVC supported via _BitScan shims |
| **Platforms** | little-endian x86-64, aarch64 and other little-endian targets; big-endian broken (issue #23) |
| **Thread safety** | Not documented; the API keeps no global state and takes a caller scratch buffer, so separate calls with separate scratch buffers should be independent (inferred from the API, not stated). |
| **Drop-in for the baseline** | partial — replaces zlib's compress()/uncompress() style one-shot use, but the bitstream is not deflate, there is no inflate/deflate streaming API, no levels and no checksum |

## Gotchas

- lzfse_encode_buffer returns 0 when the output does not fit, while lzfse_decode_buffer returns dst_size when the output is truncated; you cannot tell a truncated decode from an exact fit without a stored size.
- The shipped Makefile builds with -Os, so throughput from a plain `make` build may be below lzbench numbers built with the benchmark's own flags.
- The CLI crashes with a double free on empty input (issue #45, open).
- Encoder tunables (hash bits, hash width, good-match length, LZVN threshold) live in lzfse_tunables.h and are compile-time only.

## Known shortcomings

- Tier B on lzbench 2.4 (flags not on the results page).
- Abandoned since 2017-05 with open issues #64 (int32 positions drop the ratio from 3.01x to 2.24x on inputs over 2 GiB), #23 (big-endian broken), #45 (CLI double free on empty input) and #37/#43 (portability); no streaming API and no checksum; the Makefile builds -Os. In the same lzbench 2.4 table zstd -2 (352/1257 MB/s, 32.70%) and libdeflate -6 beat it.

## Caveats and trade-offs

lzbench bundles the 2017-03-08 version. The README itself has no numbers, so the evidence is only the lzbench table. zstd 1.5.7 -5 (126 MB/s, 1172 MB/s, ratio 29.60) beats it on every axis. Last commit 2017.

Reference C implementation with a command line tool; not tuned for SIMD. Other codecs (zstd -5, libdeflate) give similar or better ratio at higher speed.

## Maintenance

Abandoned since May 2017 with open crash, big-endian and &gt;2 GiB issues, but BSD-3-Clause, dependency-free C99 and small enough to vendor; the format itself stays maintained by Apple inside its Compression framework.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The well-known independent lzbench 2.4 suite (public code, inikep/lzbench; gcc 15.2.0 release binary, -eALL -t8,8 -o1c4; single thread of an AMD EPYC 9555P, turbo off, silesia.tar) lists lzfse 2017-03-08 at 91.1 MB/s compress, 732 MB/s decompress, 31.91% versus zlib 1.3.2 -6 at 26.8 / 314 MB/s, 32.19%. Per-codec compile flags are not on the results page, so B, as for the other lzbench-backed entries.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** All quoted rows (lzfse, zlib -6, libdeflate -6) match the lzbench README; the 3.4x / 2.3x ratios are correctly marked as derived. GitHub page: BSD-3-Clause, 1.8k stars, 194 forks, not archived; last commit 2017-05-22 (merge of PR #40), so abandoned is right.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/README.md>
  - <https://github.com/lzfse/lzfse>
  - <https://github.com/lzfse/lzfse/commits>
- **Sources the enricher read:**
  - <https://github.com/lzfse/lzfse>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/README.md>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/Makefile>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/src/lzfse.h>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/src/lzfse_tunables.h>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/src/lzfse_internal.h>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/src/lzfse_main.c>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/src/lzfse_decode_base.c>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/src/lzfse_encode_base.c>
  - <https://raw.githubusercontent.com/lzfse/lzfse/HEAD/src/lzfse_fse.h>
  - <https://github.com/lzfse/lzfse/issues?q=is%3Aissue>
  - <https://github.com/lzfse/lzfse/issues/64>
  - <https://github.com/lzfse/lzfse/issues/45>
  - <https://github.com/lzfse/lzfse/issues/23>
  - <https://github.com/lzfse/lzfse/issues/65>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/lzfse/lzfse`) · [data/wave9/enrich/raw/github_com_lzfse_lzfse.json](../../../data/wave9/enrich/raw/github_com_lzfse_lzfse.json) (enrichment confidence 0.85)

</details>
