# Free Pascal 3.2.2: compile throughput in nordlow/compiler-benchmark

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Pascal` · `GPL-2.0-or-later` · 🟢 active

> Free Pascal 3.2.2 compiles a generated 40,000-function file 1.9-3.9x faster than GCC at -O0; clang still wins.

| | |
|---|---|
| **Beats** | C (gcc-15 15.3.0, gcc 16.2.1, clang 23.1.1) and C++ (g++-15 15.3.0, g++ 16.2.1, clang++ 23.1.1) compiling the same generated arithmetic translation unit (200 call chains of depth 200, 40000 functions) with default optimization (no -O flag) |
| **Claimed result** | README table (Modern Systems Languages, sample run as of 2026-09): Free Pascal (fpc 3.2.2) Total 138 us/f (137 build + 0.20 run) and Compile 103.6 us/f, against C (gcc-15 15.3.0) 392 Total and 193.8 Compile, C (gcc 16.2.1) 454 Total and 400.1 Compile, C++ (g++-15 15.3.0) 303 Total and 269.6 Compile, C++ (g++ 16.2.1) 486 Total and 372.3 Compile, C++ (clang++ 23.1.1) 236 Total and 82.4 Compile (untemplated rows). Total: about 2.8x faster than gcc-15, 3.3x than gcc 16.2.1 and 1.7x than untemplated clang++ (derived from page data); link-free Compile column: about 1.9x faster than gcc-15, 3.9x than gcc 16.2.1, 2.6x than g++-15 and 3.6x than g++ 16.2.1 (derived from page data). Clang beats Free Pascal: C (clang 23.1.1) 118 Total and 77.9 Compile, C++ (clang++ 23.1.1) 82.4 Compile and 107 Total on the templated variant. |
| **Workload** | Microseconds per function to build (compile plus link) and to compile only a single generated file of 200 x 200 trivial Int64 add-chains; the 'Total' column is build plus a run of the resulting binary, the 'Compile' column is object-only |
| **Metric** | compile-time |
| **Hardware** | AMD Ryzen AI 7 350 (8+8 cores) at 5.09 GHz, Arch Linux, sample run as of 2026-09; one worker per core, tasks pinned with sched_setaffinity and run in parallel, minimum of up to 10 runs |
| **Compiler and flags** | cbench script, fpc: build 'fpc -O- -B -Aas -o&lt;bin&gt;' (no optimization, rebuild all, GNU assembler), compile 'fpc -Cn -O-'. gcc and g++: 'gcc -Wall -Wextra -o &lt;bin&gt; main.c', 'g++ -Wno-c++11-extensions', compile with -c, i.e. the default optimization level (-O0) with warnings enabled for C; clang the same with extra diagnostics flags. Linker not stated. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | The README attributes fast compile speed to compiler architecture (single translation unit of arithmetic chains, no header parsing) but gives no Pascal-specific explanation. Inference: Free Pascal's unit system needs no preprocessing or textual includes and it builds with -O-. |
| **Adoption** | benchmark repo 167 stars; Free Pascal is a long-established compiler (GitLab project, 75386 commits) |
| **Last commit** | 2026-10-12 |
| **Links** | [repository](https://gitlab.com/freepascal.org/fpc/source) · [benchmark](https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md) |

## Verdict

In one run of nordlow/compiler-benchmark (tables updated 2026-10-09) on an AMD Ryzen AI 7 350 under Arch Linux, the harness compiled a generated program of 200 x 200 Int64 add-chain functions. fpc 3.2.2 at -O- built it (GNU as plus ld) in 137 us per function and compiled it to an object in 103.6. The same C program at default -O0 with -Wall -Wextra took 392 Total and 193.8 object-only with gcc 15.3.0, 454 and 400.1 with gcc 16.2.1, and 303 and 269.6 with g++ 15.3.0. clang 23.1.1 was faster than fpc (118 Total, 77.9 object-only).

## Use it when

- You already write Pascal (Free Pascal or Lazarus code) and care about debug-build turnaround: on this file fpc's object-only compile (103.6 us per function) is about 1.9x faster than gcc 15 (193.8) and 2.6x faster than g++ 15 (269.6).
- Large generated sources such as tables or state machines, where an unoptimized GCC build dominates the edit-compile loop and clang is not an option.
- Projects that want one self-contained compiler and runtime with no libc dependency, across Linux, Windows, macOS and the BSDs.
- As a reference point when comparing toolchains: on this workload fpc sits between clang (faster) and every GCC row (slower).

## Skip it when

- When clang is available: clang C compiled the same file faster (77.9 against 103.6 us/f object-only, 118 against 138 Total), and clang++ was faster object-only (82.4).
- For release builds: only -O- was measured, so there is no number for fpc -O2 or -O3 against gcc -O2.
- To predict real project builds: the workload is one synthetic file of 40,000 Int64 add-chain functions that uses only the System unit and no headers.
- When you need to compile existing C or C++: fpc is a different language, and interop goes through external declarations.
- When the exact compiler version matters: 3.2.2 is the 2021 stable release (tag release_3_2_2, 2021-05-15); 3.2.4-rc2 (2026-08-26) and the 3.3.1 main branch were not measured.

## How it is fast

The benchmark gives no Pascal-specific reason. The FPC 3.2.2 source shows that x86-64 Linux defaults to the internal ELF64 object writer (assem: as_x86_64_elf64 in compiler/systems/i_linux.pas), so the link-free Compile step ('fpc -Cn -O-') skips the textual-assembly round trip through GNU as that 'gcc -c' always pays. Inference, not measured: fpc reads precompiled units (.ppu) instead of preprocessed headers and at -O- does far less intermediate-representation work than GCC, whose GIMPLE and RTL pipeline still runs at -O0.

## Compared with alternatives

Among the nordlow/compiler-benchmark siblings, dmd (13 us/f Total) and Zig (110) build faster, while Odin (147), Hare (150), C3 (153) and rustc (187) are close or slower. fpc has a link-free Compile figure (103.6) below every GCC row and the smallest binaries in the table (probably helped by stripping). Pick it when you already use Pascal; for raw compile speed dmd or clang win.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (command-line compiler 'fpc'; distribution packages or a source build) |
| **Dependencies** | GNU ld on Linux (linkextern ld_linux in i_linux.pas); GNU as only when -Aas is passed, as in this benchmark's build step; no libc by default |
| **Minimum toolchain** | fpc 3.2.2 as measured (stable release, tagged 2021-05-15) |
| **Platforms** | x86-64 targets in 3.2.2 include Linux, Win64, Darwin, FreeBSD, NetBSD, OpenBSD, DragonFly, Solaris, AROS and embedded (option list in compiler/msg/errore.msg); measured only on x86-64 Arch Linux |
| **Thread safety** | not applicable (command-line compiler); the compiler's own threading is not documented in what was read |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: fpc's Check and Compile cells run the same command. bm_Pascal in cbench passes '-Cn -O-' for both 'check' and 'compile', so the 98.7 us/f Check cell is a full object compile, not a syntax check, and its 5% gap to the 103.6 Compile cell is run-to-run noise between identical commands. Each fpc step takes 4 to 5.5 s, so the adaptive rule keeps the minimum of only 2 runs.
- Inside fpc's own row the two columns use different assemblers: Compile uses fpc's default internal ELF writer, while Build adds -Aas and pushes a textual .s file through GNU as before GNU ld, so the 33 us/f gap between Build (137) and Compile (103.6) is extra assembling plus linking, which works against fpc in the Total column. Conversely, the Compile column sets fpc's internal object writer against 'gcc -c', which emits assembly and runs GNU as (clang uses an integrated assembler). Even taken conservatively, fpc's full build with GNU as and ld (137) is still about 1.4x faster than gcc 15's object-only compile (193.8) (derived from page data).
- The '68.8 B/f, most compact machine code' figure is probably not like for like. The stock fpc.cfg template (utils/fpcmkcfg/fpc.cft in 3.2.2) adds -Xs (strip all symbols) whenever DEBUG is not defined, and cbench passes no strip flag to gcc or clang, so on a stock install the Pascal binary is stripped while the C binaries keep symbol tables for 40,000 functions. The benchmark machine's fpc.cfg was not published. The same template also turns on -Sgic, -l and -viwn.
- Noise and baselines: tasks run concurrently, one pinned worker per core on a hybrid Zen 5 and Zen 5c part, and nothing checks the built program's output or exit code. Sibling enrichers found gcc 15's Total (392) at twice its own Compile (193.8). The 3.3x to 3.9x ratios against gcc 16.2.1 rest on a GCC 15-to-16 slowdown that the README itself flags as a regression, and the README's section 3 quotes different figures (226.7 to 382.6 us/f) from its table (193.8 to 400.1). The gcc 15 Compile column (about 1.9x) is the safer comparison.

## Known shortcomings

- Wins over GCC only: clang C beats it on the link-free Compile column (77.9 vs 103.6 us per function) and clang++ on Compile (82.4) and templated Total (107); Total cells are noisy and linking is not uniform across toolchains (same caveats as the Odin, Zig and rustc rows); cbench builds gcc and clang at default -O0 and fpc at -O-; FPC last commit unverifiable (gitlab.com).
- Enricher: bm_Pascal runs the same `fpc -Cn -O-` command for Check and Compile, so the Check cell (98.7 us/f) is a full compile; Build adds -Aas (GNU as) while Compile uses fpc's internal ELF writer; the 'most compact output' figure (68.8 B/f) is probably a stripping artifact (the stock fpc.cfg adds -Xs, gcc and clang get no strip flag; the machine's fpc.cfg is unpublished). Conservative ratio: about 1.4x over gcc-15's object-only compile. The README summary now quotes clang at 118 and its section 3 GCC figures differ from the table.

## Caveats and trade-offs

The workload is one synthetic 40000-function translation unit of arithmetic with no includes, standard library or optimization, so it does not predict real project build times; at -O2 or -O3 the gcc and clang numbers would be much larger and Free Pascal's -O- row would not be a like-for-like release build. The C compilers are run with -Wall -Wextra (C) and warnings diagnostics that fpc does not get. The Total column adds the run time of the produced binary (0.10 to 0.21 us/f, clang C shows 1.2) and includes linking; the linker used is not stated, Free Pascal is forced to the external GNU assembler by -Aas, while Zig is run with -fno-llvm -fno-lld (own backend and linker) and DMD uses its own backend, so linking work is not uniform across rows. The win holds only against GCC: clang beats Free Pascal in C (118 against 138 Total, 77.9 against 103.6 Compile) and clang++ beats it in the link-free Compile column (82.4 against 103.6) and on the templated Total (107); the 1.7x over clang++ rests on the untemplated Total cell, where clang++'s link step dominates (236 Total against 82.4 Compile). Free Pascal has only an untemplated row. Run-to-run movement on the same machine is large: the README's Conclusions section quotes older numbers than its own table (clang 87 us/f against 118 in the table, gcc 418 to 455 against 392 to 454), and the sibling records' enrichers found the Total cells noisy (20% or more) because the pool runs compilers concurrently on a mixed Zen 5/Zen 5c part, so the Compile column is the more reliable comparison. Parallel pinned workers share caches and memory bandwidth. Both Pascal and Hare sit in the README's 'Modern Systems Languages' table. [retier] Enricher: Check and Compile run the same fpc command (Check is a full compile); Build adds -Aas while Compile uses the internal ELF writer; the 'most compact output' figure is probably a stripping artifact (stock fpc.cfg adds -Xs); conservative ratio about 1.4x over gcc-15 object-only.

The generated Pascal binary is the most compact of the table (68.8 bytes per function against 121.1 for gcc) but the optimizing-compile cost is not measured: every compiler runs unoptimized. Check-only mode costs 98.7 us/f, close to its full compile, because fpc has no cheap syntax-only pass.

## Maintenance

Free Pascal is actively developed: GitLab main had commits on 2026-10-12, 3.2.4-rc2 was tagged 2026-08-26, and the compiler is GPL-2.0-or-later per the verification record. The measured 3.2.2 is the 2021 stable release, and the evidence is one single-machine run of a public MIT harness whose fpc Check cell repeats the Compile command and whose size column probably compares a stripped Pascal binary with unstripped C binaries.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness (cbench in nordlow/compiler-benchmark, MIT): bm_Pascal runs 'fpc -Cn -O-' for compile and 'fpc -O- -B -Aas -o&lt;bin&gt;' for build, gcc_clang_op_flags plus bm_C_and_Cxx_using_gcc/clang give gcc/clang -Wall -Wextra and g++/clang++ -Wno-c++11-extensions with -c or -o at the default -O0, DEFAULT_FUNCTION_COUNT and DEFAULT_FUNCTION_DEPTH are 200, the README table names every compiler version and the CPU (AMD Ryzen AI 7 350, Arch Linux). Same tier as the sibling Zig, Odin, C3 and D rows of this suite.
- **Verifier notes:** All numbers match the README table rows; flags confirmed in cbench (bm_Pascal lines 1864-1897, C_WARN_FLAGS/CXX_WARN_FLAGS lines 398-399, bm_C_and_Cxx_using_gcc/clang). Both sides are unoptimized builds (fpc -O-, gcc/clang default -O0), which is symmetric for a compile-throughput metric. Shortcomings: win over GCC only (clang C and clang++ compile-only are faster), Total cells noisy and include non-uniform linking, synthetic single-file workload; last_commit 2026-10-12 for the GitLab FPC source could not be checked (page did not render activity) and is left as recorded; GitLab shows GPL-2.0-or-later and 75,386 commits.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-117 (wave 14 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cbench>
  - <https://github.com/nordlow/compiler-benchmark>
  - <https://gitlab.com/freepascal.org/fpc/source>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/process_timer.py>
  - <https://github.com/nordlow/compiler-benchmark/commits>
  - <https://github.com/nordlow/compiler-benchmark/issues?q=is%3Aissue+pascal+OR+fpc+OR+hare>
  - <https://gitlab.com/freepascal.org/fpc/source/-/raw/release_3_2_2/compiler/systems/i_linux.pas>
  - <https://gitlab.com/freepascal.org/fpc/source/-/raw/release_3_2_2/compiler/msg/errore.msg>
  - <https://gitlab.com/freepascal.org/fpc/source/-/raw/release_3_2_2/utils/fpcmkcfg/fpc.cft>
  - <https://gitlab.com/api/v4/projects/freepascal.org%2Ffpc%2Fsource/repository/tags?per_page=15>
  - <https://gitlab.com/api/v4/projects/freepascal.org%2Ffpc%2Fsource/repository/commits?per_page=3>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:free-pascal/nordlow/compiler-benchmark#compile-throughput`) · [data/wave14/enrich/raw/lang_free_pascal_nordlow_compiler_benchmark_compile_throughput.json](../../../data/wave14/enrich/raw/lang_free_pascal_nordlow_compiler_benchmark_compile_throughput.json) (enrichment confidence 0.6)

</details>
