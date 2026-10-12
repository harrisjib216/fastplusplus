# PNGenc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C (Arduino-style C++ class wrapper; can be built as C)` · `Apache-2.0 (src/ also vendors zlib 1.2.11 deflate.c, trees.c, crc32.c, adler32.c and zutil.c under the zlib license)` · 🟢 active

> Line-by-line, no-malloc PNG encoder for microcontrollers; a low-RAM libpng substitute with no speed claim or measurement.

| | |
|---|---|
| **Beats** | libpng |
| **Claimed result** | None stated. README section 'How fast is it?' only says the examples folder contains a sketch measuring the performance of encoding a 128x128 generated image; no figures and no baseline. |
| **Workload** | No comparison. The examples folder has a sketch that times encoding of a dynamically generated 128x128 image on the target board. |
| **Metric** | throughput |
| **Adoption** | 49 stars, 12 forks, 31 commits; NLnet NGI Zero Core funded (ImageCodes-Optimised project) |
| **Last commit** | 2025-11-17 |
| **Links** | [repository](https://github.com/bitbank2/PNGenc) |

## Verdict

No speed claim and no measurement exist: the README's 'How fast is it?' only points to examples/PNGenc_Test, which times one generated 128x128 8-bpp indexed image at compression level 3 with micros(), by default including the SD-card open and writes, and prints a single time with no baseline. linux/main.cpp prints only the output size. Because the compressor is stock zlib 1.2.11 deflate driven row by row, with libpng-style adaptive filtering, it should not beat libpng on throughput, and the reduced MCU window (4 KB, memLevel 5) probably costs compression ratio (not measured).

## Use it when

- Saving screenshots or sensor images to PNG on an ESP32, RP2040, Teensy or similar board with no heap and roughly 45K of RAM to spare.
- Streaming a frame buffer straight to an SD card line by line, including RGB565 display buffers via addRGB565Line.
- Small images (the default line buffer holds 2,560 bytes: 640 RGBA, 853 RGB or 2,560 8-bit pixels) where encoding speed is irrelevant next to SD-card write time.
- Projects that already use the author's PNGdec and want a matching, dependency-free encoder (the 2025 'simultaneous use with PNGdec' change).

## Skip it when

- Any desktop or server workload that needs speed: nothing shows it beating libpng, and fpnge, fpng or mtpng are measured to be many times faster.
- Lines wider than 2,560 bytes unless you raise PNG_MAX_BUFFERED_PIXELS: encodeBegin accepts widths up to 32,767, and nothing checks row size against the fixed line buffers (PNG_TOO_BIG is defined but never returned), so wide rows overflow into the live deflate output buffer and past the encoder struct.
- Grayscale or truecolor images that need a transparent color: setTransparentColor() returns success, but the tRNS chunk is only written inside the indexed-palette branch of PNGStartFile, so the transparency is silently dropped.
- 16-bit-per-channel images, gray+alpha, interlacing or metadata chunks: encodeBegin rejects 16 bpp, so gray+alpha cannot be encoded correctly, and only IHDR/PLTE/tRNS/IDAT/IEND are written.
- Code that needs strong memory safety: header and trailer writes are not bounds-checked against the caller's RAM output buffer, and the vendored zlib 1.2.11 deflate predates the CVE-2018-25032 fix (its trigger is mostly Z_FIXED, which PNGenc does not use).

## How it is fast

It is not built for speed: compression is a vendored copy of zlib 1.2.11 deflate (the same codec libpng normally calls) fed from a static pool, so throughput should track libpng at the same level. Each row gets a per-line adaptive filter chosen by minimum sum of absolute differences across None/Sub/Up/Average/Paeth (libpng's classic heuristic); 1/2/4-bpp rows are left unfiltered. On MCUs the deflate window and hash memory are cut eightfold (windowBits 12, memLevel 5) to fit RAM, and output is batched into a 2 KB buffer to reduce write() calls.

## Compared with alternatives

Pick PNGenc only when RAM and no-malloc constraints decide the choice. For any throughput goal, fpnge (about 57x libpng encode in the QOIR benchmark), fpng (about 23x per its README) or the multi-threaded GregorBudweiser pngenc are the encoders with measured wins over libpng.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none external; vendors zlib 1.2.11 deflate.c, trees.c, crc32.c, adler32.c and zutil.c (zlib license) in src/. Arduino.h is included unless __LINUX__, __MACH__ or __MCUXPRESSO is defined. |
| **Minimum toolchain** | C++ compiler for the class (GCC/Clang, since addRGB565Line uses __builtin_bswap16); linux/Makefile builds libpngenc.a at -O2. The README says it can be built as plain C, but the header's C prototypes name an undefined PNGIMAGE type and give PNG_addRGB565Line the wrong arity, so a C build likely needs header fixes. |
| **Platforms** | Any 32-bit MCU with about 45K free RAM (Arduino architectures=\*), plus Linux and macOS, where MEM_SHRINK 0 makes each PNGENC object about 270 KB. Windows needs -D__LINUX__ and a compiler with __builtin_bswap16. |
| **Thread safety** | not documented; state is per PNGENC instance, but the CRC table is a function-static lazily built on first use with no synchronization. |
| **Drop-in for the baseline** | no |

## Gotchas

- The bpp argument to encodeBegin is bits per pixel and is not checked against the pixel type: TRUECOLOR_ALPHA with bpp 8 is accepted and writes width-byte rows under an RGBA IHDR (a malformed PNG). examples/function_test Test 1 does exactly this and still passes, because it checks only the output size (127 bytes) and the magic bytes.
- Palettes are read in B,G,R order (PNGStartFile writes ucPalette[i\*3+2] as red); see closed issue #19.
- addRGB565Line issues Z_PARTIAL_FLUSH after every row, which costs compression ratio and time compared with addLine's Z_NO_FLUSH.
- The issue history is mostly about corrupt output (#2 IDAT CRC errors at 256x256, #14 missing data, #16 addLine corruption, #18 wrong IDAT length on about 25% of files with getLastError() returning 0). All are closed, but no regression test decodes the output.

## Known shortcomings

- Tier D: no numbers and no baseline; PNGenc_Test times one 128x128 image with micros() including SD-card writes and function_test checks sizes only. It vendors zlib 1.2.11's deflate, the same deflate libpng uses, so no speed edge is expected. Apache-2.0 plus the vendored zlib licence.
- Enricher (2026-10-04): no speed claim and no measurement exist; examples/PNGenc_Test times one generated 128x128 8-bpp indexed image at level 3 with micros(), including SD-card I/O by default, with no baseline, and linux/main.cpp prints only the output size. The compressor is stock zlib 1.2.11 deflate driven row by row with libpng-style adaptive filtering, so it should not beat libpng on throughput; the reduced MCU window (4 KB, memLevel 5) likely costs ratio. Bugs: the bpp argument is not checked against the pixel type (TRUECOLOR_ALPHA with bpp 8 writes malformed PNGs and the function test passes anyway); palettes read in B,G,R order (issue #19); addRGB565Line issues Z_PARTIAL_FLUSH after every row; issue history is mostly corrupt output (#2, #14, #16, #18), all closed without a decoding regression test. Tier D stands.

## Caveats and trade-offs

No speed claim against libpng, lodepng, stb_image_write or any other encoder in the README or examples. examples/PNGenc_Test/PNGenc_Test.ino times one 128x128 8-bpp indexed image with micros() and, by default (WRITE_TO_SD), includes SD-card writes. examples/function_test/function_test.ino declares timing variables but only checks output sizes and the PNG magic bytes. linux/main.cpp prints no timings (Makefile: -O2). Compression is a vendored copy of zlib 1.2.11 deflate, the same deflate libpng normally uses, so it has no reason to be faster than libpng on desktop CPUs. It targets low RAM (runs on MCUs with at least 45K free RAM, no malloc) rather than speed. Tier D, low notability (49 stars); kept because the seed list asked for it.

Embedded-oriented: needs 45K of free RAM, no malloc/free, encodes line by line, up to 8 bits per channel, own zlib compressor with effort level 1-9. Output size versus libpng is not documented.

## Maintenance

Maintained at low intensity (last commit 2025-11-17, v1.4.0, NLnet NGI Zero Core funded, 18 issues all closed); Apache-2.0 plus zlib-licensed vendored files, small enough to vendor, but treat it as a convenience encoder for small embedded images and validate its output.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** No benchmark page exists. The README 'How fast is it?' section only points to examples/PNGenc_Test, which times one 128x128 generated image with micros() (writing to an SD card by default) and compares nothing. linux/main.cpp has no timing code, and function_test.ino only checks output sizes.
- **Verifier notes:** Record accurate apart from the license (vendored zlib files) and a small caveat error: function_test.ino does not print timings. The vendored zlib 1.2.11 deflate means no throughput edge over libpng is expected. Last commit 2025-11-17 is confirmed, so it is still active.
- **Fields the verifier corrected:** `license`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** none
- **Pages the verifier opened:**
  - <https://github.com/bitbank2/PNGenc>
  - <https://github.com/bitbank2/PNGenc/commits>
  - <https://github.com/bitbank2/PNGenc/tree/master/examples>
  - <https://github.com/bitbank2/PNGenc/tree/master/src>
  - <https://github.com/bitbank2/PNGenc/tree/master/linux>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/examples/PNGenc_Test/PNGenc_Test.ino>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/examples/function_test/function_test.ino>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/linux/main.cpp>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/linux/Makefile>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/src/deflate.c>
- **Sources the enricher read:**
  - <https://github.com/bitbank2/PNGenc/commits>
  - <https://github.com/bitbank2/PNGenc/wiki>
  - <https://github.com/bitbank2/PNGenc/issues?q=is%3Aissue>
  - <https://github.com/bitbank2/PNGenc/issues/2>
  - <https://github.com/bitbank2/PNGenc/issues/16>
  - <https://github.com/bitbank2/PNGenc/issues/18>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/library.properties>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/src/PNGenc.h>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/src/PNGenc.cpp>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/src/png.inl>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/src/deflate.c>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/src/deflate.h>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/linux/main.cpp>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/linux/Makefile>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/examples/PNGenc_Test/PNGenc_Test.ino>
  - <https://raw.githubusercontent.com/bitbank2/PNGenc/HEAD/examples/function_test/function_test.ino>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/bitbank2/pngenc`) · [data/wave10/enrich/raw/github_com_bitbank2_pngenc.json](../../../data/wave10/enrich/raw/github_com_bitbank2_pngenc.json) (enrichment confidence 0.8)

</details>
