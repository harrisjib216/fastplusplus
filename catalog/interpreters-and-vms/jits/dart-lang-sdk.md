# Dart SDK (Dart VM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Dart and C++ (the SDK includes the VM)` · `BSD-3-Clause` · 🟢 active

> Dart SDK's VM: adaptive JIT plus AOT compiler; beats PyPy 7.3.14 on all four plb2 tasks and LuaJIT 2.1 on three.

| | |
|---|---|
| **Beats** | PyPy 7.3.14 and LuaJIT 2.1 (also OpenJDK 20.0.1 HotSpot) |
| **Claimed result** | plb2 (https://github.com/attractivechaos/plb2) appendix row 'dart:jit+' (Dart 3.2.4), seconds: nqueen 3.62, matmul 2.74, sudoku 3.24, bedcov 2.85 vs py:pypy+ (PyPy 7.3.14) 6.91, 4.89, 8.82, 6.27, so 1.91x, 1.78x, 2.72x and 2.20x faster (derived from page data); vs luajit+ (LuaJIT 2.1) 5.31, 2.66, 4.48, 10.52, so faster on 3 of 4 (1.47x, 1.38x, 3.69x) and 3% slower on matmul (derived from page data). Against the other listed baselines it is mixed: vs js:node+ (Node 21.5.0, V8) 3.73, 2.88, 3.77, 2.45 it is faster on nqueen, matmul and sudoku and slower on bedcov; vs java+ (OpenJDK 20.0.1 HotSpot) 3.92, 1.14, 3.20, 3.04 it is faster on nqueen and bedcov, 2.4x slower on matmul and about equal on sudoku. |
| **Workload** | plb2 single-threaded CPU-bound tasks: nqueen (15 queens), matmul (1500x1500), sudoku, bedcov. |
| **Metric** | throughput |
| **Hardware** | Apple M1 MacBook Pro |
| **Compiler and flags** | Dart 3.2.4; the plb2 src/dart/Makefile builds with `dart compile exe` (AOT); run mode for the 'dart:jit' row is not stated. |
| **Adoption** | 11.3k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/dart-lang/sdk) · [benchmark](https://github.com/attractivechaos/plb2) |

## Verdict

Plb2 (attractivechaos, hyperfine wall-clock on an Apple M1 MacBook Pro, January 2024) ran Dart 3.2.4 in JIT mode on four single-threaded tasks: nqueen 3.62 s, matmul 2.74 s, sudoku 3.24 s, bedcov 2.85 s. PyPy 7.3.14 took 6.91, 4.89, 8.82 and 6.27 s, so Dart was 1.78x to 2.72x faster (derived from page data). LuaJIT 2.1 took 5.31, 2.66, 4.48 and 10.52 s, so Dart won three of four and was 3% slower on matmul. Against OpenJDK 20 and Node 21 the results were mixed.

## Use it when

- You are choosing a garbage-collected language for CPU-bound scripts or services, and Python or Lua under PyPy/LuaJIT is too slow. In plb2, Dart 3.2.4 was 1.8x to 2.7x faster than PyPy 7.3.14 on all four tasks.
- Branchy integer or bit-twiddling code and small fixed arrays (plb2 nqueen and sudoku), where Dart was 1.5x and 3.7x faster than LuaJIT 2.1.
- Pointer-heavy array-of-objects code (plb2 bedcov), where Dart (2.85 s) was 3.7x faster than LuaJIT (10.52 s).
- Teams already on Flutter or Dart who want one language for app and backend, with the choice of JIT for development and AOT for deployment.

## Skip it when

- Dense float loops like matmul: Dart took 2.74 s against 1.14 s for OpenJDK 20 HotSpot and 0.76 s for Julia 1.10, and was 3% slower than LuaJIT.
- Expecting AOT (`dart compile exe`) to match JIT on tight typed-data loops: issue #53513 (Uint32List graph traversal, 2.76 s JIT vs 15.22 s AOT) and open issue #62619 (scanline rasterizer, about 6.5x slower AOT on Dart 3.6.0) report AOT far slower.
- When the fastest managed runtime is the goal: in the same plb2 table, .NET 8 (NativeAOT), Julia 1.10 and Bun 1.0.20 are faster than Dart on all four tasks.
- Existing Python, Lua or JavaScript code you cannot rewrite; Dart is a separate language with its own libraries.
- Lightweight embedding in a C++ application: the VM is large, built with Chromium depot_tools/GN, and the embedding API is not the main supported use.

## How it is fast

In JIT mode, functions start in an unoptimizing compiler whose call sites use inline caches to record receiver types. Hot functions (and long loops, via on-stack replacement) are then recompiled in the background by an SSA-based optimizing compiler. It specializes code speculatively from that type feedback (inlining, range analysis, representation selection and unboxing, load forwarding, GVN, allocation sinking, linear-scan register allocation) and falls back to unoptimized code when an assumption breaks. AOT mode instead runs a whole-program type flow analysis (TFA) and devirtualizes calls only where it can prove the target, with no speculation. Memory is managed by a generational GC: a parallel semispace scavenger for the young generation and concurrent marking with mark-sweep/mark-compact for the old generation.

## Compared with alternatives

Pick Dart over Julia or the .NET runtime when you want the Dart/Flutter ecosystem with both JIT and AOT deployment; for raw throughput, Julia and .NET beat it on every plb2 task. Pick it over Chez Scheme for bit-twiddling and matmul-style code (plb2 matmul 2.74 s vs Chez 9.5.8's 18.98 s), and over Graal.js only if you want a statically typed language rather than JavaScript.

## Integration

| | |
|---|---|
| **Form** | language toolchain (prebuilt SDK with `dart` CLI); the VM can also be built from source and embedded through runtime/include/dart_api.h |
| **Dependencies** | none to run the prebuilt SDK; building from source needs Python 3, Chromium depot_tools (gclient, GN, ninja) and Visual Studio 2017+ with the Windows 10 SDK on Windows |
| **Minimum toolchain** | not documented for users; plb2 used Dart 3.2.4 |
| **Platforms** | native code for x64, ARM and RISC-V on Linux, macOS and Windows (mobile through Flutter); JavaScript and WebAssembly for the web |
| **Thread safety** | Isolate model: each isolate has its own state and usually its own mutator thread, and isolates in a group share a GC heap. Embedders attach one current isolate per thread (dart_api.h). |
| **Drop-in for the baseline** | no |

## Gotchas

- Plb2's timed mode, resolved: commit 1e4d581 ('added makefile for dart compile exe', body 'this is slower...') shows the author found the AOT build slower. The '(JIT)' row therefore most likely times `dart file.dart`, not the Makefile's AOT executables. No run script is checked in.
- The Dart matmul figure comes after a manual loop-hoisting commit (d704e27, 4.81 s to 2.74 s). The Lua, Python and Java ports hoist the same loop, so the comparison stays fair.
- The plb2 Dart ports leave several parameters untyped (matmul(a, b), sudoku's _update(sr, sc, r, v) and solve(s_), `var i` in nqueen), so they run through dynamic dispatch. Dart's matmul gap to HotSpot may partly be port quality. This is not a correctness bug.
- Wall-clock times include source-to-Kernel compilation in the kernel-service isolate and JIT warm-up. The sudoku run also prints every solution. These fixed costs are the same for all languages but weigh more on short runs.

## Known shortcomings

- plb2 row is labelled JIT but the Makefile runs 'dart compile exe' (AOT) and the README legends contradict each other, so it is unclear whether the timed binary was JIT or AOT. Mixed against the baselines: 2.4x slower than HotSpot on matmul and slower than V8 on bedcov. Not C++.
- Enricher: plb2 commit 1e4d581 ('added makefile for dart compile exe', body 'this is slower') shows the author found AOT slower, so the '(JIT)' row most likely times 'dart file.dart' rather than the Makefile; the Dart ports leave parameters untyped (matmul(a, b), sudoku _update and solve) so they run through dynamic dispatch, and in the same table Julia 1.10, .NET 8 and Bun beat Dart on all 4 tasks. dart-lang/sdk issues #53513 and #62619 report AOT 5-6x slower than JIT on typed-data loops.

## Caveats and trade-offs

It is not certain which mode was timed: src/dart/Makefile compiles AOT executables with 'dart compile exe', but the table row is labelled 'dart:jit+' with runtime '(JIT)', and the README contradicts itself (the Results section says '+' marks AOT, the appendix says '+' marks JIT and '\*' AOT). Wall-clock time includes startup and JIT warmup. The win over HotSpot is narrow and mixed, and V8 (Node) is faster on bedcov. The benchmarks are one author's ports of four small programs. The Dart numbers date from the Jan 2024 run (Dart directory last changed 2024-01-07); plb2 was last updated January 2025 (Codon bump). [retier] The 'dart:jit+' row times 'dart file.dart' (JIT): plb2 commit 1e4d581 added the 'dart compile exe' Makefile with the note that AOT is slower, and dart-lang/sdk issues #53513 and #62619 report AOT 5-6x slower than JIT on typed-data loops. The Dart ports leave parameters untyped (matmul(a, b), sudoku _update and solve), so they run through dynamic dispatch; matmul 2.74 s came after hoisting commit d704e27 (was 4.81 s), the Lua, Python and Java ports hoist the same loop. Mixed against the baselines: 2.4x slower than HotSpot on matmul, slower than V8 on bedcov, and Julia 1.10, .NET 8 and Bun beat Dart on all 4 tasks in the same table. Not C++.

Dart VM is a full language runtime with its own object model and GC; embedding from C++ is possible through the Dart embedding API but is niche; JIT startup warmup.

## Maintenance

Very active (commit on 2026-10-06, 11.3k stars, BSD-3-Clause) and production-grade. You use it as a whole language toolchain rather than vendoring code, and the plb2 evidence is a single 2024 run of one author's ports.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification B, tier now B.
- **Tier reason:** plb2 is an independent third-party language shootout (attractivechaos, CC0 code in src/dart/\*.dart, src/python, src/lua) whose appendix table has exactly the record's 'dart:jit+' Dart 3.2.4 row and the PyPy 7.3.14, LuaJIT 2.1, Node 21.5.0 and OpenJDK 20.0.1 rows on an Apple M1 MacBook Pro, timed with hyperfine. It falls short of A because no run script exists and the timed Dart mode is unclear: src/dart/Makefile (added 2024-01-03) builds with 'dart compile exe' (AOT), while the row is labelled '(JIT)' and the README's two legends contradict each other on what '+' means.
- **Verifier notes:** Every number in the record matches the plb2 README appendix row for Dart and the PyPy/LuaJIT/OpenJDK rows; the README blame shows the Dart row unchanged since January 2024 apart from a plot column. Metadata checked on github.com: BSD-3-Clause, 11.3k stars, not archived, last commit 2026-10-06. Shortcomings to record: AOT vs JIT mode ambiguity in the timed row, single-shootout evidence, mixed against HotSpot and V8 (slower on matmul vs HotSpot, bedcov vs Node).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/attractivechaos/plb2>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/src/dart/Makefile>
  - <https://github.com/attractivechaos/plb2/tree/master/src/dart>
  - <https://github.com/attractivechaos/plb2/commits/master/src/dart>
  - <https://github.com/attractivechaos/plb2/commits/master>
  - <https://github.com/attractivechaos/plb2/commit/1e4d581>
  - <https://github.com/attractivechaos/plb2/commit/05164cd>
  - <https://github.com/attractivechaos/plb2/commit/d704e27>
  - <https://github.com/attractivechaos/plb2/commit/eae03aa4107704b608c42316a3b97e152a1f723e>
  - <https://github.com/attractivechaos/plb2/blame/master/README.md>
  - <https://github.com/dart-lang/sdk>
  - <https://github.com/dart-lang/sdk/commits/main>
- **Sources the enricher read:**
  - <https://github.com/dart-lang/sdk>
  - <https://raw.githubusercontent.com/dart-lang/sdk/HEAD/README.md>
  - <https://raw.githubusercontent.com/dart-lang/sdk/HEAD/runtime/docs/README.md>
  - <https://raw.githubusercontent.com/dart-lang/sdk/HEAD/runtime/docs/gc.md>
  - <https://raw.githubusercontent.com/dart-lang/sdk/HEAD/docs/README.md>
  - <https://raw.githubusercontent.com/dart-lang/sdk/HEAD/docs/Building.md>
  - <https://raw.githubusercontent.com/dart-lang/sdk/HEAD/runtime/include/dart_api.h>
  - <https://raw.githubusercontent.com/dart-lang/sdk/HEAD/runtime/include/dart_embedder_api.h>
  - <https://github.com/dart-lang/sdk/issues?q=is%3Aissue+AOT+slower+than+JIT>
  - <https://github.com/dart-lang/sdk/issues/53513>
  - <https://github.com/dart-lang/sdk/issues/62619>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/src/dart/Makefile>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/src/dart/nqueen.dart>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/src/dart/matmul.dart>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/src/dart/sudoku.dart>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/src/dart/bedcov.dart>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/src/lua/matmul.lua>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/src/python/matmul.py>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/HEAD/src/java/matmul.java>
  - <https://github.com/attractivechaos/plb2/commits/master/src/dart>
  - <https://github.com/attractivechaos/plb2/commit/1e4d581>
  - <https://github.com/attractivechaos/plb2/commit/d704e27>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/dart-lang/sdk`) · [data/wave12/enrich/raw/github_com_dart_lang_sdk.json](../../../data/wave12/enrich/raw/github_com_dart_lang_sdk.json) (enrichment confidence 0.65)

</details>
