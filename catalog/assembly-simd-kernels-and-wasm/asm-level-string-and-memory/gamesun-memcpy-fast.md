# memcpy_fast (gamesun): Cortex-M4 word and doubleword memcpy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `GPL-3.0` · 🔴 abandoned

> Plain-C Cortex-M4 memcpy with doubleword and unaligned-word loops; 1.3-5.3x faster than the toolchain memcpy on 10 KB copies.

| | |
|---|---|
| **Beats** | the toolchain's standard memcpy on Cortex-M4 (C library not stated) |
| **Claimed result** | Results table (memcpy_fast_vs_memcpy.png, linked from the README), 10240-byte copies, times in microseconds: same alignment mod 8 but not 8-aligned (a=b=1,2,3,5,6,7) 121-122 us vs 640-641 us for memcpy, 5.25x-5.29x; both 8-aligned or 4-offset pairs (0,0 and 4,4) 121-122 vs 213 us, 1.75x-1.76x; (4,0) and (0,4) 161-162 vs 214 us, 1.32x-1.33x; other mismatched alignments 188-268 us vs 640-641 us, 2.39x-3.41x. The README's '1.3 to 5.2 times' slightly understates the top of the table (528.9% = 5.29x). |
| **Workload** | memcpy_test() in memcpy_fast.c: for each destination offset a, source offset b and length offset c in 0-7, copy TEST_BUFF_SIZE (10240) + c bytes from an 8-byte-aligned static source to an 8-byte-aligned static destination with memcpy_fast and then with memcpy, timing each with TIM5 (1 us resolution) with interrupts disabled; memcpy_fast's result is checked with memcmp. The published table collapses c = 0-7 into one row per (a, b) pair. |
| **Metric** | throughput |
| **Hardware** | Cortex-M4 STM32 microcontroller (memcpy_test uses the STM32 Standard Peripheral Library and TIM5 at a 1 MHz tick); part number, clock and memory region not stated. |
| **Compiler and flags** | Not stated; the C library providing the baseline memcpy (newlib, newlib-nano or a vendor libc) is also not stated. |
| **Adoption** | 7 stars |
| **Last commit** | 2020-08-25 |
| **Links** | [repository](https://github.com/gamesun/memcpy_fast) · [benchmark](https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/README.md) |

## Verdict

On an unnamed STM32 Cortex-M4 (clock, compiler, flags and libc not stated), copying 10240-10247 bytes between 8-aligned static buffers at offsets 0-7, memcpy_fast took 121-268 us against 213-641 us for the toolchain memcpy (TIM5 at 1 us, interrupts off): 1.32-1.33x for (4,0) and (0,4), 1.75-1.76x for (0,0) and (4,4), 2.39-3.41x for mismatched alignments and 5.25-5.29x for equal non-8-aligned offsets. The baseline runs at byte speed (640 us) for every pair that is not both 4-aligned, including equal misalignments such as (1,1), so it never aligns pointers before copying words and the top ratios measure word copies against byte copies (derived from page data).

## Use it when

- Cortex-M4 firmware whose libc memcpy shows the baseline's pattern (byte speed whenever either pointer is not 4-byte aligned) and copies kilobyte-sized buffers at arbitrary byte offsets, such as packet or frame buffers.
- Bulk copies between buffers with the same misalignment (both at offset 1, 2, 3, 5, 6 or 7 mod 8): 121-122 us versus 640-641 us for 10 KB in the author's table, about 5.3x.
- 8-byte-aligned bulk copies where the toolchain memcpy only runs a word loop: 121 versus 213 us, 1.76x.
- GPL-3.0-compatible projects that can take a 130-line C file, fix its includes and inspect the generated assembly.

## Skip it when

- Toolchains whose memcpy is already tuned for Armv7-M (aligns the pointers and uses unaligned or multiple loads): the published gaps are against a memcpy that byte-copies any pair not both 4-aligned, and no comparison against a tuned memcpy exists.
- Small copies: only 10240-10247-byte copies were timed; the cost of the dispatch, head and tail code for short copies is not documented.
- Overlapping buffers: no memmove semantics (the unaligned path copies from the top word down, the aligned path from the bottom up).
- Cores or configurations that trap unaligned word accesses (the code comment states the unaligned-access assumption for Cortex-M4 only), and 64-bit targets, since pointers are cast to u32; it cannot be unit-tested on a 64-bit PC unchanged.
- Permissively licensed or proprietary firmware: GPL-3.0.

## How it is fast

Alignment dispatch: when source and destination have the same address mod 8 and n &gt;= 16, it copies the 1-7 head bytes to reach 8-byte alignment and then runs a long long loop intended to compile to LDRD/STRD (8 bytes per load/store pair). Otherwise it copies 32-bit words through possibly misaligned long pointers, relying on Cortex-M4 hardware support for unaligned LDR/STR, then a halfword and a byte for the tail. Most of the headline gain comes from the baseline, which falls back to byte copies whenever the two pointers are not both 4-byte aligned; memcpy_fast never copies bytewise for n &gt;= 4.

## Compared with alternatives

Prefer mmemmove (AJ528), Cortex-M assembly with memmove semantics measured against newlib-nano, when buffers may overlap or when the instruction choice must not depend on compiler flags; pick memcpy_fast only when you want C source you can audit and rebuild for a Cortex-M4. The Arm siblings copies-and-fills, arm-mem and Arm Optimized Routines target Cortex-A class cores, not Cortex-M.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | types.h for the u8/u32 typedefs (not in the repository); memcpy_test() additionally needs the STM32 Standard Peripheral Library (RCC, TIM5), CMSIS __disable_irq/__enable_irq and printf unless MEMCPY_TEST is removed |
| **Minimum toolchain** | C99 compiler targeting 32-bit Arm; the test uses GCC-style __attribute__((aligned(8))); the compiler, version and flags behind the published numbers are not documented |
| **Platforms** | 32-bit Arm Cortex-M4 (STM32) with unaligned LDR/STR allowed; not 64-bit targets |
| **Thread safety** | The copy functions are stateless and reentrant; memcpy_test() disables interrupts while it runs. |
| **Drop-in for the baseline** | partial — same signature and return value as memcpy, but a different symbol name, no overlap handling, Cortex-M4-class targets only, and the file does not compile as shipped outside the author's project |

## Gotchas

- Build-flag sensitive: memcpy_aligned8's forward `*dto++ = *dfrom++` loop is a plain copy loop, and GCC's -ftree-loop-distribute-patterns pass (enabled at -O3 in GCC 9 and at -O2 and higher from GCC 10, per the releases' invoke.texi; tree-loop-distribution.c emits memcpy or memmove calls for such loops) can replace it with a call to the library routine it is meant to beat. Build the file with -fno-tree-loop-distribute-patterns and check the disassembly for LDRD/STRD.
- Relies on undefined behaviour: memcpy_unaligned4 dereferences misaligned long pointers and both paths access byte buffers through long and long long lvalues (strict aliasing). The commented-out forward loop is annotated 'LDM,STM not support unaligned access', i.e. the compiler merged the accesses into multiple-load instructions that fault on unaligned addresses; the shipped reverse-indexed loop avoids that only with the author's compiler, so another compiler or optimisation level can bring the UsageFault back.
- Does not compile as shipped outside the author's project: memcpy_fast.c defines MEMCPY_TEST unconditionally (pulling in STM32 SPL timer calls), includes a types.h that is not in the repository, and memcpy_fast.h uses size_t without including &lt;stddef.h&gt;.
- Benchmark harness: only memcpy_fast's output is checked (memcmp over the copied range, so a write past n would go unnoticed), each pair is timed once with a 1 us timer, and the 5.25-5.29x rows compare word copies against the baseline's byte copies for equally misaligned pointers, a case any alignment-aware memcpy handles at aligned speed.

## Known shortcomings

- Numbers transcribed from a PNG table (1.32x-5.29x on 10240 B) with no compiler, flags, libc or MCU stated; the baseline is probably a byte-loop memcpy (640 us); misaligned-pointer undefined behaviour. GPL-3.0.
- Enricher: the baseline byte-copies any pair that is not both 4-aligned, so the 5.3x rows compare word loops against byte loops; memcpy_unaligned4 dereferences a misaligned long\* (UB) and the memcpy_aligned8 forward loop risks being replaced by a memcpy call under GCC's -ftree-loop-distribute-patterns (on at -O3 for gcc 9, -O2 and up for gcc 10); the memcmp check covers only n bytes; does not build as shipped (missing types.h, unconditional MEMCPY_TEST pulls the STM32 SPL). Retiered to D.

## Caveats and trade-offs

No compiler, flags, C library or MCU part are given, and the 10240-byte copy is the only size tested (no small copies, where the dispatch overhead matters). The baseline memcpy takes 640 us for any mismatched or odd alignment but 213 us when both pointers are 4-aligned (derived from page data), which looks like a size-optimised byte-loop memcpy such as newlib-nano's; a speed-optimised libc memcpy would narrow the gap. memcpy_unaligned4 dereferences misaligned long pointers, which is undefined behaviour in C and relies on Cortex-M4 tolerating unaligned LDR/STR; a compiler that merges those accesses into LDM/LDRD would fault, and the author works around this with a reverse-indexed loop. The code casts pointers to u32 (32-bit only) and includes a types.h that is not in the repository. GPL-3.0 is copyleft. Eleven commits in August 2020, no later activity.

Plain C: copies with long long (LDRD/STRD) loops when source and destination share 8-byte alignment and with 32-bit long loops otherwise, relying on the compiler's code generation and on Cortex-M4 unaligned LDR/STR support; casts between integer widths without regard to strict aliasing; GPL-3.0 licence blocks use in permissive code; Cortex-M4 only.

## Maintenance

Abandoned: 11 commits on 12 and 25 August 2020, no issues or releases, 7 stars; GPL-3.0 and small enough to rewrite, but it needs a types.h, removal of the built-in STM32 test and a disassembly check of the copy loops before use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party timings (memcpy_test() in memcpy_fast.c, results table in memcpy_fast_vs_memcpy.png) against the toolchain memcpy, with no compiler, flags, C library or MCU part stated, so C.
- **Retiered** C to D: Enricher (2026-10-12): crippled baseline with no valid measurement. The compared memcpy byte-copies any source/destination pair that is not both 4-byte aligned, so the headline 5.3x rows pit word loops against byte loops; the fast paths rely on misaligned long\* dereferences (UB) and a loop that GCC's -ftree-loop-distribute-patterns can turn back into a memcpy call; the project does not build as shipped.
- **Verifier notes:** README range matches the PNG table (132.1% to 528.9%); the per-case numbers exist only in the image, now transcribed into claimed_speedup. GPL-3.0, 7 stars, 1 fork, last commit 2020-08-25. Shortcomings: unnamed compiler, flags, libc and MCU, single 10 KB size, baseline likely a size-optimised byte-loop memcpy, misaligned-pointer UB in the unaligned path.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/gamesun/memcpy_fast>
  - <https://github.com/gamesun/memcpy_fast/commits>
  - <https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/README.md>
  - <https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/memcpy_fast.c>
  - <https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/memcpy_fast.h>
  - <https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/memcpy_fast_vs_memcpy.png>
- **Sources the enricher read:**
  - <https://github.com/gamesun/memcpy_fast>
  - <https://github.com/gamesun/memcpy_fast/commits>
  - <https://github.com/gamesun/memcpy_fast/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/README.md>
  - <https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/memcpy_fast.c>
  - <https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/memcpy_fast.h>
  - <https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/gamesun/memcpy_fast/HEAD/memcpy_fast_vs_memcpy.png>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-9.1.0/gcc/doc/invoke.texi>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-10.1.0/gcc/doc/invoke.texi>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-10.1.0/gcc/tree-loop-distribution.c>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/gamesun/memcpy_fast`) · [data/wave13/enrich/raw/github_com_gamesun_memcpy_fast.json](../../../data/wave13/enrich/raw/github_com_gamesun_memcpy_fast.json) (enrichment confidence 0.6)

</details>
