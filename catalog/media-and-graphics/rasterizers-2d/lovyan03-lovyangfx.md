# LovyanGFX

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Embedded display driver and drawing library for ESP32-class MCUs; 1.3x to 4.6x faster than Adafruit_GFX on an ILI9341 at 40 MHz SPI.

| | |
|---|---|
| **Beats** | Adafruit_GFX (Adafruit-GFX-Library) with the Adafruit_ILI9341 driver; TFT_eSPI is roughly equal in the same table |
| **Claimed result** | Arduino_graphicstest_PDQ result.txt (reproduced in the Arduino_GFX README Performance table), one pass per test, microseconds (lower is faster), LovyanGFX versus Adafruit_GFX with the Adafruit_ILI9341 driver: Text 22,473 vs 97,662 (4.3x); Lines 269,060 vs 1,062,311 (3.9x); Circles (outline) 25,959 vs 118,125 (4.6x); Triangles (outline) 15,884 vs 58,843 (3.7x); Rounded rects (outline) 13,089 vs 43,185 (3.3x); Circles (filled) 42,787 vs 76,739 (1.8x); Pixels 867,702 vs 1,365,211 (1.6x); Screen fill 154,341 vs 195,782 (1.3x); Rectangles (filled) 320,761 vs 406,817 (1.3x); ratios derived from page data. LovyanGFX is fastest of the four libraries on 11 of 15 rows (TFT_eSPI wins Pixels, Lines and Circles (outline); Arduino_GFX wins Text) (derived from page data). LovyanGFX's own README only says it aims for 'higher functional coverage and performances' than Adafruit_GFX and TFT_eSPI, with no numbers. |
| **Workload** | Arduino_GFX README 'Performance' table: per-primitive drawing benchmark (screen fill, text, pixels, lines, horizontal/vertical lines, rectangles, triangles, circles, arcs, rounded rectangles; filled and outline variants) pushed to an ILI9341 over SPI, comparing Adafruit_GFX, Arduino_GFX, LovyanGFX and TFT_eSPI. |
| **Metric** | latency |
| **Hardware** | TTGO T8 v1.8 (ESP32) board, PSRAM disabled, ILI9341 240x320 panel in 16-bit RGB565 on 4-wire SPI at 40 MHz (freq_write and freq_fill both 40 MHz), no DMA; Arduino IDE 1.8.15, arduino-esp32 1.0.6; test date 2021-06-16 (benchmark repo commit 8798d61); exact ESP32 CPU clock not stated |
| **Compiler and flags** | Arduino IDE 1.8.15 with the arduino-esp32 1.0.6 default toolchain; compiler flags not stated |
| **Adoption** | 1.8k stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/lovyan03/LovyanGFX) · [benchmark](https://github.com/moononournation/Arduino_graphicstest_PDQ/blob/master/result.txt) |

## Verdict

One single-pass run of moononournation's Arduino_graphicstest_PDQ (2021-06-16; Arduino IDE 1.8.15, arduino-esp32 1.0.6, TTGO T8 v1.8 ESP32, PSRAM off, ILI9341 over 4-wire SPI at 40 MHz, no DMA; compiler flags, CPU clock and LovyanGFX version not recorded) timed the same test body per library: LovyanGFX beat Adafruit_GFX with Adafruit_ILI9341 by 4.6x on outline circles, 4.3x on text, 3.9x on lines, 3.7x on outline triangles, 1.6x on pixels and 1.27-1.3x on fills. The v0 code waits for the SPI busy flag in dc_h() before releasing the bus, so each timing includes the last transfer; the earlier 2020-10-15 run of the same suite gave LovyanGFX numbers up to 6.6% different (Pixels 814,232 vs 867,702 us).

## Use it when

- Arduino or ESP-IDF firmware on ESP32, ESP32-S2/S3/C3/C6/P4 driving a supported SPI, I2C or parallel panel where Adafruit_GFX plus a controller driver is too slow: in the 2021 run it was 4.3x faster on text, 3.9x on lines and 3.3x to 4.6x on outline circles, triangles and rounded rectangles.
- Shape-heavy screens (gauges, outlines, arcs): it was the fastest of the four libraries on 11 of 15 rows, and the only one besides Arduino_GFX with arc primitives (Arcs filled 21,546 us vs Arduino_GFX 33,381 us).
- Products that must pick the board or panel at run time (LGFX_AUTODETECT for M5Stack, ODROID-GO, Wio Terminal and others), drive several displays at once, or use 24-bit colour, EPD panels or rotated and zoomed sprites (pushRotateZoom).
- UI development on a desktop first: the same code renders through SDL2 or OpenCV on Windows, Linux or macOS (examples_for_PC) before flashing.
- Moving an existing TFT_eSPI sketch onto a newer ESP32 core, via the LGFX_TFT_eSPI.hpp alias header.

## Skip it when

- Fill-dominated screens on SPI: fills are bound by the bus clock, so the gain over Adafruit_GFX is only 1.27x on Screen fill and 1.27-1.28x on filled rectangles and rounded rectangles at 40 MHz (derived from page data); a parallel bus or partial redraws matter more than the library.
- Per-pixel plotting through drawPixel or text-heavy screens where every few percent counts: TFT_eSPI was 1.12x faster on Pixels (775,781 vs 867,702 us) and Arduino_GFX 1.19x faster on Text (18,960 vs 22,473 us) in the same run (derived from page data).
- MCUs outside the README table: AVR, STM32 and nRF52 are not listed; RP2040 is SPI only with no touch support, and ESP8266 I2C is a software implementation.
- Flash-tight targets on 1.2.30 or 1.2.31: merging the implementation into one translation unit kept unused panel and touch code and grew an ESP32-C3 build by about 575 KB (#940); 1.2.32 brings it back to 346 KB (1.2.29: 329 KB), so pin 1.2.32 or later and check the map file.
- An SPI bus shared with devices in a different SPI mode on ESP32-S3: pinned open issue #491 reports a DAC in mode 2 stops responding after a display update, with no maintainer workaround posted.

## How it is fast

On ESP32 the Bus_SPI layer drives the SPI peripheral registers directly (MOSI_DLEN, W0-W15, CMD) and toggles D/C with one GPIO set/clear register write, skipping the Arduino SPI and ESP-IDF driver calls per transfer. Solid fills (writeDataRepeat) preload the 64-byte W0-W15 buffer with the colour and, on the original ESP32, retrigger 2048-bit transfers that reuse that buffer as a ring, so a fill runs at the link rate (Screen fill 154,341 us against a 153,600 us floor for five 240x320 RGB565 frames at 40 MHz, derived from page data). Pixel streams (writePixels) ping-pong between the W0-W7 and W8-W15 halves with SPI_USR_MOSI_HIGHPART so colour conversion overlaps the previous transfer. Panel_LCD caches the CASET/RASET window and skips resending it when unchanged; drawLine is Bresenham emitted as horizontal or vertical runs (writeFillRectPreclipped per run, with off-screen segments skipped before the bus is touched), and drawCircle is the midpoint algorithm emitted as eight H/V spans per step inside one held transaction.

## Compared with alternatives

Pick LovyanGFX over TFT_eSPI for the fastest shapes, fills and arcs on ESP32 SPI, run-time panel setup, ESP-IDF builds and current ESP32 chips (C6, P4, S3 RGB); TFT_eSPI kept a 12% lead on single pixels and a 1.5% lead on lines (the latter within the 7% spread between LovyanGFX's 2020 and 2021 runs) and has the STM32 and RP2040 PIO paths. Pick Arduino_GFX when you need its wider data-bus range or the fastest text; neither is comparable to Blend2D, Skia or AGG, which are desktop anti-aliased path rasterizers.

## Integration

| | |
|---|---|
| **Form** | Arduino / PlatformIO library compiled from source (include LovyanGFX.hpp; v1 implementation in a few .cpp translation units since 1.2.32); ESP-IDF component and pico-sdk builds through CMakeLists.txt and boards.cmake |
| **Dependencies** | None outside the platform SDK for drawing; bundles TJpgDec, Pngle, QRCode and bitwizeshift/result; on ESP-IDF requires the nvs_flash, efuse, esp_lcd, driver and related components, and links an arduino-esp32 component automatically when present; SDL2 or OpenCV for PC builds |
| **Minimum toolchain** | No language standard or core version is documented; CI badges cover Arduino IDE, PlatformIO and ESP-IDF builds, and the 1.2.32 release notes mention arduino-esp32 2.0.x and 3.0.x (ESP-IDF 5.1); PC builds use CMake 3.8+ with Clang or GCC |
| **Platforms** | ESP32, ESP32-S2, ESP32-S3, ESP32-C3 per the README table (SPI with DMA, I2C, parallel; RGB on S3; composite video on ESP32), plus ESP32-C6 and ESP32-P4 per recent commits (open issue #851: SPI DMA not working on ESP32-P4); ESP8266 (SPI), SAMD51/SAMD21 (SPI, I2C), RP2040 (SPI); Windows, Linux and macOS through SDL2 or OpenCV |
| **Thread safety** | Not documented. startWrite/endWrite nesting is a plain uint32_t counter in IPanel and Panel_LCD tracks _in_transaction as a plain bool, so drive each LGFX object from one task; with use_lock = true (the Bus_SPI default) each transaction takes the ESP32 SPI bus lock so other devices on the bus are excluded while it runs. |
| **Drop-in for the baseline** | partial: Adafruit_GFX-style drawing names and signatures work, and colour constants use TFT_\* names, but the Adafruit_ILI9341(cs, dc, rst) constructor and begin(freq) are replaced by an LGFX class configured with Bus_SPI and Panel config structs (or autodetect), followed by init() |

## Gotchas

- The catalogued numbers were measured with the v0 API (lgfx::Panel_ILI9341 with public freq_write/spi_cs fields, setPanel, init(sclk, miso, mosi)); the run date points to tag 0.3.12 (2021-05-30), but the version was not recorded. v1 removed that API, so the benchmark sketch does not compile against current 1.2.x and the rewritten v1 code has not been re-measured.
- Bus_SPI::config_t defaults freq_write to 16 MHz, not the 40 MHz the benchmark used; set it explicitly for ILI9341-class panels.
- Colour arguments are typed by C++ type: uint32_t means RGB888, uint16_t and int32_t mean RGB565, uint8_t means RGB332. A bare literal like 0xFF0000 is an int and is read as RGB565; write 0xFF0000U for 24-bit colours.
- draw\* calls acquire and release the bus on every call (that is how the benchmark ran), while write\* calls require an explicit startWrite(); holding startWrite() across a frame is faster but blocks other devices such as an SD card on the same SPI bus until endWrite() or endTransaction(). Before 1.2.32, pushImageDMA() with a source in PSRAM or flash sent garbage on ESP32 (#949).

## Known shortcomings

- Embedded SPI display driver, a weak fit for 2D rasterizers; the only numbers are a competitor's run (Arduino_GFX author's result.txt, TTGO T8 ESP32, ILI9341 at 40 MHz, 2021-06-16) against Adafruit_GFX, not a listed incumbent. Fastest of the four libraries on 11 of 15 rows. Not a well-known suite, so C rather than B.
- The PDQ sketch uses the v0 API (Panel_ILI9341 freq_write and spi_cs, setPanel, init(sclk, miso, mosi)), probably tag 0.3.12; the v1 rewrite removed it, so the sketch does not compile on 1.2.32 and the current code was never re-measured. The 2020 and 2021 runs differ by up to 6.6% (Pixels), and TFT_eSPI is 12% faster on Pixels. Bus_SPI defaults freq_write to 16 MHz (the bench used 40); issue #940 (firmware +575 KB in 1.2.30) fixed in 1.2.32 on 2026-10-02; #491 (ESP32-S3 shared-bus SPI mode break) and #851 (P4 DMA) open.

## Caveats and trade-offs

Measured by the author of a competing library (Arduino_GFX), not by the LovyanGFX project; the result is against that author's interest since LovyanGFX beats Arduino_GFX on most rows. The README table does not link its code, but the sketches and raw output are in moononournation/Arduino_graphicstest_PDQ (result.txt matches the table; units are microseconds). The LovyanGFX sketch runs the identical test body as the Adafruit_GFX, Arduino_GFX and TFT_eSPI sketches at the same 240x320 resolution, RGB565 colour and 40 MHz SPI, with no DMA and no bus held across tests (panel rotation 2 versus 0 for the others, same portrait size). Single pass per test, no repeat count or variance; the LovyanGFX version used is not recorded and an earlier 2020-10-15 run gives slightly different numbers (Lines 261,781). Compiler flags and Arduino board-menu settings are not stated. Screen fill is bound by the SPI link: five full-screen fills of 240x320x16 bits at 40 MHz need 153,600 microseconds (derived from page data), and LovyanGFX's 154,341 sits at that limit. LovyanGFX's own examples/Test/TFT_graphicstest_PDQ sketch differs (it holds the bus with startWrite and divides fill time by 5), so its own output is not comparable to this table. Weak category fit: an embedded SPI/parallel display driver stack with drawing primitives, not a general path rasterizer comparable to Skia, Cairo or Blend2D. license.txt collects several permissive notices (FreeBSD two-clause for LovyanGFX and the TFT_eSPI parts, Adafruit BSD, MIT); the README lists further components under MIT, 3-clause BSD and the IPA Font License for converted IPA fonts; BSD-2-Clause is recorded as the main library license.

Mimics the Adafruit_GFX and TFT_eSPI APIs while adding DMA transfers, sprite rotation and scaling, 16 and 24-bit colour modes, and 40+ display controllers over SPI, I2C and parallel buses; ESP32, ESP8266 and SAMD51 oriented; drawing primitives only, not an SVG or path engine.

## Maintenance

Actively maintained: 2,008 commits, release 1.2.32 on 2026-10-02 fixing firmware size, ESP32-C6 builds and DMA from PSRAM, 16 open issues and no open pull requests; the main code is FreeBSD two-clause with MIT, BSD and IPA Font licences for bundled parts, so it is copyable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Numbers match result.txt in moononournation/Arduino_graphicstest_PDQ, whose LovyanGFX_graphicstest_PDQ.ino runs the same test body as the Adafruit_GFX sketch on the same ILI9341 at 40 MHz; code, toolchain version and board are public but compiler flags and board-menu settings are not, and the measurer is a competing library's author with a small, not well-known repo, so neither A nor B applies.
- **Verifier notes:** Numbers verified in README table and raw result.txt; per-library sketches are equivalent. Tier stays C; benchmark_url moved to result.txt; weak category fit for orchestrator.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compared_against_cpp_std_directly`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/lovyan03/LovyanGFX>
  - <https://github.com/lovyan03/LovyanGFX/commits/master>
  - <https://github.com/lovyan03/LovyanGFX/tree/master/examples>
  - <https://github.com/lovyan03/LovyanGFX/tree/master/examples/Test>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/README.md>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/license.txt>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/examples/Test/TFT_graphicstest_PDQ/TFT_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/README.md>
  - <https://github.com/moononournation/Arduino_graphicstest_PDQ>
  - <https://github.com/moononournation/Arduino_graphicstest_PDQ/commits/master>
  - <https://github.com/moononournation/Arduino_graphicstest_PDQ/blob/master/result.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/result.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/README.md>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/Adafruit_GFX_graphicstest_PDQ/Adafruit_GFX_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/LovyanGFX_graphicstest_PDQ/LovyanGFX_graphicstest_PDQ.ino>
- **Sources the enricher read:**
  - <https://github.com/lovyan03/LovyanGFX>
  - <https://github.com/lovyan03/LovyanGFX/commits/master>
  - <https://github.com/lovyan03/LovyanGFX/releases>
  - <https://github.com/lovyan03/LovyanGFX/releases/tag/1.2.32>
  - <https://github.com/lovyan03/LovyanGFX/tags?after=0.4.18>
  - <https://github.com/lovyan03/LovyanGFX/tags?after=0.4.6>
  - <https://github.com/lovyan03/LovyanGFX/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/lovyan03/LovyanGFX/issues/940>
  - <https://github.com/lovyan03/LovyanGFX/issues/491>
  - <https://github.com/lovyan03/LovyanGFX/tree/master/src/lgfx/v1/platforms/esp32>
  - <https://github.com/lovyan03/LovyanGFX/tree/master/src/lgfx/v1/panel>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/README.md>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/license.txt>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/library.json>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/library.properties>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/boards.cmake/esp-idf.cmake>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/LovyanGFX.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1_init.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/Panel.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/LGFXBase.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/LGFXBase.cpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/LGFX_Sprite.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/misc/pixelcopy.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/panel/Panel_LCD.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/panel/Panel_LCD.inl>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/panel/Panel_Device.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/panel/Panel_Device.inl>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/panel/Panel_ILI9341.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/platforms/esp32/Bus_SPI.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/src/lgfx/v1/platforms/esp32/Bus_SPI.inl>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/examples_for_PC/README.md>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/HEAD/examples_for_PC/CMake_SDL/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/0.3.12/src/LovyanGFX.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/0.3.12/src/lgfx/v0/platforms/LGFX_SPI_ESP32.hpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/0.3.12/src/lgfx/v0/platforms/esp32_common.cpp>
  - <https://raw.githubusercontent.com/lovyan03/LovyanGFX/0.3.12/src/lgfx/v0/platforms/esp32_common.hpp>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/result.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/README.md>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/LovyanGFX_graphicstest_PDQ/LovyanGFX_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/Adafruit_GFX_graphicstest_PDQ/Adafruit_GFX_graphicstest_PDQ.ino>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/lovyan03/lovyangfx`) · [data/wave10/enrich/raw/github_com_lovyan03_lovyangfx.json](../../../data/wave10/enrich/raw/github_com_lovyan03_lovyangfx.json) (enrichment confidence 0.75)

</details>
