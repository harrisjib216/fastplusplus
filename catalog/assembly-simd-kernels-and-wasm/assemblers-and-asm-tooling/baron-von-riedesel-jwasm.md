# JWasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Watcom-1.0` · 🟢 active

> Portable MASM v6-compatible x86/x64 assembler in C; forum timings put it modestly ahead of ml.exe on assembly time.

| | |
|---|---|
| **Beats** | MASM (Microsoft Macro Assembler) |
| **Claimed result** | jwasm.sourceforge.net comparison table, Masm row: 'Since v1.9, JWasm is faster than Masm.' (no numbers on that page). Snippet only (masm32.com thread msg=92718, user jj2007): 1480 ms for JWasm versus 1800 ms for MASM 6.15 and 10.0 on a 21,000-line source (about 1.2x, derived from snippet data). |
| **Workload** | Assemble time of MASM-syntax sources. |
| **Metric** | compile-time |
| **Adoption** | 163 stars; basis of UASM and Asmc |
| **Last commit** | 2026-06-30 |
| **Links** | [repository](https://github.com/Baron-von-Riedesel/JWasm) · [benchmark](https://jwasm.sourceforge.net/) |

## Verdict

There is no reproducible benchmark. JWasm's own 2009 sourceforge page says only that it has been faster than Masm since v1.9. The numbers come from one forum poster's machine via search snippets: JWasm 1480 ms vs MASM 6.15 and 10.0 at 1800 ms on a 21,000-line source (about 1.2x). Other snippets give 5.5 s vs 6.9 s for ML 6.15 on a 28k-line library and 4997 ms vs 16356 ms for ML 10.0 building m32lib (about 1.25x and 3.3x, derived from snippet data). No hardware, JWasm version or flags are given.

## Use it when

- Building existing MASM-syntax code (Masm32, WinInc, DOS or OS/2 projects) on Linux or in CI without ml.exe, with direct ELF, COFF, OMF, PE, MZ or BIN output.
- Large sources that pull in big header files of equates and structures, where FASTPASS avoids rescanning them in every pass.
- Sources with huge data arrays: the manual notes Masm is very slow on them and can deadlock with COFF output.
- Targets or hosts outside Microsoft's toolchain: 16-bit DOS (a reduced build runs on an 8088), OS/2, or a small dependency-free C assembler to vendor.

## Skip it when

- AVX2, FMA, AVX-512 or BMI code: the opcode tables (src/H/instravx.h, src/H/instruct.h) carry AVX entries such as vaddpd, vpaddd and vbroadcastss but no vpbroadcastd, vpermq, vpgatherdd, vpsllvd, vfmadd\*, kmovw, andn or pdep.
- When assembly speed is the point: in the same masm32-forum timings Asmc was faster (1200 ms vs 1480 ms on a 21,000-line source; 3901 ms vs 4997 ms building m32lib).
- Code that depends on OPTION OLDMACROS, EXPR16 or READONLY, on exact Masm listing output, or on ml options such as -link, -Fe, -Fm, -Sc or -Fr, none of which are implemented.
- Licence-sensitive redistribution: files are mixed Sybase Open Watcom Public License 1.0 and public domain, there is no root licence file, and the manual may only be redistributed free of charge (relicensing request #20 unanswered).
- Projects written for NASM or GNU as syntax: JWasm only speaks MASM syntax.

## How it is fast

FASTPASS stores preprocessed source lines in memory during pass one, starting at the first instruction or data item, and replays only those lines in later passes. Large leading include files of equates and types (windows.inc from Masm32 or WinInc) are therefore scanned once, not once per pass. Symbols live in chained hash tables (hashpjw; 8009 global and 127 local buckets, the local table added in v1.95 because the earlier linked list was too slow with many local labels). FASTMEM is a bump allocator over 512 kB mmap/VirtualAlloc chunks that frees nothing until exit, and v2.03 cut the average number of passes.

## Compared with alternatives

Among the MASM-compatible siblings, Asmc posted faster forum timings and UASM (HJWasm) was faster on some sources and slower on others. Pick JWasm for the conservative upstream line with a long changelog of Masm-compatibility fixes, DOS and OS/2 hosts, and a C99 code base that builds with almost any compiler. Look at the forks when you need newer instruction sets or maximum assembly speed.

## Integration

| | |
|---|---|
| **Form** | built tool (standalone command-line executable from C sources; MsvcDll.mak and OWWinDll.mak build a Windows DLL) |
| **Dependencies** | none beyond the C runtime |
| **Minimum toolchain** | C99 (GccUnix.mak uses gcc -std=gnu99 -O2; makefiles also for Clang, MSVC, Open Watcom, Intel C, Pelles C, TCC, PCC and BCC); GCC 15's default C23 mode breaks the build ('bool' typedef, old-style function pointers, open issue #52), so keep -std=gnu99 |
| **Platforms** | hosts: Windows, Linux, FreeBSD, DOS (16- and 32-bit), OS/2; targets: x86 16/32-bit and x86-64 (ELF64, Win64 COFF/PE) |
| **Thread safety** | Not reentrant: symbol hash tables and module state are static globals (src/symbols.c), so run one assembly per process. |
| **Drop-in for the baseline** | partial — accepts MASM v6 (and most v8) syntax and the common ml command-line options, but never invokes a linker, ignores PAGE/TITLE/SUBTITLE, and lacks OPTION OLDMACROS/EXPR16/READONLY and options -AT, -Sp, -Ss, -St, -H and -Ta |

## Gotchas

- The speed claim is the 2009 sourceforge line 'Since v1.9, JWasm is faster than Masm.' with no numbers. All timings are masm32/masmforum posts seen only as WebSearch snippets (forum hosts unreachable here), measured on posters' own machines. They point both ways: a 2010 JWasm build regressed to about 2,700 ms vs ml's 800 ms on a 12,000-line source, and a 2012 post claimed MASM was about 3x faster on some code (unconfirmed in the thread).
- No AVX2, FMA, AVX-512 or BMI mnemonics in the opcode tables; History.txt through v2.21 never mentions them.
- Open output-correctness issues: non-zero RELA section contents with pre-2.37 binutils linkers (#12, #57), an internal error in coff.c(1490) (#56) and LEA moffs16 handling (#22). The v2.21 changelog fixes wrong ELF64 addends with explicit addends and per-pass code-buffer leaks for non-OMF formats.
- ELF output now defaults to position-independent code (-pic1) in v2.21, which can change code generated from the same source compared with v2.20.

## Known shortcomings

- The SourceForge page says 'faster than Masm' with no numbers (2009 era); a forum 1.2x figure is snippet-only. Watcom-1.0 per-file headers, some files public domain, no root LICENSE.
- Enricher: no AVX2/FMA/AVX-512/BMI in the opcode tables; mixed per-file licences and a free-of-charge-only manual; GCC 15's C23 default breaks the build (#52, use -std=gnu99); newer forum timings (snippet only) are mixed (m32lib 4997 vs ML 10.0 16356 ms, a 28k-line library 5.5 vs 6.9 s, but a 2010 build regressed to 2,700 vs 800 ms) and Asmc is faster.

## Caveats and trade-offs

The sourceforge page states the speed advantage without numbers, and the page itself dates from 2009 (latest releases listed: v1.96 of 07/26/2009 and v2.0pre of 08/31/2009), so the claim refers to 2009-era versions. The GitHub README makes no speed claim. No licence file at the repo root: source files carry per-file headers, some 'Public Domain' (src/main.c, src/assemble.c) and others under the Sybase Open Watcom Public License 1.0 (src/parser.c, src/codegen.c); the sourceforge page also names the Sybase Open Watcom Public License. The timing numbers appear only in a WebSearch result snippet of a masm32.com forum thread (https://masm32.com/board/index.php?msg=92718, unreachable here: ENOTFOUND); the same thread says on a 21,000-line source MASM 6.15 and 10.0 took 1800 ms each, UAsm64 1630 ms, JWasm 1480 ms and AsmC 1200 ms. Anecdotal forum measurement, no hardware, flags or JWasm version seen. The GitHub repository continues the JWasm line (changelog now at v2.21) and carries the 2009-era 'faster than Masm' claim forward unverified.

MASM v6-compatible assembler for Windows, Linux, DOS and OS/2; Sybase Open Watcom Public License (OSI-listed but not GPL-compatible); complex MASM macros may not assemble identically.

## Maintenance

Actively maintained (v2.20 released 01.12.2025, v2.21 in progress, last commit 2026-06-30, 11 open issues) and small enough to vendor, but the licensing is mixed per file and the speed advantage rests on 2009-era claims and forum anecdotes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The benchmark_url (jwasm.sourceforge.net) compares against Masm but only states 'Since v1.9, JWasm is faster than Masm.' with no numbers; the only numbers are a third-party masm32.com forum timing known from a search snippet (site unreachable here), with no methodology. First-party claim plus snippet-only anecdotal numbers is tier C.
- **Verifier notes:** Confirmed at C: sourceforge page compares with Masm but gives no numbers; forum numbers snippet only. Licence Watcom-1.0 confirmed from per-file headers (mixed with public-domain files; no root LICENSE), copyable stands. Metadata checked: 163 stars, not a fork, last commit 2026-06-30, active.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-08 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Baron-von-Riedesel/JWasm>
  - <https://github.com/Baron-von-Riedesel/JWasm/commits>
  - <https://jwasm.sourceforge.net/>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/History.txt>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/assemble.c>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/parser.c>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/codegen.c>
- **Sources the enricher read:**
  - <https://github.com/Baron-von-Riedesel/JWasm>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/History.txt>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/Html/Manual.html>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/GccUnix.mak>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/fastpass.c>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/H/fastpass.h>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/H/globals.h>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/symbols.c>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/memalloc.c>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/H/instravx.h>
  - <https://raw.githubusercontent.com/Baron-von-Riedesel/JWasm/HEAD/src/H/instruct.h>
  - <https://github.com/Baron-von-Riedesel/JWasm/issues>
  - <https://github.com/Baron-von-Riedesel/JWasm/issues/52>
  - <https://github.com/Baron-von-Riedesel/JWasm/issues/20>
  - <https://jwasm.sourceforge.net/>
  - https://masmforum.com/board/index.php?msg=102214 (unreachable: ENOTFOUND; WebSearch snippets only for masm32.com and masmforum.com threads)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/baron-von-riedesel/jwasm`) · [data/wave13/enrich/raw/github_com_baron_von_riedesel_jwasm.json](../../../data/wave13/enrich/raw/github_com_baron_von_riedesel_jwasm.json) (enrichment confidence 0.6)

</details>
