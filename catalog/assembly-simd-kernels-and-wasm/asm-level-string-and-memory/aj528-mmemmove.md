# mmemmove (AJ528): memmove in ARM Cortex-M assembly

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `ARM Thumb assembly (Cortex-M4 and M0+) with a C test harness` · `GPL-3.0` · 🟡 stale

> Hand-written Thumb-1 memmove for Cortex-M0+/M4 that beats newlib-nano's byte-loop memmove; separate memmove_() symbol.

| | |
|---|---|
| **Beats** | newlib generic memmove.c (byte loop under -Os; newlib ARM ships no assembly memmove) |
| **Claimed result** | 'In my testing, memmove_() is always faster than my standard memmove(). Sometimes it's only a few cycles faster, other times it is 7x faster.' Object size 'under 230 bytes' on arm-none-eabi-gcc. |
| **Workload** | common/src/main.c (Greatest tests) times one warm call of each function with the DWT cycle counter after a single untimed call. Sizes are 1, 10, 20 and 50 bytes at source offset 0x81 with destinations 0x7E, 0x82 and 0x102. Slide tests use 15, 21, 34, 512 and 513 bytes against overlapping and non-overlapping destinations. An iterate test up to 35 bytes checks correctness only. Cycle counts are printed over UART and none are committed; the README does not say which size or core gave the 7x. |
| **Metric** | latency |
| **Hardware** | STM32WLxx (Cortex-M4 core); README says the code is designed for Cortex-M4 and M0+ and probably works on other ARMv6-M and ARMv7-M cores |
| **Compiler and flags** | arm-none-eabi-gcc (version not stated). Committed Makefiles use -mcpu=cortex-m4 (or the cm0plus equivalent) -mthumb -mfloat-abi=soft --specs=nano.specs -fno-builtin -std=gnu17 -ffunction-sections -fdata-sections, with debug = 1 so OPTIMIZE_FLAGS is -O0 -ggdb3 (-O2 when debug = 0). The flags behind the README claim are not stated. The -O0 setting affects the C harness, not the hand-written assembly or the prebuilt libc memmove. |
| **Adoption** | 0 stars |
| **Last commit** | 2025-02-24 |
| **Links** | [repository](https://github.com/AJ528/mmemmove) · [benchmark](https://github.com/AJ528/mmemmove) |

## Verdict

The author reports that memmove_() was always faster than the toolchain memmove on an STM32WL55 (Cortex-M4 at 48 MHz, flash at 2 wait states, with the Cortex-M0+ core also testable), from 'a few cycles' up to 7x, timed with the DWT cycle counter around one warm call per case; the baseline is very likely newlib-nano's byte-loop memmove (both Makefiles use --specs=nano.specs), compiler version, core and copy size for the 7x are not stated, and no results are committed.

## Use it when

- Cortex-M0/M0+ firmware linked against newlib-nano (--specs=nano.specs) where memmove sits on a hot path, e.g. ring buffers, packet reassembly or in-place shifts of arrays
- Co-aligned moves of 16 bytes or more (word-aligned structs or buffers shifted by a multiple of 4 bytes): only these hit the word loop, which is where the largest gains should come from
- Code-size-constrained parts: the routine is under 230 bytes per the README, roughly the size of a small C memmove
- Cortex-M4/M3 projects that also use newlib-nano's memmove (which has no assembly fast path), as long as GPL-3.0 is acceptable

## Skip it when

- Proprietary firmware that cannot ship GPL-3.0 code: the licence is copyleft and the file would be linked into the image
- Misaligned copies (dest - src not a multiple of 4): the code never does unaligned or shift-and-merge word accesses, so these stay byte-at-a-time with only 4x unrolling and the gain is loop overhead only
- Projects on full newlib built for speed, picolibc, or a vendor or toolchain memmove that already has word-copy paths: the measured gap is against newlib-nano and has not been shown against anything faster
- Non-Cortex-M targets (Cortex-A, AArch64, RISC-V, x86): it is Thumb-only assembly
- Anywhere you need a link-time drop-in: compiler-generated memmove calls (struct assignment, __aeabi_memmove) still go to the C library

## How it is fast

It picks a copy direction once (forward when dest &lt; src or the ranges do not overlap, backward otherwise), then uses three loops: a 16-byte word loop (four LDR/STR pairs per iteration) when at least 16 bytes remain and source and destination are co-aligned (dest - src a multiple of 4, with the source start for forward copies or the source end for backward copies 4-byte aligned), a byte loop unrolled four times, and a single-byte tail loop. Loop heads are aligned with .balign 4/8 and padding NOPs to suit flash fetch. The gain comes mostly from the incumbent being weak: newlib's generic memmove.c compiles to a plain byte-at-a-time loop under -Os/__OPTIMIZE_SIZE__ (how newlib-nano is usually built), and newlib's ARM machine directory has an assembly memcpy but no assembly memmove.

## Compared with alternatives

Pick it over gamesun memcpy_fast (Cortex-M4 word/doubleword memcpy) when you need overlap-safe memmove or must run on Cortex-M0+, which has no unaligned access; arm-mem, copies-and-fills and Arm Optimized Routines target Cortex-A/AArch64 Linux and do not apply to Cortex-M firmware.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (the test bench needs arm-none-eabi-gcc, the STM32WL LL drivers submodule and Greatest; the routine itself needs nothing) |
| **Minimum toolchain** | Any GNU-compatible ARM assembler accepting .syntax unified Thumb code (arm-none-eabi-gcc used; version not stated) |
| **Platforms** | ARMv6-M and ARMv7-M Cortex-M cores; tested by the author on the STM32WL55 Cortex-M4 and Cortex-M0+ |
| **Thread safety** | Reentrant leaf function with no global state (uses only r0-r6 and the stack); not otherwise documented |
| **Drop-in for the baseline** | partial — same signature and memmove semantics, returns dest, but it is named memmove_ and must be called explicitly; renaming it to memmove would clash with the C library symbol |

## Gotchas

- The README claim predates the current code: 'more than 7x faster' was written on 2025-02-02 for an earlier Thumb-2, Cortex-M4-only version (under 350 bytes); the routine was rewritten for Cortex-M0+ on 2025-02-17 and the claim was trimmed to '7x', but no cycle counts for any version are committed.
- Correctness fix on 2025-02-24 (commit 92a9735): the backward word path tested whether the source START was 4-byte aligned instead of the source END, so backward overlapping copies of 16+ bytes whose length was not a multiple of 4 issued unaligned LDR/STR. That hard-faults on Cortex-M0+ (no unaligned access) and runs slower on Cortex-M4; any earlier M4 timing of backward copies came from that buggy path. Use the current file only.
- Harness flaw: the committed test_config.h sets TEST_CM0PLUS to 1, and on the M0+ core get_cycle_count() is an IPCC round trip to the Cortex-M4, which samples its DWT counter from a -O0 polling loop. The printed 'min cycles' handshake overhead is never subtracted and the polling phase adds jitter of the same order as the 'only a few cycles faster' differences at 1-20 bytes, and counts are M4 cycles, not M0+ cycles.
- Every timed figure is one warm call per case printed over UART, and the explicit 1/10/20/50-byte cases all use offsets with dest - src not a multiple of 4 (0x81 to 0x7E, 0x82, 0x102), so they exercise only the unrolled byte loop; the word loop is reached only by the slide tests (e.g. 0x15, 0x200 and 0x201 bytes with dest at src - 4 or src + 4).

## Known shortcomings

- 'Few cycles to 7x' against newlib-nano's memmove (--specs=nano.specs, probably a byte loop; inferred); Makefiles default to a -O0 harness and no results are committed; unaligned-access fix 2025-02-24. GPL-3.0.
- Enricher: the '7x' was written 2025-02-02 for an older Thumb-2 Cortex-M4-only version and kept after the 2025-02-17 Cortex-M0+ rewrite with no cycle counts committed for any version; until commit 92a9735 (2025-02-24) the backward word path tested source START alignment instead of END, so earlier backward copies used unaligned LDR/STR (HardFault on M0+, slow on M4); the committed test_config.h has TEST_CM0PLUS=1 and M0+ timing is an IPCC round trip to the M4 DWT counter polled from an -O0 loop with the handshake overhead never subtracted; the explicit 1-50 B cases never reach the word loop; the baseline is newlib's generic byte-loop memmove.c under -Os. Retiered to D.

## Caveats and trade-offs

First-party, unqualified range ('a few cycles' to '7x') with no table of cycle counts, sizes or alignments. The baseline is very likely newlib-nano's size-optimised memmove (--specs=nano.specs in both Makefiles), which is a weak incumbent on Cortex-M (byte loop under -Os; inference). The core on which the 7x was measured (M4 versus M0+) is not stated. Committed Makefiles default to debug = 1 (-O0 harness). Each measurement is a single call, so per-call timer overhead matters at 1-50 bytes. A correctness fix ('fixed a bug where we would try to access unaligned memory sometimes', 2025-02-24) landed on the same day as the README update, so the claim may predate it. Very small project (0 stars, 0 forks).

Cortex-M (ARMv6-M, ARMv7-M) only. Exposed as a separate symbol memmove_() to be called explicitly, not a link-time replacement for memmove. GPL-3.0 copyleft is awkward for firmware. The same author's sibling mmemcpy README says that implementation is slower than the Cortex-M4 libc memcpy because it avoids unaligned accesses, so the M4 behaviour of mmemmove is not characterised.

## Maintenance

Stale since 2025-02-24 (all visible commits fall between 2025-02-02 and 2025-02-24; 0 stars, no open issues), but it is one self-contained 130-line assembly file that passes its own overlap and offset sweep, so it is easy to vendor if GPL-3.0 is acceptable.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The only number is the README's first-party 'a few cycles' to '7x faster' against the toolchain memmove. The cycle-count harness (common/src/main.c) is public but has no committed results, no CPU core for the 7x and no compiler version, so it stays C.
- **Retiered** C to D: Enricher (2026-10-12): no measurement supports the current code. The '7x' sentence was written 2025-02-02 for an earlier Thumb-2 Cortex-M4 version and kept after the 2025-02-17 Cortex-M0+ rewrite with no cycle counts committed; the committed harness (TEST_CM0PLUS=1) times the M0+ through an IPCC round trip to the M4 DWT counter polled from an -O0 loop without subtracting the handshake, and the backward path's alignment bug (fixed 2025-02-24, commit 92a9735) affected any earlier backward-copy timing; the baseline is newlib's generic byte-loop memmove under -Os.
- **Verifier notes:** README claim verified as recorded (always faster, a few cycles to 7x, under 230 bytes, GPL-3.0, 0 stars, last commit 2025-02-24, so stale). Shortcomings to record: the baseline is newlib-nano (--specs=nano.specs), a size-optimised incumbent; the 7x has no size, core or table; there are no committed results; and the harness Makefiles default to -O0. A correctness fix for unaligned access landed 2025-02-24.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-108 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/AJ528/mmemmove>
  - <https://github.com/AJ528/mmemmove/commits/main>
  - <https://github.com/AJ528/mmemmove/tree/main/cm4>
  - <https://github.com/AJ528/mmemmove/tree/main/cm4/src>
  - <https://github.com/AJ528/mmemmove/tree/main/common/src>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/README.md>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/Makefile>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/cm4/Makefile>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/cm0plus/Makefile>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/common/src/main.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/README.md>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/Makefile>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/cm4/Makefile>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/cm0plus/Makefile>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/common/src/main.c>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/common/src/mmemmove.s>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/common/inc/test_config.h>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/cm4/STM32WL_FLASH_CM4.ld>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/cm0plus/STM32WL_FLASH_CM0P.ld>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/HEAD/cm4/src/startup_stm32wl55xx_cm4.s>
  - <https://github.com/AJ528/mmemmove/commits/main>
  - <https://github.com/AJ528/mmemmove/commits/main/common/src/mmemmove.s>
  - <https://github.com/AJ528/mmemmove/commits/main/README.md>
  - <https://github.com/AJ528/mmemmove/issues>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/3e2426eb2f50cfb0fa6c129a6862207e368a8032/common/src/mmemmove.s>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/138c559635d05a4c46bfc4c5e98074df88bf1ec4/src/mmemmove.s>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/138c559635d05a4c46bfc4c5e98074df88bf1ec4/README.md>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/66efe00d2671473d7c0a4cde6eea893d4d1ceef7/README.md>
  - <https://raw.githubusercontent.com/AJ528/mmemmove/6148851aba20bae175c1416cf0024fade3de8682/README.md>
  - <https://raw.githubusercontent.com/mirror/newlib-cygwin/master/newlib/libc/string/memmove.c>
  - <https://raw.githubusercontent.com/mirror/newlib-cygwin/master/newlib/libc/machine/arm/Makefile.inc>
  - <https://raw.githubusercontent.com/AJ528/mmemcpy/HEAD/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/aj528/mmemmove`) · [data/wave13/enrich/raw/github_com_aj528_mmemmove.json](../../../data/wave13/enrich/raw/github_com_aj528_mmemmove.json) (enrichment confidence 0.55)

</details>
