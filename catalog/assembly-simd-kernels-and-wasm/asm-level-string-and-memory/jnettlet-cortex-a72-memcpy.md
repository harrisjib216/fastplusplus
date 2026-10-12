# jnettlet/cortex_a72_memcpy (Cortex-A72 tuned AArch64 memcpy/memset)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly (AArch64)` · `MIT` · 🟡 stale

> LD_PRELOAD AArch64 memcpy/memmove/memset from Arm optimized-routines, re-tuned for Cortex-A72; ties glibc except small aligned copies.

| | |
|---|---|
| **Beats** | glibc memcpy (the 'memcpy' row) and Arm Optimized Routines memcpy (__memcpy_aarch64, __memcpy_aarch64_simd) |
| **Claimed result** | README: 'We are now pretty equivalent or faster than glibc's memcpy and Arm's optimized library memcpy on the optimized library's memcpy benchmark.' Aligned medium memcpy (bytes/ns): 16 B __memcpy_a72 4.40 vs memcpy 2.51; 32 B 8.79 vs 5.03; 64 B 12.80 vs 9.38 (about 1.75x, 1.75x, 1.36x, derived from page data). Random memcpy average 2.01 vs 1.97; large copies equal within 1-2%; unaligned backwards memmove 64K 11.69 vs 6.54. |
| **Workload** | Arm optimized-routines memcpy benchmark (string/bench/memcpy.c) on a Cortex-A72: random copies (16384 copies with lengths from a SPEC2017-derived size distribution under 4 KB) over 32K to 1024K working sets, aligned and unaligned medium copies 8 B to 512 B, large copies 1K to 64K, and forwards/backwards unaligned memmove 1K to 64K, in bytes per ns. |
| **Metric** | throughput |
| **Hardware** | Cortex-A72 (board, SoC and clock not stated) |
| **Compiler and flags** | Not stated for the benchmark. The library's Makefile builds the assembly with CPPFLAGS -fPIC -g -fno-inline -fno-builtin-inline -fno-inline-functions -fno-builtin and LDFLAGS -shared; compiler version unstated. |
| **Adoption** | 5 stars |
| **Last commit** | 2024-01-07 |
| **Links** | [repository](https://github.com/jnettlet/cortex_a72_memcpy) · [benchmark](https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/README) |

## Verdict

The author's run of Arm optimized-routines' memcpy benchmark on an unnamed Cortex-A72 (compiler, glibc and clock unstated) shows __memcpy_a72 at 1.95/4.40/8.79/12.80 bytes/ns for aligned 8/16/32/64-byte copies against 1.17/2.51/5.03/9.38 for the libc memcpy row and 1.35/2.93/5.86/10.83 for __memcpy_aarch64, with random (2.01 vs 1.97 average) and 1K-64K copies within 1-2%; those numbers were taken in July 2022 on code that was reworked in January 2024.

## Use it when

- Linux AArch64 systems with Cortex-A72 cores (the author is at SolidRun, whose HoneyComb LX2 uses 16 Cortex-A72 cores; the benchmark board is not stated) where a GPU framebuffer or PCIe BAR mapping is corrupted by the system memcpy's store order.
- Workloads dominated by small aligned copies of 8-64 bytes on Cortex-A72, where the README shows 1.36-1.75x over the libc row and 1.18-1.50x over __memcpy_aarch64.
- Unaligned copies around 128 bytes: 10.42 bytes/ns vs 7.77 for libc and 7.42 for __memcpy_aarch64, because the 96-byte cut-over sends them to the aligned-destination loop.
- Quick experiments: LD_PRELOAD one .so per process without rebuilding the application or glibc.

## Skip it when

- Any core other than Cortex-A72: memset assumes a 64-byte DC ZVA block (SKIP_ZVA_CHECK), and the tuning targets A72 fetch behaviour; glibc already IFUNC-selects good routines elsewhere.
- Copies of 512 bytes and up, random-size mixes and 1K-64K copies: the README shows these within about 1-2% of glibc and Arm's routine, so there is nothing to gain.
- Strongly ordered Device-nGnRE mappings: the code still issues unaligned and overlapping head/tail stores in every size class, and DC ZVA on Device memory raises an alignment fault; only one store-order pattern was changed.
- System-wide /etc/ld.so.preload on production machines: 5 stars, no tests, no CI, no release, last commit 2024-01-07, and the published numbers predate the current code.

## How it is fast

It is Arm optimized-routines' integer ldp/stp memcpy (2012-2020 code) with the medium-copy path cut from 128 to 96 bytes, so 97-128 byte copies go to the 64-byte software-pipelined loop with a 16-byte-aligned destination; small sizes use branchless overlapping head/tail copies, and one entry point handles memmove overlap by choosing a backwards loop. The January 2024 rework adds nop padding and 16-byte alignment of loops and branch targets to avoid taken-branch fetch penalties, and the backwards-copy tail stores its last 64 bytes in ascending order where upstream stores them descending. memset is Arm's NEON memset with DC ZVA zeroing for zero fills of 160 bytes and up, with the DCZID_EL0 block-size check compiled out.

## Compared with alternatives

Pick it over Arm Optimized Routines only when you need an LD_PRELOAD drop-in on Cortex-A72 for the device-memory store-order problem; for library use, Arm's __memcpy_aarch64 (the code it is derived from) is maintained, checks the ZVA size, and runs within 1-2% of it beyond 64 bytes. copies-and-fills and tinymembench target 32-bit ARM boards and are not alternatives on AArch64.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none (GNU make, a C compiler driver for .S files; asmdefs.h is in the repo) |
| **Minimum toolchain** | GCC or Clang that assembles AArch64 .S with Advanced SIMD; the Makefile passes only -fPIC -g -fno-builtin style flags and no -march; Debian packaging files from PR #1 |
| **Platforms** | aarch64 Linux only (LP64; ILP32 argument sanitising macros present); tuned for Cortex-A72, memset requires a 64-byte DC ZVA block |
| **Thread safety** | Reentrant leaf routines with no global state (from the source); not documented otherwise |
| **Drop-in for the baseline** | partial — exports memcpy, memmove and memset with the libc ABI for preloading, but calls that reach glibc as __memcpy_chk/__memset_chk (FORTIFY_SOURCE) or glibc-internal copies are not interposed (inference from the exported symbols). |

## Gotchas

- Hazard in memset.S: the January 2024 commit added '#define SKIP_ZVA_CHECK', which compiles out the DCZID_EL0 read that upstream uses to confirm a 64-byte DC ZVA block before zeroing; on a core with a larger block (e.g. 128 or 256 bytes) memset(p, 0, n &gt;= 160) would zero memory past the buffer, a smaller block would leave gaps, and if DC ZVA is prohibited (DZP=1) it faults. Safe on Cortex-A72's 64-byte block, which makes /etc/ld.so.preload on mixed hardware or images moved to another SoC risky.
- Benchmark caveats: the README tables (July 2022) were measured before the January 2024 rework of both files, on an unstated A72 board, compiler and glibc, with a locally modified Arm string/bench/memcpy.c (the __memcpy_a72 and memcpy_call rows are not in upstream) that is not published.
- The small-copy win over __memcpy_aarch64 is not algorithmic: for 8-32 B the current code runs the same instructions as optimized-routines v21.02 (one add moved), and in the unaligned table the two tie (1.95 vs 1.91, 4.40 vs 4.40, 8.80 vs 8.80 bytes/ns), so the aligned 1.44-1.50x gap most likely comes from code placement in a 100-million-iteration loop of one fixed size (inference). The libc 'memcpy' row is also slower than the author's 'memcpy_call' row at 8-32 B (1.17 vs 1.60), which suggests the baseline row's call path, not the copy code, sets part of the libc gap (inference).
- The headline backwards-memmove 64K result (11.69 vs 6.54 for libc) is shared by Arm's __memcpy_aarch64 (11.67), and unaligned 64 B (8.46 vs 9.35) and backwards memmove 1K-8K are slightly slower than libc.

## Known shortcomings

- No compiler, board or clock; gains only at 8-64 B, the rest inherited from Arm optimized-routines; some rows slower than glibc; numbers predate the Jan 2024 rework.
- Hazard: the January 2024 commit f60303d defines SKIP_ZVA_CHECK in memset.S, compiling out the DCZID_EL0 check, so the 64-byte DC ZVA block is hard-wired; on a core with another block size, memset(p, 0, n &gt;= 160) under ld.so.preload zeroes past the buffer, leaves gaps or faults. The README numbers (July 2022) predate that rework and use an unpublished modified Arm bench. For 8-32 B the code runs the same instructions as optimized-routines v21.02 and ties it in the unaligned table, so the aligned 1.44-1.50x over __memcpy_aarch64 most likely comes from code placement; the libc 'memcpy' row is slower than the author's own 'memcpy_call' row at 8-32 B, so part of the libc gap is call-path overhead. Real gain found at unaligned 128 B (10.42 vs 7.77 bytes/ns libc).

## Caveats and trade-offs

The repo's stated purpose is a device-memory fix (re-ordered stores in the 96-byte path for framebuffers/SPDK); the code is an initial import of Arm optimized-routines memcpy (Arm MIT header; memset.S is MIT OR Apache-2.0 WITH LLVM-exception; COPYING is MIT, Solidrun Ltd 2021), loaded via LD_PRELOAD. README tables (added July 2022) give no compiler, flags, board, SoC or clock, and the code was reworked again in January 2024 after the numbers were published. The 'memcpy' row is the system libc (presumably glibc). Gains are mostly small aligned sizes (8-64 B: 1.36-1.75x over libc, 1.18-1.50x over __memcpy_aarch64); random and large copies are within 1-2%; the backwards-memmove 64K win (11.69 vs 6.54) is shared by Arm's __memcpy_aarch64 (11.67); unaligned 64 B (8.46 vs 9.35) and backwards memmove 1K-8K (e.g. 16.48 vs 16.70 at 4K) are slightly slower than libc. [retier] The repo's stated purpose is a device-memory fix (re-ordered stores in the 96-byte path for framebuffers/SPDK); the code is an initial import of Arm optimized-routines memcpy loaded via LD_PRELOAD. README tables (July 2022) give no compiler, flags, board, SoC, glibc or clock, were measured with a locally modified, unpublished Arm string/bench/memcpy.c, and predate the January 2024 rework of both files. The small-copy win over __memcpy_aarch64 is not algorithmic: for 8-32 B the code runs the same instructions as optimized-routines v21.02 (one add moved) and the two tie in the unaligned table (4.40 vs 4.40, 8.80 vs 8.80 bytes/ns), so the aligned 1.44-1.50x gap most likely comes from code placement in a 100-million-iteration loop of one fixed size; the libc 'memcpy' row is slower than the author's own 'memcpy_call' row at 8-32 B (1.17 vs 1.60), so part of the libc gap is call-path overhead. Real gain at unaligned 128 B (10.42 vs 7.77 bytes/ns libc); random and large copies are within 1-2%; the backwards-memmove 64K win is shared by Arm's __memcpy_aarch64 (11.67); unaligned 64 B and backwards memmove 1K-8K are slightly slower than libc. Hazard: commit f60303d (January 2024) defines SKIP_ZVA_CHECK in memset.S, compiling out the DCZID_EL0 check, so memset(p, 0, n &gt;= 160) on a core with another DC ZVA block size zeroes past the buffer, leaves gaps or faults (DZP=1); safe only on Cortex-A72-class cores, risky in /etc/ld.so.preload on mixed hardware. Licences per file (MIT Solidrun 2021; memset.S MIT OR Apache-2.0 WITH LLVM-exception).

AArch64 Cortex-A72 only; built as libmemcpy.so for LD_PRELOAD or /etc/ld.so.preload; the stated purpose is fixing copies to memory-mapped device memory (framebuffers, SPDK) by reordering two stores in the 96-byte path, not general speed.

## Maintenance

Stale since January 2024, MIT (Solidrun 2021; memset.S carries Arm's MIT OR Apache-2.0 WITH LLVM-exception header) and small enough to vendor, but the current memset hard-codes a 64-byte DC ZVA block (SKIP_ZVA_CHECK), so it is only safe on Cortex-A72-class cores.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables from Arm optimized-routines' public string/bench/memcpy.c compare __memcpy_a72 against the libc 'memcpy' row and Arm's __memcpy_aarch64/__memcpy_aarch64_simd, but no compiler, flags, board, SoC or clock are given (only 'cortex-a72'), so not A; no independent measurement found.
- **Verifier notes:** All quoted numbers appear in the README (derived ratios correct). Main shortcomings: unspecified hardware/compiler, numbers predate the January 2024 rework, gains confined to 8-64 B copies and largely inherited from Arm optimized-routines (an already-known incumbent), a few rows slower than glibc. License MIT confirmed (COPYING, Solidrun Ltd); 5 stars; last commit 2024-01-07 (stale); not a GitHub fork, but code lineage is ARM-software/optimized-routines.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-27 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/README>
  - <https://github.com/jnettlet/cortex_a72_memcpy>
  - <https://github.com/jnettlet/cortex_a72_memcpy/commits>
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/COPYING>
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/memcpy.S>
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/memset.S>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/master/string/bench/memcpy.c>
- **Sources the enricher read:**
  - <https://github.com/jnettlet/cortex_a72_memcpy>
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/README>
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/COPYING>
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/memcpy.S>
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/memset.S>
  - <https://raw.githubusercontent.com/jnettlet/cortex_a72_memcpy/HEAD/asmdefs.h>
  - <https://github.com/jnettlet/cortex_a72_memcpy/commits>
  - <https://github.com/jnettlet/cortex_a72_memcpy/commit/f60303d>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/v21.02/string/aarch64/memcpy.S>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/v21.02/string/aarch64/memset.S>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/master/string/aarch64/memcpy.S>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/master/string/aarch64/memset.S>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/v21.02/string/bench/memcpy.c>
  - <https://raw.githubusercontent.com/ARM-software/optimized-routines/master/string/bench/memcpy.c>
  - WebSearch: libmemcpy.so HoneyComb LX2 memcpy framebuffer (no project hits; LKML 2018 thread 'framebuffer corruption due to overlapping stp instructions on arm64', snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jnettlet/cortex_a72_memcpy`) · [data/wave13/enrich/raw/github_com_jnettlet_cortex_a72_memcpy.json](../../../data/wave13/enrich/raw/github_com_jnettlet_cortex_a72_memcpy.json) (enrichment confidence 0.6)

</details>
