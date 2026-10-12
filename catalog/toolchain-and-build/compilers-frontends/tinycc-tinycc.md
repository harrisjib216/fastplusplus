# TinyCC (tcc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Toolchain and build](../README.md) › [Compilers and front ends](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `LGPL-2.1` · 🟢 active

> Tiny self-hosting C compiler/JIT that compiles about 9x faster than gcc -O0, trading away optimization.

| | |
|---|---|
| **Beats** | GCC at -O0 (gcc 16.2.1 in compiler-benchmark, GCC 3.2 in the bellard.org table); also Clang 22.1.8 at -O0 |
| **Claimed result** | nordlow/compiler-benchmark (README table of 2026-09-29, commit 5712a50; per-function minimum of 5 runs over 40,000 generated functions): Build [us/f] tcc 0.9.28rc 2.6 vs gcc 16.2.1 500.7 vs clang 22.1.8 60.3, about 193x faster than gcc -O0 and 23x faster than clang -O0 (derived from page data); Compile [us/f] tcc 3.5 vs gcc 732.5 vs clang 123.3, about 209x and 35x (derived from page data); Check [us/f] tcc 2.9 vs gcc 18.2 vs clang 15.4, about 6.3x and 5.3x (derived from page data), although tcc's Check row does full code generation into /dev/null while gcc and clang only run -fsyntax-only. The previous published run (the table that commit 5712a50 replaced) had Build tcc 3.6 vs gcc 805.8 vs clang 85.3 us/f, about 224x and 24x (derived from page data). First-party bellard.org figure: TinyCC 0.9.22 compiles, assembles and links the Links browser in 2.27 s (859,000 lines/s, 29.6 MB/s) vs GCC 3.2 -O0 in 20.0 s (98,000 lines/s, 3.4 MB/s) on a 2.4 GHz Pentium 4, 'about 9 times faster than GCC' (8.8x, derived from page data). The TinyCC README says 'Compiles and links about 10 times faster than gcc -O0'. |
| **Workload** | compiler-benchmark default run (--function-count=200 --function-depth=200 --run-count=5). Each repetition writes one generated C file: 40,000 one-line 'long f(long x) { return x + ... + const; }' functions in 200 call chains of depth 200, plus a main that calls the 200 chain heads and returns the sum. There is no #include or other prefix. Times are wall clock (time.perf_counter around subprocess.Popen, with psutil polling every 10 ms at the default --sample-rate=100). Each cell is the minimum of 5 repetitions divided by 40,000 (us per function). Absolute minimums: Build tcc about 0.10 s, clang 2.4 s, gcc 20.0 s; Compile tcc 0.14 s, clang 4.9 s, gcc 29.3 s (derived from page data). bellard.org: the Links browser source, 76,936 lines including headers, of which 1,950,947 lines (67.2 MB) are actually compiled; real time covers compile, assemble and link. |
| **Metric** | compile-time |
| **Hardware** | compiler-benchmark: AMD Ryzen AI 7 350, which the README labels '(8+8) @ 5.09 GHz'. It is a 28 W Krackan Point laptop part with 4 Zen 5 cores (up to 5.0 GHz) and 4 Zen 5c cores (up to 3.5 GHz), 16 threads. Arch Linux; the README says 'as of 2026-09' and the table was committed on 2026-09-29 (5712a50). bellard.org: 2.4 GHz Pentium 4 (TinyCC 0.9.22 was tagged 2004-11-08; GCC 3.2 dates from 2002). |
| **Compiler and flags** | compiler-benchmark script at commit 5712a50, with the same flags at HEAD: gcc 16.2.1 gets -Wall -Wextra; clang 22.1.8 gets -Wall -Wextra -fno-color-diagnostics -fno-caret-diagnostics -fno-diagnostics-show-option. Both then get -fsyntax-only (Check), -c (Compile) or -o main (Build), with no -O flag, so they run at default -O0. tcc 0.9.28rc is a mob-branch snapshot installed as the Arch package by provision.sh; its exact commit is not recorded. It gets -c -o /dev/null (Check), -c (Compile) or -o main (Build), with no warning or optimization flags. All three link in Build (gcc and clang through the system linker, tcc with its built-in linker); none links in Compile. bellard.org: TinyCC 0.9.22 vs GCC 3.2 -O0; no script or flags are published beyond that. |
| **Adoption** | About 3.0k stars and 570 forks on the GitHub mirror (github.com showed 3,000 on 2026-10-07; 3038 at the 2026-09-24 check). The mirror describes itself as an 'Unofficial mirror of mob development branch' of repo.or.cz/tinycc.git. The V language bundles TCC binaries for fast development builds. |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/TinyCC/tinycc) · [benchmark](https://github.com/nordlow/compiler-benchmark) |

## Verdict

On Fabrice Bellard's own tcc benchmark page, compiling the Links web browser (76,936 source lines, but 1,950,947 lines / 67.2MB actually compiled due to repeated header inclusion) on a 2.4GHz Pentium 4: TinyCC 0.9.22 finished in 2.27s (859,000 lines/s, 29.6MB/s) versus GCC 3.2 at -O0 in 20.0s (98,000 lines/s, 3.4MB/s), about a 9x wall-clock advantage. Both compilers ran with no comparable optimization flags enabled (tcc has none), and the hardware/compiler versions are roughly 2003-2005 era.

## Use it when

- Tight edit-compile-run development loops where compiler latency, not runtime speed, dominates iteration time
- Ad hoc 'C scripting' -- running a .c file directly via a #!tcc -run shebang instead of compiling a real binary
- Embedding a C compiler/JIT inside another program (via libtcc) for runtime code generation, e.g. compiling small C snippets to native code and calling them in-process
- Bootstrapping or rescue environments where binary size matters (GNU Mes uses tcc to bootstrap a build from source)
- Local/CI dev builds of large C codebases where a project bundles tcc for fast iteration and uses a real compiler for release builds (this is how the V language uses it)

## Skip it when

- Producing optimized release binaries -- there is no optimization pass comparable to gcc -O1/-O2/-O3, so generated code is measurably slower
- Code relying on full C11 or the broader GNU C extension surface -- tcc covers 'many' C11 features and GNU extensions, not all of them (not documented as 100% coverage)
- C++ code -- tcc is a C compiler only
- Toolchains that depend on gcc/clang-specific features such as LTO, sanitizers, or vendor-specific builtins not implemented by tcc
- Programs combining the -b bounds checker with signal handlers or fork() in a multi-threaded process -- the docs call this out as a known incompatibility because the bounds-checking code uses locks

## How it is fast

It skips almost everything gcc's pipeline does beyond translation: no real optimizer (tcc has no flag comparable to -O1/-O2/-O3), a single fast pass from source straight to machine code, and its own integrated preprocessor/assembler/linker avoid forking out to separate cc1/as/ld processes. It also natively supports 6 target architectures (i386, x86-64, ARM, AArch64, RISC-V64, plus legacy TMS320C67xx) with a simple, non-SSA-optimizing code generator per target. The cost of skipping optimization is codegen roughly at gcc -O0/-O1 quality.

## Compared with alternatives

Pick tcc over zapcc or MIR/c2m when you want a mature, widely-deployed, general-purpose C compiler and embeddable JIT rather than a narrower research/prototype tool: zapcc is an abandoned Clang fork focused on incremental C++ template caching, and MIR/c2m is a newer, more experimental C-to-MIR JIT (bigger claimed speedup, less production track record). Neither zapcc nor cg_clif target C the way tcc does (zapcc is C++-only via Clang, cg_clif is a Rust backend), so for straight C dev-loop speed or in-process C JITing, tcc is the direct fit.

## Integration

| | |
|---|---|
| **Form** | source-drop / standalone compiler binary (CLI, gcc-like flags); optional static and shared libtcc library for embedding as an in-memory JIT |
| **Dependencies** | none required to build (self-hosting: ./configure && make, or make test); optional -lpthread when using the -pthread flag |
| **Minimum toolchain** | Any ANSI C (C89) host compiler to bootstrap from source, or tcc itself; as a language target it implements ISO C99, many ISO C11 features, and GNU C extensions (inline asm, _Thread_local, __attribute__((cleanup)), _Static_assert, asm goto, stdatomic) |
| **Platforms** | x86 (i386), x86-64, ARM, AArch64, RISC-V64, legacy TMS320C67xx; Linux/BSD (ELF), native macOS x86-64 (Mach-O), Windows (PE, see tcc-win32.txt), Android (position-independent executables) |
| **Thread safety** | Not a single shared global state: separate TCCState compilation contexts can be created and used concurrently from different threads (see tests/libtcc_test_mt.c in the repo). Per-state concurrent use from multiple threads simultaneously is not documented. |
| **Drop-in for the baseline** | partial -- tcc accepts many gcc-compatible command-line flags and is used as a gcc substitute in several build systems (V language dev builds, GNU Mes bootstrap), but incomplete C11/GNU-extension coverage, no LTO/sanitizers, and gcc -O0/-O1-level codegen mean it cannot replace gcc for anything needing full standards coverage or optimized output |

## Gotchas

- The -b bounds checker is incompatible with signal handlers (checking is disabled inside them) and interacts badly with fork() in multi-threaded programs, per tcc-doc.texi -- both stem from locking inside the bounds-checking runtime
- Bound-checked code (-b) is not included in shared libraries; the main executable must itself be built with -b for the checker to take effect
- Codegen quality sits around gcc -O0/-O1; don't compare tcc binaries' runtime speed to an optimized gcc/clang build
- -std=version only distinguishes c11/gnu11 (sets __STDC_VERSION__ to 201112) from everything else (199901); it isn't a fine-grained standards switch like gcc's

## Known shortcomings

- Re-found by the wave 2 seed backfill (w2-mine-c) with new independent evidence: nordlow/compiler-benchmark (AMD Ryzen AI 7 350, Arch Linux, 2026-09; public script, gcc 16.2.1 and clang 22.1.8 at default -O0 with -Wall -Wextra) gives per-function build 2.6 us for tcc 0.9.28rc vs 500.7 us gcc and 60.3 us clang (about 190x and 23x, derived from page data) on a synthetic 40,000-function translation unit with no headers; the benchmark's own README says real builds are header- and link-dominated, so the gap overstates typical gains. Name override keeps the verified record's identity; retier check pending.
- Retier check moved the record C to A on nordlow/compiler-benchmark (MIT, public script at commit 5712a50; tcc 0.9.28rc vs gcc 16.2.1 and clang 22.1.8 at -O0 with -Wall -Wextra; AMD Ryzen AI 7 350, Arch Linux, table committed 2026-09-29): Build 2.6 vs 500.7 vs 60.3 us per function (about 193x and 23x), Compile 3.5 / 732.5 / 123.3 (about 209x and 35x), Check 2.9 / 18.2 / 15.4 (derived from page data). Shortcomings: synthetic single translation unit of 40,000 functions with no #include (author's own warning that real builds are header- and link-dominated); noisy harness (Build below Compile for all three; clang Compile +48% and gcc Build -38% between runs; 14 concurrent pinned tasks on a mixed Zen 5 / Zen 5c part, performance-core pinning only added 2026-10-06); wall clock with 10 ms psutil polling, min of 5 runs per function, built binaries never validated; tcc mob commit not recorded; the gcc gap is about 20x tcc's own 10x claim. Last release 0.9.27 (2017-12-12); mob branch on an unofficial mirror; LGPL-2.1 with partial MIT relicensing.

## Caveats and trade-offs

The benchmark is synthetic (one huge TU of arithmetic call chains, no #include or header parsing); its own README says real-world build times are dominated by headers and linking, so the \~190x gap overstates typical gains (the project claims about 10x vs gcc -O0, and a 2003-era Links browser comparison of 2.27 s vs 20.0 s on GCC 3.2 appears only in search snippets because bellard.org was blocked). gcc and clang are compared at their default -O0, not at -O2, so the win is against unoptimized builds only. In this run the produced binaries' run time was 113 us/f for tcc vs 98 for gcc and 155 for clang, but run time is measured on the same synthetic code. The benchmark author is a third party (nordlow), but the suite is a single-maintainer repo with 166 stars; the tcc check row uses -c so it also emits object code unlike gcc -fsyntax-only. License: COPYING is LGPL-2.1; a RELICENSING file lists authors agreeing to MIT-style terms, but the whole tree is not relicensed. [retier] This supersedes the earlier note that a gcc -O0 baseline caps the entry at C. The tier now rests on a public third-party harness, with -O0 recorded as a caveat. The workload is synthetic: a single translation unit of arithmetic call chains with no #include. The benchmark README itself warns that real-world build times are 'heavily driven by header parsing (#include), package/module resolution, standard library footprint, and cross-crate/module parallelism, none of which are exercised by isolated arithmetic trees'. gcc and clang run at their default -O0 (plus -Wall -Wextra, which tcc does not get), so the lead holds only against unoptimized builds. The 193x Build gap over gcc is about 20x TinyCC's own 'about 10 times faster than gcc -O0' claim. It comes almost entirely from gcc's code generation on this one huge translation unit: gcc Check 18.2 vs Compile 732.5 us/f (derived from page data). The same Check-to-Compile jump does not appear in the bellard.org multi-file 8.8x. tcc's Check row emits code into /dev/null, while gcc and clang only run -fsyntax-only. The harness is noisy. In the 2026-09-29 table Build is lower than Compile for all three compilers (gcc 500.7 vs 732.5, clang 60.3 vs 123.3, tcc 2.6 vs 3.5 us/f), even though Build does strictly more work. Between the two published runs, clang Compile moved from 83.5 to 123.3 (+48%) and gcc Build from 805.8 to 500.7 (-38%) (derived from page data). At commit 5712a50 the script ran len(cpus)-2 tasks at once (14 on this 16-thread part), each pinned by worker index to one logical CPU, on a 28 W laptop chip that mixes 5.0 GHz Zen 5 and 3.5 GHz Zen 5c cores. Pinning to performance cores only arrived in a 2026-10-06 commit, after this run. The tcc-vs-clang Build ratio still stays at 23-24x across both runs. Polling every 10 ms adds up to about 10% to tcc's roughly 0.10 s builds but almost nothing to gcc's 20 s builds, so it understates tcc's lead. tcc's output is not validated. The harness checks only the compiler exit code and stderr, and it runs each built binary 5 times with output discarded, never checking its exit status or sum. Run time is reported only as speed: tcc 113 vs gcc -O0 98 vs clang -O0 155 us/f, with nothing at -O2. The exact tcc mob commit is not recorded; the table shows only 0.9.28rc. The script has changed since the run (work directory moved to /tmp, core selection, table layout), so reproducing the table needs the script at commit 5712a50. compiler-benchmark is a single-maintainer repo (nordlow, 166 stars, MIT). The bellard.org 8.8x figure is first-party, has no published script, and uses TinyCC 0.9.22 against GCC 3.2 -O0 on a Pentium 4. bellard.org was EGRESS_BLOCKED here, so the figure was re-confirmed from a search snippet and the 2026-09-24 verifier's reading. The GitHub repo is an unofficial mirror of the repo.or.cz mob branch. The last tagged release is release_0_9_27 (2017-12-12), and mob's VERSION reads 0.9.28rc, so the measured code is available only from mob, not from a release. COPYING is LGPL-2.1 and the README says TCC is distributed under the LGPL. A RELICENSING file lists authors who agree to MIT-style terms for their own contributions; it does not relicense the whole tree.

Single-pass compiler with no optimizer: generated code is unoptimized (similar to gcc -O0), so it suits compile-and-run scripting, bootstrapping and fast edit cycles but not performance-critical builds. Supports i386, x86_64, arm, aarch64, riscv64 and has an optional bounds checker. Does not support C++.

## Maintenance

Actively maintained: this GitHub mirror tracks the upstream repo.or.cz mob development branch and was pushed 2026-09-22; current in-tree version is 0.9.28rc. LGPL-2.1, small self-contained C source tree, easy to vendor -- matches its 'copyable' usability rating.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** bellard.org/tcc gives a first-party table: TinyCC 0.9.22 2.27s (859000 lines/s, 29.6 MB/s) vs GCC 3.2 -O0 20.0s (98000 lines/s, 3.4 MB/s) on a 2.4 GHz Pentium 4. No benchmark script is published, and the baseline is gcc -O0, so it is C.
- **Retiered** C to A: Raised from C (first-party bellard.org table only) to A on the third-party nordlow/compiler-benchmark run: the harness is public (MIT; the script that produced the 2026-09-29 table is in history at commit 5712a50, flags unchanged at HEAD), the flags are fixed in that script (gcc/clang: -Wall -Wextra plus -fsyntax-only, -c or -o main, no -O so default -O0; tcc: -c -o /dev/null, -c or -o main, no other flags), the compiler versions are printed in the table (tcc 0.9.28rc, gcc 16.2.1, clang 22.1.8), and the CPU, OS and date are stated (AMD Ryzen AI 7 350, Arch Linux, as of 2026-09). Checked: Build links for all three compilers and Compile links for none; each cell is the minimum wall-clock time of 5 repetitions (time.perf_counter around Popen with psutil polling every 10 ms) divided by 40,000 generated functions; there is no #include in the generated file; and only the compiler exit code and stderr are checked, never the built binary's result. The workload is synthetic and the harness is noisy (14 concurrent pinned tasks, Build below Compile in the published table), which is recorded in the caveats and does not lower the tier. The exact tcc mob commit is not recorded.
- **Verifier notes:** The record misread the page: 76,936 is the line count including headers, and 1,950,947 is the number of lines compiled. The speedup and timing numbers match the page. I removed the unsupported 'QEMU TCG lineage' usage claim: QEMU's docs say only that TCG 'began as a generic backend for a C compiler', not that it uses TinyCC. Metadata checked: LGPL-2.1, 3038 stars, last commit 2026-09-22.
- **Fields the verifier corrected:** `workload`, `stars_or_usage`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** backfill w2-mine-c; retier check (wave 2)
- **Pages the verifier opened:**
  - <https://bellard.org/tcc/>
  - <https://github.com/TinyCC/tinycc>
  - <https://github.com/vlang/v>
  - <https://github.com/qemu/qemu/blob/master/docs/devel/tcg-ops.rst>
- **Sources the enricher read:**
  - <https://github.com/TinyCC/tinycc>
  - <https://github.com/TinyCC/tinycc/blob/mob/README>
  - <https://github.com/TinyCC/tinycc/blob/mob/libtcc.h>
  - <https://github.com/TinyCC/tinycc/blob/mob/USES>
  - <https://github.com/TinyCC/tinycc/blob/mob/Changelog>
  - <https://github.com/TinyCC/tinycc/blob/mob/VERSION>
  - <https://github.com/TinyCC/tinycc/blob/mob/tcc-doc.texi>
  - https://github.com/TinyCC/tinycc/issues (search: miscompile, wrong code -- no matches)
  - <https://bellard.org/tcc/>
- **Raw records:** [data/wave2/verified.json](../../../data/wave2/verified.json) (id `https://github.com/tinycc/tinycc`) · [data/wave2/enrich/raw/github_com_tinycc_tinycc.json](../../../data/wave2/enrich/raw/github_com_tinycc_tinycc.json) (enrichment confidence 0.62)

</details>
