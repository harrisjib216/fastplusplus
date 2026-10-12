# hglm ARM memcpy, memset, memzero and copy_page kernel patches (test-arm-kernel-memcpy)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `Per-file headers: MIT/X11 (benchmark.c, memcpy_armv6v7.S, new_arm.S, Copyright 2013 Harm Hanemaaijer) and GPL-2.0-only (kernel-derived memset.S, memzero.S, copy_page.S, copy templates, user-copy variants and the \*_orig.S baselines); asm.h, new_arm.h and kernel_defines\*.h have no header; no repo-level LICENSE file` · 🔴 abandoned

> 2013 hand-tuned ARMv6/ARMv7 assembly for Linux kernel copy_page, memset, memzero and memcpy, with a userspace benchmark against the old kernel routines.

| | |
|---|---|
| **Beats** | original Linux kernel ARM memcpy, memset, memzero and copy_page (the benchmark harness also runs libc memcpy/memset alongside) |
| **Claimed result** | The hglm/patches README says copy_page and larger memcpy gain 'on the order of 70%' on the armv6 Raspberry Pi, with a smaller benefit on armv7. The commit message of arm-mem-funcs/0002-Optimize-copy_page-for-modern-ARM-platforms.patch (2013-07-12) gives copy_page speed-ups from 10% (Cortex A8) to 80% (armv6 in the Raspberry Pi) over the existing kernel copy_page. No results table is checked in. |
| **Workload** | bench.script drives benchmark.c over a set of tests (mixed power-of-2 sizes, unaligned mixed sizes, copy_page) for the original kernel routines, libc and the optimized routines on ARMv6 and ARMv7. |
| **Metric** | throughput |
| **Hardware** | ARMv6 Raspberry Pi (32-byte cache line) and ARMv7 including a Cortex-A8 (64-byte cache line); exact SoCs and clocks not stated |
| **Compiler and flags** | Makefile: \$(CC) with -std=gnu99 -Ofast -Wall -DARMV7 by default (-DARMV6 for armv6, optional Thumb2 flags); compiler version and the flags used for the quoted speedups not stated |
| **Adoption** | 14 stars (test repo); 5 stars (hglm/patches) |
| **Last commit** | 2013-08-28 |
| **Links** | [repository](https://github.com/hglm/test-arm-kernel-memcpy) · [benchmark](https://github.com/hglm/patches) |

## Verdict

No results are published. The patch commit message (2013-07-12) claims copy_page speed-ups over the 2013 in-kernel copy_page of 10% on a Cortex-A8 to 80% on the ARMv6 Raspberry Pi, measured in a userspace sandbox; the patches README says 'on the order of 70%' for copy_page and large memcpy. Compiler version, SoC and clocks are unstated, and the copy_page code those figures came from was reworked two days later. An independent tester on linux-arm-kernel reported that copy_page and large-memcpy prefetching did not work well on his platforms (snippet only).

## Use it when

- You maintain a 32-bit ARMv6 (Raspberry Pi 1 class) or ARMv7 kernel or bare-metal codebase that still uses the 2013-era arch/arm/lib copy_page, memset or memzero, and you want a reference for a better prefetch distance.
- You want a ready-made validation and timing harness for ARM32 memcpy/memset variants: 50 memcpy and 23 memset size/alignment tests, plus a --validate mode that checks every byte of a 16 MiB buffer.
- Page-sized or larger copies on an ARMv6 SoC with 32-byte cache lines, where the author reports the largest gain (about 70-80% on copy_page).
- Studying how write alignment (8 vs 32 bytes) and the PLD distance interact on a given SoC before tuning your own routine.

## Skip it when

- AArch64 or x86: the code is 32-bit ARM assembly only, and the benchmark exits unless sizeof(size_t) == sizeof(int).
- Userspace memcpy/memset on a Raspberry Pi or other ARM32 board: the siblings bavison/arm-mem or copies-and-fills are drop-in libc replacements aimed at that job, and these routines carry kernel names and kernel conventions.
- Kernel copy_from_user/copy_to_user: the author's own issue #1 (2013-12-03) says the current versions do not work correctly in the kernel, and the userspace harness never exercises user-space page faults.
- Current upstream kernels: the patches stopped applying cleanly by February 2015 and nothing has changed since 2013-08-28.
- When you need published, reproducible numbers: no run output, compiler version, SoC or clock is checked in.

## How it is fast

The gain comes from a new PLD prefetch strategy for ARMv6/ARMv7 cache lines. The old copy_page issued paired preloads 2-3 lines ahead from a loop built for StrongARM. The new one does one preload per line at a configurable PREFETCH_DISTANCE and stops prefetching past the end of the source. It also uses wider 8-register LDM/STM blocks. memset and memzero align the destination to 8 bytes (ARMv7) or 32 bytes (ARMv6) before a 64-byte STM loop. They handle the 8-64 byte tail with a computed jump into an unrolled STM ladder and are written to assemble mostly to 16-bit Thumb2 instructions. The experimental memcpy adds a fast path for word-aligned copies of 256 bytes or less and uses unaligned word loads for copies of up to 64 bytes.

## Compared with alternatives

Pick it only for kernel-side 32-bit ARM copy_page/memset/memzero work or as an ARM32 test harness. For userspace on a Raspberry Pi, bavison/arm-mem or simonjhall/copies-and-fills replace libc directly. For modern Arm cores, Arm Optimized Routines is maintained and covers AArch64.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (GNU toolchain assembling .S files through the C preprocessor; the benchmark links -lm -lrt) |
| **Minimum toolchain** | Makefile uses gcc with -std=gnu99 -Ofast and unified ARM syntax; no compiler version documented |
| **Platforms** | 32-bit ARM: ARMv6 and ARMv7 tested (Thumb2 build optional on ARMv7); ARMv5 untested; the optimized memcpy and user-copy routines use PLD unconditionally, so they do not work on ARMv4 |
| **Thread safety** | not documented; the .S routines read use no global state (registers and stack only) |
| **Drop-in for the baseline** | partial — memset, memzero and copy_page keep the kernel's signatures and were packaged as kernel patches (hglm/patches/arm-mem-funcs) for 2013 kernels; memcpy and the user-copy routines exist only as userspace test versions |

## Gotchas

- The quoted speed-ups were not measured on the copy_page now at HEAD. They come from the 2013-07-12 patch commit message and the mailing-list post, both written before commit 83f288c (2013-07-14) reworked copy_page.S. The patch version runs a loop per L1_CACHE_BYTES with PREFETCH_DISTANCE 3 (96 B on ARMv6, 192 B on ARMv7). HEAD defaults to PRELOAD_LINE_SIZE 32 with a prefetch offset of 128 B (ARMv6) or 256 B (ARMv7). Running bench.script at HEAD therefore times different code from the posted kernel patch.
- Latent overrun in HEAD copy_page.S on ARMv4 (no PLD) with the default PRELOAD_LINE_SIZE 32: NO_PLD loads r2 = COPY_COUNT = 4096/32 = 128, but each loop iteration copies 64 bytes, so it copies 8192 bytes. That runs one full page past both source and destination. The kernel patch version copies 32 bytes per iteration and is correct. ARMv4 is listed as untested.
- The README's NEON step is broken: the Makefile line is '#NEON_CLAGS = DUSE_NEON', a misspelled variable with no leading '-'. Uncommenting it never sets NEON_CFLAGS, so NEON stays off unless you fix the Makefile by hand.
- Harness limits: each address/size pattern table holds only 256 entries, so the same 128 source/destination pairs repeat, keeping caches and branch predictors warm. Results print as one MB/s line per repetition with no median or aggregation. An independent tester on the July 2013 linux-arm-kernel thread (Willy Tarreau) found that the prefetch strategy did not work well for copy_page and large memcpy on his platforms. A follow-up tweak gained about 0.8% on memcpy. This comes from a WebSearch snippet only; lore.kernel.org was unreachable.

## Known shortcomings

- Only the patch 0002 commit message gives numbers (copy_page 10% on Cortex-A8 to 80% on Raspberry Pi), no published results, compiler version unstated, baseline is the old kernel routines; per-file MIT plus GPL-2.0-only with some headers unlicensed (mixed). Abandoned 2013-08-28.
- The quoted 10-80% copy_page speedups predate commit 83f288c (2013-07-14), which reworked copy_page.S; HEAD's prefetch defaults (32-byte line, 128/256-byte offset) differ from the posted kernel patch (PREFETCH_DISTANCE 3), so bench.script at HEAD times different code. Bug: HEAD copy_page.S NO_PLD path (ARMv4, line size 32) copies 8192 bytes, one full page past source and destination; the kernel patch version is correct. Issue #1: copy_from/to_user broken. Makefile NEON line is a typo ('#NEON_CLAGS = DUSE_NEON'). Willy Tarreau on the July 2013 linux-arm-kernel thread found the prefetch strategy weak for copy_page and large memcpy (WebSearch snippet only; lore.kernel.org unreachable).

## Caveats and trade-offs

First-party, loosely worded speedups ('order of 70%', '10% to 80%') with no published run output, no compiler version, and no exact SoC or clock. The baseline is the 2013 in-kernel ARM routines rather than glibc, although the harness also runs libc memcpy/memset and no libc numbers are quoted. The work is unfinished per the patches README: copy_page, memset and memzero are done, while memcpy and the user-copy variants are still in progress. As of February 2015 the patches no longer applied cleanly to upstream kernels. Licensing is per-file (MIT for the new memcpy, GPL-2.0-only for kernel-derived files), and a few small headers have no licence. NEON paths were removed from copy_page, memset and memzero; the last commit was 2013-08-28. [retier] First-party, loosely worded speedups ('order of 70%', '10% to 80%') with no published run output, no compiler version and no exact SoC or clock; the baseline is the 2013 in-kernel ARM routines, not glibc. The speedups were not measured on the copy_page at HEAD: they come from the 2013-07-12 patch commit message and mailing-list post, written before commit 83f288c (2013-07-14) reworked copy_page.S; the patch loops per L1_CACHE_BYTES with PREFETCH_DISTANCE 3 while HEAD defaults to PRELOAD_LINE_SIZE 32 with a 128-byte (ARMv6) or 256-byte (ARMv7) prefetch offset, so bench.script at HEAD times different code. Latent overrun: HEAD copy_page.S on ARMv4 (NO_PLD, line size 32) copies 8192 bytes, one full page past source and destination (the kernel patch version copies 32 bytes per iteration and is correct). The README's NEON step is broken ('#NEON_CLAGS = DUSE_NEON' misspelled, no leading dash). The harness repeats the same 128 source/destination pairs (256-entry pattern tables) and prints one MB/s line per repetition with no aggregation. Willy Tarreau on the July 2013 linux-arm-kernel thread found the prefetch strategy did not work well for copy_page and large memcpy on his platforms (WebSearch snippet only). Unfinished per the patches README (memcpy and user-copy variants in progress; copy_from/to_user broken, issue #1); patches stopped applying to upstream kernels by February 2015. Per-file licensing (MIT for the new memcpy, GPL-2.0-only for kernel-derived files, a few headers unlicensed). Last commit 2013-08-28.

32-bit ARM only (ARMv6/ARMv7); the optimized memcpy, copy_from_user and copy_to_user use PLD unconditionally so they do not work on ARMv4; NEON paths were experimental and later removed from copy_page, memset and memzero; patches no longer applied cleanly to upstream kernels by February 2015.

## Maintenance

Abandoned since 2013-08-28 and labelled experimental by its author, with a known-broken copy_from/to_user (issue #1). Licensing is per file: MIT for the new memcpy and benchmark, GPL-2.0-only for the kernel-derived memset, memzero and copy_page. No upstream merge was found. Useful as a reference and harness, not as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The harness is public: benchmark.c and bench.script compare libc memcpy/memset and the original kernel routines with the optimized ones, and the Makefile sets -std=gnu99 -Ofast. However, no results are published, and the only numbers are loose first-party statements: the hglm/patches README says 'on the order of 70%', and the copy_page patch commit message says 10% (Cortex A8) to 80% (armv6 Raspberry Pi). No compiler version and no run output are given, so the entry stays at C.
- **Verifier notes:** This is a genuine 2013 ARM kernel memcpy/memset optimisation set with a public validation and benchmark harness, but there are no published results. Tier C, abandoned since 2013-08-28. The patch commit message adds a per-CPU range (10% Cortex A8 to 80% Raspberry Pi) for copy_page. Its baseline is not in the list (old kernel routines).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `license`, `usability`, `caveats`
- **Shortcomings recorded by:** verifier batch-92 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/hglm/test-arm-kernel-memcpy>
  - <https://github.com/hglm/test-arm-kernel-memcpy/commits/master>
  - <https://github.com/hglm/patches>
  - <https://github.com/hglm/patches/tree/master/arm-mem-funcs>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/README>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/README.md>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/bench.script>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/Makefile>
  - <https://raw.githubusercontent.com/hglm/patches/HEAD/README.md>
  - <https://raw.githubusercontent.com/hglm/patches/HEAD/arm-mem-funcs/0002-Optimize-copy_page-for-modern-ARM-platforms.patch>
  - <https://raw.githubusercontent.com/hglm/patches/HEAD/arm-mem-funcs/0003-Optimize-ARM-memset-and-memzero-functions.patch>
- **Sources the enricher read:**
  - <https://github.com/hglm/test-arm-kernel-memcpy>
  - <https://github.com/hglm/test-arm-kernel-memcpy/commits/master>
  - <https://github.com/hglm/test-arm-kernel-memcpy/commit/83f288c>
  - <https://github.com/hglm/test-arm-kernel-memcpy/issues?q=is%3Aissue>
  - <https://github.com/hglm/test-arm-kernel-memcpy/issues/1>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/README>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/README.md>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/bench.script>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/Makefile>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/kernel_defines.h>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/kernel_defines_orig.h>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/asm.h>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/new_arm.h>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/copy_page.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/copy_page_orig.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/memset.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/memset_orig.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/memzero.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/memzero_orig.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/memcpy_armv6v7.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/memcpy_orig.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/copy_template.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/copy_template_orig.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/copy_from_user_armv6v7.S>
  - <https://raw.githubusercontent.com/hglm/test-arm-kernel-memcpy/HEAD/new_arm.S>
  - <https://raw.githubusercontent.com/hglm/patches/HEAD/README.md>
  - <https://raw.githubusercontent.com/hglm/patches/HEAD/arm-mem-funcs/0002-Optimize-copy_page-for-modern-ARM-platforms.patch>
  - <https://raw.githubusercontent.com/hglm/patches/HEAD/arm-mem-funcs/0003-Optimize-ARM-memset-and-memzero-functions.patch>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/hglm/test-arm-kernel-memcpy`) · [data/wave13/enrich/raw/github_com_hglm_test_arm_kernel_memcpy.json](../../../data/wave13/enrich/raw/github_com_hglm_test_arm_kernel_memcpy.json) (enrichment confidence 0.6)

</details>
