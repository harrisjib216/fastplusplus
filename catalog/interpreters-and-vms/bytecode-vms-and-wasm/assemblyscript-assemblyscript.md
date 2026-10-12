# AssemblyScript (TypeScript-like to Wasm compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [Bytecode VMs and WebAssembly runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `TypeScript` · `Apache-2.0` · 🟢 active

> Ahead-of-time compiler from a strict TypeScript dialect to WebAssembly via Binaryen; its 7.2x-over-JavaScript n-body claim is mostly a harness artifact.

| | |
|---|---|
| **Beats** | JavaScript on V8 (Node.js v18.7.0), same n-body source compiled with tsc |
| **Claimed result** | No valid numeric win: the n-body README figure (Wasm 1,606 ms vs JS 11,640 ms, about 7.2x) compares against a tsc build whose class fields start as undefined (useDefineForClassFields), a 7x penalty reproduced by the enricher; corrected, plain JavaScript is roughly equal. LeanyLabs micro-benchmarks have JS winning 4 of 6. |
| **Workload** | n-body simulation from the Computer Language Benchmarks Game (5 bodies, f64) in AssemblyScript Wasm, the same source transpiled to JavaScript with tsc, and a Rust Wasm version, timed inside Node. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (15-inch, 2019), macOS 12.5.0 (CPU model not stated) |
| **Compiler and flags** | asc from the 'latest' npm package (exact version not stated), asconfig target wasm: optimizeLevel 3, shrinkLevel 0, converge, noAssert, runtime stub; Node v18.7.0 run with --nowasm-bounds-checks --nowasm-stack-checks --noliftoff --expose-gc; Rust Wasm built with rustc 1.64.0-nightly |
| **Adoption** | about 18k stars (examples repo 313 stars) |
| **Last commit** | 2026-07-21 |
| **Links** | [repository](https://github.com/AssemblyScript/assemblyscript) · [benchmark](https://github.com/AssemblyScript/examples/tree/main/n-body) |

## Verdict

One first-party n-body run (AssemblyScript/examples, MacBook Pro 15-inch 2019, macOS 12.5.0, Node v18.7.0 with Wasm bounds and stack checks off, asc 'latest', 20M steps by default) reports 1,606 ms for AssemblyScript Wasm, 1,611 ms for Rust Wasm and 11,640 ms for the tsc-transpiled JavaScript. The JavaScript figure is inflated by the esnext class-field emit described in gotchas, so the evidence supports 'about level with Rust Wasm and with well-emitted JIT JavaScript' on this kernel, not 7.2x over V8; independent micro-benchmarks (LeanyLabs, i5-8250, AssemblyScript 0.18.x) are mixed and mostly favour JavaScript.

## Use it when

- Self-contained numeric kernels (physics steps, DSP, codecs, hashing, emulators) that do lots of i32/f64 work per call and touch few managed objects.
- You want predictable steady-state speed in browsers or Node without JIT warm-up or deoptimization cliffs, and a small module (the n-body build is 1.8 KB).
- A team that knows TypeScript needs a Wasm toolchain installable with npm, without an Emscripten/Rust/C++ toolchain.
- Plugin or sandbox code for Wasm hosts (Wasmtime, Wasmer, WAMR) where the guest must be small and its memory layout explicit.

## Skip it when

- Code that calls across the JS/Wasm boundary often or moves arrays and strings back and forth: in LeanyLabs' run JavaScript beat AssemblyScript on add (697.3M vs 125.8M ops/s), importCallback (351,545 vs 24,366 ops/s) and squareArray.
- Existing TypeScript you hoped to speed up by recompiling: the project's own FAQ says pre-existing TypeScript 'doesn't magically become faster', especially with heavy use of managed objects and GC.
- Code that relies on closures, union types, any, iterators, exceptions, async/await, JSON or RegExp (not implemented or community add-ons only).
- Server-side work that needs WASI or the component model: the project labels both 'harmful' and does not target them.
- Workloads where a well-written JIT-compiled JavaScript version already runs near the Wasm speed, which on the n-body kernel it does once the baseline harness is fixed (see gotchas).

## How it is fast

Static typing lets the compiler emit plain Wasm numeric instructions with no type checks, boxing or deoptimization, and Binaryen's optimizer (optimizeLevel 0-3, shrinkLevel, --converge re-runs passes to a fixed point) cleans up the module ahead of time. Classes are C-struct-like records in linear memory, StaticArray holds data inline, and unchecked() plus --noAssert drop bounds checks and assertions. The runtime is selectable: incremental TLSF allocator plus incremental GC (default), minimal (manual __collect) or stub (bump allocator, never frees), which is what the n-body benchmark used.

## Compared with alternatives

Siblings here are mostly Wasm runtimes (Wasmtime, WAMR, wasm3, Wasmi) that would execute AssemblyScript's output rather than compete with it; among source-to-Wasm compilers, dy/jz claims about 2x over AssemblyScript on its kernels, so pick AssemblyScript when you need a mature, widely used (18k stars) typed language with a standard library, bindings generator and GC rather than jz's JavaScript-subset approach.

## Integration

| | |
|---|---|
| **Form** | npm package (asc compiler CLI and JS API) producing .wasm modules with optional generated JS bindings |
| **Dependencies** | binaryen (pinned nightly, 131.0.0-nightly.20260721 at HEAD) and long; the generated .wasm has no runtime dependency beyond the host's imports |
| **Minimum toolchain** | Node.js &gt;= 20 and npm &gt;= 10 to run the compiler (engineStrict); output needs a Wasm engine with the MVP plus sign-extension, non-trapping float-to-int, bulk-memory and mutable-global features enabled by default |
| **Platforms** | any WebAssembly host (Chrome, Firefox, Safari, Node, Wasmtime, Wasmer); wasm32 linear memory; SIMD, threads, GC, reference types and exception handling sit behind --enable flags at various stages |
| **Thread safety** | not documented; threads is a feature flag still in implementation, and the bundled runtimes (TLSF + incremental GC) are single-threaded by design |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the headline 7.2x: the n-body JS baseline is built with 'tsc -p assembly -t esnext' and TypeScript ^4.7.4, which defaults useDefineForClassFields to true for ES2022 and later (getUseDefineForClassFields in TS 4.7.4 utilities.ts), so Body is emitted with class field declarations that start every f64 field as undefined. In this session's probe on Node 22.22.0, the same advance() loop took 3,155 ms with those field declarations and 443 ms without (5M steps, about 7x, identical positions), the same ratio as the README's 11,640 vs 1,606 ms; plain JS then runs at roughly the AssemblyScript figure. Issue 1326 (2020, older TypeScript) had JS faster than AssemblyScript on the same sample.
- The benchmark also ran Node with --nowasm-bounds-checks --nowasm-stack-checks --noliftoff, the stub runtime (never frees) and --noAssert with unchecked() array reads; production builds normally keep bounds checks and the default incremental GC, so expect slower Wasm than the table.
- unchecked() and --noAssert remove safety checks rather than proving them unnecessary; an out-of-range index then reads or writes arbitrary linear memory instead of trapping.
- Open miscompilation issue #3051 ('"+=" for an operand with side effects causes miscompilation', 2026-10-04) and a run of compiler-crash reports (#3043-#3050, 2026-10-03/04); test generated code, and pin the asc and Binaryen versions since the package tracks Binaryen nightlies.

## Known shortcomings

- Single first-party n-body run (Wasm 1606 ms vs JS 11640 ms) with no CPU model, asc 'latest' and Wasm-favouring Node flags; the JS baseline is a tsc transpile and its 11640 ms is anomalous against issue #1326 (JS 3.0 s, AS 5.6 s). LeanyLabs micro-benchmarks have JS winning 4 of 6; the ISU 2020 creative component (1.1-7.2x) is snippet only (lib.dr.iastate.edu blocked). No emscripten column.
- Enricher: the n-body JavaScript baseline is built with tsc -p assembly -t esnext under TypeScript ^4.7.4, whose useDefineForClassFields default emits class field declarations that start every f64 field as undefined; in a probe on Node 22.22.0 the same advance() loop took 3,155 ms with those declarations and 443 ms without (about 7x), the same ratio as the README's 11,640 vs 1,606 ms, so plain JavaScript runs at roughly the AssemblyScript figure. The run also used --nowasm-bounds-checks --nowasm-stack-checks --noliftoff, the stub runtime that never frees, --noAssert and unchecked() reads. Open miscompilation issue #3051 (2026-10-04) and compiler-crash reports #3043-#3050; the package tracks Binaryen nightlies.

## Caveats and trade-offs

The compiler repository itself carries no benchmark numbers (README and tests contain none) and the project's website could not be opened. The only first-party number is one n-body example in the separate AssemblyScript/examples repo: single workload, unspecified CPU model, asc version 'latest' (package.json devDependency), and Node started with --nowasm-bounds-checks --nowasm-stack-checks --noliftoff, which favours the Wasm side. The README says 'npm test [steps=1000000]' while tests/index.js defaults to 20000000 steps, and the table does not say whether it is the cold or warmed-up series. The JavaScript side is the AssemblyScript source transpiled by tsc (unchecked() calls stripped), not an idiomatic JS n-body, and its 11640 ms looks anomalous: AssemblyScript issue 1326 (June 2020, AssemblyScript 0.10.0, Node 14.4.0, Windows 10, 20,000,000 steps) measured the same sample at JavaScript 3.0 s and AssemblyScript 5.6 s, the opposite result. Independent micro-benchmarks (LeanyLabs/assemblyscript-benchmarks, 7 stars, i5-8250, assemblyscript ^0.18.4, Node version not stated) show JavaScript winning four of six cases. A 2020 Iowa State University master's creative component ('Benchmarking AssemblyScript for Faster Web Applications', Ostrich suite numerical kernels on Chrome and Firefox) reportedly finds 1.1x to 7.2x speedups over JavaScript (search snippet only; host blocked; not peer-reviewed). The baseline is JavaScript running on V8, not another Wasm runtime; the emscripten C++ baseline from the lead was not found for this project. [retier] The only first-party comparison used a crippled JavaScript baseline plus Wasm-favouring Node flags (--nowasm-bounds-checks --nowasm-stack-checks --noliftoff), the stub runtime and --noAssert with unchecked() reads; no CPU model, asc 'latest'. Issue #1326 and LeanyLabs show JavaScript faster on comparable code. Open miscompilation issue #3051 and compiler crashes #3043-#3050; pin asc and Binaryen versions.

Strictly typed TypeScript subset (no any, closures and many dynamic features unsupported or limited); compiles through Binaryen to Wasm with its own GC runtime (stub, minimal or incremental); calls across the JS and Wasm boundary are costly so only compute-heavy kernels win; code must be written in a numeric style (unchecked(), f64) to approach the quoted speed.

## Maintenance

Actively maintained (v0.28.20 released 22 July, last commit 2026-07-21, 18.0k stars, Apache-2.0, 189 open issues) and easy to adopt from npm, but the only speed claim against its baseline rests on a crippled JavaScript build and should be re-tiered or flagged as not shown to be faster.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party n-body README in AssemblyScript/examples gives 1606 ms (AS Wasm) vs 11640 ms (JS) vs 1611 ms (Rust Wasm) with public code, asconfig and Node flags, but no CPU model (only 'MacBook Pro (15-inch, 2019)'), an unpinned asc version ('latest') and an ambiguous step count, so it falls short of A; the independent LeanyLabs micro-benchmarks are a 7-star repo with mixed results, not a well-known suite.
- **Retiered** C to D: C to D: the only numeric comparison against the listed baseline (n-body Wasm 1,606 ms vs JS 11,640 ms) rests on a JavaScript build crippled by TypeScript's useDefineForClassFields default, which the enricher reproduced as a 7x penalty on Node 22.22.0 (3,155 vs 443 ms for the same loop); corrected, plain JavaScript runs at roughly the AssemblyScript figure, so no valid number shows it faster (fast_resize precedent would reject, kept and documented).
- **Verifier notes:** n-body README numbers match (1606/11640/1611 ms; 7.2x derived), LeanyLabs ops/s match. Licence Apache-2.0, \~18k stars, last commit 2026-07-21 all verified. Shortcomings: single first-party workload with no CPU model and unpinned compiler, Wasm-favouring Node flags, JS baseline is a tsc transpile whose time is 4x slower than an earlier report, and independent micro-benchmarks mostly favour JavaScript.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** independent comparison including an emscripten C++ column; comparison against an uncrippled JavaScript build with default safety checks
- **Pages the verifier opened:**
  - <https://github.com/AssemblyScript/examples/tree/main/n-body>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/README.md>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/package.json>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/asconfig.json>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/tests/index.js>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/scripts/postprocess.js>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/assembly/index.ts>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/assembly/tsconfig.json>
  - <https://github.com/AssemblyScript/assemblyscript>
  - <https://github.com/AssemblyScript/assemblyscript/commits>
  - <https://github.com/AssemblyScript/assemblyscript/issues/1326>
  - <https://github.com/LeanyLabs/assemblyscript-benchmarks>
  - <https://raw.githubusercontent.com/LeanyLabs/assemblyscript-benchmarks/HEAD/package.json>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/HEAD/README.md>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/HEAD/package.json>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/HEAD/NOTICE>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/HEAD/std/assembly.json>
  - <https://raw.githubusercontent.com/AssemblyScript/assemblyscript/HEAD/tsconfig-base.json>
  - <https://github.com/AssemblyScript/assemblyscript>
  - <https://github.com/AssemblyScript/assemblyscript/releases>
  - <https://github.com/AssemblyScript/assemblyscript/issues/1326>
  - <https://github.com/AssemblyScript/assemblyscript/issues?q=is%3Aissue+performance+slower>
  - <https://github.com/AssemblyScript/assemblyscript/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/README.md>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/package.json>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/asconfig.json>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/tests/index.js>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/assembly/index.ts>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/assembly/tsconfig.json>
  - <https://raw.githubusercontent.com/AssemblyScript/examples/HEAD/n-body/scripts/postprocess.js>
  - <https://raw.githubusercontent.com/AssemblyScript/website/HEAD/src/frequently-asked-questions.md>
  - <https://raw.githubusercontent.com/AssemblyScript/website/HEAD/src/status.md>
  - <https://raw.githubusercontent.com/AssemblyScript/website/HEAD/src/runtime.md>
  - <https://raw.githubusercontent.com/AssemblyScript/website/HEAD/src/compiler.md>
  - <https://raw.githubusercontent.com/AssemblyScript/website/HEAD/src/introduction.md>
  - <https://raw.githubusercontent.com/microsoft/TypeScript/v4.7.4/src/compiler/utilities.ts>
  - <https://raw.githubusercontent.com/LeanyLabs/assemblyscript-benchmarks/HEAD/README.md>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/assemblyscript/assemblyscript`) · [data/wave12/enrich/raw/github_com_assemblyscript_assemblyscript.json](../../../data/wave12/enrich/raw/github_com_assemblyscript_assemblyscript.json) (enrichment confidence 0.8)

</details>
