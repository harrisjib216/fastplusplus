# UASM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Watcom-1.0` · 🟡 slow

> Open-source MASM-syntax x86/x64 assembler descended from JWasm; forum timings put it modestly ahead of MASM, behind JWasm and AsmC.

| | |
|---|---|
| **Beats** | MASM (Microsoft Macro Assembler 6.15 and 10.0) |
| **Claimed result** | Snippet only (masm32.com forum post by jj2007, April 2020, not opened): on a 21,000-line source, MASM 6.15 1800 ms, MASM 10.0 1800 ms, UAsm64 1630 ms, JWasm 1480 ms, AsmC 1200 ms (UASM about 1.1x faster than MASM, derived from snippet data). Same thread, m32lib samples: UAsm64 7285 ClockTicks vs JWasm 4867 and AsmC 4181 (no MASM figure in the snippet). The README makes no speed claim. |
| **Workload** | Assemble time of a 21,000-line MASM-syntax source in a forum user's test. |
| **Metric** | compile-time |
| **Adoption** | 271 stars |
| **Last commit** | 2022-03-16 |
| **Links** | [repository](https://github.com/Terraspace/UASM) |

## Verdict

One masm32.com forum user (jj2007, April 2020; snippet only, no hardware or flags) assembled a 21,000-line MASM source in 1630 ms with UAsm64 against 1800 ms with MASM 6.15 and 10.0 (about 1.1x), while JWasm took 1480 ms and AsmC 1200 ms. Other thread snippets give UASM a 1.4x to 5x lead over various ML versions but put it about 25% behind AsmC. Nothing is reproducible.

## Use it when

- Building existing MASM-syntax code (masm32-style projects, hand-written x64 kernels) on Linux or macOS, or anywhere ml64 is unavailable or unlicensed
- Sources that need AVX-512 or other recent instructions together with MASM macros, INVOKE and calling-convention helpers for both Win64 and SystemV
- Large single-file sources where JWasm-style fastpass beats MASM's re-reading passes (forum anecdote: 21,000 lines in 1630 ms vs 1800 ms for MASM 6.15/10.0)
- Projects that already rely on UASM extensions (OO macro library, string literals, @Platform/@Arch built-ins) that ml64 does not have

## Skip it when

- When raw assembly speed is the goal: in the same forum tests AsmC (1200 ms) and JWasm (1480 ms) beat UASM's 1630 ms, and on the m32lib build UAsm64 took 7285 ticks vs JWasm 4867 and AsmC 4181
- Toolchains on GCC 15 or recent clang without extra flags: open build failures #228/#233 (C23 'bool' typedef in H/bool.h), #232, #211 (-fwritable-strings), #197 (clang), #183/#148 (macOS)
- Code that needs bit-exact MASM behaviour: open reports of MASM-inconsistent RECORD operations (#230), wrong encodings (#213 vpextrw, #225 SHRX family, fixed only on the unreleased v2.58 branch), ignored unnamed Unicode string data (#221) and missing CodeView line data (#234)
- Shipping modified builds inside a company without publishing them: the Open Watcom licence counts internal business use as 'Deploy' and then requires the modified source to be published
- New code targeting Intel APX or other post-AVX-512 extensions (#209 open)

## How it is fast

The speed comes from JWasm's design, which UASM keeps. 'Fastpass' (fastpass.c) stores preprocessed lines in memory during pass 1 and replays them in later passes instead of re-reading and re-expanding the source and include files; '-nfp' turns it off. FASTMEM (memalloc.c) is a bump allocator over 512 KB chunks taken from VirtualAlloc or mmap. A larger symbol hash table (2003 to 8009 buckets) gave JWasm a 10-20% speed-up on symbol-heavy sources (History.txt). Nothing in the repo measures UASM's own speed.

## Compared with alternatives

Among MASM-compatible assemblers, AsmC and JWasm are faster on every forum timing; pick UASM only when you need its extensions (AVX-512 and MPX coverage, SystemV/VECTORCALL INVOKE, Mach-O output, the OO macro library) or already have UASM-dialect sources. Disassemblers such as iced or Zydis solve a different problem.

## Integration

| | |
|---|---|
| **Form** | command-line executable built from C source (no GitHub releases; binaries are offered on terraspace.co.uk, not checked here) |
| **Dependencies** | none beyond a C compiler and the C runtime |
| **Minimum toolchain** | near-C89 C with 64-bit integers; makefiles for GCC, clang, MSVC (VS2019 solution), Open Watcom, Intel C, Pelles C and others. GCC 10+/clang 11+ need -fcommon; GCC 15's C23 default fails on 'typedef unsigned char bool' (#228); forcing an older -std probably works but is not documented |
| **Platforms** | hosts: Windows, Linux, macOS, DOS; targets: x86 16/32/64-bit code only |
| **Thread safety** | single-threaded tool built on global assembler state (ModuleInfo, the fastpass LineStore); the DLL build (MsvcDll.mak) is not reentrant |
| **Drop-in for the baseline** | partial: accepts most MASM/ml64 syntax and command-line conventions, but encodings and edge-case semantics differ on open issues, and UASM extensions are not accepted by MASM |

## Gotchas

- master is stale: it stops at version 2.53pre (last commit 2022-03-16, the date the catalogue records), but development continues on per-version branches: v2.57 (2024-08-12) and v2.58, still marked 'pre' in H/globals.h, last committed 2025-11-30. Build from the latest vNN branch, not master.
- The built-in macro library is expanded on pass 1 of every module unless you pass -nomlib. This is a fixed per-file cost and may be one reason UASM trails JWasm on many-small-file builds such as m32lib (untested). Its 64-bit SHIFTLEFT128 macro ends with 'mov rcx,savercx' then 'mov rcx,saversi', so it returns with rcx holding the caller's rsi and rsi still pointing at the operand (macrolib.c, v2.58). The 128-bit shift macros also save registers in static .data? slots, which makes the generated code non-reentrant.
- No benchmark harness exists: every speed number is a masm32.com forum anecdote (jj2007, 2020) seen only in search snippets, with no hardware or exact versions. Other snippets disagree on the MASM margin: newer ML64 'only about 40% slower' versus ML '3-5x slower' than UASM, and for UASM's predecessor HJWasm, 12551 ms vs ML 10.0 16356 ms on m32lib.
- Readme.txt and Doc/ are still JWasm's original texts, and History.txt stops at 2.40, so the changes in 2.41-2.58 are documented only in commits and on the unreachable project site.

## Known shortcomings

- One forum user's timing, snippet only (masm32.com blocked): 1630 ms vs MASM 1800 ms, about 1.1x, with JWasm and Asmc faster in the same test. Abandoned since 2022-03-16. Watcom-1.0 licence.
- Record correction on maintenance: master is frozen at 2.53pre (2022-03-16), but per-version branches continue (v2.57 2024-08-12, v2.58 last commit 2025-11-30), so it is slow rather than abandoned. Correctness bug in v2.58 macrolib.c SHIFTLEFT128: it ends with 'mov rcx,savercx' then 'mov rcx,saversi', so rcx is wrong and rsi is never restored (not behind any numbers). Builds fail on GCC 15 (C23 bool typedef, #228/#233), clang (#197) and macOS (#183); the OWPL licence counts internal business use as Deploy. Speed evidence is still forum snippets only; extra snippets say newer ML64 is only about 40% slower and older ML 3-5x slower.

## Caveats and trade-offs

Numbers seen only in WebSearch snippets of masm32.com forum posts (site unreachable here: ENOTFOUND); single user, one machine, no hardware, flags or exact versions. The margin over MASM is small (about 1.1x) and UASM is the slowest of the three MASM-compatible open assemblers in the same test: JWasm (1480 ms) and AsmC (1200 ms) are faster, and on the m32lib samples UAsm64 took about 1.5x JWasm's and 1.7x AsmC's ClockTicks; another forum member calls UASM 'rather slow' compared with other assemblers. UASM descends from JWasm via HJWasm (the README's chat link is still named HJWASM) but is not a GitHub fork. Last commit 2022-03-16 on the only branch (master), no releases on GitHub; project site terraspace.co.uk unreachable here. Licence is the Sybase Open Watcom Public License 1.0 (OSI-approved; GitHub's sidebar does not name it).

Described in search snippets as a JWasm-based MASM-compatible assembler; Sybase Open Watcom Public License 1.0; adds 64-bit and AVX-512 support per project descriptions (not verified here).

## Maintenance

Not abandoned as recorded: master froze at 2.53pre in March 2022, but the v2.58 branch had fixes through 2025-11-30 (SHRX encoding, NOT operator, RECORD, djgpp). Activity is slow, many build and encoding issues stay open without maintainer replies, there are no GitHub releases, and the Sybase Open Watcom Public License 1.0 (License.txt) requires publishing source of modified builds that are deployed, including internal business use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are a single forum user's (jj2007, masm32.com, April 2020) assemble times of a 21,000-line source, confirmed by a second WebSearch snippet but not openable here (masm32.com ENOTFOUND); an anecdote without hardware, versions or method is C at most, kept at C under the harness's snippet-only rule.
- **Verifier notes:** Repo confirmed: 271 stars, 62 forks, 673 commits, not archived, last commit 2022-03-16 (abandoned, over 3 years), Watcom-1.0 licence text in README. Shortcomings: anecdotal snippet-only forum timing, only about 1.1x over MASM 6.15/10.0, slower than JWasm and AsmC (both already in wave 13 merged.json as baron-von-riedesel/jwasm and nidud/asmc), abandoned. A masm32 forum snippet also says AsmC is 25-30% faster than UAsm and 7-8x faster than MASM (MASM version unstated), which hints that newer ML versions may be much slower than the 6.15/10.0 figures; not usable as a number without the page.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-09 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Terraspace/UASM>
  - <https://github.com/Terraspace/UASM/commits>
  - <https://github.com/Terraspace/UASM/branches>
  - <https://raw.githubusercontent.com/Terraspace/UASM/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/Terraspace/UASM>
  - <https://raw.githubusercontent.com/Terraspace/UASM/HEAD/README.md>
  - <https://raw.githubusercontent.com/Terraspace/UASM/HEAD/Readme.txt>
  - <https://raw.githubusercontent.com/Terraspace/UASM/HEAD/History.txt>
  - <https://raw.githubusercontent.com/Terraspace/UASM/HEAD/License.txt>
  - <https://raw.githubusercontent.com/Terraspace/UASM/HEAD/Makefile_Linux>
  - <https://raw.githubusercontent.com/Terraspace/UASM/HEAD/fastpass.c>
  - <https://raw.githubusercontent.com/Terraspace/UASM/HEAD/memalloc.c>
  - <https://raw.githubusercontent.com/Terraspace/UASM/HEAD/H/globals.h>
  - <https://github.com/Terraspace/UASM/issues>
  - <https://github.com/Terraspace/UASM/issues/228>
  - <https://github.com/Terraspace/UASM/commits>
  - <https://github.com/Terraspace/UASM/branches/all>
  - <https://github.com/Terraspace/UASM/commits/v2.58>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/README.md>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/History.txt>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/H/globals.h>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/H/bool.h>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/Makefile-Linux-GCC-64.mak>
  - <https://github.com/Terraspace/UASM/tree/v2.58/Doc>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/Doc/enh.txt>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/Doc/overview.txt>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/cmdline.c>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/H/usage.h>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/macrolib.c>
  - <https://raw.githubusercontent.com/Terraspace/UASM/v2.58/assemble.c>
  - WebSearch: UASM JWasm AsmC ML64 assembly speed timing ms masm32 forum (snippets of masm32.com msg=92718, 59871, 59170, 129297, 105041 and others; pages not opened)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/terraspace/uasm`) · [data/wave13/enrich/raw/github_com_terraspace_uasm.json](../../../data/wave13/enrich/raw/github_com_terraspace_uasm.json) (enrichment confidence 0.6)

</details>
