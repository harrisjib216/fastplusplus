# LZAV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C (header-only, C99; C++ compatible)` · `MIT` · 🟢 active

> Single-header C99 LZ77 codec: about 16% smaller output than LZ4/Snappy at Snappy-class compress speed.

| | |
|---|---|
| **Beats** | Snappy |
| **Claimed result** | README (Apple M1): LZAV 5.18 compress 627 MB/s, decompress 3830 MB/s, ratio 39.91% vs Snappy 1.1.10 495 / 3230 MB/s, 48.22%; vs LZ4 1.9.4 700 / 4570 MB/s, 47.60%. lzbench 2.4 (EPYC 9555P): lzav 5.17 -1 compress 451 MB/s, decompress 2527 MB/s, 39.91% vs snappy 1.3.1 457 / 976 MB/s, 47.85%. |
| **Workload** | In-memory compress and decompress of silesia.tar vs LZ4 and Snappy. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 9555P at 3.20 GHz, single thread, performance governor, turbo disabled, Ubuntu 26.04; README: Apple M1 3.5 GHz, Xeon E-2386G 5.1 GHz |
| **Compiler and flags** | gcc 15.2.0 (lzbench 2.4 release binary lzbench24_x86_64-linux-gnu-gcc15); lzbench v2.4 Makefile OPT_FLAGS_O3: -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG (a few codecs use the -O2 variant); run options -eALL -t8,8 -o1c4 |
| **Adoption** | 550 stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/avaneev/lzav) · [benchmark](https://github.com/inikep/lzbench) |

## Verdict

In the independent lzbench 2.4 run (gcc 15.2.0 release binary, one thread of an EPYC 9555P, silesia.tar), lzav 5.17 -1 compressed at 451 MB/s and decompressed at 2527 MB/s for a 39.91% ratio, vs snappy 1.3.1 at 457 / 976 MB/s and 47.85%: same compress speed, 2.6x decompress (derived from page data), much better ratio. The author's README tables (Apple M1 with Apple clang 15, Xeon E-2386G with clang 19.1.7, Ryzen 3700X with clang-cl 18.1.8) show a smaller decompress margin over Snappy 1.1.10 (3830 vs 3230 MB/s on M1) and LZ4 1.9.4 faster in both directions. The lzbench Snappy decompress figure (976 MB/s) is far below what the README measures for Snappy (2440-3360 MB/s), so treat the 2.6x as specific to that build; the robust wins are ratio and parity-or-better speed vs Snappy.

## Use it when

- Replacing Snappy or LZF for in-memory block compression (database pages, cache values, filesystem blocks) when you want 39.9% instead of about 48% ratio on Silesia at similar compress speed.
- Projects that want one MIT header with no build system, dependencies or SIMD requirements, including big-endian, 32-bit and WebAssembly targets.
- Decoding untrusted or possibly damaged blocks: the decompressor bounds-checks every source, destination and back-reference access and returns an error code rather than crashing.
- Write-once/read-many assets via lzav_compress_hi(): 34.85% on Silesia, decoded by the same fast decompressor.

## Skip it when

- Decompression-speed-bound paths: LZ4 decodes faster everywhere measured (lzbench EPYC 9555P: lz4 1.10.0 3832 MB/s vs lzav -1 2527 MB/s; README Apple M1: 4570 vs 3830 MB/s).
- Pure compress-speed needs: LZ4 default and lz4 --fast levels compress faster (README: LZAV about 30% slower than LZ4 at compression).
- Streaming, framed or interoperable formats: no frame, no checksum, no streaming API; you must store the uncompressed length yourself.
- Inputs larger than 2 GiB per call (int lengths); chunk them, ideally 16 MiB or more per chunk to keep the ratio.
- When zstd's ratio range matters: zstd -1 reaches 34.6% (README TurboBench) and scales to far higher levels; LZAV has only two levels.

## How it is fast

Classic LZ77 with a hash table of (4-byte prefix, 32-bit offset) tuples, 1 tuple per bucket in the default compressor (a 2048-entry on-stack table for small inputs, heap up to 1 MiB) and 8-tuple buckets in the slower HI compressor. The block format uses 10/15/21-bit offsets plus 'offset-carry' bits borrowed from neighbouring blocks, which gives a dynamic window of 2 MiB to 512 MiB at low header cost; that bigger window is where the ratio gain over LZ4 comes from. The code is scalar and portable (no SIMD), relying on prefetch hints, forced inlining and branch-likelihood hints.

## Compared with alternatives

Pick LZAV over LZ4 when ratio matters more than raw speed and you still want one portable header (39.91% vs 47.60% on Silesia); pick it over zstd --fast/-1 when decompression speed matters (lzbench: 2527 vs 1707 MB/s at 39.91% vs 41.01%) and you do not need zstd's frame format, streaming or higher levels. Pick LZ4 or misa77 if decode speed is the priority.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (libc malloc/free or C++ new[]/delete[] by default) |
| **Minimum toolchain** | ISO C99 compiler or any C++ compiler; tested with Clang, GCC, MSVC and Intel C++ |
| **Platforms** | any; tested on x86, x86-64 and AArch64 (Apple Silicon) under Windows, Linux and macOS; big- and little-endian; WebAssembly/WASI at about half native speed |
| **Thread safety** | Functions are reentrant (internal hash table is on stack or per-call heap); a caller-supplied extbuf hash table must not be shared between concurrent calls. |
| **Drop-in for the baseline** | no |

## Gotchas

- lzav_decompress() takes the expected decompressed length and returns an error if the output length differs; store it separately (issue #13 asked for a built-in size header and it was closed).
- Output of the same input may differ between LZAV versions and between big- and little-endian machines; only decompression of older formats is guaranteed (format 2 support can be dropped with LZAV_FMT_MIN=3).
- OOB checks do not guarantee correct output on corrupted input; the header advises checksumming the uncompressed data and the length header yourself.
- C++ build is noexcept and uses new[] by default; define LZAV_EXCEPT to allow throwing allocation, LZAV_MALLOC/LZAV_FREE for a custom allocator, LZAV_NS_CUSTOM to move symbols out of the global namespace. All functions are static, so no ABI to keep stable.

## Known shortcomings

- Tier B on lzbench: not faster than LZ4 or zstd at comparable ratios; the win is lzav -1 decompressing at 2527 MB/s vs zstd --fast --1 at 1707 MB/s (derived from page data). Flags not on the page.
- Decodes slower than LZ4 everywhere (lzbench 2527 vs 3832 MB/s); no tests, fuzzing or CI in the repo; the caller must store the original length; output differs across versions and endianness. lzbench's snappy 1.3.1 decompress (976 MB/s) is far below the README's Snappy 2440-3360 MB/s, so the 2.6x win over Snappy is likely build-specific. Issue #2 (2023, closed): decompress returned -5 with no documented fix.

## Caveats and trade-offs

Not faster than LZ4: LZ4 compresses and decompresses faster in both README and lzbench. The win over Snappy is decompression (2.6x in lzbench, derived from page data) and ratio; compression is on par with Snappy in lzbench (451 vs 457 MB/s). Baseline Snappy is outside the list; LZ4 comparison is a ratio-only win.

Decompressor needs the original length stored separately; blocks up to 2 GiB; \~16% better ratio than LZ4 at lower compress speed.

## Maintenance

Actively developed by one author (version 5.18, last commit 2026-10-01, 550 stars), MIT-licensed single header that is trivial to vendor; the repo has no test suite, fuzzing harness or CI visible.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now A.
- **Tier reason:** The independent lzbench suite (public code, gcc 15.2.0, single thread of an EPYC 9555P) lists lzav 5.17 -1 at 451 / 2527 MB/s, 39.91% vs snappy 1.3.1 at 457 / 976 MB/s, 47.85%; compile flags are not on the page, so B, not A. The README's own Silesia tables (Apple M1, Xeon E-2386G, Ryzen 3700X with named compilers) are first-party without flags or harness code.
- **Retiered** B to A: Raised B to A for tier consistency with FastLZ (batch verdict A on the same table): the evidence is the lzbench 2.4 README table, an independent public suite (inikep/lzbench, tag v2.4) whose release binary lzbench24_x86_64-linux-gnu-gcc15 is built with gcc 15.2.0 from the public Makefile (OPT_FLAGS_O3 = -fomit-frame-pointer -fstrict-aliasing -O3 -DNDEBUG, line 147; some codecs use the -O2 variant, line 146), run single-threaded on an AMD EPYC 9555P at 3.20 GHz with -eALL -t8,8 -o1c4 on silesia.tar. Compiler, flags, CPU model and harness are all public, so the run is reproducible and meets tier A; the earlier B verdicts counted the flags as unstated because they are not repeated on the results page.
- **Verifier notes:** All numbers in the record match the README and lzbench pages. In lzbench lzav -1 also decompresses faster than zstd 1.5.7 --fast --1 (2527 vs 1707 MB/s, derived from page data) at a similar ratio (39.91% vs 41.01%), which gives an in-list baseline comparison. The README itself states that LZ4 compresses faster.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/inikep/lzbench>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/avaneev/lzav/HEAD/README.md>
  - <https://github.com/avaneev/lzav>
  - <https://github.com/avaneev/lzav/commits>
- **Sources the enricher read:**
  - <https://github.com/avaneev/lzav>
  - <https://raw.githubusercontent.com/avaneev/lzav/HEAD/README.md>
  - <https://raw.githubusercontent.com/avaneev/lzav/HEAD/lzav.h>
  - <https://github.com/avaneev/lzav/issues?q=is%3Aissue>
  - <https://github.com/avaneev/lzav/issues/2>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/avaneev/lzav`) · [data/wave9/enrich/raw/github_com_avaneev_lzav.json](../../../data/wave9/enrich/raw/github_com_avaneev_lzav.json) (enrichment confidence 0.85)

</details>
