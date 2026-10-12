# libdeflate

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Whole-buffer DEFLATE/zlib/gzip C library: about 2.6x zlib's decompression speed and 3.3x its level-6 compression, plus faster CRC-32.

| | |
|---|---|
| **Beats** | zlib crc32() |
| **Claimed result** | NEWS.md v1.12: CRC-32 on large inputs on Apple M1 'is now about 67 GB/s, compared to 8 GB/s before, or 31 GB/s with the Apple-provided zlib' (\~2.2x vs zlib crc32, derived from page data). Separately, the README says libdeflate 'is significantly faster than the zlib library' (general claim). |
| **Workload** | CRC-32 checksum computation via the public libdeflate_crc32() API; the repo ships a 'checksum' test program that can checksum data with Adler-32 or CRC-32 using either libdeflate or zlib and optionally measure speed |
| **Metric** | throughput |
| **Hardware** | Apple M1 (for the v1.12 CRC-32 figure) |
| **Adoption** | 1.3k stars; used as an optional/default backend in libtiff, htslib, OpenEXR, and uWebSockets |
| **Last commit** | 2026-08-22 |
| **Links** | [repository](https://github.com/ebiggers/libdeflate) · [benchmark](https://github.com/ebiggers/libdeflate/blob/master/NEWS.md) |

## Verdict

The only CRC-32 vs zlib figure is the author's own NEWS.md note for v1.12 (2022): about 67 GB/s vs 31 GB/s for Apple's system zlib (\~2.2x) on large inputs on Apple M1, with no compiler, flags or input details. For DEFLATE, the independent lzbench 2.0.1 README (gcc 14.2.0, one thread of an AMD EPYC 9554 at 3.10 GHz with turbo off, silesia.tar) shows libdeflate 1.23 at level 6 compressing at 84.3 MB/s and decompressing at 912 MB/s, vs 25.3/344 for zlib 1.3.1 and 62.1/509 for zlib-ng 2.2.3; a 2023 TurboBench run on a Ryzen 6600HS shows the same ordering.

## Use it when

- Chunked compression where each chunk fits in memory and its uncompressed size is stored separately: filesystem or block compression, BGZF genomics blocks (htslib probes for libdeflate by default), TIFF strips (libtiff), OpenEXR (bundles or finds libdeflate).
- Decompression-heavy gzip/zlib workloads. In lzbench (EPYC 9554, Silesia, level 6 data) it decompresses at 912 MB/s against 344 for zlib 1.3.1 and 509 for zlib-ng 2.2.3.
- Level 6-9 compression when the output must stay DEFLATE-compatible: 84.3 MB/s at level 6 vs 25.3 (zlib) and 62.1 (zlib-ng), at a slightly better ratio (31.85% vs 32.19% and 32.49%).
- Smaller-than-zlib-9 DEFLATE output (for example PNG/ZIP assets built once and served many times). Level 12 reaches 30.52% vs 31.92% for zlib -9, at about 5 MB/s.
- Replacing zlib crc32() in hot paths on CPUs with PCLMULQDQ or ARMv8 PMULL. On Apple M1 the author measured about 67 GB/s vs 31 GB/s for Apple's zlib.

## Skip it when

- Streaming data: a single large gzip stream, sockets, or input whose size is unknown. There is no streaming API (issue #19 is still open), and the bundled libdeflate-gzip 'needs a lot of memory to process large files'. zlib-ng fits there.
- When you need a drop-in zlib API (deflateInit/inflate, z_stream). Code must be ported to libdeflate's own calls.
- Maximum speed at the lowest levels. In a TurboBench run on a Ryzen 6600HS, ISA-L igzip level 1 compressed at 615 MB/s vs 289 for libdeflate level 1, with a worse ratio (36.9% vs 34.7%). If the format is not fixed, LZ4 or zstd beat any DEFLATE.
- Memory-tight compression. A compressor takes about 668 KB at levels 2-9 and about 9 MB at levels 10-12 (issue #315); the author says this is more than zlib uses.
- CRC-32 on Intel AVX-512 parts older than Rocket Lake or Sapphire Rapids (Skylake-SP through Tiger Lake). libdeflate deliberately avoids 512-bit vectors there, and the author says zlib-ng winning CRC-32 benchmarks on those chips 'is currently expected' (issue #338 measured about 2x).

## How it is fast

The decompressor reads input and copies matches a word at a time and keeps a large bit buffer that needs refilling less often. It uses faster table-driven Huffman decoding with DEFLATE-specific tricks, and drops the branches needed to pause and resume because it only decodes whole buffers. On x86-64 a BMI2-compiled copy is picked at runtime. Each compressor level uses its own matchfinder: a hash table at level 1, hash chains with greedy/lazy/lazy2 parsing at 2-9, and binary trees with near-optimal (minimum-cost-path) parsing at 10-12, plus a block-splitting heuristic. CRC-32 uses carryless-multiply folding, chosen at runtime: PCLMULQDQ, then VPCLMULQDQ with 256- or 512-bit vectors (AVX2/AVX-512) on x86, and 12-way PMULL folding combined with crc32 instructions (plus EOR3 when SHA3 is present) on arm64. Other targets fall back to slice-by-8 tables.

## Compared with alternatives

Pick libdeflate over zlib-ng when you handle whole buffers and can adopt a new API. It decompresses about 1.8x faster than zlib-ng in lzbench, is faster at levels 6-9 with a slightly better ratio, and at level 1 matches zlib-ng's speed (207 vs 202 MB/s) with a much better ratio (34.7% vs 44.4%). Pick zlib-ng for streaming, zlib API compatibility, or CRC-32 on pre-Rocket-Lake Intel AVX-512 chips, and pick LZ4 or zstd whenever the output does not have to be DEFLATE/zlib/gzip.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib via CMake, or a source-drop (compile lib/\*.c and lib/\*/\*.c directly, no configure step) |
| **Dependencies** | none for the library; the bundled benchmark/checksum test programs use zlib for comparison runs |
| **Minimum toolchain** | C11 (since v1.26): gcc 4.9+, clang 3.9+ / Xcode 8+, MSVC 2019 16.8+; CMake 3.10+. Newer compilers enable more of the optimized code (the VPCLMULQDQ CRC paths need gcc 10+ or clang 6+ and are disabled under clang 18). |
| **Platforms** | Any C11 target. Runtime-dispatched optimized paths exist for x86/x86-64 (PCLMULQDQ, VPCLMULQDQ AVX2/AVX-512, BMI2 decompression, AVX2/VNNI Adler-32) and arm64 (PMULL, CRC32, SHA3, NEON/dotprod), with some tuning for RISC-V and PowerPC. 32-bit ARM lost accelerated CRC-32 in v1.20. There are prebuilt 64-bit Windows binaries, and a freestanding build is supported. |
| **Thread safety** | One compressor or decompressor must not be used by several threads at once, but separate objects can run concurrently (libdeflate.h). libdeflate_crc32/adler32 keep no state except a function pointer set on the first call. |
| **Drop-in for the baseline** | partial — libdeflate_crc32() matches zlib crc32()'s running-CRC semantics (and takes size_t like crc32_z), so CRC calls map one-to-one, but there is no crc32_combine. The compression API is not zlib-compatible and is whole-buffer only. |

## Gotchas

- Decompression wants the exact uncompressed size. Pass it as out_nbytes_avail with a NULL actual_out pointer to get LIBDEFLATE_SHORT_OUTPUT on a mismatch. With an unknown size you must guess a buffer and retry on LIBDEFLATE_INSUFFICIENT_SPACE, and the output buffer is undefined on any error.
- libdeflate_gzip_decompress() stops after the first gzip member. Loop over libdeflate_gzip_decompress_ex() for multi-member files (pigz/BGZF output).
- The compress functions return 0 when the output does not fit; store the chunk uncompressed in that case. Compressed bytes change between versions, so never test against golden output. The decompressor still accepts some malformed streams that zlib rejects (open issue #288).
- v1.20-1.22 could compute wrong CRCs on AVX-512 machines in rare builds (clang -O0; old macOS register-corruption bug), fixed in 1.23. The README warns that many language bindings pin old versions.

## Known shortcomings

- Only CRC figure is first-party (NEWS.md v1.12: Apple M1 CRC-32 \~67 GB/s vs Apple zlib \~31, \~2.2x) with no compiler or flags. Whole-buffer API only (no streaming). Found in wave 7 for its CRC-32; filed under wave 9's general-lossless category.
- No streaming or zlib-compatible API (whole buffers only); compressor uses 668 KB-9 MB of memory; igzip beats it at level 1; no crc32_combine. zlib-ng's CRC is \~2x faster on pre-Rocket-Lake Intel AVX-512 (issue #338, by design). Open #288: decoder accepts some streams zlib rejects.

## Caveats and trade-offs

The only numeric CRC-32 vs zlib figure is a one-line first-party note in NEWS.md for v1.12 (2022). It was measured on Apple M1 against Apple's system zlib (not necessarily stock zlib) and gives no compiler, flags or input description. The CRC code has changed since then (v1.20 added VPCLMULQDQ; later releases tuned Neoverse V). No x86 or current results table against zlib is published, though the benchmark tooling (programs/checksum.c, scripts/checksum_benchmarks.sh) is public. The usage list (libtiff, htslib, OpenEXR, uWebSockets) was not re-verified.

Primarily a whole-buffer DEFLATE/zlib/gzip compressor; libdeflate_crc32() is a secondary utility function rather than the library's focus; no incremental/streaming-only CRC API beyond the single function call

## Maintenance

Actively maintained by Eric Biggers (v1.26 released 2026-08-22, regular releases since 2016, about a dozen open issues), MIT-licensed, stable 1.x API, and easy to vendor because the sources compile without a configure step.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D. NEWS.md (v1.12, released 2022-06-12) gives first-party CRC-32 figures on Apple M1: about 67 GB/s for libdeflate vs 31 GB/s for the Apple-provided zlib. It gives no compiler, flags or input details, although the checksum tool (programs/checksum.c, -Z selects zlib) and scripts/checksum_benchmarks.sh are public.
- **Verifier notes:** The metadata checks out: MIT, 1293 stars, last commit 2026-08-22, not archived, not a fork. The upgrade to C rests on the M1 figure in NEWS.md; no commit messages on the CRC-32 source files contain numbers.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** libdeflate NEWS v1.12: M1 crc32 \~67 GB/s vs Apple zlib \~31 GB/s.; lzbench (EPYC 9554) level 6: libdeflate decompress 912 vs zlib 344, zlib-ng 509 MB/s; compress 84.3 vs 25.3, 62.1 MB/s.
- **Pages the verifier opened:**
  - <https://github.com/ebiggers/libdeflate>
  - <https://github.com/ebiggers/libdeflate/blob/master/NEWS.md>
  - <https://github.com/ebiggers/libdeflate/blob/master/scripts/checksum_benchmarks.sh>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/crc32.c>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/x86/crc32_impl.h>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/arm/crc32_impl.h>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/x86/crc32_pclmul_template.h>
- **Sources the enricher read:**
  - <https://github.com/ebiggers/libdeflate>
  - <https://github.com/ebiggers/libdeflate/blob/master/README.md>
  - <https://github.com/ebiggers/libdeflate/blob/master/NEWS.md>
  - <https://github.com/ebiggers/libdeflate/blob/master/libdeflate.h>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/crc32.c>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/x86/crc32_impl.h>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/x86/crc32_pclmul_template.h>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/x86/cpu_features.c>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/arm/crc32_impl.h>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/arm/crc32_pmull_helpers.h>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/crc32_multipliers.h>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/crc32_tables.h>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/deflate_decompress.c>
  - <https://github.com/ebiggers/libdeflate/blob/master/lib/deflate_compress.c>
  - <https://github.com/ebiggers/libdeflate/blob/master/programs/checksum.c>
  - <https://github.com/ebiggers/libdeflate/blob/master/scripts/checksum_benchmarks.sh>
  - <https://github.com/ebiggers/libdeflate/blob/master/CMakeLists.txt>
  - <https://github.com/ebiggers/libdeflate/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/ebiggers/libdeflate/issues/338>
  - <https://github.com/ebiggers/libdeflate/issues/315>
  - <https://github.com/ebiggers/libdeflate/issues/288>
  - <https://github.com/ebiggers/libdeflate/issues/284>
  - <https://github.com/ebiggers/libdeflate/issues/403>
  - <https://github.com/ebiggers/libdeflate/issues/19>
  - <https://github.com/ebiggers/libdeflate/releases>
  - <https://github.com/ebiggers/libdeflate/commits/master>
  - <https://github.com/inikep/lzbench>
  - <https://github.com/zlib-ng/zlib-ng/issues/1486>
  - <https://github.com/samtools/htslib/blob/develop/INSTALL>
  - <https://github.com/AcademySoftwareFoundation/openexr/blob/main/cmake/OpenEXRSetup.cmake>
  - <https://github.com/libsdl-org/libtiff/blob/master/CMakeLists.txt>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/ebiggers/libdeflate`) · [data/wave7/enrich/raw/github_com_ebiggers_libdeflate.json](../../../data/wave7/enrich/raw/github_com_ebiggers_libdeflate.json) (enrichment confidence 0.78)

</details>
