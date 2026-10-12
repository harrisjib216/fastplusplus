# z88dk (Z80 development kit: C compilers, z80asm assembler and assembly libraries)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C` · `Clarified Artistic License (SPDX ClArtistic: FSF-libre and GPL-compatible but not OSI-approved per the SPDX license list), 'unless otherwise stated in the appropriate file'` · 🟢 active

> Z80/8080-family C toolchain (sccz80, zsdcc, z80asm) whose assembly C and maths libraries run 1.1-5.4x fewer cycles than stock SDCC 4.6.0.

| | |
|---|---|
| **Beats** | SDCC 4.6.0 (also HI-TECH C 3.09 and 7.80 and IAR Z80 V4.06A in the same tables) |
| **Claimed result** | From the wiki Benchmarks tables, Z80 cycles for SDCC 4.6.0 against z88dk's zsdcc 4.6.0 #16639 builds: n-Body 4,361,393,645 vs 2,243,368,504 for Z88DK/SDCC_CLASSIC (math48), 1.94x fewer (derived from page data), and vs 860,188,405 for Z88DK/SDCC_CLASSIC/MATH32, 5.07x (derived); the fastest z88dk n-Body row, Z88DK/SCCZ80_NEW/MATH32 at 807,783,742, is 5.40x (derived). Whetstone 1,850,296,726 vs 916,750,272 for Z88DK/SDCC_CLASSIC, 2.02x (derived), and vs 360,608,050 for Z88DK/SDCC/MATH32, 5.13x (derived). Fasta 414,019,207 vs 241,418,675 for Z88DK/SDCC_CLASSIC, 1.71x (derived). Pi without ldiv 7,218,092,827 vs 4,010,854,332 for Z88DK/SDCC_NEW, 1.80x (derived), and vs 1,696,878,309 for Z88DK/SCCZ80_NEW_FAST, 4.25x (derived). Dhrystone 2.1 274,542,684 vs 242,442,688 for Z88DK/SDCC_NEW, 1.13x (derived). Binary-Trees 193,466,493 vs 149,280,700 for Z88DK/SDCC_CLASSIC, 1.30x (derived). The Pi and Dhrystone comparison rows are the NEW library, not the classic library as the record said. |
| **Workload** | Z80 cycle counts and code size for Dhrystone 2.1, Whetstone 1.2, n-Body, Fasta, Pi, Sieve, Fannkuch and Binary-Trees compiled by each toolchain and run on the z88dk-ticks Z80 emulator (wall clock derived at 4 MHz). |
| **Metric** | throughput |
| **Hardware** | z88dk-ticks Z80 emulator (cycle-exact count; wall time assumes a 4 MHz Z80), not a physical CPU |
| **Compiler and flags** | Baseline SDCC 4.6.0 #16608 (Linux), e.g. n-Body: 'sdcc -mz80 -DSTATIC -DTIMER --max-allocs-per-node200000 n-body.c' then makebin, timed with 'z88dk-ticks n-body.bin -start 0d7a -end 0dc0' (support/benchmarks/n-body/sdcc/readme.txt); Pi and Dhrystone use the same sdcc flags (Dhrystone adds -DNOSTRUCTASSIGN). z88dk classic zsdcc 4.6.0 #16639: 'zcc +test -vn -DSTATIC -DTIMER -D__Z88DK -compiler=sdcc -SO3 --max-allocs-per-node200000 n-body.c -o n-body.bin -lmath48 -m -lndos' (math32 rows use --math32); sccz80 classic math32: 'zcc +test -vn -DSTATIC -DTIMER -D__Z88DK -O2 n-body.c -o n-body.bin --math32 -m -lndos' (support/benchmarks/n-body/z88dk-classic/readme.txt). The __Z88DK define only enables intrinsic.h and printf/scanf options; it does not change the computation. |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/z88dk/z88dk) · [benchmark](https://github.com/z88dk/z88dk/wiki/Benchmarks) |

## Verdict

