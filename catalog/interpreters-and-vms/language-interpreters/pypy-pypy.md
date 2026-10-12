# PyPy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Python (RPython) with C` · `MIT` · 🟢 active

> Alternative Python interpreter with a meta-tracing JIT; runs pure-Python CPU-bound code 1.5-42x faster than CPython.

| | |
|---|---|
| **Beats** | CPython 3.14.6 (kostya/benchmarks); CPython 3.11.7 (plb2) |
| **Claimed result** | kostya/benchmarks: bench.b 9.398 s vs CPython 61.009 s (about 6.5x, derived from page data); matmul 3.263 s vs 136.267 s (about 42x, derived from page data); primes 0.617 s vs 1.725 s (about 2.8x, derived from page data); JSON 0.606 s vs 0.936 s (about 1.5x, derived from page data). base64 is slower: 3.534 s vs 3.099 s. plb2 (Apple M1, PyPy 7.3.14 vs CPython 3.11.7): nqueen 6.91 s vs 159.97 s, matmul 4.89 s vs 117.81 s, sudoku 8.82 s vs 52.88 s, bedcov 6.27 s vs 42.84 s. |
| **Workload** | kostya/benchmarks (Brainfuck bench.b, matmul, primes, JSON, base64) and attractivechaos/plb2 (nqueen, matmul, sudoku, bedcov), same Python source run under CPython and PyPy. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) E-2324G, Docker (Debian forky/sid) per README Environment section; base image and interpreter builds in docker/Dockerfile; plb2 numbers on Apple M1 MacBook Pro |
| **Compiler and flags** | PyPy 7.3.23 (Python 3.11.15 compatible) release tarball run as `pypy file.py` vs CPython 3.14.6 (docker/Dockerfile); plb2 used PyPy 7.3.14 vs CPython 3.11.7. |
| **Adoption** | 1.8k stars; the GitHub repository has been PyPy's canonical repository and issue tracker since the December 2023 move from Heptapod |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/pypy/pypy) · [benchmark](https://github.com/kostya/benchmarks) |

## Verdict

kostya/benchmarks ran the same Python files under PyPy 7.3.23 (Python 3.11.15) and Debian CPython 3.14.6 in Docker on an Intel Xeon E-2324G, reporting medians: Brainfuck bench.b 9.398 s vs 61.009 s (6.5x), matmul n=1500 3.263 s vs 136.267 s (42x), primes 0.617 s vs 1.725 s (2.8x), JSON 0.606 s vs 0.936 s (1.5x), while base64 was slower (3.534 s vs 3.099 s); ratios derived from page data. attractivechaos/plb2 on an Apple M1 MacBook Pro measured PyPy 7.3.14 against CPython 3.11.7 at 6.91 vs 159.97 s (nqueen, 23x), 4.89 vs 117.81 s (matmul, 24x), 8.82 vs 52.88 s (sudoku, 6.0x) and 6.27 vs 42.84 s (bedcov, 6.8x), derived from page data.

## Use it when

- Long-running pure-Python CPU-bound code (interpreters, parsers, simulations, numeric loops over lists or array.array): kostya matmul ran 42x and the Brainfuck interpreter 6.5x faster than CPython 3.14.6.
- Batch jobs and services that run for seconds or longer, so the JIT warm-up is amortised; the PyPy FAQ says even simple comparisons should run at least one second.
- Code that allocates many small short-lived objects in hot loops, where allocation removal and the nursery GC pay off.
- Projects whose native dependencies use cffi or are pure Python, so nothing goes through cpyext.

## Skip it when

