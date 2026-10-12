# ESP-DSP

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (with Xtensa and RISC-V assembly)` · `Apache-2.0` · 🟢 active

> Espressif's official DSP component: hand-written Xtensa/RISC-V assembly kernels for ESP32, ESP32-S3 and ESP32-P4 beating its own ANSI C versions.

| | |
|---|---|
| **Beats** | The library's own non-optimized ANSI C implementations of the same DSP functions (the 'ANSI Xtensa' and 'ANSI Risc-V' columns), built with the same toolchain at -O2 and -Os |
| **Claimed result** | Page values (CPU cycles, -O2): ESP32-S3 asm vs the table's 'ANSI Xtensa' column: dsps_dotprod_f32 N=256 432 vs 1311 (3.0x), dsps_dotprod_s16 307 vs 3635 (11.8x), dsps_fft2r_sc16 1024 points 15,623 vs 221,955 (14.2x), dsps_fir_f32 1024 samples/256 coeffs 443,671 vs 1,353,122 (3.0x), dsps_fft2r_fc32 1024 points 97,847 vs 175,729 (1.8x) (all derived from page data). The 'ANSI Xtensa' column holds the ESP32's ANSI values (build_bm_table.py writes ESP32 and ESP32-S3 ANSI results into the same column and the ESP32 rows come last in docs/esp_bm_results.csv); the S3's own same-chip ANSI values in that CSV give dotprod_f32 432 vs 1311 (3.0x), dotprod_s16 307 vs 2864 (9.3x), fft2r_sc16 1024 15,623 vs 214,764 (13.7x), fir_f32 443,671 vs 1,350,660 (3.0x), fft2r_fc32 1024 97,847 vs 174,698 (1.8x) (derived from page data). ESP32-P4 dsps_dotprod_s16 208 vs 3385 ANSI Risc-V (16.3x, derived). Rows with no gain or a loss: ESP32 dsps_fir_f32 1,078,691 vs 1,353,122 (1.25x), ESP32-P4 dsps_fir_f32 1,606,563 vs 1,606,552 (parity), ESP32 dsps_fft2r_sc16 1024 points 226,154 vs 221,955 (asm slower), ESP32-P4 dspm_mult_3x3x3_f32 338 vs 309 and dspm_mult_4x4x4_f32 658 vs 608 (asm slower at -O2), ESP32 dspi_dotprod image rows equal to ANSI (no ESP32 asm path). |
| **Workload** | CPU cycles per call for dot products (N=256), FIR/decimating FIR (1024 samples, 256 coefficients), radix-2/radix-4 float FFTs and 16-bit fixed-point FFTs (64 to 1024 points) and a biquad IIR (1024 samples): optimized assembly per chip versus the ANSI C version. |
| **Metric** | throughput |
| **Hardware** | ESP32 and ESP32-S3 (Xtensa) and ESP32-P4 (RISC-V); values are CPU cycle counts, clock speed not stated |
| **Compiler and flags** | ESP-IDF compiler optimization settings: CONFIG_COMPILER_OPTIMIZATION_PERF (the 'O2' columns) and CONFIG_COMPILER_OPTIMIZATION_SIZE (the 'Os' columns); compiler name and version not stated (ESP-IDF GCC toolchain assumed). |
| **Adoption** | 715 stars; official Espressif DSP component for ESP-IDF |
| **Last commit** | 2026-05-11 |
| **Links** | [repository](https://github.com/espressif/esp-dsp) · [benchmark](https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/docs/en/esp-dsp-benchmarks.rst) |

## Verdict

First-party cycle counts (docs/esp_bm_results.csv, rendered to esp-dsp-benchmarks.rst) for each chip's assembly against the same library's ANSI C, built with ESP-IDF GCC at -O2 or -Os (compiler version unstated), one timed call each. Same-chip ratios at -O2: ESP32-S3 dotprod_f32 3.0x, FIR 3.0x, fft2r_fc32 1024 1.79x, fft2r_sc16 1024 13.7x, dspm_mult_f32 16x16 8.4x. ESP32 FFTs 1.55-1.63x, FIR 1.25x, sc16 FFT 0.98x. ESP32-P4 dotprod_s16 16.3x, sc16 FFT 13.1x, float FFT 1.11x, FIR 1.0x (derived from page data).

## Use it when

- ESP32-S3 float FIR, decimating FIR and dot products: about 3.0x fewer cycles than the same-chip ANSI build (dsps_fir_f32 1024 samples x 256 taps 443,671 vs 1,350,660 cycles at -O2).
- 16-bit fixed-point work on ESP32-S3 or ESP32-P4: radix-2 sc16 FFT about 13-14x, dsps_dotprod_s16 9.3x (S3) and 16.3x (P4), 16x16 dspm_mult_s16 about 28x versus same-chip ANSI.
- Classic ESP32 float FFTs (1.55x radix-2, 1.63x radix-4 at 1024 points), biquad IIR (1.53x) and 16-bit dot products (8.3x).
- ESP-IDF projects (IDF 4.2+) that want an Apache-2.0, vendor-maintained component with an ANSI fallback for other Espressif chips and a menuconfig switch to the ANSI build for verification.

## Skip it when

- Float work on ESP32-P4: dsps_fir_f32 has no P4 assembly (the header maps it to dsps_fir_f32_ansi), the radix-2 float FFT gains only 1.11x, and open issue #119 reports dsps_fft2r_fc32_arp4 corrupting output or taking a load access fault with interrupts active (the reporter switched to ANSI at about 7% cost).
- Low-level fixed-point spectra on ESP32-S3 (SDR noise floors, near-DC analysis): issue #123 reports dsps_fft2r_sc16_aes3 truncating each butterfly term separately, giving a one-sided noise ramp near DC that the ANSI and ESP32 kernels do not show.
- Tiny fixed-size float matrix products on ESP32-P4 (3x3x3 338 vs 309 cycles, 4x4x4 658 vs 608 for ANSI) and 16-bit FFTs on the classic ESP32 at -O2 (226,154 vs 221,955 cycles at 1024 points).
- Buffers you cannot align to 16 bytes on ESP32-S3: misaligned inputs take slower fallback paths, and issue #120 reports dsps_add/sub/mul s8/s16 aes3 writing out of bounds when only the output is misaligned.
- Non-Espressif targets: elsewhere only the ANSI C code runs, so there is no speed advantage.

## How it is fast

On the classic ESP32 the kernels use Xtensa zero-overhead hardware loops and, for 16-bit work, the MAC16 multiply-accumulate unit (the platform headers gate them on XCHAL_HAVE_LOOPS and XCHAL_HAVE_MAC16). The ESP32-S3 variants use the chip's 128-bit SIMD instructions (EE.LDF.128.IP loads in the FIR kernels, 128-bit vector butterflies in the 16-bit FFT), and the ESP32-P4 variants use the esp.lp.setup zero-overhead loop, with the P4 16-bit FFT sharing the S3 kernel's structure. The baseline is the library's own plain scalar ANSI C built by the same toolchain, so the largest gains are on 16-bit fixed-point and SIMD-friendly float kernels.

## Compared with alternatives

ESP-NN is the same vendor's int8 neural-network kernel set for TFLite Micro with the same ANSI-baseline style; pick ESP-DSP for classic signal processing (FIR/IIR, FFT, dot products, matrix math) on ESP32-family chips. pqm4, Qfplib-M0 and the Pico SDK float routines target Arm Cortex-M, so they are not alternatives on Espressif silicon.

## Integration

| | |
|---|---|
| **Form** | static lib (ESP-IDF component built from source; install with idf.py add-dependency espressif/esp-dsp) |
| **Dependencies** | ESP-IDF &gt;= 4.2 (FreeRTOS, newlib) per idf_component.yml; no third-party libraries |
| **Minimum toolchain** | ESP-IDF 4.2+ with its bundled Xtensa/RISC-V GCC; CI builds IDF 5.3, latest and a Clang job; C, with C++ for the EKF and Mat classes |
| **Platforms** | Assembly for ESP32, ESP32-S3 (Xtensa) and ESP32-P4, ESP32-S31 (RISC-V); ANSI C on other Espressif chips and a Linux target for tests |
| **Thread safety** | Not documented; filter state lives in caller-owned structs, FFTs share global twiddle tables set up by the init calls, and issue #119 suggests the P4 hardware-loop kernels may not survive interrupts on some IDF versions |
| **Drop-in for the baseline** | partial: optimized and _ansi variants share signatures and the plain names switch via menuconfig, but S3 kernels expect 16-byte alignment and coefficient counts divisible by 4, and some optimized kernels round differently from ANSI |

## Gotchas

- Harness best case: test/prepare_csv_benchmarks.c times one call after two warm-up calls with interrupts masked, on memalign(16) buffers that are never initialised. Outputs are not checked; the FIR row even writes its output into its own delay line. Masking interrupts hides the P4 hardware-loop fault in #119, and the 16-byte alignment hides the S3 slow paths and the add/sub/mul overrun in #120.
- Several optimized kernels did not, or still do not, match ANSI output: dsps_fird_f32_aes3 gave wrong results and read 4 floats past the delay line on unaligned delay positions until commit 0412ab5 (Dec 2025, PR #110); P4 fird shows delay-position drift in open issue #117; S3 sc16 FFT truncation bias is in #123. The benchmark table was last regenerated 2025-03-18 (commit 972c4e9), before that fird fix and before the P4 sc16 FFT buffer-overrun fix (375e2fe, 2025-04-28).
- Table labelling: the 'ANSI Xtensa' column holds the ESP32's ANSI run, so ESP32-S3 ratios read from the page are cross-chip (same-chip S3 dotprod_s16 is 9.3x, not 11.8x). The 'ESP32P4' fir_f32 cell is the ANSI function timed twice. On S3, dsps_dotprod_s16 and dsps_dotprode_f32 still dispatch to the ESP32 ae32 code.
- FFT rows time only the in-place butterfly kernel: bit reversal (dsps_bit_rev_fc32 maps to the ANSI version even in optimized builds) and complex-to-real conversion are separate calls. On P4/S31 the fixed-size matrix macros expand with a trailing semicolon (dspm_mult_f32(A,B,C,3,3,3);), so they cannot sit before an else.

## Known shortcomings

- Numbers match but the 'ANSI Xtensa' column holds ESP32 ANSI values (build_bm_table.py overwrites the S3 value, so S3 ratios are cross-chip); same-chip ratios from docs/esp_bm_results.csv are lower (dotprod_s16 9.3x, not 11.8x); some rows are losses (P4 3x3x3/4x4x4 matmul, ESP32 fft2r_sc16); compiler version unstated; each value is one timed call.
- Enricher: one timed call with interrupts masked on memalign(16) uninitialised buffers with outputs unchecked and the FIR output aliasing the delay line; the masking hides #119 (P4 dsps_fft2r_fc32_arp4 corruption with interrupts; ANSI only about 7% slower) and the alignment hides the S3 slow paths and the #120 OOB write; the ESP32P4 fir_f32 cell times ANSI twice (the header maps dsps_fir_f32 to _ansi); the table was regenerated 2025-03-18, before the fird_f32_aes3 wrong-output/OOB-read fix 0412ab5 (PR #110) and the P4 sc16 FFT overrun fix 375e2fe; the headline S3 sc16 FFT 13.7x row has a truncation bias (#123, not bit-equal to ANSI); open #117 P4 fird position drift.

## Caveats and trade-offs

First-party table; compiler name and version not stated. Harness (test/prepare_csv_benchmarks.c, REPORT_BENCHMARK_CSV in test/report.inc) makes one warm-up call, then times a single call with interrupts masked using the CPU cycle counter, so each value is one sample; the page itself points to test/test_dsp.c. The 'ANSI Xtensa' column is the ESP32's ANSI run, so ESP32-S3 ratios against it are cross-chip; the S3's own ANSI numbers are in docs/esp_bm_results.csv and give slightly lower ratios (dotprod_s16 9.3x instead of 11.8x). Several rows show no gain or a loss (ESP32 fft2r_sc16, ESP32-P4 fir_f32, ESP32-P4 3x3x3 and 4x4x4 matrix multiply, ESP32 image dot products). The README says many functions are written in assembly; ANSI C reference implementations are the baseline, not an outside library.

Assembly is per chip (ESP32, ESP32-S3, ESP32-P4); other targets fall back to ANSI C. Gains depend heavily on chip and function. Embedded targets only, not usable on desktop CPUs.

## Maintenance

Actively maintained (v1.8.2, 2026-05-11) official Espressif Apache-2.0 component and safe to vendor, but 32 open issues include several unanswered correctness reports against the optimized S3/P4 kernels (#117, #119, #120, #123), so check optimized output against the DSP_ANSI build before shipping.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party cycle-count table; the harness is public (test/prepare_csv_benchmarks.c with the REPORT_BENCHMARK_CSV macro in test/report.inc, raw data in docs/esp_bm_results.csv, table built by docs/build_bm_table.py) and the chips are named, but the compiler name and version are not stated, so not A.
- **Verifier notes:** All claimed numbers appear on the benchmarks page and the ratios check out, but the 'ANSI Xtensa' baseline column is the ESP32's ANSI run (build_bm_table.py overwrites the S3 value), so S3 ratios are cross-chip; same-chip ratios from docs/esp_bm_results.csv were added. Apache-2.0, 715 stars, last commit 2026-05-11 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-32 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/docs/en/esp-dsp-benchmarks.rst>
  - <https://github.com/espressif/esp-dsp>
  - <https://github.com/espressif/esp-dsp/commits>
  - <https://github.com/espressif/esp-dsp/tree/master/test>
  - <https://github.com/espressif/esp-dsp/tree/master/docs>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/test/prepare_csv_benchmarks.c>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/test/report.inc>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/test/test_dsp.c>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/test/CMakeLists.txt>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/docs/build_bm_table.py>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/docs/esp_bm_results.csv>
- **Sources the enricher read:**
  - <https://github.com/espressif/esp-dsp/commits/master>
  - <https://github.com/espressif/esp-dsp/commits/master/docs/esp_bm_results.csv>
  - <https://github.com/espressif/esp-dsp/commits/master/docs/en/esp-dsp-benchmarks.rst>
  - <https://github.com/espressif/esp-dsp/commit/0412ab5>
  - <https://github.com/espressif/esp-dsp/commit/375e2fe>
  - <https://github.com/espressif/esp-dsp/issues>
  - <https://github.com/espressif/esp-dsp/issues?q=fird>
  - <https://github.com/espressif/esp-dsp/pull/110>
  - <https://github.com/espressif/esp-dsp/issues/68>
  - <https://github.com/espressif/esp-dsp/issues/117>
  - <https://github.com/espressif/esp-dsp/issues/119>
  - <https://github.com/espressif/esp-dsp/issues/120>
  - <https://github.com/espressif/esp-dsp/issues/123>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/README.md>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/idf_component.yml>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/Kconfig>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/docs/en/esp-dsp-benchmarks.rst>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/docs/build_bm_table.py>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/docs/esp_bm_results.csv>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/test/prepare_csv_benchmarks.c>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/test/report.inc>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/test/test_dsp.c>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/modules/fir/include/dsps_fir.h>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/modules/fir/include/dsps_fir_platform.h>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/modules/fft/include/dsps_fft2r.h>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/modules/fft/include/dsps_fft2r_platform.h>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/modules/matrix/mul/include/dspm_mult.h>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/modules/matrix/mul/include/dspm_mult_platform.h>
  - <https://raw.githubusercontent.com/espressif/esp-dsp/HEAD/modules/dotprod/include/dsps_dotprod.h>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/espressif/esp-dsp`) · [data/wave13/enrich/raw/github_com_espressif_esp_dsp.json](../../../data/wave13/enrich/raw/github_com_espressif_esp_dsp.json) (enrichment confidence 0.75)

</details>
