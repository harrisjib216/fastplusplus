# Cuik (C compiler with the TB backend)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> MIT C11/C23 compiler and sea-of-nodes backend library (TB); about 2x clang -O0 and 12x gcc -O0 compile speed on a synthetic benchmark.

| | |
|---|---|
| **Beats** | clang 22.1.8 (LLVM) and gcc 16.2.1 / gcc-15 15.3.0, compile and build time at their default optimisation level |
| **Claimed result** | README sample run (us per generated function, lower is better), Cuik versus clang 22.1.8 versus gcc 16.2.1: check 6.0 / 15.4 / 18.2, compile 60.6 / 123.3 / 732.5, build 57.6 / 60.3 / 500.7. That is Cuik about 2.0x faster than clang and about 12x faster than gcc at compile, about 2.6x and 3.0x at check, and about 1.05x and 8.7x at build (all derived from page data). tcc 0.9.28rc is faster again (check 2.9, compile 3.5, build 2.6) and cproc is slower (check 10.6, compile 114.8). README conclusion: 'TCC is by a large margin the fastest compiler in build speed, followed by the C compiler Cuik and D's dmd.' |
| **Workload** | nordlow/compiler-benchmark generates a synthetic C program (a grid of nested function call chains, 'return expr' bodies, long type) and measures minimum time per generated function over 5 runs for the check (syntax-only), compile (-c) and build (link to an executable) operations; Cuik is capped at 100 x 100 functions, the other C compilers run 200 x 200. |
| **Metric** | compile-time |
| **Hardware** | AMD Ryzen AI 7 350 (8+8) @ 5.09 GHz, Arch Linux, sample run as of 2026-09 |
| **Compiler and flags** | Cuik \~master (no commit given) invoked with -c -xe (check), -c (compile) and plain -o exe (build); clang 22.1.8 and gcc 16.2.1 invoked with -fsyntax-only, -c and plain build with no -O flag (so their default O0 code generation) plus warning-silencing flags, from the benchmark script. |
| **Adoption** | 1.3k stars |
| **Last commit** | 2026-07-26 |
| **Links** | [repository](https://github.com/RealNeGate/Cuik) · [benchmark](https://github.com/nordlow/compiler-benchmark) |

## Verdict

In nordlow/compiler-benchmark's 2026-09 sample run on an AMD Ryzen AI 7 350 under Arch Linux, an unpinned Cuik master build took 6.0, 60.6 and 57.6 us per generated function for check, compile and build. clang 22.1.8 took 15.4, 123.3 and 60.3, and gcc 16.2.1 took 18.2, 732.5 and 500.7, all at default -O0 settings (gcc and clang also with -Wall -Wextra) on a synthetic C program of one-line call-chain functions, with Cuik at 10,000 functions and the others at 40,000. That is about 2x clang and 12x gcc on compile, about 2.6x and 3x on check, a tie with clang on build, and slower than TinyCC on every column.

## Use it when

- You are building a language or JIT and want an MIT-licensed C library backend with a sea-of-nodes IR, x64/AArch64 codegen, in-memory JIT placement and object export, without linking LLVM.
- Fast unoptimised (-O0-class) builds of small, self-contained C11/C23 programs on x86-64 Linux or Windows, where edit-compile latency matters more than code quality (about 2x clang -O0 and 12x gcc -O0 on compile in the nordlow benchmark).
- C tooling that needs the front end as a library: stop after preprocessing, parsing or type checking and walk the result (the driver also has -bindgen, -objdump and -link modes).
- Studying or extending a compact sea-of-nodes compiler (GCM, GVN, SCCP, SROA, Rogers and Briggs allocators are all in tb/).

## Skip it when

- Production code: the README says 'unfinished and buggy' and cuik_c/README.txt says 'NOT PRODUCTION-READY'. Open issues include a Linux call miscompile (#37), a segfault with struct varargs (#60), glibc &lt;stdio.h&gt; parse failures (#58), an infinite loop on attributes in struct fields (#53) and a sema crash (#42).
- When you need optimised code: -O is opt-in, the optimizer is new (commit 'nbody.c running optimized!', Aug 2025) and there are no published code-quality numbers against clang or gcc at -O2.
- When compile speed is the only goal: in the same table TinyCC (already catalogued) was faster on every column (check 2.9, compile 3.5, build 2.6 us/f against Cuik's 6.0, 60.6 and 57.6).
- Large translation units or tight memory: the benchmark capped Cuik at 100 x 100 functions 'due to compiler stability limits', and its build peak RSS was 69.9 kB per function (about 0.7 GB for 10,000 functions, derived from page data) against clang's 8.8.
- Existing GCC/Clang build scripts, musl (#36) or macOS (#29): the driver exits with an error on unknown flags such as -Wall or -std=c11, and on Linux the GNU toolchain hard-codes /usr/include/x86_64-linux-gnu include paths and needs clang on PATH to link.

## How it is fast

The front end is a unity build with a generated DFA lexer (meta/lexgen.lua writes cuik_pp/dfa.h), arena allocation and mimalloc, and it lowers the typed AST straight into TB's graph builder. Without -O, TB skips the optimizer and per function runs Click-style global code motion (GCM) scheduling, a Rogers-style global register allocator (Briggs-Chaitin graph colouring is the alternative) and direct machine-code and object emission, with no separate assembler pass. Built with -j N, libCuik compiles translation units and functions on a thread pool; the default is single-threaded.

## Compared with alternatives

Choose Cuik/TB over TPDE when you have C source rather than LLVM IR and want no LLVM dependency, and over dstogov/ir or the copy-and-patch compilers (PochiVM, WasmNow) when you want a complete C front end together with a sea-of-nodes backend and object/JIT output in one MIT library. Choose TPDE (10-20x faster than LLVM -O0 with LLVM compatibility) or dstogov/ir (proven inside PHP's JIT) when you need a mature, tested backend. TinyCC (catalogued elsewhere) remains the faster plain C compiler.

## Integration

| | |
|---|---|
| **Form** | CLI executable, plus static or shared libraries (libCuik front end, libtb backend) built from source |
| **Dependencies** | mimalloc (git submodule); build needs Lua or LuaJIT, Ninja and Clang (default) or GCC (-gcc); on Linux, linking an executable runs the system clang |
| **Minimum toolchain** | Clang or GCC with C11 &lt;threads.h&gt; (or build with -no_threads); the release build uses -O2 -DNDEBUG and appends -march=haswell on detected hosts |
| **Platforms** | Hosts: Windows (MSVC toolchain), Linux x86-64 glibc (GNU toolchain), macOS (darwin toolchain, build issue #29 open); musl build fails (#36). Targets: x64, AArch64, MIPS32/64, wasm32 |
| **Thread safety** | libCuik is designed to compile several translation units on separate threads (CUIK_ALLOW_THREADS, -j N; default single-threaded); in TB, tb_module_create_section is documented 'not thread-safe' and code arenas must be one per thread |
| **Drop-in for the baseline** | partial: accepts -c, -o, -D, -I, -O, -g and -S, but uses -xe instead of -fsyntax-only, rejects unknown GCC flags (-Wall, -std=...), supports C11/C23 only and on Linux links through clang |

## Gotchas

- On Linux the GNU toolchain links by calling system("clang ... -lc -lm -fPIE -o &lt;out&gt; &lt;obj&gt;"), and driver.c ignores cuiklink_invoke's return value. A failed link prints 'Linker exited with code N' but cuik still exits 0, so build systems do not notice. Every Cuik 'Build' number on Linux also includes a clang link.
- -g always emits CodeView debug info (the driver hard-codes TB_DEBUGFMT_CODEVIEW, with a TODO), so gdb and lldb on Linux get no DWARF. The default build.lua appends -march=haswell whenever uname -m maps to a known arch, aarch64 included, so a default x86-64 build needs an AVX2-class CPU. The aarch64 host build looks broken (read from build.lua, not tested).
- Issue #37, open since Feb 2024 with no reply: on Linux x86-64, a printf call with 8 arguments prints garbage for the arguments after the fifth (works on Windows). The benchmark's one-argument functions never hit it, and the harness never checks the built binary's exit code or output, so a miscompile would go unnoticed.
- Harness flaws behind the numbers: Cuik ran a 4x smaller program (10,000 vs 40,000 functions) with per-function normalisation, so the Run column (mostly process start-up) cannot be compared across compilers. Cuik's Build (compile plus clang link) timed below its Compile (57.6 vs 60.6 us/f), which shows contention noise of at least 5% on the parallel, CPU-pinned harness. The 100 Hz psutil poll loop adds up to 10 ms per run, up to about 17% of Cuik's 60 ms check run (derived from page data). The Cuik binary is an unpinned '\~master' build. Treat the 2x compile ratio against clang as approximate and the build result as a tie.

## Known shortcomings

- nordlow/compiler-benchmark numbers (Cuik at an unpinned master) come from one parallel sample run where Compile exceeds Build for every C compiler (contention noise); the build win over clang is 1.05x, a tie; the README conclusion contradicts its own table (dmd 11.2x and LuaJIT 4.8x build faster); -xe is type checking only and Cuik's optimiser is off by default. An AOT C compiler, loose fit under jits.
- Enricher (nordlow/compiler-benchmark): Cuik ran 10,000 functions while the other compilers ran 40,000, so the per-function Run column is not comparable; Cuik's Build (57.6 us/function) is below its Compile (60.6) although Build includes the clang link, so contention noise is at least 5%; the 100 Hz psutil poll adds up to 10 ms per run, up to about 17% of Cuik's 60 ms check (derived); the harness never checks the built binary's exit code or output; run count defaults to 10 in code while the README says 5. Linux linking shells out to clang via system() and driver.c ignores the link result so a failed link still exits 0; -g emits CodeView only; the driver errors on -Wall and -std=c11; build.lua adds -march=haswell even on aarch64 hosts; open #37 (Linux calls with more than 5 arguments print garbage) is missed by the benchmark's one-argument functions.

## Caveats and trade-offs

Independent third-party suite, but the gap to tier A is the Cuik build: the script hard-codes its version as '\~master' (no commit, no build compiler or flags), and results are from one sample run on one machine (best of 5 per cell). The comparison is at default settings for all three (gcc and clang with no -O flag plus -Wall -Wextra, which they pay for and Cuik does not; Cuik's optimizer is off unless -O is passed, and its check mode -xe is 'type check only', comparable to -fsyntax-only), on one synthetic program shape (long chains of one-line 'return x + ...' functions), so it measures front end plus unoptimised codegen speed only; the 'Run' column (105 us/f for Cuik versus 155 clang and 98 gcc) is of unoptimised output on a synthetic program and says nothing about optimised code quality, which the lead named as a baseline and for which no numbers were found. Timing noise is visible: the suite runs tasks in parallel, one worker pinned per logical CPU (SMT siblings share cores), and the Compile column is larger than the Build column (compile plus link) for every C compiler (Cuik 60.6 vs 57.6, clang 123.3 vs 60.3, gcc 732.5 vs 500.7), so the 1.05x Build win over clang is a tie within noise and the 2x Compile win over clang may be inflated by contention. Numbers are normalised per function while Cuik is capped at 100 x 100 (10,000 functions, 'due to compiler stability limits') against 200 x 200 for the other C compilers, so fixed start-up cost weighs more on Cuik, which if anything understates its speed. The README conclusion ranks Cuik second in build speed after tcc, but its own table shows D's dmd (11.2 us/f) and LuaJIT (4.8) building faster than Cuik (57.6). Cuik's own README says 'unfinished and buggy' and carries no benchmark; a search-result snippet saying its preprocessor is about 2x faster than Clang's was not verified. LLVM as a library (TB versus LLVM backend) is not measured here. Category fit is loose: Cuik is an ahead-of-time C compiler toolchain measured on compile time, filed under jits. [retier] nordlow/compiler-benchmark (Cuik at an unpinned master, one parallel sample run, clang and gcc at default flags): Cuik ran 10,000 generated functions against 40,000 for the others, so the per-function Run column is not comparable; Build time is below Compile time, so at least 5% contention noise; no output or exit-code check; the build win over clang is 1.05x, a tie, and dmd (11.2x) and LuaJIT (4.8x) build faster. -xe is type checking only and the optimiser is off by default. An AOT C compiler with the TB backend, loose fit under jits; open #37 miscompiles calls with more than 5 arguments on Linux.

Cuik's own README: 'warning: unfinished and buggy'. Fast, thread-safe C11 front end (libCuik) plus the Tilde Backend (tb) with a sea-of-nodes IR, x64 and AArch64 codegen, ELF, COFF, PE and Mach-O output, and JIT or AOT use; MIT licensed. In the benchmark Cuik's build peak memory is far higher per function (69.9 kB/f versus clang 8.8 and gcc 17.5) and the benchmark had to cap Cuik at 100 x 100 for 'compiler stability limits'. No optimising pipeline comparable to LLVM, so it competes on compile speed rather than code quality.

## Maintenance

Active (last commit 2026-07-26; history restarted 2025-03-23 with 'Fresh start on the commit history', 32 commits since, 11 open issues) and MIT-licensed, but self-described as unfinished, buggy and not production-ready. It is usable for experiments or as an embeddable backend, not as a production C compiler. The benchmark numbers come from an unpinned build on a noisy parallel harness that compares different program sizes and never validates the built binaries.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (nordlow/compiler-benchmark, MIT, 166 stars, public script 'benchmark' with bm_C_using_cuik and gcc_clang_op_flags) shows Cuik ahead of clang 22.1.8 and gcc 16.2.1 on check and compile, with the CPU (AMD Ryzen AI 7 350) stated; it falls short of A because the Cuik binary is only labelled '\~master' (hard-coded version string, no commit, unknown build compiler and flags). The -O0 cap was considered and does not apply: the metric is compile time, the baseline compilers are release builds, and Cuik's optimizer is also off by default (-O enables it), so both sides run unoptimised codegen.
- **Verifier notes:** All table numbers (check 6.0/15.4/18.2, compile 60.6/123.3/732.5, build 57.6/60.3/500.7, tcc and cproc rows, Ryzen AI 7 350, Arch Linux, 2026-09) and the derived ratios match the nordlow/compiler-benchmark README; Cuik MIT, 1.3k stars, last commit 2026-07-26 confirmed. Shortcomings: Cuik built from an unpinned '\~master', one parallel sample run with visible contention noise (Compile slower than Build for every C compiler), build-speed win over clang is a tie, unoptimised synthetic code only, no optimised code-quality numbers; consider a category override since it is an AOT C compiler rather than a JIT.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** pinned-commit repeated run; equal function counts with output checks
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/benchmark>
  - <https://github.com/nordlow/compiler-benchmark>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/HEAD/README.md>
  - <https://github.com/RealNeGate/Cuik>
  - <https://github.com/RealNeGate/Cuik/commits/master>
  - <https://github.com/RealNeGate/Cuik/tree/master>
  - <https://github.com/RealNeGate/Cuik/tree/master/main>
  - <https://github.com/RealNeGate/Cuik/tree/master/cuik_c>
  - <https://github.com/RealNeGate/Cuik/tree/master/cuik_c/driver>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/main/main_driver.c>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/main/README.md>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/cuik_c/driver/driver_arg_parse.h>
- **Sources the enricher read:**
  - <https://github.com/RealNeGate/Cuik>
  - <https://github.com/RealNeGate/Cuik/commits/master>
  - <https://github.com/RealNeGate/Cuik/issues>
  - <https://github.com/RealNeGate/Cuik/issues/37>
  - <https://github.com/RealNeGate/Cuik/issues/57>
  - <https://github.com/RealNeGate/Cuik/issues/58>
  - <https://github.com/RealNeGate/Cuik/tree/master/cuik_c>
  - <https://github.com/RealNeGate/Cuik/tree/master/cuik_c/driver>
  - <https://github.com/RealNeGate/Cuik/tree/master/tb>
  - <https://github.com/RealNeGate/Cuik/tree/master/tb/opt>
  - <https://github.com/RealNeGate/Cuik/tree/master/tb/objects>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/HEAD/README.md>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/HEAD/main/README.md>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/HEAD/docs/BUILDING.txt>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/HEAD/docs/STRUCTURE.txt>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/cuik_c/README.txt>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/cuik_c/driver/driver.c>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/cuik_c/driver/driver_arg_parse.h>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/cuik_c/linker.c>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/cuik_c/toolchains/gnu.c>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/main/main_driver.c>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/build.lua>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/include/tb.h>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/tb/jit.c>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/tb/opt/gcm.h>
  - <https://raw.githubusercontent.com/RealNeGate/Cuik/master/tb/NOTES.txt>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/benchmark>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/process_timer.py>
  - <https://github.com/c3lang/tilde-backend>
  - https://handmadecities.com/media/seattle-2023/tb/ (EGRESS_BLOCKED; search snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/realnegate/cuik`) · [data/wave12/enrich/raw/github_com_realnegate_cuik.json](../../../data/wave12/enrich/raw/github_com_realnegate_cuik.json) (enrichment confidence 0.8)

</details>
