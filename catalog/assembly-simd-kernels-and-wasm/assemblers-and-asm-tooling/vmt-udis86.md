# udis86

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-2-Clause` · 🔴 abandoned

> Small table-driven C x86/x86-64 decoder; in decode-only mode it beat Zydis, bddisasm and XED, but it formats slowest.

| | |
|---|---|
| **Beats** | Zydis, bddisasm and Intel XED (decode only); it loses to Capstone and Zydis in decode+format |
| **Claimed result** | Decode only: udis86 80.72 MB/s vs Zydis 34.19, bddisasm 35.48 and XED 55.39 MB/s (about 2.36x, 2.28x and 1.46x, derived from page data); diStorm 92.17, yaxpeax 182.08 and iced 256.69 MB/s are faster. Decode+format: udis86 12.02 MB/s, slower than Capstone 14.02 MB/s and Zydis 22.24 MB/s. |
| **Workload** | Decode-only throughput in MB/s over the 77 MB x86-64 code section of Firefox 86.0.1 xul.dll in the disas-bench shootout of nine x86 disassembler libraries. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-6600K |
| **Compiler and flags** | Kubuntu 21.04, gcc 10.3.0; make-all.sh builds udis86 with ./configure --enable-static=yes and no LTO (comment: LTO makes the build extremely slow), while Capstone, Zydis, bddisasm, XED and diStorm are built with -flto |
| **Adoption** | 1.1k stars |
| **Last commit** | 2014-12-25 |
| **Links** | [repository](https://github.com/vmt/udis86) · [benchmark](https://github.com/icedland/disas-bench) |

## Verdict

The measurement is icedland/disas-bench (2021, Kubuntu 21.04, gcc 10.3.0, i5-6600K), one run per library over the 77 MB .text of Firefox 86.0.1 xul.dll. It recorded udis86 at 80.72 MB/s decode-only, against Zydis 34.19, bddisasm 35.48 and XED 55.39 MB/s (about 2.36x, 2.28x and 1.46x, derived from page data), with udis86 built at -O2 without LTO. In decode+format udis86 was last at 12.02 MB/s, below Capstone's 14.02. Upstream athre0z/disas-bench later dropped udis86, so no newer run exists.

## Use it when

- Quick length decoding or mnemonic and operand inspection of SSE-era x86-64 code (up to SSE4.2, AES and AVX1) in a C or C++ tool where a BSD-2 licence and a single small library matter.
- Maintaining an existing tool that already uses the udis86 API, where porting would cost more than the ISA gaps.
- Decode-only scans (instruction boundaries and opcode classes) where 80.72 MB/s on a 2021 Skylake was enough and you never print the text.

## Skip it when

- Modern compiler output: the opcode table has no AVX2 (vpbroadcast\*, vpermd, vinserti128, gathers), FMA3 (vfmadd\*), BMI1/BMI2 (bextr, pdep, shlx, tzcnt), LZCNT, F16C, ADX or EVEX/AVX-512 entries, so those bytes decode as invalid.
- Producing text: at 12.02 MB/s decode+format it was the slowest of nine libraries, behind Capstone (14.02 MB/s) and far behind Zydis (22.24), diStorm (58.85) and iced (149.21).
- Anything that needs accuracy guarantees or security hardening. There have been no commits since Dec 2014; 48 issues are open, among them wrong-decoding reports #129 (operand size), #126 (truncated jump target with 0x66), #107 (rdtscp on Intel) and #101 (popfw in 64-bit mode), plus 22 unmerged PRs; there is no fuzzing (OSS-Fuzz request #130 is open).
- When raw decode speed is the goal: in the same harness iced (256.69 MB/s), yaxpeax-x86 (182.08) and diStorm (92.17) decoded faster.

## How it is fast

Decoding is a walk over generated lookup tables. scripts/ud_itab.py compiles docs/x86/optable.xml into itab.c, and decode_ext() follows table pointers keyed by opcode byte, mod, reg, rm, mode, operand size, SSE prefix and VEX.L/W until it reaches an instruction entry. Per-instruction work is small: one ud_t reused across calls, no dynamic allocation, only explicit operands decoded, and no flags, implicit-operand or CPUID metadata. Formatting is a separate pass (the translator pointer runs only in ud_disassemble) built on vsnprintf, which is why decode+format is slow.

## Compared with alternatives

Rarely. diStorm3 is also plain C and beat udis86 in both modes of the same harness (92.17 against 80.72 MB/s decode, 58.85 against 12.02 MB/s decode+format), and Zydis, bddisasm or XED give full modern ISA coverage. Keep udis86 only for an existing integration or a tiny SSE-era decoder with a BSD-2 licence.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at run time; Python is needed at build time to generate itab.c and itab.h from optable.xml, and autotools for the Unix build (a VS2010 project is included) |
| **Minimum toolchain** | C89-era C compiler with autoconf/automake/libtool. Python 3 builds need the ud_opcode.py fix that disas-bench applies with sed (issues #120, #123). |
| **Platforms** | any host that compiles C; decodes 16-, 32- and 64-bit x86 code |
| **Thread safety** | Re-entrant per the README: all state lives in the caller's ud_t, so use one ud_t per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- The decode-only rows are not like for like. The bddisasm harness skips 1 byte after a failed decode, while udis86 consumes every byte it has read so far and marks them invalid. No row counts invalid instructions or checks that the libraries walked xul.dll the same way, so the AVX2, FMA and BMI bytes udis86 cannot decode can change its path through the file. udis86's ud_decode also returns less per instruction (explicit operands only) than full-mode decoders. Against Zydis in its minimal mode (Zydis (min), 61.33 MB/s) the lead shrinks to about 1.32x (derived from page data), compared with 2.36x against default Zydis.
- Build handicap, not an advantage: make-all.sh runs udis86's ./configure with no CFLAGS, so the library gets the autoconf default -g -O2 without LTO. The other C libraries were built with -flto (XED with --opt=3, Capstone and bddisasm as CMake Release). Each library ran once (bench.py, clock() CPU time, MB meaning MiB).
- The record's ISA note needs a correction. master's docs/x86/optable.xml does contain VEX and AVX1 forms (SSE entries tagged 'sse avx', vbroadcastss, vinsertf128, vperm2f128, vzeroupper, vtestps); it lacks AVX2, FMA, BMI and AVX-512, although the README lists extensions only up to SSE4.2/AES.
- Building is fragile on current toolchains: the generated itab order varies between Python versions (#144), and autoconf and Arch Linux build errors are open (#142, #146). The uninitialised curr reported in decode_prefixes against 1.7.2 (#116) is initialised on master, so build from master, not the 1.7.2 tarball.

## Known shortcomings

- Slower than Capstone in decode+format (0.86x) in the 2021 icedland disas-bench single-run snapshot; its only lead is decode-only against Zydis, bddisasm and XED. No AVX-512 support, dropped from the upstream disas-bench suite, abandoned since 2014.
- The decode-only rows are not like for like: the bddisasm harness skips 1 byte after a failed decode while udis86 consumes the bytes read so far, with no invalid count and no cross-check; against Zydis (min) the lead is about 1.32x, not 2.36x. udis86 was built at the autoconf default -g -O2 with no LTO (a handicap against the -flto competitors). Record correction: optable.xml has VEX and AVX1 forms but lacks AVX2, FMA, BMI and AVX-512.

## Caveats and trade-offs

Loses to the incumbent: decode+format 12.02 MB/s is the slowest row of the table, below Capstone 14.02 (about 0.86x, derived from page data) and Zydis 22.24 MB/s; the win is decode-only against Zydis, bddisasm and XED, where Capstone cannot run. iced, yaxpeax and diStorm decode faster. Shootout run once per library by the iced maintainers (a competitor) in 2021; udis86 was later dropped from the upstream athre0z/disas-bench, so no newer run exists, and in that suite's 2025 runs on newer CPUs bddisasm (about 103-106 MB/s) and Zydis (min) (about 90-104 MB/s) decode much faster than in 2021, so the decode-only lead is a 2021 snapshot. udis86 was built without LTO (library and bench) while the others used -flto, which handicaps udis86 rather than helping it. Narrower ISA coverage: the README lists extensions up to SSE4.2/AES and decode.c has partial VEX but no EVEX/AVX-512 handling, so unsupported bytes are marked invalid; the bench does not count invalid instructions or check that rows decode the file the same way, and part of the decode-only lead may come from that narrower coverage. Last commit December 2014 (abandoned). [retier] Loses to the incumbent: decode+format 12.02 MB/s is the slowest row of the table, below Capstone 14.02 (about 0.86x, derived from page data) and Zydis 22.24 MB/s; the win is decode-only against Zydis, bddisasm and XED, where Capstone cannot run, and against Zydis (min) the lead is about 1.32x, not 2.36x. Harness asymmetry: the bddisasm driver skips 1 byte after a failed decode while udis86 consumes every byte it has read so far and marks them invalid; no row counts invalid instructions or checks that the libraries walked xul.dll the same way, so the AVX2, FMA and BMI bytes udis86 cannot decode can change its path through the file, and ud_decode also returns less per instruction. Build handicap: make-all.sh runs udis86's ./configure with no CFLAGS (autoconf default -g -O2, no LTO) while XED, Capstone and bddisasm were built with -flto; each library ran once (bench.py, clock() CPU time, MB meaning MiB). The shootout was run once per library by the iced maintainers (a competitor) in 2021; udis86 was later dropped from upstream athre0z/disas-bench, so no newer run exists, and in that suite's 2025 runs bddisasm and Zydis (min) decode far faster. ISA coverage: master's docs/x86/optable.xml contains VEX and AVX1 forms (vbroadcastss, vinsertf128, vperm2f128, vzeroupper, vtestps) but lacks AVX2, FMA, BMI and AVX-512, although the README lists extensions only up to SSE4.2/AES. Building is fragile on current toolchains (#142, #144, #146); build from master, not the 1.7.2 tarball (#116).

Old, abandoned library; README lists MMX, x87, 3DNow, SSE through SSE4.2, AES, AMD-V, VMX and SMX and does not mention AVX or AVX-512, so it cannot decode current code; decoder tables are generated with Python scripts; slowest formatter in the shootout (12.02 MB/s decode+format, below BeaEngine's 13.42).

## Maintenance

Abandoned since Dec 2014 (293 commits, 1.1k stars, 319 forks, BSD-2-Clause), with no AVX2 or AVX-512 coverage. It is copyable and small, but suits only legacy integrations. A 2025 community fork (MIvanchev/udis86, issue #147) is two commits ahead and announces no ISA work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** icedland/disas-bench README lists udis86 at 80.72 MB/s decode only and 12.02 MB/s decode+format next to Zydis 34.19, bddisasm 35.48, XED 55.39 and Capstone 14.02; the harness is public (bench.py, make-all.sh, bench/udis86/main.c and Makefile with -O3, no LTO) with gcc 10.3.0 and an i5-6600K stated, run by a third party (the iced maintainers).
- **Verifier notes:** Numbers match the icedland/disas-bench README rows exactly; tier A holds (public harness, gcc 10.3.0, flags in make-all.sh and bench/udis86/Makefile, i5-6600K). Metadata confirmed on github.com: BSD-2-Clause, 1.1k stars, not archived, last commit 2014-12-25 (abandoned). Shortcomings: slower than Capstone in decode+format, decode-only win only over Zydis/bddisasm/XED in a 2021 single-run snapshot, no AVX-512 coverage, abandoned since 2014.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-42 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/icedland/disas-bench>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/udis86/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/udis86/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-amd.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-intel.png>
  - <https://github.com/vmt/udis86>
  - <https://github.com/vmt/udis86/commits>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/README>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/CHANGES>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/libudis86/decode.c>
- **Sources the enricher read:**
  - <https://github.com/vmt/udis86>
  - <https://github.com/vmt/udis86/issues>
  - <https://github.com/vmt/udis86/issues/116>
  - <https://github.com/vmt/udis86/issues/147>
  - <https://github.com/MIvanchev/udis86>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/README>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/CHANGES>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/docs/x86/optable.xml>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/libudis86/decode.c>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/libudis86/decode.h>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/libudis86/udis86.c>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/libudis86/types.h>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/libudis86/udint.h>
  - <https://raw.githubusercontent.com/vmt/udis86/HEAD/libudis86/syn.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/load_bin.inc>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/udis86/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/udis86/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/zydis/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/xed/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/bddisasm/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/distorm/main.c>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/vmt/udis86`) · [data/wave13/enrich/raw/github_com_vmt_udis86.json](../../../data/wave13/enrich/raw/github_com_vmt_udis86.json) (enrichment confidence 0.8)

</details>
