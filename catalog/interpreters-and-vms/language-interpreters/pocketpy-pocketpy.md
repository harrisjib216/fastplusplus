# pocketpy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Embeddable Python-subset interpreter in C11 for game scripting; about 1.2x CPython 3.8 on one old benchmark, slower than Lua.

| | |
|---|---|
| **Beats** | CPython 3.8.10 |
| **Claimed result** | Primes benchmark: pkpy 1.2.7 2.385 s vs CPython 3.8.10 2.871 s (about 1.2x, derived from page data); Lua 5.3.3 took 1.576 s (about 1.5x faster than pkpy, derived from page data) and C++ (gnu++11) 0.104 s. The README also says 'Currently, pkpy is as fast as cpython 3.9', but docs/performance.md calls the 1.2.7 numbers historical and says to use them 'as historical observations, not as a claim of equivalence to a particular CPython release'. |
| **Workload** | 'primes' benchmark (benchmarks/primes.py) run on pkpy 1.2.7, CPython 3.8.10, Lua 5.3.3 and a C++ version. |
| **Metric** | throughput |
| **Hardware** | Intel i5-12400F, WSL (Ubuntu 20.04 LTS) |
| **Compiler and flags** | Not stated for the Python and Lua rows (C++ row built as gnu++11). |
| **Adoption** | 2.1k stars; used in TIC-80, godot-pocketpy and others |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/pocketpy/pocketpy) · [benchmark](https://github.com/pocketpy/pocketpy) |

## Verdict

The README and docs/performance.md report one run of the primes script (Atkin sieve to 5,000,000 plus a digit trie, identical source for pkpy and CPython) on an Intel i5-12400F under WSL Ubuntu 20.04: pkpy 1.2.7 2.385 s, CPython 3.8.10 2.871 s (about 1.2x faster, derived from page data), Lua 5.3.3 1.576 s (about 1.5x faster than pkpy) and C++ (gnu++11) 0.104 s, with no compiler flags or run count stated.

## Use it when

- Adding a Python-syntax scripting layer to a C or C++ game or app with no external dependencies (TIC-80, godot-pocketpy, raylib bindings and the Crescent engine use it).
- Targets where embedding CPython is awkward: iOS, Android, Emscripten 32-bit, Raspberry Pi OS, 32-bit Linux boards such as Luckfox Pico, all officially tested.
- Script logic built from small int and float loops and method calls, the shape of the primes benchmark where pkpy 1.2.7 ran about 1.2x faster than CPython 3.8.10 (derived from page data).
- Hosts that want several isolated interpreters (16 VM slots) and background compute jobs via pkpy.ComputeThread, or reproducible floating point across platforms (the default PK_ENABLE_DETERMINISM build).

## Skip it when

- When raw script speed matters more than Python syntax: Lua 5.3.3 was about 1.5x faster than pkpy on the project's own primes run, and the LuaJIT sibling is faster still.
- Running existing CPython code: generator expressions, try/finally and else, multiple inheritance, __slots__, descriptors, __iadd__ hooks and structural pattern matching are missing, keyword passing of non-default parameters fails, and CPython wheels and C extensions cannot load.
- Arbitrary-precision integer work (hashing with big constants, crypto, exact arithmetic): ints are fixed signed 64-bit and overflow behaviour is not guaranteed.
- Sharing one interpreter between native threads: only one thread may use a VM at a time, and ComputeThread workers exchange data by pickle copies.
- Expecting the README's 'as fast as cpython 3.9' to hold for current releases: no published measurement covers the 2.x C11 interpreter or any CPython newer than 3.8.10.

## How it is fast

Values are a tagged struct (py_TValue) that stores ints as signed 64-bit, floats as doubles and small vectors inline, so int and float arithmetic in the switch-based bytecode loop (ceval.c) takes a type-check fast path with no allocation and no bignum overflow handling; the fast paths also skip method lookup because redefining a built-in type's methods is declared unsupported. Memory is managed by a stop-the-world mark-and-sweep collector with an adaptive threshold instead of per-object reference counting. Dropping CPython features (arbitrary-precision ints, generator expressions, try/finally, multiple inheritance, descriptors) keeps the runtime small and simple.

## Compared with alternatives

Pick pocketpy over Wren or LuaJIT when the requirement is Python syntax inside a dependency-free C or C++ host, accepting that it is slower than Lua; pick the Wren sibling (faster than Lua 5.2 in its own benchmarks) or LuaJIT when speed matters more than syntax, and PyPy or CPython when you need real Python compatibility and its library ecosystem.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake add_subdirectory) or source-drop (single pocketpy.h plus pocketpy.c amalgamation) |
| **Dependencies** | none beyond the C standard library; optional mimalloc (PK_ENABLE_MIMALLOC, fetched by CMake) and optional LZ4, cute_png, msgpack and periphery modules |
| **Minimum toolchain** | C11 compiler (--std=c11); on Windows only MSVC is officially supported and needs /utf-8 and /experimental:c11atomics; NDEBUG must be defined for release builds |
| **Platforms** | any platform with a C11 compiler; officially tested on Windows 64-bit, Linux 64/32-bit, macOS 64-bit, Android 64/32-bit, iOS 64-bit, Emscripten 32-bit, Raspberry Pi OS 64-bit and Luckfox Pico 32-bit |
| **Thread safety** | One native thread per VM at a time; up to 16 independent VMs, with pkpy.ComputeThread running jobs in worker VMs and passing arguments and results by pickle |
| **Drop-in for the baseline** | no |