- Short scripts, CLI tools and test suites: the FAQ warns of a very high JIT warm-up cost and that tests run once and are a bad case for JIT compilers.
- Workloads dominated by C-implemented library calls: kostya base64 is slower on PyPy (3.534 s vs 3.099 s for CPython), and the FAQ notes PyPy only speeds up code written in Python.
- Stacks built on CPython C extensions (NumPy, pandas, many binary wheels): cpyext emulates refcounting and is documented as slow, and wheel availability for PyPy lags.
- Memory-constrained deployments: base RSS is about 60 MiB versus about 11 MiB for CPython in the kostya tables.
- Code that needs Python 3.13+ features or a free-threaded build: PyPy tracks 3.11 (last supported in 8.0.x) and 3.12 (beta), and keeps a GIL.

## How it is fast

The interpreter is written in RPython, and the RPython toolchain generates a meta-tracing JIT from it: hot loops are recorded as linear traces of interpreter operations, then optimised (guards, constant folding, allocation removal of short-lived objects via escape analysis) and compiled to machine code. Object-model tricks the JIT exploits include map dicts (hidden-class style instance layouts), dict and list strategies that store unboxed ints or floats, and method caching. Memory management is incminimark, an incremental generational moving GC with bump-pointer nursery allocation instead of reference counting.

## Compared with alternatives

Pick PyPy over Codon, Cython or mypyc when you want to keep running ordinary, untyped Python source unchanged rather than compile a typed subset or an extension module; pick it over GraalPy when you want the faster and lighter runtime, since GraalPy mostly lost to PyPy3 in the independent kostya/jit-benchmarks suite.

## Integration

| | |
|---|---|
| **Form** | standalone interpreter binary (release tarballs, distro packages); not a library |
| **Dependencies** | none for the release binaries (glibc 2.28+ for Linux tarballs since v8.0.0); building from source needs a Python 2.7 host (PyPy2.7 recommended) with cffi, a C compiler, libffi, zlib, bzip2 and other dev packages |
| **Minimum toolchain** | Runs Python 2.7, 3.11 or 3.12 (beta) code; a source translation takes about 20 minutes and at least 6 GB RAM on 64-bit per pypy/doc/build.rst |
| **Platforms** | Binaries for x86-64 and x86-32 Linux, macOS x86-64 and arm64, Windows 64-bit, aarch64 Linux; PPC64 (BE and LE), ARM32, RISC-V RV64IMAFD and s390x Linux supported without official binaries |
| **Thread safety** | Has a GIL like default CPython; threads do not run Python code in parallel (the STM no-GIL variant is experimental and not shipped). |
| **Drop-in for the baseline** | partial: pure-Python code runs unchanged, but the language version lags CPython, C extensions go through slower cpyext, and GC semantics differ (no refcounting) |

## Gotchas

