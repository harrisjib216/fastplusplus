# aes-armcortexm (Schwabe and Stoffelen, Cortex-M3/M4 AES assembly)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly (ARM Thumb-2) with C wrappers` · `CC0-1.0` · 🔴 abandoned

> Hand-scheduled Thumb-2 AES-128/192/256 (T-table CTR, bitsliced and masked) for Cortex-M3/M4; about 33 cycles/byte AES-128-CTR.

| | |
|---|---|
| **Beats** | RIOT OS default C AES implementation (third-party forum report); the SAC 2016 paper compares against unnamed prior Cortex-M AES implementations; the repo README names no baseline |
| **Claimed result** | Snippet only (page not opened, egress blocked): RIOT forum post reports assembler version 45 us per encode and 87 us per decode against 74 us and 131 us for RIOT's default implementation on an STM32L151 (derived from snippet: about 1.6x encrypt, 1.5x decrypt). Paper abstract (snippet only): 'about twice as fast as existing implementations'. Repo README: absolute cycles only (see workload), no baseline. |
| **Workload** | AES-128 single-block encryption and decryption latency in microseconds on an STM32L151 (Cortex-M3) after integration into RIOT OS, per a forum post seen only as a search snippet; the repo README itself gives cycle counts for the assembly only (AES-128 single block 637.5 cycles on Cortex-M3 STM32L100C, 634.7 on Cortex-M4 STM32F407; AES-128 CTR 531.8 / 527.9 cycles per block; averaged over 4096 bytes and 10000 runs). |
| **Metric** | latency |
| **Hardware** | STM32L151 (Cortex-M3) for the forum numbers; STM32L100C (Cortex-M3) and STM32F407 (Cortex-M4) development boards for the README table |
| **Compiler and flags** | README cycle counts: arm-none-eabi-gcc (version unstated) with libopencm3, -O3 -mthumb -mcpu=cortex-m3 -msoft-float for the STM32L100C (M3) builds and -O3 -mthumb -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16 for the STM32F407 (M4) builds, per aes128ctr/Makefile; the RIOT forum timings state no compiler or flags in the snippet. |
| **Adoption** | 97 stars; integrated into RIOT OS per a forum post (snippet); jnk0le/cortexm-AES says its CM3_1T implementation is originally based on this code |
| **Last commit** | 2020-07-12 |
| **Links** | [repository](https://github.com/Ko-/aes-armcortexm) · [benchmark](https://forum.riot-os.org/t/aes-crypto-optimizations-speed-and-size/2140) |

## Verdict

The repo README reports cycle counts only: AES-128-CTR 531.8 cycles per block on a Cortex-M3 (STM32L100C, 16 MHz, 0 wait states) and 527.9 on a Cortex-M4 (STM32F407, 24 MHz, 0 wait states), single-block AES-128 encryption 637.5/634.7 cycles, built with arm-none-eabi-gcc -O3 and libopencm3, with no baseline on the page. The only baseline comparisons, a RIOT forum post (45/87 us encrypt/decrypt against 74/131 us for RIOT's default C AES on an STM32L151) and the SAC 2016 abstract's 'about twice as fast as existing implementations', were seen as search snippets only.

## Use it when

- Bulk AES-128/192/256-CTR on Cortex-M3 or M4 where timing side channels are outside the threat model: README measures 531.8 (M3) and 527.9 (M4) cycles per 16-byte block for AES-128-CTR, 651 and 767 cycles for AES-192/256.
- Low-clock MCUs running flash at zero wait states (the README numbers were taken at 16 MHz on an STM32L100C and 24 MHz on an STM32F407), where the measured cycle counts carry over.
- Research or evaluation that needs a first-order masked AES-128-CTR on an STM32F4-class Cortex-M4.
- Firmware that wants public-domain (CC0) AES assembly to vendor without licence obligations, or a reference for counter-mode caching and T-table scheduling on ARMv7-M.

## Skip it when

- You need output that interoperates with standard AES-CTR or GCM: the counter is the first 32-bit word of the block, incremented little-endian, followed by the nonce, so results differ from NIST SP 800-38A vectors from the second block on (maintainer, issue #1).
- Constant time matters: the T-table variants are explicitly not constant-time, and for constant-time AES on Cortex-M the fixsliced aadomn/aes (84.3 cycles/byte AES-128 on M3) is faster than this repo's bitsliced CTR (1618.6 cycles per block, about 101 cycles/byte, derived from page data).
- Full-speed clocks with flash wait states (e.g. STM32F4 at 168 MHz): the T-table sits in flash next to the code and no measurement at those settings is published; jnk0le/cortexm-AES warns that unrolled code can lose to looped code under STM32F4 ART cache pressure and wait states.
- Cores other than Cortex-M3/M4 (M0/M0+ lack Thumb-2; M7 has caches and different timing), or anyone needing a maintained library with tests and CBC/GCM modes: the repo is abandoned since 2020, while jnk0le/cortexm-AES (derived from this code) offers SP 800-38A-compliant big-endian CTR and GCM.
- Streaming encryption across several calls unless you manage the counter yourself (see gotchas).

## How it is fast

The fast variants use a single 1 KB T-table (Te0) and fold the other three table rotations into the barrel shifter of the EOR instructions, with fully unrolled rounds, hand register allocation and instruction scheduling produced by the authors' own scheduler tool (scheduler/). The CTR code adds counter-mode caching (based on Hongjun Wu's eSTREAM implementation, per the maintainer in issue #1): the parts of rounds 1 and 2 that depend only on the nonce and upper counter bytes are computed once per 256 blocks and only the changing low counter byte is processed per block. The constant-time variant uses a bitsliced representation (the SAC slides call it bytesliced) and the masked variant adds first-order masking with randomness from the STM32F407 hardware RNG.

## Compared with alternatives

Pick this over aadomn/aes when raw speed matters more than constant time (T-table CTR at about 33 cycles/byte against about 84 cycles/byte for fixsliced AES-128 on M3), and over pqm4-style portable C or CRYPTOGAMS when you are on a Cortex-M3/M4 and want CC0 code; pick aadomn/aes whenever side-channel resistance is required.

## Integration

| | |
|---|---|
| **Form** | source-drop (GNU as Thumb-2 .s files with C example harnesses) |
| **Dependencies** | none for the .s files; the example harnesses need libopencm3 (git submodule) and the arm-none-eabi toolchain; the masked variant needs the STM32F407 hardware RNG |
| **Minimum toolchain** | arm-none-eabi-gcc/GNU as with unified Thumb-2 syntax (version not documented); Makefiles use -O3 -mthumb -mcpu=cortex-m3 or cortex-m4 |
| **Platforms** | ARMv7-M only: Cortex-M3 (measured on STM32L100C) and Cortex-M4 (measured on STM32F407); masked variant M4/STM32F407 only |
| **Thread safety** | not documented; the routines keep state only in caller-supplied buffers and the stack, but AES_128_encrypt_ctr writes the counter back into the caller's param struct, so a param must not be shared between concurrent calls |
| **Drop-in for the baseline** | no |

## Gotchas

- Counter not advanced past the last block: AES_128_encrypt_ctr (prototype says param const \*) stores the incremented counter back into param, but exits before incrementing after the final block, so a second call continues with the counter of the previous call's last block and reuses that keystream block; a 16-byte call does not advance it at all. Open PR #6 (2023, unmerged, aes256ctr only) moves the increment before the exit. Set param.ctr = start + number_of_blocks yourself between calls.
- Whole blocks only, word-aligned buffers: the loop always loads and stores 16 bytes with LDM/STM, so a length that is not a multiple of 16 reads past the end of the input and writes up to 15 bytes past the output (the example sizes its output buffer with LEN_ROUNDED), and in/out must be 4-byte aligned on ARMv7-M.
- Benchmark conditions: the README's cycle counts were taken at 16 MHz (STM32L100C) and 24 MHz (STM32F407, PLL chosen 'low to have 0WS') with zero flash wait states, and the T-table lives in flash with the code; at production clocks with wait states and the F4 ART data cache enabled, cycles per block rise and table lookups may become timing-dependent.
- Harness gap: the in-repo examples time one call with a fixed key, nonce and input (cycles read from DWT_CYCCNT) and have their ciphertext printing commented out with no known-answer check; the README's '10000 runs with random inputs, nonces, and keys' averaging loop is not in the repository, so the published averages cannot be re-run from the repo as shipped. Issue #1 (2017) found the bitsliced CTR producing wrong output, fixed in commit 45103cb; issue #3 (2018) found the bitsliced and masked code storing temporaries below the stack pointer (interrupt-unsafe), fixed July 2018, after the 2016 measurements.

## Known shortcomings

- README gives only cycle counts with no baseline; the RIOT forum numbers (45 vs 74 us) and the SAC 2016 paper's 'about twice as fast' are snippet only (forum, eprint and sacworkshop hosts blocked); paper-access retier could lift it to B. CC0; abandoned since 2020-07-12.
- Enricher: AES_128_encrypt_ctr writes the counter back to its const-declared parameter but not past the last block, so the next call reuses the last keystream block and a 16-byte call never advances (fix in open PR #6, aes256ctr only); the counter is the first word in little-endian, so output does not match SP 800-38A vectors (#1); whole 16-byte blocks and word-aligned buffers required. Harness: one timed call with a fixed key and input, no known-answer check, the README's '10000 random runs' loop is not in the repo; 16/24 MHz clocks, 0 wait states, T-table in flash.

## Caveats and trade-offs

The repo README has absolute cycle numbers but compares against nothing, and does not mention reference C AES or mbedTLS. The two comparison datapoints (RIOT forum timings, 'about twice as fast' in the SAC 2016 paper 'All the AES You Need on Cortex-M3 and M4') come from search-result snippets only: eprint.iacr.org, ko.stoffelen.nl, sacworkshop.org (slides) and forum.riot-os.org all fail to resolve here (getaddrinfo ENOTFOUND), so tier is capped at C and the paper's comparison table was not read; a verifier with paper access should check whether it supports B (the slides list it as the fastest T-table AES-CTR and bytesliced AES-128-CTR on these cores). The forum post gives no compiler flags or clock speed in the snippet. Makefiles are public (-O3, arm-none-eabi-gcc, version unstated). Repo is old (last commit 2020-07-12, 'Fix push wrong changes to aes128ctr'); CC0 dedication has no patent grant. Later Cortex-M AES work exists (jnk0le/cortexm-AES, whose CM3_1T code is based on this repo, and aadomn/aes fixslicing) and was not compared here. The T-table implementations are not constant-time (only the bitsliced variants are). [retier] Enricher: AES_128_encrypt_ctr does not advance the counter past the last block (keystream reuse across calls; fix in open PR #6); little-endian first-word counter does not match SP 800-38A (#1); the harness is one timed call with no known-answer check.

Fully unrolled code (about 2 KB code for AES-128 block, 1 KB T-table data; ROM can be reduced at small cost); the fast table-based variants are not advertised as constant time (the separate bitsliced constant-time AES-128-CTR, about 1617 cycles per block, and a first-order masked variant for M4 are); the masked variant needs a hardware RNG and is STM32F407 specific; Cortex-M3/M4 only, GNU as Thumb-2 syntax, build uses libopencm3 submodule.

## Maintenance

Abandoned (last commit 2020-07-12; open PRs #5 from 2020 and #6 from 2023 unreviewed) but CC0 and small enough to vendor, so copyable, provided you fix the counter handoff, keep buffers padded and aligned, and accept the non-standard counter layout.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The only baseline comparison (RIOT forum: 45/87 us against 74/131 us for RIOT's default C AES on an STM32L151) could not be opened (forum.riot-os.org, eprint.iacr.org and sacworkshop.org all fail with getaddrinfo ENOTFOUND), so it rests on search snippets; the repo README gives absolute cycle counts with public Makefile flags but no baseline, and the SAC 2016 paper's 'about twice as fast as existing implementations' was seen in an abstract snippet only, without its comparison table.
- **Verifier notes:** Real SAC 2016 artifact (CC0, 97 stars, last commit 2020-07-12, abandoned) with public Makefile flags and README cycle counts, but every baseline comparison sits behind hosts unreachable from this container; kept at C. A paper-access retier could lift it to B if the SAC 2016 table names the prior implementations it beats.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-123 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/Ko-/aes-armcortexm>
  - <https://github.com/Ko-/aes-armcortexm/commits>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/aes128ctr/Makefile>
- **Sources the enricher read:**
  - <https://github.com/Ko-/aes-armcortexm>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/aes128ctr/Makefile>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/aes128ctr/aes_128_ctr.c>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/aes128ctr/aes_128_ctr.s>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/aes128/aes.c>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/common/stm32f4_wrapper.c>
  - <https://raw.githubusercontent.com/Ko-/aes-armcortexm/HEAD/common/stm32l1_wrapper.c>
  - <https://github.com/Ko-/aes-armcortexm/tree/master/aes128ctr>
  - <https://github.com/Ko-/aes-armcortexm/tree/master/common>
  - <https://github.com/Ko-/aes-armcortexm/tree/public/aes128>
  - <https://github.com/Ko-/aes-armcortexm/issues?q=is%3Aissue>
  - <https://github.com/Ko-/aes-armcortexm/issues/1>
  - <https://github.com/Ko-/aes-armcortexm/issues/3>
  - <https://github.com/Ko-/aes-armcortexm/pulls?q=is%3Apr>
  - <https://github.com/Ko-/aes-armcortexm/pull/2>
  - <https://github.com/Ko-/aes-armcortexm/pull/5>
  - <https://github.com/Ko-/aes-armcortexm/pull/6>
  - <https://github.com/Ko-/aes-armcortexm/pull/6/files>
  - <https://raw.githubusercontent.com/jnk0le/cortexm-AES/HEAD/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/ko-/aes-armcortexm`) · [data/wave13/enrich/raw/github_com_ko_aes_armcortexm.json](../../../data/wave13/enrich/raw/github_com_ko_aes_armcortexm.json) (enrichment confidence 0.75)

</details>
