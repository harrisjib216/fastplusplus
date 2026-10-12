# memlz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Header-only C/C++ word-hash compressor that compresses about 4.8x faster than LZ4 --fast -17 at similar ratio; decompresses slower.

| | |
|---|---|
| **Beats** | LZ4 (with acceleration around 32 to 64), Snappy, FastLZ, LZO |
| **Claimed result** | lzbench 2.4 (silesia.tar, one thread of an EPYC 9555P): memlz 0.5 beta compresses at 4452 MB/s and decompresses at 2039 MB/s at 59.90% size, vs lz4 1.10.0 at 550 / 3832 MB/s, 47.60%; lz4 --fast -17 at 924 / 3977 MB/s, 62.15%; snappy 1.3.1 at 457 / 976 MB/s, 47.85%; lzo1x 2.10 -1 at 500 / 561 MB/s; fastlz 0.5.0 -1 at 273 / 587 MB/s; memcpy 24075 MB/s. Compression is about 4.8x lz4 --fast -17, 8.1x default lz4 and 9.7x snappy (derived from page data); decompression is about 0.53x lz4 (slower) and 2.1x snappy (derived from page data). First-party README: '5 - 7 GB/s in one thread'; its Figure_1.png (Intel i7, model not stated) plots memlz compression at roughly 5800 MB/s on Silesia vs roughly 2250 MB/s for LZ4-64 (approximate, read from graph). |
| **Workload** | Single-thread in-memory compression and decompression of silesia.tar in lzbench 2.4 (independent); first-party README figures cover enwik8, Silesia and employees_50MB.json. |
| **Metric** | throughput |
| **Hardware** | Independent: single thread of an AMD EPYC 9555P at 3.20 GHz, turbo off (lzbench 2.4). First-party README figures: Intel i7 (model not stated) with 14000 MB/s non-cached memcpy. |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 79 stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/rrrlasse/memlz) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

In lzbench 2.4 (gcc 15.2.0 release build, one thread of an AMD EPYC 9555P with turbo off, silesia.tar), memlz 0.5 beta compressed at 4,452 MB/s and decompressed at 2,039 MB/s with a 59.90% output size, versus lz4 1.10.0 --fast -17 at 924/3,977 MB/s and 62.15%, lz4 default at 550/3,832 MB/s and 47.60%, and snappy 1.3.1 at 457/976 MB/s (compression about 4.8x lz4 --fast -17 and 8.1x lz4 default; decompression about 0.53x lz4, derived from page data). The README's 5-7 GB/s single-thread figure comes from the author's Intel i7 runs (model not stated) and is not reproduced by lzbench's 4,452 MB/s.

## Use it when

