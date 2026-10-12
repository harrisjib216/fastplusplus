# C3 compiler (c3c) compile throughput vs gcc and g++ in nordlow/compiler-benchmark

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C3` · `MIT (compiler source under src is LGPL-3.0)` · 🟢 active

> C3's c3c compiler at -O0 builds a 40,000-function generated file 1.8-3.7x faster than GCC compiles the C equivalent, but slower than clang.

| | |
|---|---|
| **Beats** | C (gcc 15.3.0 and 16.2.1, clang 23.1.1) and C++ (g++ 15.3.0 and 16.2.1, clang++ 23.1.1) compiling the same generated arithmetic translation unit |
| **Claimed result** | README table (Ryzen AI 7 350), us per generated function. Total=Build+Run untemplated: C3 (c3c 0.8.5) 153 vs C gcc-15 392 (2.6x), C gcc 16.2.1 454 (3.0x), C++ g++-15 303 (2.0x), C++ g++ 16.2.1 486 (3.2x), C++ clang++ 23.1.1 236 (1.5x); C3 is 1.3x slower than C clang 23.1.1 (118). gcc-15's Total (392) is double its Compile (193.8), so the Compile column (1.8x over gcc-15, 3.7x over gcc 16.2.1) is the more reliable comparison. |
| **Workload** | nordlow/compiler-benchmark: compile (and run) one massive synthetic translation unit of arithmetic call chains, reported as microseconds per generated function ('Total=Build+Run [us/f]'), untemplated and templated variants. |
| **Metric** | compile-time |
| **Hardware** | AMD Ryzen AI 7 350 (8+8) at 5.09 GHz, Arch Linux; README says 'as of 2026-09', tables last updated in commit d16d0a5 on 2026-10-09 |
| **Compiler and flags** | From the public harness script cbench (./benchmark is a symlink to it; the C/C++, C3 and Odin blocks are identical in the 'benchmark' script at the table commit d16d0a5, 2026-10-09): gcc, g++, clang and clang++ get -Wall -Wextra (C) or -Wno-c++11-extensions (C++) and no -O flag, so default -O0; check uses -fsyntax-only, compile uses -c, build links through the driver's default system linker. c3c: check 'compile-only -q -O0 -C', compile 'compile-only -q -O0', build 'compile -q -O0 -o main' (c3c links with its default linker, 'cc' per its help text; the standard library is included by default). Versions: c3c 0.8.5, gcc/g++ 15.3.0 and 16.2.1, clang/clang++ 23.1.1. Each cell is the minimum of --run-count=10 repetitions (capped at 3 or 2 for steps over 1 s or 3 s) divided by 40,000 generated functions (200 x 200), with tasks run concurrently in a multiprocessing pool and each worker pinned to one core via os.sched_setaffinity. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README: no C3-specific mechanism is stated; the suite attributes the spread mostly to the cost of the GCC front end and optimizing backend. |
| **Adoption** | 5.9k stars, 408 forks (c3lang/c3c); benchmark repo nordlow/compiler-benchmark 167 stars, 17 forks, MIT |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/c3lang/c3c) · [benchmark](https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/README.md) |

## Verdict

One run of nordlow/compiler-benchmark on an AMD Ryzen AI 7 350 under Arch Linux (tables committed 2026-10-09) generated 200 x 200 arithmetic call-chain functions per language. c3c 0.8.5 at -O0 compiled the C3 version in 109.3 us per function (Total build+run 153), against gcc 15.3.0 at 193.8 (392) and gcc 16.2.1 at 400.1 (454) for the same C, both at default -O0 with -Wall -Wextra. clang 23.1.1 was faster than c3c at 77.9 (118).

## Use it when

- Fast debug-build turnaround in C-style code where the alternative toolchain is GCC: c3c's -O0 compile ran 1.8x faster than gcc 15.3.0 and 3.7x faster than gcc 16.2.1 on the same synthetic call chains.
- Projects mixing C and C3 that want C ABI compatibility and modules without headers, where GCC's -O0 compile time is the bottleneck.
- Large single files of plain, non-generic functions: untemplated C3 compiled 109.3 us/f against 256.6 us/f for the generic-module version.
- Platforms c3c lists as native hosts: Windows x64 and Aarch64, macOS x64 and Aarch64, Linux x86, x64, Aarch64 and RISC-V, OpenBSD x64.

## Skip it when

- If clang is an option: clang compiled the C version faster (Compile 77.9 vs 109.3 us/f, Total 118 vs 153), and clang++ beat C3 on templated code (Compile 128.7 vs 256.6, Total 107 vs 255).
- If compile speed is the main reason: dmd (13 us/f), Zig (110), Odin (147) and the single-pass C compilers tcc (4), cuik (76) and cproc (86) built the same program faster in the same table.
- Heavy use of generic modules: templated builds were 1.7x slower than untemplated, and issue #2383 showed layered generic modules pushing analysis of a trivial program from 71 ms to 7.6 s (closed as Invalid by the maintainer).
- Very small builds: every c3c invocation also processes the standard library unless --use-stdlib=no is passed. In issue #2383 a one-line program took 729 ms to compile on master (August 2025, machine not stated), a fixed cost the 40,000-function benchmark spreads out.
- If you need a stable language: the compiler is at 0.8.5 and the README says 0.8.6 will further refine the standard library.

## How it is fast

C3 has no preprocessor or headers, so the front end parses and checks a module once. Its semantic check alone (15.0 us/f) is slightly slower than gcc's -fsyntax-only (11.9 us/f), so the gain over GCC comes from code generation: c3c hands -O0 code to LLVM and writes object files directly, while GCC's -O0 path costs 182 us/f (gcc 15) to 388 us/f (gcc 16) beyond its syntax check (derived from page data). The suite itself does not explain any mechanism. By default c3c also emits each module as a separate compilation unit and spreads code generation over one thread per online CPU, but the harness pins each compiler to one core, so that parallelism did not count here.

## Compared with alternatives

Among the nordlow/compiler-benchmark entries, dmd (13 us/f) is more than ten times faster, Zig (110/92) is faster and does not slow down on generics, and Odin (147/98) roughly matches C3. rustc (187/238) is slower untemplated but faster templated (238 vs 255). Pick C3 when you want C syntax and the C ABI with faster -O0 builds than GCC, not for the fastest compiler in the table.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (prebuilt binaries for Windows, Linux static, macOS and OpenBSD; or build from source) |
| **Dependencies** | LLVM (fetched by CMake with C3_FETCH_LLVM=ON, or system LLVM and LLD), CMake, a C compiler and libcurl to build from source; a system cc to link by default (--linker=cc) |
| **Minimum toolchain** | c3c 0.8.5 as measured; building c3c needs CMake and LLVM (liblld-21 on Debian/Ubuntu per the README) |
| **Platforms** | Windows x64 and Aarch64, macOS x64 and Aarch64, Linux x86, x64, Aarch64, RISC-V 32 and 64, OpenBSD x64; Wasm32 and several freestanding ELF targets as cross targets |
| **Thread safety** | not applicable (command-line compiler); c3c defaults to --threads equal to sysconf(_SC_NPROCESSORS_ONLN) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: the GCC Total cells that give the headline 2.6x and 3.0x are unstable. gcc-15's Total (392 us/f) is double its own link-free Compile (193.8), which would mean about 8 s of linking for one object; clang++'s untemplated Total (236) is nearly three times its Compile (82.4), and its templated Total (107) is below its Compile (128.7). The link-free Compile column (C3 1.8x faster than gcc-15, 3.7x than gcc 16.2.1) is the more reliable comparison.
- Harness: tasks run at the same time in a multiprocessing pool, one worker pinned per CPU, and the CPU each row ran on is not recorded. cpu_topology.py's frequency-based path does not filter out SMT sibling threads (the Intel and cpu_capacity paths do), and the Ryzen AI 7 350 mixes Zen 5 and Zen 5c cores. So two compilers may have shared one physical core, or run on cores of different speed. Builds over 3 s, which includes c3c and all GCC rows, were timed only twice (minimum of 2).
- Unequal work against c3c: its -O0 is 'Safe, no optimizations, emit debug info' (help text), so it writes DWARF and runtime checks, while gcc and clang ran without -g; it also processes and emits the standard library on every build. Pinned to one core, its default 16 codegen threads time-share that core. All of these work against c3c, so its margin over GCC is not inflated by them.
- Nothing checks the output: the harness ignores the built binary's exit code and result, and all compilers built unoptimised code (no -O flag for gcc and clang, -O0 for c3c). These numbers say nothing about -O2 or -O3 build times or run-time speed.

## Known shortcomings

- Unoptimised compile throughput (gcc default -O0, c3c -O0): beats gcc/g++ only (Compile 109.3 vs 193.8/400.1 us per function), slower than clang (118 vs 153) and the templated clang++ row, and Check is slower than gcc; noisy cells, README prose from a different run; not a language-level claim.
- Harness flaws: gcc-15's Total of 392 is double its Compile of 193.8, so the headline 2.6x/3.0x is shaky and the Compile column (1.8x/3.7x) is more reliable; the concurrent pool does not record the core per row, cpu_topology.py's frequency path skips the SMT-sibling filter on the Zen 5 plus Zen 5c CPU, and builds over 3 s are timed twice. Unequal work against c3c: its -O0 is 'Safe, emit debug info', the stdlib is built every time, and 16 threads run on one pinned core. Clang is still faster.

## Caveats and trade-offs

Compile-time claim, not run-time: both sides build unoptimised code (gcc/g++/clang default -O0, c3c -O0), so the -O3 rule for run-time baselines and the crippled-baseline precedent do not apply; the win is the wave's off-baseline case and is recorded as a toolchain compile-speed entry. Not a language-level win: clang compiles the C version faster than c3c compiles the C3 version (Total 118 vs 153, Compile 77.9 vs 109.3) and clang++ templated beats C3 templated (107 vs 255), and C3's semantic check (15.0 us/f) is slower than gcc's -fsyntax-only (11.9), so the gap is GCC's -O0 code generation against c3c's LLVM -O0 path. C and C++ get -Wall -Wextra or -Wno-c++11-extensions; tcc (4), cuik (76) and cproc (86) compile C faster still. Synthetic arithmetic call chains in one translation unit with no headers, standard library or modules; the README says real builds are dominated by headers, module resolution and parallelism. Noisy cells: gcc-15 Total 392 is double its Compile 193.8, clang++ untemplated Total 236 is nearly 3x its Compile 82.4, clang++ templated Total 107 is below its Compile 128.7, and the README prose (clang 87, GCC \~418-455, c3c +77% templated) comes from a different run than the tables. The built binaries' results are never checked. Single machine, single sample run by an independent D-community developer. [retier] gcc-15's Total of 392 is double its Compile of 193.8; the concurrent pool does not record the core per row, cpu_topology.py's frequency path skips the SMT-sibling filter on the Zen 5 plus Zen 5c CPU, and builds over 3 s are timed twice. Unequal work against c3c: its -O0 is 'Safe, emit debug info', the stdlib is built every time, and 16 threads run on one pinned core. Clang is still faster.

Templated builds are 1.7x slower than untemplated (153 to 255 us/f); the compiler source is LGPL-3.0 while the rest of the repository is MIT.

## Maintenance

c3c is actively developed (last commits 2026-10-10, 4,830 commits, 5.9k stars, 145 open issues; MIT, with the compiler source under LGPL-3.0) but still pre-1.0 at 0.8.5; the benchmark is a single-machine run by an independent developer whose harness is public and MIT.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Public harness (cbench in nordlow/compiler-benchmark, MIT) with every compiler command line in code (gcc/g++/clang/clang++ at default -O0 with warning flags; c3c compile -q -O0), compiler versions in the README table (c3c 0.8.5, gcc/g++ 15.3.0 and 16.2.1, clang 23.1.1) and the CPU named (AMD Ryzen AI 7 350, Arch Linux), so it meets A; upgraded from B because the flags the record could not find are in the public script, consistent with the dmd row (batch-66) and the tinycc retier on the same suite.
- **Verifier notes:** Numbers match the README table exactly; flags read from cbench (the 'benchmark' file is a 6-byte symlink to cbench) and checked unchanged at the table commit d16d0a5. c3c MIT plus LGPL-3.0 compiler source, 5.9k stars, last commit 2026-10-10 confirmed. Record as a toolchain compile-speed entry beating GCC only (clang and tcc are faster); consider a compile-time or toolchain category rather than systems-and-safety, as for the dmd row.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-86 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/benchmark>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/d16d0a5/benchmark>
  - <https://github.com/nordlow/compiler-benchmark>
  - <https://github.com/nordlow/compiler-benchmark/commits/master/README.md>
  - <https://github.com/nordlow/compiler-benchmark/commits/master/cbench>
  - <https://github.com/c3lang/c3c>
  - <https://github.com/c3lang/c3c/commits>
  - <https://raw.githubusercontent.com/c3lang/c3c/master/src/build/build_options.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/benchmark>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/cpu_topology.py>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/process_timer.py>
  - <https://github.com/nordlow/compiler-benchmark/commits/master>
  - <https://github.com/c3lang/c3c>
  - <https://github.com/c3lang/c3c/commits/master>
  - <https://raw.githubusercontent.com/c3lang/c3c/master/README.md>
  - <https://raw.githubusercontent.com/c3lang/c3c/master/src/build/build_options.c>
  - <https://raw.githubusercontent.com/c3lang/c3c/master/src/utils/cpus.c>
  - <https://github.com/c3lang/c3c/issues?q=is%3Aissue+compile+time+slow>
  - <https://github.com/c3lang/c3c/issues/2383>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:c3/nordlow/compiler-benchmark#compile-throughput`) · [data/wave14/enrich/raw/lang_c3_nordlow_compiler_benchmark_compile_throughput.json](../../../data/wave14/enrich/raw/lang_c3_nordlow_compiler_benchmark_compile_throughput.json) (enrichment confidence 0.7)

</details>
