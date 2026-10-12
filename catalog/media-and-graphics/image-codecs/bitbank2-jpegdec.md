# JPEGDEC (bitbank2)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Baseline-JPEG decoder for microcontrollers and PCs; decoded 1.7x faster than TJpgDec and 3.4x faster than picojpeg on an ESP32-S3.

| | |
|---|---|
| **Beats** | TJpgDec (via Bodmer/TJpg_Decoder) and picojpeg (via Bodmer/JPEGDecoder); libjpeg-turbo and stb_image not compared |
| **Claimed result** | Decode-only ms from atomic14's README table (one 280x240 JPEG, ESP32-S3): Bodmer/JPEGDecoder (picojpeg) 108, Bodmer/TJpg_Decoder (TJpgDec) 55, bitbank2/JPEGDEC 32 (2023 run, struck through), JPEGDEC 'New!' SIMD version 23 (added 2024-04-07; other rows not re-run), ESP32_JPEG 20. Derived from page data: JPEGDEC is 1.7x faster than TJpgDec in the same session (55/32) and 2.4x with the 2024 number (55/23, cross-session); 3.4x and 4.7x faster than picojpeg (108/32, 108/23). Espressif's ESP32_JPEG is faster still (20 ms). Decode plus draw: TJpg_Decoder 64, JPEGDEC 38 (old) or 29 (new), ESP32_JPEG 37 (JPEGDecoder's 118 is hard-coded as decode + 10 in main.cpp). The JPEGDEC README chart (perf.jpg) gives only its own per-MCU timings (tulips.h 640x480: ESP32-S3 @240MHz 91,516 us full decode, Cortex-M7 @600MHz 29,592 us, Apple M1 8,014 us full and 992 us at 1/8 size) and unquantified claims ('perform better than anything else available', 'cropping function that's faster than JPEGTRAN'). |
| **Workload** | Decode of one 280x240 baseline JPEG held in memory on an ESP32-S3 (with PSRAM), timed with millis() around the library's decode call, with and without drawing to a TFT; JPEGDEC, Bodmer/TJpg_Decoder, Bodmer/JPEGDecoder and Espressif ESP32_JPEG compared. |
| **Metric** | latency |
| **Hardware** | ESP32-S3 with PSRAM (README); the 2023 rows match the initial esp32-s3-devkitc-1 env with -DBOARD_HAS_PSRAM; the 2024 'New!' JPEGDEC row was added when that env had PSRAM commented out and a um_tinys3 (TinyS3) env existed, so its board is not stated; clock speed not stated. |
| **Compiler and flags** | PlatformIO platform espressif32 (unpinned), Arduino framework, build_flags -Ofast (applied to project and library sources); GCC version and library versions (bitbank2/JPEGDEC, bodmer/JPEGDecoder, Bodmer/TJpg_Decoder and ESP32_JPEG from git HEAD) not pinned. |
| **Adoption** | 631 stars |
| **Last commit** | 2026-03-13 |
| **Links** | [repository](https://github.com/bitbank2/JPEGDEC) · [benchmark](https://github.com/atomic14/esp32-jpeg-perf-tests) |

## Verdict

atomic14's independent ESP32-S3 harness (PlatformIO espressif32 unpinned, Arduino framework, -Ofast) decoded one 280x240 baseline 4:2:0 JPEG (23,362 bytes, restart interval 18) from RAM to RGB565 once per library per pass, timed with millis(): JPEGDEC 32 ms against 55 ms for Bodmer's TJpg_Decoder (TJpgDec R0.03 at JD_FASTDECODE 1) and 108 ms for Bodmer's JPEGDecoder (picojpeg), 1.7x and 3.4x. A later SIMD build of JPEGDEC was recorded at 23 ms without re-running the other rows, and Espressif's ESP32_JPEG was fastest at 20 ms; the README's own chart gives only JPEGDEC's per-MCU timings.

## Use it when

- Showing baseline JPEGs on an MCU-driven LCD (ESP32, ESP32-S3, Cortex-M4/M7, Teensy and similar) where about 18-20 KB of RAM for the decoder is affordable and lower latency than TJpgDec or picojpeg matters.
- MJPEG or camera-frame playback on an ESP32-S3 at small resolutions: atomic14 measured about 23-32 ms for a 280x240 frame, and pixels can be streamed to SPI DMA while the next MCU row decodes.
- Images larger than the screen: built-in 1/2, 1/4, 1/8 scaling, cropping and Exif-thumbnail extraction avoid decoding pixels you will throw away.
- E-paper or monochrome displays: the 1/2/4-bpp dithered output path saves a separate dithering pass.
- Small dependency-free baseline decoding on a host (Linux, macOS, Windows x64) when one translation unit with SSE2/NEON is enough and decode speed versus libjpeg-turbo is not the deciding factor (no such comparison has been published).

## Skip it when

- Progressive JPEGs at full size: only a 1/8-scale DC thumbnail is produced. Use libjpeg-turbo on hosts, or lowzag for scaled progressive decoding on an ESP32.
- Untrusted input on MCUs without memory protection: an out-of-bounds write in the progressive decoder is open (issue #119) and there is no fuzzing or hardening record in the repository.
- Desktop throughput work: there is no measurement against libjpeg-turbo, and arithmetic coding, 12-bit and lossless JPEG are not listed as supported.
- RAM-starved MCUs: each JPEGDEC object embeds about 17.9 KB of state, while TJpgDec runs in a 3.1-3.5 KB workspace.
- ESP32-S3 boards with PSRAM where the whole frame can be buffered: Espressif's ESP32_JPEG decoded the same image faster (20 ms vs 23 ms), at the cost of a full output buffer and a precompiled binary library.

## How it is fast

Table-driven Huffman decoding: DC codes go through a 6-bit short table plus a long table for codes starting with five 1 bits (short codes have the magnitude bits folded into the entry), AC codes through a 10-bit short table plus a long table for codes starting with six 1 bits, read from a 32- or 64-bit bit buffer refilled with byte-swapped word loads; FF00 byte-stuffing is removed in bulk ahead of decode (SSE2/NEON in JPEGFilter). The integer AAN-style IDCT tracks which columns and rows hold non-zero coefficients and skips the empty ones, DC-only blocks are filled directly, 1/4 and 1/8 scaling use 2x2 and DC-only transforms, and MCUs outside a crop rectangle decode only their DC term. SIMD IDCT and colour conversion exist for x86-64 SSE2 and AArch64 NEON; on the ESP32-S3, hand-written assembly (s3_simd_420.S, s3_simd_444.S, s3_simd_dequant.S) does YCbCr-to-RGB565 conversion and dequantisation with the S3's 128-bit vector instructions (an S3 IDCT file is still marked _FUTURE).

## Compared with alternatives

Pick JPEGDEC for baseline JPEGs on a microcontroller streaming straight to a display with 20-32 KB of RAM to spare; pick lowzag when the files are progressive and must be shown scaled on an ESP32, and libjpeg-turbo (or jpeg-nitro for multi-threaded host decoding) on desktops, where JPEGDEC has no published comparison.

## Integration

| | |
|---|---|
| **Form** | source-drop / Arduino library (src/JPEGDEC.cpp includes src/jpeg.inl, plus three ESP32-S3 .S files); ESP-IDF component; linux/makefile builds a static library |
| **Dependencies** | none for the decoder core; Arduino.h on Arduino builds; library.properties lists bb_spi_lcd (for the JPEGDisplay helper); the ESP-IDF CMakeLists.txt REQUIRES esp-dsp and arduino-esp32; the S3 SIMD path is compiled only when esp-dsp's dsps_fft2r_platform.h is found |
| **Minimum toolchain** | C++ class without exceptions or STL; uses GCC/Clang builtins (__builtin_bswap16/32/64), MSVC x64 supported since February 2025; language standard not documented |
| **Platforms** | any 32- or 64-bit MCU or host; SIMD on x86-64 (SSE2 intrinsics only), AArch64 NEON and ESP32-S3; unaligned-load fast paths on ESP32, Cortex-M4/M7, Teensy, x86-64 and AArch64; byte-wise fallbacks elsewhere |
| **Thread safety** | not documented; from the code, all decode state (Huffman tables, quantisation tables, 2 KB file buffer, 2048-pixel buffer) lives inside each JPEGDEC object and the lookup tables are const, so separate objects should be independent, but one object must not be shared |
| **Drop-in for the baseline** | false - TJpgDec (and Bodmer's TJpg_Decoder wrapper's drawJpg plus tft_output(x, y, w, h, bitmap) callback) and picojpeg have different APIs; porting a draw callback to JPEGDEC's JPEGDRAW struct (x, y, iWidth, iHeight, pPixels, pUser) is a small change |

## Gotchas

- Open memory-safety bug (issue #119, April 2026, no maintainer reply): JPEGDecodeMCU_P computes &sMCUs[iMCU & 0xffffff], so when the decode loop passes MCU_SKIP (-8), as it does for the chroma blocks of a colour progressive JPEG decoded to 8-bit gray or dithered output (and, by the same code, for MCUs outside a crop area), the pointer lands about 32 MB past the 384-entry array and the DC store still happens; confirmed in the current jpeg.inl. The baseline path (JPEGDecodeMCU) checks iMCU &lt; 0 and is not affected.
- Harness flaw behind the 1.7x: Bodmer's TJpg_Decoder ships tjpgdcnf.h with JD_FASTDECODE 1 and JD_TBLCLIP 0, not TJpgDec's table-driven Huffman level 2 or table clipping. Espressif's esp_jpeg table (ESP32-S3, 320x180 image, RGB888) has TJpgDec at 62 ms in that configuration versus 46 ms with JD_TBLCLIP 1 and JD_FASTDECODE 2 (1.35x, derived from page data), so against a fully configured TJpgDec the lead would be nearer 1.3x (estimate, different image) at the old 32 ms figure. TJpgDec's decode-only callback also memcpys every block while JPEGDEC's returns at once, and its draw callback advances the DMA buffer index before pushing, so the decode+draw column displays the previous block (timing comparable, output wrong).
- Each JPEGDEC object holds the whole JPEGIMAGE struct (about 17.9 KB), so keep it global, static or heap-allocated rather than on a small RTOS task stack; library.properties says 32K+ RAM MCUs, the README says 20K.
- Building outside Arduino needs -D__LINUX__ (or __MACH__, ESP_PLATFORM, _WIN64, __MCUXPRESSO), otherwise the header pulls in Arduino.h; linux/makefile installs with sudo cp into /usr/local. Other open reports: baseline AC tables with codes over 10 bits that do not start with six 1 bits are rejected (the slow-table fallback is commented out), images that stopped loading after 1.6.1 on an STM32H743 (#123), and red/blue swapped for some images on the Apple M1 NEON path (#120).

## Known shortcomings

- Independent atomic14 ESP32-S3 table (32 and 23 ms vs TJpgDec 55 ms and picojpeg 108 ms) is one image and one run per library with versions unpinned: main.cpp hard-codes the JPEGDecoder decode-plus-draw figure as decode + 10 so only the decode column was measured, TJpgDec has a callback memcpy asymmetry, the 2024 23 ms row comes from a different session and possibly a different board, and ESP32_JPEG is faster (20 ms).
- Enricher: open out-of-bounds write (issue #119, confirmed at HEAD jpeg.inl:1827/1887): JPEGDecodeMCU_P indexes &sMCUs[iMCU & 0xffffff], so MCU_SKIP (-8) lands about 32 MB past the array and the DC store still runs; it triggers on colour progressive JPEGs decoded to grey or dithered output and on cropped progressive decodes (the measured baseline path is unaffected). Harness: the Bodmer TJpg_Decoder baseline ships tjpgdcnf.h with JD_FASTDECODE 1 and JD_TBLCLIP 0, not TJpgDec's fastest setup, and Espressif's esp_jpeg table shows 62 vs 46 ms (1.35x derived), so the lead over a tuned TJpgDec is nearer 1.3x; the TJpg draw callback pushes the previous block. Open #123 and #120 (NEON red/blue swap); AC codes over 10 bits rejected.

## Caveats and trade-offs

Evidence is an independent but small demo: one 280x240 image, one timed decode per library per loop pass (millis() resolution, no repeats or statistics), toolchain and library versions unpinned, clock not stated. Harness asymmetries: TJpgDec's output callback memcpys every block into a DMA buffer even in the decode-only pass while JPEGDEC's callback returns at once when no TFT is passed (a small bias toward JPEGDEC); main.cpp hard-codes the first library's (Bodmer/JPEGDecoder) decode+draw time as decode + 10 ms, so that column is not measured (the decode-only column behind the claims is measured). The 23 ms 'New!' row was added in 2024 without re-running the other libraries, at a time when the devkitc env had PSRAM disabled (which compiles out the ESP32_JPEG test), so it may come from a different board or config than the 2023 rows. Espressif's ESP32_JPEG was faster in decode-only (20 vs 23 ms). No published comparison against desktop libjpeg-turbo or stb_image was found, and the lead's '1/8-scale progressive in about 18 KB' claim has no numbers. The README chart (perf.jpg) shows only JPEGDEC across boards. Espressif's esp_jpeg README speed table (GitHub copy) covers TJpgDec configurations on a different image only, not JPEGDEC; an esp32.com thread comparing ROM tjpgd and JPEGDEC is blocked here (snippet only). [retier] Independent atomic14 ESP32-S3 table (32 and 23 ms vs TJpgDec 55 ms and picojpeg 108 ms) is one image and one run per library with versions unpinned; the TJpg_Decoder baseline ships JD_FASTDECODE 1 and JD_TBLCLIP 0, not TJpgDec's fastest setup, and Espressif's esp_jpeg table (62 vs 46 ms) puts the lead nearer 1.3x; ESP32_JPEG is faster (20 ms). Open out-of-bounds write #119 in the progressive MCU path (colour progressive to grey or dithered output, cropped progressive decodes); baseline decode unaffected. MCU-oriented, 1/8-scale progressive decode in about 18 KB.

Baseline JPEG only (grayscale or YCbCr Huffman); progressive files are handled only as DC-only thumbnails (the decoder forces 1/8 scale and decodes the first scan). Aims at no more than 18K of RAM for baseline decode when output goes straight to an LCD (comment in jpeg.inl; README says 20K minimum). Callback design: caller supplies draw function, 2048-pixel internal buffer. Built-in 1/2, 1/4, 1/8 scaling, crop, Exif thumbnail, Floyd-Steinberg dithering; SIMD color conversion on ESP32-S3, Arm NEON and x86 SSE2.

## Maintenance

Actively maintained (last commit 2026-03-13, NLnet-funded, Apache-2.0, 631 stars) and easy to vendor as one translation unit, but the progressive-path out-of-bounds write (#119) is open and the 1.7x lead was measured against TJpgDec in a non-fastest build configuration, so treat it as an upper bound.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party measurement (atomic14, not the JPEGDEC author) with public code at atomic14/esp32-jpeg-perf-tests (src/main.cpp times each library's decode with millis(); src/JPEGDECTest.cpp, TJPEGTest.cpp, JPEGDecoderTest.cpp) and -Ofast in platformio.ini on an ESP32-S3. Not A: toolchain version (platform = espressif32 unpinned), library versions and clock are not stated, and it is one image with one timed decode per library.
- **Verifier notes:** Table numbers verified verbatim in atomic14's README and the harness code read; metadata matches (Apache-2.0, 631 stars, 75 forks, 212 commits, last commit 2026-03-13 'Fixed 2 issues which occur when decoding progressive images', active). baseline_in_list set to false: TJpgDec and picojpeg are widely used MCU decoders but not among the image-codecs baselines. Shortcomings to record: one-image single-run demo, unpinned versions, hard-coded decode+draw value for JPEGDecoder, callback copy asymmetry, cross-session 2024 row, ESP32_JPEG faster.
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** multi-image repeated run with pinned versions; comparison against TJpgDec at its fastest configuration
- **Pages the verifier opened:**
  - <https://github.com/atomic14/esp32-jpeg-perf-tests>
  - <https://github.com/atomic14/esp32-jpeg-perf-tests/commits>
  - <https://github.com/atomic14/esp32-jpeg-perf-tests/tree/main/src>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/README.md>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/platformio.ini>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/9052453/platformio.ini>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/ed3df28/platformio.ini>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/src/JPEGDECTest.cpp>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/src/TJPEGTest.cpp>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/src/JPEGDecoderTest.cpp>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/src/ESP32JPEGTest.cpp>
  - <https://github.com/bitbank2/JPEGDEC>
  - <https://github.com/bitbank2/JPEGDEC/commits>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/master/perf.jpg>
  - <https://raw.githubusercontent.com/espressif/idf-extra-components/HEAD/esp_jpeg/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/src/JPEGDEC.h>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/src/JPEGDEC.cpp>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/src/jpeg.inl>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/library.properties>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/library.json>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/Makefile>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/linux/makefile>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/linux/examples/jpeg_perf_test/main.cpp>
  - <https://raw.githubusercontent.com/bitbank2/JPEGDEC/HEAD/linux/examples/jpeg_perf_test/Makefile>
  - <https://github.com/bitbank2/JPEGDEC>
  - <https://github.com/bitbank2/JPEGDEC/tree/master/src>
  - <https://github.com/bitbank2/JPEGDEC/tree/master/linux>
  - <https://github.com/bitbank2/JPEGDEC/tree/master/linux/examples>
  - <https://github.com/bitbank2/JPEGDEC/tree/master/linux/examples/jpeg_perf_test>
  - <https://github.com/bitbank2/JPEGDEC/commits/master>
  - <https://github.com/bitbank2/JPEGDEC/issues?q=is%3Aissue>
  - <https://github.com/bitbank2/JPEGDEC/issues/110>
  - <https://github.com/bitbank2/JPEGDEC/issues/116>
  - <https://github.com/bitbank2/JPEGDEC/issues/119>
  - <https://github.com/bitbank2/JPEGDEC/issues/120>
  - <https://github.com/bitbank2/JPEGDEC/issues/122>
  - <https://github.com/bitbank2/JPEGDEC/issues/123>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/README.md>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/platformio.ini>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/src/JPEGDECTest.cpp>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/src/TJPEGTest.cpp>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/src/JPEGDecoderTest.cpp>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/src/ESP32JPEGTest.cpp>
  - <https://raw.githubusercontent.com/atomic14/esp32-jpeg-perf-tests/HEAD/include/images/jpeg280x240.h>
  - <https://github.com/atomic14/esp32-jpeg-perf-tests/tree/main/src>
  - <https://raw.githubusercontent.com/Bodmer/TJpg_Decoder/HEAD/src/tjpgdcnf.h>
  - <https://raw.githubusercontent.com/Bodmer/TJpg_Decoder/HEAD/src/TJpg_Decoder.h>
  - <https://raw.githubusercontent.com/espressif/idf-extra-components/HEAD/esp_jpeg/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/bitbank2/jpegdec`) · [data/wave10/enrich/raw/github_com_bitbank2_jpegdec.json](../../../data/wave10/enrich/raw/github_com_bitbank2_jpegdec.json) (enrichment confidence 0.75)

</details>