- No reference counting: files and sockets are not closed when they go out of scope (written data can sit in buffers), memoryviews are not released promptly, and sys.getrefcount does not exist; use with-blocks and explicit close().
- The GitHub default branch `main` is the Python 2.7 interpreter (CPYTHON_VERSION 2.7.18); the Python 3 interpreters live on the py3.11 and py3.12 branches.
- Some operations are much slower than CPython: `del` of a module or class attribute (documented), closures with keyword-only defaults (#5438 open), list copying (#5315 open); 229 issues match 'slower than CPython', many fixed (e.g. bytearray(n) 28x slower, #5567).
- Benchmark harness note: kostya/benchmarks times only the region between in-process start/stop notifications, excluding interpreter startup, file loading and a short self-test that runs the same code path, which helps PyPy on the sub-second JSON and primes tests; plb2 timed wall clock with startup, but its slow implementations (CPython included) were timed once with `time` rather than hyperfine. All five kostya scripts verify their output before timing; no correctness bug was found.

## Known shortcomings

- Loses base64 to CPython on kostya/benchmarks (3.534 vs 3.099 s) and its base RSS is about 60 MiB against 11 MiB; RPython/C runtime, not an embeddable C++ library. GitHub has been the canonical repo since December 2023.
- Enricher: the kostya clock skips startup, file loading and the self-test, which helps PyPy on the sub-second JSON and primes rows; plb2 timed the slow rows (CPython included) once with time rather than hyperfine. PyPy 8.0.0 (September 2026) adds a Python 3.12 beta, with 3.11 the last fully supported line; the GitHub default branch is Python 2.7.

## Caveats and trade-offs

PyPy is slower than CPython on the kostya base64 test (3.534 s vs 3.099 s), so the win is workload dependent. PyPy uses more memory: base RSS about 60 MiB vs about 11 MiB for CPython in the kostya tables (JSON: 280.66 + 125.44 MiB vs 121.30 + 325.88 MiB). PyPy 7.3.23 implements Python 3.11 while the CPython baseline is 3.14.6. Whether the Debian CPython build has its experimental JIT enabled was not checked. Ratios are derived from medians on one machine per suite. Core is MIT; the bundled stdlib in lib-python is under the PSF license.

Drop-in CPython alternative but lags CPython versions (3.11 compatible here vs 3.14), C extensions go through a slower cpyext layer, warm-up is needed and memory use is higher (bench.b: 60.19 + 30.10 MiB vs 11.38 + 0.00 MiB for CPython in the kostya tables); a 2018 hello-world startup test (bdrung/startup-time, Intel i5-2400S) put PyPy 5.8.0 at 27.53 ms vs 25.84 ms for CPython 3.6.3.

## Maintenance

Very active (last commit 2026-10-05; v8.0.0 released 2026-09 with Python 3.12 beta and cp312-abi3 groundwork, v8.0.1 bug-fix release in preparation), MIT-licensed core with PSF-licensed lib-python, and installable as a binary, so adoption costs a runtime swap rather than a build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification A, tier now A.
- **Tier reason:** kostya/benchmarks runs the same Python files under both interpreters (brainfuck/bf3.py, matmul/matmul.py, primes/primes.py, json/test.py, base64/test.py via PYPY3_RUN and PYTHON3_RUN in common/commands.mk), with the PyPy 7.3.23 release tarball and Debian CPython in docker/Dockerfile and the Xeon E-2324G CPU stated; attractivechaos/plb2 independently confirms on an Apple M1 with public code and versions.
- **Verifier notes:** All kostya and plb2 numbers match their rows; same source files run under both interpreters. Corrected the stale claim that GitHub is a mirror of Heptapod (PyPy moved its canonical repo to GitHub in December 2023; snippet from the pypy.org announcement plus GitHub PR merges in the commit log). Metadata checked: MIT (lib-python PSF), 1.8k stars, last commit 2026-10-05; the spec lists PyPy as a baseline of the 'jits' category, here it is filed under language-interpreters against CPython.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/primes/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/base64/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/README.md>
  - <https://github.com/pypy/pypy>
  - <https://github.com/pypy/pypy/commits/main>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/README.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/pypy/pypy>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/README.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/pypy/doc/cpython_differences.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/pypy/doc/faq.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/pypy/doc/build.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/pypy/doc/index-of-release-notes.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/pypy/doc/release-v8.0.0.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/pypy/doc/release-v8.0.1.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/pypy/doc/interpreter-optimizations.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/pypy/doc/gc_info.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/HEAD/rpython/doc/jit/overview.rst>
  - <https://raw.githubusercontent.com/pypy/pypy/main/pypy/module/sys/version.py>
  - <https://raw.githubusercontent.com/pypy/pypy/py3.11/pypy/module/sys/version.py>
  - <https://raw.githubusercontent.com/pypy/pypy/py3.12/pypy/module/sys/version.py>
  - <https://github.com/pypy/pypy/issues?q=is%3Aissue+slower+than+CPython>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/docker/Dockerfile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/bf3.py>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/matmul.py>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/matmul/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/primes/primes.py>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/primes/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/test.py>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/json/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/base64/test.py>
  - <https://raw.githubusercontent.com/kostya/benchmarks/HEAD/base64/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/pypy/pypy`) · [data/wave12/enrich/raw/github_com_pypy_pypy.json](../../../data/wave12/enrich/raw/github_com_pypy_pypy.json) (enrichment confidence 0.85)

</details>
