# Cinder (Meta's CPython fork with method JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C (JIT in C++)` · `Python-2.0` · 🟢 active

> Meta's CPython fork with a method-at-a-time C++ JIT and Static Python; 1.5-3.8x over its own interpreter on four microbenchmarks.

| | |
|---|---|
| **Beats** | CPython interpreter: the same Cinder build with the JIT disabled (the README calls it stock CPython; the paper did not run a separate stock CPython build) |
| **Claimed result** | cinder/3.10 README: the JIT 'can achieve 1.5-4x speed improvements on many Python performance benchmarks'; 'Static Python plus Cinder JIT achieves 18x the performance of stock CPython on a typed version of the Richards benchmark'. Peer-reviewed paper appendix (Programming 2023, Cinder 3.8-era commits, mean of 10 runs, process user time): Cinder JIT with shadow frames on the original untyped benchmarks versus the same Cinder build with the JIT off: richards 3.8x, deltablue 1.9x, nbody 1.6x, fannkuch 1.5x; Static Python + JIT on the hand-optimized typed Richards (T-Max) versus untyped Richards without the JIT 17.7x, and on the simply-typed Richards (T-Min) about 7.2x (all derived from page data). |
| **Workload** | Python microbenchmarks richards, deltablue, nbody and fannkuch (cinder/3.8 Tools/benchmarks, original untyped plus Static Python typed variants) run with the C++ method-at-a-time Cinder JIT (-X jit, JIT list limited to the benchmark code, with and without shadow frames), versus the same build with the JIT off; README additionally claims gains on unnamed 'Python performance benchmarks'. |
| **Metric** | throughput |
| **Hardware** | 64-bit CentOS Linux system (paper); CPU model not stated |
| **Compiler and flags** | Paper: Cinder 'compiled with default configure settings', compiler not named; the cinder/3.10 README says its basic build instructions give a binary without PGO/LTO |
| **Adoption** | 3.8k stars; used in production at Meta and Instagram |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/facebookincubator/cinder) · [benchmark](https://github.com/brownplt/insta-model/blob/main/pj-7.1/paper.tex) |

## Verdict

The Programming 2023 paper appendix timed four public microbenchmarks (mean of 10 runs of process user time, Cinder 3.8-era commits built with default configure settings on 64-bit CentOS Linux, CPU and compiler not stated): untyped richards 10.06 s without the JIT versus 2.64 s with JIT and shadow frames (3.8x), deltablue 1.87x, nbody 1.56x, fannkuch 1.50x; hand-typed Static Python Richards with JIT ran in 0.567 s (17.7x over untyped no-JIT). The baseline in every case is Cinder's own interpreter, not stock CPython.

## Use it when

- Large CPython services (pre-fork web servers such as Django) where you can profile production, put the hot functions in a jit-list and compile them before forking workers.
- Object-heavy, call-heavy Python code: the paper's untyped Richards ran 3.8x faster with the JIT and shadow frames than the same build without the JIT.
- Hot modules you are willing to annotate with Static Python primitives (int64, double, cbool, Array): hand-optimised typed Richards reached 17.7x and typed nbody 6.6x over the untyped no-JIT runs.
- Teams already on Python 3.14 who want the same JIT without a forked runtime: use the CinderX wheel (Linux x86-64/aarch64, macOS arm64, Windows x86-64; cinderx.jit.auto() compiles hot functions automatically).

## Skip it when

- Anyone needing support: the cinder/3.10 README answers 'Is this supported?' with 'Short answer: no', and CinderX calls itself experimental for external users.
- Numeric list-manipulating code left untyped: fannkuch and nbody gained only about 1.5x from the JIT, and simply-typed (T-Min) versions were no faster than untyped code under the JIT.
- Running Static-Python-typed code without the JIT: typed fannkuch T-Max took 34.9 s under Static Python alone versus 4.1 s for the untyped original, because the interpreter keeps primitives boxed.
- Short-lived scripts with the default JIT setting: by default the JIT compiles every function ever called, which the README warns can make programs slower; immortal instances also make straight-line code slower in the fork.
- Platforms other than Linux x64 for the fork itself (the 3.10 README says anything else, including macOS, probably won't work); the README's basic build has no PGO/LTO.

## How it is fast

The JIT lowers bytecode to a typed, register-based HIR in SSA form, runs optimisation passes, inserts reference-count operations from per-opcode metadata, lowers to LIR for register allocation and emits x64 code with AsmJit; shadow-frame mode avoids allocating full Python frames. Static Python adds typed slots (LOAD_FIELD/STORE_FIELD become fixed-offset loads), vtable-based INVOKE_FUNCTION/INVOKE_METHOD calls that the JIT turns into direct native calls, and unboxed int64/double/cbool/Array primitives. The interpreter also carries shadowcode (an inline-caching specialising interpreter similar to PEP 659) and eager evaluation of immediately awaited coroutines.

## Compared with alternatives

Pick Cinder/CinderX over the CPython copy-and-patch JIT (about 7-8% geomean on pyperformance) when you can curate hot functions or add Static Python types and want multi-x gains on object-oriented code while staying on CPython; pick Numba or Hana Jit instead for numeric array kernels, where typed loop compilation gives far larger speedups with less code change.

## Integration

| | |
|---|---|
| **Form** | Cinder: full CPython fork built from source (configure && make, or the ghcr.io cinder-runtime Docker image); successor CinderX: Python C++ extension module (pip wheel) |
| **Dependencies** | Cinder: CPython build dependencies plus the AsmJit library used by the JIT back end; the README recommends building inside the project's Fedora-based CI Docker image. CinderX: stock CPython 3.14. |
| **Minimum toolchain** | Cinder 3.10: Linux x64 toolchain from its CI image (C++ JIT; open issue #114 reports a C++20 build error); CinderX: Python 3.14, GCC 13+ or Clang 18+ |
| **Platforms** | Cinder fork: Linux x86-64 only. CinderX: Linux x86-64 and aarch64, macOS arm64, Windows x86-64 (PyPI wheels for cp314 and free-threaded cp314t) |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial: Cinder replaces the CPython 3.10 binary and runs unmodified code, but the JIT needs -X jit plus a jit-list and Static Python needs annotated modules loaded by the strict/static loader; CinderX is an import-and-enable extension for stock CPython 3.14 |

## Gotchas

- Baseline is not stock CPython: the paper's no-JIT column is the same Cinder build (with shadowcode and immortal instances), and the README's '18x the performance of stock CPython' maps to 17.7x over that build only for the hand-optimised typed Richards; the simply-typed version gives 7.2x. No CPU model, compiler or PGO/LTO state is given.
- Harness weakness: all three Richards drivers (richards.py, richards_static.py, richards_static_basic.py in Tools/benchmarks) call Richards().run(n) and discard its boolean, so the holdCount 9297 / qpktCount 23246 result check never fails a timed run; fannkuch does assert its result (30). No wrong result was found, but the timings are not output-checked for Richards.
- The paper's summary table (Microbenchmark performance ratios) is inconsistent for deltablue: richards, fannkuch and nbody divide Static Python + JIT + shadow frames by untyped code under JIT + shadow frames, but the deltablue ratios 0.59 and 0.30 match division by the typed code's no-JIT, no-Static-Python time (0.992 s); on the same basis as the other rows they would be about 0.89 and 0.45 (derived from page data). The appendix raw data used for this entry are unaffected.
- Open JIT issues show rough edges: #87 (Static Python @inline with double arguments aborts the JIT with 'No pattern found for opcode Fadd: Xxr'), #86 (nonsensical TypeError with -X jit and static compile), and #29 (-X jit-enable-jit-list-wildcards, which the paper's commands use, about 4x higher PyEntry_init overhead).

## Known shortcomings

- Raised C to B on the peer-reviewed Programming 2023 'Gradual Soundness' paper (source in brownplt/insta-model, appendix data derived: JIT 1.5-3.8x, Static Python Richards 17.7x), but the baseline is Cinder with the JIT off rather than stock CPython, no CPU or compiler is given, and the 18x holds only on hand-typed Richards (about 7x simply typed). The JIT has moved to facebookincubator/cinderx (MIT, 282 stars). Filed under jits alongside the CPython JIT.
- Enricher: all three Richards drivers discard the run() result, so the holdCount/qpktCount check never fails a timed run (fannkuch does assert); the paper's summary table is inconsistent for deltablue (0.59/0.30 divide by the typed no-JIT time of 0.992 s where the same basis as other rows gives about 0.89/0.45; appendix data unaffected). The JIT now lives in cinderx (MIT, PyPI 2026.10.5.0, Python 3.14).

## Caveats and trade-offs

The README numbers sit in the older cinder/3.10 branch (last commit 2024-06-25); the default branch meta/3.14 (last commit 2026-10-06) README says the name cinder is historical and points to facebookincubator/cinderx (MIT, 282 stars, a CPython 3.14+ extension) for the JIT and Static Python, so the JIT code now lives there. Paper timings are from Cinder 3.8 commits d0d071, c9d14c and 144a21 (2022), not the 3.10 branch. The no-JIT baseline is Cinder's own interpreter build, not stock CPython; no CPU model, compiler or PGO/LTO state given. The 18x needs hand-typed Static Python with primitive types (simply typed code gives about 7x); the 1.5-4x JIT range is backed by only four microbenchmarks in the paper. README: 'Is this supported? Short answer: no.' JIT-compiling every called function by default can make programs slower. No comparison with PyPy.

Explicitly 'not supported' for outside users (README: Is this supported? Short answer: no); JIT is enabled with -X jit and usually driven by a jit-list file; Static Python needs type annotations; the 3.10 branch is Linux x64 only; the default branch now tracks CPython 3.14 and the JIT ships as the cinderx extension.

## Maintenance

The fork's meta/3.14 branch is active (commits on 2026-10-06) but is now a CPython tree; the cinder/3.10 branch with the documented JIT stopped on 2024-06-25, and the JIT lives on in the actively released, MIT-licensed CinderX extension, which is the practical way to use it today; explicitly unsupported for outside users.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the README claims (1.5-4x, 18x) appear verbatim but without methodology, while the peer-reviewed paper 'Gradual Soundness: Lessons from Static Python' (The Art, Science, and Engineering of Programming 7(1):2, 2023; LaTeX source in brownplt/insta-model pj-7.1/paper.tex) gives 10-run timings with and without the Cinder JIT on public microbenchmarks (cinder/3.8 Tools/benchmarks). Not A: CPU model and compiler are not stated (only '64-bit CentOS Linux', 'default configure settings'), and the no-JIT baseline is Cinder's own build rather than stock CPython.
- **Verifier notes:** Claims check out against the README and the peer-reviewed paper's appendix data; upgraded to B (paper co-authored by Brown University and Meta engineers). Shortcomings: baseline is Cinder with the JIT off rather than stock CPython, no CPU/compiler, 18x only for hand-optimized Static Python Richards, and the JIT has moved to facebookincubator/cinderx, which the orchestrator may want to note or list instead.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.10/README.rst>
  - <https://github.com/facebookincubator/cinder>
  - <https://github.com/facebookincubator/cinder/commits>
  - <https://github.com/facebookincubator/cinder/commits/cinder/3.10>
  - <https://github.com/facebookincubator/cinder/tree/cinder/3.10/Tools/benchmarks>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/HEAD/LICENSE>
  - <https://github.com/facebookincubator/cinderx>
  - <https://github.com/brownplt/insta-model>
  - <https://github.com/brownplt/insta-model/tree/main/pj-7.1>
  - <https://raw.githubusercontent.com/brownplt/insta-model/HEAD/pj-7.1/paper.tex>
  - <https://raw.githubusercontent.com/brownplt/insta-model/HEAD/pj-7.1/bg.bib>
  - <https://github.com/brownplt/insta-model/blob/main/pj-7.1/paper.tex>
- **Sources the enricher read:**
  - <https://github.com/facebookincubator/cinder>
  - <https://github.com/facebookincubator/cinder/commits>
  - <https://github.com/facebookincubator/cinder/commits/cinder/3.10>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.10/README.rst>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/HEAD/README.rst>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.8/Tools/benchmarks/richards.py>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.8/Tools/benchmarks/richards_static.py>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.8/Tools/benchmarks/richards_static_basic.py>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.8/Tools/benchmarks/richards_static_lib.py>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.8/Tools/benchmarks/richards_static_basic_lib.py>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.8/Tools/benchmarks/fannkuch.py>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.8/Tools/benchmarks/fannkuch_static.py>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.8/Tools/benchmarks/fannkuch_static_lib.py>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.8/Tools/benchmarks/jitlist_main.txt>
  - <https://raw.githubusercontent.com/facebookincubator/cinder/cinder/3.8/Tools/benchmarks/jitlist_richards_static.txt>
  - <https://github.com/facebookincubator/cinder/issues?q=is%3Aissue+jit>
  - <https://github.com/facebookincubator/cinder/issues/29>
  - <https://github.com/facebookincubator/cinder/issues/87>
  - <https://github.com/facebookincubator/cinderx>
  - <https://raw.githubusercontent.com/facebookincubator/cinderx/HEAD/README.md>
  - <https://pypi.org/pypi/cinderx/json>
  - <https://raw.githubusercontent.com/brownplt/insta-model/HEAD/pj-7.1/paper.tex>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/facebookincubator/cinder`) · [data/wave12/enrich/raw/github_com_facebookincubator_cinder.json](../../../data/wave12/enrich/raw/github_com_facebookincubator_cinder.json) (enrichment confidence 0.8)

</details>
