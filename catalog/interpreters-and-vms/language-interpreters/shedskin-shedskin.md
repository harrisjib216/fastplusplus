# Shed Skin

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (transpiler) generating C++; runtime library in C++` · `GPL-3.0 (compiler); MIT/Expat, BSD-3-Clause and BSL-1.0 for the C++ runtime library; examples individually licensed` · 🟢 active

> Ahead-of-time transpiler from implicitly statically typed Python 3 to C++; README claims 12x median over CPython 3.14.

| | |
|---|---|
| **Beats** | CPython 3.14 (headline claim); CPython 3.10.6 and 3.11.0 in the sieve timing |
| **Claimed result** | Typical speedup of 1-100x over CPython 3.14 (average 20x, median 12x) across the examples. Sieve n=100000000: CPython 3.10.6 13.4 s, CPython 3.11.0 11.4 s, Shed Skin 0.9.9 1.9 s (--int32) and 1.8 s (--int32 --nowrap --nobounds), about 6-7x (derived from page data). |
| **Workload** | Over 80 non-trivial example programs (more than 25,000 lines) in the examples directory, plus a sieve example with n=100000000 timed against several Python implementations. |
| **Metric** | throughput |
| **Compiler and flags** | Shed Skin flags --int32 (and --int32 --nowrap --nobounds) for the sieve runs; C++ compiler, version and optimization flags not stated for either measurement (Shed Skin takes its C++ flags from the FLAGS files in its installation, per docs/documentation.md). |
| **Adoption** | 1.0k stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/shedskin/shedskin) · [benchmark](https://github.com/shedskin/shedskin) |

## Verdict

First-party README numbers: across the 80+ programs in examples/ the compiled code is 1-100x faster than CPython 3.14 (average 20x, median 12x), with no per-program table, script, CPU or compiler stated; a sieve run (labelled n=100000000) took 13.4 s on CPython 3.10.6, 11.4 s on 3.11.0, 5.8 s on PyPy 3.9 and 1.9 s on Shed Skin 0.9.9 with --int32 (1.8 s adding --nowrap --nobounds), about 6-7x (derived from page data) on unstated hardware.

## Use it when

- A self-contained CPU-bound kernel of a few hundred to a few thousand lines (simulations, search, ray tracers, emulators, compressors) that you want 10x+ faster without rewriting it in C++.
- You want to keep CPython as the main interpreter and call the hot part as an extension module, passing scalars, builtin containers or instances of your own classes.
- Code that is already effectively monomorphic and uses only builtins plus modules such as math, random, re, collections, heapq, itertools, array, struct.
- You need a stand-alone native binary from Python source (linking only libgc and pcre2) rather than a bundled interpreter.

## Skip it when

- Programs that depend on numpy, third-party packages or unsupported stdlib modules inside the hot code; numpy arrays must be converted with tolist(), which the docs call very inefficient.
- Code that relies on Python big integers, dict insertion order, isinstance/getattr or other dynamic features: ints are fixed-width and 'ordered dicts' are listed as unsupported.
- Large code bases: the docs say type inference does not scale well beyond several thousand lines (largest compiled program about 6,000 lines), and open issue #1032 reports the same input taking 28 s or 500 s to analyse.
- Hot paths that make many small calls across the extension-module boundary: builtin objects are fully converted (deep copy) on every call and return.
- When you need full Python compatibility with little porting effort: PyPy, Nuitka or Cython run unmodified code; Shed Skin may require 'a lot' of refactoring per its README.

## How it is fast

Whole-program type inference (rewritten in 0.9.14) lets every variable become a fixed C++ type, so ints and floats are unboxed machine values (int64 by default, int32 with --int32) and attribute access is a direct member access with no dictionary lookup or bytecode dispatch. Lists map to std::vector, dicts and sets to std::unordered_map/unordered_set (boost::unordered_flat_map/small_vector with --boost), all allocated through the Boehm GC's gc_allocator; idiomatic enumerate/zip/items loops have their temporary tuples optimized away. Optional flags strip Python safety checks: -b (bounds), -w (negative-index wrap), -z (zero division), plus --predict for run-time list-size prediction.

## Compared with alternatives

Pick Shed Skin over Cython or mypyc when the code is unannotated but effectively monomorphic and you want a large speedup without writing type declarations, and over PyPy when you must stay on CPython and only a small kernel needs to be fast; prefer Codon for a broader Python-like language with its own compiler and runtime, and PyPy, Nuitka or Cython when the code uses dynamic features or third-party libraries.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Boehm GC (libgc), PCRE2, Python development headers (for extension modules), CMake for the build/run subcommands; boost containers are bundled for --boost; Windows fetches C++ deps via CMake FetchContent |
| **Minimum toolchain** | Python &gt;= 3.8 to run the transpiler; C++20 compiler (g++ -std=c++20 on Linux/macOS, MSVC Build Tools on Windows); CMake 3.18.4+ |
| **Platforms** | Linux, macOS, Windows (MSVC + CMake); platform-specific stdlib functionality unsupported |
| **Thread safety** | not documented; the threading module is not in the supported list (multiprocessing over extension modules is the documented route to parallelism) |
| **Drop-in for the baseline** | partial: only a restricted, implicitly statically typed Python subset compiles, usually after refactoring; compiled extension modules are imported like normal modules |

## Gotchas

- Integers are fixed-width C++ ints (int64 default since 0.9.13; the README sieve rows used --int32), not Python big ints; generated executables are built without -fwrapv, so overflow is C++ undefined behaviour (only extension modules get -fwrapv). None becomes a NULL pointer, so untested paths can segfault.
- Semantics differ from CPython: dicts are std::unordered_map (iteration order not insertion order), function-argument evaluation order changes, and -w/--nowrap silently stops negative indices from wrapping (the 1.8 s sieve row used --nowrap --nobounds).
- Build flags depend on the path: `shedskin translate` uses the FLAGS file (-O2 -march=native -DNDEBUG), while `shedskin build` on Unix hard-codes -O2 without -march=native; on Windows `build` passes `--config Debug` unless --build-type is given and the -O2 option is added only for UNIX, so default Windows binaries (build/Debug/test.exe) are unoptimized debug builds.
- Harness flaw: the README sieve table says n=100000000, but examples/sieve/sieve.py hard-codes n = 10000000 at both tag v0.9.9 and HEAD (HEAD also runs main() 10 times and times only the last 5 for PyPy warm-up), so the published timings cannot be reproduced from the committed example; the 'benchmarked by asv' badge points to shedskin/benchmarks, a separate microtest suite with one 2015-era machine (Intel i5-3320M, Linux 4.0.6 fc22), not the 80-example 1-100x claim.

## Known shortcomings

- README numbers without CPU, compiler or flags; examples/ has no timing harness, the per-example chart is an image only, and the sieve rows used --int32. Python-to-C++ compiler for a restricted subset, written in Python.
- Enricher: the README sieve table says n=100000000 but examples/sieve/sieve.py hard-codes n = 10000000 at v0.9.9, at tag performance_comparison and at HEAD, and HEAD runs main() 10x timing only the last 5, so the table cannot be reproduced from the committed example; the 'benchmarked by asv' badge points to microtests on one 2015 machine (i5-3320M). Windows 'shedskin build' defaults to --config Debug and the cmake -O2 flag is UNIX-only, so default Windows binaries are unoptimized; fixed-width ints without -fwrapv; dict is std::unordered_map, so iteration order differs from CPython.

## Caveats and trade-offs

First-party numbers with no CPU model or compiler version on the page; the examples/ directory has no timing harness or per-program results, so the 1-100x (average 20x, median 12x) figures over CPython 3.14 cannot be checked, and the per-example comparison against CPython 3.10 and PyPy (git tag performance_comparison) is only an image. The sieve table mixes tool versions (CPython 3.10.6/3.11.0, Nuitka 0.6.16, PyPy 3.9 5.8 s, Numba 0.56.4 2.5 s) and the Shed Skin rows used --int32, while Shed Skin now defaults to int64; the README says Numba (int64) would be as fast with 32-bit ints. Only a restricted, implicitly statically typed Python subset compiles, often after substantial refactoring. GPL-3.0 covers the compiler only; the C++ runtime that generated code links is Expat (MIT), with BSD-3-Clause random and BSL-1.0 Boost parts. [retier] README numbers without CPU, compiler or flags; examples/ has no timing harness and the per-example chart is an image only. The README sieve table says n=100000000 but examples/sieve/sieve.py hard-codes n = 10000000 (at v0.9.9, tag performance_comparison and HEAD), and HEAD runs main() 10x timing only the last 5, so the table is not reproducible from the committed example; the sieve rows used --int32. The 'benchmarked by asv' badge points to microtests on one 2015 machine (i5-3320M). Windows 'shedskin build' defaults to --config Debug (the cmake -O2 flag is UNIX-only); fixed-width ints without -fwrapv; dict is std::unordered_map, so iteration order differs from CPython. Restricted Python subset compiled to C++.

Accepts only a restricted, implicitly statically typed Python 3 subset: about 25 stdlib modules, no external libraries, no nested functions or variable argument counts; depends on the Boehm GC; programs often need refactoring; default integers are int64 (use --int32 for narrower).

## Maintenance

Actively maintained (0.9.14 with a type-inference rewrite and Unicode str, last commit 2026-10-05, about 1.0k stars, 106 open issues); the GPL-3.0 compiler does not cover generated programs' runtime, which is Expat/BSD-3/BSL-1.0, so output is copyable, but the docs still call it experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states the 1-100x (average 20x, median 12x) speedup over CPython 3.14 across the 80+ programs in examples/ and gives a sieve timing table (CPython 3.10.6 13.4 s, 3.11.0 11.4 s, Shed Skin 0.9.9 1.9 s and 1.8 s), but names no CPU, C++ compiler or flags; the example programs are public but there is no timing harness or per-program result table in the repo, so this is first-party evidence with partial methodology.
- **Verifier notes:** Numbers match the README exactly; 6-7x for the sieve is correctly marked as derived (13.4/1.9 = 7.1x vs CPython 3.10.6, 11.4/1.8 = 6.3x vs 3.11.0). Last commit 2026-10-05 (commits.atom), about 1k stars, not archived or a fork, license GPL-3.0-only (compiler) plus Expat runtime as recorded. The asv dashboard (shedskin.github.io/benchmarks) is on a blocked host and was not checked.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/README.md>
  - <https://github.com/shedskin/shedskin>
  - <https://github.com/shedskin/shedskin/commits.atom>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/pyproject.toml>
  - <https://github.com/shedskin/shedskin/tree/master/scripts>
  - <https://github.com/shedskin/shedskin/tree/master/examples>
  - <https://github.com/shedskin/shedskin/tree/master/docs>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/docs/documentation.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/README.md>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/docs/documentation.md>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/CHANGELOG.md>
  - <https://github.com/shedskin/shedskin>
  - <https://github.com/shedskin/shedskin/tree/master/shedskin>
  - <https://github.com/shedskin/shedskin/tree/master/scripts>
  - <https://github.com/shedskin/shedskin/tree/master/shedskin/resources>
  - <https://github.com/shedskin/shedskin/tree/master/shedskin/resources/cmake>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/shedskin/resources/flags/FLAGS>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/shedskin/resources/flags/FLAGS.osx>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/shedskin/resources/flags/FLAGS.mingw>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/shedskin/cmake.py>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/shedskin/resources/cmake/fn_add_shedskin_product.cmake>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/shedskin/resources/cmake/CMakeLists.txt>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/shedskin/lib/builtin.hpp>
  - <https://github.com/shedskin/shedskin/tree/master/examples>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/examples/README.md>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/examples/CMakeLists.txt>
  - <https://github.com/shedskin/shedskin/tree/master/examples/sieve>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/examples/sieve/sieve.py>
  - <https://raw.githubusercontent.com/shedskin/shedskin/HEAD/examples/sieve/CMakeLists.txt>
  - <https://raw.githubusercontent.com/shedskin/shedskin/v0.9.9/examples/sieve/sieve.py>
  - <https://raw.githubusercontent.com/shedskin/shedskin/performance_comparison/examples/sieve/sieve.py>
  - <https://raw.githubusercontent.com/shedskin/shedskin/v0.9.9/README.md>
  - <https://github.com/shedskin/shedskin/commits/master/examples/sieve/sieve.py>
  - <https://github.com/shedskin/shedskin/issues?q=is%3Aissue%20state%3Aopen%20slow>
  - <https://github.com/shedskin/benchmarks>
  - <https://github.com/shedskin/benchmarks/tree/master/results>
  - <https://raw.githubusercontent.com/shedskin/benchmarks/master/results/bright/machine.json>
  - <https://raw.githubusercontent.com/shedskin/benchmarks/master/asv.conf.json>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/shedskin/shedskin`) · [data/wave12/enrich/raw/github_com_shedskin_shedskin.json](../../../data/wave12/enrich/raw/github_com_shedskin_shedskin.json) (enrichment confidence 0.8)

</details>
