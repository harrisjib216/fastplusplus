# TurboRLE (TRLE and SRLE)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `GPL-2.0-or-later` · 🟢 active

> Block run-length encoder (TRLE, plus escape-based SRLE for 8/16/32/64-bit runs) that out-compresses and out-runs rle8 and Mespotine RLE.

| | |
|---|---|
| **Beats** | rle8 (rainerzufalldererste/rle8 as of 2019, an SSE/AVX2 8-bit run length encoder, one configuration 'rle8 1'; that repository has since become hypersonic-rle-kit) and Mespotine RLE (MRLE); memcpy shown as a reference row. None of the general-lossless category baselines (zlib, zstd, lz4, brotli, xz) appear in the README tables. |
| **Claimed result** | README claim: 'Compress better and up to 12 times faster and decompress up to 6 times faster than other fast RLEs'; 'Can be faster than memcpy!'. Skylake table (MB/s, C = compress, D = decompress): girl.bmp trle C 2089 / D 11385, srle 8 C 11307 / D 13205 (4744806 bytes) vs rle8 C 890 / D 11998 (5901235 bytes) and mrle C 378 / D 12302; enwik9bwt trle C 472 / D 1743, srle 8 C 568 / D 4310 vs rle8 C 260 / D 675 and mrle C 207 / D 553; 1034.db trle C 774 / D 3020 vs rle8 C 456 / D 2669 and mrle C 262 / D 1491. Derived from page data: srle 8 compresses girl.bmp about 12.7x faster than rle8 and decompresses enwik9bwt about 6.4x faster than rle8; trle compresses girl.bmp about 2.3x faster than rle8 while decompressing slightly slower (11385 vs 11998 MB/s). srle 64 compresses girl.bmp at 16269 MB/s vs memcpy 13978 MB/s (output is larger, 19839711 bytes). |
| **Workload** | Single-thread run length encode and decode throughput (MB/s) and compressed size on three large files: girl.bmp (RLE64Samples), a checkers end-game tablebase file (1034.db), and enwik9 after a Burrows-Wheeler transform (enwik9bwt), measured with TurboBench. |
| **Metric** | throughput |
| **Hardware** | Intel Skylake i7-6700 3.4GHz (x86 tables for girl.bmp, 1034.db and enwik9bwt); ARM A73 ODROID-N2 1.8GHz (second set of tables covering only girl.bmp and enwik9bwt, with no rle8 row since rle8 is x86 SSE/AVX2 only) |
| **Compiler and flags** | gcc 8.3 (tables dated 2019-08); flags not stated in the README. The current TurboBench makefile builds the TurboRLE objects with -O3 -march=haswell -w -fstrict-aliasing -falign-loops=32 -DNDEBUG on x86_64, but that is the HEAD makefile, not the 2019 revision. The in-repo ./trle test tool (trle.c) benchmarks trle, srle and mrle but not rle8, so the rle8 rows can only come from TurboBench. |
| **Adoption** | 290 stars, 30 forks |
| **Last commit** | 2026-07-14 |
| **Links** | [repository](https://github.com/powturbo/Turbo-Run-Length-Encoding) · [benchmark](https://github.com/powturbo/Turbo-Run-Length-Encoding) |

## Verdict

First-party TurboBench runs (single thread, Intel i7-6700 Skylake 3.4 GHz, gcc 8.3, August 2019, flags not stated) against rle8 (2019, SSE/AVX2) and Mespotine RLE: srle 8 compresses girl.bmp at 11307 MB/s vs rle8 890 MB/s (about 12.7x, smaller output 1.2% vs 1.5%) and decodes enwik9bwt at 4310 vs 675 MB/s (about 6.4x), while trle gives the best ratio on all three files but decodes girl.bmp slightly slower than rle8 (11385 vs 11998 MB/s); no zlib, zstd or LZ4 rows exist. The in-repo trle tool verifies each round trip against a complemented copy, so decode correctness is checked, but it does not include rle8.

## Use it when

- A fast byte-preserving pre-pass before an entropy coder on run-heavy data such as BWT output: the README shows trle + TurboANX 12 at 19.2% of enwik9bwt, compressing at 1527 MB/s and decoding at 3834 MB/s on a 2019 Skylake.
- Images, masks, bitmaps and tablebase-like files dominated by long runs: trle cut girl.bmp to 0.6% while decoding at 11385 MB/s, and 1034.db to 17.4% (best ratio among the RLEs tested).
- Runs of 16/32/64-bit values (sparse integer or float arrays) where speed matters more than ratio: srle 64 decodes 1034.db at 10120 MB/s at 39.5% size on the same Skylake.
- C or C++ projects that are GPL-compatible and can vendor two .c files plus the bundled include_ headers; Java callers via the JNI wrapper.

## Skip it when

- Decoding untrusted input: the decoders never check the compressed length and never bound run lengths against outlen; issue #12 (open since 2025-09-21, no maintainer reply) shows a heap overflow in srled8 from a crafted stream, and _trled has the same unchecked rmemset pattern.
- Permissive or proprietary code: the licence is GPL-2.0-or-later; a 2020 request for a permissive licence (issue #8, Wes McKinney) was closed with no licence change, and the README offers no commercial licence.
- Data without long runs (text, binaries, general archives): every README benchmark is a run-heavy file, and LZ-family siblings such as LZ4 or zstd target repeated substrings that RLE cannot exploit.
- When the fastest RLE decoder is the goal: the 2019 tables predate the rle8 successor hypersonic-rle-kit (BSD-2-Clause), whose own 2023 run on a Ryzen 9 7950X with TurboRLE 7f6e486 and AVX2 shows its 8-bit codecs decoding faster at similar ratios (enwik9.bwt '8 Bit 3LUT Short' 40.34% and 3,046.5 MiB/s vs trle 42.0% and 2,062.9 MiB/s); that is a competitor-run comparison.
- Inputs of 4 GiB or more in one call or streaming use: lengths are 32-bit unsigned and the API is single-block only.

## How it is fast

TRLE first builds a byte histogram (the 4-way unrolled TurboHist counter) and, when some byte values are unused, uses those unused values as run codes, so literals pass through unescaped and short run lengths fit in the code byte itself; runs of the most frequent byte are folded into the length with a flag bit, and lengths beyond the code range use a variable-byte integer. When every byte value occurs it falls back to escape-based SRLE with the least frequent byte as escape. The encoder finds run boundaries by XOR-ing a 64-bit word with the word one byte later and taking ctz, and the SRLE decoder copies 16 or 32 literal bytes at a time with SSE2/AVX2 compare-and-movemask to find the next escape, filling runs with vector stores.

## Compared with alternatives

The catalogued siblings (LZ4, zstd, Blosc/c-blosc2, Density) are LZ or shuffle codecs; pick TurboRLE only when the data is dominated by long runs of bytes or fixed-width elements and you want a cheap, byte-preserving step before an entropy coder, and stay with LZ4 or zstd for general data, for a self-describing frame, or for input you do not control.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (bundled include_/conf.h; the trle test tool also uses include_/time_.h and ext/mrle.c) |
| **Minimum toolchain** | C99 (makefile uses -std=gnu99); README lists GCC 4.6+, Clang 3.2+, Visual C++ 2008+ (makefile.vs), aarch64 GCC 6.3+, ppc64le GCC 8+ |
| **Platforms** | x86-64 and x86 (SSE2 path by default, AVX2 path when compiled with AVX2 enabled), aarch64 NEON through an SSE translation header, ppc64le, loongarch64, riscv64 scalar fallback; Linux, Windows (MinGW, MSVC), macOS |
| **Thread safety** | not documented; trlec.c and trled.c keep all state (histograms, rmap) on the stack with no globals, so concurrent calls on separate buffers appear safe |
| **Drop-in for the baseline** | no |

## Gotchas

- No input validation in any decoder (trled, srled, srledN): truncated or crafted data reads past the input and writes past outlen; issue #12 (heap-buffer-overflow in srled8, reproducer writes 101 bytes into a 16-byte buffer) is still open, and the HEAD trled.c run paths have no bounds checks.
- Output buffers need undocumented slack: trlec memsets 32 bytes of bitmap header even for 2-byte inputs, srlecN with a fixed escape writes the whole escaped stream (up to about 2x the input for srle 8 when isolated escape bytes alternate with other bytes) before deciding to fall back to memcpy, and the AVX2/SSE run fill can store up to 31 bytes past a run's end. The bundled test tool allocates inlen\*4/3+1024 for compressed output and inlen+1024 for decoded output; the header gives no bound.
- The compressed length is part of the format: trled treats inlen == outlen as a stored block (memcpy) and inlen == 1 as a memset, so the exact length returned by the encoder must be stored and passed back. The srle 8/16/32/64 benchmark rows use a hard-coded escape (0xda repeated), and data rich in that value compresses worse or expands transiently.
- Build: the GNU makefile defines -mavx -mpopcnt and -march=haswell for x86_64 but never adds them to CFLAGS, so the README's 'make AVX2=1' builds the SSE2 paths only; pass MARCH=-march=haswell (or -mavx2) to get the AVX2 decoder (makefile.vs does honour AVX2=1).

## Known shortcomings

- Compares only against other RLE libraries (rle8, mrle), never zlib, zstd or lz4; the 'up to 12x/6x' picks the best variant per file; the 2019 rle8 baseline is stale and its successor hypersonic-rle-kit benchmarked TurboRLE 7f6e486 (April 2023) and beats trle on enwik9.bwt in ratio and speed; flags not in the README. Repo renamed powturbo/Turbo-Run-Length-Encoding. Filed under compression-and-encoding/general-lossless.
- Numbers hold (trle round-trip check is sound, no rle8 rows), but the decoders never bounds-check input or outlen: issue #12 (srled8 heap overflow, open since 2025-09-21, no maintainer reply), _trled has the same unchecked rmemset. Encoders need undocumented output slack (srlecN writes up to about 2x before its memcpy fallback, 32-byte bitmap memset, SIMD fill overshoots up to 31 bytes). The GNU makefile never applies its -march=haswell flags, so 'make AVX2=1' builds SSE2 only. GPL-2.0-or-later; issue #8 asking for a permissive licence (2020) closed with no change.

## Caveats and trade-offs

Tier C: first-party tables dated 2019-08 with compiler and CPU stated but no flags in the README; TurboBench is public but its 2019 build flags are not documented, and TurboRLE's own code has changed since (decoder commits as recent as 2026-07). The baselines are other RLE libraries, not the general-lossless category incumbents (zlib, zstd, lz4, brotli, xz). The 'up to 12x / 6x' claims cherry-pick the best variant per file (srle 8 vs rle8 on girl.bmp compression; srle 8 vs rle8 on enwik9bwt decompression); trle decompresses girl.bmp slower than rle8 and mrle (11385 vs 11998 and 12302 MB/s). The rle8 baseline is stale: its successor, hypersonic-rle-kit (same repository, BSD-2-Clause), benchmarks TurboRLE commit 7f6e486 (April 2023, AVX2 enabled) on an AMD Ryzen 9 7950X with Visual Studio 2022, and its own 8-bit codecs decode several times faster than trle and srle 8 at similar ratios (enwik9.bwt: '8 Bit 3LUT Short' 40.34% ratio, 765.3 MiB/s encode, 3,046.5 MiB/s decode vs trle 42.0%, 697.6 and 2,062.9 MiB/s; '8 Bit' decodes at 16,097.6 MiB/s vs srle 8 6,095.1 MiB/s); trle keeps the best plain-RLE ratio on 1034.db (17.4% vs 18.55%). That contradicts the README's 'No other RLE compress or decompress faster with better compression'. The memcpy row and the 'faster than memcpy' claim apply only to srle 64 compression of highly compressible data (girl.bmp: 16269 vs 13978 MB/s, output 4.9% of input). GPL-2.0-or-later (copyleft).

GPL-2.0-or-later (copyleft; a commercial licence is not described in the README). Pure C with no inline assembly, SIMD paths for SSE/AVX2/NEON plus a RISC-V scalar fallback, and Java JNI bindings. Several variants (srle 8/16/32/64) trade compression ratio for speed, so the fastest rows compress much worse than rle8 or mrle: the 12x and 6x figures pair different output sizes.

## Maintenance

Actively maintained (decoder and platform commits through 2026-07-14, a RISC-V scalar fallback PR merged June 2026) and small enough to vendor, but GPL-2.0-or-later and with an open, unanswered heap-overflow report (#12) in the decoder, so it suits trusted in-process data in GPL-compatible code only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Every number in the record matches the README tables (girl.bmp, 1034.db, enwik9bwt on i7-6700, gcc 8.3, 2019-08), which are first-party TurboBench runs; the benchmark harness (powturbo/TurboBench) is public but the README states no flags and the 2019 build flags are unknown (only the HEAD TurboBench makefile shows -O3 -march=haswell for TurboRLE), so it falls short of A and stays C.
- **Verifier notes:** Numbers verified exactly against the README; tier C stands. Main shortcomings: off-baseline (RLE libraries only, no zlib/zstd/lz4 rows), cherry-picked 'up to' ratios, and a stale 2019 rle8 baseline that its own successor hypersonic-rle-kit now beats in third-party (competitor-run) 2023 tables. The repository now lives at github.com/powturbo/Turbo-Run-Length-Encoding (TurboRLE redirects there); hypersonic-rle-kit (rainerzufalldererste/rle8) is not in the catalog and is a lead.
- **Fields the verifier corrected:** `baseline`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/powturbo/TurboRLE/HEAD/README.md>
  - <https://github.com/powturbo/TurboRLE>
  - <https://github.com/powturbo/Turbo-Run-Length-Encoding/commits/master>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/makefile>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/trle.c>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/trlec.c>
  - <https://raw.githubusercontent.com/powturbo/TurboBench/HEAD/makefile>
  - <https://raw.githubusercontent.com/rainerzufalldererste/rle8/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/powturbo/Turbo-Run-Length-Encoding>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/README.md>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/include/trle.h>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/include_/trle.h>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/include_/conf.h>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/include_/time_.h>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/trle_.h>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/trle.c>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/trlec.c>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/trled.c>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/makefile>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/makefile.vs>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/.github/workflows/build.yaml>
  - <https://raw.githubusercontent.com/powturbo/Turbo-Run-Length-Encoding/HEAD/LICENSE>
  - <https://github.com/powturbo/Turbo-Run-Length-Encoding/issues?q=is%3Aissue>
  - <https://github.com/powturbo/Turbo-Run-Length-Encoding/issues/12>
  - <https://github.com/powturbo/Turbo-Run-Length-Encoding/issues/8>
  - <https://github.com/powturbo/Turbo-Run-Length-Encoding/commits/master>
  - <https://raw.githubusercontent.com/rainerzufalldererste/hypersonic-rle-kit/HEAD/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/powturbo/turborle`) · [data/wave1/enrich/raw/github_com_powturbo_turborle.json](../../../data/wave1/enrich/raw/github_com_powturbo_turborle.json) (enrichment confidence 0.78)

</details>
