# Zpng

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Zstd-backed lossless RGB/RGBA image format that encodes about 23x and decodes 4.6x faster than libpng, with smaller files.

| | |
|---|---|
| **Beats** | libpng |
| **Claimed result** | QOIR benchmark: ZPNG_Lossless encode 126.21 MPixels/s and decode 256.32 vs libpng 5.49 and 56.18 (about 23x and 4.6x, derived from page data) with smaller output overall (CmpRatio 0.2182 vs 0.2423, about 10% smaller, derived; larger on icon_512: 0.0534 vs 0.0499). README: less than 6% of the compressor's time and 66% of the size on one 13.9 MB photo, measured against stb_image_write's stbi_write_png with the disk write included, not libpng. WangXuan95 CLIC2021 shootout (modified build: PNM I/O, level switch, g++ -static -O3): ZPNG 25.909 s compress and 24.083 s decompress, 1,755,786,378 bytes vs Pillow PNG (optimize=False) 334.791 s, 33.677 s, 2,003,016,524 bytes. |
| **Workload** | Lossless encode and decode of the full QOI benchmark suite (qoiformat.org tarball: icons, photos, textures, screenshots, pngimg) in nigeltao/qoir's single-threaded harness, megapixels per second plus compression ratio. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-10210U @ 1.60GHz (author's desktop machine), single-threaded; shootout: Intel Core i7 12700H, Windows 10 |
| **Compiler and flags** | gcc (Debian 10.2.1-6) 10.2.1; script/run_full_benchmarks.sh defaults CFLAGS to '-Wall -O3' and compiles adapter/zpng_adapter.cpp (which includes the vendored third_party/zpng/zpng.cpp) with -march=native -Wall -O3; zstd, libpng and libwebp are Debian Bullseye system packages (their build flags are not stated); Zpng calls zstd at level 1 |
| **Adoption** | 312 stars |
| **Last commit** | 2018-06-17 |
| **Links** | [repository](https://github.com/catid/Zpng) · [benchmark](https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt) |

## Verdict

Nigel Tao's QOIR harness ran single-threaded on an Intel i5-10210U with gcc 10.2.1 (-O3 -march=native for the adapter), 5 repetitions per image, over the whole QOI benchmark suite. Zpng (the vendored zpng.cpp with the system libzstd at level 1) encoded 126.21 MPixels/s and decoded 256.32 MPixels/s, against 5.49 and 56.18 for Debian Bullseye's libpng at default settings (about 23x and 4.6x, derived from page data), at CmpRatio 0.2182 vs 0.2423. The WangXuan95 CLIC2021 shootout used a lightly modified catid build (PNM output and a level switch; g++ -static -O3, vendored zstd 1.3.4) against Pillow's PNG, with process startup included in the times.

## Use it when

- Caching, storing or moving 8-bit RGB or RGBA frames between programs you control (capture tools, asset caches, dataset shards), where a private format is acceptable: 126 MPixels/s encode and 256 MPixels/s decode on one i5-10210U thread across the QOI suite.
- Photographs and photo textures, where it gives the smallest files among the fast codecs in the QOIR table: photo_kodak CmpRatio 0.4776 (libpng 0.5630, QOIR 0.5345, QOI 0.5829) and textures_photo 0.4156 (libpng 0.5977, QOIR 0.6052).
- Read-heavy pipelines: decoding (256 MPixels/s) runs about twice as fast as encoding and beats QOI (193.5) and libjxl's fast-lossless path (33.2 decode) in the same harness.
- Projects that already link zstd and want a lossless image codec of roughly 600 lines under BSD-3-Clause that they can vendor and adapt.

## Skip it when

- Interchange or long-term archives: .zpng is not PNG, no viewer or browser reads it, the header has no version field and is written in host byte order.
- Untrusted files: the decoder trusts the header and never checks that zstd filled the output (see gotchas). Treat it as unsafe on hostile input unless you add those checks.
- Images wider or taller than 65535 px: width and height are stored as uint16_t, and ZPNG_Compress truncates them with no error. The QOIR adapter adds the missing guard itself.
- 16-bit data: deltas are taken per byte, not per 16-bit sample, and the colour transform runs only on 8-bit RGB/RGBA. ZPNG_Decompress also reports StrideBytes as width x channels, half the real stride. The CLI loads with stbi_load, which converts 16-bit PNGs to 8-bit (issue #6, closed with no fix in the code).
- Flat graphics and icons, or when you need the smallest output: on QOIR's icon_512 set Zpng is larger than libpng (CmpRatio 0.0534 vs 0.0499), and on textures_pk it is larger than QOIR (0.5384 vs 0.4929). WebP lossless (0.1651) and slower JPEG XL settings are much smaller overall. Encoding small icons is also slower (icon_64: 80.8 MPixels/s).

## How it is fast

Filtering is one pass per row: each byte is replaced by its difference from the same channel of the pixel to the left (PNG's Sub filter only, with no Up or Paeth filters and no per-row filter search). For 8-bit RGB and RGBA it then applies the reversible GB-RG colour transform from BCIF (Y=B, U=G-B, V=G-R on the residuals) and writes Y, U, V and alpha as separate planes. In the author's README experiments the plane split made output about 1.8% smaller and compression faster than interleaved data. The planar residual buffer then goes through one ZSTD_compress call at level 1 (zstd's fast match finder with Huffman and FSE entropy coding). libpng at its defaults instead tries every filter on each row and runs zlib deflate at the default level. Decoding is ZSTD_decompress followed by the inverse transform. There are no SIMD intrinsics; the loops rely on compiler auto-vectorization (its CMake Release flags are -O3 -march=native).

## Compared with alternatives

Pick Zpng over QOI or QOIR when file size matters more than the last bit of speed: on the QOI suite its output is about 14% smaller than QOIR's (0.2182 vs 0.2525) and 23% smaller than QOI's (0.2823), at about 75% of QOIR's encode speed (126 vs 169 MPixels/s) and similar decode speed (256 vs 276). Pick fpng or fpnge when you need real PNG files. libjxl fast_lossless matches Zpng's size (0.2171) in a standard format but decodes about 7.7x slower (33.16 vs 256.32 MPixels/s).

## Integration

| | |
|---|---|
| **Form** | source-drop (zpng.cpp + zpng.h), or the CMake zpnglib static library, which also compiles the vendored zstd |
| **Dependencies** | zstd (a copy of zstd 1.3.4 is vendored in zstd/; the QOIR harness links the system libzstd instead, so newer versions work); the CLI and test app also use stb_image and stb_image_write |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11), CMake 3.5; the API is extern "C", but zpng.cpp uses templates and must be compiled as C++ |
| **Platforms** | Any (portable scalar C++, no intrinsics); the CMake Release flags hard-code -O3 -march=native on non-MSVC compilers, which ties binaries to the build machine's CPU; files are not portable between little- and big-endian hosts because the header is written as a raw struct |
| **Thread safety** | Not documented. From reading the code there is no global state and every call allocates its own buffers and zstd context, so concurrent calls on separate buffers look safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Possible memory-safety bug on crafted input (found by reading the code; not run): ZPNG_Decompress computes byteCount = width x height x bytesPerPixel in 32-bit unsigned arithmetic with no overflow check. A header of 32768 x 32768 RGBA wraps the product to 0, and with an empty zstd frame UnpackAndUnfilter then reads and writes about 4 GiB past two zero-byte allocations. The decoder also ignores how many bytes ZSTD_decompress actually produced, and level-1 frames carry no checksum, so truncated or corrupted files decode silently to zero-filled pixels.
- ZPNG_Compress ignores the input StrideBytes and assumes tightly packed rows; padded or sub-image buffers come out scrambled with no error.
- Memory per call is about 2-3x the image: compression allocates a filtered copy plus a ZSTD_compressBound output buffer, and decompression allocates the packed buffer plus the output. Results come back in malloc'd buffers that you must release with ZPNG_Free.
- The README's 'less than 6% of the time of a PNG compressor and 66% of the size' compares against stb_image_write's stbi_write_png, not libpng (apps/zpng_app.cpp times the stbi_write_png call, which also writes the 41.9 MB file to disk), against an in-memory Zpng compress of one JPEG-derived photo. The independent QOIR numbers are the ones to rely on.

## Known shortcomings

- Tier A on qoir full_benchmarks.txt row 76 (126.21/256.32 MB/s, ratio 0.2182: smaller than libpng on all subsets, WebP 0.1651 smaller still), with zstd level 1 from the Debian libzstd package. Last commit 2018-06-17 (unmaintained); the vendored zpng.cpp equals catid HEAD plus a noFilter flag. The benchmark covers the full QOI suite, not photographic images only.
- Security bugs from code reading (not run): a 32-bit byteCount overflow lets a crafted 32768x32768 RGBA header plus an empty zstd frame cause heap out-of-bounds reads and writes, and the decoder ignores the ZSTD_decompress output size so truncated files decode silently; width and height are truncated to uint16, the input StrideBytes is ignored and 16-bit StrideBytes is wrong. The README '6% time, 66% size' claim is against stb_image_write with the disk write included, not libpng; the QOIR run is not smaller than libpng on icon_512 (0.0534 vs 0.0499) and links Debian's system libzstd rather than the vendored zstd 1.3.4; the WangXuan95 shootout used a modified build (retier-05 corrects the record).

## Caveats and trade-offs

Zpng is its own format (custom header plus zstd), not PNG-compatible. Compression trade-off: overall CmpRatio 0.2182 vs libpng 0.2423 (smaller), and smaller than libpng on every subset row checked (for example photo_kodak 0.4776 vs 0.5630, screenshot_web 0.0584 vs 0.0757), but WebP lossless is smaller still (0.1651). The libpng baseline (PNG/libpng row, 'Debian Bullseye's libpng' per the file's Notes) is the distro package driven through the simplified API: adapter/png_libpng_adapter.c calls png_image_write_to_memory with image.flags = 0, so PNG_IMAGE_FLAG_FAST is not set and libpng runs at its defaults (zlib default compression level, all-filters heuristic), i.e. its default compression level, not a speed-tuned setting. Timing in test/benchmarks.c: 5 repetitions per image with gettimeofday, single-threaded, allocation included; the harness does not compare decoded pixels with the source (no round-trip check). The WebP_Lossless row uses libpng for images with a dimension above 16383 px, and the WebP decode adapter adds a full-image memcpy. The measured code is nigeltao/qoir's vendored third_party/zpng/zpng.cpp, identical to catid/Zpng HEAD except for an added noFilter flag (and a header bit) used only by the ZPNG_NofilLsl variant; the adapter copies the output buffer once more in both encode and decode, which slightly penalizes ZPNG. Zpng depends on the zstd library. The Zpng README itself claims 'less than 6% of the time of a PNG compressor and a file that is 66% of the size' (248.737 ms vs 4339.82 ms on one JPEG-derived image), without naming the PNG library. Image-Compression-Benchmark (CLIC2021, i7-12700H, Windows 10, Pillow PNG not libpng, times include process startup) lists ZPNG at 25.909 compress and 24.083 decompress time vs PNG (optimize=False) 334.791 and 33.677 (lower is better, unit not stated). [retier] Zpng is its own format (custom header plus zstd), not PNG-compatible. Smaller than libpng overall in the QOIR run (0.2182 vs 0.2423) and on most subsets (photo_kodak 0.4776 vs 0.5630, screenshot_web 0.0584 vs 0.0757) but not on icon_512 (0.0534 vs 0.0499); WebP lossless is smaller still (0.1651). The libpng baseline is Debian Bullseye's package through the simplified API with image.flags = 0 (default compression level and filter heuristic). The QOIR binary links Debian's system libzstd, not the vendored zstd 1.3.4. Decoder safety from code reading (not run): a 32-bit byteCount overflow lets a crafted 32768x32768 RGBA header plus an empty zstd frame cause heap out-of-bounds reads and writes, and the ZSTD_decompress output size is ignored so truncated files decode silently; width and height are truncated to uint16, the input StrideBytes is ignored, and 16-bit StrideBytes is wrong.

Custom non-PNG format that needs Zstd (bundled in the repo). C API plus command-line tool, about 500 lines. Works best on photographic images. Author calls it experimental and does not expect others to use it.

## Maintenance

Abandoned since 2018-06-17 (one PR, #4 from 2018, now closed; issue #5 on integer-type portability is still open), but BSD-3-Clause and about 600 lines, so it is easy to vendor; add header and decompressed-size checks before you feed it files you did not write.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent third-party run (nigeltao/qoir) with public benchmark code (test/benchmarks.c, adapter/zpng_adapter.cpp, script/run_full_benchmarks.sh), compiler gcc 10.2.1, flags -Wall -O3 -march=native for the adapter, and CPU i5-10210U stated; the ZPNG_Lossless row (126.21 / 256.32 MPixels/s, CmpRatio 0.2182) matches the record.
- **Verifier notes:** Checked rows: images/ block lines 65 (PNG/libpng 0.2423, 5.49, 56.18), 73 (WebP_Lossless 0.1651, 2.49, 89.94) and 76 (ZPNG_Lossless 0.2182, 126.21, 256.32); baseline is Debian Bullseye's libpng at default compression settings. Workload corrected: the cited row covers the whole QOI suite, not only photographic images. Metadata confirmed: BSD-3-Clause, 312 stars, not archived, last commit 2018-06-17 (abandoned).
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_libpng_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/webp_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/README.md>
  - <https://raw.githubusercontent.com/pnggroup/libpng/v1.6.37/pngwrite.c>
  - <https://raw.githubusercontent.com/pnggroup/libpng/v1.6.37/pngwutil.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/zpng_adapter.cpp>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/third_party/zpng/zpng.cpp>
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/zpng.cpp>
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/README.md>
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/LICENSE>
  - <https://github.com/catid/Zpng>
  - <https://github.com/catid/Zpng/commits>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/README.md>
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/zpng.cpp>
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/zpng.h>
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/apps/zpng_test.cpp>
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/apps/zpng_app.cpp>
  - <https://raw.githubusercontent.com/catid/Zpng/HEAD/zstd/zstd.h>
  - <https://github.com/catid/Zpng/issues?q=is%3Aissue>
  - <https://github.com/catid/Zpng/pulls?q=is%3Apr>
  - <https://github.com/catid/Zpng/issues/3>
  - <https://github.com/catid/Zpng/issues/5>
  - <https://github.com/catid/Zpng/issues/6>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/zpng_adapter.cpp>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/third_party/zpng/zpng.cpp>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/third_party/zpng/zpng.h>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
  - <https://github.com/WangXuan95/Image-Compression-Benchmark/tree/main/codec/ZPNG>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/codec/ZPNG/source.txt>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/codec/ZPNG/ZPNG_source_code.zip>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/catid/zpng`) · [data/wave10/enrich/raw/github_com_catid_zpng.json](../../../data/wave10/enrich/raw/github_com_catid_zpng.json) (enrichment confidence 0.85)

</details>
