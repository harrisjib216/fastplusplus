# ExprTk

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only C++ runtime expression parser/evaluator; evaluates pre-compiled expressions about 2-4x faster than muparser 2.2.4.

| | |
|---|---|
| **Beats** | muParser 2.2.4 (also FParser 4.5, TinyExpr, ATMSP, METL, MathExpr, MTParser, Lepton, muparserx) |
| **Claimed result** | README example summary (bench_expr.txt, 74 expressions, 5,000,000 iterations each): ExprTk (double) 901 points, score 100; muparser 2.2.4 517 points, score 37; FParser 4.5 584 points, score 43; TinyExpr 354 points, score 31; atmsp 1.0.4 530 points, score 38. Per-expression example: ExprTk 39.963 ns versus muparser 2.2.4 47.358 ns on '(a^2/sin(2\*pi/b))-a/2' (about 1.18x, derived from page data). Score is the mean over expressions of (ExprTk time / parser time) x 100 per src/ParserBench.cpp, so score 100 versus 37 means muparser runs on average at 37% of ExprTk's per-expression speed, about 2.7x (derived from page data); the README itself only says the reference parser is ExprTk. |
| **Workload** | Evaluate pre-parsed expressions (parse once, evaluate many times) with variables a, b, c, x, y, z, w; each of 74 expressions in bench_expr.txt evaluated 5,000,000 times, ranked per expression, points summed. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2687W 0 @ 3.10GHz, 8 cores / 16 logical, L3 20480 KB |
| **Compiler and flags** | MSVC 1913 (Visual Studio 2017, toolset v141), Release\|Win32 (32-bit) per math-parser-benchmark-project_msvc2017.vcxproj: Optimization MaxSpeed (/O2), InlineFunctionExpansion AnySuitable, IntrinsicFunctions, FavorSizeOrSpeed Speed, WholeProgramOptimization, FloatingPointModel Precise, NDEBUG, _SECURE_SCL=0 (flags are not printed in the results log; the vcxproj read is the current HEAD). The repo .pro file builds with g++ -std=c++11 -march=native -fopenmp -O3. |
| **Adoption** | 1.0k stars |
| **Last commit** | 2025-01-01 |
| **Links** | [repository](https://github.com/ArashPartow/exprtk) · [benchmark](https://github.com/ArashPartow/math-parser-benchmark-project) |

## Verdict

In the author's math-parser-benchmark-project (32-bit MSVC 1913 Release, Intel Xeon E5-2687W @ 3.10 GHz, 2018 logs), pre-compiled ExprTk evaluated the 74 bench_expr.txt expressions 5,000,000 times each with a mean muparser-to-ExprTk speed ratio of 0.37-0.38 (about 2.7x) and a median per-expression slowdown for muparser 2.2.4 of 3.4x; across the eight 2018 suites muparser 2.2.4 scored 24-62 and the best double-precision rival (METL or FParser) 39-78 against ExprTk's 100.

## Use it when

- Parse-once, evaluate-many workloads: user-entered formulas, config-driven transforms, spreadsheet-like columns, simulation parameters evaluated millions of times
- You need double (or float, long double, MPFR) precision with results that match native C++ arithmetic closely; precision is the library's stated first priority
- Expressions need more than arithmetic: conditionals, loops, string predicates, vectors, or calls back into C++ functions
- Portable builds on any compiler down to C++98 (the header reports min_cpp 199711L) without third-party dependencies or a JIT

## Skip it when

- Compile time or binary size is tight: exprtk.hpp is about 46,800 lines (1.66 MB) of templates; the exprtk_disable_enhanced_features define cuts both but the readme warns it causes massive evaluation slowdowns
- You compile expressions on a hot path: the readme says parser/symbol_table/expression construction and compilation are high-latency and must stay outside performance-critical code
- You need peak throughput and can accept float or a JIT: the AsmJit-based muparserSSE (float) out-scored ExprTk in 5 of 8 2018 shootout runs and was faster on 5,580 of the 6,198 bench_expr_complete expressions it passed (derived from page data)
- Function-call-heavy expressions where libm dominates: on bench_expr_random_with_functions the median gap shrinks to 1.2x over METL/FParser and 1.5x over muparser 2.2.4
- You need a bug tracker: the GitHub repo is a mirror with no Issues tab and pull requests are closed rather than merged; support goes through the author's website

## How it is fast

It is a tree-walking interpreter, not a JIT and not SIMD: the gain comes from compile-time work. The parser does constant folding, strength reduction and dead-code elimination, rewrites integer powers into multiplication chains (cardinal pow optimisation), and synthesises operand-type-specialised node templates (vov/voc/cov nodes and fused T0oT1oT2 / T0oT1oT2oT3 three- and four-operand nodes with variable or constant slots baked in as template parameters), so common shapes like 'a\*x+b' become one virtual call instead of a small subtree. Vector operations use an 8-way (or 4-way) manually unrolled loop.

## Compared with alternatives

None of the catalogued siblings (SLEEF, VDT, fmath, xsimd, NumKong) evaluate run-time expression strings; they speed up fixed compiled math kernels. Pick ExprTk when the formula is only known at run time; if it is known at compile time, write it in C++ and use SLEEF or fmath for the transcendental calls instead.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (MPFR/GMP only if you instantiate it with an MPFR type) |
| **Minimum toolchain** | C++98 (header declares min_cpp 199711L); readme lists GCC 3.5+, Clang 1.1+, MSVC 7.1+, Intel 8+, plus AMD, Nvidia, PGI, IBM XL, C++ Builder |
| **Platforms** | any (portable C++; no architecture-specific code paths) |
| **Thread safety** | exprtk::parser is documented as non-thread-safe and non-copyable; compiled expressions hold references to symbol-table variables, so concurrent evaluation needs per-thread expression and variable instances (expressions must be recompiled from strings rather than copied); rebase of vector views during evaluation is undefined behaviour |
| **Drop-in for the baseline** | partial — same parse-once/evaluate-many model as muparser and binds C++ variables by pointer/reference, but a different API (symbol_table + parser.compile + expression.value) and a superset grammar; existing muparser call sites must be rewritten |

## Gotchas

- Structural bias in the cited shootout: ExprTk is hard-wired as the reference parser in src/ParserBench.cpp, so a rival whose result differs from ExprTk's is disqualified and scores 0 for that expression while ExprTk can never fail on accuracy, and the reference gets an extra untimed full pass before its ranked run. Re-counting the 2018 logs, this barely touched double-precision rivals (muparser 2.2.4 and METL 0 result mismatches, FParser at most 1; FParser's 67 losses on bench_expr_weird are parse errors); the mismatches fall on float builds, ExprTk's own ExprTkFloat about as often as muparserSSE.
- The record's '1.18x on a single expression' understates the typical gap: re-parsing the committed 2018 bench_expr.txt log, muparser 2.2.4 is a median 3.4x slower per expression (range 1.05x to 15.8x, derived from page data); METL is a median 2.2x slower and wins 5 of 74 expressions
- All published runs are 32-bit MSVC 2017 builds from 2018 against bundled 2013-2014 era rival versions (muparser 2.2.4, FParser 4.5); there are no 64-bit, GCC/Clang or current-muparser results
- Object lifetimes are on you: variables, vectors, strings and functions registered in a symbol_table must outlive every compiled expression that references them, otherwise behaviour is undefined; compile() returns bool and errors must be checked via parser.error()

