# mexce

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Header-only C++11 JIT that compiles run-time math formula strings to x86/x86-64 code, roughly matching statically compiled C++.

| | |
|---|---|
| **Beats** | native compiler-generated C++ code for the same expressions (statically compiled) |
| **Claimed result** | README table on GitHub Actions CI (Ubuntu runner, 44,229 expressions): average evaluation 6.0 ns for the SSE2 backend versus 7.0 ns for natively compiled code; total evaluation 27.2 ms versus 32.7 ms (1.20x, derived from page data); SSE2 plus fast-math 6.0 ns and 26.8 ms (1.22x, derived from page data); x87 backend 8.0 ns and 34.8 ms, slower than native (0.94x, derived from page data); average compile time 174 us per expression for SSE2 and 135 us for x87. README: the SSE2 backend 'performs on par with or faster than native compiler-generated code'. |
| **Workload** | Compile and evaluate a suite of 44,229 scalar math expressions at run time (SSE2 and x87 backends), average evaluation time per expression and total evaluation time, versus the same expressions compiled natively. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions ubuntu runner (CPU model not stated) |
| **Compiler and flags** | Benchmark target built Release with -O3 -DNDEBUG (GCC and Clang) or /O2 (MSVC) per CMakeLists.txt; the README table does not say which compiler produced the numbers |
| **Adoption** | 6 stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/imakris/mexce) · [benchmark](https://raw.githubusercontent.com/imakris/mexce/HEAD/README.md) |

## Verdict

On a GitHub Actions ubuntu-latest runner (CPU not stated; at the table's commit the job ran CMake's default C++ compiler with no GCC/Clang split, and the harness took the median of 11 back-to-back trials of 100 evaluations), 44,229 expressions evaluated by mexce's SSE2 backend totalled 27.2 ms versus 32.7 ms for the same expressions compiled as static -O3 C++ functions called through a function-pointer table (1.20x, derived from page data); the x87 backend was 0.94x. The native corpus calls only sin, cos, tan, pow, abs, sqrt, exp and log, with no floor/ceil/round/trunc, so the verifier's roundsd-versus-libm concern cannot explain the gap.

## Use it when

- A formula arrives at run time (user input, config file, plotting or simulation parameters) and is evaluated thousands to millions of times, so the 135-177 us average compile cost is amortized.
- Scalar double arithmetic formulas on x86-64 Linux or Windows where you want code at about native speed without embedding LLVM or a C compiler.
- Projects that want one dependency-free header and only C++11.
- Long arithmetic chains where 80-bit intermediates help: the x87 backend had the most exact results in the README's ULP table (20,323 exact versus 16,636 for native code), at 0.94x native speed.

## Skip it when

- Any non-x86 target (ARM64, Apple Silicon, Graviton, RISC-V); the README lists only Windows and Linux on x86 and x86-64.
- Pre-SSE4.1 x86-64 CPUs: the SSE2 backend emits roundsd for floor/ceil/round/trunc/int with no CPUID check, so those expressions hit an illegal instruction.
- Formulas known at build time: plain C++ is as fast (1.20x on totals is the whole measured margin and the x87 backend is slower than native).
- Evaluating one formula over large arrays: there is no batch or SIMD API, and the project's own analysis measures 1.0-1.3 ns of fixed overhead per evaluate() call; a vectorising JIT fits better.
- Sandboxes or hardened processes that forbid making memory executable (mexce needs mmap plus mprotect(PROT_EXEC) or VirtualAlloc); also a single-author, 6-star project.

## How it is fast

The parser builds an element list, folds constant subtrees (by JIT-compiling and running them), runs peephole optimizers (asmd_optimizer for add/sub/mul/div chains, pow_optimizer for integer exponents) and then emits machine code directly. The default x86-64 backend keeps a virtual operand stack in XMM0-7 (XMM0-5 on Windows) using scalar SSE2 instructions, sqrtsd and SSE4.1 roundsd inline, caches variable addresses in RAX, folds variable loads into memory operands, and calls libm only for transcendentals; deeper expressions fall back to the x87 backend (80-bit stack, fsin/fcos/fptan, optional CSE). A fully constant expression is stored as a value and evaluate() returns it without calling code.

## Compared with alternatives

Pick mexce over RapidUDF when you need a dependency-free single header that JIT-compiles one scalar formula at a time on x86; RapidUDF's catalogued win comes from vectorised evaluation over arrays, which mexce does not offer. Use AsmJit or sljit when you are generating your own machine code rather than evaluating math strings, and dstogov/ir or TPDE when you need a compiler IR and back-end rather than a formula evaluator.

## Integration

| | |
|---|---|
| **Form** | header-only (mexce.h); the optional protected-expression mode is a CMake package target mexce::protected |
| **Dependencies** | none for the core; libsodium 1.0.22 only for protected expressions |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11); CI builds with GCC, Clang and MSVC (analysis/performance_acceptance.md names GCC 13.3.0, Clang 18.1.3, MSVC 19.44) |
| **Platforms** | x86-64 (SSE2 backend; SSE4.1 required when rounding functions are used) and 32-bit x86 (x87 backend); Windows and Linux |
| **Thread safety** | Not documented for evaluator objects. The built-in function and constant maps are static-local initialized so concurrent first use is safe (August 2026 fix); generated code reads bound variables by address, so treat an evaluator and its bound variables as single-threaded (inference from the code). |
| **Drop-in for the baseline** | no: it replaces ahead-of-time compiled C++ only when the formula is a run-time string, through its own bind / set_expression / evaluate API |

