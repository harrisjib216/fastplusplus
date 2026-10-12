# AnimatedGIF

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C (C99 core with an Arduino-style C++ class wrapper)` · `Apache-2.0` · 🟢 active

> Low-RAM, no-malloc animated GIF decoder for MCUs and PCs; claims to beat giflib but publishes no comparison.

| | |
|---|---|
| **Beats** | libgif (giflib) |
| **Claimed result** | README: new Turbo decode mode (output image used as the LZW dictionary, needs another 32K of RAM) 'can accelerate the decoding by 2-30x depending on the target system and image' (versus the library's own Normal mode, not versus libgif). Against libgif the README says only that the code 'will perform far better than libgif', with no number. |
| **Workload** | Decode time of an 8-frame 160x120 GIF (badgers.h) on microcontroller boards in perf.png; the 2-30x figure compares the library's own Turbo mode with its own Normal mode. |
| **Metric** | throughput |
| **Hardware** | perf.png lists MCU boards only: ESP8266 80 MHz 158,961 us; ESP32-S2 240 MHz 58,902 us; ESP32 240 MHz 49,468 us; Cortex-M0+ 48 MHz 357,160 us; Cortex-M4F 64 MHz 181,122 us; Cortex-M7 600 MHz 8,134 us. No desktop CPU stated. |
| **Adoption** | 537 stars |
| **Last commit** | 2026-07-03 |
| **Links** | [repository](https://github.com/bitbank2/AnimatedGIF) · [benchmark](https://github.com/bitbank2/AnimatedGIF) |

## Verdict

Nothing compares this library with giflib or any other decoder: perf.png only times one 8-frame 160x120 GIF (badgers.h) across six MCU boards (Cortex-M7 600 MHz 8,134 us to Cortex-M0+ 48 MHz 357,160 us) without naming the mode or library version, and the 2-30x figure is Turbo against the library's own Normal mode with no table. The only harness, examples/gif_benchmark/gif_benchmark.ino, is not like-for-like: its Turbo arm decodes RAW pixels with no palette conversion or draw callbacks, while its Normal arm runs COOKED RGB565 conversion plus a per-line callback, so its 'nearly 2X' overstates the decoder difference. A first-party 2021 blog post on the 'big memory' decoder (blocked here; search snippet only) claims about 5x faster than giflib on poorly compressed images and over 20x on well-compressed ones, with no harness.

## Use it when

- Playing GIF animations on microcontrollers (ESP32, Cortex-M0+/M4/M7, ESP8266, RP2040-class) where you cannot afford a full frame buffer or any malloc.
- Streaming decoded lines straight to an SPI LCD (optionally via DMA) while the next line decodes.
- Small embedded GUIs that play your own pre-made GIF assets from flash, where the images are known-good.
- Desktop or Raspberry Pi tools that want a dependency-free single-source GIF player and can live with the 2048-pixel width cap under __LINUX__.

## Skip it when

- Decoding untrusted GIFs: two buffer-overflow reports are open and unanswered (#115, 2026-01-27; #117, 2026-02-17, unvalidated LZW minimum code size), and the current source still reads ucCodeStart without checking it is 2-8.
- Turbo mode on any input you do not control: DecodeLZWTurbo never checks that a code is already defined and its copy routine has no bounds check by design (source comment: a check 'slows everything down about 10%'), and the repo's fuzz tests never enable Turbo.
- Wide images: canvas width is capped at 480 pixels on non-Linux builds and 2048 with __LINUX__ defined (GIF_TOO_WIDE otherwise).
- When you need a measured win over giflib on a PC: no number against giflib exists in the repo; use gif_load or giflib-turbo instead.
- Animations that rely on disposal method 2 or local palettes in low-RAM modes: the README warns they render incorrectly without a full canvas, and Turbo mode skips the previous-frame disposal restore that DecodeLZW performs.

## How it is fast

Normal mode is a classic linked-list LZW decoder tuned for MCUs: the chunked LZW stream is first 'de-chunked' into a flat buffer, codes are pulled from a 32- or 64-bit bit-buffer, and runs are copied with word-sized unaligned stores where the CPU allows it. Turbo mode (DecodeLZWTurbo) uses the output image itself as the LZW dictionary: each code is stored as an (offset, length) pair into already-decoded pixels, so emitting a string is a forward memcpy instead of a backwards linked-list walk and reversal. Recent commits add ESP32-S3/P4 assembly (s3_transparent.S, p4_transparent.S) and Arm NEON paths for transparent-pixel merging and palette lookup.

## Compared with alternatives

Pick AnimatedGIF over gif_load or giflib-turbo when the target is a microcontroller driving an LCD line by line with no heap; on a PC, gif_load has published timings against giflib 5.2.2 (1.28x-1.78x) and giflib-turbo keeps giflib's API with the same Turbo LZW technique.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libc string functions; Arduino.h when built for Arduino). Examples additionally use display libraries such as bb_spi_lcd or TFT_eSPI. |
| **Minimum toolchain** | C99 for the core (gif.inl); C++11 for the class wrapper (uses nullptr). linux/Makefile builds a static libAnimatedGIF.a with -O2. |
| **Platforms** | Any MCU with roughly 24-32K free RAM (Arduino 'architectures=\*'), plus Linux/macOS desktops and Raspberry Pi; optional NEON on Arm and assembly SIMD on ESP32-S3/P4. |
| **Thread safety** | not documented; all decoder state lives in the per-instance GIFIMAGE struct (about 25 KB, embedded in the class), so separate instances on separate threads should be independent. |
| **Drop-in for the baseline** | partial — replaces giflib functionally for playback, but with a different callback-based API; giflib-turbo (same author) is the API-compatible drop-in. |

## Gotchas

- Turbo RAW mode never calls GIFDraw: pixels are left in the turbo buffer (frame-sized, not composited), so you either read getTurboBuf() yourself or use COOKED with a frame buffer; issue #111 (open) reports COOKED Turbo output is wrong when no draw callback is given, and the code path assumes 16-bit output there.
- RAM figures disagree: README says Turbo needs 'another 32K', the header says '48K + full framebuffer', and allocTurboBuf actually allocates TURBO_BUFFER_SIZE (24,832 bytes) plus canvas width x height with plain malloc (uninitialized).
- On every 64-bit target ALLOWS_UNALIGNED is forced and the code type-puns unaligned 8-byte loads and stores, and Turbo mode fills the ucLZW array past its declared size into the following struct members (usGIFTable, ucGIFPixels, ucLineBuf); this works on x86-64/AArch64 but is undefined behavior that sanitizers will flag. A 64-bit pixel-overwrite bug (#112) was fixed only in November 2025.
- ESP32/ESP8266 users playing GIFs from RAM must supply their own file callbacks, because the in-memory reader assumes flash and uses memcpy_P.

## Known shortcomings

- Tier D: no libgif number anywhere; perf.png compares MCU boards, the 2-30x is Turbo mode against the library's own Normal mode, and gif_benchmark.ino's 'nearly 2X' is also an own-mode comparison.
- Enricher (2026-10-04): nothing compares the library with giflib or any other decoder; perf.png times one 8-frame 160x120 GIF across six MCU boards without naming mode or version, and the 2-30x figure is Turbo against the library's own Normal mode with no table. The only harness (examples/gif_benchmark/gif_benchmark.ino) is not like-for-like: the Turbo arm decodes RAW pixels with no palette conversion or draw callbacks while the Normal arm runs COOKED RGB565 conversion plus a per-line callback, so 'nearly 2X' overstates the decoder difference. Turbo RAW mode never calls GIFDraw (issue #111 open: COOKED Turbo output wrong without a draw callback); RAM figures disagree (README 32K, header 48K plus framebuffer, code 24,832 bytes plus canvas, uninitialized malloc); 64-bit targets force unaligned type-punned loads and Turbo fills ucLZW past its declared size into following struct members (undefined behavior); two security reports open for months. Tier D stands.

## Caveats and trade-offs

No numeric comparison against any recognizable baseline: perf.png is a table that compares boards with each other (speed rating relative to Cortex-M0+, plus current draw), with no libgif or giflib column. The 2-30x claim is Turbo versus the library's own Normal mode, with no table, harness, compiler, flags or image set behind it; examples/gif_benchmark/gif_benchmark.ino (an Arduino sketch timing one mode with micros()) says Turbo 'will usually result in a nearly 2X speedup' and has no libgif arm. README says the library performs far better than libgif on PC-class devices but gives no figure; the wiki (single Home page) has no numbers, linux/ holds only a Makefile (-O2) and examples, and MacOS/GIF_Test is an Xcode project with no results. Author's blog post 'A Big Memory GIF Decoder' is blocked here. Same Turbo LZW technique as the already-listed giflib-turbo (same author), which carries the drop-in giflib comparison. Tier D kept for the record; the project is notable (537 stars, 76 forks).

Turbo mode trades about 32K of extra RAM for speed; core needs only 24K RAM in normal mode, no malloc/free, line-by-line callback API built for SPI LCDs. Some GIFs (alternating transparent and opaque pixels, local palettes in COOKED mode) need a full canvas or run slower in the low-RAM modes. README says it does not use CPU-specific optimizations or assembly.

## Maintenance

Active (last commit 2026-07-03, v2.2.3 in library.properties, frequent 2025-2026 fixes and SIMD additions) and Apache-2.0, so it is easy to vendor, but two security reports have sat open for months, so treat it as a decoder for trusted assets only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** No number against libgif/giflib or any external decoder anywhere reachable: README says only 'will perform far better than libgif'; perf.png compares MCU boards with each other on one 160x120 8-frame GIF; the 2-30x is Turbo versus the library's own Normal mode with no table (examples/gif_benchmark/gif_benchmark.ino comments say 'nearly 2X' for Turbo and prints only its own time).
- **Verifier notes:** Batch note confirmed: D, baseline inside the same project is not an incumbent. Metadata matches: Apache-2.0, 537 stars, 76 forks, not a fork, not archived, last commit 2026-07-03 ('bump version number'), active.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** none (self-comparison only)
- **Pages the verifier opened:**
  - <https://github.com/bitbank2/AnimatedGIF>
  - <https://github.com/bitbank2/AnimatedGIF/commits>
  - <https://github.com/bitbank2/AnimatedGIF/wiki>
  - <https://github.com/bitbank2/AnimatedGIF/tree/master/examples>
  - <https://github.com/bitbank2/AnimatedGIF/tree/master/examples/gif_benchmark>
  - <https://github.com/bitbank2/AnimatedGIF/tree/master/examples/perf_explained>
  - <https://github.com/bitbank2/AnimatedGIF/tree/master/MacOS/GIF_Test>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/perf.png>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/linux/Makefile>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/examples/gif_benchmark/gif_benchmark.ino>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/examples/perf_explained/perf_explained.ino>
- **Sources the enricher read:**
  - <https://github.com/bitbank2/AnimatedGIF>
  - <https://github.com/bitbank2/AnimatedGIF/commits>
  - <https://github.com/bitbank2/AnimatedGIF/wiki>
  - <https://github.com/bitbank2/AnimatedGIF/tree/master/src>
  - <https://github.com/bitbank2/AnimatedGIF/tree/master/linux>
  - <https://github.com/bitbank2/AnimatedGIF/tree/master/linux/examples>
  - <https://github.com/bitbank2/AnimatedGIF/tree/master/MacOS/GIF_Test/GIF_Test>
  - <https://github.com/bitbank2/AnimatedGIF/issues>
  - <https://github.com/bitbank2/AnimatedGIF/issues?q=is%3Aissue+crash>
  - <https://github.com/bitbank2/AnimatedGIF/issues?q=is%3Aissue+turbo>
  - <https://github.com/bitbank2/AnimatedGIF/issues/111>
  - <https://github.com/bitbank2/AnimatedGIF/issues/112>
  - <https://github.com/bitbank2/AnimatedGIF/issues/115>
  - <https://github.com/bitbank2/AnimatedGIF/issues/117>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/library.properties>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/perf.png>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/src/AnimatedGIF.h>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/src/AnimatedGIF.cpp>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/src/gif.inl>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/linux/Makefile>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/examples/gif_benchmark/gif_benchmark.ino>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/examples/perf_explained/perf_explained.ino>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/MacOS/GIF_Test/GIF_Test/main.cpp>
  - <https://raw.githubusercontent.com/bitbank2/AnimatedGIF/HEAD/MacOS/GIF_Test/GIF_Test/Makefile>
  - WebSearch: bitbank2 AnimatedGIF benchmark giflib decode speed comparison (snippet of bitbanksoftware.blogspot.com 'A Big Memory GIF Decoder', not opened)
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/bitbank2/animatedgif`) · [data/wave10/enrich/raw/github_com_bitbank2_animatedgif.json](../../../data/wave10/enrich/raw/github_com_bitbank2_animatedgif.json) (enrichment confidence 0.8)

</details>
