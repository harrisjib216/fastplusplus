# cpy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Tree-walking interpreter for a Python subset in portable C; claims 1.2x-50x over CPython 3.12 with no published benchmark scripts.

| | |
|---|---|
| **Beats** | CPython 3.12 (the README names 'python3' as CPython 3.12) |
| **Claimed result** | '1.2x-50x faster than CPython' on the numeric loop, list building, dict fill/read and attribute-access benchmarks; the call-heavy recursive fib(30) benchmark is 'about on par' (README, no per-benchmark times given). |
| **Workload** | README 'How fast' section names a numeric loop, building a list, filling and reading a dict, a hot attribute-access loop and a recursive fib(30). The README says 'see tests/ for the exact scripts', but tests/ contains only the correctness tests t01-t12 and t90 (.cpy plus expected .out) and compare_python.sh, so the benchmark programs are not published. |
| **Metric** | throughput |
| **Hardware** | 'single-machine numbers' (CPU not stated); README says it is built to be developed and run on a phone (Termux) as well as PC or server |
| **Compiler and flags** | Makefile default is \$(CC) with CFLAGS ?= -O2 plus -std=gnu11 (built with clang on Termux per the README); the compiler, version and flags used for the README timings are not stated |
| **Adoption** | 0 stars at the time of the check |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/MoonLite-Br/Cpy) · [benchmark](https://github.com/MoonLite-Br/Cpy) |

## Verdict

The README alone says a numeric loop, list building, dict fill/read and an attribute-access loop run 1.2x-50x faster than CPython 3.12 and that recursive fib(30) is about on par, on one unnamed machine with no compiler, flags, times or scripts; nothing in the repository lets a reader rerun or check it.

## Use it when

- Small scripts and glue code on a phone (Termux) or a minimal Linux box where a single dependency-free C binary is easier to ship than a CPython install.
- Integer- and loop-heavy scripts whose values stay within signed 64-bit range and that use only the built-in modules listed in the README.
- Teaching or experimenting with interpreter design: the whole implementation is a handful of C files (interp.c is about 2,000 lines) with an internals guide.
- Only after timing your own script against CPython: the repository publishes no benchmark programs or per-benchmark times to rely on.

## Skip it when

- Anything that needs arbitrary-precision integers, bytes/bytearray, complex numbers, match, async/await, __slots__, __del__, str.encode, except\* or most of the standard library; pip packages and C extensions do not work.
- Generator-heavy code: every def-generator runs on its own OS thread with an 8 MB stack and each resume is a pair of semaphore handoffs, which costs far more than a CPython frame switch (generator expressions are plain iterators and are not affected).
- Long-running programs that build reference cycles: there is no cycle collector, so cyclic garbage is never freed.
- Services that put untrusted strings into dicts: string hashing is an unseeded 32-bit FNV-1a, so collisions can be precomputed, unlike CPython's randomized hash.
- Production use in general: the repository is two weeks old (six commits on 2026-09-22, 0 stars) with no releases.

## How it is fast

Values are a 16-byte tagged union, so int, float, bool and None are unboxed; a resolver pass turns every local and free variable into a frame slot index or a fixed number of parent hops. The evaluator inlines the common node kinds with an int-op-int fast path using __builtin_\*_overflow checks, calls without \*/\*\* go through a direct path that skips bound-method allocation, small frames come from a free list, and memory is reclaimed by reference counting only. Dicts and sets are a compact insertion-ordered table with linear probing, hashed with unseeded 32-bit FNV-1a for strings and a 64-bit mix for ints.

## Compared with alternatives

Pick cpy only when you need a tiny, dependency-free C binary for simple Python-syntax scripts; for real speedups on real Python code PyPy, Codon, Cython, mypyc or GraalPy have reproducible, independent numbers, and WeavePy publishes a per-fixture parity report against CPython where cpy publishes none.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc, libm and pthreads (POSIX semaphores for generators) |
| **Minimum toolchain** | C compiler accepting -std=gnu11 and GCC/Clang __builtin_\*_overflow builtins (gcc or clang); make |
| **Platforms** | CI builds and tests Linux x86-64 (with ASan/UBSan) and Linux arm64, and cross-builds Android arm64 (NDK, API 24) without running tests; macOS and Windows are not in CI |
| **Thread safety** | No threading module; the interpreter uses global state and runs on one big-stack thread (512 MB, falling back to 128/32 MB); generator threads only ever run in lockstep with the caller. |
| **Drop-in for the baseline** | partial: runs many plain .py scripts unchanged, but int overflow raises OverflowError, cycles leak, case conversion only knows Latin, Greek and Cyrillic, and anything outside the supported subset or built-in modules fails |

## Gotchas

- The speed claim cannot be reproduced: the README says 'see tests/ for the exact scripts', but tests/ holds only correctness tests t01-t12, t90 and compare_python.sh, examples/ holds demo programs (fib.cpy prints 8 Fibonacci numbers, it is not the fib(30) benchmark), and no times, CPU, compiler or flags are given for the 1.2x-50x range.
- Part of the numeric-loop advantage is semantic: int is a fixed int64 with overflow checks, so cpy skips the arbitrary-precision object path CPython must take, and a loop that overflows int64 raises OverflowError instead of continuing.
- The test suite's expected .out files are regenerated from cpy's own output (run_tests.sh --update); the CPython comparison script is a developer helper that CI does not run, so 'verified against CPython 3.12' is not enforced.
- docs/internals.md presents slot-resolved locals as the biggest difference from CPython, but CPython also indexes function locals by slot (LOAD_FAST); the claimed attribute-access and dict gains are unexplained by any published measurement.

## Known shortcomings

- Only a 1.2x-50x range with no per-benchmark times; the README says scripts are in tests/ but none are there (tests/ holds correctness tests only), 0 stars, a one-day-old repo, int64-only integers and cycles never collected. Borderline D.
- Enricher: no benchmark code anywhere (examples/fib.cpy prints 8 numbers, not fib(30)); the speedup is partly semantic (int64 with OverflowError instead of bigints); each generator is an OS thread with an 8 MB stack and a semaphore handoff per resume; no cycle collection; unseeded 32-bit FNV-1a string hash; test .out files are regenerated from cpy itself and the CPython compare script is not in CI. 0 stars, 6 commits on 2026-09-22.

## Caveats and trade-offs

Brand-new repository (all six commits dated 2026-09-22, 0 stars, 0 forks). The README gives only a 1.2x-50x range with no per-benchmark numbers, no compiler or flags and no CPU; the benchmark scripts it points to ('see tests/') are not in the repository, and tests/compare_python.sh only diffs program output against CPython 3.12, so the ratios cannot be reproduced. Semantics differ from CPython in ways that help numeric loops: int is 64-bit and raises OverflowError instead of promoting to bigint, memory is reference-counted only (reference cycles are never collected), and there is no bytes/bytearray, complex, match, async/await or __slots__. It is a tree-walking AST interpreter (no bytecode); generators each run on their own OS thread with an 8 MB stack, so generator-heavy code is likely slow. Low confidence.

Python subset: 64-bit int only (overflow raises OverflowError), no bytes/bytearray, complex numbers, match, async/await, __slots__ or metaclasses beyond type(...); standard library limited to a few built-in modules; no JIT (README says it will not out-run PyPy).

## Maintenance

Brand-new single-author project (all six commits on 2026-09-22, MIT, about 2,000 lines of evaluator plus support files, small enough to vendor) with CI on Linux and Android but no releases, no users and an unreproducible speed claim; treat it as a curiosity until benchmark scripts appear.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'How fast' section claims '1.2x-50x faster' than CPython 3.12 on four named workloads and 'about on par' on fib(30), but gives no per-benchmark times, no CPU, no compiler or flags; the scripts it says are in tests/ do not exist there (tests/ holds only correctness tests and compare_python.sh, tools/ only gen_stdlib.sh). First-party range with no methodology is C at best.
- **Verifier notes:** Claim text in the record matches the README; the only real fix is that the 'exact scripts' the README cites do not exist in tests/ or tools/, so there is no benchmark code at all. Kept at C as a weak first-party range claim (one could argue D since no individual number is given); flag 0 stars, one-day-old repo, int64-only ints and no cycle collection. MIT licence (LICENSE file, 2026 moonlite-admin) and last commit 2026-09-22 confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/MoonLite-Br/Cpy>
  - <https://github.com/MoonLite-Br/Cpy/commits>
  - <https://github.com/MoonLite-Br/Cpy/tree/main/tests>
  - <https://github.com/MoonLite-Br/Cpy/tree/main/tools>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/README.md>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/Makefile>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/tests/compare_python.sh>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/docs/internals.md>
- **Sources the enricher read:**
  - <https://github.com/MoonLite-Br/Cpy>
  - <https://github.com/MoonLite-Br/Cpy/commits>
  - <https://github.com/MoonLite-Br/Cpy/tree/main/tests>
  - <https://github.com/MoonLite-Br/Cpy/tree/main/examples>
  - <https://github.com/MoonLite-Br/Cpy/tree/main/src>
  - <https://github.com/MoonLite-Br/Cpy/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/README.md>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/Makefile>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/docs/internals.md>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/docs/language.md>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/tests/compare_python.sh>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/tools/gen_stdlib.sh>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/run_tests.sh>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/examples/fib.cpy>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/src/interp.c>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/src/value.c>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/src/cpy.h>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/src/gen.c>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/MoonLite-Br/Cpy/HEAD/.github/workflows/build.yml>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/moonlite-br/cpy`) · [data/wave12/enrich/raw/github_com_moonlite_br_cpy.json](../../../data/wave12/enrich/raw/github_com_moonlite_br_cpy.json) (enrichment confidence 0.65)

</details>
