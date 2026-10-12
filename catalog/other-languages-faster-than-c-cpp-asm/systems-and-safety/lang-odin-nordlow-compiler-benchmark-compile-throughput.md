# Odin compiler compile throughput vs gcc and g++ in nordlow/compiler-benchmark

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Odin` · `Zlib` · 🟢 active

> The Odin compiler at its default -o:minimal builds a 40,000-procedure generated file 1.3-2.7x faster than GCC compiles the C twin, but slower than clang.

| | |
|---|---|
| **Beats** | C (gcc 15.3.0 and 16.2.1, clang 23.1.1) and C++ (g++ 15.3.0 and 16.2.1, clang++ 23.1.1) compiling the same generated arithmetic translation unit |
| **Claimed result** | README table (Ryzen AI 7 350), us per generated function, Total=Build+Run. Untemplated: Odin 147 vs C gcc-15 392 (2.7x), C gcc 16.2.1 454 (3.1x), C++ g++-15 303 (2.1x), C++ g++ 16.2.1 486 (3.3x), C++ clang++ 23.1.1 236 (1.6x); Odin is 1.25x slower than C clang 23.1.1 (118). Templated: Odin 98 vs g++-15 600 (6.1x), g++ 16.2.1 566 (5.8x), clang++ 107 (1.09x, near tie). Odin has no link-free Compile cell (the harness runs only check and build for Odin). Check column: Odin 19.1 (47.0 templated) is slower than gcc -fsyntax-only (11.9 and 11.8) and clang (13.5). All ratios derived from page data. |
| **Workload** | nordlow/compiler-benchmark: compile (and run) one massive synthetic translation unit of arithmetic call chains, reported as microseconds per generated function ('Total=Build+Run [us/f]'), untemplated and templated variants. |
| **Metric** | compile-time |
| **Hardware** | AMD Ryzen AI 7 350 (8+8) at 5.09 GHz, Arch Linux; README says 'as of 2026-09', tables last updated in commit d16d0a5 on 2026-10-09 |
| **Compiler and flags** | From the public harness script cbench (./benchmark is a symlink to it; the C/C++, C3 and Odin blocks are identical in the 'benchmark' script at the table commit d16d0a5, 2026-10-09): gcc, g++, clang and clang++ get -Wall -Wextra (C) or -Wno-c++11-extensions (C++) and no -O flag, so default -O0; check uses -fsyntax-only, compile uses -c, build links through the driver's default system linker. Odin: check 'odin check &lt;file&gt; -file', build 'odin build &lt;file&gt; -file -build-mode:exe -linker:lld -out:main' with no -o flag, so Odin's default -o:minimal (per odin's help text; separate LLVM build units by default at that level). Versions: odin dev-2026-09:a2fb372b7, gcc/g++ 15.3.0 and 16.2.1, clang/clang++ 23.1.1. Each cell is the minimum of --run-count=10 repetitions (capped at 3 or 2 for steps over 1 s or 3 s) divided by 40,000 generated functions (200 x 200), with tasks run concurrently in a multiprocessing pool and each worker pinned to one core via os.sched_setaffinity. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README: the claim is throughput of the compiler front end and linking against GCC's heavier pipeline; no Odin-specific mechanism is stated in the sections read. |
| **Adoption** | 12.1k stars, 1.1k forks (odin-lang/Odin); benchmark repo nordlow/compiler-benchmark 167 stars, 17 forks, MIT |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/odin-lang/Odin) · [benchmark](https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/README.md) |

## Verdict

One run of nordlow/compiler-benchmark (tables committed in d16d0a5 on 2026-10-09) on an AMD Ryzen AI 7 350 under Arch Linux generated 200 x 200 arithmetic call-chain procedures. odin dev-2026-09:a2fb372b7 at its default -o:minimal built the Odin version, lld link included, in 147 us per function (98 templated). For the same C at default -O0 with -Wall -Wextra, gcc 15.3.0 took 392 Total (193.8 object-only) and gcc 16.2.1 took 454 (400.1); clang 23.1.1 was faster at 118 (77.9). Odin's check step (19.1 us/f) was slower than gcc -fsyntax-only (11.9).

## Use it when

- Debug-build turnaround for Odin projects when the alternative on the table is C or C++ built with GCC: a full Odin build of plain procedures ran 1.3x faster than gcc 15's object-only -c and 2.7x faster than gcc 16.2.1's (derived from page data).
- Generic code: Odin's parametric-polymorphic variant built in 98 us/f, against 600 and 566 us/f for g++ 15 and 16 templates and 107 for clang++, and far below C3 (255) and rustc (238) in the same table.
- Hosts where the compiler may use every core: Odin starts one worker thread per online CPU by default, which this benchmark disabled by pinning each compiler to one core (inference: unpinned speed was not measured).
- Compact debug-level binaries: 112.6 B per function against 121.1 for gcc and 146.1 for clang, because -o:minimal already runs SROA and CSE.

## Skip it when

- If you could compile C with clang: clang 23.1.1 built the C version faster (link-free Compile 77.9 us/f, Total 118 vs Odin's 147), and clang++ compiled the untemplated C++ in 82.4.
- If compile speed is the main reason to switch: dmd (13 us/f), Zig (110), Free Pascal (138) and the single-pass C compilers tcc (4), cuik (76) and cproc (86) built the same program faster.
- Memory-limited build machines: Odin's build peaked at 34.0 kB per function (sampled RSS summed over the compiler's process tree), about 1.36 GB for the 40,000-procedure file, against 17.2 kB/f for gcc 15 (about 0.69 GB) and 6.8 kB/f for clang (about 0.27 GB), so 2-5x more (derived from page data).
- Optimised release builds: the benchmark ran only Odin's default -o:minimal and gcc/clang at default -O0, so it says nothing about -o:speed build times (single build unit, LLVM default code generation) or run-time speed.
- WSL2 or other virtualised Linux hosts: open issue #7128 shows the default thread pool thrashing on futexes (a hello-world build took 2381 ms, 767 ms with -thread-count:1); the README also warns that the compiler is still in development.

## How it is fast

Not the front end: Odin's check alone costs 19.1 us/f against 11.9 for gcc -fsyntax-only and 13.5 for clang. The gain over GCC is in code generation: Odin's whole build minus its check is about 128 us/f (including the lld link and compiling its own runtime and core:os packages), while GCC's object-only -O0 path costs 182 us/f (gcc 15) to 388 us/f (gcc 16) beyond its syntax check (derived from page data). Odin's default -o:minimal runs a short LLVM IR pipeline (SROA, early-CSE, instsimplify, simplifycfg, always-inline per src/llvm_backend_passes.cpp) and then LLVM code generation at CodeGenLevelNone (src/llvm_backend.cpp), emitting several build units that are linked together (the -use-separate-modules default at that level, per the compiler's help text). In effect Odin inherits LLVM's fast no-optimisation backend, the same one that puts clang ahead of gcc in this table, and adds a heavier front end, so it lands between clang and gcc; the suite itself names no mechanism.

## Compared with alternatives

Of the nordlow/compiler-benchmark siblings, dmd (13 us/f) is more than ten times faster and Zig (110/92) is faster on both variants. C3 (153/255) roughly ties Odin on plain code but is 2.6x slower on generics, and rustc (187/238) is slower on both. Pick Odin when you want a C alternative whose default debug builds beat GCC and stay cheap with generic code, not for the fastest compiler in the table.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (command-line compiler; release and nightly builds linked from the README, or build from source) |
| **Dependencies** | LLVM as the backend; on Linux the clang driver for linking (src/linker.cpp runs `clang`, overridable with ODIN_CLANG_PATH) plus lld when -linker:lld is passed, as in this benchmark |
| **Minimum toolchain** | odin dev-2026-09:a2fb372b7 as measured (monthly dev tag) |
| **Platforms** | Windows, Linux and macOS per the README badge; measured on x86-64 Arch Linux only |
| **Thread safety** | not applicable (command-line compiler); defaults to one worker thread per online CPU (gb_affinity_init uses sysconf(_SC_NPROCESSORS_ONLN) and ignores the affinity mask), override with -thread-count |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry and noisy Total cells: Odin links with clang -fuse-ld=lld (-linker:lld) while gcc and g++ use the default system linker, and the harness runs no link-free compile step for Odin. The Total column behind the record's 2.7x over gcc 15 is unstable (gcc 15's C Total of 392 is double its own Compile of 193.8; clang++'s templated Total of 107 is below its Compile of 128.7). A conservative reading puts Odin's whole build, link included (147 us/f), against GCC's object-only -c: still 1.3x faster than gcc 15 (193.8), 2.7x than gcc 16.2.1 (400.1), 1.8x than g++ 15 (269.6) and 2.5x than g++ 16.2.1 (372.3). The win over GCC survives the linker asymmetry, but the headline against gcc 15 shrinks from 2.7x to 1.3x.
- Unequal work that counts against Odin: -o:minimal runs SROA, early-CSE, instsimplify and simplifycfg, more than gcc or clang do at -O0, and every Odin build type-checks and compiles base:runtime and core:os from source, because the generated program imports core:os for os.exit, while C links a precompiled libc. The C side adds only -Wall -Wextra.
- Concurrency and pinning: tasks run at the same time in a multiprocessing pool with each worker pinned to one CPU by os.sched_setaffinity. Odin ignores that mask and starts one thread per online CPU, so all of them time-share one core (issue #7128 shows how costly its futex-based pool can be on some hosts). cpu_topology.py's frequency path does not drop SMT siblings, so two compilers may have shared one physical core. Odin's 5.9 s builds, like every gcc build over 3 s, keep the minimum of only 2 repetitions.
- Unexplained cells and unchecked output: Odin's templated build (98) is faster than its untemplated one (147) even though its templated check is 2.5x slower (47.0 vs 19.1), which implies 2.5x cheaper code generation for generic procedures; noise is the likelier explanation. The README prose figures (odin 92, clang 87 us/f) come from a different run than the tables. The harness ignores the built binary's exit code and result.

## Known shortcomings

- Odin links with lld while gcc uses the default linker and there is no Compile cell, so the linker share cannot be separated; Check 19.1 is slower than gcc 11.9; slower than clang (118); noisy cells, README prose from a different run; not a language-level claim.
- Harness asymmetry and noisy Total cells: Odin links with clang -fuse-ld=lld while gcc and g++ use the system linker, there is no link-free compile step for Odin, and the Total column is unstable (gcc-15's C Total 392 is double its own Compile 193.8). A conservative reading of Odin's whole build including the link (147 us/f) against GCC's object-only -c still gives 1.3x over gcc-15 (193.8) and 2.7x over gcc 16.2.1 (400.1), so the win survives but the headline against gcc-15 shrinks from 2.7x to 1.3x. Flaws working against Odin: it ignores the affinity mask (sysconf online CPUs gives 16 threads on one pinned core; futex issue #7128 open), -o:minimal runs SROA and early CSE (more than -O0), and every build compiles base:runtime and core:os. The templated 98 &lt; untemplated 147 result is unexplained; build RSS is about 34.0 kB per function (about 1.36 GB) against gcc 17.2 and clang 6.8. No correctness bug.

## Caveats and trade-offs

Compile-time claim, not run-time: both sides build unoptimised or minimally optimised code (gcc/g++/clang default -O0, Odin default -o:minimal), so the -O3 rule for run-time baselines and the crippled-baseline precedent do not apply; recorded as a toolchain compile-speed entry. Not a language-level win: clang compiles the C version faster (118 vs 147 us/f), Odin's check (19.1) is slower than gcc -fsyntax-only (11.9), and tcc, cuik, cproc, dmd, ldmd2, Zig and fpc are all faster, so the win is against GCC's -O0 pipeline only. Harness asymmetry: Odin builds link with lld (-linker:lld) while gcc and g++ use the default system linker, and Odin has no link-free Compile cell, so the linker share of the gap cannot be separated; C adds -Wall -Wextra. Synthetic arithmetic call chains in one file with no headers, standard library or modules (the README says real builds differ). Noisy cells: Odin templated (98) is faster than untemplated (147), gcc-15 Total 392 is double its Compile 193.8, and the README prose (odin 92, clang 87, GCC \~418-455) comes from a different run than the tables. The built binaries' results are never checked. Single machine, single sample run by an independent D-community developer. [retier] Enricher: harness asymmetry and noisy Total cells; Odin links with clang -fuse-ld=lld while gcc and g++ use the system linker, there is no link-free compile step for Odin, and the Total column is unstable (gcc-15's C Total 392 is double its own Compile 193.8). A conservative reading of Odin's whole build including the link (147 us/f) against GCC's object-only -c still gives 1.3x over gcc-15 (193.8), 2.7x over gcc 16.2.1 (400.1), 1.8x over g++-15 (269.6) and 2.5x over g++ 16.2.1 (372.3), so the headline against gcc-15 shrinks from 2.7x to 1.3x. Flaws working against Odin: it ignores the affinity mask (16 threads on one pinned core; futex issue #7128 open), -o:minimal runs SROA and early CSE, and every build compiles base:runtime and core:os. Build RSS is about 34.0 kB per function against gcc 17.2 and clang 6.8.

Odin emits compact code (112.6 B/f, close to gcc's 121.1 B/f); build uses LLVM through the Odin compiler.

## Maintenance

Odin is actively developed (12.1k stars, 20,065 commits, 770 open issues, Zlib licence, last commit 2026-10-11 per the verification record) but pre-1.0, with monthly dev tags and a README warning that the compiler is still in development; the evidence is one run on one laptop by an independent developer using a public MIT harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Public harness (cbench in nordlow/compiler-benchmark, MIT) with every command line in code (gcc/g++/clang/clang++ at default -O0 with warning flags; 'odin build &lt;file&gt; -file -build-mode:exe -linker:lld' at Odin's default -o:minimal), compiler versions in the README table (odin dev-2026-09:a2fb372b7, gcc/g++ 15.3.0 and 16.2.1, clang 23.1.1) and the CPU named (AMD Ryzen AI 7 350, Arch Linux), so it meets A; upgraded from B because the flags are in the public script, consistent with the dmd row (batch-66).
- **Verifier notes:** Numbers match the README table exactly; flags read from cbench and checked unchanged at the table commit d16d0a5. Odin Zlib, 12.1k stars, last commit 2026-10-11 confirmed. The record's why_faster ('front end') is contradicted by the Check column and is corrected; record as a toolchain compile-speed entry that beats GCC only, with the lld-vs-default-linker asymmetry as its main shortcoming; category is a loose fit, as for the dmd row.
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
  - <https://github.com/odin-lang/Odin>
  - <https://github.com/odin-lang/Odin/commits>
  - <https://raw.githubusercontent.com/odin-lang/Odin/master/src/main.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/d16d0a5/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/d16d0a5/benchmark>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/cpu_topology.py>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/process_timer.py>
  - <https://github.com/odin-lang/Odin>
  - <https://github.com/odin-lang/Odin/issues?q=is%3Aissue+compile+time+slow>
  - <https://github.com/odin-lang/Odin/issues/7128>
  - <https://raw.githubusercontent.com/odin-lang/Odin/master/README.md>
  - <https://raw.githubusercontent.com/odin-lang/Odin/master/src/main.cpp>
  - <https://raw.githubusercontent.com/odin-lang/Odin/master/src/build_settings.cpp>
  - <https://raw.githubusercontent.com/odin-lang/Odin/master/src/gb/gb.h>
  - <https://raw.githubusercontent.com/odin-lang/Odin/master/src/llvm_backend.cpp>
  - <https://raw.githubusercontent.com/odin-lang/Odin/master/src/llvm_backend_opt.cpp>
  - <https://raw.githubusercontent.com/odin-lang/Odin/master/src/llvm_backend_passes.cpp>
  - <https://raw.githubusercontent.com/odin-lang/Odin/master/src/linker.cpp>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:odin/nordlow/compiler-benchmark#compile-throughput`) · [data/wave14/enrich/raw/lang_odin_nordlow_compiler_benchmark_compile_throughput.json](../../../data/wave14/enrich/raw/lang_odin_nordlow_compiler_benchmark_compile_throughput.json) (enrichment confidence 0.7)

</details>
