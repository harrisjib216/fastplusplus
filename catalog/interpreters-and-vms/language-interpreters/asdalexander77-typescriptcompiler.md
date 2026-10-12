# TypeScriptCompiler (ASDAlexander77, LLVM-based TypeScript AOT/JIT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Language interpreters](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> LLVM/MLIR ahead-of-time and JIT compiler for a TypeScript subset; no published speed comparison against Node/V8.

| | |
|---|---|
| **Beats** | V8 (Node.js) running the same TypeScript/JavaScript; no named comparison found |
| **Claimed result** | No speed numbers. README says the compiler produces native executables, WebAssembly or JIT runs 'no Node.js or JavaScript runtime required' and states no speedup against Node, V8 or Deno. Only memory figures in README and docs/memory-models.md: a ray tracer at 114 MB under -mm=none holds 4.1 MB with reference counting versus 5.8 MB with garbage collection. |
| **Workload** | No speed benchmark found. The only measurements in the repo are peak working-set memory for a ray tracer (256x256 and 512x512) and an n-body simulation under the compiler's own three memory models (-mm=gc, -mm=rc, -mm=none), which compare the compiler with itself. |
| **Metric** | other |
| **Adoption** | 776 stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/ASDAlexander77/TypeScriptCompiler) |

## Verdict

No speed claim was verified: the repo only reports peak working set of its own builds (ray tracer 256x256: 5.8 MB gc, 4.1 MB rc, 114.5 MB none; 512x512: 5.5 / 4.1 / 445.0 MB; n-body 5.6 / 4.1 / 4.1 MB) at --opt --opt_level=3 with no hardware or OS stated, and no Node/V8 baseline was run.

## Use it when

