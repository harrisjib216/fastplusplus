# CPython copy-and-patch JIT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Python-2.0` · 🟢 active

> CPython's built-in experimental copy-and-patch trace JIT; 7.5% (x86-64 Linux) to 11% (macOS arm64) geomean over the plain interpreter.

| | |
|---|---|
| **Beats** | CPython standard interpreter (tail-calling interpreter on AArch64 macOS), built with all optimizations |
| **Claimed result** | Python 3.15 What's New: 7-8% geomean pyperformance gain over the standard interpreter on x86-64 Linux and 11-12% over the tail-calling interpreter on AArch64 macOS, the two best platforms. At the same commit 80f9aa0 (2026-09-25) the published pyperf JSONs give Raspberry Pi 5 Linux aarch64 0.999x (39 of 105 benchmarks slower, html5lib 0.67x) and Windows x86-64 1.044x (unpack_sequence 0.36x); counting the 13 benchmarks bench_runner.toml excludes, x86-64 falls from 1.075 to 1.064 and macOS from 1.113 to 1.101 (derived from page data). pyperf_bench GCC 13.3.0 PGO+LTO i5-8400 run: 1.079x geomean. |
| **Workload** | pyperformance 1.14.0 suite run by bench_runner (13 benchmarks excluded from the geomean, including unpack_sequence, pickle and asyncio_tcp), JIT-enabled build versus the same CPython commit (main, 3.16.0a0, 80f9aa0, 2026-09-25) built without the JIT. |
| **Metric** | throughput |
| **Hardware** | x86-64: Intel Core i5-8400 @ 2.80GHz (6 cores, intel_pstate no turbo, performance governor), Linux 6.8.0, glibc 2.39 (runner 'ripley'). AArch64: Apple Silicon Mac on macOS 26.5.2 (runner 'jones'; CPU model not recorded in metadata). |
| **Compiler and flags** | x86-64 Linux run: GCC 13.3.0, CFLAGS -O3 -DNDEBUG -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer, configure --enable-optimizations --with-lto=full (PGO+LTO) with and without --enable-experimental-jit=yes. macOS arm64 run: Clang 21.0.0 (clang-2100.1.1.101), same configure flags plus --with-tail-call-interp on both sides. JIT stencils are generated at build time with LLVM 21 (Tools/jit/README.md). Flags from pyperf JSON metadata in savannahostrowski/pyperf_bench. |
| **Adoption** | 77.5k stars; reference Python implementation |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/python/cpython) · [benchmark](https://github.com/savannahostrowski/pyperf_bench/blob/main/results/bm-20260925-3.16.0a0-80f9aa0-JIT/bm-20260925-ripley-x86_64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0-vs-base.md) |

## Verdict

pyperformance 1.14.0 via bench_runner on main commit 80f9aa0 (3.16.0a0, 2026-09-25), JIT build against the same commit without the JIT, both PGO+LTO. Intel i5-8400, GCC 13.3.0, turbo off: 1.079x (README), 1.075x over 105 benchmarks. Apple Silicon macOS, Clang 21, both tail-calling: 1.113x. Per benchmark the range is 0.82x (k_core) to 2.47x (richards_super), and the same run shows 0.999x on a Raspberry Pi 5 and 1.044x on Windows x86-64 (all ratios derived from the pyperf JSONs).

## Use it when

- You are already on CPython 3.14/3.15 and want a free few-percent throughput gain on long-running pure-Python, loop-heavy code without changing implementation; try PYTHON_JIT=1 on the official macOS/Windows installers or a --enable-experimental-jit build
- Numeric and object-oriented inner loops in plain Python (the 2026-09-25 run shows richards 2.4x, nbody 1.5x, scimark_sor 1.4x, spectral_norm 1.4x on x86-64 Linux)
- x86-64 Linux and Apple Silicon macOS, the two platforms where the published geomean gains (1.075x and 1.113x, derived from page data) were measured
- You need every C extension and the exact CPython semantics, which rules out PyPy, GraalPy or a fork like Cinder

## Skip it when

- Linux AArch64: in the same 2026-09-25 commit run, a Raspberry Pi 5 runner (blueberry, GCC 12.2.0) gets a 1.001x geomean (README table), with 39 of 105 benchmarks slower; html5lib 0.67x, django_template 0.74x, dulwich_log 0.75x (derived from page data)
- Free-threaded (--disable-gil) builds: configure warns that the JIT is built but never used there (GH-133171)
- Production services that need stability: the docs still call it experimental and not recommended for production, and the tracker lists 81 open topic-JIT issues, including stack and frame-local corruption (#158804, #156319, #155823) and wrong guard checks (#158380)
- Template-, parser- and generator-heavy code (django_template, html5lib, k_core, mdp, pycparser regress on x86-64 Linux, Windows and macOS) and code made of long straight-line unpacking or other generated code (unpack_sequence runs 0.36x to 0.71x)
- Profiling with -X perf: the JIT turns itself off with a RuntimeWarning when perf profiling support is active

## How it is fast

Hot loops are found by backoff counters (JUMP_BACKWARD starts at 4000, RESUME at 8190). A tracing front end then records the actual path through the specialised tier-1 bytecode as a trace of micro-ops. The tier-2 optimizer does type and constant propagation, removes guards and refcount updates, and caches up to three top-of-stack values in registers (_tos_cache0-2). Code generation is copy-and-patch: at build time Clang/LLVM 21 compiles every micro-op from Tools/jit/template.c into a machine-code stencil (-Os, preserve_none, musttail), and at run time _PyJIT_Compile copies the stencils end to end and patches in operands, jump targets and GOT/trampoline addresses. No compiler runs at run time.

## Compared with alternatives

Pick it when you must stay on upstream CPython. Cinder reports 1.5-4x but is Meta's fork with its own release cadence, and PyPy/GraalPy are separate runtimes. BeamAsm is the closest analogue (an in-tree JIT of a reference VM), but it gives about 50% on estone where CPython's gives 7-11%. PochiVM and WasmNow show the same copy-and-patch technique as libraries for building your own compiler, not a Python speedup.

## Integration

| | |
|---|---|
| **Form** | build option of the CPython interpreter (configure --enable-experimental-jit / build.bat --experimental-jit); prebuilt but off by default in the official 3.14+ macOS and Windows installers |
| **Dependencies** | none at run time; building needs LLVM 21 (clang, llvm-readobj, llvm-objdump, llvm-dwarfdump) and a Python 3.11+ to run Tools/jit/build.py. The rest of CPython can be built with any compiler (GCC, MSVC). |
| **Minimum toolchain** | LLVM/Clang 21 for stencils (needs musttail and preserve_none); CPython 3.13+ (3.15 for the tracing front end and register caching) |
| **Platforms** | x86-64 and AArch64 on Linux (glibc triples), macOS and Windows, plus i686 Windows (Tools/jit/_targets.py); other triples raise ValueError at build time |
| **Thread safety** | GIL builds only; the JIT is inactive in free-threaded builds |
| **Drop-in for the baseline** | partial — same interpreter, same ABI and extensions, but you need a JIT-enabled build (or the official macOS/Windows installer) and PYTHON_JIT=1 where it ships off |

## Gotchas

- Benchmark-reporting flaw: the What's New 7-8% and 11-12% figures cite only x86-64 Linux and macOS arm64. The same 2026-09-25 commit was also run on Linux AArch64 (Raspberry Pi 5), at 0.999x (derived from the pyperf JSONs; 1.001x in the README table), and on Windows x86-64 (MSVC, tail-calling interpreter on both sides), at 1.044x. The geomean also drops 13 benchmarks via bench_runner.toml excluded_benchmarks. With them included, x86-64 falls from 1.075x to 1.064x and macOS from 1.113x to 1.101x (derived from page data). The numbers are real, but they are the best two platforms.
- pyperf runs the JIT build in its JIT mode: 6 processes x 10 values against 20 x 3 for the interpreter, so more in-process warm-up. Re-computing with only the first 3 values per JIT process gives the same geomean (1.075x x86-64, 1.111x macOS), so warm-up does not inflate the result. Short-lived scripts that never reach the 4000-iteration trace threshold will not benefit.
- Each executor gets its own page-rounded mmap (RW, then mprotect to RX, no W+X window), so many small traces cost at least a page each. Issue #149212 reports unpack_sequence splitting into about 22 chained traces, roughly 18 MB of machine code, and about 2.7x more dispatches than tier 1, because a _CHECK_VALIDITY + _SET_IP pair is inserted before every bytecode.
- Native unwinding through JIT frames arrived only in 3.15 (GDB JIT interface and libgcc frame registration on Linux ELF). On 3.14, gdb and perf cannot walk through JIT frames, and test_gdb JIT unwinding is still flaky on aarch64 (#157965).

## Known shortcomings

- Not faster than PyPy or any jits baseline: the copy-and-patch JIT's pyperf_bench numbers (GCC 13.3.0, PGO+LTO, i5-8400) show a 1.079x geomean over the plain CPython 3.16.0a0 main build, with unpack_sequence 1.4-1.8x slower; experimental and off by default.
- Enricher: the What's New 7-8% and 11-12% cite only the best 2 platforms; at the same 2026-09-25 commit 80f9aa0 a Raspberry Pi 5 (Linux aarch64) gives a 0.999x geomean (README 1.001x) with 39 of 105 benchmarks slower (html5lib 0.67x) and Windows x86-64 1.044x (unpack_sequence 0.36x); the geomean skips 13 benchmarks listed in bench_runner.toml (counting them: x86-64 1.075 to 1.064, macOS 1.113 to 1.101, derived from the pyperf JSONs). 81 open topic-JIT issues including stack and frame corruption; inactive on free-threaded builds; off under -X perf.

## Caveats and trade-offs

Compares the JIT with CPython's own interpreter, not with PyPy, LuaJIT, V8 or HotSpot, so it does not beat the jits category baselines; the gain is small (7-12% geomean) and some benchmarks slow down (k_core 11-18% slower; unpack_sequence, excluded from the geomean, about 1.4-1.8x slower, derived from the run's JSON). The JIT is still experimental and off by default (--enable-experimental-jit). Numbers come from a main-branch 3.16.0a0 build (commit 80f9aa0, 2026-09-25), not a 3.15 release binary. Runs are by a CPython core developer's own runners (savannahostrowski/pyperf_bench, doesjitgobrrr.com dashboard, which was blocked here); the macOS runner's CPU model is not recorded. Included as a flagged entry for the copy-and-patch lineage (stencils built with LLVM 21). License file is the Python license stack (PSF License Version 2 and predecessors, SPDX Python-2.0) plus 0BSD for documentation code; GitHub shows it as Other.

Experimental, off by default; enabled at build time with --enable-experimental-jit and at run time with PYTHON_JIT. Needs LLVM only at build time. Per the 3.14 notes it is not recommended for production and free-threaded builds do not support it. Machine-code unwinding support added in 3.15.

## Maintenance

Actively developed in CPython main (77.5k stars, daily commits) under the PSF licence, but still experimental and off by default with many open crash and miscompile reports; treat it as a free opt-in experiment on x86-64 Linux or macOS, not a production feature.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded C to A: the What's New numbers link to the 2026-09-25 doesjitgobrrr run, whose raw data is public in savannahostrowski/pyperf_bench (results/bm-20260925-3.16.0a0-80f9aa0-JIT/...-ripley-x86_64-...-vs-base.md: overall geometric mean 1.079x faster), run with pyperformance 1.14.0 via bench_runner (bench_runner.toml), and the pyperf JSON metadata states the compiler (GCC 13.3.0, -O3), configure flags (--enable-optimizations --with-lto=full --enable-experimental-jit=yes) and CPU (Intel Core i5-8400 @ 2.80GHz, turbo off, performance governor). The macOS AArch64 run states Clang 21.0.0 and flags but no CPU model.
- **Verifier notes:** ID ALERT: rendered id was https://github.com/python/cpython, but merge.py re-ran after rendering and that id now belongs to 'CPython tail-calling interpreter' (language-interpreters); this JIT record is now https://github.com/python/cpython#jits in merged.json, so this verdict is keyed to #jits (the tail-calling interpreter entry still needs its own verifier). Upgraded C to A on the public pyperf_bench data with compiler, flags and CPU in the JSON metadata; shortcomings: not faster than PyPy or any jits baseline, small gain, some benchmarks regress (unpack_sequence 1.4-1.8x slower), experimental and off by default.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.15.rst>
  - <https://github.com/python/cpython>
  - <https://github.com/python/cpython/commits>
  - <https://raw.githubusercontent.com/python/cpython/main/LICENSE>
  - <https://raw.githubusercontent.com/python/cpython/main/Tools/jit/README.md>
  - <https://github.com/savannahostrowski/doesjitgobrrr>
  - <https://github.com/savannahostrowski/pyperf_bench>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/bench_runner.toml>
  - <https://github.com/savannahostrowski/pyperf_bench/blob/main/results/bm-20260925-3.16.0a0-80f9aa0-JIT/bm-20260925-ripley-x86_64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0-vs-base.md>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-JIT/bm-20260925-ripley-x86_64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0-vs-base.md>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-JIT/bm-20260925-ripley-x86_64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0/bm-20260925-ripley-x86_64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-TAILCALL/bm-20260925-jones-arm64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-JIT%2CTAILCALL/bm-20260925-jones-arm64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/python/cpython/main/Tools/jit/README.md>
  - <https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.15.rst>
  - <https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.14.rst>
  - <https://raw.githubusercontent.com/python/cpython/main/Doc/whatsnew/3.13.rst>
  - <https://raw.githubusercontent.com/python/cpython/main/Python/jit.c>
  - <https://raw.githubusercontent.com/python/cpython/main/Tools/jit/template.c>
  - <https://raw.githubusercontent.com/python/cpython/main/Tools/jit/_targets.py>
  - <https://raw.githubusercontent.com/python/cpython/main/Tools/jit/build.py>
  - <https://raw.githubusercontent.com/python/cpython/main/Tools/jit/_stencils.py>
  - <https://raw.githubusercontent.com/python/cpython/main/Tools/jit/_optimizers.py>
  - <https://raw.githubusercontent.com/python/cpython/main/Python/optimizer.c>
  - <https://raw.githubusercontent.com/python/cpython/main/Python/optimizer_analysis.c>
  - <https://raw.githubusercontent.com/python/cpython/main/Include/internal/pycore_optimizer.h>
  - <https://raw.githubusercontent.com/python/cpython/main/Include/internal/pycore_backoff.h>
  - <https://raw.githubusercontent.com/python/cpython/main/configure.ac>
  - <https://raw.githubusercontent.com/python/cpython/main/Python/pylifecycle.c>
  - <https://github.com/python/cpython/issues?q=is%3Aissue%20state%3Aopen%20label%3Atopic-JIT>
  - <https://github.com/python/cpython/issues/149212>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/bench_runner.toml>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-JIT/bm-20260925-ripley-x86_64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0-vs-base.md>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-JIT/bm-20260925-blueberry-aarch64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0-vs-base.md>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0/bm-20260925-ripley-x86_64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-JIT/bm-20260925-ripley-x86_64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0/bm-20260925-blueberry-aarch64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-JIT/bm-20260925-blueberry-aarch64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-TAILCALL/bm-20260925-jones-arm64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-JIT%2CTAILCALL/bm-20260925-jones-arm64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-TAILCALL/bm-20260925-prometheus-amd64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
  - <https://raw.githubusercontent.com/savannahostrowski/pyperf_bench/HEAD/results/bm-20260925-3.16.0a0-80f9aa0-JIT%2CTAILCALL/bm-20260925-prometheus-amd64-python-80f9aa0b18d96509eec3-3.16.0a0-80f9aa0.json>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/python/cpython#jits`) · [data/wave12/enrich/raw/github_com_python_cpython_jits.json](../../../data/wave12/enrich/raw/github_com_python_cpython_jits.json) (enrichment confidence 0.8)

</details>
