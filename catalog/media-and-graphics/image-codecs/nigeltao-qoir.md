# QOIR

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Single-header C codec for a new lossless image format; encodes about 30x and decodes about 4.9x faster than libpng.

| | |
|---|---|
| **Beats** | libpng (Debian Bullseye build); also libwebp lossless |
| **Claimed result** | README: QOIR encodes 30x faster (0.033 vs 1.000) and decodes 4.9x faster (0.203 vs 1.000) than libpng. Raw table: QOIR_Lossless 168.90 MPixels/s encode and 276.45 decode vs PNG/libpng 5.49 and 56.18 and WebP_Lossless 2.49 and 89.94 (derived from page data: about 68x faster encode and 3.1x faster decode than libwebp lossless). Cost: CmpRatio 0.2525 vs libpng 0.2423 and libwebp 0.1651 (files about 4% larger than libpng, about 53% larger than lossless WebP, derived). |
| **Workload** | Single-threaded lossless encode and decode of the QOI benchmark image suite (RGB and RGBA photos, screenshots, icons) in megapixels per second plus compression ratio, against libpng, libwebp, libjxl, fpng, fpnge, QOI, ZPNG, stb and Wuffs. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-10210U @ 1.60GHz (author's desktop machine), single-threaded |
| **Compiler and flags** | gcc (Debian 10.2.1-6) 10.2.1; script/run_full_benchmarks.sh defaults CFLAGS to '-Wall -O3'; QOIR itself (src/qoir.h, included with QOIR_IMPLEMENTATION in test/benchmarks.c) is built with '-Wall -O3' only, without -march=native, while the comparison codec adapters are built with -march=native; libpng and libwebp are Debian Bullseye system packages (their build flags are not stated) |
| **Adoption** | 134 stars |
| **Last commit** | 2026-07-07 |
| **Links** | [repository](https://github.com/nigeltao/qoir) · [benchmark](https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt) |

## Verdict

Author-run and reproducible: on the qoiformat.org benchmark suite (December 2022 run, Intel i5-10210U, gcc 10.2.1, QOIR built -Wall -O3 without -march, single-threaded, 5 timed repetitions per image with allocation included), QOIR lossless encodes 168.90 and decodes 276.45 MPixels/s against Debian Bullseye's libpng through the simplified API at default zlib settings at 5.49 and 56.18 (30.8x and 4.9x) and libwebp lossless at 2.49 and 89.94, at ratio 0.2525 against 0.2423 and 0.1651. The benchmark harness does not compare decoded pixels, but a separate round_trip_tests.c checks pixel equality; the published run shows no encode or decode failures.

## Use it when

- Lossless 8-bit RGB/RGBA images that your own code both writes and reads (game or app asset pipelines, thumbnail and texture caches, screenshot or frame dumps) where encode and decode time matter more than PNG compatibility.
- Decode-heavy paths that still want a PNG-like ratio: 276 MPixels/s single-threaded decode at ratio 0.2525 against libpng's 56 MPixels/s at 0.2423 in the author's suite, and 582 against 77 MPixels/s on web screenshots.
- You need premultiplied-alpha output, decoding into an existing buffer, region (clip) decoding, or tile-parallel decoding of large images.
- You want no dependencies: one header with its own LZ4 and a permissive licence.

## Skip it when

- Files leave your system (browsers, editors, other tools): use PNG, WebP or JPEG XL. QOIR is marked 'experimental and subject to incompatible changes' and no release is listed on the repository page.
- Smallest files matter: lossless WebP (0.1651) and JPEG XL at effort 7 (0.1548) are much smaller than QOIR (0.2525), and libpng is about 4% smaller overall and smaller on the photo_tecnick, photo_wikipedia, textures_photo and pngimg subsets.
- Mostly photographic content: ZPNG (zstd plus PNG filters) makes 15-31% smaller files and decodes 1.3-1.5x faster on the photo subsets, and on textures_photo it beats QOIR on ratio, encode and decode at once (derived from page data).
- Images beyond 8-bit RGB/RGBA: no 16-bit, grayscale-only, palette or float/HDR support (the lossy mode only quantizes 8-bit channels).
- Parsing untrusted files in a security-sensitive service: the repository has no fuzz target, and a 2026 report (issue #4) showed the decoder's length checks were wrong for tiny files (it rejected valid ones).

## How it is fast

The image is cut into independent 64x64 tiles. Each tile is coded with QOI-style byte opcodes (colour-index hash, small RGB and luma deltas, runs), helped by a 64 KiB luma look-up table and SSE2 on x86-64, and the encoder keeps the smallest of four tile formats: raw literals, opcodes, or either one compressed with the bundled LZ4 block codec. There is no Huffman/deflate stage and no per-row filter search, which is where libpng's default zlib encode spends its time. Because tiles are independent, a caller can decode them on several threads into one pre-allocated buffer (the qoirview commit 913011d reports 2.56x on a 1165x859 image and 3.56x on 3600x2085, and a slowdown on a 160x120 one).

## Compared with alternatives

Choose QOIR over QOI when you want about 11% smaller files (0.2525 vs 0.2823) and 1.4x faster decode plus metadata, premultiplied alpha and tiling, and over fpng/fpnge when decode speed matters more than PNG output (fpng decodes 148 MPixels/s and only its own PNGs; fpnge has no decoder). Choose ZPNG instead for smaller files on photos if a zstd dependency is acceptable, and stay with PNG (libspng, the Wuffs decoder, fpnge) whenever other software must read the files.

## Integration

| | |
|---|---|
| **Form** | header-only (single-file C library: #define QOIR_IMPLEMENTATION in one translation unit) |
| **Dependencies** | none (bundled LZ4; QOIR_CONFIG__USE_OFFICIAL_LZ4_LIBRARY switches to liblz4) |
| **Minimum toolchain** | C99 compiler (uses stdbool.h/stdint.h); also compiles as C++; benchmarked with gcc 10.2.1; MSVC gets a memcpy-based little-endian peek/poke path |
| **Platforms** | any; SSE2 fast paths on x86-64 (gcc/clang/MSVC) can be turned off with QOIR_CONFIG__DISABLE_SIMD; published numbers are x86-64 only |
| **Thread safety** | Reentrant: no global state is written (the static look-up tables are only read), so separate calls can run on separate threads if each has its own qoir_decode_buffer/qoir_encode_buffer. The library spawns no threads; for parallel decoding the caller splits work by clip rectangles. |
| **Drop-in for the baseline** | no |

## Gotchas

- Decoding with default options yields RGBA_NONPREMUL even for RGB images; set qoir_decode_options.pixfmt or pass a pixbuf to get 3-byte RGB. (The benchmark used the default, so QOIR wrote 4 bytes per pixel where libpng wrote 3, which slightly handicaps QOIR.)
- The scratch structs are large (about 32 KiB for decode, about 37 KiB for encode); pass preallocated decbuf/encbuf to avoid a malloc per call (the benchmark reuses static ones), and do not put them on small thread stacks.
- Use a copy at or after commit ce7b583 (2026-07-07): earlier versions reject valid tiny images whose QPIX payload is under 8 bytes (issue #4, up to about 282 pixels).
- qoir_lz4_block_encode fails when dst_len is below the worst-case bound even if the output would fit; the default build also carries a 64 KiB luma table (QOIR_CONFIG__DISABLE_LARGE_LOOK_UP_TABLES removes it).

## Known shortcomings

- Tier A on its own full_benchmarks.txt rows 65, 70, 73 (168.90/276.45 MB/s vs libpng 5.49/56.18 and WebP 2.49/89.94; README 30x/4.9x confirmed). QOIR was built in test/benchmarks.c with -Wall -O3 only (adapters get -march=native). Ratio 0.2525 vs libpng 0.2423 and larger than libpng on 4 subsets. The 2026-07-07 fix ce7b583 only relaxes an over-strict length check. 134 stars.
- QOIR was built without -march and decoded RGB as 4-byte RGBA against libpng's 3-byte RGB (handicapping QOIR); the bench harness skips the pixel check (a separate round_trip_tests.c does check). ZPNG beats QOIR on all three columns for textures_photo. The format is still experimental with no release listed and no fuzz target; issue #4 (valid tiny files rejected) was fixed in ce7b583 without affecting the numbers.

## Caveats and trade-offs

QOIR is a different, experimental file format ('subject to incompatible changes'), not PNG. Compression trade-off: overall CmpRatio 0.2525 vs libpng 0.2423 (QOIR output about 4% larger, derived from page data; the README gives libpng 0.960 relative) and vs WebP lossless 0.1651; QOIR is larger than libpng on the photo_tecnick (0.5642 vs 0.5011), photo_wikipedia (0.6145 vs 0.5663), textures_photo (0.6052 vs 0.5977) and pngimg (0.1747 vs 0.1703) subsets and smaller on photo_kodak (0.5345 vs 0.5630) and screenshot_web (0.0710 vs 0.0757). The libpng baseline (PNG/libpng row, 'Debian Bullseye's libpng' per the file's Notes) is the distro package driven through the simplified API: adapter/png_libpng_adapter.c calls png_image_write_to_memory with image.flags = 0, so PNG_IMAGE_FLAG_FAST is not set and libpng runs at its defaults (zlib default compression level, all-filters heuristic), i.e. its default compression level, not a speed-tuned setting. Timing in test/benchmarks.c: 5 repetitions per image with gettimeofday, single-threaded, allocation included; the harness does not compare decoded pixels with the source (no round-trip check). The WebP_Lossless row uses libpng for images with a dimension above 16383 px, and the WebP decode adapter adds a full-image memcpy. Author's own benchmark (December 2022 run); one laptop-class CPU (i5-10210U) and gcc 10.2.1. The only later src/qoir.h change (2026-07-07, ce7b583, 'Fix qoir_chunk_payload_len vs src_len check') relaxes an over-strict length check that rejected some valid tiny files and does not affect the measured numbers. In the same table Wuffs' PNG decoder decodes at 140.79 MPixels/s (vs libpng 56.18), and the README says ZPNG is 'very competitive with and sometimes strictly better than QOIR'. AVIF was not measured (author hit Debian bug 976349), so there is no libavif comparison. An independent suite (WangXuan95/Image-Compression-Benchmark, CLIC2021, i7-12700H, Windows 10, Pillow PNG not libpng, times include process startup) lists QOIR at 23.696 compress and 19.752 decompress time vs PNG (optimize=False) 334.791 and 33.677 (lower is better, unit not stated).

Not PNG: a new experimental container (README warns of incompatible changes), so consumers need QOIR support. 24-bit RGB and 32-bit RGBA only. Larger files than libpng and much larger than WebP or JPEG XL. Tiles allow multi-threaded decoding (README links a commit claiming over 3x faster). Ships its own LZ4; single-file C library with no dependencies; optional trivial lossy mode (8 to 6 bits per channel).

## Maintenance

Mostly dormant (140 commits, 134 stars; one bug fix on 2026-07-07 after a gap since 2023-03-19, and one 2022 suggestions issue still open without a reply), but Apache-2.0 and a single dependency-free header that is easy to vendor; the file format itself is still labelled experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Author-run but fully reproducible: benchmark code is public (test/benchmarks.c, adapter/\*.c, script/run_full_benchmarks.sh), compiler gcc 10.2.1, flags -Wall -O3, and CPU i5-10210U are stated; the QOIR_Lossless, PNG/libpng and WebP_Lossless rows of doc/full_benchmarks.txt match the record and the README states 30x encode and 4.9x decode vs libpng.
- **Verifier notes:** Checked rows: images/ block lines 65 (PNG/libpng 0.2423, 5.49, 56.18), 70 (QOIR_Lossless 0.2525, 168.90, 276.45) and 73 (WebP_Lossless 0.1651, 2.49, 89.94); baselines are Debian Bullseye's libpng and libwebp, libpng at default compression settings. Metadata confirmed: Apache-2.0, 134 stars, not archived, last commit 2026-07-07 (active by rule, though the previous commit was 2023-03-19).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_libpng_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/webp_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/README.md>
  - <https://raw.githubusercontent.com/pnggroup/libpng/v1.6.37/pngwrite.c>
  - <https://raw.githubusercontent.com/pnggroup/libpng/v1.6.37/pngwutil.c>
  - <https://github.com/nigeltao/qoir>
  - <https://github.com/nigeltao/qoir/commits>
  - <https://github.com/nigeltao/qoir/commits/main/src/qoir.h>
  - <https://github.com/nigeltao/qoir/commits/main/doc/full_benchmarks.txt>
  - <https://github.com/nigeltao/qoir/commit/ce7b583beb123d897c4f20e436a2cb9d6d40e477>
  - <https://raw.githubusercontent.com/WangXuan95/Image-Compression-Benchmark/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/nigeltao/qoir>
  - <https://github.com/nigeltao/qoir/commits>
  - <https://github.com/nigeltao/qoir/issues?q=is%3Aissue>
  - <https://github.com/nigeltao/qoir/issues/2>
  - <https://github.com/nigeltao/qoir/issues/3>
  - <https://github.com/nigeltao/qoir/issues/4>
  - <https://github.com/nigeltao/qoir/tree/main/test>
  - <https://github.com/nigeltao/qoir/commit/913011d51da68c4f9c3e7c9d98aa4f9a04ac8d8e>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/README.md>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/qoir_file_format.md>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/src/qoir.h>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/round_trip_tests.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/util/check_round_trip.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_libpng_adapter.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/webp_adapter.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/nigeltao/qoir`) · [data/wave10/enrich/raw/github_com_nigeltao_qoir.json](../../../data/wave10/enrich/raw/github_com_nigeltao_qoir.json) (enrichment confidence 0.85)

</details>
