# D dmd compile throughput (nordlow/compiler-benchmark) vs clang, gcc, clang++ and g++

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `D` · `BSL-1.0` · 🟢 active

> dmd, the reference D compiler: unoptimized builds of a 40,000-function synthetic file 7.6x faster than clang, 19-39x faster than gcc.

| | |
|---|---|
| **Beats** | clang 23.1.1, gcc 15.3.0 and 16.2.1 (C) and clang++ 23.1.1, g++ 15.3.0 and 16.2.1 (C++) compiling the same generated arithmetic translation unit |
| **Claimed result** | README table (Ryzen AI 7 350, 2026-09): D (dmd 2.113.0) Total=Build+Run 13 us/f untemplated (19 templated), Compile 10.3 us/f (17.9 templated), Check 4.5 us/f, against C (clang 23.1.1) Total 118 us/f and Compile 77.9, C++ (clang++ 23.1.1) Total 236 (107 templated) and Compile 82.4 (128.7), C++ (g++-15 15.3.0) Total 303 (600) and Compile 269.6 (665.0), C (gcc-15 15.3.0) Total 392 and Compile 193.8, C (gcc 16.2.1) Total 454, C++ (g++ 16.2.1) Total 486. About 9x faster than clang C and 23x faster than g++-15 on Total, and about 7.6x (clang C) to 26x (g++-15) on the link-free Compile column (derived from page data). The README's '6x-38x' headline is dmd against the other D compilers (ldmd2 1.43.0 Total 95 us/f, gdc 16.2.1 Total 527 us/f), not against C. The C compiler tcc 0.9.28rc is faster than dmd (Total 4 us/f, Compile 2.0 us/f). |
| **Workload** | nordlow/compiler-benchmark: compile (and run) a single massive synthetic translation unit of arithmetic call chains, reported as microseconds per generated function for check, compile and Total=Build+Run, untemplated and templated variants. |
| **Metric** | compile-time |
| **Hardware** | AMD Ryzen AI 7 350 (8+8 cores) at 5.09 GHz, Arch Linux, sample run as of 2026-09 |
| **Compiler and flags** | From cbench: C/C++ via gcc, g++, clang, clang++ with -Wall -Wextra (C) or -Wno-c++11-extensions (C++) and no -O flag (default -O0); check uses -fsyntax-only, compile uses -c, build links with the compiler's default system linker. dmd and ldmd2 use -betterC; check -o-, compile -c, build adds -Xcc=-fuse-ld=lld (or gold) when available; gdc gets no extra flags. Versions: dmd 2.113.0-95551bb, ldmd2 1.43.0, gdc 16.2.1, clang/clang++ 23.1.1, gcc/g++ 15.3.0 and 16.2.1. Minimum of --run-count=10 repetitions (capped to 3 or 2 for slow steps), workers pinned to cores in a multiprocessing pool. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README: dmd's custom backend and front end do little optimization work; comparing dmd with LLVM-based ldmd2 and GCC-based gdc on the same D source isolates backend cost (dmd about 6x faster than ldmd2 and about 38x faster than gdc). |
| **Adoption** | 3.3k stars (dlang/dmd); benchmark repo nordlow/compiler-benchmark 167 stars, 17 forks, MIT |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/dlang/dmd) · [benchmark](https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md) |

## Verdict

One run of nordlow/compiler-benchmark (AMD Ryzen AI 7 350, Arch Linux, tables dated 2026-09) generated 40,000 arithmetic call-chain functions per language in one file. dmd 2.113.0 (-betterC, no -O) compiled the D version to an object in 10.3 us per function and built and ran it in 13. For the same C and C++ at default -O0, clang 23.1.1 took 77.9 us/f (Total 118), clang++ 82.4 (236), gcc 15.3.0 193.8 (392), g++ 15.3.0 269.6 (303), gcc 16.2.1 400.1 (454) and g++ 16.2.1 372.3 (486). The link-free ratios run from 7.6x to 39x, derived from page data.

## Use it when

- Edit-compile-run and debug-build loops for D code, where cold build latency matters more than how fast the generated code runs.
- Large machine-generated D modules made of many small non-template functions, the shape this benchmark measures (200 chains x 200 depth in one file).
- Clean rebuilds in CI or batch scripts with no resident compiler daemon. The README argues dmd's cold-compile speed matters most here.
- Projects already in D, with dmd for development builds and LDC or GDC for release builds from the same front end.

## Skip it when

