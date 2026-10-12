# SymEngine

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> C++ symbolic algebra core (expand, diff, series, subs, lambdify) that runs SymPy-style workloads 10x to 1000x faster than pure-Python SymPy.

| | |
|---|---|
| **Beats** | SymPy (pure Python, called through PythonCall.jl) |
| **Claimed result** | About 12-16x faster than SymPy on eval_double once the SymPy side uses an explicit-stack traversal (page's 2660x row is dominated by sympy.postorder_traversal, 38.1 of 39.6 s on SymPy 1.14.0); other rows as published, with SymPy built evaluate=False inflating its substitution times 1.3-1.5x. |
| **Workload** | Ten summary workloads run as SymEngine.jl v0.13.2 (libsymengine from SymEngine_jll 0.12.0+0) against SymPy (timed inside Python with time.perf_counter, called via PythonCall.jl) and SymbolicUtils.jl: some adapted from symengine's own C++ benchmark suite (derivative of expand((x^y+y^z+z^x)^50), 15-term series of sin(cos(1+x)), substitution into a trig product, numeric evaluation of a 10000-deep expression, lambda code generation and compiled-call time) and some taken from SymbolicUtils' own suite (substitution into a random expression with 10^5 draws, variable search on common-subtree and dissimilar expressions); plus a separate expand((x+y+z+w)^n) table for n = 8 to 32. Minimum of samples; SymPy caches cleared before each sample. |
| **Metric** | latency |
| **Hardware** | AMD EPYC 7502 32-Core Processor (128 virtual cores) on a SciML CI runner, Linux x86_64 |
| **Compiler and flags** | Julia 1.13.0 (LLVM 20.1.8); libsymengine from SymEngine_jll v0.12.0+0, a BinaryBuilder binary whose public Yggdrasil recipe (S/SymEngine/build_tarballs.jl) passes BUILD_SHARED_LIBS=yes, WITH_MPC=yes and WITH_SYMENGINE_THREAD_SAFE=yes with GMP/MPFR/MPC dependencies but no CMAKE_BUILD_TYPE or compiler version; SymPy installed unpinned through pip via CondaPkg (benchmarks/Symbolics/CondaPkg.toml), version not shown |
| **Adoption** | 1.4k stars; backend of symengine.py, SymEngine.jl and others, optional core of SymPy and Sage (usage claim not verified here) |
| **Last commit** | 2026-09-04 |
| **Links** | [repository](https://github.com/symengine/symengine) · [benchmark](https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/Symbolics/SymEngineComparison.md) |

## Verdict

SciMLBenchmarks (SymEngineComparison, AMD EPYC 7502, Julia 1.13.0, SymEngine.jl 0.13.2 over prebuilt libsymengine 0.12.0, SymPy unpinned via CondaPkg) measured SymEngine faster than SymPy on all ten summary workloads, from about 11x (variable search on dissimilar expressions) to about 1000x (diff of a 1326-term expansion) and 2000x (dense-rule substitution on unequal trees); the 2660x eval_double ratio is mostly SymPy's quadratic recursive-generator traversal in the page's own evaluator. SymbolicUtils.jl beat SymEngine on four rows.

## Use it when

- Python or Julia code where SymPy's expand, diff, subs or series dominates run time on expressions of hundreds to thousands of terms (the SciML run shows about 1000x on diff of a 1326-term expansion and 226x on expand((x+y+z+w)^32)).
- Generating many derivatives or Jacobians for code generation (mechanics, chemical kinetics, optimal control) where symbolic construction cost matters more than simplification power.
- Embedding a symbolic engine in a C or C++ application through a small MIT-licensed library with a stable C API.
- Fast numeric callbacks from symbolic expressions via the lambda visitors, where SymPy's numpy lambdify call was about 12x slower per call (CSE case) on the page.

## Skip it when

- You need SymPy's breadth: simplify, solve, integrate, assumptions on expressions (issue #2047 is open) or pretty printing variants; SymEngine covers a subset and you round-trip to SymPy for the rest.
- Pure-Julia pipelines on Symbolics.jl: SymbolicUtils.jl beat SymEngine on the same page for sparse-rule substitution (0.000593 s vs 0.00110 s), variable search (0.00049 s vs 0.00103 s) and compiled calls (3.13e-7 s vs 6.93e-7 s with CSE; 2.56e-6 s vs 1.07e-5 s without), partly because SymEngine is reached through ccall wrappers.
- Multithreaded use of a default build: WITH_SYMENGINE_THREAD_SAFE defaults to off (on only with BUILD_FOR_DISTRIBUTION or OpenMP), so reference counts are not atomic.
- Untrusted or exotic inputs where a crash is unacceptable: Release mode uses manual reference counting and raw pointers and the README says a bug can segfault; past issues include parser crashes on invalid strings (#2002) and a sparse-matrix crash (#1694).

## How it is fast

Expressions are compiled C++ objects with intrusive, non-atomic reference counting (its own RCP in Release mode instead of Teuchos::RCP), hashed canonical Add/Mul stored as coefficient dictionaries, and exact coefficients on GMP, FLINT or Boost.Multiprecision integers, so construction and canonicalisation cost what SymPy pays in Python object overhead and its cache. Hot kernels are specialised: polynomial expansion over coefficient maps (the canonical expand((x+y+z+w)^n) benchmark), series over univariate polynomial types, numeric evaluation by a C++ visitor, and lambdify through LambdaRealDoubleVisitor (a tree interpreter with optional CSE) or an LLVM JIT visitor when built WITH_LLVM.

## Compared with alternatives

The siblings in this category (FLINT, mp++, GMP alternatives such as Malachite or dashu) speed up numeric big-integer and polynomial arithmetic; pick SymEngine when the workload is symbolic expression manipulation (expand, diff, subs, series, codegen) and you want those exact coefficients handled for you, optionally on top of FLINT via INTEGER_CLASS=flint.

## Integration

| | |
|---|---|
| **Form** | static lib by default (BUILD_SHARED_LIBS OFF), shared lib optional; Python, Julia, Ruby and Haskell wrappers in separate repos |
| **Dependencies** | GMP by default (INTEGER_CLASS gmp; or gmpxx, flint, piranha, or boostmp to drop GMP); optional MPFR, MPC, FLINT, ARB, LLVM, GMP-ECM, primesieve, TCMalloc, OpenMP; vendored cereal and Teuchos |
| **Minimum toolchain** | C++11 (target_compile_features cxx_std_11), C++17 when built with LLVM 16+; CMake 3.18+ |
| **Platforms** | Linux, macOS and Windows (conda-forge and Conan packages, MinGW and MSVC builds); open issue #1975 reports test_fields failing on Apple M2 |
| **Thread safety** | Not thread-safe by default; build with WITH_SYMENGINE_THREAD_SAFE=yes (atomic reference counts; forced on with OpenMP), which the README recommends for distribution packages but turns off in its 'optimized build' recipe |
| **Drop-in for the baseline** | partial: symengine.py mirrors a SymPy-like API subset and converts to and from SymPy objects, and SymPy's USE_SYMENGINE=1 backend switch (sympy/core/backend.py) is used only by sympy.liealgebras in SymPy 1.14; everything else needs code changes |

## Gotchas

- Harness flaw behind the largest ratio: the eval_double row (SymEngine 0.0117 s vs SymPy 31.06 s, about 2660x) times the page's Python evaluator, which walks the tree with sympy.postorder_traversal, a recursive 'yield from' generator whose cost grows with nodes times depth. Rerun here with SymPy 1.14.0 on an Intel Xeon at 2.1 GHz, the 10000-deep expression (80,002 nodes) took 39.6 s, of which 38.1 s was the traversal alone (0.28, 1.23 and 5.33 s at depths 1000, 2000 and 4000: quadratic), while the same per-node SymPy calls driven by an explicit stack, as the page's own Julia evaluator does, took 0.184 s with the identical value 9.856474171370099. Against a linear traversal SymEngine's lead is roughly 12x to 16x (derived; cross-machine estimate), not 2660x.
- The random-expression substitution builds SymPy's tree with evaluate=False constructors, so SymPy's subs re-canonicalises every rebuilt node inside the timed region. Rerun here, the tree reproduced the page's 8498 nodes; subs took 1.55 s (dense) and 0.61 s (sparse) on it versus 1.03 s and 0.46 s on a tree built with evaluating constructors (8703 nodes), so that choice inflates SymPy by about 1.3x to 1.5x on top of the unequal tree sizes (3271 SymEngine nodes) already noted.
- The measured libsymengine is the prebuilt SymEngine_jll 0.12.0 with WITH_SYMENGINE_THREAD_SAFE=yes and no TCMalloc or LLVM, three releases behind 0.15.0; the README's optimized recipe (-march=native -O3, TCMalloc, thread safety off) should be faster, so SymEngine's numbers are not its best case.
- The README warns that benchmark timings depend on the order benchmarks run in one executable because of malloc behaviour, and recommends TCMalloc when benchmarking.

## Known shortcomings

- SciMLBenchmarks output (EPYC 7502): substitution rows use unequal trees (SymPy 8498 nodes vs SymEngine 3271), eval_double compares C++ evalf with a hand-written Python evaluator in one \~31 s call, SymEngine loses to SymbolicUtils.jl on 4 rows, the SymPy version is unpinned and the prebuilt libsymengine 0.12.0 has no build type or compiler stated. No symbolic-algebra category exists; filed beside FLINT under big-integer-arbitrary-precision.
- Harness flaw in the eval_double row (2660x): SymPy's time is mostly sympy.postorder_traversal, a recursive yield-from generator whose cost is quadratic in depth; rerun with SymPy 1.14.0 gave 39.6 s total of which 38.1 s is traversal, and the same per-node work with an explicit stack took 0.184 s with the same value, so the real lead is about 12-16x. The dense/sparse substitution rows build SymPy's tree with evaluate=False, which inflates SymPy's time about 1.3-1.5x (page's 8498 nodes reproduced).

## Caveats and trade-offs

The page is an independent benchmark by SciML maintainers (Aayush Sabharwal, Chris Rackauckas; SciMLBenchmarks.jl file benchmarks/Symbolics/SymEngineComparison.jmd, code public, CPU stated), but they also maintain SymbolicUtils.jl, and the first workload set was adapted from SymEngine's own suite and is described on the page as playing to a compiled symbolic kernel. The same page shows SymEngine losing to pure-Julia SymbolicUtils.jl on sparse-rule substitution (0.00110 s vs 0.000593 s), variable search (0.00103 s vs 0.00049 s with IRStructure), the compiled call with CSE (6.93e-7 s vs 3.13e-7 s) and the compiled call without CSE (1.07e-5 s vs 2.56e-6 s). The random-expression substitution compares unequal trees: realized node counts are 3271 for SymEngine, 2810 for SymbolicUtils and 8498 for SymPy, so the 2000x and 970x ratios overstate the per-node gap. The eval_double row pits SymEngine's native C++ evalf against a hand-written Python bottom-up evaluator built on SymPy constructors (SymPy's own evalf is exponential in nesting depth here), timed as a single call of about 31 s rather than a minimum of samples. SymEngine is reached through the SymEngine.jl ccall wrapper; SymPy is pure Python, so a compiled-versus-interpreted gap is expected. Build type and compiler of the prebuilt libsymengine 0.12.0 (not the newest release) and the SymPy version are not stated, hence B rather than A; the benchmark file is a single recent run. SymEngine's own repo has no README or wiki claim with SymPy numbers: the wiki pages found earlier (Optimizing expand2b, Univariate Series expansion benchmarks) only compare SymEngine variants and Piranha. Older comparisons with GiNaC, Sage and CSymPy sit in blocked pages. The wave 8 categories have no symbolic-algebra bucket; big-integer-arbitrary-precision was chosen to sit beside FLINT (SymEngine uses GMP/FLINT/MPFR/MPC for exact and arbitrary-precision coefficients). [retier] eval_double 2660x row is an artefact of SymPy's recursive postorder_traversal (quadratic in depth); same work with an explicit stack takes 0.184 s vs 39.6 s. Dense/sparse substitution rows build SymPy trees with evaluate=False (1.3-1.5x inflation). Numbers first-party-run on the symengine.org benchmarks page.

Much smaller feature set than SymPy (no full simplify, solvers or integration); a C++ expression tree with reference-counted nodes, GMP or Boost integers, optional FLINT, MPFR, LLVM JIT and Piranha; usable from C, Python, Julia, Ruby, Haskell and others through wrappers.

## Maintenance

Actively maintained (last commit 2026-09-04; latest release v0.15.0), MIT-licensed with BSD-3 vendored code and packaged on conda-forge and Conan, so easy to adopt; build it with thread safety on if you share expressions across threads.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** SciMLBenchmarks (independent third-party suite; source benchmarks/Symbolics/SymEngineComparison.jmd in SciML/SciMLBenchmarks.jl) shows SymEngine beating SymPy on every workload, with CPU (AMD EPYC 7502), Julia 1.13.0 and LLVM 20.1.8 stated; libsymengine is the prebuilt SymEngine_jll 0.12.0+0 whose Yggdrasil recipe gives CMake options but no build type or compiler version, and the SymPy version is unpinned, so not A.
- **Verifier notes:** All ten summary ratios check out against the page's HTML tables (derived ratios correct to rounding). baseline_in_list corrected to false: SymPy is not among wave 8 baselines (big-integer-arbitrary-precision lists GMP and MPFR). Repo checked on github.com: MIT, 1.4k stars, 314 forks, last commit 2026-09-04, active. Category: no spec Part 4 category covers symbolic algebra; big-integer-arbitrary-precision is the least-bad wave 8 fit (exact arithmetic on GMP/FLINT), otherwise a new symbolic-algebra category would be needed. Shortcomings to record: unequal random trees in the substitution rows (8498 SymPy nodes vs 3271), eval_double against a hand-written Python evaluator, losses to SymbolicUtils.jl on four rows, unpinned SymPy and unstated build type/compiler of the prebuilt libsymengine.
- **Fields the verifier corrected:** `baseline_in_list`, `workload`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** SciMLBenchmarks (verifier); enricher (wave 8)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/Symbolics/SymEngineComparison.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarks.jl/master/benchmarks/Symbolics/SymEngineComparison.jmd>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarks.jl/master/benchmarks/Symbolics/CondaPkg.toml>
  - <https://raw.githubusercontent.com/JuliaPackaging/Yggdrasil/master/S/SymEngine/build_tarballs.jl>
  - <https://github.com/symengine/symengine>
  - <https://github.com/symengine/symengine/commits>
- **Sources the enricher read:**
  - <https://github.com/symengine/symengine>
  - <https://github.com/symengine/symengine/commits>
  - <https://github.com/symengine/symengine/releases>
  - <https://github.com/symengine/symengine/issues?q=is%3Aissue+is%3Aopen+segfault+OR+crash+OR+thread>
  - <https://github.com/symengine/symengine/issues/1848>
  - <https://raw.githubusercontent.com/symengine/symengine/HEAD/README.md>
  - <https://raw.githubusercontent.com/symengine/symengine/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/symengine/symengine/HEAD/symengine/CMakeLists.txt>
  - <https://raw.githubusercontent.com/symengine/symengine/HEAD/cmake/UserOverride.cmake>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarksOutput/main/markdown/Symbolics/SymEngineComparison.md>
  - <https://raw.githubusercontent.com/SciML/SciMLBenchmarks.jl/master/benchmarks/Symbolics/SymEngineComparison.jmd>
  - <https://raw.githubusercontent.com/sympy/sympy/master/sympy/core/traversal.py>
  - https://pypi.org/project/sympy/ (sympy 1.14.0 wheel installed in a scratch directory to rerun the eval_double and substitution workloads, and to read sympy/core/backend.py)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/symengine/symengine`) · [data/wave8/enrich/raw/github_com_symengine_symengine.json](../../../data/wave8/enrich/raw/github_com_symengine_symengine.json) (enrichment confidence 0.8)

</details>
