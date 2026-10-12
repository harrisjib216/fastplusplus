# Rasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Single-file C Z80 cross-assembler (Amstrad CPC, ZX Spectrum) claiming tens of millions of instructions/s; SjasmPlus comparison unpublished.

| | |
|---|---|
| **Beats** | SjasmPlus (Z80 cross-assembler). The README only says 'the best alternatives' and names no competitor; SjasmPlus is named in a CPCWiki snippet that could not be opened. |
| **Claimed result** | README: 'peak performance around 100 millions instructions per second', 'tens of millions instructions per second on a modern CPU', 'way faster than the best alternatives' (no alternative named in the speed claim). CPCWiki RASM page (WebSearch snippet only, page unreachable here): '1 million lines in 0.03s on a modern computer, 100x faster than SjasmPlus'. Haiku depot package description (snippet only, page unreachable): '30 times faster than his best challenger'. The two multipliers disagree and neither has a published harness. |
| **Workload** | Assembling Z80 assembly source (Amstrad CPC demo-scale projects, e.g. a 512K cartridge of about 350,000 words); no benchmark input is published in the repo. |
| **Metric** | compile-time |
| **Hardware** | unstated ('a modern machine', 'a modern CPU') |
| **Adoption** | 167 stars, 21 forks, 638 commits; README lists Arkos Tracker, R-GX, RetroDev, PiStudio (Norecess) and the CPCSyntaxError emulator as built on or embedding RASM, plus an online playground (cpc-playground.iiivan.org) |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/EdouardBERGE/rasm) · [benchmark](https://github.com/EdouardBERGE/rasm) |

## Verdict

Only first-party absolute figures exist: the README claims a peak of about 100 million instructions per second and 'tens of millions' on a modern CPU, with no hardware, build, input or competitor stated; CPCWiki (1 million lines in 0.03 s, 100x SjasmPlus) and the Haiku depot (30x the 'best challenger') were seen as search snippets only and disagree. No timing harness, corpus or SjasmPlus version is in the repository.

## Use it when

- Large Amstrad CPC or ZX Spectrum projects (hundreds of thousands of source words, 512K cartridges, multi-bank snapshots) where assembler turnaround dominates the edit-build-run loop.
- Build pipelines that want one tool to assemble, crunch (ZX0, LZSA, AP-Ultra, Exomizer) and emit a cartridge, snapshot, EDSK or tape image without separate packer and disk-image steps.
- Embedding an assembler in an emulator, tracker or IDE through the RasmAssemble\* C API (one process, sequential assemblies).
- Retro-scene toolchains that need a self-contained C source with no external library beyond libm, buildable on Linux, macOS, Windows, MS-DOS and MorphOS.

## Skip it when

- Anything that is not Z80-family: it does not replace GNU as, NASM, MASM or the x86/ARM assemblers in this category.
- Projects written for SjasmPlus, z88dk's z80asm or VASM syntax: no compatibility mode exists for them (only old MAXAM, AS80, UZ80 and Pasmo), so porting is manual.
- Choosing on speed alone: there is no published benchmark, corpus or competitor run; the 100x (CPCWiki) and 30x (Haiku depot) ratios contradict each other and could not be checked.
- Concurrent assembly from several threads of one host process: the embedding API mutates and re-sorts the global instruction table on every call.
- Label-heavy sources on memory-tight hosts: each distinct label key can allocate up to three radix nodes of 256 pointers (about 2 KB each), trading memory for lookup speed (derived from the struct definitions in rasm.c).

## How it is fast

Sources are tokenised once into a word list; each word is dispatched to its directive or mnemonic through a fastmatch[first char][length] table into the keyword array (sorted by length, then name) and a 32-bit key compare before any strcmp, so most words cost one table lookup, one integer compare and one short string compare. Labels, variables and aliases are indexed by a cheap 32-bit key (an XOR of the name's 4-byte chunks, called 'CRC' in the code) through a 65,536-entry top table and two 256-way radix levels, with strcmp only inside the final bucket. Forward references are queued as expressions and resolved in one batch (PopAllExpression) rather than by a second full pass. The optional 'superfast' builds add mimalloc or tcmalloc for the many small allocations and compile with -DSUPERFAST, which removes several duplicate-name and reserved-word checks (see gotchas).

## Compared with alternatives

Pick it when the target is a Z80 machine and you want assembler, cruncher and disk/cartridge image output in one fast tool; z88dk (with its z80asm) is the better choice when the project mixes C and assembly through SDCC/zsdcc, and the x86 entries (Asmc, UASM, JWasm, minias, aron) do not cover Z80 at all.

## Integration

| | |
|---|---|
| **Form** | source-drop (single rasm.c of about 35,000 lines plus rasm.h, built into a CLI binary or linked with -DINTEGRATED_ASSEMBLY as an embedded library) |
| **Dependencies** | libm; bundled cruncher sources (apultra, lzsa with libdivsufsort, salvador ZX0, z80-master for autotests); optional mimalloc or tcmalloc for the superfast targets; 'make third' builds without the third-party crunchers |
| **Minimum toolchain** | Any C compiler (cc/gcc, clang, recent MSVC, MSVC 15 for Windows XP, mingw-w64); no language standard stated; the superfast targets call clang explicitly |
| **Platforms** | Linux x64 and ARM (including Raspberry Pi), macOS Intel and ARM, Windows 32/64-bit, MS-DOS, MorphOS (README); output targets are Z80 machines (Amstrad CPC/Plus, ZX Spectrum) |
| **Thread safety** | Not documented. The CLI assembles single-threaded (optional RASM_THREAD only parallelises crunching); the embedding API rewrites and qsorts the global instruction[] keyword table inside every PreProcessing call and keeps a static counter, so concurrent calls race. |
| **Drop-in for the baseline** | partial: a different assembler with its own directive set; it does not accept SjasmPlus syntax, and offers compatibility only with old MAXAM, AS80, UZ80 and Pasmo sources |

## Gotchas

- The 'make superfastmi' / 'make superfasttc' builds the README recommends for extra speed on Linux define SUPERFAST, which compiles out the checks that a label is not a reserved register name (A, BC, HL, IX, IXL ...) and that labels, variables and aliases do not collide; invalid sources that the normal build rejects are accepted silently. Which build produced the 'around 100 millions instructions per second' peak is not stated.
- Every makefile target compiles with -march=native, so a binary built from the makefiles is tied to the build machine's CPU; rebuild without it for distributable binaries.
- The embedding API aborts the host process on fatal conditions: dozens of exit() calls outside the autotest code (unreadable include or INCBIN file, thread creation failure, overlapping replace strings, missing input file) bypass the error structure returned to the caller.
- Label lookup keys XOR the name's 4-byte chunks, so names whose chunks repeat or are permuted (for example 'ABCDEFGH' and 'EFGHABCD') share a bucket and fall back to linear strcmp; correctness holds but generated label sets can lose the fast path (derived from GetCRC in rasm.c).

## Known shortcomings

- First-party peak throughput only ("100 millions instructions per second"), no harness, corpus, flags or CPU in the repo and no named baseline; the ratios against other assemblers come from snippets that disagree (CPCWiki 100x SjasmPlus, Haiku depot 30x the best challenger) and the peak may assume a mimalloc build.
- Enricher: speed figures are first-party with no benchmark code or corpus in the repo and the 100x vs 30x ratios remain snippet-only; the README's recommended superfastmi/superfasttc builds define -DSUPERFAST, which compiles out the reserved-register label checks and the label/variable/alias collision checks, and it is unstated whether the 100M instructions per second peak came from that build; every makefile target uses -march=native; the embedding API is not reentrant (rewrites and qsorts the global instruction[] per call with static counters) and exit() aborts the host process.

## Caveats and trade-offs

No benchmark script, input corpus, hardware, compiler flags or competitor version is in the repo (top-level tree shows only sources, makefiles and build scripts). The README's speed claim names no alternative; SjASM, SjASMPlus, VASM, Pasmo, UZ80, BASM and ORGAMS appear only in a 'other assemblers you could try' list, not as measured baselines. The 100x SjasmPlus ratio (CPCWiki) and the 30x 'best challenger' ratio (Haiku depot) are snippet-only and contradict each other. SjasmPlus's own README claims '1 million lines by 2-3 seconds on modern computer', so 100x compares two self-reported numbers (derived from page data and snippet). 'Instructions per second' is not directly comparable with lines per second. The peak figure may assume the mimalloc build ('make superfastmi'), which the README says gives significant improvements on Linux; unstated which build was timed.

Z80 family only (Amstrad CPC, ZX Spectrum and similar); not a replacement for GNU as, NASM or MASM. README recommends the mimalloc build ('make superfastmi') on Linux for extra speed.

## Maintenance

Actively maintained (v3.3.2 dated 04/10/2026 in rasm.h, last commit 2026-10-06, 638 commits, 2 open issues) and MIT-licensed; usable as a production CLI or embedded C source, but its speed advantage is unmeasured by anyone else and the fastest build drops some error checks.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README (benchmark_url) gives only first-party absolute throughput ('peak performance around 100 millions instructions per second', 'tens of millions instructions per second on a modern CPU') and an unnamed 'way faster than the best alternatives'; no benchmark code, corpus, compiler, flags, CPU model or competitor numbers exist in the repo. The only ratios against named assemblers (100x SjasmPlus on CPCWiki, 30x 'best challenger' on the Haiku depot listing) are snippet-only, first-party-style claims, so C (numbers without methodology).
- **Verifier notes:** Real, active (last commit 2026-10-06), MIT-licensed Z80 assembler with notable retro-scene adoption, but its speed claims are first-party absolute throughput only, with no harness and no named baseline on the repo page; keep at C with the 'no reproducible comparison, conflicting snippet-only multipliers (100x vs 30x)' shortcoming. CPCWiki (cpcwiki.eu), rasm.wikidot.com docs and depot.haiku-os.org all failed DNS here (ENOTFOUND), so their wording is from WebSearch snippets only. License, last_commit, maintenance_status and usability in the record are correct.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-47 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/EdouardBERGE/rasm>
  - <https://github.com/EdouardBERGE/rasm/commits>
  - <https://github.com/EdouardBERGE/rasm/tree/master>
  - <https://raw.githubusercontent.com/EdouardBERGE/rasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/EdouardBERGE/rasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/z00m128/sjasmplus/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/EdouardBERGE/rasm>
  - <https://raw.githubusercontent.com/EdouardBERGE/rasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/EdouardBERGE/rasm/HEAD/makefile>
  - <https://raw.githubusercontent.com/EdouardBERGE/rasm/HEAD/Makefile.linux>
  - <https://raw.githubusercontent.com/EdouardBERGE/rasm/HEAD/rasm.h>
  - <https://raw.githubusercontent.com/EdouardBERGE/rasm/HEAD/rasm.c>
  - <https://github.com/EdouardBERGE/rasm/issues?q=is%3Aissue>
  - <https://github.com/EdouardBERGE/rasm/issues?page=2&q=is%3Aissue>
  - <https://github.com/EdouardBERGE/rasm/issues/14>
  - WebSearch: rasm Z80 assembler speed benchmark sjasmplus "million lines" seconds (CPCWiki and Haiku depot snippets only)
  - https://oldwiki.cpcwiki.eu/index.php/RASM (failed: ENOTFOUND)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/edouardberge/rasm`) · [data/wave13/enrich/raw/github_com_edouardberge_rasm.json](../../../data/wave13/enrich/raw/github_com_edouardberge_rasm.json) (enrichment confidence 0.65)

</details>
