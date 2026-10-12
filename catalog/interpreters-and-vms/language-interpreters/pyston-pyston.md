# Pyston

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Python-2.0 (CPython license stack: PSF License Version 2 with BeOpen, CNRI and CWI agreements; root LICENSE is CPython's)` · 🟡 stale

> CPython 3.8 fork plus pip-installable JIT module (DynASM baseline JIT, quickening, inline caches); about 10-30% faster than stock CPython 3.8.

| | |
|---|---|
| **Beats** | CPython 3.8 |
| **Claimed result** | Pyston 'full' (CPython 3.8.12 fork with DynASM JIT): 'roughly 30% faster than CPython on web serving macrobenchmarks'; Pyston 'lite' (JIT extension module): 'roughly 10% faster on macrobenchmarks'. |
| **Workload** | Web-serving macrobenchmarks (Pyston's python-macrobenchmarks suite). |
| **Metric** | throughput |
| **Adoption** | 2.5k stars |
| **Last commit** | 2024-08-12 |
| **Links** | [repository](https://github.com/pyston/pyston) · [benchmark](https://raw.githubusercontent.com/pyston/pyston/pyston_main/README.md) |

## Verdict

The README claims Pyston-full is 'roughly 30%' faster than CPython on web-serving macrobenchmarks and pyston-lite 'roughly 10%' (the lite PyPI text says 10-25%); no CPU, compiler, run count or CPython build is given. The in-repo harness behind such numbers runs flaskblogging, djangocms and kinto from pyston/python-macrobenchmarks against the distro python3.8 and reports post-warmup per-request means. A Pyston blog result known only from a search snippet (blog blocked here) reports +65% on pyperformance for Pyston-full 2.3.5 versus CPython 3.8 on an EC2 c6i.xlarge, against +26% for CPython 3.11rc2.

## Use it when

- Long-running web services (Django, Flask style) pinned to CPython 3.8 that cannot move to a newer CPython yet
- You want a JIT without rebuilding any C extensions: pyston-lite wheels exist for CPython 3.7-3.10 on Linux x86-64/aarch64 and macOS x86-64/arm64
- Interpreter-bound pure-Python code heavy on attribute access, global lookups and Python-level calls, which the inline caches and the dispatch removal target
- A drop-in change to throughput on a CPython 3.8 fleet is worth more than PyPy's larger gains, because PyPy means changing implementations

## Skip it when

- You are on CPython 3.11 or newer: nothing supports it (issue #298 about 3.11 support for pyston-lite has no reply), and newer CPython releases already include much of this work
- Anything that needs ongoing security or bug fixes: the project is declared no longer maintained, with the last code change in Feb 2023 and open crash reports (#299 GC crash, #307/#296/#295 recursion crashes, #310 _curses)
- pyston-lite on aarch64 servers: issue #305 reports SIGSEGVs on AWS Graviton with gevent, PyYAML and kafka-python, with no fix
- Windows (no builds or wheels), musl/Alpine (no musllinux wheels, #279), or systems that forbid writable+executable memory
- Workloads that spend their time inside C extensions (NumPy, regex, I/O): the JIT only speeds up Python bytecode execution

## How it is fast

A very cheap baseline JIT (Python/aot_ceval_jit.c) uses LuaJIT's DynASM to emit machine code straight from bytecode, with no IR. That removes dispatch overhead, and a 'deferred value stack' skips value-stack pushes and pops and some refcount updates. Hot opcodes call ahead-of-time generated, type-specialised C traces (e.g. float\*float), and the JIT adds inline caches for attribute and global lookups. A code object is JIT-compiled after about 200 calls or generator resumptions (JIT_MIN_RUNS = 2 x OPCACHE_MIN_RUNS). Pyston-full adds quickening, other CPython optimisations, and an LTO+PGO+BOLT, non-PIE build; pyston-lite is itself built with PGO, LTO and BOLT.

## Compared with alternatives

Pick Pyston only if you are stuck on CPython 3.7-3.10 and need a speedup without changing implementation or code. PyPy gives much larger gains on long-running pure-Python loops but is a separate runtime. Cython, mypyc and Codon require compiling or annotating your code. The CPython tail-calling interpreter needs Python 3.14 and gives 3-5%, but it is maintained.

## Integration

| | |
|---|---|
| **Form** | module (pyston-lite wheel for CPython 3.7-3.10) or full interpreter binary (pyston-full: deb, portable directory, conda, Docker image pyston/pyston) |
| **Dependencies** | none at runtime. Building from source needs clang, LuaJIT (DynASM preprocessing), and LLVM and BOLT submodules, with LLVM built twice for the PGO build |
| **Minimum toolchain** | Building needs GCC with the global-register-variable extension (aot_ceval_jit_helper.c, compiled without LTO), -std=gnu99, clang and luajit; lite builds need Python 3.7-3.10 headers. Pyston-full runs Python 3.8.12 code. |
| **Platforms** | JIT supports only x86-64 (System V ABI) and AArch64; Linux x86-64/aarch64 for pyston-full; pyston-lite wheels for Linux x86-64/aarch64 (manylinux2014) and macOS x86-64/arm64 (no cp37 arm64); BOLT step only on x86 Linux; no Windows |
| **Thread safety** | Same GIL model as CPython 3.8; JIT thread-safety beyond that is not documented |
| **Drop-in for the baseline** | partial — pyston-lite runs on stock CPython 3.7-3.10 and keeps binary wheels working; pyston-full is API- but not ABI-compatible with CPython 3.8, so every C extension must be recompiled (no prebuilt packages per the README) |

## Gotchas

- On Linux the JIT maps its code chunks PROT_READ|PROT_WRITE|PROT_EXEC (MAP_32BIT on x86-64; MAP_JIT only on macOS), so it needs writable+executable memory. It silently stops compiling once 100 MB of JIT code is used (JIT_MAX_MEM env var). Setting JIT_PERF_MAP runs system("rm -rf /tmp/perf_map").
- Harness flaw in the repo's own `make bench` (pyston/tools/benchmarks_runner): the baseline is whatever distro python3.8 is installed, not the same source built with the same flags. The printed geomean covers only flaskblogging and djangocms. In those benchmarks the requests client and the server both run on the interpreter under test. analyze.py's per-benchmark ratio divides the system build's all-iterations mean (warmup included) by a post-warmup mean for the other builds, a small bias toward the JIT builds; the geomean line uses post-warmup means for both.
- The project wiki's 'pyperformance on windows10' page compares native Windows CPython 3.8.10 with Pyston 2.3 inside WSL2 Ubuntu, i.e. two different operating systems. Its outliers (pathlib 10.19x, startup 4.13x) reflect the OS difference, not the JIT.
- Code can tell which variant is active with hasattr(sys, 'pyston_version_info') (full) or 'pyston_lite' in sys.modules (lite). CPython tracing support works by deoptimizing back to the interpreter, so profilers and debuggers run without the JIT's speedup.

## Known shortcomings

- First-party only: README claims 'roughly 30%' (full) and 'roughly 10%' (lite) over CPython with no CPU model, flags or CPython version; the baseline is CPython 3.8-era and the repo says it is no longer maintained (last code change February 2023). Root LICENSE is CPython's PSF stack, not Apache-2.0.
- Enricher: 'make bench' (pyston/tools/benchmarks_runner) uses the installed distro python3.8 as baseline rather than a same-source build, the geomean covers only flaskblogging and djangocms with the requests client and server both running on the interpreter under test, and analyze.py compares a system mean with warm-up against post-warm-up builds (small bias toward the JIT). The wiki pyperformance page compares Windows-native CPython 3.8.10 with Pyston under WSL2, so pathlib 10.19x and startup 4.13x reflect the OS difference. Linux JIT memory is mapped RWX; open unanswered crashes #305 (pyston-lite SIGSEGV on Graviton), #299 (GC); last pyston-lite PyPI release 2.3.5 (2022-09-26).

## Caveats and trade-offs

First-party README numbers ('roughly 30%' full, 'roughly 10%' lite) with no CPU, flags, CPython version or run counts; benchmark suite is public (pyston/python-macrobenchmarks, pyperformance manifest 'pyston_standard') but no result table is published in the repo. Baseline is CPython of the 3.7-3.10 era; newer CPython releases are not compared, and PyPy is not compared. Repository description says '(No longer maintained)'; the last code change was the Feb 28, 2023 merge of PR #301 and the Aug 12, 2024 commits only touch issue templates. Licence: the only LICENSE file is CPython's (PSF License Version 2 stack); no Apache-2.0 text was found (no pyston/ or pyston_lite LICENSE, JIT sources such as Python/aot_ceval_jit.c carry no header, PyPI pyston-lite lists no licence); the Apache-2.0 claim likely comes from the separate Pyston v1 repo. Pyston-full is API- but not ABI-compatible with CPython, so C extensions must be recompiled.

Pyston-full is a CPython 3.8.12 fork with a very-low-overhead JIT (DynASM), quickening, attribute caching and build-process improvements (PGO/BOLT); API compatible but not ABI compatible, so C extensions need recompiling; pyston-lite is a pip-installable JIT extension for CPython 3.7 to 3.10 that stays binary compatible.

## Maintenance

Declared no longer maintained (last code change Feb 2023, last pyston-lite release 2.3.5 on PyPI 2022-09-26) and frozen at CPython 3.8.12 (full) and 3.7-3.10 (lite) with open crash reports. The PSF/Python-2.0 licence makes it legally copyable, but it is a legacy option, not one to adopt for new deployments.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states Pyston full is 'roughly 30% faster than CPython on web serving macrobenchmarks' and pyston-lite 'roughly 10% faster on macrobenchmarks', with no CPU, compiler flags, CPython version or run counts; the benchmark code (pyston/python-macrobenchmarks submodule, run via pyperformance 'pyston_standard') is public but no result table or methodology accompanies the numbers, so first-party tier C.
- **Verifier notes:** README numbers match the record. Licence corrected from Apache-2.0 to the CPython Python-2.0/PSF-2.0 licence stack (OSI-approved, so usability stays copyable). maintenance_status kept 'abandoned' because the authors declare it no longer maintained, although the last commit (2024-08-12) is only about 2 years old; shortcomings: first-party vague percentages, no methodology, CPython-3.8-era baseline, unmaintained.
- **Fields the verifier corrected:** `license`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/pyston/pyston>
  - <https://github.com/pyston/pyston/commits>
  - <https://github.com/pyston/pyston/blob/pyston_main/LICENSE>
  - <https://raw.githubusercontent.com/pyston/pyston/HEAD/README.md>
  - <https://raw.githubusercontent.com/pyston/pyston/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pyston/pyston/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/pyston/pyston/HEAD/Python/aot_ceval_jit.c>
  - <https://raw.githubusercontent.com/pyston/pyston/HEAD/pyston/pyston_lite/setup.py>
  - <https://raw.githubusercontent.com/pyston/python-macrobenchmarks/HEAD/README.md>
  - <https://pypi.org/pypi/pyston-lite/json>
- **Sources the enricher read:**
  - <https://github.com/pyston/pyston>
  - <https://github.com/pyston/pyston/issues>
  - <https://github.com/pyston/pyston/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/pyston/pyston/issues/188>
  - <https://github.com/pyston/pyston/issues/298>
  - <https://github.com/pyston/pyston/issues/305>
  - <https://github.com/pyston/pyston/releases>
  - <https://github.com/pyston/pyston/wiki/pyperformance-on-windows10-64bit:-cpython-3.8.10-vs-pyston-v2.3-inside-WSL2>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/README.md>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/.gitmodules>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/LICENSE>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/Makefile>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/pyston/pyston_lite/setup.py>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/pyston/tools/benchmarks_runner/Makefile>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/pyston/tools/benchmarks_runner/analyze.py>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/pyston/benchmark_requirements.txt>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/pyston/run_profile_task.py>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/Python/aot_ceval_jit.c>
  - <https://raw.githubusercontent.com/pyston/pyston/pyston_main/Python/aot_ceval.c>
  - <https://raw.githubusercontent.com/pyston/python-macrobenchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/pyston/python-macrobenchmarks/HEAD/benchmarks/bm_flaskblogging/run_benchmark.py>
  - <https://raw.githubusercontent.com/pyston/python-macrobenchmarks/HEAD/benchmarks/bm_djangocms/run_benchmark.py>
  - <https://raw.githubusercontent.com/pyston/python-macrobenchmarks/HEAD/benchmarks/MANIFEST>
  - <https://pypi.org/pypi/pyston-lite/json>
  - <https://pypi.org/pypi/pyston-lite-autoload/json>
  - https://pybenchmarks.org/u64q/pyston.php (EGRESS_BLOCKED)
  - WebSearch: 'Pyston 2.3 vs CPython 3.11 benchmark pyperformance comparison' (blog.pyston.org and phoronix.com snippets only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/pyston/pyston`) · [data/wave12/enrich/raw/github_com_pyston_pyston.json](../../../data/wave12/enrich/raw/github_com_pyston_pyston.json) (enrichment confidence 0.75)

</details>
