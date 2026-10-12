# hxcpp (Haxe C++ backend and runtime)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-1-Clause` · 🟢 active

> Runtime and build tool for Haxe's C++ target; native output beats the HashLink/JIT and Neko VM targets on CPU-bound benchmarks.

| | |
|---|---|
| **Beats** | NekoVM and HashLink (HL/JIT) Haxe targets; also compared with Haxe's JVM/Java and JavaScript (Node) targets |
| **Claimed result** | tong's gist run of the HashLink other/benchs suite: cpp total 0.7166 s vs HashLink 5.678 s (7.9x) and Neko 27.16 s (37.9x) in 2018 (derived from page data); Node (about 0.45-0.53 s once the double-counted js rows are summed once) and the JVM match or beat cpp, so hxcpp is not the fastest Haxe target overall. |
| **Workload** | tong's gist 'Haxe benchmarks' (one results file, three revisions, last active 2025-09-20) running the HashLink repository's other/benchs suite (Startup, Anonymous, BinaryTrees, Fib, FloatArray, IntArray, Mandelbrot, NBodies) compiled from the same Haxe source to each target (js, cpp, cs, hl, java, lua, neko, php, python; hlc and jvm in the 2025 rerun). In the upstream runner each program is re-launched until 1 s of total time accumulates (first run discarded), the output is checked against the expected @:result value, the per-target Startup time is subtracted, and the mean is truncated to 0.01 s. 2018 run plus a September 2025 rerun in a comment. |
| **Metric** | throughput |
| **Hardware** | 2018 run: Intel Core i5-6600 @ 3.9 GHz, 15959 MB, Arch Linux x86_64, kernel 4.17.2. 2025 rerun: AMD Ryzen 7 7700 @ 5.39 GHz, 32 GB, Arch Linux, kernel 6.16.8. |
| **Compiler and flags** | Not stated in the gist. The upstream HashLink runner (other/benchs/Benchs.hx) compiles each benchmark with haxe -cpp cpp -main &lt;name&gt; -dce full -D HXCPP_SILENT -D HXCPP_GC_GENERATIONAL and leaves C++ compilation to hxcpp's default toolchain; the gist's own runner, which adds cs, java, lua, php and python targets, is not included in the gist, so its flags are unconfirmed. |
| **Adoption** | 329 stars; the C++ target of the Haxe compiler (3,138 commits) |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/HaxeFoundation/hxcpp) · [benchmark](https://gist.github.com/tong/84992efadb204c2140e24dbdbeeee06c) |

## Verdict

An independent gist (tong) ran HashLink's other/benchs suite (Anonymous, BinaryTrees, Fib, FloatArray, IntArray, Mandelbrot, NBodies) across Haxe targets on an Intel Core i5-6600 in 2018 and an AMD Ryzen 7 7700 in 2025: hxcpp's total runtime was 0.72 s versus 5.68 s for HashLink/JIT and 27.16 s for Neko (about 7.9x and 38x, derived from page data), and in 2025 cpp beat hl on every row (for example Mandelbrot 0.13 s vs 1.32 s). Compiler, flags and Haxe/hxcpp versions are not stated, the 2018 JS total is double-counted and hlc never produced a valid result.

## Use it when

- You already write Haxe and want the fastest native target for CPU-bound code: numeric loops, typed arrays and allocation-heavy trees (2018: Mandelbrot 0.13 s vs 4.28 s HL/JIT and 9.65 s Neko).
- Shipping a native desktop, mobile or console binary from Haxe (Linux, macOS, Windows, Android, iOS toolchains are in toolchain/) where neither a JS engine nor the HashLink VM is wanted.
- Code that must link with existing C/C++ libraries through Haxe externs.
- Development loops can use cppia scripts and keep full C++ builds for releases.

## Skip it when

- Fast edit-build cycles: each small benchmark took about 2 s to build in the 2018 run versus 0.02 to 0.2 s for js, hl and neko; the HXCPP_COMPILE_CACHE object cache (docs/CompileCache.md) avoids recompiling unchanged runtime files, but generated code still goes through the C++ compiler.
- Code dominated by anonymous structures or Dynamic access: Anonymous ran 0.38 s on cpp versus 0.29 s on HL/JIT and 0.02 s on Node in 2018.
- When Node (V8) or the JVM target is acceptable: they matched or beat cpp on several rows in both runs (2025 Anonymous 0.02/0.03 s vs 0.1 s; Mandelbrot 0.07 s vs 0.13 s), and Node's 2018 total was lower once counted once (see gotchas).
- Projects that need HashLink/C (hlc), HashLink's own AOT C path: the benchmarks never produced a valid hlc number, so it is unknown whether hxcpp beats it.
- Code that cannot tolerate a conservative stop-the-world GC or that runs foreign threads without registering them with the collector.

## How it is fast

Ahead-of-time translation of statically typed Haxe to C++ compiled by g++/clang/MSVC (the default Linux toolchain passes -O2), so typed arithmetic, arrays and method calls become plain native code instead of bytecode run by the Neko interpreter or HashLink's JIT. Memory is managed by an Immix-style mark-region collector (src/hx/gc/Immix.cpp) with conservative stack scanning and an opt-in generational mode (HXCPP_GC_GENERATIONAL), which the HashLink benchmark runner enables for the cpp target.

## Compared with alternatives

The catalogued siblings are Wasm and EVM engines (Wasmi, WAMR, wasm3, wasm2go, PolkaVM), which run portable bytecode; pick hxcpp only when the source language is Haxe. Like wasm2go, it gets its speed by translating to a host language's compiler instead of interpreting or JIT-compiling.

## Integration

| | |
|---|---|
| **Form** | haxelib package: runtime headers plus a static runtime library and build tool that compile the generated C++ into an executable or shared library |
| **Dependencies** | Haxe 4 compiler and haxelib; a C++ toolchain (g++ by default on Linux, clang on Apple, MSVC on Windows); bundled third-party sources (mbedtls, sqlite, zlib, pcre2) built on demand |
| **Minimum toolchain** | Haxe 4 (Changes.md: 'Removed Haxe 3 support'); C++ standard not documented beyond an optional HXCPP_CPP17 define |
| **Platforms** | Linux (x86, x86-64, Raspberry Pi), macOS, Windows (including Arm64), Android, iOS; emscripten mentioned in docs |
| **Thread safety** | Multi-threaded with a conservative stop-the-world GC: threads must cooperate, call GCEnterBlocking/GCExitBlocking around blocking system calls, and foreign threads must attach with SetTopOfStack (docs/ThreadsAndStacks.md) |
| **Drop-in for the baseline** | partial: same Haxe source, switch -hl/-neko to -cpp, but it needs a C++ toolchain and much longer builds, and some library behaviour has differed between targets (Changes.md lists fixes aligning indexOf and directory reading with other targets) |

## Gotchas

- The gist's 2018 totals double-count JavaScript: every block lists two rows labelled js with near-identical runtimes, each js row set sums to 0.43 to 0.45 s (truncated), while the js total is 0.962 s, matching their sum; every other target's total matches its own row sum. Counted once, Node's total (about 0.45 to 0.53 s) is below cpp's 0.717 s, so 'C++ fastest overall' does not hold for 2018 (derived from page data); the wins over HashLink (5.68 s) and Neko (27.16 s) are unaffected.
- Every 2025 hlc row fails with 'result 0 but expected ...', and 0 is exactly the expected output of the suite's _Startup program, which suggests the gist runner kept executing a stale hlc binary (inference). The result check caught it, but it leaves no hlc number at all.
- Timings are whole-process wall time minus a per-target startup time taken from _Startup, averaged until 1 s accumulates and truncated to 0.01 s (other/benchs/Benchs.hx), so cpp cells of 0 or 0.01 s are at the timer's resolution and small ratios are noise. Haxe, hxcpp and C++ compiler versions are not given; hxcpp's default Linux build is g++ -O2 without LTO (-flto only with HXCPP_OPTIMIZE_LINK), and whether the gist kept the upstream -D HXCPP_GC_GENERATIONAL is unknown.
- Anonymous-structure field reads go through a virtual __Field(String) lookup returning a boxed hx::Val (include/hx/Anon.h), which explains the Anonymous row. Generational GC is opt-in and needs write barriers in native extern code; issue #740 asking what it takes to enable it has been open since 2018 with no answer.

## Known shortcomings

- Independent tong gist of the HashLink other/benchs suite (cpp total 0.7166 s vs hl 5.678 s vs neko 27.16 s): no compiler, flags or versions stated, the gist runner is unpublished, hlc was never compared (failed in 2025), JVM and Node match or beat cpp on several rows, times truncated to 0.01 s.
- Enricher: the 2018 gist totals double-count JavaScript (two rows per block labelled js, each set summing 0.43-0.45 s, so the js total of 0.962 s is their sum); counted once, Node (about 0.45-0.53 s) beats cpp (0.717 s), so 'C++ fastest overall' is false for 2018 while the wins over HashLink (5.68 s) and Neko (27.16 s) stand. Every 2025 hlc row reports 'result 0', the _Startup output, so no HL/C number exists (likely a stale binary). Times truncated to 0.01 s, default g++ -O2 without LTO, Anonymous objects are slow through a virtual __Field lookup returning boxed hx::Val.

## Caveats and trade-offs

The measurements are an individual's gist, not an official suite, and neither Haxe nor hxcpp versions, the C++ compiler or its flags are given, so the run is below tier A (the benchmark sources are public in HaxeFoundation/hashlink other/benchs, but the gist holds only results and its runner was extended beyond the upstream hl/hlc/js/neko/cpp target list). The suite comes from the HashLink repository, i.e. from the baseline's own project. The 2025 rerun lists no totals and shows hlc (HashLink's own C output) failing the result check on every benchmark ('result 0 but expected ...') and lua erroring on BinaryTrees, so hxcpp is never compared with HashLink/C, the AOT path closest to it. Even against HashLink the win is not on every row: HL/JIT beat cpp on Anonymous in 2018 (0.29 s versus 0.38 s). Against the other baselines the win is not clear: in 2018 JavaScript beat cpp on Anonymous (0.02 versus 0.38) and Java on BinaryTrees and Mandelbrot (0.06 versus 0.08, 0.12 versus 0.13), the totals put C++ 0.72 s next to Java 0.81 and JavaScript 0.96, and in the 2025 rows JVM and Node are faster than cpp on several rows (Anonymous 0.03 and 0.02 versus 0.1, BinaryTrees 0.02 versus 0.05, Mandelbrot 0.07 versus 0.13; derived from page data). Times are truncated to 0.01 s after startup subtraction, so many cells are 0 or 0.01 and small ratios are unreliable. The official HaxeBenchmarks site benchs.haxe.org exists but was blocked (EGRESS_BLOCKED), and its GitHub repo HaxeBenchmarks/benchs.haxe.org holds the site code, not result data. hxcpp is an AOT C++ backend and runtime rather than a VM, so the comparison is AOT against interpreters and JITs. The hxcpp LICENSE.txt is a one-condition BSD notice (BSD-1-Clause) that adds 'See individual source files for additional license information', so bundled third-party code carries its own terms. [retier] Gist runner unpublished, no compiler, flags or Haxe versions (default g++ -O2 without LTO), times truncated to 0.01 s; the 2018 js total double-counts its rows; every 2025 hlc row printed the _Startup result so HL/C was never measured; JVM and Node match or beat cpp on several rows. benchs.haxe.org is blocked here.

hxcpp is the runtime support for the Haxe C++ backend: Haxe source is compiled to C++ and then built by the platform C++ compiler, so builds are slow (about 2 s per small program in the gist versus 0.1 to 0.2 s for neko, hl, js) and need a C++ toolchain; it ships its own garbage collector and runtime library and has the cppia scripting host. Output is native code, so it is the fastest Haxe target on most of these rows but the language semantics follow Haxe, not C++.

## Maintenance

Active (last commit 2026-09-22 by Haxe Foundation contributors, 3,138 commits, 194 open issues) under a one-condition BSD licence, with bundled third-party code (mbedtls, sqlite, zlib, pcre2) under its own terms; it is the standard native target for any Haxe project.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent individual's gist (not by hxcpp's developers) timing the public HashLink other/benchs suite, whose upstream runner (other/benchs/Benchs.hx) checks every program's result and subtracts startup; CPU models (Intel Core i5-6600, AMD Ryzen 7 7700) are stated but Haxe/hxcpp versions, the C++ compiler and its flags are not, and the gist's extended runner (cs, java, lua, php, python targets) is not published, so it falls short of A.
- **Verifier notes:** Gist numbers verified: 2018 runtimes and totals (cpp 0.7166 s, java 0.806, js 0.962, hl 5.678, neko 27.16, so about 7.9x over HashLink and 38x over Neko, derived from page data) and every 2025 cpp/hl/neko value match the record. Tier B kept on the independent-measurement rule; if the orchestrator reads B strictly as peer-reviewed or well-known suite, this is C. Shortcomings: no compiler or flags, runner not published in the gist, hlc never compared, JVM/Node match or beat cpp on several rows, 0.01 s truncation. Last commit 2026-09-22, 329 stars, BSD-1-Clause.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** published runner with versions; published runner with versions and single-counted rows
- **Pages the verifier opened:**
  - <https://gist.github.com/tong/84992efadb204c2140e24dbdbeeee06c>
  - <https://github.com/HaxeFoundation/hxcpp>
  - <https://github.com/HaxeFoundation/hxcpp/commits/master>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/LICENSE.txt>
  - <https://github.com/HaxeFoundation/hashlink/tree/master/other/benchs>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/Benchs.hx>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/benchs.hxml>
  - <https://github.com/HaxeBenchmarks>
  - <https://github.com/HaxeBenchmarks/benchs.haxe.org>
- **Sources the enricher read:**
  - <https://github.com/HaxeFoundation/hxcpp>
  - <https://github.com/HaxeFoundation/hxcpp/commits/master>
  - <https://github.com/HaxeFoundation/hxcpp/tree/master/docs>
  - <https://github.com/HaxeFoundation/hxcpp/issues?q=is%3Aissue+performance>
  - <https://github.com/HaxeFoundation/hxcpp/issues/740>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/haxelib.json>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/Changes.md>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/toolchain/linux-toolchain.xml>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/toolchain/gcc-toolchain.xml>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/toolchain/common-defines.xml>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/docs/ThreadsAndStacks.md>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/docs/CompileCache.md>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/include/hx/Anon.h>
  - <https://raw.githubusercontent.com/HaxeFoundation/hxcpp/HEAD/src/hx/gc/Immix.cpp>
  - <https://gist.github.com/tong/84992efadb204c2140e24dbdbeeee06c>
  - <https://github.com/HaxeFoundation/hashlink/tree/master/other/benchs>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/Benchs.hx>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/benchs.hxml>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/Anonymous.hx>
  - <https://raw.githubusercontent.com/HaxeFoundation/hashlink/HEAD/other/benchs/_Startup.hx>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/haxefoundation/hxcpp`) · [data/wave12/enrich/raw/github_com_haxefoundation_hxcpp.json](../../../data/wave12/enrich/raw/github_com_haxefoundation_hxcpp.json) (enrichment confidence 0.7)

</details>
