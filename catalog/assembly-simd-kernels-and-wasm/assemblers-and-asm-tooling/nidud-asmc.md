# Asmc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly` · `GPL-2.0-or-later` · 🟢 active

> Self-hosted MASM-syntax x86/x64 assembler descended from JWasm; forum timings put it about 1.5x faster than Microsoft's ML.

| | |
|---|---|
| **Beats** | MASM (Microsoft Macro Assembler 6.15 and 10.0), also compared with JWasm and UASM |
| **Claimed result** | Snippet only: in a masm32.com thread (msg=92718) jj2007 timed a 21,000-line source at 1200 ms for AsmC versus 1800 ms for MASM 6.15 and 10.0 (1.5x, derived from snippet data), 1480 ms JWasm and 1630 ms UAsm64. A 2021 post by the same user (msg=102515) times a full build of the 22k+ line RichMasm source at 1259 ms with AsmC versus 2185 ms with ML 10.0 (about 1.7x, derived from snippet data) and 1688 ms with UAsm64, for 32-bit code. Another poster (msg=129297) says UAsm is about 25% slower than AsmC. The README makes no speed claim. |
| **Workload** | Assemble time of a 21,000-line MASM-syntax source in a forum user's test. |
| **Metric** | compile-time |
| **Adoption** | 91 stars |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/nidud/asmc) · [benchmark](https://masm32.com/board/index.php?msg=92718) |

## Verdict

Third-party forum timings only: jj2007 on masm32.com assembled a 21,000-line MASM source in 1200 ms with Asmc against 1800 ms with both ML 6.15 and ML 10.0 (1.5x, derived from snippet data), and in a 2021 post built the 22k+ line RichMasm source in 1259 ms against 2185 ms for ML 10.0 (about 1.7x, derived from snippet data). Hardware, Asmc versions and method are not stated, and the posts were seen only as search snippets.

## Use it when

- Large MASM-syntax code bases (Windows x86/x64) where ml/ml64 assembly time is a visible part of the build and you can validate the object output.
- You need MASM syntax on Linux producing ELF or ELF64 objects, which ML cannot do.
- You need instructions that older ML releases lack: the change log adds AVX-512 VBMI/VBMI2/FP16/VP2INTERSECT, AVX10.1/10.2, GFNI and APX extended registers in 2.39-2.40.
- Writing new assembly where the HLL extensions (.switch, .for, .class, inline C strings, invoke with expressions) save effort and you accept an Asmc-only dialect.

## Skip it when

- You need output identical to MASM: by default Asmc generates different code for HLL constructs and prologues (test reg,reg instead of or reg,reg; .untilcxz as dec ecx/jnz instead of loop; sub instead of add -size), so object diffs against ML fail unless you pass -Zg.
- You need a toolchain that builds from source without trusting a binary: the build needs a prebuilt asmc committed in bin/, and the maintainer says a 32-bit build 'cant be done without a binary' (issue #18).
- Assembly is a small share of build time: the measured gain is about 1.5-1.7x on a 21-22k-line source (roughly 0.6-0.9 s saved per build in those forum runs).
- You want a vendor-supported or widely deployed assembler: Asmc has 91 stars and one main author; a regression left the ELF64/Linux build broken from 2.39.09 to 2.39.15 (issue #36, fixed 2026-10-01).
- You cannot accept GPL-2.0-or-later for a tool you modify or redistribute.

## How it is fast

It keeps JWasm's architecture: the FASTPASS optimisation stores preprocessed lines in memory during pass one and replays them in later passes instead of re-reading and re-expanding the sources (fastpass.asm). Most allocations come from a bump-pointer arena that carves 512 kB chunks and frees them only at exit (LclAlloc in memalloc.asm). Symbols are looked up in FNV-style hash tables (32K global and 4K local buckets, symbols.asm), and reserved words use a table whose hashes are computed when Asmc itself is built (reswords.asm). Since 2.14 (2015) the C code inherited from JWasm has been ported to hand-written assembly and the tool now builds itself; no profile says which of these accounts for the gap to ML.

## Compared with alternatives

Against its JWasm-lineage siblings JWasm and UASM, pick Asmc when you want the fastest of the three in the same forum test (1200 ms vs 1480 ms JWasm and 1630 ms UAsm64) and the most recent instruction-set coverage and releases (v2.40, October 2026); prefer JWasm if you want a MASM clone without Asmc's dialect changes. The other siblings (minias, aron, Keystone) target GNU or Apple assembler syntax or embedding, not MASM.

## Integration

| | |
|---|---|
| **Form** | standalone command-line tool (prebuilt asmc, asmc64, asmc.exe and asmc64.exe in bin/, plus linkw, libw, make and Visual Studio .props/.targets files) |
| **Dependencies** | none at run time; building from source needs a prebuilt Asmc binary and make. Windows setup runs asmc-2.40.cmd (it offers to build the bundled libc and import libraries); Linux 'make install' uses sudo to write /usr/bin, /usr/lib/asmc and /etc/profile.d/asmc-profile.sh |
| **Minimum toolchain** | Prebuilt binaries; a source build needs an existing Asmc recent enough to assemble the current sources (issue #36: before the fix, hll.asm needed a 2.39.11 or later bootstrap; with the patch a 2.39.08 bootstrap built 2.39.15) |
| **Platforms** | Hosts: Windows x86/x64 and Linux x86/x86-64. Targets: 16/32/64-bit x86 with COFF, ELF/ELF64, OMF, PE, MZ and flat binary output |
| **Thread safety** | not applicable: single-threaded command-line tool with global assembler state, one process per invocation |
| **Drop-in for the baseline** | partial: ML-style command line and MASM syntax, but default code generation differs from Masm (use -Zg), Masm-only keywords such as SIZE, LENGTH, TYPE, HIGH, LOW, THIS and MASK are treated as identifiers unless -Zne is given, @Version reports 1000 (Masm 10), and source using Asmc's HLL extensions will not assemble with ML |

## Gotchas

- Default code generation is not Masm's: doc/command/option-zg.md lists the differences (test vs or, dec/jnz vs loop, byte-sized test on memory operands, prologue sub vs add -size); -Zg restores Masm output.
- Masm keywords HIGH, LOW, LENGTH, SIZE, TYPE, THIS, MASK, WIDTH, NAME, PAGE and TITLE are free identifiers by default; -Zne gives them their Masm meaning (doc/command/option-zne.md), so unmodified Masm sources that use them need that switch.
- Lineage: history.txt says Asmc began in 2011 as 'a modified version of JWASM' and tracked JWasm releases 2.09-2.12 before diverging, so it is a JWasm descendant even though the record's is_fork_of is null; JWasm and UASM are catalogued siblings with the same MASM claim from the same forum thread.
- Speed evidence cannot be checked: the numbers exist only in masm32.com forum snippets (masm32.com does not resolve here, ENOTFOUND) with no hardware, versions or method, and no benchmark harness lives in the repo. A 2020 snippet attributed to the author (nidud) gives 4181 clock ticks for asmc, 4867 for jwasm and 7285 for uasm64 assembling the MASM32 library (no ML row, first-party, thread URL not identified), and a 2024 snippet's '7-8x faster than MASM' contradicts the 1.5-1.7x timings.

## Known shortcomings

- Forum anecdote only (masm32.com blocked, snippet): about 1.5x vs MASM, a 2021 post about 1.7x (derived); no methodology, the README makes no claim.
- Speed numbers exist only as masm32.com forum snippets (1.5-1.7x vs ML; masm32.com fails with ENOTFOUND here) and the repo has no benchmark harness; a 2020 snippet attributed to nidud gives MASM32 library build ticks of 4181 asmc vs 4867 jwasm vs 7285 uasm64 with no ML row, and a '7-8x' snippet contradicts the 1.5x. history.txt: started in 2011 as a modified JWasm and tracked JWasm 2.09-2.12, so is_fork_of is corrected to JWasm. Default codegen differs from Masm (-Zg needed); Masm keywords SIZE/LENGTH/TYPE need -Zne; the build needs a prebuilt binary (issue #18); the ELF64 build was broken in 2.39.09-2.39.15, fixed in #36.

## Caveats and trade-offs

The MASM-compatible assembler timing numbers appear only in a WebSearch result snippet of a masm32.com forum thread (page unreachable here: ENOTFOUND), recorded as 'snippet only'; the same thread says on a 21,000-line source MASM 6.15 and 10.0 took 1800 ms each, UAsm64 1630 ms, JWasm 1480 ms and AsmC 1200 ms. Anecdotal forum measurement, no hardware, flags or versions seen. One poster in the same snippet says the same extensions make him distrust the tool, and another snippet claim of a '7-8x' speed-up over MASM contradicts the 1.5x timing above. [retier] The MASM-compatible assembler timing numbers appear only in WebSearch snippets of masm32.com forum threads (masm32.com fails with ENOTFOUND here): on a 21,000-line source MASM 6.15 and 10.0 took 1800 ms each, UAsm64 1630 ms, JWasm 1480 ms and AsmC 1200 ms (jj2007, msg=92718); a 2021 post times a full RichMasm build at 1259 ms AsmC vs 2185 ms ML 10.0 and 1688 ms UAsm64; a 2020 snippet attributed to the author (nidud) gives 4181 clock ticks for asmc, 4867 for jwasm and 7285 for uasm64 assembling the MASM32 library (no ML row, first-party); a 2024 snippet's '7-8x faster than MASM' contradicts the 1.5-1.7x timings. Anecdotal forum measurements with no hardware, flags, versions or method, and no benchmark harness in the repo; the README makes no speed claim. Lineage: a JWasm descendant (history.txt), so JWasm and UASM are catalogued siblings with the same MASM claim from the same forum thread. Default code generation is not Masm's (-Zg restores it); Masm keywords HIGH, LOW, LENGTH, SIZE, TYPE, THIS, MASK, WIDTH, NAME, PAGE and TITLE need -Zne; building needs a prebuilt binary (issue #18); the ELF64 build was broken in 2.39.09-2.39.15 (fixed in #36).

Written in assembly (MASM syntax, self-hosted); runs on Windows and Linux; GPL licence; MASM compatibility is not perfect (the project adds its own macro/language extensions and claims MASM v14 AVX-512 support while its Version macro is v10).

## Maintenance

Actively maintained (v2.40 released 2026-10-10, 1,349 commits, 0 open and 17 closed issues), GPL-2.0-or-later with prebuilt Windows and Linux binaries, so it is easy to try as a tool; the speed case is anecdotal and the build cannot be bootstrapped without an existing binary.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are third-party forum timings (masm32.com, user jj2007) with no hardware, versions or methodology, known only from search snippets because masm32.com is unreachable here (ENOTFOUND); the repo makes no speed claim. Numbers without methodology are tier C.
- **Verifier notes:** Confirmed at C: anecdotal third-party forum timings, snippet only (masm32.com ENOTFOUND here); benchmark_url set to the thread found by WebSearch (not opened). Metadata checked: 91 stars, GPL-2.0-or-later (license.txt: GPL version 2 or later), last commit 2026-10-10 (v2.40), active. Not a duplicate of UASM or JWasm (separate project, own claim); Asmc's JWasm lineage was not verified here, so is_fork_of left null.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `is_fork_of`, `caveats`
- **Shortcomings recorded by:** verifier batch-08 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/nidud/asmc>
  - <https://github.com/nidud/asmc/commits>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/license.txt>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/readme.md>
- **Sources the enricher read:**
  - <https://github.com/nidud/asmc>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/readme.md>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/source/asmc/history.txt>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/source/asmc/makefile>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/source/asmc/asmc-profile.sh>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/asmc-2.40.cmd>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/doc/command/readme.md>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/doc/command/option-zg.md>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/doc/command/option-zne.md>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/doc/symbol/at-version.md>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/doc/tools/readme.md>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/source/asmc/src/fastpass.asm>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/source/asmc/src/memalloc.asm>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/source/asmc/src/symbols.asm>
  - <https://raw.githubusercontent.com/nidud/asmc/HEAD/source/asmc/src/reswords.asm>
  - <https://github.com/nidud/asmc/tree/master/source/asmc/src>
  - <https://github.com/nidud/asmc/tree/master/bin>
  - <https://github.com/nidud/asmc/issues>
  - <https://github.com/nidud/asmc/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/nidud/asmc/issues/18>
  - <https://github.com/nidud/asmc/issues/36>
  - https://masm32.com/board/index.php?msg=92718 (attempted, ENOTFOUND; content known from WebSearch snippets only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/nidud/asmc`) · [data/wave13/enrich/raw/github_com_nidud_asmc.json](../../../data/wave13/enrich/raw/github_com_nidud_asmc.json) (enrichment confidence 0.5)

</details>