## Known shortcomings

- First-party suite (src/ParserBench.cpp, MSVC 1913, msvc2017.vcxproj flags, Xeon E5-2687W): the score is a mean of time ratios, so the \~2.7x over muparser is inflated by constant-folded expressions and the per-expression win can be \~1.18x; muparserSSE out-scored ExprTk in 5 of 8 2018 logs; bundled baselines are old (muparser 2.2.4). Last commit 2025-01-01.
- Enricher: src/ParserBench.cpp hard-wires ExprTk as the correctness reference, so rivals that disagree with it are disqualified while ExprTk never can be, and ExprTk gets an extra untimed pass (in the 2018 logs the disqualifications hit float builds, including ExprTkFloat; double rivals barely affected). Recount of the logs: the per-expression median is 3.4x vs muparser 2.2.4 on bench_expr.txt (range 1.05-15.8x), 1.5x on random_with_functions and 4.1x on bench_expr_complete, while the best double rival (METL/FParser) is 1.2-2.5x; muparserSSE (AsmJit JIT, float) won bench_expr_complete on points. Published runs are 32-bit MSVC only and stop in 2018.

## Caveats and trade-offs

The shootout suite is maintained by ExprTk's own author, so it is first-party even though code, compiler, flags and CPU are public. Score is the arithmetic mean of per-expression time ratios against ExprTk (failed rounds count 0), so it is inflated by expressions ExprTk constant-folds or special-cases; single-expression gaps are much smaller (1.18x over muparser on the README example). The README summary is labelled an example and does not match the committed 2018 bench_expr.txt log (logs/shootout_20180421_00.zip, Shootout_20180420_182359.txt: ExprTk 885 points score 100, muparser 2.2.4 523 points score 38, FParser 4.5 score 43). In the same zip's bench_expr_complete.txt run (6617 expressions, 100000 iterations) ExprTk scores 100 versus muparser 2.2.4 score 28, FParser 4.5 32, TinyExpr 15, METL 42. muparserSSE (float, AsmJit JIT) out-scored ExprTk (double) on 5 of the 8 2018 logs (score 110 to 168) and won on points in bench_expr_complete (78987 versus 77945); it ranks lower elsewhere mainly because its float results fail the precision check. Several rival parsers are old versions bundled in the repo ('may contain outdated versions'; muparser 2.2.4 predates the 2.3 series), and the published runs are 32-bit MSVC only. Last-commit date is the year-stamped commit date from the GitHub commit feed (2025-01-01 is how the author dates commits). [retier] First-party suite (src/ParserBench.cpp, 32-bit MSVC 1913 runs only, logs stop in 2018): the score is a mean of time ratios inflated by constant-folded expressions; recounting the 2018 logs gives a per-expression median of 3.4x vs muparser 2.2.4 on bench_expr.txt (range 1.05-15.8x), 1.5x on random_with_functions and 4.1x on bench_expr_complete, with the best double rival (METL/FParser) at 1.2-2.5x. The harness hard-wires ExprTk as the correctness reference, so rivals that disagree are disqualified while ExprTk never can be, and ExprTk gets an extra untimed pass (double rivals barely affected; float builds, ExprTkFloat included, lose rows). muparserSSE (AsmJit JIT, float) won bench_expr_complete on points and was faster on 5,580 of the 6,198 expressions it passed. Bundled baselines are old (muparser 2.2.4). Last commit 2025-01-01.