- Optimized release builds: the benchmark ran dmd without -O and gcc/clang at default -O0, so it says nothing about -O2/-O3 build time or about how fast dmd's code runs compared with LDC or GDC.
- Speeding up an existing C or C++ build: this is a cross-language comparison. For C, tcc compiled the same generated program faster than dmd did (Compile 2.0 vs 10.3 us/f, Total 4 vs 13), with cuik (76) and cproc (86) close behind.
- Real projects dominated by imports, Phobos, templates or CTFE: the generated file has no imports and no standard library. Its templated variant already costs 1.7x more (Compile 17.9 vs 10.3 us/f), and the README says real builds are driven by headers, modules and stdlib footprint.
- Non-x86 targets: the run was x86-64 Linux. The backend tree has x86/ and arm/ directories, but the README documents no platform list and the ARM backend's maturity was not checked. LDC and GDC are the usual cross-platform D compilers.
- Quoting precise ratios: one run on one laptop CPU, with self-contradictory cells in the C/C++ rows.

## How it is fast

The gap is in code generation, not parsing. On the same D source, the check-only step (-o-) costs 4.5 us/f with dmd, 5.8 with ldmd2 (LLVM backend) and 15.9 with gdc (GCC backend). The compile step costs 10.3, 73.7 and 497.1 us/f. dmd's backend does little optimization work at its default settings and goes straight to object code. Its front end is also cheap here: 4.5 us/f to type-check the D file against 11.9 to 13.5 for gcc and clang -fsyntax-only on the C file. The benchmark ran dmd with -betterC, which drops druntime, and linked through cc with lld.

## Compared with alternatives