## Gotchas

- round(x) and int(x) round half to even in both backends (roundsd mode 0x08; frndint with control word 0x27F), so round(2.5) returns 2.0 where std::round returns 3.0, and int(x) is not truncation; the unit test only checks 3.75, so this is untested.
- SSE4.1 roundsd is emitted without a CPUID gate (B4 in analysis/improvement_report.md); current mexce.h still has no CPUID check, and the README requirements do not mention SSE4.1.
- Harness asymmetries behind the README's 1.20x: evaluate() returns a stored value for fully constant expressions without calling any code (1,270 of the 44,229 corpus expressions are constant) and the timed loop discards the result, while the native side still makes an indirect call each iteration; and at the table's commit (cb358747, 2026-01-11) default mode still applied x-x to 0, x/x to 1 and merged cancellations such as 3x-2x (B5, fixed 2026-06-10), work that strict -O3 native code must do. By the analysis's own 1.0-1.3 ns per-call overhead the constant shortcut is worth roughly 0.13-0.17 ms of the 5.5 ms gap (estimate), so these skew rather than create the result.
- Bound variables are captured by address and must outlive the evaluator; unbinding a variable the current expression uses silently resets it to the constant 0, and code from before 2026-06-10 also has the B1 miscompile (a binary libm call at stack depth 3 got (arg2, arg2): logb(a, b + logb(2,x)) returned 2.321928 instead of 2.807355).

## Known shortcomings

- First-party README table (SSE2 27.2 ms vs native 32.7 ms, 1.20x derived) from commit cb358747 (2026-01-11), predating the B1 SSE2 libm-call miscompilation fix; compiler and CPU unstated; the native baseline was built without -msse4.1 while mexce emits roundsd with no CPUID gate; the x87 path is slower than native; no comparison with other expression JITs. 6 stars.
- Enricher: evaluate() returns the stored value for constant expressions without a call (1,270 of 44,229 expressions) while the native side still pays an indirect call; the README table also predates the B5 fix (strict-mode x-x and x/x folding, 2026-06-10); the native corpus has no floor/ceil/round/trunc, so the roundsd-vs-libm concern does not explain the gap. round()/int() are round-half-to-even (round(2.5)=2 vs std::round 3), untested; B4 roundsd without CPUID still open.

## Caveats and trade-offs

First-party numbers from a GitHub Actions ubuntu-latest runner with no CPU model; the CI matrix builds the benchmark with both GCC and Clang (-O3 -DNDEBUG) and the README does not say which produced the table. The table was written in commit cb358747 (2026-01-11, 'Add SSE2 scalar backend') and has not been re-measured since; the repository's own analysis/improvement_report.md (2026-06-10, a 35-agent analysis run) later found master bugs including B1, a miscompilation in emit_sse2_libm_binary_call where a binary libm call at virtual-stack depth 3 received (arg2, arg2) (logb(a, b + logb(2,x)) returned 2.321928 instead of 2.807355), B2 (the documented '&gt;' operator threw at parse time), B3 (one leaked executable page per constant fold) and B4 (SSE4.1 roundsd emitted with no CPUID gate, so it crashes on pre-SSE4.1 CPUs); current mexce.h has the corrected B1 register move but still no CPUID check for roundsd. The averages are whole nanoseconds (6 versus 7 ns is a one-count difference), so the total-eval ratio of 1.20x is the more precise figure. Fairness: the native baseline is one static function per expression called through a function-pointer table and built with -O3 but no -march, -msse4.1 or -fno-math-errno flag, so the compiler cannot emit roundsd for floor/ceil/round/trunc while mexce does; part of the win may come from that ISA difference. The run_benchmarks target uses 100 iterations per expression with a median of 7 round-robin rounds. There is no comparison with other expression evaluators or JITs (exprtk, muparser, tinyexpr, asmjit-based evaluators), so the claim is parity with native code, not a win over a competitor. analysis/asmd_optimizer_benchmark_summary.csv (an earlier stage) lists avg_runtime_ns 11 to 12 against compiler_runtime_ns 10 to 11, i.e. slower than native then. analysis/performance_acceptance.md (GCC 13.3.0, Clang 18.1.3, MSVC 19.44) reports evaluate medians of 6.5 to 7.6 ns but compares only mexce commits against each other, not against native code. 6 stars, single author.

