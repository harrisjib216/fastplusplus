# SWIG

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0-or-later` · 🟢 active

> Interface-file-driven C/C++ binding generator; its -builtin and -fastproxy Python modes roughly halve SWIG's own default per-call overhead.

| | |
|---|---|
| **Beats** | SWIG's own default Python proxy-class wrappers (same tool, default code generation mode) |
| **Claimed result** | Default 0.15 / 0.26 / 0.32 us; -fastproxy 0.09 / 0.16 / 0.20 us (about 1.6-1.7x lower, derived from page data); -builtin 0.07 / 0.14 / 0.17 us (about 1.9-2.1x lower, derived from page data). Manual text: '-builtin ... significant performance improvement in the wrapped code'. |
| **Workload** | Per-call overhead, in microseconds, of calling three member functions of a trivial C++ class Go from Python through SWIG-generated wrappers: callme0() with no arguments, callme4() with four ints, callme8() with eight doubles; default proxy classes vs the -fastproxy option vs the -builtin option. |
| **Metric** | latency |
| **Adoption** | 6.3k stars; long-standing multi-language binding generator |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/swig/swig) · [benchmark](https://raw.githubusercontent.com/swig/swig/master/Doc/Manual/Python.html) |

## Verdict

SWIG's Python manual (section 35.6.5.1) lists per-call times for a trivial C++ class method with 0, 4 ints or 8 doubles: default proxy classes 0.15/0.26/0.32 us, -fastproxy 0.09/0.16/0.20 us, -builtin 0.07/0.14/0.17 us, i.e. about 1.6-1.7x and 1.9-2.1x lower (derived from page data). The baseline is SWIG's own default mode, with no CPU, Python version, compiler or harness stated and no comparison against another binding tool.

## Use it when

- You already ship SWIG bindings for Python and want lower call overhead without rewriting them: add -builtin (largest gain, about 2x on trivial calls per the manual) or -O/-fastproxy (about 1.6x) and rebuild.
- One interface file must feed several target languages (Python plus Java, C#, Go, Lua, Ruby and so on) and a per-language hand-written binder is not affordable.
- Wrapping large existing C or C++ APIs mostly from headers, where call overhead of 0.1-0.3 us is small next to the work done per call.
- Generated code must compile on old toolchains: the project aims for wrappers that build as C90 or C++98.

## Skip it when

- Python-only projects chasing the lowest per-call overhead: SWIG registers methods as METH_VARARGS and packs a tuple per call, while vectorcall-based binders (nanobind) are designed around PEP 590; no head-to-head numbers exist, so measure before choosing SWIG for speed.
- Builds that need the Python Stable ABI (Py_LIMITED_API, abi3 wheels): -builtin and -fastproxy (hence -O) do not use the limited API and fail with missing symbols; only the default, slower mode is limited-API clean.
- Code that raises wrapped C++ types as Python exceptions, relies on reverse binary operators (__radd__ and friends), Python annotations on the classes, or subclassing tricks: -builtin does not support these.
- Fine-grained GIL release everywhere: the -threads option adds per-call GIL handling that the manual measured at about 60% slower (9.6 s vs 15.5 s on profiletest.i), though that table dates from SWIG 1.3.28 in 2005.

## How it is fast

-fastproxy drops the Python-level def wrapper and installs the C wrapper directly as a method via PyInstanceMethod_New (_swig_new_instance_method), removing one Python frame per call. -builtin removes the pure-Python proxy class entirely: each C++ class becomes a CPython heap type derived from SwigPyObject, methods live in the type's method table, and C++ operators map to CPython type slots (nb_add, tp_richcompare and so on), which the manual says is much faster than named method dispatch. Argument unpacking uses SWIG's own SWIG_Python_UnpackTuple (fastunpack, on by default) instead of PyArg_UnpackTuple; methods are registered as METH_NOARGS, METH_O or METH_VARARGS, with no METH_FASTCALL or vectorcall path in Source/Modules/python.cxx.

## Compared with alternatives

Pick SWIG over nanobind when one interface must generate bindings for several languages or the wrapped API is C, and over LuaBridge, LuaBridge3 or sol2 when Lua is one target among many; for Python-only or Lua-only bindings where call overhead matters, nanobind (vectorcall) and sol2 (which ranks SWIG among slower Lua binders) are the speed picks.

## Integration

| | |
|---|---|
| **Form** | code generator (swig executable, built from source or packaged); output is a C/C++ source file plus a .py module compiled into a shared library |
| **Dependencies** | PCRE2 to build the swig tool; generated Python wrappers need only CPython headers and the SWIG runtime emitted into the wrapper |
| **Minimum toolchain** | Generated code targets C90 or C++98 (CHANGES 2023-04-27); Python &gt;= 3.5 (Python 2 dropped after SWIG 4.4); building SWIG itself needs GNU make |
| **Platforms** | any platform with a C/C++ compiler and the target language's headers (Linux, macOS, Windows including MinGW) |
| **Thread safety** | Wrappers do not release the GIL unless -threads or per-function thread features are used; -nogil (SWIG 4.4+) enables free-threaded CPython builds but thread safety of the wrapped C++ code is the user's responsibility |
| **Drop-in for the baseline** | partial — -fastproxy and -builtin are command-line switches on the same interface files, but -builtin changes the Python-visible API (no new_Foo functional interface, static members no longer under cvar, no exceptions or reverse operators), so callers may need edits |

## Gotchas

- -fastproxy is silently ignored for any method that carries extra proxy code such as %pythonprepend, so the speed-up is per method, not per module; it also hides docstrings, annotations and default argument values unless -olddefs is added, which makes module import slower.
- Harness flaw: the speed table (callme0/4/8 microseconds) has no harness, hardware, Python version, compiler or repeat count, and its benchmark is not in the repository. The only performance suite ever shipped (Examples/python/performance, added with -builtin in 2011) was Python-2-only (print statement, imp, time.clock), timed a 10M-iteration for-loop including loop overhead, and was deleted on 2025-10-22 as 'out of date and non-functional' (issue #3242, commit 1db0c66).
- -builtin with several SWIG modules that share types needs an unambiguous dependency graph declared with %import, or base classes may not be initialised before derived ones.
- -dirvtable (faster director dispatch) leaks memory: the manual says the pseudo vtable is per-object and never freed.

## Known shortcomings

- Manual table compares only SWIG's own modes (default 0.15/0.26/0.32 us; -fastproxy 1.6-1.7x and -builtin 1.9-2.1x lower, derived from page data) with no incumbent, harness or methodology (Examples/python/performance is 404); -fastproxy drops docstrings, annotations and defaults without -olddefs, and -threads is 60% slower. GPL-3.0 tool with permissive Lib and Examples.
- Enricher: the speed table (default vs -fastproxy vs -builtin, us per call) has no harness, CPU, Python version or repeat count; the only perf suite ever shipped (Examples/python/performance) was Python 2 only and was deleted 2025-10-22 as non-functional (issue #3242, commit 1db0c66); the -threads table dates to SWIG 1.3.28 (2005); wrappers use METH_VARARGS tuple unpacking (no METH_FASTCALL or vectorcall); -builtin and -fastproxy break Py_LIMITED_API; -dirvtable leaks memory.

## Caveats and trade-offs

The baseline is SWIG's own default proxy-class mode, not another binding tool: the manual makes no numeric comparison against SIP, pybind11, Boost.Python, nanobind or Cython, and two WebSearches for third-party SWIG call-overhead numbers found none (nanobind's and pybind11's benchmark pages do not include SWIG). The manual itself says the overhead is 'reduced slightly' with -fastproxy. No hardware, compiler, Python version, repeat count or harness is given for the table; no benchmark script was found for it (Examples/python/performance returns 404). Trade-offs from the same manual: -fastproxy (also turned on by -O) hides docstrings, Python annotations and default argument values in the generated proxy class unless -olddefs is added, it is silently ignored for methods that use %pythonprepend or similar additions, and -builtin and -fastproxy do not work with Py_LIMITED_API. Another table in the same manual shows the -threads option slowing the profiletest.i run (single threaded 9.6 s vs fully multithreaded 15.5 s, about 60% slower). LICENSE: the SWIG tool is GPL-3.0-or-later with portions under LICENSE-UNIVERSITIES; the Lib and Examples directories (the runtime code copied into generated wrappers) are under a permissive grant ('copy, modify, distribute ... without restriction'). The lead's statement that the generated output is not covered by the GPL was not independently verified here.

-fastproxy makes generated proxy classes less user-friendly (docstrings, annotations and default arguments are not visible) and is ignored for methods with %pythonprepend-style extra code; -builtin replaces proxy classes with built-in types and does not use the Python limited API. Both are Python-only options; the per-call numbers are for Python, other target languages have no comparable table.

## Maintenance

Actively maintained (4.5.1 released 2026-09-04, 4.6.0 in progress with commits on 2026-10-07); the swig tool is GPL-3.0-or-later, but Lib and Examples are under a permissive grant and the Preface states generated code can be distributed under terms of the user's choice, so it is safe to use in proprietary builds.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Doc/Manual/Python.html section 35.6.5.1 has a first-party table of per-call timings in microseconds (callme0/4/8: Default 0.15/0.26/0.32, -fastproxy 0.09/0.16/0.20, -builtin 0.07/0.14/0.17), with no harness, hardware, compiler, Python version or repeat count stated. The comparison is between SWIG's own code-generation modes, not against another binding tool, so it is tier C.
- **Verifier notes:** Numbers and the 1.6-1.7x (-fastproxy) and 1.9-2.1x (-builtin) ratios check out as derived from page data. Shortcoming to record: off-baseline (internal mode comparison only, no incumbent such as pybind11 or Cython measured), no methodology or harness for the table, and -fastproxy loses docstrings/annotations/defaults without -olddefs. Metadata confirmed: 6.3k stars, 1.3k forks, not archived, not a fork, last commit 2026-10-07 on master, GPL-3.0 plus LICENSE-UNIVERSITIES plus permissive Lib/Examples terms.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-100 (wave 12); enricher w12 pair-010
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/swig/swig/master/Doc/Manual/Python.html>
  - <https://raw.githubusercontent.com/swig/swig/master/LICENSE>
  - <https://github.com/swig/swig>
  - <https://github.com/swig/swig/commits>
  - <https://github.com/swig/swig/tree/master/Examples/python/performance>
- **Sources the enricher read:**
  - <https://github.com/swig/swig>
  - <https://raw.githubusercontent.com/swig/swig/master/Doc/Manual/Python.html>
  - <https://raw.githubusercontent.com/swig/swig/master/Doc/Manual/Preface.html>
  - <https://raw.githubusercontent.com/swig/swig/master/README>
  - <https://raw.githubusercontent.com/swig/swig/master/LICENSE>
  - <https://raw.githubusercontent.com/swig/swig/master/CHANGES>
  - <https://raw.githubusercontent.com/swig/swig/master/CHANGES.current>
  - <https://raw.githubusercontent.com/swig/swig/master/Lib/python/pyrun.swg>
  - <https://raw.githubusercontent.com/swig/swig/master/Lib/python/builtin.swg>
  - <https://raw.githubusercontent.com/swig/swig/master/Lib/python/pyinit.swg>
  - <https://raw.githubusercontent.com/swig/swig/master/Source/Modules/python.cxx>
  - <https://raw.githubusercontent.com/swig/swig/v4.3.1/Examples/python/performance/harness.py>
  - <https://raw.githubusercontent.com/swig/swig/v4.3.1/Examples/python/performance/Makefile>
  - <https://raw.githubusercontent.com/swig/swig/v4.3.1/Examples/python/performance/func/runme.py>
  - <https://raw.githubusercontent.com/swig/swig/v4.3.1/Examples/python/performance/func/Makefile>
  - <https://raw.githubusercontent.com/swig/swig/v4.3.1/Examples/python/performance/func/Simple.i>
  - <https://github.com/swig/swig/issues?q=is%3Aissue+performance+python>
  - <https://github.com/swig/swig/issues/3242>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/swig/swig`) · [data/wave12/enrich/raw/github_com_swig_swig.json](../../../data/wave12/enrich/raw/github_com_swig_swig.json) (enrichment confidence 0.65)

</details>
