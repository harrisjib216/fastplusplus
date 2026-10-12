# TFT_eSPI

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [2D rasterizers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Arduino TFT driver plus drawing library for ESP32, RP2040, ESP8266 and STM32; 1.3x to 4.7x faster than Adafruit_GFX on an ILI9341 at 40 MHz.

| | |
|---|---|
| **Beats** | Adafruit_GFX (Adafruit-GFX-Library) with the Adafruit_ILI9341 driver |
| **Claimed result** | Arduino_graphicstest_PDQ result.txt (reproduced in the Arduino_GFX README Performance table), one pass per test, microseconds (lower is faster), TFT_eSPI versus Adafruit_GFX with the Adafruit_ILI9341 driver: Text 21,752 vs 97,662 (4.5x); Lines 264,950 vs 1,062,311 (4.0x); Circles (outline) 25,269 vs 118,125 (4.7x); Triangles (outline) 16,277 vs 58,843 (3.6x); Rounded rects (outline) 15,371 vs 43,185 (2.8x); Pixels 775,781 vs 1,365,211 (1.8x); Screen fill 155,938 vs 195,782 (1.3x); Rectangles (filled) 323,908 vs 406,817 (1.3x); ratios derived from page data. TFT_eSPI is fastest of the four on Pixels, Lines and Circles (outline) and beats LovyanGFX on Text, but trails LovyanGFX on the other rows by up to 17% (Rounded rects (outline) 15,371 vs 13,089) (derived from page data). The TFT_eSPI README says its speed additions make it 'typically 3 to 10 times faster' than the Adafruit libraries it derives from, without a benchmark or numbers behind that statement. |
| **Workload** | Arduino_GFX README 'Performance' table: per-primitive drawing benchmark (screen fill, text, pixels, lines, horizontal/vertical lines, rectangles, triangles, circles, arcs, rounded rectangles; filled and outline variants) pushed to an ILI9341 over SPI, comparing Adafruit_GFX, Arduino_GFX, LovyanGFX and TFT_eSPI. |
| **Metric** | latency |
| **Hardware** | TTGO T8 v1.8 (ESP32) board, PSRAM disabled, ILI9341 240x320 panel in 16-bit RGB565 on 4-wire SPI at 40 MHz (User_Setup.h: ILI9341_DRIVER, SPI_FREQUENCY 40000000, GLCD font), no DMA; Arduino IDE 1.8.15, arduino-esp32 1.0.6; test date 2021-06-16 (benchmark repo commit 8798d61); exact ESP32 CPU clock not stated |
| **Compiler and flags** | Arduino IDE 1.8.15 with the arduino-esp32 1.0.6 default toolchain; compiler flags not stated |
| **Adoption** | 4.9k stars; widely used Arduino and PlatformIO TFT library |
| **Last commit** | 2026-04-03 |
| **Links** | [repository](https://github.com/Bodmer/TFT_eSPI) · [benchmark](https://github.com/moononournation/Arduino_graphicstest_PDQ/blob/master/result.txt) |

## Verdict

One single-pass run of moononournation's Arduino_graphicstest_PDQ (2021-06-16; Arduino IDE 1.8.15, arduino-esp32 1.0.6, TTGO T8 v1.8 ESP32, PSRAM off, ILI9341 over SPI at 40 MHz, no DMA; compiler flags, CPU clock and TFT_eSPI version not recorded) timed the same test body in each library: TFT_eSPI beat Adafruit_GFX with Adafruit_ILI9341 by 4.7x on outline circles, 4.5x on text, 4.0x on lines, 1.8x on pixels and 1.26-1.3x on fills. Timings stop after end_tft_write's SPI-busy wait, so they include the final transfer; the 2020 run of the same suite gave noticeably different TFT_eSPI numbers, and the README's own '3 to 10 times faster' claim has no benchmark behind it.

## Use it when

- Arduino or PlatformIO firmware on ESP32, ESP32-S2/S3/C3, RP2040, ESP8266 or STM32F/L4 driving a supported SPI panel, where Adafruit_GFX plus a controller driver is too slow for pixel-, line- and text-heavy screens.
- Per-pixel or line-heavy drawing (plots, gauges, wireframes): it had the fastest Pixels (775,781 us) and Lines (264,950 us) rows of the four libraries measured.
- RP2040 with 8- or 16-bit parallel panels driven by PIO, with DMA, which the README reports at 4 ms to clear a 320x480 screen.
- Projects that want a large example set and ecosystem: Sprites for flicker-free updates, vlw smooth fonts from flash arrays or LittleFS, OpenFontRender TrueType add-on, TFT_eWidget GUI widgets, XPT2046 touch.
- Porting an existing Adafruit_GFX sketch with minimal source changes.

## Skip it when

- Recent ESP32 Arduino cores and new chips: open issues report ESP32-S3 boot crashes on cores newer than 2.0.14 (#3329) and that ESP32-C6/H2 on core 3.0.x need local modifications (#3438). The Feb 2026 commits fix DMA on C3/S3 for 3.x board packages, but the last tagged release, V2.5.43 (6 March), predates them.
- When raw speed on ESP32 SPI is the only criterion: LovyanGFX beat it on 9 of the 13 rows both ran in the same 2021 run (TFT_eSPI won only Text, Pixels, Lines and outline Circles), by up to 17% (Rounded rects outline 13,089 vs 15,371 us), and also ran the Arcs rows that TFT_eSPI lacked then (derived from page data).
- Fill-dominated screens: fills are bound by the SPI clock, so at 40 MHz the gain over Adafruit_GFX is only 1.25x to 1.3x (Screen fill 1.26x, Rectangles filled 1.26x, Rounded rects filled 1.26x); a faster bus, a parallel panel or partial redraws matter more.
- Generic Arduino boards outside the optimised list: the README says they fall back to the slower Arduino SPI calls, and only SPI panels are supported there.
- Projects needing runtime display selection or several different panels in one build: the configuration is compile-time and global to the library folder.
- Desktop or vector-graphics work: it is an embedded panel driver with integer primitives, not a general path rasterizer like the Blend2D, Skia or AGG entries in this category.

## How it is fast

On ESP32 it bypasses the Arduino SPI library and writes the SPI peripheral registers directly (TFT_WRITE_BITS sets the length register, the W0 data register and the SPI_USR start bit), and toggles DC and CS with single GPIO set/clear register writes. Solid fills (pushBlock) load the 64-byte W0-W15 buffer with the colour once and re-trigger 512-bit transfers, so a fill streams at the SPI link rate; fillScreen reached 98% of the 40 MHz link limit in the benchmark versus 78% for Adafruit_GFX (derived from page data). drawPixel caches the last column and row address and skips re-sending CASET or PASET when they are unchanged. drawLine splits Bresenham's line into horizontal or vertical runs drawn with drawFastHLine/drawFastVLine, circles are drawn as runs too, and one bus transaction is held across a whole primitive (inTransaction) instead of one per pixel.

## Compared with alternatives

Pick TFT_eSPI over LovyanGFX when per-pixel and line drawing dominate, you are on RP2040 parallel/PIO panels, or you rely on its Sprite, smooth-font and widget ecosystem; pick LovyanGFX for the fastest fills, shapes and arcs on ESP32 SPI, runtime panel configuration and better tracking of new ESP32 cores. Pick Arduino_GFX when you need its wider range of data-bus classes and panels; it was slower than both on lines, shapes and pixels but fastest on text in the same run.

## Integration

| | |
|---|---|
| **Form** | Arduino library compiled from source (TFT_eSPI.cpp plus a per-processor file); also usable as an ESP-IDF component that requires the arduino component |
| **Dependencies** | Arduino core for the target (SPI; FS/SPIFFS or LittleFS for smooth fonts loaded from flash); ESP-IDF spi_master driver for ESP32 DMA; Earle Philhower's arduino-pico core for RP2040 PIO features |
| **Minimum toolchain** | Arduino IDE or PlatformIO; ESP32 Arduino board package 2.x.x or later for the ESP32 family (README); arduino-pico core for RP2040 PIO |
| **Platforms** | Optimised: RP2040, ESP32, ESP32-S2/S3/C3, ESP8266, STM32F1/F2/F4/F7 (DMA on ESP32, RP2040 and STM32 SPI); other 32-bit Arduino boards through generic Arduino SPI calls |
| **Thread safety** | Not documented. The transaction flags (locked, inTransaction, lockTransaction) are plain bools with no RTOS mutex; on ESP32 SUPPORT_TRANSACTIONS is forced so SPI.beginTransaction takes the SPI HAL lock, but object state is unprotected, so drive one TFT_eSPI object from one task. |
| **Drop-in for the baseline** | partial: drawing calls keep Adafruit_GFX names and signatures, but the constructor takes no pins (they come from User_Setup.h), colour constants are TFT_\* rather than ILI9341_\*, and init() replaces begin(freq) |

## Gotchas

- Configuration lives inside the library folder (User_Setup.h / User_Setup_Select.h); updating the library overwrites it unless you keep setups in a sibling folder as the README's Tips describe. The shipped default User_Setup.h sets SPI_FREQUENCY to 27 MHz, not the 40 MHz used in the benchmark.
- On ESP32, pushBlock and drawPixel return before the last SPI transfer finishes (the 'Do not wait here' comment and tft_Write_16N); end_tft_write waits, but code that toggles the shared bus inside startWrite()/endWrite() must account for it. Sharing the bus with an SD card requires TFT_MISO/MOSI/SCLK to be defined explicitly (README).
- DMA is used only by pushImageDMA/pushPixelsDMA; fillRect, lines and text always use the blocking register path, and DMA is unavailable for ILI9481/ILI9486/ILI9488 over SPI.
- Smooth (vlw) fonts cannot be scaled with setTextSize, and a later change added the smooth-font background-rendering flag as a new setTextColor parameter, which the README calls breaking for some sketches.

## Known shortcomings

- Embedded SPI display driver, a weak fit for 2D rasterizers; the only numbers are a competitor's run (Arduino_GFX author's result.txt, TTGO T8 ESP32, ILI9341 at 40 MHz, 2021-06-16) against Adafruit_GFX, not a listed incumbent. The README's 'typically 3 to 10 times faster' has no benchmark behind it. February 2026 commits include a DMA code fix.
- Fills are bound by the SPI link: TFT_eSPI reaches 98% of the 40 MHz limit against Adafruit_GFX's 78% (derived from page data), so the fill gain is only 1.26x, and LovyanGFX is faster on 9 of 13 shared rows of the same result.txt. Configuration lives in the library folder with a shipped default of 27 MHz SPI; no RTOS mutex (plain bool flags); DMA only for image pushes; open issues #3329 (ESP32-S3 crash on cores newer than 2.0.14) and #3438 (C6/H2 need edits); last release V2.5.43 predates the February 2026 fixes on master (2.5.44) after a gap from July 2024.

## Caveats and trade-offs

Measured by the author of a competing library (Arduino_GFX), not by the TFT_eSPI project; the result is against that author's interest since TFT_eSPI beats Arduino_GFX on most rows. The README table does not link its code, but the sketches and raw output are in moononournation/Arduino_graphicstest_PDQ (result.txt matches the table; units are microseconds). The TFT_eSPI sketch runs the identical test body as the Adafruit_GFX and Arduino_GFX sketches at the same 240x320 resolution, RGB565 colour and 40 MHz SPI, with no DMA and no bus held across tests (TFT_eSPI's DMA mode was not used); Arcs are N/A because TFT_eSPI lacked arc calls at the time. Single pass per test, no repeat count or variance; the TFT_eSPI version is not recorded and an earlier 2020-10-15 run gives notably different numbers (Lines 308,601, Circles 44,739), so results move with library versions. Compiler flags and Arduino board-menu settings are not stated. Screen fill is bound by the SPI link: five full-screen fills of 240x320x16 bits at 40 MHz need 153,600 microseconds (derived from page data). TFT_eSPI's own TFT_graphicstest_PDQ example divides fill time by 5, so its own output is not comparable to this table. Weak category fit: an embedded SPI/parallel display driver stack with drawing primitives, not a general path rasterizer comparable to Skia, Cairo or Blend2D. Maintenance: last commit 2026-04-03; the February 2026 commits include a code fix ('Fix DMA on ESP32 C3 and S3 for board packages 3.x.x') besides README and board-header updates; 278 open issues and 75 open pull requests, and a closed June 2025 issue (#3770) called the library abandoned and suggested LovyanGFX. license.txt combines the FreeBSD two-clause licence for the original code with the Adafruit BSD and MIT notices of the code it started from; the bundled fonts have separate licence files.

Grew out of Adafruit_ILI9341 and Adafruit_GFX; DMA on ESP32, RP2040 and STM32, 8 and 16-bit parallel interfaces, sprites for flicker-free updates, smooth anti-aliased arcs, circles and rounded rectangles, anti-aliased TrueType via the OpenFontRender add-on; user-setup header files select the display and processor; generic processors fall back to slow Arduino SPI calls.

## Maintenance

Active but slow-moving: after a gap from July 2024 to February 2026, a burst of commits (DMA fix for ESP32 C3/S3 on 3.x board packages, STM32L4 DMA, new setups) ends with a README update on 2026-04-03; master reports version 2.5.44 while the latest tagged release is V2.5.43, with 278 open issues and 75 open pull requests. The licence (FreeBSD two-clause for Bodmer's code plus Adafruit BSD and MIT notices) makes it copyable, and a June 2025 issue (#3770) calling it abandoned recommended LovyanGFX.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Numbers match result.txt in moononournation/Arduino_graphicstest_PDQ, whose TFT_eSPI_graphicstest_PDQ.ino runs the same test body as the Adafruit_GFX sketch on the same ILI9341 at 40 MHz; code, toolchain version and board are public but compiler flags and board-menu settings are not, the measurer is a competing library's author with a small repo, and TFT_eSPI's own README gives only an unbenchmarked '3 to 10 times faster' claim, so C.
- **Verifier notes:** Numbers verified in README table and raw result.txt; sketches equivalent across libraries. TFT_eSPI README's '3 to 10 times faster' claim added to claimed_speedup; caveat on recent commits corrected (Feb 2026 includes a DMA code fix). Tier stays C; weak category fit for orchestrator.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compared_against_cpp_std_directly`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Bodmer/TFT_eSPI>
  - <https://github.com/Bodmer/TFT_eSPI/commits/master>
  - <https://github.com/Bodmer/TFT_eSPI/issues/3770>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/README.md>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/license.txt>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/examples/320%20x%20240/TFT_graphicstest_PDQ/TFT_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/README.md>
  - <https://github.com/moononournation/Arduino_graphicstest_PDQ>
  - <https://github.com/moononournation/Arduino_graphicstest_PDQ/commits/master>
  - <https://github.com/moononournation/Arduino_graphicstest_PDQ/blob/master/result.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/result.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/README.md>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/Adafruit_GFX_graphicstest_PDQ/Adafruit_GFX_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/TFT_eSPI_graphicstest_PDQ/TFT_eSPI_graphicstest_PDQ.ino>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/README.md>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/license.txt>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/TFT_eSPI.h>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/TFT_eSPI.cpp>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/Processors/TFT_eSPI_ESP32.h>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/Processors/TFT_eSPI_ESP32.c>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/Processors/TFT_eSPI_Generic.h>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/Processors/TFT_eSPI_Generic.c>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/User_Setup.h>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/User_Setup_Select.h>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/library.json>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/library.properties>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Bodmer/TFT_eSPI/HEAD/examples/320%20x%20240/TFT_graphicstest_PDQ/TFT_graphicstest_PDQ.ino>
  - <https://github.com/Bodmer/TFT_eSPI>
  - <https://github.com/Bodmer/TFT_eSPI/commits/master>
  - <https://github.com/Bodmer/TFT_eSPI/releases>
  - <https://github.com/Bodmer/TFT_eSPI/issues?q=is%3Aissue+is%3Aopen+slow>
  - <https://github.com/Bodmer/TFT_eSPI/issues/3329>
  - <https://github.com/Bodmer/TFT_eSPI/issues/3770>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/result.txt>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/README.md>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/TFT_eSPI_graphicstest_PDQ/TFT_eSPI_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_graphicstest_PDQ/HEAD/Adafruit_GFX_graphicstest_PDQ/Adafruit_GFX_graphicstest_PDQ.ino>
  - <https://raw.githubusercontent.com/moononournation/Arduino_GFX/HEAD/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/bodmer/tft_espi`) · [data/wave10/enrich/raw/github_com_bodmer_tft_espi.json](../../../data/wave10/enrich/raw/github_com_bodmer_tft_espi.json) (enrichment confidence 0.75)

</details>