x86 and x86-64 only; the SSE2 backend calls libm for transcendentals, the x87 backend uses 80-bit internal precision with more exact results; runtime compile cost of 135 to 177 microseconds per expression; executable memory (mmap or VirtualAlloc) required; fast-math option changes NaN and Inf semantics; optional protected-expression mode needs libsodium.

## Maintenance

Active (last commit 2026-09-24, 253 commits, 0 issues filed), BSD-2-Clause single header that is easy to vendor, but single-author with 6 stars; the README table is from January 2026 code and an older harness, measured before the June 2026 fixes for B1 (miscompile), B2 (rejected '&gt;'), B3 (page leak) and B5 (strict-mode algebra), with harness asymmetries (constant-expression shortcut, strict-mode simplifications) favouring mexce and B4 (no CPUID gate for roundsd) still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance Analysis table (Native 7.0 ns / 32.7 ms, SSE2 6.0 ns / 27.2 ms, SSE2 + fast-math 6.0 ns / 26.8 ms, x87 8.0 ns / 34.8 ms) comes from the public harness test/benchmark.cpp (native baseline in test/benchmark_native_expressions.h, -O3 -DNDEBUG per CMakeLists.txt), but it names neither the compiler (the CI matrix runs both GCC and Clang on ubuntu-latest) nor the runner's CPU model, so it is first-party with partial methodology. The table was added in commit cb358747 (2026-01-11) and is unchanged since, so it predates the 2026-06-10 report of the B1 SSE2 libm-call miscompilation that was later fixed, which also caps it at C.
- **Verifier notes:** Numbers match the README exactly and the harness is real (JIT code called through a function pointer, results checked against a SymPy reference, no no-op timing), so confirm at C. Shortcomings to record: compiler and CPU unstated; table measured on January 2026 code that predates the B1 SSE2 libm-call miscompilation fix; native baseline built without -msse4.1 while mexce emits roundsd with no CPUID gate; parity-level gain (1.20x on totals, x87 slower than native); no comparison with other expression JITs.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/README.md>
  - <https://github.com/imakris/mexce>
  - <https://github.com/imakris/mexce/commits>
  - <https://github.com/imakris/mexce/commits/master/README.md>
  - <https://raw.githubusercontent.com/imakris/mexce/cb358747119cdaa32b54add7cdb5b81269252026/README.md>
  - <https://raw.githubusercontent.com/imakris/mexce/cb358747119cdaa32b54add7cdb5b81269252026/test/benchmark.cpp>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/.github/workflows/main.yml>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/test/benchmark.cpp>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/test/benchmark_native_expressions.h>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/mexce.h>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/analysis/improvement_report.md>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/analysis/performance_acceptance.md>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/analysis/asmd_optimizer_benchmark_summary.csv>
- **Sources the enricher read:**
  - <https://github.com/imakris/mexce>
  - <https://github.com/imakris/mexce/commits>
  - <https://github.com/imakris/mexce/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/README.md>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/mexce.h>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/test/benchmark.cpp>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/test/benchmark_native_expressions.h>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/test/benchmark_native_expressions.inc>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/test/unit_tests.cpp>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/analysis/improvement_report.md>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/analysis/performance_acceptance.md>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/.github/workflows/main.yml>
  - <https://raw.githubusercontent.com/imakris/mexce/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/imakris/mexce/cb358747119cdaa32b54add7cdb5b81269252026/test/benchmark.cpp>
  - <https://raw.githubusercontent.com/imakris/mexce/cb358747119cdaa32b54add7cdb5b81269252026/CMakeLists.txt>
  - <https://raw.githubusercontent.com/imakris/mexce/cb358747119cdaa32b54add7cdb5b81269252026/.github/workflows/main.yml>
  - <https://raw.githubusercontent.com/imakris/mexce/cb358747119cdaa32b54add7cdb5b81269252026/mexce.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/imakris/mexce`) · [data/wave1/enrich/raw/github_com_imakris_mexce.json](../../../data/wave1/enrich/raw/github_com_imakris_mexce.json) (enrichment confidence 0.6)

</details>
