# ESP-NN

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (with Xtensa/PIE assembly)` · `Apache-2.0` · 🟢 active

> Espressif's int8 NN kernels in Xtensa/RISC-V PIE SIMD assembly for TFLite Micro, 1.4x to 20x over its ANSI C reference kernels.

| | |
|---|---|
| **Beats** | The library's own ANSI C reference kernels (selectable with the 'ANSI C' option under idf.py menuconfig NN_OPTIMIZATIONS) for TensorFlow Lite Micro int8 operators |
| **Claimed result** | ESP32-S3 (240 MHz): convolution in(10,10) filter 64x1x1x64 4,712,500 vs 331,008 ticks (14.24x); prelu (relu6) 1,125 vs 98 (11.48x); max pool 376,294 vs 48,069 (7.83x); fully connected 8,439 vs 1,543 (5.47x); softmax 15,209 vs 11,107 (1.37x). ESP32-P4 (360 MHz): max pool 482,184 vs 24,178 (19.94x); convolution 4,005,512 vs 572,459 (7.00x); hard_swish 703,970 vs 516,582 (1.36x). |
| **Workload** | Ticks per kernel call for int8 convolution, depthwise convolution, pooling, fully connected, softmax, prelu, hard_swish, mean and elementwise add/mul at fixed small shapes, ANSI C versus optimized assembly. |
| **Metric** | throughput |
| **Hardware** | ESP32-S3: 240 MHz, SPI QPI 80 MHz, 64 KB data cache; ESP32-P4: 360 MHz, SPI-RAM HEX 200 MHz, 128 KB L2 cache; ESP32-S31: 320 MHz, internal memory |
| **Compiler and flags** | -O2 -Wno-unused-function for the component (ESP32-S3 adds -mlongcalls -fno-unroll-loops), from CMakeLists.txt; compiler name and version not stated (ESP-IDF GCC toolchain assumed). |
| **Adoption** | 274 stars; kernel backend for TensorFlow Lite Micro on Espressif chips |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/espressif/esp-nn) · [benchmark](https://raw.githubusercontent.com/espressif/esp-nn/HEAD/README.md) |

## Verdict

Espressif's README reports single-call CPU-cycle counts of each int8 kernel against the library's own ANSI C reference kernel on the same chip and build (-O2, ESP-IDF GCC, version not stated): on a 240 MHz ESP32-S3, 1x1 conv 64-&gt;64 on a 10x10 map 4,712,500 vs 331,008 ticks (14.2x), relu6 11.5x, max pool 7.8x, fully connected 5.5x, softmax 1.4x; on a 360 MHz ESP32-P4, max pool 19.9x, conv 7.0x, hard_swish 1.4x. Outputs are checked bit-exact against the reference, but each number is one warm-cache call, and the model-level tables (Person Detection 2300 ms to 54 ms on S3) compare TFLite Micro with and without ESP-NN rather than the same C kernels.

## Use it when

- Running int8-quantized TFLite Micro models (person detection, MobileNet, YOLO-class) on ESP32-S3, ESP32-P4 or ESP32-S31, where the README shows 19x to 105x end-to-end invoke() speedups over plain TFLM kernels.
- Hand-calling int8 conv, depthwise, pooling or FC kernels from your own inference code or an AOT compiler on Espressif chips (issue #38 reports calling it directly without the TFLM interpreter).
- Layers with channel counts that are multiples of 8 or 16 and 16-byte-aligned tensors, which hit the vector fast paths.
- Dual-core S3/P4 designs that can spare the second core: esp_nn_dual_core_enable() cut MobileNetV3 Small on P4 from 388 ms to 253 ms in the README.

## Skip it when

- Any non-Espressif target: the speedups are tied to the S3 and P4/S31 PIE instruction sets; ESP32 and ESP32-C3 only get generic C optimisations.
- Float or int16 models: the library covers int8 (s8) operators only; u8 tests are commented out of the test app.
- When you need bit-exact TFLite reference output and plan to enable CONFIG_NN_SKIP_NUDGE, which trades +/-1 LSB requantization differences for speed.
- Max pool on ESP32-S3 with channel counts that are not multiples of 4: esp_nn_max_pool_s8 maps straight to the assembly kernel, which the source and tests mark as unsupported for that case.
- Safety-critical deployments that cannot absorb recent correctness churn: several layout-dependent kernel bugs were fixed between August and October 2026 and two related issues (#34, #40) are still open.

## How it is fast

On ESP32-S3 the hot loops are hand-written .S files using the LX7 PIE 128-bit vector extension (ee.vld/ee.vmax.s8/ee.vmin.s8 for pooling, 8- and 16-bit multiply-accumulate into the QACC/ACCX accumulators for conv and FC), with requantization (multiply_by_quantized_mult) also in assembly. ESP32-P4 and ESP32-S31 use C with inline PIE/QACC instructions (esp.vld.128 and friends). Convolutions go through im2col-style staging into 16-bit scratch panels, 1x1 and 3x3 specialisations, and filter panels sized to the configured data cache; an opt-in esp_nn_dual_core_enable() splits heavy kernels by output rows or channels across the second core.

## Compared with alternatives

Pick it over ESP-DSP (same vendor, same chips) when the workload is int8 quantized neural-network layers rather than float or int16 signal processing; unlike pqm4 or Qfplib it targets Espressif's PIE vector units rather than Cortex-M, so on an ESP32-S3/P4 running TFLite Micro it is the default choice rather than an alternative.

## Integration

| | |
|---|---|
| **Form** | static lib (ESP-IDF component, idf.py / component manager, version 1.4.1) |
| **Dependencies** | ESP-IDF (FreeRTOS for the optional dual-core worker); used with esp-tflite-micro for TFLite Micro models |
| **Minimum toolchain** | ESP-IDF 5.1+ (idf_component.yml) with the ESP-IDF GCC toolchain; component built at -O2 (S3 adds -mlongcalls -fno-unroll-loops) |
| **Platforms** | ESP32-S3 (Xtensa LX7 PIE assembly), ESP32-P4 and ESP32-S31 (RISC-V PIE; on S31 the PIE unit is on core 1 only), ESP32 and ESP32-C3 (generic C) |
| **Thread safety** | Not documented; scratch buffers are file-static pointers set by esp_nn_set_\*_scratch_buf, so concurrent calls of the same kernel from different tasks are not safe; the dual-core mode uses a single worker task and falls back to single core when called from the worker's core. |
| **Drop-in for the baseline** | partial — same signatures as the \*_ansi reference kernels and selected by menuconfig, but callers must size and set scratch buffers, and the S3 max pool needs channels that are a multiple of 4 |

## Gotchas

- Harness flaw behind the README kernel tables: tests/src/\*_test.c time one call of the ANSI kernel and then one call of the optimized kernel on the same freshly written buffers (single sample, no warm-up, warm data cache for both), so the 'External' (PSRAM) rows mostly measure cache-resident data; issue #20 (open since March 2025, unanswered) reports a fully connected layer running 5x slower inside esp-tflite-micro than in test_app on ESP32-S3 and suspects exactly this caching difference.
- Reproducing today gives different conditions from the tables: since 58ca1a4 (17 Sep 2026) test_app calls esp_nn_dual_core_enable() on S3 and P4, so split kernels (conv, depthwise, add, mul) run the optimized side on two cores against a single-core ANSI reference; pooling, relu6 and similar tests now print only per-suite sums rather than per-shape cycles; the S3 sdkconfig uses octal 80 MHz PSRAM while the README table says QPI 80 MHz. The kernel tables (April 2026, S31 and FC August 2026) predate the dual-core change, so they are single-core numbers.
- Recent correctness fixes in the measured kernels: S3 max pool dropped the activation_min clamp when channels % 8 == 4 (fixed e102c97, 7 Oct 2026); P4/S31 max pool wrote each pixel over the previous one when channels were not a multiple of 16 because unaligned 128-bit stores were disabled (fixed 8303c3b, 8 Oct 2026); P4 conv 1x1 raised an illegal-instruction fault on a misaligned filter pointer when the per-core PIE unaligned bits were unset (issue #40, fix 538d722, issue still open). The README shapes (16 channels, full -128..127 activation range, aligned buffers) do not hit these bugs, so the table ratios stand, but production layouts could.
- Issue #34 (open): ESP32-S3 per-channel fully connected gave memory-layout-dependent wrong logits in 1.1.x to 1.2.5; the maintainer traced it to input alignment and shipped a fix in 1.2.6, which the reporter has not confirmed. The PIE CFG register is per core and not saved per task, so other code on the core can clear the unaligned-access bits.

## Known shortcomings

- Numbers match (-O2 from CMakeLists.txt) but the compiler version is unstated and the kernel tables date from Apr 2026, before the Oct 7-8 2026 max-pool fixes (the P4 max-pool 19.94x was measured before its unaligned-store fix).
- Enricher: tests/src/\*_test.c time one warm-cache call each (ANSI C first, then optimised) on freshly written buffers; issue #20 (open) reports FC 5x slower inside esp-tflite-micro than in the test app; since 58ca1a4 (2026-09-17) the test app calls esp_nn_dual_core_enable() on S3/P4, so reruns put two cores against single-core ANSI (the README tables predate this); the pooling test prints only suite sums; the S3 max-pool clamp bug (e102c97) and the P4/S31 max-pool overwrite bug (8303c3b) both miss the README shapes; open #40 (P4 1x1 conv illegal instruction on a misaligned filter, fix 538d722) and #34 (S3 per-channel FC wrong logits in 1.1.x-1.2.5).

## Caveats and trade-offs

First-party table of tick (CPU cycle) counts; compiler version not stated. Harness: tests/src/\*_test.c call the ANSI and optimized kernel once each around profile_c_start/profile_opt_start and CHECK_EQUAL the outputs, so the optimized kernels must match the reference bit-exactly; single samples. Kernel tables were last refreshed in April 2026 (S3 and P4; fully connected Aug 2026, S31 Aug 2026) and predate the Sep 2026 S3 conv/FC/softmax perf work and the Oct 7-8 2026 correctness fixes (e102c97 S3 max pool activation_min when channels % 8 == 4; 8303c3b and 538d722 P4 PIE unaligned stores and access bits, which touch max pool); the P4 max pool 19.94x was measured before its unaligned-store fix (the S3 max pool test shape has 16 channels and is outside the %8==4 bug). ESP32-S3 kernels are largely hand-written .S files; P4/S31 kernels are mostly C with inline PIE assembly. Rows mix external (PSRAM) and internal memory placement. Model-level timings (Person Detection S3 2300 ms vs 54 ms, MobileNetV3, YOLO11n) compare TFLite Micro with and without ESP-NN, not asm against the same C.

Assembly versions are selected only on ESP32-S3, ESP32-P4 and ESP32-S31; ESP32 and ESP32-C3 get generic C optimizations instead. Chip-specific, not portable to desktop CPUs.

## Maintenance

Actively maintained by Espressif (219 commits, version 1.4.1, last commit 8 Oct 2026, 273 stars), Apache-2.0 and easy to vendor as an ESP-IDF component, but kernel tables predate the September 2026 S3 conv/FC/softmax tuning and the October 2026 max-pool and PIE alignment fixes, and issues #34 and #40 on layout-dependent faults are still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tick counts; per-kernel harness code is public (tests/src/\*_test.c time the ANSI and optimized kernel with profile_c_start/profile_opt_start and check outputs equal) and flags are in CMakeLists.txt, with chip and clock stated, but the compiler version is not given, so not A.
- **Verifier notes:** All claimed numbers match the README tables (S3 conv 14.24x, prelu 11.48x, max pool 7.83x, fully connected 5.47x, softmax 1.37x; P4 max pool 19.94x, conv 7.00x, hard_swish 1.36x). Shortcomings: compiler version unstated, single-sample timings, tables predate October 2026 max-pool correctness fixes. Apache-2.0, 274 stars, last commit 2026-10-08 confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-32 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/README.md>
  - <https://github.com/espressif/esp-nn>
  - <https://github.com/espressif/esp-nn/commits>
  - <https://github.com/espressif/esp-nn/commits/master>
  - <https://github.com/espressif/esp-nn/commits/master/README.md>
  - <https://github.com/espressif/esp-nn/tree/master/tests/src>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/tests/src/pooling_test.c>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/tests/src/convolution_test.c>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/tests/src/test_utils.c>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/tests/include/test_utils.h>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/espressif/esp-nn>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/README.md>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/Kconfig.projbuild>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/idf_component.yml>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/include/esp_nn.h>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/include/esp_nn_defs.h>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/include/esp_nn_esp32s3.h>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/include/esp_nn_multicore.h>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/src/common/esp_nn_multicore.c>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/src/convolution/esp_nn_conv_esp32s3.c>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/src/pooling/esp_nn_max_pool_s8_esp32s3.S>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/tests/include/test_utils.h>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/tests/src/test_utils.c>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/tests/src/pooling_test.c>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/tests/src/convolution_test.c>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/test_app/main/main.c>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/test_app/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/test_app/sdkconfig.defaults>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/test_app/sdkconfig.defaults.esp32s3>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/test_app/sdkconfig.defaults.esp32p4>
  - <https://raw.githubusercontent.com/espressif/esp-nn/HEAD/CONTRIBUTING.md>
  - <https://github.com/espressif/esp-nn/tree/master/test_app/main>
  - <https://github.com/espressif/esp-nn/commits/master>
  - <https://github.com/espressif/esp-nn/commits/master/README.md>
  - <https://github.com/espressif/esp-nn/commits/master/test_app/main/main.c>
  - <https://github.com/espressif/esp-nn/commit/e102c97>
  - <https://github.com/espressif/esp-nn/commit/8303c3b>
  - <https://github.com/espressif/esp-nn/issues>
  - <https://github.com/espressif/esp-nn/issues/20>
  - <https://github.com/espressif/esp-nn/issues/34>
  - <https://github.com/espressif/esp-nn/issues/40>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/espressif/esp-nn`) · [data/wave13/enrich/raw/github_com_espressif_esp_nn.json](../../../data/wave13/enrich/raw/github_com_espressif_esp_nn.json) (enrichment confidence 0.8)

</details>