Header-only (very large single header, long compile times), runtime parse into an expression tree with optional constant folding; supports scalars, vectors, strings, loops and user functions. Heavy template use hits compile time and binary size.

## Maintenance

The GitHub repo is a mirror of the author's site (header dated 20250101, last mirror commit 2025-01-01, PRs closed through 2026-07) and the benchmark logs stop in 2018, but the library is MIT, dependency-free, fuzzed on OSS-Fuzz per the readme, and copyable as a single header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Benchmark code is public (src/ParserBench.cpp plus src/Bench\*.cpp in ArashPartow/math-parser-benchmark-project); the README summary and the committed logs print the compiler (MSVC 1913, 32-bit Release) and CPU (Intel Xeon E5-2687W 0 @ 3.10GHz), and the Release|Win32 flags are in the public math-parser-benchmark-project/math-parser-benchmark-project_msvc2017.vcxproj. First-party (ExprTk's author maintains the suite), but A does not depend on who ran it.
- **Verifier notes:** Numbers on the README match the record; tier A holds because code, compiler, public vcxproj flags and CPU are all available. Shortcomings to record: first-party suite, score metric is a mean of time ratios inflated by constant-folded expressions (per-expression win over muparser can be only about 1.2x), muparserSSE beats ExprTk on score in most 2018 logs, bundled baselines are old versions, 32-bit MSVC only, repo stale (last commit 2025-01-01).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party ParserBench (verifier); enricher harness recount
- **Pages the verifier opened:**
  - <https://github.com/ArashPartow/math-parser-benchmark-project>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/readme.md>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/math-parser-benchmark-project.pro>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/ParserBench.cpp>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/bench_expr.txt>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/math-parser-benchmark-project_msvc2017.sln>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/math-parser-benchmark-project/math-parser-benchmark-project_msvc2017.vcxproj>
  - <https://github.com/ArashPartow/math-parser-benchmark-project/tree/master/logs>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/logs/shootout_20180421_00.zip>
  - <https://github.com/ArashPartow/exprtk>
  - <https://raw.githubusercontent.com/ArashPartow/exprtk/HEAD/readme.txt>
  - <https://raw.githubusercontent.com/ArashPartow/exprtk/HEAD/license.txt>
  - <https://github.com/ArashPartow/exprtk/commits/master.atom>
- **Sources the enricher read:**
  - <https://github.com/ArashPartow/exprtk>
  - <https://raw.githubusercontent.com/ArashPartow/exprtk/HEAD/readme.txt>
  - <https://raw.githubusercontent.com/ArashPartow/exprtk/HEAD/license.txt>
  - <https://raw.githubusercontent.com/ArashPartow/exprtk/HEAD/exprtk.hpp>
  - <https://github.com/ArashPartow/exprtk/issues?q=is%3Aissue>
  - <https://github.com/ArashPartow/exprtk/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/readme.md>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/bench_expr.txt>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/ParserBench.cpp>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/Benchmark.cpp>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/BenchExprTk.cpp>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/BenchMuParser2.cpp>
  - <https://github.com/ArashPartow/math-parser-benchmark-project/tree/master/logs>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/logs/shootout_20180421_00.zip>
  - <https://github.com/beltoforion/muparsersse>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/arashpartow/exprtk`) · [data/wave1/enrich/raw/github_com_arashpartow_exprtk.json](../../../data/wave1/enrich/raw/github_com_arashpartow_exprtk.json) (enrichment confidence 0.7)

</details>
