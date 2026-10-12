# Zig compiler (zig build-exe) compile throughput vs gcc and g++ in nordlow/compiler-benchmark

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig's self-hosted x86-64 backend and linker build a 40,000-function test file 3.6-4.1x faster than gcc, about level with clang.

| | |
|---|---|
| **Beats** | C (gcc 15.3.0 and 16.2.1, clang 23.1.1) and C++ (g++ 15.3.0 and 16.2.1, clang++ 23.1.1) compiling the same generated arithmetic translation unit |
| **Claimed result** | README table (AMD Ryzen AI 7 350 run, tables updated 2026-10-09), Total=Build+Run us/f (untemplated / templated): Zig 110 / 92 vs C gcc-15 392, C gcc-16 454, C++ g++-15 303 / 600, C++ g++-16 486 / 566, C clang 118, C++ clang++ 236 / 107. Derived from page data: 3.6x faster than gcc-15 and 4.1x faster than gcc-16 on C, 6.5x faster than g++-15 and 6.2x faster than g++-16 templated, 1.16x faster than clang++ templated, and 7% faster than clang C (118 vs 110). Slower than tcc 4, dmd 13, cuik 76, cproc 86 and ldmd2 95 in the same suite. The README's Conclusions section, from an earlier run, has zig 97 against clang 87 us/f (clang faster) and calls them 'on par'. |
| **Workload** | nordlow/compiler-benchmark: compile (and run) one massive synthetic translation unit of arithmetic call chains, reported as microseconds per generated function ('Total=Build+Run [us/f]'), untemplated and templated variants. |
| **Metric** | compile-time |
| **Hardware** | AMD Ryzen AI 7 350 (8+8 cores) at 5.09 GHz, Arch Linux, sample run as of 2026-09 |
| **Compiler and flags** | Flags are in the public harness cbench (README's ./benchmark is a symlink to it; the same flag code is in benchmark at d16d0a5, the 2026-10-09 commit that updated the README tables): gcc/clang C build = -Wall -Wextra -o &lt;exe&gt; with no -O flag (GCC/Clang default -O0), C++ uses -Wno-c++11-extensions instead of the warning flags; rustc gets no flags (RUSTC_FLAGS = [], so opt-level 0 through LLVM with debug assertions and overflow checks on by default; the cranelift RUSTC_NIGHTLY_FLAGS list is defined but unused); zig build-exe -fno-llvm -fno-lld -fno-clang (Debug mode, Zig's self-hosted x86_64 backend and linker). Versions from the README table: rustc 1.100.0-nightly, zig 0.18.0-dev.35+5e754304d, gcc 15.3.0 and 16.2.1, clang 23.1.1. Defaults: 200 chains x depth 200 = 40,000 functions per file, minimum of up to 10 builds (capped to 2-3 when a build exceeds 1-3 s), constants re-randomised per run to defeat caches. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README: Zig shows near-zero generic overhead (97 vs 92 us/f untemplated vs templated) thanks to comptime evaluation of uniform scalar types; the README groups Zig with odin as 'neck-and-neck with clang' and does not name a mechanism for the gap to gcc beyond the heavy GCC front end and backend. |
| **Adoption** | 43.3k stars (GitHub repo moved to Codeberg) |
| **Last commit** | 2025-11-27 |
| **Links** | [repository](https://github.com/ziglang/zig) · [benchmark](https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/README.md) |

## Verdict

In one run of nordlow/compiler-benchmark (AMD Ryzen AI 7 350, Arch Linux, tables committed 2026-10-09), zig 0.18.0-dev.35 with -fno-llvm -fno-lld -fno-clang in Debug mode built and ran a generated 40,000-function file in 110 us per function (92 templated), against unoptimised builds of the same program with gcc 15.3.0 (392), gcc 16.2.1 (454) and clang 23.1.1 (118) for C, and g++ 15.3.0 (303 / 600 templated), g++ 16.2.1 (486 / 566) and clang++ 23.1.1 (236 / 107) for C++. That is 3.6x to 4.1x faster than gcc, 2.8x to 6.5x faster than g++ and 1.07x faster than clang on Total; on link-free compile clang is faster (77.9 vs 93.2 us/f) (all ratios derived from page data).

## Use it when

- Debug-build edit-compile-run loops in Zig projects on x86-64 Linux: per the Zig 0.15.1 release notes (search snippet only) the self-hosted x86 backend became the Debug default there with about 5x faster debug compilation, and -fno-llvm forces it.
- Choosing a systems language where clean unoptimised rebuild time matters and the reference toolchain is GCC: here Zig built the same program 3.6x faster than gcc 15.3.0 and 4.1x faster than gcc 16.2.1 (C), and 2.8x to 6.5x faster than g++ 15.3.0 and 16.2.1 (C++, plain and templated).
- Generic-heavy code: Zig's comptime-generic variant built no slower than the plain one (Total 92 vs 110 us/f), while g++-15 went from 303 to 600 us/f on the templated variant.

## Skip it when

- As evidence that Zig compiles faster than C with Clang: clang compiles the same C faster on Check (13.5 vs 22.3 us/f) and Compile (77.9 vs 93.2), the Totals (118 vs 110) are inside the run-to-run spread, and the README's earlier run had clang 87 vs zig 97 us/f.
- For optimised builds: only unoptimised builds were measured (no -O flag for any compiler); Zig's ReleaseFast and ReleaseSafe build times and the speed of the generated code are not covered.
- When binary size matters: Zig's Debug executables carry 1,422-1,503 bytes per function against 121 for gcc and 146 for clang (README: runtime scaffolding, unwinding metadata and alignment padding).
- For an existing C or C++ codebase: the measured path compiles Zig source only (the harness disables Zig's bundled Clang with -fno-clang), so switching a C/C++ build to the zig driver does not reproduce these numbers.
- Targets other than x86-64: per the 0.15.1 notes (snippet only) the aarch64 self-hosted backend was still in progress, and the 2025 announcement said the default was not yet changed on Windows.

## How it is fast

Zig lowers source through its own pipeline (AstGen, Sema, then the self-hosted x86-64 backend) and links in-process, so no LLVM IR, LLVM code generation or separate system linker run; gcc and clang compile at -O0 and their drivers invoke the system linker. The README's column breakdown shows where the gain sits: on Check (semantic analysis only) Zig is slower than every C and C++ compiler (22.3 us/f vs gcc-15 11.9 and clang 13.5); on link-free Compile it is 2.1x faster than gcc-15 (93.2 vs 193.8) and 4.3x faster than gcc 16.2.1 (400.1) but 1.2x slower than clang (77.9); its Total lead over clang (110 vs 118) comes from linking in-process, roughly 17 us/f of Total beyond Compile against about 40 for clang (derived from page data). The README credits comptime evaluation of uniform scalar types for the absent generic penalty.

## Compared with alternatives

In the same table dmd is about 8x faster than Zig on Total (13 vs 110 us/f) and also faster on Check and Compile, so pick the dmd entry for raw cold-build throughput; Zig beats the Odin (147), C3 (153) and rustc (187) rows on Total, so pick it among those when you want comptime generics with no measured build penalty and a full semantic check in debug builds.

## Integration

| | |
|---|---|
| **Form** | toolchain (single zig executable compiling Zig source; not a library) |
| **Dependencies** | none for the measured path: -fno-llvm -fno-lld -fno-clang means no LLVM, LLD, Clang or system linker is invoked |
| **Minimum toolchain** | measured on zig 0.18.0-dev.35+5e754304d (an unreleased development build from Codeberg); the self-hosted x86 backend became the Debug default in 0.15.1 (release notes, search snippet only) |
| **Platforms** | x86-64 (measured on Arch Linux, AMD Ryzen AI 7 350); other targets not measured |
| **Thread safety** | not applicable (command-line compiler); the harness pins each compiler process to one logical CPU, so any internal compiler threads share that CPU |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness inconsistency found in the table: Zig's templated Total (build-exe, 92 us/f) is lower than its own templated Compile (build-obj, 109.8 us/f), although building an executable includes compiling; clang++ templated has the same inversion (107 vs 128.7) and gcc-15's C Total (392) is twice its Compile (193.8). Cells therefore carry noise of 20% or more, and the README's 'near-zero generic overhead' for Zig rests on the Total column, while Zig's own Check (22.3 to 33.8 us/f, +52%) and Compile (93.2 to 109.8, +18%) columns show a real templated cost (derived from page data).
- Harness: all tasks run at the same time in a multiprocessing pool with one worker pinned per CPU; cpu_topology.py's frequency-based hybrid path does not drop SMT sibling threads, the Ryzen AI 7 350 mixes Zen 5 and Zen 5c cores, and the CPU each row ran on is not recorded. Builds over 3 s keep the minimum of only 2 runs, which covers Zig's roughly 4.4 s build (110 us/f x 40,000) and every gcc and g++ row.
- The win over clang is the in-process linker, not code generation: Zig uses its own linker (-fno-lld) while gcc and clang call the system linker; on the link-free Compile column clang is 1.2x faster than Zig.
- Nothing checks the output: the harness sends the built program's output to /dev/null and ignores its exit code, and the compilers do unequal work at 'unoptimised' (Zig Debug emits runtime safety checks, C and C++ at default -O0 with -Wall -Wextra do not), which works against Zig.

## Known shortcomings

- zig build-exe -fno-llvm -fno-lld (self-hosted backend, Debug) only ties clang C (110 vs 118 us per function; the README's earlier run has clang faster, 87 vs 97) and wins over GCC only; output is 12x larger per function; unoptimised compile throughput, not run time.
- Noisy cells: Zig's templated Total (build-exe, 92 us per function) is below its own templated Compile (build-obj, 109.8), clang++ shows the same inversion (107 vs 128.7), and cells carry noise of 20% or more; the README's 'near-zero generic overhead' rests on that cell while Zig's own Check (+52%) and Compile (+18%) columns show a real templated cost. The win over clang comes only from the in-process linker (link-free Compile clang 77.9 vs Zig 93.2). Also a pinned concurrent pool on an SMT Zen 5c core, the minimum of 2 runs, and no output check. Zig 0.17 and 0.18 sources were unchecked (codeberg blocked).

## Caveats and trade-offs

Compile-time comparison of unoptimised builds on one synthetic translation unit of 40,000 arithmetic functions with no headers, standard library or module resolution (the README says it does not reflect real builds); not the wave's run-time -O3 comparison. The README does not state flags, but the harness does: zig build-exe -fno-llvm -fno-lld -fno-clang (Debug mode, self-hosted x86_64 backend and linker) against gcc/clang with only -Wall -Wextra (default -O0), so optimisation levels are matched at 'unoptimised' while Zig skips LLVM and the system linker entirely. Not a language win over C: clang compiles the same C at 118 us/f against Zig's 110 (7%, inside the run-to-run spread; the README's earlier run has clang 87 vs zig 97, clang faster), and tcc, dmd, cuik, cproc and ldmd2 beat Zig; the large margin is over GCC, whose GCC 15 to 16 regression the README flags. Zig's output is 1,422 to 1,503 B per function against 121 B for gcc (README: runtime scaffolding and unwinding metadata). One sample run; tasks run concurrently in a pinned multiprocessing pool on a Zen 5/Zen 5c part, and the gcc-15 C build (392) is twice its compile-only time (193.8), a sign of noise. The GitHub repository of Zig says 'Moved to Codeberg' and its last GitHub commit is 2025-11-27, so metadata here is a pointer, not the live repository. The sibling record for D (dmd) is from the same table. Independent suite, but a small one (167 stars), one machine. [retier] Enricher: Zig's templated Total (build-exe, 92 us per function) is below its own templated Compile (build-obj, 109.8), clang++ shows the same inversion (107 vs 128.7) and gcc-15's C Total (392) is twice its Compile (193.8), so cells carry noise of 20% or more; the README's 'near-zero generic overhead' rests on that cell while Zig's own Check (+52%) and Compile (+18%) columns show a real templated cost. The win over clang comes only from the in-process linker (link-free Compile clang 77.9 vs Zig 93.2). Pinned concurrent pool on an SMT Zen 5c core, minimum of 2 runs, no output check.

Compile speed only; the generated executables are about 12x larger per function than gcc's (1,503 vs 121 B/f).

## Maintenance

Zig is MIT-licensed and actively developed on Codeberg, with the GitHub repository a frozen copy since 2025-11-27 ('README: migrated to codeberg'), and the measured compiler is an unreleased 0.18 development build; the evidence is one single-machine run of a public MIT harness that changes daily (ten commits on 2026-10-12), with no output check and table cells that contradict each other by 20% or more.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A: independent public harness (nordlow/compiler-benchmark cbench: bm_Zig with zig build-exe -fno-llvm -fno-lld -fno-clang, gcc_clang_op_flags with no -O flag) fixes every flag, the README table names every compiler version, and the CPU is stated (AMD Ryzen AI 7 350, Arch Linux). All README numbers in the claim match the Zig, C and C++ rows.
- **Verifier notes:** Numbers and ratios check out against the README table; tier raised to A because the public harness pins every flag and the CPU and versions are stated. Shortcomings to record: compile-time of unoptimised builds on one synthetic file (off the wave's run-time -O3 baseline), Zig only ties clang C (7%, reversed in the README's earlier run) so the win is over GCC's backend via Zig's self-hosted no-LLVM backend, not a language effect; 12x larger output per function; single noisy run.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-87 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/benchmark>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/d16d0a5/benchmark>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cpu_topology.py>
  - <https://github.com/nordlow/compiler-benchmark>
  - <https://github.com/nordlow/compiler-benchmark/commits>
  - <https://github.com/nordlow/compiler-benchmark/commits/master/README.md>
  - <https://github.com/ziglang/zig>
  - <https://github.com/ziglang/zig/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/benchmark>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cbench>
  - <https://raw.githubusercontent.com/nordlow/compiler-benchmark/HEAD/cpu_topology.py>
  - <https://github.com/nordlow/compiler-benchmark/commits/master>
  - <https://github.com/ziglang/zig>
  - <https://github.com/ziglang/zig/commits>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:zig/nordlow/compiler-benchmark#compile-throughput`) · [data/wave14/enrich/raw/lang_zig_nordlow_compiler_benchmark_compile_throughput.json](../../../data/wave14/enrich/raw/lang_zig_nordlow_compiler_benchmark_compile_throughput.json) (enrichment confidence 0.6)

</details>
