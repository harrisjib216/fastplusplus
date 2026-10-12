# Nuitka

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (compiler generating C)` · `AGPL-3.0` · 🟢 active

> Python-to-C compiler that runs unmodified CPython 2.6-3.14 code; about 3.4x CPython 2.7 on pystone, far less on typical code.

| | |
|---|---|
| **Beats** | CPython 2.7 (Debian build) running pystone |
| **Claimed result** | README pystone table (pystones/second, best run): Debian Python 2.7 uncompiled 137497.87 vs 460995.20 compiled with LTO (3.353x) and 503681.91 with PGO (3.663x); Nuitka Python 2.7 uncompiled 144074.78 (1.048x) vs 479271.51 LTO (3.486x) and 511247.44 PGO (3.718x). The page's factors are all relative to uncompiled Debian Python 2.7; relative to its own uncompiled run the Nuitka Python 2.7 rows are about 3.33x (LTO) and 3.55x (PGO) (derived from page data). |
| **Workload** | pystone, best of 100-1000 runs, uncompiled vs compiled with --lto=yes (and --pgo-c); script tests/benchmarks/pystone.py in the repo. |
| **Metric** | throughput |
| **Compiler and flags** | nuitka --lto=yes --pgo-c (and --static-libpython=yes for the Python 3 variant); C compiler version for the table not stated (README says GCC 5.1+, Clang or MSVC 2022+ supported). |
| **Adoption** | 15.2k stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/Nuitka/Nuitka) · [benchmark](https://github.com/Nuitka/Nuitka) |

## Verdict

The only published numbers are first-party. Nuitka's README table runs pystone under Debian's CPython 2.7 and takes the best of repeated runs: 137,498 pystones/s uncompiled, 460,995 compiled with --lto=yes (3.35x) and 503,682 with --lto=yes --pgo-c (3.66x). A second row labelled 'Nuitka Python 2.7', not explained in the README, reaches 3.72x of the Debian baseline. No CPU, C compiler version or Nuitka version is given, and there are no Python 3 results.

## Use it when

- Pure-Python, call-heavy CPU code that you cannot annotate or rewrite. In the independent python-speed suite on CPython 3.9.4, Nuitka halved the recursive fibonacci time (1199 ms vs 2417 ms).
- Shipping a Python application as a standalone folder or single-file binary, where some speed-up comes as a side benefit of the build.
- Compiling one hot module into an extension module (--mode=module) and leaving the rest of the program interpreted.
- Code that depends on CPython C extensions (NumPy and similar) and therefore cannot move to PyPy or a restricted-subset compiler.

## Skip it when

- Workloads dominated by C-library calls, regex, string handling or I/O. In python-speed, regex was slightly slower than CPython 3.9.4 (2407 ms vs 2335 ms) and string/memory only 5% faster. In the Shed Skin README, Nuitka 0.6.16 took 11.4 s on the sieve example, the same as CPython 3.11.0.
- When you can add type information: Cython, mypyc, Codon or Shed Skin give much larger gains on numeric loops, and PyPy is faster on long-running pure-Python code.
- Fast edit-compile cycles or large codebases on small machines: C compilation of whole programs is slow and can exhaust RAM, and the README has a whole section on compiler out-of-memory failures and on --low-memory and --jobs.
- Code that needs pdb or tracing, reads co_code, or builds new functions from a function's __code__ (compiled functions have no bytecode).

## How it is fast

Whole-module optimisation runs on a node tree before C code generation. It does constant propagation and folding, function inlining, and removes frame setup where no frame is needed. Objects are still PyObject\*, but generic C-API calls are replaced with specialised helpers per operand type, for example BINARY_OPERATION_\* and RICH_COMPARE_\* families and exact-type iterator fast paths. A few native C types (nuitka_bool, nuitka_void) skip boxing; full C-level type inference is still listed as 'in progress'. Gains on top come from C-compiler LTO and PGO (--lto=yes, --pgo-c) and from static linking of libpython.

## Compared with alternatives

Pick Nuitka over Cython, mypyc, Codon or Shed Skin when the code must stay unmodified, unannotated, full-language Python and you also want a distributable binary. Pick it over PyPy or GraalPy when you depend on CPython C extensions or the exact CPython semantics, and accept a much smaller speed-up than those give on pure-Python hot loops.

## Integration

| | |
|---|---|
| **Form** | Python package (pip install Nuitka) that emits executables or CPython extension modules |
| **Dependencies** | CPython of the same version (or a standalone/onefile build that bundles it; Anaconda and Homebrew Python work, Windows Store Python and macOS pyenv do not); a C11 compiler (gcc 5.1+, clang, MSVC 2022+, the MinGW64 that Nuitka downloads, or zig); Scons is used internally (Python 3.4 needs a second Python for it); optional ccache and zstandard |
| **Minimum toolchain** | CPython 2.6/2.7 or 3.4-3.14; gcc 5.1+ (g++ 4.4+ as C++03 fallback) or MSVC 2022+; MinGW64 does not work with Python 3.13+ |
| **Platforms** | Linux, FreeBSD, NetBSD, macOS, Windows (32-bit, 64-bit, ARM); tested on x86, x86_64 and arm |
| **Thread safety** | not documented separately; compiled code runs inside the CPython runtime and follows its threading model |
| **Drop-in for the baseline** | partial: it runs unmodified Python source and keeps C extensions working, but the output is a binary or extension module. Extension modules must keep their file name and load only into the same CPython version, 'python -m compiled_module' fails, co_code is empty and pdb cannot trace compiled functions. |

## Gotchas

- Harness flaw in the published table: the compiled Python 2 command is 'for i in {1..100}; do BENCH=1 ./pystone.bin ; done | sort -n | head -rn 1'. head has no -r option, so it prints nothing. Read as 'head -n 1' after an ascending sort, it would pick the slowest compiled run, not the best one used for the uncompiled row. The text says 1000 runs while the loop runs 100, so the table cannot have come from these commands as printed. No CPU, C compiler version or Nuitka version is given, and the Python 3 commands have no published results.
- pystone flatters a constant-propagating compiler. Its timed loop (tests/benchmarks/pystone.py, Proc0) contains a dead store ('IntLoc3 = 5 \* IntLoc1 - IntLoc2' is overwritten on the next line) and an inner while loop over constants (IntLoc1 = 2, IntLoc2 = 3), which CPython must execute and a constant-propagating compiler can fold (not checked whether Nuitka does). The score also subtracts an empty-loop 'nulltime' that each build times itself. Expect the 3.4x to shrink sharply on real code (about 1.18x total in python-speed).
- Licence: the compiler is AGPL-3.0. LICENSE-RUNTIME.txt grants an exception only for the Target Code (your compiled program linked with Nuitka's runtime library), so modified versions of the compiler itself stay AGPL.
- Builds without --deployment keep debugging safeguards on (for example fork-bomb detection on self-execution). Code that clones functions through types.FunctionType(func.__code__, ...) breaks and must use the compiled function's clone() method instead.

## Known shortcomings

- Pystone on Python 2.7 only, no CPU or compiler version; the record's 3.49x and 3.72x were factors against Debian's uncompiled build, 3.33x and 3.55x against Nuitka's own uncompiled run (derived from page data). Shed Skin's sieve shows Nuitka 0.6.16 equal to CPython 3.11 (11.4 s). AGPL-3.0 with runtime exception.
- Enricher: the compiled pystone command 'sort -n | head -rn 1' is invalid (read as head -n 1 it would pick the slowest compiled run), the text says 1000 runs while the loop runs 100, and the timed pystone loop has a dead store plus a constant inner loop that favours constant folding. Independent vprelovac/python-speed (CPython 3.9.4): total 7841 ms vs 9274 ms, about 1.18x, with regex slower.

## Caveats and trade-offs

The published table is pystone on Python 2.7 only; the README says Python 3 measurements will follow later, and the pystone3 commands it shows have no published results. pystone is a synthetic benchmark. No CPU model and no C compiler version for the table (a separate README section says clang6 beat gcc-6.3 slightly on Linux and MinGW64 beat MSVC by about 20% on Windows). The documented commands contain a typo for the compiled Python 2 run ('sort -n | head -rn 1', head has no -r option) and the text says 1000 runs while that loop runs 100, so the table cannot have come from the commands exactly as printed. An independent timing in the Shed Skin README shows Nuitka 0.6.16 at 11.4 s on the sieve example (n=100000000), identical to CPython 3.11.0 (11.4 s) and only slightly faster than CPython 3.10.6 (13.4 s), so gains on other workloads can be near zero. Licence is AGPL-3.0 with a runtime exception (LICENSE-RUNTIME.txt) covering the compiled output.

Compiles Python to C and still depends on a Python runtime; speedups are modest on dynamic code; needs a C compiler; AGPL-3.0 licence (check implications for compiled output).

## Maintenance

Very active: develop branch committed 2026-10-05, PyPI 4.2.2 released 2026-09-22, 15.2k stars. Usable today on CPython 2.6-2.7 and 3.4-3.14 under AGPL-3.0 with a runtime exception for compiled output; some deployment features (data-file embedding, container builds) are commercial-only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Performance' chapter has a first-party pystone table against uncompiled Debian Python 2.7 with public benchmark code (tests/benchmarks/pystone.py) and Nuitka flags (--lto=yes --pgo-c), but no C compiler version or CPU model, so C.
- **Verifier notes:** Numbers verified in README Performance chapter and Shed Skin independent timing confirmed; the record's 3.49x/3.72x for the Nuitka Python rows are the page's factors against Debian uncompiled, corrected. Tier C stays; metadata checked (AGPL-3.0 with runtime exception, 15.2k stars, develop branch last commit 2026-10-05, active).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Nuitka/Nuitka>
  - <https://github.com/Nuitka/Nuitka/commits>
  - <https://raw.githubusercontent.com/Nuitka/Nuitka/HEAD/README.rst>
  - <https://raw.githubusercontent.com/Nuitka/Nuitka/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/Nuitka/Nuitka/HEAD/tests/benchmarks/pystone.py>
  - <https://raw.githubusercontent.com/Nuitka/Nuitka/HEAD/tests/benchmarks/pystone3.py>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/Nuitka/Nuitka>
  - <https://raw.githubusercontent.com/Nuitka/Nuitka/HEAD/README.rst>
  - <https://raw.githubusercontent.com/Nuitka/Nuitka/HEAD/LICENSE-RUNTIME.txt>
  - <https://raw.githubusercontent.com/Nuitka/Nuitka/HEAD/tests/benchmarks/pystone.py>
  - <https://raw.githubusercontent.com/Nuitka/Nuitka/HEAD/tests/benchmarks/pystone3.py>
  - <https://raw.githubusercontent.com/Nuitka/Nuitka/HEAD/Developer_Manual.rst>
  - <https://github.com/Nuitka/Nuitka/issues?q=is%3Aissue+slower>
  - <https://pypi.org/pypi/Nuitka/json>
  - <https://raw.githubusercontent.com/vprelovac/python-speed/HEAD/README.md>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/nuitka/nuitka`) · [data/wave12/enrich/raw/github_com_nuitka_nuitka.json](../../../data/wave12/enrich/raw/github_com_nuitka_nuitka.json) (enrichment confidence 0.75)

</details>