## Gotchas

- Evidence: the only published numbers come from pkpy 1.2.7, which was the earlier C++17/STL implementation (about 14K lines, single header); the current code is a C11 rewrite, and docs/performance.md itself says the 1.2.7 results 'are not a benchmark of the current 2.x C11 interpreter'. The primes table gives one time per implementation with no run count, timing method or build flags, and primes.lua only checks the entries it actually returned, so a short result list would still pass (primes.py asserts the full list).
- The CI benchmark step (scripts/run_tests.py benchmark) times one os.system wall-clock run per script, CPython first, against whatever Python the runner has, so start-up is included, there is no repetition and the results are not published in the repo; the pocketpy.dev performance page was blocked here and a search snippet only says pkpy took '47-82%' of CPython's time on fib, loop, primes and sort scripts with no versions.
- Int arithmetic fast paths compute lhs + rhs, lhs - rhs and lhs \* rhs directly on int64 under -O2 without -fwrapv, so overflow is C undefined behaviour rather than a Python error; the docs say not to rely on overflow exceptions. Part of the measured edge over CPython comes from skipping arbitrary-precision ints.
- The default build (PK_ENABLE_DETERMINISM=ON) adds -fno-fast-math -ffp-contract=off and ships its own binary64 math kernels (src/common/dmath\*.c) for cross-platform reproducibility; its speed cost is not documented. Redefining a built-in type's methods (for example int.__add__) is unsupported and can crash or give wrong results because the fast paths assume the originals.

## Known shortcomings

- Not faster than the Lua baseline: in its own table Lua 5.3.3 is 1.5x faster than pkpy, and the win is only 1.2x over CPython 3.8.10 on one script with pkpy 1.2.7; docs/performance.md disclaims these numbers for the current 2.x series. No compiler or flags.
- Enricher: the measured 1.2.7 was the old C++17/STL codebase, not the current C11 rewrite; the primes run is a single timing with no flags and primes.lua checks only the returned entries; int64 fast paths overflow as C undefined behaviour (no -fwrapv) and part of the edge over CPython comes from skipping bignums.

## Caveats and trade-offs