The project's wiki tables give exact Z80 cycle counts from z88dk-ticks for programs built by SDCC 4.6.0 #16608 (sdcc -mz80 --max-allocs-per-node200000) and by z88dk's zsdcc 4.6.0 #16639 and sccz80 builds, with every command line public under support/benchmarks. Against SDCC (ratios derived from page data): n-Body 1.94x with math48 and 5.07-5.40x with math32, Whetstone 2.02x and 5.13x, Fasta 1.71x and up to 3.34x, Pi 1.80x on newlib small and 3.62x on classic sccz80, Binary-Trees 1.30x (classic), Dhrystone 1.13x, Sieve 1.15x, Fannkuch 1.06x. The gains come mainly from the assembly float and 32-bit libraries.

## Use it when

- Float-heavy C on a Z80 (physics, Whetstone-style maths). With math32, n-Body runs in 0.81-0.86 G cycles against 4.36 G for SDCC 4.6.0 (5.1-5.4x) and 1.60 G for HI-TECH C 7.80 (about 2x).
- 32-bit integer arithmetic such as bignum-style division loops. The classic sccz80 library runs Pi in 1.99 G cycles against SDCC's 7.22 G (3.6x) in the default configuration.
- Retro and homebrew machines (ZX Spectrum, Spectrum Next, CP/M, MSX, RC2014, RomWBW, Game Boy), where z88dk's built-in targets, CRTs and appmake output formats save porting work.
- 8080 and 8085 targets, where sccz80 and 80cc are the supported compilers (zsdcc is Z80-only) and math32_8085 and mbf32 cores exist.
- Mixed C and assembly projects that want one assembler, linker and librarian (z80asm) with sections, macros and multi-CPU fat libraries.

## Skip it when

- Allocation-heavy code on the newlib library. Binary-Trees takes 6.57 G cycles against SDCC's 0.19 G (about 34x slower) because newlib malloc's first-fit search walks allocated blocks too. Issue #113 has been open since 2017; use the classic library (149 M cycles, 1.30x faster than SDCC) for such code.
- Tight integer loop code compiled with sccz80. On Sieve its builds take 4.67-4.96 M cycles against SDCC's 4.22 M, and on Fannkuch 67-77 M against 55.7 M. Only zsdcc with newlib wins, by 1.15x and 1.06x, and HI-TECH C 7.80 is fastest on Fannkuch.
- Code-size-critical builds that assume z88dk is always smaller. SDCC is smallest on Sieve and Dhrystone, HI-TECH C is smallest on Fannkuch, and math32 rows are larger than the older 48-bit rows.
- Projects that need strict IEEE-754 float semantics. math32 flushes denormals to signed zero, does not use round-to-nearest-even on add and subtract, and does not propagate NaN payloads.
- Projects that need an OSI-approved licence. The Clarified Artistic License is FSF-free but not OSI-approved, and individual files may carry other licences.

## How it is fast

