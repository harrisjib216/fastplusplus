# muParser

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-2-Clause` · 🟢 active

> Runtime math-expression parser that compiles to a bytecode stack machine; beats TinyExpr, Lepton and muParserX, not ExprTk.

| | |
|---|---|
| **Beats** | TinyExpr (also muParserX, Lepton, MTParser, MathExpr; it loses to ExprTk, METL and FParser in the same suite) |
| **Claimed result** | README per-expression example '(a^2/sin(2\*pi/b))-a/2': muparser 2.2.4 47.358 ns, TinyExpr 121.184 ns, Lepton 297.673 ns, muparserx 498.809 ns (muparser about 2.6x faster than TinyExpr, derived from page data); but in the README's second example '+a^+b+1.1' TinyExpr 53.620 ns beats muparser 66.387 ns. README example summary (bench_expr.txt): muparser 2.2.4 517 points (score 37), TinyExpr 354 (31), MTParser 381 (34), MathExpr 360 (29), Lepton 134 (8), muparserx 86 (5), versus FParser 4.5 584 (43), atmsp 530 (38), METL 686 (52) and ExprTk 901 (100). Committed 2018 log (logs/shootout_20180421_00.zip, Shootout_20180420_182359.txt, bench_expr.txt): muparser 523 points (score 38), TinyExpr 360 (32), MTParser 383 (34), MathExpr 364 (30), Lepton 136 (8), muparserx 85 (5). Score is the mean of per-expression (ExprTk time / parser time) x 100, so muparser averages about 1.2x TinyExpr's per-expression speed on bench_expr.txt (38/32, derived from page data); on the larger 2018 suites the gap is wider: bench_expr_complete.txt 28 versus 15 (about 1.9x), bench_expr_extensive.txt 24 versus 12 (about 2.0x), bench_expr_random_without_functions.txt 28 versus 13 (about 2.2x), but on bench_expr_weird.txt TinyExpr wins (508 points, score 46, versus muparser 394, score 35). |
| **Workload** | Evaluate pre-parsed expressions (parse once, evaluate many times) with variables a, b, c, x, y, z, w in the third-party math-parser-benchmark-project; 74 expressions from bench_expr.txt, each evaluated 5,000,000 times, ranked per expression and points summed. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2687W 0 @ 3.10GHz, 8 cores / 16 logical, L3 20480 KB, 3092 MHz |
| **Compiler and flags** | MSVC Version 1913 (Visual Studio 2017, toolset v141), Release\|Win32 (32-bit) per math-parser-benchmark-project/math-parser-benchmark-project_msvc2017.vcxproj: Optimization MaxSpeed (/O2), InlineFunctionExpansion AnySuitable, IntrinsicFunctions, FavorSizeOrSpeed Speed, WholeProgramOptimization, FloatingPointModel Precise, NDEBUG, _SECURE_SCL=0 (flags read from the current HEAD project file; the result logs print only compiler version and build type). The repo's math-parser-benchmark-project.pro builds with g++ -std=c++11 -march=native -fopenmp and -O3, with HAVE_STDINT_H and MUP_USE_OPENMP defined. |
| **Adoption** | 532 stars |
| **Last commit** | 2026-07-03 |
| **Links** | [repository](https://github.com/beltoforion/muparser) · [benchmark](https://github.com/ArashPartow/math-parser-benchmark-project) |

## Verdict

In ArashPartow's math-parser-benchmark-project (written by ExprTk's author), a bundled muparser 2.2.x evaluating 74 pre-parsed double expressions 5,000,000 times each, built with MSVC 1913 Release Win32 on a Xeon E5-2687W in 2018, scored 38 against TinyExpr's 32 on bench_expr.txt (about 1.2x on average, derived from page data) and about 1.9x to 2.2x on the larger suites, while ExprTk set the 100 reference and TinyExpr won the 'weird' suite. The README's headline expression shows 47.4 ns versus TinyExpr's 121.2 ns, but that is one favourable case.

## Use it when

- User-supplied formulas (spreadsheet cells, config-driven transforms, plotting tools) that are parsed once and evaluated millions of times on double variables
- You currently embed TinyExpr, Lepton or muParserX and evaluation time matters: the third-party shootout ranks muparser ahead of all three on its main and larger expression files
- You want a compiled BSD-2-Clause library with a plain C interface (muParserDLL) rather than a very large header
- Evaluating one expression over large arrays of inputs, where the bulk Eval(results, n) overload avoids per-call overhead

## Skip it when

- Peak evaluation speed is the goal: ExprTk, METL and FParser beat it on every 2018 suite of the same shootout, and atmsp edges it on bench_expr.txt
- Short or oddly written expressions: TinyExpr beats it on bench_expr_weird.txt (508 versus 394 points) and on single expressions such as '+a^+b+1.1'
- Expressions are evaluated only a few times each: the first Eval() includes parsing and bytecode generation, and issue #131 reports 5 to 25 ms on ESP32 to clear and redefine variables on a shared parser
- You need types other than double/float, vectors or strings as first-class values (its sibling muParserX covers those, at a large speed cost)
- Untrusted input on versions before 2.3.3/2.3.6: oss-fuzz found heap-buffer-overflow reads and access violations on malformed expressions, fixed in 2.3.2, 2.3.3 and 2.3.6

## How it is fast

The first Eval() parses the string with a shunting-yard pass into reverse-Polish bytecode and swaps an internal function pointer so later calls run only a switch-dispatched stack interpreter (ParseCmdCodeBulk). The bytecode optimizer folds constant subexpressions and fuses common patterns into single opcodes (a\*a and a^2..a^4 into VARPOW2/3/4, 2\*(3\*b+1) into one multiply-add VARMUL), and single-token expressions take a short path. Bulk mode splits the array over up to 16 OpenMP threads, each with its own slice of the value stack.

## Compared with alternatives

ExprTk is the only catalogued sibling that is an expression parser and it is faster in every suite of the shootout, so pick muparser only when you prefer its smaller compiled library, C interface, BSD-2-Clause licence or bulk array API over raw evaluation speed; the other siblings (xsimd, SLEEF, fmath and similar) are math kernels, not parsers.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake; BUILD_SHARED_LIBS defaults ON); a handful of .cpp/.h files can also be source-dropped |
| **Dependencies** | none required; OpenMP optional (CMake option ENABLE_OPENMP defaults ON) |
| **Minimum toolchain** | C++17 source per the 2.3.2 changelog; the current CMakeLists sets CMAKE_CXX_STANDARD 20 and needs CMake 3.15+ |
| **Platforms** | any platform with a C++17 compiler; changelog covers MSVC (incl. C++20), MinGW, GCC, Clang, IntelLLVM; optional wide-character build (ENABLE_WIDE_CHAR) |
| **Thread safety** | Not documented. Each Parser keeps mutable state (stack buffer, the parse-function pointer swapped on first Eval), so use one Parser per thread; issue #106 reports a segfault running parsers under OpenMP with no documented answer. The built-in rnd() uses a function-static std::mt19937 shared by all parsers, which is a data race under concurrent evaluation. |
| **Drop-in for the baseline** | partial: same parse-once, evaluate-many pattern as TinyExpr's te_compile/te_eval with pointer-bound variables, but a different C++ class API and grammar |

## Gotchas

- The shootout numbers come from a bundled copy whose header says MUP_VERSION 2.2.5 (the harness labels it 2.2.4), built with MUP_ASSERT compiled out under NDEBUG; since 2.3.2 MUP_ASSERT stays active in release builds and runs bounds checks on every stack operation of the interpreter loop, so current 2.3.6 may be slower than the 2018 results show.
- The 'omp' bulk variant was slower than plain muparser in every logged run (for example 53.252 versus 47.358 ns on the README's first expression), and the benchmark bulk path allocates nine arrays of 5,000,000 doubles; do not assume OpenMP helps.
- Issue #68 reported 36478.8 ns for '((cos(cos(tan(pi)))+a)/a)' with muparser 2.2.4 built by GCC 7+ or Clang 6, against 8 ns for ExprTk on the same machine; it was closed under the 2.3.0 milestone without a documented root cause.
- Behaviour changes across versions: since 2.3.2 math exceptions (divide by zero, sqrt of a negative) no longer throw, expressions are capped (now 20000 characters) and identifiers at 100 characters; 2.3.5 changed bitwise 'and' precedence and 2.3.6 rejects unary plus before functions.

## Known shortcomings

- ArashPartow math-parser-benchmark-project (2018, muparser 2.2.4, MSVC flags from vcxproj, Xeon E5-2687W): mid-pack, 7th by points; loses to ExprTk, METL, FParser and atmsp, and TinyExpr wins on bench_expr_weird.txt; the 2.6x is one expression, the suite average over TinyExpr is about 1.2x-2.2x.
- Enricher: the bundled benchmark header says MUP_VERSION 2.2.5 (labelled 2.2.4) with MUP_ASSERT compiled out, while since 2.3.2 release builds keep MUP_ASSERT bounds checks in the interpreter loop, so the 2018 numbers are likely optimistic for 2.3.6; issue #68 (36478.8 ns vs ExprTk 8 ns on GCC 7+/Clang 6) closed without a root cause; rnd() shares a static mt19937 (data race), thread safety undocumented (#106 segfault).

## Caveats and trade-offs

Mixed result: muparser 2.2.4 is 7th of 13 entries by points on bench_expr.txt (behind ExprTk, ExprTkFloat, muparserSSE, METL, FParser and atmsp) and loses to ExprTk, METL and FParser on every 2018 suite, so 'faster' holds only against TinyExpr, MTParser, MathExpr, Lepton and its heavier sibling muParserX; even TinyExpr beats it on bench_expr_weird.txt and on some single expressions. The suite is maintained by ExprTk's author, a competitor, and bundles muparser 2.2.4 (the README says the archive 'may contain outdated versions'); current muparser is 2.3.6 (released 2026-04-10) with many later bug fixes, so the 2018 numbers may not apply to it. The 'omp' variant is slower than plain muparser in every log read. Logged results are Windows 32-bit MSVC only, from 2018; the README summary is labelled an example. The harness pre-evaluates once to build bytecode outside the timed loop and swaps variables each iteration, and disqualifies wrong results per expression (muparser had 0 failures). The project's own site (beltoforion.de) was not read. Licence note: the benchmark README lists muParser as MIT; the repo LICENSE read today is BSD-2-Clause.

Bytecode interpreter over a parsed expression (parse once, evaluate many), not a JIT or compiler; mutable variable bindings, user callbacks and optional OpenMP over expression arrays. The muparser repo has no benchmark of its own; the README only says 'fast math parser library'.

## Maintenance

Actively maintained (2.3.6 released 2026-04-10, last commit 2026-07-03, fuzzed by oss-fuzz) and BSD-2-Clause, so easy to adopt; the only third-party speed data is eight years old, on an older version without the release-mode bounds checks the current code carries.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public benchmark code (src/BenchMuParser2.cpp, src/BenchTinyExpr.cpp, src/ParserBench.cpp in ArashPartow/math-parser-benchmark-project), compiler MSVC 1913 with Release flags in math-parser-benchmark-project/math-parser-benchmark-project_msvc2017.vcxproj, and CPU model Intel Xeon E5-2687W in the logs; the suite is third-party to muparser, so A (consistent with the ExprTk entry from the same suite).
- **Verifier notes:** Numbers match the suite README and the committed 2018 log; corrected the rank (7th, not 6th, by points) and added that TinyExpr wins on bench_expr_weird.txt and on the README's '+a^+b+1.1' example, so the 2.6x headline is one favourable expression and the suite-average gain over TinyExpr is about 1.2x to 2.2x depending on the file. Metadata checks out (BSD-2-Clause, 532 stars, 142 forks, last commit 2026-07-03, active, release 2.3.6). Shortcoming to record: mid-pack in its own shootout, slower than ExprTk, METL, FParser and atmsp; numbers are on muparser 2.2.4 from 2018, 32-bit MSVC.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** math-parser-benchmark-project (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/ArashPartow/math-parser-benchmark-project>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/readme.md>
  - <https://github.com/ArashPartow/math-parser-benchmark-project/tree/master/logs>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/logs/shootout_20180421_00.zip>
  - <https://github.com/ArashPartow/math-parser-benchmark-project/tree/master/src>
  - <https://github.com/ArashPartow/math-parser-benchmark-project/tree/master>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/math-parser-benchmark-project_msvc2017.sln>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/math-parser-benchmark-project/math-parser-benchmark-project_msvc2017.vcxproj>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/math-parser-benchmark-project.pro>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/BenchMuParser2.cpp>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/BenchTinyExpr.cpp>
  - <https://github.com/beltoforion/muparser>
  - <https://github.com/beltoforion/muparser/commits>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/beltoforion/muparser>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/README.md>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/CHANGELOG>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/include/muParserDef.h>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/include/muParserBase.h>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/include/muParserBytecode.h>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/include/muParserTemplateMagic.h>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/include/muParserCallback.h>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/src/muParserBase.cpp>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/src/muParserBytecode.cpp>
  - <https://raw.githubusercontent.com/beltoforion/muparser/HEAD/src/muParser.cpp>
  - <https://github.com/beltoforion/muparser/issues?q=is%3Aissue+performance+OR+slow+OR+thread>
  - <https://github.com/beltoforion/muparser/issues/68>
  - <https://github.com/beltoforion/muparser/issues/106>
  - <https://github.com/beltoforion/muparser/issues/131>
  - https://beltoforion.de/en/muparser/ (EGRESS_BLOCKED)
  - <https://github.com/ArashPartow/math-parser-benchmark-project>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/readme.md>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/BenchMuParser2.cpp>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/BenchTinyExpr.cpp>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/Benchmark.cpp>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/src/ParserBench.cpp>
  - <https://raw.githubusercontent.com/ArashPartow/math-parser-benchmark-project/HEAD/muparser2/muParserDef.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/beltoforion/muparser`) · [data/wave1/enrich/raw/github_com_beltoforion_muparser.json](../../../data/wave1/enrich/raw/github_com_beltoforion_muparser.json) (enrichment confidence 0.65)

</details>
