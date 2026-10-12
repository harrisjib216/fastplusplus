# CPython tail-calling interpreter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Python-2.0` · 🟢 active

> Opt-in CPython 3.14+ interpreter loop in which opcodes tail-call each other; 3-5% faster than computed-goto (Clang 19), 15-20% faster than switch dispatch (MSVC).

| | |
|---|---|
| **Beats** | CPython computed-goto interpreter loop (same source, default dispatch) |
| **Claimed result** | After correction: geomean 3-5% faster on pyperformance (issue correction notice; Python 3.14 What's New says 3-5% depending on platform and architecture, baseline Python 3.14 built with Clang 19 without the new interpreter). The original claim of 10% geomean, up to 40% on Python-heavy benchmarks (gist: 1.10x geomean, best 1.46x on scimark_sor, unpickle_list 1.02x slower) was artificially boosted by an LLVM 19 bug that slowed the computed-goto baseline. |
| **Workload** | pyperformance suite, CPython built with clang-19, ThinLTO and PGO on AMD64 Ubuntu 22.04; per-benchmark results in gist https://gist.github.com/Fidget-Spinner/497c664eef389622d146d632990b0d21 (main 2228e92da31c vs tail-call 465467f47553, 2025-01-05). |
| **Metric** | throughput |
| **Hardware** | AMD64 machine, Ubuntu 22.04 (CPU model not on the page) |
| **Compiler and flags** | clang-19 (needs Clang 19+ on x86-64 and AArch64), ThinLTO and PGO; PGO is said to be especially crucial for the speedup. |
| **Adoption** | 77.5k stars (CPython) |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/python/cpython) · [benchmark](https://github.com/python/cpython/issues/128563) |

## Verdict

Ken Jin's first-party run (pyperformance, clang-19 with ThinLTO and PGO, AMD64 Ubuntu 22.04, CPU model not given) compared tail-call commit 465467f47553 with main 2228e92da31c from the same day. It found 1.10x geomean (52 faster, 1 slower: unpickle_list 1.02x; 8 not significant), later corrected to 3-5% after the LLVM 19 baseline regression was found. An independent run by Nelson Elhage (snippet only) found 1.03x on an i5-13500 and 1.00x on an Apple M1 against clang-18. Separately, What's New 3.15 reports 15-20% on Windows x86-64 with MSVC 18 against the switch-case loop on a Ryzen 7 5800X.

## Use it when

- You build your own CPython 3.14+ with Clang 19+ on x86-64 or AArch64 and use PGO (the only configuration the docs say was validated)
- Your platform's CPython is normally built with Clang (macOS/Xcode, FreeBSD, OpenBSD), where the computed-goto loop suffers from the LLVM 19 dispatch-merging regression
- Windows x86-64 on 3.15+: the python.org binaries already use it; when building yourself, VS 2026 (MSVC 18, v145) gives 15-20% over the switch-case loop
- You want a few percent on interpreter-bound pure-Python code without any compatibility cost; in the gist, numeric loops (scimark_\*) and unpack_sequence gained most

## Skip it when

- Linux distribution Python built with GCC: against GCC or clang-18 computed-goto builds the gain measured by Nelson Elhage was 1.00-1.03x (blog known from a search snippet only)
- Builds without PGO: the issue says the speedup is mediocre without it
- Python 3.13 or older, or compilers lacking both musttail and preserve_none (main's ceval_macros.h stops the build with #error; 3.14 rejects MSVC entirely)
- Builds with frame pointers (default in 3.15 per PEP 831) or other per-function hardening: issue #154124 measures 2.7% of geomean lost to frame pointers in the tail-calling interpreter vs 1.5% in the computed-goto one (i7-12700H, Clang 22); a fix is proposed but open
- You need multi-x speedups: PyPy, Cython, mypyc or Codon are in a different league; the 3.15 JIT adds a further 11-12% over this interpreter on AArch64 macOS

## How it is fast

The opcode handlers become separate functions marked with the preserve_none calling convention, and each one ends with a guaranteed tail call (musttail) through a function-pointer table: a 'goto with arguments'. Frame, stack pointer, tstate, next_instr, the dispatch table and oparg are passed as arguments, so they stay in registers across dispatches. The compiler can then allocate registers and lay out code per handler, instead of struggling with one giant switch or computed-goto function. On Clang 19 this also sidesteps an LLVM 19 change that merges all computed-goto dispatch jumps into one shared indirect branch.

## Compared with alternatives

Pick it when you must stay on upstream CPython with full C-extension and ABI compatibility and accept single-digit gains. Pyston gives more but is frozen at CPython 3.8. PyPy, GraalPy, Cython, mypyc and Codon can give multi-x speedups but mean a different runtime or a compile step. It stacks with them rather than replacing them.

## Integration

| | |
|---|---|
| **Form** | build option of the CPython interpreter (./configure --with-tail-call-interp; PCbuild\build.bat --tail-call-interp) |
| **Dependencies** | none beyond CPython's normal build; needs a C compiler with both musttail and preserve_none |
| **Minimum toolchain** | CPython 3.14+; Clang 19+ (x86-64, AArch64) on Unix; Visual Studio 2026 / MSVC 18 (PlatformToolset v145, _MSC_VER &gt;= 1950) on Windows for 3.15+; GCC only once it provides preserve_none (What's New 3.14 says a future GCC is expected to) |
| **Platforms** | x86-64 and AArch64 (Linux, macOS); Windows x86-64 with MSVC 18 from 3.15; python-build-standalone enables it for 3.14+ builds compiled with clang |
| **Thread safety** | Same as the regular interpreter (GIL or free-threaded build); a VS 2026 free-threaded build failure (#144549) was fixed in Feb 2026 |
| **Drop-in for the baseline** | partial — no Python-visible, C-API or ABI change, but you must rebuild CPython with a supported compiler and PGO, or use a distribution that enables it (python.org Windows x64 3.15, python-build-standalone 3.14+ clang builds) |

## Gotchas

- The headline numbers depend on the baseline. The issue's original 10% geomean (gist: 1.10x, best 1.46x on scimark_sor) came from comparing against a Clang 19 computed-goto build slowed by an LLVM 19 bug, and the authors withdrew it. What's New still names 'Python 3.14 built with Clang 19' as the baseline for its 3-5%, while issue #158283 (Sep 2026) shows plain Clang 19 computed-goto builds remain 7.7% slower than GCC 13 on Linux x86-64. It is not documented whether the 3-5% was measured against a repaired baseline.
- The Windows 15-20% (Ryzen 7 5800X, MSVC 18.1.1) is measured against the switch-case loop, because MSVC has no computed gotos. It is not comparable to the clang figures, where the baseline is computed-goto dispatch.
- Each opcode handler is a real function, so per-function prologue features (frame pointers, CET/BTI shadow stacks) cost more here than in a single-function loop (#154124). Profilers and debuggers show per-opcode _TAIL_CALL_\* frames instead of _PyEval_EvalFrameDefault.
- Enabling the flag on an unsupported toolchain is a trap: a 3.14.0rc2 build with GCC 14, PGO and --with-tail-call-interp hit 'RecursionError: Stack overflow (used 8161 kB)' during the PGO step (#138215, closed not planned). The pyconfig.h macro was renamed from Py_TAIL_CALL_INTERP (3.14) to _Py_TAIL_CALL_INTERP (main), which matters for build-detection scripts.

## Known shortcomings

- First-party only, no CPU model: the 10% geomean in issue #128563 was corrected to 3-5%, and even that is measured against a Clang 19 computed-goto build that an LLVM 19 bug slowed (issue #158283: 7.7% behind GCC 13 on x86-64, 11.4% behind on arm64 Xcode 16.4). Nelson Elhage's independent rerun found 1.03x on an i5-13500 and 1.00x on an M1 (snippet only). Needs Clang 19+ and PGO; the 15-20% figure in the 3.15 What's New is MSVC 18 versus switch-case.
- Enricher: What's New 3.14 names a Clang 19 build as the 3-5% baseline, yet issue #158283 (September 2026) shows plain Clang 19 computed-goto builds still 7.7% slower than GCC 13, and it is undocumented whether the 3-5% used the repaired baseline; the Windows 15-20% is against a switch-case loop. Issue #154124: frame pointers cost 2.7% with tail calls vs 1.5% with computed goto; issue #138215: a GCC 14 3.14.0rc2 build hit a C-stack RecursionError in the PGO step. python-build-standalone enables the flag for 3.14+ clang builds.

## Caveats and trade-offs

Baseline is CPython itself, so this is a delta against the incumbent's previous dispatch, not against another implementation. The headline 10%/40% numbers were withdrawn by the authors after an LLVM 19 bug was found; the corrected 3-5% geomean is the figure to use, and even that baseline is the Clang 19 computed-goto build, which issue #158283 measures as 7.7% slower than a GCC 13 build on Linux x86-64 and 11.4% slower with Xcode 16.4 on macOS arm64 (merged dispatch jumps). An independent measurement by Nelson Elhage (blog.nelhage.com, snippet only, blocked here) found only 1.03x on a Raptor Lake i5-13500 and 1.00x on an Apple M1 against a clang-18 computed-goto build. Needs Clang 19+ on x86-64/AArch64 and PGO; opt-in via --with-tail-call-interp. Separately, Python 3.15 What's New reports 15-20% pyperformance geomean on Windows x86-64 with MSVC 18 (Visual Studio 18.1.1) versus the switch-case interpreter on an AMD Ryzen 7 5800X (chart in faster-cpython/ideas results/5800X-msvc.pgo2-vs-msvc.pgo.tc.svg), and the official Windows 64-bit binaries now use the tail-calling interpreter. CPU model absent for the clang claim, so the tier is C.

Needs Clang 19 or newer (x86-64 and AArch64) and PGO to pay off per the issue.

## Maintenance

Actively maintained in upstream CPython (Python-2.0 licence, commits daily as of 2026-10-06). It is opt-in on Unix but already shipped in python.org Windows x64 3.15 binaries and in python-build-standalone clang builds for 3.14+, so the realistic decision is which CPython build to use, not whether to adopt a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Issue #128563 (first-party, Ken Jin) compares the tail-calling build against the default computed-goto build on pyperformance with clang-19, ThinLTO and PGO, and its correction notice gives the 3-5% geomean; benchmark code (pyperformance) is public but no CPU model is stated on the issue or in the linked gist, so it falls short of A. The only independent measurement found (Nelson Elhage's blog) is blocked here and known from search snippets only.
- **Verifier notes:** Claims match the issue (10% geomean / up to 40%, then the correction notice to 3-5%) and the gist (1.10x geomean, best 1.46x). Shortcomings: first-party only, no CPU model, corrected 3-5% still measured against the LLVM 19-regressed computed-goto baseline, independent rerun shows 1.00-1.03x. License corrected to SPDX Python-2.0 (the LICENSE file is the PSF License Version 2 stack with BeOpen, CNRI and CWI agreements plus 0BSD for documentation code; Python-2.0 is the OSI-approved identifier), usability stays copyable; stars 77.5k and last commit 2026-10-06 confirmed.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/python/cpython/issues/128563>
  - <https://gist.github.com/Fidget-Spinner/497c664eef389622d146d632990b0d21>
  - <https://github.com/python/cpython>
  - <https://github.com/python/cpython/commits/main>
  - <https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.14.rst>
  - <https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.15.rst>
  - <https://raw.githubusercontent.com/python/cpython/main/LICENSE>
  - <https://github.com/faster-cpython/ideas/tree/main/results>
  - <https://raw.githubusercontent.com/faster-cpython/ideas/main/results/5800X-msvc.pgo2-vs-msvc.pgo.tc.svg>
  - <https://github.com/python/cpython/issues/158283>
- **Sources the enricher read:**
  - <https://github.com/python/cpython/issues/128563>
  - <https://gist.github.com/Fidget-Spinner/497c664eef389622d146d632990b0d21>
  - <https://github.com/python/cpython/issues/158283>
  - <https://github.com/python/cpython/issues/154124>
  - <https://github.com/python/cpython/issues/138215>
  - <https://github.com/python/cpython/issues?q=is%3Aissue%20%22tail-calling%20interpreter%22>
  - <https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.14.rst>
  - <https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.15.rst>
  - <https://raw.githubusercontent.com/python/cpython/main/Doc/using/configure.rst>
  - <https://raw.githubusercontent.com/python/cpython/main/configure.ac>
  - <https://raw.githubusercontent.com/python/cpython/main/Python/ceval_macros.h>
  - <https://raw.githubusercontent.com/python/cpython/main/Python/ceval.c>
  - <https://raw.githubusercontent.com/python/cpython/main/Python/generated_cases.c.h>
  - <https://raw.githubusercontent.com/python/cpython/main/Include/pyport.h>
  - <https://raw.githubusercontent.com/python/cpython/main/PCbuild/build.bat>
  - <https://raw.githubusercontent.com/python/cpython/main/PCbuild/pyproject.props>
  - <https://raw.githubusercontent.com/python/cpython/main/PCbuild/readme.txt>
  - <https://raw.githubusercontent.com/python/cpython/3.14/Python/ceval_macros.h>
  - <https://raw.githubusercontent.com/python/cpython/3.14/Python/ceval.c>
  - <https://raw.githubusercontent.com/python/cpython/3.14/Include/pyport.h>
  - <https://raw.githubusercontent.com/python/cpython/3.14/configure.ac>
  - <https://raw.githubusercontent.com/faster-cpython/ideas/main/results/5800X-msvc.pgo2-vs-msvc.pgo.tc.svg>
  - <https://raw.githubusercontent.com/astral-sh/python-build-standalone/main/cpython-unix/build-cpython.sh>
  - <https://github.com/pyodide/pyodide/issues/6102>
  - WebSearch: 'Python 3.14 tail-calling interpreter vs GCC computed goto build benchmark nelhage clang 18' (blog.nelhage.com/post/cpython-tail-call snippet only; blog blocked)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/python/cpython`) · [data/wave12/enrich/raw/github_com_python_cpython.json](../../../data/wave12/enrich/raw/github_com_python_cpython.json) (enrichment confidence 0.8)

</details>
