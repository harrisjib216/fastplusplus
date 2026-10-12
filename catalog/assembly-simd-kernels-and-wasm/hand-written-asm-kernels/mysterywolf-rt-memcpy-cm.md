# rt_memcpy_cm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly (ARM Cortex-M, GCC/IAR/Keil sources) with a C interface` · `Apache-2.0` · 🔴 abandoned

> Silicon Labs uC/LIB Cortex-M3/4/7 assembly memcpy packaged as RT-Thread's rt_memcpy; beats RT-Thread's C copy, ties Keil memcpy.

| | |
|---|---|
| **Beats** | RT-Thread's C rt_memcpy and the Keil C library memcpy |
| **Claimed result** | rt_memcpy 1261 ms; this assembly version 883 ms (1.43x, derived from page data); C library memcpy 906 ms (assembly 1.03x faster, derived). |
| **Workload** | Copying 10,000 bytes 10,000 times under Keil. |
| **Metric** | latency |
| **Hardware** | Cortex-M3/M4/M7 (MCU and clock not stated) |
| **Compiler and flags** | Keil (version and flags not stated) |
| **Adoption** | 12 stars; distributed as an RT-Thread online package |
| **Last commit** | 2022-06-09 |
| **Links** | [repository](https://github.com/mysterywolf/rt_memcpy_cm) · [benchmark](https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/README.md) |

## Verdict

One first-party Keil run on an unnamed Cortex-M3/4/7 board copied 10,000 bytes 10,000 times: RT-Thread's C rt_memcpy 1,261 ms, this assembly 883 ms (1.43x, derived from page data), Keil's C library memcpy 906 ms (2.6% slower, derived); that is about 113 MB/s for the assembly (derived from page data). Alignment, MCU, clock and compiler settings are not stated, and no benchmark code is published.

## Use it when

- RT-Thread firmware on Cortex-M3, M4 or M7 that does many large (hundreds of bytes and up) rt_memcpy calls between buffers with the same alignment, e.g. DMA or network buffers, when the kernel is built with its own C rt_memcpy.
- GCC or IAR builds where you cannot or do not want to route rt_memcpy to the toolchain's memcpy (RT_KLIBC_USING_LIBC_MEMCPY in RT-Thread 5.x, RT_KSERVICE_USING_STDLIB_MEMCPY in 4.1).
- Projects that want a small, auditable, Apache-2.0 copy routine with no dependencies and fixed stack use (44 bytes).

## Skip it when

- Keil/ARM Compiler projects that can call the C library memcpy: the only published number puts it at 906 vs 883 ms, about 2.6% (derived from page data), within run-to-run noise of a single undocumented run.
- Buffers whose addresses differ by an odd offset: the routine falls back to a byte-at-a-time LDRB/STRB loop (and to LDRH/STRH halfwords for a 2-byte offset) even though Cortex-M3/4/7 can do unaligned word loads, so it will be far slower than an aligned copy there; no misaligned case was measured.
- Short copies: every call checks three arguments and saves 11 registers (STMFD R3-R12 plus PUSH R0) before copying, a fixed cost the 10,000-byte benchmark hides.
- Overlapping buffers (no memmove behaviour; overlap is not checked) and cores without Thumb-2 (Cortex-M0/M0+/M23); not usable outside RT-Thread without supplying rt_ubase_t and the build glue yourself.
- Projects that need a maintained or versioned dependency: 13 commits, no tags, the package index pins 'latest' = master, last change 2022-06-09.

## How it is fast

When source and destination share the same offset modulo 4, it copies 1-3 head bytes to reach word alignment and then moves data with LDMIA/STMIA load/store-multiple of ten registers (R3-R12, 40 bytes per pair), unrolled nine times into a 360-byte loop, then single words, halfwords and bytes for the tail. The README credits the load/store-multiple instructions, not assembly as such. RT-Thread's C version (the newlib-derived word loop) moves 16 bytes per iteration with LDR/STR, which explains the 1.43x on aligned 10,000-byte copies; Keil's library memcpy already uses comparable multi-register copies, hence the near tie.

## Compared with alternatives

Pick it over the Raspberry Pi Pico SDK's pico_mem_ops when the target is an RT-Thread Cortex-M3/M4/M7 rather than an RP2040 Cortex-M0+; FastMemcpy and memcpy_benchmark are x86 SSE/AVX copies and do not apply to microcontrollers. Against the toolchain's own memcpy it offers parity, not a speedup. For Cortex-M copies outside RT-Thread, the catalogue's asm-level-string-and-memory category also lists gamesun/memcpy_fast (Cortex-M4, timed separately for each alignment case) and AJ528/mmemmove (a memmove, so overlap-safe).

## Integration

| | |
|---|---|
| **Form** | source-drop (RT-Thread online package: one .S file per toolchain plus SConscript) |
| **Dependencies** | RT-Thread build system (SCons, rtconfig.PLATFORM) and the rt_ubase_t type; the code itself needs nothing |
| **Minimum toolchain** | GNU as with .syntax unified, IAR EWARM, or armasm (Keil MDK armcc; armclang via the same _rvds.S since the 2022-06-09 SConscript change); toolchain versions not documented |
| **Platforms** | ARMv7-M Thumb-2 cores: Cortex-M3, M4, M7 (README); not M0/M0+/M23 |
| **Thread safety** | Reentrant: no global state, uses only registers and 44 bytes of the caller's stack (not documented, read from the source) |
| **Drop-in for the baseline** | partial — drop-in for RT-Thread's rt_memcpy only (same signature and return value); it relies on rt_memcpy being weak (RT-Thread 4.1) or on RT_KLIBC_USING_USER_MEMCPY, which the package Kconfig selects for RT-Thread 5.2.0 and later; it does not replace C library memcpy |

## Gotchas

- Relative misalignment is not handled by shifting or unaligned word loads: the maintainer confirms in issue #1 that non-aligned addresses are copied a byte at a time, and the code takes a halfword loop for 2-byte offsets and a byte loop for odd offsets, so 'handles non-word-aligned addresses' means correct, not fast.
- The benchmark is one Keil run with no harness in the repo, no MCU, clock, compiler version, optimisation level or buffer alignment; the 1.43x is against RT-Thread's own 16-byte-per-iteration C loop, not against a tuned memcpy. The maintainer's only other data point (issue #1) is an SD-card copy that gained about 500 ms, which he called not significant.
- Before the 2022-06-09 SConscript fix, the IAR source was selected only when PLATFORM == 'iar' (RT-Thread uses 'iccarm') and armclang was not listed, so IAR and Keil AC6 builds silently kept the C rt_memcpy; use the current master.
- NULL dst or src returns immediately without copying (dst is returned), and the routine saves R3 and R12 although AAPCS does not require it; harmless but adds cycles on every call.

## Known shortcomings

- About 2.6% over Keil memcpy in one undocumented run; Silicon Labs uC/LIB code with SPDX Apache-2.0 headers in all .S files (copyable).
- Only about 2.6% faster than the Keil libc memcpy in one Keil run with no harness; abandoned (last commit 2022-06-09).
- The code is Silicon Labs uC/LIB LDMIA/STMIA copy; the fast path runs only when src and dst share the same offset mod 4 (a 2-byte offset drops to a halfword loop, an odd offset to a byte loop; owner confirms in issue #1), and the misaligned case was never measured. Only 2.6% faster than the Keil C library memcpy (906 vs 883 ms) in one undocumented run; saves 11 registers per call. Before the 2022-06-09 SConscript fix, IAR ('iar' vs 'iccarm') and armclang builds silently kept the C rt_memcpy; RT-Thread 5.2+ needs RT_KLIBC_USING_USER_MEMCPY (the package Kconfig selects it).

## Caveats and trade-offs

Single undocumented Keil run: no benchmark code in the repo, no MCU, clock, Keil version, optimisation level or buffer alignment. The win over the Keil C library memcpy is about 2.6% (906 vs 883 ms, derived from page data), essentially parity; the 1.43x headline is against RT-Thread's own C rt_memcpy. The code is Silicon Labs uC/LIB assembly (Copyright 2004-2020 Silicon Laboratories, SPDX Apache-2.0 headers, ported to RT-Thread in 2020), and the README credits the LDMIA/STMIA load/store-multiple instructions (40 bytes per instruction pair), not assembly as such. Each call pushes R3-R12, which costs on short copies; buffers are not checked for overlap (memcpy semantics only). README is in Chinese. Last commit 2022-06-09.

Cortex-M3/4/7 only; handles non-word-aligned addresses; uses LDMIA/STMIA multi-register transfers (up to 40 bytes per operation).

## Maintenance

Abandoned since the 2022-06-09 SConscript fix (13 commits, 12 stars, 2 closed issues, no tags), but it is about 200 lines of Apache-2.0 assembly from Silicon Labs' long-used uC/LIB, small enough to vendor and still listed in the RT-Thread package index with a Kconfig update for RT-Thread 5.2.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README gives one Keil timing (10,000 bytes copied 10,000 times: rt_memcpy 1261 ms, assembly 883 ms, C library memcpy 906 ms); the repo holds only the three .S ports and SConscript, with no benchmark code, MCU, clock, Keil version or flags, so C.
- **Verifier notes:** Numbers match the README exactly; tier C confirmed, metadata (Apache-2.0, 12 stars, 5 forks, last commit 2022-06-09, abandoned) checked. Split id: merged.json also holds https://github.com/mysterywolf/rt_memcpy_cm#asm-level-string-and-memory (confirmed C in batch-27); record one of the two as duplicate. Shortcomings: \~3% win over the C library memcpy, single unspecified Keil run with no harness, abandoned.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-27 (wave 13); verifier batch-33 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/README.md>
  - <https://github.com/mysterywolf/rt_memcpy_cm>
  - <https://github.com/mysterywolf/rt_memcpy_cm/commits/master>
  - <https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/rt_memcpy_gcc.S>
  - <https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/SConscript>
  - <https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/README.md>
  - <https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/rt_memcpy_gcc.S>
  - <https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/rt_memcpy_iar.S>
  - <https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/rt_memcpy_rvds.S>
  - <https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/SConscript>
  - <https://raw.githubusercontent.com/mysterywolf/rt_memcpy_cm/HEAD/LICENSE>
  - <https://github.com/mysterywolf/rt_memcpy_cm>
  - <https://github.com/mysterywolf/rt_memcpy_cm/commits/master>
  - <https://github.com/mysterywolf/rt_memcpy_cm/commit/a1fa21c>
  - <https://github.com/mysterywolf/rt_memcpy_cm/issues?q=is%3Aissue>
  - <https://github.com/mysterywolf/rt_memcpy_cm/issues/1>
  - <https://github.com/mysterywolf/rt_memcpy_cm/issues/2>
  - <https://raw.githubusercontent.com/RT-Thread/rt-thread/v4.0.3/src/kservice.c>
  - <https://raw.githubusercontent.com/RT-Thread/rt-thread/v4.1.0/src/kservice.c>
  - <https://raw.githubusercontent.com/RT-Thread/rt-thread/master/src/kservice.c>
  - <https://raw.githubusercontent.com/RT-Thread/rt-thread/master/src/klibc/kstring.c>
  - <https://raw.githubusercontent.com/RT-Thread/rt-thread/master/src/klibc/Kconfig>
  - <https://raw.githubusercontent.com/RT-Thread/packages/master/system/enhanced-kservice/rt_memcpy_cm/Kconfig>
  - <https://raw.githubusercontent.com/RT-Thread/packages/master/system/enhanced-kservice/rt_memcpy_cm/package.json>
  - <https://raw.githubusercontent.com/RT-Thread/packages/master/system/enhanced-kservice/Kconfig>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mysterywolf/rt_memcpy_cm`) · [data/wave13/enrich/raw/github_com_mysterywolf_rt_memcpy_cm.json](../../../data/wave13/enrich/raw/github_com_mysterywolf_rt_memcpy_cm.json) (enrichment confidence 0.62)

</details>
