# lowzag

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Image codecs](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Progressive-JPEG decoder in C99 that decodes at 1/2-1/8 scale in a fraction of libjpeg-turbo's coefficient memory.

| | |
|---|---|
| **Beats** | libjpeg-turbo (progressive coefficient array memory); also ROM TJpgDec for decode time on ESP32 |
| **Claimed result** | Memory at 12 MP 4:2:0 progressive: lowzag peak_alloc 36.2, 19.6, 6.8 and 3.4 MB at scales 1/1, 1/2, 1/4 and 1/8 against libjpeg-turbo's 36.1 MB coefficient array at every scale (about 10.6x less at 1/8, derived from page data); with an 800x480 crop 3.4, 2.8, 2.4 and 2.3 MB. Measured process peak RSS (ru_maxrss, lowzag CLI vs djpeg -nosmooth, libjpeg-turbo 3.0.4 on aarch64, docs/ALGORITHM.md): 36,580 vs 36,876 KiB at 1/1, 23,648 vs 36,980 at 1/2, 9,916 vs 36,552 at 1/4, 4,636 vs 36,536 at 1/8 (about 7.9x less at 1/8, derived from page data). Decode time on ESP32-S3 at 240 MHz, lowzag on the progressive file vs ROM TJpgDec on a jpegtran-converted baseline file with the same pixels: 4000x3000 at 1/4 5.7 s vs 9.1 s (about 1.6x faster, derived), 1600x1200 at 1/2 1.75 s vs 1.95 s, 800x480 at 1/1 0.63 s vs 0.46 s (lowzag slower). |
| **Workload** | Progressive JPEG decode at 1/2, 1/4 and 1/8 scale of a 12-megapixel 4:2:0 image (peak allocation), plus decode time of progressive lowzag versus baseline TJpgDec on an ESP32-S3 at 240 MHz for 800x480, 1600x1200 and 4000x3000 test cards. |
| **Metric** | memory |
| **Hardware** | ESP32-S3 at 240 MHz (timing table); unnamed aarch64 machine for the RSS table; peak_alloc figures are allocation sizes from lowzag's own sizing code, not tied to a CPU |
| **Adoption** | 1 star |
| **Last commit** | 2026-08-11 |
| **Links** | [repository](https://github.com/lowzag/lowzag) · [benchmark](https://github.com/lowzag/lowzag) |

## Verdict

On a generated 12 MP 4:2:0 progressive file, lowzag 2.3.0's own peak_alloc is 36.2 / 19.6 / 6.8 / 3.4 MB at 1/1, 1/2, 1/4 and 1/8 (pinned in CI by test/check_docs.py), against 36.1 MB computed for libjpeg-turbo's coefficient array (282,000 blocks x 128-byte JBLOCK); a separate process-RSS table (lowzag CLI vs djpeg -nosmooth, libjpeg-turbo 3.0.4, unnamed aarch64 machine) was measured on the first release (pjpeg 1.0.0, peak_alloc 36.2 / 23.0 / 8.9 / 3.6 MB) and never re-run, so it understates the current gap at 1/2 and 1/4. The ESP32-S3 at 240 MHz times (lowzag on a progressive file vs the ROM TJpgDec, which is fixed at JD_FASTDECODE=0, on a jpegtran baseline copy) are single 1.0.0-era runs: lowzag slower at 800x480 1/1 (0.63 vs 0.46 s) and faster at 4000x3000 1/4 (5.7 vs 9.1 s).

## Use it when

- Showing camera-size progressive JPEGs (several MP) on an ESP32-S3 or similar MCU with PSRAM, at 1/2 to 1/8 scale for a small panel
- Host-side thumbnailing of large progressive JPEGs where peak memory per decode matters more than throughput (at 1/4, 6.8 MB against libjpeg-turbo's 36.1 MB coefficient array for 12 MP 4:2:0)
- When you must refuse or size a decode before allocating: lowzag_estimate() returns the exact peak_alloc from the header alone, and mem_limit degrades instead of failing
- Streaming input (socket, SD card) that cannot be seeked or held in RAM, including partial files via cfg.allow_partial
- Cropping a region out of a big progressive frame: an 800x480 window of 12 MP costs 3.4 MB at 1/1

## Skip it when

- Baseline JPEG, arithmetic coding, 12-bit, CMYK/Adobe, lossless JPEG or 4:1:1 sampling: all refused
- Throughput on a host: no speed comparison against libjpeg-turbo exists, there is no SIMD, and progressive input costs a full entropy decode of every scan
- Full-scale (1/1) decodes: lowzag stores exactly what libjpeg stores (128.5 vs 128 bytes per block), so there is no memory saving
- Memory budgets in the tens of kilobytes: storage is still proportional to the source (8-byte map per source block, 2.26 MB floor at 12 MP); bitbank2/JPEGDEC decodes progressive at 1/8 in about 18 KB constant, per the lowzag README
- Byte-identical thumbnails to libjpeg's scaled IDCT or fancy upsampling: reduced scales use coefficient truncation and chroma replication

## How it is fast

The win is memory, not speed. A reduced-scale IDCT reads only the low-frequency bs x bs corner of each 8x8 block, so lowzag stores just that corner (64, 16, 4 or 1 coefficients, row-major since 2.3.0, written through a 64-entry zigzag-to-slot map) plus an 8-byte nonzero bitmap per block. The bitmap carries the T.81 G.1.2.3 nonzero history that AC successive-approximation refinement scans need to consume the right number of correction bits for the discarded coefficients, so every scan is still entropy-decoded in full. Dequantization, the 1/2/4/8-point Loeffler IDCT (Q13, int32 only), upsampling and color conversion run only on the kept corner, which is also why it overtakes ROM TJpgDec at 1/4 on large files.

## Compared with alternatives

Pick lowzag over libjpeg-turbo (or jpeg-nitro and zenjpeg, which target host decode speed) only when the input is progressive and peak memory at reduced scale is the binding constraint, typically on an MCU with PSRAM; for decode speed on a host, libjpeg-turbo remains the choice and lowzag publishes no comparison against it.

## Integration

| | |
|---|---|
| **Form** | source-drop (two files: src/lowzag.c and include/lowzag.h, plus optional src/lowzag_mem.c), or static/shared lib via CMake, or ESP-IDF component defensiblelogic/lowzag |
| **Dependencies** | none (the core object references only memcpy and memset; lowzag_decode_mem() adds malloc/free) |
| **Minimum toolchain** | C99; CMake 3.15+ for the CMake build; ESP-IDF 5.4.1 tested for the component |
| **Platforms** | any (portable C99, no SIMD, no 64-bit multiply); tested on x86-64 and aarch64 hosts and an ESP32-S3 board |
| **Thread safety** | No static or global mutable state, so concurrent decodes on separate threads are safe (ThreadSanitizer target in CI); a single decode is not reentrant and callbacks must not call back into lowzag |
| **Drop-in for the baseline** | no |

## Gotchas

- Every public struct needs struct_size set (use LOWZAG_CFG_INIT / LOWZAG_INFO_INIT / LOWZAG_ESTIMATE_INIT); a zero or stack-garbage value returns LOWZAG_ERR_VERSION or worse
- mem_limit is opt-in (0 means unlimited) and under automatic scale selection a tight limit silently lowers chroma resolution and then scale; check info.chroma_steps as well as info.scale
- Memory follows the source dimensions, not the output: a 48 MP source decoded to 1000x750 costs 13.5 MB against 6.8 MB from 12 MP
- A crop covering more than about 93% of a 12 MP frame costs more than no crop at 1/1, because it forces the 2.26 MB nonzero map

## Known shortcomings

- A memory metric rather than speed: peak_alloc is pinned by CI (test/check_docs.py) and the libjpeg 36.1 MB figure is computed, not measured; the measured RSS table (4,636 against 36,536 KiB at 1/8 scale, 7.9x derived) names no CPU or script. The ESP32 timing pits a progressive-file lowzag against the ROM TJpgDec on the baseline file in single runs and is slower at 800x480. Weak fit for a speed list.
- Enricher (e114, 2026-10-05): no correctness bug; the AC refinement loop matches libjpeg-turbo's logic. Two stale tables, neither inflating the claim: the RSS table (36,580 / 23,648 / 9,916 / 4,636 KiB) is identical to the first commit e4d11e4 (pjpeg 1.0.0, peak_alloc 36.2 / 23.0 / 8.9 / 3.6 MB) and was never re-run after 2.3.0 (19.6 / 6.8 / 3.4 MB), so the record's '7.9x RSS at 1/8' pairs a 1.0.0 measurement with the 2.3.0 table and understates the current gap; ESP32 times are also unchanged since e4d11e4. The ROM TJpgDec baseline is fixed at JD_FASTDECODE=0 (esp_jpeg README; level 2 is only about 12% faster). The GitHub description still says 3.6 MB. C stands.

## Caveats and trade-offs

A memory win, not a speed win, and a weak fit for a speed list. The headline table compares two different quantities (lowzag's info.peak_alloc against the coefficient array size libjpeg-turbo requests, computed from its 128-byte JBLOCK), as the README says; a separate measured RSS table in docs/ALGORITHM.md supports the gap (7.9x at 1/8, derived) but gives no CPU model, compiler or script. Memory still scales with source size (8-byte map per source block, 2.26 MB floor at 12 MP). The speed table compares different work: lowzag decodes a progressive file while ROM TJpgDec decodes the baseline-format version of it, and TJpgDec's 1/2 and 1/4 modes run the full IDCT; the figures are single measurements from one board, not reproducible on a host, and at 800x480 TJpgDec is faster. There is no host speed comparison against libjpeg-turbo. Progressive (SOF2, Huffman) JPEG only. Development is on a self-hosted GitLab with GitHub as a mirror (1 star). Commits list an AI co-author (Claude). The claim that mozjpeg, stb_image, Go image/jpeg and Rust jpeg-decoder also size progressive coefficient storage from the source dimensions comes from source reading (docs/PRIOR-ART.md), not measurement.

Progressive JPEG only, portable C99, decodes at 1/2, 1/4 or 1/8 scale without allocating the full coefficient array (keeps only the low-frequency corner its reduced IDCT needs); cropping and cancellation supported; ESP-IDF component. No arithmetic coding, CMYK or lossless JPEG; 8-bit, 1 or 3 components. Development is on a private GitLab with GitHub as mirror.

## Maintenance

Active (31 commits, 2.3.0 on 2026-08-11, every commit co-authored with Claude, 1 star, developed on a self-hosted GitLab with GitHub as mirror and no issues or PRs yet); MIT, two files, unusually thorough tests (differential vs djpeg, ASan/UBSan/TSan/MSan, libFuzzer) and an explicit SECURITY.md threat model.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers only: lowzag's peak_alloc figures are reproducible (pinned in CI by test/check_docs.py through lowzag_estimate on a generated 4000x3000 corpus file), but the libjpeg 36.1 MB figure is computed from 282,000 blocks x 128-byte JBLOCK, the process peak RSS table in docs/ALGORITHM.md (lowzag CLI vs djpeg, libjpeg-turbo 3.0.4) names no CPU model, compiler or script, and the ESP32-S3 timing table is three single measurements from one board with no harness.
- **Verifier notes:** Record numbers are accurate; I added the measured RSS table and labelled the TJpgDec comparison as progressive-vs-baseline-format work. Keep at C as a memory-metric entry with a weak-fit shortcoming.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** first-party tables
- **Pages the verifier opened:**
  - <https://github.com/lowzag/lowzag>
  - <https://github.com/lowzag/lowzag/commits>
  - <https://github.com/lowzag/lowzag/tree/main/test>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/README.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/docs/ALGORITHM.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/test/check_docs.py>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/CHANGELOG.md>
- **Sources the enricher read:**
  - <https://github.com/lowzag/lowzag>
  - <https://github.com/lowzag/lowzag/commits/main>
  - <https://github.com/lowzag/lowzag/commits/main/docs/ALGORITHM.md>
  - <https://github.com/lowzag/lowzag/issues?q=is%3Aissue>
  - <https://github.com/lowzag/lowzag/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/README.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/docs/ALGORITHM.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/docs/PRIOR-ART.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/idf_component.yml>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/include/lowzag.h>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/src/lowzag.c>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/src/lowzag_mem.c>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/test/check_docs.py>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/test/run_tests.py>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/test/Makefile>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/examples/README.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/examples/decode_to_ppm.c>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/examples/esp32/README.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/HEAD/examples/esp32/main/main.c>
  - <https://raw.githubusercontent.com/lowzag/lowzag/e4d11e4/docs/ALGORITHM.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/e4d11e4/README.md>
  - <https://raw.githubusercontent.com/lowzag/lowzag/a5e78f1/docs/ALGORITHM.md>
  - <https://raw.githubusercontent.com/espressif/idf-extra-components/master/esp_jpeg/README.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/lowzag/lowzag`) · [data/wave10/enrich/raw/github_com_lowzag_lowzag.json](../../../data/wave10/enrich/raw/github_com_lowzag_lowzag.json) (enrichment confidence 0.8)

</details>
