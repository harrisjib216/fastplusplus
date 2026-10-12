# Speedy.js

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [AssemblyScript and WebAssembly languages](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `TypeScript (compiler to WebAssembly via LLVM)` · `MIT` · 🔴 abandoned

> Experimental 2017 compiler from a typed TypeScript subset to WebAssembly via LLVM; up to about 4x over 2017-era browser JS.

| | |
|---|---|
| **Beats** | Plain JavaScript in V8 (Chrome 58) and SpiderMonkey (Firefox 53); Emscripten-compiled C++ shown alongside |
| **Claimed result** | README chart doc/benchmark.png (speedup vs the same code as JS, 100% = equal), Chrome 58.0.3029.110: fib 352%, isPrime 311%, nsieve 273%, mergeSortInt 140%, tspInt 134%, mergeSort 124%, simjs 113%, intCompare 108%, tspArrayInt 107%, doubleCompare 102%, doubleAdd 100%, tspArrayDouble 100%, tspDouble 100%, arrayReverse 91%. Firefox 53.0: arrayReverse 444%, nsieve 399%, fib 288%, mergeSortInt 167%, mergeSort 157%, tspInt 138%, simjs 133%, tspArrayInt 112%, isPrime 106%, tspArrayDouble 97%, doubleAdd 96%, doubleCompare 96%, intCompare 94%, tspDouble 98%. A separate run in doc/benchmark-results.pdf (Table 1, ops/s, browser versions not given) gives, Chrome / Firefox (derived from page data): fib 3.42x / 3.0x, isPrime 3.23x / 1.07x, nsieve 1.99x / 4.03x, arrayReverse 1.02x / 4.64x, tspInt 1.37x / 1.41x, mergeSort 1.30x / 1.55x, simjs 1.08x / 1.22x, tspDouble 1.0x / 0.98x. The VMIL 2017 abstract (search snippet only) says up to four times faster and run-time fluctuation halved. |
| **Workload** | 14 small benchmark kernels (arrayReverse, doubleAdd, doubleCompare, fib, intCompare, isPrime, mergeSort, mergeSortInt, nsieve, simjs, tspArrayDouble, tspArrayInt, tspDouble, tspInt) compiled from a JavaScript subset to WebAssembly and compared with the same code run as JS. |
| **Metric** | throughput |
| **Hardware** | Not stated; packages/benchmark/results/\*.json record only the browser user agent (e.g. Chrome 59 on Intel Mac OS X 10.12.5), no CPU model. |
| **Compiler and flags** | Speedy.js: speedyjs-loader 0.0.19 built by packages/benchmark/run-benchmarks.js with {unsafe: true, optimizationLevel: 3, binaryenOpt: true, disableHeapNukeOnExit: true, exportGc: true} (not the defaults of O2, binaryenOpt false and bounds-checked runtime); LLVM WebAssembly backend with the TypeScript fork 2.3.3-with-int. Emscripten comparison: em++ -O3 -std=c++11 with BINARYEN. |
| **Adoption** | 342 stars; repo archived 2023-04-22 |
| **Last commit** | 2017-10-23 |
| **Links** | [repository](https://github.com/MichaReiser/speedy.js) · [benchmark](https://github.com/MichaReiser/speedy.js) |

## Verdict

benchmark.js ops/s of 14 small kernels compiled by Speedy.js (unsafe runtime, LLVM O3 plus Binaryen) against the same TypeScript run as JS, in Chrome 58.0.3029.110 and Firefox 53.0 on macOS 10.12 (Intel Mac user agent, no CPU model recorded) (README chart, results/20170528.json): fib about 3.5x and 2.9x, isPrime 3.1x and 1.06x, nsieve 2.7x and 4.0x, arrayReverse 0.91x and 4.4x, merge sort 1.3x to 1.6x, and the floating-point kernels at about 1.0x. Emscripten -O3 C++ builds of the same kernels land within a few percent of Speedy.js on most of them, so the gain is wasm over 2017 JIT output, not a better code generator.

## Use it when

- As a research reference for typed-subset JavaScript-to-WebAssembly compilation (VMIL 2017, Reiser and Blaeser), including its committed per-browser result files.
- Integer-heavy recursive or loop kernels that already fit the subset: fib about 3.5x (Chrome 58) and 2.9x (Firefox 53), nsieve 2.7x and 4.0x, isPrime about 3.1x in Chrome only (1.06x in Firefox).
- Studying how bounds checks and GC accounting change JS-vs-wasm comparisons: the repo has safe and unsafe runs from the same day (results/20170504-safe.json and 20170504.json).
- Reproducing the 2017 numbers with the author's prebuilt Ubuntu VM rather than a modern toolchain.

## Skip it when

- Any production or new project: archived 2023-04-22, last commit 2017-10-23, the author called it very experimental, and npm install fails on current toolchains (issue #61: llvm-node 2.1.0 does not build against LLVM 10.0.0 and Node 14.17.0).
- Code that needs strings, closures, arrow functions, object literals, inheritance or dynamic typing; none are supported.
- Floating-point or comparison-bound kernels: tspDouble, tspArrayDouble, doubleAdd and doubleCompare stay at 0.96x to 1.02x, intCompare is 0.94x in Firefox, and nbody is slower than JS (0.81x Chrome 59, 0.92x Firefox 53).
- When memory safety matters: the default and benchmarked unsafe mode has no array bounds checks, and with the safe runtime array kernels fall below plain JS (Chrome 58: simjs 0.60x, mergeSort 0.73x, arrayReverse 0.24x).
- When a maintained TypeScript-like wasm language is an option: the AssemblyScript-based siblings or MoonBit cover the same niche with active toolchains.

## How it is fast

The TypeScript checker resolves every symbol's static type (plus a 32-bit int type), so the compiler emits LLVM IR on unboxed int32/double values with no type guards, inline caches or deoptimization paths, then runs LLVM opt (O2 by default, O3 in the benchmark), s2wasm and optionally Binaryen wasm-opt. Arrays live in a C++ runtime (built with Emscripten) as contiguous typed storage, and the default 'unsafe' runtime removes their bounds checks. There is no tracing GC: by default everything allocated is freed when the entry function returns (a 'heap nuke'), or on demand through speedyJsGc (dlmalloc malloc_inspect_all + bulk_free).

## Compared with alternatives

Pick it only to study or cite the design; for new code the AssemblyScript-based siblings (as-proto, as-str, galois) or MoonBit offer a maintained TypeScript-like path to wasm, and Cheerp covers C++ sources. Its one distinguishing point is compiling marked functions inside an otherwise-JS module through LLVM, which those siblings do not do.

## Integration

| | |
|---|---|
| **Form** | module (npm speedyjs-compiler 0.0.19 CLI plus speedyjs-loader webpack loader) |
| **Dependencies** | TypeScript fork MichaReiser/TypeScript#2.3.3-with-int, llvm-node ^2.0.3, an LLVM install with the experimental WebAssembly target (LLVM_CONFIG), Binaryen s2wasm/wasm-opt, the Emscripten-built speedyjs-runtime |
| **Minimum toolchain** | 2017-era LLVM with the experimental WebAssembly backend and a Node version llvm-node 2.x builds against; llvm-node 2.1.0 fails with LLVM 10.0.0 and Node 14.17.0 (issue #61) |
| **Platforms** | Output runs in WebAssembly MVP browsers (results recorded for Chrome 58 to 61, Firefox 53 and 55, Safari 10.2 on macOS 10.12); compiler host documented for Linux/macOS (prebuilt Ubuntu VM), Windows not documented |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — existing JS/TS functions compile only if they already fit the subset; entry functions must become async, and array semantics differ from JS (out-of-bounds reads return the element default instead of undefined; out-of-bounds writes throw in safe mode and are unchecked in unsafe mode) |

## Gotchas

- Harness: packages/benchmark/run-benchmarks.js builds the Speedy.js side with {unsafe: true, optimizationLevel: 3, binaryenOpt: true, disableHeapNukeOnExit: true, exportGc: true}, so the record's 'default compiler options' is wrong (defaults are O2 and binaryenOpt false), and unsafe links the runtime built with -DUNSAFE, which drops array bounds checks. The repo's own same-day results show the gains depend on it: safe mode (20170504-safe.json) gives simjs 0.60x, mergeSort 0.73x, mergeSortInt 0.77x and arrayReverse 0.24x against JS in Chrome 58 (simjs 0.42x and arrayReverse 0.72x in Firefox 53), against 1.05x, 1.31x, 1.35x and 1.76x unsafe (20170504.json).
- Harness: with disableHeapNukeOnExit the wasm kernels never free memory inside the timed loop; speedyJsGc runs in benchmark.js's onCycle hook between cycles, while the JS engines' GC runs inside the timed region, which favours the allocating kernels (mergeSort, mergeSortInt, arrayReverse, simjs, the tsp cases).
- Selective reporting: the 2017-06-06 run that the doc/benchmark-results.pdf table comes from (Chrome 59, Firefox 53) also contains nbody, where Speedy.js loses to JS (0.81x and 0.92x) and to Emscripten (0.81x and 0.86x), plus factorize; the PDF shows 8 of its 16 kernels, and the README chart is an earlier 14-kernel run (results/20170528.json, Chrome 58). The Emscripten nsieve baseline uses bit-packed std::vector&lt;bool&gt;, so Speedy.js's 1.78x lead over Emscripten on nsieve in Chrome is not like-for-like.
- speedyjs-compiler-options.ts documents defaults the code does not use: totalStack is documented as 5 MB but set to 5\*1024\*104 bytes (about 520 KB) with no stack-overflow check, and binaryenOpt (true vs false), optimizationLevel (3 vs 2) and globalBase (1024 vs 8) also differ, so deep recursion can silently overrun the stack.

## Known shortcomings

- Downgraded B to C: the VMIL 2017 paper is unreachable (splashcon, sigplan.org, ost.ch blocked), so only the abstract snippet and the repo's doc/benchmark-results.pdf (derived ratios, Emscripten flags from compile-emcc, no CPU model) remain. Archived 2023-04-22.
- Harness flaws: run-benchmarks.js builds the Speedy.js side with unsafe: true (no array bounds checks), optimizationLevel 3 and binaryenOpt, so the record's 'default compiler options' was wrong; the repo's own safe-mode run (20170504-safe.json, Chrome 58) gives simjs 0.60x, mergeSort 0.73x, mergeSortInt 0.77x and arrayReverse 0.24x of JS. speedyJsGc runs in the onCycle hook between timed cycles, so the wasm side frees memory untimed while the JS engines' GC is timed. The 2017-06-06 run behind the PDF table also has nbody at 0.81x (Chrome 59) and 0.92x (Firefox 53); the PDF shows 8 of its 16 kernels and the README chart (20170528 run) omits nbody. The Emscripten nsieve baseline uses bit-packed std::vector&lt;bool&gt;. The documented 5 MB totalStack is really about 520 KB with no overflow check.

## Caveats and trade-offs

First-party numbers from 2017 engines (Chrome 58/59, Firefox 53); no CPU model, Speedy.js compile options unstated. Peer-reviewed basis, Reiser and Blaeser, 'Accelerate JavaScript Applications by Cross-Compiling to WebAssembly', VMIL 2017, was not opened (only an abstract snippet), so tier C pending paper access. Mixed result: about half the kernels are at or below parity (arrayReverse 91% in Chrome, intCompare 94%, doubleAdd 96%, doubleCompare 96%, tspDouble 98% in Firefox), and the README chart and the PDF table are different runs with different ratios (e.g. Chrome nsieve 273% vs 1.99x). Speedy.js accepts only a restricted, typed JavaScript subset and needs a custom TypeScript fork and an LLVM build with the experimental WebAssembly target. Archived 2023-04-22; the author calls it very experimental. [retier] First-party numbers from 2017 engines (Chrome 58/59, Firefox 53); no CPU model. The peer-reviewed basis (Reiser and Blaeser, VMIL 2017) was not opened. Harness: the Speedy.js side is built with unsafe: true (runtime built with -DUNSAFE, no array bounds checks), optimizationLevel 3 and binaryenOpt, so the published gains depend on dropping safety; the repo's own safe-mode run of the same day (results/20170504-safe.json, Chrome 58) gives simjs 0.60x, mergeSort 0.73x, mergeSortInt 0.77x and arrayReverse 0.24x of JS. With disableHeapNukeOnExit the wasm kernels never free memory inside the timed loop and speedyJsGc runs in the onCycle hook between cycles, while the JS engines' GC runs inside the timed region, which favours the allocating kernels. Selective reporting: the 2017-06-06 run behind doc/benchmark-results.pdf also contains nbody, where Speedy.js loses to JS (0.81x Chrome 59, 0.92x Firefox 53) and to Emscripten (0.81x and 0.86x), plus factorize; the PDF shows 8 of its 16 kernels and the README chart (results/20170528.json) omits nbody; the chart and the PDF are different runs with different ratios. The Emscripten nsieve baseline uses bit-packed std::vector&lt;bool&gt;, so the 1.78x lead over Emscripten there is not like-for-like. About half the kernels are at or below parity. Speedy.js accepts only a restricted typed JavaScript subset and needs a custom TypeScript fork; the documented 5 MB totalStack is really about 520 KB with no overflow check. Abandoned (2017).

Experimental compiler for a restricted JavaScript subset with an int type (custom TypeScript fork), needs a self-built LLVM with the WebAssembly target, calls from JS are async. Archived and tied to 2017 browsers.

## Maintenance

Archived 2023-04-22 (last commit 2017-10-23), MIT; not installable on current toolchains (issue #61), so it is reference material only; the headline speedups come from a first-party 2017 harness that runs the wasm side without bounds checks, keeps its frees out of the timed loop, and leaves out nbody, the kernel where Speedy.js loses to JS.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README chart (doc/benchmark.png) and doc/benchmark-results.pdf compare Speedy.js with the same code run as plain JS in Chrome and Firefox, and the harness is public (packages/benchmark/run-benchmarks.js on benchmark.js, cases/\*.ts, \*-spdy.ts, \*.cc, compile-emcc), but no CPU model is stated anywhere (the results/\*.json files record only an Intel Mac OS X 10.12.5 browser user agent) and Speedy.js compile options are defaults, so not A. The VMIL 2017 paper could not be opened (splashcon, sigplan.org, ost.ch and orix.ost.ch all failed DNS here); only a search-snippet abstract ('up to four times faster') was seen, so per the snippet-only precedent (Instrew, rv32emu) the entry stays C until someone reads the paper, which would likely make it B.
- **Verifier notes:** Downgrade B to C: the chart numbers in the record are accurate, but the only peer-reviewed source (VMIL 2017) was unreachable and seen only as a snippet, and the repo methodology lacks a CPU model. Added the doc/benchmark-results.pdf table (derived ratios) and the Emscripten build flags from compile-emcc. Metadata: MIT, 342 stars, archived 2023-04-22, last commit 2017-10-23 (abandoned). A retier to B is possible if someone reads the VMIL paper.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-04 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/MichaReiser/speedy.js>
  - <https://github.com/MichaReiser/speedy.js/commits/master>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/README.md>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/doc/benchmark.png>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/doc/benchmark-results.pdf>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/LICENSE>
  - <https://github.com/MichaReiser/speedy.js/tree/master/doc>
  - <https://github.com/MichaReiser/speedy.js/tree/master/packages>
  - <https://github.com/MichaReiser/speedy.js/tree/master/packages/benchmark>
  - <https://github.com/MichaReiser/speedy.js/tree/master/packages/benchmark/results>
  - <https://github.com/MichaReiser/speedy.js/tree/master/packages/benchmark/cases>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/run-benchmarks.js>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/webpack.config.js>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/package.json>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/results/20170606.json>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/compile-emcc>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/README.md>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/package.json>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/doc/benchmark.png>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/doc/benchmark-results.pdf>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/run-benchmarks.js>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/package.json>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/webpack.config.js>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/compile-emcc>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/pre.js>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/mergeSortInt.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/mergeSortInt-spdy.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/arrayReverse.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/arrayReverse-spdy.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/nsieve.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/nsieve-spdy.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/nsieve.cc>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/isPrime.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/isPrime-spdy.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/isPrime.cc>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/fib.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/fib-spdy.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/nbody.cc>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/cases/nbody-spdy.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/results/20170606.json>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/results/20170528.json>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/results/20170504.json>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/benchmark/results/20170504-safe.json>
  - <https://github.com/MichaReiser/speedy.js/tree/master/packages/benchmark/results>
  - <https://github.com/MichaReiser/speedy.js/commits/master/doc/benchmark.png>
  - <https://github.com/MichaReiser/speedy.js/tree/master/packages/compiler/src>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/compiler/src/speedyjs-compiler-options.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/compiler/src/compiler.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/compiler/src/code-generation/per-file/per-file-code-generator.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/compiler/src/external-tools/llvm-link.ts>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/compiler/package.json>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/compiler/README.md>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/loader/README.md>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/runtime/CMakeLists.txt>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/runtime/package.json>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/runtime/lib/macros.h>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/runtime/lib/array.h>
  - <https://raw.githubusercontent.com/MichaReiser/speedy.js/HEAD/packages/runtime/lib/memory.cc>
  - <https://github.com/MichaReiser/speedy.js/issues?q=is%3Aissue>
  - <https://github.com/MichaReiser/speedy.js/issues/59>
  - <https://github.com/MichaReiser/speedy.js/issues/61>
  - <https://github.com/MichaReiser/speedy.js/wiki/Speedy.js-Language-Reference>
  - <https://github.com/MichaReiser/speedy.js/wiki/Safe-vs.-Unsafe-Mode>
  - <https://github.com/MichaReiser/speedy.js/wiki/Unsafe-vs-Safe>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/michareiser/speedy.js`) · [data/wave13/enrich/raw/github_com_michareiser_speedy_js.json](../../../data/wave13/enrich/raw/github_com_michareiser_speedy_js.json) (enrichment confidence 0.8)

</details>