- Compression throughput is the bottleneck and roughly 60% output size is acceptable: backup, dedup and archiver pipelines, snapshotting, or spilling large buffers where LZ4 default is too slow.
- Streams of many small packets fed through one memlz_state (the README's eXdupe test streamed kilobyte packets at 4,616 MB/s without a 1 MB copy queue).
- Buffers of megabytes, where the one-off 768 KiB table reset is amortised.
- x86-64 hosts, where the SSE4.2 paths are compiled in; projects that want a one-file, dependency-free drop into C or C++.

## Skip it when

- Read-heavy data: lzbench 2.4 measured decompression at 2,039 MB/s, about 0.53x LZ4's 3,832 MB/s, so compress-once/read-often workloads should use LZ4, LZAV or similar.
- Small blocks or pages: every call (or reset) clears two hash tables of 768 KiB in total; an independent zram test (martinus/quetschn PR #17) found about 10 us per 4 KiB page in each direction and 63.6% stored size versus 34.5% for LZ4, and dropped it.
- When ratio matters: 59.90% on silesia.tar versus 47.60% for LZ4 default and 47.85% for Snappy.
- Persistent storage or interchange: the format is beta and the README warns compatibility may break between versions (header now says 0.6 beta; lzbench measured 0.5 beta).
- Non-x86 targets expecting the headline speed: ARM64 is tested but uses the scalar path only (no NEON code); big-endian behavior is not documented.

## How it is fast

It is an 8-byte-word variant of Guillaume Voirin's Chameleon algorithm (the LZP-style dictionary coder from Density): each 4- or 8-byte word is hashed with a multiplicative hash into a 64K-entry table, and if the table already holds that word the encoder emits the 16-bit hash, otherwise the literal word, with one flag bit per word. There are no match lengths, offsets or back-references, so there is no match search and the decoder rebuilds the same table as it goes. On x86-64 it processes several words per step with SSE4.1/4.2 (vectorised hashing, cmpeq/movemask hit masks and pshufb compaction), probes each 128 KB block to choose 4- or 8-byte words, and special-cases runs of repeated words (RLE) and incompressible stretches. Because the table stores word values rather than positions, streaming needs no history window, which removes the extra memcpy that LZ4-style streaming needs.

## Compared with alternatives

Pick memlz over LZ4 (including --fast acceleration) or Snappy only when compression speed is the binding constraint and decode speed and ratio can give: lzbench shows 4,452 MB/s compression versus 924 MB/s for lz4 --fast -17 at a similar ratio, but about half of LZ4's decode speed. Density uses the same Chameleon idea; compare both on your hardware, and prefer LZ4, LZAV or ZXC when data is read more often than written or blocks are small.

## Integration

| | |
|---|---|
| **Form** | header-only (define MEMLZ_IMPLEMENTATION in one translation unit) |
| **Dependencies** | none (libc malloc/memcpy; smmintrin.h on x86-64) |
| **Minimum toolchain** | C11 (stdalign.h, _Alignas) or C++11 (alignas); tested with clang, gcc and Visual Studio |
| **Platforms** | x86-64 with SSE4.2 code paths (selected via target attributes on GCC/clang; MSVC uses no attribute); ARM64 and other CPUs use portable scalar code |
| **Thread safety** | Not documented; the one-shot functions allocate a private state per call and the only statics are const tables, so independent calls are safe on separate threads, while a memlz_state must not be shared between threads. |
| **Drop-in for the baseline** | no |

## Gotchas

- Decompression takes no input-length argument: the safety guarantee only covers the bounds the header declares, so check memlz_compressed_len(src) against your real buffer size (and size the output from memlz_decompressed_len) before decompressing untrusted data.
- memlz_max_compressed_len() is 68\*len/64+100 with a 'todo, find real bound' comment in the source; allocate at least that much and do not rely on a tighter bound.
- memlz_compress/memlz_decompress malloc and memset about 768 KiB of tables on every call and return 0 on allocation failure; reuse a memlz_state through the stream API to avoid that cost.
- Stream chunks must be decompressed in exactly the order they were compressed, with the same state reset once at the start; the state must be reset with memlz_reset() before first use or calls return 0.

## Known shortcomings

- Raised C to B via lzbench 2.4 (EPYC 9555P, gcc 15.2.0): compress 4452 MB/s at 59.90% vs lz4 --fast -17 at 924 and snappy at 457, but decompression (2039 MB/s) is about 0.53x lz4, so the win is compression only.
- decompress takes no input length, so bounds come from the header only; memlz_max_compressed_len is marked 'todo, find real bound'; one-shot calls malloc and memset 768 KiB of tables on every call; the header is now 0.6 beta while lzbench measured 0.5; no NEON path.

## Caveats and trade-offs

Compression-speed win only: decompression is about half of LZ4's speed in lzbench and the ratio (59.90%) is much worse than lz4 default or snappy (about 47.6-47.9%); the fair comparison is lz4 --fast -17 (62.15%, 924 MB/s). lzbench measured 4452 MB/s, below the README's 5-7 GB/s claim (different CPU). Beta format, compatibility may break. lzbench patches memlz.h for MinGW (SSE4.2 target attribute).

Header-only C/C++, streaming mode with no extra memcpy, bounds-safe decompression. Trades ratio for compress speed and the format may change (README marks it beta).

## Maintenance

Active: 35 commits, last on 2026-10-02, with recent speedups, a 'Fix UB reads/writes' commit and an AFL fuzz harness (ASan round-trip plus malformed-input decode); MIT-licensed and trivial to vendor, but beta, so pin the version and do not use it for long-lived stored data yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the independent lzbench 2.4 suite (public code, inikep/lzbench; gcc 15.2.0 release binary; single thread of an AMD EPYC 9555P, turbo off, silesia.tar) lists memlz 0.5 beta at 4452 MB/s compress, 2039 MB/s decompress, 59.90% vs lz4 1.10.0 --fast -17 at 924 / 3977 MB/s, 62.15% and snappy 1.3.1 at 457 / 976 MB/s, 47.85%. Compile flags are not on the results page, so B, not A (consistent with lzav, lzsse, misa77 in this wave).
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** README numbers live in PNG figures (opened them: Figure_1 compress, Figure_2 decompress, LZ4/zstd-1/blosclz/Chameleon only); the stronger evidence is the lzbench table, which lists memlz alongside lz4, snappy, lzo, fastlz. Metadata OK: MIT, 79 stars, last commit 2026-10-02.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** independent: lzbench 2.4 README; independent: martinus/quetschn PR #17 zram test (4.5 GHz, 455,239 pages) stored 63.6% of pages with memlz vs 34.5% with LZ4 at about 10 us per page both ways, and dropped it
- **Pages the verifier opened:**
  - <https://github.com/rrrlasse/memlz>
  - <https://github.com/rrrlasse/memlz/commits>
  - <https://raw.githubusercontent.com/rrrlasse/memlz/HEAD/README.md>
  - <https://raw.githubusercontent.com/rrrlasse/memlz/res/Figure_1.png>
  - <https://raw.githubusercontent.com/rrrlasse/memlz/res/Figure_2.png>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/rrrlasse/memlz>
  - <https://raw.githubusercontent.com/rrrlasse/memlz/HEAD/README.md>
  - <https://raw.githubusercontent.com/rrrlasse/memlz/HEAD/memlz.h>
  - <https://github.com/rrrlasse/memlz/commits>
  - <https://github.com/rrrlasse/memlz/tree/main/test>
  - <https://raw.githubusercontent.com/rrrlasse/memlz/HEAD/test/afl.c>
  - <https://raw.githubusercontent.com/rrrlasse/memlz/HEAD/test/run.sh>
  - <https://github.com/martinus/quetschn/pull/17>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/rrrlasse/memlz`) · [data/wave9/enrich/raw/github_com_rrrlasse_memlz.json](../../../data/wave9/enrich/raw/github_com_rrrlasse_memlz.json) (enrichment confidence 0.75)

</details>
