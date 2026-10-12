# miniz

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🟢 active

> Single-file MIT zlib/Deflate replacement with ZIP and PNG helpers; measured slower than zlib, chosen for portability, not speed.

| | |
|---|---|
| **Beats** | zlib |
| **Claimed result** | README: 'at levels 2-9, miniz.c is designed to compare favorably against zlib's ratio and speed'; at level 1 it 'compresses around 5-9% better than minilzo, but is approx. 35% slower'. No numbers against zlib in the README. Independent Wuffs benchmarks (Core i5-10210U, Debian Bullseye builds) show miniz 2.2.0 decoding slower than zlib 1.2.11: deflate 10k 252 vs 289 MB/s (0.87x), 100k 287 vs 352 MB/s (0.82x); zlib 100k 272 vs 323 MB/s (0.84x). Compression speed versus zlib is unmeasured. |
| **Workload** | Single-source-file zlib/Deflate implementation; positioned between fast real-time compressors and zlib. |
| **Metric** | throughput |
| **Adoption** | 2.9k stars; vcpkg and Conan port; used widely for PNG and ZIP |
| **Last commit** | 2026-07-01 |
| **Links** | [repository](https://github.com/richgel999/miniz) · [benchmark](https://github.com/google/wuffs/blob/main/doc/benchmarks.md) |

## Verdict

The README makes only directional claims (levels 2-9 'designed to compare favorably against zlib's ratio and speed'; level 1 about 35% slower than minilzo with 5-9% better ratio) and its referenced performance page was not located. The only independent numbers, Wuffs doc/benchmarks.md (Core i5-10210U, Debian Bullseye builds, Wuffs commit 315b2e52), show miniz 2.2.0 decoding raw deflate at 204/252/287 MB/s versus zlib 1.2.11 at 241/289/352 MB/s (1k/10k/100k, 0.82-0.87x) and zlib streams at 237/272 versus 268/323 MB/s (0.84-0.88x); compression speed versus zlib is unmeasured.

## Use it when

- You need zlib-format compression or decompression in C or C++ with a single MIT-licensed source pair and no build-system dependency (embedded, games, tools).
- You need simple ZIP read/write/append or a quick PNG writer alongside Deflate, without pulling in libzip or libpng.
- Constrained or heap-free environments: tdefl/tinfl state structs can be memcpy-saved, the low-level codecs never allocate, and MINIZ_NO_MALLOC/TDEFL_LESS_MEMORY trim memory.
- Streaming with tiny buffers: the coroutine design accepts input one byte at a time.

## Skip it when

- When speed is the goal: Wuffs measured miniz 2.2.0 decoding at 0.82-0.88x of zlib 1.2.11 (i5-10210U), and libdeflate, zlib-ng and ISA-L are all much faster than zlib on both sides.
- gzip (.gz) streams or zlib features beyond the core: window_bits must be exactly 15 or -15, so gzip wrapping (31/47) and smaller windows are rejected, and there is no gz\* file API, no deflateSetDictionary/inflateSetDictionary and no deflateParams.
- Encrypted or multi-volume ZIP archives (unsupported per the README and header), or ZIP handling of untrusted archives where you cannot tolerate open bugs (see gotchas).
- Multithreaded single-stream compression: it is single-threaded only.
- Very large compressor counts in memory: by default each tdefl_compressor carries roughly 300 KB of fixed arrays (32 KiB dictionary, 64 KiB next-chain, 64 KiB hash, 64 KiB LZ code buffer, \~83 KiB output buffer; estimated from the struct fields).

## How it is fast

It is not faster than zlib on any published measurement. The compressor uses the same hash-chaining LZ77 as zlib (32 KiB window, 2^15-entry hash, per-level probe counts from 1 at level 1 to 1500 at level 10, greedy parsing at levels 0-3) and has a special level-1 path, tdefl_compress_fast, that hashes 3-byte trigrams and compares 16-bit words. The decompressor is a single coroutine function with 10-bit fast Huffman lookup tables and a 64-bit bit buffer on 64-bit targets. CRC-32 is a plain 256-entry table loop, with no slicing-by-8 or carry-less multiply.

## Compared with alternatives

Pick miniz over zlib-ng or libdeflate only when a single-file, C90, MIT-licensed codec with built-in ZIP/PNG helpers matters more than speed; for throughput, libdeflate (1.44-1.74x zlib on the same Wuffs runs) or zlib-ng are the catalogued choices, and LZ4 or zstd if you do not need the Deflate format.

## Integration

| | |
|---|---|
| **Form** | source-drop (amalgamated miniz.c + miniz.h from the releases page) or static/shared lib via CMake/Meson; header-only option via BUILD_HEADER_ONLY |
| **Dependencies** | none (libc only; stdio optional via MINIZ_NO_STDIO) |
| **Minimum toolchain** | C90 (CMake sets CMAKE_C_STANDARD 90); also compiles as C++; tested with GCC, Clang and MSVC per README |
| **Platforms** | any; little-endian and 64-bit detection is automatic, big-endian handled in portable paths |
| **Thread safety** | Separate mz_stream / tdefl / tinfl / mz_zip_archive objects can be used on separate threads; the header notes the ZIP m_last_error functionality is not thread safe; no global mutable state documented otherwise |
| **Drop-in for the baseline** | partial: zlib names and the common deflate/inflate/compress/uncompress/crc32/adler32 calls work (README says tested with libpng and libzip), but no gzip wrapper, no custom window sizes, no dictionaries, no deflateParams and no gz\* file I/O; it reports its version as "11.3.2" through ZLIB_VERSION |

## Gotchas

- Since 3.0.0 MINIZ_USE_UNALIGNED_LOADS_AND_STORES defaults to 0 on every CPU, which compiles out the level-1 fast compressor (tdefl_compress_fast) and the 64-bit bit-writer path; the header itself says to set it to 1 for best performance. If you define it to 1 yourself, MINIZ_UNALIGNED_USE_MEMCPY is not defined, so the code falls back to raw pointer-cast loads (undefined behaviour under strict aliasing and UBSan); define both.
- Open ZIP-layer bugs as of 2026-10: issue 387 (EOCD back-scan signed/unsigned promotion yields a negative file offset), 384 (mz_zip_reader_extract_iter_new frees a non-heap pointer on OOM for in-memory archives), 378 (central-directory offset overflow on zip64), 349 (pointer corruption on bigger files) and 330 (wrong extraction tied to file-position handling). The 3.1.2 changelog fixes a central-directory offset overflow and a code_len==0 infinite loop in tinfl_decompress and adds fuzz targets.
- 32-bit targets: issue 371 reported tinfl_decompress writing past the struct and output buffer on ESP32-S3 (32-bit bit buffer changes the fast-path refill cadence); it is closed, but no fixing commit was shown on the page, so over-allocate or test on 32-bit before trusting it. Issue 373 (claimed heap overflow in code-length RLE) is closed; the current m_len_codes array is padded by 137 bytes, which covers the largest run (counter &lt;= 319 plus up to 138).
- Using zlib and miniz in one binary causes symbol clashes unless MINIZ_NO_ZLIB_COMPATIBLE_NAMES is defined; on glibc, define _LARGEFILE64_SOURCE before including miniz.c or ZIP files over 2 GB fail.

## Known shortcomings

- Not faster: Wuffs' benchmarks put miniz 2.2.0 decode at 0.82-0.88x of zlib 1.2.11 and the README's speed claim has no numbers. Tier D; kept as a notable single-file zlib alternative (2.9k stars).
- Not faster than zlib: Wuffs measures decode at 0.82-0.88x. Since 3.0.0, MINIZ_USE_UNALIGNED_LOADS_AND_STORES defaults to 0, which compiles out tdefl_compress_fast and the 64-bit bit writer; setting it to 1 alone gives raw pointer casts (UB) unless MINIZ_UNALIGNED_USE_MEMCPY is also defined. Partial zlib drop-in: window_bits +-15 only, no gzip wrapper, no dictionaries, no deflateParams, no gz\* API. CRC-32 is a plain table loop. Open ZIP-layer issues 387, 384, 378, 349, 330; issue 371 (32-bit tinfl overwrite) closed with no fix commit shown.

## Caveats and trade-offs

Not faster than zlib on any measured axis: Wuffs shows decompression at 0.82-0.88x of zlib 1.2.11, and the README's compression claim has no numbers. Its value is a single-file, MIT-licensed, zlib-API-compatible implementation with ZIP and PNG helpers, not speed. zlib-ng and libdeflate are much faster. Notable (2.9k stars, vcpkg port).

Single threaded; single file; zlib-compatible API subset; includes PNG writer and ZIP reader/writer.

## Maintenance

Actively maintained (last commit 2026-07-01, 3.1.x line with fuzz targets and Catch2 tests) and MIT-licensed, so it is easy to vendor, but it belongs in the catalog for portability and convenience, not for beating zlib.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): reject; tier before verification D, tier now D.
- **Tier reason:** The README makes only a directional claim ('designed to compare favorably against zlib's ratio and speed' at levels 2-9) with no numbers; the only independent numbers found (Wuffs doc/benchmarks.md, Core i5-10210U, Debian packages, gcc 10.2.1 / clang 11) show miniz 2.2.0 decoding SLOWER than zlib 1.2.11: 0.82-0.87x for raw deflate and 0.84-0.88x for zlib streams.
- **Verifier notes:** Reject as not-faster on valid evidence, so under the keep-and-document rule the orchestrator may override to keep with the shortcoming above (it is notable, 2.9k stars). Metadata confirmed: MIT, 2.9k stars, last commit 2026-07-01, not archived. The README's 'miniz performance comparison page' link target was not located.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; independent Wuffs benchmark
- **Pages the verifier opened:**
  - <https://github.com/richgel999/miniz>
  - <https://github.com/richgel999/miniz/commits>
  - <https://raw.githubusercontent.com/google/wuffs/main/doc/benchmarks.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/readme.md>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/ChangeLog.md>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/miniz.h>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/miniz.c>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/miniz_common.h>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/miniz_tdef.c>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/miniz_tdef.h>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/miniz_tinfl.c>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/miniz_tinfl.h>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/miniz_zip.c>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/miniz_zip.h>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/richgel999/miniz/HEAD/meson.build>
  - <https://github.com/richgel999/miniz/issues?q=is%3Aissue+is%3Aopen+overflow+OR+crash+OR+corrupt+OR+CVE+OR+slow>
  - <https://github.com/richgel999/miniz/issues/373>
  - <https://github.com/richgel999/miniz/issues/371>
  - <https://github.com/richgel999/miniz/issues/330>
  - <https://raw.githubusercontent.com/google/wuffs/main/doc/benchmarks.md>
  - <https://raw.githubusercontent.com/inikep/lzbench/HEAD/README.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/richgel999/miniz`) · [data/wave9/enrich/raw/github_com_richgel999_miniz.json](../../../data/wave9/enrich/raw/github_com_richgel999_miniz.json) (enrichment confidence 0.75)

</details>