Of the compile-throughput siblings measured in the same table, only dmd is clearly faster than clang. Its Total is 13 us/f, against Zig 110, Odin 147, C3 153 and rustc 187, which beat only the GCC rows. Pick dmd when the shortest cold build of a statically typed systems language is the goal. Zig's resident incremental build mode was not measured and may change that answer for inner-loop work. If you are staying in C, tcc (4 us/f) beats them all.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (command-line compiler; build from source with `dub build dmd:compiler` per the README, or use a release binary) |
| **Dependencies** | a system C toolchain for linking (dmd links through cc; the benchmark passed -Xcc=-fuse-ld=lld); a D compiler plus dub to build dmd itself |
| **Minimum toolchain** | dmd 2.113.0-95551bb as measured (a commit-tagged build) |
| **Platforms** | x86-64 code generation as measured on Arch Linux; the backend tree also has an arm/ directory, not documented in the README |
| **Thread safety** | not applicable (command-line compiler) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: compiler tasks run at the same time in a multiprocessing pool, one worker pinned per logical CPU. The homogeneous path uses all logical CPUs minus two, and the frequency-based hybrid path in cpu_topology.py does not drop SMT sibling threads. The Ryzen AI 7 350 mixes 4 Zen 5 cores (up to 5.0 GHz) with 4 Zen 5c cores (up to 3.5 GHz, per AMD's spec in a search snippet), and the core each row ran on is not recorded. Rows may have shared a physical core or run at different clocks. The repetition count also differs: builds over 3 s keep the minimum of 2 runs (every gcc, g++, clang and clang++ build row, about 4.3 to 24 s at 40,000 functions), while dmd's 0.5 s build keeps the minimum of 10. Self-contradictory cells fit this: gcc-15's C Total (392) is twice its own Compile (193.8) while g++-15 on near-identical C++ adds 12%, and clang++'s templated Total (107) is below its Compile (128.7).
- D's configuration is lighter than typical D: -betterC means no druntime, Phobos or ModuleInfo to build or link, and only the D rows get -Xcc=-fuse-ld=lld (gcc, clang and gdc use the default system linker). Both favour D in the Total=Build+Run column. Use the link-free Compile column: 7.6x faster than clang C, 8.0x than clang++, 18.8x than gcc-15, 26x than g++-15 and 36-39x than gcc/g++ 16.2.1 (derived from page data).
- The README's '6x-38x' headline (rewritten 2026-10-12) compares dmd with the other D compilers (ldmd2, gdc), not with C. Its prose figures (dmd 11.5, ldmd2 70.3, gdc 433.2, clang 87 us/f) come from a different run than its tables.
- Nothing checks the output: the harness times the compiler and the binary's run but ignores the run's exit code and result, and every compiler built unoptimized code.

## Known shortcomings

- Not a language-level win: tcc (C) beats dmd (4 vs 13 us per function); gcc and clang build at default -O0 while dmd runs with -betterC and links with lld against the default linker for gcc/clang (flags in cbench, to which 'benchmark' is a symlink); some cells noisy and the README prose comes from a different run than its tables.
- Harness flaw: the compilers run at the same time in a multiprocessing pool with no SMT filter on the homogeneous or frequency paths, on a Ryzen AI 7 350 that mixes 4 Zen 5 (5.0 GHz) and 4 Zen 5c (3.5 GHz) cores; builds over 3 s keep the minimum of 2 runs (every gcc and clang build row, 4.3-24 s) while dmd keeps the minimum of 10, which explains the self-contradictory cells (gcc-15 C Total 392 is twice its own Compile; clang++ templated Total 107 is below its Compile 128.7). D-only -betterC plus lld. The link-free Compile column is still 7.6x (clang) to 39x (gcc 16.2.1); the ratios are noisy but the direction holds.

## Caveats and trade-offs

Compile-time claim, not run-time: both sides build unoptimized code (gcc/clang default -O0, dmd without -O), so the -O3 rule for run-time baselines does not apply. Not a language-level win: the C compiler tcc compiles the same generated program faster than dmd (Total 4 vs 13 us/f) and cuik and cproc are close (76 and 86 us/f), so the gap is dmd's implementation against GCC and Clang, as the dmd vs ldmd2 vs gdc rows show. Harness asymmetries: D builds link with lld via -Xcc=-fuse-ld=lld while gcc and clang use the default system linker, and D uses -betterC (no druntime), which favours D in the Total=Build+Run column; the link-free Compile column still shows 7.6x to 26x. C adds -Wall -Wextra. Synthetic arithmetic call chains in one translation unit, no headers, standard library or modules; the README says real builds differ. Noisy cells: clang++ templated Total 107 is below its own Compile 128.7, and clang++ untemplated Total 236 is nearly 3x its Compile 82.4; the README prose (dmd 11.5, ldmd2 70.3, gdc 433.2, clang 87 us/f) comes from a different run than the tables. Single machine, single sample run by a D community developer (nordlow). [retier] The compilers run concurrently in a multiprocessing pool with no SMT filter on a Ryzen AI 7 350 that mixes 4 Zen 5 and 4 Zen 5c cores; builds over 3 s keep the minimum of 2 runs while dmd keeps the minimum of 10, which explains self-contradictory cells (gcc-15 C Total 392 is twice its own Compile; clang++ templated Total 107 is below its Compile 128.7). The link-free Compile column is still 7.6x (clang) to 39x (gcc 16.2.1).

dmd generates less optimized code than LDC or GCC; this claim is about build time, not run time. In the README's table Zig (110 us/f) is on par with clang C (118) and Odin (147), C3 (153) and Rust (187) are slower than dmd but not faster than clang, so only dmd is a clear compile-time win.

## Maintenance

dmd is actively maintained (commits on master through 2026-10-12, 3.3k stars, BSL-1.0); the evidence is a single-machine run by a D community developer using a public MIT harness whose README changed daily from 2026-10-09 to 2026-10-12, so re-run it before quoting ratios.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Public harness (cbench in nordlow/compiler-benchmark; ./benchmark is a symlink to it) with every compiler command line in code (gcc/clang/g++/clang++ get only -Wall -Wextra plus -fsyntax-only, -c or -o, i.e. default -O0; dmd gets -betterC and, for build, -Xcc=-fuse-ld=lld when ld.lld is present), compiler versions in the README table and the CPU named (AMD Ryzen AI 7 350 at 5.09 GHz, Arch Linux, 2026-09 run), so it meets A; upgraded from B because the flags the record could not read are in the public script.
- **Verifier notes:** Numbers match the README table exactly; flags read from the cbench script (the 'benchmark' file is a 6-byte symlink to cbench, which is why the search agent got a 6-byte body). Record as a toolchain compile-speed entry rather than a D-beats-C language claim: tcc (C) is faster than dmd on the same benchmark, and the D build uses lld while C/C++ builds use the default linker. The orchestrator may want a compile-time or toolchain category instead of systems-and-safety.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-66 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/benchmark>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cbench>
  - <https://github.com/nordlow/compiler-benchmark>
  - <https://github.com/nordlow/compiler-benchmark/commits>
  - <https://github.com/dlang/dmd>
  - <https://github.com/dlang/dmd/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cpu_topology.py>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/process_timer.py>
  - <https://github.com/nordlow/compiler-benchmark/commits>
  - <https://github.com/dlang/dmd>
  - <https://github.com/dlang/dmd/commits/master>
  - <https://github.com/dlang/dmd/tree/master/compiler/src/dmd/backend>
  - WebSearch snippet only: https://www.amd.com/en/products/processors/laptop/ryzen/ai-300-series/amd-ryzen-ai-7-350.html (4x Zen 5 up to 5 GHz, 4x Zen 5c up to 3.5 GHz)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:d/nordlow/compiler-benchmark#compile-throughput`) · [data/wave14/enrich/raw/lang_d_nordlow_compiler_benchmark_compile_throughput.json](../../../data/wave14/enrich/raw/lang_d_nordlow_compiler_benchmark_compile_throughput.json) (enrichment confidence 0.6)

</details>