- You want a single native binary (or a .dll/.so callable from C/C++) from TypeScript source with no Node, V8 or Bun on the target machine.
- Embedding TypeScript-written logic in a C/C++ host via shared libraries and tsbindgen-generated C bindings, on Windows x64/x86, Linux x64 or Android (arm64-v8a, x86_64 cross-built from Windows).
- Small memory footprint matters more than throughput: -mm=rc keeps a ray tracer at 4.1 MB peak working set versus 5.8 MB under Boehm GC, and a hello-world is 145 KB under -mm=rc versus 335 KB under -mm=gc (project's own figures).
- Experimenting with TypeScript to wasm32 output without a JS engine inside the module (you supply the host imports yourself, as the README's run.html loader does).

## Skip it when

- You need a proven speedup over Node/V8: none is published, and the project's own reference-counting design doc says throughput is not the argument for its memory models.
- Existing Node or npm code: Node APIs and npm packages are not available, the language subset has its own semantics (strict null checks, compile-time typing, main() entry), and the default library is the only source of JS built-ins.
- Production use: releases are tagged v0.0-pre-alpha (latest v0.0-pre-alpha90), and basic-semantics bugs were fixed only days ago (#509 an empty string was truthy in conditions, #498 for await ran its body as concurrent tasks and lost writes, #456/#457 throws inside try not caught, #513 a mismatched object literal was silently not assigned).
- Data with back-references under -mm=rc: parent links, doubly linked lists and closures capturing their owner are never freed; counts are non-atomic, so -mm=rc is single-threaded.
- Building from source on a constrained machine: the README asks for about 50 GB of free disk for the LLVM/MLIR build (prebuilt release packages avoid this).

## How it is fast

Static ahead-of-time compilation: TypeScript with its type annotations is lowered to typed ops in the project's own MLIR dialect (TypeScriptOps.td), with explicit integer types such as s32/i32 alongside number, then optimized by LLVM (--opt --opt_level=3), so there is no interpreter, inline cache or JIT warm-up. Memory is managed by the Boehm conservative collector by default, or by compiler-inserted reference counting (-mm=rc) or no freeing at all (-mm=none). No measurement in the repo shows that this beats V8; the only numbers are peak working set across the three memory models.

## Compared with alternatives

Pick it over katsu, LLRT or lo when you want TypeScript compiled to a standalone native or wasm binary or a C-callable shared library with no JS engine at all; pick those siblings when you need measured wins over Node (katsu's cold start, LLRT's Lambda cold start) or Node/npm compatibility.

## Integration

| | |
|---|---|
| **Form** | compiler toolchain (prebuilt tslang release packages, or built from source with CMake/Ninja); output is native exe, dll/so, object file or wasm32 |
| **Dependencies** | LLVM/MLIR 22.1.8 (to build the compiler), Boehm GC (for -mm=gc), the tslang async runtime library and the separate TypeScriptCompilerDefaultLib default library; libcurl for fetch() (stubbed on Android, where fetch() throws) |
| **Minimum toolchain** | Windows: Visual Studio 2026; Linux: gcc or clang with cmake, ninja-build and libtinfo-dev (README tested on Ubuntu 20.04 and 22.04) |
| **Platforms** | Windows x64 and x86, Linux x64, Android arm64-v8a and x86_64 (API 29+, cross-compiled from a Windows host), wasm32-unknown-unknown (-mm=none); the JIT is host-only |
| **Thread safety** | Not documented for user code. -mm=rc uses non-atomic counts and is single-threaded per docs/memory-models.md; -mm=gc shared libraries had thread races in Boehm registration fixed on 2026-10-06 (#522, #523). |
| **Drop-in for the baseline** | no |

## Gotchas

- No benchmark against Node, V8, Deno or any other runtime exists in README, docs/memory-models.md or tslang/docs/reference-counting-evaluation.md; every number compares the compiler's own -mm=gc/-mm=rc/-mm=none modes (peak working set, --opt --opt_level=3, no hardware stated). The design doc's section 9.28 shows the same ray tracer at 129.5 MB under -mm=rc before the discarded-temporaries fix, so the 4.1 MB headline depends on very recent ownership work.
- Windows -mm=gc: if an executable and a tslang shared library each link the static gc.lib, each gets its own collector and one frees objects the other still holds; the symptom is plausible wrong values, not a crash. Current tslang links gc.dll automatically for --emit=dll and refuses old statically linked libraries, but hand-linked builds must use the shared gc.lib.
- Mixing modules built with different -mm values compiles with only a warning, and objects crossing between them leak.
- 0 open issues, and the 25 most recent were all filed and closed by the maintainer within the last week; the README badge says the project is developed with Claude Code. Expect fast churn and little outside bug reporting.

## Known shortcomings

- No speed benchmark against Node, V8, Deno or any runtime; the only numbers are peak memory of its own -mm=gc/rc/none modes against each other (ray tracer 5.8/4.1/114.5 MB; n-body 5.6/4.1/4.1 MB), and tslang/docs/reference-counting-evaluation.md section 7 says 'Performance is not the argument'. Kept at D under the keep-and-document rule (verifier noted a strict reject). The rc mode leaks reference cycles and its counts are not atomic; the project is built by Claude Code. 776 stars, MIT.
- Enricher: design doc section 9.28 shows the same ray tracer at 129.5 MB under -mm=rc before the discarded-temporaries fix, so the 4.1 MB headline rests on very recent work; still pre-alpha (v0.0-pre-alpha90). Basic-semantics bugs closed only this week: #509 empty string truthy, #498 for-await ran its body as concurrent tasks, #456/#457 throws not caught, #513 object literal silently not assigned; the last 25 issues were all filed and closed by the maintainer. -mm=rc leaks cycles with non-atomic counts; a Windows static gc.lib linked into two modules gives silently wrong values.

## Caveats and trade-offs

Tier D: no numeric comparison against Node, V8, Deno or any named baseline found in README, docs/memory-models.md, tslang/docs/reference-counting-evaluation.md or a web search. The only numbers compare the compiler with itself: peak working set of a ray tracer (256x256: 5.8 MB gc, 4.1 MB rc, 114.5 MB none; 512x512: 5.5 / 4.1 / 445.0 MB) and an n-body simulation (5.6 / 4.1 / 4.1 MB), built with --opt --opt_level=3, no hardware stated. reference-counting-evaluation.md section 7 is titled 'Performance is not the argument' and says the case for reference counting is determinism and memory footprint, not throughput. -mm=rc does not collect reference cycles and its counts are not atomic (single-threaded). The README header badge says the project is developed by Claude Code. 776 stars (under 1k). Included at tier D only because the seed list names it; a speed claim vs Node would need an independent benchmark.

Compiles a TypeScript subset with its own semantics (strict null checks, a custom default library for JavaScript built-ins, no JS runtime) to LLVM/MLIR native executables, WebAssembly or JIT; garbage collection by default, with reference counting or no freeing selectable via -mm. Runs without Node.js, so Node APIs and npm packages are not available unless its default library provides them (not verified). Builds against LLVM/MLIR 22.1.8 (prebuilt MLIR releases exist).

## Maintenance

Very active (last commit 2026-10-06, hundreds of commits) and MIT-licensed, but still pre-alpha with a fast-moving language subset; usable for experiments and C/C++ embedding, not as a measured faster alternative to Node.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null and no speed numbers against Node, V8, Deno or any other runtime exist in the README, docs/memory-models.md or tslang/docs/reference-counting-evaluation.md; the only figures are peak working-set memory of the compiler's own -mm=gc/-mm=rc/-mm=none modes compared with each other, so there is no numeric win over a named baseline (tier D).
- **Verifier notes:** Real, active MIT project (776 stars, 40 forks, not a fork, not archived, last commit 2026-10-06 '#525 Bounded copies'), but it makes no speed claim against any baseline and its own design doc says performance is not the argument; under the prompt's strict list this would be a no-baseline-comparison / not-notable-tier-d reject, kept as confirm at D per the keep-and-document policy. Shortcomings to record: no benchmark against Node/V8/Deno, only self-comparison memory figures across its three memory models, under 1k stars, rc mode leaks reference cycles.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** any runtime comparison
- **Pages the verifier opened:**
  - <https://github.com/ASDAlexander77/TypeScriptCompiler>
  - <https://github.com/ASDAlexander77/TypeScriptCompiler/commits>
  - <https://github.com/ASDAlexander77/TypeScriptCompiler/tree/main/tslang/docs>
  - <https://raw.githubusercontent.com/ASDAlexander77/TypeScriptCompiler/HEAD/README.md>
  - <https://raw.githubusercontent.com/ASDAlexander77/TypeScriptCompiler/HEAD/docs/memory-models.md>
  - <https://raw.githubusercontent.com/ASDAlexander77/TypeScriptCompiler/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ASDAlexander77/TypeScriptCompiler/HEAD/tslang/docs/reference-counting-evaluation.md>
- **Sources the enricher read:**
  - <https://github.com/ASDAlexander77/TypeScriptCompiler>
  - <https://raw.githubusercontent.com/ASDAlexander77/TypeScriptCompiler/HEAD/README.md>
  - <https://raw.githubusercontent.com/ASDAlexander77/TypeScriptCompiler/HEAD/docs/memory-models.md>
  - <https://raw.githubusercontent.com/ASDAlexander77/TypeScriptCompiler/HEAD/tslang/docs/reference-counting-evaluation.md>
  - <https://raw.githubusercontent.com/ASDAlexander77/TypeScriptCompiler/HEAD/LICENSE>
  - <https://github.com/ASDAlexander77/TypeScriptCompiler/issues?q=is%3Aissue>
  - <https://github.com/ASDAlexander77/TypeScriptCompiler/issues?q=is%3Aissue+performance+OR+slow+OR+node>
  - <https://github.com/ASDAlexander77/TypeScriptCompiler/discussions>
  - <https://github.com/ASDAlexander77/TypeScriptCompiler/releases>
  - <https://github.com/ASDAlexander77/TypeScriptCompiler/releases/tag/v0.0-pre-alpha90>
  - <https://github.com/ASDAlexander77/TypeScriptCompiler/wiki>
  - <https://github.com/ASDAlexander77/TypeScriptCompiler/tree/main/tslang>
  - <https://github.com/ASDAlexander77/TypeScriptCompiler/tree/main/tslang/include/TypeScript>
  - <https://raw.githubusercontent.com/ASDAlexander77/TypeScriptCompilerDefaultLib/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/asdalexander77/typescriptcompiler`) · [data/wave12/enrich/raw/github_com_asdalexander77_typescriptcompiler.json](../../../data/wave12/enrich/raw/github_com_asdalexander77_typescriptcompiler.json) (enrichment confidence 0.75)

</details>
