# FastLZ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟡 stale

> Two-file ANSI C byte-aligned LZ77 block compressor; about 3x zlib -1 compression speed and 2x decompression, at a worse ratio.

| | |
|---|---|
| **Beats** | zlib 1.3.2 (-1, -6, -9) in lzbench 2.4; zlib -1/-9 (version unstated) in the FastLZ README |
| **Claimed result** | lzbench 2.4 on silesia.tar, single thread AMD EPYC 9555P: fastlz 0.5.0 -1 273 MB/s compress, 587 MB/s decompress, ratio 49.37%; fastlz -2 294 / 561 MB/s, 47.61%; zlib 1.3.2 -1 89.0 / 297 MB/s, 36.45%; zlib -6 26.8 / 314 MB/s, 32.19%; zlib -9 11.3 / 318 MB/s, 31.92% (about 3.1x faster compression and 2.0x faster decompression than zlib -1, derived from page data). FastLZ README (enwik8, no methodology): FastLZ ratio 54.2%, 159 MB/s compress, 305 MB/s decompress; zlib -1 42.3%, 50 / 184 MB/s; zlib -9 36.5%, 11 / 185 MB/s. Ratio is compressed size as percent of input, so FastLZ output is larger. |
| **Workload** | Compress and decompress enwik8 (100 MB text), compared with zlib levels 1 and 9 (via lzbench per the README). |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04 (lzbench README); FastLZ README numbers have no hardware stated |
| **Compiler and flags** | lzbench 2.4 release binary built with gcc 15.2.0; lzbench Makefile builds codecs with -O3 -DNDEBUG -fomit-frame-pointer -fstrict-aliasing; run options -eALL -t8,8 -o1c4 |
| **Adoption** | 544 stars, 105 forks; included in lzbench; used in Godot, HHVM, Apache Traffic Server, Calligra, OSv, Netty, Death Stranding and as a basis for Blosc per README |
| **Last commit** | 2024-08-02 |
| **Links** | [repository](https://github.com/ariya/FastLZ) · [benchmark](https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md) |

## Verdict

lzbench 2.4 (gcc 15.2.0, -O3, one thread of an AMD EPYC 9555P at 3.20 GHz, turbo off, silesia.tar): fastlz 0.5.0 -1 compresses at 273 MB/s and decompresses at 587 MB/s with output 49.37% of input, versus zlib 1.3.2 -1 at 89.0 / 297 MB/s and 36.45% (about 3.1x and 2.0x, derived from page data). The FastLZ README's own enwik8 table (159 / 305 MB/s vs zlib -1 50 / 184 MB/s) gives no hardware or compiler.

## Use it when

- You need something several times faster than zlib on compressible blocks (text, logs, raw pixel rows, game assets) and can accept roughly 50% output size versus 36% for zlib -1 on Silesia.
- You want a tiny, vendorable codec: two files, ANSI C/C90, MIT, compiles with GCC, Clang, MSVC and TinyCC, including DOS and big-endian targets.
- You must read data already written in FastLZ format by existing users such as Godot, HHVM or Apache Traffic Server.
- Embedded or exotic toolchains where LZ4 or Snappy are harder to build: CI covers PowerPC, ppc64, s390x, armhf, arm64, MIPS and RISC-V.

## Skip it when

- New designs that only want speed: in the same lzbench 2.4 run LZ4 1.10.0 compresses about 2x faster (550 vs 273 MB/s) and decompresses about 6.5x faster (3832 vs 587 MB/s) at a slightly better ratio (47.60% vs 49.37%).
- When ratio matters: zstd -1 or zlib-ng -1 give much smaller output at comparable or better speed.
- Streams or very large buffers: the API is block-only with int lengths (under 2 GiB per call) and level 1 sees only an 8 KB window (level 2 about 72 KB), so long-range redundancy is lost.
- Already compressed inputs (images, video, archives): the README says it is not intended for them and output can grow past the input size.
- Projects that want an actively developed codec: last release 0.5.0 is from 2020-02-02 and the format's level 2 is still marked 'To be written' in the README.

## How it is fast

It is a greedy single-probe LZ77: a 13-bit multiplicative hash (Knuth constant 2654435769) of the next 3 bytes indexes an 8192-entry table of last positions, and a match is taken whenever the 3 bytes agree, with no chain search or lazy matching. Output is byte-aligned opcodes (literal runs up to 32 bytes, short and long matches with 13-bit offsets) with no entropy coding, so decoding is a branch on the top 3 bits plus memcpy/memmove. On x86-64 and aarch64 it reads 32-bit words directly to compare the first 4 bytes of a match.

## Compared with alternatives

Pick FastLZ over LZ4 or Snappy only for compatibility with existing FastLZ data or for a C90/TinyCC-portable two-file drop; LZ4 beats it on every axis in lzbench 2.4, and libslz is a similar-speed choice when gzip/deflate output compatibility is needed.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc string.h only; FASTLZ_USE_MEMMOVE=0 removes even that) |
| **Minimum toolchain** | ANSI C/C90 compiler; CI uses GCC, Clang, TinyCC and VS 2019 |
| **Platforms** | any; 32/64-bit, little and big endian; tested on amd64, i686, i586 DOS, PowerPC, ppc64(le), s390x, armhf, arm64, MIPS(64)(el), RISC-V |
| **Thread safety** | Not documented; the functions keep their hash table on the stack and use no globals, so concurrent calls on separate buffers look safe from the source. |
| **Drop-in for the baseline** | no |

