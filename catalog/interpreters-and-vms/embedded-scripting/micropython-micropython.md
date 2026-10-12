# MicroPython

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Lean Python 3 implementation for microcontrollers and embedding; about 3.4x faster than Duktape 1.2.2 on 2015 fib(34), slower than PUC Lua.

| | |
|---|---|
| **Beats** | Duktape 1.2.2 (per javascript/duktape/duktape.h in the scriptorium repo), built with cl /Ox /Oy /MT /DNDEBUG; the same table lists PUC Lua at 1.341 s, where this engine is slower |
| **Claimed result** | 2.842 s versus Duktape 9.544 s, about 3.4x faster than Duktape (derived from page data); slower than PUC Lua at 1.341 s (about 2.1x, derived from page data). |
| **Workload** | Recursive fib(34) (tests/fib.py vs tests/fib.js) run as a separate process through bench.exe: each session averages 5 launches (run.bat '@bench 5') of whole-process wall time including start-up, and the README table keeps the minimum session average per engine; July 2015 snapshot. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz (exact model not stated), 8 GiB RAM, Windows 7 64-bit |
| **Compiler and flags** | VS2015 RC or VS2013 (python/make.bat: cl /Ox /Oy /MT /DNDEBUG over py/\*.c and the windows port sources); Duktape 1.2.2 built with cl /Ox /Oy /MT /DNDEBUG (javascript/duktape/make.bat); Lua's flags not stated |
| **Adoption** | 22.1k stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/micropython/micropython) · [benchmark](https://github.com/r-lyeh-archived/scriptorium) |

## Verdict

Third-party 2015 scriptorium shootout on an AMD A10 at 3.8 GHz running Windows 7 64-bit: recursive fib(34), whole process timed through bench.exe and averaged over 5 launches, best session kept. MicroPython 1.4.4 (Windows port, MSVC /Ox) took 2.842 s against 9.544 s for Duktape 1.2.2 (MSVC /Ox, no fastint), about 3.4x faster, and 1.341 s for PUC Lua.

## Use it when

- You want Python syntax for scripting on microcontrollers (esp32, rp2, stm32, samd, mimxrt and others) with as little as 256 KiB flash and 16 KiB RAM.
- Embedding a small Python-like interpreter in a C application through the embed port, where CPython is too large.
- Recursive or integer-heavy scripting where small-int tagging avoids allocation, with hot functions moved to @micropython.native or @micropython.viper.
- Picking a scripting engine against Duktape 1.x-era JavaScript, which used doubles for every number unless built with fastint.

## Skip it when

- Raw interpreter speed: in the same 2015 table PUC Lua (1.341 s) is about 2.1x faster, and AngelScript, Lily, mruby, Squirrel, s7 and NekoVM all finish fib(34) faster.
- Code that needs full CPython semantics, the CPython C API or C extensions such as NumPy: only a subset of Python 3 is implemented, and the differences are catalogued in tests/cpydiff.
- Long-running, allocation-heavy services on small heaps: open issues report heap fragmentation (#15894, an RP2 web server after 60 h) and super-linear json.dumps on large lists (#19147).
- Production Windows hosts: the README of the Windows port calls it experimental and community-supported, and the benchmarked build was that port compiled with MSVC.

## How it is fast

A compact bytecode VM in which every object is one machine word: small ints and interned strings (qstrs) are tagged immediates (MICROPY_OBJ_REPR_A), so integer-heavy code such as fib allocates nothing. MICROPY_OPT_CACHE_MAP_LOOKUP_IN_BYTECODE caches the results of global, name and attribute lookups in the bytecode (enabled in the benchmarked Windows build), and GCC builds can use computed-goto dispatch, which mpconfig.h puts at roughly 10% faster. Per-function @micropython.native and @micropython.viper decorators emit machine code; the docs put native at roughly twice the speed of bytecode, and viper gains more by using machine-word integers.

## Compared with alternatives

Pick MicroPython over Lua, mruby, Squirrel or AngelScript when you need Python syntax and ready-made microcontroller ports rather than top interpreter speed, since all of those beat it on this fib test. Among JavaScript-side alternatives, QuickJS or XS beat Duktape by larger and more recent margins.

## Integration

| | |
|---|---|
| **Form** | source-drop (ports/embed generates self-contained .c/.h for a host C project) or standalone firmware or executables per port |
| **Dependencies** | none for the core; the build uses make, bash and Python 3.3+ (rp2 and esp32 also use CMake), and the microcontroller ports need their vendor SDKs |
| **Minimum toolchain** | gcc per the README (MSVC and mingw-w64 builds exist for the Windows port); Python 3.3+ for the build scripts |
| **Platforms** | Unix-like (Linux, BSD, macOS, WSL), Windows (experimental port), and over twenty microcontroller ports in three support tiers |
| **Thread safety** | Interpreter state is one global (mp_state_ctx), so one interpreter per process; ports with _thread run with or without a GIL depending on MICROPY_PY_THREAD_GIL; @native code does not release the GIL |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness: scriptorium's bench.exe times whole processes launched through system() (cmd.exe and interpreter start-up included; N-1 runs to nul, the last printing to the console), and bench.cc keeps each engine's minimum session average. MicroPython ran in only two sessions, 6.687 s and 2.842 s. In the first session every engine was slower (PUC Lua 2.359 s against 1.341 s later), so compare engines within a session: 2.14x faster than Duktape in session 1 and 3.36x in session 3.
- The measured build is MicroPython v1.4.4-90-g9220dc4-dirty (genhdr/mpversion.h, built 2015-07-09) from the experimental Windows port compiled with MSVC, which sets MICROPY_OPT_COMPUTED_GOTO to 0 and turns on MICROPY_DEBUG_PRINTERS and source-line info. Current MicroPython is v1.29.0 (August 2026), and the result says nothing about current builds or microcontroller ports.
- The Duktape baseline is handicapped. javascript/duktape/make.bat builds Duktape 1.2.2 with cl /Ox /Oy /MT /DNDEBUG but without DUK_OPT_FASTINT, so every JS number is a double. fib.js also calls a global function, while MicroPython's build caches global lookups in bytecode. The effect of either difference was not measured.
- bench.csv also holds four Duktape runs (9.063-9.715 s) in a two-column format that bench.cc's parser drops (it needs three fields). The table's 9.544 s is therefore not Duktape's best run; against 9.063 s the gap would be about 3.2x (derived from page data).

## Known shortcomings

- One 2015 scriptorium fib(34) run (2.842 s vs Duktape 1.2.2 at 9.544 s, engines built /Ox /Oy /MT /DNDEBUG) with run-to-run spread 6.69 vs 2.84 s; 2.1x slower than Lua, 2015 code, startup timed, CPU model and compiler version unstated.
- Enricher: the measured build is v1.4.4-90-dirty (2015-07-09), the experimental Windows port under MSVC with computed goto off and debug printers on; the Duktape 1.2.2 baseline was built without DUK_OPT_FASTINT (all numbers doubles) and bench.cc's parser drops 4 two-column Duktape rows (9.063-9.715 s), so the best Duktape run is missing (about 3.2x, not 3.4x, derived); only 2 MicroPython sessions (6.687 and 2.842 s) with session 1 slow for every engine.

## Caveats and trade-offs

Eleven-year-old snapshot (July 2015) on one recursive-fib test; the author says 'Take it with a grain of salt'. Timings include process start-up and the table keeps each engine's best session (bench.csv shows Duktape from 9.54 s to 14.30 s across sessions). The baseline is Duktape 1.2.2, far older than current releases; both fib.py and fib.js call a global function. PUC Lua (1.341 s in the same table) is about 2.1x faster than this engine. Scriptorium is archived. The first logged session in bench.csv has MicroPython at 6.69 s (against Duktape 14.30 s, still about 2.1x faster) versus 2.84 s in the last, so its number is the least stable in the table. The MicroPython tested is the 2015 Windows port built from the vendored python/micropython tree, far older than the current code.

Python 3 subset for microcontrollers with 20+ ports; its own design goal is small size and low memory use rather than raw speed.

## Maintenance

Very active MIT project (22.1k stars, 9.0k forks, 19,127 commits, last commit 2026-10-02, v1.29.0 released August 2026) that is easy to vendor through the embed port, but the speed evidence is an eleven-year-old single micro-benchmark on an experimental Windows build against a handicapped Duktape baseline.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh-archived/scriptorium, 525 stars, Unlicense) with public harness (bench.cc, run.bat, tests/fib.py, tests/fib.js, python/make.bat and javascript/duktape/make.bat, both cl /Ox /Oy /MT /DNDEBUG) lists micropython 2.842 s (row 23) vs duktape 9.544 s (row 32) and Lua 1.341 s. Not A because the CPU is given only as 'AMD A10 3.8 GHz' without a model number; B matches the other scriptorium entries.
- **Verifier notes:** Numbers match the scriptorium README and bench.csv; the record's 'per-engine flags not stated' and 'Duktape version not stated' were wrong (make.bat files give /Ox /Oy /MT /DNDEBUG; duktape.h says 1.2.2). Main shortcomings: one 2015 fib(34) micro-benchmark with start-up in the timing, unstable MicroPython timing (6.69 s vs 2.84 s), old Duktape baseline, 2.1x slower than PUC Lua; metadata (MIT, 22.1k stars, last commit 2026-10-02) confirmed.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/tests>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.py>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/python>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/python/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/duktape.h>
  - <https://github.com/micropython/micropython>
  - <https://github.com/micropython/micropython/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.py>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/python/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/duktape.h>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/python/micropython/windows/mpconfigport.h>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/python/micropython/windows/build/genhdr/mpversion.h>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/python/micropython/py/mpconfig.h>
  - <https://raw.githubusercontent.com/micropython/micropython/HEAD/README.md>
  - <https://raw.githubusercontent.com/micropython/micropython/HEAD/ports/embed/README.md>
  - <https://raw.githubusercontent.com/micropython/micropython/HEAD/examples/embedding/README.md>
  - <https://raw.githubusercontent.com/micropython/micropython/HEAD/docs/reference/speed_python.rst>
  - <https://raw.githubusercontent.com/micropython/micropython/HEAD/ports/windows/README.md>
  - <https://raw.githubusercontent.com/micropython/micropython/HEAD/ports/windows/mpconfigport.h>
  - <https://raw.githubusercontent.com/micropython/micropython/HEAD/py/mpstate.h>
  - <https://github.com/micropython/micropython>
  - <https://github.com/micropython/micropython/releases>
  - <https://github.com/micropython/micropython/tree/master/tests>
  - <https://github.com/micropython/micropython/issues?q=is%3Aissue%20state%3Aopen%20performance>
  - <https://github.com/svaarala/duktape/issues/57>
  - https://blog.miguelgrinberg.com/post/benchmarking-micropython (EGRESS_BLOCKED; search snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/micropython/micropython`) · [data/wave12/enrich/raw/github_com_micropython_micropython.json](../../../data/wave12/enrich/raw/github_com_micropython_micropython.json) (enrichment confidence 0.75)

</details>
