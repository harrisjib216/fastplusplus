# SymbolicUtils.jl / Symbolics.jl (Julia symbolic engine) vs SymEngine (C++): SciMLBenchmarks SymEngineComparison

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Julia` · `MIT` · 🟢 active

> Pure-Julia symbolic term-rewriting engine (core of Symbolics.jl). It beats SymEngine (C++) only on IR-cached search and substitution and on JIT-compiled evaluation.

| | |
|---|---|
| **Beats** | SymEngine v0.12.0 (C++ symbolic library, via SymEngine.jl v0.13.2 and SymEngine_jll) |
| **Claimed result** | Summary table (SymEngine s vs SymbolicUtils s; the SymbolicUtils column is the faster of two variants): SymbolicUtils faster in 4 of 10 rows: compiled call with CSE 6.93256e-7 vs 3.13135e-7 (2.2x), variable search on dissimilar expressions 4.67036e-4 vs 2.13078e-4 (2.2x), variable search on common subtrees 1.02663e-3 vs 4.89876e-4 (2.1x), sparse-rule substitution 1.10077e-3 vs 5.92595e-4 (1.9x). The per-variant tables show the plain variants: search_variables! without IRStructure is slower than SymEngine (1.37841e-3 vs 1.02663e-3 common, 5.97345e-4 vs 4.67036e-4 dissimilar), and the plain Substituter wins the sparse rule by only 1.28x (8.61063e-4 vs 1.10077e-3) on a 2810-node tree against SymEngine's 3271-node tree. The compiled call without CSE is 1.0665e-5 vs 2.559e-6 (4.2x). SymEngine faster in the other 6 rows: diff of expand 6.95691e-3 vs 0.332787 (48x), eval_double of a 10000-deep expression 0.0116745 vs 0.331982 (28x), codegen init without CSE 1.15092e-3 vs 1.34645e-2 (12x; with CSE 1.66448e-4 vs 3.34998e-3, 20x), series 1.99123e-3 vs 1.98982e-2 (10x), trig-product substitution 1.478e-5 vs 6.0009e-5 (4.1x), dense-rule substitution 1.13195e-3 vs 3.95472e-3 (3.5x). All ratios derived from page data. |
| **Workload** | Ten symbolic workloads adapted from SymEngine's own C++ benchmark suite plus SymbolicUtils-native ones: diff of expand((x^y+y^z+z^x)^50), 15-term Taylor series, trig-product substitution, 10^5-draw random-expression substitution (dense and sparse rule), variable search on shared and unshared expression sets, numeric evaluation of a 10000-deep expression, code-generation init, and the call of the generated function with common-subexpression elimination. |
| **Metric** | latency |
| **Hardware** | 128 x AMD EPYC 7502 32-Core Processor (128 virtual cores), Linux x86_64 CI runner |
| **Compiler and flags** | Julia 1.13.0 (LLVM 20.1.8, JIT target znver2), SymbolicUtils v4.46.6, Symbolics v7.39.2, SymEngine.jl v0.13.2 over the prebuilt SymEngine_jll v0.12.0+0. Per the public Yggdrasil recipe (S/SymEngine/build_tarballs.jl, symengine commit 088aa01) SymEngine_jll is built with CMake and no CMAKE_BUILD_TYPE, which SymEngine's CMakeLists defaults to Release (CMake's -O3 -DNDEBUG), for a generic x86_64 target, with WITH_SYMENGINE_THREAD_SAFE=yes, GMP integers and no LLVM (derived from public build recipe; compiler version not stated). Timings are minimum over samples (Chairmarks). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Per the benchmark text: the substitution and search wins use SymbolicUtils' IRStructure acceleration structure, which visits shared subexpressions once; the compiled-call win is a native Julia function produced by Code.toexpr plus eval (JIT compiled), against SymEngine's LambdaRealDoubleVisitor, which the file describes as 'an interpreter over the expression tree'. |
| **Adoption** | 560 stars; Symbolics.jl core |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/JuliaSymbolics/SymbolicUtils.jl) · [benchmark](https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/Symbolics/SymEngineComparison.md) |

## Verdict

In SciMLBenchmarks' SymEngineComparison (Julia 1.13.0 JIT, SymbolicUtils 4.46.6 and Symbolics 7.39.2 against SymEngine 0.12.0 through SymEngine.jl 0.13.2, AMD EPYC 7502 CI runner, Chairmarks minima), SymbolicUtils wins 4 of the 10 summary rows. Those are the CSE'd compiled call (0.31 vs 0.69 us), two IR-backed variable searches (2.1-2.2x) and sparse substitution (1.9x with IRStructure, 1.28x without). It is 3.5-48x slower in the other six rows and 41-361x slower on polynomial expansion, which the summary omits.

## Use it when

- Julia or ModelingToolkit pipelines that turn symbolic models into numeric functions and call them many times: the generated function's call was 2.2x (with CSE) to 4.2x (without) faster than SymEngine's lambda visitor, once the 12-20x slower code generation and the first-call LLVM compile are paid.
- Repeated variable searches or substitutions over a fixed, large set of expressions with shared subtrees, where you can keep one IRStructure alive across calls (2.1-2.2x over SymEngine free_symbols in the search rows).
- Sparse substitutions that match few nodes of a large tree: IRSubstituter was 1.9x and the plain Substituter 1.28x faster than SymEngine subs.
- Building custom rewrite systems (user rule sets, custom term types through TermInterface), which SymEngine does not offer.

## Skip it when

- Polynomial expansion: SymEngine is 41x (n=8) to 361x (n=32) faster on expand((x+y+z+w)^n) in the same run, and SymbolicUtils' expand uses Int64 coefficients that silently wrap above 2^63 (stated in the benchmark text).
- Differentiation, Taylor series and deep numeric evaluation, where SymEngine is 48x, 10x and 28x faster.
- One-shot code generation: codegen init is 12x (no CSE) to 20x (CSE) slower than SymEngine's, before the LLVM compile on first call, which neither row counts.
- Dense substitutions (3.5x slower) and small expressions (trig-product substitution 4.1x slower).
- Non-Julia hosts: there is no C or C++ API, so it is not an option for a C++ codebase that uses SymEngine directly.

## How it is fast

Expressions are hash-consed (one shared object per distinct subexpression, held in a global WeakCacheSet), so trees are really DAGs. An IRStructure flattens a set of expressions into a linear IR with a dependency graph. search_variables! and IRSubstituter then visit each shared node once and skip subtrees a sparse rule cannot touch. Code generation lowers an expression, optionally after common-subexpression elimination (Code.cse), to a Julia Expr that is eval'd and JIT-compiled by LLVM to native code. The compiled-call comparison is against SymEngine's LambdaRealDoubleVisitor, which walks a tree of closures.

## Compared with alternatives

Its wins share ClangJIT's mechanism (compile the specific expression at run time), but they apply only when you generate code from symbolic models in Julia and call it many times. For raw symbolic algebra speed (expand, diff, series, evaluation), SymEngine itself, already in the list, is the faster choice by 10-361x.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | about 29 Julia packages, including DynamicPolynomials, MultivariatePolynomials, Graphs, TermInterface, WeakCacheSets, TaskLocalValues, SpecialFunctions, MacroTools, Moshi and PrecompileTools; Symbolics.jl is needed for differentiation |
| **Minimum toolchain** | Julia 1.10 (Project.toml compat); the benchmark ran on Julia 1.13.0 |
| **Platforms** | any platform Julia supports (pure Julia) |
| **Thread safety** | Expression construction goes through a global hash-consing WeakCacheSet behind one ReentrantLock (WCS_LOCK), so it is safe but serialized across threads. The equality memo and the COMPARE_FULL flag are task-local. Multithreaded simplification is still an open issue (#62); otherwise not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw in the compiled-call rows (the two rows SymbolicUtils wins by JIT): the inputs are x=0.0, y=1.732, z=3.464, so log(x) = -Inf and every call returns +Inf (reproduced by evaluating the same expression in numpy). Every function of x (sin, cos, log, tan, sinh, cosh, tanh, atanh, asin, acos, atan) gets argument 0, typically its cheapest path. The per-call rows therefore mostly time dispatch overhead (closure-tree interpreter against native code), the case most favourable to the JIT; the 2.2x/4.2x margins were not measured at ordinary inputs.
- Harness selection: the 10-row summary leaves out the expand table, where SymEngine is 41-361x faster, and reports the faster SymbolicUtils variant per row. IRSubstituter calls populate_ir! on its input, so the warm-up call inserts the whole tree and its substituted results into the IR. clear_cache! empties only the Int32 index cache, so no timed sample pays IR construction. The search IRs are populated explicitly before timing. All timings are Chairmarks minima, which leaves GC pauses out of the allocation-heavy Julia side.
- Library limits that the benchmark had to work around: the recursive evaluate stack-overflows on a 10000-deep expression (the harness uses its own iterative evaluator), and code generation crashed in get_degrees on a zero-symbol Term inside an Add (the harness folds 2^e to a constant to avoid it).
- The baseline is SymEngine_jll 0.12.0, three releases old. Per the verifier's reading of the Yggdrasil recipe it is built thread-safe, for generic x86_64 and without LLVM, so SymEngine's own LLVM-compiled lambda was unavailable and the JIT-vs-interpreter rows compare different execution models.

## Known shortcomings

- Two of the four wins need an IRStructure built outside the timed region; without it, search is 1.28-1.34x slower and sparse substitution only 1.28x faster on a 14% smaller tree; the compiled-call win is JIT code against SymEngine's interpreter; SymEngine_jll 0.12.0 is a generic x86_64 Release -O3 build without LLVM; SymEngine is already listed from the same page, so this is the reverse claim.
- Harness flaw: the compiled-call rows (the 2.2x and 4.2x JIT wins) evaluate at x=0.0, where log(0) = -Inf makes every call return +Inf (reproduced in numpy) and every x function sees argument 0, so those rows mostly time dispatch overhead and favour the JIT (degenerate-workload precedent). The 10-row summary omits the expand table, where SymEngine is 41-361x faster. The IRSubstituter warm-up call fills the IR and clear_cache! empties only the index cache, so no timed sample pays the IR build; Chairmarks minima drop GC pauses on the Julia side; a global hash-consing ReentrantLock serialises expression construction across threads.

## Caveats and trade-offs

First-party benchmark by the Symbolics/SciML maintainers, single CI run without variance; the file says the first workload set 'plays to SymEngine's strengths', and SymEngine wins 6 of 10 rows by 3.5-48x. Two of the four SymbolicUtils wins (variable search) need an IRStructure populated outside the timed region; the plain search_variables! is 1.28-1.34x slower than SymEngine, and the IR-backed substitution likewise reuses an IR built in warm-up, so the IR rows exclude the DAG construction SymEngine's subs and free_symbols pay for. The plain Substituter's 1.28x sparse-rule win is on a tree 14% smaller than SymEngine's (2810 vs 3271 nodes). SymEngine 'variable search' is free_symbols converted to a Julia Vector and unioned into a Julia Set through ccall-based hashing, not an identical operation. The compiled-call row is JIT-compiled native code against SymEngine's tree interpreter (the jll has no LLVM backend), and the SymbolicUtils codegen-init row times only toexpr plus eval, so LLVM compilation of the generated function, which happens on the first call, is in neither row. SymEngine_jll is SymEngine 0.12.0 (three releases behind 0.15.0) built thread-safe (atomic reference counts) for generic x86_64 without TCMalloc, not SymEngine's tuned configuration, and its compiler version is not stated. [retier] The compiled-call rows (the 2.2x and 4.2x JIT wins) evaluate at x=0.0, where log(0) = -Inf makes every call return +Inf and every x function sees argument 0, so they mostly time dispatch overhead and favour the JIT. The 10-row summary omits the expand table, where SymEngine is 41-361x faster. The IRSubstituter warm-up fills the IR and clear_cache! empties only the index cache, so no timed sample pays the IR build; Chairmarks minima drop GC pauses; a global hash-consing ReentrantLock serialises expression construction across threads.

The JIT path pays a large setup cost: codegen init is 12x slower than SymEngine's. Core operations (expand, differentiate, series, deep evaluation) are 10-48x slower than SymEngine in this run.

## Maintenance

Actively developed (last commit 2026-10-11, v4.50.0, MIT, 560 stars) as the core of Symbolics.jl and ModelingToolkit. The benchmark is first-party, by SciML maintainers, on v4.46.6 from a single CI run.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** First-party SciML benchmark (SciMLBenchmarks.jl benchmarks/Symbolics/SymEngineComparison.jmd) with Julia 1.13.0 and EPYC 7502 stated; the SymEngine side is the prebuilt SymEngine_jll 0.12.0 whose compiler is not stated (flags only derivable from the Yggdrasil recipe), so not A; C. Downgraded as a claim: two of the four 'wins' exist only with an IRStructure built outside the timed region.
- **Retiered** C to D: Enricher: the compiled-call rows behind the JIT wins evaluate at x=0.0, where every call returns +Inf and the rows time dispatch overhead (degenerate-workload precedent, ThreadPool), and the summary omits the expand table where SymEngine is 41-361x faster; no valid like-for-like win remains: C to D.
- **Verifier notes:** Summary numbers on the page match the record, but the headline '4 of 10 rows faster' overstates the language win: the two search wins and most of the sparse-substitution win come from an IRStructure precomputed outside the timed region (plain variants lose search and win sparse substitution by only 1.28x on a smaller tree), and the compiled-call win is JIT code against SymEngine's interpreter in an LLVM-less, thread-safe SymEngine_jll build. SymEngine is already listed in COPYABLE.md with this same page as its benchmark, so this is the reverse claim on the same benchmark; keep as tier C with these shortcomings. Metadata checked: MIT LICENSE.md, 560 stars, last commit 2026-10-11, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-75 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/Symbolics/SymEngineComparison.md>
  - <https://github.com/JuliaSymbolics/SymbolicUtils.jl>
  - <https://github.com/JuliaSymbolics/SymbolicUtils.jl/commits>
  - <https://raw.githubusercontent.com/JuliaSymbolics/SymbolicUtils.jl/master/LICENSE.md>
  - <https://github.com/JuliaSymbolics/SymbolicUtils.jl/tree/master/src>
  - <https://raw.githubusercontent.com/JuliaSymbolics/SymbolicUtils.jl/master/src/irstructure.jl>
  - <https://raw.githubusercontent.com/JuliaSymbolics/SymbolicUtils.jl/master/src/substitute.jl>
  - <https://raw.githubusercontent.com/JuliaPackaging/Yggdrasil/master/S/SymEngine/build_tarballs.jl>
  - <https://raw.githubusercontent.com/symengine/symengine/088aa01bf4ba020e22b7492086abdc08b37a5f7f/CMakeLists.txt>
  - <https://raw.githubusercontent.com/symengine/SymEngine.jl/master/src/subs.jl>
  - <https://raw.githubusercontent.com/symengine/SymEngine.jl/master/src/types.jl>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/Symbolics/SymEngineComparison.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarks.jl/master/benchmarks/Symbolics/SymEngineComparison.jmd>
  - <https://raw.githubusercontent.com/JuliaSymbolics/SymbolicUtils.jl/master/README.md>
  - <https://raw.githubusercontent.com/JuliaSymbolics/SymbolicUtils.jl/master/Project.toml>
  - <https://raw.githubusercontent.com/JuliaSymbolics/SymbolicUtils.jl/master/src/irstructure.jl>
  - <https://raw.githubusercontent.com/JuliaSymbolics/SymbolicUtils.jl/master/src/substitute.jl>
  - <https://raw.githubusercontent.com/JuliaSymbolics/SymbolicUtils.jl/master/src/hashconsing.jl>
  - <https://raw.githubusercontent.com/JuliaSymbolics/SymbolicUtils.jl/master/src/graph_traversal.jl>
  - <https://github.com/JuliaSymbolics/SymbolicUtils.jl>
  - <https://github.com/JuliaSymbolics/SymbolicUtils.jl/tree/master/src>
  - <https://github.com/JuliaSymbolics/SymbolicUtils.jl/issues?q=is%3Aissue%20state%3Aopen%20performance>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/juliasymbolics/symbolicutils.jl`) · [data/wave14/enrich/raw/github_com_juliasymbolics_symbolicutils_jl.json](../../../data/wave14/enrich/raw/github_com_juliasymbolics_symbolicutils_jl.json) (enrichment confidence 0.6)

</details>