Most of the speed comes from the libraries, not the compilers. The C standard library and the float and 32-bit integer runtimes are hand-written Z80 assembly, while SDCC ships C-implemented float and long routines (the wiki blames SDCC's losses on these). math32 is an assembly IEEE-754 single-precision package. It uses an unrolled 32_24x8 software mantissa multiply on a plain Z80, the hardware multiplies on Z80N, Z180, eZ80 and Rabbit, and a Quake magic-number seed plus three Newton-Raphson steps for sqrt. Its add and subtract use a cheaper jam-sticky rounding rule instead of round-to-nearest-even. The newlib 'fast integer' build reduces most 32-bit divides to 16-bit divides. zsdcc also uses the __z88dk_callee and __z88dk_fastcall calling conventions to pass arguments to library calls more cheaply.

## Compared with alternatives

Rasm is the only other Z80 sibling, a standalone cross-assembler with an assembly-throughput claim. Pick z88dk when you need C compilers plus optimised Z80 runtime libraries, not just fast assembly of large .asm sources. The x86 siblings (Zydis, iced, Keystone, JWasm, UASM) cover other ISAs and do not compete.

## Integration

| | |
|---|---|
| **Form** | cross toolchain (compilers, z80asm assembler/linker and prebuilt target libraries statically linked into the output binary) |
| **Dependencies** | Host side: prebuilt Windows and macOS nightlies, a Linux Snap, a Docker image, or a source build that needs git submodules (m4 is used for the macro pass). Target side: none beyond the chosen z88dk library. |
| **Minimum toolchain** | Not documented in the pages read for building from source. On the target side, sccz80 accepts near-C90 C and zsdcc accepts SDCC's larger C subset. |
| **Platforms** | Hosts: Windows, macOS, Linux. Target CPUs: 8080/8085, KR580VM1, gbz80, Z80, Z80N, Z180, eZ80 (Z80 mode), R800, Rabbit r2ka-r6k and KC160. Classic library targets cover more than 100 machines. |
| **Thread safety** | math32 says all of its code is re-entrant. Re-entrancy of the rest of the C library is not documented in the pages read. |
| **Drop-in for the baseline** | partial — zsdcc is the same SDCC 4.6.0 front end, but you build through zcc with a target, a -clib choice and z88dk headers. It uses __sdcccall(0) with z88dk callee/fastcall conventions, not stock SDCC's __sdcccall(1), so linking against objects from stock SDCC is not documented. |

## Gotchas

- Harness flaw in the baseline rows. All eight SDCC readmes (n-Body, Pi, Whetstone, Dhrystone, Fasta, Binary-Trees, Sieve, Fannkuch) derive TIMER_START and TIMER_STOP from .sym and .map values by hand, and in every one the documented arithmetic gives a different address from the one passed to z88dk-ticks. Examples: n-Body works out to 0xd83/0xdcc but ran with 0d7a/0dc0; Pi to 0x213/0x32e but ran with 0214/0363; Whetstone's stop to 0xbde but ran with 09ca, a window 532 bytes shorter. z88dk-ticks (cpu_run in src/ticks/ticks.c) resets its counter every time PC equals -start and halts the first time PC equals -end, so a wrong address silently changes the measured window. The z88dk rows look up the symbols from the map file (-x map -start TIMER_START), which avoids this. The counts are not at the -counter cap and their sizes look plausible, but the baseline windows cannot be checked without rebuilding.
- Rows are not all like for like. Whetstone and Fasta were timed with SDCC built without -DSTATIC, while every z88dk build used -DSTATIC (static rather than stack locals). Unlabelled z88dk float rows use 48-bit genmath or math48, which zsdcc narrows to 4 bytes. The newlib \*_FAST Pi rows need the z80 library rebuilt with __CLIB_OPT_IMATH=75, which is not the default. The wiki's sccz80 newlib Pi rows quote April 2020 counts (4,012,440,735 and 1,696,878,309) even though the readme has slower April 2022 remeasures (4,028,061,102 and 1,766,815,709).
- Since v2.5, -lm links math32 instead of genmath (classic) or math48 (newlib). Old build lines therefore change float width and precision silently; use --genmath, --math48 or --mbf64 to get the wider formats back.
- All cycle counts come from the project's own z88dk-ticks emulator, and the wall-clock columns are cycles divided by 4 MHz. The HI-TECH C and IAR rows were also run by the z88dk project, and HI-TECH C 7.80 is disqualified on Fasta for wrong output.

## Known shortcomings

- Gains come mostly from the assembly float and integer libraries; the NEW library is 34x slower on Binary-Trees and z88dk loses or barely wins on Sieve and Fannkuch (HI-TECH 7.80 fastest there); Pi and Dhrystone rows are against SDCC_NEW; weak category fit. Clarified Artistic License is not OSI-approved per SPDX (reference).
- Harness flaw in the baseline rows: all eight SDCC readmes hand-derive TIMER_START and TIMER_STOP addresses, and none of the documented sums match the addresses passed to z88dk-ticks (n-Body 0xd83/0xdcc derived vs 0d7a/0dc0 used; Pi 0x213/0x32e vs 0214/0363; Whetstone stop 0xbde vs 09ca); ticks.c resets the count at every start hit and halts at the first end hit, so the baseline windows cannot be verified without rebuilding. Whetstone and Fasta SDCC builds lack the -DSTATIC that every z88dk build uses, Pi \*_FAST rows need newlib rebuilt with __CLIB_OPT_IMATH=75, the wiki's Pi sccz80 newlib rows cite April 2020 counts although slower April 2022 remeasures exist (1,766,815,709 vs 1,696,878,309), and math32 is not strict IEEE (denormals flushed, add/sub not round-to-nearest-even).

## Caveats and trade-offs

The win is not uniform. With the NEW library Binary-Trees takes 6,570,984,020 cycles against 193,466,493 for plain SDCC (about 34x slower; the wiki blames the fast-realloc free-block search, issue #113), while the classic library is 1.30x faster. On Sieve the sccz80 builds (4.77M to 4.96M cycles) are slower than SDCC (4,218,689) and only Z88DK/SDCC_NEW (3,679,114) wins, by 1.15x and barely ahead of IAR (3,714,152); on Fannkuch HI-TECH C 7.80 is fastest and smallest (51,982,515 cycles, 868 bytes), sccz80 is slower than SDCC and SDCC_NEW wins by only 1.06x. The large n-Body, Whetstone, Fasta and Pi gains come mostly from z88dk's assembly-language float and 32-bit integer libraries replacing SDCC's C-implemented ones (the wiki says so), since zsdcc is z88dk's patched build of the same SDCC 4.6.0. Rows without a MATH32 label use pre-v2.5 genmath or math48 (48-bit) libraries and are not comparable to MATH32 rows; rows come from different dates (sccz80 NEW April 2021, sccz80 classic January 2022, zsdcc and SDCC August-September 2026). All results, including the HI-TECH C and IAR runs, were measured by the z88dk project itself. HI-TECH C 7.80 gives wrong Fasta output (DISQ). The baseline is a C compiler, not GNU as, NASM or MASM, and the z80asm assembler itself is not benchmarked, so the fit to assemblers-and-asm-tooling is weak. Clarified Artistic License is not OSI-approved and individual files may carry other licences. [retier] The win is not uniform: with the NEW library Binary-Trees is about 34x slower than plain SDCC (fast-realloc free-block search, issue #113), on Sieve only Z88DK/SDCC_NEW wins (1.15x) and the sccz80 builds lose, and on Fannkuch HI-TECH C 7.80 is fastest. Harness flaw in the baseline rows: all eight SDCC readmes (n-Body, Pi, Whetstone, Dhrystone, Fasta, Binary-Trees, Sieve, Fannkuch) hand-derive TIMER_START and TIMER_STOP from .sym and .map values, and none of the documented sums match the addresses passed to z88dk-ticks (n-Body 0xd83/0xdcc vs 0d7a/0dc0 used; Pi 0x213/0x32e vs 0214/0363; Whetstone stop 0xbde vs 09ca); ticks.c resets the count at every start hit and halts at the first end hit, so the baseline windows cannot be verified without rebuilding (the z88dk rows use map symbols). Whetstone and Fasta SDCC builds lack the -DSTATIC every z88dk build uses; Pi \*_FAST rows need newlib rebuilt with __CLIB_OPT_IMATH=75; the wiki's Pi sccz80 newlib rows cite April 2020 counts although slower April 2022 remeasures exist (1,766,815,709 vs 1,696,878,309); math32 is not strict IEEE (denormals flushed, add/sub not round-to-nearest-even). Cycle counts from an emulator, not a physical CPU.

Z80-family targets only; the speed comes from hand-written assembly libraries and a cheaper calling convention, with larger code in several rows (SDCC is smaller on Sieve, Fannkuch and Dhrystone sizes).

## Maintenance

Very active: 26,468 commits, eight commits on 2026-10-11 alone, 178 open issues and nightly builds. Usability is reference-grade because the Clarified Artistic License is not OSI-approved, but the toolchain is free to use and the benchmark sources and command lines are public, so a rebuild with symbol-based TIMER addresses for SDCC would settle the baseline windows.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now C.
- **Tier reason:** The wiki Benchmarks tables compare z88dk builds against SDCC 4.6.0 #16608, HI-TECH C 3.09/7.80 and IAR 4.06A, and every row is backed by public code in support/benchmarks/&lt;benchmark&gt;/ (base source plus per-compiler subdirectories whose readme.txt gives the exact command lines, compiler versions and the z88dk-ticks invocation). The 'hardware' is a cycle-exact Z80 emulator, so the counts are deterministic per binary and fully reproducible.
- **Retiered** A to C: Enricher: the baseline SDCC rows cannot be verified: all eight SDCC readmes hand-derive the TIMER_START/STOP addresses and none of the documented sums match the addresses passed to z88dk-ticks, whose counter resets at every start hit and halts at the first end hit; two SDCC builds lack -DSTATIC while every z88dk build has it, and the sccz80 Pi rows cite 2020 counts that 2022 remeasures contradict. First-party wiki with unverifiable baseline windows and build asymmetries: A to C.
- **Verifier notes:** All quoted cycle counts match the wiki tables (raw wiki markdown read) and the per-compiler readme.txt RESULT blocks; only the library labels for the Pi and Dhrystone rows were wrong. Category fit is weak: this is a C toolchain-plus-library comparison, so the orchestrator may want a category override to a compilers category; usability moved to reference because ClArtistic is not OSI-approved (SPDX isOsiApproved false).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `license`, `usability`, `caveats`
- **Shortcomings recorded by:** verifier batch-51 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/z88dk/z88dk/wiki/Benchmarks>
  - <https://raw.githubusercontent.com/wiki/z88dk/z88dk/Benchmarks.md>
  - <https://github.com/z88dk/z88dk>
  - <https://github.com/z88dk/z88dk/commits/master>
  - <https://github.com/z88dk/z88dk/tree/master>
  - <https://github.com/z88dk/z88dk/tree/master/support>
  - <https://github.com/z88dk/z88dk/tree/master/support/benchmarks>
  - <https://github.com/z88dk/z88dk/tree/master/support/benchmarks/n-body>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/n-body/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/n-body/sdcc/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/n-body/z88dk-classic/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/pi/sdcc/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/dhrystone21/sdcc/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/n-body/n-body.c>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/pi/pi.c>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/fasta/fasta.c>
  - <https://raw.githubusercontent.com/spdx/license-list-data/main/json/details/ClArtistic.json>
- **Sources the enricher read:**
  - <https://github.com/z88dk/z88dk>
  - <https://github.com/z88dk/z88dk/commits/master>
  - <https://github.com/z88dk/z88dk/issues/113>
  - <https://github.com/z88dk/z88dk/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/README.md>
  - <https://raw.githubusercontent.com/wiki/z88dk/z88dk/Benchmarks.md>
  - <https://raw.githubusercontent.com/wiki/z88dk/z88dk/Compilers.md>
  - <https://raw.githubusercontent.com/wiki/z88dk/z88dk/Tool---z80asm.md>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/libsrc/math/float/math32/readme.md>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/src/ticks/ticks.c>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/n-body/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/n-body/n-body.c>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/n-body/sdcc/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/n-body/z88dk-classic/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/n-body/z88dk-new/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/whetstone/whetstone.c>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/whetstone/sdcc/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/whetstone/z88dk-classic/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/whetstone/z88dk-new/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/pi/pi.c>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/pi/sdcc/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/pi/z88dk-new/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/fasta/fasta.c>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/fasta/sdcc/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/fasta/z88dk-classic/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/dhrystone21/sdcc/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/dhrystone21/z88dk-new/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/binary-trees/sdcc/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/sieve/sdcc/readme.txt>
  - <https://raw.githubusercontent.com/z88dk/z88dk/HEAD/support/benchmarks/fannkuch/sdcc/readme.txt>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/z88dk/z88dk`) · [data/wave13/enrich/raw/github_com_z88dk_z88dk.json](../../../data/wave13/enrich/raw/github_com_z88dk_z88dk.json) (enrichment confidence 0.6)

</details>
