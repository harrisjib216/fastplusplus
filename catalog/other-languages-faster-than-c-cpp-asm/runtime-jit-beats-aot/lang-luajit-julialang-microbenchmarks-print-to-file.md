# LuaJIT 2.1: print_to_file in JuliaLang/Microbenchmarks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Lua` · `MIT` · 🟢 active

> LuaJIT 2.1 writes 100,000 formatted integer lines to /dev/null in 6.26 ms versus 8.02 ms for C fprintf, on separate CI runners.

| | |
|---|---|
| **Beats** | C fprintf loop (c/perf.c printfd: fprintf(f, "%ld %ld\n", i, i+1) to /dev/null) built with gcc 13.3.0 -std=c99 -O2 |
| **Claimed result** | LuaJIT 6.26 ms vs C 8.02 ms (0.78x of the C time, about 1.28x faster, derived from page data). Rust 4.17 ms (0.52x) is also faster than C; Julia 10.17 ms (1.27x) and Java 58.74 ms are slower. |
| **Workload** | Write 100,000 formatted lines to /dev/null; each language runs the benchmark 5 times internally, the Makefile invokes each script 3 times, and the overall minimum is reported. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu-latest runners (x86_64). Each language runs in its own workflow job (bench-c, bench-lua, ...) and so on its own runner VM, and the results are only collected afterwards. No CPU model is stated, and the C and LuaJIT runs may have used different CPUs. Single-thread environment variables are set. |
| **Compiler and flags** | C: gcc 13.3.0 -std=c99 -O2 (the Makefile copies benchmarks/c2.csv, built from bin/perf2, into benchmarks/c.csv; the workflow passes no extra CFLAGS), linked with OpenBLAS. LuaJIT 2.1.1703358377 from Ubuntu's apt luajit package, run as 'luajit lua/perf.lua'. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 91 stars |
| **Last commit** | 2026-04-21 |
| **Links** | [repository](https://github.com/JuliaLang/Microbenchmarks) · [benchmark](https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/benchmarks/index.html) |

## Verdict

On the JuliaLang/Microbenchmarks results page (generated 21 April 2026), print_to_file took 6.26 ms under LuaJIT 2.1.1703358377 against 8.02 ms for C fprintf built with gcc 13.3.0 -std=c99 -O2, both writing 100,000 lines to /dev/null and both reported as the minimum of 15 timed runs. C and LuaJIT ran in different GitHub Actions jobs on separate ubuntu-latest x86_64 runners with no CPU model given, so the ratio is a cross-machine comparison.

## Use it when

- You already run Lua code under LuaJIT and its hot loop emits many lines of integers through string.format and file:write: this shows that path is competitive with C stdio.
- Logging or report generation from LuaJIT where the format string is a constant literal, so the recorder can specialise it.
- As a data point that printf-family formatting in C is slow per call, before you blame the language: a specialised integer formatter beats glibc fprintf.

## Skip it when

- As evidence that LuaJIT beats C in general: in the same table LuaJIT is slower than C on the other seven benchmarks (recursion_fibonacci 5.20x, userfunc_mandelbrot 2.54x, matrix_statistics 2.29x, recursion_quicksort 2.24x, parse_integers 1.21x, matrix_multiply 1.14x, iteration_pi_sum 1.07x).
- As a C or C++ replacement for formatted output: Rust's BufWriter plus writeln! ran in 4.17 ms (0.52x of C) in the same table, and a C program that calls an integer-to-string routine and fwrite directly (as LuaJIT does internally) was not measured but would likely remove most of the gap.
- Format strings that are built at run time, or arguments that are not narrowed integers: the recorder then falls back to generic lj_strfmt_putfnum_int, lj_strfmt_putfxint or lj_strfmt_putfnum calls, or aborts the trace (%p, non-string %s).
- Workloads where per-line string allocation matters: each string.format result is still materialised as an interned Lua string (IR_BUFSTR) before fwrite, so there is GC pressure that the measurement on /dev/null does not expose.

## How it is fast

LuaJIT's trace recorder (recff_format in src/lj_ffrecord.c) guards on the constant format string, parses it once at record time, and emits a plain-%d shortcut (IR_TOSTR with IRTOSTR_INT) for each narrowed integer argument; the assembler (asm_bufput in src/lj_asm.c) fuses that into direct lj_strfmt_putint calls, which use the digit-pair routine lj_strfmt_wint, and the one-character literals become lj_buf_putchar calls. recff_io_write then calls fwrite on the FILE\* straight from the trace. glibc's fprintf instead re-parses the format string through vfprintf on every call. So the win is LuaJIT's runtime formatter (written in C) against glibc printf, not JIT-generated user code beating gcc's codegen; this is inference from the sources, since the suite states no mechanism.

## Compared with alternatives

Among the LuaJIT siblings, the kostya/jit-benchmarks k-nucleotide row (A tier, 2.7x over an untuned std::unordered_map) and the dyu/ffi-overhead call-loop row (1.3x on FFI calls) are stronger evidence; cite this row only when the question is specifically formatted text output from LuaJIT, and treat it as directional.

## Integration

| | |
|---|---|
| **Form** | LuaJIT runtime: the luajit executable, or libluajit (static or shared) embedded through the Lua C API |
| **Dependencies** | none for this benchmark (the suite's perf.lua also requires the scilua 'sci' rock and OpenBLAS for its matrix rows) |
| **Minimum toolchain** | LuaJIT 2.1 (measured with Ubuntu's luajit package, version 2.1.1703358377); building LuaJIT needs GCC, Clang or MSVC and GNU Make |
| **Platforms** | x86, x64, ARM, ARM64, PPC, MIPS32 and MIPS64 targets in src/lj_arch.h; Linux, macOS, BSD and Windows builds; measured on x86_64 GitHub Actions runners only |
| **Thread safety** | not documented for this benchmark; a LuaJIT lua_State is single-threaded and the benchmark is serial |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: .github/workflows/benchmarks.yml runs C (job bench-c) and LuaJIT (job bench-lua) on separate ubuntu-latest runner VMs and only collects the CSVs afterwards, with no CPU model recorded, so the 6.26 ms vs 8.02 ms ratio crosses machines; a 1.28x gap is within the spread one can expect between shared runner VMs.
- The two sides use different timers and inputs: c/perf.c times with gettimeofday (wall clock, microsecond resolution) while lua/perf.lua uses clock_gettime(CLOCK_MONOTONIC) through the FFI; C writes i = 0..99,999 and Lua writes i = 1..100,000. Rust's version writes "i i" rather than "i i+1". These differences are small next to the cross-runner problem.
- The C baseline is built at -O2 (the Makefile copies benchmarks/c2.csv into c.csv), but the time is spent in glibc's vfprintf, so the optimisation level of perf.c barely matters here.
- The %d shortcut depends on the trace narrowing the loop variable to an integer; the first of the five internal repetitions also includes trace recording, and the reported number is the best of up to 15 runs, so it reflects the compiled steady state only.

## Known shortcomings

- Cross-machine: the workflow runs bench-c and bench-lua on separate ubuntu-latest VMs with no CPU model; C built -O2; the win comes from LuaJIT's runtime formatter (recff_format specialisation, lj_strfmt_wint) against glibc vfprintf, not codegen. Language-level row on LuaJIT (listed in wave 12).
- The cross-runner flaw is confirmed in .github/workflows/benchmarks.yml (jobs bench-c and bench-lua on separate ubuntu-latest VMs, no CPU model recorded) and the two sides also use different timers (C gettimeofday, Lua clock_gettime CLOCK_MONOTONIC through the FFI) and slightly different inputs (C writes 0..99,999, Lua 1..100,000). The win is LuaJIT's specialised string.format (recff_format, asm_bufput fusing to lj_strfmt_putint) plus fwrite against glibc vfprintf; it still interns one string per line.

## Caveats and trade-offs

Cross-machine comparison: C and LuaJIT run in separate GitHub Actions jobs (bench-c, bench-lua) on separate shared runner VMs with no CPU model recorded. The C side is built at -O2, not -O3. The work is dominated by formatting libraries, not compiled user code. C calls glibc fprintf(f, "%ld %ld\n", ...), which parses the format string in vfprintf on every line. LuaJIT's trace recorder (recff_format in src/lj_ffrecord.c) specialises string.format to the constant '%d %d\n' and turns each plain %d into an integer-to-string conversion (lj_strfmt_wint in src/lj_strfmt.c), and f:write then calls fwrite. So the gap is LuaJIT's runtime formatter against glibc printf, not a code-generation win (inference from the sources; the suite states no mechanism). Rust is faster still at 4.17 ms (0.52x). This is the only one of 8 benchmarks that goes LuaJIT's way. It is slower than C on the other seven: recursion_fibonacci 5.20x, userfunc_mandelbrot 2.54x, matrix_statistics 2.29x, recursion_quicksort 2.24x, parse_integers 1.21x, matrix_multiply 1.14x, iteration_pi_sum 1.07x. Times are best-of-15 minimums in milliseconds. The suite is maintained by the Julia project and is first-party for Julia but third-party for LuaJIT. [retier] Enricher: .github/workflows/benchmarks.yml runs C (job bench-c) and LuaJIT (job bench-lua) on separate ubuntu-latest runner VMs with no CPU model recorded; the two sides use different timers (C gettimeofday, Lua clock_gettime CLOCK_MONOTONIC through the FFI) and slightly different inputs (C writes 0..99,999, Lua 1..100,000). The win is LuaJIT's specialised string.format (recff_format, asm_bufput fusing to lj_strfmt_putint) plus fwrite against glibc vfprintf; it still interns one string per line.

The win covers formatted integer output only; LuaJIT needs its runtime and the result excludes start-up.

## Maintenance

The suite is active (last commits 2026-04-21, CI-dependency bumps; methodology standardised in PR #112 on 2026-03-02), MIT-licensed, and LuaJIT itself is MIT and maintained in rolling 2.1 releases; this row is a directional data point about LuaJIT's formatter, not a reusable component.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The page shows C print_to_file at 8.02 ms (1.00x) and LuaJIT at 6.26 ms (0.78x), and the code (c/perf.c printfd, lua/perf.lua printfd), Makefile and versions are public. However, .github/workflows/benchmarks.yml runs C (job bench-c) and LuaJIT (job bench-lua) as separate jobs on separate ubuntu-latest runner VMs with no CPU model recorded, so the 1.28x is a cross-machine comparison (cross-run precedent: D). The C side is also built at -O2, not -O3.
- **Verifier notes:** Downgrade C to D. The numbers match the page, but the CI workflow measures C and LuaJIT on different runner VMs, which is a cross-machine comparison. The C baseline is -O2, and the win is LuaJIT's own runtime formatter (written in C) against glibc vfprintf, not a language-level codegen win. LuaJIT itself is already listed in wave 12 (https://github.com/luajit/luajit), so the orchestrator may treat this as a second claim on that project. MIT, 91 stars, active (last commit 2026-04-21).
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-55 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/benchmarks/index.html>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/notes/index.html>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/Makefile>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/c/perf.c>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/lua/perf.lua>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/README.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/LICENSE.md>
  - <https://github.com/JuliaLang/Microbenchmarks>
  - <https://github.com/JuliaLang/Microbenchmarks/commits/master>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lj_strfmt.c>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lib_io.c>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lj_ffrecord.c>
- **Sources the enricher read:**
  - <https://github.com/JuliaLang/Microbenchmarks>
  - <https://github.com/JuliaLang/Microbenchmarks/commits/master>
  - <https://github.com/JuliaLang/Microbenchmarks/issues?q=is%3Aissue+print_to_file+OR+printfd+OR+lua>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/README.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/Makefile>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/c/perf.c>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/lua/perf.lua>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/rust/src/main.rs>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/julia/perf.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/bin/table.jl>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/bin/versions.sh>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/.github/workflows/benchmarks.yml>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/master/LICENSE.md>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/benchmarks/index.html>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/benchmarks.csv>
  - <https://raw.githubusercontent.com/JuliaLang/Microbenchmarks/gh-pages/dev/notes/index.html>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/README>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/doc/install.html>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lj_ffrecord.c>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lj_asm.c>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lj_strfmt.c>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lib_io.c>
  - <https://raw.githubusercontent.com/LuaJIT/LuaJIT/v2.1/src/lj_arch.h>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:luajit/julialang/microbenchmarks#print-to-file`) · [data/wave14/enrich/raw/lang_luajit_julialang_microbenchmarks_print_to_file.json](../../../data/wave14/enrich/raw/lang_luajit_julialang_microbenchmarks_print_to_file.json) (enrichment confidence 0.7)

</details>
