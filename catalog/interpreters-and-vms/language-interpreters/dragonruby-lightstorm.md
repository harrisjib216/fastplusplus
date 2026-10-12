# Lightstorm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Ahead-of-time compiler from mruby 3.0 bytecode to C via MLIR/EmitC; about 1.4x faster than the mruby VM on aobench.

| | |
|---|---|
| **Beats** | mruby VM executing the same program's precompiled bytecode (tests/benchmarks/bench.py pairs 'lightstorm &lt;bench&gt;' with 'mruby &lt;bench&gt;' built from mrbc bytecode linked to mruby_static); the README chart labels it only 'Baseline' |
| **Claimed result** | README: 'The compiled version (rightmost) decreases total execution time by nearly \~30%'. Reading the aobench.png bar chart: time about 78% of baseline for Compiled and about 71% for Compiled + escape + CSE (about 1.4x faster, derived from page data); the bar labelled 'Misses' (type not stated) is about 47% and 43% of baseline (values read off the chart). |
| **Workload** | aobench ray-tracing benchmark (openbenchmarking aobench) compiled ahead of time to C through LLVM versus the interpreted baseline. |
| **Metric** | throughput |
| **Compiler and flags** | Generated C and lightstorm_runtime.c: CMake Release (-O3), -flto only with LIGHTSTORM_LTO; baseline libmruby (pinned mruby 3.0.0 commit 0f45836) built with CFLAGS=LIGHTSTORM_CFLAGS, which is '-g' by default (gcc.rake drops its -O3 when CFLAGS is set), so unoptimized unless LIGHTSTORM_LTO is on |
| **Adoption** | 143 stars |
| **Last commit** | 2024-12-13 |
| **Links** | [repository](https://github.com/DragonRuby/lightstorm) · [benchmark](https://github.com/DragonRuby/lightstorm) |

## Verdict

One first-party bar chart for the aobench Ruby port: total time about 78% of the mruby 3.0 bytecode VM for plain compiled output and about 71% with escape analysis plus CSE (about 1.4x faster, derived from page data), with cycles, instructions, branches, 'misses' and loads/stores also lower; the harness is hyperfine (one warm-up run) over the Lightstorm executable and the same program as mruby bytecode, built with clang 19, but CPU, run count and whether LIGHTSTORM_LTO was set are not stated. The LLVM blog post (blocked here; search snippet only) says other benchmarks ranged from 1% to 1200% speedups, but those numbers are not in the repo.

## Use it when

- Embedding mruby (for example a game scripting layer, the DragonRuby use case) and wanting to ship hot, float-heavy scripts as native code instead of bytecode.
- Numeric loops written with while loops, plain methods and instance variables, which is exactly the shape of the aobench port it was tuned on.
- Research or teaching: a compact (about 1,000-line bytecode converter) example of building a language AOT compiler on MLIR with the EmitC dialect, so the output is portable C rather than target-specific LLVM IR.
- Targets where JIT is not allowed (consoles, iOS) but an extra C compile step in the build is fine.

## Skip it when

- Any normal Ruby program: the converter rejects blocks, lambdas, yield, rescue/raise, super, default, variadic, keyword and block arguments, OP_ASET and several other opcodes (lib/compiler/converter.cpp), so idiomatic code using .times or .each does not compile; the aobench port itself had its .times blocks rewritten as while loops.
- CRuby/MRI workloads or Rails: it is built on mruby 3.0.0 (pinned submodule commit 0f45836) and its default gembox, not CRuby, and it is not compared against CRuby or YJIT at all; Spinel or TruffleRuby are the siblings to look at there.
- Code that relies on Ruby exceptions: any exception raised inside a call made through ls_send_argv is caught, printed and the process calls abort().
- Production use: version 0.1.0, no issues filed, no releases, last commit 2024-12-13, and only one benchmark published.
- If you need a large speedup on call-heavy code: method dispatch is still mrb_funcall_argv without inline caching ('TODO: add caching' in the runtime), so gains are limited to removing dispatch and boxing overhead.

## How it is fast

It removes the mruby interpreter's fetch/decode/dispatch loop by turning each bytecode op into a call to an always_inline C helper from lightstorm_runtime.c, which the generated file #includes, so the C compiler can inline and optimize across ops (integer/float fast paths for arithmetic and comparisons, falling back to mrb_funcall_argv for everything else). Two MLIR passes run before emission: a simple escape analysis ('EscapeAnalysisAtHome') that gives arithmetic results consumed only by other arithmetic ops a stack-allocated RFloat slot instead of a GC-heap float, and MLIR's standard common-subexpression elimination. Method sends, ivar access and object allocation still go through the regular mruby runtime, which is why instructions only drop about 12-21% on the chart.

## Compared with alternatives

Pick Lightstorm over Spinel or TruffleRuby only if you are already on mruby (for example embedding it in a game) and can restrict hot code to its block-free subset; Spinel is the catalogued choice for big AOT speedups over CRuby (about 8.5x over YJIT on 28 benchmarks), and TruffleRuby or YJIT if you need full Ruby. Against LuaAOT, the closest analogue (AOT of a small embeddable VM's bytecode to C, 1.2x-2.6x over Lua), Lightstorm shows a similar size of gain but on one benchmark only.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | LLVM 19 with MLIR (find_package LLVM and MLIR), CMake 3.28+ and Ninja to build the compiler; bundled mruby 3.0.0 submodule (built with rake, so Ruby/rake is needed); hyperfine and Python 3 for the benchmark target; lit and filecheck for integration tests |
| **Minimum toolchain** | C++20 for the compiler; clang-19 (Ubuntu preset) or Homebrew llvm@19 (macOS preset); generated code is C compiled with clang |
| **Platforms** | Ubuntu and macOS build presets; generated C is meant to be portable, other OSes not documented |
| **Thread safety** | not documented (single mrb_state per program, as in mruby) |
| **Drop-in for the baseline** | partial — same mruby 3.0 runtime and semantics for the supported subset, but whole-program AOT to an executable; no runtime eval/require of new code and large parts of Ruby syntax rejected at compile time |

## Gotchas

- Harness flaw in the published benchmark setup: cmake/mruby.cmake builds the whole mruby library with CFLAGS set to LIGHTSTORM_CFLAGS, which is just '-g' unless LIGHTSTORM_LTO is set, and mruby's gcc/clang toolchain (tasks/toolchains/gcc.rake at the pinned commit) replaces its default '-g -O3' with ENV['CFLAGS'], so in the default configuration the baseline mruby VM (vm.c and the rest of libmruby.a) is compiled without optimization while the Lightstorm-generated C and its inlined runtime get CMake's Release -O3. The README chart does not say which configuration produced it, so the \~30% gain may partly be -O3 vs -O0 (from reading the build files; not reproduced here).
- The escape-analysis pass only checks that every user of an arithmetic result is another arithmetic op; if that consumer falls back to a user-defined operator method (for example a custom Vec#\* taking a Float argument), a pointer to a stack-allocated RFloat is passed into Ruby code that can store it, which would dangle after the function returns (from reading lib/optimizations/optimizations.cpp; not tested).
- Arithmetic fast paths do not check whether Integer or Float operators have been redefined (the 'need to check if op is overridden' comment has no check behind it), matching mruby's own VM shortcuts but not CRuby semantics.
- bench.py runs hyperfine on both executables without comparing their stdout, so the benchmark itself does not check that the compiled and interpreted aobench render the same image; the image is only 64x64 with 2 subsamples and 8 AO samples, so process startup (mrb_open with the default gembox) is part of the measured time.

## Known shortcomings

- One aobench PNG chart against the mruby bytecode VM (tests/benchmarks/bench.py with hyperfine), about 1.4x (derived from page data), with no hardware or run details; -O3 -flto only with LIGHTSTORM_LTO. Off-baseline (mruby), stale since 2024-12-13.
- Enricher: cmake/mruby.cmake builds all of libmruby with CFLAGS=LIGHTSTORM_CFLAGS, which is just '-g' unless LIGHTSTORM_LTO is set, and mruby's gcc.rake (pinned commit 0f45836, mruby 3.0.0) replaces its default -O3 with that CFLAGS, so by default the baseline mruby VM is unoptimized while the generated C and inlined lightstorm_runtime.c get CMake Release -O3; the chart does not say which configuration produced it, so the about 1.4x gain may be partly -O3 against -O0. The escape-analysis pass can hand a stack RFloat to a user-defined operator method (possible dangling reference, from code reading); the converter rejects blocks, lambdas, yield, exceptions, super and kwargs; aobench was rewritten with while loops; bench.py does not compare outputs.

## Caveats and trade-offs

One benchmark (aobench, tests/benchmarks/bm_ao_render.rb) and the numbers exist only in a PNG chart; the baseline is mruby's bytecode VM (not CRuby MRI or YJIT), confirmed from tests/benchmarks/bench.py although the README does not name it; no hardware, run count or build configuration is given for the chart; the LLVM blog post with more detail (blog.llvm.org/posts/2024-12-03-minimalistic-ruby-compiler) could not be opened here (egress blocked); last commit December 2024. [retier] One aobench PNG chart against the mruby bytecode VM (tests/benchmarks/bench.py with hyperfine), about 1.4x derived, no hardware or run details; by default the baseline mruby is built without an -O flag while the generated C gets -O3, and the chart does not say which configuration it used. The converter rejects blocks, lambdas, yield, exceptions, super and kwargs; aobench was rewritten with while loops; bench.py does not compare outputs; the escape-analysis pass may hand a stack RFloat to a user-defined operator method. Off-baseline (mruby), stale since 2024-12-13.

Minimalistic ahead-of-time Ruby compiler (simplified Firestorm that targets C, built on mruby); it is not a full CRuby/MRI replacement and compiles only what the project supports.

## Maintenance

Stale since 2024-12-13 at version 0.1.0 with no releases or issues; MIT-licensed and small, so it is better read as a reference design for an MLIR/EmitC Ruby AOT compiler than adopted as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers only: one aobench bar chart (aobench.png) in the README; the harness tests/benchmarks/bench.py (hyperfine, lightstorm binary vs the same program as mruby bytecode) and clang-19 presets are public, but no CPU model, run count or exact build configuration is tied to the chart.
- **Verifier notes:** Chart values in the record are read correctly (78% and 71% time); the inferred mruby baseline is confirmed by bench.py, which times lightstorm vs mruby bytecode with hyperfine. Shortcomings: single benchmark shown, chart only, no hardware or run details, stale since 2024-12-13, and only about 1.4x vs an interpreter. Metadata checked: MIT, 143 stars, last commit 2024-12-13 (stale).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/DragonRuby/lightstorm>
  - <https://github.com/DragonRuby/lightstorm/commits/main>
  - <https://github.com/DragonRuby/lightstorm/tree/main/tests/benchmarks>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/README.md>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/aobench.png>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/cmake/lightstorm.cmake>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/tests/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/tests/benchmarks/bench.py>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/DragonRuby/lightstorm>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/README.md>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/aobench.png>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/CMakePresets.json>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/cmake/lightstorm.cmake>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/cmake/mruby.cmake>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/cmake/version.cmake>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/tests/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/tests/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/tests/benchmarks/bench.py>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/tests/benchmarks/benchmarks_bytecode_main.c>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/tests/benchmarks/bm_ao_render.rb>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/lib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/lib/runtime/CMakeLists.txt>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/lib/runtime/lightstorm_runtime.c>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/lib/runtime/lightstorm_runtime_main.c>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/lib/optimizations/optimizations.cpp>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/lib/conversion/c_conversion.cpp>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/lib/compiler/compiler.cpp>
  - <https://raw.githubusercontent.com/DragonRuby/lightstorm/HEAD/lib/compiler/converter.cpp>
  - <https://github.com/DragonRuby/lightstorm/tree/main/third_party>
  - <https://github.com/DragonRuby/lightstorm/tree/main/lib/runtime>
  - <https://github.com/DragonRuby/lightstorm/tree/main/lib/optimizations>
  - <https://github.com/DragonRuby/lightstorm/tree/main/lib/conversion>
  - <https://github.com/DragonRuby/lightstorm/tree/main/lib/compiler>
  - <https://github.com/DragonRuby/lightstorm/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/mruby/mruby/0f45836b5954accf508f333f932741b925214471/tasks/toolchains/gcc.rake>
  - <https://raw.githubusercontent.com/mruby/mruby/0f45836b5954accf508f333f932741b925214471/tasks/toolchains/clang.rake>
  - <https://raw.githubusercontent.com/mruby/mruby/0f45836b5954accf508f333f932741b925214471/build_config/default.rb>
  - <https://raw.githubusercontent.com/mruby/mruby/0f45836b5954accf508f333f932741b925214471/Rakefile>
  - <https://raw.githubusercontent.com/mruby/mruby/0f45836b5954accf508f333f932741b925214471/include/mruby/version.h>
  - <https://raw.githubusercontent.com/mruby/mruby/HEAD/tasks/toolchains/gcc.rake>
  - https://blog.llvm.org/posts/2024-12-03-minimalistic-ruby-compiler/ (EGRESS_BLOCKED; WebSearch snippet only)
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/dragonruby/lightstorm`) · [data/wave12/enrich/raw/github_com_dragonruby_lightstorm.json](../../../data/wave12/enrich/raw/github_com_dragonruby_lightstorm.json) (enrichment confidence 0.75)

</details>
