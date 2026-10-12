# S6 (DeepMind CPython JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> DeepMind's archived decorator-driven JIT library for CPython 3.7; first-party 7-9.5x on Richards, 5x slower on unpack_sequence.

| | |
|---|---|
| **Beats** | CPython 3.7 interpreter |
| **Claimed result** | Richards: 7x over the default Python 3.7 interpreter at 100 iterations, 9.5x average on internal dev machines; raytrace 3-4.5x; unpack_sequence worst case 0.2x (a 5x slowdown) or 0.97x in a tweaked variant; README headline 'up to 10x over CPython for pure Python benchmarks'. |
| **Workload** | Three pyperformance benchmarks modified by DeepMind, in src/benchmarks/: richards.py, raytrace.py, and unpack_sequence_fast.py / unpack_sequence_slow.py. pyperf was removed because it segfaults under S6. Each script runs the plain CPython 3.7 interpreter, then the @s6.jit version, in the same process. |
| **Metric** | throughput |
| **Hardware** | 'internal dev machines' (no CPU model stated) |
| **Compiler and flags** | Public Dockerfile: clang 13 (apt.llvm.org); CPython 3.7 branch built from source with CFLAGS=-fno-omit-frame-pointer and ./configure --enable-shared (no --enable-optimizations/PGO). The build behind the internal-machine numbers is not stated. |
| **Adoption** | 151 stars |
| **Last commit** | 2022-09-14 |
| **Links** | [repository](https://github.com/deepmind/s6) · [benchmark](https://github.com/deepmind/s6) |

## Verdict

First-party only: the README reports Richards about 7x over 'the default Python 3.7 interpreter' at 100 iterations 'depending on your hardware' and 9.5x on unnamed internal dev machines, raytrace 3-4.5x, and unpack_sequence 0.2x (slow variant) or 0.97x (fast variant). The numbers come from single-run scripts in src/benchmarks that time the baseline and then the S6 run in the same process; the public build is clang 13 against a non-PGO, frame-pointer CPython 3.7, and no independent reproduction was found.

## Use it when

- Studying how to build a V8-style JIT (hidden classes, SSA IR, deoptimisation) as a CPython library: the README is a detailed design write-up and the C++ source is Apache-2.0.
- Object-oriented pure-Python hot loops (method calls, attribute access) on a CPython 3.7 you control: Richards is the case with the first-party 7x (100 iterations) and 9.5x (internal machines) figures.
- Pure-Python floating-point code such as the raytrace benchmark (3-4.5x first-party), where unboxing applies.
- x86-64 Linux setups that can rebuild CPython 3.7 with -fno-omit-frame-pointer and run the Docker build.

## Skip it when

- Anything needing support or a current Python: the repository was archived on 2023-07-05 with a single import commit, DeepMind stopped work on it, and only CPython 3.7 is supported.
- Code dominated by C-API calls such as NumPy: the README says these are bottlenecked by C API call time.
- Large functions or heavy tuple/list unpacking: unpack_sequence ran 5x slower (0.2x) because the hot loop stays in S6's own interpreter, which is slower than ceval.c; the README advises splitting big functions.
- Stock distribution CPython builds: without frame pointers JIT compilation 'might crash', and the --wrap=PyFrame_FastToLocalsWithError link step is not in the release, so compilation 'might misbehave'; pyperf segfaults under S6 (benchmark docstrings).
- Non-x86-64 hosts: code generation targets x86 only.

## How it is fast

S6's ceval-like interpreter collects type feedback, and an Oracle counts executed bytecodes to pick hot code objects for asynchronous compilation. Bytecode is translated to strongjit, an SSA IR with block arguments; optimisation passes run on it, functions are specialised on the type of their first argument behind guards with deoptimisation back to CPython frames, and boxed int/float/bool arithmetic is unboxed. Attribute and global loads use V8-style hidden classes (class IDs hidden in the top 20 bits of a dict's ma_version_tag or a type's tp_flags) so they become guarded fixed-slot loads, and attributes that never change are treated as constants; the IR is lowered to x86-64 machine code with asmjit.

## Compared with alternatives

Pick S6 only as a design reference: for running code, Cinder's CinderX extension (actively released for CPython 3.14, 1.5-3.8x over its own interpreter) or CPython's built-in copy-and-patch JIT (about 7-8% geomean, supported) are the practical CPython JITs, and Numba or Hana Jit fit numeric kernels better.

## Integration

| | |
|---|---|
| **Form** | Python C++ extension module (pybind11) built from source with CMake/Ninja; Docker image recommended |
| **Dependencies** | CPython 3.7 shared library, abseil-cpp, asmjit, pybind11, pybind11_abseil, re2, udis86, cppitertools, googletest (pinned via FetchContent in src/CMake/deps.cmake), protobuf from the system |
| **Minimum toolchain** | C++17, clang (Dockerfile uses clang 13), CMake 3.16.3+, CPython 3.7 configured with --enable-shared and built with -fno-omit-frame-pointer |
| **Platforms** | x86-64 Linux (Ubuntu 20.04 Docker image); no other targets |
| **Thread safety** | not documented; the design relies on the GIL (type modifications 'stop the world', which the README calls easy because of the GIL), and compilation runs asynchronously from the Oracle |
| **Drop-in for the baseline** | partial: no CPython source changes and only a @s6.jit decorator on the entry point, but it needs a frame-pointer CPython 3.7 build plus S6's own build, and some workloads run slower |

## Gotchas

- Harness flaw: @s6.jit is applied at import time (in the Richards class body and on module-level functions), and the decorator calls Initialize(adopt_types=true), which adopts all existing types, swaps the generic tp_setattro of every adoptable type for S6's GenericSetAttrUsingClasses (string interning plus a class attribute-map lookup) and hooks PyType_Type.tp_new. The 'Default Python 3.7' baseline in richards.py, raytrace.py and the unpack_sequence scripts is therefore timed on a CPython already instrumented by S6, not stock CPython; Richards' attribute-store-heavy loop pays the wrapper, which can inflate the reported speedup by an unmeasured amount.
- Each script times one wall-clock run per mode (time.time() or perf_counter), baseline first and S6 second in the same process, with no repetitions; richards.py discards _run's correctness result (holdCount 9297 / qpktCount 23246), so a wrong result would still print a speedup, and its default is 50 iterations while the README quotes 100. The S6 time includes JIT warm-up and compilation.
- Specialisation is on the first argument's type only; hidden classes are not used for objects with custom __getattr__/__setattr__ or a negative tp_dictoffset, and any dict change made outside S6 resets the class ID to 0, dropping that object off the fast path.
- The public numbers come from 'internal dev machines' with no CPU or build named; the Docker baseline CPython is the unpinned 3.7 branch built without PGO and with frame pointers kept.

## Known shortcomings

- Archived, CPython 3.7 only; the 9.5x is on unnamed internal machines, src/benchmarks/richards.py does one time.time() run per mode and ignores the correctness return, and the Dockerfile baseline is a clang 13 non-PGO CPython with frame pointers. Last commit 2022-09-14; filed under jits.
- Enricher: @s6.jit runs at import and calls Initialize(adopt_types=true), which swaps tp_setattro to GenericSetAttrUsingClasses and hooks tp_new before the 'Default Python 3.7' baseline is timed, so the baseline is S6-instrumented CPython rather than stock and the 9.5x may be inflated by an unmeasured amount; one run per mode, the Richards result is discarded, default 50 iterations against the README's 100.

## Caveats and trade-offs

The repo was archived on 2023-07-05 and holds one Copybara import commit (2022-09-14); DeepMind says it stopped work on S6. The README says most testing used internal or private benchmarks; the public numbers are for three modified pyperformance benchmarks on unnamed hardware. The harness (e.g. src/benchmarks/richards.py) times one wall-clock run of each mode with time.time(), with no repetitions. It ignores the benchmark's own correctness return value, so a wrong-result run would still print a speedup. The S6 timing includes JIT warm-up. The public Dockerfile's baseline CPython is a non-PGO build with frame pointers kept, which is slower than a distribution CPython. On unpack_sequence S6 is 5x slower (0.2x), or 0.97x in the tweaked variant. Only CPython 3.7 is supported, and it is long out of support. Apache-2.0 is in src/LICENSE and in per-file headers (the root build.sh carries the same header); there is no root LICENSE file. [retier] Archived DeepMind research JIT for CPython 3.7 only; the 9.5x Richards figure is on unnamed internal machines with one time.time() run per mode, the Richards result discarded and 50 default iterations against the README's 100. @s6.jit runs at import and calls Initialize(adopt_types=true), swapping tp_setattro to GenericSetAttrUsingClasses and hooking tp_new before the 'Default Python 3.7' baseline is timed, so the baseline is S6-instrumented rather than stock CPython. Dockerfile baseline: clang 13, non-PGO CPython with frame pointers. Last commit 2022-09-14.

Standalone JIT library for CPython 3.7 (strongjit IR lowered to x86 with asmjit); emits x86 machine code via asmjit; calls into C APIs such as NumPy are bottlenecked by C API call time; needs the project's Docker build.

## Maintenance

Abandoned: archived 2023-07-05 after one Copybara import commit (2022-09-14) and tied to CPython 3.7; Apache-2.0 (src/LICENSE and per-file headers), so the code can be copied, but in practice it is a reference design rather than a usable dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** The README gives first-party speedups against CPython 3.7, and the benchmark scripts are public in src/benchmarks/ (richards.py, raytrace.py, unpack_sequence_fast.py, unpack_sequence_slow.py). The Dockerfile names clang 13, but the headline 9.5x and 3-4.5x numbers come from unnamed 'internal dev machines' with no CPU model, so C.
- **Verifier notes:** The claimed speedups match the README (7x Richards at 100 iterations 'depending on your hardware', 9.5x on internal machines, raytrace 3-4.5x, unpack_sequence 0.2x/0.97x, 'up to 10x'). Last commit corrected from null to 2022-09-14. Main shortcomings: archived, CPython 3.7 only, a single-run harness that does not check results, and no hardware named. The real category is wave 12's jits (it is a JIT for CPython), not language-interpreters.
- **Fields the verifier corrected:** `last_commit`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/deepmind/s6>
  - <https://github.com/deepmind/s6/commits/main>
  - <https://github.com/deepmind/s6/tree/main/src>
  - <https://github.com/deepmind/s6/tree/main/src/benchmarks>
  - <https://github.com/deepmind/s6/tree/main/notebooks>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/README.md>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/LICENSE>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/build.sh>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/benchmarks/richards.py>
- **Sources the enricher read:**
  - <https://github.com/deepmind/s6>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/README.md>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/build.sh>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/LICENSE>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/CMake/deps.cmake>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/benchmarks/richards.py>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/benchmarks/raytrace.py>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/benchmarks/unpack_sequence_fast.py>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/benchmarks/unpack_sequence_slow.py>
  - <https://github.com/deepmind/s6/tree/main/src>
  - <https://github.com/deepmind/s6/tree/main/src/python>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/python/api.cc>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/api.cc>
  - <https://github.com/deepmind/s6/tree/main/src/runtime>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/runtime/interposer.cc>
  - <https://github.com/deepmind/s6/tree/main/src/classes>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/classes/object.cc>
  - <https://raw.githubusercontent.com/deepmind/s6/HEAD/src/classes/getsetattr.cc>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/deepmind/s6`) · [data/wave12/enrich/raw/github_com_deepmind_s6.json](../../../data/wave12/enrich/raw/github_com_deepmind_s6.json) (enrichment confidence 0.75)

</details>
