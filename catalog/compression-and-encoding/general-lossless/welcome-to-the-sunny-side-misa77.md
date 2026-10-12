# misa77

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> LZ77 codec built for decode speed: about 2x LZ4's decompression throughput on Silesia at a better ratio, with slow compression.

| | |
|---|---|
| **Beats** | LZ4 (lz4 1.10.0 and lz4hc) |
| **Claimed result** | README (Intel i7-14650HX, turbo off): level 1 decompress 5376 MB/s at 42.64% vs LZ4 1.10.0 2514 MB/s at 47.59% (2.1x, derived from page data); vs zstd 1.5.7 -1 903 MB/s at 34.54%. lzbench 2.4 (EPYC 9555P): misa77 0.6.0 -1 decompress 7813 MB/s at 42.65% vs lz4 1.10.0 3832 MB/s at 47.60% (2.0x, derived from page data); compress 73.8 MB/s vs lz4 550 MB/s. |
| **Workload** | Decompression throughput versus compression ratio on silesia.tar, single thread, trusted-input (unsafe) decoder, compared with lz4, lz4hc, zstd, lzav, snappy, zxc and LZSSE. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04; silesia.tar (211,947,520 bytes). The project's own README table (Intel Core i7-14650HX, Apple M3) gives 5376 MB/s versus lz4 2514 MB/s. |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 172 stars; merged into lzbench and TurboBench |
| **Last commit** | 2026-08-10 |
| **Links** | [repository](https://github.com/welcome-to-the-sunny-side/misa77) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

In lzbench 2.4 run by the suite maintainer (gcc 15.2.0 release binary, one thread of an AMD EPYC 9555P, turbo off, silesia.tar), misa77 0.6.0 level 1 decompressed at 7813 MB/s with a 42.65% ratio vs lz4 1.10.0 at 3832 MB/s and 47.60% (2.0x, derived from page data), while compressing at 73.8 vs 550 MB/s. The author's own lzbench runs show the same shape on an i7-14650HX (5376 vs 2514 MB/s) and an Apple M3 (12638 vs 5195 MB/s).

## Use it when

- Assets, game data, model files, read-only database pages or package contents that are compressed once and decompressed many times on the hot path.
- Single-threaded decode-bound pipelines where LZ4 is the current choice and a 1.5-2x faster decode with a smaller output (42.6% vs 47.6% of original on silesia.tar at level 1) is worth a slower build step.
- x86-64 (AVX2 or SSE2) and AArch64/Apple Silicon servers or clients built with GCC or Clang and C++20.
- Data that is compressible: per the README, level 1 decodes faster than lz4 on all 12 Silesia files.

## Skip it when

- Compression-heavy or write-once-read-once workloads: level 1 compresses at 54-74 MB/s vs lz4's 371-550 MB/s in the same runs (about 7x slower), and levels 3-4 drop to 7-11 MB/s on the Intel run.
- Long-term storage or interchange: the format is v0.x and the README says it may change unexpectedly; there is no frame format, checksum, or streaming API.
- Untrusted input at level 4: the heavy format has no safe decoder yet (safe mode returns 0), and the default decoder is the unsafe one, where malformed input is undefined behavior.
- When ratio matters more than decode speed: zstd -1 reaches 34.5% on silesia.tar vs misa77 level 1 at 42.6%; level 4 (35.5%) needs a 176 MB encoder state.
- Big-endian or 32-bit targets, MSVC builds (the dispatcher uses __builtin_cpu_supports and GCC/Clang flags), or projects stuck below C++20.

## How it is fast

The format is shaped around a nearly branch-free decode loop: in the light format (levels -1 to 3) match lengths are capped at 32 bytes and match distances must be at least 33 bytes, so every match is one unconditional 32-byte vector copy that can never overlap its source; up to 16 literals are copied unconditionally, and a mandatory raw-literal suffix of at least 32 bytes serves as padding for those over-reads and over-writes. Control tokens (3 bytes: token plus 16-bit offset) grow forward from the start while literals grow backward from the end, so the decoder walks two streams with no interleaving. The compressors then spend effort choosing parses that suit this decoder (lookahead matching up to optimal parsing, with a suffix-array (SA-IS) based optimal parser for the level-4 heavy format, which uses 20-bit offsets and a length lookup table). AVX2 or SSE2 is chosen at runtime on x86-64, NEON on AArch64.

## Compared with alternatives

Pick misa77 over LZ4 when decode throughput is the hot path and compression is a one-off cost: in lzbench 2.4 level 1 decodes at 7813 vs 3832 MB/s with a smaller output. Its edge narrows at high ratios (level 4: 5177 MB/s at 35.51% vs lzsse8 -6: 5007 MB/s at 35.61%, though LZSSE is x86-only), and ZXC -1 decodes faster (8151 MB/s) at a much worse ratio (61.76%); prefer LZ4 or ZXC when compression speed or a stable format matters, and zstd when ratio matters more than decode speed.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (CMake &gt;= 3.20 for the build; the CLI needs POSIX) |
| **Minimum toolchain** | C++20, GCC or Clang (MSVC not documented and the source uses GCC/Clang builtins), CMake 3.20+ |
| **Platforms** | little-endian 64-bit only: x86-64 (runtime AVX2/SSE2 dispatch), AArch64 (NEON), portable scalar fallback for others |
| **Thread safety** | not documented; the API is stateless free functions over caller-owned buffers |
| **Drop-in for the baseline** | partial — same role as LZ4's block API (one-shot buffer compress/decompress) but different function signatures and an incompatible format; no LZ4 frame or streaming equivalent |

## Gotchas

- decompress defaults to the unsafe decoder; pass misa77::dconfig(true) for corrupt or hostile input (README: about 3% slower on x86-64, 1-2% on M3; lzbench 2.4: 7694 vs 7813 MB/s at level 1).
- Size the output with compress_bound using the same config as compress, because the bound differs between the light and heavy formats.
- Decompression throughput is not monotonic in level: level 1 decodes fastest, level -1 decodes 23-28% slower, levels 2-4 13-21% slower.
- Results are sensitive to codegen: the default CMake build uses -march=x86-64 for the CLI and core, and the README recommends -DMISA77_MARCH=native; do not enable LTO (the CMake file warns it breaks the ISA fallbacks).

## Known shortcomings

- Tier B on lzbench (decode 7813 vs lz4 3832 MB/s, about 2x derived from page data); flags not on the page.
- Format is v0.x and may change; level 4 (the heavy format) has no safe decoder and the unsafe decoder is the default; compression is about 7x slower than lz4; GCC/Clang only (__builtin_cpu_supports). At matched ratio the edge mostly vanishes: level 4 at 5177 MB/s and 35.51% vs lzsse8 -6 at 5007 MB/s and 35.61% (lzbench 2.4).

## Caveats and trade-offs

Compares against LZ4-class codecs; zstd and zlib are not beaten on ratio. Ratio is worse than lz4hc at some levels. The lzbench table is third-party (lzbench maintainer) but the exact compile flags are not stated. Project is young (0.6.0).

Slow compression by design (write-once, read-many). Needs a C++20 compiler, little-endian 64-bit only; AVX2/SSE2 chosen at runtime on x86, NEON on ARM. Unsafe decoder has undefined behavior on corrupt input; the safe decoder costs about 3-5% and level 4 has no safe decoder yet.

## Maintenance

Active (last commit 2026-08-10, 172 stars, 1 open feature request) and MIT-licensed, small enough to vendor via add_subdirectory, but a young v0.6.0 codec whose format is not frozen and whose hardening is limited so far to local ASan/UBSan fuzzing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The independent lzbench 2.4 table (public code, gcc 15.2.0, single thread of an EPYC 9555P) lists misa77 0.6.0 -1 at 73.8 MB/s compress, 7813 MB/s decompress, 42.65% vs lz4 1.10.0 at 550 / 3832 MB/s, 47.60%; flags are not stated on the page, so B. The README's own lzbench runs (i7-14650HX turbo off, Apple M3) name no compiler or flags, so they alone would be C.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** README numbers and lzbench rows match the record; MIT license, 172 stars, last commit 2026-08-10 confirmed. misa77 was merged into lzbench recently (0.6.0 dated 2026-07-30), so the lzbench run is by the suite maintainer, not the misa77 author.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://github.com/welcome-to-the-sunny-side/misa77>
  - <https://raw.githubusercontent.com/welcome-to-the-sunny-side/misa77/HEAD/README.md>
  - <https://github.com/welcome-to-the-sunny-side/misa77/commits/main>
- **Sources the enricher read:**
  - <https://github.com/welcome-to-the-sunny-side/misa77>
  - <https://raw.githubusercontent.com/welcome-to-the-sunny-side/misa77/HEAD/README.md>
  - <https://raw.githubusercontent.com/welcome-to-the-sunny-side/misa77/HEAD/docs/format.md>
  - <https://raw.githubusercontent.com/welcome-to-the-sunny-side/misa77/HEAD/include/misa77/misa77.h>
  - <https://raw.githubusercontent.com/welcome-to-the-sunny-side/misa77/HEAD/src/format.h>
  - <https://raw.githubusercontent.com/welcome-to-the-sunny-side/misa77/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/welcome-to-the-sunny-side/misa77/HEAD/src/decompressor_zoo/light_unsafe_dimpl.h>
  - <https://raw.githubusercontent.com/welcome-to-the-sunny-side/misa77/HEAD/src/decompress.cpp>
  - <https://raw.githubusercontent.com/welcome-to-the-sunny-side/misa77/HEAD/src/compress.cpp>
  - <https://github.com/welcome-to-the-sunny-side/misa77/issues?q=is%3Aissue>
  - https://github.com/inikep/lzbench (README via https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md)
  - WebSearch: misa77 compression codec decompression faster than LZ4 (snippets of the Show HN thread and a dev.to write-up; pages not opened)
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/welcome-to-the-sunny-side/misa77`) · [data/wave9/enrich/raw/github_com_welcome_to_the_sunny_side_misa77.json](../../../data/wave9/enrich/raw/github_com_welcome_to_the_sunny_side_misa77.json) (enrichment confidence 0.85)

</details>