## Gotchas

- Compression contract is easy to violate: input must be at least 16 bytes and the output buffer at least 5% larger than the input and no smaller than 66 bytes; there is no compressBound helper and no bounds checking in the compressor.
- Decompression returns 0 on corrupt input or a too-small maxout; it was hardened against corrupted input only in 0.5.0 (2020). The README's 40-line reference decoder has no bounds checks and is explicitly unsafe.
- The compressor puts a 32 KB hash table (8192 x uint32) on the stack per call, which matters on small embedded stacks.
- On x86-64 and aarch64 flz_readu32 dereferences an unaligned uint32_t pointer, which is undefined behavior in C even though it works on those CPUs.

## Known shortcomings

- Upgraded C to A via the lzbench 2.4 README (gcc 15.2.0 -O3, EPYC 9555P): fastlz 0.5.0 -1 273/587 MB/s vs zlib 1.3.2 -1 89/297 MB/s; LZ4 and Snappy beat it.
- In lzbench 2.4 LZ4 1.10.0 beats it on every axis (550/3832 vs 273/587 MB/s at 47.60% vs 49.37%). The compressor has no bounds checks (needs input of at least 16 bytes and an output buffer at least 5% larger and at least 66 bytes); the unaligned uint32 dereference on x86-64/aarch64 is undefined behaviour; the decoder was hardened only in 0.5.0 (2020); no release since 2020-02-02.
- Tier A rests on the lzbench 2.4 table (independent suite, public Makefile flags, gcc 15.2.0, EPYC 9555P); the README's own table has no methodology. Retier-02 raised the other lzbench 2.4 entries in this wave to A on the same basis.

## Caveats and trade-offs

FastLZ README table has no CPU, compiler, flags or lzbench version and appears to come from an old run; the lzbench 2.4 numbers are the reproducible ones. In the same lzbench table LZ4 1.10.0 (550 / 3832 MB/s at 47.60%), Snappy 1.3.1 and LZF 3.6 match or beat FastLZ, and zlib-ng 2.3.3 -1 (196 / 466 MB/s at 44.41%) narrows the gap to zlib-class codecs, so FastLZ is faster than stock zlib but not state of the art. Last release 0.5.0 dates from 2020; last commit 2024-08-02 (CI and warning fixes).

Byte-aligned LZ77 with worse ratio than zlib (54.2% vs 42.3% at level 1). ANSI C/C90, small and portable; bindings for Rust, Python, JS, Ruby, Lua.

## Maintenance

Stale: last release 0.5.0 in February 2020 and last commits in 2024 are CI and warning fixes, but it is MIT-licensed, two files and widely deployed, so vendoring it is low-risk.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the FastLZ README table has no methodology, but it points to lzbench, an independent third-party suite whose README (lzbench 2.4, public code, gcc 15.2.0, Makefile -O3 -DNDEBUG -fomit-frame-pointer -fstrict-aliasing, AMD EPYC 9555P single thread, silesia.tar) lists fastlz 0.5.0 against zlib 1.3.2 at -1/-6/-9.
- **Verifier notes:** Real, widely used entry; tier raised C to A via lzbench's independent, fully specified run (fastlz 0.5.0 row checked as this project's row). License MIT confirmed (LICENSE.MIT); last commit 2024-08-02 so 'stale' is correct.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** independent: lzbench 2.4 README; enricher; lzbench 2.4
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ariya/FastLZ/HEAD/README.md>
  - <https://raw.githubusercontent.com/ariya/FastLZ/HEAD/LICENSE.MIT>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
  - <https://github.com/ariya/FastLZ>
  - <https://github.com/ariya/FastLZ/commits>
- **Sources the enricher read:**
  - <https://github.com/ariya/FastLZ>
  - <https://raw.githubusercontent.com/ariya/FastLZ/HEAD/README.md>
  - <https://raw.githubusercontent.com/ariya/FastLZ/HEAD/fastlz.h>
  - <https://raw.githubusercontent.com/ariya/FastLZ/HEAD/fastlz.c>
  - <https://raw.githubusercontent.com/ariya/FastLZ/HEAD/ChangeLog>
  - <https://github.com/ariya/FastLZ/issues>
  - <https://github.com/ariya/FastLZ/issues?q=is%3Aissue+state%3Aclosed>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/ariya/fastlz`) · [data/wave9/enrich/raw/github_com_ariya_fastlz.json](../../../data/wave9/enrich/raw/github_com_ariya_fastlz.json) (enrichment confidence 0.85)

</details>
