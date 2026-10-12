# fpng

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Unlicense` · 🟡 stale

> Single-file C++ PNG writer/reader for 24/32bpp: about 35x libpng's default encode speed, files about 29% larger.

| | |
|---|---|
| **Beats** | libpng |
| **Claimed result** | README text: about 23x faster compression and 2.5-3x faster decompression than libpng (decompression only on fpng-compressed PNGs). QOIR benchmark: fpng encode 192.16 MPixels/s vs libpng 5.49 (about 35x, derived from page data) and decode 148.19 vs 56.18 (about 2.6x, derived from page data); output files about 1.29x larger than libpng (CmpRatio 0.3115 vs 0.2423, derived). |
| **Workload** | Lossless 24/32bpp PNG encode, and decode of fpng-produced PNGs, single-threaded, on the QOI benchmark suite (QOIR harness) and on 303 GPU-texture test images (fpng README). |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-10210U @ 1.60GHz (author's desktop machine), single-threaded; fpng README: Xeon E5-2690 3.00 GHz |
| **Compiler and flags** | gcc (Debian 10.2.1-6) 10.2.1; script/run_full_benchmarks.sh defaults to CFLAGS '-Wall -O3' and compiles each codec adapter with -march=native; fpng.cpp is vendored in qoir third_party/fpng and #included into adapter/png_fpng_adapter.cpp, so fpng itself is built with -Wall -O3 -march=native (without the -fno-strict-aliasing that fpng's README says it was tested with); libpng is Debian Bullseye's system package (build flags not stated) driven through its simplified API at default settings; fpng's own README benchmarks used MSVC 2019 (flags not stated) |
| **Adoption** | 990 stars |
| **Last commit** | 2024-08-26 |
| **Links** | [repository](https://github.com/richgel999/fpng) · [benchmark](https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt) |

## Verdict

Nigel Tao's QOIR harness (gcc 10.2.1, -O3 -march=native, i5-10210U, single thread, QOI benchmark image set, Debian Bullseye libpng through its simplified API with default flags) measured fpng encoding at 192.16 vs 5.49 MPixels/s (about 35x). It measured decoding at 148.19 vs 56.18 MPixels/s (about 2.6x), with files 1.29x larger (CmpRatio 0.3115 vs 0.2423). Each codec decodes its own encoder's output. Wuffs, decoding the original PNGs, reached 140.79 MPixels/s, so fpng's decode lead over a modern general PNG decoder is about 5% (derived from page data).

## Use it when

- Writing many PNGs where encode time dominates: screenshots, frame dumps, texture-pipeline intermediates or debug images. QOIR's run measured 192 vs 5.5 MPixels/s against libpng's default settings, 21x to 45x per image category.
- Round-tripping your own files: fpng writes and fpng reads back at 148 MPixels/s (2.6x libpng decoding libpng's own files), with only the output buffer allocated during decode.
- Producing files other tools must open: the output is conformant PNG, which the author reports loads in libpng, Wuffs, lodepng, stb_image and pngcheck.
- Dropping two files into a C++ project with no zlib or libpng dependency, on x86-64 with SSE4.1/PCLMUL or with scalar fallbacks elsewhere.

## Skip it when

- File size matters. In QOIR's run fpng's files were 16% to 68% larger than libpng's, depending on category (icons worst), and fpnge was both 1.6x faster and 10% smaller overall in the same run.
- Decoding arbitrary or untrusted PNGs. The fast decoder rejects anything fpng did not write, and the author recommends Wuffs for decoding. Past reports include a heap-buffer-overflow read in fpng_get_info_internal (#26, fixed in the August 2024 bounds-check commit) and SIGILL crashes in fpng_adler32 on macOS CI runners (#24).
- Images wider or taller than 65,535 pixels. The encoder writes only the low 16 bits of width and height into IHDR but accepts sizes up to 2^24, so it returns success with a corrupt file (open issue #31).
- Grayscale, paletted, 16-bit, interlaced PNGs or PNGs with metadata: only 8-bit RGB/RGBA is supported, and issue #16 (asking for ICC/resolution tags and 8-bit support) is still open.
- Needing an active upstream: the last commit was 2024-08-26 and 17 issues are open.

## How it is fast

The encoder fixes every choice libpng searches over. The first row uses filter 0 and every later row uses filter 2 (Up), applied with SSE4.1 byte subtraction. A pixel-wise Deflate 'parser' emits literals in groups of 3 or 4 bytes and only RLE matches at distance 3 or 4 (whole pixels), all in one dynamic Huffman block. In the default one-pass mode the Huffman tables are precomputed (trained), so there is no frequency pass at all. CRC-32 uses PCLMULQDQ folding and Adler-32 uses SSE4.1, both chosen at run time after fpng_init(). The decoder relies on the same constraints: matches of distance 3 or 4 let it inflate straight into the output image with no window or temporary zlib buffer. A 12-bit lookup table packs two literals per entry when both codes fit, and it verifies neither the IDAT CRC-32 nor the zlib Adler-32.

## Compared with alternatives

Pick fpng over fpnge when you also want a fast reader for your own PNGs (fpnge is encoder-only) or need a scalar build. In QOIR's run fpnge encodes 1.6x faster into 10% smaller files, so pick fpnge for pure write speed. Pick QOI or QOIR instead when the files never leave your pipeline: QOIR decodes faster with smaller files than fpng. Pick libspng or Wuffs for reading arbitrary PNGs.

## Integration

| | |
|---|---|
| **Form** | source-drop (fpng.cpp + fpng.h; can be #included as a single translation unit) |
| **Dependencies** | none (C++ standard library std::vector; the test app adds lodepng, stb_image, qoi, wuffs) |
| **Minimum toolchain** | C++11 (the CMake file sets -std=c++11); tested by the author with MSVC 2019/2022, gcc 7.5 and clang 6/10 |
| **Platforms** | any little-endian CPU (big-endian code paths exist but are untested); SSE4.1+PCLMUL fast paths on x86/x64 only, and gcc/clang need -msse4.1 -mpclmul (or -DFPNG_NO_SSE=1) for the file to compile on x86; unaligned 32/64-bit loads are enabled by default only on x86 |
| **Thread safety** | Not documented. fpng_init() writes a global CPU-feature struct, so call it once before starting threads. After that, encode and decode keep their state in locals and the caller's std::vector; the only mutable global, g_huff_counts, exists only in FPNG_TRAIN_HUFFMAN_TABLES builds. |
| **Drop-in for the baseline** | partial: produces and (for its own files) reads standard PNG, but with its own two-function API instead of libpng's; you still need libpng, Wuffs or similar to read other PNGs |

## Gotchas

- Call fpng::fpng_init() first. Without it the SSE4.1/PCLMUL paths never activate; fpng_cpu_supports_sse41() asserts and returns false.
- Building the whole file with -msse4.1 -mpclmul lets the compiler emit SSE4.1 anywhere in it, so the run-time CPU check is not a full guard on older CPUs. The code also uses type-punned unaligned loads (READ_LE32/WRITE_LE64 via reinterpret_cast) and the README says it was tested only with -fno-strict-aliasing.
- num_chans=4 always writes a 32bpp file: there is no automatic detection of opaque images. The one-pass Huffman tables were trained on the author's corpus; FPNG_ENCODE_SLOWER builds per-image tables, giving about 6% smaller files at about 40% slower encode.
- The scratch buffer size (bpl + 1) \* h uses 32-bit arithmetic (int bpl, uint32_t h). The input check allows w\*h up to 2^32 pixels, so an image above 4 GiB of filtered data (e.g. 32768x32768 RGBA) wraps the allocation, and the filter loop would write past it. Found by code reading, not run.

## Known shortcomings

- Tier A on nigeltao/qoir full_benchmarks.txt rows 63/65 (192.16 vs 5.49 MB/s encode, 148.19 vs 56.18 decode; gcc 10.2.1, i5-10210U, Debian Bullseye libpng at default compression). Trade-off: files about 29% larger than libpng's, and the fast decode applies only to fpng's own output. The harness runs 5 repetitions with gettimeofday and never checks round-trip pixels. Vendored fpng.cpp equals upstream except the August 2024 bounds fix.
- Decode asymmetry: fpng skips the IDAT CRC-32 and the zlib Adler-32 while libpng checks both by default; the encode baseline is libpng with flags 0 (PNG_IMAGE_FLAG_FAST never tried); per category encode is 21-45x faster with files 1.16-1.68x larger. Encoder bugs outside the benchmark: IHDR writes 16-bit width and height but the encoder accepts up to 2^24, so a side above 65535 yields a corrupt PNG with a success return (open #31); the (bpl+1)\*h buffer size wraps in 32-bit arithmetic, a heap overflow above 4 GiB of filtered data (code reading, untested).

## Caveats and trade-offs

fpng's README tables compare against qoi, lodepng and stb_image only; its libpng claim (\~23x encode, 2.5-3x decode on fpng-compressed PNGs) is a prose line from MSVC 2019 runs on a Xeon E5-2690. The A tier rests on nigeltao/qoir's public harness (Nov 2022, one i5-10210U, gcc 10.2.1, Debian Bullseye libpng at the simplified API's default zlib settings; faster libpng settings such as a lower zlib level were not tried). Trade-off: fpng's PNGs are about 29% larger than libpng's in that run (CmpRatio 0.3115 vs 0.2423, derived from page data). Output is standard PNG that any decoder reads, but fpng's fast decoder only accepts fpng-written files, and the harness has each codec decode its own encoder's output, so the 2.6x decode figure compares fpng decoding fpng files with libpng decoding libpng files; Wuffs decodes the original PNGs at 140.79 MP/s in the same run. The harness never checks decoded pixels against the source. SIMD paths are x86-only (SSE4.1/PCLMUL). The author recommends Wuffs for reading arbitrary PNGs; an Aug 2024 commit fixed an off-by-four-bytes chunk bounds check on malformed input, and the issue tracker has heap-buffer-overflow and macOS segfault reports. Unlicense public-domain dedication: no patent grant.

Encoder writes standards-conformant PNG readable by any decoder, but the fast decoder only accepts PNGs written by fpng (returns FPNG_DECODE_NOT_FPNG otherwise). 24/32bpp only. SIMD (SSE4.1 plus PCLMUL for CRC and Adler) is x86 only. Output about 29% larger than libpng. Single source file, no dependencies. README recommends Wuffs for decoding untrusted PNGs.

## Maintenance

Stale since 2024-08-26 (last commit: a chunk bounds-check fix), Unlicense public-domain dedication and two files to vendor; the 16-bit IHDR dimension bug (#31) is still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** The images/ aggregate rows 'PNG/fpng' (0.3115 CmpRatio, 192.16 Enc, 148.19 Dec MPixels/s) and 'PNG/libpng' (0.2423, 5.49, 56.18) in nigeltao/qoir doc/full_benchmarks.txt match the record; the harness is public (script/run_full_benchmarks.sh, test/benchmarks.c, adapter/png_fpng_adapter.cpp, adapter/png_libpng_adapter.c) and the file states gcc 10.2.1, the script's -O3 -march=native flags and an i5-10210U, against Debian Bullseye's libpng package, so A holds.
- **Verifier notes:** Numbers match lines 63 and 65 (images/ aggregate) of full_benchmarks.txt; the file's Notes say PNG/libpng is Debian Bullseye's libpng, i.e. the distro package. qoir's vendored fpng.cpp is identical to upstream src/fpng.cpp except the Aug 2024 chunk bounds-check fix, so the numbers reflect current fpng code. Metadata confirmed: Unlicense, 990 stars, last commit 2024-08-26 (stale).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/README.md>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_libpng_adapter.c>
  - <https://github.com/nigeltao/qoir/commits/main/doc/full_benchmarks.txt>
  - <https://github.com/nigeltao/qoir/tree/main/third_party>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_fpng_adapter.cpp>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/third_party/fpng/fpng.cpp>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/third_party/fpng/fpng.h>
  - <https://raw.githubusercontent.com/richgel999/fpng/HEAD/README.md>
  - <https://raw.githubusercontent.com/richgel999/fpng/HEAD/src/fpng.cpp>
  - <https://raw.githubusercontent.com/richgel999/fpng/HEAD/src/fpng.h>
  - <https://github.com/richgel999/fpng>
  - <https://github.com/richgel999/fpng/commits>
  - <https://github.com/richgel999/fpng/issues?q=is%3Aissue>
- **Sources the enricher read:**
  - <https://github.com/richgel999/fpng>
  - <https://raw.githubusercontent.com/richgel999/fpng/HEAD/README.md>
  - <https://raw.githubusercontent.com/richgel999/fpng/HEAD/src/fpng.cpp>
  - <https://raw.githubusercontent.com/richgel999/fpng/HEAD/src/fpng.h>
  - <https://raw.githubusercontent.com/richgel999/fpng/HEAD/src/fpng_test.cpp>
  - <https://raw.githubusercontent.com/richgel999/fpng/HEAD/CMakeLists.txt>
  - <https://github.com/richgel999/fpng/issues?q=is%3Aissue>
  - <https://github.com/richgel999/fpng/issues/9>
  - <https://github.com/richgel999/fpng/issues/24>
  - <https://github.com/richgel999/fpng/issues/26>
  - <https://github.com/richgel999/fpng/issues/29>
  - <https://github.com/richgel999/fpng/issues/31>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/doc/full_benchmarks.txt>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/script/run_full_benchmarks.sh>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/test/benchmarks.c>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_fpng_adapter.cpp>
  - <https://raw.githubusercontent.com/nigeltao/qoir/HEAD/adapter/png_libpng_adapter.c>
  - <https://raw.githubusercontent.com/pnggroup/libpng/libpng16/pngwrite.c>
  - <https://raw.githubusercontent.com/pnggroup/libpng/libpng16/png.h>
  - <https://raw.githubusercontent.com/pnggroup/libpng/libpng16/pngrutil.c>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/richgel999/fpng`) · [data/wave10/enrich/raw/github_com_richgel999_fpng.json](../../../data/wave10/enrich/raw/github_com_richgel999_fpng.json) (enrichment confidence 0.85)

</details>
