# kiwi (nucleic, C++ Cassowary solver)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only C++11 Cassowary linear-constraint solver for UI layout, claimed 10-500x faster than the original Cassowary C++ solver.

| | |
|---|---|
| **Beats** | original Cassowary C++ solver (cassowary-0.60 assumed; the README does not give a version) |
| **Claimed result** | README: 'Kiwi ranges from 10x to 500x faster than the original Cassowary solver with typical use cases gaining a 40x improvement. Memory savings are consistently &gt; 5x.' |
| **Workload** | Constraint solving with the Cassowary algorithm for typical user-interface layout use cases; the README does not describe the workload. |
| **Metric** | other |
| **Adoption** | 781 stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/nucleic/kiwi) · [benchmark](https://github.com/nucleic/kiwi) |

## Verdict

The only evidence is first-party README prose ('10x to 500x faster than the original Cassowary solver with typical use cases gaining a 40x improvement', memory savings over 5x), unchanged since the 2013-2014 0.1.x releases, with no named Cassowary version, workload, hardware, compiler or benchmark code; the repo's benchmarks measure Kiwi alone and cannot reproduce the comparison.

## Use it when

- GUI or document layout engines that re-solve a few dozen to a few hundred linear constraints on every resize, using edit variables for window width and height.
- Python code that needs a Cassowary solver: kiwisolver (1.5.1, Python 3.10+) ships wheels and is already installed wherever Matplotlib is (matplotlib 3.11.2 requires kiwisolver&gt;=1.3.1).
- C++ projects that want a dependency-free, BSD-3-Clause, header-only constraint solver consumable through CMake FetchContent as kiwi::kiwi.
- Replacing the original Cassowary C++ toolkit or other ports where stay constraints are not needed or can be emulated with edit variables.

## Skip it when

- When you need general LP or QP solving with an objective you choose: Kiwi has no user objective (open issues #164 and #176 ask for one); use an LP/QP solver such as HiGHS, PIQP or OSQP.
- Strict strength hierarchies: because strengths are summed doubles, many weak constraints can outweigh a medium one (documented in solver_internals.rst); the original Cassowary's lexicographic ordering guarantees the hierarchy.
- Large or high-churn systems on one long-lived solver: every map is a sorted vector (O(n) insert and erase), and removed edit variables and constraints leave zeroed cells in the objective, so maintainers recommend rebuilding the solver when constraints change often (issue #154).
- Multithreaded use of shared Variable or Constraint objects: refcounts are non-atomic and a maintainer states 'kiwisolver is not threadsafe' (issue #230).
- Anyone who needs the 10-500x figure for a decision: no benchmark against Cassowary, workload, hardware or compiler has ever been published.

## How it is fast

It implements the incremental simplex method of the Cassowary paper (primal optimize after adds, dual simplex after suggestValue on edit variables) but replaces Cassowary's lexicographic symbolic weights with single doubles (strength::create packs three tiers as a\*1e6 + b\*1e3 + c), so every tableau cell is one double. All solver maps (rows, variables, constraints, edits and each row's cells) are Loki AssocVector sorted vectors, which the docs credit with about 2x over std::map, and Variable/Constraint handles use a non-atomic intrusive refcount instead of std::shared_ptr.

## Compared with alternatives

No catalogued sibling solves Cassowary constraints; the category's QP solvers (PIQP, ProxQP, QPALM) handle general convex objectives, while Kiwi is the pick for incremental, strength-prioritised layout constraints re-solved on every resize. For JavaScript, use its TypeScript descendant lume/kiwi (wave 13) instead.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for C++ (Loki AssocVector is vendored in kiwi/AssocVector.h); the Python wrapper builds with cppy |
| **Minimum toolchain** | C++11 (CMakeLists sets cxx_std_11, CMake 3.15+; CI tests C++11 and C++20); Python wrapper needs Python 3.10+ |
| **Platforms** | any platform with a C++11 compiler; Python wheels per release notes include free-threaded CPython builds and RISC-V |
| **Thread safety** | not thread safe: one solver per thread, and Variable/Constraint handles must not be shared across threads because SharedData uses non-atomic reference counts; the Python wrapper holds the GIL or a global lock around solver calls |
| **Drop-in for the baseline** | partial — same Cassowary model and edit-variable workflow, but a different API, no stay constraints, and floating-point instead of lexicographic strengths, so solutions can differ in corner cases |

## Gotchas

- Errors are C++ exceptions (UnsatisfiableConstraint, DuplicateConstraint, UnknownEditVariable, BadRequiredStrength, InternalSolverError), and edit variables cannot have required strength.
- Feasibility and pivoting use a fixed absolute epsilon of 1e-8 (impl::nearZero), regardless of the magnitude of coordinates or coefficients.
- Strength components are clipped to [0, 1000] each, so custom strengths saturate (strong is 1e6, required is 1,001,001,000) and weighting tricks beyond those bounds silently do nothing.
- The repo's own C++ benchmark (benchmarks/enaml_like_benchmark.cpp, nanobench, g++ -O2) times only Kiwi, and its 'suggest value WxH' cases resubmit the same width and height every iteration, so after the first iteration delta is 0 and no dual-simplex work is timed; the Python benchmark cycles six sizes and is the better re-solve measurement.

## Known shortcomings

- The 10x-500x over Cassowary is first-party README prose unchanged since PyPI 0.1.3 (2014-07-12); the benchmarks directory times kiwi alone (g++ -O2) with no Cassowary comparison, and no independent numbers were found.
- Enricher: the repo's own enaml_like_benchmark.cpp resends the same width and height in its 'suggest value' cases, so after the first iteration the delta is 0 and no dual-simplex work is timed (the Python benchmark cycles six sizes). Non-atomic refcounts, and the maintainer says kiwisolver is not thread-safe (#230); removed constraints leave zeroed objective cells (#154); fixed 1e-8 epsilon; strengths saturate.

## Caveats and trade-offs

Numbers only in README prose and mirrored in docs/source/index.rst and downstream package descriptions: no workload, hardware, compiler, flags, Cassowary version or benchmark code against Cassowary is published. The claim text is unchanged since at least kiwisolver 0.1.3 on PyPI (uploaded 2014-07-12), so the measurement dates from 2014 or earlier and was taken against the Cassowary code of that time. The repo's benchmarks directory (enaml_like_benchmark.cpp built by build_and_run_bench.sh with g++ -std=c++11 -O2, and a Python variant using perf) measures only kiwi itself, mainly to compare internal map types; they cannot reproduce the Cassowary comparison. The 2x speedup over std::map for kiwi's internal AssocVector-style sorted map is a sentence in docs/source/basis/solver_internals.rst with no table. amoeba (starwing, C) says it improves on kiwi's suggest path but gives no numbers. A JavaScript port line (kiwi.js and its fork lume/kiwi, listed in wave 13) is a separate entry, not a duplicate of this C++ project.

Not a refactoring of the original, so behaviour differs: stay constraints were dropped (emulate with edit variables or equality constraints), and strengths are plain floating point numbers instead of lexicographic ordering, so in rare corner cases many weak constraints can outweigh a medium one. Header-only C++ with hand-rolled Python bindings. Internally uses Loki's AssocVector, which the docs say gives a 2x speedup over std::map.

## Maintenance

Actively maintained by the Nucleic team (solver 1.5.1 released 2026-08-28, commits into October 2026, 781 stars) as a Matplotlib dependency, BSD-3-Clause and header-only, though a March 2026 static-review batch of Python-wrapper bugs (issues #223-#231, refcount and lock handling) is still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The 10x-500x (typical 40x) speedup and &gt;5x memory savings over the original Cassowary solver appear only as first-party README and docs prose with no workload, hardware, compiler, Cassowary version or benchmark code against Cassowary; the repo's benchmarks/ (enaml_like_benchmark.cpp, g++ -std=c++11 -O2) time kiwi alone. One WebSearch found no independent head-to-head measurement.
- **Verifier notes:** Claim verified verbatim on the README and docs index; tier C stands for unreproducible first-party prose, and the claim dates to 2014 or earlier (PyPI 0.1.3). Metadata checked: BSD-3-Clause (Modified BSD, Nucleic Development Team), 781 stars, not a fork, last commit 2026-10-09, active. Not a duplicate of any listed entry (lume/kiwi in wave 13 is a TypeScript descendant).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-181 (wave 8 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/nucleic/kiwi>
  - <https://github.com/nucleic/kiwi/commits>
  - <https://github.com/nucleic/kiwi/tree/main/benchmarks>
  - <https://github.com/nucleic/kiwi/tree/main/docs/source/basis>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/README.md>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/docs/source/index.rst>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/docs/source/basis/solver_internals.rst>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/benchmarks/build_and_run_bench.sh>
  - <https://pypi.org/pypi/kiwisolver/0.1.3/json>
- **Sources the enricher read:**
  - <https://github.com/nucleic/kiwi>
  - <https://github.com/nucleic/kiwi/issues>
  - <https://github.com/nucleic/kiwi/issues/154>
  - <https://github.com/nucleic/kiwi/issues/230>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/README.md>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/releasenotes.rst>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/docs/source/index.rst>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/docs/source/basis/solver_internals.rst>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/docs/source/basis/basic_systems.rst>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/docs/source/use_cases/enaml.rst>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/benchmarks/enaml_like_benchmark.cpp>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/benchmarks/enaml_like_benchmark.py>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/benchmarks/build_and_run_bench.sh>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/kiwi.h>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/solverimpl.h>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/solver.h>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/maptype.h>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/AssocVector.h>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/row.h>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/strength.h>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/shareddata.h>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/errors.h>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/util.h>
  - <https://raw.githubusercontent.com/nucleic/kiwi/HEAD/kiwi/version.h>
  - <https://pypi.org/pypi/kiwisolver/json>
  - <https://pypi.org/pypi/matplotlib/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nucleic/kiwi`) · [data/wave8/enrich/raw/github_com_nucleic_kiwi.json](../../../data/wave8/enrich/raw/github_com_nucleic_kiwi.json) (enrichment confidence 0.75)

</details>