Does not beat the category's in-list baseline: in its own table Lua 5.3.3 is about 1.5x faster than pkpy. The win over CPython is small (about 1.2x), on one benchmark, against an old CPython 3.8.10, and was measured on pkpy 1.2.7; the project's docs/performance.md says these 1.2.7 results 'are not a benchmark of the current 2.x C11 interpreter'. Compiler and flags not stated for any of the measured builds. The linked performance page (pocketpy.github.io/performance) and an older 1.2.6 CI comparison were not opened. Listed to document the shortcoming.

Portable Python 3 interpreter in C11 designed as a game-scripting alternative to Lua; single-header or CMake integration; supports a subset of Python (no full standard library); tested on Windows, Linux, macOS, Android, iOS, Emscripten and Raspberry Pi OS.

## Maintenance

Actively maintained (2.1k stars, 221 forks, over 4,300 commits, last commit 2026-10-03, MIT) with CI on Windows, Linux, macOS and Android and production users such as TIC-80; easy to vendor as two files, but treat its speed claims as unmeasured for the current 2.x interpreter.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party primes timings in the README (repeated in docs/performance.md) with benchmark code public at commit 9481d653 (benchmarks/primes.py, primes.lua, primes.cpp, all of which assert the expected result) and the CPU stated (i5-12400F, WSL Ubuntu 20.04), but no compiler or build flags for pkpy, CPython or Lua, so not A; no independent measurement, so C.
- **Verifier notes:** Numbers, versions and hardware match the README exactly; the primes scripts at the recorded commit are equivalent across languages and check their output, so the evidence is valid but thin and dated. Shortcomings to record: slower than Lua (in-list baseline) by about 1.5x; only a 1.2x win over CPython 3.8 on one script; numbers predate the 2.x C11 rewrite and the project itself disclaims them; no compiler/flags. CPython is an in-list baseline for language-interpreters, not for embedded-scripting.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/README.md>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/main/docs/performance.md>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/9481d653b60b81f4590a4d48f2be496f6962261e/benchmarks/primes.py>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/9481d653b60b81f4590a4d48f2be496f6962261e/benchmarks/primes.lua>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/9481d653b60b81f4590a4d48f2be496f6962261e/benchmarks/primes.cpp>
  - <https://github.com/pocketpy/pocketpy>
  - <https://github.com/pocketpy/pocketpy/commits>
- **Sources the enricher read:**
  - <https://github.com/pocketpy/pocketpy>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/README.md>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/docs/performance.md>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/docs/features/differences.md>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/docs/features/ub.md>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/docs/features/threading.md>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/CMakeOptions.txt>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/.github/workflows/main.yml>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/scripts/run_tests.py>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/src/interpreter/ceval.c>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/src/interpreter/heap.c>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/HEAD/include/pocketpy/objects/base.h>
  - <https://github.com/pocketpy/pocketpy/tree/main/benchmarks>
  - <https://github.com/pocketpy/pocketpy/tree/main/src/interpreter>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/9481d653b60b81f4590a4d48f2be496f6962261e/README.md>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/9481d653b60b81f4590a4d48f2be496f6962261e/benchmarks/primes.py>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/9481d653b60b81f4590a4d48f2be496f6962261e/benchmarks/primes.lua>
  - <https://raw.githubusercontent.com/pocketpy/pocketpy/9481d653b60b81f4590a4d48f2be496f6962261e/benchmarks/primes.cpp>
  - <https://github.com/pocketpy/pocketpy/issues?q=is%3Aissue%20performance%20OR%20slow%20OR%20slower>
  - <https://github.com/pocketpy/pocketpy/issues/197>
  - https://pocketpy.dev/performance/ (EGRESS_BLOCKED; WebSearch snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/pocketpy/pocketpy`) · [data/wave12/enrich/raw/github_com_pocketpy_pocketpy.json](../../../data/wave12/enrich/raw/github_com_pocketpy_pocketpy.json) (enrichment confidence 0.75)

</details>
