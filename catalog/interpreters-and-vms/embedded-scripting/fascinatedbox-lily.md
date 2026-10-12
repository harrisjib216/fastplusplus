# Lily

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Embedded scripting](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Statically typed embeddable C interpreter; about 4.8x faster than Duktape 1.2.2 on 2015 fib(34), slower than PUC Lua.

| | |
|---|---|
| **Beats** | Duktape 1.2.2 (per javascript/duktape/duktape.h in the scriptorium repo), built with cl /Ox /Oy /MT /DNDEBUG; the same table lists PUC Lua at 1.341 s, where this engine is slower |
| **Claimed result** | 2.005 s versus Duktape 9.544 s, about 4.8x faster than Duktape (derived from page data); slower than PUC Lua at 1.341 s (about 1.5x, derived from page data). |
| **Workload** | Recursive fib(34) (tests/fib.lly vs tests/fib.js) run as a separate process through bench.exe: each session averages 5 launches (run.bat '@bench 5') of whole-process wall time including start-up, and the README table keeps the minimum session average per engine; July 2015 snapshot. |
| **Metric** | throughput |
| **Hardware** | AMD A10 3.8 GHz (exact model not stated), 8 GiB RAM, Windows 7 64-bit |
| **Compiler and flags** | VS2015 RC (lily/make.bat: cl /Ox /Oy /MT /DNDEBUG /Dinline= /Dstrerror_r= psapi.lib); Duktape 1.2.2 built with cl /Ox /Oy /MT /DNDEBUG (javascript/duktape/make.bat); Lua's flags not stated |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/FascinatedBox/lily) · [benchmark](https://github.com/r-lyeh-archived/scriptorium) |

## Verdict

In r-lyeh's archived scriptorium shootout (July 2015, AMD A10 3.8 GHz, Windows 7 64-bit, VS2015 RC cl /Ox /Oy /MT /DNDEBUG for both), recursive fib(34) as a whole process averaged over 5 launches, best session kept: Lily 2.005 s vs Duktape 1.2.2 9.544 s (about 4.8x, derived from page data) and PUC Lua 1.341 s (Lily about 1.5x slower). The timing includes process start-up and Duktape ran without fastint.

## Use it when

- You embed a scripting layer in a C or C++ host and want static typing that rejects bad scripts at load time rather than at run time.
- You need several independent interpreters in one process (each lily_state is separate; one lily_config can initialise many).
- You want a sandbox switch: config.sandbox = 1 loads no predefined modules unless the host opens them, blocks library imports and makes File opens raise RuntimeError.
- Integer- and call-heavy script logic where Duktape 1.x-class engines are the alternative; in the 2015 scriptorium fib(34) run Lily took 2.005 s against Duktape's 9.544 s.
- You want a small, dependency-free MIT C11 codebase built with CMake that also builds on Windows (MSVC), Linux, BSD, macOS and Haiku.

## Skip it when

- Raw speed is the goal: PUC Lua (1.341 s), LuaJIT (0.111 s with JIT, 0.521 s without), Wren (1.997 s) and AngelScript (2.039 s) were as fast or faster in the same 2015 table, and there is no newer published benchmark for Lily.
- You need an existing language and ecosystem (JavaScript, Lua, Python); Lily scripts and libraries are Lily-only and the syntax has changed across releases (2.5 removed `case enum.variant` matching, a breaking change).
- Deep recursion: the VM's default call-depth limit is 100 frames (vm-&gt;depth_max = 100); scripts must call sys.set_recursion_limit, and lily_config has no field for the host to raise it.
- Untrusted scripts that need CPU or memory limits: sandbox mode restricts modules and file access only; no instruction-count or allocation budget hooks are documented in lily.h.
- Hash tables exposed to attacker-chosen keys with the default config: the SipHash key defaults to the fixed bytes 1..16, so the host must set config.sipkey itself.

## How it is fast

The type checker resolves types at parse time, so the emitter writes type-specialised 16-bit register-machine opcodes (o_int_add, o_number_add, o_compare_eq with integer/string/double fast paths) that the VM executes without dynamic type dispatch; integers are unboxed int64 in the register. Calls to a `define` are statically bound (o_call_native) rather than resolved through a global property lookup as Duktape does for fibR. Dispatch is a plain switch loop (no computed goto, no JIT); memory uses refcounting plus a tagged cycle collector for values that can form cycles (gc_start 100, gc_multiplier 4 by default).

## Compared with alternatives

Pick Lily over AngelScript, Squirrel or mruby (all about 2.0-2.1 s in the same 2015 table, so speed is a wash) when you want a statically typed language with a C11 API, a built-in sandbox flag and an MIT licence; pick Daslang if you want a statically typed embedded language that is measured as fast on current benchmarks, and Lua or Luau if speed and ecosystem matter more than static types.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none beyond libc (links libdl on Linux and libm off Windows); CMake builds liblily as a shared library by default, static with -DBUILD_SHARED_LIBS=OFF |
| **Minimum toolchain** | C11 compiler (anonymous unions), CMake 3.10+; the CMake build uses -O2 on GCC/Clang |
| **Platforms** | Windows (MSVC, MinGW), Linux, \*BSD, macOS, Haiku; architecture-neutral C, no JIT |
| **Thread safety** | not documented; separate lily_state instances do not share interpreter state, but no locking or thread guarantee is stated |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws behind the number: scriptorium's bench.cc launches the interpreter with system() and sets overhead = 0 (the fib(0) start-up subtraction was never implemented), so start-up and parse time are inside the 2.005 s; the README table keeps each engine's minimum across sessions (Lily 2.31 s in the first logged session, Duktape 9.54 to 14.30 s); the script output is never checked; and its idx::operator&lt; (time, else name) is not a strict weak ordering, so ranks can be misordered even though the times are right.
- The baseline was handicapped by its build: Duktape 1.2.2 was compiled from scriptorium's make.bat without DUK_OPT_FASTINT, so all its arithmetic ran in doubles, and fib.js calls a global fibR through a property lookup per call while fib.lly calls a statically bound define.
- The measured Lily is a pre-0.15 July 2015 snapshot (old `integer` / `string::format` syntax) linked under the old owner jesserayadkins; the current 2.5 VM is a different code base and has never been benchmarked against Duktape or QuickJS on any page read.
- Errors propagate with setjmp/longjmp (lily_jump_setup in lily_vm_execute); C++ foreign functions that hold RAII objects when a Lily exception is raised will skip their destructors. Crash fixes still land in 2026 releases (closure plus high-index global #646, incomplete Hash literal #641).

## Known shortcomings

- One 2015 scriptorium fib(34) run (2.005 s vs Duktape 1.2.2 at 9.544 s, engines built /Ox /Oy /MT /DNDEBUG, each session averaging 5 launches with the best session kept, startup timed); slower than Lua (1.341 s) in the kept session but ahead of it in the first, so within noise. CPU model and compiler version unstated.
- Enricher: scriptorium's bench.cc sets overhead = 0 so fib(0) start-up is never subtracted, keeps each engine's minimum across sessions, never checks output, and its idx::operator&lt; is not a strict weak ordering (ranks unreliable); Duktape 1.2.2 was built without DUK_OPT_FASTINT (all doubles). The measured Lily is a pre-0.15 2015 snapshot and the current 2.5 VM was never benchmarked; default recursion limit 100 frames that the host cannot raise, fixed default sipkey, setjmp/longjmp error path skips C++ destructors.

## Caveats and trade-offs

Eleven-year-old snapshot (July 2015) on one recursive-fib test; the author says 'Take it with a grain of salt'. Timings include process start-up and the table keeps each engine's best session (bench.csv shows Duktape from 9.54 s to 14.30 s across sessions, and Lily 2.31 s in the first session). The baseline is Duktape 1.2.2, far older than current releases, and fib.js calls a global fibR (a property lookup per call in Duktape) while fib.lly calls a statically bound define. PUC Lua is 1.341 s in the table, so Lily is about 1.5x slower than Lua there, although in the first logged session Lily (2.31 s) edged Lua (2.36 s), so the Lua ordering is within run-to-run noise. Scriptorium is archived and links the project under its old owner (jesserayadkins/lily); the 2015 Lily tested uses old syntax and is far older than the current code.

Statically typed interpreted language designed for embedding and sandboxing with multiple interpreter instances; not Lua-compatible.

## Maintenance

Actively maintained (quarterly releases, 2.5 on 2026-07-10, last commit 2026-09-22, CI and tracker on GitLab with GitHub as a copy) and MIT with no dependencies, so it is easy to vendor, but its only speed evidence is an eleven-year-old single-kernel run of a pre-1.0 build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party shootout (r-lyeh-archived/scriptorium, 525 stars, Unlicense) with public harness (bench.cc, run.bat, tests/fib.lly, tests/fib.js, lily/make.bat and javascript/duktape/make.bat, both cl /Ox /Oy /MT /DNDEBUG) lists lily 2.005 s (row 17) vs duktape 9.544 s (row 32) and Lua 1.341 s. Not A because the CPU is given only as 'AMD A10 3.8 GHz' without a model number; B matches the chibi-scheme, Pawn, Neko and TinyVM precedents.
- **Verifier notes:** Numbers match the scriptorium README and bench.csv. The record's claim that per-engine flags and the Duktape version are not stated was wrong: make.bat files give /Ox /Oy /MT /DNDEBUG and duktape.h says 1.2.2. Main shortcomings: one 2015 fib(34) micro-benchmark with start-up in the timing, an old Duktape 1.2.2 baseline, slower than PUC Lua; metadata (MIT, 1.1k stars, last commit 2026-09-22) confirmed.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/r-lyeh-archived/scriptorium>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/tests>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lly>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/lily>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/lily/make.bat>
  - <https://github.com/r-lyeh-archived/scriptorium/tree/master/javascript/duktape>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/duktape.h>
  - <https://github.com/FascinatedBox/lily>
  - <https://github.com/FascinatedBox/lily/commits>
  - <https://github.com/jesserayadkins/lily>
- **Sources the enricher read:**
  - <https://github.com/FascinatedBox/lily>
  - <https://github.com/FascinatedBox/lily/commits>
  - <https://github.com/FascinatedBox/lily/tree/main/src>
  - <https://raw.githubusercontent.com/FascinatedBox/lily/HEAD/README.md>
  - <https://raw.githubusercontent.com/FascinatedBox/lily/HEAD/RELEASES.md>
  - <https://raw.githubusercontent.com/FascinatedBox/lily/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/FascinatedBox/lily/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/FascinatedBox/lily/HEAD/src/lily.h>
  - <https://raw.githubusercontent.com/FascinatedBox/lily/HEAD/src/lily_vm.c>
  - <https://raw.githubusercontent.com/FascinatedBox/lily/HEAD/src/lily_opcode.h>
  - <https://raw.githubusercontent.com/FascinatedBox/lily/HEAD/src/lily_value.h>
  - <https://raw.githubusercontent.com/FascinatedBox/lily/HEAD/src/lily_platform.h>
  - <https://raw.githubusercontent.com/FascinatedBox/lily/HEAD/src/lily_pkg_sys.c>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/README.md>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.cc>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/bench.csv>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/run.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lly>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.js>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/tests/fib.lua>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/lily/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/make.bat>
  - <https://raw.githubusercontent.com/r-lyeh-archived/scriptorium/HEAD/javascript/duktape/duktape.h>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/fascinatedbox/lily`) · [data/wave12/enrich/raw/github_com_fascinatedbox_lily.json](../../../data/wave12/enrich/raw/github_com_fascinatedbox_lily.json) (enrichment confidence 0.55)

</details>
