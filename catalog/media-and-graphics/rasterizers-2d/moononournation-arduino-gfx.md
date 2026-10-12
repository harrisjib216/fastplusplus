# Arduino_GFX (GFX Library for Arduino)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Arduino display library for about 40 panel controllers and many buses; 1.2x-5.2x faster than Adafruit_GFX on an ESP32 SPI ILI9341.

| | |
|---|---|
| **Beats** | Adafruit_GFX (Adafruit-GFX-Library) with the Adafruit_ILI9341 driver |
| **Claimed result** | Arduino_graphicstest_PDQ result.txt (reproduced in the Arduino_GFX README Performance table), one pass per test, microseconds (lower is faster), Arduino_GFX versus Adafruit_GFX with the Adafruit_ILI9341 driver: Text 18,960 vs 97,662 (5.2x); Lines 412,026 vs 1,062,311 (2.6x); Circles (outline) 40,955 vs 118,125 (2.9x); Triangles (outline) 23,570 vs 58,843 (2.5x); Rounded rects (outline) 21,562 vs 43,185 (2.0x); Pixels 903,549 vs 1,365,211 (1.5x); Screen fill 160,094 vs 195,782 (1.2x); Rectangles (filled) 332,696 vs 406,817 (1.2x); ratios derived from page data. Arduino_GFX is slower than LovyanGFX and TFT_eSPI on every row except Text (for example Lines 412,026 vs 269,060 and 264,950; Circles 40,955 vs 25,959 and 25,269). |
| **Workload** | Arduino_GFX README 'Performance' table: per-primitive drawing benchmark (screen fill, text, pixels, lines, horizontal/vertical lines, rectangles, triangles, circles, arcs, rounded rectangles; filled and outline variants) pushed to an ILI9341 over SPI, comparing Adafruit_GFX, Arduino_GFX, LovyanGFX and TFT_eSPI. |
| **Metric** | latency |
| **Hardware** | TTGO T8 v1.8 (ESP32) board, PSRAM disabled, ILI9341 240x320 panel in 16-bit RGB565 on 4-wire SPI at 40 MHz (pins CS 5, DC 27, RST 33, SCLK 18, MOSI 23, MISO 19), no DMA; Arduino IDE 1.8.15, arduino-esp32 1.0.6; test date 2021-06-16 (benchmark repo commit 8798d61 'refresh test parameters'); exact ESP32 CPU clock not stated |
| **Compiler and flags** | Arduino IDE 1.8.15 with the arduino-esp32 1.0.6 default toolchain; compiler flags not stated |
| **Adoption** | 1.1k stars; 80+ display models supported |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/moononournation/Arduino_GFX) · [benchmark](https://github.com/moononournation/Arduino_graphicstest_PDQ/blob/master/result.txt) |

## Verdict

The author's single-pass Arduino_graphicstest_PDQ run (2021-06-16; Arduino IDE 1.8.15, arduino-esp32 1.0.6, TTGO T8 v1.8 ESP32, PSRAM off, ILI9341 over 4-wire SPI at 40 MHz, no DMA; compiler flags, CPU clock and library versions not recorded) timed identical test bodies in four libraries: Arduino_GFX beat Adafruit_GFX with Adafruit_ILI9341 by 5.2x on text, 2.9x on outline circles, 2.6x on lines, 2.5x on outline triangles, 1.5x on pixels and 1.2x on fills. Timings stop after the last call returns, and Arduino_ESP32SPI blocks until each SPI transfer completes, so no queued work escapes the timer; the 2020-10-15 run of the same suite gave nearly identical Arduino_GFX numbers (Text 18,933, Pixels 903,550, Lines 433,864 us).

## Use it when

- Arduino IDE projects on ESP32-family boards (ESP32, S2, S3, C3, C5, C6, H2, P4), RP2040/RP2350, ESP8266, AVR, nRF52, RTL872x, STM32 or SAMD21 that use a panel or bus few other libraries cover: 9-bit SPI panels (HX8357B), ESP32-S3 RGB panels, ESP32-P4 DSI, AMOLED dev boards from LilyGo, Waveshare, Makerfabs and others.
- Replacing Adafruit_GFX plus a controller driver when text, outline shapes and lines are slow: the 2021 run measured 5.2x on text, 2.9x on outline circles and 2.6x on lines against Adafruit_GFX with Adafruit_ILI9341.
- Text-heavy screens with opaque (background-coloured) built-in or GFXfont text, where it had the fastest Text row of the four libraries (18,960 us vs 21,752 for TFT_eSPI and 22,473 for LovyanGFX).
- Projects that want the panel and pins chosen in the sketch (or from the bundled dev-device declarations) instead of editing a header inside the library folder, or that need CJK text from U8g2 fonts.
- LVGL front ends on supported dev boards; the library ships LVGL benchmark, hello-world and widgets examples.

## Skip it when

- Maximum drawing speed on ESP32 SPI: in the same 2021 run LovyanGFX and TFT_eSPI beat it on every row except Text, by up to 1.65x (Lines 412,026 vs 264,950 us; Rounded rects outline 21,562 vs 13,089 us; derived from page data). Its own README says speed is not its first priority.
- Fill-dominated screens: fills are bound by the 40 MHz SPI link, so it is only 1.2x faster than Adafruit_GFX there; the blocking poll per 32-pixel chunk reached 95.9% of the link rate versus 98.5-99.5% for TFT_eSPI and LovyanGFX (derived from page data).
- PlatformIO or ESP-IDF-first projects: the README says only the Arduino IDE is supported and points PlatformIO problems to PlatformIO; ESP32LCD8, ESP32LCD16 and ESP32RGBPanel buses work only on arduino-esp32 2.x, not 3.x.
- Projects needing support or new features on request: the author estimates sponsorship at under one man-hour per month, closes non-issue issues and routes feature requests to Discussions.
- Desktop, anti-aliased or vector-path rendering: it is an integer RGB565 embedded display stack, not a path rasterizer like the Blend2D, Skia or AGG entries in this category.

## How it is fast

The display layer is split from the bus layer, and each bus class writes the MCU's peripheral directly. On ESP32, Arduino_ESP32SPI programs the SPI registers itself, packs bytes into a 64-byte DMA-capable buffer and polls cmd.usr until each transfer ends; fills preload the hardware data buffer with the colour and re-trigger 32-pixel transfers, and DC and CS are toggled with single GPIO set/clear register writes. Arduino_ILI9341::writeAddrWindow caches the last column and row windows and skips CASET or PASET when unchanged. Arduino_TFT::writeSlashLine splits Bresenham lines into horizontal or vertical runs sent as one window each, and opaque built-in or GFXfont characters go out as one address window per character with a row buffer (writePixels) instead of per-pixel writes, which is why it posted the fastest Text row. Like the other non-Adafruit libraries, it never reads back display memory.

## Compared with alternatives

Pick Arduino_GFX over TFT_eSPI or LovyanGFX when you need its panel and bus breadth (9-bit SPI, RGB and DSI panels, many ready-made dev-board declarations), sketch-level configuration, U8g2 CJK fonts or the fastest opaque text; pick LovyanGFX or TFT_eSPI when SPI drawing speed for lines, shapes and pixels dominates, since both were faster on every other row of the same run.

## Integration

| | |
|---|---|
| **Form** | Arduino library compiled from source (src/\*.cpp: core classes plus per-bus and per-display classes) |
| **Dependencies** | Arduino core for the target board; optional U8g2 (include U8g2lib.h before Arduino_GFX_Library.h for U8g2 fonts); LVGL only for the LVGL examples |
| **Minimum toolchain** | Arduino IDE (the only supported IDE per README); C++ standard not documented; ESP32 RGB/LCD parallel buses need arduino-esp32 2.x, and v1.6.5 added compatibility with arduino-esp32 3.3.6 |
| **Platforms** | ESP32, ESP32-S2/S3/C2/C3/C5/C6/H2/P4, ESP8266, RP2040/RP2350, AVR (Uno, Nano, Mega), Arduino UNO R4, nRF52 (Nano 33 BLE), RTL8720/8722, STM32 (BlackPill F411), SAMD21, Sony Spresense; generic boards through the Arduino SPI class |
| **Thread safety** | Not documented. Arduino_ESP32SPI takes the Arduino core's SPI bus lock in beginWrite when is_shared_interface is true (the default), but object state such as the cached address window and the partial-byte buffer index is unprotected, so drive each display object from one task. |
| **Drop-in for the baseline** | partial: drawing calls keep Adafruit_GFX names, but construction differs (data-bus object plus display object, begin(speed)), colour constants are RGB565_\*, and the class does not derive from Adafruit_GFX, so code taking an Adafruit_GFX reference will not accept it |

## Gotchas

- The published numbers are from a mid-2021 release on arduino-esp32 1.0.6 and are not reproducible as-is today: the PDQ sketch uses WHITE, BLACK, RED and similar names, while the 1.6.8 headers read here define only RGB565_\* constants, and the bus and text code has changed since (v1.6.5 fixed drawChar crashes, v1.6.7 clips built-in font pixels before preclipped writes).
- Arduino_ESP32SPI defaults to is_shared_interface = true, which runs spiTransaction on every startWrite; pass false to hold the bus from begin() when no other SPI device shares it. The benchmark sketch kept the default and also passed a MISO pin, which makes writeRepeat reload the SPI data registers for every 32-pixel chunk.
- Plain drawLine with diagonal slopes still costs one address-window update per run, and drawPixel costs a CASET (or PASET), RAMWR and a blocking transfer per pixel; batch pixels into a Canvas or draw16bitRGBBitmap when you can.
- Open bug #754 (January 2026): 9-bit SPI on ESP32-family chips pads partial bytes with garbage in flush_data_buf, corrupting 9-bit panels; the 8-bit DC/SPI path used in the benchmark is not affected.

## Known shortcomings

- Embedded SPI display driver (ILI9341 240x320 RGB565 at 40 MHz on a TTGO T8 v1.8 ESP32, arduino-esp32 1.0.6, no DMA), a weak fit for 2D rasterizers; baseline Adafruit_GFX plus Adafruit_ILI9341 is not a listed incumbent. First-party single-pass microsecond timings (moononournation/Arduino_graphicstest_PDQ result.txt, 2021-06-16, commit 8798d61) with flags and board settings unstated. Faster than Adafruit_GFX on every row but slower than LovyanGFX and TFT_eSPI on every row except Text; screen fill sits at the 153,600 us SPI wire limit (derived).
- Slower than LovyanGFX and TFT_eSPI on every row but Text (up to 1.65x) in its own result.txt; fills reach 95.9% of the SPI link against 98.5-99.5% for the others. The 2021 sketch will not build against 1.6.8 (WHITE and BLACK gone, only RGB565_\* names); the bench used the default is_shared_interface=true plus a MISO pin; Arduino IDE only; open #754 (9-bit SPI garbage).

## Caveats and trade-offs

First-party measurement: the author of Arduino_GFX ran all four libraries, and his README says 'This library is not putting speed at the first priority'. The README table does not link its code, but the sketches and raw output are in moononournation/Arduino_graphicstest_PDQ (result.txt matches the table digit for digit; the units are microseconds per the sketches' 'Benchmark micro-secs' header). The four sketches run identical test bodies (adapted from Adafruit and Xark's PDQ graphicstest) at the same 240x320 resolution, RGB565 colour and 40 MHz SPI, with no DMA and no bus held across tests; Arcs are N/A for Adafruit_GFX and TFT_eSPI because those libraries lacked arc calls at the time. Single pass per test, no repeat count or variance; library versions not recorded, and an earlier 2020-10-15 run in the same repository's README gives different numbers for some libraries (for example TFT_eSPI Lines 308,601), so results move with library versions. The benchmark repository's README still lists the older hardware (ESP32-DevKitC, ESP32 LCDKit, Arduino IDE 1.8.13). Compiler flags and Arduino board-menu settings are not stated. Screen fill is bound by the SPI link: five full-screen fills of 240x320x16 bits at 40 MHz need 153,600 microseconds (derived from page data), so fills differ only in overhead above that wire limit. Weak category fit: an embedded SPI display driver stack with drawing primitives, not a general path rasterizer comparable to Skia, Cairo or Blend2D. license.txt is the Adafruit two-clause BSD text, so BSD-2-Clause is recorded; the GitHub sidebar does not detect a license.

Arduino-style C++ library for ESP32, RP2040, AVR and other microcontrollers with many display controllers and data-bus classes; skips display read-back to save footprint and time; also offers arcs, which Adafruit_GFX lacks (N/A in the table); focuses on breadth of hardware support, not on matching Skia-class path rendering.

## Maintenance

Active, single maintainer: release v1.6.8 (September 2026, mostly new boards and DSI fixes), 1,539 commits, 1.1k stars, 249 forks and only 2 open issues because non-bug issues are closed; the Adafruit-derived two-clause BSD licence (license.txt; GitHub detects none) makes it copyable, but support is explicitly minimal.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The Arduino_GFX README Performance table matches result.txt in moononournation/Arduino_graphicstest_PDQ exactly, and that repository holds the per-library benchmark sketches (Adafruit_GFX_graphicstest_PDQ.ino, Arduino_GFX_graphicstest_PDQ.ino, LovyanGFX_graphicstest_PDQ.ino, TFT_eSPI_graphicstest_PDQ.ino), so code, toolchain version (arduino-esp32 1.0.6) and board (TTGO T8 v1.8, ESP32) are public; compiler flags and Arduino board-menu settings (board profile, CPU clock) are not stated, so it falls short of A, and the measurement is first-party for Arduino_GFX (its author ran it), so C.
- **Verifier notes:** Numbers verified against both the README table and the raw result.txt; benchmark code found in a separate repo by the same author, so benchmark_url now points at result.txt. Tier stays C (flags unstated, first-party for Arduino_GFX); category fit is weak, orchestrator decides.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compared_against_cpp_std_directly`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/moononournation/Arduino_GFX>
  - <https://github.com/moononournation/Arduino_GFX/commits/master>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/README.md>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/license.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/examples/PDQgraphicstest/PDQgraphicstest.ino>
  - <https://github.com/moononournation/Arduino_graphicstest_PDQ>
  - <https://github.com/moononournation/Arduino_graphicstest_PDQ/commits/master>
  - <https://github.com/moononournation/Arduino_graphicstest_PDQ/commit/8798d61>
  - <https://github.com/moononournation/Arduino_graphicstest_PDQ/blob/master/result.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/README.md>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/result.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/Adafruit_GFX_graphicstest_PDQ/Adafruit_GFX_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/Arduino_GFX_graphicstest_PDQ/Arduino_GFX_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/LovyanGFX_graphicstest_PDQ/LovyanGFX_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/TFT_eSPI_graphicstest_PDQ/TFT_eSPI_graphicstest_PDQ.ino>
- **Sources the enricher read:**
  - <https://github.com/moononournation/Arduino_GFX>
  - <https://github.com/moononournation/Arduino_GFX/issues>
  - <https://github.com/moononournation/Arduino_GFX/issues/754>
  - <https://github.com/moononournation/Arduino_GFX/releases>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/README.md>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/library.properties>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/license.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/Arduino_GFX.h>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/Arduino_GFX.cpp>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/Arduino_G.h>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/Arduino_GFX_Library.h>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/Arduino_TFT.h>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/Arduino_TFT.cpp>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/Arduino_DataBus.h>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/Arduino_DataBus.cpp>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/databus/Arduino_ESP32SPI.h>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/databus/Arduino_ESP32SPI.cpp>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/display/Arduino_ILI9341.h>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/src/display/Arduino_ILI9341.cpp>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/examples/PDQgraphicstest/PDQgraphicstest.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/README.md>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/result.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/Adafruit_GFX_graphicstest_PDQ/Adafruit_GFX_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/Arduino_GFX_graphicstest_PDQ/Arduino_GFX_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/LovyanGFX_graphicstest_PDQ/LovyanGFX_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/TFT_eSPI_graphicstest_PDQ/TFT_eSPI_graphicstest_PDQ.ino>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/moononournation/arduino_gfx`) · [data/wave10/enrich/raw/github_com_moononournation_arduino_gfx.json](../../../data/wave10/enrich/raw/github_com_moononournation_arduino_gfx.json) (enrichment confidence 0.75)

</details>
